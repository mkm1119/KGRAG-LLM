#!/usr/bin/env python3
"""Data review pack (display only): sample CSVs, chart, raw-vs-normalized comparison. No new interpretation, no renames of raw fields."""
import csv, gzip, json, glob, os, io, re, datetime as dt, subprocess, html
OUT="04_reports/data_review"
def rd(p): return list(csv.DictReader(open(p,encoding="utf-8-sig",newline="")))
def wr(name,rows,cols):
    with open(f"{OUT}/{name}","w",newline="",encoding="utf-8-sig") as f:
        w=csv.writer(f); w.writerow(cols); [w.writerow([r.get(c,"") for c in cols]) for r in rows]
def md(rows,cols,heads=None):
    heads=heads or cols
    def cell(v): return str(v).replace("|","\\|").replace("\n"," ")
    return "\n".join(["| "+" | ".join(heads)+" |","|"+"---|"*len(cols)]+["| "+" | ".join(cell(r.get(c,"")) for c in cols)+" |" for r in rows])
S={}  # markdown fragments
# ---- 1. inventory
def nrows_gz(p): return sum(1 for _ in gzip.open(p,"rt",encoding="utf-8"))-1
def nrows(p): return len(rd(p))
inv=[
 ("Dam","K-water MyWater getBasic/damList; KHNP 페이지(이름만); 별표1","03_normalized/dam_catalog.csv",nrows("03_normalized/dam_catalog.csv"),"dam_id_source, dam_name_source, operator_evidence, organization, river_label_in_source, 별표1 한강수계 여부","제원은 스냅샷(현재)","Dam"),
 ("Dam(제원 상세)","MyWater getBasic","03_normalized/dam_catalog_kwater_basic.csv",nrows("03_normalized/dam_catalog_kwater_basic.csv"),"높이·길이·유역면적·계획홍수위·상시만수위·홍수기제한수위·총저수용량 등 [DATAn]","스냅샷","Dam (속성)"),
 ("ObservationStation","MyWater getRain(우량A/수위C)","03_normalized/observation_station_list.csv",nrows("03_normalized/observation_station_list.csv"),"station_id_OBS_CD, station_name_source, station_type, associated_DAM_CD","지점 목록(시점 스냅샷)","ObservationStation"),
 ("MeasurementDataset(목록)","MyWater getPeriod/getHydr/getRain","03_normalized/measurement_dataset_list.csv",nrows("03_normalized/measurement_dataset_list.csv"),"dataset_id(임시), resolution, variable(s), facility, start/end, n_raw_files","2019-08-01~2026-09-28 중 요청 구간","MeasurementDataset"),
 ("Measurement(시간 long)","MyWater getPeriod","03_normalized/kwater_mywater_period_hourly_long.csv.gz",nrows_gz("03_normalized/kwater_mywater_period_hourly_long.csv.gz"),"DAM_CD, SDATE_raw, source_variable_name, value_raw, key_present_in_raw","2021-01-01~2026-09-28","MeasurementDataset 내용"),
 ("Measurement(일 long)","MyWater getPeriod","03_normalized/kwater_mywater_period_daily_long.csv.gz",nrows_gz("03_normalized/kwater_mywater_period_daily_long.csv.gz"),"동일","2021-01-01~2026-09-28","〃"),
 ("Measurement(10분 long, 홍수기)","MyWater getPeriod","03_normalized/kwater_mywater_period_10min_long.csv.gz",nrows_gz("03_normalized/kwater_mywater_period_10min_long.csv.gz"),"동일","2021~2025 각 6/21~9/30","〃"),
 ("Measurement(댐별 hydr 시간)","MyWater getHydr","03_normalized/kwater_mywater_hydr_H_wide.csv.gz",nrows_gz("03_normalized/kwater_mywater_hydr_H_wide.csv.gz"),"DAM_CD, SDATE_raw, DATA1~DATA7(수위·저수량·강우량·유입량·?·총방류량·저수율)","2021-01-01~2026-09-28 (11개 시설)","〃"),
 ("Criterion","법제처 DRF (연계운영규정 별표3·조문)","03_normalized/criterion_list.csv",nrows("03_normalized/criterion_list.csv"),"criterion_id(임시), locator, verbatim_text_or_value, unit, applies_to_facility, defined_in_document","시행 2026-07-08 기준 현행","Criterion"),
 ("Document","법제처 DRF/첨부, K-water·KHNP·포털 스냅샷","03_normalized/document_list.csv",nrows("03_normalized/document_list.csv"),"document_id(임시), title, organization, type, source_url, raw_file, sha256","2026-09-29 수집","Document"),
 ("Approval","한강홍수통제소(공공데이터포털 15085926 CSV)","03_normalized/approval_records_hrfco_raw_fields.csv",nrows("03_normalized/approval_records_hrfco_raw_fields.csv"),"순차번호, 관측소코드, 관측소명, 승인년월일시분, 방류시작시간, 접수방류량, 접수일자, 비고","승인 2010-07-16~2021-07-16","Approval"),
 ("상·하류 관계 evidence","K-water 한강유역본부 시설 소개 텍스트","03_normalized/dam_network_evidence.csv",nrows("03_normalized/dam_network_evidence.csv"),"upstream_dam, downstream_dam, relation_type, verbatim_quote, verification_status","현재 서술","(현재 Ontology에 대응 Relation 없음)"),
 ("수계 소속(membership)","연계운영규정 별표1","03_normalized/han_system_membership_byeolpyo1.csv",nrows("03_normalized/han_system_membership_byeolpyo1.csv"),"basin_label, facility_category, facilities_verbatim","현행","Dam 속성(수계 소속)"),
 ("Approval–Measurement 연결 사례","위 자료의 조합","03_normalized/linkage_pilot_cases.csv",nrows("03_normalized/linkage_pilot_cases.csv"),"case_id, 승인 원문 필드, linked_criterion_id, n_hourly_measurement_rows","2019-08~10, 2020-07-25~09-10","(연결 가능성 확인용)"),
]
S["inventory"]=md([dict(zip(["k","src","file","n","cols","per","onto"],r)) for r in inv],["k","src","file","n","cols","per","onto"],["데이터","출처","파일","레코드 수","주요 컬럼","기간","관련 Ontology 개념"])
# ---- 2. samples
dam=rd("03_normalized/dam_catalog.csv")
kb={r["dam_id_source"]:r for r in rd("03_normalized/dam_catalog_kwater_basic.csv")}
rows=[]
for r in dam[:11]:
    k=kb.get(r["dam_id_source"],{})
    rows.append({"dam_id_source":r["dam_id_source"],"dam_name_source":r["dam_name_source"],"organization":r["organization"],"river_label(source)":r["river_label_in_source(하천 그룹 표기; 검증된 수계 아님)"],"총저수용량(MCM)[DATA13]":k.get("총저수용량(MCM)[DATA13]",""),"유역면적(km2)[DATA5]":k.get("유역면적(km2)[DATA5]",""),"홍수기제한수위(EL.m)[DATA10]":k.get("홍수기제한수위(EL.m)[DATA10]",""),"계획홍수위(EL.m)[DATA8]":k.get("계획홍수위(EL.m)[DATA8]","")})
