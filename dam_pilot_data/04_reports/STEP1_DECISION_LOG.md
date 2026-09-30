# STEP 1 Decision / Ambiguity Log

- 기준: `01_AI_RESEARCH_HANDOFF.md`(canonical). 대상: Initial Ontology v0.1 (수정하지 않음).
- 규칙: 기존 판단이 바뀌면 **이전 기록을 삭제하지 않고** 변경 이유를 "변경 이력"에 추가한다.
- 상태: RESOLVED / REVIEW_REQUIRED / LITERATURE_CHECK_REQUIRED / DATA_REQUIRED / EXPERT_REVIEW_REQUIRED / DEFERRED
- 근거 수준: **A** 문헌 직접 근거 / **B** 본 연구 적용 결정 / **C** 추가 검토 필요
- 문제 유형: **A** Ontology / **B** Data·Mapping / **C** Data Availability / **D** Literature·Methodology / **E** Expert Review

## 1. STEP 1-A 에서 발생한 항목

| ID | 발견 단계 | 쟁점 | 관련 CQ | 관련 Ontology 요소 | 관련 실제 자료 | 관련 문헌 | 현재 판단 | 근거 수준 | 유형 | 상태 | 다음 필요한 행동 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S1A-01 | 1-A | Noy & McGuinness(2001), Li et al.(2025) 원문을 이 세션에서 열람하지 못함(protege/ksl/web.stanford.edu, mdpi.com, doi.org egress 차단). Step 1 절차를 handoff 정리와 기존 지식에 의존 | 전체 | STEP 1 전체 방법론 근거 | handoff §4.1, §17 | Noy 2001; Li 2025 | Step 1의 기본 질문 틀을 사용하되, 원문 대조 전까지 "원문 직접 인용"으로 표기하지 않음 | A(handoff 정리) / 원문 대조 C | D | LITERATURE_CHECK_REQUIRED | 원문 PDF를 사용자가 제공하거나 해당 호스트 egress 허용 후 Step 1 절(기본 질문, CQ, 반복성) verbatim 대조·쪽 번호 기록 |
| S1A-02 | 1-A | Domain 정의문 초안: "댐 운영 의사결정 지원을 위한 근거 지식(관측·측정자료, 운영행위, 방류 승인, 운영기준, 근거 문서와 출처)의 의미 구조" | CQ1~6 | 전체 Class 7개 | 연구 목적 문장, STEP 0 자료 | Noy Step 1 | M 문서 §3 Q1 초안 채택 제안. 사용자 확인 전 확정하지 않음 | B | B/E | REVIEW_REQUIRED | 사용자가 문구 확인·수정 |
| S1A-03 | 1-A | domain(댐 운영 일반)과 pilot 자료 범위(한강수계, 승인 2010~2021, 측정 2019~2026 일부)의 구분; "댐"의 경계(다목적댐·용수댐·수력발전댐·홍수조절용댐·조정지·보를 모두 Dam으로 볼지) | CQ1, CQ2 | Dam | dam_catalog.csv, 별표1, K-water 시설 목록 | (미조사 — 1-C/1-D) | domain은 일반 댐 운영, 자료 범위는 pilot으로 구분해 기술. 시설 유형 경계는 미결정 | B | A/B | REVIEW_REQUIRED | 1-D 용어 도출에서 시설 유형 용어 수집; 1-F에서 검토 |
| S1A-04 | 1-A | 사용자/유지·검토 주체가 canonical에 명시되지 않음. 최종 사용자(운영자)와 Ontology 직접 소비 주체를 나눠 읽은 것은 본 연구 해석 | - | 전체 | handoff §1.1, §3 | Noy Step 1 (누가 사용·유지하는가); Li 2025 (expert review) | 임의 가정하지 않음. 최종 사용자 = 댐 운영자(handoff), 유지·검토 주체 = 미정 | C | E | EXPERT_REVIEW_REQUIRED | 사용자: 설계·유지 책임자, 검토할 도메인 전문가(분야·역할) 지정 |
| S1A-05 | 1-A | 제외 범위: canonical 명시 제외(자동 결정, rationale 추정 등) 외에 이번에 제안한 제외(예측 모형, 안전관리·수질·용수·발전 자체, 한강수계 외) | - | 범위 | handoff §1.2, §4.3 | - | canonical 명시 제외는 그대로; 제안 제외는 미확정 | B(제안) | E | REVIEW_REQUIRED | 사용자 확인 |
| S1A-06 | 1-A | 상·하류 관계가 Ontology scope에 포함되는지. 실제 공식 서술 evidence는 있으나 CQ1~6에 상·하류 질문이 없고 v0.1에 Relation 없음 | (없음) | (신규 Relation 후보 — 추가하지 않음) | dam_network_evidence.csv(11건, 단일 출처) | (미조사) | 자동 추가 금지. canonical §12 절차(반복 필요성 확인 → 문헌 검토 → 결정) 유지 | C | A/D | DEFERRED | 1-B에서 CQ와의 관련성 확인 후 필요 시 문헌 검토 |
| S1A-07 | 1-A | **Criterion 시점 적용성**: 연구 목적이 "당시의" 기준을 요구하나 확보한 Criterion은 2026-07-08 시행 현행본뿐, 대표 Approval 사례는 2019~2020 | CQ4, CQ5 | Criterion, Document, (Criterion–시점 표현 여부) | criterion_list.csv, linkage_pilot_cases.csv | - | 2020 승인 ↔ 2026 기준 연결은 주장하지 않음. 시점 표현이 Ontology에 필요한지 미결정 | B(목적) / 자료 C | B/C | DATA_REQUIRED | 당시 시행 버전(연혁) 확보 가능성 조사 — 별도 gap-filling 필요, 이후 STEP 1-F/G에서 표현 방식 검토 |
| S1A-08 | 1-A | 이전 산출물(K, L, linkage_pilot_cases.csv, STEP0_summary 5-1)에서 "Criterion·Document 연결"이 시점 적용성을 암시 | CQ4 | Criterion | 위 파일들 | - | 해당 연결을 "시설명 기준의 대조(현행 버전; 당시 적용성 미검증)"로 정정 주석 추가. 기존 문장은 삭제하지 않음 | - | B | RESOLVED (문서 정정만; 근본 쟁점은 S1A-07) | — |
| S1A-09 | 1-A | Operation: 개념은 scope에 두지만 실제 instance 없음. Approval·비고·접수방류량·총방류량 변화로 추론 금지 | CQ2, CQ3, CQ4, CQ5 | Operation 및 관련 Relation 4개 | (없음) | - | 미검증 유지 | B | C | DATA_REQUIRED | 별도 targeted gap-filling (Operation instance) |
| S1A-10 | 1-A | 행위자(홍수통제소장·시설관리자·관계기관·운영기관)가 규정·자료에 등장하나 v0.1에 대응 개념 없음 | CQ3(승인 주체), CQ5 | (신규 후보 — 추가하지 않음) | 규정 제2조, 승인 파일 제공기관 표기, dam_catalog.csv | (미조사) | 결정하지 않음. 1-D 용어 도출에서 용어로만 수집 | C | A | DEFERRED | 1-D |
| S1A-11 | 1-A | 측정 시계열 저장 방식 미결정. Ontology는 Dam–Station–Dataset 수준 연결을 scope로 둔다는 경계 제안 | CQ1, CQ6 | MeasurementDataset, ObservationStation | handoff §6.3, 측정 dataset 71개 | GraphAide(handoff §7.3; STEP 3) | 저장 방식은 결정하지 않음 | B | A/D | DEFERRED | 1-F/1-H |
| S1A-12 | 1-A | handoff §4.2의 "대표 운영 상황 정의 → 대표 사용자 질문 정의" 단계가 이번 지침 1-A~J에 별도로 없음; 1-C(기존 Ontology 재사용 검토)는 handoff 흐름에 없는 추가 | - | STEP 1 흐름 | handoff §4.1~4.2 | Noy (재사용 단계) | 충돌로 보지 않음(비차단). 대표 운영 상황/대표 사용자 질문을 1-B에서 CQ와 함께 다룰지 확인 필요 | B | D | REVIEW_REQUIRED | 사용자 확인 (1-B 범위) |

