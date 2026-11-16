// 11/26 한강수력본부 발표자료 초안(pptx). 구성: 구조(온톨로지 → CQ → Class·속성·관계 → KG → 자료 → RAG → 최종 구조) → 시연 범위 → 시연 영상 → 향후 방향.
// 모양은 7월 기술 세미나 자료(로고 위치, 남색·파랑, KoPubWorld돋움체)를 따른다. 숫자는 03_normalized의 KG(kgv4)와 측정 저장소에서 센 값이다.
// 사용: node build_khnp_talk_1126.js <출력.pptx> <khnp 로고.jpg> <kmu 로고.jpg>
let pptxgen; try { pptxgen = require('pptxgenjs'); } catch (e) { pptxgen = require('./mini_pptx.js'); }  // pptxgenjs가 없으면 같은 폴더의 대체 모듈을 쓴다
const [OUT, KHNP, KMU] = process.argv.slice(2);
const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE'; // 13.333 x 7.5
pres.title = '댐 운영 의사결정 프레임워크 구축 자문 용역 - 지식그래프 기반 질의응답 구조와 시연';
const F = 'KoPubWorld돋움체 Medium';
pres.theme = { headFontFace: F, bodyFontFace: F };
const NAVY = '003B71', BLUE = '0070C0', SKY = 'EEF5FC', SKY2 = 'DCE9F7', LINE = 'C9D8E8', GRAY = '6B7280', INK = '2B2B2B', ORANGE = 'C55A11', WHITE = 'FFFFFF', PALE = 'F6F8FB';
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
function node(s, x, y, w, h, title, sub, o = {}) {
  box(s, x, y, w, h, { fill: o.fill || NAVY, line: o.line || o.fill || NAVY, r: o.r });
  s.addText([{ text: title, options: { fontSize: o.fs || 16, bold: true, color: o.color || WHITE, breakLine: !!sub } }].concat(sub ? [{ text: sub, options: { fontSize: o.fs2 || 11, color: o.color2 || 'CFE0F2' } }] : []),
    { x, y, w, h, fontFace: F, align: 'center', valign: 'middle', margin: 0.05, isTextBox: true });
}
function arrow(s, x1, y1, x2, y2, label, o = {}) {
  s.addShape(pres.ShapeType.line, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1), flipH: x2 < x1, flipV: y2 < y1,
    line: { color: o.color || BLUE, width: o.width || 1.75, endArrowType: 'triangle', dashType: o.dash ? 'dash' : 'solid' } });
  if (label) {
    const w = o.lw || 1.5, cx = (x1 + x2) / 2 + (o.dx || 0), cy = (y1 + y2) / 2 + (o.dy || 0);
    s.addText(label, { x: cx - w / 2, y: cy - 0.16, w, h: 0.32, fontFace: F, fontSize: o.fs || 12, color: o.lc || ORANGE, bold: true, align: 'center', valign: 'middle', margin: 0, isTextBox: true, fill: { color: o.bg || WHITE } });
  }
}
const chip = (s, x, y, w, text, o = {}) => { box(s, x, y, w, 0.34, { fill: o.fill || BLUE, r: 0.17 }); T(s, text, { x, y, w, h: 0.34, fontSize: o.fs || 12, bold: true, color: o.color || WHITE, align: 'center', valign: 'middle' }); };
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
  const items = [['Ⅰ', '만든 구조', '온톨로지와 지식그래프로\n자료를 잇고, 근거를 찾아 답하는 구조'], ['Ⅱ', '시연', '정한 범위의 질문에\n근거와 출처를 붙여 답하는 모습'], ['Ⅲ', '향후 방향', '지금 구조의 한계와\n다음 단계']];
  items.forEach((it, i) => { const x = 0.55 + i * 4.18;
    box(s, x, 2.2, 3.9, 3.6, { fill: i === 0 ? NAVY : SKY });
    T(s, it[0], { x: x + 0.35, y: 2.5, w: 1, h: 0.7, fontSize: 36, bold: true, color: i === 0 ? '9DBEDD' : BLUE });
    T(s, it[1], { x: x + 0.35, y: 3.45, w: 3.3, h: 0.5, fontSize: 24, bold: true, color: i === 0 ? WHITE : NAVY });
    T(s, it[2], { x: x + 0.35, y: 4.15, w: 3.3, h: 1.2, fontSize: 15, color: i === 0 ? 'DCE9F7' : INK, lineSpacingMultiple: 1.25 });
  });
}

