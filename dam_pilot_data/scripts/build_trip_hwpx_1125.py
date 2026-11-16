#!/usr/bin/env python3
"""출장 계획(안)과 출장계획서(국내)를 한글(hwpx)로 만든다. 서식(글자·문단 모양, 표 테두리)은 실무회의 계획(안) hwpx의 것을 그대로 쓴다.
내용은 build_trip_plan_1125.js, build_trip_form_1125.js(docx)와 같다. 줄 배치 정보(linesegarray)는 넣지 않는다(한글이 열 때 계산).
사용: python3 build_trip_hwpx_1125.py <서식 hwpx> <출장계획안.hwpx> <출장계획서.hwpx>"""
import sys, re, zipfile, random
from xml.sax.saxutils import escape as E

TPL, OUT_PLAN, OUT_FORM = sys.argv[1:4]
src = zipfile.ZipFile(TPL); SEC = src.read('Contents/section0.xml').decode('utf-8')
HEAD = SEC[:SEC.index('<hp:p ')]                     # xml 선언 + <hs:sec ...>
FIRST = SEC[SEC.index('<hp:p '):SEC.index('<hp:run charPrIDRef="7"><hp:tbl')]  # 첫 문단의 구역 설정(secPr) 부분
W = 48190
rid = lambda: str(random.randint(10**8, 2 * 10**9))
won = lambda n: format(n, ',')

def para(runs, ppr):  # runs: [(charPr, text)]
    return '<hp:p id="%s" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">%s</hp:p>' % (
        rid(), ppr, ''.join('<hp:run charPrIDRef="%d"><hp:t>%s</hp:t></hp:run>' % (c, E(t)) for c, t in runs))
sec = lambda t: para([(9, '□ ' + t)], 24)
item = lambda k, v: para([(7, 'ㅇ '), (8, '(%s) ' % k), (7, v)], 25)
dot = lambda t: para([(7, 'ㅇ ' + t)], 25)
note = lambda t: para([(10, t)], 27)
gap = lambda: para([(7, '')], 0)

def tc(lines, col, row, cs, rs, w, h, head=False, left=False, bf=None, cpr=None):
    ps = ''.join(para([(cpr or (11 if head else 10), t)], 29 if left else 28) for t in lines)
    return ('<hp:tc name="" header="%d" hasMargin="1" protect="0" editable="0" dirty="0" borderFillIDRef="%d"><hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">%s</hp:subList>'
            '<hp:cellAddr colAddr="%d" rowAddr="%d"/><hp:cellSpan colSpan="%d" rowSpan="%d"/><hp:cellSz width="%d" height="%d"/><hp:cellMargin left="600" right="600" top="400" bottom="400"/></hp:tc>') % (
        1 if head else 0, bf or (6 if head else 7), ps, col, row, cs, rs, w, h)

def table(widths, rows, wrap=True):
    """rows: [[cell]], cell = dict(t=글 또는 [줄], cs, rs, head, left). 병합으로 가려지는 칸은 적지 않는다."""
    n = len(widths); occ = set(); trs = []; total_h = 0
    for r, cells in enumerate(rows):
        c = 0; out = []; rh = 2100
        for cell in cells:
            while (r, c) in occ: c += 1
            cs, rs = cell.get('cs', 1), cell.get('rs', 1)
            lines = cell['t'] if isinstance(cell['t'], list) else [cell['t']]
            for dr in range(rs):
                for dc in range(cs):
                    if dr or dc: occ.add((r + dr, c + dc))
            h = 1400 * len(lines) + 800
            if rs == 1: rh = max(rh, h)
            out.append((lines, c, r, cs, rs, sum(widths[c:c + cs]), cell)); c += cs
        trs.append('<hp:tr>' + ''.join(tc(l, c, r, cs, rs, w, rh * rs, head=x.get('head', False), left=x.get('left', False), bf=x.get('bf'), cpr=x.get('cpr')) for l, c, r, cs, rs, w, x in out) + '</hp:tr>')
        total_h += rh
    t = ('<hp:tbl id="%s" zOrder="1" numberingType="TABLE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" pageBreak="CELL" repeatHeader="1" rowCnt="%d" colCnt="%d" cellSpacing="0" borderFillIDRef="3" noAdjust="0">'
         '<hp:sz width="%d" widthRelTo="ABSOLUTE" height="%d" heightRelTo="ABSOLUTE" protect="0"/><hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="COLUMN" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>'
         '<hp:outMargin left="0" right="0" top="0" bottom="0"/><hp:inMargin left="600" right="600" top="400" bottom="400"/>%s</hp:tbl>') % (rid(), len(rows), n, sum(widths), total_h, ''.join(trs))
    run = '<hp:run charPrIDRef="7">%s<hp:t/></hp:run>' % t
    return ('<hp:p id="%s" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">%s</hp:p>' % (rid(), run)) if wrap else run

