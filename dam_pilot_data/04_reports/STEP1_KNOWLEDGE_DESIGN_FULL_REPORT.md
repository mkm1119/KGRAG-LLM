# STEP 1 — Knowledge Design 전체 보고서 (1-A ~ 1-J)

- 작성일: 2026-09-30. 실행 근거: 마스터 실행 지침, canonical `01_AI_RESEARCH_HANDOFF.md`(저장소 밖 업로드 폴더 보관).
- **Initial Ontology v0.1(7 Class / 8 Relation / 9 Data property)은 덮어쓰지 않았다.** 모든 변경은 `working_ontology_candidate_v1.csv`의 후보(CANDIDATE_ADDITION/HELD)로만 기록했다. CQ1~CQ6 문구도 수정하지 않았다.
- 문헌 원문 대조와 A/B/C 분류: `STEP1_METHOD_EVIDENCE.md` (A 문헌 직접 / B 본 연구 적용 / C 검토 필요). 이 보고서의 "A/B/C"는 같은 기준이다.
- Hard Stop: STEP 1에서 발생하지 않았다(§11).

## 0. 단계 대응표 (문헌 vs 본 연구)
| 본 연구 substep | Noy 대응 | 근거 수준 | 산출물 |
|---|---|---|---|
| 1-A Domain/Scope | Step 1 (p.5) | A | `M_STEP1A_DOMAIN_SCOPE.md` |
| 1-B CQ 검토 | Step 1 CQ (p.5) | A(CQ의 역할)+B(검토 기준) | `N_STEP1B_COMPETENCY_QUESTION_REVIEW.md`, `step1_cq_review_matrix.csv` |
| 1-C 기존 Ontology 검토 | Step 2 (p.5–6) | A | §3 (원문 미독 항목은 LITERATURE_CHECK_REQUIRED) |
| 1-D 용어 도출 | Step 3 (p.6) | A | `step1_term_inventory.csv` (163) |
| 1-E/F Class·Property 검증 | Step 4–5 (p.6–9) | A(원칙)+B(판정 코드) | `step1_ontology_element_validation.csv` (24) |
| 1-G 제약 후보 | Step 6 (p.9–11) | A(facet 개념)+B | 요소 검증표 `constraint_candidate_1G` 열 |
| 1-H 대표 instance | Step 7 (p.11) | A(개념)+B(실제 record 사용) | `step1_representative_instances.csv` (15) |
| 1-I CQ 검증 | Step 1의 litmus test (p.5) | A(개념)+B(5분류) | `step1_cq_validation.csv` |
| 1-J 전문가 검토 대상 | (Noy: 전문가 논의 p.4) / Li p.9–12 / DDKG p.8 | 절차는 문헌에 없음 → B/C | §10 |

## 1. STEP 1-A — Domain/Scope (요약)
- Domain 정의(제안, S1A-02): 댐 운영 의사결정 지원을 위한 근거 지식(관측·측정자료, 운영행위, 방류 승인, 운영기준, 근거 문서와 출처)의 의미 구조. 결정 지원이며 자동 방류 결정이 아니다.
- 자료 범위(한강수계 pilot)와 domain(일반 댐 운영)을 구분. 미결정 항목은 결정 로그 S1A-xx 유지(RESOLVED 변경 없음).

## 2. STEP 1-B — CQ 검토
CQ1 KEEP_WITH_REVIEW, CQ2 KEEP, CQ3 REVISION_CANDIDATE(승인 접근 경로가 Operation 경유뿐), CQ4 REVISION_CANDIDATE("당시의" 시점 조건 부재), CQ5 KEEP_WITH_REVIEW(세 대상 혼합), CQ6 KEEP_WITH_REVIEW.
CQ GAP CANDIDATE: G-1 Operation 없이 시설·시점으로 접근, G-2 시점 적용성, G-3 상·하류 맥락(목적상 필요 여부 미결), G-4 측정값 성격. 상세: N 문서. 적용하지 않음.

