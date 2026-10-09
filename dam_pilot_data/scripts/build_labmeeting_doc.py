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
add(title('댐 운영 판단 지원을 위한', 'Ontology–KG–Hybrid Retrieval–LLM 연구 진행'))
add(subtitle('Ontology 설계 → KG 구축 → 검색·LLM 답변'))
add(dateline('2026.10.09 랩미팅'))
add(label('주차별 연구 진행 정리'))
add(table([
    ['구분', '주요 내용'],
    ['전주\nOntology 설계', '• Noy & McGuinness(2001)의 개발 절차를 참고하여 Ontology 설계 수행\n• 전체 질문 1개와 세부 질문 6개(CQ1~CQ6) 설정, 주요 용어 166개 정리\n• Class 6개, Relation 8개, Data Property 설계, 대량 측정자료는 KG 밖에서 조회하는 구조 설정'],
    ['이번주\nKG 구축 및\n검색·LLM 답변',
     '• 4개 댐(충주·소양강·횡성·광동)의 방류 승인 %d건, K-water 시간별 수문기상 자료(약 %.1f만 행), 연계운영규정 별표3 등을 수집·정리\n'
     '• 근거 문헌의 방법을 참고하여 KG 구축: 개체 %d개, 관계 %d개, Ontology 적합성 검사 통과\n'
     '• CQ 답변 가능성 점검 중 Approval–Dam 연결 부재를 발견하여 Relation 1개 추가(8개 → 9개)\n'
     '• 질문 → 의도 분류(LLM) → Neo4j·측정자료·문서 조회 → 근거 묶음 → 답변 생성 흐름을 구현하고 Qwen3-8B로 CQ1~CQ6과 수치 비교를 모두 포함하는 통합 질문을 구성하여 답변 확인' % (len(APPS), MEAS / 10000, NE, NR)],
    ['다음주\n개선 및 확장', '• 답변 개선(현재와 사례의 차이를 프로그램이 계산, 사례 수 지정 규칙) 반영 후 재실행, CQ별 단일 질문 추가, 더 큰 모델(32B)과 비교\n• 같은 LLM에 표 데이터를 그대로 주는 방식과 KG 방식 비교\n• 사람 검토: 비고 분류 정확도, 연구자 지정 임시 기준(행위 시각, 유사 사례)\n• 실제 운영기록 확보 방안 정리(한수원 현장 방문 등)'],
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
    ['문서 저장소', '규정 원문(별표 단위 청크)', '연계운영규정 별표3(현행과 시행일별 연혁)'],
], [2300, 4000, 3672]))
add(box('KG의 역할', tmpl_table('KG의 역할')[0][1]))

# ---- 2장 KG 구축
add(h1('2. KG 구축'))
add(h2('2.1 구축 대상 자료'))
add(table([
    ['자료', '출처', '범위', '사용'],
    ['방류 승인 기록', '한강홍수통제소 댐방류승인(공공데이터포털)', '충주·소양강·횡성·광동 4개 댐 %d건 (%s ~ %s)' % (len(APPS), a_first, a_last), 'Approval, Operation'],
    ['수문기상 시간자료', 'K-water MyWater', '4개 댐 × 6개 변수(수위, 저수량, 강우량, 유입량, 총방류량, 저수율), 시간별 %s행 (충주·횡성 2010-08~, 소양강 2011-06~, 광동 2016-06~ 2026-09)' % format(MEAS, ','), '측정자료 저장소, 상태 Entity'],
    ['홍수기 제한수위', '연계운영규정 별표3(법제처)', '충주 138.0, 소양강 190.3, 횡성 178.2 EL.m (광동댐은 별표3에 수록되지 않음). 시행일이 다른 연혁 9개 판', 'Criterion'],
    ['규정 원문', '법제처 국가법령정보(XML)', '연계운영규정 별표3 현행과 시행일별 연혁 9개 판의 원문 → 문서 저장소 %d개 청크' % USED_CH, '문서 저장소, 근거 위치'],
], [1700, 2500, 4272, 1500]))
add(h2('2.2 구축 절차 개요'))
add(para('구축은 7단계로 수행하였다. 각 단계는 근거 문헌의 방법을 참고하였고, 문헌에 방법이 없는 부분은 연구자 판단이라고 표시하였다. 단계별 내용은 2.3~2.9에 정리하였다.'))
add(flow(['1 소스 구분\nDDKG', '2 전처리\nDDKG · Zhang', '3 구조화 자료 매핑\nOntoDSMS', '4 비정형 텍스트 추출\nDDKG', '5 개체 해소·연결\nGraphAide', '6 정규화·검증\nGraphAide · DDKG · Noy', '7 저장\nDDKG · GraphAide']))

add(h2('2.3 단계 1. 소스 구분'))
add(lead('필요한 이유', '표로 정리된 자료는 열의 값을 Ontology의 속성에 옮기면 되지만, 문장이나 글자로 그린 표는 내용을 읽어서 값을 뽑아야 한다. 처리 방법이 다르므로 먼저 구분한다.'))
add(lead('문헌의 방법', 'DDKG(Huang 2026, 3.2.1)는 댐 안전 점검 보고서와 댐 관리 플랫폼의 자료로 KG를 만든 연구이다. 플랫폼에서 내려받은 표(댐 높이, 저수용량 등)는 값을 그대로 옮기고, 보고서의 글(결함 설명, 안전 평가 결과)은 따로 읽어서 필요한 내용을 뽑는다. 즉 표로 된 자료와 글로 된 자료를 나누어 서로 다른 방법으로 처리한다.'))
add(lead('우리가 수행한 내용', '수집한 자료를 같은 기준으로 나누었다. 법제처 XML 안의 별표는 겉으로는 표이지만 선 문자(┌─┬─┐│)로 그린 표가 글자로 들어 있어서 비정형으로 구분하였다.'))
add(table([
    ['구분', '자료', '예', '이후 처리'],
    ['구조화 자료', '승인 CSV', '열이 정해진 표(관측소코드, 승인년월일시분, 방류시작시간, 접수방류량, 비고 …)', '단계 3: 열을 속성으로 매핑'],
    ['구조화 자료', 'K-water 시간별 측정자료', '열이 정해진 표(DAM_CD, SDATE_raw, 수위, 저수량, 강우량, 유입량, 총방류량, 저수율)', '단계 3: 변수를 상태 Entity로 매핑, 측정값은 외부 저장소'],
    ['비정형 텍스트', '승인 CSV의 비고 열', '“이내 탄력적 조정”, “(초기수문방류 100㎥/s)”처럼 짧은 문장', '단계 4: 규칙으로 운영행위 종류 추출'],
    ['비정형 텍스트', '연계운영규정 별표3', '│한 강 │다목적댐 │소양강댐 │190.3 │-│ 처럼 선 문자로 그린 표', '단계 4: 줄과 셀을 읽어 제한수위 추출, 원문은 문서 저장소에 청크로 저장'],
], [1500, 2000, 3972, 2500]))

