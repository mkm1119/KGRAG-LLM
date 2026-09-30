#!/usr/bin/env python3
"""STEP 3 pilot: rule-based retrieval over KG CSV + regulation text + measurement extract.
No LLM here. Every evidence row carries source file + locator. Retrieval paths are explicit."""
import csv, collections, json
N='03_normalized/'
rd=lambda f:list(csv.DictReader(open(N+f,encoding='utf-8-sig')))
ents={e['entity_id']:e for e in rd('kg_entities_pilot.csv')}
rels=rd('kg_relations_pilot.csv'); props=collections.defaultdict(dict)
for p in rd('kg_properties_pilot.csv'): props[p['entity_id']][p['property']]=p['value']
prov={p['fact_id']:p for p in rd('kg_provenance_pilot.csv')}
inb=collections.defaultdict(list); outb=collections.defaultdict(list)
for r in rels: outb[r['subject_id']].append(r); inb[r['object_id']].append(r)
ext=rd('linkage_pilot_measurement_extract.csv'); OFF=[k for k in ext[0] if k.startswith('offset')][0]
ev=[]
def add(qid,etype,content,src,loc,path):
    eid=f'{qid}-E{sum(1 for e in ev if e["question_id"]==qid)+1:02d}'
    ev.append(dict(question_id=qid,evidence_id=eid,evidence_type=etype,content=content,source_file=src,source_locator=loc,retrieval_path=path)); return eid
def dam_by(system,name_or_code):
    for e in ents.values():
        if e['class_']=='Dam' and e['entity_id'].split('|')[1]==system and (props[e['entity_id']].get('Dam.sourceFacilityName')==name_or_code or props[e['entity_id']].get('Dam.sourceFacilityCode')==name_or_code): return e['entity_id']
def approvals_of(dam): return [r['subject_id'] for r in inb[dam] if r['relation']=='concernsDam' and r['subject_id'].startswith('APR')]
def approval_ev(qid,a,path):
    p=props[a]; pr=prov['P|%s|Approval.sourceSequenceNo'%a]
    txt='; '.join(f'{k.split(".")[1]}={v}' for k,v in p.items())
    return add(qid,'KG_ENTITY(Approval)',f'순차번호 {p["Approval.sourceSequenceNo"]}: {txt}',pr['source_file'],pr['source_locator'],path)
def meas_ev(qid,case,path):
    rows=[x for x in ext if x['case_id']==case]
    for x in rows:
        add(qid,'MEASUREMENT(hourly, MyWater getHydr)',f'label={x["SDATE_raw"]} offset={x[OFF]}h 수위={x["DATA1_수위(EL.m)"]} 저수량={x["DATA2_저수량(MCM)"]} 강우량={x["DATA3_강우량(mm)"]} 유입량={x["DATA4_유입량(CMS)"]} 총방류량={x["DATA6_총방류량(CMS)"]} 저수율={x["DATA7_저수율(%)"]}',x['source_file'],f'case={case};SDATE_raw={x["SDATE_raw"]}',path)
    return rows
def derived_ev(qid,rows,path):
    def rng(k): v=[float(x[k]) for x in rows]; return min(v),max(v)
    lo,hi=rng('DATA6_총방류량(CMS)'); wl,wh=rng('DATA1_수위(EL.m)'); il,ih=rng('DATA4_유입량(CMS)')
    return add(qid,'DERIVED_COMPUTATION(from listed measurement rows)',f'창 내 {len(rows)}행: 총방류량 최소 {lo:g} ~ 최대 {hi:g} CMS; 수위 {wl:g} ~ {wh:g} EL.m; 유입량 {il:g} ~ {ih:g} CMS (단순 최소/최대, 라벨 기준 naive)','computed','min/max over rows above',path)
def criterion_ev(qid,cid,path):
    e='CRT|'+cid; p=props[e]; pr=prov['P|%s|Criterion.statementVerbatim'%e]
    doc=[r['object_id'] for r in outb[e] if r['relation']=='definedIn'][0]
    a=add(qid,'KG_ENTITY(Criterion)',f'{p["Criterion.locator"]} :: {p["Criterion.statementVerbatim"]} (unit={p.get("Criterion.unit","")}; facilityNameInSource={p.get("Criterion.facilityNameInSource")})',pr['source_file'],pr['source_locator'],path)
    d=add(qid,'KG_ENTITY(Document)',f'{doc}: {props[doc]["Document.title"]}; effectiveDate={props[doc].get("Document.effectiveDate")}',prov['E|'+doc]['source_file'],prov['E|'+doc]['source_locator'],path+' -> definedIn')
    return a,d
Q=[]
def q(qid,typ,text,expect): Q.append(dict(question_id=qid,question_type=typ,question=text,expected_evidence_kinds=expect))

