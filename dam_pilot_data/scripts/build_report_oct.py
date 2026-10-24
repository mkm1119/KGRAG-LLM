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
        ('b', 'RAG-LLM 프레임워크를 5개 파트(온톨로지 설계, 자료 구조화·매핑, 수치자료 연계·저장, 질의 해석·검색, 근거 구성·응답)로 구분하고 파트별 선행연구의 기술·방법 분석'),
        ('b', '분석 결과를 바탕으로 파트별 적용 기술과 후속 검토 사항 정리'),
        ('b', 'RAG-sLLM 아키텍처(안)의 구성 계층(지식기반·검색·응답 계층)과 계층 간 연계 구조 정리')]
PLAN1 = [('h', '적용기술 요소 및 모델 제안'),
         ('b', 'RAG-sLLM 아키텍처(안)와 데이터 파이프라인(안)를 통합하여 파트별 적용 기술이 반영된 최종 구조 정리'),
         ('b', 'sLLM 후보군 평가 및 도메인 특화 성능 향상 전략 결과를 응답 계층에 반영'),
         ('b', '파트별 후속 검토 사항(의도 파악 방식, 검색 방식 등) 확정')]
ACT2 = [('h', 'RAG-LLM 통합 파이프라인(안) 제시'),
        ('b', '수집, 전처리, 지식기반 구성 각 단계의 파이프라인(안) 도식 작성'),
        ('b', '자료 유형(구조화 자료, 문서 자료)별 전처리 체계(안) 정리'),
        ('b', '온톨로지 시드의 설계·보완 절차와 KG 검증 방안 정리'),
        ('b', '9월 조사·검토 결과를 바탕으로 수집경로, 온톨로지 설계방안, 데이터 전처리 체계(안) 정리'),
        ('b', '검색 계층의 근거를 응답 계층에 전달하는 표준 프롬프트 프레임의 구성 틀 정리'),
        ('b', '한수원 현장방문 계획 수립 (조사 항목 정리, 방문 일정 협의)')]
