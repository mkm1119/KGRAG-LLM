# G. API Requirement Report (사용자 조치가 필요한 API)

작성 기준일: 2026-09-29 (UTC). 모든 내용은 세션 중 실제로 열람한 공식 페이지 원문(`01_raw/DataGoKr/catalog_pages/`) 기준이며,
확인하지 못한 항목은 "미확인"으로 표기했다. **API key는 채팅에 요구하지 않는다.** 스크립트는 환경변수(`SERVICE_KEY`)를 사용한다.

## 0. 이번 세션 네트워크에서의 실제 접근 결과 요약

| Source | 결과 | 비고 |
|---|---|---|
| MyWater (www.water.or.kr) | **접근 가능, 인증 없이 시계열 수집 성공** | 사이트 자체 ajax endpoint |
| K-water (www.kwater.or.kr) | 접근 가능 (HTML) | 시설 소개 텍스트 |
| 공공데이터포털 (www.data.go.kr, apis.data.go.kr) | 접근 가능(간헐적 연결 리셋, 재시도로 성공) | API는 키 필요: 키 없이 호출 시 `401 SERVICE_KEY_IS_NULL` 확인 |
| KHNP (www.khnp.co.kr) | 접근 가능 (HTML) | 현재/전일 수문자료만 |
| 법제처 (www.law.go.kr) | 접근 가능(간헐적 리셋) | `law.go.kr`(www 없음)·`open.law.go.kr`는 egress 차단 |
| 기상자료개방포털 (data.kma.go.kr) | 페이지 접근 가능 | `apihub.kma.go.kr`·`www.kma.go.kr` egress 403. 상세 다운로드는 로그인 필요 |
| **WAMIS (www.wamis.go.kr)** | **접근 불가** | http: 503(upstream connect timeout), https: 연결 리셋 (다회 재시도 동일), `wamis.go.kr` egress 403 |
| **한강홍수통제소 (www.hrfco.go.kr, api.hrfco.go.kr)** | **접근 불가** | https 연결 리셋, http 503, `hrfco.go.kr` egress 403 |
| 환경부 (www.me.go.kr) | egress 403 | |
| opendata.kwater.or.kr | egress 403 | |

원자료: `04_reports/access_probe.tsv`, `access_probe_retry.tsv`, 프록시 상태 로그.

## 1. 사용자가 직접 해야 하는 조치

### 1-1. 세션 네트워크(egress allowlist) 요청 — 조치 없이는 아래 자료가 수집 불가
WAMIS/한강홍수통제소는 이번 세션에서 **호스트 응답 자체가 없거나(연결 리셋/503) 정책으로 차단**되었다. 현재 확인된 상태만 보고하며, 원인(해외 IP 차단인지 egress 정책인지)은 이 세션에서 판별하지 못했다(추정하지 않음).

허용(또는 접근성 확인)이 필요한 호스트:
`www.wamis.go.kr`, `wamis.go.kr`, `www.hrfco.go.kr`, `api.hrfco.go.kr`, `hrfco.go.kr`, `apihub.kma.go.kr`, `www.kma.go.kr`, `open.law.go.kr`, `law.go.kr`, `www.me.go.kr`, `opendata.kwater.or.kr`

### 1-2. 공공데이터포털 serviceKey (무료, 자동승인 API 위주)
신청 사이트: https://www.data.go.kr → 로그인 → 각 API 상세 페이지 "활용신청". 발급된 일반 인증키(Encoding/Decoding)를 환경변수 `SERVICE_KEY`로 세션에 제공.

