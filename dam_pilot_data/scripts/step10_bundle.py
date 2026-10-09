#!/usr/bin/env python3
"""STEP 10 (R3): step9_retrieve.run()의 결과(dict)를 LLM이 읽는 근거 묶음으로 만든다. stdlib만 사용.
형식 두 가지: 'tagged'(태그로 섹션 구분 + 표, 항목마다 근거 번호) / 'json'(구조 그대로). 같은 결과를 두 형식으로 만들어 비교할 수 있다.
"""
import json, re

UNITS = {'수위': 'EL.m', '저수량': 'MCM', '강우량': 'mm', '유입량': 'CMS', '총방류량': 'CMS', '저수율': '%'}
ORDER = ['수위', '저수량', '강우량', '유입량', '총방류량', '저수율']


def tm(s):
    return re.sub(r':00Z?$', '', str(s).replace('T', ' ').replace('Z', ''))[:16]


def table(state):
    if not state:
        return '(측정값 없음)'
    names = [v for v in ORDER if v in state['variables']]
    out = []
    if state.get('rows') is not None:
        out.append('| 시각 | ' + ' | '.join('%s(%s)' % (v, UNITS[v]) for v in names) + ' |')
        out.append('|' + '---|' * (len(names) + 1))
        for t, v in state['rows']:
            out.append('| %s | ' % t + ' | '.join(str(v[n]) if v[n] != '' else '없음' for n in names) + ' |')
    else:
        out.append('(%d개 시각을 요약함) | 변수 | 최소 | 최대 | 처음 | 마지막 |' % state['n_rows'])
        for n in names:
            s = state['summary'].get(n)
            if s:
                out.append('| %s(%s) | %s | %s | %s | %s |' % (n, UNITS[n], s['min'], s['max'], s['first'], s['last']))
    return '\n'.join(out)


def ev_lines(evs):
    seen, out = set(), []
    for e in evs or []:
        if e['ev'] in seen:
            continue
        seen.add(e['ev'])
        out.append('[%s] %s, 위치: %s' % (e['ev'], e['title'], e['locator']))
    return out


def crit_block(crits, dam):
    if not crits:
        return '<운영기준 댐="%s">이 댐에 적용되는 홍수기 제한수위 자료 없음 (연계운영규정 별표3에 수록되지 않음)</운영기준>' % dam
    out = []
    for c in crits:
        lines = ['<운영기준 id="%s" 댐="%s">%s: %s %s' % (c['id'], dam, c['type'], c['value'], c['unit'])]
        cur = [e for e in c['evidence'] if e['locator'] == '별표 3']
        hist = [e for e in c['evidence'] if e['locator'].startswith('별표 3 / 시행')]
        if cur and cur[0].get('text'):
            key = dam.replace('댐', '')
            keep = [l for l in cur[0]['text'].splitlines() if key in l.replace(' ', '') or '구 분' in l or '주)' in l or '표시의 댐' in l or '시범' in l]
            lines.append('근거 원문 발췌(별표3):\n' + '\n'.join(keep))
        if hist:
            lines.append('같은 값이 적용된 별표3 연혁 판: %d개 (%s ~ %s)' % (len(hist), hist[0]['locator'].split('시행 ')[-1], hist[-1]['locator'].split('시행 ')[-1]))
        lines += ev_lines(c['evidence'][:1])
        out.append('\n'.join(lines) + '\n</운영기준>')
    return '\n'.join(out)


def ops_block(ops):
    if not ops:
        return '(해당 기간의 운영행위 없음)'
    g = {}
    for o in ops:
        g.setdefault(o['op'], {'type': o['type'], 'time': tm(o['time']), 'aps': []})['aps'].append(o)
    out = []
    for oid, v in g.items():
        out.append('<운영행위 id="%s" 종류="%s" 시각="%s">' % (oid, v['type'], v['time']))
        for a in v['aps']:
            if a.get('approval'):
                out.append('허가한 승인 [%s] 승인일 %s: %s' % (a['approval'], a.get('approval_date', ''), a.get('approval_content', '')))
        out.append('</운영행위>')
    return '\n'.join(out)