add(h2('2.4 단계 2. 전처리'))
add(lead('필요한 이유', '매핑과 추출 전에 같은 자료가 두 번 세어지거나 시각이 어긋나는 문제를 없앤다. 원본은 바꾸지 않고, 수정한 내용은 로그로 남긴다.'))
add(lead('문헌의 방법', 'DDKG(3.2.1)의 점검 보고서는 PDF·DOC·이미지 등 형식이 제각각이고 필요 없는 내용이 많아서, 먼저 글자를 읽을 수 있는 형식(마크다운)으로 바꾸고(필요하면 OCR로 글자를 인식), 정규식으로 필요한 부분(현장 점검, 안전 분석 등 4개 구간)만 잘라 하나의 텍스트 모음으로 합친다. Zhang(2025)은 수집한 문서를 OCR한 뒤 문서·문장·단어 단위로 걸러 정제한다.'))
add(lead('우리가 수행한 내용', '표 자료는 아래와 같이 정리하였다.'))
add(table([
    ['대상', '처리', '결과'],
    ['승인 CSV', '모든 열의 값이 같고 순차번호만 다른 중복 행은 첫 행만 남기고 제거, 제거한 행은 로그에 기록', '3,929행 중 7행 제거 → 3,922행. 4개 댐에서는 광동댐 1건(순차번호 2220, 2218과 동일) 제거. 충주조정지는 범위에서 제외하여 승인 %d건' % len(APPS)],
    ['측정 시간자료', '시각 라벨의 24시 표기를 다음날 0시로 변환, 결측은 채우지 않고 비워 둠', '4개 댐 × 6개 변수, %s행' % format(MEAS, ',')],
], [1800, 4572, 3600]))

add(h2('2.5 단계 3. 구조화 자료 매핑'))
add(lead('필요한 이유', '구조화된 표의 값을 해석을 더하지 않고 Ontology의 Entity와 Data Property로 옮기기 위해, 어느 표·열이 어느 Class·속성이 되는지 규칙을 먼저 정한다.'))
add(lead('문헌의 방법', 'OntoDSMS(Zhou 2023)는 댐 모니터링 시스템에서 관계형 DB(표)의 자료를 온톨로지에 연결한다. 대응 원칙은 단순하다. DB의 표 하나는 Class 하나(예: 댐 표 → Dam), 표의 열은 그 Class의 속성(예: 댐이름 열 → damName), 표의 행은 개체(예: ‘충주댐’ 행 → 충주댐 개체)에 대응시킨다. 이 대응을 설정 파일(D2RQ 매핑 파일)에 적어 두고, DB의 값은 복사하지 않고 필요할 때 읽는다.'))
add(lead('우리가 수행한 내용', '같은 원칙으로 규칙표를 만들어 승인 CSV와 측정자료의 열을 Entity와 Data Property로 옮겼다(D2RQ 도구는 쓰지 않음). 이 단계에서는 Entity와 속성만 만들고, Entity 사이의 관계는 단계 5에서 만든다. Class마다 원천 자료와 만들어지는 결과의 예는 다음과 같다.'))
add(table([
    ['Class', '원천 자료 (열 이름: 값)', 'ID 규칙', '만들어지는 개체와 속성 (예)'],
    ['Dam', 'MyWater 댐 정보 — 댐코드: 1003110, 댐이름: 충주댐, 댐 유형: 다목적댐', 'DAM:댐코드', 'DAM:1003110\ndamName = 충주댐\ndamType = 다목적댐'],
    ['HydrometeorologicalState', '측정자료의 열 “수위”(댐코드 1003110). 수위·저수량·강우량·유입량·총방류량·저수율 6개 열마다 1개 (댐 4 × 변수 6 = %d개)' % EC['HydrometeorologicalState'], 'HMS:댐코드:변수', 'HMS:1003110:수위\nvariableType = 수위\nstationCode = 1003110'],
    ['Approval', '승인 CSV 한 행 — 순차번호: 1368, 승인년월일시분: 2012-08-24, 방류시작시간: 2012-08-24 15:00, 접수방류량: 2000, 비고: 이내 탄력적 조정', 'APR:순차번호', 'APR:1368\napprovalTime = 2012-08-24\napprovalContent = “방류시작 2012-08-24 15:00; 접수방류량 2000㎥/s; 비고: 이내 탄력적 조정”'],
    ['EvidenceSource (승인)', '위와 같은 승인 CSV 한 행', 'EVI:AP:순차번호', 'EVI:AP:1368\nsourceTitle = 환경부 한강홍수통제소 홍수예보 댐방류승인\nsourceType = 승인자료\nsourceLocator = 순차번호 1368'],
    ['EvidenceSource (측정)', '측정자료의 댐별 소스 — 댐코드: 1003110', 'EVI:KW:댐코드', 'EVI:KW:1003110\nsourceTitle = K-water MyWater 수문 시간자료\nsourceType = 측정자료\nsourceLocator = DAM_CD=1003110 충주댐 시간별 자료'],
], [1700, 3300, 1500, 3472]))
add(box('원칙', '값은 원자료 그대로 옮기고 해석을 더하지 않는다. 측정값 전체는 KG에 복사하지 않고, 찾아가는 키(stationCode)만 둔다. Operation과 Criterion은 텍스트에서 읽어야 하므로 단계 4에서 만든다.'))
add(lead('구조화 자료로 정하는 속성 값: 운영행위 시각', 'Operation 개체는 단계 4에서 비고를 읽어 만들지만, 시각(operationTime)은 글이 아니라 구조화 자료에서 정한다. 승인의 시각과 실제 운영행위 시각은 다르므로, 승인 CSV의 방류시작시간 앞 3시간~뒤 6시간에서 측정자료의 총방류량이 직전보다 1 CMS 또는 10%% 이상 변한 시각 중 시작에 가장 가까운 것을 행위 시각으로 한다. 변화가 없으면 승인의 방류시작시간을 쓰고, 비고에 시각이 있으면 그 시각을 쓴다. 결과: 측정 변화 %d, 승인 시작 %d, 비고 명시 %d.' % (TSRC['측정'], TSRC['승인'], TSRC['비고'])))
add(box('판단 표시', '이 행위 시각 기준(앞 3시간~뒤 6시간, 1 CMS 또는 10%)은 연구자가 정한 임시 기준이다. 실제 운영행위의 시각을 정하는 기준이나 운영기록이 있으면 전문가의 검토를 받아 방법을 수정할 계획이다.'))

