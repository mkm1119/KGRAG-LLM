#!/usr/bin/env python3
"""STEP 9 (R1~R2): 의도(JSON) -> Cypher 템플릿 -> Neo4j 질의 -> 측정 저장소 / 문서 저장소 조회 -> 근거 묶음(dict).
LLM 의도 분류는 이 파일 밖(05_retrieval/intent_prompt.md)에서 한다. 여기서는 정해진 의도와 값만 받는다.
환경변수 NEO4J_HOME(cypher-shell 위치), stdlib만 사용.
"""
import csv, importlib.util, json, os, re, subprocess, sys
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__)); N = os.path.join(HERE, '..', '03_normalized')
CS = os.path.join(os.environ.get('NEO4J_HOME', ''), 'bin', 'cypher-shell')
DAMS = {'충주': '충주댐', '충주댐': '충주댐', '소양강': '소양강댐', '소양강댐': '소양강댐', '횡성': '횡성댐', '횡성댐': '횡성댐', '광동': '광동댐', '광동댐': '광동댐'}
INTENTS = {'CQ1', 'CQ2', 'CQ3', 'CQ4', 'CQ5', 'CQ6', 'INTEGRATED', 'OUT_OF_SCOPE'}
_spec = importlib.util.spec_from_file_location('r3b', os.path.join(HERE, 'step3b_retrieval.py'))
r3b = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(r3b)
_ms = None


def ms():
    global _ms
    if _ms is None:
        _ms = r3b.Measurement()
    return _ms


def cypher(query, **params):
    env = dict(os.environ, LC_ALL='C.UTF-8', LANG='C.UTF-8', JAVA_TOOL_OPTIONS='-Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 -Dstderr.encoding=UTF-8 -Dsun.jnu.encoding=UTF-8')
    cmd = [CS, '-a', 'bolt://localhost:7687', '--format', 'plain']
    for k, v in params.items():
        cmd += ['--param', '%s => %s' % (k, json.dumps(v, ensure_ascii=False))]
    out = subprocess.run(cmd + [query], capture_output=True, text=True, env=env).stdout
    lines = [l for l in out.splitlines() if l and not l.startswith('Picked up')]
    if not lines:
        return []
    rd = list(csv.reader(lines, skipinitialspace=True, escapechar='\\')); head = rd[0]
    return [dict(zip(head, r)) for r in rd[1:]]


def parse_t(s, end=False):
    s = s.replace(' ', 'T')
    if len(s) == 10:
        d = datetime.strptime(s, '%Y-%m-%d')
        return d + timedelta(days=1) if end else d
    return datetime.strptime(s, '%Y-%m-%dT%H:%M')


def span(time):
    if 'at' in time:
        a = time['at']
        return (parse_t(a), parse_t(a, True)) if len(a) == 10 else (parse_t(a), parse_t(a) + timedelta(hours=1))
    return parse_t(time['start']), parse_t(time['end'], True)


def validate(req):
    it = req.get('intent'); sl = req.get('slots', {})
    if it not in INTENTS:
        return None, '정해진 의도 목록에 없는 의도: %s' % it
    if it == 'OUT_OF_SCOPE':
        return None, '범위 밖: %s' % sl.get('reason', '')
    if it == 'CQ6':
        t = sl.get('target', {})
        if t.get('type') not in ('approval', 'operation', 'criterion', 'state'):
            return None, 'target.type 오류'
        if t['type'] in ('criterion', 'state') and DAMS.get(t.get('dam')) is None:
            return None, '허용되지 않은 댐: %s' % t.get('dam')
        if t['type'] in ('approval', 'operation') and not t.get('id'):
            return None, 'target.id 없음'
        return {'intent': it, 'target': dict(t, dam=DAMS.get(t.get('dam')))}, None
    dam = DAMS.get(sl.get('dam'))
    if dam is None:
        return None, '허용되지 않은 댐: %s' % sl.get('dam')
    out = {'intent': it, 'dam': dam}
    if it in ('CQ2', 'CQ3', 'CQ4', 'INTEGRATED'):
        try:
            out['start'], out['end'] = span(sl['time'])
        except Exception as e:
            return None, '시점 형식 오류: %s' % e
    return out, None


# ---- 측정 저장소 (KG의 HMS.stationCode가 조회 키)
def state_vars(dam):
    return cypher("MATCH (d:Dam {damName:$dam})-[:hasHydrometeorologicalState]->(h) RETURN h.variableType AS var, h.stationCode AS code ORDER BY var", dam=dam)


