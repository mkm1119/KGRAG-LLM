#!/usr/bin/env python3
"""승인 비고(자유 문장)를 Operation(방류·조작 행위)으로 분류한다. 규칙 기반, stdlib만 사용.

입력: 03_normalized/approval_records_hrfco_raw_fields.csv (한강홍수통제소 댐방류승인 원자료)
출력: 03_normalized/operation_from_remarks_5dams.csv
원칙: 비고에 행위가 적힌 승인은 그 행위로, 비고가 없거나 한정어/수치뿐인 승인은 일반 '방류'로 Operation을 만든다(결정 2026-10). 승인 변경 문구뿐인 승인은 같은 방류의 변경이므로 만들지 않고 사유를 남긴다.
비고는 승인 문구이므로 '실행 확인'이 아니다.
"""
import csv, re, collections, sys, os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '03_normalized')
SRC = os.path.join(BASE, 'approval_records_hrfco_raw_fields.csv')
OUT = os.path.join(BASE, 'operation_from_remarks_5dams.csv')
DAMS = ('충주', '소양강', '횡성', '광동')  # 충주조정지는 테스트 대상에서 제외(2026-10 결정)

QUALIFIERS = [r'\(?\s*발전방류\s*포함\s*\)?', r'발전방류포함', r'여수로\s*자연월류량\s*제외', r'자연월류\s*미포함', r'\(?\s*자연월류[^)]*\)?']

# (operationType, 정규식, 설명). 한 비고에서 여러 유형이 동시에 잡힐 수 있다.
ACTION_RULES = [
    ('방류종료', r'방류\s*종료', '종료 문구'),
    ('초기방류', r'초기\s*수문\s*방류|초기\s*방류|\(\s*초기\s*\d', '초기방류 문구'),
    ('점진·점증방류', r'점진|점증', '점진/점증 문구'),
    ('증가방류', r'증가\s*방류|증가\s*예정|\d\s*cms\s*증|㎥/s\s*증가|㎥/s증가', '증가 문구'),
    ('감소방류', r'감소\s*방류', '감소 문구'),
    ('탄력적 방류', r'탄력', '탄력 문구'),
]
CHANGE_RE = re.compile(r'변경|연장|정정')  # 승인 변경: 행위가 아니라 승인 쪽 변경으로 본다
GENERIC_RE = re.compile(r'수문\s*방류|수문조작에\s*의한\s*방류|이내\s*방류|방류\s*시작|방류\s*\)')
GATE_OTHER_RE = re.compile(r'수문조작')
ACTUAL_START_RE = re.compile(r'실제\s*방류는\s*(\d{1,2})\s*시부터')
END_TIME_RE = re.compile(r'(\d{1,2})\.(\d{1,2})\s+(\d{1,2}):(\d{2})\s*수문방류종료')
AMOUNT_RE = re.compile(r'[\d][\d ,\.]*\s*(?:㎥/s|cms)')


def clean(b):
    b = b.replace('\n', ' ')
    for q in QUALIFIERS:
        b = re.sub(q, ' ', b)
    return re.sub(r'\s+', ' ', b).strip()


import importlib.util
from datetime import datetime, timedelta
_spec = importlib.util.spec_from_file_location('r3b', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'step3b_retrieval.py'))
r3b = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(r3b)
MS = r3b.Measurement()
NAME2CODE = {v.replace('댐', ''): k for k, v in r3b.CODES.items()}
BEFORE, AFTER, ABS_THR, REL_THR = 3, 6, 1.0, 0.10


def observed_change(dam, start):
    """결정(2026-10): 행위 시각 = 방류 시작 시각 앞 BEFORE시간~뒤 AFTER시간에서 총방류량이 직전 시각보다 max(ABS_THR CMS, REL_THR) 이상 바뀐 시각 중 시작에 가장 가까운 것(같으면 나중).
    측정 라벨 시각(01~24시, 의미 미확정, ±1시간)을 그대로 쓴다. 없으면 None."""
    t0 = datetime.strptime(start, '%Y-%m-%d %H:%M')
    if t0.minute:
        t0 = t0.replace(minute=0) + timedelta(hours=1)
    code, ser = NAME2CODE[dam], {}
    for h in range(-BEFORE - 1, AFTER + 1):
        v = MS.d.get((code, t0 + timedelta(hours=h)))
        if v and r3b.fnum(v['총방류량']) is not None:
            ser[h] = r3b.fnum(v['총방류량'])
    cand = []
    for h in range(-BEFORE, AFTER + 1):
        if h in ser and h - 1 in ser:
            d = ser[h] - ser[h - 1]
            if abs(d) >= max(ABS_THR, REL_THR * max(ser[h - 1], 0.1)):
                cand.append((h, d))
    if not cand:
        return None
    h, d = min(cand, key=lambda x: (abs(x[0]), -x[0]))
    return (t0 + timedelta(hours=h)).strftime('%Y-%m-%d %H:%M'), d


