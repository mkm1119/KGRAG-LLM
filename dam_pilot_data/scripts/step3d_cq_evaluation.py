#!/usr/bin/env python3
"""STEP 3D: KG v3 전체를 대상으로 온톨로지 CQ1~CQ6과 통합 질문에 답할 수 있는지 점검한다. stdlib만 사용.
엄격(v1): 온톨로지의 Class 6개와 관계 8개만 사용. 변형(v1.1): Approval–Dam 직접 관계와 규정 규칙(Criterion)을 추가로 사용.
출력: 03_normalized/step3d_cq_matrix.csv, step3d_case_assembly.csv, step3d_similar_cases.csv
"""
import collections, csv, importlib.util, os, re, statistics
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
N = os.path.join(HERE, '..', '03_normalized')
spec = importlib.util.spec_from_file_location('r3b', os.path.join(HERE, 'step3b_retrieval.py'))
r3b = importlib.util.module_from_spec(spec); spec.loader.exec_module(r3b)
rd = r3b.rd

cls, label, P = {}, {}, collections.defaultdict(dict)
for r in rd('kgv3_entities.csv'):
    cls[r['entity_id']], label[r['entity_id']] = r['class'], r['label']
for r in rd('kgv3_properties.csv'):
    P[r['entity_id']][r['property']] = r['value']
REL = rd('kgv3_relations.csv')
chunks = {r['chunk_id']: r for r in rd('kgv3_chunks.csv')}
ms = r3b.Measurement()
CODES = r3b.CODES
ONTO_REL = {'hasHydrometeorologicalState', 'performedOnDam', 'authorizes', 'appliesToDam', 'supportedBy'}


def build(strict):
    out, inv = collections.defaultdict(lambda: collections.defaultdict(list)), collections.defaultdict(lambda: collections.defaultdict(list))
    for r in REL:
        if r['relation'] not in ONTO_REL:
            if strict:
                continue
        if strict and r['origin'] in ('variant', 'general-rule'):
            continue
        if strict and (r['subject'].startswith('CRI:R') or r['object'].startswith('CRI:R')):
            continue
        out[r['subject']][r['relation']].append(r['object'])
        inv[r['object']][r['relation']].append(r['subject'])
    return out, inv


G = {True: build(True), False: build(False)}
dams = sorted(e for e, c in cls.items() if c == 'Dam')
ops = sorted(e for e, c in cls.items() if c == 'Operation')
apps = sorted(e for e, c in cls.items() if c == 'Approval')
code_of = lambda d: d.split(':')[1]
rows = []


def M(cq, dim, strict, variant, detail=''):
    rows.append({'cq': cq, 'item': dim, 'strict_v1': strict, 'variant_v1.1': variant, 'detail': detail})


# ---------- CQ1 현재 상태
latest = {}
for (c, t) in ms.d:
    if c not in latest or t > latest[c]:
        latest[c] = t
for d in dams:
    c = code_of(d)
    vals = ms.d[(c, latest[c])]
    nonnull = sum(1 for v in vals.values() if r3b.fnum(v) is not None)
    hms = G[True][0][d]['hasHydrometeorologicalState']
    M('CQ1', label[d], '상태 %d/6 변수 (기상 = 댐 강우량으로 정의)' % nonnull if len(hms) == 6 and nonnull == 6 else '상태 항목 부족',
      '동일', '기준시점 %s; 수위 %s EL.m, 강우량 %s mm, 유입량 %s CMS, 총방류량 %s CMS; 기온·풍속 등은 범위 밖(ASOS 미수집)' % (latest[c], vals['수위'], vals['강우량'], vals['유입량'], vals['총방류량']))

# ---------- CQ2 과거 상태 (운영행위/승인 시점 기준 창)
def win_n(code, tstr):
    return len(ms.window(code, r3b.to_dt(tstr)))


apv = {r['순차번호']: r for r in rd('approval_records_hrfco_raw_fields.csv') if r['관측소명'] in ('충주', '충주조정지', '소양강', '횡성', '광동')}
codes_by_name = {'충주': '1003110', '충주조정지': '1003611', '소양강': '1012110', '횡성': '1006110', '광동': '1001210'}
by_dam = collections.defaultdict(lambda: [0, 0, 0, 0])
for seq, r in apv.items():
    c = codes_by_name[r['관측소명']]
    n = win_n(c, r['방류시작시간'])
    by_dam[CODES[c]][0] += 1
    by_dam[CODES[c]][1] += 1 if n > 0 else 0
tot = sum(v[0] for v in by_dam.values()); got = sum(v[1] for v in by_dam.values())
M('CQ2', '승인 102건의 방류시작 전후 상태 창', '%d/%d건에서 조회 가능' % (got, tot), '동일', '; '.join('%s %d/%d' % (k, v[1], v[0]) for k, v in sorted(by_dam.items())))
opw = collections.defaultdict(lambda: [0, 0])
for o in ops:
    d = G[True][0][o]['performedOnDam'][0]
    n = win_n(code_of(d), P[o]['operationTime'].replace('T', ' '))
    opw[label[d]][0] += 1
    opw[label[d]][1] += 1 if n > 0 else 0
