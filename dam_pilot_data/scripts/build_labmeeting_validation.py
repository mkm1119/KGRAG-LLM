#!/usr/bin/env python3
"""랩미팅 자료(docx): 온톨로지 설계 방법 검토와 검증 방법.
서식은 11/06 자료(build_labmeeting_how_kg2.py)와 같다(labdoc_lib, 같은 템플릿).
근거 문헌: references/evidence_literature/ (해설: lab_meeting/paper_review/검증부분_해석6, 해석7)
11/12 16차: 2장 온톨로지의 검증(문헌이 말한 확인 → CQ를 우리가 만든 문제 → 지금까지 한 CQ 확인 → CQ를 늘려 전문가에게 검토받고 온톨로지를 넓히는 방안). 부록은 연구 구조.
1장 온톨로지 설계 방법 검토, 2장 검증의 문제와 요구사항(KG 구축 리뷰), 3장 품질 평가(차원, 방법, 우리 KG의 지금 상태),
4장 품질 개선, 5장 전문가 검토를 평가와 개선에 쓰는 방법, 6장 다음 계획,
부록 A 실행한 평가의 상세 결과, 부록 B 전문가 검토지 초안.
수치는 step6_validate.py, step13_source_cq_check.py의 출력 CSV와 원본 승인 CSV에서 읽는다.
본문의 {키}는 처음 나온 순서대로 [번호]로 바뀐다(참고문헌 번호와 같음).
사용: python3 scripts/build_labmeeting_validation.py <출력 docx>
"""
import importlib.util, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('L', os.path.join(HERE, 'labdoc_lib.py')); L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
_li, _para = L.li, L.para
LS = ' w:line="252" w:lineRule="auto"'
L.li = lambda t, sz=19: _li(t, sz).replace('<w:spacing w:after="60"/>', '<w:spacing w:after="40"%s/>' % LS, 1)
L.para = lambda t, sz=19: _para(t, sz).replace('w:after="120"/>', 'w:after="100"%s/>' % LS, 1)
L.cell.__defaults__ = L.cell.__defaults__[:4] + (17,) + L.cell.__defaults__[5:]
L.table.__defaults__ = (True, True, 17, ())
_h1 = L.h1
L.h1 = lambda t, pagebreak=False: _h1(t, pagebreak).replace('<w:pStyle w:val="1"/>', '<w:pStyle w:val="1"/><w:spacing w:before="280" w:after="40"/>', 1)
L.label = lambda t: '<w:p><w:pPr><w:keepNext/><w:spacing w:before="140" w:after="20"/><w:rPr>%s</w:rPr></w:pPr>%s</w:p>' % (L.LANG, L.run(t, sz=22, b=True, color='1F4E79'))
for n in ('title', 'subtitle', 'dateline', 'label', 'h1', 'h2', 'para', 'li', 'spacer', 'table'):
    globals()[n] = getattr(L, n)

ROOT = os.path.join(HERE, '..')
LAB = os.path.join(ROOT, '..', 'lab_meeting')
OUT = sys.argv[1]
T = L.Template(os.path.join(LAB, '랩미팅 자료_KG구축_검색답변_최종.docx'))

# ------------------------------------------------------------------ 사실: 검사 결과(출력 CSV)와 KG 크기
import collections, csv
N3 = os.path.join(ROOT, '03_normalized')
rd = lambda p: list(csv.DictReader(open(os.path.join(N3, p), encoding='utf-8-sig')))
V = {r['id']: r for r in rd('step6_validation.csv')}
S = {r['id']: r for r in rd('step13_source_cq_check.csv')}
assert all(V[k]['result'] == '통과' and V[k]['count'] == '0' for k in ('V1', 'V2', 'V3', 'V4', 'V5'))
assert V['V9']['count'] == '63/80' and V['V10']['count'] == '80/80'
N_ENT, N_REL = len(rd('kgv4_entities.csv')), len(rd('kgv4_relations.csv'))
assert (N_ENT, N_REL) == (264, 418)
assert all(r['result'] == '일치' for k, r in S.items() if k not in ('S7b', 'S8', 'R1', 'R2'))
assert (S['S9']['kg'], S['S10']['kg'], S['R1']['expected'], S['R1']['kg'], S['R2']['kg']) == ('4', '3', '68', '65', '11')
assert (S['S1']['kg'], S['S7']['kg'], S['S7b']['kg'], S['S8']['kg'], S['C6']['kg']) == ('80', '65', '3', '68', '175')
OPS = rd('operation_from_remarks_5dams.csv')
RULE = collections.Counter(o['rule'] for o in OPS if o['operation_created'] == 'Y')
N_CHG = sum(o['operation_created'] == 'N' for o in OPS)
assert sum(RULE.values()) == 68 and N_CHG == 17 and len(RULE) == 9
DAMS = ['충주댐', '소양강댐', '횡성댐', '광동댐']
# 범위를 넓힐 후보 질문: 업무 질문 82개 가운데 온톨로지 확장이 필요하다고 분류한 것(O1~O4)
Q82 = {q['id']: q for q in json.load(open(os.path.join(ROOT, '05_retrieval', 'question_set_tasks82.json'), encoding='utf-8'))}
NQ = collections.Counter(q['expect'] for q in Q82.values())
assert len(Q82) == 82 and (NQ['answer_now'], NQ['extend'], NQ['refuse']) == (13, 36, 33)
NX = collections.Counter(q['extension'] for q in Q82.values() if q['expect'] == 'extend')
assert (NX['O1'], NX['O2'], NX['O3'], NX['O4']) == (4, 2, 4, 1)
def QX(i, t, e):
    assert Q82[i]['question'] == t and Q82[i]['extension'] == e, i
    return t
