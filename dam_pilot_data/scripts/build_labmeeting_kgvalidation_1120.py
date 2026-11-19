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

REFS = {
    'HU': 'Huang, J., Hou, W., Zhang, S., Du, Z., & Yin, J. (2026). Dam defects ontology and knowledge graph construction from multi-source hazard data using large language models. Advanced Engineering Informatics, 76, 104987.',
    'ZH': 'Zhou, Y., Bao, T., Shu, X., Li, Y., & Li, Y. (2023). BIM and ontology-based knowledge management for dam safety monitoring. Automation in Construction, 145, 104649.',
    'LI': 'Li, S., Erickson, C., Zajac, M., Guo, X., Duan, Q., & Gong, J. (2025). A semi-automated framework for flood ontology construction with an application in risk communication. Water, 17, 2801.',
    'PU': 'Purohit, S., Chin, G., Mackey, P. S., & Cottam, J. A. (2024). GraphAide: Advanced graph-assisted query and reasoning system. 2024 IEEE International Conference on Big Data, 3485–3493.',
    'HO': 'Hogan, A., Blomqvist, E., Cochez, M., et al. (2021). Knowledge graphs. ACM Computing Surveys, 54(4), Article 71. (7장 Quality Assessment)',
    'SH': 'Shami, F., Marchesin, S., & Silvello, G. (2026). Benchmarking large language models for knowledge graph validation. arXiv:2602.10748.',
    'HM': 'Huaman, E. (2026). Knowledge graphs quality assessment in the era of LLMs: A conceptual framework. arXiv:2610.31684.',
    'AM': 'Al Mustafa, T., & König-Ries, B. (2026). Benchmarking automated knowledge graph construction from semi-structured data. arXiv:2609.26985.',
    'KO': 'Kommineni, V. K., König-Ries, B., & Samuel, S. (2024). From human experts to machines: An LLM supported approach to ontology and knowledge graph construction. arXiv:2403.08345.',
    'MA': 'Marchesin, S., & Silvello, G. (2025). Credible intervals for knowledge graph accuracy estimation. Proceedings of the ACM on Management of Data (SIGMOD). arXiv:2502.18961.',
    'GA': 'Gao, J., Li, X., Xu, Y. E., Sisman, B., Dong, X. L., & Yang, J. (2019). Efficient knowledge graph accuracy evaluation. Proceedings of the VLDB Endowment, 12(11), 1679–1691. arXiv:1907.09657.',
}

# ================================================================== 표지·요약
add(title('KG 검증 방법 조사와 적용 방안', '').replace('<w:br/><w:t xml:space="preserve"></w:t>', ''))
add(dateline('2026.11.20 · 문경민'))
add(h1('요약'))
add(table([[a, cite(b)] for a, b in [
    ('지난주', '· 온톨로지 구축 방법을 문헌으로 정리하고, CQ를 이용한 전문가 검토를 구체화했다.\n· 온톨로지의 검증만 다뤘다. KG 자체를 검증하는 방법을 찾아야 한다.'),
    ('이번 주', '① 선행 구축 연구가 KG를 어떻게 검증했는지 확인했다.\n· 네 편 모두 완성된 KG의 값을 검증하는 방법을 근거와 함께 제시하지 않았다(1장).\n\n② 검증의 목적을 정했다.\n· KG에 들어간 Entity, 속성값, Relation이 그것을 가져온 실제 자료의 내용과 맞는지 확인한다. 우리 KG는 확장되므로 방법은 확장 후에도 쓸 수 있어야 한다(2장).\n\n③ 최신 문헌이 다룬 KG 검증 방법을 비교해 목적에 맞는 방법을 골랐다.\n· 형식과 제약은 규칙 검사, 그대로 옮긴 값은 원본 대조, 해석해서 만든 값은 사람이 일부를 판정해 전체 정확도를 추정하는 방법(Marchesin·Silvello, 2025)을 골랐다.\n· 고른 방법이 인용한 과거 문헌으로 따라가, 이 방법이 Gao 외(2019)에서 나왔음을 확인하고 내용을 정리했다(3장).\n\n④ 우리 KG에 적용하는 방안을 정리했다.\n· 지금은 해석해서 만든 값을 전부 판정하고, 확장 후에는 표본으로 판정한다(4장).'),
    ('다음 주', '· 판정 기준과 판정표를 만든다.\n· 판정자를 정한다.')]], [1300, 8672], header=False, firstcol=True, sz=22))