M('CQ2', '운영행위 69건의 상태 창', '%d/%d건에서 조회 가능' % (sum(v[1] for v in opw.values()), len(ops)), '동일', '; '.join('%s %d/%d' % (k, v[1], v[0]) for k, v in sorted(opw.items())))
M('CQ2', '임의 과거 시점(연속 구간)', '5개 댐 모두 시간 단위 조회 가능', '동일', '; '.join('%s %s~%s' % (CODES[c], v[0].date(), v[1].date()) for c, v in sorted(ms.cover.items())))

# ---------- CQ3 과거 운영행위
sel = collections.Counter(P[o]['operationType'] for o in ops)
M('CQ3', '운영행위 개체', '%d개 (승인 %d/%d건에서 생성)' % (len(ops), len({G[True][1][o]['authorizes'][0] for o in ops}), len(apps)), '동일', '유형: ' + ', '.join('%s %d' % kv for kv in sel.most_common()))
cc = collections.Counter(P[o].get('x_measured_check', '속성없음') for o in ops)
M('CQ3', '측정 대조(행위 방향 vs 총방류량 변화)', '속성 없음(변형 속성)', '; '.join('%s %d' % kv for kv in cc.most_common()), '시작 전후 총방류량, 임계 0.5 CMS; 일치는 방향 확인이며 수행의 직접 증명 아님')

# ---------- CQ4 과거 방류 승인
def reach(strict):
    out, inv = G[strict]
    s = set()
    for d in dams:
        for o in inv[d]['performedOnDam']:
            for a in inv[o]['authorizes']:
                s.add(a)
        for a in inv[d]['concernsDam']:
            s.add(a)
    return s


ra, rb = reach(True), reach(False)
M('CQ4', '댐에서 도달 가능한 승인', '%d/%d건' % (len(ra), len(apps)), '%d/%d건' % (len(rb), len(apps)), 'v1.1은 Approval–Dam 직접 관계(concernsDam) 사용')
period = sum(1 for a in apps if re.search(r'방류기간|\d+/\d+\s*\d+:\d+\s*~|종료|~', P[a]['approvalContent']))
M('CQ4', '승인 사항 충족(시행령 제48조: 방류량·시작 시각·방류기간)', '방류량 %d/%d, 시작 시각 %d/%d, 방류기간 %d/%d (비고에서)' % (len(apps), len(apps), len(apps), len(apps), period, len(apps)), '동일', '승인일은 날짜만 있음; 방류기간은 비고에 일부만 기재')

# ---------- CQ5 현재 운영기준
for d in dams:
    s = [c for c in G[True][1][d]['appliesToDam']]
    v = [c for c in G[False][1][d]['appliesToDam']]
    lim = [c for c in s if P[c].get('criterionType') == '홍수기 제한수위']
    hist = len(G[True][0][lim[0]]['supportedBy']) - 1 if lim else 0
    M('CQ5', label[d], '제한수위 %s' % ('; '.join('%s EL.m (연혁 %d개 판 동일)' % (P[c]['criterionValue'], hist) for c in lim) if lim else '없음 (별표3에 미수록)'),
      '제한수위 %d + 규칙 %d개' % (len(lim), len(v) - len(s)), '')

# ---------- CQ6 공식 근거
def resolvable(ev):
    t = P[ev].get('sourceType')
    if t == '승인자료':
        return re.sub(r'\D', '', P[ev]['sourceLocator']) in apv
    if t == '측정자료':
        return re.search(r'DAM_CD=(\d+)', P[ev]['sourceLocator']).group(1) in {c for c, _ in ms.d}
    cid = P[ev].get('x_chunk_id') or ('LAW:별표3' if P[ev]['sourceLocator'] == '별표 3' else '')
    return cid in chunks


for name, ids in [('Approval', apps), ('Operation', ops), ('HydrometeorologicalState', [e for e, c in cls.items() if c == 'HydrometeorologicalState']),
                  ('Criterion(제한수위)', [e for e, c in cls.items() if c == 'Criterion' and not e.startswith('CRI:R')]),
                  ('Criterion(규칙, v1.1)', [e for e, c in cls.items() if c == 'Criterion' and e.startswith('CRI:R')])]:
    g = G[False][0]
    have = [i for i in ids if g[i]['supportedBy']]
    res = [i for i in have if all(resolvable(e) for e in g[i]['supportedBy'])]
    note = '근거가 승인 레코드와 동일(독립 근거 아님)' if name == 'Operation' else ''
    M('CQ6', name, '%d/%d 근거 연결, %d 위치 확인' % (len(have), len(ids), len(res)) if not name.endswith('v1.1)') else '해당 없음', '%d/%d 근거 연결, %d 위치 확인' % (len(have), len(ids), len(res)), note)

# ---------- 통합 질문: 사례 조립
lim_of = {}
for d in dams:
    c = [c for c in G[True][1][d]['appliesToDam'] if P[c].get('criterionType') == '홍수기 제한수위']
    lim_of[d] = float(P[c[0]]['criterionValue']) if c else None


