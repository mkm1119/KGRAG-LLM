#!/usr/bin/env python3
"""Normalized tables from station-level raw (getHydr, getRain) + ObservationStation list + MeasurementDataset list.
Raw field names DATA1..DATA7 are kept; source-page labels are added as separate metadata columns."""
import json, glob, csv, gzip, os, re, collections, hashlib
R="01_raw/KWater/mywater_station"; O="03_normalized"
HYDR_LABEL={"DATA1":("수위","EL.m"),"DATA2":("저수량","MCM"),"DATA3":("강우량","mm"),"DATA4":("유입량","CMS"),"DATA5":("(사이트 미표시; 의미 미확정)",""),"DATA6":("총방류량","CMS"),"DATA7":("저수율","%")}
RAIN_LABEL={"A":{"DATA1":("지점명",""),"DATA2":("시간우량","mm"),"DATA3":("누적우량","mm")},"C":{"DATA1":("지점명",""),"DATA2":("수위","m"),"DATA3":("유량","CMS")}}
man={}
for r in csv.DictReader(open("02_metadata/mywater_station_fetch_manifest.csv",encoding="utf-8")): man[r["file_name"]]=r
def rt(fn): return man.get(fn,{}).get("retrieval_time_utc","")
# --- hydr
for res in ("D","H","M"):
    fs=sorted(glob.glob(f"{R}/hydr/{res}/*/*.json"))
    if not fs: continue
    with gzip.open(f"{O}/kwater_mywater_hydr_{res}_wide.csv.gz","wt",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["source_file","retrieval_time_utc","param1_resolution","DAM_CD","SDATE_raw","DATA1_수위(EL.m)","DATA2_저수량(MCM)","DATA3_강우량(mm)","DATA4_유입량(CMS)","DATA5_source_label_unknown","DATA6_총방류량(CMS)","DATA7_저수율(%)"])
        n=0
        for fn in fs:
            for r in json.load(open(fn,encoding="utf-8")).get("list") or []:
                w.writerow([fn,rt(fn),res,r.get("DAM_CD"),r.get("SDATE")]+[r.get(k,"") for k in ("DATA1","DATA2","DATA3","DATA4","DATA5","DATA6","DATA7")]); n+=1
    print("hydr",res,n)
# --- rain / level stations
stations={}
with gzip.open(f"{O}/kwater_mywater_rain_level_window_snapshot_long.csv.gz","wt",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["source_file","retrieval_time_utc","DAM_CD_query","station_type_param1","OBS_CD","DATA1_지점명","SDATE_raw","DATA2_raw","DATA2_label","DATA3_raw","DATA3_label"])
    n=0
    for fn in sorted(glob.glob(f"{R}/rain/*/*/*.json")):
        kind=fn.split("/")[-3]; lab=RAIN_LABEL[kind]
        for r in json.load(open(fn,encoding="utf-8")).get("list") or []:
            key=(r.get("DAM_CD"),kind,r.get("OBS_CD")); stations.setdefault(key,r.get("DATA1"))
            w.writerow([fn,rt(fn),r.get("DAM_CD"),kind,r.get("OBS_CD"),r.get("DATA1"),r.get("SDATE"),r.get("DATA2",""),"%s(%s)"%lab["DATA2"],r.get("DATA3",""),"%s(%s)"%lab["DATA3"]]); n+=1
print("rain rows",n)
names={"1012110":"소양강댐","1003110":"충주댐","1003611":"충주조정지","1006110":"횡성댐","1001210":"광동댐","1009710":"평화의댐","1021701":"군남댐","1022701":"한탄강댐","1007601":"강천보","1007602":"여주보","1007603":"이포보"}
with open(f"{O}/observation_station_list.csv","w",newline="",encoding="utf-8-sig") as f:
    w=csv.writer(f); w.writerow(["station_id_OBS_CD","station_name_source","station_type_per_source_page","associated_DAM_CD_in_query","associated_dam_name_source","source_system","note"])
    for (d,k,o),nm in sorted(stations.items()):
        w.writerow([o,nm,"우량관측소(A)" if k=="A" else "수위관측소(C)",d,names.get(d,""),"MyWater getRain","연관은 조회 파라미터(damCd) 기준이며 공간·수문학적 관계로 확정되지 않음; 좌표 미제공"])
print("stations",len(stations))
# --- MeasurementDataset list (inventory of what was actually retrieved)
rows=[]
def add(sid,res,group,var,files,dams,note=""):
    if not files: return
    spans=[re.search(r"(\d{4}-\d\d-\d\d)_(\d{4}-\d\d-\d\d)\.json",x) for x in files]
    a=min(s.group(1) for s in spans); b=max(s.group(2) for s in spans)
    rows.append([sid,"K-water MyWater",res,group,var,dams,a,b,len(files),"; ".join(sorted({os.path.dirname(x) for x in files}))[:200],note])
VARN={"DATA1":"저수위","DATA2":"저수량","DATA3":"강우량","DATA4":"유입량","DATA5":"자체유입량","DATA6":"총방류량"}
grp=collections.defaultdict(list)
for fn in glob.glob("01_raw/KWater/mywater_period/*/group*/DATA*/*.json"):
    p=fn.split("/"); grp[(p[-4],p[-3],p[-2])].append(fn)
i=0
for (res,g,v),fs in sorted(grp.items()):
    i+=1; add(f"DS-P{i:03d}",{"D1":"daily","H1":"hourly","M1":"10min"}[res],g,f"{v}={VARN[v]}",fs,"group내 전 시설 응답(damList) 원본 보존",
      "" if not (res=="H1" and g=="group3") else "INCOMPLETE: 사용자 지시로 수집 중단")
gs=collections.defaultdict(list)
for fn in glob.glob(f"{R}/hydr/*/*/*.json"): p=fn.split("/"); gs[("hydr-"+p[-3],p[-2])].append(fn)
for fn in glob.glob(f"{R}/rain/*/*/*.json"): p=fn.split("/"); gs[("rain-"+p[-3],p[-2])].append(fn)
for (k,d),fs in sorted(gs.items()):
    i+=1; add(f"DS-S{i:03d}",{"hydr-D":"daily","hydr-H":"hourly","hydr-M":"10min"}.get(k,"window-end snapshot (param rainJobGb=H)"),k,"getHydr DATA1-7" if k.startswith("hydr") else "getRain",fs,f"{d} {names.get(d,'')}",
      ("NOT A TIME SERIES: getRain returned one record per station per request window (SDATE=end date+'24'); per-station series needs getRainTrend (not collected)" if k.startswith("rain") else "")+(" | INCOMPLETE(user-directed stop)" if (k=="rain-C" and d=="1006110") else ""))
with open(f"{O}/measurement_dataset_list.csv","w",newline="",encoding="utf-8-sig") as f:
    w=csv.writer(f); w.writerow(["dataset_id(연구용 임시ID)","source","temporal_resolution","group_or_kind","variable(s)","facility","start_requested","end_requested","n_raw_files","raw_dirs","status_note"]); w.writerows(rows)
print("datasets",len(rows))
