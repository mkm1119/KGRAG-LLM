# M. STEP 1-A — Domain and Scope

- 작성일: 2026-09-30 (STEP 1-A만 수행; STEP 1-B 이후는 사용자 확인 전 진행하지 않음)
- 기준: `01_AI_RESEARCH_HANDOFF.md`(canonical) + 이번 STEP 1 실행 지침. 현재 Ontology는 **Initial Ontology v0.1**로 취급하며 **수정하지 않았다**(Class/Relation/Data Property/CQ 모두 그대로).
- 이 문서의 진술은 근거 수준을 **A(문헌 직접 근거) / B(본 연구 적용 결정) / C(추가 검토 필요)** 로 표시한다. 상태는 `STEP1_DECISION_LOG.md`의 코드(RESOLVED / REVIEW_REQUIRED / LITERATURE_CHECK_REQUIRED / DATA_REQUIRED / EXPERT_REVIEW_REQUIRED / DEFERRED)를 쓴다.
- **문헌 원문 접근 상태 (v2 개정):** Noy & McGuinness 원문은 사용자가 공유한 PDF(`references/evidence_literature/Noy.pdf`, 25쪽)에서 **이번에 직접 대조했다.** 쪽 번호는 PDF 쪽과 인쇄 쪽이 일치한다. PDF에 발행 연도·보고서 번호는 표시되어 있지 않아 "2001"은 handoff의 서지 표기를 따른다. **Li et al.(2025) `36_FloodOntology.pdf`는 이 환경의 추출 도구로 읽지 못해 원문 대조를 하지 못했다**(이 문서에서는 handoff §4.1 기재 수준으로만 인용) → `S1A-01`은 Li et al.에 한해 LITERATURE_CHECK_REQUIRED로 유지. (v1은 원문 없이 작성되었고 그 차이는 §10 개정 이력에 기록)

---

## 1. 이 단계의 방법론 근거

| 항목 | 내용 | 근거 수준 |
|---|---|---|
| Noy & McGuinness, *Ontology Development 101: A Guide to Creating Your First Ontology* — **Step 1. "Determine the domain and scope of the ontology"** (PDF p.5, 3절 "A Simple Knowledge-Engineering Methodology" 안의 첫 단계) | 저자들은 "defining its domain and scope"로 온톨로지 개발을 시작하라고 제안하고, 네 가지 기본 질문에 답하라고 한다: 온톨로지가 다룰 **domain**은 무엇인가 / 무엇에 **사용**할 것인가 / 온톨로지 정보가 어떤 **종류의 질문**에 답해야 하는가 / **누가 사용하고 유지**하는가. 이 답은 설계 과정에서 바뀔 수 있으나, 매 시점의 모델 **범위를 한정**한다고 한다. 예시(와인·음식)에서 domain을 정하고, 무엇을 포함하지 않을지도 서술한다(포도주 저장고 재고관리·식당 직원 관리 개념은 관련되어 있어도 포함될 가능성이 낮다고 예시). 사용 목적이 포함할 정보(예: 소매가격, 도매가격)를 좌우한다는 예도 든다. 인용은 부록 §9. | **A (원문 대조 완료)** |
| Noy & McGuinness — **Competency questions** (PDF p.5, Step 1 안) | "One of the ways to determine the scope of the ontology is to sketch a list of questions that a knowledge base based on the ontology should be able to answer, competency questions (Gruninger and Fox 1995)." 이 질문들은 이후 온톨로지가 충분한 정보를 담는지 판단하는 **"litmus test"** 로 쓰이며, 스케치일 뿐 **exhaustive할 필요는 없다.** → 문헌에서 CQ는 **Step 1(scope 결정) 안에서 제시**되고, 이후 검증 기준으로도 쓰인다. 이번 지침은 CQ를 1-B로 분리했다(§6). | **A (원문 대조 완료)** |
| Noy & McGuinness — 방법론의 전제 (PDF p.4, 3절 도입부) | "there is no one 'correct' way or methodology for developing ontologies"; 개발 규칙 1) "There is no one correct way to model a domain", 2) "Ontology development is necessarily an iterative process"; 초기 온톨로지는 "applications or problem-solving methods or by discussing it with experts in the field, or both"로 평가·디버깅하고 거의 확실히 수정하게 된다. → 초안(v0.1)을 정답으로 가정하지 않고 반복적으로 검토하는 이번 STEP 1의 태도와 부합. **문헌은 이 절차가 "v0.1처럼 이미 있는 초안에서 출발"하는 경우를 다루지는 않는다**: 가이드는 "assume that no relevant ontologies already exist and start developing the ontology from scratch"(p.6)고 가정한다 → v0.1 출발은 **B(본 연구 적용)**. | **A (전제) / B (v0.1 출발 적용)** |
| Li et al. (2025), Water 17, 2801 | handoff §4.1 기준: expert가 정의한 초기 ontology/domain boundary, CQ 기반 확장, authoritative documents 활용, 자동 필터링 + human review, hierarchy/relation/domain-range에 대한 expert validation. **Noy를 대체하는 주 근거가 아니라 expert review 보강 근거.** STEP 1-A에서는 "domain boundary를 전문가 검토 대상으로 둔다"는 원리만 사용 | A (handoff 기재; 원문 미열람) |
| 본 연구의 Domain/Scope **내용**(댐 운영 의사결정 지원, 한강수계 pilot, 포함·제외 항목) | 문헌이 제시한 것이 아니라 연구 목적과 실제 자료에서 도출한 **본 연구 적용 결정** | **B** |
| 유지 주체, 전문가 검토 주체, 최종 사용자의 세부 | canonical이 명시하지 않은 부분 | **C** |

