# I. Ontology Compatibility Report (STEP 0)

기준: `01_AI_RESEARCH_HANDOFF.md`의 현재 Ontology (Class 7개, Relation 8개, Data Property 9개). **Ontology·KG는 수정/구축하지 않았다.**
아래 분류는 실제 수집 자료에 대해서만 판단했다. 새 개념은 "제안(HOLD)"으로만 적으며 채택 여부는 `03_PILOT_METHOD_EVIDENCE_CHECKLIST` 절차(G1~G6)를 거쳐야 한다.

분류 코드: **OK** = 현재 Ontology로 표현 가능(실제 instance 확보) / **AMBIG** = 표현은 되나 의미가 애매 / **NO-EXPR** = 현재 Ontology로 표현 불가 / **NOT-OBTAINED** = 현재 수집 환경에서는 실제 instance를 확보하지 못함(존재 여부에 대한 결론이 아님).

## 1. Class별

| Class | 판정 | 확보된 실제 instance (연구용 목록 위치) | 비고 |
|---|---|---|---|
| Dam | **OK (+AMBIG)** | K-water 시설 11개(MyWater DAM_CD 있음), KHNP 한강 수력발전댐 7개(이름만) — `03_normalized/dam_catalog.csv` | ① 시설 유형(다목적댐/용수댐/수력발전댐/홍수조절용댐/보/조정지)이 source에 있으나 현재 Data Property에는 유형 속성이 없음 → AMBIG. ② `충주조정지`(MyWater)와 별표1의 `충주댐(조정지댐포함)` 및 K-water 서술의 `역조정지댐`이 동일 시설인지 명칭 기반이라 REVIEW_REQUIRED. ③ 기관 간 공통 ID 없음(KHNP는 ID 미확보) → 이름 기반 연결만 가능. ④ 좌표는 MyWater에서 제공되지 않아 미확보. |
| ObservationStation | **OK (+AMBIG)** | 94개 (지점코드 OBS_CD, 지점명, 우량 A/수위 C 구분) — `observation_station_list.csv` | ① 댐 자체의 수위·유입·방류 시계열은 관측소 코드 없이 댐 단위(DAM_CD)로 제공 → 댐 수위를 "관측소"로 볼지 애매. ② 좌표 미제공. ③ 댐–관측소 연관은 사이트 조회 구조(damCd 파라미터) 기준이며 수문학적 관계 검증은 아님. |
| MeasurementDataset | **OK** | 71개 임시 dataset (해상도·변수·기간·원본 파일 단위) — `measurement_dataset_list.csv` | datasetId는 연구용 임시ID. 관측소 단위 시계열은 확보되지 않음(`getRain`은 요청 창 끝 1건 스냅샷). |
| Criterion | **OK (+AMBIG/NO-EXPR)** | 15건: 별표3 홍수기 제한수위 9개 댐, 연계운영규정 제2·6·7·11·13·14조 — `criterion_list.csv` | ① 현재 Data Property에 Criterion의 "값/단위"(예: 제한수위 EL.m)를 담을 속성이 없음 → 값 표현은 NO-EXPR, 조문 텍스트 자체는 OK. ② 별표3 셀 값에 각주표시(예: `25.51)`)가 붙어 값과 주석 분리가 애매. ③ 개별 댐관리규정은 법제처에서 확인되지 않음(NOT-OBTAINED). |
| Document | **OK (+AMBIG)** | 41건(법령·행정규칙 XML, 원본 PDF/HWPX, 웹 스냅샷) — `document_list.csv` | ① 문서 내 위치(조·항·별표)와 시행일자/개정 버전을 담을 속성이 없음 → AMBIG. ② documentId는 연구용 임시ID. |
| Approval | **NOT-OBTAINED** | 실제 승인 record 0건 | 규범 근거는 확인됨: 연계운영규정 제6조② "홍수조절을 위한 수문조작이 필요한 경우에는 홍수통제소장의 사전 승인" (Criterion/Document로 기록). **실제 승인 instance는 한강홍수통제소/WAMIS 접근 불가 및 인증키 필요 API로 인해 확보하지 못함.** 별도 targeted gap-filling 대상. |
| Operation | **NOT-OBTAINED** | 실제 운영행위 record 0건 | 규범 근거: 제14조(비상방류 통보·지시 등). 실제 수문조작/방류 이력 instance는 확보하지 못함. K-water 수문 방류정보 API(15140222)는 인증키+심의승인 필요. |