# ---------- Direct / checkable
q('Q01','DIRECT','충주(승인파일 관측소코드 1003110)의 2020년 방류 승인 record는 몇 건이며 각각 접수일자·방류시작시간·접수방류량은?','KG: Dam→Approval')
d=dam_by('HRFCO_APPROVAL','1003110'); aps=[a for a in approvals_of(d) if props[a]['Approval.approvalDateSource'].startswith('2020')]
for a in sorted(aps,key=lambda a:int(props[a]['Approval.sourceSequenceNo'])): approval_ev('Q01',a,'Dam(HRFCO 1003110) <-concernsDam- Approval, filter 승인일 2020')
q('Q02','DIRECT','소양강댐의 홍수기 제한수위 기준값과 그 값이 실린 문서는?','KG: Criterion→Document')
criterion_ev('Q02','CR-01','Criterion(facilityNameInSource=소양강댐)')
q('Q03','DIRECT','승인 순차번호 3519의 비고 원문은?','KG: Approval property')
approval_ev('Q03','APR|3519','Approval by sourceSequenceNo')
q('Q04','DIRECT','MyWater 충주댐(1003110)에 조회 목록으로 연결된 관측소는 몇 개이며 유형별로는?','KG: Dam→monitoredBy→Station')
dm=dam_by('MYWATER','1003110'); st=[r['object_id'] for r in outb[dm] if r['relation']=='monitoredBy']
cnt=collections.Counter(props[s]['ObservationStation.variableType'] for s in st)
add('Q04','KG_AGGREGATE(Station)',f'monitoredBy 관측소 {len(st)}개; 유형 분포(원천 표기)={dict(cnt)}; 예: '+', '.join(props[s]['ObservationStation.stationId']+' '+props[s]['ObservationStation.stationName'] for s in st[:3]),'03_normalized/observation_station_list.csv','associated_DAM_CD_in_query=1003110','Dam(MYWATER 1003110) -monitoredBy-> Station (source-listed; not a spatial claim)')
q('Q05','DIRECT','충주댐의 2020-08 방류 운영행위(수문조작) 기록은?','KG: Operation')
q('Q06','DIRECT','2020-08-02 충주댐 승인 당시 적용되던 홍수기 제한수위는?','Criterion at time T')
criterion_ev('Q06','CR-02','Criterion(facilityNameInSource=충주댐); 현행(2026-07-08 시행)본만 보유')
# ---------- Natural operator questions
q('N01','NATURAL','충주댐에서 2020년 8월 초 방류 승인이 났을 때 그 무렵 저수위·유입량·방류량은 어땠나?','KG Approval + measurement window (crosswalk REVIEW_REQUIRED)')
approval_ev('N01','APR|3412','Dam(HRFCO 1003110) <-concernsDam- Approval 3412')
add('N01','EXTERNAL_LOOKUP(crosswalk, REVIEW_REQUIRED)','approval_facility_code_crosswalk.csv: 승인파일 1003110 충주 ↔ MyWater DAM_CD 1003110 충주댐 "same code AND similar name (동일시설 여부는 REVIEW_REQUIRED)"','03_normalized/approval_facility_code_crosswalk.csv','approval_file_관측소코드=1003110','KG 간선으로는 연결 불가(S2-01) → crosswalk 표를 외부 조회')
rows=meas_ev('N01','AP-3412','hourly extract for case AP-3412 (방류시작시간 -6h..+12h, naive label)')
derived_ev('N01',rows,'min/max over N01 rows')
q('N02','NATURAL','횡성댐의 2020년 방류 승인은 어떤 운영기준을 근거로 한 것인가?','Approval→Criterion (rationale)')
d=dam_by('HRFCO_APPROVAL','1006110'); aps=[a for a in approvals_of(d) if props[a]['Approval.approvalDateSource'].startswith('2020')]
add('N02','KG_AGGREGATE(Approval)',f'승인파일 횡성(1006110)에 연결된 2020년 Approval {len(aps)}건: '+', '.join(props[a]['Approval.sourceSequenceNo'] for a in aps),'03_normalized/approval_records_hrfco_raw_fields.csv','관측소코드=1006110','Dam(HRFCO 1006110) <-concernsDam- Approval, filter 2020')
for a in aps: approval_ev('N02',a,'Dam(HRFCO 1006110) <-concernsDam- Approval, filter 2020')
criterion_ev('N02','CR-03','Criterion(facilityNameInSource=횡성댐); 현행본 — 승인과의 관계는 KG에 없음')
q('N03','NATURAL','광동댐 방류 승인 시 참고할 운영기준(시설별 값)이 있나?','Criterion by facility')
crs=[e for e in ents if e.startswith('CRT|') and props[e].get('Criterion.facilityNameInSource') and '광동' in props[e]['Criterion.facilityNameInSource']]
add('N03','KG_AGGREGATE(Criterion)',f'facilityNameInSource에 "광동"을 포함하는 Criterion {len(crs)}건(15건 중); 시설명 지정 Criterion은 CR-01~CR-09(9개 시설), 나머지 CR-10~CR-15는 시설 지정 없는 조문','03_normalized/criterion_list.csv','applies_to_facility_per_source','Criterion filter by facilityNameInSource')
q('N04','NATURAL','충주댐 2020-08-02 승인의 접수방류량(3000)만큼 실제로 방류가 이루어졌나?','Approval amount vs measured discharge (no equating)')
approval_ev('N04','APR|3412','Approval 3412')
rows=meas_ev('N04','AP-3412','same window as N01'); derived_ev('N04',rows,'min/max over N04 rows')
q('N05','NATURAL','소양강댐 현재 상황과 유사한 과거 승인 사례는?','similarity (undefined)')
add('N05','NO_RETRIEVAL_METHOD','유사도 정의·현재 상태 입력·검색 방법이 본 pilot에 없음(handoff §4.3: STEP 3 retrieval 설계 사항). KG에는 유사도 관계가 없음','-','-','(none)')
json.dump(Q,open('/tmp/_q.json','w'),ensure_ascii=False)
def wr(f,rows):
    with open(N+f,'w',encoding='utf-8-sig',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
wr('qa_pilot_questions.csv',Q); wr('qa_retrieved_evidence.csv',ev)
print(collections.Counter(e['question_id'] for e in ev))
for e in ev:
    if e['question_id'] in('Q01','Q02','Q03','Q04','Q06','N02','N03','N05') or e['evidence_id'] in('N01-E01','N01-E02','N01-E03','N01-E10'): print(e['evidence_id'],e['content'][:260])
