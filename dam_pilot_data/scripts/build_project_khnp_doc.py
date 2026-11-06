#!/usr/bin/env python3
"""과제 자료(docx): 한수원 11/26 방문 준비 — 태스크 82개, 질문 세트, 지금 구조로 실행한 결과, 한계와 개선할 점, 시연 계획.
랩미팅 자료(연구)와 분리한 과제용 자료이다. 랩미팅 자료와 같은 서식(labdoc_lib)을 쓴다.
사용: python3 scripts/build_project_khnp_doc.py <출력 docx>
그림: project_khnp/fig/ (이 스크립트가 HTML을 쓰고 playwright로 찍는다. 구조 그림과 시연 화면은 기존 그림을 쓴다)
"""
import collections, csv, importlib.util, json, os, re, shutil, struct, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('L', os.path.join(HERE, 'labdoc_lib.py')); L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
_li, _para = L.li, L.para
LS = ' w:line="252" w:lineRule="auto"'
L.li = lambda t, sz=19: _li(t, sz).replace('<w:spacing w:after="60"/>', '<w:spacing w:after="40"%s/>' % LS, 1)
L.para = lambda t, sz=19: _para(t, sz).replace('w:after="120"/>', 'w:after="100"%s/>' % LS, 1)
L.cell.__defaults__ = L.cell.__defaults__[:4] + (17,) + L.cell.__defaults__[5:]
L.table.__defaults__ = (True, True, 17, ())
_h1 = L.h1
L.h1 = lambda t, pagebreak=False: _h1(t, False).replace('<w:pStyle w:val="1"/>', '<w:pStyle w:val="1"/><w:spacing w:before="280" w:after="40"/>', 1)
L.label = lambda t: '<w:p><w:pPr><w:keepNext/><w:spacing w:before="140" w:after="20"/><w:rPr>%s</w:rPr></w:pPr>%s</w:p>' % (L.LANG, L.run(t, sz=22, b=True, color='1F4E79'))
for n in ('run', 'title', 'subtitle', 'dateline', 'label', 'h1', 'h2', 'para', 'li', 'spacer', 'table', 'caption'):
    globals()[n] = getattr(L, n)

ROOT = os.path.join(HERE, '..'); R5 = os.path.join(ROOT, '05_retrieval')
REPO = os.path.join(ROOT, '..')
LAB = os.path.join(REPO, 'lab_meeting')
OUTDIR = os.path.join(REPO, 'project_khnp'); FIG = os.path.join(OUTDIR, 'fig'); os.makedirs(FIG, exist_ok=True)
OUT = sys.argv[1]
T = L.Template(os.path.join(LAB, '랩미팅 자료_KG구축_검색답변_최종.docx'))

# ------------------------------------------------------------------ 사실 (파일에서 읽음)
TASKS = list(csv.DictReader(open(os.path.join(LAB, 'task_candidates', '태스크후보_v1.csv'), encoding='utf-8-sig')))
TK = {t['번호']: t for t in TASKS}
Q82 = json.load(open(os.path.join(R5, 'question_set_tasks82.json'), encoding='utf-8'))
RV = {r['id']: r for r in csv.DictReader(open(os.path.join(R5, 'tasks82_llm_review.csv'), encoding='utf-8-sig'))}
RUN = os.path.join(R5, 'server_runs_20261106_tasks82')
ANS = {f[:-5]: json.load(open(os.path.join(RUN, f), encoding='utf-8')) for f in os.listdir(RUN) if re.match(r'q\d+\.json$', f)}
assert len(TASKS) == len(Q82) == len(RV) == len(ANS) == 82
AREAS = list(dict.fromkeys(t['업무 영역'] for t in TASKS))
assert len(AREAS) == 11


def scope(q):   # 질문 세트에서 정한 범위
    if q['expect'] == 'answer_now':
        return 'now'
    if q['expect'] == 'extend':
        return 'pub' if q['extension'].startswith('P') else 'ext'
    return 'int'


