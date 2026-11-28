#!/usr/bin/env python3
"""최종보고회 발표자료(pptx): 템플릿의 틀에 과업 1·2의 수행 내용과 적용성 검토(시연)를 채운다.
(원래 설명) 최종보고회 발표자료 템플릿(pptx). 11/26 한강수력본부 발표자료의 디자인(글꼴, 색, 머리글 배치)을 그대로 쓰고,
구성은 표지 → 목차 → Ⅰ 과업개요 → Ⅱ 사업수행 결과(과업 세부 항목 12개) → Ⅲ 향후 추진계획 → 맺음으로 잡는다.
새 슬라이드는 기준 발표자료의 도형을 복사해 만들므로 서식이 같다.
사용: python3 -I dam_pilot_data/scripts/build_final_deck.py <기준 발표자료.pptx> <출력.pptx>
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
            _mid(put(s, 'bold14', L, BAR_Y, 960120, BAR_H, num, size=15, color=GOLD, align=PP_ALIGN.CENTER))
        _mid(put(s, 'bold14', L + (1051560 if num else 182880), BAR_Y, W - 1234440, BAR_H, sub, size=15, color=NAVY))
    put(s, 'num', 11155680, 6446520, 548640, 274320, '0')
    return s


FRAME, INNER = 'A9BEDB', 'F6F9FD'


def panel(s, x, y, w, h, head=None, checks=None, size=12):
    """참고 발표자료의 상자: 바깥 틀 + 머리 칸(꼬리표와 소제목) + 안쪽 상자 + 체크 줄. 비우면 'ㅇ'만 둔다.
    체크 줄 아래의 시작 높이를 돌려준다."""
    rect(s, x, y, w, h, FRAME, round_=True)
    rect(s, x + 54864, y + 64008, w - 109728, 384048, 'DCE9F7')
    rect(s, x + 146304, y, 301752, 448056, NAVY, prst='flowChartOffpageConnector')
    _mid(put(s, 'bold14', x + 521208, y + 64008, w - 640080, 384048, head or 'ㅇ', size=14, color=NAVY))
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
    lines = max(1, math.ceil(wid / ((w - 457200) * 0.80)))
    h = 320040 + (lines - 1) * 219456
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
TOC = [('Ⅰ.', '과업개요', '목적 및 배경, 과업범위, 추진 경과, 수행조직'), ('Ⅱ.', '과업 수행 내용', '과업 4개 분야, 세부 항목 12개의 수행 내용'),
       ('Ⅲ.', '적용성 검토', '시범 구성과 현장 시연'), ('Ⅳ.', '연구개발 추진 방향', '후속 연구개발 방향과 로드맵(안)')]
for k, (ro, nm, ds) in enumerate(TOC):
    y = 1005840 + k * 1280160
    put(s, 'bold14', 4480560, y, 1005840, 548640, ro, size=30, color=BLUE)
    put(s, 'bold14', 5486400, y + 54864, 6000000, 457200, nm, size=24, color=NAVY)
    put(s, 'sub', 5486400, y + 548640, 6000000, 301752, ds, size=14)
    rect(s, 4480560, y + 969264, 7040880, 9144, 'B6BCC6')
order.append(s)

MEMO = {}                                            # 슬라이드 순번(0부터) -> 메모 글
# ================================================================== Ⅰ 과업개요
order.append(divider('Ⅰ', '과업개요', '목적 및 배경, 과업범위, 추진 경과, 수행조직'))
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
SC = [('과업 목표', ['댐 및 수력발전 운영을 위한 생성형 AI 기술 도입 방안의 연구개발 기획 방향 마련']),
      ('기술 역무', ['■ 국내외 기술 트렌드 조사', '수자원 분야 사례 조사, 국내 운영 여건 조사, 적용 기술요소 및 모델 제안',
                 '■ LLM 활용 데이터 파이프라인 조사', '수집 경로 조사, 온톨로지·메타데이터 설계방안 조사, RAG-LLM 통합 파이프라인(안) 제시',
                 '■ sLLM 후보군 평가 방향', '후보 모델 조사, 모델 구조 및 특성 검토, 후보군 적용방안 제시',
                 '■ 도메인 특화 성능 향상 전략', 'RAG 기반 적용방안 조사, 경량 미세조정 방식 검토, 성능 향상 전략 제시']),
      ('기타 역무', ['용역 공정관리 및 월간 진도보고, 각종 회의 및 보고서, 기술 및 학술자문'])]
g = tbl(s, [[a, '\n'.join(b)] for a, b in SC], [16, 84], y=TOP + 54864, row_h=700000, size=14, head_fill='FFFFFF')
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
s = page(C1, '3. 추진 경과')
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
                    (XB, '인공지능 분야 (과업 3·4)', [['공동 책임연구원', '김장호', '인공지능 박사', 'sLLM 후보군 평가,\n모델 구조·특성 검토'], ['연구보조원', '황솔희', '인공지능 학사', 'sLLM 후보 모델 조사·비교 지원']])):
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

# ================================================================== Ⅱ 과업 수행 내용
order.append(divider('Ⅱ', '과업 수행 내용', '과업 4개 분야, 세부 항목 12개의 수행 내용'))
ITEMS = [('1. 국내외 기술 트렌드 조사', ['1-1 수자원 분야 사례 조사', '1-2 국내 운영 여건 조사', '1-3 적용 기술요소 및 모델 제안']),
         ('2. LLM 활용 데이터 파이프라인 조사', ['2-1 수집 경로 조사', '2-2 온톨로지·메타데이터 설계방안 조사', '2-3 RAG-LLM 통합 파이프라인(안) 제시']),
         ('3. sLLM 후보군 평가 방향', ['3-1 후보 모델 조사', '3-2 모델 구조 및 특성 검토', '3-3 후보군 적용방안 제시']),
         ('4. 도메인 특화 성능 향상 전략', ['4-1 RAG 기반 적용방안 조사', '4-2 경량 미세조정 방식 검토', '4-3 성능 향상 전략 제시'])]
C2 = 'Ⅱ. 과업 수행 내용'
PY, PH = TOP - 45720, 4754880
HW = (W - 182880) // 2
XR = L + HW + 182880
HEADC = 'C9D9EE'
FIGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'project_khnp', 'final_report', 'figures')
KFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'project_khnp')
_tn, _fn = [0], [0]


def tcap(s, x, y, w, text):
    _tn[0] += 1
    put(s, 'bold14', x, y, w, 283464, '표 %d. %s' % (_tn[0], text), size=12, color=NAVY, align=PP_ALIGN.CENTER)


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from final_report_drawings import DRAWN                      # 최종보고서의 직접 그린 그림(도형 목록)을 슬라이드 도형으로 다시 그린다
from pptx.enum.shapes import MSO_CONNECTOR
LINE_C = '5B6B82'


def arrow(s, x1, y1, x2, y2, width=1.5):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Emu(int(x1)), Emu(int(y1)), Emu(int(x2)), Emu(int(y2)))
    c.line.color.rgb = RGBColor.from_string(LINE_C); c.line.width = Pt(width)
    ln = c.line._get_or_add_ln()
    ln.append(ln.makeelement(NS + 'tailEnd', {'type': 'triangle', 'w': 'med', 'len': 'med'}))
    return c


def draw(s, key, x, y, w, h):
    """도형 목록(DRAWN[key])을 상자 (x, y, w, h)에 비율대로 맞춰 그린다. 글자 크기는 축척에 맞춘다."""
    sh, DW, DH = DRAWN[key]
    k = min(w / DW, h / DH)
    pt = max(9, min(15, round(10 * k / 127 * 2) / 2))
    ox, oy = x + (w - DW * k) / 2, y + (h - DH * k) / 2
    for it in sh:
        if it[0] == 'arrow':
            arrow(s, ox + it[1] * k, oy + it[2] * k, ox + it[3] * k, oy + it[4] * k)
            continue
        X, Y, Wd, Ht = int(ox + it[1] * k), int(oy + it[2] * k), int(it[3] * k), int(it[4] * k)
        lines = it[5]
        if it[0] == 'box':
            r = rect(s, X, Y, Wd, Ht, it[6].lstrip('#'), line=LINE_C); r.line.width = Pt(0.75)
        if lines:
            t = _mid(put(s, 'body', X, Y, Wd, Ht, '\n'.join(lines), size=pt, color=INK, align=PP_ALIGN.CENTER))
            tf = t.text_frame; tf.margin_left = tf.margin_right = Emu(18288); tf.word_wrap = True
            ps = tf.paragraphs
            if it[0] == 'box' and len(ps) > 1:
                for r_ in ps[0].runs: r_.font.bold = True
                for p_ in ps[1:]:
                    for r_ in p_.runs: r_.font.size = Pt(max(9, pt - 1))
            elif it[0] == 'text':
                for p_ in ps:
                    for r_ in p_.runs: r_.font.bold = True; r_.font.color.rgb = RGBColor.from_string(NAVY)
                if it[3] <= 10000:                       # 판 이름: 왼쪽 위에 붙인다
                    tf.vertical_anchor = MSO_ANCHOR.TOP; tf.margin_top = Emu(27432)
                    for p_ in ps: p_.alignment = PP_ALIGN.LEFT
    return pt


def fig(s, path, x, y, w, h, caption, src=None):
    """상자(x, y, w, h) 안에 그림을 비율대로 가운데에 놓고 아래에 그림 제목과 자료 줄을 둔다. path가 DRAWN의 이름이면 도형으로 그린다."""
    ch = 283464 + (256032 if src else 0)
    bh = h - ch - 45720
    if path in DRAWN:
        print('  도형 그림 %-14s 글자 %.1fpt' % (path, draw(s, path, x, y, w, bh)))
    else:
        from PIL import Image
        iw, ih = Image.open(path).size
        pw = w; ph = int(pw * ih / iw)
        if ph > bh: ph = bh; pw = int(ph * iw / ih)
        pic = s.shapes.add_picture(path, Emu(x + (w - pw) // 2), Emu(y + (bh - ph) // 2), Emu(pw), Emu(ph))
        pic.line.color.rgb = RGBColor.from_string('B6BCC6'); pic.line.width = Pt(0.75)
    _fn[0] += 1
    put(s, 'bold14', x, y + bh + 45720, w, 283464, '그림 %d. %s' % (_fn[0], caption), size=12, color=NAVY, align=PP_ALIGN.CENTER)
    if src:
        put(s, 'sub', x, y + bh + 45720 + 265176, w, 256032, '자료: ' + src, size=11, align=PP_ALIGN.CENTER)


def full(field, num, name, head, checks, caption, rows, widths, size=12, src=None, csize=13, max_rh=640080):
    """상자 하나: 소제목, 체크 줄, 표 제목, 표(, 자료 줄)."""
    s = page(C2, field, name, num)
    yy = panel(s, L, PY, W, PH, head, checks, size=csize)
    tcap(s, L + 100584, yy + 9144, W - 201168, caption)
    ty = yy + 301752
    bottom = PY + PH - 91440 - (265176 if src else 0)
    tbl(s, rows, widths, x=L + 100584, y=ty, w=W - 201168, row_h=min((bottom - ty) // len(rows), max_rh), size=size, head_fill=HEADC, tight=True)
    if src:
        put(s, 'sub', L + 100584, PY + PH - 338328, W - 201168, 256032, '자료: ' + src, size=11)
    order.append(s)
    return s


def split_fig(field, num, name, lhead, checks, rhead, path, caption, src=None, rows=None, widths=None, tcaption=None, size=12, csize=13, lw=0.5, label=None):
    """왼쪽 상자: 체크 줄(과 표), 오른쪽 상자: 그림. lw는 왼쪽 상자의 폭 비율."""
    s = page(label or C2, field, name, num)
    LW = int((W - 182880) * lw); RX = L + LW + 182880; RW = L + W - RX
    yy = panel(s, L, PY, LW, PH, lhead, checks, size=csize)
    if rows:
        tcap(s, L + 100584, yy + 9144, LW - 201168, tcaption)
        ty = yy + 301752
        tbl(s, rows, widths, x=L + 100584, y=ty, w=LW - 201168, row_h=min((PY + PH - 91440 - ty) // len(rows), 640080), size=size, head_fill=HEADC, tight=True)
    panel(s, RX, PY, RW, PH, rhead, [])
    fig(s, path, RX + 137160, PY + 594360, RW - 274320, PH - 685800, caption, src)
    order.append(s)
    return s


def split_chk(field, num, name, lhead, lchecks, rhead, rchecks, size=13):
    s = page(C2, field, name, num)
    panel(s, L, PY, HW, PH, lhead, lchecks, size=size)
    panel(s, XR, PY, HW, PH, rhead, rchecks, size=size)
    order.append(s)
    return s


def stack_fig(field, num, name, head, checks, path, caption, src=None, csize=13, label=None):
    """상자 하나: 체크 줄 아래에 그림을 상자 폭으로 둔다(가로로 긴 그림)."""
    s = page(label or C2, field, name, num)
    yy = panel(s, L, PY, W, PH, head, checks, size=csize)
    fig(s, path, L + 228600, yy + 45720, W - 457200, PY + PH - 91440 - yy - 45720, caption, src)
    order.append(s)
    return s


def mixed(field, num, name, head, checks, tcaption, rows, widths, path, caption, lw=0.42, size=12, csize=13, label=None, src=None):
    """상자 하나: 체크 줄 아래 왼쪽에 표, 오른쪽에 그림."""
    s = page(label or C2, field, name, num)
    yy = panel(s, L, PY, W, PH, head, checks, size=csize)
    TW1 = int((W - 201168) * lw)
    tcap(s, L + 100584, yy + 9144, TW1, tcaption)
    ty = yy + 301752
    tbl(s, rows, widths, x=L + 100584, y=ty, w=TW1, row_h=min((PY + PH - 91440 - ty) // len(rows), 640080), size=size, head_fill=HEADC, tight=True)
    fx = L + 100584 + TW1 + 137160
    fig(s, path, fx, yy + 9144, L + W - 100584 - fx, PY + PH - 91440 - yy - 9144, caption, src)
    order.append(s)
    return s


def quad(field, num, name, cells, size=13):
    """상자 네 개(2×2): cells = [(소제목, [체크 줄...]), ...]"""
    s = page(C2, field, name, num)
    QH = (PH - 137160) // 2
    for k_, (hd, chk) in enumerate(cells):
        panel(s, L if k_ % 2 == 0 else XR, PY + (k_ // 2) * (QH + 137160), HW, QH, hd, chk, size=size)
    order.append(s)
    return s


F1, F2 = ITEMS[0][0], ITEMS[1][0]
# ------------------------------------------------------------------ 1-1 수자원 분야 사례 조사
full(F1, '1-1', '수자원 분야 사례 조사', '조사 범위와 세 유형의 특성', [
    '수자원 분야에 직접 적용한 국내외 사례, 국내 타 분야 사례, 이들이 바탕으로 삼은 일반 방법을 RAG 기반 질의응답, 도메인 특화 LLM, 운영지식 구조화의 세 유형으로 조사',
    '개정되는 지식을 저장소(RAG, KG)에 두면 자료 교체로 갱신할 수 있고, 가중치에 학습된 지식은 다시 학습이 필요'],
    '세 유형의 특성', [
    ['항목', 'RAG 기반 질의응답', '도메인 특화 LLM', '운영지식 구조화'],
    ['지식을 두는 곳', '문서 저장소(의미 검색과 단어 검색을 위한 색인)', '모델의 가중치', '온톨로지와 KG의 개체·관계'],
    ['지식의 반영 방법', '질의 시점에 검색하여 프롬프트에 포함', '추가 사전학습, 미세조정', '자료에서 개체·관계를 추출하여 구축'],
    ['자료의 갱신', '저장소의 문서를 교체', '모델을 다시 학습', 'KG의 개체·관계를 추가·수정'],
    ['응답의 근거 제시', '검색한 문서나 KG 항목을 근거로 제시 가능', '가중치에 학습된 지식은 출처 제시가 어려움', '개체·관계와 출처 속성으로 근거 추적 가능'],
    ['강점', '규정 개정의 즉시 반영, 근거 제시', '분야 용어와 정해진 과업의 성능', '자료 사이의 관계 파악, 근거 추적']], [16, 30, 26, 28])
split_fig(F1, '1-1', '수자원 분야 사례 조사', '주요 사례의 기술 원리', [
    '세 사례 모두 생성 모델을 미세조정하지 않고, 검색한 근거를 입력에 결합하여 응답'],
    'KG와 문서 검색의 경로를 나눈 사례', os.path.join(FIGS, 'rag_fig2.png'), '수리 지식 QA 라우팅 시스템의 전체 구조', 'Han 외(2026)',
    rows=[['사례', '풀려는 문제', '기술 원리'],
          ['KGL 수리시설 점검 QA', '위험 유형·발생 부위가 빠진 점검 질의', 'KG에서 얻은 명확화 경로로 되물어 질의를 단계적으로 명확화'],
          ['수리 지식 QA 라우팅', '단일 출처 질의응답의 답변 범위 불완전', '질의 의도에 따라 KG, 문서 RAG, LLM 단독의 세 경로 중 하나로 분기'],
          ['WaterCopilot', '흩어진 정책 문서와 실시간 수문 자료', '문서 검색과 수문 자료 API 호출을 결합하고 출처와 함께 응답']],
    widths=[24, 34, 42], tcaption='RAG 기반 질의응답 주요 사례')
full(F1, '1-1', '수자원 분야 사례 조사', '댐 운영 의사결정 지원에 적합한 구성', [
    '검색 근거에 기반한 응답을 기본으로 하고 운영지식 KG와 수문 자료 조회를 결합한 구성이 적합',
    '근거를 찾지 못한 질의에는 답하지 않고, 근거를 제시하여 최종 판단은 운영자가 수행하는 구성'],
    '댐 운영 의사결정 지원에 적합한 구성', [
    ['구성요소', '적용 방향', '근거 사례'],
    ['응답 구조', '검색 근거에 기반한 응답, 근거가 없으면 무응답', '수리 지식 QA 라우팅, WaterRAG'],
    ['문서 자료', '운영 규정·매뉴얼은 문서 저장소에 두고 원문을 조회, 표가 든 문서의 전처리', 'WaterCopilot'],
    ['운영지식', '댐 운영을 대상으로 한 온톨로지와 KG, 온톨로지 제약과 전문가 검토', 'DDKG'],
    ['수문 자료', '측정자료 저장소에 두고 조회 도구로 연결', 'OntoDSMS, WaterCopilot'],
    ['생성 모델', '공개 가중치 모델의 내부 구동, 경량 미세조정은 보완 수단', 'HydroLLM, 하천사방 기술기준 QA'],
    ['운영자 역할', '근거 제시와 운영자의 최종 판단', 'FKG-RAG']], [16, 54, 30])
# ------------------------------------------------------------------ 1-2 국내 운영 여건 조사
quad(F1, '1-2', '국내 운영 여건 조사', [
    ('현장방문 조사: 업무 절차', [
        '발전 계획을 미리 수립하여 제출하고, 실제 발전은 급전 지시와 관계기관의 요청, 수위 여건에 따라 조정',
        '한강수계의 발전용 댐은 상류와 하류가 이어져 있어 한 댐의 방류가 하류 댐의 수위에 영향']),
    ('현장방문 조사: 자료 활용 방식', [
        '수문 자료와 발전 운영 자료는 통합 운영 시스템(WEOS)에서 관리하고 조회',
        '판단의 경위는 운영 자료에 함께 남지 않아 운영 수치만으로는 판단 과정을 확인하기 어려움']),
    ('현장방문 조사: 의사결정 구조', [
        '규정에 정한 기준과 관계기관 협의에 따른 실제 운영이 다른 경우가 있고, 택할 수 있는 운영 방안이 여럿임',
        '판단을 대신하는 기능보다 택할 수 있는 방안과 유의사항을 제시하는 기능이 필요하다는 의견']),
    ('현장방문 조사: 시스템 운영 환경', [
        '업무 시스템은 외부망과 분리된 폐쇄망에서 운영',
        '통합 운영 시스템은 댐 운영 모의 모델(물리 모델)을 갖추고 있으며 LLM 기능을 더하는 방안이 준비되고 있음'])])
full(F1, '1-2', '국내 운영 여건 조사', '기술 적용 시 고려사항', [
    '1단계는 의사결정의 대체가 아닌 자료의 정리·문서화 지원으로 범위를 설정',
    '답할 수 있는 범위를 정하고 그 범위 안에서 근거와 함께 정확하게 응답하는 구성이 필요'],
    '현장방문 조사 결과와 기술 적용 시 고려사항', [
    ['구분', '조사에서 확인한 사항', '기술 적용 시 고려사항'],
    ['업무 절차', '발전 계획과 실제 발전이 외부 지시와 요청에 따라 달라지며, 통합 운영으로 전환 중임', '운영 절차의 변경을 반영할 수 있는 갱신 구조'],
    ['자료 활용 방식', '운영 수치는 시스템에서 관리되나 판단의 경위는 함께 남지 않음', '판단 근거의 축적, 규정과 운영 사례의 병행 제시'],
    ['의사결정 구조', '규정과 실제 운영이 다를 수 있고 택할 수 있는 방안이 여럿임', '여러 방안의 제시, 운영자 판단을 전제로 한 응답'],
    ['시스템 운영 환경', '폐쇄망에서 운영되며 물리 모델과 LLM 기능 추가 구상이 있음', '기관 내부 설치, 기존 물리 모델과 문서 검색 기능과의 결합'],
    ['사용자', '긴 지시문 작성 없이 답을 얻기를 원함', '짧은 질의와 자동 근거 구성']], [16, 46, 38])
# ------------------------------------------------------------------ 1-3 적용 기술요소 및 모델 제안
full(F1, '1-3', '적용 기술요소 및 모델 제안', '사례 조사와 운영 여건 조사에서 도출한 핵심 기술요소', [
    '사례 조사와 국내 운영 여건 조사의 결과에서 지식기반 구성, 수문자료 연계, 운영자 지원체계의 세 기술요소를 도출'],
    '핵심 기술요소의 필요성, 원리, 적용 방향', [
    ['기술요소', '필요성', '기술의 원리', '적용 방향'],
    ['지식기반 구성', '운영 기준, 시설, 수문 상태, 과거의 승인과 운영 이력 사이의 관계를 따라 근거를 찾을 수 있어야 함', '온톨로지로 개념과 관계를 정의하고, KG에 실제 자료를 개체와 관계로 구성', '댐을 중심으로 시설, 상태, 운영, 승인, 운영기준, 근거자료를 연결한 운영지식 KG'],
    ['수문자료 연계', '운영 판단의 근거인 수위, 유입량, 방류량은 제공 기관의 시스템에서 주기적으로 갱신', '수치 시계열은 원래의 저장소에 두고 KG에는 식별 키만 두어 필요한 구간의 값만 조회', '수문·기상 수치는 측정자료 저장소에 두고 KG의 식별 키로 연결'],
    ['운영자 지원체계', '응답과 함께 근거를 확인할 수 있어야 하며 최종 판단은 운영자가 수행', '질의와 관련된 근거를 먼저 찾아 생성 모델의 입력에 결합(RAG)', '질의 해석, 근거 조회, 근거 묶음 구성, sLLM의 근거 기반 응답']], [14, 30, 29, 27], max_rh=960120)
split_fig(F1, '1-3', '적용 기술요소 및 모델 제안', 'RAG-sLLM 아키텍처(안)', [
    '지식기반 계층: KG에 개체 간 관계와 근거 출처를 구조화하고, 수치 시계열과 규정 원문은 외부 저장소에 두어 식별 키로 연계',
    '검색 계층: 질의의 의도와 대상을 파악하고 근거를 검색하여 출처가 붙은 근거 묶음으로 구성',
    '응답 계층: 근거 묶음을 입력으로 sLLM이 근거 중심으로 응답',
    '변동이 잦은 문서는 문서 검색 경로로 받고, 계산과 예측은 기존 물리 모델을 호출하는 구성을 검토'],
    '계층의 구성', 's13_fig_arch', 'RAG-sLLM 아키텍처(안) 구성 계층', lw=0.40)
# ------------------------------------------------------------------ 2-1 수집 경로 조사
full(F2, '2-1', '수집 경로 조사', '자료별 적정 수집 경로(안)', [
    '수문, 기상, 방류 승인 기록, 운영 규정, 전력 단가 자료의 수집 경로를 제공 방식, 인증, 자료 단위, 제공 기간, 식별 체계 기준으로 조사',
    '공식성, 이력 제공, 식별 키, 접근 조건의 네 기준으로 자료별 적정 수집 경로(안)를 제시'],
    '자료별 적정 수집 경로(안)', [
    ['자료', '적정 수집 경로(안)', '제공 방식', '수집 단위'],
    ['수문(공개 자료가 제공되는 댐)', '공개 수문 운영 정보 OpenAPI', 'OpenAPI', '10분·시간·일'],
    ['수문(한수원 관리 댐)', '통합 운영 시스템(WEOS)의 수문 자료', '내부 시스템 조회', '시스템의 저장 주기'],
    ['댐 제원·코드', '공개 댐코드 조회, 수문 제원 현황 OpenAPI', 'OpenAPI', '수시'],
    ['기상', '공개 지상 기상 시간자료 조회 서비스', 'OpenAPI', '시간'],
    ['방류 승인', '공개 방류 승인 기록 파일', '파일(CSV)', '승인 건별'],
    ['운영 규정', '공개 법령 정보(행정규칙), 첨부파일', 'OpenAPI, 파일', '개정 시'],
    ['전력 단가', '통합 운영 시스템(WEOS)의 발전 운영 자료', '내부 시스템 조회', '시간']], [26, 40, 18, 16])
quad(F2, '2-1', '수집 경로 조사', [
    ('관측소·시설의 식별 체계', [
        '기관마다 관측소·시설의 코드 체계가 달라 같은 시설을 가리키는 코드의 대응을 정리할 필요',
        '수집 단계에서 시설 단위의 대응표를 작성하고 대응의 근거를 함께 기록']),
    ('자료별 데이터 형태', [
        '수문·기상 관측값은 정형 자료로, 규정은 문서 자료로 제공되어 다루는 방식을 구분',
        '시각 표기, 문자열 수치, 빈 값의 표기가 자료마다 달라 형식을 통일하되 원본 값은 보관']),
    ('공개 자료에서 확인되지 않는 항목', [
        '방류 승인 내역은 공개 자료로 확인할 수 있으나 승인 판단의 근거를 담은 자료는 확보하기 어려움',
        '승인 내역에 수문 자료와 운영 규정을 연결하여 판단 근거를 재구성하고, 판단의 경위는 운영 과정에서 기록하여 축적하는 방향을 검토']),
    ('한수원 내부 자료', [
        '과거 수문 이력과 발전 운영 자료는 통합 운영 시스템의 자료로 보완',
        '내부 자료의 수집과 보관은 폐쇄망 안에서 수행하고, 공개 자료는 반입 승인 절차를 거쳐 들이는 구성'])])
# ------------------------------------------------------------------ 2-2 온톨로지·메타데이터 설계방안 조사
stack_fig(F2, '2-2', '온톨로지·메타데이터 설계방안 조사', '온톨로지 설계 방법 조사', [
    '단계적 설계 방법과 LLM을 쓴 반자동 방법을 조사: 초기 판을 만든 뒤 전문가 검토로 반복하여 보완하는 절차가 공통',
    '댐 분야 선행 온톨로지는 구조, 계측, 결함, 안전평가를 대상으로 하여, 댐 운영을 대상으로 한 Class는 새로 정의'],
    's22_fig_noy', '온톨로지의 단계적 설계 절차(7단계)', 'Noy·McGuinness(2001)의 절차를 도식으로 재구성')
stack_fig(F2, '2-2', '온톨로지·메타데이터 설계방안 조사', '메타데이터 설계요소와 자료 유형별 전처리 체계(안)', [
    '메타데이터는 식별 키, 출처 정보, 시점 정보, 단위·표기 형식, 자료 유형의 다섯 설계요소로 구성',
    '자료를 구조화 자료, 수치 시계열, 문서 자료로 구분하여 처리 경로와 보관 위치를 지정',
    '표기 형식을 통일하고 출처·시점 정보를 유지하며, 원본은 변경하지 않고 정리 내용을 기록'],
    's22_fig_prep', '자료 유형별 전처리 경로(안)')
mixed(F2, '2-2', '온톨로지·메타데이터 설계방안 조사', '댐 운영 온톨로지 설계(안)', [
    '댐 Class를 중심으로 상태, 운영행위, 방류 승인, 운영기준을 연결하고 각 개체는 근거자료에 연결하여 출처를 추적',
    '질문·범위 정의, 온톨로지 정의, KG 구축, 점검, 보완의 절차를 전문가 검토와 함께 반복'],
    '댐 운영 온톨로지(안)의 Class', [['Class', '나타내는 대상'],
          ['댐', '댐·보 등 운영 대상 시설'],
          ['수문·기상 상태', '댐별 수문·기상 관측 항목'],
          ['운영행위', '방류 등 운영행위'],
          ['방류 승인', '방류 승인 기록'],
          ['운영기준', '홍수기 제한수위 등 운영 기준값'],
          ['근거자료', '값이 적힌 자료와 그 위치']], [36, 64],
    's22_fig_onto', '댐 운영 온톨로지(안)의 Class와 관계', lw=0.36)
# ------------------------------------------------------------------ 2-3 RAG-LLM 통합 파이프라인(안) 제시
stack_fig(F2, '2-3', 'RAG-LLM 통합 파이프라인(안) 제시', '지식기반 구축(①~③)과 질의응답(④~⑦)으로 구성한 통합 파이프라인(안)', [
    '지식기반 구축은 자료의 수집, 전처리, 지식기반 구성의 순서로 KG와 외부 저장소를 구성',
    '질의응답은 질의 해석, 근거 조회, 근거 정리, 응답의 순서로 근거 묶음을 구성하여 응답'],
    's23_pipeline', 'RAG-LLM 통합 파이프라인(안)')
full(F2, '2-3', 'RAG-LLM 통합 파이프라인(안) 제시', '단계별 입력, 처리, 산출', [
    '질의 해석(④)과 응답(⑦)은 sLLM이 수행하고, 나머지 단계는 정해진 규칙과 절차에 따라 처리'],
    '통합 파이프라인(안)의 단계별 입력·처리·산출', [
    ['단계', '입력', '처리', '산출', '처리 주체'],
    ['① 수집', '수집 대상별 수집 경로', '구조화 자료와 문서 자료를 수집', '원본 자료', '규칙'],
    ['② 전처리', '원본 자료', '자료 유형별로 표기 형식을 통일하고 값은 원본 유지', '정리된 자료', '규칙'],
    ['③ 지식기반 구성', '정리된 자료, 온톨로지', 'KG를 구성하고 수치 시계열과 규정 원문은 외부 저장소에 두어 식별 키로 연계', 'KG, 외부 저장소', '규칙'],
    ['④ 질의 해석', '사용자 질의', '의도, 대상 댐, 기간을 추출하고 허용 범위 확인', '의도·대상·기간', 'sLLM'],
    ['⑤ 근거 조회', '의도·대상·기간', '의도별 질의 규칙으로 KG를 조회하고 식별 키로 외부 저장소 조회', '개체·관계, 측정값, 규정 원문', '규칙'],
    ['⑥ 근거 정리', '조회 결과', '의도별 구역으로 근거를 모으고 항목마다 출처 번호 부여', '근거 묶음', '규칙'],
    ['⑦ 응답', '표준 프롬프트 프레임', '근거 묶음 안에서 근거와 판단을 구분하여 응답', '출처 번호가 포함된 응답', 'sLLM']], [15, 18, 39, 18, 10])
mixed(F2, '2-3', 'RAG-LLM 통합 파이프라인(안) 제시', '근거 묶음, 표준 프롬프트 프레임, 근거 사용 원칙(안)', [
    '조회한 근거를 현재 상태, 과거 이력, 운영 기준, 출처·위치의 구역으로 모으고 항목마다 출처 번호를 부여하여 sLLM에 전달'],
    '근거 사용 원칙(안)', [['항목', '내용'],
          ['근거의 사용', '근거 묶음의 내용만 사실로 사용, 사실마다 출처 번호 표기'],
          ['판단의 구분', '비교·해석은 판단임을 밝히고 근거를 표기'],
          ['근거가 없는 경우', '근거에 없는 내용은 자료에 없음으로 응답'],
          ['항목 불일치', '그 이름의 항목이 근거에 없으면 다른 값으로 대체하지 않음']], [30, 70],
    's23_frame_fig', '표준 프롬프트 프레임을 통한 근거 전달', lw=0.40)
# ------------------------------------------------------------------ 과업 3·4: 인공지능학과 작성(항목마다 2장, 빈 상자)
for fi, (field, subs) in enumerate(ITEMS[2:], 2):
    for sub in subs:
        num, name = sub.split(' ', 1)
        for _ in range(2):
            s = page(C2, field, name, num)
            panel(s, L, PY, HW, PH)
            panel(s, XR, PY, HW, PH)
            MEMO[len(order)] = '[인공지능학과 작성] %s %s: 상자 머리(ㅇ)에 소제목, 체크 줄에 요지, 그 아래에 표나 그림을 넣어 작성. 과업 1·2의 쪽(글과 표, 글과 그림)을 참고. 상자 수와 크기는 내용에 맞게 조정하고, 장이 모자라면 슬라이드를 복제' % (num, name)
            order.append(s)

# ================================================================== Ⅲ 적용성 검토(시범 구성과 현장 시연)
order.append(divider('Ⅲ', '적용성 검토', '시범 구성과 현장 시연'))
C3 = 'Ⅲ. 적용성 검토'
mixed('1. 시범 구성', '1.', '공개 자료로 구성한 시범 지식기반과 질의응답', '시범 구성의 범위', [
    '제시한 온톨로지(안)와 통합 파이프라인(안)이 실제 자료에서 동작하는지를 공개 자료로 확인',
    '질문을 해석하고 KG와 저장소에서 근거를 찾아 출처 번호를 붙여 응답하는 흐름을 구성'],
    '시범 구성의 규모', [['구분', '내용'],
        ['자료', '공개 자료 3종(시간 측정값, 방류 승인 기록, 운영 규정)'],
        ['온톨로지', 'Class 6개, 관계 9개'],
        ['지식그래프(KG)', 'Entity 264개, 관계 418개'],
        ['외부 저장소', '측정값 약 87만 행, 규정 원문'],
        ['대상', '댐 4개, 질문 범주 6개'],
        ['생성 모델', '범용 LLM']], [32, 68],
    's23_pipeline', '시범 구성에 적용한 파이프라인(생성 모델은 범용 LLM)', lw=0.40, label=C3)
s = page(C3, '1. 시범 구성', '질문 하나의 처리 과정(예)', '1.')
panel(s, L, PY, W, PH, '질의 해석부터 응답까지의 처리 예', [])
QX, QY, QW = L + 137160, PY + 594360, W - 274320
rect(s, QX, QY, QW, 420624, 'FDF5E2', line='D9B44A', round_=True)
_mid(put(s, 'bold14', QX + 137160, QY, QW - 274320, 420624, '질문   "2020년 8월 충주댐 방류 승인과 운영행위, 그때의 수문 상태를 알려줘."', size=14, color=INK))
STEPS = [('④ 질의 해석', 'LLM', '질문 범주: 과거 상태, 운영행위, 방류 승인  /  대상: 충주댐  /  기간: 2020년 8월'),
         ('⑤ 근거 조회', '규칙', 'KG에서 운영행위 1건과 방류 승인 3건을 조회하고, 운영 시각(2020-08-02 18:00)의 측정값을 저장소에서 조회'),
         ('⑥ 근거 정리', '규칙', '질문 범주별 구역으로 근거를 모으고 항목마다 출처 번호를 부여'),
         ('⑦ 응답', 'LLM', '근거(출처 번호를 붙인 사실)와 판단(어느 근거에서 나온 판단인지 표기)으로 나누어 응답')]
SY = QY + 420624 + 137160; SH = (PY + PH - 137160 - SY - 3 * 109728) // 4
for k_, (nm_, who_, tx_) in enumerate(STEPS):
    y_ = SY + k_ * (SH + 109728)
    rect(s, QX, y_, 2011680, SH, NAVY, round_=True)
    _mid(put(s, 'bold14', QX, y_, 2011680, SH, nm_, size=15, color='FFFFFF', align=PP_ALIGN.CENTER))
    rect(s, QX + 2103120, y_, 1005840, SH, 'DCE9F7' if who_ == '규칙' else 'F9ECEC', line='B6BCC6', round_=True)
    _mid(put(s, 'bold14', QX + 2103120, y_, 1005840, SH, who_, size=13, color=NAVY, align=PP_ALIGN.CENTER))
    rect(s, QX + 3200400, y_, QW - 3200400, SH, 'FFFFFF', line='B6BCC6', round_=True)
    _mid(put(s, 'body', QX + 3337560, y_, QW - 3474720, SH, tx_, size=14, color=INK))
    if k_ < 3:
        arrow(s, QX + 1005840, y_ + SH, QX + 1005840, y_ + SH + 109728)
order.append(s)
s = page(C3, '2. 현장 시연', '시연 질문의 구성', '2.')
yy = panel(s, L, PY, W, PH, '질문 범주마다 대응하는 질문과 두 범주를 이어서 묻는 질문으로 구성', [
    '현장에서 노트북으로 직접 질문을 입력하고, 응답의 출처 번호를 눌러 근거 원문을 확인'], size=13)
tcap(s, L + 100584, yy + 9144, W - 201168, '시연 질문')
rows = [['질문 범주', '확인하는 내용', '시연 질문'],
        ['현재 상태', '대상 댐의 현재 수문·기상 상태', '충주댐 지금 상황 알려줘'],
        ['과거 상태', '과거 시점의 수문·기상 상태', '2020년 8월 2일 18시 충주댐 수위는?'],
        ['운영행위', '과거에 실제로 수행된 운영행위', '2011년 7월 충주댐 방류 조작 기록 알려줘'],
        ['방류 승인', '과거의 방류 승인과 승인 내용', '2020년 8월 충주댐 방류 승인이 어떻게 바뀌었는지 정리해줘'],
        ['운영기준', '현재 적용되는 운영기준과 기준값', '충주댐 홍수기 제한수위는 얼마야?'],
        ['근거', '기준을 확인할 수 있는 공식 근거', '충주댐 제한수위 근거 규정이 뭐야?'],
        ['현재 상태 + 운영기준', '현재 상태와 운영기준을 함께 확인', '충주댐 지금 수위가 홍수기 제한수위보다 높아?'],
        ['운영행위 → 과거 상태', '운영행위를 찾고 그 시점의 상태를 확인', '2011년 7월 충주댐 방류 조작 시점마다 수위와 유입량은?']]
ty = yy + 301752
tbl(s, rows, [22, 34, 44], x=L + 100584, y=ty, w=W - 201168, row_h=(PY + PH - 91440 - ty) // len(rows), size=12, head_fill=HEADC, tight=True)
order.append(s)
s = page(C3, '2. 현장 시연', '시연 화면과 진행 순서', '2.')
LW3 = int(W * 0.36); RX3 = L + LW3 + 182880; RW3 = L + W - RX3
panel(s, L, PY, LW3, PH, '진행 순서', [
    '① 화면의 대상 댐과 물어볼 수 있는 질문 종류를 확인',
    '② 질문 범주별 질문을 차례로 입력하고 응답의 근거와 판단을 확인',
    '③ 응답의 출처 번호를 눌러 측정값, 승인 기록, 규정 원문을 확인',
    '④ 두 범주를 이어서 묻는 질문으로 근거가 함께 구성되는지 확인',
    '⑤ 참석자가 직접 질문을 입력'], size=13)
panel(s, RX3, PY, RW3, PH, '시연 화면', [])
fig(s, os.path.join(KFIG, 'demo_screen.png'), RX3 + 137160, PY + 594360, RW3 - 274320, PH - 685800, '시범 구성의 질의응답 화면')
MEMO[len(order)] = '현장 시연: 노트북으로 직접 시연하는 것을 목표로 함. 접속 방식(연구실 서버 연결 또는 노트북 단독 구동)과 예비용 시연 영상 사용 여부를 정한 뒤 진행 순서를 확정'
order.append(s)

# ================================================================== Ⅳ 연구개발 추진 방향
order.append(divider('Ⅳ', '연구개발 추진 방향', '후속 연구개발 방향과 로드맵(안)'))
s = page('Ⅳ. 연구개발 추진 방향', '연구개발 추진 방향', '후속 연구개발 방향과 로드맵(안)')      # 한 쪽으로 두고 비운다
MEMO[len(order)] = '내용과 구성이 정해지지 않아 비워둠'
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
