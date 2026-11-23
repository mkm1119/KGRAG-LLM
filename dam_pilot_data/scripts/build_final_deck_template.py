#!/usr/bin/env python3
"""최종보고회 발표자료 템플릿(pptx). 11/26 한강수력본부 발표자료의 디자인(글꼴, 색, 머리글 배치)을 그대로 쓰고,
구성은 표지 → 목차 → Ⅰ 과업개요 → Ⅱ 사업수행 결과(과업 세부 항목 12개) → Ⅲ 향후 추진계획 → 맺음으로 잡는다.
새 슬라이드는 기준 발표자료의 도형을 복사해 만들므로 서식이 같다.
사용: python3 -I dam_pilot_data/scripts/build_final_deck_template.py <기준 발표자료.pptx> <출력.pptx>
"""
import copy, sys
from pptx.enum.dml import MSO_LINE
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

BASE, OUT = sys.argv[1], sys.argv[2]
prs = Presentation(BASE)
S = list(prs.slides)
NAVY, BLUE, PALE, GRAY, INK, HEAD = '003B71', '0070C0', 'EEF5FC', '6B7280', '2B2B2B', 'E5E7EB'
FONT = '한컴산뜻돋움'
L, W = 502920, 11183112                      # 본문 왼쪽 끝과 폭


def el(slide_idx, name):
    return [sh for sh in S[slide_idx - 1].shapes if sh.name == name][0]._element


P = {  # 본보기 도형(기준 발표자료에서 가져옴)
    'label': el(20, 'Text 2'), 'title': el(20, 'Text 3'), 'sub': el(20, 'Text 4'), 'num': el(20, 'Slide Number'),
    'card': el(20, 'Shape 5'), 'navy': el(2, 'Shape 5'), 'big': el(20, 'Text 6'), 'head': el(20, 'Text 7'), 'body': el(20, 'Text 8'),
    'bold14': el(3, 'Text 5'), 'end1': el(25, 'Text 2'), 'end2': el(25, 'Text 3'),
}
NS = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
_n = [100]


def put(slide, proto, x, y, w, h, text=None, size=None, color=None, bold=None, align=None):
    e = copy.deepcopy(P[proto]); slide.shapes._spTree.append(e)
    sh = slide.shapes[-1]
    _n[0] += 1
    e.nvSpPr.cNvPr.set('id', str(_n[0]))
    sh.left, sh.top, sh.width, sh.height = Emu(x), Emu(y), Emu(w), Emu(h)
    if text is not None:
        lines = text.split('\n')
        tx = sh.text_frame._txBody
        ps = tx.findall(NS + 'p')
        p0 = ps[0]
        for p in ps[1:]:
            tx.remove(p)
        rs = p0.findall(NS + 'r')
        if not rs:                                   # 쪽 번호처럼 필드로 된 글
            t = tx.find('.//' + NS + 't')
            if t is not None: t.text = lines[0]
            return sh
        for r in rs[1:]:
            p0.remove(r)
        for br in p0.findall(NS + 'br'):
            p0.remove(br)
        rs[0].find(NS + 't').text = lines[0]
        for ln in lines[1:]:
            q = copy.deepcopy(p0); q.find(NS + 'r').find(NS + 't').text = ln; tx.append(q)
        for para in sh.text_frame.paragraphs:
            if align is not None:
                para.alignment = align
            for r in para.runs:
                if size: r.font.size = Pt(size)
                if color: r.font.color.rgb = RGBColor.from_string(color)
                if bold is not None: r.font.bold = bold
    return sh


def new(layout=1):
    return prs.slides.add_slide(prs.slide_layouts[layout])


GOLD = 'FFD166'
BAND_H, BAR_Y, BAR_H, TOP = 667512, 1005840, 393192, 1554480          # 제목 띠 높이, 세부 항목 띠 위치·높이, 본문 시작


