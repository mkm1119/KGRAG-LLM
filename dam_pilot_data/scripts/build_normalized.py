#!/usr/bin/env python3
"""RAW -> NORMALIZED (long/wide tables). No renaming of raw values, no interpolation, no unit conversion.
Only adds metadata columns. COLn -> DAM mapping is taken from each response's own damList (RNUM), never assumed."""
import json, glob, csv, gzip, os, re, sys
ROOT="01_raw/KWater/mywater_period"
OUT="03_normalized"
# variable selectors -> names/units exactly as displayed by the site's own JS (period.html: subTitle)
VAR={"DATA1":("저수위","EL.m"),"DATA2":("저수량","MCM"),"DATA3":("강우량","mm"),"DATA4":("유입량","CMS"),"DATA5":("자체유입량","CMS"),"DATA6":("총방류량","CMS")}
# facilities the site labels 한강 (RIVR_NM) -- kept as the SITE's grouping label, not as verified basin membership
HAN_LABELLED=None  # filled from data: RIVR_NM == '한강'
RES={"D1":"daily","H1":"hourly","M1":"10min"}
def load_manifest():
    m={}
    p="02_metadata/mywater_fetch_manifest.csv"
    for r in csv.DictReader(open(p,encoding="utf-8")): m[r["file_name"]]=r["retrieval_time_utc"]
    return m
def main():
    man=load_manifest()
    files=sorted(glob.glob(f"{ROOT}/*/group*/DATA*/*.json"))
    os.makedirs(OUT,exist_ok=True)
    outs={}
    def w(res):
        if res not in outs:
            f=gzip.open(f"{OUT}/kwater_mywater_period_{RES[res]}_long.csv.gz","wt",newline="",encoding="utf-8")
            cw=csv.writer(f); cw.writerow(["source_file","retrieval_time_utc","source_system","param3_resolution","param2_group","DAM_CD","DAM_NM_source","RIVR_NM_source_label","DAM_BO_NM_source","source_variable_selector","source_variable_name","unit_per_source_page","SDATE_raw","value_raw","key_present_in_raw","COL_index_in_response"])
            outs[res]=(f,cw)
        return outs[res][1]
    n=0
    for fn in files:
        parts=fn.split("/"); res=parts[-4]; grp=parts[-3].replace("group",""); var=parts[-2]
        j=json.load(open(fn,encoding="utf-8"))
        dl=j.get("damList",[]) or []
        keep=[d for d in dl if d.get("RIVR_NM")=="한강"]
        if not keep: continue
        cw=w(res); vn,un=VAR[var]
        for row in j.get("periodList",[]) or []:
            for d in keep:
                col=f"COL{d['RNUM']}"
                present="Y" if col in row else "N"   # missing = key absent in server JSON (no null/'' observed)
                v=row.get(col,None)
                cw.writerow([fn,man.get(fn,""),"MyWater ajaxProc getPeriod",res,grp,d["DAM_CD"],d["DAM_NM"],d["RIVR_NM"],d.get("DAM_BO_NM",""),var,vn,un,row["SDATE"],"" if v is None else v,present,d["RNUM"]]); n+=1
    for f,_ in outs.values(): f.close()
    print("period long rows:",n)
if __name__=="__main__": main()
