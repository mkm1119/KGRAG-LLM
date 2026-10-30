#!/usr/bin/env python3
"""랩미팅 자료용 통일 그림(HTML) 생성: 단위마다 같은 틀의 '과정 ①~⑤' 그림과 '결과(CSV 3개 → Entity)' 그림, 끝난 상태 그림.
출력: lab_meeting/how/fig/unified/unified_figs.html (PNG는 playwright로 따로 찍는다)"""
import html, os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'lab_meeting', 'how', 'fig', 'unified', 'unified_figs.html')
e = html.escape

CSS = '''
:root{--key:#E07A2F;--cls:#23907F;--line:#C9C9C9}
*{box-sizing:border-box}
body{margin:0;background:#fff;color:#222;font-family:"WenQuanYi Zen Hei",sans-serif;font-size:15px;line-height:1.45}
.fig{width:840px;padding:14px 16px;margin:0 0 30px;background:#fff}
.cap{font-size:14.5px;font-weight:bold;margin:0 0 6px}
.cap span{font-weight:normal;color:#666}
.pg{display:grid;grid-template-columns:66px 200px 24px 250px 24px minmax(0,1fr);align-items:stretch;gap:8px 0}
.pg .h{font-size:13px;color:#666;font-weight:bold;align-self:end}
.pg .n{display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:13.5px;background:#1F4E79;color:#fff;border-radius:7px;text-align:center;line-height:1.25;padding:4px}
.pg .k{border:1.5px solid var(--line);border-radius:7px;padding:6px 8px;background:#fff;font-size:13.5px;word-break:break-all}
.pg .q{border-radius:7px;padding:6px 8px;background:#EFEFEB;font-size:13.5px}
.pg .r{border-radius:7px;padding:6px 8px;background:#EEF6EA;border:1.5px solid #B9D8AE;font-size:13.5px;word-break:break-all}
.pg .ar{display:flex;align-items:center;justify-content:center;color:#555;font-size:17px}
.pr{display:block;margin-top:3px;font-size:12px;color:#8A6A00}
.mono{font-family:"DejaVu Sans Mono",monospace;font-size:12.5px}
.k b,.r b{color:#111}
.g6{display:grid;grid-template-columns:500px 30px minmax(0,1fr);gap:8px 0;align-items:center}
.mt{border-collapse:collapse;font-size:12.5px;width:100%}
.mt th,.mt td{border:1px solid var(--line);padding:2px 5px;text-align:left;word-break:break-all}
.mt th{background:#666;color:#fff;font-weight:bold}
.mt td:first-child,.mt th:first-child,.mt td:last-child,.mt th:last-child{white-space:nowrap;word-break:normal}
.mt td:nth-child(2){word-break:normal}
.c6{font-size:13px;font-weight:bold;margin:0 0 2px}
.c6 span{font-weight:normal;color:#666}
.card{border:2.5px solid #23907F;border-radius:12px;background:#E8F5F2;padding:9px 11px;font-size:13.5px;word-break:break-all}
.card .t{font-size:17px;font-weight:bold}
.tag{display:inline-block;border-radius:5px;padding:1px 8px;color:#fff;font-weight:bold;font-size:12.5px}
.note{color:#555;font-size:13.5px}
.ar2{text-align:center;color:#555;font-size:20px}
'''


def proc(fid, cap, rows):
    """rows: (번호이름, 입력, 규칙, 결과, 원리 or '')"""
    h = ['<div class="fig" id="%s"><div class="cap">%s</div><div class="pg">' % (fid, cap),
         '<div></div><div class="h">입력</div><div></div><div class="h">규칙</div><div></div><div class="h">결과</div>']
    for n, k, q, r, pr in rows:
        h.append('<div class="n">%s</div><div class="k">%s</div><div class="ar">→</div><div class="q">%s%s</div><div class="ar">→</div><div class="r">%s</div>'
                 % (n, k, q, ('<span class="pr">%s</span>' % pr) if pr else '', r))
    h.append('</div></div>')
    return ''.join(h)


def tbl(head, rows):
    return '<table class="mt"><tr>%s</tr>%s</table>' % (''.join('<th>%s</th>' % e(x) for x in head),
                                                          ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % e(c) for c in r) for r in rows))