def measure(dam, start, end, max_rows=48):
    vars_ = state_vars(dam); code = vars_[0]['code']; names = [v['var'] for v in vars_]
    t = start.replace(minute=0, second=0, microsecond=0) + (timedelta(hours=1) if start.minute else timedelta(0))
    rows = []
    while t < end:
        v = ms().d.get((code, t))
        if v is not None:
            rows.append((t.strftime('%Y-%m-%d %H:%M'), {k: v[k] for k in names}))
        t += timedelta(hours=1)
    res = {'station_code': code, 'variables': names, 'rows': rows if len(rows) <= max_rows else None, 'n_rows': len(rows)}
    if len(rows) > max_rows:
        res['summary'] = {}
        for k in names:
            xs = [(r3b.fnum(v[k]), tt) for tt, v in rows if r3b.fnum(v[k]) is not None]
            if xs:
                res['summary'][k] = {'min': min(xs)[0], 'max': max(xs)[0], 'first': xs[0][0], 'last': xs[-1][0], 'n': len(xs)}
    return res


def latest(dam):
    code = state_vars(dam)[0]['code']
    t = max(t for (c, t) in ms().d if c == code)
    return t, measure(dam, t, t + timedelta(hours=1))


# ---- 문서 저장소 / 승인 원자료
_chunks = None


def chunk(cid):
    global _chunks
    if _chunks is None:
        _chunks = {r['chunk_id']: r for r in csv.DictReader(open(os.path.join(N, 'kgv3_chunks.csv'), encoding='utf-8-sig'))}
    return _chunks.get(cid)


EV_Q = "MATCH (x:Entity {id:$id})-[:supportedBy]->(e:EvidenceSource) RETURN e.id AS ev, e.sourceTitle AS title, e.sourceType AS type, e.sourceLocator AS locator, e.chunkId AS chunkId ORDER BY ev"


def evidence(node_id):
    out = []
    for e in cypher(EV_Q, id=node_id):
        d = dict(e)
        if e['chunkId'] and e['chunkId'] != 'null':
            c = chunk(e['chunkId']); d['text'] = c['text'] if c else None
        out.append(d)
    return out


def run(req):
    q, err = validate(req)
    if err:
        return {'status': 'refused', 'reason': err}
    it, dam = q['intent'], q.get('dam')
    R = {'status': 'ok', 'intent': it, 'dam': dam}
    if it == 'CQ1':
        t, m = latest(dam); R['as_of'] = str(t); R['state'] = m
    elif it == 'CQ2':
        R['state'] = measure(dam, q['start'], q['end'])
    elif it == 'CQ3' or it == 'INTEGRATED':
        ops = cypher("MATCH (o:Operation)-[:performedOnDam]->(d:Dam {damName:$dam}) WHERE o.operationTime >= datetime($s) AND o.operationTime < datetime($e) "
                     "OPTIONAL MATCH (a:Approval)-[:authorizes]->(o) RETURN o.id AS op, o.operationType AS type, toString(o.operationTime) AS time, a.id AS approval, a.approvalTime AS approval_date, a.approvalContent AS approval_content ORDER BY time, op",
                     dam=dam, s=q['start'].strftime('%Y-%m-%dT%H:%M:00'), e=q['end'].strftime('%Y-%m-%dT%H:%M:00'))
        R['operations'] = ops
        if it == 'INTEGRATED':
            R['cases'] = []
            for o in ops:
                t0 = datetime.strptime(o['time'][:16], '%Y-%m-%dT%H:%M')
                R['cases'].append({'operation': o['op'], 'state_window': measure(dam, t0 - timedelta(hours=6), t0 + timedelta(hours=13)),
                                   'operation_evidence': evidence(o['op']), 'approval_evidence': evidence(o['approval'])})
            R['criterion'] = criterion(dam)
    elif it == 'CQ4':
        R['approvals'] = cypher("MATCH (a:Approval)-[:concernsDam]->(d:Dam {damName:$dam}) WHERE a.approvalTime >= date($s) AND a.approvalTime < date($e) "
                                "RETURN a.id AS approval, toString(a.approvalTime) AS date, a.approvalContent AS content ORDER BY date, approval",
                                dam=dam, s=q['start'].strftime('%Y-%m-%d'), e=q['end'].strftime('%Y-%m-%d'))
    elif it == 'CQ5':
        R['criterion'] = criterion(dam)
    elif it == 'CQ6':
        t = q['target']
        if t['type'] == 'approval': R['evidence'] = evidence('APR:' + str(t['id']).replace('APR:', ''))
        elif t['type'] == 'operation': R['evidence'] = evidence(t['id'])
        elif t['type'] == 'criterion': R['criterion'] = criterion(t['dam'])
        else:
            R['evidence'] = []
            for h in cypher("MATCH (d:Dam {damName:$dam})-[:hasHydrometeorologicalState]->(h) RETURN h.id AS id", dam=t['dam']):
                R['evidence'] += evidence(h['id'])
    return R


def criterion(dam):
    cs = cypher("MATCH (c:Criterion)-[:appliesToDam]->(d:Dam {damName:$dam}) RETURN c.id AS id, c.criterionType AS type, c.criterionValue AS value, c.unit AS unit", dam=dam)
    for c in cs:
        c['evidence'] = evidence(c['id'])
    return cs or []


if __name__ == '__main__':
    print(json.dumps(run(json.loads(sys.argv[1])), ensure_ascii=False, indent=1, default=str))
