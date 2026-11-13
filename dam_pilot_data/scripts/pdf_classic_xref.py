#!/usr/bin/env python3
"""xref 스트림·객체 스트림을 쓰는 PDF를 고전 xref 표 형식으로 다시 쓴다(내용은 그대로). stdlib만 사용.
build_paper_review_pdf.py가 고전 xref 표만 지원하므로, 그 앞 단계로 쓴다.
사용: python3 pdf_classic_xref.py <입력.pdf> <출력.pdf>
"""
import re, sys
from pdf_text_extract2 import PDF


def main(src, dst):
    pdf = PDF(src)
    tr = None
    for n, body in pdf.obj.items():
        d = pdf.dictpart(n)
        if re.search(rb'/Type\s*/XRef', d) and b'/Root' in d:
            tr = d
    if tr is None:
        raise SystemExit('xref 스트림을 찾지 못함(이미 고전 형식일 수 있음)')
    root = re.search(rb'/Root\s+(\d+)\s+(\d+)\s+R', tr).group(0)
    info = re.search(rb'/Info\s+(\d+)\s+(\d+)\s+R', tr)
    out = bytearray(b'%PDF-1.7\n%\xe2\xe3\xcf\xd3\n'); off = {}
    for n in sorted(pdf.obj):
        d = pdf.dictpart(n)
        if re.search(rb'/Type\s*/(XRef|ObjStm)\b', d):
            continue
        off[n] = len(out)
        out += b'%d 0 obj\n' % n + pdf.obj[n].strip(b'\r\n ') + b'\nendobj\n'
    size = max(off) + 1; xr = len(out)
    out += b'xref\n0 %d\n' % size + b'0000000000 65535 f \n'
    for n in range(1, size):
        out += (b'%010d 00000 n \n' % off[n]) if n in off else b'0000000000 65535 f \n'
    out += b'trailer\n<< /Size %d %s %s >>\nstartxref\n%d\n%%%%EOF\n' % (size, root, info.group(0) if info else b'', xr)
    open(dst, 'wb').write(out)
    print('objects', len(off))


if __name__ == '__main__':
    main(*sys.argv[1:3])
