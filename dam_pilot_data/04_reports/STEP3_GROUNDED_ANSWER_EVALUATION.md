# STEP 3 — Grounded Answer Evaluation

입력: `qa_answer_claim_check.csv` (25 claim 중 3개는 제외 대조 사례). 스크립트 `scripts/step3_answers.py`.

## 1. 결과
| claim 클래스 | 수 | 자동 검사 |
|---|---|---|
| RETRIEVED_FACT | 13 | 13 PASS(인용 문자열이 evidence 본문에 존재) |
| DERIVED_INTERPRETATION | 1 | PASS (창 내 최소/최대; 계산 evidence 인용) |
| UNCERTAIN | 3 | PASS |
| UNAVAILABLE | 5 | PASS (Q05는 KG의 Operation 엔티티 0건을 코드로 확인) |
| UNSUPPORTED_GENERATION(답변에서 제외) | 3 | EXCLUDED |
답변에 포함된 claim은 모두 evidence ID에 연결. "게이트를 열어야 한다" 류의 판단 주장은 없음.

## 2. 검사가 실제로 잡은 것
초기 실행에서 N02 claim 1건이 FAIL — 승인 필터를 2020년으로 좁히자 evidence ID가 이동했기 때문(claim이 잘못된 evidence를 가리킴). ID 수정 후 PASS. 자동 검사가 evidence-claim 불일치를 실제로 탐지함을 보여주는 사례.

## 3. 한계 (정직한 보고)
- 문자열 포함 검사는 **의미 정확성을 검증하지 않는다**(값이 맞는 위치에 쓰였는지, 해석이 적절한지).
- UNSUPPORTED_GENERATION 3건은 **실제 모델 출력에서 관찰된 것이 아니라** "이런 주장은 답변에서 제외한다"는 대조 예시로 작성한 것이다. 따라서 이 pilot은 환각률을 측정하지 않았다.
- 답변 작성자와 검사 규칙 설계자가 같으므로 독립 평가가 아니다. 전문가 검토 필요(EXPERT_REVIEW_REQUIRED).
- 규칙: 운영 판단(방류 여부 등)은 하지 않음.
