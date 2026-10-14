#!/usr/bin/env python3
"""랩미팅 자료(docx) 생성. 이전 자료(최종본8)를 서식 템플릿으로 삼아 본문만 새로 만든다. stdlib만 사용.
- 이전 자료의 표(용어, CQ, Class, Relation, Data Property, 근거 문헌)는 원문을 읽어 그대로 재사용한다.
- 숫자(개체·관계 수, 승인·운영행위 수 등)는 현재 파일에서 읽어 쓴다.
사용: python3 scripts/build_labmeeting_doc.py <출력 docx 경로>
"""
import collections, csv, gzip, html, os, re, sys, zipfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
N = os.path.join(ROOT, '03_normalized')
TEMPLATE = os.path.join(ROOT, '..', 'lab_meeting', '2026.10.02_랩미팅 자료_최종본8_용어정리.docx')
OUT = sys.argv[1]

# ------------------------------------------------------------------ 사실(현재 파일에서)
rd = lambda p: list(csv.DictReader(open(os.path.join(N, p), encoding='utf-8-sig')))
ents, rels = rd('kgv3_entities.csv'), rd('kgv3_relations.csv')
EC, RC = collections.Counter(e['class'] for e in ents), collections.Counter(r['relation'] for r in rels)
APPS = [a for a in rd('approval_records_clean.csv') if a['관측소명'] in ('충주', '소양강', '횡성', '광동')]
OPS = [o for o in rd('operation_from_remarks_5dams.csv') if o['operation_created'] == 'Y']
OPC = collections.Counter(o['operationType'] for o in OPS)
TSRC = collections.Counter(('측정' if o['time_source'].startswith('측정') else '승인' if o['time_source'].startswith('승인') else '비고') for o in OPS)
MEAS = sum(1 for f in ('kwater_mywater_hydr_H_aligned_wide.csv.gz', 'kwater_mywater_hydr_H_wide.csv.gz')
           for r in csv.DictReader(gzip.open(os.path.join(N, f), 'rt', encoding='utf-8-sig'))
           if r['DAM_CD'] in ('1003110', '1012110', '1006110', '1001210'))
CHUNKS = len(rd('kgv3_chunks.csv'))
USED_CH = len({r['value'] for r in rd('kgv3_properties.csv') if r['property'] == 'chunkId'})  # KG가 chunkId로 참조하는 문서 청크
V = {r['id']: r for r in rd('step6_validation.csv')}
CHK = {r['operation']: r['result'] for r in rd('operation_measured_check.csv')}
CHKC = collections.Counter(CHK.values())
assert (EC['Approval'], EC['Operation']) == (len(APPS), len(OPS)), 'KG와 승인·운영행위 수 불일치'
a_first, a_last = min(a['승인년월일시분'] for a in APPS)[:7], max(a['승인년월일시분'] for a in APPS)[:7]
NE, NR = len(ents), len(rels)
BEFORE, AFTER = V['V9']['count'], V['V10']['count']

# ------------------------------------------------------------------ 템플릿 읽기
tz = zipfile.ZipFile(TEMPLATE)
TX = tz.read('word/document.xml').decode('utf8')
BODY = TX[TX.index('<w:body>') + 8:TX.index('</w:body>')]
TOP = re.findall(r'<w:p[ >].*?</w:p>|<w:tbl>.*?</w:tbl>', BODY, flags=re.S)
SECT = re.findall(r'<w:sectPr.*?</w:sectPr>', BODY, flags=re.S)[-1]
ROOT_OPEN = TX[:TX.index('<w:body>') + 8]


def ptxt(p):
    return html.unescape(''.join(re.findall(r'<w:t(?:\s[^>]*)?>(.*?)</w:t>', p, flags=re.S)))


def tmpl_table(first_cell, nth=0):
    hits = [t for t in TOP if t.startswith('<w:tbl') and ptxt(re.findall(r'<w:tc>.*?</w:tc>', t, flags=re.S)[0]).strip() == first_cell]
    t = hits[nth]
    rows = []
    for tr in re.findall(r'<w:tr[ >].*?</w:tr>', t, flags=re.S):
        rows.append(['\n'.join(x for x in (ptxt(p) for p in re.findall(r'<w:p[ >].*?</w:p>', tc, flags=re.S)) if x) for tc in re.findall(r'<w:tc>.*?</w:tc>', tr, flags=re.S)])
    return rows


