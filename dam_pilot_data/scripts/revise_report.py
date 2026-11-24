#!/usr/bin/env python3
"""최종보고서 1·2장 정리(2차). sections/_old2 의 판에서 출발하여 다음을 한다.
1) 1.2절: 지시되지 않은 법령·조문 정리를 빼고 착수보고회 → 자료 활용 → 현장방문 → 적용 고려사항의 순서로 둔다.
2) 1.3·2.2·2.3절: 문헌 편수 집계와 분류 편수표, 논문 안의 불일치를 적은 문장을 뺀다.
3) 같은 논문의 상세 설명이 여러 절에 되풀이되는 곳은 한 곳에만 두고 나머지는 요지와 참조로 줄인다.
4) 선행 사례를 나열한 세부 줄(-)의 수를 꼭지마다 제한하여 분량을 줄인다.
5) 1.1절의 주요 개념과 종합 시사점은 공정보고(8월)의 서술을 기본으로 되돌린다.
6) 절마다 '조사 → 비교 → 상세 → 산출 → 다음 절'의 흐름을 적은 줄을 넣는다.
사용: python3 dam_pilot_data/scripts/revise_report.py
"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
SEC = os.path.join(HERE, '..', '..', 'project_khnp', 'final_report', 'sections')
load = lambda n: json.load(open(os.path.join(SEC, '_old2', n + '.json'), encoding='utf-8'))
COUNT = re.compile(r'(?<![0-9,])[0-9]{1,2}편')
NOTE = re.compile(r'서로 맞지 않|표와 다름|본문 수치와 다름|서로 다름$|논문 안에서|그림에만 (있어|제시)|글에는 제시되지 않|확인되지 않음$|제시되지 않음$|조사 범위에서 .*확인되지 않')


def prune(items, pat):
    """pat에 걸리는 ◦(와 그 아래 -), -, 본문을 뺀다. 내용이 없어진 □ 도 뺀다."""
    out, skip = [], False
    for k, v in items:
        if k == 'CI':
            skip = bool(pat.search(v))
            if not skip: out.append([k, v])
        elif k == 'DS':
            if not skip and not pat.search(v): out.append([k, v])
        elif k == 'BODY':
            skip = False
            if not pat.search(v): out.append([k, v])
        else:
            skip = False; out.append([k, v])
    res = []
    for i, (k, v) in enumerate(out):
        if k == 'SQ' and (i + 1 == len(out) or out[i + 1][0] in ('SQ', 'H3', 'H4', 'H5', 'TABLE', 'FIGPLACE', 'BODY')): continue
        res.append([k, v])
    return res


def drop_tables(items, test):
    return [[k, v] for k, v in items if not (k == 'TABLE' and test(v))]


def cap_ds(items, n, where):
    """where(h3, h4)가 참인 구간에서 ◦ 하나에 딸린 - 를 n개까지만 둔다."""
    out, h3, h4, c = [], '', '', 0
    for k, v in items:
        if k == 'H3': h3, h4 = v, ''
        elif k == 'H4': h4 = v
        if k == 'CI': c = 0
        if k == 'DS' and where(h3, h4):
            c += 1
            if c > n: continue
        out.append([k, v])
    return out


def shorten_h5(items, keys, ref):
    """제목에 keys의 낱말이 든 H5 구간(논문 한 편의 상세 설명)을 요지 두 줄과 참조로 줄인다."""
    out, i = [], 0
    while i < len(items):
        k, v = items[i]
        if k == 'H5' and any(x in v for x in keys):
            out.append([k, v]); j = i + 1; ci = 0
            while j < len(items) and items[j][0] not in ('H5', 'H4', 'H3'):
                kk, vv = items[j]
                if kk == 'CI' and ci < 2 and not NOTE.search(vv):
                    out.append([kk, vv]); ci += 1
                j += 1
            out.append(['DS', '구성과 결과의 상세는 %s 참조' % [r for x, r in ref.items() if x in v][0]])
            i = j; continue
        out.append([k, v]); i += 1
    return out


def drop_section(items, level, starts):
    """제목이 starts로 시작하는 H3(또는 H4) 구간을 통째로 뺀다."""
    out, skip = [], False
    order = {'H3': 3, 'H4': 4, 'H5': 5}
    for k, v in items:
        if k in order and order[k] <= order[level]:
            skip = (k == level and v.startswith(starts))
        if not skip: out.append([k, v])
    return out


def drop_sq(items, starts):
    out, skip = [], False
    for k, v in items:
        if k in ('SQ', 'H3', 'H4', 'H5'): skip = (k == 'SQ' and v.startswith(starts))
        if not skip: out.append([k, v])
    return out


def L(text):
    """'□ ', '◦ ', '- ', 'B ' 로 시작하는 줄을 항목으로 바꾼다."""
    m = {'□': 'SQ', '◦': 'CI', '-': 'DS', 'B': 'BODY', '#4': 'H4', '#3': 'H3'}
    return [[m[t.split(' ', 1)[0]], t.split(' ', 1)[1]] for t in (x.strip() for x in text.strip().split('\n')) if t]


def insert_after_h3(items, h3starts, new):
    out, i = [], 0
    while i < len(items):
        k, v = items[i]; out.append([k, v])
        if k == 'H3' and v.startswith(h3starts):
            if i + 1 < len(items) and items[i + 1][0] == 'BODY':      # 흐름 줄은 절 첫 본문 뒤에 둔다
                out.append(items[i + 1]); i += 1
            out += new
        i += 1
    return out


def replace_h4(items, h4starts, new, h3starts=None):
    out, skip, h3 = [], False, ''
    for k, v in items:
        if k == 'H3': h3 = v; skip = False
        if k == 'H4':
            skip = v.startswith(h4starts) and (h3starts is None or h3.startswith(h3starts))
            if skip: out += new
        if not skip: out.append([k, v])
    return out


OUT = {}
# ============================================================ 1.1.1 : 주요 개념은 공정보고(8월)의 서술을 기본으로
s = load('1_1_1')
s = replace_h4(s, '나. 주요 개념', L('''
#4 나. 주요 개념
□ RAG(검색증강생성)
◦ LLM이 답변을 생성하기 전에 외부 지식베이스에서 관련 정보를 검색해 답변의 사실 정확성과 관련성을 높이는 과정 ⟦문헌:Lewis2020⟧
- 질의 임베딩, 유사도 기반 검색, 재순위화(reranking), LLM 생성의 단계로 구성 ⟦문헌:05_IWMS-LLM⟧
- 지식베이스 구축 시점을 기준으로 사전 적재형(batch-ingested)과 실시간 API 호출형(Tool-calling)으로 구분
□ LLM / 도메인 특화 LLM
◦ 특정 과학 분야의 전문 어휘·개념·추론 과제를 다루도록 학습되거나 미세조정된 대규모 신경망 언어모델 ⟦문헌:18_HydroLLM⟧
- 모델 용량과 데이터 규모의 정합이 성능에 중요하며, 1.5B~32B 규모 비교 실험에서 8B급 모델이 가장 안정적인 성능을 보인 사례가 확인
□ 온톨로지·KG
◦ 온톨로지는 도메인의 형식적 어휘·스키마를 규정해 개념과 관계를 정의한 것이고, 지식그래프(KG)는 이 스키마를 실제 데이터로 채워 구체화한 것 ⟦문헌:36_FloodOntology⟧
- 온톨로지는 "설계도", KG는 "채워진 그래프"에 해당
□ 온프레미스
◦ 클라우드·온프레미스·하이브리드 3가지 배포 방식 중 하나로, 완전한 통제와 컴플라이언스 준수가 가능하지만 상당한 초기 투자가 필요한 배포 방식 ⟦문헌:51_온프레미스LLM비용분석⟧
- 헬스케어·금융·법률 등 민감한 도메인에서 주로 채택
'''))
# 세 유형은 과업 내용에서 주어진 구분이므로 그대로 밝히고, 개념 정의·유형 비교와 겹치는 '세 유형의 개요'는 뺀다
s = drop_section(s, 'H4', '다. 세 유형의 개요')
for it in s:
    if it[0] == 'BODY' and it[1].startswith('수자원 관리 분야에서 대규모 언어모델'):
        it[1] = '과업 내용에 따라 수자원 관리 분야의 대규모 언어모델(LLM) 적용 사례를 검색 증강 생성(RAG) 기반 질의응답, 도메인 특화 LLM, 운영지식 구조화(온톨로지·지식그래프)의 세 축으로 조사하였다. 본 절은 축별 국내외 사례와 사례 간 비교, 댐 운영 의사결정 지원에 대한 시사점을 제시한다.'
s += L('''
#4 다. 보고서 1·2장의 흐름
B 1장과 2장은 절마다 선행 사례와 방법을 조사하여 표로 비교하고, 그중 댐 운영 자료와 조건이 가까운 것을 추려 상세히 분석한 뒤 본 과업의 적용 방향이나 (안)을 산출하는 순서로 구성하였다. 앞 절의 산출은 뒤 절의 입력이 되며, 절 사이의 연결은 ⟦표:s111_flow⟧와 같다.
''')
s.append(['TABLE', {'label': 's111_flow', 'caption': '1·2장의 절별 조사 내용과 산출', 'widths': [15, 27, 30, 28], 'align': ['c', 'l', 'l', 'l'], 'rows': [
    ['절', '조사·비교한 것', '산출', '이어지는 절'],
    ['1.1 사례 조사', 'RAG, 도메인 특화 LLM, 운영지식 구조화의 국내외 사례', '유형별 구성 방식과 댐 운영에 적합한 구성', '1.3의 기술요소 검토, 3·4장의 모델 검토'],
    ['1.2 운영 여건 조사', '착수보고회 의견, 공개 자료의 제공 방식, 현장방문 조사', '기술 적용 시 고려사항', '1.3의 적용 방향, 2.1의 수집 대상'],
    ['1.3 기술요소 및 모델 제안', '프레임워크를 5개 파트로 나눈 파트별 선행 기술', '파트별 적용 기술(안)과 RAG-sLLM 아키텍처(안)', '2.2의 설계(안), 2.3의 파이프라인(안)'],
    ['2.1 수집 경로 조사', '수문·기상·승인 기록·규정의 제공 경로와 데이터 형태', '자료별 적정 수집 경로(안)', '2.2의 전처리 체계(안)'],
    ['2.2 온톨로지·메타데이터', '온톨로지 설계 방법, 메타데이터 항목, 처리 방식', '전처리 체계(안), 댐 운영 온톨로지 설계(안)', '2.3의 지식기반 구축 단계'],
    ['2.3 통합 파이프라인(안)', '질의 해석, 근거 조회, 근거 전달 방식', '7단계 파이프라인(안)과 표준 프롬프트 프레임(안)', '3·4장의 sLLM 적용, 5장의 추진 방향']]}])
OUT['1_1_1'] = s

# ============================================================ 1.1.2~1.1.4 : 사례 상세의 세부 줄을 줄이고 흐름 줄을 넣는다
FLOW11 = {
    '1_1_2': ('1.1.2', 'RAG 기반 질의응답', '문서 검색형, KG 결합형, 정형 자료 조회형, 에이전트형'),
    '1_1_3': ('1.1.3', '도메인 특화 LLM', '추가 사전학습, 경량 미세조정, 미세조정과 검색의 결합'),
    '1_1_4': ('1.1.4', '운영지식 구조화', '온톨로지 설계, KG 구축, 저장과 활용')}
for n, (num, name, kinds) in FLOW11.items():
    s = load(n)
    s = prune(s, NOTE)
    s = cap_ds(s, 1, lambda h3, h4: h4.startswith('다.'))
    s = cap_ds(s, 2, lambda h3, h4: h4.startswith(('가.', '라.', '마.')))
    # 첫 본문 뒤에 흐름 줄
    i = [j for j, (k, v) in enumerate(s) if k == 'BODY'][0]
    s[i + 1:i + 1] = L('''
□ 본 소절의 구성
◦ %s의 구성 방식(%s)을 정리하고 국내외 사례를 같은 항목의 표로 비교
◦ 댐·수리시설의 운영 자료를 다룬 사례를 추려 구성과 결과를 상세히 분석
◦ 사례 비교 결과에서 댐 운영 적용 방향을 도출하여 1.1.5의 종합과 1.3의 기술요소 검토로 연결
''' % (name, kinds))
    OUT[n] = s
# 타 분야 KG 사례의 항목 비교표 두 개는 사례 목록표와 내용이 겹치므로 뺀다
OUT['1_1_4'] = drop_tables(OUT['1_1_4'], lambda v: v['label'] in ('kg_cmp1_other', 'kg_cmp2_other'))
for i, (k, v) in enumerate(OUT['1_1_4']):
    if k == 'BODY' and 'kg_cmp1_other' in v:
        OUT['1_1_4'][i] = [k, '댐·수리시설·홍수 분야 사례는 ⟦표:kg_list_water⟧에, 타 분야 사례와 일반 방법은 ⟦표:kg_list_other⟧에 정리하였다. 댐·수리시설·홍수 분야 사례의 자료, 구조·방법, 지식 구조, 검색은 ⟦표:kg_cmp1_water⟧에, 생성 모델, 평가 방법, 대표 결과는 ⟦표:kg_cmp2_water⟧에 정리하였다.']

# ============================================================ 1.1.5 : 종합 시사점은 공정보고(8월)의 서술을 기본으로
s = load('1_1_5')
s = replace_h4(s, '다. 댐 운영 의사결정 지원에 적합한 구성', L('''
#4 다. 종합 시사점(댐 운영 프레임워크 구축 관점)
□ 검색증강(RAG) 구조 자체의 필요성 확인
◦ IWMS-LLM, WaterRAG, 수리시설 점검 QA 세 사례 모두 사전 구축된 문헌·지식 DB를 검색하는 사전 적재형 RAG 구조로 전문지식 질의응답의 정확도와 시스템 활용성을 높임 ⟦문헌:05_IWMS-LLM⟧, ⟦문헌:06_WaterRAG⟧, ⟦문헌:07_수리시설점검QA⟧
- WaterRAG의 답변 정확성 통과율은 80.5%로 LLM 단독(64.9%)보다 높음
- 운영규정·과거사례 등 정적 문서가 많은 댐 운영 도메인에도 사전 적재형 RAG 기반 접근이 필요함을 뒷받침하는 근거임
□ 7B~8B급 경량 모델의 실효성
◦ WaterGPT, HydroLLM, EnvGPT 모두 7B~8B급에서 높은 성능을 보임 ⟦문헌:17_WaterGPT⟧, ⟦문헌:18_HydroLLM⟧, ⟦문헌:20_EnvGPT⟧
- HydroLLM의 32B 과적합 사례는 모델 크기를 무조건 키우는 것이 능사가 아님을 보여줌
- 3.3 후보군 적용방안에서 "데이터 규모 대비 적정 모델 크기" 검토가 필요함
□ 경량 임베딩 모델 병행 고려
◦ HydroEmbed처럼 22.7M 파라미터의 초경량 임베딩 모델을 별도로 두면 온프레미스·저지연 환경에서 검색 단계의 자원 부담을 줄일 수 있음 ⟦문헌:19_HydroEmbed⟧
- 4.1 RAG 기반 적용방안 조사 시 검색기 후보로 추가 검토할 가치가 있음
□ 온톨로지·KG 구축 방법론의 실행 청사진 확보
◦ Flood Ontology, MS GraphRAG, Train Maintenance KG, GraphAide가 서로 다른 도메인에서 제시한 온톨로지 설계 절차와 KG 구축 절차는 출처가 다양한 자료를 지식그래프로 연결하고 근거를 추적 가능하게 유지하는 작업에 참고할 수 있는 구체적 절차를 제공 ⟦문헌:36_FloodOntology⟧, ⟦문헌:37_MSGraphRAG⟧, ⟦문헌:38_TrainMaintenanceKG⟧, ⟦문헌:39_GraphAide⟧
- 댐 분야에서는 DDKG와 OntoDSMS가 보고서와 계측 자료를 온톨로지에 연결한 절차를 제시 ⟦문헌:46_DDKG⟧, ⟦문헌:47_OntoDSMS⟧
- 2.2 온톨로지·메타데이터 설계와 2.3 파이프라인(안) 단계에서 이 절차를 적용
□ 도메인 범용성 확인
◦ 금융·법률·국방·시설안전 등 수자원과 무관한 도메인에서도 RAG, 도메인 특화 LLM, 온톨로지·KG 구조가 동일하게 유효하게 작동함이 확인
- 특정 산업의 특수성이 아니라 아키텍처 자체의 범용성에서 기인한 결과로 해석되며, 수자원·댐 운영 도메인에도 동일한 아키텍처를 적용할 수 있다는 근거를 뒷받침
□ 댐 운영 의사결정 지원에 적합한 구성
◦ 위 시사점과 유형별 적용 방향을 종합하면, 검색 근거에 기반한 응답을 기본으로 하고 운영지식 KG와 수문 자료 조회를 결합한 구성이 적합
- 구성요소별 적용 방향은 ⟦표:s115_fit⟧과 같으며, 적용 기술요소(1.3), 온톨로지·메타데이터 설계방안(2.2), 통합 파이프라인(안)(2.3)의 근거가 됨
'''))
tb = [x for x in load('1_1_5') if x[0] == 'TABLE' and x[1]['label'] == 's115_fit'][0]
s.append(tb)
OUT['1_1_5'] = s

# ============================================================ 1.2 : 법령·조문 정리를 빼고 공정보고(8월)의 착수보고회 내용을 중심으로
s = load('1_2')
s = drop_section(s, 'H3', '1.2.2')
s = drop_sq(s, '규정에서 확인되는 자료의 쓰임')
s = drop_section(s, 'H4', '가. 규정상 절차에서 도출되는 고려사항')
LAW = re.compile(r'법령|조문|연계운영규정|하천법|제[0-9]+조|별표')
s = prune(s, LAW)
for k, v in s:
    if k == 'TABLE' and v['label'] == 's12_method':
        v['rows'] = [v['rows'][0]] + [r for r in v['rows'][1:] if not LAW.search(' '.join(map(str, r)))]
REN = {'1.2.3': '1.2.3 자료 활용 방식', '1.2.4': '1.2.2 착수보고회 논의와 주요 쟁점', '1.2.5': '1.2.4 현장방문 조사', '1.2.6': '1.2.5 기술 적용 시 고려사항'}
blocks, cur = {}, None
for k, v in s:
    if k == 'H3':
        cur = v[:5]; blocks[cur] = []
        v = REN.get(cur, v)
    blocks[cur].append([k, v])
s = blocks['1.2.1'] + blocks['1.2.4'] + blocks['1.2.3'] + blocks['1.2.5'] + blocks['1.2.6']
let = iter('가나다라마')
h3 = ''
for it in s:
    if it[0] == 'H3': h3 = it[1]
    if it[0] == 'H4' and h3.startswith('1.2.5'):
        it[1] = next(let) + it[1][1:]
    for a, b in (('1.2.6', '1.2.5'),):
        if isinstance(it[1], str) and it[0] != 'H3': it[1] = it[1].replace(a, b)
s = insert_after_h3(s, '1.2.1', L('''
□ 본 절의 구성
◦ 착수보고회에서 제시된 발주처의 의견과 쟁점을 정리(1.2.2)
◦ 댐 운영에 쓰이는 공개 자료의 제공 방식을 조사(1.2.3)
◦ 한수원 한강수력본부 현장방문 조사로 업무 절차와 자료 활용 방식, 시스템 운영 환경을 확인(1.2.4)
◦ 세 조사의 결과에서 기술 적용 시 고려사항을 도출하여 1.3의 적용 방향과 2.1의 수집 대상으로 연결(1.2.5)
'''))
FIX12 = [('댐 운영의 업무 절차와 의사결정 구조를 공개 규정에 근거하여 정리', '댐 운영의 업무 절차와 의사결정 구조, 자료 활용 방식을 착수보고회 논의와 현장방문 조사로 확인'),
         ('규정과 공개 자료의 조사는 한강수계의 댐과 보를 중심으로 수행', '공개 자료의 조사는 한강수계의 댐과 보를 중심으로 수행'),
         ('규정에서 확인한 운영 절차, 공개 자료의 제공 방식, 착수보고회에서 제시된 쟁점을 근거로', '공개 자료의 제공 방식과 착수보고회에서 제시된 쟁점을 근거로'),
         ('제공기관별로 시설 코드 체계가 다르고 규정에는 이름만 있어 시설의 대응 관계를 정리할 필요', '제공기관별로 시설 코드 체계가 달라 시설의 대응 관계를 정리할 필요')]
for it in s:
    if isinstance(it[1], str):
        for a, b in FIX12: it[1] = it[1].replace(a, b)
OUT['1_2'] = s

# ============================================================ 1.3 / 2.2 / 2.3
REF = {'Noy': '2.2.2', 'Li 외(2025)': '2.2.2', '초기 온톨로지와 확장': '2.2.2', 'Huang 외(2026)': '1.1.4', 'Zhou 외(2023)': '1.1.4',
       'Han 외(2026)': '1.1.2', '의도 인식과 답변 경로 분기': '1.1.2', '개체 인식·개체 연결·의도 인식': '1.1.2', '지식 출처에 따른 경로 분기': '1.1.2'}
s = load('1_3')
s = drop_tables(s, lambda v: ('편수' in v['rows'][0] and '분류' in v['caption']) or v['caption'].endswith('문헌 목록'))
s = prune(s, COUNT); s = prune(s, NOTE)
s = shorten_h5(s, ['Noy', 'Li 외(2025)', 'Huang 외(2026)', 'Zhou 외(2023)', 'Han 외(2026)'], REF)
s = shorten_h5(s, ['(3) 계산된 근거의 전달과 답변 검증'], {'(3) 계산된 근거의 전달과 답변 검증': '1.3.4와 2.3.3'})
s = shorten_h5(s, ['(1) KG 지식을 우선하는 프롬프트', '(1) 의도 투표와 범주별 질의 규칙'], {'(1) KG 지식을 우선하는 프롬프트': '2.3.3', '(1) 의도 투표와 범주별 질의 규칙': '2.3.3'})
s = cap_ds(s, 0, lambda h3, h4: h4.startswith('가.'))           # 선행 기술의 나열은 비교표가 맡는다
s = cap_ds(s, 1, lambda h3, h4: h4.startswith('나.'))
s = cap_ds(s, 2, lambda h3, h4: h4.startswith('다.'))
s = insert_after_h3(s, '1.3.1', L('''
□ 본 절의 구성
◦ RAG-LLM 프레임워크를 5개 파트로 나누고, 파트마다 선행 기술을 조사하여 표로 비교
◦ 댐 운영 자료와 조건이 가까운 방법을 추려 절차와 보고된 결과를 상세히 분석
◦ 파트별 적용 방향을 정하고 이를 묶어 RAG-sLLM 아키텍처(안)과 적용 기술 종합을 산출
- 산출은 2.2의 온톨로지·전처리 설계(안)와 2.3의 통합 파이프라인(안)의 근거가 됨
'''))
OUT['1_3'] = s

s = load('2_2')
s = drop_tables(s, lambda v: '편수' in v['rows'][0] or '조사 대상 문헌' in v['caption'])
s = drop_tables(s, lambda v: v['caption'].startswith('KG 구축 후 점검 항목'))
s = prune(s, COUNT); s = prune(s, NOTE)
s = prune(s, re.compile(r'Neo4j를 사용|stationCode|concernsDam|점검 항목'))
s = cap_ds(s, 1, lambda h3, h4: h3.startswith(('2.2.2', '2.2.3')) and h4.startswith(('가.', '나.')) or (h3.startswith('2.2.4') and h4.startswith('가.')))
s = cap_ds(s, 2, lambda h3, h4: h3.startswith('2.2.2') and h4.startswith('다.'))
s = insert_after_h3(s, '2.2.1', L('''
□ 본 절의 구성
◦ 온톨로지 설계 방법과 메타데이터 항목, 자료 처리 방식을 선행 사례에서 조사하여 표로 비교
◦ 단계적 설계 방법, 댐 분야 적용 사례, 전문가 검토를 둔 반자동 방법을 추려 상세히 분석
◦ 2.1의 자료 현황에 맞추어 전처리 체계(안), 댐 운영 온톨로지 설계(안), 설계·보완 절차(안)를 산출
- 산출은 2.3 통합 파이프라인(안)의 전처리 단계와 지식기반 구성 단계의 입력이 됨
'''))
OUT['2_2'] = s

s = load('2_3')
s = drop_tables(s, lambda v: '조사 대상 문헌' in v['caption'])
s = prune(s, COUNT); s = prune(s, NOTE)
s = shorten_h5(s, ['개체 인식·개체 연결·의도 인식', '지식 출처에 따른 경로 분기'], REF)
s = cap_ds(s, 0, lambda h3, h4: (h3.startswith(('2.3.3', '2.3.4')) and h4.startswith('가.')))
s = cap_ds(s, 1, lambda h3, h4: (h3.startswith('2.3.5') and h4.startswith('가.')) or (h3.startswith('2.3.6') and h4.startswith('나.')))
s = cap_ds(s, 2, lambda h3, h4: h3.startswith(('2.3.3', '2.3.4')) and h4.startswith('나.'))
s = cap_ds(s, 1, lambda h3, h4: h3.startswith('2.3.8'))
s = insert_after_h3(s, '2.3.1', L('''
□ 본 절의 구성
◦ 2.1의 수집 경로와 2.2의 전처리·온톨로지 설계(안)를 지식기반 구축 단계(①~③)로 연결
◦ 질의 해석, 근거 조회, 근거 정리의 선행 방식을 조사하여 표로 비교하고 주요 방식을 상세히 분석
◦ 7단계의 입력·처리·산출과 표준 프롬프트 프레임(안), 근거 사용 원칙(안)을 산출
- 산출은 3·4장의 sLLM 적용과 성능 향상 전략의 전제가 됨
'''))
OUT['2_3'] = s

# 2.1은 내용을 유지하고 흐름 줄만 넣는다
s = load('2_1')
s = prune(s, NOTE)
s = cap_ds(s, 2, lambda h3, h4: h3.startswith(('2.1.2', '2.1.3', '2.1.4', '2.1.6', '2.1.7')))
s = insert_after_h3(s, '2.1.1', L('''
□ 본 절의 구성
◦ 댐 운영 판단에 쓰이는 자료를 영역별로 나누고 제공 기관의 수집 경로를 같은 기준으로 조사하여 표로 비교
◦ 경로별 데이터 형태와 식별 체계를 상세히 확인하고 공개 자료의 한계를 정리
◦ 자료별 적정 수집 경로(안)을 산출하여 2.2의 전처리 체계(안)와 2.3의 수집 단계로 연결
'''))
OUT['2_1'] = s

def tidy(items):
    """제목의 편수 표기를 지우고, 제목 바로 뒤에 표만 남은 곳에는 표를 가리키는 본문 한 줄을 넣는다."""
    out = []
    for i, (k, v) in enumerate(items):
        if k in ('SQ', 'H5') and isinstance(v, str): v = re.sub(r' [0-9]+편$', '', v)
        out.append([k, v])
        if k == 'H4' and i + 1 < len(items) and items[i + 1][0] == 'TABLE':
            out.append(['BODY', '같은 항목으로 비교한 결과는 ⟦표:%s⟧와 같다.' % items[i + 1][1]['label']])
    return out


for _n in list(OUT):
    OUT[_n] = tidy(prune(OUT[_n], re.compile(r'^$')))
tot = 0
for n, items in OUT.items():
    # 표가 빠진 뒤 남은 표 참조가 든 문장은 참조만 지운다
    labels = {v['label'] for k, v in items if k in ('TABLE', 'FIGPLACE')}
    for it in items:
        if isinstance(it[1], str):
            for typ, lab in re.findall(r'⟦(표|그림):([^⟧]+)⟧', it[1]):
                if lab.strip() not in labels and not any(lab.strip() in {v['label'] for k, v in o if k in ('TABLE', 'FIGPLACE')} for o in OUT.values()):
                    it[1] = '(삭제)'
    items = [it for it in items if it[1] != '(삭제)']
    OUT[n] = items
    json.dump(items, open(os.path.join(SEC, n + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    pc = sum(len(v) for k, v in items if isinstance(v, str)); tc = sum(len(str(c)) for k, v in items if k == 'TABLE' for r in v['rows'] for c in r)
    tot += pc + tc
    print('%-6s 본문 %6d  표글자 %6d  표 %2d  그림 %2d' % (n, pc, tc, sum(k == 'TABLE' for k, v in items), sum(k == 'FIGPLACE' for k, v in items)))
print('합계', tot, '(이전 177269, 190쪽) → 추정', round(190 * tot / 177269), '쪽')
