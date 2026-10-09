#!/usr/bin/env python3
"""STEP 2D: KG v3 구축. KG v2에 (1) Approval–Dam 직접 관계, (2) 기준 연혁 9개 판의 근거, (3) 관련 조문 청크(문서 저장소)를 더한다.
온톨로지에 없는 요소는 origin='variant' 또는 속성 이름 'x_'로 표시해, 평가에서 v1(엄격)과 v1.1(변형)을 가를 수 있게 한다. stdlib만 사용.
입력: kgv2_*.csv, approval_records_clean.csv, criterion_version_history.csv, regulation_rules_v1.csv, han_system_membership_byeolpyo1.csv
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
DAMCODES = {'충주': '1003110', '소양강': '1012110', '횡성': '1006110', '광동': '1001210'}

# (A) Approval–Dam 직접 관계 (온톨로지 수정: 관계 추가, C12)
for r in rd('approval_records_clean.csv'):
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
              (ev, 'sourceLocator', '별표 3 / 시행 %s-%s-%s' % (eff[:4], eff[4:6], eff[6:])), (ev, 'chunkId', 'LAWHIST:별표3@' + eff)]
    lines = []
    for nm, (val, eto, vd, no, rt) in sorted(d.items()):
        lines.append('%s 홍수기 제한수위 %s EL.m (적용 %s~%s)' % (nm, val, eff, eto or '현재'))
        cid = crit_ids[nm]
        if float(val) == float(cur[cid]):
            rels.append((cid, 'supportedBy', ev, 'MR-SUP-CRI-HIST', 'real', '해당 판의 별표3 값이 현행과 같음'))
    chunks.append(('LAWHIST:별표3@' + eff, '댐과 보 등의 연계운영규정(연혁)', '별표 3 / 시행 ' + eff, '\n'.join(lines)))
    prov.append((ev, 'entity', '03_normalized/criterion_version_history.csv', 'effective_from=' + eff, 'MR-EVI-HIST', 'real', '판별 값은 연혁 표에서 읽음(원문 XML 대조 필요)'))

# (C) 법령 조문 청크는 문서 저장소에만 둔다(결정 2026-10: 규정 규칙 18개는 KG에서 제외. CQ1~CQ6에 필요하지 않음).
seen = set()
for r in rd('regulation_rules_v1.csv'):
    if r['source_doc'] == '연계운영규정':
        continue
    art = re.match(r'(제\d+조(?:의\d+)?)', r['article']).group(1)
    if (r['source_doc'], art) not in seen:
        seen.add((r['source_doc'], art))
        chunks.append(('LAW:%s:%s' % (r['source_doc'].replace(' ', ''), art), r['source_doc'], art, DOCS[r['source_doc']][art]))

wr('kgv3_entities.csv', ['entity_id', 'class', 'label'], ents)
wr('kgv3_properties.csv', ['entity_id', 'property', 'value', 'datatype'], props)
wr('kgv3_relations.csv', ['subject', 'relation', 'object', 'rule', 'origin', 'note'], rels)
wr('kgv3_provenance.csv', ['item', 'kind', 'source_file', 'source_locator', 'rule', 'data_origin', 'note'], prov)
wr('kgv3_chunks.csv', ['chunk_id', 'doc_title', 'locator', 'text'], chunks)
import collections
print('entities', collections.Counter(c for _, c, _ in ents))
print('relations', collections.Counter((r[1], r[4]) for r in rels))
print('chunks', len(chunks), 'properties', len(props), '연혁 판', len(vers))
