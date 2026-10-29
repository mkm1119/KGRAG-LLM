#!/usr/bin/env python3
"""PDF 페이지의 글자 줄과 위치(x, y)를 뽑는다. stdlib만 사용. pdf_text_extract2의 해석기를 재사용한다.
반환: [(x, y, size, text)]  (PDF 좌표, 왼쪽 아래 원점)"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdf_text_extract2 import PDF, TOK, unesc


def mul(a, b):
    return [a[0]*b[0]+a[1]*b[2], a[0]*b[1]+a[1]*b[3], a[2]*b[0]+a[3]*b[2], a[2]*b[1]+a[3]*b[3],
            a[4]*b[0]+a[5]*b[2]+b[4], a[4]*b[1]+a[5]*b[3]+b[5]]


def runs(pdf, pn):
    fonts = pdf.resources_fonts(pn)
    ctm = [1, 0, 0, 1, 0, 0]; stack = []
    tm = tlm = [1, 0, 0, 1, 0, 0]; cur = None; fs = 1; tl = 0
    out = []; args = []; arr = None

    def dec(bs):
        cm = pdf.cmap(cur) if cur else None
        if not cm:
            return bs.decode('latin-1')
        m, nb = cm
        return ''.join(m.get(int.from_bytes(bs[i:i+nb], 'big'), '') for i in range(0, len(bs)-nb+1, nb))

    def show(s):
        t = mul(tm, ctm)
        out.append((t[4], t[5], fs * abs(t[3] or t[0]), s))

    for m in TOK.finditer(pdf.content(pn)):
        t = m.group(0)
        if t == b'[':
            arr = []; continue
        if t == b']':
            args.append(arr); arr = None; continue
        if t[:1] in b'(<' and not t.startswith(b'<<'):
            v = unesc(t[1:-1]) if t[:1] == b'(' else bytes.fromhex(re.sub(rb'\s', b'', t[1:-1]).decode() + ('0' if len(re.sub(rb'\s', b'', t[1:-1])) % 2 else ''))
            (arr if arr is not None else args).append(v); continue
        if re.fullmatch(rb'[-+]?\d*\.?\d+', t):
            (arr if arr is not None else args).append(float(t)); continue
        if t.startswith(b'/'):
            args.append(t[1:]); continue
        op = t
        try:
            if op == b'q': stack.append(ctm[:])
            elif op == b'Q': ctm = stack.pop() if stack else ctm
            elif op == b'cm': ctm = mul(args[-6:], ctm)
            elif op == b'BT': tm = tlm = [1, 0, 0, 1, 0, 0]
            elif op == b'Tf':
                cur = fonts.get(args[-2]) if isinstance(args[-2], bytes) else None; fs = args[-1]
            elif op == b'TL': tl = args[-1]
            elif op in (b'Td', b'TD'):
                if op == b'TD': tl = -args[-1]
                tlm = mul([1, 0, 0, 1, args[-2], args[-1]], tlm); tm = tlm[:]
            elif op == b'Tm': tlm = list(args[-6:]); tm = tlm[:]
            elif op == b'T*': tlm = mul([1, 0, 0, 1, 0, -tl], tlm); tm = tlm[:]
            elif op == b'Tj' or op == b"'":
                if op == b"'": tlm = mul([1, 0, 0, 1, 0, -tl], tlm); tm = tlm[:]
                show(dec(args[-1]))
            elif op == b'TJ':
                show(''.join(dec(x) if isinstance(x, bytes) else (' ' if x < -200 else '') for x in args[-1]))
        except Exception:
            pass
        args = []
    return out


def lines(pdf, pn, tol=2.0, mid=297.6):
    """같은 줄(y)의 글자를 x 순서로 합친다. 두 열(mid 기준 왼쪽·오른쪽)은 합치지 않는다."""
    rs = sorted(runs(pdf, pn), key=lambda r: (-round(r[1]), r[0]))
    out = []
    for x, y, s, t in rs:
        if out and abs(out[-1][1] - y) < tol and x - out[-1][4] < 30 and x >= out[-1][0] and (x >= mid) == (out[-1][0] >= mid):
            out[-1][3] += t; out[-1][4] = x + len(t) * s * 0.45
        else:
            out.append([x, y, s, t, x + len(t) * s * 0.45])
    return [(x, y, s, t) for x, y, s, t, _ in out]


if __name__ == '__main__':
    p = PDF(sys.argv[1]); pages = p.pages()
    for x, y, s, t in lines(p, pages[int(sys.argv[2]) - 1])[:int(sys.argv[3]) if len(sys.argv) > 3 else 80]:
        print('%6.1f %6.1f %4.1f %s' % (x, y, s, t[:90]))
