# STEP 1 Decision / Ambiguity Log

- 기준: `01_AI_RESEARCH_HANDOFF.md`(canonical). 대상: Initial Ontology v0.1 (수정하지 않음).
- 규칙: 기존 판단이 바뀌면 **이전 기록을 삭제하지 않고** 변경 이유를 "변경 이력"에 추가한다.
- 상태: RESOLVED / REVIEW_REQUIRED / LITERATURE_CHECK_REQUIRED / DATA_REQUIRED / EXPERT_REVIEW_REQUIRED / DEFERRED
- 근거 수준: **A** 문헌 직접 근거 / **B** 본 연구 적용 결정 / **C** 추가 검토 필요
- 문제 유형: **A** Ontology / **B** Data·Mapping / **C** Data Availability / **D** Literature·Methodology / **E** Expert Review

## 1. STEP 1-A 에서 발생한 항목

| ID | 발견 단계 | 쟁점 | 관련 CQ | 관련 Ontology 요소 | 관련 실제 자료 | 관련 문헌 | 현재 판단 | 근거 수준 | 유형 | 상태 | 다음 필요한 행동 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S1A-01 | 1-A | **Noy & McGuinness: 원문 대조 완료**(Noy.pdf, Step 1 = PDF p.5, 3절 = p.4). **Li et al.(2025): 원문 미대조** — `36_FloodOntology.pdf`를 이 환경의 추출 도구로 읽지 못함. Li et al.은 handoff §4.1 기재 수준으로만 사용 | 전체 | STEP 1 방법론 근거 | Noy.pdf, handoff §4.1·§17 | Noy; Li 2025 | Noy: 근거 확정(M 문서 §1·§9). Li: 원문 대조 전까지 "직접 인용"으로 표기하지 않음 | A(Noy 확정) / Li는 A(handoff 기재)+원문 C | D | LITERATURE_CHECK_REQUIRED (Li et al.에 한함) | Li et al. PDF를 읽을 수 있는 방법 확보(텍스트 추출 도구 또는 텍스트본) 후 expert boundary/validation 서술 대조 |
| S1A-02 | 1-A | Domain 정의문 초안: "댐 운영 의사결정 지원을 위한 근거 지식(관측·측정자료, 운영행위, 방류 승인, 운영기준, 근거 문서와 출처)의 의미 구조" | CQ1~6 | 전체 Class 7개 | 연구 목적 문장, STEP 0 자료 | Noy Step 1 | M 문서 §3 Q1 초안 채택 제안. 사용자 확인 전 확정하지 않음 | B | B/E | REVIEW_REQUIRED | 사용자가 문구 확인·수정 |
| S1A-03 | 1-A | domain(댐 운영 일반)과 pilot 자료 범위(한강수계, 승인 2010~2021, 측정 2019~2026 일부)의 구분; "댐"의 경계(다목적댐·용수댐·수력발전댐·홍수조절용댐·조정지·보를 모두 Dam으로 볼지) | CQ1, CQ2 | Dam | dam_catalog.csv, 별표1, K-water 시설 목록 | (미조사 — 1-C/1-D) | domain은 일반 댐 운영, 자료 범위는 pilot으로 구분해 기술. 시설 유형 경계는 미결정 | B | A/B | REVIEW_REQUIRED | 1-D 용어 도출에서 시설 유형 용어 수집; 1-F에서 검토 |
| S1A-04 | 1-A | 사용자/유지·검토 주체가 canonical에 명시되지 않음. 최종 사용자(운영자)와 Ontology 직접 소비 주체를 나눠 읽은 것은 본 연구 해석 | - | 전체 | handoff §1.1, §3 | Noy Step 1 (p.5: "Who will use and maintain the ontology?", 사용자와 유지 주체가 다른 집단일 수 있다는 예); Li 2025 (expert review; 미대조) | 임의 가정하지 않음. 최종 사용자 = 댐 운영자(handoff), 유지·검토 주체 = 미정. 사용자를 최종 사용자/직접 소비 주체로 나누는 것은 문헌에 없는 본 연구 적용 | C | E | EXPERT_REVIEW_REQUIRED | 사용자: 설계·유지 책임자, 검토할 도메인 전문가(분야·역할) 지정 |
| S1A-05 | 1-A | 제외 범위: canonical 명시 제외(자동 결정, rationale 추정 등) 외에 이번에 제안한 제외(예측 모형, 안전관리·수질·용수·발전 자체, 한강수계 외) | - | 범위 | handoff §1.2, §4.3 | - | canonical 명시 제외는 그대로; 제안 제외는 미확정 | B(제안) | E | REVIEW_REQUIRED | 사용자 확인 |
| S1A-06 | 1-A | 상·하류 관계가 Ontology scope에 포함되는지. 실제 공식 서술 evidence는 있으나 CQ1~6에 상·하류 질문이 없고 v0.1에 Relation 없음 | (없음) | (신규 Relation 후보 — 추가하지 않음) | dam_network_evidence.csv(11건, 단일 출처) | (미조사) | 자동 추가 금지. canonical §12 절차(반복 필요성 확인 → 문헌 검토 → 결정) 유지 | C | A/D | DEFERRED | 1-B에서 CQ와의 관련성 확인 후 필요 시 문헌 검토 |
| S1A-07 | 1-A | **Criterion 시점 적용성**: 연구 목적이 "당시의" 기준을 요구하나 확보한 Criterion은 2026-07-08 시행 현행본뿐, 대표 Approval 사례는 2019~2020 | CQ4, CQ5 | Criterion, Document, (Criterion–시점 표현 여부) | criterion_list.csv, linkage_pilot_cases.csv | - | 2020 승인 ↔ 2026 기준 연결은 주장하지 않음. 시점 표현이 Ontology에 필요한지 미결정 | B(목적) / 자료 C | B/C | DATA_REQUIRED | 당시 시행 버전(연혁) 확보 가능성 조사 — 별도 gap-filling 필요, 이후 STEP 1-F/G에서 표현 방식 검토 |
| S1A-08 | 1-A | 이전 산출물(K, L, linkage_pilot_cases.csv, STEP0_summary 5-1)에서 "Criterion·Document 연결"이 시점 적용성을 암시 | CQ4 | Criterion | 위 파일들 | - | 해당 연결을 "시설명 기준의 대조(현행 버전; 당시 적용성 미검증)"로 정정 주석 추가. 기존 문장은 삭제하지 않음 | - | B | RESOLVED (문서 정정만; 근본 쟁점은 S1A-07) | — |
| S1A-09 | 1-A | Operation: 개념은 scope에 두지만 실제 instance 없음. Approval·비고·접수방류량·총방류량 변화로 추론 금지 | CQ2, CQ3, CQ4, CQ5 | Operation 및 관련 Relation 4개 | (없음) | - | 미검증 유지 | B | C | DATA_REQUIRED | 별도 targeted gap-filling (Operation instance) |
| S1A-10 | 1-A | 행위자(홍수통제소장·시설관리자·관계기관·운영기관)가 규정·자료에 등장하나 v0.1에 대응 개념 없음 | CQ3(승인 주체), CQ5 | (신규 후보 — 추가하지 않음) | 규정 제2조, 승인 파일 제공기관 표기, dam_catalog.csv | (미조사) | 결정하지 않음. 1-D 용어 도출에서 용어로만 수집 | C | A | DEFERRED | 1-D |
| S1A-11 | 1-A | 측정 시계열 저장 방식 미결정. Ontology는 Dam–Station–Dataset 수준 연결을 scope로 둔다는 경계 제안 | CQ1, CQ6 | MeasurementDataset, ObservationStation | handoff §6.3, 측정 dataset 71개 | GraphAide(handoff §7.3; STEP 3) | 저장 방식은 결정하지 않음 | B | A/D | DEFERRED | 1-F/1-H |
| S1A-12 | 1-A | handoff §4.2의 "대표 운영 상황 정의 → 대표 사용자 질문 정의" 단계가 이번 지침 1-A~J에 별도로 없음; 1-C(기존 Ontology 재사용 검토)는 handoff 흐름에 없는 추가 | - | STEP 1 흐름 | handoff §4.1~4.2 | Noy Step 2 "Consider reusing existing ontologies"(p.5–6; 1-C에 대응, 문헌 근거 A 확인); "대표 운영 상황/대표 사용자 질문"이라는 단계명은 Noy 원문에서 확인되지 않음(handoff §4.1도 본 연구 적용이라 명시) | 충돌로 보지 않음(비차단). 1-C는 문헌 근거가 확인된 추가. 대표 운영 상황/대표 사용자 질문을 1-B에서 CQ와 함께 다룰지 확인 필요 | B | D | REVIEW_REQUIRED | 사용자 확인 (1-B 범위) |

