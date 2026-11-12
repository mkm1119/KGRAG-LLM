#!/usr/bin/env python3
"""STEP 13: KG v4를 (가) 원자료와 대조하고 (나) CQ1~CQ6마다 KG에서 근거를 찾아 원자료에서 센 값과 대조하고 (다) 분야 상식으로 만든 후보 규칙을 실행한다. stdlib만 사용.
step6_validate.py(온톨로지 규칙 검사)와 짝이 되는 검사이다. KG를 만든 중간 파일이 아니라 원본 파일을 다시 읽어 기대 값을 만든다.
원자료: 01_raw/FloodControl 승인 CSV(cp949), 01_raw/Law 연계운영규정 XML(별표3).
중간 파일을 쓰는 곳: 운영행위(비고에서 뽑은 표 operation_from_remarks_5dams.csv), 중복 제거 기록(approval_preprocess_log.csv).
출력: 03_normalized/step13_source_cq_check.csv
"""
import collections, csv, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..'); N = os.path.join(ROOT, '03_normalized')
rd = lambda p: list(csv.DictReader(open(os.path.join(N, p), encoding='utf-8-sig')))
DAMS = {'1003110': '충주댐', '1012110': '소양강댐', '1006110': '횡성댐', '1001210': '광동댐'}

ent = {r['entity_id']: r['class'] for r in rd('kgv4_entities.csv')}
prop = collections.defaultdict(dict)
for r in rd('kgv4_properties.csv'):
    prop[r['entity_id']][r['property']] = r['value']
rels = rd('kgv4_relations.csv')
out_ = collections.defaultdict(lambda: collections.defaultdict(list)); in_ = collections.defaultdict(lambda: collections.defaultdict(list))
for r in rels:
    out_[r['subject']][r['relation']].append(r['object']); in_[r['object']][r['relation']].append(r['subject'])

rows = []
def add(i, group, item, expect, got, note=''):
    rows.append({'id': i, 'group': group, 'check': item, 'expected': expect, 'kg': got, 'result': '일치' if str(expect) == str(got) else '불일치', 'note': note})

# ------------------------------------------------------------------ (가) 원자료 대조
raw = list(csv.DictReader(open(os.path.join(ROOT, '01_raw', 'FloodControl', '환경부_한강홍수통제소_홍수예보_댐방류승인_20220727.csv'), encoding='cp949')))
sel = {r['순차번호']: r for r in raw if r['관측소코드'].strip() in DAMS}
dup = {r['removed_seq'] for r in rd('approval_preprocess_log.csv')} & set(sel)
exp = {k: v for k, v in sel.items() if k not in dup}
kg_apr = {e.split(':')[1] for e, c in ent.items() if c == 'Approval'}
add('S1', '원자료 대조', '승인 개수와 순차번호 (원본 %d행 − 값이 모두 같은 중복 %d행)' % (len(sel), len(dup)), len(exp), len(kg_apr & set(exp)),
    '원본에만 있음 %s, KG에만 있음 %s' % (sorted(set(exp) - kg_apr), sorted(kg_apr - set(exp))))
ok_t = sum(prop['APR:' + k].get('approvalTime') == v['승인년월일시분'].strip()[:10] for k, v in exp.items())
add('S2', '원자료 대조', '승인일(approvalTime)이 원본 승인년월일과 같음', len(exp), ok_t)
sp = lambda t: re.sub(r'\s+', ' ', t.strip())
def content_ok(k, v, norm):
    c = prop['APR:' + k].get('approvalContent', '')
    return all((sp(x) if norm else x.strip()) in c for x in (v['방류시작시간'], v['접수방류량'], v['비고']) if x.strip())
n_exact = sum(content_ok(k, v, False) for k, v in exp.items())
add('S3', '원자료 대조', '승인내용(approvalContent)에 원본의 방류시작시간·접수방류량·비고가 들어 있음(연속 공백은 한 칸으로 봄)', len(exp), sum(content_ok(k, v, True) for k, v in exp.items()),
    '글자까지 그대로 같은 것 %d개, 나머지 %d개는 원본 비고의 연속 공백·끝 공백만 다름' % (n_exact, len(exp) - n_exact))
