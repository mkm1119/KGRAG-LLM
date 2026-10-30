#!/usr/bin/env python3
"""랩미팅 자료(docx): 단계 3. 구조화 자료 매핑의 how 보완.
앞에는 바뀐 점과 전후 비교, 이어서 벤치마킹한 문헌의 원리, 본문은 승인 표 한 행을 따라가는 구현 과정과 결과물, 뒤에는 검토할 점과 문헌 표기.
그림은 lab_meeting/how/fig/step3_doc_f*.png (원본 step3_doc_figs.html).
사용: python3 scripts/build_labmeeting_how_step3.py <출력 docx>
"""
import collections, csv, importlib.util, os, struct, sys
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('L', os.path.join(HERE, 'labdoc_lib.py')); L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
for n in ('run', 'title', 'subtitle', 'dateline', 'label', 'h1', 'h2', 'para', 'li', 'lead', 'spacer', 'table', 'code', 'caption'):
    globals()[n] = getattr(L, n)

ROOT = os.path.join(HERE, '..'); N = os.path.join(ROOT, '03_normalized')
LAB = os.path.join(ROOT, '..', 'lab_meeting')
FIG = os.path.join(LAB, 'how', 'fig')
OUT = sys.argv[1]
T = L.Template(os.path.join(LAB, '랩미팅 자료_KG구축_검색답변_최종.docx'))
rd = lambda p: list(csv.DictReader(open(os.path.join(N, p), encoding='utf-8-sig')))

# ------------------------------------------------------------------ 사실 (현재 파일에서)
ents, props, prov = rd('kgv4_entities.csv'), rd('kgv4_properties.csv'), rd('kgv4_provenance.csv')
grp = lambda i: ':'.join(i.split(':')[:2]) if i.startswith('EVI') else i.split(':')[0]
EC = collections.Counter(grp(e['entity_id']) for e in ents)
PC = collections.Counter(grp(p['entity_id']) for p in props)
S3 = ('APR', 'EVI:AP', 'EVI:KW', 'HMS', 'DAM')
NE3, NP3 = sum(EC[k] for k in S3), sum(PC[k] for k in S3)
assert (EC['APR'], EC['EVI:AP'], EC['HMS'], EC['DAM'], EC['EVI:KW']) == (80, 80, 24, 4, 4), EC
assert (NE3, NP3) == (192, 468), (NE3, NP3)
P504 = {p['property']: p['value'] for p in props if p['entity_id'] == 'APR:504'}
assert P504['approvalTime'] == '2011-06-27' and '실제방류는 20시부터' in P504['approvalContent']


def fig(name):
    pth = os.path.join(FIG, name + '.png')
    with open(pth, 'rb') as f:
        w, h = struct.unpack('>II', f.read(24)[16:24])
    return L.image(name, pth, w, h, name, width=int(L.W * 0.97))