SC_NAME = {'now': '지금 구조로 답함', 'ext': '확장하면 답함(O·T)', 'pub': '공개자료를 모으면 답함(P)', 'int': '내부 자료·모형 필요'}
SC = collections.Counter(scope(q) for q in Q82)
assert SC == {'now': 13, 'ext': 31, 'pub': 5, 'int': 33}, SC
OUTS = ['① 근거로 맞게 답함', '② 거절·"자료에 없음" 안내', '③ 잘못 답함', '④ 처리 실패']
EXPS = ['지금 답해야 함', '확장해야 함', '거절·안내해야 함']
XC = collections.Counter((r['기대'], r['결과']) for r in RV.values())
LC = {k: sum(k in r['한계'] for r in RV.values()) for k in 'ABCDEFG'}
assert LC == {'A': 11, 'B': 6, 'C': 6, 'D': 6, 'E': 8, 'F': 5, 'G': 16}
SEC = round(sum(float(r['초']) for r in RV.values()) / 82)
ANSWERED_OK = [q['id'] for q in Q82 if RV[q['id']]['결과'].startswith('①')]

# ------------------------------------------------------------------ 그림 (HTML → PNG)
SEQ = {'now': '#1c5cab', 'ext': '#5598e7', 'pub': '#9ec5f4', 'int': '#c4c3bd'}   # 범위: 파랑 단계(가까울수록 진함) + 회색(우리 자료 밖)
SEQ_TXT = {'now': '#fff', 'ext': '#fff', 'pub': '#0b0b0b', 'int': '#0b0b0b'}
CAT = ['#2a78d6', '#1baf7a', '#eb6834', '#6250d6']   # 결과 ①~④ (validate_palette.js light: 통과, 청록은 숫자 표시로 보완)
CAT_TXT = ['#fff', '#0b0b0b', '#fff', '#fff']
FONT = 'font-family="WenQuanYi Zen Hei"'


def legend(items):
    return ''.join('<span style="display:inline-flex;align-items:center;gap:6px;margin-right:18px"><span style="width:14px;height:14px;border-radius:3px;background:%s;display:inline-block"></span>%s</span>' % (c, t) for c, t in items)


def hbar_rows(rows, keys, colors, txt, label_w=150, bar_w=600, unit=None, total_label=True):
    """rows: [(라벨, {key: n})]. 막대 하나가 한 줄, 조각 사이 2px 흰 틈, 조각 안에 개수."""
    unit = unit or bar_w / max(sum(v.values()) for _, v in rows)
    h, gap = 26, 10; H = len(rows) * (h + gap) + 4
    s = ['<svg width="%d" height="%d" viewBox="0 0 %d %d" %s font-size="13">' % (label_w + bar_w + 50, H, label_w + bar_w + 50, H, FONT)]
    for i, (lab, v) in enumerate(rows):
        y = i * (h + gap) + 2; x = label_w
        s.append('<text x="%d" y="%d" text-anchor="end" fill="#0b0b0b">%s</text>' % (label_w - 10, y + h / 2 + 5, lab))
        for k, c, tc in zip(keys, colors, txt):
            n = v.get(k, 0)
            if not n:
                continue
            w = n * unit
            s.append('<rect x="%.1f" y="%d" width="%.1f" height="%d" rx="3" fill="%s"/>' % (x, y, max(w - 2, 1), h, c))
            if w >= 16:
                s.append('<text x="%.1f" y="%d" text-anchor="middle" fill="%s" font-weight="bold">%d</text>' % (x + (w - 2) / 2, y + h / 2 + 5, tc, n))
            x += w
        if total_label:
            s.append('<text x="%.1f" y="%d" fill="#52514e">%d</text>' % (x + 6, y + h / 2 + 5, sum(v.values())))
    s.append('</svg>')
    return ''.join(s)


KEYS = ['now', 'ext', 'pub', 'int']
by_area = collections.defaultdict(collections.Counter)
for q in Q82:
    by_area[TK[q['task']]['업무 영역']][scope(q)] += 1
F1 = ('<div class="fig" id="t1"><div class="lg">%s</div>%s</div>' %
      (legend([(SEQ[k], SC_NAME[k]) for k in KEYS]),
       hbar_rows([('%s %s' % (chr(65 + i), a), by_area[a]) for i, a in enumerate(AREAS)], KEYS, [SEQ[k] for k in KEYS], [SEQ_TXT[k] for k in KEYS], label_w=190, bar_w=560, unit=56)))
