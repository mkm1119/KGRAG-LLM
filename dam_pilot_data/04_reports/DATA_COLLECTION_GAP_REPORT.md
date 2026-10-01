# DATA COLLECTION GAP REPORT (STEP 2 mapping 전 원천자료 보완)

작성: 2026-10-01. 범위: 자료 점검·공식 출처 보완·정의/출처(provenance) 정리까지. **KG는 구축하지 않았고, ontology·CQ·기존 정규화 파일은 수정하지 않았다.** 새로 받은 파일은 모두 `01_raw/` 아래에 원본 그대로 두고, 요청·해시·수신시각은 `02_metadata/gap_fetch_log.csv`(65건: 성공 59, 실패 6)에 기록했다. 수집 스크립트: `scripts/gap_fetch.py`, `gap_parse_criterion_history.py`, `gap_build_criterion_history.py`, `gap_build_tables.py`, `hwp_text_extract.py`.

참고(비교): 이번 지시서의 core ontology(Dam / HydrometeorologicalState / Operation / Approval / Criterion / EvidenceSource)는 저장소의 Initial Ontology v0.1(7 Class: Dam, Operation, Approval, Criterion, Document, ObservationStation, MeasurementDataset)과 이름·구조가 다르다. 이번 작업은 지시서의 구조를 기준으로 gap을 기술했고, 어느 쪽도 수정하지 않았다. 두 구조의 대응(예: Document↔EvidenceSource, ObservationStation+MeasurementDataset↔HydrometeorologicalState)은 사람 확인 사항이다(HUMAN_REVIEW_QUEUE H-10).

## 1. 기존 확보자료 요약 (조사 결과)
| 영역 | 기존 확보 | 한계 |
|---|---|---|
| Dam catalog | K-water MyWater 11개(코드·명·유형), 승인 파일 시설 16개, KHNP 7개(코드 없음) — `dam_catalog*.csv`, `approval_facility_code_crosswalk.csv` | 출처별 코드·표기 상이, 동일시설 미확정 |
| 측정 | MyWater getHydr H/D(11댐 2021~2026), getPeriod, getRain(94 관측소 창 말 스냅샷), 승인 연계 창(2019-08~2020-09, 24건) | 관측소 단위 시계열은 이번에야 조회키 확인(§2-6) |
| 관측소 | 94개, 각 OBS_CD는 정확히 1개 damCd 조회 아래에만 나열 | 댐 소속 의미 확정 아님 |
| 승인 | HRFCO CSV 3,929건(2010-07-16~2021-07-16), 필드 8개 | 필드 정의 불충분 |
| Criterion | 현행(2026-07-08) 연계운영규정 15건 | 과거 버전 없음 |
| 문서 | 45건 메타데이터 | — |
| 시간 | `time_conventions.csv`(관찰 위주) | 공식 정의 미확인 |

## 2. 데이터 공백별 조사 결과
(근거 파일은 각 항목에 병기)

