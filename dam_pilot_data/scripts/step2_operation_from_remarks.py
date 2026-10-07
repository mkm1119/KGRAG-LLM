#!/usr/bin/env python3
"""승인 비고(자유 문장)를 Operation(방류·조작 행위)으로 분류한다. 규칙 기반, stdlib만 사용.

입력: 03_normalized/approval_records_hrfco_raw_fields.csv (한강홍수통제소 댐방류승인 원자료)
출력: 03_normalized/operation_from_remarks_5dams.csv
원칙: 비고에 행위가 적힌 승인만 Operation으로 만든다. 비고가 없거나 한정어/승인변경뿐이면 만들지 않고 사유를 남긴다.
비고는 승인 문구이므로 '실행 확인'이 아니다.
"""
import csv, re, collections, sys, os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '03_normalized')
SRC = os.path.join(BASE, 'approval_records_hrfco_raw_fields.csv')
OUT = os.path.join(BASE, 'operation_from_remarks_5dams.csv')
DAMS = ('충주', '충주조정지', '소양강', '횡성', '광동')

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
    if ops:
        return ops, ''
    if not raw:
        return [], '비고 없음'
    if has_change:
        return [], '승인 변경 문구만 있음(행위 아님)'
    return [], '한정어/수치만 있고 행위 문구 없음'


def main():
    rows = [r for r in csv.DictReader(open(SRC, encoding='utf-8-sig')) if r['관측소명'] in DAMS]
    out, noop = [], collections.Counter()
    for r in rows:
        ops, why_not = classify(r)
        base = {'순차번호': r['순차번호'], '댐': r['관측소명'], '승인일': r['승인년월일시분'][:10],
                '방류시작시간': r['방류시작시간'], '접수방류량': r['접수방류량'], '비고_원문': r['비고'].replace('\n', ' ').strip()}
        if ops:
            for o in ops:
                review = 'Y' if (o['operationType'] == '수문조작(연계 시설)' or o['rule'] in ('타 시설 수문조작 문구',)) else 'N'
                out.append({**base, 'operation_created': 'Y', **o, 'not_created_reason': '', 'review_needed': review})
        else:
            noop[why_not] += 1
            review = 'Y' if why_not.startswith('한정어') else 'N'
            out.append({**base, 'operation_created': 'N', 'operationType': '', 'rule': '', 'operationTime': '', 'time_source': '',
                        'amount_raw': '', 'has_change_text': '', 'not_created_reason': why_not, 'review_needed': review})
    cols = ['순차번호', '댐', '승인일', '방류시작시간', '접수방류량', '비고_원문', 'operation_created', 'operationType', 'rule',
            'operationTime', 'time_source', 'amount_raw', 'has_change_text', 'not_created_reason', 'review_needed']
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