add(h2('2.6 단계 4. 비정형 텍스트 추출'))
add(lead('필요한 이유', '운영행위의 종류와 제한수위 값은 표의 열로 있지 않고 글 속에 있어서, 글을 읽어 값을 뽑아야 한다.'))
add(lead('문헌의 방법', 'DDKG(3.2.2~3.2.3)는 글의 형태에 따라 추출 방법을 나눈다. “홍수 조절 안전성 평가 등급은 C등급이다”처럼 정해진 문형은 정규식으로 ‘C’를 바로 뽑는다. 같은 결함도 표현이 제각각인 설명문은 정규식으로 처리하기 어려워 LLM을 미세조정하여 분류한다. GraphAide(Purohit 2024)는 Ontology의 Class·관계 목록을 LLM에 주고 그 틀 안에서만 지식을 만들게 한다.'))
add(lead('우리가 수행한 내용', '승인 비고와 별표3 모두 정해진 형태가 있어 규칙(정규식)으로 읽었다. LLM 추출은 사용하지 않았다. 같은 입력에서 항상 같은 결과가 나오고, 규칙을 그대로 보여 줄 수 있기 때문이다.'))
add(lead('A. 승인 비고 → Operation 종류', '비고에서 아래 문구를 찾아 운영행위의 종류(operationType)를 정한다. 한 비고에서 여러 문구가 잡히면 각각 Operation 한 개로 만든다.'))
add(table([
    ['비고 원문 (예)', '걸리는 문구 (규칙)', '만들어지는 Operation 종류'],
    ['(초기수문방류 100㎥/s)', '“초기방류”, “초기수문방류”', '초기방류'],
    ['10cms 증 / 이내 증가방류', '“증가방류”, “숫자 cms 증”', '증가방류'],
    ['이내 점증방류', '“점진”, “점증”', '점진·점증방류'],
    ['9.11 16:00 수문방류종료', '“방류종료”', '방류종료'],
    ['이내 탄력적 조정', '“탄력”', '탄력적 방류 (원문 용어를 보존)'],
    ['수문방류 승인', '“수문방류”, “이내 방류” 등 일반 방류 문구', '방류 (일반)'],
    ['(비고 없음)', '-', '방류 (일반, 종류 미상). 승인 자체가 해당 시각의 방류 승인이므로 포함'],
    ['이내 변경승인(기존 500 ㎥/s), 방류 시간 정정', '“변경”, “연장”, “정정”', 'Operation을 만들지 않음 (같은 방류의 변경 → 단계 5에서 원 승인에 연결)'],
], [3400, 3300, 3272]))
add(para('결과: 승인 %d건에서 Operation %d개가 만들어졌다(%s).' % (len(APPS), len(OPS), ', '.join('%s %d' % kv for kv in OPC.most_common()))))
add(lead('B. 별표3 → Criterion', '별표 내용은 선 문자로 그린 표가 글자로 들어 있다. “│”로 시작하는 줄을 “│” 기준으로 잘라 셀로 읽고(구분, 댐 종류, 댐 이름, 홍수기 제한수위, 시설별 최저 운영수위), 댐 이름의 공백을 제거한다.'))
add(table([
    ['별표3 원문 (줄)', '읽은 결과', '만들어지는 Criterion'],
    ['│한 강 │다목적댐 │소양강댐 │190.3 │-│', '댐 이름 소양강댐, 제한수위 190.3', 'criterionType 홍수기 제한수위, criterionValue 190.3, unit EL.m'],
    ['│수 계 │ │충 주 댐 │138.0 │-│', '댐 이름 “충 주 댐” → 충주댐, 제한수위 138.0', 'criterionValue 138.0'],
    ['│ │ │횡 성 댐 │178.2 │-│', '댐 이름 “횡 성 댐” → 횡성댐, 제한수위 178.2', 'criterionValue 178.2'],
    ['(광동댐 줄 없음)', '별표3에 수록되지 않음', 'Criterion 없음'],
], [3300, 3300, 3372]))
add(para('시행일이 다른 연혁 9개 판도 같은 방법으로 읽어, 제한수위가 바뀐 이력을 근거자료로 남겼다.'))
add(lead('C. 별표3 원문 → 문서 청크', '제한수위의 근거로 답변에 인용하려면 값뿐 아니라 별표3 원문(표와 각주)이 필요하다. 별표3 원문을 고치지 않고 청크로 저장하고, 현행 판 1개(LAW:별표3)와 시행일별 연혁 9개 판(LAWHIST:별표3@시행일)에 청크 번호를 붙였다. 근거자료 Entity의 chunkId가 이 번호를 가리켜, 질문에 답할 때 원문을 찾아온다. 문서 청크는 모두 %d개이다.' % USED_CH))
add(box('판단 표시', '문서를 임베딩 벡터가 아닌 청크 번호로 저장하고 찾아가는 방식은 문헌(벡터 저장)과 달라 연구자 판단이다. 개체에서 출발하는 질문과 원문 그대로의 인용을 위한 선택이다.'))

