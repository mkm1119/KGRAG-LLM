#!/usr/bin/env python3
"""랩미팅 자료(docx): KG 구축 how (2) — Relation 채우기, 저장, 검색·답변과 11/26 시연 계획.
10/30 자료(build_labmeeting_how_kg.py)와 같은 서식·구성(따른 원리 → 과정 → 결과, 검토할 점, 다음 계획, 부록)이다.
그림은 lab_meeting/how2/fig/kg2_*.png (원본 kg2_figs.html, scripts/build_kg_doc2_figs.py).
사용: python3 scripts/build_labmeeting_how_kg2.py <출력 docx>
"""
import collections, csv, importlib.util, json, os, re, struct, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('L', os.path.join(HERE, 'labdoc_lib.py')); L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
# 10/30 자료와 같은 서식: 본문 9.5pt·줄 간격 1.05, 표 8.5pt, 작은 제목 11pt
_li, _para, _pr = L.li, L.para, L.para_runs
LS = ' w:line="252" w:lineRule="auto"'
L.li = lambda t, sz=19: _li(t, sz).replace('<w:spacing w:after="60"/>', '<w:spacing w:after="40"%s/>' % LS, 1)
L.para = lambda t, sz=19: _para(t, sz).replace('w:after="120"/>', 'w:after="100"%s/>' % LS, 1)
L.cell.__defaults__ = L.cell.__defaults__[:4] + (17,) + L.cell.__defaults__[5:]
L.table.__defaults__ = (True, True, 17, ())
_h1 = L.h1
L.h1 = lambda t, pagebreak=False: _h1(t, False).replace('<w:pStyle w:val="1"/>', '<w:pStyle w:val="1"/><w:spacing w:before="280" w:after="40"/>', 1)
L.label = lambda t: '<w:p><w:pPr><w:keepNext/><w:spacing w:before="140" w:after="20"/><w:rPr>%s</w:rPr></w:pPr>%s</w:p>' % (L.LANG, L.run(t, sz=22, b=True, color='1F4E79'))
for n in ('run', 'title', 'subtitle', 'dateline', 'label', 'h1', 'h2', 'para', 'li', 'spacer', 'table', 'caption'):
    globals()[n] = getattr(L, n)

ROOT = os.path.join(HERE, '..'); N = os.path.join(ROOT, '03_normalized')
LAB = os.path.join(ROOT, '..', 'lab_meeting')
FIG = os.path.join(LAB, 'how2', 'fig')
RUNS = os.path.join(ROOT, '05_retrieval', 'server_runs_20261016')
OUT = sys.argv[1]
T = L.Template(os.path.join(LAB, '랩미팅 자료_KG구축_검색답변_최종.docx'))
rd = lambda p: list(csv.DictReader(open(os.path.join(N, p), encoding='utf-8-sig')))

# ------------------------------------------------------------------ 사실 (현재 파일에서 확인)
ents, props, rels = rd('kgv4_entities.csv'), rd('kgv4_properties.csv'), rd('kgv4_relations.csv')
cls = {e['entity_id']: e['class'] for e in ents}
CC = collections.Counter(cls.values())
RC = collections.Counter(r['relation'] for r in rels)
assert (len(ents), len(props), len(rels)) == (264, 616, 418)
assert RC == {'supportedBy': 175, 'concernsDam': 80, 'authorizes': 68, 'performedOnDam': 68, 'hasHydrometeorologicalState': 24, 'appliesToDam': 3}, RC
LINKED = collections.defaultdict(set)
for r in rels:
    LINKED[r['relation']].add(r['subject'])
assert len(LINKED['concernsDam']) == 80 and len(LINKED['performedOnDam']) == 68 and len(LINKED['authorizes']) == 63 and len(LINKED['appliesToDam']) == 3
NEW = sum(v for k, v in RC.items() if k != 'supportedBy')
assert NEW == 243
CYPHER_LINES = sum(1 for _ in open(os.path.join(N, 'kgv4_load.cypher'), encoding='utf-8'))
assert CYPHER_LINES == 684
TR = {q: json.load(open(os.path.join(RUNS, '084150_answer_q1-q5', q + '_trace.json'), encoding='utf-8')) for q in ('q1', 'q2', 'q3', 'q4', 'q5')}
assert TR['q3']['intent_json'] == {'intent': ['CQ2', 'CQ3', 'CQ4'], 'dam': '충주댐', 'period': {'start': '2020-08-01', 'end': '2020-08-31'}}
assert '수문 상황과 유입량 변화에 따라 조정된 것으로 판단' in TR['q3']['answer'] and '[CQ5]' in TR['q4']['answer']
Q1_INTENTS = [json.load(open(os.path.join(RUNS, d, 'q1_trace.json'), encoding='utf-8'))['intent_json']['intent']
              for d in ('083450_no_answer_q1-q5', '084150_answer_q1-q5', '091208_answer_q1', '091453_answer_q1', '091737_answer_q1')]
assert sum('CQ2' in i for i in Q1_INTENTS) == 1, Q1_INTENTS

TRIM = os.path.join(FIG, 'trim')
os.makedirs(TRIM, exist_ok=True)
PX2DXA = L.W * 0.97 / 2100 * 0.76   # 10/30 자료와 같은 비율(그림 글자 크기 같음)


def fig(name):
    pth = os.path.join(TRIM, name + '.png')
    subprocess.run(['convert', os.path.join(FIG, name + '.png'), '-trim', '-bordercolor', 'white', '-border', '12', '+repage', pth], check=True)
    with open(pth, 'rb') as f:
        w, h = struct.unpack('>II', f.read(24)[16:24])
    full = name in ('kg2_k1', 'kg2_c1', 'kg2_c2', 'kg2_s3', 'kg2_s2', 'kg2_r1')   # Entity가 많은 결과 KG와 Cypher 문이 든 그림은 쪽 너비 전체로
    return L.image(name, pth, w, h, name, width=L.W if full else min(int(w * PX2DXA), L.W))


B = []
add = B.append
FIGNO = {}


def figcap(name, text):
    FIGNO[name] = len(FIGNO) + 1
    add(fig('kg2_' + name))
    add(caption('그림 %d. %s' % (FIGNO[name], text)))


def lis(*items):
    for t in items:
        add(li(t))


rtable = lambda rows, widths: table(rows, widths, header=True, firstcol=False)

