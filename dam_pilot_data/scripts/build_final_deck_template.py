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


def panel(s, x, y, w, h, head=None, checks=None, size=12):
    """참고 발표자료의 상자: 바깥 틀 + 머리 칸(꼬리표와 소제목) + 안쪽 상자 + 체크 줄. 비우면 'ㅇ'만 둔다.
    체크 줄 아래의 시작 높이를 돌려준다."""
    rect(s, x, y, w, h, FRAME, round_=True)
    rect(s, x + 54864, y + 64008, w - 109728, 384048, 'DCE9F7')
    rect(s, x + 146304, y, 301752, 448056, NAVY, prst='flowChartOffpageConnector')
    put(s, 'bold14', x + 521208, y + 100584, w - 640080, 301752, head or 'ㅇ', size=14, color=NAVY)
    rect(s, x + 45720, y + 521208, w - 91440, h - 566928, INNER, round_=True)
    yy = y + 603504
    if checks is None:
        yy += check(s, x + 100584, yy, min(w - 201168, 3840480), 'ㅇ')
    else:
        for t in checks:
            yy += check(s, x + 100584, yy, w - 201168, t, size)
    return yy


def _mid(sh):
    tf = sh.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_top = tf.margin_bottom = Emu(0)
    return sh


def check(s, x, y, w, text, size=12):
    """체크 줄 하나. 글이 길면 줄 수만큼 높이를 늘린다. 차지한 높이(간격 포함)를 돌려준다."""
    import math
    wid = sum(1.0 if ord(c) > 0x2E7F else 0.55 for c in text) * size * 12700
    lines = max(1, math.ceil(wid / ((w - 457200) * 0.86)))
    h = 320040 + (lines - 1) * 201168
    D = 265176
    rect(s, x, y, w, h, 'FFFFFF', line='B6BCC6', round_=True)
    rect(s, x + 27432, y + (h - D) // 2, D, D, NAVY, prst='ellipse')
    _mid(put(s, 'bold14', x + 27432, y + (h - D) // 2, D, D, '✓', size=10, color='FFFFFF', align=PP_ALIGN.CENTER))
    _mid(put(s, 'body', x + 347472, y, w - 420624, h, text, size=size, color=INK))
    return h + 64008


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

_t10 = [sh for sh in cover.shapes if sh.name == 'Text 10'][0]
_e = copy.deepcopy(_t10._element); _t10._element.addnext(_e)
_new = [sh for sh in cover.shapes if sh._element is _e][0]
for sh in cover.shapes:
    if sh.name == 'Text 9': set_text(sh, '발주기관  ┃  한국수력원자력(주)')
    if sh.name == 'Text 11': sh.top = Emu(5634000)
set_text(_t10, '수행기관  ┃  국민대학교 산학협력단')
_new.top = Emu(5132040); set_text(_new, '연구책임자  ┃  신주영')
order = [cover]
# 목차: 참고 발표자료와 같은 배치(왼쪽 색 면에 '목 차', 오른쪽에 장 목록)
s = new(0)
rect(s, 0, 0, 3767328, 6858000, NAVY)
rect(s, 0, 1143000, 3767328, 27432, '9DBEDD')
put(s, 'end1', 0, 1554480, 3767328, 822960, '목   차')
for k, (ro, nm, ds) in enumerate([('Ⅰ.', '과업개요', '목적 및 배경, 과업범위, 공정률, 수행조직'), ('Ⅱ.', '사업수행 결과', '과업 4개 분야, 세부 항목 12개의 수행 결과'), ('Ⅲ.', '향후 추진계획', '과업 분야별 향후 추진계획')]):
    y = 1371600 + k * 1463040
    put(s, 'bold14', 4480560, y, 1005840, 548640, ro, size=32, color=BLUE)
    put(s, 'bold14', 5486400, y + 64008, 6000000, 457200, nm, size=26, color=NAVY)
    put(s, 'sub', 5486400, y + 594360, 6000000, 301752, ds, size=14)
    rect(s, 4480560, y + 1069848, 7040880, 9144, 'B6BCC6')
order.append(s)

MEMO = {}                                            # 슬라이드 순번(0부터) -> 메모 글
# ================================================================== Ⅰ 과업개요
order.append(divider('Ⅰ', '과업개요', '목적 및 배경, 과업범위, 공정률, 수행조직'))
C1 = 'Ⅰ. 과업개요'
# --- 1. 목적 및 배경 (1): 과업 기본 정보 (이름표 + 내용 띠 + 점선)
s = page(C1, '1. 목적 및 배경')
INFO = [('과업명', '댐 운영 의사결정 프레임워크 구축 자문 용역', NAVY), ('발주기관', '한국수력원자력(주)', BLUE), ('수행기관', '국민대학교 산학협력단', NAVY),
        ('과업기간', '2026. 07. 23. ~ 2027. 01. 22. (착수 후 6개월, 12월 조기 준공 예정)', BLUE), ('책임연구원', '국민대학교 신주영 교수', NAVY)]
for k, (lab, val, col) in enumerate(INFO):
    y = 1234440 + k * 978408
    rect(s, 696000, y, 10800000, 476717, PALE, round_=True)
    rect(s, 681832, y - 9047, 1526573, 476717, col, round_=True)
    _mid(put(s, 'bold14', 681832, y - 9047, 1526573, 476717, lab, size=16, color='FFFFFF', align=PP_ALIGN.CENTER))
    _mid(put(s, 'bold14', 2208405, y, 9287595, 476717, val, size=16, color=INK, align=PP_ALIGN.CENTER))
    rect(s, 696000, y + 722376, 10800000, 9144, 'FFFFFF', line='9AA3AF', dash=True)
order.append(s)
# --- 1. 목적 및 배경 (2): 용역 규격서의 '현황 및 필요성'과 '최종목표'
s = page(C1, '1. 목적 및 배경', '목적 및 배경', '1.')
BG = [('댐 운영 판단에 쓰이는 비정형 자료를 의사결정에 연결하는 체계의 부재',
       ['댐 운영은 수문 데이터뿐만 아니라 과거의 운영 경험, 매뉴얼, 관련 법령 등 비정형 데이터에 대한 종합적 판단이 필수적',
        '이를 정형화해 의사결정에 연결하는 모델·시스템이 부재']),
      ('sLLM 기반 스마트 의사결정 체계에 대한 수요',
       ['sLLM 기반 스마트 의사결정 체계를 통해 비숙련 운영자를 보조',
        '방류 시점을 정밀하게 제어하여 수력발전 효율을 높이는 운영 효율화 기술에 대한 수요가 높음']),
      ('운영 매뉴얼과 수문 데이터의 통합 분석 필요',
       ['텍스트 형태의 운영 매뉴얼과 수치 기반의 수문 데이터를 통합 분석',
        '위기 상황 발생 시 담당자에게 즉각적인 가이드라인을 제시하여 인적 오류를 최소화'])]
y = TOP + 18288
for hd, subs in BG:
    put(s, 'bold14', L + 91440, y, W - 182880, 320040, '● ' + hd, size=16, color=NAVY); y += 384048
    for t in subs:
        put(s, 'body', L + 457200, y, W - 594360, 301752, '▪  ' + t, size=14, color=INK); y += 338328
    y += 118872
rect(s, L + 91440, 5285232, W - 182880, 822960, 'EEF1F5')
rect(s, L + 91440, 5230368, 1413050, 932688, BLUE, prst='homePlate')
_mid(put(s, 'bold14', L + 91440, 5230368, 1234440, 932688, '목 표', size=17, color='FFFFFF', align=PP_ALIGN.CENTER))
_mid(put(s, 'bold14', L + 1691640, 5285232, W - 1965960, 822960, 'sLLM 기반 댐 운영 의사결정 및 발전 최적화 프레임워크 구축을 위한 기술적 타당성 검토', size=15, color=INK))
order.append(s)
# --- 2. 과업범위: 번호 띠 + ● 과업범위 + 표(용역 규격서의 용역 적용범위)
s = page(C1, '2. 과업범위', '과업범위', '2.')
dot(s, L + 91440, TOP - 54864, '과업범위')
SC = [('과업 목표', ['댐 및 수력발전 운영을 위한 생성형 AI 기술 도입 방안의 연구개발 기획 방향 마련']),
      ('기술 역무', ['■ 국내외 기술 트렌드 조사', '수자원 분야 사례 조사, 국내 운영 여건 조사, 적용 기술요소 및 모델 제안',
                 '■ LLM 활용 데이터 파이프라인 조사', '수집 경로 조사, 온톨로지·메타데이터 설계방안 조사, RAG-LLM 통합 파이프라인(안) 제시',
                 '■ sLLM 후보군 평가 방향', '후보 모델 조사, 모델 구조 및 특성 검토, 후보군 적용방안 제시',
                 '■ 도메인 특화 성능 향상 전략', 'RAG 기반 적용방안 조사, 경량 미세조정 방식 검토, 성능 향상 전략 제시']),
      ('기타 역무', ['용역 공정관리 및 월간 진도보고, 각종 회의 및 보고서, 기술 및 학술자문'])]
g = tbl(s, [[a, '\n'.join(b)] for a, b in SC], [16, 84], y=TOP + 283464, row_h=700000, size=14, head_fill='FFFFFF')
for i, hh in enumerate((640080, 3246120, 640080)):
    g.rows[i].height = Emu(hh)
    c0 = g.cell(i, 0); c0.fill.solid(); c0.fill.fore_color.rgb = RGBColor.from_string(NAVY)
    for r in c0.text_frame.paragraphs[0].runs:
        r.font.size = Pt(16); r.font.bold = True; r.font.color.rgb = RGBColor.from_string('FFFFFF')
    c1 = g.cell(i, 1); c1.margin_left = Emu(228600)
    for pp in c1.text_frame.paragraphs:
        pp.alignment = PP_ALIGN.LEFT
        head = pp.runs[0].text.startswith('■')
        if i == 1 and not head: pp.runs[0].text = '      ' + pp.runs[0].text
        for r in pp.runs:
            r.font.bold = head; r.font.size = Pt(15 if head or i != 1 else 14)
            r.font.color.rgb = RGBColor.from_string(NAVY if head else INK)
order.append(s)
# --- 3. 공정률: ● 추진 계획 + 공정표(계획과 실적, 12월 조기 준공 반영)
s = page(C1, '3. 공정률')
dot(s, L, 859536, '추진 계획')
PLAN_C, ACT_C, RED = '8A94A3', BLUE, 'C0392B'
for k, (col, t) in enumerate(((PLAN_C, '계획'), (ACT_C, '실적(12월 조기 준공 반영)'), (RED, '최종보고회'))):
    x = 2286000 + (0, 1097280, 3566160)[k]
    rect(s, x, 941832, 384048, 118872, col)
    put(s, 'sub', x + 438912, 859536, 2377440, 283464, t, size=12)
M = ["'26.8", "'26.9", "'26.10", "'26.11", "'26.12", "'27.1"]
# (이름, 계획한 달, 실적 달) : 달은 1('26.8)~6('27.1). 분야 줄은 None
SCH = [('1. 국내외 기술 트렌드 조사', None, None), ('수자원 분야 사례 조사', [1], [1]), ('국내 운영 여건 조사', [1], [1]), ('적용 기술요소 및 모델 제안', [2, 3], [2, 3]),
       ('2. LLM 활용 데이터 파이프라인 조사', None, None), ('수집 경로 조사', [2], [2]), ('온톨로지·메타데이터 설계방안 조사', [2], [2]), ('RAG-LLM 통합 파이프라인(안) 제시', [3, 4], [3, 4]),
       ('3. sLLM 후보군 평가 방향', None, None), ('후보 모델 조사', [3], [3]), ('모델 구조 및 특성 검토', [3, 4], [3, 4]), ('후보군 적용방안 제시', [5], [5]),
       ('4. 도메인 특화 성능 향상 전략', None, None), ('RAG 기반 적용방안 조사', [4], [4]), ('경량 미세조정 방식 검토', [4, 5], [4, 5]), ('성능 향상 전략 제시', [6], [5]),
       ('5. 최종 보고서 작성', None, None), ('최종 보고서 작성', [5, 6], [4, 5]), ('최종보고회(12. 9.), 조기 준공(12월)', 'mark', None)]
GY, RH = 1179576, 259080                                        # 공정표는 표 대신 도형으로 그려 막대 위치가 어긋나지 않게 한다
NW = int(W * 0.40); CW = (W - NW) // 6; X0 = L + NW
GL = '9AA3AF'


def gcell(x, y, w, fill, text=None, bold=False, align=PP_ALIGN.CENTER, indent=0, color=INK):
    r = rect(s, x, y, w, RH, fill, line=GL); r.line.width = Pt(0.5)
    if text:
        _mid(put(s, 'bold14' if bold else 'body', x + 64008 + indent, y, w - 128016 - indent, RH, text, size=11, color=color, align=align, bold=bold))


gcell(L, GY, NW, 'C9D9EE', '과업 내용', bold=True, color=NAVY)
for j, m in enumerate(M):
    gcell(X0 + j * CW, GY, CW, 'C9D9EE', m, bold=True, color=NAVY)
span = lambda ms: (X0 + (min(ms) - 1) * CW, (max(ms) - min(ms) + 1) * CW)
for i, (n, pl, ac) in enumerate(SCH, 1):
    y = GY + i * RH
    grp = pl is None
    gcell(L, y, NW, PALE if grp else 'FFFFFF', n, bold=grp, align=PP_ALIGN.LEFT, indent=0 if grp else 274320)
    for j in range(6):
        gcell(X0 + j * CW, y, CW, 'E5E7EB' if j == 5 else (PALE if grp else 'FFFFFF'))
    if grp:
        kids = []
        for n2, pl2, ac2 in SCH[i:]:
            if pl2 is None: break
            if pl2 != 'mark': kids += ac2
        x, w = span(kids); rect(s, x, y + 91440, w, 76200, NAVY)
    elif pl == 'mark':
        rect(s, X0 + 4 * CW + int(CW * 9 / 31) - 64008, y + 45720, 128016, 167640, RED)
    else:
        x, w = span(pl); rect(s, x + 18288, y + 45720, w - 36576, 64008, PLAN_C)
        x, w = span(ac); rect(s, x + 18288, y + 128016, w - 36576, 91440, ACT_C)
order.append(s)
# --- 4. 수행조직: 번호 띠 + 조직도 + 분야별 표 2개
s = page(C1, '4. 수행조직', '사업수행 조직 구성', '4.')
CX, OW = L + W // 2, 3200400
y = TOP - 45720
for k, (hd, val) in enumerate([('발 주 처', '한국수력원자력(주)'), ('수 행 기 관', '국민대학교 산학협력단'), ('책임연구원(1인)', '신주영 교수')]):
    rect(s, CX - OW // 2, y, OW, 301752, NAVY)
    _mid(put(s, 'bold14', CX - OW // 2, y, OW, 301752, hd, size=14, color='FFFFFF', align=PP_ALIGN.CENTER))
    rect(s, CX - OW // 2, y + 301752, OW, 356616, 'E5E7EB')
    _mid(put(s, 'bold14', CX - OW // 2, y + 301752, OW, 356616, val, size=15, color=INK, align=PP_ALIGN.CENTER))
    y += 658368
    rect(s, CX - 6350, y, 12700, 118872, NAVY); y += 118872
TW = (W - 274320) // 2
XA, XB = L, L + W - TW
rect(s, XA + TW // 2, y - 6350, XB - XA, 12700, NAVY)
for x in (XA, XB):
    rect(s, x + TW // 2 - 6350, y, 12700, 146304, NAVY)
ty = y + 146304
for x, hd, rows in ((XA, '수자원 분야 (과업 1·2)', [['책임연구원', '신주영', '수공학 박사', '용역 총괄, 댐 운영 의사결정 및\n수자원 분야 기술 검토'], ['연구보조원', '문경민', '수공학 학사', '데이터 파이프라인·온톨로지\n조사 지원']]),
                    (XB, '인공지능 분야 (과업 3·4)', [['연구원', '김장호', '인공지능 박사', 'sLLM 후보군 평가,\n모델 구조·특성 검토'], ['연구보조원', '황솔희', '인공지능 학사', 'sLLM 후보 모델 조사·비교 지원']])):
    g = tbl(s, [[hd, '', '', ''], ['구분', '성명', '전공 · 학위', '담당 업무']] + rows, [20, 14, 24, 42], x=x, y=ty, w=TW, row_h=420000, size=12, head_fill='C9D9EE')
    g.cell(0, 0).merge(g.cell(0, 3))
    for r in g.cell(0, 0).text_frame.paragraphs[0].runs: r.font.size = Pt(15)
    g.rows[2].height = g.rows[3].height = Emu(777240)
    for j in range(4):
        c = g.cell(1, j); c.fill.solid(); c.fill.fore_color.rgb = RGBColor.from_string(PALE)
        for pp in c.text_frame.paragraphs:
            pp.alignment = PP_ALIGN.CENTER
            for r in pp.runs: r.font.bold = True; r.font.color.rgb = RGBColor.from_string(NAVY)
    for i in (2, 3):
        for j in (1, 2, 3):
            for pp in g.cell(i, j).text_frame.paragraphs: pp.alignment = PP_ALIGN.CENTER
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
XR = L + HW + 182880
HEADC = 'C9D9EE'


def one(head, checks, rows, widths, size=11):
    """1-1 예시: 상자 하나에 소제목, 체크 줄, 표. 표는 남은 높이에 맞춘다."""
    s = page(C2, ITEMS[0][0], '수자원 분야 사례 조사', '1-1')
    yy = panel(s, L, PY, W, PH, head, checks)
    rh = (PY + PH - 91440 - yy - 27432) // len(rows)
    tbl(s, rows, widths, x=L + 100584, y=yy + 27432, w=W - 201168, row_h=min(rh, 520000), size=size, head_fill=HEADC, tight=True)
    order.append(s)


def two(lhead, rows, widths, rhead, checks, size=11):
    """1-1 예시: 왼쪽 상자에 표, 오른쪽 상자에 체크 줄."""
    s = page(C2, ITEMS[0][0], '수자원 분야 사례 조사', '1-1')
    yy = panel(s, L, PY, HW, PH, lhead, [])
    rh = (PY + PH - 91440 - yy) // len(rows)
    g = tbl(s, rows, widths, x=L + 100584, y=yy, w=HW - 201168, row_h=min(rh, 420000), size=size, head_fill=HEADC, tight=True)
    i = 1
    while i < len(rows):                                         # 같은 분류 기준은 한 칸으로 합친다
        j = i
        while j + 1 < len(rows) and rows[j + 1][0] == rows[i][0]: j += 1
        for k in range(i + 1, j + 1): g.cell(k, 0).text_frame.paragraphs[0].runs[0].text = ''
        if j > i: g.cell(i, 0).merge(g.cell(j, 0))
        c = g.cell(i, 0); c.fill.solid(); c.fill.fore_color.rgb = RGBColor.from_string(PALE)
        i = j + 1
    for i in range(1, len(rows)):
        for j in (1, 2): g.cell(i, j).text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    panel(s, XR, PY, HW, PH, rhead, checks, size=13)
    order.append(s)


# ① 조사 개요
one('조사 대상 문헌의 구성 (63편)', [
    '수자원 분야의 LLM 활용 사례를 RAG 기반 질의응답, 도메인 특화 LLM, 운영지식 구조화(온톨로지·KG)의 세 유형으로 나누어 63편 조사',
    '수자원 분야(댐·수리시설, 홍수, 수문·수자원 일반) 문헌은 36편이며, 댐·수리시설 14편 중 7편이 운영지식 구조화 유형',
    '2025~2026년 게재 문헌이 46편이며, 유형마다 조사 → 분류 → 주요 항목 비교 → 주요 사례 상세 비교 → 검토 결과의 순서로 정리'],
    [['유형', '합계', '댐·수리시설', '홍수', '수문·수자원 일반', '수자원 외', '학술지', '학술대회', '사전 공개본'],
     ['RAG 기반 질의응답', '21', '4', '7', '6', '4', '11', '2', '8'],
     ['도메인 특화 LLM', '18', '3', '1', '6', '8', '11', '1', '6'],
     ['운영지식 구조화(온톨로지·KG)', '24', '7', '2', '0', '15', '16', '4', '3'],
     ['합계', '63', '14', '10', '12', '27', '38', '7', '17']],
    [24, 8, 11, 8, 13, 10, 8, 9, 9], size=13)
# ② RAG 기반 질의응답: 분류와 검토 결과
two('RAG 기반 질의응답 21편의 분류', [['분류 기준', '구분', '편수'],
    ['지식 구조', '온톨로지+KG', '4'], ['지식 구조', 'KG', '3'], ['지식 구조', '사용 안 함', '14'],
    ['검색 방식', '희소+벡터', '5'], ['검색 방식', '벡터', '4'], ['검색 방식', '그래프 질의', '3'], ['검색 방식', '그래프+벡터', '3'], ['검색 방식', '도구 호출', '5'], ['검색 방식', '규칙 기반', '1'],
    ['생성 모델 운용', '상용 API', '9'], ['생성 모델 운용', '공개 모델 로컬', '8'], ['생성 모델 운용', '상용 API·공개 모델 병행', '3'], ['생성 모델 운용', '논문에 제시되지 않음', '1']],
    [30, 50, 20], '검토 결과', [
    '21편 가운데 17편이 생성 모델을 미세조정하지 않고 검색 근거만으로 구성',
    '규정·매뉴얼 등 문서 자료는 검색으로, 수문 자료 등 정형 자료는 조회 도구로 나누는 구성이 확인',
    'KG를 넣은 구성은 LLM 단독 구성보다 높은 수치가 보고되었으나, KG만 쓴 구성은 답변 범위가 제한',
    '근거를 찾지 못한 질의에 답하지 않도록 한 설계와, 빠진 조건을 되물어 보완하는 절차가 확인',
    '사람 평가자의 채점을 포함한 사례는 21편 가운데 6편'])
# ③ RAG 기반 질의응답: 주요 사례 상세 비교
one('RAG 기반 질의응답: 주요 3개 사례의 상세 비교', [
    'KG와 문서 검색을 함께 쓴 수리 분야 사례 2편과, 문서 검색에 실시간 수문 자료 호출을 결합한 사례 1편을 같은 항목으로 비교'],
    [['항목', 'KGL 수리시설 점검 QA (Yang 외, 2024)', '수리 지식 QA 라우팅 (Han 외, 2026)', 'WaterCopilot (Vickneswaran 외, 2026)'],
     ['풀려는 문제', '위험 유형·발생 부위가 빠진 점검 질의의 단계적 명확화', '단일 출처 질의응답의 답변 범위 불완전', '흩어진 정책 문서와 실시간 수문 자료의 단일 창구 통합'],
     ['근거 자료', '점검 보고서·기록 글 4,292건, 점검 질문 3,321건', 'KG 개체 50만 개 이상·관계 120만 개, 문서 150건', '정책·보고서 PDF, 실시간 수문 자료 API'],
     ['지식 구조', '개체 6종·관계 5종 온톨로지, T5 추출', '기존 수리 KG', '사용 안 함'],
     ['검색 방식', '명확화 경로 벡터 검색', 'KG 질의 + 문서 벡터 검색', '벡터 + 메타데이터 필터, API 도구 호출'],
     ['생성 모델', 'GPT-4 호출', 'ChatGLM2-6B (로컬 사설 배치)', 'GPT 기반 (클라우드)'],
     ['평가 방법', '각 100문항, 석사과정생 3명 채점', '질문 500개 전문가 3명 정답 판정', '질문 30개, RAGAS 4개 지표'],
     ['대표 결과', 'MRR 0.783 (KG 기반 0.617, LLM 기반 0.604)', '종단 정확도 86.4% (KG-Only 48.4%, LLM-Only 73.5%)', 'RAGAS Score 약 0.8043'],
     ['한계', '수리 점검 KG만으로 평가', '기존 KG의 포괄 범위 부족', '표·그림 내용 미추출, 사람 평가 없음']],
    [13, 29, 29, 29])
# ④ 도메인 특화 LLM: 분류와 검토 결과
two('도메인 특화 LLM 18편의 분류', [['분류 기준', '구분', '편수'],
    ['연구 유형', '모델 개발', '8'], ['연구 유형', '시스템 구축', '3'], ['연구 유형', '벤치마크·평가', '3'], ['연구 유형', '조사·전망', '3'], ['연구 유형', '방법 제안', '1'],
    ['미세조정 방식', 'LoRA 계열', '7'], ['미세조정 방식', '추가 사전학습+미세조정', '3'], ['미세조정 방식', '방식 미기재', '1'], ['미세조정 방식', '안 함', '7']],
    [30, 50, 20], '검토 결과', [
    '미세조정한 생성 모델의 기반이 명시된 10편은 모두 공개 가중치 모델',
    '추가 사전학습 사례 가운데 토큰 수를 밝힌 2편은 10억 토큰 이상의 말뭉치를 사용',
    'LoRA 미세조정 사례는 수천~십만 건 규모의 질의응답·지시문 자료를 사용',
    '분야 미세조정에 따른 일반 능력 또는 유용성의 하락이 2편에서 보고',
    '저수지 운영 규정 질의응답을 대상으로 한 평가 자료는 18편 안에서 확인되지 않음'])
# ⑤ 도메인 특화 LLM: 주요 사례 상세 비교
one('도메인 특화 LLM: 주요 3개 사례의 상세 비교', [
    '추가 사전학습과 전체 미세조정, LoRA 미세조정의 모델 규모 비교, 공개 모델에 검색과 KG를 결합한 사례를 같은 항목으로 비교'],
    [['항목', 'WaterGPT (Ren 외, 2024)', 'HydroLLM (Kizilkaya 외, 2025)', 'CSKR-LLM-HWCEC (Chen 외, 2026)'],
     ['접근', '추가 사전학습 + 전체 미세조정', 'LoRA 미세조정의 모델 규모 비교', '공개 모델에 벡터 검색과 KG 결합'],
     ['자료', '말뭉치 약 10.97억 토큰, SFT 단일 10만 쌍·다중 3천 건', '교과서·논문 2,000편에서 만든 QA 약 8,800쌍', '안전 표준 41건, 조항 약 30,800개'],
     ['기반 모델', 'Qwen2-7B-Instruct', '공개 모델 6종 (1.5B~32B)', 'Qwen2.5-14B'],
     ['지식 구조·검색', '사용 안 함, 도구·DB 호출', '사용 안 함', 'KG(1만 노드 초과), 벡터 검색과 KG 개체 대조'],
     ['운영 환경', 'A800 GPU 1장 추론', 'H100 NVL 2장 실험', 'A6000 GPU 2장 추론, 로컬 지식 기반'],
     ['평가 방법', 'EvalWater 10,202문항 정확도', '벤치마크 형식별 정확도·코사인 유사도', '전문가 5명 100문항 5점 채점, Rouge·Bleu'],
     ['대표 결과', 'EvalWater 83.09 (원본 66.18, GPT-4-turbo 65.26)', '8B 모델 평균 75.7%로 최고, 32B 모델 과적합', 'Rouge-L 0.1460 (ChatGPT-4.0 0.0800)'],
     ['한계', '일반 능력 평가(Ceval) 약 8점 하락', '자료 규모가 작아 일반화 제한', 'KG가 표준 41건에 의존']],
    [13, 29, 29, 29])
# ⑥ 운영지식 구조화: 분류와 검토 결과
two('운영지식 구조화 24편의 분류', [['분류 기준', '구분', '편수'],
    ['대상 분야', '댐·수리시설', '7'], ['대상 분야', '홍수', '2'], ['대상 분야', '수자원 외', '15'],
    ['지식 구조의 종류', '온톨로지+KG', '15'], ['지식 구조의 종류', 'KG', '6'], ['지식 구조의 종류', '사용 안 함', '3'],
    ['KG 구축 방식', '수작업·규칙', '7'], ['KG 구축 방식', '전통 NLP 모델', '3'], ['KG 구축 방식', 'LLM 추출', '6'], ['KG 구축 방식', '혼합', '5'], ['KG 구축 방식', '해당 없음', '3']],
    [30, 50, 20], '검토 결과', [
    '자료의 유형에 따라 KG 구축 방식이 다르므로, 자료 유형별로 구축 방식을 나누어 정할 필요',
    '수치 자료를 KG에 복제하지 않고 DB에 둔 채 연결한 사례가 확인',
    '온톨로지로 LLM의 추출·분류 결과를 제약한 사례가 확인',
    '평가는 추출 품질, 질의 결과, 후속 작업의 성능 가운데 일부만 다룸',
    '댐 운영 규정 문서를 KG로 구조화한 과정을 제시한 사례는 조사 문헌에서 확인되지 않음'])
# ⑦ 운영지식 구조화: 주요 사례 상세 비교
one('운영지식 구조화: 댐 분야 온톨로지·KG 구축 사례 3편의 비교', [
    '댐 안전평가 보고서의 구조화, 계측 자료의 통합, 결함 진단을 대상으로 한 댐 분야 사례 3편을 같은 항목으로 비교'],
    [['항목', 'DDKG (Huang 외, 2026)', 'OntoDSMS (Zhou 외, 2023)', '중력댐 결함 진단 KG (Pei 외, 2026)'],
     ['풀려는 문제', '보고서에 흩어진 결함 정보의 구조화', '이질적인 감시 자료의 통합', '결함 진전 경로와 원인의 진단'],
     ['자료', '댐 22,076개 안전평가 보고서, 구조화 표', '댐 1개(센서 179개)의 BIM, 계측 자료 DB', '점검 보고서 2건, 2017~2022년 계측 자료'],
     ['온톨로지 설계', '7단계 방법, OWL', '7단계 방법, SSN/SOSA 재사용', '7단계 방법과 하향식 접근'],
     ['KG 구축 방법', '정규식, LLM 추출·분할, LoRA 미세조정 LLM 분류, 전문가 검토', '관계형 DB를 온톨로지에 사상(가상 그래프)', '프롬프트 제약 LLM의 트리플 추출'],
     ['KG 규모', '노드 201,362개, 관계 953,447개', '두 시스템의 개체 492,875개', '노드 126개, 관계 438개'],
     ['질의·활용', '다중 제약 검색, 유역 결함 분석', '질의, 규칙 추론으로 이상 센서 판별', '결함 경로 양방향 추론'],
     ['대표 결과', '분류 F1 92.87%, 90.76%', '질의 응답 0.26초 (SQL 2.72초)', '프롬프트 제약으로 precision 약 12% 향상'],
     ['한계', 'KG 자체의 체계적 평가 부재', 'BIM의 비기하 속성만 고려', '시간에 따라 변하는 환경 하중 미고려']],
    [13, 29, 29, 29])
# ⑧ 유형 간 비교
one('세 유형의 비교', [
    '세 유형은 분야 지식을 두는 곳(문서 저장소, 모델의 가중치, 온톨로지·KG)에서 구분',
    'RAG 기반 질의응답 21편 중 7편이 KG를 근거 저장소로 함께 사용하여, 유형을 결합한 구성이 확인'],
    [['항목', 'RAG 기반 질의응답', '도메인 특화 LLM', '운영지식 구조화'],
     ['지식을 두는 곳', '문서 저장소(벡터·희소 색인), 일부는 KG와 병행', '모델의 가중치', '온톨로지와 KG의 개체·관계'],
     ['지식의 반영 방법', '질의 시점에 검색하여 프롬프트에 포함', '추가 사전학습, 미세조정', '자료에서 개체·관계를 추출하여 구축'],
     ['자료의 갱신', '저장소의 문서를 교체', '모델을 다시 학습', 'KG의 개체·관계를 추가·수정'],
     ['응답의 근거 제시', '검색한 문서나 KG 항목을 근거로 제시 가능', '가중치에 학습된 지식은 출처 제시가 어려움', '개체·관계와 출처 속성으로 근거 추적 가능'],
     ['평가 방식', '검색 지표, 답변 지표, LLM 채점, 전문가 채점', '객관식 정확도, 유사도 지표, LLM 채점, 전문가 채점', '추출 품질, 질의 결과의 일치, 후속 작업의 성능'],
     ['확인된 한계', '표·그림이 든 문서의 처리, 상용 API 의존 구성의 모델 교체', '분야 미세조정에 따른 일반 능력 하락 보고 2편', 'KG 자체의 완전성 평가 부재, 시계열 자료 통합']],
    [16, 28, 28, 28], size=12)
# ⑨ 시사점
s = page(C2, ITEMS[0][0], '수자원 분야 사례 조사', '1-1')
panel(s, L, PY, HW, PH, '댐 운영 의사결정 지원에 대한 시사점 (1)', [
    '근거를 제시하는 구조: 지식을 가중치에만 두는 구성보다 검색 근거나 KG 항목을 응답에 연결하는 구성이 근거 제시에 적합',
    '문서 자료와 정형 자료의 구분: 규정·매뉴얼은 검색으로, 수위·방류량 등 수치 자료는 조회 도구나 DB 연결로 구분',
    '운영지식의 구조화: 댐 운영(방류 승인, 운영 기준, 수문 상태)을 대상으로 한 온톨로지는 별도로 설계할 필요'], size=14)
panel(s, XR, PY, HW, PH, '댐 운영 의사결정 지원에 대한 시사점 (2)', [
    '운용 환경: 내부 자료를 다루는 환경에서는 공개 모델의 내부 구동을 전제로 구성을 검토할 필요',
    '평가 자료의 확보: 댐 운영 업무의 질의 유형을 정하고 운영 실무자가 참여하는 평가 자료를 마련할 필요',
    '적용 범위의 한정: LLM은 근거 자료의 검색과 정리를 맡고 최종 판단은 운영자가 하는 구성이 적절'], size=14)
order.append(s)
# --- 나머지 항목: 항목마다 2장, 번호 띠와 빈 상자 2개. 인공지능학과 담당 쪽에는 메모를 단다
for fi, (field, subs) in enumerate(ITEMS):
    for sub in subs:
        num, name = sub.split(' ', 1)
        if num == '1-1':
            continue
        for _ in range(2):
            s = page(C2, field, name, num)
            panel(s, L, PY, HW, PH)
            panel(s, XR, PY, HW, PH)
            if fi >= 2:
                MEMO[len(order)] = '[인공지능학과 작성] %s %s: 상자 머리(ㅇ)에 소제목, 체크 줄에 요지, 그 아래에 표나 그림을 넣어 작성. 1-1 슬라이드를 예시로 참고. 상자 수와 크기는 내용에 맞게 조정하고, 장이 모자라면 슬라이드를 복제' % (num, name)
            order.append(s)

# ================================================================== Ⅲ 향후 추진계획
order.append(divider('Ⅲ', '향후 추진계획', '과업 분야별 향후 추진계획'))
for k, (field, subs) in enumerate(ITEMS, 1):
    s = page('Ⅲ. 향후 추진계획', '향후 추진계획', field.split('. ', 1)[1], '과업%d' % k)
    for y, h in ((TOP - 45720, 762000), (TOP + 1371600, 1357971), (TOP + 3383280, 762000)):
        put(s, 'bold14', L, y, 502920, 283464, 'ㅇ', size=14, color=NAVY)
        rect(s, L + 137160, y + 347472, W - 137160, h, INNER, line=FRAME, round_=True)
    if k >= 3:
        MEMO[len(order)] = '[인공지능학과 작성] 과업%d %s의 향후 추진계획: ㅇ에 소제목, 상자 안에 내용을 작성' % (k, field.split('. ', 1)[1])
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


def add_memos(path, memos, author='Claude'):
    """저장한 pptx에 메모(댓글)를 단다. memos: {슬라이드 순번(0부터): 글}. 저장하면 슬라이드 파일 이름이 순서대로 매겨진다."""
    import zipfile, shutil, re
    from xml.sax.saxutils import escape
    tmp = path + '.tmp'; zi = zipfile.ZipFile(path); zo = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
    PNS = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
    REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/'
    HEAD = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    for it in zi.infolist():
        data = zi.read(it.filename)
        if it.filename == 'ppt/commentAuthors.xml':
            continue                                         # 기준 발표자료의 작성자 목록은 새로 쓴다
        if it.filename == '[Content_Types].xml':
            data = re.sub(r'<Override PartName="/ppt/commentAuthors.xml"[^>]*/>', '', data.decode()).encode()
            add = '<Override PartName="/ppt/commentAuthors.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.commentAuthors+xml"/>'
            add += ''.join('<Override PartName="/ppt/comments/comment%d.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.comments+xml"/>' % (k + 1) for k in range(len(memos)))
            data = data.decode().replace('</Types>', add + '</Types>').encode()
        elif it.filename == 'ppt/_rels/presentation.xml.rels':
            data = re.sub(r'<Relationship [^>]*commentAuthors[^>]*/>', '', data.decode()).encode()
            data = data.decode().replace('</Relationships>', '<Relationship Id="rIdCmAuth" Type="%scommentAuthors" Target="commentAuthors.xml"/></Relationships>' % REL).encode()
        else:
            m = re.match(r'ppt/slides/_rels/slide(\d+)\.xml\.rels$', it.filename)
            if m and int(m.group(1)) - 1 in memos:
                k = sorted(memos).index(int(m.group(1)) - 1) + 1
                data = data.decode().replace('</Relationships>', '<Relationship Id="rIdCm" Type="%scomments" Target="../comments/comment%d.xml"/></Relationships>' % (REL, k)).encode()
        zo.writestr(it, data)
    zo.writestr('ppt/commentAuthors.xml', HEAD + '<p:cmAuthorLst %s><p:cmAuthor id="1" name="%s" initials="C" lastIdx="%d" clrIdx="0"/></p:cmAuthorLst>' % (PNS, author, len(memos)))
    for k, i in enumerate(sorted(memos), 1):
        zo.writestr('ppt/comments/comment%d.xml' % k, HEAD + '<p:cmLst %s><p:cm authorId="1" dt="2026-11-23T21:00:00.000" idx="%d"><p:pos x="1745" y="663"/><p:text>%s</p:text></p:cm></p:cmLst>' % (PNS, k, escape(memos[i])))
    zo.close(); zi.close(); shutil.move(tmp, path)


add_memos(OUT, MEMO)
print('저장', OUT, '슬라이드', len(prs.slides))
