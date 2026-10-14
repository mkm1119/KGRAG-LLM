#!/usr/bin/env python3
"""교수님 회의자료용 그림 2개(논문식 흑백 도식). 포스터 그림 부품(build_poster_figures.py)을 재사용한다.
사용: NODE_PATH=/opt/node22/lib/node_modules python3 scripts/build_meeting_figures.py"""
import importlib.util, os
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('pf', os.path.join(HERE, 'build_poster_figures.py')); pf = importlib.util.module_from_spec(spec); spec.loader.exec_module(pf)
OUT = os.path.join(HERE, '..', '..', 'lab_meeting', 'meeting_figs'); os.makedirs(OUT, exist_ok=True)
pf.tf.OUT = OUT; pf.tf.W = 1000
Svg, box, cyl, panel, INK, NAVY = pf.Svg, pf.box, pf.cyl, pf.panel, pf.INK, pf.NAVY


def fig_framework():
    g = Svg(780)
    panel(g, 0, 0, 265, 330, '(a) Ontology 설계')
    box(g, 20, 52, 225, 125, 'CQ', ['전체 질문 1개', '세부 질문 6개'])
    g.line(132, 179, 132, 213, INK, 'ar')
    box(g, 20, 213, 225, 112, 'Class · 관계', ['Class 6, Relation 9', 'Data Property'])
    panel(g, 285, 0, 715, 330, '(b) 지식그래프(KG) 구축')
    box(g, 300, 60, 160, 250, '원자료 4종', ['승인 기록', '시간 자료', '규정 별표3', '댐 정보'], 26, 22)
    g.line(462, 185, 498, 185, INK, 'ar')
    box(g, 500, 60, 170, 250, '6단계', ['전처리', '매핑 · 추출', '관계 연결', '검증 · 저장'], 26, 21)
    g.line(672, 185, 708, 185, INK, 'ar')
    cyl(g, 710, 52, 275, 84, 'KG (Neo4j)', None)
    cyl(g, 710, 144, 275, 84, '측정자료 저장소', None)
    cyl(g, 710, 236, 275, 84, '문서 저장소', None)
    panel(g, 0, 380, 1000, 380, '(c) 질문 응답 (RAG)')
    xs = [14, 214, 414, 614, 814]; ws = 172
    box(g, xs[0], 450, ws, 150, '사용자', ['질문'], 28, 24)
    box(g, xs[1], 450, ws, 150, '질문 해석', ['의도 CQ1~6', '댐 · 시점'], 26, 20, sw=5)
    box(g, xs[2], 450, ws, 150, '근거 검색', ['입력 확인', 'KG · 저장소 조회'], 26, 20)
    box(g, xs[3], 450, ws, 150, '근거 묶음', ['출처 번호가 붙은', '원값 근거'], 26, 20)
    box(g, xs[4], 450, ws, 150, '답변 생성', ['근거 / 판단', '분리해서 작성'], 26, 20, sw=5)
    for i in range(4):
        g.line(xs[i] + ws + 2, 525, xs[i + 1] - 2, 525, INK, 'ar')
    g.path('M848,324 L848,360 L500,360 L500,448', '#555', 'ar', '8 6', 3)
    g.text(520, 350, '저장소에서 읽어 옴', 24, False, '#444', 'start')
    # 역할 막대
    g.rect(214, 630, 172, 44, '#fff', INK, 5, None, 4); g.text(300, 660, 'LLM', 24, True, INK)
    g.rect(414, 630, 372, 44, '#fff', INK, 2.5, None, 4); g.text(600, 660, '자동화 (코드)', 24, True, INK)
    g.rect(814, 630, 172, 44, '#fff', INK, 5, None, 4); g.text(900, 660, 'LLM', 24, True, INK)
    g.text(500, 725, '굵은 테두리: LLM 파트 (논의 대상),  가는 테두리: 정해진 규칙으로 구현', 22, False, '#444')
    g.save('meeting_fig1_framework')


def card(g, x, y, w, cls, ent, lines):
    n = 1 + len(lines); h = 70 + n * 26 - 14
    g.rect(x, y, w, h, '#fff', INK, 2.5, None, 6)
    g.rect(x, y, w, 44, '#e9eef5', INK, 2.5, None, 6)
    g.text(x + 14, y + 31, cls, 23, True, NAVY, 'start')
    g.text(x + 14, y + 74, ent, 16, True, '#222', 'start')
    for i, ln in enumerate(lines):
        g.text(x + 14, y + 74 + (i + 1) * 26, ln, 16, False, '#222', 'start')
    return h


