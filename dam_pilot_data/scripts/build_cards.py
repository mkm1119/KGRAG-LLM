#!/usr/bin/env python3
"""랩미팅 자료의 단계별 원리 카드 그림. 한 카드 = 단계 이름·근거 문헌 / 문헌에서 가져온 원리 / 입력 → 처리 → 결과 / 대표 예시.
사용: NODE_PATH=/opt/node22/lib/node_modules python3 scripts/build_cards.py"""
import importlib.util, os
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('pf', os.path.join(HERE, 'build_poster_figures.py')); pf = importlib.util.module_from_spec(spec); spec.loader.exec_module(pf)
OUT = os.path.join(HERE, '..', '..', 'lab_meeting', 'card_figs'); os.makedirs(OUT, exist_ok=True)
pf.tf.OUT = OUT; pf.tf.W = 1000
Svg, INK, NAVY = pf.Svg, pf.INK, pf.NAVY
MEAS = 508246


def lines(g, x, y, texts, size=19, lh=26, bold=False, fill='#222', anchor='start'):
    for i, t in enumerate(texts):
        g.text(x, y + i * lh, t, size, bold, fill, anchor)


def pad(g):
    # 가장자리 선이 잘리지 않도록 전체를 약간 줄여 안쪽으로 둔다
    g.p.insert(0, '<g transform="translate(5,5) scale(0.99)">'); g.p.append('</g>'); g.h = int(g.h * 0.99) + 10


def header(g, title, source):
    g.rect(0, 0, 1000, 76, NAVY, NAVY, 1, None, 8)
    g.text(24, 50, title, 32, True, '#fff', 'start')
    g.text(976, 48, source, 22, False, '#dbe6f5', 'end')


def principle(g, y, texts):
    h = 28 + 27 * len(texts) + 12
    g.rect(0, y, 1000, h, '#fff8dc', '#d9b44a', 2, None, 8)
    g.text(18, y + 28, '문헌에서 가져온 원리', 20, True, '#7a5800', 'start')
    lines(g, 18, y + 28 + 30, texts, 19, 27)
    return y + h


def flow_rows(g, y, head, rows):
    """rows: (자료 줄들, 처리 줄들, 결과 줄들, 높이)"""
    g.text(20, y + 22, head[0], 19, True, '#555', 'start'); g.text(235, y + 22, head[1], 19, True, '#555', 'start'); g.text(705, y + 22, head[2], 19, True, '#555', 'start')
    y += 34
    for a, b, c, h in rows:
        g.rect(0, y, 215, h, '#f1f1f1', '#888', 2, None, 6)
        lines(g, 14, y + 30, a, 19, 26, True)
        g.rect(235, y, 450, h, '#e8f1fb', '#4a78b5', 2, None, 6)
        lines(g, 248, y + 30, b, 19, 26)
        g.rect(705, y, 295, h, '#e8f6ea', '#4c9a5a', 2, None, 6)
        lines(g, 719, y + 30, c, 19, 26)
        g.line(217, y + h // 2, 233, y + h // 2, INK, 'ar', None, 2); g.line(687, y + h // 2, 703, y + h // 2, INK, 'ar', None, 2)
        y += h + 10
    return y


def card_2_3():
    g = Svg(1000)
    y = 0
    y = flow_rows(g, y, ('자료', '전처리', '결과'), [
        (['① 방류 승인 기록'], ['값이 모두 같은 중복 행은 첫 행만 남김', '(제거한 행은 로그에 기록)', '→ 4개 댐만 선택'], ['한강수계 3,929행', '→ 중복 7행 제거 3,922행', '→ 4개 댐 80건'], 104),
        (['② 수문기상', '시간 자료'], ['응답(JSON)을 열 구조가 같은 표로', '옮김(변환·보간 없음) → 4개 댐 선택', '→ 24시는 다음날 0시로 읽음,', '   빈 값은 채우지 않음'], ['4개 댐 × 6개 변수', '{0:,}행'.format(MEAS)], 130),
        (['③ 연계운영규정', '   별표3'], ['규정 XML에서 별표 번호로', '별표3 부분만 골라냄'], ['별표3의 텍스트'], 78),
        (['④ 댐 기본 정보'], ['4개 댐의 행만 선택'], ['4개 댐'], 52)])
    # 대표 예시 두 개
    y += 4
    g.rect(0, y, 488, 150, '#fff', '#888', 2, '8 5', 6)
    g.text(14, y + 28, '예시 ① 중복 행', 20, True, NAVY, 'start')
    cols = [14, 140, 208, 392]
    for x, t in zip(cols, ['순차번호', '관측소', '방류시작시간', '접수방류량']):
        g.text(x, y + 58, t, 16, True, '#555', 'start')
    for k, (a, col) in enumerate([('2218', INK), ('2220 (제거)', '#b3261e')]):
        yy = y + 86 + k * 28
        for x, t in zip(cols, [a, '광동', '2016-07-04 18:00', '200']):
            g.text(x, yy, t, 17, False, col, 'start')
    g.text(14, y + 140, '순차번호만 다르고 값이 모두 같아 2220을 제거한다', 17, False, '#444', 'start')
    g.rect(512, y, 488, 150, '#fff', '#888', 2, '8 5', 6)
    g.text(526, y + 28, '예시 ② 시각 라벨 (24시 표기)', 20, True, NAVY, 'start')
    g.text(526, y + 62, '2012082416  →  2012-08-24 16:00', 19, False, INK, 'start')
    g.text(526, y + 92, '2016062924  →  2016-06-30 00:00', 19, False, '#b3261e', 'start')
    lines(g, 526, y + 122, ['라벨 = 날짜 8자리 + 시각 2자리(01~24)', '24시는 그날의 끝이므로 다음날 0시로 읽는다'], 16, 21, False, '#444')
    y += 164
    # 확인 필요
    g.rect(0, y, 1000, 112, '#fff3e6', '#e08a1e', 2, '8 5', 6)
    g.text(14, y + 28, '확인 필요', 19, True, '#b35c00', 'start')
    lines(g, 14, y + 54, ['시각 라벨 01~24가 “그 시각 직전 한 시간의 값”인지 “그 시각 정각의 값”인지 K-water 자료 설명에서',
                          '확인하지 못했다. 지금은 라벨 시각을 그대로 읽는다(±1시간 차이 가능). 확인되면 읽는 규칙만 바꾸면 된다.'], 17, 25)
    y += 126
    g.text(0, y + 18, '원본 파일은 바꾸지 않고, 정리한 내용은 로그에 남긴다.', 17, False, '#444', 'start')
    g.h = y + 36
    pad(g)
    g.save('card_2_3')


if __name__ == '__main__':
    card_2_3()