# ================================================================== 1. 선행 구축 연구
add(h1('1. 선행 구축 연구는 KG를 어떻게 검증했나', pagebreak=True))
P('지난주에는 온톨로지의 검증을 다뤘다. CQ에 답이 나오는지를 보는 것은 KG를 쓸 수 있는지의 확인이고, KG에 들어간 값이 맞는지는 따로 확인해야 한다. 먼저 지금까지 참고한 구축 연구 네 편이 이 부분을 어떻게 했는지 확인했다.')
add(label('표 1. 선행 구축 연구의 KG 검증'))
tbl([['연구', '검증한 것', '방법', '방법의 근거 문헌'],
     ['OntoDSMS (2023){ZH}', '옮긴 KG가 원래 데이터베이스와 같은 결과를 내는가', '같은 내용의 질의를 KG(SPARQL)와 원래 데이터베이스(SQL)에 실행해 결과를 대조했다.', '인용 없음'],
     ['DDKG (2026){HU}', 'KG를 만드는 데 쓴 LLM 분류의 성능', '기계가 라벨을 단 결함 서술 가운데 1,200개를 전문가가 검증·수정해 정답으로 삼고, 분류의 정밀도, 재현율, F1을 계산했다. 완성된 KG의 평가는 향후 과제로 남겼다.', '인용 없음'],
     ['홍수 온톨로지 (2025){LI}', '온톨로지', '구조 지표, 평가용 CQ의 개념 포괄도, 전문가 검토. KG의 값은 검증 대상이 아니다.', '—'],
     ['GraphAide (2024){PU}', '구축 구성요소와 답변', '답변 평가 지표(RAGAS). 정식 정량 평가는 향후 작업으로 남겼다.', '—']],
    [1900, 2500, 4172, 1400])
KEY('정리', '네 편 가운데 완성된 KG의 값을 원본과 대조한 것은 OntoDSMS뿐이고, 그 방법의 근거 문헌은 제시되지 않았다. 그래서 KG 검증을 직접 다룬 최신 문헌에서 방법을 비교해 골랐다(3장).')

# ================================================================== 2. 목적과 조건
add(h1('2. 검증의 목적과 조건', pagebreak=True))
add(h2('2.1 목적'))
P('KG에 들어간 Entity, 속성값, Relation이 그것을 가져온 실제 자료의 내용과 맞는지 확인한다.')
add(label('표 2. 확인할 것'))
tbl([['확인할 것', '뜻', '우리 KG의 예'],
     ['Entity', '자료에 있는 대상이 KG에 맞게 들어갔는가', 'Approval 80개, Operation 68개, HydrometeorologicalState 24개'],
     ['속성값', '그 대상의 값이 자료의 값과 같은가', 'approvalTime, approvalContent, criterionValue'],
     ['Relation', '대상끼리의 연결이 자료의 내용과 맞는가', '이 승인이 이 댐에 관한 것인가(concernsDam). 이 승인이 이 운영행위를 허가했는가(authorizes).']],
    [1500, 4000, 4472])
P('값이 KG에 들어온 경로는 둘이다. 확인하는 방법이 서로 다르다.')
add(label('표 3. 값이 들어온 경로와 지금 KG의 Relation 수 (전체 %d개)' % len(REL)))
tbl([['경로', '뜻', 'Relation', '개수'],
     ['자료에서 그대로 옮김', '자료의 칸에 있는 값을 그대로 넣었다.', 'concernsDam %d, hasHydrometeorologicalState %d, supportedBy %d' % (RO[('concernsDam', 'real')], RO[('hasHydrometeorologicalState', 'real')], RO[('supportedBy', 'real')]), str(ORI['real'])],
     ['자료를 해석해서 만듦', '승인 기록의 비고 문구에서 운영행위를 뽑고, 그 운영행위에 댐, 승인, 근거를 이었다. 운영기준은 댐 이름을 맞춰 이었다.', 'performedOnDam %d, supportedBy %d, authorizes %d, appliesToDam %d' % (RO[('performedOnDam', 'derived')], RO[('supportedBy', 'derived')], RO[('authorizes', 'constructed')], RO[('appliesToDam', 'name-match')]), str(ORI['derived'] + ORI['constructed'] + ORI['name-match'])]],
    [2000, 3600, 3572, 800])
