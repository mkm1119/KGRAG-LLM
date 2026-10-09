#!/usr/bin/env python3
"""STEP 2E: Operation(승인 비고에서 분류한 행위)을 측정 총방류량과 대조해 Operation 속성으로 덧붙인다. stdlib만 사용.
규칙: 증가·초기·점진 계열은 시작 후 6시간 내 최대 총방류량이 시작 직전보다 0.5 CMS 넘게 커지면 '일치', 감소·종료 계열은 최소값이 0.5 CMS 넘게 작아지면 '일치'.
방향이 없는 행위(방류, 탄력적 방류, 수문조작)는 '판정불가(방향 없음)', 측정 창이 없으면 '측정없음'. 일치는 방향 확인이며 행위 수행의 직접 증명은 아니다(유입량 변화로도 움직일 수 있음).
입력: operation_from_remarks_5dams.csv, kgv3_properties.csv (step2d 이후 실행) / 출력: operation_measured_check.csv, kgv3_properties.csv에 x_ 속성 추가(재실행해도 중복 없음)
"""
import collections, csv, importlib.util, os

HERE = os.path.dirname(os.path.abspath(__file__))
N = os.path.join(HERE, '..', '03_normalized')
spec = importlib.util.spec_from_file_location('r3b', os.path.join(HERE, 'step3b_retrieval.py'))
r3b = importlib.util.module_from_spec(spec); spec.loader.exec_module(r3b)
ms = r3b.Measurement()
name2code = {v.replace('댐', ''): k for k, v in r3b.CODES.items()}
UP, DN, THR = ('증가방류', '초기방류', '점진·점증방류'), ('감소방류', '방류종료'), 0.5

out, k = [], collections.Counter()
for o in r3b.rd('operation_from_remarks_5dams.csv'):
    if o['operation_created'] != 'Y':
        continue
    k[o['순차번호']] += 1
    oid = 'OPR:%s:%d' % (o['순차번호'], k[o['순차번호']])
    typ = o['operationType']
    w = ms.window(name2code[o['댐']], r3b.to_dt(o['operationTime']), before=3, after=6)
    val = lambda x: r3b.fnum(x['총방류량'])
    pre = [val(r) for h, _, r in w if h <= 0 and val(r) is not None]
    post = [val(r) for h, _, r in w if h >= 1 and val(r) is not None]
    if not pre or not post:
        res, b, mx, mn = '측정없음', '', '', ''
    else:
        b, mx, mn = pre[-1], max(post), min(post)
        if typ in UP:
            res = '일치' if mx > b + THR else '불일치'
        elif typ in DN:
            res = '일치' if mn < b - THR else '불일치'
        else:
            res = '판정불가(방향 없음)'
    out.append({'operation': oid, 'type': typ, 'result': res, 'before': b, 'after_max': mx, 'after_min': mn})
with open(os.path.join(N, 'operation_measured_check.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

pp = os.path.join(N, 'kgv3_properties.csv')
rows = list(csv.reader(open(pp, encoding='utf-8-sig')))
rows = [r for r in rows if r[1] not in ('x_measured_check', 'x_measured_before', 'x_measured_after_max', 'x_measured_after_min')]
for r in out:
    rows += [[r['operation'], 'x_measured_check', r['result'], 'variant'], [r['operation'], 'x_measured_before', r['before'], 'variant'],
             [r['operation'], 'x_measured_after_max', r['after_max'], 'variant'], [r['operation'], 'x_measured_after_min', r['after_min'], 'variant']]
with open(pp, 'w', newline='', encoding='utf-8-sig') as f:
    csv.writer(f).writerows(rows)
print(collections.Counter(r['result'] for r in out))
