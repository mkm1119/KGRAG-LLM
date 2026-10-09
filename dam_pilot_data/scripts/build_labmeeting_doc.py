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
MEAS = sum(1 for r in csv.DictReader(gzip.open(os.path.join(N, 'kwater_mywater_hydr_H_aligned_wide.csv.gz'), 'rt', encoding='utf-8-sig'))
           if r['DAM_CD'] in ('1003110', '1012110', '1006110', '1001210'))
CHUNKS = len(rd('kgv3_chunks.csv'))
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
add(title('댐 운영 판단 지원을 위한', 'Ontology–KG–Hybrid Retrieval–LLM 연구 진행'))
add(subtitle('Ontology 설계 → KG 구축 → 검색·LLM 답변 예비 테스트'))
add(dateline('2026.10 랩미팅'))
add(label('주차별 연구 진행 정리'))
add(table([
    ['구분', '주요 내용'],
    ['전주\nOntology 설계', '• Noy & McGuinness(2001)의 개발 절차를 참고하여 Ontology 설계 수행\n• 전체 질문 1개와 세부 질문 6개(CQ1~CQ6) 설정, 주요 용어 166개 정리\n• Class 6개, Relation 8개, Data Property 설계, 대량 측정자료는 KG 밖에서 조회하는 구조 설정'],
    ['이번주\nKG 구축 및\n검색·답변 예비 테스트',
     '• 4개 댐(충주·소양강·횡성·광동)의 방류 승인 %d건, K-water 시간별 수문기상 자료(약 %.1f만 행), 연계운영규정 별표3 등을 수집·정리\n'
     '• 근거 문헌의 방법을 참고하여 KG 구축: 개체 %d개, 관계 %d개, Ontology 적합성 검사 통과\n'
     '• CQ 답변 가능성 점검 중 Approval–Dam 연결 부재를 발견하여 Relation 1개 추가(8개 → 9개)\n'
     '• 질문 → 의도 분류(LLM) → Neo4j·측정자료·문서 조회 → 근거 묶음 → 답변 생성 흐름을 구현하고 Qwen3-8B로 질문 10개를 예비 테스트' % (len(APPS), MEAS / 10000, NE, NR)],
    ['다음주\n개선 및 확장', '• 예비 테스트에서 발견한 오류의 수정 반영 후 재실행, 더 큰 모델(32B)과 비교\n• 같은 LLM에 표 데이터를 그대로 주는 방식과 KG 방식 비교\n• 사람 검토: 비고 분류 정확도, 연구자 지정 임시 기준(행위 시각, 유사 사례)\n• 실제 운영기록 확보 방안 정리(한수원 현장 방문 등)'],
], [1701, 8271]))

# ---- 1장
add(h1('1. Ontology 구조와 개념 정리'))
add(para('전주에 설계한 Ontology의 구조와 정의를 정리한다. 이후 KG 구축과 검색·답변은 이 구조를 기준으로 수행하였다.'))
add(h2('1.1 용어 정리'))
terms = tmpl_table('용어')
terms += [['Intent (의도)', '사용자 질문이 CQ 중 어느 질문에 해당하는지 나타내는 분류. 의도마다 가져올 근거의 구성이 정해져 있다.'],
          ['근거 묶음 (Evidence Bundle)', '의도에 따라 KG, 측정자료, 문서에서 가져온 근거를 LLM이 읽을 수 있게 정리한 입력. 비교에 필요한 값은 프로그램이 계산하여 포함한다.']]
add(table(terms, [2300, 7672]))
add(h2('1.2 연구 목적과 Ontology가 답해야 할 질문'))
add(box('연구 목적', tmpl_table('Purpose(연구 목적)')[0][1]))
add(box('전체 질문', tmpl_table('전체 질문')[0][1]))
add(table(tmpl_table('번호'), [800, 2200, 6972]))
add(h2('1.3 Class (6개)'))
add(table(tmpl_table('Class'), [2200, 3200, 1700, 2872]))
add(h2('1.4 Relation (8개)'))
add(table(tmpl_table('Subject'), [2000, 2500, 2200, 3272]))
add(h2('1.5 Data Property'))
add(table(tmpl_table('Class', 1), [2300, 3100, 4572]))
add(h2('1.6 KG와 외부 저장소의 역할'))
add(table([
    ['구분', '저장하는 것', '예'],
    ['KG', '의미와 관계, 근거 위치, 외부 자료를 찾아가는 정보', '승인·운영행위 Entity, 변수 종류와 측정소 코드, 근거자료의 위치'],
    ['측정자료 저장소', '시간별 실제 측정 시계열 값 전체', '수위, 유입량, 방류량 등'],
    ['문서 저장소', '규정·법령 문서 원문(조문 단위)', '연계운영규정 별표3, 하천법 조문'],
], [2300, 4000, 3672]))
add(box('KG의 역할', tmpl_table('KG의 역할')[0][1]))