lis('그대로 옮긴 값은 자료의 값과 같은지를 보면 된다.',
    '해석해서 만든 값은 그 해석이 자료의 내용과 맞는지를 봐야 한다. 예: 비고 문구에서 뽑은 운영행위의 종류(operationType).')
add(h2('2.2 조건'))
lis('우리 KG는 확장된다. 댐, 자료의 종류, 글에서 뽑는 정보가 늘어난다.',
    '검증 방법은 확장 후에도 쓸 수 있어야 한다.')

# ================================================================== 3. 문헌
add(h1('3. KG 검증 방법의 비교와 선정', pagebreak=False))
P('최신 문헌이 다룬 KG 검증 방법을 비교하고(3.1), 2장의 목적과 조건에 맞는 방법을 골랐다(3.2). 고른 방법의 내용을 정리하고(3.3), 그 논문이 인용한 과거 문헌으로 따라가 방법이 어디서 나왔는지 확인했다(3.4).')
add(h2('3.1 최신 문헌이 다룬 KG 검증 방법'))
P('2021년 이후 문헌 가운데 KG의 검증이나 품질 평가를 직접 다룬 여섯 편에서 방법을 뽑았다.')
add(label('표 4. 최신 문헌의 KG 검증 방법 비교'))
tbl([['방법', '확인하는 것', '문헌의 평가', 'KG가 커질 때'],
     ['품질 관점(차원)별 지표로 평가{HM,AM}', '형식, 정확성, 일관성, 완전성 등 여러 관점', 'Huaman은 관점 24개와 절차를 제안했으나 KG에 적용한 결과가 없다{HM}. Al Mustafa·König-Ries는 표에서 만든 KG의 지표를 정의했으나 심사 전 원고이고 결과 장이 비어 있다{AM}.', '적용 결과가 없어 확인할 수 없다.'],
     ['규칙·제약 검사{HO,SH}', '값의 형식, 제약 위반, 모순', '검증 도구로 평가하고 위반 수를 센다{HO}. 잘 정의된 사실에는 효과적이나 다양한 사실로 일반화되지 않고, 규칙을 사람이 정의하는 것이 어렵고 비싸다{SH}.', '"더 확장 가능한 대안"{SH}'],
     ['전문가가 전부 판정{SH}', '값이 사실과 맞는가', '"가장 신뢰할 수 있는 선택지"{SH}', '트리플 하나에 몇 분이 걸려 큰 KG에서는 불가능하다{SH}.'],
     ['LLM이 판정{SH,KO}', '값이 사실과 맞는가', '"실제 KG 검증에 쓸 만큼 안정적이고 신뢰할 수 있지 않다"{SH}. 사람과 판정 LLM이 200개 가운데 42개에서 달랐다{KO}.', '가능하나 신뢰가 부족하다.'],
     ['사람이 일부를 판정해 전체 정확도를 추정{MA}', '값이 사실과 맞는가', '큰 KG의 정확도를 평가하는 "표준적인 접근"이다. 추정에 오차 범위를 붙여 통계적으로 보장한다{MA}.', '필요한 판정 수가 KG의 크기에 영향을 받지 않는다{MA}.']],
    [2100, 1900, 3872, 2100])
lis('Shami 외는 LLM의 판정을 사실 13,530개(YAGO, DBpedia, FactBench)로 시험했다. 정확도가 0.99인 YAGO에서 틀린 사실을 찾는 F1이 0.01~0.03이었다. 모델이 거의 모든 사실을 맞다고 답해 드문 오류를 찾지 못했다. 웹 근거를 붙이거나 여러 모델을 다수결로 묶어도 일관되게 나아지지 않았다{SH}.',
    'Hogan 외는 값이 사실과 맞는지(의미 정확성)를 "평가하기 어렵다"고 하고 선택지를 셋 들었다. 사람이 직접 확인한다, 여러 출처와 자동으로 대조한다, KG를 만든 과정을 검증한다{HO}. 1장의 DDKG가 한 일은 셋째에 해당한다.')

