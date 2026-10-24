#!/usr/bin/env python3
"""월간 공정보고용 그림(논문식: 흰 바탕, 검정 선, 회색 채움, 큰 글자). 본문 폭에 넣었을 때 글자가 약 10pt가 되도록 26px(제목 28px)로 그린다.
사용: NODE_PATH=/opt/node22/lib/node_modules python3 scripts/build_report_figs.py"""
import importlib.util, os
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('pf', os.path.join(HERE, 'build_poster_figures.py')); pf = importlib.util.module_from_spec(spec); spec.loader.exec_module(pf)
OUT = os.path.join(HERE, '..', '..', 'lab_meeting', 'report_figs'); os.makedirs(OUT, exist_ok=True)
pf.tf.OUT = OUT; pf.tf.W = 1000
Svg = pf.Svg
INK = '#222'
T, B = 28, 26   # 제목, 본문 글자 크기(px)


def box(g, x, y, w, h, lines, fill='#fff', thick=False, dash=None, size=B, bold_first=True):
    g.rect(x, y, w, h, fill, INK, 4 if thick else 2, dash, 6)
    n = len(lines)
    lh = size * 1.32
    y0 = y + h / 2 - (n - 1) * lh / 2 + size * 0.33
    for i, t in enumerate(lines):
        g.text(x + w / 2, y0 + i * lh, t, size, bold_first and i == 0 and n > 1, INK, 'middle')


def cyl(g, x, y, w, h, t, size=B):
    ry = 14
    g.add('<path d="M%d,%d a%d,%d 0 0,1 %d,0 v%d a%d,%d 0 0,1 -%d,0 z" fill="#f0f0f0" stroke="%s" stroke-width="2"/>' % (x, y + ry, w / 2, ry, w, h - 2 * ry, w / 2, ry, w, INK))
    g.add('<path d="M%d,%d a%d,%d 0 0,0 %d,0" fill="none" stroke="%s" stroke-width="2"/>' % (x, y + ry, w / 2, ry, w, INK))
    lines = t.split('\n')
    lh = size * 1.3
    y0 = y + h / 2 + ry / 2 - (len(lines) - 1) * lh / 2 + size * 0.33
    for i, s in enumerate(lines):
        g.text(x + w / 2, y0 + i * lh, s, size, False, INK, 'middle')


def arr(g, x1, y1, x2, y2, dash=None, sw=3):
    g.line(x1, y1, x2, y2, INK, 'ar', dash, sw)


def panel(g, x, y, w, h, title):
    g.rect(x, y, w, h, '#fff', '#777', 2, '9 6', 4)
    g.text(x + 14, y + 34, title, T, True, '#1f3a5f', 'start')


def fig_approach():
    g = Svg(1000)
    bw, gap = 290, 65
    xs = [i * (bw + gap) for i in range(3)]
    for x, l in zip(xs, [['① 파트 분해', '5개 파트로 구분'], ['② 기술 분석', '선행연구의 기술·방법'], ['③ 적용 방향', '파트별 적용 기술']]):
        box(g, x, 0, bw, 130, l, fill='#f2f2f2')
    for i in range(2):
        arr(g, xs[i] + bw + 3, 65, xs[i + 1] - 3, 65)
    parts = ['온톨로지\n설계', '자료 구조화\n·매핑', '수치자료\n연계·저장', '질의 해석\n·검색', '근거 구성\n·응답']
    w = 184
    for i, t in enumerate(parts):
        box(g, i * (w + 20), 190, w, 118, t.split('\n'), bold_first=False)
    g.text(0, 175, '5개 파트', T, True, '#1f3a5f', 'start')
    g.h = 320
    g.save('fig_approach')


def fig_arch():
    g = Svg(1000)
    # 응답 계층
    panel(g, 0, 0, 1000, 150, '응답 계층')
    box(g, 250, 52, 500, 80, ['근거 기반 응답 (sLLM)'], thick=True)
    # 검색 계층
    panel(g, 0, 210, 1000, 190, '검색 계층')
    bw = 270
    xs = [30, 365, 700]
    for x, t in zip(xs, ['질의 해석', '근거 검색', '근거 구성']):
        box(g, x, 262, bw, 100, [t], fill='#f2f2f2')
    arr(g, xs[0] + bw + 3, 312, xs[1] - 3, 312); arr(g, xs[1] + bw + 3, 312, xs[2] - 3, 312)
    # 지식기반 계층
    panel(g, 0, 460, 1000, 210, '지식기반 계층')
    cyl(g, 30, 518, 270, 120, 'KG\n(개체·관계)')
    cyl(g, 365, 518, 270, 120, '측정자료\n저장소')
    cyl(g, 700, 518, 270, 120, '문서\n저장소')
    # 연결 화살표
    arr(g, 835, 400, 835, 218 + 190 - 2) if False else None
    arr(g, 500, 456, 500, 404)      # 지식기반 -> 근거 검색
    arr(g, 835, 456, 835, 404)      # 지식기반 -> 근거 구성
    arr(g, 835, 208, 835, 154)      # 근거 구성 -> 응답
    g.text(520, 438, '근거', 24, False, INK, 'start', True)
    g.text(855, 438, '근거', 24, False, INK, 'start', True)
    g.text(855, 190, '근거 묶음', 24, False, INK, 'start', True)
    # 사용자 질의
    g.text(30, 196, '사용자 질의', 24, True, '#1f3a5f', 'start', True) if False else None
    box(g, 30, 156, 200, 46, ['사용자 질의'], bold_first=False, size=24, fill='#fff') if False else None
    g.h = 690
    g.save('fig1_architecture')


