// 출장계획서(국내) docx. 연구행정시스템에 올리는 출장계획서 양식(hwp)과 같은 구성. 11/25~26 한강수력본부 출장(1박 2일).
// 사용: node build_trip_form_1125.js <출력.docx>
const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, AlignmentType, BorderStyle, ShadingType, VerticalAlign } = require('docx');
const FONT = '맑은 고딕', W = 9638;
const r = (t, o = {}) => new TextRun({ text: t, font: FONT, size: o.size || 20, bold: o.bold });
const p = (t, o = {}) => new Paragraph({ alignment: o.align, spacing: { before: o.before ?? 40, after: o.after ?? 40, line: o.line || 300 }, children: [r(t, o)] });
const B = { style: BorderStyle.SINGLE, size: 6, color: '000000' };
const cell = (kids, w, o = {}) => new TableCell({ width: { size: w, type: WidthType.DXA }, borders: { top: B, bottom: B, left: B, right: B },
  shading: o.head ? { type: ShadingType.CLEAR, fill: 'E7E6E6', color: 'auto' } : undefined, verticalAlign: VerticalAlign.CENTER,
  margins: { top: 100, bottom: 100, left: 120, right: 120 }, columnSpan: o.span, rowSpan: o.rows, children: kids });
const H = (t, w, o = {}) => cell(t.split('\n').map(x => p(x, { bold: true, align: AlignmentType.CENTER })), w, { head: true, ...o });
const V = (t, w, o = {}) => cell((Array.isArray(t) ? t : [t]).map(x => p(x)), w, o);
const C = [1100, 1500, 1700, 2300, 1100, 1938]; // 합 9638
const NAME = '「댐 운영 의사결정 프레임워크 구축 자문 용역」 수행 결과 시연 및 실무 협의';
const DAY = '26.11.25.(수) ~ 26.11.26.(목)';
const PLACE = '한국수력원자력(주) 한강수력본부';
const row = k => new TableRow({ children: k });
const table = new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: C, rows: [
  row([H('출장명', C[0]), V(NAME, W - C[0], { span: 5 })]),
  row([H('일  자', C[0]), V(DAY, C[1] + C[2] + C[3], { span: 3 }), H('출장지', C[4]), V(PLACE + ' (강원특별자치도 춘천시)', C[5])]),
  row([H('출장자', C[0]), V('신주영, 문경민', W - C[0], { span: 5 })]),
  row([H('출 장\n내 용', C[0], { rows: 6 }), H('출장 목적', C[1]), V('용역 수행 결과 시연 및 발주처 실무 협의', W - C[0] - C[1], { span: 4 })]),
  row([H('출장 일시', C[1]), V(DAY, W - C[0] - C[1], { span: 4 })]),
  row([H('출장 일정', C[1], { rows: 2 }), V('26.11.25(수)', C[2]), V(['서울 출발 (11.25. ○○:○○)', '춘천 도착 (11.25. ○○:○○)', '시연 준비 점검', '숙박 (춘천시)'], C[3] + C[4] + C[5], { span: 3 })]),
  row([V('26.11.26(목)', C[2]), V(['한강수력본부 도착 (11.26. ○○:○○)', '용역 수행 결과 시연', '발주처 실무 협의', '춘천 출발 (11.26. ○○:○○)', '서울 도착 (11.26. ○○:○○)'], C[3] + C[4] + C[5], { span: 3 })]),
  row([H('장   소', C[1]), V(PLACE + ' (강원특별자치도 춘천시 신북읍 영서로)', W - C[0] - C[1], { span: 4 })]),
  row([H('참 석 자', C[1]), V('신주영, 문경민, 김장호, 황솔비', W - C[0] - C[1], { span: 4 })]),
  row([cell([p('국내출장계획서를 상기와 같이 제출합니다.', { align: AlignmentType.CENTER, bold: true, before: 200 }), p('2026. 11. ○○.', { align: AlignmentType.CENTER, before: 120 }),
    p('연구책임자 : 신 주 영   (인)', { align: AlignmentType.RIGHT, bold: true, before: 120, after: 200 })], W, { span: 6 })]),
] });
const doc = new Document({ styles: { default: { document: { run: { font: FONT, size: 20 } } } },
  sections: [{ properties: { page: { margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } }, children: [
    p('출장계획서(국내)', { size: 40, bold: true, align: AlignmentType.CENTER, after: 300 }), table ] }] });
Packer.toBuffer(doc).then(b => { fs.writeFileSync(process.argv[2], b); console.log('saved', process.argv[2]); });
