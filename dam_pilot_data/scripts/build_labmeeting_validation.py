#!/usr/bin/env python3
"""랩미팅 자료(docx): 온톨로지 검증 방법 — 선행연구 분석과 우리 구조에 맞는 방안, 향후 계획.
서식은 11/06 자료(build_labmeeting_how_kg2.py)와 같다(labdoc_lib, 같은 템플릿).
근거 문헌: references/evidence_literature/ (해석: lab_meeting/paper_review/검증부분_해석*.md)
11/12 사용자 메모 반영 후, 표 위주였던 내용을 방법마다 문단으로 풀어 씀(절차, 논문의 예와 수치, 한계).
향후 계획은 업무 질문 82개, 참고문헌은 번호.
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


def CODE(t):
    add(L.code(t))


REFS['AL23'] = 'Alharbi, R., Tamma, V., Grasso, F., & Payne, T. (2023). An experiment in retrofitting competency questions for existing ontologies. arXiv:2311.05662.'
REFS['WI'] = 'Wilson, R. S. I., Goonetillake, J. S., Walisadeera, A. I., & Ginige, A. (2023). A conceptual model for ontology quality assessment: A systematic review. Semantic Web, 14(6), 1051–1097.'
REFS['LG'] = 'Li, J., Garijo, D., & Poveda-Villalón, M. (2026). Large language models for ontology engineering: A systematic literature review. Semantic Web. https://doi.org/10.1177/22104968261465514'
REFS['KL'] = 'Keet, C. M., & Ławrynowicz, A. (2016). Test-driven development of ontologies. ESWC 2016, LNCS 9678. (extended version: arXiv:1512.06211)'

# ================================================================== 표지·요약
add(title('온톨로지 검증 방법', '선행연구 분석과 우리 구조에 맞는 방안'))
add(dateline('2026.11 · 문경민'))
add(h1('요약'))
lis('조사 방법: 최신 논문에서 출발해, 그 논문이 구축 방법론과 검증 방법 부분에서 인용한 과거 논문까지 거슬러 올라가 보았다.',
    '구축 방법론: 최신 댐 온톨로지 연구(2026)에서 거슬러 올라가 보니, 선행 댐 연구(2023)가 여러 방법론을 비교해 Noy·McGuinness 방법을 골랐다. 비교적 성숙하고, Gruber의 온톨로지 설계 기준 다섯 가지를 엄격히 따르는 유일한 방법이라는 이유였다. 이 방법은 역량 질문(CQ)으로 범위를 정하고, 완성한 온톨로지를 CQ와 전문가 논의로 확인한다.',
    '검증 방법: 최신 CQ 검증 연구(2025)에서 거슬러 올라가 보니, 온톨로지를 시험하는 여러 방식 중 CQ로 하는 방식이 가장 많이 쓰였다. CQ로 검증하는 방법은 질의 실행 대조, 개념 포괄도, LLM 보조가 있고, 맞는 답이 나오는지를 직접 확인하는 질의 실행 대조가 가장 직접적이다. 다만 CQ 자체의 품질이 결과를 좌우한다.',
    '우리 연구 적용: Noy가 제시한 두 확인 방법(CQ, 전문가 논의)을 구체화한다. 전문가 검토로 CQ 세트를 확정해 구성용과 검증용으로 나누고, 검증용 CQ를 질의로 실행해 정확성과 완전성을 센다.',
    '향후: 업무 질문 82개를 전문가 검토로 검증된 CQ로 만들어 적용하고, 그다음 KG 자체의 검증 방법을 조사해 적용한다.')

# ================================================================== 1. 구축 방법론
add(h1('1. 온톨로지 구축 방법론', pagebreak=True))
add(h2('1.1 최신 논문에서 거슬러 올라가기'))
P('우리 연구와 가장 가까운 최신 논문인 댐 결함 온톨로지(DDKG, 2026)에서 출발했다. 이 논문은 7단계 방법으로 온톨로지를 만들었지만 그 방법의 출처는 적지 않았고, 선행연구로 댐 안전 모니터링 온톨로지(OntoDSMS, 2023)를 인용한다{HU}. 그래서 OntoDSMS의 구축 방법론 부분을 보고, 거기서 인용한 문헌으로 다시 올라갔다.')
CODE('DDKG (2026, 댐 결함)  →  OntoDSMS (2023, 댐 안전 모니터링)\n   →  Noy·McGuinness (2001, 구축 방법)  →  Gruber (1995, 설계 기준)')
add(label('OntoDSMS는 왜 Noy·McGuinness 방법을 골랐나'))
P('OntoDSMS는 도메인 온톨로지를 만드는 방법으로 TOVE, IDEF5, Skeleton, KACTUS, SENSUS, METHONTOLOGY, Noy·McGuinness 방법의 일곱 가지를 들고, 그중 Noy·McGuinness 방법을 골랐다. 이유는 이 방법이 "비교적 성숙했고, Gruber의 온톨로지 구축 기본 원칙 다섯 가지를 엄격히 따르는 현재 유일한 방법"이라는 것이다{ZH}. 그리고 DDKG가 쓴 7단계도 Noy·McGuinness의 7단계와 같은 순서다{HU}.')
P('Gruber가 제안한 다섯 기준은 표 1과 같다. 온톨로지를 만들 때 지켜야 할 설계 원칙으로, 온톨로지 평가 방법론인 FOCA도 평가 연구를 정리하는 첫머리에 이 기준을 소개한다{FOCA}.')
add(label('표 1. Gruber(1995)의 온톨로지 설계 기준 (FOCA의 정리를 옮김)'))
tbl([['기준', '뜻'],
     ['명료성', '정의한 용어의 의도된 뜻을 효과적으로 전달해야 한다. 정의는 객관적이어야 하고 사회적·계산적 맥락에 독립적이어야 한다.'],
     ['일관성', '정의와 일관된 추론만 허용해야 한다. 최소한 정의하는 공리가 논리적으로 모순이 없어야 하고, 자연어 설명과 예시도 이와 맞아야 한다.'],
     ['확장성', '공유 어휘의 쓰임을 예상해 설계해야 한다. 예상되는 여러 과업의 개념적 바탕이 되고, 기존 정의를 고치지 않고 확장할 수 있어야 한다.'],
     ['최소 인코딩 편향', '특정 표기나 구현의 편의 때문에 표현을 고르지 않고, 지식 수준에서 개념을 정의해야 한다.'],
     ['최소 존재론적 약속', '의도한 지식 공유에 필요한 만큼만 세계에 대해 주장해, 쓰는 쪽이 필요에 따라 구체화할 여지를 남겨야 한다.']],
    [2200, 7772])

add(label('Noy·McGuinness 방법의 내용과 CQ'))
P('Noy·McGuinness는 온톨로지를 7단계로 만든다: ① 분야와 범위 정하기 → ② 기존 온톨로지 재사용 검토 → ③ 중요한 용어 나열 → ④ 클래스와 계층 정의 → ⑤ 클래스의 속성 정의 → ⑥ 속성의 제약 정의 → ⑦ 인스턴스 생성{NOY}.')
P('①단계에서 범위를 정하는 방법은 두 가지가 나온다. 먼저 기본 질문 네 가지에 답한다: 다룰 분야는 무엇인가, 무엇에 쓸 것인가, 어떤 유형의 질문에 답해야 하는가, 누가 쓰고 유지할 것인가. 다음으로 "범위를 정하는 한 방법"으로, 이 온톨로지 위의 지식베이스가 답해야 할 질문, 즉 역량 질문(CQ)을 대략 적어 본다. 와인 온톨로지라면 "구운 고기에는 어떤 와인이 가장 좋은가?" 같은 질문이다. 이 CQ는 ⑤단계에서 속성을 정의하는 기준으로 다시 쓰인다{NOY}. Noy·McGuinness는 CQ를 "한 방법"이라고 했지만, 최근 문헌은 CQ를 대부분의 온톨로지 공학 방법론에서 필수인 "초석"으로 보고{AL23}, Monfardini 외의 실무자 조사에서도 CQ는 주로 범위를 정하고 평가하는 데 쓰였다{KK}.')
P('완성한 온톨로지를 확인하는 방법도 두 가지가 나온다. 첫째, CQ가 나중에 "리트머스 시험"으로 쓰인다. 리트머스 종이가 산성인지를 바로 가려 주듯, 온톨로지가 이 질문들에 답할 만큼 정보를 담고 있는지를 가리는 기준이라는 뜻이다. 둘째, 초기 온톨로지를 응용에 써 보거나 그 분야 전문가와 논의하거나, 또는 둘 다 해서 평가하고 고친다{NOY}. 다만 Noy·McGuinness는 이를 "할 수 있다"는 수준으로 적었을 뿐, 구체적으로 어떻게 하는지는 정하지 않았다. 그 구체적인 방법은 2장에서 따로 거슬러 올라가 찾았다.')

add(h2('1.2 다른 방법론과의 비교와 우리의 선택'))
P('범위를 넓혀 최근 체계적 리뷰 두 편을 보았다. Wilson 외(2023)는 2010~2021년 연구를 리뷰해 Uschold·King, TOVE, METHONTOLOGY, SENSUS, On-To-Knowledge, DILIGENT 같은 전통적 방법론과 SAMOD, eXtreme Design(XD), AMOD 같은 애자일 방법론을 정리했다. 평가에 대해서는, Uschold·King, TOVE, On-To-Knowledge는 다 만든 뒤 평가 단계를 두고 METHONTOLOGY는 모든 단계마다 평가하지만, 어느 방법론도 평가 방법을 자세히 설명하지 않는다고 지적했다{WI}. Li·Garijo·Poveda-Villalón(2026)은 METHONTOLOGY, On-To-Knowledge, DILIGENT, Noy·McGuinness를 이 분야의 실무를 정립한 전통적 방법론으로 꼽으면서, 이들이 단계를 차례로 밟는 흐름이라 재사용·협업·상호운용 같은 요구는 다 담지 못할 수 있고, 이를 위해 NeOn이 여러 온톨로지를 엮는 네트워크 방식을 도입했다고 정리한다{LG}.')
P('수자원·재난 분야는 어떨까. 홍수·재난 온톨로지 12편을 정리한 Li 외(2025)의 표에서는 METHONTOLOGY 2편, NeOn 2편, Uschold 계열 2편이었고 나머지는 연구마다 따로 설계했으며, Noy·McGuinness 방법을 쓴 연구는 없었다{LI}. 즉 분야 전체에서 하나의 방법론이 정답으로 정해진 것은 아니다.')
P('정리하면, 문헌에서 Noy·McGuinness가 다른 방법보다 낫다고 판단한 근거는 OntoDSMS의 비교(성숙도, Gruber 기준 준수)이고, 같은 댐 분야의 최신 연구 두 편이 이 방법을 따랐다. 최근 리뷰가 지적한 약점(재사용·협업)은 여러 온톨로지를 엮을 때 중요한데, 우리는 댐 운영 온톨로지 하나를 새로 만드는 경우여서 이 약점의 영향이 작다고 보았다(우리 판단). 그래서 우리 온톨로지는 Noy·McGuinness 7단계로 설계했다.')

# ================================================================== 2. 검증 방법
add(h1('2. 온톨로지 검증 방법'))
add(h2('2.1 최신 논문에서 거슬러 올라가기'))
P('CQ로 온톨로지를 검증하는 최신 연구인 Lippolis 외(2025)와, CQ의 종류를 구분한 Keet·Khan(2024)에서 출발해 그 인용을 따라 올라갔다.')
CODE('Lippolis 외 (2025), Keet·Khan (2024)\n   →  Keet·Ławrynowicz (2016, 시험 주도 개발)\n   →  Blomqvist 외 (2012, 온톨로지 시험 방법론), Vrandečić·Gangemi (2006, 단위 시험)\n   →  Uschold·Gruninger (1996), Gruninger·Fox (1995, CQ의 시작)')
P('거슬러 올라간 흐름은 다음과 같다. CQ는 Gruninger·Fox(1995)에서 시작해{NOY}, Uschold·Gruninger(1996)가 비공식 질문과 형식 질의 사이를 잇는 온톨로지 요구사항으로 설명했다. Vrandečić·Gangemi(2006)는 소프트웨어의 단위 시험(unit test) 개념을 온톨로지에 가져와, 요구사항을 단위 시험처럼 다루자고 제안했다{LIP}. 이들이 검토한 방식에는 공리와 그 부정으로 시험하기, CQ를 형식화하기, 무결성 제약으로 점검하기, 정의역·치역 단언 등이 있었는데, 그 뒤 CQ로 하는 방식이 상대적으로 가장 많이 쓰이게 되었다{KL}. Blomqvist 외(2012)는 CQ를 요구사항으로 쓰는 온톨로지 시험 방법론을 제안하고, CQ를 SPARQL 질의로 다시 쓰면 모델링 실수를 효과적으로 찾아낸다는 것을 보였다{LIP}.')
P('이후 CQ 시험을 돕는 도구들이 나왔다. CQ의 패턴을 분석해 SPARQL 질의로 바꾸는 연구, 개체를 넣어 보고 질의로 확인하는 시험 도구, eXtreme Design의 시험 도구, 특정 클래스나 관계가 있는지만 확인하는 점검기 등이다{KL}. Keet·Ławrynowicz(2016)는 여기에 시험 주도 개발(TDD)을 더했다. 시험을 먼저 만들어 실패하는 것을 확인하고, 온톨로지를 고친 뒤, 같은 시험이 통과하는지 확인하는 방식이다{KL}. 가장 최근의 Lippolis 외(2025)는 이 CQ 검증을 LLM이 돕게 했다{LIP}. 그리고 Wilson 외(2023)는 온톨로지 품질 지표를 정리하면서 정확성을 "맞게 답한 CQ의 수"로, 완전성을 "충분한 답을 낸 CQ의 수"로 잰다고 정리했다{WI}.')

add(h2('2.2 CQ로 검증하는 방법과 진행'))
P('CQ로 검증한다는 것은 "이 질문에 맞게 답할 수 있는가"를 확인하는 것이다. 이를 실제로 확인하는 방법은 문헌에서 세 가지로 나뉜다.')

add(label('① 질의 실행 대조: CQ를 단위 시험처럼 쓰는 방법'))
P('Vrandečić·Gangemi와 Blomqvist 외에서 이어진 방법이다. Lippolis 외(2025)의 설명과 예를 따라 진행 순서를 정리하면 다음과 같다{LIP}.')
lis('CQ를 답하는 데 필요한 클래스와 관계로 풀어 쓴다. 예: "누가 오르간을 만들었거나 고쳤나?"에는 클래스 두 개(사람, 오르간)와 관계 하나(만들었다/고쳤다)가 필요하다.',
    '그 클래스와 관계가 온톨로지에 있는지 보고 판정한다. 모두 있으면 "예", 없으면 "아니오", 속성 하나만 빠져 있으면 "아니오(경미)"로 표시한다.',
    'CQ를 질의로 써서 실행하고, 나온 결과를 미리 정한 기대 답과 대조한다. 같으면 통과, 다르면 실패다.')
P('우리 온톨로지라면 CQ4(과거 방류 승인)의 질문 "%s"는 다음 질의가 된다(우리 KG는 Neo4j에 있어 질의 언어로 Cypher를 쓴다).' % EX_OK['question'])
CODE("MATCH (a:Approval)-[:concernsDam]->(d:Dam {damName: '소양강댐'})\nWHERE a.approvalTime STARTS WITH '2017-08'\nRETURN a.approvalTime, a.approvalContent")
P('기대 답은 원자료 승인 기록에서 미리 정해 둔다. 이 경우 원자료 기준 2건(8월 24일 최대 1,500㎥/s 방류 승인, 8월 27일 같은 방류의 기간 연장)이다. 질의 결과가 이 2건과 같으면 통과, 하나가 빠지거나 다른 댐 건이 섞이면 실패로 보고 원인을 찾는다.')
P('시험 주도 개발(TDD)은 이 방법을 온톨로지를 고치는 과정과 묶는다. ① 시험할 CQ를 고르고, ② 시험을 실행해 실패하는지 확인하고, ③ 통과에 필요한 클래스·관계를 온톨로지에 추가하고, ④ 같은 시험을 다시 실행해 통과하는지 확인하고, ⑤ 마지막으로 모든 시험을 다시 실행해 이번 수정이 기존에 통과하던 것을 망가뜨리지 않았는지 확인한다(회귀 시험). 원문은 8단계이며, 여기서는 추론기로 분류하는 단계와 정리 단계를 뺀 핵심만 옮겼다{KL}.')
P('한계도 지적된다. 질의를 사람이 손으로 써야 하고 온톨로지·질의 언어·분야 지식이 모두 필요해 시간과 자원이 많이 든다. CQ의 용어가 복잡하거나 모호하면 어떤 질의로 바꿔야 할지부터 정하기 어렵다{LIP}. 또 CQ에 답할 수 있는지를 시험해도, 무엇을 어떻게 고쳐야 하는지까지 알려 주지는 않는다{KL}.')

add(label('② 개념 포괄도: CQ의 개념이 온톨로지에 있는지 보는 방법'))
P('홍수 온톨로지를 반자동으로 만든 Li 외(2025)가 쓴 방법이다. 질의를 실행하지 않고, CQ에 나오는 개념이 온톨로지의 개념으로 충분히 덮이는지를 본다. 이 연구는 먼저 CQ를 나눠 70%는 온톨로지를 확장하는 데 쓰고, 30%는 마지막 평가에만 쓰도록 떼어 두었다. 평가는 떼어 둔 CQ로 다음과 같이 했다{LI}.')
lis('시험 CQ 12개에서 LLM이 질문마다 핵심 개념을 3~7개씩 뽑았다(모두 56개).',
    '온톨로지 구축에 참여한 평가자 3명이 각 개념을 "좋음/나쁨"으로 판단하고 빠진 개념을 제안했다. 3명 중 2명 이상이 승인한 개념만 남겼더니 2개가 빠지고 12개가 더해져 66개가 되었다(LLM 개념 승인율 93.5%).',
    '확정한 개념과 온톨로지의 클래스 이름을 각각 임베딩(text-embedding-3-large)하고, 코사인 유사도가 기준값 이상인 클래스가 있으면 그 개념이 포괄된 것으로 보았다.')
P('데이터 없이 구조만으로 많은 CQ를 빠르게 볼 수 있고, 중복 클래스나 빠진 개념이 드러난다는 장점이 있다. 그러나 저자들이 밝힌 한계가 크다. 어떤 유사도를 기준으로 할지 정할 수 없어, 같은 온톨로지인데도 기준값 0.3에서는 개념의 100%가, 0.9에서는 7.6%만 대응되었다. 또 모든 단어가 든 사전과 비교하면 포괄도 100%가 나오듯, 개념이 "있는지"를 볼 뿐 정확성이나 실제 쓸모는 보여 주지 못한다{LI}.')

add(label('③ LLM 보조: LLM이 판단을 제안하고 사람이 확인하는 방법'))
P('Lippolis 외(2025)는 ①의 수작업 부담을 줄이려고 OE-Assist라는 도구를 만들었다. LLM에 과업 설명, 판정 예시 몇 개, 온톨로지의 사용자 스토리, CQ, 온톨로지를 함께 주면, LLM이 CQ가 맞게 모델링되었는지(예/아니오)와 이를 확인할 SPARQL 질의를 내놓는다. 사람은 온톨로지 편집기 안에서 이 제안을 보고 최종 판정한다. 지식 엔지니어 19명으로 실험한 결과, LLM의 제안이 맞을 때는 사람의 정확도가 70.5%에서 83.2%로 올랐지만, 제안이 틀릴 때는 71.9%에서 43.9%로 크게 떨어져, 전체 정확도는 의미 있게 달라지지 않았다{LIP}.')

add(label('표 2. CQ로 검증하는 방법 요약'))
tbl([['방법', '확인하는 것', '장점', '한계'],
     ['① 질의 실행 대조{LIP,KL}', 'CQ에 실제로 맞는 답이 나오는가', '직접적이고, 모델링 실수를 잘 찾음', '질의 수작업, 모호한 CQ는 질의로 바꾸기 어려움'],
     ['② 개념 포괄도{LI}', 'CQ의 개념이 온톨로지에 있는가', '구조만으로 빠르게, 빠진 개념 발견', '기준값에 따라 100%~7.6%, 정확성은 못 봄'],
     ['③ LLM 보조{LIP}', '①의 판단을 LLM이 제안', '수작업과 체감 난이도 감소', '틀린 제안이면 정확도 71.9%→43.9%']],
    [2000, 2600, 2600, 2772])

add(h2('2.3 어떤 방법이 좋은가'))
add(label('CQ 방법 사이에서'))
P('우리가 확인하려는 것은 "운영자의 질문에 맞게 답하는가"이고, Wilson 외의 정리대로라면 이는 맞게 답한 CQ의 수(정확성)와 충분한 답을 낸 CQ의 수(완전성)로 잰다{WI}. 이를 직접 셀 수 있는 것은 실제로 답을 내 보는 ①이다. ②는 저자들 스스로 정확성을 보여 주지 못한다고 했고{LI}, ③은 틀린 제안이 사람의 판단을 흐린다는 결과가 있다{LIP}. 그래서 ①을 쓴다.')
add(label('CQ 외의 평가 접근과 비교'))
P('CQ 말고도 평가 접근은 있다. Wilson 외는 기존 서베이들이 평가 접근을 응용(과업) 기반, 데이터 기반, 기준 온톨로지 기반, 전문가 기반으로 나눈다고 정리한다{WI}. 그 서베이 중 하나인 Raad·Cruz는 어떤 접근도 모든 품질 기준을 평가하지 못하고, 가장 맞는 접근은 평가 목적에 따라 다르다고 정리한다{RC}. 우리 목적에 대 보면 표 3과 같다.')
add(label('표 3. 평가 접근과 우리 경우'))
tbl([['접근', '하는 일{RC,WI}', '우리 경우'],
     ['기준 온톨로지 기반', '참조 온톨로지와 비교', '댐 운영 온톨로지를 찾지 못함'],
     ['데이터(분야 문서) 기반', '분야 문서의 용어와 비교', '규정 문서는 있으나 이번에는 넣지 않음(3장)'],
     ['응용(과업) 기반', '쓰임에서의 성능으로 평가, CQ 검증이 여기에 가까움', '업무 질문과 CQ가 있음 → 중심'],
     ['전문가 기반', '전문가가 판단', 'CQ 검토에 넣음 → 아래 약점 보완'],
     ['품질 기준 기반', '구조 지표, 논리 규칙(추론기)', 'OWL로 정의하지 않아 이번에는 넣지 않음(3장)']],
    [2400, 3800, 3772])
P('Lippolis 외도 기준 온톨로지·분야 문서 비교는 비교할 자원이 없거나 불완전한 경우가 많고, 온톨로지의 요구사항을 평가에 반영하지 못한다고 지적한다{LIP}. 질문에 답하는 것이 목적인 우리에게는 응용(과업) 기반인 CQ 검증과 전문가 기반이 목적에 맞다.')

add(label('그런데 CQ에는 약점이 있다'))
lis('기준이 없다: CQ를 어떻게 만들고 무엇이 좋은 CQ인지에 대한 안내가 매우 부족해, CQ가 모호하게 쓰이거나 질의로 바꿀 수 없게 만들어진다. 모호한 CQ는 불완전한 온톨로지로 이어진다{KK}.',
    '만드는 사람에 따라 크게 다르다: 같은 요구사항에서 만든 CQ를 비교하면 엔지니어가 만든 CQ의 수용률이 90%를 넘어 가장 높았고, 질문 단위로 겹치는 정도는 엔지니어 두 명 사이가 15.3%, 두 LLM 사이가 2.9%, LLM과 사람 사이는 거의 0%였다. 좋은 CQ를 끌어내는 데 사람의 전문성이 여전히 중심이다{AL}.',
    '지식의 간극이 있다: 엔지니어는 CQ를 형식화할 줄 알지만 분야 지식이 부족하고, 도메인 전문가는 그 반대다. IDEA2는 전문가가 CQ를 검토하고 고쳐 다시 검토받는 과정을 합의에 이를 때까지 반복해 CQ의 수용도와 관련성을 높였다{WL}.')
P('어느 검증 방법을 쓰든 시험지(CQ)가 나쁘면 결과도 의미가 없다. 지금 우리 CQ는 연구자가 만들었고, 같은 CQ로 온톨로지를 만들고 확인해 왔다. 연구자의 생각으로 연구자의 결과를 채점하는 셈이므로, 분야를 아는 사람이 CQ를 검토하는 과정이 필요하다.')

# ================================================================== 3. 적용
add(h1('3. 우리 연구에 적용'))
P('새 방법을 더하는 것이 아니라, 처음 설계에서 따른 Noy·McGuinness가 제시한 두 확인 방법(CQ 리트머스 시험, 전문가와 논의)을 2장의 문헌으로 구체화한다. 바뀌는 점은 두 가지다. CQ를 전문가 검토로 확정하고, 같은 CQ로 만들고 확인하던 것을 구성용과 검증용으로 나눈다.')

add(label('1단계. 전문가 검토로 CQ 세트 확정'))
P('질문 목록을 전문가 2명 이상에게 보내 질문마다 세 가지를 판단받는다: (가) 실제 업무에서 묻는 질문인가, (나) 뜻이 하나로 읽히는가, (다) 우리 온톨로지가 반드시 답할 수 있어야 하는가. 고칠 점은 직접 적어 달라고 한다. 예를 들어 "충주댐 계획홍수위까지 얼마나 여유 있어?"는 지금 수위 기준인지, 어느 시점 기준인지가 드러나지 않아 (나)에서 고칠 대상이 될 수 있다. 2명 이상이 동의한 질문만 남기고, 의견이 갈린 질문은 고쳐서 다시 검토받는다. 홍수 온톨로지 연구가 평가자 3명 중 2명 이상이 승인한 개념만 남긴 방식{LI}과 IDEA2가 합의에 이를 때까지 반복한 방식{WL}을 따랐다.')

add(label('2단계. 구성용과 검증용으로 나누기'))
P('확정한 CQ를 구성용(온톨로지를 만들고 고치는 데 씀)과 검증용(시험에만 씀)으로 나눈다. 비율은 홍수 온톨로지 연구의 70:30을 따른다{LI}. 검증용은 1단계 (다)에서 "반드시 답해야 한다"고 판단된 CQ에서만 뽑는다. 범위를 정하는 CQ는 답할 수 없어도 되지만, 검증하는 CQ는 질의로 바꿀 수 있고 반드시 답할 수 있어야 하기 때문이다{KK}. 한 유형이 한쪽에만 몰리지 않도록 유형마다 나눠 담는다(우리 설정).')

add(label('3단계. 검증용 CQ를 질의로 실행해 판정'))
P('검증용 CQ마다 2.2 ①의 순서대로 "예/아니오/아니오(경미)"로 판정하고{LIP}, "예"인 CQ는 질의를 실행해 원자료에서 미리 정한 기대 답과 대조한다(예: 2.2의 소양강댐 승인 질의). 결과는 맞게 답한 CQ의 수(정확성)와 충분한 답을 낸 CQ의 수(완전성)로 센다{WI}. 우리 온톨로지는 CQ마다 질의 템플릿을 이미 갖고 있어 질의 수작업이 줄고, 모호한 CQ는 1단계에서 먼저 걸러진다.')

add(label('4단계. 통과하지 못한 CQ로 구조 개선 (시험 주도 개발)'))
P('예를 들어 "%s"는 지금 온톨로지로 답할 수 없다(판정: 아니오). 운영기준 클래스에는 홍수기 제한수위만 있고, 댐 클래스에는 댐 이름과 형식만 있어 계획홍수위와 상시만수위를 담을 곳이 없기 때문이다. 이때 TDD 순서를 따른다. 시험이 실패하는 것을 확인했으니, 같은 내용을 담은 구성용 CQ를 근거로 댐 제원 속성을 추가하고, 같은 시험을 다시 실행해 통과하는지 보고, 모든 검증용 CQ를 다시 실행해 기존 통과 결과가 유지되는지 확인한다{KL}. 이는 Noy·McGuinness의 ⑤단계(CQ에 답할 정보가 부족하면 속성을 정의)를 다시 밟는 것이기도 하다{NOY}.' % EX_EXT['question'])
P('구조를 고치는 근거는 구성용 CQ에서만 가져오고, 검증용 CQ는 통과 여부를 판단하는 데만 쓴다. 시험 문제를 보고 답안을 맞추면 시험이 의미가 없듯, 검증용 CQ에 맞춰 구조를 고치면 검증이 되지 않기 때문이다. 홍수 온톨로지 연구가 30%를 "최종 평가에만" 쓰도록 떼어 둔 이유도 같다{LI}.')

add(label('정한 것과 아직 정할 것'))
tbl([['항목', '정한 것', '근거'],
     ['검토자', '댐 운영 실무자와 수자원 분야 연구자, 2명 이상', 'Noy의 전문가 논의{NOY}, CQ 약점 보완{AL,WL}'],
     ['남길 기준', '2명 이상 동의, 갈리면 고쳐서 재검토', '3명 중 2명 승인{LI}, 합의까지 반복{WL}'],
     ['나누는 비율', '구성용 70%, 검증용 30%, 유형별로 나눔', '70:30{LI}, 유형별은 우리 설정'],
     ['검증용 조건', '반드시 답해야 하는 CQ만', '검증 CQ는 답할 수 있어야{KK}'],
     ['검증 방법', '질의 실행 대조, 정확성·완전성으로 셈, 고칠 때는 TDD 순서', '{LIP,WI,KL}'],
     ['LLM 보조', '쓰지 않음', '틀린 제안이면 정확도 크게 하락{LIP}'],
     ['아직 정할 것', '검토자 섭외', '']],
    [1700, 4100, 4172])
P('"2명 이상 동의"와 "70:30"은 홍수 온톨로지 연구 한 편에서 가져온 것이고, 그 연구에서 다수결 대상은 CQ가 아니라 CQ에서 뽑은 개념이었다. 따라서 이 숫자는 검증된 최적값이 아니라 선행연구를 따른 우리 설정이다.')

add(label('검토했지만 이번에 넣지 않은 것'))
lis('추론기 검사: 홍수·재난 분야에서 CQ로 검증한 4편은 모두 추론기 검사도 함께 썼다{LI}. 그러나 추론기는 OWL 같은 논리 언어로 적은 규칙이 있어야 돌아가는데, 우리 온톨로지는 OWL로 정의하지 않고 Neo4j 그래프 구조로 구현했고, 처음 설계에도 없던 방법이다. 온톨로지를 OWL로 옮길지 정할 때 함께 검토한다.',
    '규정 문서와의 비교: 이번 목적에서 확인할 정확성과 완전성은 CQ에 답한 결과로 잴 수 있다{WI}. 처음 설계에 없던 방법을 결합을 위해 덧붙이지 않는다.')

# ================================================================== 4. 향후 계획
add(h1('4. 향후 계획'))
add(h2('4.1 업무 질문 82개로 검증된 CQ를 만들어 적용'))
P('댐 운영 업무 82개에서 업무마다 실제로 물을 법한 질문을 하나씩 만들어 두었다(질문 %d개). 이 질문들은 업무 목록에서 출발했다는 점에서 연구자가 머릿속으로 만든 CQ보다 실제 업무에 가깝지만, 아직 연구자가 쓴 문장이다. 이 82개를 3장의 1단계대로 전문가에게 검토받으면, 실제 업무를 반영하고 CQ의 약점(모호함, 연구자 관점)을 보완한 검증된 CQ 세트가 된다. 그다음 이 CQ 세트로 2~4단계를 적용한다.' % len(Q82))
add(h2('4.2 KG 자체의 검증'))
P('온톨로지 검증은 "구조가 질문에 답할 수 있는가"를 보는 것이고, 그 구조에 채운 값(KG)이 맞는지는 별도의 문제다. 온톨로지 구조를 정한 뒤, KG에 채운 값이 맞고 빠짐없고 모순이 없는지 검증하는 방법을 같은 방식(최신 논문에서 거슬러 올라가기)으로 조사해 적용한다. KG 품질 연구는 이를 정확성, 완전성, 일관성 같은 차원과 지표로 다룬다{ZA,PA}.')

# ================================================================== 참고문헌
add(h1('참고문헌'))
assert set(ORDER) == set(REFS), set(REFS) ^ set(ORDER)
for i, k in enumerate(ORDER, 1):
    add(L.para('[%d] %s' % (i, REFS[k]), 17))

T.save(OUT, ''.join(B), L.IMGS, page_numbers=True)
print('saved', OUT, 'refs', len(ORDER))
