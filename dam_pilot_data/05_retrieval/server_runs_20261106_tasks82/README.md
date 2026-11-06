# 서버 실행 기록: 한수원 태스크 82개 질문 (2026-11-06)

- 질문: ../question_set_tasks82.json (태스크마다 사용자 요청 예를 실제 댐·날짜로 바꾼 질문 하나)
- 모델: Qwen3-32B-AWQ (vLLM, --max-model-len 32768, RTX A6000 1장), 의도 추출과 답변 모두 같은 모델
- 실행: scripts/run_eval_server.sh → eval_question_set.py --mode llm (원래 결과 폴더 eval_runs/20261106_085631_llm)
- 질문마다 q*.json: 의도 원문(intent_raw), 의도 JSON, 찾은 근거(result), 근거 묶음(bundle), 답변(answer), 오류(error)
- 근거 묶음이 2만 자를 넘는 질문(한도 초과 오류가 난 것 등)은 이 보관본에서 앞 2만 자만 남겼다(bundle_truncated_in_archive). 원래 길이는 bundle_chars.
- 사람이 읽고 나눈 결과: ../tasks82_llm_review.md (만드는 코드 ../tasks82_llm_review.py)
