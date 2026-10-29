#!/usr/bin/env python3
"""두 단 논문 PDF의 본문을 열 순서(왼쪽 → 오른쪽)로 이어 붙이고, 문장 단위로 나눠 위치(줄 사각형)를 돌려준다. stdlib만 사용."""
import re
from pdf_text_extract2 import PDF
from pdf_text_positions import lines

COLS = ((37.6, 289.0), (306.6, 557.7))
ABBR = ('Fig', 'Figs', 'al', 'e.g', 'i.e', 'Eq', 'No', 'vs', 'Sect', 'Ref')


def norm(t):
    return re.sub(r'[^a-z0-9]', '', t.lower())


class Page:
    def __init__(self, pdf, pn, W=595.0):
        ls = [l for l in lines(pdf, pn) if 60 < l[1] < 745 and l[2] >= 7.6]
        self.rows = []
        for c, (L0, R0) in enumerate(COLS):
            cl = sorted([l for l in ls if (l[0] >= W / 2 - 10) == bool(c)], key=lambda l: -l[1])
            self.rows += [(c, l) for l in cl]
        raw, rmap, self.breaks = '', [], set()
        for i, (c, l) in enumerate(self.rows):
            t = l[3].rstrip()
            L0 = COLS[c][0]
            if l[0] > L0 + 6 or re.match(r'\d+(\.\d+)*\.\s*[A-Z]', t) or re.match(r'\(\d+\)|[a-d]\)', t):
                self.breaks.add(len(raw) + (1 if raw else 0))     # 새 문단·소제목이 시작하는 위치
            if i and re.match(r'\d+(\.\d+)*\.\s*[A-Z]', self.rows[i - 1][1][3]):
                self.breaks.add(len(raw) + (1 if raw else 0))
            if raw:
                if raw.endswith('-'):
                    raw = raw[:-1]; rmap.pop()
                else:
                    raw += ' '; rmap.append((i - 1, len(self.rows[i - 1][1][3].rstrip())))
            for k, ch in enumerate(t):
                raw += ch; rmap.append((i, k))
        self.raw, self.rmap = raw, rmap
        self.nidx = [i for i, ch in enumerate(raw) if ch.isalnum()]
        self.ntext = ''.join(raw[i].lower() for i in self.nidx)

    def find(self, phrase):
        k = self.ntext.find(norm(phrase))
        return None if k < 0 else self.nidx[k]

    def sentence_end(self, s):
        """s(원문 문자 위치)에서 시작한 문장의 끝 위치."""
        nb = min([b for b in self.breaks if b > s + 1] or [len(self.raw)])
        for m in re.finditer(r'[.:](?=\s+[A-Z(“"]|\s*$)', self.raw[s:]):
            e = s + m.end()
            if e > nb:
                break
            before = self.raw[max(s, e - 6):e - 1].split(' ')[-1]
            if before.rstrip('.') in ABBR or re.fullmatch(r'\d+', before):
                continue
            return e
        return nb

    def rects(self, a, b):
        """원문 문자 구간 [a, b)를 덮는 줄별 사각형."""
        out = {}
        for p in range(a, b):
            i, k = self.rmap[p]
            lo, hi = out.get(i, (k, k))
            out[i] = (min(lo, k), max(hi, k + 1))
        rs = []
        for i, (lo, hi) in sorted(out.items()):
            c, l = self.rows[i]
            L0, R0 = COLS[c]
            t = l[3].rstrip(); n = max(1, len(t))
            wid = min(R0 - l[0], n * l[2] * 0.52) if i + 1 < len(self.rows) and self.rows[i + 1][1][0] <= L0 + 6 and self.rows[i + 1][0] == c else min(R0 - l[0], n * l[2] * 0.47)
            x0 = l[0] + wid * lo / n; x1 = l[0] + wid * hi / n
            rs.append((x0 - 0.8, l[1] - l[2] * 0.25, x1 + 0.8, l[1] + l[2] * 0.85))
        return rs, self.rows[min(out)][1]

    def sentences(self):
        out, s = [], 0
        while s < len(self.raw):
            while s < len(self.raw) and self.raw[s] == ' ':
                s += 1
            e = self.sentence_end(s)
            out.append(self.raw[s:e]); s = e
        return out


if __name__ == '__main__':
    import sys
    pdf = PDF(sys.argv[1]); pages = pdf.pages()
    for pi in map(int, sys.argv[2].split(',')):
        pg = Page(pdf, pages[pi - 1])
        print('=== p%d' % pi)
        for j, s in enumerate(pg.sentences()):
            print('%d| %s' % (j, s[:160]))
