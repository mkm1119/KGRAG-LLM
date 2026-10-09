#!/usr/bin/env python3
"""STEP 2D: KG v3 구축. KG v2에 (1) Approval–Dam 직접 관계(변형), (2) 기준 연혁 9개 판의 근거, (3) 규정 규칙 18개(원문), (4) 관련 조문 청크를 더한다.
온톨로지에 없는 요소는 origin='variant' 또는 속성 이름 'x_'로 표시해, 평가에서 v1(엄격)과 v1.1(변형)을 가를 수 있게 한다. stdlib만 사용.
입력: kgv2_*.csv, approval_records_hrfco_raw_fields.csv, criterion_version_history.csv, regulation_rules_v1.csv, han_system_membership_byeolpyo1.csv
출력: kgv3_entities / kgv3_properties / kgv3_relations / kgv3_provenance / kgv3_chunks (03_normalized)
"""
import csv, importlib.util, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
N = os.path.join(HERE, '..', '03_normalized')
spec = importlib.util.spec_from_file_location('rules', os.path.join(HERE, 'step2c_regulation_rules.py'))
rules_mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(rules_mod)
DOCS = rules_mod.DOCS


def rd(p):
    return list(csv.DictReader(open(os.path.join(N, p), encoding='utf-8-sig')))


def wr(name, header, rows):
    with open(os.path.join(N, name), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)


ents = [(r['entity_id'], r['class'], r['label']) for r in rd('kgv2_entities.csv')]
props = [(r['entity_id'], r['property'], r['value'], r['datatype']) for r in rd('kgv2_properties.csv')]
rels = [(r['subject'], r['relation'], r['object'], r['rule'], r['origin'], r['note']) for r in rd('kgv2_relations.csv')]
prov = [(r['item'], r['kind'], r['source_file'], r['source_locator'], r['rule'], r['data_origin'], r['note']) for r in rd('kgv2_provenance.csv')]
chunks = [(r['chunk_id'], r['doc_title'], r['locator'], r['text']) for r in rd('kgv2_chunks.csv')]
have = {e[0] for e in ents}
DAMCODES = {'충주': '1003110', '충주조정지': '1003611', '소양강': '1012110', '횡성': '1006110', '광동': '1001210'}
ALLDAMS = ['DAM:' + c for c in DAMCODES.values()]

# (A) Approval–Dam 직접 관계 (온톨로지 수정: 관계 추가, C12)
for r in rd('approval_records_hrfco_raw_fields.csv'):
    if r['관측소명'] in DAMCODES:
        rels.append(('APR:' + r['순차번호'], 'concernsDam', 'DAM:' + DAMCODES[r['관측소명']], 'MR-APR-DAM', 'ontology-fix', '온톨로지 수정(C12): 승인 행의 시설 코드'))

# (B) 별표3 연혁 9개 판: 판마다 근거자료 1개, 제한수위 Criterion을 해당 판에 연결(값이 같은 경우만)
hist = rd('criterion_version_history.csv')
crit_ids = {}
for e in ents:
    if e[1] == 'Criterion':
        crit_ids[re.sub(r'\s', '', e[2]).replace('홍수기제한수위', '')] = e[0]
vers = {}
for r in hist:
    nm = re.sub(r'\s', '', r['facility(raw, spaces kept)'])
    if nm in crit_ids:
        vers.setdefault(r['effective_from(시행일자)'], {})[nm] = (r['criterion_value_derived(footnote marker split; derived)'], r['effective_to(next version 시행일자; not a legal 폐지일)'], r['version_date(발령일자)'], r['promulgation_no'], r['revision_type'])
cur = {}
for p in props:
    if p[1] == 'criterionValue':
        cur[p[0]] = p[2]
for eff, d in sorted(vers.items()):
    ev = 'EVI:LAW:별표3@' + eff
    ents.append((ev, 'EvidenceSource', '연계운영규정 별표3 (시행 %s-%s-%s)' % (eff[:4], eff[4:6], eff[6:])))
    props += [(ev, 'sourceTitle', '댐과 보 등의 연계운영규정 (훈령 제%s호, %s)' % (list(d.values())[0][3], list(d.values())[0][4])), (ev, 'sourceType', '규정(연혁)'),
              (ev, 'sourceLocator', '별표 3 / 시행 %s-%s-%s' % (eff[:4], eff[4:6], eff[6:])), (ev, 'x_chunk_id', 'LAWHIST:별표3@' + eff)]
    lines = []
    for nm, (val, eto, vd, no, rt) in sorted(d.items()):
        lines.append('%s 홍수기 제한수위 %s EL.m (적용 %s~%s)' % (nm, val, eff, eto or '현재'))
        cid = crit_ids[nm]
        if float(val) == float(cur[cid]):
            rels.append((cid, 'supportedBy', ev, 'MR-SUP-CRI-HIST', 'real', '해당 판의 별표3 값이 현행과 같음'))
    chunks.append(('LAWHIST:별표3@' + eff, '댐과 보 등의 연계운영규정(연혁)', '별표 3 / 시행 ' + eff, '\n'.join(lines)))
    prov.append((ev, 'entity', '03_normalized/criterion_version_history.csv', 'effective_from=' + eff, 'MR-EVI-HIST', 'real', '판별 값은 연혁 표에서 읽음(원문 XML 대조 필요)'))

