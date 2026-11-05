#!/usr/bin/env python3
"""11/26 시연용 채팅 서버. 브라우저에서 질문하면 step11 파이프라인(의도 추출 LLM → KG 검색 → 근거 묶음 → 답변 LLM)을
단계별로 보여 주고, 답변의 출처 번호를 누르면 원문(승인 기록 행, 측정값 행, 규정 원문, KG Entity)을 보여 준다. stdlib만 사용.

모드
  live   : 실제 실행. 환경변수 LLM_BASE_URL, LLM_MODEL, (LLM_API_KEY, LLM_NO_THINK), NEO4J_HOME 필요 (RUN_ON_SERVER.md와 같음)
  replay : LLM·Neo4j 없이 미리 받아 둔 실행 기록(*_trace.json, *_retrieval.json)을 재생. 인터넷이 안 될 때와 화면 점검용.

사용
  python3 scripts/demo_server.py                       # live, 127.0.0.1:8765
  python3 scripts/demo_server.py --replay 05_retrieval/server_runs_20261016/084150_answer_q1-q5
노트북에서 보기(서버 포트를 외부에 열지 않음): ssh -L 8765:127.0.0.1:8765 <서버> 후 노트북 브라우저에서 http://localhost:8765
질문과 결과는 05_retrieval/demo_logs/<날짜>/에 남는다(현장 질문 수집용).
"""
import argparse, csv, glob, importlib.util, json, os, re, sys, threading, time, traceback
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
N = os.path.join(ROOT, '03_normalized'); DEMO = os.path.join(ROOT, 'demo'); LOGS = os.path.join(ROOT, '05_retrieval', 'demo_logs')

CQ = {'CQ1': '현재 수문 상태', 'CQ2': '과거 수문 상태', 'CQ3': '과거 운영행위', 'CQ4': '과거 방류 승인', 'CQ5': '홍수기 제한수위', 'CQ6': '공식 근거'}
PATH = {'CQ1': ['Dam → hasHydrometeorologicalState → 수문·기상 상태', '측정 저장소(가장 최근 시각)'],
        'CQ2': ['운영행위의 시각 또는 기간', '측정 저장소(그 시각의 행)'],
        'CQ3': ['운영행위 → performedOnDam → Dam', '승인 → authorizes → 운영행위'],
        'CQ4': ['승인 → concernsDam → Dam'],
        'CQ5': ['운영기준 → appliesToDam → Dam', '운영기준 → supportedBy → 근거', '문서 저장소(규정 원문)'],
        'CQ6': ['조회한 Entity → supportedBy → 근거']}
DAMS = ['충주댐', '소양강댐', '횡성댐', '광동댐']
EXAMPLES = ['충주댐 지금 수위랑 유입량 알려줘',
            '소양강댐의 홍수기 제한수위는 얼마이고 그 근거는 무엇인가?',
            '2020년 8월 충주댐 방류 승인과 운영행위, 그때의 수문 상태를 알려줘.',
            '횡성댐 현재 수위가 제한수위보다 높아?',
            '2011년 7월 소양강댐 방류 승인 내역',
            '팔당댐의 현재 수위는?']


def load(name, fname):
    s = importlib.util.spec_from_file_location(name, os.path.join(HERE, fname)); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