add('S4', '원자료 대조', '승인이 이어진 댐(concernsDam)이 원본 관측소코드의 댐과 같음', len(exp),
    sum(out_['APR:' + k]['concernsDam'] == ['DAM:' + v['관측소코드'].strip()] for k, v in exp.items()))
xml = open(os.path.join(ROOT, '01_raw', 'Law', 'admrul_2100000282102_댐과보등의연계운영규정_현행20260708.xml'), encoding='utf-8').read()
annex = {}
for m in re.finditer(r'│([^│\n]*댐)\s*│\s*([0-9.]+)[^│]*│', xml):
    annex.setdefault(m.group(1).replace(' ', ''), m.group(2))
cri = {}
for e, c in ent.items():
    if c == 'Criterion':
        cri[DAMS[out_[e]['appliesToDam'][0].split(':')[1]]] = prop[e]['criterionValue']
add('S5', '원자료 대조', '운영기준 값(criterionValue)이 규정 별표3 원문의 그 댐 값과 같음', len(cri), sum(annex.get(d) == v for d, v in cri.items()),
    '; '.join('%s KG %s / 원문 %s' % (d, v, annex.get(d)) for d, v in cri.items()) + '; 광동댐은 별표3에 없음' * ('광동댐' not in annex))
# 댐: K-water 댐 기본정보를 정리한 표(dam_catalog_kwater_basic.csv)와 대조. 운영기준은 같은 표의 홍수기제한수위(규정과 독립된 자료)와도 대조
cat = {r['dam_id_source']: r for r in rd('dam_catalog_kwater_basic.csv')}
dams = [e for e, c in ent.items() if c == 'Dam']
add('S9', '원자료 대조', '댐의 이름과 유형(damName, damType)이 K-water 댐 기본정보와 같음', len(dams),
    sum(e.split(':')[1] in cat and prop[e].get('damName') == cat[e.split(':')[1]]['dam_name_source'] and prop[e].get('damType') == cat[e.split(':')[1]]['facility_type_source'] for e in dams),
    '기대 값은 K-water 댐 기본정보를 정리한 표에서 읽음')
kw = {r['dam_name_source']: r['홍수기제한수위(EL.m)[DATA10]'] for r in cat.values()}
add('S10', '다른 자료와 대조', '운영기준 값이 K-water 댐 기본정보의 홍수기제한수위와 같음(규정 별표3과 독립된 자료)', len(cri),
    sum(d in kw and float(kw[d]) == float(v) for d, v in cri.items()),
    '; '.join('%s KG %s / K-water %s' % (d, v, kw.get(d)) for d, v in cri.items()) + '; 광동댐은 K-water에만 %s' % kw.get('광동댐'))
ops = [o for o in rd('operation_from_remarks_5dams.csv') if o['operation_created'] == 'Y']
kg_opr = [e for e, c in ent.items() if c == 'Operation']
add('S6', '원자료 대조', '운영행위가 나온 승인이 모두 원본에 있음', len(kg_opr), sum(e.split(':')[1] in exp for e in kg_opr))
by_start = [e for e in kg_opr if prop[e]['operationTime'].replace('T', ' ') == exp[e.split(':')[1]]['방류시작시간'].strip()]
rest = [e for e in kg_opr if e not in by_start]
add('S7', '원자료 대조', '운영행위 시각(operationTime)이 원본 방류시작시간과 같음(비고에 시각이 적힌 %d개 제외)' % len(rest), len(kg_opr) - len(rest), len(by_start))
rows.append({'id': 'S7b', 'group': '원자료 대조', 'check': '운영행위 시각을 비고에 적힌 시각으로 읽은 것', 'expected': '-', 'kg': len(rest), 'result': '사람 확인 필요',
             'note': ', '.join('%s 비고 "%s" → %s' % (e, exp[e.split(':')[1]]['비고'].strip(), prop[e]['operationTime']) for e in rest)})
typ = collections.Counter(prop[e]['operationType'] for e in kg_opr)
rows.append({'id': 'S8', 'group': '원자료 대조', 'check': '운영행위 유형(operationType)은 비고 문구를 규칙으로 읽은 값', 'expected': '-', 'kg': len(kg_opr), 'result': '사람 확인 필요',
             'note': '; '.join('%s %d' % kv for kv in typ.most_common()) + '. 원본에 유형 열이 없어 대조할 값이 없음'})