## 2. STEP 0 에서 이월된 불확실성 (지침 §11 A~G)

| ID | 발견 단계 | 쟁점 | 관련 CQ | 관련 Ontology 요소 | 관련 실제 자료 | 관련 문헌 | 현재 판단 | 근거 수준 | 유형 | 상태 | 다음 필요한 행동 / 예정 단계 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S0-A | 0 | Criterion temporal validity | CQ4,5 | Criterion, Document | 위 S1A-07 | - | S1A-07로 통합 관리 | B/C | B/C | DATA_REQUIRED | 연혁 버전 확보 조사 |
| S0-B | 0 | `접수방류량`=`approvedReleaseAmount`? `승인년월일시분`=`approvalTime`(값에 시각 없음)? `접수일자`, `방류시작시간`, `비고`의 위치 | CQ3 | Approval.approvalTime, approvedReleaseAmount | approval_records_hrfco_raw_fields.csv, J 보고서 | (미조사) | 확정하지 않음. 원본 필드명·값 보존 | C | A/B | REVIEW_REQUIRED | STEP 1-F(Property 검토); 출처 정의 추가 확인 |
| S0-C | 0 | Station–Dataset: 장기 측정은 dam-level(getPeriod/getHydr); `hasDataset` 직접 확인 안 됨 | CQ1, CQ6 | ObservationStation–hasDataset | L 보고서, I 보고서 | (미조사) | 미확정 | C | A/B | REVIEW_REQUIRED | STEP 1-F/1-H |
| S0-D | 0 | 시설 식별: 같은 코드·다른 이름, 같은 이름·다른 코드(보 3곳) | CQ2~CQ6 | Dam.damId | approval_facility_code_crosswalk.csv | - | 자동 통합 금지 | B | B | REVIEW_REQUIRED | STEP 1-E/1-H |
| S0-E | 0 | 시간 규약: hour=24, timezone, 방류시작시간/승인일/접수일, SDATE 라벨 | CQ1, CQ3, CQ6 | Operation.operationTime, Approval.approvalTime 등 | time_conventions.csv | - | 보정·변환하지 않음 | C | B | REVIEW_REQUIRED | STEP 1-G/1-H; 출처 정의 확인 |
| S0-F | 0 | 상·하류 Relation 부재 | - | (후보) | dam_network_evidence.csv | (미조사) | S1A-06으로 관리 | C | A/D | DEFERRED | S1A-06 |
| S0-G | 0 | Operation instance 없음 | CQ2~5 | Operation | - | - | S1A-09로 관리 | B | C | DATA_REQUIRED | S1A-09 |

