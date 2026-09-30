# STEP 2 — KG Construction Report (pilot)

## 1. 절차
literature check(`STEP2_METHOD_EVIDENCE.md`) → mapping rules(`mapping_rules_pilot.csv`) → 구축(`scripts/step2_build_kg.py`) → 검증(`scripts/step2_validate_kg.py`, `STEP2_MAPPING_VALIDATION.md`). 구현: CSV(저장·질의 기술 미결정). Ontology는 `working_ontology_candidate_v1.csv`(v0.1 + 후보)를 사용, v0.1은 불변.

## 2. 산출물 규모
| 클래스 | 수 | | 관계 | 수 |
|---|---|---|---|---|
| Approval | 3,929 | | Approval–concernsDam→Dam | 3,929 |
| ObservationStation | 94 | | Dam–monitoredBy→Station | 94 |
| MeasurementDataset | 71 | | Dataset–concernsDam→Dam | 34 |
| Document | 45 | | Criterion–definedIn→Document | 15 |
| Dam | 27 (MyWater 11, 승인파일 16) | | | |
| Criterion | 15 | | | |
속성 24,468행, provenance 32,721행(entity·property·relation마다 원본 파일·위치·sha256·매핑 규칙).

## 3. 만들 수 있었던 것 vs 없었던 것
§ `STEP2_MAPPING_VALIDATION.md` 4. 요약: 원천이 명시한 연결만 생성했고, 추론 관계는 0. Operation·Approval–Criterion·시설 동일성·hasDataset·documentedBy·상하류는 생성하지 않음.

## 4. 그래프의 성격
- 대부분 star 구조(Dam ← Approval 3,929개). 다단계 경로는 Dam→Station(94), Criterion→Document 정도. Approval, Criterion, Measurement는 **서로 다른 연결 성분**에 놓인다(V11/V12). 즉 KG가 표현하는 것은 대체로 "시설별 목록"이며 관계 추론을 필요로 하는 다중 홉 구조가 아직 없다.
- STEP 3에서 KG 필요성을 정직하게 평가해야 한다(KG 우위를 전제하지 않음).

## 5. 이슈(결정 로그로 이관)
S2-01 시설 동일성(S0-D)이 통합 질의의 병목; S2-02 Criterion–Dam 관계 후보(RC-11) 필요 여부; S2-03 dataset 기간을 실제 커버리지로 채울지; S2-04 그룹 dataset의 Dam 연결; S2-05 KG에 측정값을 넣지 않은 결정은 handoff §6.3 미결정 사항의 잠정 처리.