def rect(slide_or_layout, x, y, w, h, fill, line=None, round_=False, prst=None, dash=False):
    e = copy.deepcopy(P['card']); slide_or_layout.shapes._spTree.append(e)
    sh = slide_or_layout.shapes[-1]
    _n[0] += 1; e.nvSpPr.cNvPr.set('id', str(_n[0]))
    sh.left, sh.top, sh.width, sh.height = Emu(x), Emu(y), Emu(w), Emu(h)
    if not round_:
        e.spPr.find(NS + 'prstGeom').set('prst', 'rect')
        for av in e.spPr.find(NS + 'prstGeom').findall(NS + 'avLst'):
            for g in list(av): av.remove(g)
    if prst:
        e.spPr.find(NS + 'prstGeom').set('prst', prst)
    sh.fill.solid(); sh.fill.fore_color.rgb = RGBColor.from_string(fill)
    if line:
        sh.line.color.rgb = RGBColor.from_string(line); sh.line.width = Pt(0.75 if dash else 1.25)
        if dash:
            sh.line.dash_style = MSO_LINE.DASH
    else:
        sh.line.fill.background()
    return sh


# 본문 레이아웃에 제목 띠와 아래 선을 넣는다(슬라이드마다 그리지 않고 바탕에 둠)
_lay = prs.slide_layouts[1]
_b1 = rect(_lay, 0, 0, 12192000, BAND_H, PALE); _b2 = rect(_lay, 0, BAND_H, 12192000, 36576, NAVY); _b3 = rect(_lay, L, 6373368, W, 12700, 'B6BCC6')
for _b in (_b3, _b2, _b1):                               # 로고보다 뒤로 보낸다
    _lay.shapes._spTree.remove(_b._element); _lay.shapes._spTree.insert(2, _b._element)


def page(label, title, sub=None, num=None):
    """label: 장 이름(오른쪽 위 꼬리표), title: 제목 띠, sub: 번호 띠의 이름(없으면 띠를 그리지 않음), num: 번호"""
    s = new(1)
    put(s, 'title', L - 91440, 100584, 6400800, 466344, title, size=24)
    rect(s, 9601200, BAND_H + 36576, 2590800, 301752, NAVY)
    put(s, 'bold14', 9601200, BAND_H + 54864, 2590800, 265176, label, size=11, color='FFFFFF', align=PP_ALIGN.CENTER)
    if sub:
        rect(s, L, BAR_Y, W, BAR_H, 'DCE9F7', round_=True)
        if num:
            rect(s, L, BAR_Y, 960120, BAR_H, NAVY, round_=True)
            put(s, 'bold14', L, BAR_Y + 45720, 960120, 301752, num, size=15, color=GOLD, align=PP_ALIGN.CENTER)
        put(s, 'bold14', L + (1051560 if num else 182880), BAR_Y + 45720, W - 1234440, 301752, sub, size=15, color=NAVY)
    put(s, 'num', 11155680, 6446520, 548640, 274320, '0')
    return s


FRAME, INNER = 'A9BEDB', 'F6F9FD'


def panel(s, x, y, w, h, head=None, checks=None):
    """참고 발표자료의 상자: 바깥 틀 + 머리 칸(꼬리표와 소제목) + 안쪽 상자 + 체크 줄. 비우면 'ㅇ'만 둔다."""
    rect(s, x, y, w, h, FRAME, round_=True)
    rect(s, x + 54864, y + 64008, w - 109728, 384048, 'DCE9F7')
    rect(s, x + 146304, y, 301752, 448056, NAVY, prst='flowChartOffpageConnector')
    put(s, 'bold14', x + 521208, y + 100584, w - 640080, 301752, head or 'ㅇ', size=14, color=NAVY)
    rect(s, x + 45720, y + 521208, w - 91440, h - 566928, INNER, round_=True)
    if checks is None:
        check(s, x + 100584, y + 603504, min(w - 201168, 3840480), 'ㅇ')
    else:
        for k, t in enumerate(checks):
            check(s, x + 100584, y + 603504 + k * 393192, w - 201168, t)
    return y + 603504 + len(checks or [1]) * 393192          # 체크 줄 아래의 시작 높이