## 2. 사용한 입력
- `01_AI_RESEARCH_HANDOFF.md` §1(연구 목적·비목표), §3(개념), §4(STEP 1), §5(Ontology), §6.3(Measurement 결정), §12(Pilot 범위), §13, §17
- `STEP0_summary.md`, `04_reports/I_Ontology_Compatibility_Report.md`, `J_Approval_Gap_Filling_Report.md`, `K_Approval_Measurement_Linkage_Pilot.md`, `L_DATA_REVIEW.md`
- 실제 규정 원문: 「댐과 보 등의 연계운영규정」 (기후에너지환경부 훈령 제42호, 시행 2026-07-08) 제1·2·6·14조 (`01_raw/Law/admrul_2100000282102_…xml`)
- STEP 0 실제 자료(Dam, ObservationStation, MeasurementDataset, Criterion, Document, Approval, 상·하류 evidence)의 존재 여부와 규모

---

## 3. Domain and Scope 정리 (Noy Step 1 질문에 대응)

> 아래는 **초안(proposed)** 이다. 사용자 확인 전에는 확정하지 않는다(상태 REVIEW_REQUIRED 포함).

### Q1. Ontology가 다룰 domain은 무엇인가?
**제안:** *댐 운영 의사결정 지원을 위한 근거 지식의 domain* — 곧, 댐의 수문·기상 상태를 나타내는 관측·측정자료, 댐에서 이루어진 운영행위, 그와 관련된 방류 승인, 운영기준(규정상 기준), 그리고 이들을 뒷받침하는 문서와 출처 사이의 의미 구조. (근거 수준 **B**; 연구 목적 문장과 handoff §1.1·§3에서 도출)

- **domain(개념 영역)과 pilot 자료 범위를 구분한다.** domain은 위와 같고, 실제 자료로 검토하는 pilot 범위는 **한강수계 여러 댐**(handoff §12)이다. STEP 0에서 확보한 자료는 K-water 11개 시설, KHNP 한강 수력발전댐 7개(이름만), 승인 record(2010-07-16~2021-07-16), 측정자료(2021-01~2026-09, 일부 2019·2020 구간), 연계운영규정 등이다. (→ `S1A-03`)
- 용어 해석: `Dam`은 자료에서 다목적댐·용수댐·수력발전댐·홍수조절용댐·조정지·보가 같은 체계로 나열되어 있어 "댐"의 경계(보·조정지 포함 여부)는 아직 정하지 않았다. STEP 1-D/1-F에서 다룬다(`S1A-03`).

