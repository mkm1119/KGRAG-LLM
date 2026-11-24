#!/usr/bin/env python3
"""2장 다절(적용 기술요소 및 모델 제안)을 제안 중심으로 다시 구성한다(한 번만 실행, 이전 내용은 sections/_old6).
- 조사가 목적인 절(2장 가절, 3장 가절·나절)은 조사 → 비교 → 분석 → 적용의 흐름을 그대로 둔다.
- 제안이 목적인 2장 다절은 기술요소의 도출 → 아키텍처(안) → 기술요소별 적용 기술(안)(검토한 방식의 표, 선택과 이유) → 종합의 순서로 둔다.
- 기술요소마다 두었던 '선행 기술 조사'와 '주요 방법의 상세'는 본문에서 빼고, 온톨로지 설계 방법은 조사 절인 3장 나절 2)로, 나머지는 부록(A_1.json)으로 옮긴다.
사용: python3 dam_pilot_data/scripts/apply_proposal_1124.py
"""
import json, os, re, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
SEC = os.path.join(HERE, '..', '..', 'project_khnp', 'final_report', 'sections')
OLD = os.path.join(SEC, '_old6')
assert not os.path.exists(OLD), '이미 실행함'
os.makedirs(OLD)
D = {}
for f in ('1_3', '2_2', '2_3'):
    shutil.copy(os.path.join(SEC, f + '.json'), OLD)
    D[f] = json.load(open(os.path.join(SEC, f + '.json'), encoding='utf-8'))
A, B, C = D['1_3'], D['2_2'], D['2_3']


def h3_block(L, title):
    """제목이 title로 시작하는 소절(H3)의 내용(제목 제외)."""
    i = [k for k, x in enumerate(L) if x[0] == 'H3' and x[1].split(' ', 1)[1].startswith(title)][0]
    j = [k for k in range(i + 1, len(L) + 1) if k == len(L) or L[k][0] == 'H3'][0]
    return L[i + 1:j]


def h4_block(blk, letter):
    """소절 안에서 '가.' 등으로 시작하는 묶음(H4)의 내용(제목 제외)."""
    i = [k for k, x in enumerate(blk) if x[0] == 'H4' and x[1].startswith(letter + '.')][0]
    j = [k for k in range(i + 1, len(blk) + 1) if k == len(blk) or blk[k][0] == 'H4'][0]
    return blk[i + 1:j]


def pre_h4(blk):
    i = [k for k, x in enumerate(blk) if x[0] == 'H4'][0]
    return blk[:i]


def drop_ref(items):
    return [x for x in items if not (x[0] == 'DS' and re.match(r'구성과 결과의 상세는 .* 참조$', x[1]))]


def upto_table(items):
    """묶음의 처음부터 첫 표까지(표를 가리키는 문장과 표)와 그 뒤."""
    i = [k for k, x in enumerate(items) if x[0] == 'TABLE'][0]
    return items[:i + 1], items[i + 1:]


P = {n: h3_block(A, t) for n, t in (('onto', '온톨로지 설계'), ('struct', '자료 구조화·매핑'), ('link', '수치자료 연계·저장'), ('qa', '질의 해석·검색'), ('ans', '근거 구성·응답'))}
intro0 = h3_block(A, '검토 방법'); arch = h3_block(A, 'RAG-sLLM 아키텍처(안)'); summ = h3_block(A, '적용 기술 종합'); concl = h3_block(A, '소결')

# ------------------------------------------------------------------ 부록으로 옮길 내용
qa_na = h4_block(P['qa'], '나'); ans_na = h4_block(P['ans'], '나')
i1 = [k for k, x in enumerate(qa_na) if x == ['SQ', '질의 해석 방식의 분류']][0]
qa_evidence, qa_class = qa_na[:i1], qa_na[i1:]                       # 앞: 기술 비교표와 보고된 결과, 뒤: 방식의 분류(3장 다절에서 옮겨 온 것)
i2 = [k for k, x in enumerate(ans_na) if x[0] == 'BODY' and x[1].startswith('KG에서 얻은 지식을 LLM의 입력으로')][0]
ans_evidence, ans_ctx = ans_na[:i2], ans_na[i2:]
APP = ([['H3', '부록 1. 자료 구조화와 수치자료 연계 방법의 상세'], ['H4', '가. 자료 구조화·매핑']] + drop_ref(h4_block(P['struct'], '다'))
       + [['H4', '나. 수치자료 연계·저장']] + drop_ref(h4_block(P['link'], '다'))
       + [['H3', '부록 2. 질의 해석과 근거 조회 방식의 상세'], ['H4', '가. 방식의 분류']] + qa_class
       + [['H4', '나. 주요 방식']] + drop_ref(h4_block(P['qa'], '다'))
       + [['H3', '부록 3. 근거 구성과 응답 방식의 상세'], ['H4', '가. KG 지식을 프롬프트에 넣는 방식']] + ans_ctx
       + [['H4', '나. 주요 방식']] + drop_ref(h4_block(P['ans'], '다')))

