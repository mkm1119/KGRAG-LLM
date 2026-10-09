# 예시 요청 실행 결과 (의도 JSON은 사람이 채움, LLM 분류 아님)

## 1. CQ1
- 질문: 소양강댐 지금 수위랑 방류량이 어때?
- 요청: `{"intent": "CQ1", "slots": {"dam": "소양강댐"}}`
- 결과 요약: `{"status": "ok", "state_rows": 1}`

## 2. CQ2
- 질문: 2020년 8월 2일 18시 충주댐 상태는?
- 요청: `{"intent": "CQ2", "slots": {"dam": "충주", "time": {"at": "2020-08-02T18:00"}}}`
- 결과 요약: `{"status": "ok", "state_rows": 1}`

## 3. CQ3
- 질문: 2020년 8월에 충주댐에서 어떤 방류 조작이 있었어?
- 요청: `{"intent": "CQ3", "slots": {"dam": "충주댐", "time": {"start": "2020-08-01", "end": "2020-08-31"}}}`
- 결과 요약: `{"status": "ok", "operations": 2}`

## 4. CQ4
- 질문: 2020년 8월 광동댐 방류 승인 내역 알려줘
- 요청: `{"intent": "CQ4", "slots": {"dam": "광동댐", "time": {"start": "2020-08-01", "end": "2020-08-31"}}}`
- 결과 요약: `{"status": "ok", "approvals": 4}`

## 5. CQ5
- 질문: 횡성댐 홍수기 제한수위는?
- 요청: `{"intent": "CQ5", "slots": {"dam": "횡성댐"}}`
- 결과 요약: `{"status": "ok", "criterion": 1}`

## 6. CQ5
- 질문: 광동댐 홍수기 제한수위는?
- 요청: `{"intent": "CQ5", "slots": {"dam": "광동댐"}}`
- 결과 요약: `{"status": "ok", "criterion": 0}`

## 7. CQ6
- 질문: 승인 3412의 공식 근거는 뭐야?
- 요청: `{"intent": "CQ6", "slots": {"target": {"type": "approval", "id": "3412"}}}`
- 결과 요약: `{"status": "ok", "evidence": 1}`

## 8. CQ6
- 질문: 충주댐 수위 자료는 어디서 온 거야?
- 요청: `{"intent": "CQ6", "slots": {"target": {"type": "state", "dam": "충주댐"}}}`
- 결과 요약: `{"status": "ok", "evidence": 6}`

## 9. INTEGRATED
- 질문: 2017년 8월 24일부터 31일까지 소양강댐 운영 상황을 승인, 당시 상태, 기준까지 알려줘
- 요청: `{"intent": "INTEGRATED", "slots": {"dam": "소양강댐", "time": {"start": "2017-08-24", "end": "2017-08-31"}}}`
- 결과 요약: `{"status": "ok", "operations": 4, "cases": 4, "criterion": 1}`

## 10. CQ1
- 질문: 팔당댐 현재 수위는?
- 요청: `{"intent": "CQ1", "slots": {"dam": "팔당댐"}}`
- 결과 요약: `{"status": "refused", "reason": "허용되지 않은 댐: 팔당댐"}`

## 11. OUT_OF_SCOPE
- 질문: 충주댐은 왜 2020년 8월에 방류했어?
- 요청: `{"intent": "OUT_OF_SCOPE", "slots": {"reason": "방류 사유는 자료에 없음"}}`
- 결과 요약: `{"status": "refused", "reason": "범위 밖: 방류 사유는 자료에 없음"}`
