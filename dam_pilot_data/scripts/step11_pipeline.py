#!/usr/bin/env python3
"""STEP 11: 질문 -> (LLM) 의도(CQ1~CQ6, 여러 개 가능)·값 추출 -> (자동화 코드) 입력 확인·Cypher 템플릿·Neo4j·측정/문서 저장소 -> 근거 묶음 -> (LLM) 답변.
LLM은 OpenAI 호환 API(vLLM, Ollama, llama.cpp 서버 등)에 연결한다. stdlib만 사용.

환경변수: LLM_BASE_URL(예: http://localhost:8000/v1), LLM_MODEL(예: Qwen/Qwen2.5-7B-Instruct), LLM_API_KEY(선택), NEO4J_HOME
사용:
  python3 scripts/step11_pipeline.py --question "2020년 8월 충주댐 운영행위는?"
  python3 scripts/step11_pipeline.py --questions-file 05_retrieval/questions_example.json
  python3 scripts/step11_pipeline.py --mock --questions-file 05_retrieval/examples_requests.json   # 배관 점검용 가짜 LLM. 결과를 성과로 쓰지 말 것
각 질문의 전 과정(의도 원문, 의도 JSON, 검색 결과, 근거 묶음, 답변)을 05_retrieval/runs/<시각>/에 저장한다.
"""
import argparse, importlib.util, json, os, re, sys, time, urllib.request
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__)); R5 = os.path.join(HERE, '..', '05_retrieval')


def load(name, fname):
    s = importlib.util.spec_from_file_location(name, os.path.join(HERE, fname)); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


r9, r10 = load('r9', 'step9_retrieve.py'), load('r10', 'step10_bundle.py')
INTENT_PROMPT = open(os.path.join(R5, 'intent_prompt.md'), encoding='utf-8').read()
ANSWER_PROMPT = open(os.path.join(R5, 'answer_prompt.md'), encoding='utf-8').read()


def chat(messages, temperature=0.0, max_tokens=1500):
    base, model = os.environ['LLM_BASE_URL'].rstrip('/'), os.environ['LLM_MODEL']
    body = {'model': model, 'messages': messages, 'temperature': temperature, 'max_tokens': max_tokens}
    if os.environ.get('LLM_NO_THINK'):
        body['chat_template_kwargs'] = {'enable_thinking': False}
    req = urllib.request.Request(base + '/chat/completions', data=json.dumps(body).encode('utf-8'),
                                 headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + os.environ.get('LLM_API_KEY', 'none')})
    out = json.loads(urllib.request.urlopen(req, timeout=600).read().decode('utf-8'))
    txt = out['choices'][0]['message']['content'] or ''
    return re.sub(r'<think>.*?</think>', '', txt, flags=re.S).strip()


def parse_json(txt):
    """JSON 객체 하나를 읽는다. 같은 키가 두 번 나오면(예: 댐이 둘) 마지막 값만 취하지 않고 그 사실을 알린다. 반환: (객체 또는 None, 중복된 키 목록)"""
    m = re.search(r'\{.*\}', txt, flags=re.S)
    if not m:
        return None, []
    dups = []

    def hook(pairs):
        seen = {}
        for k, v in pairs:
            if k in seen and k not in dups:
                dups.append(k)
            seen[k] = v
        return seen

    try:
        return json.loads(m.group(0), object_pairs_hook=hook), dups
    except Exception:
        return None, []


WEEK = '월화수목금토일'


def today():
    """오늘 날짜. 시연이나 재현 때는 환경변수 PIPELINE_TODAY=YYYY-MM-DD로 고정할 수 있다."""
    v = os.environ.get('PIPELINE_TODAY')
    return datetime.strptime(v, '%Y-%m-%d') if v else datetime.now()


def intent_system():
    """질문 해석 프롬프트 + 기준 시각(오늘 날짜, 저장된 측정자료의 마지막 시각). '오늘', '지난달' 같은 말을 실제 날짜로 바꾸는 데 쓴다."""
    t = today()
    o = [INTENT_PROMPT.rstrip(), '', '## 기준 시각', '- 오늘 날짜: %s (%s요일)' % (t.strftime('%Y-%m-%d'), WEEK[t.weekday()])]
    try:
        st = r9.store()
        o.append('- 저장된 측정자료의 마지막 시각: ' + ', '.join('%s %s' % (n, st.latest(c).strftime('%Y-%m-%d %H:%M')) for c, n in r9.M.CODES.items()))
    except Exception:
        pass
    return '\n'.join(o)


def intent_llm(question):
    sysm = intent_system()
    msgs = [{'role': 'system', 'content': sysm}, {'role': 'user', 'content': question}]
    raw = chat(msgs)
    j, dups = parse_json(raw)
    if j is None:
        msgs += [{'role': 'assistant', 'content': raw}, {'role': 'user', 'content': 'JSON 하나만 다시 출력하세요.'}]
        raw2 = chat(msgs)
        raw, (j, dups) = raw + '\n--- 재시도 ---\n' + raw2, parse_json(raw2)
    if dups:
        return raw, {'intent': [], 'reason': '질문에 같은 종류의 값(%s)이 둘 이상 있어 한 번에 처리하지 않음' % ', '.join(dups)}
    # 값 확인: 시점이 날짜로 읽히지 않으면(형식 예시를 그대로 냄, '내일' 등) 이유를 알려 주고 한 번 다시 묻는다
    if j and j.get('intent'):
        _, err = r9.check(j)
        if err and err.startswith('시점 형식 오류'):
            msgs2 = [{'role': 'system', 'content': sysm}, {'role': 'user', 'content': question}, {'role': 'assistant', 'content': json.dumps(j, ensure_ascii=False)},
                     {'role': 'user', 'content': 'period 값을 날짜로 읽을 수 없습니다(%s). 기준 시각의 오늘 날짜로 실제 날짜를 계산해 넣으세요. 질문에 시점이 없으면 "전체", '
                                                 '미래의 값이나 날짜가 아닌 숫자를 묻는 질문이면 intent를 빈 목록으로 두고 reason을 적으세요. JSON 하나만 다시 출력하세요.' % err}]
            raw2 = chat(msgs2); j2, d2 = parse_json(raw2)
            raw += '\n--- 시점 재시도 ---\n' + raw2
            if j2 is not None and not d2:
                j = j2
    return raw, j


