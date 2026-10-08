#!/usr/bin/env python3
"""KG v2의 구축 과정과 개체·관계 전체를 한 문서(04_reports/KG_V2_CONTENTS.md)로 덤프한다. stdlib만 사용."""
import csv, os, collections, re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
N = os.path.join(ROOT, '03_normalized')
OUT = os.path.join(ROOT, '04_reports', 'KG_V2_CONTENTS.md')


def rd(p):
    return list(csv.DictReader(open(os.path.join(N, p), encoding='utf-8-sig')))


def cell(x):
    return str(x).replace('|', '\\|').replace('\n', ' ')


def table(header, rows):
    L = ['| ' + ' | '.join(header) + ' |', '|' + '|'.join(['---'] * len(header)) + '|']
    for r in rows:
        L.append('| ' + ' | '.join(cell(c) for c in r) + ' |')
    return '\n'.join(L)


def main():
    ents, props, rels, prov = rd('kgv2_entities.csv'), rd('kgv2_properties.csv'), rd('kgv2_relations.csv'), rd('kgv2_provenance.csv')
    chunks = rd('kgv2_chunks.csv')
    label = {e['entity_id']: e['label'] for e in ents}
    cls = {e['entity_id']: e['class'] for e in ents}
    P = collections.defaultdict(dict)
    for p in props:
        P[p['entity_id']][p['property']] = p['value']
    pv = {p['item']: p for p in prov}
    by_cls = collections.defaultdict(list)
    for e in ents:
        by_cls[e['class']].append(e['entity_id'])
    L = []
    A = L.append
    A('# KG v2 구축 과정과 개체·관계 전체')
    A('')
    A('- 기준 온톨로지: 랩미팅 최종본7 (Class 6, Relation 8). 대상: 충주댐, 충주조정지, 소양강댐, 횡성댐, 광동댐')
    A('- 생성: `scripts/step2_operation_from_remarks.py` → `scripts/step2b_build_kg.py` → 이 문서는 `scripts/kgv2_dump_report.py`가 `kgv2_*.csv`에서 만든다.')
    A('- 구현은 CSV 파일이다(그래프 DB 미사용). 시계열 수치와 규정 원문은 KG에 넣지 않고 측정자료 저장소와 문서 저장소에 둔다.')
    A('')
    A('## 1. 구축 과정')
    A('')
    A('| 단계 | 입력 | 규칙 | 결과 | 자료 성격 |')
    A('|---|---|---|---|---|')
    A('| 1 Dam | MyWater 일자료(댐 코드·유형), 승인 파일 관측소 코드 | 5개 댐을 시설 코드로 생성. 승인 파일과 K-water의 코드가 같음(동일시설 확정은 REVIEW_REQUIRED) | Dam %d | 실제 자료 |' % len(by_cls['Dam']))
    A('| 2 HydrometeorologicalState | 변수 6종(수위, 저수량, 강우량, 유입량, 총방류량, 저수율) | 댐 x 변수 조합마다 개체 생성. `stationCode`는 댐 단위 시설 코드. 수치는 KG에 넣지 않음 | HMS %d, `hasHydrometeorologicalState` %d | 실제 자료의 항목 구조 |' % (len(by_cls['HydrometeorologicalState']), sum(1 for r in rels if r['relation'] == 'hasHydrometeorologicalState')))
    A('| 3 Approval | 한강홍수통제소 댐방류승인 CSV (5개 댐 102행) | 1행 = Approval 1개. `approvalTime`=승인일(날짜만), `approvalContent`=방류시작·접수방류량·비고 | Approval %d | 실제 자료 |' % len(by_cls['Approval']))
    A('| 4 Operation | 승인 비고 분류표 `operation_from_remarks_5dams.csv` | 비고에서 증가·초기·점진·탄력·종료 등 행위 문구를 규칙으로 분류. 비고가 없거나 승인 변경 문구뿐이면 만들지 않음. `operationTime`=방류시작시간(비고에 시각이 있으면 그 시각) | Operation %d (승인 64건에서 생성) | 비고에서 분류한 연구용 구성(실행 확인 아님) |' % len(by_cls['Operation']))
    A('| 5 Criterion | `criterion_list.csv` (연계운영규정 별표 3) | 테스트 댐에 해당하는 홍수기 제한수위 행만 생성. 값은 원문 셀에서 읽음 | Criterion %d | 실제 자료(현행 규정 값) |' % len(by_cls['Criterion']))
    A('| 6 EvidenceSource | 승인 순차번호, 댐별 측정자료, 규정 별표 3 | 승인 1건마다 근거자료 1개(순차번호 위치), 댐마다 측정자료 1개, 규정 별표 3 1개 | EvidenceSource %d | 실제 자료의 위치 정보 |' % len(by_cls['EvidenceSource']))
    A('| 7 관계 | 위 개체들 | `performedOnDam`: 승인 행의 시설 코드, `authorizes`: 같은 승인 행에서 분류한 행위, `appliesToDam`: 별표 3 시설명과 댐 이름 일치, `supportedBy`: 항목별 출처 | 관계 %d | 관계마다 origin 표시(아래 4절) |' % len(rels))
    A('| 8 문서 청크 | 연계운영규정 XML(현행, 시행 2026-07-08) | 조문 단위와 별표 단위로 분할 | 청크 %d | 실제 자료 |' % len(chunks))
    A('')
    A('Operation 분류 규칙(위에서 아래로 적용, 한 비고에서 여러 유형이 동시에 잡힐 수 있음):')
    A('')
    A(table(['유형', '비고 문구 예'], [['방류종료', '수문방류종료'], ['초기방류', '초기수문방류, 초기방류, (초기 1000㎥/s…)'], ['점진·점증방류', '점진방류, 점증방류'],
                                   ['증가방류', '증가방류, 증가예정, 10cms 증'], ['감소방류', '감소방류 (5개 댐에서는 0건)'], ['탄력적 방류', '탄력적 방류, 탄력 조절'],
                                   ['방류(일반)', '수문방류 승인, 이내 방류, 실제방류는 20시부터'], ['수문조작(연계 시설)', '강천보 여주보 이포보 수문조작 (검토 대상 1건)'],
                                   ['만들지 않음', '비고 없음, 변경승인·기간연장·정정 문구뿐, 한정어(발전방류 포함 등)뿐']]))
    A('')
    A('## 2. 한 건 추적 예: 충주댐 승인 3647')
    A('')
    raw = [r for r in rd('approval_records_hrfco_raw_fields.csv') if r['순차번호'] == '3647'][0]
    A('원자료(승인 CSV %s행): 순차번호 %s / 관측소 %s(%s) / 승인일 %s / 방류시작 %s / 접수방류량 %s / 비고 "%s"' % (
        raw['row_number_in_file'], raw['순차번호'], raw['관측소명'], raw['관측소코드'], raw['승인년월일시분'], raw['방류시작시간'], raw['접수방류량'], re.sub(r'\s+', ' ', raw['비고'])))
    A('')
    chain = ['APR:3647', 'OPR:3647:1', 'EVI:AP:3647', 'DAM:1003110', 'CRI:CR-02', 'EVI:LAW:별표3']
    rows = []
    for e in chain:
        rows.append([e, cls[e], label[e], '; '.join('%s=%s' % (k, v) for k, v in P[e].items())])
    A(table(['개체', 'Class', '이름', '속성'], rows))
    A('')
    rr = [r for r in rels if r['subject'] in chain and r['object'] in chain]
    A(table(['주어', '관계', '목적어', 'origin', '규칙'], [[r['subject'], r['relation'], r['object'], r['origin'], r['rule']] for r in rr]))
    A('')
    A('이후 검색 단계에서 `OPR:3647:1`의 시각 2020-08-06T06:00으로 `DAM:1003110`의 상태 항목(`HMS:1003110:*`, stationCode 1003110)을 찾아 측정자료 저장소에서 -6~+12시간을 조회한다.')
    A('')
    A('## 3. 개체 전체')
    for c in ['Dam', 'HydrometeorologicalState', 'Criterion', 'Operation', 'Approval', 'EvidenceSource']:
        ids = by_cls[c]
        A('')
        A('### %s (%d)' % (c, len(ids)))
        A('')
        if c == 'Dam':
            A(table(['id', '이름', 'damType'], [[i, label[i], P[i].get('damType', '')] for i in ids]))
        elif c == 'HydrometeorologicalState':
            A(table(['id', 'variableType', 'stationCode'], [[i, P[i]['variableType'], P[i]['stationCode']] for i in ids]))
        elif c == 'Criterion':
            A(table(['id', 'criterionType', 'criterionValue', 'unit', '비고'], [[i, P[i]['criterionType'], P[i]['criterionValue'], P[i]['unit'], pv[i]['note']] for i in ids]))
        elif c == 'Operation':
            A(table(['id', 'operationType', 'operationTime', '분류 규칙', '시각 출처'], [[i, P[i]['operationType'], P[i]['operationTime'], pv[i]['rule'], pv[i]['note']] for i in ids]))
        elif c == 'Approval':
            A(table(['id', 'approvalTime', 'approvalContent'], [[i, P[i]['approvalTime'], P[i]['approvalContent']] for i in ids]))
        else:
            A(table(['id', 'sourceType', 'sourceTitle', 'sourceLocator'], [[i, P[i]['sourceType'], P[i]['sourceTitle'], P[i]['sourceLocator']] for i in ids]))
    A('')
    A('## 4. 관계 전체')
    A('')
    oc = collections.Counter((r['relation'], r['origin']) for r in rels)
    A(table(['관계', 'origin', '개수', 'origin 의미'], [[k[0], k[1], v, {'real': '원자료에 직접 있는 연결', 'derived': '원자료에서 규칙으로 도출', 'constructed': '연구용 구성(원자료에 연결 근거 없음)', 'name-match': '이름 일치로 연결(코드 없음)'}[k[1]]] for k, v in sorted(oc.items())]))
    for rel in ['hasHydrometeorologicalState', 'performedOnDam', 'authorizes', 'appliesToDam', 'supportedBy']:
        rs = [r for r in rels if r['relation'] == rel]
        A('')
        A('### %s (%d)' % (rel, len(rs)))
        A('')
        A(table(['주어', '목적어', 'origin', '규칙'], [['%s (%s)' % (r['subject'], label[r['subject']]), '%s (%s)' % (r['object'], label[r['object']]), r['origin'], r['rule']] for r in rs]))
    A('')
    A('## 5. 문서 저장소 청크')
    A('')
    A(table(['chunk_id', '위치', '글자 수'], [[c['chunk_id'], c['locator'], len(c['text'])] for c in chunks]))
    A('')
    A('## 6. 생성하지 않은 것')
    A('')
    A('- 승인 비고가 없거나 변경 문구뿐인 승인 38건은 Operation이 없고, Approval에서 Dam으로 가는 직접 관계가 없어 Dam에서 도달할 수 없다.')
    A('- Dam 간 상하류 관계, 승인과 기준의 직접 관계, 관측소 단위 상태 항목은 만들지 않았다(온톨로지에 없음).')
    open(OUT, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print(len(L), 'lines ->', OUT)


if __name__ == '__main__':
    main()