# ------------------------------------------------------------------ 출처 원문
class Sources:
    def __init__(self, store):
        rd = lambda f: list(csv.DictReader(open(os.path.join(N, f), encoding='utf-8-sig')))
        self.ent = {e['entity_id']: e for e in rd('kgv4_entities.csv')}
        self.prop = {}
        for p in rd('kgv4_properties.csv'):
            self.prop.setdefault(p['entity_id'], []).append((p['property'], p['value']))
        self.rel = {}
        for r in rd('kgv4_relations.csv'):
            self.rel.setdefault(r['subject'], []).append((r['relation'], r['object']))
        self.apr = {r['순차번호']: r for r in rd('approval_records_clean.csv')}
        self.doc = {d['sourceLocator']: d for d in rd('kgv4_documents.csv')}
        self.store = store

    def approval_row(self, seq):
        r = self.apr.get(seq)
        if not r:
            return None
        keys = ['순차번호', '관측소코드', '관측소명', '승인년월일시분', '방류시작시간', '접수방류량', '접수일자', '비고']
        return {'caption': '원본: %s (%s), 원본 파일의 %s번째 행' % (r['original_file_name'], r['source_organization'], r['row_number_in_file']),
                'rows': [[k, r[k] or '(빈칸)'] for k in keys]}

    def get(self, sid):
        sid = sid.strip('[]')
        out = {'id': sid, 'blocks': []}
        m = re.fullmatch(r'MEA:(\d+):(\d{10})', sid)
        if m:
            code, lab = m.groups()
            t = datetime(int(lab[:4]), int(lab[4:6]), int(lab[6:8]), int(lab[8:10]))
            v = self.store.d.get((code, t)) if self.store else None
            out['title'] = '측정값 %s %s' % (code, t.strftime('%Y-%m-%d %H:%M'))
            out['kind'] = '측정 저장소 (KG 밖 CSV, K-water MyWater 시간자료)'
            if v is None:
                out['blocks'].append({'text': '저장소에 이 시각의 값이 없습니다.'})
            else:
                units = {'수위': 'EL.m', '저수량': 'MCM', '강우량': 'mm', '유입량': 'CMS', '총방류량': 'CMS', '저수율': '%'}
                out['blocks'].append({'caption': 'DAM_CD = %s, 시각 = %s 인 행' % (code, t.strftime('%Y-%m-%d %H:%M')),
                                      'rows': [[k, '%s %s' % (x, units[k]) if x != '' else '(없음)'] for k, x in v.items()]})
                out['blocks'].append({'text': 'KG의 수문·기상 상태 Entity(HMS:%s:…)가 가진 stationCode %s와 시각으로 이 행을 찾았습니다.' % (code, code)})
            return out
        e = self.ent.get(sid)
        if not e:
            out['title'] = sid; out['kind'] = '알 수 없는 출처 번호'
            out['blocks'].append({'text': 'KG에 이 번호의 Entity가 없습니다.'})
            return out
        out['title'] = '%s  %s' % (sid, e['label']); out['kind'] = 'KG Entity · Class %s' % e['class']
        out['blocks'].append({'caption': 'Data Property', 'rows': [[k, v] for k, v in self.prop.get(sid, [])]})
        rels = self.rel.get(sid, [])
        if rels:
            out['blocks'].append({'caption': 'Relation (이 Entity에서 나가는 선)', 'rows': [[r, '%s  %s' % (o, self.ent.get(o, {}).get('label', ''))] for r, o in rels]})
        seq = None
        if sid.startswith(('APR:', 'EVI:AP:')):
            seq = sid.split(':')[-1]
        elif sid.startswith('OPR:'):
            seq = sid.split(':')[1]
        if seq:
            a = self.approval_row(seq)
            if a:
                a['caption'] = '승인 기록 원본 행 (순차번호 %s) — %s' % (seq, a['caption'])
                out['blocks'].append(a)
        if sid.startswith(('CRI:', 'EVI:LAW')):
            d = self.doc.get('별표 3')
            if d:
                out['blocks'].append({'caption': '문서 저장소: %s' % d['doc_title'], 'pre': re.sub(r'\n\s*\n+', '\n', d['text'])})
        return out


# ------------------------------------------------------------------ 실행
def summary(res):
    s = []
    if 'state_now' in res:
        s.append('현재 상태: %s 측정값' % res['state_now']['time'])
    if 'criteria' in res:
        s.append('운영기준 %d건' % len(res['criteria']))
    if 'operations' in res:
        s.append('운영행위 %d건' % len({o['op'] for o in res['operations']}))
    if 'approvals' in res:
        s.append('방류 승인 %d건' % len(res['approvals']))
    if 'state_at_operations' in res:
        s.append('운영 시각 측정값 %d건' % len(res['state_at_operations']))
    if 'state_period' in res:
        s.append('기간 측정값 %d행' % len(res['state_period']))
    if 'evidence' in res:
        s.append('출처 %d건' % len({e['ev'] for v in res['evidence'].values() for e in v}))
    return s


