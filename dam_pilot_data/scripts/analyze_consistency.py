#!/usr/bin/env python3
"""Descriptive consistency checks (no repair/interpolation, no causal claims)."""
import gzip, csv, json, collections, statistics
out={}
# 1) 저수율(DATA7) vs 저수량(DATA2)/총저수용량(DATA13) for Han K-water dams (daily hydr)
basic={}
for r in csv.DictReader(open("03_normalized/dam_catalog_kwater_basic.csv",encoding="utf-8-sig")):
    v=r.get("총저수용량(MCM)[DATA13]")
    if v not in (None,""): basic[r["dam_id_source"]]=float(v)
d=collections.defaultdict(list)
for r in csv.DictReader(gzip.open("03_normalized/kwater_mywater_hydr_D_wide.csv.gz","rt",encoding="utf-8")):
    try: q=float(r["DATA2_저수량(MCM)"]); ratio=float(r["DATA7_저수율(%)"])
    except: continue
    cap=basic.get(r["DAM_CD"])
    if cap: d[r["DAM_CD"]].append(ratio-100*q/cap)
res={}
for k,v in d.items(): res[k]={"n":len(v),"median_abs_diff_pct_points":round(statistics.median(abs(x) for x in v),3),"max_abs_diff":round(max(abs(x) for x in v),3)}
out["storage_rate_vs_storage_over_total_capacity"]=res
# 2) period D1 (group1) vs hydr D : same dam/date/variable
per={}
for r in csv.DictReader(gzip.open("03_normalized/kwater_mywater_period_daily_long.csv.gz","rt",encoding="utf-8")):
    if r["source_variable_selector"] in ("DATA1","DATA4","DATA6") and r["param2_group"]=="1":
        per[(r["DAM_CD"],r["SDATE_raw"].replace("-",""),r["source_variable_selector"])]=r["value_raw"]
mp={"DATA1":"DATA1_수위(EL.m)","DATA4":"DATA4_유입량(CMS)","DATA6":"DATA6_총방류량(CMS)"}
cmp=collections.Counter(); ex=[]
for r in csv.DictReader(gzip.open("03_normalized/kwater_mywater_hydr_D_wide.csv.gz","rt",encoding="utf-8")):
    for v,col in mp.items():
        k=(r["DAM_CD"],r["SDATE_raw"],v)
        if k in per:
            try: same=abs(float(per[k])-float(r[col]))<1e-6
            except: same=False
            cmp[(v,same)]+=1
            if not same and len(ex)<5: ex.append([k,per[k],r[col]])
out["period_vs_hydr_daily_equal"]={f"{a}:{b}":c for (a,b),c in cmp.items()}; out["period_vs_hydr_daily_mismatch_examples"]=ex
# 3) official-relation pair alignment (hourly): 충주댐 1003110 -> 충주조정지 1003611 ; timestamps present in both
ser=collections.defaultdict(dict)
for r in csv.DictReader(gzip.open("03_normalized/kwater_mywater_period_hourly_long.csv.gz","rt",encoding="utf-8")):
    if r["param2_group"]=="1" and r["DAM_CD"] in ("1003110","1003611","1012110") and r["source_variable_selector"] in ("DATA4","DATA6","DATA1"):
        ser[(r["DAM_CD"],r["source_variable_selector"])][r["SDATE_raw"]]=(r["value_raw"],r["key_present_in_raw"])
def cnt(a,b): 
    A,B=ser[a],ser[b]; both=[t for t in A if t in B and A[t][1]=="Y" and B[t][1]=="Y"]; return {"n_a":len(A),"n_b":len(B),"timestamps_with_both_present":len(both)}
out["hourly_alignment_충주댐총방류량_vs_충주조정지유입량"]=cnt(("1003110","DATA6"),("1003611","DATA4"))
ts=sorted(ser[("1003110","DATA6")]); out["hourly_range_충주댐"]=[ts[0],ts[-1]]
# 4) absent-key stats for Han-labelled facilities
ab=collections.Counter(); tot=collections.Counter()
for r in csv.DictReader(gzip.open("03_normalized/kwater_mywater_period_hourly_long.csv.gz","rt",encoding="utf-8")):
    tot[r["DAM_NM_source"]]+=1
    if r["key_present_in_raw"]=="N": ab[r["DAM_NM_source"]]+=1
out["hourly_absent_key_by_facility"]={k:f"{ab[k]}/{tot[k]}" for k in tot if ab[k]}
json.dump(out,open("04_reports/analysis_consistency.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(json.dumps(out,ensure_ascii=False,indent=1)[:3500])
