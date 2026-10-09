#!/usr/bin/env python3
"""STEP 11: 질문 -> (LLM) 의도·값 추출 -> (프로그램) Cypher 템플릿·Neo4j·측정/문서 저장소·유클리드 거리 -> 근거 묶음 -> (LLM) 답변.
LLM은 OpenAI 호환 API(vLLM, Ollama, llama.cpp 서버 등)에 연결한다. stdlib만 사용.

환경변수: LLM_BASE_URL(예: http://localhost:8000/v1), LLM_MODEL(예: Qwen/Qwen2.5-7B-Instruct), LLM_API_KEY(선택), NEO4J_HOME
사용:
  python3 scripts/step11_pipeline.py --question "2020년 8월 충주댐 운영행위는?"
  python3 scripts/step11_pipeline.py --questions-file 05_retrieval/questions_example.json --format tagged
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
    m = re.search(r'\{.*\}', txt, flags=re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def intent_llm(question):
    raw = chat([{'role': 'system', 'content': INTENT_PROMPT}, {'role': 'user', 'content': question}])
    j = parse_json(raw)
    if j is None:
        raw2 = chat([{'role': 'system', 'content': INTENT_PROMPT}, {'role': 'user', 'content': question},
                     {'role': 'assistant', 'content': raw}, {'role': 'user', 'content': 'JSON 하나만 다시 출력하세요.'}])
        raw, j = raw + '\n--- 재시도 ---\n' + raw2, parse_json(raw2)
    return raw, j


def answer_llm(question, bundle):
    return chat([{'role': 'system', 'content': ANSWER_PROMPT}, {'role': 'user', 'content': '질문: %s\n\n%s' % (question, bundle)}], max_tokens=2000)


def mock(examples):
    by_q = {e['question']: e for e in examples}

    def i(q):
        e = by_q.get(q)
        j = {'intent': e['intent'], 'slots': e['slots']} if e else None
        return '[MOCK 의도: 예시 파일에서 가져옴]', j

    return i, (lambda q, b: '[MOCK 답변: LLM이 호출되지 않았음. 근거 묶음 길이 %d자]' % len(b))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--question'); ap.add_argument('--questions-file'); ap.add_argument('--format', default='tagged', choices=['tagged', 'json'])
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
        res = r9.run(j) if j else {'status': 'refused', 'reason': '의도 JSON을 얻지 못함'}
        tr['retrieval_status'] = res.get('status'); tr['retrieval_reason'] = res.get('reason')
        bundle = r10.build(res, a.format); tr['bundle'] = bundle
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
