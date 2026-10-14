#!/usr/bin/env python3
"""학회 포스터 초안: KSCE 포스터 템플릿(pptx)의 머리띠·제목 양식을 유지하고 본문을 댐 운영 KG-LLM 연구 내용으로 채운다.
사용: python3 scripts/build_poster.py <템플릿.pptx> <출력.pptx> [--scale N]   (--scale: 미리보기용으로 전체 크기를 1/N로 줄인 사본)
그림: team_brief/fig0_framework.png, fig2_kg_example.png, KMU 로고(poster_assets/kmu_logo.png)
"""
import os, re, shutil, sys, zipfile, struct
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
ASSET = os.path.join(ROOT, 'lab_meeting', 'poster_assets')
EMU_PT = 12700
BODY = 2600   # 본문 글자 크기(1/100 pt)
TBL = 2200    # 표 글자 크기

# ---------------------------------------------------------------- 글자 폭으로 높이 추정
def tw(text, sz):
    w = 0.0
    for ch in text:
        o = ord(ch)
        if o > 0x2E80: w += 0.93
        elif ch == ' ': w += 0.32
        elif ch.isupper() or ch.isdigit(): w += 0.62
        else: w += 0.52
    return w * sz / 100

def lines_needed(text, sz, width_emu):
    avail = width_emu / EMU_PT
    n, cur = 1, 0.0
    for word in re.split(r'(?<=\s)', text):
        ww = tw(word, sz)
        if cur + ww > avail and cur > 0:
            n += 1; cur = ww
        else:
            cur += ww
    return n

# ---------------------------------------------------------------- XML 부품
FONT = ('<a:latin typeface="나눔고딕" pitchFamily="50" charset="-127"/><a:ea typeface="나눔고딕" pitchFamily="50" charset="-127"/>'
        '<a:cs typeface="Arial" panose="020B0604020202020204" pitchFamily="34" charset="0"/>')
INK = '<a:solidFill><a:schemeClr val="tx1"><a:lumMod val="85000"/><a:lumOff val="15000"/></a:schemeClr></a:solidFill>'
WHITE = '<a:solidFill><a:schemeClr val="bg1"/></a:solidFill>'
NAVY = '<a:solidFill><a:srgbClr val="1F4E79"/></a:solidFill>'

_id = [1000]
def nid():
    _id[0] += 1
    return _id[0]

def run(t, sz, b=False, fill=INK, base=None):
    return ('<a:r><a:rPr lang="ko-KR" altLang="en-US" sz="%d" b="%d"%s dirty="0">%s%s</a:rPr><a:t>%s</a:t></a:r>'
            % (sz, 1 if b else 0, ' baseline="30000"' if base else '', fill, FONT, escape(t)))

def runs(spec, sz, fill=INK, bold_all=False):
    """spec: 문자열 또는 [(글자, 굵게)] — '**굵게**' 표기를 지원"""
    out = []
    for i, part in enumerate(re.split(r'\*\*', spec)):
        if part:
            out.append(run(part, sz, bold_all or i % 2 == 1, fill))
    return ''.join(out)

def plain(spec):
    return spec.replace('**', '')

def para(spec, sz, bullet=True, algn=None, spc_aft=600, lnspc=118000, fill=INK, bold_all=False, indent=0, marL=None):
    if bullet:
        ppr = ('<a:pPr marL="%d" indent="-%d"><a:lnSpc><a:spcPct val="%d"/></a:lnSpc><a:spcAft><a:spcPts val="%d"/></a:spcAft>'
               '<a:buBlip><a:blip r:embed="rId4"/></a:buBlip></a:pPr>' % (334726 + indent, 334726, lnspc, spc_aft))
    else:
        ppr = ('<a:pPr marL="%d" indent="0"%s><a:lnSpc><a:spcPct val="%d"/></a:lnSpc><a:spcAft><a:spcPts val="%d"/></a:spcAft><a:buNone/></a:pPr>'
               % (marL or 0, ' algn="%s"' % algn if algn else '', lnspc, spc_aft))
    return '<a:p>%s%s</a:p>' % (ppr, runs(spec, sz, fill, bold_all))

