#!/usr/bin/env python3
"""2장의 흐름을 맞춘다(한 번만 실행, 이전 내용은 sections/_old7). 부록은 쓰지 않는다.
- 장 전체: 사례 조사(왜 이 접근인가) → 국내 운영 여건(조건) → 적용 기술요소(선정과 제안).
- 적용 기술요소 절(1_3): 기술요소의 도출 → 요소 기술별 검토(비교표 → 추린 방식의 상세 → 판단과 적용 기술(안)) → 아키텍처(안) → 종합 → 소결.
  부록으로 뺐던 방식별 상세를 요소 기술마다 2~3개씩 되돌린다. 판단 문단에는 국내 운영 여건의 조건을 이유로 적는다.
- 사례 조사 절: 뒤 절이 인용하는데 사례 목록에 없던 문헌을 '일반 방법·타 분야'로 목록에 넣는다.
사용: python3 dam_pilot_data/scripts/apply_select_1124.py
"""
import json, os, re, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
SEC = os.path.join(HERE, '..', '..', 'project_khnp', 'final_report', 'sections')
OLD = os.path.join(SEC, '_old7')
assert not os.path.exists(OLD), '이미 실행함'
os.makedirs(OLD)
D = {}
for f in ('1_1_2', '1_1_4', '1_3', '2_2', '2_3', 'A_1'):
    shutil.copy(os.path.join(SEC, f + '.json'), OLD)
    D[f] = json.load(open(os.path.join(SEC, f + '.json'), encoding='utf-8'))
T, A = D['1_3'], D['A_1']
P5 = json.load(open(os.path.join(SEC, '_old5', '1_3.json'), encoding='utf-8'))      # 온톨로지 설계의 요약된 상세(3.2.2를 가리키는 판)
for i in (2, 5, 19, 23, 33, 43, 91, 105, 108, 126, 144, 147, 174, 213, 216, 227):
    assert A[i][0] == 'H5', i
assert A[124][0] == 'BODY' and A[125][0] == 'TABLE' and A[172][0] == 'BODY' and A[173][0] == 'TABLE' and A[186][0] == 'H4' and A[212][0] == 'H4' and A[22][0] == 'H4' and A[46][0] == 'H3'
assert P5[35][0] == 'H5' and P5[35][1].startswith('(1) 단계적 설계 방법론') and P5[47] == ['H4', '라. 적용 방향']

METHODS = {
    'onto': P5[35:47],
    'struct': A[2:22],
    'link': A[23:46],
    'qa': A[91:105] + A[108:124] + A[126:144],          # 가중 투표, 온톨로지로 제약한 intent 추출, 의도·유형별 질의 규칙
    'ans': A[213:230],
}
EXTRA = {'qa': A[124:126] + A[172:174], 'ans': A[187:212]}     # 비교에 잇는 표: 주요 사례 비교, KG 지식 전달 방식
JUDGE = {
    'onto': '세 방식을 비교하면, 전문가가 단계 절차에 따라 Class와 관계를 정의하는 방식은 댐 분야 사례가 공통으로 따른 절차이고, LLM으로 온톨로지를 넓히는 방식은 후보의 일부가 기각되어 전문가 검토를 함께 두었다. 한수원 내부 자료의 구성이 확정되지 않았고 자동으로 생성한 결과를 점검할 기준도 마련되지 않았으므로, 운영자의 질문에서 출발한 초기 온톨로지를 전문가가 정하고 구축 결과에 따라 보완하는 방식이 적절하다.',
    'struct': '모델 학습이나 LLM에 의한 추출은 주석 자료나 정확도를 검증할 기준이 있어야 하며, 착수보고회에서도 학습에 쓸 자료의 적절성을 먼저 평가하는 단계가 필요하다는 의견이 제시되었다(2.2.2). 따라서 정형 자료의 대응과 구조가 일정한 문서의 규칙 기반 추출을 적용 기술(안)으로 하고, LLM 기반 추출은 검증 기준이 마련된 뒤의 후속 검토 사항으로 두는 것이 적절하다.',
    'link': '댐 운영에 쓰이는 수문·기상 수치는 제공기관의 시스템에서 10분, 시간, 일 단위로 제공되므로(2.2.3), KG에 복제하면 원본과의 차이를 따로 관리하여야 한다. 따라서 수치는 원본 저장소에 두고 KG에는 식별 키만 두는 방식이 적절하다.',
    'qa': '세 방식을 비교하면, 의도 범주를 정해 두고 범주별 질의 규칙으로 조회하는 방식은 수리·하천 분야 사례에서 쓰였고 같은 질의에 같은 조회 결과를 얻을 수 있다. LLM이 질의문을 직접 쓰는 방식은 실행되지 않는 질의문과 정의되지 않은 관계의 생성이 보고되었다. 운영 질의는 근거를 찾지 못하면 답하지 않아야 하고(2.1.2) 응답의 근거를 함께 제시하여야 하므로(2.2.2), 조회 결과를 재현할 수 있는 의도 범주와 질의 규칙 방식이 적절하다.',
    'ans': '착수보고회에서 예측값만 제공하는 구조가 아니라 판단 근거를 함께 제시하는 구조가 필요한 것으로 확인되었다(2.2.2). 따라서 검색한 결과를 출처 번호가 붙은 근거로 구성하여 전달하고, 응답에서 사용한 근거를 표기하는 방식이 적절하다.',
}


