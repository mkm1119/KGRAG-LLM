# STEP 2 데이터 대응표 (최종본7 온톨로지 기준)

- 작성일: 2026-10-07
- 기준: 랩미팅 최종본7의 Class 6개, Relation 8개, Data Property (수정본 최종본8은 용어표만 다름)
- 이전 파일럿 KG(`kg_*_pilot.csv`)는 7-Class 후보(`working_ontology_candidate_v1.csv`) 기준이므로, 아래 대응표로 새 기준에 맞게 다시 구성한다.
- 수치는 저장소의 `03_normalized`, `02_metadata` 파일을 직접 집계한 값이다.

## 1. Class·Data Property별 데이터

| Class | Data Property | 가진 데이터 | 규모 | 부족한 점 |
|---|---|---|---|---|
| Dam | damName, damType | `dam_catalog.csv`, `dam_basic_raw_all_damGb.csv` (K-water 11개 시설), 승인 파일의 16개 시설 | 시설 27 | 기관별 시설 코드가 달라 동일시설 대응이 필요. 같은 코드·비슷한 이름 7건은 `REVIEW_REQUIRED`, 이름만 비슷하고 코드가 다른 보 3건 |
| HydrometeorologicalState | variableType, stationCode | 변수 7종 (저수위, 저수량, 강우량, 유입량, 자체유입량, 총방류량, 저수율). 댐별 우량관측소 코드 (`kwater_station_api_by_dam.csv` 118행) | 아래 §2 | 댐 단위 변수는 `DAM_CD`, 강우는 관측소 코드를 쓰므로 `stationCode`의 의미가 둘로 갈림 |
| Operation | operationType, operationTime | **실제 기록 없음** (`data_gap_inventory` G01) | 0 | §3의 도출 방식 결정 필요 |
| Approval | approvalTime, approvalContent | 한강홍수통제소 댐방류승인 CSV | 3,929건, 2010-07-16~2021-07-16, 시설 16 | 승인일은 날짜만 있음. 방류시작시간은 별도 컬럼 |
| Criterion | criterionType, criterionValue, unit | `criterion_list.csv`: 별표3 홍수기 제한수위 9개 댐(CR-01~09), 조문 6건(CR-10~15). 개정 이력 228행 | 15 | 제한수위 값이 있는 것은 9건뿐. 조문 6건은 값이 아닌 문장 |
| EvidenceSource | sourceTitle, sourceType, sourceLocator | 문서 45건(`document_list.csv`), 측정 데이터셋 71건(`measurement_dataset_list.csv`), 승인 CSV(sha256 기록) | 약 117 | 위치(별표 번호, 순차번호 등)는 Criterion·Approval은 있고 Operation은 없음 |

## 2. 측정 자료(Measurement Store) 범위

| 해상도 | 기간 | 시설 |
|---|---|---|
| 일 | 2021-01-01~2026-09-28 | 10개 (광동, 달방, 소양강, 충주, 충주조정지, 횡성, 강천보, 여주보, 이포보, 단양수중보) |
| 시간 | 2021-01~2026-09 (강천보, 여주보, 이포보, 단양수중보는 2021-03까지) | 위와 동일 |
| 10분 | 2021-06~2025-09 | 소양강, 충주, 충주조정지, 횡성 |
| 승인 연계 구간 | 승인별 방류시작 -6시간 ~ +12시간 (2019~2020) | `linkage_pilot_cases.csv`의 24건 |

K-water MyWater 시각 표기는 `HH=01~24` 형식이고 시각 의미(구간 시작·종료)는 미확정이다 (`time_conventions_verified.csv`).

## 3. 시간 겹침 문제 (이번 대응표에서 확인된 핵심)

- 승인 자료는 2010~2021-07, MyWater 일·시간·10분 자료는 2021-01 이후이다.
- 승인 자료 중 2021년 이후 건은 57건이고, 충주·소양강·횡성은 0건이다 (팔당 30, 보 3개 각 6, 괴산 6, 광동 3).
- 따라서 승인과 측정자료를 함께 조회할 수 있는 것은 **승인 연계 구간으로 별도 수집한 24건**(광동, 충주, 횡성, 소양강, 2019~2020)이다.
- 제한수위 기준이 있고 측정자료도 있는 댐은 **충주, 소양강, 횡성** 3곳이다. 광동은 용수댐이라 별표3 기준이 없다.
- 팔당, 괴산, 청평, 의암, 춘천, 화천은 기준과 승인은 있으나 K-water 측정 자료가 없다 (KHNP 현재·전일 값 스냅샷만).

## 4. 관계(Relation)별 연결 가능성

| Relation | 연결 근거 | 상태 |
|---|---|---|
| Dam –hasHydrometeorologicalState→ HydrometeorologicalState | 댐 코드, 댐별 관측소 코드 | 가능 (조회 파라미터 기준 연관) |
| Operation –performedOnDam→ Dam | Operation 도출 후 | Operation 결정 후 |
| Approval –authorizes→ Operation | 승인 파일에 운영행위 식별자 없음 (G03 `NOT_FOUND`) | **연구용으로 구성** (실제 연결 근거 없음) |
| Criterion –appliesToDam→ Dam | 별표3 시설명 기준 | 가능 (이름 기준 대응) |
| ○ –supportedBy→ EvidenceSource | 파일·문서·위치 | 가능 |

## 5. 승인 자료의 시간 특성

- 방류시작시간이 있는 3,929건 중 승인일과 같은 날 3,670건, 승인일보다 **이전** 76건, 이후 183건.
- 승인일 이전 방류시작은 보정하지 않고 원문 그대로 둔다.
- 승인일자는 컬럼 이름은 "년월일시분"이지만 값은 날짜만 있다 (`time_conventions_verified.csv`).

## 6. 테스트 전에 정할 것

1. **테스트 대상 댐:** 충주, 소양강, 횡성을 중심으로, 광동을 승인 건수가 많은 보조 사례로.
2. **Operation 도출 방식:**
   - (가) 승인 연계 구간의 실제 측정 총방류량 변화에서 Operation을 도출하고, 같은 시각의 승인과 연결한다. 연결은 연구용으로 구성한 것임을 표시한다.
   - (나) 승인의 방류시작시간·방류량을 그대로 Operation으로 복제한다. 가장 단순하지만 Operation이 Approval과 구분되지 않는다.
3. **Criterion 범위:** 값이 있는 제한수위 9건만 쓸지, 조문 6건도 EvidenceSource 위치로만 사용할지.
