// 11/26 한강수력본부 발표자료 초안(pptx). 구성: 구조(온톨로지 → CQ → Class·속성·관계 → KG → 자료 → 외부 저장소 → RAG) → 시연 범위 → 시연 영상 → 한계와 향후 방향.
// 모양은 7월 기술 세미나 자료(로고 위치, 남색·파랑, KoPubWorld돋움체)를 따른다. 숫자와 예시 값은 03_normalized의 KG(kgv4), 승인 기록, 측정 저장소에서 가져온 값이다.
// 사용: node build_khnp_talk_1126.js <출력.pptx> <khnp 로고.jpg> <kmu 로고.jpg> <KG 전체 그림.png>
let pptxgen; try { pptxgen = require('pptxgenjs'); } catch (e) { pptxgen = require('./mini_pptx.js'); }  // pptxgenjs가 없으면 같은 폴더의 대체 모듈을 쓴다
const [OUT, KHNP, KMU, KGPIC] = process.argv.slice(2);
const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE'; // 13.333 x 7.5
pres.title = '댐 운영 의사결정 프레임워크 구축 자문 용역 - 지식그래프 기반 질의응답 구조와 시연';
const F = 'KoPubWorld돋움체 Medium';
pres.theme = { headFontFace: F, bodyFontFace: F };
const NAVY = '003B71', BLUE = '0070C0', SKY = 'EEF5FC', SKY2 = 'DCE9F7', LINE = 'C9D8E8', GRAY = '6B7280', INK = '2B2B2B', ORANGE = 'C55A11', WHITE = 'FFFFFF', PALE = 'F6F8FB';
const C_HMS = '2E9E8F', C_CRI = 'C55A11', C_APR = '0070C0', C_OPR = '7B5EA7', C_EVI = '7F8B99'; // KG 전체 그림과 같은 색
const FOOT = '댐 운영 의사결정 프레임워크 구축 자문 용역';

pres.defineSlideMaster({ title: 'CONTENT', background: { color: WHITE }, objects: [
  { image: { path: KHNP, x: 7.73, y: 0.18, w: 3.27, h: 0.47 } },
  { image: { path: KMU, x: 11.1, y: 0.03, w: 2.21, h: 0.74 } },
  { text: { text: FOOT, options: { x: 0.55, y: 7.05, w: 6, h: 0.3, fontFace: F, fontSize: 9, color: '9AA5B1', margin: 0 } } },
], slideNumber: { x: 12.2, y: 7.05, w: 0.6, h: 0.3, fontFace: F, fontSize: 9, color: '9AA5B1', align: 'right' } });

// ---- 도우미
const T = (s, text, o) => s.addText(text, Object.assign({ fontFace: F, color: INK, margin: 0, isTextBox: true, valign: 'top' }, o));
function head(s, sec, title, sub) {
  T(s, sec, { x: 0.55, y: 0.32, w: 6.5, h: 0.3, fontSize: 11, color: BLUE, bold: true });
  T(s, title, { x: 0.55, y: 0.66, w: 12.2, h: 0.6, fontSize: 26, color: NAVY, bold: true });
  if (sub) T(s, sub, { x: 0.55, y: 1.3, w: 12.2, h: 0.35, fontSize: 14, color: GRAY });
}
const box = (s, x, y, w, h, o = {}) => s.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: o.r ?? 0.08, fill: { color: o.fill || SKY }, line: { color: o.line || o.fill || SKY, width: o.lw ?? 0.75 } });
const rect = (s, x, y, w, h, fill, line) => s.addShape(pres.ShapeType.rect, { x, y, w, h, fill: { color: fill }, line: { color: line || fill, width: 0.75 } });
// 상자 하나(제목 + 작은 글씨). 반환값은 화살표를 이을 때 쓰는 자리 정보
function node(s, x, y, w, h, title, sub, o = {}) {
  box(s, x, y, w, h, { fill: o.fill || NAVY, line: o.line || o.fill || NAVY, r: o.r });
  s.addText([{ text: title, options: { fontSize: o.fs || 16, bold: true, color: o.color || WHITE, breakLine: !!sub } }].concat(sub ? [{ text: sub, options: { fontSize: o.fs2 || 11, color: o.color2 || 'DCE9F7' } }] : []),
    { x, y, w, h, fontFace: F, align: 'center', valign: 'middle', margin: 0.05, isTextBox: true });
  return { x, y, w, h };
}
// 상자 가장자리에서 상대 상자 쪽으로 나가는 점
function edge(a, b) {
  const ax = a.x + a.w / 2, ay = a.y + a.h / 2, bx = b.x + b.w / 2, by = b.y + b.h / 2, dx = bx - ax, dy = by - ay;
  const t = Math.min(dx ? (a.w / 2) / Math.abs(dx) : 1e9, dy ? (a.h / 2) / Math.abs(dy) : 1e9);
  return [ax + dx * t, ay + dy * t];
}
// 점에서 점으로 가는 화살표. 양 끝을 조금 띄워 화살촉이 상자에 가리지 않게 하고, 이름표는 선 옆에 둔다
function line(s, p, q, label, o = {}) {
  const dx = q[0] - p[0], dy = q[1] - p[1], L = Math.hypot(dx, dy) || 1, ux = dx / L, uy = dy / L, g = o.gap ?? 0.07;
  const x1 = p[0] + ux * g, y1 = p[1] + uy * g, x2 = q[0] - ux * g, y2 = q[1] - uy * g;
  s.addShape(pres.ShapeType.line, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1), flipH: x2 < x1, flipV: y2 < y1,
    line: { color: o.color || BLUE, width: o.width || 2, endArrowType: 'triangle', dashType: o.dash ? 'dash' : 'solid' } });
  if (label) {
    const w = o.lw || 1.5, off = o.off ?? 0.2, t = o.t ?? 0.5; let nx = -uy, ny = ux; if (ny > 0) { nx = -nx; ny = -ny; }   // 이름표는 선의 위쪽
    const cx = x1 + (x2 - x1) * t + nx * off * (o.side || 1), cy = y1 + (y2 - y1) * t + ny * off * (o.side || 1);
    T(s, label, { x: cx - w / 2, y: cy - 0.15, w, h: 0.3, fontSize: o.fs || 12, color: o.lc || ORANGE, bold: true, align: 'center', valign: 'middle' });
  }
}
const link = (s, a, b, label, o) => line(s, edge(a, b), edge(b, a), label, o);
const chip = (s, x, y, w, text, o = {}) => { box(s, x, y, w, o.h || 0.34, { fill: o.fill || BLUE, r: (o.h || 0.34) / 2 }); T(s, text, { x, y, w, h: o.h || 0.34, fontSize: o.fs || 12, bold: true, color: o.color || WHITE, align: 'center', valign: 'middle' }); };
// 작은 표(원본 자료의 모양을 보여 주는 용도)
function mini(s, x, y, widths, headRow, rows, o = {}) {
  const hh = o.hh || 0.36, rh = o.rh || 0.36, fs = o.fs || 12; let cx = x;
  widths.forEach((w, i) => { rect(s, cx, y, w, hh, 'E5E7EB', 'B6BCC6'); T(s, headRow[i], { x: cx, y, w, h: hh, fontSize: fs, bold: true, align: 'center', valign: 'middle' });
    rows.forEach((r, k) => { const hl = o.hl === k; rect(s, cx, y + hh + k * rh, w, rh, hl ? 'FFF4D6' : WHITE, 'B6BCC6'); T(s, r[i], { x: cx, y: y + hh + k * rh, w, h: rh, fontSize: fs, align: 'center', valign: 'middle', bold: hl }); });
    cx += w; });
  return { x, y, w: widths.reduce((a, b) => a + b, 0), h: hh + rows.length * rh };
}
const add = sec => pres.addSlide({ masterName: 'CONTENT', sectionTitle: sec });