def tagged(R):
    it, dam = R['intent'], R.get('dam')
    o = ['<근거묶음 질문유형="%s"%s>' % (it, ' 댐="%s"' % dam if dam else '')]
    o.append('<안내>이 묶음의 자료만으로 답한다. 운영행위의 시각은 승인된 방류 시작 시각 또는 측정 방류량 변화에서 정한 연구자 지정 임시 기준이며 실제 수행의 확정이 아니다. 측정 시각은 1시간 단위 라벨이다.</안내>')
    if it == 'CQ1':
        o.append('<현재상태 기준시각="%s" 비고="저장된 가장 최근 시각이며 실시간이 아님">\n%s\n</현재상태>' % (tm(R['as_of']), table(R['state'])))
    elif it == 'CQ2':
        o.append('<과거상태>\n%s\n</과거상태>' % table(R['state']))
    elif it == 'CQ3':
        o.append(ops_block(R['operations']))
    elif it == 'CQ4':
        for a in R['approvals']:
            o.append('<승인 id="%s" 승인일="%s">%s</승인>' % (a['approval'], a['date'], a['content']))
        if not R['approvals']:
            o.append('(해당 기간의 승인 없음)')
    elif it == 'CQ5':
        o.append(crit_block(R['criterion'], dam))
    elif it == 'CQ6':
        if 'criterion' in R:
            o.append(crit_block(R['criterion'], dam))
        else:
            o += ['<근거>' + l + '</근거>' for l in ev_lines(R['evidence'])]
    elif it == 'INTEGRATED':
        o.append(ops_block(R['operations']))
        for c in R['cases']:
            o.append('<당시상태 운영행위="%s" 범위="행위 시각 앞 6시간~뒤 12시간">\n%s\n</당시상태>' % (c['operation'], table(c['state_window'])))
            o += ['<근거 운영행위="%s">%s</근거>' % (c['operation'], l) for l in ev_lines(c['approval_evidence'])]
        o.append(crit_block(R['criterion'], dam))
    elif it == 'SIMILAR':
        s = R['similar']
        cur = s['current']
        o.append('<현재상태 기준시각="%s" 비고="저장된 가장 최근 시각이며 실시간이 아님">수위 %s EL.m, 유입량 %s CMS, 총방류량 %s CMS, 강우량 %s mm</현재상태>' % (tm(s['as_of']), cur.get('수위'), cur.get('유입량'), cur.get('총방류량'), cur.get('강우량')))
        o.append('<유사도 방식="수위·유입량을 그 댐 전체 기록의 최솟값~최댓값으로 0~1 정규화한 벡터의 유클리드 거리(작을수록 비슷함, 연구자 지정 임시 기준)" 후보사례수="%d">거리 0은 완전히 같음이고 값이 클수록 현재와 상태가 다르다. 사례끼리의 거리 차이와 현재 상태와의 차이를 함께 보고 판단한다.</유사도>' % s['n_candidates'])
        for i, c in enumerate(s['cases'], 1):
            st = c['state_at_op']
            o.append('<유사사례 순위="%d" 시각="%s" 거리="%s" 당시 수위="%s EL.m" 유입량="%s CMS" 총방류량="%s CMS">' % (i, tm(c['time']), c['euclidean'], st['수위'], st['유입량'], st['총방류량']))
            for r in c['rows']:
                o.append('운영행위 [%s] %s / 허가한 승인 [%s] 승인일 %s: %s' % (r['op'], r['type'], r['approval'], r['approval_date'], r['approval_content']))
            o.append('당시상태(앞 6시간~뒤 12시간):\n' + table(c['state_window']))
            o += ev_lines(c['approval_evidence'])
            o.append('</유사사례>')
        o.append(crit_block(R['criterion'], dam))
    o.append('</근거묶음>')
    return '\n'.join(o)


def build(R, fmt='tagged'):
    if R.get('status') != 'ok':
        return '<근거묶음 상태="질의 불가">%s</근거묶음>' % R.get('reason', '') if fmt == 'tagged' else json.dumps(R, ensure_ascii=False)
    return tagged(R) if fmt == 'tagged' else json.dumps(R, ensure_ascii=False, indent=1, default=str)