# ---- 2장 KG 구축
add(h1('2. KG 구축'))
add(h2('2.1 구축 대상 자료'))
add(table([
    ['자료', '출처', '범위', '사용'],
    ['방류 승인 기록', '한강홍수통제소 댐방류승인(공공데이터포털)', '충주·소양강·횡성·광동 4개 댐 %d건 (%s ~ %s)' % (len(APPS), a_first, a_last), 'Approval, Operation'],
    ['수문기상 시간자료', 'K-water MyWater', '4개 댐 × 6개 변수(수위, 저수량, 강우량, 유입량, 총방류량, 저수율), 시간별 %s행 (충주·횡성 2010-08~, 소양강 2011-06~, 광동 2016-06~ 2026-09)' % format(MEAS, ','), '측정자료 저장소, 상태 Entity'],
    ['홍수기 제한수위', '연계운영규정 별표3(법제처) 및 연혁 9개 판', '충주 138.0, 소양강 190.3, 횡성 178.2 EL.m (광동댐은 별표3에 수록되지 않음)', 'Criterion'],
    ['법령·규정 조문', '법제처 국가법령정보(XML)', '연계운영규정 조문·별표, 하천법·시행령·댐건설관리법 관련 조문 %d개 청크' % CHUNKS, '문서 저장소, 근거 위치'],
], [1700, 2500, 4272, 1500]))
add(box('범위', '테스트 대상은 K-water 관리 4개 댐으로 하고, 수문기상 자료는 K-water 시간별 6개 변수를 사용하였다. 충주조정지는 테스트 범위에서 제외하였다.'))
add(h2('2.2 구축 절차 개요'))
add(para('구축은 7단계로 수행하였다. 각 단계는 근거 문헌의 방법을 참고하였고, 문헌에 방법이 없는 부분은 연구자 판단이라고 표시하였다. 단계별 내용은 2.3~2.9에 정리하였다.'))
add(flow(['1 소스 구분\nDDKG', '2 전처리\nDDKG · Zhang', '3 구조화 자료 매핑\nOntoDSMS', '4 비정형 텍스트 추출\nDDKG', '5 개체 해소·연결\nGraphAide', '6 정규화·검증\nGraphAide · DDKG · Noy', '7 저장\nDDKG · GraphAide']))

add(h2('2.3 단계 1. 소스 구분'))
add(lead('필요한 이유', '표로 정리된 자료는 값을 Ontology 구조에 옮기면 되지만, 문장으로 된 자료는 의미를 읽어 분류해야 한다. 자료 유형에 따라 이후 처리 방식이 달라지므로 먼저 구분한다.'))
add(lead('문헌의 방법', 'DDKG(Huang 2026, 3.2.1)는 관리 플랫폼의 구조화된 표는 Dam, Properties, Location, Parameter 등 상위 클래스의 자료로 쓰고, PDF·DOC 등 비정형 텍스트는 HazardForm, HazardComponent, SafetyEvaluation 클래스의 자료로 구분하여 서로 다른 방식으로 처리한다.'))
add(lead('우리가 수행한 내용', '수집한 자료를 아래와 같이 구분하였다.'))
add(table([
    ['구분', '자료', '이후 처리'],
    ['구조화 자료', '승인 CSV, K-water 시간별 측정자료, 별표3 표', '단계 3: 규칙표로 Entity·속성·관계에 매핑'],
    ['비정형 텍스트', '승인 비고(방류 종류, 비고 문구)', '단계 4: 규칙으로 Operation 추출'],
    ['비정형 텍스트', '규정·법령 조문', '단계 2: 조문 단위로 분할 → 문서 저장소(청크)'],
], [1800, 4172, 4000]))