// ================================================= 1. 표지
pres.addSection({ title: '표지' });
{
  const s = pres.addSlide({ sectionTitle: '표지' }); s.background = { color: WHITE };
  s.addImage({ path: KHNP, x: 7.73, y: 0.18, w: 3.27, h: 0.47 }); s.addImage({ path: KMU, x: 11.1, y: 0.03, w: 2.21, h: 0.74 });
  box(s, 0, 0.9, 5.2, 6.6, { fill: NAVY, r: 0 });
  T(s, 'Knowledge Graph', { x: 0.6, y: 3.0, w: 4.2, h: 0.5, fontSize: 22, color: '9DBEDD', bold: true });
  T(s, '+ RAG + LLM', { x: 0.6, y: 3.5, w: 4.2, h: 0.5, fontSize: 22, color: WHITE, bold: true });
  T(s, '수행 결과 발표', { x: 6.0, y: 2.55, w: 6.8, h: 0.35, fontSize: 14, color: BLUE, bold: true, align: 'right' });
  T(s, '댐 운영 의사결정\n프레임워크 구축 자문 용역', { x: 6.0, y: 2.95, w: 6.8, h: 1.5, fontSize: 34, color: NAVY, bold: true, align: 'right' });
  T(s, '지식그래프 기반 질의응답 구조와 시연', { x: 6.0, y: 4.5, w: 6.8, h: 0.4, fontSize: 16, color: GRAY, align: 'right' });
  s.addShape(pres.ShapeType.line, { x: 8.3, y: 5.2, w: 4.5, h: 0, line: { color: 'BCBEC0', width: 0.75 } });
  T(s, '주관연구기관  ┃  국민대학교 산학협력단', { x: 6.0, y: 5.35, w: 6.8, h: 0.32, fontSize: 13, color: INK, align: 'right' });
  T(s, '연구책임자  ┃  신주영', { x: 6.0, y: 5.7, w: 6.8, h: 0.32, fontSize: 13, color: INK, align: 'right' });
  T(s, '2026. 11.', { x: 6.0, y: 6.25, w: 6.8, h: 0.3, fontSize: 12, color: GRAY, align: 'right' });
}

// ================================================= 2. 순서
pres.addSection({ title: '순서' });
{
  const s = add('순서'); head(s, '발표 순서', '오늘 말씀드릴 내용', '구조를 간단히 설명드리고, 시연 영상을 보여 드립니다');
  const items = [['Ⅰ', '만든 구조', '온톨로지와 지식그래프로\n자료를 잇고, 근거를 찾아 답하는 구조'], ['Ⅱ', '시연', '정한 범위의 질문에\n근거와 출처를 붙여 답하는 모습'], ['Ⅲ', '한계와 향후 방향', '지금 구조의 한계와\n다음 단계']];
  items.forEach((it, i) => { const x = 0.55 + i * 4.18;
    box(s, x, 2.0, 3.9, 4.5, { fill: i === 0 ? NAVY : SKY });
    T(s, it[0], { x: x + 0.4, y: 2.45, w: 1, h: 0.8, fontSize: 40, bold: true, color: i === 0 ? '9DBEDD' : BLUE });
    T(s, it[1], { x: x + 0.4, y: 3.6, w: 3.3, h: 0.55, fontSize: 26, bold: true, color: i === 0 ? WHITE : NAVY });
    T(s, it[2], { x: x + 0.4, y: 4.45, w: 3.3, h: 1.4, fontSize: 16, color: i === 0 ? 'DCE9F7' : INK, lineSpacingMultiple: 1.3 });
  });
}