PLAN2 = [('h', 'RAG-LLM 통합 파이프라인(안) 제시'),
         ('b', '한수원 현장방문(11월 예정)을 통해 내부 데이터의 보유 현황·접근 경로를 조사하고 수집경로, 온톨로지 설계방안, 데이터 전처리 체계에 반영'),
         ('b', '수집부터 응답까지 이어지는 RAG-LLM 통합 파이프라인(안)을 표준 프롬프트 프레임과 연계하여 작성'),
         ('b', '자료 수집 방향(로드맵) 제시'),
         ('b', '최종 보고서 작성을 위한 파트별 분석 결과 정리')]
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
    SQ('검토 방법'),
    CI('본 과업의 RAG-LLM 프레임워크를 온톨로지 설계, 자료 구조화·매핑, 수치자료 연계·저장, 질의 해석·검색, 근거 구성·응답의 5개 파트로 구분하고, 파트마다 선행연구의 기술과 방법을 분석하여 적용할 기술과 후속 검토 사항을 정리 (그림 1)'),
    CI('분석 대상: 온톨로지 설계 방법론 [1][6], 댐 분야 온톨로지·KG 구축 사례 [2][3], 그래프 기반 질의응답 시스템 [4][5], 검색 결합 생성(RAG) [7], 그래프 데이터베이스 [8]'),
    CI('10월에는 1.3에서 아키텍처 관점을, 2.3에서 데이터 파이프라인 관점을 각각 정리하고, 11월에 두 관점을 하나의 통합 구조로 정리'),
    pic('fig_approach.png'),
    cap('그림 1 연구 접근: 파트 분해, 기술 분석, 적용 선택, 통합'),
    SQ('RAG-sLLM 아키텍처(안) 구성 계층'),
    CI('선행연구 분석 결과를 바탕으로 지식기반, 검색, 응답의 3개 계층으로 아키텍처(안) 구성 (그림 2, 표 9)'),
    DS('지식기반 계층: 온톨로지 기반 KG에 개체 간 관계와 근거 출처를 구조화하고, 수치 시계열과 규정 원문은 외부 저장소에 두어 KG와 키로 연계 [2][3]'),
    DS('검색 계층: 질의에서 의도와 대상을 파악하고, 의도에 따라 KG와 외부 저장소에서 근거를 검색하여 출처가 붙은 근거로 구성 [4][5]'),
    DS('응답 계층: 구성된 근거를 입력으로 sLLM이 근거 중심으로 응답하며, 모델 및 성능 향상 방안은 3, 4에서 제시'),
    CI('계층 사이에서는 질의 → 의도·대상 → 근거 → 근거 묶음 → 응답의 순서로 정보가 전달되며, 지식기반 계층은 데이터 파이프라인(2.3)의 결과로 구성'),
    pic('fig1_architecture.png'),
    cap('그림 2 RAG-sLLM 아키텍처(안) 구성 계층'),
    SQ('파트별 기술 분석 및 적용 방향'),
    CI('① 온톨로지 설계 (표 10)'),
    DS('단계적 설계 방법론 [1]: 도메인·범위 결정 → 기존 온톨로지 재사용 검토 → 용어 나열 → 클래스·계층 정의 → 속성 정의 → 제약 정의 → 인스턴스 생성의 7단계이며, 하나의 정답이 있는 것이 아니라 반복적으로 개선하는 과정으로 제시'),
    DS('질문 기반 범위 설정 [1]: 온톨로지가 답해야 할 질문(Competency Question)을 범위 설정과 점검에 활용하되 모든 질문을 망라할 필요는 없다고 설명'),
    DS('시드 온톨로지와 확장 [6]: 전문가가 초기 온톨로지(시드)와 최상위 클래스를 정의하고, 질문 생성과 권위 문서를 통해 확장 후보를 만든 뒤 임베딩 유사도 필터와 전문가 검토를 거쳐 반영'),
    DS('댐 분야 적용 [2][3]: 댐 안전 모니터링에서 [1]의 절차를 적용하고 [2], 모든 최상위 클래스를 댐 개체에 연결하는 구조로 다원 자료를 하나의 KG에 정리 [3]'),
    DS('적용 방향: 질문 기반으로 필요한 Class·관계·속성을 정의한 초기 온톨로지(시드)를 두고 KG 구축·검증 결과로 보완하는 반복 절차와 댐 중심 연결 구조 채택 [1][3][6]. LLM을 이용한 질문 생성과 자동 확장 후보 필터는 자료 범위와 검증 체계가 정해진 뒤 검토'),
    CI('② 자료 구조화·매핑 (표 11)'),
    DS('구조화 자료 대응 [2]: 관계형 DB를 가상 RDF 그래프로 접근하여 데이터를 복제하지 않고 조회하며, 테이블은 클래스에, 컬럼은 속성에, 행은 인스턴스에, 셀 값은 리터럴에 대응시키고 자동 생성된 매핑은 온톨로지 용어에 맞게 수정'),
    DS('문서 자료 구조화 [3]: 자료를 구조화 표와 비정형 텍스트로 나누고, 텍스트는 변환·OCR·정규식으로 블록을 분리한 뒤 규칙 기반 추출 또는 LLM 기반 분류(미세조정, 온도 변화를 준 반복 추론의 투표, 온톨로지 제약 일관성 검사)로 처리'),
    DS('LLM 기반 지식 추출 [4][5]: 온톨로지로 LLM 응답 형식을 제한하고 개체 중의성 해소와 스키마 검증으로 일관성을 확보 [4], 개체·관계를 동시에 추출하고 F1로 성능을 평가 [5]'),
    DS('적용 방향: 정형 자료는 열을 속성에, 행을 개체에 대응시키고 값은 원본 유지 [2], 정해진 형태로 서술된 문서 자료(승인 비고, 규정 별표)는 규칙 기반으로 추출 [3], 관계는 자료에서 근거가 확인된 개체 쌍에만 생성 [6]. LLM 기반 추출은 정확도를 검증할 표본과 기준이 마련된 뒤 검토 [3][4][5]'),
    CI('③ 수치자료 연계·저장'),
    DS('가상 매핑 [2]: 수치 데이터를 원본 DB에 두고 온톨로지 질의로 조회하여 복제 없이 접근'),
    DS('외부 함수·저장소 연계 [4]: 시계열 등 외부 자료를 불러오는 외부 함수 실행 기능을 시스템 기능으로 제시 (보고된 실험에서는 다루지 않음)'),
    DS('그래프 데이터베이스 저장 [3][8]: 추출 결과를 JSON으로 통합하고 스크립트로 Cypher 명령문을 생성하여 Neo4j에 일괄 적재하며, 그래프 데이터베이스는 개체를 노드, 관계를 간선으로 저장'),
    DS('적용 방향: KG에는 개체·관계와 찾아가는 키(코드, 시점)만 저장하고 수치 시계열과 규정 원문은 외부 저장소(측정자료, 문서)에 보관 [2][4], KG는 Neo4j에 저장하고 Cypher로 조회 [3][8]'),
    CI('④ 질의 해석·검색 (표 12)'),
    DS('의도 파악 [5]: 질문의 의도를 규칙 기반, 지도학습 기반, LLM 기반 결과를 F1 점수 비중으로 투표하여 정하며, LLM 출력의 안정성이 충분하지 않다고 서술'),
    DS('질의 규칙 [5]: 의도 범주마다 자연어 질문을 Cypher 질의로 바꾸는 규칙을 미리 설계하고, 조회한 KG 지식을 LLM 프롬프트에 포함하여 우선 사용하도록 함'),
    DS('하이브리드 검색 [4]: 벡터 검색과 서브그래프 매칭을 결합한 컨텍스트 생성, 질의 확장, Cypher 자동 생성'),
    DS('적용 방향: 정해진 의도 범주에서 질문의 의도와 대상(댐·시점)을 추출하고 의도별 질의 규칙(Cypher)으로 KG 조회 [5], 추출된 의도와 대상이 허용 범위 안에 있는지 확인한 뒤 조회. 의도 파악 방식(규칙·학습·LLM 투표)과 벡터 검색 결합 여부는 11월 통합 구조에서 검토 [4][5]'),
    CI('⑤ 근거 구성·응답'),
    DS('검색 결합 생성 [7]: 검색한 근거를 생성 모델의 입력에 결합하여 모델 내부 지식에만 의존하지 않고 응답'),
    DS('지식 활용 프롬프트 [5]: KG에서 얻은 지식을 프롬프트에 포함하고 LLM이 이를 우선 사용하도록 하여 응답의 근거를 확보'),
    DS('컨텍스트 생성과 평가 [4]: 검색 결과를 컨텍스트로 구성하고, 여러 구성요소로 이루어진 시스템은 단일 지표만으로 평가하기 어려워 구성요소별 지표가 필요하다고 설명'),
    DS('적용 방향: 출처 번호가 붙은 근거 묶음과 근거 사용 원칙을 표준 프롬프트 프레임으로 구성하여 sLLM이 근거 중심으로 응답 [5][7], 답변은 근거와 판단을 구분하여 표기하고 근거에 없는 내용은 “자료에 없음”으로 처리, 평가는 검색(근거 확보)과 응답(근거 기반 답변)을 구분하여 설계 [4]'),
    SQ('적용 기술 종합'),
    CI('파트별 분석 결과 적용 기술과 후속 검토 사항을 표 13으로 정리하고, 후속 검토 사항은 11월 통합 구조 작성 과정에서 확정'),
    H1('2. LLM 활용 데이터 파이프라인 조사'),
    H2('2.3 RAG-LLM 통합 파이프라인(안) 제시'),
    SQ('데이터 파이프라인 구성'),
    CI('1.3의 지식기반 계층을 구성하는 데이터 파이프라인을 수집 → 전처리 → 지식기반 구성의 3단계로 설계하고, 현장방문으로 확보할 한수원 내부 자료를 수집 단계에 추가 (그림 3, 표 15)'),
    DS('수집: 수문·기상 자료, 운영 근거(규정), 방류 승인 기록을 자료별 제공 방식, 인증, 단위·주기에 맞춰 수집'),
    DS('전처리: 정형 자료는 열을 속성에, 행을 개체에 대응시키되 값은 원본 유지, 문서 자료(승인 비고, 규정 별표)는 규칙으로 값 추출, 시각·수치·결측 표기 통일'),
    DS('지식기반 구성: 코드·시점이 일치하는 개체 쌍에 관계를 생성하고 온톨로지 제약으로 검증한 뒤 KG와 외부 저장소에 저장'),
    pic('fig2_pipeline.png'),
    cap('그림 3 데이터 파이프라인(안): 수집, 전처리, 지식기반 구성'),
    SQ('수집 단계(안)'),
    CI('수집 대상을 수문, 기상, 운영 근거(규정), 방류 승인의 4개 영역으로 구분하고 영역별 제공기관·제공 방식·인증·단위·주기를 기준으로 수집경로 정리 (9월 조사 결과)'),
    DS('수치 시계열(수문·기상)은 관측소·댐 코드와 시점을 기준으로 수집하여 외부 저장소(측정자료)에 보관'),
    DS('운영 근거(규정)는 개정 연혁을 포함한 문서 단위로 수집하여 문서 저장소에 보관'),
    DS('방류 승인은 승인 건별 기록을 파일로 수집'),
    DS('한수원 내부 자료(수문자료, 내부 센서·운영 데이터)는 현장방문 후 수집경로에 추가'),
    SQ('전처리 단계(안)'),
    CI('자료 유형(구조화 자료, 문서 자료)에 따라 처리 경로를 구분하고 공통 정리 항목을 적용 (그림 4, 표 14)'),
    DS('구조화 자료: 열은 속성에, 행은 개체에 대응시키고 값은 원본 그대로 유지하며 코드와 시점을 연결 키로 사용 [2]'),
    DS('문서 자료: 문서 단위로 분리하고 규칙(키워드, 정규식)으로 값을 추출하며, 문자로 그린 표는 행과 열 구조로 변환 [3]'),
    DS('공통 정리: 시각, 수치, 결측 표기를 하나의 형식으로 통일하고 대상 선택과 중복 제거를 수행하며 자료의 출처와 시점 정보를 유지'),
    DS('원본 자료는 변경하지 않고 정리 내용을 기록으로 남겨 추적'),
    pic('fig_process.png'),
    cap('그림 4 자료 유형별 전처리 경로'),
    SQ('지식기반 구성 단계(안)'),
    CI('온톨로지(시드)에 맞춰 개체를 만들고 관계를 연결한 뒤 검증하여 저장'),
    DS('개체 생성: 전처리된 자료의 행·값을 온톨로지의 Class와 속성에 맞춰 개체로 생성하고 개체마다 근거 출처 개체를 연결'),
    DS('관계 연결: 코드, 이름, 순번 등 자료에 적힌 값이 일치하는 개체 쌍에만 관계를 생성하고 근거 없는 추정 연결은 만들지 않음 [6]'),
    DS('검증: 온톨로지가 허용한 관계의 양 끝 Class, 필수 속성, 값 형식, 근거 연결 여부를 점검하고, 질문마다 정해진 경로로 필요한 개체에 도달하는지 확인 [3]'),
    DS('저장: 개체·관계는 JSON으로 정리하여 Cypher 명령문으로 변환해 Neo4j에 적재하고, 수치와 원문은 외부 저장소에 둠 [3]'),
    SQ('온톨로지 설계방안'),
    CI('온톨로지는 질문에서 출발하여 시드를 정의하고, KG 구축과 검증 결과로 보완하는 절차로 설계 (그림 5)'),
    DS('질문(CQ)과 범위를 정한 뒤 이에 답하는 데 필요한 Class·관계·속성을 시드로 정의'),
    DS('구축한 KG로 질문에 필요한 개체에 도달하는지 점검하고, 도달하지 못하면 부족한 관계나 속성을 시드에 추가'),
    DS('보완 내용은 전문가 검토를 거쳐 반영하며 자동 생성된 내용은 그대로 수용하지 않음 [1][6]'),
    pic('fig_seed.png'),
    cap('그림 5 온톨로지 시드 설계·보완 절차'),
    SQ('검색·응답 연계(표준 프롬프트 프레임)'),
    CI('검색 계층이 구성한 근거를 응답 계층(sLLM)에 전달하는 표준 프롬프트 프레임의 구성 틀 정리 (그림 6, 표 16)'),
    DS('근거 묶음: 의도별 구역(현재 상태, 과거 상태, 운영행위·승인, 운영기준, 출처 및 위치)으로 근거를 모으고 항목마다 출처 번호 부여'),
    DS('근거 사용 원칙: 주어진 근거만 사실로 사용, 해석·비교는 판단으로 구분하여 근거를 함께 표기, 근거에 없는 내용은 “자료에 없음”으로 답변'),
    DS('프레임의 세부 항목과 sLLM 연계 방식은 11월 통합 구조에서 구체화'),
    pic('fig_frame.png'),
    cap('그림 6 표준 프롬프트 프레임 구성 틀'),
    SQ('수집경로·온톨로지 설계방안·전처리 체계(안) 정리'),
    CI('9월 조사·검토 결과를 바탕으로 수집경로, 온톨로지 설계방안, 데이터 전처리 체계(안)를 3단계의 입력·처리·산출로 정리 (표 15)'),
    DS('수집경로: 영역별(수문, 기상, 운영 근거, 방류 승인) 제공기관·제공 방식·단위·주기 기준으로 정리 (9월 보고 표 2)'),
    DS('온톨로지 설계방안: 코드·시점 기준 연결, 출처·시점 정보 유지, 관계는 자료에서 근거가 확인된 경우에만 생성 (9월 보고 표 8)'),
    DS('전처리 체계: 대상 선택, 표기 형식 통일, 정형·문서 자료별 구조화 방식 구분 (표 14)'),
    SQ('한수원 현장방문 계획 수립'),
    CI('한수원 내부 자료의 보유 현황과 접근 경로를 조사하기 위해 현장방문(11월 26일 예정)의 조사 항목을 정리하고 방문 일정 협의 (표 17)'),
    DS('조사 항목: 보유 자료 범위, 갱신 주기, 제공 방식, 접근 권한, 반출 제한'),
    DS('관제시스템 확인을 통해 자료의 생성·활용 방식을 파악하고, 확인 결과를 바탕으로 수행 가능한 태스크 후보를 정리하여 실무자 확인 요청'),
    DS('조사 결과는 수집경로, 온톨로지 설계방안, 전처리 체계에 반영하여 11월 통합 구조에 포함'),
    SQ('11월 통합 계획'),
    CI('1.3의 아키텍처 구성 계층과 2.3의 데이터 파이프라인을 하나의 RAG-LLM 통합 파이프라인(안)으로 통합 (지식기반 계층 = 지식기반 구성 단계의 결과)'),
    DS('파트별 적용 기술 확정과 sLLM 후보군 평가·도메인 특화 성능 향상 전략(3, 4)의 반영'),
    DS('현장방문 결과를 반영한 수집·전처리 보완'),
    DS('자료 수집 방향(로드맵) 제시'),
    H1('3. sLLM 후보군 평가 방향'),
    CI('(인공지능 학부 작성 내용 취합 예정)'),
    H1('4. 도메인 특화 성능 향상 전략'),
    CI('(인공지능 학부 작성 내용 취합 예정)'),
]

