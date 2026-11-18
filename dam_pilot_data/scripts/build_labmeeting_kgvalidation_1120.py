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
    ('이번 주', '① 선행 구축 연구가 KG를 어떻게 검증했는지 확인했다.\n· 네 편 모두 완성된 KG의 값을 검증하는 방법을 근거와 함께 제시하지 않았다(1장).\n\n② 검증의 목적을 정했다.\n· KG에 들어간 Entity, 속성값, Relation이 그것을 가져온 실제 자료의 내용과 맞는지 확인한다. 우리 KG는 확장되므로 방법은 확장 후에도 쓸 수 있어야 한다(2장).\n\n③ KG 검증을 다룬 문헌을 최신 논문에서 과거로 따라가 정리했다.\n· 형식과 제약은 도구로 검사하고, 값이 사실과 맞는지는 사람의 판정을 기준으로 삼는다.\n· 큰 KG에서는 사람이 일부만 판정해 전체 정확도를 오차 범위와 함께 추정한다. Gao 외(2019)가 제안했고 Marchesin·Silvello(2025)가 이어받았다(3장).\n\n④ 우리 KG에 적용하는 방안을 정리했다.\n· 지금은 해석해서 만든 값을 전부 판정하고, 확장 후에는 표본으로 판정한다(4장).'),
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
KEY('정리', '네 편 가운데 완성된 KG의 값을 원본과 대조한 것은 OntoDSMS뿐이고, 그 방법의 근거 문헌은 제시되지 않았다. 그래서 KG 검증을 직접 다룬 문헌에서 방법을 찾았다(3장).')

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
add(h1('3. KG 검증을 다룬 문헌', pagebreak=False))
add(h2('3.1 조사 경로'))
P('KG의 정확도 평가를 다룬 최신 논문에서 출발해, 그 방법이 나온 문헌을 과거로 따라갔다. 무엇을 사람이 판정해야 하는지는 KG 전반을 정리한 문헌과 LLM 검증을 시험한 문헌으로 보완했다.')
FLOW('Marchesin·Silvello (2025)\n표본 추정의 구간 계산 개선', 'Marchesin·Silvello (2024)\n구간 계산 개선', 'Gao 외 (2019)\n표본으로 KG 정확도 추정')
lis('Marchesin·Silvello(2025)는 KG 정확도 평가를 Gao 외(2019)가 정리한 문제로 놓고, 그 표본 추출 방식을 "KG 정확도 평가의 최신 기법"이라고 했다{MA}.',
    'Marchesin·Silvello(2024)는 원문을 구하지 못했다. 2025년 논문의 설명으로만 확인했다{MA}.',
    '보완: Hogan 외(2021) 7장{HO}, Shami 외(2026){SH}, Kommineni 외(2024){KO}.')

add(h2('3.2 무엇을 보느냐에 따라 방법이 다르다: Hogan 외 (2021)'))
P('Hogan 외는 KG 전반을 정리한 문헌으로, 7장에서 품질을 보는 관점(차원)과 관점마다 재는 방법을 정리했다{HO}. 표 4는 그 가운데 우리 목적(2장)에 해당하는 것이다.')
add(label(cite('표 4. 품질의 관점과 재는 방법{HO}')))
tbl([['관점', '뜻', '재는 방법'],
     ['구문 정확성', '값이 정해진 형식에 맞는가', '검증 도구로 평가할 수 있다.'],
     ['유효성', '정해 둔 제약을 어기지 않는가', '제약마다 위반 수를 센다.'],
     ['일관성', '서로 모순되는 내용이 없는가', '찾은 모순의 수를 센다.'],
     ['의미 정확성', '값이 실제 사실을 맞게 나타내는가', '"평가하기 어렵다."\n① 사람이 직접 확인한다.\n② 여러 출처와 자동으로 대조한다.\n③ KG를 만든 과정을 검증한다(전문가나 정답 자료로 정밀도를 잰다).'],
     ['완전성', '필요한 정보가 다 있는가', '정답 표본과 비교하거나, 완전한 원본에 대해 추출의 재현율을 잰다.']],
    [1700, 3300, 4972])
lis('형식, 제약, 모순은 도구로 검사할 수 있다. 값이 사실과 맞는지(의미 정확성)는 방법이 하나로 정해져 있지 않다.',
    '1장의 DDKG가 한 일(분류의 정밀도를 전문가 정답으로 잼)은 이 표의 ③에 해당한다.')

