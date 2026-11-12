#!/usr/bin/env python3
"""STEP 9: 입력 확인 → KG 조회(Cypher 템플릿, Neo4j) → 외부 저장소 조회(측정자료·문서) → 근거(dict).  (자동화 코드 부분. 질문 해석과 답변은 LLM)
입력(LLM이 질문에서 뽑은 것): {"intent": ["CQ1",...,"CQ6"], "dam": "충주댐", "period": "전체" | {"at": ...} | {"start": ..., "end": ...}, "target": {"type": "approval|operation|criterion", "id": ...}(CQ6만 단독일 때)}
환경변수 NEO4J_HOME(cypher-shell 위치). stdlib만 사용.
"""
import csv, importlib.util, json, os, subprocess, sys
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__)); N = os.path.join(HERE, '..', '03_normalized')
CS = os.path.join(os.environ.get('NEO4J_HOME', ''), 'bin', 'cypher-shell')
DAMS = {'충주': '충주댐', '충주댐': '충주댐', '소양강': '소양강댐', '소양강댐': '소양강댐', '횡성': '횡성댐', '횡성댐': '횡성댐', '광동': '광동댐', '광동댐': '광동댐'}
INTENTS = ('CQ1', 'CQ2', 'CQ3', 'CQ4', 'CQ5', 'CQ6')
_s = importlib.util.spec_from_file_location('ms', os.path.join(HERE, 'measurement_store.py')); M = importlib.util.module_from_spec(_s); _s.loader.exec_module(M)
_store = None


def store():
    global _store
    if _store is None:
        _store = M.Store()
    return _store


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


# ---- 단계 1. 입력 확인 (정규화 포함)
import re, calendar

_KO = re.compile(r'^(\d{4})년(?:(\d{1,2})월(?:(\d{1,2})일(?:(\d{1,2})시(?:(\d{1,2})분)?)?)?)?$')
_ISO = re.compile(r'^(\d{4})(?:[-./](\d{1,2})(?:[-./](\d{1,2})(?:[T ](\d{1,2})(?::(\d{1,2})(?::\d{1,2}(?:\.\d+)?)?)?)?)?)?$')


def parse_t(v):
    """시점 문자열을 (시작, 끝, 단위)로 읽는다. 끝은 포함하지 않는다. 단위: year, month, day, time.
    받는 형식: 2020, 2020-08, 2020-08-02, 2020-08-02T18, 2020-08-02T18:00(:00), 2020.08.02, 2020/08/02, '2020년 8월 2일 18시'.
    형식 예시('YYYY-MM-DD')나 '내일' 같은 말은 날짜가 아니므로 ValueError."""
    if not isinstance(v, str):
        raise ValueError('시점 값이 문자열이 아님: %r' % (v,))
    t = v.strip().rstrip('Z')
    m = _ISO.match(t) or _KO.match(re.sub(r'\s+', '', t))
    if not m:
        raise ValueError('날짜로 읽을 수 없는 값 %r' % v)
    y, mo, d, h, mi = [int(x) if x is not None else None for x in m.groups()]
    if not 1900 <= y <= 2100:
        raise ValueError('연도가 범위(1900~2100) 밖 %r' % v)
    if mo is None:
        return datetime(y, 1, 1), datetime(y + 1, 1, 1), 'year'
    if d is None:
        return datetime(y, mo, 1), datetime(y, mo, 1) + timedelta(days=calendar.monthrange(y, mo)[1]), 'month'
    if h is None:
        return datetime(y, mo, d), datetime(y, mo, d) + timedelta(days=1), 'day'
    if h == 24:
        t0 = datetime(y, mo, d) + timedelta(days=1)
    else:
        t0 = datetime(y, mo, d, h, mi or 0)
    return t0, t0 + timedelta(hours=1), 'time'


def norm_period(p):
    """period를 (시작, 끝, 정리한 period)로 만든다. '전체'이면 (None, None, '전체')."""
    if p in (None, '', '전체') or (isinstance(p, dict) and (not p or set(p.values()) <= {'전체', None, ''})):
        return None, None, '전체'
    if isinstance(p, str):
        p = {'at': p}
    if not isinstance(p, dict):
        raise ValueError('period 형식 오류: %r' % (p,))
    f = lambda t: t.strftime('%Y-%m-%d') if (t.hour, t.minute) == (0, 0) else t.strftime('%Y-%m-%dT%H:%M')
    if p.get('at'):
        s_, e_, unit = parse_t(p['at'])
        if unit in ('day', 'time'):
            return s_, e_, {'at': f(s_)}
        return s_, e_, {'start': f(s_), 'end': f(e_ - timedelta(days=1))}
    if p.get('start') and p.get('end'):
        s_ = parse_t(p['start'])[0]; e0, e1, unit = parse_t(p['end'])
        e_ = e0 if unit == 'time' else e1          # 날짜만 쓴 end는 그 날(달, 해) 전체
        if e_ <= s_:
            raise ValueError('기간의 끝이 시작보다 앞섬: %s ~ %s' % (p['start'], p['end']))
        return s_, e_, {'start': f(s_), 'end': f(e0 if unit == 'time' else e_ - timedelta(days=1))}
    raise ValueError('period에 at 또는 start·end가 없음: %r' % (p,))