# ------------------------------------------------------------------ (나) CQ별 질의: 댐에서 출발해 KG에서 찾은 개수와 원자료에서 센 개수
exp_apr = collections.Counter(DAMS[v['관측소코드'].strip()] for v in exp.values())
exp_opr = collections.Counter(o['댐'] + '댐' for o in ops)
for code, dam in DAMS.items():
    d = 'DAM:' + code
    hms = out_[d]['hasHydrometeorologicalState']
    add('C1-' + dam, 'CQ1·CQ2 수문·기상 상태', dam + ': 댐에서 이어진 상태 변수(수위·저수량·강우량·유입량·총방류량·저수율)', 6, len(hms), '값은 KG 밖의 측정자료 저장소에서 읽음')
    add('C3-' + dam, 'CQ3 과거 운영행위', dam + ': 댐에서 이어진 운영행위', exp_opr[dam], len(in_[d]['performedOnDam']), '기대 값은 비고에서 뽑은 표에서 셈')
    add('C4-' + dam, 'CQ4 과거 방류 승인', dam + ': 댐에서 이어진 승인', exp_apr[dam], len(in_[d]['concernsDam']), '기대 값은 원본 승인 CSV에서 셈')
    add('C5-' + dam, 'CQ5 운영기준', dam + ': 댐에 적용되는 운영기준', 1 if dam in annex else 0, len(in_[d]['appliesToDam']), '기대 값은 별표3에 그 댐이 있는지')
tgt = [e for e, c in ent.items() if c in ('HydrometeorologicalState', 'Operation', 'Approval', 'Criterion')]
add('C6', 'CQ6 공식 근거', '상태·운영행위·승인·운영기준에서 이어진 근거자료에 출처 위치(sourceLocator)가 있음', len(tgt),
    sum(bool(out_[e]['supportedBy']) and all(prop[x].get('sourceLocator') for x in out_[e]['supportedBy']) for e in tgt))
loc = [prop[e]['sourceLocator'] for e, c in ent.items() if c == 'EvidenceSource' and e.startswith('EVI:AP:')]
add('C6b', 'CQ6 공식 근거', '승인 근거자료의 출처 위치(순차번호)가 원본에 있는 행을 가리킴', len(loc), sum(l.replace('순차번호', '').strip() in exp for l in loc))

# ------------------------------------------------------------------ (다) 후보 규칙: 분야 상식으로 만든 규칙. 맞는 규칙인지는 전문가 확인이 필요하다
au = [(r['subject'], r['object']) for r in rels if r['relation'] == 'authorizes']
early = [(a, o) for a, o in au if prop[o]['operationTime'][:10] < prop[a]['approvalTime']]
rows.append({'id': 'R1', 'group': '후보 규칙', 'check': '운영행위의 날짜가 그 운영행위를 허가한 승인의 승인일보다 이르지 않음', 'expected': len(au), 'kg': len(au) - len(early), 'result': '전문가 확인 필요',
             'note': '; '.join('%s(%s) 시각 %s / %s 승인일 %s' % (o, prop[o]['operationType'], prop[o]['operationTime'], a, prop[a]['approvalTime']) for a, o in early)})
grp = collections.defaultdict(list)
for k, v in exp.items():
    grp[(v['관측소코드'].strip(), v['방류시작시간'].strip())].append(k)
multi = {k: v for k, v in grp.items() if len(v) > 1}
rows.append({'id': 'R2', 'group': '후보 규칙', 'check': '같은 댐에 같은 방류시작시간을 가진 승인이 둘 이상인 묶음', 'expected': '-', 'kg': len(multi), 'result': '정보',
             'note': '승인 %d개. 변경·연장 승인을 가려내는 데 쓸 수 있음' % sum(len(v) for v in multi.values())})

with open(os.path.join(N, 'step13_source_cq_check.csv'), 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for r in rows:
    print(' | '.join(str(r[k]) for k in ('id', 'check', 'expected', 'kg', 'result', 'note')))
print(collections.Counter(r['result'] for r in rows))
