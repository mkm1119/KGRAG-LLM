#!/usr/bin/env python3
"""랩미팅 자료(docx): 온톨로지 검증과 KG 검증 방법 — 선행연구 분석과 우리 구조에 맞는 방안.
서식은 11/06 자료(build_labmeeting_how_kg2.py)와 같다(labdoc_lib, 같은 템플릿).
근거 문헌: references/evidence_literature/ (해석: lab_meeting/paper_review/검증부분_해석*.md)
KG 숫자는 dam_pilot_data/03_normalized/kgv4_*.csv에서 계산한다.
사용: python3 scripts/build_labmeeting_validation.py <출력 docx>
"""
import collections, csv, importlib.util, os, sys
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

# ------------------------------------------------------------------ 사실: 지금 KG(kgv4)에서 계산
rd = lambda p: list(csv.DictReader(open(os.path.join(N, p), encoding='utf-8-sig')))
ENT, REL = rd('kgv4_entities.csv'), rd('kgv4_relations.csv')
CC = collections.Counter(e['class'] for e in ENT)
SUB = collections.defaultdict(set)
for r in REL:
    SUB[r['relation']].add(r['subject'])
N_APR, N_OP = CC['Approval'], CC['Operation']
APR_DAM, OP_DAM, APR_OP = len(SUB['concernsDam']), len(SUB['performedOnDam']), len(SUB['authorizes'])
assert (len(ENT), len(REL), N_APR, N_OP) == (264, 418, 80, 68)
assert (APR_DAM, OP_DAM, APR_OP) == (80, 68, 63)

B = []
add = B.append


def lis(*items):
    for t in items:
        add(li(t))


rtable = lambda rows, widths: table(rows, widths, header=True, firstcol=False)

# ================================================================== 표지·요약
add(title('온톨로지와 KG의 검증 방법', '선행연구 분석과 우리 구조에 맞는 방안'))
add(dateline('2026.11 · 문경민'))
add(h1('요약'))
add(label('온톨로지 검증'))
lis('댐 분야 최근 논문들은 온톨로지를 Noy·McGuinness 방법으로 만들었고, 이 방법은 역량 질문(CQ)을 범위 설정과 검증의 기본으로 제시한다.',
    'CQ 검증은 오래 쓰인 방법이지만, CQ를 누가 어떻게 만드느냐에 따라 품질이 달라지는 약점이 있다.',
    '→ 전문가의 검토를 받아 CQ 세트를 만들고, 그중 검증용 CQ로 온톨로지를 시험하는 방안을 제안한다.')
add(label('KG 검증'))
lis('댐 분야 논문들은 추출 단계만 수치로 평가하고 KG 자체의 검증은 향후 과제로 남겼다. KG 품질 연구는 정확성·완전성·일관성을 지표로 잰다.',
    '사람이 판정하는 정답 자료는 비용이 커서 작게 만들 수밖에 없는 것이 약점이다.',
    '→ 우리 KG는 정형 원자료에서 만들었으므로 원자료를 기준으로 지표를 자동 계산하고, 원자료로 판단할 수 없는 부분만 전문가가 표본으로 판정하는 방안을 제안한다.')

# ================================================================== 1. 온톨로지 검증
add(h1('1. 온톨로지 검증', pagebreak=True))
add(h2('1.1 선행연구는 온톨로지를 어떻게 만들고 검증했나'))
lis('댐 분야 최근 논문 두 편(Huang 외, 2026; Zhou 외, 2023)은 모두 Noy·McGuinness의 7단계 방법으로 온톨로지를 만들었다.',
    'Noy·McGuinness는 1단계에서 "온톨로지가 답할 수 있어야 하는 질문", 즉 역량 질문(CQ)으로 범위를 정하고, 이 질문을 나중에 온톨로지가 충분한지 확인하는 리트머스 시험으로 쓰라고 한다.',
    '다른 주요 방법론(NeOn, METHONTOLOGY, eXtreme Design)도 CQ를 설계와 검증의 바탕으로 쓴다. 홍수 분야 온톨로지들도 CQ를 질의로 바꿔 답이 나오는지 확인하거나 추론기로 모순을 검사한 경우가 가장 많았다(Li 외, 2025).',
    'CQ를 질의로 바꿔 기대한 답이 나오는지 보는 CQ 검증은 10년 넘게 쓰인 방법이다(Lippolis 외, 2025).')

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
lis('검증 CQ를 어디서 얻을지: 설계에 쓰지 않은 질문, 또는 전문가가 낸 질문',
    '누가 검토할지: 댐 운영 실무 경험자, 수자원 분야 연구자')

# ================================================================== 2. KG 검증
add(h1('2. KG 검증'))
add(h2('2.1 선행연구는 KG를 어떻게 검증했나'))
lis('댐 분야 논문들은 KG 자체를 수치로 검증하지 않았다. Huang 외(2026)는 개체 인식 단계만 정밀도·재현율로 평가하고, KG 자체의 구조, 완전성, 일관성, 실제 효용 평가를 향후 과제로 남겼다. Purohit 외(2024)도 정식 평가를 향후 과제로 두었다.',
    '도메인 특화 KG는 그 분야의 사실을 모두 모은 완전하고 정확한 기준이 없어 평가가 어렵고, 사례 연구나 도메인 전문가로 평가하기도 한다(Abu-Salih, 2021).',
    '반면 KG 품질 연구는 품질을 차원으로 나누고 차원마다 지표로 잰다(Zaveri 외, 2016). 그중 핵심은 정확성(값이 실제 사실과 맞는가), 완전성(필요한 정보가 다 있는가), 일관성(모순이 없는가)이다.',
    '평가는 일부를 사람이 정답으로 표시해 비교하거나 결과를 사람이 판정하는 방식으로 하며, 판정은 보통 표본으로 하고 판정자 간 일치도를 함께 보고한다(Paulheim, 2017). KG의 정확도를 "맞는 사실의 비율"로 정의하고 표본으로 추정하는 방법도 있다(Gao 외, 2019).')

