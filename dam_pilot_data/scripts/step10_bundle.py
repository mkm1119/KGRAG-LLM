#!/usr/bin/env python3
"""STEP 10 (R3): step9_retrieve.run()의 결과(dict)를 LLM이 읽는 근거 묶음으로 만든다. stdlib만 사용.
형식 두 가지: 'tagged'(태그로 섹션 구분 + 표, 항목마다 근거 번호) / 'json'(구조 그대로). 같은 결과를 두 형식으로 만들어 비교할 수 있다.
"""
import json, re

UNITS = {'수위': 'EL.m', '저수량': 'MCM', '강우량': 'mm', '유입량': 'CMS', '총방류량': 'CMS', '저수율': '%'}
ORDER = ['수위', '저수량', '강우량', '유입량', '총방류량', '저수율']


def fmt(x):
    """측정값 표시: 소수 3자리까지(부동소수 잡음 제거)."""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return str(x)
    return ('%.3f' % v).rstrip('0').rstrip('.')


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
            out.append('| %s | ' % t + ' | '.join(fmt(v[n]) if v[n] != '' else '없음' for n in names) + ' |')
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
        lines += ['제한수위의 근거: ' + l for l in ev_lines(c['evidence'][:1])]
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


def fl(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def limit_of(crits):
    for c in crits or []:
        if c.get('type') == '홍수기 제한수위' and fl(c.get('value')) is not None:
            return fl(c['value'])
    return None


def amounts(rows):
    out = []
    for r in rows:
        m = re.search(r'접수방류량\s*([\d,\.]+)', r.get('approval_content', '') or '')
        key = (r.get('approval'), m.group(1) if m else None, r.get('approval_date', ''))
        if m and key not in out:
            out.append(key)
    return out


def derived(window, limit, rows, label):
    """프로그램이 계산한 비교 값(LLM은 계산하지 않는다). 창 범위와 승인일을 함께 적어 오해를 막는다."""
    L = []
    rs = (window or {}).get('rows') or []
    if not rs:
        return ''
    w0, w1 = rs[0][0], rs[-1][0]
    lv = [(t, fl(v.get('수위'))) for t, v in rs if fl(v.get('수위')) is not None]
    dq = [(t, fl(v.get('총방류량'))) for t, v in rs if fl(v.get('총방류량')) is not None]
    if lv:
        t, m = max(lv, key=lambda x: x[1])
        L.append('창 내 최고 수위 %s EL.m (%s)' % (fmt(m), t) + (', 제한수위 %s EL.m 대비 %+.2f m' % (limit, m - limit) if limit is not None else ', 제한수위 자료 없음'))
    if dq:
        t, m = max(dq, key=lambda x: x[1])
        L.append('창 내 최대 총방류량 %s CMS (%s)' % (fmt(m), t))
        late = []
        for ap, a, ad in amounts(rows):
            av = fl(a.replace(',', ''))
            if not av:
                continue
            if ad and ad > w1[:10]:
                late.append('[%s](승인일 %s, 접수방류량 %s ㎥/s)' % (ap, ad, a))
            else:
                L.append('승인 [%s] (승인일 %s) 접수방류량 %s ㎥/s 대비 창 내 최대 총방류량 %.1f%%' % (ap, ad, a, 100 * m / av))
        if late:
            L.append('다음 승인은 승인일이 창(%s까지)보다 늦어 창 시점의 상한이 아니므로 비율을 계산하지 않았다: %s' % (w1[:10], ', '.join(late)))
    return '<계산값 대상="%s" 창="%s ~ %s (행위 시각 앞 6시간~뒤 12시간)" 출처="프로그램 계산, 측정 시각 라벨 기준">\n%s\n</계산값>' % (label, w0, w1, '\n'.join(L)) if L else ''


def tagged(R):
    it, dam = R['intent'], R.get('dam')
    o = ['<근거묶음 질문유형="%s"%s>' % (it, ' 댐="%s"' % dam if dam else '')]
    o.append('<안내>이 묶음의 자료만으로 답한다. 운영행위의 시각은 승인된 방류 시작 시각 또는 측정 방류량 변화에서 정한 연구자 지정 임시 기준이며 실제 수행의 확정이 아니다. 측정 시각은 1시간 단위 라벨이다.</안내>')
    if it == 'CQ1':
        o.append('<현재상태 기준시각="%s" 비고="저장된 가장 최근 시각이며 실시간이 아님">\n%s\n</현재상태>' % (tm(R['as_of']), table(R['state'])))
    elif it == 'CURRENT':
        o.append('<현재상태 기준시각="%s" 비고="저장된 가장 최근 시각이며 실시간이 아님">\n%s\n</현재상태>' % (tm(R['as_of']), table(R['state'])))
        lim = limit_of(R['criterion']); r0 = R['state']['rows'][0][1] if R['state'].get('rows') else {}
        if lim is not None and fl(r0.get('수위')) is not None:
            o.append('<계산값 대상="현재" 출처="프로그램 계산">현재 수위 %s EL.m, 제한수위 %s EL.m 대비 %+.2f m</계산값>' % (r0['수위'], lim, fl(r0['수위']) - lim))
        o.append(crit_block(R['criterion'], dam))
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
            rows_ = [x for x in R['operations'] if x['op'] == c['operation']]
            d_ = derived(c['state_window'], limit_of(R['criterion']), rows_, c['operation'])
            if d_:
                o.append(d_)
            o += ['<방류의 근거 운영행위="%s" 비고="승인 기록(이 방류를 허가한 승인)">%s</방류의 근거>' % (c['operation'], l) for l in ev_lines(c['approval_evidence'])]
        o.append(crit_block(R['criterion'], dam))
    elif it == 'SIMILAR':
        s = R['similar']
        cur = s['current']
        o.append('<현재상태 기준시각="%s" 비고="저장된 가장 최근 시각이며 실시간이 아님">수위 %s EL.m, 유입량 %s CMS, 총방류량 %s CMS, 강우량 %s mm</현재상태>' % (tm(s['as_of']), fmt(cur.get('수위')), fmt(cur.get('유입량')), fmt(cur.get('총방류량')), fmt(cur.get('강우량'))))
        lim = limit_of(R['criterion'])
        if lim is not None and fl(cur.get('수위')) is not None:
            o.append('<계산값 대상="현재" 출처="프로그램 계산">현재 수위 %s EL.m, 제한수위 %s EL.m 대비 %+.2f m</계산값>' % (cur['수위'], lim, fl(cur['수위']) - lim))
        o.append('<유사도 방식="수위·유입량을 그 댐 전체 기록의 최솟값~최댓값으로 0~1 정규화한 벡터의 유클리드 거리(작을수록 비슷함, 연구자 지정 임시 기준)" 후보사례수="%d">거리 0은 완전히 같음이고 값이 클수록 현재와 상태가 다르다. 사례끼리의 거리 차이와 현재 상태와의 차이를 함께 보고 판단한다.</유사도>' % s['n_candidates'])
        for i, c in enumerate(s['cases'], 1):
            st = c['state_at_op']
            o.append('<유사사례 순위="%d" 시각="%s" 거리="%s" 당시 수위="%s EL.m" 유입량="%s CMS" 총방류량="%s CMS">' % (i, tm(c['time']), c['euclidean'], fmt(st['수위']), fmt(st['유입량']), fmt(st['총방류량'])))
            cur_l, cur_i, cs_l, cs_i = fl(cur.get('수위')), fl(cur.get('유입량')), fl(st.get('수위')), fl(st.get('유입량'))
            parts = []
            if None not in (cur_l, cs_l):
                parts.append('당시(행위 시각) 수위 %s EL.m는 현재 수위보다 %+.2f m' % (fmt(cs_l), cs_l - cur_l))
                if lim is not None:
                    parts.append('당시 수위의 제한수위 대비 %+.2f m' % (cs_l - lim))
            if None not in (cur_i, cs_i) and cur_i > 0:
                parts.append('당시 유입량 %s CMS는 현재 유입량의 %.1f배' % (fmt(cs_i), cs_i / cur_i))
            if parts:
                o.append('<계산값 대상="현재 대비 사례 %d" 출처="프로그램 계산">%s</계산값>' % (i, '; '.join(parts)))
            for r in c['rows']:
                o.append('운영행위 [%s] %s / 허가한 승인 [%s] 승인일 %s: %s' % (r['op'], r['type'], r['approval'], r['approval_date'], r['approval_content']))
            o.append('당시상태(앞 6시간~뒤 12시간):\n' + table(c['state_window']))
            d_ = derived(c['state_window'], lim, c['rows'], c['operations'][0] if c.get('operations') else '')
            if d_:
                o.append(d_)
            o += ev_lines(c['approval_evidence'])
            o.append('</유사사례>')
        o.append(crit_block(R['criterion'], dam))
    o.append('</근거묶음>')
    return '\n'.join(o)


def build(R, fmt='tagged'):
    if R.get('status') != 'ok':
        return '<근거묶음 상태="질의 불가">%s</근거묶음>' % R.get('reason', '') if fmt == 'tagged' else json.dumps(R, ensure_ascii=False)
    return tagged(R) if fmt == 'tagged' else json.dumps(R, ensure_ascii=False, indent=1, default=str)
