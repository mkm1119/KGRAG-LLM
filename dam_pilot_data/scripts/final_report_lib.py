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
WIDTH = 42520                      # 본문 폭(템플릿 표의 폭)
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


def table(caption, rows, widths, align=None, unit=None, note=None):
    """표 제목, (단위), 표, (주·자료) 문단의 목록을 돌려준다. rows[0]은 머리줄. widths는 비율. align은 열마다 'c'(가운데)나 'l'(왼쪽)."""
    n = len(rows[0])
    assert all(len(r) == n for r in rows), [len(r) for r in rows]
    tot = float(sum(widths)); ws = [int(round(w * WIDTH / tot)) for w in widths]; ws[-1] += WIDTH - sum(ws)
    align = align or (['c'] + ['l'] * (n - 1))
    trs = ''
    for r, row in enumerate(rows):
        kind = 'head' if r == 0 else ('last' if r == len(rows) - 1 else 'body')
        tcs = ''.join(_cell(v, r, c, ws[c], kind, 0 if c == 0 else (2 if c == n - 1 else 1), align[c], r == 0) for c, v in enumerate(row))
        trs += '<hp:tr>%s</hp:tr>' % tcs
    tbl = ('<hp:p id="0" paraPrIDRef="49" styleIDRef="51" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="20">'
           '<hp:tbl id="%d" zOrder="%d" numberingType="TABLE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" pageBreak="CELL" repeatHeader="1" rowCnt="%d" colCnt="%d" cellSpacing="0" borderFillIDRef="4" noAdjust="0">'
           '<hp:sz width="%d" widthRelTo="ABSOLUTE" height="%d" heightRelTo="ABSOLUTE" protect="0"/>'
           '<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="PARA" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>'
           '<hp:outMargin left="0" right="0" top="0" bottom="0"/><hp:inMargin left="510" right="510" top="141" bottom="141"/>%s</hp:tbl><hp:t/></hp:run></hp:p>'
           % (nid(), nid() % 1000, len(rows), n, WIDTH, 1700 * len(rows), trs))
    out = [TCAP(caption)]
    if unit: out.append(UNIT(unit))
    out.append(tbl)
    if note: out.append(NOTE(note))
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
            a = self._find('[작성 안내]'); b = self._find('목    차')
            self.ps = self.ps[:a] + self.ps[b:]
        self.stats = {}

    def _find(self, starts, after=0):
        hit = [i for i, p in enumerate(self.ps) if i >= after and text_of(p).startswith(starts)]
        assert hit, starts
        return hit[0]

    def fill(self, heading, items):
        """본문에서 제목이 heading인 절 아래의 빈 문단을 items로 바꾼다."""
        toc = self._find('목    차')
        first_body = self._find('1. 국내외 기술 트렌드 조사', toc + 2)      # 목차 뒤의 본문 시작
        i = self._find(heading, first_body)
        j = i + 1
        while j < len(self.ps) and text_of(self.ps[j]) == '' and '<hp:tbl' not in self.ps[j] and '<hp:pic' not in self.ps[j]:
            j += 1
        self.ps = self.ps[:i + 1] + list(items) + self.ps[j:]
        self.stats[heading] = sum(len(text_of(x)) for x in items)

    def references(self, refs):
        i = self._find('참고문헌', self._find('5. 연구개발 추진 방향', self._find('목    차') + 20))
        j = i + 1
        while j < len(self.ps) and not text_of(self.ps[j]).startswith('부록'):
            j += 1
        self.ps = self.ps[:i + 1] + [REF('%d. %s' % (k + 1, r)) for k, r in enumerate(refs)] + self.ps[j:]

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
                zo.writestr(n, body.encode('utf8') if n == 'Contents/section0.xml' else self.z.read(n), compress_type=zipfile.ZIP_DEFLATED)
        return body
