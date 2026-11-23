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


def page(label, title, sub):
    s = new(1)
    put(s, 'label', L, 292608, 5943600, 274320, label)
    put(s, 'title', L, 603504, 11155680, 548640, title)
    put(s, 'sub', L, 1188720, 11155680, 320040, sub)
    put(s, 'num', 11155680, 6446520, 548640, 274320, '0')
    return s


def divider(roman, name, desc):
    s = new(0)
    bg = S[24]._element.cSld.find('{http://schemas.openxmlformats.org/presentationml/2006/main}bg')      # 맺음 슬라이드와 같은 남색 바탕
    if bg is not None:
        s._element.cSld.insert(0, copy.deepcopy(bg))
    put(s, 'end1', L, 2286000, W, 822960, roman, color='9DBEDD')
    put(s, 'end1', L, 3108960, W, 822960, name)
    put(s, 'end2', L, 4023360, W, 457200, desc)
    return s


def tbl(slide, rows, widths, x=L, y=1737360, w=W, row_h=420000, size=12, head_fill=HEAD, first_col_bold=True):
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
s = page('작성 안내 (제출 전 삭제)', '작성 기준', '아래 기준에 맞춰 Ⅱ장의 담당 슬라이드를 작성. 이 슬라이드와 다음 예시 슬라이드 2장은 제출 전에 삭제')
tbl(s, [['구분', '기준'],
        ['글꼴', '한컴산뜻돋움 (모든 글)'],
        ['머리글 3줄', '첫 줄: 장 이름(11pt, 파랑) / 둘째 줄: 과업 분야(26pt, 남색) / 셋째 줄: 세부 항목 번호와 이름(14pt, 회색)'],
        ['본문 글', '개조식 명사형 종결(~임, ~함 대신 "~을 정리", "~으로 구성"). 본문 14~16pt, 표 안의 글 11~13pt'],
        ['색', '남색 003B71(제목·강조), 파랑 0070C0(번호·구분), 연한 파랑 EEF5FC(상자 바탕), 회색 6B7280(설명), 본문 2B2B2B'],
        ['슬라이드 구성', '세부 항목마다 조사 내용 → 비교·분석 → 검토 결과(적용 방향)의 순서. 한 항목이 한 장을 넘으면 슬라이드를 복제하여 사용'],
        ['표와 그림', '표 제목은 표 위, 그림 제목은 그림 아래. 출처가 있으면 아래에 "자료: 저자(연도)"로 표기'],
        ['분량', '세부 항목마다 1~3장. 전체 발표 시간에 맞춰 조정']],
    [16, 84], row_h=470000, size=13)
order.append(s)
s = page('작성 안내 (제출 전 삭제)', '작성 예시 ①: 글과 그림', '1-1 세부 항목 이름')
put(s, 'card', L, 1737360, 5486400, 4480560)
put(s, 'bold14', L + 228600, 1874520, 5029200, 320040, '조사 내용')
put(s, 'body', L + 228600, 2286000, 5029200, 3749040, '• 조사한 대상과 범위를 한 줄로\n• 핵심 내용 1\n• 핵심 내용 2\n• 핵심 내용 3', size=15)
put(s, 'card', 6217920, 1737360, 5468112, 3566160)
put(s, 'sub', 6217920, 3337560, 5468112, 320040, '(그림 자리)', align=PP_ALIGN.CENTER)
put(s, 'sub', 6217920, 5349240, 5468112, 320040, '그림 1. 그림 제목', size=12, align=PP_ALIGN.CENTER)
put(s, 'navy', 6217920, 5715000, 5468112, 502920)
put(s, 'bold14', 6309360, 5806440, 5285232, 320040, '검토 결과: 이 슬라이드의 결론을 한 문장으로', color='FFFFFF')
order.append(s)
s = page('작성 안내 (제출 전 삭제)', '작성 예시 ②: 표', '1-2 세부 항목 이름')
put(s, 'bold14', L, 1691640, W, 320040, '표 1. 표 제목')
tbl(s, [['구분', '항목 1', '항목 2', '항목 3'], ['대상 A', '내용', '내용', '내용'], ['대상 B', '내용', '내용', '내용'], ['대상 C', '내용', '내용', '내용']],
    [16, 28, 28, 28], y=2057400, row_h=560000, size=13)
