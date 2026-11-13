#!/usr/bin/env python3
"""랩미팅 자료(docx): 온톨로지 설계 방법 검토와 검증 방법.
서식은 11/06 자료(build_labmeeting_how_kg2.py)와 같다(labdoc_lib, 같은 템플릿).
근거 문헌: references/evidence_literature/ (해설: lab_meeting/paper_review/검증부분_해석6, 해석7)
11/12 19차: 요약 글씨 키움, 1장을 DDKG 의견에서 출발해 Noy부터 정리(Gruber 원칙은 OntoDSMS 설명 안으로), CQ를 쓴 이유에 두 연구와의 조건 차이 추가.
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
add(title('온톨로지 설계 방법 검토와 검증 방안', '').replace('<w:br/><w:t xml:space="preserve"></w:t>', ''))
add(dateline('2026.11.13 · 문경민'))
add(h1('요약'))
add(table([[a, cite(b)] for a, b in [
    ('지난주', '· KG 구축 방법(Relation 잇기, 저장, 검색·답변)을 정리했다.\n· 온톨로지를 CQ1~CQ6에 답하는 구조로 만들어, 그 밖의 질문에는 답하지 못한다는 점을 보았다.\n· 온톨로지를 CQ로 만든 방법이 맞는지 온톨로지 구축 방법을 검토할 필요가 있다.\n· 검증을 어떻게 할지 더 고민해 마무리할 것. 필요하면 외부 전문가의 도움을 받는 방법을 찾을 것.'),
    ('이번 주', '① 온톨로지 구축 방법을 문헌으로 정리했다.\n· DDKG에서 출발해 인용을 따라가, DDKG와 OntoDSMS가 모두 Noy·McGuinness 7단계로 온톨로지를 만들었음을 확인했다.\n· 우리도 같은 7단계를 따랐고, 운영자의 질문에 답한다는 목적에 맞아 이 방법이 제시한 역량 질문(CQ)으로 범위를 정했다.\n\n② 한계를 정리했다.\n· CQ 6개는 우리가 만들었고 확인받지 않았다.\n· 정한 질문이 맞는지는 우리가 판정할 수 없어 전문가의 검토가 필요하다(1.3).\n\n③ 온톨로지를 검증하고 개선하는 방법으로 CQ를 이용한 전문가 검토를 구체화했다.\n· 근거: Noy·McGuinness와 DDKG는 전문가 검토로 온톨로지를 고치고 넓혔다. 홍수 온톨로지 연구는 LLM으로 만든 CQ를 사람이 검토해 남기고, 확장용과 평가용으로 나눠 썼다.\n· 이 절차를 따라 질문 후보 82개를 댐 운영 실무자에게 검토받아 CQ를 정하고, 70%로 온톨로지를 넓히고 30%로 평가한다.'),
    ('다음 주', '· 질문 후보 82개의 목록과 평가표를 완성한다.\n· KG 구축 단계의 검증을 어떻게 할지 고민한다.')]], [1300, 8672], header=False, firstcol=True, sz=22))

# ================================================================== 1. 온톨로지 설계 방법 검토
add(h1('1. 온톨로지 설계 방법: 왜 CQ로 설계했나', pagebreak=True))
add(h2('1.1 조사 경로'))
P('우리 연구와 가장 가까운 최신 논문에서 출발해, 온톨로지를 만드는 방법에 대해 인용된 문헌을 과거로 차례로 따라갔다.')
FLOW('DDKG (2026)\n댐 결함 온톨로지', 'OntoDSMS (2023)\n댐 안전 모니터링 온톨로지', 'Noy·McGuinness (2001)\n온톨로지 구축 방법')
lis('DDKG는 선행연구로 OntoDSMS를 인용한다{HU}.',
    'OntoDSMS는 온톨로지를 만드는 방법으로 Noy·McGuinness 방법을 골랐다{ZH}.')
add(h2('1.2 과거에서 현재까지: Noy·McGuinness 방법이 댐 온톨로지에 쓰이기까지'))
add(label('① Noy·McGuinness (2001): 온톨로지를 만드는 7단계 방법'))
P('Noy·McGuinness는 온톨로지를 처음 만드는 사람을 위한 안내서로, 온톨로지를 아래 7단계로 만드는 방법을 제시했다{NOY}.')
FLOW('① 범위\n정하기', '② 재사용\n검토', '③ 용어\n나열', '④ 클래스\n·계층', '⑤ 속성\n정의', '⑥ 제약\n정의', '⑦ 인스턴스\n생성')

add(label('② OntoDSMS (2023): Noy·McGuinness 방법으로 댐 안전 모니터링 온톨로지를 구축'))
P('OntoDSMS는 구축 방법 일곱 가지(TOVE, IDEF5, Skeleton, KACTUS, SENSUS, METHONTOLOGY, Noy·McGuinness) 중 Noy·McGuinness 방법을 골랐다. 이유는 이 방법이 비교적 성숙했고, Gruber의 온톨로지 구축 기본 원칙 다섯 가지를 엄격히 따르는 현재 유일한 방법이라는 것이다{ZH}. Gruber의 다섯 가지 원칙은 표 1과 같다{FOCA}')
add(label('표 1. Gruber의 온톨로지 설계 기준'))
tbl([['기준', '뜻'],
     ['명료성', '정의한 용어의 의도된 뜻을 효과적으로 전달해야 한다. 정의는 객관적이고 맥락에 독립적이어야 한다.'],
     ['일관성', '정의와 일관된 추론만 허용해야 한다. 정의하는 공리에 논리적 모순이 없어야 한다.'],
     ['확장성', '예상되는 여러 과업의 바탕이 되고, 기존 정의를 고치지 않고 확장할 수 있어야 한다.'],
     ['최소 인코딩 편향', '특정 표기나 구현의 편의 때문에 표현을 고르지 않아야 한다.'],
     ['최소 존재론적 약속', '필요한 만큼만 세계에 대해 주장해, 쓰는 쪽이 구체화할 여지를 남겨야 한다.']],
    [2200, 7772])


add(label('③ DDKG (2026): 같은 7단계로 댐 결함 온톨로지를 구축'))
P('DDKG는 OntoDSMS를 선행연구로 인용하고, 같은 7단계를 같은 순서로 밟아 댐 결함 온톨로지를 만들었다{HU}. 표 2는 두 연구가 각 단계에서 한 일이다.')
add(label('표 2. Noy·McGuinness 7단계를 댐 분야 두 연구가 적용한 내용'))
tbl([['단계{NOY}', 'OntoDSMS (2023){ZH}', 'DDKG (2026){HU}'],
     ['① 범위 정하기', '온톨로지가 다룰 범위를 기존 댐 안전 모니터링 시스템에 있는 객체, 속성, 전문 용어, 관계 전체로 정했다.', '댐 위험 분야의 온톨로지와 관련 과업을 정의했다.'],
     ['② 재사용 검토', '센서와 관측을 나타내는 W3C 표준 온톨로지(SSN, SOSA)에서 클래스 계층과 공리 일부를 가져와, 댐 모니터링에 맞게 확장하고 고쳤다.', '댐 위험과 관련된 기존 온톨로지 모델의 재사용을 검토했다.'],
     ['③ 용어 나열', '서로 겹치는지, 클래스인지 속성인지 따지지 않고 용어를 모두 적었다.\n예: 변형·침투·환경량 모니터링, 상대 변위, 균열 개도, 양압력, 탄성계수, 재료 정보', '관련 용어를 나열했다.'],
     ['④ 클래스·계층', '가장 일반적인 개념에서 시작해 하위로 나누는 하향식으로 정했다.\n예: 최상위 Structure 아래에 LeftBankSection, DrainGate를 두고, DrainGate를 다시 Pier, Gate로 나눔', '최상위 클래스 7개를 정했다(Dam, Properties, Location, Parameter, HazardForm, HazardComponent, SafetyEvaluation).\n이 중 HazardForm과 HazardComponent의 하위 계층은 댐 안전 평가 지침(SL 258–2017)과 전문가 지식으로 정했다.'],
     ['⑤ 속성 정의', '③에서 적은 용어 중 클래스로 쓰지 않은 나머지를 속성으로 정했다. 개체와 개체를 잇는 속성(예: hasSection)과 개체와 값을 잇는 속성으로 나눴다.', '최상위 클래스를 잇는 관계 7개를 정했다.\n예: Dam –exhibitsHazard→ HazardForm, HazardForm –occursAt→ HazardComponent\n클래스 안의 계층은 hasSubclass로 이었다.'],
     ['⑥ 제약 정의', '속성마다 값의 유형(문자열, 숫자, 참·거짓, 열거), 허용 값, 값의 개수를 정했다.\n예: hasName의 값 유형은 문자열', '제약을 명시했다.'],
     ['⑦ 인스턴스 생성', '클래스를 고르고, 그 클래스의 개체를 하나 만들고, 속성 값을 채우는 순서로 개체를 넣었다.', '인스턴스를 생성했다.']],
    [1700, 4300, 3972])
lis('두 연구가 범위와 개념을 정한 재료는 서로 달랐다. OntoDSMS는 기존 댐 안전 모니터링 시스템과 기존 센서 온톨로지를 재사용했고{ZH}, DDKG는 댐 안전 평가 지침과 전문가 지식을 썼다{HU}. 두 논문에 CQ는 나오지 않는다.')

H2B('1.3 우리 연구: 같은 7단계를 따르고, 범위는 CQ로 정했다')
add(label('Noy·McGuinness 7단계를 따른 이유'))
lis('온톨로지 설계 기준을 따르는 방법으로 평가되었다. OntoDSMS는 이 방법을 Gruber의 설계 기준 다섯 가지를 엄격히 따르는 유일한 방법이라고 평가했다{ZH}.',
    '댐 분야에서 이어서 쓰인 방법이다. 2023년 댐 안전 모니터링 온톨로지와 2026년 댐 결함 온톨로지가 모두 이 7단계로 만들어졌다{ZH,HU}.')
add(label('①단계에서 CQ로 범위를 정한 이유'))
lis('DDKG와 OntoDSMS는 같은 7단계를 따랐지만 우리와 조건이 달랐다. OntoDSMS는 가져다 쓸 표준 온톨로지(SSN, SOSA)와 기존 모니터링 시스템의 자료가 있었고{ZH}, DDKG는 분류의 바탕이 되는 안전 평가 지침과 결함 서술 약 12만 건의 자료가 있었다{HU}. 우리는 댐 운영에 대해 그대로 가져다 쓸 온톨로지를 확인한 범위에서는 찾지 못했고, 자료도 4개 댐의 승인 기록 80건으로 적다.',
    '우리가 만들려는 것은 댐 운영자의 질문에 답하는 시스템이다.',
    'Noy·McGuinness가 ①단계에서 제시한 CQ는 "온톨로지 위의 지식베이스가 답할 수 있어야 하는 질문"이다{NOY}. 운영자의 질문에 답한다는 우리 목적과 같은 개념이다.',
    '그래서 답해야 할 질문을 먼저 정하고, 그 질문에 답하는 데 필요한 것으로 온톨로지의 범위와 속성을 정하는 이 방식이 우리 목적에 맞다고 보았다. 표 3은 그렇게 정한 CQ 여섯 개다.')
add(label('표 3. 우리 온톨로지의 CQ'))
tbl([['번호', '질문 대상', '질문'],
     ['CQ1', '현재 수문·기상 상태', '대상 댐의 현재 또는 기준시점의 강우, 수위, 유입량, 방류량 등 수문·기상 상태는 무엇인가?'],
     ['CQ2', '과거 수문·기상 상태', '선택된 과거 시점 또는 사례에서 대상 댐의 강우, 수위, 유입량, 방류량 등 수문·기상 상태는 어떠했는가?'],
     ['CQ3', '과거 운영행위', '해당 과거 시점 또는 사례에서 실제로 수행된 댐 운영행위는 무엇이었는가?'],
     ['CQ4', '과거 방류 승인', '해당 과거 시점 또는 사례에서 어떤 방류 승인이 있었으며, 그 승인내용은 무엇인가?'],
     ['CQ5', '현재 운영기준', '현재 대상 댐에 적용되는 운영기준은 무엇이며, 현재 운영 판단과 관련된 기준값은 무엇인가?'],
     ['CQ6', '공식 근거', '각 수문·기상 상태, 운영행위, 승인내용 및 운영기준을 확인할 수 있는 공식 자료 또는 근거문서는 무엇인가?']],
    [1000, 2400, 6572])
add(label('한계'))
lis('CQ 6개(표 3)는 우리가 만들었고, 실제 운영에서 묻는 질문인지 확인받은 적이 없다.',
    '정한 질문이 맞는지, 빠진 질문이 없는지는 우리가 판정할 수 없다. 전문가의 검토가 필요하다(2장).')

# ================================================================== 2. 온톨로지의 검증과 개선
add(h1('2. 온톨로지의 검증과 개선: CQ를 이용한 전문가 검토', pagebreak=True))
P('1장의 한계에서, CQ가 맞는지는 우리가 판정할 수 없고 전문가의 검토가 필요하다고 보았다. 2장은 그 검토를 어떤 절차로 하고 무엇으로 평가할지를 문헌에서 찾아 정한 것이다.')
add(h2('2.1 근거: 온톨로지 구축에서 전문가 검토를 쓴 연구'))
add(label('① Noy·McGuinness (2001)'))
lis('초기 온톨로지는 응용에 써 보거나 분야 전문가와 논의해 평가하고, 그 결과로 고친다고 했다. 온톨로지 개발은 이렇게 되풀이하는 과정이라고 했다{NOY}.')
add(label('② DDKG (2026)'))
lis('KG를 만드는 과정에 "전문가 검토와 온톨로지 확장" 단계를 두었다. 추출한 결함 서술 가운데 온톨로지의 제약과 맞지 않는 것을 전문가에게 보낸다{HU}.',
    '전문가는 그 개념이 온톨로지에 이미 있는지 판단한다. 있으면 맞는 항목에 연결하고, 새 개념이면 온톨로지에 항목을 추가한다. 논문은 이를 온톨로지의 반복 확장이라고 했다{HU}.',
    '이 단계를 둔 이유도 적었다. 전문가 경험만으로 정한 계층은 지식의 경계에 묶여 온톨로지가 다루는 범위가 제한될 수 있다는 것이다{HU}.')
KEY('정리', '두 문헌 모두 전문가 검토의 결과로 온톨로지를 고치거나 넓힌다. 다만 DDKG에서 전문가가 보는 것은 추출된 결함 서술이고 CQ가 아니다. 우리 온톨로지는 CQ에서 나왔으므로, CQ를 검토 대상으로 삼은 연구를 따로 찾았다(2.2).')

add(h2('2.2 CQ로 검토하고 평가한 수자원 분야 연구: 홍수 온톨로지'))
P('Li 등(2025)은 홍수 위험 소통을 위한 온톨로지를 만들면서, LLM으로 CQ를 만들고 사람이 검토해 남긴 뒤 그 CQ로 온톨로지를 넓히고 평가했다{LI}. 절차는 아래와 같다.')
FLOW('① 초기\n온톨로지', '② LLM으로\nCQ 생성', '③ 사람이\n검토해 남김', '④ 확장용·\n평가용 나눔', '⑤ 확장용으로\n온톨로지 확장', '⑥ 평가용으로\n평가')
add(label('표 4. 홍수 온톨로지 연구의 단계별 내용'))
tbl([['단계', '한 일{LI}'],
     ['① 초기 온톨로지', '이해관계자 면담과 요구사항 분석을 바탕으로 연구진이 최상위 클래스 6개와 그 하위 클래스를 정했다.'],
     ['② CQ 생성', '초기 온톨로지를 입력으로 주고 LLM(GPT-4o)으로 CQ를 여러 개 만들었다.'],
     ['③ 검토', '만든 CQ를 사람이 검토해 질이 좋은 40개만 남겼다.'],
     ['④ 나눔', '남긴 CQ의 70%는 온톨로지 확장에 쓰고, 30%는 최종 온톨로지를 평가하는 데만 쓰도록 떼어 두었다.'],
     ['⑤ 확장', '확장용 CQ에서 LLM으로 클래스와 관계 후보를 뽑았다. 후보는 자동 거름(임베딩 유사도로 중복 제거)과 사람의 검토를 거쳐 온톨로지에 넣었다.'],
     ['⑥ 평가', '평가용 CQ로 개념 포괄도를 보았다. "CQ에 들어 있는 개념을 온톨로지가 갖고 있는가"를 묻는 평가다.\n· CQ마다 LLM으로 핵심 개념을 3~7개 뽑았다.\n· 평가자 3명이 개념마다 좋음, 나쁨을 표시하고 빠진 개념을 제안했다. 2명 이상이 동의한 것만 남겼다(56개 중 2개를 빼고 12개를 더해 66개).\n· 남은 개념과 온톨로지의 이름을 임베딩해 유사도로 맞춰 보고, 기준값을 바꿔 가며 맞는 비율을 보았다.']],
    [1900, 8072])
lis('③의 검토와 ⑥의 평가자 3명은 온톨로지를 만든 연구진이다{LI}. 외부 실무자가 검토한 것은 아니다.')

H2B('2.3 우리 연구에 적용: 같은 절차를 따르되 검토자와 평가 방법을 바꾼다')
FLOW('① LLM으로\n질문 후보 생성', '② 실무자가\n검토', '③ CQ\n확정', '④ 확장용·\n평가용 나눔', '⑤ 온톨로지\n확장', '⑥ 평가용\nCQ로 평가')
add(label('표 5. 홍수 온톨로지 연구의 절차와 우리 적용'))
tbl([['단계', '홍수 온톨로지 연구{LI}', '우리 연구'],
     ['① 후보 생성', 'LLM으로 CQ 생성', '업무 태스크 후보마다 LLM으로 질문을 만들어 82개를 준비했다.'],
     ['② 검토', '연구진이 검토해 40개를 남김', '댐 운영 실무자가 질문마다 필요함, 고칠 것, 필요 없음을 표시하고 빠진 질문을 적는다(표 6).'],
     ['③ CQ 확정', '검토로 남긴 것이 CQ', '필요함으로 표시된 질문과 고친 질문, 추가된 질문을 CQ로 삼는다.'],
     ['④ 나눔', '70%는 확장, 30%는 평가', '같은 비율로 나눈다. 평가용은 온톨로지를 넓힐 때 보지 않는다.'],
     ['⑤ 확장', 'LLM으로 후보를 뽑고 자동 거름과 사람 검토', '확장용 CQ마다 답에 필요한 개념을 적고, 지금 온톨로지에 없는 Class, Relation, 속성을 더한다. Noy·McGuinness 7단계의 ③~⑦단계를 다시 밟는다{NOY}.'],
     ['⑥ 평가', '평가용 CQ의 개념 포괄도. 임베딩 유사도로 대조', '평가용 CQ마다 필요한 개념을 적고, 넓힌 온톨로지에 있는지를 표로 대조한다(표 7).']],
    [1400, 3400, 5172])
add(label('② 실무자 검토의 방법'))
CARD([('검토자', '댐 운영 실무자.'),
      ('보여 줄 것', '질문 후보 82개의 목록(표 6의 형태).'),
      ('묻는 것', '질문마다: 실제 업무에서 필요한 질문인가. 고칠 곳이 있는가.\n목록 전체: 빠진 질문이 있는가.'),
      ('판단을 받는 법', '질문마다 필요함, 고칠 것, 필요 없음 가운데 하나를 표시받고, 빠진 질문은 따로 적어 받는다.')], 1700)
_x = label('표 6. 실무자에게 줄 목록의 형태 (82개 가운데 예시 8개)'); add(_x.replace('<w:keepNext/>', '<w:keepNext/><w:pageBreakBefore/>', 1))
tbl([['번호', '업무', '질문', '판단', '의견'],
     ['1', Q82['q001']['task_name'], Q82['q001']['question'], '', ''],
     ['2', Q82['q017']['task_name'], Q82['q017']['question'], '', ''],
     ['3', Q82['q008']['task_name'], Q82['q008']['question'], '', ''],
     ['4', Q82['q030']['task_name'], Q82['q030']['question'], '', ''],
     ['5', Q82['q022']['task_name'], Q82['q022']['question'], '', ''],
     ['6', Q82['q031']['task_name'], Q82['q031']['question'], '', ''],
     ['7', Q82['q016']['task_name'], Q82['q016']['question'], '', ''],
     ['8', Q82['q021']['task_name'], Q82['q021']['question'], '', ''],
     ['', '빠진 질문', '', '', '']],
    [800, 2700, 4200, 900, 1372])
lis('판단 칸에는 필요함, 고칠 것, 필요 없음 가운데 하나를 적는다.')
add(label('⑥ 평가의 방법: 개념 포괄도'))
lis('평가용 CQ마다 그 질문에 답하는 데 필요한 개념을 적는다.',
    '개념마다 넓힌 온톨로지의 Class, Relation, 속성 가운데 해당하는 것이 있는지 대조한다.',
    '포괄도는 "온톨로지에 있는 개념 수 ÷ 필요한 개념 수"다. CQ마다, 그리고 평가용 CQ 전체로 계산한다.',
    '평가용 CQ는 온톨로지를 넓힐 때 쓰지 않은 질문이므로, 포괄도가 낮게 나온 개념은 다음 확장에서 다룰 대상이 된다.')
add(label('표 7. 평가표의 형태 (형태를 보이기 위해 지금의 CQ4와 지금의 온톨로지로 채운 예)'))
tbl([['CQ', '필요한 개념', '온톨로지에서 해당하는 것', '있음'],
     ['CQ4. 해당 과거 시점에 어떤 방류 승인이 있었으며, 그 승인내용은 무엇인가?', '방류 승인', 'Class Approval', '○'],
     ['', '승인한 날', 'Approval의 속성 approvalTime', '○'],
     ['', '승인내용', 'Approval의 속성 approvalContent', '○'],
     ['', '대상 댐', 'Class Dam, Relation concernsDam', '○'],
     ['', '포괄도', '4 ÷ 4', '']],
    [3700, 1700, 3672, 900])
lis('실제 평가는 실무자 검토 뒤 평가용으로 떼어 둔 CQ와 넓힌 온톨로지로 한다.')
add(label('한계'))
lis('검토로 남는 CQ가 적으면 평가용 30%는 몇 개뿐이다. 홍수 온톨로지 연구도 평가용은 12개였다{LI}.',
    '홍수 온톨로지 연구의 평가는 개념만 대조하고, 개념을 잇는 관계가 온톨로지에 있는지는 확인하지 않는다{LI}. 개념이 모두 있어도 그것을 잇는 Relation이 없으면 CQ에 답할 수 없으므로, 관계를 확인하는 방법은 따로 정해야 한다.',
    '개념 포괄도는 온톨로지에 필요한 개념이 있는지만 본다. KG에 들어간 값이 맞는지, 답변이 맞는지는 이 평가로 알 수 없다(3장).',
    '필요한 개념을 적는 일과 대조하는 일을 우리가 하므로, 그 결과도 실무자나 다른 사람의 확인을 받는 것이 좋다. 홍수 온톨로지 연구는 이 부분을 평가자 3명의 다수결로 했다{LI}.')
KEY('정리', 'Noy·McGuinness와 DDKG는 전문가 검토로 온톨로지를 고치고 넓혔고, 홍수 온톨로지 연구는 CQ를 LLM으로 만들어 사람이 검토하고 확장용과 평가용으로 나눠 썼다. 우리는 이 절차를 따라 질문 후보 82개를 실무자에게 검토받아 CQ를 정하고, 70%로 온톨로지를 넓히고 30%로 개념 포괄도를 평가한다.')

# ================================================================== 3. 다음 계획
add(h1('3. 다음 계획'))
lis('검토를 받은 뒤 CQ를 확정해 확장용과 평가용으로 나누고, 온톨로지를 넓혀 평가한다.',
    '이번에는 온톨로지의 검증만 다뤘다. KG 구축 단계의 검증도 따로 고민할 필요가 있다.')

# ================================================================== 부록 A. 연구 구조
add(h1('부록 A. 지금까지 구체화한 연구 구조', pagebreak=True))
P('앞선 랩미팅 자료(10/16, 10/30, 11/06)에서 정리한 구조다. 온톨로지, KG 구축, 검색·답변의 순서다.')
add(h2('A.1 온톨로지'))
lis('답해야 할 질문은 CQ 6개다(표 3).')
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
add(label('표 A3. KG 구축 단계 (11/06 자료 표 1)'))
tbl([['단계', '하는 일', '방법', '정리한 자료'],
     ['자료 준비', '소스 구분과 전처리', '—', '10/30'],
     ['Class·Data Property 채우기', 'Entity와 속성값을 채움', '구조화 자료 매핑(정형 표), 비정형 텍스트 추출(비고, 별표3)', '10/30'],
     ['Relation 잇기', '만든 Entity를 Relation마다 실제 시작·끝 Entity로 이음', '키로 이을 끝 Entity를 찾음(댐 표기 맞추기 포함)', '11/06'],
     ['저장', '완성한 KG를 Neo4j에 넣음', 'CSV → Cypher → Neo4j', '11/06'],
     ['검색·답변', '질문에 맞는 근거를 KG에서 찾아 LLM이 답함', '의도 추출 → Cypher 템플릿 조회 → 근거 묶음 → 답변', '11/06']],
    [2400, 3000, 3372, 1200])
add(h2('A.3 검색·답변'))
FLOW('① 의도·값 추출\n(LLM)', '② 입력 확인\n(코드)', '③ KG 검색과\n저장소 조회 (코드)', '④ 근거 묶음\n(코드)', '⑤ 답변\n(LLM)')
lis('질문에서 의도(CQ1~CQ6)와 값(댐, 기간)을 뽑고, CQ마다 정해 둔 조회문으로 KG를 검색해 근거를 묶은 뒤 LLM이 답한다. LLM은 처음과 마지막에만 쓴다.',
    '수문 측정값은 KG 밖의 측정자료 저장소에 두고, 댐 코드와 시각으로 조회한다.')

# ================================================================== 참고문헌
add(h1('참고문헌'))
assert set(ORDER) == set(REFS), set(REFS) ^ set(ORDER)
for i, k in enumerate(ORDER, 1):
    add(L.para('[%d] %s' % (i, REFS[k]), 17))

T.save(OUT, ''.join(B), L.IMGS, page_numbers=True)
print('saved', OUT, 'refs', len(ORDER))


