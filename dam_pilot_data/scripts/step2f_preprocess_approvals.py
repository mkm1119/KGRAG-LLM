#!/usr/bin/env python3
"""STEP 2F: 승인 CSV 전처리. 값이 모두 같은 중복 행(순차번호만 다름)은 첫 행만 남기고 나머지를 제거한다. stdlib만 사용.
원본(approval_records_hrfco_raw_fields.csv)은 바꾸지 않는다. 제거한 행은 로그에 남긴다.
출력: 03_normalized/approval_records_clean.csv, approval_preprocess_log.csv
"""
import csv, os, collections
N = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '03_normalized')
rows = list(csv.DictReader(open(os.path.join(N, 'approval_records_hrfco_raw_fields.csv'), encoding='utf-8-sig')))
KEY = ('관측소코드', '승인년월일시분', '방류시작시간', '접수방류량', '접수일자', '비고')
seen, keep, log = {}, [], []
for r in rows:
    k = tuple(r[c].strip() for c in KEY)
    if k in seen:
        log.append({'removed_seq': r['순차번호'], 'kept_seq': seen[k], '관측소명': r['관측소명'], '승인일': r['승인년월일시분'], '방류시작시간': r['방류시작시간'],
                    'reason': '값이 모두 같은 중복 행(순차번호만 다름): 첫 행만 유지'})
    else:
        seen[k] = r['순차번호']; keep.append(r)
with open(os.path.join(N, 'approval_records_clean.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(keep)
cols = ['removed_seq', 'kept_seq', '관측소명', '승인일', '방류시작시간', 'reason']
with open(os.path.join(N, 'approval_preprocess_log.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(log)
print('전체', len(rows), '유지', len(keep), '제거', len(log), dict(collections.Counter(x['관측소명'] for x in log)))
