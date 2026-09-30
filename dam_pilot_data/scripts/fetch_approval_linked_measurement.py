#!/usr/bin/env python3
"""Minimal hourly Measurement around selected approval periods (Approval + Measurement linkage pilot).
Selection basis (from approval CSV, method-neutral): K-water-coded facilities with approvals >= 2019-08-01.
  Window A 2020-07-25..2020-09-10: 광동(1001210), 충주(1003110), 충주조정지(1003611; 충주댐 공식 하류 서술 시설), 횡성(1006110), 소양강(1012110)
  Window B 2019-08-01..2019-10-15: 광동(1001210)
Endpoints identical to earlier collectors; raw responses stored unmodified; own manifest."""
import sys, os, json, time, hashlib, csv
sys.path.insert(0, os.path.dirname(__file__))
from mywater_client import post, call, BASE
from fetch_kwater_mywater import windows
ROOT="01_raw/KWater/mywater_approval_linked"; MAN="02_metadata/mywater_approval_linked_manifest.csv"
A=("2020-07-25","2020-09-10"); B=("2019-08-01","2019-10-15")
HYDR={"A":["1001210","1003110","1003611","1006110","1012110"],"B":["1001210"]}
PERIOD={"A":[("1","1003110/충주·충주조정지·횡성·소양강 group1"),("2","광동 group2")],"B":[("2","광동 group2")]}
VARS=["DATA1","DATA2","DATA3","DATA4","DATA5","DATA6"]
new=not os.path.exists(MAN); mf=open(MAN,"a",newline="",encoding="utf-8"); w=csv.writer(mf)
if new: w.writerow(["retrieval_time_utc","window","endpoint","query_parameters_json","file_name","bytes","sha256","n_rows","errorChk"])
def save(t,win,params,raw,j,fn,n):
    os.makedirs(os.path.dirname(fn),exist_ok=True); open(fn,"wb").write(raw)
    w.writerow([t,win,BASE,json.dumps(params,ensure_ascii=False),fn,len(raw),hashlib.sha256(raw).hexdigest(),n,j.get("errorChk")]); mf.flush(); time.sleep(1.0)
for win,(s,e) in (("A",A),("B",B)):
    for a,b in windows(s,e,29):
        for d in HYDR[win]:
            fn=f"{ROOT}/hydr/H/{d}/{a}_{b}.json"
            if os.path.exists(fn): continue
            p={"mode":"getHydr","damCd":d,"param1":"H","startDate":a,"endDate":b,"page":""}
            t,raw,j=post(p)
            if raw is None: print("FAIL",p,j); continue
            save(t,win,p,raw,j,fn,len(j.get("list") or []))
        for g,_ in PERIOD[win]:
            for v in VARS:
                fn=f"{ROOT}/period/H1/group{g}/{v}/{a}_{b}.json"
                if os.path.exists(fn): continue
                t,params,raw,j=call(v,g,"H1",a,b)
                if raw is None: print("FAIL",params,j); continue
                save(t,win,params,raw,j,fn,len(j.get("periodList") or []))
print("DONE")