### Q2. Ontology를 사용하는 목적은 무엇인가?
**canonical 목적(변경 없음, A=handoff):** "현재 댐의 기상·수문 상태를 파악하고, 이와 관련된 과거 운영행위와 당시의 승인·운영기준·근거자료를 연결하여 운영자의 판단을 지원한다."

**Ontology의 역할(경계만 명시; B):**
1. 위 목적에 필요한 대상(개체 종류)과 그 사이의 관계·속성·제약을 **명시적 의미 구조**로 정의한다.
2. 이후 STEP 2에서 서로 다른 출처(정형자료, 문서, 측정자료)를 공통 구조로 mapping/extraction할 때의 기준이 된다.
3. 이후 STEP 3에서 질문을 이해하고 근거를 찾는 데 쓰일 **의미 구조**를 제공한다(구현은 이 단계에서 다루지 않음).
- 이 연구는 **decision support**이며 최종 운영 판단은 운영자에게 있다(handoff §1.2 A). 자동 방류 결정 시스템으로 확대하지 않는다.

### Q3. 어떤 종류의 질문에 답하기 위한 Ontology인가?
현재 CQ1~CQ6(참고용; **적절성 검증은 STEP 1-B**에서 수행, 이번에 수정하지 않음):
| 유형 | CQ |
|---|---|
| 관측자료 연결 (어떤 관측·측정자료가 연결되어 있는가) | CQ1, CQ6 |
| 과거 운영행위 (무엇이 이루어졌는가) | CQ2 |
| 승인 (관련 방류 승인은 무엇인가) | CQ3 |
| 운영기준 (관련 운영기준은 무엇인가) | CQ4 |
| 근거 문서 (어느 문서에서 확인되는가) | CQ5 |

- 이 Ontology가 **답하는 것은 "어떤 종류의 정보가 어떻게 연결되는가"의 구조**이고, 구체적 값(수위, 방류량 등)은 자료에서 조회된다.
- 답하지 않는 질문 유형(handoff 기준): 현재와 **유사한 과거 운영상황**은 Ontology CQ에 포함하지 않고 STEP 3 retrieval 설계 문제로 둔다(handoff §4.3 A). "지금 무엇을 해야 하는가/얼마를 방류해야 하는가"는 범위 밖(§3-Q7).

### Q4. 주요 사용자는 누구인가?
- **시스템의 최종 사용자(decision-maker):** 댐 운영자 — handoff가 "Human operator의 판단을 위한 근거 검색·연결·설명 시스템"이라고 명시(A=handoff). 구체적으로 어떤 기관·직무의 운영자인지는 canonical에 없음 → **C**.
- **Ontology를 직접 소비하는 주체(B, 본 연구의 해석):** (i) STEP 2에서 자료를 mapping하는 연구자, (ii) STEP 3에서 질문·근거 검색을 수행할 구성요소(구현 미정). Noy는 Step 1에서 "Who will use and maintain the ontology?"를 묻고, 온톨로지를 **유지하는 사람들**과 **사용하는 사람들**이 서로 다른 언어로 domain을 서술할 수 있다는 예(그 경우 언어 간 매핑 제공)까지 든다(A, PDF p.5). 그러나 사용자를 **최종 사용자(운영자)와 Ontology 직접 소비 주체로 나누어 읽는 것은 문헌에 없는 본 연구의 적용(B)** 이다. (→ `S1A-04`)

