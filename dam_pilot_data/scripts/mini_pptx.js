// pptxgenjs가 없는 환경에서 쓰는 작은 대체 모듈. build_khnp_talk_1126.js가 쓰는 기능만 구현한다:
// layout, defineSlideMaster(배경·그림·글상자·쪽 번호), addSection(무시), addSlide, slide.background, addText, addShape(rect, roundRect, line), addImage, writeFile.
// 좌표는 인치, 글자 크기는 pt, 색은 6자리 hex. jszip이 필요하다(NODE_PATH로 찾음).
const fs = require('fs'), path = require('path');
const JSZip = require('jszip');
const E = v => Math.round(v * 914400);
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const NS = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"';
const DECL = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n';
const fill = c => c ? `<a:solidFill><a:srgbClr val="${c}"/></a:solidFill>` : '<a:noFill/>';

class Holder { // 슬라이드와 레이아웃이 함께 쓰는 도형 목록
  constructor(pres) { this.pres = pres; this.items = []; this.media = []; this.background = null; }
  addText(text, o = {}) { this.items.push({ k: 'text', text, o }); return this; }
  addShape(type, o = {}) { this.items.push({ k: 'shape', type, o }); return this; }
  addImage(o = {}) { this.items.push({ k: 'image', o }); return this; }
  addNotes() { return this; }
  xml(startId, relBase) {
    let id = startId, out = '', rels = [];
    for (const it of this.items) {
      id += 1;
      if (it.k === 'image') {
        const rid = 'rId' + (relBase + rels.length + 1); rels.push({ rid, file: this.pres._media(it.o.path) });
        out += `<p:pic><p:nvPicPr><p:cNvPr id="${id}" name="Picture ${id}"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr><p:blipFill><a:blip r:embed="${rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>`
          + `<p:spPr><a:xfrm><a:off x="${E(it.o.x)}" y="${E(it.o.y)}"/><a:ext cx="${E(it.o.w)}" cy="${E(it.o.h)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>`;
      } else if (it.k === 'shape' && it.type === 'line') {
        const o = it.o, ln = o.line || {};
        out += `<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="${id}" name="Line ${id}"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr><p:spPr><a:xfrm${o.flipH ? ' flipH="1"' : ''}${o.flipV ? ' flipV="1"' : ''}><a:off x="${E(o.x)}" y="${E(o.y)}"/><a:ext cx="${E(o.w)}" cy="${E(o.h)}"/></a:xfrm>`
          + `<a:prstGeom prst="line"><a:avLst/></a:prstGeom><a:ln w="${Math.round((ln.width || 1) * 12700)}">${fill(ln.color || '000000')}<a:prstDash val="${ln.dashType === 'dash' ? 'dash' : 'solid'}"/>${ln.endArrowType ? '<a:tailEnd type="triangle" w="med" len="med"/>' : ''}</a:ln></p:spPr></p:cxnSp>`;
      } else if (it.k === 'shape') {
        const o = it.o, ln = o.line || {};
        const adj = it.type === 'roundRect' ? Math.min(50000, Math.round(((o.rectRadius ?? 0.1) / Math.min(o.w, o.h)) * 100000)) : null;
        out += `<p:sp><p:nvSpPr><p:cNvPr id="${id}" name="Shape ${id}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="${E(o.x)}" y="${E(o.y)}"/><a:ext cx="${E(o.w)}" cy="${E(o.h)}"/></a:xfrm>`
          + `<a:prstGeom prst="${it.type}"><a:avLst>${adj !== null ? `<a:gd name="adj" fmla="val ${adj}"/>` : ''}</a:avLst></a:prstGeom>${fill(o.fill && o.fill.color)}`
          + (ln.width === 0 ? '<a:ln><a:noFill/></a:ln>' : `<a:ln w="${Math.round((ln.width ?? 0.75) * 12700)}">${fill(ln.color || (o.fill && o.fill.color))}</a:ln>`)
          + `</p:spPr><p:txBody><a:bodyPr rtlCol="0" anchor="ctr"/><a:lstStyle/><a:p><a:endParaRPr lang="ko-KR"/></a:p></p:txBody></p:sp>`;
      } else out += this._text(it, id);
    }
    return { xml: out, rels, lastId: id };
  }
  _text(it, id) {
    const o = it.o, F = o.fontFace || this.pres.theme.bodyFontFace || 'Arial';
    const m = o.margin === undefined ? 0.05 : o.margin, M = E(typeof m === 'number' ? m : 0);
    const anchor = { top: 't', middle: 'ctr', bottom: 'b' }[o.valign || 'top'];
    const rpr = (r, tag = 'a:rPr') => `<${tag} lang="ko-KR" altLang="en-US" sz="${Math.round((r.fontSize || o.fontSize || 14) * 100)}" b="${(r.bold ?? o.bold) ? 1 : 0}" dirty="0">${fill(r.color || o.color || '000000')}<a:latin typeface="${esc(F)}"/><a:ea typeface="${esc(F)}"/><a:cs typeface="${esc(F)}"/></${tag}>`;
    // 문단 나누기
    let paras = [];
    if (o.field === 'slidenum') paras = [{ runs: [{ field: true, o: {} }], o: {} }];
    else if (typeof it.text === 'string') paras = it.text.split('\n').map(t => ({ runs: [{ text: t, o: {} }], o: {} }));
    else {
      let cur = { runs: [], o: {} };
      for (const r of it.text) {
        const ro = r.options || {}; const parts = String(r.text).split('\n');
        parts.forEach((t, i) => { if (i > 0) { paras.push(cur); cur = { runs: [], o: {} }; } cur.runs.push({ text: t, o: ro }); if (ro.bullet) cur.o.bullet = true; });
        if (ro.breakLine) { paras.push(cur); cur = { runs: [], o: {} }; }
      }
      if (cur.runs.length) paras.push(cur);
    }
    const algn = { left: 'l', center: 'ctr', right: 'r' }[o.align || 'left'];
    const ps = paras.map(p => {
      let ppr = `<a:pPr algn="${algn}"${p.o.bullet ? ' marL="285750" indent="-285750"' : ''}>`;
      if (o.lineSpacingMultiple) ppr += `<a:lnSpc><a:spcPct val="${Math.round(o.lineSpacingMultiple * 100000)}"/></a:lnSpc>`;
      if (o.paraSpaceAfter) ppr += `<a:spcAft><a:spcPts val="${Math.round(o.paraSpaceAfter * 100)}"/></a:spcAft>`;
      ppr += p.o.bullet ? '<a:buFont typeface="Arial"/><a:buChar char="&#8226;"/>' : '<a:buNone/>';
      ppr += '</a:pPr>';
      const runs = p.runs.map(r => r.field ? `<a:fld id="{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}" type="slidenum">${rpr(r.o)}<a:t>‹#›</a:t></a:fld>` : (r.text === '' ? '' : `<a:r>${rpr(r.o)}<a:t>${esc(r.text)}</a:t></a:r>`)).join('');
      return `<a:p>${ppr}${runs}${rpr({}, 'a:endParaRPr')}</a:p>`;
    }).join('');
    return `<p:sp><p:nvSpPr><p:cNvPr id="${id}" name="${esc(o.objectName || 'Text ' + id)}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="${E(o.x)}" y="${E(o.y)}"/><a:ext cx="${E(o.w)}" cy="${E(o.h)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>${fill(o.fill && o.fill.color)}</p:spPr>`
      + `<p:txBody><a:bodyPr wrap="square" lIns="${M}" tIns="${M}" rIns="${M}" bIns="${M}" rtlCol="0" anchor="${anchor}"><a:noAutofit/></a:bodyPr><a:lstStyle/>${ps}</p:txBody></p:sp>`;
  }
}

