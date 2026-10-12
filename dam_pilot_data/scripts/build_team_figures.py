#!/usr/bin/env python3
"""LLM 연구팀 공유 요약본의 그림 4개를 SVG(HTML)로 만들고 Chromium(Playwright)으로 PNG 렌더링.
글씨는 최소 24px, 폭 1500px 기준. 사용: python3 scripts/build_team_figures.py  (NODE_PATH, Playwright 필요)
"""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'team_brief')
W = 1500

HEAD = ('<!doctype html><html><head><meta charset="utf-8"><style>body{margin:0;background:#fff;font-family:\'WenQuanYi Zen Hei\',\'Noto Sans CJK KR\',sans-serif}'
        'svg text{font-family:\'WenQuanYi Zen Hei\',\'Noto Sans CJK KR\',sans-serif}</style></head><body>')
DEFS = ('<defs>'
        '<marker id="ar" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 z" fill="#44546a"/></marker>'
        '<marker id="arg" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 z" fill="#2e7d32"/></marker>'
        '<marker id="arp" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 z" fill="#7e57c2"/></marker>'
        '<marker id="arh" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 z" fill="#78909c"/></marker>'
        '</defs>')
COL = {  # fill, stroke, title-color
    'gray': ('#f5f5f5', '#757575', '#212121'), 'src': ('#eceff1', '#78909c', '#263238'),
    'llm': ('#fff3e0', '#ef6c00', '#bf360c'), 'auto': ('#e3f2fd', '#1976d2', '#0d47a1'),
    'store': ('#e8f5e9', '#2e7d32', '#1b5e20'), 'onto': ('#ede7f6', '#7e57c2', '#311b92'),
}


class Svg:
    def __init__(self, h):
        self.h = h
        self.p = []

    def add(self, s):
        self.p.append(s)

    def rect(self, x, y, w, h, fill, stroke, sw=3, dash=None, rx=14):
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        self.add('<rect x="%d" y="%d" width="%d" height="%d" rx="%d" fill="%s" stroke="%s" stroke-width="%d"%s/>' % (x, y, w, h, rx, fill, stroke, sw, d))

    def text(self, x, y, t, size=24, bold=False, fill='#37474f', anchor='middle', halo=False):
        t = t.replace('&', '&amp;')
        extra = ' stroke="#fff" stroke-width="7" paint-order="stroke"' if halo else ''
        self.add('<text x="%d" y="%d" font-size="%d"%s fill="%s" text-anchor="%s"%s>%s</text>' % (x, y, size, ' font-weight="bold"' if bold else '', fill, anchor, extra, t))

    def line(self, x1, y1, x2, y2, color='#44546a', mk='ar', dash=None, sw=4):
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        m = ' marker-end="url(#%s)"' % mk if mk else ''
        self.add('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="%d"%s%s/>' % (x1, y1, x2, y2, color, sw, d, m))

    def path(self, d, color='#44546a', mk='ar', dash=None, sw=4):
        dd = ' stroke-dasharray="%s"' % dash if dash else ''
        m = ' marker-end="url(#%s)"' % mk if mk else ''
        self.add('<path d="%s" fill="none" stroke="%s" stroke-width="%d"%s%s/>' % (d, color, sw, dd, m))

    def node(self, x, y, w, h, kind, title, lines=(), tsize=30, bsize=25, dash=None, label=None):
        f, s, c = COL[kind]
        self.rect(x, y, w, h, f, s, 3, dash)
        cy = y + 44
        if label:
            self.text(x + w / 2, cy, label, 24, False, c)
            cy += 46
        self.text(x + w / 2, cy, title, tsize, True, c)
        cy += 14
        for ln in lines:
            cy += bsize + 10
            self.text(x + w / 2, cy, ln, bsize, False, '#37474f')

    def save(self, name):
        html = HEAD + '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, self.h, W, self.h) + DEFS
        html += '<rect width="%d" height="%d" fill="#fff"/>' % (W, self.h) + ''.join(self.p) + '</svg></body></html>'
        hp = os.path.join(OUT, name + '.html')
        open(hp, 'w', encoding='utf-8').write(html)
        script = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});"
                  "const p=await b.newPage({viewport:{width:%d,height:%d},deviceScaleFactor:1.4});await p.goto('file://%s');"
                  "await p.screenshot({path:'%s',clip:{x:0,y:0,width:%d,height:%d}});await b.close();})();") % (
            W, self.h, os.path.abspath(hp), os.path.abspath(os.path.join(OUT, name + '.png')), W, self.h)
        env = dict(os.environ, NODE_PATH='/opt/node22/lib/node_modules')
        subprocess.run(['node', '-e', script], check=True, env=env)
        print('저장', name, W, self.h)