## 3. 변경 이력
| 날짜 | ID | 변경 | 이유 |
|---|---|---|---|
| 2026-09-30 | S1A-01, S1A-04, S1A-12 | **개정(Noy 원문 대조 후)**: S1A-01은 "Noy·Li 모두 미대조"에서 "Noy 대조 완료, Li만 미대조"로 범위 축소; S1A-04는 v1의 "문헌이 사용자를 구분하지 않았다"를 "Noy는 사용자와 유지 주체를 구분하나, 최종 사용자/직접 소비 주체 구분은 본 연구 적용"으로 정정; S1A-12는 1-C의 문헌 근거(Noy Step 2) 확인 추가 | 사용자가 공유한 Noy.pdf 원문 대조 (M 문서 v2, §10) |
| 2026-09-30 | S1A-08 | 신규 등록 | K/L 문서·linkage_pilot_cases.csv의 Criterion "연결" 표현이 §11-A와 어긋남을 STEP 1-A 점검에서 발견 |

## 4. STEP 1-B ~ 1-J 추가 항목 (마스터 실행, 2026-09-30) — 기존 항목·상태는 변경하지 않음

| ID | 단계 | 쟁점 | 현재 판단 | 근거 수준 | 상태 | 다음 행동 |
|---|---|---|---|---|---|---|
| S1B-01 | 1-B | CQ3 승인 접근 경로(Operation 경유뿐) | REVISION_CANDIDATE, 문구 미수정 | B | REVIEW_REQUIRED | 사용자 결정 |
| S1B-02 | 1-B | CQ1↔CQ6 역할 중복 | 의도된 상위·하위로 보이나 확인 필요 | B | REVIEW_REQUIRED | 사용자 확인 |
| S1B-03 | 1-B | CQ4 "당시의" 시점 조건 없음 | REVISION_CANDIDATE | B | REVIEW_REQUIRED | S1A-07과 함께 |
| S1B-04 | 1-B | CQ5 세 대상 혼합 | KEEP_WITH_REVIEW | B | REVIEW_REQUIRED | 분리 여부 |
| S1B-05 | 1-B | G-1 운영행위 없이 시설·시점 접근 | GAP 후보 | C | REVIEW_REQUIRED | CQ3과 통합 여부 |
| S1B-06 | 1-B | G-2 시점 적용성 | GAP 후보 | C | DATA_REQUIRED | 연혁 |
| S1B-07 | 1-B | G-3 상·하류 (필요성 미결) | GAP 후보, 추가 안 함 | C | DEFERRED | S1A-06 |
| S1B-08 | 1-B | G-4 측정값 성격(잠정/최종) | 변수 사전·provenance 문제일 수 있음 | C | REVIEW_REQUIRED | - |
| S1C-01 | 1-C | 재사용 후보(SOSA/SSN, PROV-O, HY_Features 등) 원문 미독 | 자동 import 금지 | C | LITERATURE_CHECK_REQUIRED | 원문 확보 |
| S1C-02 | 1-C | OntoDSMS의 SSN/SOSA 재사용과 본 연구 Station/Dataset 관계 | 원문 확인 후 | C | LITERATURE_CHECK_REQUIRED | - |
| S1D-01 | 1-D | 용어 163개 수집, 분류 미실시 | 완료 | A | CONFIRMED(절차 수행) | - |
| S1E-01..24 | 1-E/F | 요소 검증(KEEP 9 / REVIEW 8 / NOT_TESTABLE 7) | `step1_ontology_element_validation.csv` | A/B | 요소별 상태는 CSV verdict | 전문가 검토 |
| S1G-01 | 1-G | approvalTime 유형, 금액 단위, 시간대 미고정 | 후보만 | C | REVIEW_REQUIRED | S0-B/E |
| S1H-01 | 1-H | 충주 승인 3412/3519 관계 추론 금지 | 원문 보존 | B | REVIEW_REQUIRED | - |
| S1I-01..06 | 1-I | CQ별 문제 분류 | `step1_cq_validation.csv` | B | REVIEW_REQUIRED | - |
| S1J-01 | 1-J | 전문가 검토 대상 7종 (프로토콜 미정의) | 대상 목록만 | C | EXPERT_REVIEW_REQUIRED | 전문가·절차 지정 |
| S1L-01 | 전체 | `11_LSMKG.pdf` 부재 | STEP 3 근거 검증 불가 | - | LITERATURE_CHECK_REQUIRED | 파일 공유 |

