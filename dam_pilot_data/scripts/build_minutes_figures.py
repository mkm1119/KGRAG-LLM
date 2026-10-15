#!/usr/bin/env python3
"""회의록용 그림. 김장호 교수 제시 자료(docx)의 도구 호출 흐름도를 글자 그대로 다시 그린다(원본은 어두운 화면 캡처에 버튼이 겹쳐 있음).
구성도(image7)는 원본을 그대로 복사한다. 사용: NODE_PATH=/opt/node22/lib/node_modules python3 build_minutes_figures.py <docx 풀린 폴더>"""
import importlib.util, os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('pf', os.path.join(HERE, 'build_poster_figures.py')); pf = importlib.util.module_from_spec(spec); spec.loader.exec_module(pf)
OUT = os.path.join(HERE, '..', '..', 'lab_meeting', 'minutes_figs'); os.makedirs(OUT, exist_ok=True)
pf.tf.OUT = OUT; pf.tf.W = 1000
Svg, INK = pf.Svg, pf.INK
shutil.copy(os.path.join(sys.argv[1], 'word', 'media', 'image7.png'), os.path.join(OUT, 'fig1_sllm.png'))

g = Svg(720)
X = {'op': 110, 'ex': 340, 'llm': 640, 'tool': 890}
names = {'op': '운영자', 'ex': '실행 프로그램', 'llm': 'LLM', 'tool': '업무 도구'}
for k, x in X.items():
    for y in (8, 650):
        g.rect(x - 90, y, 180, 52, '#eef3fa', '#44546a', 2, None, 6)
        g.text(x, y + 34, names[k], 24, True, INK)
    g.line(x, 60, x, 650, '#999', None, None, 2)
# loop 영역
g.rect(215, 210, 740, 330, 'none', '#888', 2, '6 5', 4)
g.text(228, 236, 'loop', 20, True, '#555', 'start')
g.text(945, 236, '[추가 작업이 필요한 동안]', 20, False, '#555', 'end')


def msg(a, b, y, t, dash=None):
    g.line(X[a], y, X[b] + (-3 if X[b] > X[a] else 3), y, INK, 'ar', dash, 2)
    g.text((X[a] + X[b]) // 2, y - 10, t, 20, False, INK, 'middle', True)


msg('op', 'ex', 105, '자연어 질문')
msg('ex', 'llm', 165, '질문 + 지시문 + 사용 가능한 도구 명세')
msg('llm', 'ex', 285, '도구 호출 요청 JSON 생성')
g.text(X['ex'] + 14, 336, 'JSON 파싱 및 인자·권한 검증', 20, False, INK, 'start')
g.path('M%d,350 h40 v22 h-38' % X['ex'], INK, 'ar', None, 2)
msg('ex', 'tool', 415, '지정한 함수 실행')
msg('tool', 'ex', 465, '조회·검색·계산 결과', '8 6')
msg('ex', 'llm', 515, '기존 대화 + 호출 기록 + 실행 결과')
msg('llm', 'ex', 575, '최종 답변 생성', '8 6')
msg('ex', 'op', 625, '답변과 근거 제시', '8 6')
g.save('fig2_toolcall')
