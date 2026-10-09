#!/usr/bin/env python3
"""승인 기간에 맞춘 시간 단위 측정 자료 수집(K-water MyWater getHydr, param1=H).
기존 수집(2021년 이후 + 승인 연계 24건 창)이 승인 기간(2010~2021-07)과 어긋나 있어, 5개 댐의 승인 기간을 연속으로 채운다.
원응답은 그대로 저장하고, 이미 받은 파일은 건너뛴다(재개 가능). 요청은 한 번에 1건, 요청 사이 1초 대기.
출력: 01_raw/KWater/mywater_aligned/hydr/H/<DAM_CD>/<시작>_<끝>.json, 02_metadata/mywater_aligned_manifest.csv"""
import csv, datetime as dt, hashlib, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mywater_client import post, BASE

ROOT = '01_raw/KWater/mywater_aligned/hydr/H'
MAN = '02_metadata/mywater_aligned_manifest.csv'
SPANS = {'1006110': ('2010-08-01', '2020-12-30'),   # 횡성: 승인 2010-09-10~2020-08-29
         '1003110': ('2010-08-01', '2020-12-30'),   # 충주: 2010-09-22~2020-09-03
         '1003611': ('2011-04-01', '2012-10-31'),   # 충주조정지: 2011-05-01~2012-08-30
         '1012110': ('2011-06-01', '2020-12-30'),   # 소양강: 2011-07-27~2020-09-03
         '1001210': ('2016-06-01', '2020-12-30')}   # 광동: 2016-07-04~2021-07-03 (2020-12-31 이후는 기존 수집)


def windows(s, e, span=29):
    a = dt.date.fromisoformat(s); b = dt.date.fromisoformat(e)
    while a <= b:
        z = min(a + dt.timedelta(days=span), b)
        yield a.isoformat(), z.isoformat()
        a = z + dt.timedelta(days=1)


def main():
    new = not os.path.exists(MAN)
    mf = open(MAN, 'a', newline='', encoding='utf-8'); w = csv.writer(mf)
    if new:
        w.writerow(['retrieval_time_utc', 'endpoint', 'query_parameters_json', 'file_name', 'bytes', 'sha256', 'n_rows', 'errorChk'])
    todo = [(d, a, b) for d, (s, e) in SPANS.items() for a, b in windows(s, e)]
    print('requests', len(todo), flush=True)
    done = fail = 0
    for i, (d, a, b) in enumerate(todo, 1):
        fn = '%s/%s/%s_%s.json' % (ROOT, d, a, b)
        if os.path.exists(fn):
            continue
        p = {'mode': 'getHydr', 'damCd': d, 'param1': 'H', 'startDate': a, 'endDate': b, 'page': ''}
        t, raw, j = post(p)
        if raw is None:
            fail += 1; print('FAIL', d, a, b, j, flush=True); time.sleep(3); continue
        os.makedirs(os.path.dirname(fn), exist_ok=True); open(fn, 'wb').write(raw)
        w.writerow([t, BASE, json.dumps(p, ensure_ascii=False), fn, len(raw), hashlib.sha256(raw).hexdigest(), len(j.get('list') or []), j.get('errorChk')]); mf.flush()
        done += 1
        if done % 25 == 0:
            print('progress', done, '/', len(todo), 'fail', fail, flush=True)
        time.sleep(1.0)
    print('DONE', done, 'fail', fail, flush=True)


if __name__ == '__main__':
    main()
