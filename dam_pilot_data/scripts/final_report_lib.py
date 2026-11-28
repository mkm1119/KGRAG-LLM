#!/usr/bin/env python3
"""최종보고서(hwpx) 작성 도구. 템플릿(project_khnp/final_report/최종보고서_템플릿.hwpx)의 스타일을 그대로 쓴다.
템플릿의 문단·표 XML을 본보기로 삼아 같은 스타일 번호로 문단과 표를 만들고, 절 제목 아래의 빈 문단을 내용으로 바꾼다.
한글 프로그램이 없는 환경에서 만들므로 줄 나눔 정보(linesegarray)는 넣지 않는다(한글이 열 때 계산한다).

쓰는 법:
    from final_report_lib import *
    doc = Report(TEMPLATE)
    doc.fill('1.1 수자원 분야 사례 조사', [H3('1.1.1 조사 개요'), BODY('...'), SQ('...'), CI('...'), DS('...'), *table('표 1.1 ...', rows, [20, 30, 50])])
    doc.references(['저자(연도), "제목", 학술지, 권(호), 쪽.', ...])
    doc.save(out_path)
"""
import os, re, zipfile, xml.dom.minidom
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, '..', '..', 'project_khnp', 'final_report', '최종보고서_템플릿.hwpx')
WIDTH = 49606                      # 본문 폭(발주처 양식의 여백: 210 - 15 - 12 - 제본 8 = 175mm)
_id = [1950000000]


def nid():
    _id[0] += 1
    return _id[0]


def _p(text, para, style, char, page_break=0):
    return ('<hp:p id="0" paraPrIDRef="%d" styleIDRef="%d" pageBreak="%d" columnBreak="0" merged="0"><hp:run charPrIDRef="%d"><hp:t>%s</hp:t></hp:run></hp:p>'
            % (para, style, page_break, char, escape(text)))


# 스타일 번호는 템플릿 header.xml의 '보고서_*' 스타일과 같다 (문단 모양, 스타일, 글자 모양)
def H1(t): return _p(t, 33, 34, 22, 1)        # 1. 큰 목차 (새 쪽)
def H2(t): return _p(t, 34, 35, 17)           # 1.1
def H3(t): return _p(t, 35, 36, 23)           # 1.1.1
def H4(t): return _p(t, 36, 37, 24)           # 가.
def H5(t): return _p(t, 37, 38, 25)           # (1)
def BODY(t): return _p(t, 38, 39, 26)         # 본문
def SQ(t): return _p('□ ' + t, 39, 40, 26)
def CI(t): return _p('◦ ' + t, 40, 41, 26)
def DS(t): return _p('- ' + t, 41, 42, 26)
def TCAP(t): return _p(t, 42, 43, 27)         # 표 제목 (표 위)
def FCAP(t): return _p(t, 43, 44, 27)         # 그림 제목 (그림 아래)
def UNIT(t): return _p(t, 46, 48, 28)         # [단위: ]
def NOTE(t): return _p(t, 47, 49, 28)         # 주·자료
def REF(t): return _p(t, 48, 50, 26)          # 참고문헌
def BLANK(): return _p('', 38, 39, 26)

# 목차 쪽(발주처 양식): 제목 20pt 굵게 가운데, 줄마다 점선과 쪽 번호 자리. 문단·글자 모양 번호는 upgrade_template_khnp.py가 덧붙인 것이다.
_TAB = '<hp:tab width="20000" leader="3" type="2"/>'      # 점선은 문단 모양의 탭 정의(오른쪽 탭, 채움선)에서 나온다
ROMAN = '<hp:ctrl><hp:pageNum pos="BOTTOM_CENTER" formatType="ROMAN_SMALL" sideChar="-"/></hp:ctrl>'



# ── 그림(이미지) 삽입 ─────────────────────────────────────────────
PICS = []                     # (binary item id, 파일 경로) — save()에서 BinData와 manifest에 넣는다


def _png_size(path):
    import struct
    with open(path, 'rb') as f:
        head = f.read(24)
    return struct.unpack('>II', head[16:24])


