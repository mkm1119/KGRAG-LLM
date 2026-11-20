import copy, sys
from pptx import Presentation
from lxml import etree
from xml.sax.saxutils import escape
SRC, OUT = sys.argv[1], sys.argv[2]
NS = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
F = '<a:latin typeface="한컴산뜻돋움"/><a:ea typeface="한컴산뜻돋움"/><a:cs typeface="한컴산뜻돋움"/>'
NAVY, BLUE, PALE, INK, GRAY, LINE = '003B71', '0070C0', 'EEF5FC', '2B2B2B', '6B7280', 'C9D8E8'

def tb(i, x, y, w, h, text, sz=1400, b=0, color=INK, algn='l', anchor='t', ln=130):
    ps = ''
    for para in text.split('\n'):
        runs = ''
        for k, seg in enumerate(para.split('**')):   # **굵게**
            if seg == '': continue
            bb = 1 if (k % 2 == 1 or b) else 0
            cc = NAVY if (k % 2 == 1 and not b and color == INK) else color
            runs += '<a:r><a:rPr lang="ko-KR" altLang="en-US" sz="%d" b="%d" dirty="0"><a:solidFill><a:srgbClr val="%s"/></a:solidFill>%s</a:rPr><a:t>%s</a:t></a:r>' % (sz, bb, cc, F, escape(seg))
        ps += '<a:p><a:pPr algn="%s"><a:lnSpc><a:spcPct val="%d000"/></a:lnSpc><a:buNone/></a:pPr>%s</a:p>' % (algn, ln, runs)
    return ('<p:sp %s><p:nvSpPr><p:cNvPr id="%d" name="Text %d"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr><p:txBody><a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0" rtlCol="0" anchor="%s"><a:noAutofit/></a:bodyPr><a:lstStyle/>%s</p:txBody></p:sp>' % (NS, i, i, x, y, w, h, anchor, ps))

def box(i, x, y, w, h, fill, line=None, adj=4000):
    return ('<p:sp %s><p:nvSpPr><p:cNvPr id="%d" name="Shape %d"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val %d"/></a:avLst></a:prstGeom><a:solidFill><a:srgbClr val="%s"/></a:solidFill><a:ln w="9525"><a:solidFill><a:srgbClr val="%s"/></a:solidFill></a:ln></p:spPr><p:txBody><a:bodyPr rtlCol="0" anchor="ctr"/><a:lstStyle/><a:p><a:endParaRPr lang="ko-KR"/></a:p></p:txBody></p:sp>' % (NS, i, i, x, y, w, h, adj, fill, line or fill))

def line(i, x, y, w, h=0, color=LINE, arrow=False, wd=12700):
    return ('<p:cxnSp %s><p:nvCxnSpPr><p:cNvPr id="%d" name="Line %d"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr><p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="line"><a:avLst/></a:prstGeom><a:ln w="%d"><a:solidFill><a:srgbClr val="%s"/></a:solidFill><a:prstDash val="solid"/>%s</a:ln></p:spPr></p:cxnSp>' % (NS, i, i, x, y, w, h, wd, color, '<a:tailEnd type="triangle"/>' if arrow else ''))

prs = Presentation(SRC)
base = prs.slides[16]            # 17쪽
assert base.shapes[1].text_frame.text == '향후 방향'

def new_slide(title, sub, num, parts):
    s = prs.slides.add_slide(base.slide_layout)
    tree = s.shapes._spTree
    for sp in list(tree)[2:]: tree.remove(sp)
    src = list(base.shapes._spTree)
    for el in src[2:5]: tree.append(copy.deepcopy(el))      # 장 이름, 제목, 부제
    tree.append(copy.deepcopy(src[-1]))                     # 쪽 번호
    sh = list(s.shapes)
    def settext(shape, t):
        rs = shape.text_frame.paragraphs[0].runs
        rs[0].text = t
        for r in rs[1:]: r._r.getparent().remove(r._r)
    settext(sh[1], title); settext(sh[2], sub)
    num_el = tree[-1]
    for x in parts: num_el.addprevious(etree.fromstring(x))
    return s

