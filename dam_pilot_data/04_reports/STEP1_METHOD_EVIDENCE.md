# STEP 1 — Method Evidence (문헌 원문 대조)

- 작성일: 2026-09-30. 기준: `01_AI_RESEARCH_HANDOFF.md`(canonical) + 마스터 실행 지침.
- **원문 대조 방법:** `references/evidence_literature/`의 PDF를 표준 라이브러리 추출기(`dam_pilot_data/scripts/pdf_text_extract.py`, `pdf_text_extract2.py`)로 텍스트화해 직접 읽었다. 쪽 번호는 **PDF 쪽**(인쇄 쪽과 일치 확인: Noy, Li, DDKG). 표(table) 내용과 그림은 추출되지 않은 경우가 있다.
- **읽지 못한 것:** `11_LSMKG.pdf`는 저장소에도 업로드에도 **존재하지 않는다**(한 번도 공유되지 않음). handoff §17의 Zhang et al. (2025)과 같은 논문인지도 확인할 수 없다 → STEP 3의 해당 근거는 `LITERATURE_CHECK_REQUIRED`.
- 근거 수준: **A** LITERATURE-DIRECT / **B** STUDY-ADAPTATION / **C** REVIEW-REQUIRED.

## 1. 원문 확인 결과 (논문별)

| 파일 | 서지(원문 1쪽 기준) | handoff의 역할 | 원문 확인 결과 |
|---|---|---|---|
| `Noy.pdf` | Noy & McGuinness, *Ontology Development 101: A Guide to Creating Your First Ontology*, Stanford. (PDF에 연도 없음; Li 2025의 참고문헌 10번이 "Technical Report KSL-01-05, Stanford Knowledge Systems Laboratory, 2001"로 표기 — 간접 확인) | STEP 1 주 방법론 | 지지됨 (§2-1) |
| `36_FloodOntology.pdf` | Li, Erickson, Zajac, Guo, Duan, Gong. *A Semi-Automated Framework for Flood Ontology Construction with an Application in Risk Communication*. Water 2025, 17, 2801 (1쪽 표기 게재 2025-09-23) | expert/human review 보강 | 지지됨, 단 범위 주의 (§2-2) |
| `47_OntoDSMS.pdf` | Zhou, Bao, Shu, Li, Li. *BIM and ontology-based knowledge management for dam safety monitoring* (Automation in Construction 계열; 1쪽 저널명은 추출되지 않음) | STEP 2 structured/monitoring data ↔ ontology mapping | 지지됨, 범위 주의 (§2-3) |
| `46_DDKG.pdf` | Huang, Hou, Zhang, Du, Yin. *Dam defects ontology and knowledge graph construction from Multi-Source hazard data using large language models*. Advanced Engineering Informatics 76 (2026) 104987 | STEP 2 unstructured documents → KG | 지지됨, 범위 주의 (§2-4) |
| `39_GraphAide.pdf` | Purohit, Chin, Mackey, Cottam. *GraphAide: Advanced Graph-Assisted Query and Reasoning System*, PNNL | STEP 3 hybrid retrieval | 부분 지지 (§2-5) |
| `11_LSMKG.pdf` | (없음) | STEP 3 query understanding / KG QA | **검증 불가** |

## 2. 논문이 실제로 수행한 것 (WHAT THE PAPER ACTUALLY DID)