dam_cols=list(rows[0].keys()); wr("sample_dam.csv",rows,dam_cols); S["dam"]=md(rows[:8],dam_cols)
st=rd("03_normalized/observation_station_list.csv")
sel=[r for r in st if r["associated_DAM_CD_in_query"] in ("1003110",)][:5]+[r for r in st if r["associated_DAM_CD_in_query"]=="1012110"][:4]
st_cols=["station_id_OBS_CD","station_name_source","station_type_per_source_page","associated_DAM_CD_in_query","associated_dam_name_source"]
wr("sample_station.csv",sel,st_cols); S["station"]=md(sel,st_cols)
# approvals 10 (충주 4 + 횡성 3 + 소양강 3 from case file) verbatim
cases=rd("03_normalized/linkage_pilot_cases.csv")
ap_sel=[c for c in cases if c["관측소명"]=="충주"]+[c for c in cases if c["관측소명"]=="횡성"][:3]+[c for c in cases if c["관측소명"]=="소양강"]
ap_cols=["case_id","관측소명","승인년월일시분","방류시작시간","접수방류량","접수일자","비고(verbatim)"]
wr("sample_approval_10.csv",ap_sel,ap_cols); S["approval"]=md(ap_sel,ap_cols,["case_id(연구용)","관측소명","승인년월일시분","방류시작시간","접수방류량","접수일자","비고"])
# criteria 5
cr=rd("03_normalized/criterion_list.csv"); cr5=[c for c in cr if c["locator_in_document"].startswith("[별표3]") and any(n in c["applies_to_facility_per_source"] for n in ("소양강","충주","횡성","화천","팔당"))]
cr_cols=["criterion_id(연구용 임시ID)","applies_to_facility_per_source","verbatim_text_or_value","unit","defined_in_document","source_url"]
wr("sample_criterion_5.csv",cr5,cr_cols); S["criterion"]=md(cr5,["criterion_id(연구용 임시ID)","applies_to_facility_per_source","verbatim_text_or_value","unit"])
docs=rd("03_normalized/document_list.csv")
dsel=[d for d in docs if "연계운영규정" in d["title_or_filename"] or "연계운영규정" in d["note"]]
d_cols=["document_id(연구용 임시ID)","title_or_filename","type","raw_file","sha256"]
wr("sample_document_for_criterion.csv",dsel,d_cols); S["document"]=md([{**d,"sha256":d["sha256"][:12]+"…"} for d in dsel],d_cols)
# ---- measurement sample + case series
def lab2dt(L): 
    d=dt.datetime.strptime(L[:8],"%Y%m%d"); return d+dt.timedelta(hours=int(L[8:]))
