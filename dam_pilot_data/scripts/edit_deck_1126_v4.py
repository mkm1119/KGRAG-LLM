import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'deck_v3.py' if os.path.exists(os.path.join(HERE, 'deck_v3.py')) else 'edit_deck_1126_v3.py'), encoding='utf-8').read()
exec(src[:src.index('prs = Presentation(SRC)')])      # 도형 함수만 가져온다
prs = Presentation(SRC); S = list(prs.slides); assert len(S) == 24
s15 = S[14]; assert s15.shapes[1].text_frame.text.startswith('질의응답 과정 ①②')

def settext(shape, t):
    rs = shape.text_frame.paragraphs[0].runs; rs[0].text = t
    for r in rs[1:]: r._r.getparent().remove(r._r)
def fill(s, title, sub, parts):
    tree = s.shapes._spTree; els = list(tree)[2:]
    for el in els[3:-1]: tree.remove(el)
    sh = list(s.shapes); assert sh[-1].name == 'Slide Number'
    settext(sh[1], title); settext(sh[2], sub)
    for x in parts:
        for y in (x if isinstance(x, list) else [x]): tree[-1].addprevious(etree.fromstring(y))
def cls(x, y, w, h, color, name):
    """온톨로지의 Class: 흰 바탕에 색 테두리."""
    return [box(x, y, w, h, WHITE, color, 10000), tb(x, y, w, h, name, 1200, 1, color, 'ctr', 'ctr')]

L0, W = 502920, 11155680
P = []
qy = 1690000
P.append(box(L0, qy, W, 400000, NAVY, None, 10000))
P.append(tb(L0 + 200000, qy, 900000, 400000, '질문', 1300, 1, 'BFD9F2', 'l', 'ctr'))
P.append(tb(L0 + 1000000, qy, W - 1200000, 400000, '충주댐 지금 수위가 홍수기 제한수위보다 높아?', 1500, 1, WHITE, 'l', 'ctr'))
ty = qy + 480000; th = 6260000 - ty; lw = 2750000
P.append(box(L0, ty, lw, th, PALE, None, 2759)); P.append(box(L0, ty, lw, 520000, BLUE, None, 8421))
P.append(tb(L0 + 180000, ty, lw - 360000, 520000, '① 질문 해석', 1500, 1, WHITE, 'l', 'ctr'))
P.append(tb(L0 + lw - 900000, ty, 720000, 520000, 'LLM', 1100, 1, SUBW, 'r', 'ctr'))
P.append(tb(L0 + 180000, ty + 640000, lw - 360000, 700000, '질문이 어느 CQ에 해당하는지와 댐, 기간을 뽑아 정해진 형식으로 출력', 1150, 0, GRAY, 'l', 't', 125))
for j, (a, b2) in enumerate([('CQ', 'CQ1 현재 상태\nCQ5 운영기준'), ('댐', '충주댐'), ('기간', '전체')]):
    yy = ty + 1500000 + [0, 780000, 1260000][j]
    P.append(tb(L0 + 180000, yy, 600000, 300000, a, 1200, 1, BLUE))
    P.append(tb(L0 + 800000, yy, lw - 980000, 640000, b2, 1300, 1, NAVY, 'l', 't', 125))
