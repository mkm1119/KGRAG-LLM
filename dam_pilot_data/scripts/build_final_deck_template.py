#!/usr/bin/env python3
"""최종보고회 발표자료 템플릿(pptx). 11/26 한강수력본부 발표자료의 디자인(글꼴, 색, 머리글 배치)을 그대로 쓰고,
구성은 표지 → 목차 → Ⅰ 과업개요 → Ⅱ 사업수행 결과(과업 세부 항목 12개) → Ⅲ 향후 추진계획 → 맺음으로 잡는다.
새 슬라이드는 기준 발표자료의 도형을 복사해 만들므로 서식이 같다.
사용: python3 -I dam_pilot_data/scripts/build_final_deck_template.py <기준 발표자료.pptx> <출력.pptx>
"""
import copy, sys
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


def rect(slide_or_layout, x, y, w, h, fill, line=None, round_=False):
    e = copy.deepcopy(P['card']); slide_or_layout.shapes._spTree.append(e)
    sh = slide_or_layout.shapes[-1]
    _n[0] += 1; e.nvSpPr.cNvPr.set('id', str(_n[0]))
    sh.left, sh.top, sh.width, sh.height = Emu(x), Emu(y), Emu(w), Emu(h)
    if not round_:
        e.spPr.find(NS + 'prstGeom').set('prst', 'rect')
        for av in e.spPr.find(NS + 'prstGeom').findall(NS + 'avLst'):
            for g in list(av): av.remove(g)
    sh.fill.solid(); sh.fill.fore_color.rgb = RGBColor.from_string(fill)
    if line:
        sh.line.color.rgb = RGBColor.from_string(line); sh.line.width = Pt(1.25)
    else:
        sh.line.fill.background()
    return sh


# 본문 레이아웃에 제목 띠와 아래 선을 넣는다(슬라이드마다 그리지 않고 바탕에 둠)
_lay = prs.slide_layouts[1]
_b1 = rect(_lay, 0, 0, 12192000, BAND_H, PALE); _b2 = rect(_lay, 0, BAND_H, 12192000, 36576, NAVY); _b3 = rect(_lay, L, 6373368, W, 12700, 'B6BCC6')
for _b in (_b3, _b2, _b1):                               # 로고보다 뒤로 보낸다
    _lay.shapes._spTree.remove(_b._element); _lay.shapes._spTree.insert(2, _b._element)


def page(label, title, sub, num=None):
    """label: 장 이름(오른쪽 위 꼬리표), title: 과업 분야(제목 띠), sub: 세부 항목 이름(번호 띠), num: 세부 항목 번호"""
    s = new(1)
    put(s, 'title', L - 91440, 100584, 6400800, 466344, title, size=24)
    rect(s, 9601200, BAND_H + 36576, 2590800, 301752, NAVY)
    put(s, 'bold14', 9601200, BAND_H + 54864, 2590800, 265176, label, size=11, color='FFFFFF', align=PP_ALIGN.CENTER)
    rect(s, L, BAR_Y, W, BAR_H, 'DCE9F7', round_=True)
    if num:
        rect(s, L, BAR_Y, 960120, BAR_H, NAVY, round_=True)
        put(s, 'bold14', L, BAR_Y + 45720, 960120, 301752, num, size=15, color=GOLD, align=PP_ALIGN.CENTER)
    put(s, 'bold14', L + (1051560 if num else 182880), BAR_Y + 45720, W - 1234440, 301752, sub, size=15, color=NAVY)
    put(s, 'num', 11155680, 6446520, 548640, 274320, '0')
    return s