def check(req):
    its = req.get('intent')
    its = [its] if isinstance(its, str) else its
    if not its or any(i not in INTENTS for i in its):
        return None, '정해진 의도(CQ1~CQ6) 밖: %s' % its
    its = [i for i in INTENTS if i in its]
    out = {'intent': its}
    t = req.get('target')
    if its == ['CQ6'] and t:
        if t.get('type') not in ('approval', 'operation', 'criterion') or not t.get('id'):
            return None, 'CQ6 대상 오류'
        out['target'] = t
        return out, None
    d = req.get('dam')
    if not d:
        return None, '댐이 지정되지 않음 (충주댐, 소양강댐, 횡성댐, 광동댐 중 하나를 정해 물어야 한다)'
    dam = DAMS.get(d) if isinstance(d, str) else None
    if dam is None:
        return None, '범위 밖의 댐: %s' % (d,)
    out['dam'] = dam
    try:
        s_, e_, p = norm_period(req.get('period', '전체'))
    except Exception as e:
        return None, '시점 형식 오류: %s' % e
    out['start'], out['end'] = (s_, e_) if s_ else (datetime(1900, 1, 1), datetime(2999, 1, 1))
    out['period'] = p
    return out, None


# ---- 단계 2. KG 조회 (의도별 Cypher 템플릿)
Q_STATE = "MATCH (d:Dam {damName:$dam})-[:hasHydrometeorologicalState]->(h) RETURN h.id AS id, h.variableType AS var, h.stationCode AS code ORDER BY var"
Q_OPS = ("MATCH (o:Operation)-[:performedOnDam]->(d:Dam {damName:$dam}) WHERE o.operationTime >= datetime($s) AND o.operationTime < datetime($e) "
         "OPTIONAL MATCH (a:Approval)-[:authorizes]->(o) RETURN o.id AS op, o.operationType AS type, toString(o.operationTime) AS time, a.id AS approval ORDER BY time, op, approval")
Q_APPS = ("MATCH (a:Approval)-[:concernsDam]->(d:Dam {damName:$dam}) WHERE a.approvalTime >= date($s) AND a.approvalTime < date($e) "
          "RETURN a.id AS approval, toString(a.approvalTime) AS date, a.approvalContent AS content ORDER BY date, approval")
Q_CRI = "MATCH (c:Criterion)-[:appliesToDam]->(d:Dam {damName:$dam}) RETURN c.id AS id, c.criterionType AS type, c.criterionValue AS value, c.unit AS unit"
Q_EVI = "MATCH (x:Entity {id:$id})-[:supportedBy]->(e:EvidenceSource) RETURN e.id AS ev, e.sourceTitle AS title, e.sourceType AS type, e.sourceLocator AS locator ORDER BY ev"
Q_ONE = "MATCH (x:Entity {id:$id}) RETURN x.id AS id, labels(x) AS labels"


def evidence_of(node_id):
    return cypher(Q_EVI, id=node_id)


# ---- 단계 3. 외부 저장소 조회
_docs = None


def document(locator):
    """문서 저장소: 조회 키 = EvidenceSource.sourceLocator."""
    global _docs
    if _docs is None:
        _docs = {r['sourceLocator']: r for r in csv.DictReader(open(os.path.join(N, 'kgv4_documents.csv'), encoding='utf-8-sig'))}
    return _docs.get(locator)


def rows_out(pairs):
    return [(t.strftime('%Y-%m-%d %H:%M'), v) for t, v in pairs]


MAX_PERIOD_ROWS = 100   # 기간의 정시 행이 이보다 많으면 전부 싣지 않고 요약한다(모델 입력 한도)


