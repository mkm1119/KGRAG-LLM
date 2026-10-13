#!/usr/bin/env python3
"""학회 포스터용 그림 2개. 캔버스 폭 1000px로 그려 포스터에서 글씨가 22pt 안팎이 되도록 한다.
사용: NODE_PATH=/opt/node22/lib/node_modules python3 scripts/build_poster_figures.py
"""
import importlib.util, os

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('tf', os.path.join(HERE, 'build_team_figures.py'))
tf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tf)
tf.OUT = os.path.join(HERE, '..', '..', 'lab_meeting', 'poster_assets')
tf.W = 1000
os.makedirs(tf.OUT, exist_ok=True)
tf.COL['yel'] = ('#fff9c4', '#f9a825', '#7a5800')
tf.COL['hms'] = ('#b2dfdb', '#00796b', '#004d40')
tf.COL['apr'] = ('#ffe0b2', '#ef6c00', '#bf360c')
tf.COL['opr'] = ('#ffccbc', '#d84315', '#bf360c')
tf.COL['dam'] = ('#bbdefb', '#1565c0', '#0d47a1')
tf.COL['cri'] = ('#e1bee7', '#8e24aa', '#6a1b9a')
Svg = tf.Svg


def poster_framework():
    g = Svg(1000)
    g.node(10, 10, 980, 112, 'onto', 'STEP 1  Ontology 설계', ['개체 6종류 · 관계 9종류'], 34, 28)
    g.line(500, 124, 500, 176, '#7e57c2', 'arp')
    g.text(530, 160, '설계에 맞춰 구축', 26, False, '#5e35b1', 'start')
    g.node(10, 178, 980, 112, 'auto', 'STEP 2  지식그래프(KG) 구축', ['원자료 3종을 정리해 세 저장소에 담는다'], 34, 28)
    xs = [10, 355, 700]
    names = [('문서 저장소', '규정 원문'), ('지식그래프 (KG)', '관계 · 근거 번호'), ('측정자료 저장소', '시간별 측정값')]
    for x, (t, d) in zip(xs, names):
        g.line(x + 145, 292, x + 145, 336, '#44546a', 'ar')
        g.node(x, 338, 290, 124, 'store', t, [d], 28, 26)
    g.rect(0, 496, 1000, 500, '#fffaf0', '#d9b36a', 3, None, 18)
    g.text(190, 545, 'STEP 3  질문 응답', 30, True, '#7a4a00', 'start')
    g.rect(14, 574, 972, 210, '#f1f8f2', '#2e7d32', 3, '10 8', 14)
    for x, (t, d) in zip(xs, [('문서 검색', '번호로 원문 읽기'), ('KG 검색', '연결 따라 찾기'), ('측정자료 검색', '번호로 값 읽기')]):
        g.line(x + 145, 464, x + 145, 594, '#2e7d32', 'arg')
        g.node(x, 596, 290, 124, 'store', t, [d], 28, 26)
    g.text(500, 762, '하이브리드 검색', 28, True, '#1b5e20')
    g.node(10, 826, 290, 160, 'gray', '사용자 질문', ['“소양강댐 지금과 비슷한', '과거 사례는?”'], 30, 24)
    g.node(355, 826, 290, 160, 'llm', '질문 해석 (LLM)', ['댐 · 시점 · 유형을', '정리한다'], 30, 26)
    g.node(700, 826, 290, 160, 'llm', 'LLM 답변', ['모은 근거 안에서만', '설명, 출처 표시'], 30, 26)
    g.line(302, 906, 353, 906, '#44546a', 'ar')
    g.line(500, 824, 500, 788, '#44546a', 'ar')
    g.text(516, 812, '찾을 내용', 24, False, '#44546a', 'start', True)
    g.line(845, 788, 845, 824, '#44546a', 'ar')
    g.text(830, 812, '근거', 24, False, '#44546a', 'end', True)
    g.save('poster_fig1_framework')


def poster_kg():
    g = Svg(780)
    w, h = 265, 165
    cx = [2, 367, 732]
    cy = [15, 305, 595]
    def nd(c, r, kind, label, title, detail):
        g.node(cx[c], cy[r], w, h, kind, title, [detail], 30, 24, None, label)
    nd(0, 0, 'apr', '방류 승인', '승인 1368', '2012-08-24')
    nd(1, 0, 'cri', '운영기준', '제한수위', '138.0 EL.m')
    nd(2, 0, 'yel', '근거자료', '규정 별표3', 'LAW:별표3')
    nd(0, 1, 'opr', '운영행위', '탄력적 방류', '16:00 시작')
    nd(1, 1, 'dam', '댐', '충주댐', '다목적댐')
    nd(2, 1, 'hms', '수문기상 상태', '충주댐_수위', '측정소 1003110')
    nd(0, 2, 'yel', '근거자료', '승인 기록', '1368번')
    nd(2, 2, 'yel', '근거자료', 'K-water 자료', '댐코드 1003110')
    g.line(135, 182, 135, 303, '#37474f', 'ar'); g.text(152, 250, '허가한다', 24, False, '#37474f', 'start', True)
    g.line(262, 160, 420, 303, '#37474f', 'ar'); g.text(300, 212, '대상 댐', 24, False, '#37474f', 'start', True)
    g.line(500, 182, 500, 303, '#37474f', 'ar'); g.text(516, 250, '적용되는 댐', 24, False, '#37474f', 'start', True)
    g.line(634, 97, 730, 97, '#78909c', 'arh'); g.text(682, 81, '근거', 24, False, '#546e7a', 'middle', True)
    g.line(269, 387, 365, 387, '#37474f', 'ar'); g.text(317, 371, '수행 댐', 24, False, '#37474f', 'middle', True)
    g.line(634, 387, 730, 387, '#37474f', 'ar'); g.text(682, 371, '보유', 24, False, '#37474f', 'middle', True)
    g.line(135, 472, 135, 593, '#78909c', 'arh'); g.text(152, 540, '근거', 24, False, '#546e7a', 'start', True)
    g.line(865, 472, 865, 593, '#78909c', 'arh'); g.text(882, 540, '근거', 24, False, '#546e7a', 'start', True)
    g.save('poster_fig2_kg')


if __name__ == '__main__':
    poster_framework()
    poster_kg()