# ================================================================== 표지
add(title('KG 구축 how 보완 (2)', 'Relation 채우기 · 저장 · 검색·답변'))
add(subtitle('따른 문헌의 원리와 실제 수행 과정, 그리고 11/26 시연 계획'))
add(dateline('2026.11 · 문경민'))

# ================================================================== 1. 현황
add(h1('1. KG 구축 단계와 방법론 구체화 현황'))
lis('KG 구축은 온톨로지가 정해 둔 틀(Class, Data Property, Relation)에 자료의 실제 값을 채우는 일이다. 10/30 자료에서는 Class(Entity)와 Data Property(속성값)를 채우는 과정을 정리했다. 그 결과 Entity 264개와 속성값 616개가 만들어졌다.',
    '이번 자료는 남은 Relation을 채우는 과정(2장), 채운 결과를 Neo4j에 넣는 저장(3장), 채워진 KG로 질문에 답하는 검색·답변(4장)을 같은 방식(따른 원리 → 과정 → 결과)으로 정리했다. 온톨로지와 KG의 내용은 10/30 자료와 같다.',
    '검증은 11/02 회의에 따라 다른 연구들이 KG·온톨로지를 어떻게 검증했는지 조사한 뒤 정리한다. 각 원리의 자세한 설명은 부록 C에 있다.')
DONE, NOW, NEXT = 'E3F1DC', 'D6E8F7', 'FDEBD3'


def status_table():
    ws = [2100, 2900, 3172, 1800]
    rows = [('자료 준비', '소스 구분과 전처리', '—', '정리함 (10/30)', DONE),
            ('Class·Data Property 채우기', 'Entity와 속성값을 채움', '구조화 자료 매핑(정형 표), 비정형 텍스트 추출(비고, 별표3)', '정리함 (10/30)', DONE),
            ('Relation 채우기', 'Relation마다 실제 시작·끝 Entity를 이음', '자료 속 키로 끝 Entity를 정함(댐 표기 맞추기 포함)', '이번 (2장)', NOW),
            ('저장', '채운 결과를 Neo4j에 넣음', 'CSV → Cypher → Neo4j', '이번 (3장)', NOW),
            ('검색·답변', '질문에 맞는 근거를 KG에서 찾아 LLM이 답함', '의도 추출 → Cypher 템플릿 조회 → 근거 묶음 → 답변', '이번 (4장)', NOW),
            ('검증', '만든 KG가 맞는지 확인', '—', '선행연구 조사 후', NEXT)]
    out = ['<w:tbl><w:tblPr><w:tblW w:w="%d" w:type="dxa"/><w:jc w:val="center"/><w:tblBorders>%s</w:tblBorders><w:tblLayout w:type="fixed"/></w:tblPr><w:tblGrid>%s</w:tblGrid>'
           % (L.W, L.BORD, ''.join('<w:gridCol w:w="%d"/>' % w for w in ws))]
    out.append('<w:tr><w:trPr><w:cantSplit/><w:tblHeader/></w:trPr>' + ''.join(L.cell(c, w, fill='D9EAF7', b=True, center=True) for c, w in zip(['단계', '하는 일', '방법', '방법론 정리'], ws)) + '</w:tr>')
    for name, job, how, st, fill in rows:
        out.append('<w:tr><w:trPr><w:cantSplit/></w:trPr>' + L.cell(name, ws[0], fill='EEF5FA', b=True, color='1F4E79', center=True)
                   + L.cell(job, ws[1]) + L.cell(how, ws[2]) + L.cell(st, ws[3], fill=fill, b=True, center=True) + '</w:tr>')
    out.append('</w:tbl>')
    return ''.join(out) + spacer()


add(label('표 1. 단계별 하는 일과 방법론 정리 여부'))
add(status_table())

# ================================================================== 2. Relation 채우기
add(h1('2. Relation 채우기'))
add(h2('2.1 왜 Relation을 따로 채우는가'))
lis('그림 {{r0}}의 왼쪽은 온톨로지의 Relation 한 줄 "Approval —concernsDam→ Dam"이다. 이것은 Class 사이의 규칙이라 어느 승인이 어느 댐에 관한 것인지는 들어 있지 않다.',
    '오른쪽은 KG이다. 승인 APR:504에서 댐 4개로 가는 선은 모두 온톨로지 규칙에 맞는다(점선). 승인 80개 × 댐 4개 = 320가지 조합이 형식상 맞지만, 실제 관계는 80개뿐이다.',
    '실제 관계를 고르는 것은 자료 안의 키이다. 승인 504행의 관측소코드가 1003110이므로 APR:504의 끝 Entity는 DAM:1003110(충주댐)이다(실선).',
    'Class와 Data Property만 채우면 KG에는 선이 하나도 없어서 "충주댐의 승인"을 조회해도 아무것도 나오지 않는다. Relation 채우기는 속성 칸에 값을 채우는 것과 같은 일이며, 채우는 값이 숫자나 글자가 아니라 다른 Entity(끝 Entity)라는 점만 다르다.')
figcap('r0', '온톨로지가 허락한 조합(점선) 가운데 자료 속 키로 실제 관계(실선)를 고른다')
add(label('Class·Data Property 채우기 다음에 하는 이유'))
lis('끝 Entity가 먼저 만들어져 있어야 한다. 승인 표를 옮길 때는 다른 자료(K-water 일자료)에서 만드는 댐 Entity가 아직 없을 수 있다.',
    '자료마다 다르게 적힌 댐("충주", 1003110, "충 주 댐")을 같은 댐으로 알아봐야 끝 Entity를 정할 수 있다(2.3).',
    '그래서 모든 Entity를 만든 뒤에 Relation을 채운다. 근거 관계(supportedBy)도 온톨로지의 Relation이므로 이 단계에서 함께 정리한다(10/30 자료 과정 4의 근거 연결).')

