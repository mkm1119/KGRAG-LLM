#!/usr/bin/env python3
"""Normalize approval CSV: original column names preserved, provenance columns appended. No interpretation of 비고."""
import csv, hashlib, os, datetime, collections, gzip
F="01_raw/FloodControl/환경부_한강홍수통제소_홍수예보_댐방류승인_20220727.csv"
PAGE="https://www.data.go.kr/data/15085926/fileData.do"
DL="https://www.data.go.kr/cmm/cmm/fileDownload.do?atchFileId=FILE_000000002577079&fileDetailSn=1&insertDataPrcus=N"
sha=hashlib.sha256(open(F,"rb").read()).hexdigest()
rt=datetime.datetime.utcfromtimestamp(os.path.getmtime(F)).strftime("%Y-%m-%dT%H:%M:%SZ")
rows=list(csv.reader(open(F,encoding="cp949",newline="")))
h=rows[0]; d=rows[1:]
with open("03_normalized/approval_records_hrfco_raw_fields.csv","w",newline="",encoding="utf-8-sig") as f:
    w=csv.writer(f); w.writerow(["row_number_in_file"]+h+["source_organization","source_dataset_page_url","download_url","original_file_name","file_sha256","retrieval_time_utc(file mtime; download time not separately logged)","encoding_of_original(cp949)"])
    for i,r in enumerate(d,1):
        w.writerow([i]+r+["기후에너지환경부 한강홍수통제소",PAGE,DL,os.path.basename(F),sha,rt,"cp949"])
# facility code crosswalk vs MyWater DAM_CD (descriptive; identity NOT asserted)
MW={"1012110":"소양강댐","1003110":"충주댐","1003611":"충주조정지","1006110":"횡성댐","1001210":"광동댐","1302210":"달방댐","1021701":"군남댐","1007601":"강천보","1007602":"여주보","1007603":"이포보","1009710":"평화의댐","1022701":"한탄강댐"}
agg=collections.OrderedDict()
for r in d:
    k=(r[1],r[2]); a=agg.setdefault(k,[0,r[3],r[3],collections.Counter()]); a[0]+=1; a[1]=min(a[1],r[3]); a[2]=max(a[2],r[3])
by_name={v:k for k,v in MW.items()}
with open("03_normalized/approval_facility_code_crosswalk.csv","w",newline="",encoding="utf-8-sig") as f:
    w=csv.writer(f); w.writerow(["approval_file_관측소코드","approval_file_관측소명","n_records","first_승인","last_승인","MyWater_DAM_CD_same_code","MyWater_name_for_that_code","MyWater_code_with_similar_name","relation_status"])
    for (c,n),(cnt,a,b,_) in sorted(agg.items(),key=lambda x:-x[1][0]):
        same=MW.get(c,""); sim=""
        for nm,cd in by_name.items():
            if n.replace("댐","")==nm.replace("댐",""): sim=cd
        st="same code AND similar name (동일시설 여부는 REVIEW_REQUIRED)" if same and sim==c else ("similar name but DIFFERENT code" if sim and sim!=c else ("no MyWater counterpart collected" ))
        w.writerow([c,n,cnt,a,b,c if same else "",same,sim,st])
print(len(d),"records; facilities",len(agg))
