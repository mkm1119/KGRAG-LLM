#!/usr/bin/env python3
"""pptx 슬라이드에 넣는 '진짜 도형' 그림 부품(이미지 아님): 사각형·타원·원통·선·글상자를 DrawingML로 만들고 그룹으로 묶는다. stdlib만 사용.
좌표는 그림 안의 px 단위로 쓰고 Canvas가 EMU로 바꾼다."""
import re
from xml.sax.saxutils import escape

EMU_PT = 12700
FONT = ('<a:latin typeface="나눔고딕" pitchFamily="50" charset="-127"/><a:ea typeface="나눔고딕" pitchFamily="50" charset="-127"/>'
        '<a:cs typeface="Arial" panose="020B0604020202020204" pitchFamily="34" charset="0"/>')
_id = [5000]


def nid():
    _id[0] += 1
    return _id[0]


def rgb(c):
    return '<a:solidFill><a:srgbClr val="%s"/></a:solidFill>' % c


def tw(text, px):
    """글자 폭 추정(px)"""
    w = 0.0
    for ch in text:
        o = ord(ch)
        w += 0.93 if o > 0x2E80 else 0.32 if ch == ' ' else 0.62 if (ch.isupper() or ch.isdigit()) else 0.52
    return w * px


class Canvas:
    def __init__(self, ox, oy, width_emu, wpx, hpx, name='그림'):
        self.ox, self.oy, self.s = ox, oy, width_emu / float(wpx)
        self.wpx, self.hpx, self.name = wpx, hpx, name
        self.items = []

    def E(self, v):
        return int(round(v * self.s))

    def pt(self, px):
        return int(round(px * self.s / EMU_PT * 100))   # 1/100 pt

    def height_emu(self):
        return self.E(self.hpx)

    def _para(self, text, px, bold=False, color='262626', algn='ctr'):
        return ('<a:p><a:pPr algn="%s"><a:lnSpc><a:spcPct val="100000"/></a:lnSpc></a:pPr><a:r><a:rPr lang="ko-KR" altLang="en-US" sz="%d" b="%d" dirty="0">%s%s</a:rPr><a:t>%s</a:t></a:r></a:p>'
                % (algn, self.pt(px), 1 if bold else 0, rgb(color), FONT, escape(text)))

    def shape(self, prst, x, y, w, h, lines=(), fill=None, line='262626', lw=2.0, dash=False, anchor='ctr', algn='ctr', ins=8, name='도형', adj=None):
        """lines: [(text, px, bold, color)]"""
        paras = ''.join(self._para(t, px, b, c, algn) for (t, px, b, c) in lines) or '<a:p><a:endParaRPr lang="ko-KR"/></a:p>'
        ln = ('<a:ln w="%d">%s%s</a:ln>' % (int(lw * EMU_PT), rgb(line), '<a:prstDash val="dash"/>' if dash else '')) if line else '<a:ln><a:noFill/></a:ln>'
        av = '<a:avLst>%s</a:avLst>' % ('<a:gd name="adj" fmla="val %d"/>' % adj if adj is not None else '')
        i = self.E(ins)
        self.items.append('<p:sp><p:nvSpPr><p:cNvPr id="%d" name="%s"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
                          '<a:prstGeom prst="%s">%s</a:prstGeom>%s%s</p:spPr><p:txBody><a:bodyPr wrap="square" lIns="%d" tIns="%d" rIns="%d" bIns="%d" anchor="%s"><a:noAutofit/></a:bodyPr><a:lstStyle/>%s</p:txBody></p:sp>'
                          % (nid(), name, self.ox + self.E(x), self.oy + self.E(y), self.E(w), self.E(h), prst, av, rgb(fill) if fill else '<a:noFill/>', ln, i, i // 2, i, i // 2, anchor, paras))

    def box(self, x, y, w, h, title, sub=(), tpx=26, spx=21, thick=False, fill='FFFFFF', radius=True):
        lines = [(title, tpx, True, '222222')] + [(t, spx, False, '444444') for t in sub]
        self.shape('roundRect' if radius else 'rect', x, y, w, h, lines, fill=fill, lw=3.5 if thick else 1.75, adj=6000 if radius else None)

    def cyl(self, x, y, w, h, title, px=24):
        self.shape('can', x, y, w, h, [(title, px, True, '222222')], fill='F2F2F2', lw=1.75)

    def panel(self, x, y, w, h, tag, px=25):
        self.shape('rect', x, y, w, h, fill=None, line='888888', lw=1.5, dash=True)
        self.text(x + 10, y + 6, w - 20, px + 12, tag, px, True, '1F3A5F', algn='l')

    def text(self, x, y, w, h, t, px, bold=False, color='222222', algn='ctr', halo=False, anchor='ctr'):
        self.shape('rect', x, y, w, h, [(t, px, bold, color)], fill='FFFFFF' if halo else None, line=None, algn=algn, anchor=anchor, ins=2, name='글상자')

    def label(self, cx, cy, t, px=20, color='222222'):
        w = tw(t, px) + 10
        self.text(cx - w / 2, cy - px * 0.7, w, px * 1.4, t, px, False, color, halo=True)

    def line(self, x1, y1, x2, y2, arrow=True, color='3B4A63', lw=2.5, dash=False):
        x, y = min(x1, x2), min(y1, y2)
        fl = (' flipH="1"' if x2 < x1 else '') + (' flipV="1"' if y2 < y1 else '')
        tail = '<a:tailEnd type="triangle" w="med" len="med"/>' if arrow else ''
        self.items.append('<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="%d" name="선"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr><p:spPr><a:xfrm%s><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
                          '<a:prstGeom prst="line"><a:avLst/></a:prstGeom><a:ln w="%d">%s%s%s</a:ln></p:spPr></p:cxnSp>'
                          % (nid(), fl, self.ox + self.E(x), self.oy + self.E(y), self.E(abs(x2 - x1)), self.E(abs(y2 - y1)), int(lw * EMU_PT), rgb(color),
                             '<a:prstDash val="dash"/>' if dash else '', tail))

    def poly(self, pts, color='3B4A63', lw=2.5, dash=False):
        for i in range(len(pts) - 1):
            self.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], arrow=(i == len(pts) - 2), color=color, lw=lw, dash=dash)

    def xml(self):
        x0, y0, w, h = self.ox, self.oy, self.E(self.wpx), self.E(self.hpx)
        return ('<p:grpSp><p:nvGrpSpPr><p:cNvPr id="%d" name="%s"/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/>'
                '<a:chOff x="%d" y="%d"/><a:chExt cx="%d" cy="%d"/></a:xfrm></p:grpSpPr>%s</p:grpSp>' % (nid(), self.name, x0, y0, w, h, x0, y0, w, h, ''.join(self.items)))