def est_h(items, sz, width, bullet=True, spc_aft=600, lnspc=1.18, pad=66158):
    h = 2 * 33079
    for it in items:
        n = lines_needed(plain(it), sz, width - 2 * pad - (334726 if bullet else 0))
        h += n * sz / 100 * 1.2 * lnspc * EMU_PT + spc_aft / 100 * EMU_PT
    return int(h)

def textbox(x, y, w, paras, h, name='본문', fill=None, line=None, anchor='t', pad=66158):
    sp = '<a:solidFill><a:srgbClr val="%s"/></a:solidFill>' % fill if fill else '<a:noFill/>'
    ln = '<a:ln w="19050"><a:solidFill><a:srgbClr val="%s"/></a:solidFill></a:ln>' % line if line else '<a:ln><a:noFill/></a:ln>'
    return ('<p:sp><p:nvSpPr><p:cNvPr id="%d" name="%s"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>%s%s</p:spPr><p:txBody><a:bodyPr wrap="square" lIns="%d" tIns="33079" rIns="%d" bIns="33079" anchor="%s"><a:noAutofit/></a:bodyPr><a:lstStyle/>%s</p:txBody></p:sp>'
            % (nid(), name, x, y, w, h, sp, ln, pad, pad, anchor, ''.join(paras)))

def pic(rid, x, y, w, h, name='그림', descr=''):
    return ('<p:pic><p:nvPicPr><p:cNvPr id="%d" name="%s" descr="%s"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
            '<p:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/></a:stretch></p:blipFill><p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:ln w="12700"><a:solidFill><a:srgbClr val="BFC5CC"/></a:solidFill></a:ln></p:spPr></p:pic>'
            % (nid(), name, escape(descr), rid, x, y, w, h))

def table(x, y, colw, rows, sz=2400, rowh=None, head_fill='1F4E79', band='EEF3F8', first_col_bold=True):
    """rows[0]은 머리글. 셀은 문자열(‘**’ 굵게 허용). 높이는 줄 수로 추정하여 (표 높이)를 돌려준다."""
    W = sum(colw)
    trs, total = [], 0
    for ri, row in enumerate(rows):
        nl = max(lines_needed(plain(c), sz, colw[ci] - 2 * 91440) for ci, c in enumerate(row))
        rh = int(nl * sz / 100 * 1.25 * EMU_PT + 2 * 60000 + 30000)
        total += rh
        tcs = []
        for ci, c in enumerate(row):
            head = ri == 0
            fill = head_fill if head else (band if ri % 2 == 0 else 'FFFFFF')
            col = WHITE if head else INK
            algn = 'ctr' if head or (ci == len(row) - 1 and len(plain(c)) <= 5) else 'l'
            bold = head or (first_col_bold and ci == 0)
            body = '<a:p><a:pPr algn="%s"><a:lnSpc><a:spcPct val="105000"/></a:lnSpc></a:pPr>%s</a:p>' % (algn, runs(c, sz, col, bold))
            bd = ''.join('<a:%s w="9525"><a:solidFill><a:srgbClr val="9AA7B5"/></a:solidFill></a:%s>' % (e, e) for e in ('lnL', 'lnR', 'lnT', 'lnB'))
            tcs.append('<a:tc><a:txBody><a:bodyPr/><a:lstStyle/>%s</a:txBody><a:tcPr marL="91440" marR="91440" marT="60000" marB="60000" anchor="ctr">%s<a:solidFill><a:srgbClr val="%s"/></a:solidFill></a:tcPr></a:tc>' % (body, bd, fill))
        trs.append('<a:tr h="%d">%s</a:tr>' % (rh, ''.join(tcs)))
    grid = ''.join('<a:gridCol w="%d"/>' % c for c in colw)
    xml = ('<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="%d" name="표"/><p:cNvGraphicFramePr><a:graphicFrameLocks noGrp="1"/></p:cNvGraphicFramePr><p:nvPr/></p:nvGraphicFramePr>'
           '<p:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></p:xfrm><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/table">'
           '<a:tbl><a:tblPr firstRow="1" bandRow="1"/><a:tblGrid>%s</a:tblGrid>%s</a:tbl></a:graphicData></a:graphic></p:graphicFrame>'
           % (nid(), x, y, W, total, grid, ''.join(trs)))
    return xml, total