def role_table():
    """표 2: 승인 표의 열과 역할(머리 색 = 역할)."""
    cols = [('순차번호', 'E07A2F'), ('관측소코드', '2F66D0'), ('관측소명', '23907F'), ('승인년월일시분', '3F8F2A'),
            ('방류시작시간', '8A55C2'), ('접수방류량', '8A55C2'), ('비고', '8A55C2')]
    ws = [1100, 1250, 1000, 1500, 1800, 1100, 2222]
    assert sum(ws) == L.W
    rows = [['473', '1006110', '횡성', '2011-06-24', '2011-06-24 18:00', '100', '수문방류 승인'],
            ['504', '1003110', '충주', '2011-06-27', '2011-06-27 18:00', '2000', '(실제방류는 20시부터)'],
            ['574', '1003110', '충주', '2011-07-01', '2011-07-01 18:00', '2000', '(실제 방류는 19시부터)']]
    role = ['식별자 키\n(과정 1)', '관계에 사용\n(단계 5)', '표시 이름\n(과정 2)', '속성 하나\n(과정 3)', '세 열을 내용 속성 하나로 (과정 3)', '', '']
    out = ['<w:tbl><w:tblPr><w:tblW w:w="%d" w:type="dxa"/><w:jc w:val="center"/><w:tblBorders>%s</w:tblBorders><w:tblLayout w:type="fixed"/></w:tblPr><w:tblGrid>%s</w:tblGrid>'
           % (L.W, L.BORD, ''.join('<w:gridCol w:w="%d"/>' % w for w in ws))]
    out.append('<w:tr><w:trPr><w:cantSplit/></w:trPr>' + ''.join(L.cell(c, w, fill=f, b=True, color='FFFFFF', center=True) for (c, f), w in zip(cols, ws)) + '</w:tr>')
    for r in rows:
        hl = r[0] == '504'
        out.append('<w:tr><w:trPr><w:cantSplit/></w:trPr>' + ''.join(L.cell(c, w, fill='FFF1C9' if hl else None, b=hl, center=True) for c, w in zip(r, ws)) + '</w:tr>')
    # 역할 행: 방류시작시간~비고 세 칸은 하나로 합침
    tc = ''.join(L.cell(c, w, fill='F2F2F2', center=True, sz=17) for c, w in zip(role[:4], ws[:4]))
    merged = L.cell(role[4], sum(ws[4:]), fill='F2F2F2', center=True, sz=17).replace('<w:tcPr>', '<w:tcPr><w:gridSpan w:val="3"/>', 1)
    out.append('<w:tr><w:trPr><w:cantSplit/></w:trPr>' + tc + merged + '</w:tr>')
    out.append('</w:tbl>')
    return ''.join(out) + spacer()


def rtable(rows, widths):
    """결과 파일 발췌: 머리글 = 파일의 열 이름(우리말)."""
    return table(rows, widths, header=True, firstcol=False)


B = []
add = B.append

# ------------------------------------------------------------------ 표지
add(title('단계 3. 구조화 자료 매핑', 'how 보완'))
add(subtitle('벤치마킹한 문헌의 원리와 우리 구현 과정'))
add(dateline('2026.10.30 · 문경민'))

# ------------------------------------------------------------------ 1. 바뀐 점
add(h1('1. 이번에 바뀐 점'))
add(label('핵심'))
add(li('문헌 표기를 바로잡았다. OntoDSMS는 Zhou 외(2023)가 만든 댐 안전 모니터링 온톨로지의 이름이고, 관계형 DB를 온톨로지에 연결한 기술은 기존 오픈소스 플랫폼 D2RQ이다. 우리가 벤치마킹한 것은 D2RQ의 매핑 원리 4개이다(2장).'))
add(li('how를 채웠다. 승인 표의 504행 하나를 따라가며 식별자 → Class → 속성 → 근거·출처 순서로, 각 과정이 무엇을 어떻게 만들고 결과물이 무엇인지 보였다(3장).'))
add(li('결과물을 보이게 했다. 결과 파일 3개의 한 줄이 무엇이고 Neo4j 노드의 어디가 되는지(그림 6), 단계 3이 끝났을 때 충주댐의 Entity가 어떤 상태인지(그림 7) 그렸다.'))
add(li('매핑을 검토하며 찾은 온톨로지의 부족한 점과 10/19 질문(AP와 APR)은 검토할 점으로 정리했다(4장).'))
add(label('표 1. 10/16 자료와 비교'))
add(table([
    ['항목', '10/16 자료', '이번'],
    ['문헌 표기', '"OntoDSMS(Zhou 2023)는 … 관계형 DB의 자료를 온톨로지에 연결한다" — OntoDSMS를 기술 이름처럼 씀',
     '논문(Zhou 외 2023) · 온톨로지(OntoDSMS) · 연결 도구(D2RQ)를 구분. 벤치마킹 대상 = D2RQ의 매핑 원리'],
    ['문헌의 방법', '표 → Class, 열 → 속성, 행 → 개체 (대응 원칙만)',
     '논문 그림 3의 매핑 구문을 근거로 원리 4개: 키 값으로 식별자, 표 → Class, 열 → 속성, 대응은 사람이 결정 (2장)'],
    ['우리 구현', 'Class별 결과 예시 표', '한 행을 따라가는 과정 5개와 과정별 결과물 (3장)'],
    ['결과물', '예시 값만', '결과 파일 3개와 Neo4j 노드의 대응(그림 6), 단계 3이 끝난 상태(그림 7)'],
    ['검토할 점', '없음', 'approvalContent에 세 열이 합쳐짐, ID 접두어 표기 (4장)'],
    ['10/19 질문', '—', '매핑이 어떻게 작동하나 → 3장 · 댐 기본 자료 → 3.3 · AP와 APR → 4장 2'],
], [1700, 3700, 4572]))

