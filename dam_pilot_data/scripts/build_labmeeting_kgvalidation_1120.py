#!/usr/bin/env python3
"""랩미팅 자료(docx) 2026.11.20: KG 검증 방법 조사와 적용 방안.
서식은 11/13 자료(build_labmeeting_validation.py)와 같다(labdoc_lib, 같은 템플릿).
근거 문헌 해설: lab_meeting/paper_review/검증부분_해석8, 해석11, 해석12.
KG 수치는 03_normalized/kgv4_*.csv, step6_validation.csv, operation_measured_check.csv에서 읽는다.
사용: python3 scripts/build_labmeeting_kgvalidation_1120.py <출력 docx>
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

# ------------------------------------------------------------------ 사실: KG 크기와 검사 결과
import collections, csv
N3 = os.path.join(ROOT, '03_normalized')
rd = lambda p: list(csv.DictReader(open(os.path.join(N3, p), encoding='utf-8-sig')))
REL = rd('kgv4_relations.csv')
ORI = collections.Counter(r['origin'] for r in REL)
RO = collections.Counter((r['relation'], r['origin']) for r in REL)
assert len(REL) == 418 and ORI == {'real': 211, 'derived': 136, 'constructed': 68, 'name-match': 3}, ORI
V = {r['id']: r for r in rd('step6_validation.csv')}
assert all(V[k]['result'] == '통과' and V[k]['count'] == '0' for k in ('V1', 'V2', 'V3', 'V4', 'V5'))
MC = collections.Counter(r[k] for r in rd('operation_measured_check.csv') for k in r if k in ('verdict', 'result', '판정'))
print('measured check', dict(MC))

OPS = rd('operation_from_remarks_5dams.csv')
NRULE = len(set(o['rule'] for o in OPS if o['operation_created'] == 'Y'))
NPROP = len(rd('kgv4_properties.csv'))
assert NRULE == 9 and NPROP == 616, (NRULE, NPROP)

REFS = {
    'HO': 'Hogan, A., Blomqvist, E., Cochez, M., et al. (2021). Knowledge graphs. ACM Computing Surveys, 54(4), Article 71.',
    'KO': 'Kommineni, V. K., König-Ries, B., & Samuel, S. (2024). From human experts to machines: An LLM supported approach to ontology and knowledge graph construction. arXiv:2403.08345.',
    'HF': 'Hofer, M., Obraczka, D., Saeedi, A., Köpcke, H., & Rahm, E. (2023). Construction of knowledge graphs: State and challenges. arXiv:2302.11509.',
    'SH': 'Shami, F., Marchesin, S., & Silvello, G. (2026). Benchmarking large language models for knowledge graph validation. arXiv:2602.10748.',
    'HU': 'Huang, J., Hou, W., Zhang, S., Du, Z., & Yin, J. (2026). Dam defects ontology and knowledge graph construction from multi-source hazard data using large language models. Advanced Engineering Informatics, 76, 104987.',
    'GA': 'Gao, J., Li, X., Xu, Y. E., Sisman, B., Dong, X. L., & Yang, J. (2019). Efficient knowledge graph accuracy evaluation. Proceedings of the VLDB Endowment, 12(11), 1679–1691. arXiv:1907.09657.',
    'MA': 'Marchesin, S., & Silvello, G. (2025). Credible intervals for knowledge graph accuracy estimation. Proceedings of the ACM on Management of Data (SIGMOD). arXiv:2502.18961.',
}

# ================================================================== 표지·요약
add(title('KG 검증 방법 조사와 적용 방안', '').replace('<w:br/><w:t xml:space="preserve"></w:t>', ''))
add(dateline('2026.11.20 · 문경민'))
add(h1('요약'))
add(table([[a, cite(b)] for a, b in [
    ('지난주', '· 온톨로지 구축 방법을 문헌으로 정리하고, CQ를 이용한 전문가 검토를 구체화했다.\n· 온톨로지의 검증만 다뤘다. KG 자체를 검증하는 방법을 찾아야 한다.'),
    ('이번 주', '① 무엇을 검증하는지 나눴다.\n· 온톨로지, 추출, 적재, 답변의 넷이다. 이번에 다루는 것은 KG에 든 값, 곧 추출과 적재다(1장).\n\n② 지금의 KG를 만든 방식과 그에 맞춘 검증을 정리했다.\n· 표의 칸을 규칙으로 옮겨 만들었고, 규칙 검사와 원본 대조로 전부를 확인했다(2장).\n· 이 검증은 규모가 작고, 비교할 원본 칸이 있고, 규칙을 손으로 정할 수 있다는 조건에 기댄다(3장).\n\n③ 확장하면 만드는 방식이 바뀐다는 것을 문헌으로 확인했다.\n· 필요한 구축 과업은 자료의 종류에 달려 있다. 글에서는 값을 자동으로 추출해야 한다(4장).\n\n④ 자동으로 만든 KG를 검증하는 방법을 조사했다.\n· 사람이 일부를 판정해 정확도를 추정하는 방법과, 정답을 달아 둔 자료로 추출 도구를 채점하는 방법이 있다. LLM에게 판정을 맡기는 것은 아직 신뢰가 부족하다(5장).\n\n⑤ 검증 방법은 KG를 만든 방식이 정한다. 그래서 범위, 자료, 구축 방식, 검증 방법의 순서로 정한다(6장).'),
    ('다음 주', '· CQ의 실무자 검토로 범위를 정하고, 그에 따라 자료와 구축 방식, 검증 방법을 차례로 정한다.\n· 지금의 KG에서 남은 것(비고 문구를 읽는 규칙 9개)을 실무자에게 검토받는다.')]], [1300, 8672], header=False, firstcol=True, sz=22))

# ================================================================== 1
add(h1('1. 무엇을 검증하는가', pagebreak=True))
add(label('① 온톨로지의 검증만으로는 부족하다'))
lis('지난주에 정리한 온톨로지의 검증은 CQ에 답하는 데 필요한 개념(Class, Relation, 속성)이 온톨로지에 있는지를 본다. 그 틀에 채운 값이 맞는지는 알 수 없다.',
    '우리 시스템은 질문에 맞는 Entity와 Relation을 KG에서 찾아 근거로 묶고, LLM은 그 근거로 답을 쓴다. 온톨로지가 맞아도 KG에 든 값이 틀리면, 틀린 내용이 근거와 함께 답변에 나온다.',
    'Hogan 외(2021)는 처음 만든 KG가 대개 불완전하고, 중복되거나 서로 모순되거나 틀린 내용을 담는다고 했다. 그래서 KG를 만든 뒤 그 품질을 평가하는 것이 "결정적인 단계"라고 했다{HO}.')
add(label('② 검증의 대상을 넷으로 나눈다'))
tbl([['대상', '묻는 것', '다룬 자료'],
     ['온톨로지', 'CQ에 답하는 데 필요한 개념이 있는가', '11/13'],
     ['추출', '자료에서 값을 맞게 뽑았는가. 빠뜨린 것이 없는가', '이번 자료'],
     ['적재', '뽑은 값이 KG의 맞는 자리에, 정한 형식으로 들어갔는가', '이번 자료'],
     ['답변', 'KG를 근거로 LLM이 쓴 답변이 맞는가', '11/06 (질문 82개 평가)']],
    [1700, 6072, 2200])
lis('Kommineni 외(2024)는 LLM으로 만든 KG의 평가와, 그 KG로 낸 답변의 평가를 따로 했다{KO}.',
    'Hofer 외(2023)는 품질 보증이 완성된 KG뿐 아니라 지식 추출 같은 구축의 각 과업 안에서도 중요하다고 했다{HF}.',
    '넷으로 나눈 것은 위 문헌을 참고해 우리가 정리한 것이다. 이번 자료가 다루는 것은 KG에 든 값, 곧 추출과 적재다.')

# ================================================================== 2
add(h1('2. 지금의 KG: 만든 방식과 그에 맞춘 검증', pagebreak=False))
add(h2('2.1 만든 방식'))
lis('지금의 KG는 정형 자료(승인 CSV, 측정 CSV, 규정의 별표)에서 만들었다. 표의 칸에 있는 값을 변환 규칙으로 KG의 자리에 옮겼다.',
    'Hofer 외(2023)는 정형 자료를 매핑 규칙으로 변환해 KG로 만들고, 이 경우 지식 추출은 필요하지 않을 수 있다고 했다{HF}.')
add(label('표 1. 값이 들어온 경로와 지금 KG의 Relation 수 (전체 %d개)' % len(REL)))
tbl([['경로', '뜻', 'Relation', '개수'],
     ['칸의 값을 그대로 옮김', '자료의 칸에 있는 값을 그대로 넣었다.', 'concernsDam %d, hasHydrometeorologicalState %d, supportedBy %d' % (RO[('concernsDam', 'real')], RO[('hasHydrometeorologicalState', 'real')], RO[('supportedBy', 'real')]), str(ORI['real'])],
     ['비고 문구를 읽어 만듦', '승인 기록의 비고 문구를 규칙 %d개로 읽어 운영행위를 만들고, 그 운영행위에 댐, 승인, 근거를 이었다. 운영기준은 댐 이름을 맞춰 이었다.' % NRULE, 'performedOnDam %d, supportedBy %d, authorizes %d, appliesToDam %d' % (RO[('performedOnDam', 'derived')], RO[('supportedBy', 'derived')], RO[('authorizes', 'constructed')], RO[('appliesToDam', 'name-match')]), str(ORI['derived'] + ORI['constructed'] + ORI['name-match'])]],
    [2000, 3600, 3572, 800])
lis('지금의 KG에서 추출이라고 할 것은 비고 문구를 읽어 운영행위의 종류를 정한 부분(68개)뿐이다. 나머지는 칸의 값을 옮긴 것이다.')

add(h2('2.2 검증 방법과 근거'))
add(label('① 규칙 검사: 적재를 확인한다'))
lis('온톨로지의 정의(어느 Class끼리 이어지는가, Class마다 어떤 속성이 있어야 하는가, 값의 형식)를 규칙으로 옮기고, KG 전체에서 어기는 것을 프로그램으로 찾는다.',
    'Hogan 외(2021)는 KG가 정해 둔 제약을 어기지 않는지를 유효성이라 하고, 제약마다 위반 수를 세어 잰다고 했다{HO}. Hofer 외(2023)는 사람이 만든 제약에 기반한 규칙 분석을 품질 문제를 찾는 흔한 방법으로 들었다{HF}.',
    '확인하지 못하는 것: 값이 사실인지는 보지 않는다. 승인일이 원본과 하루 달라도 날짜 형식이 맞으면 통과한다.')
add(label('② 원본 대조: 원본대로 옮겨졌는지 확인한다'))
lis('KG의 값마다 그 값이 나온 원본의 행을 찾아(승인은 순차번호, 댐은 관측소코드) 값이 같은지 프로그램으로 비교한다. 개수도 비교해 한쪽에만 있는 것을 찾는다.',
    'Hogan 외(2021)는 값이 사실과 맞는지 평가하는 선택지의 하나로 출처와의 대조를 들었다{HO}.',
    '확인하지 못하는 것: 비교할 원본 칸이 없는 값. 비고 문구를 읽어 정한 운영행위의 종류가 여기에 해당한다.')
lis('두 방법은 문헌에서 찾아 적용한 것이 아니다. 온톨로지와 원본을 기준으로 삼아 검사를 짰고, 위 문헌의 분류에서 어디에 해당하는지를 이번에 확인했다.')

add(h2('2.3 결과'))
add(label('표 2. 규칙 검사의 규칙 5개와 결과'))
tbl([['규칙', '어긴 것으로 잡히는 예', '어긴 수'],
     ['Relation의 양 끝이 온톨로지가 허용한 Class 쌍이다.', 'authorizes가 Approval에서 Dam으로 이어짐', '0'],
     ['Class마다 있어야 하는 속성이 모두 있다.', 'Approval에 approvalTime이 없음', '0'],
     ['날짜, 시각, 수치의 형식이 맞다.', 'operationTime에 날짜가 아닌 글자가 있음', '0'],
     ['상태 변수, 운영행위, 승인, 운영기준이 모두 근거자료에 이어져 있다.', '근거자료가 없는 운영행위', '0'],
     ['승인이 이어진 댐과 그 승인이 허가한 운영행위의 댐이 같다.', '충주댐 승인이 횡성댐 운영행위를 허가함', '0']],
    [4600, 4172, 1200])
add(label('표 3. 원본 대조의 항목과 결과'))
tbl([['대조한 것', '원본', '결과'],
     ['승인의 개수와 순차번호', '승인 CSV (81행, 값이 모두 같은 중복 1행 제외)', '80개 중 80개 일치'],
     ['승인일(approvalTime)', '승인 CSV의 승인년월일', '80개 중 80개 일치'],
     ['승인내용(approvalContent)', '승인 CSV의 방류시작시간, 접수방류량, 비고', '80개 중 80개 일치'],
     ['승인이 이어진 댐(concernsDam)', '승인 CSV의 관측소코드', '80개 중 80개 일치'],
     ['운영행위가 나온 승인', '승인 CSV의 순차번호', '68개 중 68개 일치'],
     ['운영행위의 시각(operationTime)', '승인 CSV의 방류시작시간', '65개 중 65개 일치 (비고에 시각이 적힌 3개 제외)'],
     ['운영기준 값(criterionValue)', '규정 별표 3', '3개 중 3개 일치'],
     ['댐의 이름과 유형', 'K-water 댐 기본정보', '4개 중 4개 일치']],
    [3200, 3700, 3072])
add(label('남은 것'))
lis('비고 문구를 읽어 정한 운영행위의 종류 68개와 비고에 적힌 시각으로 읽은 3개는 비교할 원본 칸이 없어 확인하지 못했다.',
    '종류는 규칙 %d개로 정했다(예: 비고에 "증"이 있으면 증가방류). 68개를 하나씩 보는 대신 규칙 %d개가 맞는지를 실무자에게 검토받으면 된다.' % (NRULE, NRULE))

# ================================================================== 3
add(h1('3. 이 검증이 기대는 조건', pagebreak=False))
P('2장의 검증으로 KG 전부를 확인할 수 있었던 것은 아래 세 조건이 성립했기 때문이다.')
add(label('표 4. 세 조건과 확장했을 때'))
tbl([['조건', '지금', '확장했을 때'],
     ['규모가 작다', 'Entity %d개, Relation %d개, 속성값 %d개' % (264, len(REL), NPROP), '댐과 기간, 자료의 종류가 늘면 사람이 결과를 다 볼 수 없다.'],
     ['비교할 원본 칸이 있다', '값의 대부분이 표의 칸에서 왔다.', '규정 본문이나 보고서 같은 글에는 칸이 없다. 원본 대조를 프로그램으로 할 수 없다.'],
     ['규칙을 손으로 정할 수 있다', '승인 80건의 비고를 읽는 데 규칙 %d개를 썼다.' % NRULE, '글의 표현이 다양해지면 규칙을 계속 늘려야 한다.']],
    [2400, 3300, 4272])
lis('Shami 외(2026)는 규칙에 기반한 검증이 잘 정의되고 자주 나오는 사실에는 효과적이나 다양한 사실로 일반화되지 않고, 규칙을 사람이 정의하는 것이 어렵고 비싸다고 했다{SH}.',
    'Hofer 외(2023)는 구축 파이프라인의 단계들이 사람의 개입을 필요로 하는 것이 큰 자료로의 확장을 제한한다고 했다. 사람이 패턴을 만들어 관계를 추출하는 방식에 대해서도 사람의 개입이 제한 요인이라고 했다{HF}.')
KEY('정리', '지금의 검증은 지금의 만든 방식에 맞춘 것이다. 확장해서 만든 방식이 바뀌면 검증 방법도 다시 정해야 한다.')

# ================================================================== 4
add(h1('4. 확장하면 만드는 방식이 바뀐다', pagebreak=False))
add(label('① 확장하면 자료가 글로 넓어진다'))
lis('11/13 자료에서 준비한 질문 후보 82개에는 지금의 KG로 답할 수 없는 질문이 있다. 예: "연계운영규정에서 홍수기는 언제부터 언제까지야?", "댐에서 방류하기 전에 하류에 알려야 한다는 규정 있어?"',
    '이런 질문에 답하려면 규정의 본문 같은 글에서 내용을 가져와야 한다.')
add(label('② 필요한 구축 과업은 자료의 종류에 달려 있다'))
lis('Hofer 외(2023)는 KG 구축에 필요한 과업이 입력 자료의 종류에 달려 있다고 했다{HF}.')
tbl([['자료의 종류', '만드는 방식{HF}', '우리 자료'],
     ['정형 자료 (데이터베이스, 표)', '매핑 규칙으로 변환한다. 지식 추출은 필요하지 않을 수 있다.', '승인 CSV, 측정 CSV, 규정의 별표 (지금의 KG)'],
     ['글 (비정형 자료)', '지식 추출이 필요하다. 글에서 개체를 찾고, 그 개체를 KG의 Entity에 잇고, 개체 사이의 관계를 뽑는다.', '규정의 본문, 보고서 (확장 후)']],
    [2400, 4372, 3200])
lis('Hofer 외(2023)는 자료의 양이 많으므로 파이프라인을 가능한 한 자동화해야 한다고 했다. 다만 완전히 자동인 구축은 아직 이르고, 자료를 고르는 일과 온톨로지를 만드는 일에는 사람의 입력이 필요하다고 했다{HF}.')
add(label('③ 글에서 LLM으로 추출한 사례'))
lis('DDKG(Huang 외, 2026)는 댐 점검 자료의 결함 서술을 LLM으로 분류해 KG에 넣었다{HU}.',
    'Kommineni 외(2024)는 CQ의 답변과 온톨로지를 LLM에 주어 KG를 만들었다{KO}.')
KEY('정리', '확장하면 글에서 값을 자동으로 추출하게 된다. 이때는 2장의 원본 대조가 닿지 않는 추출을 따로 검증해야 한다.')

# ================================================================== 5
add(h1('5. 자동으로 만든 KG를 검증하는 방법', pagebreak=True))
P('글에서 자동으로 추출해 만든 KG를 검증하는 방법을 문헌에서 찾았다. 추출이 맞는지를 보는 방법 셋(5.1~5.3)이고, 적재는 지금과 같이 규칙 검사로 본다(5.4).')
add(h2('5.1 사람이 일부를 판정해 정확도를 추정: Gao 외(2019), Marchesin·Silvello(2025)'))
add(label('① 용어'))
tbl([['용어', '뜻', '예'],
     ['트리플', 'KG에 들어 있는 사실 하나. (대상, 관계, 대상 또는 값)의 세 부분으로 적는다. 문헌에서는 Relation, 속성값, Class 소속을 모두 트리플로 센다.', '(승인 A, concernsDam, 충주댐)\n"승인 A는 충주댐에 관한 것이다."'],
     ['KG의 정확도', '맞는 트리플 수 ÷ 전체 트리플 수. 트리플이 맞는지는 사람이 판정한다{GA}.', '트리플 100개 중 90개가 맞으면 90%'],
     ['오차 범위', '일부만 보고 계산한 정확도가 실제 정확도에서 벗어날 수 있는 폭.', '"90% ± 5%"는 실제 정확도가 85%~95% 사이에 있다고 본다는 뜻']],
    [1500, 5000, 3472])
add(label('② 방법'))
lis('큰 KG는 사람이 모두 판정할 수 없다. 그래서 일부를 뽑아 판정하고, 그 결과로 전체 정확도를 오차 범위와 함께 추정한다{GA}.',
    '판정자에게는 트리플과 그것이 나온 원문을 나란히 보이고, 원문이 그렇게 말하는지를 맞음 또는 틀림으로 받는다.')
tbl([['단계', '하는 일{GA}'],
     ['1. 대상을 뽑는다', 'KG의 대상(Entity) 가운데 n개를 무작위로 뽑는다. 딸린 트리플이 많은 대상일수록 뽑힐 확률이 높다.'],
     ['2. 트리플을 뽑는다', '뽑힌 대상마다 딸린 트리플 가운데 3~5개를 무작위로 뽑는다. 같은 대상의 트리플을 이어서 보면 판정이 빠르기 때문이다.'],
     ['3. 판정한다', '사람이 뽑힌 트리플을 하나씩 보고 맞음 또는 틀림으로 판정한다.'],
     ['4. 계산한다', '대상별 정확도 = 그 대상에서 맞은 트리플 수 ÷ 판정한 트리플 수\n전체 정확도의 추정값 = 대상별 정확도의 평균\n오차 범위 = 1.96 × √( (대상별 정확도 − 평균)²의 합 ÷ (n × (n − 1)) )'],
     ['5. 끝낼지 정한다', '오차 범위가 정해 둔 폭(예: 5%) 이하이면 끝낸다. 넘으면 1로 돌아가 대상을 더 뽑는다.']],
    [2200, 7772])
add(label('③ 계산 예 (설명을 위해 만든 숫자)'))
lis('대상 20개를 뽑아 대상마다 트리플 3개씩, 모두 60개를 판정했다. 18개 대상은 3개가 모두 맞았고(1.00), 2개 대상은 3개 중 2개가 맞았다(0.67).',
    '추정값 = (18 × 1.00 + 2 × 0.67) ÷ 20 = 0.967',
    '오차 범위 = 1.96 × √( 0.200 ÷ (20 × 19) ) = 0.045',
    '결과는 "정확도 96.7% ± 4.5%"이고, 오차 범위가 5% 이하이므로 여기서 끝낸다.')
add(label('④ 문헌의 결과'))
lis('트리플 약 200만 개의 영화 KG에서 정확도를 88% ± 5%로 추정했다. KG를 2,600만 개에서 1억 3천만 개까지 키워도 판정 비용이 거의 같았다{GA}.',
    '판정해야 하는 수는 KG의 크기가 아니라 정확도에 달려 있다. 정확도가 0.99인 자료는 31개, 0.91인 자료는 112개, 0.54인 자료는 257개쯤을 판정하고 끝났다{MA}.',
    'KG에 내용이 추가되면 처음부터 다시 하지 않는다. 추가된 부분에서만 새로 뽑아 판정하고, 앞의 결과와 합쳐 전체 정확도를 계산한다{GA}.',
    'Marchesin·Silvello(2025)는 Gao 외(2019)의 절차를 그대로 쓰고 4단계의 오차 범위 식만 바꿨다. 30개를 뽑아 모두 맞으면 오차 범위가 0으로 나오는 문제를 고친 것이다{MA}.')
add(label('⑤ 알 수 있는 것과 없는 것'))
lis('알 수 있는 것: KG에 들어 있는 것 가운데 맞는 비율.',
    '알 수 없는 것: 원문에 있는데 뽑지 못한 것. KG에 없으니 뽑힐 수 없다. 판정하지 않은 트리플 가운데 어느 것이 틀렸는지도 알 수 없다.')

add(h2('5.2 정답을 달아 둔 자료로 추출 도구를 채점: DDKG(Huang 외, 2026)'))
lis('KG가 아니라 KG를 만드는 도구(추출하는 LLM이나 규칙)를 평가하는 방법이다. Hogan 외(2021)는 KG를 만든 과정을 전문가나 정답 자료로 검증하는 것을 값이 사실과 맞는지 평가하는 선택지의 하나로 들었다{HO}.',
    'DDKG는 LLM이 분류한 결함 서술 약 12만 건 가운데 1,200개를 무작위로 뽑아 전문가가 검증하고 고쳐 정답으로 삼았다. 이 정답과 비교해 분류의 정밀도, 재현율, F1을 계산했다{HU}.',
    '알 수 있는 것: 뽑은 것 가운데 맞는 비율(정밀도)과, 뽑아야 할 것 가운데 뽑은 비율(재현율). 5.1의 방법이 보지 못하는 "빠뜨린 것"을 볼 수 있다.',
    '필요한 것: 사람이 만든 정답 자료. Hofer 외(2023)는 이런 정답 자료가 비용이 들어 대개 작다고 했다{HF}.')

add(h2('5.3 LLM이 판정: Shami 외(2026)'))
lis('사람 대신 LLM에게 트리플이 맞는지 묻는 방법이다.',
    'Shami 외(2026)는 사람이 맞고 틀림을 표시해 둔 사실 13,530개로 LLM의 판정을 시험했다. 결론은 "실제 KG 검증에 쓸 만큼 안정적이고 신뢰할 수 있지 않다"이다{SH}.',
    '틀린 것이 100개 중 1개꼴인 KG에서는 LLM이 틀린 것을 거의 찾지 못했다(F1 0.01~0.03){SH}.',
    'Kommineni 외(2024)의 실험에서는 같은 답변 200개를 사람과 LLM이 각각 판정했는데 42개에서 판정이 달랐다{KO}.')

add(h2('5.4 적재: 규칙 검사'))
lis('추출한 값이 맞는 Class와 Relation에 정한 형식으로 들어갔는지는 만든 방식과 상관없이 규칙 검사로 확인할 수 있다(2.2 ①).',
    'Shami 외(2026)는 규칙에 기반한 검증을 사람의 검증보다 "더 확장 가능한 대안"이라고 했다{SH}.')

add(label('표 5. 방법의 비교'))
tbl([['방법', '확인하는 것', '나오는 숫자', '필요한 것', '문헌의 평가'],
     ['5.1 일부를 판정해 추정', '추출 (맞게 뽑았는가)', '정확도 ± 오차 범위', '판정자', '큰 KG의 정확도를 평가하는 표준적인 접근{MA}'],
     ['5.2 추출 도구 채점', '추출 (맞게 뽑았는가, 빠뜨리지 않았는가)', '정밀도, 재현율, F1', '정답 자료', '정답 자료가 비용이 들어 대개 작다{HF}'],
     ['5.3 LLM이 판정', '추출 (맞게 뽑았는가)', '정확도', 'LLM', '아직 신뢰가 부족하다{SH}'],
     ['5.4 규칙 검사', '적재', '규칙별 위반 수', '규칙', '확장 가능하다{SH}']],
    [2100, 2400, 1900, 1300, 2272])

# ================================================================== 6
add(h1('6. 정리: 검증 방법은 KG를 만든 방식이 정한다', pagebreak=True))
add(label('표 6. 지금의 KG와 확장한 뒤의 KG'))
tbl([['', '지금의 KG', '확장한 뒤의 KG'],
     ['자료', '정형 자료 (표)', '정형 자료 + 글'],
     ['만든 방식', '칸의 값을 규칙으로 옮김', '글에서 값을 자동으로 추출 (방식은 정해지지 않음)'],
     ['추출의 검증', '원본 대조 (프로그램, 전부)', '사람이 일부를 판정해 추정(5.1), 정답 자료로 도구 채점(5.2)'],
     ['적재의 검증', '규칙 검사 (프로그램, 전부)', '규칙 검사 (프로그램, 전부)'],
     ['상태', '했다. 비고를 읽는 규칙 %d개의 검토가 남았다.' % NRULE, '구축 방식을 정한 뒤에 정한다.']],
    [1700, 3800, 4472])
lis('지금의 KG에 한 검증과 확장한 뒤에 할 검증은 같은 원칙의 두 경우다. 만든 방식이 정해지면 그 방식에서 틀릴 수 있는 곳이 정해지고, 검증은 그곳을 본다.',
    '확장한 뒤의 구축 방식은 아직 정하지 않았다. 그래서 5장의 방법은 선정한 것이 아니라 후보다.',
    '정하는 순서는 범위(CQ), 자료, 구축 방식, 검증 방법이다. 범위가 정해져야 어떤 자료가 필요한지 알 수 있고, 자료의 종류가 구축 방식을 정하며{HF}, 구축 방식이 검증 방법을 정한다.')

# ================================================================== 7
add(h1('7. 다음 계획', pagebreak=False))
FLOW('① CQ\n실무자 검토', '② 범위 확정,\n온톨로지 확장', '③ 자료\n수집', '④ 구축 방식\n선정', '⑤ 검증 방법\n확정과 적용')
tbl([['단계', '하는 일', '방법'],
     ['① CQ 실무자 검토', '질문 후보 82개를 실무자에게 검토받아 CQ를 확정한다.', '11/13 자료 2장'],
     ['② 범위 확정, 온톨로지 확장', '확정한 CQ의 70%로 온톨로지를 넓히고 30%로 평가한다.', '11/13 자료 2장'],
     ['③ 자료 수집', '넓힌 온톨로지에 넣을 자료를 모은다. 자료의 종류(표, 글)를 확인한다.', '—'],
     ['④ 구축 방식 선정', '자료의 종류에 맞는 구축 방식을 문헌에서 조사해 정한다.', '이번 자료 4장에서 이어서 조사'],
     ['⑤ 검증 방법 확정과 적용', '구축 방식에 맞춰 5장의 후보 가운데 정하고, 넓힌 KG에 적용한다.', '이번 자료 5장']],
    [2500, 4972, 2500])
lis('①의 검토를 받을 때 지금의 KG에서 남은 것(비고 문구를 읽는 규칙 %d개)도 함께 검토받는다.' % NRULE,
    '검증에서 틀린 것이 나오면 그 값을 만든 규칙이나 추출 방식을 고치고 다시 검증한다. 이것을 되풀이한다.')

# ================================================================== 참고문헌
add(h1('참고문헌'))
assert set(ORDER) == set(REFS), set(REFS) ^ set(ORDER)
for i, k in enumerate(ORDER, 1):
    add(L.para('[%d] %s' % (i, REFS[k]), 17))

T.save(OUT, ''.join(B), L.IMGS, page_numbers=True)
print('saved', OUT, 'refs', len(ORDER))
