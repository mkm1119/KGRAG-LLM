import copy, sys
from pptx import Presentation
from lxml import etree
from xml.sax.saxutils import escape
SRC, OUT = sys.argv[1], sys.argv[2]
NS = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
KF = '<a:latin typeface="한컴산뜻돋움"/><a:ea typeface="한컴산뜻돋움"/><a:cs typeface="한컴산뜻돋움"/>'
MF = '<a:latin typeface="Consolas"/><a:ea typeface="한컴산뜻돋움"/><a:cs typeface="Consolas"/>'
NAVY, BLUE, PALE, INK, GRAY, LINE, WHITE = '003B71', '0070C0', 'EEF5FC', '2B2B2B', '6B7280', 'C9D8E8', 'FFFFFF'
TEAL, ORG, EVG, CELLH, CELLB, SUBW = '2E9E8F', 'C55A11', '7F8B99', 'E5E7EB', 'B6BCC6', 'DCE9F7'
n = [300]
def nid(): n[0] += 1; return n[0]

def _runs(para, sz, b, color, font):
    runs = ''
    for k, seg in enumerate(para.split('**')):
        if seg == '': continue
        bb = 1 if (k % 2 == 1 or b) else 0
        cc = NAVY if (k % 2 == 1 and not b and color == INK) else color
        runs += '<a:r><a:rPr lang="ko-KR" altLang="en-US" sz="%d" b="%d" dirty="0"><a:solidFill><a:srgbClr val="%s"/></a:solidFill>%s</a:rPr><a:t>%s</a:t></a:r>' % (sz, bb, cc, font, escape(seg))
    return runs

def tb(x, y, w, h, text, sz=1400, b=0, color=INK, algn='l', anchor='t', ln=130, mono=False, paras=None):
    """paras: [(text, sz, b, color)] 를 주면 문단마다 다른 모양."""
    i = nid(); ps = ''; font = MF if mono else KF
    items = paras or [(t, sz, b, color) for t in text.split('\n')]
    for (t, s2, b2, c2) in items:
        ps += '<a:p><a:pPr algn="%s"><a:lnSpc><a:spcPct val="%d000"/></a:lnSpc><a:buNone/></a:pPr>%s</a:p>' % (algn, ln, _runs(t, s2, b2, c2, font))
    return ('<p:sp %s><p:nvSpPr><p:cNvPr id="%d" name="Text %d"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr><p:txBody><a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0" rtlCol="0" anchor="%s"><a:noAutofit/></a:bodyPr><a:lstStyle/>%s</p:txBody></p:sp>' % (NS, i, i, x, y, w, h, anchor, ps))

def box(x, y, w, h, fill, line=None, adj=4000, rect=False):
    i = nid()
    geom = '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>' if rect else '<a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val %d"/></a:avLst></a:prstGeom>' % adj
    return ('<p:sp %s><p:nvSpPr><p:cNvPr id="%d" name="Shape %d"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>%s<a:solidFill><a:srgbClr val="%s"/></a:solidFill><a:ln w="9525"><a:solidFill><a:srgbClr val="%s"/></a:solidFill></a:ln></p:spPr><p:txBody><a:bodyPr rtlCol="0" anchor="ctr"/><a:lstStyle/><a:p><a:endParaRPr lang="ko-KR"/></a:p></p:txBody></p:sp>' % (NS, i, i, x, y, w, h, geom, fill, line or fill))

def ln(x1, y1, x2, y2, color=BLUE, wd=25400, dash=False, arrow=True):
    i = nid(); fl = ''
    if x2 < x1: fl += ' flipH="1"'
    if y2 < y1: fl += ' flipV="1"'
    return ('<p:cxnSp %s><p:nvCxnSpPr><p:cNvPr id="%d" name="Line %d"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr><p:spPr><a:xfrm%s><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="line"><a:avLst/></a:prstGeom><a:ln w="%d"><a:solidFill><a:srgbClr val="%s"/></a:solidFill><a:prstDash val="%s"/>%s</a:ln></p:spPr></p:cxnSp>' % (NS, i, i, fl, min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1), wd, color, 'dash' if dash else 'solid', '<a:tailEnd type="triangle" w="med" len="med"/>' if arrow else ''))