P.append(tb(L0 + 180000, ty + th - 620000, lw - 360000, 520000, 'LLM은 공개된 범용 모델(Qwen3-32B)을 추가 학습 없이 사용', 1000, 0, GRAY, 'l', 't', 120))
rx = L0 + lw + 160000; rw = W - lw - 160000
P.append(ln(L0 + lw + 20000, ty + th // 2, rx - 20000, ty + th // 2, NAVY, 19050))
P.append(box(rx, ty, rw, th, PALE, None, 2759)); P.append(box(rx, ty, rw, 520000, NAVY, None, 8421))
P.append(tb(rx + 180000, ty, 2200000, 520000, '② 근거 조회', 1500, 1, WHITE, 'l', 'ctr'))
P.append(tb(rx + 2000000, ty, rw - 2180000, 520000, '코드   ·   CQ마다 정해 둔 조회 구조에 질문의 댐을 넣어, KG에서 그 부분만 가져옴', 1100, 0, SUBW, 'r', 'ctr'))

ix = rx + 180000; iw = rw - 360000
LB = 1000000; a_w = 1100000; g1 = 850000; b_w = 1750000; g2 = 850000; c_w = 1200000; g3 = 200000
xa = ix + LB; xb = xa + a_w + g1; xc = xb + b_w + g2; xd = xc + c_w + g3; d_w = ix + iw - xd
CH, EH, GAP = 360000, 540000, 300000

def row(y0, tag, name, struct, got):
    P.append(box(ix, y0, 620000, 300000, BLUE, None, 30000)); P.append(tb(ix, y0, 620000, 300000, tag, 1100, 1, WHITE, 'ctr', 'ctr'))
    P.append(tb(ix + 720000, y0, 3000000, 300000, name, 1200, 1, NAVY, 'l', 'ctr'))
    ys = y0 + 370000; ye = ys + CH + GAP
    P.append(tb(ix, ys, LB - 80000, CH, '', anchor='ctr', ln=110, paras=[('조회 구조', 1050, 1, GRAY), ('(Class)', 950, 0, GRAY)]))
    P.append(tb(ix, ye, LB - 80000, EH, '', anchor='ctr', ln=110, paras=[('KG에서', 1050, 1, GRAY), ('가져온 부분', 1050, 1, GRAY)]))
    struct(ys); got(ye)
    return ye + EH
def down(x, ys, ye, label=None):
    P.append(dln(x, ys + CH + 20000, x, ye - 30000))
    if label: P.append(tb(x + 60000, ys + CH + 40000, 1500000, GAP - 80000, label, 950, 1, GRAY, 'l', 'ctr'))

# ---- CQ1
y1 = ty + 600000
def st1(ys):
    P.append(cls(xa, ys, a_w, CH, NAVY, '댐')); P.append(cls(xb, ys, b_w, CH, TEAL, '수문·기상 상태'))
    P.append(ln(xa + a_w, ys + CH // 2, xb - 30000, ys + CH // 2, GRAY, 15875)); P.append(tb(xa + a_w, ys + CH // 2 - 270000, g1, 240000, '상태를 가짐', 1000, 1, GRAY, 'ctr'))
    down(xa + a_w // 2, ys, ys + CH + GAP, '충주댐을 넣음'); down(xb + b_w // 2, ys, ys + CH + GAP)
def got1(ye):
    P.append(ent(xa, ye, a_w, EH, NAVY, '충주댐', tsz=1300))
    P.append(ln(xa + a_w, ye + EH // 2, xb - 30000, ye + EH // 2)); P.append(rel(xa + a_w, ye + EH // 2 - 290000, '상태를 가짐', g1))
    P.append(ent(xb, ye, b_w, EH, TEAL, '수위 등 6개', '열쇠: 1003110', tsz=1300))
    x3 = xb + b_w + 950000
    P.append(ln(xb + b_w, ye + EH // 2, x3 - 30000, ye + EH // 2, TEAL)); P.append(tb(xb + b_w, ye + EH // 2 - 290000, 950000, 260000, '열쇠로 조회', 1050, 1, TEAL, 'ctr'))
    P.append(box(x3, ye, ix + iw - x3, EH, WHITE, TEAL, 8000))
    P.append(tb(x3 + 40000, ye, ix + iw - x3 - 80000, EH, '', algn='ctr', anchor='ctr', ln=110, paras=[('측정 저장소의 가장 최근 시각', 1050, 1, TEAL), ('2026-09-28 23:00  수위 131.6689', 950, 0, INK)]))
end1 = row(y1, 'CQ1', '현재 상태', st1, got1)
P.append(ln(ix, end1 + 95000, ix + iw, end1 + 95000, LINE, 9525, False, False))
# ---- CQ5
def st5(ys):
    P.append(cls(xa, ys, a_w, CH, NAVY, '댐')); P.append(cls(xb, ys, b_w, CH, ORG, '운영기준')); P.append(cls(xc, ys, c_w, CH, EVG, '근거'))
    P.append(ln(xb, ys + CH // 2, xa + a_w + 30000, ys + CH // 2, GRAY, 15875)); P.append(tb(xa + a_w, ys + CH // 2 - 270000, g1, 240000, '적용됨', 1000, 1, GRAY, 'ctr'))
    P.append(ln(xb + b_w, ys + CH // 2, xc - 30000, ys + CH // 2, GRAY, 15875)); P.append(tb(xb + b_w, ys + CH // 2 - 270000, g2, 240000, '근거를 둠', 1000, 1, GRAY, 'ctr'))
    down(xa + a_w // 2, ys, ys + CH + GAP, '충주댐을 넣음'); down(xb + b_w // 2, ys, ys + CH + GAP); down(xc + c_w // 2, ys, ys + CH + GAP)
def got5(ye):
    P.append(ent(xa, ye, a_w, EH, NAVY, '충주댐', tsz=1300))
    P.append(ln(xb, ye + EH // 2, xa + a_w + 30000, ye + EH // 2)); P.append(rel(xa + a_w, ye + EH // 2 - 290000, '적용됨', g1))
    P.append(ent(xb, ye, b_w, EH, ORG, '홍수기 제한수위', '138.0 EL.m', tsz=1300))
    P.append(ln(xb + b_w, ye + EH // 2, xc - 30000, ye + EH // 2)); P.append(rel(xb + b_w, ye + EH // 2 - 290000, '근거를 둠', g2))
    P.append(ent(xc, ye, c_w, EH, EVG, '근거', '열쇠: 별표 3', tsz=1300))
    P.append(ln(xc + c_w, ye + EH // 2, xd - 20000, ye + EH // 2, EVG, 19050))
    P.append(box(xd, ye, d_w, EH, WHITE, EVG, 8000))
    P.append(tb(xd + 20000, ye, d_w - 40000, EH, '', algn='ctr', anchor='ctr', ln=110, paras=[('문서 저장소', 1000, 1, GRAY), ('별표 3 원문', 950, 0, INK)]))
end5 = row(end1 + 190000, 'CQ5', '운영기준', st5, got5)
fill(s15, '질의응답 과정 ①②: 질문 해석과 근거 조회', '시연 질문 하나가 실제로 처리된 과정 (2026-11-15 실행 기록)', P)
prs.save(OUT)
print('bottom', end5, 'panel end', ty + th)
