#!/usr/bin/env python3
"""2장 다절과 3장의 범위를 나눈다(한 번만 실행, 이전 내용은 sections/_old5).
- 2장 다절(1_3): 다섯 기술요소를 같은 깊이로 조사·비교하고 적용 방향을 정한다('어떤 방법으로 할 것인가').
- 3장 나절(2_2): 온톨로지와 메타데이터에 무엇을 담을지를 조사한다. 설계 방법의 조사는 2장 다절 2)로 옮기고,
  3.2.2는 선행 온톨로지의 구성(Class·관계) 조사로 바꾼다.
- 3장 다절(2_3): 조사를 다시 하지 않고 단계 구성만 둔다. 질의 해석·근거 조회·지식 전달 방식의 조사는 2장 다절 5)·6)으로 옮긴다.
사용: python3 dam_pilot_data/scripts/apply_restructure_1124.py
"""
import glob, json, os, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
SEC = os.path.join(HERE, '..', '..', 'project_khnp', 'final_report', 'sections')
OLD = os.path.join(SEC, '_old5')
assert not os.path.exists(OLD), '이미 실행함'
os.makedirs(OLD)
D = {}
for f in ('1_3', '2_2', '2_3'):
    shutil.copy(os.path.join(SEC, f + '.json'), OLD)
    D[f] = json.load(open(os.path.join(SEC, f + '.json'), encoding='utf-8'))
A, B, C = D['1_3'], D['2_2'], D['2_3']


def at(L, i, kind, starts):
    k, v = L[i]
    assert k == kind and str(v if isinstance(v, str) else v.get('label')).startswith(starts), (i, k, str(v)[:50])


# ------------------------------------------------------------------ 옮길 조각을 먼저 떼어 둔다
at(C, 80, 'H4', '가. 선행 방식의 조사와 분류'); at(C, 106, 'TABLE', 's23_intent_class'); at(C, 107, 'H4', '나. 주요 방식 상세')
at(C, 142, 'TABLE', 's23_intent_cmp'); at(C, 143, 'H4', '다. 적용 방향'); at(C, 164, 'H3', '3.3.4')
at(C, 165, 'H4', '가. 선행 방식의 조사와 분류'); at(C, 181, 'TABLE', 's23_retr_class'); at(C, 182, 'H4', '나. 주요 방식 상세')
at(C, 183, 'BODY', '세 방식의 비교는'); at(C, 231, 'TABLE', 's23_retr_cmp'); at(C, 232, 'H4', '다. 적용 방향'); at(C, 254, 'H3', '3.3.5')
at(C, 256, 'H4', '가. 선행 사례의 KG 지식 전달 방식'); at(C, 281, 'TABLE', 's23_ctx'); at(C, 282, 'H4', '나. 근거 묶음의 구성(안)'); at(C, 301, 'H4', '다. 표준 프롬프트 프레임의 구성(안)')
intent_class = C[81:107]; intent_detail = C[108:142]; intent_cmp = C[142]
retr_class = C[166:182]; retr_detail = C[184:231]; retr_cmp = C[231]
ctx = C[257:282]
assert intent_class[0] == ['SQ', '분류 결과'] and retr_class[0] == ['SQ', '분류 결과']
intent_class[0] = ['SQ', '질의 해석 방식의 분류']; retr_class[0] = ['SQ', '근거 조회 방식의 분류']

at(B, 17, 'H3', '3.2.2 온톨로지 설계 방법 조사'); at(B, 26, 'TABLE', 's22_cmp_water'); at(B, 27, 'TABLE', 's22_cmp_other'); at(B, 29, 'CI', 'Bian(2025)')
at(B, 32, 'H5', '(1) 단계적 설계 방법'); at(B, 50, 'FIGPLACE', 's22_fig_noy'); at(B, 51, 'H5', '(2) 댐 분야의 적용 사례'); at(B, 82, 'FIGPLACE', 's22_fig_huang')
at(B, 83, 'H5', '(3) LLM을 쓴 반자동 방법'); at(B, 104, 'FIGPLACE', 's22_fig_li'); at(B, 105, 'TABLE', 's22_method3'); at(B, 106, 'H4', '라. 적용 방향')
at(B, 121, 'CI', '기존 표준 온톨로지'); at(B, 122, 'H3', '3.2.3')
bian = B[29:31]; noy = B[32:51]; dam_cases = B[52:83]; li = B[83:105]; method3 = B[105]; reuse = B[121]

