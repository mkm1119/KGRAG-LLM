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


def fig_kg():
    g = Svg(760)
    w, h = 270, 130
    cx = [0, 365, 730]; cy = [10, 270, 530]
    def ell(c, r, cls, name):
        x, y = cx[c], cy[r]
        g.add('<ellipse cx="%d" cy="%d" rx="%d" ry="%d" fill="#fff" stroke="%s" stroke-width="2.5"/>' % (x + w / 2, y + h / 2, w / 2, h / 2, NAVY))
        g.text(x + w / 2, y + h / 2 - 8, cls, 24, False, NAVY); g.text(x + w / 2, y + h / 2 + 30, name, 28, True, INK)
    def rec(c, r, cls, name):
        x, y = cx[c], cy[r]
        g.rect(x, y + 10, w, h - 20, '#f2f2f2', INK, 2.5, None, 4)
        g.text(x + w / 2, y + h / 2 - 8, cls, 24, False, '#444'); g.text(x + w / 2, y + h / 2 + 30, name, 28, True, INK)
    ell(0, 0, 'Approval', '승인 1368'); ell(1, 0, 'Criterion', '제한수위 138.0'); rec(2, 0, 'EvidenceSource', '규정 별표3')
    ell(0, 1, 'Operation', '탄력적 방류'); ell(1, 1, 'Dam', '충주댐'); ell(2, 1, 'HMS', '충주댐_수위')
    rec(0, 2, 'EvidenceSource', '승인 기록'); rec(2, 2, 'EvidenceSource', 'K-water 자료')
    L = lambda *a: g.line(*a, INK, 'ar', None, 3)
    L(135, 142, 135, 268); g.text(150, 214, 'authorizes', 22, False, INK, 'start', True)
    L(235, 125, 420, 272); g.text(300, 176, 'concernsDam', 22, False, INK, 'start', True)
    L(500, 142, 500, 268); g.text(515, 214, 'appliesToDam', 22, False, INK, 'start', True)
    L(635, 75, 728, 75); g.text(682, 59, 'supportedBy', 20, False, INK, 'middle', True)
    L(270, 335, 363, 335); g.text(317, 319, 'performedOnDam', 18, False, INK, 'middle', True)
    L(635, 335, 728, 335); g.text(682, 319, 'hasHMS', 20, False, INK, 'middle', True)
    L(135, 402, 135, 528); g.text(150, 474, 'supportedBy', 22, False, INK, 'start', True)
    L(865, 402, 865, 528); g.text(880, 474, 'supportedBy', 22, False, INK, 'start', True)
    g.text(500, 700, '값은 KG 밖: stationCode 로 측정자료, sourceLocator 로 문서를 찾아감', 22, False, '#444', 'middle')
    g.text(500, 735, '타원: 개체,  사각형: 근거자료,  HMS = HydrometeorologicalState', 20, False, '#444', 'middle')
    g.save('meeting_fig2_kg')


if __name__ == '__main__':
    fig_framework(); fig_kg()