def PIC(path, max_w=None, max_h=40000):
    """PNG 그림을 글자처럼 취급하는 개체로 넣은 가운데 정렬 문단을 만든다(그림 제목 문단과 같은 정렬)."""
    wpx, hpx = _png_size(path)
    ow, oh = wpx * 75, hpx * 75                      # 96dpi 기준 hwpunit
    cw = min(max_w or int(WIDTH * 0.92), ow); ch = int(cw * oh / ow)
    if ch > max_h:
        ch = max_h; cw = int(ch * ow / oh)
    bid = 'fig%d' % (len(PICS) + 1); PICS.append((bid, path))
    sx, sy = cw / ow, ch / oh
    pic = ('<hp:pic id="%d" zOrder="0" numberingType="PICTURE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" href="" groupLevel="0" instid="%d" reverse="0">'
           '<hp:offset x="0" y="0"/><hp:orgSz width="%d" height="%d"/><hp:curSz width="%d" height="%d"/><hp:flip horizontal="0" vertical="0"/>'
           '<hp:rotationInfo angle="0" centerX="%d" centerY="%d" rotateimage="1"/><hp:renderingInfo><hc:transMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/>'
           '<hc:scaMatrix e1="%.6f" e2="0" e3="0" e4="0" e5="%.6f" e6="0"/><hc:rotMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/></hp:renderingInfo>'
           '<hp:imgRect><hc:pt0 x="0" y="0"/><hc:pt1 x="%d" y="0"/><hc:pt2 x="%d" y="%d"/><hc:pt3 x="0" y="%d"/></hp:imgRect>'
           '<hp:imgClip left="0" right="%d" top="0" bottom="%d"/><hp:inMargin left="0" right="0" top="0" bottom="0"/><hp:imgDim dimwidth="%d" dimheight="%d"/>'
           '<hc:img binaryItemIDRef="%s" bright="0" contrast="0" effect="REAL_PIC" alpha="0"/><hp:effects/>'
           '<hp:sz width="%d" widthRelTo="ABSOLUTE" height="%d" heightRelTo="ABSOLUTE" protect="0"/>'
           '<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="PARA" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>'
           '<hp:outMargin left="0" right="0" top="0" bottom="0"/></hp:pic>') % (
        nid(), nid(), ow, oh, cw, ch, cw // 2, ch // 2, sx, sy, ow, ow, oh, oh, ow, oh, ow, oh, bid, cw, ch)
    p = FCAP('')
    return re.sub(r'<hp:run ([^>]*)>.*?</hp:run>', lambda m: '<hp:run %s>%s<hp:t/></hp:run>' % (m.group(1), pic), p, count=1, flags=re.S) if '<hp:run' in p else p

# ---- 한글 도형(사각형, 화살표 선)으로 그리는 그림 ----
_IDM = '<hc:scaMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/><hc:rotMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/>'


def _shape_head(tag, x, y, w, h, grouped, extra=''):
    wrap = 'TOP_AND_BOTTOM'
    return ('<hp:%s id="%d" zOrder="%d" numberingType="NONE" textWrap="%s" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" href="" groupLevel="%d" instid="%d"%s>'
            '<hp:offset x="%d" y="%d"/><hp:orgSz width="%d" height="%d"/><hp:curSz width="%d" height="%d"/><hp:flip horizontal="0" vertical="0"/>'
            '<hp:rotationInfo angle="0" centerX="%d" centerY="%d" rotateimage="1"/><hp:renderingInfo><hc:transMatrix e1="1" e2="0" e3="%d" e4="0" e5="1" e6="%d"/>%s</hp:renderingInfo>'
            % (tag, nid(), nid() % 1000, wrap, 1 if grouped else 0, nid(), extra,
               x if grouped else 0, y if grouped else 0, w, h, w, h, w // 2, h // 2, x if grouped else 0, y if grouped else 0, _IDM))


def _shape_tail(tag, x, y, w, h, grouped):
    if grouped:
        return '</hp:%s>' % tag
    return ('<hp:sz width="%d" widthRelTo="ABSOLUTE" height="%d" heightRelTo="ABSOLUTE" protect="0"/>'
            '<hp:pos treatAsChar="0" affectLSpacing="0" flowWithText="1" allowOverlap="1" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="COLUMN" vertAlign="TOP" horzAlign="LEFT" vertOffset="%d" horzOffset="%d"/>'
            '<hp:outMargin left="0" right="0" top="0" bottom="0"/></hp:%s>' % (w, h, y, x, tag))


def _rect(x, y, w, h, lines, fill='#FFFFFF', border=True, grouped=True):
    brush = '<hc:fillBrush><hc:winBrush faceColor="%s" hatchColor="#000000" alpha="0"/></hc:fillBrush>' % fill if fill else ''
    paras = ''.join('<hp:p id="0" paraPrIDRef="44" styleIDRef="46" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="20"><hp:t>%s</hp:t></hp:run></hp:p>' % escape(t) for t in lines)
    return (_shape_head('rect', x, y, w, h, grouped, ' ratio="0"')
            + '<hp:lineShape color="#404040" width="%d" style="%s" endCap="FLAT" headStyle="NORMAL" tailStyle="NORMAL" headfill="1" tailfill="1" headSz="MEDIUM_MEDIUM" tailSz="MEDIUM_MEDIUM" outlineStyle="NORMAL" alpha="0"/>' % (57 if border else 0, 'SOLID' if border else 'NONE')
            + brush
            + '<hp:shadow type="NONE" color="#B2B2B2" offsetX="0" offsetY="0" alpha="0"/>'
            + '<hp:drawText lastWidth="%d" name="" editable="0"><hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">%s</hp:subList>'
              '<hp:textMargin left="283" right="283" top="283" bottom="283"/></hp:drawText>' % (w, paras)
            + '<hc:pt0 x="0" y="0"/><hc:pt1 x="%d" y="0"/><hc:pt2 x="%d" y="%d"/><hc:pt3 x="0" y="%d"/>' % (w, w, h, h)
            + _shape_tail('rect', x, y, w, h, grouped))


def _arrow(x1, y1, x2, y2, grouped=True):
    """(x1, y1)에서 (x2, y2)로 가는 화살표 선."""
    x, y, w, h = min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1)
    return (_shape_head('line', x, y, max(w, 1), max(h, 1), grouped, ' isReverseHV="0"')
            + '<hp:lineShape color="#404040" width="85" style="SOLID" endCap="FLAT" headStyle="NORMAL" tailStyle="ARROW" headfill="1" tailfill="1" headSz="MEDIUM_MEDIUM" tailSz="MEDIUM_MEDIUM" outlineStyle="NORMAL" alpha="0"/>'
            + '<hp:shadow type="NONE" color="#B2B2B2" offsetX="0" offsetY="0" alpha="0"/>'
            + '<hc:startPt x="%d" y="%d"/><hc:endPt x="%d" y="%d"/>' % (x1 - x, y1 - y, x2 - x, y2 - y)
            + _shape_tail('line', x, y, max(w, 1), max(h, 1), grouped))


def DRAWING(shapes, W, H, mode='group'):
    """도형 목록으로 그림 문단을 만든다. shapes: ('box', x, y, w, h, [줄...], 채움색) / ('text', x, y, w, h, [줄...]) / ('arrow', x1, y1, x2, y2).
    mode 'group': 묶음 개체 하나를 글자처럼 취급 / 'free': 도형을 하나씩 문단 기준 위치에 둔다."""
    g = mode == 'group'
    xs = []
    for sh in shapes:
        if sh[0] == 'box': xs.append(_rect(sh[1], sh[2], sh[3], sh[4], sh[5], sh[6] if len(sh) > 6 else '#FFFFFF', True, g))
        elif sh[0] == 'text': xs.append(_rect(sh[1], sh[2], sh[3], sh[4], sh[5], None, False, g))
        else: xs.append(_arrow(sh[1], sh[2], sh[3], sh[4], g))
    if g:
        obj = ('<hp:container id="%d" zOrder="0" numberingType="PICTURE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" href="" groupLevel="0" instid="%d">'
               '<hp:offset x="0" y="0"/><hp:orgSz width="%d" height="%d"/><hp:curSz width="%d" height="%d"/><hp:flip horizontal="0" vertical="0"/>'
               '<hp:rotationInfo angle="0" centerX="%d" centerY="%d" rotateimage="1"/><hp:renderingInfo><hc:transMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/>%s</hp:renderingInfo>%s'
               '<hp:sz width="%d" widthRelTo="ABSOLUTE" height="%d" heightRelTo="ABSOLUTE" protect="0"/>'
               '<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="PARA" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>'
               '<hp:outMargin left="0" right="0" top="0" bottom="0"/></hp:container>') % (nid(), nid(), W, H, W, H, W // 2, H // 2, _IDM, ''.join(xs), W, H)
    else:
        obj = ''.join(xs)
    p = FCAP('')
    return re.sub(r'<hp:run ([^>]*)>.*?</hp:run>', lambda m: '<hp:run %s>%s<hp:t/></hp:run>' % (m.group(1), obj), p, count=1, flags=re.S)


def _toc(t, para, char, page=''):
    return ('<hp:p id="0" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="%d"><hp:t>%s%s%s</hp:t></hp:run></hp:p>'
            % (para, char, escape(t), _TAB, escape(page)))


def TITLE(t): return _p(t, 55, 0, 33, 1)        # 목 차, 표 목 차, 그 림 목 차, 참 고 문 헌 (새 쪽)
def TOCC(t, page=''): return _toc(t, 56, 34, page)   # 목차: 장(15pt)
def TOCE(t, page=''): return _toc(t, 56, 26, page)   # 목차: 가. 수준(12pt)
def LISTE(t, page=''): return _toc(t, 57, 26, page)  # 표 목차, 그림 목차의 줄
def PAGELINE(): return _p('PAGE', 58, 0, 26)
def TBLANK(): return _p('', 56, 0, 26)
def nospace(p): return text_of(p).replace(' ', '')


# 발주처 양식의 제목 번호: 1. -> 가. -> 1) -> 가) -> ①. 소절 파일은 2.1.3, 가., (1)로 적어 두고 조립할 때 바꾼다.
KA = '가나다라마바사아자차카타파하'
CIRC = '①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮'


def form_h2(t): return re.sub(r'^\d\.(\d) ', lambda m: KA[int(m.group(1)) - 1] + '. ', t)            # 2.1 제목 -> 가. 제목
def form_h3(t): return re.sub(r'^\d\.\d\.(\d+) ', lambda m: m.group(1) + ') ', t)                    # 2.1.3 제목 -> 3) 제목
def form_h4(t): return re.sub(r'^([가-하])\. ', r'\1) ', t)                                            # 가. 제목 -> 가) 제목
def form_h5(t): return re.sub(r'^\((\d+)\) ', lambda m: CIRC[int(m.group(1)) - 1] + ' ', t)            # (1) 제목 -> ① 제목


def form_refs(t):
    """본문의 절 참조를 양식의 번호로 바꾼다: 3.2.4 -> 3장 나절 4), 3.2절 -> 3장 나절."""
    t = re.sub(r'(?<![\w.\-])([1-7])\.(\d)\.(\d{1,2})(?![\d.])', lambda m: '%s장 %s절 %s)' % (m.group(1), KA[int(m.group(2)) - 1], m.group(3)), t)
    return re.sub(r'(?<![\w.\-])([1-7])\.(\d)절', lambda m: '%s장 %s절' % (m.group(1), KA[int(m.group(2)) - 1]), t)


# 표 칸의 테두리 번호(템플릿 예시 표에서 읽은 값): 머리줄·가운데 줄·마지막 줄 × 왼쪽·가운데·오른쪽 칸
_BF = {}


def _load_borderfills(table_xml):
    cells = table_xml.split('<hp:tc ')[1:]
    grid = {}
    for c in cells:
        bf = int(re.search(r'borderFillIDRef="(\d+)"', c).group(1))
        m = re.search(r'colAddr="(\d+)" rowAddr="(\d+)"', c)
        grid[(int(m.group(2)), int(m.group(1)))] = bf
    nr = max(r for r, _ in grid) + 1; nc = max(c for _, c in grid) + 1
    for name, r in (('head', 0), ('body', 1), ('last', nr - 1)):
        _BF[name] = (grid[(r, 0)], grid[(r, 1)], grid[(r, nc - 1)])


def _cell(text, r, c, w, kind, pos, align, header, colspan=1, rowspan=1):
    bf = _BF[kind][pos]
    para, style, char = (44, 45, 27) if header else ((44, 46, 20) if align == 'c' else (45, 47, 20))
    paras = ''.join('<hp:p id="0" paraPrIDRef="%d" styleIDRef="%d" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="%d"><hp:t>%s</hp:t></hp:run></hp:p>'
                    % (para, style, char, escape(t)) for t in str(text).split('\n'))
    return ('<hp:tc name="" header="%d" hasMargin="0" protect="0" editable="0" dirty="0" borderFillIDRef="%d">'
            '<hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">%s</hp:subList>'
            '<hp:cellAddr colAddr="%d" rowAddr="%d"/><hp:cellSpan colSpan="%d" rowSpan="%d"/><hp:cellSz width="%d" height="1700"/><hp:cellMargin left="510" right="510" top="141" bottom="141"/></hp:tc>'
            % (1 if header else 0, bf, paras, c, r, colspan, rowspan, w))


def _em(word):
    """낱말의 너비(글자 수 기준, 한글·전각은 1, 영문·숫자·기호는 0.55)."""
    return sum(1.0 if ord(c) > 0x2E7F or c in '①②③④⑤⑥⑦⑧⑨⑩·' else 0.55 for c in word)


def _fit_widths(ws, rows, size=1000, pad=1020 + 160):
    """낱말이 칸 안에서 글자 단위로 끊기지 않도록 열 너비를 고친다.
    머리줄은 모든 낱말이, 내용 칸은 6글자 이하의 낱말이 한 줄에 들어가는 너비를 최소로 하고, 모자라는 만큼은 여유가 있는 열에서 줄인다."""
    n = len(ws); need = [0] * n
    for r, row in enumerate(rows):
        for c, v in enumerate(row):
            for w in re.split(r'[\s]+', str(v)):
                e = _em(w)
                if r == 0 or e <= 6:
                    need[c] = max(need[c], int(e * size * 1.06) + pad)
    if sum(need) > sum(ws):                                   # 다 넣을 수 없으면 비율대로 줄인다
        need = [int(x * sum(ws) / sum(need)) for x in need]
    for _ in range(10):
        short = sum(max(0, need[c] - ws[c]) for c in range(n))
        if short <= 0: break
        spare = [max(0, ws[c] - need[c]) for c in range(n)]
        tot = sum(spare)
        if tot <= 0: break
        ws = [max(ws[c], need[c]) - int(round(spare[c] * short / tot)) for c in range(n)]
    return ws


def table(caption, rows, widths, align=None, unit=None, note=None):
    """표 제목, (단위), 표, (주·자료) 문단의 목록을 돌려준다. rows[0]은 머리줄. widths는 비율. align은 열마다 'c'(가운데)나 'l'(왼쪽)."""
    n = len(rows[0])
    assert all(len(r) == n for r in rows), [len(r) for r in rows]
    tot = float(sum(widths)); ws = [int(round(w * WIDTH / tot)) for w in widths]
    ws = _fit_widths(ws, rows); ws[-1] += WIDTH - sum(ws)
    align = align or (['c'] + ['l'] * (n - 1))
    trs = ''
    for r, row in enumerate(rows):
        kind = 'head' if r == 0 else ('last' if r == len(rows) - 1 else 'body')
        tcs = ''.join(_cell(v, r, c, ws[c], kind, 0 if c == 0 else (2 if c == n - 1 else 1), align[c], r == 0) for c, v in enumerate(row))
        trs += '<hp:tr>%s</hp:tr>' % tcs
    tbl = ('<hp:p id="0" paraPrIDRef="49" styleIDRef="51" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="20">'
           '<hp:tbl id="%d" zOrder="%d" numberingType="TABLE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" pageBreak="TABLE" repeatHeader="1" rowCnt="%d" colCnt="%d" cellSpacing="0" borderFillIDRef="4" noAdjust="0">'
           '<hp:sz width="%d" widthRelTo="ABSOLUTE" height="%d" heightRelTo="ABSOLUTE" protect="0"/>'
           '<hp:pos treatAsChar="0" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="COLUMN" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>'
           '<hp:outMargin left="0" right="0" top="0" bottom="0"/><hp:inMargin left="510" right="510" top="141" bottom="141"/>%s</hp:tbl><hp:t/></hp:run></hp:p>'
           % (nid(), nid() % 1000, len(rows), n, WIDTH, 1700 * len(rows), trs))
    out = [TCAP(caption)]
    if unit: out.append(UNIT(unit))
    out.append(tbl)
    out.append(BLANK())
    return out


def _top_paragraphs(x):
    ps, depth, start = [], 0, None
    for m in re.finditer(r'<hp:p |</hp:p>', x):
        if m.group(0) == '<hp:p ':
            if depth == 0: start = m.start()
            depth += 1
        else:
            depth -= 1
            if depth == 0: ps.append((start, m.end()))
    return ps


def text_of(p):
    p = re.sub(r'<hp:fieldBegin.*?</hp:fieldBegin>', '', p, flags=re.S)        # 메모 내용은 본문 글이 아니다
    return re.sub(r'<[^>]+>', '', p).strip()


class Report:
    def __init__(self, template=TEMPLATE, drop_guide=True):
        self.z = zipfile.ZipFile(template)
        sec = self.z.read('Contents/section0.xml').decode('utf8')
        sp = _top_paragraphs(sec)
        self.head, self.tail = sec[:sp[0][0]], sec[sp[-1][1]:]
        self.ps = [sec[a:b] for a, b in sp]
        ex = [p for p in self.ps if '<hp:tbl' in p and '사례 수' in p]
        _load_borderfills(ex[0])
        if drop_guide:                       # [작성 안내]부터 '목 차' 앞까지(안내와 예시)를 뺀다
            a = self._find('[작성 안내]'); b = self.toc_start()
            self.ps = self.ps[:a] + self.ps[b:]
        self.stats = {}

    def _find(self, starts, after=0):
        hit = [i for i, p in enumerate(self.ps) if i >= after and text_of(p).startswith(starts)]
        assert hit, starts
        return hit[0]

    def _style(self, i):
        return int(re.search(r'styleIDRef="(\d+)"', self.ps[i]).group(1))

    def body_start(self):
        """목차 뒤에서 본문이 시작하는 문단(1. 서론)의 위치."""
        return [k for k in range(self.toc_start() + 1, len(self.ps)) if self._style(k) == 34 and re.match(r'\d+\.', text_of(self.ps[k]))][0]

    def toc_start(self):
        return [k for k, p in enumerate(self.ps) if nospace(p) == '목차' and 'paraPrIDRef="55"' in p][0]

    def rebuild_toc(self):
        """본문의 장·절·소절 제목과 표·그림 제목으로 목차, 표 목차, 그림 목차를 다시 만든다(쪽 번호는 한글에서 넣는다)."""
        toc, bs = self.toc_start(), self.body_start()
        ent, tabs, figs, first = [], [], [], True
        for k in range(bs, len(self.ps)):
            st, t = self._style(k), text_of(self.ps[k])
            if not t: continue
            if st == 34:
                if not first: ent.append(TBLANK())
                ent.append(TOCC(t)); first = False
            elif st == 35: ent.append(TOCE(' ' + t))
            elif st == 43: tabs.append(LISTE(t))
            elif st == 44: figs.append(LISTE(t))
        front = [TBLANK(), PAGELINE(), TOCE('목    차'), TOCE('표 목 차'), TOCE('그림목차'), TBLANK(), PAGELINE(), TBLANK()]
        back = [TBLANK(), TOCE('참고문헌')]
        self.ps = (self.ps[:toc + 1] + front + ent + back + [TITLE('표 목 차'), TBLANK()] + (tabs or [TBLANK()])
                   + [TITLE('그 림 목 차'), TBLANK()] + (figs or [TBLANK()]) + self.ps[bs:])
        return len(ent), len(tabs), len(figs)

    def fill(self, heading, items, chapter=None):
        """본문에서 제목이 heading인 절 아래의 빈 문단을 items로 바꾼다."""
        start = self.body_start()
        if chapter:                                      # 같은 제목의 절(라. 최종 산출물)이 장마다 있으므로 그 장 안에서 찾는다
            start = [k for k in range(start, len(self.ps)) if self._style(k) == 34 and text_of(self.ps[k]).startswith(chapter + '.')][0]
        i = [k for k in range(start, len(self.ps)) if self._style(k) == 35 and text_of(self.ps[k]) == heading][0]
        j = i + 1
        while j < len(self.ps) and text_of(self.ps[j]) == '' and '<hp:tbl' not in self.ps[j] and '<hp:pic' not in self.ps[j]:
            j += 1
        self.ps = self.ps[:i + 1] + list(items) + self.ps[j:]
        self.stats[heading] = sum(len(text_of(x)) for x in items)

    def _lines(self, p):
        """문단 하나가 차지하는 줄 수의 어림값(쪽 나눔 판단용)."""
        if '<hp:pic' in p:
            m = re.search(r'<hp:sz width="\d+"[^>]*height="(\d+)"', p)
            return (int(m.group(1)) if m else 20000) / 1900.0 + 1
        if '<hp:tbl' in p:
            rows = len(re.findall(r'<hp:tr>', p)) or 1
            return max(rows * 1.3, len(text_of(p)) / 42.0 * 1.5) + 1
        return max(1, -(-len(text_of(p)) // 42))

    def page_breaks(self, min_lines=70, verbose=False):
        """절(가. 나.)은 새 쪽에서 시작한다. 그 아래 꼭지(1) 2))는 분량이 두 쪽 안팎 이상일 때만 새 쪽에서 시작한다.
        장 제목 바로 아래의 절, 절 제목 바로 아래의 꼭지, 내용이 없는 절은 그대로 둔다."""
        bs = self.body_start()
        heads = [k for k in range(bs, len(self.ps)) if self._style(k) in (34, 35, 36) and text_of(self.ps[k])]
        done = []
        for n, k in enumerate(heads):
            st = self._style(k)
            if st == 34 or text_of(self.ps[k]).replace(' ', '') == '참고문헌':
                continue
            prev = [j for j in range(k - 1, bs - 1, -1) if text_of(self.ps[j]) or '<hp:tbl' in self.ps[j] or '<hp:pic' in self.ps[j]]
            if prev and self._style(prev[0]) in (34, 35) and '<hp:tbl' not in self.ps[prev[0]]:
                continue                                  # 윗 제목 바로 아래이면 붙여 둔다
            end = next((h for h in heads[n + 1:] if self._style(h) <= st), len(self.ps))
            size = sum(self._lines(p) for p in self.ps[k + 1:end])
            if (st == 35 and size >= 3) or (st == 36 and size >= min_lines):
                self.ps[k] = self.ps[k].replace('pageBreak="0"', 'pageBreak="1"', 1)
                done.append((text_of(self.ps[k]), round(size / 35.0, 1)))
            elif verbose and st == 36:
                done.append(('  (붙임) ' + text_of(self.ps[k]), round(size / 35.0, 1)))
        return done

    def references(self, refs):
        i = [k for k in range(self.body_start(), len(self.ps)) if nospace(self.ps[k]) == '참고문헌' and 'paraPrIDRef="55"' in self.ps[k]][0]
        j = i + 1
        j = len(self.ps)                                  # 참고문헌이 마지막이다(부록 없음)
        self.ps = self.ps[:i + 1] + [REF('%d. %s' % (k + 1, r)) for k, r in enumerate(refs)] + self.ps[j:]

    def keep_only(self, chapter):
        """본문에서 한 장만 남긴다(나누어 검토할 때). chapter는 장 번호 문자열."""
        bs = self.body_start()
        h1 = [k for k in range(bs, len(self.ps)) if self._style(k) == 34]
        ref = [k for k in range(bs, len(self.ps)) if nospace(self.ps[k]) == '참고문헌' and 'paraPrIDRef="55"' in self.ps[k]][0]
        a = [k for k in h1 if text_of(self.ps[k]).startswith(chapter + '.')][0]
        b = min([k for k in h1 if k > a] + [ref])
        self.ps = self.ps[:bs] + self.ps[a:b] + self.ps[ref:]

    def set_cover(self, date_text):
        i = self._find('(작성 템플릿)'); self.ps[i] = self.ps[i].replace('(작성 템플릿)', '')
        i = self._find('20  .   .'); self.ps[i] = self.ps[i].replace('20  .   .', date_text)

    def save(self, out):
        body = self.head + ''.join(re.sub(r'<hp:linesegarray>.*?</hp:linesegarray>', '', p, flags=re.S) if '<hp:tbl' not in p and '<hp:pic' not in p else p for p in self.ps) + self.tail
        xml.dom.minidom.parseString(body.encode('utf8'))
        with zipfile.ZipFile(out, 'w') as zo:
            zo.writestr(zipfile.ZipInfo('mimetype'), self.z.read('mimetype'), compress_type=zipfile.ZIP_STORED)
            for it in self.z.infolist():
                n = it.filename
                if n in ('mimetype', 'Preview/PrvImage.png'):
                    continue
                data = body.encode('utf8') if n == 'Contents/section0.xml' else self.z.read(n)
                if n == 'Contents/content.hpf' and PICS:      # 넣은 그림을 manifest에 등록
                    items = ''.join('<opf:item id="%s" href="BinData/%s.png" media-type="image/png" isEmbeded="1"/>' % (b, b) for b, _ in PICS)
                    data = data.decode('utf8').replace('</opf:manifest>', items + '</opf:manifest>').encode('utf8')
                zo.writestr(n, data, compress_type=zipfile.ZIP_DEFLATED)
            for b, path in PICS:
                zo.write(path, 'BinData/%s.png' % b, compress_type=zipfile.ZIP_DEFLATED)
        return body
