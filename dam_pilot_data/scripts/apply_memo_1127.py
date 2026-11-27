#!/usr/bin/env python3
"""2026-11-27 메모 반영: 2.3의 구성을 '사례의 기술 원리 → 적용 기술(안)'으로 바로잡는다.

한 번만 실행하는 이관 스크립트다. 실행 전 섹션을 sections/_old11 에 백업한다.
- 0_1: '(계약 기준)' 삭제
- 0_3: 추진 일정 표를 월 단위로, 사진 자리 삭제, 현장방문 참석자 표를 일정 표로, 답변 열을 실제 답변으로
- 1_1_2~4: '다. 주요 사례'를 기술 원리 위주로 재배열
- 1_2: 2.2.4에서 수행기관의 요청 사항(평가 자료와 실무자 검토) 삭제
- 1_3: 파트별 비교표·적용 조건·장단점·보고된 결과·판단·후속 검토를 걷어내고 2.3.4 삭제
"""
import json, re, shutil, sys
from pathlib import Path

SEC = Path(__file__).resolve().parents[2] / 'project_khnp/final_report/sections'
BAK = SEC / '_old11'
if BAK.exists():
    sys.exit('이미 실행됨(_old11 존재)')
BAK.mkdir()
for f in SEC.glob('*.json'):
    shutil.copy(f, BAK / f.name)

load = lambda n: json.loads((SEC / f'{n}.json').read_text(encoding='utf8'))
save = lambda n, d: (SEC / f'{n}.json').write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf8')


def find(d, kind, start):
    for i, it in enumerate(d):
        if it[0] == kind and isinstance(it[1], str) and it[1].startswith(start):
            return i
    raise KeyError(start)


def tbl(d, label):
    for it in d:
        if it[0] == 'TABLE' and it[1]['label'] == label:
            return it[1]
    raise KeyError(label)


# ───────── 0_1 ─────────
d = load('0_1')
s = json.dumps(d, ensure_ascii=False)
assert '(계약 기준)' in s
save('0_1', json.loads(s.replace('(계약 기준)', '')))

# ───────── 0_3 ─────────
d = load('0_3')
t = tbl(d, 's0_history')
t['rows'] = [['시기', '내용'],
             ['2026. 7.', '과업 착수, 착수보고회'],
             ['2026. 9. ~ 12.', '월간 공정보고(8월 ~ 11월)'],
             ['2026. 11.', '한수원 한강수력본부 현장방문 조사'],
             ['2026. 12.', '최종보고회']]
d = [it for it in d if not (it[0] == 'FIGPLACE' and it[1]['label'] in ('s0_fig_kickoff', 's0_fig_visit'))]
i = next(i for i, it in enumerate(d) if it[0] == 'TABLE' and it[1]['label'] == 's0_visit_attend')
assert d[i - 1] == ['CI', '참석자']
d[i - 1] = ['CI', '일정']
d[i] = ['TABLE', {'label': 's0_visit_plan', 'caption': '현장방문 조사 일정', 'widths': [26, 74], 'align': ['c', 'l'], 'rows': [
    ['시간', '내용'],
    ['오전', '【확인 후 기재】 오전 일정'],
    ['13:30 ~ 15:30', '과업 수행 결과 발표, 실무자 질의응답'],
], 'note': None}]
j = find(d, 'CI', '일시: 2026년 11월 26일')
d[j][1] = '일시: 2026년 11월 26일(목)'
t = tbl(d, 's0_visit_opinion')
t['rows'][0] = ['구분', '주요의견', '답변']
ans = {
    '기존 계획과의 관계': '- 문서 검색 방식은 뜻이 가까운 문서를 가져오므로 질의에 맞지 않는 근거가 섞일 수 있고, 지식그래프 방식은 정해 둔 범위에서 관계로 이어진 근거를 가져온다고 설명함\n- 두 방식은 함께 쓸 수 있으며 기존 시스템에 결합하는 방향이 가능하다고 답변함',
    '기능의 범위': '- 계산과 예측은 LLM이 직접 하지 않고 미리 정의한 물리 모델을 호출하여 그 결과로 답하는 구조가 적합하다고 답변함\n- 발표한 구성은 조회와 근거 제시까지이며 모델 호출은 다음 단계의 범위라고 설명함',
    '운영 판단의 특성': '- 지식그래프는 판단하지 않고 근거를 제공하며, 규정과 다르게 운영한 과거 사례도 함께 찾아 제시할 수 있다고 답변함\n- 여러 방안을 만들어 제시하고 선택은 운영자가 하는 구성이 가능하다고 답변함',
    '갱신과 유지관리': '- 변동이 적은 기준은 지식그래프로, 변동이 잦은 문서는 문서 검색으로 나누는 이원 구성을 제시함\n- 문서를 갱신할 때 이전 판본을 관리하여야 한다는 점을 함께 논의함',
    '사용 편의': '- 사용자는 한 줄의 질의만 입력하고, 근거는 시스템이 구성하여 모델에 전달하는 구조라고 답변함',
    '활용 방안': '- 과거 운영 자료와 미리 정해 둔 양식으로 운영 결과를 정리하는 기능은 가능하다고 답변함',
    '협조 요청': '- 수행기관이 목록과 예시를 작성하여 보내고, 실무자는 필요 여부와 정오를 표시하는 방식으로 협의함',
}
for r in t['rows'][1:]:
    r[2] = ans[r[0]]
