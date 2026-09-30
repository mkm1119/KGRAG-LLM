# N. STEP 1-B — Competency Questions Review

- 작성일: 2026-09-30. 기준: `01_AI_RESEARCH_HANDOFF.md`, `M_STEP1A_DOMAIN_SCOPE.md`(provisional baseline), 현재 CQ1~CQ6(수정하지 않음).
- 표: `03_normalized/step1_cq_review_matrix.csv`. 결정 로그: `STEP1_DECISION_LOG.md`(S1B-xx).
- **이 단계의 판정은 "현재 Ontology가 CQ에 답할 수 있는가"가 아니다.** 그것은 STEP 1-I에서 평가한다. 여기서는 CQ **자체가** 연구 목적과 Domain/Scope를 적절히 반영하는지만 본다. 자료가 없다는 이유로 CQ를 제거하지 않았다.

## 0. 방법론적 위치

```
Noy 공식 Step 1. Determine the domain and scope of the ontology (PDF p.5)
├─ 본 연구 STEP 1-A: Domain / Scope 명시            (M 문서)
└─ 본 연구 STEP 1-B: Competency Questions 검토      (이 문서)
Noy 공식 Step 2 (Consider reusing existing ontologies) ↔ 본 연구 STEP 1-C   (이번 문서 범위 밖)
```
- **A. 문헌 직접 근거 (Noy.pdf 원문 대조):** p.5 — "One of the ways to determine the scope of the ontology is to sketch a list of questions that a knowledge base based on the ontology should be able to answer, competency questions (Gruninger and Fox 1995). These questions will serve as the litmus test later: Does the ontology contain enough information to answer these types of questions? Do the answers require a particular level of detail or representation of a particular area? These competency questions are just a sketch and do not need to be exhaustive." → CQ는 scope 결정 도구이며 이후 온톨로지가 충분한지 판단하는 시금석이고, 완결적일 필요가 없다. p.8 Step 5 — "The classes alone will not provide enough information to answer the competency questions from Step 1." → CQ는 속성 설계(Step 5)의 기준으로도 다시 쓰인다. p.5 — "The answers to these questions may change during the ontology-design process" → CQ·scope는 고정되지 않는다.
- **A-보조:** Li et al.(2025) Stage 2(p.10)는 CQ를 온톨로지 확장(70%)과 평가(30%)에 사용한다. 다만 그들의 CQ는 LLM이 생성한 뒤 사람이 40개로 걸러낸 것이며 우리 CQ와 출처가 다르다. 이 단계에서는 그 절차를 **채택하지 않는다(NOT-ADOPTED)**.
- **B. 본 연구 적용 결정:** 아래 검토 항목(목적 관련성, 중복, 목적 혼합, 구현 전제, availability와 domain 필요성의 구분)과 판정 코드는 Noy의 항목이 아니라 본 연구가 CQ를 점검하기 위해 정한 기준이다.
- **문헌이 직접 말하지 않는 것:** Noy는 CQ 개수, 중복 허용 여부, CQ 검토 기준을 제시하지 않는다(CQ는 "just a sketch").
- "대표 운영 상황/대표 사용자 질문"(handoff §4.2)은 Noy에 없는 본 연구 operationalization(B)이다. 새 가상 시나리오는 만들지 않았고, 현실성 확인은 **STEP 0에서 확인된 실제 상황**(승인 기록, 규정 조문)만 사용했다.

## 1. 연구 목적과 사용한 baseline
연구 목적(변경 없음): "현재 댐의 기상·수문 상태를 파악하고, 이와 관련된 과거 운영행위와 당시의 승인·운영기준·근거자료를 연결하여 운영자의 판단을 지원한다." 최종 운영 판단은 운영자이며 decision support 목적이다(자동 방류 결정 아님).
STEP 1-A baseline의 남은 보류(S1A-04/05/06/07/09/10)는 해결하지 않았고, 이 검토와 직접 관련되는 경우에만 §5에 표시했다.