### 2-1. Operation 실제 기록 — **해결하지 못함 (DATA_REQUIRED 유지)**
- 조사: data.go.kr 18개 검색어, 후보 카탈로그 약 15건 열람, 법제처 규정, K-water MyWater 현황 페이지, 접근 시도(`03_normalized/operation_source_search_log.csv`, 검색 결과 원본 `01_raw/DataGoKr/search/`).
- 한강수계(충주·소양강·횡성·광동 등)에 대해 **실제 수문조작·방류 수행 기록으로 확인된 자료는 없다.**
- 가장 가까운 후보: ① K-water 수문 방류정보 조회 서비스(15140222): 방류시작·종료 시간 필드, 15분 주기, 충주·소양강·횡성·광동 코드 포함 — **방류 통보 메시지이며 실제 수행 기록인지 공식 설명에 구분이 없고, 인증키·심의승인이 필요해 호출하지 못했다**(`01_raw/DataGoKr/catalog_pages/15140222.html`). ② 섬진강댐 수문 개폐 정보(15117149)는 수문 단위 값(수문1~15, 2021-06~2023-07)으로 Operation 구조에 가장 가깝지만 **한강수계가 아니다** — 구조 참고용으로만 원본 저장(`01_raw/DataGoKr/operation_candidates/`).
- 오인 방지: K-water의 "수문 운영 정보"(15099110)·"수문 현황정보"의 "수문"은 水文(수위·유입량·방류량 등 관측 변수)이며 수문 개폐가 아님(제공항목 목록). 총방류량 시계열은 측정 결과 변수이며 Operation 근거로 쓰지 않는다. MyWater 한강현황의 "방류상태" 열은 15개 시설 모두 "-"(2026-09-29, 2026-10-01 두 스냅샷)로 내용이 없다.
- 접근 불가: hrfco.go.kr, api.hrfco.go.kr, wamis.go.kr, me.go.kr, opendata.kwater.or.kr — 연결 실패(2회 시도일 모두). **"없다"가 아니라 "이 환경에서 확인하지 못했다".**
- 규정은 행위의 존재를 서술한다(제6조② 수문조작 시 홍수통제소장 사전 승인; 제14조① 방류량 조정 후 지체없이 통보; `01_raw/Law_history/admrul_2100000134749_*20180629.xml`). 기록물의 형식·공개 여부는 규정에 없다.

### 2-2. Approval 필드 공식 정의 — **부분 해결** (`02_metadata/approval_field_dictionary.csv`)
출처: 공공데이터포털 파일데이터 15085926 설명(제공기관 한강홍수통제소; 원문 `01_raw/FloodControl/pages/datagokr_15085926_fileData.{html,json}`).
| 필드 | 상태 | 요지 |
|---|---|---|
| 방류시작시간 | VERIFIED(형식) | "방류 시작시간(년월일시분)" — 시간대·계획/실제 구분은 없음 |
| 비고 | VERIFIED(범주) | 초기방류·수문전폐·방류시간 변경·증감 등 "특이사항" 기록 |
| 접수방류량 | PARTIAL | "접수 방류량(단위 : CMS)" — **승인량인지 요청량인지는 정의 없음.** 데이터셋은 "방류승인 요청을 받아 승인 진행을 완료한 … 승인 내역"이라고만 서술 → approvedReleaseAmount 매핑 근거 못 찾음 |
| 승인년월일시분 | PARTIAL | 공식 설명은 "승인일자"(날짜); 머리글만 시분 암시; 값은 날짜뿐(3,929/3,929) |
| 관측소코드/명 | PARTIAL | "댐 관측소 코드/명"뿐, 코드 체계 명세 없음 |
| 순차번호 | PARTIAL | 정의 없음(항목 나열) |
| 접수일자 | UNRESOLVED | 정의 없음 |
공식 설명 외의 근거(데이터 관찰, 예: 3519 비고의 "(당초) 3000 (변경) 7000"과 접수방류량 7000의 일치)는 정의로 쓰지 않았다. 페이지의 관리부서·연락처(예보통제과)가 정의 질의 창구이다.