def fig_framework(ox, oy, width_emu):
    """그림 1: Ontology 설계 → KG 구축 → 질문 응답(자동화와 LLM)"""
    c = Canvas(ox, oy, width_emu, 1000, 560, '그림1 전체 구조')
    c.panel(0, 0, 265, 290, '1 Ontology 설계', 22)
    c.box(20, 48, 225, 100, 'CQ', ['전체 질문 1개', '세부 질문 6개'])
    c.line(132, 150, 132, 172)
    c.box(20, 174, 225, 100, 'Class · 관계', ['Class 6, 관계 9', 'Data Property'])
    c.panel(285, 0, 715, 290, '2 KG 구축', 22)
    c.box(300, 50, 160, 225, '원자료 4종', ['승인 기록', '시간 자료', '규정 별표3', '댐 정보'])
    c.line(462, 162, 498, 162)
    c.box(500, 50, 170, 225, '6단계', ['전처리', '매핑 · 추출', '관계 연결', '검증 · 저장'])
    c.line(672, 162, 708, 162)
    c.cyl(710, 46, 275, 70, 'KG (Neo4j)')
    c.cyl(710, 126, 275, 70, '측정자료 저장소')
    c.cyl(710, 206, 275, 70, '문서 저장소')
    c.panel(0, 330, 1000, 215, '3 근거 기반 질의응답', 22)
    xs, w = [14, 214, 414, 614, 814], 172
    c.box(xs[0], 392, w, 140, '사용자', ['질문'], 28, 24)
    c.box(xs[1], 392, w, 140, '질문 해석', ['의도 CQ1~6', '댐 · 시점'], 26, 19)
    c.box(xs[2], 392, w, 140, '근거 검색', ['입력 확인', 'KG · 저장소', '조회'], 26, 19)
    c.box(xs[3], 392, w, 140, '근거 묶음', ['출처 번호 부착', '원값 근거'], 26, 19)
    c.box(xs[4], 392, w, 140, '답변 생성', ['근거 / 판단', '분리 작성'], 26, 19)
    for i in range(4):
        c.line(xs[i] + w + 2, 462, xs[i + 1] - 2, 462)
    c.poly([(848, 278), (848, 312), (500, 312), (500, 390)], color='555555', lw=2.0, dash=True)
    c.text(520, 318, 300, 28, '저장소에서 읽어 옴', 20, False, '444444', algn='l')
    return c