T9 = [['계층', '기술요소', '선행연구', '적용 방향'],
      ['지식기반', '온톨로지 설계', 'Noy & McGuinness(2001) [1]', '범위·용도 확인에서 출발하여 클래스·속성을 단계적으로 정의하고 전문가 검토로 보완'],
      ['지식기반', '수치자료 연계', 'Zhou 외(2022) [2]', '수치 시계열은 별도 저장소에 두고 KG는 코드·시점 키로 연계'],
      ['지식기반', '자료 연결 구조', 'Huang 외(2026) [3]', '댐을 중심으로 수치·문서·규정을 하나의 KG로 연결하고 제약 검사와 전문가 검증으로 점검'],
      ['지식기반', '관계 생성', 'Li 외(2025) [6]', '자료에서 근거가 확인된 개체 쌍에만 관계 생성'],
      ['검색', '질의 해석', 'Zhang 외(2025) [5]', '질의를 의도와 대상으로 해석하고 의도별 질의 규칙으로 KG 조회'],
      ['검색', 'KG·의미 검색 결합', 'Purohit 외(2024) [4]', 'KG 탐색으로 근거를 확보하고 의미 검색으로 보완하여 LLM에 전달할 컨텍스트 구성'],
      ['응답', '근거 기반 응답', 'Zhang 외(2025) [5], Lewis 외(2020) [7]', '출처가 포함된 근거를 프롬프트로 구성하여 sLLM이 근거 중심으로 응답 (모델은 3, 4에서 제시)']]
