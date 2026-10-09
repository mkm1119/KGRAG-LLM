#!/usr/bin/env python3
"""STEP 2B: 최종본7 온톨로지(Class 6, Relation 8) 기준 KG v2 구축 (테스트 5개 댐). stdlib만 사용.

KG에는 의미·관계·근거 위치만 넣고, 시계열 수치(Measurement Store)와 규정 원문(Document Store)은 밖에 둔다.
입력: 승인 CSV, step2_operation_from_remarks 산출물, criterion_list.csv, 연계운영규정 XML, MyWater 일자료(댐 유형)
출력(03_normalized): kgv2_entities / kgv2_properties / kgv2_relations / kgv2_provenance / kgv2_chunks (CSV)
"""
import csv, gzip, os, re, sys, collections
import xml.etree.ElementTree as ET

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
N = os.path.join(ROOT, '03_normalized')
LAW_XML = os.path.join(ROOT, '01_raw/Law/admrul_2100000282102_댐과보등의연계운영규정_현행20260708.xml')

# 승인 파일의 관측소명 -> (KG 댐 이름, 시설 코드). 5개 댐은 승인 파일과 K-water 코드가 같다(동일시설 확정은 REVIEW_REQUIRED).
DAMS = {'충주': ('충주댐', '1003110'), '소양강': ('소양강댐', '1012110'),
        '횡성': ('횡성댐', '1006110'), '광동': ('광동댐', '1001210')}
HMS_VARS = [('수위', 'DATA1_수위(EL.m)'), ('저수량', 'DATA2_저수량(MCM)'), ('강우량', 'DATA3_강우량(mm)'),
            ('유입량', 'DATA4_유입량(CMS)'), ('총방류량', 'DATA6_총방류량(CMS)'), ('저수율', 'DATA7_저수율(%)')]


def rd(p):
    return list(csv.DictReader(open(os.path.join(N, p), encoding='utf-8-sig')))


def iso(s):
    s = s.strip()
    return s.replace(' ', 'T') if s else ''