F2 = ('<div class="fig" id="t2"><div class="lg">%s</div>%s</div>' %
      (legend(list(zip(CAT, OUTS))),
       hbar_rows([('%s (%d)' % (e, sum(XC[(e, o)] for o in OUTS)), {o: XC[(e, o)] for o in OUTS}) for e in EXPS], OUTS, CAT, CAT_TXT, label_w=170, bar_w=560, unit=560 / 36, total_label=False)))
# 그림 3: 82개 전체, 범위별로 쌓고 누적 개수 표시
cum, segs, x0, U = 0, [], 20, 760 / 82
for k in KEYS:
    n = SC[k]; w = n * U
    segs.append('<rect x="%.1f" y="40" width="%.1f" height="34" rx="3" fill="%s"/><text x="%.1f" y="62" text-anchor="middle" fill="%s" font-weight="bold">%d</text>' % (x0 + cum * U, w - 2, SEQ[k], x0 + cum * U + (w - 2) / 2, SEQ_TXT[k], n))
    cum += n
marks = ''
for c, t, anc, dx in [(13, '지금 13', 'middle', 0), (44, '확장 후 44', 'end', -4), (49, '공개자료까지 49', 'start', 4)]:
    xx = x0 + c * U - 1
    marks += '<line x1="%.1f" y1="30" x2="%.1f" y2="84" stroke="#0b0b0b" stroke-width="1.5"/><text x="%.1f" y="22" text-anchor="%s" fill="#0b0b0b" font-weight="bold">%s</text>' % (xx, xx, xx + dx, anc, t)
F3 = ('<div class="fig" id="t3"><div class="lg">%s</div><svg width="800" height="110" viewBox="0 0 800 110" %s font-size="13">%s%s'
      '<text x="20" y="102" fill="#52514e">0</text><text x="780" y="102" text-anchor="end" fill="#52514e">82개 태스크</text></svg></div>' %
      (legend([(SEQ[k], SC_NAME[k]) for k in KEYS]), FONT, ''.join(segs), marks))
html = ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>body{margin:0;background:#fff;color:#0b0b0b;font-family:"WenQuanYi Zen Hei",sans-serif;font-size:14px}'
        '.fig{width:860px;padding:12px 14px;background:#fff}.lg{font-size:13px;color:#52514e;margin:0 0 10px 4px}</style></head><body>' + F1 + F2 + F3 + '</body></html>')
open(os.path.join(FIG, 'charts.html'), 'w', encoding='utf-8').write(html)
SHOT = os.path.join(HERE, 'shot_figs.js')
subprocess.run(['node', SHOT, os.path.join(FIG, 'charts.html'), FIG, 'kh_', 't1', 't2', 't3'], check=True)
shutil.copy(os.path.join(LAB, 'how2', 'fig', 'kg2_q0.png'), os.path.join(FIG, 'kh_flow.png'))
shutil.copy(os.path.join(OUTDIR, 'demo_screen.png'), os.path.join(FIG, 'kh_demo.png'))

TRIM = os.path.join(FIG, 'trim'); os.makedirs(TRIM, exist_ok=True)
PX2DXA = L.W * 0.97 / 2100 * 0.76


def fig(name, full=False):
    pth = os.path.join(TRIM, name + '.png')
    subprocess.run(['convert', os.path.join(FIG, name + '.png'), '-trim', '-bordercolor', 'white', '-border', '12', '+repage', pth], check=True)
    with open(pth, 'rb') as f:
        w, h = struct.unpack('>II', f.read(24)[16:24])
    return L.image(name, pth, w, h, name, width=L.W if full else min(int(w * PX2DXA), L.W))


B = []
add = B.append
FIGNO = {}


def figcap(name, text, full=False):
    FIGNO[name] = len(FIGNO) + 1
    add(fig('kh_' + name, full))
    add(caption('그림 %d. %s' % (FIGNO[name], text)))


def lis(*items):
    for t in items:
        add(li(t))


rtable = lambda rows, widths, sz=17: table(rows, widths, True, False, sz)

# ================================================================== 표지
add(title('댐 운영 LLM 태스크 82개와 시연 계획', '한수원 방문(11/26) 준비'))
add(subtitle('태스크 · 질문 세트 · 지금 구조의 실행 결과 · 한계와 개선 · 시연'))
add(dateline('2026.11 · 문경민'))

