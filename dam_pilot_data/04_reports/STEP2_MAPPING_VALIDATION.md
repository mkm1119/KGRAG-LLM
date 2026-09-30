# STEP 2 — Mapping Validation

결과: `03_normalized/kg_validation_results.csv` (스크립트 `scripts/step2_validate_kg.py`). 규칙: `mapping_rules_pilot.csv`.

## 1. 구조 검증 (V1–V12)
V1–V10 PASS (entity ID 유일 4,181; 관계 끝점 존재 4,072; 관계 domain/range가 candidate v1 4종 안; 모든 entity/property/relation에 provenance 32,721행; Approval 3,929건 각각 concernsDam 1개; 금지 관계 0; approvedReleaseAmount/approvalTime 미채움; Dam 27 = MyWater 11 + 승인파일 16, 병합 없음; Approval 수·비고 수(3,764)가 STEP 0 원본 계수와 일치).
V11–V12는 **발견 사항**이다.

## 2. 매핑 규칙 판정
SUPPORTED: MR-01~11(상세는 CSV). NOT_SUPPORTED: MR-03b(접수방류량↔approvedReleaseAmount 등), MR-12(hasDataset). REVIEW_REQUIRED: MR-13(documentedBy). NOT_CREATED: MR-14.

## 3. 원본 대비 손실/변형 점검
- 값 변환 없음(문자열 그대로). 빈 값은 속성 미생성. 시간 라벨 보정 없음(hour=24 그대로 — 측정 값은 KG에 없음).
- Approval의 `비고`는 해석 없이 문자열 보존.
- Criterion CR-09 값 `25.51)`은 원문 그대로(오타 여부 미확인).
- MeasurementDataset.periodStart/End는 요청 기간이며 실제 커버리지가 아님(rain-C 횡성 등 일부 INCOMPLETE 표기가 note 열에만 있고 KG에는 미반영 → 개선 후보).

## 4. 생성하지 못한 관계/엔티티와 이유
| 대상 | 이유 |
|---|---|
| Operation 및 targetDam/relatedApproval/relatedCriterion/recordedIn | 실제 record 없음(S1A-09) |
| Approval–Criterion | 2019~2020 승인 ↔ 2026 현행 기준의 시점 적용성 미검증; 관계 없음 |
| Approval-file Dam ↔ MyWater Dam 동일성 | 같은 코드·이름이지만 공식 대응 확인 없음(S0-D). 이로 인해 **KG 간선만으로는 Approval → MeasurementDataset 도달 불가(0/3,929)** |
| Criterion → Dam | v0.1·v1 모두 관계 없음; 시설명은 리터럴 속성(facilityNameInSource, 신규 속성 후보 RC-11) |
| hasDataset | 관측소 단위 자료 없음 |
| documentedBy | 승인 문서 연결은 파일 단위 provenance뿐 |
| upstream/downstream | HELD |
| KHNP 댐 7개 노드 | 공식 ID 없음, 연결 가능한 자료 없음 |
| 그룹 dataset 37개의 Dam 연결 | 다댐 응답; 원본 파싱으로 도출 가능하나 pilot에서 미구현 |

## 5. 판단
- 구조적 무결성은 확보. **그러나 이 KG로 연구 목적(승인·기준·측정을 한 사례로 연결)을 그래프 탐색만으로 수행할 수 없다.** 원인은 KG 구축 오류가 아니라 (i) 시설 식별 미해결(S0-D), (ii) Criterion–Dam 관계 부재(온톨로지), (iii) 시점 적용성(자료). 이는 Hard Stop 조건("Criterion applicability를 추론해야만 KG 구축 가능")을 **회피**한 결과이며, 회피 비용으로 KG의 연결성이 낮다. STEP 3에서 이 한계를 그대로 평가한다.