# ------------------------------------------------------------------ 온톨로지 설계 방법은 조사 절인 3.2.2로
onto_ga = h4_block(P['onto'], '가'); onto_da = h4_block(P['onto'], '다')
k3 = [k for k, x in enumerate(onto_da) if x[0] == 'H5' and x[1].startswith('(3)')][0]
k4 = [k for k, x in enumerate(onto_da) if x[0] == 'BODY' and '⟦표:s22_method3⟧' in x[1]][0]
method_detail = onto_da[:k3] + onto_da[k4:]                           # (1) 단계적 설계, (2) 반자동 방법, 절차 비교표. (3) 댐 중심 구조는 3.2.2의 구성 조사에 있다
b322 = h3_block(B, '선행 온톨로지의 구성 조사')
old_dir = h4_block(b322, '다')
new322 = ([['BODY', '댐 운영 온톨로지의 설계 절차와 Class 구성을 정하기 위하여 온톨로지를 설계하는 방법과 선행 온톨로지가 둔 Class·관계를 조사하였다.'],
           ['H4', '가. 온톨로지 설계 방법']] + onto_ga + method_detail
          + [['H4', '나. 선행 온톨로지의 구성 비교']] + h4_block(b322, '가')
          + [['H4', '다. 댐 분야 온톨로지의 구성']] + h4_block(b322, '나')
          + [['H4', '라. 적용 방향'],
             ['SQ', '설계 절차'],
             ['CI', '운영자의 질문과 범위를 먼저 정하고 필요한 Class, 관계, 속성을 단계적으로 정의'],
             ['DS', '근거: Noy·McGuinness(2001) ⟦문헌:Noy2001⟧의 7단계 절차와 이를 따른 댐 분야 사례 ⟦문헌:47_OntoDSMS⟧, ⟦문헌:46_DDKG⟧'],
             ['CI', '자동으로 생성된 Class, 관계, 분류는 전문가 검토를 거쳐 반영'],
             ['DS', '근거: 후보의 약 8~10%가 기각된 Li 외(2025) ⟦문헌:36_FloodOntology⟧의 정제 결과']] + old_dir)
i = [k for k, x in enumerate(B) if x[0] == 'H3' and '선행 온톨로지의 구성 조사' in x[1]][0]
j = [k for k in range(i + 1, len(B)) if B[k][0] == 'H3'][0]
B[i:j] = [['H3', '3.2.2 온톨로지 설계 방법과 선행 온톨로지의 구성 조사']] + new322
n = 0
for it in B:
    if isinstance(it[1], str):
        for a, b in (('선행 온톨로지의 구성, 메타데이터 항목, 자료의 처리 방식을 선행연구에서 조사하고', '온톨로지 설계 방법과 선행 온톨로지의 구성, 메타데이터 항목, 자료의 처리 방식을 선행연구에서 조사하고'),
                     ('조사 내용은 선행 온톨로지의 구성, 메타데이터 항목', '조사 내용은 온톨로지 설계 방법과 선행 온톨로지의 구성, 메타데이터 항목'),
                     ('2.3.2와 3.2.2의 적용 방향에 따라', '2.3.3과 3.2.2의 적용 방향에 따라')):
            if a in it[1]: it[1] = it[1].replace(a, b); n += 1
assert n == 3, n
for it in C:
    if isinstance(it[1], str) and it[1].startswith('2.3.5의 적용 방향에 따라'):
        it[1] = it[1].replace('2.3.5의 적용 방향에 따라', '2.3.3의 적용 기술(안)에 따라'); n += 1
assert n == 5, n


# ------------------------------------------------------------------ 2장 다절: 제안 중심 구성
def element(key, note):
    """기술요소 하나: 설명, 검토한 방식(비교표), 선택의 근거가 되는 보고 결과, 적용 기술(안)."""
    blk = P[key]
    na = {'qa': qa_evidence, 'ans': ans_evidence}.get(key, h4_block(blk, '나'))
    tbl = [x for x in na if x[0] == 'TABLE'][0]
    rest = [x for x in na if x is not tbl and not (x[0] == 'BODY' and '⟦표:%s⟧' % tbl[1]['label'] in x[1])]
    return (pre_h4(blk) + [['SQ', '검토한 방식'], ['CI', '선행 문헌이 쓴 방식과 본 과업의 활용은 ⟦표:%s⟧와 같음' % tbl[1]['label']], ['DS', note], tbl]
            + rest + h4_block(blk, '라'))