// ================================================= Ⅰ. 구조
pres.addSection({ title: 'Ⅰ. 만든 구조' });
// 3. 온톨로지
{
  const s = add('Ⅰ. 만든 구조'); head(s, 'Ⅰ. 만든 구조', '온톨로지란', '어떤 것들이 있고, 서로 어떻게 이어지는지를 미리 정해 둔 설계도');
  node(s, 1.2, 3.0, 3.0, 1.3, '댐', 'Class (종류)');
  node(s, 9.1, 3.0, 3.0, 1.3, '운영기준', 'Class (종류)');
  arrow(s, 9.1, 3.65, 4.2, 3.65, '적용된다  (관계)', { lw: 2.3, fs: 14 });
  box(s, 1.2, 4.55, 3.0, 0.95, { fill: PALE, line: LINE }); T(s, [{ text: '속성', options: { bold: true, color: BLUE, breakLine: true } }, { text: '이름, 종류' }], { x: 1.2, y: 4.55, w: 3.0, h: 0.95, fontSize: 14, align: 'center', valign: 'middle' });
  box(s, 9.1, 4.55, 3.0, 0.95, { fill: PALE, line: LINE }); T(s, [{ text: '속성', options: { bold: true, color: BLUE, breakLine: true } }, { text: '종류, 값, 단위' }], { x: 9.1, y: 4.55, w: 3.0, h: 0.95, fontSize: 14, align: 'center', valign: 'middle' });
  const d = [['Class', '다루는 대상의 종류'], ['속성', 'Class를 설명하는 항목'], ['관계', 'Class와 Class를 잇는 선']];
  d.forEach((x, i) => { chip(s, 0.55 + i * 4.18, 6.0, 1.1, x[0]); T(s, x[1], { x: 1.8 + i * 4.18, y: 6.0, w: 2.8, h: 0.34, fontSize: 14, valign: 'middle' }); });
  T(s, '예', { x: 0.55, y: 2.0, w: 1, h: 0.4, fontSize: 14, bold: true, color: GRAY });
  T(s, '"운영기준은 댐에 적용된다"', { x: 1.2, y: 2.0, w: 8, h: 0.4, fontSize: 18, bold: true, color: NAVY });
}
// 4. CQ
{
  const s = add('Ⅰ. 만든 구조'); head(s, 'Ⅰ. 만든 구조', '범위를 정하는 방법: CQ', 'CQ(Competency Question)는 이 구조가 답해야 하는 질문이다. CQ를 정하면 다룰 범위가 정해진다');
  const cq = [['CQ1', '댐의 현재 수문 상태는?'], ['CQ2', '과거 어느 시점의 수문 상태는?'], ['CQ3', '과거에 어떤 방류 조작이 있었나?'], ['CQ4', '과거에 어떤 방류 승인이 있었나?'], ['CQ5', '댐에 적용되는 운영기준은?'], ['CQ6', '위 내용의 공식 근거는?']];
  cq.forEach((c, i) => { const x = 0.55 + (i % 2) * 6.2, y = 2.05 + Math.floor(i / 2) * 1.25;
    box(s, x, y, 5.95, 1.0, { fill: SKY }); chip(s, x + 0.3, y + 0.33, 0.95, c[0]);
    T(s, c[1], { x: x + 1.5, y, w: 4.3, h: 1.0, fontSize: 18, bold: true, color: NAVY, valign: 'middle' });
  });
  box(s, 0.55, 5.95, 12.23, 0.75, { fill: NAVY });
  T(s, '이번 과업에서는 댐 운영 기록 조회에 필요한 질문 6개를 범위로 정했다', { x: 0.55, y: 5.95, w: 12.23, h: 0.75, fontSize: 16, bold: true, color: WHITE, align: 'center', valign: 'middle' });
}
// 5. CQ에서 Class와 관계
{
  const s = add('Ⅰ. 만든 구조'); head(s, 'Ⅰ. 만든 구조', 'CQ에서 Class와 관계를 뽑는다', '질문에 나오는 대상이 Class가 되고, 대상 사이의 연결이 관계가 된다');
  const row = (y, parts, cls, rel) => {
    box(s, 0.55, y, 6.6, 1.15, { fill: PALE, line: LINE });
    s.addText(parts.map(p => ({ text: p[0], options: { color: p[1] ? (p[1] === 'c' ? BLUE : ORANGE) : INK, bold: !!p[1] } })), { x: 0.8, y, w: 6.2, h: 1.15, fontFace: F, fontSize: 18, valign: 'middle', margin: 0, isTextBox: true });
    arrow(s, 7.3, y + 0.575, 7.95, y + 0.575, null, { color: GRAY });
    cls.forEach((c, i) => node(s, 8.1 + i * 1.62, y + 0.1, 1.5, 0.5, c, null, { fs: 13 }));
    T(s, rel, { x: 8.1, y: y + 0.68, w: 4.7, h: 0.4, fontSize: 13, bold: true, color: ORANGE });
  };
  row(2.05, [['충주댐', 'c'], ['에서 과거에 어떤 '], ['방류 조작', 'c'], ['이 ', null], ['있었나', 'r'], ['?']], ['댐', '운영행위'], '관계: 운영행위가 댐에서 수행됨');
  row(3.4, [['그 조작을 ', null], ['허가한', 'r'], [' '], ['방류 승인', 'c'], ['은?']], ['방류 승인', '운영행위'], '관계: 승인이 운영행위를 허가함');
  row(4.75, [['그 승인의 ', null], ['공식 근거', 'c'], ['는 ', null], ['무엇인가', 'r'], ['?']], ['방류 승인', '근거'], '관계: 승인이 근거를 둠');
  chip(s, 0.55, 6.2, 1.3, 'Class', { fill: BLUE }); T(s, '파란 글자', { x: 2.0, y: 6.2, w: 1.5, h: 0.34, fontSize: 13, color: GRAY, valign: 'middle' });
  chip(s, 3.6, 6.2, 1.3, '관계', { fill: ORANGE }); T(s, '주황 글자', { x: 5.05, y: 6.2, w: 1.5, h: 0.34, fontSize: 13, color: GRAY, valign: 'middle' });
}
// 6. 우리 온톨로지
{
  const s = add('Ⅰ. 만든 구조'); head(s, 'Ⅰ. 만든 구조', '이렇게 만든 온톨로지', 'Class 6개와 그 사이의 관계 6개');
  const W = 2.6, H = 1.05;
  const P = { dam: [5.37, 3.55], hms: [0.75, 3.55], cri: [5.37, 1.85], opr: [9.98, 3.55], apr: [9.98, 5.5], evi: [5.37, 5.5] };
  arrow(s, P.dam[0], P.dam[1] + H / 2, P.hms[0] + W, P.hms[1] + H / 2, '상태를 가짐');
  arrow(s, P.cri[0] + W / 2, P.cri[1] + H, P.dam[0] + W / 2, P.dam[1], '적용됨', { dx: 0.75 });
  arrow(s, P.opr[0], P.opr[1] + H / 2, P.dam[0] + W, P.dam[1] + H / 2, '수행됨');
  arrow(s, P.apr[0] + W / 2, P.apr[1], P.opr[0] + W / 2, P.opr[1] + H, '허가함', { dx: 0.75 });
  arrow(s, P.apr[0], P.apr[1] + 0.25, P.dam[0] + W - 0.1, P.dam[1] + H, '대상', { lw: 0.8 });
  arrow(s, P.apr[0], P.apr[1] + H * 0.7, P.evi[0] + W, P.evi[1] + H * 0.7, '근거를 둠');
  node(s, P.dam[0], P.dam[1], W, H, '댐', '이름, 종류');
  node(s, P.hms[0], P.hms[1], W, H, '수문·기상 상태', '항목, 관측소 코드', { fill: BLUE });
  node(s, P.cri[0], P.cri[1], W, H, '운영기준', '종류, 값, 단위', { fill: BLUE });
  node(s, P.opr[0], P.opr[1], W, H, '운영행위', '종류, 시각', { fill: BLUE });
  node(s, P.apr[0], P.apr[1], W, H, '방류 승인', '승인일, 승인 내용', { fill: BLUE });
  node(s, P.evi[0], P.evi[1], W, H, '근거', '제목, 종류, 위치', { fill: '5B7FA6' });
  T(s, '운영행위와 운영기준도\n근거와 이어진다', { x: 0.75, y: 5.55, w: 3.6, h: 0.8, fontSize: 13, color: GRAY, lineSpacingMultiple: 1.2 });
  T(s, '상자 = Class,  상자 안 작은 글씨 = 속성,  화살표 = 관계', { x: 0.75, y: 1.95, w: 4.4, h: 0.6, fontSize: 13, color: GRAY });
}
// 7. KG
{
  const s = add('Ⅰ. 만든 구조'); head(s, 'Ⅰ. 만든 구조', '지식그래프(KG)란', '온톨로지라는 틀에 실제 자료를 채워 넣은 것');
  T(s, '온톨로지 (틀)', { x: 0.55, y: 1.95, w: 5.4, h: 0.4, fontSize: 16, bold: true, color: GRAY, align: 'center' });
  box(s, 0.55, 2.4, 5.4, 3.5, { fill: PALE, line: LINE });
  node(s, 0.95, 3.0, 1.9, 0.9, '방류 승인', null, { fill: WHITE, line: BLUE, color: BLUE }); node(s, 3.65, 3.0, 1.9, 0.9, '운영행위', null, { fill: WHITE, line: BLUE, color: BLUE }); node(s, 2.3, 4.6, 1.9, 0.9, '댐', null, { fill: WHITE, line: BLUE, color: BLUE });
  arrow(s, 2.85, 3.45, 3.65, 3.45, '허가함', { lw: 0.9, bg: PALE }); arrow(s, 4.6, 3.9, 3.7, 4.6, '수행됨', { lw: 0.9, bg: PALE, dx: 0.55 });
  arrow(s, 6.1, 4.15, 7.25, 4.15, null, { color: NAVY, width: 3 }); T(s, '실제 자료를\n채움', { x: 5.95, y: 4.3, w: 1.45, h: 0.6, fontSize: 12, color: NAVY, bold: true, align: 'center' });
  T(s, '지식그래프 (실제 값)', { x: 7.4, y: 1.95, w: 5.4, h: 0.4, fontSize: 16, bold: true, color: NAVY, align: 'center' });
  box(s, 7.4, 2.4, 5.4, 3.5, { fill: SKY, line: SKY2 });
  node(s, 7.7, 2.9, 2.2, 1.1, '승인 3412', '2020-08-02\n승인량 3000㎥/s', { fs: 14, fs2: 10 }); node(s, 10.35, 2.9, 2.2, 1.1, '방류', '2020-08-02 18:00', { fs: 14, fs2: 10 }); node(s, 9.0, 4.55, 2.2, 1.0, '충주댐', '다목적댐', { fs: 14, fs2: 10 });
  arrow(s, 9.9, 3.45, 10.35, 3.45); arrow(s, 11.3, 4.0, 10.4, 4.55);
  box(s, 0.55, 6.1, 12.23, 0.65, { fill: NAVY });
  T(s, 'Entity: Class에 실제 값이 들어간 하나하나 (예: 충주댐, 승인 3412)', { x: 0.55, y: 6.1, w: 12.23, h: 0.65, fontSize: 15, bold: true, color: WHITE, align: 'center', valign: 'middle' });
}
// 8. 자료
{
  const s = add('Ⅰ. 만든 구조'); head(s, 'Ⅰ. 만든 구조', 'KG에 채운 실제 자료', 'K-water 댐 4개(충주댐, 소양강댐, 횡성댐, 광동댐)의 공개 자료 세 종류');
  const d = [['시간 측정값', 'K-water 공개 자료', ['수위, 저수량, 강우량,', '유입량, 총방류량, 저수율'], '약 87만 행', '2010 ~ 2026년, 1시간 간격'],
    ['방류 승인 기록', '한강홍수통제소 공개 자료', ['승인일, 방류 시작 시각,', '승인 방류량, 비고'], '80건', '2010 ~ 2021년'],
    ['운영 규정', '댐과 보 등의 연계운영규정', ['별표 3', '댐별 홍수기 제한수위'], '3건', '충주댐, 소양강댐, 횡성댐']];
  d.forEach((x, i) => { const X = 0.55 + i * 4.18;
    box(s, X, 2.05, 3.9, 4.6, { fill: SKY });
    box(s, X, 2.05, 3.9, 1.05, { fill: NAVY });
    T(s, x[0], { x: X + 0.3, y: 2.17, w: 3.3, h: 0.45, fontSize: 20, bold: true, color: WHITE });
    T(s, x[1], { x: X + 0.3, y: 2.63, w: 3.3, h: 0.35, fontSize: 12, color: 'CFE0F2' });
    T(s, x[2].join('\n'), { x: X + 0.3, y: 3.4, w: 3.3, h: 0.9, fontSize: 15, color: INK, lineSpacingMultiple: 1.25 });
    T(s, x[3], { x: X + 0.3, y: 4.55, w: 3.3, h: 0.9, fontSize: 40, bold: true, color: BLUE });
    T(s, x[4], { x: X + 0.3, y: 5.75, w: 3.3, h: 0.4, fontSize: 13, color: GRAY });
  });
}
// 9. 자료가 Class에 들어가는 모습
{
  const s = add('Ⅰ. 만든 구조'); head(s, 'Ⅰ. 만든 구조', '자료 한 줄이 KG가 되는 과정', '방류 승인 기록의 한 행이 Class 네 곳에 나뉘어 들어가고, 관계로 이어진다');
  T(s, '방류 승인 기록 (원본 표의 한 행)', { x: 0.55, y: 1.9, w: 6, h: 0.35, fontSize: 13, bold: true, color: GRAY });
  const cols = [['순차번호', '3412', 1.5], ['관측소명', '충주', 1.5], ['승인년월일', '2020-08-02', 2.2], ['방류시작시간', '2020-08-02 18:00', 2.9], ['접수방류량', '3000', 1.8], ['비고', '', 2.33]];
  let x = 0.55; const xs = [];
  cols.forEach(c => { xs.push([x, c[2]]);
    s.addShape(pres.ShapeType.rect, { x, y: 2.3, w: c[2], h: 0.45, fill: { color: 'E5E7EB' }, line: { color: 'B6BCC6', width: 0.75 } });
    T(s, c[0], { x, y: 2.3, w: c[2], h: 0.45, fontSize: 13, bold: true, align: 'center', valign: 'middle' });
    s.addShape(pres.ShapeType.rect, { x, y: 2.75, w: c[2], h: 0.5, fill: { color: WHITE }, line: { color: 'B6BCC6', width: 0.75 } });
    T(s, c[1], { x, y: 2.75, w: c[2], h: 0.5, fontSize: 14, align: 'center', valign: 'middle' }); x += c[2]; });
  const mid = i => xs[i][0] + xs[i][1] / 2;
  const N = [[0.75, '댐', '충주댐'], [3.85, '방류 승인', '승인 3412\n승인일 2020-08-02\n승인량 3000㎥/s'], [6.95, '운영행위', '방류\n2020-08-02 18:00'], [10.05, '근거', '원본 기록\n순차번호 3412']];
  arrow(s, mid(1), 3.25, N[0][0] + 1.25, 4.4, null, { color: GRAY, dash: true, width: 1.25 });
  arrow(s, mid(2), 3.25, N[1][0] + 1.25, 4.4, null, { color: GRAY, dash: true, width: 1.25 });
  arrow(s, mid(4), 3.25, N[1][0] + 1.6, 4.4, null, { color: GRAY, dash: true, width: 1.25 });
  arrow(s, mid(3), 3.25, N[2][0] + 1.25, 4.4, null, { color: GRAY, dash: true, width: 1.25 });
  arrow(s, mid(0), 3.25, N[3][0] + 0.4, 4.4, null, { color: 'C0C6CF', dash: true, width: 1 });
  N.forEach(n => { box(s, n[0], 4.4, 2.5, 0.5, { fill: BLUE }); T(s, n[1], { x: n[0], y: 4.4, w: 2.5, h: 0.5, fontSize: 14, bold: true, color: WHITE, align: 'center', valign: 'middle' });
    box(s, n[0], 4.9, 2.5, 1.15, { fill: SKY, line: SKY2 }); T(s, n[2], { x: n[0], y: 4.9, w: 2.5, h: 1.15, fontSize: 13, align: 'center', valign: 'middle', lineSpacingMultiple: 1.15 }); });
  arrow(s, N[1][0], 5.45, N[0][0] + 2.5, 5.45, '대상', { lw: 0.55, fs: 11 });
  arrow(s, N[1][0] + 2.5, 5.45, N[2][0], 5.45, '허가함', { lw: 0.58, fs: 11 });
  arrow(s, N[2][0] + 2.5, 5.45, N[3][0], 5.45, '근거', { lw: 0.55, fs: 11 });
  T(s, '위 = 원본 표,  아래 = KG의 Entity,  점선 = 값이 들어가는 자리,  실선 = 관계', { x: 0.55, y: 6.35, w: 12.2, h: 0.35, fontSize: 13, color: GRAY });
}
// 10. 완성된 KG와 외부 저장소
{
  const s = add('Ⅰ. 만든 구조'); head(s, 'Ⅰ. 만든 구조', '완성된 KG와 외부 저장소', 'KG에는 연결 관계를 담고, 양이 많은 측정값과 규정 원문은 KG 밖에 둔다');
  box(s, 0.55, 2.0, 6.3, 4.7, { fill: SKY });
  T(s, '지식그래프 (KG)', { x: 0.85, y: 2.2, w: 5.7, h: 0.4, fontSize: 18, bold: true, color: NAVY });
  T(s, '264', { x: 0.85, y: 2.75, w: 2.7, h: 0.9, fontSize: 48, bold: true, color: BLUE }); T(s, 'Entity', { x: 0.85, y: 3.65, w: 2.7, h: 0.35, fontSize: 14, color: GRAY });
  T(s, '418', { x: 3.75, y: 2.75, w: 2.7, h: 0.9, fontSize: 48, bold: true, color: BLUE }); T(s, '관계', { x: 3.75, y: 3.65, w: 2.7, h: 0.35, fontSize: 14, color: GRAY });
  const cnt = [['댐', 4], ['수문·기상 상태', 24], ['운영기준', 3], ['운영행위', 68], ['방류 승인', 80], ['근거', 85]];
  cnt.forEach((c, i) => { const X = 0.85 + (i % 3) * 1.95, Y = 4.4 + Math.floor(i / 3) * 1.05;
    box(s, X, Y, 1.8, 0.9, { fill: WHITE, line: SKY2 }); T(s, [{ text: String(c[1]), options: { fontSize: 20, bold: true, color: NAVY, breakLine: true } }, { text: c[0], options: { fontSize: 12, color: GRAY } }], { x: X, y: Y, w: 1.8, h: 0.9, align: 'center', valign: 'middle' }); });
  arrow(s, 6.85, 3.35, 7.7, 3.35, null, { color: NAVY, width: 2.25 }); arrow(s, 6.85, 5.4, 7.7, 5.4, null, { color: NAVY, width: 2.25 });
  const ext = [[2.35, '측정 저장소', '시간 측정값 약 87만 행', 'KG에는 관측소 코드만 두고,\n시각으로 값을 찾아온다'], [4.4, '문서 저장소', '연계운영규정 별표 3 원문', 'KG에는 문서 위치만 두고,\n원문을 찾아온다']];
  ext.forEach(e => { box(s, 7.7, e[0], 5.08, 1.95, { fill: PALE, line: LINE });
    T(s, e[1], { x: 8.0, y: e[0] + 0.2, w: 4.5, h: 0.4, fontSize: 18, bold: true, color: NAVY });
    T(s, e[2], { x: 8.0, y: e[0] + 0.65, w: 4.5, h: 0.35, fontSize: 14, bold: true, color: BLUE });
    T(s, e[3], { x: 8.0, y: e[0] + 1.05, w: 4.5, h: 0.75, fontSize: 13, color: INK, lineSpacingMultiple: 1.2 }); });
  T(s, '외부 저장소', { x: 7.7, y: 1.95, w: 5, h: 0.35, fontSize: 13, bold: true, color: GRAY });
}
// 11. RAG
{
  const s = add('Ⅰ. 만든 구조'); head(s, 'Ⅰ. 만든 구조', 'KG는 RAG로 LLM에 쓰인다', 'RAG: 답하기 전에 관련 근거를 먼저 찾아서 LLM에 함께 주는 방식');
  T(s, 'LLM만 쓸 때', { x: 0.55, y: 2.0, w: 5, h: 0.4, fontSize: 16, bold: true, color: GRAY });
  box(s, 0.55, 2.45, 12.23, 1.5, { fill: PALE, line: LINE });
  node(s, 0.9, 2.75, 2.4, 0.9, '질문', null, { fill: WHITE, line: GRAY, color: INK }); arrow(s, 3.3, 3.2, 5.4, 3.2, null, { color: GRAY });
  node(s, 5.4, 2.75, 2.4, 0.9, 'LLM', null, { fill: GRAY }); arrow(s, 7.8, 3.2, 9.9, 3.2, null, { color: GRAY });
  node(s, 9.9, 2.75, 2.55, 0.9, '답변', '근거를 알 수 없음', { fill: WHITE, line: GRAY, color: INK, color2: ORANGE, fs2: 12 });
  T(s, 'RAG를 쓸 때', { x: 0.55, y: 4.25, w: 5, h: 0.4, fontSize: 16, bold: true, color: NAVY });
  box(s, 0.55, 4.7, 12.23, 1.95, { fill: SKY });
  node(s, 0.9, 5.2, 2.0, 0.9, '질문', null, { fill: WHITE, line: BLUE, color: NAVY }); arrow(s, 2.9, 5.65, 3.75, 5.65);
  node(s, 3.75, 5.0, 2.7, 1.3, 'KG에서\n근거 찾기', null, { fill: BLUE, fs: 15 }); arrow(s, 6.45, 5.65, 7.3, 5.65);
  node(s, 7.3, 5.2, 2.0, 0.9, 'LLM', '질문 + 근거', { fill: NAVY, fs2: 11 }); arrow(s, 9.3, 5.65, 10.15, 5.65);
  node(s, 10.15, 5.0, 2.35, 1.3, '답변', '근거와 출처 번호가\n함께 나옴', { fill: WHITE, line: BLUE, color: NAVY, color2: BLUE, fs2: 12 });
}
// 12. 최종 구조
{
  const s = add('Ⅰ. 만든 구조'); head(s, 'Ⅰ. 만든 구조', '최종 구조', '찾는 일은 코드가, 읽고 쓰는 일은 LLM이 한다');
  const st = [['①', '질문 해석', 'LLM', '어느 CQ인지,\n어느 댐·기간인지'], ['②', 'KG·저장소 검색', '코드', '관계를 따라가\n근거를 찾음'], ['③', '근거 정리', '코드', '찾은 값에\n출처 번호를 붙임'], ['④', '답변 작성', 'LLM', '근거만으로\n답을 씀']];
  node(s, 0.55, 3.2, 1.45, 1.5, '질문', null, { fill: WHITE, line: NAVY, color: NAVY });
  st.forEach((x, i) => { const X = 2.5 + i * 2.33; const llm = x[2] === 'LLM';
    arrow(s, X - 0.48, 3.95, X - 0.04, 3.95, null, { color: NAVY });
    box(s, X, 2.55, 1.85, 2.8, { fill: llm ? NAVY : SKY, line: llm ? NAVY : SKY2 });
    T(s, x[0], { x: X, y: 2.7, w: 1.85, h: 0.45, fontSize: 20, bold: true, color: llm ? '9DBEDD' : BLUE, align: 'center' });
    T(s, x[1], { x: X + 0.05, y: 3.2, w: 1.75, h: 0.75, fontSize: 15, bold: true, color: llm ? WHITE : NAVY, align: 'center', valign: 'middle' });
    T(s, x[3], { x: X + 0.05, y: 4.05, w: 1.75, h: 0.75, fontSize: 11.5, color: llm ? 'DCE9F7' : INK, align: 'center', lineSpacingMultiple: 1.15 });
    chip(s, X + 0.45, 4.9, 0.95, x[2], { fill: llm ? BLUE : WHITE, color: llm ? WHITE : BLUE, fs: 11 }); });
  arrow(s, 11.35 - 0.02, 3.95, 11.77, 3.95, null, { color: NAVY });
  node(s, 11.8, 3.2, 1.0, 1.5, '답변', null, { fill: WHITE, line: NAVY, color: NAVY, fs: 14 });
  arrow(s, 5.75, 6.0, 5.75, 5.4, null, { color: BLUE });
  box(s, 3.3, 6.0, 2.3, 0.7, { fill: WHITE, line: BLUE }); T(s, '지식그래프 (KG)', { x: 3.3, y: 6.0, w: 2.3, h: 0.7, fontSize: 13, bold: true, color: NAVY, align: 'center', valign: 'middle' });
  box(s, 5.9, 6.0, 2.3, 0.7, { fill: WHITE, line: BLUE }); T(s, '측정·문서 저장소', { x: 5.9, y: 6.0, w: 2.3, h: 0.7, fontSize: 13, bold: true, color: NAVY, align: 'center', valign: 'middle' });
  T(s, 'LLM: 공개된 범용 모델을 연구실 서버에서 실행', { x: 8.5, y: 6.15, w: 4.3, h: 0.4, fontSize: 12, color: GRAY });
}

