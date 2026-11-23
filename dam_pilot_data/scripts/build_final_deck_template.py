#!/usr/bin/env python3
"""최종보고회 발표자료 템플릿(pptx). 11/26 한강수력본부 발표자료의 디자인(글꼴, 색, 머리글 배치)을 그대로 쓰고,
구성은 표지 → 목차 → Ⅰ 과업개요 → Ⅱ 사업수행 결과(과업 세부 항목 12개) → Ⅲ 향후 추진계획 → 맺음으로 잡는다.
새 슬라이드는 기준 발표자료의 도형을 복사해 만들므로 서식이 같다.
사용: python3 -I dam_pilot_data/scripts/build_final_deck_template.py <기준 발표자료.pptx> <출력.pptx>
"""
import copy, sys, os
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


def _clear_white(pic):
    """로고 그림의 흰 바탕을 투명하게 바꾼다(띠의 색 위에 흰 네모가 보이지 않게)."""
    import io
    from PIL import Image
    im = Image.open(io.BytesIO(pic.image.blob)).convert('RGBA')
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            m = min(r, g, b)
            if m >= 250: px[x, y] = (r, g, b, 0)
            elif m >= 215: px[x, y] = (r, g, b, int(a * (250 - m) / 35))     # 가장자리는 서서히
    buf = io.BytesIO(); im.save(buf, 'PNG'); buf.seek(0)
    part, rid = pic.part.get_or_add_image_part(buf)
    pic._element.blipFill.blip.set('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed', rid)


_pics = sorted([sh for sh in _lay.shapes if sh.shape_type == 13], key=lambda sh: sh.left)
print('레이아웃 로고', [(sh.name, sh.left, sh.top, sh.width, sh.height) for sh in _pics])
for _pc in _pics:
    _clear_white(_pc)
