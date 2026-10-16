#!/usr/bin/env bash
# 서버에서 파이프라인(질문 -> 의도 -> 검색 -> 근거 묶음 -> 답변)을 한 번에 실행한다.
# 사전 조건: (1) vLLM이 이미 떠 있음 (2) Neo4j가 설치돼 있고 NEO4J_HOME이 설정됨
# 사용: NEO4J_HOME=<neo4j 폴더> bash scripts/run_qwen.sh [--no-answer] [질문파일.json]
#   --no-answer: 의도 추출, 검색, 근거 묶음까지만 실행(LLM 답변 생략)
#   질문파일을 생략하면 05_retrieval/questions_example.json(질문 5개)을 쓴다.
# 환경변수(선택): LLM_BASE_URL(기본 http://localhost:8000/v1), LLM_MODEL(기본 Qwen/Qwen3-32B-AWQ), LLM_NO_THINK(기본 1), LLM_API_KEY
set -e
: "${NEO4J_HOME:?NEO4J_HOME 필요 (예: export NEO4J_HOME=\$PWD/neo4j-community-5.26.0)}"
HERE="$(cd "$(dirname "$0")" && pwd)"
export LLM_BASE_URL="${LLM_BASE_URL:-http://localhost:8000/v1}"
export LLM_MODEL="${LLM_MODEL:-Qwen/Qwen3-32B-AWQ}"
export LLM_NO_THINK="${LLM_NO_THINK:-1}"
EXTRA=""
if [ "$1" = "--no-answer" ]; then EXTRA="--no-answer"; shift; fi
QF="${1:-$HERE/../05_retrieval/questions_example.json}"

echo "== 1/3 vLLM 확인: $LLM_BASE_URL, 모델 $LLM_MODEL"
AUTH=()
[ -n "$LLM_API_KEY" ] && AUTH=(-H "Authorization: Bearer $LLM_API_KEY")
if ! curl -sf "${AUTH[@]}" "$LLM_BASE_URL/models" >/dev/null; then
  echo "vLLM이 응답하지 않습니다. 서버를 먼저 띄우세요." >&2; exit 1
fi
curl -s "${AUTH[@]}" "$LLM_BASE_URL/models" | grep -q "$LLM_MODEL" || echo "경고: 서빙 중인 모델 이름에 '$LLM_MODEL'이 없습니다. LLM_MODEL을 확인하세요."

echo "== 2/3 Neo4j 시작과 KG 적재"
bash "$HERE/neo4j_up.sh"

echo "== 3/3 파이프라인 실행: $QF $EXTRA"
python3 "$HERE/step11_pipeline.py" $EXTRA --questions-file "$QF"
echo "결과: $HERE/../05_retrieval/runs/ 아래 가장 최근 폴더"
