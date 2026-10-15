#!/usr/bin/env python3
"""회의록을 한글 문서(.hwpx)로 만든다. 한글(Hancom)에서 만든 월간 공정보고 hwpx의 header(글꼴·문단·테두리 서식)와 쪽 설정을 그대로 쓰고, 본문(section0)만 회의록 내용으로 바꾼다.
내용은 build_minutes_1015.py가 저장한 lab_meeting/minutes_blocks.json. 사용: python3 build_minutes_hwpx.py <기준.hwpx> <출력.hwpx>
주의: 이 환경에는 한글 프로그램이 없어 열어 보며 확인하지 못했다(구조는 기준 파일과 같은 형식으로 작성)."""
import json, os, re, sys, zipfile
from xml.sax.saxutils import escape
HERE = os.path.dirname(os.path.abspath(__file__))
BASE, OUT = sys.argv[1], sys.argv[2]
blocks = json.load(open(os.path.join(HERE, '..', '..', 'lab_meeting', 'minutes_blocks.json'), encoding='utf-8'))
z = zipfile.ZipFile(BASE)
sec = z.read('Contents/section0.xml').decode('utf8')
W = 42520   # 본문 폭(기준 파일의 쪽 설정)

# 기준 파일의 첫 문단(쪽 설정 secPr 포함)을 그대로 쓰되, 글자 내용은 비운다
head = sec[:sec.index('<hp:p ')]
first_end = sec.index('</hp:p>') + len('</hp:p>')
first = sec[sec.index('<hp:p '):first_end]
assert '<hp:secPr' in first
first = re.sub(r'<hp:t>.*?</hp:t>', '', first, flags=re.S)
first = re.sub(r'<hp:linesegarray>.*?</hp:linesegarray>', '', first, flags=re.S)
_id = [900000000]


def nid():
    _id[0] += 1
    return _id[0]


def p(text, para, char, style=0, tail=''):
    return ('<hp:p id="2147483648" paraPrIDRef="%d" styleIDRef="%d" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="%d"><hp:t>%s</hp:t></hp:run></hp:p>'
            % (para, style, char, escape(text)))


def empty(para=20, char=38):
    return '<hp:p id="2147483648" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="%d"/></hp:p>' % (para, char)


def lines_est(text, width, size_pt=11):
    cap = max(4, int(width / 100.0 / (size_pt * 0.55)))
    return max(1, sum(max(1, -(-len(t) // cap)) for t in text.split('\n')))


def cell(col, row, width, height, text, header=False, bf=4):
    fill = 13 if header else bf        # 머리글 칸은 기준 파일의 색 있는 테두리 서식, 본문 칸은 실선
    ps = ''.join(p(t, 32 if header else 35, 24 if header else 65) for t in (text.split('\n') or ['']))
    return ('<hp:tc name="" header="%d" hasMargin="0" protect="0" editable="0" dirty="0" borderFillIDRef="%d"><hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">%s</hp:subList>'
            '<hp:cellAddr colAddr="%d" rowAddr="%d"/><hp:cellSpan colSpan="1" rowSpan="1"/><hp:cellSz width="%d" height="%d"/><hp:cellMargin left="141" right="141" top="141" bottom="141"/></hp:tc>'
            % (1 if header else 0, fill, ps, col, row, width, height))


def tbl(rows, widths, header=True):
    tot = sum(widths)
    ws = [int(round(w * W / tot)) for w in widths]
    ws[-1] += W - sum(ws)
    trs, total_h = [], 0
    for ri, r in enumerate(rows):
        nl = max(lines_est(t, ws[ci] - 400) for ci, t in enumerate(r))
        h = 600 + nl * 1500
        total_h += h
        tcs = ''.join(cell(ci, ri, ws[ci], h, t, header=(header and ri == 0)) for ci, t in enumerate(r))
        trs.append('<hp:tr>%s</hp:tr>' % tcs)
    body = ('<hp:tbl id="%d" zOrder="0" numberingType="NONE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" pageBreak="CELL" repeatHeader="1" rowCnt="%d" colCnt="%d" cellSpacing="0" borderFillIDRef="4" noAdjust="0">'
            '<hp:sz width="%d" widthRelTo="ABSOLUTE" height="%d" heightRelTo="ABSOLUTE" protect="0"/><hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="PARA" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>'
            '<hp:outMargin left="0" right="0" top="0" bottom="0"/><hp:inMargin left="141" right="141" top="141" bottom="141"/>%s</hp:tbl>' % (nid(), len(rows), len(rows[0]), W, total_h, ''.join(trs)))
    return '<hp:p id="2147483648" paraPrIDRef="20" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="38">%s<hp:t/></hp:run></hp:p>' % body


out = [first]
for blk in blocks:
    k = blk[0]
    if k == 'title':
        out.append(empty()); out.append(p(blk[1], 20, 15)); out.append(empty())
    elif k == 'h':
        out.append(empty()); out.append(p(blk[1], 28, 41))
    elif k == 'sub':
        out.append(p(' □ ' + blk[1], 28, 42, 3))
    elif k == 'b':
        out.append(p('  ◦ ' + blk[1], 29, 42))
    elif k == 'tbl':
        out.append(tbl(blk[1], blk[2], blk[3])); out.append(empty())
body = head + ''.join(out) + '</hs:sec>'
import xml.dom.minidom
xml.dom.minidom.parseString(body.encode('utf8'))
text = '\n'.join(b[1] if b[0] != 'tbl' else '\n'.join(' | '.join(r) for r in b[1]) for b in blocks)
cpf = z.read('Contents/content.hpf').decode('utf8')
cpf = re.sub(r'<opf:title>.*?</opf:title>', '<opf:title>%s</opf:title>' % escape(blocks[0][1]), cpf, count=1)
with zipfile.ZipFile(OUT, 'w') as zo:
    zo.writestr(zipfile.ZipInfo('mimetype'), z.read('mimetype'), compress_type=zipfile.ZIP_STORED)
    for it in z.infolist():
        n = it.filename
        if n == 'mimetype':
            continue
        if n == 'Contents/section0.xml':
            data = body.encode('utf8')
        elif n == 'Preview/PrvText.txt':
            data = text.encode('utf8')
        elif n == 'Contents/content.hpf':
            data = cpf.encode('utf8')
        elif n == 'Preview/PrvImage.png':
            continue
        else:
            data = z.read(n)
        zo.writestr(n, data, compress_type=zipfile.ZIP_DEFLATED)
print('저장', OUT, len(blocks))
