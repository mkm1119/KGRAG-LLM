#!/usr/bin/env python3
"""랩미팅 자료(docx): 온톨로지 검증 방법 — 선행연구 분석과 우리 구조에 맞는 방안, 향후 계획.
서식은 11/06 자료(build_labmeeting_how_kg2.py)와 같다(labdoc_lib, 같은 템플릿).
근거 문헌: references/evidence_literature/ (해석: lab_meeting/paper_review/검증부분_해석*.md)
11/12 메모 4차 반영: 1장 왜 CQ인가(DDKG→OntoDSMS→Noy→Gruber), 2장 CQ 검증 방법(조사한 연구, 방법별 진행, 비교와 선택, CQ의 품질),
3장 적용, 4장 향후. 긴 문단 대신 흐름 그림, 방법별 정리 상자, 짧은 항목으로 정리.
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
    return re.sub(r'\{([A-Z0-9,]+)\}', rep, t)


B = []
add = B.append


def lis(*items):
    for t in items:
        add(li(cite(t)))


def tbl(rows, widths):
    add(table([[cite(c) for c in r] for r in rows], widths, header=True, firstcol=False))



def P(t):
    add(para(cite(t)))


def KEY(head, t):
    add(L.lead(head, cite(t)))


def CODE(t):
    add(L.code(t))


def FLOW(*items):
    add(L.flow(list(items)))


def CARD(rows, w1=1700):
    """왼쪽에 항목 이름, 오른쪽에 내용(줄바꿈 가능)을 두는 정리 상자."""
    add(table([[a, cite(b)] for a, b in rows], [w1, 9972 - w1], header=False, firstcol=True))


del REFS['RC']
REFS['WI'] = 'Wilson, R. S. I., Goonetillake, J. S., Walisadeera, A. I., & Ginige, A. (2023). A conceptual model for ontology quality assessment: A systematic review. Semantic Web, 14(6), 1051–1097.'
REFS['KL'] = 'Keet, C. M., & Ławrynowicz, A. (2016). Test-driven development of ontologies. ESWC 2016, LNCS 9678. (extended version: arXiv:1512.06211)'

# ================================================================== 표지·요약
add(title('온톨로지 검증 방법', '선행연구 분석과 우리 구조에 맞는 방안'))
add(dateline('2026.11 · 문경민'))
add(h1('요약'))
lis('조사 방법: 최신 논문에서 출발해, 그 논문이 인용한 과거 논문까지 따라가며 조사해 보았다.',
    '왜 CQ인가: 최신 댐 온톨로지 연구들은 Noy·McGuinness 방법으로 온톨로지를 만들었다. 선행 댐 연구는 이 방법을 "비교적 성숙하고, Gruber의 온톨로지 설계 기준 다섯 가지를 엄격히 따르는 유일한 방법"이라는 이유로 골랐다. 이 방법에서 온톨로지를 확인하는 기준이 역량 질문(CQ)이다.',
    'CQ 검증 방법: CQ로 검증하는 연구를 찾아 비교하니 방법은 질의 실행 대조, 개념 포괄도, LLM 보조 세 가지였다. 이 중 맞는 답이 나오는지를 직접 확인하는 질의 실행 대조를 골랐다. 다만 어느 방법이든 CQ 자체의 품질이 결과를 좌우한다.',
    '우리 연구 적용: 전문가 검토로 CQ 세트를 확정 → 구성용과 검증용으로 나누기 → 검증용 CQ를 질의로 실행해 판정 → 통과하지 못한 CQ로 구조 개선.',
    '향후: 업무 질문 82개를 전문가 검토로 검증된 CQ로 만들어 적용하고, 그다음 KG 자체의 검증 방법을 조사해 적용한다.')

# ================================================================== 1. 왜 CQ인가
add(h1('1. 왜 CQ인가', pagebreak=True))
add(h2('1.1 조사 경로'))
P('우리 연구와 가장 가까운 최신 논문인 댐 결함 온톨로지(DDKG, 2026)에서 출발해, 인용된 문헌을 차례로 따라갔다.')
FLOW('DDKG (2026)\n댐 결함 온톨로지', 'OntoDSMS (2023)\n댐 안전 모니터링 온톨로지', 'Noy·McGuinness (2001)\n온톨로지 구축 방법', 'Gruber (1995)\n온톨로지 설계 기준')
lis('DDKG는 7단계로 온톨로지를 만들었고, 선행연구로 OntoDSMS를 인용한다{HU}.',
    'OntoDSMS는 구축 방법으로 Noy·McGuinness 방법을 골랐고, 그 이유로 Gruber의 설계 기준을 든다{ZH}.',
    'DDKG의 7단계는 Noy·McGuinness의 7단계와 같은 순서다{HU,NOY}.')

add(h2('1.2 댐 분야 연구가 Noy·McGuinness 방법을 고른 이유'))
CARD([('비교한 방법', 'TOVE, IDEF5, Skeleton, KACTUS, SENSUS, METHONTOLOGY, Noy·McGuinness (일곱 가지){ZH}'),
      ('고른 방법', 'Noy·McGuinness{ZH}'),
      ('이유', '① 비교적 성숙한 방법이다.\n② Gruber의 온톨로지 구축 기본 원칙 다섯 가지를 엄격히 따르는 현재 유일한 방법이다{ZH}.')])
add(label('표 1. Gruber(1995)의 온톨로지 설계 기준 (FOCA의 정리를 옮김)'))
tbl([['기준', '뜻{FOCA}'],
     ['명료성', '정의한 용어의 의도된 뜻을 효과적으로 전달해야 한다. 정의는 객관적이고 맥락에 독립적이어야 한다.'],
     ['일관성', '정의와 일관된 추론만 허용해야 한다. 정의하는 공리에 논리적 모순이 없어야 한다.'],
     ['확장성', '예상되는 여러 과업의 바탕이 되고, 기존 정의를 고치지 않고 확장할 수 있어야 한다.'],
     ['최소 인코딩 편향', '특정 표기나 구현의 편의 때문에 표현을 고르지 않아야 한다.'],
     ['최소 존재론적 약속', '필요한 만큼만 세계에 대해 주장해, 쓰는 쪽이 구체화할 여지를 남겨야 한다.']],
    [2200, 7772])

add(h2('1.3 Noy·McGuinness 방법에서 CQ의 역할'))
P('Noy·McGuinness 방법은 온톨로지를 7단계로 만든다{NOY}.')
FLOW('① 범위\n정하기', '② 재사용\n검토', '③ 용어\n나열', '④ 클래스\n·계층', '⑤ 속성\n정의', '⑥ 제약\n정의', '⑦ 인스턴스\n생성')
P('역량 질문(CQ)은 "이 온톨로지 위의 지식베이스가 답할 수 있어야 하는 질문"이다(예: 와인 온톨로지의 "구운 고기에는 어떤 와인이 가장 좋은가?"). 이 방법에서 CQ는 세 곳에 쓰인다{NOY}.')
CARD([('① 범위 정하기', 'CQ를 대략 적어 보며 온톨로지에 무엇이 들어가야 하는지 정한다.'),
      ('⑤ 속성 정의', '클래스만으로는 CQ에 답할 정보가 부족하므로, CQ에 답하는 데 필요한 속성을 정의한다.'),
      ('완성한 뒤 확인', 'CQ가 "리트머스 시험"으로 쓰인다. 온톨로지가 이 질문들에 답할 만큼 정보를 담고 있는지를 가리는 기준이라는 뜻이다.')], 2000)
lis('Noy·McGuinness는 초기 온톨로지를 그 분야 전문가와 논의해 평가하고 고치라고도 한다{NOY}.',
    '다만 CQ로 확인하는 구체적인 방법은 정하지 않았다. 그 방법은 2장에서 조사했다.')
KEY('정리', '댐 분야 연구는 설계 기준을 가장 잘 따르는 방법으로 Noy·McGuinness 방법을 골랐고, 우리 온톨로지도 이 방법으로 설계했다. 이 방법에서 온톨로지를 만드는 기준이자 확인하는 기준이 CQ이므로, 우리 온톨로지의 검증도 CQ로 한다.')

# ================================================================== 2. CQ 검증 방법
add(h1('2. CQ 검증 방법'))
add(h2('2.1 조사한 연구'))
P('CQ로 온톨로지를 검증하는 최신 연구(Lippolis 외, 2025)에서 출발해 인용된 연구를 따라갔고, 수자원 분야에서는 홍수 온톨로지 연구(Li 외, 2025)를 함께 보았다.')
add(label('표 2. CQ 검증 방법을 다룬 연구'))
tbl([['연구', '찾은 경로', '다룬 방법'],
     ['Lippolis 외 (2025){LIP}', '출발 논문', '질의 실행 대조의 절차, LLM 보조'],
     ['Blomqvist 외 (2012)', 'Lippolis 외가 인용{LIP}', 'CQ를 질의로 바꿔 시험하는 방법론'],
     ['Vrandečić·Gangemi (2006)', 'Lippolis 외가 인용{LIP}', 'CQ를 단위 시험처럼 쓰자는 제안'],
     ['Keet·Ławrynowicz (2016){KL}', 'Keet·Khan (2024)이 인용{KK}', '시험 주도 개발: 시험과 수정을 묶는 순서'],
     ['Li 외 (2025){LI}', '수자원 분야 연구', '개념 포괄도']],
    [3200, 3000, 3772])
KEY('정리', '찾은 방법은 세 가지다: ① 질의 실행 대조, ② 개념 포괄도, ③ LLM 보조.')

add(h2('2.2 방법별 진행 방식'))
add(label('① 질의 실행 대조'))
CARD([('확인하는 것', 'CQ에 실제로 맞는 답이 나오는가'),
      ('진행 순서', '1. CQ를 답하는 데 필요한 클래스와 관계로 풀어 쓴다. 예: "누가 오르간을 만들었거나 고쳤나?" → 클래스 둘(사람, 오르간), 관계 하나(만들었다/고쳤다)\n2. 그 클래스와 관계가 온톨로지에 있는지 판정한다: 예 / 아니오 / 아니오(경미, 속성 하나만 빠짐)\n3. CQ를 질의로 써서 실행하고, 결과를 미리 정한 기대 답과 대조한다. 같으면 통과{LIP}'),
      ('고칠 때의 순서\n(시험 주도 개발)', '시험이 실패하는 것을 확인 → 필요한 클래스·관계를 추가 → 같은 시험이 통과하는지 확인 → 모든 시험을 다시 실행해 기존 결과가 유지되는지 확인{KL}'),
      ('논문의 결과', 'CQ를 질의로 다시 쓰면 모델링 실수를 효과적으로 찾아낸다(Blomqvist 외). 10년 넘게 여러 프로젝트에서 쓰였다{LIP}.'),
      ('한계', '질의를 손으로 써야 해 시간과 자원이 든다. CQ가 모호하면 질의로 바꾸기 어렵다{LIP}.')], 2000)
P('우리 온톨로지로 예를 들면, CQ4(과거 방류 승인)의 질문 "%s"는 다음 질의가 된다(우리 KG는 Neo4j에 있어 질의 언어는 Cypher).' % EX_OK['question'])
CODE("MATCH (a:Approval)-[:concernsDam]->(d:Dam {damName: '소양강댐'})\nWHERE a.approvalTime STARTS WITH '2017-08'\nRETURN a.approvalTime, a.approvalContent")
lis('기대 답(원자료 승인 기록에서 미리 정함): 원자료 기준 2건. 8월 24일 승인(최대 1,500㎥/s 방류)과 8월 27일 승인(같은 방류의 기간 연장).',
    '판정: 결과가 이 2건과 같으면 통과. 하나가 빠지거나 다른 댐 건이 섞이면 실패.')

add(label('② 개념 포괄도'))
CARD([('확인하는 것', 'CQ에 나오는 개념이 온톨로지에 있는가 (질의는 실행하지 않음)'),
      ('진행 순서', '1. CQ를 나눈다: 70%는 온톨로지를 만드는 데, 30%는 평가에만 쓴다.\n2. 평가용 CQ 12개에서 LLM이 핵심 개념을 3~7개씩 뽑는다(56개).\n3. 평가자 3명이 개념을 검토해 2명 이상 승인한 것만 남긴다(66개로 확정).\n4. 개념과 온톨로지 클래스 이름을 임베딩해, 유사도가 기준값 이상인 클래스가 있으면 포괄된 것으로 본다{LI}.'),
      ('논문의 결과', '중복 클래스와 빠진 개념을 찾아냈다{LI}.'),
      ('한계', '기준값을 정할 수 없다: 같은 온톨로지인데 기준값 0.3이면 개념의 100%, 0.9이면 7.6%가 대응된다.\n개념이 "있는지"만 볼 뿐 정확성이나 쓸모는 보여 주지 못한다(저자들이 밝힘){LI}.')], 2000)

add(label('③ LLM 보조'))
CARD([('확인하는 것', '①의 판정을 LLM이 대신 제안하고 사람이 최종 판단'),
      ('진행 순서', '1. LLM에 과업 설명, 판정 예시, 사용자 스토리, CQ, 온톨로지를 준다.\n2. LLM이 예/아니오 판정과 확인용 질의를 내놓는다.\n3. 사람이 온톨로지 편집기에서 이 제안을 보고 최종 판정한다{LIP}.'),
      ('논문의 결과', '지식 엔지니어 19명 실험. LLM 제안이 맞으면 사람의 정확도 70.5% → 83.2%, 틀리면 71.9% → 43.9%. 전체 정확도는 의미 있게 달라지지 않았다{LIP}.'),
      ('한계', '틀린 제안을 사람이 그대로 따라간다{LIP}.')], 2000)

add(h2('2.3 비교와 선택'))
add(label('표 3. CQ 검증 방법 비교'))
tbl([['방법', '확인하는 것', '장점', '한계'],
     ['① 질의 실행 대조', '맞는 답이 나오는가', '직접 확인, 실수를 잘 찾음', '질의 수작업, 모호한 CQ'],
     ['② 개념 포괄도', '개념이 있는가', '구조만으로 빠름', '기준값에 따라 100%~7.6%, 정확성은 못 봄'],
     ['③ LLM 보조', '①을 LLM이 제안', '수작업 감소', '틀린 제안이면 정확도 하락']],
    [2200, 2400, 2500, 2872])
KEY('선택', '① 질의 실행 대조.')
lis('우리가 확인하려는 것은 "운영자의 질문에 맞게 답하는가"이다. 온톨로지 품질 리뷰는 정확성을 "맞게 답한 CQ의 수"로, 완전성을 "충분한 답을 낸 CQ의 수"로 잰다고 정리한다{WI}. 이를 직접 셀 수 있는 것은 실제로 답을 내 보는 ①이다.',
    '②는 정확성을 보여 주지 못하고{LI}, ③은 틀린 제안이 사람의 판단을 흐린다{LIP}.',
    '①의 한계인 질의 수작업은, 우리 온톨로지가 CQ마다 질의 템플릿을 이미 갖고 있어 부담이 작다.')

add(h2('2.4 선택한 방법의 전제: CQ의 품질'))
P('어느 방법이든 시험지(CQ)가 나쁘면 결과도 의미가 없다. 문헌이 지적하는 CQ의 약점은 세 가지다.')
CARD([('기준이 없다', '좋은 CQ가 무엇인지에 대한 안내가 부족해 CQ가 모호하게 쓰이거나 질의로 바꿀 수 없게 만들어진다. 모호한 CQ는 불완전한 온톨로지로 이어진다{KK}.'),
      ('만드는 사람에 따라 다르다', '같은 요구사항에서 만든 CQ가 겹치는 정도: 엔지니어 두 명 사이 15.3%, 두 LLM 사이 2.9%, LLM과 사람 사이 거의 0%. 좋은 CQ에는 사람의 전문성이 중심이다{AL}.'),
      ('지식의 간극', '엔지니어는 CQ를 형식화할 줄 알지만 분야 지식이 부족하고, 도메인 전문가는 그 반대다. 전문가가 CQ를 검토하고 고치는 과정을 합의까지 반복하면 CQ의 수용도가 높아진다{WL}.')], 2400)
KEY('정리', '지금 우리 CQ는 연구자가 만들었고, 같은 CQ로 온톨로지를 만들고 확인해 왔다. 연구자의 생각으로 연구자의 결과를 채점하는 셈이므로, 분야를 아는 사람이 CQ를 검토하는 과정과 만드는 CQ와 시험하는 CQ를 나누는 과정이 필요하다.')

# ================================================================== 3. 적용
add(h1('3. 우리 연구에 적용'))
P('새 방법을 더하는 것이 아니라, 처음 설계에서 따른 Noy·McGuinness 방법의 확인 절차(CQ 리트머스 시험, 전문가와 논의)를 2장의 문헌으로 구체화한다.')
FLOW('1단계\n전문가 검토로\nCQ 세트 확정', '2단계\n구성용·검증용으로\n나누기', '3단계\n검증용 CQ를\n질의로 실행해 판정', '4단계\n통과 못 한 CQ로\n구조 개선')

add(label('1단계. 전문가 검토로 CQ 세트 확정'))
CARD([('하는 일', '질문 목록을 전문가 2명 이상에게 보내 질문마다 세 가지를 판단받는다.\n(가) 실제 업무에서 묻는 질문인가\n(나) 뜻이 하나로 읽히는가\n(다) 우리 온톨로지가 반드시 답할 수 있어야 하는가\n2명 이상 동의한 질문만 남기고, 갈린 질문은 고쳐서 다시 검토받는다.'),
      ('예', '"충주댐 계획홍수위까지 얼마나 여유 있어?" → 지금 수위 기준인지 어느 시점 기준인지 드러나지 않아 (나)에서 고칠 대상이 될 수 있다.'),
      ('근거', '평가자 3명 중 2명 이상 승인한 것만 남김{LI}, 합의까지 검토 반복{WL}')], 1400)
add(label('2단계. 구성용과 검증용으로 나누기'))
CARD([('하는 일', '확정한 CQ를 구성용 70%(온톨로지를 만들고 고치는 데 씀)와 검증용 30%(시험에만 씀)로 나눈다.\n검증용은 1단계 (다)에서 "반드시 답해야 한다"고 판단된 CQ에서만 뽑는다.\n한 유형이 한쪽에 몰리지 않게 유형마다 나눠 담는다(우리 설정).'),
      ('근거', '70:30으로 나눠 30%는 평가에만 씀{LI}. 범위를 정하는 CQ는 답할 수 없어도 되지만 검증하는 CQ는 반드시 답할 수 있어야 함{KK}')], 1400)
add(label('3단계. 검증용 CQ를 질의로 실행해 판정'))
CARD([('하는 일', '검증용 CQ마다 2.2 ①의 순서로 "예 / 아니오 / 아니오(경미)"를 판정하고, "예"인 CQ는 질의를 실행해 기대 답과 대조한다.\n결과는 맞게 답한 CQ의 수(정확성)와 충분한 답을 낸 CQ의 수(완전성)로 센다.'),
      ('예', '2.2의 소양강댐 승인 질의: 기대 답 2건과 같으면 통과'),
      ('근거', '판정 방식{LIP}, 정확성·완전성 지표{WI}')], 1400)
add(label('4단계. 통과하지 못한 CQ로 구조 개선'))
CARD([('하는 일', '실패를 확인 → 구성용 CQ를 근거로 구조를 수정 → 같은 시험이 통과하는지 확인 → 모든 검증용 CQ를 다시 실행해 기존 결과가 유지되는지 확인.\n구조를 고치는 근거는 구성용 CQ에서만 가져온다. 검증용 CQ에 맞춰 고치면 시험 문제를 보고 답안을 맞추는 것이 되기 때문이다.'),
      ('예', '"%s" → 판정: 아니오. 운영기준에는 홍수기 제한수위만, 댐 클래스에는 이름과 형식만 있어 담을 곳이 없다 → 댐 제원 속성을 추가 → 다시 시험.' % EX_EXT['question']),
      ('근거', '시험 주도 개발의 순서{KL}, 평가용 CQ는 평가에만 씀{LI}')], 1400)

add(label('정한 것과 아직 정할 것'))
tbl([['항목', '정한 것', '근거'],
     ['검토자', '댐 운영 실무자와 수자원 분야 연구자, 2명 이상', '전문가와 논의{NOY}, CQ 약점 보완{AL,WL}'],
     ['남길 기준', '2명 이상 동의, 갈리면 고쳐서 재검토', '{LI,WL}'],
     ['나누는 비율', '구성용 70%, 검증용 30%', '{LI}'],
     ['검증 방법', '질의 실행 대조, 정확성·완전성으로 셈', '{LIP,WI,KL}'],
     ['LLM 보조', '쓰지 않음', '틀린 제안이면 정확도 하락{LIP}'],
     ['아직 정할 것', '검토자 섭외', '']],
    [1700, 4600, 3672])
lis('"2명 이상 동의"와 "70:30"은 홍수 온톨로지 연구 한 편에서 가져왔고, 그 연구의 다수결 대상은 CQ가 아니라 CQ에서 뽑은 개념이었다. 검증된 최적값이 아니라 선행연구를 따른 우리 설정이다.',
    '추론기 검사는 넣지 않았다. 홍수·재난 분야에서 CQ로 검증한 4편이 함께 쓴 방법이지만{LI}, OWL 같은 논리 언어로 적은 규칙이 있어야 하고 우리 온톨로지는 Neo4j 그래프 구조로 구현했다. 온톨로지를 OWL로 옮길지 정할 때 함께 검토한다.')

# ================================================================== 4. 향후 계획
add(h1('4. 향후 계획'))
add(label('4.1 업무 질문 82개로 검증된 CQ를 만들어 적용'))
lis('댐 운영 업무 82개에서 업무마다 실제로 물을 법한 질문을 하나씩 만들어 두었다(질문 %d개). 업무 목록에서 출발해 실제 업무에 가깝지만, 아직 연구자가 쓴 문장이다.' % len(Q82),
    '이 82개를 3장 1단계대로 전문가에게 검토받으면, 실제 업무를 반영하고 CQ의 약점을 보완한 검증된 CQ 세트가 된다.',
    '이 CQ 세트로 2~4단계를 적용해 온톨로지 구조를 개선하고 검증한다.')
add(label('4.2 KG 자체의 검증'))
lis('온톨로지 검증은 "구조가 질문에 답할 수 있는가"를 보는 것이고, 그 구조에 채운 값(KG)이 맞는지는 별도의 문제다.',
    '온톨로지 구조를 정한 뒤, KG에 채운 값이 맞고 빠짐없고 모순이 없는지 검증하는 방법을 같은 방식(최신 논문에서 인용을 따라가기)으로 조사해 적용한다. KG 품질 연구는 이를 정확성, 완전성, 일관성 같은 차원과 지표로 다룬다{ZA,PA}.')

# ================================================================== 참고문헌
add(h1('참고문헌'))
assert set(ORDER) == set(REFS), set(REFS) ^ set(ORDER)
for i, k in enumerate(ORDER, 1):
    add(L.para('[%d] %s' % (i, REFS[k]), 17))

T.save(OUT, ''.join(B), L.IMGS, page_numbers=True)
print('saved', OUT, 'refs', len(ORDER))