### 2-1. Noy & McGuinness
- **절 구조:** 1 Why develop an ontology? (p.1) / 2 What is in an ontology? (p.3) / 3 A Simple Knowledge-Engineering Methodology (p.4) / 4 Defining classes and a class hierarchy (p.12) / 5 Defining properties—more details (p.20) / 6 Naming (p.22) / 7 Other Resources / 8 Conclusions (p.23).
- **일곱 단계:** Step 1 Determine the domain and scope (p.5); Step 2 Consider reusing existing ontologies (p.5–6); Step 3 Enumerate important terms (p.6); Step 4 Define the classes and the class hierarchy (p.6–8); Step 5 Define the properties of classes—slots (p.8–9); Step 6 Define the facets of the slots (p.9–11); Step 7 Create instances (p.11).
- **전제(p.4):** "there is no one 'correct' way or methodology"; 규칙 "There is no one correct way to model a domain"; "Ontology development is necessarily an iterative process"; 초기 온톨로지는 "using it in applications or problem-solving methods or by discussing it with experts in the field, or both"로 평가·디버깅하며 "almost certainly need to revise the initial ontology". **문헌은 처음부터 만드는 경우를 가정한다**(p.6 "start developing the ontology from scratch").
- **Step 1(p.5):** 네 기본 질문(domain / 용도 / 질문 종류 / 사용·유지 주체); competency questions는 scope를 정하는 방법 중 하나이며 "litmus test", "just a sketch and do not need to be exhaustive".
- **Step 2(p.5–6):** 기존 온톨로지 재사용 검토("almost always worth considering what someone else has done"); 형식(formalism)은 대개 중요하지 않다.
- **Step 3(p.6):** 용어를 "without worrying about overlap between concepts they represent, relations among the terms, or any properties ..., or whether the concepts are classes or slots" 포괄적으로 나열.
- **Step 4(p.7–8):** 접근법 top-down/bottom-up/combination, 어느 것이 더 낫다고 하지 않음; 클래스는 "terms that describe objects having independent existence rather than terms that describe these objects"; 계층은 is-a. **4.4(p.16)** 새 클래스 도입 시점, **4.5(p.17)** 새 클래스 vs 속성값 — "The answer usually lies in the scope that we defined for the ontology"; **4.7(p.19)** "The ontology should not contain all the possible information about the domain".
- **Step 5(p.8–9):** 속성 종류: intrinsic, extrinsic, parts, relationships to other individuals. "The classes alone will not provide enough information to answer the competency questions from Step 1." 속성은 그것을 가질 수 있는 가장 일반적인 클래스에 붙인다.
- **Step 6(p.9–11):** facet = value type, allowed values, cardinality; value type(String, Number, Boolean, Enumerated, Instance); domain/range 규칙("find the most general classes ...", "do not define a domain and range that is overly general").
- **Step 7(p.11):** (1) 클래스 선택 (2) 인스턴스 생성 (3) 슬롯 값 채움.
- **문헌이 하지 않은 것:** Noy는 댐 운영 도메인을 다루지 않는다. "대표 운영 상황/대표 사용자 질문"이라는 단계는 없다. 전문가 검토의 절차·인원은 규정하지 않는다(p.4에서 전문가와의 논의를 평가 수단으로 언급할 뿐). 1-E(초안과 용어 비교), 1-I(CQ 기반 검증 단계)에 해당하는 독립 단계는 없다.

### 2-2. Li et al. (2025) — 4단계+사례 구조
- **Stage 1 (p.9–10):** 전문가가 초기 온톨로지(seed) 정의 — 프로그램 요구사항 검토와 이해관계자 인터뷰 기반, 최상위 클래스 6개("six key narrative pillars")와 하위 클래스, **속성은 아직 없음**. 서술: "human expertise delineates the conceptual boundary of the domain, and LLMs subsequently elaborate on that boundary".
- **Stage 2 (p.10–11):** GPT-4o가 CQ를 생성하고 사람이 수동 검토해 40개만 유지; CQ를 70%(확장용)/30%(평가용)로 분할; 확장 후보는 (1) 임베딩 코사인 유사도 필터(임계 0.7) (2) 사람의 간단한 검토(개념 granularity 통합) 후, LLM이 위치·관계를 제안하고 "final review by a human expert to ensure logical consistency and appropriate domain-range assignments".
- **Stage 3 (p.11–12):** FEMA·DHS 등 권위 문서와 뉴스로 스키마 보강; 4단계(중복 제거 → LLM 배치 → 삽입 → "human expert review and approval"); 후보의 약 8%(개체)·10%(관계) 기각, 기각 유형 = hallucination/logical error, ambiguity, semantic drift(Table 3).
- **Stage 4–5 (p.12–16):** 뉴스로 인스턴스 채움(Neo4j), 사례 연구.
- **인스턴스 관계 원칙(p.13):** "the existence of a valid ontological relationship between two classes does not entail that such a relationship holds between all corresponding entities of those classes. A relationship is created in the knowledge graph only when there is sufficient contextual evidence" — STEP 2 규칙과 직접 관련.
- **평가(p.16–19):** OntoQA 지표(RR, IR) + 30% CQ로 개념 커버리지(임베딩 거리) 평가.
- **범위 주의:** 도메인은 홍수 위험 소통(댐 운영 아님). CQ는 **LLM 생성 후 사람 필터**이며 우리 CQ(연구 목적에서 도출)와 출처가 다르다. Noy는 참고문헌 10번으로만 인용되고 Noy의 단계를 적용했다는 서술은 확인되지 않았다.

