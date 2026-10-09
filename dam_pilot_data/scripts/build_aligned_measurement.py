#!/usr/bin/env python3
"""승인 기간에 맞춰 새로 받은 MyWater 시간자료(JSON 원응답)를 기존 hydr_H_wide와 같은 열 구조의 표로 정규화한다.
값은 원응답 그대로 옮기고 변환·보간하지 않는다. 출력: 03_normalized/kwater_mywater_hydr_H_aligned_wide.csv.gz"""
import csv, glob, gzip, json, os

ROOT = '01_raw/KWater/mywater_aligned/hydr/H'
OUT = '03_normalized/kwater_mywater_hydr_H_aligned_wide.csv.gz'
HEAD = ['source_file', 'retrieval_time_utc', 'param1_resolution', 'DAM_CD', 'SDATE_raw', 'DATA1_수위(EL.m)', 'DATA2_저수량(MCM)', 'DATA3_강우량(mm)',
        'DATA4_유입량(CMS)', 'DATA5_source_label_unknown', 'DATA6_총방류량(CMS)', 'DATA7_저수율(%)']
rt = {}
for r in csv.DictReader(open('02_metadata/mywater_aligned_manifest.csv', encoding='utf-8')):
    rt[r['file_name']] = r['retrieval_time_utc']
n = 0; seen = set(); dup = 0
with gzip.open(OUT, 'wt', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f); w.writerow(HEAD)
    for fn in sorted(glob.glob(ROOT + '/*/*.json')):
        j = json.load(open(fn, encoding='utf-8'))
        for x in j.get('list') or []:
            k = (x.get('DAM_CD'), x.get('SDATE'))
            if k in seen:
                dup += 1
                continue
            seen.add(k)
            w.writerow([fn, rt.get(fn, ''), 'H', x.get('DAM_CD'), x.get('SDATE')] + [('' if x.get('DATA%d' % i) is None else x.get('DATA%d' % i)) for i in range(1, 8)])
            n += 1
print('rows', n, 'duplicate keys skipped', dup)
