#!/usr/bin/env python3
"""랩미팅 자료(docx): 온톨로지 검증 방법 — 선행연구 분석과 우리 구조에 맞는 방안, 향후 계획.
서식은 11/06 자료(build_labmeeting_how_kg2.py)와 같다(labdoc_lib, 같은 템플릿).
근거 문헌: references/evidence_literature/ (해석: lab_meeting/paper_review/검증부분_해석*.md)
11/12 메모 5차 반영: 요약을 지난주/이번 주/다음 주로, 1장을 검증 방법 여섯 가지 비교 후 CQ 선택으로(읽는 순서대로 설명),
2장 CQ 검증 방법 비교와 선택, 3장 적용, 4장 향후, 부록 A Gruber 기준.
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
CARD([('지난주', 'KG 구축 방법(Relation 잇기, 저장, 검색·답변)을 정리했다.\n받은 의견: 검증을 어떻게 할지 더 고민해 마무리할 것, 필요하면 외부 전문가의 도움을 받는 방법을 찾을 것.'),
      ('이번 주', '온톨로지를 어떻게 검증할지 선행연구를 조사해 정했다(KG 자체의 검증은 다음 순서로 둠).\n① 온톨로지 검증 방법 여섯 가지를 비교해, 역량 질문(CQ)으로 검증하기로 했다(1장).\n② CQ로 검증하는 방법 세 가지를 비교해, CQ를 질의로 실행해 기대 답과 대조하는 방법을 골랐다(2장).\n③ CQ의 약점을 보완하도록, 전문가 검토로 CQ를 확정하고 구성용과 검증용으로 나누는 적용 방안을 만들었다(3장).'),
      ('다음 주', '업무 질문 82개를 전문가 검토용으로 준비하고, 검토자를 정한다.\nKG 자체의 검증 방법을 같은 방식으로 조사한다(4장).')], 1300)

# ================================================================== 1. 왜 CQ인가
add(h1('1. 왜 CQ인가', pagebreak=True))
add(h2('1.1 배경: 우리 온톨로지와 CQ'))
P('우리 온톨로지는 Noy·McGuinness 방법으로 설계했다. 이 방법은 온톨로지를 아래 7단계로 만든다{NOY}.')
FLOW('① 범위\n정하기', '② 재사용\n검토', '③ 용어\n나열', '④ 클래스\n·계층', '⑤ 속성\n정의', '⑥ 제약\n정의', '⑦ 인스턴스\n생성')
lis('역량 질문(CQ)은 "이 온톨로지 위의 지식베이스가 답할 수 있어야 하는 질문"이다. 예: 와인 온톨로지의 "구운 고기에는 어떤 와인이 가장 좋은가?"',
    '이 방법에서 CQ는 ①단계에서 범위를 정하는 데, ⑤단계에서 CQ에 답하는 데 필요한 속성을 정의하는 데 쓰인다. 완성한 뒤에는 온톨로지가 이 질문들에 답할 만큼 정보를 담고 있는지 가리는 "리트머스 시험"으로 쓰인다{NOY}.',
    '댐 분야의 최신 온톨로지 연구 두 편도 이 방법을 따랐다. 댐 안전 모니터링 온톨로지(OntoDSMS, 2023)는 구축 방법 일곱 가지(TOVE, IDEF5, Skeleton, KACTUS, SENSUS, METHONTOLOGY, Noy·McGuinness) 중 이 방법을 골랐는데, 비교적 성숙하고 Gruber의 온톨로지 설계 기준 다섯 가지(명료성, 일관성, 확장성, 최소 인코딩 편향, 최소 존재론적 약속, 부록 A)를 엄격히 따르는 유일한 방법이라는 이유였다{ZH}. 댐 결함 온톨로지(DDKG, 2026)도 같은 7단계를 같은 순서로 밟았다{HU}.')
P('그런데 Noy·McGuinness는 완성한 온톨로지를 확인하는 방법으로 CQ만 든 것이 아니다. 응용에 써 보거나 그 분야 전문가와 논의해 평가하라고도 하고, 어느 것이든 구체적인 절차는 정하지 않았다{NOY}. 그래서 "CQ로 검증한다"고 정하기 전에, 실제 연구들이 온톨로지를 어떤 방법으로 검증했는지 조사해 비교했다.')

add(h2('1.2 조사한 연구와 찾은 검증 방법'))
lis('수자원·재난 분야: 홍수·재난 온톨로지 12편의 검증 방법을 정리한 Li 외(2025)의 표와, 이 연구 자체의 검증{LI}',
    '댐 분야: OntoDSMS(2023){ZH}, DDKG(2026){HU}',
    '일반: 2010~2021년 온톨로지 품질 평가 연구를 체계적으로 리뷰한 Wilson 외(2023){WI}, 최신 CQ 검증 연구인 Lippolis 외(2025){LIP}')
add(label('표 1. 연구들이 실제로 쓴 검증 방법'))
tbl([['검증 방법', '홍수·재난 12편{LI}', '댐 2편'],
     ['CQ 검증', '4편', '없음'],
     ['추론기 검사', '6편', '없음'],
     ['구조 지표·설계 오류 점검', '2편', '없음'],
     ['사례 적용', '3편', 'OntoDSMS{ZH}'],
     ['전문가 검토', '1편', 'DDKG{HU}'],
     ['기준 온톨로지·분야 문서 비교', '1편(분야 자료 비교)', '없음'],
     ['검증 없음', '2편', '']],
    [4000, 3000, 2972])
lis('한 편이 여러 방법을 함께 쓴 경우가 있어 합은 편수보다 크다. CQ로 검증한 4편은 모두 추론기 검사를 함께 썼다{LI}.')

add(h2('1.3 방법별로 무엇을 어떻게 확인하나'))
P('Wilson 외(2023)는 온톨로지 평가를 두 관점으로 나눈다. 구조와 내용을 들여다보고 "온톨로지를 바르게 만들었는가"를 확인하는 것(내재적 평가)과, 온톨로지를 시스템의 한 부품으로 보고 "맞는 온톨로지를 만들었는가", 즉 쓰는 목적에 맞는지를 확인하는 것(외재적 평가)이다. 뒤의 것은 주로 사용자와 도메인 전문가가 참여해 한다{WI}. 표 2는 방법마다 확인하는 것과 실제 연구의 방식을 정리한 것이다.')
add(label('표 2. 온톨로지 검증 방법 비교'))
tbl([['방법', '확인하는 것', '실제 연구의 방식', '한계'],
     ['CQ 검증', '필요한 질문에 맞게 답하는가\n(맞는 온톨로지인가)', 'CQ를 질의로 바꿔 실행해 답을 확인한다. 맞게 답한 CQ의 수로 정확성을, 충분한 답을 낸 CQ의 수로 완전성을 잰다{WI}. 잘 확립된 방법으로 평가된다{LIP}.', 'CQ의 품질에 좌우되고 수작업이 든다{LIP}.'],
     ['추론기 검사', '정의에 논리적 모순이 없는가\n(바르게 만들었는가)', 'OWL로 적은 온톨로지를 추론기(HermiT, Pellet)로 분류해 모순이 생기는지 본다{KL,LI}.', '모순이 없는지만 본다. 논리 언어(OWL)로 적은 규칙이 있어야 한다.'],
     ['구조 지표·설계 오류 점검', '구조가 풍부하고 흔한 설계 실수가 없는가\n(바르게 만들었는가)', '홍수 온톨로지 연구는 관계 풍부도와 상속 풍부도(OntoQA)를 계산해 기존 온톨로지 세 개와 비교했다{LI}.', '저자들 스스로 구조 평가만으로는 부족하고 과업 중심의 정량 평가가 다음 단계라고 했다{LI}.'],
     ['사례 적용', '실제 사례에서 쓸 수 있는가\n(맞는 온톨로지인가)', 'OntoDSMS는 콘크리트댐 사례에서 온톨로지 질의 결과를 같은 내용의 데이터베이스 질의 결과와 비교했다{ZH}. 홍수 온톨로지 연구는 홍수 경보문을 온톨로지로 다시 써서 전후를 비교했다{LI}.', '고른 사례에 대한 정성적 확인이다{LI}.'],
     ['전문가 검토', '분야 지식에 비추어 맞는가\n(맞는 온톨로지인가)', '태국 홍수 대피 온톨로지는 전문가 인터뷰로{LI}, DDKG는 전문가가 분류 결과를 검증하고 온톨로지를 확장하는 방식으로 했다{HU}.', '평가가 주관적이다{WI}.'],
     ['기준 온톨로지·분야 문서 비교', '인정된 기준과 얼마나 일치하는가', '이미 인정된 온톨로지나 분야 문서와 비교한다{WI}.', '비교할 기준이 없거나 불완전한 경우가 많고, 온톨로지의 요구사항을 반영하지 못한다{LIP}.']],
    [1700, 2200, 3672, 2400])

add(h2('1.4 비교와 선택'))
KEY('선택', 'CQ 검증을 중심으로 하고, 전문가 검토를 CQ를 확정하는 데 함께 쓴다.')
lis('확인하려는 것과 맞는다: 우리 온톨로지의 목적은 댐 운영자의 질문에 맞게 답하는 것이다. 이는 "맞는 온톨로지를 만들었는가"의 문제이고, 이 관점의 정확성과 완전성을 재는 지표가 CQ에 답한 결과다{WI}.',
    '요구사항이 이미 CQ로 있다: 우리 온톨로지는 처음부터 CQ를 정하고 설계했다(1.1). 완성한 온톨로지가 그 CQ에 답하는지 보는 것은 설계한 목적을 이뤘는지 보는 직접적인 확인이다.',
    '다른 방법은 우리 목적을 직접 확인하지 못하거나 지금 쓸 수 없다: 추론기 검사와 구조 지표는 "바르게 만들었는가"를 보는 것이고, 추론기는 OWL로 적은 규칙이 필요한데 우리 온톨로지는 Neo4j 그래프 구조로 구현했다. 사례 적용은 고른 사례만 확인한다. 비교할 댐 운영 온톨로지는 찾지 못했다.',
    '전문가 검토는 주관적이라는 한계가 있지만, CQ가 실제 업무에 맞는지를 판단하는 데 필요하다. 그래서 따로 쓰지 않고 CQ를 확정하는 단계에 넣는다(3장).')
lis('참고: 같은 방법으로 만든 댐 분야 두 연구는 CQ 검증을 보고하지 않았다(표 1). 댐 분야에서 CQ 검증을 어떻게 할지는 아직 다뤄지지 않은 부분이다.')

# ================================================================== 2. CQ 검증 방법
add(h1('2. CQ 검증 방법'))
add(h2('2.1 조사한 연구'))
P('CQ로 온톨로지를 검증하는 최신 연구(Lippolis 외, 2025)에서 출발해 인용된 연구를 따라갔고, 수자원 분야에서는 홍수 온톨로지 연구(Li 외, 2025)를 함께 보았다.')
add(label('표 3. CQ 검증 방법을 다룬 연구'))
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
add(label('② 개념 포괄도'))
CARD([('확인하는 것', 'CQ에 나오는 개념이 온톨로지에 있는가 (질의는 실행하지 않음)'),
      ('진행 순서', '1. CQ를 나눈다: 70%는 온톨로지를 만드는 데, 30%는 평가에만 쓴다.\n2. 평가용 CQ에서 LLM이 질문마다 핵심 개념을 3~7개씩 뽑는다.\n3. 평가자 3명이 뽑힌 개념을 검토해, 2명 이상 승인한 것만 남기고 빠진 개념을 더한다.\n4. 개념과 온톨로지 클래스 이름을 임베딩해, 유사도가 기준값 이상인 클래스가 있으면 포괄된 것으로 본다{LI}.'),
      ('논문의 결과', '중복 클래스와 빠진 개념을 찾아냈다{LI}.'),
      ('한계', '기준값을 정할 수 없다: 같은 온톨로지인데 기준값 0.3이면 개념의 100%, 0.9이면 7.6%가 대응된다.\n개념이 "있는지"만 볼 뿐 정확성이나 쓸모는 보여 주지 못한다(저자들이 밝힘){LI}.')], 2000)

add(label('③ LLM 보조'))
CARD([('확인하는 것', '①의 판정을 LLM이 대신 제안하고 사람이 최종 판단'),
      ('진행 순서', '1. LLM에 과업 설명, 판정 예시, 사용자 스토리, CQ, 온톨로지를 준다.\n2. LLM이 예/아니오 판정과 확인용 질의를 내놓는다.\n3. 사람이 온톨로지 편집기에서 이 제안을 보고 최종 판정한다{LIP}.'),
      ('논문의 결과', '지식 엔지니어 19명 실험. LLM 제안이 맞으면 사람의 정확도 70.5% → 83.2%, 틀리면 71.9% → 43.9%. 전체 정확도는 의미 있게 달라지지 않았다{LIP}.'),
      ('한계', '틀린 제안을 사람이 그대로 따라간다{LIP}.')], 2000)

add(h2('2.3 비교와 선택'))
add(label('표 4. CQ 검증 방법 비교'))
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
P('1장에서 고른 CQ 검증과 전문가 검토를, 2장에서 고른 질의 실행 대조로 구체화하면 아래 네 단계가 된다.')
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
      ('예', '"%s" → 질의를 실행해, 원자료 승인 기록에서 미리 정해 둔 기대 답(그 달의 승인 목록)과 같으면 통과' % EX_OK['question']),
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
    '추론기 검사를 넣지 않은 이유는 1.4에 적었다. 온톨로지를 OWL로 옮길지 정할 때 함께 검토한다.')

# ================================================================== 4. 향후 계획
add(h1('4. 향후 계획'))
add(label('4.1 업무 질문 82개로 검증된 CQ를 만들어 적용'))
lis('댐 운영 업무 82개에서 업무마다 실제로 물을 법한 질문을 하나씩 만들어 두었다(질문 %d개). 업무 목록에서 출발해 실제 업무에 가깝지만, 아직 연구자가 쓴 문장이다.' % len(Q82),
    '이 82개를 3장 1단계대로 전문가에게 검토받으면, 실제 업무를 반영하고 CQ의 약점을 보완한 검증된 CQ 세트가 된다.',
    '이 CQ 세트로 2~4단계를 적용해 온톨로지 구조를 개선하고 검증한다.')
add(label('4.2 KG 자체의 검증'))
lis('온톨로지 검증은 "구조가 질문에 답할 수 있는가"를 보는 것이고, 그 구조에 채운 값(KG)이 맞는지는 별도의 문제다.',
    '온톨로지 구조를 정한 뒤, KG에 채운 값이 맞고 빠짐없고 모순이 없는지 검증하는 방법을 같은 방식(최신 논문에서 인용을 따라가기)으로 조사해 적용한다. KG 품질 연구는 이를 정확성, 완전성, 일관성 같은 차원과 지표로 다룬다{ZA,PA}.')

# ================================================================== 부록
add(h1('부록 A. Gruber(1995)의 온톨로지 설계 기준', pagebreak=True))
P('OntoDSMS가 Noy·McGuinness 방법을 고른 이유로 든 기준이다(1.1). 아래는 온톨로지 평가 방법론 FOCA가 정리한 내용을 옮긴 것이다{FOCA}.')
tbl([['기준', '뜻'],
     ['명료성', '정의한 용어의 의도된 뜻을 효과적으로 전달해야 한다. 정의는 객관적이고 맥락에 독립적이어야 한다.'],
     ['일관성', '정의와 일관된 추론만 허용해야 한다. 정의하는 공리에 논리적 모순이 없어야 한다.'],
     ['확장성', '예상되는 여러 과업의 바탕이 되고, 기존 정의를 고치지 않고 확장할 수 있어야 한다.'],
     ['최소 인코딩 편향', '특정 표기나 구현의 편의 때문에 표현을 고르지 않아야 한다.'],
     ['최소 존재론적 약속', '필요한 만큼만 세계에 대해 주장해, 쓰는 쪽이 구체화할 여지를 남겨야 한다.']],
    [2200, 7772])

# ================================================================== 참고문헌
add(h1('참고문헌'))
assert set(ORDER) == set(REFS), set(REFS) ^ set(ORDER)
for i, k in enumerate(ORDER, 1):
    add(L.para('[%d] %s' % (i, REFS[k]), 17))

T.save(OUT, ''.join(B), L.IMGS, page_numbers=True)
print('saved', OUT, 'refs', len(ORDER))
