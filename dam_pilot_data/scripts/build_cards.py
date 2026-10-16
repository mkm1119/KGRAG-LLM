#!/usr/bin/env python3
"""랩미팅 자료의 그림 카드. 이유와 원리는 본문 글로 쓰고, 단계의 적용 과정만 그림으로 그린다.
사용: NODE_PATH=/opt/node22/lib/node_modules python3 scripts/build_cards.py [카드이름 ...]"""
import collections, csv, importlib.util, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('pf', os.path.join(HERE, 'build_poster_figures.py')); pf = importlib.util.module_from_spec(spec); spec.loader.exec_module(pf)
OUT = os.path.join(HERE, '..', '..', 'lab_meeting', 'card_figs'); os.makedirs(OUT, exist_ok=True)
N = os.path.join(HERE, '..', '03_normalized')
pf.tf.OUT = OUT; pf.tf.W = 1000
Svg, INK, NAVY = pf.Svg, pf.INK, pf.NAVY
NOPS, NAPR, NAPR_LINKED = 14, 15, 13
MEAS = 508246
rd = lambda p: list(csv.DictReader(open(os.path.join(N, p), encoding='utf-8-sig')))
ENTS, RELS = rd('kgv4_entities.csv'), rd('kgv4_relations.csv')
EC, RC = collections.Counter(e['class'] for e in ENTS), collections.Counter(r['relation'] for r in RELS)
NE, NR = len(ENTS), len(RELS)
assert (NE, NR) == (264, 418)

# 색: (배경, 테두리)
GRAY = ('#f1f1f1', '#888'); BLUE = ('#e8f1fb', '#4a78b5'); GREEN = ('#e8f6ea', '#4c9a5a'); YEL = ('#fff8dc', '#d9b44a')
ORG = ('#fff3e6', '#e08a1e'); WHITE = ('#fff', '#888'); PURP = ('#f1ebf8', '#7b5ea7'); RED = ('#fdecea', '#b3261e')


def cw(c, size):
    o = ord(c)
    if 0xAC00 <= o <= 0xD7A3 or 0x2E80 <= o <= 0x9FFF or c in '→×≤≥·←↔“”‘’—…①②③④⑤⑥':
        return size * (0.5 if c == '·' else 1.0)
    if c == ' ':
        return size * 0.32
    if c in '.,:;|()[]{}!\'"`-/':
        return size * 0.38
    if c.isupper() or c.isdigit():
        return size * 0.6
    return size * 0.54


def tw(t, size):
    return sum(cw(c, size) for c in t)


def wrap(text, size, maxw):
    out = []
    for para in text.split('\n'):
        cur = ''
        for ch in para:
            if tw(cur + ch, size) > maxw and cur:
                # 단어 중간이면 직전 공백에서 끊는다
                k = cur.rfind(' ')
                if k > 0 and ch != ' ' and tw(cur[:k], size) > maxw * 0.45 and cur[k + 1:] != '':
                    out.append(cur[:k]); cur = cur[k + 1:] + ch
                else:
                    out.append(cur); cur = ch.lstrip()
            else:
                cur += ch
        out.append(cur)
    return out


def lines(g, x, y, texts, size=19, lh=26, bold=False, fill='#222', anchor='start'):
    for i, t in enumerate(texts):
        g.text(x, y + i * lh, t, size, bold, fill, anchor)


def tbox(g, x, y, w, text, size=18, color=GRAY, pad=12, bold=False, fill='#222', minh=0, dash=None, h=None, lh=None, title=None, tsize=None):
    """글이 들어간 상자. 높이는 글에 맞춰 정해진다. h를 주면 그 높이를 쓴다. 반환: 상자 높이"""
    lh = lh or int(size * 1.42)
    ls = wrap(text, size, w - 2 * pad)
    th = 0
    if title:
        tsize = tsize or size + 1
        th = int(tsize * 1.5)
    hh = h or max(minh, 2 * pad + th + len(ls) * lh - (lh - size))
    g.rect(x, y, w, hh, color[0], color[1], 2, dash, 6)
    yy = y + pad + size * 0.85
    if title:
        g.text(x + pad, y + pad + tsize * 0.9, title, tsize, True, NAVY, 'start'); yy = y + pad + th + size * 0.8
    lines(g, x + pad, yy, ls, size, lh, bold, fill)
    return hh


def arrow_h(g, x1, x2, y, color=INK):
    g.line(x1, y, x2, y, color, 'ar', None, 2)


