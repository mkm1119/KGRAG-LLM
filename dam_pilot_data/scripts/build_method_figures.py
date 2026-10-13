#!/usr/bin/env python3
"""랩미팅 보강 '단계별 방법론과 원리' 카드에 넣는 그림. build_team_figures.py의 Svg 부품을 쓴다(글씨 24px 이상, 폭 1500px).
사용: python3 scripts/build_method_figures.py [단계 이름 ...]   (이름이 없으면 전부)  — NODE_PATH와 Playwright 필요
"""
import importlib.util, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('tf', os.path.join(HERE, 'build_team_figures.py'))
tf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tf)
tf.OUT = os.path.join(HERE, '..', '..', 'lab_meeting', 'method_figs')
os.makedirs(tf.OUT, exist_ok=True)
tf.COL['teal'] = ('#e0f2f1', '#00796b', '#004d40')
Svg = tf.Svg


def step1_source():
    """KG 구축 단계 1. 소스 구분: 자료 세 가지가 표 경로와 글 경로로 나뉘는 과정"""
    g = Svg(1000)
    g.text(40, 52, '자료를 두 경로로 나눈다: 열과 행의 의미가 자료에 정해져 있는가?', 32, True, '#1f4e79', 'start')
    w, gap, y0, h = 450, 35, 90, 215
    xs = [40, 40 + w + gap, 40 + 2 * (w + gap)]
    # 원자료 세 가지
    g.node(xs[0], y0, w, h, 'src', '① 방류 승인 기록', ['표 파일 · 한 행 = 승인 1건', '1368 | 1003110 | 2012-08-24 |', '… | 이내 탄력적 조정'], 28, 24)
    g.node(xs[1], y0, w, h, 'src', '② 수문기상 시간 자료', ['표 파일 · 한 행 = 한 시각', '1012110 | 2017082515 |', '192.53 | 1027.58 | …'], 28, 24)
    g.node(xs[2], y0, w, h, 'src', '③ 규정 별표3', ['글 · 선 문자로 그린 표', '│충 주 댐  │138.0 │ -', '│소양강댐  │190.3 │ -'], 28, 24)
    # 판단
    dy = y0 + h + 85
    g.node(40, dy, 1420, 110, 'onto', '판단: 열과 행의 의미가 자료에 정해져 있는가?',
           ['표 파일은 첫 줄에 열 이름이 있다.  별표3는 선으로 그렸을 뿐 열 이름이 없는 글이다.'], 30, 25)
    for i, x in enumerate(xs):
        g.line(x + w // 2, y0 + h + 2, x + w // 2, dy - 2, '#7e57c2', 'arp')
    # 두 경로
    ry = dy + 110 + 95
    g.node(40, ry, 690, 285, 'auto', '표 경로  (예: ①, ②)',
           ['열 이름을 보고 값을 속성에 그대로 옮긴다.', '해석을 더하지 않아 같은 표는 항상 같은 결과다.', '예) 승인일 열 “2012-08-24” → 승인일 속성', '→ 단계 3. 구조화 자료 매핑'], 30, 24)
    g.node(770, ry, 690, 285, 'teal', '글 경로  (예: ③)',
           ['글 속의 낱말과 패턴을 찾아 값을 뽑는다.', '해석이 필요하여 오류가 생길 수 있다.', '예) “충 주 댐 │138.0” → 충주댐 제한수위 138.0', '승인 기록의 비고 문장(“이내 탄력적 조정”)도 여기서', '→ 단계 4. 비정형 텍스트 추출'], 30, 24)
    g.line(385, dy + 112, 385, ry - 2)
    g.text(410, dy + 168, '예  (① ②)', 28, True, '#0d47a1', 'start')
    g.line(1115, dy + 112, 1115, ry - 2)
    g.text(1140, dy + 168, '아니오  (③, ①의 비고 문장)', 28, True, '#004d40', 'start')
    g.text(40, ry + 285 + 52, '해석이 들어가는 부분이 글 경로 한 곳에 모이므로, 어디를 검토해야 하는지가 분명해진다.', 26, False, '#44546a', 'start')
    g.h = ry + 285 + 85
    g.save('step1_source')


FIGS = {'step1_source': step1_source}

if __name__ == '__main__':
    names = sys.argv[1:] or list(FIGS)
    for n in names:
        FIGS[n]()