### 2-3. 과거 Criterion / 규정 버전 — **대부분 해결** (`03_normalized/criterion_version_history.csv`)
- 법제처 DRF(`nw=2`)로 「댐과 보 등의 연계운영규정」(행정규칙ID 41392) 연혁 **9개판**을 확보: 2012-01-01(제정, 발령 2011-10-31), 2013-01-01, 2013-04-17, 2016-04-29, 2018-06-29, 2022-07-06, 2024-02-29, 2025-11-11, 2026-07-08(현행). 원본 XML `01_raw/Law_history/`.
- [별표3] 홍수기 제한수위: 6개판은 XML 본문 표에서, **3개판(2013-01-01, 2013-04-17, 2016-04-29)은 XML에 표가 비어 있어 첨부 HWP를 받아 텍스트를 추출**(`01_raw/Law_history/attachments/`, 추출 스크립트 `hwp_text_extract.py`). HWP판은 열 구조를 직접 확인할 수 없어 "시설명 → 홍수기 제한수위 → 최저 운영수위" 그룹 순서로 행을 복원했다(검증 상태 `EXTRACTED_FROM_OFFICIAL_HWP_ATTACHMENT`, 분석에 쓰기 전 원본 대조 권장 — H-11).
- **관찰(원본 값 비교):** 한강수계 시설(소양강 190.3, 충주 138.0, 횡성 178.2, 화천 175.0, 춘천 102.0/98.0, 의암 70.5/67.0, 청평 50.0/46.0, 괴산 134.0, 팔당 25.5(각주 1) 표기)은 **9개판 모두에서 값이 같다**. 값이 판마다 바뀐 시설은 임하·섬진강·보현산·부안·장흥(모두 한강수계 밖)이다. 따라서 판별 가능한 시점 적용성은 "한강수계 시설의 별표3 값은 2012-01-01 이후 변화 없음"이라는 **관찰**이며, 개별 승인이 그 기준에 근거했다는 뜻이 아니다(Approval–Criterion 관계는 만들지 않음).
- 정정(이전 산출물): 현행 Criterion CR-09 팔당댐 값 "25.51)"은 **25.5에 각주 표기 "1)"가 붙은 것**이다. 표 하단 주석 원문: "1) 표시의 댐의 경우 홍수기 제한수위가 별도로 설정되어 있지 않아 상시만수위를 대신 표기하였다."(`01_raw/Law_history/*20180629.xml` [별표3] 주). 이번 CSV는 원문 `25.51)`을 보존하고 파생 열(`criterion_value_derived`=25.5, `footnote_marker_in_raw`=1))을 별도로 둔다. 기존 `criterion_list.csv`는 수정하지 않았다.
- 승인(2010-07-16~2021-07-16, 3,929건)의 시행 판 기준 분포(집계만; record별 연결 아님): 2012-01-01 이전 **1,146건(규정 시리즈에 해당 판 없음)**, 2012-01-01판 344건, 2013-01-01판 2건, 2013-04-17판 694건, 2016-04-29판 803건, 2018-06-29판 940건. 2012 이전 승인에 적용된 기준은 이번에 확인하지 못했다(DATA_REQUIRED).
- 광동댐은 모든 판의 [별표3]에 없다(별표1에는 2018-06-29판부터 있음). `effective_to`는 "다음 판 시행일"이며 법적 폐지일이 아니다.

### 2-4. 공식 Dam identity / crosswalk — **해결하지 못함 (OFFICIAL_CROSSWALK_REQUIRED)** (`03_normalized/facility_identity_evidence.csv`, 36쌍)
- 후보 쌍만 생성했다. 상태: **POSSIBLE_SAME 24, UNRESOLVED 11, CONFLICT 1, VERIFIED_SAME 0.**
- 새로 확인한 공식 정황: K-water 공식 댐코드 목록(15140222 설명)은 "1003110 충주 / 1006110 횡성 / 1012110 소양강 / 1001210 광동 / 1302210 달방 / 1021701 군남" 식으로 접미 "댐" 없는 명칭을 쓰며, 승인 파일의 명칭·코드와 일치한다. 그러나 **두 목록이 같은 코드 체계라는 명시적 서술이나 공식 대응표는 없어** VERIFIED_SAME으로 올리지 않았다. 공식 HRFCO 댐 관측소 코드표(WAMIS/hrfco)는 접근할 수 없었다.
- 강천·여주·이포: 이름은 같고 코드가 다름(1007801-3 vs 1007601-3) → UNRESOLVED.
- KHNP 6개 시설: KHNP API 발전소 코드(3110 화천 등, 15157779 설명)와 승인 코드(1010310 등) 체계가 다르고, KHNP API의 대상은 "수력발전소"(plant)라 댐과 같은 단위인지 근거 없음.
- 규정 시설명↔Dam: 규정은 코드 없이 명칭만 사용. 별표1은 "충주댐(조정지댐포함)"으로 한 항목인데 승인 파일·K-water는 충주조정지를 별도 코드(1003611)로 둔다 → CONFLICT(단위 불일치). 광동댐은 별표3에 없어 appliesToDam 후보 자체가 없다.