add(h2('2.2 따른 원리와 진행 방식'))
lis('따른 원리: Purohit 외(2024)는 GraphAide에서 뉴스 기사 1,846건으로 KG를 만들 때, 글에서 뽑은 대상의 표기를 기준 지식베이스(DARPA Wikidata)의 식별자(QID)에 대응시켰다. 같은 QID를 받은 표기는 같은 Entity가 된다(부록 C.1).',
    '원리: 기준 식별자를 하나 정하고, 자료마다 다르게 적힌 같은 대상을 그 식별자에 대응시킨다. 우리는 K-water 댐 코드를 기준 식별자로 삼았다. 대상이 댐 4개라서 코드 일치와 대응 표로 했고, GraphAide의 벡터 검색과 LLM 재순위는 쓰지 않았다.',
    '참고로 Huang 외(2026)는 댐마다 관련 Entity를 JSON 파일 하나로 묶어 적재했고, 본문에 서로 다른 자료의 같은 대상을 맞추는 단계는 따로 없다. 우리 자료는 승인 기록, K-water 자료, 규정이 서로 다른 기관에서 따로 와서 댐 표기를 맞추는 과정이 필요하다.',
    '진행 방식: 먼저 댐 표기를 기준 식별자에 맞춘다(2.3). 그 다음 Relation마다 시작 Entity를 하나씩 읽고, 자료 속 키로 끝 Entity를 정해 관계 한 줄을 쓰며, 끝 Entity를 정한 방법(규칙)과 값의 성격을 남긴다. 키가 어느 자료에서 나오는지에 따라 세 가지 방식이 있다(표 2, 2.4~2.6).')
add(label('표 2. Relation별 끝 Entity를 정하는 키'))
REL_ROWS = [['supportedBy', 'Approval → EvidenceSource', '같은 순차번호', '2.4 승인 한 행', '원본 그대로', 80],
            ['supportedBy', 'Operation → EvidenceSource', '운영행위 ID의 순차번호', '2.4 승인 한 행', '원본에서 유도', 68],
            ['authorizes', 'Approval → Operation', '같은 순차번호', '2.4 승인 한 행', '연구용 구성', RC['authorizes']],
            ['concernsDam', 'Approval → Dam', '관측소코드 = 댐 코드', '2.4 승인 한 행', '원본 그대로', RC['concernsDam']],
            ['performedOnDam', 'Operation → Dam', '순차번호 → 관측소코드', '2.4 승인 한 행', '원본에서 유도', RC['performedOnDam']],
            ['hasHydrometeorologicalState', 'Dam → HMS', '같은 댐 코드', '2.5 댐 코드', '원본 그대로', RC['hasHydrometeorologicalState']],
            ['supportedBy', 'HMS → EvidenceSource', '같은 댐 코드', '2.5 댐 코드', '원본 그대로', 24],
            ['appliesToDam', 'Criterion → Dam', '별표3 댐 이름 → 대응 표', '2.6 별표3 이름', '이름 일치', RC['appliesToDam']],
            ['supportedBy', 'Criterion → EvidenceSource', '규정 하나 → 고정 ID', '2.6 별표3 이름', '원본 그대로', 3]]
assert sum(r[5] for r in REL_ROWS) == len(rels)
add(rtable([['Relation', '시작 → 끝', '끝 Entity를 정하는 키', '방식', '값의 성격', '개수']] + [r[:5] + [str(r[5])] for r in REL_ROWS] + [['합계', '', '', '', '', str(len(rels))]],
           [2300, 2300, 2072, 1400, 1250, 650]))
add(para('값의 성격: 원본 그대로 = 원본의 키가 같아서 이음 / 원본에서 유도 = 원본의 키를 한 번 거쳐 이음 / 연구용 구성 = 원본에 직접 적힌 관계가 아니라 연구에서 정해 이음 / 이름 일치 = 코드가 없어 이름으로 이음.', sz=18))

add(h2('2.3 댐 표기 맞추기 (개체 해소)'))
lis('그림 {{g1}}의 왼쪽은 충주댐이 자료마다 적힌 모습이다. 승인 기록은 관측소코드 1003110과 관측소명 "충주", K-water 자료는 DAM_CD 1003110, 규정 별표3은 "충 주 댐"이라는 이름뿐이고 코드가 없다.',
    '승인 기록은 관측소코드가 K-water 댐 코드와 같아서 그대로 맞춘다(자료 준비 때 4개 댐 모두 같음을 확인). K-water 자료의 DAM_CD는 기준 식별자 자체이다.',
    '별표3은 비정형 텍스트 추출에서 공백을 빼고 읽은 "충주댐"을 대응 표(표준 댐명 → 댐 코드, 4줄)에서 찾아 1003110을 얻는다. 광동댐은 별표3에 없다.',
    '결과: 세 표기가 모두 하나의 Entity DAM:1003110을 가리킨다. 이후 2.4~2.6에서 댐을 끝 Entity로 정할 때 이 대응을 쓴다.')
figcap('g1', '자료마다 다른 충주댐 표기 세 가지를 기준 식별자 DAM:1003110에 맞춘다')

add(h2('2.4 승인 기록 한 행으로 채우는 관계'))
lis('표 2의 9줄 중 5줄은 승인 기록의 한 행에서 끝 Entity가 정해진다. 그림 {{g0}}의 위쪽은 승인 504행을 칸 그대로 그린 것이다.',
    '10/30 단계에서 이 행의 승인 칸들로 APR:504를, 비고를 추출해 OPR:504:1을, 출처 열로 EVI:AP:504를 만들었다. 세 ID에 모두 이 행의 순차번호 504(주황)가 들어 있다.',
    '화살표는 이번에 채우는 관계이다. 위쪽 세 화살표, 곧 APR:504 → OPR:504:1(authorizes), APR:504 → EVI:AP:504와 OPR:504:1 → EVI:AP:504(supportedBy)는 ID의 순차번호가 같은 것끼리 잇는다. 아래쪽 두 화살표, 곧 APR:504 → DAM:1003110(concernsDam)과 OPR:504:1 → DAM:1003110(performedOnDam)은 이 행의 관측소코드 1003110(파랑)으로 끝 Entity를 정한다.',
    'authorizes는 "같은 승인 행의 비고에서 뽑은 행위를 그 승인이 허가했다"고 연구에서 정해 이은 것이라 값의 성격이 연구용 구성이다(검토할 점 1).',
    '결과: 승인 80행에 같은 방법을 적용해 supportedBy 148개(승인 80, 운영행위 68), authorizes 68개, concernsDam 80개, performedOnDam 68개를 채운다. 변경 승인 17개는 운영행위가 없어 authorizes가 없다.')
figcap('g0', '승인 504행 하나에서 채우는 관계 — 순차번호 504와 관측소코드 1003110이 끝 Entity를 정한다')