def panel(g, y, h, fill, stroke, title, sub=None, tcolor='#1f4e79'):
    g.rect(15, y, 1470, h, fill, stroke, 2, None, 18)
    g.text(40, y + 50, title, 34, True, tcolor, 'start')
    if sub:
        g.text(40, y + 92, sub, 25, False, '#44546a', 'start')


# =============================================================== 그림 1: 큰 틀 전체와 하이브리드 검색
def fig1():
    g = Svg(1300)
    LC, CC, RC = 40, 550, 1060          # 왼쪽(문서)·가운데(KG)·오른쪽(측정자료) 열의 x
    CW = 400
    xs = (LC + CW / 2, CC + CW / 2, RC + CW / 2)
    # STEP 1
    g.node(40, 15, 1420, 125, 'onto', 'STEP 1  Ontology 설계', ['무엇이 있고 어떻게 연결되는지 정한 설계도 (개체 6종류, 관계 9종류)'], 32, 25)
    g.line(750, 142, 750, 193, '#7e57c2', 'arp')
    g.text(778, 176, '설계에 맞춰 구축', 26, False, '#4527a0', 'start')
    # STEP 2
    g.node(40, 195, 1420, 140, 'auto', 'STEP 2  지식그래프(KG) 구축 (자동 처리)',
           ['원자료(방류 승인 기록, 수문기상 시간 자료, 규정 별표3)를', '설계에 맞게 정리해 세 저장소에 나누어 담는다'], 32, 25)
    for x in xs:
        g.line(int(x), 337, int(x), 418)
    # 저장소
    g.node(LC, 420, CW, 150, 'store', '문서 저장소', ['규정 원문 전체'], 29, 25)
    g.node(CC, 420, CW, 150, 'store', '지식그래프 (KG)', ['관계와 근거의 위치(번호)'], 29, 25)
    g.node(RC, 420, CW, 150, 'store', '측정자료 저장소', ['시간별 측정값 전체'], 29, 25)
    # STEP 3 패널
    py = 610
    g.rect(15, py, 1470, 585, '#fffaf2', '#d9b36c', 2, None, 18)
    g.text(300, py + 48, 'STEP 3  질문 응답', 34, True, '#7a4b00', 'start')
    cy = py + 70                                   # 하이브리드 컨테이너 상단
    g.rect(25, cy, 1450, 275, '#f1f8f1', '#2e7d32', 3, '12 8', 16)
    ly = cy + 25
    g.node(LC, ly, CW, 175, 'store', '문서 검색', ['KG가 알려 준 조각 번호로', '규정 원문을 읽어 온다'], 29, 24)
    g.node(CC, ly, CW, 175, 'store', 'KG 검색', ['연결을 따라가며 관련 승인·', '기준과 근거의 위치를 찾는다'], 29, 24)
    g.node(RC, ly, CW, 175, 'store', '측정자료 검색', ['KG가 알려 준 측정소 번호로', '시간별 숫자를 읽어 온다'], 29, 24)
    for x in xs:
        g.line(int(x), 572, int(x), ly - 2, '#2e7d32', 'arg')
    g.line(CC - 2, ly + 100, LC + CW + 2, ly + 100, '#2e7d32', 'arg')
    g.line(CC + CW + 2, ly + 100, RC - 2, ly + 100, '#2e7d32', 'arg')
    g.text(495, ly + 82, '번호', 25, False, '#2e7d32')
    g.text(1005, ly + 82, '번호', 25, False, '#2e7d32')
    g.text(750, cy + 252, '하이브리드 검색: 출처마다 맞는 방식으로 찾아 합친다', 28, True, '#1b5e20')
    # 질문 → 해석 → (검색) → 답변
    ry = cy + 275 + 62
    g.node(40, ry, 330, 165, 'gray', '사용자 질문', ['“소양강댐 지금 상태와', '비슷했던 과거 사례는?”'], 29, 24)
    g.node(430, ry, 430, 165, 'llm', '질문 해석 (LLM)', ['어느 댐, 어느 시점에 대해', '무엇을 묻는지 정리'], 29, 24)
    g.node(1000, ry, 460, 165, 'llm', '근거 통합 · LLM 답변', ['합친 근거 안에서만 설명하고', '출처를 표시한다'], 29, 24)
    g.line(372, ry + 82, 428, ry + 82)
    g.line(645, ry - 2, 645, cy + 277, '#44546a', 'ar')
    g.text(668, ry - 18, '찾을 내용', 25, False, '#44546a', 'start')
    g.line(1230, cy + 277, 1230, ry - 2, '#44546a', 'ar')
    g.text(1253, ry - 18, '모은 근거', 25, False, '#44546a', 'start')
    fy = ry + 165 + 85
    g.text(40, fy, 'KG에는 수치 전체나 원문 전체를 넣지 않고, 연결 관계와 근거의 위치(번호)만 둔다.', 25, False, '#44546a', 'start')
    g.text(40, fy + 38, '주황색은 LLM이 하는 일이다. 질문은 해석 → 하이브리드 검색 → 답변 순서로 처리된다.', 25, False, '#44546a', 'start')
    g.rects_fix = None
    pan = [i for i, x in enumerate(g.p) if x.startswith('<rect x="15" y="%d"' % py)][0]
    g.p[pan] = '<rect x="15" y="%d" width="1470" height="%d" rx="18" fill="#fffaf2" stroke="#d9b36c" stroke-width="2"/>' % (py, ry + 165 + 30 - py)
    g.h = fy + 38 + 40
    g.save('fig0_framework')