def dln(x1, y1, x2, y2, arrow=True): return ln(x1, y1, x2, y2, GRAY, 15875, True, arrow)

def ent(x, y, w, h, fill, title, *subs, tsz=1500):
    """KG의 Entity 상자: 굵은 이름과 작은 설명."""
    return [box(x, y, w, h, fill, None, 10000),
            tb(x + 40000, y, w - 80000, h, '', algn='ctr', anchor='ctr', ln=110, paras=[(title, tsz, 1, WHITE)] + [(s, 1050, 0, SUBW) for s in subs])]
def cell(x, y, w, h, text, head=False, hi=False, sz=1200):
    return [box(x, y, w, h, CELLH if head else ('FFF4E5' if hi else WHITE), CELLB, rect=True),
            tb(x + 20000, y, w - 40000, h, text, sz, 1 if (head or hi) else 0, INK, 'ctr', 'ctr')]
def rel(x, y, t, w=1100000, algn='ctr'): return tb(x, y, w, 260000, t, 1100, 1, ORG, algn)
def note(x, y, t, w=1800000): return tb(x, y, w, 260000, t, 1050, 1, GRAY, 'l', 'ctr')

prs = Presentation(SRC)
S = list(prs.slides); assert len(S) == 23
def ttl(s): return s.shapes[1].text_frame.text
assert ttl(S[9]) == '자료 종류별 KG 구성' and ttl(S[13]) == '최종 프레임워크' and ttl(S[14]) == '질문 한 건이 처리되는 과정' and ttl(S[15]) == '사용한 LLM과 답변 원칙' and ttl(S[21]).startswith('향후 계획')

def settext(shape, t):
    rs = shape.text_frame.paragraphs[0].runs
    rs[0].text = t
    for r in rs[1:]: r._r.getparent().remove(r._r)
def fill(s, title, sub, parts):
    tree = s.shapes._spTree; els = list(tree)[2:]
    for el in els[3:-1]: tree.remove(el)
    sh = list(s.shapes); assert sh[-1].name == 'Slide Number', sh[-1].name
    settext(sh[1], title); settext(sh[2], sub)
    for x in parts:
        for y in (x if isinstance(x, list) else [x]): tree[-1].addprevious(etree.fromstring(y))
def new_slide(base, title, sub, parts):
    s = prs.slides.add_slide(base.slide_layout); tree = s.shapes._spTree
    for sp in list(tree)[2:]: tree.remove(sp)
    src = list(base.shapes._spTree)
    for el in src[2:5]: tree.append(copy.deepcopy(el))
    num = [e for e in src if e.find('.//{*}cNvPr') is not None and e.find('.//{*}cNvPr').get('name') == 'Slide Number'][0]
    tree.append(copy.deepcopy(num)); fill(s, title, sub, parts); return s
def legend(P, extra=''):
    P.append(dln(5650000, 6185000, 5950000, 6185000)); P.append(tb(6020000, 6040000, 1900000, 290000, '열의 값이 Entity에 들어감', 1050, 0, GRAY, 'l', 'ctr'))
    P.append(ln(8040000, 6185000, 8360000, 6185000, BLUE, 19050)); P.append(tb(8430000, 6040000, 3200000, 290000, 'Entity 사이의 관계' + extra, 1050, 0, GRAY, 'l', 'ctr'))

L0, W = 502920, 11155680
HY, HH, RH = 1920240, 329184, 350000