add(h2('2.4 단계 2. 전처리'))
add(lead('필요한 이유', '매핑과 추출 전에 중복과 표기 차이를 정리해 같은 자료가 두 번 세어지거나 시각이 어긋나지 않게 한다. 원본은 바꾸지 않고, 수정한 내용은 로그로 남긴다.'))
add(lead('문헌의 방법', 'DDKG(3.2.1)는 비정형 텍스트를 마크다운으로 변환(OCR 포함)하고, 정규식으로 지식이 있는 블록의 경계를 나누어 불필요한 내용을 제거한 뒤 하나의 코퍼스로 통합한다. Zhang(2025)은 수집 문서를 OCR 후 문서·문장·단어 수준에서 걸러 정제한다(저장소에 PDF가 없어 기존 정리 내용을 인용). 두 문헌 모두 구조화된 표의 정제 방법은 다루지 않는다.'))
add(lead('우리가 수행한 내용', '법령은 XML 원문이 이미 조문 단위로 구조화되어 있어 OCR은 필요 없고, 조문·별표 단위로 분할하였다. 구조화 자료의 정제는 문헌이 없어 연구자 판단으로 아래와 같이 정하였다.'))
add(table([
    ['대상', '처리', '결과'],
    ['승인 CSV', '값이 모두 같고 순차번호만 다른 중복 행은 첫 행만 남기고 제거, 제거 행은 로그에 기록', '3,929행 중 7행 제거 → 3,922행. 4개 댐에서는 광동댐 1건 제거, 충주조정지 제외 후 승인 %d건' % len(APPS)],
    ['측정 시간자료', '시각 라벨 24시 표기를 다음날 0시로 변환, 결측은 채우지 않고 비워 둠', '4개 댐 × 6개 변수, %s행' % format(MEAS, ',')],
    ['법령 XML', '조문·별표 단위로 분할', '문서 청크 %d개' % CHUNKS],
], [1800, 4572, 3600]))
add(box('판단 표시', '구조화 자료의 중복 제거 기준과 시각 변환은 문헌에 없어 연구자 판단으로 정하였다.'))

add(h2('2.5 단계 3. 구조화 자료 매핑'))
add(lead('필요한 이유', '구조화 자료의 값을 해석을 더하지 않고 Ontology의 Class·속성·관계로 옮기기 위해 변환 규칙을 먼저 정한다.'))
add(lead('문헌의 방법', 'OntoDSMS(Zhou 2023)는 D2RQ로 관계형 DB와 온톨로지를 매핑한다. 원칙은 표는 Class, 열은 DatatypeProperty, 행은 Instance에 대응시키는 것이고, 가상 RDF 그래프를 두어 데이터를 복제하지 않고 접근한다.'))
add(lead('우리가 수행한 내용', 'D2RQ 도구는 쓰지 않고 같은 원칙을 규칙표로 적용하였다. 값은 원자료 그대로 옮기고, 측정값 전체와 문서 원문은 KG로 복제하지 않고 조회 키만 두었다.'))
add(table([
    ['Class', '원천', 'ID', '속성 · 관계'],
    ['Dam', '승인 파일의 시설, MyWater 댐 정보', 'DAM:시설코드', 'damName, damType'],
    ['HydrometeorologicalState', '시간자료의 변수 6종', 'HMS:시설코드:변수 (댐 × 변수 = %d개)' % EC['HydrometeorologicalState'], 'variableType, stationCode(측정자료 조회 키로 K-water 시설 코드 사용) / hasHydrometeorologicalState'],
    ['Approval', '승인 CSV 한 행', 'APR:순차번호', 'approvalTime(승인일), approvalContent(방류 시작, 접수방류량, 비고를 한 문장으로) / concernsDam'],
    ['Criterion', '별표3', 'CRI:번호', 'criterionType, criterionValue, unit / appliesToDam'],
    ['EvidenceSource', '승인 레코드, 측정 소스, 별표3와 연혁', 'EVI:출처', 'sourceTitle, sourceType, sourceLocator, chunkId(규정 근거) / 다른 Class에서 supportedBy'],
], [2300, 2400, 2372, 2900]))

