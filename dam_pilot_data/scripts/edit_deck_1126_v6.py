import sys, os, csv, collections
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'deck_v3.py' if os.path.exists(os.path.join(HERE, 'deck_v3.py')) else 'edit_deck_1126_v3.py'), encoding='utf-8').read()
exec(src[:src.index('prs = Presentation(SRC)')])
CSV = sys.argv[3]
R = list(csv.DictReader(open(CSV, encoding='utf-8-sig'))); assert len(R) == 82
by = {r['번호']: r for r in R}; cnt = collections.Counter(r['업무 영역'] for r in R)
areas = list(dict.fromkeys(r['업무 영역'] for r in R)); assert len(areas) == 11
pick = [('A04', 'A07'), ('B04', 'B09'), ('C02', 'C05'), ('D03', 'D02'), ('E02', 'E01'), ('F05', 'F04'), ('G01', 'G06'), ('H01', 'H05'), ('I04', 'I05'), ('J03', 'J02'), ('K03', 'K01')]
prs = Presentation(SRC); S = list(prs.slides); assert len(S) == 24
base = S[22]; assert base.shapes[1].text_frame.text.startswith('향후 계획: CQ 실무자 설문')
def settext(shape, t):
    rs = shape.text_frame.paragraphs[0].runs; rs[0].text = t
    for r in rs[1:]: r._r.getparent().remove(r._r)
L0, W = 502920, 11155680
P = []
cw = [2300000, 3250000, 3250000, 850000, 750000, 755680]; cx = [L0]
for c in cw[:-1]: cx.append(cx[-1] + c)
y = 1700000; hh = 380000; rh = 320000
P.append(box(L0, y, W, hh, NAVY, None, 6000))
for k, t in enumerate(['업무 영역', '질문 예시 1', '질문 예시 2', '후보 수', '필요', '불필요']):
    P.append(tb(cx[k] + (150000 if k < 3 else 0), y, cw[k] - (200000 if k < 3 else 0), hh, t, 1200, 1, WHITE, 'l' if k < 3 else 'ctr', 'ctr'))
y += hh + 30000
for i, (area, (a, b)) in enumerate(zip(areas, pick)):
    assert by[a]['업무 영역'] == area and by[b]['업무 영역'] == area
    yy = y + i * rh
    P.append(box(L0, yy, W, rh - 30000, PALE if i % 2 == 0 else WHITE, PALE, 3000))
    P.append(tb(cx[0] + 150000, yy, cw[0] - 200000, rh - 30000, area, 1150, 1, NAVY, 'l', 'ctr'))
    P.append(tb(cx[1] + 150000, yy, cw[1] - 200000, rh - 30000, by[a]['사용자 요청 예'], 1050, 0, INK, 'l', 'ctr'))
    P.append(tb(cx[2] + 150000, yy, cw[2] - 200000, rh - 30000, by[b]['사용자 요청 예'], 1050, 0, INK, 'l', 'ctr'))
    P.append(tb(cx[3], yy, cw[3], rh - 30000, '%d개' % cnt[area], 1100, 0, GRAY, 'ctr', 'ctr'))
    for k in (4, 5):
        P.append(box(cx[k] + cw[k] // 2 - 90000, yy + (rh - 30000) // 2 - 90000, 180000, 180000, WHITE, GRAY, 1000, rect=True))
yb = y + 11 * rh + 20000
P.append(box(L0, yb, W, 340000, WHITE, BLUE, 6000))
P.append(tb(L0 + 150000, yb, W - 300000, 340000, '**목록에 없는 질문 (부족한 것)**      실무에서 실제로 생기는 질문을 직접 적는 칸', 1150, 0, INK, 'l', 'ctr'))
P.append(tb(L0, 6040000, W, 240000, '고안 중인 초안의 일부이며, 질문의 수와 표현은 설문 전까지 바뀔 수 있음.  전체 후보 82개 (11개 업무 영역)', 1000, 0, GRAY, 'l', 'ctr'))
import copy
s = prs.slides.add_slide(base.slide_layout); tree = s.shapes._spTree
for sp in list(tree)[2:]: tree.remove(sp)
srcs = list(base.shapes._spTree)
for el in srcs[2:5]: tree.append(copy.deepcopy(el))
tree.append(copy.deepcopy(srcs[-1]))
sh = list(s.shapes); assert sh[-1].name == 'Slide Number'
settext(sh[1], 'CQ 설문 목록의 예시'); settext(sh[2], '댐 운영 업무를 11개 영역으로 나누어 질문 후보를 정리 중. 영역마다 두 개씩 예시')
for x in P:
    for yv in (x if isinstance(x, list) else [x]): tree[-1].addprevious(etree.fromstring(yv))
ids = prs.slides._sldIdLst; lst = list(ids); new = lst[-1]; ids.remove(new); lst[22].addnext(new)
for i, sl in enumerate(prs.slides, 1):
    for shp in sl.shapes:
        if shp.name == 'Slide Number' and shp.has_text_frame and shp.text_frame.text.strip().isdigit():
            ts = shp._element.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/main}t'); ts[0].text = str(i)
            for t in ts[1:]: t.text = ''
prs.save(OUT)
