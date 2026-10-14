#!/usr/bin/env python3
"""측정자료 저장소: K-water MyWater 시간자료(4개 댐 × 6개 변수). KG에는 값을 넣지 않고, 조회 키(stationCode + 시각 라벨)로 읽는다.
파일 두 개(처음 받은 자료 hydr_H_wide, 승인 기간에 맞춰 받은 자료 hydr_H_aligned_wide)를 합친 것이며, 같은 (댐, 시각)이 겹치면 처음 받은 값을 쓴다.
시각 라벨 SDATE 'YYYYMMDDHH'(HH=01..24)는 24시를 다음날 00시로 읽는다(라벨의 시각 의미는 미확인, ±1시간).
"""
import csv, gzip, os
from datetime import datetime, timedelta

N = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '03_normalized')
CODES = {'1003110': '충주댐', '1012110': '소양강댐', '1006110': '횡성댐', '1001210': '광동댐'}
VARS = {'수위': 'DATA1_수위(EL.m)', '저수량': 'DATA2_저수량(MCM)', '강우량': 'DATA3_강우량(mm)',
        '유입량': 'DATA4_유입량(CMS)', '총방류량': 'DATA6_총방류량(CMS)', '저수율': 'DATA7_저수율(%)'}
UNITS = {'수위': 'EL.m', '저수량': 'MCM', '강우량': 'mm', '유입량': 'CMS', '총방류량': 'CMS', '저수율': '%'}


def label_time(s):
    return datetime(int(s[:4]), int(s[4:6]), int(s[6:8])) + timedelta(hours=int(s[8:10]))


class Store:
    def __init__(self):
        self.d = {}
        for f in ('kwater_mywater_hydr_H_wide.csv.gz', 'kwater_mywater_hydr_H_aligned_wide.csv.gz'):
            for r in csv.DictReader(gzip.open(os.path.join(N, f), 'rt', encoding='utf-8-sig')):
                if r['DAM_CD'] in CODES:
                    self.d.setdefault((r['DAM_CD'], label_time(r['SDATE_raw'])), {v: r[c] for v, c in VARS.items()})

    def latest(self, code):
        """저장된 가장 최근 시각."""
        return max(t for (c, t) in self.d if c == code)

    def at(self, code, t):
        """시각 t의 값. 정각이면 그 시각 1행, 아니면 t를 감싸는 앞뒤 정시 2행. 없는 시각은 건너뛴다. 반환: [(시각, 값 dict)]"""
        if t.minute == 0 and t.second == 0:
            ts = [t]
        else:
            lo = t.replace(minute=0, second=0, microsecond=0)
            ts = [lo, lo + timedelta(hours=1)]
        return [(x, self.d[(code, x)]) for x in ts if (code, x) in self.d]

    def span(self, code, start, end):
        """[start, end) 안의 정시 행."""
        t = start.replace(minute=0, second=0, microsecond=0)
        if t < start:
            t += timedelta(hours=1)
        out = []
        while t < end:
            if (code, t) in self.d:
                out.append((t, self.d[(code, t)]))
            t += timedelta(hours=1)
        return out