# ---------------------------------------------------------------- 템플릿 블록 재사용
def blocks(s):
    return {m.group(0): m for m in re.finditer(r'<p:sp>.*?</p:sp>', s, flags=re.S)}

def find_sp(s, name):
    for m in re.finditer(r'<p:sp>.*?</p:sp>', s, flags=re.S):
        if 'name="%s"' % name in m.group(0):
            return m.group(0)
    raise KeyError(name)

def set_xfrm(b, x, y, w, h):
    return re.sub(r'<a:off x="-?\d+" y="-?\d+"/><a:ext cx="\d+" cy="\d+"/>', '<a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/>' % (x, y, w, h), b, count=1)

def set_id(b, name=None):
    b = re.sub(r'<p:cNvPr id="\d+"', '<p:cNvPr id="%d"' % nid(), b, count=1)
    b = re.sub(r'<a:extLst>.*?</a:extLst>', '', b, count=1, flags=re.S) if '<a:extLst>' in b.split('</p:cNvPr>')[0] or True else b
    return b

def header_bar(tpl, x, y, w, text):
    b = set_xfrm(set_id(tpl), x, y, w, 1023024)
    rpr = re.search(r'<a:rPr lang="ko-KR".*?</a:rPr>', b, flags=re.S).group(0)
    b = re.sub(r'<a:p>.*</a:p>', '<a:p><a:pPr defTabSz="2048653"/><a:r>%s<a:t>%s</a:t></a:r></a:p>' % (rpr, escape(text)), b, flags=re.S)
    return b.replace('wrap="none"', 'wrap="square"')

def label_pill(tpl, x, y, w, text, sz=3600):
    b = set_xfrm(set_id(tpl), x, y, w, 705340)
    b = re.sub(r'<a:t>[^<]*</a:t>', '<a:t>%s</a:t>' % escape(text), b, count=1)
    b = re.sub(r'sz="4000"', 'sz="%d"' % sz, b)
    return b

def caption_bar(tpl, x, y, w, text):
    b = set_xfrm(set_id(tpl), x, y, w, 645985)
    rpr = re.search(r'<a:rPr lang="ko-KR".*?</a:rPr>', b, flags=re.S).group(0)
    b = re.sub(r'<a:p>.*</a:p>', '<a:p><a:pPr marL="0" lvl="1"><a:lnSpc><a:spcPct val="107000"/></a:lnSpc></a:pPr><a:r>%s<a:t>%s</a:t></a:r></a:p>' % (rpr, escape(text)), b, flags=re.S)
    return b

def png_size(path):
    with open(path, 'rb') as f:
        d = f.read(24)
    return struct.unpack('>II', d[16:24])

# ---------------------------------------------------------------- 내용
TITLE_KO = '온톨로지 기반 지식그래프를 활용한 댐 운영 의사결정 지원 LLM 프레임워크 구축'
TITLE_EN = 'Development of an LLM Framework for Dam Operation Decision Support Using an Ontology-based Knowledge Graph'
AUTH_KO = [('문경민', '*'), ('신주영', '**'), ('장상범', '***'), ('조수빈', '****')]
AUTH_EN = 'Moon, Kyeungmin ・ Shin, Ju-Young ・ Jang, Sangbeom ・ Cho, Subin'
AFFIL = [('*', '국민대학교 건설시스템공학과 석사과정'), ('**', '국민대학교 건설시스템공학과 교수'), ('***', '국민대학교 건설시스템공학과 석사과정'), ('****', '국민대학교 건설시스템공학과 석사과정')]