// ================================================= Ⅰ. 구조
pres.addSection({ title: 'Ⅰ. 만든 구조' });
// 3. 온톨로지: 구성요소 세 가지를 한 그림에서
{
  const s = add('Ⅰ. 만든 구조'); head(s, 'Ⅰ. 만든 구조', '온톨로지란', '어떤 분야에 무엇이 있고, 각각 어떤 특징을 가지며, 서로 어떻게 이어지는지를 정해 둔 설계도');
  const comp = [['Class', NAVY, '다루는 대상의 종류', '예: 댐, 방류 승인, 운영행위'], ['속성', C_HMS, 'Class를 설명하는 항목', '예: 방류 승인의 승인일, 승인 내용'], ['관계', ORANGE, 'Class와 Class를 잇는 선', '예: 방류 승인이 운영행위를 허가함']];
  T(s, '온톨로지의 구성요소', { x: 0.55, y: 1.9, w: 4.0, h: 0.35, fontSize: 14, bold: true, color: GRAY });
  comp.forEach((c, i) => { const y = 2.3 + i * 1.47;
    box(s, 0.55, y, 4.1, 1.32, { fill: PALE, line: LINE }); chip(s, 0.75, y + 0.2, 1.05, c[0], { fill: c[1], fs: 13, h: 0.38 });
    T(s, c[2], { x: 1.95, y: y + 0.2, w: 2.6, h: 0.38, fontSize: 15, bold: true, color: NAVY, valign: 'middle' });
    T(s, c[3], { x: 0.75, y: y + 0.75, w: 3.8, h: 0.4, fontSize: 13, color: GRAY, valign: 'middle' }); });
  box(s, 4.95, 2.3, 7.83, 4.26, { fill: SKY });
  T(s, '예: 방류 승인 기록을 온톨로지로 나타내면', { x: 4.95, y: 1.9, w: 7.8, h: 0.35, fontSize: 14, bold: true, color: GRAY });
  const A = node(s, 5.35, 2.75, 2.5, 0.85, '방류 승인'), B = node(s, 9.85, 2.75, 2.5, 0.85, '운영행위'), D = node(s, 7.6, 5.1, 2.5, 0.85, '댐');
  const prop = (x, y, t) => { box(s, x, y, 2.5, 0.62, { fill: WHITE, line: C_HMS }); T(s, t, { x, y, w: 2.5, h: 0.62, fontSize: 12.5, color: INK, align: 'center', valign: 'middle' }); };
  prop(5.35, 3.6, '승인일, 승인 내용'); prop(9.85, 3.6, '종류, 시각'); prop(7.6, 5.95, '이름, 종류');
  link(s, A, B, '허가함', { lw: 1.0, fs: 13 });
  line(s, [6.6, 4.22], [7.9, 5.1], '대상', { lw: 0.8, fs: 13, side: -1, off: 0.3 }); line(s, [11.1, 4.22], [9.8, 5.1], '수행됨', { lw: 1.0, fs: 13, off: 0.4 });
  chip(s, 5.35, 2.37, 0.85, 'Class', { fill: NAVY, fs: 11, h: 0.3 }); chip(s, 5.35, 4.3, 0.75, '속성', { fill: C_HMS, fs: 11, h: 0.3 }); chip(s, 8.5, 2.5, 0.75, '관계', { fill: ORANGE, fs: 11, h: 0.3 });
}
// 4. CQ
{
  const s = add('Ⅰ. 만든 구조'); head(s, 'Ⅰ. 만든 구조', '범위를 정하는 방법: CQ', '온톨로지는 한 번에 모든 것을 담지 않는다. 먼저 답해야 할 질문을 정하고, 그 질문에 필요한 만큼만 만든다');
  box(s, 0.55, 1.9, 12.23, 1.05, { fill: NAVY });
  T(s, [{ text: 'CQ (Competency Question)', options: { bold: true, color: WHITE, fontSize: 18, breakLine: true } }, { text: '온톨로지가 답할 수 있어야 하는 질문.  만들기 전에 먼저 정하고, 다 만든 뒤에는 이 질문에 답이 되는지로 확인한다', options: { color: 'DCE9F7', fontSize: 14 } }],
    { x: 0.85, y: 1.9, w: 11.7, h: 1.05, valign: 'middle', lineSpacingMultiple: 1.2 });
  const cq = [['CQ1', '댐의 현재 수문 상태는?'], ['CQ2', '과거 어느 시점의 수문 상태는?'], ['CQ3', '과거에 어떤 방류 조작이 있었나?'], ['CQ4', '과거에 어떤 방류 승인이 있었나?'], ['CQ5', '댐에 적용되는 운영기준은?'], ['CQ6', '위 내용의 공식 근거는?']];
  cq.forEach((c, i) => { const x = 0.55 + (i % 2) * 6.2, y = 3.15 + Math.floor(i / 2) * 0.93;
    box(s, x, y, 6.03, 0.8, { fill: SKY }); chip(s, x + 0.25, y + 0.23, 0.95, c[0]);
    T(s, c[1], { x: x + 1.45, y, w: 4.4, h: 0.8, fontSize: 17, bold: true, color: NAVY, valign: 'middle' }); });
  box(s, 0.55, 5.98, 12.23, 0.78, { fill: PALE, line: LINE });
  T(s, [{ text: '이번 과업의 출발 범위  ', options: { bold: true, color: BLUE } }, { text: '댐 운영 기록을 조회하는 질문 6개로 시작했다. 실무 검토를 거쳐 질문을 더하면 범위가 넓어진다' }], { x: 0.85, y: 5.98, w: 11.7, h: 0.78, fontSize: 15, valign: 'middle' });
}
// 5. CQ에서 Class와 관계 (트리플)
{
  const s = add('Ⅰ. 만든 구조'); head(s, 'Ⅰ. 만든 구조', 'CQ에서 Class와 관계를 뽑는다', '질문에 나오는 대상이 Class가 되고, 대상 사이의 연결이 관계가 된다');
  T(s, 'CQ', { x: 0.55, y: 1.85, w: 5.5, h: 0.3, fontSize: 13, bold: true, color: GRAY });
  T(s, '뽑아낸 Class와 관계   ( Class — 관계 → Class )', { x: 6.35, y: 1.85, w: 6.4, h: 0.3, fontSize: 13, bold: true, color: GRAY });
  const rows = [
    ['CQ1·2', [['댐', 'c'], ['의 현재·과거 '], ['수문 상태', 'c'], ['는?']], '댐은 수문·기상 상태를 가진다', '댐', '상태를 가짐', '수문·기상 상태'],
    ['CQ3', [['댐', 'c'], ['에서 과거에 어떤 '], ['방류 조작', 'c'], ['이 있었나?']], '운영행위는 댐에서 수행된다', '운영행위', '수행됨', '댐'],
    ['CQ4', [['과거에 어떤 '], ['방류 승인', 'c'], ['이 있었나?']], '방류 승인은 운영행위를 허가한다', '방류 승인', '허가함', '운영행위'],
    ['CQ5', [['댐', 'c'], ['에 적용되는 '], ['운영기준', 'c'], ['은?']], '운영기준은 댐에 적용된다', '운영기준', '적용됨', '댐'],
    ['CQ6', [['위 내용의 공식 '], ['근거', 'c'], ['는?']], '방류 승인은 근거를 둔다', '방류 승인', '근거를 둠', '근거'],
  ];
  rows.forEach((r, i) => { const y = 2.2 + i * 0.92;
    box(s, 0.55, y, 5.55, 0.8, { fill: PALE, line: LINE }); chip(s, 0.7, y + 0.23, 0.95, r[0], { fs: 11.5 });
    s.addText(r[1].map(p => ({ text: p[0], options: { color: p[1] ? BLUE : INK, bold: !!p[1] } })), { x: 1.8, y: y + 0.06, w: 4.2, h: 0.4, fontFace: F, fontSize: 15.5, valign: 'middle', margin: 0, isTextBox: true });
    T(s, '→ ' + r[2], { x: 1.8, y: y + 0.44, w: 4.2, h: 0.3, fontSize: 12, color: ORANGE, bold: true, valign: 'middle' });
    box(s, 6.35, y, 6.43, 0.8, { fill: SKY });
    const a = node(s, 6.55, y + 0.12, 2.15, 0.56, r[3], null, { fs: 14 }), b = node(s, 10.43, y + 0.12, 2.15, 0.56, r[5], null, { fs: 14 });
    link(s, a, b, r[4], { lw: 1.5, fs: 12.5, off: 0.17 }); });
}
// 6. 우리 온톨로지 (그림으로 전부)
{
  const s = add('Ⅰ. 만든 구조'); head(s, 'Ⅰ. 만든 구조', '이렇게 만든 온톨로지', 'Class 6개가 관계로 이어진 모습');
  const W = 2.65, H = 1.0;
  const dam = node(s, 5.34, 1.85, W, H, '댐', '이름, 종류');
  const cri = node(s, 0.6, 3.6, W, H, '운영기준', '종류, 값, 단위', { fill: C_CRI });
  const apr = node(s, 3.76, 3.6, W, H, '방류 승인', '승인일, 승인 내용', { fill: C_APR });
  const opr = node(s, 6.92, 3.6, W, H, '운영행위', '종류, 시각', { fill: C_OPR });
  const hms = node(s, 10.08, 3.6, W, H, '수문·기상 상태', '항목, 관측소 코드', { fill: C_HMS });
  const evi = node(s, 5.34, 5.55, W, H, '근거', '제목, 종류, 위치', { fill: C_EVI });
  link(s, cri, dam, '적용됨', { lw: 0.9 }); link(s, apr, dam, '대상', { lw: 0.7, off: 0.28 }); link(s, opr, dam, '수행됨', { lw: 0.9, off: 0.33, side: -1 }); link(s, dam, hms, '상태를 가짐', { lw: 1.3 });
  link(s, apr, opr, '허가함', { lw: 0.9, off: 0.18 });
  link(s, cri, evi, '근거를 둠', { lw: 1.1, side: -1, off: 0.22 }); link(s, apr, evi, null); link(s, opr, evi, null); link(s, hms, evi, '근거를 둠', { lw: 1.1, side: -1, off: 0.22 });
  // 범례 (그림으로)
  box(s, 0.6, 5.5, 3.3, 1.2, { fill: PALE, line: LINE });
  box(s, 0.78, 5.66, 0.75, 0.4, { fill: NAVY }); T(s, 'Class', { x: 1.65, y: 5.66, w: 1.2, h: 0.4, fontSize: 12, valign: 'middle' });
  T(s, '작은 글씨', { x: 0.78, y: 6.18, w: 0.8, h: 0.35, fontSize: 9.5, color: GRAY, valign: 'middle' }); T(s, '속성', { x: 1.65, y: 6.18, w: 0.8, h: 0.35, fontSize: 12, valign: 'middle' });
  line(s, [2.55, 5.86], [3.2, 5.86], null, { gap: 0 }); T(s, '관계', { x: 3.25, y: 5.66, w: 0.6, h: 0.4, fontSize: 12, valign: 'middle' });
}
// 7. KG
{
  const s = add('Ⅰ. 만든 구조'); head(s, 'Ⅰ. 만든 구조', '지식그래프(KG)란', '온톨로지라는 틀에 실제 자료를 채워 넣은 것');
  T(s, '온톨로지 (틀)', { x: 0.55, y: 1.9, w: 5.4, h: 0.4, fontSize: 16, bold: true, color: GRAY, align: 'center' });
  box(s, 0.55, 2.35, 5.4, 3.6, { fill: PALE, line: LINE });
  const a1 = node(s, 0.9, 2.95, 1.95, 0.9, '방류 승인', null, { fill: WHITE, line: BLUE, color: BLUE }), b1 = node(s, 3.65, 2.95, 1.95, 0.9, '운영행위', null, { fill: WHITE, line: BLUE, color: BLUE }), d1 = node(s, 2.27, 4.6, 1.95, 0.9, '댐', null, { fill: WHITE, line: BLUE, color: BLUE });
  link(s, a1, b1, '허가함', { lw: 0.8, off: 0.18 }); link(s, b1, d1, '수행됨', { lw: 0.8, side: -1, off: 0.35 }); link(s, a1, d1, '대상', { lw: 0.6, off: 0.3 });
  line(s, [6.1, 4.15], [7.25, 4.15], null, { color: NAVY, width: 3, gap: 0 }); T(s, '실제 자료를\n채움', { x: 5.95, y: 4.3, w: 1.45, h: 0.6, fontSize: 12, color: NAVY, bold: true, align: 'center' });
  T(s, '지식그래프 (실제 값)', { x: 7.4, y: 1.9, w: 5.4, h: 0.4, fontSize: 16, bold: true, color: NAVY, align: 'center' });
  box(s, 7.4, 2.35, 5.4, 3.6, { fill: SKY, line: SKY2 });
  const a2 = node(s, 7.65, 2.85, 2.2, 1.1, '승인 3412', '2020-08-02\n승인량 3000㎥/s', { fs: 14, fs2: 10 }), b2 = node(s, 10.35, 2.85, 2.2, 1.1, '방류', '2020-08-02 18:00', { fs: 14, fs2: 10 }), d2 = node(s, 9.0, 4.6, 2.2, 1.0, '충주댐', '다목적댐', { fs: 14, fs2: 10 });
  link(s, a2, b2, null); link(s, b2, d2, null); link(s, a2, d2, null);
  box(s, 0.55, 6.12, 12.23, 0.62, { fill: NAVY });
  T(s, 'Entity: Class에 실제 값이 들어간 하나하나 (예: 충주댐, 승인 3412)', { x: 0.55, y: 6.12, w: 12.23, h: 0.62, fontSize: 15, bold: true, color: WHITE, align: 'center', valign: 'middle' });
}
// 8. 자료 (원본 표의 모양을 보여 줌)
{
  const s = add('Ⅰ. 만든 구조'); head(s, 'Ⅰ. 만든 구조', 'KG에 채운 실제 자료', 'K-water 댐 4개(충주댐, 소양강댐, 횡성댐, 광동댐)의 공개 자료 세 종류');
  const col = [[0.55, '시간 측정값', 'K-water 공개 자료', '댐 지점에서 1시간마다 잰 값 6가지', '6개 항목 · 2010~2026년 · 약 87만 행'], [4.73, '방류 승인 기록', '한강홍수통제소 공개 자료', '언제, 얼마의 방류를 승인했는지', '댐 4개 · 2010~2021년 · 80건'], [8.91, '운영 규정', '댐과 보 등의 연계운영규정 별표 3', '댐별 홍수기 제한수위', '충주댐, 소양강댐, 횡성댐 · 3건']];
  col.forEach(c => { box(s, c[0], 1.9, 3.87, 4.85, { fill: SKY }); box(s, c[0], 1.9, 3.87, 0.95, { fill: NAVY });
    T(s, c[1], { x: c[0] + 0.25, y: 1.98, w: 3.4, h: 0.45, fontSize: 19, bold: true, color: WHITE }); T(s, c[2], { x: c[0] + 0.25, y: 2.43, w: 3.4, h: 0.32, fontSize: 11.5, color: 'CFE0F2' });
    T(s, c[3], { x: c[0] + 0.25, y: 3.02, w: 3.4, h: 0.35, fontSize: 14, bold: true, color: NAVY });
    T(s, c[4], { x: c[0] + 0.25, y: 6.25, w: 3.4, h: 0.32, fontSize: 12, color: GRAY }); });
  mini(s, 0.75, 3.5, [1.0, 0.8, 0.85, 0.82], ['시각', '수위', '유입량', '총방류량'], [['17:00', '139.37', '4693.7', '707.3'], ['18:00', '139.55', '4945.2', '707.1'], ['19:00', '139.69', '4015.5', '707.5']], { fs: 12, rh: 0.4, hh: 0.4 });
  T(s, '충주댐 2020-08-02  (EL.m, CMS)', { x: 0.75, y: 5.2, w: 3.5, h: 0.3, fontSize: 11, color: GRAY });
  T(s, '+ 저수량, 강우량, 저수율', { x: 0.75, y: 5.5, w: 3.5, h: 0.3, fontSize: 11, color: GRAY });
  mini(s, 4.93, 3.5, [1.15, 1.25, 1.07], ['승인일', '방류 시작', '승인 방류량'], [['2020-08-02', '08-02 18:00', '3000'], ['2020-08-06', '08-02 18:00', '7000'], ['2020-08-12', '08-06 06:00', '7000']], { fs: 12, rh: 0.4, hh: 0.4 });
  T(s, '충주댐 2020년 8월  (㎥/s)', { x: 4.93, y: 5.2, w: 3.5, h: 0.3, fontSize: 11, color: GRAY });
  T(s, '+ 비고 (기간·방류량 변경 내용 등)', { x: 4.93, y: 5.5, w: 3.5, h: 0.3, fontSize: 11, color: GRAY });
  mini(s, 9.11, 3.5, [1.6, 1.87], ['댐', '홍수기 제한수위'], [['소양강댐', '190.3'], ['충주댐', '138.0'], ['횡성댐', '178.2']], { fs: 12, rh: 0.4, hh: 0.4 });
  T(s, '단위 EL.m', { x: 9.11, y: 5.2, w: 3.5, h: 0.3, fontSize: 11, color: GRAY });
}
// 9. 자료가 KG가 되는 과정 (세 자료 → Class 6개)
{
  const s = add('Ⅰ. 만든 구조'); head(s, 'Ⅰ. 만든 구조', '자료가 KG가 되는 과정', '원본 자료의 칸이 온톨로지의 Class 자리에 들어간다');
  T(s, '원본 자료', { x: 0.55, y: 1.82, w: 5.9, h: 0.3, fontSize: 13, bold: true, color: GRAY }); T(s, 'KG  (Class에 값이 들어간 모습)', { x: 8.35, y: 1.82, w: 4.4, h: 0.3, fontSize: 13, bold: true, color: GRAY });
  // 자료 1: 방류 승인 기록 (비고가 있는 행)
  T(s, '방류 승인 기록', { x: 0.55, y: 2.15, w: 4, h: 0.28, fontSize: 12.5, bold: true, color: NAVY });
  const t1 = mini(s, 0.55, 2.45, [0.95, 0.85, 1.25, 1.75, 1.1], ['순차번호', '관측소', '승인일', '방류 시작', '방류량'], [['2755', '충주', '2017-08-24', '2017-08-25 14:00', '2000']], { fs: 11.5, hh: 0.32, rh: 0.36 });
  rect(s, 0.55, 3.13, 0.95, 0.42, 'E5E7EB', 'B6BCC6'); T(s, '비고', { x: 0.55, y: 3.13, w: 0.95, h: 0.42, fontSize: 11.5, bold: true, align: 'center', valign: 'middle' });
  rect(s, 1.5, 3.13, 4.95, 0.42, WHITE, 'B6BCC6'); T(s, '최대 2000㎥/s 이내 탄력적방류(초기 1500㎥/s 이내 방류)', { x: 1.56, y: 3.13, w: 4.85, h: 0.42, fontSize: 11, valign: 'middle' });
  // 자료 2: 규정
  T(s, '연계운영규정 별표 3', { x: 0.55, y: 4.0, w: 4, h: 0.28, fontSize: 12.5, bold: true, color: NAVY });
  const t2 = mini(s, 0.55, 4.3, [1.2, 1.6, 2.0], ['수계', '댐명', '홍수기 제한수위'], [['한강', '충주댐', '138.0 EL.m']], { fs: 11.5, hh: 0.32, rh: 0.36 });
  // 자료 3: 측정값
  T(s, '시간 측정값', { x: 0.55, y: 5.35, w: 4, h: 0.28, fontSize: 12.5, bold: true, color: NAVY });
  const t3 = mini(s, 0.55, 5.65, [1.35, 1.75, 0.95, 0.95, 0.9], ['관측소 코드', '시각', '수위', '유입량', '…'], [['1003110', '2020-08-02 18:00', '139.55', '4945.2', '…']], { fs: 11.5, hh: 0.32, rh: 0.36 });
  // Class 6개
  const cls = [['댐', NAVY, '충주댐'], ['방류 승인', C_APR, '승인 2755 · 2017-08-24 · 2000㎥/s'], ['운영행위', C_OPR, '초기방류, 탄력적 방류 · 2017-08-25 14:00'], ['근거', C_EVI, '승인 기록 2755번 행 · 규정 별표 3'], ['운영기준', C_CRI, '홍수기 제한수위 138.0 EL.m'], ['수문·기상 상태', C_HMS, '수위 등 6개 항목 · 관측소 코드 1003110']];
  const R = cls.map((c, i) => { const y = 2.15 + i * 0.76; box(s, 8.35, y, 4.43, 0.64, { fill: WHITE, line: c[1], lw: 1.25 }); box(s, 8.35, y, 1.55, 0.64, { fill: c[1] });
    T(s, c[0], { x: 8.35, y, w: 1.55, h: 0.64, fontSize: 12.5, bold: true, color: WHITE, align: 'center', valign: 'middle' }); T(s, c[2], { x: 10.0, y, w: 2.72, h: 0.64, fontSize: 11, valign: 'middle' }); return [8.35, y + 0.32]; });
  const from1 = [6.5, 3.0], from2 = [5.4, 4.64], from3 = [6.5, 5.99];
  [0, 1, 2, 3].forEach(i => line(s, from1, R[i], null, { color: GRAY, width: 1.5 }));
  line(s, from2, R[3], null, { color: GRAY, width: 1.5 }); line(s, from2, R[4], null, { color: GRAY, width: 1.5 }); line(s, from3, R[5], null, { color: GRAY, width: 1.5 });
  T(s, '비고의 "초기방류", "탄력적 방류"가 운영행위가 된다.  측정값 자체는 KG에 넣지 않고 측정 저장소에 둔다(다음 장)', { x: 0.55, y: 6.68, w: 12.2, h: 0.3, fontSize: 12, color: GRAY });
}
// 10. 외부 저장소
{
  const s = add('Ⅰ. 만든 구조'); head(s, 'Ⅰ. 만든 구조', '외부 저장소', '양이 많은 측정값과 긴 규정 원문은 KG 밖에 두고, KG에는 찾아갈 열쇠만 둔다');
  box(s, 0.55, 1.9, 4.75, 4.85, { fill: SKY }); T(s, '지식그래프 (KG)', { x: 0.8, y: 2.02, w: 4.2, h: 0.4, fontSize: 16, bold: true, color: NAVY });
  const dam = node(s, 0.8, 2.75, 1.6, 0.9, '충주댐', null, { fs: 15 }), hms = node(s, 2.9, 2.75, 2.15, 0.9, '수위', '열쇠: 관측소 코드 1003110', { fill: C_HMS, fs: 15, fs2: 10 });
  const cri = node(s, 0.8, 4.95, 1.6, 0.9, '제한수위', '138.0 EL.m', { fill: C_CRI, fs: 15, fs2: 10 }), evi = node(s, 2.9, 4.95, 2.15, 0.9, '근거', '열쇠: 별표 3', { fill: C_EVI, fs: 15, fs2: 10 });
  link(s, dam, hms, null); link(s, cri, dam, null); link(s, cri, evi, null);
  // 측정 저장소
  s.addShape(pres.ShapeType.can, { x: 7.3, y: 2.05, w: 1.5, h: 1.75, fill: { color: C_HMS }, line: { color: C_HMS, width: 0.75 } });
  T(s, '측정\n저장소', { x: 7.3, y: 2.55, w: 1.5, h: 1.0, fontSize: 15, bold: true, color: WHITE, align: 'center', valign: 'middle' });
  mini(s, 9.1, 2.1, [1.75, 0.95, 0.98], ['시각', '수위', '유입량'], [['2020-08-02 17:00', '139.37', '4693.7'], ['2020-08-02 18:00', '139.55', '4945.2'], ['2020-08-02 19:00', '139.69', '4015.5']], { fs: 11.5, hh: 0.34, rh: 0.36, hl: 1 });
  T(s, '시간 측정값 약 87만 행', { x: 9.1, y: 3.6, w: 3.7, h: 0.3, fontSize: 12, color: GRAY });
  line(s, [5.05, 3.2], [7.3, 3.0], null, { color: C_HMS });
  T(s, '관측소 코드와 시각으로 찾음', { x: 5.2, y: 2.55, w: 2.0, h: 0.5, fontSize: 11.5, bold: true, color: C_HMS, align: 'center', valign: 'bottom' });
  // 문서 저장소
  s.addShape(pres.ShapeType.can, { x: 7.3, y: 4.45, w: 1.5, h: 1.75, fill: { color: C_EVI }, line: { color: C_EVI, width: 0.75 } });
  T(s, '문서\n저장소', { x: 7.3, y: 4.95, w: 1.5, h: 1.0, fontSize: 15, bold: true, color: WHITE, align: 'center', valign: 'middle' });
  box(s, 9.1, 4.5, 3.68, 1.65, { fill: WHITE, line: 'B6BCC6', r: 0.03 });
  T(s, [{ text: '[별표 3] 댐의 홍수기 제한수위', options: { bold: true, breakLine: true } }, { text: '한강 수계  다목적댐', options: { breakLine: true } }, { text: '소양강댐 190.3 / 충주댐 138.0 / 횡성댐 178.2' }], { x: 9.25, y: 4.55, w: 3.4, h: 1.55, fontSize: 11.5, valign: 'middle', lineSpacingMultiple: 1.35 });
  T(s, '규정 원문', { x: 9.1, y: 6.2, w: 3.7, h: 0.3, fontSize: 12, color: GRAY });
  line(s, [5.05, 5.4], [7.3, 5.4], null, { color: C_EVI });
  T(s, '문서 위치로 찾음', { x: 5.2, y: 4.95, w: 2.0, h: 0.35, fontSize: 11.5, bold: true, color: GRAY, align: 'center', valign: 'bottom' });
}
// 11. 완성된 KG (전체 그림)
{
  const s = add('Ⅰ. 만든 구조'); head(s, 'Ⅰ. 만든 구조', '완성된 KG', '댐 4개의 Entity와 관계 전체. 점 하나가 Entity, 선 하나가 관계다');
  s.addImage({ path: KGPIC, x: 0.55, y: 1.75, w: 12.23, h: 3.575 });
  const lg = [['댐', NAVY, 4], ['수문·기상 상태', C_HMS, 24], ['운영기준', C_CRI, 3], ['방류 승인', C_APR, 80], ['운영행위', C_OPR, 68], ['근거', '9AA5B1', 85]];
  box(s, 0.55, 5.5, 12.23, 1.25, { fill: PALE, line: LINE });
  lg.forEach((l, i) => { const x = 0.85 + i * 1.98;
    s.addShape(pres.ShapeType.ellipse, { x, y: 5.72, w: 0.26, h: 0.26, fill: { color: l[1] }, line: { color: l[1], width: 0.5 } });
    T(s, l[0], { x: x + 0.36, y: 5.67, w: 1.6, h: 0.36, fontSize: 13, bold: true, color: NAVY, valign: 'middle' }); T(s, l[2] + '개', { x: x + 0.36, y: 6.03, w: 1.6, h: 0.3, fontSize: 12, color: GRAY }); });
  T(s, 'Entity 264개, 관계 418개.  가운데 큰 점이 댐이고, 바깥으로 갈수록 방류 승인 → 운영행위 → 근거 순서로 이어진다', { x: 0.85, y: 6.38, w: 11.7, h: 0.3, fontSize: 11.5, color: GRAY });
}
// 12. RAG
{
  const s = add('Ⅰ. 만든 구조'); head(s, 'Ⅰ. 만든 구조', 'KG는 RAG로 LLM에 쓰인다', null);
  box(s, 0.55, 1.4, 12.23, 0.95, { fill: NAVY });
  T(s, [{ text: 'RAG (Retrieval-Augmented Generation, 검색 증강 생성)', options: { bold: true, color: WHITE, fontSize: 17, breakLine: true } }, { text: 'LLM이 답하기 전에 관련 근거를 먼저 찾아서 질문과 함께 주는 방식. LLM은 받은 근거 안에서만 답을 쓴다', options: { color: 'DCE9F7', fontSize: 13.5 } }],
    { x: 0.85, y: 1.4, w: 11.7, h: 0.95, valign: 'middle', lineSpacingMultiple: 1.2 });
  T(s, 'LLM만 쓸 때', { x: 0.55, y: 2.55, w: 5, h: 0.35, fontSize: 15, bold: true, color: GRAY });
  box(s, 0.55, 2.93, 12.23, 1.35, { fill: PALE, line: LINE });
  const q1 = node(s, 0.9, 3.18, 2.4, 0.85, '질문', null, { fill: WHITE, line: GRAY, color: INK }), l1 = node(s, 5.4, 3.18, 2.4, 0.85, 'LLM', '학습한 내용으로만 답함', { fill: GRAY, fs2: 11 }), a1 = node(s, 9.9, 3.18, 2.55, 0.85, '답변', '근거를 알 수 없음', { fill: WHITE, line: GRAY, color: INK, color2: ORANGE, fs2: 12 });
  link(s, q1, l1, null, { color: GRAY }); link(s, l1, a1, null, { color: GRAY });
  T(s, 'RAG를 쓸 때 (이번에 만든 구조)', { x: 0.55, y: 4.48, w: 6, h: 0.35, fontSize: 15, bold: true, color: NAVY });
  box(s, 0.55, 4.86, 12.23, 1.9, { fill: SKY });
  const q2 = node(s, 0.9, 5.36, 1.9, 0.9, '질문', null, { fill: WHITE, line: BLUE, color: NAVY }), k2 = node(s, 3.6, 5.16, 2.9, 1.3, 'KG와 저장소에서\n근거 찾기', null, { fill: BLUE, fs: 15 }), l2 = node(s, 7.3, 5.36, 2.0, 0.9, 'LLM', '질문 + 근거', { fill: NAVY, fs2: 11 }), a2 = node(s, 10.1, 5.16, 2.4, 1.3, '답변', '근거와 출처 번호가\n함께 나옴', { fill: WHITE, line: BLUE, color: NAVY, color2: BLUE, fs2: 12 });
  link(s, q2, k2, null); link(s, k2, l2, null); link(s, l2, a2, null);
}

