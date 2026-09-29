#!/usr/bin/env python3
"""Dam catalog (C) from raw: MyWater damList + getBasic; cross-check flood-season limit level vs 연계운영규정 별표3.
Nothing is inferred: blank = not provided by the source."""
import json, glob, csv, re, os
BASIC="01_raw/KWater/mywater_station/basic"
# labels & units exactly as printed in MyWater sumun page table headers (dam layout / weir layout)
DAM_FIELDS=[("DATA1","높이","m"),("DATA2","길이","m"),("DATA3","정상표고","EL.m"),("DATA4","체적","천m3"),("DATA5","유역면적","km2"),("DATA6","연간용수공급용량","MCM"),("DATA7","저수면적","km2"),("DATA8","계획홍수위","EL.m"),("DATA9","상시만수위","EL.m"),("DATA10","홍수기제한수위","EL.m"),("DATA11","월류정표고","EL.m"),("DATA12","저수위","EL.m"),("DATA13","총저수용량","MCM"),("DATA14","유효저수량","MCM"),("DATA15","홍수조절용량","MCM"),("DATA16","사업기간_시작","yyyymmdd"),("DATA17","사업기간_종료","yyyymmdd"),("DATA18","댐형식","code")]
# weir layout mapping is different (see period/sumun JS getBasic weir branch) -> keep raw only for weirs
def main():
    # facility list per site (period damList) with DAM_GB
    fac={}
    for fn in glob.glob("01_raw/KWater/mywater_period/D1/group*/DATA1/2021-01-01_2021-12-31.json"):
        for d in json.load(open(fn,encoding="utf-8"))["damList"]:
            fac[d["DAM_CD"]]=d
    # 별표3 flood-season limit (text) for cross-check
    a3=open("03_normalized/law_admrul_annex_000300_text.txt",encoding="utf-8").read()
    rows=[];raw_rows=[]
    for fn in sorted(glob.glob(f"{BASIC}/*.json")):
        m=re.search(r"(\d+)_damGb(\d)\.json",fn); cd,gb=m.group(1),m.group(2)
        j=json.load(open(fn,encoding="utf-8")); lst=j.get("list") or []
        if not lst: continue
        site=fac.get(cd,{}); site_gb=site.get("DAM_GB")
        rule="site damList DAM_GB"
        if site_gb is None:  # facility absent from the period damList (e.g. 평화의댐/군남댐/한탄강댐): observed rule only
            g3=json.load(open(f"{BASIC}/{cd}_damGb3.json",encoding="utf-8")).get("list")
            site_gb="3" if g3 else "1"; rule="observed: damGb=3 row present -> weir layout, else damGb=1 (identical to damGb=2 in all cases)"
            site={"DAM_NM":{"1009710":"평화의댐","1021701":"군남댐","1022701":"한탄강댐"}.get(cd,""),"DAM_BO_NM":"","RIVR_NM":"","DAM_GB":site_gb}
        raw_rows.append({"DAM_CD":cd,"damGb_requested":gb,"DAM_GB_per_site_list":site_gb,"is_layout_per_site_list":str(gb==site_gb),"raw_json":json.dumps(lst[0],ensure_ascii=False)})
        if gb!=site_gb: continue
        r=lst[0]
        row={"dam_id_source":cd,"dam_name_source":site.get("DAM_NM",""),"layout_rule":rule,"facility_type_source":site.get("DAM_BO_NM",""),"operator_per_source":"한국수자원공사(K-water) [MyWater/K-water 페이지 게재]","river_label_source":site.get("RIVR_NM",""),"latitude":"","longitude":""}
        if gb!="3":
            for k,lab,u in DAM_FIELDS: row[f"{lab}({u})[{k}]"]=r.get(k,"")
        else:
            row["weir_layout_raw"]=json.dumps(r,ensure_ascii=False)
        rows.append(row)
    keys=[]
    for r in rows:
        for k in r:
            if k not in keys: keys.append(k)
    with open("03_normalized/dam_catalog_kwater_basic.csv","w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=keys); w.writeheader(); w.writerows(rows)
    with open("03_normalized/dam_basic_raw_all_damGb.csv","w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=list(raw_rows[0].keys())); w.writeheader(); w.writerows(raw_rows)
    print(len(rows),"facilities in catalog;",len(raw_rows),"raw basic responses")
    # cross-check flood limit level: K-water DATA10 vs law annex 3
    cc=[]
    for r in rows:
        v=r.get("홍수기제한수위(EL.m)[DATA10]")
        if v in ("",None): continue
        nm=r["dam_name_source"]
        mm=re.search(r"│\s*"+r"\s*".join(list(nm.replace("댐","")))+r"\s*댐\s*│\s*([\d\.]+)",a3)
        cc.append([nm,v,mm.group(1) if mm else "(별표3에 해당 명칭 없음/매칭 실패)"])
    with open("03_normalized/crosscheck_flood_limit_level_kwater_vs_law_annex3.csv","w",newline="",encoding="utf-8-sig") as f:
        w=csv.writer(f); w.writerow(["dam_name_source","K-water MyWater 홍수기제한수위 DATA10 (EL.m)","연계운영규정 별표3 홍수기 제한수위 (EL.m; 각주표시 숫자 포함 가능)"]); w.writerows(cc)
    for c in cc: print(c)
if __name__=="__main__": main()
