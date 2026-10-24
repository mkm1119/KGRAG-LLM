#!/usr/bin/env python3
"""10월 월간 공정보고용 그림: 그림 1(RAG-sLLM 아키텍처 구성 계층), 그림 2(데이터 파이프라인: 수집 → 전처리 → 지식기반 구성).
두 그림은 '지식기반' 블록을 같은 이름·색으로 그려 11월에 하나의 통합 구조로 합칠 수 있게 한다.
사용: NODE_PATH=/opt/node22/lib/node_modules python3 scripts/build_report_figs.py"""
import importlib.util, os
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('bc', os.path.join(HERE, 'build_cards.py')); bc = importlib.util.module_from_spec(spec); spec.loader.exec_module(bc)
OUT = os.path.join(HERE, '..', '..', 'lab_meeting', 'report_figs'); os.makedirs(OUT, exist_ok=True)
bc.pf.tf.OUT = OUT
Svg, NAVY, INK = bc.Svg, bc.NAVY, bc.INK
tbox, arrow_h, finish, lines, wrap = bc.tbox, bc.arrow_h, bc.finish, bc.lines, bc.wrap
BLUE, GREEN, GRAY, YEL, WHITE = bc.BLUE, bc.GREEN, bc.GRAY, bc.YEL, bc.WHITE
KB = GREEN    # 지식기반 블록 색(두 그림 공통)


def layer_label(g, x, y, w, h, t):
    g.rect(x, y, w, h, '#1f3a5f', '#1f3a5f', 1, None, 6)
    bc.vtext(g, x + w / 2 + 6, y + h / 2 + 4, t, 16)


def fig_arch():
    g = Svg(1000)
    LW = 70
    X = LW + 16
    def side(y, h, t):
        g.rect(0, y, LW, h, '#1f3a5f', '#1f3a5f', 1, None, 6)
        g.add('<text x="38" y="%d" font-size="20" fill="#fff" text-anchor="middle" transform="rotate(-90 38 %d)">%s</text>' % (y + h / 2 + 8, y + h / 2 + 8, t))
    # 응답 계층
    y0, h0 = 0, 110
    side(y0, h0, '응답 계층')
    tbox(g, X, y0, 580, '근거를 출처와 함께 받아 응답 생성', 16, WHITE, 12, h=h0, dash='8 5', title='근거 기반 응답 (sLLM)')
    tbox(g, X + 600, y0, 314, '모델·성능 향상 방안은 3, 4에서 제시', 15, GRAY, 12, h=h0)
    # 검색 계층
    y1, h1 = y0 + h0 + 70, 140
    side(y1, h1, '검색 계층')
    bw = 285
    xs = [X, X + bw + 30, X + 2 * (bw + 30)]
    for x, t, d in zip(xs, ['질의 해석', '근거 검색', '근거 구성'], ['질의에서 의도와 대상을 파악', '의도에 따라 KG와 저장소에서 근거를 검색', '출처가 붙은 근거를 프롬프트로 구성']):
        tbox(g, x, y1, bw, d, 15, BLUE, 12, h=h1, title=t)
    arrow_h(g, xs[0] + bw + 2, xs[1] - 2, y1 + h1 / 2); arrow_h(g, xs[1] + bw + 2, xs[2] - 2, y1 + h1 / 2)
    # 지식기반 계층
    y2, h2 = y1 + h1 + 70, 150
    side(y2, h2, '지식기반 계층')
    tbox(g, X, y2, 400, '온톨로지 기반 지식그래프(KG)로 개체 간 관계와 근거 출처를 구조화', 15, KB, 12, h=h2, title='지식기반')
    tbox(g, X + 440, y2, 474, '측정자료 저장소(수치 시계열)와 문서 저장소(규정 원문)', 15, KB, 12, h=h2, title='외부 저장소')
    g.line(X + 402, y2 + h2 / 2, X + 438, y2 + h2 / 2, INK, 'ar', None, 2)
    g.text(X + 420, y2 + h2 / 2 - 10, '키', 13, False, INK, 'middle', True)
    # 계층 간 화살표
    cx2, cx1 = xs[2] + bw / 2, xs[1] + bw / 2
    g.line(cx1, y2, cx1, y1 + h1 + 2, INK, 'ar', None, 3)
    g.line(cx2, y2, cx2, y1 + h1 + 2, INK, 'ar', None, 3)
    g.line(cx2, y1, cx2, y0 + h0 + 2, INK, 'ar', None, 3)
    g.text(cx2 - 12, (y1 + h1 + y2) / 2 + 6, '근거', 14, False, INK, 'end', True)
    g.text(cx2 - 12, (y0 + h0 + y1) / 2 + 6, '근거 묶음 + 질의', 14, False, INK, 'end', True)
    # 사용자 질의
    g.text(X, y0 + h0 + 42, '사용자 질의', 15, True, NAVY, 'start')
    g.line(X + 20, y0 + h0 + 52, X + 20, y1 - 2, INK, 'ar', None, 3)
    finish(g, y2 + h2 + 8, 'fig1_architecture')


