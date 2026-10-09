#!/usr/bin/env python3
"""의도 분류 채점: 실행 폴더(05_retrieval/runs/<시각>/)의 trace와 질문 파일(expected_intent, expected_dam)을 비교한다. 사용: python3 scripts/step12_score_intents.py <실행 폴더> <질문 파일>"""
import json, os, sys
run, qf = sys.argv[1], sys.argv[2]
DAMS = {'충주': '충주댐', '충주댐': '충주댐', '소양강': '소양강댐', '소양강댐': '소양강댐', '횡성': '횡성댐', '횡성댐': '횡성댐', '광동': '광동댐', '광동댐': '광동댐'}
n = ok_i = ok_d = nd = 0
for q in json.load(open(qf, encoding='utf-8')):
    f = os.path.join(run, q['id'] + '_trace.json')
    if not os.path.exists(f):
        continue
    t = json.load(open(f, encoding='utf-8')); j = t.get('intent_json') or {}; sl = j.get('slots', {})
    gi = j.get('intent'); gd = DAMS.get((sl.get('dam') or (sl.get('target') or {}).get('dam')))
    n += 1; ok_i += gi == q['expected_intent']
    if q.get('expected_dam'):
        nd += 1; ok_d += gd == q['expected_dam']
    print('%-4s 의도 %-12s (기대 %-12s) %s | 댐 %s (기대 %s) | 검색 %s' % (q['id'], gi, q['expected_intent'], 'O' if gi == q['expected_intent'] else 'X', gd, q.get('expected_dam'), t.get('retrieval_status')))
print('의도 일치 %d/%d, 댐 일치 %d/%d' % (ok_i, n, ok_d, nd))
