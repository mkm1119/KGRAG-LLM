#!/usr/bin/env python3
"""Minimal PDF text extractor (stdlib only) for simple-encoded PDFs (e.g. Quartz PDFContext + MacRoman).
Used only to READ literature for citation checking; extracted text is a working aid, not a substitute for the PDF."""
import re, zlib, sys
def load(path):
    b=open(path,'rb').read()
    objs={int(n):o for n,o in re.findall(rb'(?m)^(\d+) 0 obj(.*?)endobj',b,flags=re.S)}
    return b,objs
def stream(o):
    m=re.search(rb'stream\r?\n(.*?)\r?\nendstream',o,flags=re.S)
    if not m: return b''
    head=o[:m.start()]
    d=m.group(1)
    if b'FlateDecode' in head:
        try: return zlib.decompress(d)
        except Exception: return b''
    return d
def unesc(s):
    out=bytearray(); i=0
    while i<len(s):
        c=s[i]
        if c==0x5c and i+1<len(s):
            n=s[i+1]; i+=2
            if n in b'nrtbf': out.append({ord('n'):10,ord('r'):13,ord('t'):9,ord('b'):8,ord('f'):12}[n])
            elif 48<=n<=55:
                j=i-1; k=0
                while k<3 and j<len(s) and 48<=s[j]<=55: k+=1; j+=1
                out.append(int(s[i-1:j],8)&255); i=j
            elif n in b'\r\n': pass
            else: out.append(n)
        else: out.append(c); i+=1
    return bytes(out)
def page_order(objs):
    pages=[]
    def walk(n):
        o=objs.get(n,b'')
        if re.search(rb'/Type\s*/Pages',o):
            kids=re.search(rb'/Kids\s*\[(.*?)\]',o,flags=re.S)
            for k in re.findall(rb'(\d+) 0 R',kids.group(1)): walk(int(k))
        elif re.search(rb'/Type\s*/Page\b',o): pages.append(n)
    root=[n for n,o in objs.items() if re.search(rb'/Type\s*/Pages',o) and b'/Parent' not in o]
    for r in root: walk(r)
    return pages
TOK=re.compile(rb'(?P<tm>(?:-?[\d.]+\s+){5}(?P<x>-?[\d.]+)\s+(?P<y>-?[\d.]+)\s+Tm)|(?P<tj>\((?:\\.|[^\\)])*\)\s*Tj)|(?P<tjs>\[(?:\\.|[^\]\\])*\]\s*TJ)|(?P<td>-?[\d.]+\s+-?[\d.]+\s+T[dD])|(?P<ts>T\*)',re.S)
def content_text(c):
    out=[]; y=None; line=[]
    def flush():
        nonlocal line
        if line: out.append(''.join(line)); line=[]
    for m in TOK.finditer(c):
        if m.group('tm'):
            ny=float(m.group('y'))
            if y is None or abs(ny-y)>2: flush()
            y=ny
        elif m.group('td') or m.group('ts'): flush()
        elif m.group('tj'):
            s=m.group('tj'); s=s[1:s.rindex(b')')]; line.append(unesc(s).decode('mac_roman','replace'))
        elif m.group('tjs'):
            arr=m.group('tjs')
            for part in re.finditer(rb'\((?:\\.|[^\\)])*\)|-?[\d.]+',arr):
                p=part.group(0)
                if p.startswith(b'('): line.append(unesc(p[1:-1]).decode('mac_roman','replace'))
                else:
                    try:
                        if float(p)<-200: line.append(' ')
                    except: pass
    flush(); return out
def extract(path):
    b,objs=load(path); res=[]
    for i,pn in enumerate(page_order(objs),1):
        o=objs[pn]; cs=re.search(rb'/Contents\s*(\[.*?\]|\d+ 0 R)',o,flags=re.S)
        refs=[int(x) for x in re.findall(rb'(\d+) 0 R',cs.group(1))] if cs else []
        c=b'\n'.join(stream(objs.get(r,b'')) for r in refs)
        res.append((i,'\n'.join(content_text(c))))
    return res
if __name__=="__main__":
    for i,t in extract(sys.argv[1]): print(f"\n=== PAGE {i} ===\n{t}")
