#!/usr/bin/env python3
"""11월 월간 공정보고(hwpx) 초안: 10월 보고서 hwpx를 기준으로 쪽 설정·서식을 그대로 쓰고,
표지의 월, Ⅲ 주요 추진현황, Ⅳ 세부 수행 실적, Ⅴ 부록, Ⅵ 참고문헌을 11월 내용으로 바꾼다.
공정표의 11월 항목(2.3, 3.2, 4.1, 4.2) 가운데 2.3만 쓰고, 3.2·4.1·4.2는 인공지능 학부 작성분을 취합할 자리만 둔다.
2.3의 현장방문 및 회의(11. 26.) 내용은 소제목 아래를 빈 줄로 두어 방문 뒤에 채운다.
사용: python3 scripts/build_report_nov.py <10월 기준.hwpx> <출력.hwpx>   (이 환경에는 한글 프로그램이 없어 열어 보며 확인하지 못했다)
문단·표를 만드는 함수는 build_report_oct.py의 것을 그대로 가져다 쓴다."""
import csv, collections, os, re, struct, sys, zipfile, xml.dom.minidom
from xml.sax.saxutils import escape
HERE = os.path.dirname(os.path.abspath(__file__))
BASE, OUT = sys.argv[1], sys.argv[2]
FIGS = os.path.join(HERE, '..', '..', 'lab_meeting', 'report_figs')
W = 42520
_oct = open(os.path.join(HERE, 'build_report_oct.py'), encoding='utf-8').read()
exec(_oct[_oct.index('_id = [1900100000]'):_oct.index('# ---------------------------------------------------------------- 표지·제목')])
_id[0] = 1911100000

z = zipfile.ZipFile(BASE)
sec = z.read('Contents/section0.xml').decode('utf8')


def top_paragraphs(x):
    ps, depth, start = [], 0, None
    for m in re.finditer(r'<hp:p |</hp:p>', x):
        if m.group(0) == '<hp:p ':
            if depth == 0:
                start = m.start()
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                ps.append((start, m.end()))
    return ps


spans = top_paragraphs(sec)
head = sec[:spans[0][0]]
ps = [sec[a:b] for a, b in spans]
tail = sec[spans[-1][1]:]


def text_of(p):
    return re.sub(r'<[^>]+>', '', ''.join(re.findall(r'<hp:t>(.*?)</hp:t>', p, re.S)))


def idx(startswith):
    hit = [i for i, p in enumerate(ps) if text_of(p).startswith(startswith)]
    assert len(hit) == 1, (startswith, hit)
    return hit[0]


I_TITLE, I_DATE = idx('월간 공정보고 (10월)'), idx('2026. 10.')
I_III = idx('’26년 10월 실적')
I_IV, I_V, I_VI = idx('Ⅳ. 세부 수행 실적'), idx('Ⅴ. 부록'), idx('Ⅵ. 참고문헌')
assert len(ps) == 213 and I_IV == I_III + 1, (len(ps), I_III, I_IV)

# ---------------------------------------------------------------- 표지
ps[I_TITLE] = ps[I_TITLE].replace('(10월)', '(11월)')
ps[I_DATE] = ps[I_DATE].replace('2026. 10.', '2026. 11.')

# ---------------------------------------------------------------- 태스크 후보(사실)
TASKS = list(csv.DictReader(open(os.path.join(HERE, '..', '..', 'lab_meeting', 'task_candidates', '태스크후보_v1.csv'), encoding='utf-8-sig')))
AREAS = list(dict.fromkeys(r['업무 영역'] for r in TASKS))
NA = collections.Counter(r['업무 영역'] for r in TASKS)
AV = collections.Counter(r['현재 가능(내부)'] for r in TASKS)
assert len(TASKS) == 82 and len(AREAS) == 11 and dict(AV) == {'가능': 10, '부분 가능': 33, '공개자료 추가 필요': 10, '내부 자료 필요': 29}, (len(TASKS), AV)
BY = {r['번호']: r for r in TASKS}
EX = ['A04', 'B04', 'C02', 'D03', 'E02', 'F05', 'G01', 'H01', 'I04', 'J03', 'K03']       # 영역별 예시 하나