// ================================================= Ⅱ. 시연
pres.addSection({ title: 'Ⅱ. 시연' });
// 13. 시연 범위
{
  const s = add('Ⅱ. 시연'); head(s, 'Ⅱ. 시연', '시연에서 보여 드릴 질문', '정한 범위(CQ) 안의 질문에 답하고, 범위 밖의 질문에는 답하지 않는다');
  const q = [['CQ1', '충주댐 지금 상황 알려줘'], ['CQ2', '2020년 8월 2일 18시 충주댐 수위는?'], ['CQ3', '2011년 7월 충주댐 방류 조작 기록 알려줘'], ['CQ4', '2020년 8월 충주댐 방류 승인이 어떻게 바뀌었는지 정리해줘'], ['CQ5', '충주댐 홍수기 제한수위는 얼마야?'], ['CQ6', '충주댐 제한수위 근거 규정이 뭐야?']];
  q.forEach((c, i) => { const y = 1.9 + i * 0.54; if (i % 2 === 0) rect(s, 0.55, y, 7.6, 0.54, PALE);
    chip(s, 0.7, y + 0.1, 0.85, c[0], { fs: 11 }); T(s, c[1], { x: 1.75, y, w: 6.3, h: 0.54, fontSize: 14.5, valign: 'middle' }); });
  T(s, '관계를 이어서 찾는 질문', { x: 0.55, y: 5.3, w: 7.6, h: 0.32, fontSize: 13, bold: true, color: ORANGE });
  const m = [['CQ1+5', '충주댐 지금 수위가 홍수기 제한수위보다 높아?'], ['CQ3→2', '2011년 7월 충주댐 방류 조작 시점마다 수위와 유입량은?']];
  m.forEach((c, i) => { const y = 5.66 + i * 0.54; rect(s, 0.55, y, 7.6, 0.54, 'FDF3EA');
    chip(s, 0.7, y + 0.1, 0.95, c[0], { fs: 11, fill: ORANGE }); T(s, c[1], { x: 1.8, y, w: 6.3, h: 0.54, fontSize: 14.5, valign: 'middle' }); });
  box(s, 8.5, 1.9, 4.28, 2.3, { fill: SKY });
  T(s, '답변의 모양', { x: 8.75, y: 2.05, w: 3.8, h: 0.4, fontSize: 16, bold: true, color: NAVY });
  T(s, [{ text: '근거', options: { bold: true, color: BLUE } }, { text: '  KG와 저장소에서 찾은 값', options: { breakLine: true } }, { text: '판단', options: { bold: true, color: BLUE } }, { text: '  근거를 비교·정리한 문장', options: { breakLine: true } }, { text: '출처 번호', options: { bold: true, color: BLUE } }, { text: '  누르면 원문이 열림' }], { x: 8.75, y: 2.55, w: 3.8, h: 1.45, fontSize: 14, lineSpacingMultiple: 1.45 });
  box(s, 8.5, 4.4, 4.28, 2.34, { fill: PALE, line: LINE });
  T(s, '범위 밖 (답하지 않음)', { x: 8.75, y: 4.55, w: 3.8, h: 0.4, fontSize: 16, bold: true, color: GRAY });
  T(s, '4개 댐이 아닌 댐\n예측, 수문 개도, 하류 수위\n방류 사유, 절차\n조건을 주고 사례를 찾는 질문', { x: 8.75, y: 5.05, w: 3.8, h: 1.55, fontSize: 14, lineSpacingMultiple: 1.3 });
}
// 14. 시연 영상
{
  const s = add('Ⅱ. 시연'); head(s, 'Ⅱ. 시연', '시연 영상', null);
  box(s, 1.9, 1.6, 9.55, 5.2, { fill: '1F2937', r: 0.05 });
  T(s, '시연 영상 넣는 자리', { x: 1.9, y: 3.7, w: 9.55, h: 0.6, fontSize: 24, bold: true, color: WHITE, align: 'center' });
  T(s, '삽입 > 비디오 > 이 디바이스 (파일로 넣어 인터넷 없이 재생)', { x: 1.9, y: 4.4, w: 9.55, h: 0.4, fontSize: 14, color: '9CA3AF', align: 'center' });
}

