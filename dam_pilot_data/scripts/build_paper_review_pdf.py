#!/usr/bin/env python3
"""논문 리뷰용 PDF 만들기: 원문 PDF의 각 페이지 오른쪽을 넓혀 [문단별 해석] 칸과 [빈 메모] 칸을 붙인다. stdlib만 사용.

원문 페이지 내용(글자·그림·링크)은 그대로 두고, 증분 저장(incremental update)으로 페이지 크기와 내용 스트림만 덧붙인다.
그래서 원문 글자를 그대로 선택·형광펜 칠할 수 있다. 분류 방식: 고전 xref 표를 쓰는 PDF(목적 문서: DDKG)만 지원.

사용: python3 build_paper_review_pdf.py <원문.pdf> <해석.json | -> <출력.pdf> [memo]   ('-'이면 빈 메모 칸만, memo이면 json 내용을 메모 칸에 씀)
해석.json: {"1": [{"lead": "원문 문단 첫머리", "ko": "해석"}, ...], "2": [...]}  (lead가 "#"로 시작하면 소제목 줄)
"""
import json, re, struct, sys, zlib

FONT_TTC = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
TRANS_W, MEMO_W = 400.0, 300.0          # 해석 칸, 메모 칸 너비(pt)
PAD = 14.0


# ---------------------------------------------------------------- 글꼴: TTC에서 TTF 하나를 꺼내 쓰는 글리프만 남긴다
class Font:
    def __init__(self, path, index=0):
        b = open(path, 'rb').read()
        off = struct.unpack('>I', b[12 + 4 * index:16 + 4 * index])[0] if b[:4] == b'ttcf' else 0
        n = struct.unpack('>H', b[off + 4:off + 6])[0]
        self.b, self.t = b, {}
        for i in range(n):
            tag, _, o, ln = struct.unpack('>4sIII', b[off + 12 + 16 * i:off + 28 + 16 * i])
            self.t[tag.decode('latin1')] = (o, ln)
        self.upem = struct.unpack('>H', self.tab('head')[18:20])[0]
        self.loca_long = struct.unpack('>h', self.tab('head')[50:52])[0] == 1
        self.nglyph = struct.unpack('>H', self.tab('maxp')[4:6])[0]
        self.nhm = struct.unpack('>H', self.tab('hhea')[34:36])[0]
        hm = self.tab('hmtx')
        self.adv = [struct.unpack('>H', hm[4 * min(i, self.nhm - 1):4 * min(i, self.nhm - 1) + 2])[0] for i in range(self.nglyph)]
        self.cmap = self._cmap()
        lo = self.tab('loca')
        if self.loca_long:
            self.loca = list(struct.unpack('>%dI' % (self.nglyph + 1), lo[:4 * (self.nglyph + 1)]))
        else:
            self.loca = [x * 2 for x in struct.unpack('>%dH' % (self.nglyph + 1), lo[:2 * (self.nglyph + 1)])]

    def tab(self, tag):
        o, ln = self.t[tag]
        return self.b[o:o + ln]

    def _cmap(self):
        c = self.tab('cmap'); n = struct.unpack('>H', c[2:4])[0]; m = {}
        for i in range(n):
            pid, eid, off = struct.unpack('>HHI', c[4 + 8 * i:12 + 8 * i])
            if struct.unpack('>H', c[off:off + 2])[0] == 4 and pid in (0, 3):
                seg = struct.unpack('>H', c[off + 6:off + 8])[0] // 2
                p = off + 14
                ends = struct.unpack('>%dH' % seg, c[p:p + 2 * seg]); p += 2 * seg + 2
                starts = struct.unpack('>%dH' % seg, c[p:p + 2 * seg]); p += 2 * seg
                deltas = struct.unpack('>%dh' % seg, c[p:p + 2 * seg]); ro_pos = p + 2 * seg
                ros = struct.unpack('>%dH' % seg, c[ro_pos:ro_pos + 2 * seg])
                for k in range(seg):
                    for ch in range(starts[k], ends[k] + 1):
                        if ch == 0xFFFF:
                            continue
                        if ros[k] == 0:
                            g = (ch + deltas[k]) & 0xFFFF
                        else:
                            a = ro_pos + 2 * k + ros[k] + 2 * (ch - starts[k])
                            g = struct.unpack('>H', c[a:a + 2])[0]
                            if g:
                                g = (g + deltas[k]) & 0xFFFF
                        if g:
                            m.setdefault(ch, g)
        return m

    def gid(self, ch):
        return self.cmap.get(ord(ch), self.cmap.get(ord('?'), 0))

    def width(self, s, size):
        return sum(self.adv[self.gid(ch)] for ch in s) * size / self.upem

    def subset_ttf(self, gids):
        glyf = self.tab('glyf')
        keep = set(gids) | {0}
        todo = list(keep)
        while todo:                      # 합성 글리프의 부품 글리프도 포함
            g = todo.pop()
            d = glyf[self.loca[g]:self.loca[g + 1]]
            if len(d) >= 10 and struct.unpack('>h', d[:2])[0] < 0:
                p = 10
                while True:
                    flags, comp = struct.unpack('>HH', d[p:p + 4])
                    if comp not in keep:
                        keep.add(comp); todo.append(comp)
                    p += 4 + (4 if flags & 1 else 2)
                    p += 8 if flags & 0x80 else 4 if flags & 0x40 else 2 if flags & 8 else 0
                    if not flags & 0x20:
                        break
        new_glyf, new_loca = bytearray(), []
        for g in range(self.nglyph):
            new_loca.append(len(new_glyf))
            if g in keep:
                d = glyf[self.loca[g]:self.loca[g + 1]]
                new_glyf += d
                new_glyf += b'\0' * ((4 - len(d) % 4) % 4)
        new_loca.append(len(new_glyf))
        head = bytearray(self.tab('head')); head[8:12] = b'\0\0\0\0'; head[50:52] = struct.pack('>h', 1)
        post = self.tab('post')[:32]; post = post[:0] + struct.pack('>I', 0x00030000) + post[4:32]
        tables = {'head': bytes(head), 'hhea': self.tab('hhea'), 'maxp': self.tab('maxp'), 'hmtx': self.tab('hmtx'),
                  'loca': struct.pack('>%dI' % len(new_loca), *new_loca), 'glyf': bytes(new_glyf),
                  'cvt ': self.tab('cvt '), 'OS/2': self.tab('OS/2'), 'name': self.tab('name'), 'post': post}
        tags = sorted(tables)
        out = bytearray(struct.pack('>IHHHH', 0x00010000, len(tags), 0, 0, 0))
        off = 12 + 16 * len(tags); body = bytearray()
        for tg in tags:
            d = tables[tg]
            cs = sum(struct.unpack('>%dI' % ((len(d) + 3) // 4), d + b'\0' * ((4 - len(d) % 4) % 4))) & 0xFFFFFFFF
            out += struct.pack('>4sIII', tg.encode('latin1'), cs, off + len(body), len(d))
            body += d + b'\0' * ((4 - len(d) % 4) % 4)
        return bytes(out + body)


# ---------------------------------------------------------------- 줄바꿈
def wrap(font, text, size, width):
    lines = []
    for para in text.split('\n'):
        line = ''
        for tok in re.findall(r'\S+\s*', para) or ['']:
            if font.width(line + tok.rstrip(), size) <= width:
                line += tok
                continue
            if line:
                lines.append(line.rstrip()); line = ''
            while font.width(tok.rstrip(), size) > width:          # 너무 긴 토큰은 글자 단위로 자름
                k = len(tok)
                while k > 1 and font.width(tok[:k], size) > width:
                    k -= 1
                lines.append(tok[:k]); tok = tok[k:]
            line = tok
        lines.append(line.rstrip())
    return lines


def wrap_ind(font, text, size, width):
    """메모용: 줄 앞 공백은 들여쓰기, '- '·'1. ' 같은 글머리는 내어쓰기로 처리. [(x 이동, 줄)] 반환."""
    out = []
    for para in text.split('\n'):
        n = len(para) - len(para.lstrip(' '))
        body = para.strip()
        ind = n * 4.0
        m = re.match(r'(- |· |\d+\. |[①-⑩] )', body)
        hang = font.width(m.group(1), size) if m else 0
        lines = wrap(font, body, size, width - ind) if not hang else None
        if hang:
            first = wrap(font, body, size, width - ind)
            lines = [first[0]] + wrap(font, body[len(first[0]):].strip(), size, width - ind - hang) if len(first) > 1 else first
            out += [(ind + (hang if i else 0), l) for i, l in enumerate(lines)]
        else:
            out += [(ind, l) for l in lines]
    return out


# ---------------------------------------------------------------- 메모가 가리키는 원문 위치 찾기
COLORS = [(0.85, 0.33, 0.31), (0.20, 0.47, 0.75), (0.30, 0.62, 0.35), (0.85, 0.55, 0.15), (0.55, 0.38, 0.70), (0.15, 0.60, 0.62), (0.60, 0.45, 0.30)]


def norm(t):
    return re.sub(r'[^a-z0-9]', '', t.lower())


def anchor_finder(src, W):
    """문구가 시작하는 줄을 찾고, 그 문단이 끝나는 곳까지 형광펜 칠할 사각형들을 만든다.
    문단의 끝: 다음 줄이 들여쓰기되었거나(새 문단), 줄 간격이 크게 벌어지거나(제목·그림), 글자 크기가 바뀌는 곳.
    왼쪽 열 끝까지 이어지면 오른쪽 열 맨 위에서 계속한다."""
    from pdf_text_extract2 import PDF
    from pdf_text_positions import lines
    pdf = PDF(src); pages = pdf.pages()
    COLS = ((37.6, 289.0), (306.6, 557.7))

    def colof(x):
        return 0 if x < W / 2 - 10 else 1

    def find(pi, phrase):
        start = phrase.startswith('^'); ph = norm(phrase.lstrip('^'))
        ls = [l for l in lines(pdf, pages[pi - 1]) if l[1] < 745]          # 머리말(저자·학술지명) 제외
        full = []                                  # 열을 무시하고 같은 높이의 줄을 합친 것(가운데 정렬된 그림 제목 등)
        for l in sorted(ls, key=lambda l: (-round(l[1]), l[0])):
            if full and abs(full[-1][1] - l[1]) < 2:
                full[-1] = (full[-1][0], full[-1][1], full[-1][2], full[-1][3] + l[3])
            else:
                full.append(tuple(l))
        bycol = [sorted([l for l in ls if colof(l[0]) == c], key=lambda l: -l[1]) for c in (0, 1)]
        for col in (0, 1, 2):
            cl = full if col == 2 else bycol[col]
            text, offs = '', []
            for l in cl:
                offs.append(len(text)); text += norm(l[3])
            k = text.find(ph)
            while k >= 0:
                if not start or k in offs:
                    j = max(i for i, o in enumerate(offs) if o <= k)
                    line = cl[j]
                    if col == 2:                   # 두 열에 걸친 줄(초록, 그림 제목): 같은 왼쪽 끝으로 이어지는 줄까지
                        rows = [l for l in full if l[2] >= 6.6]
                        k0 = next(i for i, l in enumerate(rows) if l[1] <= line[1] + 0.5)
                        seq = [rows[k0]]
                        for l in rows[k0 + 1:]:
                            if abs(l[0] - line[0]) > 6 or seq[-1][1] - l[1] > l[2] * 2.0 or abs(l[2] - seq[-1][2]) > 0.5:
                                break
                            seq.append(l)
                        frac = (k - offs[j]) / max(1, len(norm(line[3])))
                        R0 = 557.7
                        rects = []
                        for n, l in enumerate(seq):
                            x0 = l[0] + (frac * (R0 - l[0]) if n == 0 else 0)
                            x1 = min(R0, l[0] + len(l[3]) * l[2] * 0.53) if n == len(seq) - 1 else R0   # 그림 제목은 띄어쓰기가 빠져 뽑히므로 넉넉히
                            rects.append((x0 - 1, l[1] - l[2] * 0.25, max(x0 + 4, x1 + 1), l[1] + l[2] * 0.85))
                        return line, rects
                    frac = (k - offs[j]) / max(1, len(norm(line[3])))
                    return line, span(bycol, col, line, frac)
                k = text.find(ph, k + 1)
        return None

    def span(bycol, col, first, frac):
        body = [[l for l in bycol[c] if l[2] >= 6.6] for c in (0, 1)]
        seq = []                                   # (열, 줄)
        c = col
        rows = body[c]
        k = next(i for i, l in enumerate(rows) if l[1] <= first[1] + 0.5)
        prev = None
        while True:
            if k >= len(rows):
                if c == 0 and body[1] and prev is not None and prev[2] >= 7.6:   # 왼쪽 열 끝 → 오른쪽 열 맨 위로(본문일 때만)
                    c, rows = 1, body[1]
                    # 오른쪽 열에서 같은 크기 본문의 첫 줄부터(그 위의 그림 글자는 건너뜀)
                    k = next((i for i, r in enumerate(rows) if abs(r[2] - prev[2]) < 0.3 and COLS[1][0] - 1 <= r[0] <= COLS[1][0] + 13), len(rows))
                    if k >= len(rows) or rows[k][0] > COLS[1][0] + 6:  # 오른쪽 열이 새 문단으로 시작하면 끝
                        break
                    prev = None
                    continue
                break
            l = rows[k]
            if prev is not None:
                L0 = COLS[c][0]
                if l[0] > L0 + 6 or prev[1] - l[1] > prev[2] * 2.0 or abs(l[2] - prev[2]) > 0.5:
                    # 왼쪽 열에서 끊겼는데 그 아래에 같은 크기의 본문 줄이 더 없으면(그림·표·각주뿐) 오른쪽 열로 이어진다
                    rest = rows[k:]
                    bodylike = [r for r in rest if abs(r[2] - prev[2]) < 0.3 and L0 - 1 <= r[0] <= L0 + 13]
                    if c == 0 and not bodylike and prev[2] >= 7.6 and l[0] <= L0 + 6 and body[1]:
                        k = len(rows); continue
                    if c == 0 and not bodylike and prev[2] >= 7.6 and body[1]:
                        k = len(rows); continue
                    break
            seq.append((c, l)); prev = l; k += 1
        rects = []
        for n, (c, l) in enumerate(seq):
            L0, R0 = COLS[c]
            last = n == len(seq) - 1
            x0 = l[0] + (frac * (R0 - l[0]) if n == 0 else 0)
            x1 = min(R0, l[0] + len(l[3]) * l[2] * 0.47) if last else R0
            rects.append((x0 - 1, l[1] - l[2] * 0.25, max(x0 + 4, x1 + 1), l[1] + l[2] * 0.85))
        return rects
    return find


def circle(cx, cy, r):
    k = 0.5523 * r
    return (b'%.2f %.2f m %.2f %.2f %.2f %.2f %.2f %.2f c %.2f %.2f %.2f %.2f %.2f %.2f c %.2f %.2f %.2f %.2f %.2f %.2f c %.2f %.2f %.2f %.2f %.2f %.2f c f'
            % (cx + r, cy, cx + r, cy + k, cx + k, cy + r, cx, cy + r, cx - k, cy + r, cx - r, cy + k, cx - r, cy,
               cx - r, cy - k, cx - k, cy - r, cx, cy - r, cx + k, cy - r, cx + r, cy - k, cx + r, cy))


# ---------------------------------------------------------------- PDF 증분 저장
def main(src, tjson, dst, mode='review'):
    b = open(src, 'rb').read()
    global TRANS_W, MEMO_W
    memo = mode == 'memo'
    if memo:                      # 메모 칸에 메모 내용을 써 넣음(해석 칸 없음)
        tr, TRANS_W, MEMO_W = json.load(open(tjson, encoding='utf-8')), 0.0, 420.0
    elif tjson == '-':
        tr, TRANS_W, MEMO_W = {}, 0.0, 360.0
    else:
        tr = json.load(open(tjson, encoding='utf-8'))
    objs = {}
    for m in re.finditer(rb'(?<![\d])(\d+)\s+0\s+obj\b(.*?)endobj', b, re.S):
        objs[int(m.group(1))] = m.group(2)
    sx = int(re.findall(rb'startxref\s+(\d+)', b)[-1])
    trailer = re.search(rb'trailer\s*<<(.*?)>>\s*startxref', b[sx:], re.S).group(1)
    root = re.search(rb'/Root\s+(\d+) 0 R', trailer).group(0)
    info = re.search(rb'/Info\s+\d+ 0 R', trailer)
    idm = re.search(rb'/ID\s*\[[^\]]*\]', trailer)
    size = max(int(x) for x in re.findall(rb'/Size\s+(\d+)', b))
    pages_ref = int(re.search(rb'/Pages\s+(\d+) 0 R', objs[int(re.search(rb'(\d+)', root.split()[1]).group(1))]).group(1))

    def kids(n):
        d = objs[n]
        if re.search(rb'/Type\s*/Page\b(?!s)', d):
            return [n]
        return [p for k in re.findall(rb'(\d+) 0 R', re.search(rb'/Kids\s*\[(.*?)\]', d, re.S).group(1)) for p in kids(int(k))]
    pages = kids(pages_ref)

    font = Font(FONT_TTC)
    used = set(' ?…·“”')
    for v in tr.values():
        for e in v:
            used |= set(e.get('lead', '')) | set(e['ko'])
    used |= set('해석메모쪽원문문단 ()0123456789/p.-')
    new = {}
    nxt = [size]

    def add(data):
        n = nxt[0]; nxt[0] += 1; new[n] = data; return n

    def stream(dct, data, compress=True):
        if compress:
            data = zlib.compress(data, 9); dct += b' /Filter /FlateDecode'
        return b'<< ' + dct + b' /Length %d >>\nstream\n' % len(data) + data + b'\nendstream'

    gids = sorted({font.gid(c) for c in used})
    ttf = font.subset_ttf(gids)
    ff = add(stream(b'/Length1 %d' % len(ttf), ttf))
    fd = add(b'<< /Type /FontDescriptor /FontName /WQYZenHei /Flags 4 /FontBBox [-50 -200 1050 950] /ItalicAngle 0 '
             b'/Ascent 880 /Descent -120 /CapHeight 700 /StemV 80 /FontFile2 %d 0 R >>' % ff)
    w = b' '.join(b'%d [%d]' % (g, round(font.adv[g] * 1000 / font.upem)) for g in gids)
    cid = add(b'<< /Type /Font /Subtype /CIDFontType2 /BaseFont /WQYZenHei /CIDSystemInfo << /Registry (Adobe) /Ordering (Identity) /Supplement 0 >> '
              b'/FontDescriptor %d 0 R /CIDToGIDMap /Identity /DW 1000 /W [%s] >>' % (fd, w))
    rev = {}
    for c in used:
        rev.setdefault(font.gid(c), c)
    bf = '\n'.join('<%04X> <%s>' % (g, ''.join('%04X' % u for u in struct.unpack('>%dH' % (len(rev[g].encode('utf-16-be')) // 2), rev[g].encode('utf-16-be'))))
                   for g in gids if g in rev)
    tu = ('/CIDInit /ProcSet findresource begin 12 dict begin begincmap /CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def '
          '/CMapName /Adobe-Identity-UCS def /CMapType 2 def 1 begincodespacerange <0000> <FFFF> endcodespacerange\n'
          '%d beginbfchar\n%s\nendbfchar endcmap CMapName currentdict /CMap defineresource pop end end' % (len(rev), bf)).encode()
    tun = add(stream(b'', tu))
    f0 = add(b'<< /Type /Font /Subtype /Type0 /BaseFont /WQYZenHei /Encoding /Identity-H /DescendantFonts [%d 0 R] /ToUnicode %d 0 R >>' % (cid, tun))
    qs = add(stream(b'', b'q\n', False))
    Qs = add(stream(b'', b'Q\n', False))

    def tj(s):
        return b'<' + ''.join('%04X' % font.gid(c) for c in s).encode() + b'> Tj'

    overflow = []; missing = []
    finder = anchor_finder(src, 595.0) if memo else None
    marks = []
    _sp = {}

    def sent_page(pi):
        if pi not in _sp:
            from pdf_sentences import Page, PDF as _P
            if '_pdf' not in _sp:
                _sp['_pdf'] = _P(src)
            _sp[pi] = Page(_sp['_pdf'], _sp['_pdf'].pages()[pi - 1])
        return _sp[pi]
    for pi, pn in enumerate(pages, 1):
        d = objs[pn]
        mb = [float(x) for x in re.search(rb'/MediaBox\s*\[([^\]]*)\]', d).group(1).split()]
        x0, y0, W, H = mb
        X1 = W + PAD if not memo else W + PAD   # 글을 쓰는 칸 시작
        X2 = W + TRANS_W                   # 메모 칸 시작
        WT = W + TRANS_W + MEMO_W
        entries = tr.get(str(pi), [])
        num = 0
        for e in entries:
            if e.get('anchors'):
                num += 1; e['_n'] = num
        # 글자 크기를 줄여 가며 한 페이지에 맞춤
        TW = (MEMO_W if memo else TRANS_W) - 2 * PAD
        WR = (lambda t, sz, w: wrap_ind(font, t, sz, w)) if memo else (lambda t, sz, w: [(0, l) for l in wrap(font, t, sz, w)])
        for size in (7.6, 7.2, 6.8, 6.4, 6.0, 5.6, 5.2, 4.8):
            lead_size = size - 0.8; lh = size * 1.38
            blocks = []
            for e in entries:
                lead = e.get('lead', '')
                if lead.startswith('#'):
                    nb = e.get('_n')
                    blocks.append(('h', [(dx + (13 if nb else 0), l) for dx, l in WR(lead[1:].strip(), size + 0.6, TW - (13 if nb else 0))], size + 0.6, nb))
                    if e['ko']:
                        blocks.append(('k', WR(e['ko'], size, TW), size))
                    continue
                if lead:
                    blocks.append(('l', WR('¶ ' + lead, lead_size, TW), lead_size))
                blocks.append(('k', WR(e['ko'], size, TW), size))
            need = sum(len(L) * s * 1.38 + (3.5 if k == 'k' else 1.5 if k == 'l' else 3) for k, L, s, *_ in blocks)
            if need <= H - 62:
                break
        else:
            overflow.append(pi)
        c = []
        c.append(b'q 1 1 1 rg %.2f 0 %.2f %.2f re f Q' % (W, TRANS_W + MEMO_W, H))
        c.append(b'q 0.55 0.55 0.6 RG 0.6 w %.2f 0 m %.2f %.2f l S Q' % (W, W, H))
        y = H - 26
        if TRANS_W:
            c.append(b'q 0.97 0.975 0.985 rg %.2f 0 %.2f %.2f re f Q' % (W, TRANS_W, H))
            c.append(b'q 0.55 0.55 0.6 RG 0.6 w %.2f 0 m %.2f %.2f l S Q' % (X2, X2, H))
            c.append(b'BT /FKR 8.5 Tf 0.12 0.23 0.37 rg %.2f %.2f Td %s ET' % (X1, y, tj('해석 (p.%d)' % pi)))
        c.append(b'BT /FKR 8.5 Tf 0.12 0.23 0.37 rg %.2f %.2f Td %s ET' % (X2 + PAD, y, tj('메모' + (' (p.%d)' % pi if memo else ''))))
        y -= 16
        for kind, L, s, *nb in blocks:
            col = {'h': b'0.12 0.23 0.37', 'l': b'0.45 0.45 0.5', 'k': b'0.1 0.1 0.1'}[kind]
            if nb and nb[0]:
                r_, g_, b_ = COLORS[(nb[0] - 1) % len(COLORS)]
                c.append(b'q %.2f %.2f %.2f rg %s Q' % (r_, g_, b_, circle(X1 + 5, y - s * 1.38 + s * 0.35, 5.2)))
                c.append(b'BT /FKR 6.2 Tf 1 1 1 rg %.2f %.2f Td %s ET' % (X1 + 5 - font.width(str(nb[0]), 6.2) / 2, y - s * 1.38 + s * 0.35 - 2.1, tj(str(nb[0]))))
            for dx, line in L:
                y -= s * 1.38
                c.append(b'BT /FKR %.2f Tf %s rg %.2f %.2f Td %s ET' % (s, col, X1 + dx, y, tj(line)))
            y -= 3.5 if kind == 'k' else 1.5 if kind == 'l' else 3
        hl = []                                # 원문 아래에 깔 형광펜(글자보다 먼저 그림)
        for e in entries:                      # 원문 쪽에 같은 번호 표시
            if not e.get('_n'):
                continue
            r_, g_, b_ = COLORS[(e['_n'] - 1) % len(COLORS)]
            tint = tuple(1 - 0.30 * (1 - v) for v in (r_, g_, b_))
            spans = []                         # 문장 단위 표시: (시작, 끝)
            for a in e['anchors']:
                if a.startswith('S:'):
                    pg = sent_page(pi)
                    st = pg.find(a[2:])
                    if st is None:
                        missing.append((pi, a)); continue
                    spans.append((st, pg.sentence_end(st)))
                    continue
                hit = finder(pi, a)            # 그림·표 제목, 초록 등은 줄 단위
                if not hit:
                    missing.append((pi, a)); continue
                (lx, ly, lsz, _), rects = hit
                hl.append(b'%.3f %.3f %.3f rg ' % tint + b' '.join(b'%.2f %.2f %.2f %.2f re' % (x0, y0, x1 - x0, y1 - y0) for x0, y0, x1, y1 in rects) + b' f')
                marks.append((lx, ly, lsz))
            prev = None
            for st, en in sorted(spans):
                rects, first = sent_page(pi).rects(st, en)
                hl.append(b'%.3f %.3f %.3f rg ' % tint + b' '.join(b'%.2f %.2f %.2f %.2f re' % (x0, y0, x1 - x0, y1 - y0) for x0, y0, x1, y1 in rects) + b' f')
                if prev is None or st - prev > 2:      # 이어지는 문장이면 번호를 다시 찍지 않음
                    marks.append((306.6 if first[0] >= 297.6 else 37.6, first[1], first[2]))   # 번호는 그 줄의 열 왼쪽 여백에
                prev = en
            for lx, ly, lsz in marks:
                cx, cy = lx - 7.5, ly + lsz * 0.35
                c.append(b'q %.2f %.2f %.2f rg %s Q' % (r_, g_, b_, circle(cx, cy, 5.0)))
                c.append(b'BT /FKR 6.0 Tf 1 1 1 rg %.2f %.2f Td %s ET' % (cx - font.width(str(e['_n']), 6.0) / 2, cy - 2.0, tj(str(e['_n']))))
            marks.clear()
        cs = add(stream(b'', b'\n'.join(c)))
        # 페이지 사전 고치기
        nd = d
        for box in (rb'/MediaBox', rb'/CropBox', rb'/BleedBox', rb'/TrimBox', rb'/ArtBox'):
            nd = re.sub(box + rb'\s*\[[^\]]*\]', box + b' [%g %g %.3f %g]' % (x0, y0, WT, H), nd)
        cm = re.search(rb'/Contents\s*(\[[^\]]*\]|\d+ 0 R)', nd)
        inner = cm.group(1)[1:-1] if cm.group(1).startswith(b'[') else cm.group(1)
        pre = (b'%d 0 R ' % add(stream(b'', b'q ' + b'\n'.join(hl) + b' Q'))) if hl else b''
        nd = nd[:cm.start()] + b'/Contents [%s%d 0 R %s %d 0 R %d 0 R]' % (pre, qs, inner.strip(), Qs, cs) + nd[cm.end():]
        rm = re.search(rb'/Resources\s*(\d+) 0 R', nd)
        if rm:                                   # 참조된 자원 사전은 복사해서 고친다
            res = objs[int(rm.group(1))].strip()
            res = add(add_font(res, f0))
            nd = nd[:rm.start()] + b'/Resources %d 0 R' % res + nd[rm.end():]
        else:
            m = re.search(rb'/Resources\s*<<', nd)
            nd = nd[:m.start()] + add_font_inline(nd[m.start():], f0, objs)
        new[pn] = nd.strip()

    out = bytearray(b)
    if not out.endswith(b'\n'):
        out += b'\n'
    offs = {}
    for n in sorted(new):
        offs[n] = len(out)
        out += b'%d 0 obj\n' % n + new[n] + b'\nendobj\n'
    xref = len(out)
    out += b'xref\n'
    ns = sorted(offs)
    i = 0
    while i < len(ns):
        j = i
        while j + 1 < len(ns) and ns[j + 1] == ns[j] + 1:
            j += 1
        out += b'%d %d\n' % (ns[i], j - i + 1)
        for n in ns[i:j + 1]:
            out += b'%010d 00000 n\r\n' % offs[n]
        i = j + 1
    out += b'trailer\n<< /Size %d %s %s %s /Prev %d >>\nstartxref\n%d\n%%%%EOF\n' % (
        nxt[0], root, info.group(0) if info else b'', idm.group(0) if idm else b'', sx, xref)
    open(dst, 'wb').write(out)
    print('pages', len(pages), 'font glyphs', len(gids), 'subset KB', len(ttf) // 1024, 'overflow pages', overflow)
    for pm in missing:
        print('원문 위치를 못 찾음:', pm)


def add_font(res, f0):
    m = re.search(rb'/Font\s*<<', res)
    if m:
        return res[:m.end()] + b' /FKR %d 0 R ' % f0 + res[m.end():]
    return res.replace(b'<<', b'<< /Font << /FKR %d 0 R >> ' % f0, 1)


def add_font_inline(s, f0, objs):
    """s는 '/Resources <<'로 시작하는 뒷부분. 자원 사전 안의 /Font에 FKR을 더한다."""
    m = re.search(rb'/Font\s*<<', s)
    depth_end = matching(s, s.index(b'<<'))
    if m and m.start() < depth_end:
        return s[:m.end()] + b' /FKR %d 0 R ' % f0 + s[m.end():]
    m = re.search(rb'/Font\s*(\d+) 0 R', s)
    if m and m.start() < depth_end:
        fd = objs[int(m.group(1))].strip()
        fd = fd.replace(b'<<', b'<< /FKR %d 0 R ' % f0, 1)
        return s[:m.start()] + b'/Font ' + fd + s[m.end():]
    k = s.index(b'<<') + 2
    return s[:k] + b' /Font << /FKR %d 0 R >> ' % f0 + s[k:]


def matching(s, i):
    depth = 0
    while i < len(s):
        if s[i:i + 2] == b'<<':
            depth += 1; i += 2; continue
        if s[i:i + 2] == b'>>':
            depth -= 1; i += 2
            if depth == 0:
                return i
            continue
        i += 1
    return len(s)


if __name__ == '__main__':
    main(*sys.argv[1:5])
