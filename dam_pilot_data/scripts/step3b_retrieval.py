#!/usr/bin/env python3
"""STEP 3B: KG v2 + 문서 저장소 + 측정자료 저장소 하이브리드 검색 (B안: 시각으로 상태를 잇는 검색 단계) 및 표 기반 대조.

- KG 경로: Operation → Dam → HydrometeorologicalState(stationCode) → 측정자료 저장소(시각 창), Dam ← Criterion, 각 항목 → EvidenceSource → 문서 청크
- 표 기반 대조: 승인 CSV / 비고 분류표 / 기준표를 조인 키로 직접 필터 (KG 미사용)
산출: 03_normalized/step3b_retrieval_results.csv, step3b_bundles.md
LLM 답변 단계 입력(근거 묶음)에는 정답(표 기반 값)을 넣지 않는다.
"""
import csv, gzip, os, re, collections
from datetime import datetime, timedelta

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
N = os.path.join(ROOT, '03_normalized')
CODES = {'1003110': '충주댐', '1003611': '충주조정지', '1012110': '소양강댐', '1006110': '횡성댐', '1001210': '광동댐'}
VARS = {'수위': 'DATA1_수위(EL.m)', '저수량': 'DATA2_저수량(MCM)', '강우량': 'DATA3_강우량(mm)',
        '유입량': 'DATA4_유입량(CMS)', '총방류량': 'DATA6_총방류량(CMS)', '저수율': 'DATA7_저수율(%)'}
UNITS = {'수위': 'EL.m', '저수량': 'MCM', '강우량': 'mm', '유입량': 'CMS', '총방류량': 'CMS', '저수율': '%'}


def rd(p):
    return list(csv.DictReader(open(os.path.join(N, p), encoding='utf-8-sig')))


def label_time(s):
    """MyWater SDATE 'YYYYMMDDHH' (HH=01..24, 시각 의미 미확정) -> datetime. HH=24는 다음날 00시."""
    return datetime(int(s[:4]), int(s[4:6]), int(s[6:8])) + timedelta(hours=int(s[8:10]))


def to_dt(s):
    return datetime.strptime(s.replace('T', ' ')[:16], '%Y-%m-%d %H:%M')


class KG:
    def __init__(self):
        self.cls, self.label, self.props = {}, {}, collections.defaultdict(dict)
        for r in rd('kgv2_entities.csv'):
            self.cls[r['entity_id']], self.label[r['entity_id']] = r['class'], r['label']
        for r in rd('kgv2_properties.csv'):
            self.props[r['entity_id']][r['property']] = r['value']
        self.out, self.inv = collections.defaultdict(lambda: collections.defaultdict(list)), collections.defaultdict(lambda: collections.defaultdict(list))
        self.rel_origin = {}
        for r in rd('kgv2_relations.csv'):
            self.out[r['subject']][r['relation']].append(r['object'])
            self.inv[r['object']][r['relation']].append(r['subject'])
            self.rel_origin[(r['subject'], r['relation'], r['object'])] = r['origin']
        self.prov = {r['item']: r for r in rd('kgv2_provenance.csv')}
        self.chunks = {r['chunk_id']: r for r in rd('kgv2_chunks.csv')}

    def dam_of_code(self, code):
        return 'DAM:' + code

    def operations(self, code, start=None, end=None, otype=None):
        res = []
        for op in self.inv['DAM:' + code]['performedOnDam']:
            t = to_dt(self.props[op]['operationTime'])
            if start and t < start:
                continue
            if end and t >= end:
                continue
            if otype and self.props[op]['operationType'] != otype:
                continue
            res.append(op)
        return sorted(res, key=lambda o: self.props[o]['operationTime'])

    def approvals_via_operations(self, code, start=None, end=None):
        """Approval은 Dam에 직접 연결되지 않아 Operation을 거쳐야만 도달한다."""
        seen = []
        for op in self.operations(code):
            for ap in self.inv[op]['authorizes']:
                d = datetime.strptime(self.props[ap]['approvalTime'], '%Y-%m-%d')
                if (start and d < start) or (end and d >= end):
                    continue
                if ap not in seen:
                    seen.append(ap)
        return seen

    def criteria(self, code):
        return self.inv['DAM:' + code]['appliesToDam']

    def evidence(self, eid):
        out = []
        for ev in self.out[eid]['supportedBy']:
            p = self.props[ev]
            out.append({'id': ev, 'title': p['sourceTitle'], 'type': p['sourceType'], 'locator': p['sourceLocator']})
        return out

    def chunk_for_locator(self, locator):
        m = re.match(r'별표 (\d+)$', locator)
        if m:
            return self.chunks.get('LAW:별표' + m.group(1))
        return None


