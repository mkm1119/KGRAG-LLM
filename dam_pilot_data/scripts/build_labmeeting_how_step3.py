#!/usr/bin/env python3
"""랩미팅 자료(docx): 단계 3. 구조화 자료 매핑의 how 보완.
앞에는 바뀐 점과 전후 비교, 본문은 승인 표 한 행을 따라가는 구현 과정, 뒤에는 문헌 근거(D2RQ 원리) 블록.
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
    role = ['식별자 키\n(과정 1)', '관계에 사용\n(단계 5)', '라벨\n(과정 2)', '속성 하나\n(과정 3)', '세 열을 내용 속성 하나로 (과정 3)', '', '']
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


B = []
add = B.append

# ------------------------------------------------------------------ 표지
add(title('단계 3. 구조화 자료 매핑', 'how 보완'))
add(subtitle('벤치마킹한 문헌의 원리와 우리 구현 과정'))
add(dateline('2026.10.30 · 문경민'))

# ------------------------------------------------------------------ 1. 바뀐 점
add(h1('1. 이번에 바뀐 점'))
add(label('핵심'))
add(li('문헌 표기를 바로잡았다. OntoDSMS는 Zhou 외(2023)가 만든 댐 안전 모니터링 온톨로지의 이름이고, 관계형 DB를 온톨로지에 연결한 기술은 기존 오픈소스 플랫폼 D2RQ이다. 우리가 벤치마킹한 것은 D2RQ의 매핑 원리 4개이다(부록 A).'))
add(li('how를 채웠다. 승인 표의 504행 하나를 따라가며 식별자 → 클래스 → 속성 → 근거·출처 순서로, 각 과정이 무엇을 어떻게 만들고 결과물이 무엇인지 보였다(2장, 그림 1~4).'))
add(li('원리와 다르게 구현한 부분은 데이터 구조에 맞춘 응용 5가지로 정리했다(3장). 매핑을 검토하며 찾은 온톨로지의 부족한 점은 검토할 점으로 남겼다(4장).'))
add(label('표 1. 10/16 자료와 비교'))
add(table([
    ['항목', '10/16 자료', '이번'],
    ['문헌 표기', '"OntoDSMS(Zhou 2023)는 … 관계형 DB의 자료를 온톨로지에 연결한다" — OntoDSMS를 기술 이름처럼 씀',
     '논문(Zhou 외 2023) · 온톨로지(OntoDSMS) · 연결 도구(D2RQ)를 구분. 벤치마킹 대상 = D2RQ의 매핑 원리'],
    ['문헌의 방법', '표 → Class, 열 → 속성, 행 → 개체 (대응 원칙만)',
     '논문 그림 3의 매핑 구문을 근거로 원리 4개: 키 값으로 식별자, 표 → 클래스, 열 → 속성, 대응은 사람이 결정 (부록 A)'],
    ['우리 구현', 'Class별 결과 예시 표', '한 행을 따라가는 과정 5개와 과정별 결과물 (2장)'],
    ['원리와 다른 부분', '"D2RQ 도구는 쓰지 않음" 한 줄', '데이터 구조에 맞춘 응용 5가지와 그 이유 (3장)'],
    ['검토할 점', '없음', 'approvalContent에 세 열이 합쳐짐, ID 접두어 표기 (4장)'],
    ['10/19 질문', '—', '매핑이 어떻게 작동하나 → 2장 · AP와 APR → 4장 2 · 댐 기본 자료 → 2.3'],
], [1700, 3700, 4572], left_cols=(1, 2)))

# ------------------------------------------------------------------ 2. 구현
add(h1('2. 우리 구현: 승인 표 한 행이 KG 개체가 되는 과정'))
add(para('단계 3은 정형 표(승인 기록, K-water 측정자료)의 값을 해석을 더하지 않고 Ontology의 개체와 속성으로 옮기는 단계이다. '
         '아래는 승인 표의 504행 하나를 따라간다. 각 과정 제목의 "원리 n"은 부록 A의 D2RQ 원리 번호이고, 그림의 노란 점선 상자는 그 원리에 해당하는 D2RQ 구문이다.'))

add(h2('2.1 입력: 승인 표와 열의 역할'))
add(para('입력은 전처리를 마친 승인 표(approval_records_clean.csv)에서 대상 4개 댐(충주, 소양강, 횡성, 광동)의 80행이다. 한 행은 승인 한 건이다. '
         '변환하기 전에 열마다 어떤 역할을 할지 먼저 정했다(원리 4: 대응은 사람이 정한다). 표 2의 머리 색이 역할이다.'))
add(label('표 2. 승인 표(일부)와 열의 역할'))
add(role_table())
add(para('표에는 이 밖에 원본 CSV의 행 번호(row_number_in_file)와 출처 열 6개(기관, 내려받은 주소, 원본 파일명, SHA-256 등)가 있다. 이 열들은 과정 4·5의 근거 개체와 출처 기록에 쓴다.'))

add(h2('2.2 과정 1~5'))
add(lead('과정 1. 식별자 만들기 (원리 1)',
         '틀 "APR:" + {순차번호}에 504를 넣어 승인 개체 APR:504를 만들고, 같은 행에서 틀 "EVI:AP:" + {순차번호}로 근거 개체 EVI:AP:504를 만든다. '
         '순차번호를 키로 쓴 이유는 원본 자료가 승인 한 건마다 매긴 번호이고, 전처리(단계 2)에서 중복 행을 지운 뒤에는 표 안에서 유일하기 때문이다. '
         '그래서 80행은 서로 다른 ID 80쌍이 된다. ID가 값에서 결정되므로 KG를 다시 만들어도 같은 ID가 나오고, 단계 5는 이 ID로 개체를 정확히 찾아 관계를 잇는다.'))
add(fig('step3_doc_f1'))
add(caption('그림 1. 식별자 만들기 — 키 열의 값을 틀에 끼운다'))

add(lead('과정 2. 클래스 지정과 라벨 (원리 2, 원리 3의 pattern)',
         '승인 표에서 나온 APR: ID 80개는 모두 Approval 클래스의 인스턴스로, EVI:AP: ID 80개는 모두 EvidenceSource 클래스의 인스턴스로 기록한다. '
         '라벨은 틀 "승인 {순차번호} ({댐명})"으로 만든다. 승인 자료의 관측소명은 "충주"이고 K-water 자료는 "충주댐"이라, 관측소명을 표준 댐명 사전으로 바꾼 뒤 틀에 넣는다.'))
add(fig('step3_doc_f2'))
add(caption('그림 2. 클래스 지정과 라벨'))
add(para('결과물 (kgv4_entities.csv: 개체 ID, 클래스, 라벨)'))
add(code('APR:504,    Approval,       승인 504 (충주댐)\nEVI:AP:504, EvidenceSource, 한강홍수통제소 댐방류승인 순차번호 504'))

add(lead('과정 3. 열 → 속성 (원리 3)',
         '승인년월일시분 열은 approvalTime 속성에 대응한다. 원본 값에 시각이 없으므로 앞 10글자를 날짜(date)로 저장한다(column). '
         '방류시작시간, 접수방류량, 비고 세 열은 문자열 틀에 넣어 approvalContent 하나로 저장한다(pattern). 주어진 온톨로지에 Approval의 내용 속성이 approvalContent 하나뿐이어서 이렇게 모았다(4장 검토할 점 1). '
         '관측소코드는 속성으로 만들지 않고, 단계 5에서 Dam 개체를 찾아 concernsDam 관계로 잇는 데 쓴다.'))
add(fig('step3_doc_f3'))
add(caption('그림 3. 열 → 속성 — 원본 셀 값, 변환 규칙, 결과'))
add(para('결과물 (kgv4_properties.csv: 개체 ID, 속성, 값, 자료형)'))
add(code('APR:504, approvalTime,    2011-06-27, date\nAPR:504, approvalContent, ' + P504['approvalContent'] + ', string'))
add(lead('비고는 어떻게 다루나',
         '이 단계에서 비고는 표의 한 칸으로서 셀 값을 그대로 옮기기만 한다. 앞뒤 공백을 지우고, 비어 있으면 넣지 않고(80행 중 15행), 비어 있지 않으면 "비고: " 뒤에 원문을 붙인다. '
         '"(실제방류는 20시부터)"가 실제 방류 시각이라는 것을 읽어 운영행위 OPR:504:1(방류, 20:00)을 만드는 것은 단계 4(비정형 텍스트 추출)의 일이다. '
         '같은 열이 두 단계에 나오지만, 단계 3은 원문을 보존하고 단계 4는 그 원문을 해석한다. 원문이 승인 개체에 남아 있어서 단계 4의 추출 결과를 원문과 바로 대조할 수 있다.'))

add(lead('과정 4. 근거 개체 (응용 1, 3장)',
         '같은 행의 출처 열을 근거 개체 EVI:AP:504의 속성으로 옮긴다. 승인 개체와 근거 개체는 같은 행에서 함께 만들어지므로, 다른 표를 찾지 않고 바로 APR:504 —supportedBy→ EVI:AP:504로 잇는다.'))
add(code('EVI:AP:504, sourceTitle,   환경부 한강홍수통제소 홍수예보 댐방류승인\nEVI:AP:504, sourceType,    승인자료\nEVI:AP:504, sourceLocator, 순차번호 504'))
add(lead('과정 5. 출처 기록 (응용 1, 3장)',
         '개체마다 원본 파일, 원본 안의 위치, 적용한 매핑 규칙의 ID, 값의 성격을 한 줄로 남긴다. row_number_in_file은 원본 CSV의 행 번호라서 원 파일의 해당 행을 바로 열 수 있고, '
         'rule은 어떤 규칙으로 만들었는지(D2RQ에서 매핑 파일이 하던 기록), real은 원본 값을 가공 없이 옮겼다는 뜻이다.'))
add(code('개체     원본 파일                   위치                    규칙    값의 성격  메모\nAPR:504  approval_records_clean.csv  row_number_in_file=504  MR-APR  real       승인일은 날짜만 있음'))

add(lead('결과', '504행 하나에서 승인 개체와 근거 개체가 속성을 갖추고 supportedBy로 이어진다. 댐과의 관계(concernsDam)와 운영행위(OPR:504:1)는 이후 단계에서 만든다.'))
add(fig('step3_doc_f4'))
add(caption('그림 4. 504행 하나에서 만들어진 그래프 조각'))

add(h2('2.3 댐 표와 측정 표'))
add(lead('Dam (댐 기본 자료)',
         '댐 한 개가 한 행인 기본 정보 표는 따로 없고, K-water 일자료(kwater_mywater_period_daily_long.csv.gz)의 측정 행마다 댐 코드(DAM_CD)와 댐 유형이 반복해서 붙어 있다. '
         '틀 "DAM:" + {DAM_CD}로 식별자를 만들면 같은 댐의 여러 행이 같은 ID로 모이므로, 이를 하나의 Dam 인스턴스로 기록한다. 댐 유형 열은 damType 속성으로 옮기고, damName에는 표준 댐명을 넣는다. '
         '이 Dam 개체는 단계 5에서 승인(concernsDam)과 측정 상태(hasHydrometeorologicalState)가 모이는 중심이 된다.'))
add(code('DAM:1003110, Dam, 충주댐\nDAM:1003110, damName, 충주댐,   string\nDAM:1003110, damType, 다목적댐, string'))
add(lead('HydrometeorologicalState (HMS)',
         'K-water 시간자료는 한 행이 (댐 코드, 시각)이고 변수 6개(수위, 저수량, 강우량, 유입량, 총방류량, 저수율)가 열로 펼쳐진 넓은 형태이다(553,609행). '
         '행의 키(DAM_CD)와 열 머리(변수명)를 함께 틀에 넣어 HMS:1003110:수위처럼 (댐, 변수)마다 개체를 만든다(댐 4 × 변수 6 = 24개). '
         '시각별 값은 KG에 넣지 않고 측정 저장소에 두며, 질문이 오면 (댐 코드, 시각)으로 조회한다. 같은 방식으로 댐마다 측정자료 근거 개체 EVI:KW:{DAM_CD}(4개)를 만든다.'))
add(fig('step3_doc_f5'))
add(caption('그림 5. K-water 시간자료 → HMS 개체'))

add(h2('2.4 단계 3의 결과물'))
add(li('개체 %d개: Approval %d, EvidenceSource %d(승인 %d + 측정자료 %d), HMS %d, Dam %d'
       % (NE3, EC['APR'], EC['EVI:AP'] + EC['EVI:KW'], EC['EVI:AP'], EC['EVI:KW'], EC['HMS'], EC['DAM'])))
add(li('속성 %d개: 승인 %d, 근거 %d, HMS %d, 댐 %d' % (NP3, PC['APR'], PC['EVI:AP'] + PC['EVI:KW'], PC['HMS'], PC['DAM'])))
add(li('개체마다 출처 기록 1줄'))
add(para('이 단계가 끝나면 개체와 속성은 갖춰지지만, 서로 다른 표에서 나온 개체(승인과 댐 등)는 아직 연결되지 않았다. 연결은 단계 5에서 다룬다.'))

# ------------------------------------------------------------------ 3. 응용
add(h1('3. 데이터 구조에 맞춘 응용'))
add(para('원리는 그대로 두고, 우리 자료의 구조가 OntoDSMS의 DB와 달라서 구현 방식을 바꾼 부분이다.'))
add(lead('응용 1. 원본이 DB가 아니라 파일 → 값을 옮기고 출처를 기록',
         'OntoDSMS의 원본은 MySQL DB였고, D2RQ는 원본 DB를 그대로 둔 채 질의할 때마다 매핑을 거쳐 읽는다(가상 그래프). '
         '우리 원본은 공공데이터 포털과 K-water에서 내려받은 CSV·JSON 파일이라 질의를 받을 수 있는 DB가 아니다. 그래서 매핑한 값을 그래프 DB(Neo4j)로 옮겼다. '
         '값을 옮기면 KG의 값과 원본 행의 연결이 끊기므로 과정 4(근거 개체)와 과정 5(출처 기록)를 추가했다. '
         '같은 이유로 매핑 규칙은 별도 매핑 파일 대신 변환 코드에 적고, 각 개체에 규칙 ID를 남겼다. 열이 몇 개뿐이라 자동 생성 후 수정하는 단계 없이 처음부터 사람이 대응을 정했다.'))
add(lead('응용 2. 승인 시각 열에 날짜만 있음 → 날짜형으로',
         '열 이름은 승인년월일시분이지만 원본 값은 모두 날짜뿐이다. 없는 시각을 만들어 넣지 않고 값의 실제 형태대로 date로 저장했고, 이 사실을 출처 기록의 메모로 남겼다.'))
add(lead('응용 3. 댐 기본 정보 표가 없음 → 같은 키의 여러 행을 하나의 인스턴스로',
         '원리 2는 행 하나가 인스턴스 하나이지만, 우리 자료에서 댐 정보는 측정 행마다 반복될 뿐이다. 식별자가 키 값에서 결정되므로(원리 1) 같은 DAM_CD의 행들은 같은 ID로 모이고, 이를 하나의 Dam 인스턴스로 기록했다.'))
add(lead('응용 4. 넓은 형태의 측정 표, 55만 행 → (키 열, 열 머리)로 개체',
         '원리를 그대로 적용하면 시간자료의 각 행이 인스턴스가 되어 553,609개의 노드가 속성 6개씩을 갖는다. KG에 필요한 것은 "어느 댐에 어떤 측정 변수가 있는가"라는 구조이고, '
         '시각별 값은 측정 저장소에서 시각으로 찾으면 된다. 그래서 키가 들어 있는 두 곳(키 열 DAM_CD와 열 머리 변수명)을 식별자 틀에 넣었다. 원리 1을 넓은 표에 맞게 적용한 것이다.'))
add(lead('응용 5. 다른 개체를 가리키는 열 → 속성이 아니라 관계로',
         '승인 표의 관측소코드 값은 K-water의 댐 코드와 같다. 이 값을 문자열 속성으로 두지 않고 단계 5에서 Dam 개체를 찾아 concernsDam 관계로 잇는 데 썼다. '
         '그래서 "충주댐의 승인"을 문자열 비교가 아니라 관계를 따라가서 찾는다. D2RQ 규격에도 이런 열을 다른 클래스로 잇는 선언(refersToClassMap, join)이 있는 것으로 알려져 있으나, 원문은 아직 확인하지 못했다.'))

# ------------------------------------------------------------------ 4. 검토할 점
add(h1('4. 검토할 점 (온톨로지 발전 후보)'))
add(lead('1. approvalContent 하나에 세 열이 들어가 있음',
         '방류시작시간, 접수방류량, 비고를 문자열 하나로 저장하고, 접수일자 열은 어느 속성에도 들어가지 않았다. 구축 당시 주어진 온톨로지에서 Approval의 속성은 approvalTime과 approvalContent 두 개뿐이었고, '
         '온톨로지는 수정하지 않는다는 전제로 매핑했기 때문이다. 즉 데이터 구조가 아니라 온톨로지의 속성 정의가 합치게 만든 것이다. 세 열은 원본에서 이미 나뉘어 있고 형태(시각, 숫자, 문장)도 분명하므로, '
         '원리 3대로라면 속성도 따로여야 한다. 합친 결과 "접수방류량 2000㎥/s 이상인 승인", "승인일과 방류 시작의 시간 차" 같은 조건 질의를 할 수 없다.'))
add(li('선택지 ① Approval 속성 추가: dischargeStartTime(datetime), requestedDischarge(decimal, ㎥/s), remark(string), 필요하면 receiptDate(date). 추가하면 KG 재생성, 검증, Cypher 내보내기를 다시 한다.'))
add(li('선택지 ② 현재대로 두고, 승인 내용은 답변에 원문으로 보여 주는 용도로만 쓴다.'))
add(li('판단 기준: 지금의 CQ4(과거 방류 승인)는 댐과 기간으로 승인을 찾아 내용을 그대로 돌려주므로 분리가 꼭 필요하지 않다. 방류량이나 시각을 조건으로 쓰는 질의를 CQ에 넣을 때 함께 정한다.'))
add(lead('2. ID 접두어 표기 (10/19 질문: AP와 APR)',
         'APR:504와 EVI:AP:504는 같은 행에서 나온 서로 다른 클래스의 개체(승인, 근거)이다. 접두어는 클래스를, 숫자는 같은 원본 행을 나타낸다. '
         '두 개체의 연결은 문자열을 비교해 찾는 것이 아니라, 같은 행을 처리할 때 두 ID를 함께 만들면서 supportedBy 관계로 바로 잇는다(과정 4). 그래서 연결은 된다. '
         '다만 EVI 안의 AP는 출처 종류(승인자료)를 뜻하는데 클래스 접두어 APR과 비슷해 헷갈린다는 지적은 유효하다. '
         '출처 종류 표기를 클래스 접두어와 맞추는 것(EVI:APR:504)과, 현행을 유지하고 ID 규칙을 문서로 정리하는 것 중에서 정한다.'))

# ------------------------------------------------------------------ 부록 A
add(h1('부록 A. 문헌 근거: 벤치마킹한 D2RQ의 매핑 원리'))
add(label('[변경] 10/16 자료 2.5절 "문헌의 방법"을 대체'))
add(lead('표기',
         'Zhou, Z. 외 (2023). BIM and ontology-based knowledge management for dam safety monitoring. Automation in Construction, 145, 104649. '
         'OntoDSMS는 이 논문이 구축한 댐 안전 모니터링 시스템(DSMS) 도메인 온톨로지의 이름이다. D2RQ는 이 논문이 만든 것이 아니라 기존 오픈소스 플랫폼이며, '
         '논문은 MySQL에 저장된 모니터링 데이터를 OntoDSMS에 연결할 때 D2RQ를 사용했다(4장, 그림 3). 본 연구가 벤치마킹한 것은 D2RQ의 매핑 원리이다.'))
add(para('논문 4장에 따르면 D2RQ는 "표는 클래스, 열은 속성(DatatypeProperty), 행은 인스턴스, 셀은 값"이라는 대응을 매핑 파일(Turtle 문법)의 선언으로 구현한다. '
         '아래는 논문 그림 3(수정된 매핑 파일 일부)의 구문이다.'))
add(code('map:item a d2rq:ClassMap;\n    d2rq:uriPattern "item/@@item.item_ID@@";\n    d2rq:class :Item.\n\n'
         'map:item__label a d2rq:PropertyBridge;\n    d2rq:belongsToClassMap map:item;\n    d2rq:property rdfs:label;\n    d2rq:pattern "item #@@item.item_ID@@".\n\n'
         'map:item_Genre a d2rq:PropertyBridge;\n    d2rq:belongsToClassMap map:item;\n    d2rq:property :itemName;\n    d2rq:column "item.Genre".'))
add(lead('원리 1. 행의 키 값으로 개체 식별자를 만든다',
         'ClassMap의 uriPattern은 @@ 사이에 적힌 열(item 표의 item_ID)의 값을 행마다 끼워 넣는 틀이다. item_ID가 7인 행은 item/7이라는 식별자를 갖는다. '
         '식별자가 키 값에서 결정되므로 같은 행은 언제나 같은 식별자를 받고, 다른 매핑이나 질의가 이 식별자로 개체를 다시 가리킬 수 있다.'))
add(lead('원리 2. 한 표에서 나온 식별자는 모두 같은 클래스의 인스턴스가 된다',
         '같은 ClassMap의 d2rq:class :Item은 위 틀로 만든 모든 식별자를 Item 클래스의 인스턴스로 선언한다. 논문은 이를 "Converting a table in a database to a class in an ontology"라고 설명한다.'))
add(lead('원리 3. 열 하나를 속성 하나에 대응시키고, 셀 값을 속성값으로 옮긴다',
         'PropertyBridge는 값을 어느 개체에 붙일지(belongsToClassMap), 온톨로지의 어떤 속성인지(property), 어느 열의 셀 값을 옮길지(column)를 선언한다. '
         '논문은 이를 "Converting a column in a table to a DatatypeProperty in an ontology"라고 설명한다. 고정 문자열과 열 값을 조합할 때는 pattern을 쓴다(그림 3의 rdfs:label).'))
add(lead('원리 4. 열과 속성의 대응은 사람이 온톨로지 용어로 정한다',
         '매핑 파일은 DB 구조로부터 자동 생성되며, 이때 이름은 DB의 표·열 이름 그대로이다. 이를 사람이 온톨로지 용어에 맞게 수정한다. '
         '그림 3에서 Genre 열이 :itemName 속성에 대응된 것이 그 결과이다.'))
add(para('본 연구가 따르지 않은 부분: D2RQ는 데이터를 복사하지 않는 가상 RDF 그래프로 동작하며, RDF 질의(SPARQL)를 SQL로 번역해 원본 DB에서 실행한다. '
         '우리 원본은 DB가 아니므로 이 방식 대신 값을 옮기고 출처를 기록했다(3장 응용 1).'))

T.save(OUT, ''.join(B), L.IMGS)
print('saved', OUT)