# ================================================================== 1. 개요
add(h1('1. 개요'))
lis('11/26 한수원 방문에서 두 가지를 한다. 지금까지 만든 KG 기반 질의응답 구조를 시연하고, 실무자에게 댐 운영 LLM 태스크 82개를 검토받는다.',
    '이 자료는 태스크 82개를 만든 내용(2장), 태스크마다 만든 질문 세트(3장), 지금 구조로 82개 질문에 답을 받은 결과(4장), 한계와 개선할 점(5장), 시연 계획(6장)을 정리한다.',
    '태스크 82개 전체와 질문별 결과는 부록 A, B에 있다.')

# ================================================================== 2. 태스크 82개
add(h1('2. 태스크 82개'))
add(h2('2.1 태스크란'))
lis('태스크는 LLM 시스템에 맡길 수 있는 일 하나로, 입력과 출력이 정해져 있다(10/15 회의). 예: "지정 댐의 가장 최근 수위·유입량·방류량을 모아 요약"(입력: 수문 시간자료, 출력: 수치와 서술).',
    '실무자가 필요하다고 확인한 태스크는 이후 학습 데이터(SFT, DPO)와 검증 데이터셋(날짜·수치·순서를 바꿔 늘림)을 만드는 기준이 된다.')
add(h2('2.2 만든 방법과 구성'))
lis('댐 운영 업무를 11개 영역으로 나누고, 영역마다 LLM에 맡길 수 있는 일을 실현 가능성과 관계없이 모두 적었다. 태스크마다 하는 일, 사용자 요청 예, 입력 자료, 처리 유형, 출력 형태를 적었다(부록 A).',
    '그림 {{t1}}은 영역별 태스크 수이다. 색은 3장에서 질문마다 정한 범위로, 지금 구조로 답할 수 있는지, 확장하면 답할 수 있는지, 한수원 내부 자료나 예측 모형이 필요한지를 나타낸다.',
    '수문 상황 파악, 방류 승인, 규정·기준, 과거 사례 영역은 지금 구조나 확장으로 다룰 수 있는 태스크가 많다. 발전 운영, 시설·계측, 예측·계획 영역은 대부분 내부 자료나 모형이 필요하다.')
figcap('t1', '업무 영역별 태스크 수와 범위 (82개)', full=True)
add(h2('2.3 실무자 확인표'))
lis('태스크 82개를 실무자 확인표(태스크후보_실무자체크_v1.xlsx)로 만들었다. 태스크마다 "필요", "불필요"에 표시하고 의견을 적는다. 목록에 없는 업무는 추가 태스크 시트에 적는다.',
    '확인표에는 범위(지금 구조로 답할 수 있는지)를 넣지 않았다. 실현 가능성과 관계없이 업무에 필요한지만 묻기 위해서이다.')

# ================================================================== 3. 질문 세트
add(h1('3. 태스크 82개로 만든 질문 세트'))
lis('태스크마다 사용자 요청 예의 "OO댐", "어제" 같은 부분을 실제 대상 댐(충주댐, 소양강댐, 횡성댐, 광동댐)과 날짜로 바꿔 질문을 하나씩 만들었다(82개, 표 1에 예).',
    '실행 전에 질문마다 지금 구조로 기대하는 결과를 정했다(표 2). 지금 답해야 하는 질문 13개에는 정답 의도(질문 종류, 댐, 기간)를 적어 LLM의 해석과 비교했다. 확장해야 하는 질문에는 필요한 확장을 적었다(5장 표 5).')
EXQ = ['A01', 'A02', 'C01', 'E01', 'H02', 'J01']
QT = {q['task']: q for q in Q82}
EXPN = {'answer_now': '지금 답해야 함', 'extend': '확장해야 함', 'refuse': '거절·안내해야 함'}
add(label('표 1. 사용자 요청 예에서 만든 질문 (예)'))
add(rtable([['태스크', '사용자 요청 예', '실행한 질문', '기대 결과']]
           + [[t + ' ' + TK[t]['태스크'], TK[t]['사용자 요청 예'], QT[t]['question'], EXPN[QT[t]['expect']] + (' (%s)' % QT[t]['extension'] if QT[t]['extension'] else '')] for t in EXQ],
           [2600, 2500, 3072, 1800]))
