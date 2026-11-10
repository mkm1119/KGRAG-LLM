// 11/13 실무회의 계획(안) docx. 내용은 사용자가 고친 hwpx(최종본) 기준. 참고 양식: 회의 계획(안) HWP
// 사용: node build_meeting_plan_1113.js <출력.docx> [약도.png]
const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, AlignmentType,
  BorderStyle, ShadingType, VerticalAlign, PageBreak, ImageRun } = require('docx');

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
const item = (k, v) => p([r('ㅇ '), r('(' + k + ') ', { bold: true }), r(v)], { indent: 400 });
const ctr = (t, o) => p(t, { align: AlignmentType.CENTER, size: 20, before: 0, after: 0, ...o });

const title = box([
  p('『댐 운영 의사결정 프레임워크 구축 자문 용역』', { bold: true, size: 30, align: AlignmentType.CENTER, before: 120 }),
  p('연구용역 실무회의 계획(안)', { bold: true, size: 30, align: AlignmentType.CENTER, after: 120 }),
], { borders: { top: { style: BorderStyle.DOUBLE, size: 6, color: '000000' }, bottom: { style: BorderStyle.DOUBLE, size: 6, color: '000000' }, left: NB, right: NB } });

const outline = box([
  p('〈 용 역 개 요 〉', { bold: true, align: AlignmentType.CENTER }),
  ...[['용 역 명', '댐 운영 의사결정 프레임워크 구축 자문 용역'], ['발 주 처', '한국수력원자력(주)'], ['수 행 사', '국민대학교 산학협력단'],
    ['계약기간', "'26. 07. 23. ~ '27. 01. 22."],
    ['주요내용', '국내외 기술 트렌드 조사, LLM 활용 데이터 파이프라인 조사(온톨로지·메타데이터 설계, RAG-LLM 통합 파이프라인), sLLM 후보군 평가 방향, 도메인 특화 성능 향상 전략 등']]
    .map(([k, v]) => p([r('▸ '), r('(' + k + ') ', { bold: true }), r(v)], { indent: 1500, hanging: 1500 })),
], { fill: 'F2F2F2' });

const SW = [2300, 700, 4738, 1900];
const sched = new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: SW, rows: [
  new TableRow({ tableHeader: true, children: [
    cell([ctr('시간계획', { bold: true })], SW[0] + SW[1], { fill: 'D9D9D9', span: 2 }),
    cell([ctr('내    용', { bold: true })], SW[2], { fill: 'D9D9D9' }), cell([ctr('비    고', { bold: true })], SW[3], { fill: 'D9D9D9' })] }),
  ...[['17:30~17:40', "10'", '참석자 소개, 회의 목적 안내', '진행자'],
    ['17:40~18:10', "30'", '용역 추진 현황 공유', '용역 수행사'],
    ['18:10~18:50', "40'", '최종보고서 작성 방향 논의', '전체 참석자'],
    ['18:50~19:20', "30'", '의견 교환 및 질의응답', '전체 참석자'],
    ['19:20~19:30', "10'", '향후 일정 공유 및 마무리', '-']]
    .map(x => new TableRow({ children: x.map((t, i) => cell([i === 2 ? p(t, { size: 20, before: 0, after: 0 }) : ctr(t)], SW[i])) })),
] });

const tag = t => new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: [1300, W - 1300], rows: [new TableRow({ children: [
  cell([ctr('붙임' + t[0], { bold: true, color: 'FFFFFF', size: 22 })], 1300, { fill: '404040' }),
  cell([p(t[1], { bold: true, size: 26, before: 0, after: 0 })], W - 1300, { borders: { top: NB, left: NB, right: NB, bottom: B } })] })] });

// 약도: 이미지가 있으면 넣고, 없으면 같은 크기의 빈 칸
const MAP = process.argv[3];
const mapW = 560, mapH = 360; // px (docx ImageRun 단위)
const mapCell = MAP && fs.existsSync(MAP)
  ? [new Paragraph({ alignment: AlignmentType.CENTER, children: [new ImageRun({ type: 'png', data: fs.readFileSync(MAP), transformation: { width: mapW, height: mapH } })] })]
  : [p('', { before: 2200 }), ctr('(약도 삽입 위치: 청수장, 정릉역 2번 출구)', { color: '808080' }), p('', { after: 2200 })];
const mapBox = new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: [W], rows: [
  new TableRow({ children: [cell([ctr('약    도', { bold: true })], W, { fill: 'D9D9D9' })] }),
  new TableRow({ children: [cell(mapCell, W)] })] });

const MW = [900, 2600, 1500, 2000, 2638];
const people = [['1', '국민대학교', '교  수', '신  주  영', '용역 수행사'], ['2', '경기대학교', '교  수', '성  경  민', '외부 참석자'],
  ['3', '국민대학교', '연구원', '박  지  연', '-'], ['4', '국민대학교', '연구원', '장  상  범', '-'],
  ['5', '국민대학교', '연구원', '조  수  빈', '-'], ['6', '국민대학교', '연구원', '김  지  환', '-'],
  ['7', '국민대학교', '연구원', '길  준  영', '-'], ['8', '국민대학교', '연구원', '문  경  민', '용역 수행사'],
  ['9', '국민대학교', '연구원', '고  윤  채', '-']];
const roster = new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: MW, rows: [
  new TableRow({ tableHeader: true, children: ['번호', '소속', '직위', '이름', '비 고'].map((t, i) => cell([ctr(t, { bold: true })], MW[i], { fill: 'D9D9D9' })) }),
  ...people.map(x => new TableRow({ children: x.map((t, i) => cell([ctr(t)], MW[i])) })),
] });

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 22 } } } },
  sections: [{ properties: { page: { margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } }, children: [
    title,
    p('', { before: 120 }),
    outline,
    sec('회의 개요'),
    item('일시', "'26. 11. 13(금) 17:30 ~ 19:30"),
    item('장소', '청수장 (식사를 겸한 회의, 주소는 붙임1)'),
    p([r('ㅇ '), r('(참석) ', { bold: true }), r('[경기대학교(1)] 성경민 교수')], { indent: 400 }),
    p('[국민대학교(8)] 신주영 교수, 박지연 연구원, 장상범 연구원, 조수빈 연구원, 김지환 연구원, 길준영 연구원, 문경민 연구원, 고윤채 연구원', { indent: 1260 }),
    item('소요예산', '회의비(석식) 9명 × 50,000원 이내 = 450,000원 이내'),
    p('※ 참석자는 일정에 따라 조정될 수 있음', { indent: 1000, size: 20 }),
    sec('회의 목적'),
    p('ㅇ 용역 추진 현황 공유 및 최종보고서 작성 방향 등 세부사항 논의', { indent: 400 }),
    sec('회의 일정'),
    sched,
    new Paragraph({ children: [new PageBreak()] }),
    tag(['1', '회의 장소 안내']),
    sec('청수장'),
    item('주소', '서울특별시 성북구 정릉로 237-2'),
    item('오시는 길', '우이신설선 정릉역 2번 출구, 정릉삼거리 정릉도서관 앞'),
    p('', { before: 60 }),
    mapBox,
    new Paragraph({ children: [new PageBreak()] }),
    tag(['2', '참석자 명단']),
    p([r('ㅇ 총 참석인원 9명')], { indent: 400, before: 160, after: 120 }),
    roster,
  ] }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(process.argv[2], b); console.log('saved', process.argv[2], MAP ? 'map=' + MAP : 'map=placeholder'); });
