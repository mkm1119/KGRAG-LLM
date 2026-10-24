#!/usr/bin/env python3
"""10월 월간 공정보고(hwpx) 초안: 9월 보고서 hwpx를 기준으로 쪽 설정·서식을 그대로 쓰고, 우리 담당 부분(1.3, 2.3)과 Ⅲ 추진현황만 10월 내용으로 바꾼다.
3(sLLM 후보군), 4(도메인 특화) 절은 인공지능 학부 작성분을 취합할 자리만 둔다.
사용: python3 scripts/build_report_oct.py <9월 기준.hwpx> <출력.hwpx>   (이 환경에는 한글 프로그램이 없어 열어 보며 확인하지 못했다)"""
import os, re, struct, sys, zipfile, xml.dom.minidom
from xml.sax.saxutils import escape
HERE = os.path.dirname(os.path.abspath(__file__))
BASE, OUT = sys.argv[1], sys.argv[2]
FIGS = os.path.join(HERE, '..', '..', 'lab_meeting', 'report_figs')
z = zipfile.ZipFile(BASE)
sec = z.read('Contents/section0.xml').decode('utf8')
W = 42520


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
assert len(ps) == 173 and '(9월)' in ps[3] and '2026. 9.' in ps[10]
_id = [1900100000]


def nid():
    _id[0] += 1
    return _id[0]


def P(text, para, char, style=0):
    return ('<hp:p id="0" paraPrIDRef="%d" styleIDRef="%d" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="%d"><hp:t>%s</hp:t></hp:run></hp:p>' % (para, style, char, escape(text)))


def H1(t): return P(t, 51, 41)
def H2(t): return P(t, 58, 63)
def SQ(t): return P('□ ' + t, 59, 42, 31)
def CI(t): return P('◦ ' + t, 61, 42, 29)
def DS(t): return P('- ' + t, 64, 64, 30)
def BL(): return P('', 61, 42, 29)


def cap(t): return P(t, 65, 66, 21)


