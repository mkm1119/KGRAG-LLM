#!/usr/bin/env python3
"""KG와 비교하기 위한 '엑셀 방식' 입력 구성. stdlib만 사용(xlsx를 직접 기록).

같은 원자료를 KG 없이 평평한 시트 4개로 LLM에 주는 경우를 재현한다.
- 승인_원본: 한강홍수통제소 승인 CSV 원본 컬럼 그대로 (5개 댐 102행)
- 제한수위_별표3: 연계운영규정 별표3 (원문 셀 값)
- 규정_조문: 연계운영규정 조문·별표 원문
- 측정_시간자료: K-water 시간자료 (측정자료 저장소와 같은 행)
시설 이름·코드를 잇는 대응표나 운영행위 분류, 근거 ID는 일부러 넣지 않는다(엑셀로 받았을 때의 상태).
출력: 04_reports/excel_baseline_5dams.xlsx, 03_normalized/step3c_excel_vs_kg_stats.csv
"""
import csv, importlib.util, os, re, zipfile
from datetime import datetime, timedelta
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
N = os.path.join(ROOT, '03_normalized')
spec = importlib.util.spec_from_file_location('r3b', os.path.join(HERE, 'step3b_retrieval.py'))
r3b = importlib.util.module_from_spec(spec); spec.loader.exec_module(r3b)

CODES = r3b.CODES
CTRL = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')


def col(n):
    s = ''
    while True:
        n, r = divmod(n, 26)
        s = chr(65 + r) + s
        if n == 0:
            return s
        n -= 1


def cell_xml(ref, v, bold=False):
    s = ' s="1"' if bold else ''
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return '<c r="%s"%s><v>%s</v></c>' % (ref, s, repr(v))
    return '<c r="%s"%s t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>' % (ref, s, escape(CTRL.sub('', str(v))))


def sheet_xml(header, rows):
    yield '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
    yield '<row r="1">' + ''.join(cell_xml('%s1' % col(i), h, True) for i, h in enumerate(header)) + '</row>'
    for n, row in enumerate(rows, start=2):
        yield '<row r="%d">' % n + ''.join(cell_xml('%s%d' % (col(i), n), v) for i, v in enumerate(row)) + '</row>'
    yield '</sheetData></worksheet>'