### Q5. 누가 Ontology를 유지·검토할 것으로 가정하는가?
- canonical은 유지 주체를 명시하지 않는다. **임의로 가정하지 않는다.** Noy는 유지 주체를 Step 1에서 답해야 할 질문으로 두지만 누구여야 하는지는 정하지 않는다(A, p.5).
- 확정된 것은 "expert review / human validation을 각 STEP의 Validation에 포함하며 LLM 제안을 자동 수용하지 않는다"는 원칙뿐이다(handoff §2, §3·§4.1의 Li et al. 보강 근거; A=handoff).
- **미정:** 설계·유지 책임자(현재는 연구자로 보이나 확정 아님), 검토에 참여할 도메인 전문가(댐 운영/수문 분야)가 누구인지 → `S1A-04` **EXPERT_REVIEW_REQUIRED** (사용자 확인 필요).

### Q6. 연구 범위에 명시적으로 포함되는 것 (초안)
| 포함 | 근거 (실제 자료 / 규정) | 근거 수준 |
|---|---|---|
| 댐(대상 시설)과 그 식별 | 11+7개 시설 (`dam_catalog.csv`) | B |
| 댐의 수문·기상 **관측소와 측정 dataset** 및 그 출처 | 94개 관측소, 71개 dataset 목록; 측정자료는 **dataset 단위 연결**까지가 Ontology 범위 후보(시계열 전체를 node로 저장할지는 미결정, handoff §6.3) | B / 저장 방식 C |
| **과거 운영행위**(Operation) — 개념은 포함 | 연구 목적 문장("과거 운영행위"); 규정 제14조 등 규범 근거. **실제 instance는 미확보** | B, 자료는 DATA_REQUIRED |
| **방류 승인**(Approval) | 승인 record 3,929건(`approval_records_hrfco_raw_fields.csv`). 규정 제6조②: "홍수조절을 위한 수문조작이 필요한 경우에는 홍수통제소장의 사전 승인을 받아야 한다" | B |
| **운영기준**(Criterion) | 연계운영규정 [별표3] 홍수기 제한수위 9개 댐 + 조문 15건(`criterion_list.csv`) | B |
| **근거 문서**(Document)와 기준·승인·운영의 출처 링크 | 문서 45건(`document_list.csv`) | B |
| 자료 출처 추적(provenance)을 **기존 source link(recordedIn/documentedBy/definedIn 등)로 표현할 수 있는지** 검토 | handoff §9: Provenance는 별도 top-level 개념으로 추가하지 않음 | A(handoff) |
| **시간 차원**: "과거 운영행위와 **당시의** 승인·운영기준·근거자료" | 연구 목적 문장이 시점 대응을 요구함. 그러나 확보한 Criterion은 현행(2026-07-08 시행) 버전이며 2019~2020 승인에 **적용됐는지 검증 불가** | B 목적 / 자료 DATA_REQUIRED (`S1A-07`) |

### Q7. 연구 범위에 명시적으로 포함되지 않는 것
**(a) canonical에 명시된 제외 (A=handoff §1.2, §4.3, §18).** 제외 범위를 명시하는 것 자체는 Noy Step 1의 방식이다(예: 와인·음식 온톨로지가 "managing inventory in a winery or employees in a restaurant" 개념은 포함하지 않을 가능성이 높다고 예시, p.5).
- 자동 수문 개방 결정, 자동 방류량 산정·명령
- 출처에 없는 조치 사유·인과관계를 LLM이 추정하는 것(Rationale 자동 생성 포함)
- "AI가 댐을 운영한다"는 시스템
- "현재와 유사한 과거 운영상황" 자체를 Ontology CQ로 다루는 것(STEP 3 문제)
- Urban Flood conceptual reference를 과학적 근거로 인용하는 것; 구현 기술 선결정(Neo4j/Cypher 등)

