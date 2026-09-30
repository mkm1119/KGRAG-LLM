# MASTER RESEARCH EXECUTION REPORT (STEP 1 → 2 → 3)

작성일 2026-09-30. Hard Stop 없이 STEP 1–3을 연속 수행. 모든 미결은 `STEP1_DECISION_LOG.md`에 누적(기존 상태 변경 없음, RESOLVED 승인 없음).

## 1. Canonical architecture (변경 없음)
Ontology → KG → Hybrid Retrieval → LLM, 3-STEP(Knowledge Design / Construction / QA). 목적: 운영자의 판단 **지원**(자동 방류 결정 아님). canonical 원본 `01_AI_RESEARCH_HANDOFF.md`는 저장소 밖(업로드 폴더) 보관.
## 2. 사용 문헌 (원문 직접 대조; `STEP1_METHOD_EVIDENCE.md`)
Noy & McGuinness, Li et al. 2025(Water 17, 2801), OntoDSMS(Zhou et al.), DDKG(Huang et al., AEI 76), GraphAide(Purohit et al.). **LSMKG 원문 없음(검증 불가).**
## 3. STEP 1
절차·결과: `STEP1_KNOWLEDGE_DESIGN_FULL_REPORT.md`, `N_STEP1B_...`, `STEP1_REVISION_CANDIDATES.md`. 요소 24개 중 KEEP 9 / REVIEW_REQUIRED 8 / NOT_TESTABLE 7. CQ: KEEP 1, KEEP_WITH_REVIEW 3, REVISION_CANDIDATE 2. v0.1·CQ 미변경. Working Ontology Candidate v1 = v0.1 24 + 후보 26 + 보류 2.
## 4. STEP 2
`STEP2_*`. Pilot KG: 4,181 엔티티 / 4,072 관계 / 24,468 속성 / provenance 32,721. 관계는 원천이 명시한 4종만(Approval·Dataset→Dam concernsDam, Dam→Station monitoredBy, Criterion→Document definedIn). 검증 V1–V10 PASS.
## 5. STEP 3
`STEP3_*`. 질문 11개(직접 6/자연 5), 규칙 기반 검색, claim 25개(근거 검사: 통과 22, 제외 대조 3). KG 필요성: 이 pilot에서 표 검색 대비 추가 능력 관찰되지 않음(입증도 반증도 아님).
## 6. Cross-stage 진단
① 시설 동일성 미해결(S0-D)이 KG 매핑에서 Approval과 측정 자료를 다른 연결 성분으로 분리 → N01/N04. ② Approval–Criterion·Operation 부재로 "당시의 승인·기준·근거" 사슬이 끊김 → N02, Q05, Q06. ③ 시점 적용성 자료 부재 → Q06. ④ 유사 사례 검색 미설계 → N05. 온톨로지 결함이라기보다 **원천 의미·자료 부재**가 주 원인이며, 온톨로지에서는 Approval→Dam과 Criterion→Dam 경로 부재가 실제 구조 문제다.
## 7. 해결된 결정(이번 실행 중 작업 수준; 사용자 승인 대상 아님)
후보 기반 진행(v0.1 불변), 출처별 Dam identity, 원천 필드 명칭 보존, 측정값은 KG 밖 조회, 추론 관계 0.
## 8. 남은 모호성
S0-B 필드 의미, S0-D 시설 동일성, S0-E 시간 규약, S1A-06 상·하류, S1A-07 시점 적용성, S1A-09 Operation, S1A-10 행위자, 승인·측정 저장 방식(handoff §6.3).
## 9–11. 수정 후보
Ontology: RC-01~10 + RC-11(Criterion→Dam 또는 시설 속성). KG mapping: 데이터셋 실제 커버리지, 그룹 dataset의 Dam 연결, 시설 동일성 규칙. Retrieval: 유사도 정의, 텍스트(비정형)·벡터 검색 도입 여부, 시간창 규약.
## 12. 전문가 검토 항목
`STEP1_KNOWLEDGE_DESIGN_FULL_REPORT.md` §10 (7종) + STEP 3 답변의 독립 평가.
## 13. 추가 데이터 필요
규정 개정 연혁(당시 기준), Operation record, 승인 CSV 필드 정의서, 공식 시설 코드 대응, 승인 후 실제 방류 장기 시간자료.
## 14. 문헌 직접 주장
Noy 7단계·CQ 역할; OntoDSMS 테이블→클래스 매핑 원칙과 Noy 적용; DDKG의 Dam anchor 구조; Li의 "문맥 증거 있을 때만 관계 생성"; GraphAide의 구성요소별 평가 원칙.
## 15. 본 연구 적용(문헌 비직접)
CQ 검토 기준·판정 코드, 요소 검증 verdict, 출처별 Dam 인스턴스, concernsDam, claim 5분류, KG 필요성 체크리스트, 규칙 기반 검색.
## 16. 미검증 주장
LSMKG 관련, SOSA/SSN/PROV-O/HY_Features 등 기존 온톨로지, GraphAide의 시계열 결합(논문이 시연하지 않음), 답변 검사의 의미 정확성, 환각률.
## 17. handoff와 원문의 차이
D1–D6 (`STEP1_METHOD_EVIDENCE.md` §3): 특히 GraphAide는 KG+텍스트+측정 결합을 시연하지 않았고, DDKG는 hazard 분류 중심이며 Noy를 인용하지 않고, OntoDSMS는 안전 모니터링 도메인이다.
## 18. 이 실행이 하지 않은 것
Ontology/CQ 덮어쓰기, Operation 생성, Approval–Criterion 연결, 시설 병합, 상·하류 관계, 근거 추론, 임의 임계값·신뢰도, 구현 기술 확정.
## 19. 파일 목록
04_reports: STEP1_KNOWLEDGE_DESIGN_FULL_REPORT, STEP1_METHOD_EVIDENCE, STEP1_REVISION_CANDIDATES, N_STEP1B_..., STEP1_DECISION_LOG, STEP2_KG_CONSTRUCTION_REPORT, STEP2_METHOD_EVIDENCE, STEP2_MAPPING_VALIDATION, STEP3_QA_REPORT, STEP3_METHOD_EVIDENCE, STEP3_RETRIEVAL_EVALUATION, STEP3_GROUNDED_ANSWER_EVALUATION. 03_normalized: step1_*.csv, working_ontology_candidate_v1.csv, kg_*_pilot.csv, mapping_rules_pilot.csv, kg_validation_results.csv, qa_*.csv. scripts: step1_*, step2_*, step3_*.

