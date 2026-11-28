# -*- coding: utf-8 -*-
"""최종보고서에서 직접 그린 그림 7개의 도형 목록(한글 도형으로 넣는다).
도형: ('box', x, y, w, h, [줄...], 채움색) / ('text', x, y, w, h, [줄...]) / ('arrow', x1, y1, x2, y2). 단위는 hwpunit(1mm = 283.5)."""
B, G, Y, P, PANEL, W0 = '#E8EDFA', '#EDF4EC', '#FDF5E2', '#F9ECEC', '#F7F7F7', '#FFFFFF'
FULL = 48400


def row(labels, y, bw, bh, gap, fill, arrows=True, total=FULL, x0=None):
    """상자를 한 줄로 가운데에 놓고 사이를 화살표로 잇는다."""
    n = len(labels)
    x = (total - (n * bw + (n - 1) * gap)) // 2 if x0 is None else x0
    X = [x + i * (bw + gap) for i in range(n)]
    fills = fill if isinstance(fill, list) else [fill] * n
    sh = [('box', X[i], y, bw, bh, list(labels[i]), fills[i]) for i in range(n)]
    if arrows:
        sh += [('arrow', X[i] + bw, y + bh // 2, X[i + 1], y + bh // 2) for i in range(n - 1)]
    return sh, X


def noy():
    bw, bh, gap = 10600, 5800, 2000
    t = [('1단계', '분야와 범위의 결정'), ('2단계', '기존 온톨로지의', '재사용 검토'), ('3단계', '중요한 용어의 나열'), ('4단계', 'Class와 계층의 정의'),
         ('5단계', 'Class의 속성 정의'), ('6단계', '속성의 제약 정의'), ('7단계', '인스턴스의 생성')]
    sh, X = row(t[:4], 0, bw, bh, gap, B)
    y2 = 8400
    sh += [('arrow', X[3] + bw // 2, bh, X[3] + bw // 2, y2)]
    sh += [('box', X[3 - i], y2, bw, bh, list(t[4 + i]), G) for i in range(3)]
    sh += [('arrow', X[3 - i], y2 + bh // 2, X[2 - i] + bw, y2 + bh // 2) for i in range(2)]
    sh += [('text', X[1], y2 + bh + 400, X[3] + bw - X[1], 2200, ['초기 판을 만든 뒤 반복하여 수정'])]
    return sh, FULL, y2 + bh + 2600


def arch():
    ph, gap = 7400, 3000
    sh = []
    ys = [0, ph + gap, 2 * (ph + gap)]
    for y, name in zip(ys, ['응답 계층', '검색 계층', '지식기반 계층']):
        sh += [('box', 0, y, FULL, ph, [], PANEL), ('text', 300, y + 200, 9000, 2400, [name])]
    sh += row([('근거 기반 응답 (sLLM)',)], ys[0] + 2500, 15000, 3400, 0, B)[0]
    sh += row([('의도·대상 파악', '(사용자 질의 해석)'), ('근거 검색',), ('근거 구성',)], ys[1] + 2300, 11500, 4300, 2400, Y)[0]
    sh += row([('KG', '(개체·관계)'), ('측정자료 저장소',), ('문서 저장소',)], ys[2] + 2300, 11500, 4300, 1200, G, arrows=False)[0]
    for k, lab in ((1, '근거 묶음'), (2, '근거')):
        sh += [('arrow', FULL // 2, ys[k], FULL // 2, ys[k - 1] + ph), ('text', FULL // 2 + 500, ys[k] - gap + 400, 8000, 2200, [lab])]
    return sh, FULL, ys[2] + ph


def prep():
    c = [(0, 10000), (13000, 22000), (38000, 10400)]; hh, rh = 2700, 4300
    head = ['자료 유형', '처리', '결과']
    rows = [(('구조화 자료',), ('열→속성, 행→개체 대응', '표기 형식 통일, 값은 원본 유지'), ('개체·속성 (KG)',)),
            (('수치 시계열',), ('외부 저장소에 보관', 'KG와 식별 키로 연계'), ('측정자료 저장소',)),
            (('문서 자료',), ('문서 단위 분리', '규칙 기반 값 추출'), ('개체·속성 (KG)', '원문 (문서 저장소)'))]
    sh = [('box', x, 0, w, hh, [head[i]], '#E6E9F2') for i, (x, w) in enumerate(c)]
    fills = [B, W0, G]
    for r, cells in enumerate(rows):
        y = hh + r * rh
        sh += [('box', x, y, w, rh, list(cells[i]), fills[i]) for i, (x, w) in enumerate(c)]
        sh += [('arrow', c[i][0] + c[i][1] + 400, y + rh // 2, c[i + 1][0] - 400, y + rh // 2) for i in range(2)]
    return sh, FULL, hh + 3 * rh


def onto():
    bw, bh = 11000, 3400
    sh, X = row([('수문·기상 상태',), ('운영행위',), ('방류 승인',), ('운영기준',)], 0, bw, bh, 1200, Y, arrows=False)
    dx, dw, dy = 13200, 22000, 6400
    sh += [('arrow', FULL // 2, dy, FULL // 2, bh), ('text', FULL // 2 + 500, bh + 400, 8000, 2200, ['댐에 연결'])]
    sh += [('box', dx, dy, dw, bh, ['댐'], B)]
    sh += [('text', 0, dy + bh + 500, FULL, 2200, ['수문·기상 상태, 운영행위, 방류 승인, 운영기준 → 근거자료에 연결(출처 추적)'])]
    y3 = dy + bh + 3200
    sh += [('box', dx, y3, dw, 4600, ['근거자료', '값이 적힌 자료와 그 위치'], G)]
    return sh, FULL, y3 + 4600


def proc():
    bw, bh = 9800, 4400
    sh, X = row([('① 질문·범위', '정의'), ('② 온톨로지', '정의'), ('③ KG 구축',), ('④ 점검',)], 0, bw, bh, 2400, [B, B, G, Y])
    sh += [('arrow', X[3] + bw // 2, bh + 2600, X[1] + bw // 2, bh + 2600), ('arrow', X[1] + bw // 2, bh + 2600, X[1] + bw // 2, bh)]
    sh += [('arrow', X[3] + bw // 2, bh, X[3] + bw // 2, bh + 2600)]
    sh += [('text', X[1] + bw // 2 + 500, bh + 300, X[3] - X[1] - 1000, 2200, ['전문가 검토 후 ②에 반영 (반복)'])]
    y2 = bh + 4000
    sh += [('box', 1500, y2, FULL - 3000, 3400, ['⑤ 질문에 필요한 개체에 도달하지 못하면 부족한 관계·속성을 보완'], P)]
    return sh, FULL, y2 + 3400


def pipeline():
    ph, gap, bh = 8200, 3200, 4400
    sh = [('box', 0, 0, FULL, ph, [], PANEL), ('text', 300, 200, 10000, 2400, ['지식기반 구축'])]
    sh += row([('① 수집', '구조화 자료, 문서 자료'), ('② 전처리', '자료 유형별 정리'), ('③ 지식기반 구성', 'KG, 외부 저장소')], 2700, 12400, bh, 2400, G)[0]
    y2 = ph + gap
    sh += [('box', 0, y2, FULL, ph, [], PANEL), ('text', 300, y2 + 200, 10000, 2400, ['질의응답'])]
    r, X = row([('④ 질의 해석', '의도·대상·기간'), ('⑤ 근거 조회', '의도별 질의 규칙'), ('⑥ 근거 정리', '표준 프롬프트 프레임'), ('⑦ 응답', 'sLLM')], y2 + 2700, 10600, bh, 1800, [Y, Y, Y, B])
    sh += r
    sh += [('text', 300, ph + 500, 6500, 2200, ['사용자 질의']), ('arrow', 7400, ph + 300, 7400, y2 - 300)]
    sh += [('arrow', FULL - 7400, ph + 300, FULL - 7400, y2 - 300), ('text', FULL - 6800, ph + 500, 4000, 2200, ['근거'])]
    return sh, FULL, y2 + ph


def frame():
    cx, cw, bh, gap = 9200, 30000, 3400, 2000
    sh = [('box', cx, 0, cw, bh, ['사용자 질의'], B)]
    y = bh + gap
    sh += [('arrow', FULL // 2, bh, FULL // 2, y)]
    ph = 7400
    sh += [('box', 3000, y, FULL - 6000, ph, [], PANEL), ('text', 3300, y + 300, FULL - 6600, 2200, ['근거 묶음 (구역별, 항목마다 출처 번호)'])]
    sh += row([('현재 상태',), ('과거 이력',), ('운영 기준',), ('출처·위치',)], y + 3000, 9400, 3400, 1100, G, arrows=False)[0]
    y2 = y + ph + gap
    sh += [('arrow', FULL // 2, y + ph, FULL // 2, y2), ('box', cx, y2, cw, bh, ['근거 사용 원칙'], Y)]
    y3 = y2 + bh + gap
    sh += [('arrow', FULL // 2, y2 + bh, FULL // 2, y3), ('box', cx, y3, cw, 4400, ['sLLM 응답', '근거·판단 구분 답변'], P)]
    return sh, FULL, y3 + 4400


DRAWN = {'s22_fig_noy': noy(), 's13_fig_arch': arch(), 's22_fig_prep': prep(), 's22_fig_onto': onto(),
         's22_fig_proc': proc(), 's23_pipeline': pipeline(), 's23_frame_fig': frame()}


def _w(s):
    return sum(1000 if ord(c) > 0x2E7F or c in '①②③④⑤⑥⑦→·' and c != '·' else (350 if c == ' ' else 600) for c in s)


if __name__ == '__main__':                     # 미리보기(SVG)와 글자 넘침 점검
    import sys
    for k, (sh, W, H) in DRAWN.items():
        o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-200 -200 %d %d" width="%d" height="%d" font-family="WenQuanYi Zen Hei" font-size="1000">' % (W + 400, H + 400, (W + 400) // 40, (H + 400) // 40),
             '<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#404040"/></marker></defs><rect x="-200" y="-200" width="100%" height="100%" fill="white"/>']
        for s in sh:
            if s[0] == 'arrow':
                o.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#404040" stroke-width="85" marker-end="url(#a)"/>' % s[1:5])
            else:
                _, x, y, w, h, lines = s[:6]
                if s[0] == 'box': o.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="#404040" stroke-width="57"/>' % (x, y, w, h, s[6]))
                for i, t in enumerate(lines):
                    if _w(t) > w - 566: print('넘침', k, t, _w(t), w - 566)
                    o.append('<text x="%d" y="%d" text-anchor="middle">%s</text>' % (x + w // 2, y + h // 2 + 350 + int((i - (len(lines) - 1) / 2) * 1600), t))
                if len(lines) * 1600 + 566 > h: print('높이 부족', k, lines, h)
            if s[0] != 'arrow' and (s[1] < 0 or s[1] + s[3] > W or s[2] + s[4] > H): print('범위 밖', k, s)
        open(sys.argv[1] + '/' + k + '.svg', 'w', encoding='utf-8').write(''.join(o) + '</svg>')
