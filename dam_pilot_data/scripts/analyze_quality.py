#!/usr/bin/env python3
"""Descriptive data-quality analysis of RAW. No repair, no interpolation."""
import json, glob, re, csv, collections, datetime as dt, os
ROOT="01_raw/KWater/mywater_period"
def days(a,b): return (dt.date.fromisoformat(b)-dt.date.fromisoformat(a)).days+1
EXP={"D1":1,"H1":24,"M1":144}
absent=[]; rows=[]; cellstat=collections.defaultdict(collections.Counter)
for fn in sorted(glob.glob(f"{ROOT}/*/group*/DATA*/*.json")):
    p=fn.split("/"); res,grp,var=p[-4],p[-3],p[-2]
    a,b=p[-1][:-5].split("_")
    try: j=json.load(open(fn,encoding="utf-8"))
    except Exception as e: rows.append([fn,res,grp,var,a,b,"","","UNREADABLE"]); continue
    n=len(j.get("periodList") or []); exp=days(a,b)*EXP[res]
    sd=[r["SDATE"] for r in j.get("periodList") or []]
    rows.append([fn,res,grp,var,a,b,n,exp,"OK" if n==exp else f"ROWS_DIFF({n-exp:+d})",len(sd)-len(set(sd)),j.get("errorChk")])
    st=cellstat[(res,grp,var)]
    dl=j.get("damList") or []
    for r in j.get("periodList") or []:
        for d in dl:
            if f"COL{d['RNUM']}" not in r:
                st["key_absent"]+=1; absent.append([fn,r.get("SDATE"),d["DAM_CD"],d["DAM_NM"],f"COL{d['RNUM']}"])
        for k,v in r.items():
            if k.startswith("COL"):
                st["cells"]+=1
                if v is None: st["None"]+=1
                elif isinstance(v,str) and v.strip()=="" : st["empty_str"]+=1
                elif isinstance(v,str): st["str_numeric"]+=1
                else: st["json_number"]+=1
w=csv.writer(open("04_reports/quality_window_completeness.csv","w",newline="",encoding="utf-8-sig"))
w.writerow(["file","resolution","group","variable_selector","start","end","rows","expected_rows","status","dup_SDATE_in_window","errorChk"]); w.writerows(rows)
w=csv.writer(open("04_reports/quality_cell_types.csv","w",newline="",encoding="utf-8-sig"))
w.writerow(["resolution","group","variable_selector","cells_present","None","empty_str","str_numeric","json_number","key_absent"])
for (res,grp,var),st in sorted(cellstat.items()): w.writerow([res,grp,var,st["cells"],st["None"],st["empty_str"],st["str_numeric"],st["json_number"],st["key_absent"]])
bad=[r for r in rows if r[8]!="OK"]
print("windows:",len(rows),"non-OK:",len(bad)); 
for r in bad[:10]: print(r)

w=csv.writer(open("04_reports/quality_absent_keys.csv","w",newline="",encoding="utf-8-sig"))
w.writerow(["file","SDATE_raw","DAM_CD","DAM_NM_source","COL_key"]); w.writerows(absent)
print("absent-key cells:",len(absent))
