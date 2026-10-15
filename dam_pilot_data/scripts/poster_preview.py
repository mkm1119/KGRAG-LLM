#!/usr/bin/env python3
"""포스터 pptx의 슬라이드를 HTML로 그려 PNG로 저장하는 미리보기(LibreOffice를 쓸 수 없을 때). 템플릿의 머리띠·패널과 build_poster.py가 만든 도형을 지원한다.
사용: NODE_PATH=/opt/node22/lib/node_modules python3 scripts/poster_preview.py <포스터.pptx> <출력.png> [px당EMU=8000]
"""
import base64, html, os, re, subprocess, sys, zipfile

def main(pptx, out, k=8000, zoom=1.0):
    z = zipfile.ZipFile(pptx)
    s = z.read('ppt/slides/slide1.xml').decode('utf8')
    rels = dict(re.findall(r'Id="(rId\d+)"[^>]*?Target="\.\./media/([^"]+)"', z.read('ppt/slides/_rels/slide1.xml.rels').decode('utf8')))
    rels.update({a: b for b, a in re.findall(r'Target="\.\./media/([^"]+)"[^>]*?Id="(rId\d+)"', z.read('ppt/slides/_rels/slide1.xml.rels').decode('utf8'))})
    W, H = [int(v) for v in re.search(r'<p:sldSz cx="(\d+)" cy="(\d+)"', z.read('ppt/presentation.xml').decode('utf8')).groups()]
    px = lambda v: v / k
    def uri(name):
        d = z.read('ppt/media/' + name)
        return 'data:image/%s;base64,%s' % ('jpeg' if name.endswith('jpg') else 'png', base64.b64encode(d).decode())

    def clr(b):
        m = re.search(r'<a:srgbClr val="(\w+)"', b)
        if m: return '#' + m.group(1)
        if 'schemeClr val="bg1"' in b: return '#fff'
        if 'schemeClr val="tx1"' in b: return '#262626'
        return '#262626'

    def paras_html(body):
        out = []
        for p in re.findall(r'<a:p>(.*?)</a:p>', body, flags=re.S):
            algn = re.search(r'<a:pPr[^>]*algn="(\w+)"', p)
            marL = re.search(r'<a:pPr[^>]*marL="(\d+)"', p)
            bu = '<a:buBlip>' in p
            aft = re.search(r'<a:spcAft><a:spcPts val="(\d+)"', p)
            lns = re.search(r'<a:lnSpc><a:spcPct val="(\d+)"', p)
            spans = []
            for r in re.findall(r'<a:r>(.*?)</a:r>', p, flags=re.S):
                sz = int(re.search(r'sz="(\d+)"', r).group(1)) / 100
                b = 'font-weight:700;' if 'b="1"' in r else ''
                sup = 'vertical-align:super;font-size:%.1fpx;' % (sz * 12700 / k * 0.65) if 'baseline="30000"' in r else ''
                c = clr(re.search(r'<a:rPr.*?</a:rPr>', r, flags=re.S).group(0))
                t = html.escape(re.search(r'<a:t>(.*?)</a:t>', r, flags=re.S).group(1))
                spans.append('<span style="font-size:%.1fpx;%s%scolor:%s">%s</span>' % (sz * 12700 / k, b, sup, c, t))
            st = 'margin:0 0 %.1fpx 0;line-height:%.2f;' % ((int(aft.group(1)) / 100 * 12700 / k) if aft else 0, (int(lns.group(1)) / 100000 * 1.2) if lns else 1.2)
            if algn: st += 'text-align:%s;' % {'ctr': 'center', 'l': 'left', 'r': 'right'}.get(algn.group(1), 'left')
            if bu: st += 'padding-left:%.1fpx;position:relative;' % px(334726)
            mark = '<span style="position:absolute;left:%.1fpx;top:0.45em;width:.55em;height:.55em;background:#3b6190;border-radius:50%%"></span>' % 0 if bu else ''
            out.append('<div style="%s">%s%s</div>' % (st, mark, ''.join(spans) or '&nbsp;'))
        return ''.join(out)

    els = []
    # 레이아웃: 머리띠 이미지와 두 패널
    els.append('<img src="%s" style="position:absolute;left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx">' % (uri('image1.jpg'), px(33983), px(35249), px(30275357), px(5797797)))
    for x, y, w, h in [(387465, 6099356, 14506964, 36186940), (15382036, 6099358, 14505719, 36186939)]:
        els.append('<div style="position:absolute;left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx;background:#fff;border:2px solid #bfbfbf;box-sizing:border-box"></div>' % (px(x), px(y), px(w), px(h)))
    # 머리 그룹(로고와 학술대회 이름): 흰 글씨
    els.append('<div style="position:absolute;left:%.1fpx;top:%.1fpx;width:%.1fpx;color:#fff;font:700 %.1fpx sans-serif;text-align:center">KSCE 2026 CONVENTION</div>' % (px(375966), px(375545), px(5074637), 36 * 12700 / k))
    els.append('<img src="%s" style="position:absolute;left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx;object-fit:cover;object-position:bottom">' % (uri('image2.png'), px(441848), px(985071), px(5076000), px(1120640)))

    body = s[s.index('</p:grpSp>') + len('</p:grpSp>'):]
    for m in re.finditer(r'<p:(sp|pic|graphicFrame)>(.*?)</p:\1>', body, flags=re.S):
        kind, b = m.group(1), m.group(2)
        mm = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"/><a:ext cx="(\d+)" cy="(\d+)"', b)
        if not mm: continue
        x, y, w, h = [int(v) for v in mm.groups()]
        st = 'position:absolute;left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx;box-sizing:border-box;overflow:hidden;' % (px(x), px(y), px(w), px(h))
        if kind == 'pic':
            rid = re.search(r'r:embed="(rId\d+)"', b).group(1)
            ell = ''
            els.append('<img src="%s" style="%sobject-fit:fill;border:2px solid #bfc5cc">' % (uri(rels[rid]), st) if 'poster_rId13' not in rels[rid] else '<img src="%s" style="%s">' % (uri(rels[rid]), st))
        elif kind == 'graphicFrame':
            cols = [int(v) for v in re.findall(r'<a:gridCol w="(\d+)"', b)]
            rows = []
            for tr in re.findall(r'<a:tr h="(\d+)">(.*?)</a:tr>', b, flags=re.S):
                cells = []
                for ci, tc in enumerate(re.findall(r'<a:tc>(.*?)</a:tc>', tr[1], flags=re.S)):
                    fill = re.search(r'<a:solidFill><a:srgbClr val="(\w+)"/></a:solidFill></a:tcPr>', tc).group(1)
                    cells.append('<td style="width:%.1fpx;background:#%s;border:1px solid #9aa7b5;padding:%.1fpx %.1fpx;vertical-align:middle">%s</td>' % (px(cols[ci]), fill, px(60000), px(91440), paras_html(tc)))
                rows.append('<tr style="height:%.1fpx">%s</tr>' % (px(int(tr[0])), ''.join(cells)))
            els.append('<table style="%sborder-collapse:collapse;table-layout:fixed;overflow:visible;height:auto">%s</table>' % (st.replace('overflow:hidden;', '').replace('height:%.1fpx;' % px(h), ''), ''.join(rows)))
        else:
            if 'prst="ellipse"' in b:
                els.append('<div style="%sbackground:#fff;border-radius:50%%"></div>' % st); continue
            fill = ''
            f = re.search(r'</a:prstGeom>(.*?)(?:<a:ln|</p:spPr>)', b, flags=re.S)
            if f and 'srgbClr' in f.group(1): fill = 'background:#%s;' % re.search(r'srgbClr val="(\w+)"', f.group(1)).group(1)
            elif f and 'schemeClr val="accent1"' in f.group(1): fill = 'background:#3b6190;'
            elif f and 'lumMod val="85000"' in f.group(1): fill = 'background:#d9d9d9;'
            tb = re.search(r'<p:txBody>(.*?)</p:txBody>', b, flags=re.S)
            ins = re.search(r'lIns="(\d+)" tIns="(\d+)" rIns="(\d+)" bIns="(\d+)"', b)
            pad = 'padding:%.1fpx %.1fpx;' % (px(int(ins.group(2))), px(int(ins.group(1)))) if ins else ''
            anc = 'display:flex;flex-direction:column;justify-content:center;' if 'anchor="ctr"' in b else ''
            rad = 'border-radius:999px;' if ('roundRect' in b and 'name="로고' in b) else ''
            prst = re.search(r'prst="(\w+)"', b)
            prst = prst.group(1) if prst else 'rect'
            if prst == 'roundRect' and not rad: rad = 'border-radius:%.1fpx;' % (px(min(w, h)) * 0.06)
            if prst == 'can': rad = 'border-radius:50%% / %.1fpx;' % (px(h) * 0.22)
            bd = ''
            lnm = re.search(r'<a:ln w="(\d+)">(.*?)</a:ln>', b, flags=re.S)
            if lnm and 'srgbClr' in lnm.group(2):
                bd = 'border:%.1fpx %s #%s;' % (max(1.0, int(lnm.group(1)) / k), 'dashed' if 'prstDash' in lnm.group(2) else 'solid', re.search(r'srgbClr val="(\w+)"', lnm.group(2)).group(1))
            els.append('<div style="%s%s%s%s%s%s">%s</div>' % (st, fill, pad, anc, rad, bd, paras_html(tb.group(1)) if tb else ''))

    lines = []
    for m in re.finditer(r'<p:cxnSp>(.*?)</p:cxnSp>', body, flags=re.S):
        b = m.group(1)
        xf = re.search(r'<a:xfrm([^>]*)><a:off x="(-?\d+)" y="(-?\d+)"/><a:ext cx="(\d+)" cy="(\d+)"/>', b)
        fl, x, y, w, h = xf.group(1), int(xf.group(2)), int(xf.group(3)), int(xf.group(4)), int(xf.group(5))
        x1, x2 = (x + w, x) if 'flipH="1"' in fl else (x, x + w)
        y1, y2 = (y + h, y) if 'flipV="1"' in fl else (y, y + h)
        col = re.search(r'<a:ln w="(\d+)">.*?srgbClr val="(\w+)"', b, flags=re.S)
        lw = max(1.0, int(col.group(1)) / k)
        dash = ' stroke-dasharray="%d,%d"' % (lw * 3, lw * 2) if 'prstDash' in b else ''
        mk = ' marker-end="url(#ah)"' if 'tailEnd' in b else ''
        lines.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#%s" stroke-width="%.1f"%s%s/>' % (px(x1), px(y1), px(x2), px(y2), col.group(2), lw, dash, mk))
    svg = ('<svg style="position:absolute;left:0;top:0" width="%.0f" height="%.0f"><defs><marker id="ah" markerWidth="5" markerHeight="5" refX="4" refY="2.5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L5,2.5 L0,5 z" fill="#3B4A63"/></marker></defs>%s</svg>' % (px(W), px(H), ''.join(lines)))
    els.append(svg)
    page = ('<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#fff;font-family:"WenQuanYi Zen Hei","Noto Sans CJK KR","Nanum Gothic",sans-serif}'
            '.p{position:relative;width:%.0fpx;height:%.0fpx;overflow:hidden}</style><div class="p">%s</div>' % (px(W), px(H), ''.join(els)))
    hp = out.replace('.png', '.html')
    open(hp, 'w', encoding='utf8').write(page)
    js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:%d,height:%d}});"
          "await p.goto('file://%s');await p.evaluate(z=>{document.body.style.zoom=z},%s);await p.screenshot({path:'%s'});await b.close()})()" % (int(px(W)*zoom)+1, int(px(H)*zoom)+1, os.path.abspath(hp), zoom, os.path.abspath(out)))
    jp = hp.replace('.html', '.cjs')
    open(jp, 'w').write(js)
    subprocess.run(['node', jp], check=True, env=dict(os.environ, NODE_PATH=os.environ.get('NODE_PATH', '/opt/node22/lib/node_modules')))
    os.remove(jp)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 8000, float(sys.argv[4]) if len(sys.argv) > 4 else 1.0)
