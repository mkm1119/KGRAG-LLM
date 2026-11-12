#!/usr/bin/env python3
"""STEP 10: step9_retrieve.run()의 결과(dict)를 근거 묶음(텍스트)으로 만든다. stdlib만 사용.
규칙: (1) 근거는 의도별 구역으로 나눈다 (2) 항목마다 출처 번호를 붙인다 (KG 개체는 자기 id, 측정값은 [MEA:관측소코드:시각라벨]) (3) 값은 저장소 원값 그대로이고 계산한 값은 넣지 않는다.
묶음 끝에는 근거 사용 원칙 3문장을 붙인다.
"""
import re

ORDER = ['수위', '저수량', '강우량', '유입량', '총방류량', '저수율']
UNITS = {'수위': 'EL.m', '저수량': 'MCM', '강우량': 'mm', '유입량': 'CMS', '총방류량': 'CMS', '저수율': '%'}
SCOPE = ('■ 이 시스템에 있는 자료: 댐 지점의 시간 측정값 6종(수위, 저수량, 강우량, 유입량, 총방류량, 저수율), 방류 승인 기록, 승인에서 나온 운영행위(방류), '
         '홍수기 제한수위(충주댐, 소양강댐, 횡성댐). 그 밖의 항목(계획홍수위, 상시만수위, 발전 방류량, 수문 개도, 하류 수위, 예측값, 계획, 절차 등)은 없다.')


def period_text(p):
    if isinstance(p, dict):
        return p['at'] if 'at' in p else '%s ~ %s' % (p.get('start'), p.get('end'))
    return str(p)


PRINCIPLES = ('1. 위 근거에 있는 내용만 사실로 쓰고, 문장마다 출처 번호를 붙인다. 출처 번호는 대괄호 안의 번호([MEA:...], [OPR:...], [APR:...], [CRI:...] 등)뿐이다. 구역 이름(CQ1, 근거 1)은 출처 번호가 아니다.\n'
              '2. 비교나 해석은 LLM의 판단임을 밝히고, 어느 근거에서 나온 판단인지 적는다.\n'
              '3. 근거에 없는 내용은 "자료에 없음"이라고 답한다.')


def fmt(x):
    """값 표시: 저장소 원값 그대로 쓰되, 부동소수 표기 잡음(0.5736666666666667)만 소수 4자리로 정리한다. 값을 바꾸거나 계산하지 않는다."""
    try:
        f = float(x)
    except (TypeError, ValueError):
        return str(x)
    return str(x) if len(str(x)) <= 9 else ('%.4f' % f).rstrip('0').rstrip('.')


def mea(code, t, v):
    tag = '[MEA:%s:%s]' % (code, t.replace('-', '').replace(' ', '').replace(':', '')[:10])
    vals = ', '.join('%s %s %s' % (n, fmt(v[n]) if v[n] != '' else '없음', UNITS[n]) for n in ORDER)
    return '%s %s  %s' % (tag, t, vals)


def mea_rows(code, rows):
    return [mea(code, t, v) for t, v in rows] or ['(해당 시각의 측정값 없음)']


