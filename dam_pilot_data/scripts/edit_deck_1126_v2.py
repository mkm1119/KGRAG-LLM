import copy, sys
from pptx import Presentation
from lxml import etree
from xml.sax.saxutils import escape
SRC, OUT = sys.argv[1], sys.argv[2]
NS = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
F = '<a:latin typeface="한컴산뜻돋움"/><a:ea typeface="한컴산뜻돋움"/><a:cs typeface="한컴산뜻돋움"/>'
NAVY, BLUE, PALE, INK, GRAY, LINE, WHITE = '003B71', '0070C0', 'EEF5FC', '2B2B2B', '6B7280', 'C9D8E8', 'FFFFFF'
n = [200]
def nid(): n[0] += 1; return n[0]

def tb(x, y, w, h, text, sz=1400, b=0, color=INK, algn='l', anchor='t', ln=130):
    i = nid(); ps = ''
    for para in text.split('\n'):
        runs = ''
        for k, seg in enumerate(para.split('**')):
            if seg == '': continue
            bb = 1 if (k % 2 == 1 or b) else 0
            cc = NAVY if (k % 2 == 1 and not b and color == INK) else color
            runs += '<a:r><a:rPr lang="ko-KR" altLang="en-US" sz="%d" b="%d" dirty="0"><a:solidFill><a:srgbClr val="%s"/></a:solidFill>%s</a:rPr><a:t>%s</a:t></a:r>' % (sz, bb, cc, F, escape(seg))
        ps += '<a:p><a:pPr algn="%s"><a:lnSpc><a:spcPct val="%d000"/></a:lnSpc><a:buNone/></a:pPr>%s</a:p>' % (algn, ln, runs)
    return ('<p:sp %s><p:nvSpPr><p:cNvPr id="%d" name="Text %d"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr><p:txBody><a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0" rtlCol="0" anchor="%s"><a:noAutofit/></a:bodyPr><a:lstStyle/>%s</p:txBody></p:sp>' % (NS, i, i, x, y, w, h, anchor, ps))

def box(x, y, w, h, fill, line=None, adj=4000):
    i = nid()
    return ('<p:sp %s><p:nvSpPr><p:cNvPr id="%d" name="Shape %d"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val %d"/></a:avLst></a:prstGeom><a:solidFill><a:srgbClr val="%s"/></a:solidFill><a:ln w="9525"><a:solidFill><a:srgbClr val="%s"/></a:solidFill></a:ln></p:spPr><p:txBody><a:bodyPr rtlCol="0" anchor="ctr"/><a:lstStyle/><a:p><a:endParaRPr lang="ko-KR"/></a:p></p:txBody></p:sp>' % (NS, i, i, x, y, w, h, adj, fill, line or fill))

def line(x, y, w, h=0, color=LINE, arrow=False, wd=12700):
    i = nid()
    return ('<p:cxnSp %s><p:nvCxnSpPr><p:cNvPr id="%d" name="Line %d"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr><p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="line"><a:avLst/></a:prstGeom><a:ln w="%d"><a:solidFill><a:srgbClr val="%s"/></a:solidFill><a:prstDash val="solid"/>%s</a:ln></p:spPr></p:cxnSp>' % (NS, i, i, x, y, w, h, wd, color, '<a:tailEnd type="triangle"/>' if arrow else ''))

prs = Presentation(SRC)
S = list(prs.slides); assert len(S) == 20
def ttl(s): return s.shapes[1].text_frame.text
assert ttl(S[8]) == '자료가 KG가 되는 과정' and ttl(S[12]) == '최종 프레임워크' and ttl(S[16]) == '향후 방향'

def settext(shape, t):
    rs = shape.text_frame.paragraphs[0].runs
    rs[0].text = t
    for r in rs[1:]: r._r.getparent().remove(r._r)

def fill(s, title, sub, parts):
    """머리글 셋과 쪽 번호만 남기고 본문을 새로 채운다."""
    tree = s.shapes._spTree; els = list(tree)[2:]
    for el in els[3:-1]: tree.remove(el)
    sh = list(s.shapes); assert sh[-1].name == 'Slide Number', sh[-1].name
    settext(sh[1], title); settext(sh[2], sub)
    for x in parts: tree[-1].addprevious(etree.fromstring(x))