# ------------------------------------------------------------------ 2장 다절(1_3): 뒤에서부터 고친다
at(A, 277, 'TABLE', 's13_ans_cmp'); at(A, 278, 'H4', '다. 주요 방법의 상세')
A[278:278] = ctx                     # 나. 분류와 비교의 끝에 KG 지식 전달 방식의 비교를 잇는다
# 6) 나. 의 앞쪽 내용에 소제목을 붙여 구분한다
at(A, 256, 'H4', '나. 분류와 비교'); at(A, 257, 'SQ', '근거의 전달 형식')

at(A, 201, 'TABLE', 's13_qa_cmp'); at(A, 202, 'H4', '다. 주요 방법의 상세'); at(A, 211, 'H5', '(3) 그래프 검색과 벡터 검색의 결합'); at(A, 222, 'H4', '라. 적용 방향')
graphaide = A[212:222]
A[202:222] = ([['H4', '다. 주요 방법의 상세']] + intent_detail
              + [['BODY', '질의 해석 주요 사례의 비교는 ⟦표:s23_intent_cmp⟧와 같다.'], intent_cmp]
              + [[k, (v.replace('(1) ', '(4) ').replace('(2) ', '(5) ').replace('(3) ', '(6) ') if k == 'H5' else v)] for k, v in retr_detail]
              + [['BODY', '근거 조회 주요 방식의 비교는 ⟦표:s23_retr_cmp⟧와 같다.'], retr_cmp]
              + [['H5', '(7) 그래프 검색과 벡터 검색의 결합: Purohit 외(2024) ⟦문헌:39_GraphAide⟧']] + graphaide)
A[202:202] = intent_class + retr_class

at(A, 31, 'H4', '나. 분류와 비교'); at(A, 34, 'H4', '다. 주요 방법의 상세'); at(A, 43, 'H5', '(3) 댐 중심 연결 구조'); at(A, 47, 'H4', '라. 적용 방향'); at(A, 24, 'CI', 'Bian(2025)')
huang = A[44:47]
A[34:47] = ([['H4', '다. 주요 방법의 상세'], ['H5', '(1) 단계적 설계 방법: Noy·McGuinness(2001) ⟦문헌:Noy2001⟧']] + noy[1:]
            + [['H5', '(2) LLM을 쓴 반자동 방법: Li 외(2025) ⟦문헌:36_FloodOntology⟧']] + li[1:]
            + [['H5', '(3) 댐 중심 연결 구조: Huang 외(2026) ⟦문헌:46_DDKG⟧']] + huang
            + [['BODY', '주요 설계 방법의 절차 비교는 ⟦표:s22_method3⟧와 같다.'], method3])
A[24:25] = bian

# ------------------------------------------------------------------ 3장 나절(2_2): 3.2.2를 선행 온톨로지의 구성 조사로
for t in (B[26], B[27]):
    t[1]['caption'] = t[1]['caption'].replace('온톨로지 설계 방법의 항목 비교', '선행 온톨로지의 구성 비교')