hy={}
for fn in glob.glob("01_raw/KWater/mywater_approval_linked/hydr/H/*/*.json"):
    for r in json.load(open(fn,encoding="utf-8"))["list"]: hy[(r["DAM_CD"],r["SDATE"])]=r
def series(code,a,b):
    out=[(lab2dt(k[1]),k[1],r) for k,r in hy.items() if k[0]==code and a<=lab2dt(k[1])<=b]; return sorted(out)
t0=dt.datetime(2020,7,30); t1=dt.datetime(2020,8,12)
mcols=["timestamp_label(SDATE)","dam","DATA1_수위(EL.m)","DATA4_유입량(CMS)","DATA6_총방류량(CMS)","DATA3_강우량(mm)"]
def mrow(nm,L,r): return {"timestamp_label(SDATE)":L,"dam":nm,"DATA1_수위(EL.m)":r["DATA1"],"DATA4_유입량(CMS)":r["DATA4"],"DATA6_총방류량(CMS)":r["DATA6"],"DATA3_강우량(mm)":r["DATA3"]}
ms=[mrow("충주댐(1003110)",L,r) for _,L,r in series("1003110",dt.datetime(2020,8,2,14),dt.datetime(2020,8,2,22))]+[mrow("충주조정지(1003611)",L,r) for _,L,r in series("1003611",dt.datetime(2020,8,2,14),dt.datetime(2020,8,2,22))]
wr("sample_measurement_hourly_충주댐_충주조정지.csv",ms,mcols); S["meas"]=md(ms[:12],mcols)
# ---- case: AP-3412
ext=[r for r in rd("03_normalized/linkage_pilot_measurement_extract.csv") if r["case_id"]=="AP-3412"]
ecols=["offset_hours_from_방류시작시간(naive label; convention unresolved)","SDATE_raw","DATA1_수위(EL.m)","DATA4_유입량(CMS)","DATA6_총방류량(CMS)","DATA3_강우량(mm)"]
wr("case_AP-3412_measurement_minus6h_plus12h.csv",ext,ecols); S["case_meas"]=md(ext,ecols)
# ---- raw vs normalized
F="01_raw/FloodControl/환경부_한강홍수통제소_홍수예보_댐방류승인_20220727.csv"
raw_lines=open(F,"rb").read().decode("cp949").splitlines(); raw_line=[l for l in raw_lines if l.startswith("3412,")][0]
norm=[r for r in rd("03_normalized/approval_records_hrfco_raw_fields.csv") if r["순차번호"]=="3412"][0]
S["raw_ap"]=raw_lines[0]+"\n"+raw_line; S["norm_ap"]=json.dumps(norm,ensure_ascii=False,indent=1)
fn=sorted(glob.glob("01_raw/KWater/mywater_station/hydr/H/1003110/2021-01-01_2021-01-30.json"))[0]
jr=json.load(open(fn,encoding="utf-8")); rr=jr["list"][0]
S["raw_hydr_file"]=fn; S["raw_hydr"]=json.dumps(rr,ensure_ascii=False)
nm=None
for r in csv.DictReader(gzip.open("03_normalized/kwater_mywater_hydr_H_wide.csv.gz","rt",encoding="utf-8")):
    if r["DAM_CD"]=="1003110" and r["SDATE_raw"]==rr["SDATE"] and r["source_file"]==fn: nm=r; break