def check(s, x, y, w, text):
    rect(s, x, y, w, 320040, 'FFFFFF', line='B6BCC6', round_=True)
    rect(s, x + 18288, y + 18288, 283464, 283464, NAVY, prst='ellipse')
    put(s, 'bold14', x + 18288, y + 22860, 283464, 265176, '✓', size=11, color='FFFFFF', align=PP_ALIGN.CENTER)
    put(s, 'body', x + 347472, y + 13716, w - 420624, 292608, text, size=12, color=INK)


def dot(s, x, y, text, w=6400800):
    put(s, 'bold14', x, y, w, 301752, '● ' + text, size=14, color=NAVY)


def conclusion(s, text, y=5806440):
    rect(s, L, y, W, 466344, NAVY, round_=True)
    put(s, 'bold14', L + 182880, y + 82296, W - 365760, 301752, text, size=14, color='FFFFFF')


def divider(roman, name, desc):
    s = new(0)
    bg = S[24]._element.cSld.find('{http://schemas.openxmlformats.org/presentationml/2006/main}bg')      # 맺음 슬라이드와 같은 남색 바탕
    if bg is not None:
        s._element.cSld.insert(0, copy.deepcopy(bg))
    put(s, 'end1', L, 2286000, W, 822960, roman, color='9DBEDD')
    put(s, 'end1', L, 3108960, W, 822960, name)
    put(s, 'end2', L, 4023360, W, 457200, desc)
    return s


def tbl(slide, rows, widths, x=L, y=1737360, w=W, row_h=420000, size=12, head_fill=HEAD, first_col_bold=True, tight=False):
    n, m = len(rows), len(rows[0])
    gt = slide.shapes.add_table(n, m, Emu(x), Emu(y), Emu(w), Emu(row_h * n)).table
    tot = float(sum(widths))
    for j, wd in enumerate(widths):
        gt.columns[j].width = Emu(int(w * wd / tot))
    tblPr = gt._tbl.tblPr
    for a in ('bandRow', 'firstRow'):
        tblPr.set(a, '0')
    sid = tblPr.find(NS + 'tableStyleId')
    if sid is not None:
        sid.text = '{5940675A-B579-460E-94D1-54222C63F5DA}'       # 테두리만 있는 표 스타일
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            c = gt.cell(i, j); c.vertical_anchor = MSO_ANCHOR.MIDDLE
            if tight:
                c.margin_top = c.margin_bottom = Emu(18288)
            c.fill.solid(); c.fill.fore_color.rgb = RGBColor.from_string(head_fill if i == 0 else 'FFFFFF')
            tf = c.text_frame; tf.word_wrap = True
            for k, ln in enumerate(str(v).split('\n')):
                para = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
                para.alignment = PP_ALIGN.CENTER if (i == 0 or (j == 0 and first_col_bold) or len(ln) <= 3) else PP_ALIGN.LEFT
                r = para.add_run(); r.text = ln
                r.font.name = FONT; r.font.size = Pt(size); r.font.bold = (i == 0 or (j == 0 and first_col_bold))
                r.font.color.rgb = RGBColor.from_string(NAVY if i == 0 else INK)
                rPr = r._r.get_or_add_rPr()
                for tag in ('ea', 'cs'):
                    f = rPr.find(NS + tag)
                    if f is None:
                        f = rPr.makeelement(NS + tag, {}); rPr.append(f)
                    f.set('typeface', FONT)
    return gt


def set_text(shape, text):
    rs = [r for p in shape.text_frame.paragraphs for r in p.runs]
    rs[0].text = text
    for r in rs[1:]:
        r.text = ''


# ------------------------------------------------------------------ 표지와 목차(기준 슬라이드를 고쳐 씀)
cover, toc, thanks = S[0], S[1], S[24]
for sh in cover.shapes:
    if sh.name == 'Text 5': set_text(sh, '최종보고회')
    if sh.name == 'Text 7': set_text(sh, '(발표자료 작성 템플릿)')
    if sh.name == 'Text 11': set_text(sh, '2026. 12. 9.')
T = {'Text 2': '발표 순서', 'Text 4': '과업개요, 과업 항목별 수행 결과, 향후 추진계획의 순서로 발표',
     'Text 7': '과업개요', 'Text 11': '사업수행 결과', 'Text 15': '향후 추진계획'}