def result(fid, ents, props, provs, cards, color='#23907F'):
    left = ('<div class="c6">kgv4_entities.csv <span>한 줄 = Entity 하나</span></div>' + tbl(['Entity ID', 'Class'], ents) +
            '<div class="c6" style="margin-top:7px">kgv4_properties.csv <span>한 줄 = 속성 하나</span></div>' + tbl(['Entity ID', '속성', '값', '자료형'], props) +
            '<div class="c6" style="margin-top:7px">kgv4_provenance.csv <span>한 줄 = 출처 하나</span></div>' + tbl(['Entity ID', '원본 파일', '위치', '규칙', '값의 성격'], provs))
    right = ''.join(cards)
    return '<div class="fig" id="%s"><div class="g6"><div>%s</div><div class="ar2">⟹</div><div>%s</div></div></div>' % (fid, left, right)


def card(eid, cls, lines, src=None, color='#23907F', bg='#E8F5F2'):
    return ('<div class="card" style="border-color:%s;background:%s;margin-bottom:8px"><div class="t">%s <span class="tag" style="background:%s">%s</span></div>%s%s</div>'
            % (color, bg, e(eid), color, e(cls), ''.join('<div>%s</div>' % x for x in lines),
               ('<div style="margin-top:5px;border-top:1px dashed #9cc;padding-top:4px;font-size:12.5px;color:#444">출처: %s</div>' % e(src)) if src else ''))


F = []
# ---------------- 승인
F.append(proc('P_APR', '승인 표 504행 → Approval과 EvidenceSource', [
    ('① 식별자', '순차번호 = <b>504</b>', '틀 <span class="mono">"APR:"+{순차번호}</span>, 같은 행에서 <span class="mono">"EVI:AP:"+{순차번호}</span>', '<b>APR:504</b>, <b>EVI:AP:504</b><br><span class="note">80행 → 서로 다른 ID 80쌍</span>', '원리 1 · uriPattern'),
    ('② Class', '승인 표의 행', '이 표에서 만든 APR: ID는 모두 Approval, EVI:AP: ID는 모두 EvidenceSource', 'APR:504 → Approval<br>EVI:AP:504 → EvidenceSource', '원리 2 · d2rq:class'),
    ('③ 속성', '승인년월일시분 = 2011-06-27<br>방류시작시간 = 2011-06-27 18:00<br>접수방류량 = 2000<br>비고 = (실제방류는 20시부터)', '열 하나 → 속성 하나(날짜로). 세 열은 글자 틀 "방류시작 {}; 접수방류량 {}㎥/s; 비고: {}"에 넣어 하나로', 'approvalTime = 2011-06-27 (날짜)<br>approvalContent = "방류시작 2011-06-27 18:00; 접수방류량 2000㎥/s; 비고: (실제방류는 20시부터)" (글자)', '원리 3 · column / pattern'),
    ('④ 근거 연결', '출처 열: 기관, 파일명 …', '출처 열을 근거 Entity의 속성으로. 같은 행에서 동시에 만든 두 Entity를 그 자리에서 잇는다', 'EVI:AP:504: sourceTitle, sourceType = 승인자료, sourceLocator = 순차번호 504<br><b>APR:504 —supportedBy→ EVI:AP:504</b>', ''),
    ('⑤ 출처 기록', '원본 행 번호 = 504', '어느 파일의 어느 행을, 어떤 규칙으로 옮겼는지', 'approval_records_clean.csv · 504번째 행 · MR-APR · 원본 그대로', ''),
]))
F.append(result('R_APR', [['APR:504', 'Approval'], ['EVI:AP:504', 'EvidenceSource']],
                [['APR:504', 'approvalTime', '2011-06-27', '날짜'], ['APR:504', 'approvalContent', '방류시작 2011-06-27 18:00; 접수방류량 2000㎥/s; 비고: (실제방류는 20시부터)', '글자'],
                 ['EVI:AP:504', 'sourceType', '승인자료', '글자'], ['EVI:AP:504', 'sourceLocator', '순차번호 504', '글자']],
                [['APR:504', 'approval_records_clean.csv', '504번째 행', 'MR-APR', '원본 그대로']],
                [card('APR:504', 'Approval', ['approvalTime = 2011-06-27', 'approvalContent = "방류시작 2011-06-27 18:00; 접수방류량 2000㎥/s; 비고: (실제방류는 20시부터)"', '<b>→ supportedBy EVI:AP:504</b>'], 'approval_records_clean.csv 504번째 행'),
                 card('EVI:AP:504', 'EvidenceSource', ['sourceTitle = 환경부 한강홍수통제소 홍수예보 댐방류승인', 'sourceType = 승인자료', 'sourceLocator = 순차번호 504'], None, '#7A7A7A', '#F2F2F2')]))
