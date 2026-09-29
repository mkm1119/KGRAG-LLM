#!/usr/bin/env python3
"""Access probe with retries. Records every attempt (no data interpretation)."""
import subprocess, sys, csv, datetime, concurrent.futures as cf
T = [
 ("WAMIS","http://www.wamis.go.kr/"),
 ("WAMIS","http://www.wamis.go.kr:80/ssd_dam_lst.aspx"),
 ("WAMIS","https://wamis.go.kr/"),
 ("HRFCO","https://www.hrfco.go.kr/"),
 ("HRFCO","http://www.hrfco.go.kr/"),
 ("HRFCO","https://api.hrfco.go.kr/"),
 ("HRFCO","http://api.hrfco.go.kr/"),
 ("HRFCO","https://hrfco.go.kr/"),
 ("DATAGO","https://www.data.go.kr/"),
 ("DATAGO","https://apis.data.go.kr/"),
 ("DATAGO","https://www.data.go.kr/data/15000000/openapi.do"),
 ("KHNP","https://www.khnp.co.kr/main/contents.do?key=1189"),
 ("KWATER","https://www.kwater.or.kr/main.do?s_mid=1"),
 ("KWATER","https://www.water.or.kr/"),
 ("KWATER","https://www.water.or.kr/realtime/sub01/damStatus.do"),
 ("KMA","https://data.kma.go.kr/"),
 ("KMA","https://apihub.kma.go.kr/"),
 ("KMA","https://www.kma.go.kr/"),
 ("KMA","https://api.data.go.kr/"),
 ("LAW","https://www.law.go.kr/"),
 ("LAW","http://www.law.go.kr/"),
 ("LAW","https://open.law.go.kr/"),
 ("LAW","http://www.law.go.kr/DRF/lawSearch.do?OC=test&target=law&type=XML&query=%EB%8C%90"),
 ("ME","https://www.me.go.kr/"),
 ("ME","https://www.mois.go.kr/"),
]
def run(t, n=4):
    s,u=t; out=[]
    for i in range(n):
        ts=datetime.datetime.utcnow().isoformat()+"Z"
        p=subprocess.run(["curl","-sS","-L","-m","25","-o","/dev/null","-w","%{http_code}\t%{size_download}\t%{content_type}",u],capture_output=True,text=True)
        code,size,ct=(p.stdout.split("\t")+["","",""])[:3]
        out.append((ts,s,u,i+1,code,size,ct,p.stderr.strip()[:80]))
        if code.startswith(("2","3","4")) and code!="000": break
    return out
rows=[]
with cf.ThreadPoolExecutor(6) as ex:
    for r in ex.map(run,T): rows+=r
w=csv.writer(open("04_reports/access_probe_retry.tsv","w"),delimiter="\t")
w.writerow(["time_utc","source","url","attempt","http_code","bytes","content_type","error"]); w.writerows(rows)
last={}
for r in rows: last[r[2]]=r
for u,r in last.items(): print(f"{r[1]:7}{r[3]}x {r[4]:>4} {r[5]:>7}  {u[:70]} {r[7][:50]}")
