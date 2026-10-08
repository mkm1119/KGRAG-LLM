#!/usr/bin/env python3
"""답변의 숫자·ID가 근거 묶음에 있는지 검사한다(근거 외 주장 탐지의 1차 점검). 의미 판단은 사람이 한다."""
import re, os
N = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '03_normalized')
def split(t):
    out = {}
    for m in re.finditer(r'### (Q\d+)\s*(.*?)(?=\n### |\Z)', t, flags=re.S):
        out[m.group(1)] = m.group(2)
    return out
b = split(open(os.path.join(N, 'step3b_bundles.md'), encoding='utf-8').read())
a = split(open(os.path.join(N, 'step3b_answers.md'), encoding='utf-8').read())
common = re.search(r'공통 유의:.*', open(os.path.join(N, 'step3b_bundles.md'), encoding='utf-8').read()).group(0)
bad = 0
for q, ans in a.items():
    src = b.get(q, '') + common
    nums = [n for n in re.findall(r'\d+(?:\.\d+)?', ans) if '.' in n or len(n) >= 2]
    ids = [i.rstrip('.') for i in re.findall(r'EVI:LAW:별표\d|(?:APR|OPR|EVI|CRI|HMS|DAM):[0-9A-Za-z:\.\-]+', ans)]
    miss = [n for n in nums if n not in src]
    missid = [i for i in ids if i not in src]
    print(q, '숫자', len(nums), '근거 없음', miss, '| ID', len(ids), '근거 없음', missid)
    bad += len(miss) + len(missid)
print('근거 묶음에 없는 숫자/ID 총', bad)