T10 = [['방법', '선행연구', '주요 내용', '본 과업의 활용'],
       ['단계적 설계 방법론', 'Noy & McGuinness(2001) [1]', '도메인·범위 결정, 재사용 검토, 용어 나열, 클래스·계층, 속성, 제약, 인스턴스의 7단계. 반복적 개선. 질문(CQ)을 범위 점검에 활용', '채택: 질문 기반으로 Class·관계·속성을 단계적으로 정의'],
       ['시드 온톨로지와 확장', 'Li 외(2025) [6]', '전문가가 초기 온톨로지(시드)를 정의하고 질문 생성·권위 문서로 확장 후보를 만든 뒤 자동 필터와 전문가 검토로 반영. 관계는 근거가 확인되는 개체 쌍에만 생성', '일부 채택: 시드 정의, 전문가 검토 후 반영, 근거가 확인된 관계. LLM 기반 질문 생성·자동 필터는 후속 검토'],
       ['댐 분야 적용 사례', 'Zhou 외(2022) [2]', '[1]의 절차를 댐 안전 모니터링에 적용하고 기존 어휘의 재사용을 검토', '참고: 범위 한정과 재사용 검토 방식'],
       ['댐 중심 연결 구조', 'Huang 외(2026) [3]', '7단계로 구축하고 모든 최상위 클래스를 댐 개체에 연결하여 다원 자료를 하나의 KG에 정리', '채택: 댐 중심 연결 구조']]