add(h2('2.2 이 방법들의 약점'))
lis('사람이 만드는 정답 자료는 품질이 높지만 비용이 커서 작게 만들 수밖에 없다(Paulheim, 2017).',
    '사람의 판정도 사람마다 달라 여러 명의 판정과 일치도 확인이 필요하다(Paulheim, 2017).')

add(h2('2.3 우리 구조에 제안하는 방법'))
lis('우리 KG는 승인 기록, 관측 자료, 규정 같은 정형 원자료에서 만들었다. 도메인 KG 연구들이 어려워한 기준 자료를 원자료로 대신할 수 있어, KG 품질 연구의 지표를 그대로 계산할 수 있다.')
add(label('표 1. 우리 KG에 적용할 검증'))
add(rtable([['차원', '확인할 것', '방법', '누가'],
            ['정확성', 'KG의 값이 원자료와 같은가', '원자료와 전부 대조', '자동'],
            ['', '글에서 뽑은 값과 댐 연결이 맞는가', '표본을 뽑아 판정', '전문가'],
            ['완전성', '원자료의 대상과 연결이 빠짐없이 들어갔는가', '비율 계산', '자동'],
            ['일관성', '온톨로지에 정한 규칙을 지키는가 (예: 승인은 댐 하나에 연결)', '규칙 위반 질의', '자동']],
           [1500, 3900, 2672, 1900]))
lis('예: 지금 KG에서 완전성을 계산하면 승인 %d건과 운영행위 %d건은 모두 댐과 연결되어 있다. 승인 중 운영행위와 이어진 것은 %d건(%d%%)이다. 나머지 %d건이 원래 운영이 없었던 것인지 연결이 빠진 것인지는 원자료만으로 판단하기 어려워, 이런 대상이 전문가 판정으로 넘어간다.'
    % (APR_DAM, OP_DAM, APR_OP, round(APR_OP / N_APR * 100), N_APR - APR_OP),
    '전문가 판정은 같은 댐이나 같은 승인 건끼리 묶어 보여 준다. 같은 대상의 사실을 묶어 확인하면 판정 비용이 줄어든다(Gao 외, 2019).',
    '→ 자동으로 할 수 있는 것은 원자료로 하고 사람이 판단해야 하는 것만 전문가에게 맡겨, 비용을 줄이면서 댐 분야 논문들이 향후 과제로 남긴 KG 자체의 검증을 수치로 할 수 있다.')
add(label('정할 것'))
lis('전문가에게 보여 줄 표본의 크기와 묶는 단위', '판정자 수(2명 이상이어야 일치도를 낼 수 있음)')

# ================================================================== 참고문헌
add(h1('참고문헌'))
lis('Abu-Salih, B. (2021). Domain-specific knowledge graphs: A survey. Journal of Network and Computer Applications, 185, 103076.',
    'Alharbi, R., Tamma, V., Payne, T. R., & de Berardinis, J. (2025). A comparative study of competency question elicitation methods from ontology requirements. arXiv:2507.02989.',
    'Gao, J., Li, X., Xu, Y. E., Sisman, B., Dong, X. L., & Yang, J. (2019). Efficient knowledge graph accuracy evaluation. Proceedings of the VLDB Endowment, 12(11).',
    'Huang, J., Hou, W., Zhang, S., Du, Z., & Yin, J. (2026). Dam defects ontology and knowledge graph construction from multi-source hazard data using large language models. Advanced Engineering Informatics, 76, 104987.',
    'Keet, C. M., & Khan, Z. C. (2024). Discerning and characterising types of competency questions for ontologies. arXiv:2412.13688.',
    'Li, S., Erickson, C., Zajac, M., Guo, X., Duan, Q., & Gong, J. (2025). A semi-automated framework for flood ontology construction with an application in risk communication. Water, 17, 2801.',
    'Lippolis, A. S., Saeedizade, M. J., Keskisärkkä, R., Gangemi, A., Blomqvist, E., & Nuzzolese, A. G. (2025). Large language models assisting ontology evaluation. arXiv:2507.14552.',
    'Noy, N. F., & McGuinness, D. L. (2001). Ontology development 101: A guide to creating your first ontology. Stanford University.',
    'Paulheim, H. (2017). Knowledge graph refinement: A survey of approaches and evaluation methods. Semantic Web, 8(3), 489–508.',
    'Purohit, S., Chin, G., Mackey, P. S., & Cottam, J. A. (2024). GraphAide: Advanced graph-assisted query and reasoning system. 2024 IEEE International Conference on Big Data.',
    'Raad, J., & Cruz, C. (2015). A survey on ontology evaluation methods. KEOD 2015, 179–186.',
    'Watkiss-Leek, E., Alharbi, R., Rostron, H., Ng, A., et al. (2026). IDEA2: Expert-in-the-loop competency question elicitation for collaborative ontology engineering. arXiv:2604.01344.',
    'Zaveri, A., Rula, A., Maurino, A., Pietrobon, R., Lehmann, J., & Auer, S. (2016). Quality assessment for linked data: A survey. Semantic Web, 7(1), 63–93.',
    'Zhou, Y., Bao, T., Shu, X., Li, Y., & Li, Y. (2023). BIM and ontology-based knowledge management for dam safety monitoring. Automation in Construction, 145, 104649.')

T.save(OUT, ''.join(B), L.IMGS, page_numbers=True)
print('saved', OUT)
