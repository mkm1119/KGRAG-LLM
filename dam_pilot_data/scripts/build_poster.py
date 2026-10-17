#!/usr/bin/env python3
"""학회 포스터 초안: KSCE 포스터 템플릿(pptx)의 머리띠·제목 양식을 유지하고 본문을 댐 운영 KG-LLM 연구 내용으로 채운다.
사용: python3 scripts/build_poster.py <템플릿.pptx> <출력.pptx> [--scale N]   (--scale: 미리보기용으로 전체 크기를 1/N로 줄인 사본)
그림: team_brief/fig0_framework.png, fig2_kg_example.png, KMU 로고(poster_assets/kmu_logo.png)
"""
import os, re, shutil, sys, zipfile, struct
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
import importlib.util as _iu
_sp = _iu.spec_from_file_location('pptx_shapes', os.path.join(HERE, 'pptx_shapes.py')); SH = _iu.module_from_spec(_sp); _sp.loader.exec_module(SH)
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
ASSET = os.path.join(ROOT, 'lab_meeting', 'poster_assets')
EMU_PT = 12700
BODY = 2300   # 본문 글자 크기(1/100 pt)
TBL = 2100    # 표 글자 크기

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
    avail = width_emu / EMU_PT * 0.92   # 굵은 글씨·단어 단위 줄바꿈 여유
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
        nl = max(sum(lines_needed(plain(t), sz, colw[ci] - 2 * 91440) for t in c.split('\n')) for ci, c in enumerate(row))
        rh = int(nl * sz / 100 * 1.25 * EMU_PT + 2 * 60000 + 30000)
        total += rh
        tcs = []
        for ci, c in enumerate(row):
            head = ri == 0
            fill = head_fill if head else (band if ri % 2 == 0 else 'FFFFFF')
            col = WHITE if head else INK
            algn = 'ctr' if head or (ci == len(row) - 1 and len(plain(c)) <= 5) else 'l'
            bold = head or (first_col_bold and ci == 0)
            body = ''.join('<a:p><a:pPr algn="%s"><a:lnSpc><a:spcPct val="105000"/></a:lnSpc></a:pPr>%s</a:p>' % (algn, runs(t, sz, col, bold)) for t in c.split('\n'))
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
    '댐 운영 판단에는 **방류 승인 기록**, **수문·기상 관측 자료**, **운영 규정** 등 여러 자료를 함께 확인해야 하나, 자료마다 형식과 이름이 달라 사람이 일일이 연결해야 함',
    '대규모 언어모델(LLM) 단독 활용은 답변의 **근거를 확인하기 어려워**, 외부 자료를 검색해 답변에 활용하는 **검색증강생성(RAG)** 이 쓰이나, 자료 간 관계와 출처를 함께 다루려면 구조화된 지식이 필요함',
    '본 연구는 **온톨로지 기반 지식그래프(KG)** 를 RAG 기반 검색 및 LLM 답변 생성과 연계하여, 운영자의 **근거 기반 의사결정을 지원하는 프레임워크**를 구축함',
    '**온톨로지**는 대상(Class)과 관계를 정리한 의미 구조이고, **KG**는 여기에 실제 개체·관계를 채운 그래프이며, **RAG**는 근거를 검색해 LLM에 주고 그 근거로 답하게 하는 방식임',
]
CONCEPT_ROWS = [
    ['용어', '설명'],
    ['온톨로지 / Class / Entity', '댐 운영 분야의 대상 종류(Class, 예: 댐)와 관계·속성을 정리한 의미 구조. Entity는 Class에 속한 실제 개체(예: 충주댐)'],
    ['관계 / Data Property', '관계는 개체 사이의 연결(예: 승인이 운영행위를 허가함), Data Property는 개체가 가진 값(예: 승인일)'],
    ['CQ', 'Competency Question. 온톨로지가 답할 수 있어야 하는 질문으로, 필요한 Class·관계를 정하는 기준'],
    ['지식그래프 (KG)', '온톨로지에 실제 개체·관계·값을 채운 그래프. Neo4j(그래프 DB)에 저장하고 Cypher(연결 패턴으로 찾는 질의 언어)로 조회'],
    ['구조화 자료 / 문서 자료', '표(구조화 자료)는 규칙으로 개체·속성에 옮기고, 글 속의 값(승인 비고, 규정 별표)은 규칙으로 추출'],
    ['외부 저장소', 'KG 밖에 둔 측정값 전체(측정자료 저장소)와 규정 원문(문서 저장소). KG에는 찾아가는 키만 둠'],
    ['RAG', '질문과 관련된 근거를 검색해 LLM에 함께 주고, 그 근거로 답하게 하는 방식'],
    ['의도 / 근거 묶음', '의도는 질문이 CQ1~CQ6 중 무엇을 묻는지의 분류(복수 가능), 근거 묶음은 검색한 근거에 출처 번호를 붙여 LLM에 주는 입력'],
]
OVERVIEW_BUL = [
    '프레임워크는 **세 단계**로 구성됨: **① Ontology 설계 → ② KG 구축 → ③ 근거 기반 질의응답**',
    '각 단계의 **방법**을 설명하고, 이해를 돕기 위해 **충주댐 승인 기록**을 예시로 따라감',
]
ST1_BUL = [
    '운영자가 확인해야 할 질문을 **전체 질문 1개와 세부 질문 6개(CQ1~CQ6)** 로 정함',
    '이 질문에 답하는 데 필요한 **Class 6개와 관계 9개**, Class별 **Data Property**를 정의함',
]
ST2_BUL = [
    '자료의 형태에 맞게 **6단계**로 처리하여 Ontology에 맞는 개체와 관계로 구축함',
    '측정값 전체와 규정 원문은 KG 밖 저장소에 두고, KG에는 **찾아가는 키**만 저장함',
]
KG_EXPL = [
    '구축된 KG의 일부(충주댐 승인 기록 한 건): 승인 기록 한 행은 **Approval**과 **EvidenceSource**로, 비고에서 규칙으로 읽은 운영행위는 **Operation**으로, 별표3의 제한수위는 **Criterion**으로 만들어지고, 값이 일치하는 개체끼리 관계로 연결됨 (구축 결과: **개체 264, 관계 418**)',
]
ST3_BUL = [
    '질문에서 **의도(CQ, 복수 가능)** 와 대상(댐·시점)을 뽑고, 의도에 따라 KG와 저장소에서 근거를 찾아 **출처 번호가 붙은 근거 묶음**으로 정리함',
    '근거 묶음을 바탕으로 답변하며, **근거와 판단을 나누어** 표시함',
]
CQ_ROWS = [
    ['번호', '질문 (Competency Question)'],
    ['전체 질문', '특정 댐의 현재 수문·기상 상태와 운영기준을 확인하고, 선택된 과거 사례의 상태·운영행위·승인·근거를 함께 추적하여 운영 판단을 지원할 수 있는가?'],
    ['CQ1', '대상 댐의 현재 수문·기상 상태는 무엇인가?'],
    ['CQ2', '선택된 과거 시점 또는 사례의 수문·기상 상태는 어떠했는가?'],
    ['CQ3', '해당 과거 시점 또는 사례에서 수행된 운영행위는 무엇이었는가?'],
    ['CQ4', '해당 과거 시점 또는 사례의 방류 승인과 승인 내용은 무엇인가?'],
    ['CQ5', '현재 대상 댐에 적용되는 운영기준과 기준값은 무엇인가?'],
    ['CQ6', '위 정보를 확인할 수 있는 공식 자료 또는 근거문서는 무엇인가?'],
]
CONCL = [
    '운영 자료를 **Ontology**에 맞춰 **KG**로 구축하고, 수치·원문은 외부 저장소에 두는 방법을 정리함',
    '의도에 따라 근거를 찾아 **출처 번호가 붙은 근거 묶음**으로 정리하고, **근거와 판단을 나누어** 답하는 **프레임워크**를 구축함',
    '운영자가 현재 상태, 운영기준, 과거 승인·운영행위를 **근거와 함께** 확인할 수 있어 **실무자의 운영 의사결정 지원에 활용할 수 있음**',
    '향후 평가 질문 세트로 의도 추출과 답변의 정확도를 검증할 계획임',
]
ACK = '본 결과물은 기후에너지환경부의 재원으로 한국환경산업기술원의 기후변화 적응 수재해 관리 기술개발사업(R&D)의 지원을 받아 연구되었습니다(RS-2026-25502939). 본 연구는 기후에너지환경부「기후변화특성화대학원사업」의 지원으로 수행되었습니다.'
REFS = [
    'Noy, N. F. and McGuinness, D. L. (2001). “Ontology development 101: A guide to creating your first ontology.” Stanford Knowledge Systems Laboratory Technical Report KSL-01-05.',
    'Huang, J., Hou, W., Zhang, S., Du, Z. and Yin, J. (2026). “Dam defects ontology and knowledge graph construction from multi-source hazard data using large language models.” Advanced Engineering Informatics, Vol. 76, 104987.',
    'Zhou, Y., Bao, T., Shu, X., Li, Y. and Li, Y. (2023). “BIM and ontology-based knowledge management for dam safety monitoring.” Automation in Construction, Vol. 145, 104649.',
    'Li, S., Erickson, C., Zajac, M., Guo, X., Duan, Q. and Gong, J. (2025). “A semi-automated framework for flood ontology construction with an application in risk communication.” Water, Vol. 17, No. 19, 2801.',
    'Zhang, D., Ma, G., Qu, T., Wang, X., Zhou, W. and Wang, X. (2025). “A knowledge graph-enhanced large language model for question answering of hydraulic structure safety management.” Advanced Engineering Informatics, Vol. 66, 103468.',
    'Purohit, S., Chin, G., Mackey, P. S. and Cottam, J. A. (2024). “GraphAide: Advanced graph-assisted query and reasoning system.” Proc. IEEE Int. Conf. on Big Data (BigData), pp. 3485-3493.',
    'Lewis, P. et al. (2020). “Retrieval-augmented generation for knowledge-intensive NLP tasks.” Advances in Neural Information Processing Systems, Vol. 33, pp. 9459-9474.',
    'Angles, R. and Gutierrez, C. (2008). “Survey of graph database models.” ACM Computing Surveys, Vol. 40, No. 1, Article 1.',
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
    imgs = {'rId13': os.path.join(ASSET, 'kmu_logo.png')}
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
    GAP = 200000
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

    def native(col, y, canvas_fn, width):
        x = LX if col == 'L' else RX
        c = canvas_fn(x + (CW - width) // 2, y, width)
        shapes.append(c.xml())
        return y + c.height_emu() + 60000

    def caption(col, y, text):
        x = LX if col == 'L' else RX
        shapes.append(textbox(x, y, CW, [para(text, 2200, bullet=False, algn='ctr')], 520000))
        return y + 520000

    def bullets(col, y, items, sz=BODY):
        x = LX if col == 'L' else RX
        h = est_h(items, sz, CW)
        shapes.append(textbox(x, y, CW, [para(t, sz) for t in items], h))
        return y + h

    # 왼쪽 열: 서론 / 프레임워크 개요 / 단계 1
    y = 6350000
    y = section('L', y, '서론', INTRO) + GAP
    y = section('L', y, '프레임워크 개요', OVERVIEW_BUL)
    y = native('L', y, SH.fig_framework, 13200000)
    y = caption('L', y, '그림 1. 연구의 구성') + GAP
    y = section('L', y, '단계 1. Ontology 설계', ST1_BUL)
    y = tbl('L', y, 'Table 1. 전체 질문과 세부 질문(CQ)', [2000000, 11500000], CQ_ROWS)
    y = native('L', y, lambda x_, y_, w_: SH.fig_kg(x_, y_, w_, schema=True), 12400000)
    y = caption('L', y, '그림 2. Ontology: Class 6개, 관계 9개, Class별 Data Property')
    log['L_end'] = y

    # 오른쪽 열: 단계 2 / 단계 3 / 결론 / 감사 / 참고문헌
    y = 6350000
    y = section('R', y, '단계 2. KG 구축', ST2_BUL)
    y = native('R', y, SH.fig_steps, 11000000)
    y = caption('R', y, '그림 3. KG 구축 6단계')
    y = native('R', y, SH.fig_kg, 9600000)
    y = caption('R', y, '그림 4. 구축된 KG의 일부 (충주댐 승인 1368번)')
    y = bullets('R', y, KG_EXPL) + GAP
    y = section('R', y, '단계 3. 근거 기반 질의응답', ST3_BUL)
    y = native('R', y, SH.fig_qa, 11400000)
    y = caption('R', y, '그림 5. 질의응답의 처리 단계') + GAP
    y = section('R', y, '결론', CONCL) + GAP
    y = section('R', y, '감사의 글', None)
    h = est_h([ACK], 1600, CW, bullet=False)
    shapes.append(textbox(RX, y, CW, [para(ACK, 1600, bullet=False)], h)); y += h + 100000
    y = section('R', y, '참고문헌', None)
    h = est_h(REFS, 1400, CW, bullet=False, spc_aft=150)
    shapes.append(textbox(RX, y, CW, [para('%d. %s' % (i + 1, r), 1400, bullet=False, spc_aft=150) for i, r in enumerate(REFS)], h)); y += h
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