add(label('표 2. 기대 결과의 뜻과 질문 수'))
add(rtable([['기대 결과', '뜻', '질문 수'],
            ['지금 답해야 함', '지금 KG와 저장소(질문 종류 CQ1~CQ6)로 답할 수 있다', str(SC['now'])],
            ['확장해야 함', '온톨로지나 계산 도구를 확장하거나(%d), 공개자료를 더 모으면(%d) 답할 수 있다' % (SC['ext'], SC['pub']), str(SC['ext'] + SC['pub'])],
            ['거절·안내해야 함', '한수원 내부 자료(발전, 설비·계측, 매뉴얼)나 예측 모형이 필요하다. 답 대신 범위를 안내해야 한다', str(SC['int'])],
            ['계', '', '82']], [2000, 6772, 1200]))

# ================================================================== 4. 실행 결과
add(h1('4. 지금 구조로 82개 질문에 답을 받은 결과'))
add(h2('4.1 지금 구조'))
lis('대상은 K-water 다목적댐 4개(충주, 소양강, 횡성, 광동)이다. KG에는 Entity 264개와 Relation 418개(승인, 운영행위, 수문·기상 상태, 운영기준, 근거)가 있고, 시간별 측정값(2010-08 ~ 2026-09-28 23:00)과 규정 원문(연계운영규정 별표3)은 KG 밖 저장소에 둔다. 승인 기록은 2021-07까지 있다.',
    '그림 {{flow}}처럼 질문 하나가 여섯 과정을 거친다. LLM은 질문 해석(①)과 답변 작성(⑥)에만 쓰고, 근거는 코드가 KG와 저장소에서 찾는다. 답변의 사실마다 출처 번호가 붙는다.',
    '답할 수 있는 질문 종류는 현재 수문 상태(CQ1), 과거 수문 상태(CQ2), 과거 운영행위(CQ3), 방류 승인(CQ4), 홍수기 제한수위(CQ5), 공식 근거(CQ6)이다.')
figcap('flow', '질문 하나가 처리되는 과정 (2020년 8월 충주댐 질문, 10/16 서버 실행)', full=True)
add(h2('4.2 실행'))
lis('2026-11-06 연구실 서버에서 82개 질문을 실행했다. 모델은 Qwen3-32B-AWQ(범용 LLM, GPU 1장)이며 질문당 평균 %d초 걸렸다.' % SEC,
    '답변까지 읽고 결과를 네 가지로 나눴다. ③은 묻는 것과 다른 값으로 대신 답했거나 근거 없는 판단을 쓴 경우, ④는 LLM이 낸 값의 형식이 틀려 조회하지 않았거나 근거가 모델 한도를 넘은 경우이다.')
add(h2('4.3 결과'))
figcap('t2', '기대 결과별 실행 결과 (82개)', full=True)
lis('지금 답해야 하는 13개 중 %d개는 근거의 값과 출처 번호로 맞게 답했다. 3개는 기간 값의 형식이 틀려 조회하지 못했고, 1개는 "2017년 8월"을 8월 1일 하루로 읽어 "방류 기록 없음"이라고 답했다. 광동댐 제한수위는 별표3에 없어 "자료에 없음"이라고 답했다.' % XC[('지금 답해야 함', OUTS[0])],
    '거절·안내해야 하는 33개 중 %d개는 거절하거나 "자료에 없음"이라고 안내했고, %d개는 다른 값이나 근거 없는 판단으로 답했다.' % (XC[('거절·안내해야 함', OUTS[1])], XC[('거절·안내해야 함', OUTS[2])]),
    '확장해야 하는 36개 중 %d개는 "자료에 없음"으로 안내했고, %d개는 지금 근거로 일부 답했다(하루 수위 변화, 언론 설명자료 초안 등). %d개는 잘못 답했고, %d개는 처리하지 못했다.' % tuple(XC[('확장해야 함', o)] for o in (OUTS[1], OUTS[0], OUTS[2], OUTS[3])),
    '표 3은 결과별 실제 예이다.')