def rows_table(g, y, cols, head, rows, size=17, colors=None, pad=10, gap=6, head_size=16, arrows=False):
    """cols: [(x, w)], head: 열 제목들, rows: 각 행의 칸 글(문자열). 행 높이는 가장 긴 칸에 맞춘다."""
    for (x, w), t in zip(cols, head):
        g.text(x + 4, y + 18, t, head_size, True, '#555', 'start')
    y += 28
    for r in rows:
        hs = [len(wrap(t, size, w - 2 * pad)) for (x, w), t in zip(cols, r)]
        hh = 2 * pad + max(hs) * int(size * 1.42) - int(size * 0.42)
        for i, ((x, w), t) in enumerate(zip(cols, r)):
            c = (colors[i] if colors else GRAY)
            tbox(g, x, y, w, t, size, c, pad, h=hh)
            if arrows and i < len(cols) - 1:
                x2 = cols[i + 1][0]
                if x2 - (x + w) >= 14:
                    g.line(x + w + 1, y + hh // 2, x2 - 2, y + hh // 2, INK, 'ar', None, 2)
        y += hh + gap
    return y


def vtext(g, x, y, t, size=15):
    g.add('<text x="%d" y="%d" font-size="%d" fill="%s" text-anchor="middle" transform="rotate(-90 %d %d)">%s</text>' % (x, y, size, INK, x, y, t))


def pad(g):
    # 가장자리 선이 잘리지 않도록 전체를 약간 줄여 안쪽으로 둔다
    g.p.insert(0, '<g transform="translate(5,5) scale(0.99)">'); g.p.append('</g>'); g.h = int(g.h * 0.99) + 10


def finish(g, y, name):
    g.h = y + 6
    pad(g)
    g.save(name)



def stack(g, y, items, x=0, w=1000, gap=12):
    """items: 함수 목록. 각 함수는 (g, y) -> 다음 y"""
    for f in items:
        y = f(g, y) + gap
    return y


# ---------------------------------------------------------------- 1.3 Ontology 구조 (Class, Relation, Data Property)
def card_1_ontology():
    g = Svg(1000)
    W, H = 390, 0
    cls = {
        'Approval': ('운영행위(방류·수문 운영)에 대한 승인', 'approvalTime, approvalContent', 'CQ4'),
        'Operation': ('실제로 수행된 댐 운영행위', 'operationType, operationTime', 'CQ3'),
        'EvidenceSource': ('상태·운영·승인·기준을 확인할 수 있는 공식 근거자료', 'sourceTitle, sourceType, sourceLocator', 'CQ6'),
        'Criterion': ('특정 Dam에 적용되는 운영기준', 'criterionType, criterionValue, unit', 'CQ5'),
        'Dam': ('댐 운영 의사결정의 대상이 되는 물리적 시설', 'damName, damType', 'CQ1~CQ6'),
        'HydrometeorologicalState': ('댐과 연결되는 수문·기상 변수(강우, 수위, 유입량, 방류량 등)', 'variableType, stationCode', 'CQ1, CQ2')}
    X0, X1 = 50, 560
    pos = {'Approval': (X0, 0), 'Operation': (X0, 1), 'EvidenceSource': (X0, 2), 'Criterion': (X1, 0), 'Dam': (X1, 1), 'HydrometeorologicalState': (X1, 2)}
    heights = {}
    for k, (m, p, c) in cls.items():
        n = len(wrap(m, 16, W - 24))
        heights[k] = 36 + n * 22 + 26 + 30
    rowh = [max(heights[k] for k, (x, r) in pos.items() if r == i) for i in range(3)]
    ytop = [16, 16 + rowh[0] + 80, 16 + rowh[0] + rowh[1] + 80 + 80]
    for k, (m, p, c) in cls.items():
        x, r = pos[k]; y = ytop[r]; h = rowh[r]
        g.rect(x, y, W, h, '#fff', INK, 2, None, 6)
        g.rect(x, y, W, 34, '#e6edf6', INK, 2, None, 6)
        g.text(x + 12, y + 25, k, 21, True, NAVY, 'start')
        g.text(x + W - 12, y + 25, c, 16, False, '#555', 'end')
        ls = wrap(m, 16, W - 24)
        lines(g, x + 12, y + 56, ls, 16, 22, False, '#222')
        g.text(x + 12, y + 56 + len(ls) * 22 + 6, '속성: ' + p, 15, False, '#1f4e79', 'start')
    def mid(k, side):
        x, r = pos[k]; return (x + (W if side == 'r' else 0), ytop[r] + rowh[r] // 2)
    L = lambda *a: g.line(*a, INK, 'ar', None, 2)
    # 세로 관계
    cx0, cx1 = X0 + 140, X1 + 140
    L(cx0, ytop[0] + rowh[0], cx0, ytop[1]); g.text(cx0 + 10, ytop[0] + rowh[0] + 46, 'authorizes', 16, False, INK, 'start')
    L(cx1, ytop[0] + rowh[0], cx1, ytop[1]); g.text(cx1 + 10, ytop[0] + rowh[0] + 46, 'appliesToDam', 16, False, INK, 'start')
    L(cx1, ytop[1] + rowh[1], cx1, ytop[2]); g.text(cx1 + 10, ytop[1] + rowh[1] + 46, 'hasHydrometeorologicalState', 16, False, INK, 'start')
    L(cx0, ytop[1] + rowh[1], cx0, ytop[2]); g.text(cx0 + 10, ytop[1] + rowh[1] + 46, 'supportedBy', 16, False, INK, 'start')
    # 가로 관계
    yy = ytop[1] + rowh[1] // 2
    L(X0 + W, yy, X1, yy); g.text((X0 + W + X1) // 2, yy - 8, 'performedOnDam', 15, False, INK, 'middle', True)
    yy2 = ytop[2] + rowh[2] // 2
    L(X1, yy2, X0 + W, yy2); g.text((X0 + W + X1) // 2, yy2 - 8, 'supportedBy', 15, False, INK, 'middle', True)
    # 9번째 관계 (점선): Approval -> Dam
    g.line(X0 + W, ytop[0] + 60, X1 - 4, ytop[1] + 20, '#b35c00', 'ar', '7 5', 2)
    g.text((X0 + W + X1) // 2, ytop[0] + rowh[0] + 44, 'concernsDam', 15, True, '#b35c00', 'middle', True)
    # supportedBy: Approval(왼쪽 가장자리), Criterion(오른쪽 가장자리) -> EvidenceSource
    ye = ytop[2] + rowh[2] - 20
    g.path('M%d,%d L20,%d L20,%d L%d,%d' % (X0, ytop[0] + 20, ytop[0] + 20, ye, X0 - 2, ye), INK, 'ar', None, 2)
    vtext(g, 12, (ytop[0] + ye) // 2, 'supportedBy')
    g.path('M%d,%d L980,%d L980,%d L%d,%d L%d,%d' % (X1 + W, ytop[0] + 20, ytop[0] + 20, ytop[2] + rowh[2] + 24, X0 + 220, ytop[2] + rowh[2] + 24, X0 + 220, ytop[2] + rowh[2] + 2), INK, 'ar', None, 2)
    vtext(g, 992, (ytop[0] + ye) // 2, 'supportedBy')
    y = ytop[2] + rowh[2] + 46
    g.text(0, y, '실선: 10/02에 설계한 관계 8개. 점선(concernsDam): 단계 5 검증에서 추가한 관계(2.7절). CQ 표시는 그 Class가 필요한 질문이다.', 15, False, '#444', 'start')
    finish(g, y + 12, 'card_1_ontology')


# ---------------------------------------------------------------- 2.1 사용 데이터
def card_2_1():
    g = Svg(1000)
    y = 0
    specs = [
        ('① 방류 승인 기록', '한강홍수통제소 홍수예보 댐방류승인 (공공데이터포털, CSV)', '충주·소양강·횡성·광동 4개 댐 승인 80건 (2010-09 ~ 2021-07)',
         '한 행 = 승인 한 건', ['순차번호 1368 | 관측소 충주 | 승인 2012-08-24', '방류시작 2012-08-24 15:00 | 접수방류량 2000', '비고: 이내 탄력적 조정']),
        ('② 수문기상 시간 자료', 'K-water MyWater', '4개 댐 × 6개 변수(수위, 저수량, 강우량, 유입량, 총방류량, 저수율) 시간별 {0:,}행 (충주·횡성 2010-08~, 소양강 2011-06~, 광동 2016-06~ 2026-09)'.format(MEAS),
         '한 행 = 한 댐의 한 시각', ['댐 코드 1003110 | 시각 라벨 2012082416', '수위 134.18 | 저수량 1697.5206 | 강우량 0', '유입량 1152.728 | 총방류량 944.784 | 저수율 61.7']),
        ('③ 연계운영규정 별표3', '법제처 국가법령정보 (XML)', '댐의 홍수기 제한수위 (현행 판, 시행 2026-07-08)',
         '선 문자로 그린 표가 글자로 들어 있음', ['│한 강 │다목적댐 │소양강댐 │190.3 │-│', '│수 계 │ │충 주 댐 │138.0 │-│', '│ │ │횡 성 댐 │178.2 │-│']),
        ('④ 댐 기본 정보', 'K-water MyWater', '4개 댐의 댐 코드, 이름, 유형',
         '한 행 = 댐 한 곳', ['댐 코드 1003110 | 댐 이름 충주댐', '수계 한강 | 댐 유형 다목적댐'])]
    cw_ = 488
    for i in range(0, 4, 2):
        hh = 0
        for j in (0, 1):
            t, src, rng, st, ex = specs[i + j]
            n1 = len(wrap('출처: ' + src, 16, cw_ - 24)); n2 = len(wrap('범위: ' + rng, 16, cw_ - 24)); n3 = len(wrap(st, 16, cw_ - 24))
            hh = max(hh, 46 + (n1 + n2) * 22 + 12 + n3 * 22 + 12 + len(ex) * 22 + 20)
        for j in (0, 1):
            t, src, rng, st, ex = specs[i + j]
            x = j * (cw_ + 24)
            g.rect(x, y, cw_, hh, '#fff', INK, 2, None, 6); g.rect(x, y, cw_, 36, '#e6edf6', INK, 2, None, 6)
            g.text(x + 12, y + 26, t, 20, True, NAVY, 'start')
            yy = y + 60
            ls = wrap('출처: ' + src, 16, cw_ - 24) + wrap('범위: ' + rng, 16, cw_ - 24)
            lines(g, x + 12, yy, ls, 16, 22); yy += len(ls) * 22 + 8
            g.text(x + 12, yy, st, 16, True, '#1f4e79', 'start') if len(wrap(st, 16, cw_ - 24)) == 1 else lines(g, x + 12, yy, wrap(st, 16, cw_ - 24), 16, 22, True, '#1f4e79')
            yy += len(wrap(st, 16, cw_ - 24)) * 22 + 6
            g.rect(x + 10, yy - 14, cw_ - 20, len(ex) * 22 + 14, '#f6f6f6', '#bbb', 1, None, 4)
            lines(g, x + 18, yy + 4, ex, 15, 22, False, '#333')
        y += hh + 16
    finish(g, y, 'card_2_1')


# ---------------------------------------------------------------- 2.2 구축 절차 개요
def card_2_2():
    g = Svg(1000)
    y = 0
    bw = 150
    def step(x, y, w, h, n, title, doc, color):
        g.rect(x, y, w, h, color[0], color[1], 2, None, 6)
        g.text(x + w / 2, y + 30, n, 18, True, NAVY, 'middle')
        ls = wrap(title, 17, w - 14); lines(g, x + w / 2, y + 56, ls, 17, 22, True, '#222', 'middle')
        lines(g, x + w / 2, y + 62 + len(ls) * 22, wrap(doc, 14, w - 14), 14, 18, False, '#555', 'middle')
    # 위 줄: 전처리 -> (구조화 / 문서) -> 관계 연결 -> 검증 -> 저장
    H1 = 150
    step(0, 60, 150, H1, '단계 1', '전처리', 'DDKG 3.2.1', BLUE)
    step(215, 0, 170, 120, '단계 2', '구조화 자료 매핑', 'OntoDSMS', BLUE)
    step(215, 156, 170, 120, '단계 3', '문서 자료 추출', 'DDKG 3.2.2', BLUE)
    step(450, 60, 160, H1, '단계 4', '관계 연결', 'Noy & McGuinness Step 7, DDKG ⑦, Li 2025', BLUE)
    step(675, 60, 150, H1, '단계 5', '검증', 'DDKG 3.2.3, Noy & McGuinness Step 6', BLUE)
    step(890, 60, 110, H1, '단계 6', '저장', 'DDKG 3.3', BLUE)
    for x1, x2, yy in [(150, 213, 135), (385, 448, 60), (385, 448, 216), (610, 673, 135), (825, 888, 135)]:
        pass
    g.line(150, 100, 213, 60, INK, 'ar', None, 2); g.line(150, 170, 213, 216, INK, 'ar', None, 2)
    g.line(385, 60, 448, 100, INK, 'ar', None, 2); g.line(385, 216, 448, 170, INK, 'ar', None, 2)
    arrow_h(g, 610, 673, 135); arrow_h(g, 825, 888, 135)
    # 입력 / 출력 설명
    y = 296
    g.text(0, y, '자료는 두 가지로 나누어 처리한다', 18, True, '#555', 'start'); y += 12
    h1 = tbox(g, 0, y, 488, '구조화 자료: 열의 의미가 정해진 표\n④ 댐 기본 정보, ① 방류 승인 기록의 앞 열(순차번호~접수방류량), ② 수문기상 시간 자료  →  단계 2', 16, BLUE, 12)
    tbox(g, 512, y, 488, '문서 자료: 값이 글 속에 들어 있는 자료\n① 방류 승인 기록의 비고 열, ③ 연계운영규정 별표3  →  단계 3\n(별표3은 선 문자로 그린 표이지만 규정 글 속에 들어 있어 문서 자료로 본다)', 16, GREEN, 12, h=h1 + 22)
    y += h1 + 22 + 16
    g.text(0, y, '순서: 자료 형태에 맞게 처리(1~4) → 만든 KG를 검증(5) → 저장(6). DDKG(Huang 2026)의 구성(출처와 전처리 → 지식 추출 → 저장)을 따른다.', 15, False, '#444', 'start')
    finish(g, y + 14, 'card_2_2')


# ---------------------------------------------------------------- 2.3 전처리
def card_2_3():
    g = Svg(1000)
    cols = [(0, 215), (235, 450), (705, 295)]
    y = rows_table(g, 0, cols, ('자료', '전처리', '결과'), [
        ('① 방류 승인 기록', '값이 모두 같은 중복 행은 첫 행만 남김 (제거한 행은 로그에 기록)\n→ 4개 댐만 선택', '한강수계 3,929행\n→ 중복 7행 제거 3,922행\n→ 4개 댐 80건'),
        ('② 수문기상 시간 자료', '응답(JSON)을 열 구조가 같은 표로 옮김(변환·보간 없음)\n→ 4개 댐 선택\n→ 24시는 다음날 0시로 읽음, 빈 값은 채우지 않음', '4개 댐 × 6개 변수\n{0:,}행'.format(MEAS)),
        ('③ 연계운영규정 별표3', '규정 XML에서 별표 번호로 별표3 부분만 골라냄', '별표3의 텍스트'),
        ('④ 댐 기본 정보', '4개 댐의 행만 선택', '4개 댐')], 18, [GRAY, BLUE, GREEN], 12, 8, arrows=True)
    y += 4
    g.rect(0, y, 488, 150, '#fff', '#888', 2, '8 5', 6)
    g.text(14, y + 28, '예시 ① 중복 행', 20, True, NAVY, 'start')
    cols2 = [14, 140, 208, 392]
    for x, t in zip(cols2, ['순차번호', '관측소', '방류시작시간', '접수방류량']):
        g.text(x, y + 58, t, 16, True, '#555', 'start')
    for k, (a, col) in enumerate([('2218', INK), ('2220 (제거)', '#b3261e')]):
        yy = y + 86 + k * 28
        for x, t in zip(cols2, [a, '광동', '2016-07-04 18:00', '200']):
            g.text(x, yy, t, 17, False, col, 'start')
    g.text(14, y + 140, '순차번호만 다르고 값이 모두 같아 2220을 제거한다', 17, False, '#444', 'start')
    g.rect(512, y, 488, 150, '#fff', '#888', 2, '8 5', 6)
    g.text(526, y + 28, '예시 ② 시각 라벨 (24시 표기)', 20, True, NAVY, 'start')
    g.text(526, y + 62, '2012082416  →  2012-08-24 16:00', 19, False, INK, 'start')
    g.text(526, y + 92, '2016062924  →  2016-06-30 00:00', 19, False, '#b3261e', 'start')
    lines(g, 526, y + 122, ['라벨 = 날짜 8자리 + 시각 2자리(01~24)', '24시는 그날의 끝이므로 다음날 0시로 읽는다'], 16, 21, False, '#444')
    y += 164
    hh = tbox(g, 0, y, 1000, '확인 필요  시각 라벨 01~24가 “그 시각 직전 한 시간의 값”인지 “그 시각 정각의 값”인지 K-water 자료 설명에서 확인하지 못했다. 지금은 라벨 시각을 그대로 읽는다(±1시간 차이 가능). 확인되면 읽는 규칙만 바꾸면 된다.', 17, ORG, 14, dash='8 5')
    y += hh + 14
    g.text(0, y + 10, '원본 파일은 바꾸지 않고, 정리한 내용은 로그에 남긴다.', 17, False, '#444', 'start')
    finish(g, y + 20, 'card_2_3')



def sect(g, y, t):
    g.text(0, y + 18, t, 19, True, NAVY, 'start')
    return y + 30


def resultbar(g, y, t):
    h = tbox(g, 0, y, 1000, t, 17, GREEN, 12)
    return y + h + 14


# ---------------------------------------------------------------- 2.4 구조화 자료 매핑
def card_2_4():
    g = Svg(1000)
    cols = [(0, 230), (250, 280), (550, 450)]
    y = rows_table(g, 0, cols, ('자료', 'Class와 개체 ID', '열 → Data Property'), [
        ('④ 댐 기본 정보', 'Dam\nDAM:댐코드', '댐 이름(DAM_NM_source) → damName\n댐 유형(DAM_BO_NM_source) → damType'),
        ('① 방류 승인 기록 (한 행)', 'Approval\nAPR:순차번호', '승인년월일시분 → approvalTime\n방류시작시간, 접수방류량, 비고 → approvalContent (한 문장으로 합침)'),
        ('(같은 행)', 'EvidenceSource\nEVI:AP:순차번호', '(자료 출처 고정값) → sourceTitle, sourceType\n순차번호 → sourceLocator'),
        ('② 수문기상 시간 자료 (댐 × 변수)', 'HydrometeorologicalState\nHMS:댐코드:변수', '변수 이름(수위, 저수량, …) → variableType\n댐 코드(DAM_CD) → stationCode (측정값을 찾아가는 키)'),
        ('(같은 시간 자료)', 'EvidenceSource\nEVI:KW:댐코드', '(자료 출처 고정값) → sourceTitle, sourceType\n댐 코드와 이름 → sourceLocator')], 16, [GRAY, BLUE, GREEN], 10, 6, arrows=True)
    y += 8
    y = sect(g, y, '예시: ① 승인 1368 한 행이 이렇게 개체가 된다')
    h1 = tbox(g, 0, y, 330, '순차번호: 1368\n승인년월일시분: 2012-08-24\n방류시작시간: 2012-08-24 15:00\n접수방류량: 2000\n비고: 이내 탄력적 조정', 16, GRAY, 12)
    ha = tbox(g, 380, y, 620, 'APR:1368 (Approval)\napprovalTime = 2012-08-24\napprovalContent = “방류시작 2012-08-24 15:00; 접수방류량 2000㎥/s; 비고: 이내 탄력적 조정”', 16, BLUE, 12)
    hb = tbox(g, 380, y + ha + 8, 620, 'EVI:AP:1368 (EvidenceSource)\nsourceTitle = 환경부 한강홍수통제소 홍수예보 댐방류승인\nsourceType = 승인자료, sourceLocator = 순차번호 1368', 16, GREEN, 12)
    ymid = y + (ha + 8 + hb) // 2
    g.line(332, ymid, 378, ymid, INK, 'ar', None, 2)
    y += max(h1, ha + 8 + hb) + 14
    y = sect(g, y, '시간 자료는 값이 아니라 “어느 댐에 어떤 변수가 있는가”를 개체로 만든다')
    hh = tbox(g, 0, y, 1000, 'HMS:1003110:수위 → variableType = 수위, stationCode = 1003110.   시간별 측정값 {0:,}행은 KG에 넣지 않고 측정자료 저장소에 그대로 두며, 질문이 오면 stationCode와 시각으로 값을 읽는다.'.format(MEAS), 16, YEL, 12)
    y += hh + 14
    y = resultbar(g, y, '결과  이 단계에서 개체 192개가 만들어진다 (Dam 4, Approval 80, 승인 근거자료 80, 상태 24, 측정 근거자료 4).')
    finish(g, y, 'card_2_4')


# ---------------------------------------------------------------- 2.5 문서 자료 추출
def card_2_5():
    g = Svg(1000)
    y = sect(g, 0, 'A. 승인 기록의 비고 → Operation   (한 비고에서 여러 문구가 잡히면 각각 Operation 한 개)')
    cols = [(0, 360), (380, 330), (730, 270)]
    y = rows_table(g, y - 6, cols, ('비고 원문 (승인 순차번호)', '걸리는 문구 (규칙)', 'Operation 종류'), [
        ('(초기수문방류 100㎥/s) (2327)', '“초기방류”, “초기수문방류”', '초기방류'),
        ('10cms 증 (394)', '“증가방류”, “숫자 cms 증”', '증가방류'),
        ('이내 점증방류 (1103)', '“점진”, “점증”', '점진·점증방류'),
        ('9.11 16:00 수문방류종료 (279)', '“방류종료”', '방류종료'),
        ('이내 탄력적 조정 (1368)', '“탄력”', '탄력적 방류'),
        ('수문방류 승인 (473)', '“수문방류”, “이내 방류” 등 일반 방류 문구', '방류 (일반)'),
        ('(비고 없음) (418)', '-', '방류 (일반, 종류 미상)'),
        ('이내 변경승인(기존 500 ㎥/s), 방류 시간 정정', '“변경”, “연장”, “정정”', 'Operation을 만들지 않음 (같은 방류의 변경)')], 15, [GRAY, BLUE, GREEN], 8, 4, arrows=True, head_size=15)
    y += 6
    y = sect(g, y, '운영행위 시각(operationTime): 비고의 시각(정규식), 없으면 방류시작시간')
    cols = [(0, 340), (360, 320), (700, 300)]
    y = rows_table(g, y - 6, cols, ('승인', '비고', 'operationTime'), [
        ('2327 (방류시작 2016-07-16 12:00)', '(초기수문방류 100㎥/s)  시각 없음', '2016-07-16 12:00 (방류시작시간)'),
        ('279 (방류시작 2010-09-10 17:00)', '9.11 16:00 수문방류종료', '2010-09-11 16:00 (비고의 시각)'),
        ('504 (방류시작 2011-06-27 18:00)', '(실제방류는 20시부터)', '2011-06-27 20:00 (비고의 시각)')], 15, [GRAY, BLUE, GREEN], 8, 4, arrows=True, head_size=15)
    y = resultbar(g, y + 2, '결과  승인 80건에서 Operation 68개 (방류 25, 탄력적 방류 25, 초기방류 9, 증가방류 7, 방류종료 1, 점진·점증방류 1)')
    y = sect(g, y + 4, 'B. 별표3 → Criterion   (“│”로 시작하는 줄을 “│” 기준으로 잘라 셀로 읽고, 댐 이름의 공백을 제거)')
    cols = [(0, 360), (380, 330), (730, 270)]
    y = rows_table(g, y - 6, cols, ('별표3 원문 (줄)', '읽은 결과', '만들어지는 Criterion'), [
        ('│한 강 │다목적댐 │소양강댐 │190.3 │-│', '댐 이름 소양강댐, 제한수위 190.3', 'criterionType = 홍수기 제한수위, criterionValue = 190.3, unit = EL.m'),
        ('│수 계 │ │충 주 댐 │138.0 │-│', '“충 주 댐” → 충주댐, 제한수위 138.0', 'criterionValue = 138.0'),
        ('│ │ │횡 성 댐 │178.2 │-│', '“횡 성 댐” → 횡성댐, 제한수위 178.2', 'criterionValue = 178.2'),
        ('(광동댐 줄 없음)', '별표3에 수록되지 않음', 'Criterion 없음')], 15, [GRAY, BLUE, GREEN], 8, 4, arrows=True, head_size=15)
    y = resultbar(g, y + 2, '결과  Criterion 3개 (충주, 소양강, 횡성)')
    y = sect(g, y + 4, 'C. 별표3 원문 → 문서 저장소   (원문은 고치지 않고 두고, KG에는 찾아가는 키만 둔다)')
    cols = [(0, 280), (300, 380), (700, 300)]
    y = rows_table(g, y - 6, cols, ('자료', 'KG 안 (개체와 키)', 'KG 밖 (저장소)'), [
        ('② 수문기상 시간 자료', '상태 개체의 stationCode', '측정자료 저장소: 시간별 측정값'),
        ('③ 별표3', '근거자료 개체의 sourceLocator (예: 별표 3)', '문서 저장소: 별표3 원문 (현행 한 판)')], 15, [GRAY, BLUE, GREEN], 8, 4, arrows=True, head_size=15)
    finish(g, y, 'card_2_5')


# ---------------------------------------------------------------- 2.6 관계 연결 (연결 규칙)
def card_2_6():
    g = Svg(1000)
    y = sect(g, 0, '개체 ID에는 연결에 쓰는 값이 들어 있다')
    cols = [(0, 150), (170, 430), (620, 380)]
    y = rows_table(g, y - 6, cols, ('개체', 'ID 규칙', '연결에 쓰는 값'), [
        ('댐', 'DAM:댐코드', '댐 코드 (K-water의 DAM_CD)'),
        ('승인', 'APR:순차번호', '승인 기록의 관측소코드 (한강홍수통제소 코드)'),
        ('운영행위', 'OPR:승인 순차번호:순번', '만든 승인의 순차번호'),
        ('상태', 'HMS:댐코드:변수', '댐 코드'),
        ('근거자료', 'EVI:AP:순차번호, EVI:KW:댐코드, EVI:LAW:별표3', '만든 자료의 순차번호, 댐 코드')], 15, [GRAY, BLUE, GREEN], 7, 3, head_size=15)
    y = sect(g, y + 6, '관계마다 일치시키는 값과 만들어지는 개수')
    cols = [(0, 255), (265, 185), (460, 465), (935, 65)]
    y = rows_table(g, y - 6, cols, ('관계', '연결하는 개체 쌍', '일치시키는 값', '개수'), [
        ('Approval –concernsDam→ Dam', '승인 한 건과 그 승인이 다루는 댐', '승인 기록의 관측소코드 = 댐 정보의 댐 코드 (1003110 = 1003110). 이름도 같다(관측소명 “충주” = 댐 이름 “충주댐”에서 “댐”을 뺀 것). 4개 댐 모두 해당', str(RC['concernsDam'])),
        ('Approval –authorizes→ Operation', '승인 한 건과 그 비고에서 읽어 만든 운영행위', '승인의 순차번호 = 운영행위 ID의 승인 순차번호 (APR:1368 → OPR:1368:1). 같은 승인 레코드에서 만든 개체', str(RC['authorizes'])),
        ('Operation –performedOnDam→ Dam', '운영행위와 수행된 댐', '운영행위를 만든 승인의 관측소코드 = 댐 코드 (승인 → 댐 연결과 같은 코드)', str(RC['performedOnDam'])),
        ('Dam –hasHydrometeorologicalState→ HMS', '댐과 그 댐의 변수별 상태', '댐 정보의 댐 코드 = 시간 자료의 댐 코드 (같은 기관의 같은 코드 체계)', str(RC['hasHydrometeorologicalState'])),
        ('Criterion –appliesToDam→ Dam', '제한수위와 적용 댐', '별표3의 댐 이름(공백 제거) = 댐 정보의 댐 이름. 별표3에는 코드가 없어 이름이 같다는 것으로 연결', str(RC['appliesToDam'])),
        ('Approval, Operation, HMS, Criterion –supportedBy→ EvidenceSource', '개체와 그것을 만든 자료의 근거자료', '만든 자료가 곧 근거: 승인 → 같은 순차번호의 승인 레코드, Operation → 만든 승인의 순차번호, 상태 → 같은 댐 코드의 측정자료, Criterion → 별표3', str(RC['supportedBy']))],
        14, [GRAY, BLUE, GREEN, WHITE], 8, 4, head_size=15)
    y = sect(g, y + 6, '연결에 쓰는 값의 대응')
    xl, xr, wl = 0, 508, 492
    t1 = tbox(g, xl, y, wl, '① 승인 관측소코드 ↔ 댐 코드 (한강홍수통제소 승인 파일과 K-water 댐 정보)\n1003110, 충주 ↔ 1003110, 충주댐\n1012110, 소양강 ↔ 1012110, 소양강댐\n1006110, 횡성 ↔ 1006110, 횡성댐\n1001210, 광동 ↔ 1001210, 광동댐', 15, GRAY, 10)
    tbox(g, xr, y, wl, '② 별표3 댐 이름 ↔ 댐 이름 (별표3에는 코드가 없다)\n충 주 댐 → 충주댐 ↔ 충주댐\n소양강댐 → 소양강댐 ↔ 소양강댐\n횡 성 댐 → 횡성댐 ↔ 횡성댐\n(광동댐 없음) → 이 관계 없음', 15, GRAY, 10, h=t1)
    y += t1 + 12
    y = resultbar(g, y, '결과  관계 {0}개. 변경·연장·정정 승인과 원 승인을 잇는 관계는 자료에 연결 근거가 없어 만들지 않는다.'.format(NR))
    finish(g, y, 'card_2_6')


# ---------------------------------------------------------------- 2.7 검증
def card_2_7():
    g = Svg(1000)
    y = sect(g, 0, 'A. 구조 검사   (각 검사는 위반 목록을 세어 0건이면 통과)')
    cols = [(0, 215), (225, 565), (800, 200)]
    y = rows_table(g, y - 6, cols, ('검사', '방법', '결과'), [
        ('관계의 양 끝 Class', '관계 유형마다 Ontology가 허용한 (시작 Class, 끝 Class) 쌍과 비교. 예: authorizes는 Approval → Operation만 허용', '모든 관계, 위반 0건'),
        ('필수 Data Property', 'Class별 필수 속성이 개체마다 있는지 확인. 예: Operation은 operationType과 operationTime', '모든 개체, 위반 0건'),
        ('값 형식', 'approvalTime은 YYYY-MM-DD, operationTime은 YYYY-MM-DDThh:mm, criterionValue는 숫자로 읽히는지 확인', 'Approval, Operation, Criterion, 위반 0건'),
        ('근거 연결', '상태, 운영행위, 승인, 운영기준 개체마다 supportedBy 관계가 1개 이상 있는지 확인', '위반 0건'),
        ('경로 일치', '승인이 가리키는 댐(concernsDam)과 그 승인이 허가한 운영행위가 수행된 댐(performedOnDam)이 같은지 비교', 'authorizes 관계, 위반 0건')], 14, [GRAY, BLUE, GREEN], 8, 4, head_size=15)
    y = sect(g, y + 4, 'B. 질문 경로 점검   (CQ마다 Ontology의 경로를 KG에서 실제로 따라가 보고, 답에 필요한 개체가 나오는지 확인)')
    cols = [(0, 190), (200, 330), (540, 460)]
    y = rows_table(g, y - 6, cols, ('CQ', '따라가는 경로', '점검 결과'), [
        ('CQ1 현재 상태', 'Dam → 상태 → 측정자료', '4개 댐 모두 6개 변수 조회, 가장 최근 시각 2026-09-28 23:00'),
        ('CQ2 과거 상태', 'CQ1과 같은 경로', '운영행위 68개 모두 시각의 값 조회 (정각 63개는 1행, 정각이 아닌 5개는 앞뒤 정시 2행)'),
        ('CQ3 과거 운영행위', 'Dam ← performedOnDam ← Operation', '운영행위 68개 (충주 14, 소양강 5, 횡성 22, 광동 27)'),
        ('CQ4 과거 방류 승인', 'Dam ← 승인', '아래 C 참고'),
        ('CQ5 현재 운영기준', 'Criterion → Dam, 별표3 원문', '충주 138.0, 소양강 190.3, 횡성 178.2 EL.m (광동댐은 별표3에 없어 기준 없음)'),
        ('CQ6 공식 근거', '대상 개체 → supportedBy → EvidenceSource', '승인, 운영행위, 상태, 운영기준 모두 근거자료와 연결')], 14, [GRAY, BLUE, GREEN], 8, 4, head_size=15)
    y = sect(g, y + 4, 'C. 발견한 문제와 보완')
    # 보완 전
    bw, bh = 150, 56
    def mini(x0, title, extra, ok):
        g.rect(x0, y, 488, 170, '#fff', '#888', 2, '8 5', 6)
        g.text(x0 + 14, y + 26, title, 18, True, NAVY, 'start')
        for k, (nm, xx) in enumerate([('Approval', 20), ('Operation', 170), ('Dam', 340)]):
            tbox(g, x0 + xx, y + 44, 130, nm, 16, BLUE if nm != 'Dam' else GREEN, 8, h=36)
        g.line(x0 + 150, y + 62, x0 + 170, y + 62, INK, 'ar', None, 2); g.line(x0 + 300, y + 62, x0 + 340, y + 62, INK, 'ar', None, 2)
        g.text(x0 + 160, y + 40, 'authorizes', 12, False, INK, 'middle'); g.text(x0 + 320, y + 40, 'performedOnDam', 12, False, INK, 'middle')
        if extra:
            g.path('M%d,%d L%d,%d L%d,%d L%d,%d' % (x0 + 85, y + 80, x0 + 85, y + 108, x0 + 405, y + 108, x0 + 405, y + 82), '#b35c00', 'ar', '7 5', 2)
            g.text(x0 + 245, y + 102, 'concernsDam (추가)', 13, True, '#b35c00', 'middle', True)
        lines(g, x0 + 14, y + 134, wrap(ok, 15, 462), 15, 20)
    mini(0, '보완 전', False, 'Operation이 없는 승인 17건(변경·연장·정정)은 댐에서 도달할 수 없다. CQ4에서 도달 가능한 승인 63/80건')
    mini(512, '보완 후', True, '승인 기록의 관측소코드와 댐 코드의 일치로 연결(추정 없음). 도달 가능한 승인 80/80건')
    y += 184
    y = resultbar(g, y, '수정된 Ontology  Class 6개(변경 없음), Relation 8개 → 9개 (Approval –concernsDam→ Dam 추가). 예) 승인 1369(횡성, 비고 “방류 시간 정정”)는 Operation이 없어 보완 전에는 댐에서 찾아지지 않았다.')
    finish(g, y, 'card_2_7')


# ---------------------------------------------------------------- 2.8 저장
def card_2_8():
    g = Svg(1000)
    y = sect(g, 0, '1) 단계 2~4의 결과를 표 세 개로 정리  →  2) 표의 행마다 Cypher 명령문을 자동 생성  →  3) Neo4j에 적재')
    w1 = 300
    hs = []
    hs.append(tbox(g, 0, y, w1, '개체 표 (개체 ID | Class | 이름)\nDAM:1003110 | Dam | 충주댐\nAPR:1368 | Approval | 승인 1368 (충주댐)\nOPR:1368:1 | Operation | 충주댐 탄력적 방류 (2012-08-24 15:00)', 14, GRAY, 10))
    hs.append(tbox(g, 0, y + hs[0] + 6, w1, '속성 표 (개체 ID | 속성 | 값)\nDAM:1003110 | damName | 충주댐\nOPR:1368:1 | operationType | 탄력적 방류\nOPR:1368:1 | operationTime | 2012-08-24T15:00', 14, GRAY, 10))
    hs.append(tbox(g, 0, y + hs[0] + hs[1] + 12, w1, '관계 표 (시작 개체 | 관계 | 끝 개체)\nAPR:1368 | authorizes | OPR:1368:1\nAPR:1368 | concernsDam | DAM:1003110', 14, GRAY, 10))
    tot = sum(hs) + 12
    g.line(302, y + tot // 2, 338, y + tot // 2, INK, 'ar', None, 2)
    hc = tbox(g, 340, y, 380, "개체 한 행: 이 ID의 노드를 만들고 속성 값을 붙여라\nMERGE (n:Entity:Dam {id: 'DAM:1003110'})\nSET n.damName = '충주댐', n.damType = '다목적댐';\n\n관계 한 행: 두 노드를 찾아 이 이름의 선으로 이어라\nMATCH (a:Entity {id: 'APR:1368'}), (b:Entity {id: 'OPR:1368:1'})\nMERGE (a)-[r:authorizes]->(b);", 13, BLUE, 10, h=tot)
    g.line(722, y + tot // 2, 758, y + tot // 2, INK, 'ar', None, 2)
    tbox(g, 760, y, 240, 'Neo4j 적재\n같은 ID의 노드가 중복으로 만들어지지 않도록 ID가 유일해야 한다는 제약을 둔다', 15, GREEN, 12, h=tot)
    y += tot + 16
    y = sect(g, y, '4) 측정값 전체와 문서 원문은 Neo4j에 넣지 않고 각 저장소에 둔다. KG에는 찾아가는 키(stationCode, sourceLocator)만 둔다')
    cols = [(0, 230), (250, 440), (710, 290)]
    y = rows_table(g, y - 6, cols, ('저장소', '보관하는 것', '규모와 만든 자료'), [
        ('KG (Neo4j)', '개체와 관계, 근거의 위치(키)', '개체 {0}, 관계 {1}  (① ② ③ ④)'.format(NE, NR)),
        ('측정자료 저장소', '시간별 측정값 전체', '{0:,}행  (②)'.format(MEAS)),
        ('문서 저장소', '규정 원문(별표3 현행)', '1개  (③)')], 15, [GREEN, GRAY, WHITE], 9, 4, head_size=15)
    y += 6
    ec = '   '.join('{0} {1}'.format(k, EC[k]) for k in ('Dam', 'HydrometeorologicalState', 'Approval', 'Operation', 'Criterion', 'EvidenceSource'))
    rc = '   '.join('{0} {1}'.format(k, RC[k]) for k in ('supportedBy', 'concernsDam', 'authorizes', 'performedOnDam', 'hasHydrometeorologicalState', 'appliesToDam'))
    h1 = tbox(g, 0, y, 1000, '개체 ({0}):  {1}'.format(NE, ec), 14, WHITE, 10)
    y += h1 + 6
    h2 = tbox(g, 0, y, 1000, '관계 ({0}):  {1}'.format(NR, rc), 14, WHITE, 10)
    finish(g, y + h2, 'card_2_8')



# ---------------------------------------------------------------- 3.1 전체 흐름
def card_3_1():
    g = Svg(1000)
    cols = [(0, 230), (250, 130), (400, 600)]
    y = rows_table(g, 0, cols, ('단계', '구분', '입력 → 출력'), [
        ('질문 해석', 'LLM', '질문 → 의도와 값(댐, 시점)'),
        ('1 입력 확인', '자동화', '의도와 값 → 확인된 의도와 값 (벗어나면 “범위 밖”)'),
        ('2 KG 조회', '자동화', '의도와 값 → 관련 개체와 찾아가는 키'),
        ('3 외부 저장소 조회', '자동화', '키 → 측정값, 규정 원문'),
        ('4 근거 묶음 구성', '자동화', '찾은 근거 → 출처 번호가 붙은 근거 묶음'),
        ('답변 생성', 'LLM', '질문 + 근거 묶음 → 답변')], 16, [GRAY, WHITE, BLUE], 10, 6, arrows=True)
    y += 10
    w = 485
    h1 = tbox(g, 0, y, w, 'LLM → 자동화\n의도(여러 개 가능)와 값', 16, YEL, 12)
    h2 = tbox(g, 515, y, w, '자동화 → LLM\n근거 묶음과 질문, 그리고 근거 사용 원칙 세 문장', 16, YEL, 12, h=h1)
    y += h1 + 10
    tbox(g, 0, y, 1000, '근거 사용 원칙\n(1) 주어진 근거만 사실로 사용하고, 사실마다 출처 번호를 붙인다.\n(2) 근거를 해석하거나 비교한 내용은 LLM의 판단임을 밝히고, 어떤 근거에서 나온 판단인지 함께 적는다.\n(3) 근거에 없는 내용은 “자료에 없음”이라고 답한다.', 15, GREEN, 12)
    finish(g, y + 142, 'card_3_1')


# ---------------------------------------------------------------- 3.2 의도와 근거 구성
def card_3_2():
    g = Svg(1000)
    y = sect(g, 0, '의도(CQ)마다 따라가는 경로와 가져오는 근거')
    cols = [(0, 190), (205, 450), (670, 330)]
    y = rows_table(g, y - 6, cols, ('의도', '따라가는 경로 (Ontology)', '가져오는 근거'), [
        ('CQ1 현재 상태', 'Dam → hasHydrometeorologicalState → 상태 → stationCode로 측정자료 조회', '저장된 가장 최근 시각의 6개 변수'),
        ('CQ2 과거 상태', 'CQ1과 같은 경로, 시점을 지정', '지정한 시점의 6개 변수. 운영행위와 함께 물으면 그 운영행위 시각의 값'),
        ('CQ3 과거 운영행위', 'Dam ← performedOnDam ← Operation (← authorizes ← Approval)', '운영행위(종류, 시각)와 그것을 허가한 승인'),
        ('CQ4 과거 방류 승인', 'Dam ← concernsDam ← Approval', '승인(승인일, 방류시작, 접수방류량, 비고)'),
        ('CQ5 현재 운영기준', 'Criterion → appliesToDam → Dam, sourceLocator로 문서 조회', '제한수위와 근거(별표3 원문)'),
        ('CQ6 공식 근거', '대상 개체 → supportedBy → EvidenceSource', '출처와 위치(승인 레코드, 측정자료, 별표3)')], 14, [GRAY, BLUE, GREEN], 8, 4, head_size=15)
    y += 4
    tbox(g, 0, y, 1000, '시점: CQ2~CQ4는 하루, 기간, 전체 기간 중 하나 (없으면 전체).   현재: 실시간이 아니라 저장된 가장 최근 시각(2026-09-28 23:00).   여러 의도: 의도마다 근거를 가져와 하나의 근거 묶음으로 합친다.', 14, YEL, 10)
    y += 70
    y = sect(g, y, '예시 질문 → LLM이 뽑은 의도 → 규칙이 가져온 근거 (충주댐, 실제 실행 결과)')
    cols = [(0, 330), (350, 130), (500, 500)]
    y = rows_table(g, y - 6, cols, ('질문의 부분', 'LLM이 뽑은 의도', '규칙이 가져온 근거'), [
        ('현재 수문, 기상 데이터', 'CQ1', '최근 시각(2026-09-28 23:00)의 수위, 저수량, 강우량, 유입량, 총방류량, 저수율'),
        ('제한수위', 'CQ5', '홍수기 제한수위 138.0 EL.m와 별표3 원문'),
        ('비슷한 수문상태일 때의 운영 행위', 'CQ3', '충주댐의 운영행위 {0}개 (종류, 시각)와 그것을 허가한 승인'.format(NOPS)),
        ('비슷한 수문상태일 때의 승인', 'CQ4', '충주댐의 방류 승인 {0}건 (승인일, 방류시작, 접수방류량, 비고)'.format(NAPR)),
        ('그때의 수문상태', '뽑히지 않음', '운영행위 시각의 상태(CQ2)는 이번 실행에서 뽑히지 않아 가져오지 못했다 (5번 실행 중 1번만 포함, 3.8절 한계 2)')],
        14, [GRAY, WHITE, GREEN], 8, 4, head_size=15)
    finish(g, y, 'card_3_2')


# ---------------------------------------------------------------- 3.3 입력 확인
def card_3_3():
    g = Svg(1000)
    y = sect(g, 0, '확인 항목과 기준')
    cols = [(0, 200), (215, 500), (730, 270)]
    y = rows_table(g, y - 6, cols, ('확인 항목', '기준', '어긋날 때'), [
        ('의도', 'CQ1~CQ6 중 하나 이상', '목록에 없는 의도는 “범위 밖”'),
        ('댐', 'KG에 있는 4개 댐 중 하나. 표기는 KG의 이름으로 맞춘다 (충주 → 충주댐)', 'KG에 없는 댐은 “범위 밖”'),
        ('시점 (CQ2~CQ4)', '날짜(2012-08-24), 기간(시작~끝), 전체 중 하나', '형식이 틀리면 “시점 형식 오류”'),
        ('대상 (CQ6)', '대상 종류(승인, 운영행위, 운영기준)와 식별 값', '종류가 목록에 없거나 식별 값이 없으면 오류')], 15, [GRAY, BLUE, YEL], 8, 4, head_size=15)
    y += 4
    y = sect(g, y, '어긋나면 KG를 조회하지 않고 “범위 밖”과 사유를 돌려준다. 통과하면 다음 단계로 넘긴다')
    cols = [(0, 500), (520, 480)]
    y = rows_table(g, y - 6, cols, ('LLM이 넘긴 값', '확인 결과'), [
        ('{"intent": ["CQ1","CQ5","CQ4","CQ3"], "dam": "충주댐", "period": "전체"}', '통과 (예시 질문의 실제 출력)'),
        ('{"intent": ["CQ4"], "dam": "충주", "period": {"at": "2012-08-24"}}', '통과. 댐 표기를 “충주댐”으로 맞춤'),
        ('{"intent": ["CQ4"], "dam": "팔당댐", "period": "전체"}', '범위 밖. 팔당댐은 KG의 4개 댐이 아님'),
        ('{"intent": [], "reason": "팔당댐은 허용된 댐 목록에 없습니다."}', '조회하지 않음. 의도가 비면 사유를 그대로 전한다 (“팔당댐의 현재 수위는?”의 실제 출력)')], 13, [GRAY, GREEN], 8, 4, head_size=15)
    tbox(g, 0, y + 6, 1000, '첫 행과 마지막 행은 서버 실행의 실제 출력이고, 가운데 두 행은 확인 규칙을 보이기 위한 예이다.', 14, WHITE, 8)
    finish(g, y + 52, 'card_3_3')


# ---------------------------------------------------------------- 3.4 KG 조회 (질의 + KG 경로)
def card_3_4():
    g = Svg(1000)
    y = sect(g, 0, '의도마다 미리 만든 Cypher 질의 틀에 단계 1을 통과한 댐과 값만 채워 실행한다')
    cols = [(0, 150), (165, 520), (700, 300)]
    y = rows_table(g, y - 6, cols, ('의도', '질의 틀 (Cypher)', '뜻'), [
        ('CQ1, CQ2', 'MATCH (d:Dam {damName: $dam})-[:hasHydrometeorologicalState]->(h)\nRETURN h.variableType, h.stationCode', '상태 개체에서 변수 종류와 측정값을 찾아가는 키를 가져온다'),
        ('CQ3', 'MATCH (o:Operation)-[:performedOnDam]->(d:Dam {damName: $dam})\nOPTIONAL MATCH (a:Approval)-[:authorizes]->(o)\nRETURN o.id, o.operationType, o.operationTime, a.id, a.approvalTime, a.approvalContent', '그 댐의 운영행위와 허가한 승인을 함께 가져온다'),
        ('CQ4', 'MATCH (a:Approval)-[:concernsDam]->(d:Dam {damName: $dam})\nRETURN a.id, a.approvalTime, a.approvalContent', '그 댐에 관한 승인을 가져온다'),
        ('CQ5', 'MATCH (c:Criterion)-[:appliesToDam]->(d:Dam {damName: $dam})\nRETURN c.id, c.criterionType, c.criterionValue, c.unit', '그 댐에 적용되는 운영기준을 가져온다'),
        ('CQ6', 'MATCH (x:Entity {id: $id})-[:supportedBy]->(e:EvidenceSource)\nRETURN e.id, e.sourceTitle, e.sourceType, e.sourceLocator', '대상 개체의 근거자료를 가져온다')], 12, [GRAY, BLUE, GREEN], 8, 4, head_size=15)
    tbox(g, 0, y + 4, 1000, 'CQ2~CQ4에 시점이 지정되면 WHERE 조건으로 기간을 건다. 전체이면 조건 없이 전부 가져온다. LLM이 질의를 쓰지 않으므로 어떤 질의가 실행되었는지 확인할 수 있고, 같은 입력이면 같은 결과가 나온다.', 14, YEL, 10)
    y += 74
    y = sect(g, y, '예시 질문의 KG 조회 결과: 충주댐에서 따라간 경로')
    # nodes
    cx, cy = 440, y + 150
    tbox(g, cx, cy - 22, 150, 'Dam\n충주댐', 16, GREEN, 8, h=60)
    tbox(g, 40, y + 4, 230, 'APR:1368\n승인일 2012-08-24, 2000㎥/s', 14, BLUE, 8, h=56)
    tbox(g, 40, y + 120, 230, 'OPR:1368:1\n탄력적 방류, 2012-08-24 15:00', 14, BLUE, 8, h=56)
    tbox(g, 40, y + 236, 230, '(변경 승인 {0}건)\nOperation이 없는 승인'.format(NAPR - NAPR_LINKED), 14, GRAY, 8, h=56)
    tbox(g, 730, y + 4, 250, 'Criterion CRI:CR-02\n홍수기 제한수위 138.0 EL.m', 14, YEL, 8, h=56)
    tbox(g, 730, y + 120, 250, '상태 6개 (HMS:1003110:*)\n수위, 저수량, 강우량, 유입량, 총방류량, 저수율\nstationCode 1003110', 13, ORG, 8, h=92)
    g.line(155, y + 60, 155, y + 118, INK, 'ar', None, 2)
    g.text(165, y + 94, 'authorizes', 13, False, INK, 'start')
    g.line(272, y + 148, 438, cy + 8, INK, 'ar', None, 2)
    g.text(300, y + 168, 'performedOnDam', 13, False, INK, 'start')
    g.line(272, y + 38, 438, cy - 10, '#b35c00', 'ar', '7 5', 2)
    g.text(330, y + 62, 'concernsDam', 13, False, '#b35c00', 'start')
    g.line(272, y + 264, 438, cy + 24, '#b35c00', 'ar', '7 5', 2)
    g.line(730, y + 40, 592, cy - 6, INK, 'ar', None, 2)
    g.text(745, y + 100, 'appliesToDam', 13, False, INK, 'start')
    g.line(592, cy + 16, 728, y + 150, INK, 'ar', None, 2)
    g.text(470, y + 214, 'hasHydrometeorologicalState', 13, False, INK, 'start')
    y += 312
    tbox(g, 0, y, 1000, 'CQ4: 충주댐에 관한 승인 {0}건 = 운영행위에 연결된 {1}건 + 변경 승인 {2}건.   CQ3: 운영행위 {3}개와 허가한 승인.   CQ5: 제한수위 138.0.   CQ1: 값이 아니라 측정값을 찾아가는 키만 돌려준다.'.format(NAPR, NAPR_LINKED, NAPR - NAPR_LINKED, NOPS), 14, GREEN, 10)
    finish(g, y + 62, 'card_3_4')


# ---------------------------------------------------------------- 3.5 외부 저장소 조회
def card_3_5():
    g = Svg(1000)
    cols = [(0, 260), (280, 330), (630, 370)]
    y = rows_table(g, 0, cols, ('조회', '키', '가져오는 것'), [
        ('측정자료 저장소', 'stationCode + 시각 라벨', '해당 시각의 6개 변수 값'),
        ('문서 저장소', 'sourceLocator', '별표3 원문')], 16, [GRAY, BLUE, GREEN], 10, 6, arrows=True)
    y += 8
    y = sect(g, y, '시각 규칙 (측정자료는 1시간 간격)')
    w = 485
    h1 = tbox(g, 515, y, w, '운영 시점의 상태(CQ2)\n운영 시각이 정각이면 그 행 1개, 아니면 앞뒤 정시 행 2개. 값은 원값 그대로 주고 어느 쪽이 가까운지, 추세 해석은 LLM이 판단한다', 15, YEL, 10)
    tbox(g, 0, y, w, '현재 상태(CQ1)\n저장된 가장 최근 시각을 쓴다. 충주댐은 2026-09-28 23:00', 15, YEL, 10, h=h1)
    y += h1 + 4
    y += 8
    y = sect(g, y, '충주댐 저장소 조회 결과 (저장소 원값 그대로)')
    cols = [(0, 255), (265, 105), (380, 130), (520, 110), (640, 125), (775, 125), (910, 90)]
    y = rows_table(g, y - 6, cols, ('시각', '수위', '저수량', '강우량', '유입량', '총방류량', '저수율'), [
        ('2026-09-28 23:00 (현재, CQ1)', '131.6689', '1491.3423', '0', '14.402', '0.43', '54.2'),
        ('2012-08-24 15:00 (OPR:1368:1)', '134.17', '1696.772', '0', '1107.905', '692.183', '61.7'),
        ('2018-09-05 14:00 (OPR:3178:1)', '140.8', '2234.156', '0', '1200.388', '715.11', '81.2'),
        ('2020-08-02 18:00 (OPR:3412:1)', '139.55', '2126.472', '1.901', '4945.201', '707.145', '77.3')],
        13, [GRAY, WHITE, WHITE, WHITE, WHITE, WHITE, WHITE], 8, 4, head_size=13)
    tbox(g, 0, y + 4, 1000, '단위: 수위 EL.m, 저수량 MCM, 강우량 mm, 유입량·총방류량 CMS, 저수율 %.  첫 행만 이번 실행에서 CQ1로 가져온 값이다. 나머지 행은 CQ2 조회 규칙을 보이는 예이며, 이번 실행에서는 CQ2가 뽑히지 않아 근거 묶음에 들어가지 않았다.', 13, YEL, 8)
    y += 76
    y = sect(g, y, '정각이 아닌 예: 광동댐 OPR:3365:1 (2020-07-23 16:30) → 앞뒤 정시 두 행')
    cols = [(0, 255), (265, 105), (380, 130), (520, 110), (640, 125), (775, 125), (910, 90)]
    y = rows_table(g, y - 6, cols, ('시각', '수위', '저수량', '강우량', '유입량', '총방류량', '저수율'), [
        ('2020-07-23 16:00', '672.1', '9.2848', '2.5321', '0', '0.5737', '74.07'),
        ('2020-07-23 17:00', '672.1', '9.2848', '4', '0.643', '0.6428', '74.07')],
        13, [GRAY, WHITE, WHITE, WHITE, WHITE, WHITE, WHITE], 8, 4, head_size=13)
    tbox(g, 0, y + 4, 1000, '부동소수 표기 잡음(예: 0.5736666666666667)만 소수 4자리로 정리해서 보여 준다.   별표3 원문은 sourceLocator(별표 3)로 가져오며, 충주댐 제한수위 행(138.0 EL.m)이 포함된 현행 표 전체를 근거로 준다.', 13, WHITE, 8)
    finish(g, y + 66, 'card_3_5')


CARDS = {k[5:]: v for k, v in list(globals().items()) if k.startswith('card_')}
if __name__ == '__main__':
    names = sys.argv[1:] or sorted(CARDS)
    for n in names:
        CARDS[n]()
