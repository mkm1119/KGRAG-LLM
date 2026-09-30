# STEP 1 — Revision Candidates (적용하지 않음; 사용자 검토용)

Initial Ontology v0.1과 CQ1~6은 그대로다. 아래는 **후보**이며 상태는 전부 REVIEW_REQUIRED 이상이다.

## A. Ontology
| ID | 후보 | 근거(실제 자료) | 문헌 근거 | 상태 |
|---|---|---|---|---|
| RC-01 | Approval–concernsDam→Dam | 승인 3,929건이 record마다 시설(관측소코드·명)을 가짐; Operation 없음 | A(DDKG: 모든 클래스가 Dam에 연결, p.4) + B(적용) | REVIEW_REQUIRED |
| RC-02 | MeasurementDataset–concernsDam→Dam | 장기 측정은 댐 단위 제공(getPeriod/getHydr) | B | REVIEW_REQUIRED |
| RC-03 | Approval 원문 필드 속성(releaseStartTime, receivedDate, receivedReleaseAmount, approvalDateSource, remarks, sourceSequenceNo) | Approval CSV 컬럼; 의미 미확정 | A(Noy Step 5 속성 개념)+B | REVIEW_REQUIRED (approvedReleaseAmount 매핑 미확정) |
| RC-04 | Criterion 값·단위·위치 속성 | criterion_list 15건 | B | REVIEW_REQUIRED |
| RC-05 | Document 제목·시행일·버전 속성 | 규정 XML 기본정보 | B | REVIEW_REQUIRED; 효력 종료일 자료 없음 |
| RC-06 | Dam 시설 유형 속성(클래스 분할 여부 별도) | DAM_BO_NM 등 | Noy 4.5(p.17) | REVIEW_REQUIRED |
| RC-07 | Dam 출처 식별 속성(sourceSystem/code/name) — 병합 금지 | 코드·명칭 불일치 | B | REVIEW_REQUIRED |
| RC-08 | Dataset/Station 기술 속성 | dataset 71, station 94 | A(속성 개념)+B | REVIEW_REQUIRED |
| RC-09 | upstream/downstream | dam_network_evidence 11건(단일 출처) | C | HELD |
| RC-10 | Actor/Organization | 규정 제2조 | C | HELD |

## B. CQ (문구 미수정)
CQ3(접근 경로), CQ4(당시 시점), CQ5(분리 여부) — `N_STEP1B...` §3. CQ GAP G-1~G-4.

## C. Scope
SR-1 '기상' 범위(관측/예보), SR-2 상·하류, SR-3 운영기준 범위.

## D. 데이터 필요
연혁별 규정 버전(당시 기준), Operation record, 필드 정의서(승인 CSV), 시설 코드 대응표(공식).