put(s, 'sub', L, 4389120, W, 274320, '자료: 저자(연도)', size=11)
put(s, 'navy', L, 5486400, W, 594360)
put(s, 'bold14', L + 137160, 5623560, W - 274320, 320040, '검토 결과: 표에서 확인되는 내용과 본 과업의 적용 방향을 한두 문장으로', color='FFFFFF')
order.append(s)
order.append(toc)

# ------------------------------------------------------------------ Ⅰ 과업개요
order.append(divider('Ⅰ', '과업개요', '목적 및 배경, 과업범위, 추진 일정, 수행조직'))
s = page('Ⅰ. 과업개요', '1. 목적 및 배경', '과업의 기본 정보와 추진 배경, 목적')
tbl(s, [['구분', '내용'],
        ['과업명', '댐 운영 의사결정 프레임워크 구축 자문 용역'],
        ['발주기관', '한국수력원자력(주)'],
        ['수행기관', '국민대학교 산학협력단'],
        ['과업기간', '2026. 07. 23. ~ 2027. 01. 22. (착수일로부터 6개월)']],
    [20, 80], w=5486400, row_h=560000, size=13)
put(s, 'card', 6217920, 1737360, 5468112, 2103120)
put(s, 'bold14', 6400800, 1874520, 5120640, 320040, '추진 배경')
put(s, 'body', 6400800, 2240280, 5120640, 1508760, '댐 운영은 수문 자료뿐 아니라 과거 운영 경험, 매뉴얼, 관련 법령 등 비정형 자료에 대한 종합 판단이 필요하나, 이를 정형화하여 의사결정에 연결하는 모델·시스템이 부재', size=14)
put(s, 'card', 6217920, 3977640, 5468112, 2103120)
put(s, 'bold14', 6400800, 4114800, 5120640, 320040, '목적')
put(s, 'body', 6400800, 4480560, 5120640, 1508760, 'sLLM 기반 댐 운영 의사결정 및 발전 최적화 프레임워크 구축을 위한 기술적 타당성 검토', size=14)
order.append(s)
s = page('Ⅰ. 과업개요', '2. 과업범위', '4개 분야, 세부 항목 12개')
tbl(s, [['과업 분야', '세부 항목', '담당'],
        ['1. 국내외 기술 트렌드 조사', '1-1 수자원 분야 사례 조사\n1-2 국내 운영 여건 조사\n1-3 적용 기술요소 및 모델 제안', '수자원 연구실'],
        ['2. LLM 활용 데이터 파이프라인 조사', '2-1 수집 경로 조사\n2-2 온톨로지·메타데이터 설계방안 조사\n2-3 RAG-LLM 통합 파이프라인(안) 제시', '수자원 연구실'],
        ['3. sLLM 후보군 평가 방향', '3-1 후보 모델 조사\n3-2 모델 구조 및 특성 검토\n3-3 후보군 적용방안 제시', '인공지능학과'],
        ['4. 도메인 특화 성능 향상 전략', '4-1 RAG 기반 적용방안 조사\n4-2 경량 미세조정 방식 검토\n4-3 성능 향상 전략 제시', '인공지능학과']],
    [32, 50, 18], row_h=900000, size=13)
order.append(s)
s = page('Ⅰ. 과업개요', '3. 추진 일정', '세부 항목별 수행 기간 (착수 후 6개월)')
M = ["'26.8", "'26.9", "'26.10", "'26.11", "'26.12", "'27.1"]
SCH = [('1-1 수자원 분야 사례 조사', [1]), ('1-2 국내 운영 여건 조사', [1]), ('1-3 적용 기술요소 및 모델 제안', [2, 3]),
       ('2-1 수집 경로 조사', [2]), ('2-2 온톨로지·메타데이터 설계방안 조사', [2]), ('2-3 RAG-LLM 통합 파이프라인(안) 제시', [3, 4]),
       ('3-1 후보 모델 조사', [3]), ('3-2 모델 구조 및 특성 검토', [3, 4]), ('3-3 후보군 적용방안 제시', [5]),
       ('4-1 RAG 기반 적용방안 조사', [4]), ('4-2 경량 미세조정 방식 검토', [4, 5]), ('4-3 성능 향상 전략 제시', [6]), ('최종 보고서 작성', [5, 6])]
