# 서버에서 파이프라인 실행하기 (Qwen + Neo4j)

흐름: 질문 → **LLM**이 의도·값(JSON) 추출 → 프로그램이 Cypher 템플릿으로 Neo4j 질의, 측정·문서 저장소 조회, 유클리드 거리 계산 → 근거 묶음 → **LLM**이 답변.
같은 Qwen 하나가 두 역할을 프롬프트만 바꿔 맡는다. 이 저장소의 코드는 파이썬 표준 라이브러리만 쓴다.

## 1. 준비
```bash
git clone https://github.com/mkm1119/KGRAG-LLM.git && cd KGRAG-LLM
git checkout claude/ecstatic-edison-92f1f8
```

## 2. Neo4j (KG 적재)
Java 21과 Neo4j 5.26 Community가 필요하다(Docker를 쓰면 `neo4j:5.26`도 가능하나 `neo4j_up.sh`는 로컬 설치를 가정한다).
```bash
wget https://dist.neo4j.org/neo4j-community-5.26.0-unix.tar.gz && tar xzf neo4j-community-5.26.0-unix.tar.gz
# conf/neo4j.conf 에서 인증을 끈다(시험용): dbms.security.auth_enabled=false
export NEO4J_HOME=$PWD/neo4j-community-5.26.0
bash dam_pilot_data/scripts/neo4j_up.sh      # 시작 + KG 적재. 마지막 줄이 "nodes: 273, rels: 457"이면 정상
```
한글이 `???`로 보이면 UTF-8 설정(`LC_ALL=C.UTF-8`, `-Dfile.encoding=UTF-8`)이 빠진 것이다. 스크립트가 설정한다.

## 3. Qwen 서빙 (OpenAI 호환 API)
- vLLM 예: `vllm serve Qwen/Qwen2.5-7B-Instruct --port 8000 --max-model-len 16384`  → `LLM_BASE_URL=http://localhost:8000/v1`
- Ollama 예: `ollama pull qwen2.5:7b-instruct` → `LLM_BASE_URL=http://localhost:11434/v1`, `LLM_MODEL=qwen2.5:7b-instruct`
- 통합·유사 사례 질문의 근거 묶음이 길다(약 7천자). 컨텍스트가 짧은 설정이면 잘릴 수 있다.
- Qwen3처럼 생각(thinking) 모드가 있는 모델은 `export LLM_NO_THINK=1`을 주거나, 출력의 `<think>…</think>`는 코드가 제거한다.
- 위 모델 이름은 예시이고 이 환경에서 실제 Qwen으로 시험한 적은 없다. 서버의 모델에 맞게 바꾼다.

## 4. 실행
```bash
export LLM_BASE_URL=http://localhost:8000/v1 LLM_MODEL=Qwen/Qwen2.5-7B-Instruct NEO4J_HOME=...
python3 dam_pilot_data/scripts/step11_pipeline.py --question "2020년 8월에 충주댐에서 어떤 방류 조작이 있었어?"
python3 dam_pilot_data/scripts/step11_pipeline.py --questions-file dam_pilot_data/05_retrieval/questions_example.json --format tagged
python3 dam_pilot_data/scripts/step11_pipeline.py --questions-file dam_pilot_data/05_retrieval/questions_example.json --format json
```
결과는 `dam_pilot_data/05_retrieval/runs/<시각>/`에 질문마다 `*_trace.json`(의도 원문, 의도 JSON, 근거 묶음, 답변)과 `*_retrieval.json`(검색 결과)로 저장된다.
`--no-answer`는 의도·검색·근거 묶음까지만 실행한다. `--mock`은 LLM 없이 배관만 점검하는 가짜 모드이고 그 결과는 성과가 아니다.

## 5. 확인할 것
1. **의도 분류:** `python3 dam_pilot_data/scripts/step12_score_intents.py <실행 폴더> dam_pilot_data/05_retrieval/questions_example.json` → 의도와 댐이 기대와 맞는지. 실행에 쓴 질문 파일과 같은 파일로 채점해야 한다(질문 번호로 짝을 짓는다). (질문 19개, 표현이 다양하고 범위 밖 질문 5개 포함. 기대값은 사람이 정한 것).
2. **답변 점검(사람):** 각 답변이 근거 묶음의 수치와 같은지, 근거 번호를 붙였는지, "왜"에 대해 사유를 지어내지 않았는지, 자료가 없을 때 "자료에 없음"이라고 했는지, 실시간이라고 단정하지 않았는지.
3. **형식 비교:** 같은 질문 파일을 `--format tagged`와 `--format json`으로 각각 돌려 답변 차이를 비교한다.
4. **비교 기준선(Excel 방식)은 이 안내에 포함하지 않았다.** 같은 Qwen에게 표 데이터를 그대로 주는 조건은 별도로 만들어야 한다.

## 6. 보안 (서버에서 실행할 때)
- Neo4j는 기본값(localhost에서만 접속)을 유지한다. 인증을 끈 설정(시험용)을 쓴다면 접속 주소를 외부로 바꾸지 않는다.
- vLLM은 `--host 127.0.0.1 --api-key <비밀값>`으로 띄워 로컬에서만 받게 하고, 파이프라인에는 `LLM_API_KEY`로 같은 값을 준다. Ollama는 기본이 로컬 전용이다.
- 7687, 7474, 8000 같은 포트를 서버 방화벽에서 외부에 열지 않는다.
- 이 묶음에는 비밀 값(인증키, 토큰)이 들어 있지 않다.

## 7. 여러 관계를 따라가며 비교하는 질문 세트
`05_retrieval/questions_multi.json`(10개): 현재 상태와 제한수위 비교(CURRENT), 비슷한 과거 사례와 승인·방류·근거 비교(SIMILAR), 기간 안의 승인된 방류량 대비 실제 방류량과 제한수위 비교(INTEGRATED), 자료가 없는 경우(광동댐 제한수위), 지원하지 않는 질문(여러 댐 비교). 차이와 비율은 프로그램이 `<계산값>`으로 계산해 근거 묶음에 넣고, LLM은 그 값을 인용만 한다.