## 2. CQ 검토표
| CQ | 연구 목적 관련성 | Domain/Scope 적합성 | 필요한 지식 종류 | 다른 CQ와 중복 | domain 필요성(자료와 독립) | 문제점 | 판정 |
|---|---|---|---|---|---|---|---|
| CQ1 | 직접(상태 파악) | scope 안 | 관측·측정자료(변수·기간·출처), 댐과 자료의 연결 | CQ6과 부분 중복 | 강함(규정 제11·13조) | 연결 정보와 값 조회의 경계 불명; '기상' 범위·'현재' vs 이력 미정 | **KEEP_WITH_REVIEW** |
| CQ2 | 직접(과거 운영행위) | scope 안(instance 미확보) | 운영행위(시점·대상) | 없음(anchor) | 강함(규정 제6·14조) | '운영행위' 정의 없음(1-D/1-F 과제) — 자료 부재는 CQ 문제가 아님 | **KEEP** |
| CQ3 | 직접(당시의 승인) | scope 안 | 방류 승인(시점·시설·량·특이사항) | CQ4–6과 anchor 공유 | 강함(규정 제6조②, 승인 3,929건) | 승인 접근 경로가 운영행위 경유 하나뿐 — 실제 승인은 시설·일시 기준으로 존재 | **REVISION_CANDIDATE** |
| CQ4 | 직접(당시의 운영기준) | scope 안, 운영기준 범위 미확정 | 운영기준(값·내용), 대상 시설, 적용 시점/버전 | CQ3과 anchor, CQ5와 부분 중복 | 강함(제6조②·별표3, 규정 개정 이력) | 목적은 "당시의"인데 CQ4에는 시점 조건이 없음 | **REVISION_CANDIDATE** |
| CQ5 | 직접(근거자료) | scope 안 | 문서(출처·위치·버전) | CQ3/4의 출처와 부분 중복 | 강함(연구 핵심) | 운영·승인·기준 세 대상을 한 CQ에 묶음; '문서' 범위·위치·버전 미표현 | **KEEP_WITH_REVIEW** |
| CQ6 | 직접(운영 시점의 상태) | scope 안 | 측정자료(강우·유입량·저수위·방류량), 관측소/경로 | CQ1의 구체화 | 강함(규정 제13조) | 변수 의미가 출처마다 다름; 관측소 경유 전제; 운영 시점 anchor | **KEEP_WITH_REVIEW** |

(상세 문장은 `step1_cq_review_matrix.csv`.)

## 3. CQ별 검토 (실제 근거 포함)

### CQ1 — KEEP_WITH_REVIEW
- 목적 관련성은 직접적이다. 다만 문구는 "어떤 관측자료가 **연결**되어 있는가"를 묻고, 목적은 "상태를 **파악**"한다는 값 수준까지 포함한다. 연결 정보(무엇이 있는가)와 값(무슨 수치인가)의 경계가 CQ에서 명시되지 않는다. 이는 Ontology가 값 자체를 담는지(handoff §6.3: 시계열 전체를 node로 저장할지는 미결정) 여부와 연결된 범위 문제이며, 지금 결정하지 않는다.
- '기상'의 범위(관측만인지 예보를 포함하는지)는 1-A에서 예측 모형을 제외 후보(S1A-05)로 둔 것과 관련된다 → **SCOPE REVISION CANDIDATE SR-1**(적용하지 않음).
- CQ6와의 관계: CQ6은 "운영 시점"과 4개 변수로 좁힌 질문이라 CQ1의 하위 질문으로 읽힌다. 중복 자체는 문제가 아니지만 역할 구분을 사용자와 확인한다(S1B-02).

### CQ2 — KEEP
- 연구 목적의 "과거 운영행위"를 직접 표현하며 CQ2–CQ6의 anchor다. 실제 Operation record가 없다는 사실은 **데이터 문제**이며 CQ 제거 사유가 아니다(지침 §5-10). 규정은 운영행위를 서술한다: 제6조② "홍수조절을 위한 수문조작이 필요한 경우", 제14조① "방류량을 조정하고 그 결과를 관할 홍수통제소장에게 지체없이 통보".
- 문제: '운영행위'의 정의·유형이 CQ 안에 없다. 승인 `비고`(증가방류·감소방류·수문전폐 등)나 측정 변화로부터 Operation을 만들 수 없다는 제약은 그대로다.

### CQ3 — REVISION_CANDIDATE
- **관찰(STEP 0 실제 자료):** 승인 record 3,929건은 각각 시설(관측소코드·명), 승인일, 방류시작시간을 직접 가지며 Operation record 없이 존재한다. 예: 충주 순차번호 3412(2020-08-02, 방류시작 2020-08-02 18:00).
- **문제:** CQ3은 승인을 "해당 운영행위와 **관련된**" 것으로만 정의한다. 운영행위가 식별되지 않으면 승인을 물을 수 없고, "2020-08 충주댐에 어떤 방류 승인이 있었나"라는 자연스러운 질문이 CQ 문구로는 표현되지 않는다. 연구 목적은 운영행위와 당시의 승인을 **연결**하는 것이므로 anchor 자체는 타당하나 **접근 경로가 하나뿐**이다.
- **수정안(적용하지 않음):** "특정 댐·시점(또는 해당 운영행위)과 관련된 방류 승인은 무엇인가?" 이는 CQ GAP `G-1`(§4)과 함께 사용자 결정이 필요하다.

