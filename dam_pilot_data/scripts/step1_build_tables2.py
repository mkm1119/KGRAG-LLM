#!/usr/bin/env python3
"""STEP 1-H representative instances (real records only), 1-I CQ validation, Working Ontology Candidate v1.
Initial Ontology v0.1 is unchanged; v1 is a separate candidate table."""
import csv, json, glob, re
def rd(p): return list(csv.DictReader(open(p,encoding='utf-8-sig',newline='')))
def W(path,rows,cols):
    with open(path,'w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); [w.writerow({c:r.get(c,'') for c in cols}) for r in rows]
ap={r['순차번호']:r for r in rd('03_normalized/approval_records_hrfco_raw_fields.csv')}
cases=rd('03_normalized/linkage_pilot_cases.csv')
crit={r['applies_to_facility_per_source']:r for r in rd('03_normalized/criterion_list.csv') if r['criterion_type'].startswith('홍수기 제한수위')}
docs=rd('03_normalized/document_list.csv')
regdoc=[d for d in docs if 'admrul_2100000282102' in d['raw_file']][0]
stations=[s for s in rd('03_normalized/observation_station_list.csv') if s['associated_DAM_CD_in_query']=='1003110' and s['station_type_per_source_page'].startswith('우량')][:3]
dsl=rd('03_normalized/measurement_dataset_list.csv')
ds_c=[d for d in dsl if d['facility'].startswith('1003110') and d['group_or_kind'] in ('hydr-H','hydr-D')]
I=[]
def inst(ref,cls,src,expr,notexpr,flags): I.append(dict(instance_ref=ref,v01_class=cls,real_source_record=src,expressible_with_v01=expr,not_expressible_with_v01=notexpr,status_flags=flags))
# --- 충주댐 set (real)
inst('I-01','Dam','MyWater getPeriod damList: DAM_CD=1003110, DAM_NM=충주댐, RIVR_NM=한강, DAM_BO_NM=다목적댐 (01_raw/KWater/mywater_period/…)','Dam instance; Dam.damId="1003110"','출처(MyWater) 범위; 시설 유형(다목적댐); 하천 그룹 라벨(검증된 수계 아님)','ID system 미표현')
inst('I-02','Dam','Approval CSV: 관측소코드=1003110, 관측소명=충주 (승인 파일 3412/3519/3647/3771행 등)','별개 Dam instance; Dam.damId="1003110"','I-01과 같은 시설인지: 코드만 일치, 이름 표기 상이 → 동일시설 확정 불가','FACILITY_IDENTITY_UNRESOLVED (병합하지 않음)')
for k,seq in (('I-03','3412'),('I-04','3519')):
    r=ap[seq]
    inst(k,'Approval',f"Approval CSV 순차번호={seq}: 승인년월일시분={r['승인년월일시분']}, 방류시작시간={r['방류시작시간']}, 접수방류량={r['접수방류량']}, 접수일자={r['접수일자']}, 비고={r['비고'][:80]}",
         'Approval instance; approvalTime/approvedReleaseAmount는 값 의미가 미확정이라 채우지 않음(REVIEW)','방류시작시간, 접수일자, 접수방류량(승인량과 동일 여부 미검증), 비고(원문 보존), 대상 시설(Approval→Dam 경로가 v0.1에 없음)','APPROVAL_FIELD_SEMANTICS_UNRESOLVED; NO_APPROVAL_TO_DAM_PATH')
inst('I-05','MeasurementDataset',"MyWater getHydr H, DAM_CD=1003110: "+'; '.join(sorted({d['start_requested']+'~'+d['end_requested'] for d in ds_c if d['group_or_kind']=='hydr-H'})[:1])+" (01_raw/KWater/mywater_station/hydr/H/1003110/, mywater_approval_linked/hydr/H/1003110/)",'MeasurementDataset instance; datasetId(연구용 임시 ID)','변수·단위·해상도·기간을 담을 속성; Dam과의 연결(Dam–Dataset 경로 없음, 관측소 경유 자료 아님)','NO_DAM_TO_DATASET_PATH; TIMESTAMP_CONVENTION_UNRESOLVED')
for i,s in enumerate(stations):
    inst(f'I-{6+i:02d}','ObservationStation',f"MyWater getRain 우량관측소: OBS_CD={s['station_id_OBS_CD']}, 지점명={s['station_name_source']} (damCd=1003110 조회)",'ObservationStation instance; stationId; variableType="우량"(관측소 유형 후보); Dam–monitoredBy 후보(출처가 충주댐 아래 나열)','좌표(미제공); 이 관측소의 시계열(미확보 — getRain은 종료 시점 1건)','MONITOREDBY_SEMANTICS_REVIEW; NO_STATION_LEVEL_DATASET')
c=crit['충주댐']
inst('I-09','Criterion',f"criterion_list {c['criterion_id(연구용 임시ID)']}: {c['locator_in_document']} — {c['verbatim_text_or_value']} ({c['unit']})",'Criterion instance; definedIn → Document(I-10)','값(138.0)과 단위(EL.m), 적용 시점/버전, 적용 대상 시설(충주댐)','CRITERION_VALUE_NOT_EXPRESSIBLE; TEMPORAL_APPLICABILITY_UNRESOLVED')
inst('I-10','Document',f"document_list {regdoc['document_id(연구용 임시ID)']}: {regdoc['raw_file']} (sha256 {regdoc['sha256'][:12]}…)",'Document instance; documentId','문서 제목, 시행일자(2026-07-08), 소관부처, 문서 내 위치(별표3) — 속성 부재','DOCUMENT_VERSION_NOT_EXPRESSIBLE')
inst('I-11','(관계 미주장)','Approval I-03/I-04(2020-08) ↔ Criterion I-09(현행 2026-07-08)','—','2020년 승인과 2026년 현행 기준의 연결은 **주장하지 않음**; v0.1에는 Approval–Criterion 직접 관계도 없음(Operation 경유)','NOT_ASSERTED (S1A-07)')
# 횡성/소양강
for name,code,cr in (('횡성','1006110','횡성댐'),('소양강','1012110','소양강댐')):
    ids=[c for c in cases if c['관측소명']==name]
    inst(f'I-{12 if name=="횡성" else 14}','Approval',f"{name}: 승인 {len(ids)}건 ("+', '.join(x['case_id'] for x in ids)+f"), 관측소코드={code}",'Approval instances (필드 의미 REVIEW)','방류시작시간·접수일자·비고·대상 시설','동일 제약(I-03)')
    cc=crit[cr]
    inst(f'I-{13 if name=="횡성" else 15}','Criterion',f"{cc['criterion_id(연구용 임시ID)']}: {cc['verbatim_text_or_value']}",'Criterion instance; definedIn → I-10','값·단위·적용 시점','동일 제약(I-09)')
IC=['instance_ref','v01_class','real_source_record','expressible_with_v01','not_expressible_with_v01','status_flags']
W('03_normalized/step1_representative_instances.csv',I,IC)
# ---------------- 1-I CQ validation
V=[
dict(cq_id='CQ1',v01_can_represent='부분: Dam–monitoredBy→Station–hasDataset→Dataset 경로는 있음',actual_facts_exist='관측소 목록 O(94, 출처 나열); 장기 측정자료는 댐 단위 O; 관측소 단위 시계열 X',problem_classification='ONTOLOGY_REVISION_CANDIDATE(댐 단위 dataset을 Dam에 연결할 경로 없음: RC-02) + DATA_AVAILABILITY(관측소 단위 시계열) + SOURCE_SEMANTIC(monitoredBy 의미)',v1_candidate_effect='concernsDam(MeasurementDataset→Dam) 후보로 해소 가능(미채택)',log_ids='S1I-01'),
dict(cq_id='CQ2',v01_can_represent='예: Operation, targetDam, operationTime/Type',actual_facts_exist='X (독립 Operation record 미확보)',problem_classification='DATA_AVAILABILITY (스키마 문제 아님)',v1_candidate_effect='없음',log_ids='S1I-02'),
dict(cq_id='CQ3',v01_can_represent='Operation–relatedApproval→Approval 경로만 표현',actual_facts_exist='승인 3,929건 O; 연결될 Operation X',problem_classification='ONTOLOGY_REVISION_CANDIDATE(Approval→Dam 경로 없음: RC-01; Approval의 방류시작시간·접수일자·비고 속성 없음: RC-03) + DATA_AVAILABILITY(Operation)',v1_candidate_effect='concernsDam(Approval→Dam)+Approval 속성 후보로 표현 가능(미채택)',log_ids='S1I-03'),
dict(cq_id='CQ4',v01_can_represent='Operation–relatedCriterion→Criterion 경로만 표현; 기준 값·단위·적용 시점 표현 불가',actual_facts_exist='Criterion 15건 O(현행 버전); 당시 버전 X',problem_classification='ONTOLOGY_REVISION_CANDIDATE(값·시점 속성: RC-04) + DATA_AVAILABILITY(연혁) + DATA_AVAILABILITY(Operation)',v1_candidate_effect='Criterion 속성 후보로 값 표현 가능; 시점 적용성은 자료가 필요',log_ids='S1I-04'),
dict(cq_id='CQ5',v01_can_represent='Criterion–definedIn→Document 표현 가능; Approval–documentedBy(REVIEW); Operation–recordedIn',actual_facts_exist='Criterion→Document O(15/15); Approval 문서 X(파일 단위); Operation X',problem_classification='부분 OK(definedIn) + SOURCE_SEMANTIC(documentedBy) + DATA_AVAILABILITY(Operation) + ONTOLOGY(문서 버전·위치 속성: RC-05, 근거 C)',v1_candidate_effect='Document 속성 후보(버전) 추가',log_ids='S1I-05'),
dict(cq_id='CQ6',v01_can_represent='관측소·dataset 경로는 표현; 변수·단위·해상도·기간 속성 없음',actual_facts_exist='댐 단위 시계열 O(저수위·유입량·총방류량·강우량); 관측소 단위 X; 운영 시점 anchor(Operation) X',problem_classification='ONTOLOGY_REVISION_CANDIDATE(dataset 속성: RC-08, Dam 연결: RC-02) + SOURCE_SEMANTIC(방류량 의미·시각 규약) + DATA_AVAILABILITY(Operation anchor)',v1_candidate_effect='MeasurementDataset 속성·concernsDam 후보',log_ids='S1I-06'),
]
W('03_normalized/step1_cq_validation.csv',V,['cq_id','v01_can_represent','actual_facts_exist','problem_classification','v1_candidate_effect','log_ids'])
# ---------------- Working Ontology Candidate v1
U='UNCHANGED_FROM_V0.1'; A='CANDIDATE_ADDITION'; H='HELD_NOT_ADOPTED'
V1=[]
def v1(t,name,dom,rng,status,src_term,ev,lvl,issue,rc): V1.append(dict(element_type=t,name=name,domain=dom,range_or_value_type=rng,status=status,source_term_verbatim=src_term,evidence=ev,method_evidence=lvl,open_issue=issue,revision_candidate=rc))
for c in ['Dam','Operation','Approval','Criterion','Document','ObservationStation','MeasurementDataset']: v1('Class',c,'','',U,'','Initial Ontology v0.1','—','','')
for n,d,r in [('targetDam','Operation','Dam'),('relatedApproval','Operation','Approval'),('relatedCriterion','Operation','Criterion'),('recordedIn','Operation','Document'),('documentedBy','Approval','Document'),('definedIn','Criterion','Document'),('monitoredBy','Dam','ObservationStation'),('hasDataset','ObservationStation','MeasurementDataset')]: v1('Relation',n,d,r,U,'','Initial Ontology v0.1','—','','')
for n,d,r in [('damId','Dam','String'),('operationTime','Operation','(미정)'),('operationType','Operation','(미정)'),('approvalTime','Approval','(미정)'),('approvedReleaseAmount','Approval','Number'),('stationId','ObservationStation','String'),('variableType','ObservationStation','(미정)'),('datasetId','MeasurementDataset','String'),('documentId','Document','String')]: v1('DataProperty',n,d,r,U,'','Initial Ontology v0.1','—','값 의미 미확정 항목 포함(S0-B/S0-E)','')
# candidate additions
v1('Relation','concernsDam','Approval','Dam',A,'(승인 파일: 관측소코드/관측소명)','STEP 0: 승인 3,929건이 각 record에 시설을 가짐; DDKG p.4: 모든 최상위 클래스를 Dam에 연결','A(패턴: DDKG) + B(적용)','Dam은 **출처별 identity**(병합 금지)이며 이 관계는 출처 내 시설을 가리킴','RC-01')
v1('Relation','concernsDam','MeasurementDataset','Dam',A,'(MyWater getHydr damCd)','STEP 0: 장기 측정자료가 댐 단위로 제공','A(패턴) + B','관측소 경유가 아닌 dataset-댐 연결','RC-02')
for n,src,vt in [('releaseStartTime','방류시작시간','String(YYYY-MM-DD HH:MM; 시간대 미명시)'),('receivedDate','접수일자','String(YYYY-MM-DD)'),('receivedReleaseAmount','접수방류량','Number(CMS, 데이터셋 설명 근거)'),('approvalDateSource','승인년월일시분','String(YYYY-MM-DD; 값에 시각 없음)'),('remarks','비고','String(원문 그대로)'),('sourceSequenceNo','순차번호','Integer')]:
    v1('DataProperty','Approval.'+n,'Approval',vt,A,src,'Approval CSV 컬럼; Noy Step 5 p.8 (intrinsic/extrinsic properties)','A(속성 개념) + B','approvalTime/approvedReleaseAmount와의 관계는 미결정(자동 매핑 금지)','RC-03')
for n,src in [('sourceSystem','(출처 시스템명)'),('sourceFacilityCode','DAM_CD / 관측소코드'),('sourceFacilityName','DAM_NM / 관측소명')]:
    v1('DataProperty','Dam.'+n,'Dam','String',A,src,'STEP 0: 기관별 코드·이름 불일치(보 3곳 코드 상이, 명칭 표기 상이)','B','병합 근거 없음 → Dam instance를 출처별로 유지','RC-07')
for n,src,vt in [('statementVerbatim','조문/별표 셀 원문','String'),('locator','조·별표 위치','String'),('valueVerbatim','별표3 셀 원문','String'),('unit','EL.m 등','String')]:
    v1('DataProperty','Criterion.'+n,'Criterion',vt,A,src,'criterion_list.csv; Noy Step 5','A(속성 개념) + B','locator를 Criterion의 속성으로 둘지 definedIn 관계의 속성으로 둘지 미결정(근거 C, LITERATURE_CHECK_REQUIRED)','RC-04/RC-05')
for n,src in [('title','문서 제목'),('effectiveDate','시행일자'),('versionNote','훈령 번호·개정 구분')]:
    v1('DataProperty','Document.'+n,'Document','String',A,src,'규정 XML 기본정보','B','효력 기간(종료일)은 자료 없음 → 시점 적용성은 표현만 가능','RC-05')
for n,src in [('sourceSystem','출처'),('variableNamesSource','원본 변수명(DATAn 및 페이지 라벨)'),('resolution','해상도'),('periodStart','기간 시작'),('periodEnd','기간 끝')]:
    v1('DataProperty','MeasurementDataset.'+n,'MeasurementDataset','String',A,src,'measurement_dataset_list.csv; variable_dictionary.csv','A(속성 개념) + B','변수 의미 통합 금지(원본 변수명 보존)','RC-08')
for n in ['stationName','sourceSystem']: v1('DataProperty','ObservationStation.'+n,'ObservationStation','String',A,'지점명 / 출처','observation_station_list.csv','B','','RC-08')
v1('DataProperty','Dam.facilityTypeSource','Dam','String(출처 표기 그대로)',A,'DAM_BO_NM 등','MyWater/K-water 시설 유형 표기','B','클래스로 나눌지는 미결정(Noy 4.5 p.17)','RC-06')
# held
v1('Relation','upstreamOf/downstreamOf','Dam','Dam',H,'K-water 시설 소개 텍스트(단일 출처)','dam_network_evidence.csv','C','CQ에 없음; handoff §12 절차 필요(반복 필요성→문헌 검토→결정)','RC-09')
v1('Class','Organization/Actor','','',H,'홍수통제소, 시설관리자, K-water 등','규정 제2조','C','v0.1 CQ에 승인 주체 질문 없음','RC-10')
V1C=['element_type','name','domain','range_or_value_type','status','source_term_verbatim','evidence','method_evidence','open_issue','revision_candidate']
W('03_normalized/working_ontology_candidate_v1.csv',V1,V1C)
import collections
print(len(I),'instances;',len(V),'cq validations;',len(V1),'v1 rows',dict(collections.Counter(r['status'] for r in V1)))
