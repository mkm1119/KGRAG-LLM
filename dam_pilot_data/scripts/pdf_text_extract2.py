#!/usr/bin/env python3
"""Stdlib-only PDF text extractor v2: object streams (ObjStm), FlateDecode, ToUnicode CMaps, hex/literal strings.
Reading aid for literature checking only. Output is NOT a substitute for the PDF (layout/spacing may be imperfect)."""
import re, zlib, sys, collections
def inflate(d):
    try: return zlib.decompress(d)
    except Exception:
        try: return zlib.decompressobj().decompress(d)
        except Exception: return b''
class PDF:
    def __init__(self,path):
        self.b=open(path,'rb').read(); self.obj={}; self.stm={}
        for m in re.finditer(rb'(?<![\d])(\d+)\s+(\d+)\s+obj\b(.*?)endobj',self.b,flags=re.S):
            n=int(m.group(1)); body=m.group(3)
            self.obj[n]=body
        for n,body in list(self.obj.items()):
            s=self._raw_stream(body)
            if s is not None: self.stm[n]=s
        # expand object streams
        for n,body in list(self.obj.items()):
            if re.search(rb'/Type\s*/ObjStm',body) and n in self.stm:
                data=self.decode(n)
                N=int(re.search(rb'/N\s+(\d+)',body).group(1)); F=int(re.search(rb'/First\s+(\d+)',body).group(1))
                hdr=list(map(int,re.findall(rb'\d+',data[:F])))[:2*N]
                pairs=[(hdr[i],hdr[i+1]) for i in range(0,len(hdr)-1,2)]
                for k,(num,off) in enumerate(pairs):
                    end=pairs[k+1][1] if k+1<len(pairs) else len(data)-F
                    self.obj.setdefault(num,data[F+off:F+end])
    def _raw_stream(self,body):
        m=re.search(rb'stream\r?\n',body)
        if not m: return None
        e=body.rfind(b'endstream')
        return body[m.end():e if e>0 else len(body)].rstrip(b'\r\n') if e>0 else body[m.end():]
    def decode(self,n):
        body=self.obj[n]; d=self.stm.get(n,b'')
        head=body[:body.find(b'stream')] if b'stream' in body else body
        if b'FlateDecode' in head: return inflate(d)
        return d
    def dictpart(self,n):
        b=self.obj.get(n,b''); i=b.find(b'stream'); return b[:i] if i>=0 else b
    def ref(self,s,key):
        m=re.search(rb'/'+key+rb'\s+(\d+)\s+\d+\s+R',s); return int(m.group(1)) if m else None
    # ---- pages
    def pages(self):
        out=[]
        def walk(n,seen=set()):
            if n in seen: return
            seen.add(n); d=self.dictpart(n)
            if re.search(rb'/Type\s*/Pages\b',d):
                k=re.search(rb'/Kids\s*\[(.*?)\]',d,flags=re.S)
                for r in re.findall(rb'(\d+)\s+\d+\s+R',k.group(1)) if k else []: walk(int(r),seen)
            elif re.search(rb'/Type\s*/Page\b',d): out.append(n)
        roots=[n for n in self.obj if re.search(rb'/Type\s*/Pages\b',self.dictpart(n)) and not re.search(rb'/Parent',self.dictpart(n))]
        for r in roots: walk(r)
        if not out: out=[n for n in self.obj if re.search(rb'/Type\s*/Page\b',self.dictpart(n))]
        return out
    def resources_fonts(self,pn):
        n=pn; seen=set()
        while n and n not in seen:
            seen.add(n); d=self.dictpart(n)
            m=re.search(rb'/Resources\s*(\d+)\s+\d+\s+R',d)
            res=self.dictpart(int(m.group(1))) if m else (d[d.find(b'/Resources'):] if b'/Resources' in d else None)
            if res:
                f=re.search(rb'/Font\s*(\d+)\s+\d+\s+R',res)
                fd=self.dictpart(int(f.group(1))) if f else res[res.find(b'/Font'):] if b'/Font' in res else b''
                fonts={nm:int(r) for nm,r in re.findall(rb'/([A-Za-z0-9_.+-]+)\s+(\d+)\s+\d+\s+R',fd)}
                if fonts: return fonts
            p=self.ref(d,b'Parent'); n=p
        return {}
    def cmap(self,fn):
        d=self.dictpart(fn); tu=self.ref(d,b'ToUnicode'); 
        if tu is None or tu not in self.obj: return None
        if not hasattr(self,'_cm'): self._cm={}
        if tu in self._cm: return self._cm[tu]
        t=self.decode(tu); m={}; two=b'<0000>' in t or b'<00>' not in t
        def u(h): 
            try: return bytes.fromhex(h.decode()).decode('utf-16-be','replace')
            except Exception: return ''
        for blk in re.findall(rb'beginbfchar(.*?)endbfchar',t,flags=re.S):
            for a,c in re.findall(rb'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>',blk): m[int(a,16)]=u(c)
        for blk in re.findall(rb'beginbfrange(.*?)endbfrange',t,flags=re.S):
            for lo,hi,rest in re.findall(rb'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*(\[.*?\]|<[0-9A-Fa-f]+>)',blk,flags=re.S):
                lo=int(lo,16); hi=int(hi,16)
                if rest.startswith(b'['):
                    for i,c in enumerate(re.findall(rb'<([0-9A-Fa-f]+)>',rest)): m[lo+i]=u(c)
                else:
                    base=rest.strip(b'<>'); s=bytes.fromhex(base.decode()).decode('utf-16-be','replace')
                    for i in range(hi-lo+1): m[lo+i]=s[:-1]+chr(ord(s[-1])+i) if s else ''
        cs=re.search(rb'begincodespacerange\s*<([0-9A-Fa-f]+)>',t); nb=len(cs.group(1))//2 if cs else (2 if max(m,default=0)>255 else 1)
        self._cm[tu]=(m,nb); return self._cm[tu]
    def resources_xobj(self,pn):
        n=pn; seen=set()
        while n and n not in seen:
            seen.add(n); d=self.dictpart(n)
            m=re.search(rb'/Resources\s*(\d+)\s+\d+\s+R',d)
            res=self.dictpart(int(m.group(1))) if m else (d[d.find(b'/Resources'):] if b'/Resources' in d else None)
            if res and b'/XObject' in res:
                x=re.search(rb'/XObject\s*(\d+)\s+\d+\s+R',res)
                xd=self.dictpart(int(x.group(1))) if x else res[res.find(b'/XObject'):]
                return {nm:int(r) for nm,r in re.findall(rb'/([A-Za-z0-9_.+-]+)\s+(\d+)\s+\d+\s+R',xd)}
            n=self.ref(d,b'Parent')
        return {}
    def form_fonts(self,xn):
        d=self.dictpart(xn); f=re.search(rb'/Font\s*<<(.*?)>>',d,flags=re.S)
        return {nm:int(r) for nm,r in re.findall(rb'/([A-Za-z0-9_.+-]+)\s+(\d+)\s+\d+\s+R',f.group(1))} if f else {}
    def content(self,pn):
        d=self.dictpart(pn); c=re.search(rb'/Contents\s*(\[.*?\]|\d+\s+\d+\s+R)',d,flags=re.S)
        refs=[int(x) for x in re.findall(rb'(\d+)\s+\d+\s+R',c.group(1))] if c else []
        return b'\n'.join(self.decode(r) for r in refs if r in self.obj)