add(h2('2.5 댐 코드로 채우는 관계'))
lis('그림 {{gB}}의 맨 위는 K-water 시간자료의 충주댐 한 행이다. 10/30 단계에서 이 표의 DAM_CD와 열 머리(변수)로 HMS 6개를 만들었고(각 열 바로 아래), 댐마다 측정자료 근거 EVI:KW 하나를 만들었다. 댐 Entity는 일자료에서 만들었다.',
    '세 종류 Entity의 ID에 모두 같은 댐 코드 1003110(파랑)이 들어 있다. 그래서 위의 DAM:1003110에서 HMS 6개로(hasHydrometeorologicalState), HMS 6개에서 아래의 EVI:KW:1003110으로(supportedBy) 코드가 같은 것끼리 잇는다. 다른 자료를 찾을 필요가 없다.',
    '결과: 4개 댐 × 6개 변수로 hasHydrometeorologicalState 24개, supportedBy 24개를 채운다.')
figcap('gB', '댐 코드로 채우는 관계 — 같은 코드 1003110을 가진 Dam, HMS, 측정자료 근거를 잇는다')

add(h2('2.6 별표3 댐 이름으로 채우는 관계'))
lis('그림 {{gC}}의 위쪽은 비정형 텍스트 추출로 만든 중간 파일 criterion_list.csv의 한 줄이다. 10/30 단계에서 이 줄로 CRI:CR-02를 만들었다(점선).',
    '별표3에는 댐 코드가 없다. 그래서 이 줄의 댐 이름 "충주댐"을 오른쪽 대응 표에서 찾아 댐 코드 1003110을 얻고, CRI:CR-02 → DAM:1003110(appliesToDam)을 쓴다. 코드가 아니라 이름으로 정한 끝 Entity이므로 값의 성격을 "이름 일치"로 남긴다.',
    '근거는 규정 하나뿐이라 근거 Entity도 하나(고정 ID EVI:LAW:별표3)이다. 기준 3개 모두 CRI → EVI:LAW:별표3(supportedBy)으로 잇는다.',
    '결과: appliesToDam 3개(충주, 소양강, 횡성), supportedBy 3개를 채운다.')
figcap('gC', '별표3 댐 이름으로 채우는 관계 — 이름을 대응 표로 댐 코드에 맞춘다')

add(h2('2.7 결과: Relation이 채워진 CSV'))
lis('Relation 9종(온톨로지의 관계 9개)의 실제 관계 %d개가 kgv4_relations.csv에 한 줄씩 채워진다. 그림 {{r1}}은 그 파일의 실제 줄이다.' % len(rels),
    '한 줄은 Relation 하나이며, 시작 Entity(subject), Relation 이름(relation), 끝 Entity(object), 끝 Entity를 정한 규칙(rule), 값의 성격(origin), 설명(note)으로 이루어진다. 예를 들어 "APR:504, concernsDam, DAM:1003110"은 승인 504가 충주댐에 관한 것이라는 관계 하나이다.',
    '이로써 KG에 들어갈 내용은 CSV 파일 세 개에 모두 채워졌다. kgv4_entities(Entity와 Class), kgv4_properties(Data Property 값), kgv4_relations(Relation)이다. 이 세 파일을 그래프로 저장하는 것이 3장이다.',
    '연결 확인(10/19 질문 "연결이 실제로 되나"): 4개 댐 전체에서 승인 80개 모두 댐과 근거에, 운영행위 68개 모두 댐·승인·근거에, HMS 24개 모두 댐과 근거에, 기준 3개 모두 댐과 근거에 이어졌다. 승인 중 운영행위로 이어진 것은 63개이며, 나머지 17개는 변경 승인이다.')
figcap('r1', 'kgv4_relations.csv의 실제 줄 — 충주댐 Entity 몇 개가 시작인 줄 14개')

# ================================================================== 3. 저장
add(h1('3. 저장'))
add(h2('3.1 따른 원리와 진행 방식'))
lis('따른 원리: Huang 외(2026)는 추출한 지식을 JSON으로 모은 뒤, 온톨로지의 관계에 따라 Python 스크립트가 JSON의 키-값을 읽어 Cypher 문을 만들고, Entity와 Relation을 Neo4j에 한꺼번에 넣었다. Neo4j는 Cypher로 조회·추가·삭제·수정이 효율적이고 여러 Relation을 건너는 질의에 강해서 골랐다고 밝혔다(부록 C.2).',
    'Neo4j는 Entity와 Relation을 그래프(점과 선) 모양으로 저장하는 데이터베이스이다. Cypher는 Neo4j에 Entity와 Relation을 넣고 찾을 때 쓰는 명령 문장이다. CSV는 줄의 목록이라 "충주댐에서 출발해 관계를 따라간다"는 질의를 바로 할 수 없어서, 그래프로 저장한다.',
    '우리는 모은 형태가 JSON이 아니라 2장까지 채운 CSV 파일 세 개이다. Python 스크립트가 이 파일의 줄을 읽어 Cypher 문을 쓰고(과정 1·2), 그 문을 모은 파일을 Neo4j에서 실행한다(과정 3). 출처 파일(kgv4_provenance)은 Neo4j에 넣지 않고 CSV로 둔다.',
    '아래 그림들은 CSV의 칸과 Cypher 문의 자리를 같은 색으로 칠했다. 같은 색 칸의 값이 Cypher 문의 그 자리에 들어가며, 자리 위의 작은 글자는 그 값이 온 CSV 열 이름이다.')

add(h2('3.2 CSV → Cypher → Neo4j'))
add(label('과정 1. Entity를 Cypher 문으로 쓰고 Neo4j에 넣기'))
lis('원리: Entity 하나는 Cypher 문 하나가 되고, 실행하면 Neo4j에 Entity 하나가 생긴다. Class와 Data Property 값도 그 문 안에 함께 들어간다.',
    '그림 {{c1}}의 위는 입력이다. kgv4_entities.csv의 APR:504 줄 1개와 kgv4_properties.csv의 APR:504 줄 2개를 Python 스크립트가 Entity ID로 모은다.',
    '가운데가 그 줄들로 쓴 Cypher 문이다. 같은 색을 따라가면, entity_id(APR:504)는 {id: \'APR:504\'} 자리에, class(Approval)는 :Approval 자리에, label은 n.label = 뒤에 들어간다. property(approvalTime, approvalContent)는 n. 뒤의 이름 자리에, value는 = 뒤의 값 자리에 들어간다. datatype이 date이면 값을 date( )로 감싸 글자가 아니라 날짜로 넣는다. 그래야 4장에서 "2020년 8월 안"처럼 기간으로 비교해 찾을 수 있다.',
    '문장의 뜻은 그림의 설명과 같다. MERGE는 이 Entity가 없으면 만들고 있으면 그대로 쓰라는 뜻이라서, 같은 문을 다시 실행해도 APR:504가 둘이 되지 않는다. SET은 Data Property 값을 넣으라는 뜻이다.',
    '맨 아래가 실행 결과이다. Neo4j에 Entity APR:504가 Class와 Data Property 값을 가진 채 생긴다. %d개 Entity마다 이런 문이 하나씩 쓰인다.' % len(ents))