## 2. STEP 0 에서 이월된 불확실성 (지침 §11 A~G)

| ID | 발견 단계 | 쟁점 | 관련 CQ | 관련 Ontology 요소 | 관련 실제 자료 | 관련 문헌 | 현재 판단 | 근거 수준 | 유형 | 상태 | 다음 필요한 행동 / 예정 단계 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S0-A | 0 | Criterion temporal validity | CQ4,5 | Criterion, Document | 위 S1A-07 | - | S1A-07로 통합 관리 | B/C | B/C | DATA_REQUIRED | 연혁 버전 확보 조사 |
| S0-B | 0 | `접수방류량`=`approvedReleaseAmount`? `승인년월일시분`=`approvalTime`(값에 시각 없음)? `접수일자`, `방류시작시간`, `비고`의 위치 | CQ3 | Approval.approvalTime, approvedReleaseAmount | approval_records_hrfco_raw_fields.csv, J 보고서 | (미조사) | 확정하지 않음. 원본 필드명·값 보존 | C | A/B | REVIEW_REQUIRED | STEP 1-F(Property 검토); 출처 정의 추가 확인 |
| S0-C | 0 | Station–Dataset: 장기 측정은 dam-level(getPeriod/getHydr); `hasDataset` 직접 확인 안 됨 | CQ1, CQ6 | ObservationStation–hasDataset | L 보고서, I 보고서 | (미조사) | 미확정 | C | A/B | REVIEW_REQUIRED | STEP 1-F/1-H |
| S0-D | 0 | 시설 식별: 같은 코드·다른 이름, 같은 이름·다른 코드(보 3곳) | CQ2~CQ6 | Dam.damId | approval_facility_code_crosswalk.csv | - | 자동 통합 금지 | B | B | REVIEW_REQUIRED | STEP 1-E/1-H |
| S0-E | 0 | 시간 규약: hour=24, timezone, 방류시작시간/승인일/접수일, SDATE 라벨 | CQ1, CQ3, CQ6 | Operation.operationTime, Approval.approvalTime 등 | time_conventions.csv | - | 보정·변환하지 않음 | C | B | REVIEW_REQUIRED | STEP 1-G/1-H; 출처 정의 확인 |
| S0-F | 0 | 상·하류 Relation 부재 | - | (후보) | dam_network_evidence.csv | (미조사) | S1A-06으로 관리 | C | A/D | DEFERRED | S1A-06 |
| S0-G | 0 | Operation instance 없음 | CQ2~5 | Operation | - | - | S1A-09로 관리 | B | C | DATA_REQUIRED | S1A-09 |

## 3. 변경 이력
| 날짜 | ID | 변경 | 이유 |
|---|---|---|---|
| 2026-09-30 | S1A-08 | 신규 등록 | K/L 문서·linkage_pilot_cases.csv의 Criterion "연결" 표현이 §11-A와 어긋남을 STEP 1-A 점검에서 발견 |