assert intro0[0][0] == 'BODY' and intro0[0][1].startswith('2.1절의 사례 조사에서는')
k = [i for i, x in enumerate(intro0) if x == ['SQ', '검토 대상']][0]
t = [i for i, x in enumerate(intro0) if x[0] == 'TABLE'][0]
derive = ['TABLE', {'label': 's13_derive', 'caption': '조사 결과에서 도출한 기술요소', 'widths': [50, 24, 26], 'align': ['l', 'l', 'l'], 'rows': [
    ['조사에서 확인된 사항', '해당 절', '기술요소'],
    ['운영 기준과 시설·상태의 관계를 다루는 운영지식의 구조화가 필요하며, 기존 댐 분야 온톨로지는 결함 진단과 안전 평가를 대상으로 함', '2.1.4', '① 온톨로지 설계'],
    ['운영에 쓰이는 자료가 수문·기상·방류 승인 기록의 정형 자료와 운영 규정의 문서 자료로 나뉘고, 제공기관마다 시설 코드와 표기 형식이 다름', '2.2.3, 2.2.5', '② 자료 구조화·매핑'],
    ['수위·방류량 등 시계열 자료는 KG에 복제하지 않고 측정자료 저장소에 둔 채 연결하는 구성이 사례에서 쓰임', '2.1.4', '③ 수치자료 연계·저장'],
    ['조건이 빠진 질의를 보완하고 근거를 찾지 못한 질의에는 답하지 않는 절차가 필요하며, 전문가가 아닌 사용자도 이용할 수 있어야 함', '2.1.2, 2.2.2', '④ 질의 해석·검색'],
    ['예측값만이 아니라 판단 근거를 함께 제시하는 구조가 필요하며, 응답은 근거와 함께 제시하고 최종 판단은 운영자가 함', '2.1.2, 2.2.2', '⑤ 근거 구성·응답']]}]
sec1 = ([['H3', '2.3.1 기술요소의 도출'], ['BODY', intro0[0][1].replace(' 파트의 구성은 ⟦표:s13_parts⟧와 같다.', ' 조사 결과에서 도출한 기술요소는 ⟦표:s13_derive⟧와 같다.')], derive]
        + intro0[1:k] + [['CI', '파트별로 다루는 내용과 과업 내용의 요소는 ⟦표:s13_parts⟧와 같음'], intro0[t]])
assert arch[0][0] == 'BODY' and arch[0][1].startswith('파트별 검토 결과를 바탕으로')
arch[0][1] = arch[0][1].replace('파트별 검토 결과를 바탕으로 RAG-sLLM 아키텍처(안)를', '도출한 다섯 기술요소를 묶어 RAG-sLLM 아키텍처(안)를')
sec3 = [['H3', '2.3.3 기술요소별 적용 기술(안)'],
        ['BODY', '아키텍처(안)의 계층을 이루는 다섯 기술요소마다 선행 문헌이 쓴 방식을 검토하고, 댐 운영 자료와 운영 여건에 맞는 적용 기술(안)을 선택하였다.'],
        ['H4', '가. 온톨로지 설계']] + element('onto', '설계 방법의 절차와 선행 온톨로지의 구성은 3.2.2에서 조사') \
    + [['H4', '나. 자료 구조화·매핑']] + element('struct', '방식별 절차와 보고된 결과는 부록 1에 수록') \
    + [['H4', '다. 수치자료 연계·저장']] + element('link', '방식별 절차와 보고된 결과는 부록 1에 수록') \
    + [['H4', '라. 질의 해석·검색']] + element('qa', '방식의 분류와 방식별 절차, 보고된 결과는 부록 2에 수록') \
    + [['H4', '마. 근거 구성·응답']] + element('ans', '방식별 절차와 보고된 결과는 부록 3에 수록')
for it in concl:
    if isinstance(it[1], str) and it[1].startswith('파트별 선행 기술 비교표와 주요 방법의 상세 분석'):
        it[1] = '조사 결과에서 도출한 다섯 기술요소(⟦표:s13_derive⟧)와 기술요소별로 검토한 방식의 비교표'
newA = sec1 + [['H3', '2.3.2 RAG-sLLM 아키텍처(안)']] + arch + sec3 + [['H3', '2.3.4 적용 기술 종합']] + summ + [['H3', '2.3.5 소결']] + concl
D['1_3'] = newA
D['A_1'] = APP
for f, items in D.items():
    json.dump(items, open(os.path.join(SEC, f + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f, len(items), '항목,', sum(len(v) if isinstance(v, str) else sum(len(str(c)) for r in v.get('rows', []) for c in r) for k, v in items), '자')
