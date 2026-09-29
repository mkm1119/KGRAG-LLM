#!/usr/bin/env python3
import os, hashlib, csv, sys
rows=[]
CAT={"01_raw":"raw","01_raw_archive":"raw_archive","02_metadata":"metadata","03_normalized":"normalized","04_reports":"report","scripts":"code"}
for top in CAT:
    for d,_,fs in os.walk(top):
        for f in fs:
            p=os.path.join(d,f); h=hashlib.sha256(open(p,"rb").read()).hexdigest()
            rows.append([p,CAT[top],os.path.getsize(p),h])
rows.sort()
w=csv.writer(open("02_metadata/FINAL_MANIFEST.csv","w",newline="",encoding="utf-8-sig")); w.writerow(["path","category","bytes","sha256"]); w.writerows(rows)
print(len(rows),"files;",sum(r[2] for r in rows)//1024//1024,"MB")