new322 = [
    ['H3', '3.2.2 선행 온톨로지의 구성 조사'],
    ['BODY', '2.3.2에서 댐 운영 온톨로지는 운영자의 질문에서 출발한 초기 온톨로지를 두고 구축 결과에 따라 보완하는 방법으로 설계하기로 하였다. 이 온톨로지에 담을 Class와 관계를 정하기 위하여 선행 온톨로지가 무엇을 Class와 관계로 두었는지를 조사하였다.'],
    ['H4', '가. 선행 온톨로지의 구성 비교'],
    ['BODY', '선행 온톨로지의 구성은 댐·수리시설·홍수 분야가 ⟦표:s22_cmp_water⟧, 수자원 외 분야가 ⟦표:s22_cmp_other⟧와 같다.'],
    B[26], B[27],
    ['H4', '나. 댐 분야 온톨로지의 구성'],
] + dam_cases + [
    ['H4', '다. 적용 방향'],
    ['SQ', '댐을 중심으로 한 Class 구성'],
    ['CI', '여러 출처의 자료를 댐 개체에 연결하는 댐 중심 구조를 채택'],
    ['DS', '근거: 객체 속성이 모두 댐 Class에서 출발하는 Huang 외(2026) ⟦문헌:46_DDKG⟧의 구성'],
    ['CI', '관측값과 관측 대상을 서로 다른 Class로 구분'],
    ['DS', '근거: 센서, 관측, 관측 속성을 구분한 Zhou 외(2023) ⟦문헌:47_OntoDSMS⟧, Shu 외(2025) ⟦문헌:48_댐구조안전온톨로지평가⟧의 구성'],
    ['SQ', '댐 운영을 대상으로 한 Class의 정의'],
    ['CI', '댐 분야 선행 온톨로지의 Class는 구조, 계측, 결함, 안전평가를 대상으로 함 ⟦문헌:47_OntoDSMS⟧, ⟦문헌:46_DDKG⟧, ⟦문헌:43_중력댐결함진단⟧, ⟦문헌:48_댐구조안전온톨로지평가⟧'],
    ['DS', '대상이 달라지면 온톨로지를 다시 만들어야 한다는 점이 사례에서 서술됨 ⟦문헌:43_중력댐결함진단⟧'],
    ['CI', '방류 승인, 운영 기준, 수문 상태에 해당하는 Class는 3.2.5의 댐 운영 온톨로지 설계(안)에서 새로 정의'],
    ['SQ', '후속 검토로 둔 사항'],
    reuse,
]
B[17:122] = new322
at(B, 1, 'BODY', '수집한 자료를 RAG와 LLM이'); assert '온톨로지와 메타데이터의 설계 방법을 선행연구에서 조사하고' in B[1][1]
B[1][1] = B[1][1].replace('온톨로지와 메타데이터의 설계 방법을 선행연구에서 조사하고', '선행 온톨로지의 구성, 메타데이터 항목, 자료의 처리 방식을 선행연구에서 조사하고')
n = 0
for it in B:
    if isinstance(it[1], str):
        for a, b in (('조사 내용은 온톨로지 설계 방법, 메타데이터 항목', '조사 내용은 선행 온톨로지의 구성, 메타데이터 항목'),
                     ('3.2.2의 적용 방향에 따라 댐 운영 온톨로지(안)를', '2.3.2와 3.2.2의 적용 방향에 따라 댐 운영 온톨로지(안)를'),
                     ('댐 분야의 온톨로지 구축 사례는 전문가가 단계 절차에 따라 Class와 관계를 정의하는 방식을 씀', '댐 분야의 선행 온톨로지는 구조, 계측, 결함, 안전평가를 대상으로 하여, 댐 운영을 대상으로 한 Class는 새로 정의하여야 함')):
            if a in it[1]: it[1] = it[1].replace(a, b); n += 1
assert n == 3, n

# ------------------------------------------------------------------ 3장 다절(2_3): 조사를 빼고 단계 구성만 (뒤에서부터)
C[301][1] = '나. 표준 프롬프트 프레임의 구성(안)'; C[282][1] = '가. 근거 묶음의 구성(안)'
del C[256:282]
at(C, 233, 'BODY', 'KG는 의도별로'); C[233][1] = '2.3.5의 적용 방향에 따라 ' + C[233][1]
del C[165:233]
at(C, 144, 'BODY', '해석 결과는 의도'); C[144][1] = '2.3.5의 적용 방향에 따라 질의 ' + C[144][1]
del C[80:144]

# 옮긴 뒤 맞지 않게 된 절 참조
fix = 0
for L in (A, B, C):
    for it in L:
        if isinstance(it[1], str):
            for a, b in (('구성과 결과의 상세는 2.3.4와 3.3.3 참조', '구성과 결과의 상세는 2.3.4와 2.3.5 참조'), ('구성과 결과의 상세는 3.3.3 참조', '구성과 결과의 상세는 2.3.5 참조'), ('구성과 결과의 상세는 3.3.4 참조', '구성과 결과의 상세는 2.3.5 참조')):
                if a in it[1]: it[1] = it[1].replace(a, b); fix += 1
print('절 참조 고침', fix)
for f, items in D.items():
    json.dump(items, open(os.path.join(SEC, f + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f, len(items), '항목,', sum(len(v) if isinstance(v, str) else sum(len(str(c)) for r in v.get('rows', []) for c in r) for k, v in items), '자')