cq = lambda c, d: '%s / %s' % (S['%s-%s' % (c, d)]['kg'], S['%s-%s' % (c, d)]['expected'])

# 후보 규칙에 걸린 운영행위와 그 승인(원본 승인 CSV에서 읽음)
_raw = {r['순차번호']: r for r in csv.DictReader(open(os.path.join(ROOT, '01_raw', 'FloodControl', '환경부_한강홍수통제소_홍수예보_댐방류승인_20220727.csv'), encoding='cp949'))}
assert len(_raw) == 3929
_pp = collections.defaultdict(dict)
for _r in rd('kgv4_properties.csv'):
    _pp[_r['entity_id']][_r['property']] = _r['value']
EARLY = sorted((r['subject'], r['object']) for r in rd('kgv4_relations.csv') if r['relation'] == 'authorizes' and _pp[r['object']]['operationTime'][:10] < _pp[r['subject']]['approvalTime'])
assert EARLY == [('APR:2866', 'OPR:2866:1'), ('APR:2866', 'OPR:2866:2'), ('APR:3091', 'OPR:3091:1')]
for _late, _first in (('2866', '2713'), ('3091', '3052')):  # 같은 댐, 같은 방류시작시간, 앞선 승인에서 이미 운영행위를 만듦
    assert _raw[_late]['관측소코드'] == _raw[_first]['관측소코드'] and _raw[_late]['방류시작시간'] == _raw[_first]['방류시작시간']
    assert _raw[_first]['승인년월일시분'] < _raw[_late]['승인년월일시분'] and ('OPR:%s:1' % _first) in _pp
assert (_pp['APR:2866']['approvalTime'], _pp['OPR:2866:1']['operationTime'], _pp['OPR:2866:1']['operationType'], _pp['OPR:2866:2']['operationType']) == ('2017-08-24', '2017-08-23T17:00', '증가방류', '탄력적 방류')
assert (_pp['APR:3091']['approvalTime'], _pp['OPR:3091:1']['operationTime'], _pp['OPR:3091:1']['operationType']) == ('2018-08-29', '2018-08-23T22:00', '방류')
assert (_raw['2713']['접수방류량'], _raw['2866']['접수방류량'], _raw['3052']['접수방류량'], _raw['3091']['접수방류량'], _raw['3091']['비고'].strip()) == ('100', '200', '300', '300', '')
_d4 = sorted(r['승인년월일시분'].strip() for r in _raw.values() if r['관측소코드'].strip() in ('1003110', '1012110', '1006110', '1001210'))
assert (_d4[0][:7], _d4[-1][:7]) == ('2010-09', '2021-07')
assert len(rd('approval_preprocess_log.csv')) == 7
_cy = open(os.path.join(N3, 'kgv4_load.cypher'), encoding='utf-8').read()
assert (_cy.count('MERGE (n:Entity'), _cy.count(']->')) == (N_ENT, N_REL)
assert V['V6']['count'] == '0'


def apr_txt(seq):
    r = _raw[seq]
    return '승인 %s (%s, %s㎥/s)\n비고: %s' % (seq, r['승인년월일시분'].strip(), r['접수방류량'].strip(), re.sub(r'\s+', ' ', r['비고'].strip()) or '없음')


# ------------------------------------------------------------------ 참고문헌 (본문에 처음 나온 순서로 번호)
REFS = {
    'NOY': 'Noy, N. F., & McGuinness, D. L. (2001). Ontology development 101: A guide to creating your first ontology. Stanford University.',
    'HU': 'Huang, J., Hou, W., Zhang, S., Du, Z., & Yin, J. (2026). Dam defects ontology and knowledge graph construction from multi-source hazard data using large language models. Advanced Engineering Informatics, 76, 104987.',
    'ZH': 'Zhou, Y., Bao, T., Shu, X., Li, Y., & Li, Y. (2023). BIM and ontology-based knowledge management for dam safety monitoring. Automation in Construction, 145, 104649.',
    'FOCA': 'Bandeira, J., Bittencourt, I. I., Espinheira, P., & Isotani, S. (2016). FOCA: A methodology for ontology evaluation. arXiv:1612.03353.',
    'PU': 'Purohit, S., Chin, G., Mackey, P. S., & Cottam, J. A. (2024). GraphAide: Advanced graph-assisted query and reasoning system. 2024 IEEE International Conference on Big Data.',
    'LI': 'Li, S., Erickson, C., Zajac, M., Guo, X., Duan, Q., & Gong, J. (2025). A semi-automated framework for flood ontology construction with an application in risk communication. Water, 17, 2801.',
}
ORDER = []