INTRO = [
    '댐 운영 판단에는 **방류 승인 기록**, **수문기상 시간 자료**, **규정의 홍수기 제한수위**를 함께 확인해야 하나, 자료마다 형식과 이름이 달라 사람이 일일이 연결해야 함',
    '대규모 언어모델(LLM)은 자연어 질의응답에 유용하나, 단독 활용 시 답변의 **근거를 확인하기 어려워** 구조화된 지식과의 연계가 필요함',
    '본 연구는 **온톨로지 기반 지식그래프(KG)** 와 **하이브리드 검색**, **LLM**을 연계하여 운영자의 **근거 기반 의사결정을 지원하는 프레임워크**를 구축하고자 함',
]
METHOD = [
    '**STEP 1 Ontology 설계**: 운영자에게 필요한 질문(Competency Question, CQ) 7개를 먼저 정하고, 이에 답하도록 **개체 6종류**(댐, 수문기상 상태, 방류 승인, 운영행위, 운영기준, 근거자료)와 **관계 9종류**를 설계함',
    '**STEP 2 KG 구축**: 자료를 표 경로(열 이름으로 매핑)와 글 경로(규칙으로 추출)로 나누어 7단계로 구축함. 수치 전체와 규정 원문은 KG 밖 저장소에 두고, KG에는 관계와 근거의 위치(번호)만 저장함',
    '**STEP 3 질문 처리**: LLM이 질문을 유형과 값(댐, 시점)으로 변환 → Cypher로 KG 탐색 → 번호로 측정자료·문서 저장소 조회 → 계산은 코드가 수행 → 모은 **근거 안에서만** LLM이 답변하고 출처 번호를 붙임',
]
DATA_ROWS = [
    ['자료', '규모', 'KG 반영 방식'],
    ['방류 승인 기록', '4개 댐 승인 80건', 'Approval 80, 비고 분류로 Operation 68'],
    ['수문기상 시간 자료', '508,246행 (수위·유입량 등 6변수)', '측정자료 저장소에 보관, KG에는 상태 항목 24개'],
    ['규정 별표3 (제한수위)', '10조각 (현행 1 + 연혁 9)', 'Criterion 3, 원문은 문서 저장소'],
]
DATA_BUL = [
    '승인 기록의 **비고 문장**은 키워드 규칙으로 분류하여 운영행위를 만들고, 변경·연장·정정 문구는 새 운영행위로 만들지 않음',
    '운영행위 시각은 **비고 명시 → 측정 방류량 변화 → 승인 시작 시각** 순서로 정함 (68건: 측정 54, 승인 시작 11, 비고 명시 3)',
]
KG_ROWS = [
    ['구분', '종류', '개수'],
    ['개체', 'Dam 4, HMS 24, Approval 80, Operation 68, Criterion 3, EvidenceSource 94', '273'],
    ['관계', '허가한다, 대상 댐, 수행된 댐, 상태 보유, 적용되는 댐, 근거 등 9종류', '457'],
    ['속성', '승인일, 방류 시작 시각, 승인 방류량, 제한수위 등', '653행'],
]
KG_BUL = [
    '구조 검증 **5개 항목**에서 어긋남은 0건이었고, 승인 80건 모두 **승인–운영행위–댐–상태–근거자료**로 이어져 질문 경로를 따라 근거를 찾을 수 있음',
]
QT_ROWS = [
    ['질문 유형', '뜻', '예시 질문'],
    ['CQ1', '현재 수문기상 상태', '소양강댐 지금 수위는?'],
    ['CQ2', '과거 수문기상 상태', '충주댐 2012-08-24 16:00의 수위는?'],
    ['CQ3', '과거 운영행위', '충주댐 2012-08-24에 수행된 운영행위는?'],
    ['CQ4', '과거 방류 승인', '충주댐 2012-08-24의 방류 승인 내용은?'],
    ['CQ5', '현재 운영기준', '충주댐의 홍수기 제한수위는?'],
    ['CQ6', '공식 근거', '충주댐 승인 1368번의 공식 근거는?'],
    ['SIMILAR', '현재와 비슷한 과거 사례', '소양강댐 지금과 비슷했던 과거 사례는?'],
]
QA_ROWS = [
    ['단계', '실제 내용 (소양강댐, SIMILAR 질문)'],
    ['① 질문 해석 (LLM)', '{"intent": "SIMILAR", "slots": {"dam": "소양강댐", "k": 1}}'],
    ['② 현재 상태·기준', '수위 185.2644 EL.m, 제한수위 190.3 EL.m → 제한수위보다 **5.04 m 낮음** (코드가 계산)'],
    ['③ 비슷한 과거 사례', '수위·유입량을 0~1로 정규화한 거리가 가장 작은 시점: **2017-08-25 15:00 (거리 0.223)**'],
    ['④ 운영행위·승인', '탄력적 방류 [OPR:2754:2], 승인 [APR:2754], 승인 방류량 1500 ㎥/s'],
    ['⑤ 승인량 대비 방류량', '사례 전후 최대 총방류량 1011.2 CMS = **승인량의 67.4%** (코드가 계산)'],
    ['⑥ LLM 답변', '“소양강댐 현재 수위는 185.2644 EL.m로, 제한수위 190.3 EL.m 대비 −5.04 m입니다 [CRI:CR-01] …” (출처 번호 포함)'],
]
QA_BUL = [
    '질문 해석은 **Qwen3-8B**(vLLM)가 JSON으로 출력하고, 코드가 질문 유형·댐·날짜 값을 검증함',
    '숫자 계산과 비슷한 사례 선택은 **코드**가 하고, 답변은 **근거 모음**의 번호 붙은 자료를 바탕으로 **LLM**이 작성하여 운영자가 출처를 확인할 수 있음',
]
CONCL = [
    '댐 운영 자료(방류 승인 기록, 수문기상 시간 자료, 규정 별표3)를 **Ontology(개체 6종류, 관계 9종류)** 에 맞춰 **KG(개체 273, 관계 457)** 로 구축하고, 수치·원문은 외부 저장소에 두어 KG는 연결과 근거 위치만 담도록 함',
    'KG와 측정자료·문서 저장소를 함께 찾는 **하이브리드 검색**과, 출처 번호가 붙은 근거 안에서 답하는 **LLM**을 연계한 **질문 응답 프레임워크**를 구축함',
    '운영자가 현재 상태, 제한수위, 과거 승인·운영행위, 비슷한 과거 사례를 **근거와 함께** 확인할 수 있어 **댐 운영 의사결정을 지원**함',
]
ACK = '본 결과물은 기후에너지환경부의 재원으로 한국환경산업기술원의 기후변화 적응 수재해 관리 기술개발사업(R&D)의 지원을 받아 연구되었습니다(RS-2026-25502939). 본 연구는 기후에너지환경부「기후변화특성화대학원사업」의 지원으로 수행되었습니다.'
REFS = [
    'Purohit, S., Chin, G., Mackey, P. S. and Cottam, J. A. (2024). “GraphAide: Advanced graph-assisted query and reasoning system.” Proc. IEEE Int. Conf. on Big Data (BigData), pp. 3485-3493.',
    'Papadakis, E., McCluskey, T. L., Louadah, H. and Tucker, G. (2023). “Ontology-guided knowledge graph construction to support scheduling in a train maintenance depot.” CEUR Workshop Proceedings, Vol. 3493.',
    'Li, S., Erickson, C., Zajac, M., Guo, X., Duan, Q. and Gong, J. (2025). “A semi-automated framework for flood ontology construction with an application in risk communication.” Water, Vol. 17, No. 19, 2801.',
    'Noy, N. F. and McGuinness, D. L. (2001). “Ontology development 101: A guide to creating your first ontology.” Stanford Knowledge Systems Laboratory Technical Report KSL-01-05.',
]