S["norm_hydr"]=json.dumps(nm,ensure_ascii=False,indent=1)
pf="01_raw/KWater/mywater_period/H1/group1/DATA4/2021-01-01_2021-01-30.json"
pj=json.load(open(pf,encoding="utf-8")); pr=pj["periodList"][0]; dl={d["DAM_CD"]:d for d in pj["damList"]}
S["raw_period_file"]=pf; S["raw_period_row"]=json.dumps(pr,ensure_ascii=False); S["raw_period_dam"]=json.dumps(dl["1003110"],ensure_ascii=False)
col="COL%d"%dl["1003110"]["RNUM"]
npn=None
with gzip.open("03_normalized/kwater_mywater_period_hourly_long.csv.gz","rt",encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["source_file"]==pf and r["DAM_CD"]=="1003110" and r["SDATE_raw"]==pr["SDATE"]: npn=r; break
S["norm_period"]=json.dumps(npn,ensure_ascii=False,indent=1); S["period_col"]=col
# ---- chart (SVG -> HTML -> PNG)
ser=series("1003110",t0,t1)
panels=[("저수위 (DATA1, EL.m)","DATA1"),("유입량 (DATA4, CMS)","DATA4"),("총방류량 (DATA6, CMS)","DATA6"),("강우량 (DATA3, mm)","DATA3")]
W,H=1100,190; L,R,T,B=70,30,22,26; PW=W-L-R; PH=H-T-B
span=(t1-t0).total_seconds()
def X(t): return L+PW*((t-t0).total_seconds()/span)
marks=[(dt.datetime(2020,8,2,18),"08-02 18:00 방류시작시간 (AP-3412, AP-3519)"),(dt.datetime(2020,8,6,6),"08-06 06:00 방류시작시간 (AP-3647)")]
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H*4+70}" font-family="WenQuanYi Zen Hei, Noto Sans CJK KR, sans-serif">','<rect width="100%" height="100%" fill="#fcfcfb"/>',
 f'<text x="{L}" y="24" font-size="16" fill="#0b0b0b" font-weight="600">충주댐 시간자료 (MyWater getHydr 원본 field) 2020-07-30 ~ 2020-08-12 — 세로선: 승인 파일의 방류시작시간</text>',
 f'<text x="{L}" y="44" font-size="12" fill="#52514e">시각 축은 SDATE 라벨(YYYYMMDDHH, HH=01..24)을 date+HH시로 표시한 것이며 시각 규약은 미확정(±1시간 불확실). 세로선은 승인 기록의 시작시간일 뿐 조작·인과의 증거가 아님.</text>']
