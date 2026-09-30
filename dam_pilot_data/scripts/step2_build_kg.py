#!/usr/bin/env python3
"""STEP 2 pilot KG builder. Source-faithful CSV output; no merges, no inference.
Reads 03_normalized/*.csv (derived from raw) and writes kg_*_pilot.csv + mapping_rules_pilot.csv."""
import csv, gzip, collections, os
N='03_normalized/'
def rd(f): return list(csv.DictReader(open(N+f,encoding='utf-8-sig')))
def wr(f,rows,cols):
    with open(N+f,'w',encoding='utf-8-sig',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=cols); w.writeheader(); w.writerows(rows)

ents=[];rels=[];props=[];prov=[]
def E(eid,cls,label,src): ents.append(dict(entity_id=eid,class_=cls,label=label,source_system=src))
def P(eid,prop,val,rule,src_file,loc,sha='',status='SUPPORTED',note=''):
    if val is None or str(val).strip()=='' : return
    fid=f'P|{eid}|{prop}'
    props.append(dict(entity_id=eid,property=prop,value=val,mapping_rule_id=rule,status=status))
    prov.append(dict(fact_id=fid,fact_type='property',source_file=src_file,source_locator=loc,source_sha256=sha,mapping_rule_id=rule,note=note))
def R(s,rel,o,rule,src_file,loc,status='SUPPORTED',note=''):
    fid=f'R|{s}|{rel}|{o}'
    rels.append(dict(subject_id=s,relation=rel,object_id=o,mapping_rule_id=rule,status=status,note=note))
    prov.append(dict(fact_id=fid,fact_type='relation',source_file=src_file,source_locator=loc,source_sha256='',mapping_rule_id=rule,note=note))
def EP(eid,src_file,loc,rule,sha=''):
    prov.append(dict(fact_id=f'E|{eid}',fact_type='entity',source_file=src_file,source_locator=loc,source_sha256=sha,mapping_rule_id=rule,note=''))

# ---- Dam: MyWater (source-scoped)
cat=rd('dam_catalog.csv'); basic={x['dam_id_source']:x for x in rd('dam_catalog_kwater_basic.csv')}
mw_dams=[]
for x in cat:
    if not x['dam_id_source']: continue   # KHNP dams without official ID: not instantiated (MR-01 scope)
    eid='DAM|MYWATER|'+x['dam_id_source']; mw_dams.append(eid)
    E(eid,'Dam',x['dam_name_source'],'K-water MyWater')
    EP(eid,'03_normalized/dam_catalog.csv','dam_id_source='+x['dam_id_source'],'MR-01')
    P(eid,'Dam.damId',x['dam_id_source'],'MR-01','03_normalized/dam_catalog.csv','dam_id_source',status='REVIEW_REQUIRED',note='ID scope is source system only')
    P(eid,'Dam.sourceSystem','K-water MyWater','MR-01','03_normalized/dam_catalog.csv','id_system')
    P(eid,'Dam.sourceFacilityCode',x['dam_id_source'],'MR-01','03_normalized/dam_catalog.csv','dam_id_source')
    P(eid,'Dam.sourceFacilityName',x['dam_name_source'],'MR-01','03_normalized/dam_catalog.csv','dam_name_source')
    b=basic.get(x['dam_id_source'])
    if b: P(eid,'Dam.facilityTypeSource',b['facility_type_source'],'MR-01','03_normalized/dam_catalog_kwater_basic.csv','facility_type_source')