def h3(L, title):
    i = [k for k, x in enumerate(L) if x[0] == 'H3' and x[1].split(' ', 1)[1].startswith(title)][0]
    j = [k for k in range(i + 1, len(L) + 1) if k == len(L) or L[k][0] == 'H3'][0]
    return L[i + 1:j]


def renum(items, start):
    out, n = [], start
    for k, v in items:
        if k == 'H5':
            v = re.sub(r'^\(\d+\) ', '(%d) ' % n, v); n += 1
        out.append([k, v])
    return out, n


sec1 = h3(T, '기술요소의 도출'); elems = h3(T, '기술요소별 적용 기술(안)'); arch = h3(T, 'RAG-sLLM 아키텍처(안)'); summ = h3(T, '적용 기술 종합'); concl = h3(T, '소결')
idx = [k for k, x in enumerate(elems) if x[0] == 'H4'] + [len(elems)]
assert len(idx) == 6
new_elems = []
for key, a, b in zip(('onto', 'struct', 'link', 'qa', 'ans'), idx, idx[1:]):
    blk = elems[a + 1:b]
    sp = [k for k, x in enumerate(blk) if x[0] == 'SQ' and (x[1].startswith('적용 기술(안)') or x[1].startswith('적용 방향('))][0]
    reason = ''
    if blk[sp - 1][0] == 'BODY' and sp - 1 > 0:
        reason = blk[sp - 1][1] + ' '; cmp_part = blk[1:sp - 1]
    else:
        cmp_part = blk[1:sp]
    cmp_part = [x for x in cmp_part if x != ['SQ', '검토한 방식'] and not (x[0] == 'DS' and ('부록' in x[1] or '3.2.2에서 조사' in x[1]))]
    cmp_part = [['BODY', x[1].replace('와 같음', '와 같다.')] if x[0] == 'CI' and x[1].startswith('선행 문헌이 쓴 방식과 본 과업의 활용은') else x for x in cmp_part]
    methods, n = renum(METHODS[key], 2)
    new_elems += ([elems[a], blk[0], ['H5', '(1) 검토한 방식의 비교']] + cmp_part + EXTRA.get(key, []) + methods
                  + [['H5', '(%d) 판단과 적용 기술(안)' % n], ['BODY', reason + JUDGE[key]]] + blk[sp:])
for it in new_elems:
    if it[0] == 'BODY' and it[1].startswith('아키텍처(안)의 계층을 이루는 다섯 기술요소마다'):
        it[1] = '도출한 다섯 기술요소마다 선행 문헌이 쓴 방식을 비교하고, 그 가운데 댐 운영 자료와 가까운 방식을 추려 자세히 검토한 뒤 국내 운영 여건에 비추어 적용 기술(안)을 선정하였다.'
assert arch[0][0] == 'BODY'
arch[0][1] = arch[0][1].replace('도출한 다섯 기술요소를 묶어 RAG-sLLM 아키텍처(안)를', '선정한 적용 기술(안)을 묶어 RAG-sLLM 아키텍처(안)를')
D['1_3'] = ([['H3', '2.3.1 기술요소의 도출']] + sec1 + [['H3', '2.3.2 기술요소별 검토와 적용 기술(안)']] + new_elems
            + [['H3', '2.3.3 RAG-sLLM 아키텍처(안)']] + arch + [['H3', '2.3.4 적용 기술 종합']] + summ + [['H3', '2.3.5 소결']] + concl)
n = 0
for f in ('2_2', '2_3'):
    for it in D[f]:
        if isinstance(it[1], str):
            for a, b in (('2.3.3과 3.2.2의 적용 방향에 따라', '2.3.2와 3.2.2의 적용 방향에 따라'), ('2.3.3의 적용 기술(안)에 따라', '2.3.2의 적용 기술(안)에 따라')):
                if a in it[1]: it[1] = it[1].replace(a, b); n += 1
assert n == 3, n
del D['A_1']
os.remove(os.path.join(SEC, 'A_1.json'))

