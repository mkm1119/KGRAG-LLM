#!/usr/bin/env python3
"""STEP 1 tables (authored analysis). Initial Ontology v0.1 is NOT modified; candidates are separate rows/statuses."""
import csv
def W(path,rows,cols):
    with open(path,'w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); [w.writerow({c:r.get(c,'') for c in cols}) for r in rows]
# ------------------------------------------------------------------ 1-B CQ review matrix
CQ={
'CQ1':"대상 댐의 특정 시점·기간의 수문·기상 상태를 확인하기 위해 어떤 관측자료가 연결되어 있는가?",
'CQ2':"특정 시점·기간에 대상 댐에서 어떤 운영행위가 이루어졌는가?",
'CQ3':"해당 운영행위와 관련된 방류 승인은 무엇인가?",
'CQ4':"해당 운영행위와 관련된 운영기준은 무엇인가?",
'CQ5':"해당 운영·승인·기준은 어떤 문서에서 확인할 수 있는가?",
'CQ6':"해당 운영 시점의 강우·유입량·저수위·방류량은 어떤 관측소·측정자료를 통해 확인할 수 있는가?"}
M=[
dict(cq_id='CQ1',cq_text=CQ['CQ1'],purpose_relevance="직접: 목적 문장의 '현재 댐의 기상·수문 상태를 파악'에 대응",scope_fit="1-A scope 안(관측소·측정 dataset과 댐의 연결)",knowledge_types_needed="관측·측정자료(변수·기간·출처), 댐과 자료의 연결 (※ 현재 Ontology Class와 동일시하지 않음)",overlap_with_other_cqs="CQ6과 부분 중복: CQ6은 운영 시점·특정 변수로 좁힌 하위 질문 성격",domain_need_independent_of_data="강함: 규정 제11조(상시 모니터링), 제13조(월별 저수위·유입량·방류량 실적) 등 자료 기반 운영이 규정된 domain",problems="(a) '연결된 관측자료'를 묻는데 목적은 '상태 파악'(값)까지 포함 → 연결 정보와 값 조회의 경계가 문구에 없음 (b) '기상'의 범위(관측만인지 예보 포함인지) 미정 — 1-A Q7-b와 연결 (c) '현재'(실시간) vs 이력 구분 미정(handoff §6.3)",verdict='KEEP_WITH_REVIEW',revision_or_scope_note="CQ REVISION CANDIDATE 아님. 'CQ1–CQ6 관계 정리'(CQ1을 상위, CQ6을 운영 시점 한정 질문으로 볼지)는 사용자 확인 사항. SCOPE REVISION CANDIDATE: '기상'의 범위(SR-1)",method_evidence="A: CQ는 scope 도구·litmus test(Noy p.5) / B: 평가 기준",log_ids='S1B-01, S1B-02'),
dict(cq_id='CQ2',cq_text=CQ['CQ2'],purpose_relevance="직접: '과거 운영행위'",scope_fit="1-A scope 안(개념 포함; instance는 DATA_REQUIRED)",knowledge_types_needed="운영행위(무엇이 언제 어느 댐에서), 시점·대상",overlap_with_other_cqs="없음(CQ3–CQ6의 anchor 역할)",domain_need_independent_of_data="강함: 규정 제6조② 수문조작, 제14조 방류량 조정·통보",problems="'운영행위'의 정의·유형이 CQ에 없음(→1-D/1-F에서 다룸). 실제 instance 부재는 데이터 문제이며 CQ 부적절의 근거가 아님. 승인·측정으로부터 추론 금지",verdict='KEEP',revision_or_scope_note="-",method_evidence="B",log_ids='S1B-03'),
dict(cq_id='CQ3',cq_text=CQ['CQ3'],purpose_relevance="직접: '당시의 승인'",scope_fit="1-A scope 안",knowledge_types_needed="방류 승인(승인 시점, 대상 시설, 방류 시작·량, 특이사항)",overlap_with_other_cqs="CQ4·CQ5·CQ6과 '해당 운영행위/운영 시점' anchor를 공유",domain_need_independent_of_data="강함: 규정 제6조② '홍수통제소장의 사전 승인'; 승인 자료 3,929건",problems="승인에 이르는 경로가 **운영행위 경유 하나뿐**임. STEP 0에서 승인은 운영행위 record 없이 시설·일시 기준으로 존재·조회되며, '2020-08 충주댐에 어떤 방류 승인이 있었나' 같은 자연스러운 질문이 이 CQ 문구로는 표현되지 않음(목적의 '운영행위와 당시의 승인을 연결'과 접근 경로를 구분할 필요)",verdict='REVISION_CANDIDATE',revision_or_scope_note="CQ REVISION CANDIDATE(적용 안 함): '특정 댐·시점(또는 해당 운영행위)과 관련된 방류 승인은 무엇인가?'",method_evidence="B(근거: STEP 0 실제 자료 + 규정 제6조②)",log_ids='S1B-04'),
dict(cq_id='CQ4',cq_text=CQ['CQ4'],purpose_relevance="직접: '당시의 … 운영기준'",scope_fit="1-A scope 안이나 '운영기준'의 범위(규정만? 댐별 관리규정·지침?) 미확정",knowledge_types_needed="운영기준(값·규정 내용), 적용 대상 시설, **적용 시점/버전**",overlap_with_other_cqs="CQ3과 anchor 공유; CQ5와 근거 문서 부분 중복",domain_need_independent_of_data="강함: 규정 제6조② 홍수기 제한수위 준수, 별표3; 규정은 2018·2024·2026년 개정 이력이 있음(부칙)",problems="목적은 '**당시의**' 기준을 요구하나 CQ4에는 시점 적용 조건이 없어, 현행 기준을 답해도 CQ상 문제가 없음 → 목적과 CQ의 불일치. STEP 0에서 실제로 현행(2026-07-08) 버전만 확보(시점 적용성 미검증). '관련된'(중립)의 판정 방식(시설 대응/시기 대응) 미정",verdict='REVISION_CANDIDATE',revision_or_scope_note="CQ REVISION CANDIDATE(적용 안 함): '…당시 적용되던 운영기준은 무엇인가?'. 데이터: 개정 연혁 확보 필요(DATA_REQUIRED)",method_evidence="B(근거: 목적 문장 + 규정 부칙 개정 이력 + STEP 0)",log_ids='S1B-05'),
dict(cq_id='CQ5',cq_text=CQ['CQ5'],purpose_relevance="직접: '근거자료' 및 근거 기반 판단 지원",scope_fit="1-A scope 안",knowledge_types_needed="문서(출처), 문서 내 위치, (버전)",overlap_with_other_cqs="CQ3·CQ4의 근거 문서와 부분 중복(각 항목의 출처를 묻는 종합 질문)",domain_need_independent_of_data="강함: 연구 핵심(근거 추적), 규정·승인 기록·운영 기록의 출처가 서로 다름",problems="한 CQ에 운영·승인·기준 세 대상을 묶어 목적이 혼합됨(출처 종류가 다름: 규정 조문 / 승인 데이터 / 운영 기록). '문서'의 범위(원문서 vs 데이터셋 파일)와 문서 내 위치·버전 요구가 문구에 없음",verdict='KEEP_WITH_REVIEW',revision_or_scope_note="CQ REVISION CANDIDATE 가능성: 대상별 분리(적용 안 함, 사용자 판단)",method_evidence="B",log_ids='S1B-06'),
dict(cq_id='CQ6',cq_text=CQ['CQ6'],purpose_relevance="직접: '수문·기상 상태'를 운영 시점에 연결",scope_fit="1-A scope 안",knowledge_types_needed="측정자료(강우·유입량·저수위·방류량), 자료를 제공하는 관측소·경로, 시점",overlap_with_other_cqs="CQ1의 구체화(부분 중복)",domain_need_independent_of_data="강함: 규정 제13조가 저수위·유입량·방류량 실적을 명시",problems="(a) 변수 4종을 열거 — 도메인 근거(제13조)는 있으나 변수 의미가 source마다 달라(방류량=총방류량/발전방류 등) CQ 밖의 쟁점 (b) '어떤 관측소…를 통해'는 관측소 경유를 전제하나 실제 장기 자료는 댐 단위 제공 → 데이터 구조에 대한 의존 가능성(경미) (c) '해당 운영 시점' anchor(CQ3과 같은 접근 경로 문제)",verdict='KEEP_WITH_REVIEW',revision_or_scope_note="-",method_evidence="B",log_ids='S1B-07'),
]
CQ_COLS=['cq_id','cq_text','purpose_relevance','scope_fit','knowledge_types_needed','overlap_with_other_cqs','domain_need_independent_of_data','problems','verdict','revision_or_scope_note','method_evidence','log_ids']
W('03_normalized/step1_cq_review_matrix.csv',M,CQ_COLS)
# ------------------------------------------------------------------ 1-E/F element validation
E=[]
def e(t,name,v01,indep,cq,data,lit,issue,noy,verdict,c1g,logs=''):
    E.append(dict(element_type=t,element=name,v01_definition=v01,independent_meaning_in_domain=indep,needed_by_cq=cq,appears_in_actual_data=data,supported_by_literature_or_regulation=lit,modeling_adequacy_issue=issue,noy_principle_referenced=noy,verdict=verdict,constraint_candidate_1G=c1g,log_ids=logs))
# classes
e('Class','Dam','Class','Y — 독립적 존재를 가진 시설(Noy Step 4 기준)','CQ1–CQ6 (대상)','MyWater 시설 11개(DAM_CD), 승인 파일 시설 16개(관측소코드), KHNP 이름 7개','DDKG: 최상위 클래스 c1 Dam이며 다른 최상위 클래스를 모두 Dam에 연결(p.4); 규정 별표1 시설 목록','시설 유형(다목적댐/용수댐/수력발전댐/홍수조절용댐/보/조정지)을 클래스로 나눌지 속성값으로 둘지 미결정(Noy 4.5 p.17: "usually in the scope"); 기관별 시설 ID가 달라 하나의 Dam으로 병합할 수 없음','Noy Step 4 p.7–8, 4.5 p.17','KEEP','-','S1E-01')
e('Class','Operation','Class','Y(개념) — 시점·대상을 갖는 행위','CQ2–CQ6 (anchor)','없음(독립 record 미확보)','규정 제6조②(수문조작), 제14조(방류량 조정·통보)는 행위를 서술; 문헌 온톨로지에서는 확인 안 됨','정의·유형·경계(수문조작 / 방류 / 방류량 조정)가 미정. Approval과 동일시 금지','Noy 4.5 p.17','NOT_TESTABLE','-','S1E-02')
e('Class','Approval','Class','Y — 홍수통제소장이 내리는 승인 기록(순차번호를 가진 record)','CQ3','3,929건(2010-07-16~2021-07-16)','규정 제6조② "홍수통제소장의 사전 승인"','v0.1에서 Approval은 Operation을 거쳐서만 Dam에 도달(Approval→Dam 경로 없음). 실제 자료는 시설 정보를 record가 직접 가짐','Noy Step 5 p.8 (relationships to other individuals)','KEEP','-','S1E-03')
e('Class','Criterion','Class','PARTIAL — 문서에 정의된 기준. 단위가 조문인지 (시설별) 값인지 미정','CQ4','15건(별표3 홍수기 제한수위 9개 댐 + 6개 조문)','규정 제6조②, 별표3','granularity(조문 vs 시설별 값), 값·단위·적용 시점을 담을 속성 부재','Noy 4.5 p.17','KEEP','-','S1E-04')
e('Class','Document','Class','Y — 독립된 문서/파일','CQ5','45건(법령 XML·원본 PDF/HWPX·웹 스냅샷)','규정 자체','한 문서의 표현(XML/PDF/HWPX)이 여러 파일; 버전(시행일자)·문서 내 위치를 담을 곳 없음','Noy Step 5 p.8','KEEP','-','S1E-05')
e('Class','ObservationStation','Class','Y — 물리적 관측지점','CQ1, CQ6','우량·수위관측소 94개(MyWater getRain)','OntoDSMS: Sensor/Observation(SOSA)를 확장해 사용(p.4–5)','실제 장기 측정자료는 댐 단위 → 관측소와 dataset의 연결이 직접 확인되지 않음','Noy 4.5 p.17','KEEP','-','S1E-06')
e('Class','MeasurementDataset','Class','PARTIAL — 측정값 집합(논리적 객체); dataset 단위(출처×시설×변수×해상도×기간)는 연구자 정의','CQ1, CQ6','71개(연구용 임시 단위)','OntoDSMS는 모니터링 데이터를 DB 인스턴스로 다룸(p.6–7); "dataset" 클래스의 직접 선례는 확인되지 않음','dataset의 의미·단위 미정','Noy 4.5 p.17','REVIEW_REQUIRED','-','S1E-07')
# relations
e('Relation','targetDam','Operation→Dam','-','CQ2–CQ6','Operation instance 없음','-','-','Noy Step 6 p.10 (domain/range)','NOT_TESTABLE','domain=Operation, range=Dam; cardinality 미결정(연계운영으로 복수 댐일 가능성 — 자료 없음)','S1E-08')
e('Relation','relatedApproval','Operation→Approval','-','CQ3','없음','-','중립 의미 유지(basedOn 등으로 변경 금지). 실제 자료에서 한 방류에 복수 승인이 반복됨(예: AP-3412·AP-3519가 같은 방류시작시간) → 1:N 가능성','Noy Step 6 p.9 (cardinality)','NOT_TESTABLE','domain=Operation, range=Approval; N:M 후보','S1E-09')
e('Relation','relatedCriterion','Operation→Criterion','-','CQ4','없음','-','중립 의미 유지','Noy Step 6','NOT_TESTABLE','domain=Operation, range=Criterion','S1E-10')
e('Relation','recordedIn','Operation→Document','-','CQ5','없음','-','-','Noy Step 6','NOT_TESTABLE','domain=Operation, range=Document','S1E-11')
e('Relation','documentedBy','Approval→Document','-','CQ5','승인 record의 출처는 파일 데이터셋(data.go.kr 15085926)뿐, record별 문서 식별자 없음','-','파일 단위 출처를 "문서화"로 볼지 판단 필요(provenance와 혼동 위험)','Noy Step 6','REVIEW_REQUIRED','domain=Approval, range=Document','S1E-12')
e('Relation','definedIn','Criterion→Document','-','CQ4, CQ5','15/15 Criterion이 원문 조문·별표 위치와 파일을 가짐','규정 자체','Document 식별: 같은 문서의 XML/PDF/HWPX','Noy Step 6','KEEP','domain=Criterion, range=Document; Criterion당 문서 ≥1(문서 버전 미결정)','S1E-13')
e('Relation','monitoredBy','Dam→ObservationStation','-','CQ1, CQ6','MyWater가 댐별로 우량/수위관측소를 나열(94개)','OntoDSMS: 센서 분포에 따라 댐 구조 계층을 구성(p.5) [성격 유사, 도메인 다름]','출처의 "댐 아래 나열"이 monitoredBy의 의미와 같은지 판단 필요(수문학적 인접성 미검증)','Noy Step 5 p.8 (relationships)','REVIEW_REQUIRED','domain=Dam, range=ObservationStation','S1E-14')
e('Relation','hasDataset','ObservationStation→MeasurementDataset','-','CQ1, CQ6','관측소 단위 시계열 없음(getRain은 종료 시점 1건); 시계열은 댐 단위','-','현 자료로는 직접 확인되지 않음','Noy Step 6','REVIEW_REQUIRED','domain=ObservationStation, range=MeasurementDataset','S1E-15')
# data properties
e('DataProperty','Dam.damId','Dam→value','-','CQ1–CQ6','MyWater DAM_CD, 승인 파일 관측소코드(보 3곳은 코드 상이)','-','출처별 ID가 달라 하나의 ID로 정의 불가; 병합 근거 없음','Noy Step 6 (value type String)','REVIEW_REQUIRED','value type String; 출처 범위(system) 필요','S1E-16')
e('DataProperty','Operation.operationTime','Operation→value','-','CQ2','없음','-','instant/interval, 시간대 미정','Noy Step 6','NOT_TESTABLE','value type 미정','S1E-17')
e('DataProperty','Operation.operationType','Operation→value','-','CQ2','없음','-','허용값 미정; 승인 비고로부터 추론 금지','Noy Step 6 (enumerated)','NOT_TESTABLE','allowed values 미정','S1E-18')
e('DataProperty','Approval.approvalTime','Approval→value','-','CQ3','승인년월일시분(값은 날짜만), 접수일자(62건에서 상이)','-','시각 없음·시간대 미명시·접수일자와의 관계 미정','Noy Step 6','REVIEW_REQUIRED','value type 미정(date vs dateTime)','S1E-19')
e('DataProperty','Approval.approvedReleaseAmount','Approval→value','-','CQ3','접수방류량(CMS; 공란 4건)','-','원본 명칭이 "접수"; 승인량과 동일 여부 미검증','Noy Step 6','REVIEW_REQUIRED','value type Number, unit CMS(설명 근거); 의미 확정 불가','S1E-20')
e('DataProperty','ObservationStation.stationId','ObservationStation→value','-','CQ1, CQ6','OBS_CD 94개','-','출처 범위 필요','Noy Step 6','KEEP','value type String','S1E-21')
e('DataProperty','ObservationStation.variableType','ObservationStation→value','-','CQ6','관측소 유형: 우량(A)/수위(C)','-','"variableType"이 관측 변수를 뜻하는지 관측소 유형인지 불명; 출처마다 수위 단위·의미 다름','Noy Step 6 (enumerated)','REVIEW_REQUIRED','allowed values 후보 {우량, 수위}(자료 관찰)','S1E-22')
e('DataProperty','MeasurementDataset.datasetId','MeasurementDataset→value','-','CQ1, CQ6','연구용 임시 ID','-','dataset 단위 정의 필요','Noy Step 6','KEEP','value type String','S1E-23')
e('DataProperty','Document.documentId','Document→value','-','CQ5','연구용 임시 ID + sha256','-','-','Noy Step 6','KEEP','value type String','S1E-24')
EL_COLS=['element_type','element','v01_definition','independent_meaning_in_domain','needed_by_cq','appears_in_actual_data','supported_by_literature_or_regulation','modeling_adequacy_issue','noy_principle_referenced','verdict','constraint_candidate_1G','log_ids']
W('03_normalized/step1_ontology_element_validation.csv',E,EL_COLS)
print(len(M),'CQs;',len(E),'elements')