add(h2('3.2 목적에 맞는 방법의 선정'))
P('2장에서 확인할 것을 값이 들어온 경로로 나눴다(표 3). 경로마다 표 4에서 맞는 방법을 골랐다.')
add(label('표 5. 선정한 방법과 이유'))
tbl([['확인할 것', '선정한 방법', '이유'],
     ['형식과 제약', '규칙·제약 검사', '형식과 제약 위반은 도구로 평가할 수 있고{HO}, 확장 가능하다{SH}.'],
     ['그대로 옮긴 값', '원본 대조', '기준이 되는 원본 값이 있어 사람의 판단 없이 비교할 수 있다. 출처와의 대조는 의미 정확성을 평가하는 선택지의 하나다{HO}.'],
     ['해석해서 만든 값', '사람이 일부를 판정해 전체 정확도를 추정', '비교할 원본 값이 없어 판단이 필요하다. 판단은 사람의 판정이 가장 신뢰할 수 있고{SH}, LLM의 판정은 아직 신뢰가 부족하다{SH,KO}. 사람이 전부 판정하는 것은 확장 후에 쓸 수 없고{SH}, 일부를 판정해 추정하는 방법은 KG의 크기에 영향을 받지 않는다{MA}.']],
    [1700, 2600, 5672])
lis('품질 관점별 지표로 평가하는 방법은 고르지 않았다. 적용한 결과가 보고되지 않았다{HM,AM}.',
    '규칙 검사와 원본 대조는 10월에 했다(4장). 아래에서는 새로 고른 방법인 표본 추정을 정리한다.')

add(h2('3.3 선정한 방법: Marchesin·Silvello (2025)'))
add(label('① 문제'))
lis('KG의 정확도는 맞는 트리플의 비율이고, 트리플이 맞는지는 사람의 판정으로 정한다{MA}.',
    '실제 KG는 수억에서 수십억 개의 사실을 담아 모두 판정할 수 없다. 그래서 표본을 뽑아 정확도를 추정하고 오차 범위를 붙인다{MA}.',
    '목표는 오차 범위가 정해 둔 한계 이하가 되게 하면서 사람의 판정 비용을 최소로 하는 것이다{MA}.')
add(label('② 절차'))
FLOW('① 조금\n뽑는다', '② 사람이\n판정한다', '③ 정확도와 구간을\n계산한다', '④ 오차가 한계\n이하이면 끝낸다')
lis('④에서 한계를 넘으면 ①로 돌아간다. 필요한 만큼만 판정하게 된다{MA}.',
    '뽑는 방법은 2단계 묶음 추출(TWCS)이다. 대상(Entity)을 먼저 뽑고 그 대상의 트리플을 몇 개씩 뽑는다. 논문은 이것을 "KG 정확도 평가의 최신 기법"이라고 했고, Gao 외(2019)의 방법이다{MA}.')
add(label('③ 이 논문이 더한 것'))
lis('앞선 연구의 구간 계산법은 정확도가 0이나 1에 가까울 때 신뢰성 문제가 있다. 예를 들어 30개를 뽑아 모두 맞으면 구간의 폭이 0이 된다{MA}.',
    '베이즈 통계의 구간으로 바꾸고, 사전 정보를 고르지 않아도 되는 알고리즘(aHPD)을 제안했다{MA}.')
add(label(cite('표 6. 95% 수준에서 오차 ±5%에 이르는 데 필요한 판정 수{MA} (2단계 묶음 추출, aHPD, 1,000회 평균)')))
tbl([['자료', '사실 수', '정확도', '필요한 판정 수', '판정 시간'],
     ['YAGO', '1,386', '0.99', '31 ± 2', '0.41시간'],
     ['NELL', '1,860', '0.91', '112 ± 68', '1.40시간'],
     ['DBpedia', '9,344', '0.85', '222 ± 83', '2.55시간'],
     ['FactBench', '2,800', '0.54', '257 ± 39', '3.11시간']],
    [2200, 1800, 1600, 2400, 1972])