def tmpl_paras(prefix):
    return [ptxt(p) for p in TOP if p.startswith('<w:p') and ptxt(p).startswith(prefix)]


# ------------------------------------------------------------------ XML 부품 (이전 자료의 서식을 그대로 따름)
LANG = '<w:lang w:eastAsia="ko-KR"/>'
esc = lambda s: html.escape(s, quote=False)


def run(text, sz=None, b=False, color=None):
    pr = ('<w:b/>' if b else '') + ('<w:color w:val="%s"/>' % color if color else '') + ('<w:sz w:val="%d"/><w:szCs w:val="%d"/>' % (sz, sz) if sz else '') + LANG
    return '<w:r><w:rPr>%s</w:rPr><w:t xml:space="preserve">%s</w:t></w:r>' % (pr, esc(text))


def title(text1, text2):
    return ('<w:p><w:pPr><w:spacing w:before="1000"/><w:jc w:val="center"/><w:rPr>%s</w:rPr></w:pPr><w:r><w:rPr><w:b/><w:color w:val="1F4E79"/><w:sz w:val="44"/>%s</w:rPr>'
            '<w:t xml:space="preserve">%s</w:t><w:br/><w:t xml:space="preserve">%s</w:t></w:r></w:p>' % (LANG, LANG, esc(text1), esc(text2)))


def subtitle(text):
    return '<w:p><w:pPr><w:jc w:val="center"/><w:rPr>%s</w:rPr></w:pPr>%s</w:p>' % (LANG, run(text, sz=23, b=True, color='505050'))


def dateline(text):
    return '<w:p><w:pPr><w:spacing w:before="400"/><w:jc w:val="center"/><w:rPr>%s</w:rPr></w:pPr>%s</w:p>' % (LANG, run(text, color='646464'))


def label(text):
    return '<w:p><w:pPr><w:keepNext/><w:spacing w:before="240"/><w:rPr>%s</w:rPr></w:pPr>%s</w:p>' % (LANG, run(text, sz=25, b=True, color='1F4E79'))


def h1(text, pagebreak=True):
    return '<w:p><w:pPr><w:pStyle w:val="1"/>%s<w:rPr>%s</w:rPr></w:pPr>%s</w:p>' % ('<w:pageBreakBefore/>' if pagebreak else '', LANG, run(text))


def h2(text):
    return '<w:p><w:pPr><w:pStyle w:val="21"/><w:rPr>%s</w:rPr></w:pPr>%s</w:p>' % (LANG, run(text))


def para(text):
    return '<w:p><w:pPr><w:spacing w:before="60" w:after="120"/><w:rPr>%s</w:rPr></w:pPr>%s</w:p>' % (LANG, run(text, sz=BODY))


def li(text):
    return '<w:p><w:pPr><w:pStyle w:val="a0"/><w:spacing w:after="60"/><w:rPr>%s</w:rPr></w:pPr>%s</w:p>' % (LANG, run(text, sz=BODY))


def spacer():
    return '<w:p><w:pPr><w:spacing w:after="60"/><w:rPr>%s</w:rPr></w:pPr></w:p>' % LANG


