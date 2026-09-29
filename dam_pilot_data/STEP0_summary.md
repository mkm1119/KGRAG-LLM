# STEP 0 Summary — 한강수계 댐 운영 자료 조사·수집

- 기준 문서: `01_AI_RESEARCH_HANDOFF.md` (canonical). KG 구축·Ontology 수정·새 방법 도입 **없음**.
- 수집 기간(세션): 2026-09-29 UTC. **사용자 지시로 bulk 수집을 2026-09-29T12:32:40Z에 종료**했고(`02_metadata/collection_stopped_utc.txt`), 이미 받은 파일은 모두 보존했다.
- 이 문서는 사실·한계 기록이며, 아직 KG 필요성이나 방법론에 대한 결론을 담지 않는다.

## 1. 이번 세션 네트워크에서의 source 접근 결과 (재테스트)

| Source | 결과 |
|---|---|
| MyWater(K-water 물정보포털) | 접근 가능. 사이트 자체 ajax endpoint에서 **인증 없이** 시계열 수집 |
| K-water 사이트, KHNP 사이트 | 접근 가능(HTML) |
| 공공데이터포털(www/apis.data.go.kr) | 접근 가능. API는 서비스키 필요 (키 없이 호출 시 401 `SERVICE_KEY_IS_NULL` 확인·저장) |
| 법제처 www.law.go.kr (DRF, `OC=test` 샘플값) | 접근 가능(간헐적 리셋 → 재시도). `law.go.kr`(www 없음)/`open.law.go.kr` 차단 |
| 기상자료개방포털 data.kma.go.kr | 페이지 접근 가능, **상세 다운로드는 로그인 필요**(자동 우회 안 함). `apihub.kma.go.kr`/`www.kma.go.kr` egress 403 |
| **WAMIS, 한강홍수통제소(hrfco/api.hrfco)** | **사이트 접근 불가**(단, 방류승인은 data.go.kr 파일데이터로 확보 §5)(https 연결 리셋, http 503, no-www 호스트 egress 403; 다회 재시도 동일). 원인(egress 정책 vs 해외 IP 차단)은 판별하지 못함 |
| 환경부 me.go.kr, opendata.kwater.or.kr | egress 403 |

증적: `04_reports/access_probe.tsv`, `access_probe_retry.tsv`, `proxy_relay_failures_snapshot.json`.

## 2. 수집된 실제 자료

### 2.1 Measurement (K-water MyWater, 원본 JSON 그대로)
- `getPeriod` (기간별자료; 변수 6종: 저수위·저수량·강우량·유입량·자체유입량·총방류량): 일자료 2021-01-01~2026-09-28 (3개 그룹 전체), **시간자료** group1(다목적댐 4: 소양강·충주·충주조정지·횡성) 2021-01-01~2026-09-28 전 변수 완료, group2(용수댐; 광동댐·달방댐 등) 5개 변수 완료·총방류량은 ~2024-09-11까지, group3(보) 3개 윈도만(중단), **10분 자료** group1 홍수기 구간(6/21~9/30) 2021~2025.
- `getHydr` (댐별 수위·저수량·저수율·강우량·유입량·총방류량): 11개 시설 일·시간 2021-01-01~2026-09-28. (10분 `getHydr`은 수집하지 않음)
- `getBasic` 제원: 11개 시설.
- `getRain` (우량A/수위C 관측소): 94개 지점 목록 확보. **주의: 응답이 기간 시계열이 아니라 요청 창 끝 시점 1건이라 관측소 시계열로는 사용할 수 없음.** 지점 시계열은 `getRainTrend`가 필요하나 수집하지 않음.
- 승인 CSV 1개(3,929행) 별도. 규모: 원본 JSON 3,024개(약 476MB, 압축 아카이브 53MB `01_raw_archive/`), 정규화 long/wide 테이블(gz) 6개.
- 완전성(`04_reports/quality_window_completeness.csv`): 1,376개 period 윈도 중 1,375개가 기대 행수와 일치, **1개 불일치**(H1/group3/DATA1/2021-01-01_2021-01-30: 721행 vs 기대 720; 보정하지 않고 원본 유지).
- 결측 규칙: null/'' 없이 **해당 COLn 키가 응답에서 사라짐**(정규화에서 `key_present_in_raw=N`). 한강 K-water 시설 시간자료에서는 시설당 1건.
- 값 일치성: 같은 댐·시각의 `getPeriod`(2자리)와 `getHydr`(3~4자리) 일자료 25,164쌍이 표시 정밀도 내(최대차 0.005)에서 일치.