add(h2('2.6 단계 4. 비정형 텍스트 추출'))
add(lead('필요한 이유', '운영행위(Operation)의 종류는 승인 비고의 문구(초기방류, 증가방류 등)로만 알 수 있어, 비고를 읽고 분류해야 한다.'))
add(lead('문헌의 방법', 'DDKG(3.2.2)는 안전평가 등급처럼 표준화된 표현은 정규식으로 직접 추출하고, 복잡하고 다양한 표현(결함 설명)은 LLM 기반 분류(3.2.3)로 처리한다. GraphAide(Purohit 2024)는 온톨로지를 입력으로 주어 LLM의 응답 스키마를 제한한다.'))
add(lead('우리가 수행한 내용', '승인 비고가 짧고 정해진 틀로 쓰여 있어 규칙 기반 추출을 선택하였다(LLM 추출은 사용하지 않음). 같은 입력에서 같은 결과가 나오고 규칙을 그대로 보일 수 있다.'))
add(table([
    ['규칙', '내용'],
    ['종류 분류', '승인 비고의 문구로 분류한다: 초기방류, 증가방류, 점진·점증방류, 방류종료, 탄력적 방류(원문 용어를 보존), 그 밖의 방류 문구는 일반 방류'],
    ['비고가 없는 승인', '해당 시각의 방류 승인이므로 일반 방류 Operation으로 포함한다(종류 미상).'],
    ['변경 승인', '같은 방류의 기간·양 변경이므로 새 Operation을 만들지 않고, 같은 댐·같은 방류 시작 시각의 원 승인 Operation에 연결한다(추정 표시, 변경 승인 17건 중 11건 연결).'],
    ['행위 시각', '방류 시작 시각 앞 3시간~뒤 6시간에서 총방류량이 직전보다 1 CMS 또는 10%% 이상 변한 시각 중 시작에 가장 가까운 것. 변화가 없으면 승인의 방류 시작 시각.'],
    ['결과', '승인 %d건에서 Operation %d개: %s. 시각 출처는 측정 변화 %d, 승인 시작 %d, 비고 명시 %d.' % (len(APPS), len(OPS), ', '.join('%s %d' % kv for kv in OPC.most_common()), TSRC['측정'], TSRC['승인'], TSRC['비고'])],
], [2000, 7972]))
add(box('판단 표시', '행위 시각 기준(앞 3시간~뒤 6시간, 1 CMS 또는 10%)은 연구자가 정한 임시 기준이며 규정·문헌에 근거가 없다. 승인 시각과 다른 실제 행위 시각을 측정 변화로 찾기 위해 도입하였다.'))

add(h2('2.7 단계 5. 개체 해소·연결'))
add(lead('필요한 이유', '같은 댐이 자료마다 "충주", "충주댐", "충 주 댐"처럼 다르게 적혀 있어, 같은 Dam으로 연결하지 않으면 승인·측정·기준 사이의 경로가 끊긴다.'))
add(lead('문헌의 방법', 'GraphAide(Purohit 2024)는 텍스트에서 추출한 개체 언급을 외부 식별자(Wikidata QID)에 대응시키는데, LLM과 벡터 검색으로 후보를 찾아 재순위하여 중의성을 해소한다.'))
add(lead('우리가 수행한 내용', '우리 자료는 모호한 문장 속 언급이 아니라 시설 코드와 이름이 있는 표여서, 코드나 이름이 일치할 때만 연결하고 추측으로 연결하지 않았다.'))
add(table([
    ['연결', '기준', '결과'],
    ['승인 파일 → Dam', '승인 파일의 관측소 코드가 K-water 댐 코드와 같으면 같은 Dam', '4개 댐의 승인 %d건 모두 연결' % len(APPS)],
    ['별표3 → Dam', '이름의 공백을 제거하여 일치(“충 주 댐” → 충주댐)', '충주·소양강·횡성 3개 댐. 광동댐은 별표3에 없어 Criterion 없음'],
    ['측정자료 → 상태 Entity', 'K-water 시설 코드를 stationCode로 사용', '댐 × 변수 %d개 Entity' % EC['HydrometeorologicalState']],
], [2300, 4372, 3300]))

