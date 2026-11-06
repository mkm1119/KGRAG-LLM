#!/usr/bin/env python3
"""랩미팅 자료(docx): KG 구축 how (2) — Relation 채우기, 저장, 검색·답변.
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
    full = name in ('kg2_k1', 'kg2_c1', 'kg2_c2', 'kg2_s3', 'kg2_s2', 'kg2_r1', 'kg2_q1', 'kg2_q2', 'kg2_ap1')   # Entity가 많은 결과 KG와 Cypher 문이 든 그림은 쪽 너비 전체로
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


def cont(t):   # 앞 불렛에 이어지는 문단(불렛 없음)
    add('<w:p><w:pPr><w:spacing w:after="40"%s/><w:ind w:left="360"/><w:rPr>%s</w:rPr></w:pPr>%s</w:p>' % (LS, L.LANG, L.run(t, sz=19)))


rtable = lambda rows, widths: table(rows, widths, header=True, firstcol=False)

# ================================================================== 표지
add(title('KG 구축 how 보완', 'Relation 잇기 · 저장 · 검색·답변'))
add(subtitle('따른 문헌의 원리와 실제 수행 과정'))
add(dateline('2026.11 · 문경민'))

# ================================================================== 1. 현황
add(h1('1. KG 구축 단계와 방법론 구체화 현황'))
lis('KG 구축은 두 단계로 한다. 먼저 온톨로지의 Class와 Data Property에 맞춰 자료에서 실제값으로 Entity와 그 Data Property를 만들고, 다음에 만든 Entity들을 온톨로지의 Relation에 맞춰 이어 KG를 완성한다.',
    '10/30 자료에서 앞 단계를 정리했고, 그 결과 Entity 264개와 Data Property 값 616개가 만들어졌다. 이번 자료는 Entity를 Relation으로 잇는 과정(2장), 완성한 KG를 Neo4j에 넣는 저장(3장), KG로 질문에 답하는 검색·답변(4장)을 같은 방식(따른 원리 → 과정 → 결과)으로 정리했다.',
    '온톨로지의 CQ와 Relation은 부록 B, 10/30 자료까지의 결과는 부록 C, 각 원리의 자세한 설명은 부록 D에 있다.')
DONE, NOW, NEXT = 'E3F1DC', 'D6E8F7', 'FDEBD3'


def status_table():
    ws = [2100, 2900, 3172, 1800]
    rows = [('자료 준비', '소스 구분과 전처리', '—', '정리함 (10/30)', DONE),
            ('Class·Data Property 채우기', 'Entity와 속성값을 채움', '구조화 자료 매핑(정형 표), 비정형 텍스트 추출(비고, 별표3)', '정리함 (10/30)', DONE),
            ('Relation 잇기', '만든 Entity를 Relation마다 실제 시작·끝 Entity로 이음', '키로 이을 끝 Entity를 찾음(댐 표기 맞추기 포함)', '이번 (2장)', NOW),
            ('저장', '완성한 KG를 Neo4j에 넣음', 'CSV → Cypher → Neo4j', '이번 (3장)', NOW),
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
add(h1('2. Relation 잇기'))
add(h2('2.1 Relation 잇기란'))
lis('그림 {{r0}}의 왼쪽은 온톨로지의 Relation 정의 "Approval —concernsDam→ Dam"이다. 어느 승인이 어느 댐에 관한 것인지는 들어 있지 않다.',
    '오른쪽은 KG의 일부이다. 정의에 맞는 조합은 승인 80개 × 댐 4개 = 320가지이지만(회색 점선), 실제 Relation은 80개뿐이다. 승인 504행의 관측소코드 1003110이 충주댐의 댐 코드와 같으므로 APR:504를 DAM:1003110과 잇는다(실선).',
    'Entity와 Data Property 값만 있는 KG에는 선이 없어서 "충주댐의 승인"을 조회해도 아무것도 나오지 않는다. 이번 단계에서 Entity를 Relation으로 이어 KG를 완성한다.')
figcap('r0', '온톨로지의 Relation 정의에 맞는 조합(회색 점선) 가운데, 승인 기록의 관측소코드로 실제로 이을 댐(실선)을 찾는다')

add(h2('2.2 따른 원리와 진행 방식'))
lis('따른 원리(Purohit 외, 2024; 부록 D.1): 기준 식별자를 하나 정하고, 자료마다 다르게 적힌 같은 대상을 그 식별자에 대응시킨다. 우리는 K-water 댐 코드를 기준 식별자로 삼았고, 대상이 댐 4개라서 이번에는 코드 일치와 대응 표로 맞췄다.',
    '진행 방식: 댐 표기를 댐 코드에 맞춘 뒤, Relation마다 시작 Entity를 하나씩 읽고 키로 이을 끝 Entity를 찾아 Relation 한 줄을 쓴다. 키는 두 Entity가 같은 대상에 관한 것임을 알려 주는 값(승인 순차번호, 댐 코드, 댐 이름)이다.')

add(h2('2.3 댐 표기 맞추기 (개체 해소)'))
lis('그림 {{g1}}의 왼쪽은 충주댐이 자료마다 적힌 모습이다. ① 승인 기록의 관측소코드는 K-water 댐 코드와 같아서 그대로 맞춘다(자료 준비 때 4개 댐 모두 같음을 확인).',
    '② K-water 자료의 DAM_CD는 기준 식별자 자체이다.',
    '③ 규정 별표3에는 이름 "충 주 댐"뿐이라, 공백을 빼고 읽은 "충주댐"을 대응 표(4줄)에서 찾아 1003110을 얻는다. 광동댐은 별표3에 없다.',
    '결과: 세 표기가 모두 하나의 Entity DAM:1003110을 가리킨다.')
figcap('g1', '자료마다 다른 충주댐 표기 세 가지를 기준 식별자 DAM:1003110에 맞춘다')

add(h2('2.4 승인 기록 한 행으로 잇는 Relation'))
lis('그림 {{g0}}의 위쪽은 승인 기록 원본(CSV)의 504행이다. 범례처럼 회색 점선은 앞 단계에서 Entity를 만든 길, 파란 점선은 키 비교, 검은 실선은 이번에 이은 Relation이다.',
    '앞 단계에서 이 행으로 만든 APR:504, OPR:504:1, EVI:AP:504의 ID에는 모두 순차번호 504가 들어 있다. 그래서 ① APR:504 → OPR:504:1(authorizes), ② APR:504 → EVI:AP:504와 OPR:504:1 → EVI:AP:504(supportedBy)는 순차번호가 같은 것끼리 잇는다.')
cont('③ APR:504 → DAM:1003110(concernsDam)과 OPR:504:1 → DAM:1003110(performedOnDam)은 이 행의 관측소코드 1003110과 같은 댐 코드를 가진 DAM:1003110을 끝 Entity로 찾는다.')
lis('결과: 승인 80행에 같은 방법을 적용해 supportedBy 148개(승인 80, 운영행위 68), authorizes 68개, concernsDam 80개, performedOnDam 68개를 잇는다. 변경 승인 17개는 운영행위가 없어 authorizes가 없다.')
figcap('g0', '승인 504행 하나에서 잇는 Relation — 순차번호 504와 관측소코드 1003110으로 이을 Entity를 찾는다')

add(h2('2.5 댐 코드로 잇는 Relation'))
lis('그림 {{gB}}의 위쪽은 K-water 시간자료의 충주댐 한 행이다. 앞 단계에서 이 행으로 만든 HMS 6개와 EVI:KW:1003110, 일자료로 만든 DAM:1003110의 ID에 모두 댐 코드 1003110이 들어 있다.',
    '그래서 ① DAM:1003110 → HMS 6개(hasHydrometeorologicalState), ② HMS 6개 → EVI:KW:1003110(supportedBy)을 코드가 같은 것끼리 잇는다.',
    '결과: 4개 댐 × 6개 변수로 hasHydrometeorologicalState 24개, supportedBy 24개를 잇는다.')
figcap('gB', '댐 코드로 잇는 Relation — 같은 코드 1003110을 가진 Dam, HMS, 측정자료 근거를 잇는다')

add(h2('2.6 별표3 댐 이름으로 잇는 Relation'))
lis('그림 {{gC}}의 위쪽은 별표3에서 추출한 중간 파일 criterion_list.csv의 한 줄이고, 앞 단계에서 이 줄로 CRI:CR-02를 만들었다.',
    '별표3에는 댐 코드가 없어 ① 댐 이름 "충주댐"을 대응 표에서 찾아 1003110을 얻고, ② CRI:CR-02 → DAM:1003110(appliesToDam)을 쓴다. 이름으로 찾았다는 표시(name-match)를 Relation에 남긴다.',
    '③ 규정이 하나라 근거 Entity도 EVI:LAW:별표3 하나이고, 기준 3개 모두 이것과 잇는다(supportedBy).',
    '결과: appliesToDam 3개(충주, 소양강, 횡성), supportedBy 3개를 잇는다.')
figcap('gC', '별표3 댐 이름으로 잇는 Relation — 이름을 대응 표로 댐 코드에 맞춘다')

add(h2('2.7 결과: Relation을 이은 CSV'))
lis('실제 Relation %d개가 kgv4_relations.csv에 한 줄씩 쓰였다(그림 {{r1}}). 한 줄은 시작 Entity(subject), Relation 이름(relation), 끝 Entity(object), 끝 Entity를 찾은 방법의 이름(rule), 원본의 키로 바로 이었는지 표시(origin), 설명(note)이다.' % len(rels),
    '이로써 KG에 들어갈 내용이 CSV 파일 세 개(kgv4_entities, kgv4_properties, kgv4_relations)에 모두 담겼다.',
    '연결 확인: 4개 댐 전체에서 승인 80개 모두 댐과 근거에, 운영행위 68개 모두 댐·승인·근거에, HMS 24개 모두 댐과 근거에, 기준 3개 모두 댐과 근거에 이어졌다. 승인 중 운영행위로 이어진 것은 63개이며, 나머지 17개는 변경 승인이다.')
figcap('r1', 'kgv4_relations.csv의 실제 줄 — 충주댐 Entity 몇 개가 시작인 줄 14개')

# ================================================================== 3. 저장
add(h1('3. 저장'))
add(h2('3.1 따른 원리와 진행 방식'))
lis('따른 원리(Huang 외, 2026; 부록 D.2): 모은 자료를 Python 스크립트가 읽어 Cypher 문을 만들고 Neo4j에 한꺼번에 넣는다. 우리는 JSON 대신 2장까지 만든 CSV 세 개를 읽어 Cypher 문을 쓰고, 그 문을 모은 파일을 Neo4j에서 실행했다.',
    '따른 원리(Zhou 외, 2023; 부록 D.3): 데이터는 원래 저장소에 두고 키로 KG와 대응시켜, 질의할 때 그 행을 읽어 온다. 우리는 시간별 측정값과 규정 원문을 KG 밖 CSV에 두고, KG에는 그 행을 찾을 키만 두었다. 출처 파일(kgv4_provenance)도 CSV로 둔다.',
    '진행 방식: Neo4j는 Entity와 Relation을 그래프(점과 선)로 저장하는 데이터베이스이고, Cypher는 Neo4j에 넣고 찾을 때 쓰는 명령 문장이다. CSV는 줄의 목록이라 관계를 따라가는 질의를 바로 할 수 없어서, Entity, Relation 순서로 Cypher 문을 써서 Neo4j에 넣는다.')

add(h2('3.2 CSV → Cypher → Neo4j'))
add(label('과정 1. Entity를 Cypher 문으로 쓰고 Neo4j에 넣기'))
lis('원리: Entity 하나가 Cypher 문 하나가 되고, 실행하면 Neo4j에 Entity 하나가 Class와 Data Property 값을 가진 채 생긴다.',
    '그림 {{c1}}의 맨 위는 kgv4_entities.csv와 kgv4_properties.csv의 APR:504 줄이며, 화살표를 따라 각 열의 값이 가운데 틀의 { } 자리에 들어간다. datatype이 date이면 값을 date( )로 감싸 날짜로 넣어, "2020년 8월 안"처럼 기간으로 비교해 찾을 수 있게 한다.',
    'MERGE는 Entity가 없을 때만 만들어서, 같은 문을 다시 실행해도 APR:504가 둘이 되지 않는다. %d개 Entity마다 이런 문이 하나씩 쓰인다.' % len(ents))
figcap('c1', '과정 1 — CSV 열의 값이 Cypher 문의 자리로 들어가고, 실행하면 Neo4j에 Entity가 생긴다 (APR:504)')
add(label('과정 2. Relation을 Cypher 문으로 쓰고 Neo4j에 넣기'))
lis('원리: Relation 하나가 Cypher 문 하나가 된다. 문은 Neo4j에 이미 있는 두 Entity를 찾고 그 사이에 Relation을 만든다.',
    '그림 {{c2}}의 맨 위는 kgv4_relations.csv의 한 줄이다. Relation은 Neo4j 안의 두 Entity 사이에 긋는 것이라, 과정 1의 Entity 문이 먼저 실행되어 있어야 한다. %d개 Relation마다 이런 문이 하나씩 쓰인다.' % len(rels))
figcap('c2', '과정 2 — 관계 CSV 한 줄이 Cypher 문이 되고, 실행하면 두 Entity 사이에 Relation이 생긴다')
add(label('과정 3. Cypher 문을 모아 Neo4j에서 실행하기'))
lis('원리: 과정 1·2의 문을 파일 하나(kgv4_load.cypher, %d줄)에 모아 Neo4j가 위에서부터 한 번에 실행한다. Relation 문은 Entity를 찾아야 하므로 Entity 문 뒤에 둔다(그림 {{s3}} 왼쪽).' % CYPHER_LINES,
    '실행할 때는 Neo4j를 비운 뒤 파일 전체를 다시 넣는다(오른쪽). MERGE는 없는 것을 더할 뿐 CSV에서 지운 줄을 Neo4j에서 지우지 않으므로, 비우지 않으면 CSV에서 지운 Relation이 Neo4j에 남는다. 마지막에 센 수(%d, %d)가 CSV의 줄 수와 같으면 Neo4j의 KG가 CSV와 같다.' % (len(ents), len(rels)))
figcap('s3', '과정 3 — Cypher 파일의 구성과 실행 순서')

add(h2('3.3 KG 밖에 두는 것: 측정 저장소와 문서 저장소'))
lis('시간별 측정값(508,246행)과 규정 원문은 CSV로 두고, KG에는 그 행을 찾을 키만 Data Property로 둔다. 조회할 때 코드가 이 키로 CSV의 행을 읽는다.',
    '그림 {{s2}}의 위는 측정 저장소이다. HMS:1003110:수위의 stationCode와 찾을 시각으로 DAM_CD와 SDATE_raw가 같은 행을 찾으면, DATA1_수위 열이 그 시각의 수위(139.55 EL.m)이다. 아래는 문서 저장소이며, EVI:LAW:별표3의 sourceLocator로 규정 원문의 행을 찾는다.')
figcap('s2', '외부 저장소 CSV의 실제 모습과, KG의 값으로 행을 찾는 방법')

add(h2('3.4 결과: Neo4j에 저장된 KG'))
lis('Neo4j에 Entity %d개와 Relation %d개가 저장되었다. 그림 {{k1}}은 그중 충주댐의 Entity 53개와 Relation이다.' % (len(ents), len(rels)),
    '왼쪽 세 점선 상자는 승인자료 근거 15, 승인 15, 운영행위 14개이며 한 줄이 승인 한 건이다. 3519와 3647은 변경 승인이라 운영행위가 없다.')
figcap('k1', 'Neo4j에 저장된 KG(충주댐 Entity 53개)와 외부 저장소로 가는 길')

# ================================================================== 4. 검색·답변
add(h1('4. 검색·답변'))
add(h2('4.1 따른 원리와 진행 방식'))
lis('따른 원리(Purohit 외, 2024; 부록 D.1): KG를 조회한 결과를 LLM에 근거로 주어 답변을 만들어, LLM이 자료에 없는 사실을 지어내는 것(환각)을 줄인다. 우리는 이번 시험에서 조회 템플릿을 CQ마다 미리 정해 두고, LLM은 질문에서 의도(CQ1~CQ6)와 값(댐, 기간)만 뽑게 했다.',
    '진행 방식: 의도·값 추출(LLM) → 입력 확인(코드) → KG 검색과 외부 저장소 조회(코드) → 근거 묶음(코드) → 답변(LLM)의 다섯 과정이다. LLM은 처음과 마지막에만 쓴다(같은 모델 Qwen3-32B-AWQ, 지시문만 다름).',
    '아래에서는 서버에서 실행한 질문 하나(2026-10-16)를 따라간다.')

add(h2('4.2 질문에서 근거 묶음까지'))
add(label('입력'))
lis('질문: "%s"' % TR['q3']['question'])
add(label('과정 1. 의도·값 추출 (LLM)'))
lis('원리: LLM은 지시문(그림 {{q1}} 가운데)에 정해 둔 의도 목록과 허용되는 댐 안에서만 고르고, 값은 Cypher 템플릿에 그대로 넣을 수 있는 형식으로 적는다.',
    '화살표처럼 "그때의 수문 상태"는 CQ2, "운영행위"는 CQ3, "방류 승인"은 CQ4가 되고, "2020년 8월"은 2020-08-01 ~ 2020-08-31이 된다. 아래의 "%s"는 팔당댐이 허용되는 댐에 없어 규칙 4에 따라 intent가 비고, KG를 조회하지 않는다.' % TR['q5']['question'])
figcap('q1', '의도·값 추출 — 질문 속 표현을 지시문의 의도 목록, 허용되는 댐, 값의 형식에 맞춰 JSON으로 적는다')
add(label('과정 2. 입력 확인 (코드)'))
lis('의도가 CQ1~CQ6 안인지, 댐이 4개 댐 안인지 확인하고 이름을 표준 댐명으로 바꾼다("충주" → 충주댐).',
    '기간의 끝 날짜는 그 날 전체로 읽어 [2020-08-01 00:00, 2020-09-01 00:00)으로 바꾼다. 확인을 통과하지 못하면 조회하지 않고 "질의 불가: 이유"를 답변 과정으로 넘긴다.')
add(label('과정 3. KG 검색과 외부 저장소 조회 (코드)'))
lis('원리: 고른 의도마다 미리 정한 Cypher 템플릿에 댐 이름과 기간만 넣어 실행한다. 템플릿은 KG의 Relation을 따라가고, 측정값과 원문은 KG의 키로 외부 저장소에서 가져온다.',
    '그림 {{q2}}에서 댐 코드 템플릿은 hasHydrometeorologicalState를 따라 stationCode 1003110을 얻는다. CQ4 템플릿은 concernsDam으로 이어진 승인 15개 가운데 기간 안의 APR:3412, APR:3519, APR:3647을, CQ3 템플릿은 performedOnDam으로 이어진 운영행위 가운데 OPR:3412:1과 그것을 허가한 APR:3412(authorizes)를 찾는다.',
    'CQ2는 운영행위의 시각마다 측정 저장소에서 stationCode와 operationTime(2020080218)이 같은 행을 읽는다. 정각이 아닌 시각은 앞뒤 정시 두 행을 읽는다.',
    '다른 의도가 있는 질문은 표 2의 경로를 따른다.')
figcap('q2', 'KG 검색과 외부 저장소 조회 — 템플릿이 따라가는 Relation과 기간 조건, KG의 값으로 찾는 측정 저장소의 행')
add(label('표 2. 의도별 Cypher 템플릿이 따라가는 Relation과 외부 저장소'))
add(rtable([['의도', '따라가는 Relation (Cypher 템플릿)', '외부 저장소'],
            ['CQ1 현재 상태', 'Dam → hasHydrometeorologicalState → HMS (stationCode)', '측정: 저장된 가장 최근 시각의 행'],
            ['CQ2 과거 상태', '(CQ3과 함께면) 운영행위의 operationTime', '측정: 그 시각의 행, CQ3이 없으면 기간 안의 행'],
            ['CQ3 운영행위', 'Operation → performedOnDam → Dam, Approval → authorizes → Operation', '—'],
            ['CQ4 승인', 'Approval → concernsDam → Dam', '—'],
            ['CQ5 운영기준', 'Criterion → appliesToDam → Dam, Criterion → supportedBy → EvidenceSource', '문서: sourceLocator의 원문'],
            ['CQ6 근거', '조회한 Entity → supportedBy → EvidenceSource', '—']],
           [1700, 5272, 3000]))
add(label('과정 4. 근거 묶음 (코드)'))
lis('조회 결과를 의도별 구역으로 나누고, 항목마다 출처 번호를 붙인다. 출처 번호는 KG의 Entity ID이고, 측정값은 [MEA:댐 코드:시각]이다.',
    '값은 저장소의 원값 그대로 쓰고 계산한 값은 넣지 않는다. 끝에 근거 사용 원칙 3문장을 붙인다.')
figcap('q4', '근거 묶음 — LLM에 주는 근거 전체')
add(label('과정 5. 답변 (LLM)'))
lis('LLM에 답변 지시문과 근거 묶음을 준다. 지시문: 근거 묶음에 있는 내용만 사실로 쓰고 출처 번호를 붙인다, 비교·해석은 "판단"으로 나누고 쓴 근거를 적는다, 없으면 "자료에 없음".',
    '주의 사항도 함께 준다: 운영행위 시각은 비고의 시각이거나 승인된 방류 시작 시각이다, "현재"는 저장된 가장 최근 시각이며 실시간이 아니다, 방류 사유는 자료에 없으므로 단정하지 않는다.')

add(h2('4.3 결과: 답변'))
lis('그림 {{q5}}가 이 질문의 답변이다. "근거"에는 승인 세 건의 방류량과 기간이 [APR:3412], [APR:3519], [APR:3647]과 함께, 방류 시작 시각의 수문 상태가 [MEA:1003110:2020080218]과 함께 쓰여 있다.',
    '"판단"에는 방류량이 3000㎥/s에서 7000㎥/s로 늘고 기간이 연장되었다는 비교가 쓴 근거와 함께 있다. 빨간 글씨 문장은 자료에 없는 사유를 추정한 것으로, 지시문의 "사유를 단정하지 않는다"를 어겼다.',
    '근거 묶음의 운영행위 [OPR:3412:1]은 답변에 출처 번호로 쓰이지 않았다.')
figcap('q5', '답변 — 근거(출처 번호)와 판단(쓴 근거)으로 나뉜다')

# ================================================================== 5. 검토할 점과 다음 계획
add(h1('5. 검토할 점과 다음 계획'))
add(label('1. 답할 수 있는 질문의 범위 (온톨로지, 검색·답변)'))
lis('온톨로지는 CQ1~CQ6에 답할 수 있는 구조로 만들었고, 검색은 CQ마다 정한 Cypher 템플릿으로 한다(4장). 그래서 지금 구조는 질문의 의도가 CQ1~CQ6에 해당할 때만 답할 수 있다.',
    '의도 목록에 없는 질문은 과정 1에서 intent가 비어 조회하지 않는다. 예: 방류 사유를 묻는 질문, 4개 댐 밖의 댐이나 두 댐을 함께 묻는 질문.')
add(label('2. 과제 발표와 시연'))
lis('11/20 과제 발표와 11/26 시연은 지금 구조(4장)로 한다.')
add(label('3. 연구'))
lis('온톨로지 생성 방식을 다시 검토한다.',
    '검색·답변과 검증에 대한 선행 논문을 더 찾아 읽고 지금 방법과 비교한 뒤, 더 좋은 결과를 내는 방법을 적용한다. 검증은 11/02 회의에 따라 다른 연구들이 KG·온톨로지를 어떻게 검증했는지부터 조사한다.')

# ================================================================== 부록
para = lambda t, sz=16: L.para(t, sz)
li = lambda t, sz=16: L.li(t, sz)
L.cell.__defaults__ = L.cell.__defaults__[:4] + (14,) + L.cell.__defaults__[5:]
L.table.__defaults__ = (True, True, 14, ())
table = L.table
add(h1('부록 A. 용어 정리'))
add(label('표 3. 용어 정의'))
add(table([['용어', '본 연구에서의 정의'],
           ['Relation 잇기', '온톨로지의 Relation 정의에 맞는 Class 사이의 조합 가운데, 키로 실제로 이어질 Entity 쌍(시작 Entity → 끝 Entity)을 찾아 잇는 일.'],
           ['키', '두 자료나 두 Entity가 같은 대상에 관한 것임을 알려 주는 값. 예: 승인 순차번호 504, 댐 코드 1003110. Relation을 이을 때와 외부 저장소에서 행을 찾을 때 같은 뜻으로 쓴다.'],
           ['시작·끝 Entity', 'Relation 한 줄의 출발점과 도착점. "APR:504 —concernsDam→ DAM:1003110"에서 APR:504가 시작 Entity, DAM:1003110이 끝 Entity.'],
           ['개체 해소', '자료마다 다르게 적힌 같은 대상(충주, 충 주 댐, 1003110)을 하나의 기준 식별자에 대응시키는 일. 문헌의 entity disambiguation.'],
           ['기준 식별자', '같은 대상을 가리키는 표기들을 모으는 기준 ID. 본 연구는 K-water 댐 코드, GraphAide는 Wikidata의 QID.'],
           ['Neo4j', 'Entity와 Relation을 그래프(점과 선) 모양으로 저장하는 데이터베이스.'],
           ['Cypher', 'Neo4j에 Entity와 Relation을 넣고 찾을 때 쓰는 명령 문장. MERGE(없으면 만듦), MATCH(찾음), SET(값을 넣음) 등.'],
           ['지시문', 'LLM에 질문과 함께 주는 지침 글(프롬프트). 의도·값 추출용과 답변용이 따로 있다.'],
           ['조회 템플릿', 'CQ마다 미리 정해 둔 Cypher 문. 댐 이름과 기간만 바꿔 넣어 실행한다.'],
           ['의도', '질문이 요구하는 CQ(CQ1~CQ6). 한 질문에 여러 개가 있을 수 있다.'],
           ['근거 묶음', 'KG와 저장소에서 찾은 근거를 의도별 구역과 출처 번호를 붙여 LLM에 주는 글.'],
           ['출처 번호', '근거 항목마다 붙이는 표시. KG의 Entity ID이거나 측정값의 [MEA:댐 코드:시각].'],
           ['환각', 'LLM이 자료에 없는 사실을 지어내는 것.']], [1944, 8028], firstcol=True))
add(h1('부록 B. Ontology가 답해야 할 질문과 관계'))
add(label('표 4. 세부 질문 (CQ1~CQ6)'))
add(table([['번호', '질문 대상', '세부 질문'],
           ['CQ1', '현재 수문·기상 상태', '대상 댐의 현재 또는 기준시점의 강우, 수위, 유입량, 방류량 등 수문·기상 상태는 무엇인가?'],
           ['CQ2', '과거 수문·기상 상태', '선택된 과거 시점 또는 사례에서 대상 댐의 강우, 수위, 유입량, 방류량 등 수문·기상 상태는 어떠했는가?'],
           ['CQ3', '과거 운영행위', '해당 과거 시점 또는 사례에서 실제로 수행된 댐 운영행위는 무엇이었는가?'],
           ['CQ4', '과거 방류 승인', '해당 과거 시점 또는 사례에서 어떤 방류 승인이 있었으며, 그 승인내용은 무엇인가?'],
           ['CQ5', '현재 운영기준', '현재 대상 댐에 적용되는 운영기준은 무엇이며, 현재 운영 판단과 관련된 기준값은 무엇인가?'],
           ['CQ6', '공식 근거', '각 수문·기상 상태, 운영행위, 승인내용 및 운영기준을 확인할 수 있는 공식 자료 또는 근거문서는 무엇인가?']], [1000, 2200, 6772]))
add(label('표 5. Relation (9개)'))
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
EVC = collections.Counter(e['entity_id'].split(':')[1] for e in ents if e['class'] == 'EvidenceSource')
assert EVC == {'AP': 80, 'KW': 4, 'LAW': 1}, EVC
PC = collections.Counter(cls[p['entity_id']] if cls[p['entity_id']] != 'EvidenceSource' else 'EVI:' + p['entity_id'].split(':')[1] for p in props)
assert sum(PC.values()) == 616 and RC['supportedBy'] == 175
add(h1('부록 C. 10/30 자료까지의 결과: 자료 준비, Class·Data Property 채우기'))
lis('자료 준비: 승인 기록 3,929행에서 중복 7행을 지우고 대상 4개 댐의 80행을 남겼다. K-water 시간자료 두 파일을 이어 붙여 4개 댐의 508,246행을 측정 저장소에, 규정 XML에서 꺼낸 별표3 원문을 문서 저장소에 두었다.',
    'Class·Data Property 채우기: 정형 표는 구조화 자료 매핑으로, 승인 비고와 별표3은 비정형 텍스트 추출로 Entity와 속성값을 만들었다. 그림 {{ap1}}은 충주댐에 관한 실제 Entity를 자료마다 하나씩 보인 것이다. 결과는 kgv4_entities.csv(Entity %d개)와 kgv4_properties.csv(속성값 %d개)이다.' % (len(ents), len(props)),
    '이 단계에서 이어진 Relation은 같은 행·같은 자료에서 함께 만든 근거(supportedBy) %d개뿐이었다. 나머지 Relation %d개를 2장에서 이었다.' % (RC['supportedBy'], NEW))
figcap('ap1', '10/30 자료까지 만든 Entity — 자료마다 충주댐의 실제 Entity 하나와 그 Data Property 값')
add(h1('부록 D. 근거 문헌의 원리'))
add(h2('D.1 Purohit 외(2024) — Relation 잇기(개체 해소), 검색·답변'))
lis('무엇인가: 여러 출처의 정형·비정형 자료로 KG를 만들고, 그 KG를 조회·추론하는 질의 시스템 GraphAide를 제안한 학회 논문이다(IEEE BigData 2024). OpenAI LLM, Chroma 벡터 DB, Neo4j, LangChain으로 구현했다.',
    'KG 생성 단계의 개체 해소: 기준 지식베이스로 DARPA Wikidata(DWD)를 쓰고, QID마다 설명 문서를 만들어 벡터 DB에 넣었다. 온톨로지와 DWD에 기반한 에이전트가 글에서 대상의 표기를 뽑고, RAG 기반 후보 재순위로 가장 가까운 QID를 고른다. → 기준 식별자에 대응시키는 원리를 적용했다. 대상이 댐 4개라 이번에는 코드 일치와 대응 표로 했고, 벡터 DB와 LLM 재순위는 대상과 자료가 늘어날 때 적용을 검토한다.',
    '질의 단계: LLM이 질문을 여러 형태로 확장하고, 이를 부분 그래프 조회 템플릿으로 바꿔 Cypher를 자동 생성한다. 그래프 조회 결과와 벡터 검색 결과를 합쳐 LLM의 맥락으로 주고, 답변을 모아 하나의 응답을 만든다. 정해진 순서(chain)와 에이전트를 함께 쓴다. → 이번 시험에는 KG 조회 결과를 LLM의 근거로 주는 원리를 적용하고 Cypher는 CQ마다 미리 정한 템플릿을 썼다. 질의 확장, Cypher 자동 생성, 벡터 검색, 에이전트는 답할 수 있는 질문의 범위를 넓힐 때 적용을 검토한다.',
    '평가: RAGAS 지표와 전문가 정성 평가를 쓴다고 밝혔으며, 정식 평가는 향후 과제로 두었다.')
add(h2('D.2 Huang 외(2026) — 저장'))
lis('추출한 지식을 JSON으로 통합하고, DDO의 의미·계층 관계에 따라 Python 스크립트가 JSON 키-값을 읽어 Cypher 문을 만든다. 이 문들로 DDKG의 Entity를 일괄 생성하고 Entity 사이의 관계를 만들어 Neo4j에 적재한다.',
    '저장소로 Neo4j를 고른 이유: Cypher로 조회·추가·삭제·수정이 효율적이고, 다중 홉 추론과 복잡한 질의에 강하다.',
    '구축한 DDKG는 Entity 201,362개, Relation 953,447개이다. → JSON 대신 CSV를 모은 형태로 쓴 것 외에는 같은 순서(모음 → 스크립트로 Cypher 생성 → 일괄 적재)를 따랐다.')
add(h2('D.3 Zhou 외(2023) — KG 밖에 두는 저장소'))
lis('무엇인가: 댐 안전 모니터링을 위한 BIM·온톨로지 기반 지식관리 저널 논문이다(Automation in Construction). OntoDSMS는 이 논문이 만든 댐 안전 모니터링 시스템(DSMS) 도메인 온톨로지의 이름이고, D2RQ는 이 논문이 쓴 기존 오픈소스 도구이다.',
    '데이터를 원래 저장소에 둠: D2RQ는 관계형 DB에 접근하는 가상 RDF 그래프를 제공하며, RDB의 내용을 RDF 저장소에 복제하지 않고 RDF로 접근하게 한다(원문 6쪽).',
    '키로 대응: 매핑 파일에서 표의 ID 열 값으로 인스턴스 식별자를 만들고(uriPattern), 표는 Class, 열은 DatatypeProperty, 행은 인스턴스, 셀은 값에 대응시킨다(원문 6쪽 그림 3, 7쪽).',
    '질의할 때 읽어 옴: D2RQ는 RDF 질의를 SQL 문으로 번역해 RDB에서 실행한다(원문 7쪽). 이력 데이터와 실시간 수집 데이터를 MySQL에 둔 채 온톨로지와 대응시켰고(원문 10쪽), 질의 1에서 4번 구간 수직 변위 센서의 2015-2-28 이후 모니터링 데이터를 조회했다.',
    '→ 데이터를 원래 저장소에 두고 키로 KG와 이어 질의할 때 읽어 오는 원리를 따랐다. 매핑 파일과 SQL 번역 대신, KG에서 키를 얻은 뒤 코드가 CSV에서 행을 찾는다.')
add(h1('부록 E. 참고문헌'))
lis('Huang, J., Hou, W., Zhang, S., Du, Z., & Yin, J. (2026). Dam defects ontology and knowledge graph construction from multi-source hazard data using large language models. Advanced Engineering Informatics, 76, 104987.',
    'Purohit, S., Chin, G., Mackey, P. S., & Cottam, J. A. (2024). GraphAide: Advanced Graph-Assisted Query and Reasoning System. 2024 IEEE International Conference on Big Data. https://doi.org/10.1109/BigData62323.2024.10825705',
    'Zhou, Y., Bao, T., Shu, X., Li, Y., & Li, Y. (2023). BIM and ontology-based knowledge management for dam safety monitoring. Automation in Construction, 145, 104649.')

body = re.sub(r'\{\{(\w+)\}\}', lambda mo: str(FIGNO[mo.group(1)]), ''.join(B))
T.save(OUT, body, L.IMGS, page_numbers=True)
print('saved', OUT, 'figs', len(FIGNO))
