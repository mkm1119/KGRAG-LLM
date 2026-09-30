# STEP 2 — Method Evidence (WHAT THE PAPER DID / WHAT THIS STUDY ADOPTS)

원문은 `references/evidence_literature/`의 PDF를 직접 읽음(세부 쪽 번호는 `STEP1_METHOD_EVIDENCE.md` §2-2~2-4). A 문헌 직접 / B 본 연구 적용 / C 검토 필요.

| 항목 | 논문이 실제로 한 것 | 본 연구의 채택 | 수준 |
|---|---|---|---|
| 구조화 데이터 → 온톨로지 매핑 | OntoDSMS(p.6–7): 관계형 DB를 D2RQ로 가상 RDF에 매핑, 테이블→클래스·컬럼→DatatypeProperty·행→인스턴스·셀→Literal, 자동 생성 매핑을 온톨로지 용어에 맞게 수정 | 같은 **매핑 원칙**을 CSV에 적용(행→인스턴스, 열→속성). D2RQ/SPARQL/RDF는 사용하지 않고 CSV로 구현(구현 기술 미결정) | A(원칙)/B(구현) |
| 데이터 복제 여부 | OntoDSMS는 가상 그래프(복제 없음) | 시계열 값은 KG에 저장하지 않음(MyWater 원본 파일 참조); 메타데이터만 노드화 | B |
| 모든 정보를 Dam에 anchor | DDKG(p.4): 모든 최상위 클래스를 Dam에 연결 | Approval·MeasurementDataset을 concernsDam으로 Dam에 연결 | A(패턴)/B |
| 비정형 문서→KG | DDKG(p.7–9): hazard 텍스트의 분류(라벨), 미세조정·투표·온톨로지 제약 검사·전문가 검증 | **사용하지 않음.** 본 pilot은 LLM 추출 없이 구조화 자료·규정 조문 단위 수동/규칙 매핑. 규정 조문에서 관계 추출은 수행하지 않음 → 문헌 근거가 없는 확장을 하지 않기 위함 | A(논문의 범위)/미채택 |
| 관계 생성 조건 | Li et al.(p.13): 클래스 간 관계가 유효해도 모든 개체 쌍에 성립하지 않으며 충분한 문맥 증거가 있을 때만 KG에 관계 생성 | 원천이 명시한 연결만 생성(Approval의 시설코드, 데이터셋 요청 시설, 조회 관측소 목록, 조문의 문서). 추정 관계 0 | A(원칙)/B |
| 전문가 검증 | DDKG p.8, Li p.9–12 | 프로토콜 미정의; REVIEW_REQUIRED 항목만 표시 | C |
| 제약/일관성 검사 | DDKG: 충돌 라벨쌍 집합 기반 ontology-constraint consistency check(hazard 라벨 대상) | 본 연구는 구조 무결성 검사(V1–V12)만 수행. 의미 제약 검사는 하지 않음(제약 미확정, S1G-01) | B |
| 저장소 | DDKG Neo4j(201,362 노드) | 미결정 — CSV | - |
| 평가 | OntoDSMS: SQL vs 온톨로지 검색 시간 비교 | STEP 3에서 검색 시간 비교 안 함(임의 지표/임계값 금지); 질적 필요성 점검 | B |

**문헌이 뒷받침하지 않는 것:** 규정 조문·승인 CSV를 KG로 옮기는 절차 자체를 직접 다룬 문헌은 확보 원문에 없음. 본 pilot 매핑은 전반적으로 B(본 연구 적용)이며, 원칙만 A이다.