add(h2('2.8 단계 6. 정규화와 Ontology 검증'))
add(lead('필요한 이유', '만든 KG가 정의한 Ontology를 지키는지, CQ에 답하는 데 필요한 경로가 실제로 이어지는지를 확인한다.'))
add(lead('문헌의 방법', 'GraphAide는 Pydantic 스키마 검증기로 생성된 서브그래프의 일관성을 유지한다. DDKG(OHCF)는 분류 결과가 온톨로지 제약에 어긋나는 라벨 쌍을 걸러내는 일관성 검사를 둔다. Noy & McGuinness(2001)는 속성에 값 유형·개수(cardinality) 제약을 정의하도록 한다.'))
add(lead('우리가 수행한 내용', '관계의 양 끝 Class, 필수 속성, 값 형식, 근거 연결, 경로 일치를 검사하고, 이어서 CQ별 답변 가능성을 점검하였다.'))
add(table([
    ['검사', '결과'],
    ['모든 관계의 양 끝이 허용된 Class 쌍', '통과'],
    ['Class별 필수 Data Property가 모두 있음', '통과'],
    ['날짜·시각·수치 값 형식', '통과'],
    ['상태·운영행위·승인·기준이 모두 근거자료에 연결됨', '통과'],
    ['승인의 댐과 그 승인이 허가한 운영행위의 댐이 같음', '통과'],
], [6000, 3972]))
add(table([
    ['CQ', '점검 결과', '판정'],
    ['CQ1 현재 상태', '4개 댐 모두 6개 변수 조회 (기준 시각 2026-09-28 23:00)', '가능'],
    ['CQ2 과거 상태', '승인 %d건, 운영행위 %d개 모두 방류 전후 상태 조회, 임의 과거 시점도 조회' % (len(APPS), len(OPS)), '가능'],
    ['CQ3 과거 운영행위', '운영행위 %d개. 실제 수행 여부는 방향이 있는 행위 18개 중 %d개에서 측정 방류량 변화 방향과 일치 확인(KG 밖 검증)' % (len(OPS), CHKC['일치']), '부분 (실제 운영기록 없음)'],
    ['CQ4 과거 방류 승인', '수정 후 %s건 (수정 전 %s건)' % (AFTER, BEFORE), '가능'],
    ['CQ5 현재 운영기준', '충주 138.0, 소양강 190.3, 횡성 178.2 EL.m. 광동댐은 별표3에 없어 기준 없음', '가능 (3개 댐)'],
    ['CQ6 공식 근거', '승인, 운영행위, 상태, 제한수위 모두 근거자료와 위치 연결 (운영행위의 근거는 승인 레코드와 동일)', '가능'],
    ['통합 질문', '운영행위 %d개 모두 상태·승인·근거 조립, 제한수위까지 이어지는 사례 41건' % len(OPS), '가능'],
], [2200, 5772, 2000]))
add(box('발견한 문제', '운영행위가 없는 승인(변경 승인 등)은 Dam에서 찾아갈 경로가 없어, 댐에서 도달 가능한 승인이 %s건에 그쳤다(Approval → Operation → Dam 경로만 존재).' % BEFORE))
add(box('수정', 'Relation concernsDam(Approval → Dam)을 추가하여 %s건 모두 도달 가능하게 하였다. 승인 레코드의 시설 코드로 연결하므로 추정이 없다.' % AFTER))
add(table([
    ['수정된 Ontology', '변경 내용'],
    ['Class', '6개 (변경 없음)'],
    ['Relation', '8개 → 9개: Approval –concernsDam→ Dam 추가'],
    ['Data Property', 'EvidenceSource에 chunkId 추가 (문서 저장소의 조문 청크를 찾아가는 키로, HydrometeorologicalState의 stationCode와 같은 역할)'],
], [2300, 7672]))

add(h2('2.9 단계 7. 저장과 구축 결과'))
add(lead('필요한 이유', '승인 → 운영행위 → 댐 → 상태처럼 여러 단계의 관계를 따라가는 질문에 답하려면 관계 탐색과 질의 언어를 지원하는 저장소가 필요하다.'))
add(lead('문헌의 방법', 'DDKG(3.3)는 Neo4j와 Cypher를 사용한다. 추출 결과를 JSON으로 모으고 Python 스크립트가 이를 읽어 Cypher 문을 만들어 노드와 관계를 일괄 적재하며, 201,362개 노드와 953,447개 관계를 구축하였다. GraphAide도 Neo4j를 사용하고, 시계열 자료는 시계열 DB를 외부 함수로 호출해 가져온다.'))
add(lead('우리가 수행한 내용', 'KG를 CSV(개체·속성·관계)로 만든 뒤 스크립트로 Cypher 적재문을 생성하여 Neo4j에 적재하였다. 측정값은 시계열 저장소, 문서 원문은 청크 저장소에 두었다.'))
add(table([
    ['구분', '결과'],
    ['개체 %d개' % NE, ', '.join('%s %d' % (k, EC[k]) for k in ('Dam', 'HydrometeorologicalState', 'Approval', 'Operation', 'Criterion', 'EvidenceSource'))],
    ['관계 %d개' % NR, ', '.join('%s %d' % kv for kv in RC.most_common())],
    ['외부 저장소', '측정자료 %s행, 문서 청크 %d개 (KG 밖)' % (format(MEAS, ','), CHUNKS)],
], [2300, 7672]))