# =============================================================== 그림 2: STEP 1·2
def fig2():
    g = Svg(1000)
    panel(g, 15, 300, '#f3f0fa', '#9c8fc7', 'STEP 1. Ontology 설계: 먼저 정한 설계도', None, '#4527a0')
    g.node(40, 95, 400, 205, 'onto', '답해야 할 질문 7개', ['예) 지금 제한수위는?', '비슷했던 과거의 승인은?'], 28, 25)
    g.node(500, 95, 520, 205, 'onto', '개체 6종류 · 관계 9종류', ['댐, 수문기상 상태, 방류 승인,', '운영행위, 운영기준, 근거자료', '관계 예) 승인이 운영행위를 허가'], 28, 25)
    g.node(1080, 95, 380, 205, 'onto', '설계도의 쓰임', ['① KG를 만드는 틀', '② 질문 유형의 기준'], 28, 25)
    g.line(442, 200, 498, 200, '#7e57c2', 'arp')
    g.line(1022, 200, 1078, 200, '#7e57c2', 'arp')
    g.line(760, 302, 760, 392, '#7e57c2', 'arp')
    g.text(785, 360, '이 설계에 맞춰 구축', 26, False, '#4527a0', 'start')

    y0 = 395
    panel(g, y0, 590, '#f7f9fc', '#9fb3c8', 'STEP 2. 사전 구축: 자료를 구조화해 세 저장소에 담는다', '한 번 수행하고 자료가 바뀌면 갱신한다. LLM 없이 미리 정한 규칙으로 자동 처리한다.')
    sy = y0 + 125
    src = [('방류 승인 기록 (표)', ['4개 댐 80건']), ('수문기상 자료 (표)', ['시간별 약 50.8만 줄']), ('규정 별표3 (글)', ['홍수기 제한수위'])]
    for i, (t, ls) in enumerate(src):
        g.node(40, sy + i * 150, 380, 130, 'src', t, ls, 27, 25)
    g.rect(500, sy, 460, 430, '#e3f2fd', '#1976d2', 3)
    g.text(730, sy + 48, 'KG 구축 7단계 (자동 처리)', 28, True, '#0d47a1')
    for i, t in enumerate(['1 자료 유형 구분 (표/글)', '2 전처리 (중복·시각 정리)', '3 표의 열을 속성으로 매핑', '4 글에서 값 추출 (규칙)', '5 같은 댐끼리 개체 연결', '6 구조 규칙 검증', '7 저장 (Neo4j에 적재)']):
        g.text(525, sy + 98 + i * 42, t, 25, False, '#0d47a1', 'start')
    g.text(730, sy + 410, '문헌 방법 참고, 그 외 연구자 판단', 24, False, '#37474f')
    for i in range(3):
        g.line(422, sy + 65 + i * 150, 498, sy + 150 + i * 65 - 15 + (0 if i == 1 else 0))
    stores = [('지식그래프 (Neo4j)', ['개체(점) 273개', '관계(선) 457개']), ('측정자료 저장소', ['시간별 값 전체', '(KG에는 번호만)']), ('문서 저장소', ['별표3 원문 10조각', '(KG에는 번호만)'])]
    for i, (t, ls) in enumerate(stores):
        g.node(1020, sy + i * 150, 440, 142, 'store', t, ls, 27, 24)
    for i in range(3):
        g.line(962, sy + 150 + i * 65 - 15, 1018, sy + 65 + i * 150)
    g.h = y0 + 590 + 15
    g.save('fig1a_step12')