def panel(s, x, y, w, h, head=None, hints=None, ink=False):
    """머리 칸이 있는 테두리 상자. head: 소제목, hints: ✓ 요지(줄 목록). 둘 다 비우면 작성용 빈 상자(ㅇ)"""
    rect(s, x, y, w, h, 'FFFFFF', line='7F9CC0', round_=True)
    rect(s, x, y, w, 420624, PALE, line='7F9CC0', round_=True)
    rect(s, x + 137160, y - 45720, 201168, 384048, NAVY)
    put(s, 'bold14', x + 430000, y + 54864, w - 520000, 301752, head or 'ㅇ', size=14, color=NAVY)
    put(s, 'body', x + 182880, y + 530352, w - 365760, 320040, '\n'.join('✓ ' + t for t in (hints or ['ㅇ'])), size=13, color=INK if ink else GRAY)


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
# ------------------------------------------------------------------ 작성 안내(제출 전 삭제)
GUIDE = '작성 안내 (제출 전 삭제)'
s = page(GUIDE, '작성 기준', '아래 기준에 맞춰 Ⅱ장의 담당 슬라이드를 작성. 이 슬라이드는 제출 전에 삭제')
tbl(s, [['구분', '기준'],
        ['글꼴', '한컴산뜻돋움 (모든 글)'],
        ['슬라이드 머리', '제목 띠: 과업 분야 이름 / 오른쪽 위 꼬리표: 장 이름 / 번호 띠: 세부 항목 번호(1-1)와 이름'],
        ['본문 글', '개조식 명사형 종결("~을 정리", "~으로 구성"). 본문 14~16pt, 표 안의 글 11~13pt'],
        ['색', '남색 003B71(제목·강조), 파랑 0070C0(구분), 연한 파랑 EEF5FC·DCE9F7(바탕), 회색 6B7280(설명), 본문 2B2B2B'],
        ['슬라이드 구성', '세부 항목마다 번호 띠 아래에 상자를 두고, 상자 머리에 소제목, 상자 안에 ✓ 요지 2~4줄과 표·그림을 배치. 상자의 수와 크기는 내용에 맞게 조정하고, 한 장을 넘으면 슬라이드를 복제하여 사용'],
        ['작성 예시', 'Ⅱ장의 1-1 슬라이드 3장(글과 표, 표 중심, 글과 그림)을 예시로 작성해 두었으며, 나머지 항목은 같은 방식으로 작성'],
        ['표와 그림', '표 제목은 표 위, 그림 제목은 그림 아래. 출처가 있으면 아래에 "자료: 저자(연도)"로 표기'],
        ['분량', '세부 항목마다 1~3장. 전체 발표 시간에 맞춰 조정']],
    [16, 84], y=TOP, row_h=440000, size=13)
order.append(s)
HW = (W - 182880) // 2
# 목차는 기준 슬라이드의 카드 3개를 그대로 쓰고 머리글만 새 양식에 맞춘다
for sh in list(toc.shapes):
    if sh.name == 'Text 2':
        sh._element.getparent().remove(sh._element)
    elif sh.name == 'Text 3':
        sh.left, sh.top, sh.width, sh.height = Emu(L - 91440), Emu(100584), Emu(6400800), Emu(466344)
        for r in sh.text_frame.paragraphs[0].runs: r.font.size = Pt(24)
    elif sh.name == 'Text 4':
        sh.top = Emu(1005840)
order.append(toc)

# ------------------------------------------------------------------ Ⅰ 과업개요
order.append(divider('Ⅰ', '과업개요', '목적 및 배경, 과업범위, 추진 일정, 수행조직'))
C1 = 'Ⅰ. 과업개요'
s = page(C1, '1. 목적 및 배경', '과업의 기본 정보와 추진 배경, 목적')
tbl(s, [['구분', '내용'],
        ['과업명', '댐 운영 의사결정 프레임워크 구축 자문 용역'],
        ['발주기관', '한국수력원자력(주)'],
        ['수행기관', '국민대학교 산학협력단'],
        ['과업기간', '2026. 07. 23. ~ 2027. 01. 22. (착수일로부터 6개월)'],
        ['책임연구원', '국민대학교 신주영 교수']],
    [22, 78], y=TOP, w=HW, row_h=700000, size=14)
X2 = L + HW + 182880
panel(s, X2, TOP, HW, 2011680, '추진 배경', ['댐 운영은 수문 자료뿐 아니라 과거 운영 경험, 매뉴얼, 관련 법령 등 비정형 자료에 대한 종합 판단이 필요', '이를 정형화하여 의사결정에 연결하는 모델·시스템이 부재'])
panel(s, X2, TOP + 2194560, HW, 2011680, '목적', ['sLLM 기반 댐 운영 의사결정 및 발전 최적화 프레임워크 구축을 위한 기술적 타당성 검토'])
order.append(s)
s = page(C1, '2. 과업범위', '4개 분야, 세부 항목 12개')
tbl(s, [['과업 분야', '세부 항목', '담당'],
        ['1. 국내외 기술 트렌드 조사', '1-1 수자원 분야 사례 조사\n1-2 국내 운영 여건 조사\n1-3 적용 기술요소 및 모델 제안', '수자원 연구실'],
        ['2. LLM 활용 데이터 파이프라인 조사', '2-1 수집 경로 조사\n2-2 온톨로지·메타데이터 설계방안 조사\n2-3 RAG-LLM 통합 파이프라인(안) 제시', '수자원 연구실'],
        ['3. sLLM 후보군 평가 방향', '3-1 후보 모델 조사\n3-2 모델 구조 및 특성 검토\n3-3 후보군 적용방안 제시', '인공지능학과'],
        ['4. 도메인 특화 성능 향상 전략', '4-1 RAG 기반 적용방안 조사\n4-2 경량 미세조정 방식 검토\n4-3 성능 향상 전략 제시', '인공지능학과']],
    [32, 50, 18], y=TOP, row_h=930000, size=14)
