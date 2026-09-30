#!/usr/bin/env python3
"""Approval + Measurement + Criterion + Document linkage pilot (descriptive only).
- Approval fields verbatim; 비고 verbatim; no Operation/Rationale/causal inference.
- Measurement extract keeps raw SDATE labels; alignment to 방류시작시간 is by NAIVE label (hour-label convention unresolved -> flagged).
- Criterion link only where the source (연계운영규정 별표3) names the facility."""
import csv, glob, json, datetime as dt, collections, os
ap=list(csv.DictReader(open("03_normalized/approval_records_hrfco_raw_fields.csv",encoding="utf-8-sig")))
WIN={"A":("2020-07-25","2020-09-10",{"1001210","1003110","1003611","1006110","1012110"}),"B":("2019-08-01","2019-10-15",{"1001210"})}
crit={r["applies_to_facility_per_source"]:r for r in csv.DictReader(open("03_normalized/criterion_list.csv",encoding="utf-8-sig")) if r["criterion_type"].startswith("홍수기 제한수위")}
NAME2MW={"1001210":"광동댐","1003110":"충주댐","1003611":"충주조정지","1006110":"횡성댐","1012110":"소양강댐"}
docs={r["title_or_filename"]:r["document_id(연구용 임시ID)"] for r in csv.DictReader(open("03_normalized/document_list.csv",encoding="utf-8-sig"))}
DOCID=[v for k,v in docs.items() if "연계운영규정_일부개정전문_20260708.pdf" in k]
DOCID=DOCID[0] if DOCID else ""
# hydr hourly (approval-linked + earlier station files)
hy={}
for fn in glob.glob("01_raw/KWater/mywater_approval_linked/hydr/H/*/*.json")+glob.glob("01_raw/KWater/mywater_station/hydr/H/*/*.json"):
    for r in json.load(open(fn,encoding="utf-8")).get("list") or []: hy[(r["DAM_CD"],r["SDATE"])]=(fn,r)
def lab(d): return d.strftime("%Y%m%d%H")
cases=[];ext=[]
for r in ap:
    st=r["방류시작시간"][:10]; code=r["관측소코드"]; win=None
    for k,(a,b,ds) in WIN.items():
        if a<=st<=b and code in ds: win=k
    if not win: continue
    cid=f"AP-{r['순차번호']}"
    cr=crit.get(NAME2MW[code],None)
    s=dt.datetime.strptime(r["방류시작시간"],"%Y-%m-%d %H:%M")
    n=0
    for off in range(-6,13):
        d=s+dt.timedelta(hours=off); L=lab(d)
        # raw label with hour 24 style: naive label uses HH 00..23 -> also try (date-1)+24
        cand=[L]
        if d.hour==0: cand.append((d-dt.timedelta(days=1)).strftime("%Y%m%d")+"24")
        for c in cand:
            if (code,c) in hy:
                fn,m=hy[(code,c)]; n+=1
                ext.append([cid,off,c,fn,m.get("DATA1"),m.get("DATA2"),m.get("DATA3"),m.get("DATA4"),m.get("DATA5"),m.get("DATA6"),m.get("DATA7")])
    cases.append([cid,win,r["row_number_in_file"],r["순차번호"],r["관측소코드"],r["관측소명"],r["승인년월일시분"],r["방류시작시간"],r["접수방류량"],r["접수일자"],r["비고"],
        NAME2MW[code]+"(MyWater DAM_CD 동일; 동일시설 확정 REVIEW_REQUIRED)", cr["criterion_id(연구용 임시ID)"] if cr else "", cr["verbatim_text_or_value"] if cr else "별표3에 해당 시설 없음(광동댐은 용수댐; 기준 미연결)", DOCID if cr else "", n])
H=["case_id","window","row_number_in_approval_file","순차번호","관측소코드","관측소명","승인년월일시분","방류시작시간","접수방류량","접수일자","비고(verbatim)","linked_dam_in_measurement_source","linked_criterion_id","linked_criterion_value_verbatim","linked_document_id(연계운영규정 PDF)","n_hourly_measurement_rows_extracted(-6h..+12h, naive label)"]
csv.writer(open("03_normalized/linkage_pilot_cases.csv","w",newline="",encoding="utf-8-sig")).writerows([H]+cases)
csv.writer(open("03_normalized/linkage_pilot_measurement_extract.csv","w",newline="",encoding="utf-8-sig")).writerows([["case_id","offset_hours_from_방류시작시간(naive label; convention unresolved)","SDATE_raw","source_file","DATA1_수위(EL.m)","DATA2_저수량(MCM)","DATA3_강우량(mm)","DATA4_유입량(CMS)","DATA5_source_label_unknown","DATA6_총방류량(CMS)","DATA7_저수율(%)"]]+ext)
print(len(cases),"cases;",len(ext),"measurement rows;",collections.Counter((c[1],c[5]) for c in cases))
print("cases with 0 measurement rows:",sum(1 for c in cases if c[-1]==0),"; with criterion:",sum(1 for c in cases if c[12]))