save('0_3', d)

# ───────── 1_2 ─────────
d = load('1_2')
i = find(d, 'SQ', '평가 자료와 실무자 검토')
del d[i:i + 2]
save('1_2', d)

# ───────── 1_1_2 ~ 1_1_4: 다. 주요 사례를 기술 원리 위주로 ─────────
PRIN = ['처리 단계', '온톨로지의 구성', 'KG 구축 방법', '저장과 질의']


def regroup_case(items):
    """H5 아래 한 사례의 항목을 문제 → 기술 원리 → 그림 → 자료와 보고된 결과 순으로 재배열."""
    groups, raws, seen_eval = {}, [], False
    cur = None
    order = []
    for it in items:
        if it[0] == 'SQ':
            cur = it[1]
            if cur in ('풀려는 문제', '자료', '평가와 결과', '한계') or cur in PRIN:
                groups[cur] = []
                if cur == '평가와 결과':
                    seen_eval = True
            else:                      # 알 수 없는 SQ(세 사례의 비교 등)는 끝에 그대로
                cur = None
                raws.append(('tail', it))
            continue
        if it[0] in ('CI', 'DS') and cur:
            groups[cur].append(it)
        else:
            cur = None
            raws.append(('mid' if (it[0] == 'FIGPLACE' and not seen_eval) else 'tail', it))
    out = []
    if '풀려는 문제' in groups:
        out += [['SQ', '풀려는 문제']] + groups['풀려는 문제']
    for p in PRIN:
        if p in groups:
            out += [['SQ', '기술 원리' if p == '처리 단계' else p]] + groups[p]
    out += [it for pos, it in raws if pos == 'mid']
    res = [it for it in groups.get('자료', []) if it[0] == 'CI'] + groups.get('평가와 결과', [])
    if res:
        out += [['SQ', '자료와 보고된 결과']] + res
    out += [it for pos, it in raws if pos == 'tail']
    return out


for n in ('1_1_2', '1_1_3', '1_1_4'):
    d = load(n)
    a = find(d, 'H4', '다. 주요 사례의 구성과 결과')
    b = find(d, 'H4', '라. ')
    blk = d[a:b]
    blk[0][1] = '다. 주요 사례의 기술 원리'
    assert blk[1][0] == 'BODY'
    blk[1][1] = blk[1][1].replace('의 구성과 결과는 다음과 같다', '의 기술 원리와 보고된 결과는 다음과 같다')
    new, case = blk[:2], None
    for it in blk[2:]:
        if it[0] == 'H5':
            if case is not None:
                new += regroup_case(case)
            new.append(it)
            case = []
        else:
            case.append(it)
    new += regroup_case(case)
    d[a:b] = new
    save(n, d)

# ───────── 1_3: 사례의 기술 원리 → 적용 기술(안) ─────────
d = load('1_3')
a = find(d, 'H3', '2.3.2')
b = find(d, 'H3', '2.3.3')
c = find(d, 'H3', '2.3.4')
head, part, arch = d[:a], d[a:b], d[b:c]          # 2.3.4(c 이후)는 삭제

