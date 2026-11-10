// 한강수력본부 출장 계획(안) docx. 양식은 11/13 실무회의 계획(안)과 같다.
// 여비: 국민대 여비규정(2024.03.14) 별표2 국내 여비 정액표. 출장 일정은 녹취(11/10 교수님 면담) 기준 2박3일.
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
const D = 3, N = 2;
const prof = [40000 * D, 60000 * D, 150000 * N];
const stu = [30000 * D * 3, 40000 * D * 3, 100000 * N * 3];
const sum = a => a.reduce((x, y) => x + y, 0);
const budgetRows = [
  ['교수(제1호)', '1', won(prof[0]), won(prof[1]), won(prof[2]), won(sum(prof))],
  ['연구원(제3호)', '3', won(stu[0]), won(stu[1]), won(stu[2]), won(sum(stu))],
  ['계', '4', won(prof[0] + stu[0]), won(prof[1] + stu[1]), won(prof[2] + stu[2]), won(sum(prof) + sum(stu))],
];

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 22 } } } },
  sections: [{ properties: { page: { margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } }, children: [
    title,
    sec('출장 개요'),
    item('기간', "'26. 11. 25(수) ~ 11. 27(금) (2박 3일)"),
    item('출장지', '한국수력원자력(주) 한강수력본부 (춘천댐)'),
    item('출장자', '신주영 교수, 문경민 연구원, ○○○ 연구원, ○○○ 연구원 (4명)'),
    item('교통', '자가용 (신주영 교수 차량)'),
    item('숙박', '춘천 시내 ○○○ (2박)'),
    sec('출장 목적'),
    p('ㅇ 용역 수행 결과 시연 및 발주처 실무 협의', { indent: 400 }),
    sec('세부 일정'),
    grid([2200, 1900, 5538], ['일자', '시간', '내    용'], [
      ['11. 25(수)', '○○:○○~', '국민대학교 출발, 춘천 숙소 도착 및 시연 준비 점검'],
      ['11. 26(목)', '○○:○○~○○:○○', '한강수력본부 시연 및 실무 협의'],
      ['', '○○:○○~○○:○○', '현장(춘천댐) 확인'],
      ['11. 27(금)', '○○:○○~○○:○○', '(업무 내용 기재)'],
      ['', '○○:○○~', '춘천 출발, 국민대학교 도착'],
    ], { left: [2] }),
    sec('소요예산'),
    p('ㅇ 국민대학교 여비규정 별표2(국내 여비 정액표) 기준, 단위: 원', { indent: 400 }),
    grid([1900, 700, 1650, 1650, 2088, 1650], ['구분', '인원', '일비(3일)', '식비(3일)', '숙박비(2박, 상한)', '계'], budgetRows, { total: true }),
    p('※ 일비·식비는 정액, 숙박비는 실비(1박 상한 교수 150,000원, 연구원 100,000원)', { indent: 600, size: 20, before: 120 }),
    p('※ 자가운전 운임은 철도 운임 또는 우등고속 정액 지급 가능(여비규정 제17조 제3항)', { indent: 600, size: 20 }),
    p('※ 집행은 용역 여비 예산 700,800원 이내', { indent: 600, size: 20 }),
  ] }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(process.argv[2], b); console.log('saved', process.argv[2]); });
