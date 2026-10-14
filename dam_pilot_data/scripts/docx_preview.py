#!/usr/bin/env python3
"""docx(본 프로젝트가 만든 서식 부분집합)를 HTML로 그려 PNG 페이지로 저장하는 미리보기(LibreOffice를 쓸 수 없을 때).
사용: NODE_PATH=/opt/node22/lib/node_modules python3 scripts/docx_preview.py <docx> <출력 폴더>"""
import html, os, re, subprocess, sys, zipfile

def main(docx, outdir):
    os.makedirs(outdir, exist_ok=True)
    x = zipfile.ZipFile(docx).read('word/document.xml').decode('utf8')
    b = x[x.index('<w:body>') + 8:x.index('</w:body>')]
    top = re.findall(r'<w:p[ >].*?</w:p>|<w:tbl>.*?</w:tbl>', b, flags=re.S)
    PX = 665 / 9972.0
    def runs(p):
        out = []
        for r in re.findall(r'<w:r>.*?</w:r>', p, flags=re.S):
            st = ''
            if '<w:b/>' in r: st += 'font-weight:700;'
            c = re.search(r'<w:color w:val="(\w+)"', r)
            if c: st += 'color:#%s;' % c.group(1)
            s = re.search(r'<w:sz w:val="(\d+)"', r)
            if s: st += 'font-size:%.1fpt;' % (int(s.group(1)) / 2)
            if 'Consolas' in r: st += 'font-family:Consolas,"WenQuanYi Zen Hei",monospace;'
            t = ''.join(re.findall(r'<w:t(?:\s[^>]*)?>(.*?)</w:t>', r, flags=re.S))
            if '<w:br/>' in r: t = t.replace('', '')
            out.append('<span style="%s">%s</span>' % (st, t.replace('\n', '<br>')))
        return ''.join(out)
    import base64
    zf = zipfile.ZipFile(docx)
    relx = zf.read('word/_rels/document.xml.rels').decode('utf8')
    def para(p, in_tbl=False):
        if '<w:drawing>' in p:
            rid = re.search(r'r:embed="(\w+)"', p).group(1)
            tgt = re.search(r'Id="%s"[^>]*Target="([^"]+)"|Target="([^"]+)"[^>]*Id="%s"' % (rid, rid), relx)
            tgt = tgt.group(1) or tgt.group(2)
            ext = re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"', p)
            wpx = int(ext.group(1)) / 635 * PX
            return '<div style="text-align:center"><img style="width:%.0fpx" src="data:image/png;base64,%s"></div>' % (wpx, base64.b64encode(zf.read('word/' + tgt)).decode())
        sty = re.search(r'<w:pStyle w:val="(\w+)"', p)
        center = '<w:jc w:val="center"/>' in p
        pb = '<w:pageBreakBefore/>' in p
        body = runs(p) or '&nbsp;'
        if '<w:br/>' in p: body = body.replace('</span><span', '<br><span')
        al = 'text-align:center;' if center else ''
        if in_tbl: return '<div style="%smargin:0 0 1px 0;white-space:pre-wrap">%s</div>' % (al, body)
        if sty and sty.group(1) == '1': return '<h1 class="%s">%s</h1>' % ('pb' if pb else '', body)
        if sty and sty.group(1) == '21': return '<h2>%s</h2>' % body
        if sty and sty.group(1) == 'a0': return '<div style="margin:2px 0 3px 16px;text-indent:-12px">• %s</div>' % body
        return '<div style="%smargin:3px 0 5px 0;white-space:pre-wrap">%s</div>' % (al, body)
    def tbl(t):
        ws = [int(v) for v in re.findall(r'<w:gridCol w:w="(\d+)"', t)]
        rows = []
        for tr in re.findall(r'<w:tr[ >].*?</w:tr>', t, flags=re.S):
            cells = []
            for tc in re.findall(r'<w:tc>.*?</w:tc>', tr, flags=re.S):
                fill = re.search(r'w:fill="(\w+)"', tc)
                w = int(re.search(r'<w:tcW w:w="(\d+)"', tc).group(1))
                ps = ''.join(para(p, True) for p in re.findall(r'<w:p[ >].*?</w:p>', tc, flags=re.S))
                cells.append('<td style="width:%.0fpx;%s">%s</td>' % (w * PX, 'background:#%s;' % fill.group(1) if fill else '', ps))
            rows.append('<tr>%s</tr>' % ''.join(cells))
        return '<table>%s</table>' % ''.join(rows)
    parts = [tbl(p) if p.startswith('<w:tbl') else para(p) for p in top]
    page = ('<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#fff;font-family:"WenQuanYi Zen Hei","Noto Sans CJK KR",sans-serif;font-size:10pt;color:#222}'
            '.pg{width:665px;margin:0 auto;padding:30px 0}table{border-collapse:collapse;table-layout:fixed;width:665px;margin:4px 0 8px;font-size:9pt}'
            'td{border:1px solid #a6a6a6;padding:4px 7px;vertical-align:middle}h1{font-size:17pt;color:#1f4e79;border-bottom:2px solid #1f4e79;margin:22px 0 8px;padding-bottom:3px}'
            'h1.pb{break-before:page;page-break-before:always}h2{font-size:13pt;color:#1f4e79;margin:18px 0 6px}</style><div class="pg">%s</div>' % ''.join(parts))
    hp = os.path.join(outdir, 'preview.html'); open(hp, 'w', encoding='utf8').write(page)
    js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});const p=await b.newPage({viewport:{width:760,height:1000}});"
          "await p.goto('file://%s');const h=await p.evaluate(()=>document.body.scrollHeight);const n=Math.ceil(h/1100);"
          "for(let i=0;i<n;i++){await p.screenshot({fullPage:true,path:'%s/p'+String(i+1).padStart(2,'0')+'.png',clip:{x:0,y:i*1100,width:760,height:Math.min(1100,h-i*1100)}});}console.log('pages',n,'height',h);await b.close()})()" % (os.path.abspath(hp), os.path.abspath(outdir)))
    jp = os.path.join(outdir, 'shot.cjs'); open(jp, 'w').write(js)
    subprocess.run(['node', jp], check=True, env=dict(os.environ, NODE_PATH='/opt/node22/lib/node_modules'))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
