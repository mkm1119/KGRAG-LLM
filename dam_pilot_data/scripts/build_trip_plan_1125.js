// 한강수력본부 출장 계획(안) docx. 양식은 11/13 실무회의 계획(안)과 같다.
// 여비: 국민대 여비규정(2024.03.14) 별표2 국내 여비 정액표. 1안 1박2일, 2안 2박3일(11/10 교수님 면담에서는 2박3일로 계획).
// 사용: node build_trip_plan_1125.js <출력.docx>
const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, AlignmentType,
  BorderStyle, ShadingType, VerticalAlign } = require('docx');

const FONT = '맑은 고딕';
const W = 9638;
const r = (t, o = {}) => new TextRun({ text: t, font: FONT, size: o.size || 22, bold: o.bold, color: o.color });
const p = (t, o = {}) => new Paragraph({ alignment: o.align, spacing: { before: o.before ?? 60, after: o.after ?? 60, line: 320 },
  indent: o.indent ? { left: o.indent, hanging: o.hanging || 0 } : undefined, children: Array.isArray(t) ? t : [r(t, o)] });
const B = { style: BorderStyle.SINGLE, size: 6, color: '000000' };
const NB = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const all = b => ({ top: b, bottom: b, left: b, right: b });
const cell = (kids, w, o = {}) => new TableCell({ width: { size: w, type: WidthType.DXA }, borders: o.borders || all(B),
  shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill, color: 'auto' } : undefined, verticalAlign: VerticalAlign.CENTER,
  margins: { top: 80, bottom: 80, left: 120, right: 120 }, columnSpan: o.span, children: kids });
const box = (kids, o = {}) => new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: [W], rows: [new TableRow({ children: [cell(kids, W, o)] })] });
const sec = t => p([r('□ ', { bold: true, size: 26 }), r(t, { bold: true, size: 26 })], { before: 240, after: 80 });
const item = (k, v) => p([r('ㅇ '), r('(' + k + ') ', { bold: true }), r(v)], { indent: 400 });
const ctr = (t, o) => p(t, { align: AlignmentType.CENTER, size: 20, before: 0, after: 0, ...o });
const grid = (widths, head, rows, o = {}) => new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: widths, rows: [
  new TableRow({ tableHeader: true, children: head.map((t, i) => cell([ctr(t, { bold: true })], widths[i], { fill: 'D9D9D9' })) }),
  ...rows.map((x, ri) => new TableRow({ children: x.map((t, i) => cell([(o.left || []).includes(i) ? p(t, { size: 20, before: 0, after: 0 }) : ctr(t, ri === rows.length - 1 && o.total ? { bold: true } : {})], widths[i],
    ri === rows.length - 1 && o.total ? { fill: 'F2F2F2' } : {})) })),
] });
const won = n => n.toLocaleString('en-US');

const title = box([
  p('『댐 운영 의사결정 프레임워크 구축 자문 용역』', { bold: true, size: 30, align: AlignmentType.CENTER, before: 120 }),
  p('한강수력본부 출장 계획(안)', { bold: true, size: 30, align: AlignmentType.CENTER, after: 120 }),
], { borders: { top: { style: BorderStyle.DOUBLE, size: 6, color: '000000' }, bottom: { style: BorderStyle.DOUBLE, size: 6, color: '000000' }, left: NB, right: NB } });

// 여비 (별표2): 제1호 교수 일비 40,000 식비 60,000 숙박 실비 상한 150,000 / 제3호 연구원·대학원생 일비 30,000 식비 40,000 숙박 상한 100,000
// 1박 2일 2명(교수, 연구원) + 당일 2명(인공지능학과 교수, 연구원). 교원 당일 출장은 식비 제외(산학협력단 정산 기준).
// 숙박: 더잭슨나인스호텔 슈페리어 더블룸(예약 사이트 2026-11-16 조회). 운임: ITX-청춘 용산~춘천 일반실 9,800원 왕복. 용역 여비 예산 700,800원.
const BUDGET = 700800, FARE = 9800 * 2, ROOM_P = 135000, ROOM_S = 87943;
const R = [ // 구분, 일정, 일비, 식비, 숙박비, 운임
  ['신주영 교수(제1호)', '1박 2일', 40000 * 2, 60000 * 2, ROOM_P, FARE],
  ['문경민 연구원(제3호)', '1박 2일', 30000 * 2, 40000 * 2, ROOM_S, 0],
  ['김장호 교수(제1호)', '당일', 40000, 0, 0, FARE],
  ['○○○ 연구원(제3호)', '당일', 30000, 40000, 0, 0],
];
const tot = i => R.reduce((u, x) => u + x[i], 0);
const z = n => n ? won(n) : '-';
const rs = x => x[2] + x[3] + x[4] + x[5];
const TOTAL = R.reduce((u, x) => u + rs(x), 0);
const rows = [...R.map(x => [x[0], x[1], z(x[2]), z(x[3]), z(x[4]), z(x[5]), won(rs(x))]),
  ['계', '4명', won(tot(2)), won(tot(3)), won(tot(4)), won(tot(5)), won(TOTAL)]];