figcap('c1', '과정 1 — CSV 칸이 Cypher 문의 자리로 들어가고, 실행하면 Neo4j에 Entity가 생긴다 (APR:504)')
add(label('과정 2. Relation을 Cypher 문으로 쓰고 Neo4j에 넣기'))
lis('원리: Relation 하나는 Cypher 문 하나가 된다. Relation은 두 Entity 사이에 긋는 것이므로, 문은 두 Entity를 먼저 찾고 그 사이에 Relation을 만든다.',
    '그림 {{c2}}의 위는 kgv4_relations.csv의 한 줄이다. 같은 색을 따라가면, subject(APR:504)와 object(DAM:1003110)는 MATCH 문에서 찾을 두 Entity의 ID 자리에, relation(concernsDam)은 화살표 안의 이름 자리에, rule, origin, note는 SET 뒤의 값 자리에 들어간다.',
    'MATCH는 이미 있는 Entity를 찾으라는 뜻이고, 찾은 두 Entity를 이 문 안에서 a와 b로 부른다. (a)-[r:concernsDam]->(b)는 a에서 b로 가는 concernsDam Relation이라는 뜻이며, MERGE로 없을 때만 만든다.',
    '맨 아래가 실행 결과이다. 두 Entity 사이에 방향이 있는 선 하나가 생기고, 그 선에 규칙과 값의 성격이 남는다. %d개 Relation마다 이런 문이 하나씩 쓰인다.' % len(rels))
figcap('c2', '과정 2 — 관계 CSV 한 줄이 Cypher 문이 되고, 실행하면 두 Entity 사이에 Relation이 생긴다')
add(label('과정 3. Cypher 문을 모아 Neo4j에서 실행하기'))
lis('원리: 과정 1·2에서 쓴 문을 파일 하나에 모아, Neo4j가 위에서부터 한 번에 실행하게 한다.',
    '그림 {{s3}}의 왼쪽이 그 파일(kgv4_load.cypher, %d줄)이다. 주석 1줄, ID가 겹치지 않게 막는 규칙 1줄, Entity 문 %d줄, Relation 문 %d줄 순서이다. Relation 문은 두 Entity를 찾아야 하므로 Entity 문이 모두 끝난 뒤에 온다.' % (CYPHER_LINES, len(ents), len(rels)),
    '오른쪽은 위에서 아래로 실행 순서이다. Neo4j를 켜고, 이전에 넣은 Entity와 Relation을 모두 지운 뒤, 파일을 실행하고, 마지막에 Entity와 Relation 수를 세어 %d개, %d개인지 확인한다.' % (len(ents), len(rels)),
    '매번 지우고 처음부터 넣으므로, CSV를 고친 뒤 다시 실행하면 Neo4j의 KG가 CSV와 항상 같아진다.')
figcap('s3', '과정 3 — Cypher 파일의 구성과 실행 순서')

add(h2('3.3 KG 밖에 두는 것: 측정 저장소와 문서 저장소'))
lis('시간별 측정값(508,246행)과 규정 원문은 KG에 넣지 않고 CSV 파일로 둔다. KG에는 그 파일의 행을 찾아갈 값만 Data Property로 둔다.',
    '그림 {{s2}}의 위는 측정 저장소이다. Entity HMS:1003110:수위의 stationCode(1003110)가 DAM_CD 열과 같고, 찾을 시각(2020-08-02 18:00)이 SDATE_raw 열(2020080218)과 같은 행을 찾는다. 그 행의 DATA1_수위 열이 그 시각의 수위 139.55 EL.m이다.',
    '아래는 문서 저장소이다. Entity EVI:LAW:별표3의 sourceLocator("별표 3")가 sourceLocator 열과 같은 행을 찾으면, 그 행의 text가 규정 원문이다.')
figcap('s2', '외부 저장소 CSV의 실제 모습과, KG의 값으로 행을 찾는 방법')

add(h2('3.4 결과: Neo4j에 저장된 KG'))
lis('Neo4j에 Entity %d개와 Relation %d개가 저장된다(표 3).' % (len(ents), len(rels)),
    '그림 {{k1}}은 Neo4j에 저장된 충주댐의 Entity 53개와 Relation을 생략 없이 그린 것이다. 왼쪽 세 점선 상자는 승인자료 근거 15, 승인 15, 운영행위 14개이고, 한 줄이 승인 한 건이다. 승인마다 왼쪽 근거(supportedBy)와 오른쪽 운영행위(authorizes)로 이어지며, 3519와 3647은 변경 승인이라 운영행위가 없다.',
    '상자에서 나가는 굵은 선은 상자 안의 Entity가 모두 가진 Relation이다. 승인 15개는 모두 DAM:1003110에(concernsDam), 운영행위 14개는 모두 DAM:1003110에(performedOnDam)와 같은 순차번호의 근거에(supportedBy) 이어진다. 오른쪽 위는 DAM:1003110의 HMS 6개와 그 근거, 오른쪽 아래는 기준 CR-02와 그 근거이다.',
    '맨 아래 두 점선 상자는 KG에 넣지 않은 외부 저장소이고, 점선 화살표는 Relation이 아니라 KG의 값으로 그 행을 찾아오는 길이다. HMS의 stationCode와 시각으로 측정값을, EVI:LAW:별표3의 sourceLocator로 규정 원문을 가져온다. 4장의 검색이 이 KG의 Relation을 따라가고, 이 점선으로 값을 가져온다.')
figcap('k1', 'Neo4j에 저장된 KG(충주댐 Entity 53개)와 외부 저장소로 가는 길')
add(label('표 3. Neo4j에 저장된 Entity와 Relation 수'))
add(rtable([['Class', 'Entity 수', 'Relation', 'Relation 수'],
            ['EvidenceSource', str(CC['EvidenceSource']), 'supportedBy', str(RC['supportedBy'])],
            ['Approval', str(CC['Approval']), 'concernsDam', str(RC['concernsDam'])],
            ['Operation', str(CC['Operation']), 'authorizes', str(RC['authorizes'])],
            ['HydrometeorologicalState', str(CC['HydrometeorologicalState']), 'performedOnDam', str(RC['performedOnDam'])],
            ['Dam', str(CC['Dam']), 'hasHydrometeorologicalState', str(RC['hasHydrometeorologicalState'])],
            ['Criterion', str(CC['Criterion']), 'appliesToDam', str(RC['appliesToDam'])],
            ['합계', str(len(ents)), '합계', str(len(rels))]], [3200, 1786, 3200, 1786]))