def card(c, x, y, w, cls, ent, lines, px=18):
    for t in ([ent] if ent else []) + lines:
        assert tw(t, px) <= w - 30, ('카드 글이 넓음', t, tw(t, px), w)
    n = (1 if ent else 0) + len(lines)
    h = 66 + n * 28
    c.shape('rect', x, y, w, h, fill='FFFFFF', lw=1.75)
    c.shape('rect', x, y, w, 44, [(cls, 24, True, '1F4E79')], fill='E9EEF5', lw=1.75, algn='l', ins=14)
    items = ([(ent, px, True, '222222')] if ent else []) + [(t, px, False, '222222') for t in lines]
    c.shape('rect', x, y + 46, w, h - 46, items, fill=None, line=None, algn='l', anchor='t', ins=14, name='속성')
    return h


def fig_kg(ox, oy, width_emu, schema=False):
    """그림 2: Class 6, 관계 9를 모두 적용한 충주댐 승인 1368 예시(개체 ID와 Data Property 값 포함)"""
    c = Canvas(ox, oy, width_emu, 1090, 690, '그림2 KG 예시')
    X0, X1, W_ = 45, 620, 440
    if schema:
        hA = card(c, X0, 0, W_, 'Approval', None, ['approvalTime', 'approvalContent'])
        hK = card(c, X1, 0, W_, 'Criterion', None, ['criterionType', 'criterionValue', 'unit'])
    else:
        hA = card(c, X0, 0, W_, 'Approval', 'APR:1368', ['approvalTime = 2012-08-24', 'approvalContent = “방류시작 15:00; 2000㎥/s”'])
        hK = card(c, X1, 0, W_, 'Criterion', 'CRI:CR-02', ['criterionType = 홍수기 제한수위', 'criterionValue = 138.0', 'unit = EL.m'])
    yB = max(hA, hK) + 56
    if schema:
        hB = card(c, X0, yB, W_, 'Operation', None, ['operationType', 'operationTime'])
        hD = card(c, X1, yB, W_, 'Dam', None, ['damName', 'damType'])
    else:
        hB = card(c, X0, yB, W_, 'Operation', 'OPR:1368:1', ['operationType = 탄력적 방류', 'operationTime = 2012-08-24T15:00'])
        hD = card(c, X1, yB, W_, 'Dam', 'DAM:1003110', ['damName = 충주댐', 'damType = 다목적댐'])
    yC = yB + max(hB, hD) + 56
    if schema:
        hC = card(c, X0, yC, W_, 'EvidenceSource', None, ['sourceTitle', 'sourceType', 'sourceLocator'])
        hH = card(c, X1, yC, W_, 'HydrometeorologicalState', None, ['variableType', 'stationCode'])
    else:
        hC = card(c, X0, yC, W_, 'EvidenceSource', 'EVI:AP:1368', ['sourceTitle = 홍수예보 댐방류승인', 'sourceType = 승인자료', 'sourceLocator = 순차번호 1368'])
        hH = card(c, X1, yC, W_, 'HydrometeorologicalState', 'HMS:1003110:수위', ['variableType = 수위', 'stationCode = 1003110'])
    m0, m1 = X0 + 220, X1 + 220
    c.line(m0, hA + 2, m0, yB - 2); c.label(m0 + 80, hA + 35, 'authorizes', 19)
    c.line(X0 + W_ + 2, 90, X1 - 2, yB + 40); c.label(X0 + W_ + 70, 150, 'concernsDam', 18)
    c.line(X0 + W_ + 2, yB + 90, X1 - 2, yB + 90); c.label(X0 + W_ + 68, yB + 68, 'performedOnDam', 15)
    c.line(m1, hK + 2, m1, yB - 2); c.label(m1 + 85, hK + 35, 'appliesToDam', 19)
    c.line(m1, yB + hD + 2, m1, yC - 2); c.label(m1 + 120, yB + hD + 35, 'hasHydrometeorologicalState', 16)
    c.line(m0, yB + hB + 2, m0, yC - 2); c.label(m0 + 70, yB + hB + 35, 'supportedBy', 19)
    c.line(X1 - 2, yC + 90, X0 + W_ + 2, yC + 90); c.label(X0 + W_ + 68, yC + 68, 'supportedBy', 18)
    c.poly([(X0, 70), (18, 70), (18, yC + 120), (X0 - 2, yC + 120)])
    c.poly([(X1 + W_, 70), (1070, 70), (1070, yC + max(hC, hH) + 28), (X0 + 300, yC + max(hC, hH) + 28), (X0 + 300, yC + hC + 2)])
    c.hpx = yC + max(hC, hH) + 62
    yT = yC + max(hC, hH) + 40
    c.text(0, yT, 1090, 28, ('카드: Class 이름과 Data Property.   화살표: 관계(Relation) 9종류' if schema else '카드: Class 이름, 개체(Entity) ID, Data Property = 값.   화살표: 관계(Relation) 9종류'), 20, False, '444444')
    return c