SRC = {'가': '2.1.4', '나': '2.1.4', '다': '2.1.4', '라': '2.1.2', '마': '2.1.2'}
DERIVE = {
    '가': '댐 분야 사례는 전문가가 단계 절차에 따라 Class와 관계를 정의하였고, LLM으로 온톨로지를 넓힌 사례는 전문가 검토를 함께 두었다. 이에 따라 운영자의 질문에서 출발한 초기 온톨로지를 전문가가 정하고 구축 결과에 따라 보완하는 방식을 적용 기술(안)으로 한다.',
    '나': '댐 운영 자료는 수문·기상 수치와 방류 승인 기록 같은 정형 자료, 운영 규정 같은 문서 자료로 이루어진다. 사례에서 정형 자료는 열과 항목의 대응으로, 양식이 일정한 문서는 규칙으로 구조화하였으므로 이를 적용 기술(안)으로 한다.',
    '다': '수치 시계열을 다룬 사례는 수치를 원본 저장소에 두고 KG와 연결하였다. 댐 운영에 쓰이는 수문·기상 수치는 제공기관의 시스템에서 주기적으로 갱신되므로, 수치는 원본 저장소에 두고 KG에는 식별 키만 두는 방식을 적용 기술(안)으로 한다.',
    '라': '수리·하천 분야 사례는 의도 범주를 정해 두고 범주별 질의 규칙으로 조회하여 같은 질의에 같은 조회 결과를 얻었다. 운영 질의는 응답의 근거를 함께 제시하여야 하므로(2.2.2), 조회 결과를 재현할 수 있는 의도 범주와 질의 규칙 방식을 적용 기술(안)으로 한다.',
    '마': '사례는 검색한 근거를 응답 모델의 입력에 결합하고 출처 표시를 함께 두었다. 착수보고회에서 판단 근거를 함께 제시하는 구조가 필요한 것으로 확인되었으므로(2.2.2), 검색한 결과를 출처 번호가 붙은 근거로 구성하여 전달하고 응답에서 사용한 근거를 표기하는 방식을 적용 기술(안)으로 한다.',
}

part[0][1] = '2.3.2 기술요소별 기술 원리와 적용 기술(안)'
out = [part[0]]
key = None            # 현재 파트(가~마)
mode = None           # 'intro' | 'drop' | 'method' | 'apply'
keep_sq = False
for it in part[1:]:
    k, v = it
    if k == 'H4':
        key, mode = v[0], 'intro'
        out.append(it)
        continue
    if key is None:    # 2.3.2 머리말(BODY 등)
        out.append(it)
        continue
    if k == 'H5':
        num = int(re.match(r'\((\d)\)', v).group(1))
        if num == 1:
            mode = 'drop'
        elif num in (2, 3, 4):
            mode = 'method'
            out.append(['H5', f'({num - 1})' + v[3:]])
        else:
            mode = 'apply'
            out.append(['H5', '(4) 적용 기술(안)'])
            out.append(['BODY', DERIVE[key]])
        keep_sq = False
        continue
    if mode == 'intro':
        if k == 'BODY':
            it = ['BODY', v + f' {SRC[key]}에서 조사한 사례 가운데 이 파트에 해당하는 방식의 기술 원리는 다음과 같다.']
        out.append(it)
    elif mode == 'method':
        if k == 'SQ':
            keep_sq = (v == '기술 원리')
            if keep_sq:
                out.append(it)
        elif k == 'FIGPLACE' or (keep_sq and k in ('CI', 'DS')):
            out.append(it)
    elif mode == 'apply':
        if k == 'SQ':
            keep_sq = v.startswith('적용 기술(안)') or v.startswith('적용 방향')
        elif keep_sq and k in ('CI', 'DS'):
            out.append(it)

# 2.3.1: 파트 구분 설명과 표에서 '검토'라는 틀을 걷어냄
for it in head:
    if it[0] == 'CI' and it[1].startswith('파트를 나눈 이유는'):
        it[1] = '파트를 나눈 이유는 파트마다 입력과 산출이 달라 해당하는 사례와 기술이 다르기 때문임'
    if it[0] == 'DS' and it[1].startswith('과업 내용의 세 요소가 서로 다른 파트에 대응'):
        it[1] = '과업 내용의 세 요소가 서로 다른 파트에 대응'
t = tbl(head, 's13_parts')
t['caption'] = 'RAG-LLM 프레임워크의 파트 구분'
t['rows'][0][-1] = '관련 사례'

# 2.3.3: 2.3.4가 없어졌으므로 3.3절로 이어지는 문장만 둠
arch.append(['BODY', '아키텍처(안)는 적용할 기술요소의 큰 틀이며, 자료별 수집 경로(3.1절)와 온톨로지·메타데이터 설계(3.2절)를 더한 단계별 구성은 3.3절의 RAG-LLM 통합 파이프라인(안)에서 제시한다.'])
save('1_3', head + out + arch)

# ───────── 1_4: 산출물 표에서 삭제된 표·절 참조 정리 ─────────
d = load('1_4')
s = json.dumps(d, ensure_ascii=False)
print('1_4 참조:', re.findall(r'[^"]{0,40}(?:2\.3\.4|적용 기술 종합)[^"]{0,40}', s))
print('done')