def flood(t):
    return (t.month, t.day) >= (6, 21) and (t.month, t.day) <= (9, 20)


case_rows = []
cnt = collections.Counter()
for o in ops:
    d = G[True][0][o]['performedOnDam'][0]
    c = code_of(d)
    t = r3b.to_dt(P[o]['operationTime'])
    w = ms.window(c, t)
    aps = G[True][1][o]['authorizes']
    lv = [r3b.fnum(r['수위']) for _, _, r in w if r3b.fnum(r['수위']) is not None]
    lim = lim_of[d]
    over = round(max(lv) - lim, 2) if (lv and lim is not None) else ''
    ad = datetime.strptime(P[aps[0]]['approvalTime'], '%Y-%m-%d') if aps else None
    order = '' if ad is None else ('승인일 ≤ 방류시작일' if ad.date() <= t.date() else '방류시작 이후 승인(변경승인 포함 가능)')
    comp_s = bool(w) and bool(aps) and lim is not None
    comp_v = bool(w) and bool(aps)
    cnt['windows'] += bool(w); cnt['comp_strict'] += comp_s; cnt['comp_variant'] += comp_v; cnt['flood'] += flood(t)
    case_rows.append({'operation': o, 'dam': label[d], 'time': P[o]['operationTime'], 'type': P[o]['operationType'], 'window_rows': len(w), 'approvals': ' '.join(aps),
                      'flood_season': 'Y' if flood(t) else 'N', 'level_max_minus_limit_m': over, 'approval_order': order,
                      'measured_check': P[o].get('x_measured_check', ''), 'complete_v1': 'Y' if comp_s else 'N', 'complete_v1.1': 'Y' if comp_v else 'N'})
with open(os.path.join(N, 'step3d_case_assembly.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=list(case_rows[0].keys())); w.writeheader(); w.writerows(case_rows)
M('통합', '운영행위 69건 중 상태 창이 있는 사례', '%d건' % cnt['windows'], '동일', '상태 + 운영행위 + 승인 + 근거를 함께 조립할 수 있는 사례')
M('통합', '제한수위까지 함께 조립되는 사례', '%d건 (충주·소양강·횡성 사례)' % cnt['comp_strict'], '%d건 (규칙 18개 포함)' % cnt['comp_variant'], '')
M('통합', '홍수기에 해당하는 운영행위', '판정 불가(규칙 없음)', '%d/%d건' % (cnt['flood'], len(ops)), '연계운영규정 제2조 3호 적용')

# ---------- 비슷한 과거 사례 (현재 상태 -> 사례)
def stats(c):
    lv = [r3b.fnum(v['수위']) for (cc, t), v in ms.d.items() if cc == c and t >= datetime(2021, 1, 1) and r3b.fnum(v['수위']) is not None]
    iv = [r3b.fnum(v['유입량']) for (cc, t), v in ms.d.items() if cc == c and t >= datetime(2021, 1, 1) and r3b.fnum(v['유입량']) is not None]
    return (max(lv) - min(lv) or 1, max(iv) - min(iv) or 1)


sim = []
for d in dams:
    c = code_of(d)
    cur = ms.d[(c, latest[c])]
    rl, ri = stats(c)
    cand = []
    for r in case_rows:
        if r['dam'] == label[d] and r['window_rows'] >= 10:
            t = r3b.to_dt(r['time'])
            at = ms.d.get((c, t)) or ms.d.get((c, t + timedelta(hours=1)))
            if at and r3b.fnum(at['수위']) is not None and r3b.fnum(at['유입량']) is not None:
                dist = abs(r3b.fnum(cur['수위']) - r3b.fnum(at['수위'])) / rl + abs(r3b.fnum(cur['유입량']) - r3b.fnum(at['유입량'])) / ri
                cand.append((dist, r, at))
    cand.sort(key=lambda x: x[0])
    sim.append({'dam': label[d], 'current_time': str(latest[c]), 'current_level': cur['수위'], 'current_inflow': cur['유입량'], 'candidate_cases': len(cand),
                'best_case': cand[0][1]['operation'] if cand else '', 'best_time': cand[0][1]['time'] if cand else '', 'best_distance': round(cand[0][0], 3) if cand else ''})
with open(os.path.join(N, 'step3d_similar_cases.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=list(sim[0].keys())); w.writeheader(); w.writerows(sim)
M('통합', '현재 상태와 비슷한 과거 사례 검색', '댐별 후보 사례 ' + ', '.join('%s %d' % (s['dam'], s['candidate_cases']) for s in sim), '동일', '사례 후보는 상태 창이 있는 운영행위뿐(2019~2020)')

with open(os.path.join(N, 'step3d_cq_matrix.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
for r in rows:
    print(r['cq'], '|', r['item'], '|', r['strict_v1'], '|', r['variant_v1.1'], '|', r['detail'][:150])
print()
for s in sim:
    print(s)
print('cases', dict(cnt))