def nlines(text, px, w):
    """글상자 안에서 줄바꿈된 줄 수(추정)"""
    n = 0
    for para in text.split('\n'):
        cur, k = 0.0, 1
        for ch in para:
            cw_ = tw(ch, px)
            if cur + cw_ > w and cur > 0:
                k += 1; cur = cw_
            else:
                cur += cw_
        n += k
    return n


def rows_fig(ox, oy, width_emu, rows, name='그림', lw_=300, px=21, tpx=24, rpx=18, gap=12, thick_rows=()):
    """왼쪽: 단계 이름(굵게)·근거 문헌(작게), 오른쪽: 적용 예시 글. rows: [(제목, 문헌, [예시 줄...])]"""
    W = 1000
    rx = lw_ + 44
    rw = W - rx
    ins = 14
    hs = []
    for t, ref, ex in rows:
        hl = nlines(t, tpx, lw_ - 2 * ins) * tpx * 1.25 + 2 * ins + 6
        hr = sum(nlines(e, px, rw - 2 * ins) for e in ex) * px * 1.28 + 2 * ins + 4
        hs.append(max(hl, hr))
    total = sum(hs) + gap * (len(rows) - 1)
    c = Canvas(ox, oy, width_emu, W, int(total) + 4, name)
    y = 0.0
    for i, ((t, ref, ex), h) in enumerate(zip(rows, hs)):
        lines = [(t, tpx, True, '1F3A5F')]
        c.shape('roundRect', 0, y, lw_, h, lines, fill='E9EEF5', lw=3.5 if i in thick_rows else 1.75, algn='l', ins=ins, adj=6000)
        c.line(lw_ + 4, y + h / 2, rx - 4, y + h / 2)
        c.shape('rect', rx, y, rw, h, [(e, px, False, '222222') for e in ex], fill='FFFFFF', lw=1.75, algn='l', ins=ins)
        y += h + gap
    return c


