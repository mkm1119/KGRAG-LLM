#!/usr/bin/env python3
"""리뷰 메모의 형광펜 위치를 낱말 단위로 정확히 잡는다(1단 편집 논문용).
메모 JSON의 'S:문장 첫머리'와 줄 단위 문구를, poppler(pdftotext -bbox-layout)가 주는 낱말 상자로 바꿔 'BOX:x0,y0,x1,y1' 목록으로 쓴다.
build_paper_review_pdf.py의 글자 수 비례 추정 대신 실제 낱말 위치를 쓰므로 문장의 시작과 끝이 낱말 경계에 정확히 맞는다.

사용: python3 memo_anchor_boxes.py <원문.pdf> <메모.json> <출력.json> [본문 왼쪽 끝=166] [머리말 아래 경계(위에서부터 pt)=60]
"""
import json, re, subprocess, sys
import xml.etree.ElementTree as ET

SRC, MEMO, OUT = sys.argv[1:4]
LEFT = float(sys.argv[4]) if len(sys.argv) > 4 else 166.0
TOPCUT = float(sys.argv[5]) if len(sys.argv) > 5 else 60.0
ABBR = {'Fig', 'Figs', 'al', 'e.g', 'i.e', 'Eq', 'No', 'vs', 'Sect', 'Ref', 'etc'}
norm = lambda t: re.sub(r'[^a-z0-9]', '', t.lower())


class Page:
    def __init__(self, pn):
        x = subprocess.run(['pdftotext', '-bbox-layout', '-f', str(pn), '-l', str(pn), SRC, '-'], capture_output=True, text=True).stdout
        x = re.sub(r'<!DOCTYPE[^>]*>', '', x).replace('xmlns="http://www.w3.org/1999/xhtml"', '')
        root = ET.fromstring(x)
        page = root.find('.//page'); self.H = float(page.get('height'))
        lines = []
        for ln in page.iter('line'):
            ws = [(float(w.get('xMin')), float(w.get('yMin')), float(w.get('xMax')), float(w.get('yMax')), w.text or '') for w in ln.iter('word')]
            ws = [w for w in ws if w[4].strip() and w[0] >= LEFT - 3]            # 왼쪽 여백의 서지 정보는 뺀다
            if not ws or float(ln.get('yMin')) < TOPCUT:
                continue
            lines.append({'x0': min(w[0] for w in ws), 'y0': min(w[1] for w in ws), 'y1': max(w[3] for w in ws), 'ws': sorted(ws)})
        lines.sort(key=lambda l: (round(l['y0']), l['x0']))
        merged = []                                   # 같은 높이로 쪼개진 줄 조각을 합친다
        for l in lines:
            if merged and abs(merged[-1]['y0'] - l['y0']) < 3 and abs(merged[-1]['y1'] - l['y1']) < 3:
                m = merged[-1]; m['ws'] = sorted(m['ws'] + l['ws']); m['x0'] = min(m['x0'], l['x0'])
            else:
                merged.append(l)
        self.lines = merged
        self.words = []                               # (줄 번호, x0, x1, 글자, 문단 시작 여부)
        for i, l in enumerate(merged):
            gap = i and l['y0'] - merged[i - 1]['y1']
            h = l['y1'] - l['y0']
            newpar = i == 0 or re.fullmatch(r'\d+(\.\d+)*\.', l['ws'][0][4]) or l['x0'] > LEFT + 8 or gap > h * 0.9 or abs(h - (merged[i - 1]['y1'] - merged[i - 1]['y0'])) > 3.5
            for k, w in enumerate(l['ws']):
                self.words.append((i, w[0], w[2], w[4], newpar and k == 0))
        self.ntext, self.nmap = '', []
        for j, w in enumerate(self.words):
            t = norm(w[3]); self.ntext += t; self.nmap += [j] * len(t)

    def find(self, phrase):
        k = self.ntext.find(norm(phrase))
        return None if k < 0 else self.nmap[k]

    def sentence_end(self, a):
        """낱말 a에서 시작한 문장의 마지막 낱말 번호."""
        n = len(self.words)
        for j in range(a, n):
            if j + 1 >= n or self.words[j + 1][4]:                 # 쪽이나 문단의 끝
                return j
            t = self.words[j][3]; nx = self.words[j + 1][3]
            core = t.rstrip('”"’\')')
            if not core or core[-1] not in '.:':
                continue
            if not re.match(r'[A-Z(“"‘\[]', nx):
                continue
            stem = core[:-1].strip('(“"')
            if stem in ABBR or stem.endswith('et al') or (re.fullmatch(r'\d+', stem) and (self.words[j][4] or j == a)):
                continue
            return j
        return n - 1

    def par_end(self, a):
        n = len(self.words)
        for j in range(a, n):
            if j + 1 >= n or self.words[j + 1][4]:
                return j
        return n - 1

    def row(self, phrase, every=False):
        """문구가 들어 있는 줄(표의 행) 전체. 글자 그대로 비교한다."""
        out = []
        for i, l in enumerate(self.lines):
            if phrase in ' '.join(w[4] for w in l['ws']):
                js = [j for j, w in enumerate(self.words) if w[0] == i]
                out.append((js[0], js[-1]))
                if not every:
                    break
        return out

    def exact(self, phrase):
        """문구와 낱말이 글자 그대로 같은 곳 모두(표의 칸에 든 짧은 말)."""
        ws = phrase.split(); out = []
        for j in range(len(self.words) - len(ws) + 1):
            if all(self.words[j + k][3] == ws[k] for k in range(len(ws))) and len({self.words[j + k][0] for k in range(len(ws))}) == 1:
                out.append((j, j + len(ws) - 1))
        return out

    def boxes(self, a, b):
        out = {}
        for j in range(a, b + 1):
            i, x0, x1 = self.words[j][:3]
            lo, hi = out.get(i, (x0, x1)); out[i] = (min(lo, x0), max(hi, x1))
        rs = []
        for i, (x0, x1) in sorted(out.items()):
            l = self.lines[i]
            rs.append('BOX:%.2f,%.2f,%.2f,%.2f' % (x0 - 0.8, self.H - l['y1'] + 0.6, x1 + 0.8, self.H - l['y0'] - 0.6))
        return rs


M = json.load(open(MEMO, encoding='utf-8'))
missing, pages = [], {}
for p in M:
    for e in M[p]:
        new = []
        for a in e.get('anchors', []):
            pg = pages.setdefault(p, Page(int(p)))
            m = re.match(r'(RA|R|WA):(.*)', a, re.S)
            if m:
                spans = pg.exact(m.group(2)) if m.group(1) == 'WA' else pg.row(m.group(2), m.group(1) == 'RA')
                if not spans:
                    missing.append((p, a))
                for s0, s1 in spans:
                    new += pg.boxes(s0, s1)
                continue
            line = not a.startswith('S:')
            st = pg.find(a if line else a[2:])
            if st is None:
                missing.append((p, a)); continue
            new += pg.boxes(st, pg.par_end(st) if line else pg.sentence_end(st))
        e['anchors'] = new
json.dump(M, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('boxes', sum(len(e['anchors']) for p in M for e in M[p]), 'missing', missing)