order.append(s)
s = page(C1, '3. 추진 일정', '세부 항목별 수행 기간 (착수 후 6개월)')
M = ["'26.8", "'26.9", "'26.10", "'26.11", "'26.12", "'27.1"]
SCH = [('1. 국내외 기술 트렌드 조사', None), ('1-1 수자원 분야 사례 조사', [1]), ('1-2 국내 운영 여건 조사', [1]), ('1-3 적용 기술요소 및 모델 제안', [2, 3]),
       ('2. LLM 활용 데이터 파이프라인 조사', None), ('2-1 수집 경로 조사', [2]), ('2-2 온톨로지·메타데이터 설계방안 조사', [2]), ('2-3 RAG-LLM 통합 파이프라인(안) 제시', [3, 4]),
       ('3. sLLM 후보군 평가 방향', None), ('3-1 후보 모델 조사', [3]), ('3-2 모델 구조 및 특성 검토', [3, 4]), ('3-3 후보군 적용방안 제시', [5]),
       ('4. 도메인 특화 성능 향상 전략', None), ('4-1 RAG 기반 적용방안 조사', [4]), ('4-2 경량 미세조정 방식 검토', [4, 5]), ('4-3 성능 향상 전략 제시', [6]),
       ('5. 최종 보고서 작성', [5, 6])]
gt = tbl(s, [['수행 내용'] + M] + [[('' if ms is None or n.startswith('5.') else '   ') + n] + ['' for _ in M] for n, ms in SCH], [40, 10, 10, 10, 10, 10, 10], y=TOP, row_h=262000, size=11, first_col_bold=False, tight=True)
for i, (n, ms) in enumerate(SCH, 1):
    if ms is None:
        for j in range(7):
            c = gt.cell(i, j); c.fill.solid(); c.fill.fore_color.rgb = RGBColor.from_string(PALE)
        for r in gt.cell(i, 0).text_frame.paragraphs[0].runs: r.font.bold = True
        continue
    for j in ms:
        c = gt.cell(i, j); c.fill.solid(); c.fill.fore_color.rgb = RGBColor.from_string(BLUE)
order.append(s)
s = page(C1, '4. 수행조직', '사업수행 조직 구성', '4.')
CX, BWD, BH = L + W // 2, 3383280, 347472


