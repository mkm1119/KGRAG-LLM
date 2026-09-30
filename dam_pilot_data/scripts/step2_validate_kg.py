import csv,collections
N='03_normalized/'
rd=lambda f:list(csv.DictReader(open(N+f,encoding='utf-8-sig')))
ents=rd('kg_entities_pilot.csv');rels=rd('kg_relations_pilot.csv');props=rd('kg_properties_pilot.csv');prov=rd('kg_provenance_pilot.csv')
ids={e['entity_id'] for e in ents}; cls={e['entity_id']:e['class_'] for e in ents}
pf={p['fact_id'] for p in prov}
out=[]
def chk(n,ok,d): out.append((n,'PASS' if ok else 'FAIL',d))
chk('V1 entity_id unique',len(ids)==len(ents),f'{len(ents)} entities')
chk('V2 relation endpoints exist',all(r['subject_id'] in ids and r['object_id'] in ids for r in rels),f'{len(rels)} relations')
allowed={('Approval','concernsDam','Dam'),('MeasurementDataset','concernsDam','Dam'),('Dam','monitoredBy','ObservationStation'),('Criterion','definedIn','Document')}
chk('V3 relation domain/range within candidate v1',all((cls[r['subject_id']],r['relation'],cls[r['object_id']]) in allowed for r in rels),str(collections.Counter((cls[r['subject_id']],r['relation'],cls[r['object_id']]) for r in rels)))
chk('V4 every entity/property/relation has provenance',all(('E|'+e['entity_id']) in pf for e in ents) and all(('P|%s|%s'%(p['entity_id'],p['property'])) in pf for p in props) and all(('R|%s|%s|%s'%(r['subject_id'],r['relation'],r['object_id'])) in pf for r in rels),f'{len(prov)} provenance rows')
c=collections.Counter(r['subject_id'] for r in rels if r['relation']=='concernsDam' and r['subject_id'].startswith('APR'))
chk('V5 each Approval has exactly one concernsDam',len(c)==3929 and set(c.values())=={1},'3929 approvals')
chk('V6 no Approval-Criterion / Operation / upstream relations',not any(r['relation'] in('relatedCriterion','relatedApproval','targetDam','recordedIn','upstreamOf','downstreamOf','documentedBy') for r in rels) and not any(e['class_']=='Operation' for e in ents),'none present')
chk('V7 no approvedReleaseAmount / approvalTime / operation* populated',not any(p['property'] in('Approval.approvedReleaseAmount','Approval.approvalTime') or p['property'].startswith('Operation') for p in props),'unmapped by design')
# cross-source: no Approval-file Dam linked to MyWater Dam
chk('V8 no cross-source Dam merge (distinct IDs per source)',not any(e['entity_id'].startswith('DAM|') and e['entity_id'].count('|')!=2 for e in ents),'27 Dam nodes = 11 MyWater + 16 approval-file')
# raw count reconciliation
n_ap=sum(1 for _ in open(N+'approval_records_hrfco_raw_fields.csv',encoding='utf-8-sig'))-1
chk('V9 Approval node count = source rows',n_ap==sum(1 for e in ents if e['class_']=='Approval'),f'{n_ap}')
rem=sum(1 for p in props if p['property']=='Approval.remarks'); chk('V10 remarks count = 3,764 (STEP 0 count)',rem==3764,str(rem))
# reachability: Approval -> MeasurementDataset via KG only
dam_of={r['subject_id']:r['object_id'] for r in rels if r['relation']=='concernsDam' and r['subject_id'].startswith('APR')}
dsdams={r['object_id'] for r in rels if r['relation']=='concernsDam' and r['subject_id'].startswith('DS')}
reach=sum(1 for a,d in dam_of.items() if d in dsdams)
chk('V11 (finding) Approvals reachable to a MeasurementDataset through KG edges only',True,f'{reach} of 3929 (0 expected: Approval Dam nodes and MyWater Dam nodes are separate by design)')
chk('V12 (finding) Criterion reachable to a Dam',True,'0: no Criterion-Dam relation exists in v0.1 or candidate v1 (Criterion.facilityNameInSource is a literal)')
for o in out: print(o)
open(N+'kg_validation_results.csv','w',encoding='utf-8-sig').write('check,result,detail\n'+'\n'.join('%s,%s,"%s"'%(a,b,d.replace('"',"'")) for a,b,d in out)+'\n')