# ---------------------------------------------------------------- Ⅲ 주요 추진현황
VISIT = '(현장방문(11. 26.) 후 작성)'
AI = '(인공지능 학부 작성 내용 취합 예정)'
EMPTY = [('e', '')]
ACT2 = [('h', 'RAG-LLM 통합 파이프라인(안) 제시'),
        ('b', '수집, 전처리, 지식기반 구성, 질의 해석, 근거 조회, 근거 정리, 응답으로 이어지는 RAG-LLM 통합 파이프라인(안) 작성'),
        ('b', '통합 파이프라인(안)과 표준 프롬프트 프레임의 연계 구조 및 근거 사용 원칙 정리'),
        ('b', '한수원 한강수력본부 현장방문 및 회의(11. 26.)')]
PLAN2 = [('h', '최종 보고서 작성'),
         ('b', '현장방문 조사 결과를 반영하여 RAG-LLM 통합 파이프라인(안) 보완'),
         ('b', '최종 보고서 초안 작성')]


def cell_paras(items):
    out = []
    for kind, t in items:
        if kind == 'h':
            out.append('<hp:p id="0" paraPrIDRef="52" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="24"><hp:t>&lt;%s&gt;</hp:t></hp:run></hp:p>' % escape(t))
        elif kind == 'b':
            out.append('<hp:p id="0" paraPrIDRef="53" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="26"><hp:t>%s</hp:t></hp:run></hp:p>' % escape(t))
        else:
            out.append('<hp:p id="0" paraPrIDRef="53" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="26"/></hp:p>')
    return ''.join(out)


def set_cell(part, items):
    key = 'textHeight="0" hasTextRef="0" hasNumRef="0">'
    a = part.index(key) + len(key)
    b = part.index('</hp:subList>')
    return part[:a] + cell_paras(items) + part[b:]


t = ps[I_III].replace('’26년 10월 실적', '’26년 11월 실적').replace('’26년 11월 계획', '’26년 12월 계획')
parts = t.split('<hp:tc ')
tcs = parts[1:]
pos = {}
for i, c in enumerate(tcs):
    m = re.search(r'<hp:cellAddr colAddr="(\d+)" rowAddr="(\d+)"/>', c)
    pos[(int(m.group(2)), int(m.group(1)))] = i
for (r, c), items in {(3, 0): EMPTY, (3, 1): EMPTY, (5, 0): ACT2, (5, 1): PLAN2}.items():
    assert '적용기술 요소' in tcs[pos[(r, c)]] or 'RAG-LLM 통합' in tcs[pos[(r, c)]], (r, c)
    tcs[pos[(r, c)]] = set_cell(tcs[pos[(r, c)]], items)
ps[I_III] = parts[0] + ''.join('<hp:tc ' + c for c in tcs)
assert '’26년 11월 실적' in ps[I_III] and '’26년 12월 계획' in ps[I_III]

def fig_total():
    """통합 파이프라인(안) 도식(한글 표로 그림). 윗줄은 지식기반 구축, 아랫줄은 질의응답."""
    Wd = [9000, 2100, 9000, 2100, 9700, 2100, 8318]
    Hh = [3000, 1500, 3000]
    c = {(0, 0): ('① 수집\n구조화 자료, 문서 자료', 'gray'), (0, 1): ('▶', 'arrow'), (0, 2): ('② 전처리\n자료 유형별 정리', 'gray'), (0, 3): ('▶', 'arrow'),
         (0, 4): ('③ 지식기반 구성\nKG, 외부 저장소', 'gray'), (0, 6): ('사용자 질의', 'dash'),
         (1, 4): ('▼ 근거', 'arrow'), (1, 6): ('▼', 'arrow'),
         (2, 0): ('⑦ 응답\nsLLM', 'gray'), (2, 1): ('◀', 'arrow'), (2, 2): ('⑥ 근거 정리\n표준 프롬프트 프레임', 'gray'), (2, 3): ('◀', 'arrow'),
         (2, 4): ('⑤ 근거 조회\n의도별 질의 규칙', 'gray'), (2, 5): ('◀', 'arrow'), (2, 6): ('④ 질의 해석\n의도·대상·기간', 'gray')}
    return figtab(Wd, Hh, c)