L0, W = 502920, 11155680
# ---------------- 18쪽
P = []; n = [100]
def nid(): n[0] += 1; return n[0]
bw, bh, y0 = 1850000, 760000, 1783080
gap = (W - 5 * bw) // 4
for k, (a, b2) in enumerate([('질문 (CQ)', '답해야 할 질문을 정함'), ('온톨로지', '질문에 필요한 만큼 구축'), ('자료', '온톨로지에 맞춰 수집'), ('지식그래프 (KG)', '자료를 채움'), ('답변', '근거와 출처를 붙여 답함')]):
    x = L0 + k * (bw + gap)
    first = k == 0
    P.append(box(nid(), x, y0, bw, bh, BLUE if first else 'FFFFFF', BLUE if first else LINE, 8000))
    P.append(tb(nid(), x, y0 + 130000, bw, 300000, a, 1500, 1, 'FFFFFF' if first else NAVY, 'ctr'))
    P.append(tb(nid(), x, y0 + 440000, bw, 240000, b2, 1050, 0, 'FFFFFF' if first else GRAY, 'ctr'))
    if k < 4: P.append(line(nid(), x + bw + 60000, y0 + bh // 2, gap - 120000, 0, NAVY, True))
P.append(tb(nid(), L0, 2680000, W, 300000, '질문을 먼저 정하고 그 질문에 필요한 만큼만 구축하는 구조이므로, **답할 수 있는 범위는 처음에 정한 질문이 결정**', 1400, 0, INK, 'l'))
pw = (W - 260000) // 2; py, ph, hh = 3200000, 2380000, 560000
for k, (head, dark, rows) in enumerate([
    ('지금', False, ['질문 6개를 연구진이 공개 자료를 보고 정함', '근거와 출처를 붙여 답하는 구조가 동작함을 확인', '그러나 실무에서 실제로 필요한 질문인지는 **확인되지 않음**']),
    ('실무 질문이 반영되면', True, ['댐 운영 중 실제로 생기는 질문으로 질문(CQ)을 보완', '그 질문에 맞춰 온톨로지, 자료, KG를 확장', '**실무에 필요한 질문에 근거를 붙여 답하는 구조**로 발전'])]):
    x = L0 + k * (pw + 260000)
    P.append(box(nid(), x, py, pw, ph, PALE, None, 2759))
    P.append(box(nid(), x, py, pw, hh, NAVY if dark else 'DCE9F7', None, 8421))
    P.append(tb(nid(), x + 230000, py, pw - 460000, hh, head, 1600, 1, 'FFFFFF' if dark else NAVY, 'l', 'ctr'))
    for j, r in enumerate(rows):
        yy = py + hh + 200000 + j * 520000
        P.append(tb(nid(), x + 230000, yy, 300000, 320000, '①②③'[j], 1400, 1, BLUE))
        P.append(tb(nid(), x + 560000, yy, pw - 790000, 420000, r, 1400))
P.append(line(nid(), L0 + pw + 50000, py + ph // 2, 160000, 0, NAVY, True, 19050))
P.append(box(nid(), L0, 5760000, W, 480000, NAVY, None, 12000))
P.append(tb(nid(), L0, 5760000, W, 480000, '어떤 질문이 필요한지는 댐을 실제로 운영하는 실무자만 알 수 있음', 1500, 1, 'FFFFFF', 'ctr', 'ctr'))
new_slide('범위 확장에 실무 질문이 필요한 이유', '이 구조가 답할 수 있는 범위는 처음에 정한 질문(CQ)이 결정', 18, P)

# ---------------- 19쪽
P = []
cy, ch, hh = 1783080, 3760000, 800000
for k, (head, req, ex, eff) in enumerate([
    ('①  운영 중 실제로 생기는 질문',
     '댐을 운영하면서 확인이 필요했던 것, 판단할 때 찾아보신 것을 **질문의 형태로 알려 주시면**,',
     '예시)  “유입량이 이 정도일 때 과거에는 방류를 어떻게 했는가?”',
     '그 질문을 질문(CQ)에 추가하여, 실무에서 실제로 묻는 내용에 답하도록 범위를 넓힐 수 있습니다'),
    ('②  질문 후보에 대한 의견',
     '연구진이 정리한 질문 후보를 보시고 **필요한 질문인지, 빠진 질문은 없는지 의견을 주시면**,',
     '예시)  “이 질문은 실무에서 쓰지 않는다”,  “이런 질문이 빠져 있다”',
     '실무에 필요한 질문부터 우선하여 온톨로지와 KG를 구축할 수 있습니다')]):
    x = L0 + k * (pw + 260000)
    P.append(box(nid(), x, cy, pw, ch, PALE, None, 2759))
    P.append(box(nid(), x, cy, pw, hh, NAVY, None, 8421))
    P.append(tb(nid(), x + 230000, cy, pw - 460000, hh, head, 1800, 1, 'FFFFFF', 'l', 'ctr'))
    P.append(tb(nid(), x + 230000, cy + hh + 230000, pw - 460000, 760000, req, 1400))
    P.append(tb(nid(), x + 230000, cy + hh + 1080000, pw - 460000, 420000, ex, 1200, 0, GRAY))
    P.append(line(nid(), x + 230000, cy + hh + 1620000, pw - 460000))
    P.append(tb(nid(), x + 230000, cy + hh + 1740000, pw - 460000, 260000, '반영되면', 1100, 1, BLUE))
    P.append(tb(nid(), x + 230000, cy + hh + 2030000, pw - 460000, 760000, eff, 1400, 1, NAVY))
P.append(box(nid(), L0, 5760000, W, 480000, NAVY, None, 12000))
P.append(tb(nid(), L0, 5760000, W, 480000, '주신 질문은  질문(CQ) → 온톨로지 → 자료 → KG  순서로 반영하여, 실무에 더 맞는 구조로 발전시키겠습니다', 1500, 1, 'FFFFFF', 'ctr', 'ctr'))
new_slide('실무자께 요청드리는 사항', '아래 두 가지를 주시면 실무에 더 맞는 구조로 발전시킬 수 있습니다', 19, P)

# 새 슬라이드 둘을 마지막(감사합니다) 앞으로
ids = prs.slides._sldIdLst; lst = list(ids)
assert len(lst) == 20
for el in lst[18:]: ids.remove(el)
for el in lst[18:]: lst[17].addprevious(el)
prs.save(OUT)
