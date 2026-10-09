#!/usr/bin/env bash
# Neo4j를 시작하고 03_normalized/kgv3_load.cypher로 KG를 (다시) 적재한다. 사용: NEO4J_HOME=<neo4j 폴더> bash scripts/neo4j_up.sh
set -e
: "${NEO4J_HOME:?NEO4J_HOME 필요}"
export LC_ALL=C.UTF-8 LANG=C.UTF-8 JAVA_TOOL_OPTIONS="-Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 -Dstderr.encoding=UTF-8 -Dsun.jnu.encoding=UTF-8"
HERE="$(cd "$(dirname "$0")" && pwd)"
"$NEO4J_HOME/bin/neo4j" status >/dev/null 2>&1 || "$NEO4J_HOME/bin/neo4j" start >/dev/null 2>&1
for i in $(seq 1 40); do "$NEO4J_HOME/bin/cypher-shell" -a bolt://localhost:7687 "RETURN 1" >/dev/null 2>&1 && break; sleep 3; done
CS="$NEO4J_HOME/bin/cypher-shell -a bolt://localhost:7687 --format plain"
$CS "MATCH (n) DETACH DELETE n" >/dev/null 2>&1
$CS -f "$HERE/../03_normalized/kgv3_load.cypher" >/dev/null 2>&1
echo "nodes: $($CS 'MATCH (n:Entity) RETURN count(n)' 2>/dev/null | tail -1), rels: $($CS 'MATCH ()-[r]->() RETURN count(r)' 2>/dev/null | tail -1)"