# ---- 3장 검색과 LLM 답변
add(h1('3. 검색과 LLM 답변'))
add(para('KG 구축 결과를 이용해 질문에서 답변까지의 흐름을 구현하였다. LLM은 질문 해석(의도 분류)과 답변 생성에만 사용하고, 질의와 계산은 프로그램이 수행한다.'))
add(h2('3.1 전체 흐름'))
add(table([
    ['단계', '수행 내용', '담당'],
    ['1 의도·값 추출', '정해진 의도 목록 중 하나와 댐·시점을 JSON으로 출력', 'LLM'],
    ['2 값 검증', '의도가 목록에 있는지, 댐이 4개 중 하나인지, 시점 형식이 맞는지 확인하고 어긋나면 질의하지 않고 거절(여러 댐, 사유 질문 포함)', '프로그램'],
    ['3 KG 질의', '의도별 Cypher 템플릿에 값을 채워 Neo4j에서 운영행위·승인·기준·근거를 조회', '프로그램'],
    ['4 외부 저장소 조회', 'KG의 stationCode와 chunkId로 측정자료 저장소에서 시간별 값, 문서 저장소에서 조문 원문을 조회', '프로그램'],
    ['5 비교 값 계산', '제한수위 대비 차이, 승인량 대비 비율, 현재와 사례의 차이, 유사 사례(유클리드 거리)', '프로그램'],
    ['6 근거 묶음 → 답변', '태그와 표로 구성한 근거 묶음을 LLM에 주고, 규칙에 따라 근거 번호를 인용하여 답변', 'LLM'],
], [2200, 6272, 1500]))
add(h2('3.2 의도별 근거 구성'))
add(table([
    ['의도', '가져오는 근거', '출처'],
    ['CQ1 현재 상태', '저장된 가장 최근 시각의 6개 변수', 'KG(조회 키) → 측정자료'],
    ['CQ2 과거 상태', '지정한 시점·기간의 6개 변수', 'KG → 측정자료'],
    ['CQ3 과거 운영행위', '기간 내 운영행위(종류, 시각)와 허가한 승인', 'KG'],
    ['CQ4 과거 방류 승인', '기간 내 승인(승인일, 내용)', 'KG'],
    ['CQ5 현재 운영기준', '제한수위와 근거(별표3 원문 발췌, 연혁)', 'KG → 문서'],
    ['CQ6 공식 근거', '대상 항목의 출처와 위치', 'KG → 승인 원자료·측정·문서'],
    ['CURRENT', '현재 상태 + 제한수위 + 두 값의 차이', 'KG, 측정자료'],
    ['INTEGRATED', '운영행위 + 승인 + 당시 상태 + 제한수위 + 근거 + 비교 값', 'KG, 측정자료, 문서'],
    ['SIMILAR', '현재 상태와 가까운 과거 사례 상위 3개와 각 사례의 승인·상태·기준·근거', '측정자료, KG, 문서'],
    ['OUT_OF_SCOPE', '위 어디에도 해당하지 않거나 허용 범위 밖(여러 댐 비교, 사유 질문)', '거절'],
], [2200, 5372, 2400]))
add(h2('3.3 설계 근거'))
add(table([
    ['설계', '근거 문헌', '이유'],
    ['의도를 분류한 뒤 의도별로 질의를 만든다', 'Zhang(2025) 3.3: 질문 의도를 파싱하고 의도별 Cypher 변환 규칙 사용', '질문 유형이 CQ로 정해져 있어 근거 구성을 빠뜨리지 않기 위해'],
    ['LLM의 출력을 정해진 의도 목록으로 제한한다', 'Zhang(2025): LLM 출력을 정해진 라벨로 제어', 'LLM 출력의 불안정성을 줄이기 위해'],
    ['LLM이 Cypher를 쓰지 않고 템플릿을 사용한다', '연구자 판단 (GraphAide는 LLM이 Cypher를 생성)', '질의 오류를 줄이고 결과를 점검하기 쉽게 하기 위해'],
    ['Neo4j와 Cypher로 질의한다', 'DDKG, Zhang, GraphAide', '다단계 관계 탐색과 질의 언어 기반 검색'],
    ['KG에서 외부 저장소를 찾아가 측정값과 원문을 가져온다', 'GraphAide: 시계열 DB 등 외부 자료 호출, OntoDSMS: 데이터를 복제하지 않고 접근', '대량 측정값을 KG에 복제하지 않기 위해'],
    ['문서는 조문 단위 청크로 두고 청크 번호로 조회한다', '연구자 판단 (문헌은 임베딩 벡터에 저장)', '개체에서 출발하는 질문과 정확한 조문 인용을 위해. 벡터 검색과의 비교는 이후 실험으로'],
    ['비교 값을 프로그램이 계산한다', '연구자 판단', 'LLM의 계산 오류를 막기 위해'],
    ['유사 사례는 수위·유입량의 유클리드 거리로 찾는다', '연구자 판단 (문헌의 유사도는 텍스트 임베딩의 코사인 유사도이며 수치 상태 기준은 없음)', '값의 크기를 반영하는 거리를 사용. 코사인 유사도는 이 데이터에서 변별력이 없어 제외'],
], [3100, 3600, 3272]))
add(h2('3.4 근거 묶음과 답변 규칙'))
add(li('근거 묶음은 태그로 섹션을 구분하고 수치는 표로 쓰며, 항목마다 근거 번호(승인, 운영행위, 근거자료)를 붙인다.'))
add(li('답변은 묶음 안의 자료만 사용하고, 사실마다 근거 번호를 인용한다. 자료가 없으면 “자료에 없음”이라고 답한다.'))
add(li('원인·사유를 단정하지 않는다. “현재 상태”는 저장된 가장 최근 시각 값임을 기준 시각과 함께 밝힌다.'))
add(li('비교에 필요한 차이와 비율은 묶음의 계산값만 인용하고 LLM이 직접 계산하지 않는다.'))