class Measurement:
    """측정자료 저장소: MyWater 시간자료(2021~) + 승인 연계 구간(2019~2020, 방류시작 -6h~+12h만)."""

    def __init__(self):
        self.d = {}
        for r in csv.DictReader(gzip.open(os.path.join(N, 'kwater_mywater_hydr_H_wide.csv.gz'), 'rt', encoding='utf-8-sig')):
            if r['DAM_CD'] in CODES:
                self.d[(r['DAM_CD'], label_time(r['SDATE_raw']))] = {v: r[c] for v, c in VARS.items()}
        cases = {r['case_id']: r for r in rd('linkage_pilot_cases.csv')}
        off = [c for c in rd('linkage_pilot_measurement_extract.csv')[0].keys() if c.startswith('offset')][0]
        for r in rd('linkage_pilot_measurement_extract.csv'):
            code = cases[r['case_id']]['관측소코드']
            k = (code, label_time(r['SDATE_raw']))
            self.d.setdefault(k, {v: r[c] for v, c in VARS.items()})
        self.cover = collections.defaultdict(lambda: [None, None, 0])
        for (code, t) in self.d:
            c = self.cover[code]; c[2] += 1
            c[0] = t if c[0] is None or t < c[0] else c[0]
            c[1] = t if c[1] is None or t > c[1] else c[1]

    def window(self, code, t, before=6, after=12):
        rows = []
        for h in range(-before, after + 1):
            tt = t + timedelta(hours=h)
            if (code, tt) in self.d:
                rows.append((h, tt, self.d[(code, tt)]))
        return rows


def fnum(x):
    try:
        return float(x)
    except Exception:
        return None


def state_summary(win, var):
    vals = [(h, fnum(r[var])) for h, _, r in win if fnum(r[var]) is not None]
    if not vals:
        return None
    pre = [v for h, v in vals if h <= 0]
    return {'n': len(vals), 'at_start': next((v for h, v in vals if h == 0), None), 'before_min': min(pre) if pre else None,
            'max': max(v for _, v in vals), 'min': min(v for _, v in vals), 'last': vals[-1][1]}


def op_bundle(kg, ms, op, before=6, after=12):
    """Operation에서 출발해 승인·댐·기준·상태(시각 창)·근거를 모은다."""
    p = kg.props[op]
    t = to_dt(p['operationTime'])
    dam = kg.out[op]['performedOnDam'][0]
    code = dam.split(':')[1]
    b = {'operation': {'id': op, 'type': p['operationType'], 'time': p['operationTime'], 'dam': kg.label[dam]},
         'approvals': [], 'criteria': [], 'states': {}, 'evidence': [], 'chunks': [], 'computed': [], 'notes': []}
    for ap in kg.inv[op]['authorizes']:
        ap_p = kg.props[ap]
        b['approvals'].append({'id': ap, 'approvalTime': ap_p['approvalTime'], 'content': ap_p['approvalContent']})
        b['evidence'] += kg.evidence(ap)
    b['evidence'] += [e for e in kg.evidence(op) if e['id'] not in [x['id'] for x in b['evidence']]]
    win = ms.window(code, t, before, after)
    hmss = kg.out[dam]['hasHydrometeorologicalState']
    for h in hmss:
        var = kg.props[h]['variableType']
        s = state_summary(win, var)
        if s:
            b['states'][var] = s
    if not win:
        b['notes'].append('측정자료 저장소에 이 시각 전후(%d~+%dh) 자료가 없음 (저장소 범위: %s)' % (
            -before, after, ', '.join('%s~%s' % (v[0].date(), v[1].date()) for k, v in ms.cover.items() if k == code)))
    for c in kg.criteria(code):
        cp = kg.props[c]
        b['criteria'].append({'id': c, 'type': cp['criterionType'], 'value': cp['criterionValue'], 'unit': cp['unit']})
        for ev in kg.evidence(c):
            b['evidence'].append(ev)
            ch = kg.chunk_for_locator(ev['locator'])
            if ch and ch['chunk_id'] not in [x['chunk_id'] for x in b['chunks']]:
                b['chunks'].append(ch)
        if t.year < 2026:
            b['notes'].append('기준값 %s는 현행 규정(시행 2026-07-08) 별표3 값이며, 운영행위 당시(%d년)의 기준과 같은지는 확인되지 않음' % (cp['criterionValue'], t.year))
        if 'max' in b['states'].get('수위', {}) and cp['criterionType'] == '홍수기 제한수위':
            lv = b['states']['수위']
            b['computed'].append('창 안 수위 최대 %.2f EL.m, 최소 %.2f EL.m; 홍수기 제한수위 %s EL.m 대비 최대 %+.2f m (검색 단계의 단순 계산)' % (
                lv['max'], lv['min'], cp['criterionValue'], lv['max'] - float(cp['criterionValue'])))
            b['notes'].append('홍수기는 6월 21일~9월 20일(제2조)')
    return b