for sh in toc.shapes:
    if sh.name in T: set_text(sh, T[sh.name])
MULTI = {'Text 8': ['목적 및 배경, 과업범위,', '추진 일정, 수행조직'], 'Text 12': ['과업 4개 분야,', '세부 항목 12개의 수행 결과'], 'Text 16': ['향후 연구개발 방향과', '추진 계획(안)']}
for sh in toc.shapes:
    if sh.name in MULTI:
        ps = sh.text_frame.paragraphs
        for p, t in zip(ps, MULTI[sh.name]):
            p.runs[0].text = t
            for r in p.runs[1:]: r.text = ''
        for p in ps[len(MULTI[sh.name]):]:
            for r in p.runs: r.text = ''

order = [cover]
# 목차: 기준 슬라이드의 카드 3개를 쓰고 머리글만 본문 양식에 맞춘다
for sh in list(toc.shapes):
    if sh.name == 'Text 2':
        sh._element.getparent().remove(sh._element)
    elif sh.name == 'Text 3':
        sh.left, sh.top, sh.width, sh.height = Emu(L - 91440), Emu(100584), Emu(6400800), Emu(466344)
        for r in sh.text_frame.paragraphs[0].runs: r.font.size = Pt(24)
    elif sh.name == 'Text 4':
        sh.top = Emu(1005840)
order.append(toc)

# ================================================================== Ⅰ 과업개요
order.append(divider('Ⅰ', '과업개요', '목적 및 배경, 과업범위, 공정률, 수행조직'))
C1 = 'Ⅰ. 과업개요'
# --- 1. 목적 및 배경 (1): 과업 기본 정보 (이름표 + 내용 띠 + 점선)
s = page(C1, '1. 목적 및 배경')
INFO = [('과업명', '댐 운영 의사결정 프레임워크 구축 자문 용역', NAVY), ('발주기관', '한국수력원자력(주)', BLUE), ('수행기관', '국민대학교 산학협력단', NAVY),
        ('과업기간', '2026. 07. 23. ~ 2027. 01. 22. (착수일로부터 6개월)', BLUE), ('책임연구원', '국민대학교 신주영 교수', NAVY)]
for k, (lab, val, col) in enumerate(INFO):
    y = 1234440 + k * 978408
    rect(s, 696000, y, 10800000, 476717, PALE, round_=True)
    rect(s, 681832, y - 9047, 1526573, 476717, col, round_=True)
    put(s, 'bold14', 681832, y + 82296, 1526573, 301752, lab, size=16, color='FFFFFF', align=PP_ALIGN.CENTER)
    put(s, 'bold14', 2208405, y + 82296, 9287595, 301752, val, size=16, color=INK, align=PP_ALIGN.CENTER)
    rect(s, 696000, y + 722376, 10800000, 9144, 'FFFFFF', line='9AA3AF', dash=True)
order.append(s)
# --- 1. 목적 및 배경 (2): 배경 글 + 목표
s = page(C1, '1. 목적 및 배경', '목적 및 배경', '1.')
BG = [('댐 운영 판단에 필요한 비정형 자료의 활용 체계 부재',
       ['댐 운영은 수문 자료뿐 아니라 과거 운영 경험, 매뉴얼, 관련 법령 등 비정형 자료에 대한 종합 판단이 필요',
        '비정형 자료를 정형화하여 의사결정에 연결하는 모델·시스템이 부재']),
      ('sLLM 기반 의사결정 지원 기술에 대한 수요',
       ['sLLM 기반 스마트 의사결정 체계를 통한 비숙련 운영자 보조',
        '방류 시점을 정밀 제어하는 수력발전 운영 효율화 기술에 대한 수요'])]
y = TOP + 91440
for hd, subs in BG:
    dot(s, L + 91440, y, hd, w=W - 182880); y += 393192
    for t in subs:
        put(s, 'body', L + 502920, y, W - 640080, 292608, '▪  ' + t, size=13, color=INK); y += 356616
    y += 182880