def cite(t):
    def rep(m):
        keys = m.group(1).split(',')
        for k in keys:
            if k not in ORDER:
                ORDER.append(k)
        return '[' + ', '.join(str(ORDER.index(k) + 1) for k in keys) + ']'
    return re.sub(r'\{([A-Z0-9,]+)\}', rep, t)


B = []
add = B.append


def lis(*items):
    for t in items:
        add(li(cite(t)))


def tbl(rows, widths):
    add(table([[cite(str(c)) for c in r] for r in rows], widths, header=True, firstcol=False))



def P(t):
    add(para(cite(t)))


def KEY(head, t):
    add(L.lead(head, cite(t)))


def CODE(t):
    add(L.code(t))


def FLOW(*items):
    add(L.flow(list(items)))


def H2B(t):
    """새 쪽에서 시작하는 소제목."""
    x = h2(t); assert '<w:pStyle w:val="21"/>' in x
    add(x.replace('<w:pStyle w:val="21"/>', '<w:pStyle w:val="21"/><w:pageBreakBefore/>', 1))


def CARD(rows, w1=1700):
    """왼쪽에 항목 이름, 오른쪽에 내용(줄바꿈 가능)을 두는 정리 상자."""
    add(table([[a, cite(b)] for a, b in rows], [w1, 9972 - w1], header=False, firstcol=True))

# ================================================================== 표지·요약
add(title('온톨로지 설계 방법 검토와 검증 방법', '문헌 검토와 전문가 검토 방안'))
add(dateline('2026.11.13 · 문경민'))
add(h1('요약'))
CARD([('지난주', 'KG 구축 방법(Relation 잇기, 저장, 검색·답변)을 정리했고, 검토할 점 두 가지를 남겼다.\n(가) 온톨로지를 CQ1~CQ6에 답하는 구조로 만들어 그 밖의 질문에는 답하지 못한다. 온톨로지 생성 방식을 다시 검토한다.\n(나) 선행 연구들이 KG·온톨로지를 어떻게 검증했는지 조사한다.\n받은 의견: 검증을 어떻게 할지 더 고민해 마무리할 것, 필요하면 외부 전문가의 도움을 받는 방법을 찾을 것.'),
      ('이번 주', '① 온톨로지 설계 방법을 문헌으로 검토했다. 댐 분야 최신 논문에서 인용을 따라 올라가 설계 방법의 흐름을 확인했고, 범위를 정하는 세 가지 방법 가운데 역량 질문(CQ)이 운영자의 질문에 답한다는 우리 목적에 가장 잘 맞는다고 판단했다(1장).\n② 같은 문헌이 온톨로지의 확인에 대해 말한 것을 따라 검증을 정리했다. CQ로 확인하는 것은 9월부터 해 왔고, 그 과정에서 Relation 하나를 더했다. 그러나 CQ 자체는 우리가 만들었고 확인받지 않았다(2.1~2.3).\n③ 그래서 질문 후보를 82개로 늘려 전문가에게 검토받고, 확인된 CQ로 온톨로지를 넓히는 방안을 정했다(2.4).'),
      ('다음 주', '질문 후보를 검토지로 만들고, 검토를 요청할 전문가를 정한다(3장).')], 1300)

# ================================================================== 1. 온톨로지 설계 방법 검토
add(h1('1. 온톨로지 설계 방법 검토', pagebreak=True))
P('지난주 자료의 검토할 점은 "온톨로지를 CQ1~CQ6에 답하는 구조로 만들어, 질문의 의도가 CQ1~CQ6에 해당할 때만 답할 수 있다. 따라서 선행연구를 비교하고 온톨로지 생성 방식을 다시 검토한다"였다. 그래서 온톨로지를 설계하는 방법을 문헌으로 다시 검토했다.')
add(h2('1.1 검토 경로'))
P('우리 연구와 가장 가까운 최신 논문에서 출발해, 온톨로지를 만드는 방법에 대해 인용된 문헌을 과거로 차례로 따라갔다.')
FLOW('DDKG (2026)\n댐 결함 온톨로지', 'OntoDSMS (2023)\n댐 안전 모니터링 온톨로지', 'Noy·McGuinness (2001)\n온톨로지 구축 방법', 'Gruber (1993, 1995)\n온톨로지 설계 기준')
lis('DDKG는 선행연구로 OntoDSMS를 인용한다{HU}.',
    'OntoDSMS는 온톨로지를 만드는 방법으로 Noy·McGuinness 방법을 골랐고, 고른 이유로 Gruber의 설계 기준을 든다{ZH}.')