# ------------------------------------------------------------------ 2. 문헌의 원리
add(h1('2. 벤치마킹한 문헌의 원리: D2RQ 매핑'))
add(lead('표기',
         'Zhou 외(2023)는 댐 안전 모니터링을 위한 BIM·온톨로지 기반 지식관리를 다룬 논문이고, OntoDSMS는 이 논문이 구축한 댐 안전 모니터링 시스템(DSMS) 도메인 온톨로지의 이름이다. '
         'D2RQ는 이 논문이 만든 것이 아니라 기존 오픈소스 플랫폼이며, 논문은 MySQL에 저장된 모니터링 데이터를 OntoDSMS에 연결할 때 D2RQ를 사용했다(4장, 그림 3). 본 연구가 벤치마킹한 것은 D2RQ의 매핑 원리이다.'))
add(lead('용어 대응', '문헌의 instance는 우리 용어로 Entity, 문헌의 DatatypeProperty는 우리의 Data Property이다(10/16 자료 1.1 용어 정리). 이하 우리 용어로 쓴다.'))
add(para('D2RQ는 "표는 Class, 열은 Data Property, 행은 Entity, 셀은 값"이라는 대응을 매핑 파일(Turtle 문법)에 선언한다. 아래는 논문 그림 3(수정된 매핑 파일 일부)의 구문이다.'))
add(code('map:item a d2rq:ClassMap;\n    d2rq:uriPattern "item/@@item.item_ID@@";\n    d2rq:class :Item.\n\n'
         'map:item_Genre a d2rq:PropertyBridge;\n    d2rq:belongsToClassMap map:item;\n    d2rq:property :itemName;\n    d2rq:column "item.Genre".'))
add(lead('원리 1. 행의 키 값으로 Entity의 식별자를 만든다 → 과정 1',
         'ClassMap의 uriPattern은 @@ 사이에 적힌 열(item 표의 item_ID)의 값을 행마다 끼워 넣는 틀이다. item_ID가 7인 행은 item/7이라는 식별자를 갖는다. '
         '식별자가 키 값에서 결정되므로 같은 행은 언제나 같은 식별자를 받고, 다른 매핑이나 질의가 이 식별자로 그 Entity를 다시 가리킬 수 있다.'))
add(lead('원리 2. 한 표에서 나온 식별자는 모두 같은 Class의 Entity가 된다 → 과정 2',
         '같은 ClassMap의 d2rq:class :Item은 위 틀로 만든 모든 식별자를 Item Class의 Entity로 선언한다. 논문은 이를 "Converting a table in a database to a class in an ontology"라고 설명한다.'))
add(lead('원리 3. 열 하나를 Data Property 하나에 대응시키고, 셀 값을 그 값으로 옮긴다 → 과정 3',
         'PropertyBridge는 값을 어느 Entity에 붙일지(belongsToClassMap), 온톨로지의 어떤 속성인지(property), 어느 열의 셀 값을 옮길지(column)를 선언한다. '
         '논문은 이를 "Converting a column in a table to a DatatypeProperty in an ontology"라고 설명한다. 고정 문자열과 열 값을 조합해야 할 때는 column 대신 pattern을 쓴다.'))