rect(s, L + 91440, 5120640, W - 182880, 877824, 'EEF1F5')
rect(s, L + 91440, 5065776, 1413050, 987552, BLUE, prst='homePlate')
put(s, 'bold14', L + 91440, 5403456, 1234440, 301752, '목 표', size=16, color='FFFFFF', align=PP_ALIGN.CENTER)
put(s, 'body', L + 1737360, 5385816, W - 2011680, 320040, '▪  sLLM 기반 댐 운영 의사결정 및 발전 최적화 프레임워크 구축을 위한 기술적 타당성 검토', size=13, color=INK)
order.append(s)
# --- 2. 과업범위: 번호 띠 + ● 과업범위 + 표
s = page(C1, '2. 과업범위', '과업범위', '2.')
dot(s, L + 91440, TOP - 27432, '과업범위')
tbl(s, [['과업 대상', '▪  댐 운영 의사결정 지원을 위한 sLLM·RAG 기술의 국내외 적용 사례, 자료 수집 경로, 지식 구조화 방안, 후보 모델\n▪  국내 댐 운영 현장의 업무 절차와 자료 활용 방식'],
        ['내용적 범위', '▪  국내외 기술 트렌드 조사: 수자원 분야 사례 조사, 국내 운영 여건 조사, 적용 기술요소 및 모델 제안\n'
                   '▪  LLM 활용 데이터 파이프라인 조사: 수집 경로 조사, 온톨로지·메타데이터 설계방안 조사, RAG-LLM 통합 파이프라인(안) 제시\n'
                   '▪  sLLM 후보군 평가 방향: 후보 모델 조사, 모델 구조 및 특성 검토, 후보군 적용방안 제시\n'
                   '▪  도메인 특화 성능 향상 전략: RAG 기반 적용방안 조사, 경량 미세조정 방식 검토, 성능 향상 전략 제시']],
    [16, 84], y=TOP + 365760, row_h=1900000, size=13, head_fill='FFFFFF')
_g = s.shapes[-1].table
_g.rows[0].height = Emu(1280160); _g.rows[1].height = Emu(2651760)
for _i in (0, 1):
    for _p in _g.cell(_i, 1).text_frame.paragraphs:                 # 내용 칸은 왼쪽 맞춤, 보통 굵기
        _p.alignment = PP_ALIGN.LEFT
        for _r in _p.runs:
            _r.font.bold = False; _r.font.color.rgb = RGBColor.from_string(INK)
order.append(s)
# --- 3. 공정률: ● 추진 계획 + 공정표
s = page(C1, '3. 공정률')
dot(s, L, 868680, '추진 계획')
M = ["'26.8", "'26.9", "'26.10", "'26.11", "'26.12", "'27.1"]
SCH = [('1. 국내외 기술 트렌드 조사', None), ('수자원 분야 사례 조사', [1]), ('국내 운영 여건 조사', [1]), ('적용 기술요소 및 모델 제안', [2, 3]),
       ('2. LLM 활용 데이터 파이프라인 조사', None), ('수집 경로 조사', [2]), ('온톨로지·메타데이터 설계방안 조사', [2]), ('RAG-LLM 통합 파이프라인(안) 제시', [3, 4]),
       ('3. sLLM 후보군 평가 방향', None), ('후보 모델 조사', [3]), ('모델 구조 및 특성 검토', [3, 4]), ('후보군 적용방안 제시', [5]),
       ('4. 도메인 특화 성능 향상 전략', None), ('RAG 기반 적용방안 조사', [4]), ('경량 미세조정 방식 검토', [4, 5]), ('성능 향상 전략 제시', [6]),
       ('5. 최종 보고서 작성', [5, 6])]