# =============================================================== 그림 3: STEP 3
def fig3():
    g = Svg(1000)
    panel(g, 15, 985, '#fffaf2', '#d9b36c', 'STEP 3. 질문 처리: 질문이 올 때마다 수행한다', 'LLM은 처음(질문 해석)과 끝(답변 작성)에만 쓰고, 가운데는 규칙으로 자동 처리한다.', '#7a4b00')
    L, R = 40, 780
    bw, bh = 680, 160
    y1, y2, y3, y4 = 140, 345, 550, 755
    g.node(L, y1, bw, bh, 'gray', '사용자 질문', ['“소양강댐 지금 상태와', '비슷했던 과거 사례는?”'])
    g.node(R, y1, bw, bh, 'llm', '① 질문 해석 [LLM]', ['질문 유형과 댐·기간 값을', '정해진 형식(JSON)으로 출력'])
    g.line(722, y1 + 80, 778, y1 + 80)
    g.line(1120, y1 + bh + 2, 1120, y2 - 2)
    g.node(R, y2, bw, bh, 'auto', '② 값 검증 [자동]', ['질문 유형, 댐, 날짜 형식 확인', '어긋나면 “범위 밖” 처리'])
    g.node(L, y2, bw, bh, 'auto', '③ KG 조회 [자동]', ['질문 유형별 조회문에 값을 채워', 'KG(Neo4j)에서 조회'])
    g.line(778, y2 + 80, 722, y2 + 80)
    g.line(380, y2 + bh + 2, 380, y3 - 2)
    g.node(L, y3, bw, bh, 'auto', '④ 저장소 조회 [자동]', ['KG가 알려 준 번호로', '측정값과 규정 원문을 읽어 옴'])
    g.node(R, y3, bw, bh, 'auto', '⑤ 비교 값 계산 [자동]', ['제한수위와의 차이, 승인량 대비', '비율, 비슷한 과거 사례 선택'])
    g.line(722, y3 + 80, 778, y3 + 80)
    g.line(1120, y3 + bh + 2, 1120, y4 - 2)
    g.node(R, y4, bw, bh, 'llm', '⑥ 답변 작성 [LLM]', ['③~⑤ 결과를 번호 붙은 근거 모음으로', '받아 출처 번호를 붙여 한국어로 답변'])
    g.node(L, y4, bw, bh, 'gray', '답변', ['+ 출처 번호'])
    g.line(778, y4 + 80, 722, y4 + 80)
    ly = y4 + bh + 55
    items = [(40, 'llm', 'LLM이 하는 일'), (390, 'auto', '규칙으로 자동 처리'), (800, 'gray', '입출력')]
    for x, k, t in items:
        f, s, _ = COL[k]
        g.rect(x, ly - 28, 36, 36, f, s, 3, None, 6)
        g.text(x + 50, ly, t, 25, False, '#37474f', 'start')
    g.h = 1000 + 15
    g.save('fig1b_step3')