### 2-3. OntoDSMS (Zhou et al.)
- **Noy 적용(p.3–5):** Fig. 1 "Top-down modeling process using the Noy & McGuiness approach"; "The Noy & McGuiness approach ... is considered to be relatively mature"; 3.1 Step 1 domain/scope, 3.2 Step 2 reuse(SSN/SOSA를 확장·수정), 3.3 Step 3 terms, 3.4 Step 4 classes(top-down 선택) 순으로 서술. **댐 도메인에서 Noy 절차를 적용한 실제 사례(문헌 직접 근거).**
- **RDB↔온톨로지 매핑(p.6–7):** D2RQ 플랫폼으로 관계형 DB를 가상 RDF 그래프로 접근(데이터를 RDF 저장소로 복제하지 않음), SPARQL 질의를 SQL로 변환. 매핑 원칙: 테이블→클래스, 컬럼→DatatypeProperty, 행→인스턴스, 셀 값→Literal; 자동 생성된 매핑 파일을 온톨로지 용어와 맞도록 수정.
- **평가(p.11):** 동일 데이터(엔티티 492,875개)에서 SQL과 온톨로지 질의를 비교해 검색 시간 보고(초록: "reducing retrieval time effectively compared with traditional databases").
- **범위 주의:** BIM 기반 댐 안전 모니터링(센서·구조 데이터)이며 방류 승인·운영기준·문서는 다루지 않음. CWA/OWA(닫힌/열린 세계 가정) 논의 있음(p.3).

### 2-4. DDKG (Huang et al.)
- **온톨로지 구축(p.3):** "a seven-step methodology": (1) 도메인·과제 정의 (2) 기존 온톨로지 재사용 검토 (3) 용어 나열 (4) 클래스·계층 (5) 속성·관계 (6) 제약 (7) 인스턴스 — **Noy의 일곱 단계와 구조가 같으나 원문에 Noy 인용은 없다**(본문 검색 결과 없음). OWL/Protégé 사용.
- **구조(p.4):** 최상위 클래스 7개 — Dam, Properties, Location, Parameter, HazardForm, HazardComponent, SafetyEvaluation. **"All top-level classes are connected to the Dam entity to anchor all related information to specific engineering instances."**
- **추출(p.7–9):** 대상은 위험(hazard) 서술 텍스트의 **분류**(HazardForm/HazardComponent 라벨). OHCF = 미세조정(LoRA), temperature-perturbed voting, ontology-constraint consistency checking(충돌 라벨쌍 집합), expert validation. 전문가는 "False" 표시 샘플을 검토해 기존 노드에 연결하거나 새 노드를 온톨로지에 추가(p.8 d). 학습 데이터는 DeepSeek-V3가 예비 라벨 → 전문가 검증 → 증강(p.9).
- **KG(p.8, 11):** Neo4j 저장, 201,362 노드·953,447 관계, 원천은 중국 22,076개 결함·위험 댐의 안전평가 보고서.
- **범위 주의:** 핵심 과제는 hazard 분류이며 일반적인 관계 추출이 아니다(관계 추출이라는 용어는 참고문헌에서만 확인). 우리 자료(승인 CSV, 규정 조문)는 성격이 다르다.

### 2-5. GraphAide (Purohit et al.)
- **구조(p.2–4):** KG 생성 단계와 질의 단계. 나열된 기능: 벡터 DB 관리, "Enhanced context generation: Combines vector-based retrieval with graph-based subgraph matching", "External function execution capability: Enriches context by retrieving multi-modal data sources, such as temporal data from time-series databases"(p.2). 질의 확장(p.3), 서브그래프 매칭 템플릿(Cypher 자동 생성 지원, p.3).
- **평가 원칙(p.3):** 여러 구성요소(agent)가 있는 응용은 "a single metric is often insufficient", 각 agent별 지표가 필요; RAGAS 사용.
- **실제 실험(p.4–7):** GPT-4o, Chroma, Neo4j, LangChain; **뉴스 기사 1,846건으로 우크라이나–러시아 분쟁 KG 생성**, 각 단계 응답에 대한 정성 평가와 노드 타입 할당에 RAGAS 지표(p.5–6). 결론(p.7): "Future work will focus on formal evaluation to report quantitative improvements".
- **범위 주의(handoff와 다름):** **외부 시계열 조회는 기능으로 나열되었으나 보고된 실험에서 시연·평가되지 않았다.** "KG + Text + Measurement" 구조를 제시한 논문이 아니다. 본 PDF에는 "Authorized licensed use limited to: Kookmin University ... IEEE Xplore" 문구가 있다(재배포 주의).