def guide(reason):
    return ('이 질문에는 답하지 않았습니다. (%s)\n\n이 시연은 아래 범위에서 답합니다.\n'
            '- 대상 댐: 충주댐, 소양강댐, 횡성댐, 광동댐 (K-water 다목적댐)\n'
            '- 물어볼 수 있는 것: 현재(저장된 마지막 시각) 수문 상태, 과거 시점의 수문 상태, 과거 방류 승인과 운영행위, 홍수기 제한수위와 근거 규정\n'
            '- 한 번에 댐 하나씩 물어봐 주세요. 방류 사유처럼 자료에 없는 내용은 답하지 않습니다.' % reason)


def intent_view(j):
    if not j:
        return None
    p = j.get('period')
    if isinstance(p, dict):
        p = p.get('at') or '%s ~ %s' % (p.get('start', ''), p.get('end', ''))
    return {'intents': ['%s %s' % (i, CQ.get(i, '')) for i in j.get('intent') or []], 'dam': j.get('dam'), 'period': p,
            'paths': [x for i in j.get('intent') or [] for x in PATH.get(i, [])], 'reason': j.get('reason')}


class Engine:
    def __init__(self, replay_dirs):
        self.replay = {}
        if replay_dirs:
            for d in replay_dirs:
                for f in sorted(glob.glob(os.path.join(d, '*_trace.json'))):
                    tr = json.load(open(f, encoding='utf-8'))
                    if not tr.get('answer'):
                        continue
                    rf = f.replace('_trace.json', '_retrieval.json')
                    tr['_res'] = json.load(open(rf, encoding='utf-8')) if os.path.exists(rf) else {}
                    self.replay.setdefault(self.key(tr['question']), tr)
            self.P = None
            ms = load('ms', 'measurement_store.py')
            t0 = time.time(); self.store = ms.Store(); print('측정 저장소 읽음 %.1f초' % (time.time() - t0))
        else:
            self.P = load('p11', 'step11_pipeline.py')
            t0 = time.time(); self.store = self.P.r9.store(); print('측정 저장소 미리 읽음 %.1f초' % (time.time() - t0))
        self.src = Sources(self.store)
        self.latest = {c: self.store.latest(c).strftime('%Y-%m-%d %H:%M') for c in ('1003110',)}

    @staticmethod
    def key(q):
        return re.sub(r'[\s.?!,]', '', q)

    def examples(self):
        if self.P:
            return EXAMPLES
        return [t['question'] for t in self.replay.values()]

    def run(self, q, emit):
        t0 = time.time(); log = {'question': q, 'time': datetime.now().isoformat(timespec='seconds'), 'mode': 'live' if self.P else 'replay'}
        el = lambda: round(time.time() - t0, 1)
        emit('stage', {'key': 'intent'})
        if self.P:
            raw, j = self.P.intent_llm(q)
        else:
            tr = self.replay.get(self.key(q))
            if not tr:
                emit('answer', {'text': '오프라인 재생 모드입니다. 미리 받아 둔 질문만 보여 드릴 수 있습니다. 왼쪽 예시 질문을 눌러 주세요.', 'refused': True})
                emit('done', {'seconds': el()}); return log
            time.sleep(0.8); raw, j = tr['intent_raw'], tr['intent_json']
        log['intent_json'] = j
        emit('intent', dict(intent_view(j) or {}, seconds=el()))
        if not j or not j.get('intent'):
            emit('answer', {'text': guide((j or {}).get('reason') or '질문의 의도를 해석하지 못함'), 'refused': True})
            emit('done', {'seconds': el()}); return log
        emit('stage', {'key': 'search'})
        if self.P:
            res = self.P.r9.run(j)
        else:
            time.sleep(0.6); res = tr['_res'] or {'status': tr.get('retrieval_status'), 'reason': tr.get('retrieval_reason')}
        log['retrieval_status'] = res.get('status')
        if res.get('status') != 'ok':
            emit('search', {'items': [], 'seconds': el()})
            emit('answer', {'text': guide(res.get('reason', '')), 'refused': True})
            emit('done', {'seconds': el()}); return log
        emit('search', {'items': summary(res), 'seconds': el()})
        emit('stage', {'key': 'bundle'})
        bundle = self.P.r10.build(res, q) if self.P else tr['bundle']
        log['bundle'] = bundle
        emit('bundle', {'text': bundle, 'seconds': el()})
        emit('stage', {'key': 'answer'})
        if self.P:
            ans = self.P.answer_llm(q, bundle)
        else:
            time.sleep(1.2); ans = tr['answer']
        log['answer'] = ans
        emit('answer', {'text': ans})
        log['seconds'] = el()
        emit('done', {'seconds': el()})
        return log