add(h2('2.7 단계 5. 개체 해소·연결'))
add(lead('필요한 이유', '같은 댐이 자료마다 “충주”, “충주댐”, “충 주 댐”처럼 다르게 적혀 있다. 같은 Dam으로 이어 주어야 승인·측정·기준 사이의 경로가 끊기지 않고, 이 연결이 Ontology의 Relation이 된다.'))
add(lead('문헌의 방법', 'GraphAide(Purohit 2024)는 뉴스 기사에서 뽑은 이름이 같은 대상을 가리키는지 판단한다. Wikidata의 고유번호(QID)를 기준으로 삼아 후보를 찾고, LLM이 가장 맞는 번호를 골라 연결한다.'))
add(lead('우리가 수행한 내용', '우리 자료는 시설 코드나 정확한 이름이 있는 표여서 LLM 판단이 필요 없다. 코드나 이름이 일치할 때만 연결하고 추측으로 연결하지 않았다. Relation별 연결 방법은 다음과 같다.'))
add(table([
    ['Relation', '연결 방법', '개수', '출처 표시'],
    ['Approval –concernsDam→ Dam', '승인 CSV의 관측소코드 = Dam의 댐코드', '%d' % RC['concernsDam'], '실제 코드 일치'],
    ['Approval –authorizes→ Operation', '승인에서 Operation을 만들었으면 그 승인이 해당 Operation을 승인', '%d' % 68, '구성'],
    ['Approval –authorizes→ Operation (변경 승인)', '새 Operation이 없는 변경 승인 17건은 같은 댐·같은 방류 시작 시각의 원 승인의 Operation에 연결. 11건이 연결되고 6건은 원 승인을 찾지 못함', '12 (11건)', '추정으로 표시'],
    ['Operation –performedOnDam→ Dam', 'Operation을 만든 승인의 Dam', '%d' % RC['performedOnDam'], '승인에서 유도'],
    ['Dam –hasHydrometeorologicalState→ HMS', '댐코드가 같은 댐과 상태 Entity', '%d' % RC['hasHydrometeorologicalState'], '실제 코드 일치'],
    ['Criterion –appliesToDam→ Dam', '별표3 댐 이름의 공백을 제거하여 Dam 이름과 일치', '%d' % RC['appliesToDam'], '이름 일치'],
    ['모든 Class –supportedBy→ EvidenceSource', '승인 → 승인 레코드, 상태 → 측정자료 댐별 소스, Operation → 그것을 만든 승인 레코드, Criterion → 별표3와 연혁', '%d' % RC['supportedBy'], '자료 출처에서 유도'],
], [2900, 4072, 1200, 1800]))

add(h2('2.8 단계 6. 정규화와 Ontology 검증'))
add(lead('필요한 이유', '만든 KG가 정의한 Ontology를 지키는지, CQ에 답하는 데 필요한 경로가 실제로 이어지는지를 확인한다.'))
add(lead('문헌의 방법', 'GraphAide(Purohit 2024)는 LLM이 만든 KG 조각이 정해진 형식(어떤 속성이 있어야 하는지, 값의 형식)에 맞는지를 Pydantic이라는 검증 도구로 검사한다. DDKG(OHCF)는 LLM이 분류한 결과가 Ontology의 규칙과 모순되면(함께 나올 수 없는 라벨 조합) 걸러낸다. Noy & McGuinness(2001)는 속성마다 값의 종류(문자, 숫자, 다른 개체)와 개수 제한을 정하도록 한다.'))
add(lead('우리가 수행한 내용', '문헌의 검사를 Ontology 정의에 맞게 바꾸어 검사 프로그램을 만들고, KG 전체를 대상으로 실행하였다. 각 검사는 위반 목록을 세어 0건이면 통과로 한다.'))
add(table([
    ['검사', '방법', '대상', '위반'],
    ['관계의 양 끝 Class', '관계 유형마다 Ontology가 허용한 (시작 Class, 끝 Class) 쌍 목록과 비교 (예: authorizes는 Approval → Operation만 허용)', '관계 %d개' % NR, '0건 (통과)'],
    ['필수 Data Property', 'Class별 필수 속성(1.5절)이 개체마다 있는지 확인 (예: Operation은 operationType과 operationTime)', '개체 %d개' % NE, '0건 (통과)'],
    ['값 형식', 'approvalTime은 YYYY-MM-DD, operationTime은 YYYY-MM-DDThh:mm 패턴, criterionValue는 숫자로 읽히는지 확인', 'Approval %d, Operation %d, Criterion %d' % (EC['Approval'], EC['Operation'], EC['Criterion']), '0건 (통과)'],
    ['근거 연결', 'HMS·Operation·Approval·Criterion 개체마다 supportedBy 관계가 1개 이상 있는지 확인', '개체 %d개' % (EC['HydrometeorologicalState'] + EC['Operation'] + EC['Approval'] + EC['Criterion']), '0건 (통과)'],
    ['경로 일치', '승인이 가리키는 댐(concernsDam)과 그 승인이 승인한 Operation이 수행된 댐(performedOnDam)이 같은지 비교', 'authorizes 관계 %d개' % RC['authorizes'], '0건 (통과)'],
], [1700, 4372, 2200, 1700]))
add(para('이어서 CQ마다 Ontology의 경로를 KG에서 실제로 따라가 보고, 답에 필요한 Entity가 얼마나 나오는지 세어 CQ 답변 가능성을 점검하였다.'))
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
    ['Data Property', 'EvidenceSource에 chunkId 추가 (문서 저장소의 원문 청크를 찾아가는 키로, HydrometeorologicalState의 stationCode와 같은 역할)'],
], [2300, 7672]))

