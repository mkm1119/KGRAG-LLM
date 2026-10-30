#!/usr/bin/env python3
"""랩미팅·회의 자료(docx) 공통 부품. 10/09 자료(docx)를 서식 템플릿으로 읽어 같은 서식의 문단·표를 만든다. stdlib만 사용."""
import html, re, zipfile

ROOT_TMPL = None
LANG = '<w:lang w:eastAsia="ko-KR"/>'
esc = lambda s: html.escape(s, quote=False)
BODY, TBL = 20, 18
W = 9972


class Template:
    def __init__(self, path):
        self.z = zipfile.ZipFile(path)
        x = self.z.read('word/document.xml').decode('utf8')
        b = x[x.index('<w:body>') + 8:x.index('</w:body>')]
        self.top = re.findall(r'<w:p[ >].*?</w:p>|<w:tbl>.*?</w:tbl>', b, flags=re.S)
        self.sect = re.findall(r'<w:sectPr.*?</w:sectPr>', b, flags=re.S)[-1]
        self.open = x[:x.index('<w:body>') + 8]

    @staticmethod
    def text(p):
        return html.unescape(''.join(re.findall(r'<w:t(?:\s[^>]*)?>(.*?)</w:t>', p, flags=re.S)))

    def rows(self, i):
        out = []
        for tr in re.findall(r'<w:tr[ >].*?</w:tr>', self.top[i], flags=re.S):
            out.append(['\n'.join(t for t in (self.text(p) for p in re.findall(r'<w:p[ >].*?</w:p>', tc, flags=re.S)) if t) for tc in re.findall(r'<w:tc>.*?</w:tc>', tr, flags=re.S)])
        return out

    def widths(self, i):
        return [int(v) for v in re.findall(r'<w:gridCol w:w="(\d+)"', self.top[i])]

    def save(self, out, body_xml, images=None, page_numbers=False):
        import xml.dom.minidom
        doc = self.open + body_xml + self.sect + '</w:body></w:document>'
        xml.dom.minidom.parseString(doc.encode('utf8'))
        images = images or {}
        rels = self.z.read('word/_rels/document.xml.rels').decode('utf8')
        ct = self.z.read('[Content_Types].xml').decode('utf8')
        for key, (rid, path) in images.items():
            rels = rels.replace('</Relationships>', '<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/%s.png"/></Relationships>' % (rid, key))
        if images and 'Extension="png"' not in ct:
            ct = ct.replace('<Default Extension="xml"', '<Default Extension="png" ContentType="image/png"/><Default Extension="xml"')
        with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zo:
            for item in self.z.infolist():
                data = self.z.read(item.filename)
                if item.filename == 'word/document.xml':
                    data = doc.encode('utf8')
                elif item.filename == 'word/_rels/document.xml.rels':
                    data = rels.encode('utf8')
                elif item.filename == '[Content_Types].xml':
                    data = ct.encode('utf8')
                elif page_numbers and item.filename.startswith('word/footer'):
                    data = add_page_number(data.decode('utf8')).encode('utf8')
                zo.writestr(item, data)
            for key, (rid, path) in images.items():
                zo.write(path, 'word/media/%s.png' % key)


def add_page_number(ftr):
    """바닥글 마지막 문단을 가운데 정렬된 '쪽 / 전체쪽' 필드로 바꾼다."""
    rpr = '<w:rPr><w:color w:val="787878"/><w:sz w:val="16"/>%s</w:rPr>' % LANG
    fld = lambda instr: '<w:fldSimple w:instr=" %s "><w:r>%s<w:t>1</w:t></w:r></w:fldSimple>' % (instr, rpr)
    add = '%s<w:r>%s<w:t xml:space="preserve"> / </w:t></w:r>%s' % (fld('PAGE'), rpr, fld('NUMPAGES'))
    i = ftr.rindex('</w:p>')
    j = ftr.rindex('<w:p', 0, i)
    k = ftr.index('</w:pPr>', j) + len('</w:pPr>') if '</w:pPr>' in ftr[j:i] else ftr.index('>', j) + 1
    return ftr[:k] + add + ftr[i:]  # 바닥글 글자는 지우고 가운데에 "쪽 / 전체 쪽"만