add(label('표 3. 결과별 실제 예'))
EX = [('q010', '현재(2026-09-28 23:00) 수위 131.67 EL.m가 홍수기 제한수위 138.0 EL.m보다 낮다고 답함. 출처 [MEA:1003110:2026092823], [CRI:CR-02]'),
      ('q020', '승인 3건으로 방류량이 3000에서 7000㎥/s로 늘고 기간이 두 번 연장된 과정을 정리함. 출처 [APR:3412], [APR:3519], [APR:3647]'),
      ('q026', '의도 해석 단계에서 "발전량은 지원되지 않는다"며 조회하지 않음'),
      ('q063', '총방류량 0.43 CMS를 발전 방류량이라고 답함'),
      ('q052', '충주댐 수위 131.67 EL.m를 하류 목계교 수위라고 답함'),
      ('q014', 'LLM이 기간 값에 형식 예시 "YYYY-MM-DD"를 그대로 내 조회하지 못함'),
      ('q033', '한 달 시간자료(약 10만 자)가 근거로 들어가 모델 한도(32,768토큰)를 넘음')]
QID = {q['id']: q for q in Q82}
add(rtable([['질문', '결과', '답변']] + [[QID[i]['question'], RV[i]['결과'], t] for i, t in EX], [3000, 1900, 5072]))

# ================================================================== 5. 한계와 개선할 점
add(h1('5. 한계와 개선할 점'))
add(h2('5.1 실행에서 드러난 한계와 개선할 점'))
add(label('표 4. 한계와 개선할 점'))
add(rtable([['한계', '질문 수', '실제 예', '개선할 점'],
            ['A 질문 해석(값 추출) 오류', str(LC['A']), '"2017년 8월" → 8월 1일 하루, 방류량 "1000과 2000" → 연도, 형식 예시 "YYYY-MM-DD"를 값으로 냄', '해석 지시문의 값 형식을 실제 예로 바꾸고, 시각("18:00")과 월("2017-08")도 받는다'],
            ['B 오늘 날짜를 모름', str(LC['B']), '"오늘", "지난달", "지금까지"를 2023년 날짜로 가정', '해석 지시문에 오늘 날짜와 자료의 마지막 시각을 넣는다'],
            ['C 근거가 모델 한도를 넘음', str(LC['C']), '한 달 시간자료 약 10만 자, 전체 기간 1,500만 자 이상', '기간이 길면 원자료 대신 기간 통계(최고·최저·평균·변화량)를 근거로 준다'],
            ['D 다른 값으로 대신 답함', str(LC['D']), '발전 방류량 → 총방류량, 목계교 수위 → 충주댐 수위, 계획홍수위 → 홍수기 제한수위', '"묻는 값이 근거에 없으면 다른 값으로 대신하지 않는다"를 답변 지시문에 넣고, 댐 제원을 KG에 넣는다(O1)'],
            ['E 근거 없는 판단', str(LC['E']), '방류 사유 추정, 한 시각의 강우 0 mm로 "건기 지속", 2020년 보고서에 2026년 값을 섞음', '판단은 근거 값끼리의 비교만 쓰게 한다'],
            ['F 거절 이유가 맞지 않음', str(LC['F']), '통보 문자·발전 방류 질문에 "방류 사유는 자료에 없음"', '거절할 때 필요한 자료의 이름을 쓰게 한다'],
            ['G 출처 번호 형식', str(LC['G']), '[CQ5], [자료에 없음]을 출처처럼 붙임', '근거 묶음에 있는 출처 번호만 쓰게 한다']],
           [2100, 900, 3572, 3400]))
lis('D와 E의 답변은 근거와 출처 번호를 갖춘 형식이라, 답변만 읽어서는 잘못 답한 것을 알아보기 어렵다. 시연 전에 A~G를 고치고 같은 82개 질문을 다시 실행해 그림 {{t2}}와 비교한다.')
add(h2('5.2 확장: 답할 수 있는 태스크 넓히기'))
EXC = collections.Counter(q['extension'] for q in Q82 if q['expect'] == 'extend')
EXT = [('O1', '온톨로지', 'Dam 제원(계획홍수위, 상시만수위, 총저수용량, 저수위 등)과 근거'), ('O2', '온톨로지', '운영기준에 홍수기 기간'),
       ('O3', '온톨로지', '규정 조문을 근거로, 문서 저장소 확대'), ('O4', '온톨로지', '댐 사이의 수계(상·하류) 관계'),
       ('T1', '계산 도구', '기간 통계(최고·최저·평균·변화량)'), ('T2', '계산 도구', '예년 같은 시기 비교'), ('T3', '계산 도구', '여러 댐 비교'),
       ('T4', '계산 도구', '승인 방류량 대비 실측 방류량'), ('T5', '계산 도구', '결측·이상치 찾기'), ('T6', '계산 도구', '홍수·가뭄 사상 찾기'),
       ('T7', '계산 도구', '보고서·설명자료 초안'), ('T8', '계산 도구', '번호로 원문 조회')]