# ------------------------------------------------------------------ HTTP
class H(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.0'

    def log_message(self, fmt, *a):
        pass

    def send(self, code, body, ctype):
        b = body.encode('utf-8') if isinstance(body, str) else body
        self.send_response(code); self.send_header('Content-Type', ctype); self.send_header('Content-Length', str(len(b)))
        self.send_header('Cache-Control', 'no-store'); self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        u = urlparse(self.path); qs = parse_qs(u.query)
        if u.path in ('/', '/index.html'):
            return self.send(200, open(os.path.join(DEMO, 'index.html'), encoding='utf-8').read(), 'text/html; charset=utf-8')
        if u.path == '/api/config':
            return self.send(200, json.dumps({'mode': 'live' if ENGINE.P else 'replay', 'examples': ENGINE.examples(), 'dams': DAMS,
                                              'latest': ENGINE.latest.get('1003110')}, ensure_ascii=False), 'application/json')
        if u.path == '/api/source':
            return self.send(200, json.dumps(ENGINE.src.get(qs.get('id', [''])[0]), ensure_ascii=False), 'application/json')
        if u.path == '/api/ask':
            q = (qs.get('q', [''])[0] or '').strip()[:300]
            self.send_response(200); self.send_header('Content-Type', 'text/event-stream; charset=utf-8'); self.send_header('Cache-Control', 'no-store'); self.end_headers()
            lock = threading.Lock()

            def emit(ev, data):
                with lock:
                    self.wfile.write(('event: %s\ndata: %s\n\n' % (ev, json.dumps(data, ensure_ascii=False))).encode('utf-8')); self.wfile.flush()
            try:
                if not q:
                    emit('answer', {'text': '질문을 입력해 주세요.', 'refused': True}); emit('done', {'seconds': 0}); return
                log = ENGINE.run(q, emit)
                d = os.path.join(LOGS, datetime.now().strftime('%Y%m%d')); os.makedirs(d, exist_ok=True)
                json.dump(log, open(os.path.join(d, datetime.now().strftime('%H%M%S_%f') + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            except (BrokenPipeError, ConnectionResetError):
                pass
            except Exception as e:
                traceback.print_exc()
                try:
                    emit('error', {'text': '처리 중 오류가 났습니다: %s' % e}); emit('done', {'seconds': 0})
                except Exception:
                    pass
            return
        self.send(404, 'not found', 'text/plain')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--host', default='127.0.0.1'); ap.add_argument('--port', type=int, default=8765)
    ap.add_argument('--replay', help='재생할 실행 기록 폴더(쉼표로 여러 개)')
    a = ap.parse_args()
    if a.host not in ('127.0.0.1', 'localhost'):
        print('주의: %s로 열면 같은 네트워크의 다른 기기에서도 접속할 수 있습니다.' % a.host)
    ENGINE = Engine(a.replay.split(',') if a.replay else None)
    print('시연 서버: http://%s:%d  (모드: %s)' % (a.host, a.port, 'live' if ENGINE.P else 'replay'))
    ThreadingHTTPServer((a.host, a.port), H).serve_forever()