T11 = [['기술', '선행연구', '방식', '특징', '본 과업의 활용'],
       ['가상 매핑', 'Zhou 외(2022) [2]', '관계형 DB를 가상 RDF 그래프로 접근. 테이블→클래스, 컬럼→속성, 행→인스턴스, 셀→리터럴', '복제 없이 조회. 자동 생성 매핑의 수정 필요', '채택(원칙): 열→속성, 행→개체, 값 원본 유지'],
       ['규칙 기반 추출', 'Huang 외(2026) [3]', '변환·OCR·정규식으로 블록을 분리한 뒤 규칙으로 추출', '정해진 형태로 서술된 내용에 적합. 규칙 작성 필요', '채택: 승인 비고, 규정 별표'],
       ['LLM 기반 분류·추출', 'Huang 외(2026) [3], Purohit 외(2024) [4], Zhang 외(2025) [5]', '미세조정·투표·제약 일관성 검사 [3], 응답 형식 제한·중의성 해소·스키마 검증 [4], 개체·관계 동시 추출과 F1 평가 [5]', '비정형 텍스트로 확장 가능. 정확도 검증 체계 필요', '후속 검토']]
T12 = [['기술', '선행연구', '방식', '본 과업의 활용'],
       ['의도 파악', 'Zhang 외(2025) [5]', '규칙·지도학습·LLM 결과를 F1 비중으로 투표. LLM 출력 안정성 한계 서술', '후속 검토 (의도 범주 기반 추출은 채택)'],
       ['질의 규칙', 'Zhang 외(2025) [5]', '의도 범주별 Cypher 질의 규칙을 미리 설계하고 KG 지식을 프롬프트에 포함', '채택'],
       ['하이브리드 검색', 'Purohit 외(2024) [4]', '벡터 검색과 서브그래프 매칭 결합, 질의 확장, Cypher 자동 생성', '후속 검토'],
       ['검색 결합 생성', 'Lewis 외(2020) [7]', '검색한 근거를 생성 모델 입력에 결합', '채택'],
       ['구성요소별 평가', 'Purohit 외(2024) [4]', '여러 구성요소로 이루어진 시스템은 구성요소별 지표 필요', '채택(원칙): 검색과 응답을 구분하여 평가 설계']]