def fmt_bundle(q, bs, extra=''):
    L = ['### %s %s' % (q['id'], q['text']), '']
    if extra:
        L += [extra, '']
    for b in bs:
        o = b['operation']
        L.append('- 운영행위: %s / %s / %s (id %s)' % (o['dam'], o['type'], o['time'], o['id']))
        for a in b['approvals']:
            L.append('  - 승인 %s: 승인일 %s; %s' % (a['id'], a['approvalTime'], a['content']))
        for v, s in b['states'].items():
            L.append('  - 상태 %s(%s): 시작시각 %s, 시작 전 최소 %s, 창 최대 %s, 창 최소 %s, 창 마지막 %s (n=%d)' % (
                v, UNITS[v], s['at_start'], s['before_min'], s['max'], s['min'], s['last'], s['n']))
        for c in b['criteria']:
            L.append('  - 기준 %s: %s %s %s' % (c['id'], c['type'], c['value'], c['unit']))
        for c in b['computed']:
            L.append('  - 계산: ' + c)
        for n in b['notes']:
            L.append('  - 유의: ' + n)
        L.append('  - 근거: ' + '; '.join('%s[%s %s]' % (e['id'], e['type'], e['locator']) for e in b['evidence']))
        for ch in b['chunks']:
            L.append('  - 문서 청크 %s (%s):' % (ch['chunk_id'], ch['locator']))
            L += ['    > ' + ln for ln in ch['text'].split('\n') if ln.strip()][:40]
    L.append('')
    return '\n'.join(L)


# ---------------- 표 기반 대조(KG 미사용) ----------------
def tb_approvals(code, start, end):
    res = []
    for r in rd('approval_records_hrfco_raw_fields.csv'):
        if r['관측소코드'] == code:
            d = datetime.strptime(r['승인년월일시분'][:10], '%Y-%m-%d')
            if start <= d < end:
                res.append(r['순차번호'])
    return res


def tb_ops(code, start, end, otype=None):
    res = []
    for r in rd('operation_from_remarks_5dams.csv'):
        if r['operation_created'] == 'Y' and (otype is None or r['operationType'] == otype):
            t = to_dt(r['operationTime'])
            nm = {'1003110': '충주', '1003611': '충주조정지', '1012110': '소양강', '1006110': '횡성', '1001210': '광동'}[code]
            if r['댐'] == nm and start <= t < end:
                res.append(r['순차번호'])
    return res