def fig_frame2():
    Wd = [10000, 10000, 10000, 12318]
    Hh = [2000, 1300, 1800, 2400, 1300, 2000, 1300, 2000]
    c = {(0, 0): ('사용자 질의', 'white', 4), (1, 0): ('▼', 'arrow', 4),
         (2, 0): ('근거 묶음 (구역별, 항목마다 출처 번호)', 'dash', 4),
         (3, 0): ('현재 상태', 'white'), (3, 1): ('과거 이력', 'white'), (3, 2): ('운영 기준', 'white'), (3, 3): ('출처·위치', 'white'),
         (4, 0): ('▼', 'arrow', 4),
         (5, 0): ('근거 사용 원칙', 'gray', 4),
         (6, 0): ('▼', 'arrow', 4),
         (7, 0): ('sLLM 응답', 'white', 2), (7, 2): ('근거·판단 구분 답변', 'white', 2)}
    return figtab(Wd, Hh, c)


# ---------------------------------------------------------------- Ⅳ 세부 수행 실적 (공정표의 11월 항목: 2.3, 3.2, 4.1, 4.2)
IV = [
    H1('2. LLM 활용 데이터 파이프라인 조사'), H2('2.3 RAG-LLM 통합 파이프라인(안) 제시'),
    SQ('RAG-LLM 통합 파이프라인(안) 구성'),
    CI('수집, 전처리, 지식기반 구성 단계의 파이프라인(안)에 질의응답 단계를 연결하여 수집부터 응답까지 7단계로 이어지는 통합 파이프라인(안) 작성 (그림 1, 표 1)'),
    DS('지식기반 구축(①~③): 자료를 수집하고 정리하여 KG와 외부 저장소를 구성'),
    DS('질의응답(④~⑦): 사용자 질의를 해석하여 지식기반에서 근거를 조회하고, 정리한 근거로 응답'),
    DS('질의 해석과 응답은 sLLM이 수행하고, 근거 조회와 근거 정리는 정해진 규칙에 따른 처리로 구분'),
    fig_total(),
    cap('그림 1 RAG-LLM 통합 파이프라인(안)'),
    SQ('① 수집 단계'),
    CI('자료별 수집 경로에 따라 구조화 자료와 문서 자료를 수집'),
    DS('수집 대상: 수문·기상 자료(수치 시계열), 방류 승인 기록, 운영 규정'),
    DS('자료별 제공기관, 제공 방식, 단위·주기를 기준으로 수집 경로를 구분'),
    DS('수치 시계열은 식별 키(대상 코드, 시점)를 기준으로 수집하고, 문서 자료는 문서 단위로 수집'),
    SQ('② 전처리 단계'),
    CI('자료 유형에 따라 처리 경로를 구분하고 공통 정리 항목을 적용 (그림 2)'),
    DS('구조화 자료: 열은 속성에, 행은 개체에 대응시키고 값은 원본 그대로 유지하며 식별 키로 연결 [2]'),
    DS('수치 시계열: KG에 넣지 않고 외부 저장소에 보관하며 KG와 식별 키로 연계 [2][4]'),
    DS('문서 자료: 문서 단위로 분리하고, 구조가 일정한 경우 규칙 기반으로 값을 추출 [3]'),
    DS('공통 정리: 표기 형식을 통일하고 자료의 출처와 시점 정보를 유지하며, 원본은 변경하지 않고 정리 내용을 기록'),
    fig_proc(),
    cap('그림 2 자료 유형별 전처리 경로'),
    SQ('③ 지식기반 구성 단계'),
    CI('온톨로지를 기준으로 개체를 만들고 관계를 연결한 뒤 검증하여 저장'),
    DS('개체 생성: 전처리된 자료를 온톨로지의 Class와 속성에 맞춰 개체로 생성하고 개체마다 근거 출처를 연결'),
    DS('관계 연결: 자료에 적힌 값(식별 키)이 일치하는 개체 쌍에만 관계를 생성 [6]'),
    DS('검증: 온톨로지가 허용한 관계의 양 끝 Class, 필수 속성, 값 형식, 근거 연결 여부를 점검 [3]'),
    DS('저장: 개체·관계는 KG에, 수치 시계열과 규정 원문은 외부 저장소(측정자료 저장소, 문서 저장소)에 저장 [3][8]'),
    SQ('④ 질의 해석 단계'),
    CI('사용자 질의에서 근거 조회에 필요한 항목(의도, 대상, 기간)을 추출 [5]'),
    DS('의도: 미리 정해 둔 질문 범주 가운데 질의가 해당하는 범주를 선택하며, 하나의 질의가 여러 범주에 해당할 수 있음'),
    DS('대상: 질의에 나온 댐 이름을 KG의 댐 개체 식별 키에 대응'),
    DS('기간: 질의의 시점·기간 표현을 조회 구간으로 변환'),
    DS('추출 결과가 정해 둔 범주와 KG에 있는 대상 안에 있는지 확인한 뒤 근거 조회 단계로 전달'),
    SQ('⑤ 근거 조회 단계'),
    CI('의도별로 정해 둔 질의 규칙에 따라 KG와 외부 저장소에서 근거를 조회'),
    DS('KG 조회: 의도마다 조회할 개체와 관계의 경로를 질의 규칙으로 정해 두고, 대상과 기간을 넣어 조회 [5]'),
    DS('외부 저장소 조회: KG에서 조회한 개체의 식별 키로 측정자료 저장소의 해당 구간 수치와 문서 저장소의 규정 원문을 조회 [2][4]'),
    DS('조회 결과에는 개체마다 연결된 근거 출처를 함께 포함'),
    DS('의미 검색의 결합 여부는 대상 문서 자료가 확정된 뒤 검토 [4]'),
    SQ('⑥ 근거 정리 단계'),
    CI('조회한 근거를 표준 프롬프트 프레임의 근거 묶음으로 정리 (그림 3)'),
    DS('의도별 구역(현재 상태, 과거 이력, 운영 기준, 출처·위치)으로 근거를 모음'),
    DS('근거 항목마다 출처 번호를 부여하여 응답에서 어느 근거를 사용하였는지 표기할 수 있도록 함'),
    DS('표준 프롬프트 프레임: 사용자 질의, 근거 묶음, 근거 사용 원칙으로 구성하여 응답 단계에 전달'),
    fig_frame2(),
    cap('그림 3 표준 프롬프트 프레임을 통한 근거 전달'),
    SQ('⑦ 응답 단계'),
    CI('표준 프롬프트 프레임을 입력으로 sLLM이 근거 사용 원칙에 따라 응답 [7] (표 2)'),
    DS('주어진 근거만 사실로 사용하고 사실마다 출처 번호 표기'),
    DS('비교·해석은 판단으로 구분하고 어느 근거에서 나온 판단인지 표기'),
    DS('근거에 없는 내용은 자료에 없음으로 응답'),
    DS('질의가 묻는 항목이 근거에 없는 경우 이름이 다른 값으로 대체하지 않음'),
    DS('응답에 사용할 sLLM과 성능 향상 방안은 3, 4에서 제시'),
    SQ('한수원 현장방문 및 회의 (11. 26., 한강수력본부)'),
    BL(), BL(), BL(),

    H1('3. sLLM 후보군 평가 방향'), H2('3.2 모델 구조 및 특성 검토'),
    CI(AI),
    H1('4. 도메인 특화 성능 향상 전략'), H2('4.1 RAG 기반 적용방안 조사'),
    CI(AI),
    H2('4.2 경량 미세조정 방식 검토'),
    CI(AI),
]