if len(_pics) == 2:                                      # 두 로고의 높이를 띠 안에 맞추고 세로 가운데에 둔다
    _k, _u = _pics                                       # 왼쪽: 한국수력원자력, 오른쪽: 국민대학교
    _uh = 521208; _uw = int(_u.width * _uh / _u.height)
    _u.width, _u.height = Emu(_uw), Emu(_uh)
    _u.left, _u.top = Emu(12192000 - 228600 - _uw), Emu((BAND_H - _uh) // 2)
    _kh = 384048; _kw = int(_k.width * _kh / _k.height)
    _k.width, _k.height = Emu(_kw), Emu(_kh)
    _k.left, _k.top = Emu(int(_u.left) - 228600 - _kw), Emu((BAND_H - _kh) // 2)


def page(label, title, sub=None, num=None):
    """label: 장 이름(오른쪽 위 꼬리표), title: 제목 띠, sub: 번호 띠의 이름(없으면 띠를 그리지 않음), num: 번호"""
    s = new(1)
    put(s, 'title', L - 91440, 100584, 6400800, 466344, title, size=24)
    rect(s, 9601200, BAND_H + 36576, 2590800, 301752, NAVY)
    _mid(put(s, 'bold14', 9601200, BAND_H + 36576, 2590800, 301752, label, size=13, color='FFFFFF', align=PP_ALIGN.CENTER))
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
for sh in list(cover.shapes):
    if sh.name == 'Text 7': sh._element.getparent().remove(sh._element)      # 표지의 '(작성 템플릿)' 글은 두지 않는다
order = [cover]
# 목차: 참고 발표자료와 같은 배치(왼쪽 색 면에 '목 차', 오른쪽에 장 목록)
s = new(0)
rect(s, 0, 0, 3767328, 6858000, NAVY)
rect(s, 0, 1143000, 3767328, 27432, '9DBEDD')
put(s, 'end1', 0, 1554480, 3767328, 822960, '목   차')
for k, (ro, nm, ds) in enumerate([('Ⅰ.', '과업개요', '목적 및 배경, 과업범위, 공정률, 수행조직'), ('Ⅱ.', '사업수행 결과', '과업 4개 분야, 세부 항목 12개의 수행 결과'), ('Ⅲ.', '향후 추진계획', '연구개발 추진 방향 및 로드맵(안)')]):
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
    x = 2272283 + (0, 1097280, 3566160)[k]
    rect(s, x, 888044, 384048, 118872, col)
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
        rect(s, X0 + 4 * CW + 18288, y + 45720, CW - 36576, 82296, RED)
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
    tbl(s, rows, widths, x=L + 100584, y=yy + 27432, w=W - 201168, row_h=min(rh, 860000), size=size, head_fill=HEADC, tight=True)
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


def chk2(lhead, lchecks, rhead, rchecks, size=13):
    """1-1 예시: 양쪽 상자에 체크 줄(왼쪽 사례 비교 결과, 오른쪽 댐 운영 적용 방향)."""
    s = page(C2, ITEMS[0][0], '수자원 분야 사례 조사', '1-1')
    panel(s, L, PY, HW, PH, lhead, lchecks, size=size)
    panel(s, XR, PY, HW, PH, rhead, rchecks, size=size)
    order.append(s)


# 1-1은 작성 예시 2장만 둔다(글과 표, 글과 그림). 내용은 최종보고서 1.1절에서 일부만 가져왔다.
# 예시 ①: 상자 하나에 소제목, 체크 줄(요지), 표 제목, 표
EX_C = 'C0392B'


def ex_note(s, text):
    """번호 띠 오른쪽에 작성 예시임을 적는다."""
    put(s, 'bold14', L + W - 6583680, BAR_Y + 54864, 6492240, 283464, text, size=12, color=EX_C, align=PP_ALIGN.RIGHT)


s = page(C2, ITEMS[0][0], '수자원 분야 사례 조사', '1-1')
ex_note(s, '[작성 예시 ①] 주요 내용(체크 줄)과 표의 배치 예시')
yy = panel(s, L, PY, W, PH, 'RAG 기반 질의응답의 구성 방식', [
    '모델을 다시 학습시키지 않고 문서·KG·DB에서 찾은 근거를 프롬프트에 넣어 응답을 생성하는 방식',
    '규정이 개정되면 저장소의 자료만 교체하면 되고 응답에 근거 출처를 붙일 수 있어 댐 운영 질의응답에 직접 대응'], size=13)
put(s, 'bold14', L + 100584, yy + 18288, W - 201168, 283464, '표 1. RAG 기반 질의응답의 구성 방식과 대표 사례', size=12, color=NAVY, align=PP_ALIGN.CENTER)
rows = [['구성 방식', '근거를 찾는 방법', '적합한 자료와 질의', '대표 사례와 결과'],
        ['문서 검색형', '문서 조각의 벡터 검색, 희소 검색·재순위화 결합', '규정, 지침, 매뉴얼, 보고서 등 문서 자료에 대한 질의', 'WaterRAG: 답변 정확성 통과율 64.91% → 80.51%'],
        ['KG 결합형', 'KG 질의와 문서 검색의 병행, 질의별 경로 분기', '시설, 기준, 사건 사이의 관계를 묻는 질의', '수리 지식 QA 라우팅: 종단 정확도 86.4% (LLM 단독 73.5%)'],
        ['정형 자료 조회형', 'LLM이 DB 질의나 자료 API를 호출', '수위, 유량, 강우 등 수치 자료를 묻는 질의', 'WaterCopilot: 문서 검색과 실시간 수문 자료 호출을 결합'],
        ['에이전트형', 'LLM이 여러 도구와 모형을 단계적으로 호출', '수문 모의, 모형 보정 등 여러 단계의 작업', 'AQUAH: 조절되는 유역을 자연 유역과 구분하기 어려운 한계']]
ty = yy + 320040
tbl(s, rows, [15, 27, 27, 31], x=L + 100584, y=ty, w=W - 201168, row_h=(PY + PH - 91440 - 283464 - ty) // len(rows), size=13, head_fill=HEADC, tight=True)
put(s, 'sub', L + 100584, PY + PH - 347472, W - 201168, 256032, '자료: Zhai 외(2026), Han 외(2026), Vickneswaran 외(2026), Yan 외(2025)', size=11)
order.append(s)
# 예시 ②: 왼쪽 상자에 체크 줄(주요 내용)과 표, 오른쪽 상자에 그림과 그림 제목. 상자 안을 아래까지 채운다
s = page(C2, ITEMS[0][0], '수자원 분야 사례 조사', '1-1')
ex_note(s, '[작성 예시 ②] 주요 내용, 표, 그림의 배치 예시 · 내용은 작성 시 교체')
yy = panel(s, L, PY, HW, PH, '댐 운영 의사결정 지원에 적합한 구성', [
    '검색 근거에 기반한 응답을 기본으로 하고, 운영지식 KG와 수문 자료 조회를 결합한 구성이 적합',
    '근거를 찾지 못한 질의에는 답하지 않도록 구성',
    'LLM은 근거 자료의 검색과 정리를 맡고 최종 판단은 운영자가 수행'], size=13)
put(s, 'bold14', L + 100584, yy + 18288, HW - 201168, 283464, '표 2. 자료별 처리 방식', size=12, color=NAVY, align=PP_ALIGN.CENTER)
rows = [['자료', '처리 방식', '근거 사례'],
        ['운영 규정·매뉴얼', '문서 검색으로 근거 조항을 찾아 출처와 함께 제시', 'WaterRAG'],
        ['운영 기준, 시설·상태의 관계', '온톨로지와 KG로 정리하여 조회', 'DDKG'],
        ['수위·방류량 등 수문 자료', '측정자료 저장소에 두고 조회 도구로 연결', 'OntoDSMS, WaterCopilot']]
ty = yy + 320040
tbl(s, rows, [30, 46, 24], x=L + 100584, y=ty, w=HW - 201168, row_h=(PY + PH - 91440 - ty) // len(rows), size=12, head_fill=HEADC, tight=True)
panel(s, XR, PY, HW, PH, '문서 검색과 수문 자료 조회를 결합한 사례', [])
_fig = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'project_khnp', 'fig', 'deck_example_WaterCopilot_Fig1.png')      # 논문 그림을 옮긴 예시
_aw = HW - 320040; _ah = int(_aw * 545 / 1070)
_pic = s.shapes.add_picture(_fig, Emu(XR + 160020), Emu(PY + 620000 + (PH - 1340000 - _ah) // 2), Emu(_aw), Emu(_ah))
_pic.line.color.rgb = RGBColor.from_string('B6BCC6'); _pic.line.width = Pt(0.75)
put(s, 'bold14', XR + 100584, PY + PH - 640080, HW - 201168, 283464, '그림 1. WaterCopilot 에이전트와 플러그인의 구조', size=12, color=NAVY, align=PP_ALIGN.CENTER)
put(s, 'sub', XR + 100584, PY + PH - 356616, HW - 201168, 256032, '자료: Vickneswaran 외(2026)의 Figure 1', size=11, align=PP_ALIGN.CENTER)
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
                MEMO[len(order)] = '[인공지능학과 작성] %s %s: 상자 머리(ㅇ)에 소제목, 체크 줄에 요지, 그 아래에 표나 그림을 넣어 작성. 1-1의 예시 2장(글과 표, 글과 그림)을 참고. 상자 수와 크기는 내용에 맞게 조정하고, 장이 모자라면 슬라이드를 복제' % (num, name)
            order.append(s)
    # 분야가 끝날 때마다 수행 결과와 산출물을 모으는 쪽
    s = page(C2, field, '수행 결과 종합', '%d.' % (fi + 1))            # 세부 항목별이 아니라 분야 전체를 다룬다
    for title, y, h in (('● 주요 수행 결과', TOP - 45720, 2651760), ('● 종합 결론', TOP + 3108960, 1188720)):
        put(s, 'bold14', L, y, 4572000, 283464, title, size=14, color=NAVY)
        rect(s, L + 137160, y + 347472, W - 137160, h if h > 2000000 else h - 347472, INNER, line=FRAME, round_=True)
    if fi >= 2:
        MEMO[len(order)] = '[인공지능학과 작성] %s의 수행 결과 종합: 세부 항목별이 아니라 분야 전체의 주요 수행 결과와 종합 결론을 간단히 작성' % field
    order.append(s)

# ================================================================== Ⅲ 향후 추진계획
order.append(divider('Ⅲ', '향후 추진계획', '연구개발 추진 방향 및 로드맵(안)'))
# 최종보고이므로 과업별 계획이 아니라 연구개발 추진 방향과 로드맵(안)을 둔다(책임연구원 담당, 틀만 제공)
s = page('Ⅲ. 향후 추진계획', '향후 추진계획', '연구개발 추진 방향', '1.')
for y, h in ((TOP - 45720, 762000), (TOP + 1371600, 1357971), (TOP + 3383280, 762000)):
    put(s, 'bold14', L, y, 914400, 283464, '● ㅇ', size=14, color=NAVY)
    rect(s, L + 137160, y + 347472, W - 137160, h, INNER, line=FRAME, round_=True)
order.append(s)
s = page('Ⅲ. 향후 추진계획', '향후 추진계획', '로드맵(안)', '2.')          # 형식을 정하지 않아 비워 둔다
MEMO[len(order)] = '[책임연구원 작성] 로드맵(안): 구성 형식을 정하지 않아 비워 둠. 내용에 맞는 형식(표, 그림 등)으로 작성'
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
    _rel = {re.search(r'Id="([^"]+)"', m).group(1): re.search(r'Target="([^"]+)"', m).group(1) for m in re.findall(r'<Relationship [^>]*/>', zi.read('ppt/_rels/presentation.xml.rels').decode())}
    _ord = [_rel[r].split('/')[-1] for r in re.findall(r'<p:sldId [^>]*r:id="([^"]+)"', zi.read('ppt/presentation.xml').decode())]
    byfile = {_ord[i]: i for i in memos}                      # 슬라이드 파일 이름은 발표 순서와 다르므로 순서 목록에서 찾는다
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
            m = re.match(r'ppt/slides/_rels/(slide[0-9]+[.]xml)[.]rels$', it.filename)
            if m and m.group(1) in byfile:
                k = sorted(memos).index(byfile[m.group(1)]) + 1
                data = data.decode().replace('</Relationships>', '<Relationship Id="rIdCm" Type="%scomments" Target="../comments/comment%d.xml"/></Relationships>' % (REL, k)).encode()
        zo.writestr(it, data)
    zo.writestr('ppt/commentAuthors.xml', HEAD + '<p:cmAuthorLst %s><p:cmAuthor id="1" name="%s" initials="C" lastIdx="%d" clrIdx="0"/></p:cmAuthorLst>' % (PNS, author, len(memos)))
    for k, i in enumerate(sorted(memos), 1):
        zo.writestr('ppt/comments/comment%d.xml' % k, HEAD + '<p:cmLst %s><p:cm authorId="1" dt="2026-11-23T21:00:00.000" idx="%d"><p:pos x="1745" y="663"/><p:text>%s</p:text></p:cm></p:cmLst>' % (PNS, k, escape(memos[i])))
    zo.close(); zi.close(); shutil.move(tmp, path)


add_memos(OUT, MEMO)
print('저장', OUT, '슬라이드', len(prs.slides))
