import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
f4 = 'deck_v4.py' if os.path.exists(os.path.join(HERE, 'deck_v4.py')) else 'edit_deck_1126_v4.py'
s = open(os.path.join(HERE, f4), encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a); s = s.replace(a, b)
rep('assert len(S) == 24', 'assert len(S) == 25')
# 같은 자리에 오는 글자의 크기를 맞춘다
rep("name, 1200, 1, color, 'ctr', 'ctr')", "name, 1300, 1, color, 'ctr', 'ctr')")                      # Class 상자 = Entity 상자 이름
rep("('조회 구조', 1050, 1, GRAY), ('(Class)', 950, 0, GRAY)", "('조회 구조', 1050, 1, GRAY), ('(Class)', 1050, 1, GRAY)")
rep("label, 950, 1, GRAY, 'l', 'ctr')", "label, 1050, 1, GRAY, 'l', 'ctr')")
rep("240000, '상태를 가짐', 1000, 1, GRAY, 'ctr')", "240000, '상태를 가짐', 1100, 1, GRAY, 'ctr')")
rep("240000, '적용됨', 1000, 1, GRAY, 'ctr')", "240000, '적용됨', 1100, 1, GRAY, 'ctr')")
rep("240000, '근거를 둠', 1000, 1, GRAY, 'ctr')", "240000, '근거를 둠', 1100, 1, GRAY, 'ctr')")
rep("'열쇠로 조회', 1050, 1, TEAL, 'ctr')", "'열쇠로 조회', 1100, 1, TEAL, 'ctr')")
rep("('측정 저장소의 가장 최근 시각', 1050, 1, TEAL), ('2026-09-28 23:00  수위 131.6689', 950, 0, INK)", "('측정 저장소', 1050, 1, TEAL), ('가장 최근 시각 2026-09-28 23:00', 950, 0, INK), ('수위 131.6689 EL.m', 950, 0, INK)")
rep("('문서 저장소', 1000, 1, GRAY), ('별표 3 원문', 950, 0, INK)", "('문서 저장소', 1050, 1, GRAY), ('별표 3 원문', 950, 0, INK)")
rep("'LLM은 공개된 범용 모델(Qwen3-32B)을 추가 학습 없이 사용', 1000, 0, GRAY", "'LLM은 공개된 범용 모델(Qwen3-32B)을 추가 학습 없이 사용', 1050, 0, GRAY")
rep("'질문이 어느 CQ에 해당하는지와 댐, 기간을 뽑아 정해진 형식으로 출력', 1150, 0, GRAY", "'질문이 어느 CQ에 해당하는지와 댐, 기간을 뽑아 정해진 형식으로 출력', 1050, 0, GRAY")
rep("300000, a, 1200, 1, BLUE))", "300000, a, 1300, 1, BLUE))")
rep("3000000, 300000, name, 1200, 1, NAVY, 'l', 'ctr')", "3000000, 300000, name, 1300, 1, NAVY, 'l', 'ctr')")
rep("prs.save(OUT)", """
s9 = S[8]; t9 = s9.shapes[1]; assert t9.text_frame.text == '자료가 KG가 되는 과정'
settext(t9, '자료가 KG가 되는 과정: 방류 승인 기록')
prs.save(OUT)""")
s = s.replace("f3 = ", "")
s = s.replace("src = open(os.path.join(HERE, 'deck_v3.py' if os.path.exists(os.path.join(HERE, 'deck_v3.py')) else 'edit_deck_1126_v3.py'), encoding='utf-8').read()", "src = open(os.path.join(HERE, 'deck_v3.py' if os.path.exists(os.path.join(HERE, 'deck_v3.py')) else 'edit_deck_1126_v3.py'), encoding='utf-8').read()")
exec(compile(s, f4, 'exec'))