add(lead('원리 4. 열과 속성의 대응은 사람이 온톨로지 용어로 정한다 → 3.1',
         '매핑 파일은 DB 구조로부터 자동 생성되며, 이때 이름은 DB의 표·열 이름 그대로이다. 이를 사람이 온톨로지 용어에 맞게 수정한다. 그림 3에서 Genre 열이 :itemName 속성에 대응된 것이 그 결과이다.'))

# ------------------------------------------------------------------ 3. 구현
add(h1('3. 우리 구현: 승인 표 한 행이 KG의 Entity가 되는 과정'))
add(para('단계 3은 정형 표(승인 기록, K-water 측정자료)의 값을 해석을 더하지 않고 Ontology의 Entity와 Data Property로 옮기는 단계이다. '
         '아래는 승인 표의 504행 하나를 따라간다. 그림의 노란 점선 상자는 해당 과정에 쓰인 D2RQ 원리(2장)이다.'))

add(h2('3.1 입력: 승인 표와 열의 역할 (원리 4)'))
add(para('입력은 전처리를 마친 승인 표(approval_records_clean.csv)에서 대상 4개 댐(충주, 소양강, 횡성, 광동)의 80행이다. 한 행은 승인 한 건이다. '
         '변환하기 전에 열마다 어떤 역할을 할지 사람이 먼저 정했다. 표 2의 머리 색이 역할이다.'))
add(label('표 2. 승인 표(일부)와 열의 역할'))
add(role_table())
add(para('표에는 이 밖에 원본 CSV의 행 번호(row_number_in_file)와 출처 열 6개(기관, 내려받은 주소, 원본 파일명, SHA-256 등)가 있으며, 과정 4·5에 쓴다.'))

add(h2('3.2 과정 1~5'))
add(lead('과정 1. 식별자 만들기 (원리 1)',
         '틀 "APR:" + {순차번호}에 504를 넣어 승인 Entity APR:504를 만들고, 같은 행에서 틀 "EVI:AP:" + {순차번호}로 그 승인이 적힌 자료의 Entity EVI:AP:504를 만든다. '
         '순차번호를 키로 쓴 이유는 원본 자료가 승인 한 건마다 매긴 번호이고, 전처리(단계 2)에서 중복 행을 지운 뒤에는 표 안에서 유일하기 때문이다. '
         '그래서 80행은 서로 다른 ID 80쌍이 된다. ID가 값에서 결정되므로 KG를 다시 만들어도 같은 ID가 나오고, 단계 5는 이 ID로 Entity를 정확히 찾아 관계를 잇는다.'))
add(fig('step3_doc_f1'))
add(caption('그림 1. 식별자 만들기 — 키 열의 값을 틀에 끼운다'))

add(lead('과정 2. Class 지정 (원리 2)',
         '승인 표에서 나온 APR: ID 80개는 모두 Approval Class의 Entity로, EVI:AP: ID 80개는 모두 EvidenceSource Class의 Entity로 기록한다. '
         '각 Entity에는 그래프를 사람이 볼 때 알아보기 쉽도록 표시 이름("승인 504 (충주댐)")을 붙인다. 표시 이름은 온톨로지의 Data Property가 아니며 검색과 답변에는 쓰지 않는다.'))
add(fig('step3_doc_f2'))
add(caption('그림 2. Class 지정과 표시 이름'))
add(para('결과물: Entity 표(kgv4_entities.csv). 한 줄이 Entity 하나이다.'))
add(rtable([['Entity ID', 'Class', '표시 이름'],
            ['APR:504', 'Approval', '승인 504 (충주댐)'],
            ['EVI:AP:504', 'EvidenceSource', '한강홍수통제소 댐방류승인 순차번호 504']], [2200, 2600, 5172]))