def fig_pipeline():
    g = Svg(1000)
    bw, gap = 250, 50
    xs = [0, bw + gap, 2 * (bw + gap)]
    heads = [('① 수집', ['수문·기상 자료', '운영 규정', '방류 승인 기록']),
             ('② 전처리', ['정형 자료 대응', '문서 자료 추출', '표기 형식 통일']),
             ('③ 지식기반 구성', ['개체·관계 생성', '검증', '저장'])]
    for x, (t, ls) in zip(xs, heads):
        g.rect(x, 0, bw, 250, '#f2f2f2', INK, 2, None, 6)
        g.text(x + bw / 2, 48, t, T, True, INK, 'middle')
        for i, l in enumerate(ls):
            g.text(x + bw / 2, 112 + i * 44, l, B, False, INK, 'middle')
    for i in range(2):
        arr(g, xs[i] + bw + 3, 125, xs[i + 1] - 3, 125)
    x3 = xs[2] + bw + 55
    cyl(g, x3, 20, 1000 - x3, 100, 'KG')
    cyl(g, x3, 135, 1000 - x3, 100, '외부\n저장소', size=24)
    arr(g, xs[2] + bw + 3, 70, x3 - 3, 70); arr(g, xs[2] + bw + 3, 185, x3 - 3, 185)
    box(g, 0, 330, bw + 60, 90, ['한수원 내부 자료'], dash='9 6', bold_first=False, size=24)
    arr(g, bw / 2, 328, bw / 2, 254, dash='7 5')
    g.h = 440
    g.save('fig2_pipeline')


def fig_process():
    g = Svg(1000)
    cols = [0, 350, 700]
    w = 300
    for x, t in zip(cols, ['자료 유형', '처리', '결과']):
        g.text(x + w / 2, 34, t, T, True, '#1f3a5f', 'middle')
    rows = [(['구조화 자료', '(수치 시계열, 시설 정보)'], ['열 → 속성, 행 → 개체', '값은 원본 유지'], ['개체·속성', '값은 외부 저장소']),
            (['문서 자료', '(승인 비고, 규정 별표)'], ['규칙으로 값 추출', '표를 행·열로 변환'], ['개체·속성', '원문은 문서 저장소']),
            (['공통'], ['표기 형식 통일', '출처·시점 유지'], ['출처가 확인되는 개체'])]
    y = 60
    for a, b, c in rows:
        h = 130
        box(g, cols[0], y, w, h, a, bold_first=True, fill='#f2f2f2')
        box(g, cols[1], y, w, h, b, bold_first=False)
        box(g, cols[2], y, w, h, c, bold_first=False)
        arr(g, cols[0] + w + 3, y + h / 2, cols[1] - 3, y + h / 2); arr(g, cols[1] + w + 3, y + h / 2, cols[2] - 3, y + h / 2)
        y += h + 24
    g.h = 530
    g.save('fig_process')


def fig_seed():
    g = Svg(1000)
    bw, gap = 220, 40
    xs = [i * (bw + gap) for i in range(4)]
    items = [['① 질문 정의'], ['② 온톨로지', '정의'], ['③ KG 구축'], ['④ 검증']]
    for x, l in zip(xs, items):
        box(g, x, 0, bw, 120, l, fill='#f2f2f2', bold_first=False)
    for i in range(3):
        arr(g, xs[i] + bw + 3, 60, xs[i + 1] - 3, 60)
    g.path('M%d,%d L%d,%d L%d,%d L%d,%d' % (xs[3] + bw / 2, 124, xs[3] + bw / 2, 190, xs[1] + bw / 2, 190, xs[1] + bw / 2, 126), INK, 'ar', '8 6', 3)
    g.text((xs[1] + xs[3] + bw) / 2, 232, '⑤ 온톨로지 보완 (전문가 검토 후 반영)', B, False, INK, 'middle')
    g.h = 260
    g.save('fig_seed')


def fig_frame():
    g = Svg(1000)
    box(g, 0, 0, 330, 80, ['사용자 질의'], bold_first=False)
    arr(g, 165, 83, 165, 130)
    panel(g, 0, 134, 1000, 200, '근거 묶음 (구역·출처 번호)')
    zones = ['현재 상태', '과거 상태', '운영행위\n·승인', '운영기준', '출처·위치']
    zw = 176
    for i, z in enumerate(zones):
        box(g, 20 + i * (zw + 20), 190, zw, 118, z.split('\n'), bold_first=False, fill='#f2f2f2')
    arr(g, 500, 338, 500, 384)
    box(g, 0, 388, 1000, 80, ['근거 사용 원칙'], bold_first=False, fill='#f2f2f2')
    arr(g, 500, 472, 500, 518)
    box(g, 0, 522, 420, 90, ['sLLM 응답'], thick=True, bold_first=False)
    arr(g, 423, 567, 577, 567)
    box(g, 580, 522, 420, 90, ['근거·판단 구분 답변'], bold_first=False)
    g.h = 640
    g.save('fig_frame')


if __name__ == '__main__':
    fig_approach(); fig_arch(); fig_pipeline(); fig_process(); fig_seed(); fig_frame()