class Pres {
  constructor() { this.layout = 'LAYOUT_WIDE'; this.theme = {}; this.slides = []; this.masters = {}; this.mediaFiles = []; this.title = '';
    this.ShapeType = { rect: 'rect', roundRect: 'roundRect', line: 'line', ellipse: 'ellipse', can: 'can' }; }
  _media(p) { let i = this.mediaFiles.indexOf(p); if (i < 0) { this.mediaFiles.push(p); i = this.mediaFiles.length - 1; } return 'image' + (i + 1) + path.extname(p).toLowerCase(); }
  addSection() {}
  defineSlideMaster(d) {
    const h = new Holder(this); h.background = d.background;
    for (const ob of d.objects || []) { if (ob.image) h.addImage(ob.image); if (ob.text) h.addText(ob.text.text, ob.text.options); }
    this.masters[d.title] = { holder: h, slideNumber: d.slideNumber };
  }
  addSlide(o = {}) { const s = new Holder(this); s.masterName = o.masterName; this.slides.push(s); return s; }
  async writeFile({ fileName }) {
    const zip = new JSZip(); const W = this.layout === 'LAYOUT_WIDE' ? 13.333 : 10, H = this.layout === 'LAYOUT_WIDE' ? 7.5 : 5.625;
    const F = this.theme.bodyFontFace || 'Arial';
    const tree = inner => `<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>${inner}</p:spTree>`;
    const bg = b => b && b.color ? `<p:bg><p:bgPr>${fill(b.color)}<a:effectLst/></p:bgPr></p:bg>` : '';
    const relsXml = list => DECL + `<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">${list.map(r => `<Relationship Id="${r[0]}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/${r[1]}" Target="${r[2]}"/>`).join('')}</Relationships>`;
    // 레이아웃: 1 = 빈 화면, 그 뒤로 defineSlideMaster로 만든 것
    const names = Object.keys(this.masters); const layoutOf = n => 2 + names.indexOf(n);
    const layouts = [{ name: 'Blank', holder: new Holder(this) }].concat(names.map(n => ({ name: n, holder: this.masters[n].holder })));
    layouts.forEach((L, i) => {
      const r = L.holder.xml(1, 1);
      zip.file(`ppt/slideLayouts/slideLayout${i + 1}.xml`, DECL + `<p:sldLayout ${NS} type="blank" preserve="1"><p:cSld name="${esc(L.name)}">${bg(L.holder.background)}${tree(r.xml)}</p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>`);
      zip.file(`ppt/slideLayouts/_rels/slideLayout${i + 1}.xml.rels`, relsXml([['rId1', 'slideMaster', '../slideMasters/slideMaster1.xml']].concat(r.rels.map(x => [x.rid, 'image', '../media/' + x.file]))));
    });
    zip.file('ppt/slideMasters/slideMaster1.xml', DECL + `<p:sldMaster ${NS}><p:cSld><p:bg><p:bgPr>${fill('FFFFFF')}<a:effectLst/></p:bgPr></p:bg>${tree('')}</p:cSld><p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>`
      + `<p:sldLayoutIdLst>${layouts.map((_, i) => `<p:sldLayoutId id="${2147483649 + i}" r:id="rId${i + 1}"/>`).join('')}</p:sldLayoutIdLst><p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>`);
    zip.file('ppt/slideMasters/_rels/slideMaster1.xml.rels', relsXml(layouts.map((_, i) => ['rId' + (i + 1), 'slideLayout', `../slideLayouts/slideLayout${i + 1}.xml`]).concat([['rId' + (layouts.length + 1), 'theme', '../theme/theme1.xml']])));
    this.slides.forEach((s, i) => {
      const m = this.masters[s.masterName];
      if (m && m.slideNumber) { const n = m.slideNumber; s.addText('', { x: n.x, y: n.y, w: n.w, h: n.h, fontFace: n.fontFace, fontSize: n.fontSize, color: n.color, align: n.align, margin: 0, field: 'slidenum', objectName: 'Slide Number' }); }
      const r = s.xml(1, 1);
      zip.file(`ppt/slides/slide${i + 1}.xml`, DECL + `<p:sld ${NS}><p:cSld>${bg(s.background)}${tree(r.xml)}</p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>`);
      zip.file(`ppt/slides/_rels/slide${i + 1}.xml.rels`, relsXml([['rId1', 'slideLayout', `../slideLayouts/slideLayout${m ? layoutOf(s.masterName) : 1}.xml`]].concat(r.rels.map(x => [x.rid, 'image', '../media/' + x.file]))));
    });
    this.mediaFiles.forEach((p, i) => zip.file('ppt/media/image' + (i + 1) + path.extname(p).toLowerCase(), fs.readFileSync(p)));
    const n = this.slides.length;
    zip.file('ppt/presentation.xml', DECL + `<p:presentation ${NS} saveSubsetFonts="1"><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst><p:sldIdLst>${this.slides.map((_, i) => `<p:sldId id="${256 + i}" r:id="rId${i + 2}"/>`).join('')}</p:sldIdLst>`
      + `<p:sldSz cx="${E(W)}" cy="${E(H)}"/><p:notesSz cx="6858000" cy="9144000"/></p:presentation>`);
    zip.file('ppt/_rels/presentation.xml.rels', relsXml([['rId1', 'slideMaster', 'slideMasters/slideMaster1.xml']].concat(this.slides.map((_, i) => ['rId' + (i + 2), 'slide', `slides/slide${i + 1}.xml`]),
      [['rId' + (n + 2), 'presProps', 'presProps.xml'], ['rId' + (n + 3), 'viewProps', 'viewProps.xml'], ['rId' + (n + 4), 'theme', 'theme/theme1.xml'], ['rId' + (n + 5), 'tableStyles', 'tableStyles.xml']])));
    zip.file('ppt/presProps.xml', DECL + `<p:presentationPr ${NS}/>`);
    zip.file('ppt/viewProps.xml', DECL + `<p:viewPr ${NS}><p:normalViewPr><p:restoredLeft sz="15620"/><p:restoredTop sz="94660"/></p:normalViewPr><p:slideViewPr><p:cSldViewPr><p:cViewPr varScale="1"><p:scale><a:sx n="100" d="100"/><a:sy n="100" d="100"/></p:scale><p:origin x="0" y="0"/></p:cViewPr><p:guideLst/></p:cSldViewPr></p:slideViewPr><p:notesTextViewPr><p:cViewPr><p:scale><a:sx n="1" d="1"/><a:sy n="1" d="1"/></p:scale><p:origin x="0" y="0"/></p:cViewPr></p:notesTextViewPr><p:gridSpacing cx="72008" cy="72008"/></p:viewPr>`);
    zip.file('ppt/tableStyles.xml', DECL + '<a:tblStyleLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" def="{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}"/>');
    const fonts = `<a:latin typeface="${esc(F)}"/><a:ea typeface="${esc(F)}"/><a:cs typeface="${esc(F)}"/>`;
    const fmt = '<a:fmtScheme name="Office"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst>'
      + '<a:lnStyleLst><a:ln w="6350"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln w="12700"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln w="19050"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst>'
      + '<a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>'
      + '<a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme>';
    const clr = [['dk1', '2B2B2B'], ['lt1', 'FFFFFF'], ['dk2', '003B71'], ['lt2', 'EEF5FC'], ['accent1', '0070C0'], ['accent2', 'C55A11'], ['accent3', '6B7280'], ['accent4', '5B7FA6'], ['accent5', '9DBEDD'], ['accent6', '70AD47'], ['hlink', '0563C1'], ['folHlink', '954F72']];
    zip.file('ppt/theme/theme1.xml', DECL + `<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="KHNP Talk"><a:themeElements><a:clrScheme name="KHNP Talk">${clr.map(c => `<a:${c[0]}><a:srgbClr val="${c[1]}"/></a:${c[0]}>`).join('')}</a:clrScheme>`
      + `<a:fontScheme name="KHNP Talk"><a:majorFont>${fonts}</a:majorFont><a:minorFont>${fonts}</a:minorFont></a:fontScheme>${fmt}</a:themeElements><a:objectDefaults/><a:extraClrSchemeLst/></a:theme>`);
    const ext = [...new Set(this.mediaFiles.map(p => path.extname(p).toLowerCase().slice(1)))];
    const mime = { jpg: 'image/jpeg', jpeg: 'image/jpeg', png: 'image/png' };
    zip.file('[Content_Types].xml', DECL + `<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>${ext.map(e => `<Default Extension="${e}" ContentType="${mime[e]}"/>`).join('')}`
      + '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/><Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>'
      + layouts.map((_, i) => `<Override PartName="/ppt/slideLayouts/slideLayout${i + 1}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>`).join('')
      + this.slides.map((_, i) => `<Override PartName="/ppt/slides/slide${i + 1}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>`).join('')
      + '<Override PartName="/ppt/presProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"/><Override PartName="/ppt/viewProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml"/>'
      + '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/><Override PartName="/ppt/tableStyles.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.tableStyles+xml"/>'
      + '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/><Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/></Types>');
    zip.file('_rels/.rels', DECL + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/></Relationships>');
    const now = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
    zip.file('docProps/core.xml', DECL + `<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>${esc(this.title)}</dc:title><dcterms:created xsi:type="dcterms:W3CDTF">${now}</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">${now}</dcterms:modified></cp:coreProperties>`);
    zip.file('docProps/app.xml', DECL + `<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>Microsoft Office PowerPoint</Application><Slides>${n}</Slides></Properties>`);
    fs.writeFileSync(fileName, await zip.generateAsync({ type: 'nodebuffer', compression: 'DEFLATE' }));
    return fileName;
  }
}
module.exports = Pres;