add(lead('과정 3. 열 → Data Property (원리 3)',
         '승인년월일시분 열은 approvalTime에 대응한다. 원본 값에 시각이 없어 앞 10글자를 날짜(date)로 저장한다(column). '
         '방류시작시간, 접수방류량, 비고 세 열은 문자열 틀에 넣어 approvalContent 하나로 저장한다(pattern). 주어진 온톨로지에 Approval의 내용 속성이 approvalContent 하나뿐이어서 이렇게 모았다(4장 검토할 점 1). '
         '관측소코드는 다른 Entity(댐)를 가리키는 열이므로 Data Property로 만들지 않고, 단계 5에서 Dam Entity를 찾아 concernsDam 관계로 잇는 데 쓴다.'))
add(fig('step3_doc_f3'))
add(caption('그림 3. 열 → Data Property — 원본 셀 값, 변환 규칙, 결과'))
add(para('결과물: 속성 표(kgv4_properties.csv). 한 줄이 Entity의 속성 하나이다.'))
add(rtable([['Entity ID', '속성', '값', '자료형'],
            ['APR:504', 'approvalTime', '2011-06-27', 'date'],
            ['APR:504', 'approvalContent', P504['approvalContent'], 'string']], [1500, 2000, 5272, 1200]))
add(lead('비고는 어떻게 다루나',
         '이 단계에서 비고는 표의 한 칸으로서 셀 값을 그대로 옮기기만 한다. 앞뒤 공백을 지우고, 비어 있으면 넣지 않고(80행 중 15행), 비어 있지 않으면 "비고: " 뒤에 원문을 붙인다. '
         '"(실제방류는 20시부터)"가 실제 방류 시각이라는 것을 읽어 운영행위 OPR:504:1(방류, 20:00)을 만드는 것은 단계 4(비정형 텍스트 추출)의 일이다. '
         '단계 3은 원문을 보존하고 단계 4는 그 원문을 해석한다. 원문이 승인 Entity에 남아 있어서 단계 4의 추출 결과를 원문과 바로 대조할 수 있다.'))

add(lead('과정 4. 근거 Entity의 속성',
         '같은 행의 출처 열을 근거 Entity EVI:AP:504의 속성으로 옮긴다. 승인 Entity와 근거 Entity는 같은 행에서 함께 만들어지므로, 다른 표를 찾지 않고 바로 APR:504 —supportedBy→ EVI:AP:504로 잇는다.'))
add(rtable([['Entity ID', '속성', '값', '자료형'],
            ['EVI:AP:504', 'sourceTitle', '환경부 한강홍수통제소 홍수예보 댐방류승인', 'string'],
            ['EVI:AP:504', 'sourceType', '승인자료', 'string'],
            ['EVI:AP:504', 'sourceLocator', '순차번호 504', 'string']], [1700, 2000, 5072, 1200]))

add(lead('과정 5. 출처 기록',
         '우리 원본은 DB가 아니라 내려받은 CSV·JSON 파일이어서, 매핑한 값을 그래프 DB(Neo4j)로 옮겨 저장한다. 값을 옮기면 KG의 값과 원본 행의 연결이 끊기므로, Entity마다 원본 파일과 그 안의 위치, 적용한 규칙의 ID, 값의 성격을 출처 표에 남긴다. '
         'row_number_in_file은 원본 CSV의 행 번호라서 원 파일의 해당 행을 바로 열 수 있고, real은 원본 값을 가공 없이 옮겼다는 뜻이다. 출처 표는 그래프에 넣지 않고 파일로 둔다.'))
add(rtable([['Entity ID', '원본 파일', '위치', '규칙', '값의 성격', '메모'],
            ['APR:504', 'approval_records_clean.csv', 'row_number_in_file=504', 'MR-APR', 'real', '승인일은 날짜만 있음']],
           [1300, 2700, 2300, 1100, 1100, 1472]))

add(lead('결과: 파일 3개와 노드 하나',
         '과정 1~5의 결과물은 파일 3개(Entity 표, 속성 표, 출처 표)이다. 이 중 Entity 표와 속성 표의 줄들이 단계 7에서 Neo4j 노드 하나로 합쳐진다. '
         'Entity 표의 한 줄이 노드와 그 Class를, 속성 표의 줄들이 노드의 속성을 이룬다. 출처 표는 노드의 ID로 원본 행을 찾는 색인으로 남는다.'))