## 최종 상태표
| Decision | Evidence | Literature-direct | Study adaptation | Actual-data support | Status |
|---|---|---|---|---|---|
| Ontology v0.1 유지, 변경은 후보로만 | 요소 검증 24 | Noy Step 4–5 | 판정 코드 | Y | CONFIRMED |
| Approval–concernsDam→Dam | 승인 3,929건 시설 필드 | DDKG anchor 패턴 | 적용 | Y | PROVISIONAL |
| MeasurementDataset–concernsDam→Dam | 댐 단위 제공 | - | Y | Y | PROVISIONAL |
| approvedReleaseAmount ← 접수방류량 | - | - | - | 의미 불명 | REVIEW_REQUIRED |
| Approval-file Dam ≡ MyWater Dam | 코드·이름 유사 | - | - | 부분 | EXPERT_REVIEW_REQUIRED |
| Approval–Criterion 관계 | - | - | - | 시점·근거 없음 | DATA_REQUIRED |
| Operation 클래스 검증 | - | - | - | record 없음 | DATA_REQUIRED |
| CQ3/CQ4 수정 | CQ 검토 | Noy CQ 역할 | 검토 기준 | Y | REVIEW_REQUIRED |
| 상·하류 관계 | 단일 출처 서술 | - | - | 약함 | DEFERRED |
| 측정값 KG 저장 여부 | - | GraphAide(미시연) | 파일 조회 | - | PROVISIONAL |
| 기존 온톨로지(SOSA/SSN 등) 재사용 | 검색만 | OntoDSMS SSN/SOSA | - | - | REVIEW_REQUIRED |
| 규칙 기반 검색 + claim 검사 | QA 11문 | GraphAide 평가 원칙 | Y | Y | PROVISIONAL |
| KG 필요성 | pilot 관찰 | 없음 | 체크리스트 | flat 자료 | REVIEW_REQUIRED |
| LSMKG 근거 | 파일 없음 | - | - | - | DEFERRED |