**(b) 이번 단계에서 제안하는 제외 (B — 사용자 확인 필요, `S1A-05`):**
- 홍수 예측·유입량 예측 등 **예측 모형**
- 댐 안전관리·점검(예: 저수지·댐 안전관리법 체계), 수질, 용수공급, 발전 운영 **자체**의 모델링 (다만 측정자료에 포함된 변수나 규정 문서는 자료로 다룰 수 있음)
- 하천·수계 전반의 수문 모델, 홍수예보 체계 자체
- 한강수계 **외** 수계 (pilot 범위 밖; domain 일반화는 주장하지 않음)

**(c) 경계가 아직 정해지지 않은 것 (DEFERRED/REVIEW_REQUIRED):**
- **상·하류 관계:** STEP 0에서 실제 공식 서술 evidence는 있으나 CQ1~CQ6 어디에도 상·하류 질문은 없고 v0.1에 Relation도 없다. handoff §12는 "실제 자료에서 반복 필요성 확인 → 관련 Ontology/KG 문헌 검토 후 도입 여부 결정"을 요구한다. → 범위 포함 여부 **미결정** (`S1A-06`).
- **행위자**(홍수통제소, 시설관리자, 관계기관, 운영기관 K-water/KHNP): 규정 제2조와 자료에 등장하나 v0.1에 대응 개념이 없다. **결정하지 않고** STEP 1-D 용어 도출로 넘긴다 (`S1A-10`).

### Q8. Knowledge Graph / Hybrid Retrieval / LLM과의 관계 (역할·경계만)
| 구성 | 관계 | 이 단계에서 하지 않는 것 |
|---|---|---|
| Ontology (STEP 1) | 무엇을 어떤 관계·속성·제약으로 표현할지 정의하는 **의미 구조** | — |
| Knowledge Graph (STEP 2) | Ontology 위에 **실제 entity/relation/property value를 채운 결과** | 구축·저장 기술 선택 |
| Hybrid Retrieval (STEP 3) | 질문에 필요한 KG·Text·Measurement 근거를 찾음 | 설계·구현 |
| LLM (STEP 3) | 검색된 근거를 통합해 설명; 출처 밖 사실을 추가하지 않음 | 구현 |
- 측정 시계열 전체를 KG에 넣을지는 미결정(handoff §6.3). Ontology는 Dam–Station–Dataset 수준의 **의미 연결**을 다루는 것으로 경계를 둔다(B; `S1A-11`).
- KG가 필요하다는 전제는 증명 대상이며 이 단계에서 결론내리지 않는다(handoff §10).

---

## 4. 세 축 점검 (목적·CQ / 문헌·규정 / 실제 자료)

| Scope 요소 | ① 목적·CQ | ② 문헌·규정 | ③ 실제 자료(STEP 0) | 판단 |
|---|---|---|---|---|
| 측정자료·관측소 | CQ1, CQ6 | (문헌 조사는 STEP 1-C) | 있음(관측소 94, dataset 71); 관측소 단위 시계열은 없음 | scope 포함 |
| 운영행위 | CQ2 | 규정 제14조 등 | **instance 없음** | scope 포함(개념), 자료 미확보 |
| 승인 | CQ3 | 제6조② | **3,929건** | scope 포함 |
| 운영기준 | CQ4 | 제6조, 별표3 | 15건(현행 버전만) | scope 포함, 시점 적용성 미검증 |
| 문서 | CQ5 | — | 45건 | scope 포함 |
| 상·하류 | (없음) | (문헌 미조사) | 공식 서술 11건 | **미결정** |
| 행위자 | (없음) | 제2조 정의 | 승인 파일·규정에 등장 | **미결정(1-D로 이월)** |