def grid(widths, head, rows, left=(), total=False):
    R = [[dict(t=h, head=True) for h in head]]
    for i, r in enumerate(rows):
        last = total and i == len(rows) - 1
        R.append([dict(t=x, left=(j in left), cpr=11 if last else None) for j, x in enumerate(r)])
    return table(widths, R)

def title(lines):
    box = table([W], [[dict(t=lines, bf=4, cpr=13)]], wrap=False).replace('zOrder="1"', 'zOrder="5"', 1)
    return FIRST + box + '</hp:p>'

def save(path, body, preview):
    xml = HEAD + body + '</hs:sec>'
    from xml.dom import minidom; minidom.parseString(xml.encode('utf-8'))  # 형식 확인
    with zipfile.ZipFile(path, 'w') as z:
        for i in src.infolist():
            if i.filename.startswith('BinData/'): continue
            d = src.read(i.filename)
            if i.filename == 'Contents/section0.xml': d = xml.encode('utf-8')
            if i.filename == 'Preview/PrvText.txt': d = preview.encode('utf-8')
            if i.filename == 'Contents/content.hpf': d = re.sub(rb'<opf:item [^>]*BinData/[^>]*/>', b'', d)
            ni = zipfile.ZipInfo(i.filename, i.date_time); ni.compress_type = i.compress_type; ni.create_system = i.create_system; ni.external_attr = i.external_attr
            z.writestr(ni, d)
    print('saved', path, len(xml))

# ---------------------------------------------------------------- 내용 (docx와 같음)
BUDGET, FARE, ROOM_P, ROOM_S, CUT_P, CUT_S = 700800, 9800 * 2, 147257, 87943, 20000, 13334
R = [('신주영 교수(제1호)', '1박 2일', 80000, 120000 - CUT_P, ROOM_P, FARE), ('문경민 연구원(제3호)', '1박 2일', 60000, 80000 - CUT_S, ROOM_S, FARE),
     ('김장호 교수(제1호)', '당일', 40000, 0, 0, FARE), ('황솔비 연구원(제3호)', '당일', 30000, 40000 - CUT_S, 0, FARE)]
z_ = lambda n: won(n) if n else '-'
tot = lambda i: sum(x[i] for x in R); TOTAL = sum(sum(x[2:]) for x in R)
brows = [[x[0], x[1], z_(x[2]), z_(x[3]), z_(x[4]), z_(x[5]), won(sum(x[2:]))] for x in R] + [['계', '4명', won(tot(2)), won(tot(3)), won(tot(4)), won(tot(5)), won(TOTAL)]]