def new_slide(base, title, sub, parts):
    s = prs.slides.add_slide(base.slide_layout)
    tree = s.shapes._spTree
    for sp in list(tree)[2:]: tree.remove(sp)
    src = list(base.shapes._spTree)
    for el in src[2:5]: tree.append(copy.deepcopy(el))
    num = [e for e in src if e.find('.//{*}cNvPr') is not None and e.find('.//{*}cNvPr').get('name') == 'Slide Number'][0]
    tree.append(copy.deepcopy(num))
    fill(s, title, sub, parts)
    return s

L0, W = 502920, 11155680

# ================= A. 자료 종류별 KG 구성 (9쪽 뒤)
P = []
cols = [1900000, 5100000, 2300000, 1855680]; xs = [L0]
for c in cols[:-1]: xs.append(xs[-1] + c)
y = 1720000; hh = 420000
P.append(box(L0, y, W, hh, NAVY, None, 10000))
for x, c, t in zip(xs, cols, ['자료', 'KG에 들어간 것 (Entity)', 'KG 밖 저장소에 둔 것', 'Entity 수']):
    P.append(tb(x + 150000, y, c - 200000, hh, t, 1300, 1, WHITE, 'l', 'ctr'))
rows = [
 ('시간 측정값', 'K-water 공개 자료',
  '댐마다 **수문·기상 상태 6개**(수위, 저수량, 강우량, 유입량, 총방류량, 저수율)\n측정값 자체는 넣지 않고, 찾아갈 열쇠인 관측소 코드만 저장',
  '측정값 약 87만 행\n(1시간 단위, 2010~2026년)', '수문·기상 상태 24\n근거 4'),
 ('방류 승인 기록', '한강홍수통제소 공개 자료',
  '한 행마다 **방류 승인 1개**(승인일, 방류시작시간, 방류량)\n비고의 문구에서 **운영행위**(방류, 초기방류, 증가방류, 탄력적 방류 등)를 읽어 냄',
  '없음\n(값을 모두 KG에 넣음)', '방류 승인 80\n운영행위 68\n근거 80'),
 ('운영 규정', '댐과 보 등의 연계운영규정',
  '별표 3의 댐별 행마다 **운영기준 1개**(홍수기 제한수위, 값, 단위)\n광동댐은 별표 3에 없어 운영기준이 없음',
  '규정 원문\n(별표 3 전체)', '운영기준 3\n근거 1')]
rh = 1130000; y += hh + 50000
for k, (a, a2, kg, st, cnt) in enumerate(rows):
    yy = y + k * (rh + 50000)
    P.append(box(L0, yy, W, rh, PALE, None, 3000))
    P.append(tb(xs[0] + 150000, yy + 250000, cols[0] - 200000, 320000, a, 1500, 1, NAVY))
    P.append(tb(xs[0] + 150000, yy + 600000, cols[0] - 200000, 300000, a2, 1050, 0, GRAY))
    P.append(tb(xs[1] + 150000, yy + 170000, cols[1] - 300000, rh - 200000, kg, 1200, 0, INK, 'l', 't', 125))
    P.append(tb(xs[2] + 150000, yy + 250000, cols[2] - 300000, rh - 300000, st, 1250))
    P.append(tb(xs[3] + 150000, yy + 170000, cols[3] - 200000, rh - 200000, cnt, 1250, 1, NAVY))
yb = y + 3 * (rh + 50000) + 20000
P.append(box(L0, yb, W, 620000, WHITE, LINE, 6000))
P.append(tb(L0 + 200000, yb, W - 400000, 620000,
            '**Entity 264개**  =  댐 4 + 수문·기상 상태 24 + 방류 승인 80 + 운영행위 68 + 운영기준 3 + 근거 85\n**관계 418개**  =  상태를 가짐 24 + 대상 80 + 수행됨 68 + 허가함 68 + 적용됨 3 + 근거를 둠 175', 1200, 0, INK, 'l', 'ctr', 125))
sA = new_slide(S[8], '자료 종류별 KG 구성', '세 종류의 자료가 각각 무엇으로 KG에 들어갔는지와 그 개수', P)

