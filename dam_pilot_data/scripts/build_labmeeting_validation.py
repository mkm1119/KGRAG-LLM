#!/usr/bin/env python3
"""랩미팅 자료(docx): 온톨로지 검증 방법 — 선행연구 분석과 우리 구조에 맞는 방안, 향후 계획.
서식은 11/06 자료(build_labmeeting_how_kg2.py)와 같다(labdoc_lib, 같은 템플릿).
근거 문헌: references/evidence_literature/ (해석: lab_meeting/paper_review/검증부분_해석*.md)
질문 세트 숫자는 05_retrieval/question_set_v2.json에서 센다. KG 검증은 이번 범위에서 빼고 향후 계획에 둔다.
사용: python3 scripts/build_labmeeting_validation.py <출력 docx>
"""
import collections, importlib.util, json, os, sys
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

ROOT = os.path.join(HERE, '..'); N = os.path.join(ROOT, '03_normalized')
LAB = os.path.join(ROOT, '..', 'lab_meeting')
OUT = sys.argv[1]
T = L.Template(os.path.join(LAB, '랩미팅 자료_KG구축_검색답변_최종.docx'))

# ------------------------------------------------------------------ 사실: 연구용 질문 세트 v2
R5 = os.path.join(ROOT, '05_retrieval')
QS = json.load(open(os.path.join(R5, 'question_set_v2.json'), encoding='utf-8'))
EXP = collections.Counter(q['expect'] for q in QS)
assert len(QS) == 127 and (EXP['answer_now'], EXP['extend'], EXP['refuse']) == (47, 42, 37)

B = []
add = B.append


def lis(*items):
    for t in items:
        add(li(t))


rtable = lambda rows, widths: table(rows, widths, header=True, firstcol=False)

# ================================================================== 표지·요약
add(title('온톨로지 검증 방법', '선행연구 분석과 우리 구조에 맞는 방안'))
add(dateline('2026.11 · 문경민'))
add(h1('요약'))
lis('조사 범위: 방법론·서베이(일반) → 수자원·재난 분야 → 댐 분야 순으로 좁혀 왔으며, 출발 논문의 참고문헌을 따라가는 조사를 계속하고 있다.',
    '주요 온톨로지 구축 방법론은 역량 질문(CQ)을 범위 설정과 검증의 기본으로 두며, 수자원·재난 분야와 댐 분야의 온톨로지 연구도 이를 따랐다.',
    'CQ 검증은 오래 쓰인 방법이지만, CQ를 누가 어떻게 만드느냐에 따라 품질이 달라지는 약점이 있다.',
    '→ 전문가의 검토를 받아 CQ 세트를 만들고, 그중 검증용 CQ로 온톨로지를 시험하는 방안을 제안한다.',
    '향후: 우리가 만든 질문 세트를 전문가 검토로 검증된 CQ로 만들어 온톨로지 구조를 개선·검증하고, 그다음 KG 자체의 검증 방법을 조사해 적용한다.')

# ================================================================== 1. 온톨로지 검증
add(h1('1. 온톨로지 검증', pagebreak=True))
add(h2('1.1 선행연구는 온톨로지를 어떻게 만들고 검증했나'))
lis('주요 온톨로지 구축 방법론(Noy·McGuinness, NeOn, METHONTOLOGY, eXtreme Design)은 공통으로 역량 질문(CQ), 즉 "온톨로지가 답할 수 있어야 하는 질문"을 설계와 검증의 바탕으로 둔다(Watkiss-Leek 외, 2026). 그중 Noy·McGuinness는 1단계에서 CQ로 범위를 정하고, 이 질문을 나중에 온톨로지가 충분한지 확인하는 리트머스 시험으로 쓰라고 한다.',
    'CQ를 질의로 바꿔 기대한 답이 나오는지 보는 CQ 검증은 10년 넘게 쓰인 방법이다(Lippolis 외, 2025).',
    '수자원·재난 분야 온톨로지 12편을 정리한 연구에서도 CQ를 질의로 바꿔 답이 나오는지 확인하거나 추론기로 모순을 검사한 경우가 가장 많았다(Li 외, 2025).',
    '댐 분야 논문 두 편(Huang 외, 2026; Zhou 외, 2023)도 CQ를 1단계에 두는 Noy·McGuinness의 7단계 방법으로 온톨로지를 만들었다.')

add(h2('1.2 다른 검증 방법은 왜 어려운가'))
lis('온톨로지 평가 방법은 크게 기준 온톨로지와 비교, 분야 문서와 비교, 과업 성능, 품질 기준의 네 가지다(Raad·Cruz, 2015).',
    '앞의 두 방법은 비교할 기준 자원이 있어야 하는데, 이런 자원은 대부분 없거나 불완전하고, 온톨로지의 요구사항을 반영하지도 못한다(Lippolis 외, 2025). 댐 운영 분야에도 비교할 기준 온톨로지가 없다.')

add(h2('1.3 CQ의 약점'))
lis('좋은 CQ가 무엇인지에 대한 기준과 지침이 부족해, CQ가 모호하게 쓰이거나 답할 수 없게 만들어지는 경우가 많다. 모호한 CQ는 불완전한 온톨로지로 이어진다(Keet·Khan, 2024).',
    '같은 요구사항에서도 CQ를 만드는 방법에 따라 결과가 크게 다르다. 온톨로지 엔지니어가 만든 CQ가 가장 적합했고, LLM이 만든 CQ는 사람의 것과 겹치는 부분이 거의 없었다(Alharbi 외, 2025).',
    '엔지니어는 CQ를 형식화할 줄 알지만 도메인 지식이 부족하고, 도메인 전문가는 그 반대라는 간극이 있다(Watkiss-Leek 외, 2026).',
    '→ 지금 우리 CQ는 연구자가 만든 것이라, 이 CQ로만 검증하면 연구자의 생각으로 연구자의 결과를 채점하는 셈이 된다.')