def pic(fname, ratio=0.86):
    path = os.path.join(FIGS, fname)
    with open(path, 'rb') as f:
        d = f.read(24)
    pw, ph = struct.unpack('>II', d[16:24])
    iid = os.path.splitext(fname)[0]
    media.append((iid, fname))
    w = int(W * ratio); h = int(w * ph / pw)
    return ('<hp:p id="0" paraPrIDRef="20" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="38">'
            '<hp:pic id="%d" zOrder="1" numberingType="NONE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" href="" groupLevel="0" instid="%d" reverse="0">'
            '<hp:offset x="0" y="0"/><hp:orgSz width="%d" height="%d"/><hp:curSz width="%d" height="%d"/><hp:flip horizontal="0" vertical="0"/>'
            '<hp:rotationInfo angle="0" centerX="%d" centerY="%d" rotateimage="1"/><hp:renderingInfo><hc:transMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/><hc:scaMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/><hc:rotMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/></hp:renderingInfo>'
            '<hp:imgRect><hc:pt0 x="0" y="0"/><hc:pt1 x="%d" y="0"/><hc:pt2 x="%d" y="%d"/><hc:pt3 x="0" y="%d"/></hp:imgRect>'
            '<hp:imgClip left="0" right="%d" top="0" bottom="%d"/><hp:inMargin left="0" right="0" top="0" bottom="0"/><hp:imgDim dimwidth="%d" dimheight="%d"/>'
            '<hc:img binaryItemIDRef="%s" bright="0" contrast="0" effect="REAL_PIC" alpha="0"/><hp:effects/>'
            '<hp:sz width="%d" widthRelTo="ABSOLUTE" height="%d" heightRelTo="ABSOLUTE" protect="0"/>'
            '<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="PARA" vertAlign="TOP" horzAlign="CENTER" vertOffset="0" horzOffset="0"/>'
            '<hp:outMargin left="0" right="0" top="0" bottom="0"/><hp:shapeComment>그림입니다.\n원본 그림의 이름: %s</hp:shapeComment></hp:pic><hp:t/></hp:run></hp:p>'
            % (nid(), nid(), w, h, w, h, w // 2, h // 2, w, w, h, h, pw * 75, ph * 75, pw * 75, ph * 75, iid, w, h, escape(fname)))


media = []


def cell(col, row, width, text, head=False, first=False):
    bf, pp, st, cp = (61, 70, 23, 51) if (head or first) else (4, 71, 23, 52)
    paras = ''.join('<hp:p id="0" paraPrIDRef="%d" styleIDRef="%d" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="%d"><hp:t>%s</hp:t></hp:run></hp:p>' % (pp, st, cp, escape(t)) for t in text.split('\n'))
    return ('<hp:tc name="" header="%d" hasMargin="0" protect="0" editable="0" dirty="0" borderFillIDRef="%d"><hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">%s</hp:subList>'
            '<hp:cellAddr colAddr="%d" rowAddr="%d"/><hp:cellSpan colSpan="1" rowSpan="1"/><hp:cellSz width="%d" height="282"/><hp:cellMargin left="510" right="510" top="141" bottom="141"/></hp:tc>'
            % (1 if head else 0, bf, paras, col, row, width))


def table(caption, rows, widths):
    tot = sum(widths); ws = [int(round(w * 42318 / tot)) for w in widths]; ws[-1] += 42318 - sum(ws)
    trs = ''.join('<hp:tr>%s</hp:tr>' % ''.join(cell(ci, ri, ws[ci], t, head=(ri == 0), first=(ci == 0)) for ci, t in enumerate(r)) for ri, r in enumerate(rows))
    return ('<hp:p id="0" paraPrIDRef="51" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="20"><hp:tbl id="%d" zOrder="12" numberingType="TABLE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" pageBreak="TABLE" repeatHeader="1" rowCnt="%d" colCnt="%d" cellSpacing="0" borderFillIDRef="4" noAdjust="0">'
            '<hp:sz width="42318" widthRelTo="ABSOLUTE" height="%d" heightRelTo="ABSOLUTE" protect="0"/><hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="PARA" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/><hp:outMargin left="140" right="140" top="140" bottom="140"/>'
            '<hp:caption side="TOP" fullSz="0" width="8504" gap="850" lastWidth="42318"><hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="TOP" linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">'
            '<hp:p id="0" paraPrIDRef="65" styleIDRef="21" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="66"><hp:t>%s</hp:t></hp:run></hp:p></hp:subList></hp:caption>'
            '<hp:inMargin left="510" right="510" top="141" bottom="141"/>%s</hp:tbl><hp:t/></hp:run></hp:p>' % (nid(), len(rows), len(rows[0]), 282 * len(rows), escape(caption), trs))


# ---------------------------------------------------------------- 표지·제목
ps[3] = ps[3].replace('(9월)', '(10월)')
ps[10] = ps[10].replace('2026. 9.', '2026. 10.')

# ---------------------------------------------------------------- Ⅲ 주요 추진현황
def cell_paras(items):
    out = []
    for kind, t in items:
        if kind == 'h':
            out.append('<hp:p id="0" paraPrIDRef="52" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="24"><hp:t>&lt;%s&gt;</hp:t></hp:run></hp:p>' % escape(t))
        elif kind == 'b':
            out.append('<hp:p id="0" paraPrIDRef="53" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="26"><hp:t>%s</hp:t></hp:run></hp:p>' % escape(t))
    return ''.join(out)


ACT1 = [('h', '적용기술 요소 및 모델 제안'),
        ('b', '선행연구 조사를 바탕으로 기술요소(온톨로지 설계, 자료 구조화·연결, 수치자료 연계, 검색·응답)별 적용 방향 확정'),
        ('b', 'RAG-sLLM 아키텍처(안)의 구성 계층(지식기반·검색·응답 계층)과 계층 간 연계 구조 정리')]
PLAN1 = [('h', '적용기술 요소 및 모델 제안'),
         ('b', 'RAG-sLLM 아키텍처(안)와 데이터 파이프라인(안)를 통합하여 파트별 적용 기술이 반영된 최종 구조 정리'),
         ('b', 'sLLM 후보군 평가 결과를 응답 계층에 연계')]
ACT2 = [('h', 'RAG-LLM 통합 파이프라인(안) 제시'),
        ('b', '수집, 전처리, 지식기반 구성 각 단계의 파이프라인(안) 도식 작성'),
        ('b', '9월 조사·검토 결과를 바탕으로 수집경로, 온톨로지 설계방안, 데이터 전처리 체계(안) 정리'),
        ('b', '한수원 현장방문 계획 수립 (조사 항목 정리, 방문 일정 협의)')]
PLAN2 = [('h', 'RAG-LLM 통합 파이프라인(안) 제시'),
         ('b', '한수원 현장방문(11월 예정)을 통해 내부 데이터의 보유 현황·접근 경로를 조사하고 수집경로, 온톨로지 설계방안, 데이터 전처리 체계에 반영'),
         ('b', '수집부터 응답까지 이어지는 RAG-LLM 통합 파이프라인(안)을 표준 프롬프트 프레임과 연계하여 작성'),
         ('b', '자료 수집 방향(로드맵) 제시')]
t = ps[70]
t = t.replace('’26년 9월 실적', '’26년 10월 실적').replace('’26년 10월 계획', '’26년 11월 계획')
parts = t.split('<hp:tc ')
assert len(parts) == 11, len(parts)   # 앞부분 + 셀 10개
def set_cell(part, items):
    a = part.index('textHeight="0" hasTextRef="0" hasNumRef="0">') + len('textHeight="0" hasTextRef="0" hasNumRef="0">')
    b = part.index('</hp:subList>')
    return part[:a] + cell_paras(items) + part[b:]
# 셀 순서: 0 실적헤더, 1 계획헤더, 2~3 빈칸, 4 '1.' 제목, 5 실적1, 6 계획1, 7 '2.' 제목, 8 실적2, 9 계획2
for idx, items in ((6, ACT1), (7, PLAN1), (9, ACT2), (10, PLAN2)):
    pass
tcs = parts[1:]
order = [t_ for t_ in tcs]
def find(substr_row):
    return [i for i, c in enumerate(tcs) if substr_row in c]
rows = {}
for i, c in enumerate(tcs):
    m = re.search(r'<hp:cellAddr colAddr="(\d+)" rowAddr="(\d+)"/>', c)
    rows[(int(m.group(2)), int(m.group(1)))] = i
tcs[rows[(3, 0)]] = set_cell(tcs[rows[(3, 0)]], ACT1); tcs[rows[(3, 1)]] = set_cell(tcs[rows[(3, 1)]], PLAN1)
tcs[rows[(5, 0)]] = set_cell(tcs[rows[(5, 0)]], ACT2); tcs[rows[(5, 1)]] = set_cell(tcs[rows[(5, 1)]], PLAN2)
ps[70] = parts[0] + ''.join('<hp:tc ' + c for c in tcs)
# 고정 높이가 작으면 한글이 줄여 표시할 수 있어 셀 높이를 충분히 키운다
ps[70] = ps[70].replace('height="12446"', 'height="9000"').replace('height="7826"', 'height="9000"')

# ---------------------------------------------------------------- Ⅳ 세부 수행 실적
IV = [
    H1('1. 국내외 기술 트렌드 조사'),
    H2('1.3 적용 기술요소 및 모델 제안'),
    SQ('RAG-sLLM 아키텍처(안) 구성 계층'),
    CI('선행연구 조사 결과를 바탕으로 지식기반 계층, 검색 계층, 응답 계층의 3개 계층으로 아키텍처(안) 구성 (그림 1, 표 9)'),
    DS('지식기반 계층: 온톨로지 기반 KG에 개체 간 관계와 근거 출처를 구조화하고, 수치 시계열과 규정 원문은 외부 저장소에 두어 KG와 키로 연계 [2][3]'),
    DS('검색 계층: 질의에서 의도와 대상을 파악하고, 의도에 따라 KG와 외부 저장소에서 근거를 검색하여 출처가 붙은 근거로 구성 [4][5]'),
    DS('응답 계층: 구성된 근거를 입력으로 sLLM이 근거 중심으로 응답하며, 모델 및 성능 향상 방안은 3, 4에서 제시'),
    pic('fig1_architecture.png'),
    cap('그림 1 RAG-sLLM 아키텍처(안) 구성 계층'),
    SQ('기술요소별 적용 방향'),
    CI('아키텍처 계층별 기술요소를 선행연구와 비교하여 적용 방향 확정 (표 9)'),
    DS('온톨로지 설계: 범위·용도 확인에서 출발하는 단계적 설계와 전문가 검토를 통한 보완 [1]'),
    DS('수치자료 연계: 수치 시계열은 원본 저장소에 두고 KG는 코드·시점으로 연계 [2]'),
    DS('자료 연결 구조: 댐을 중심으로 수치·문서·규정을 연결하고 온톨로지 제약과 전문가 검증으로 점검 [3]'),
    DS('관계 생성: 자료에서 근거가 확인된 개체 쌍에만 관계 생성 [6]'),
    DS('질의 해석: 질의를 의도와 대상으로 해석하고, 의도별 질의 규칙으로 KG 조회 [5]'),
    DS('근거 검색·응답: KG 탐색과 의미(벡터) 검색을 결합하여 LLM에 전달할 근거 구성 [4]'),
    H1('2. LLM 활용 데이터 파이프라인 조사'),
    H2('2.3 RAG-LLM 통합 파이프라인(안) 제시'),
    SQ('데이터 파이프라인(안): 수집 → 전처리 → 지식기반 구성'),
    CI('수집, 전처리, 지식기반 구성의 3단계 파이프라인(안)을 도식화하고, 지식기반 구성 결과를 1.3의 지식기반 계층과 연결 (그림 2, 표 10)'),
    DS('수집: 수문·기상 자료, 운영 근거(규정), 방류 승인 기록을 자료별 제공 방식, 인증, 단위·주기에 맞춰 수집'),
    DS('전처리: 정형 자료는 열을 속성에, 행을 개체에 대응시키되 값은 원본 유지, 문서 자료(승인 비고, 규정 별표)는 규칙으로 값 추출, 시각·수치·결측 표기 통일'),
    DS('지식기반 구성: 코드·시점이 일치하는 개체 쌍에 관계를 생성하고 온톨로지 제약으로 검증한 뒤 KG와 외부 저장소에 저장'),
    pic('fig2_pipeline.png'),
    cap('그림 2 데이터 파이프라인(안): 수집, 전처리, 지식기반 구성'),
    SQ('수집경로·온톨로지 설계방안·전처리 체계(안) 정리'),
    CI('9월 조사·검토 결과를 바탕으로 수집경로, 온톨로지 설계방안, 데이터 전처리 체계(안)를 단계별 입력·처리·산출로 정리 (표 10)'),
    DS('수집경로: 영역별(수문, 기상, 운영 근거, 방류 승인) 제공기관·제공 방식·단위·주기 기준으로 정리 (9월 보고 표 2)'),
    DS('온톨로지 설계방안: 코드·시점 기준 연결, 출처·시점 정보 유지, 관계는 자료에서 근거가 확인된 경우에만 생성 (9월 보고 표 8)'),
    DS('전처리 체계: 대상 선택, 표기 형식 통일, 정형·문서 자료별 구조화 방식 구분'),
    SQ('한수원 현장방문 계획 수립'),
    CI('한수원 내부 자료의 보유 현황과 접근 경로를 조사하기 위해 현장방문(11월 26일 예정)의 조사 항목을 정리하고 방문 일정 협의 (표 11)'),
    DS('조사 결과는 수집경로, 온톨로지 설계방안, 데이터 전처리 체계에 반영'),
    H1('3. sLLM 후보군 평가 방향'),
    CI('(인공지능 학부 작성 내용 취합 예정)'),
    H1('4. 도메인 특화 성능 향상 전략'),
    CI('(인공지능 학부 작성 내용 취합 예정)'),
]

# ---------------------------------------------------------------- Ⅴ 부록 (표 9~11)
T9 = [['계층', '기술요소', '선행연구', '적용 방향'],
      ['지식기반', '온톨로지 설계', 'Noy & McGuinness(2001) [1]', '범위·용도 확인에서 출발하여 클래스·속성을 단계적으로 정의하고 전문가 검토로 보완'],
      ['지식기반', '수치자료 연계', 'Zhou 외(2022) [2]', '수치 시계열은 별도 저장소에 두고 KG는 코드·시점 키로 연계'],
      ['지식기반', '자료 연결 구조', 'Huang 외(2026) [3]', '댐을 중심으로 수치·문서·규정을 하나의 KG로 연결하고 제약 검사와 전문가 검증으로 점검'],
      ['지식기반', '관계 생성', 'Li 외(2025) [6]', '자료에서 근거가 확인된 개체 쌍에만 관계 생성'],
      ['검색', '질의 해석', 'Zhang 외(2025) [5]', '질의를 의도와 대상으로 해석하고 의도별 질의 규칙으로 KG 조회'],
      ['검색', 'KG·의미 검색 결합', 'Purohit 외(2024) [4]', 'KG 탐색으로 근거를 확보하고 의미 검색으로 보완하여 LLM에 전달할 컨텍스트 구성'],
      ['응답', '근거 기반 응답', 'Zhang 외(2025) [5], Purohit 외(2024) [4]', '출처가 포함된 근거를 프롬프트로 구성하여 sLLM이 근거 중심으로 응답 (모델은 3, 4에서 제시)']]
T10 = [['단계', '입력', '처리', '산출'],
       ['수집', '수문·기상 자료, 운영규정, 방류 승인 기록', '제공 방식, 인증, 단위·주기에 맞춰 수집', '원자료(수치 시계열, 문서, 승인 기록)'],
       ['전처리', '원자료', '정형 자료는 열→속성, 행→개체 대응(값 원본 유지), 문서 자료는 규칙으로 값 추출, 시각·수치·결측 표기 통일', '온톨로지에 맞춘 개체·속성'],
       ['지식기반 구성', '개체·속성', '코드·시점이 일치하는 개체 쌍에 관계 생성, 온톨로지 제약 검증, 저장', 'KG, 외부 저장소(측정자료·문서)']]
T11 = [['항목', '내용'],
       ['방문 일정', '2026. 11. 26. (예정, 일정 협의)'],
       ['조사 대상', '한수원 수문자료, 내부 센서 및 운영 데이터, 관제시스템'],
       ['조사 항목', '보유 자료 범위, 갱신 주기, 제공 방식, 접근 권한, 반출 제한'],
       ['방문 후 연계', '조사 결과를 수집경로, 온톨로지 설계방안, 전처리 체계에 반영하고, 관제시스템 확인 결과를 바탕으로 수행 가능한 태스크 후보를 정리하여 실무자 확인 요청']]
APPX = [H1('1. 국내외 기술 트렌드 조사'), H2('1.3 적용 기술요소 및 모델 제안'),
        table('표 9 RAG-sLLM 아키텍처 계층별 기술요소와 선행연구', T9, [10, 16, 22, 52]),
        H1('2. LLM 활용 데이터 파이프라인 조사'), H2('2.3 RAG-LLM 통합 파이프라인(안) 제시'),
        table('표 10 데이터 파이프라인 단계별 입력·처리·산출', T10, [12, 24, 40, 24]),
        table('표 11 한수원 현장방문 계획', T11, [14, 86])]

REF5 = 'Zhang 외(2025), "A knowledge graph-enhanced large language model for question answering of hydraulic structure safety management", Advanced Engineering Informatics, Vol. 66, 103468'
REF6 = 'Li 외(2025), "A semi-automated framework for flood ontology construction with an application in risk communication", Water, Vol. 17, No. 19, 2801'

# ---------------------------------------------------------------- 조립
new = ps[:72] + IV + [ps[154]] + APPX + [ps[167]] + ps[168:172]
new += ['<hp:p id="0" paraPrIDRef="69" styleIDRef="23" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="65"><hp:t>5. %s</hp:t></hp:run></hp:p>' % escape(REF5),
        '<hp:p id="0" paraPrIDRef="69" styleIDRef="23" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="65"><hp:t>6. %s</hp:t></hp:run></hp:p>' % escape(REF6), ps[172]]
body = head + ''.join(new) + tail
xml.dom.minidom.parseString(body.encode('utf8'))
cpf = z.read('Contents/content.hpf').decode('utf8')
for iid, fn in media:
    cpf = cpf.replace('<opf:item id="header"', '<opf:item id="%s" href="BinData/%s" media-type="image/png" isEmbeded="1"/><opf:item id="header"' % (iid, fn), 1)
with zipfile.ZipFile(OUT, 'w') as zo:
    zo.writestr(zipfile.ZipInfo('mimetype'), z.read('mimetype'), compress_type=zipfile.ZIP_STORED)
    for it in z.infolist():
        n = it.filename
        if n == 'mimetype' or n == 'Preview/PrvImage.png':
            continue
        data = body.encode('utf8') if n == 'Contents/section0.xml' else cpf.encode('utf8') if n == 'Contents/content.hpf' else z.read(n)
        zo.writestr(n, data, compress_type=zipfile.ZIP_DEFLATED)
    for iid, fn in media:
        zo.writestr('BinData/' + fn, open(os.path.join(FIGS, fn), 'rb').read(), compress_type=zipfile.ZIP_DEFLATED)
print('저장', OUT, len(new))