add(h2('1.2 과거에서 현재까지: 설계 기준이 댐 온톨로지에 쓰이기까지'))
add(label('① Gruber (1993, 1995): 온톨로지 설계 기준'))
P('Gruber는 온톨로지를 만들 때 지켜야 할 기준 다섯 가지를 제안했다. 아래는 온톨로지 평가 방법론 FOCA가 정리한 내용을 옮긴 것이다{FOCA}.')
add(label('표 1. Gruber의 온톨로지 설계 기준'))
tbl([['기준', '뜻'],
     ['명료성', '정의한 용어의 의도된 뜻을 효과적으로 전달해야 한다. 정의는 객관적이고 맥락에 독립적이어야 한다.'],
     ['일관성', '정의와 일관된 추론만 허용해야 한다. 정의하는 공리에 논리적 모순이 없어야 한다.'],
     ['확장성', '예상되는 여러 과업의 바탕이 되고, 기존 정의를 고치지 않고 확장할 수 있어야 한다.'],
     ['최소 인코딩 편향', '특정 표기나 구현의 편의 때문에 표현을 고르지 않아야 한다.'],
     ['최소 존재론적 약속', '필요한 만큼만 세계에 대해 주장해, 쓰는 쪽이 구체화할 여지를 남겨야 한다.']],
    [2200, 7772])

add(label('② Noy·McGuinness (2001): 온톨로지를 만드는 7단계 방법'))
P('Noy·McGuinness는 온톨로지를 처음 만드는 사람을 위한 안내서로, 온톨로지를 아래 7단계로 만드는 방법을 제시했다. 온톨로지의 정의와 "지식을 공유하기 위해 만든다"는 목적은 Gruber(1993)를 인용한다{NOY}.')
FLOW('① 범위\n정하기', '② 재사용\n검토', '③ 용어\n나열', '④ 클래스\n·계층', '⑤ 속성\n정의', '⑥ 제약\n정의', '⑦ 인스턴스\n생성')
lis('①단계에서 범위를 정하는 방법으로 역량 질문(CQ)을 제시한다. CQ는 "이 온톨로지 위의 지식베이스가 답할 수 있어야 하는 질문"을 대략 적은 목록이다. 예를 들어 와인 온톨로지라면 "구운 고기에는 어떤 와인이 가장 좋은가?" 같은 질문을 적고, 그 질문에서 온톨로지에 무엇이 들어가야 하는지를 정한다{NOY}.',
    '⑤단계에서는 클래스만으로는 ①단계의 CQ에 답할 정보가 부족하므로, CQ에 답하는 데 필요한 속성을 정의한다{NOY}.')

add(label('③ OntoDSMS (2023): Noy·McGuinness 방법으로 댐 안전 모니터링 온톨로지를 구축'))
P('OntoDSMS는 구축 방법 일곱 가지(TOVE, IDEF5, Skeleton, KACTUS, SENSUS, METHONTOLOGY, Noy·McGuinness) 중 Noy·McGuinness 방법을 골랐다. 이유는 이 방법이 비교적 성숙했고, Gruber의 온톨로지 구축 기본 원칙 다섯 가지를 엄격히 따르는 현재 유일한 방법이라는 것이다. 그리고 논문의 3장을 이 7단계 그대로 나누어 온톨로지를 만들었다{ZH}.')

add(label('④ DDKG (2026): 같은 7단계로 댐 결함 온톨로지를 구축'))
P('DDKG는 OntoDSMS를 선행연구로 인용하고, 같은 7단계를 같은 순서로 밟아 댐 결함 온톨로지를 만들었다{HU}. 표 2는 두 연구가 각 단계에서 한 일이다.')
add(label('표 2. Noy·McGuinness 7단계를 댐 분야 두 연구가 적용한 내용'))
tbl([['단계{NOY}', 'OntoDSMS (2023){ZH}', 'DDKG (2026){HU}'],
     ['① 범위 정하기', '댐 안전 모니터링 시스템의 객체, 속성, 전문 용어, 관계를 범위로 정함', '댐 위험 도메인 온톨로지와 관련 과업을 정의'],
     ['② 재사용 검토', '센서와 관측을 나타내는 기존 표준 온톨로지(W3C의 SSN, SOSA)에서 센서, 관측 등의 클래스와 관계를 가져와 댐 모니터링에 맞게 고쳐 씀', '댐 위험 관련 기존 온톨로지의 재사용 검토'],
     ['③ 용어 나열', '변형 모니터링, 침투 모니터링, 환경량 모니터링 등 용어를 나열', '관련 용어 나열'],
     ['④ 클래스·계층', '가장 일반적인 개념에서 시작하는 하향식으로 정의', '최상위 클래스 7개를 정하고, 하위 계층은 댐 안전 평가 지침(SL 258–2017)과 전문가 지식으로 정함'],
     ['⑤ 속성 정의', '개체 사이의 관계와 개체의 값을 나타내는 속성을 정의', '클래스의 속성과 관계 정의'],
     ['⑥ 제약 정의', '속성의 값 유형, 허용 값, 값의 개수를 정의', '제약 명시'],
     ['⑦ 인스턴스 생성', '완성한 틀에 개체를 채움', '인스턴스 생성']],
    [2000, 4500, 3472])
lis('두 연구는 같은 7단계를 밟았지만, 범위와 개념을 정한 재료는 서로 달랐다. 두 논문에 CQ는 나오지 않는다. 이 차이를 1.3에서 비교한다.')