def fig_build(ox, oy, width_emu):
    rows = [
        ('1 전처리', 'DDKG 3.2.1', ['중복 행 제거, 시각 표기 통일, 4개 댐 선택', '예) 승인 기록 한 행: 순차번호 1368, 충주, 방류시작 2012-08-24 15:00, 접수방류량 2000, 비고 “이내 탄력적 조정”']),
        ('2 구조화 자료 매핑', 'OntoDSMS', ['열 → Data Property, 행 → 개체', '예) Approval APR:1368, EvidenceSource EVI:AP:1368']),
        ('3 문서 자료 추출', 'DDKG 3.2.2', ['글 속의 값을 규칙(키워드, 정규식)으로 추출', '예) 비고 “탄력” → Operation OPR:1368:1 (탄력적 방류), 별표3 → Criterion CRI:CR-02 (제한수위 138.0 EL.m)']),
        ('4 관계 연결', 'Noy & McGuinness Step 7, DDKG ⑦, Li 2025', ['값이 일치하는 개체 쌍에만 관계 생성', '예) 관측소코드 1003110 = 댐 코드 1003110 → APR:1368 ─concernsDam→ DAM:1003110']),
        ('5 검증', 'DDKG 3.2.3, Noy & McGuinness Step 6', ['Ontology의 허용 규칙으로 점검하고, 문제는 Ontology 보완', '예) 승인–댐 연결 부재를 발견해 관계 추가 (8개 → 9개), 도달 가능한 승인 80/80건']),
        ('6 저장', 'DDKG 3.3', ['KG는 Neo4j, 수치·원문은 외부 저장소', '개체 264, 관계 418 / 측정자료 508,246행 / 규정 별표3 원문']),
    ]
    return rows_fig(ox, oy, width_emu, rows, '그림 KG 구축 6단계')


def fig_qa(ox, oy, width_emu):
    rows = [
        ('질문 해석', '', ['질문에서 의도(CQ, 복수 가능)와 대상(댐·시점)을 뽑음']),
        ('1 입력 확인', '', ['의도·대상이 허용 범위인지 확인하고 표기를 맞춤 (범위 밖이면 조회하지 않음)']),
        ('2 KG 조회', '', ['의도별 Cypher 질의 틀로 관계를 따라 개체와 찾아가는 키를 가져옴']),
        ('3 저장소 조회', '', ['키로 측정값·규정 원문을 읽음 (값은 원값 그대로)']),
        ('4 근거 묶음 구성', '', ['의도별 구역으로 모으고 항목마다 출처 번호를 붙임']),
        ('답변 생성', '', ['근거 묶음과 근거 사용 원칙(근거만 사실로, 출처 번호 표기)을 받아 답변', '근거: 사실과 출처 번호  /  판단: 판단임을 밝히고 근거 표시  /  없는 내용: “자료에 없음”']),
    ]
    return rows_fig(ox, oy, width_emu, rows, '그림 질의응답 흐름')


def fig_steps(ox, oy, width_emu):
    """KG 구축 6단계(한 줄 설명)"""
    c = Canvas(ox, oy, width_emu, 1000, 300, '그림 KG 구축 6단계')
    items = [('1 전처리', '중복·표기 정리, 대상 댐 선택'), ('2 구조화 자료 매핑', '표의 열·행을 속성·개체로 옮김'), ('3 문서 자료 추출', '글 속의 값을 규칙으로 추출'),
             ('4 관계 연결', '값이 일치하는 개체 쌍에 관계 생성'), ('5 검증', '허용 규칙으로 점검, Ontology 보완'), ('6 저장', 'KG는 Neo4j, 측정값·원문은 저장소')]
    w, h = 300, 125
    xs = [0, 350, 700]
    for i, (t, d) in enumerate(items):
        x = xs[i % 3]; y = 0 if i < 3 else 175
        c.shape('roundRect', x, y, w, h, [(t, 26, True, '1F3A5F'), (d, 21, False, '222222')], fill='E9EEF5', lw=1.75, adj=6000)
    c.line(302, 62, 348, 62); c.line(652, 62, 698, 62)
    c.poly([(850, 127), (850, 150), (150, 150), (150, 173)])
    c.line(302, 237, 348, 237); c.line(652, 237, 698, 237)
    return c
