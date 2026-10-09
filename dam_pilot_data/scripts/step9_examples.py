#!/usr/bin/env python3
"""예시 요청(05_retrieval/examples_requests.json)을 step9_retrieve.run으로 실행해 결과 요약을 05_retrieval/examples_results.md에 쓴다. 의도 JSON은 사람이 채운 것이며 LLM 분류 결과가 아니다."""
import importlib.util, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); R5 = os.path.join(HERE, '..', '05_retrieval')
s = importlib.util.spec_from_file_location('r9', os.path.join(HERE, 'step9_retrieve.py')); r9 = importlib.util.module_from_spec(s); s.loader.exec_module(r9)
out = ['# 예시 요청 실행 결과 (의도 JSON은 사람이 채움, LLM 분류 아님)\n']
for i, q in enumerate(json.load(open(os.path.join(R5, 'examples_requests.json'), encoding='utf-8')), 1):
    res = r9.run({'intent': q['intent'], 'slots': q['slots']})
    brief = {k: (len(v) if isinstance(v, list) else v) for k, v in res.items() if k in ('status', 'reason', 'operations', 'approvals', 'criterion', 'evidence', 'cases')}
    if 'state' in res: brief['state_rows'] = res['state']['n_rows']
    out.append('## %d. %s\n- 질문: %s\n- 요청: `%s`\n- 결과 요약: `%s`\n' % (i, q['intent'], q['question'], json.dumps({'intent': q['intent'], 'slots': q['slots']}, ensure_ascii=False), json.dumps(brief, ensure_ascii=False)))
    json.dump(res, open(os.path.join(R5, 'result_%02d.json' % i), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
open(os.path.join(R5, 'examples_results.md'), 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