# ================================================================== 4. 검색·답변
add(h1('4. 검색·답변'))
add(h2('4.1 따른 원리와 진행 방식'))
lis('따른 원리: Purohit 외(2024)의 GraphAide는 질의 단계에서 LLM이 자연어 질문을 부분 그래프 조회 템플릿으로 바꾸고, 이를 Cypher로 Neo4j에서 실행한 결과를 LLM에 맥락으로 주어 답변을 만든다. KG의 관계를 따라 찾은 근거를 주므로 LLM이 없는 사실을 지어내는 것(환각)을 줄인다(부록 C.1).',
    '우리는 조회 템플릿을 CQ마다 미리 정해 두었다(Cypher 6개). LLM은 질문에서 의도(CQ1~CQ6)와 값(댐, 기간)만 뽑고, 그 다음은 코드가 정해진 순서대로 KG와 저장소를 조회한다. GraphAide의 Cypher 자동 생성, 질의 확장, 벡터 검색, 에이전트는 쓰지 않았다.',
    '진행 방식: 질문 하나가 6단계를 거친다. LLM은 ①과 ⑥ 두 곳에서 쓰고(같은 모델, 지시문만 다름), ②~⑤는 코드가 한다(그림 {{q0}}). 아래에서 서버 실행 기록의 질문 하나를 따라간다(Qwen3-32B, 2026-10-16).')
figcap('q0', '질문 하나가 답변까지 가는 전체 경로')

add(h2('4.2 질문 하나를 따라가기'))
add(label('입력'))
lis('질문: "2020년 8월 충주댐 방류 승인과 운영행위, 그때의 수문 상태를 알려줘."')
add(label('과정 1. 의도·값 추출 (LLM)'))
lis('LLM에 지시문과 질문을 준다. 지시문에는 의도 목록(CQ1~CQ6), 허용 댐 4개, 값의 형식, 규칙 5개가 있다(목록 밖 의도를 만들지 않음, 질문에 없는 값을 추측하지 않음, 이유를 묻는 질문과 범위 밖 댐은 의도를 비우고 이유를 적음, JSON 하나만 출력).',
    '이 질문에서 LLM은 "방류 승인" → CQ4, "운영행위" → CQ3, "그때의 수문 상태" → CQ2, 댐 = 충주댐, 기간 = 2020-08-01 ~ 2020-08-31을 뽑았다.')
figcap('q1', '질문 속 표현이 의도와 값이 되는 과정')
add(label('과정 2. 입력 확인 (코드)'))
lis('의도가 CQ1~CQ6 안인지, 댐이 4개 댐 안인지 확인하고 이름을 표준 댐명으로 바꾼다("충주" → 충주댐).',
    '기간의 끝 날짜는 그 날 전체로 읽어 [2020-08-01 00:00, 2020-09-01 00:00)으로 바꾼다. 확인을 통과하지 못하면 조회하지 않고 "질의 불가: 이유"를 답변 단계로 넘긴다.')
add(label('과정 3. KG 조회 (코드, Cypher 템플릿)'))
lis('먼저 충주댐의 HMS에서 stationCode(1003110)를 얻는다. 측정 저장소를 찾아갈 키이다.',
    'CQ3: 충주댐에서 performedOnDam을 거꾸로 따라가 기간 안의 운영행위를 찾고, authorizes로 그것을 허가한 승인을 찾는다 → OPR:3412:1 ← APR:3412.',
    'CQ4: concernsDam으로 승인일이 기간 안인 승인을 찾는다 → APR:3412, APR:3519, APR:3647. 뒤의 둘은 변경 승인이라 운영행위가 없다.',
    '2장에서 채운 관계가 여기서 조회 경로로 쓰인다. CQ별 경로는 그림 {{q2}}의 표와 같다.')
figcap('q2', 'CQ3 Cypher 템플릿과 따라가는 관계, CQ별 조회 경로')
add(label('과정 4. 외부 저장소 조회 (코드)'))
lis('CQ2와 CQ3이 함께 있으면 운영행위 시각마다 그 시각의 측정값을 읽는다. 키는 stationCode 1003110과 시각 2020-08-02 18:00이다.',
    'CQ1은 저장된 가장 최근 시각의 값을, CQ5는 문서 저장소에서 별표3 원문을 읽는다.')
figcap('q3', '운영 시각과 댐 코드로 측정 저장소의 한 행을 읽는다')
add(label('과정 5. 근거 묶음 (코드)'))
lis('조회 결과를 의도별 구역으로 나누고, 항목마다 출처 번호를 붙인다. 출처 번호는 KG의 Entity ID이고, 측정값은 [MEA:댐 코드:시각]이다.',
    '값은 저장소의 원값 그대로 쓰고 계산한 값은 넣지 않는다. 끝에 근거 사용 원칙 3문장을 붙인다.')
figcap('q4', '근거 묶음 — LLM에 주는 근거 전체')
add(label('과정 6. 답변 (LLM)'))
lis('LLM에 답변 지시문과 근거 묶음을 준다. 지시문: 근거 묶음에 있는 내용만 사실로 쓰고 출처 번호를 붙인다, 비교·해석은 "판단"으로 나누고 쓴 근거를 적는다, 없으면 "자료에 없음".',
    '주의 사항도 함께 준다: 운영행위 시각은 비고의 시각이거나 승인된 방류 시작 시각이다, "현재"는 저장된 가장 최근 시각이며 실시간이 아니다, 방류 사유는 자료에 없으므로 단정하지 않는다.')
figcap('q5', '답변 — 근거(출처 번호)와 판단(쓴 근거)으로 나뉜다')

