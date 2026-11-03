#!/usr/bin/env python3
"""랩미팅 자료(개체 해소·연결, 저장, 검색·답변)의 그림 HTML을 만든다. 값은 kgv4_*.csv와 서버 실행 기록(server_runs_20261016)의 실제 값이다.
출력: lab_meeting/how2/fig/kg2_figs.html  (그림마다 <div class="fig" id="...">, 렌더는 playwright로 id별 캡처)
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'lab_meeting', 'how2', 'fig')
HEAD = open(os.path.join(OUT, 'head.html'), encoding='utf-8').read()

CSS = '''<style>
.k2{display:grid;gap:10px 0;align-items:center}
.nd{display:inline-block;border-radius:8px;padding:5px 10px;font-weight:bold;white-space:nowrap;border:2px solid}
.dam{border-color:#E07A2F;background:#FFF4EA}
.apr{border-color:#23907F;background:#E8F5F2}
.opr{border-color:#8A55C2;background:#F3ECFA}
.hms{border-color:#2F66D0;background:#EEF2FB}
.cri{border-color:#C77A1E;background:#FDF3E3}
.evi{border-color:#7A7A7A;background:#F2F2F2}
.rel{font-size:13.5px;font-weight:bold;color:#2F4F9A;white-space:nowrap}
.code{font-family:"DejaVu Sans Mono",monospace;font-size:13px;background:#F7F7F5;border:1.5px solid #ddd;border-radius:8px;padding:8px 10px;white-space:pre-wrap;line-height:1.5}
.hl1{background:#FFE7C2}.hl2{background:#D9F0E8}.hl3{background:#E4E9FA}.hl4{background:#F3E6FA}
.tagL{display:inline-block;border-radius:5px;padding:1px 7px;font-size:12.5px;font-weight:bold;color:#fff}
.llm{background:#B3261E}.cd{background:#2F66D0}
.step{border:1.5px solid var(--line);border-radius:9px;padding:8px 10px;background:#fff;font-size:14.5px}
.arrow{font-size:20px;color:#555;text-align:center}
</style>'''

F = []
add = F.append

# ================================================================== 2장 개체 해소·연결
add('''<!-- r0: 온톨로지의 짝과 실제 짝 -->
<div class="fig" id="r0">
 <div style="display:grid;grid-template-columns:300px 30px 1fr;align-items:center;gap:0 6px">
  <div class="step" style="background:#FFF8E6;border-color:#D9B44A;text-align:center"><span class="hd">온톨로지 (Class 사이의 관계)</span><br><span class="nd apr" style="margin-top:6px">Approval</span> <span class="rel">— concernsDam →</span> <span class="nd dam">Dam</span><br><span class="note">"승인은 어떤 댐에 관한 것이다" (규칙 한 줄)</span></div>
  <div class="arrow">→</div>
  <div class="step"><span class="hd">KG (Entity 사이의 실제 관계) — 승인 504행의 관측소코드 = <b style="color:var(--key)">1003110</b></span>
   <svg width="470" height="190" viewBox="0 0 470 190" font-family="WenQuanYi Zen Hei" font-size="14">
    <defs><marker id="mr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#444"/></marker></defs>
    <rect x="10" y="75" width="120" height="40" rx="8" fill="#E8F5F2" stroke="#23907F" stroke-width="2.5"/><text x="70" y="100" text-anchor="middle" font-weight="bold">APR:504</text>
    <g font-size="13.5">
     <rect x="300" y="8" width="160" height="34" rx="7" fill="#FFF4EA" stroke="#E07A2F" stroke-width="3"/><text x="380" y="30" text-anchor="middle" font-weight="bold">DAM:1003110 충주</text>
     <rect x="300" y="54" width="160" height="34" rx="7" fill="#fff" stroke="#ccc" stroke-width="1.5"/><text x="380" y="76" text-anchor="middle" fill="#999">DAM:1012110 소양강</text>
     <rect x="300" y="100" width="160" height="34" rx="7" fill="#fff" stroke="#ccc" stroke-width="1.5"/><text x="380" y="122" text-anchor="middle" fill="#999">DAM:1006110 횡성</text>
     <rect x="300" y="146" width="160" height="34" rx="7" fill="#fff" stroke="#ccc" stroke-width="1.5"/><text x="380" y="168" text-anchor="middle" fill="#999">DAM:1001210 광동</text>
    </g>
    <line x1="130" y1="90" x2="296" y2="26" stroke="#444" stroke-width="2.8" marker-end="url(#mr)"/>
    <line x1="130" y1="95" x2="296" y2="71" stroke="#bbb" stroke-width="1.5" stroke-dasharray="5 4"/>
    <line x1="130" y1="100" x2="296" y2="117" stroke="#bbb" stroke-width="1.5" stroke-dasharray="5 4"/>
    <line x1="130" y1="105" x2="296" y2="163" stroke="#bbb" stroke-width="1.5" stroke-dasharray="5 4"/>
    <text x="140" y="56" font-size="12.5" fill="#2F4F9A" font-weight="bold">concernsDam</text>
   </svg>
  </div>
 </div>
 <div class="note" style="margin-top:8px">온톨로지 규칙만 보면 승인 80개 × 댐 4개 = 320가지 조합이 모두 형식상 맞다(점선). 그중 실제 관계 80개를 고르는 근거가 자료 안의 키이다(실선: 관측소코드 1003110 → 충주댐).</div>
</div>''')

add('''<!-- g1: 댐 표기 맞추기 -->
<div class="fig" id="g1">
 <svg width="808" height="300" viewBox="0 0 808 300" font-family="WenQuanYi Zen Hei" font-size="13.5"><defs><marker id="a1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#444"/></marker><marker id="a1g" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#aaa"/></marker></defs><text x="2" y="14" font-size="12.5" fill="#555" font-weight="bold">① 승인 기록 504행</text><rect x="2" y="20" width="90" height="26" fill="#2F66D0"/><text x="47" y="38" text-anchor="middle" fill="#fff" font-weight="bold" font-size="12.5">관측소코드</text><rect x="92" y="20" width="70" height="26" fill="#888"/><text x="127" y="38" text-anchor="middle" fill="#fff" font-weight="bold" font-size="12.5">관측소명</text><rect x="2" y="46" width="160" height="30" fill="#FFF1C9" stroke="#ccc"/><text x="47" y="66" text-anchor="middle" font-weight="bold" fill="#2F66D0">1003110</text><text x="127" y="66" text-anchor="middle">충주</text><text x="2" y="114" font-size="12.5" fill="#555" font-weight="bold">② K-water 시간자료 한 행</text><rect x="2" y="120" width="90" height="26" fill="#2F66D0"/><text x="47" y="138" text-anchor="middle" fill="#fff" font-weight="bold" font-size="12.5">DAM_CD</text><rect x="92" y="120" width="100" height="26" fill="#888"/><text x="142" y="138" text-anchor="middle" fill="#fff" font-weight="bold" font-size="12.5">SDATE</text><rect x="2" y="146" width="190" height="30" fill="#FFF1C9" stroke="#ccc"/><text x="47" y="166" text-anchor="middle" font-weight="bold" fill="#2F66D0">1003110</text><text x="142" y="166" text-anchor="middle">2021010101</text><text x="2" y="214" font-size="12.5" fill="#555" font-weight="bold">③ 규정 별표3 원문의 한 줄 (코드 없음)</text><rect x="2" y="222" width="250" height="30" fill="#FFF1C9" stroke="#ccc"/><text x="10" y="242" font-family="DejaVu Sans Mono" font-size="12.5">│수 계│  │<tspan fill="#C77A1E" font-weight="bold">충 주 댐</tspan>│138.0│</text><g stroke="#444" stroke-width="2" fill="none" marker-end="url(#a1)"><path d="M162,61 C330,61 400,150 556,158"/><path d="M192,161 L556,164"/><path d="M252,237 L330,237"/><path d="M470,237 C520,237 520,195 556,174"/></g><g font-size="12" fill="#2F4F9A" font-weight="bold"><text x="290" y="90">관측소코드 = 댐 코드</text><text x="330" y="156">기준 식별자 그대로</text><text x="200" y="276">공백 빼고 "충주댐"</text></g><rect x="332" y="200" width="138" height="78" rx="6" fill="#fff" stroke="#999"/><text x="401" y="216" text-anchor="middle" font-size="11.5" fill="#555" font-weight="bold">대응 표 (4줄)</text><text x="340" y="236" font-size="11.5">충주댐 → <tspan fill="#2F66D0" font-weight="bold">1003110</tspan></text><text x="340" y="252" font-size="11.5" fill="#999">소양강댐 → 1012110</text><text x="340" y="268" font-size="11.5" fill="#999">횡성댐 → 1006110 …</text><rect x="558" y="140" width="190" height="46" rx="7" fill="#FFF4EA" stroke="#E07A2F" stroke-width="2"/><text x="653" y="161" text-anchor="middle" font-size="15" font-weight="bold">DAM:<tspan fill="#2F66D0">1003110</tspan></text><text x="653" y="175" text-anchor="middle" font-size="11" fill="#555">충주댐</text><text x="560" y="210" font-size="12" fill="#555">세 표기가 모두 이 Entity를 가리킨다</text></svg>
 <div class="d2rq"><b>원리 · Purohit 외(2024)</b> — 기준 식별자(QID)를 정하고, 자료마다 다르게 적힌 같은 대상을 그 식별자에 대응시킨다. 우리의 기준 식별자는 K-water 댐 코드이다.</div>
</div>''')

add('''<!-- g0: 승인 504행 하나에서 나오는 Entity와 관계 -->
<div class="fig" id="g0">
 <svg width="808" height="400" viewBox="0 0 808 400" font-family="WenQuanYi Zen Hei" font-size="13.5">
  <defs>
   <marker id="m0" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#444"/></marker>
   <marker id="m0g" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#aaa"/></marker>
  </defs>
  <text x="2" y="12" font-size="13" fill="#555" font-weight="bold">승인 기록 504행 (approval_records_clean.csv)</text>
  <!-- 머리 -->
  <g font-size="12.5" fill="#fff" font-weight="bold" text-anchor="middle">
   <rect x="2" y="18" width="78" height="26" fill="#E07A2F"/><text x="41" y="36">순차번호</text>
   <rect x="80" y="18" width="92" height="26" fill="#2F66D0"/><text x="126" y="36">관측소코드</text>
   <rect x="172" y="18" width="62" height="26" fill="#888"/><text x="203" y="36">관측소명</text>
   <rect x="234" y="18" width="94" height="26" fill="#3F8F2A"/><text x="281" y="36">승인일</text>
   <rect x="328" y="18" width="150" height="26" fill="#3F8F2A"/><text x="403" y="36">방류시작 · 접수방류량</text>
   <rect x="478" y="18" width="170" height="26" fill="#8A55C2"/><text x="563" y="36">비고</text>
   <rect x="648" y="18" width="158" height="26" fill="#7A7A7A"/><text x="727" y="36">출처 열</text>
  </g>
  <g text-anchor="middle">
   <rect x="2" y="44" width="804" height="36" fill="#FFF1C9" stroke="#C9C9C9"/>
   <text x="41" y="67" font-weight="bold" fill="#E07A2F" font-size="15">504</text>
   <text x="126" y="67" font-weight="bold" fill="#2F66D0">1003110</text>
   <text x="203" y="67">충주</text>
   <text x="281" y="67">2011-06-27</text>
   <text x="403" y="67">2011-06-27 18:00 · 2000</text>
   <text x="563" y="67">(실제방류는 20시부터)</text>
   <text x="727" y="63" font-size="11.5">한강홍수통제소</text><text x="727" y="76" font-size="11.5">댐방류승인 파일 …</text>
  </g>
  <!-- 칸 → Entity (회색 점선) -->
  <g stroke="#aaa" stroke-width="1.6" stroke-dasharray="5 4" fill="none" marker-end="url(#m0g)">
   <path d="M281,80 L240,166"/><path d="M403,80 L262,166"/>
   <path d="M563,80 L520,166"/>
   <path d="M727,80 L727,166"/>
   <path d="M126,80 L126,336 L296,336"/>
  </g>
  <g font-size="11.5" fill="#888">
   <text x="300" y="120">속성값</text>
   <text x="550" y="120">추출(비고 규칙)</text>
   <text x="735" y="120">속성값</text>
   <text x="12" y="240">관측소코드 = 댐 코드</text><text x="12" y="255">→ 댐 Entity를 가리킴</text>
  </g>
  <!-- Entity -->
  <rect x="170" y="168" width="140" height="42" rx="8" fill="#E8F5F2" stroke="#23907F" stroke-width="2.5"/><text x="240" y="194" text-anchor="middle" font-weight="bold">APR:<tspan fill="#E07A2F">504</tspan></text>
  <rect x="450" y="168" width="140" height="42" rx="8" fill="#F3ECFA" stroke="#8A55C2" stroke-width="2.5"/><text x="520" y="194" text-anchor="middle" font-weight="bold">OPR:<tspan fill="#E07A2F">504</tspan>:1</text>
  <rect x="660" y="168" width="140" height="42" rx="8" fill="#F2F2F2" stroke="#7A7A7A" stroke-width="2.5"/><text x="730" y="194" text-anchor="middle" font-weight="bold">EVI:AP:<tspan fill="#E07A2F">504</tspan></text>
  <rect x="300" y="314" width="210" height="44" rx="8" fill="#FFF4EA" stroke="#E07A2F" stroke-width="2.5"/><text x="405" y="333" text-anchor="middle" font-weight="bold">DAM:<tspan fill="#2F66D0">1003110</tspan></text><text x="405" y="350" text-anchor="middle" font-size="11.5">충주댐 (K-water 자료에서 만든 Entity)</text>
  <!-- 관계 -->
  <g stroke="#444" stroke-width="2.4" fill="none" marker-end="url(#m0)">
   <line x1="310" y1="189" x2="446" y2="189"/>
   <line x1="590" y1="189" x2="656" y2="189"/>
   <path d="M240,210 C240,290 730,290 730,214"/>
   <line x1="255" y1="210" x2="355" y2="310"/>
   <line x1="505" y1="210" x2="440" y2="310"/>
  </g>
  <g font-size="12.5" font-weight="bold" fill="#2F4F9A">
   <text x="378" y="182" text-anchor="middle">authorizes</text>
   <text x="623" y="160" text-anchor="middle">supportedBy</text>
   <text x="600" y="282">supportedBy</text>
   <text x="315" y="252">concernsDam</text>
   <text x="470" y="262">performedOnDam</text>
  </g>
 </svg>
 <div class="note">한 행에서 Entity 3개(APR, OPR, EVI:AP)가 나오고, 세 ID에 모두 순차번호 <b style="color:var(--key)">504</b>가 들어간다. 그래서 순차번호만 보면 같은 행에서 나온 Entity끼리의 관계(authorizes, supportedBy)를 바로 정할 수 있다. 댐은 그 행의 관측소코드 <b style="color:#2F66D0">1003110</b>으로 정한다(concernsDam, performedOnDam).</div>
</div>''')

add('''<!-- g7: 근거 관계 4종 -->
<div class="fig" id="g7">
 <table class="t" style="font-size:14.5px;width:100%">
  <tr><th>시작</th><th>짝을 정하는 키</th><th>끝 (근거 Entity)</th><th>개수</th></tr>
  <tr><td><span class="nd apr">APR:<b style="color:var(--key)">504</b></span></td><td>같은 순차번호 504 (같은 승인 행에서 만든 근거)</td><td><span class="nd evi">EVI:AP:<b style="color:var(--key)">504</b></span></td><td>80</td></tr>
  <tr><td><span class="nd opr">OPR:<b style="color:var(--key)">504</b>:1</span></td><td>운영행위 ID의 순차번호 504 (비고가 적힌 승인 행의 근거)</td><td><span class="nd evi">EVI:AP:<b style="color:var(--key)">504</b></span></td><td>68</td></tr>
  <tr><td><span class="nd hms">HMS:<b style="color:var(--key)">1003110</b>:수위</span></td><td>같은 댐 코드 1003110 (그 댐의 측정자료)</td><td><span class="nd evi">EVI:KW:<b style="color:var(--key)">1003110</b></span></td><td>24</td></tr>
  <tr><td><span class="nd cri">CRI:CR-02</span></td><td>규정은 하나라 고정 ID (별표3)</td><td><span class="nd evi">EVI:LAW:별표3</span></td><td>3</td></tr>
 </table>
 <div class="note" style="margin-top:6px">근거 Entity는 10/30 단계에서 이미 만들어 두었다. 시작 Entity의 ID에 든 키(순차번호, 댐 코드)로 끝을 바로 정하므로 다른 표를 찾지 않는다.</div>
</div>''')

add('''<!-- gB: 댐 코드로 채우는 관계 -->
<div class="fig" id="gB">
<svg width="808" height="410" viewBox="0 0 808 410" font-family="WenQuanYi Zen Hei" font-size="13"><defs><marker id="ab" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#444"/></marker><marker id="abg" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#aaa"/></marker></defs>
<text x="2" y="12" font-size="12.5" fill="#555" font-weight="bold">K-water 시간자료 (넓은 표, 충주댐의 한 행)</text>
<rect x="2" y="18" width="96" height="26" fill="#2F66D0"/><text x="50" y="36" text-anchor="middle" fill="#fff" font-weight="bold" font-size="12.5">DAM_CD</text><rect x="100" y="18" width="116" height="26" fill="#E07A2F"/><text x="158" y="36" text-anchor="middle" fill="#fff" font-weight="bold" font-size="12.5">DATA1_수위</text><rect x="218" y="18" width="116" height="26" fill="#E07A2F"/><text x="276" y="36" text-anchor="middle" fill="#fff" font-weight="bold" font-size="12.5">DATA2_저수량</text><rect x="336" y="18" width="116" height="26" fill="#E07A2F"/><text x="394" y="36" text-anchor="middle" fill="#fff" font-weight="bold" font-size="12.5">DATA3_강우량</text><rect x="454" y="18" width="116" height="26" fill="#E07A2F"/><text x="512" y="36" text-anchor="middle" fill="#fff" font-weight="bold" font-size="12.5">DATA4_유입량</text><rect x="572" y="18" width="116" height="26" fill="#E07A2F"/><text x="630" y="36" text-anchor="middle" fill="#fff" font-weight="bold" font-size="12.5">DATA6_총방류량</text><rect x="690" y="18" width="116" height="26" fill="#E07A2F"/><text x="748" y="36" text-anchor="middle" fill="#fff" font-weight="bold" font-size="12.5">DATA7_저수율</text>
<rect x="2" y="44" width="804" height="28" fill="#FFF1C9" stroke="#ccc"/><text x="50" y="63" text-anchor="middle" font-weight="bold" fill="#2F66D0">1003110</text>
<text x="158" y="63" text-anchor="middle" fill="#777">131.55</text>
<path d="M158,72 L158,148" stroke="#aaa" stroke-width="1.5" stroke-dasharray="5 4" fill="none" marker-end="url(#abg)"/>
<line x1="310" y1="298" x2="158" y2="192" stroke="#444" stroke-width="1.8" marker-end="url(#ab)"/>
<line x1="158" y1="192" x2="570" y2="298" stroke="#888" stroke-width="1.4" marker-end="url(#ab)"/>
<text x="276" y="63" text-anchor="middle" fill="#777">1484.5892</text>
<path d="M276,72 L276,148" stroke="#aaa" stroke-width="1.5" stroke-dasharray="5 4" fill="none" marker-end="url(#abg)"/>
<line x1="310" y1="298" x2="276" y2="192" stroke="#444" stroke-width="1.8" marker-end="url(#ab)"/>
<line x1="276" y1="192" x2="570" y2="298" stroke="#888" stroke-width="1.4" marker-end="url(#ab)"/>
<text x="394" y="63" text-anchor="middle" fill="#777">0</text>
<path d="M394,72 L394,148" stroke="#aaa" stroke-width="1.5" stroke-dasharray="5 4" fill="none" marker-end="url(#abg)"/>
<line x1="310" y1="298" x2="394" y2="192" stroke="#444" stroke-width="1.8" marker-end="url(#ab)"/>
<line x1="394" y1="192" x2="570" y2="298" stroke="#888" stroke-width="1.4" marker-end="url(#ab)"/>
<text x="512" y="63" text-anchor="middle" fill="#777">186.52</text>
<path d="M512,72 L512,148" stroke="#aaa" stroke-width="1.5" stroke-dasharray="5 4" fill="none" marker-end="url(#abg)"/>
<line x1="310" y1="298" x2="512" y2="192" stroke="#444" stroke-width="1.8" marker-end="url(#ab)"/>
<line x1="512" y1="192" x2="570" y2="298" stroke="#888" stroke-width="1.4" marker-end="url(#ab)"/>
<text x="630" y="63" text-anchor="middle" fill="#777">0.159</text>
<path d="M630,72 L630,148" stroke="#aaa" stroke-width="1.5" stroke-dasharray="5 4" fill="none" marker-end="url(#abg)"/>
<line x1="310" y1="298" x2="630" y2="192" stroke="#444" stroke-width="1.8" marker-end="url(#ab)"/>
<line x1="630" y1="192" x2="570" y2="298" stroke="#888" stroke-width="1.4" marker-end="url(#ab)"/>
<text x="748" y="63" text-anchor="middle" fill="#777">53.99</text>
<path d="M748,72 L748,148" stroke="#aaa" stroke-width="1.5" stroke-dasharray="5 4" fill="none" marker-end="url(#abg)"/>
<line x1="310" y1="298" x2="748" y2="192" stroke="#444" stroke-width="1.8" marker-end="url(#ab)"/>
<line x1="748" y1="192" x2="570" y2="298" stroke="#888" stroke-width="1.4" marker-end="url(#ab)"/>
<rect x="104" y="150" width="110" height="40" rx="7" fill="#EEF2FB" stroke="#2F66D0" stroke-width="2"/><text x="159" y="168" text-anchor="middle" font-size="11.5" font-weight="bold">HMS:<tspan fill="#2F66D0">1003110</tspan></text><text x="159" y="182" text-anchor="middle" font-size="11" fill="#555">수위</text>
<rect x="222" y="150" width="110" height="40" rx="7" fill="#EEF2FB" stroke="#2F66D0" stroke-width="2"/><text x="277" y="168" text-anchor="middle" font-size="11.5" font-weight="bold">HMS:<tspan fill="#2F66D0">1003110</tspan></text><text x="277" y="182" text-anchor="middle" font-size="11" fill="#555">저수량</text>
<rect x="340" y="150" width="110" height="40" rx="7" fill="#EEF2FB" stroke="#2F66D0" stroke-width="2"/><text x="395" y="168" text-anchor="middle" font-size="11.5" font-weight="bold">HMS:<tspan fill="#2F66D0">1003110</tspan></text><text x="395" y="182" text-anchor="middle" font-size="11" fill="#555">강우량</text>
<rect x="458" y="150" width="110" height="40" rx="7" fill="#EEF2FB" stroke="#2F66D0" stroke-width="2"/><text x="513" y="168" text-anchor="middle" font-size="11.5" font-weight="bold">HMS:<tspan fill="#2F66D0">1003110</tspan></text><text x="513" y="182" text-anchor="middle" font-size="11" fill="#555">유입량</text>
<rect x="576" y="150" width="110" height="40" rx="7" fill="#EEF2FB" stroke="#2F66D0" stroke-width="2"/><text x="631" y="168" text-anchor="middle" font-size="11.5" font-weight="bold">HMS:<tspan fill="#2F66D0">1003110</tspan></text><text x="631" y="182" text-anchor="middle" font-size="11" fill="#555">총방류량</text>
<rect x="694" y="150" width="110" height="40" rx="7" fill="#EEF2FB" stroke="#2F66D0" stroke-width="2"/><text x="749" y="168" text-anchor="middle" font-size="11.5" font-weight="bold">HMS:<tspan fill="#2F66D0">1003110</tspan></text><text x="749" y="182" text-anchor="middle" font-size="11" fill="#555">저수율</text>
<text x="600" y="112" font-size="11.5" fill="#888">열 머리(변수)마다 HMS 하나</text>
<rect x="220" y="300" width="180" height="44" rx="7" fill="#FFF4EA" stroke="#E07A2F" stroke-width="2"/><text x="310" y="320" text-anchor="middle" font-size="14" font-weight="bold">DAM:<tspan fill="#2F66D0">1003110</tspan></text><text x="310" y="334" text-anchor="middle" font-size="11" fill="#555">충주댐 (일자료에서)</text>
<rect x="470" y="300" width="200" height="44" rx="7" fill="#F2F2F2" stroke="#7A7A7A" stroke-width="2"/><text x="570" y="320" text-anchor="middle" font-size="14" font-weight="bold">EVI:KW:<tspan fill="#2F66D0">1003110</tspan></text><text x="570" y="334" text-anchor="middle" font-size="11" fill="#555">충주댐 측정자료 근거</text>
<text x="96" y="262" font-size="12.5" font-weight="bold" fill="#2F4F9A">hasHydrometeorologicalState ×6</text>
<text x="600" y="262" font-size="12.5" font-weight="bold" fill="#2F4F9A">supportedBy ×6</text>
<path d="M50,72 C50,250 120,322 218,322" stroke="#aaa" stroke-width="1.5" stroke-dasharray="5 4" fill="none" marker-end="url(#abg)"/>
<text x="8" y="385" font-size="12" fill="#555">세 종류 Entity의 ID에 모두 같은 댐 코드 <tspan fill="#2F66D0" font-weight="bold">1003110</tspan>이 들어 있어, 코드가 같은 것끼리 잇는다.</text>
</svg>
</div>''')

add('''<!-- gC: 별표3 댐 이름으로 채우는 관계 -->
<div class="fig" id="gC">
 <svg width="808" height="330" viewBox="0 0 808 330" font-family="WenQuanYi Zen Hei" font-size="13"><defs><marker id="ac" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#444"/></marker><marker id="acg" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#aaa"/></marker></defs><text x="2" y="12" font-size="12.5" fill="#555" font-weight="bold">비정형 텍스트 추출로 만든 중간 파일 criterion_list.csv의 한 줄</text><rect x="2" y="18" width="90" height="26" fill="#C77A1E"/><text x="47" y="36" text-anchor="middle" fill="#fff" font-weight="bold" font-size="12.5">번호</text><rect x="92" y="18" width="120" height="26" fill="#C77A1E"/><text x="152" y="36" text-anchor="middle" fill="#fff" font-weight="bold" font-size="12.5">댐 (별표3 원문)</text><rect x="212" y="18" width="150" height="26" fill="#888"/><text x="287" y="36" text-anchor="middle" fill="#fff" font-weight="bold" font-size="12.5">제한수위 칸</text><rect x="2" y="44" width="360" height="30" fill="#FFF1C9" stroke="#ccc"/><text x="47" y="64" text-anchor="middle" font-weight="bold">CR-02</text><text x="152" y="64" text-anchor="middle" font-weight="bold" fill="#C77A1E">충주댐</text><text x="287" y="64" text-anchor="middle">'138.0'</text><rect x="20" y="170" width="170" height="44" rx="7" fill="#FDF3E3" stroke="#C77A1E" stroke-width="2"/><text x="105" y="190" text-anchor="middle" font-size="14" font-weight="bold">CRI:CR-02</text><text x="105" y="204" text-anchor="middle" font-size="11" fill="#555">홍수기 제한수위 138.0</text><path d="M47,74 L90,168" stroke="#aaa" stroke-width="1.5" stroke-dasharray="5 4" fill="none" marker-end="url(#acg)"/><rect x="420" y="20" width="200" height="96" rx="6" fill="#fff" stroke="#999"/><text x="520" y="38" text-anchor="middle" font-size="12" fill="#555" font-weight="bold">대응 표: 표준 댐명 → 댐 코드</text><text x="432" y="60" font-size="12.5" fill="#999">소양강댐 → 1012110</text><rect x="428" y="66" width="184" height="22" fill="#FFF1C9"/><text x="432" y="82" font-size="12.5" font-weight="bold">충주댐 → <tspan fill="#2F66D0">1003110</tspan></text><text x="432" y="106" font-size="12.5" fill="#999">횡성댐 → 1006110 …</text><path d="M212,59 L418,77" stroke="#aaa" stroke-width="1.5" stroke-dasharray="5 4" fill="none" marker-end="url(#acg)"/><text x="240" y="98" font-size="11.5" fill="#888">같은 이름을 찾는다</text><rect x="430" y="170" width="180" height="44" rx="7" fill="#FFF4EA" stroke="#E07A2F" stroke-width="2"/><text x="520" y="190" text-anchor="middle" font-size="14" font-weight="bold">DAM:<tspan fill="#2F66D0">1003110</tspan></text><text x="520" y="204" text-anchor="middle" font-size="11" fill="#555">충주댐</text><path d="M520,116 L520,168" stroke="#aaa" stroke-width="1.5" stroke-dasharray="5 4" fill="none" marker-end="url(#acg)"/><line x1="190" y1="192" x2="428" y2="192" stroke="#444" stroke-width="2.4" marker-end="url(#ac)"/><text x="309" y="184" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#2F4F9A">appliesToDam</text><text x="309" y="210" text-anchor="middle" font-size="11.5" fill="#888">(값의 성격: 이름 일치)</text><rect x="20" y="270" width="170" height="44" rx="7" fill="#F2F2F2" stroke="#7A7A7A" stroke-width="2"/><text x="105" y="290" text-anchor="middle" font-size="13.5" font-weight="bold">EVI:LAW:별표3</text><text x="105" y="304" text-anchor="middle" font-size="11" fill="#555">연계운영규정 별표3</text><line x1="105" y1="214" x2="105" y2="268" stroke="#444" stroke-width="2.4" marker-end="url(#ac)"/><text x="115" y="248" font-size="12.5" font-weight="bold" fill="#2F4F9A">supportedBy</text><text x="230" y="290" font-size="12" fill="#555">규정은 하나라 근거 Entity도 하나(고정 ID)이다.</text><text x="230" y="306" font-size="12" fill="#555">기준 3개(CR-01, 02, 03)가 모두 이 Entity를 끝 Entity로 한다.</text></svg>
</div>''')

add('''<!-- g2: hasHydrometeorologicalState -->
<div class="fig" id="g2">
 <div style="display:flex;align-items:center;gap:14px">
  <div class="step" style="flex:0 0 250px"><span class="hd">시작: Dam</span><br><span class="nd dam">DAM:1003110</span><br><span class="note">ID 속의 댐 코드 <b style="color:var(--key)">1003110</b></span></div>
  <div style="flex:0 0 190px;text-align:center"><div class="rel">hasHydrometeorologicalState</div><div style="border-top:2.5px solid #444;margin:2px 6px;position:relative"><span style="position:absolute;right:-6px;top:-11px;font-size:16px">▶</span></div><div class="note" style="font-size:13px">같은 댐 코드</div></div>
  <div class="step" style="flex:1"><span class="hd">끝: HMS (stationCode = 1003110인 것 6개)</span><br><span class="nd hms">HMS:<b style="color:var(--key)">1003110</b>:수위</span> <span class="nd hms">…:저수량</span> <span class="nd hms">…:강우량</span><br><span class="nd hms" style="margin-top:4px">…:유입량</span> <span class="nd hms">…:총방류량</span> <span class="nd hms">…:저수율</span></div>
 </div>
 <div class="note" style="margin-top:8px">① 댐을 하나씩 꺼낸다 → ② 같은 댐 코드로 만든 HMS 6개를 찾는다 → ③ 관계 줄 6개를 쓴다. 4개 댐 × 6 = 24개. 값의 성격: 원본 그대로(코드 일치).</div>
</div>''')

add('''<!-- g3: concernsDam -->
<div class="fig" id="g3">
 <div style="display:flex;align-items:center;gap:14px">
  <div class="step" style="flex:0 0 250px"><span class="hd">시작: Approval</span><br><span class="nd apr">APR:504</span><br><span class="note">승인 504행의 관측소코드 = <b style="color:var(--key)">1003110</b></span></div>
  <div style="flex:0 0 150px;text-align:center"><div class="rel">concernsDam</div><div style="border-top:2.5px solid #444;margin:2px 6px;position:relative"><span style="position:absolute;right:-6px;top:-11px;font-size:16px">▶</span></div><div class="note" style="font-size:13px">관측소코드 = 댐 코드</div></div>
  <div class="step" style="flex:1"><span class="hd">끝: Dam</span><br><span class="nd dam">DAM:<b style="color:var(--key)">1003110</b></span> <span class="note">충주댐</span></div>
 </div>
 <table class="t" style="margin-top:10px;font-size:14px">
  <tr><th>순차번호</th><th style="background:var(--key)">관측소코드</th><th>관측소명</th><th>→ 시작 Entity</th><th>→ 끝 Entity</th></tr>
  <tr class="hl"><td>504</td><td>1003110</td><td>충주</td><td>APR:504</td><td>DAM:1003110</td></tr>
  <tr><td>473</td><td>1006110</td><td>횡성</td><td>APR:473</td><td>DAM:1006110</td></tr>
  <tr class="dim"><td colspan="5" style="text-align:center">… 승인 80개 → 80개 모두 댐 하나에 이어짐 (충주 15, 소양강 6, 횡성 24, 광동 35)</td></tr>
 </table>
</div>''')

add('''<!-- g4: authorizes, performedOnDam -->
<div class="fig" id="g4">
 <div style="display:grid;grid-template-columns:1fr 1fr 1fr;align-items:center;gap:0 6px;text-align:center">
  <div class="step"><span class="hd">같은 승인 504행</span><br>비고 "(실제방류는 20시부터)"<br>관측소코드 <b style="color:var(--key)">1003110</b></div>
  <div></div><div></div>
 </div>
 <svg width="808" height="210" viewBox="0 0 808 210" font-family="WenQuanYi Zen Hei" font-size="15">
  <defs><marker id="m4" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#444"/></marker></defs>
  <rect x="20" y="70" width="150" height="44" rx="8" fill="#E8F5F2" stroke="#23907F" stroke-width="2.5"/><text x="95" y="98" text-anchor="middle" font-weight="bold">APR:504</text>
  <rect x="330" y="70" width="160" height="44" rx="8" fill="#F3ECFA" stroke="#8A55C2" stroke-width="2.5"/><text x="410" y="98" text-anchor="middle" font-weight="bold">OPR:504:1</text>
  <rect x="640" y="70" width="150" height="44" rx="8" fill="#FFF4EA" stroke="#E07A2F" stroke-width="2.5"/><text x="715" y="98" text-anchor="middle" font-weight="bold">DAM:1003110</text>
  <line x1="170" y1="92" x2="326" y2="92" stroke="#444" stroke-width="2.5" marker-end="url(#m4)"/>
  <text x="248" y="82" text-anchor="middle" font-weight="bold" fill="#2F4F9A">authorizes</text>
  <text x="248" y="134" text-anchor="middle" font-size="13" fill="#555">같은 순차번호 504</text>
  <text x="248" y="152" text-anchor="middle" font-size="13" fill="#555">(그 행의 비고에서 뽑은 행위)</text>
  <line x1="490" y1="92" x2="636" y2="92" stroke="#444" stroke-width="2.5" marker-end="url(#m4)"/>
  <text x="563" y="82" text-anchor="middle" font-weight="bold" fill="#2F4F9A">performedOnDam</text>
  <text x="563" y="134" text-anchor="middle" font-size="13" fill="#555">504 → 승인 504행의</text>
  <text x="563" y="152" text-anchor="middle" font-size="13" fill="#555">관측소코드 1003110</text>
  <path d="M95,70 C95,20 715,20 715,66" fill="none" stroke="#999" stroke-width="2" stroke-dasharray="6 5" marker-end="url(#m4)"/>
  <text x="405" y="30" text-anchor="middle" font-size="13" fill="#777">concernsDam</text>
  <text x="20" y="196" font-size="13.5" fill="#555">운영행위 ID의 순차번호(504)가 같은 승인 행을 가리키므로, 승인과 댐을 다른 표에서 찾지 않는다.</text>
 </svg>
 <div class="note">authorizes 68개(값의 성격: 연구용 구성 — 실행 확인 아님), performedOnDam 68개(값의 성격: 원본에서 유도). 운영행위 68개가 모두 승인 하나와 댐 하나에 이어진다.</div>
</div>''')

add('''<!-- g5: appliesToDam -->
<div class="fig" id="g5">
 <div style="display:grid;grid-template-columns:250px 34px 270px 34px 1fr;align-items:center">
  <div class="cv"><span class="nd cri">CRI:CR-02</span><br>중간 파일의 댐 칸<br><b>충주댐</b> <span class="note">(별표3 원문 "충 주 댐")</span></div><div class="ar">→</div>
  <div class="rl">대응 표의 <b>표준 댐명</b>에서 같은 이름을 찾아 그 댐 코드를 꺼낸다<br><span class="note">별표3에는 코드가 없다</span></div><div class="ar">→</div>
  <div class="out"><span class="rel">appliesToDam</span> → <span class="nd dam">DAM:1003110</span></div>
 </div>
 <div class="note" style="margin-top:8px">기준 3개 → 충주(CR-02), 소양강(CR-01), 횡성(CR-03) 각각 댐 하나. 값의 성격: 이름 일치(name-match) — 코드가 아니라 이름으로 찾은 연결임을 관계에 남긴다.</div>
</div>''')

add('''<!-- g6: 충주댐 KG 전체 -->
<div class="fig" id="g6">
<svg width="808" height="760" viewBox="0 0 808 760" font-family="WenQuanYi Zen Hei" font-size="11"><defs><marker id="a6" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#444"/></marker><marker id="a6g" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#aaa"/></marker></defs><g font-size="12" font-weight="bold" fill="#555"><text x="8" y="26">근거(승인자료) 15</text><text x="128" y="26">승인 15</text><text x="262" y="26">운영행위 14</text><text x="690" y="44">수문·기상 상태 6</text></g><line x1="128" y1="52" x2="106" y2="52" stroke="#999" stroke-width="1.2" marker-end="url(#a6)"/><line x1="228" y1="52" x2="485" y2="400" stroke="#23907F" stroke-width="0.9" opacity="0.6"/><line x1="228" y1="52" x2="260" y2="52" stroke="#444" stroke-width="1.2" marker-end="url(#a6)"/><line x1="412" y1="52" x2="485" y2="400" stroke="#8A55C2" stroke-width="0.9" opacity="0.6"/><path d="M292,40 C252,18 128,18 88,40" stroke="#bbb" stroke-width="0.9" fill="none"/><line x1="128" y1="84" x2="106" y2="84" stroke="#999" stroke-width="1.2" marker-end="url(#a6)"/><line x1="228" y1="84" x2="485" y2="400" stroke="#23907F" stroke-width="0.9" opacity="0.6"/><line x1="228" y1="84" x2="260" y2="84" stroke="#444" stroke-width="1.2" marker-end="url(#a6)"/><line x1="412" y1="84" x2="485" y2="400" stroke="#8A55C2" stroke-width="0.9" opacity="0.6"/><path d="M292,72 C252,50 128,50 88,72" stroke="#bbb" stroke-width="0.9" fill="none"/><line x1="128" y1="116" x2="106" y2="116" stroke="#999" stroke-width="1.2" marker-end="url(#a6)"/><line x1="228" y1="116" x2="485" y2="400" stroke="#23907F" stroke-width="0.9" opacity="0.6"/><line x1="228" y1="116" x2="260" y2="116" stroke="#444" stroke-width="1.2" marker-end="url(#a6)"/><line x1="412" y1="116" x2="485" y2="400" stroke="#8A55C2" stroke-width="0.9" opacity="0.6"/><path d="M292,104 C252,82 128,82 88,104" stroke="#bbb" stroke-width="0.9" fill="none"/><line x1="128" y1="148" x2="106" y2="148" stroke="#999" stroke-width="1.2" marker-end="url(#a6)"/><line x1="228" y1="148" x2="485" y2="400" stroke="#23907F" stroke-width="0.9" opacity="0.6"/><line x1="228" y1="148" x2="260" y2="148" stroke="#444" stroke-width="1.2" marker-end="url(#a6)"/><line x1="412" y1="148" x2="485" y2="400" stroke="#8A55C2" stroke-width="0.9" opacity="0.6"/><path d="M292,136 C252,114 128,114 88,136" stroke="#bbb" stroke-width="0.9" fill="none"/><line x1="128" y1="180" x2="106" y2="180" stroke="#999" stroke-width="1.2" marker-end="url(#a6)"/><line x1="228" y1="180" x2="485" y2="400" stroke="#23907F" stroke-width="0.9" opacity="0.6"/><line x1="228" y1="180" x2="260" y2="180" stroke="#444" stroke-width="1.2" marker-end="url(#a6)"/><line x1="412" y1="180" x2="485" y2="400" stroke="#8A55C2" stroke-width="0.9" opacity="0.6"/><path d="M292,168 C252,146 128,146 88,168" stroke="#bbb" stroke-width="0.9" fill="none"/><line x1="128" y1="212" x2="106" y2="212" stroke="#999" stroke-width="1.2" marker-end="url(#a6)"/><line x1="228" y1="212" x2="485" y2="400" stroke="#23907F" stroke-width="0.9" opacity="0.6"/><line x1="228" y1="212" x2="260" y2="212" stroke="#444" stroke-width="1.2" marker-end="url(#a6)"/><line x1="412" y1="212" x2="485" y2="400" stroke="#8A55C2" stroke-width="0.9" opacity="0.6"/><path d="M292,200 C252,178 128,178 88,200" stroke="#bbb" stroke-width="0.9" fill="none"/><line x1="128" y1="244" x2="106" y2="244" stroke="#999" stroke-width="1.2" marker-end="url(#a6)"/><line x1="228" y1="244" x2="485" y2="400" stroke="#23907F" stroke-width="0.9" opacity="0.6"/><line x1="228" y1="244" x2="260" y2="244" stroke="#444" stroke-width="1.2" marker-end="url(#a6)"/><line x1="412" y1="244" x2="485" y2="400" stroke="#8A55C2" stroke-width="0.9" opacity="0.6"/><path d="M292,232 C252,210 128,210 88,232" stroke="#bbb" stroke-width="0.9" fill="none"/><line x1="128" y1="276" x2="106" y2="276" stroke="#999" stroke-width="1.2" marker-end="url(#a6)"/><line x1="228" y1="276" x2="485" y2="400" stroke="#23907F" stroke-width="0.9" opacity="0.6"/><line x1="228" y1="276" x2="260" y2="276" stroke="#444" stroke-width="1.2" marker-end="url(#a6)"/><line x1="412" y1="276" x2="485" y2="400" stroke="#8A55C2" stroke-width="0.9" opacity="0.6"/><path d="M292,264 C252,242 128,242 88,264" stroke="#bbb" stroke-width="0.9" fill="none"/><line x1="128" y1="308" x2="106" y2="308" stroke="#999" stroke-width="1.2" marker-end="url(#a6)"/><line x1="228" y1="308" x2="485" y2="400" stroke="#23907F" stroke-width="0.9" opacity="0.6"/><line x1="228" y1="308" x2="260" y2="308" stroke="#444" stroke-width="1.2" marker-end="url(#a6)"/><line x1="412" y1="308" x2="485" y2="400" stroke="#8A55C2" stroke-width="0.9" opacity="0.6"/><path d="M292,296 C252,274 128,274 88,296" stroke="#bbb" stroke-width="0.9" fill="none"/><line x1="128" y1="355" x2="106" y2="355" stroke="#999" stroke-width="1.2" marker-end="url(#a6)"/><line x1="228" y1="355" x2="485" y2="400" stroke="#23907F" stroke-width="0.9" opacity="0.6"/><line x1="228" y1="355" x2="260" y2="340" stroke="#444" stroke-width="1.2" marker-end="url(#a6)"/><line x1="412" y1="340" x2="485" y2="400" stroke="#8A55C2" stroke-width="0.9" opacity="0.6"/><path d="M292,328 C252,306 128,321 88,343" stroke="#bbb" stroke-width="0.9" fill="none"/><line x1="228" y1="355" x2="260" y2="370" stroke="#444" stroke-width="1.2" marker-end="url(#a6)"/><line x1="412" y1="370" x2="485" y2="400" stroke="#8A55C2" stroke-width="0.9" opacity="0.6"/><path d="M292,358 C252,336 128,321 88,343" stroke="#bbb" stroke-width="0.9" fill="none"/><line x1="128" y1="402" x2="106" y2="402" stroke="#999" stroke-width="1.2" marker-end="url(#a6)"/><line x1="228" y1="402" x2="485" y2="400" stroke="#23907F" stroke-width="0.9" opacity="0.6"/><line x1="228" y1="402" x2="260" y2="402" stroke="#444" stroke-width="1.2" marker-end="url(#a6)"/><line x1="412" y1="402" x2="485" y2="400" stroke="#8A55C2" stroke-width="0.9" opacity="0.6"/><path d="M292,390 C252,368 128,368 88,390" stroke="#bbb" stroke-width="0.9" fill="none"/><line x1="128" y1="434" x2="106" y2="434" stroke="#999" stroke-width="1.2" marker-end="url(#a6)"/><line x1="228" y1="434" x2="485" y2="400" stroke="#23907F" stroke-width="0.9" opacity="0.6"/><line x1="228" y1="434" x2="260" y2="434" stroke="#444" stroke-width="1.2" marker-end="url(#a6)"/><line x1="412" y1="434" x2="485" y2="400" stroke="#8A55C2" stroke-width="0.9" opacity="0.6"/><path d="M292,422 C252,400 128,400 88,422" stroke="#bbb" stroke-width="0.9" fill="none"/><line x1="128" y1="466" x2="106" y2="466" stroke="#999" stroke-width="1.2" marker-end="url(#a6)"/><line x1="228" y1="466" x2="485" y2="400" stroke="#23907F" stroke-width="0.9" opacity="0.6"/><line x1="128" y1="498" x2="106" y2="498" stroke="#999" stroke-width="1.2" marker-end="url(#a6)"/><line x1="228" y1="498" x2="485" y2="400" stroke="#23907F" stroke-width="0.9" opacity="0.6"/><line x1="128" y1="530" x2="106" y2="530" stroke="#999" stroke-width="1.2" marker-end="url(#a6)"/><line x1="228" y1="530" x2="485" y2="400" stroke="#23907F" stroke-width="0.9" opacity="0.6"/><line x1="228" y1="530" x2="260" y2="530" stroke="#444" stroke-width="1.2" marker-end="url(#a6)"/><line x1="412" y1="530" x2="485" y2="400" stroke="#8A55C2" stroke-width="0.9" opacity="0.6"/><path d="M292,518 C252,496 128,496 88,518" stroke="#bbb" stroke-width="0.9" fill="none"/><line x1="600" y1="376" x2="688" y2="70" stroke="#2F66D0" stroke-width="1" marker-end="url(#a6)"/><line x1="802" y1="70" x2="807" y2="70" stroke="#999" stroke-width="1.2"/><line x1="600" y1="376" x2="688" y2="106" stroke="#2F66D0" stroke-width="1" marker-end="url(#a6)"/><line x1="802" y1="106" x2="807" y2="106" stroke="#999" stroke-width="1.2"/><line x1="600" y1="376" x2="688" y2="142" stroke="#2F66D0" stroke-width="1" marker-end="url(#a6)"/><line x1="802" y1="142" x2="807" y2="142" stroke="#999" stroke-width="1.2"/><line x1="600" y1="376" x2="688" y2="178" stroke="#2F66D0" stroke-width="1" marker-end="url(#a6)"/><line x1="802" y1="178" x2="807" y2="178" stroke="#999" stroke-width="1.2"/><line x1="600" y1="376" x2="688" y2="214" stroke="#2F66D0" stroke-width="1" marker-end="url(#a6)"/><line x1="802" y1="214" x2="807" y2="214" stroke="#999" stroke-width="1.2"/><line x1="600" y1="376" x2="688" y2="250" stroke="#2F66D0" stroke-width="1" marker-end="url(#a6)"/><line x1="802" y1="250" x2="807" y2="250" stroke="#999" stroke-width="1.2"/><path d="M807,70 L807,330 L795,330" stroke="#999" stroke-width="1.2" fill="none" marker-end="url(#a6)"/><line x1="660" y1="575" x2="580" y2="426" stroke="#C77A1E" stroke-width="1.5" marker-end="url(#a6)"/><line x1="730" y1="600" x2="730" y2="638" stroke="#999" stroke-width="1.2" marker-end="url(#a6)"/><rect x="8" y="40" width="96" height="24" rx="7" fill="#F2F2F2" stroke="#7A7A7A" stroke-width="2"/><text x="56" y="57" text-anchor="middle" font-size="10.5" >EVI:AP:418</text><rect x="128" y="40" width="100" height="24" rx="7" fill="#E8F5F2" stroke="#23907F" stroke-width="2"/><text x="178" y="57" text-anchor="middle" font-size="11" font-weight="bold">APR:418</text><rect x="262" y="40" width="150" height="24" rx="7" fill="#F3ECFA" stroke="#8A55C2" stroke-width="2"/><text x="337" y="57" text-anchor="middle" font-size="10.5" >OPR:418:1 방류</text><rect x="8" y="72" width="96" height="24" rx="7" fill="#F2F2F2" stroke="#7A7A7A" stroke-width="2"/><text x="56" y="89" text-anchor="middle" font-size="10.5" >EVI:AP:504</text><rect x="128" y="72" width="100" height="24" rx="7" fill="#E8F5F2" stroke="#23907F" stroke-width="2"/><text x="178" y="89" text-anchor="middle" font-size="11" font-weight="bold">APR:504</text><rect x="262" y="72" width="150" height="24" rx="7" fill="#F3ECFA" stroke="#8A55C2" stroke-width="2"/><text x="337" y="89" text-anchor="middle" font-size="10.5" >OPR:504:1 방류</text><rect x="8" y="104" width="96" height="24" rx="7" fill="#F2F2F2" stroke="#7A7A7A" stroke-width="2"/><text x="56" y="121" text-anchor="middle" font-size="10.5" >EVI:AP:574</text><rect x="128" y="104" width="100" height="24" rx="7" fill="#E8F5F2" stroke="#23907F" stroke-width="2"/><text x="178" y="121" text-anchor="middle" font-size="11" font-weight="bold">APR:574</text><rect x="262" y="104" width="150" height="24" rx="7" fill="#F3ECFA" stroke="#8A55C2" stroke-width="2"/><text x="337" y="121" text-anchor="middle" font-size="10.5" >OPR:574:1 방류</text><rect x="8" y="136" width="96" height="24" rx="7" fill="#F2F2F2" stroke="#7A7A7A" stroke-width="2"/><text x="56" y="153" text-anchor="middle" font-size="10.5" >EVI:AP:597</text><rect x="128" y="136" width="100" height="24" rx="7" fill="#E8F5F2" stroke="#23907F" stroke-width="2"/><text x="178" y="153" text-anchor="middle" font-size="11" font-weight="bold">APR:597</text><rect x="262" y="136" width="150" height="24" rx="7" fill="#F3ECFA" stroke="#8A55C2" stroke-width="2"/><text x="337" y="153" text-anchor="middle" font-size="10.5" >OPR:597:1 증가방류</text><rect x="8" y="168" width="96" height="24" rx="7" fill="#F2F2F2" stroke="#7A7A7A" stroke-width="2"/><text x="56" y="185" text-anchor="middle" font-size="10.5" >EVI:AP:626</text><rect x="128" y="168" width="100" height="24" rx="7" fill="#E8F5F2" stroke="#23907F" stroke-width="2"/><text x="178" y="185" text-anchor="middle" font-size="11" font-weight="bold">APR:626</text><rect x="262" y="168" width="150" height="24" rx="7" fill="#F3ECFA" stroke="#8A55C2" stroke-width="2"/><text x="337" y="185" text-anchor="middle" font-size="10.5" >OPR:626:1 증가방류</text><rect x="8" y="200" width="96" height="24" rx="7" fill="#F2F2F2" stroke="#7A7A7A" stroke-width="2"/><text x="56" y="217" text-anchor="middle" font-size="10.5" >EVI:AP:1103</text><rect x="128" y="200" width="100" height="24" rx="7" fill="#E8F5F2" stroke="#23907F" stroke-width="2"/><text x="178" y="217" text-anchor="middle" font-size="11" font-weight="bold">APR:1103</text><rect x="262" y="200" width="150" height="24" rx="7" fill="#F3ECFA" stroke="#8A55C2" stroke-width="2"/><text x="337" y="217" text-anchor="middle" font-size="10.5" >OPR:1103:1 점진·점증방류</text><rect x="8" y="232" width="96" height="24" rx="7" fill="#F2F2F2" stroke="#7A7A7A" stroke-width="2"/><text x="56" y="249" text-anchor="middle" font-size="10.5" >EVI:AP:1114</text><rect x="128" y="232" width="100" height="24" rx="7" fill="#E8F5F2" stroke="#23907F" stroke-width="2"/><text x="178" y="249" text-anchor="middle" font-size="11" font-weight="bold">APR:1114</text><rect x="262" y="232" width="150" height="24" rx="7" fill="#F3ECFA" stroke="#8A55C2" stroke-width="2"/><text x="337" y="249" text-anchor="middle" font-size="10.5" >OPR:1114:1 증가방류</text><rect x="8" y="264" width="96" height="24" rx="7" fill="#F2F2F2" stroke="#7A7A7A" stroke-width="2"/><text x="56" y="281" text-anchor="middle" font-size="10.5" >EVI:AP:1368</text><rect x="128" y="264" width="100" height="24" rx="7" fill="#E8F5F2" stroke="#23907F" stroke-width="2"/><text x="178" y="281" text-anchor="middle" font-size="11" font-weight="bold">APR:1368</text><rect x="262" y="264" width="150" height="24" rx="7" fill="#F3ECFA" stroke="#8A55C2" stroke-width="2"/><text x="337" y="281" text-anchor="middle" font-size="10.5" >OPR:1368:1 탄력적 방류</text><rect x="8" y="296" width="96" height="24" rx="7" fill="#F2F2F2" stroke="#7A7A7A" stroke-width="2"/><text x="56" y="313" text-anchor="middle" font-size="10.5" >EVI:AP:1445</text><rect x="128" y="296" width="100" height="24" rx="7" fill="#E8F5F2" stroke="#23907F" stroke-width="2"/><text x="178" y="313" text-anchor="middle" font-size="11" font-weight="bold">APR:1445</text><rect x="262" y="296" width="150" height="24" rx="7" fill="#F3ECFA" stroke="#8A55C2" stroke-width="2"/><text x="337" y="313" text-anchor="middle" font-size="10.5" >OPR:1445:1 탄력적 방류</text><rect x="8" y="343" width="96" height="24" rx="7" fill="#F2F2F2" stroke="#7A7A7A" stroke-width="2"/><text x="56" y="360" text-anchor="middle" font-size="10.5" >EVI:AP:2755</text><rect x="128" y="343" width="100" height="24" rx="7" fill="#E8F5F2" stroke="#23907F" stroke-width="2"/><text x="178" y="360" text-anchor="middle" font-size="11" font-weight="bold">APR:2755</text><rect x="262" y="328" width="150" height="24" rx="7" fill="#F3ECFA" stroke="#8A55C2" stroke-width="2"/><text x="337" y="345" text-anchor="middle" font-size="10.5" >OPR:2755:1 초기방류</text><rect x="262" y="358" width="150" height="24" rx="7" fill="#F3ECFA" stroke="#8A55C2" stroke-width="2"/><text x="337" y="375" text-anchor="middle" font-size="10.5" >OPR:2755:2 탄력적 방류</text><rect x="8" y="390" width="96" height="24" rx="7" fill="#F2F2F2" stroke="#7A7A7A" stroke-width="2"/><text x="56" y="407" text-anchor="middle" font-size="10.5" >EVI:AP:3178</text><rect x="128" y="390" width="100" height="24" rx="7" fill="#E8F5F2" stroke="#23907F" stroke-width="2"/><text x="178" y="407" text-anchor="middle" font-size="11" font-weight="bold">APR:3178</text><rect x="262" y="390" width="150" height="24" rx="7" fill="#F3ECFA" stroke="#8A55C2" stroke-width="2"/><text x="337" y="407" text-anchor="middle" font-size="10.5" >OPR:3178:1 탄력적 방류</text><rect x="8" y="422" width="96" height="24" rx="7" fill="#F2F2F2" stroke="#7A7A7A" stroke-width="2"/><text x="56" y="439" text-anchor="middle" font-size="10.5" >EVI:AP:3412</text><rect x="128" y="422" width="100" height="24" rx="7" fill="#E8F5F2" stroke="#23907F" stroke-width="2"/><text x="178" y="439" text-anchor="middle" font-size="11" font-weight="bold">APR:3412</text><rect x="262" y="422" width="150" height="24" rx="7" fill="#F3ECFA" stroke="#8A55C2" stroke-width="2"/><text x="337" y="439" text-anchor="middle" font-size="10.5" >OPR:3412:1 방류</text><rect x="8" y="454" width="96" height="24" rx="7" fill="#F2F2F2" stroke="#7A7A7A" stroke-width="2"/><text x="56" y="471" text-anchor="middle" font-size="10.5" >EVI:AP:3519</text><rect x="128" y="454" width="100" height="24" rx="7" fill="#E8F5F2" stroke="#23907F" stroke-width="2"/><text x="178" y="471" text-anchor="middle" font-size="11" font-weight="bold">APR:3519</text><text x="262" y="470" font-size="10.5" fill="#999">변경 승인 (운영행위 없음)</text><rect x="8" y="486" width="96" height="24" rx="7" fill="#F2F2F2" stroke="#7A7A7A" stroke-width="2"/><text x="56" y="503" text-anchor="middle" font-size="10.5" >EVI:AP:3647</text><rect x="128" y="486" width="100" height="24" rx="7" fill="#E8F5F2" stroke="#23907F" stroke-width="2"/><text x="178" y="503" text-anchor="middle" font-size="11" font-weight="bold">APR:3647</text><text x="262" y="502" font-size="10.5" fill="#999">변경 승인 (운영행위 없음)</text><rect x="8" y="518" width="96" height="24" rx="7" fill="#F2F2F2" stroke="#7A7A7A" stroke-width="2"/><text x="56" y="535" text-anchor="middle" font-size="10.5" >EVI:AP:3771</text><rect x="128" y="518" width="100" height="24" rx="7" fill="#E8F5F2" stroke="#23907F" stroke-width="2"/><text x="178" y="535" text-anchor="middle" font-size="11" font-weight="bold">APR:3771</text><rect x="262" y="518" width="150" height="24" rx="7" fill="#F3ECFA" stroke="#8A55C2" stroke-width="2"/><text x="337" y="535" text-anchor="middle" font-size="10.5" >OPR:3771:1 방류</text><rect x="485" y="376" width="150" height="48" rx="7" fill="#FFF4EA" stroke="#E07A2F" stroke-width="2"/><text x="560" y="398" text-anchor="middle" font-size="13.5" font-weight="bold">DAM:1003110</text><text x="560" y="412" text-anchor="middle" font-size="11" fill="#555">충주댐 · 다목적댐</text><rect x="690" y="58" width="112" height="24" rx="7" fill="#EEF2FB" stroke="#2F66D0" stroke-width="2"/><text x="746" y="75" text-anchor="middle" font-size="10.5" >HMS:…:수위</text><rect x="690" y="94" width="112" height="24" rx="7" fill="#EEF2FB" stroke="#2F66D0" stroke-width="2"/><text x="746" y="111" text-anchor="middle" font-size="10.5" >HMS:…:저수량</text><rect x="690" y="130" width="112" height="24" rx="7" fill="#EEF2FB" stroke="#2F66D0" stroke-width="2"/><text x="746" y="147" text-anchor="middle" font-size="10.5" >HMS:…:강우량</text><rect x="690" y="166" width="112" height="24" rx="7" fill="#EEF2FB" stroke="#2F66D0" stroke-width="2"/><text x="746" y="183" text-anchor="middle" font-size="10.5" >HMS:…:유입량</text><rect x="690" y="202" width="112" height="24" rx="7" fill="#EEF2FB" stroke="#2F66D0" stroke-width="2"/><text x="746" y="219" text-anchor="middle" font-size="10.5" >HMS:…:총방류량</text><rect x="690" y="238" width="112" height="24" rx="7" fill="#EEF2FB" stroke="#2F66D0" stroke-width="2"/><text x="746" y="255" text-anchor="middle" font-size="10.5" >HMS:…:저수율</text><rect x="690" y="318" width="104" height="26" rx="7" fill="#F2F2F2" stroke="#7A7A7A" stroke-width="2"/><text x="742" y="336" text-anchor="middle" font-size="10.5" >EVI:KW:1003110</text><rect x="660" y="560" width="140" height="40" rx="7" fill="#FDF3E3" stroke="#C77A1E" stroke-width="2"/><text x="730" y="578" text-anchor="middle" font-size="12" font-weight="bold">CRI:CR-02</text><text x="730" y="592" text-anchor="middle" font-size="11" fill="#555">제한수위 138.0 EL.m</text><rect x="660" y="640" width="140" height="26" rx="7" fill="#F2F2F2" stroke="#7A7A7A" stroke-width="2"/><text x="730" y="658" text-anchor="middle" font-size="10.5" >EVI:LAW:별표3</text><g font-size="11.5"><rect x="380" y="610" width="270" height="140" rx="6" fill="#fff" stroke="#ddd"/><line x1="392" y1="630" x2="422" y2="630" stroke="#23907F" stroke-width="1.6"/><text x="428" y="634">concernsDam (승인 → 댐)</text><line x1="392" y1="650" x2="422" y2="650" stroke="#8A55C2" stroke-width="1.6"/><text x="428" y="654">performedOnDam (운영행위 → 댐)</text><line x1="392" y1="670" x2="422" y2="670" stroke="#444" stroke-width="1.6"/><text x="428" y="674">authorizes (승인 → 운영행위)</text><line x1="392" y1="690" x2="422" y2="690" stroke="#999" stroke-width="1.6"/><text x="428" y="694">supportedBy (→ 근거)</text><line x1="392" y1="710" x2="422" y2="710" stroke="#2F66D0" stroke-width="1.6"/><text x="428" y="714">hasHydrometeorologicalState</text><line x1="392" y1="730" x2="422" y2="730" stroke="#C77A1E" stroke-width="1.6"/><text x="428" y="734">appliesToDam (기준 → 댐)</text></g></svg>
<div class="note">충주댐에 이어진 Entity 53개(댐 1, 승인 15, 승인자료 근거 15, 운영행위 14, HMS 6, 측정자료 근거 1, 기준 1, 규정 근거 1)와 그 관계를 모두 그렸다. 4개 댐 전체로는 Entity 264개, 관계 418개이다.</div>
</div>''')

# ================================================================== 3장 저장
add('''<!-- s1: CSV 줄 → Cypher 문 -->
<div class="fig" id="s1">
 <div class="hd">① Entity 하나 → 노드 하나 (entities·properties의 APR:504 줄을 모아서)</div>
 <div class="code"><span class="note">kgv4_entities.csv    </span>APR:504, Approval
<span class="note">kgv4_properties.csv  </span>APR:504, approvalTime, 2011-06-27, <b>date</b>
<span class="note">                     </span>APR:504, approvalContent, 방류시작 2011-06-27 18:00; 접수방류량 2000㎥/s; …, string</div>
 <div class="arrow">↓ Python 스크립트가 줄을 읽어 Cypher 문을 쓴다</div>
 <div class="code"><span class="hl1">MERGE (n:Entity:Approval {id: 'APR:504'})</span> SET n.label = '승인 504 (충주댐)',
  <span class="hl2">n.approvalTime = date('2011-06-27')</span>, n.approvalContent = '방류시작 2011-06-27 18:00; …';</div>
 <div class="note" style="margin:4px 0 12px"><span class="hl1">&nbsp;노드 만들기&nbsp;</span> 라벨 = Entity + Class, 같은 id가 있으면 새로 만들지 않음(MERGE) · <span class="hl2">&nbsp;자료형 변환&nbsp;</span> 날짜는 date(), 일시는 datetime(), 숫자는 숫자로</div>
 <div class="hd">② 관계 한 줄 → 관계 하나 (relations의 줄)</div>
 <div class="code"><span class="note">kgv4_relations.csv   </span>APR:504, concernsDam, DAM:1003110, MR-APR-DAM, real</div>
 <div class="arrow">↓</div>
 <div class="code"><span class="hl3">MATCH (a:Entity {id: 'APR:504'}), (b:Entity {id: 'DAM:1003110'})</span>
<span class="hl4">MERGE (a)-[r:concernsDam]->(b)</span> SET r.rule = 'MR-APR-DAM', r.origin = 'real', …;</div>
 <div class="note" style="margin-top:4px"><span class="hl3">&nbsp;두 노드 찾기&nbsp;</span> 시작·끝 ID로 · <span class="hl4">&nbsp;관계 만들기&nbsp;</span> 관계 이름 그대로, 규칙과 값의 성격을 관계의 속성으로 남김</div>
</div>''')

add('''<!-- s2: KG와 외부 저장소 -->
<div class="fig" id="s2">
 <div style="display:grid;grid-template-columns:1fr 60px 1fr;align-items:center;gap:14px 0">
  <div class="step" style="background:#FFF8E6;border-color:#D9B44A"><b>Neo4j (KG)</b><br><span class="nd hms" style="margin:4px 0">HMS:1003110:수위</span><br>stationCode = <b style="color:var(--key)">1003110</b>, variableType = 수위<br><span class="note">값은 넣지 않음</span></div>
  <div class="arrow">→<div class="note" style="font-size:12px">댐 코드 + 시각</div></div>
  <div class="step"><b>측정 저장소</b> <span class="note">(시간자료 508,246행)</span><br><span class="mono" style="font-size:13px">(1003110, 2020-08-02 18:00)</span><br>수위 139.55 EL.m, 유입량 4945.201 CMS, …</div>
  <div class="step" style="background:#FFF8E6;border-color:#D9B44A"><b>Neo4j (KG)</b><br><span class="nd evi" style="margin:4px 0">EVI:LAW:별표3</span><br>sourceLocator = <b style="color:var(--key)">별표 3</b></div>
  <div class="arrow">→<div class="note" style="font-size:12px">조회 키</div></div>
  <div class="step"><b>문서 저장소</b> <span class="note">(kgv4_documents.csv)</span><br>"별표 3" → 연계운영규정 별표3 원문<br><span class="mono" style="font-size:12.5px">│충 주 댐│138.0│…</span></div>
 </div>
 <div class="note" style="margin-top:10px">KG에는 의미·관계·근거 위치와 외부 저장소를 찾아가는 키만 둔다. 시간별 측정값과 규정 원문은 KG 밖에 두고, 질의할 때 키로 읽는다.</div>
</div>''')

# ================================================================== 4장 검색·답변
add('''<!-- q0: 전체 경로 한 장 -->
<div class="fig" id="q0">
 <div class="step" style="background:#FFF8E6;border-color:#D9B44A"><b>질문</b> "2020년 8월 충주댐 방류 승인과 운영행위, 그때의 수문 상태를 알려줘."</div>
 <div class="arrow">↓</div>
 <div class="step"><span class="tagL llm">LLM</span> <b>① 의도·값 추출</b> → <span class="mono" style="font-size:13px">{"intent": ["CQ2","CQ3","CQ4"], "dam": "충주댐", "period": {"start": "2020-08-01", "end": "2020-08-31"}}</span></div>
 <div class="arrow">↓</div>
 <div class="step"><span class="tagL cd">코드</span> <b>② 입력 확인</b> → 의도가 CQ1~CQ6 안인지, 댐이 4개 댐 안인지 확인, 기간을 [2020-08-01 00:00, 2020-09-01 00:00)로</div>
 <div class="arrow">↓</div>
 <div class="step"><span class="tagL cd">코드</span> <b>③ KG 조회 (Cypher 템플릿)</b> → 운영행위 OPR:3412:1(← 승인 APR:3412), 승인 APR:3412·APR:3519·APR:3647, 측정 키 1003110</div>
 <div class="arrow">↓</div>
 <div class="step"><span class="tagL cd">코드</span> <b>④ 외부 저장소 조회</b> → 운영 시각 2020-08-02 18:00의 측정값: 수위 139.55 EL.m, 유입량 4945.201 CMS, …</div>
 <div class="arrow">↓</div>
 <div class="step"><span class="tagL cd">코드</span> <b>⑤ 근거 묶음</b> → 의도별 구역, 항목마다 출처 번호([OPR:3412:1], [APR:3412], [MEA:1003110:2020080218] …)</div>
 <div class="arrow">↓</div>
 <div class="step"><span class="tagL llm">LLM</span> <b>⑥ 답변</b> → "근거"(출처 번호를 붙인 사실)와 "판단"(어느 근거에서 나왔는지 표시)으로 나누어 답함</div>
 <div class="note" style="margin-top:6px">LLM은 ①과 ⑥ 두 곳에서만 쓰고(같은 모델, 프롬프트만 다름), KG와 저장소에서 근거를 찾는 ②~⑤는 코드가 정해진 순서대로 한다. 서버 실행 기록: Qwen3-32B, 38.8초.</div>
</div>''')

add('''<!-- q1: 의도·값 추출 -->
<div class="fig" id="q1">
 <div class="code" style="font-size:14.5px">"<span class="hl1">2020년 8월</span> <span class="hl3">충주댐</span> <span class="hl2">방류 승인</span>과 <span class="hl4">운영행위</span>, <span class="hl1">그때의</span> <span class="hl4" style="background:#DDEEFF">수문 상태</span>를 알려줘."</div>
 <div class="arrow">↓ 의도 목록(CQ1~CQ6)과 허용 댐 4개를 적은 지시문과 함께 LLM에 준다</div>
 <table class="t" style="font-size:14px;width:100%">
  <tr><th>질문 속 표현</th><th>뽑은 값</th><th>의미</th></tr>
  <tr><td><span class="hl2">방류 승인</span></td><td>CQ4</td><td>과거 방류 승인</td></tr>
  <tr><td><span class="hl4">운영행위</span></td><td>CQ3</td><td>과거 운영행위</td></tr>
  <tr><td><span class="hl1">그때의</span> <span style="background:#DDEEFF">수문 상태</span></td><td>CQ2</td><td>과거 시점의 수문·기상 상태</td></tr>
  <tr><td><span class="hl3">충주댐</span></td><td>dam = 충주댐</td><td>허용 댐 4개 중 하나 ("충주"라고 해도 충주댐으로)</td></tr>
  <tr><td><span class="hl1">2020년 8월</span></td><td>period = 2020-08-01 ~ 2020-08-31</td><td>시점이 없으면 "전체"</td></tr>
 </table>
 <div class="note" style="margin-top:6px">출력은 JSON 하나뿐이다. 목록 밖의 댐(예: 팔당댐), 이유를 묻는 질문("왜 방류했나")은 의도를 비우고 이유를 적는다 → 이후 단계에서 "질의 불가"로 답한다.</div>
</div>''')

add('''<!-- q2: KG 조회 -->
<div class="fig" id="q2">
 <div class="hd">CQ3 운영행위 템플릿 (값 $dam = '충주댐', $s = 2020-08-01, $e = 2020-09-01)</div>
 <div class="code">MATCH (o:Operation)-[:<b>performedOnDam</b>]->(d:Dam {damName:$dam})
WHERE o.operationTime >= datetime($s) AND o.operationTime &lt; datetime($e)
OPTIONAL MATCH (a:Approval)-[:<b>authorizes</b>]->(o)
RETURN o.id, o.operationType, o.operationTime, a.id</div>
 <svg width="808" height="120" viewBox="0 0 808 120" font-family="WenQuanYi Zen Hei" font-size="14">
  <defs><marker id="m7" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#444"/></marker></defs>
  <rect x="10" y="40" width="160" height="40" rx="8" fill="#E8F5F2" stroke="#23907F" stroke-width="2.5"/><text x="90" y="65" text-anchor="middle" font-weight="bold">APR:3412</text>
  <rect x="300" y="40" width="190" height="40" rx="8" fill="#F3ECFA" stroke="#8A55C2" stroke-width="2.5"/><text x="395" y="58" text-anchor="middle" font-weight="bold">OPR:3412:1</text><text x="395" y="74" text-anchor="middle" font-size="12">방류, 2020-08-02 18:00</text>
  <rect x="620" y="40" width="170" height="40" rx="8" fill="#FFF4EA" stroke="#E07A2F" stroke-width="2.5"/><text x="705" y="65" text-anchor="middle" font-weight="bold">충주댐</text>
  <line x1="170" y1="60" x2="296" y2="60" stroke="#444" stroke-width="2" marker-end="url(#m7)"/><text x="233" y="50" text-anchor="middle" font-size="12.5" fill="#2F4F9A">authorizes</text>
  <line x1="490" y1="60" x2="616" y2="60" stroke="#444" stroke-width="2" marker-end="url(#m7)"/><text x="553" y="50" text-anchor="middle" font-size="12.5" fill="#2F4F9A">performedOnDam</text>
  <text x="400" y="110" text-anchor="middle" font-size="13" fill="#555">충주댐에서 출발해 관계를 거꾸로 따라가, 기간 안의 운영행위와 그것을 허가한 승인을 찾는다</text>
 </svg>
 <table class="t" style="font-size:14px;width:100%">
  <tr><th>의도</th><th>따라가는 관계 (Cypher 템플릿)</th><th>외부 저장소</th><th>이 질문의 결과</th></tr>
  <tr><td>CQ1 현재 상태</td><td>Dam → hasHydrometeorologicalState → HMS (stationCode 얻기)</td><td>측정: 가장 최근 시각</td><td>—</td></tr>
  <tr><td>CQ2 과거 상태</td><td>(운영행위가 있으면) 운영 시각</td><td>측정: 그 시각</td><td>2020-08-02 18:00 1행</td></tr>
  <tr class="hl"><td>CQ3 운영행위</td><td>Operation → performedOnDam → Dam, Approval → authorizes → Operation</td><td>—</td><td>OPR:3412:1 ← APR:3412</td></tr>
  <tr class="hl"><td>CQ4 승인</td><td>Approval → concernsDam → Dam (승인일이 기간 안)</td><td>—</td><td>APR:3412, 3519, 3647</td></tr>
  <tr><td>CQ5 운영기준</td><td>Criterion → appliesToDam → Dam</td><td>문서: sourceLocator</td><td>—</td></tr>
  <tr><td>CQ6 근거</td><td>조회한 항목마다 → supportedBy → EvidenceSource</td><td>—</td><td>—</td></tr>
 </table>
</div>''')

add('''<!-- q3: 측정 저장소 조회 -->
<div class="fig" id="q3">
 <div style="display:grid;grid-template-columns:260px 40px 1fr;align-items:center;gap:0">
  <div class="step"><span class="nd opr">OPR:3412:1</span><br>operationTime = 2020-08-02 18:00<br><span class="nd hms" style="margin-top:4px">HMS:1003110:…</span><br>stationCode = <b style="color:var(--key)">1003110</b></div>
  <div class="arrow">→</div>
  <div>
   <div class="hd">측정 저장소에서 (1003110, 2020-08-02 18:00) 한 행</div>
   <table class="t" style="font-size:14px;margin-top:4px">
    <tr><th>수위</th><th>저수량</th><th>강우량</th><th>유입량</th><th>총방류량</th><th>저수율</th></tr>
    <tr><td>139.55 EL.m</td><td>2126.472 MCM</td><td>1.901 mm</td><td>4945.201 CMS</td><td>707.145 CMS</td><td>77.3 %</td></tr>
   </table>
   <div class="note" style="margin-top:4px">출처 번호 <b>[MEA:1003110:2020080218]</b> (측정 · 댐 코드 · 시각 라벨)</div>
  </div>
 </div>
 <div class="note" style="margin-top:8px">정각이 아닌 운영 시각(예: 06:30)은 앞뒤 정시 두 행을 함께 준다. 값은 저장소의 원값 그대로이며 계산한 값은 넣지 않는다.</div>
</div>''')

add('''<!-- q4: 근거 묶음 -->
<div class="fig" id="q4">
 <div class="code" style="font-size:13px">[질문] 2020년 8월 충주댐 방류 승인과 운영행위, 그때의 수문 상태를 알려줘.
[대상] 충주댐, 기간 2020-08-01 ~ 2020-08-31

<span class="hl4">[근거 1. 운영행위와 허가한 승인]  (CQ3)</span> 운영행위의 시각은 비고에 적힌 시각, 없으면 승인된 방류 시작 시각이다.
<span class="hl1">[OPR:3412:1]</span> 방류, 시각 2020-08-02 18:00 ← 승인 <span class="hl1">[APR:3412]</span>

<span class="hl4">[근거 2. 운영 시각의 상태]  (CQ2)</span>
<span class="hl1">[MEA:1003110:2020080218]</span> 2020-08-02 18:00  수위 139.55 EL.m, 저수량 2126.472 MCM, 강우량 1.901 mm,
   유입량 4945.201 CMS, 총방류량 707.145 CMS, 저수율 77.3 %

<span class="hl4">[근거 3. 방류 승인]  (CQ4)</span>
<span class="hl1">[APR:3412]</span> 승인일 2020-08-02: 방류시작 2020-08-02 18:00; 접수방류량 3000㎥/s
<span class="hl1">[APR:3519]</span> 승인일 2020-08-06: 방류시작 2020-08-02 18:00; 접수방류량 7000㎥/s; 비고: 방류기간 (당초) … (변경) …
<span class="hl1">[APR:3647]</span> 승인일 2020-08-12: 방류시작 2020-08-06 06:00; 접수방류량 7000㎥/s; 비고: 수문방류 변경승인(방류기간연장) …

<span class="hl2">[근거 사용 원칙]</span> 근거에 있는 내용만 사실로 쓰고 출처 번호를 붙인다 / 비교·해석은 판단임을 밝힌다 / 없으면 "자료에 없음"</div>
 <div class="note" style="margin-top:4px"><span class="hl4">&nbsp;의도별 구역&nbsp;</span> <span class="hl1">&nbsp;출처 번호 = KG의 Entity ID, 측정값은 MEA&nbsp;</span> <span class="hl2">&nbsp;원칙 3문장&nbsp;</span></div>
</div>''')

add('''<!-- q5: 답변 -->
<div class="fig" id="q5">
 <div class="code" style="font-size:13px;background:#fff"><b>근거</b>
- 2020년 8월 2일 18:00에 방류가 승인되었으며, 방류량은 3000㎥/s로 접수되었습니다. <span class="hl1">[APR:3412]</span>
- 이후 8월 6일에 방류 승인이 변경되어 방류량이 7000㎥/s로 증가하고, 방류 기간이 8월 2일 18:00부터 8월 16일 24:00까지로
  확정되었습니다. <span class="hl1">[APR:3519]</span>
- 8월 12일에는 방류 기간이 다시 연장되어 8월 6일 06:00부터 8월 22일 00:00까지로 확정되었습니다. <span class="hl1">[APR:3647]</span>
- 방류가 시작된 2020년 8월 2일 18:00 기준, 수위는 139.55 EL.m, … 저수율은 77.3%입니다. <span class="hl1">[MEA:1003110:2020080218]</span>

<b>판단</b>
- 방류량은 처음 3000㎥/s에서 이후 7000㎥/s로 증가했습니다. 방류 기간은 여러 차례 변경되며 최종적으로 8월 22일 00:00까지
  연장되었습니다. <span class="hl2">(근거: [APR:3412], [APR:3519], [APR:3647])</span>
- … <span class="warn" style="font-weight:normal">이는 댐의 수문 상황과 유입량 변화에 따라 조정된 것으로 판단됩니다.</span> (근거: [APR:3412], …)</div>
 <div class="note" style="margin-top:4px"><span class="hl1">&nbsp;사실마다 출처 번호&nbsp;</span> <span class="hl2">&nbsp;판단마다 쓴 근거&nbsp;</span> <span class="warn">빨간 글씨</span>: 자료에 없는 사유를 추정한 문장 → 검토할 점 3</div>
</div>''')

html = HEAD.replace('</style></head><body>', '</style>' + CSS + '</head><body>') + '\n\n'.join(F) + '\n</body></html>'
open(os.path.join(OUT, 'kg2_figs.html'), 'w', encoding='utf-8').write(html)
print('figs', len(F))