## 3. STEP 1-C — 기존 Ontology 재사용 검토
- **원문으로 확인한 것(A):** OntoDSMS는 Noy의 단계를 적용하고 SSN/SOSA를 재사용한다고 서술한다. DDKG는 자체 DDO(최상위 c1 Dam…c7)를 정의하며 Noy를 인용하지 않는다. Li et al.은 seed 온톨로지를 전문가가 정의하고 기존 온톨로지와의 비교를 서술한다(`STEP1_METHOD_EVIDENCE.md` §2).
- **검색으로만 식별, 원문 미독(C, LITERATURE_CHECK_REQUIRED):** SOSA/SSN 명세, PROV-O, HY_Features/WaterML2, OFPO/KGFPO, Digital Watersheds. 이 후보들을 **본 연구 Ontology에 자동 import하지 않는다**. 재사용 여부는 (i) 원문 대조, (ii) 사용자 결정 후 검토한다.
- 판단: 기존 온톨로지 중 어느 것도 이 연구의 5개 지식 종류(측정·운영·승인·기준·문서)를 한 번에 커버한다고 확인된 바 없음. 그러나 "없다"는 결론도 내리지 않는다(조사 범위 한계).
- 로그: S1C-01(재사용 후보 목록 미검증), S1C-02(SSN/SOSA와 MeasurementDataset/ObservationStation의 관계는 원문 확인 후 검토).

## 4. STEP 1-D — 용어 도출
`step1_term_inventory.csv` 163개 용어. 출처: 규정 XML, 승인 CSV 컬럼·비고, MyWater 변수명, 시설 유형 표기. 원문 표기 그대로 수집했고 클래스/속성으로 미리 분류하지 않았다(Noy Step 3: 중복·관계·클래스 여부 고민 없이 나열). 규정 텍스트 빈도는 CDATA 제거 후 계산.
주요 관찰: '운영행위'라는 용어는 규정에 1회뿐이며, 행위는 '수문조작', '방류량 조정' 등으로 서술된다. '기상'은 규정에서 1회 등장. 행위자(홍수통제소장 등)가 반복 등장하지만 v0.1에는 대응 개념이 없다(보류 RC-10).

## 5. STEP 1-E/F — Class·Relation·Property 검증 (24개 요소)
| 판정 | 요소 |
|---|---|
| KEEP | Dam, Approval, Criterion, Document, ObservationStation, definedIn, stationId, datasetId, documentId |
| REVIEW_REQUIRED | MeasurementDataset, documentedBy, monitoredBy, hasDataset, Dam.damId, Approval.approvalTime, Approval.approvedReleaseAmount, ObservationStation.variableType |
| NOT_TESTABLE | Operation, targetDam, relatedApproval, relatedCriterion, recordedIn, operationTime, operationType |
- NOT_TESTABLE = 실제 Operation record가 없어 실제 자료로 검증 불가(요소 제거 사유 아님).
- 핵심 문제: (1) Approval·MeasurementDataset이 Dam에 직접 연결되는 경로가 없음 → `concernsDam` 후보(RC-01/02). (2) Approval 필드(접수방류량, 승인년월일시분, 접수일자, 방류시작시간, 비고)의 의미가 v0.1 속성과 1:1로 대응하지 않음 → 원문 필드 보존형 속성 후보(RC-03). (3) 장기 측정자료는 댐 단위이며 관측소 단위 dataset이 없어 hasDataset이 실제로 확인되지 않음. (4) Dam 식별은 출처별.

## 6. STEP 1-G — 제약 후보 (Noy Step 6: value type, allowed values, cardinality, domain/range)
후보만 기록(확정 아님). 상세는 요소 검증표의 `constraint_candidate_1G`.
- 확정하지 않는 것: `approvalTime` 값 유형(date vs dateTime — 원본에는 날짜만), `approvedReleaseAmount` 단위·의미, `operationType` 허용값, 시간대·hour=24 규약. 출처 의미가 불명확한 값을 임의로 제약하면 오류가 고정되므로 미고정.
- 제안 가능한 것: `definedIn` domain=Criterion, range=Document; Criterion당 문서 ≥1; `variableType` 후보값 {우량, 수위}는 관찰된 두 값이며 허용값 확정 아님.
- Noy가 경고한 "overly general domain/range"(p.10–11)를 피하기 위해 concernsDam은 Approval/MeasurementDataset로 한정해 제안.

## 7. STEP 1-H — 실제 record 기반 대표 instance
`step1_representative_instances.csv` 15건(충주·횡성·소양강). v0.1로 표현 가능한 부분과 불가능한 부분을 분리. I-11은 **2020 승인 ↔ 2026 기준 연결을 주장하지 않음**을 명시(NOT_ASSERTED).
- 발견: 같은 충주댐 코드(1003110)가 승인 CSV(관측소코드)와 MyWater(DAM_CD)에 있으나 동일 시설 확정은 아님 → Dam instance 2개로 둠(I-01/I-02).
- 승인 3412(접수방류량 3000)와 3519(7000, 비고에 당초 3000·변경 기간)는 같은 방류시작시간을 가지며 접수일자가 다르다. 비고는 원문 그대로 보존, 관계(수정 승인인지)를 추론하지 않음.