add(h2('3.3 값이 사실과 맞는지는 사람의 판정이 기준이다'))
add(label('① 사람의 판정'))
lis('Gao 외와 Marchesin·Silvello는 KG의 정확도를 "맞는 트리플의 비율"로 정의하고, 트리플이 맞는지는 사람의 판정으로 정한다고 했다{GA,MA}.',
    'Shami 외는 전문가의 수동 검증을 "가장 신뢰할 수 있는 선택지"라고 했다. 다만 큰 KG에서는 트리플 하나에 몇 분이 걸려 전부 하는 것이 불가능하다고 했다{SH}.')
add(label('② 자동 방법과 LLM 판정'))
lis('규칙·제약 기반 자동 검증은 더 확장 가능한 대안이지만, 잘 정의되고 자주 나오는 사실에만 효과적이고 규칙을 사람이 정의하는 것이 어렵고 비싸다{SH}.',
    'Shami 외는 LLM이 KG의 사실을 얼마나 잘 검증하는지를 사실 13,530개(YAGO, DBpedia, FactBench)로 시험했다. 결론은 "실제 KG 검증에 쓸 만큼 안정적이고 신뢰할 수 있지 않다"이다{SH}.',
    '정확도가 0.99인 YAGO에서 틀린 사실을 찾는 F1이 0.01~0.03이었다. 모델이 거의 모든 사실을 맞다고 답해 드문 오류를 찾지 못했다{SH}.',
    '웹 근거를 붙이거나 여러 모델을 다수결로 묶어도 일관되게 나아지지 않았다{SH}.',
    'Kommineni 외는 CQ에서 온톨로지와 KG를 만든 뒤 답변을 사람과 판정 LLM이 각각 평가했는데, 200개 가운데 42개에서 판정이 달랐다. 자동으로 만든 KG의 평가에는 사람이 참여하는 방식을 권했다{KO}.')
KEY('정리', '값이 사실과 맞는지는 사람의 판정을 기준으로 삼는다. 남는 문제는 2.2의 조건이다. KG가 커지면 사람이 전부 판정할 수 없다.')

add(h2('3.4 사람의 판정을 큰 KG에서도 쓰는 방법: Gao 외 (2019)'))
P('Gao 외는 사람이 KG의 일부만 판정해 전체 정확도를 추정하는 방법을 제안했다{GA}.')
add(label('① 문제'))
lis('정해 둔 오차 범위(예: 95% 수준에서 ±5%)를 만족하면서 사람의 판정 비용을 최소로 한다{GA}.')
add(label('② 판정 비용'))
lis('판정은 두 단계다. 이 대상이 무엇인지 파악하고(약 45초), 관계가 맞는지 확인한다(약 25초){GA}.',
    '같은 대상에 딸린 트리플을 이어서 판정하면 앞 단계를 한 번만 하면 된다{GA}.')
add(label('③ 뽑는 방법: 2단계 묶음 추출(TWCS)'))
FLOW('① 대상(Entity)을\n뽑는다', '② 그 대상의 트리플을\n3~5개 뽑는다', '③ 사람이\n판정한다', '④ 정확도와\n오차 범위를 계산한다')
lis('기준 방법보다 판정 비용이 최대 60% 줄었다{GA}.')
add(label('④ 결과'))
tbl([['내용', '결과{GA}'],
     ['영화 KG (트리플 약 200만)', '174개를 판정해 정확도 88% ± 5%로 추정했다.'],
     ['KG의 크기를 키웠을 때', '트리플 2,600만에서 1억 3천만까지 키워도 판정 비용이 거의 같았다. "비용은 KG의 크기에 민감하지 않다."'],
     ['비용을 좌우하는 것', 'KG의 정확도다. 정확도가 50% 근처일 때 비용이 가장 크고, 높을수록 적게 판정해도 된다.']],
    [3000, 6972])
add(label('⑤ KG가 늘어날 때'))
lis('추가분이 들어올 때마다 처음부터 다시 평가하지 않고, 앞서 판정한 결과를 재사용한다{GA}.',
    '추가분을 별도의 묶음(층)으로 보고 그 묶음에서만 새로 뽑는 방식이 가장 쌌다. 기준 방법보다 비용이 최대 80% 줄었다{GA}.')

