#!/usr/bin/env python3
"""STEP 2C-2: 전처리 점검. 승인 CSV, 측정 시간자료, 규정 청크의 형식·결측·중복·일관성을 검사한다. stdlib만 사용.
출력: 03_normalized/step2c_preprocess_checks.csv (점검 결과표)"""
import csv, gzip, importlib.util, os, re, collections
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
N = os.path.join(HERE, '..', '03_normalized')
spec = importlib.util.spec_from_file_location('r3b', os.path.join(HERE, 'step3b_retrieval.py'))
r3b = importlib.util.module_from_spec(spec); spec.loader.exec_module(r3b)
DAMS = {'충주': '1003110', '충주조정지': '1003611', '소양강': '1012110', '횡성': '1006110', '광동': '1001210'}
rows = []


def add(pid, target, check, result, count, note=''):
    rows.append({'id': pid, 'target': target, 'check': check, 'result': result, 'count': count, 'note': note})


# ---- 승인 CSV
allr = r3b.rd('approval_records_hrfco_raw_fields.csv')
ap = [r for r in allr if r['관측소명'] in DAMS]
add('P01', '승인 CSV', '전체 행 수 / 5개 댐 행 수', '정보', '%d / %d' % (len(allr), len(ap)))
bad = [r['순차번호'] for r in ap if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', r['승인년월일시분'])]
add('P02', '승인 CSV', '승인일이 YYYY-MM-DD 형식', '통과' if not bad else '확인필요', len(bad), ','.join(bad[:8]))
bad = [r['순차번호'] for r in ap if not re.fullmatch(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', r['방류시작시간'].strip())]
add('P03', '승인 CSV', '방류시작시간이 YYYY-MM-DD HH:MM 형식', '통과' if not bad else '확인필요', len(bad), ','.join(bad[:8]))
nonnum = []
for r in ap:
    try:
        v = float(r['접수방류량'])
        if v <= 0:
            nonnum.append(r['순차번호'])
    except Exception:
        nonnum.append(r['순차번호'])
add('P04', '승인 CSV', '접수방류량이 양의 숫자', '통과' if not nonnum else '확인필요', len(nonnum), ','.join(nonnum[:8]))
early = [r['순차번호'] for r in ap if r['방류시작시간'][:10] < r['승인년월일시분'][:10]]
add('P05', '승인 CSV', '방류시작 날짜가 승인일보다 이전', '정보(보정 안 함)', len(early), '승인일 날짜만 있고 변경승인이 원 방류시작을 유지하는 경우가 있음: ' + ','.join(early[:10]))
diff = [r['순차번호'] for r in ap if r['접수일자'] != r['승인년월일시분']]
add('P06', '승인 CSV', '접수일자가 승인일과 다름', '정보', len(diff), '접수일자 정의가 원자료에 없음')
codemap = collections.defaultdict(set)
for r in allr:
    codemap[r['관측소코드']].add(r['관측소명'])
multi = {k: v for k, v in codemap.items() if len(v) > 1}
add('P07', '승인 CSV', '시설 코드 1개에 이름 1개', '통과' if not multi else '확인필요', len(multi), str(multi) if multi else '')
key = collections.Counter((r['관측소코드'], r['승인년월일시분'], r['방류시작시간'], r['접수방류량'], r['비고'].strip()) for r in ap)
dup = {k: v for k, v in key.items() if v > 1}
add('P08', '승인 CSV', '모든 필드가 같은 중복 승인', '통과' if not dup else '확인필요', len(dup), '; '.join('%s x%d' % (k[:3], v) for k, v in list(dup.items())[:4]))
ctrl = [r['순차번호'] for r in ap if re.search(r'[\r\n\t]', r['비고'])]
add('P09', '승인 CSV', '비고에 줄바꿈·탭 포함', '정보', len(ctrl), '공백 하나로 정규화해 사용')
add('P10', '승인 CSV', '24:00 표기가 비고 텍스트에만 존재하는지', '정보', sum(1 for r in ap if '24:00' in r['비고'] or '24시' in r['비고']), '방류시작시간 컬럼에는 24시 표기 없음')

# ---- 측정 시간자료 (시간 정렬 후 파일: kwater_mywater_hydr_H_aligned_wide.csv.gz)
raw = collections.Counter(); blank = collections.Counter(); neg = collections.Counter(); hh = collections.Counter(); keys = collections.Counter()
times = collections.defaultdict(set)
for r in csv.DictReader(gzip.open(os.path.join(N, 'kwater_mywater_hydr_H_aligned_wide.csv.gz'), 'rt', encoding='utf-8-sig')):
    if r['DAM_CD'] not in r3b.CODES:
        continue
    raw[r['DAM_CD']] += 1
    keys[(r['DAM_CD'], r['SDATE_raw'])] += 1
    hh[r['SDATE_raw'][8:10]] += 1
    times[r['DAM_CD']].add(r3b.label_time(r['SDATE_raw']))
    for v, c in r3b.VARS.items():
        x = r[c].strip()
        if x == '':
            blank[(r['DAM_CD'], v)] += 1
        else:
            try:
                if float(x) < 0:
                    neg[v] += 1
            except Exception:
                blank[(r['DAM_CD'], v)] += 1
add('P11', '측정 시간자료', '5개 댐 행 수(원 행, 중복 포함)', '정보', sum(raw.values()), str({r3b.CODES[k]: v for k, v in raw.items()}))
add('P12', '측정 시간자료', '변수별 결측(빈 값)', '정보(채우지 않음)', sum(blank.values()), str({'%s/%s' % (r3b.CODES[k[0]], k[1]): v for k, v in blank.items()}))
add('P13', '측정 시간자료', '변수별 음수 값', '정보' if neg else '통과', sum(neg.values()), str(dict(neg)))
dk = {k: v for k, v in keys.items() if v > 1}
same = 0
add('P14', '측정 시간자료', '(댐, 시각 라벨) 중복 행(요청 창이 겹친 부분)', '정보(적재 때 1건으로 합침)', len(dk), '값이 서로 다른 중복 여부는 build_aligned_measurement.py가 확인')
add('P15', '측정 시간자료', '시각 라벨의 시(HH) 분포 (24시·00시 표기)', '정보', '24시 %d행, 00시 %d행' % (hh.get('24', 0), hh.get('00', 0)), '시각 의미 미확정(구간 시작/종료); 24시는 다음날 0시로 변환')
gaps = []
for c, ts in sorted(times.items()):
    lo, hi = min(ts), max(ts); t = lo
    while t <= hi:
        if t not in ts:
            gaps.append((r3b.CODES[c], t))
        t += timedelta(hours=1)
bydam = collections.defaultdict(list)
for n, t in gaps:
    bydam[n].append(t)
def ranges(ts):
    ts = sorted(ts); out = []; s0 = e0 = ts[0]
    for t in ts[1:]:
        if t - e0 == timedelta(hours=1):
            e0 = t
        else:
            out.append((s0, e0)); s0 = e0 = t
    out.append((s0, e0))
    return out
desc = '; '.join('%s %d개 구간 %s' % (n, len(ranges(v)), ', '.join('%s~%s' % (a, b) if a != b else str(a) for a, b in ranges(v)[:3])) for n, v in sorted(bydam.items()))
add('P16', '측정 시간자료', '시간 공백(첫 시각~끝 시각 사이 1시간 간격 기준)', '정보(채우지 않음)', len(gaps), desc)
ms = r3b.Measurement()
cov = {r3b.CODES[k]: '%s~%s' % (v[0].date(), v[1].date()) for k, v in ms.cover.items()}
add('P17', '측정 저장소', '댐별 측정 범위', '정보', len(ms.d), str(cov))

# ---- 규정
ch = r3b.rd('kgv2_chunks.csv')
arts = sorted(int(re.search(r'제(\d+)조$', c['chunk_id']).group(1)) for c in ch if re.search(r'제\d+조$', c['chunk_id']))
gap = [i for i in range(1, max(arts) + 1) if i not in arts]
add('P18', '규정 청크', '조문 번호가 1부터 연속', '통과' if not gap else '확인필요', len(arts), '누락 %s' % gap if gap else '제1~%d조' % max(arts))
add('P19', '규정 청크', '별표 청크', '정보', sum(1 for c in ch if '별표' in c['chunk_id']), '별표 1~3')
crit = r3b.rd('kgv2_properties.csv')
cv = {p['entity_id']: p['value'] for p in crit if p['property'] == 'criterionValue'}
add('P20', '별표3 파싱', '테스트 댐 5곳 중 제한수위 값이 있는 댐', '정보', len(cv), '충주·소양강·횡성만 별표3에 있음(광동·충주조정지는 별표3에 없음)')
names = collections.Counter()
for c in ch:
    if c['chunk_id'] == 'LAW:별표3':
        for nm in ['충 주 댐', '충주댐', '소양강댐', '횡 성 댐', '횡성댐']:
            if nm in c['text']:
                names[nm] += 1
add('P21', '별표3', '댐 이름 표기가 공백 포함 형태', '확인필요', dict(names), '"충 주 댐", "횡 성 댐"처럼 공백이 있어 이름 비교 전 공백 제거 필요')

with open(os.path.join(N, 'step2c_preprocess_checks.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
for r in rows:
    print(r['id'], '|', r['target'], '|', r['check'], '|', r['result'], '|', r['count'], '|', r['note'][:110])


if __name__ == '__main__':
    pass