## 8. STEP 1-I — CQ 검증 (v0.1 + 실제 자료)
문제 분류: ONTOLOGY_REVISION_CANDIDATE / DATA_AVAILABILITY / SOURCE_SEMANTIC / CQ_REVISION_CANDIDATE / KG_OR_RETRIEVAL_ISSUE.
| CQ | 분류 | 요지 |
|---|---|---|
| CQ1 | ONTOLOGY_REVISION_CANDIDATE | 댐 단위 dataset을 Dam에 잇는 경로 필요 |
| CQ2 | DATA_AVAILABILITY | Operation record 없음; 스키마 문제 아님 |
| CQ3 | ONTOLOGY_REVISION_CANDIDATE + CQ_REVISION_CANDIDATE | Approval→Dam 부재 |
| CQ4 | ONTOLOGY_REVISION_CANDIDATE + DATA_AVAILABILITY | 값·시점 속성; 당시 버전 자료 없음 |
| CQ5 | 부분 OK + SOURCE_SEMANTIC | Criterion→Document 15/15; 승인 문서 연결은 파일 수준 |
| CQ6 | ONTOLOGY_REVISION_CANDIDATE | dataset 속성; 관측소 단위 자료 없음 |
가장 큰 구조적 결론: **Operation이 부재한 현재 자료에서는 v0.1 경로(모든 것이 Operation 경유)로는 CQ2 외 어떤 CQ도 실제 자료로 답할 수 없다.** 후보 v1은 이를 Operation 없이 시설로 접근하는 `concernsDam`으로 완화하나, canonical architecture(Ontology-KG-Hybrid Retrieval-LLM)는 변경하지 않는다.

## 9. Working Ontology Candidate v1
`working_ontology_candidate_v1.csv`: 52행 = v0.1 유지 24 + 후보 추가 26 + 보류 2. 후보는 모두 실제 자료 근거와 근거 수준(A/B)을 표기. 보류: upstream/downstream(RC-09, 근거는 단일 출처 서술), Actor/Organization(RC-10). 이 v1은 **작업용**이며 확정 Ontology가 아니다.

## 10. STEP 1-J — 전문가 검토 대상
문헌: Li et al.은 전문가가 seed와 최종 domain/range를 검토했고(p.9–12), DDKG는 전문가 검증을 OHCF에 포함(p.8). 검토 절차·인원·기준은 문헌이 우리에게 규정하지 않으므로 **프로토콜을 만들지 않았다**. 검토를 요청할 대상만 나열한다:
1. `접수방류량`·`승인년월일시분`·`접수일자`·`방류시작시간` 의미(한강홍수통제소/데이터 제공기관)
2. 승인 파일 관측소코드와 MyWater DAM_CD의 동일 시설 여부
3. 규정 개정 연혁과 당시 적용 기준(S1A-07)
4. '운영행위' 정의(수문조작/방류/조정), Operation record 소재
5. 상·하류 관계의 필요성과 출처, 행위자 개념
6. 유입량·저수율 등 출처별 변수 정의 차이
7. concernsDam 등 candidate 관계의 domain/range

## 11. Hard Stop 점검 (STEP 1 종료 시점)
| 조건 | 판정 |
|---|---|
| 핵심 논문이 handoff 주장을 지지하지 않음 | 없음. 단 범위 차이 D1–D6(`STEP1_METHOD_EVIDENCE.md`)와 LSMKG 원문 부재 → STEP 3에서 다룸 |
| canonical architecture 변경 필요 | 없음 |
| v0.1 핵심의 대폭 변경 필요 | 없음(추가 후보 중심; Approval→Dam 경로 부재가 가장 큼) |
| 다수의 신규 Class/Relation 필요 | 아님(신규 Relation 1종 + 속성, Class 신규 0; 보류 2) |
| Operation/Relation/Approval 의미 추론 필요 | 회피(미확정 유지) |
| 최소 검증 데이터 부족 | Approval·Measurement·Criterion·Document는 충분; Operation만 부재(NOT_TESTABLE로 처리) |
→ **Hard Stop 없음. STEP 2로 진행.**

## 12. 남은 미결(요약)
S1A-04(유지 주체), S1A-05(제외 범위), S1A-06(상·하류), S1A-07(시점 적용성), S1A-09(Operation), S0-B~E. 모두 RESOLVED로 바꾸지 않았다.
