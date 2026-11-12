# 서버 실행 기록: 한수원 태스크 82개 질문, 보완 후 (서버 시각 2026-11-12 13:32 시작)

- 질문: ../question_set_tasks82.json (11/06 실행과 같은 82개)
- 모델: Qwen3-32B-AWQ (vLLM, --max-model-len 32768, RTX A6000 1장). 11/06과 같은 설정으로 다시 띄웠다.
- 코드와 프롬프트: 11/13 보완본(../tasks82_fix_20261113.md). 기준 날짜는 PIPELINE_TODAY=2026-11-06으로 고정했다.
- 실행: scripts/run_eval_server.sh (원래 결과 폴더 eval_runs/20261112_133236_llm). 82개 합계 약 26분.
- 사람이 읽고 나눈 결과와 11/06과의 비교: ../tasks82_llm_review_1113.md (만드는 코드 ../tasks82_llm_review_1113.py)