T13 = [['파트', '적용 기술(안)', '근거', '후속 검토 사항'],
       ['온톨로지 설계', '질문 기반 시드 정의, 검증 결과로 보완, 댐 중심 연결', '[1][3][6]', 'LLM 기반 질문 생성·자동 확장 후보 필터'],
       ['자료 구조화·매핑', '정형 자료는 열→속성·행→개체, 문서 자료는 규칙 기반 추출', '[2][3][6]', 'LLM 기반 추출(정확도 검증 체계 마련 후)'],
       ['수치자료 연계·저장', 'KG에는 키만, 수치·원문은 외부 저장소. Neo4j와 Cypher', '[2][3][4][8]', '현장 자료의 제공 방식에 따른 연계 방식 보완'],
       ['질의 해석·검색', '의도 범주 추출 후 의도별 질의 규칙으로 KG 조회', '[5]', '의도 파악 방식, 벡터 검색 결합'],
       ['근거 구성·응답', '출처 번호가 붙은 근거 묶음, 근거와 판단 구분, sLLM 응답', '[4][5][7]', '프롬프트 프레임 세부, 응답 평가 방식']]
T14 = [['자료 유형', '대상 자료', '처리', '연결 키', '보관 위치'],
       ['구조화 자료', '수문·기상 시계열', '열→속성 대응, 시각·수치·결측 표기 통일', '관측소·댐 코드, 시점', '값: 측정자료 저장소, 키: KG'],
       ['구조화 자료', '시설(댐) 정보', '대상 시설 선택, 코드·명칭 정리', '댐 코드', 'KG'],
       ['구조화 자료', '방류 승인 기록의 정형 항목', '중복 제거, 시각 표기 통일, 대상 선택', '관측소 코드, 순번', 'KG'],
       ['문서 자료', '방류 승인 기록의 비고', '키워드 규칙으로 운영행위 종류와 시각 추출', '승인 순번', 'KG'],
       ['문서 자료', '규정 별표(기준값 표)', '별표 단위 분리, 문자로 그린 표를 행·열로 변환, 댐 이름 표기 정리', '댐 이름', '값: KG, 원문: 문서 저장소']]