# ---------------- 댐
F.append(proc('P_DAM', 'K-water 일자료의 충주댐 행 → Dam', [
    ('① 식별자', 'DAM_CD = <b>1003110</b><br><span class="note">충주댐 12,582행 모두 같은 값</span>', '틀 <span class="mono">"DAM:"+{DAM_CD}</span>. 같은 코드의 행은 같은 ID로 모인다', '<b>DAM:1003110</b> 하나', '원리 1 · uriPattern'),
    ('② Class', '댐 자료의 행', '이 자료에서 만든 DAM: ID는 모두 Dam', 'DAM:1003110 → Dam', '원리 2 · d2rq:class'),
    ('③ 속성', '댐 유형 = 다목적댐<br>댐 이름 = 충주댐', '댐 유형 열 → damType. 이름은 승인 자료의 "충주"와 맞춘 표준 댐명', 'damType = 다목적댐 (글자)<br>damName = 충주댐 (글자)', '원리 3 · column'),
    ('④ 근거 연결', '—', '온톨로지에서 supportedBy는 상태·운영행위·승인·기준에만 정의되어 있다', '근거 Entity 없음 (출처 기록만 남김)', ''),
    ('⑤ 출처 기록', 'DAM_CD = 1003110', '어느 파일의 어느 행을, 어떤 규칙으로 옮겼는지', 'kwater_mywater_period_daily_long.csv.gz · DAM_CD=1003110 · MR-DAM · 원본 그대로', ''),
]))
F.append(result('R_DAM', [['DAM:1003110', 'Dam']],
                [['DAM:1003110', 'damName', '충주댐', '글자'], ['DAM:1003110', 'damType', '다목적댐', '글자']],
                [['DAM:1003110', 'kwater_mywater_period_daily_long.csv.gz', 'DAM_CD=1003110', 'MR-DAM', '원본 그대로']],
                [card('DAM:1003110', 'Dam', ['damName = 충주댐', 'damType = 다목적댐'], 'K-water 일자료 DAM_CD=1003110', '#E07A2F', '#FFF4EA')]))
# ---------------- HMS
F.append(proc('P_HMS', 'K-water 시간자료의 충주댐 수위 열 → HydrometeorologicalState', [
    ('① 식별자', 'DAM_CD = <b>1003110</b><br>열 머리 = <b>수위</b>', '틀 <span class="mono">"HMS:"+{DAM_CD}+":"+{변수}</span>. 키가 키 열과 열 머리 두 곳에 있음', '<b>HMS:1003110:수위</b><br><span class="note">댐 4 × 변수 6 = 24개</span>', '원리 1 응용 · 넓은 표'),
    ('② Class', '시간자료의 (댐, 변수)', '이 자료에서 만든 HMS: ID는 모두 HydrometeorologicalState', 'HMS:1003110:수위 → HydrometeorologicalState', '원리 2'),
    ('③ 속성', '열 머리 = 수위<br>DAM_CD = 1003110', '변수명 → variableType, 댐 코드 → stationCode. 시각별 값은 KG에 넣지 않음', 'variableType = 수위<br>stationCode = 1003110<br><span class="note">값(131.55 …)은 측정 저장소</span>', '원리 3'),
    ('④ 근거 연결', '같은 자료(댐별 시간자료)', '댐마다 근거 Entity <span class="mono">"EVI:KW:"+{DAM_CD}</span>를 만들고 잇는다', 'EVI:KW:1003110: sourceType = 측정자료<br><b>HMS:1003110:수위 —supportedBy→ EVI:KW:1003110</b>', ''),
    ('⑤ 출처 기록', '값이 들어 있는 열', '위치에 열 이름을 남긴다', 'kwater_mywater_hydr_H_wide.csv.gz · DATA1_수위(EL.m) · MR-HMS · 원본 그대로', ''),
]))
F.append(result('R_HMS', [['HMS:1003110:수위', 'HydrometeorologicalState'], ['EVI:KW:1003110', 'EvidenceSource']],
                [['HMS:1003110:수위', 'variableType', '수위', '글자'], ['HMS:1003110:수위', 'stationCode', '1003110', '글자'], ['EVI:KW:1003110', 'sourceType', '측정자료', '글자'],
                 ['EVI:KW:1003110', 'sourceLocator', 'DAM_CD=1003110 충주댐 시간별 자료', '글자']],
                [['HMS:1003110:수위', 'kwater_mywater_hydr_H_wide.csv.gz', 'DATA1_수위(EL.m)', 'MR-HMS', '원본 그대로']],
                [card('HMS:1003110:수위', 'HydrometeorologicalState', ['variableType = 수위', 'stationCode = 1003110', '<b>→ supportedBy EVI:KW:1003110</b>'], 'K-water 시간자료 열 DATA1_수위(EL.m)', '#2F66D0', '#EEF2FB'),
                 card('EVI:KW:1003110', 'EvidenceSource', ['sourceTitle = K-water MyWater 수문 시간자료', 'sourceType = 측정자료'], None, '#7A7A7A', '#F2F2F2')]))
