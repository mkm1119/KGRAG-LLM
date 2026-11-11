#!/usr/bin/env python3
"""랩미팅 자료(docx): 온톨로지 검증 방법 — 선행연구 분석과 우리 구조에 맞는 방안, 향후 계획.
서식은 11/06 자료(build_labmeeting_how_kg2.py)와 같다(labdoc_lib, 같은 템플릿).
근거 문헌: references/evidence_literature/ (해석: lab_meeting/paper_review/검증부분_해석*.md)
11/12 사용자 메모 반영: 방법론 설명 표, CQ로 검증하는 방법 비교, 다른 검증 방법과의 비교(문헌 근거),
제안 방법을 단계와 예시로, 향후 계획은 업무 질문 82개로, 참고문헌 번호.
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

# ------------------------------------------------------------------ 사실: 업무 질문 82개와 예시 질문
R5 = os.path.join(ROOT, '05_retrieval')
Q82 = {q['id']: q for q in json.load(open(os.path.join(R5, 'question_set_tasks82.json'), encoding='utf-8'))}
assert len(Q82) == 82
EX_OK, EX_EXT = Q82['q017'], Q82['q069']
assert EX_OK['question'] == '2017년 8월 소양강댐 방류 승인 내역 알려줘' and EX_OK['gold']['intent'] == ['CQ4']
assert EX_EXT['question'] == '소양강댐 계획홍수위랑 상시만수위 알려줘' and EX_EXT['expect'] == 'extend'

# ------------------------------------------------------------------ 참고문헌 (본문에 처음 나온 순서로 번호)
REFS = {
    'WL': 'Watkiss-Leek, E., Alharbi, R., Rostron, H., Ng, A., et al. (2026). IDEA2: Expert-in-the-loop competency question elicitation for collaborative ontology engineering. arXiv:2604.01344.',
    'NOY': 'Noy, N. F., & McGuinness, D. L. (2001). Ontology development 101: A guide to creating your first ontology. Stanford University.',
    'LIP': 'Lippolis, A. S., Saeedizade, M. J., Keskisärkkä, R., Gangemi, A., Blomqvist, E., & Nuzzolese, A. G. (2025). Large language models assisting ontology evaluation. arXiv:2507.14552.',
    'KK': 'Keet, C. M., & Khan, Z. C. (2024). Discerning and characterising types of competency questions for ontologies. arXiv:2412.13688.',
    'LI': 'Li, S., Erickson, C., Zajac, M., Guo, X., Duan, Q., & Gong, J. (2025). A semi-automated framework for flood ontology construction with an application in risk communication. Water, 17, 2801.',
    'HU': 'Huang, J., Hou, W., Zhang, S., Du, Z., & Yin, J. (2026). Dam defects ontology and knowledge graph construction from multi-source hazard data using large language models. Advanced Engineering Informatics, 76, 104987.',
    'ZH': 'Zhou, Y., Bao, T., Shu, X., Li, Y., & Li, Y. (2023). BIM and ontology-based knowledge management for dam safety monitoring. Automation in Construction, 145, 104649.',
    'FOCA': 'Bandeira, J., Bittencourt, I. I., Espinheira, P., & Isotani, S. (2016). FOCA: A methodology for ontology evaluation. arXiv:1612.03353.',
    'RC': 'Raad, J., & Cruz, C. (2015). A survey on ontology evaluation methods. KEOD 2015, 179–186.',
    'AL': 'Alharbi, R., Tamma, V., Payne, T. R., & de Berardinis, J. (2025). A comparative study of competency question elicitation methods from ontology requirements. arXiv:2507.02989.',
    'ZA': 'Zaveri, A., Rula, A., Maurino, A., Pietrobon, R., Lehmann, J., & Auer, S. (2016). Quality assessment for linked data: A survey. Semantic Web, 7(1), 63–93.',
    'PA': 'Paulheim, H. (2017). Knowledge graph refinement: A survey of approaches and evaluation methods. Semantic Web, 8(3), 489–508.',
}
ORDER = []


def cite(t):
    def rep(m):
        keys = m.group(1).split(',')
        for k in keys:
            if k not in ORDER:
                ORDER.append(k)
        return '[' + ', '.join(str(ORDER.index(k) + 1) for k in keys) + ']'
    return re.sub(r'\{([A-Z,]+)\}', rep, t)


B = []
add = B.append


def lis(*items):
    for t in items:
        add(li(cite(t)))


def tbl(rows, widths):
    add(table([[cite(c) for c in r] for r in rows], widths, header=True, firstcol=False))


# ================================================================== 표지·요약
add(title('온톨로지 검증 방법', '선행연구 분석과 우리 구조에 맞는 방안'))
add(dateline('2026.11 · 문경민'))
add(h1('요약'))
lis('조사 범위: 방법론·서베이(일반) → 수자원·재난 분야 → 댐 분야 순으로 좁혀 가며, 출발 논문의 참고문헌을 따라가 조사해 보았다.',
    '주요 온톨로지 구축 방법론은 역량 질문(CQ)을 범위 설정과 검증의 기본으로 두며, 수자원·재난 분야와 댐 분야의 온톨로지 연구도 이를 따랐다.',
    'CQ로 검증하는 방법은 질의 실행 대조, 개념 포괄도, LLM 보조, 점검 항목 방식이 있으며, 어느 방법이든 CQ의 품질이 결과를 좌우한다.',
    '→ 전문가 검토로 CQ 세트를 확정해 구성용과 검증용으로 나누고, 검증용 CQ를 질의로 실행해 온톨로지를 시험하며, 추론기로 일관성을 함께 확인하는 방안을 제안한다.',
    '향후: 업무 질문 82개를 전문가 검토로 검증된 CQ로 만들어 이 방안을 적용하고, 그다음 KG 자체의 검증 방법을 조사해 적용한다.')

# ================================================================== 1. 온톨로지 검증
add(h1('1. 온톨로지 검증', pagebreak=True))
add(h2('1.1 선행연구는 온톨로지를 어떻게 만들었나'))
lis('주요 온톨로지 구축 방법론은 공통으로 역량 질문(CQ), 즉 "온톨로지가 답할 수 있어야 하는 질문"을 설계와 검증의 바탕으로 둔다{WL}. 표 1은 이번 조사에서 확인한 방법론과 CQ를 쓰는 곳, 그 방법론을 쓴 연구이다.')
add(label('표 1. 주요 온톨로지 구축 방법론과 CQ'))
tbl([['방법론', '내용과 CQ를 쓰는 곳', '이 방법론을 쓴 연구'],
     ['Noy·McGuinness', '7단계(범위 정하기 → 기존 온톨로지 재사용 검토 → 용어 나열 → 클래스·계층 → 속성 → 제약 → 인스턴스). 1단계에서 CQ로 범위를 정하고, 완성한 온톨로지가 이 CQ에 답할 만큼 정보를 담았는지 확인하는 기준으로 쓴다{NOY}', '댐 분야 2편{HU,ZH}'],
     ['METHONTOLOGY', '요구사항 명세 단계와 검증 단계에 CQ를 넣는다{LIP}', '홍수·재난 분야 2편{LI}'],
     ['NeOn', 'CQ를 범위 설정과 검증 모두에 쓴다고 가정한다{KK}', '홍수·재난 분야 2편{LI}'],
     ['eXtreme Design', '반복적으로 개발하는 틀로, 요구사항 명세와 검증 단계에 CQ를 넣는다{LIP}', '이번 조사 범위에서는 없음']],
    [2000, 5772, 2200])
lis('Noy·McGuinness의 "확인하는 기준"은 원문의 litmus test(리트머스 시험)로, 온톨로지가 이 질문들에 답할 수 있으면 충분하고 답할 수 없으면 무엇이 빠졌는지를 가리는 기준이라는 뜻이다{NOY}.')

add(h2('1.2 CQ로 검증하는 방법'))
lis('CQ로 온톨로지를 검증하는 방법은 문헌에서 표 2의 네 가지로 나뉜다.')
add(label('표 2. CQ로 온톨로지를 검증하는 방법 비교'))
tbl([['방법', '하는 일', '장점', '약점', '문헌'],
     ['① 질의 실행 대조', 'CQ를 질의(SPARQL 등)로 바꿔 실행하고 기대한 답과 대조한다. CQ를 단위 시험처럼 쓰는 방식', '온톨로지가 실제로 답하는지 직접 확인하고, 모델링 실수를 효과적으로 찾는다', '질의를 손으로 쓰는 수작업이 많고, CQ의 용어가 모호하면 질의로 바꾸기 어렵다', '{LIP}'],
     ['② 개념 포괄도', '검증용 CQ에서 핵심 개념을 뽑아 온톨로지의 개념과 의미 유사도로 대응시킨다(떼어 둔 30% CQ 사용)', '데이터 없이 구조만으로 많은 CQ를 빠르게 확인한다', '유사도의 기준값이 모호하고, 정확성이나 쓸모를 직접 보여 주지는 못한다', '{LI}'],
     ['③ LLM 보조', 'LLM이 CQ마다 답할 수 있는지(예/아니오)와 질의를 제안하고 사람이 확인한다', '사람의 수작업과 체감 난이도를 줄인다', 'LLM 제안이 틀리면 사람의 판단 정확도도 떨어진다', '{LIP}'],
     ['④ 점검 항목', '"CQ를 정의했는가", "CQ에 답했는가"를 평가 항목으로 점수화한다', '간단하고 다른 평가 항목과 함께 쓸 수 있다', '"답했는가"를 판단하는 방법은 따로 필요하다', '{FOCA}']],
    [1500, 2900, 2300, 2272, 1000])
lis('CQ와 함께 많이 쓰는 검증은 추론기 검사이다. 추론기(HermiT, Pellet 등)는 온톨로지에 정한 규칙(클래스의 상하 관계, 서로 겹칠 수 없는 클래스 등)에 논리적 모순이 없는지 자동으로 검사하는 프로그램이다.',
    '홍수·재난 분야 온톨로지 12편의 검증 방법을 세면 표 3과 같다{LI}. 한 편이 여러 방법을 쓴 경우가 있어 합은 12보다 크다.')
add(label('표 3. 홍수·재난 분야 온톨로지 12편의 검증 방법'))
tbl([['검증 방법', '편수'],
     ['추론기 검사(추론 시험 포함)', '6'],
     ['CQ를 질의로 실행해 확인', '4'],
     ['사례 연구·응용', '3'],
     ['검증 없음', '2'],
     ['구조 지표(OntoQA), 설계 오류 점검 도구(OOPS!), 전문가 인터뷰', '각 1']],
    [7472, 2500])

add(h2('1.3 CQ 외의 검증 방법과 비교'))
lis('온톨로지 평가 접근은 크게 네 가지이며, 접근마다 잘 재는 품질 기준과 필요한 것이 다르다{RC}. CQ 검증은 요구사항(질문)에 답하는지 보는 기능 평가로{LIP}, 네 접근 중 과업 기반에 가장 가깝다.')
add(label('표 4. 온톨로지 평가 접근 비교와 우리 경우'))
tbl([['접근', '비교 대상', '잘 재는 기준', '필요한 것', '우리 경우'],
     ['기준 온톨로지 비교', '이미 인정된 온톨로지', '정확성, 완전성, 간결성', '같은 목적으로 만든 기준 온톨로지', '이번 조사에서 댐 운영 온톨로지는 찾지 못함'],
     ['분야 문서 비교', '분야를 다루는 문서 모음', '정확성, 완전성, 간결성', '분야 문서 모음', '규정 문서로 보완 검토 가능'],
     ['과업 기반(CQ 포함)', '과업에서의 성능', '적응성, 계산 효율', '과업과 평가 질문', '업무 질문과 CQ가 있음'],
     ['품질 기준', '구조 지표, 논리 규칙', '명료성, 일관성', '지표 계산, 추론기', '추론기 검사 바로 가능']],
    [1800, 1900, 1800, 2000, 2472])
lis('Raad·Cruz는 어떤 접근도 모든 기준을 평가하지 못하므로 둘 이상을 결합해야 하고, 가장 맞는 접근은 평가 목적에 따라 다르다고 정리한다{RC}.',
    '기준 온톨로지·분야 문서 비교는 비교할 자원이 있어야 하고 온톨로지의 요구사항을 직접 반영하지 못한다는 한계가 지적된다{LIP}. 우리 온톨로지는 질문(CQ)에 답하는 것을 목적으로 설계했으므로 과업 기반(CQ)을 중심에 두고, 일관성을 재는 품질 기준(추론기 검사)을 결합하는 것이 목적에 맞다. 분야 문서 비교는 규정 문서로 보완할 수 있는 방법으로 남겨 둔다.')

add(h2('1.4 CQ의 약점'))
lis('좋은 CQ가 무엇인지에 대한 기준과 지침이 부족해, CQ가 모호하게 쓰이거나 답할 수 없게 만들어지는 경우가 많다. 모호한 CQ는 불완전한 온톨로지로 이어진다{KK}.',
    '같은 요구사항에서도 CQ를 만드는 방법에 따라 결과가 크게 다르다. 온톨로지 엔지니어가 만든 CQ가 가장 적합했고, LLM이 만든 CQ는 사람의 것과 겹치는 부분이 거의 없었다{AL}.',
    '엔지니어는 CQ를 형식화할 줄 알지만 도메인 지식이 부족하고, 도메인 전문가는 그 반대라는 간극이 있다{WL}.',
    '→ 지금 우리 CQ는 연구자가 만든 것이라, 이 CQ로만 검증하면 연구자의 생각으로 연구자의 결과를 채점하는 셈이 된다. 표 2의 어느 방법을 쓰든 CQ 자체의 품질을 먼저 확보해야 한다.')

add(h2('1.5 우리 구조에 제안하는 방법'))
lis('표 2의 ①(질의 실행 대조)을 중심으로, 1.4의 약점은 전문가 검토로, 1.3의 결합은 추론기 검사로 채운다. 단계는 다음과 같다.')
add(label('1단계. 전문가 검토로 CQ 세트 확정'))
lis('질문 목록을 전문가 2명 이상에게 보여 질문마다 "실제 업무에 맞는가", "모호하지 않은가", "온톨로지가 답할 수 있어야 하는가"를 판단하고 고칠 점을 제안받는다.',
    '2명 이상이 동의한 질문만 남긴다. 홍수 온톨로지 연구는 평가자 3명 중 2명이 동의한 개념만 남겼고{LI}, IDEA2는 전문가 의견으로 CQ를 고쳐 합의에 이를 때까지 반복했다{WL}.')
add(label('2단계. 구성용과 검증용으로 나누기'))
lis('확정한 CQ를 구성용(온톨로지를 만들고 고치는 데 씀)과 검증용(시험에만 씀)으로 나눈다. 홍수 온톨로지 연구는 70%를 구성에, 30%를 평가에 썼다{LI}.',
    '검증용은 1단계에서 "온톨로지가 답할 수 있어야 한다"고 판단된 CQ에서 뽑는다. 범위 설정 CQ는 답할 수 없어도 되지만 검증 CQ는 반드시 답할 수 있어야 하기 때문이다{KK}.')
add(label('3단계. 검증용 CQ를 질의로 실행해 대조 (표 2의 ①)'))
lis('예: "%s" → CQ4(과거 방류 승인: 댐 ← concernsDam ← 승인)의 질의로 실행 → 원자료 승인 기록에서 미리 정한 기대 답(해당 기간의 승인 목록)과 대조 → 같으면 통과.' % EX_OK['question'],
    '우리 온톨로지는 CQ마다 질의 템플릿을 이미 만들어 두어, 표 2 ①의 약점인 질의 수작업이 적다.')
add(label('4단계. 통과하지 못한 CQ로 구조 개선'))
lis('예: "%s" → 지금 온톨로지의 운영기준에는 홍수기 제한수위만 있어 답할 구조가 없음 → 댐 제원(계획홍수위, 상시만수위)을 담을 구조를 추가 → 3단계를 다시 실행.' % EX_EXT['question'],
    '구성용 CQ로 구조를 고치고, 검증용 CQ로만 통과 여부를 판단한다. 시험에 쓰는 질문으로 구조를 맞추면 검증이 되지 않기 때문이다.')
add(label('5단계. 추론기로 일관성 확인'))
lis('구조를 고칠 때마다 추론기로 모순이 없는지 확인한다. 홍수·재난 온톨로지에서 가장 많이 쓴 검증이다(표 3).')
add(label('정한 것'))
tbl([['항목', '정한 것', '근거'],
     ['검토자', '댐 운영 실무자와 수자원 분야 연구자, 2명 이상', '홍수 온톨로지 연구는 평가자 3명이 다수결로 판단{LI}'],
     ['남길 기준', '2명 이상 동의', '3명 중 2명 동의{LI}'],
     ['나누는 비율', '구성용 70%, 검증용 30%', '{LI}'],
     ['검증 방법', '질의 실행 대조(①) + 추론기 일관성 검사', '표 2, 표 3, 둘 이상 결합{RC}'],
     ['LLM 보조(③)', '쓰지 않음', 'LLM 제안이 틀리면 사람 판단도 흐려짐{LIP}']],
    [1800, 3700, 4472])
lis('남은 것: 실제 검토자 섭외.')

# ================================================================== 2. 향후 계획
add(h1('2. 향후 계획'))
add(h2('2.1 업무 질문 82개로 검증된 CQ를 만들어 적용'))
lis('댐 운영 업무 82개에서 업무마다 질문을 하나씩 만들어 두었다(질문 %d개).' % len(Q82),
    '이 82개를 1.5의 1단계대로 전문가에게 검토받으면, 실제 업무를 반영하고 CQ의 약점(모호함, 연구자 관점)을 보완한 검증된 CQ 세트가 된다.',
    '이 CQ 세트로 1.5의 2~5단계를 적용한다: 구성용과 검증용으로 나누고, 구성용으로 온톨로지 구조를 고치고, 검증용을 질의로 실행해 통과 여부를 확인하고, 추론기로 일관성을 확인한다.')
add(h2('2.2 KG 자체의 검증'))
lis('온톨로지 구조를 정한 뒤, 그 구조에 채운 값이 맞고 빠짐없고 모순이 없는지 검증하는 방법을 조사해 적용한다. KG 품질 연구는 이를 정확성, 완전성, 일관성 같은 차원과 지표로 다룬다{ZA,PA}.')

# ================================================================== 참고문헌
add(h1('참고문헌'))
assert set(ORDER) == set(REFS), set(REFS) ^ set(ORDER)
for i, k in enumerate(ORDER, 1):
    add(L.para('[%d] %s' % (i, REFS[k]), 17))

T.save(OUT, ''.join(B), L.IMGS, page_numbers=True)
print('saved', OUT, 'refs', len(ORDER))