| API | data.go.kr ID | endpoint (카탈로그 원문) | 심의 | 개발계정 트래픽 | 주요 필수 파라미터 |
|---|---|---|---|---|---|
| K-water 수문 운영 정보 | 15099110 | `https://apis.data.go.kr/B500001/dam/sluicePresentCondition/{hourlist\|…}` (시간/10분/일 3종) | 개발·운영 자동승인 | 10,000/일 | serviceKey, pageNo, numOfRows, damcode(7자리), stdt, eddt(YYYY-MM-DD), _type(json/xml) |
| K-water 다목적댐 운영 정보 | 15099049 | `https://apis.data.go.kr/B500001/dam/multipurPoseDam/multipurPoseDamlist` | 자동승인 | 100/일 | serviceKey, pageNo, numOfRows, tdate, ldate, vdate, vtime |
| K-water 용수댐 운영 정보 | 15099047 | `https://apis.data.go.kr/B500001/dam/waterDam/waterDamlist` | 자동승인 | 100/일 | (동일 계열) |
| K-water 댐코드 조회 | 15099105 | `https://apis.data.go.kr/B500001/dam/damCode/damCodelist` | 자동승인 | 100/일 | serviceKey, pageNo, numOfRows |
| K-water 수문 제원 현황 | 15099107 | `https://apis.data.go.kr/B500001/dam/dataPresent/dataPresentlist` | 자동승인 | 100/일 | serviceKey, pageNo, numOfRows, damcode |
| 한강홍수통제소 표준수문DB | 3040409 | LINK형(실제 호출 host `api.hrfco.go.kr` 추정 — **카탈로그에서 endpoint 미확인**, 사이트 접속 불가로 검증 못함) | 운영단계 자동승인 | 기관 정책 | 미확인 |
| 행정안전부 홍수통제소 수위10분 / 우량10분 / 유량분 | 15153508 / 15150667 / 15150614 | 카탈로그에 URL 미노출 | 개발 자동승인, **운영 심의승인** | 기관 정책 | 미확인 |
| 행정안전부 댐제원정보 | 15153328 | 카탈로그에 URL 미노출 | 운영 심의승인 | 기관 정책 | 미확인 |
| 한국수자원공사 수문 방류정보 조회 서비스 | 15140222 | `http://opendata.kwater.or.kr/openapi-data/service/pubd/dam/flugtDschgInfo/list` (opendata.kwater.or.kr는 egress 차단) | **심의승인** | 10,000/일 | 미확인 |

- 응답 항목(15099110, 카탈로그 원문): `obsrdt`(일시), `lowlevel`(댐수위 EL.m), `rf`(강우량 ㎜), `inflowqy`(유입량 ㎥/sec), `totdcwtrqy`(총방류량 ㎥/sec), `rsvwtqy`(저수량 백만㎥), `rsvwtrt`(저수율 %).
  - 카탈로그가 밝힌 보유기간: 2006-01 ~ 현재(지점별 상이), 제공지점 61개소, 주기 10분/시간/일.
  - pagination: `pageNo`/`numOfRows`. date limit / rate limit: 카탈로그에 일일 트래픽만 명시(초당 제한 미확인).
- 키 없이 호출 시 응답(저장됨: `01_raw/DataGoKr/probe_nokey/`): HTTP 401, `SERVICE_KEY_IS_NULL`.

### 1-3. 법제처 OC
`open.law.go.kr` 회원가입 후 OC(이메일 ID) 등록. 이번 수집은 문서상 샘플값 `OC=test`를 사용했다(정식·대량 사용 전 본인 OC 필요).

### 1-4. 기상청
- API허브(`apihub.kma.go.kr`): 회원가입·로그인 후 API 신청 → authKey. 이번 세션에서는 egress 403.
- 기상자료개방포털(`data.kma.go.kr`) ASOS/AWS 다운로드: 로그인(회원가입) 필요. 페이지가 "조회 결과는 10건만 표출, 상세결과는 파일 다운로드"라고 안내 → 대량 수집은 로그인 후 다운로드 또는 API허브 authKey 필요. 자동 우회는 수행하지 않았다.

## 2. 인증키 없이 수집한 것과 그 한계
- MyWater ajax endpoint는 **공식 문서화된 OpenAPI가 아니다**(사이트 페이지 JS에서 확인한 내부 endpoint). 사이트 개편 시 변경될 수 있고, 이용약관상 자동수집 허용 여부는 이번 세션에서 확인하지 못했다(요청 간 1초 이상 간격, 동시 요청 4개 이하로 제한하여 수행).
- 공식 OpenAPI(15099110)로 같은 자료를 재수집하면 동일 시계열의 교차검증이 가능하다(키 발급 후 재개 작업).

## 3. 사용자 조치 후 재개 작업
1. WAMIS/HRFCO 접근 허용 → 한강수계 댐·보 관측소 목록, 표준수문DB 댐자료, 방류승인 관련 공개자료 수집, 하천·수계 연결 정보 확인.
2. serviceKey 제공 → 15099110 재수집(교차검증), 15099105/15099107(댐코드·제원), 홍수통제소 계열 API.
3. 기상청 authKey 또는 로그인 다운로드 → ASOS/AWS 강수(원본 보존), Dam–Station 대응표 작성(선정사유 기록).