def classify(rec):
    raw = rec['비고'].strip()
    start = rec['방류시작시간'].strip()
    day = rec['승인년월일시분'][:10]
    b = clean(raw)
    types = []
    for t, pat, why in ACTION_RULES:
        if re.search(pat, b):
            types.append((t, why))
    has_change = bool(CHANGE_RE.search(b))
    if not types:
        m = ACTUAL_START_RE.search(b)
        if m:
            types.append(('방류', '실제 방류 시각 문구'))
        elif GENERIC_RE.search(b) and not has_change:
            types.append(('방류', '방류 문구'))
        elif GATE_OTHER_RE.search(b) and not has_change:
            types.append(('수문조작(연계 시설)', '타 시설 수문조작 문구'))
    ops, reasons = [], []
    for t, why in types:
        op_time, tsrc = start, '방류시작시간'
        if t == '방류종료':
            m = END_TIME_RE.search(raw)
            if m:
                op_time, tsrc = '%s-%02d-%02d %02d:%s' % (day[:4], int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)), '비고 명시 시각'
        if t == '방류' and ACTUAL_START_RE.search(b):
            h = int(ACTUAL_START_RE.search(b).group(1))
            op_time, tsrc = '%s %02d:00' % (start[:10], h), '비고 명시 시각(실제 방류)'
        amt = AMOUNT_RE.search(raw)
        ops.append({'operationType': t, 'rule': why, 'operationTime': op_time, 'time_source': tsrc,
                    'amount_raw': amt.group(0).strip() if amt else '', 'has_change_text': 'Y' if has_change else 'N'})
    # 결정(2026-10): 변경 문구가 있는 승인은 같은 방류 사건의 변경이므로 새 Operation을 만들지 않는다(행위 문구가 함께 있어도). 원 승인의 Operation에 잇는 일은 step2b에서 한다.
    if has_change:
        return [], '승인 변경(같은 방류의 변경, 원 승인의 행위 참조)'
    if ops:
        return ops, ''
    # 결정(2026-10): 비고가 없거나 한정어/수치만 있는 승인도 해당 시각의 방류 승인이므로 일반 '방류'로 둔다(종류 미상, 승인 자체에서 도출).
    why = '비고 없음→승인 자체(일반 방류)' if not raw else '한정어/수치만→승인 자체(일반 방류)'
    return [{'operationType': '방류', 'rule': why, 'operationTime': start, 'time_source': '방류시작시간', 'amount_raw': '', 'has_change_text': 'N'}], ''


def main():
    rows = [r for r in csv.DictReader(open(SRC, encoding='utf-8-sig')) if r['관측소명'] in DAMS]
    out, noop = [], collections.Counter()
    for r in rows:
        ops, why_not = classify(r)
        base = {'순차번호': r['순차번호'], '댐': r['관측소명'], '승인일': r['승인년월일시분'][:10],
                '방류시작시간': r['방류시작시간'], '접수방류량': r['접수방류량'], '비고_원문': r['비고'].replace('\n', ' ').strip()}
        if ops:
            for o in ops:
                o['approved_start'] = r['방류시작시간'].strip()
                if o['time_source'] == '방류시작시간':
                    oc = observed_change(r['관측소명'], r['방류시작시간'].strip())
                    if oc:
                        o['operationTime'], o['time_source'], o['change_amount'] = oc[0], '측정 방류량 변화 시각', round(oc[1], 3)
                    else:
                        o['time_source'], o['change_amount'] = '승인 시작시각(변화 미검출)', ''
                else:
                    o['change_amount'] = ''
                review = 'Y' if (o['operationType'] == '수문조작(연계 시설)' or o['rule'] in ('타 시설 수문조작 문구',)) else 'N'
                out.append({**base, 'operation_created': 'Y', **o, 'not_created_reason': '', 'review_needed': review})
        else:
            noop[why_not] += 1
            review = 'Y' if why_not.startswith('한정어') else 'N'
            out.append({**base, 'operation_created': 'N', 'operationType': '', 'rule': '', 'operationTime': '', 'time_source': '',
                        'amount_raw': '', 'has_change_text': '', 'approved_start': '', 'change_amount': '', 'not_created_reason': why_not, 'review_needed': review})
    cols = ['순차번호', '댐', '승인일', '방류시작시간', '접수방류량', '비고_원문', 'operation_created', 'operationType', 'rule',
            'operationTime', 'time_source', 'approved_start', 'change_amount', 'amount_raw', 'has_change_text', 'not_created_reason', 'review_needed']
    with open(OUT, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(out)
    made = [o for o in out if o['operation_created'] == 'Y']
    print('승인', len(rows), '| Operation 행', len(made), '| Operation이 생긴 승인', len({o['순차번호'] for o in made}))
    print('유형별', collections.Counter(o['operationType'] for o in made).most_common())
    print('댐별 승인/생성승인', {d: (sum(1 for r in rows if r['관측소명'] == d), len({o['순차번호'] for o in made if o['댐'] == d})) for d in DAMS})
    print('미생성 사유', dict(noop))
    print('시각 출처', collections.Counter(o['time_source'] for o in made).most_common())


if __name__ == '__main__':
    main()