# ---------------- 운영행위
F.append(proc('P_OPR', '중간 파일 operation_from_remarks_5dams.csv의 504행 줄 → Operation', [
    ('① 식별자', '순차번호 = <b>504</b><br>이 비고의 몇 번째 행위 = <b>1</b>', '틀 <span class="mono">"OPR:"+{순차번호}+":"+{순번}</span>', '<b>OPR:504:1</b><br><span class="note">2754 → OPR:2754:1, OPR:2754:2</span>', ''),
    ('② Class', '비고에서 뽑은 행위', '모두 Operation', 'OPR:504:1 → Operation', ''),
    ('③ 속성', 'operationType = 방류<br>operationTime = 2011-06-27 20:00', '행위 유형은 글자, 시각은 일시로', 'operationType = 방류 (글자)<br>operationTime = 2011-06-27T20:00 (일시)', ''),
    ('④ 근거 연결', '비고가 적힌 행 = 504', '그 행의 근거 Entity에 잇는다 (순차번호로 바로 정해짐)', '<b>OPR:504:1 —supportedBy→ EVI:AP:504</b>', ''),
    ('⑤ 출처 기록', 'rule = 실제 방류 시각 문구', '어느 파일의 어느 줄을, 어떤 규칙으로 만들었는지', 'operation_from_remarks_5dams.csv · 순차번호=504 · 규칙 "실제 방류 시각 문구" · 비고에서 분류', ''),
]))
F.append(result('R_OPR', [['OPR:504:1', 'Operation']],
                [['OPR:504:1', 'operationType', '방류', '글자'], ['OPR:504:1', 'operationTime', '2011-06-27T20:00', '일시']],
                [['OPR:504:1', 'operation_from_remarks_5dams.csv', '순차번호=504', '실제 방류 시각 문구', '비고에서 분류']],
                [card('OPR:504:1', 'Operation', ['operationType = 방류', 'operationTime = 2011-06-27T20:00', '<b>→ supportedBy EVI:AP:504</b>'], '승인 504행의 비고에서 분류', '#8A55C2', '#F3ECFA')]))
# ---------------- 기준
F.append(proc('P_CRI', '중간 파일 criterion_list.csv의 CR-02 줄 → Criterion', [
    ('① 식별자', '번호 = <b>CR-02</b><br><span class="note">별표3 한강수계 댐 순서로 붙인 연구용 번호</span>', '틀 <span class="mono">"CRI:"+{번호}</span>', '<b>CRI:CR-02</b>', ''),
    ('② Class', '별표3에서 뽑은 기준', '모두 Criterion', 'CRI:CR-02 → Criterion', ''),
    ('③ 속성', '제한수위 칸 = \'138.0\'<br>단위 = EL.m', '칸 원문을 숫자로 읽음 (숫자뿐인 칸만)', 'criterionType = 홍수기 제한수위<br>criterionValue = 138.0 (숫자)<br>unit = EL.m', ''),
    ('④ 근거 연결', '규정 XML의 별표3', '규정 하나에 근거 Entity 하나, 고정 ID <span class="mono">"EVI:LAW:별표3"</span>', 'EVI:LAW:별표3: sourceType = 규정, sourceLocator = 별표 3<br><b>CRI:CR-02 —supportedBy→ EVI:LAW:별표3</b>', ''),
    ('⑤ 출처 기록', 'CR-02 줄', '어느 파일의 어느 줄을, 어떤 규칙으로 옮겼는지', 'criterion_list.csv · CR-02 · MR-CRI · 원본 그대로', ''),
]))
F.append(result('R_CRI', [['CRI:CR-02', 'Criterion'], ['EVI:LAW:별표3', 'EvidenceSource']],
                [['CRI:CR-02', 'criterionType', '홍수기 제한수위', '글자'], ['CRI:CR-02', 'criterionValue', '138.0', '숫자'], ['CRI:CR-02', 'unit', 'EL.m', '글자'],
                 ['EVI:LAW:별표3', 'sourceLocator', '별표 3', '글자']],
                [['CRI:CR-02', 'criterion_list.csv', 'CR-02', 'MR-CRI', '원본 그대로']],
                [card('CRI:CR-02', 'Criterion', ['criterionType = 홍수기 제한수위', 'criterionValue = 138.0', 'unit = EL.m', '<b>→ supportedBy EVI:LAW:별표3</b>'], 'criterion_list.csv CR-02', '#C77A1E', '#FDF3E3'),
                 card('EVI:LAW:별표3', 'EvidenceSource', ['sourceTitle = 댐과 보 등의 연계운영규정 (훈령 제42호, 2026-07-08 시행)', 'sourceType = 규정', 'sourceLocator = 별표 3 (문서 저장소 조회 키)'], None, '#7A7A7A', '#F2F2F2')]))