# ---- 4장 예비 테스트
add(h1('4. 예비 테스트'))
add(h2('4.1 테스트 구성'))
add(table([
    ['항목', '내용'],
    ['모델', 'Qwen3-8B-AWQ (vLLM). 서버 GPU 메모리 제약으로 소형 모델을 사용하였다.'],
    ['저장소', 'Neo4j 5.26(KG 개체 %d개, 관계 %d개), 측정자료 저장소, 문서 청크 %d개' % (NE, NR, CHUNKS)],
    ['질문', '10개: CQ에 맞는 핵심 질문 5개(m01, m02, m06, m08, m09)와 비교·계산·범위 밖을 포함한 확장 질문 5개(m03, m04, m05, m07, m10)'],
    ['판정 기준', '의도·댐 분류, 답변의 수치가 근거 묶음과 일치, 근거 번호 인용, 근거 없는 주장 여부'],
], [2000, 7972]))
add(h2('4.2 결과'))
add(table([
    ['질문', '구분', '의도', '판정', '비고'],
    ['m01 소양강 현재 수위와 제한수위', '핵심', 'CURRENT 일치', '맞음', '185.26 EL.m, 제한수위 190.3 대비 −5.04 m, 기준 시각과 실시간이 아님을 명시'],
    ['m02 충주 현재와 제한수위', '핵심', 'CURRENT 일치', '맞음', '131.67 EL.m, 제한수위 대비 −6.33 m'],
    ['m08 광동 현재와 제한수위', '핵심', 'CURRENT 일치', '맞음', '제한수위 자료 없음(별표3 미수록)을 정확히 답함'],
    ['m06 횡성 2020-08 방류 정리', '핵심', 'INTEGRATED 일치', '대체로 맞음', '사례 3개의 수위, 제한수위 대비, 방류량이 묶음과 일치. 방류 시각을 “승인된”으로 표현, 일부 근거 번호가 묶음에 없음(수정)'],
    ['m09 충주 방류 전 승인과 공식 근거', '핵심', 'INTEGRATED 일치', '오류', '방류의 근거(승인 기록)와 제한수위의 근거(별표3)를 혼동하고 근거 번호를 일부만 인용(수정)'],
    ['m04 소양강 유사 사례와 승인량 대비 방류량', '확장', 'SIMILAR 일치', '대체로 맞음', '유사 사례(2017-08-25)의 방류량이 승인 1500㎥/s의 67.4%로 묶음과 일치. 값 하나를 직접 계산'],
    ['m07 광동 유사 사례', '확장', 'SIMILAR 일치', '대체로 맞음', '제한수위 없음을 정확히 답함. 요청하지 않은 사례 수 추가, 승인과 방류 시작을 혼동'],
    ['m03 충주 유사 사례와 제한수위 비교', '확장', 'SIMILAR 일치', '오류', '현재 값을 사례 값으로 섞고 증가율을 직접 계산하여 틀림'],
    ['m05 충주 승인량과 실제 방류량의 차이', '확장', 'INTEGRATED 일치', '오류', '비율을 “차이”로 서술하고, 창 이후에 승인된 상한을 사용'],
    ['m10 소양강·충주 중 제한수위에 더 가까운 댐', '확장', 'CURRENT 불일치', '실패', '두 댐 비교(기대: 범위 밖)를 한 댐으로 처리'],
], [2700, 700, 1500, 1100, 3972]))
add(box('요약', '의도 분류는 10개 중 9개가 일치하였다. 핵심 질문 5개 중 맞음 3개, 대체로 맞음 1개, 오류 1개이고, 확장 질문 5개 중 대체로 맞음 2개, 오류 2개, 실패 1개이다.'))
add(h2('4.3 오류 원인과 수정'))
add(table([
    ['원인', '질문', '수정', '상태'],
    ['LLM이 같은 키를 두 번 쓴 JSON에서 파서가 마지막 값만 취함', 'm10', '중복 키를 감지하여 범위 밖으로 거절', '수정 (재실행 필요)'],
    ['운영행위의 근거에 허가한 승인 중 첫 승인의 근거만 포함', 'm09, m06, m07', '모든 승인의 근거를 승인일 순으로 포함하고 방류의 근거와 제한수위의 근거를 구분', '수정'],
    ['창 이후에 승인된 상한에도 비율을 계산', 'm05, m09', '승인일이 창보다 늦은 승인은 비율에서 제외하고 사유를 표시', '수정'],
    ['현재와 사례의 차이를 LLM이 직접 계산', 'm03, m04', '수위 차, 제한수위 대비, 유입량 배수를 프로그램이 계산해 제공', '수정'],
    ['요청하지 않은 사례 수, 긴 소수 표기', 'm03, m04, m07', '프롬프트 보강, 측정값 반올림', '수정'],
    ['개념 혼동, 경고 무시(모델)', 'm05, m09', '프롬프트에 규칙 추가, 더 큰 모델에서 재확인', '재실행 필요'],
], [3600, 1500, 3500, 1372]))
add(box('해석', '질문에서 답변 생성까지 전 과정이 동작하고, 근거 묶음의 수치와 근거 번호를 인용한 답변이 생성됨을 확인하였다. 오류의 상당수는 근거 묶음의 구성에서 비롯되어 수정하였다. 본 결과는 소형 모델로 한 번 실행한 예비 결과이며 정확도나 효과를 입증하는 것은 아니다.'))

