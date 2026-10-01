#!/usr/bin/env python3
"""Retrying fetch with provenance logging for the data-gap supplement. Raw bytes saved unchanged."""
import subprocess, hashlib, os, sys, datetime, csv, urllib.parse
ROOT='/home/user/KGRAG-LLM/dam_pilot_data/'
LOG=ROOT+'02_metadata/gap_fetch_log.csv'
def fetch(url, out_rel, org, system, title, note='', params='', tries=6, timeout=60, extra=()):
    out=ROOT+out_rel; os.makedirs(os.path.dirname(out),exist_ok=True)
    status='FAIL'; code=''; 
    for i in range(tries):
        r=subprocess.run(['curl','-sS','-L','-m',str(timeout),'-o',out,'-w','%{http_code}',*extra,url],capture_output=True,text=True)
        code=r.stdout.strip()
        if code=='200' and os.path.getsize(out)>0: status='OK'; break
        import time; time.sleep(2*(i+1))
    sha=hashlib.sha256(open(out,'rb').read()).hexdigest() if status=='OK' else ''
    size=os.path.getsize(out) if os.path.exists(out) else 0
    if status!='OK' and os.path.exists(out): os.remove(out)
    new=not os.path.exists(LOG)
    with open(LOG,'a',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f)
        if new: w.writerow(['source_organization','source_system','source_page_title','source_url','retrieval_time_utc','request_parameters','saved_as','http_status','sha256','bytes','collection_note','result'])
        w.writerow([org,system,title,url,datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),params,out_rel if status=='OK' else '',code,sha,size,note,status])
    return status,out
if __name__=='__main__':
    print(fetch(*sys.argv[1:6]))