규정 원문(`01_raw/Law/admrul_2100000282102_…xml`, 원문 그대로):
- 제1조(목적): "…댐, 보 등의 하천시설 … 연계운영을 통하여 갈수 및 홍수로 인한 재해의 방지와 물환경의 적정한 관리 및 수자원의 효율적인 운용을 위하여 필요한 사항을 규정함을 목적으로 한다."
- 제6조②: "시설관리자는 각 시설의 홍수기 제한수위를 준수하여야 하고, 홍수조절을 위한 수문조작이 필요한 경우에는 홍수통제소장의 사전 승인을 받아야 한다."
- 제14조①: "시설관리자는 … 방류량을 조정할 필요가 있는 경우에 방류량을 조정하고 그 결과를 관할 홍수통제소장에게 지체없이 통보하여야 한다."
※ 이 조문들은 **domain 경계의 규범적 근거**로만 사용한다. 이 조문을 근거로 Approval과 Operation을 동일시하거나 특정 record 사이의 관계를 추정하지 않는다.

## 5. 이번 단계에서 발견한 문제 (유형 구분)

| 유형 | 내용 | 로그 ID |
|---|---|---|
| D 문헌/방법론 | 원문 접근 불가로 Step 1 절차를 원문 대조하지 못함 | S1A-01 |
| B 데이터/매핑 | Criterion 시점 적용성(현행 2026 버전 vs 2019~2020 승인); 시설 식별(코드/이름 불일치) | S1A-07, S0-D |
| C 자료 가용성 | Operation instance 없음 | S1A-09 |
| E 전문가 검토 | 유지 주체·전문가, 최종 사용자 특정, 제외 범위 | S1A-04, S1A-05 |
| A 온톨로지(가능성, 미확정) | 상·하류, 행위자 개념이 v0.1에 없음 → 1-D/1-F로 이월 | S1A-06, S1A-10 |

## 6. canonical 문서와의 충돌 점검
- **범위·비목표·CQ·Ontology 요소·Relation 이름·금지사항:** 이번 지침과 canonical이 **일치**한다(충돌 없음). `relatedCriterion`은 중립 의미 유지, Operation/Approval 분리, upstream/downstream 자동 추가 금지 모두 동일.
- **차이 2건(충돌 아님, 비차단; 사용자 확인 요청 — `S1A-12`):**
  1. handoff §4.2의 STEP 1 흐름에는 "대표 운영 상황 정의 → 대표 사용자 질문 정의"가 있으나, 이번 지침의 1-A~1-J에는 해당 단계가 별도로 없다. handoff §4.1은 이 표현이 Noy의 공식 단계명이 아니라 본 연구의 적용 방식이라고 밝히며, **Noy 원문에서도 이 이름의 단계는 확인되지 않는다**(Step 1 안에는 CQ 스케치가 있음, p.5). 1-B에서 CQ와 함께 다룰지 확인 필요.
  2. 이번 지침의 1-C(기존 Ontology 재사용 검토)는 handoff §4.2의 흐름에 없으나, **Noy의 Step 2 "Consider reusing existing ontologies"(PDF p.5–6)에 직접 대응**하므로 문헌 근거(A)가 있는 추가이며 handoff와 모순되지 않는다. 또한 문헌에서는 CQ 작성이 Step 1 안에 포함되는데 이번 지침은 1-B로 분리했다 — canonical도 CQ를 별도 단계로 둔다.
- **Noy 단계와 이번 지침의 대응(정보 제공용; 이번 단계에서 수행하는 것은 1-A뿐):** Noy Step 1 ↔ 1-A(+CQ는 1-B); Step 2 ↔ 1-C; Step 3 "Enumerate important terms" ↔ 1-D; Step 4–5 (classes/hierarchy, properties) ↔ 1-F; Step 6 (facets) ↔ 1-G; Step 7 (instances) ↔ 1-H. **1-E(v0.1과 용어 비교), 1-I(CQ 기반 검증; Noy는 CQ를 litmus test로 언급), 1-J(expert review; Noy p.4는 전문가와의 논의를 평가 방법으로 언급, 보강 근거는 Li et al.)는 Noy의 번호 단계가 아니며 본 연구의 구성(B)**이다. (대응은 Noy PDF의 단계 제목 확인 범위 내; Step 3~7 세부는 각 단계에서 다시 대조한다.)