assert sum(EXC[c] for c, _, _ in EXT) == SC['ext']
add(label('표 5. 확장과 그것으로 답할 수 있게 되는 태스크'))
add(rtable([['확장', '종류', '내용', '태스크 수', '태스크 예']]
           + [[c, k, d, str(EXC[c]), next(q['task'] + ' ' + q['task_name'] for q in Q82 if q['extension'] == c)] for c, k, d in EXT]
           + [['P1~P4', '자료 수집', '유역 강우, 하천 수위·경보, 하천유지용수 기준, 규정 개정 이력(공개자료)', str(SC['pub']), '']],
           [900, 1200, 4272, 1100, 2500]))
lis('그림 {{t3}}처럼 O1~O4와 T1~T8을 하면 82개 중 %d개, 공개자료(P1~P4)까지 모으면 %d개 태스크를 다루는 구조가 된다.' % (SC['now'] + SC['ext'], SC['now'] + SC['ext'] + SC['pub']),
    '나머지 %d개는 한수원 내부 자료(발전, 설비·계측, 매뉴얼·양식)나 예측 모형이 필요하다. 이 태스크는 KG 검색을 여러 도구 중 하나로 쓰고 내부 자료와 모형을 함께 부르는 에이전트 구조에서 다룬다. 어떤 내부 자료를 받을 수 있는지는 실무자 검토 때 확인한다.' % SC['int'])
figcap('t3', '지금 구조와 확장 뒤에 다루는 태스크 수 (82개 중)', full=True)

# ================================================================== 6. 시연 계획
add(h1('6. 시연 계획'))
add(h2('6.1 발표와 시연 순서 (11/20 과제 발표, 11/26 한수원 방문)'))
add(label('표 6. 발표와 시연 순서'))
add(rtable([['순서', '내용', '보일 것'],
            ['① 구조와 원리', '온톨로지·KG로 댐 운영 자료를 잇고, LLM은 질문 해석과 답변 작성에만 쓰며, 근거는 KG와 저장소에서 찾아 출처 번호를 붙인다', '그림 {{flow}}'],
            ['② 시연', '정해진 범위(대상 댐 4개, 질문 종류 CQ1~CQ6) 안에서 작동하는 것을 보인다. 참석자가 노트북으로 직접 질문하고, 답변의 출처 번호를 눌러 원문을 확인한다', '그림 {{demo}}, 예시 질문'],
            ['③ 한계', '태스크 82개 중 지금 구조로 답하는 범위, 실행에서 드러난 한계, 내부 자료·모형이 필요한 태스크', '그림 {{t2}}, 그림 {{t3}}, 표 4'],
            ['④ 실무자 검토 요청', '태스크 82개가 업무에 필요한지 표시하고, 빠진 업무를 적어 주시도록 요청한다', '실무자 확인표'],
            ['⑤ 다음 계획', '검토 결과를 토대로 온톨로지와 KG를 넓힌다', '표 5']],
           [1900, 5372, 2700]))
add(h2('6.2 시연 화면과 예시 질문'))
lis('시연은 노트북 브라우저의 질의응답 화면으로 한다(그림 {{demo}}). 왼쪽에 대상 댐, 물어볼 수 있는 것, 예시 질문, 알아 둘 점을 두고, 답변의 출처 번호를 누르면 오른쪽에 원문(측정값 행, 승인 기록 행, 규정 원문)이 열린다.',
    '예시 질문은 이번 실행에서 근거로 맞게 답한 질문에서 고른다: %s.' % ', '.join('"%s"' % QID[i]['question'] for i in ['q001', 'q010', 'q020', 'q029', 'q044']),
    '범위 밖 질문(다른 댐, 발전, 예측 등)에는 답 대신 범위와 필요한 자료를 안내한다.',
    '인터넷이 안 될 때를 대비해 시연 동영상을 찍어 둔다.')