# ================= 10쪽: 시간 측정값 -> KG
P = []
P.append(tb(L0, 1627632, 1100000, 274320, '원본 두 행', 1400, 1, GRAY))
P.append(tb(1600200, 1627632, 10058400, 274320, '측정값은 1시간마다 한 행씩 쌓여 약 87만 행. 값은 KG에 넣지 않고, 항목마다 Entity 하나와 찾아갈 열쇠(관측소 코드)만 KG에 저장', 1200, 0, INK, 'l', 'ctr'))
cw = [1350000, 1900000] + [(W - 3250000) // 6] * 6; cx = [L0]
for c in cw[:-1]: cx.append(cx[-1] + c)
heads = ['관측소 코드', '시각', '수위 (EL.m)', '저수량 (백만㎥)', '강우량 (mm)', '유입량 (㎥/s)', '총방류량 (㎥/s)', '저수율 (%)']
rows = [['1003110', '2020-08-02 17:00', '139.37', '2111.215', '0.711', '4693.654', '707.265', '76.8'],
        ['1003110', '2020-08-02 18:00', '139.55', '2126.472', '1.901', '4945.201', '707.145', '77.3']]
for k in range(8):
    P.append(cell(cx[k], HY, cw[k], HH, heads[k], head=True, sz=1100))
    for j, r in enumerate(rows): P.append(cell(cx[k], HY + HH + j * RH, cw[k], RH, r[k], sz=1100))
tend = HY + HH + 2 * RH
sy, sh_, sw = 3560000, 720000, 1180000
names = ['수위', '저수량', '강우량', '유입량', '총방류량', '저수율']
for k in range(6):
    mid = cx[k + 2] + cw[k + 2] // 2
    P.append(dln(mid, tend + 40000, mid, sy - 30000))
    P.append(ent(mid - sw // 2, sy, sw, sh_, TEAL, names[k], '열쇠: 1003110', tsz=1400))
P.append(note(cx[2] + cw[2] // 2 + 70000, tend + 170000, '열의 이름 → 항목'))
dy, dh, dx, dw = 4720000, 720000, L0 + 150000, 1500000
P.append(dln(L0 + 500000, tend + 40000, L0 + 500000, dy - 30000)); P.append(note(L0 + 570000, tend + 170000, '관측소 코드 → 댐', 1400000))
P.append(ent(dx, dy, dw, dh, NAVY, '충주댐', '댐'))
busy = dy + dh // 2; lastmid = cx[7] + cw[7] // 2
P.append(ln(dx + dw, busy, lastmid, busy, BLUE, 25400, False, False))
for k in range(6):
    mid = cx[k + 2] + cw[k + 2] // 2
    P.append(ln(mid, busy, mid, sy + sh_ + 30000))
P.append(rel(dx + dw + 150000, busy - 300000, '상태를 가짐', 1200000, 'l'))
ex, ey, ew, eh = 4300000, 5520000, 3000000, 500000
P.append(ent(ex, ey, ew, eh, EVG, '근거', 'K-water 수문 시간자료 (충주댐)', tsz=1300))
P.append(ln(ex + ew // 2, busy, ex + ew // 2, ey - 30000)); P.append(rel(ex + ew // 2 + 80000, busy + 80000, '근거를 둠 (상태 6개 각각)', 2400000, 'l'))
P.append(tb(7700000, 5480000, 3950000, 520000, '댐 4개에 같은 방식으로 적용: 수문·기상 상태 Entity 24개\n측정값 자체는 측정 저장소에 보관 (다음 쪽)', 1100, 0, GRAY, 'l', 'ctr', 120))
legend(P)
fill(S[9], '자료가 KG가 되는 과정: 시간 측정값', '측정값의 열 이름이 수문·기상 상태 Entity가 되는 예 (충주댐, 관측소 코드 1003110)', P)

# ================= 11쪽(신규): 운영 규정 -> KG
P = []
P.append(tb(L0, 1627632, 1100000, 274320, '원본 표', 1400, 1, GRAY))
P.append(tb(1600200, 1627632, 10058400, 274320, '댐과 보 등의 연계운영규정  [별표 3] 댐의 홍수기 제한수위(제6조)  가운데 한강 수계 다목적댐 부분', 1200, 0, INK, 'l', 'ctr'))
cw = [1300000, 1500000, 1700000, 2500000]; cx = [L0]
for c in cw[:-1]: cx.append(cx[-1] + c)
heads = ['구분', '댐 종류', '댐명', '홍수기 제한수위 (EL.m)']
rows = [['한강 수계', '다목적댐', '소양강댐', '190.3'], ['한강 수계', '다목적댐', '충주댐', '138.0'], ['한강 수계', '다목적댐', '횡성댐', '178.2']]
for k in range(4):
    P.append(cell(cx[k], HY, cw[k], HH, heads[k], head=True))
    for j, r in enumerate(rows): P.append(cell(cx[k], HY + HH + j * RH, cw[k], RH, r[k], hi=(j == 1 and k >= 2)))
tend = HY + HH + 3 * RH; tright = cx[3] + cw[3]
P.append(tb(tright + 300000, HY + 60000, 3900000, 1200000, '· 충주댐 행 하나가 운영기준 Entity 하나가 됨\n· 같은 방식으로 소양강댐, 횡성댐도 생성: 운영기준 3개\n· 광동댐은 별표 3에 없어 운영기준이 없음\n· 별표 3의 원문 전체는 문서 저장소에 보관', 1150, 0, INK, 'l', 't', 135))
ky, kh = 4050000, 900000
m_dam = cx[2] + cw[2] // 2; m_cri = cx[3] + cw[3] // 2
P.append(tb(182880, ky + 300000, 548640, 274320, 'KG', 1400, 1, GRAY))
dam_x, dam_w = m_dam - 1150000, 1700000
cri_x, cri_w = m_cri - 900000, 2700000
evi_x, evi_w = 9000000, 2600000
P.append(dln(m_dam, tend + 40000, m_dam, ky - 30000)); P.append(note(m_dam + 70000, tend + 300000, '댐 이름으로 댐을 찾음', 1700000))
P.append(dln(m_cri + 400000, tend + 40000, m_cri + 400000, ky - 30000)); P.append(note(m_cri + 470000, tend + 300000, '값'))
P.append(ent(dam_x, ky, dam_w, kh, NAVY, '충주댐', '댐'))
P.append(ent(cri_x, ky, cri_w, kh, ORG, '홍수기 제한수위', '운영기준', '값 138.0 · 단위 EL.m'))
P.append(ent(evi_x, ky, evi_w, kh, EVG, '근거', '댐과 보 등의 연계운영규정', '위치: 별표 3'))
P.append(ln(cri_x, ky + kh // 2, dam_x + dam_w + 30000, ky + kh // 2)); P.append(rel(dam_x + dam_w - 100000, ky + kh // 2 - 300000, '적용됨', cri_x - dam_x - dam_w + 200000))
P.append(ln(cri_x + cri_w, ky + kh // 2, evi_x - 30000, ky + kh // 2)); P.append(rel(cri_x + cri_w, ky + kh // 2 - 300000, '근거를 둠', evi_x - cri_x - cri_w))
ex = evi_x + evi_w // 2
P.append(dln(ex, 3640000, ex, ky - 30000)); P.append(note(ex + 70000, 3720000, '근거의 위치', 1200000))
P.append(tb(ex - 1300000, 3350000, 2600000, 260000, '[별표 3]  (표의 제목)', 1100, 1, INK, 'ctr'))
legend(P)
sREG = new_slide(S[8], '자료가 KG가 되는 과정: 운영 규정', '규정의 별표 한 행이 운영기준 Entity와 관계가 되는 예 (충주댐, 홍수기 제한수위)', P)

# ================= 질의응답 과정 ①②
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
P.append(tb(rx + 180000, ty, rw - 360000, 520000, '② 근거 조회', 1500, 1, WHITE, 'l', 'ctr'))
P.append(tb(rx + 2000000, ty, rw - 2180000, 520000, '코드   ·   CQ마다 정해 둔 조회문으로 KG를 조회하고, KG의 열쇠로 저장소를 조회', 1100, 0, SUBW, 'r', 'ctr'))
def qrow(y0, tag, q, gloss):
    P.append(box(rx + 180000, y0, 620000, 300000, BLUE, None, 30000)); P.append(tb(rx + 180000, y0, 620000, 300000, tag, 1100, 1, WHITE, 'ctr', 'ctr'))
    P.append(tb(rx + 900000, y0, 1300000, 300000, '조회문', 1100, 1, GRAY, 'l', 'ctr'))
    P.append(box(rx + 180000, y0 + 350000, rw - 360000, 470000, 'F3F4F6', CELLH, 4000))
    P.append(tb(rx + 300000, y0 + 350000, rw - 600000, 470000, q, 950, 0, INK, 'l', 'ctr', 115, mono=True))
    P.append(tb(rx + 1600000, y0, rw - 1800000, 300000, gloss, 950, 0, GRAY, 'r', 'ctr'))
bw_, bh_ = 1650000, 600000
# CQ1
y1 = ty + 620000
qrow(y1, 'CQ1', "MATCH (d:Dam {damName:'충주댐'})-[:hasHydrometeorologicalState]->(h)\nRETURN h.id, h.variableType, h.stationCode", 'Dam 댐 · hasHydrometeorologicalState 상태를 가짐')
gy = y1 + 920000; x1 = rx + 180000
P.append(ent(x1, gy, 1300000, bh_, NAVY, '충주댐', tsz=1300))
x2 = x1 + 1300000 + 950000
P.append(ln(x1 + 1300000, gy + bh_ // 2, x2 - 30000, gy + bh_ // 2)); P.append(rel(x1 + 1300000, gy + bh_ // 2 - 290000, '상태를 가짐', 950000))
P.append(ent(x2, gy, 1900000, bh_, TEAL, '수위 등 6개', '열쇠: 관측소 코드 1003110', tsz=1300))
x3 = x2 + 1900000 + 1000000
P.append(ln(x2 + 1900000, gy + bh_ // 2, x3 - 30000, gy + bh_ // 2, TEAL)); P.append(tb(x2 + 1900000, gy + bh_ // 2 - 290000, 1000000, 260000, '열쇠로 조회', 1050, 1, TEAL, 'ctr'))
P.append(box(x3, gy, rx + rw - 180000 - x3, bh_, WHITE, TEAL, 8000))
P.append(tb(x3 + 60000, gy, rx + rw - 180000 - x3 - 120000, bh_, '', algn='ctr', anchor='ctr', ln=110, paras=[('측정 저장소의 가장 최근 시각', 1100, 1, TEAL), ('2026-09-28 23:00  수위 131.6689', 1000, 0, INK)]))
# CQ5
y2 = gy + bh_ + 200000
P.append(ln(rx + 180000, y2 - 100000, rx + rw - 180000, y2 - 100000, LINE, 9525, False, False))
qrow(y2, 'CQ5', "MATCH (c:Criterion)-[:appliesToDam]->(d:Dam {damName:'충주댐'})  RETURN c.id, c.criterionType, c.criterionValue, c.unit\nMATCH (x {id:'CRI:CR-02'})-[:supportedBy]->(e:EvidenceSource)  RETURN e.sourceTitle, e.sourceLocator", 'Criterion 운영기준 · appliesToDam 적용됨 · supportedBy 근거를 둠')
gy = y2 + 920000
P.append(ent(x1, gy, 1300000, bh_, NAVY, '충주댐', tsz=1300))
P.append(ln(x2, gy + bh_ // 2, x1 + 1300000 + 30000, gy + bh_ // 2)); P.append(rel(x1 + 1300000, gy + bh_ // 2 - 290000, '적용됨', 950000))
P.append(ent(x2, gy, 1900000, bh_, ORG, '홍수기 제한수위', '138.0 EL.m', tsz=1300))
xe = x2 + 1900000 + 900000; we = 1300000
P.append(ln(x2 + 1900000, gy + bh_ // 2, xe - 30000, gy + bh_ // 2)); P.append(rel(x2 + 1900000, gy + bh_ // 2 - 290000, '근거를 둠', 900000))
P.append(ent(xe, gy, we, bh_, EVG, '근거', '열쇠: 별표 3', tsz=1300))
xs_ = xe + we + 250000
P.append(ln(xe + we, gy + bh_ // 2, xs_ - 30000, gy + bh_ // 2, EVG))
P.append(box(xs_, gy, rx + rw - 180000 - xs_, bh_, WHITE, EVG, 8000))
P.append(tb(xs_ + 40000, gy, rx + rw - 180000 - xs_ - 80000, bh_, '', algn='ctr', anchor='ctr', ln=110, paras=[('문서 저장소', 1100, 1, GRAY), ('별표 3 원문', 1000, 0, INK)]))
sQ1 = new_slide(S[8], '질의응답 과정 ①②: 질문 해석과 근거 조회', '시연 질문 하나가 실제로 처리된 과정 (2026-11-15 실행 기록)', P)

# ================= 질의응답 과정 ③④
P = []
P.append(box(L0, qy, W, 400000, NAVY, None, 10000))
P.append(tb(L0 + 200000, qy, 900000, 400000, '질문', 1300, 1, 'BFD9F2', 'l', 'ctr'))
P.append(tb(L0 + 1000000, qy, W - 1200000, 400000, '충주댐 지금 수위가 홍수기 제한수위보다 높아?', 1500, 1, WHITE, 'l', 'ctr'))
lw = 6100000; rx = L0 + lw + 160000; rw = W - lw - 160000
P.append(box(L0, ty, lw, th, PALE, None, 2759)); P.append(box(L0, ty, lw, 520000, NAVY, None, 8421))
P.append(tb(L0 + 180000, ty, 2500000, 520000, '③ 근거 정리', 1500, 1, WHITE, 'l', 'ctr'))
P.append(tb(L0 + 2300000, ty, lw - 2480000, 520000, '코드   ·   찾은 근거에 출처 번호를 붙여 한 묶음으로 정리', 1100, 0, SUBW, 'r', 'ctr'))
P.append(box(L0 + 180000, ty + 640000, lw - 360000, th - 1330000, WHITE, CELLH, 3000))
bundle = [('■ 근거 1. 현재 상태 (CQ1 구역)  저장된 가장 최근 시각이며 실시간이 아님', 1000, 1, NAVY),
          ('**[MEA:1003110:2026092823]** 2026-09-28 23:00  수위 131.6689 EL.m, 저수량 1491.3423 MCM, 강우량 0 mm, 유입량 14.402 CMS, 총방류량 0.43 CMS, 저수율 54.2 %', 1000, 0, INK),
          (' ', 600, 0, INK),
          ('■ 근거 2. 운영기준 (CQ5 구역)', 1000, 1, NAVY),
          ('**[CRI:CR-02]** 충주댐 홍수기 제한수위: 138.0 EL.m', 1000, 0, INK),
          ('**[EVI:LAW:별표3]** 댐과 보 등의 연계운영규정 (기후에너지환경부 훈령 제42호, 시행 2026-07-08) 원문:  [별표 3] 댐의 홍수기 제한수위(제6조) …', 1000, 0, INK),
          (' ', 600, 0, INK),
          ('■ 근거 사용 원칙', 1000, 1, NAVY),
          ('1. 위 근거에 있는 내용만 사실로 쓰고, 문장마다 출처 번호를 붙인다.', 1000, 0, INK),
          ('2. 비교나 해석은 LLM의 판단임을 밝히고, 어느 근거에서 나온 판단인지 적는다.', 1000, 0, INK),
          ('3. 근거에 없는 내용은 "자료에 없음"이라고 답한다.', 1000, 0, INK)]
P.append(tb(L0 + 330000, ty + 720000, lw - 660000, th - 1480000, '', ln=128, paras=bundle))
P.append(tb(L0 + 180000, ty + th - 620000, lw - 360000, 520000, '출처 번호의 뜻   MEA: 측정값(관측소 코드, 시각)   CRI: 운영기준   EVI: 근거 문서\n이 묶음이 질문과 함께 LLM에 입력됨', 1000, 0, GRAY, 'l', 'ctr', 125))
P.append(ln(L0 + lw + 20000, ty + th // 2, rx - 20000, ty + th // 2, NAVY, 19050))
P.append(box(rx, ty, rw, th, PALE, None, 2759)); P.append(box(rx, ty, rw, 520000, BLUE, None, 8421))
P.append(tb(rx + 180000, ty, 2500000, 520000, '④ 답변 작성', 1500, 1, WHITE, 'l', 'ctr'))
P.append(tb(rx + rw - 900000, ty, 720000, 520000, 'LLM', 1100, 1, SUBW, 'r', 'ctr'))
P.append(box(rx + 180000, ty + 640000, rw - 360000, th - 1630000, WHITE, CELLH, 3000))
ans = [('근거', 1150, 1, BLUE),
       ('· 충주댐의 현재 수위는 2026-09-28 23:00 기준 131.6689 EL.m이다 **[MEA:1003110:2026092823]**.', 1100, 0, INK),
       ('· 충주댐의 홍수기 제한수위는 138.0 EL.m이다 **[CRI:CR-02]**.', 1100, 0, INK),
       (' ', 600, 0, INK),
       ('판단', 1150, 1, BLUE),
       ('**현재 충주댐 수위(131.6689 EL.m)는 홍수기 제한수위(138.0 EL.m)보다 낮다.** (근거: [MEA:1003110:2026092823], [CRI:CR-02])', 1100, 0, INK)]
P.append(tb(rx + 330000, ty + 730000, rw - 660000, th - 1800000, '', ln=135, paras=ans))
P.append(tb(rx + 180000, ty + th - 920000, rw - 360000, 820000, '· 사실과 판단을 나누어 답함\n· 사실 문장마다 출처 번호가 붙어 있어, 번호로 근거를 다시 확인할 수 있음\n· 답변은 실행 기록의 원문', 1050, 0, GRAY, 'l', 'ctr', 128))
sQ2 = new_slide(S[8], '질의응답 과정 ③④: 근거 정리와 답변 작성', '찾은 근거가 출처 번호와 함께 LLM에 전달되고, LLM은 그 안에서만 답변 (2026-11-15 실행 기록)', P)

# ================= 22쪽: 설문 계획
s22 = S[21]
for sh in s22.shapes:
    if not sh.has_text_frame: continue
    for para in sh.text_frame.paragraphs:
        for r in para.runs:
            t = r.text
            for a, b in [('향후 계획: CQ 실무자 조사', '향후 계획: CQ 실무자 설문'), ('부족한 것을 조사할 계획', '부족한 것을 설문으로 조사할 계획'), ('조사할 내용', '설문 내용'), ('조사 결과의 반영', '설문 결과의 반영'), ('실무자 조사', '실무자 설문'), ('조사 결과 반영', '설문 결과 반영'), ('조사 결과를 반영하여', '설문 결과를 반영하여')]:
                t = t.replace(a, b)
            if t != r.text: r.text = t

# ================= 순서, 삭제, 쪽 번호
ids = prs.slides._sldIdLst; lst = list(ids); assert len(lst) == 26
reg, q1, q2 = lst[23], lst[24], lst[25]
for el in (reg, q1, q2): ids.remove(el)
lst[9].addnext(reg)                 # 측정값 뒤에 운영 규정
frame = lst[13]; ids.remove(frame)  # 최종 프레임워크를 Ⅰ장 끝으로
old15, old16 = lst[14], lst[15]
old15.addprevious(q1); q1.addnext(q2); q2.addnext(frame)
for el in (old15, old16):
    prs.part.drop_rel(el.rId); ids.remove(el)
assert len(list(ids)) == 24
for i, s in enumerate(prs.slides, 1):
    for sh in s.shapes:
        if sh.name == 'Slide Number' and sh.has_text_frame and sh.text_frame.text.strip().isdigit():
            ts = sh._element.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/main}t'); ts[0].text = str(i)
            for t in ts[1:]: t.text = ''
prs.save(OUT)