const note = t => p(t, { indent: 600, size: 20 });
const dot = t => p('ㅇ ' + t, { indent: 400 });

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 22 } } } },
  sections: [{ properties: { page: { margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } }, children: [
    title,
    sec('출장 개요'),
    item('기간', "'26. 11. 25(수) ~ 11. 26(목) (1박 2일), 인공지능학과는 11. 26(목) 당일"),
    item('출장지', '한국수력원자력(주) 한강수력본부 (강원특별자치도 춘천시 신북읍 영서로)'),
    item('출장자', '(1박 2일) 신주영 교수, 문경민 연구원 / (당일) 김장호 교수, ○○○ 연구원 (4명)'),
    item('교통', '자가용 (연구실별 교수 차량)'),
    item('목적', '용역 수행 결과 시연 및 발주처 실무 협의'),
    sec('세부 일정'),
    grid([2200, 1900, 5538], ['일자', '시간', '내    용'], [
      ['11. 25(수)', '○○:○○~', '(신주영 교수, 문경민) 국민대학교 출발, 춘천 숙소 도착 및 시연 준비 점검'],
      ['11. 26(목)', '○○:○○~', '(김장호 교수, ○○○) 국민대학교 출발, 한강수력본부 도착'],
      ['', '○○:○○~○○:○○', '한강수력본부 시연 및 실무 협의'],
      ['', '○○:○○~', '춘천 출발, 국민대학교 도착'],
    ], { left: [2] }),
    sec('숙박'),
    item('숙소', '더잭슨나인스호텔 (춘천시 중앙로 193, 춘천역에서 차로 약 2분)'),
    item('선정 사유', '한강수력본부 주변에 숙박시설이 없어, 본부 방향(시내 북쪽)에 있고 주차가 되는 시내 호텔로 정함'),
    item('본부까지', '자가용 약 ○○분 (주소 기준 추정 약 20분, 지도 앱 확인 후 기재)'),
    item('주차', '객실당 1대 무료. 주차장이 좁아 만차 시 도보 2분 거리 야외 주차장 이용. 예약 시 주차 가능 상품 확인'),
    grid([2400, 2500, 1700, 3038], ['투숙자', '객실', '요금(1박)', '비고'], [
      ['신주영 교수', '슈페리어 더블룸', won(ROOM_P), '조식 포함, 11. 22까지 무료 취소, 상한 150,000원 이내'],
      ['문경민 연구원', '슈페리어 더블룸', won(ROOM_S), '11. 22까지 무료 취소, 상한 100,000원 이내'],
    ], { left: [3] }),
    note('※ 요금은 예약 사이트 조회 기준(\'26. 11. 16), 세금·봉사료 포함'),
    sec('소요예산'),
    p('ㅇ 국민대학교 여비규정 별표2(국내 여비 정액표) 기준, 단위: 원', { indent: 400 }),
    grid([2350, 950, 1200, 1250, 1250, 1150, 1488], ['구분', '일정', '일비', '식비', '숙박비', '운임', '계'], rows, { total: true }),
    p('※ 계 ' + won(TOTAL) + '원으로 용역 여비 예산 ' + won(BUDGET) + '원을 ' + won(TOTAL - BUDGET) + '원 초과. 초과분은 일비·식비에서 감액하여 예산만큼 청구', { indent: 600, size: 20, before: 120 }),
    note('※ 일비·식비는 정액, 숙박비는 실비. 교원의 당일 출장은 식비 제외'),
    note('※ 운임은 자가운전 교원에게 철도 운임 지급(여비규정 제17조 제3항). ITX-청춘 용산~춘천 일반실 9,800원 왕복 기준'),
    sec('확인이 필요한 사항'),
    dot('조식 포함 객실의 숙박비를 그대로 인정하는지, 식비가 감액되는지 (산학협력단)'),
    dot('초과분을 일비·식비 감액으로 처리할 수 있는지 (산학협력단)'),
    dot('인공지능학과 참석 연구원, 출발·회의 시간'),
  ] }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(process.argv[2], b); console.log('saved', process.argv[2], TOTAL); });