# ---- Dam: approval-file facilities (source-scoped, NOT merged with MyWater)
cw=rd('approval_facility_code_crosswalk.csv'); ap_dam={}
for x in cw:
    code=x['approval_file_관측소코드']; eid='DAM|HRFCO_APPROVAL|'+code; ap_dam[code]=eid
    E(eid,'Dam',x['approval_file_관측소명'],'HRFCO approval file (data.go.kr 15085926)')
    EP(eid,'03_normalized/approval_facility_code_crosswalk.csv','approval_file_관측소코드='+code,'MR-02')
    P(eid,'Dam.damId',code,'MR-02','03_normalized/approval_facility_code_crosswalk.csv','approval_file_관측소코드',status='REVIEW_REQUIRED',note='ID scope is source system only')
    P(eid,'Dam.sourceSystem','HRFCO approval file','MR-02','03_normalized/approval_facility_code_crosswalk.csv','-')
    P(eid,'Dam.sourceFacilityCode',code,'MR-02','03_normalized/approval_facility_code_crosswalk.csv','approval_file_관측소코드')
    P(eid,'Dam.sourceFacilityName',x['approval_file_관측소명'],'MR-02','03_normalized/approval_facility_code_crosswalk.csv','approval_file_관측소명')

# ---- Approval
ap=rd('approval_records_hrfco_raw_fields.csv'); nrel=0
for x in ap:
    eid='APR|'+x['순차번호']; f='03_normalized/approval_records_hrfco_raw_fields.csv'; loc='row_number_in_file='+x['row_number_in_file']; sha=x['file_sha256']
    E(eid,'Approval','방류승인 순차번호 '+x['순차번호'],'HRFCO approval file')
    EP(eid,f,loc,'MR-03',sha)
    P(eid,'Approval.sourceSequenceNo',x['순차번호'],'MR-03',f,loc,sha)
    P(eid,'Approval.approvalDateSource',x['승인년월일시분'],'MR-03',f,loc,sha,note='value has date only')
    P(eid,'Approval.releaseStartTime',x['방류시작시간'],'MR-03',f,loc,sha)
    P(eid,'Approval.receivedReleaseAmount',x['접수방류량'],'MR-03',f,loc,sha,note='NOT mapped to approvedReleaseAmount')
    P(eid,'Approval.receivedDate',x['접수일자'],'MR-03',f,loc,sha)
    P(eid,'Approval.remarks',x['비고'],'MR-03',f,loc,sha,note='verbatim; no interpretation')
    d=ap_dam.get(x['관측소코드'])
    if d: R(eid,'concernsDam',d,'MR-04',f,loc,note='source-scoped to approval-file facility code'); nrel+=1

# ---- Documents
docs=rd('document_list.csv')
for x in docs:
    eid='DOC|'+x['document_id(연구용 임시ID)']
    E(eid,'Document',x['title_or_filename'],x['organization'])
    EP(eid,'03_normalized/document_list.csv','document_id='+x['document_id(연구용 임시ID)'],'MR-05',x['sha256'])
    P(eid,'Document.documentId',x['document_id(연구용 임시ID)'],'MR-05','03_normalized/document_list.csv','document_id',status='REVIEW_REQUIRED',note='research-temporary ID')
    P(eid,'Document.title',x['title_or_filename'],'MR-05','03_normalized/document_list.csv','title_or_filename')
reg_xml=[x for x in docs if 'admrul_2100000282102' in x['raw_file'] and x['raw_file'].endswith('현행20260708.xml')]
assert len(reg_xml)==1, reg_xml
regid='DOC|'+reg_xml[0]['document_id(연구용 임시ID)']
P(regid,'Document.effectiveDate','2026-07-08','MR-05','03_normalized/criterion_list.csv','defined_in_document (훈령 제42호, 시행 2026-07-08)')

# ---- Criterion
for x in rd('criterion_list.csv'):
    cid=x['criterion_id(연구용 임시ID)']; eid='CRT|'+cid; f='03_normalized/criterion_list.csv'
    E(eid,'Criterion',x['locator_in_document'][:80],'법제처 행정규칙 XML')
    EP(eid,f,'criterion_id='+cid,'MR-06')
    P(eid,'Criterion.locator',x['locator_in_document'],'MR-06',f,'locator_in_document')
    P(eid,'Criterion.statementVerbatim',x['verbatim_text_or_value'],'MR-06',f,'verbatim_text_or_value')
    P(eid,'Criterion.unit',x['unit'],'MR-06',f,'unit')
    P(eid,'Criterion.facilityNameInSource',x['applies_to_facility_per_source'],'MR-06',f,'applies_to_facility_per_source',status='REVIEW_REQUIRED',note='new property candidate (RC-11); no Criterion->Dam relation created')
    R(eid,'definedIn',regid,'MR-07',f,'defined_in_document (regulation XML raw_file)')