# ---- 5장 한계와 다음 계획
add(h1('5. 한계와 다음 계획'))
add(h2('5.1 한계'))
add(table([
    ['한계', '내용'],
    ['적재형 측정자료', '측정자료는 미리 받아 둔 자료이므로 “현재”는 저장된 가장 최근 시각(2026-09-28 23시)이다. 질의 시점에 실시간으로 조회하는 방식으로의 개선을 검토한다.'],
    ['연구자 지정 임시 기준', '운영행위 시각 규칙(변화 기준 1 CMS 또는 10%, 구간 −3~+6시간)과 유사 사례 거리(수위·유입량 정규화 유클리드)는 규정·문헌에 근거가 없다.'],
    ['실제 수행 확인', '운영행위는 승인 비고에서 분류한 것이다. 실제 운영기록을 확보하지 못하여, 방향이 있는 행위 18개 중 %d개가 측정 변화 방향과 일치하는 정도만 확인하였다.' % CHKC['일치']],
    ['추출 정확도', '비고 분류 정확도를 사람이 만든 정답으로 측정하지 않았다.'],
    ['LLM 평가', '소형 모델(8B), 질문 10개, 1회 실행이다. 의도 분류 정확도와 답변의 안정성은 확인되지 않았고, 표 데이터를 그대로 주는 방식과의 비교 기준선이 없다.'],
    ['자료 범위', '기상 변수는 댐 강우량만 사용하였고, 광동댐은 별표3에 없어 제한수위 기준이 없다.'],
], [2300, 7672]))
add(h2('5.2 다음 계획'))
add(li('수정 반영 후 같은 질문으로 재실행하여 수정 전후를 비교하고, GPU가 확보되면 32B 모델로 확인'))
add(li('같은 LLM에 표 데이터를 그대로 주는 방식(기준선)과 KG 방식 비교'))
add(li('사람 검토: 비고 분류 정확도 측정, 임시 기준(행위 시각, 유사 사례)의 타당성 확인'))
add(li('실제 운영기록 확보 방안 정리(한수원 현장 방문 등), 질의 시점 실시간 조회 방식 검토'))
add(h2('5.3 주요 근거 문헌'))
for r in tmpl_paras('Noy,') + tmpl_paras('Li, S.') + tmpl_paras('Zhou, Y.') + tmpl_paras('Huang, J.') + tmpl_paras('Zhang, D.') + tmpl_paras('Purohit'):
    add(li(r))

doc = ROOT_OPEN + ''.join(B) + SECT + '</w:body></w:document>'
import xml.dom.minidom
xml.dom.minidom.parseString(doc.encode('utf8'))  # 형식 검사
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as zo:
    for item in tz.infolist():
        data = tz.read(item.filename)
        if item.filename == 'word/document.xml':
            data = doc.encode('utf8')
        zo.writestr(item, data)
print('저장', OUT, '| 요소', len(B), '| 개체', NE, '관계', NR, '승인', len(APPS), '운영행위', len(OPS), '측정행', MEAS)
