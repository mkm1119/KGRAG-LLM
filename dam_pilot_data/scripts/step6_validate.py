#!/usr/bin/env python3
"""STEP 6: KG v3가 온톨로지(최종본8)에 맞는지 확인한다. stdlib만 사용.
기준: Class 6, 관계 8(+ 수정으로 추가한 Approval–Dam concernsDam), 클래스별 데이터 속성(문서 3.7절).
확인 항목: (1) 관계 양 끝의 클래스 (2) 필수 속성 (3) 값 형식 (4) 근거 연결 (5) 두 경로의 댐 일치 (6) 온톨로지 밖 요소 목록, (7) 수정 전후 CQ4 도달 가능 승인 수.
출력: 03_normalized/step6_validation.csv
"""
import collections, csv, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); N = os.path.join(HERE, '..', '03_normalized')
rd = lambda p: list(csv.DictReader(open(os.path.join(N, p), encoding='utf-8-sig')))
ent = {r['entity_id']: r['class'] for r in rd('kgv3_entities.csv')}
props = collections.defaultdict(lambda: collections.defaultdict(list))
for r in rd('kgv3_properties.csv'):
    props[r['entity_id']][r['property']].append((r['value'], r['datatype']))
rels = rd('kgv3_relations.csv')
PAIRS = {'hasHydrometeorologicalState': [('Dam', 'HydrometeorologicalState')], 'performedOnDam': [('Operation', 'Dam')],
         'authorizes': [('Approval', 'Operation')], 'appliesToDam': [('Criterion', 'Dam')],
         'supportedBy': [(c, 'EvidenceSource') for c in ('HydrometeorologicalState', 'Operation', 'Approval', 'Criterion')],
         'concernsDam': [('Approval', 'Dam')]}  # concernsDam은 CQ4 검증에서 발견해 추가한 관계(수정)
ONTO_PROPS = {'Dam': ['damName', 'damType'], 'HydrometeorologicalState': ['variableType', 'stationCode'], 'Operation': ['operationType', 'operationTime'],
              'Approval': ['approvalTime', 'approvalContent'], 'Criterion': ['criterionType', 'criterionValue', 'unit'], 'EvidenceSource': ['sourceTitle', 'sourceType', 'sourceLocator']}
ALLOWED_EXTRA = {'EvidenceSource': ['chunkId']}  # 확장: 외부 문서 저장소 조회 키(stationCode와 같은 역할), 규정 근거에만 있음
rows = []
def add(i, item, result, n, note=''):
    rows.append({'id': i, 'check': item, 'result': result, 'count': n, 'note': note})

# (1) 관계 양 끝 클래스
bad = [(r['subject'], r['relation'], r['object']) for r in rels if (ent.get(r['subject']), ent.get(r['object'])) not in PAIRS.get(r['relation'], [])]
add('V1', '모든 관계의 양 끝이 허용된 클래스 쌍', '통과' if not bad else '실패', len(bad), str(bad[:3]))
# (2) 필수 속성
miss = []
for e, c in ent.items():
    for p in ONTO_PROPS[c]:
        if p not in props[e]:
            miss.append((e, p))
add('V2', '클래스별 필수 속성이 모두 있음', '통과' if not miss else '실패', len(miss), str(miss[:3]))
# (3) 값 형식
fmt = []
for e, c in ent.items():
    for v, _ in props[e].get('approvalTime', []):
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', v): fmt.append((e, v))
    for v, _ in props[e].get('operationTime', []):
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}', v): fmt.append((e, v))
    if c == 'Criterion':
        for v, _ in props[e].get('criterionValue', []):
            try: float(v)
            except ValueError: fmt.append((e, v))
add('V3', '날짜·시각·수치 값 형식', '통과' if not fmt else '실패', len(fmt), str(fmt[:3]))
# (4) 근거 연결: 근거 대상 4개 클래스
sup = collections.defaultdict(list)
for r in rels:
    if r['relation'] == 'supportedBy': sup[r['subject']].append(r['object'])
nos = [e for e, c in ent.items() if c in ('HydrometeorologicalState', 'Operation', 'Approval', 'Criterion') and not sup[e]]
add('V4', 'HMS·Operation·Approval·Criterion 모두 근거자료에 연결됨', '통과' if not nos else '실패', len(nos), str(nos[:3]))
# (5) 두 경로의 댐 일치
cd = {r['subject']: r['object'] for r in rels if r['relation'] == 'concernsDam'}
pd = {r['subject']: r['object'] for r in rels if r['relation'] == 'performedOnDam'}
au = collections.defaultdict(list)
for r in rels:
    if r['relation'] == 'authorizes': au[r['subject']].append(r['object'])
mism = [(a, o) for a, ops in au.items() for o in ops if cd.get(a) != pd.get(o)]
add('V5', '승인의 댐(concernsDam)과 그 승인이 허가한 행위의 댐(performedOnDam)이 같음', '통과' if not mism else '실패', len(mism), str(mism[:3]))
# (6) 온톨로지 밖 요소
xprops = collections.Counter(p for e in props for p in props[e] if p not in ONTO_PROPS[ent[e]] + ALLOWED_EXTRA.get(ent[e], []) if e in ent)
add('V6', '온톨로지에 없는 데이터 속성(x_ 접두)', '정보', sum(xprops.values()), '; '.join('%s %d' % kv for kv in sorted(xprops.items())))
orig = {k for k in PAIRS if k != 'concernsDam'}
orels = collections.Counter(r['relation'] for r in rels if r['relation'] not in orig)
add('V7', '문서 8개 관계 밖의 관계', '정보', sum(orels.values()), str(dict(orels)))
# (7) 수정 전후 CQ4
apps = [e for e, c in ent.items() if c == 'Approval']
reach_old = {a for a, ops in au.items() if ops}
add('V9', 'CQ4 댐에서 도달 가능한 승인: 수정 전(관계 8개)', '정보', '%d/%d' % (len(reach_old), len(apps)), 'Dam←performedOnDam←Operation←authorizes←Approval 경로만 사용')
add('V10', 'CQ4 댐에서 도달 가능한 승인: 수정 후(concernsDam 추가)', '정보', '%d/%d' % (len(set(cd)), len(apps)), '')
with open(os.path.join(N, 'step6_validation.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
for r in rows: print(r['id'], '|', r['check'], '|', r['result'], '|', r['count'], '|', r['note'][:150])
