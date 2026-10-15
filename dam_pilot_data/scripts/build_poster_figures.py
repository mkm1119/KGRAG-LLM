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


INK = '#222'
NAVY = '#1f3a5f'


def box(g, x, y, w, h, title, lines=(), ts=28, bs=24, fill='#fff', dash=None, rx=6, sw=2.5, bold=True):
    g.rect(x, y, w, h, fill, INK, sw, dash, rx)
    n = 1 + len(lines)
    gap = bs + 8
    top = y + h / 2 - (ts + (n - 1) * gap) / 2 + ts * 0.8
    g.text(x + w / 2, top, title, ts, bold, INK)
    for i, ln in enumerate(lines):
        g.text(x + w / 2, top + ts * 0.2 + (i + 1) * gap, ln, bs, False, '#444')


def cyl(g, x, y, w, h, title, sub=None, ts=26, bs=22):
    e = 16
    g.add('<path d="M%d,%d a%d,%d 0 0 1 %d,0 v%d a%d,%d 0 0 1 -%d,0 z" fill="#f2f2f2" stroke="%s" stroke-width="2.5"/>' % (x, y + e, w / 2, e, w, h - 2 * e, w / 2, e, w, INK))
    g.add('<path d="M%d,%d a%d,%d 0 0 0 %d,0" fill="none" stroke="%s" stroke-width="2.5"/>' % (x, y + e, w / 2, e, w, INK))
    g.text(x + w / 2, y + h / 2 + 18, title, ts, True, INK)


def panel(g, x, y, w, h, tag):
    g.rect(x, y, w, h, '#fff', '#888', 2, '9 6', 4)
    g.text(x + 12, y + 32, tag, 26, True, NAVY, 'start')


def poster_framework():
    g = Svg(704)
    # (a) Ontology 설계
    panel(g, 0, 0, 265, 330, '(a) Ontology 설계')
    box(g, 20, 52, 225, 125, 'CQ 설정', ['전체 질문 1개', '세부 질문 6개'])
    g.line(132, 179, 132, 213, INK, 'ar')
    box(g, 20, 213, 225, 112, 'Class · 관계', ['개체 6종류', '관계 9종류'])
    # (b) KG 구축
    panel(g, 285, 0, 715, 330, '(b) 지식그래프(KG) 구축')
    box(g, 300, 60, 160, 250, '원자료', ['방류 승인', '시간 자료', '규정 별표3'])
    g.line(462, 185, 498, 185, INK, 'ar')
    box(g, 500, 60, 170, 250, 'KG 구축', ['전처리', '매핑 · 추출', '관계 연결', '검증 · 저장'], 26, 22)
    g.line(672, 185, 708, 185, INK, 'ar')
    cyl(g, 710, 52, 275, 84, 'KG (Neo4j)', None)
    cyl(g, 710, 144, 275, 84, '측정자료 저장소', None)
    cyl(g, 710, 236, 275, 84, '문서 저장소', None)
    # (c) 질문 응답
    panel(g, 0, 380, 1000, 320, '(c) 질문 응답 (RAG)')
    xs = [14, 214, 414, 614, 814]
    ws = 172
    box(g, xs[0], 450, ws, 200, '사용자', ['질문'], 28, 28)
    box(g, xs[1], 450, ws, 200, '질문 해석', ['(LLM)', '의도·댐·시점'], 28, 22)
    box(g, xs[2], 450, ws, 200, '근거 검색', ['KG: Cypher', '측정자료 조회', '문서 조회'], 28, 22)
    box(g, xs[3], 450, ws, 200, '근거 묶음', ['출처 번호가', '붙은 원값 근거'], 28, 22)
    box(g, xs[4], 450, ws, 200, '답변 (LLM)', ['근거 / 판단을', '나누어 작성'], 28, 22)
    for i in range(4):
        g.line(xs[i] + ws + 2, 550, xs[i + 1] - 2, 550, INK, 'ar')
    # 저장소 → 근거 검색 (점선)
    g.path('M848,324 L848,360 L500,360 L500,448', '#555', 'ar', '8 6', 3)
    g.text(520, 350, '저장소에서 읽어 옴', 24, False, '#444', 'start')
    g.save('poster_fig1_framework')


def poster_kg():
    """Class 6개, Relation 9개를 모두 적용한 충주댐 승인 1368 예시(왼쪽 여백에 Approval의 supportedBy 경로)."""
    tf.W = 1040
    g = Svg(690)
    w, h = 270, 130
    cx = [40, 395, 750]
    cy = [10, 270, 530]
    def ell(c, r, cls, name):
        x, y = cx[c], cy[r]
        g.add('<ellipse cx="%d" cy="%d" rx="%d" ry="%d" fill="#fff" stroke="%s" stroke-width="2.5"/>' % (x + w / 2, y + h / 2, w / 2, h / 2, NAVY))
        g.text(x + w / 2, y + h / 2 - 8, cls, 24, False, NAVY)
        g.text(x + w / 2, y + h / 2 + 30, name, 28, True, INK)
    def rec(c, r, cls, name):
        x, y = cx[c], cy[r]
        g.rect(x, y + 10, w, h - 20, '#f2f2f2', INK, 2.5, None, 4)
        g.text(x + w / 2, y + h / 2 - 8, cls, 24, False, '#444')
        g.text(x + w / 2, y + h / 2 + 30, name, 28, True, INK)
    ell(0, 0, 'Approval', '승인 1368')
    ell(1, 0, 'Criterion', '제한수위 138.0')
    rec(2, 0, 'EvidenceSource', '규정 별표3')
    ell(0, 1, 'Operation', '탄력적 방류')
    ell(1, 1, 'Dam', '충주댐')
    ell(2, 1, 'HMS', '충주댐_수위')
    rec(0, 2, 'EvidenceSource', '승인 기록')
    rec(2, 2, 'EvidenceSource', 'K-water 자료')
    L = lambda *a: g.line(*a, INK, 'ar', None, 3)
    L(175, 142, 175, 268); g.text(190, 214, 'authorizes', 22, False, INK, 'start', True)
    L(275, 125, 460, 272); g.text(350, 190, 'concernsDam', 22, False, INK, 'start', True)
    L(540, 142, 540, 268); g.text(555, 214, 'appliesToDam', 22, False, INK, 'start', True)
    L(675, 75, 748, 75); g.text(712, 59, 'supportedBy', 18, False, INK, 'middle', True)
    L(312, 335, 393, 335); g.text(352, 319, 'performedOnDam', 15, False, INK, 'middle', True)
    L(675, 335, 748, 335); g.text(712, 319, 'hasHMS', 20, False, INK, 'middle', True)
    L(175, 402, 175, 528); g.text(190, 474, 'supportedBy', 22, False, INK, 'start', True)
    L(885, 402, 885, 528); g.text(900, 474, 'supportedBy', 22, False, INK, 'start', True)
    g.path('M40,75 L12,75 L12,595 L38,595', INK, 'ar', None, 3)
    g.add('<text transform="translate(30,330) rotate(-90)" font-size="22" fill="#222" text-anchor="middle" stroke="#fff" stroke-width="6" paint-order="stroke">supportedBy</text>')
    g.save('poster_fig2_kg')
    tf.W = 1000


if __name__ == '__main__':
    poster_framework()
    poster_kg()