def main():
    kg, ms = KG(), Measurement()
    D = datetime
    results, bundles = [], ['# STEP 3B 근거 묶음 (LLM 답변 단계 입력)', '', '각 묶음은 KG 경로와 시각 기반 검색으로 모은 근거만 담는다. 정답(표 기반 값)은 포함하지 않는다.', '',
               '공통 유의: 운영행위(Operation)는 승인 비고(자유 문장)에서 규칙으로 분류한 연구용 구성이며 실제 수행이 확인된 기록이 아니다. 측정 시각 표기(01~24시)의 의미가 확정되지 않아 ±1시간 차이가 있을 수 있다.', '']

    def rec(qid, text, kind, truth, kgres, note=''):
        truth, kgres = sorted(set(truth)), sorted(set(kgres))
        miss = [x for x in truth if x not in kgres]
        results.append({'id': qid, 'question': text, 'type': kind, 'table_n': len(truth), 'kg_n': len(kgres),
                        'kg_recall': ('%.2f' % (1 - len(miss) / len(truth))) if truth else '', 'missing_in_kg': ' '.join(miss), 'note': note})

    # Q01 기준 조회
    q = {'id': 'Q01', 'text': '충주댐의 홍수기 제한수위는 얼마이며 근거는 무엇인가?'}
    crit = kg.criteria('1003110')
    L = ['### Q01 ' + q['text'], '']
    for c in crit:
        cp = kg.props[c]; L.append('- 기준 %s: %s %s %s' % (c, cp['criterionType'], cp['criterionValue'], cp['unit']))
        for ev in kg.evidence(c):
            L.append('  - 근거 %s[%s %s]' % (ev['id'], ev['type'], ev['locator']))
            ch = kg.chunk_for_locator(ev['locator'])
            if ch:
                L.append('  - 문서 청크 %s:' % ch['chunk_id']); L += ['    > ' + x for x in ch['text'].split('\n') if x.strip()][:40]
    bundles.append('\n'.join(L) + '\n')
    truth = [r['criterion_id(연구용 임시ID)'] for r in rd('criterion_list.csv') if r['applies_to_facility_per_source'].strip() == '충주댐' and '제한수위' in r['criterion_type']]
    rec('Q01', q['text'], '기준 조회(1홉+문서)', ['CRI:' + x for x in truth], crit, '기준값과 근거 청크 연결')

    # Q02 운영행위 목록
    q = {'id': 'Q02', 'text': '소양강댐에서 2020년 8월에 수행된 운영행위는 무엇인가?'}
    ops = kg.operations('1012110', D(2020, 8, 1), D(2020, 9, 1))
    bundles.append('### Q02 %s\n\n' % q['text'] + '\n'.join('- %s (id %s) / %s / %s (근거 %s)' % (kg.label[o], o, kg.props[o]['operationType'], kg.props[o]['operationTime'], ', '.join(e['id'] for e in kg.evidence(o))) for o in ops) + '\n')
    rec('Q02', q['text'], '운영행위 목록(1홉)', ['OPR:%s' % s for s in tb_ops('1012110', D(2020, 8, 1), D(2020, 9, 1))], ['OPR:' + o.split(':')[1] for o in ops], '비고 분류표와 동일 입력이라 정합성 확인용')

    # Q03 승인 목록 (Approval-Dam 직접 관계 없음)
    q = {'id': 'Q03', 'text': '충주댐의 2020년 8월 방류 승인은 몇 건이고 내용은 무엇인가?'}
    aps = kg.approvals_via_operations('1003110', D(2020, 8, 1), D(2020, 9, 1))
    bundles.append('### Q03 %s\n\n- 유의: 이 목록은 운영행위가 연결된 승인만 포함한다. 운영행위가 연결되지 않은 승인은 이 경로로 검색되지 않는다.\n' % q['text'] + '\n'.join('- %s: 승인일 %s; %s (근거 %s)' % (a, kg.props[a]['approvalTime'], kg.props[a]['approvalContent'], ', '.join(e['id'] for e in kg.evidence(a))) for a in aps) + '\n')
    rec('Q03', q['text'], '승인 목록(Dam→Operation→Approval)', ['APR:' + s for s in tb_approvals('1003110', D(2020, 8, 1), D(2020, 9, 1))], aps, 'Operation이 없는 승인은 Dam에서 도달 불가')

    # Q04~Q06, Q10 시각 기반 상태 조회
    def state_q(qid, text, code, day, hour_min=None):
        ops = [o for o in kg.operations(code, day, day + timedelta(days=1))]
        bs = [op_bundle(kg, ms, o) for o in ops]
        bundles.append(fmt_bundle({'id': qid, 'text': text}, bs, '' if bs else '- 해당 일자에 KG에서 찾은 운영행위 없음'))
        t_ops = tb_ops(code, day, day + timedelta(days=1))
        kg_ops = [o.split(':')[1] for o in ops]
        win_ok = all(bool(ms.window(code, to_dt(kg.props[o]['operationTime']))) for o in ops) if ops else False
        rec(qid, text, '시각 기반 상태 조회(Operation→상태 창)', ['OPR:' + s for s in t_ops], ['OPR:' + s for s in kg_ops],
            '측정 창 있음' if win_ok else '측정 창 없음' if ops else '운영행위 없음')
        return bs

    state_q('Q04', '소양강댐 2020-08-05 방류 시작 당시 수위·유입량·방류량은?', '1012110', D(2020, 8, 5))
    state_q('Q05', '충주댐 2020-08-06 방류 때 수위는 제한수위 대비 어땠고 근거 규정은 무엇인가?', '1003110', D(2020, 8, 6))
    state_q('Q06', '횡성댐 2020-08-04 방류 승인과 당시 강우량·방류량은?', '1006110', D(2020, 8, 4))
    state_q('Q10', '횡성댐 2017-07-11 초기방류 당시 수위는?', '1006110', D(2017, 7, 11))

    # Q11 표 기반이 유리한 사례
    q = {'id': 'Q11', 'text': '광동댐 2021년 7월 방류 승인과 당시 방류량은?'}
    aps = kg.approvals_via_operations('1001210', D(2021, 7, 1), D(2021, 8, 1))
    bundles.append('### Q11 %s\n\n- 유의: 이 경로는 운영행위가 연결된 승인만 찾는다. 운영행위가 연결되지 않은 승인은 이 경로로 검색되지 않는다.\n' % q['text'] + ('\n'.join('- %s' % a for a in aps) if aps else '- KG에서 이 기간의 운영행위·승인을 찾지 못함') + '\n')
    rec('Q11', q['text'], '승인 목록(Dam→Operation→Approval)', ['APR:' + s for s in tb_approvals('1001210', D(2021, 7, 1), D(2021, 8, 1))], aps, '표 기반은 시설 코드로 직접 필터')

    # 프로브: 상하류 / 사유 / 감소방류
    bundles.append('### Q07 충주댐 방류 당시 하류 충주조정지댐의 수위는?\n\n- KG에 Dam 간 상·하류 관계가 없음. 어느 댐이 하류인지 KG로 확인할 수 없음.\n- (참고) 측정자료 저장소 충주조정지 범위: %s\n' % ('; '.join('%s~%s' % (v[0], v[1]) for k, v in ms.cover.items() if k == '1003611')))
    rec('Q07', '충주댐 방류 당시 하류 충주조정지댐의 수위는?', '프로브: 댐 간 관계', [], [], 'Dam–Dam 관계 부재(구조)와 2020-08 측정 부재(데이터)')
    ops = kg.operations('1003110', D(2020, 8, 6), D(2020, 8, 7))
    bundles.append('### Q08 충주댐 2020-08-06 방류를 한 이유는?\n\n' + '\n'.join('- %s %s (승인 내용: %s)' % (kg.props[o]['operationType'], kg.props[o]['operationTime'], '; '.join(kg.props[a]['approvalContent'] for a in kg.inv[o]['authorizes'])) for o in ops) + '\n- 사유를 기록한 필드/자료는 KG와 연결된 근거에 없음.\n')
    rec('Q08', '충주댐 2020-08-06 방류를 한 이유는?', '프로브: 사유', [], [], '사유 자료 부재')
    dec = kg.operations('1003110', otype='감소방류') + kg.operations('1012110', otype='감소방류') + kg.operations('1006110', otype='감소방류') + kg.operations('1001210', otype='감소방류') + kg.operations('1003611', otype='감소방류')
    bundles.append('### Q09 5개 댐에서 감소방류를 한 사례는?\n\n- KG에서 operationType=감소방류인 운영행위: %d건 (비고에 감소 문구가 있는 승인 없음)\n' % len(dec))
    rec('Q09', '5개 댐에서 감소방류를 한 사례는?', '프로브: 없음의 답변', [], dec, 'KG 결과 0건: 없다와 기록이 없다의 구분 필요')

    with open(os.path.join(N, 'step3b_retrieval_results.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys())); w.writeheader(); w.writerows(results)
    open(os.path.join(N, 'step3b_bundles.md'), 'w', encoding='utf-8').write('\n'.join(bundles))
    for r in results:
        print(r['id'], r['type'], '표', r['table_n'], 'KG', r['kg_n'], 'recall', r['kg_recall'], '|', r['missing_in_kg'][:40], '|', r['note'])
    print('측정 저장소 범위', {CODES[k]: (str(v[0]), str(v[1]), v[2]) for k, v in ms.cover.items()})


if __name__ == '__main__':
    main()