def obox(s, x, y, w, h, text, fill, color, line=None, size=13):
    rect(s, x, y, w, h, fill, line=line, round_=True)
    put(s, 'bold14', x, y + (h - 290000) // 2 - (110000 if '\n' in text else 0), w, 290000, text, size=size, color=color, align=PP_ALIGN.CENTER)


y0 = TOP
for k, (t, fill, col, ln) in enumerate([('발주기관  |  한국수력원자력(주)', NAVY, 'FFFFFF', None), ('수행기관  |  국민대학교 산학협력단', BLUE, 'FFFFFF', None), ('책임연구원  |  신주영 (수공학)', PALE, NAVY, '7F9CC0')]):
    obox(s, CX - BWD // 2, y0 + k * (BH + 118872), BWD, BH, t, fill, col, ln)
    rect(s, CX - 6350, y0 + k * (BH + 118872) + BH, 12700, 118872, NAVY)
yb = y0 + 3 * (BH + 118872)                       # 가지가 갈라지는 높이
XL, XR = L + W // 4, L + 3 * W // 4
rect(s, XL, yb - 6350, XR - XL, 12700, NAVY)
for xc, t in ((XL, '수자원 분야 (과업 1·2)\n책임연구원 신주영, 연구보조원 문경민'), (XR, '인공지능 분야 (과업 3·4)\n연구원 김장호, 연구보조원 황솔희')):
    rect(s, xc - 6350, yb, 12700, 118872, NAVY)
    obox(s, xc - 2286000, yb + 118872, 4572000, 594360, t, 'FFFFFF', NAVY, '7F9CC0', size=12)
tbl(s, [['구분', '성명', '전공 분야', '학위', '담당 업무'],
        ['책임연구원', '신주영', '수공학', '박사', '용역 총괄, 댐 운영 의사결정 및 수자원 분야 기술 검토'],
        ['연구원', '김장호', '인공지능', '박사', 'sLLM 후보군 평가, 모델 구조·특성 검토'],
        ['연구보조원', '문경민', '수공학', '학사', '데이터 파이프라인·온톨로지 조사 지원'],
        ['연구보조원', '황솔희', '인공지능', '학사', 'sLLM 후보 모델 조사·비교 지원']],
    [15, 12, 14, 9, 50], y=yb + 118872 + 594360 + 182880, row_h=380000, size=12)
order.append(s)

# ------------------------------------------------------------------ Ⅱ 사업수행 결과
order.append(divider('Ⅱ', '사업수행 결과', '과업 4개 분야, 세부 항목 12개의 수행 결과'))
ITEMS = [('1. 국내외 기술 트렌드 조사', '수자원 연구실', ['1-1 수자원 분야 사례 조사', '1-2 국내 운영 여건 조사', '1-3 적용 기술요소 및 모델 제안']),
         ('2. LLM 활용 데이터 파이프라인 조사', '수자원 연구실', ['2-1 수집 경로 조사', '2-2 온톨로지·메타데이터 설계방안 조사', '2-3 RAG-LLM 통합 파이프라인(안) 제시']),
         ('3. sLLM 후보군 평가 방향', '인공지능학과', ['3-1 후보 모델 조사', '3-2 모델 구조 및 특성 검토', '3-3 후보군 적용방안 제시']),
         ('4. 도메인 특화 성능 향상 전략', '인공지능학과', ['4-1 RAG 기반 적용방안 조사', '4-2 경량 미세조정 방식 검토', '4-3 성능 향상 전략 제시'])]
HW = (W - 182880) // 2
PH = 4663440                                      # 상자 높이(번호 띠 아래부터 아래 선 위까지)
C2 = 'Ⅱ. 사업수행 결과'
F1 = ITEMS[0][0]
# --- 1-1 작성 예시 ①: 글과 표
s = page(C2, F1, '수자원 분야 사례 조사', '1-1')
panel(s, L, TOP, W, PH, '조사 대상 문헌의 구성', [
    '수자원 관리 분야의 LLM 활용 사례를 RAG 기반 질의응답, 도메인 특화 LLM, 운영지식 구조화의 세 유형으로 나누어 63편 조사',
    '수자원 분야(댐·수리시설, 홍수, 수문·수자원 일반) 문헌은 36편이며, 댐·수리시설 14편 중 7편이 운영지식 구조화 유형',
    '2025~2026년 게재 문헌이 46편으로 조사 대상의 대부분이 최근 2년의 문헌'], ink=True)
put(s, 'bold14', L + 182880, TOP + 1600200, W - 365760, 290000, '표 1. 조사 대상 문헌의 유형별·대상 분야별 구성 [단위: 편]', size=12, color=NAVY)
tbl(s, [['유형', '합계', '댐·수리시설', '홍수', '수문·수자원 일반', '수자원 외'],
        ['RAG 기반 질의응답', '21', '4', '7', '6', '4'],
        ['도메인 특화 LLM', '18', '3', '1', '6', '8'],
        ['운영지식 구조화(온톨로지·KG)', '24', '7', '2', '0', '15'],
        ['합계', '63', '14', '10', '12', '27']],
    [30, 14, 14, 14, 14, 14], x=L + 182880, y=TOP + 1920240, w=W - 365760, row_h=480000, size=13)
order.append(s)
# --- 1-1 작성 예시 ②: 표 중심
s = page(C2, F1, '수자원 분야 사례 조사', '1-1')
panel(s, L, TOP, W, PH, '유형 간 비교', [
    '세 유형은 분야 지식을 두는 곳(문서 저장소, 모델의 가중치, 온톨로지·KG)에서 구분',
    'RAG 기반 질의응답 21편 중 7편이 KG를 근거 저장소로 함께 사용하여, 유형을 결합한 구성이 확인'], ink=True)
put(s, 'bold14', L + 182880, TOP + 1234440, W - 365760, 290000, '표 2. 세 유형의 비교', size=12, color=NAVY)
tbl(s, [['항목', 'RAG 기반 질의응답', '도메인 특화 LLM', '운영지식 구조화'],
        ['지식을 두는 곳', '문서 저장소(벡터·희소 색인)', '모델의 가중치', '온톨로지와 KG의 개체·관계'],
        ['지식의 반영 방법', '질의 시점에 검색하여 프롬프트에 포함', '추가 사전학습, 미세조정', '자료에서 개체·관계를 추출하여 구축'],
        ['자료의 갱신', '저장소의 문서를 교체', '모델을 다시 학습', 'KG의 개체·관계를 추가·수정'],
        ['응답의 근거 제시', '검색한 문서나 KG 항목을 근거로 제시 가능', '가중치에 학습된 지식은 출처 제시가 어려움', '개체·관계와 출처 속성으로 근거 추적 가능'],
        ['확인된 한계', '표·그림이 든 문서의 처리', '분야 미세조정에 따른 일반 능력 하락 보고 2편', 'KG 자체의 완전성 평가 부재, 시계열 자료 통합']],
    [16, 28, 28, 28], x=L + 182880, y=TOP + 1554480, w=W - 365760, row_h=480000, size=12)
order.append(s)
# --- 1-1 작성 예시 ③: 글과 그림
s = page(C2, F1, '수자원 분야 사례 조사', '1-1')
panel(s, L, TOP, HW, PH, '댐 운영 의사결정 지원에 대한 시사점', [
    '근거 제시: 지식을 가중치에만 두는 구성보다 검색 근거나 KG 항목을 응답에 연결하는 구성이 적합',
    '자료 구분: 규정·매뉴얼 등 문서는 검색으로, 수위·방류량 등 수치 자료는 조회 도구나 DB 연결로 구분',
    '운영지식 구조화: 댐 운영(방류 승인, 운영 기준, 수문 상태)을 대상으로 한 온톨로지는 별도 설계 필요',
    '운용 환경: 내부 자료를 다루므로 공개 모델의 내부 구동을 전제로 구성 검토',
    '적용 범위: LLM은 근거 자료의 검색과 정리를 맡고 최종 판단은 운영자가 수행'], ink=True)
panel(s, L + HW + 182880, TOP, HW, PH, '유형을 결합한 구성 사례', ['그림과 함께 요지를 1~2줄로 작성'])
rect(s, L + HW + 365760, TOP + 1005840, HW - 365760, 3108960, 'F7F9FC', line='B6BCC6')
put(s, 'sub', L + HW + 365760, TOP + 2400300, HW - 365760, 320040, '(그림 자리)', align=PP_ALIGN.CENTER)
put(s, 'sub', L + HW + 365760, TOP + 4160520, HW - 365760, 290000, '그림 1. 그림 제목 / 자료: 저자(연도)', size=11, align=PP_ALIGN.CENTER)
order.append(s)
# --- 나머지 항목: 번호 띠와 빈 상자만 둔다
for field, owner, subs in ITEMS:
    for sub in subs:
        num, name = sub.split(' ', 1)
        if num == '1-1':
            continue
        s = page(C2, field, name, num)
        put(s, 'sub', L + W - 2011680, BAR_Y + 73152, 1920240, 265176, '담당: ' + owner, size=11, align=PP_ALIGN.RIGHT)
        panel(s, L, TOP, HW, PH)
        panel(s, L + HW + 182880, TOP, HW, PH)
        order.append(s)

# ------------------------------------------------------------------ Ⅲ 향후 추진계획, 맺음
order.append(divider('Ⅲ', '향후 추진계획', '향후 연구개발 방향과 추진 계획(안)'))
s = page('Ⅲ. 향후 추진계획', '향후 추진계획', '연구개발 추진 방향 및 로드맵(안)')
put(s, 'sub', L + W - 2011680, BAR_Y + 73152, 1920240, 265176, '담당: 책임연구원', size=11, align=PP_ALIGN.RIGHT)
for k in range(3):
    panel(s, L, TOP + k * 1584960, W, 1493520)
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
