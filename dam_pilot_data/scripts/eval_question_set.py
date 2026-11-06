#!/usr/bin/env python3
"""질문 세트를 지금 구조로 돌려 검토표를 만든다. stdlib만 사용.

  --mode gold : LLM 없이, 사람이 정한 정답 의도(gold)로 KG 검색과 근거 묶음까지 실행 (검색·KG 범위 점검)
  --mode llm  : 서버에서 실제 파이프라인 전체 실행(의도 추출 LLM → 검색 → 근거 묶음 → 답변 LLM). gold와 의도를 비교
환경변수는 step11과 같다(NEO4J_HOME, llm 모드는 LLM_BASE_URL 등).
결과: 05_retrieval/eval_runs/<시각>_<모드>/ 에 질문별 JSON과 review.md(검토표)
"""
import argparse, importlib.util, json, os, time
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__)); R5 = os.path.join(HERE, '..', '05_retrieval')
s = importlib.util.spec_from_file_location('p11', os.path.join(HERE, 'step11_pipeline.py')); P = importlib.util.module_from_spec(s); s.loader.exec_module(P)


def norm_period(p):
    return json.dumps(p, sort_keys=True, ensure_ascii=False) if isinstance(p, dict) else str(p)


def found(res):
    if res.get('status') != 'ok':
        return '거절: ' + str(res.get('reason'))
    f = []
    if 'state_now' in res: f.append('현재 %s(%d행)' % (res['state_now']['time'], len(res['state_now']['rows'])))
    if 'criteria' in res: f.append('기준 %d' % len(res['criteria']))
    if 'operations' in res: f.append('운영 %d' % len({o['op'] for o in res['operations']}))
    if 'approvals' in res: f.append('승인 %d' % len(res['approvals']))
    if 'state_at_operations' in res: f.append('운영시각 측정 %d' % sum(len(x['rows']) for x in res['state_at_operations']))
    if 'state_period' in res: f.append('기간 측정 %d행' % len(res['state_period']))
    if 'evidence' in res: f.append('출처 %d' % len({e['ev'] for v in res['evidence'].values() for e in v}))
    return ', '.join(f) or '(없음)'


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--mode', choices=['gold', 'llm'], default='gold')
    ap.add_argument('--file', default=os.path.join(R5, 'question_set_v1.json')); ap.add_argument('--only', help='expect 값만(answer_now 등)')
    a = ap.parse_args()
    qs = json.load(open(a.file, encoding='utf-8'))
    if a.only:
        qs = [q for q in qs if q['expect'] == a.only]
    run = os.path.join(R5, 'eval_runs', datetime.now().strftime('%Y%m%d_%H%M%S') + '_' + a.mode); os.makedirs(run)
    rows = []
    for q in qs:
        t0 = time.time(); r = dict(q)
        if a.mode == 'gold':
            if not q['gold']:
                r['result'] = '(gold 없음: %s)' % (q['extension'] or '범위 밖'); rows.append(r); continue
            j = q['gold']
        else:
            try:
                raw, j = P.intent_llm(q['question']); r['intent_raw'] = raw
            except Exception as e:
                raw, j = None, None; r['error'] = '의도 추출 오류: %s: %s' % (type(e).__name__, e)
        r['intent_json'] = j
        try:
            res = P.r9.run(j) if j and j.get('intent') else {'status': 'refused', 'reason': (j or {}).get('reason', '의도 없음')}
            bundle = P.r10.build(res, q['question'])
            r['result'] = found(res); r['bundle_chars'] = len(bundle); r['bundle'] = bundle
            if a.mode == 'llm':
                r['answer'] = P.answer_llm(q['question'], bundle) if res.get('status') == 'ok' else None
        except Exception as e:   # 한 질문의 오류로 전체가 멈추지 않게 기록하고 넘어간다 (예: 근거 묶음이 모델 한도를 넘어 400)
            body = ''
            if hasattr(e, 'read'):
                try:
                    body = e.read().decode('utf-8', 'replace')[:500]
                except Exception:
                    pass
            r['error'] = '%s: %s %s' % (type(e).__name__, e, body)
            r['result'] = '오류: %s (근거 묶음 %s자)' % (type(e).__name__, r.get('bundle_chars', '?'))
        if a.mode == 'llm':
            g = q['gold']
            r['intent_match'] = (g is None and not (j or {}).get('intent')) or (g is not None and j is not None and sorted(j.get('intent') or []) == sorted(g['intent'])
                                and j.get('dam') == g.get('dam') and norm_period(j.get('period')) == norm_period(g.get('period'))
                                and j.get('target') == g.get('target'))
        r['seconds'] = round(time.time() - t0, 1)
        json.dump(r, open(os.path.join(run, q['id'] + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
        rows.append(r); print(q['id'], q['expect'], r['result'][:80], r.get('bundle_chars', ''))
    md = ['# 질문 세트 검토 (%s 모드, %s)' % (a.mode, datetime.now().strftime('%Y-%m-%d %H:%M')), '',
          '| id | 태스크 | 질문 | 기대 | 의도 | 찾은 근거 | 묶음 글자수 |' + (' 의도 일치 |' if a.mode == 'llm' else ''), '|---|---|---|---|---|---|---|' + ('---|' if a.mode == 'llm' else '')]
    for r in rows:
        j = r.get('intent_json') or {}
        it = '%s / %s / %s' % (','.join(j.get('intent') or []) or '-', j.get('dam') or '-', norm_period(j.get('period')) if j.get('period') else '-') if j else '-'
        md.append('| %s | %s | %s | %s%s | %s | %s | %s |' % (r['id'], r['task'], r['question'], r['expect'], ' (%s)' % r['extension'] if r.get('extension') else '', it, r['result'], r.get('bundle_chars', ''))
                  + (' %s |' % ('O' if r.get('intent_match') else 'X') if a.mode == 'llm' else ''))
    open(os.path.join(run, 'review.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print('저장:', run)


if __name__ == '__main__':
    main()
