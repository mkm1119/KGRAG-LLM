# STEP 3 — Method Evidence

| 항목 | 문헌이 실제로 한 것 | 본 연구 채택 | 수준 |
|---|---|---|---|
| Hybrid 검색(KG + 벡터) | GraphAide(PDF p.2–4): 벡터 검색과 서브그래프 매칭을 결합한 context 생성, 질의 확장, Cypher 자동 생성 지원. 실험은 뉴스 1,846건 기반 KG, GPT-4o·Chroma·Neo4j·LangChain | **벡터 검색·임베딩·LLM 모델·Cypher는 사용하지 않음**(구현 기술 미결정). 규칙 기반 KG 순회 + 파일 조회로 대체 | 논문 구조 참고(A) / 실제 구현은 B |
| 외부 시계열 조회 | GraphAide p.2: 기능 목록에만 존재, 보고된 실험에서 시연·평가 안 됨 | 시간자료는 KG 밖 파일에서 조회(STUDY-ADAPTATION). **"논문이 KG+텍스트+측정 결합을 검증했다"고 주장하지 않음** | C |
| 구성요소별 평가 | GraphAide p.3: 여러 구성요소가 있는 시스템은 단일 지표가 부족, 구성요소별 지표 필요 | 검색(증거 회수)과 근거 기반 답변을 **분리 평가**(원칙만 채택). RAGAS 등 지표는 사용하지 않음 | A(원칙)/B |
| 질의 이해·KG QA | LSMKG(Zhang et al. 2025)가 handoff에서 지정됨 — **원문 파일이 저장소·업로드 어디에도 없음** | 근거로 사용하지 않음. 질의 이해는 사람이 질문에 대응하는 검색 규칙을 정한 규칙 기반 | LITERATURE_CHECK_REQUIRED |
| 근거 기반 답변 | (확보 원문에 댐 운영 QA의 근거-답변 검증 방법 없음) | 답변을 claim으로 분해해 evidence ID에 연결하고 원문 문자열 포함 여부를 자동 확인; 클래스 RETRIEVED_FACT / DERIVED_INTERPRETATION / UNCERTAIN / UNAVAILABLE / UNSUPPORTED_GENERATION | B(본 연구 방법) |
| KG 필요성 판단 | (문헌에 벤치마크 없음) | 질문별 체크리스트(다중 홉/출처 결합/관계 필터/근거 추적)는 **본 연구 분석 기준이며 문헌 기준이 아님** | B |
| 평가 임계값·신뢰도 점수 | - | 사용하지 않음(임의 임계값·점수 금지) | - |

"LLM" 역할: 이 세션의 모델이 **검색된 evidence만 사용**해 답변 claim을 작성. 모델 사전 지식은 댐 운영 근거로 쓰지 않음. 자동 검사는 문자열 포함 여부만 확인하며 의미 정확성은 보증하지 않는다(§ GROUNDED 평가 한계).