TAG = re.compile(r'\[([^\[\]\n]{1,60})\]')
ID = re.compile(r'^[A-Z]{2,5}:\S+$')
LAST_CITE = {}


def cite_check(answer, bundle):
    """답변의 대괄호 표시를 근거 묶음의 출처 번호와 맞춰 본다. 반환: (맞는 번호, 묶음에 없는 번호나 출처 번호가 아닌 표시)"""
    valid = {x for x in TAG.findall(bundle) if ID.match(x)}
    used = TAG.findall(answer or '')
    ok = [x for x in used if x in valid]
    bad = sorted({x for x in used if x not in valid and (ID.match(x) or re.match(r'^(CQ\d|근거\s*\d|원칙|자료에 없음|출처)', x))})
    return ok, bad, valid


def answer_llm(question, bundle):
    msgs = [{'role': 'system', 'content': ANSWER_PROMPT}, {'role': 'user', 'content': bundle}]
    ans = chat(msgs, max_tokens=2500)
    ok, bad, valid = cite_check(ans, bundle)
    LAST_CITE.clear(); LAST_CITE.update({'retry': False, 'bad_first': bad, 'n_ok_first': len(ok)})
    if bad or (valid and not ok):   # 출처 번호가 아닌 표시를 썼거나 출처 번호가 하나도 없으면 한 번 다시 쓰게 한다
        why = ('다음 표시는 근거 묶음의 출처 번호가 아닙니다: %s. ' % ', '.join('[%s]' % b for b in bad)) if bad else '사실 문장에 출처 번호가 없습니다. '
        msgs += [{'role': 'assistant', 'content': ans},
                 {'role': 'user', 'content': why + '출처 번호는 근거 묶음에서 항목 앞에 붙은 대괄호 번호만 씁니다. 구역 이름(CQ1, 근거 1), "원칙", "자료에 없음"은 대괄호에 넣지 않습니다. '
                                                   '출처 번호를 붙일 수 없는 문장은 근거 부분에서 빼거나 "자료에 없음"이라고 쓰세요. 같은 형식으로 답변 전체를 다시 쓰세요.'}]
        ans2 = chat(msgs, max_tokens=2500)
        ok2, bad2, _ = cite_check(ans2, bundle)
        LAST_CITE.update({'retry': True, 'bad_final': bad2, 'n_ok_final': len(ok2)})
        if len(bad2) < len(bad) or (ok2 and not ok):
            ans = ans2
    return ans


def mock(examples):
    by_q = {e['question']: e for e in examples}

    def i(q):
        e = by_q.get(q)
        j = {k_: v_ for k_, v_ in e.items() if k_ != 'question'} if e else None
        return '[MOCK 의도: 예시 파일에서 가져옴]', j

    return i, (lambda q, b: '[MOCK 답변: LLM이 호출되지 않았음. 근거 묶음 길이 %d자]' % len(b))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--question'); ap.add_argument('--questions-file'); ap.add_argument('--format', default='tagged', choices=['tagged'])
    ap.add_argument('--mock', action='store_true'); ap.add_argument('--no-answer', action='store_true', help='의도·검색·근거 묶음까지만 실행')
    a = ap.parse_args()
    qs = [{'id': 'q1', 'question': a.question}] if a.question else json.load(open(a.questions_file, encoding='utf-8'))
    qs = [dict(q, id=q.get('id', 'q%d' % (n + 1))) for n, q in enumerate(qs)]
    f_int, f_ans = intent_llm, answer_llm
    if a.mock:
        f_int, f_ans = mock(json.load(open(os.path.join(R5, 'examples_requests.json'), encoding='utf-8')))
    run_dir = os.path.join(R5, 'runs', datetime.now().strftime('%Y%m%d_%H%M%S') + ('_mock' if a.mock else '')); os.makedirs(run_dir)
    for q in qs:
        t0 = time.time(); tr = {'id': q['id'], 'question': q['question'], 'format': a.format, 'mock': a.mock}
        raw, j = f_int(q['question']); tr['intent_raw'], tr['intent_json'] = raw, j
        res = (r9.run(j) if j.get('intent') else {'status': 'refused', 'reason': j.get('reason', '의도 없음')}) if j else {'status': 'refused', 'reason': '의도 JSON을 얻지 못함'}
        tr['retrieval_status'] = res.get('status'); tr['retrieval_reason'] = res.get('reason')
        bundle = r10.build(res, q['question']); tr['bundle'] = bundle
        if not a.no_answer:
            tr['answer'] = f_ans(q['question'], bundle)
        tr['seconds'] = round(time.time() - t0, 1)
        json.dump(res, open(os.path.join(run_dir, q['id'] + '_retrieval.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
        json.dump(tr, open(os.path.join(run_dir, q['id'] + '_trace.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('[%s] %s -> %s (%s) %.1fs' % (q['id'], q['question'][:40], (j or {}).get('intent'), res.get('status'), tr['seconds']))
        if not a.no_answer:
            print('   ', (tr['answer'] or '')[:200].replace('\n', ' '))
    print('저장:', run_dir)


if __name__ == '__main__':
    main()