def summarize(code, rows, start, end):
    """긴 기간의 정시 행을 줄인다. 원래 행에서 고른 것(처음, 마지막, 변수별 최대·최소)은 원값 그대로이고,
    개수와 강우량 합계만 코드가 계산한다."""
    num = lambda v: float(v) if v not in ('', None) else None
    S = {'n_rows': len(rows), 'first': rows_out(rows[:1]), 'last': rows_out(rows[-1:]), 'vars': {}}
    first, last = rows[0][0], rows[-1][0]
    S['n_expected'] = int((last - first).total_seconds() // 3600) + 1
    for n in M.VARS:
        vals = [(num(v[n]), t, v) for t, v in rows if num(v[n]) is not None]
        d = {'n_missing': len(rows) - len(vals)}
        if vals:
            hi = max(vals, key=lambda x: x[0]); lo = min(vals, key=lambda x: x[0])
            d['max'] = rows_out([(hi[1], hi[2])]); d['min'] = rows_out([(lo[1], lo[2])])
            if n == '강우량':
                d['sum'] = round(sum(x[0] for x in vals), 3)
        S['vars'][n] = d
    return S


def run(req):
    q, err = check(req)
    if err:
        return {'status': 'refused', 'reason': err}
    its = q['intent']
    R = {'status': 'ok', 'intent': its, 'dam': q.get('dam'), 'period': q.get('period')}
    if 'target' in q:
        t = q['target']; nid = ('APR:' if t['type'] == 'approval' else '') + str(t['id']).replace('APR:', '')
        R['evidence'] = {nid: evidence_of(nid)}
        return R
    dam = q['dam']; hs = cypher(Q_STATE, dam=dam); code = hs[0]['code']; R['station_code'] = code
    R['hms'] = hs
    ev = {}
    # CQ1: 현재 상태 = 저장된 가장 최근 시각
    if 'CQ1' in its:
        t = store().latest(code)
        R['state_now'] = {'time': t.strftime('%Y-%m-%d %H:%M'), 'rows': rows_out(store().at(code, t))}
        for h in hs:
            ev[h['id']] = evidence_of(h['id'])
    # CQ5: 운영기준 (+ 별표3 원문)
    if 'CQ5' in its:
        R['criteria'] = cypher(Q_CRI, dam=dam)
        for c in R['criteria']:
            ev[c['id']] = evidence_of(c['id'])
            c['document'] = [dict(document(e['locator']) or {}, ev=e['ev']) for e in ev[c['id']] if document(e['locator'])]
    # CQ3: 운영행위와 허가한 승인
    ops = []
    if 'CQ3' in its or 'CQ2' in its:
        ops = cypher(Q_OPS, dam=dam, s=q['start'].strftime('%Y-%m-%dT%H:%M:00'), e=q['end'].strftime('%Y-%m-%dT%H:%M:00'))
    if 'CQ3' in its:
        R['operations'] = ops
        for o in ops:
            ev[o['op']] = evidence_of(o['op'])
            if o.get('approval'):
                ev[o['approval']] = evidence_of(o['approval'])
    # CQ2: 상태. 운영행위가 함께 있으면 각 운영 시각의 상태, 없으면 기간의 정시 행
    if 'CQ2' in its:
        if 'CQ3' in its:
            seen, R['state_at_operations'] = set(), []
            for o in ops:
                if o['op'] in seen:
                    continue
                seen.add(o['op'])
                t = datetime.strptime(o['time'][:16], '%Y-%m-%dT%H:%M')
                R['state_at_operations'].append({'op': o['op'], 'time': o['time'][:16].replace('T', ' '), 'rows': rows_out(store().at(code, t))})
        else:
            rows = store().span(code, q['start'], q['end'])
            if len(rows) > MAX_PERIOD_ROWS:
                R['state_period_summary'] = summarize(code, rows, q['start'], q['end'])
            else:
                R['state_period'] = rows_out(rows)
    if 'CQ1' in its or 'CQ2' in its:
        R['data_range'] = [x.strftime('%Y-%m-%d %H:%M') for x in store().range(code)]
    # CQ4: 승인
    if 'CQ4' in its:
        R['approvals'] = cypher(Q_APPS, dam=dam, s=q['start'].strftime('%Y-%m-%d'), e=q['end'].strftime('%Y-%m-%d'))
        for a in R['approvals']:
            ev[a['approval']] = evidence_of(a['approval'])
    # CQ6: 근거 (위에서 조회한 항목 전부의 supportedBy)
    if 'CQ6' in its:
        R['evidence'] = ev
    return R


if __name__ == '__main__':
    print(json.dumps(run(json.loads(sys.argv[1])), ensure_ascii=False, indent=1, default=str))