def run(text, sz=None, b=False, color=None, mono=False):
    pr = ('<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:cs="Consolas" w:eastAsia="맑은 고딕"/>' if mono else '') + ('<w:b/>' if b else '') + ('<w:color w:val="%s"/>' % color if color else '') + ('<w:sz w:val="%d"/><w:szCs w:val="%d"/>' % (sz, sz) if sz else '') + LANG
    return '<w:r><w:rPr>%s</w:rPr><w:t xml:space="preserve">%s</w:t></w:r>' % (pr, esc(text))


def title(t1, t2):
    return ('<w:p><w:pPr><w:spacing w:before="1000"/><w:jc w:val="center"/><w:rPr>%s</w:rPr></w:pPr><w:r><w:rPr><w:b/><w:color w:val="1F4E79"/><w:sz w:val="44"/>%s</w:rPr>'
            '<w:t xml:space="preserve">%s</w:t><w:br/><w:t xml:space="preserve">%s</w:t></w:r></w:p>' % (LANG, LANG, esc(t1), esc(t2)))


def subtitle(t):
    return '<w:p><w:pPr><w:jc w:val="center"/><w:rPr>%s</w:rPr></w:pPr>%s</w:p>' % (LANG, run(t, sz=23, b=True, color='505050'))


def dateline(t, before=400):
    return '<w:p><w:pPr><w:spacing w:before="%d"/><w:jc w:val="center"/><w:rPr>%s</w:rPr></w:pPr>%s</w:p>' % (before, LANG, run(t, color='646464'))


def label(t):
    return '<w:p><w:pPr><w:keepNext/><w:spacing w:before="240"/><w:rPr>%s</w:rPr></w:pPr>%s</w:p>' % (LANG, run(t, sz=25, b=True, color='1F4E79'))


def h1(t, pagebreak=True):
    return '<w:p><w:pPr><w:pStyle w:val="1"/>%s<w:rPr>%s</w:rPr></w:pPr>%s</w:p>' % ('<w:pageBreakBefore/>' if pagebreak else '', LANG, run(t))


def h2(t):
    return '<w:p><w:pPr><w:pStyle w:val="21"/><w:rPr>%s</w:rPr></w:pPr>%s</w:p>' % (LANG, run(t))


def para(t, sz=BODY):
    return '<w:p><w:pPr><w:spacing w:before="60" w:after="120"/><w:rPr>%s</w:rPr></w:pPr>%s</w:p>' % (LANG, run(t, sz=sz))



def para_runs(parts, sz=BODY):
    """굵기가 섞인 문단: parts = [(글자, 굵게 여부), ...]"""
    return '<w:p><w:pPr><w:spacing w:before="40" w:after="120"/><w:rPr>%s</w:rPr></w:pPr>%s</w:p>' % (LANG, ''.join(run(t, sz=sz, b=b, color='1F4E79' if b else None) for t, b in parts))


def li(t, sz=BODY):
    return '<w:p><w:pPr><w:pStyle w:val="a0"/><w:spacing w:after="60"/><w:rPr>%s</w:rPr></w:pPr>%s</w:p>' % (LANG, run(t, sz=sz))


def lead(head, text):
    return '<w:p><w:pPr><w:spacing w:before="60" w:after="100"/><w:rPr>%s</w:rPr></w:pPr>%s%s</w:p>' % (LANG, run(head + '  ', sz=BODY, b=True, color='1F4E79'), run(text, sz=BODY))


def spacer():
    return '<w:p><w:pPr><w:spacing w:after="60"/><w:rPr>%s</w:rPr></w:pPr></w:p>' % LANG