add(fig('step3_doc_f6'))
add(caption('그림 6. 결과 파일 3개의 한 줄과 Neo4j 노드의 대응 (APR:504)'))
add(fig('step3_doc_f4'))
add(caption('그림 4. 504행 하나에서 만들어진 그래프 조각 (실선 = 단계 3, 점선 = 이후 단계)'))

add(h2('3.3 댐 표와 측정 표'))
add(lead('Dam (댐 기본 자료)',
         '댐 한 개가 한 행인 기본 정보 표는 따로 없고, K-water 일자료(kwater_mywater_period_daily_long.csv.gz)의 측정 행마다 댐 코드(DAM_CD)와 댐 유형이 반복해서 붙어 있다. '
         '틀 "DAM:" + {DAM_CD}로 식별자를 만들면 같은 댐의 여러 행이 같은 ID로 모이므로, 이를 하나의 Dam Entity로 기록한다. 댐 유형 열은 damType으로 옮기고, damName에는 표준 댐명을 넣는다. '
         '이 Dam Entity가 단계 5에서 승인(concernsDam)과 측정 상태(hasHydrometeorologicalState)가 모이는 중심이 된다.'))
add(rtable([['Entity ID', '속성', '값', '자료형'],
            ['DAM:1003110', 'damName', '충주댐', 'string'],
            ['DAM:1003110', 'damType', '다목적댐', 'string']], [1900, 2000, 4872, 1200]))
add(lead('HydrometeorologicalState (HMS)',
         'K-water 시간자료는 한 행이 (댐 코드, 시각)이고 변수 6개(수위, 저수량, 강우량, 유입량, 총방류량, 저수율)가 열로 펼쳐진 넓은 형태이며 553,609행이다. '
         '행마다 Entity를 만들면 55만 개가 되지만, KG에 필요한 것은 "어느 댐에 어떤 측정 변수가 있는가"이다. 그래서 키가 들어 있는 두 곳, 즉 키 열(DAM_CD)과 열 머리(변수명)를 틀에 넣어 '
         'HMS:1003110:수위처럼 (댐, 변수)마다 Entity를 만든다(댐 4 × 변수 6 = 24개). 시각별 값은 KG에 넣지 않고 측정 저장소에 두며, 질문이 오면 (댐 코드, 시각)으로 조회한다. '
         '같은 자료에서 댐마다 측정자료 근거 Entity EVI:KW:{DAM_CD}를 만들고 HMS와 supportedBy로 잇는다.'))
add(fig('step3_doc_f5'))
add(caption('그림 5. K-water 시간자료 → HMS Entity'))

add(h2('3.4 단계 3이 끝난 상태'))
add(para('그림 7은 단계 3이 끝났을 때 충주댐에 관련된 Entity를 만든 자료별로 모은 것이다. Entity와 속성은 갖춰졌고, 같은 행·같은 자료에서 함께 만든 근거만 supportedBy로 이어져 있다. '
         '승인과 댐, 댐과 측정 상태처럼 서로 다른 자료에서 나온 Entity는 아직 이어지지 않았으며, 이것을 단계 5에서 잇는다.'))
add(fig('step3_doc_f7'))
add(caption('그림 7. 단계 3이 끝난 상태 — 충주댐의 Entity'))
add(para('4개 댐 전체로는 Approval %d, EvidenceSource %d(승인자료 %d, 측정자료 %d), HMS %d, Dam %d로 Entity %d개, 속성 %d개이다.'
         % (EC['APR'], EC['EVI:AP'] + EC['EVI:KW'], EC['EVI:AP'], EC['EVI:KW'], EC['HMS'], EC['DAM'], NE3, NP3)))