TOK=re.compile(rb'\((?:\\.|[^\\()]|\((?:\\.|[^\\()])*\))*\)|<[0-9A-Fa-f\s]*>|\[|\]|/[^\s/\[\]()<>]+|[-+]?\d*\.?\d+|[A-Za-z\'"*]+',re.S)
def unesc(s):
    out=bytearray(); i=0
    while i<len(s):
        c=s[i]
        if c==0x5c and i+1<len(s):
            n=s[i+1]; i+=2
            if n in b'nrtbf': out.append({110:10,114:13,116:9,98:8,102:12}[n])
            elif 48<=n<=55:
                j=i-1; k=0
                while k<3 and j<len(s) and 48<=s[j]<=55: k+=1; j+=1
                out.append(int(s[i-1:j],8)&255); i=j
            elif n in b'\r\n': pass
            else: out.append(n)
        else: out.append(c); i+=1
    return bytes(out)
def page_text(pdf,pn,depth=0,_content=None,_fonts=None,_x=None):
    fonts=_fonts if _fonts is not None else pdf.resources_fonts(pn); xobj=_x if _x is not None else pdf.resources_xobj(pn) if depth==0 else {}
    cur=None; out=[]; line=[]; y=None
    def dec(bs):
        if cur is None: return bs.decode('latin-1')
        cm=pdf.cmap(cur)
        if not cm: return bs.decode('mac_roman','replace') if len(bs) else ''
        m,nb=cm; s=''
        for i in range(0,len(bs)-nb+1,nb): s+=m.get(int.from_bytes(bs[i:i+nb],'big'),'')
        return s
    def flush():
        nonlocal line
        if line: out.append(''.join(line)); line=[]
    stack=[]; arr=None
    for m in TOK.finditer(_content if _content is not None else pdf.content(pn)):
        t=m.group(0)
        if t==b'[': arr=[]; continue
        if t==b']':
            stack.append(arr); arr=None; continue
        if t.startswith(b'(') : v=('s',unesc(t[1:-1]))
        elif t.startswith(b'<'): 
            h=re.sub(rb'\s',b'',t[1:-1]); h=h+b'0' if len(h)%2 else h; v=('s',bytes.fromhex(h.decode()))
        elif t.startswith(b'/'): v=('n',t[1:])
        elif re.fullmatch(rb'[-+]?\d*\.?\d+',t): v=('d',float(t))
        else:
            op=t
            if op==b'Tf' and len(stack)>=2 and isinstance(stack[-2],tuple) and stack[-2][0]=='n': cur=fonts.get(stack[-2][1])
            elif op in (b'Tj',b"'",b'"') and stack and isinstance(stack[-1],tuple) and stack[-1][0]=='s': line.append(dec(stack[-1][1]))
            elif op==b'TJ' and stack and isinstance(stack[-1],list):
                for e in stack[-1]:
                    if e[0]=='s': line.append(dec(e[1]))
                    elif e[0]=='d' and e[1]<-180: line.append(' ')
            elif op in (b'Td',b'TD') and len(stack)>=2:
                try:
                    dy=stack[-1][1]
                    if abs(dy)>0.5: flush()
                except Exception: pass
            elif op==b'Tm' and len(stack)>=6:
                ny=stack[-1][1]
                if y is None or abs(ny-y)>1.5: flush()
                y=ny
            elif op==b'Do' and stack and isinstance(stack[-1],tuple) and stack[-1][0]=='n' and depth<3:
                xn=xobj.get(stack[-1][1])
                if xn and b'/Form' in pdf.dictpart(xn):
                    flush(); sub=page_text(pdf,pn,depth+1,pdf.decode(xn),{**fonts,**pdf.form_fonts(xn)},{})
                    if sub: out.append(sub)
            elif op in (b'T*',b'ET'): flush() if op==b'T*' else None
            stack=[]; continue
        if arr is not None: arr.append(v)
        else: stack.append(v)
    flush(); return '\n'.join(out)
def extract(path):
    p=PDF(path); return [(i,page_text(p,pn)) for i,pn in enumerate(p.pages(),1)]
if __name__=="__main__":
    for i,t in extract(sys.argv[1]): print(f"\n=== PAGE {i} ===\n{t}")