H2B('1.3 검토 결과: 범위를 정하는 세 가지 방법과 우리 연구')
P('검토한 문헌에서 온톨로지를 만드는 순서는 Noy·McGuinness 7단계로 같았다. 그러나 무엇으로 범위와 개념을 정하는지는 세 가지로 달랐다. 표 3은 세 방법을 우리 연구에 비추어 본 것이다.')
add(label('표 3. 범위와 개념을 정하는 세 가지 방법'))
tbl([['방법', '문헌', '무엇으로 정하나', '우리 연구에 비추어 보면'],
     ['기존 온톨로지와 시스템의 재사용', 'OntoDSMS{ZH}', '기존 댐 안전 모니터링 시스템의 객체, 기존 센서 표준 온톨로지(SSN, SOSA)', '검토한 두 댐 온톨로지의 대상은 안전 모니터링(센서, 관측)과 결함이다. 우리가 다루는 운영(운영행위, 방류 승인, 운영기준)과 대상이 달라 그대로 가져올 수 없다.'],
     ['지침과 전문가 지식', 'DDKG{HU}', '댐 안전 평가 지침(SL 258–2017)의 분류, 전문가 지식', 'DDKG의 목적은 결함을 분류하는 것이어서 지침의 분류가 클래스 계층이 되었다. 우리의 목적은 분류가 아니라 운영자의 질문에 답하는 것이다.'],
     ['역량 질문(CQ)', 'Noy·McGuinness{NOY}', '온톨로지 위의 지식베이스가 답할 수 있어야 하는 질문', '운영자의 질문에 답하는 시스템을 만든다는 우리 목적과 같은 개념이다. 답해야 할 질문에서 범위와 속성을 정한다.']],
    [1900, 2000, 2500, 3572])
lis('만드는 순서는 댐 분야 두 연구와 같이 Noy·McGuinness 7단계를 따른다. 2023년과 2026년의 댐 온톨로지가 모두 이 7단계로 만들어졌고, OntoDSMS는 이 방법을 Gruber의 설계 기준을 엄격히 따르는 유일한 방법이라고 평가했다{ZH,HU}.',
    '①단계에서 범위를 정하는 방법은 세 가지 가운데 CQ가 우리 목적에 가장 잘 맞는다고 판단했다(표 3의 오른쪽 칸은 우리 판단이다). 표 4는 그렇게 정한 CQ 여섯 개다.')
add(label('표 4. 우리 온톨로지의 CQ'))
tbl([['번호', '질문 대상', '질문'],
     ['CQ1', '현재 수문·기상 상태', '대상 댐의 현재 또는 기준시점의 강우, 수위, 유입량, 방류량 등 수문·기상 상태는 무엇인가?'],
     ['CQ2', '과거 수문·기상 상태', '선택된 과거 시점 또는 사례에서 대상 댐의 강우, 수위, 유입량, 방류량 등 수문·기상 상태는 어떠했는가?'],
     ['CQ3', '과거 운영행위', '해당 과거 시점 또는 사례에서 실제로 수행된 댐 운영행위는 무엇이었는가?'],
     ['CQ4', '과거 방류 승인', '해당 과거 시점 또는 사례에서 어떤 방류 승인이 있었으며, 그 승인내용은 무엇인가?'],
     ['CQ5', '현재 운영기준', '현재 대상 댐에 적용되는 운영기준은 무엇이며, 현재 운영 판단과 관련된 기준값은 무엇인가?'],
     ['CQ6', '공식 근거', '각 수문·기상 상태, 운영행위, 승인내용 및 운영기준을 확인할 수 있는 공식 자료 또는 근거문서는 무엇인가?']],
    [1000, 2400, 6572])
add(label('지난주 검토할 점에 대한 답'))
lis('지금 구조가 CQ1~CQ6에 해당하는 질문에만 답하는 것은 CQ로 범위를 정한 결과다.',
    'Noy·McGuinness는 온톨로지 개발이 반복 과정이라고 했다{NOY}. 답할 질문을 넓히려면 CQ를 더하고 ③~⑦단계를 다시 밟는다. 그래서 설계 방법은 바꾸지 않는다.',
    '다만 CQ 6개는 우리가 정했다. 이 질문들이 실제 댐 운영에서 묻는 질문인지는 전문가 검토에서 확인한다(2장).')


# ================================================================== 2. 온톨로지의 검증
add(h1('2. 온톨로지의 검증', pagebreak=True))
add(h2('2.1 설계에 쓴 문헌이 확인에 대해 말한 것'))
P('1장에서 본 대로 우리 온톨로지는 Noy·McGuinness의 방법으로 설계했다. 이 문헌은 만든 온톨로지를 확인하는 것에 대해서도 말한다{NOY}.')
add(label('표 5. Noy·McGuinness가 온톨로지의 확인에 대해 말한 것'))
tbl([['문헌의 말{NOY}', '뜻', '이 자료에서'],
     ['CQ는 나중에 리트머스 시험으로 쓰인다.', '다 만든 온톨로지가 CQ에 답할 만큼 정보를 담고 있는지를 CQ로 확인한다.', '2.3'],
     ['초기 온톨로지는 응용에 써 보거나 분야 전문가와 논의해 평가하고 고친다.', '전문가의 검토로 온톨로지를 평가한다.', '2.4'],
     ['온톨로지 개발은 반복 과정이다.', '한 번 만들고 끝나는 것이 아니라, 평가한 결과로 고치기를 되풀이한다.', '2.3, 2.4']],
    [3900, 4700, 1372])