lis('1억 트리플의 합성 자료에서도 필요한 판정 수가 같은 자릿수였다. 논문은 "추정 방법은 자료의 크기에 영향을 받지 않고, 성능을 좌우하는 것은 정확도 수준"이라고 했다{MA}.',
    '결론에서 실무자에게 2단계 묶음 추출과 aHPD를 함께 쓸 것을 권했다{MA}.',
    '내용이 계속 바뀌는 KG에 적용하는 것은 향후 과제로 남겼다{MA}.')

add(h2('3.4 이 방법이 나온 과거 문헌'))
P('Marchesin·Silvello(2025)의 관련 연구 절을 따라 과거로 갔다{MA}.')
FLOW('Marchesin·Silvello (2025)\n구간 계산 개선', 'Marchesin·Silvello (2024)\n구간 계산 개선', 'Gao 외 (2019)\n표본으로 KG 정확도 추정')
add(label(cite('표 7. 표본 추정의 계보{MA}')))
tbl([['연구', '한 일', '뒤 연구가 고친 점'],
     ['KGEval (2017)', '사람이 판정한 사실에서 규칙으로 다른 사실의 맞고 틀림을 추론했다.', '큰 KG로 확장되지 않고, 추론이 확률적이어서 오류가 퍼진다.'],
     ['Gao 외 (2019)', '표본 추출과 통계적 보장이 있는 추정으로 바꿨다. 2단계 묶음 추출을 제안했다.', '구간 계산법에 신뢰성 문제가 있다.'],
     ['Marchesin·Silvello (2024)', '구간 계산법을 바꿨다.', '한 번의 평가 결과에 대해 확률로 해석할 수 없다.'],
     ['Marchesin·Silvello (2025)', '베이즈 구간과 aHPD를 제안했다.', '—']],
    [2400, 4000, 3572])
lis('KGEval과 Marchesin·Silvello(2024)는 원문을 읽지 못했다. 2025년 논문의 설명이다{MA}.')
add(label('Gao 외 (2019)의 내용'))
lis('문제를 처음 정리했다. 정해 둔 오차 범위(예: 95% 수준에서 ±5%)를 만족하면서 사람의 판정 비용을 최소로 한다{GA}.',
    '판정은 두 단계다. 이 대상이 무엇인지 파악하고(약 45초), 관계가 맞는지 확인한다(약 25초). 같은 대상에 딸린 트리플을 이어서 판정하면 앞 단계를 한 번만 하면 된다{GA}.',
    '그래서 대상을 먼저 뽑고 그 대상의 트리플을 3~5개씩 판정한다(2단계 묶음 추출). 기준 방법보다 판정 비용이 최대 60% 줄었다{GA}.',
    '트리플 약 200만 개의 영화 KG에서 174개를 판정해 정확도 88% ± 5%로 추정했다{GA}.',
    '트리플 2,600만에서 1억 3천만까지 키워도 판정 비용이 거의 같았다. 비용을 좌우하는 것은 KG의 정확도다{GA}.',
    'KG가 늘어날 때는 처음부터 다시 평가하지 않고 앞서 판정한 결과를 재사용한다. 추가분을 별도의 묶음(층)으로 보고 그 묶음에서만 새로 뽑는 방식이 가장 쌌다. 기준 방법보다 비용이 최대 80% 줄었다{GA}.')
KEY('정리', '최신 문헌의 방법 가운데, 해석해서 만든 값에는 사람이 일부를 판정해 전체 정확도를 추정하는 방법을 골랐다. 사람의 판정이 가장 신뢰할 수 있고{SH}, 이 방법은 KG의 크기에 영향을 받지 않아{MA,GA} 2.2의 조건을 만족한다. 방법은 Gao 외(2019)에서 나와 Marchesin·Silvello(2025)까지 이어졌고, KG가 늘어날 때의 절차는 Gao 외에 있다{GA}.')