def write_xlsx(path, sheets):
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>' + ''.join('<Override PartName="/xl/worksheets/sheet%d.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' % (i + 1) for i in range(len(sheets))) + '</Types>')
        z.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        z.writestr('xl/workbook.xml', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>' + ''.join('<sheet name="%s" sheetId="%d" r:id="rId%d"/>' % (escape(nm), i + 1, i + 1) for i, (nm, _, _) in enumerate(sheets)) + '</sheets></workbook>')
        z.writestr('xl/_rels/workbook.xml.rels', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + ''.join('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet%d.xml"/>' % (i + 1, i + 1) for i in range(len(sheets))) + '<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>' % (len(sheets) + 1))
        z.writestr('xl/styles.xml', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fonts count="2"><font><sz val="11"/><name val="Malgun Gothic"/></font><font><b/><sz val="11"/><name val="Malgun Gothic"/></font></fonts><fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills><borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/></cellXfs></styleSheet>')
        for i, (nm, header, rows) in enumerate(sheets):
            with z.open('xl/worksheets/sheet%d.xml' % (i + 1), 'w') as f:
                for chunk in sheet_xml(header, rows):
                    f.write(chunk.encode('utf-8'))


def num(x):
    try:
        return float(x)
    except Exception:
        return x


def main():
    names = {'충주', '소양강', '횡성', '광동'}
    ap = [r for r in r3b.rd('approval_records_hrfco_raw_fields.csv') if r['관측소명'] in names]
    ap_rows = [[r['순차번호'], r['관측소코드'], r['관측소명'], r['승인년월일시분'], r['방류시작시간'], num(r['접수방류량']), r['접수일자'], r['비고']] for r in ap]
    # 별표3 (원문 표에서 한강수계 행)
    txt = open(os.path.join(N, 'law_admrul_annex_000300_text.txt'), encoding='utf-8').read()
    crit_rows = []
    for nm in ['소양강댐', '충 주 댐', '횡 성 댐', '화 천 댐', '춘 천 댐', '의 암 댐', '청 평 댐', '괴 산 댐', '팔 당 댐']:
        m = re.search(r'%s\s*│\s*([\d\. ]+\d\)?)\s*│\s*([\d\.\-]+)' % re.escape(nm), txt)
        if m:
            crit_rows.append([nm, m.group(1).strip(), m.group(2).strip(), 'EL.m', '댐과 보 등의 연계운영규정 별표3'])
    chunks = r3b.rd('kgv2_chunks.csv')
    ch_rows = [[c['locator'], c['text']] for c in chunks]
    ms = r3b.Measurement()
    meas = sorted(ms.d.items(), key=lambda kv: (kv[0][0], kv[0][1]))
    me_rows = [[code, CODES[code], t.strftime('%Y-%m-%d %H:%M'), num(v['수위']), num(v['저수량']), num(v['강우량']), num(v['유입량']), num(v['총방류량']), num(v['저수율'])] for (code, t), v in meas]
    out = os.path.join(ROOT, '04_reports', 'excel_baseline_5dams.xlsx')
    write_xlsx(out, [('승인_원본', ['순차번호', '관측소코드', '관측소명', '승인년월일시분', '방류시작시간', '접수방류량', '접수일자', '비고'], ap_rows),
                     ('제한수위_별표3', ['댐명(원문 표기)', '홍수기 제한수위', '시설별 최저 운영수위', '단위', '출처'], crit_rows),
                     ('규정_조문', ['위치', '원문'], ch_rows),
                     ('측정_시간자료', ['댐코드', '댐명', '시각(라벨)', '수위(EL.m)', '저수량(MCM)', '강우량(mm)', '유입량(CMS)', '총방류량(CMS)', '저수율(%)'], me_rows)])
    print('xlsx', out, round(os.path.getsize(out) / 1e6, 1), 'MB | 승인', len(ap_rows), '제한수위', len(crit_rows), '조문', len(ch_rows), '측정', len(me_rows))
    # 질문별 입력 크기 비교
    import collections
    bundles = open(os.path.join(N, 'step3b_bundles.md'), encoding='utf-8').read()
    kgb = {m.group(1): len(m.group(2)) for m in re.finditer(r'### (Q\d+)\s*(.*?)(?=\n### |\Z)', bundles, flags=re.S)}
    ap_chars = sum(len('\t'.join(map(str, r))) + 1 for r in ap_rows)
    crit_chars = sum(len('\t'.join(map(str, r))) + 1 for r in crit_rows)
    law3 = len([c for c in chunks if c['chunk_id'] == 'LAW:별표3'][0]['text'])
    D = datetime
    spec_q = {'Q01': (None, None, ['제한수위', '규정']), 'Q02': (None, None, ['승인']), 'Q03': (None, None, ['승인']),
              'Q04': ('1012110', D(2020, 8, 5), ['승인', '측정']), 'Q05': ('1003110', D(2020, 8, 6), ['승인', '측정', '제한수위', '규정']),
              'Q06': ('1006110', D(2020, 8, 4), ['승인', '측정']), 'Q10': ('1006110', D(2017, 7, 11), ['승인', '측정']),
              'Q11': ('1001210', D(2021, 7, 3), ['승인', '측정'])}
    rows = []
    for q, (code, day, sheets_needed) in spec_q.items():
        chars = 0
        if '승인' in sheets_needed:
            chars += ap_chars
        if '제한수위' in sheets_needed:
            chars += crit_chars
        if '규정' in sheets_needed:
            chars += law3
        mrows = 0
        if code:
            lo, hi = day - timedelta(days=1), day + timedelta(days=2)
            mrows = sum(1 for (c, t) in ms.d if c == code and lo <= t < hi)
            chars += mrows * 60
        rows.append({'id': q, 'sheets_needed': ' + '.join(sheets_needed), 'excel_prefiltered_chars': chars, 'excel_measure_rows_in_3day_window': mrows, 'kg_bundle_chars': kgb.get(q, 0)})
    with open(os.path.join(N, 'step3c_excel_vs_kg_stats.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    for r in rows:
        print(r)
    print('measurement total rows', len(me_rows), '| 승인 시트 글자수', ap_chars, '| 별표3 글자수', law3)


if __name__ == '__main__':
    main()