add(h2('2.2 문제: CQ는 우리가 만들었고 확인받지 않았다'))
lis('표 5의 첫째 확인은 CQ를 기준으로 삼는다. 그런데 CQ 6개(표 4)는 우리가 만들었고, 실제 운영에서 묻는 질문인지 확인받은 적이 없다.',
    '그래서 CQ로 확인한 결과(2.3)는 "우리가 정한 질문에는 답할 수 있다"까지만 말한다. 정한 질문이 맞는지, 빠진 질문이 없는지는 말하지 못한다.',
    '지난주 자료에서 본 한계(CQ1~CQ6에 해당하는 질문만 답한다)도 여기서 나온다. CQ가 좁으면 온톨로지도 좁다.',
    '이것은 우리가 판정할 수 없다. 문헌이 말한 대로 분야 전문가의 검토가 필요하다{NOY}(2.4).')
H2B('2.3 지금까지 한 것: CQ로 확인')
P('CQ로 확인한다는 것은, CQ를 하나 골라 "이 질문의 답이 온톨로지의 Class와 Relation을 따라가면 나오는가"를 보는 것이다. CQ4(어떤 방류 승인이 있었으며 그 승인내용은 무엇인가)를 예로 든다.')
FLOW('충주댐\n(Dam)', '충주댐에 관한 승인\n(Approval)', '승인을 확인할 근거자료\n(EvidenceSource)')
lis('이 질문에 답하려면 댐에서 출발해 그 댐의 승인에 닿고, 승인에서 근거자료에 닿아야 한다. 닿으려면 그 사이를 잇는 Relation이 온톨로지에 있어야 한다.',
    '10월에 실제 자료를 넣은 KG에서 이 길을 따라가 보니, 승인 80개 가운데 63개만 댐에서 닿았다. 당시 온톨로지에는 댐에서 운영행위를 거쳐 승인으로 가는 길만 있었고, 운영행위가 없는 승인 17개는 닿지 않았다.',
    '그래서 Approval과 Dam을 직접 잇는 Relation(concernsDam)을 온톨로지에 더했고, 80개 모두 닿게 되었다.')
add(label('표 6. CQ로 확인한 과정'))
tbl([['시점', '한 일', '결과', '고친 것'],
     ['9월\n(온톨로지 초안)', 'CQ마다 초안의 Class와 Relation으로 답을 표현할 수 있는지, 답이 될 자료가 있는지를 보았다. 답할 수 없으면 원인을 다섯 가지로 나눴다(온톨로지 구조, 자료 없음, 출처의 뜻이 불명확, CQ 문구, KG·검색).', '여러 CQ에서, 승인과 측정자료를 댐에 직접 잇는 길이 없어 답할 수 없었다.', '댐에 직접 잇는 Relation을 후보로 적어 두었다.'],
     ['10월\n(KG를 만든 뒤)', '실제 자료를 넣은 KG에서 CQ의 길을 따라가 닿는 개수를 셌다.', '승인 80개 가운데 63개만 댐에서 닿았다.', 'Approval과 Dam을 잇는 Relation을 더했다(Relation 8개 → 9개). 80개 모두 닿았다.'],
     ['11월\n(지금의 KG)', 'CQ 6개 모두에 대해, 댐마다 닿는 개수를 원자료에서 센 개수와 비교했다.', '모든 댐에서 개수가 같다(표 7).', '—']],
    [1500, 3700, 2400, 2372])
add(label('표 7. CQ1~CQ5: 댐에서 길을 따라 찾은 개수 / 원자료에서 센 개수'))
tbl([['CQ', '댐에서 찾는 것'] + DAMS,
     ['CQ1, CQ2', '상태 변수 6개'] + [cq('C1', d) for d in DAMS],
     ['CQ3', '운영행위'] + [cq('C3', d) for d in DAMS],
     ['CQ4', '승인'] + [cq('C4', d) for d in DAMS],
     ['CQ5', '운영기준'] + [cq('C5', d) for d in DAMS]],
    [1100, 3672, 1300, 1300, 1300, 1300])
lis('CQ6(공식 근거)은 근거가 필요한 Entity %s개가 모두 출처 위치가 적힌 근거자료에 이어져 있다. 광동댐의 운영기준이 0개인 것은 규정 별표3에 광동댐이 없기 때문이다.' % S['C6']['kg'],
    '근거: CQ로 확인한다는 것은 Noy·McGuinness에서 가져왔다{NOY}. 이 문헌에는 세부 절차가 없어, 답할 수 없을 때 원인을 다섯 가지로 나누는 기준은 우리가 더했다. KG를 만든 뒤의 확인에서는 DDKG의 방법(온톨로지의 제약으로 결과를 판정하고, 걸린 문제로 온톨로지를 보완한다)을 함께 따랐다{HU}.',
    '이 결과가 말하는 범위: 우리가 만든 CQ 6개에 대해서는 답에 필요한 길이 온톨로지에 있다. 2.2의 문제 때문에 그 이상은 말하지 못한다.')