gt = tbl(s, [['수행 내용'] + M] + [[n] + ['' for _ in M] for n, _ in SCH], [40, 10, 10, 10, 10, 10, 10], row_h=320000, size=11, first_col_bold=False)
for i, (n, ms) in enumerate(SCH, 1):
    for j in ms:
        c = gt.cell(i, j); c.fill.solid(); c.fill.fore_color.rgb = RGBColor.from_string(BLUE)
order.append(s)
s = page('Ⅰ. 과업개요', '4. 수행조직', '참여 인력과 담당 업무')
tbl(s, [['구분', '성명', '전공 분야', '담당 업무'],
        ['책임연구원', '신주영', '수공학', '용역 총괄, 댐 운영 의사결정 및 수자원 분야 기술 검토'],
        ['연구원', '김장호', '인공지능', 'sLLM 후보군 평가, 모델 구조·특성 검토'],
        ['연구보조원', '문경민', '수공학', '데이터 파이프라인·온톨로지 조사 지원'],
        ['연구보조원', '황솔희', '인공지능', 'sLLM 후보 모델 조사·비교 지원']],
    [16, 14, 16, 54], row_h=640000, size=13)
order.append(s)

# ------------------------------------------------------------------ Ⅱ 사업수행 결과
order.append(divider('Ⅱ', '사업수행 결과', '과업 4개 분야, 세부 항목 12개의 수행 결과'))
ITEMS = [('1. 국내외 기술 트렌드 조사', '수자원 연구실', ['1-1 수자원 분야 사례 조사', '1-2 국내 운영 여건 조사', '1-3 적용 기술요소 및 모델 제안']),
         ('2. LLM 활용 데이터 파이프라인 조사', '수자원 연구실', ['2-1 수집 경로 조사', '2-2 온톨로지·메타데이터 설계방안 조사', '2-3 RAG-LLM 통합 파이프라인(안) 제시']),
         ('3. sLLM 후보군 평가 방향', '인공지능학과', ['3-1 후보 모델 조사', '3-2 모델 구조 및 특성 검토', '3-3 후보군 적용방안 제시']),
         ('4. 도메인 특화 성능 향상 전략', '인공지능학과', ['4-1 RAG 기반 적용방안 조사', '4-2 경량 미세조정 방식 검토', '4-3 성능 향상 전략 제시'])]
BW = (W - 2 * 137160) // 3
for field, owner, subs in ITEMS:
    for sub in subs:
        s = page('Ⅱ. 사업수행 결과', field, sub)
        for k, (hd, hint) in enumerate([('조사 내용', '조사한 대상과 범위,\n핵심 내용'), ('비교·분석', '조사한 대상을 같은 기준으로\n비교한 표나 그림'), ('검토 결과', '비교에서 확인된 내용과\n적용 방향(안)')]):
            x = L + k * (BW + 137160)
            put(s, 'card', x, 1737360, BW, 3886200)
            put(s, 'bold14', x + 182880, 1874520, BW - 365760, 320040, hd)
            put(s, 'body', x + 182880, 2286000, BW - 365760, 3200400, hint, size=14, color=GRAY)
        put(s, 'navy', L, 5760720, W, 502920)
        put(s, 'bold14', L + 137160, 5852160, W - 274320, 320040, '[작성] 담당: %s  ·  이 줄에 슬라이드의 결론을 한 문장으로 작성' % owner, color='FFFFFF')
        order.append(s)

# ------------------------------------------------------------------ Ⅲ 향후 추진계획, 맺음
order.append(divider('Ⅲ', '향후 추진계획', '향후 연구개발 방향과 추진 계획(안)'))
s = page('Ⅲ. 향후 추진계획', '향후 추진계획', '연구개발 추진 방향 및 로드맵(안)')
put(s, 'card', L, 1737360, W, 3886200)
put(s, 'body', L + 228600, 1920240, W - 457200, 3474720, '[작성] 담당: 책임연구원', size=14, color=GRAY)
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