## 7. 이전 산출물 정정 주석 (S1A-08)
STEP 0 마지막 보완(K 보고서, L 요약, `linkage_pilot_cases.csv`)에서 **2019~2020년 승인에 현행(2026-07-08 시행) Criterion·Document를 "연결"**했다고 기술했다. 이 연결은 **시설명 대응(같은 댐의 현행 기준값 대조)** 일 뿐이며 해당 기준이 당시(2019~2020)에 적용되었는지는 검증되지 않았다(지침 §11-A). K·L 문서와 그래프 라벨에 정정 주석을 덧붙였다(기존 기록은 삭제하지 않음). 시점 적용성 자체는 `S1A-07` DATA_REQUIRED로 남는다.

---

## 8. [STEP 1-A 수행 결과] (Method Evidence Check)

1. **목적:** Noy & McGuinness의 첫 단계(domain·scope 결정)에 따라 본 연구 Ontology의 domain, 목적, 질문 유형, 사용자·유지 주체, 포함/제외 범위, KG·Retrieval·LLM과의 경계를 명시한다.
2. **문헌 근거:** Noy & McGuinness — 3절 "A Simple Knowledge-Engineering Methodology"(p.4)와 그 안의 **Step 1. Determine the domain and scope of the ontology**(p.5, 네 기본 질문·competency questions) — **원문 대조 완료**; Li et al. (2025) — expert-defined boundary·expert validation [handoff 기재 기준; **원문 미대조**].
3. **본 연구가 가져오는 요소:** 네 기본 질문(domain / 용도 / 질문 유형 / 사용·유지 주체)으로 scope를 먼저 명시하는 절차; 답이 개발 중 바뀔 수 있다는 전제; CQ를 scope 결정 도구(및 이후 litmus test)로 쓰는 원리; 포함하지 않는 대상을 명시하는 방식; 초안을 반복적으로 평가·수정한다는 태도; domain boundary를 expert review 대상으로 두는 원리(Li et al., handoff 기준).
4. **문헌이 직접 지원하지 않는 본 연구 적용:** 댐 운영 의사결정 지원이라는 domain 내용, 한강수계 pilot 범위, 포함/제외 항목, **이미 존재하는 Initial Ontology v0.1에서 출발**하는 것(Noy는 "from scratch"를 가정), 사용자를 "최종 사용자/직접 소비 주체"로 나눈 해석, 상·하류·행위자 경계 처리.
5. **수행한 작업:** canonical·STEP 0 보고서·규정 원문 재독; Noy 기본 질문별 정리; 세 축(목적·CQ / 규정 / 실제 자료) 점검; 충돌 점검; 이전 산출물 정정.
6. **사용한 실제 자료:** STEP 0 자료의 존재 여부·규모(승인 3,929건 등), 연계운영규정 제1·2·6·14조·별표1·3. (Ontology 수정에는 사용하지 않음)
7. **결과:** §3의 Domain/Scope 초안(Q1~Q8). 상·하류·행위자는 경계 미결정으로 유지.
8. **REVIEW_REQUIRED 항목:** `STEP1_DECISION_LOG.md`의 S1A-01(Li et al.에 한해) ~ S1A-12 및 이월 S0-B~S0-F.
9. **아직 결정하면 안 되는 사항:** Class/Relation 추가·수정, CQ 수정, `접수방류량`=`approvedReleaseAmount`, 2020 승인↔2026 기준 연결, 시설 코드 통합, 시각 규약, 상·하류 Relation, Operation 추론.
10. **사용자 확인이 필요한 사항:** Domain 문구(§3 Q1), 유지 주체·전문가 지정(Q5), 제안 제외 범위(Q7-b), 상·하류·행위자의 scope 포함 여부, handoff 흐름과의 차이 2건(§6), Li et al. `36_FloodOntology.pdf`를 읽을 수 있는 방법(텍스트 추출 도구 또는 텍스트본 제공).