for i,(title,key) in enumerate(panels):
    y0=70+i*H
    vals=[float(r[key]) for _,_,r in ser if r.get(key) not in (None,"")]
    lo,hi=min(vals),max(vals)
    if key=="DATA1": lo=min(lo,137.0); hi=max(hi,139.0)
    else: lo=0 if lo>=0 else lo
    import math
    def nice(lo_,hi_,n=4):
        raw=(hi_-lo_)/n or 1; m=10**math.floor(math.log10(raw)); st=min((x*m for x in (1,2,2.5,5,10) if x*m>=raw),default=raw)
        a=math.floor(lo_/st)*st; b=math.ceil(hi_/st)*st; return a,b,st
    ymin,ymax,ystep=nice(lo,hi)
    def Y(v): return y0+T+PH*(1-(v-ymin)/(ymax-ymin))
    svg.append(f'<text x="{L}" y="{y0+14}" font-size="13" fill="#0b0b0b" font-weight="600">{title}</text>')
    v=ymin
    while v<=ymax+1e-9:
        yy=Y(v); lab=(f"{v:.1f}" if ystep<1 or key=="DATA1" else f"{v:.0f}")
        svg.append(f'<line x1="{L}" x2="{W-R}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="#e7e6e2" stroke-width="1"/><text x="{L-6}" y="{yy+4:.1f}" font-size="11" fill="#52514e" text-anchor="end">{lab}</text>')
        v+=ystep
    for dday in range(0,14):
        td=t0+dt.timedelta(days=dday); xx=X(td)
        svg.append(f'<line x1="{xx:.1f}" x2="{xx:.1f}" y1="{y0+T+PH}" y2="{y0+T+PH+4}" stroke="#52514e"/>')
        if i==3 and dday%1==0: svg.append(f'<text x="{xx:.1f}" y="{y0+T+PH+17}" font-size="10" fill="#52514e" text-anchor="middle">{td.strftime("%m-%d")}</text>')
    if key=="DATA1":
        yy=Y(138.0); svg.append(f'<line x1="{L}" x2="{W-R}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="#52514e" stroke-width="1.2" stroke-dasharray="6 4"/><text x="{W-R-4}" y="{yy-5:.1f}" font-size="11" fill="#52514e" text-anchor="end">별표3 홍수기 제한수위 138.0 (CR-02)</text>')
    if key=="DATA3":
        for tt,_,r in ser:
            v=float(r[key]) if r.get(key) not in (None,"") else 0
            if v>0: svg.append(f'<rect x="{X(tt)-1:.1f}" y="{Y(v):.1f}" width="2" height="{Y(0)-Y(v):.1f}" fill="#2a78d6"/>')
    else:
        pts=" ".join(f"{X(tt):.1f},{Y(float(r[key])):.1f}" for tt,_,r in ser if r.get(key) not in (None,""))
        svg.append(f'<polyline points="{pts}" fill="none" stroke="#2a78d6" stroke-width="2" stroke-linejoin="round"/>')
    for mt,ml in marks:
        xx=X(mt); svg.append(f'<line x1="{xx:.1f}" x2="{xx:.1f}" y1="{y0+T}" y2="{y0+T+PH}" stroke="#eb6834" stroke-width="1.5" stroke-dasharray="3 3"/>')
        if i==0: svg.append(f'<text x="{xx+4:.1f}" y="{y0+T+12}" font-size="11" fill="#52514e">{ml}</text>')
    svg.append(f'<line x1="{L}" x2="{L}" y1="{y0+T}" y2="{y0+T+PH}" stroke="#52514e"/><line x1="{L}" x2="{W-R}" y1="{y0+T+PH}" y2="{y0+T+PH}" stroke="#52514e"/>')
svg.append("</svg>")
open(f"{OUT}/case_chungju_2020-08_timeseries.svg","w",encoding="utf-8").write("\n".join(svg))
open(f"{OUT}/_chart.html","w",encoding="utf-8").write('<!doctype html><meta charset="utf-8"><body style="margin:0">'+"\n".join(svg))
json.dump(S,open(f"{OUT}/_fragments.json","w",encoding="utf-8"),ensure_ascii=False)
print("ok", len(ser),"series rows")