add(label('결과'))
lis('질문마다 의도 원문, 의도 JSON, 조회 결과, 근거 묶음, 답변이 파일로 남는다. 서버에서 질문 5개를 실행한 결과는 표 4와 같다.')
add(label('표 4. 서버 실행 결과 (Qwen3-32B, 2026-10-16)'))
fmt_i = lambda t: ', '.join(t['intent_json'].get('intent') or []) or '없음 (거절)'
add(rtable([['질문', '뽑은 의도', '결과', '시간'],
            ['충주댐 현재 상태를 제한수위와 비교하고, 비슷한 수문 상태일 때의 승인·운영행위', fmt_i(TR['q1']), '근거와 판단으로 답함', '%.1f초' % TR['q1']['seconds']],
            ['소양강댐의 홍수기 제한수위와 그 근거', fmt_i(TR['q2']), '190.3 EL.m과 별표3 근거로 답함', '%.1f초' % TR['q2']['seconds']],
            ['2020년 8월 충주댐 승인·운영행위·수문 상태', fmt_i(TR['q3']), '4.2의 예', '%.1f초' % TR['q3']['seconds']],
            ['광동댐 제한수위', fmt_i(TR['q4']), '별표3에 없어 "자료에 없음"', '%.1f초' % TR['q4']['seconds']],
            ['팔당댐의 현재 수위', fmt_i(TR['q5']), '범위 밖 댐이라 질의 불가', '%.1f초' % TR['q5']['seconds']]],
           [4372, 1900, 2700, 1000]))

# ================================================================== 5. 검토할 점
add(h1('5. 검토할 점'))
add(label('1. authorizes는 연구용 구성 (Relation 채우기)'))
lis('운영행위가 승인 비고에서 구성한 것이므로, "그 승인이 그 운영행위를 허가했다"는 연결도 연구에서 정한 것이다. 실행을 확인한 연결이 아니다.',
    '답변 지시문에 "실제 수행이 확정된 것처럼 쓰지 않는다"를 넣어 다루고 있다. 실제 운영 기록을 얻으면 다시 정한다.')
add(label('2. 같은 코드를 같은 시설로 봄 (Relation 채우기)'))
lis('승인 파일의 관측소코드와 K-water 댐 코드가 같으면 같은 댐으로 보았다(4개 댐 모두 이름도 일치). 두 기관의 코드가 같은 시설을 뜻한다는 공식 자료로 확인하지는 않았다.',
    '별표3은 코드가 없어 이름으로 이었다(appliesToDam 3개).')
add(label('3. 답변 품질과 속도 (검색·답변, 서버 실행 기록)'))
lis('2020년 8월 질문의 판단에 "댐의 수문 상황과 유입량 변화에 따라 조정된 것으로 판단됩니다"처럼 자료에 없는 사유를 추정한 문장이 있다. 지시문의 "사유를 단정하지 않는다"를 어긴 것이다.',
    '광동댐 질문의 답변에서 출처 자리에 의도 이름([CQ5])을 적었다.',
    '같은 종합 질문을 5번 실행했을 때 CQ2(과거 상태)를 뽑은 것은 1번이었다. 의도 추출이 실행마다 다를 수 있다.',
    '종합 질문은 %.1f초 걸렸다. 첫 질문에서 측정 저장소(50만 행)를 읽는 시간이 들어 있다.' % TR['q1']['seconds'],
    '시연 전에 지시문을 고치고, 정해 둔 질문 세트로 반복해서 확인한다.')

# ================================================================== 6. 다음 계획
add(h1('6. 다음 계획'))
add(label('11/26 시연 구조'))
lis('이번에 정리한 검색·답변 구조를 그대로 쓰고, 처음 보는 사람이 직접 질문할 수 있도록 아래를 더한다.',
    '채팅 화면: 노트북 브라우저에서 질문하고 답변을 본다. 답변의 출처 번호를 누르면 원문(승인 기록 행, 별표3 원문, 측정값)이 보인다.',
    '답할 수 있는 범위 안내: 대상 댐 4개와 질문 종류(CQ1~CQ6), 예시 질문을 화면에 둔다. 범위 밖 질문과 인사에는 범위와 예시 질문으로 안내한다.',
    '이어지는 질문: "그럼 소양강댐은?"처럼 앞 질문의 댐·기간을 이어받는다.',
    '속도: 측정 저장소를 서버를 켤 때 미리 읽어 둔다.',
    '접속: 노트북 → 핫스팟 → 연구실 서버. 인터넷이 안 될 때를 대비해 시연 동영상을 찍어 둔다.',
    '시연 때 밝힐 점: "현재"는 저장된 마지막 시각(2026-09-28)이며 실시간이 아니다. 범용 LLM을 썼다. 실제 운영에 쓰려면 자료 연결 확대와 에이전트 등이 더 필요하다.')
add(label('11/20 발표 자료'))
lis('처음 보는 사람을 위한 설명 순서로 만든다: 왜 필요한가 → 무엇을 만들었나(온톨로지·KG) → 어떻게 답하나(이번 4장) → 시연 → 한계와 향후 계획.')
add(label('검증'))
lis('11/02 회의에 따라 다른 연구들의 KG·온톨로지 검증 방법을 조사해 분석한 뒤, 적용할 방안을 정리한다.')

# ================================================================== 부록
para = lambda t, sz=16: L.para(t, sz)
li = lambda t, sz=16: L.li(t, sz)
L.cell.__defaults__ = L.cell.__defaults__[:4] + (14,) + L.cell.__defaults__[5:]
L.table.__defaults__ = (True, True, 14, ())
table = L.table
add(h1('부록 A. 용어 정리'))
add(label('표 5. 용어 정의'))
add(table([['용어', '본 연구에서의 정의'],
           ['Relation 채우기', '온톨로지가 허락한 Class 사이의 관계 가운데, 자료 속 키로 Entity 사이의 실제 관계(시작 Entity → 끝 Entity)를 골라 잇는 일.'],
           ['개체 해소', '자료마다 다르게 적힌 같은 대상(충주, 충 주 댐, 1003110)을 하나의 기준 식별자에 대응시키는 일. 문헌의 entity disambiguation.'],
           ['기준 식별자', '같은 대상을 가리키는 표기들을 모으는 기준 ID. 본 연구는 K-water 댐 코드, GraphAide는 Wikidata의 QID.'],
           ['Neo4j', 'Entity와 Relation을 그래프(점과 선) 모양으로 저장하는 데이터베이스.'],
           ['Cypher', 'Neo4j에 Entity와 Relation을 넣고 찾을 때 쓰는 명령 문장. MERGE(없으면 만듦), MATCH(찾음), SET(값을 넣음) 등.'],
           ['조회 템플릿', 'CQ마다 미리 정해 둔 Cypher 문. 댐 이름과 기간만 바꿔 넣어 실행한다.'],
           ['의도', '질문이 요구하는 CQ(CQ1~CQ6). 한 질문에 여러 개가 있을 수 있다.'],
           ['근거 묶음', 'KG와 저장소에서 찾은 근거를 의도별 구역과 출처 번호를 붙여 LLM에 주는 글.'],
           ['출처 번호', '근거 항목마다 붙이는 표시. KG의 Entity ID이거나 측정값의 [MEA:댐 코드:시각].'],
           ['환각', 'LLM이 자료에 없는 사실을 지어내는 것.']], [1944, 8028], firstcol=True))