## 2. Relation별

| Relation | 판정 | 근거 |
|---|---|---|
| Operation –targetDam→ Dam | NOT-OBTAINED | Operation instance 없음 |
| Operation –relatedApproval→ Approval | NOT-OBTAINED | 양쪽 instance 없음 |
| Operation –relatedCriterion→ Criterion | NOT-OBTAINED | Operation instance 없음 (Criterion 쪽은 확보). neutral 의미 유지(`basedOn`으로 변경하지 않음) |
| Operation –recordedIn→ Document | NOT-OBTAINED | Operation instance 없음 |
| Approval –documentedBy→ Document | NOT-OBTAINED | Approval instance 없음 |
| Criterion –definedIn→ Document | **OK** | 15개 Criterion 모두 원문 조문/별표 위치와 원본 파일이 있음 |
| Dam –monitoredBy→ ObservationStation | **OK (근거 약함)** | K-water MyWater가 댐별로 나열한 우량/수위관측소 (공식 관계 문서 아님, 사이트 목록 기준) |
| ObservationStation –hasDataset→ MeasurementDataset | **AMBIG** | 관측소 단위 시계열이 확보되지 않음. 확보한 시계열은 댐 단위(Dam→Dataset)이며 현재 Ontology에 Dam→Dataset 직접 관계가 없음 |

## 3. 현재 Ontology로 표현되지 않는 실제 정보 (HOLD; 채택 아님)

| Issue | 실제 관찰 | 현재 단계 판단 |
|---|---|---|
| ISS-01 상·하류 관계 | K-water 공식 서술로 확인된 댐 간 관계 있음(`dam_network_evidence.csv`: 충주댐→역조정지댐, 충주댐→강천/여주/이포보(거리), 소양강댐→의암·청평·팔당(하류지역)) | 현재 Relation으로 표현 불가. **`upstreamOf/downstreamOf`를 추가하지 않음.** 필요성(반복 사용)과 문헌 검증 후 결정. HOLD |
| ISS-02 변수 의미 차이 | `저수율`이 K-water 두 문서에서 다르게 정의, `유입량/자체유입량/총방류량`, KHNP `방류량` vs K-water `총방류량` (variable_dictionary.csv) | Data Property(`variableType`) 수준에서 원본 변수명·정의 보존 필요 여부 검토. 자동 통합 금지. HOLD |
| ISS-03 시설 유형/좌표/제원 | 시설 유형·제원(총저수용량, 제한수위 등)이 source에 존재 | 현재 Data Property 밖. Dam 속성 확장 필요성은 CQ와의 관련성 확인 후 판단. HOLD |
| ISS-04 Criterion의 값 | 별표3은 시설별 수치(EL.m) 기준 | Criterion Data Property 부재. CQ4(운영기준) 관련이므로 검토 우선순위 높음. HOLD |
| ISS-05 Document 위치·버전 | 조·항·별표 위치, 시행일자, 훈령 번호 | provenance 관련. 현재 top-level 개념 추가 안 함. HOLD |
| ISS-06 시계열 시각 규약 | 시간자료의 hour=24 표기, 시간대 미명시 | 측정자료 처리 규칙(STEP 2) 이슈. Ontology 변경 사항 아님 |

## 4. CQ 점검 (표현 가능성만)
- CQ1 (관측자료 연결): Dam–Station–Dataset 일부 가능(관측소 시계열 미확보로 부분).
- CQ2 (운영행위), CQ3 (승인): **현재 수집 환경에서는 실제 instance를 확보하지 못해 미검증.**
- CQ4 (운영기준): 별표3·조문으로 부분 가능(값 표현 한계 ISS-04).
- CQ5 (문서 확인): 가능 (definedIn).
- CQ6 (강우·유입·저수위·방류 측정자료): 댐 단위 자료로 가능(댐 강우량/유입량/저수위/총방류량), 관측소 단위는 미확보.

## 5. KG Necessity Check
Approval/Operation이 없어 `Operation→Approval→Document` 다중 관계 탐색을 시험할 수 없으므로 **이번 단계에서 KG 필요성 결론을 내리지 않는다**(보류). 현재 자료만 보면 Dam·Station·Dataset·Criterion·Document는 단순 표/관계형 테이블로도 저장·조회가 가능한 구조다.
