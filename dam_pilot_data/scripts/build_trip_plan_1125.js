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

// 여비: 국민대 여비규정 별표2 + 여비 업무 처리 지침(2025.11.01). 제1호 교수 일비 40,000 식비 60,000 숙박 상한 150,000 / 제3호 일비 30,000 식비 40,000 숙박 상한 100,000
// 1박 2일 2명 + 당일 2명. 수도권 외 당일 출장은 식비 없음(대학원생은 4시간 이상이면 지급 가능). 제공받는 점심 1식 감액(교수 20,000, 학생 13,334).
// 운임: ITX-청춘 용산~춘천 일반실 9,800원 왕복(교수는 자가운전, 학생은 실제 탑승). 용역 여비 예산 700,800원.
const BUDGET = 700800, FARE = 9800 * 2, ROOM_P = 148959, ROOM_S = 95784, CUT_P = 20000, CUT_S = 13334;
const R = [ // 구분, 일정, 일비, 식비, 숙박비, 운임
  ['신주영 교수(제1호)', '1박 2일', 40000 * 2, 60000 * 2 - CUT_P, ROOM_P, FARE],
  ['문경민 연구원(제3호)', '1박 2일', 30000 * 2, 40000 * 2 - CUT_S, ROOM_S, FARE],
  ['김장호 교수(제1호)', '당일', 40000, 0, 0, FARE],
  ['황솔희 연구원(제3호)', '당일', 30000, 40000 - CUT_S, 0, FARE],
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
    item('출장자', '(1박 2일) 신주영 교수, 문경민 연구원 / (당일) 김장호 교수, 황솔희 연구원 (4명)'),
    item('교통', '교수 2명은 자가용, 연구원 2명은 ITX-청춘(용산~춘천)'),
    item('목적', '용역 수행 결과 발표(시연 영상 포함) 및 발주처 실무 협의'),
    sec('세부 일정'),
    grid([2200, 1900, 5538], ['일자', '시간', '내    용'], [
      ['11. 25(수)', '○○:○○~', '(신주영 교수, 문경민) 서울 출발, 춘천 숙소 도착 및 발표 준비 점검'],
      ['11. 26(목)', '○○:○○~', '(김장호 교수, 황솔희) 서울 출발, 한강수력본부 도착'],
      ['', '○○:○○~○○:○○', '한강수력본부 수행 결과 발표(시연 영상 포함) 및 실무 협의'],
        ['', '○○:○○~○○:○○', '점심 식사'],
        ['', '○○:○○~○○:○○', '(그 밖에 예정된 회의·일정)'],
      ['', '○○:○○~', '춘천 출발, 서울 도착'],
    ], { left: [2] }),
    sec('숙박'),
    item('숙소', '춘천 호텔벤틀리 (춘천시 춘천로170번길 17)'),
    item('선정 사유', '한강수력본부 주변에 숙박시설이 없어, 주차가 되는 춘천 시내 호텔로 정함'),
    item('본부까지', '자가용 약 ○○분 (주소 기준 추정 약 20분, 지도 앱 확인 후 기재)'),
    item('주차', '건물 내 주차장(15대), 객실당 1대 무료. 만차 시 도보 5분 거리 공영주차장 이용'),
    grid([2400, 2500, 1700, 3038], ['투숙자', '객실', '요금(1박)', '비고'], [
      ['신주영 교수', '로얄 트리플', won(ROOM_P), '조식 미포함, 11. 22까지 무료 취소, 상한 150,000원 이내'],
      ['문경민 연구원', '로얄 디럭스 슈퍼룸', won(ROOM_S), '조식 미포함, 11. 18까지 무료 취소, 상한 100,000원 이내'],
    ], { left: [3] }),
    note('※ 요금은 예약 사이트 조회 기준, 세금·봉사료 포함'),
    sec('소요예산'),
    p('ㅇ 국민대학교 여비규정 별표2 및 여비 업무 처리 지침(\'25. 11. 1. 시행) 기준, 단위: 원', { indent: 400 }),
    grid([2300, 1150, 1150, 1200, 1250, 1100, 1488], ['구분', '일정', '일비', '식비', '숙박비', '운임', '계'], rows, { total: true }),
    p('※ 계 ' + won(TOTAL) + '원으로 용역 여비 예산 ' + won(BUDGET) + '원을 ' + won(TOTAL - BUDGET) + '원 초과. 초과분은 일비·식비에서 감액 처리하여 예산만큼 지급', { indent: 600, size: 20, before: 120 }),
    note('※ 식비: 제공받는 점심 1식 감액(교수 20,000원, 연구원 13,334원, 지침 제12조 제1항)'),
    note('※ 당일 출장: 교원은 일비·운임만 지급, 대학원생은 4시간 이상 출장 시 식비 지급 가능(지침 제5조 제5항, 별표1)'),
    note('※ 운임: ITX-청춘 용산~춘천 일반실 9,800원 왕복. 자가용 이용 시에도 철도 운임으로 지급(지침 제5조 제4항), 연구원은 실제 탑승'),
    note('※ 숙박비: 실비, 본인 또는 본교 소속 동행자 명의 카드 영수증 제출(지침 제6조 제2항)'),
    sec('확인이 필요한 사항'),
    dot('한강수력본부 도착 시간, 발표 시작 시간과 발표에 주어지는 시간 (발주처)'),
    dot('발표 외에 예정된 회의나 일정이 있는지 (발주처)'),
    dot('점심 식사 시간과 제공 여부 (발주처, 제공받지 않으면 식비 감액 없음)'),
    dot('위 일정에 맞춘 서울 출발 시간과 복귀 시간'),
  ] }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(process.argv[2], b); console.log('saved', process.argv[2], TOTAL); });