add(h2('2.9 단계 7. 저장과 구축 결과'))
add(lead('필요한 이유', '승인 → 운영행위 → 댐 → 상태처럼 여러 단계의 관계를 따라가는 질문에 답하려면 관계 탐색과 질의 언어를 지원하는 저장소가 필요하다.'))
add(lead('문헌의 방법', 'DDKG(3.3)는 추출한 지식을 JSON 파일로 모은 뒤, 파이썬 스크립트가 JSON을 읽어 Neo4j용 질의문(Cypher)을 만들고 이를 실행해 노드와 관계를 한꺼번에 적재한다(노드 201,362개, 관계 953,447개). Neo4j는 여러 단계 관계를 따라가는 검색에 강하다고 설명한다. GraphAide도 Neo4j를 쓰고, 시계열 자료는 시계열 DB를 외부 함수로 호출해 가져온다.'))
add(lead('우리가 수행한 내용', 'Neo4j는 개체를 노드(점), 관계를 노드 사이의 선으로 저장하는 그래프 데이터베이스이고, Cypher는 Neo4j에 노드와 관계를 만들거나 조회하라고 지시하는 명령 언어(관계형 DB의 SQL에 해당)이다. DDKG와 같은 순서로 수행하였다.'))
add(li('1) 단계 3~5의 결과를 세 개의 표(개체 표, 속성 표, 관계 표)로 정리하였다.'))
add(table([
    ['개체 표: 개체 ID', 'Class', '이름'],
    ['DAM:1003110', 'Dam', '충주댐'],
    ['APR:1368', 'Approval', '승인 1368 (충주댐)'],
    ['OPR:1368:1', 'Operation', '충주댐 탄력적 방류 (2012-08-24 16:00)'],
], [3000, 2500, 4472]))
add(table([
    ['속성 표: 개체 ID', '속성 이름', '값'],
    ['DAM:1003110', 'damName', '충주댐'],
    ['OPR:1368:1', 'operationType', '탄력적 방류'],
    ['OPR:1368:1', 'operationTime', '2012-08-24T16:00'],
], [3000, 2500, 4472]))
add(table([
    ['관계 표: 시작 개체', '관계 이름', '끝 개체'],
    ['APR:1368', 'authorizes', 'OPR:1368:1'],
    ['APR:1368', 'concernsDam', 'DAM:1003110'],
], [3000, 2500, 4472]))
add(li('2) 표의 행마다 Neo4j에 넣을 Cypher 명령문을 프로그램이 자동으로 만든다. 개체 한 행은 “이 ID의 노드를 만들고 속성 값을 붙여라”, 관계 한 행은 “두 노드를 찾아 이 관계 이름의 선으로 이어라”는 명령문이 된다.'))
add(li('3) 명령문 %d개(노드 %d + 관계 %d)를 Neo4j에서 실행하여 적재하였다. 같은 ID의 노드가 중복으로 만들어지지 않도록 ID가 유일해야 한다는 제약을 두었다.' % (NE + NR, NE, NR)))
add(li('4) 측정값 전체와 문서 원문은 Neo4j에 넣지 않고 측정자료 저장소와 문서 저장소에 두었다.'))
add(table([
    ['표의 행 (예)', '만들어지는 Cypher 명령문 (일부 생략)', '뜻'],
    ['개체 표 DAM:1003110, Dam, 충주댐\n속성 표 damName = 충주댐, damType = 다목적댐', "MERGE (n:Entity:Dam {id: 'DAM:1003110'}) SET n.label = '충주댐', n.damName = '충주댐', n.damType = '다목적댐';", "ID가 DAM:1003110인 Dam 노드를 만들고(MERGE) 이름과 유형 값을 붙인다(SET)"],
    ['관계 표 APR:1368, authorizes, OPR:1368:1', "MATCH (a:Entity {id: 'APR:1368'}), (b:Entity {id: 'OPR:1368:1'}) MERGE (a)-[r:authorizes]->(b);", "두 노드를 찾아서(MATCH) authorizes라는 이름의 선으로 잇는다(MERGE)"],
], [3000, 4372, 2600]))
add(table([
    ['구분', '결과'],
    ['개체 %d개' % NE, ', '.join('%s %d' % (k, EC[k]) for k in ('Dam', 'HydrometeorologicalState', 'Approval', 'Operation', 'Criterion', 'EvidenceSource'))],
    ['관계 %d개' % NR, ', '.join('%s %d' % kv for kv in RC.most_common())],
    ['외부 저장소', '측정자료 %s행, 문서 청크 %d개(별표3 원문) — KG 밖' % (format(MEAS, ','), USED_CH)],
], [2300, 7672]))

# ---- 3장 검색과 LLM 답변
import json
RUN1 = os.path.join(ROOT, '05_retrieval', 'results_run1')
QS = {q['id']: q['question'] for q in json.load(open(os.path.join(ROOT, '05_retrieval', 'questions_multi.json'), encoding='utf-8'))}
TR = lambda i: json.load(open(os.path.join(RUN1, '%s_trace.json' % i), encoding='utf-8'))
t6 = TR('m06')
t4 = TR('m04')
add(h1('3. 검색과 LLM 답변'))
add(para('구축한 KG로 CQ에 실제로 답할 수 있는지 확인하기 위해, 질문을 받아 근거를 찾고 답변을 만드는 흐름을 구현하였다. LLM은 질문을 해석하고 답변을 쓰는 데만 사용하고, 근거 조회와 값 계산은 프로그램이 한다. LLM이 근거를 만들거나 계산하지 않게 하여, 답변의 모든 내용을 KG와 외부 저장소의 근거로 확인할 수 있게 하기 위해서이다.'))
add(h2('3.1 전체 흐름과 예시 질문'))
add(flow(['1 질문 해석\n(LLM)', '2 값 검증\n(프로그램)', '3 KG 조회\n(프로그램)', '4 외부 저장소 조회\n(프로그램)', '5 비교 값 계산\n(프로그램)', '6 근거 묶음 → 답변\n(LLM)']))
add(para('CQ1~CQ6과 수치 비교를 모두 포함하는 통합 질문을 구성하여 답변을 받아 보았다. 이 질문은 현재 상태와 제한수위를 확인하고, 비슷했던 과거 사례의 상태·운영행위·승인·근거와 승인량 대비 방류량까지 함께 보는 질문으로 Ontology의 전체 질문에 해당한다. 3.3~3.8은 이 질문이 각 단계에서 어떻게 처리되는지 따라가며 설명한다.'))
add(box('예시 질문', QS['m04']))
add(h2('3.2 의도와 근거 구성'))
add(para('질문이 어느 의도에 해당하는지에 따라 가져올 근거가 정해진다. 의도는 CQ1~CQ6과 SIMILAR이다. CQ1~CQ6의 근거 구성은 Ontology 설계에서 CQ마다 정한 Relation 경로(1.4절)를 그대로 따른다.'))
add(table([
    ['의도', '따라가는 경로 (Ontology)', '가져오는 근거'],
    ['CQ1 현재 상태', 'Dam → hasHydrometeorologicalState → 상태 Entity → stationCode로 측정자료 조회', '저장된 가장 최근 시각의 6개 변수'],
    ['CQ2 과거 상태', 'CQ1과 같은 경로', '지정한 시점·기간의 6개 변수'],
    ['CQ3 과거 운영행위', 'Dam ← performedOnDam ← Operation (← authorizes ← Approval)', '기간 내 운영행위(종류, 시각)와 그것을 허가한 승인'],
    ['CQ4 과거 방류 승인', 'Dam ← concernsDam ← Approval', '기간 내 승인(승인일, 내용)'],
    ['CQ5 현재 운영기준', 'Criterion → appliesToDam → Dam, chunkId로 문서 조회', '제한수위와 근거(별표3 원문 발췌, 연혁)'],
    ['CQ6 공식 근거', '대상 항목 → supportedBy → EvidenceSource', '출처와 위치(승인 원자료, 측정자료, 별표3)'],
    ['SIMILAR', '현재 상태와 과거 운영행위 시점의 상태를 비교하여 가까운 사례를 고르고, 그 사례에 CQ2·CQ3·CQ4·CQ6의 경로를 적용', '현재 상태, 제한수위, 가까운 과거 사례의 상태·운영행위·승인·근거, 계산한 비교 값'],
], [2000, 4272, 3700]))
add(para('SIMILAR는 CQ에 없는 의도이다. Ontology의 전체 질문은 현재 상태를 과거 사례와 비교하는 것인데, 어떤 CQ도 값을 비교하여 사례를 고르는 질문을 다루지 않아 값 비교가 필요하다고 판단하여 추가하였다. 사례를 고르는 거리 기준은 연구자가 정한 임시 기준이다(3.7절). 범위 밖 질문(여러 댐 비교, 사유 질문)은 의도가 아니라 단계 2의 검증에서 거절한다.'))
add(label('예시 질문이 필요로 하는 근거'))
add(table([
    ['질문의 부분', '해당 의도', '따라가는 경로', '가져오는 근거'],
    ['소양강댐 지금 상태', 'CQ1', 'Dam → 상태 → 측정자료', '저장된 가장 최근 시각의 6개 변수'],
    ['제한수위와 비교', 'CQ5', 'Criterion → Dam, 별표3 원문', '제한수위 190.3 EL.m와 현재와의 차이'],
    ['비슷했던 과거 사례', 'SIMILAR', '운영행위 시점들의 수위·유입량 비교', '거리가 가장 가까운 사례'],
    ['그 사례의 상태', 'CQ2', 'CQ1과 같은 경로, 사례 시점', '사례 구간의 6개 변수'],
    ['그 사례의 운영행위와 승인', 'CQ3, CQ4', 'Dam ← Operation ← Approval', '운영행위 종류·시각, 승인 내용'],
    ['근거', 'CQ6', 'supportedBy → EvidenceSource', '승인 레코드, 별표3'],
    ['승인된 방류량 대비 실제 방류량', 'SIMILAR (비교 값)', '프로그램 계산', '최대 총방류량 / 접수방류량'],
], [2600, 1500, 3000, 2872]))