T15 = [['단계', '입력', '처리', '산출'],
       ['수집', '수문·기상 자료, 운영규정, 방류 승인 기록 (+ 한수원 내부 자료)', '제공 방식, 인증, 단위·주기에 맞춰 수집', '원자료(수치 시계열, 문서, 승인 기록)'],
       ['전처리', '원자료', '정형 자료는 열→속성, 행→개체 대응(값 원본 유지), 문서 자료는 규칙으로 값 추출, 시각·수치·결측 표기 통일', '온톨로지에 맞춘 개체·속성'],
       ['지식기반 구성', '개체·속성', '코드·시점이 일치하는 개체 쌍에 관계 생성, 온톨로지 제약 검증, 저장', 'KG, 외부 저장소(측정자료·문서)']]
T16 = [['구성 요소', '내용', '역할'],
       ['사용자 질의', '운영자가 입력한 질문', '의도와 대상(댐·시점) 추출의 입력'],
       ['근거 묶음', '의도별 구역(현재 상태, 과거 상태, 운영행위·승인, 운영기준, 출처 및 위치)으로 모은 근거와 항목별 출처 번호', '응답의 사실 근거'],
       ['근거 사용 원칙', '주어진 근거만 사실로 사용, 해석·비교는 판단으로 구분하고 근거 표기, 근거에 없으면 “자료에 없음”', '응답 형식과 범위 제어'],
       ['응답', '근거와 판단을 구분한 답변', '운영자 의사결정 지원']]