# ================================================================== 4. 적용
add(h1('4. 우리 연구에 적용', pagebreak=True))
add(h2('4.1 확인할 것마다의 방법'))
add(label('표 8. 검증 방법과 지금 상태'))
tbl([['확인할 것', '방법', '근거', '지금 상태'],
     ['형식과 제약', '규칙 검사. Relation 양 끝의 Class, 필수 속성, 값의 형식, 근거 연결, 승인과 운영행위의 댐 일치.', '표 5의 이유{HO,SH}.', '규칙 5개, 위반 0건 (10월)'],
     ['그대로 옮긴 값', '원본 대조. KG의 값을 원본 자료의 값과 비교한다.', '표 5의 이유{HO}.', '승인 80건, 운영기준 3건 일치 (10월)'],
     ['해석해서 만든 값', '사람의 판정.', '표 5의 이유{SH,MA}.', '사람의 판정은 하지 않음. 측정값과의 자동 대조만 함: 일치 %d, 변화 미검출 %d, 판정 불가 %d (10월)' % (MC['일치'], MC['변화미검출'], MC['판정불가(방향 없음)'])]],
    [1700, 3600, 2672, 2000])
add(h2('4.2 사람의 판정: 지금과 확장 후'))
tbl([['', '지금', '확장 후'],
     ['대상', '해석해서 만든 Operation 68개와 그에 이어진 Relation', '추가된 Entity와 Relation 가운데 해석해서 만든 것'],
     ['판정 범위', '전부', '표본'],
     ['이유', '표 6에서 필요한 판정 수는 약 30~260개다. 지금의 규모는 이 수와 비슷해 표본으로 줄어드는 것이 없다.', '전부 판정할 수 없다{GA,MA,SH}.']],
    [1500, 4236, 4236])
add(label('표 9. 확장 후 표본 판정의 설정'))
tbl([['정할 것', '문헌의 값', '우리'],
     ['판정 단위', '트리플{GA,MA}', 'Relation 하나, 속성값 하나'],
     ['묶음', '주어가 같은 트리플{GA,MA}', 'Entity (예: Operation 하나와 그에 이어진 Relation)'],
     ['묶음당 판정 수', '3~5개{GA}', '같게 한다.'],
     ['끝내는 조건', '95% 수준에서 오차 ±5%{GA,MA}', '같게 한다.'],
     ['구간 계산', 'aHPD{MA}', '같게 한다.'],
     ['KG가 늘어날 때', '추가분을 별도의 층으로 보고 그 층에서만 뽑는다{GA}.', '댐이나 자료를 추가할 때마다 한 층으로 둔다.']],
    [2000, 3700, 4272])
add(label('한계'))
lis('판정자가 정해지지 않았다. 문헌의 실험 자료는 일반 지식(인물, 영화, 스포츠)이고 판정자는 크라우드 작업자였다{GA,MA}. 댐 운영은 전문 분야여서 판정자가 실무자나 전문가여야 한다.',
    '문헌은 사실 하나를 보통 3~5명이 판정한다고 했다{MA}. 우리가 그만큼의 판정자를 구할 수 있는지는 정해지지 않았다.',
    '표본 판정은 정확도(값이 맞는가)만 추정한다. 빠진 것이 없는지는 원본 대조로 따로 봐야 한다.',
    '값이 들어온 경로별로 정확도를 따로 내는 것은 문헌에 없다. Gao 외는 Relation 종류별 정확도를 향후 과제로 남겼다{GA}.',
    'Marchesin·Silvello(2024)는 원문을 읽지 못했다.')
KEY('정리', '형식과 제약은 규칙 검사로, 그대로 옮긴 값은 원본 대조로 확인했다. 해석해서 만든 값은 사람의 판정으로 확인하며, 지금은 전부 판정하고 확장 후에는 Gao 외와 Marchesin·Silvello의 표본 방식으로 판정한다.')

# ================================================================== 5. 다음 계획
add(h1('5. 다음 계획', pagebreak=False))
lis('판정 기준을 정한다. 무엇에 비추어 맞다고 할지를 Relation과 속성마다 적는다.',
    '판정표를 만든다. Operation 68개마다 원본 승인 기록의 비고 문구와 KG의 값을 나란히 보인다.',
    '판정자를 정한다. 지난주에 정리한 CQ 검토와 같은 실무자에게 함께 받을 수 있는지 확인한다.')

# ================================================================== 참고문헌
add(h1('참고문헌'))
assert set(ORDER) == set(REFS), set(REFS) ^ set(ORDER)
for i, k in enumerate(ORDER, 1):
    add(L.para('[%d] %s' % (i, REFS[k]), 17))

T.save(OUT, ''.join(B), L.IMGS, page_numbers=True)
print('saved', OUT, 'refs', len(ORDER))
