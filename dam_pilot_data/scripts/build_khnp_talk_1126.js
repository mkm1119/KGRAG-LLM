// 11/26 한강수력본부 발표자료 초안(pptx). 구성: 구조(온톨로지 → CQ → Class·속성·관계 → KG → 자료 → 외부 저장소 → RAG) → 시연 범위 → 시연 영상 → 한계와 향후 방향.
// 모양은 7월 기술 세미나 자료(로고 위치, 남색·파랑, KoPubWorld돋움체)를 따른다. 숫자와 예시 값은 03_normalized의 KG(kgv4), 승인 기록, 측정 저장소에서 가져온 값이다.
// 사용: node build_khnp_talk_1126.js <출력.pptx> <khnp 로고.jpg> <kmu 로고.jpg> <KG 전체 그림.png> <표지 그림.png>
let pptxgen; try { pptxgen = require('pptxgenjs'); } catch (e) { pptxgen = require('./mini_pptx.js'); }  // pptxgenjs가 없으면 같은 폴더의 대체 모듈을 쓴다
const [OUT, KHNP, KMU, KGPIC, COVER] = process.argv.slice(2);
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
function mini(s, x, y, widths, headRow, rows, o = {}) {   // hl: 색칠할 행 번호(들), cfs: 열마다 다른 글자 크기
  const hh = o.hh || 0.36, rh = o.rh || 0.36, fs = o.fs || 12, hls = [].concat(o.hl ?? []); let cx = x;
  widths.forEach((w, i) => { rect(s, cx, y, w, hh, 'E5E7EB', 'B6BCC6'); T(s, headRow[i], { x: cx, y, w, h: hh, fontSize: fs, bold: true, align: 'center', valign: 'middle' });
    rows.forEach((r, k) => { const hl = hls.includes(k); rect(s, cx, y + hh + k * rh, w, rh, hl ? 'FFF4D6' : WHITE, 'B6BCC6'); T(s, r[i], { x: cx + 0.03, y: y + hh + k * rh, w: w - 0.06, h: rh, fontSize: (o.cfs && o.cfs[i]) || fs, align: 'center', valign: 'middle', bold: hl }); });
    cx += w; });
  return { x, y, w: widths.reduce((a, b) => a + b, 0), h: hh + rows.length * rh };
}
const add = sec => pres.addSlide({ masterName: 'CONTENT', sectionTitle: sec });

// ================================================= 1. 표지
pres.addSection({ title: '표지' });
{
  const s = pres.addSlide({ sectionTitle: '표지' }); s.background = { color: WHITE };
  s.addImage({ path: KHNP, x: 7.73, y: 0.18, w: 3.27, h: 0.47 }); s.addImage({ path: KMU, x: 11.1, y: 0.03, w: 2.21, h: 0.74 });
  s.addImage({ path: COVER, x: 0, y: 0.9, w: 5.2, h: 6.6 });   // 댐과 지식그래프를 그린 그림(fig/cover_dam.svg). 사진으로 바꿀 때는 이 자리에 넣는다
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
  const s = add('순서'); head(s, '발표 순서', '오늘 말씀드릴 내용', '연구 프레임워크를 간단히 설명드리고, 시연 테스트 영상을 보여 드립니다');
  const items = [['Ⅰ', '연구 프레임워크', '온톨로지와 지식그래프로\n자료를 잇고, 근거를 찾아 답하는 구조'], ['Ⅱ', '시연 테스트', '정한 범위의 질문에\n근거와 출처를 붙여 답하는 모습'], ['Ⅲ', '한계와 향후 방향', '지금 구조의 한계와\n다음 단계']];
  items.forEach((it, i) => { const x = 0.55 + i * 4.18;
    box(s, x, 2.0, 3.9, 4.5, { fill: i === 0 ? NAVY : SKY });
    T(s, it[0], { x: x + 0.4, y: 2.45, w: 1, h: 0.8, fontSize: 40, bold: true, color: i === 0 ? '9DBEDD' : BLUE });
    T(s, it[1], { x: x + 0.4, y: 3.6, w: 3.3, h: 0.55, fontSize: 26, bold: true, color: i === 0 ? WHITE : NAVY });
    T(s, it[2], { x: x + 0.4, y: 4.45, w: 3.3, h: 1.4, fontSize: 16, color: i === 0 ? 'DCE9F7' : INK, lineSpacingMultiple: 1.3 });
  });
}

