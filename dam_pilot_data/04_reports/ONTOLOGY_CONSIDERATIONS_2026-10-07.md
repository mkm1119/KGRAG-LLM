# 온톨로지 고려사항 (미적용, 테스트로 확인)

- 작성일: 2026-10-07
- 기준 문서: 랩미팅 자료 최종본7 (2026.10.02), 교수님 도시침수 개념 정리 PDF(「Urban Flood Ontology–KG 지식 시스템 중간 정리」)
- 방침: 아래 항목은 **온톨로지 문서에 반영하지 않는다.** 실제 데이터로 KG를 구축하고 LLM 답변까지 테스트한 뒤, 문제가 확인된 항목만 개선한다 (교수님 자료 10~12쪽 Ontology↔KG 공진화).
- 문서에 반영한 것은 용어표 한 곳뿐이다: `Property` 항목을 추가하고 Relation(Object Property)과 Data Property를 그 아래 두 갈래로 표기 (최종본8_용어정리).

## 고려사항과 테스트 확인 항목

| # | 고려사항 | 근거 | 현재 설계 | 테스트에서 확인할 것 |
|---|---|---|---|---|
| C1 | 관계 방향 | 랩미팅 17:34, 21:52 (전사 불명확: "방향만 맞춰주면"). 교수님 PDF에는 방향 규칙 없음 | 관계 의미상 자연스러운 방향으로 정의, 역방향은 탐색에서 사용 | 역방향 탐색(예: Dam → Criterion)이 실제로 되는가 |
| C2 | Criterion과 EvidenceSource 구분 | 랩미팅 14:18, 17:34 ("애매") | `supportedBy` 유지. Criterion = 기준값, EvidenceSource = 그 값이 적힌 문서·위치 | CQ5·CQ6 답변에서 기준값과 근거 위치가 구분되어 나오는가 |
| C3 | 시간 | 랩미팅(방류 시간에 수치 데이터를 엮기). PDF 4·19~20쪽(시간 Data Property, 시간 조건, Temporal Index) | `operationTime`, `approvalTime` 단일 값 | 시점 기준 수치 조회 정확성. 승인(날짜만)과 방류시작(시각) 불일치. 방류는 구간이므로 시작·종료 구분 필요 여부 |
| C4 | 제약 (허용되는 관계·값) | PDF 3·13쪽 (Constraints/Rules, semantic contract, Ontology Validation) | 없음 | 적재 시 형식·값이 어긋난 자료가 얼마나 나오는가. 많으면 제약표 추가 |
| C5 | Class 정의와 승격 기준 | PDF 5~6쪽 (독립 identity + 추가 Property/Relation) | Class별 의미·예·CQ만 기재 | 응답이 Class 경계(예: Operation vs Approval)를 혼동하는가 |
| C6 | 문서·측정자료 연결 | PDF 18쪽 (`documentedBy`, `hasDataset`, `observedBy`를 Relation으로) | `supportedBy` 하나로 통합, `sourceType`·`sourceLocator`·`stationCode`로 구분 | 문서와 측정자료를 분리해서 찾아갈 수 있는가 |
| C7 | 가상 데이터 표시 | 랩미팅(승인·운영 이력은 가짜 데이터로 우선 테스트) | 없음 | 가상 데이터를 쓴 답변에서 실제 기록과 구분이 필요한가. 필요 시 `sourceType`에 "가상(테스트용)" 값 |
| C8 | Provenance·Confidence·fact 유형 | PDF 9쪽 | `EvidenceSource`·`supportedBy`가 근거 관리 역할. 별도 개념은 불필요로 판단 | 근거 없는 답변이나 근거 혼동이 나타나는가 |
| C9 | Layer | PDF 6~7쪽 (관리용 묶음, formal type 아님) | 사용하지 않음 (Class 6개) | 해당 없음 |
| C10 | Entity Resolution·Linking | PDF 8~9쪽 | STEP 2 과제 | 기관별 댐·관측소 코드(K-water, 기상청, 한강홍수통제소) 대응 |
| C11 | 온톨로지 표현("확정") | PDF 10~12쪽 (공진화, Human-in-the-loop) | "STEP 1 완료" | 테스트 결과를 반영해 버전으로 관리 |
| C12 | Approval–Dam 직접 관계 부재 | STEP 3B 결과 | Approval은 Operation을 거쳐야 Dam에 닿음 | Operation 없는 승인 38건이 승인 목록 질문에서 누락 (Q03 1/3, Q11 0/3). 직접 관계를 넣은 변형으로 비교 |
| C13 | Dam 간 상하류 관계 | STEP 3B Q07 | 없음 | 상하류 질문이 실제로 나오는지, 필요하면 어떤 근거 자료로 채울지 |
| C14 | Operation 정의와 사유 속성 | STEP 3B Q08 | 사유 속성 없음, 비고에서 분류한 행위 | 승인 비고에 사유가 거의 없음. 한수원 현장방문에서 운영 기록 확인 후 판단 |
| C15 | stationCode의 의미 | STEP 3B 구축 | 댐 단위 시설 코드를 사용 (관측소 코드 아님) | 우량·수위 관측소 단위 값이 필요한 질문이 나오는지 |
| C16 | Criterion의 적용 시점 | STEP 3B Q05 | 현행 규정 값 하나 | 과거 운영행위와 비교할 때 당시 기준과의 차이 (규정 개정 이력 활용) |

## 데이터 관련 유의점 (테스트 입력)

- 실제 Operation 기록은 확보하지 못했다. 한강홍수통제소 방류승인 CSV는 승인 기록이며, 방류시작시간을 운영 시점의 대용으로 쓴다.
- 승인일자는 날짜만 있고, 방류시작시간은 별도 컬럼이다.
- 가상 승인·운영 이력은 "방류량이 있으면 승인된 것으로 본다"는 기준으로 만든다 (랩미팅 교수님 언급).

## 개선 반영 절차

1. 테스트 결과에서 문제가 확인된 항목만 선별한다.
2. 선별한 항목을 온톨로지 문서에 반영하고 버전을 올린다.
3. 반영하지 않은 항목은 근거(테스트에서 문제 없음)와 함께 이 표에 남긴다.