T17 = [['항목', '내용'],
       ['방문 일정', '2026. 11. 26. (예정, 일정 협의)'],
       ['조사 대상', '한수원 수문자료, 내부 센서 및 운영 데이터, 관제시스템'],
       ['조사 항목', '보유 자료 범위, 갱신 주기, 제공 방식, 접근 권한, 반출 제한'],
       ['확인 사항', '자료 식별 방식(코드·명칭 체계), 시각·단위·결측 표기, 자료 생성·활용 방식'],
       ['방문 후 연계', '조사 결과를 수집경로, 온톨로지 설계방안, 전처리 체계에 반영하고, 관제시스템 확인 결과를 바탕으로 수행 가능한 태스크 후보를 정리하여 실무자 확인 요청']]
APPX = [H1('1. 국내외 기술 트렌드 조사'), H2('1.3 적용 기술요소 및 모델 제안'),
        table('표 9 RAG-sLLM 아키텍처 계층별 기술요소와 선행연구', T9, [9, 15, 24, 52]),
        table('표 10 온톨로지 설계 방법 비교', T10, [16, 18, 36, 30]),
        table('표 11 자료 구조화·지식 추출 기술 비교', T11, [14, 18, 32, 18, 18]),
        table('표 12 질의 해석·검색·응답 기술 비교', T12, [14, 18, 42, 26]),
        table('표 13 파트별 적용 기술 종합', T13, [16, 34, 14, 36]),
        H1('2. LLM 활용 데이터 파이프라인 조사'), H2('2.3 RAG-LLM 통합 파이프라인(안) 제시'),
        table('표 14 자료 유형별 전처리 체계(안)', T14, [12, 20, 34, 16, 18]),
        table('표 15 데이터 파이프라인 단계별 입력·처리·산출', T15, [12, 26, 38, 24]),
        table('표 16 표준 프롬프트 프레임 구성', T16, [16, 56, 28]),
        table('표 17 한수원 현장방문 계획', T17, [14, 86])]

REF5 = 'Zhang 외(2025), "A knowledge graph-enhanced large language model for question answering of hydraulic structure safety management", Advanced Engineering Informatics, Vol. 66, 103468'
REF7 = 'Lewis 외(2020), "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", Advances in Neural Information Processing Systems, Vol. 33, pp. 9459-9474'
REF8 = 'Angles, R., Gutierrez, C.(2008), "Survey of Graph Database Models", ACM Computing Surveys, Vol. 40, No. 1, Article 1'
REF6 = 'Li 외(2025), "A semi-automated framework for flood ontology construction with an application in risk communication", Water, Vol. 17, No. 19, 2801'

# ---------------------------------------------------------------- 조립
new = ps[:72] + IV + [ps[154]] + APPX + [ps[167]] + ps[168:172]
new += ['<hp:p id="0" paraPrIDRef="69" styleIDRef="23" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="65"><hp:t>5. %s</hp:t></hp:run></hp:p>' % escape(REF5),
        '<hp:p id="0" paraPrIDRef="69" styleIDRef="23" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="65"><hp:t>6. %s</hp:t></hp:run></hp:p>' % escape(REF6),
        '<hp:p id="0" paraPrIDRef="69" styleIDRef="23" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="65"><hp:t>7. %s</hp:t></hp:run></hp:p>' % escape(REF7),
        '<hp:p id="0" paraPrIDRef="69" styleIDRef="23" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="65"><hp:t>8. %s</hp:t></hp:run></hp:p>' % escape(REF8), ps[172]]
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