# ---------------- 비정형 추출이 끝난 상태
G = '''<div class="fig" id="S4">
 <style>.grp{border:1.5px dashed #BBB;border-radius:10px;padding:7px 9px;background:#FBFBF8}.grp .gt{font-size:13px;color:#555;font-weight:bold;margin-bottom:5px}
 .nd{display:inline-block;border-radius:7px;padding:3px 8px;margin:2px 0;font-size:13px;border:2px solid}.lk{font-size:12px;color:#444;margin:0 4px}</style>
 <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
  <div class="grp"><div class="gt">승인 표에서 (구조화 자료 매핑)</div>
   <span class="nd" style="border-color:#23907F;background:#E8F5F2">APR:504</span><span class="lk">—supportedBy→</span><span class="nd" style="border-color:#7A7A7A;background:#F2F2F2">EVI:AP:504</span>
   <div class="note" style="font-size:12.5px">충주댐 승인 15개, 각각 근거 EVI:AP</div></div>
  <div class="grp" style="border-color:#8A55C2"><div class="gt" style="color:#5E3A8E">비고에서 (비정형 텍스트 추출) — 새로 더해짐</div>
   <span class="nd" style="border-color:#8A55C2;background:#F3ECFA">OPR:504:1</span><span class="lk">—supportedBy→</span><span class="nd" style="border-color:#7A7A7A;background:#F2F2F2">EVI:AP:504</span>
   <div class="note" style="font-size:12.5px">충주댐 운영행위 14개 (13개 승인에서)</div></div>
  <div class="grp"><div class="gt">K-water 일자료 (구조화 자료 매핑)</div>
   <span class="nd" style="border-color:#E07A2F;background:#FFF4EA">DAM:1003110</span> <span class="note" style="font-size:12.5px">충주댐 · 다목적댐</span></div>
  <div class="grp" style="border-color:#C77A1E"><div class="gt" style="color:#8A5A10">별표3에서 (비정형 텍스트 추출) — 새로 더해짐</div>
   <span class="nd" style="border-color:#C77A1E;background:#FDF3E3">CRI:CR-02</span><span class="lk">—supportedBy→</span><span class="nd" style="border-color:#7A7A7A;background:#F2F2F2">EVI:LAW:별표3</span>
   <div class="note" style="font-size:12.5px">홍수기 제한수위 138.0 EL.m</div></div>
  <div class="grp" style="grid-column:span 2"><div class="gt">K-water 시간자료 (구조화 자료 매핑)</div>
   <span class="nd" style="border-color:#2F66D0;background:#EEF2FB">HMS:1003110:수위</span> <span class="nd" style="border-color:#2F66D0;background:#EEF2FB">…:저수량</span> <span class="nd" style="border-color:#2F66D0;background:#EEF2FB">…:강우량</span> <span class="nd" style="border-color:#2F66D0;background:#EEF2FB">…:유입량</span> <span class="nd" style="border-color:#2F66D0;background:#EEF2FB">…:총방류량</span> <span class="nd" style="border-color:#2F66D0;background:#EEF2FB">…:저수율</span>
   <span class="lk">—supportedBy→</span><span class="nd" style="border-color:#7A7A7A;background:#F2F2F2">EVI:KW:1003110</span></div>
 </div>
 <div class="note" style="margin-top:8px">각 자료에서 Entity와 속성이 모두 만들어졌고, 같은 행·같은 자료에서 함께 만든 근거만 이어져 있다. 승인 ↔ 댐, 운영행위 ↔ 댐, 승인 ↔ 운영행위, 기준 ↔ 댐, 댐 ↔ 측정 상태는 아직 이어지지 않았다.</div>
</div>'''
F.append(G)
open(OUT, 'w', encoding='utf-8').write('<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>통일 그림</title><style>%s</style></head><body>%s</body></html>' % (CSS, '\n'.join(F)))
print('wrote', OUT)