add(h2('3.3 단계 1. 질문 해석'))
add(lead('필요한 이유', '사용자는 자유로운 문장으로 묻지만, KG를 조회하려면 그 질문이 어느 CQ에 해당하는지(의도)와 댐·기간 같은 값이 필요하다.'))
add(lead('문헌의 방법', 'Zhang(2025, 3.3)은 질문을 받으면 먼저 질문의 의도를 파악하고(규칙, 지도학습 모델, LLM의 투표를 조합), 의도마다 정해 둔 Cypher 변환 규칙으로 KG를 조회한다. LLM이 자유롭게 쓰지 않고 정해진 라벨 중에서 고르게 하여 출력을 안정시킨다. GraphAide(Purohit 2024)도 LLM의 응답을 Ontology가 정한 틀 안으로 제한한다.'))
add(lead('우리가 수행한 내용', 'LLM(Qwen3-8B)에게 질문과 3.2절의 의도 목록(CQ1~CQ6, SIMILAR)과 분류 규칙을 주고, 의도 하나와 댐·사례 수 같은 값을 JSON 형식으로만 출력하게 하였다. 질문 표현이 다양하고 CQ별 학습 데이터가 없어, 규칙이나 지도학습 모델 대신 LLM이 분류하도록 하였다. 예시 질문은 현재 상태와 비슷한 과거 사례를 묻고 있어 SIMILAR로 분류되었다.'))
add(box('예시 질문의 LLM 출력', t4['intent_raw']))
add(table([
    ['항목', '값', '뜻'],
    ['intent', 'SIMILAR', '질문의 의도. 현재 상태를 제한수위와 비교하고, 비슷했던 과거 사례를 찾아 비교하는 질문이므로 SIMILAR로 분류'],
    ['slots.dam', '소양강댐', '질문에서 뽑은 댐 이름. 이후 조회의 대상 댐이 된다'],
    ['slots.k', '1', '가져올 유사 사례의 수. 질문에 사례 수가 없었으나 LLM이 1로 지정하였다'],
], [1800, 1600, 6572]))

add(h2('3.4 단계 2. 값 검증'))
add(lead('필요한 이유', 'LLM의 출력은 정해진 범위를 벗어날 수 있으므로, 조회하기 전에 코드로 확인한다.'))
add(lead('문헌의 방법', 'GraphAide는 LLM이 생성한 결과가 정해진 형식에 맞는지 Pydantic이라는 검증 도구로 확인한다(2.8절).'))
add(lead('우리가 수행한 내용', '프로그램이 다음을 확인하고, 하나라도 어긋나면 조회하지 않고 “범위 밖”으로 답한다: 의도가 목록에 있는지, 댐이 KG에 있는 4개 중 하나인지, 날짜 형식이 맞는지, JSON에 같은 키가 두 번 나오지 않는지, 여러 댐을 비교하는 질문이 아닌지. 예시 질문은 의도가 목록에 있고, 소양강댐은 4개 댐에 포함되며, 사례 수가 정수여서 통과한다.'))