### 2-5. 시간 필드 규약 — **부분 해결** (`02_metadata/time_conventions_verified.csv`, 14행)
- 원자료로 확인(VERIFIED_BY_RAW): MyWater 시간자료 라벨은 하루 HH=01..24이며, HH=00은 getHydr H 전체에서 **1건**(여주보 1007602, 2021010200)뿐 — 이전 메모의 "00시 행은 전일 24로 표기"와 일치하지만 예외 1건이 있다. 검증 호출(getRainTrend, 2020-08-02~03)도 01..24, 00 없음.
- 공식 기술문서(15099110 v1.5.1) 샘플: 시간 자료는 "10-01 01시"부터, 10분 자료는 "10-01 00시 10분"부터 시작(요청 stdt=eddt=2018-10-01) — 구간 종료 시각 라벨과 일관되나 **명시 정의문은 아니다** → interval_semantics는 PARTIAL로 유지.
- timezone: 공식 서술은 찾지 못했다. 다만 페이지 시각과 수신시각이 UTC+9로 정합(MyWater 한강현황 기준일시 23:00 vs 수신 14:03:26Z; KHNP 측정시간 20:44:50 vs 수신 11:46Z) — **KST로 추정 가능하다는 관찰**이며 정의가 아니다.
- 승인 파일: 방류시작시간은 YYYY-MM-DD HH:MM(HH 00~23, 24 없음), 비고 안에 "24:00" 표기 2건(자유 텍스트), 승인년월일시분은 날짜만, 접수일자 정의 없음. 어떤 시각도 변환하지 않았다.

### 2-6. HydrometeorologicalState 조회키 — **부분 해결** (`03_normalized/measurement_lookup_key_evidence.csv`, 90행)
- 유입량·방류량·저수위·저수량·저수율·(댐 단위)강우량: MyWater getHydr/getPeriod에서 **DAM_CODE(DAM_CD)** 로 조회(원자료 66행 검증; 11댐×6변수). stationCode가 아님.
- 강우량(관측소 단위)·하천 수위/유량: **(damCd, OBS_CD) 조합**. 이전 보고(STEP 0/2)의 "관측소 단위 시계열 없음(getRain은 창 말 스냅샷)"을 이번에 부분 수정: getRainTrend에 damCd+obsCd를 주면 시간별 시계열이 반환됨을 충주댐 소속 관측소 2개(우량 1001420, 수위 1002655, 2020-08-02~03, 각 48행)로 검증(`01_raw/KWater/lookup_probe/`). 나머지 관측소는 키 형식만 확인(사이트 JS), 미호출.
- 모든 변수가 stationCode 기반이라는 가정은 성립하지 않는다(유입량·방류량은 관측소 단위 자료 없음).
- 공식 API: K-water 수문 운영 정보(15099110) 키 = damcode; KHNP 수문자료(15157779) 키 = genName/ippt(발전소 코드). 둘 다 인증키 필요로 미호출(`OFFICIAL_DOC_ONLY`). HRFCO/WAMIS 조회키는 접근 불가로 **NOT_FOUND**.

## 3. 새로 수집한 자료 목록 (모두 `dam_pilot_data/` 하위)
| 경로 | 내용 | 출처 |
|---|---|---|
| `01_raw/Law_history/` | 연계운영규정 연혁 목록 및 9개판 XML, 별표3 HWP 첨부 3개, 연혁 탐색 응답 | 법제처 DRF/첨부 다운로드 |
| `01_raw/DataGoKr/search/` | data.go.kr 검색 결과 18건(검색 단서) | 공공데이터포털 |
| `01_raw/DataGoKr/catalog_pages/` | 후보 데이터셋 카탈로그 11건 추가(15139712, 15117149, 15083335, 15150943, 15157779, 15085911, 15152729, 15083336, 15083252, 3068550, 15086305) | 공공데이터포털 |
| `01_raw/DataGoKr/tech_docs/` | K-water OpenAPI 기술문서 5건(.docx)과 추출 텍스트 | 공공데이터포털 참고문서 |
| `01_raw/DataGoKr/operation_candidates/` | 섬진강댐 수문 개폐 정보 CSV(참고, 한강수계 밖) | 공공데이터포털 15117149 |
| `01_raw/KWater/lookup_probe/` | getRainTrend 검증 응답 2건 | MyWater ajaxProc |
| `01_raw/KWater/pages/mywater_floodstatus_hangang_2026-10-01.html` | 한강현황(방류상태 열) 재수집 | MyWater |
| `02_metadata/gap_fetch_log.csv` | 위 전부의 출처기관·시스템·제목·URL·수신시각·파라미터·sha256·HTTP 상태 | — |
이용허락: data.go.kr 해당 페이지들이 "이용허락범위 제한 없음"으로 표기(15085926, 15099110, 15117149, 15140222, 15157779). 법제처 자료는 별도 라이선스 표기를 확인하지 않음.