# ------------------------------------------------------------------ 사례 목록: 뒤 절이 인용하는 문헌 가운데 목록에 없는 것을 넣는다
ROWS = {'Lewis2020': ('RAG', 'Lewis 외(2020)', '지식 집약 과제의 검색 결합 생성(일반 방법)'),
        'arxiv_2306.04136': ('지식 보강 프롬프트 KGQA', 'Baek 외(2023)', '일반 KG 질의응답'),
        'arxiv_2309.11206': ('Retrieve-Rewrite-Answer', 'Wu 외(2023)', '일반 KG 질의응답'),
        'arxiv_2311.09841': ('학술 KG 질의응답', 'Taffa·Usbeck(2023)', '학술 지식그래프 질의응답'),
        'arxiv_2402.16568': ('시간 KG 2단계 생성 질의응답', 'Gao 외(2024)', '시간 지식그래프 질의응답'),
        'arxiv_2405.12035': ('KG-RAG', 'Sanmartín(2024)', 'LLM 에이전트의 지식 보강'),
        'arxiv_2406.10710': ('SyntheT2C', 'Zhong 외(2024)', '그래프 질의 생성의 학습 자료(의료 KG)'),
        'arxiv_2412.10064': ('Text2Cypher', 'Ozsoy 외(2024)', '자연어 질문의 그래프 질의 생성'),
        'arxiv_2502.11491': ('온톨로지 기반 역방향 추론', 'Liu 외(2025)', '일반 KG 질의응답'),
        'arxiv_2505.05118': ('Text2Cypher 스키마 필터링', 'Ozsoy(2025)', '자연어 질문의 그래프 질의 생성'),
        'arxiv_2506.21445': ('다국어 Text2Cypher', 'Ozsoy·Tai(2025)', '자연어 질문의 그래프 질의 생성(다국어)'),
        'arxiv_2507.04127': ('BYOKG-RAG', 'Mavromatis 외(2025)', '임의의 KG에 대한 질의응답'),
        'arxiv_2611.15904': ('HeriKGQA', 'Kong 외(2026)', '문화유산 센서 모니터링 자료의 KG 질의응답')}
KROWS = {'Noy2001': ('Ontology Development 101', 'Noy·McGuinness(2001)', '온톨로지 설계 방법론(일반 방법)'),
         'Angles2008': ('그래프 데이터베이스 모델 조사', 'Angles·Gutierrez(2008)', '그래프 데이터베이스(일반 방법)')}
cited = set()
for f in ('1_3', '2_2', '2_3'):
    cited |= set(re.findall(r'⟦문헌:([^⟧]+)⟧', json.dumps(D[f], ensure_ascii=False)))
listed = set()
for f in ('1_1_1', '1_1_2', '1_1_3', '1_1_4', '1_1_5'):
    L = D.get(f) or json.load(open(os.path.join(SEC, f + '.json'), encoding='utf-8'))
    for k, v in L:
        if k == 'TABLE' and 'list' in v['label']:
            listed |= set(re.findall(r'⟦문헌:([^⟧]+)⟧', json.dumps(v, ensure_ascii=False)))
miss = sorted(cited - listed)
assert set(miss) <= set(ROWS) | set(KROWS), set(miss) - set(ROWS) - set(KROWS)
R, K = D['1_1_2'], D['1_1_4']
t = [x for x in R if x[0] == 'TABLE' and x[1]['label'] == 'rag_list'][0][1]
assert t['rows'][-1][1] == '21'
add = [k for k in ROWS if k in miss]
t['rows'] += [['KG 질의응답의 일반 방법·타 분야 사례', str(22 + i), ROWS[k][0], '%s ⟦문헌:%s⟧' % (ROWS[k][1], k), ROWS[k][2]] for i, k in enumerate(add)]
t = [x for x in K if x[0] == 'TABLE' and x[1]['label'] == 'kg_list_other'][0][1]
assert t['rows'][-1][0] == '24'
kadd = [k for k in KROWS if k in miss]
t['rows'] += [[str(25 + i), KROWS[k][0], '%s ⟦문헌:%s⟧' % (KROWS[k][1], k), KROWS[k][2]] for i, k in enumerate(kadd)]
i = [k for k, x in enumerate(R) if x[0] == 'BODY' and x[1].startswith('수자원 분야 사례와 국내 타 분야 사례는 ⟦표:rag_list⟧')][0]
R[i][1] = ('수자원 분야 사례, 국내 타 분야 사례, KG 질의응답의 일반 방법과 타 분야 사례는 ⟦표:rag_list⟧와 같다. 수자원 분야와 국내 타 분야 사례(1~21번)의 자료, 구조, 지식 구조, 검색 방식은 ⟦표:rag_cmp1⟧, '
           '생성 모델, 미세조정, 운영 환경, 평가 방법, 대표 결과는 ⟦표:rag_cmp2⟧와 같다. 22번부터의 문헌은 2.3절에서 적용 기술요소를 검토할 때 방식별로 다시 다룬다.')
print('사례 목록에 넣은 문헌:', add + kadd)
for f, items in D.items():
    json.dump(items, open(os.path.join(SEC, f + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f, len(items), '항목,', sum(len(v) if isinstance(v, str) else sum(len(str(c)) for r in v.get('rows', []) for c in r) for k, v in items), '자')