---

## 9. 부록 — Noy & McGuinness 원문 발췌 (Noy.pdf, 쪽 번호는 PDF=인쇄 쪽)
※ 추출 텍스트에서 줄바꿈 때 소실된 공백을 복원해 옮겼다. 짧은 발췌만 수록한다. 서지: PDF p.1 — "Ontology Development 101: A Guide to Creating Your First Ontology", Natalya F. Noy and Deborah L. McGuinness, Stanford University(연도는 PDF에 없음; handoff는 2001).

- **p.4 (3절 도입):** "there is no one 'correct' way or methodology for developing ontologies." / 규칙 "1) There is no one correct way to model a domain — there are always viable alternatives. The best solution almost always depends on the application that you have in mind and the extensions that you anticipate. 2) Ontology development is necessarily an iterative process." / "After we define an initial version of the ontology, we can evaluate and debug it by using it in applications or problem-solving methods or by discussing it with experts in the field, or both. As a result, we will almost certainly need to revise the initial ontology."
- **p.5 (Step 1):** "We suggest starting the development of an ontology by defining its domain and scope. That is, answer several basic questions: What is the domain that the ontology will cover? / For what we are going to use the ontology? / For what types of questions the information in the ontology should provide answers? / Who will use and maintain the ontology? The answers to these questions may change during the ontology-design process, but at any given time they help limit the scope of the model."
- **p.5 (Step 1, 사용 목적·유지 주체의 예):** "If the people who will maintain the ontology describe the domain in a language that is different from the language of the ontology users, we may need to provide the mapping between the languages."
- **p.5 (Step 1, 포함하지 않는 것의 예):** "it is unlikely that the ontology will include concepts for managing inventory in a winery or employees in a restaurant even though these concepts are somewhat related to the notions of wine and food."
- **p.5 (Competency questions):** "One of the ways to determine the scope of the ontology is to sketch a list of questions that a knowledge base based on the ontology should be able to answer, competency questions (Gruninger and Fox 1995). These questions will serve as the litmus test later: Does the ontology contain enough information to answer these types of questions? ... These competency questions are just a sketch and do not need to be exhaustive."
- **p.5–6 (Step 2, 재사용):** "It is almost always worth considering what someone else has done and checking if we can refine and extend existing sources for our particular domain and task." / p.6: "For this guide however we will assume that no relevant ontologies already exist and start developing the ontology from scratch."

## 10. 개정 이력 (삭제 없이 기록)
| 버전 | 날짜 | 내용 |
|---|---|---|
| v1 | 2026-09-30 | Noy 원문 없이(handoff 요약과 기존 지식으로) 작성. Noy 인용은 요약 수준이며 절·쪽 번호 없음 |
| v2 | 2026-09-30 | Noy.pdf로 원문 대조. **바뀐 점:** ① Noy의 기본 질문·CQ 서술·반복성·전문가 논의(평가)를 원문 표현과 쪽 번호로 확정(A). ② v1은 "문헌이 사용자를 구분하지 않았다"고 썼으나, 원문은 **사용자와 유지 주체가 다른 집단일 수 있음**을 명시한다(§Q4 수정; 최종 사용자/직접 소비 주체 구분은 여전히 B). ③ v1의 "재사용 검토는 Noy의 기존 온톨로지 재사용 단계에 해당" 추정을 원문(Step 2, p.5–6)으로 확정(§6). ④ v1에 없던 **"문헌은 from scratch를 가정, 본 연구는 v0.1에서 출발"** 차이를 명시. ⑤ **바뀌지 않은 것:** Domain/Scope 초안 내용(§3 Q1~Q8), 포함/제외 항목, 결정 로그의 REVIEW_REQUIRED 항목 — Domain/Scope 내용은 문헌이 아니라 연구 목적·자료에서 도출한 B이므로 원문 대조로 결론이 바뀌지 않았다. Li et al.은 미대조. |