figcap('demo', '시연 화면 — 답변의 출처 번호를 누르면 측정 저장소의 원래 행이 열린다 (재생 모드 화면)', full=True)
add(h2('6.3 시연 때 밝힐 점'))
lis('"현재"는 저장된 마지막 시각(2026-09-28 23:00)의 값이며 실시간이 아니다. 승인 기록은 2021-07까지 있다.',
    '범용 LLM(Qwen3-32B-AWQ)을 그대로 썼다. 학습 데이터로 조정하지 않았다.',
    '실제 운영에 쓰려면 한수원 내부 자료 연계와, KG 검색·계산·예측 모형을 함께 부르는 에이전트 구조가 더 필요하다.')
add(h2('6.4 실무자 검토 뒤 계획'))
lis('실무자가 "필요"로 표시한 태스크를 우선 대상으로 정한다.',
    '그 가운데 확장으로 다룰 수 있는 태스크는 표 5의 온톨로지 확장(O)과 계산 도구(T)로 넓히고, 같은 질문으로 다시 실행해 결과를 비교한다.',
    '내부 자료가 필요한 태스크는 받을 수 있는 자료를 확인해 온톨로지에 Class와 Relation을 더한다(예: 발전 실적, 수문 설비).',
    '확인된 태스크로 학습 데이터(SFT, DPO)와 검증 데이터셋을 만든다.')
add(h2('6.5 준비할 것'))
add(label('표 7. 준비할 것'))
add(rtable([['언제까지', '할 일'],
            ['11/20 발표 전', '표 4의 A~G를 고치고 82개 질문을 다시 실행해 비교, 시연 화면의 예시 질문과 안내 문구 갱신, 발표 자료'],
            ['11/26 방문 전', '시연 동영상, 노트북 접속(핫스팟 → 연구실 서버) 점검, 실무자 확인표 준비']],
           [2000, 7972]))

# ================================================================== 부록
para = lambda t, sz=16: L.para(t, sz)
li = lambda t, sz=16: L.li(t, sz)
add(h1('부록 A. 태스크 82개'))
add(label('표 8. 태스크 82개 (영역별)'))
rows = [['번호', '태스크', '하는 일', '사용자 요청 예']]
for t in TASKS:
    rows.append([t['번호'], t['태스크'], t['하는 일'], t['사용자 요청 예']])
add(table(rows, [700, 2300, 4572, 2400], True, False, 13))
add(h1('부록 B. 82개 질문의 실행 결과'))
add(label('표 9. 질문별 범위와 결과'))
SCS = {'now': '지금 구조', 'ext': '확장', 'pub': '공개자료', 'int': '내부 자료·모형'}
rows = [['번호', '실행한 질문', '범위', '결과', '메모']]
for q in sorted(Q82, key=lambda q: q['task']):
    r = RV[q['id']]
    rows.append([q['task'], q['question'], SCS[scope(q)] + (' ' + q['extension'] if q['extension'] else ''), r['결과'], r['메모']])
add(table(rows, [700, 3300, 1300, 1900, 2772], True, False, 13))
add(h1('부록 C. 용어'))
add(table([['용어', '뜻'],
           ['온톨로지', '댐 운영 자료의 종류(Class), 값(Data Property), 관계(Relation)를 정한 틀'],
           ['KG(지식그래프)', '온톨로지에 맞춰 실제 자료를 Entity와 Relation으로 이은 것. Neo4j에 저장한다'],
           ['CQ', '온톨로지가 답해야 할 질문 종류(CQ1~CQ6)'],
           ['근거 묶음', 'KG와 저장소에서 찾은 근거에 출처 번호를 붙여 LLM에 주는 글'],
           ['출처 번호', '근거마다 붙는 표시. KG의 Entity ID(예: APR:3412) 또는 측정값 [MEA:댐 코드:시각]'],
           ['에이전트', 'LLM이 KG 검색, 계산, 예측 모형 같은 여러 도구를 골라 부르며 일을 처리하는 구조']], [2000, 7972], True, True, 14))

body = re.sub(r'\{\{(\w+)\}\}', lambda mo: str(FIGNO[mo.group(1)]), ''.join(B))
T.save(OUT, body, L.IMGS, page_numbers=True)
print('saved', OUT, 'figs', len(FIGNO))