BORD = ''.join('<w:%s w:val="single" w:sz="5" w:space="0" w:color="A6A6A6"/>' % s for s in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'))
MAR = '<w:tcMar><w:top w:w="80" w:type="dxa"/><w:left w:w="110" w:type="dxa"/><w:bottom w:w="80" w:type="dxa"/><w:right w:w="110" w:type="dxa"/></w:tcMar><w:vAlign w:val="center"/>'


BODY = 20  # 본문·글머리 글자 크기(10pt)
TBL = 18   # 표 안 글자 크기(9pt, 머리글·강조 상자 포함)


def cell(text, w, fill=None, b=False, color=None, center=False, sz=TBL):
    lines = [l for l in str(text).split('\n')] or ['']
    ps = ''.join('<w:p><w:pPr><w:spacing w:after="20" w:line="252" w:lineRule="auto"/>%s</w:pPr>%s</w:p>' % ('<w:jc w:val="center"/>' if center else '', run(l, sz=sz, b=b, color=color)) for l in lines)
    return '<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/>%s%s</w:tcPr>%s</w:tc>' % (w, '<w:shd w:val="clear" w:color="auto" w:fill="%s"/>' % fill if fill else '', MAR, ps)


def table(rows, widths, header=True, firstcol=True, sz=TBL):
    assert sum(widths) == 9972, (sum(widths), rows[0])
    out = ['<w:tbl><w:tblPr><w:tblW w:w="9972" w:type="dxa"/><w:jc w:val="center"/><w:tblBorders>%s</w:tblBorders><w:tblLayout w:type="fixed"/>'
           '<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/></w:tblPr><w:tblGrid>%s</w:tblGrid>'
           % (BORD, ''.join('<w:gridCol w:w="%d"/>' % w for w in widths))]
    for i, r in enumerate(rows):
        assert len(r) == len(widths), r
        hd = header and i == 0
        out.append('<w:tr><w:trPr><w:cantSplit/>%s<w:jc w:val="center"/></w:trPr>' % ('<w:tblHeader/>' if hd else ''))
        for j, (c, w) in enumerate(zip(r, widths)):
            if hd:
                out.append(cell(c, w, fill='D9EAF7', b=True, center=True, sz=sz))
            elif j == 0 and firstcol:
                out.append(cell(c, w, fill='EEF5FA', b=True, color='1F4E79', center=True, sz=sz))
            else:
                out.append(cell(c, w, sz=sz))
        out.append('</w:tr>')
    out.append('</w:tbl>')
    return ''.join(out) + spacer()


def box(lab, text, w1=1944):
    return table([[lab, text]], [w1, 9972 - w1], header=False, sz=TBL)


def lead(head, text):
    return '<w:p><w:pPr><w:spacing w:before="60" w:after="100"/><w:rPr>%s</w:rPr></w:pPr>%s%s</w:p>' % (LANG, run(head + '  ', sz=BODY, b=True, color='1F4E79'), run(text, sz=BODY))


def flow(items):
    n = len(items)
    aw = 300
    bw = (9972 - aw * (n - 1)) // n
    ws = []
    for i in range(n):
        ws.append(bw)
        if i < n - 1:
            ws.append(aw)
    ws[-1] += 9972 - sum(ws)
    out = ['<w:tbl><w:tblPr><w:tblW w:w="9972" w:type="dxa"/><w:jc w:val="center"/><w:tblLayout w:type="fixed"/></w:tblPr><w:tblGrid>%s</w:tblGrid><w:tr><w:trPr><w:cantSplit/></w:trPr>' % ''.join('<w:gridCol w:w="%d"/>' % w for w in ws)]
    k = 0
    for i, t in enumerate(items):
        out.append(cell(t, ws[k], fill='EEF5FA', b=False, center=True, sz=TBL).replace('<w:tcPr>', '<w:tcPr>', 1))
        k += 1
        if i < n - 1:
            out.append(cell('→', ws[k], center=True, sz=TBL))
            k += 1
    out.append('</w:tr></w:tbl>')
    return ''.join(out) + spacer()


# ------------------------------------------------------------------ 본문
B = []
add = B.append
add(title('KG 구축 방법', '2.1 ~ 2.5 정리 초안'))
add(dateline('2026.10 랩미팅 방법론 정리'))
add(h1('2. KG 구축', pagebreak=False))
add(para('Ontology(1장)에 맞춰 실제 자료로 KG를 만드는 과정이다. 구축은 DDKG(Huang 2026)의 구성(출처와 전처리 → 지식 추출 → 저장)을 따르고, 구조화 자료의 매핑은 OntoDSMS(Zhou 2023)의 원리를 따른다.'))

# ---------------------------------------------------------------- 2.1
add(h2('2.1 사용 데이터'))
add(label('데이터 출처와 범위'))
add(table([
    ['자료', '출처', '범위'],
    ['① 방류 승인 기록', '한강홍수통제소 홍수예보 댐방류승인 (공공데이터포털, CSV)', '충주·소양강·횡성·광동 4개 댐 승인 %d건 (%s ~ %s)' % (len(APPS), a_first, a_last)],
    ['② 수문기상 시간 자료', 'K-water MyWater', '4개 댐 × 6개 변수(수위, 저수량, 강우량, 유입량, 총방류량, 저수율), 시간별 %s행 (충주·횡성 2010-08~, 소양강 2011-06~, 광동 2016-06~ 2026-09)' % format(MEAS, ',')],
    ['③ 연계운영규정 별표3', '법제처 국가법령정보 (XML)', '홍수기 제한수위 (현행 판과 시행일이 다른 연혁 판)'],
    ['④ 댐 기본 정보', 'K-water MyWater', '4개 댐의 댐 코드, 이름, 유형'],
], [2200, 3772, 4000]))
add(label('데이터 구조'))
add(para('① 방류 승인 기록: 한 행이 승인 한 건이다.'))
add(table([
    ['순차번호', '관측소코드', '관측소명', '승인년월일시분', '방류시작시간', '접수방류량', '비고'],
    ['1368', '1003110', '충주', '2012-08-24', '2012-08-24 15:00', '2000', '이내 탄력적 조정'],
    ['2327', '1001210', '광동', '2016-07-15', '2016-07-16 12:00', '100', '(초기수문방류 100㎥/s)'],
    ['279', '1006110', '횡성', '2010-09-10', '2010-09-10 17:00', '100', '9.11 16:00 수문방류종료'],
], [900, 1200, 1000, 1500, 1900, 1200, 2272], firstcol=False))
add(para('② 수문기상 시간 자료: 한 행이 한 댐의 한 시각이다.'))
add(table([
    ['DAM_CD', 'SDATE_raw', '수위(EL.m)', '저수량(MCM)', '강우량(mm)', '유입량(CMS)', '총방류량(CMS)', '저수율(%)'],
    ['1003110', '2012082416', '134.18', '1697.5206', '0', '1152.728', '944.784', '61.7'],
], [1100, 1300, 1150, 1250, 1100, 1250, 1450, 1372], firstcol=False))
add(para('③ 연계운영규정 별표3: 법제처 XML 안에 선 문자로 그려진 표가 글자로 들어 있다.'))
add(table([
    ['[별표 3] 댐의 홍수기 제한수위(제6조)\n┌───┬─────┬─────┬────────┬──────────┐\n│구 분 │댐 종류   │댐 명     │홍수기 제한수위 │시설별 최저 운영수위│\n│      │          │          │(EL.m)          │(EL.m)              │\n├───┼─────┼─────┼────────┼──────────┤\n│한 강 │다목적댐  │소양강댐  │190.3           │-                   │\n│수 계 │          │충 주 댐  │138.0           │-                   │\n│      │          │횡 성 댐  │178.2           │-                   │'],
], [9972], header=False, firstcol=False))
add(para('④ 댐 기본 정보: 한 행이 댐 한 곳이다.'))
add(table([
    ['DAM_CD', 'DAM_NM_source', 'RIVR_NM_source_label', 'DAM_BO_NM_source'],
    ['1003110', '충주댐', '한강', '다목적댐'],
], [2000, 2600, 2900, 2472], firstcol=False))

# ---------------------------------------------------------------- 2.2
add(h2('2.2 구축 절차 개요'))
add(table([
    ['단계', '하는 일', '따르는 문헌'],
    ['1 전처리', '중복 제거, 시각 표기 정리, 필요한 부분 골라냄', 'DDKG 3.2.1'],
    ['2 구조화 자료 매핑', '열이 정해진 표를 개체·속성으로 옮김', 'OntoDSMS'],
    ['3 문서 자료 추출', '글에서 규칙(키워드, 정규식)으로 값을 뽑음', 'DDKG 3.2.2'],
    ['4 관계 연결', '개체 사이 관계를 만들고 모든 정보를 Dam에 연결', 'DDKG 3.1'],
    ['5 검증', '허용 규칙으로 관계를 검사하고 필요하면 Ontology를 보완', 'DDKG 3.2.3 식 (10)~(11)'],
    ['6 저장', 'KG는 Neo4j에, 측정값과 원문은 각 저장소에 적재', 'DDKG 3.3'],
], [2400, 5372, 2200]))
add(para('이 절에서는 단계 1~3을 정리한다.'))

# ---------------------------------------------------------------- 2.3
add(h2('2.3 단계 1. 전처리'))
add(lead('필요한 이유', '자료를 KG로 옮기기 전에 같은 자료가 두 번 세어지거나 시각 표기가 어긋나는 문제를 없애고, 필요한 부분만 골라낸다. 원본은 바꾸지 않고, 정리한 내용은 로그로 남긴다.'))
add(lead('문헌에서 가져온 원리', 'DDKG(3.2.1)는 지식을 추출하기 전에 자료의 잡음을 줄이고 형식을 통일한다. 형식을 변환하고, 정규식으로 필요한 지식이 들어 있는 부분의 경계를 찾아 불필요한 내용을 없앤 뒤, 하나의 모음으로 합친다. 우리도 같은 원리로 자료마다 필요한 만큼만 정리한다.'))
add(table([
    ['자료', '전처리', '결과'],
    ['① 방류 승인 기록', '값이 모두 같고 순차번호만 다른 중복 행은 첫 행만 남긴다. 제거한 행은 로그에 기록한다. 4개 댐의 행만 선택한다.', '한강수계 전체 3,929행 → 중복 7행 제거 3,922행 → 4개 댐 %d건.\n예) 순차번호 2220은 2218과 값이 모두 같아 제거 (광동, 2016-07-04 18:00, 200㎥/s)' % len(APPS)],
    ['② 수문기상 시간 자료', '처음 받은 자료와 승인 기간에 맞춰 추가로 받은 자료를 열 구조가 같은 표로 정리한다. 4개 댐의 행만 선택한다. 시각 라벨의 24시 표기를 다음날 0시로 바꾼다. 빈 값은 채우지 않고 그대로 둔다.', '4개 댐 × 6개 변수, %s행.\n예) 2016062924 → 2016-06-30 00:00' % format(MEAS, ',')],
    ['③ 연계운영규정 별표3', '규정 XML에서 별표 번호로 별표3 부분만 골라낸다.', '별표3 한 판의 텍스트'],
    ['④ 댐 기본 정보', '4개 댐의 행만 선택한다.', '4개 댐'],
], [2000, 4772, 3200]))
add(box('확인 필요', '③ 연혁 판: 시행일이 다른 판 중 3개 판(2013-01-01, 2013-04-17, 2016-04-29)은 법제처 XML의 별표 내용이 비어 있고 HWP 첨부로만 제공된다. 이 판들의 처리 방법은 결정이 필요하다.'))

# ---------------------------------------------------------------- 2.4
add(h2('2.4 단계 2. 구조화 자료 매핑'))
add(lead('필요한 이유', '열과 행이 정해진 표는 해석 없이 Ontology의 개체와 속성으로 옮길 수 있다. 어느 표와 열이 어느 Class와 Data Property가 되는지 규칙을 먼저 정해 두면, 같은 표는 항상 같은 결과가 나온다.'))
add(lead('문헌에서 가져온 원리', 'OntoDSMS(Zhou 2023)는 관계형 DB의 표를 Ontology에 다음과 같이 대응시킨다. 또 DB의 값은 복사하지 않고, 필요할 때 읽을 수 있도록 연결만 둔다.'))
add(table([
    ['표(DB)의 요소', '대응', '예'],
    ['표 하나', 'Class 하나', '댐 표 → Dam'],
    ['열', '그 Class의 Data Property', '댐이름 열 → damName'],
    ['행', '개체(Entity)', '‘충주댐’ 행 → 충주댐 개체'],
    ['칸의 값', 'Data Property의 값', '“충주댐” → damName = 충주댐'],
    ['대량 값', '복사하지 않고 DB에 둔 채 연결', '측정값 → 측정자료 저장소'],
], [2400, 3500, 4072]))
add(lead('우리 적용', '구조화 자료인 ④ 댐 기본 정보, ① 승인 기록의 앞 열, ② 수문기상 시간 자료에 같은 대응을 적용한다. Entity에는 Ontology에서 정한 Data Property를 붙이고, 외부 저장소에서 값을 찾아갈 키도 Data Property로 둔다.'))
add(table([
    ['자료', 'Class', '개체 ID 규칙', '만들어지는 개체와 속성 (예)'],
    ['④ 댐 기본 정보', 'Dam', 'DAM:댐코드', 'DAM:1003110\ndamName = 충주댐\ndamType = 다목적댐'],
    ['① 승인 기록 (앞 열)', 'Approval', 'APR:순차번호', 'APR:1368\napprovalTime = 2012-08-24\napprovalContent = “방류시작 2012-08-24 15:00; 접수방류량 2000㎥/s; 비고: 이내 탄력적 조정”'],
    ['① 승인 기록 (한 행)', 'EvidenceSource', 'EVI:AP:순차번호', 'EVI:AP:1368\nsourceTitle = 환경부 한강홍수통제소 홍수예보 댐방류승인\nsourceType = 승인자료\nsourceLocator = 순차번호 1368'],
    ['② 수문기상 시간 자료', 'HydrometeorologicalState', 'HMS:댐코드:변수', 'HMS:1003110:수위\nvariableType = 수위\nstationCode = 1003110 (측정값을 찾아가는 키)'],
    ['② 수문기상 시간 자료 (댐별)', 'EvidenceSource', 'EVI:KW:댐코드', 'EVI:KW:1003110\nsourceTitle = K-water MyWater 수문 시간자료\nsourceType = 측정자료\nsourceLocator = DAM_CD=1003110 충주댐 시간별 자료'],
], [2300, 2000, 1700, 3972]))
add(para('시간 자료는 값이 아니라 “어느 댐에 어떤 변수가 있는가”를 개체로 만든다. 댐 4개 × 변수 6개로 상태 개체 %d개가 만들어지고, 시간별 측정값 %s행은 KG에 넣지 않고 측정자료 저장소에 그대로 둔다. 질문이 오면 상태 개체의 stationCode(댐 코드)와 시각으로 저장소에서 값을 읽는다.' % (EC['HydrometeorologicalState'], format(MEAS, ','))))

# ---------------------------------------------------------------- 2.5
add(h2('2.5 단계 3. 문서 자료 추출'))
add(lead('필요한 이유', '운영행위의 종류와 제한수위 값은 표의 열에 있지 않고 글 속에 있어서, 글을 읽어 값을 뽑아야 한다.'))
add(lead('문헌에서 가져온 원리', 'DDKG(3.2.2)는 정해진 형태로 서술된 내용을 정규식(규칙)으로 바로 추출한다. 예를 들어 “안전성 평가 등급은 C등급이다”라는 문장에서 “C”를 규칙으로 뽑으며, 딥러닝이 필요 없다. 우리 자료의 글(승인 비고, 별표3)은 모두 정해진 형태가 있어 같은 원리로 규칙을 쓴다.'))
add(label('A. 승인 기록의 비고 → Operation 종류'))
add(para('비고에서 아래 문구를 찾아 운영행위의 종류(operationType)를 정한다. 한 비고에서 여러 문구가 잡히면 각각 Operation 한 개로 만든다.'))
add(table([
    ['비고 원문 (승인 순차번호)', '걸리는 문구 (규칙)', 'Operation 종류'],
    ['(초기수문방류 100㎥/s) (2327)', '“초기방류”, “초기수문방류”', '초기방류'],
    ['10cms 증 (394)', '“증가방류”, “숫자 cms 증”', '증가방류'],
    ['이내 점증방류 (1103)', '“점진”, “점증”', '점진·점증방류'],
    ['9.11 16:00 수문방류종료 (279)', '“방류종료”', '방류종료'],
    ['이내 탄력적 조정 (1368)', '“탄력”', '탄력적 방류 (원문 용어를 보존)'],
    ['수문방류 승인 (473)', '“수문방류”, “이내 방류” 등 일반 방류 문구', '방류 (일반)'],
    ['(비고 없음) (418)', '-', '방류 (일반, 종류 미상)'],
    ['이내 변경승인(기존 500 ㎥/s), 방류 시간 정정', '“변경”, “연장”, “정정”', 'Operation을 만들지 않음 (같은 방류의 변경)'],
], [3300, 3300, 3372]))
add(para('결과: 승인 %d건에서 Operation %d개가 만들어졌다(%s).' % (len(APPS), len(OPS), ', '.join('%s %d' % kv for kv in OPC.most_common()))))
add(box('확인 필요', '운영행위 시각(operationTime): 현재 구현은 승인의 방류시작시간 앞 3시간~뒤 6시간의 측정 방류량 변화로 보정한다. 이 기준은 문헌에 근거가 없어, 승인에 적힌 방류시작시간을 그대로 쓰는 방안과 비교하여 정해야 한다.'))
add(label('B. 별표3 → Criterion'))
add(para('별표3는 선 문자로 그린 표가 글자로 들어 있다. “│”로 시작하는 줄을 “│” 기준으로 잘라 셀로 읽고(구분, 댐 종류, 댐 이름, 홍수기 제한수위, 시설별 최저 운영수위), 댐 이름의 공백을 제거한다.'))
add(table([
    ['별표3 원문 (줄)', '읽은 결과', '만들어지는 Criterion'],
    ['│한 강 │다목적댐 │소양강댐 │190.3 │-│', '댐 이름 소양강댐, 제한수위 190.3', 'criterionType 홍수기 제한수위, criterionValue 190.3, unit EL.m'],
    ['│수 계 │ │충 주 댐 │138.0 │-│', '댐 이름 “충 주 댐” → 충주댐, 제한수위 138.0', 'criterionValue 138.0'],
    ['│ │ │횡 성 댐 │178.2 │-│', '댐 이름 “횡 성 댐” → 횡성댐, 제한수위 178.2', 'criterionValue 178.2'],
    ['(광동댐 줄 없음)', '별표3에 수록되지 않음', 'Criterion 없음'],
], [3300, 3300, 3372]))
add(label('C. 별표3 원문 → 문서 저장소'))
add(para('제한수위를 답변의 근거로 보이려면 값뿐 아니라 별표3 원문(표와 각주)이 필요하다. 원문은 고치지 않고 문서 저장소에 두고, 근거자료(EvidenceSource) 개체에 찾아갈 키(sourceLocator)를 붙여 KG와 연결한다. 이 방식은 ② 시간 자료와 같다. 값 전체는 KG 밖에 두고, KG에는 찾아가는 키만 둔다.'))
add(table([
    ['자료', 'KG 안 (개체와 키)', 'KG 밖 (저장소)'],
    ['② 수문기상 시간 자료', '상태 개체의 stationCode', '측정자료 저장소: 시간별 측정값'],
    ['③ 별표3', '근거자료 개체의 sourceLocator (예: 별표 3)', '문서 저장소: 별표3 원문'],
], [2600, 4172, 3200]))
add(box('확인 필요', '현재 구현은 문서 번호를 chunkId(예: LAW:별표3)라는 별도 속성으로 붙이고 있다. Ontology 설계의 sourceLocator로 일원화할지 정해야 한다. 또 연혁 판 9개는 원문이 아니라 연혁 표에서 만든 요약 문장이 저장되어 있어, 원문(XML 6개 판, HWP 첨부 3개 판)으로 바꿀지 정해야 한다.'))

doc = ROOT_OPEN + ''.join(B) + SECT + '</w:body></w:document>'
import xml.dom.minidom
xml.dom.minidom.parseString(doc.encode('utf8'))
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as zo:
    for item in tz.infolist():
        data = tz.read(item.filename)
        if item.filename == 'word/document.xml':
            data = doc.encode('utf8')
        zo.writestr(item, data)
print('저장', OUT, len(B))