def fig_pipeline():
    g = Svg(1000)
    bw, gap = 240, 40
    xs = [0, bw + gap, 2 * (bw + gap)]
    h = 230
    items = [('① 수집', '수문·기상 자료, 운영 근거(규정), 방류 승인 기록을 제공 방식에 맞춰 수집', BLUE),
             ('② 전처리', '온톨로지 기반 전처리: 정형 자료는 열을 속성으로, 행을 개체로 대응하고 문서 자료는 규칙으로 값을 추출하며 표기 형식을 통일', BLUE),
             ('③ 지식기반 구성', '개체와 관계를 생성하고(근거가 확인된 쌍만 연결) 온톨로지 제약으로 검증한 뒤 저장', KB)]
    for x, (t, d, c) in zip(xs, items):
        tbox(g, x, 0, bw, d, 15, c, 14, h=h, title=t)
    arrow_h(g, xs[0] + bw + 2, xs[1] - 2, h / 2); arrow_h(g, xs[1] + bw + 2, xs[2] - 2, h / 2)
    tbox(g, xs[0], h + 50, bw, '한수원 내부 자료 (현장방문 후 반영)', 15, GRAY, 12, dash='8 5')
    g.line(xs[0] + bw / 2, h + 48, xs[0] + bw / 2, h + 2, '#888', 'ar', '6 4', 2)
    x3 = xs[2] + bw + 40
    tbox(g, x3, 0, 1000 - x3, 'KG (개체·관계)', 15, KB, 10, h=95)
    tbox(g, x3, 135, 1000 - x3, '외부 저장소', 15, KB, 10, h=95)
    g.line(xs[2] + bw + 2, 47, x3 - 2, 47, INK, 'ar', None, 2); g.line(xs[2] + bw + 2, 183, x3 - 2, 183, INK, 'ar', None, 2)
    g.text(xs[2] + bw / 2 + 20, h + 78, '→ 검색·응답 계층으로 연결 (그림 1)', 15, True, NAVY, 'middle')
    finish(g, h + 110, 'fig2_pipeline')


def fig_approach():
    """그림 2: 파트 분해 → 선행연구 기술 분석 → 적용 기술 선택 → 통합 구조 (10월 → 11월)"""
    g = Svg(1000)
    bw, gap = 212, 38
    xs = [i * (bw + gap) for i in range(4)]
    items = [('① 파트 분해', 'RAG-LLM 프레임워크를 5개 파트로 구분', BLUE),
             ('② 기술 분석', '파트별 선행연구의 기술과 방법 분석', BLUE),
             ('③ 적용 선택', '파트별 적용 기술과 보완 사항 정리', BLUE),
             ('④ 통합 구조', '적용 기술을 하나의 구조로 통합', KB)]
    h = 150
    for x, (t, d, c) in zip(xs, items):
        tbox(g, x, 70, bw, d, 15, c, 12, h=h, title=t)
    for i in range(3):
        arrow_h(g, xs[i] + bw + 2, xs[i + 1] - 2, 70 + h / 2)
    g.rect(0, 0, 3 * bw + 2 * gap, 40, '#eef3f8', '#1f3a5f', 2, None, 6); g.text((3 * bw + 2 * gap) / 2, 28, '10월: 1.3 아키텍처 구성 계층, 2.3 데이터 파이프라인(안)을 각각 정리', 14, True, NAVY, 'middle')
    g.rect(xs[3], 0, bw, 40, '#eef3f8', '#1f3a5f', 2, None, 6); g.text(xs[3] + bw / 2, 28, '11월: 통합', 14, True, NAVY, 'middle')
    parts = ['온톨로지 설계', '자료 구조화·매핑', '수치자료 연계·저장', '질의 해석·검색', '근거 구성·응답']
    y = 70 + h + 40
    g.text(0, y, '5개 파트', 15, True, NAVY, 'start')
    bw2 = 188
    for i, t in enumerate(parts):
        tbox(g, i * (bw2 + 15), y + 14, bw2, t, 14, GRAY, 10, h=62)
    finish(g, y + 14 + 62 + 6, 'fig_approach')