H2B('2.4 방안: CQ를 늘려 전문가에게 검토받고 온톨로지를 넓힌다')
add(label('근거'))
lis('CQ는 온톨로지의 범위를 정하는 방법이다. 그러므로 범위를 넓히려면 CQ를 늘린다. 온톨로지 개발은 반복 과정이고, 분야 전문가와 논의해 평가하고 고친다{NOY}.',
    '홍수 온톨로지를 만든 연구는 CQ를 LLM으로 만든 뒤, 자동 선별과 전문가 검토로 걸러서 썼다{LI}.',
    'DDKG는 전문가 검토에서 새 개념이 나오면 온톨로지에 더해, 온톨로지를 되풀이해 넓혔다{HU}.')
add(label('방안'))
FLOW('① 질문 후보를\n늘린다', '② 전문가가\n검토한다', '③ CQ를\n확정한다', '④ 온톨로지를\n넓힌다', '⑤ CQ로 다시\n확인한다 (2.3)')
add(label('① 질문 후보를 늘린다'))
P('CQ 6개에서만 출발하면 범위가 좁다. 그래서 업무 태스크 후보마다 LLM으로 질문을 만들어 후보 82개를 준비했다. 실무자가 낸 질문이 아니므로 검토가 필요하다. 지금의 온톨로지에 대어 우리가 나눠 본 결과는 표 8과 같다.')
add(label('표 8. 질문 후보 82개 (우리가 나눈 것)'))
tbl([['구분', '질문 수', '뜻'],
     ['지금 온톨로지로 답할 수 있다', NQ['answer_now'], 'CQ 6개의 범위 안에 있다.'],
     ['넓혀야 답할 수 있다', NQ['extend'], '그 가운데 %d개는 온톨로지에 Class, Relation, 속성을 더해야 하고(표 9), %d개는 검색이나 계산 기능이 더 필요하다.' % (NX['O1'] + NX['O2'] + NX['O3'] + NX['O4'], NQ['extend'] - (NX['O1'] + NX['O2'] + NX['O3'] + NX['O4']))],
     ['연구 범위 밖이다', NQ['refuse'], '예측, 문서 작성처럼 이 연구가 다루지 않는 것이다.']],
    [3000, 1100, 5872])
add(label('표 9. 온톨로지에 더해야 답할 수 있는 질문'))
tbl([['더해야 할 것', '질문 수', '질문 예시'],
     ['댐의 제원(Dam의 속성)', NX['O1'], QX('q008', '충주댐 총저수용량이 얼마야?', 'O1')],
     ['운영기준의 종류(홍수기 기간 등)', NX['O2'], QX('q030', '연계운영규정에서 홍수기는 언제부터 언제까지야?', 'O2')],
     ['규정 조문과 용어', NX['O3'], QX('q031', '댐에서 방류하기 전에 하류에 알려야 한다는 규정 있어?', 'O3')],
     ['댐 사이의 관계(수계)', NX['O4'], QX('q022', '광동댐 방류가 충주댐에 영향을 줘?', 'O4')]],
    [3400, 1100, 5472])
add(label('② 전문가가 검토한다'))
CARD([('검토자', '댐 운영(수문 조작, 방류 승인) 실무 경험이 있는 연구실 밖의 사람.'),
      ('보여 줄 것', '질문 후보 82개와 우리가 나눈 구분(표 8), 그리고 지금의 Class 6개와 Relation 9개(부록 A.1).'),
      ('묻는 것', '질문마다: 실제 업무에서 필요한 질문인가. 고칠 곳이 있는가.\n목록 전체: 빠진 질문이 있는가.\nClass와 Relation: 실무에서 쓰는 개념과 맞는가.'),
      ('판단을 받는 법', '항목마다 필요함, 고칠 것, 필요 없음 가운데 하나를 표시받고, 빠진 것은 따로 적어 받는다.')], 1700)
add(label('③ CQ를 확정하고, ④ 온톨로지를 넓히고, ⑤ 다시 확인한다'))
lis('전문가가 필요하다고 한 질문을 묶어 CQ로 삼는다. CQ의 수가 6개에서 늘어난다.',
    '새 CQ 가운데 지금 온톨로지로 답할 수 없는 것에 대해 Class, Relation, 속성을 더한다. Noy·McGuinness 7단계의 ③~⑦단계를 다시 밟는 것이다{NOY}.',
    '넓힌 온톨로지에 자료를 넣고 2.3의 확인을 다시 한다. 이번에는 전문가가 확인한 CQ가 기준이 된다.')
KEY('정리', '지금까지는 우리가 만든 CQ 6개로 온톨로지를 확인했다. 앞으로는 질문 후보를 늘려 전문가에게 검토받고, 확인된 CQ로 온톨로지를 넓히고 다시 확인하기를 되풀이한다.')