add(h2('3.5 단계 3. KG 조회'))
add(lead('필요한 이유', '의도에 해당하는 운영행위, 승인, 기준, 근거는 KG에 관계로 연결되어 있으므로, 관계를 따라가 찾아야 한다.'))
add(lead('문헌의 방법', 'DDKG, Zhang(2025), GraphAide는 모두 Neo4j에 KG를 저장하고 Cypher(Neo4j의 질의 언어)로 조회한다. Zhang은 의도마다 정해 둔 Cypher 규칙을 쓰고, GraphAide는 LLM이 질문에서 Cypher를 자동으로 만들어 실행한다.'))
add(lead('우리가 수행한 내용', '의도마다 Cypher 질의 틀을 미리 만들어 두고, 단계 2를 통과한 댐과 값만 채워 실행한다. LLM이 질의를 직접 만들면 잘못된 질의가 나올 수 있고 어떤 질의가 실행되었는지 확인하기 어려워, GraphAide와 달리 정해진 틀을 사용하였다. 예시 질문(SIMILAR)은 아래 두 질의를 쓴다.'))
add(table([
    ['질의 (Cypher)', '뜻'],
    ['MATCH (o:Operation)-[:performedOnDam]->(d:Dam {damName: $dam}) RETURN o.id, o.operationTime', '댐 이름이 $dam인 Dam에서 수행된 모든 Operation의 ID와 운영행위 시각을 가져온다. 이 시점들이 비교할 과거 사례의 후보가 된다 (소양강댐은 측정값이 있는 4개 시점)'],
    ['MATCH (x:Entity {id: $id})-[:supportedBy]->(e:EvidenceSource) RETURN e.id, e.sourceTitle, e.sourceType, e.sourceLocator, e.chunkId', '선택된 사례의 운영행위, 승인, 제한수위처럼 $id로 지정한 개체의 근거자료를 가져온다'],
], [5600, 4372]))
add(para('선택된 과거 사례(유사도 순위 1)에 대해 KG에서 가져온 내용은 다음과 같다.'))
add(table([
    ['운영행위', '종류', '운영행위 시각', '허가한 승인 (승인일)'],
    ['OPR:2754:1', '초기방류', '2017-08-25 15:00', 'APR:2754 (08-24), APR:2804 (08-27)'],
    ['OPR:2754:2', '탄력적 방류', '2017-08-25 15:00', 'APR:2754 (08-24), APR:2804 (08-27)'],
], [2000, 1800, 2400, 3772]))
add(para('제한수위는 Criterion CRI:CR-01(소양강댐 홍수기 제한수위 190.3 EL.m)에서 가져온다.'))

add(h2('3.6 단계 4. 외부 저장소 조회'))
add(lead('필요한 이유', '측정값 전체와 문서 원문은 KG에 없고 외부 저장소에 있으므로, KG가 알려 주는 키로 찾아와야 한다.'))
add(lead('문헌의 방법', 'GraphAide는 시계열 자료를 시계열 DB에서 외부 함수로 호출해 가져와 답변의 문맥에 더한다. OntoDSMS는 DB의 값을 복사하지 않고 필요할 때 읽는다(2.5절).'))
add(lead('우리가 수행한 내용', 'KG의 상태 Entity에 있는 stationCode(소양강댐 1012110)로 측정자료 저장소에서 두 가지를 읽는다. 하나는 현재 상태(저장된 가장 최근 시각), 다른 하나는 사례의 운영행위 시각 앞 6시간~뒤 12시간의 시간별 6개 변수이다. 행위 전후의 변화를 볼 수 있도록 이 구간으로 정하였다. 제한수위의 근거는 chunkId(LAW:별표3)로 문서 저장소에서 별표3 원문을 읽어 온다.'))
add(table([
    ['구분', '시각', '수위 (EL.m)', '유입량 (CMS)', '총방류량 (CMS)'],
    ['현재', '2026-09-28 23:00', '185.2644', '95.079', '102.579'],
    ['사례 (OPR:2754)', '2017-08-25 14:00', '192.5', '769.051', '97.134'],
    ['사례 (OPR:2754)', '2017-08-25 15:00', '192.53', '1027.58', '523.33'],
    ['사례 (OPR:2754)', '2017-08-25 18:00', '192.56', '1011.2', '1011.2'],
], [2000, 2500, 1700, 1800, 1972]))

add(h2('3.7 단계 5. 비교 값 계산'))
add(lead('필요한 이유', '“제한수위보다 얼마나 낮은가”, “승인량 대비 얼마나 방류했는가”, “현재와 비슷한 과거 사례는 어느 것인가”처럼 값을 비교해야 하는 질문이 있다. LLM이 숫자를 직접 계산하면 틀릴 수 있어, 계산은 프로그램이 한다.'))
add(lead('문헌의 방법', '수치 비교에 해당하는 문헌의 방법은 없다. 유사 사례를 찾는 문헌들은 텍스트를 임베딩 벡터로 바꾸어 코사인 유사도로 비교하며, 수위·유입량 같은 수치 상태를 비교하는 기준은 없다.'))
add(lead('우리가 수행한 내용', '프로그램이 다음을 계산하여 근거 묶음에 포함한다. 유사 사례는 현재 수위·유입량과 후보 사례의 수위·유입량을 각각 그 댐 기록의 최솟값~최댓값으로 0~1로 맞춘 뒤 유클리드 거리가 가까운 순서로 고른다. 코사인 유사도는 두 값의 크기를 보지 않아 이 자료에서는 거의 모든 사례가 1에 가까워 구분되지 않았다. 제한수위 대비 차이와 승인량 대비 최대 방류량 비율도 계산하며, 구간보다 늦게 승인된 상한은 비율에서 제외한다.'))
add(table([
    ['계산 항목', '값'],
    ['현재 수위의 제한수위 대비', '185.2644 EL.m, 제한수위 190.3 EL.m 대비 -5.04 m'],
    ['사례의 유사도 (유클리드 거리)', '후보 4개 중 거리 0.223으로 1위 (2017-08-25 15:00, 당시 수위 192.53 EL.m, 유입량 1027.58 CMS)'],
    ['사례 구간 내 최고 수위', '192.56 EL.m (2017-08-25 16:00), 제한수위 대비 +2.26 m'],
    ['사례 구간 내 최대 총방류량', '1011.2 CMS (2017-08-25 18:00)'],
    ['승인량 대비 비율', 'APR:2754 접수방류량 1500㎥/s 대비 67.4%. APR:2804(승인일 08-27)는 구간(08-26까지)보다 늦게 승인되어 제외 표시'],
], [3300, 6672]))
add(box('판단 표시', '유사 사례의 거리 기준은 연구자가 정한 임시 기준이다. 사례를 고르는 기준이 있으면 전문가의 검토를 받아 수정할 계획이다.'))