### CQ4 — REVISION_CANDIDATE
- **관찰:** 목적은 "**당시의** … 운영기준"이다. 규정 원문 부칙에는 개정이 여러 번 기재되어 있다(부칙 시행일 2018-06-29, 2024-02-29, 2026-07-08). STEP 0에서 실제로 확보한 것은 현행(2026-07-08 시행)뿐이다.
- **문제:** CQ4에는 시점 적용 조건이 없어 현행 기준을 반환해도 CQ 위반이 아니다. 목적과 CQ가 어긋날 위험이 있다. 또한 '운영기준'의 범위(규정만인지, 댐별 관리규정·지침도 포함하는지)가 1-A에서 미확정이다.
- **수정안(적용하지 않음):** "…해당 운영행위 **당시 적용되던** 운영기준은 무엇인가?" 자료(개정 연혁)는 별도 확보가 필요하다(`DATA_REQUIRED`, S1A-07).

### CQ5 — KEEP_WITH_REVIEW
- 근거 기반 판단 지원이라는 목적의 핵심이며 domain 필요성이 강하다. 그러나 운영·승인·기준의 출처가 서로 다른 종류(규정 조문 / 승인 데이터셋 / 운영 기록)라 세 질문이 한 문장에 섞여 있다. 또한 "어느 문서"에서 더 나아가 문서 내 위치(조·별표)와 버전이 필요하다는 점이 문구에 드러나지 않는다(STEP 0에서 Criterion은 조문·별표 위치를 가지며 승인은 파일 단위 출처뿐).
- 분리 여부는 사용자 판단 사항이며 지금 수정하지 않는다.

### CQ6 — KEEP_WITH_REVIEW
- 규정 제13조는 "월별 저수위, 유입량, 방류량, 발전량 등 운영실적"을 명시하므로 4개 변수 열거는 도메인 근거가 있다. 그러나 STEP 0에서 확인된 변수 의미 차이(`방류량` vs `총방류량`, `저수율` 정의 충돌)는 CQ가 아닌 변수 정의의 문제다.
- "어떤 관측소·측정자료를 통해"는 관측소를 경유한다는 전제를 담는다. 실제 장기 시계열은 댐 단위로 제공된다(STEP 0). ObservationStation 개념이 도메인에 실재하므로 CQ 문구는 유지하되 특정 자료 구조에 대한 의존 가능성을 표시한다. '운영 시점' anchor는 CQ3과 같은 접근 경로 문제가 있다.

## 4. 누락 후보 — [CQ GAP CANDIDATE] (자동 추가하지 않음)

**G-1. 운영행위 없이 시설·시점으로 승인·기준·측정에 접근**
- 빠진 정보 요구: 운영행위가 식별되지 않은 상태에서, 특정 댐·기간에 존재하는 방류 승인·적용 기준·측정자료를 확인하는 질문.
- 목적상 필요: 운영자는 현재 상황과 관련된 과거 승인을 시설·시점으로 찾는다. 승인은 규정상 운영행위의 **사전** 절차이며(제6조②) 운영행위 record 없이도 존재한다.
- 기존 CQ로 부족한 이유: CQ3–CQ6이 모두 "해당 운영행위/운영 시점"에 anchor.
- 근거: STEP 0 실제 자료(승인 3,929건은 Operation 없이 존재), 규정 제6조②. 문헌 근거: **C** — Noy가 이 문제를 다루지 않음.
- 추가 검토: CQ3 revision과 통합할지, 별도 CQ로 둘지.

**G-2. 기준·승인·측정의 시점 적용성(당시의)**
- 빠진 정보 요구: 특정 시점에 어떤 버전의 규정·기준이 유효했는가.
- 목적상 필요: 목적 문장 "당시의". 기존 CQ로 부족: CQ4는 시점 조건이 없고 CQ5는 버전을 묻지 않음.
- 근거: 규정 부칙의 개정 이력(2018, 2024, 2026), STEP 0의 현행 버전 한정 확보. 문헌 근거: **C**(Li et al.은 시점별 규정 버전을 다루지 않음).
- 추가 검토: 자료(연혁) 확보 — `DATA_REQUIRED`.