## 3. handoff와 원문이 달랐던 사항
| # | handoff 서술 | 원문 확인 | 처리 |
|---|---|---|---|
| D1 | GraphAide: "External time-series → Measurement Retrieval"의 근거, component별 evaluation | 시계열 외부 함수는 **기능 목록**(p.2)이고 **실험에서 미시연**; 컴포넌트별 지표 필요 원칙은 p.3에서 확인; 정량 평가는 미래 과제 | 시계열 부분은 A가 아니라 **B(본 연구 적용)** 로 표기 |
| D2 | DDKG: "Entity/Relation extraction + ontology validation + expert review" | 실제 과제는 **hazard 분류**, 제약 검사·전문가 검증 확인; 관계 추출은 본문에서 확인되지 않음 | "관계 추출"은 문헌 직접 근거에서 제외 |
| D3 | Li et al.: "expert-defined initial ontology/domain boundary, CQ-driven expansion, authoritative documents, automated filtering + human review, domain-range expert validation" | 모두 확인. 단 **CQ는 LLM 생성+사람 필터**, 자동 필터는 임베딩 유사도(임계 0.7), 사람 검토는 소수 | 자동 필터·LLM 생성은 **채택하지 않음(D. NOT-ADOPTED)** |
| D4 | OntoDSMS: "RDB ↔ ontology mapping, dynamic monitoring + static information" | 확인(D2RQ, 테이블→클래스 원칙). **추가:** OntoDSMS 자체가 Noy 절차를 댐 도메인에 적용(직접 근거) | 실제 구현(D2RQ)은 채택하지 않음 |
| D5 | Noy: (handoff 요약) | 확인. **추가:** 문헌은 "from scratch" 가정; 4.5/4.7의 class vs property, scope 한정 원칙 | v0.1 출발은 **B** |
| D6 | LSMKG/Zhang 2025 | **원문 없음** | LITERATURE_CHECK_REQUIRED |

Hard Stop 조건 1("선정한 핵심 원 논문이 handoff의 핵심 방법론 주장을 실제로 지원하지 않는 경우")에는 **해당하지 않는다**: 확인된 논문은 모두 핵심 방법론 주장을 지지하며 차이는 범위·시연 여부에 관한 것이다. LSMKG는 지지 여부를 알 수 없는 **미확인** 상태다.

## 4. STEP 1 하위 단계의 방법 근거 분류
| 하위 단계 | A 문헌 직접 | B 본 연구 적용 | C 검토 필요 |
|---|---|---|---|
| 1-A Domain/Scope | Noy Step 1 네 질문(p.5) | 댐 운영 domain, 한강수계 pilot, 사용자 구분 | 유지·검토 주체 |
| 1-B CQ 검토 | CQ는 scope 도구·litmus test·non-exhaustive(p.5); Step 5에서 CQ에 답할 정보 필요(p.8) | 연구 목적 기준의 CQ 적절성 평가 항목(중복·혼합·구현 전제·availability 분리) | CQ 수정 여부 |
| 1-C 재사용 검토 | Noy Step 2(p.5–6); OntoDSMS의 SSN/SOSA 재사용(p.4) | 후보 평가 기준(범위·CQ 관련성·재사용 정도) | 표준 어휘 원문 미열람(W3C·OGC 차단) |
| 1-D 용어 나열 | Noy Step 3(p.6) | 출처(목적·CQ·규정·자료)별 인벤토리 | — |
| 1-E/F 설계 검토 | Noy Step 4–5(p.7–9, 4.4·4.5·4.7) | v0.1 요소별 검토 기준(독립 의미·CQ·자료·문헌) | 수정안 채택 |
| 1-G 제약 | Noy Step 6(p.9–11) | 시간·의미 제약 후보 | source 의미 불명 항목 |
| 1-H 대표 인스턴스 | Noy Step 7(p.11) | 실제 사례로 표현 가능성 확인(STEP 2와 구분) | — |
| 1-I CQ 검증 | CQ를 litmus test로 사용(p.5) | 문제 원인 5분류 | — |
| 1-J 전문가 검토 | Noy p.4(전문가와 논의), Li Stage 2–3(전문가 최종 검토 p.10–12), DDKG stage d(p.8) | 검토 대상 목록화 | 검토자 지정, 절차 |