add(h1('부록 B. Ontology가 답해야 할 질문과 관계'))
add(label('표 6. 세부 질문 (CQ1~CQ6)'))
add(table([['번호', '질문 대상', '세부 질문'],
           ['CQ1', '현재 수문·기상 상태', '대상 댐의 현재 또는 기준시점의 강우, 수위, 유입량, 방류량 등 수문·기상 상태는 무엇인가?'],
           ['CQ2', '과거 수문·기상 상태', '선택된 과거 시점 또는 사례에서 대상 댐의 강우, 수위, 유입량, 방류량 등 수문·기상 상태는 어떠했는가?'],
           ['CQ3', '과거 운영행위', '해당 과거 시점 또는 사례에서 실제로 수행된 댐 운영행위는 무엇이었는가?'],
           ['CQ4', '과거 방류 승인', '해당 과거 시점 또는 사례에서 어떤 방류 승인이 있었으며, 그 승인내용은 무엇인가?'],
           ['CQ5', '현재 운영기준', '현재 대상 댐에 적용되는 운영기준은 무엇이며, 현재 운영 판단과 관련된 기준값은 무엇인가?'],
           ['CQ6', '공식 근거', '각 수문·기상 상태, 운영행위, 승인내용 및 운영기준을 확인할 수 있는 공식 자료 또는 근거문서는 무엇인가?']], [1000, 2200, 6772]))
add(label('표 7. Relation (9개)'))
add(table([['Subject', 'Relation', 'Object', '의미'],
           ['Dam', 'hasHydrometeorologicalState', 'HydrometeorologicalState', '댐이 해당 수문·기상 변수 정보와 연결됨'],
           ['Operation', 'performedOnDam', 'Dam', '운영행위가 특정 Dam에서 수행됨'],
           ['Approval', 'authorizes', 'Operation', 'Approval이 특정 Operation을 승인함'],
           ['Approval', 'concernsDam', 'Dam', 'Approval이 특정 Dam에 관한 것임'],
           ['Criterion', 'appliesToDam', 'Dam', '운영기준이 특정 Dam에 적용됨'],
           ['HydrometeorologicalState', 'supportedBy', 'EvidenceSource', '상태를 확인할 수 있는 근거자료'],
           ['Operation', 'supportedBy', 'EvidenceSource', '운영행위를 확인할 수 있는 근거자료'],
           ['Approval', 'supportedBy', 'EvidenceSource', '승인을 확인할 수 있는 근거자료'],
           ['Criterion', 'supportedBy', 'EvidenceSource', '운영기준을 확인할 수 있는 근거자료']], [2300, 2700, 2300, 2672]))
add(h1('부록 C. 근거 문헌의 원리'))
add(h2('C.1 Purohit 외(2024) — Relation 채우기(개체 해소), 검색·답변'))
lis('무엇인가: 여러 출처의 정형·비정형 자료로 KG를 만들고, 그 KG를 조회·추론하는 질의 시스템 GraphAide를 제안한 학회 논문이다(IEEE BigData 2024). OpenAI LLM, Chroma 벡터 DB, Neo4j, LangChain으로 구현했다.',
    'KG 생성 단계의 개체 해소: 기준 지식베이스로 DARPA Wikidata(DWD)를 쓰고, QID마다 설명 문서를 만들어 벡터 DB에 넣었다. 온톨로지와 DWD에 기반한 에이전트가 글에서 대상의 표기를 뽑고, RAG 기반 후보 재순위로 가장 가까운 QID를 고른다. → 기준 식별자에 대응시키는 원리만 따랐고, 벡터 DB와 LLM 재순위는 쓰지 않았다.',
    '질의 단계: LLM이 질문을 여러 형태로 확장하고, 이를 부분 그래프 조회 템플릿으로 바꿔 Cypher를 자동 생성한다. 그래프 조회 결과와 벡터 검색 결과를 합쳐 LLM의 맥락으로 주고, 답변을 모아 하나의 응답을 만든다. 정해진 순서(chain)와 에이전트를 함께 쓴다. → KG 조회 결과를 LLM의 근거로 주는 원리를 따랐고, Cypher는 CQ마다 미리 정한 템플릿으로 대신했다.',
    '평가: RAGAS 지표와 전문가 정성 평가를 쓴다고 밝혔으며, 정식 평가는 향후 과제로 두었다.')
add(h2('C.2 Huang 외(2026) — 저장'))
lis('추출한 지식을 JSON으로 통합하고, DDO의 의미·계층 관계에 따라 Python 스크립트가 JSON 키-값을 읽어 Cypher 문을 만든다. 이 문들로 DDKG의 Entity를 일괄 생성하고 Entity 사이의 관계를 만들어 Neo4j에 적재한다.',
    '저장소로 Neo4j를 고른 이유: Cypher로 조회·추가·삭제·수정이 효율적이고, 다중 홉 추론과 복잡한 질의에 강하다.',
    '구축한 DDKG는 Entity 201,362개, Relation 953,447개이다. → JSON 대신 CSV를 모은 형태로 쓴 것 외에는 같은 순서(모음 → 스크립트로 Cypher 생성 → 일괄 적재)를 따랐다.')
add(h1('부록 D. 참고문헌'))
lis('Huang, J., Hou, W., Zhang, S., Du, Z., & Yin, J. (2026). Dam defects ontology and knowledge graph construction from multi-source hazard data using large language models. Advanced Engineering Informatics, 76, 104987.',
    'Purohit, S., Chin, G., Mackey, P. S., & Cottam, J. A. (2024). GraphAide: Advanced Graph-Assisted Query and Reasoning System. 2024 IEEE International Conference on Big Data. https://doi.org/10.1109/BigData62323.2024.10825705')

body = re.sub(r'\{\{(\w+)\}\}', lambda mo: str(FIGNO[mo.group(1)]), ''.join(B))
T.save(OUT, body, L.IMGS, page_numbers=True)
print('saved', OUT, 'figs', len(FIGNO))
