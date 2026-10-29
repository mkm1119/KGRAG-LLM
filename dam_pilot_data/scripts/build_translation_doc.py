#!/usr/bin/env python3
"""논문 해석 JSON을 A4 HTML로 만든다(인쇄는 Chromium으로). 사용: python3 build_translation_doc.py <해석.json> <출력.html> <제목> <서지>"""
import html, json, sys
src, dst, title, cite = sys.argv[1:5]
m = json.load(open(src, encoding='utf-8'))
o = ['<!doctype html><html><head><meta charset="utf-8"><style>@page{size:A4;margin:16mm}body{font-family:"WenQuanYi Zen Hei",sans-serif;font-size:10pt;line-height:1.6;color:#1a1a1a}'
     'h1{font-size:15pt;margin:0 0 4pt}.sub{color:#555;font-size:9pt;margin-bottom:14pt}h2{font-size:11.5pt;color:#1f3a5f;border-bottom:1px solid #9aa6b5;padding-bottom:2pt;margin:18pt 0 6pt}'
     'h3{font-size:10.5pt;color:#1f3a5f;margin:10pt 0 3pt}.lead{color:#777;font-size:8.5pt;margin:8pt 0 1pt}p{margin:0 0 4pt;white-space:pre-wrap}</style></head><body>',
     '<h1>%s</h1><div class="sub">%s<br>문단마다 회색 글씨는 원문 문단의 첫머리이고, 그 아래가 해석이다. 쪽 번호는 원문 PDF의 쪽이다.</div>' % (html.escape(title), cite)]
for p in sorted(m, key=int):
    o.append('<h2>원문 %s쪽</h2>' % p)
    for e in m[p]:
        if e['lead'].startswith('#'):
            o.append('<h3>%s</h3>' % html.escape(e['lead'][1:].strip()))
        else:
            o.append('<div class="lead">%s</div>' % html.escape(e['lead']))
        if e['ko']:
            o.append('<p>%s</p>' % html.escape(e['ko']))
o.append('</body></html>')
open(dst, 'w', encoding='utf-8').write(''.join(o))
