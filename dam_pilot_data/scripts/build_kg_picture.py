#!/usr/bin/env python3
"""KG 전체(kgv4의 Entity와 관계 전부)를 한 장의 그림(SVG)으로 그린다. 댐마다 한 묶음이고, 안쪽부터 댐, 수문·기상 상태와 운영기준, 방류 승인, 운영행위, 근거 순서로 둔다.
사용: python3 build_kg_picture.py <출력.svg>   (PNG는 브라우저로 SVG를 열어 화면을 찍어 만든다)"""
import csv, math, os, sys, collections
N = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '03_normalized')
rd = lambda f: list(csv.DictReader(open(os.path.join(N, f), encoding='utf-8-sig')))
ent = {e['entity_id']: e for e in rd('kgv4_entities.csv')}; rel = rd('kgv4_relations.csv')
COL = {'Dam': '#003B71', 'HydrometeorologicalState': '#2E9E8F', 'Criterion': '#C55A11', 'Approval': '#0070C0', 'Operation': '#7B5EA7', 'EvidenceSource': '#9AA5B1'}
R = {'Dam': 15, 'HydrometeorologicalState': 6, 'Criterion': 8, 'Approval': 6, 'Operation': 5.5, 'EvidenceSource': 4}
dams = [e for e, v in ent.items() if v['class'] == 'Dam']
dam_of = {}
for r in rel:
    if r['relation'] in ('concernsDam', 'performedOnDam', 'appliesToDam'): dam_of[r['subject']] = r['object']
    if r['relation'] == 'hasHydrometeorologicalState': dam_of[r['object']] = r['subject']
auth = collections.defaultdict(list)
for r in rel:
    if r['relation'] == 'authorizes': auth[r['subject']].append(r['object'])
evs = collections.defaultdict(set)
for r in rel:
    if r['relation'] == 'supportedBy': evs[r['object']].add(r['subject'])
W, H = 2600, 760; CW = W / 4; pos = {}
order = sorted(dams, key=lambda d: -sum(1 for x in dam_of.values() if x == d))
for i, d in enumerate(order):
    cx, cy = CW * (i + .5), H / 2 + 10; pos[d] = (cx, cy)
    inner = sorted([e for e, dd in dam_of.items() if dd == d and ent[e]['class'] in ('HydrometeorologicalState', 'Criterion')])
    for k, e in enumerate(inner):
        a = -math.pi / 2 + 2 * math.pi * k / max(len(inner), 1); pos[e] = (cx + 62 * math.cos(a), cy + 62 * math.sin(a))
    aps = sorted([e for e, dd in dam_of.items() if dd == d and ent[e]['class'] == 'Approval'], key=lambda x: int(x.split(':')[1]))
    for k, a_ in enumerate(aps):
        a = -math.pi / 2 + 2 * math.pi * (k + .5) / len(aps); pos[a_] = (cx + 150 * math.cos(a), cy + 150 * math.sin(a))
        ops = auth.get(a_, [])
        for j, o in enumerate(ops):
            if o in pos: continue
            b = a + (j - (len(ops) - 1) / 2) * 0.075; pos[o] = (cx + 215 * math.cos(b), cy + 215 * math.sin(b))
    for o in [e for e, dd in dam_of.items() if dd == d and ent[e]['class'] == 'Operation' and e not in pos]:
        pos[o] = (cx, cy + 215)
for e, subs in evs.items():   # 근거: 이어진 Entity들의 바깥쪽. 여러 댐에 걸친 근거는 위쪽 가운데
    ds = {dam_of.get(s) for s in subs}
    pts = [pos[s] for s in subs if s in pos]
    if len(ds) == 1 and None not in ds:
        cx, cy = pos[list(ds)[0]]; mx = sum(p[0] for p in pts) / len(pts); my = sum(p[1] for p in pts) / len(pts)
        a = math.atan2(my - cy, mx - cx); rr = 285 if any(ent[s]['class'] in ('Approval', 'Operation') for s in subs) else 105
        pos[e] = (cx + rr * math.cos(a), cy + rr * math.sin(a))
    else:
        k = sorted(x for x in evs if len({dam_of.get(s) for s in evs[x]}) != 1).index(e); pos[e] = (W / 2 - 60 + 120 * k, 40)
o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d"><rect width="100%%" height="100%%" fill="white"/>' % (W, H, W, H)]
for r in rel:
    if r['subject'] in pos and r['object'] in pos:
        (x1, y1), (x2, y2) = pos[r['subject']], pos[r['object']]
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%s" opacity="%s"/>' % (x1, y1, x2, y2, '#8FA3BA', 1.5, 0.85 if r['relation'] != 'supportedBy' else 0.6))
for e, (x, y) in sorted(pos.items(), key=lambda z: R[ent[z[0]]['class']]):
    c = ent[e]['class']; o.append('<circle cx="%.1f" cy="%.1f" r="%s" fill="%s" stroke="white" stroke-width="1.2"/>' % (x, y, R[c], COL[c]))
for d in order:
    x, y = pos[d]; o.append('<text x="%.1f" y="%.1f" font-family="KoPubWorld돋움체 Medium, NanumGothic, sans-serif" font-size="30" font-weight="700" fill="#003B71" text-anchor="middle">%s</text>' % (x, H - 22, ent[d]['label']))
o.append('</svg>'); open(sys.argv[1], 'w', encoding='utf-8').write('\n'.join(o))
print('nodes', len(pos), 'of', len(ent), 'edges', sum(1 for r in rel if r['subject'] in pos and r['object'] in pos), 'of', len(rel))