plan = ''.join([
    title(['『댐 운영 의사결정 프레임워크 구축 자문 용역』', '한강수력본부 출장 계획(안)']),
    sec('출장 개요'),
    item('기간', "'26. 11. 25(수) ~ 11. 26(목) (1박 2일), 인공지능학과는 11. 26(목) 당일"),
    item('출장지', '한국수력원자력(주) 한강수력본부 (강원특별자치도 춘천시 신북읍 영서로)'),
    item('출장자', '(1박 2일) 신주영 교수, 문경민 연구원 / (당일) 김장호 교수, 황솔비 연구원 (4명)'),
    item('교통', '교수 2명은 자가용, 연구원 2명은 ITX-청춘(용산~춘천)'),
    item('목적', '용역 수행 결과 시연 및 발주처 실무 협의'),
    sec('세부 일정'),
    grid([9000, 9500, 29690], ['일자', '시간', '내    용'], [
        ['11. 25(수)', '○○:○○~', '(신주영 교수, 문경민) 서울 출발, 춘천 숙소 도착 및 시연 준비 점검'],
        ['11. 26(목)', '○○:○○~', '(김장호 교수, 황솔비) 서울 출발, 한강수력본부 도착'],
        ['', '○○:○○~○○:○○', '한강수력본부 시연 및 실무 협의'],
        ['', '○○:○○~', '춘천 출발, 서울 도착']], left=(2,)),
    sec('숙박'),
    item('숙소', '더잭슨나인스호텔 (춘천시 중앙로 193, 춘천역에서 차로 약 2분)'),
    item('선정 사유', '한강수력본부 주변에 숙박시설이 없어, 본부 방향(시내 북쪽)에 있고 주차가 되는 시내 호텔로 정함'),
    item('본부까지', '자가용 약 ○○분 (주소 기준 추정 약 20분, 지도 앱 확인 후 기재)'),
    item('주차', '객실당 1대 무료. 주차장이 좁아 만차 시 도보 2분 거리 야외 주차장 이용. 예약 시 주차 가능 상품 확인'),
    grid([10500, 11000, 8000, 18690], ['투숙자', '객실', '요금(1박)', '비고'], [
        ['신주영 교수', '○○○', won(ROOM_P), '조식 미포함, 상한 150,000원 이내'],
        ['문경민 연구원', '슈페리어 더블룸', won(ROOM_S), '조식 미포함, 11. 22까지 무료 취소, 상한 100,000원 이내']], left=(3,)),
    note('※ 요금은 예약 사이트 조회 기준, 세금·봉사료 포함'),
    sec('소요예산'),
    dot("국민대학교 여비규정 별표2 및 여비 업무 처리 지침('25. 11. 1. 시행) 기준, 단위: 원"),
    grid([12500, 5200, 5800, 6000, 6200, 5600, 6890], ['구분', '일정', '일비', '식비', '숙박비', '운임', '계'], brows, total=True),
    note('※ 계 %s원으로 용역 여비 예산 %s원을 %s원 초과. 초과분은 일비·식비에서 감액하여 예산만큼 청구' % (won(TOTAL), won(BUDGET), won(TOTAL - BUDGET))),
    note('※ 식비: 제공받는 점심 1식 감액(교수 20,000원, 연구원 13,334원, 지침 제12조 제1항)'),
    note('※ 당일 출장: 교원은 일비·운임만 지급, 대학원생은 4시간 이상 출장 시 식비 지급 가능(지침 제5조 제5항, 별표1)'),
    note('※ 운임: ITX-청춘 용산~춘천 일반실 9,800원 왕복. 자가용 이용 시에도 철도 운임으로 지급(지침 제5조 제4항), 연구원은 실제 탑승'),
    note('※ 숙박비: 실비, 본인 또는 본교 소속 동행자 명의 카드 영수증 제출(지침 제6조 제2항)'),
    sec('확인이 필요한 사항'),
    dot('한강수력본부의 점심 제공 여부 (제공받지 않으면 식비 감액 없음)'),
    dot('초과분을 일비·식비 감액으로 처리할 수 있는지 (산학협력단)'),
    dot('출발·회의 시간'),
])
save(OUT_PLAN, plan, '『댐 운영 의사결정 프레임워크 구축 자문 용역』\r\n한강수력본부 출장 계획(안)\r\n')

NAME = '「댐 운영 의사결정 프레임워크 구축 자문 용역」 수행 결과 시연 및 실무 협의'
DAY = '26.11.25.(수) ~ 26.11.26.(목)'; PLACE = '한국수력원자력(주) 한강수력본부'
C = [5500, 7500, 8500, 11500, 5500, 9690]
H = lambda t, **k: dict(t=t, head=True, **k); V = lambda t, **k: dict(t=t, left=True, **k)
form = ''.join([
    title(['출장계획서(국내)']), gap(),
    table(C, [
        [H('출장명'), V(NAME, cs=5)],
        [H('일  자'), V(DAY, cs=3), H('출장지'), V(PLACE + ' (강원특별자치도 춘천시)')],
        [H('출장자'), V('신주영, 문경민', cs=5)],
        [H(['출 장', '내 용'], rs=6), H('출장 목적'), V('용역 수행 결과 시연 및 발주처 실무 협의', cs=4)],
        [H('출장 일시'), V(DAY, cs=4)],
        [H('출장 일정', rs=2), V('26.11.25(수)'), V(['서울 출발 (11.25. ○○:○○)', '춘천 도착 (11.25. ○○:○○)', '시연 준비 점검', '숙박 (춘천시)'], cs=3)],
        [V('26.11.26(목)'), V(['한강수력본부 도착 (11.26. ○○:○○)', '용역 수행 결과 시연', '발주처 실무 협의', '춘천 출발 (11.26. ○○:○○)', '서울 도착 (11.26. ○○:○○)'], cs=3)],
        [H('장   소'), V(PLACE + ' (강원특별자치도 춘천시 신북읍 영서로)', cs=4)],
        [H('참 석 자'), V('신주영, 문경민, 김장호, 황솔비', cs=4)],
        [dict(t=['', '국내출장계획서를 상기와 같이 제출합니다.', '2026. 11. ○○.', '연구책임자 : 신 주 영   (인)', ''], cs=6, cpr=7)],
    ]),
])
save(OUT_FORM, form, '출장계획서(국내)\r\n')