### 2.2 Dam / ObservationStation / MeasurementDataset 목록
- `03_normalized/dam_catalog.csv` (18행: K-water 11 + KHNP 수력발전댐 7[이름만, ID 미확보]), `dam_catalog_kwater_basic.csv`(제원), `dam_basic_raw_all_damGb.csv`
- `observation_station_list.csv` (94), `measurement_dataset_list.csv` (71)
- 좌표(lat/lon)는 source가 제공하지 않아 **미확보**.

### 2.3 Criterion / Document
- `criterion_list.csv` 15건: 연계운영규정 [별표3] 홍수기 제한수위 9개 댐(소양강·충주·횡성·화천·춘천·의암·청평·괴산·팔당) + 제2·6·7·11·13·14조.
- `document_list.csv` 41건: 법제처 법령·행정규칙 XML 11건(하천법·시행령, 댐건설관리법·시행령, 저수지댐안전관리법, 홍수조절지 및 저류지 관리규정, 한강권역 하천유역수자원관리계획 고시[고시문 2.7KB만], 지구단위 홍수방어기준, 댐시설 최소유지관리기준, 수문조사업무규정, 수문자료 공인·배포기준, 연계운영규정 본문), **연계운영규정 원본 PDF/HWPX 및 별표1 서식 원본 4건**, 웹 스냅샷.
- 교차검증: 소양강 190.3, 충주 138(=138.0), 횡성 178.2는 MyWater 제원(홍수기제한수위)과 별표3이 일치 (`crosscheck_flood_limit_level_kwater_vs_law_annex3.csv`).
- 미확보: 개별 댐관리규정(법제처 미게재 확인), 비상대처계획, 운영기관 공식 설명자료 일부, 한강권역 하천유역수자원관리계획 본문.

## 3. 공식 근거가 확인된 상·하류 관계 (`03_normalized/dam_network_evidence.csv`)
원문 문장을 그대로 인용하고 상태를 구분했다. 좌표·나열 순서로 추정한 관계는 없다.
- **OFFICIAL_TEXT_STATED (K-water 한강유역본부 시설 소개, 단일 기관 출처)**: 충주댐→역조정지댐("본댐 하류 19.6km 지점"), 충주댐→강천보/여주보/이포보(충주댐 하류 약 56/66/78km), 소양강댐→의암·청평·팔당댐("하류지역인"; 세 댐 상호 순서는 미명시), 소양강→북한강 합류, 섬강→남한강 합류(하천 수준).
- **REVIEW_REQUIRED(유도값)**: 보–보 순서(수치 비교로 유도, 원문이 직접 서술하지 않음).
- 연계운영규정 별표1은 **한강수계 소속(membership)만** 명시(`han_system_membership_byeolpyo1.csv`); 표의 나열 순서는 상·하류 순서로 해석하지 않음.
- 미확보: WAMIS/홍수통제소 등 제2 출처에 의한 교차검증(접근 불가). 위 관계는 모두 **단일 출처**임.
- **Measurement 후보 쌍(공식 서술 + 시계열 모두 있음)**: 충주댐(1003110)–충주조정지(1003611): group1 시간자료 6변수 2021-01-01~2026-09-28 완료(양쪽 동일 50,328시각 모두 키 존재) / 충주댐–강천보(1007601)·여주보(1007602)·이포보(1007603): `getHydr` 시간자료 완료. **소양강댐→의암·청평·팔당은 공식 서술은 있으나 하류측 과거 시계열이 없음**(KHNP는 현재/전일 값만, MyWater 목록에 없음).