BORD = ''.join('<w:%s w:val="single" w:sz="5" w:space="0" w:color="A6A6A6"/>' % s for s in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'))
MAR = '<w:tcMar><w:top w:w="80" w:type="dxa"/><w:left w:w="110" w:type="dxa"/><w:bottom w:w="80" w:type="dxa"/><w:right w:w="110" w:type="dxa"/></w:tcMar><w:vAlign w:val="center"/>'


def cell(text, w, fill=None, b=False, color=None, center=False, sz=TBL, mono=False, left=False):
    lines = str(text).split('\n') or ['']
    ps = ''.join('<w:p><w:pPr><w:spacing w:after="20" w:line="252" w:lineRule="auto"/>%s</w:pPr>%s</w:p>' % ('<w:jc w:val="center"/>' if center else '', run(l, sz=sz, b=b, color=color, mono=mono)) for l in lines)
    return '<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/>%s%s</w:tcPr>%s</w:tc>' % (w, '<w:shd w:val="clear" w:color="auto" w:fill="%s"/>' % fill if fill else '', MAR, ps)


def table(rows, widths, header=True, firstcol=True, sz=TBL, left_cols=()):
    assert sum(widths) == W, (sum(widths), rows[0])
    out = ['<w:tbl><w:tblPr><w:tblW w:w="%d" w:type="dxa"/><w:jc w:val="center"/><w:tblBorders>%s</w:tblBorders><w:tblLayout w:type="fixed"/>'
           '<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/></w:tblPr><w:tblGrid>%s</w:tblGrid>'
           % (W, BORD, ''.join('<w:gridCol w:w="%d"/>' % w for w in widths))]
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


def box(lab, text, w1=1944, sz=TBL):
    return table([[lab, text]], [w1, W - w1], header=False, sz=sz)


def code(text, sz=17):
    """고정폭 글자 상자(질의문, 근거 묶음 등)."""
    out = ['<w:tbl><w:tblPr><w:tblW w:w="%d" w:type="dxa"/><w:jc w:val="center"/><w:tblBorders>%s</w:tblBorders><w:tblLayout w:type="fixed"/></w:tblPr><w:tblGrid><w:gridCol w:w="%d"/></w:tblGrid><w:tr><w:trPr><w:jc w:val="center"/></w:trPr>' % (W, BORD, W)]
    out.append(cell(text, W, fill='F7F7F7', sz=sz, mono=True))
    out.append('</w:tr></w:tbl>')
    return ''.join(out) + spacer()


def flow(items, sz=TBL):
    n = len(items); aw = 300
    bw = (W - aw * (n - 1)) // n
    ws = []
    for i in range(n):
        ws.append(bw)
        if i < n - 1:
            ws.append(aw)
    ws[-1] += W - sum(ws)
    out = ['<w:tbl><w:tblPr><w:tblW w:w="%d" w:type="dxa"/><w:jc w:val="center"/><w:tblLayout w:type="fixed"/></w:tblPr><w:tblGrid>%s</w:tblGrid><w:tr><w:trPr><w:cantSplit/></w:trPr>' % (W, ''.join('<w:gridCol w:w="%d"/>' % w for w in ws))]
    k = 0
    for i, t in enumerate(items):
        out.append(cell(t, ws[k], fill='EEF5FA', center=True, sz=sz)); k += 1
        if i < n - 1:
            out.append(cell('→', ws[k], center=True, sz=sz)); k += 1
    out.append('</w:tr></w:tbl>')
    return ''.join(out) + spacer()


IMGS = {}


def image(key, path, px_w, px_h, name, width=W):
    rid = 'rIdImg%d' % (len(IMGS) + 1)
    IMGS[key] = (rid, path)
    cx = width * 635
    cy = int(cx * px_h / px_w)
    n = len(IMGS)
    return ('<w:p><w:pPr><w:keepNext/><w:spacing w:before="60" w:after="40"/><w:jc w:val="center"/></w:pPr><w:r><w:drawing>'
            '<wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="%d" cy="%d"/><wp:docPr id="%d" name="%s" descr="%s"/>'
            '<wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/></wp:cNvGraphicFramePr>'
            '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="%d" name="%s"/><pic:cNvPicPr/></pic:nvPicPr>'
            '<pic:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
            '</a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>') % (cx, cy, n, name, esc(name), n, name, rid, cx, cy)


def caption(t):
    return '<w:p><w:pPr><w:spacing w:before="0" w:after="120"/><w:jc w:val="center"/><w:rPr>%s</w:rPr></w:pPr>%s</w:p>' % (LANG, run(t, sz=18, color='505050'))
