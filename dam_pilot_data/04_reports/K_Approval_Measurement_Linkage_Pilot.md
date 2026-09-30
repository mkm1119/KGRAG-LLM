# K. Approval + Measurement + Criterion + Document 연결 파일럿 (STEP 0 마지막 보완)

목적은 규모 확대가 아니라 **동일한 실제 사례에서 `Dam + Approval + Measurement + Criterion + Document`가 연결되는지 확인**하는 것이다. Operation이나 인과관계는 추론하지 않았고, 원본 변수명·의미 불확실성은 그대로 유지했다. 이 보완 후 데이터 수집은 종료한다.

## 1. 선정 근거 (승인 파일 통계만 사용)
승인 CSV에서 MyWater로 조회 가능한 2019-08 이후, K-water 코드 시설의 승인 건수: 광동 19, 횡성 5, 충주 4, 소양강 3, 달방 3.
| 선택 | 이유 |
|---|---|
| 광동댐(1001210) | 승인 건수가 가장 많음 |
| 충주댐(1003110) + 충주조정지(1003611) | 충주댐→역조정지댐이 K-water 공식 서술로 확인된 쌍. 같은 기간 두 시설 hourly 확보 |
| 횡성댐(1006110), 소양강댐(1012110) | 같은 기간(2020-08~09)에 승인이 있고 추가 호출 비용이 작음 |
기간 A 2020-07-25~2020-09-10(5개 시설), 기간 B 2019-08-01~2019-10-15(광동댐). 달방·강천/여주/이포보는 제외(달방은 승인이 단일 시점, 보는 승인 파일과 MyWater 코드가 달라 동일시설 미확정).

## 2. 추가 수집 (총 55회 호출, 8.4MB)
- 스크립트 `scripts/fetch_approval_linked_measurement.py`; 원본 `01_raw/KWater/mywater_approval_linked/` (hydr `getHydr` H, period `getPeriod` H1 6변수); 요청 로그 `02_metadata/mywater_approval_linked_manifest.csv`. 실패 0건. 이후 추가 수집 없음.

## 3. 연결 결과 (`03_normalized/linkage_pilot_cases.csv`, `linkage_pilot_measurement_extract.csv`)
- 승인 record **24건**(기간 A 18, B 6) 모두에 대해 Dam(코드 일치, 동일시설 확정은 REVIEW_REQUIRED) → Approval 원문 필드 → 시간자료 발췌(방류시작시간 -6h~+12h, 라벨 기준 19행 내외) 연결 가능.
- **Criterion·Document 연결: 24건 중 12건**(충주 4→CR-02 138.0, 횡성 5→CR-03 178.2, 소양강 3→CR-01 190.3; 별표3 근거, Document는 연계운영규정 원본). **광동댐 12건은 기준 미연결** — 광동댐은 별표3에 없음(별표1에는 한강수계 용수댐으로 있음).
- `비고`가 있는 record 20건(원문 그대로 유지).
- 같은 시설·기간에 승인과 측정이 존재함을 확인했을 뿐이다. 예로 기간 A 충주댐 접수방류량 값 {2000, 3000, 7000}과 같은 기간 측정 총방류량(시간자료) 최대값 약 4,004 CMS는 **서로 다른 수치**이며, 이는 승인 파일의 `접수방류량`과 측정 `총방류량`이 다른 개념임을 보여주는 관찰일 뿐 차이의 원인은 해석하지 않았다.

> **[정정 주석 — STEP 1-A, 2026-09-30]** 이 보고서의 "Criterion·Document 연결"은 **같은 시설의 현행(2026-07-08 시행) 연계운영규정 [별표3] 값과의 시설명 기준 대조**를 뜻한다. 2019~2020년 승인에 그 기준이 **당시 적용되었는지는 검증되지 않았다**(STEP 1 지침 §11-A; `STEP1_DECISION_LOG.md` S1A-07, S1A-08). `linkage_pilot_cases.csv`의 `linked_criterion_*` 열도 같은 의미로 읽어야 한다. 기존 서술은 삭제하지 않았다.

## 4. 이 파일럿으로 확인되지 않는 것 (해석 금지)
- 승인이 실제 조작(Operation)을 발생시켰는지, 측정 방류량 변화의 원인이 무엇인지 — **주장하지 않음**. 승인 존재+측정 변화 관찰만으로 Operation을 만들지 않는다.
- `증가방류`, `수문전폐` 등 비고 문구는 승인 파일에 기록된 내용이며 실행 증거가 아니다.
- 방류시작시간과 시간자료 라벨의 정확한 정렬: 시간 라벨 규약(hour=24, 시간대)이 미확정이라 발췌는 라벨 기준(naive)이며 정렬은 STEP 1/2에서 확정해야 한다.
- 승인 파일 코드와 MyWater DAM_CD의 동일 시설 여부, `접수방류량`=승인방류량 여부.

## 5. STEP 1 Ontology Validation으로 넘길 검증 질문 (실제 자료 기반)
1. `승인년월일시분` ↔ `approvalTime`: 값에는 시각이 없다(날짜만).
2. `접수방류량` ↔ `approvedReleaseAmount`: 원본 명칭·정의 추가 확인 필요; 실제 방류량과 분리 유지.
3. `접수일자`: 승인일자와 다른 record 62건 — 별도 개념인지.
4. `방류시작시간`: 24건 전부에 존재, 전체 3,929건에서도 반복 — Approval의 Property 후보인지.
5. `비고`: 3,764건 내용 존재(증가·감소·수문전폐·초기방류 등). 의미 부여 없이 evidence text로 보존. Operation 정의 검토 시 domain evidence로만 사용.
6. Criterion 값(EL.m) 표현, Document 위치/버전, 시설 유형, 시설 식별(코드 불일치)은 `I_Ontology_Compatibility_Report.md`의 HOLD 이슈 참조.