## 4. 변수 사전과 시각 규약
`02_metadata/variable_dictionary.csv`(23행), `time_conventions.csv`. 원문 정의를 인용하고 해석하지 않았다. 확인된 의미 충돌:
- `저수율`: MyWater(유효저수율 정의)와 data.go.kr(총저수용량 기준 정의)가 다름. 수치는 다수 댐에서 저수량/총저수용량과 일치(중앙 절대차 0.003%p)하나 충주조정지는 크게 다름(중앙차 43%p) — 원인 미확인.
- `유입량`·`총방류량`의 K-water 내부 서술 차이, 충주조정지에서 유입량≠자체유입량(관찰만), KHNP `방류량` vs K-water `총방류량`(동일시 금지).
- 시간자료 hour=24 표기(시각 규약 REVIEW_REQUIRED), 시간대 미명시, 실시간·잠정 vs 최종 구분 미명시(KHNP는 잠정 고지).

## 5. Approval / Operation
**Approval — 실제 record 확보 (초기 결론 "미확보"를 대체).** 공공데이터포털 파일데이터 15085926(한강홍수통제소 댐방류승인 CSV, 로그인 없이 다운로드)에서 **3,929건, 승인 2010-07-16~2021-07-16, 16개 시설**(팔당·괴산·청평·의암·춘천·화천댐, 강천·여주·이포보, 광동·횡성·충주조정지·충주·소양강·달방·군남)을 원본 그대로 보존했다(`01_raw/FloodControl/`). 원본 컬럼: `순차번호, 관측소코드, 관측소명, 승인년월일시분, 방류시작시간, 접수방류량, 접수일자, 비고`. 방류종료시간 컬럼은 없고 `비고`(3,764건 내용)는 원문 그대로 보존했으며 Rationale/Operation으로 해석하지 않았다. 상세는 `04_reports/J_Approval_Gap_Filling_Report.md`.
- 한계: 파일은 "수시(1회성)" 스냅샷이라 **2021-07-16 이후 이력 없음**; 홍수통제소 웹 테이블(`hrfco.go.kr/sumun/dam/damFct.do`)의 다운로드/AJAX endpoint는 접속 불가로 확인하지 못함; `접수방류량`이 승인방류량과 같은지 미확인; 확보한 Measurement(2021-01-01~)와의 시간 겹침은 승인 57건뿐.
**Operation — 현재 수집 환경에서는 실제 instance를 확보하지 못함.** 규범 근거(연계운영규정 제6조②, 제14조)만 확인. 승인 파일은 Operation이 아님. (K-water 수문 방류정보 API 15140222는 인증키+심의승인 필요.)

## 6. 재현·보존
- 코드 `scripts/`(수집: `fetch_kwater_mywater.py`, `fetch_kwater_station.py`, `mywater_client.py`, `fetch_law.py`, `probe_*`; 정규화/분석: `build_*.py`, `analyze_*.py`). 함수 분리는 `fetch_kwater()`/`fetch_law()` 등 source별 파일 단위.
- endpoint/parameter/batch: MyWater `POST https://www.water.or.kr/kor/realtime/sumun/ajaxProc.do` (헤더 `AJAX: true`, form-encoded; mode=getPeriod|getHydr|getBasic|getRain). 배치 윈도: 일 364일, 시간 30일, 10분 7일(사이트 조회한도 365/30/7). 요청 간 1초 이상, 동시 최대 4스트림, 실패 시 최대 4회 재시도.
- 요청 로그: `02_metadata/mywater_fetch_manifest.csv`(1,376), `mywater_station_fetch_manifest.csv`(1,745행/1,648파일), `law_fetch_manifest.csv`, 접근 프로브 TSV, 실행 로그 `04_reports/*.log`. 최종 파일 해시: `02_metadata/FINAL_MANIFEST.csv`. 원본 복원: `01_raw_archive/README.md`.