# ---------------------------------------------------------------- Ⅴ 부록
T1 = [['단계', '입력', '처리', '산출'],
      ['수집', '수집 대상별 수집 경로', '구조화 자료와 문서 자료를 수집', '원본 자료'],
      ['전처리', '원본 자료', '자료 유형별로 표기 형식을 통일하고 값은 원본 유지', '정리된 자료'],
      ['지식기반 구성', '정리된 자료, 온톨로지', '온톨로지를 기준으로 KG를 구성하고, 수치 시계열과 규정 원문은 외부 저장소에 두어 식별 키로 연계', 'KG, 외부 저장소'],
      ['질의 해석', '사용자 질의', '질의에서 의도(질문 범주), 대상 댐, 기간을 추출하고 허용 범위 확인', '의도·대상·기간'],
      ['근거 조회', '의도·대상·기간', '의도별 질의 규칙으로 KG를 조회하고, KG의 식별 키로 측정자료 저장소와 문서 저장소 조회', '개체·관계, 측정값, 규정 원문'],
      ['근거 정리', '조회 결과', '의도별 구역으로 근거를 모으고 항목마다 출처 번호 부여', '근거 묶음'],
      ['응답', '표준 프롬프트 프레임(근거 사용 원칙, 근거 묶음, 사용자 질의)', 'sLLM이 근거 묶음 안에서 근거와 판단을 구분하여 응답', '출처 번호가 포함된 응답']]