**G-3. 수계·상하류 맥락**
- 빠진 정보 요구: 대상 댐의 운영과 함께 고려되는 상·하류 시설/수계 상태.
- 목적상 필요 여부: 목적 문장에는 명시되어 있지 않다. 규정은 "수계 전체 홍수 상황을 고려"(제6조③), 연계운영(제2조 1호)을 서술하고, K-water 시설 소개에 댐 간 상·하류 서술(STEP 0, 단일 출처)이 있다.
- **이 정보 요구가 목적상 CQ에 필요한지 자체가 미결정**이다(`S1A-06`). 필요하다고 판단해도 CQ나 Ontology에 추가하지 않는다. 문헌 근거: **C, LITERATURE_CHECK_REQUIRED**.

**G-4. 측정값의 성격(실시간·잠정·최종, 관측·계산)**
- 빠진 정보 요구: 근거로 제시하는 측정값이 관측인지 계산값인지, 잠정인지 최종인지.
- 목적상 필요: "근거자료"를 근거로 쓰려면 성격 표시가 필요하다. 기존 CQ로 부족: CQ1/CQ6은 자료의 존재·경로만 묻는다.
- 근거: STEP 0(유입량은 계산값이라는 K-water 서술, KHNP 페이지의 잠정 고지). 문헌 근거: **C**. 이는 CQ보다 변수 사전·provenance 문제일 수 있어 `S1B-08`로 기록.

**필요성만 기록(CQ 후보로 두지 않음):** "현재 상태와 유사한 과거 운영사례는 무엇인가?" — handoff §4.3이 Ontology CQ에서 제외하고 STEP 3 retrieval 설계로 넘긴 질문이다. 연구 목적 문장("현재 … 상태를 파악하고 … 과거 운영행위 … 연결")과 관련이 있어 필요성은 있으나 similarity/retrieval 설계와 연결되므로 CQ로 추가하지 않는다.

## 5. STEP 1-A 보류사항 중 CQ 검토와 직접 연결된 것
"이 CQ가 해당 보류사항의 해결을 요구한다"만 기록한다(해결하지 않음).
| CQ | 관련 보류사항 |
|---|---|
| CQ1, CQ6 | S0-C(관측소–dataset), S0-E(시간 규약), S1A-11(측정 저장 방식) |
| CQ2 | S1A-09(Operation instance), S1A-10(행위자) |
| CQ3 | S0-B(Approval field semantics), S0-D(시설 식별), S1A-09 |
| CQ4 | S1A-07/S0-A(Criterion temporal validity), S1A-05(운영기준 범위) |
| CQ5 | S1A-07(문서 버전), S0-B(승인의 문서) |
| (CQ 없음) | S1A-06(상·하류) — G-3 |

## 6. 전체 관찰
- **Operation hub 구조:** CQ3–CQ6이 모두 "해당 운영행위/운영 시점"에 anchor된다. 이는 연구 목적("과거 운영행위와 당시의 승인·기준·근거자료를 **연결**")과 부합하지만, (i) Operation record가 없으면 사슬 전체가 묻히고(데이터 문제), (ii) 승인·기준·측정을 시설·시점으로 직접 접근하는 경로가 CQ에 없다(CQ 설계 문제, G-1). 두 문제를 혼동하지 않는다.
- **중복:** CQ1↔CQ6 부분, CQ3/CQ4↔CQ5 부분. 의도된 중첩(상위-하위, 항목-근거)으로 보이나 역할 구분을 확인한다.
- **구현 전제:** CQ 문구가 특정 저장·검색 기술을 전제하지 않는다. 다만 CQ6의 "관측소 경유"는 자료 구조 의존 가능성이 있다.
- **SCOPE REVISION CANDIDATE:** SR-1 '기상' 범위(관측만/예보), SR-2 상·하류 맥락(=G-3), SR-3 운영기준의 범위(규정만/댐별 관리규정 포함)(=S1A-05 관련). **적용하지 않음.**

## 7. 결과 요약
CQ1 KEEP_WITH_REVIEW · CQ2 KEEP · CQ3 REVISION_CANDIDATE · CQ4 REVISION_CANDIDATE · CQ5 KEEP_WITH_REVIEW · CQ6 KEEP_WITH_REVIEW. CQ 문구는 수정하지 않았고, 수정안은 위와 같이 제시만 했다. Working Ontology Candidate v1의 설계 검토(1-E/F)와 CQ 기반 검증(1-I)에서 이 판정을 참조한다.