**변경 이력 추가:** S1A-01의 "Li 미대조"는 Li.pdf를 이후 원문 대조함(`STEP1_METHOD_EVIDENCE.md`). 상태 표기는 사용자 승인 전까지 그대로 두고, 대조 완료 사실만 여기에 기록.

## 5. STEP 2 추가 항목 (2026-09-30)
| ID | 쟁점 | 현재 판단 | 상태 |
|---|---|---|---|
| S2-01 | Approval-file Dam ↔ MyWater Dam 동일성 미해결 → KG 간선만으로 Approval→Measurement 도달 0/3,929 | 병합하지 않음(S0-D 유지); 통합 질의는 crosswalk 표를 검토 필요 플래그와 함께 외부 조회 | REVIEW_REQUIRED |
| S2-02 | Criterion→Dam 관계 부재(v0.1·v1). facilityNameInSource 리터럴로만 보존 | RC-11 후보(적용 안 함) | REVIEW_REQUIRED |
| S2-03 | MeasurementDataset 기간은 요청 기간(실제 커버리지 아님) | 실제 커버리지 산출은 개선 후보 | REVIEW_REQUIRED |
| S2-04 | 그룹 dataset 37개의 Dam 연결 미구현 | 원본 damList로 도출 가능 | DEFERRED |
| S2-05 | 측정값을 KG에 저장하지 않음 | handoff §6.3 미결정의 잠정 처리 | PROVISIONAL |
| S2-06 | 접수방류량·승인년월일시분 매핑 미확정 → approvedReleaseAmount/approvalTime 미채움 | S0-B 유지 | REVIEW_REQUIRED |