# (C) 규정 규칙 18개를 Criterion으로(변형): criterionValue에 조문 원문
ev_by_art = {}
for r in rd('regulation_rules_v1.csv'):
    rid = 'CRI:' + r['rule_id']
    ents.append((rid, 'Criterion', '[규칙] %s %s' % (r['source_doc'], r['article'])))
    props += [(rid, 'criterionType', r['rule_type']), (rid, 'criterionValue', r['verbatim'], 'text'), (rid, 'unit', ''),
              (rid, 'x_subject', r['subject'], 'variant'), (rid, 'x_condition', r['condition'], 'variant'),
              (rid, 'x_requirement', r['requirement_or_power'], 'variant'), (rid, 'x_use', r['use_in_kg'], 'variant')]
    prov.append((rid, 'entity', '03_normalized/regulation_rules_v1.csv', r['rule_id'], 'MR-RULE', 'real(원문)+Claude 주석', '구조화 칸은 Claude 주석, 사람 검토 필요'))
    art = re.match(r'(제\d+조(?:의\d+)?)', r['article']).group(1)
    key = (r['source_doc'], art)
    if key not in ev_by_art:
        evid = 'EVI:LAW:%s:%s' % (r['source_doc'].replace(' ', ''), art)
        ev_by_art[key] = evid
        if r['source_doc'] == '연계운영규정':
            cid = 'LAW:' + art
        else:
            cid = 'LAW:%s:%s' % (r['source_doc'].replace(' ', ''), art)
            chunks.append((cid, r['source_doc'], art, DOCS[r['source_doc']][art]))
        ents.append((evid, 'EvidenceSource', '%s %s' % (r['source_doc'], art)))
        props += [(evid, 'sourceTitle', r['source_doc']), (evid, 'sourceType', '법령' if r['source_doc'] != '연계운영규정' else '규정'),
                  (evid, 'sourceLocator', art), (evid, 'x_chunk_id', cid)]
        prov.append((evid, 'entity', '01_raw/Law/', '%s %s' % (r['source_doc'], art), 'MR-EVI-RULE', 'real'))
    rels.append((rid, 'supportedBy', ev_by_art[key], 'MR-SUP-RULE', 'real', ''))
    for d in ALLDAMS:
        rels.append((rid, 'appliesToDam', d, 'MR-RULE-DAM', 'general-rule', '댐 일반에 적용되는 규칙(원문에 댐 이름 없음)' if r['applies_to'] in ('댐', '시설') else ''))

# (D) 별표1 시설 분류를 Dam의 변형 속성으로
b1 = rd('han_system_membership_byeolpyo1.csv')
cat = {}
for r in b1:
    for nm in r['facilities_verbatim'].split(','):
        cat[re.sub(r'\s|\(.*?\)', '', nm)] = r['facility_category_in_source']
dam_label = {e[0]: e[2] for e in ents if e[1] == 'Dam'}
for did, nm in dam_label.items():
    key = '충주댐' if nm == '충주조정지' else nm
    if key in cat:
        props.append((did, 'x_byeolpyo1_category', cat[key] + (' (별표1에 충주댐(조정지댐포함)으로 표기)' if nm == '충주조정지' else ''), 'variant'))

wr('kgv3_entities.csv', ['entity_id', 'class', 'label'], ents)
wr('kgv3_properties.csv', ['entity_id', 'property', 'value', 'datatype'], props)
wr('kgv3_relations.csv', ['subject', 'relation', 'object', 'rule', 'origin', 'note'], rels)
wr('kgv3_provenance.csv', ['item', 'kind', 'source_file', 'source_locator', 'rule', 'data_origin', 'note'], prov)
wr('kgv3_chunks.csv', ['chunk_id', 'doc_title', 'locator', 'text'], chunks)
import collections
print('entities', collections.Counter(c for _, c, _ in ents))
print('relations', collections.Counter((r[1], r[4]) for r in rels))
print('chunks', len(chunks), 'properties', len(props), '연혁 판', len(vers))
