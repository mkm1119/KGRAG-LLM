#!/usr/bin/env python3
"""랩미팅 자료(docx): KG 구축 단계 1~3(소스 구분, 전처리, 구조화 자료 매핑)의 how 보완.
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
    role = ['식별자 키\n(과정 1)', '옮기지 않음\n(댐 코드와 같은 값)', '옮기지 않음\n(코드와 같은 정보)', '속성 하나\n(과정 3)', '세 열을 내용 속성 하나로 (과정 3)', '', '']
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
    """결과 표 발췌: 머리글 = 표의 열 이름(우리말)."""
    return table(rows, widths, header=True, firstcol=False)


def lis(*items):
    for t in items:
        add(li(t))


B = []
add = B.append

# ------------------------------------------------------------------ 표지
add(title('KG 구축 how 보완', '단계 1~4: 자료 준비 · 구조화 자료 매핑 · 비정형 텍스트 추출'))
add(subtitle('벤치마킹한 문헌의 원리와 우리 구현 과정'))
add(dateline('2026.10.30 · 문경민'))

# ------------------------------------------------------------------ 1. 바뀐 점
add(h1('1. 이번에 바뀐 점'))
add(label('핵심'))
lis('자료 준비(단계 1 소스 구분, 단계 2 전처리)를 한 장으로 묶었다. 소스 구분은 DDKG가 자료를 정형 표와 비정형 텍스트로 나누어 서로 다른 Class를 채운 원리를 따랐다(그림 1). 전처리는 문헌을 따른 것이 아니라 자료 준비이며, 실제 자료의 행으로 무엇이 지워지고 바뀌는지 보였다(그림 2~4).',
    '10/16 자료는 전처리의 근거를 DDKG 전처리로 적었으나, 우리 전처리는 DDKG의 기술(형식 변환, OCR, 정규식 구간 추출)을 쓰지 않았으므로 바로잡았다.',
    '단계 3(구조화 자료 매핑): 문헌 표기를 바로잡았다(OntoDSMS = Zhou 외 2023이 만든 온톨로지, D2RQ = 그 논문이 사용한 기존 도구). D2RQ의 매핑 원리 4개를 따라 승인 표의 504행 하나가 Entity가 되는 과정과 결과물(CSV 파일 3개)을 보였다(그림 5~12).',
    '단계 4(비정형 텍스트 추출): DDKG의 규칙 기반 추출 원리(정해진 문형은 정규식으로 바로 뽑는다)를 따라, 비고에서 운영행위를, 별표3에서 홍수기 제한수위를 뽑는 과정을 실제 행으로 보였다(그림 13~14). 운영행위 시각은 측정값 보정을 없애고 비고의 시각 또는 방류시작시간으로 바꾸었다.',
    '검토할 점: 매핑을 검토하며 찾은 온톨로지의 부족한 점, 10/19 질문(AP와 APR), 전처리에서 남은 확인 사항, 추출 규칙의 한계를 모았다.',
    '다음 주: 단계 5(개체 해소·연결)까지 이번 주에 채우고, 단계 6 검증, 단계 7 저장, 검색·답변은 다음 주에 다룬다(6장).')
add(label('표 1. 10/16 자료와 비교'))
add(table([
    ['항목', '10/16 자료', '이번'],
    ['단계 1 근거', 'DDKG 3.2.1: 표와 글을 나누어 처리', 'DDKG의 지식 출처 구분(정형 표 → c1~c4, 비정형 텍스트 → c5~c7)을 원리로 밝히고, 우리 자료 → Class 대응을 그림으로'],
    ['단계 2 근거', 'DDKG 3.2.1 전처리, Zhang(2025)', '문헌 근거 없음(자료 준비)'],
    ['단계 2 설명', '처리와 결과를 표로', '실제 자료의 행으로 지우는 행, 바뀌는 시각, 꺼내는 부분을 보임'],
    ['단계 3 문헌 표기', '"OntoDSMS(Zhou 2023)는 … 연결한다" — OntoDSMS를 기술 이름처럼 씀', '논문(Zhou 외 2023) · 온톨로지(OntoDSMS) · 연결 도구(D2RQ)를 구분. 벤치마킹 대상 = D2RQ의 매핑 원리'],
    ['단계 3 방법', '표 → Class, 열 → 속성, 행 → 개체 (원칙만)', '원리 4개와 예, 한 행을 따라가는 과정 5개와 과정별 결과'],
    ['단계 3 결과', '예시 값만', 'CSV 파일 3개와 실제 줄, 그것을 모은 Entity(그림 9), 단계 3이 끝난 상태(그림 12)'],
    ['단계 4 근거', 'DDKG 3.2.2~3.2.3, GraphAide', 'DDKG 3.2.2(규칙 기반 추출)만. LLM 추출과 GraphAide는 쓰지 않았으므로 뺌'],
    ['단계 4 시각', '방류시작시간 앞 3시간~뒤 6시간의 총방류량 변화로 운영행위 시각을 정함', '측정값 보정을 없앰. 비고에 적힌 시각, 없으면 방류시작시간'],
    ['단계 4 설명', '문구 목록 표', '규칙 표(표 3)와 실제 비고 5건이 Operation이 되는 과정(그림 13), 별표3 칸 읽기(그림 14)'],
    ['검토할 점', '없음', 'approvalContent에 세 열이 합쳐짐, ID 접두어 표기, 전처리 확인 사항, 승인 조건과 실행 정보의 구분, 별표3 각주'],
    ['10/19 질문', '—', '전처리 후 무엇이 남나 → 2.2 · 매핑이 어떻게 작동하나 → 3.2 · 댐 기본 자료 → 3.3 · AP와 APR → 과정 4, 4장'],
], [1700, 3500, 4772]))

# ------------------------------------------------------------------ 2. 자료 준비
add(h1('2. 자료 준비 (단계 1 소스 구분 · 단계 2 전처리)'))
add(h2('2.1 소스 구분: 자료마다 처리 방법과 채우는 Class를 정한다'))
lis('벤치마킹한 원리: Huang 외(2026)는 결함·위험 댐 22,076개의 자료로 댐 결함 지식그래프(DDKG, Dam Defects Knowledge Graph)를 만든 논문이다. 플랫폼의 정형 표가 c1~c4(Dam, Properties, Location, Parameter)를, 안전 감정 보고서의 비정형 텍스트가 c5~c7(위험 형태, 위험 부위, 안전평가)을 채운다. 즉 Class마다 출처를 정하고, 정형 표인지 비정형 텍스트인지에 따라 처리를 나눈다.',
    '우리 자료 5가지도 같은 원리로 나누었다(그림 1). 승인 기록 CSV와 K-water 일자료·시간자료는 열이 정해진 정형 표라서 열 값을 그대로 옮긴다(단계 3).',
    '승인 기록의 비고 열은 표 안에 있지만 "(실제방류는 20시부터)" 같은 문장이고, 규정 별표3은 선 문자(│, ─)로 그린 글자라서 칸을 그대로 읽을 수 없다. 둘 다 글자를 읽어 값을 뽑아야 하므로 비정형으로 나누었다(단계 4).',
    '그래서 비고 열은 두 번 쓰인다. 단계 3에서는 승인 표의 한 칸으로서 원문을 그대로 옮기고, 단계 4에서는 그 문장을 읽어 운영행위(Operation)를 뽑는다.')
add(fig('step3_doc_f10'))
add(caption('그림 1. 소스 구분 — 자료 5가지의 형태, 처리 방법, 채우는 Class'))

add(h2('2.2 전처리: 원본은 그대로 두고, 쓸 수 있는 형태로 정리한다'))
lis('DDKG의 전처리는 형식이 제각각인 보고서를 마크다운으로 바꾸고(이미지는 OCR) 정규식으로 필요한 네 구간만 잘라내는 것이다. 우리 자료는 정형 표이거나 이미 글자(XML)라서 이 기술을 쓰지 않았다. 따라서 이 부분은 문헌을 따른 방법이 아니라 자료 준비이다.',
    '원칙은 원본 값은 바꾸지 않고, 지우거나 바꾼 것은 기록으로 남기는 것이다.')
add(label('승인 기록: 중복 행을 지우고 대상 댐의 행을 고른다'))
lis('원본은 한강수계 16개 시설의 승인 3,929행이다. 행마다 원본 행 번호와 출처 열(기관, 파일명 등)을 붙인다. 원본 행 번호는 단계 3에서 Entity의 출처가 원본의 어느 행인지 가리키는 데 쓰인다.',
    '그림 2에서 2220행은 2218행과 값이 모두 같다. 같은 승인이 두 번 입력된 것으로 보고 2220을 지우고, (지운 번호, 남긴 번호, 이유)를 로그에 남긴다. 2219는 방류시작시간이 달라 남긴다. 이렇게 지운 행은 전체 7행이다.',
    '괴산댐, 팔당댐처럼 대상 4개 댐(충주, 소양강, 횡성, 광동)이 아닌 행은 매핑에 쓰지 않는다. 남은 80행이 단계 3의 입력이다.')
add(fig('step3_doc_f12'))
add(caption('그림 2. 승인 기록 원본의 실제 행과 처리 — 중복 행 2220을 지우고 대상 댐 행만 남긴다'))
add(label('K-water 시간자료: 두 파일을 이어 붙이고 24시를 다음날 0시로 읽는다'))
lis('시간자료는 두 번에 나눠 받았다. 승인 기간에 맞춰 받은 파일(2010-08~2020-12)과 처음 받은 파일(2021-01~2026-09)은 기간이 이어져 겹치는 시각이 없으므로 그대로 이어 붙인다.',
    '시각 라벨 SDATE_raw는 YYYYMMDDHH 형식이고 시가 01~24로 되어 있다. "24시"는 일반 시각으로 읽을 수 없으므로 다음날 0시로 읽는다. 그림 3의 2020123124가 2021-01-01 00:00이 된다. 이렇게 해야 승인·운영 시각과 같은 시각 체계로 비교할 수 있다.',
    '수위, 유입량 같은 값은 바꾸지 않고, 빈 값도 채우지 않는다. 결과는 4개 댐 × 6개 변수의 508,246개 (댐, 시각)이며, KG가 아닌 측정 저장소에 둔다.')
add(fig('step3_doc_f13'))
add(caption('그림 3. K-water 시간자료의 실제 행 — 두 파일의 경계와 24시 변환 (충주댐)'))
add(label('연계운영규정 별표3: XML에서 별표3만 꺼낸다'))
lis('규정 XML에는 규정 정보, 조문 24개, 부칙, 별표 1~3이 태그로 나뉘어 있다(그림 4).',
    '태그 <별표단위> 중 별표번호가 0003인 것의 <별표내용>만 꺼내, 글자를 바꾸지 않고 문서 저장소에 조회 키 "별표 3"으로 저장한다. 홍수기 제한수위의 근거로 원문을 그대로 보여 주기 위해서이다.',
    '원문의 문자로 그린 표에서 댐별 값을 읽는 일은 단계 4에서 한다.')
add(fig('step3_doc_f14'))
add(caption('그림 4. 규정 XML의 구조와 별표3 꺼내기'))

# ------------------------------------------------------------------ 2. 문헌의 원리
add(h1('3. 단계 3. 구조화 자료 매핑'))
add(h2('3.1 벤치마킹한 문헌의 원리: D2RQ 매핑'))
add(label('표기'))
lis('Zhou 외(2023): 댐 안전 모니터링을 위한 BIM·온톨로지 기반 지식관리를 다룬 논문',
    'OntoDSMS: 이 논문이 구축한 댐 안전 모니터링 시스템(DSMS) 도메인 온톨로지의 이름',
    'D2RQ: 이 논문이 만든 것이 아니라 기존 오픈소스 플랫폼. 논문은 MySQL에 저장된 모니터링 데이터를 OntoDSMS에 연결할 때 D2RQ를 사용했다',
    '본 연구가 벤치마킹한 것: D2RQ의 매핑 원리',
    '용어: 문헌의 instance는 우리 용어로 Entity, DatatypeProperty는 Data Property이다. 이하 우리 용어로 쓴다')
add(label('원리 1. 행의 키 값으로 Entity의 식별자를 만든다'))
lis('D2RQ는 식별자의 틀을 uriPattern으로 정한다. 예: "item/@@item.item_ID@@"',
    '@@ 사이에 적힌 열(item_ID)의 값을 행마다 끼워 넣는다. item_ID가 7인 행 → item/7',
    '식별자를 원본의 키 값으로 만들므로, 같은 행은 언제나 같은 식별자를 받는다')
add(label('원리 2. 한 표에서 나온 식별자는 모두 같은 Class의 Entity가 된다'))
lis('D2RQ는 d2rq:class :Item으로, 그 표의 모든 행 식별자를 Item Class의 Entity로 선언한다',
    '논문의 설명: "Converting a table in a database to a class in an ontology"')
add(label('원리 3. 열 하나를 Data Property 하나에 대응시키고, 셀 값을 그 값으로 옮긴다'))
lis('D2RQ는 열마다 어느 Entity에 붙일지, 어떤 속성인지, 어느 열의 값을 옮길지를 선언한다. 예: column "item.Genre" → 속성 :itemName',
    '고정 문자열과 열 값을 조합해야 할 때는 column 대신 pattern(틀)을 쓴다',
    '논문의 설명: "Converting a column in a table to a DatatypeProperty in an ontology"')
add(label('원리 4. 열과 속성의 대응은 사람이 온톨로지 용어로 정한다'))
lis('매핑 파일은 DB 구조로부터 자동 생성되며, 이때 이름은 DB의 표·열 이름 그대로이다',
    '이를 사람이 온톨로지 용어에 맞게 고친다. 예: Genre 열 → :itemName 속성')

# ------------------------------------------------------------------ 3. 구현
add(h2('3.2 우리 구현: 승인 표 한 행이 Entity가 되는 과정'))
lis('단계 3은 정형 표(승인 기록, K-water 측정자료)의 값을 해석을 더하지 않고 Ontology의 Entity와 Data Property로 옮기는 단계이다.',
    '아래는 승인 표의 504행 하나를 따라간다. 그림의 노란 점선 상자는 그 과정에 쓰인 D2RQ 원리이다.')

add(label('입력: 승인 표와 열의 역할 (원리 4)'))
lis('입력: 전처리를 마친 승인 표(approval_records_clean.csv)에서 대상 4개 댐(충주, 소양강, 횡성, 광동)의 80행. 한 행은 승인 한 건이다.',
    '변환하기 전에 열마다 어떤 역할을 할지 사람이 먼저 정했다. 표 2의 머리 색이 역할이다.')
add(label('표 2. 승인 표(일부)와 열의 역할'))
add(role_table())
lis('관측소코드: 자료 준비 때 승인 파일의 관측소코드와 K-water의 댐 코드(DAM_CD)를 대조했고, 4개 댐 모두 같은 코드였다(1003110 충주 ↔ 1003110 충주댐 등). 댐 자체의 정보는 댐 자료에서 만들므로(3.3) 승인 Entity의 속성으로 옮기지 않는다.',
    '관측소명: 관측소코드와 같은 정보라 옮기지 않는다.',
    '이 밖에 원본 CSV의 행 번호와 출처 열(기관, 내려받은 주소, 원본 파일명 등)이 있으며, 과정 4·5에 쓴다.')

add(label('과정 1. 식별자 만들기 (원리 1)'))
lis('틀 "APR:" + {순차번호}에 504를 넣어 승인 Entity APR:504를 만든다.',
    '같은 행에서 틀 "EVI:AP:" + {순차번호}로 그 승인이 적힌 자료의 Entity EVI:AP:504를 만든다.',
    '순차번호를 키로 쓴 이유: 원본 자료가 승인 한 건마다 매긴 번호이고, 전처리에서 중복 행을 지운 뒤에는 표 안에서 유일하다. 그래서 80행은 서로 다른 ID 80쌍이 된다.',
    'ID는 처리 순서나 무작위 번호가 아니라 원본의 순차번호로 만든다. 그래서 같은 행은 언제 다시 만들어도 같은 ID가 된다.')
add(fig('step3_doc_f1'))
add(caption('그림 5. 식별자 만들기 — 키 열의 값을 틀에 끼운다'))

add(label('과정 2. Class 지정 (원리 2)'))
lis('승인 표에서 만든 APR: ID 80개는 모두 Approval Class의 Entity로 기록한다.',
    'EVI:AP: ID 80개는 모두 EvidenceSource Class의 Entity로 기록한다.')
add(fig('step3_doc_f2'))
add(caption('그림 6. Class 지정'))
add(para('결과: CSV 파일 kgv4_entities.csv에 줄이 생긴다 (한 줄 = Entity 하나)'))
add(rtable([['Entity ID', 'Class'], ['APR:504', 'Approval'], ['EVI:AP:504', 'EvidenceSource']], [4986, 4986]))

add(label('과정 3. 열 → Data Property (원리 3)'))
lis('승인년월일시분 → approvalTime. 원본 값에 시각이 없어 앞 10글자를 날짜로 저장한다(column).',
    '방류시작시간, 접수방류량, 비고 → approvalContent 하나. 세 값을 글자 틀에 넣어 저장한다(pattern). 비고는 원문 그대로 넣는다.',
    '세 열을 합친 이유: 주어진 온톨로지에 Approval의 내용 속성이 approvalContent 하나뿐이었다(4장 검토할 점 1).')
add(fig('step3_doc_f3'))
add(caption('그림 7. 열 → Data Property — 원본 셀 값, 변환 규칙, 결과'))
add(para('결과: CSV 파일 kgv4_properties.csv에 줄이 생긴다 (한 줄 = Entity의 속성 하나)'))
add(rtable([['Entity ID', '속성', '값', '자료형'],
            ['APR:504', 'approvalTime', '2011-06-27', '날짜'],
            ['APR:504', 'approvalContent', P504['approvalContent'], '글자']], [1500, 2000, 5372, 1100]))

add(label('과정 4. 근거 Entity와 연결'))
lis('같은 행의 출처 열을 근거 Entity EVI:AP:504의 속성으로 옮긴다(아래 표).',
    'APR:504와 EVI:AP:504는 같은 504행을 처리하면서 동시에 만든다. 그래서 만드는 그 자리에서 APR:504 —supportedBy→ EVI:AP:504로 잇는다(그림 8).',
    '두 ID의 504는 둘이 같은 원본 행에서 나왔다는 표시이다. 나중에 ID 글자(AP, APR)를 맞춰 보고 찾아서 잇는 것이 아니다.')
add(fig('step3_doc_f8'))
add(caption('그림 8. 같은 행에서 함께 만들며 잇는다 (APR:504 → EVI:AP:504)'))
add(para('결과: 근거 Entity의 속성도 같은 CSV 파일 kgv4_properties.csv에 줄로 추가된다'))
add(rtable([['Entity ID', '속성', '값', '자료형'],
            ['EVI:AP:504', 'sourceTitle', '환경부 한강홍수통제소 홍수예보 댐방류승인', '글자'],
            ['EVI:AP:504', 'sourceType', '승인자료', '글자'],
            ['EVI:AP:504', 'sourceLocator', '순차번호 504', '글자']], [1700, 2000, 5172, 1100]))

add(label('과정 5. 출처 기록'))
lis('우리 원본은 DB가 아니라 내려받은 CSV·JSON 파일이어서, 매핑한 값을 옮겨 저장한다.',
    '값을 옮기면 KG의 값과 원본 행의 연결이 끊긴다. 그래서 Entity마다 원본 파일, 그 안의 위치, 적용한 규칙, 값의 성격을 출처 파일에 남긴다.',
    '위치(504번째 행)로 원 파일의 해당 행을 바로 열 수 있다. 값의 성격 "원본 그대로"는 원본 값을 가공 없이 옮겼다는 뜻이다.')
add(para('결과: CSV 파일 kgv4_provenance.csv에 줄이 생긴다 (한 줄 = Entity의 출처 하나)'))
add(rtable([['Entity ID', '원본 파일', '위치', '규칙', '값의 성격', '메모'],
            ['APR:504', 'approval_records_clean.csv', '504번째 행', 'MR-APR', '원본 그대로', '승인일은 날짜만 있음']],
           [1300, 2800, 1500, 1200, 1500, 1672]))

add(label('결과: CSV 파일 3개'))
lis('단계 3의 결과물은 CSV 파일 3개이며, 03_normalized 폴더에 저장된다.',
    'kgv4_entities.csv: Entity ID와 Class (한 줄 = Entity 하나)',
    'kgv4_properties.csv: Entity ID, 속성, 값, 자료형 (한 줄 = Entity의 속성 하나)',
    'kgv4_provenance.csv: Entity ID, 원본 파일, 위치, 규칙, 값의 성격 (한 줄 = Entity의 출처 하나)',
    '세 파일의 줄을 Entity ID(APR:504)로 모으면 Entity 하나의 전체 모습이 된다: Class, 속성값, 출처(그림 9).')
add(para('파일 안의 실제 모습 (첫 줄은 열 이름, 이어서 APR:504의 줄)'))
add(code('kgv4_entities.csv\n  entity_id,class,label\n  APR:504,Approval,승인 504 (충주댐)\n\n'
         'kgv4_properties.csv\n  entity_id,property,value,datatype\n  APR:504,approvalTime,2011-06-27,date\n  APR:504,approvalContent,' + P504['approvalContent'] + ',string\n\n'
         'kgv4_provenance.csv\n  item,kind,source_file,source_locator,rule,data_origin,note\n  APR:504,entity,03_normalized/approval_records_clean.csv,row_number_in_file=504,MR-APR,real,승인일은 날짜만 있음'))
add(fig('step3_doc_f6'))
add(caption('그림 9. CSV 파일 3개의 줄과 그것을 모은 Entity (APR:504)'))

add(h2('3.3 댐 자료와 측정 자료'))
add(label('Dam (댐 기본 자료)'))
lis('입력: 댐 한 개가 한 행인 표는 따로 없다. K-water 일자료에는 댐 하나의 하루 측정값이 한 행이고, 행마다 댐 코드(DAM_CD), 댐 이름, 댐 유형이 반복해서 붙어 있다.',
    '식별자: 틀 "DAM:" + {DAM_CD}로 만든다. 충주댐의 12,582행은 모두 DAM_CD가 1003110이므로 모두 DAM:1003110이 되고, Entity 하나로 모인다(원리 1).',
    'Class: Dam',
    '속성: 댐 유형 열 → damType(다목적댐). damName에는 승인 자료의 "충주"와 맞춘 표준 댐명(충주댐)을 넣는다.',
    '결과: 승인과 같은 CSV 파일 3개에 Dam Entity의 줄이 추가된다.')
add(fig('step3_doc_f9'))
add(caption('그림 10. K-water 일자료 → Dam Entity'))
add(label('HydrometeorologicalState (HMS, 수문·기상 상태)'))
lis('입력: K-water 시간자료. 한 행이 (댐 코드, 시각)이고 변수 6개(수위, 저수량, 강우량, 유입량, 총방류량, 저수율)가 열로 펼쳐진 넓은 형태이며 553,609행이다.',
    '행마다 Entity를 만들면 55만 개가 된다. KG에 필요한 것은 "어느 댐에 어떤 측정 변수가 있는가"이므로, 키 열(DAM_CD)과 열 머리(변수명)를 함께 틀에 넣어 (댐, 변수)마다 Entity를 만든다. 예: HMS:1003110:수위',
    '결과: 댐 4 × 변수 6 = 24개. 속성은 variableType(수위 등)과 stationCode(1003110)이다.',
    '시각별 값은 KG에 넣지 않고 측정 저장소에 그대로 둔다.',
    '같은 자료에서 댐마다 측정자료 근거 Entity EVI:KW:{DAM_CD}를 만들고, HMS와 supportedBy로 잇는다.',
    '결과: 같은 CSV 파일 3개에 HMS와 근거 Entity의 줄이 추가된다.')
add(fig('step3_doc_f5'))
add(caption('그림 11. K-water 시간자료 → HMS Entity'))

add(h2('3.4 단계 3이 끝난 상태'))
lis('그림 12은 충주댐에 관련된 Entity를 만든 자료별로 모은 것이다.',
    '각 자료에서 Entity와 속성이 만들어졌고, 같은 행·같은 자료에서 함께 만든 근거만 supportedBy로 이어져 있다.',
    '서로 다른 자료에서 만든 승인, 댐, 측정 상태 Entity는 아직 서로 떨어져 있다.',
    '4개 댐 전체: Approval %d, EvidenceSource %d(승인자료 %d, 측정자료 %d), HMS %d, Dam %d. 모두 Entity %d개, 속성 %d개.'
    % (EC['APR'], EC['EVI:AP'] + EC['EVI:KW'], EC['EVI:AP'], EC['EVI:KW'], EC['HMS'], EC['DAM'], NE3, NP3))
add(fig('step3_doc_f7'))
add(caption('그림 12. 단계 3이 끝난 상태 — 충주댐의 Entity'))

# ------------------------------------------------------------------ 4. 단계 4
add(h1('4. 단계 4. 비정형 텍스트 추출'))
add(h2('4.1 벤치마킹한 문헌의 원리: DDKG의 규칙 기반 지식 추출'))
lis('DDKG의 c7(안전평가) Entity는 홍수 방어, 침투, 구조, 내진, 금속 구조 각각의 A/B/C 등급이다.',
    '이 결과는 보고서에서 고도로 표준화된 문형으로 쓰이므로, 딥러닝 없이 정규식으로 바로 뽑는다. 예: "홍수 방어 안전 등급은 C등급이다" → C',
    '반면 같은 결함도 표현이 제각각인 위험 서술(c5 위험 형태, c6 위험 부위)은 정규식으로 처리하기 어려워 LLM으로 분류한다.',
    '즉 원리는 "정해진 문형으로 반복되는 텍스트는 정규식 규칙으로 뽑고, LLM은 표현이 다양한 텍스트에만 쓴다"이다.',
    '우리 자료는 규칙 쪽에 해당한다. 비고는 한 기관이 쓰는 짧은 문구라 어휘가 한정되어 있고("탄력적 방류", "초기수문방류", "실제방류는 N시부터"), 별표3은 칸 배치가 고정된 표이다. 그래서 LLM 추출은 쓰지 않았다.')

add(h2('4.2 비고 → Operation (운영행위)'))
lis('대상: 단계 3에서 승인 Entity에 원문 그대로 옮긴 비고. 80개 승인의 비고를 한 건씩 아래 순서로 처리한다.',
    '① 행위가 아닌 조건 문구를 지운다: "발전방류 포함", "여수로 자연월류량 제외" 등',
    '② 승인 변경 문구("변경", "연장", "정정")가 있으면 새 방류가 아니라 같은 방류의 승인을 바꾼 것으로 보고 Operation을 만들지 않는다. 만들지 않은 사유는 기록한다.',
    '③ 행위 문구 규칙(표 3)을 대조해, 잡힌 문구마다 Operation 하나를 만든다. 한 비고에서 두 개가 잡히면 두 개를 만든다.',
    '④ 행위 문구가 없으면 일반 "방류" 하나를 만든다(실제 방류 시각 문구, 일반 방류 문구, 비고 없음).',
    '⑤ 시각: 비고에 시각이 적혀 있으면 그 시각, 없으면 승인의 방류시작시간을 쓴다.',
    'ID는 "OPR:" + {순차번호} + ":" + {순번}으로 만든다. 한 승인에서 Operation이 둘이면 OPR:2754:1, OPR:2754:2가 된다.')
add(label('표 3. 행위 문구 규칙과 적용 건수 (대상 80건)'))
add(table([
    ['operationType', '찾는 문구 (정규식)', '예', '건수'],
    ['방류종료', '방류\\s*종료', '9.11 16:00 수문방류종료', '1'],
    ['초기방류', '초기\\s*수문\\s*방류 | 초기\\s*방류 | \\(\\s*초기\\s*\\d', '(초기수문방류 100㎥/s)', '9'],
    ['점진·점증방류', '점진 | 점증', '이내 점증방류', '1'],
    ['증가방류', '증가\\s*방류 | \\d\\s*cms\\s*증 | ㎥/s\\s*증가 등', '(증가방류 200 ㎥/s)', '7'],
    ['감소방류', '감소\\s*방류', '—', '0'],
    ['탄력적 방류', '탄력', '최대 100㎥/s 이내 탄력적 방류', '25'],
    ['방류', '실제\\s*방류는\\s*(\\d+)\\s*시부터 / 수문\\s*방류 등 / 비고 없음', '(실제방류는 20시부터)', '25'],
    ['(만들지 않음)', '변경 | 연장 | 정정', '방류기간 (당초) … (변경) …', '17건'],
], [1900, 3700, 3172, 1200]))
add(fig('step3_doc_f15'))
add(caption('그림 13. 실제 비고 5건이 Operation이 되는 과정'))
add(para('결과: 중간 파일 operation_from_remarks_5dams.csv(만든 68행 + 만들지 않은 17행과 사유), 그리고 KG CSV 파일에 Operation의 줄'))
add(rtable([['Entity ID', '속성', '값', '자료형'],
            ['OPR:504:1', 'operationType', '방류', '글자'],
            ['OPR:504:1', 'operationTime', '2011-06-27T20:00', '일시'],
            ['OPR:2754:1', 'operationType', '초기방류', '글자'],
            ['OPR:2754:2', 'operationType', '탄력적 방류', '글자']], [2000, 2400, 4372, 1200]))
lis('80개 승인 중 63개에서 Operation 68개가 만들어진다(58개 승인에서 1개, 5개 승인에서 2개). 17개 승인은 변경 승인이라 만들지 않았다.',
    'Operation도 승인과 같은 행에서 나왔으므로, 근거 Entity EVI:AP:{순차번호}에 supportedBy로 바로 잇는다.')

add(h2('4.3 별표3 → Criterion (홍수기 제한수위)'))
lis('대상: 단계 2에서 꺼내 둔 별표3 원문. 선 문자로 그린 표라 칸이 "│"로 나뉘어 있고, 댐 이름 글자 사이에 공백이 있다("충 주 댐").',
    '① 댐 이름마다 정규식으로 그 댐의 행을 찾는다. 이름 글자 사이에 공백을 허용(\\s*)해서 "충 주 댐"과 "충주댐"을 같은 이름으로 읽고, 이어지는 두 칸(홍수기 제한수위, 시설별 최저 운영수위)의 글자를 원문 그대로 남긴다(criterion_list.csv).',
    '② 대상 댐이면서 제한수위 칸이 숫자뿐인 경우에만 Criterion을 만든다. 값은 숫자(criterionValue), 단위는 EL.m이다.',
    '결과: 충주, 소양강, 횡성 3개(CRI:CR-01~03). 광동댐은 별표3에 없다. Criterion은 규정 근거 EVI:LAW:별표3에 supportedBy로 잇는다.')
add(fig('step3_doc_f16'))
add(caption('그림 14. 별표3의 문자로 그린 표에서 댐별 제한수위 칸 읽기'))

# ------------------------------------------------------------------ 5. 검토할 점
add(h1('5. 검토할 점'))
add(label('1. approvalContent 하나에 세 열이 들어가 있음 (단계 3, 온톨로지 발전 후보)'))
lis('현재: 방류시작시간, 접수방류량, 비고를 글자 하나로 저장한다. 접수일자 열은 어느 속성에도 들어가지 않았다.',
    '이유: 구축 당시 주어진 온톨로지에서 Approval의 Data Property는 approvalTime과 approvalContent 두 개뿐이었고, 온톨로지는 수정하지 않는다는 전제로 매핑했다.',
    '원리로 보면: 세 열은 원본에서 이미 나뉘어 있고 형태(시각, 숫자, 문장)도 분명하므로, 원리 3대로라면 속성도 따로여야 한다.',
    '할 수 없는 것: "접수방류량 2000㎥/s 이상인 승인", "승인일과 방류 시작의 시간 차" 같은 조건 질의',
    '선택지 ①: Approval에 Data Property 추가 — dischargeStartTime(일시), requestedDischarge(숫자, ㎥/s), remark(글자), 필요하면 receiptDate(날짜)',
    '선택지 ②: 현재대로 두고, 승인 내용은 답변에 원문으로 보여 주는 용도로만 쓴다',
    '판단 기준: 지금의 CQ4(과거 방류 승인)는 댐과 기간으로 승인을 찾아 내용을 그대로 돌려주므로 분리가 꼭 필요하지 않다. 방류량이나 시각을 조건으로 쓰는 질문을 CQ에 넣을 때 함께 정한다.')
add(label('2. ID 접두어 표기 (단계 3, 10/19 질문: AP와 APR)'))
lis('연결: APR:504와 EVI:AP:504는 같은 504행에서 동시에 만들어지고, 그 자리에서 이어진다(과정 4, 그림 8). 그래서 글자가 달라도 연결에는 문제가 없다.',
    '표기: APR은 승인(Approval), EVI는 근거 자료(EvidenceSource)이고, EVI 뒤의 AP는 출처 종류(승인자료)이다. 측정자료는 KW, 규정은 LAW이다.',
    '검토: 사람이 볼 때 AP와 APR이 비슷해 헷갈린다. 출처 종류 표기를 Class 접두어와 맞출지(EVI:APR:504) 정한다.')

add(label('3. 전처리에서 남은 확인 사항 (단계 2)'))
lis('중복 판단 기준: 6개 값(관측소코드, 승인일, 방류시작시간, 접수방류량, 접수일자, 비고)이 모두 같으면 같은 승인이 두 번 입력된 것으로 보았다. 실제로 같은 내용의 승인이 두 번 있었을 가능성은 원 승인 대장 없이는 확인할 수 없다.',
    '24시 라벨의 의미: K-water 시간자료의 "24시"가 그 시각의 순간값인지 앞 1시간의 값인지 자료에 설명이 없다. 그래서 시각이 ±1시간 어긋날 수 있다.')

add(label('4. 승인 조건과 실행 정보를 구분하지 않음 (단계 4)'))
lis('비고에는 승인 조건(허가한 범위와 방식, 예: "최대 X 이내 탄력적 방류"), 승인 변경, 실제 실행 정보(예: "실제방류는 20시부터", "수문방류종료")가 섞여 있다.',
    '지금 규칙은 승인 변경만 구분하고, 승인 조건도 운영행위로 만든다. "탄력적 방류" 25건은 허가한 방식이고, 비고가 빈 15건은 승인 자체를 방류로 만든 것이다.',
    '그래서 Operation은 "실제로 한 행위"가 아니라 "승인이 허가한 행위"에 가깝다(코드에도 "실행 확인 아님"으로 표시). 비고를 승인 조건 / 승인 변경 / 실행 정보로 나누고, 승인 조건은 Approval의 속성으로 옮길지 검토한다(검토할 점 1과 연결).')
add(label('5. 별표3 각주가 붙은 값을 건너뜀 (단계 4)'))
lis('팔당댐의 "25.51)"처럼 값 뒤에 각주 번호가 붙으면 숫자만 받는 규칙에서 빠진다. 대상 3개 댐에는 각주가 없어 지금은 영향이 없지만, 대상을 넓히면 값과 각주를 나누어 저장해야 한다.')

# ------------------------------------------------------------------ 6. 다음 주
add(h1('6. 다음 주에 다룰 것'))
add(label('단계 5. 개체 해소·연결'))
lis('이번 주에 채워 이 문서에 더한다.')
add(label('단계 6. 검증 (10/19 지적: 검증 파트가 가장 약함, 다시 고민)'))
lis('제약 하나하나의 정의와 그 제약을 고른 근거(문헌), 판정 방법과 결과',
    '온톨로지를 검증하는 것인지 KG를 검증하는 것인지, 매핑·입력 오류(KG 오류)와 온톨로지 오류의 구분')
add(label('단계 7. 저장'))
lis('저장된 형태(CSV 파일과 그 줄), Cypher가 무엇인지, CSV 한 줄이 Cypher 한 줄을 거쳐 Neo4j에 들어가는 모습')
add(label('검색과 답변'))
lis('의도별 경로를 미리 정해 두는 방식의 한계, 어디까지 탐색할지를 LLM이 판단하게 하는 방안, LLM 입력 구성, CQ를 "판단에 필요한 정보와의 관계"로 다시 정의하는 것')

# ------------------------------------------------------------------ 부록
add(h1('부록. 문헌'))
lis('Huang, J. 외 (2026). Dam defects ontology and knowledge graph construction from multi-source hazard data using large language models. Advanced Engineering Informatics, 76, 104987. — 단계 1의 근거(3.2.1절 지식 출처)',
    'Zhou, Z. 외 (2023). BIM and ontology-based knowledge management for dam safety monitoring. Automation in Construction, 145, 104649.',
    'D2RQ 매핑에 대한 설명은 이 논문의 4장, 매핑 파일의 예는 그림 7(수정된 매핑 파일 일부)에 있다.')

T.save(OUT, ''.join(B), L.IMGS, page_numbers=True)
print('saved', OUT)
