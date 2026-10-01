#!/usr/bin/env python3
"""Minimal stdlib HWP5 text extractor (OLE CFB reader + BodyText record parser). Output is for reading only; raw .hwp is kept."""
import struct,zlib,re,sys
def read_cfb(data):
    ss=1<<struct.unpack('<H',data[30:32])[0]; mss=1<<struct.unpack('<H',data[32:34])[0]
    nfat,dirstart,_,cutoff,minifat,nmf,difat0,ndifat=struct.unpack('<IIIIIIII',data[44:76])[0],struct.unpack('<I',data[48:52])[0],0,struct.unpack('<I',data[56:60])[0],struct.unpack('<I',data[60:64])[0],struct.unpack('<I',data[64:68])[0],struct.unpack('<I',data[68:72])[0],struct.unpack('<I',data[72:76])[0]
    sec=lambda n:data[512+n*ss:512+(n+1)*ss]
    difat=list(struct.unpack('<109I',data[76:512]))
    d=difat0
    for _ in range(ndifat):
        s=sec(d); v=struct.unpack('<%dI'%(ss//4),s); difat+=list(v[:-1]); d=v[-1]
    fat=[]
    for n in difat:
        if n<0xFFFFFFFA: fat+=list(struct.unpack('<%dI'%(ss//4),sec(n)))
    def chain(start):
        out=[];n=start
        while n<0xFFFFFFFA and len(out)<100000: out.append(n); n=fat[n]
        return out
    def stream(start,size): return b''.join(sec(n) for n in chain(start))[:size]
    dirdata=b''.join(sec(n) for n in chain(dirstart))
    ents=[]
    for i in range(0,len(dirdata),128):
        e=dirdata[i:i+128]
        nl=struct.unpack('<H',e[64:66])[0]; name=e[:max(nl-2,0)].decode('utf-16le','ignore')
        typ=e[66]; left,right,child=struct.unpack('<III',e[68:80]); start=struct.unpack('<I',e[116:120])[0]; size=struct.unpack('<Q',e[120:128])[0]
        ents.append(dict(name=name,type=typ,left=left,right=right,child=child,start=start,size=size))
    root=ents[0]; ministream=stream(root['start'],root['size'])
    minifatdata=b''.join(sec(n) for n in chain(minifat)); mfat=list(struct.unpack('<%dI'%(len(minifatdata)//4),minifatdata)) if minifatdata else []
    def getstream(e):
        if e['size']<cutoff:
            out=b'';n=e['start']
            while n<0xFFFFFFFA: out+=ministream[n*mss:(n+1)*mss]; n=mfat[n]
            return out[:e['size']]
        return stream(e['start'],e['size'])
    def walk(idx,path,res):
        if idx==0xFFFFFFFF: return
        e=ents[idx]; walk(e['left'],path,res); 
        p=path+[e['name']]; res[tuple(p)]=e
        if e['type']==1: walk(e['child'],p,res)
        walk(e['right'],path,res)
    res={}; walk(root['child'],[],res)
    return res,getstream
def hwp_text(path):
    data=open(path,'rb').read(); res,get=read_cfb(data)
    fh=get(res[('FileHeader',)]); comp=struct.unpack('<I',fh[36:40])[0]&1
    out=[]
    for k in sorted(k for k in res if len(k)==2 and k[0]=='BodyText'):
        d=get(res[k])
        if comp: d=zlib.decompress(d,-15)
        i=0
        while i+4<=len(d):
            h=struct.unpack('<I',d[i:i+4])[0]; tag=h&0x3ff; size=(h>>20)&0xfff; i+=4
            if size==0xfff: size=struct.unpack('<I',d[i:i+4])[0]; i+=4
            if tag==67: out.append(re.sub(r'[\x00-\x08\x0b-\x1f]','',d[i:i+size].decode('utf-16le','ignore')))
            i+=size
    return '\n'.join(out)
if __name__=='__main__':
    t=hwp_text(sys.argv[1]); open(sys.argv[2],'w',encoding='utf-8').write(t); print(len(t)); print(t[:1500])