add(h2('3.5 최신 연구: Marchesin·Silvello (2025)'))
P('Marchesin·Silvello는 Gao 외의 문제 정의, 추출 방식, 비용 함수를 그대로 쓰고, 오차 범위를 계산하는 방법을 바꿨다{MA}.')
add(label('① 절차'))
FLOW('① 조금\n뽑는다', '② 사람이\n판정한다', '③ 정확도와 구간을\n계산한다', '④ 오차가 한계\n이하이면 끝낸다')
lis('④에서 한계를 넘으면 ①로 돌아간다. 필요한 만큼만 판정하게 된다{MA}.')
add(label('② 바꾼 것'))
lis('Gao 외가 쓴 구간 계산법은 정확도가 0이나 1에 가까울 때 신뢰성 문제가 있다. 예를 들어 30개를 뽑아 모두 맞으면 구간의 폭이 0이 된다{MA}.',
    '베이즈 통계의 구간으로 바꾸고, 사전 정보를 고르지 않아도 되는 알고리즘(aHPD)을 제안했다{MA}.')
add(label(cite('표 5. 95% 수준에서 오차 ±5%에 이르는 데 필요한 판정 수{MA} (2단계 묶음 추출, aHPD, 1,000회 평균)')))
tbl([['자료', '사실 수', '정확도', '필요한 판정 수', '판정 시간'],
     ['YAGO', '1,386', '0.99', '31 ± 2', '0.41시간'],
     ['NELL', '1,860', '0.91', '112 ± 68', '1.40시간'],
     ['DBpedia', '9,344', '0.85', '222 ± 83', '2.55시간'],
     ['FactBench', '2,800', '0.54', '257 ± 39', '3.11시간']],
    [2200, 1800, 1600, 2400, 1972])
lis('1억 트리플의 합성 자료에서도 필요한 판정 수가 같은 자릿수였다. 논문은 "추정 방법은 자료의 크기에 영향을 받지 않고, 성능을 좌우하는 것은 정확도 수준"이라고 했다{MA}.',
    '결론에서 실무자에게 2단계 묶음 추출과 aHPD를 함께 쓸 것을 권했다{MA}.',
    '내용이 계속 바뀌는 KG에 적용하는 것은 향후 과제로 남겼다{MA}. 이 부분의 근거는 Gao 외의 방법(3.4 ⑤)이다.')
KEY('정리', '값이 사실과 맞는지는 사람의 판정이 기준이고{GA,MA,SH}, 큰 KG에서는 일부만 판정해 전체 정확도를 오차 범위와 함께 추정한다{GA,MA}. 필요한 판정 수는 KG의 크기가 아니라 정확도에 달려 있어{GA,MA}, 2.2의 조건을 만족한다.')

# ================================================================== 4. 적용
add(h1('4. 우리 연구에 적용', pagebreak=True))
add(h2('4.1 확인할 것마다의 방법'))
add(label('표 6. 검증 방법과 지금 상태'))
tbl([['확인할 것', '방법', '근거', '지금 상태'],
     ['형식과 제약', '규칙 검사. Relation 양 끝의 Class, 필수 속성, 값의 형식, 근거 연결, 승인과 운영행위의 댐 일치.', '유효성: 제약마다 위반 수를 센다{HO}.', '규칙 5개, 위반 0건 (10월)'],
     ['그대로 옮긴 값', '원본 대조. KG의 값을 원본 자료의 값과 비교한다.', '의미 정확성 ②: 출처와 대조한다{HO}.', '승인 80건, 운영기준 3건 일치 (10월)'],
     ['해석해서 만든 값', '사람의 판정.', '사람의 판정이 기준이다{GA,MA,SH}.', '사람의 판정은 하지 않음. 측정값과의 자동 대조만 함: 일치 %d, 변화 미검출 %d, 판정 불가 %d (10월)' % (MC['일치'], MC['변화미검출'], MC['판정불가(방향 없음)'])]],
    [1700, 3600, 2672, 2000])
add(h2('4.2 사람의 판정: 지금과 확장 후'))
tbl([['', '지금', '확장 후'],
     ['대상', '해석해서 만든 Operation 68개와 그에 이어진 Relation', '추가된 Entity와 Relation 가운데 해석해서 만든 것'],
     ['판정 범위', '전부', '표본'],
     ['이유', '표 5에서 필요한 판정 수는 약 30~260개다. 지금의 규모는 이 수와 비슷해 표본으로 줄어드는 것이 없다.', '전부 판정할 수 없다{GA,MA,SH}.']],
    [1500, 4236, 4236])
add(label('표 7. 확장 후 표본 판정의 설정'))
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