# ------------------------------------------------------------------ 4. 검토할 점
add(h1('4. 검토할 점 (온톨로지 발전 후보)'))
add(lead('1. approvalContent 하나에 세 열이 들어가 있음',
         '방류시작시간, 접수방류량, 비고를 문자열 하나로 저장하고, 접수일자 열은 어느 속성에도 들어가지 않았다. 구축 당시 주어진 온톨로지에서 Approval의 Data Property는 approvalTime과 approvalContent 두 개뿐이었고, '
         '온톨로지는 수정하지 않는다는 전제로 매핑했기 때문이다. 세 열은 원본에서 이미 나뉘어 있고 형태(시각, 숫자, 문장)도 분명하므로 원리 3대로라면 속성도 따로여야 한다. '
         '합친 결과 "접수방류량 2000㎥/s 이상인 승인", "승인일과 방류 시작의 시간 차" 같은 조건 질의를 할 수 없다.'))
add(li('선택지 ① Approval에 Data Property 추가: dischargeStartTime(datetime), requestedDischarge(decimal, ㎥/s), remark(string), 필요하면 receiptDate(date).'))
add(li('선택지 ② 현재대로 두고, 승인 내용은 답변에 원문으로 보여 주는 용도로만 쓴다.'))
add(li('판단 기준: 지금의 CQ4(과거 방류 승인)는 댐과 기간으로 승인을 찾아 내용을 그대로 돌려주므로 분리가 꼭 필요하지 않다. 방류량이나 시각을 조건으로 쓰는 질의를 CQ에 넣을 때 함께 정한다.'))
add(lead('2. ID 접두어 표기 (10/19 질문: AP와 APR이 같은 것 아닌가, 달라서 연결이 안 되지 않나)',
         '504행 하나에서 Entity가 두 개 만들어진다. 승인 자체(APR:504)와 그 승인이 적힌 자료(EVI:AP:504)이다. ID 앞부분은 무엇의 Entity인지를, 뒤의 숫자는 둘 다 원본 504행에서 왔다는 것을 나타낸다. '
         'EVI 뒤의 AP는 근거 자료의 출처 종류(승인자료)이며, 측정자료는 KW, 규정은 LAW이다. '
         '두 Entity의 연결은 ID의 글자를 맞춰 보는 방식이 아니라 관계 선으로 된다. 504행을 처리할 때 두 Entity를 함께 만들면서 supportedBy 선을 바로 긋고, "504 승인의 근거"는 이 선을 따라가서 찾는다(그림 8). '
         '다만 사람이 볼 때 AP와 APR이 비슷해 헷갈리므로, 출처 종류 표기를 Class 접두어와 맞출지(EVI:APR:504) 정한다.'))
add(fig('step3_doc_f8'))
add(caption('그림 8. ID 접두어의 뜻과 연결 방식'))

# ------------------------------------------------------------------ 부록
add(h1('부록. 문헌 표기와 따르지 않은 부분'))
add(lead('문헌', 'Zhou, Z. 외 (2023). BIM and ontology-based knowledge management for dam safety monitoring. Automation in Construction, 145, 104649.'))
add(lead('그림 3의 표시 이름 구문',
         '그림 3에는 2장의 구문 외에 Entity의 표시 이름을 만드는 선언도 있다: map:item__label a d2rq:PropertyBridge; d2rq:belongsToClassMap map:item; d2rq:property rdfs:label; d2rq:pattern "item #@@item.item_ID@@". '
         '고정 문자열("item #")과 키 열의 값을 조합하는 pattern의 예이다.'))
add(lead('따르지 않은 부분',
         'D2RQ는 데이터를 복사하지 않는 가상 RDF 그래프로 동작하며, RDF 질의(SPARQL)를 SQL로 번역해 원본 DB에서 실행한다. '
         '우리 원본은 DB가 아니라 파일이므로 이 방식 대신 값을 그래프 DB로 옮기고 출처를 기록했다(과정 5). 같은 이유로 매핑 규칙은 별도 매핑 파일 대신 변환 코드에 두고, Entity마다 규칙 ID를 남겼다.'))

T.save(OUT, ''.join(B), L.IMGS)
print('saved', OUT)
