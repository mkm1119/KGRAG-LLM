#!/usr/bin/env python3
"""fetch_kwater(): MyWater period data, batch by window, raw JSON preserved unmodified.
Resumable: skips windows whose raw file already exists. Appends provenance to manifest."""
import sys, os, json, time, hashlib, datetime as dt, csv
sys.path.insert(0, os.path.dirname(__file__))
from mywater_client import call, BASE
ROOT="01_raw/KWater/mywater_period"
MAN="02_metadata/mywater_fetch_manifest.csv"
VARS=["DATA1","DATA2","DATA3","DATA4","DATA5","DATA6"]
SPAN={"D1":364,"H1":29,"M1":6}   # inclusive window length-1 days (site limits 365/30/7)
def windows(s,e,span):
    a=dt.date.fromisoformat(s); b=dt.date.fromisoformat(e)
    while a<=b:
        z=min(a+dt.timedelta(days=span),b); yield a.isoformat(),z.isoformat(); a=z+dt.timedelta(days=1)
def run(res,group,start,end,vars_=VARS,sleep=1.0):
    os.makedirs(os.path.dirname(MAN),exist_ok=True)
    new=not os.path.exists(MAN)
    mf=open(MAN,"a",newline="",encoding="utf-8"); w=csv.writer(mf)
    if new: w.writerow(["retrieval_time_utc","source_organization","source_system","API_endpoint","param1_variable","param2_group","param3_resolution","startDate","endDate","file_name","bytes","sha256","n_damList","n_rows","errorChk"])
    for v in vars_:
        d=f"{ROOT}/{res}/group{group}/{v}"; os.makedirs(d,exist_ok=True)
        for s,e in windows(start,end,SPAN[res]):
            fn=f"{d}/{s}_{e}.json"
            if os.path.exists(fn): continue
            t,params,raw,j=call(v,group,res,s,e)
            if raw is None: print("FAIL",res,group,v,s,e,j,flush=True); continue
            open(fn,"wb").write(raw)
            w.writerow([t,"K-water","MyWater(water.or.kr) 댐/보 기간별자료",BASE,v,group,res,s,e,fn,len(raw),hashlib.sha256(raw).hexdigest(),len(j.get("damList",[])),len(j.get("periodList",[])),j.get("errorChk")]); mf.flush()
            time.sleep(sleep)
if __name__=="__main__":
    res,group,start,end=sys.argv[1:5]
    run(res,group,start,end)
    print("DONE",res,group,start,end,flush=True)