// ================================================= Ⅰ. 구조
pres.addSection({ title: 'Ⅰ. 연구 프레임워크' });
// 3. 온톨로지: 구성요소 세 가지를 한 그림에서
{
  const s = add('Ⅰ. 연구 프레임워크'); head(s, 'Ⅰ. 연구 프레임워크', '온톨로지란', '어떤 분야에 무엇이 있고, 각각 어떤 특징을 가지며, 서로 어떻게 이어지는지를 정해 둔 설계도');
  const comp = [['Class', NAVY, '다루는 대상의 종류', '예: 댐, 방류 승인, 운영행위'], ['속성', C_HMS, 'Class를 설명하는 항목', '예: 방류 승인의 승인일, 승인 내용'], ['관계', ORANGE, 'Class와 Class를 잇는 선', '예: 방류 승인이 운영행위를 허가함']];
  T(s, '온톨로지의 구성요소', { x: 0.55, y: 1.9, w: 4.0, h: 0.35, fontSize: 14, bold: true, color: GRAY });
  comp.forEach((c, i) => { const y = 2.3 + i * 1.47;
    box(s, 0.55, y, 4.1, 1.32, { fill: PALE, line: LINE }); chip(s, 0.75, y + 0.2, 1.05, c[0], { fill: c[1], fs: 13, h: 0.38 });
    T(s, c[2], { x: 1.95, y: y + 0.2, w: 2.6, h: 0.38, fontSize: 15, bold: true, color: NAVY, valign: 'middle' });
    T(s, c[3], { x: 0.75, y: y + 0.75, w: 3.8, h: 0.4, fontSize: 13, color: GRAY, valign: 'middle' }); });
  box(s, 4.95, 2.3, 7.83, 4.26, { fill: SKY });
  T(s, '예: 방류 승인 기록을 온톨로지로 나타내면', { x: 4.95, y: 1.9, w: 7.8, h: 0.35, fontSize: 14, bold: true, color: GRAY });
  const A = node(s, 5.35, 2.75, 2.5, 0.85, '      방류 승인'), B = node(s, 9.85, 2.75, 2.5, 0.85, '운영행위'), D = node(s, 7.6, 5.1, 2.5, 0.85, '댐');
  const prop = (x, y, t) => { box(s, x, y, 2.5, 0.62, { fill: WHITE, line: C_HMS }); T(s, t, { x, y, w: 2.5, h: 0.62, fontSize: 12.5, color: INK, align: 'center', valign: 'middle' }); };
  prop(5.35, 3.6, '        승인일, 승인 내용'); prop(9.85, 3.6, '종류, 시각'); prop(7.6, 5.95, '이름, 종류');
  link(s, A, B, '허가함', { lw: 1.0, fs: 13 });
  line(s, [6.6, 4.22], [7.9, 5.1], '대상', { lw: 0.8, fs: 13, side: -1, off: 0.3 }); line(s, [11.1, 4.22], [9.8, 5.1], '수행됨', { lw: 1.0, fs: 13, off: 0.4 });
  chip(s, 5.43, 3.02, 0.62, 'Class', { fill: WHITE, color: NAVY, fs: 11, h: 0.3 }); chip(s, 5.43, 3.76, 0.62, '속성', { fill: C_HMS, fs: 11, h: 0.3 }); chip(s, 8.5, 2.5, 0.75, '관계', { fill: ORANGE, fs: 11, h: 0.3 });
}
// 4. CQ (랩미팅 자료의 CQ 원문)
{
  const s = add('Ⅰ. 연구 프레임워크'); head(s, 'Ⅰ. 연구 프레임워크', '온톨로지 구축의 첫 단계: CQ', '온톨로지는 모든 것을 담지 않는다. 먼저 답해야 할 질문을 정하고, 그 질문에 필요한 만큼만 만든다');
  box(s, 0.55, 1.85, 12.23, 0.85, { fill: NAVY });
  T(s, [{ text: 'CQ (Competency Question)  ', options: { bold: true, color: WHITE, fontSize: 18 } }, { text: '온톨로지가 답할 수 있어야 하는 질문.  만들기 전에 정하고, 만든 뒤에는 이 질문에 답이 되는지로 확인한다', options: { color: 'DCE9F7', fontSize: 12.5 } }],
    { x: 0.85, y: 1.85, w: 11.7, h: 0.85, valign: 'middle' });
  const cq = [['CQ1', '현재 수문·기상 상태', '대상 댐의 현재 또는 기준시점의 강우, 수위, 유입량, 방류량 등 수문·기상 상태는 무엇인가?'],
    ['CQ2', '과거 수문·기상 상태', '선택된 과거 시점 또는 사례에서 대상 댐의 강우, 수위, 유입량, 방류량 등 수문·기상 상태는 어떠했는가?'],
    ['CQ3', '과거 운영행위', '해당 과거 시점 또는 사례에서 실제로 수행된 댐 운영행위는 무엇이었는가?'],
    ['CQ4', '과거 방류 승인', '해당 과거 시점 또는 사례에서 어떤 방류 승인이 있었으며, 그 승인내용은 무엇인가?'],
    ['CQ5', '현재 운영기준', '현재 대상 댐에 적용되는 운영기준은 무엇이며, 현재 운영 판단과 관련된 기준값은 무엇인가?'],
    ['CQ6', '공식 근거', '각 수문·기상 상태, 운영행위, 승인내용 및 운영기준을 확인할 수 있는 공식 자료 또는 근거문서는 무엇인가?']];
  cq.forEach((c, i) => { const y = 2.85 + i * 0.66;
    box(s, 0.55, y, 12.23, 0.58, { fill: i % 2 ? PALE : SKY }); chip(s, 0.75, y + 0.12, 0.85, c[0]);
    T(s, c[1], { x: 1.8, y, w: 2.6, h: 0.58, fontSize: 15.5, bold: true, color: NAVY, valign: 'middle' });
    T(s, c[2], { x: 4.45, y, w: 8.2, h: 0.58, fontSize: 13.5, valign: 'middle' }); });
}
// 5. CQ에서 Class, 그 다음 Class 사이의 관계 (두 단계를 나눠서 보여 준다)
{
  const s = add('Ⅰ. 연구 프레임워크'); head(s, 'Ⅰ. 연구 프레임워크', 'CQ에서 뽑은 Class와 관계', 'CQ가 묻는 대상을 Class로 뽑고, 뽑은 Class 사이를 관계로 잇는다');
  T(s, '① CQ가 묻는 대상 → Class', { x: 0.55, y: 1.78, w: 5.9, h: 0.34, fontSize: 15, bold: true, color: NAVY });
  T(s, '② Class 사이를 잇는 관계   ( Class — 관계 → Class )', { x: 6.75, y: 1.78, w: 6.0, h: 0.34, fontSize: 15, bold: true, color: NAVY });
  const cq = [['CQ1', '현재 수문·기상 상태', '수문·기상 상태', C_HMS], ['CQ2', '과거 수문·기상 상태', '수문·기상 상태', C_HMS], ['CQ3', '과거 운영행위', '운영행위', C_OPR], ['CQ4', '과거 방류 승인', '방류 승인', C_APR], ['CQ5', '현재 운영기준', '운영기준', C_CRI], ['CQ6', '공식 근거', '근거', C_EVI]];
  cq.forEach((r, i) => { const y = 2.18 + i * 0.66;
    box(s, 0.55, y, 5.9, 0.56, { fill: PALE, line: LINE }); chip(s, 0.7, y + 0.11, 0.85, r[0], { fs: 12 });
    T(s, r[1], { x: 1.7, y, w: 2.3, h: 0.56, fontSize: 15, valign: 'middle' });
    line(s, [3.95, y + 0.28], [4.45, y + 0.28], null, { color: GRAY, gap: 0 }); node(s, 4.5, y + 0.07, 1.85, 0.42, r[2], null, { fs: 13.5, fill: r[3] }); });
  box(s, 0.55, 6.14, 5.9, 0.56, { fill: PALE, line: LINE }); T(s, '모든 CQ의 대상', { x: 0.7, y: 6.14, w: 3.2, h: 0.56, fontSize: 15, valign: 'middle', bold: true, color: NAVY });
  line(s, [3.95, 6.42], [4.45, 6.42], null, { color: GRAY, gap: 0 }); node(s, 4.5, 6.21, 1.85, 0.42, '댐', null, { fs: 13.5 });
  const tr = [['댐', NAVY, '상태를 가짐', '수문·기상 상태', C_HMS], ['운영행위', C_OPR, '수행됨', '댐', NAVY], ['방류 승인', C_APR, '대상', '댐', NAVY], ['방류 승인', C_APR, '허가함', '운영행위', C_OPR], ['운영기준', C_CRI, '적용됨', '댐', NAVY], ['상태, 운영행위,\n승인, 기준', GRAY, '근거를 둠', '근거', C_EVI]];
  tr.forEach((r, i) => { const y = 2.18 + i * 0.76;
    box(s, 6.75, y, 6.03, 0.66, { fill: SKY });
    const a = node(s, 6.93, y + 0.08, 2.05, 0.5, r[0], null, { fs: r[0].includes('\n') ? 11.5 : 14.5, fill: r[1] }), b = node(s, 10.55, y + 0.08, 2.05, 0.5, r[3], null, { fs: 14.5, fill: r[4] });
    link(s, a, b, r[2], { lw: 1.5, fs: 13.5, off: 0.17 }); });
}
// 6. 우리 온톨로지 (그림으로 전부)
{
  const s = add('Ⅰ. 연구 프레임워크'); head(s, 'Ⅰ. 연구 프레임워크', '댐 운영 온톨로지 구조', 'Class 6개와 관계 9개');
  const W = 2.65, H = 1.0;
  const dam = node(s, 5.34, 1.85, W, H, '댐', '이름, 종류');
  const cri = node(s, 0.6, 3.6, W, H, '운영기준', '종류, 값, 단위', { fill: C_CRI });
  const apr = node(s, 3.76, 3.6, W, H, '방류 승인', '승인일, 승인 내용', { fill: C_APR });
  const opr = node(s, 6.92, 3.6, W, H, '운영행위', '종류, 시각', { fill: C_OPR });
  const hms = node(s, 10.08, 3.6, W, H, '수문·기상 상태', '항목, 관측소 코드', { fill: C_HMS });
  const evi = node(s, 5.34, 5.4, W, H, '근거', '제목, 종류, 위치', { fill: C_EVI });
  link(s, cri, dam, '적용됨', { lw: 0.9 }); link(s, apr, dam, '대상', { lw: 0.7, off: 0.28 }); link(s, opr, dam, '수행됨', { lw: 0.9, off: 0.33, side: -1 }); link(s, dam, hms, '상태를 가짐', { lw: 1.3 });
  link(s, apr, opr, '허가함', { lw: 0.5, off: 0.17, fs: 10.5 });
  link(s, cri, evi, '근거를 둠', { lw: 1.1, side: -1, off: 0.22 }); link(s, apr, evi, null); link(s, opr, evi, null); link(s, hms, evi, '근거를 둠', { lw: 1.1, side: -1, off: 0.22 });
  T(s, '상자는 Class, 상자 안의 작은 글씨는 속성, 화살표는 관계를 나타낸다', { x: 0.55, y: 6.6, w: 12.23, h: 0.35, fontSize: 14, color: GRAY, align: 'center' });
}
// 7. KG
{
  const s = add('Ⅰ. 연구 프레임워크'); head(s, 'Ⅰ. 연구 프레임워크', '지식그래프(KG)란', '온톨로지라는 틀에 실제 자료를 채워 넣은 것');
  T(s, '온톨로지  (Class와 관계)', { x: 0.55, y: 1.85, w: 5.4, h: 0.4, fontSize: 16, bold: true, color: GRAY, align: 'center' });
  box(s, 0.55, 2.3, 5.4, 3.7, { fill: PALE, line: LINE });
  const a1 = node(s, 0.9, 3.0, 1.95, 0.9, '방류 승인', null, { fill: WHITE, line: BLUE, color: BLUE }), b1 = node(s, 3.65, 3.0, 1.95, 0.9, '운영행위', null, { fill: WHITE, line: BLUE, color: BLUE }), d1 = node(s, 2.27, 4.7, 1.95, 0.9, '댐', null, { fill: WHITE, line: BLUE, color: BLUE });
  link(s, a1, b1, '허가함', { lw: 0.8, off: 0.18 }); link(s, b1, d1, '수행됨', { lw: 0.8, side: -1, off: 0.35 }); link(s, a1, d1, '대상', { lw: 0.6, off: 0.3 });
  chip(s, 0.9, 2.55, 0.8, 'Class', { fill: BLUE, fs: 11.5, h: 0.32 });
  line(s, [6.1, 4.15], [7.25, 4.15], null, { color: NAVY, width: 3, gap: 0 }); T(s, '실제 자료를\n채움', { x: 5.95, y: 4.3, w: 1.45, h: 0.6, fontSize: 12, color: NAVY, bold: true, align: 'center' });
  T(s, '지식그래프  (Entity와 관계)', { x: 7.4, y: 1.85, w: 5.4, h: 0.4, fontSize: 16, bold: true, color: NAVY, align: 'center' });
  box(s, 7.4, 2.3, 5.4, 3.7, { fill: SKY, line: SKY2 });
  const a2 = node(s, 7.65, 2.95, 2.2, 1.05, '승인 3412', '2020-08-02\n승인량 3000㎥/s', { fs: 14, fs2: 10 }), b2 = node(s, 10.35, 2.95, 2.2, 1.05, '방류', '2020-08-02 18:00', { fs: 14, fs2: 10 }), d2 = node(s, 9.0, 4.7, 2.2, 0.95, '충주댐', '다목적댐', { fs: 14, fs2: 10 });
  link(s, a2, b2, '허가함', { lw: 0.8, off: 0.7 }); link(s, b2, d2, '수행됨', { lw: 0.8, side: -1, off: 0.35 }); link(s, a2, d2, '대상', { lw: 0.6, off: 0.3 });
  chip(s, 7.65, 2.5, 0.85, 'Entity', { fill: NAVY, fs: 11.5, h: 0.32 });
  box(s, 0.55, 6.15, 12.23, 0.62, { fill: NAVY });
  T(s, 'Entity: Class에 실제 자료가 들어간 하나하나.   방류 승인(Class) → 승인 3412(Entity),   댐(Class) → 충주댐(Entity)', { x: 0.55, y: 6.15, w: 12.23, h: 0.62, fontSize: 15, bold: true, color: WHITE, align: 'center', valign: 'middle' });
}
// 8. 자료 (원본의 모양 그대로)
{
  const s = add('Ⅰ. 연구 프레임워크'); head(s, 'Ⅰ. 연구 프레임워크', 'KG에 채운 실제 자료', 'K-water 댐 4개(충주댐, 소양강댐, 횡성댐, 광동댐)의 공개 자료 세 종류');
  const lab = (x, y, a, b) => s.addText([{ text: a, options: { bold: true, color: NAVY, fontSize: 16 } }, { text: '   ' + b, options: { color: GRAY, fontSize: 12 } }], { x, y, w: 7.6, h: 0.36, fontFace: F, margin: 0, isTextBox: true, valign: 'middle' });
  lab(0.55, 1.8, '시간 측정값', 'K-water 공개 자료 (표 형식)');
  mini(s, 0.55, 2.2, [1.6, 0.95, 1.05, 0.95, 1.05, 1.05, 0.95], ['시각', '수위\n(EL.m)', '저수량\n(백만㎥)', '강우량\n(mm)', '유입량\n(㎥/s)', '총방류량\n(㎥/s)', '저수율\n(%)'],
    [['2020-08-02 17:00', '139.37', '2111.215', '0.711', '4693.654', '707.265', '76.8'], ['2020-08-02 18:00', '139.55', '2126.472', '1.901', '4945.201', '707.145', '77.3'], ['2020-08-02 19:00', '139.69', '2138.381', '0.273', '4015.509', '707.453', '77.8']], { fs: 11.5, hh: 0.5, rh: 0.34 });
  T(s, '충주댐 예시.  1시간마다 6개 항목, 2010~2026년, 약 87만 행', { x: 0.55, y: 3.76, w: 7.6, h: 0.3, fontSize: 12.5, color: INK });
  lab(0.55, 4.2, '방류 승인 기록', '한강홍수통제소 공개 자료 (표 형식)');
  mini(s, 0.55, 4.6, [0.75, 0.75, 1.1, 1.2, 0.85, 2.95], ['순차번호', '관측소명', '승인년월일시분', '방류시작시간', '접수방류량', '비고'],
    [['3412', '충주', '2020-08-02', '2020-08-02 18:00', '3000', ''], ['3519', '충주', '2020-08-06', '2020-08-02 18:00', '7000', '방류기간 (당초) 08/02 18:00 ~ 08/12 18:00 (변경) 08/02 18:00 ~ 08/16 24:00 방류량(당초) 3000㎥/s(변경) 7000㎥/s'], ['3647', '충주', '2020-08-12', '2020-08-06 06:00', '7000', '수문방류 변경승인(방류기간연장) 최대방류량내 탄력적 방류 …']], { fs: 11, hh: 0.36, rh: 0.52, cfs: { 5: 9.5 } });
  T(s, '충주댐 2020년 8월 예시.  댐 4개, 2010~2021년, 80건.  비고는 사람이 쓴 문장이다', { x: 0.55, y: 6.56, w: 7.6, h: 0.3, fontSize: 12.5, color: INK });
  lab(8.5, 1.8, '운영 규정', '규정 문서 (표가 아닌 글)');
  box(s, 8.5, 2.2, 4.28, 4.28, { fill: WHITE, line: 'B6BCC6', r: 0.02 });
  T(s, '댐과 보 등의 연계운영규정', { x: 8.7, y: 2.3, w: 3.9, h: 0.3, fontSize: 11, color: GRAY });
  T(s, '[별표 3] 댐의 홍수기 제한수위(제6조)', { x: 8.7, y: 2.6, w: 3.9, h: 0.34, fontSize: 13, bold: true });
  mini(s, 8.7, 3.05, [0.75, 1.05, 0.95, 1.13], ['구분', '댐 종류', '댐명', '홍수기\n제한수위(EL.m)'], [['한강\n수계', '다목적댐', '소양강댐', '190.3'], ['', '', '충주댐', '138.0'], ['', '', '횡성댐', '178.2'], ['', '수력발전댐', '화천댐', '175.0'], ['', '', '춘천댐', '102.0'], ['', '', '…', '…']], { fs: 11, hh: 0.5, rh: 0.4, hl: [0, 1, 2] });
  T(s, '색칠한 3행(K-water 댐)의 값을 사용.  3건', { x: 8.5, y: 6.56, w: 4.28, h: 0.3, fontSize: 12.5, color: INK });
}
// 9. 자료가 KG가 되는 과정: 랩미팅 자료(구조화 자료 매핑)처럼 '한 행 → Entity' 표로 보여 준다
{
  const s = add('Ⅰ. 연구 프레임워크'); head(s, 'Ⅰ. 연구 프레임워크', '자료가 KG가 되는 과정', '방류 승인 기록 한 행이 Entity가 되는 예 (충주댐, 순차번호 2755)');
  T(s, '원본 한 행', { x: 0.55, y: 1.78, w: 4, h: 0.3, fontSize: 14, bold: true, color: GRAY });
  mini(s, 0.55, 2.1, [1.0, 1.0, 1.55, 1.85, 1.2, 5.63], ['순차번호', '관측소명', '승인년월일시분', '방류시작시간', '접수방류량', '비고'], [['2755', '충주', '2017-08-24', '2017-08-25 14:00', '2000', '최대 2000㎥/s(발전방류 포함)이내 탄력적방류(초기 1500 ㎥/s이내 방류)']], { fs: 12, hh: 0.36, rh: 0.44 });
  T(s, '쓰는 열', { x: 0.55, y: 3.12, w: 3.7, h: 0.3, fontSize: 14, bold: true, color: GRAY });
  T(s, 'Entity (Class)', { x: 4.9, y: 3.12, w: 2.6, h: 0.3, fontSize: 14, bold: true, color: GRAY });
  T(s, 'Entity에 들어간 값 (속성)', { x: 7.75, y: 3.12, w: 5, h: 0.3, fontSize: 14, bold: true, color: GRAY });
  const m = [['관측소명', '충주댐', '댐', NAVY, '이름 = 충주댐'],
    ['승인년월일시분, 방류시작시간,\n접수방류량, 비고', '승인 2755', '방류 승인', C_APR, '승인일 = 2017-08-24\n승인 내용 = 방류시작 2017-08-25 14:00; 2000㎥/s; 비고'],
    ['비고의 문구, 방류시작시간', '초기방류 · 탄력적 방류', '운영행위 2개', C_OPR, '종류 = 초기방류 / 탄력적 방류  (비고에서 찾은 문구)\n시각 = 2017-08-25 14:00'],
    ['순차번호', '근거', '승인 기록', C_EVI, '제목 = 한강홍수통제소 댐방류승인\n위치 = 순차번호 2755']];
  m.forEach((r, i) => { const y = 3.46 + i * 0.7;
    box(s, 0.55, y, 3.7, 0.6, { fill: 'E5E7EB', line: 'B6BCC6', r: 0.03 }); T(s, r[0], { x: 0.65, y, w: 3.5, h: 0.6, fontSize: 12.5, bold: true, align: 'center', valign: 'middle' });
    line(s, [4.27, y + 0.3], [4.88, y + 0.3], null, { color: GRAY, gap: 0 });
    node(s, 4.9, y, 2.6, 0.6, r[1], r[2], { fill: r[3], fs: 13.5, fs2: 10 });
    box(s, 7.75, y, 5.03, 0.6, { fill: WHITE, line: r[3], lw: 1.25, r: 0.03 }); T(s, r[4], { x: 7.9, y, w: 4.8, h: 0.6, fontSize: 11.5, valign: 'middle' }); });
  box(s, 0.55, 6.3, 12.23, 0.58, { fill: SKY });
  s.addText([{ text: 'Entity 사이의 관계   ', options: { bold: true, color: NAVY } }, { text: '승인 2755 ' }, { text: '— 대상 →', options: { color: ORANGE, bold: true } }, { text: ' 충주댐    승인 2755 ' }, { text: '— 허가함 →', options: { color: ORANGE, bold: true } }, { text: ' 운영행위    운영행위 ' }, { text: '— 수행됨 →', options: { color: ORANGE, bold: true } }, { text: ' 충주댐    승인, 운영행위 ' }, { text: '— 근거를 둠 →', options: { color: ORANGE, bold: true } }, { text: ' 근거' }],
    { x: 0.7, y: 6.3, w: 12.0, h: 0.58, fontFace: F, fontSize: 11.5, color: INK, valign: 'middle', margin: 0, isTextBox: true });
}
// 10. 외부 저장소
{
  const s = add('Ⅰ. 연구 프레임워크'); head(s, 'Ⅰ. 연구 프레임워크', '외부 저장소', '양이 많은 측정값과 긴 규정 원문은 KG 밖에 두고, KG에는 찾아갈 열쇠만 둔다');
  box(s, 0.55, 1.9, 4.75, 4.85, { fill: SKY }); T(s, '지식그래프 (KG)', { x: 0.8, y: 2.02, w: 4.2, h: 0.4, fontSize: 16, bold: true, color: NAVY });
  const dam = node(s, 0.8, 2.75, 1.6, 0.9, '충주댐', null, { fs: 15 }), hms = node(s, 2.9, 2.75, 2.15, 0.9, '수위', '열쇠: 관측소 코드 1003110', { fill: C_HMS, fs: 15, fs2: 10 });
  const cri = node(s, 0.8, 4.95, 1.6, 0.9, '제한수위', '138.0 EL.m', { fill: C_CRI, fs: 15, fs2: 10 }), evi = node(s, 2.9, 4.95, 2.15, 0.9, '근거', '열쇠: 별표 3', { fill: C_EVI, fs: 15, fs2: 10 });
  link(s, dam, hms, null); link(s, cri, dam, null); link(s, cri, evi, null);
  // 측정 저장소: 열쇠는 관측소 코드 하나. 시각은 질문에서 뽑아 그 행을 읽는다
  s.addShape(pres.ShapeType.can, { x: 7.3, y: 2.05, w: 1.5, h: 1.75, fill: { color: C_HMS }, line: { color: C_HMS, width: 0.75 } });
  T(s, '측정\n저장소', { x: 7.3, y: 2.55, w: 1.5, h: 1.0, fontSize: 15, bold: true, color: WHITE, align: 'center', valign: 'middle' });
  mini(s, 9.1, 2.1, [1.0, 1.4, 0.6, 0.68], ['관측소 코드', '시각', '수위', '유입량'], [['1003110', '2020-08-02 17:00', '139.37', '4693.7'], ['1003110', '2020-08-02 18:00', '139.55', '4945.2'], ['1003110', '2020-08-02 19:00', '139.69', '4015.5']], { fs: 10.5, hh: 0.34, rh: 0.36 });
  line(s, [5.05, 3.2], [7.3, 3.0], null, { color: C_HMS });
  T(s, '관측소 코드로\n그 댐의 측정값을 찾음', { x: 5.15, y: 2.35, w: 2.1, h: 0.6, fontSize: 11.5, bold: true, color: C_HMS, align: 'center', valign: 'bottom' });
  T(s, '시간 측정값 약 87만 행', { x: 9.1, y: 3.6, w: 3.7, h: 0.3, fontSize: 12, color: GRAY });
  // 문서 저장소
  s.addShape(pres.ShapeType.can, { x: 7.3, y: 4.45, w: 1.5, h: 1.75, fill: { color: C_EVI }, line: { color: C_EVI, width: 0.75 } });
  T(s, '문서\n저장소', { x: 7.3, y: 4.95, w: 1.5, h: 1.0, fontSize: 15, bold: true, color: WHITE, align: 'center', valign: 'middle' });
  box(s, 9.1, 4.5, 3.68, 1.65, { fill: WHITE, line: 'B6BCC6', r: 0.03 });
  T(s, [{ text: '[별표 3] 댐의 홍수기 제한수위', options: { bold: true, breakLine: true } }, { text: '한강 수계  다목적댐', options: { breakLine: true } }, { text: '소양강댐 190.3 / 충주댐 138.0 / 횡성댐 178.2' }], { x: 9.25, y: 4.55, w: 3.4, h: 1.55, fontSize: 11.5, valign: 'middle', lineSpacingMultiple: 1.35 });
  T(s, '규정 원문', { x: 9.1, y: 6.2, w: 3.7, h: 0.3, fontSize: 12, color: GRAY });
  line(s, [5.05, 5.4], [7.3, 5.4], null, { color: C_EVI });
  T(s, '문서 위치로 찾음', { x: 5.2, y: 4.95, w: 2.0, h: 0.35, fontSize: 11.5, bold: true, color: GRAY, align: 'center', valign: 'bottom' });
}
// 11. 완성된 KG: 충주댐 예시 (kgv4의 충주댐 Entity. 승인과 운영행위는 2020년 8월분)
{
  const s = add('Ⅰ. 연구 프레임워크'); head(s, 'Ⅰ. 연구 프레임워크', '완성된 KG: 충주댐 예시', '충주댐에 이어진 Entity와 관계 (방류 승인과 운영행위는 2020년 8월분만 표시)');
  const dam = node(s, 5.5, 3.5, 2.2, 0.95, '충주댐', '다목적댐', { fs: 18, fs2: 11 });
  // 수문·기상 상태 6개
  box(s, 0.55, 1.8, 2.5, 3.72, { fill: 'EAF6F4', line: C_HMS });
  T(s, '수문·기상 상태 · 관측소 코드 1003110', { x: 0.55, y: 1.84, w: 2.5, h: 0.28, fontSize: 9.5, bold: true, color: C_HMS, align: 'center', valign: 'middle' });
  const H = ['수위', '저수량', '강우량', '유입량', '총방류량', '저수율'].map((v, i) => node(s, 0.8, 2.17 + i * 0.55, 2.0, 0.45, v, null, { fill: C_HMS, fs: 13 }));
  H.forEach((h, i) => line(s, [5.5, 3.72 + i * 0.1], [2.8, h.y + 0.225], i === 0 ? '상태를 가짐' : null, { color: C_HMS, width: 1.5, lw: 1.2, fs: 12, off: 0.3, t: 0.3 }));
  const ek = node(s, 0.55, 5.85, 2.5, 0.7, '근거', 'K-water 수문 시간자료', { fill: C_EVI, fs: 13, fs2: 10 });
  line(s, [1.8, 5.52], [1.8, 5.85], null, { color: C_EVI, gap: 0.03 }); T(s, '근거를 둠', { x: 1.95, y: 5.54, w: 1.1, h: 0.28, fontSize: 11, bold: true, color: ORANGE, valign: 'middle' });
  // 운영기준
  const cri = node(s, 5.35, 1.85, 2.5, 0.8, '홍수기 제한수위', '138.0 EL.m', { fill: C_CRI, fs: 14, fs2: 11 });
  const el = node(s, 9.3, 1.85, 3.45, 0.8, '근거', '댐과 보 등의 연계운영규정 별표 3', { fill: C_EVI, fs: 13, fs2: 10 });
  link(s, cri, dam, '적용됨', { lw: 0.9, fs: 12, off: 0.45 }); link(s, cri, el, '근거를 둠', { lw: 1.1, fs: 12, off: 0.18 });
  // 방류 승인 3건, 운영행위 1개
  const A = [['승인 3647', '2020-08-12 · 7000㎥/s', '3647'], ['승인 3519', '2020-08-06 · 7000㎥/s', '3519'], ['승인 3412', '2020-08-02 · 3000㎥/s', '3412']].map((a, i) => {
    const y = 2.95 + i * 0.95, ap = node(s, 8.5, y, 2.15, 0.75, a[0], a[1], { fill: C_APR, fs: 13.5, fs2: 10 }), ev = node(s, 11.2, y, 1.55, 0.75, '근거', '순차번호 ' + a[2], { fill: C_EVI, fs: 12.5, fs2: 9.5 });
    line(s, [8.5, y + 0.375], [7.7, 3.8 + i * 0.17], i === 0 ? '대상' : null, { lw: 0.6, fs: 12, off: 0.2 }); link(s, ap, ev, null, { color: C_EVI }); return [ap, ev]; });
  const op = node(s, 5.5, 5.5, 2.2, 0.85, '방류', '2020-08-02 18:00', { fill: C_OPR, fs: 14, fs2: 10.5 });
  link(s, op, dam, '수행됨', { lw: 0.9, fs: 12, off: 0.48 });
  line(s, [8.5, 5.4], [7.7, 5.75], '허가함', { lw: 0.9, fs: 12, off: 0.22, side: -1 });
  line(s, [7.7, 6.1], [11.9, 5.6], null, { color: C_EVI });
  T(s, '충주댐 전체: 방류 승인 15건, 운영행위 14개.     KG 전체(댐 4개): Entity 264개, 관계 418개', { x: 3.3, y: 6.62, w: 9.48, h: 0.32, fontSize: 13, bold: true, color: NAVY, align: 'right' });
}
// 12. RAG
{
  const s = add('Ⅰ. 연구 프레임워크'); head(s, 'Ⅰ. 연구 프레임워크', 'RAG: KG와 LLM의 연결 방식', null);
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
pres.addSection({ title: 'Ⅱ. 시연 테스트' });
// 13. 시연 질문: CQ와 그에 대응하는 시연 질문을 나란히
{
  const s = add('Ⅱ. 시연 테스트'); head(s, 'Ⅱ. 시연 테스트', '시연 테스트 질문 구성', 'CQ마다 대응하는 질문 1개, 두 CQ를 이어서 묻는 질문 2개');
  rect(s, 0.55, 1.85, 12.23, 0.44, NAVY);
  T(s, 'CQ', { x: 0.55, y: 1.85, w: 5.75, h: 0.44, fontSize: 14, bold: true, color: WHITE, align: 'center', valign: 'middle' }); T(s, '시연 질문', { x: 6.3, y: 1.85, w: 6.48, h: 0.44, fontSize: 14, bold: true, color: WHITE, align: 'center', valign: 'middle' });
  const q = [['CQ1', '대상 댐의 현재 수문·기상 상태는 무엇인가?', '충주댐 지금 상황 알려줘'], ['CQ2', '과거 시점의 수문·기상 상태는 어떠했는가?', '2020년 8월 2일 18시 충주댐 수위는?'], ['CQ3', '과거에 실제로 수행된 운영행위는 무엇이었는가?', '2011년 7월 충주댐 방류 조작 기록 알려줘'],
    ['CQ4', '과거에 어떤 방류 승인이 있었으며, 승인내용은?', '2020년 8월 충주댐 방류 승인이 어떻게 바뀌었는지 정리해줘'], ['CQ5', '현재 적용되는 운영기준과 기준값은 무엇인가?', '충주댐 홍수기 제한수위는 얼마야?'], ['CQ6', '이를 확인할 수 있는 공식 근거는 무엇인가?', '충주댐 제한수위 근거 규정이 뭐야?'],
    ['CQ1+5', '현재 상태와 운영기준을 함께 확인', '충주댐 지금 수위가 홍수기 제한수위보다 높아?'], ['CQ3→2', '운영행위를 찾고, 그 시점의 상태를 확인', '2011년 7월 충주댐 방류 조작 시점마다 수위와 유입량은?']];
  q.forEach((c, i) => { const y = 2.29 + i * 0.555, two = i >= 6; rect(s, 0.55, y, 12.23, 0.555, two ? 'FDF3EA' : (i % 2 ? WHITE : PALE), LINE);
    chip(s, 0.7, y + 0.11, 0.95, c[0], { fs: 11.5, fill: two ? ORANGE : BLUE });
    T(s, c[1], { x: 1.85, y, w: 4.4, h: 0.555, fontSize: 13.5, valign: 'middle' }); T(s, c[2], { x: 6.5, y, w: 6.2, h: 0.555, fontSize: 14.5, bold: true, color: NAVY, valign: 'middle' }); });
}
// 14. 시연 영상
{
  const s = add('Ⅱ. 시연 테스트'); head(s, 'Ⅱ. 시연 테스트', '시연 영상', null);
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