add(h2('1.4 우리 구조에 제안하는 방법'))
lis('전문가의 검토를 받아 CQ 세트를 만든다. 위 연구들은 모두 사람, 특히 도메인 전문가의 참여로 CQ의 품질 문제를 보완했다(Alharbi 외, 2025; Watkiss-Leek 외, 2026).',
    'CQ를 범위 설정용과 검증용으로 나눈다. 범위 설정 CQ는 답할 수 없어도 되지만 검증 CQ는 온톨로지가 반드시 답할 수 있어야 한다(Keet·Khan, 2024). 홍수 온톨로지 연구도 CQ의 70%로 온톨로지를 만들고 떼어 둔 30%로 평가했다(Li 외, 2025).',
    '검증 CQ로 온톨로지를 시험하고, 답할 수 없는 CQ가 있으면 빠진 구조를 찾아 고친다.',
    '→ 지금의 연구 구조(CQ로 설계한 온톨로지)를 그대로 쓰면서 CQ의 약점을 전문가로 보완할 수 있어, 우리 연구 구조에 가장 무리가 없는 방안으로 판단했다.')
add(label('정할 것'))
lis('누가 검토할지: 댐 운영 실무 경험자, 수자원 분야 연구자',
    '몇 명이 검토할지: 판단이 갈릴 때를 대비해 2명 이상')

# ================================================================== 2. 향후 계획
add(h1('2. 향후 계획'))
add(h2('2.1 질문 세트로 검증된 CQ 만들기'))
lis('지금까지 연구용 질문 세트 %d개를 만들고, 질문마다 기대 동작을 정해 두었다: 지금 KG로 답해야 할 질문 %d개, 확장해야 답할 수 있는 질문 %d개, 범위 밖이라 거절해야 할 질문 %d개.' % (len(QS), EXP['answer_now'], EXP['extend'], EXP['refuse']),
    '이 질문 세트를 전문가에게 검토받으면, 실제 업무의 지식 요구를 반영한 검증된 CQ 세트가 된다. 1.4의 "전문가 검토를 받은 CQ 세트"를 새로 만드는 대신 이미 만든 질문 세트에서 출발할 수 있다.',
    '설계에 쓴 CQ와 따로 만든 질문이라, 검증용 CQ(Keet·Khan, 2024)로 쓰기에도 맞는다.')
add(h2('2.2 검증된 CQ로 온톨로지 구조 개선·검증'))
lis('지금 답해야 할 질문에 답이 나오는지 시험해 온톨로지를 검증한다.',
    '확장해야 할 질문은 지금 온톨로지에 없는 구조를 가리키므로, 이 질문으로 온톨로지 구조를 개선하고 다시 검증한다.')
add(h2('2.3 KG 자체의 검증'))
lis('온톨로지 구조를 정한 뒤, 그 구조에 채운 값이 맞고 빠짐없고 모순이 없는지 검증하는 방법을 조사해 적용한다. KG 품질 연구는 이를 정확성, 완전성, 일관성 같은 차원과 지표로 다룬다(Zaveri 외, 2016; Paulheim, 2017).')

# ================================================================== 참고문헌
add(h1('참고문헌'))
lis('Alharbi, R., Tamma, V., Payne, T. R., & de Berardinis, J. (2025). A comparative study of competency question elicitation methods from ontology requirements. arXiv:2507.02989.',
    'Huang, J., Hou, W., Zhang, S., Du, Z., & Yin, J. (2026). Dam defects ontology and knowledge graph construction from multi-source hazard data using large language models. Advanced Engineering Informatics, 76, 104987.',
    'Keet, C. M., & Khan, Z. C. (2024). Discerning and characterising types of competency questions for ontologies. arXiv:2412.13688.',
    'Li, S., Erickson, C., Zajac, M., Guo, X., Duan, Q., & Gong, J. (2025). A semi-automated framework for flood ontology construction with an application in risk communication. Water, 17, 2801.',
    'Lippolis, A. S., Saeedizade, M. J., Keskisärkkä, R., Gangemi, A., Blomqvist, E., & Nuzzolese, A. G. (2025). Large language models assisting ontology evaluation. arXiv:2507.14552.',
    'Noy, N. F., & McGuinness, D. L. (2001). Ontology development 101: A guide to creating your first ontology. Stanford University.',
    'Paulheim, H. (2017). Knowledge graph refinement: A survey of approaches and evaluation methods. Semantic Web, 8(3), 489–508.',
    'Raad, J., & Cruz, C. (2015). A survey on ontology evaluation methods. KEOD 2015, 179–186.',
    'Watkiss-Leek, E., Alharbi, R., Rostron, H., Ng, A., et al. (2026). IDEA2: Expert-in-the-loop competency question elicitation for collaborative ontology engineering. arXiv:2604.01344.',
    'Zaveri, A., Rula, A., Maurino, A., Pietrobon, R., Lehmann, J., & Auer, S. (2016). Quality assessment for linked data: A survey. Semantic Web, 7(1), 63–93.',
    'Zhou, Y., Bao, T., Shu, X., Li, Y., & Li, Y. (2023). BIM and ontology-based knowledge management for dam safety monitoring. Automation in Construction, 145, 104649.')

T.save(OUT, ''.join(B), L.IMGS, page_numbers=True)
print('saved', OUT)