// ================================================= Ⅱ. 시연
pres.addSection({ title: 'Ⅱ. 시연' });
// 13. 시연 범위
{
  const s = add('Ⅱ. 시연'); head(s, 'Ⅱ. 시연', '시연에서 보여 드릴 질문', '정한 범위(CQ) 안의 질문에 답하고, 범위 밖의 질문에는 답하지 않는다');
  const q = [['CQ1', '충주댐 지금 상황 알려줘'], ['CQ2', '2020년 8월 2일 18시 충주댐 수위는?'], ['CQ3', '2011년 7월 충주댐 방류 조작 기록 알려줘'], ['CQ4', '2020년 8월 충주댐 방류 승인이 어떻게 바뀌었는지 정리해줘'], ['CQ5', '충주댐 홍수기 제한수위는 얼마야?'], ['CQ6', '충주댐 제한수위 근거 규정이 뭐야?']];
  q.forEach((c, i) => { const y = 1.95 + i * 0.52; if (i % 2 === 0) s.addShape(pres.ShapeType.rect, { x: 0.55, y, w: 7.6, h: 0.52, fill: { color: PALE }, line: { color: PALE, width: 0 } });
    chip(s, 0.7, y + 0.09, 0.85, c[0], { fs: 11 }); T(s, c[1], { x: 1.75, y, w: 6.3, h: 0.52, fontSize: 14, valign: 'middle' }); });
  T(s, '관계를 이어서 찾는 질문', { x: 0.55, y: 5.25, w: 7.6, h: 0.35, fontSize: 13, bold: true, color: ORANGE });
  const m = [['CQ1+5', '충주댐 지금 수위가 홍수기 제한수위보다 높아?'], ['CQ3→2', '2011년 7월 충주댐 방류 조작 시점마다 수위와 유입량은?']];
  m.forEach((c, i) => { const y = 5.65 + i * 0.52; s.addShape(pres.ShapeType.rect, { x: 0.55, y, w: 7.6, h: 0.52, fill: { color: 'FDF3EA' }, line: { color: 'FDF3EA', width: 0 } });
    chip(s, 0.7, y + 0.09, 0.95, c[0], { fs: 11, fill: ORANGE }); T(s, c[1], { x: 1.8, y, w: 6.3, h: 0.52, fontSize: 14, valign: 'middle' }); });
  box(s, 8.5, 1.95, 4.28, 2.25, { fill: SKY });
  T(s, '답변의 모양', { x: 8.75, y: 2.1, w: 3.8, h: 0.4, fontSize: 16, bold: true, color: NAVY });
  T(s, [{ text: '근거', options: { bold: true, color: BLUE } }, { text: '  KG와 저장소에서 찾은 값', options: { breakLine: true } }, { text: '판단', options: { bold: true, color: BLUE } }, { text: '  근거를 비교·정리한 문장', options: { breakLine: true } }, { text: '출처 번호', options: { bold: true, color: BLUE } }, { text: '  누르면 원문이 열림' }], { x: 8.75, y: 2.6, w: 3.8, h: 1.4, fontSize: 14, lineSpacingMultiple: 1.45 });
  box(s, 8.5, 4.4, 4.28, 2.3, { fill: PALE, line: LINE });
  T(s, '범위 밖 (답하지 않음)', { x: 8.75, y: 4.55, w: 3.8, h: 0.4, fontSize: 16, bold: true, color: GRAY });
  T(s, '4개 댐이 아닌 댐\n예측, 수문 개도, 하류 수위\n방류 사유, 절차\n조건을 주고 사례를 찾는 질문', { x: 8.75, y: 5.05, w: 3.8, h: 1.5, fontSize: 14, lineSpacingMultiple: 1.3 });
}
// 14. 시연 영상
{
  const s = add('Ⅱ. 시연'); head(s, 'Ⅱ. 시연', '시연 영상', null);
  box(s, 1.9, 1.7, 9.55, 5.1, { fill: '1F2937', r: 0.05 });
  T(s, '시연 영상 넣는 자리', { x: 1.9, y: 3.7, w: 9.55, h: 0.6, fontSize: 24, bold: true, color: WHITE, align: 'center' });
  T(s, '삽입 > 비디오 > 이 디바이스 (파일로 넣어 인터넷 없이 재생)', { x: 1.9, y: 4.4, w: 9.55, h: 0.4, fontSize: 14, color: '9CA3AF', align: 'center' });
}