gt = tbl(s, [['과업 내용'] + M] + [[('' if ms is None or n.startswith('5.') else '      ') + n] + ['' for _ in M] for n, ms in SCH], [40, 10, 10, 10, 10, 10, 10], y=1188720, row_h=262000, size=11, first_col_bold=False, tight=True, head_fill='C9D9EE')
for i, (n, ms) in enumerate(SCH, 1):
    if ms is None:
        for j in range(7):
            c = gt.cell(i, j); c.fill.solid(); c.fill.fore_color.rgb = RGBColor.from_string(PALE)
        for r in gt.cell(i, 0).text_frame.paragraphs[0].runs: r.font.bold = True
        continue
    for j in ms:
        c = gt.cell(i, j); c.fill.solid(); c.fill.fore_color.rgb = RGBColor.from_string(BLUE)
order.append(s)
# --- 4. 수행조직: 번호 띠 + 조직도 + 분야별 표 2개
s = page(C1, '4. 수행조직', '사업수행 조직 구성', '4.')
CX, OW = L + W // 2, 2514600
y = TOP - 45720
for k, (hd, val) in enumerate([('발 주 처', '한국수력원자력(주)'), ('수 행 기 관', '국민대학교 산학협력단'), ('책임연구원(1인)', '신주영 교수')]):
    rect(s, CX - OW // 2, y, OW, 265176, NAVY)
    put(s, 'bold14', CX - OW // 2, y + 9144, OW, 256032, hd, size=12, color='FFFFFF', align=PP_ALIGN.CENTER)
    rect(s, CX - OW // 2, y + 265176, OW, 301752, 'E5E7EB')
    put(s, 'bold14', CX - OW // 2, y + 283464, OW, 265176, val, size=12, color=INK, align=PP_ALIGN.CENTER)
    y += 566928
    rect(s, CX - 6350, y, 12700, 91440, NAVY); y += 91440
TW = 5040000
XA, XB = L + 182880, L + W - 182880 - TW
rect(s, XA + TW // 2, y - 6350, XB - XA, 12700, NAVY)
for x in (XA, XB):
    rect(s, x + TW // 2 - 6350, y, 12700, 164592, NAVY)
ty = y + 164592
for x, hd, rows in ((XA, '수자원 분야 (과업 1·2)', [['책임연구원', '수공학 · 박사', '신주영'], ['연구보조원', '수공학 · 학사', '문경민']]),
                    (XB, '인공지능 분야 (과업 3·4)', [['연구원', '인공지능 · 박사', '김장호'], ['연구보조원', '인공지능 · 학사', '황솔희']])):
    g = tbl(s, [[hd, '', '']] + rows, [30, 35, 35], x=x, y=ty, w=TW, row_h=420000, size=13, head_fill='C9D9EE')
    g.cell(0, 0).merge(g.cell(0, 2))
    for _i in (1, 2):
        for _j in (1, 2):
            g.cell(_i, _j).text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
order.append(s)

# ================================================================== Ⅱ 사업수행 결과
order.append(divider('Ⅱ', '사업수행 결과', '과업 4개 분야, 세부 항목 12개의 수행 결과'))
ITEMS = [('1. 국내외 기술 트렌드 조사', ['1-1 수자원 분야 사례 조사', '1-2 국내 운영 여건 조사', '1-3 적용 기술요소 및 모델 제안']),
         ('2. LLM 활용 데이터 파이프라인 조사', ['2-1 수집 경로 조사', '2-2 온톨로지·메타데이터 설계방안 조사', '2-3 RAG-LLM 통합 파이프라인(안) 제시']),
         ('3. sLLM 후보군 평가 방향', ['3-1 후보 모델 조사', '3-2 모델 구조 및 특성 검토', '3-3 후보군 적용방안 제시']),
         ('4. 도메인 특화 성능 향상 전략', ['4-1 RAG 기반 적용방안 조사', '4-2 경량 미세조정 방식 검토', '4-3 성능 향상 전략 제시'])]
C2 = 'Ⅱ. 사업수행 결과'
PY, PH = TOP - 45720, 4754880
HW = (W - 182880) // 2
# --- 1-1: 작성 예시(상자 하나에 소제목, 체크 줄, 표)
s = page(C2, ITEMS[0][0], '수자원 분야 사례 조사', '1-1')
yy = panel(s, L, PY, W, PH, '수자원 분야 LLM 활용 사례의 유형별 비교 및 시사점', [
    '수자원 분야의 LLM 활용 사례 63편을 RAG 기반 질의응답(21편), 도메인 특화 LLM(18편), 운영지식 구조화(24편)의 세 유형으로 조사',
    '세 유형은 분야 지식을 두는 곳(문서 저장소, 모델의 가중치, 온톨로지·KG)에서 구분되며, RAG 21편 중 7편이 KG를 함께 사용',
    '운영 판단을 지원하는 응답에는 근거 제시가 필요하므로, 검색 근거나 KG 항목을 응답에 연결하는 구성이 적합'])
tbl(s, [['항목', 'RAG 기반 질의응답', '도메인 특화 LLM', '운영지식 구조화'],
        ['조사 문헌', '21편', '18편', '24편'],
        ['지식을 두는 곳', '문서 저장소(벡터·희소 색인)', '모델의 가중치', '온톨로지와 KG의 개체·관계'],
        ['지식의 반영 방법', '질의 시점에 검색하여 프롬프트에 포함', '추가 사전학습, 미세조정', '자료에서 개체·관계를 추출하여 구축'],
        ['자료의 갱신', '저장소의 문서를 교체', '모델을 다시 학습', 'KG의 개체·관계를 추가·수정'],
        ['응답의 근거 제시', '검색한 문서나 KG 항목을 근거로 제시 가능', '가중치에 학습된 지식은 출처 제시가 어려움', '개체·관계와 출처 속성으로 근거 추적 가능'],
        ['확인된 한계', '표·그림이 든 문서의 처리', '분야 미세조정에 따른 일반 능력 하락 보고 2편', 'KG 자체의 완전성 평가 부재, 시계열 자료 통합']],
    [16, 28, 28, 28], x=L + 100584, y=yy + 45720, w=W - 201168, row_h=356616, size=11, head_fill='C9D9EE', tight=True)
order.append(s)
# --- 나머지 항목: 항목마다 2장, 번호 띠와 빈 상자 2개
for field, subs in ITEMS:
    for sub in subs:
        num, name = sub.split(' ', 1)
        if num == '1-1':
            continue
        for _ in range(2):
            s = page(C2, field, name, num)
            panel(s, L, PY, HW, PH)
            panel(s, L + HW + 182880, PY, HW, PH)
            order.append(s)

# ================================================================== Ⅲ 향후 추진계획
order.append(divider('Ⅲ', '향후 추진계획', '과업 분야별 향후 추진계획'))
for k, (field, subs) in enumerate(ITEMS, 1):
    s = page('Ⅲ. 향후 추진계획', '향후 추진계획', field.split('. ', 1)[1], '과업%d' % k)
    for y, h in ((TOP - 45720, 762000), (TOP + 1371600, 1357971), (TOP + 3383280, 762000)):
        put(s, 'bold14', L, y, 502920, 283464, 'ㅇ', size=14, color=NAVY)
        rect(s, L + 137160, y + 347472, W - 137160, h, INNER, line=FRAME, round_=True)
    order.append(s)
order.append(thanks)

# ------------------------------------------------------------------ 순서 정리: 기준 발표자료의 나머지 슬라이드는 뺀다
sldIdLst = prs.slides._sldIdLst
RID = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
key = lambda sl: str(sl.part.partname)                      # 슬라이드 객체는 매번 새로 만들어지므로 파일 이름으로 구분
keep = set(key(x) for x in order)
elems = {key(sl): e for sl, e in zip(list(prs.slides), list(sldIdLst))}
for sl, e in zip(list(prs.slides), list(sldIdLst)):
    if key(sl) not in keep:
        prs.part.drop_rel(e.get(RID)); sldIdLst.remove(e)
for e in list(sldIdLst):
    sldIdLst.remove(e)
for sl in order:
    sldIdLst.append(elems[key(sl)])
for i, sl in enumerate(prs.slides, 1):                      # 쪽 번호
    for sh in sl.shapes:
        if sh.name == 'Slide Number':
            t = sh._element.find('.//' + NS + 't')
            if t is not None: t.text = str(i)
prs.save(OUT)
print('저장', OUT, '슬라이드', len(prs.slides))