# ================================================================== 3. 다음 계획
add(h1('3. 다음 계획'))
lis('질문 후보 82개와 Class, Relation을 검토지로 만든다.',
    '검토를 요청할 전문가를 교수님과 상의해 정한다.',
    '검토를 받은 뒤 CQ를 확정하고, 온톨로지를 넓힌 뒤 2.3의 확인을 다시 한다.')

# ================================================================== 부록 A. 연구 구조
add(h1('부록 A. 지금까지 구체화한 연구 구조', pagebreak=True))
P('앞선 랩미팅 자료(10/16, 10/30, 11/06)에서 정리한 구조다. 온톨로지, KG 구축, 검색·답변의 순서다.')
add(h2('A.1 온톨로지'))
lis('답해야 할 질문은 CQ 6개다(표 4).')
add(label('표 A1. Class (6개)와 KG에 들어 있는 개수'))
_n = collections.Counter(r['class'] for r in rd('kgv4_entities.csv'))
tbl([['Class', '뜻', 'Data Property', '개수'],
     ['Dam', '댐', 'damName, damType', _n['Dam']],
     ['HydrometeorologicalState', '댐의 수문·기상 상태 변수', 'variableType, stationCode', _n['HydrometeorologicalState']],
     ['Operation', '실제로 한 운영행위', 'operationType, operationTime', _n['Operation']],
     ['Approval', '방류 승인', 'approvalTime, approvalContent', _n['Approval']],
     ['Criterion', '운영기준', 'criterionType, criterionValue, unit', _n['Criterion']],
     ['EvidenceSource', '근거자료', 'sourceTitle, sourceType, sourceLocator', _n['EvidenceSource']]],
    [2600, 2400, 3972, 1000])
add(label('표 A2. Relation (9개)와 KG에 들어 있는 개수'))
_m = collections.Counter(r['relation'] for r in rd('kgv4_relations.csv'))
assert sum(_n.values()) == N_ENT and sum(_m.values()) == N_REL
tbl([['Subject', 'Relation', 'Object', '뜻', '개수'],
     ['Dam', 'hasHydrometeorologicalState', 'HydrometeorologicalState', '댐이 그 상태 변수를 가진다', _m['hasHydrometeorologicalState']],
     ['Operation', 'performedOnDam', 'Dam', '운영행위가 그 댐에서 수행되었다', _m['performedOnDam']],
     ['Approval', 'authorizes', 'Operation', '승인이 그 운영행위를 허가했다', _m['authorizes']],
     ['Approval', 'concernsDam', 'Dam', '승인이 그 댐에 관한 것이다', _m['concernsDam']],
     ['Criterion', 'appliesToDam', 'Dam', '운영기준이 그 댐에 적용된다', _m['appliesToDam']],
     ['상태, 운영행위, 승인, 운영기준', 'supportedBy (4개)', 'EvidenceSource', '각각을 확인할 수 있는 근거자료', _m['supportedBy']]],
    [2000, 2900, 2500, 1872, 700])
H2B('A.2 KG 구축')
add(label('표 A3. KG 구축 단계와 따른 문헌'))
tbl([['단계', '하는 일', '방법', '따른 문헌'],
     ['자료 준비', '소스 구분과 전처리', '중복 행 제거, 대상 4개 댐 선택', '—'],
     ['Class·Data Property 채우기', 'Entity와 속성값을 채움', '구조화 자료 매핑(정형 표), 비정형 텍스트 추출(비고, 별표3)', 'OntoDSMS{ZH}, DDKG{HU}'],
     ['Relation 잇기', '만든 Entity를 Relation마다 실제 시작·끝 Entity로 이음', '키로 이을 끝 Entity를 찾음(댐 표기 맞추기 포함)', 'GraphAide{PU}'],
     ['저장', '완성한 KG를 Neo4j에 넣음', 'CSV → Cypher → Neo4j', 'DDKG{HU}, OntoDSMS{ZH}'],
     ['검증', '설계한 온톨로지가 맞는지 확인', 'CQ로 확인, 전문가 검토(이번 자료 2장)', 'Noy·McGuinness{NOY}']],
    [2300, 2700, 3300, 1672])
add(h2('A.3 검색·답변'))
FLOW('① 의도·값 추출\n(LLM)', '② 입력 확인\n(코드)', '③ KG 검색과\n저장소 조회 (코드)', '④ 근거 묶음\n(코드)', '⑤ 답변\n(LLM)')
lis('질문에서 의도(CQ1~CQ6)와 값(댐, 기간)을 뽑고, CQ마다 정해 둔 조회문으로 KG를 검색해 근거를 묶은 뒤 LLM이 답한다{PU}. LLM은 처음과 마지막에만 쓴다.',
    '수문 측정값은 KG 밖의 측정자료 저장소에 두고, 댐 코드와 시각으로 조회한다.')

# ================================================================== 참고문헌
add(h1('참고문헌'))
assert set(ORDER) == set(REFS), set(REFS) ^ set(ORDER)
for i, k in enumerate(ORDER, 1):
    add(L.para('[%d] %s' % (i, REFS[k]), 17))

T.save(OUT, ''.join(B), L.IMGS, page_numbers=True)
print('saved', OUT, 'refs', len(ORDER))