def build(R, question=None):
    if R.get('status') != 'ok':
        return '■ 질의 불가: %s' % R.get('reason', '')
    its, dam, code = R['intent'], R.get('dam'), R.get('station_code')
    o = []
    if question:
        o.append('■ 질문: ' + question)
    o.append('■ 대상: %s, 기간 %s' % (dam or '(지정 항목)', period_text(R.get('period'))))
    if R.get('data_range'):
        o.append('■ 저장된 측정자료의 범위: %s ~ %s (시간 단위, 댐 지점). 이 범위 밖의 시각은 자료가 없다.' % tuple(R['data_range']))
    o.append(SCOPE)
    n = 0
    if 'state_now' in R:
        n += 1
        o.append('\n■ 근거 %d. 현재 상태 (CQ1 구역) 저장된 가장 최근 시각이며 실시간이 아님' % n)
        o += mea_rows(code, R['state_now']['rows'])
    if 'criteria' in R:
        n += 1
        o.append('\n■ 근거 %d. 운영기준 (CQ5 구역)' % n)
        if not R['criteria']:
            o.append('이 댐에 적용되는 홍수기 제한수위 자료 없음 (연계운영규정 별표3에 수록되지 않음)')
        for c in R['criteria']:
            o.append('[%s] %s %s: %s %s' % (c['id'], dam, c['type'], c['value'], c['unit']))
            for d in c.get('document', []):
                o.append('[%s] %s 원문:\n%s' % (d['ev'], d['doc_title'], re.sub(r'\n\s*\n+', '\n', d['text'])))
    if 'operations' in R:
        n += 1
        o.append('\n■ 근거 %d. 운영행위와 허가한 승인 (CQ3 구역) 운영행위의 시각은 비고에 적힌 시각, 없으면 승인된 방류 시작 시각이다.' % n)
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
        o.append('\n■ 근거 %d. 운영 시각의 상태 (CQ2 구역) 정각이 아닌 시각은 앞뒤 정시 행을 모두 준다.' % n)
        g = {}
        for s_ in R['state_at_operations']:   # 같은 시각의 운영행위는 측정 행을 한 번만 보인다
            g.setdefault(s_['time'], {'ops': [], 'rows': s_['rows']})['ops'].append(s_['op'])
        for t, v in g.items():
            o.append('%s %s' % (', '.join('[%s]' % x for x in v['ops']), t))
            o += ['  ' + l for l in mea_rows(code, v['rows'])]
    if 'state_period' in R:
        n += 1
        o.append('\n■ 근거 %d. 기간의 상태 (CQ2 구역)' % n)
        o += mea_rows(code, R['state_period']) if R['state_period'] else ['(해당 기간의 측정값 없음)']
    if 'state_period_summary' in R:
        n += 1
        S = R['state_period_summary']
        o.append('\n■ 근거 %d. 기간의 상태 요약 (CQ2 구역) 정시 행이 %d개라 전부 싣지 않았다. 아래 행은 원래 행에서 고른 것이고 값은 원값 그대로다.' % (n, S['n_rows']))
        o.append('처음 행: ' + mea_rows(code, S['first'])[0])
        o.append('마지막 행: ' + mea_rows(code, S['last'])[0])
        for v in ORDER:
            d = S['vars'][v]
            if 'max' not in d:
                o.append('%s: 값이 있는 행 없음' % v); continue
            o.append('%s 최대 행: %s' % (v, mea_rows(code, d['max'])[0]))
            o.append('%s 최소 행: %s' % (v, mea_rows(code, d['min'])[0]))
        o.append('코드가 센 값(출처 번호 없음. "코드가 계산한 값"이라고 밝히고 쓴다): 처음~마지막 사이 정시 %d개 중 저장된 행 %d개, 빠진 시각 %d개; 값이 빈 행 수 %s; 강우량 합계 %s mm'
                 % (S['n_expected'], S['n_rows'], S['n_expected'] - S['n_rows'], ', '.join('%s %d' % (v, S['vars'][v]['n_missing']) for v in ORDER), S['vars']['강우량'].get('sum', '없음')))
        o.append('위에 없는 시각의 값, 평균, 추세는 이 묶음으로 답할 수 없다. 필요하면 기간을 4일 이내로 좁혀 다시 물어야 한다.')
    if 'approvals' in R:
        n += 1
        o.append('\n■ 근거 %d. 방류 승인 (CQ4 구역)' % n)
        for a in R['approvals']:
            o.append('[%s] 승인일 %s: %s' % (a['approval'], a['date'], a['content']))
        if not R['approvals']:
            o.append('(해당 기간의 승인 없음)')
    if 'evidence' in R:
        n += 1
        o.append('\n■ 근거 %d. 출처 (CQ6 구역)' % n)
        g = {}
        for k, evs in R['evidence'].items():
            for e in evs:
                g.setdefault(e['ev'], {'e': e, 'items': []})['items'].append(k)
        for ev_id, v in g.items():
            e = v['e']
            o.append('[%s] %s, 위치: %s  ← 근거가 되는 항목: %s' % (ev_id, e['title'], e['locator'], ', '.join('[%s]' % i for i in v['items'])))
    o.append('\n■ 근거 사용 원칙\n' + PRINCIPLES)
    return '\n'.join(o)