// ================================================= Ⅲ. 향후
pres.addSection({ title: 'Ⅲ. 향후 방향' });
// 15. 지금 구조의 범위와 한계
{
  const s = add('Ⅲ. 향후 방향'); head(s, 'Ⅲ. 향후 방향', '지금 구조가 하는 일과 못 하는 일', '정한 범위에서는 근거를 밝혀 답하지만, 범위 밖은 아직 다루지 못한다');
  box(s, 0.55, 2.0, 5.95, 3.9, { fill: SKY });
  T(s, '하는 일', { x: 0.85, y: 2.2, w: 5.3, h: 0.45, fontSize: 20, bold: true, color: NAVY });
  T(s, [{ text: '정한 질문 6종(CQ)에 답한다', options: { bullet: true, breakLine: true } }, { text: '값마다 출처 번호를 붙이고, 원문을 보여 준다', options: { bullet: true, breakLine: true } }, { text: '승인 기록, 측정값, 규정을 이어서 찾는다', options: { bullet: true, breakLine: true } }, { text: '자료에 없으면 없다고 답한다', options: { bullet: true } }], { x: 0.85, y: 2.85, w: 5.4, h: 3.2, fontSize: 16, paraSpaceAfter: 12 });
  box(s, 6.83, 2.0, 5.95, 3.9, { fill: PALE, line: LINE });
  T(s, '아직 못 하는 일', { x: 7.13, y: 2.2, w: 5.3, h: 0.45, fontSize: 20, bold: true, color: ORANGE });
  T(s, [{ text: '"지금"은 저장된 마지막 값이다 (실시간 자료가 아님)', options: { bullet: true, breakLine: true } }, { text: '"지금 수위가 이런데, 비슷했던 과거 사례는?"처럼 조건을 주는 질문', options: { bullet: true, breakLine: true } }, { text: '미리 정하지 않은 형태의 질문', options: { bullet: true, breakLine: true } }, { text: '판단 문장의 표현이 거칠 때가 있다', options: { bullet: true } }], { x: 7.13, y: 2.85, w: 5.4, h: 3.2, fontSize: 16, paraSpaceAfter: 12 });
}
// 16. 향후 방향 (교수님 작성)
{
  const s = add('Ⅲ. 향후 방향'); head(s, 'Ⅲ. 향후 방향', '향후 방향', '기본 틀 위에 모듈을 하나씩 더해 고도화한다');
  const it = [['실시간 자료 연계', '저장해 둔 자료 대신\n운영 자료를 바로 가져옴'], ['에이전트', '질문에 따라 필요한 도구를\nLLM이 골라 이어서 씀'], ['LLM 고도화', '댐 운영 분야에 맞춘\n모델과 답변 품질 개선'], ['범위 확장', '댐, 자료 종류, 질문 유형을\n단계적으로 늘림']];
  it.forEach((x, i) => { const X = 0.55 + i * 3.11;
    box(s, X, 2.3, 2.9, 2.6, { fill: i % 2 ? SKY : NAVY });
    T(s, x[0], { x: X + 0.25, y: 2.6, w: 2.4, h: 0.8, fontSize: 19, bold: true, color: i % 2 ? NAVY : WHITE, valign: 'middle' });
    T(s, x[1], { x: X + 0.25, y: 3.55, w: 2.4, h: 1.1, fontSize: 14, color: i % 2 ? INK : 'DCE9F7', lineSpacingMultiple: 1.25 }); });
  box(s, 0.55, 5.3, 12.23, 1.3, { fill: 'FFF7E6', line: 'F2C879' });
  T(s, '이 장은 교수님 작성 부분입니다 (한두 장). 위 네 항목은 11/13 논의 내용을 옮겨 둔 자리 표시입니다.', { x: 0.85, y: 5.3, w: 11.6, h: 1.3, fontSize: 14, color: '8A5A00', valign: 'middle' });
}
// 17. 끝
{
  const s = pres.addSlide({ sectionTitle: 'Ⅲ. 향후 방향' }); s.background = { color: NAVY };
  T(s, '감사합니다', { x: 0.55, y: 3.0, w: 12.23, h: 0.9, fontSize: 40, bold: true, color: WHITE, align: 'center' });
  T(s, '질문과 의견을 부탁드립니다', { x: 0.55, y: 4.0, w: 12.23, h: 0.5, fontSize: 18, color: '9DBEDD', align: 'center' });
}
pres.writeFile({ fileName: OUT }).then(f => console.log('saved', f));