# ================= B. 질문 한 건이 처리되는 과정 (13쪽 뒤)
P = []
y = 1700000
P.append(box(L0, y, W, 430000, NAVY, None, 10000))
P.append(tb(L0 + 200000, y, 900000, 430000, '질문', 1300, 1, 'BFD9F2', 'l', 'ctr'))
P.append(tb(L0 + 1000000, y, W - 1200000, 430000, '충주댐 지금 수위가 홍수기 제한수위보다 높아?', 1500, 1, WHITE, 'l', 'ctr'))
steps = [
 ('① 질문 해석', 'LLM', '질문이 어느 CQ에 해당하는지와 댐, 기간을 뽑아 정해진 형식으로 출력',
  'CQ: **CQ1(현재 상태), CQ5(운영기준)**      댐: **충주댐**      기간: 전체'),
 ('② 근거 조회', '코드', 'CQ마다 정해 둔 조회문으로 KG를 조회하고, KG에 있는 열쇠로 저장소를 조회',
  'CQ1:  충주댐 → 상태를 가짐 → 수위 등 6개 (관측소 코드 1003110) → 측정 저장소의 가장 최근 시각\nCQ5:  운영기준 → 적용됨 → 충주댐,   운영기준 → 근거를 둠 → 별표 3 원문'),
 ('③ 근거 정리', '코드', '찾은 근거마다 출처 번호를 붙여 한 묶음으로 정리',
  '[MEA:1003110:2026092823]  2026-09-28 23:00  수위 131.6689 EL.m, 유입량 14.402 ㎥/s …\n[CRI:CR-02]  충주댐 홍수기 제한수위: 138.0 EL.m        [EVI:LAW:별표3]  규정 원문'),
 ('④ 답변 작성', 'LLM', '근거 묶음 안에서만 답을 쓰고, 사실 문장마다 출처 번호를 붙임',
  '근거: 충주댐의 현재 수위는 2026-09-28 23:00 기준 131.6689 EL.m이다 [MEA:1003110:2026092823]. 홍수기 제한수위는 138.0 EL.m이다 [CRI:CR-02].\n판단: **현재 수위는 홍수기 제한수위보다 낮다.**')]