add(h2('3.8 단계 6. 근거 묶음과 답변 생성'))
add(lead('필요한 이유', 'LLM이 KG에서 나온 근거 안에서만 답하게 하고, 어느 근거에서 나온 말인지 확인할 수 있게 해야 한다. 연구 목적상 근거에 없는 사유를 추정해서는 안 된다.'))
add(lead('문헌의 방법', 'GraphAide는 그래프에서 찾은 결과와 외부 자료를 합쳐 LLM에 문맥으로 주고, 그 문맥을 바탕으로 답변을 생성한다.'))
add(lead('우리가 수행한 내용', '단계 3~5에서 얻은 자료를 하나의 근거 묶음으로 정리하여 LLM에 준다. 묶음은 태그로 구역을 나누고, 수치는 표로 쓰며, 항목마다 근거 번호(승인 [APR:…], 근거자료 [EVI:…])를 붙인다. LLM에게는 다음 규칙을 주었다. 이 규칙은 근거 기반으로 지원하고 근거 없는 사유를 추정하지 않는다는 Ontology의 목적에서 정하였다.'))
add(li('묶음 안의 자료만 사용하고, 사실마다 근거 번호를 인용한다. 자료가 없으면 “자료에 없음”이라고 답한다.'))
add(li('원인·사유를 단정하지 않는다. “현재 상태”는 저장된 가장 최근 시각의 값임을 기준 시각과 함께 밝힌다.'))
add(li('차이와 비율은 묶음의 계산값만 인용하고 직접 계산하지 않는다.'))
add(table([
    ['근거 묶음의 일부 (예시 질문)'],
    ['<현재상태 기준시각="2026-09-28 23:00" 비고="저장된 가장 최근 시각이며 실시간이 아님">수위 185.2644 EL.m, 유입량 95.079 CMS …</현재상태>\n<계산값 대상="현재" 출처="프로그램 계산">현재 수위 185.2644 EL.m, 제한수위 190.3 EL.m 대비 -5.04 m</계산값>\n<유사사례 순위="1" 시각="2017-08-25 15:00" 거리="0.223" 당시 수위="192.53 EL.m" 유입량="1027.58 CMS" …>\n운영행위 [OPR:2754:1] 초기방류 / 허가한 승인 [APR:2754] 승인일 2017-08-24: 방류시작 2017-08-25 14:00; 접수방류량 1500㎥/s …\n당시상태(앞 6시간~뒤 12시간): | 시각 | 수위 | … |\n<계산값 대상="OPR:2754:2">… 승인 [APR:2754] 접수방류량 1500 ㎥/s 대비 창 내 최대 총방류량 67.4%</계산값>\n</유사사례>\n<운영기준 id="CRI:CR-01" 댐="소양강댐">홍수기 제한수위: 190.3 EL.m … [EVI:LAW:별표3]</운영기준>'],
], [9972], firstcol=False))

add(h2('3.9 예시 질문의 답변'))
add(table([
    ['질문', QS['m04']],
    ['답변 (전문)', t4['answer'].replace('**', '')],
], [1800, 8172], header=False))
add(box('확인', '답변의 현재 수위, 제한수위 대비 -5.04 m, 사례 시각·수위, 승인량 대비 67.4%와 최대 총방류량 1011.2 CMS가 근거 묶음과 일치하고 근거 번호를 인용하였다. 두 가지는 정확하지 않다. 현재와 사례의 수위 차 “+7.27 m”는 묶음의 계산값이 아니라 LLM이 직접 계산한 값이고, 사례 수를 묻지 않았는데 LLM이 1개로 지정하여 사례가 하나만 제시되었다.'))

# ---- 4장 한계와 다음 계획
add(h1('4. 한계와 다음 계획'))
add(h2('4.1 한계'))
add(table([
    ['한계', '내용'],
    ['적재형 측정자료', '측정자료는 미리 받아 둔 자료이므로 “현재”는 저장된 가장 최근 시각(2026-09-28 23시)이다. 질의 시점에 실시간으로 조회하는 방식으로의 개선을 검토한다.'],
    ['연구자 지정 임시 기준', '운영행위 시각 규칙(변화 기준 1 CMS 또는 10%, 구간 −3~+6시간)과 유사 사례 거리(수위·유입량 정규화 유클리드)는 규정·문헌에 근거가 없다.'],
    ['실제 수행 확인', '운영행위는 승인 비고에서 분류한 것이다. 실제 운영기록을 확보하지 못하여, 방향이 있는 행위 18개 중 %d개가 측정 변화 방향과 일치하는 정도만 확인하였다.' % CHKC['일치']],
    ['추출 정확도', '비고 분류 정확도를 사람이 만든 정답으로 측정하지 않았다.'],
    ['답변의 한계', '예시 답변에서 현재와 사례의 수위 차(+7.27 m)를 LLM이 직접 계산하였고, 사례 수를 LLM이 1개로 지정하여 사례가 하나만 제시되었다. 답변에 인용된 나머지 수치와 근거 번호는 근거 묶음과 일치하였다.'],
    ['LLM 평가', '소형 모델(8B)로 통합 질문 1개를 1회 실행하였다. 의도 분류 정확도와 답변의 안정성은 확인되지 않았고, 표 데이터를 그대로 주는 방식과의 비교 기준선이 없다.'],
    ['자료 범위', '기상 변수는 댐 강우량만 사용하였고, 광동댐은 별표3에 없어 제한수위 기준이 없다.'],
], [2300, 7672]))
add(h2('4.2 다음 계획'))
add(li('답변 개선: 현재와 사례의 차이(수위 차, 유입량 배수)를 프로그램이 계산하여 근거 묶음에 포함하고, 사례 수는 질문에 명시된 경우에만 지정하도록 하여 같은 질문으로 재실행한 뒤 수정 전후를 비교'))
add(li('GPU가 확보되면 32B 모델로 같은 질문을 실행하여 모델 크기에 따른 차이를 확인'))
add(li('같은 LLM에 표 데이터를 그대로 주는 방식(기준선)과 KG 방식 비교'))
add(li('사람 검토: 비고 분류 정확도 측정, 임시 기준(행위 시각, 유사 사례)의 타당성 확인'))
add(li('실제 운영기록 확보 방안 정리(한수원 현장 방문 등), 질의 시점 실시간 조회 방식 검토'))
add(h2('4.3 주요 근거 문헌'))
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
