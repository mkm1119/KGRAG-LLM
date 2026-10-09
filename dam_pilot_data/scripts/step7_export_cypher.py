#!/usr/bin/env python3
"""STEP 7: KG v3(CSV)를 Neo4j에 적재하는 Cypher 스크립트를 생성한다. stdlib만 사용.
방식(DDKG 3.3절): 추출·매핑 결과를 표/JSON으로 모은 뒤 스크립트로 Cypher 문을 만들어 일괄 적재한다.
- 개체 -> 노드 (라벨 = 클래스, 속성 id/label + 데이터 속성). 날짜/시각/수치는 Cypher 타입으로 변환.
- 관계 -> 관계 (유형 = 관계명, 속성 rule/origin/note).
- 측정 시계열과 문서 청크는 그래프에 넣지 않는다(KG는 연결과 의미만, 값은 외부 저장소).
출력: 03_normalized/kgv3_load.cypher
"""
import collections, csv, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); N = os.path.join(HERE, '..', '03_normalized')
rd = lambda p: list(csv.DictReader(open(os.path.join(N, p), encoding='utf-8-sig')))
q = lambda s: "'" + s.replace('\\', '\\\\').replace("'", "\\'").replace('\n', ' ').replace('\r', ' ') + "'"
ents, props, rels = rd('kgv3_entities.csv'), rd('kgv3_properties.csv'), rd('kgv3_relations.csv')
byent = collections.defaultdict(lambda: collections.defaultdict(list))
for r in props:
    byent[r['entity_id']][r['property']].append((r['value'], r['datatype']))


def val(v, dt):
    if dt == 'date' and re.fullmatch(r'\d{4}-\d{2}-\d{2}', v): return "date(%s)" % q(v)
    if dt == 'datetime' and re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}', v): return "datetime(%s)" % q(v + ':00')
    if dt == 'decimal':
        try: return repr(float(v))
        except ValueError: pass
    return q(v)


out = ['// KG v3 적재 스크립트 (자동 생성: scripts/step7_export_cypher.py). 기준 저장소는 kgv3_*.csv.',
       'CREATE CONSTRAINT kg_id IF NOT EXISTS FOR (n:Entity) REQUIRE n.id IS UNIQUE;']
for e in ents:
    sets = ['n.id = %s' % q(e['entity_id']), 'n.label = %s' % q(e['label'])]
    for p, lst in byent[e['entity_id']].items():
        vs = [val(v, dt) for v, dt in lst]
        sets.append('n.%s = %s' % (p, vs[0] if len(vs) == 1 else '[' + ', '.join(vs) + ']'))
    out.append('MERGE (n:Entity:%s {id: %s}) SET %s;' % (e['class'], q(e['entity_id']), ', '.join(sets[1:])))
for r in rels:
    out.append('MATCH (a:Entity {id: %s}), (b:Entity {id: %s}) MERGE (a)-[r:%s]->(b) SET r.rule = %s, r.origin = %s, r.note = %s;' %
               (q(r['subject']), q(r['object']), r['relation'], q(r['rule']), q(r['origin']), q(r['note'])))
open(os.path.join(N, 'kgv3_load.cypher'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('nodes', len(ents), 'rels', len(rels), 'statements', len(out))