산출 표: `03_normalized/data_gap_inventory.csv`(28건), `02_metadata/approval_field_dictionary.csv`, `02_metadata/time_conventions_verified.csv`, `03_normalized/facility_identity_evidence.csv`, `03_normalized/criterion_version_history.csv`(연혁 9 + 시설별 행 219), `03_normalized/measurement_lookup_key_evidence.csv`, `03_normalized/operation_source_search_log.csv`.

## 4. 해결된 gap
- 규정 연혁 목록과 판별 원문(9개판) 확보(G12 일부), 한강 시설 별표3 값의 판별 비교.
- 승인 파일 설명 문장 기반 필드 정의 중 방류시작시간·비고(G07/G10).
- 유입량·방류량·저수위 등의 조회키 유형(DAM_CODE) 및 관측소 단위 조회키(G22–G24 일부).
- 이전 산출물의 "25.51)" 해석 오류 정정(§2-3).

## 5. 부분 해결된 gap
승인 필드 정의(접수방류량·승인년월일시분·관측소코드), 시간 규약, 조회키(강우량·수위), 규정 연혁(2012 이후만; HWP 3판 복원), 시설명·유형(G19), EvidenceSource 메타데이터(G28).

## 6. 해결하지 못한 gap
Operation 실제 기록(G01), 승인–운영 연결(G03), 공식 시설 대응표(G05/G15–G18), HRFCO 조회키(G25), 2012 이전 승인(1,146건)에 적용된 기준(G13), 별표3 외 시설별 기준(G14), 2019 이전 승인 주변 측정 창(G27).

## 7. 공식 정의를 찾지 못한 field
접수일자(정의 없음), 접수방류량의 승인량 여부, 승인년월일시분의 시각 성분, 방류시작시간의 timezone/계획·실제 구분, 관측소코드의 코드 체계, MyWater `DATA5`(getHydr, 사이트 미표시), 방류상태(MyWater 한강현황), 수문1~15 값의 의미(섬진강 참고 자료).

## 8. entity identity unresolved 목록
승인 파일 7개 동일코드 시설(충주·횡성·소양강·광동·충주조정지·달방·군남), 보 3곳(코드 상이), KHNP 6개 시설(코드 체계·plant/dam 단위), 규정 ↔ Dam(충주댐 조정지 포함 단위 불일치), 광동댐(별표3 없음). 상세 `facility_identity_evidence.csv`.

## 9. 시간 의미 unresolved 목록
MyWater 시간 라벨의 구간 시작/종료(공식 정의문 없음), 일자료 집계 규칙, 승인 파일 timezone·방류시작의 계획/실제, 접수일자, 승인 시각 성분, 규정 버전의 법적 효력 종료일.

## 10. STEP 2 mapping 전에 사람 검토가 필요한 항목
`04_reports/HUMAN_REVIEW_QUEUE.md` 참조(H-01~H-12).

## 부록. 이번 작업에서 하지 않은 것
KG 구축, ontology class/relation/property 추가·변경, Dam 병합, Approval↔Operation/Criterion 연결, 접수방류량의 의미 부여, 현행 규정을 과거 승인에 연결, 이름 유사성 기반 동일시설 확정, 기존 파일의 변경(신규 파일 추가 + `04_reports/STEP1_DECISION_LOG.md` §6에 갱신 제안만 append; 기존 상태 값은 변경하지 않음).