T2 = [['항목', '내용'],
      ['근거의 사용', '근거 묶음에 있는 내용만 사실로 사용하고, 사실마다 출처 번호를 표기'],
      ['판단의 구분', '비교·해석은 판단임을 밝히고, 어느 근거에서 나온 판단인지 표기'],
      ['근거가 없는 경우', '근거에 없는 내용은 자료에 없음으로 응답'],
      ['항목 불일치', '질의가 묻는 항목이 근거에 그 이름으로 없으면 이름이 다른 값으로 대체하지 않음']]
T4 = [['업무 영역', '태스크 후보 수', '태스크 예', '사용자 요청 예']] + [[a, '%d' % NA[a], BY[e]['태스크'], BY[e]['사용자 요청 예']] for a, e in zip(AREAS, EX)]
for a, e in zip(AREAS, EX):
    assert BY[e]['업무 영역'] == a, (a, e)
APPX = [H1('2. LLM 활용 데이터 파이프라인 조사'), H2('2.3 RAG-LLM 통합 파이프라인(안) 제시'),
        table('표 1 RAG-LLM 통합 파이프라인(안)의 단계별 입력·처리·산출', T1, [13, 22, 43, 22]),
        table('표 2 표준 프롬프트 프레임의 근거 사용 원칙', T2, [20, 80])]

# ---------------------------------------------------------------- Ⅵ 참고문헌
def ref(n, t):
    return '<hp:p id="0" paraPrIDRef="69" styleIDRef="23" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="65"><hp:t>%d. %s</hp:t></hp:run></hp:p>' % (n, escape(t))


REFS_OLD = ps[I_VI + 1:I_VI + 9]
assert text_of(REFS_OLD[0]).startswith('1. Noy') and text_of(REFS_OLD[7]).startswith('8. Angles')
REFS_NEW = [ref(9, 'Mihindukulasooriya 외(2023), "Text2KGBench: A Benchmark for Ontology-Driven Knowledge Graph Generation from Text", The Semantic Web - ISWC 2023, Lecture Notes in Computer Science, Vol. 14266'),
            ref(10, 'Hogan 외(2021), "Knowledge Graphs", ACM Computing Surveys, Vol. 54, No. 4, Article 71')]

# ---------------------------------------------------------------- 조립
new = ps[:I_IV + 1] + IV + [ps[I_V]] + APPX + [ps[I_VI]] + REFS_OLD + ps[I_VI + 9:]
body = head + ''.join(new) + tail
xml.dom.minidom.parseString(body.encode('utf8'))
with zipfile.ZipFile(OUT, 'w') as zo:
    zo.writestr(zipfile.ZipInfo('mimetype'), z.read('mimetype'), compress_type=zipfile.ZIP_STORED)
    for it in z.infolist():
        n = it.filename
        if n == 'mimetype' or n == 'Preview/PrvImage.png':
            continue
        zo.writestr(n, body.encode('utf8') if n == 'Contents/section0.xml' else z.read(n), compress_type=zipfile.ZIP_DEFLATED)
print('저장', OUT, '문단', len(new))