def main():
    ent, props, rels, prov = [], [], [], []

    def E(eid, cls, label):
        ent.append((eid, cls, label))

    def P(eid, name, val, dtype='string'):
        props.append((eid, name, val, dtype))

    def R(s, r, o, rule, origin, note=''):
        rels.append((s, r, o, rule, origin, note))

    def V(item, kind, src, loc, rule, origin, note=''):
        prov.append((item, kind, src, loc, rule, origin, note))

    # ---- Dam
    types = {}
    for i, r in enumerate(csv.DictReader(gzip.open(os.path.join(N, 'kwater_mywater_period_daily_long.csv.gz'), 'rt', encoding='utf-8-sig'))):
        types.setdefault(r['DAM_CD'], r['DAM_BO_NM_source'])
    code2dam = {}
    for ap_name, (nm, code) in DAMS.items():
        eid = 'DAM:' + code
        code2dam[code] = eid
        E(eid, 'Dam', nm)
        P(eid, 'damName', nm)
        P(eid, 'damType', types.get(code, ''))
        V(eid, 'entity', '03_normalized/kwater_mywater_period_daily_long.csv.gz', 'DAM_CD=' + code, 'MR-DAM', 'real',
          '댐 유형은 K-water 원문(DAM_BO_NM_source) 그대로; 승인 파일과 코드 일치(동일시설 REVIEW_REQUIRED)')

    # ---- Evidence: 측정자료(댐별), 규정(별표3)
    for ap_name, (nm, code) in DAMS.items():
        eid = 'EVI:KW:' + code
        E(eid, 'EvidenceSource', 'K-water MyWater 수문자료 ' + nm)
        P(eid, 'sourceTitle', 'K-water MyWater 수문 시간자료')
        P(eid, 'sourceType', '측정자료')
        P(eid, 'sourceLocator', 'DAM_CD=%s %s 시간별 자료' % (code, nm))
        V(eid, 'entity', '03_normalized/kwater_mywater_hydr_H_wide.csv.gz', 'DAM_CD=' + code, 'MR-EVI-KW', 'real')
    law_id = 'EVI:LAW:별표3'
    E(law_id, 'EvidenceSource', '댐과 보 등의 연계운영규정 별표3')
    P(law_id, 'sourceTitle', '댐과 보 등의 연계운영규정 (기후에너지환경부 훈령 제42호, 시행 2026-07-08)')
    P(law_id, 'sourceType', '규정')
    P(law_id, 'sourceLocator', '별표 3')
    V(law_id, 'entity', '01_raw/Law/admrul_2100000282102_댐과보등의연계운영규정_현행20260708.xml', '별표3', 'MR-EVI-LAW', 'real')

    # ---- HydrometeorologicalState: 댐 x 변수 (stationCode는 K-water 시설 코드; 강우량도 댐 단위 값)
    for ap_name, (nm, code) in DAMS.items():
        for var, col in HMS_VARS:
            hid = 'HMS:%s:%s' % (code, var)
            E(hid, 'HydrometeorologicalState', '%s_%s' % (nm, var))
            P(hid, 'variableType', var)
            P(hid, 'stationCode', code)
            R('DAM:' + code, 'hasHydrometeorologicalState', hid, 'MR-HMS', 'real')
            R(hid, 'supportedBy', 'EVI:KW:' + code, 'MR-SUP-HMS', 'real')
            V(hid, 'entity', '03_normalized/kwater_mywater_hydr_H_wide.csv.gz', col, 'MR-HMS', 'real',
              'stationCode는 댐 단위 시설 코드(관측소 코드 아님)')

    # ---- Approval + Evidence(승인자료, 순차번호별)
    aps = [r for r in rd('approval_records_clean.csv') if r['관측소명'] in DAMS]
    for r in aps:
        seq, nm = r['순차번호'], r['관측소명']
        aid, evid = 'APR:' + seq, 'EVI:AP:' + seq
        parts = ['방류시작 ' + r['방류시작시간'].strip(), '접수방류량 %s㎥/s' % r['접수방류량'].strip()]
        if r['비고'].strip():
            parts.append('비고: ' + re.sub(r'\s+', ' ', r['비고'].strip()))
        E(aid, 'Approval', '승인 %s (%s)' % (seq, DAMS[nm][0]))
        P(aid, 'approvalTime', r['승인년월일시분'][:10], 'date')
        P(aid, 'approvalContent', '; '.join(parts))
        E(evid, 'EvidenceSource', '한강홍수통제소 댐방류승인 순차번호 ' + seq)
        P(evid, 'sourceTitle', '환경부 한강홍수통제소 홍수예보 댐방류승인')
        P(evid, 'sourceType', '승인자료')
        P(evid, 'sourceLocator', '순차번호 ' + seq)
        R(aid, 'supportedBy', evid, 'MR-SUP-APR', 'real')
        V(aid, 'entity', '03_normalized/approval_records_clean.csv', 'row_number_in_file=' + r['row_number_in_file'],
          'MR-APR', 'real', '승인일은 날짜만 있음; 시설은 Operation을 거쳐 Dam에 연결됨')
        V(evid, 'entity', '03_normalized/approval_records_clean.csv', '순차번호=' + seq, 'MR-EVI-AP', 'real')

    # ---- Operation: 승인 비고에서 분류한 행위 (연구용 구성, 실행 확인 아님)
    k = collections.Counter()
    opsrows = rd('operation_from_remarks_5dams.csv')
    ops_of = collections.defaultdict(list)
    for r in opsrows:
        if r['operation_created'] != 'Y':
            continue
        seq = r['순차번호']
        k[seq] += 1
        oid = 'OPR:%s:%d' % (seq, k[seq])
        ops_of[seq].append(oid)
        code = DAMS[r['댐']][1]
        E(oid, 'Operation', '%s %s (%s)' % (DAMS[r['댐']][0], r['operationType'], r['operationTime']))
        P(oid, 'operationType', r['operationType'])
        P(oid, 'operationTime', iso(r['operationTime']), 'datetime')
        R(oid, 'performedOnDam', 'DAM:' + code, 'MR-OPR-DAM', 'derived', '승인 행의 시설 코드')
        R('APR:' + seq, 'authorizes', oid, 'MR-AUTH', 'constructed', '같은 승인 행의 비고에서 분류한 행위(연구용 구성, 실행 확인 아님)')
        R(oid, 'supportedBy', 'EVI:AP:' + seq, 'MR-SUP-OPR', 'derived')
        V(oid, 'entity', '03_normalized/operation_from_remarks_5dams.csv', '순차번호=' + seq, r['rule'], 'derived(비고 분류)',
          '시각 출처: ' + r['time_source'])

    # ---- 변경 승인 -> 원 승인의 Operation (같은 댐, 같은 방류 시작 시각이면 같은 방류 사건으로 추정)
    first = {}
    for r in opsrows:
        first.setdefault(r['순차번호'], r)
    for seq, r in first.items():
        if not r['not_created_reason'].startswith('승인 변경'):
            continue
        for oseq, o in first.items():
            if oseq != seq and o['댐'] == r['댐'] and o['방류시작시간'] == r['방류시작시간'] and not o['not_created_reason'].startswith('승인 변경'):
                for oid in ops_of.get(oseq, []):
                    R('APR:' + seq, 'authorizes', oid, 'MR-AUTH-CHG', 'inferred', '변경 승인: 같은 댐·같은 방류 시작 시각의 원 승인 %s의 행위로 연결(추정)' % oseq)

    # ---- Criterion: 별표3 홍수기 제한수위 (테스트 댐에 해당하는 것)
    name2code = {v[0]: v[1] for v in DAMS.values()}
    for r in rd('criterion_list.csv'):
        fac = r['applies_to_facility_per_source'].strip()
        if fac not in name2code or '제한수위' not in r['criterion_type']:
            continue
        m = re.search(r"홍수기 제한수위 셀 원문='([\d\.]+)'", r['verbatim_text_or_value'])
        if not m:
            continue
        cid = 'CRI:' + r['criterion_id(연구용 임시ID)']
        E(cid, 'Criterion', fac + ' 홍수기 제한수위')
        P(cid, 'criterionType', '홍수기 제한수위')
        P(cid, 'criterionValue', m.group(1), 'decimal')
        P(cid, 'unit', r['unit'])
        R(cid, 'appliesToDam', 'DAM:' + name2code[fac], 'MR-CRI-DAM', 'name-match', '별표3 시설명 일치(코드 없음)')
        R(cid, 'supportedBy', law_id, 'MR-SUP-CRI', 'real')
        V(cid, 'entity', '03_normalized/criterion_list.csv', r['criterion_id(연구용 임시ID)'], 'MR-CRI', 'real',
          '별표3 해당 행(각주 표시 없음)')

    # ---- Document store: 연계운영규정 조문·별표 청크
    chunks = []
    root = ET.parse(LAW_XML).getroot()
    for el in root.findall('조문내용'):
        t = (el.text or '').strip()
        m = re.match(r'제(\d+)조(?:의(\d+))?\(([^)]*)\)', t)
        if m:
            loc = '제%s조%s' % (m.group(1), ('의' + m.group(2)) if m.group(2) else '')
            chunks.append(('LAW:' + loc, '댐과 보 등의 연계운영규정', loc + '(' + m.group(3) + ')', re.sub(r'[ \t]+', ' ', t)))
    for b in root.iter('별표단위'):
        no = (b.findtext('별표번호') or '').strip().lstrip('0') or '0'
        title = (b.findtext('별표제목') or '').strip()
        body = (b.findtext('별표내용') or '').strip()
        chunks.append(('LAW:별표%s' % no, '댐과 보 등의 연계운영규정', '별표 %s' % no, title + '\n' + body))
    with open(os.path.join(N, 'kgv2_chunks.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f); w.writerow(['chunk_id', 'doc_title', 'locator', 'text']); w.writerows(chunks)

    def out(name, header, rows):
        with open(os.path.join(N, name), 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f); w.writerow(header); w.writerows(rows)

    out('kgv2_entities.csv', ['entity_id', 'class', 'label'], ent)
    out('kgv2_properties.csv', ['entity_id', 'property', 'value', 'datatype'], props)
    out('kgv2_relations.csv', ['subject', 'relation', 'object', 'rule', 'origin', 'note'], rels)
    out('kgv2_provenance.csv', ['item', 'kind', 'source_file', 'source_locator', 'rule', 'data_origin', 'note'], prov)
    print('entities', collections.Counter(c for _, c, _ in ent))
    print('relations', collections.Counter(r for _, r, _, _, _, _ in rels))
    print('chunks', len(chunks), 'properties', len(props))


if __name__ == '__main__':
    main()