y += 430000 + 60000
for k, (a, who, what, res) in enumerate(steps):
    rh = [780000, 940000, 940000, 1160000][k]; yy = y; y += rh + 50000
    llm = who == 'LLM'
    P.append(box(L0, yy, 2050000, rh, BLUE if llm else NAVY, None, 6000))
    P.append(tb(L0 + 170000, yy + rh // 2 - 250000, 1800000, 300000, a, 1500, 1, WHITE))
    P.append(tb(L0 + 170000, yy + rh // 2 + 80000, 1800000, 240000, who + ('이 수행' if llm else '가 수행'), 1050, 0, 'DCE9F7'))
    P.append(box(L0 + 2110000, yy, W - 2110000, rh, PALE, None, 3000))
    P.append(tb(L0 + 2300000, yy + 110000, W - 2500000, 260000, what, 1150, 0, GRAY))
    P.append(tb(L0 + 2300000, yy + 400000, W - 2500000, rh - 430000, res, 1150, 0, INK, 'l', 't', 120))
sB = new_slide(S[12], '질문 한 건이 처리되는 과정', '시연 질문 하나가 네 단계를 거치며 실제로 나온 결과 (2026-11-15 실행 기록)', P)

# ================= C. 사용한 LLM과 답변 원칙
P = []
pw = (W - 260000) // 2; py = 1720000; ph = 4480000; hh = 560000
kv = [('모델', '**Qwen3-32B**\n공개된 범용 LLM. 댐 운영 분야 자료로 추가 학습하지 않고 그대로 사용'),
      ('실행 환경', '연구실 서버(GPU RTX A6000 1장)에서 직접 실행'),
      ('LLM이 하는 일', '① 질문 해석, ④ 답변 작성\n같은 모델에 지시문만 바꿔 두 역할을 맡김'),
      ('코드가 하는 일', '② 근거 조회, ③ 근거 정리\n정해 둔 조회문을 쓰며, 이 단계에 LLM은 관여하지 않음'),
      ('KG 저장', '그래프 데이터베이스 (Neo4j)')]
P.append(box(L0, py, pw, ph, PALE, None, 2759)); P.append(box(L0, py, pw, hh, NAVY, None, 8421))
P.append(tb(L0 + 230000, py, pw - 460000, hh, '사용한 LLM과 구성', 1600, 1, WHITE, 'l', 'ctr'))
yy = py + hh + 170000
for k, (a, b2) in enumerate(kv):
    h = 760000 if '\n' in b2 else 520000
    P.append(tb(L0 + 230000, yy, 1350000, 300000, a, 1250, 1, BLUE))
    P.append(tb(L0 + 1600000, yy, pw - 1830000, h, b2, 1250, 0, INK, 'l', 't', 125))
    yy += h + 60000
x2 = L0 + pw + 260000
P.append(box(x2, py, pw, ph, PALE, None, 2759)); P.append(box(x2, py, pw, hh, NAVY, None, 8421))
P.append(tb(x2 + 230000, py, pw - 460000, hh, '답변 원칙 (LLM에 주는 지시)', 1600, 1, WHITE, 'l', 'ctr'))
rules = ['근거 묶음에 있는 내용만 사실로 쓰고, 사실 문장마다 **출처 번호**를 붙인다',
         '비교나 해석은 **판단임을 밝히고**, 어느 근거에서 나온 판단인지 적는다',
         '근거에 없는 내용은 **“자료에 없음”**이라고 답한다',
         '묻는 항목이 근거에 그 이름으로 없으면 **다른 값으로 대신 답하지 않는다**\n예: 계획홍수위를 물었는데 근거에 홍수기 제한수위만 있는 경우']
yy = py + hh + 200000
for k, r in enumerate(rules):
    h = 1050000 if '\n' in r else 760000
    P.append(tb(x2 + 230000, yy, 330000, 320000, '①②③④'[k], 1400, 1, BLUE))
    P.append(tb(x2 + 590000, yy, pw - 820000, h, r, 1300, 0, INK, 'l', 't', 125))
    yy += h + 60000
sC = new_slide(S[12], '사용한 LLM과 답변 원칙', 'LLM은 질문 해석과 답변 작성만 맡고, 근거를 찾는 일은 코드가 수행', P)

# ================= 18쪽: 용어를 CQ로 통일
P = []
bw, bh, y0 = 1850000, 760000, 1783080; gap = (W - 5 * bw) // 4
for k, (a, b2) in enumerate([('CQ', '답해야 할 질문을 정함'), ('온톨로지', 'CQ에 필요한 만큼 구축'), ('자료', '온톨로지에 맞춰 수집'), ('지식그래프 (KG)', '자료를 채움'), ('답변', '근거와 출처를 붙여 답함')]):
    x = L0 + k * (bw + gap); first = k == 0
    P.append(box(x, y0, bw, bh, BLUE if first else WHITE, BLUE if first else LINE, 8000))
    P.append(tb(x, y0 + 130000, bw, 300000, a, 1500, 1, WHITE if first else NAVY, 'ctr'))
    P.append(tb(x, y0 + 440000, bw, 240000, b2, 1050, 0, WHITE if first else GRAY, 'ctr'))
    if k < 4: P.append(line(x + bw + 60000, y0 + bh // 2, gap - 120000, 0, NAVY, True))
P.append(tb(L0, 2680000, W, 300000, 'CQ를 먼저 정하고 그 CQ에 필요한 만큼만 구축하는 구조이므로, **답할 수 있는 범위는 처음에 정한 CQ가 결정**', 1400))
py, ph, hh = 3200000, 2380000, 560000
for k, (head, dark, rws) in enumerate([
    ('지금', False, ['CQ 6개를 연구진이 공개 자료를 보고 정함', '근거와 출처를 붙여 답하는 구조가 동작함을 확인', '그러나 실무에서 실제로 필요한 CQ인지는 **확인되지 않음**']),
    ('실무의 의견이 반영되면', True, ['댐 운영 중 실제로 생기는 질문으로 CQ를 보완', '그 CQ에 맞춰 온톨로지, 자료, KG를 확장', '**실무에 필요한 질문에 근거를 붙여 답하는 구조**로 발전'])]):
    x = L0 + k * (pw + 260000)
    P.append(box(x, py, pw, ph, PALE, None, 2759)); P.append(box(x, py, pw, hh, NAVY if dark else 'DCE9F7', None, 8421))
    P.append(tb(x + 230000, py, pw - 460000, hh, head, 1600, 1, WHITE if dark else NAVY, 'l', 'ctr'))
    for j, r in enumerate(rws):
        yy = py + hh + 200000 + j * 520000
        P.append(tb(x + 230000, yy, 300000, 320000, '①②③'[j], 1400, 1, BLUE))
        P.append(tb(x + 560000, yy, pw - 790000, 420000, r, 1400))
P.append(line(L0 + pw + 50000, py + ph // 2, 160000, 0, NAVY, True, 19050))
P.append(box(L0, 5760000, W, 480000, NAVY, None, 12000))
P.append(tb(L0, 5760000, W, 480000, '어떤 CQ가 필요한지는 댐을 실제로 운영하는 실무자만 알 수 있음', 1500, 1, WHITE, 'ctr', 'ctr'))
fill(S[17], '범위 확장에 실무의 의견이 필요한 이유', '이 구조가 답할 수 있는 범위는 처음에 정한 CQ가 결정', P)

# ================= 19쪽: 향후 계획으로
P = []
cw = (W - 2 * 220000) // 3; cy, ch, hh = 1720000, 2500000, 640000
for k, (head, what, eff) in enumerate([
    ('필요한 CQ', '목록에 있는 CQ 가운데 실무에서 실제로 쓰이는 것', '우선하여 온톨로지와 KG에 반영'),
    ('필요 없는 CQ', '목록에 있지만 실무에서는 쓰이지 않는 것', '범위에서 제외'),
    ('부족한 CQ', '목록에는 없지만 댐 운영 중 실제로 생기는 질문', 'CQ에 추가')]):
    x = L0 + k * (cw + 220000)
    P.append(box(x, cy, cw, ch, PALE, None, 2759)); P.append(box(x, cy, cw, hh, NAVY, None, 8421))
    P.append(tb(x + 220000, cy, cw - 440000, hh, head, 1700, 1, WHITE, 'l', 'ctr'))
    P.append(tb(x + 220000, cy + hh + 180000, cw - 440000, 240000, '조사할 내용', 1100, 1, BLUE))
    P.append(tb(x + 220000, cy + hh + 450000, cw - 440000, 600000, what, 1300))
    P.append(line(x + 220000, cy + hh + 1130000, cw - 440000))
    P.append(tb(x + 220000, cy + hh + 1230000, cw - 440000, 240000, '조사 결과의 반영', 1100, 1, BLUE))
    P.append(tb(x + 220000, cy + hh + 1500000, cw - 440000, 300000, eff, 1300, 1, NAVY))
fy = cy + ch + 230000; fw = 2300000; fg = (W - 4 * fw) // 3
P.append(tb(L0, fy, W, 260000, '진행 순서', 1100, 1, BLUE))
for k, (a, b2) in enumerate([('CQ 목록 작성', '연구진'), ('실무자 조사', '필요 · 불필요 · 부족'), ('CQ 확정', '조사 결과 반영'), ('온톨로지 · KG 확장', '확정한 CQ에 맞춰')]):
    x = L0 + k * (fw + fg); hi = k == 1
    P.append(box(x, fy + 320000, fw, 700000, BLUE if hi else WHITE, BLUE if hi else LINE, 8000))
    P.append(tb(x, fy + 320000 + 120000, fw, 280000, a, 1400, 1, WHITE if hi else NAVY, 'ctr'))
    P.append(tb(x, fy + 320000 + 410000, fw, 220000, b2, 1050, 0, WHITE if hi else GRAY, 'ctr'))
    if k < 3: P.append(line(x + fw + 60000, fy + 670000, fg - 120000, 0, NAVY, True))
P.append(box(L0, 5800000, W, 460000, NAVY, None, 12000))
P.append(tb(L0, 5800000, W, 460000, '조사 결과를 반영하여 실무에서 실제로 묻는 내용에 답하는 구조로 발전시킬 계획', 1500, 1, WHITE, 'ctr', 'ctr'))
fill(S[18], '향후 계획: CQ 실무자 조사', '댐 운영과 관련된 CQ 목록을 실무자께 드리고, 필요한 것과 필요 없는 것, 부족한 것을 조사할 계획', P)

# ================= 순서와 쪽 번호
ids = prs.slides._sldIdLst; lst = list(ids); assert len(lst) == 23
a, b, c = lst[20], lst[21], lst[22]
for el in (a, b, c): ids.remove(el)
lst[8].addnext(a); lst[12].addnext(b); b.addnext(c)
for i, s in enumerate(prs.slides, 1):
    for sh in s.shapes:
        if sh.name == 'Slide Number' and sh.has_text_frame and sh.text_frame.text.strip().isdigit():
            ts = sh._element.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/main}t'); ts[0].text = str(i)
            for t in ts[1:]: t.text = ''
prs.save(OUT)