# ---------------------------------------------------------------- 조립
def build(tpl_path, out_path, scale=1):
    work = out_path + '.dir'
    shutil.rmtree(work, ignore_errors=True)
    with zipfile.ZipFile(tpl_path) as z:
        z.extractall(work)
    sp = os.path.join(work, 'ppt', 'slides', 'slide1.xml')
    s = open(sp, encoding='utf8').read()

    head = re.search(r'<p:grpSp>.*?</p:grpSp>', s, flags=re.S).group(0).replace('KSCE 2023 CONVENTION', 'KSCE 2026 CONVENTION')
    t_hdr = find_sp(s, '직사각형 1')
    t_pill = find_sp(s, '모서리가 둥근 직사각형 25')
    t_cap = find_sp(s, '직사각형 415')
    t_title = find_sp(s, '직사각형 5')

    # 그림 파일 복사 및 관계
    media = os.path.join(work, 'ppt', 'media')
    imgs = {'rId11': os.path.join(ASSET, 'poster_fig1_framework.png'),
            'rId12': os.path.join(ASSET, 'poster_fig2_kg.png'),
            'rId13': os.path.join(ASSET, 'kmu_logo.png')}
    rels_p = os.path.join(work, 'ppt', 'slides', '_rels', 'slide1.xml.rels')
    rels = open(rels_p, encoding='utf8').read()
    add = ''
    for rid, p in imgs.items():
        fn = 'poster_%s.png' % rid
        shutil.copy(p, os.path.join(media, fn))
        add += '<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/%s"/>' % (rid, fn)
    open(rels_p, 'w', encoding='utf8').write(rels.replace('</Relationships>', add + '</Relationships>'))

    shapes = [head]
    # --- 제목 영역
    tt = set_xfrm(set_id(t_title), 5992955, 300000, 20582661, 2700000)
    kr_rpr = re.search(r'<a:rPr lang="ko-KR".*?</a:rPr>', tt, flags=re.S).group(0).replace('sz="7063"', 'sz="5000"')
    en_rpr = re.search(r'<a:rPr lang="en-US" altLang="ko-KR" sz="5779".*?</a:rPr>', tt, flags=re.S).group(0).replace('sz="5779"', 'sz="3000"')
    tt = re.sub(r'<a:p>.*</a:p>', '<a:p><a:pPr algn="ctr"><a:lnSpc><a:spcPct val="115000"/></a:lnSpc></a:pPr><a:r>%s<a:t>%s</a:t></a:r></a:p>'
                '<a:p><a:pPr algn="ctr"><a:lnSpc><a:spcPct val="115000"/></a:lnSpc></a:pPr><a:r>%s<a:t>%s</a:t></a:r></a:p>' % (kr_rpr, escape(TITLE_KO), en_rpr, escape(TITLE_EN)), tt, flags=re.S)
    tt = tt.replace('<a:spAutoFit/>', '<a:noAutofit/>')
    shapes.append(tt)

    def wr(t, sz, base=False):
        return ('<a:r><a:rPr lang="ko-KR" altLang="en-US" sz="%d"%s dirty="0">%s%s</a:rPr><a:t>%s</a:t></a:r>' % (sz, ' baseline="30000"' if base else '', WHITE, FONT, escape(t)))
    au = ''.join(wr(n, 4000) + wr(m, 4000, True) + (wr('․', 4000) if i < 3 else '') for i, (n, m) in enumerate(AUTH_KO))
    shapes.append(textbox(5992958, 3080000, 20582660,
                          ['<a:p><a:pPr algn="ctr"><a:lnSpc><a:spcPct val="120000"/></a:lnSpc></a:pPr>%s</a:p>' % au,
                           '<a:p><a:pPr algn="ctr"/>%s</a:p>' % wr(AUTH_EN, 2800)], 1400000, name='저자'))
    af = ''.join(wr(m, 2600, True) + wr(t + ('   ' if i < 3 else ''), 2600) for i, (m, t) in enumerate(AFFIL))
    shapes.append(textbox(1327064, 4600000, 27500000, ['<a:p><a:pPr algn="ctr"/>%s</a:p>' % af], 560000, name='소속'))
    # --- 학교 로고(오른쪽 위): 흰 원 위에 올림
    shapes.append('<p:sp><p:nvSpPr><p:cNvPr id="%d" name="로고 배경"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="26850000" y="600000"/><a:ext cx="3000000" cy="3000000"/></a:xfrm>'
                  '<a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill><a:ln><a:noFill/></a:ln></p:spPr></p:sp>' % nid())
    shapes.append(pic('rId13', 26950000, 700000, 2800000, 2800000, '국민대학교 로고', 'Kookmin University'))

    LX, RX, CW = 597946, 15570184, 14113138
    HX_L, HX_R, HW = 674157, 15691431, 13943667
    GAP = 380000
    log = {}

    def section(col, y, title, body_items=None, sz=None):
        x, hx = (LX, HX_L) if col == 'L' else (RX, HX_R)
        shapes.append(header_bar(t_hdr, hx, y, HW, title))
        y += 1023024 + 120000
        if body_items:
            h = est_h(body_items, BODY, CW)
            shapes.append(textbox(x, y, CW, [para(t, BODY) for t in body_items], h))
            y += h
        return y

    def figure(col, y, rid, path, width, caption=None):
        x = LX if col == 'L' else RX
        pw, ph = png_size(path)
        h = int(width * ph / pw)
        shapes.append(pic(rid, x + (CW - width) // 2, y, width, h, caption or '그림', caption or ''))
        y += h + 60000
        if caption:
            shapes.append(textbox(x, y, CW, [para(caption, 2400, bullet=False, algn='ctr', bold_all=False, fill=INK)], 800000))
            y += 800000
        return y

    def tbl(col, y, cap, colw, rows, sz=TBL):
        x = LX if col == 'L' else RX
        shapes.append(caption_bar(t_cap, x + 232858, y, CW - 463716, cap))
        y += 645985 + 90000
        xml, h = table(x + 100000, y, colw, rows, sz)
        shapes.append(xml)
        return y + h + 120000

    # 왼쪽 열
    y = 6350000
    y = section('L', y, '서론', INTRO) + GAP
    y = section('L', y, '연구방법', None)
    y = figure('L', y, 'rId11', imgs['rId11'], 11000000, '그림 1. 연구의 구성: Ontology 설계 → KG 구축 → 질문 처리(하이브리드 검색 + LLM)')
    items = METHOD
    h = est_h(items, BODY, CW)
    shapes.append(textbox(LX, y, CW, [para(t, BODY) for t in items], h)); y += h + 60000
    y = tbl('L', y, 'Table 1. 질문 유형(CQ1~CQ6 + SIMILAR)', [1900000, 4200000, 7500000], QT_ROWS) + GAP - 120000
    y = section('L', y, '대상 자료 및 KG 구축 규칙', None)
    y = tbl('L', y, 'Table 2. 사용한 자료와 KG 반영 방식', [3000000, 4200000, 6400000], DATA_ROWS)
    h = est_h(DATA_BUL, BODY, CW)
    shapes.append(textbox(LX, y, CW, [para(t, BODY) for t in DATA_BUL], h)); y += h
    log['L_end'] = y

    # 오른쪽 열
    y = 6350000
    y = section('R', y, 'KG 구축 결과', None)
    y = tbl('R', y, 'Table 3. 구축한 지식그래프의 규모', [1600000, 10400000, 1600000], KG_ROWS)
    y = figure('R', y, 'rId12', imgs['rId12'], 10500000, '그림 2. 지식그래프의 일부: 충주댐 승인 1368번')
    h = est_h(KG_BUL, BODY, CW)
    shapes.append(textbox(RX, y, CW, [para(t, BODY) for t in KG_BUL], h)); y += h + GAP
    y = section('R', y, '질문 처리 과정과 예시', None)
    y = tbl('R', y, 'Table 4. SIMILAR 질문의 처리 과정', [3200000, 10400000], QA_ROWS)
    h = est_h(QA_BUL, BODY, CW)
    shapes.append(textbox(RX, y, CW, [para(t, BODY) for t in QA_BUL], h)); y += h + GAP
    y = section('R', y, '결론', CONCL) + GAP
    y = section('R', y, '감사의 글', None)
    h = est_h([ACK], 2000, CW, bullet=False)
    shapes.append(textbox(RX, y, CW, [para(ACK, 2000, bullet=False)], h)); y += h + 150000
    y = section('R', y, '참고문헌', None)
    h = est_h(REFS, 1800, CW, bullet=False, spc_aft=300)
    shapes.append(textbox(RX, y, CW, [para('%d. %s' % (i + 1, r), 1800, bullet=False, spc_aft=300) for i, r in enumerate(REFS)], h)); y += h
    log['R_end'] = y

    body = ''.join(shapes)
    head_xml = s[:s.index('<p:grpSp>')]
    tail = s[s.rindex('</p:spTree>'):]
    new = head_xml + body + tail
    open(sp, 'w', encoding='utf8').write(new)

    if scale > 1:
        pres = os.path.join(work, 'ppt', 'presentation.xml')
        ps = open(pres, encoding='utf8').read()
        def div(m): return '%s="%d"' % (m.group(1), int(int(m.group(2)) / scale))
        ps = re.sub(r'(cx|cy)="(\d+)"', div, ps, count=2)
        open(pres, 'w', encoding='utf8').write(ps)
        n = open(sp, encoding='utf8').read()
        n = re.sub(r'\b(x|y|cx|cy)="(-?\d+)"', lambda m: '%s="%d"' % (m.group(1), int(m.group(2)) / scale), n)
        n = re.sub(r'\bsz="(\d+)"', lambda m: 'sz="%d"' % max(100, int(int(m.group(1)) / scale)), n)
        n = re.sub(r'\b(marL|indent|lIns|rIns|tIns|bIns)="(-?\d+)"', lambda m: '%s="%d"' % (m.group(1), int(m.group(2)) / scale), n)
        n = re.sub(r'(<a:spcPts val=")(\d+)', lambda m: m.group(1) + str(int(int(m.group(2)) / scale)), n)
        n = re.sub(r'(<a:(?:gridCol|tr)\b[^>]*?\b)(w|h)="(\d+)"', lambda m: '%s%s="%d"' % (m.group(1), m.group(2), int(m.group(3)) / scale), n)
        open(sp, 'w', encoding='utf8').write(n)
        lay = os.path.join(work, 'ppt', 'slideLayouts', 'slideLayout1.xml')
        l = open(lay, encoding='utf8').read()
        l = re.sub(r'\b(x|y|cx|cy)="(-?\d+)"', lambda m: '%s="%d"' % (m.group(1), int(m.group(2)) / scale), l)
        open(lay, 'w', encoding='utf8').write(l)

    if os.path.exists(out_path):
        os.remove(out_path)
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as z:
        # [Content_Types].xml 을 먼저 넣는다
        z.write(os.path.join(work, '[Content_Types].xml'), '[Content_Types].xml')
        for dp, _, fs in os.walk(work):
            for f in fs:
                full = os.path.join(dp, f)
                arc = os.path.relpath(full, work)
                if arc != '[Content_Types].xml':
                    z.write(full, arc)
    shutil.rmtree(work)
    return log

if __name__ == '__main__':
    a = sys.argv[1:]
    sc = 1
    if '--scale' in a:
        i = a.index('--scale'); sc = int(a[i + 1]); del a[i:i + 2]
    print(build(a[0], a[1], sc))
