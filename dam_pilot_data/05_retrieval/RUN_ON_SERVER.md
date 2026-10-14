# 서버에서 파이프라인 실행하기 (Qwen + Neo4j)

흐름: 질문 → **LLM**이 의도(CQ1~CQ6, 여러 개 가능)와 값(JSON) 추출 → **자동화(코드)**가 입력 확인, Cypher 템플릿으로 Neo4j 조회, 측정·문서 저장소 조회, 근거 묶음 구성 → **LLM**이 근거와 판단을 나누어 답변.
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
bash dam_pilot_data/scripts/neo4j_up.sh      # 시작 + KG 적재. 마지막 줄이 "nodes: 264, rels: 418"이면 정상
```
한글이 `???`로 보이면 UTF-8 설정(`LC_ALL=C.UTF-8`, `-Dfile.encoding=UTF-8`)이 빠진 것이다. 스크립트가 설정한다.

## 3. Qwen 서빙 (OpenAI 호환 API)
- vLLM 예: `vllm serve Qwen/Qwen2.5-7B-Instruct --port 8000 --max-model-len 16384`  → `LLM_BASE_URL=http://localhost:8000/v1`
- Ollama 예: `ollama pull qwen2.5:7b-instruct` → `LLM_BASE_URL=http://localhost:11434/v1`, `LLM_MODEL=qwen2.5:7b-instruct`
- 전체 질문(CQ1~CQ6)의 근거 묶음이 길다(약 1만자). 컨텍스트가 짧은 설정이면 잘릴 수 있다. `--max-model-len 16384` 이상을 권장한다.
- Qwen3처럼 생각(thinking) 모드가 있는 모델은 `export LLM_NO_THINK=1`을 주거나, 출력의 `<think>…</think>`는 코드가 제거한다.
- 위 모델 이름은 예시이고 이 환경에서 실제 Qwen으로 시험한 적은 없다. 서버의 모델에 맞게 바꾼다.

## 4. 실행
```bash
export LLM_BASE_URL=http://localhost:8000/v1 LLM_MODEL=Qwen/Qwen3-8B LLM_NO_THINK=1 NEO4J_HOME=...
python3 dam_pilot_data/scripts/step11_pipeline.py --question "충주댐 현재 수문, 기상 데이터를 가져오고 제한수위와 비교한 후에, 이와 비슷한 수문상태일 때의 승인 및 운영 행위가 있었으면 알려줘."
python3 dam_pilot_data/scripts/step11_pipeline.py --questions-file dam_pilot_data/05_retrieval/questions_example.json
```
첫 질문은 측정자료(50만 행)를 읽느라 1~2분 걸리고 이후 질문은 몇 초다. 질문 파일 5개: 전체 질문, 제한수위와 근거, 기간 지정, 광동댐 제한수위, 범위 밖 댐(거절).
결과는 `dam_pilot_data/05_retrieval/runs/<시각>/`에 질문마다 `*_trace.json`(의도 원문, 의도 JSON, 근거 묶음, 답변)과 `*_retrieval.json`(검색 결과)로 저장된다.
`--no-answer`는 의도·검색·근거 묶음까지만 실행한다. `--mock`은 LLM 없이 배관만 점검하는 가짜 모드이고 그 결과는 성과가 아니다.

## 5. 확인할 것 (사람이 점검)
1. **의도 추출:** `*_trace.json`의 `intent_json`이 질문이 요구하는 CQ를 모두 담았는지(전체 질문은 CQ1~CQ6), 댐 이름이 정규화됐는지, 범위 밖 댐은 `intent: []`와 `reason`으로 나왔는지.
2. **근거와 판단의 분리:** 답변이 "근거"와 "판단" 두 부분으로 나뉘는지, 근거 문장마다 출처 번호가 붙었는지, 판단 문장 끝에 어느 근거에서 나왔는지 적었는지.
3. **값의 일치:** 답변의 수치가 근거 묶음의 원값과 같은지(모델이 계산한 값은 어떤 값으로 계산했는지 보였는지).
4. **지어내기:** "왜 방류했나" 같은 사유를 지어내지 않았는지, 자료에 없는 내용을 "자료에 없음"이라고 했는지, 현재 상태를 실시간이라고 단정하지 않았는지.
5. 의도 채점 스크립트(`step12_score_intents.py`)와 비교 기준선(Excel 방식)은 옛 설계(SIMILAR 등) 기준이라 이 안내에서 제외했다.

## 6. 보안 (서버에서 실행할 때)
- Neo4j는 기본값(localhost에서만 접속)을 유지한다. 인증을 끈 설정(시험용)을 쓴다면 접속 주소를 외부로 바꾸지 않는다.
- vLLM은 `--host 127.0.0.1 --api-key <비밀값>`으로 띄워 로컬에서만 받게 하고, 파이프라인에는 `LLM_API_KEY`로 같은 값을 준다. Ollama는 기본이 로컬 전용이다.
- 7687, 7474, 8000 같은 포트를 서버 방화벽에서 외부에 열지 않는다.
- 이 묶음에는 비밀 값(인증키, 토큰)이 들어 있지 않다.