// ================================================= Ⅲ. 한계와 향후 방향
pres.addSection({ title: 'Ⅲ. 한계와 향후 방향' });
// 15. 한계 (크게)
{
  const s = add('Ⅲ. 한계와 향후 방향'); head(s, 'Ⅲ. 한계와 향후 방향', '지금 구조의 한계', '기본 틀을 만든 단계이며, 아래 세 가지가 남아 있다');
  const lim = [['①', '정한 범위 안에서만 답한다', '처음에 정한 질문(CQ) 6개와\n댐 4개의 자료 안에서만 답하고,\n그 밖의 질문에는 답하지 못한다'], ['②', '판단하는 문장의 품질이\n고르지 않다', '범용 LLM을 그대로 써서,\n근거를 찾는 것은 정확하지만\n해석·판단하는 문장은 거칠 때가 있다'], ['③', '저장해 둔 자료로 답한다', '실시간 자료와 이어져 있지 않아,\n"지금"은 저장된 마지막 시각의\n값이다']];
  lim.forEach((l, i) => { const x = 0.55 + i * 4.18;
    box(s, x, 1.95, 3.9, 4.7, { fill: SKY });
    T(s, l[0], { x: x + 0.35, y: 2.2, w: 1, h: 0.8, fontSize: 40, bold: true, color: BLUE });
    T(s, l[1], { x: x + 0.35, y: 3.2, w: 3.3, h: 1.0, fontSize: 21, bold: true, color: NAVY, valign: 'middle', lineSpacingMultiple: 1.15 });
    T(s, l[2], { x: x + 0.35, y: 4.5, w: 3.3, h: 1.8, fontSize: 15, color: INK, lineSpacingMultiple: 1.35 }); });
}
// 16. 향후 방향
{
  const s = add('Ⅲ. 한계와 향후 방향'); head(s, 'Ⅲ. 한계와 향후 방향', '향후 방향', '만들어 둔 기본 틀 위에 모듈을 하나씩 더해 고도화한다');
  const it = [['범위 확장', '실무자와 전문가의 자문을 받아 질문(CQ)을 보완하고, 그에 맞춰 온톨로지의 Class와 관계를 넓힌다', '댐, 자료 종류, 질문 유형을 단계적으로 늘린다'],
    ['실시간 자료 연계', '저장해 둔 자료 대신 운영 자료를 바로 가져오게 한다', '"지금"이 실제 현재 값이 된다'],
    ['에이전트', '질문에 따라 필요한 도구(KG 검색, 측정값 조회, 비슷한 사례 찾기)를 LLM이 골라 이어서 쓴다', '상황을 알려 주고 비슷한 과거 사례를 묻는 질문에 답한다'],
    ['LLM 고도화', '댐 운영 분야에 맞춘 모델을 쓰고, 분야 자료로 성능을 높인다', '해석·판단하는 문장의 품질을 높인다']];
  it.forEach((x, i) => { const X = 0.55 + i * 3.11;
    box(s, X, 1.95, 2.9, 4.75, { fill: SKY }); box(s, X, 1.95, 2.9, 0.95, { fill: NAVY });
    T(s, x[0], { x: X + 0.25, y: 1.95, w: 2.4, h: 0.95, fontSize: 19, bold: true, color: WHITE, valign: 'middle' });
    T(s, x[1], { x: X + 0.25, y: 3.1, w: 2.4, h: 1.8, fontSize: 13, color: INK, lineSpacingMultiple: 1.3 });
    s.addShape(pres.ShapeType.line, { x: X + 0.25, y: 5.05, w: 2.4, h: 0, line: { color: LINE, width: 1 } });
    T(s, '기대 효과', { x: X + 0.25, y: 5.18, w: 2.4, h: 0.3, fontSize: 11.5, bold: true, color: BLUE });
    T(s, x[2], { x: X + 0.25, y: 5.5, w: 2.4, h: 1.1, fontSize: 13, color: NAVY, bold: true, lineSpacingMultiple: 1.25 }); });
}
// 17. 끝
{
  const s = pres.addSlide({ sectionTitle: 'Ⅲ. 한계와 향후 방향' }); s.background = { color: NAVY };
  T(s, '감사합니다', { x: 0.55, y: 3.0, w: 12.23, h: 0.9, fontSize: 40, bold: true, color: WHITE, align: 'center' });
  T(s, '질문과 의견을 부탁드립니다', { x: 0.55, y: 4.0, w: 12.23, h: 0.5, fontSize: 18, color: '9DBEDD', align: 'center' });
}
pres.writeFile({ fileName: OUT }).then(f => console.log('saved', f));