def fig_seed():
    """온톨로지 시드 설계·보완 절차"""
    g = Svg(1000)
    bw, gap = 212, 38
    xs = [i * (bw + gap) for i in range(4)]
    items = [('① 질문 정의', '운영자가 확인해야 할 질문(CQ)과 범위 정의', BLUE),
             ('② 시드 온톨로지', '질문에 답하는 데 필요한 Class·관계·속성을 초기 온톨로지(시드)로 정의', BLUE),
             ('③ KG 구축', '시드에 맞춰 자료를 개체와 관계로 구축', KB),
             ('④ 검증', '질문 경로 점검과 구조 검사로 시드의 부족한 부분 확인', YEL)]
    h = 190
    for x, (t, d, c) in zip(xs, items):
        tbox(g, x, 0, bw, d, 15, c, 12, h=h, title=t)
    for i in range(3):
        arrow_h(g, xs[i] + bw + 2, xs[i + 1] - 2, h / 2)
    g.path('M%d,%d L%d,%d L%d,%d L%d,%d' % (xs[3] + bw / 2, h + 2, xs[3] + bw / 2, h + 50, xs[1] + bw / 2, h + 50, xs[1] + bw / 2, h + 4), '#b35c00', 'ar', '7 5', 2)
    g.text((xs[1] + xs[3] + bw) / 2, h + 80, '⑤ 시드 보완 (전문가 검토 후 반영, 반복)', 15, True, '#b35c00', 'middle')
    finish(g, h + 100, 'fig_seed')


def fig_process():
    """자료 유형별 처리 경로"""
    g = Svg(1000)
    col = [0, 330, 660]
    w = 300
    g.text(col[0] + w / 2, 30, '자료 유형', 16, True, NAVY, 'middle')
    g.text(col[1] + w / 2, 30, '처리', 16, True, NAVY, 'middle')
    g.text(col[2] + w / 2, 30, '결과', 16, True, NAVY, 'middle')
    rows = [('구조화 자료\n수치 시계열, 시설 정보,\n표 형태의 기준값', '열은 속성에, 행은 개체에 대응\n값은 원본 유지\n코드·시점 키로 연결', '개체·속성\n(수치 값은 외부 저장소)'),
            ('문서 자료\n승인 기록의 비고,\n규정 조문·별표', '문서 단위로 분리\n규칙(키워드, 정규식)으로 값 추출\n문자로 그린 표는 행·열로 변환', '개체·속성\n(원문은 문서 저장소)'),
            ('공통', '시각·수치·결측 표기 통일\n대상 선택, 중복 제거\n출처·시점 정보 유지', '출처가 확인되는 개체')]
    y = 56
    for r, c in zip(rows, [BLUE, BLUE, YEL]):
        hh = 150
        tbox(g, col[0], y, w, r[0].replace('\\n', '\n'), 15, GRAY, 12, h=hh)
        tbox(g, col[1], y, w, r[1].replace('\\n', '\n'), 15, c, 12, h=hh)
        tbox(g, col[2], y, 340, r[2].replace('\\n', '\n'), 15, KB, 12, h=hh)
        arrow_h(g, col[0] + w + 2, col[1] - 2, y + hh / 2); arrow_h(g, col[1] + w + 2, col[2] - 2, y + hh / 2)
        y += hh + 22
    finish(g, y, 'fig_process')


def fig_frame():
    """표준 프롬프트 프레임 구성(틀)"""
    g = Svg(1000)
    tbox(g, 0, 0, 300, '사용자 질의', 15, GRAY, 12, h=60)
    g.text(0, 120, '근거 묶음 (의도별 구역, 항목마다 출처 번호)', 15, True, NAVY, 'start')
    zones = ['현재 상태', '과거 상태', '운영행위·승인', '운영기준', '출처 및 위치']
    zw = 185
    for i, z in enumerate(zones):
        tbox(g, i * (zw + 18), 138, zw, z, 15, KB, 10, h=56)
    tbox(g, 0, 232, 1000, '근거 사용 원칙: 주어진 근거만 사실로 사용하고 사실마다 출처 번호를 붙인다 / 근거를 해석·비교한 내용은 판단임을 밝히고 근거를 함께 적는다 / 근거에 없는 내용은 “자료에 없음”으로 답한다', 14, YEL, 12)
    g.line(150, 62, 150, 100, INK, 'ar', None, 3)
    g.line(500, 205, 500, 228, INK, 'ar', None, 3)
    tbox(g, 0, 345, 480, 'sLLM 응답 (모델은 3, 4에서 제시)', 15, GRAY, 12, dash='8 5')
    tbox(g, 520, 345, 480, '근거와 판단을 구분한 답변', 15, BLUE, 12)
    g.line(482, 372, 518, 372, INK, 'ar', None, 3)
    g.line(500, 300, 240, 342, INK, 'ar', None, 3)
    finish(g, 345 + 60, 'fig_frame')


if __name__ == '__main__':
    fig_arch(); fig_pipeline(); fig_approach(); fig_seed(); fig_process(); fig_frame()