def vtext(g, x, y, t, size=18):
    g.add('<text transform="translate(%d,%d) rotate(-90)" font-size="%d" fill="#222" text-anchor="middle" stroke="#fff" stroke-width="6" paint-order="stroke">%s</text>' % (x, y, size, t))


def fig_kg():
    """Ontology의 Class 6개, Relation 9개를 모두 그린 KG 예시(충주댐 승인 1368)."""
    pf.tf.W = 1050
    g = Svg(720)
    X0, X1, W_ = 45, 575, 400
    hA = card(g, X0, 0, W_, 'Approval', 'APR:1368', ['approvalTime = 2012-08-24', 'approvalContent = “방류시작 2012-08-24 15:00;', '  접수방류량 2000㎥/s; 비고: 이내 탄력적 조정”'])
    hK = card(g, X1, 0, W_, 'Criterion', 'CRI:CR-02', ['criterionType = 홍수기 제한수위', 'criterionValue = 138.0', 'unit = EL.m'])
    yB = hA + 60
    hB = card(g, X0, yB, W_, 'Operation', 'OPR:1368:1', ['operationType = 탄력적 방류', 'operationTime = 2012-08-24T15:00'])
    hD = card(g, X1, yB, W_, 'Dam', 'DAM:1003110', ['damName = 충주댐', 'damType = 다목적댐'])
    yC = yB + hB + 55
    hC = card(g, X0, yC, W_, 'EvidenceSource', 'EVI:AP:1368', ['sourceTitle = 한강홍수통제소 홍수예보 댐방류승인', 'sourceType = 승인자료', 'sourceLocator = 순차번호 1368'])
    hH = card(g, X1, yC, W_, 'HydrometeorologicalState', 'HMS:1003110:수위', ['variableType = 수위', 'stationCode = 1003110'])
    L = lambda *a: g.line(*a, INK, 'ar', None, 3)
    mx0, mx1 = X0 + 215, X1 + 215
    # Approval --authorizes--> Operation
    L(mx0, hA + 2, mx0, yB - 2); g.text(mx0 + 15, hA + 36, 'authorizes', 20, False, INK, 'start', True)
    # Approval --concernsDam--> Dam
    L(X0 + W_ + 2, 110, X1 - 2, yB + 30); g.text(510, 165, 'concernsDam', 20, False, INK, 'middle', True)
    # Operation --performedOnDam--> Dam
    L(X0 + W_ + 2, yB + 74, X1 - 2, yB + 74); g.text(510, yB + 62, 'performedOnDam', 18, False, INK, 'middle', True)
    # Criterion --appliesToDam--> Dam
    L(mx1, hK + 2, mx1, yB - 2); g.text(mx1 + 15, hK + 36, 'appliesToDam', 20, False, INK, 'start', True)
    # Dam --hasHydrometeorologicalState--> HMS
    L(mx1, yB + hD + 2, mx1, yC - 2); g.text(mx1, yB + hD + 34, 'hasHydrometeorologicalState', 17, False, INK, 'middle', True)
    # supportedBy: Operation, HMS (direct), Approval (left margin), Criterion (right margin, bottom)
    L(mx0, yB + hB + 2, mx0, yC - 2); g.text(mx0 + 15, yB + hB + 36, 'supportedBy', 20, False, INK, 'start', True)
    L(X1 - 2, yC + 70, X0 + W_ + 2, yC + 70); g.text(510, yC + 58, 'supportedBy', 20, False, INK, 'middle', True)
    g.path('M%d,60 L16,60 L16,%d L%d,%d' % (X0, yC + 100, X0 - 2, yC + 100), INK, 'ar', None, 3)
    vtext(g, 34, yB + 40, 'supportedBy')
    yBot = yC + max(hC, hH) + 28
    g.path('M%d,60 L1030,60 L1030,%d L300,%d L300,%d' % (X1 + W_, yBot, yBot, yC + hC + 2), INK, 'ar', None, 3)
    vtext(g, 1014, yB + 40, 'supportedBy')
    yT = yBot + 40
    g.text(525, yT, '카드: 위쪽 Class, 첫 줄 개체(Entity) ID, 아래 Data Property = 값.  화살표: 관계(Relation)', 20, False, '#444', 'middle')
    g.text(525, yT + 28, '값 자체(측정값, 규정 원문)는 KG 밖 저장소에 두고, KG에는 찾아가는 키(stationCode, sourceLocator)만 둔다', 20, False, '#444', 'middle')
    g.h = yT + 50
    g.save('meeting_fig2_kg')
    pf.tf.W = 1000


if __name__ == '__main__':
    fig_framework(); fig_kg()