# ---- Stations + monitoredBy (source-listed)
for x in rd('observation_station_list.csv'):
    eid='STN|MYWATER|'+x['station_id_OBS_CD']; f='03_normalized/observation_station_list.csv'
    E(eid,'ObservationStation',x['station_name_source'],'K-water MyWater getRain')
    EP(eid,f,'station_id_OBS_CD='+x['station_id_OBS_CD'],'MR-08')
    P(eid,'ObservationStation.stationId',x['station_id_OBS_CD'],'MR-08',f,'station_id_OBS_CD')
    P(eid,'ObservationStation.stationName',x['station_name_source'],'MR-08',f,'station_name_source')
    P(eid,'ObservationStation.sourceSystem',x['source_system'],'MR-08',f,'source_system')
    P(eid,'ObservationStation.variableType',x['station_type_per_source_page'],'MR-08',f,'station_type_per_source_page',status='REVIEW_REQUIRED',note='source page label; allowed values not fixed')
    d='DAM|MYWATER|'+x['associated_DAM_CD_in_query']
    if d in mw_dams: R(d,'monitoredBy',eid,'MR-09',f,'associated_DAM_CD_in_query (source lists station under this dam query; spatial/hydrologic relation NOT verified)',note='association = query parameter')

# ---- Datasets
byname={}
for d in mw_dams: byname[d.split('|')[2]]=d
for x in rd('measurement_dataset_list.csv'):
    did=x['dataset_id(연구용 임시ID)']; eid='DS|'+did; f='03_normalized/measurement_dataset_list.csv'
    E(eid,'MeasurementDataset',did+' '+x['variable(s)'],x['source'])
    EP(eid,f,'dataset_id='+did,'MR-10')
    P(eid,'MeasurementDataset.datasetId',did,'MR-10',f,'dataset_id',status='REVIEW_REQUIRED',note='research-temporary ID')
    P(eid,'MeasurementDataset.sourceSystem',x['source'],'MR-10',f,'source')
    P(eid,'MeasurementDataset.variableNamesSource',x['variable(s)'],'MR-10',f,'variable(s)')
    P(eid,'MeasurementDataset.resolution',x['temporal_resolution'],'MR-10',f,'temporal_resolution')
    P(eid,'MeasurementDataset.periodStart',x['start_requested'],'MR-10',f,'start_requested',note='REQUESTED period, not verified coverage')
    P(eid,'MeasurementDataset.periodEnd',x['end_requested'],'MR-10',f,'end_requested',note='REQUESTED period, not verified coverage')
    fac=x['facility'].split(' ')[0]
    if fac in byname and x['group_or_kind'] in ('hydr-D','hydr-H','rain-A','rain-C'):
        R(eid,'concernsDam',byname[fac],'MR-11',f,'facility='+x['facility'],note='dataset requested for this single facility')
# ---- output
wr('kg_entities_pilot.csv',ents,['entity_id','class_','label','source_system'])
wr('kg_relations_pilot.csv',rels,['subject_id','relation','object_id','mapping_rule_id','status','note'])
wr('kg_properties_pilot.csv',props,['entity_id','property','value','mapping_rule_id','status'])
wr('kg_provenance_pilot.csv',prov,['fact_id','fact_type','source_file','source_locator','source_sha256','mapping_rule_id','note'])
print(collections.Counter(e['class_'] for e in ents)); print(collections.Counter((r['relation'],r['subject_id'].split('|')[0]) for r in rels)); print(len(props),len(prov))
