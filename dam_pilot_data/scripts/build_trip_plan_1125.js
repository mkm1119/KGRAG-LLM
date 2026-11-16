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
// 출장자 2명(제1호 1명, 제3호 1명). 1안 1박2일, 2안 2박3일. 용역 여비 예산 700,800원.
const BUDGET = 700800;
const calc = (D, N) => { const a = [40000 * D, 60000 * D, 150000 * N], b = [30000 * D, 40000 * D, 100000 * N]; const s = x => x.reduce((u, v) => u + v, 0);
  return { rows: [['교수(제1호)', '1', won(a[0]), won(a[1]), won(a[2]), won(s(a))], ['연구원(제3호)', '1', won(b[0]), won(b[1]), won(b[2]), won(s(b))],
    ['계', '2', won(a[0] + b[0]), won(a[1] + b[1]), won(a[2] + b[2]), won(s(a) + s(b))]], fixed: a[0] + a[1] + b[0] + b[1], lodge: a[2] + b[2], total: s(a) + s(b) }; };
const P1 = calc(2, 1), P2 = calc(3, 2);
const BW = [1900, 700, 1650, 1650, 2088, 1650];
const note = t => p(t, { indent: 600, size: 20 });

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 22 } } } },
  sections: [{ properties: { page: { margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } }, children: [
    title,
    sec('출장 개요'),
    item('기간', "(1안) '26. 11. 25(수) ~ 11. 26(목) (1박 2일) / (2안) '26. 11. 25(수) ~ 11. 27(금) (2박 3일)"),
    item('출장지', '한국수력원자력(주) 한강수력본부 (강원특별자치도 춘천시 신북읍)'),
    item('출장자', '신주영 교수, 문경민 연구원 (2명)'),
    item('교통', '자가용 (신주영 교수 차량)'),
    item('숙박', '춘천 시내 ○○○ (출장지 주변에 숙박시설이 없어 시내에서 숙박)'),
    sec('출장 목적'),
    p('ㅇ 용역 수행 결과 시연 및 발주처 실무 협의', { indent: 400 }),
    sec('세부 일정'),
    p('ㅇ (1안) 1박 2일', { indent: 400, bold: true }),
    grid([2200, 1900, 5538], ['일자', '시간', '내    용'], [
      ['11. 25(수)', '○○:○○~', '국민대학교 출발, 춘천 숙소 도착 및 시연 준비 점검'],
      ['11. 26(목)', '○○:○○~○○:○○', '한강수력본부 시연 및 실무 협의'],
      ['', '○○:○○~', '춘천 출발, 국민대학교 도착'],
    ], { left: [2] }),
    p('ㅇ (2안) 2박 3일', { indent: 400, bold: true, before: 200 }),
    grid([2200, 1900, 5538], ['일자', '시간', '내    용'], [
      ['11. 25(수)', '○○:○○~', '국민대학교 출발, 춘천 숙소 도착 및 시연 준비 점검'],
      ['11. 26(목)', '○○:○○~○○:○○', '한강수력본부 시연 및 실무 협의'],
      ['11. 27(금)', '○○:○○~○○:○○', '(업무 내용 기재)'],
      ['', '○○:○○~', '춘천 출발, 국민대학교 도착'],
    ], { left: [2] }),
    sec('소요예산'),
    p('ㅇ 국민대학교 여비규정 별표2(국내 여비 정액표) 기준, 단위: 원', { indent: 400 }),
    p('ㅇ (1안) 1박 2일', { indent: 400, bold: true }),
    grid(BW, ['구분', '인원', '일비(2일)', '식비(2일)', '숙박비(1박, 상한)', '계'], P1.rows, { total: true }),
    note('※ 운임: 교수 1명 철도 운임(서울~춘천 왕복) ○○,○○○원 별도'),
    note('※ 운임 제외 ' + won(P1.total) + '원(숙박비 상한 기준)으로 예산 ' + won(BUDGET) + '원 대비 ' + won(BUDGET - P1.total) + '원 여유'),
    p('ㅇ (2안) 2박 3일', { indent: 400, bold: true, before: 200 }),
    grid(BW, ['구분', '인원', '일비(3일)', '식비(3일)', '숙박비(2박, 상한)', '계'], P2.rows, { total: true }),
    note('※ 운임: 교수 1명 철도 운임(서울~춘천 왕복) ○○,○○○원 별도'),
    note('※ 운임 제외 ' + won(P2.total) + '원(숙박비 상한 기준)으로 예산 ' + won(BUDGET) + '원을 ' + won(P2.total - BUDGET) + '원 초과'),
    note('※ 일비·식비 ' + won(P2.fixed) + '원을 뺀 ' + won(BUDGET - P2.fixed) + '원 이내에서 숙박비(2박)와 운임을 집행해야 예산에 맞음'),
    p('※ 일비·식비는 정액, 숙박비는 실비(1박 상한 교수 150,000원, 연구원 100,000원)', { indent: 600, size: 20, before: 160 }),
    note('※ 자가운전 운임은 운전한 교직원에게 철도 운임 또는 우등고속 정액으로 지급(여비규정 제17조 제3항), 통행료 내역 등으로 증빙'),
    note('※ 집행은 용역 여비 예산 ' + won(BUDGET) + '원 이내'),
  ] }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(process.argv[2], b); console.log('saved', process.argv[2]); });