# =============================================================== 그림 4: KG 예시
def fig4():
    g = Svg(1560)
    g.text(40, 62, '지식그래프의 일부: 충주댐 승인 1368번 한 건', 36, True, '#1f4e79', 'start')
    g.text(40, 108, '점은 개체, 검은 화살표는 의미 관계, 회색 화살표는 근거자료를 가리키는 관계,', 25, False, '#546e7a', 'start')
    g.text(40, 142, '초록 파선은 KG 밖 저장소를 찾아가는 번호이다.', 25, False, '#546e7a', 'start')
    c1, c2, c3, nw, nh = 50, 570, 1090, 360, 150
    R0, R1, R2, R3, R4 = 180, 455, 755, 1055, 1355

    def nd(x, y, fill, stroke, tc, label, main, detail, msize=31):
        g.rect(x, y, nw, nh, fill, stroke, 3)
        g.text(x + nw / 2, y + 40, label, 24, False, tc)
        g.text(x + nw / 2, y + 87, main, msize, True, '#212121')
        g.text(x + nw / 2, y + 128, detail, 24, False, '#37474f')
    nd(c1, R1, '#ffe0b2', '#ef6c00', '#bf360c', '방류 승인 (Approval)', '승인 1368', '승인일 2012-08-24')
    nd(c2, R1, '#e1bee7', '#8e24aa', '#6a1b9a', '운영기준 (Criterion)', '홍수기 제한수위', '138.0 EL.m')
    nd(c1, R2, '#ffccbc', '#d84315', '#bf360c', '운영행위 (Operation)', '탄력적 방류', '시각 2012-08-24 16:00')
    nd(c2, R2, '#bbdefb', '#1565c0', '#0d47a1', '댐 (Dam)', '충주댐', '다목적댐', 34)
    nd(c3, R2, '#b2dfdb', '#00796b', '#00695c', '수문기상 상태 (HMS)', '충주댐_수위', '측정소 번호 1003110')
    nd(c1, R3, '#fff9c4', '#f9a825', '#7a5b00', '근거자료 (EvidenceSource)', '방류 승인 기록', '한강홍수통제소 1368번', 31)
    nd(c3, R3, '#fff9c4', '#f9a825', '#7a5b00', '근거자료 (EvidenceSource)', 'K-water 시간자료', '댐코드 1003110', 31)
    nd(c3, R1, '#fff9c4', '#f9a825', '#7a5b00', '근거자료 (EvidenceSource)', '연계운영규정 별표3', '조각 번호 LAW:별표3', 29)
    for (x, y, t, d) in [(c3, R0, '문서 저장소 (KG 밖)', '별표3 원문 전체'), (c3, R4, '측정자료 저장소 (KG 밖)', '시간별 측정값 전체')]:
        g.rect(x, y, nw, 130, '#e8f5e9', '#2e7d32', 3, '12 8')
        g.text(x + nw / 2, y + 52, t, 27, True, '#1b5e20')
        g.text(x + nw / 2, y + 97, d, 24, False, '#33691e')
    K, G = '#263238', '#78909c'
    # 의미 관계
    g.line(230, R1 + nh + 2, 230, R2 - 3, K)
    g.text(252, 690, '허가한다', 26, False, K, 'start')
    g.line(412, R1 + 100, 640, R2 - 3, K)
    g.text(512, 668, '대상 댐', 26, False, K, 'end', True)
    g.line(750, R1 + nh + 2, 750, R2 - 3, K)
    g.text(772, 690, '적용되는 댐', 26, False, K, 'start')
    g.line(412, R2 + 75, 568, R2 + 75, K)
    g.text(490, R2 + 52, '수행된 댐', 26, False, K, 'middle')
    g.line(932, R2 + 75, 1088, R2 + 75, K)
    g.text(1010, R2 + 52, '상태 보유', 26, False, K, 'middle')
    # 근거
    g.line(932, R1 + 75, 1088, R1 + 75, G, 'arh')
    g.text(1010, R1 + 52, '근거', 26, False, '#546e7a', 'middle')
    g.line(230, R2 + nh + 2, 230, R3 - 3, G, 'arh')
    g.text(252, 990, '근거', 26, False, '#546e7a', 'start')
    g.line(1270, R2 + nh + 2, 1270, R3 - 3, G, 'arh')
    g.text(1292, 990, '근거', 26, False, '#546e7a', 'start')
    g.path('M50,%d L20,%d L20,%d L48,%d' % (R1 + 75, R1 + 75, R3 + 75, R3 + 75), G, 'arh')
    # KG 밖 저장소로
    g.line(1270, R1 - 2, 1270, R0 + 134, '#2e7d32', 'arg', '12 8')
    g.text(1245, 385, '조각 번호로 찾아감', 25, False, '#2e7d32', 'end')
    g.line(1270, R3 + nh + 2, 1270, R4 - 3, '#2e7d32', 'arg', '12 8')
    g.text(1245, 1290, '측정소 번호로 찾아감', 25, False, '#2e7d32', 'end')
    g.h = R4 + 130 + 30
    g.save('fig2_kg_example')


if __name__ == '__main__':
    fig1(); fig2(); fig3(); fig4()
