# 서버 실행 결과 (2026-10-16)

사용자가 서버에서 `step11_pipeline.py`를 실행해 얻은 결과 폴더를 그대로 보관한다(수정하지 않음).

- 모델: Qwen/Qwen3-32B-AWQ (4비트 AWQ), vLLM 서빙, temperature 0, 생각 모드 끔(`LLM_NO_THINK=1`)
- 질문 파일: `05_retrieval/questions_example.json`의 q1~q5 (q1이 전체 질문, q2~q5는 동작 확인용 질문)

| 폴더 | 실행 | 내용 |
|---|---|---|
| `083450_no_answer_q1-q5` | `--no-answer` | 의도 추출, 검색, 근거 묶음까지(답변 없음) |
| `084150_answer_q1-q5` | 전체 | q1~q5 답변 포함 |
| `091208_answer_q1`, `091453_answer_q1`, `091737_answer_q1` | 전체 | q1만 3회 반복 실행(의도, 근거 묶음, 답변 모두 동일) |

q1의 의도는 083450에서 `CQ1, CQ5, CQ2, CQ3, CQ4`, 나머지 4회에서 `CQ1, CQ5, CQ4, CQ3`(CQ2 없음)이었다.
