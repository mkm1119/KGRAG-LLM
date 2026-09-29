#!/usr/bin/env python3
"""fetch_kwater() part 2: MyWater getBasic / getHydr / getRain for K-water facilities listed in the
law-cited 한강수계 (별표1) + K-water-listed weirs. Raw JSON preserved verbatim; resumable."""
import sys, os, json, time, hashlib, csv, datetime as dt
sys.path.insert(0, os.path.dirname(__file__))
from mywater_client import post, BASE
from fetch_kwater_mywater import windows
MAN="02_metadata/mywater_station_fetch_manifest.csv"
DAMS={ # MyWater DAM_CD : MyWater DAM_NM (as listed by site)
 "1012110":"소양강댐","1003110":"충주댐","1003611":"충주조정지","1006110":"횡성댐","1001210":"광동댐",
 "1009710":"평화의댐","1021701":"군남댐","1022701":"한탄강댐","1007601":"강천보","1007602":"여주보","1007603":"이포보"}
RES_DAMS=[d for d in DAMS if d not in("1007601","1007602","1007603")]
SPAN={"D":364,"H":29,"M":6}
START,END="2021-01-01","2026-09-28"
_mf=None;_w=None
def log(row):
    global _mf,_w
    if _w is None:
        new=not os.path.exists(MAN); _mf=open(MAN,"a",newline="",encoding="utf-8"); _w=csv.writer(_mf)
        if new: _w.writerow(["retrieval_time_utc","source_organization","source_system","API_endpoint","query_parameters_json","file_name","bytes","sha256","n_list_rows","errorChk"])
    _w.writerow(row); _mf.flush()
def do(params,fn,sleep=1.0):
    if os.path.exists(fn): return
    t,raw,j=post(params)
    if raw is None: print("FAIL",params,j,flush=True); return
    os.makedirs(os.path.dirname(fn),exist_ok=True); open(fn,"wb").write(raw)
    log([t,"K-water","MyWater(water.or.kr) 수문 ajaxProc",BASE,json.dumps(params,ensure_ascii=False),fn,len(raw),hashlib.sha256(raw).hexdigest(),len(j.get("list",[]) or []),j.get("errorChk")])
    time.sleep(sleep)
R="01_raw/KWater/mywater_station"
def basic():
    for d in DAMS:
        for gb in ("1","2","3"):
            fn=f"{R}/basic/{d}_damGb{gb}.json"
            do({"mode":"getBasic","damCd":d,"damGb":gb},fn)
def hydr():
    for res,(s,e_) in {"D":(START,END),"H":(START,END)}.items():
        for d in DAMS:
            for a,b in windows(s,e_,SPAN[res]):
                do({"mode":"getHydr","damCd":d,"param1":res,"startDate":a,"endDate":b,"page":""},f"{R}/hydr/{res}/{d}/{a}_{b}.json")
def hydr_flood10():
    for y in range(2021,2026):
        for d in RES_DAMS:
            for a,b in windows(f"{y}-06-21",f"{y}-09-30",SPAN["M"]):
                do({"mode":"getHydr","damCd":d,"param1":"M","startDate":a,"endDate":b,"page":""},f"{R}/hydr/M/{d}/{a}_{b}.json")
def rain():
    for kind in ("A","C"):
        for d in DAMS:
            if kind=="A" and d in("1007601","1007602","1007603"): continue
            for a,b in windows(START,END,SPAN["H"]):
                do({"mode":"getRain","damCd":d,"param1":kind,"rainJobGb":"H","rainStartDate":a,"rainEndDate":b},f"{R}/rain/{kind}/{d}/{a}_{b}.json")
if __name__=="__main__":
    for step in sys.argv[1:]: globals()[step](); print("DONE",step,flush=True)

# --- extra: remaining K-water 한강유역본부 facilities (per https://www.kwater.or.kr/busi/sub02/facilitiespresentPage.do?s_mid=1515)
EXTRA={"1302210":"달방댐","1003801":"단양수중보"}
def extra():
    for d in EXTRA:
        for gb in ("1","2","3"):
            do({"mode":"getBasic","damCd":d,"damGb":gb},f"{R}/basic/{d}_damGb{gb}.json")
        for res in ("D","H"):
            for a,b in windows(START,END,SPAN[res]):
                do({"mode":"getHydr","damCd":d,"param1":res,"startDate":a,"endDate":b,"page":""},f"{R}/hydr/{res}/{d}/{a}_{b}.json")
        for kind in ("A","C"):
            for a,b in windows(START,END,SPAN["H"]):
                do({"mode":"getRain","damCd":d,"param1":kind,"rainJobGb":"H","rainStartDate":a,"rainEndDate":b},f"{R}/rain/{kind}/{d}/{a}_{b}.json")
