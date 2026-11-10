// 11/13 실무회의 계획(안) docx. 참고 양식: 기후부 용역 중간보고회의 계획(안) HWP
const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, AlignmentType,
  BorderStyle, ShadingType, VerticalAlign, PageBreak } = require('docx');

const FONT = '맑은 고딕';
const W = 9638; // A4 본문 폭(여백 1134) DXA
const r = (t, o = {}) => new TextRun({ text: t, font: FONT, size: o.size || 22, bold: o.bold, color: o.color });
const p = (t, o = {}) => new Paragraph({ alignment: o.align, spacing: { before: o.before ?? 60, after: o.after ?? 60, line: 320 },
  indent: o.indent ? { left: o.indent, hanging: o.hanging || 0 } : undefined,
  children: Array.isArray(t) ? t : [r(t, o)] });
const B = { style: BorderStyle.SINGLE, size: 6, color: '000000' };
const NB = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const all = b => ({ top: b, bottom: b, left: b, right: b });
const cell = (kids, w, o = {}) => new TableCell({ width: { size: w, type: WidthType.DXA }, borders: o.borders || all(B),
  shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill, color: 'auto' } : undefined, verticalAlign: VerticalAlign.CENTER,
  margins: { top: 80, bottom: 80, left: 120, right: 120 }, columnSpan: o.span, children: kids });
const box = (kids, o = {}) => new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: [W],
  rows: [new TableRow({ children: [cell(kids, W, o)] })] });
const sec = t => p([r('□ ', { bold: true, size: 26 }), r(t, { bold: true, size: 26 })], { before: 240, after: 80 });
const item = (k, v) => p([r('ㅇ '), r('(' + k + ') ', { bold: true }), r(v)], { indent: 400, hanging: 0 });
const sub = t => p(t, { indent: 1400 });

// 표지 상자
const title = box([
  p('『(용역명)』', { bold: true, size: 30, align: AlignmentType.CENTER, before: 120 }),
  p('연구용역 실무회의 계획(안)', { bold: true, size: 30, align: AlignmentType.CENTER, after: 120 }),
], { borders: { top: { style: BorderStyle.DOUBLE, size: 6, color: '000000' }, bottom: { style: BorderStyle.DOUBLE, size: 6, color: '000000' }, left: NB, right: NB } });

const outline = box([
  p('〈 용 역 개 요 〉', { bold: true, align: AlignmentType.CENTER }),
  ...[['용 역 명', '○○○○○○○○'], ['발 주 처', '한국수력원자력(주)'], ['수 행 사', '국민대학교'],
    ['계약기간', "'26. ○○. ○○. ~ '26. 12. ○○."],
    ['주요내용', '국내외 기술 트렌드 조사, LLM 활용 데이터 파이프라인 조사(온톨로지·메타데이터 설계, RAG-LLM 통합 파이프라인), sLLM 후보군 평가 방향, 도메인 특화 성능 향상 전략 등']]
    .map(([k, v]) => p([r('▸ '), r('(' + k + ') ', { bold: true }), r(v)], { indent: 1500, hanging: 1500 })),
], { fill: 'F2F2F2' });

const SW = [2300, 700, 4738, 1900];
const hdr = ['시간계획', '', '내    용', '비    고'];
const rows = [
  ['○○:○○~○○:○○', "10'", '참석자 소개, 회의 목적 안내', '진행자'],
  ['○○:○○~○○:○○', "20'", '시연 준비 점검: 태스크 82개 질문·답변 결과와 시연 전 보완 항목', '문경민'],
  ['○○:○○~○○:○○', "20'", '최종보고서 작성 방향: 목차·분량, 작성 분담, 일정', '수행기관'],
  ['○○:○○~○○:○○', "20'", '외부 참석자 의견 청취 및 질의응답', '외부 참석자'],
  ['○○:○○~○○:○○', "10'", '준공 일정 공유(12/11 사전검토 제출 서류), 마무리', '-'],
];
const ctr = (t, o) => p(t, { align: AlignmentType.CENTER, size: 20, before: 0, after: 0, ...o });
const sched = new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: SW, rows: [
  new TableRow({ tableHeader: true, children: [
    cell([ctr('시간계획', { bold: true })], SW[0] + SW[1], { fill: 'D9D9D9', span: 2 }),
    cell([ctr('내    용', { bold: true })], SW[2], { fill: 'D9D9D9' }), cell([ctr('비    고', { bold: true })], SW[3], { fill: 'D9D9D9' })] }),
  ...rows.map(x => new TableRow({ children: x.map((t, i) => cell([i === 2 ? p(t, { size: 20, before: 0, after: 0 }) : ctr(t)], SW[i])) })),
] });

const tag = t => new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: [1300, W - 1300], rows: [new TableRow({ children: [
  cell([ctr('붙임' + t[0], { bold: true, color: 'FFFFFF', size: 22 })], 1300, { fill: '404040' }),
  cell([p(t[1], { bold: true, size: 26, before: 0, after: 0 })], W - 1300, { borders: { top: NB, left: NB, right: NB, bottom: B } })] })] });

const MW = [900, 2600, 1500, 2000, 2638];
const people = [['1', '국민대학교', '교  수', '신 주 영', '책임연구원'], ['2', '국민대학교', '연구원', '문 경 민', '수행기관'],
  ['3', '국민대학교', '연구원', '○ ○ ○', '수행기관'], ['4', '국민대학교', '연구원', '○ ○ ○', '수행기관'],
  ['5', '국민대학교', '연구원', '○ ○ ○', '수행기관'], ['○', '○○○○', '박  사', '○ ○ ○', '외부']];
const roster = new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: MW, rows: [
  new TableRow({ tableHeader: true, children: ['번호', '소속', '직위', '이름', '비 고'].map((t, i) => cell([ctr(t, { bold: true })], MW[i], { fill: 'D9D9D9' })) }),
  ...people.map(x => new TableRow({ children: x.map((t, i) => cell([ctr(t)], MW[i])) })),
] });

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 22 } } } },
  sections: [{ properties: { page: { margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } }, children: [
    title,
    p("('26. 11. 13(금), 국민대학교 ○○연구실)", { align: AlignmentType.CENTER, before: 120, after: 200 }),
    outline,
    sec('회의 개요'),
    item('일시', "'26. 11. 13(금) ○○:○○ ~ ○○:○○"),
    item('장소', '○○○ (식당명, 주소는 붙임1)'),
    p([r('ㅇ '), r('(참석) ', { bold: true }), r('[수행기관(○)] 교수(1), 연구원(○)')], { indent: 400 }),
    sub('[외부(1)] ○○○ 박사(○○○○)'),
    item('소요예산', '회의비(석식) ○명 × 50,000원 이내 = ○○○,○○○원'),
    p('※ 참석자는 일정에 따라 조정될 수 있음', { indent: 1000, size: 20 }),
    sec('회의 목적'),
    p('ㅇ 11/26 한강수력본부 시연 준비사항 점검과 최종보고서 작성 방향 논의', { indent: 400 }),
    sec('회의 일정'),
    sched,
    new Paragraph({ children: [new PageBreak()] }),
    tag(['1', '회의 장소 안내']),
    sec('○○○ (식당명)'),
    item('주소', '○○시 ○○구 ○○로 ○○'),
    item('오시는 길', '○○역 ○번 출구 도보 ○분'),
    p('', { before: 400 }),
    tag(['2', '참석자 명단']),
    p([r('ㅇ 총 참석인원 ○명')], { indent: 400, before: 160, after: 120 }),
    roster,
  ] }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(process.argv[2], b); console.log('saved', process.argv[2]); });