## 6. 데이터 공백 보완(2026-10-01) 후 갱신 제안 — 기존 상태는 변경하지 않음 (사용자 승인 전 RESOLVED 금지)
| ID | 갱신 제안 | 근거 |
|---|---|---|
| S1A-07 / S0-A | 제안: DATA_REQUIRED → PARTIALLY_AVAILABLE. 2012-01-01 이후 연혁 9개판 확보, 한강수계 시설 별표3 값은 전 판 동일. 2012 이전 1,146건은 여전히 DATA_REQUIRED | `03_normalized/criterion_version_history.csv`; `DATA_COLLECTION_GAP_REPORT.md` §2-3 |
| S0-B | 제안: REVIEW_REQUIRED 유지. 승인 필드의 공식 설명 확보(방류시작시간·비고 VERIFIED; 접수방류량 PARTIAL; 접수일자 UNRESOLVED) | `02_metadata/approval_field_dictionary.csv` |
| S0-C | 제안: 부분 갱신. getRainTrend(damCd+obsCd)로 관측소 단위 시계열 조회 가능(충주 2개 관측소 검증) — STEP 2의 "관측소 단위 dataset 없음"(MR-12 NOT_SUPPORTED) 판단 재검토 필요 | `01_raw/KWater/lookup_probe/`; `measurement_lookup_key_evidence.csv` |
| S0-D | 제안: 유지(OFFICIAL_CROSSWALK_REQUIRED). VERIFIED_SAME 0건 | `facility_identity_evidence.csv` |
| S0-E | 제안: 부분 갱신. 시간 라벨 분포 확인, 공식 정의문은 없음 | `time_conventions_verified.csv` |
| S0-G / S1A-09 | 제안: DATA_REQUIRED 유지. 후보와 한계를 기록 | `operation_source_search_log.csv` |
| STEP 2 정정 | CR-09 값 "25.51)"는 25.5 + 각주 1) | `DATA_COLLECTION_GAP_REPORT.md` §2-3 |
