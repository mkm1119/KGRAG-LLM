#!/usr/bin/env python3
"""STEP 10: step9_retrieve.run()의 결과(dict)를 근거 묶음(텍스트)으로 만든다. stdlib만 사용.
규칙: (1) 근거는 의도별 구역으로 나눈다 (2) 항목마다 출처 번호를 붙인다 (KG 개체는 자기 id, 측정값은 [MEA:관측소코드:시각라벨]) (3) 값은 저장소 원값 그대로이고 계산한 값은 넣지 않는다.
묶음 끝에는 근거 사용 원칙 3문장을 붙인다.
"""
import re

ORDER = ['수위', '저수량', '강우량', '유입량', '총방류량', '저수율']
UNITS = {'수위': 'EL.m', '저수량': 'MCM', '강우량': 'mm', '유입량': 'CMS', '총방류량': 'CMS', '저수율': '%'}
PRINCIPLES = ('1. 위 근거에 있는 내용만 사실로 쓰고, 문장마다 출처 번호를 붙인다.\n'
              '2. 비교나 해석은 LLM의 판단임을 밝히고, 어느 근거에서 나온 판단인지 적는다.\n'
              '3. 근거에 없는 내용은 "자료에 없음"이라고 답한다.')


def mea(code, t, v):
    tag = '[MEA:%s:%s]' % (code, t.replace('-', '').replace(' ', '').replace(':', '')[:10])
    vals = ', '.join('%s %s %s' % (n, v[n] if v[n] != '' else '없음', UNITS[n]) for n in ORDER)
    return '%s %s  %s' % (tag, t, vals)


def mea_rows(code, rows):
    return [mea(code, t, v) for t, v in rows] or ['(해당 시각의 측정값 없음)']


def build(R, question=None):
    if R.get('status') != 'ok':
        return '[근거 묶음] 질의 불가: %s' % R.get('reason', '')
    its, dam, code = R['intent'], R.get('dam'), R.get('station_code')
    o = []
    if question:
        o.append('[질문] ' + question)
    o.append('[대상] %s, 기간 %s' % (dam or '(지정 항목)', R['period'] if isinstance(R.get('period'), str) else R.get('period')))
    n = 0
    if 'state_now' in R:
        n += 1
        o.append('\n[근거 %d. 현재 상태]  (CQ1) 저장된 가장 최근 시각이며 실시간이 아님' % n)
        o += mea_rows(code, R['state_now']['rows'])
    if 'criteria' in R:
        n += 1
        o.append('\n[근거 %d. 운영기준]  (CQ5)' % n)
        if not R['criteria']:
            o.append('이 댐에 적용되는 홍수기 제한수위 자료 없음 (연계운영규정 별표3에 수록되지 않음)')
        for c in R['criteria']:
            o.append('[%s] %s %s: %s %s' % (c['id'], dam, c['type'], c['value'], c['unit']))
            for d in c.get('document', []):
                o.append('[%s] %s 원문:\n%s' % (d['ev'], d['doc_title'], re.sub(r'\n\s*\n+', '\n', d['text'])))
    if 'operations' in R:
        n += 1
        o.append('\n[근거 %d. 운영행위와 허가한 승인]  (CQ3) 운영행위의 시각은 비고에 적힌 시각, 없으면 승인된 방류 시작 시각이다.' % n)
        g = {}
        for x in R['operations']:
            g.setdefault(x['op'], {'type': x['type'], 'time': x['time'][:16].replace('T', ' '), 'aps': []})
            if x.get('approval'):
                g[x['op']]['aps'].append(x['approval'])
        for oid, v in g.items():
            o.append('[%s] %s, 시각 %s' % (oid, v['type'], v['time']) + (' ← 승인 ' + ', '.join('[%s]' % a for a in v['aps']) if v['aps'] else ''))
        if not g:
            o.append('(해당 기간의 운영행위 없음)')
    if 'state_at_operations' in R:
        n += 1
        o.append('\n[근거 %d. 운영 시각의 상태]  (CQ2) 정각이 아닌 시각은 앞뒤 정시 행을 모두 준다.' % n)
        for s in R['state_at_operations']:
            o.append('[%s] %s' % (s['op'], s['time']))
            o += ['  ' + l for l in mea_rows(code, s['rows'])]
    if 'state_period' in R:
        n += 1
        o.append('\n[근거 %d. 기간의 상태]  (CQ2)' % n)
        o += mea_rows(code, R['state_period'])
    if 'approvals' in R:
        n += 1
        o.append('\n[근거 %d. 방류 승인]  (CQ4)' % n)
        for a in R['approvals']:
            o.append('[%s] 승인일 %s: %s' % (a['approval'], a['date'], a['content']))
        if not R['approvals']:
            o.append('(해당 기간의 승인 없음)')
    if 'evidence' in R:
        n += 1
        o.append('\n[근거 %d. 출처]  (CQ6)' % n)
        g = {}
        for k, evs in R['evidence'].items():
            for e in evs:
                g.setdefault(e['ev'], {'e': e, 'items': []})['items'].append(k)
        for ev_id, v in g.items():
            e = v['e']
            o.append('[%s] %s, 위치: %s  ← 근거가 되는 항목: %s' % (ev_id, e['title'], e['locator'], ', '.join('[%s]' % i for i in v['items'])))
    o.append('\n[근거 사용 원칙]\n' + PRINCIPLES)
    return '\n'.join(o)
