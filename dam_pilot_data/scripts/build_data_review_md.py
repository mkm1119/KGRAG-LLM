#!/usr/bin/env python3
import json, csv
F=json.load(open("04_reports/data_review/_fragments.json",encoding="utf-8"))
def rd(p): return list(csv.DictReader(open(p,encoding="utf-8-sig",newline="")))
def cell(v): return str(v).replace("|","\\|").replace("\n"," ")
def md(rows,cols): return "\n".join(["| "+" | ".join(cols)+" |","|"+"---|"*len(cols)]+["| "+" | ".join(cell(r.get(c,"")) for c in cols)+" |" for r in rows])
crit=rd("03_normalized/criterion_list.csv"); cr02=[c for c in crit if c["criterion_id(연구용 임시ID)"]=="CR-02"][0]
art6=[c for c in crit if c["locator_in_document"]=="제6조"][0]
net=[r for r in rd("03_normalized/dam_network_evidence.csv")]
netcols=["upstream_dam","downstream_dam","relation_type","verification_status"]
docs=[d for d in rd("03_normalized/document_list.csv") if "연계운영규정" in d["title_or_filename"] or "연계운영규정" in d["note"]]
dam=[r for r in rd("03_normalized/dam_catalog_kwater_basic.csv") if r["dam_id_source"]=="1003110"][0]
keys=[k for k in dam if "[DATA" in k]
basic=[{"field(원본 표기)":k,"value":dam[k]} for k in keys]
md_out=f"""# L. 데이터 검토용 요약 (Data Review)

> **목적:** 지금까지 수집·정규화한 실제 자료가 어떤 모습인지 보여주는 것. Ontology 수정, KG 구축, 새 Relation 생성, 변수 의미 통합은 하지 않았다. 표의 값은 원자료/정규화 파일에서 그대로 가져왔고, 해석 문장은 넣지 않았다. 원본 컬럼명은 임의로 바꾸지 않았다(괄호 안 단위·라벨은 출처 페이지 표기).
> 이 문서는 `scripts/build_data_review.py`, `build_data_review_md.py`가 데이터에서 자동 생성했다. 표본 CSV와 그래프는 `04_reports/data_review/`에 있다.

## 1. 현재 확보한 데이터 전체 구성

{F['inventory']}

> "관련 Ontology 개념"은 현재 Ontology(Class 7개) 중 어느 것과 관련되는지만 표시한 것이며 매핑을 확정한 것이 아니다. `Operation`은 실제 instance를 확보하지 못했다(현재 수집 환경 기준).
> 측정자료 원본 JSON은 `01_raw/KWater/…`(압축본 `01_raw_archive/`), 승인 원본은 `01_raw/FloodControl/`, 법령 원본은 `01_raw/Law/`, `01_raw/Regulations/`.

## 2. 실제 데이터 샘플

### 2-1. Dam (`03_normalized/dam_catalog.csv` 앞 8행, 제원은 `dam_catalog_kwater_basic.csv`에서 결합)
{F['dam']}
→ 전체 샘플: `04_reports/data_review/sample_dam.csv`. `river_label(source)`는 출처가 붙인 하천 그룹 표기이며 검증된 수계가 아니다. KHNP 댐은 제원을 수집하지 못했다.

### 2-2. ObservationStation (`observation_station_list.csv`, 충주댐 5개 + 소양강댐 4개 지점)
{F['station']}
→ `sample_station.csv`. 좌표는 출처가 제공하지 않아 없음.

### 2-3. Measurement — 충주댐·충주조정지 hourly 일부 (MyWater `getHydr` 원본 field, 2020-08-02 14~22시 라벨)
{F['meas']}
→ `sample_measurement_hourly_충주댐_충주조정지.csv`. `DATA1`=수위, `DATA3`=강우량, `DATA4`=유입량, `DATA6`=총방류량은 출처 페이지 렌더링 코드 근거이며, `DATA2`(저수량)·`DATA5`(의미 미표시)·`DATA7`(저수율)는 생략했다. 시각 라벨 규약(hour=24 표기 등)은 미확정.

### 2-4. Approval — 실제 승인 record 10건 (`approval_records_hrfco_raw_fields.csv`에서 발췌, 충주 4·횡성 3·소양강 3)
{F['approval']}
→ `sample_approval_10.csv`. `case_id`는 연구용 임시 ID(AP-순차번호). 전체 3,929건은 `03_normalized/approval_records_hrfco_raw_fields.csv`. `비고`는 원문 그대로이며 의미를 부여하지 않았다.

### 2-5. Criterion — 홍수기 제한수위 5건 (연계운영규정 [별표3])
{F['criterion']}
→ `sample_criterion_5.csv`(출처 URL 포함). 셀 원문에 각주표시가 붙은 경우는 별표에 그대로 있음(예: 팔당댐 `25.51)`).

### 2-6. Document — 위 Criterion이 들어 있는 문서와 위치
- 위치: **「댐과 보 등의 연계운영규정」(기후에너지환경부 훈령 제42호, 시행 2026-07-08) [별표3] 댐의 홍수기 제한수위(제6조 관련)**.
- 원문 XML: `01_raw/Law/admrul_2100000282102_댐과보등의연계운영규정_현행20260708.xml` (법제처 DRF `lawService.do?OC=test&target=admrul&ID=2100000282102&type=XML`)
- 원본 첨부: PDF/HWPX (`01_raw/Regulations/`), 별표1 서식 원본 2개.
{md([{**d,'sha256':d['sha256'][:12]+'…'} for d in docs],["document_id(연구용 임시ID)","title_or_filename","type","raw_file","sha256"])}

### 2-7. 상·하류 관계 evidence (원문 인용은 `dam_network_evidence.csv`의 `verbatim_quote`)
{md(net,netcols)}
→ 전체: `03_normalized/dam_network_evidence.csv`, 수계 소속: `han_system_membership_byeolpyo1.csv`. 모두 K-water 한 곳의 서술이며 2차 출처로 검증하지 못했다. `REVIEW_REQUIRED`는 유도값으로 공식 서술이 아니다.

## 3. 서로 연결 가능한 실제 사례 한 건 — 충주댐, 2020-08 (승인 4건)

> 아래는 **현재 자료상 실제로 연결 가능한 정보를 병렬로 나열**한 것이다. KG 관계를 새로 만들지 않았고, 승인·측정·기준 사이의 인과나 Operation을 해석하지 않았다.

### (1) 대상 Dam
- MyWater `DAM_CD` **1003110 충주댐** / 승인 파일 `관측소코드` 1003110, `관측소명` '충주' — 코드는 같지만 동일시설 확정은 REVIEW_REQUIRED.
- 제원(MyWater getBasic 원본 field, 출처 페이지 표기):
{md(basic,["field(원본 표기)","value"])}

### (2) Approval 원문 (승인 파일, 충주 4건 전부, 기간 2020-08~09)
{chr(10).join(F['approval'].split(chr(10))[:2])}
{chr(10).join(l for l in F['approval'].split(chr(10)) if '| 충주 |' in l)}

### (3) 승인 전후 hourly Measurement — AP-3412 (방류시작시간 2020-08-02 18:00), -6h ~ +12h
(`offset`은 방류시작시간의 시(18)를 SDATE 라벨 시로 그대로 대응시킨 **naive 정렬**이며 시각 규약 미확정이라 ±1시간 불확실)
{F['case_meas']}
→ `case_AP-3412_measurement_minus6h_plus12h.csv`. 기간 전체 시계열은 4절 그래프.

### (4) Criterion
- **{cr02['criterion_id(연구용 임시ID)']}** {cr02['locator_in_document']} — {cr02['verbatim_text_or_value']} ({cr02['unit']})
- 관련 조문 **제6조**(원문): {art6['verbatim_text_or_value']}

### (5) Document
- 「댐과 보 등의 연계운영규정」 [별표3] / 제6조. 원문 XML, 원본 PDF/HWPX 경로는 2-6절. 소관: 기후에너지환경부(수자원관리과 표기), 출처 URL: `http://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000282102&type=XML`.

## 4. 시계열 그래프

![충주댐 2020-07-30~08-12](data_review/case_chungju_2020-08_timeseries.png)

- 파일: `04_reports/data_review/case_chungju_2020-08_timeseries.png` (벡터: `.svg`)
- 패널별 자기 축(이중축 없음). 세로 주황 점선 = 승인 파일의 `방류시작시간`(2020-08-02 18:00, 2020-08-06 06:00), 점선 회색 = [별표3] 홍수기 제한수위 138.0. 데이터는 `getHydr` hourly 원본 field(DATA1 수위, DATA4 유입량, DATA6 총방류량, DATA3 강우량) 313행.
- 이 그래프는 값을 나란히 보여줄 뿐이며 승인과 측정 변화의 관계를 해석하지 않는다. 시각 축은 라벨 기준 표시.

## 5. 원본(RAW)과 정규화본 비교

### 5-1. Approval record (순차번호 3412)
**RAW** — `01_raw/FloodControl/환경부_한강홍수통제소_홍수예보_댐방류승인_20220727.csv` (cp949, 헤더+해당 행):
```
{F['raw_ap']}
```
**NORMALIZED** — `03_normalized/approval_records_hrfco_raw_fields.csv` (UTF-8):
```json
{F['norm_ap']}
```
- 그대로 유지: 원본 8개 컬럼 이름과 값 전부(값 변형·형식 변환 없음).
- 추가된 것: `row_number_in_file`, `source_organization`, `source_dataset_page_url`, `download_url`, `original_file_name`, `file_sha256`, `retrieval_time_utc`(파일 mtime; 별도 다운로드 시각 미기록), `encoding_of_original`.

### 5-2. MyWater getHydr 시간 record (충주댐)
**RAW JSON 한 행** — `{F['raw_hydr_file']}` 의 `list[0]`:
```json
{F['raw_hydr']}
```
**NORMALIZED** — `03_normalized/kwater_mywater_hydr_H_wide.csv.gz`:
```json
{F['norm_hydr']}
```
- 그대로 유지: `SDATE`(→`SDATE_raw`), `DATA1~7` 값의 숫자 내용, `DAM_CD`. 단, **원본 JSON의 숫자형(예: `47.75`)이 CSV에서는 텍스트로 저장되어 자료형 정보는 유지되지 않는다**(일부 필드는 원본에서도 문자열; 예: 일자료 `"DATA2": "1577.3207"`).
- 추가된 것: `source_file`, `retrieval_time_utc`(요청 manifest 기준), `param1_resolution`; 컬럼 머리글에 출처 페이지 라벨 병기(DATA5는 '라벨 미확인').

### 5-3. MyWater getPeriod (COLn → 댐 대응)
**RAW** — `{F['raw_period_file']}` `periodList[0]` (열 이름 COLn은 응답 안의 `damList.RNUM`으로만 댐과 대응):
```json
{F['raw_period_row']}
```
충주댐 `damList` 항목(이 응답 기준 `{F['period_col']}`):
```json
{F['raw_period_dam']}
```
**NORMALIZED** — `03_normalized/kwater_mywater_period_hourly_long.csv.gz` (해당 셀 1행):
```json
{F['norm_period']}
```
- 그대로 유지: 값 문자열(`value_raw`), `SDATE_raw`.
- 추가된 것: 댐 식별(`DAM_CD`, `DAM_NM_source`, `RIVR_NM_source_label`), 변수 이름·단위(출처 페이지 표기), `key_present_in_raw`(결측=키 없음 구분), `COL_index_in_response`, provenance.

## 6. 파일 위치 (이 문서에서 보여준 자료)
| 자료 | 경로 |
|---|---|
| 표본 CSV·그래프 | `04_reports/data_review/` (`sample_*.csv`, `case_*.csv`, `case_chungju_2020-08_timeseries.png/.svg`) |
| Dam | `03_normalized/dam_catalog.csv`, `dam_catalog_kwater_basic.csv`, `dam_basic_raw_all_damGb.csv` |
| ObservationStation | `03_normalized/observation_station_list.csv` |
| MeasurementDataset 목록 | `03_normalized/measurement_dataset_list.csv` |
| Measurement 정규화 | `03_normalized/kwater_mywater_*_long.csv.gz`, `kwater_mywater_hydr_{{D,H}}_wide.csv.gz` |
| Measurement 원본 | `01_raw/KWater/mywater_period/`, `mywater_station/`, `mywater_approval_linked/` (압축: `01_raw_archive/`) |
| Approval | 원본 `01_raw/FloodControl/…csv`, 정규화 `03_normalized/approval_records_hrfco_raw_fields.csv` |
| 연결 사례 | `03_normalized/linkage_pilot_cases.csv`, `linkage_pilot_measurement_extract.csv` |
| Criterion / Document | `03_normalized/criterion_list.csv`, `document_list.csv`, `law_admrul_annex_000300_text.txt`; 원본 `01_raw/Law/`, `01_raw/Regulations/` |
| 상·하류 evidence | `03_normalized/dam_network_evidence.csv`, `han_system_membership_byeolpyo1.csv` |
| 변수 정의 / 시각 규약 | `02_metadata/variable_dictionary.csv`, `time_conventions.csv` |
| 종합 | `STEP0_summary.md`, `04_reports/I_Ontology_Compatibility_Report.md`, `J_*`, `K_*` |
"""
open("04_reports/L_DATA_REVIEW.md","w",encoding="utf-8").write(md_out)
print(len(md_out))
