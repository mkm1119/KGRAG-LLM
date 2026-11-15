#!/usr/bin/env bash
# 서버에서 시연 채팅 화면을 띄운다(LLM이 실제로 답함). vLLM은 먼저 띄워 둔다.
# 사용: bash dam_pilot_data/scripts/run_demo_server.sh        (127.0.0.1:8765, 끝낼 때 Ctrl+C)
# 폴더 배치(기본값): 이 폴더와 같은 위치에 neo4j-community-5.26.0, jre21 이 있다고 가정. 다르면 NEO4J_HOME, JAVA_HOME을 먼저 export.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$HERE/../.." && pwd)"
export NEO4J_HOME="${NEO4J_HOME:-$ROOT/../neo4j-community-5.26.0}"
export JAVA_HOME="${JAVA_HOME:-$ROOT/../jre21}"
export PATH="$JAVA_HOME/bin:$PATH"
export LLM_BASE_URL="${LLM_BASE_URL:-http://localhost:8000/v1}"
export LLM_MODEL="${LLM_MODEL:-Qwen/Qwen3-32B-AWQ}"
export LLM_NO_THINK="${LLM_NO_THINK:-1}"

echo "== 1/3 vLLM 확인: $LLM_BASE_URL ($LLM_MODEL)"
curl -sf "$LLM_BASE_URL/models" | grep -q "$LLM_MODEL" || { echo "vLLM이 응답하지 않거나 모델 이름이 다릅니다. vllm.log와 LLM_MODEL을 확인하세요." >&2; exit 1; }

echo "== 2/3 Neo4j 시작과 KG 적재 (NEO4J_HOME=$NEO4J_HOME)"
[ -x "$NEO4J_HOME/bin/neo4j" ] || { echo "Neo4j가 $NEO4J_HOME 에 없습니다. NEO4J_HOME을 export 하세요." >&2; exit 1; }
bash "$HERE/neo4j_up.sh"

echo "== 3/3 시연 화면 서버 시작"
cd "$ROOT"
python3 "$HERE/demo_server.py"