## 7. 한계·정직한 주의 (재사용 전 확인)
1. MyWater endpoint는 **공식 문서화된 OpenAPI가 아님**(사이트 페이지 JS에서 확인). 이용약관상 자동수집 허용 여부는 미확인. 공식 API(15099110, 키 필요)로의 교차검증은 미수행.
2. 관측소 `getRain` 자료는 시계열이 아님(§2.1). `getHydr` 10분 자료 미수집. `extra()`(달방댐·단양수중보 추가 수집)는 스크립트에 있으나 **실행하지 않음**(사용자 지시로 범위 축소); 달방댐·단양수중보는 group2/3 `getPeriod`에만 있음.
3. station manifest에 중복 요청 97건(동시 프로세스 겹침). 디스크 파일은 마지막 응답이며 FINAL_MANIFEST의 sha256은 디스크 기준. 응답에는 `nowTime`, 클라이언트 `ip` 필드가 echo되어 있음(원본 보존).
4. 스크립트 내부 자동 재시도(연결 리셋 등)는 개별 로그로 남기지 않았음. 최종 실패(FAIL)로 기록된 요청은 0건.
5. 10분 자료 요청 구간은 6/21~9/30이며 규정상 홍수기 정의(6/21~9/20)보다 넓음.
6. 법제처 DRF는 문서상 샘플 `OC=test` 사용. 정식·대량 사용은 본인 OC 등록 필요.
7. 사이트가 `한강`으로 표기한 하천 그룹 라벨은 검증된 수계가 아님(달방댐·단양수중보는 별표1 한강수계 목록에 없음).
8. (Approval) 위 §5 한계 참조.
9. KHNP 자료는 현재/전일 스냅샷뿐이며 과거 시계열 없음. 기상청 강수(ASOS/AWS) 미수집 → Dam–Weather Station 대응표 미작성(선정 근거를 기록할 수 없어 임의 작성하지 않음).

## 8. 남은 gap-filling 시 필요한 사용자 조치 (Operation, 2021-07 이후 승인)
- 세션 egress에 `www.wamis.go.kr`, `www.hrfco.go.kr`, `api.hrfco.go.kr`, `apihub.kma.go.kr`, `open.law.go.kr`, `opendata.kwater.or.kr` 등 허용 (`04_reports/G_API_Requirement_Report.md` 참조).
- 공공데이터포털 serviceKey(환경변수 `SERVICE_KEY`), 필요 시 법제처 OC, 기상청 authKey.

## 산출물 색인 (요청 1~10)
1. raw: `01_raw/`, `01_raw_archive/`  2. 코드: `scripts/`  3. endpoint/parameter/batch: 본 문서 §6, `mywater_*_manifest.csv`, `G_API_Requirement_Report.md`  4. request/error log: `02_metadata/*manifest*.csv`, `04_reports/access_probe*.tsv`, `*.log`, `proxy_relay_failures_snapshot.json`, `quality_*.csv`  5. `02_metadata/source_catalog.csv`(S16 승인 추가)  6. `02_metadata/variable_dictionary.csv`, `time_conventions.csv`  7. `03_normalized/dam_catalog.csv`, `observation_station_list.csv`, `measurement_dataset_list.csv`  8. `03_normalized/criterion_list.csv`, `document_list.csv`, **승인: `approval_records_hrfco_raw_fields.csv`, `approval_facility_code_crosswalk.csv`, `J_Approval_Gap_Filling_Report.md`**  9. `03_normalized/dam_network_evidence.csv`, `han_system_membership_byeolpyo1.csv`  10. `04_reports/I_Ontology_Compatibility_Report.md`
