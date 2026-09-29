#!/usr/bin/env python3
"""MyWater (K-water) unauthenticated period-data client.
Endpoint discovered from the site's own page JS (period.html -> /kor/realtime/sumun/ajaxProc.do).
Raw JSON responses are stored verbatim; nothing is renamed/interpolated."""
import subprocess, json, time, datetime, os, hashlib
BASE="https://www.water.or.kr/kor/realtime/sumun/ajaxProc.do"
REF="https://www.water.or.kr/kor/realtime/sumun/index.do?mode=period&menuId=13_91_93_95"
def call(param1,param2,param3,start,end,retries=4):
    data={"mode":"getPeriod","param1":param1,"param2":param2,"param3":param3,"startDate":start,"endDate":end}
    args=["curl","-sS","-m","90","-X","POST",BASE,"-H","AJAX: true","-H","X-Requested-With: XMLHttpRequest","-H","Referer: "+REF]
    for k,v in data.items(): args+=["--data-urlencode",f"{k}={v}"]
    last=None
    for i in range(retries):
        t=datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        p=subprocess.run(args,capture_output=True)
        if p.returncode==0 and p.stdout[:1]==b"{":
            try:
                j=json.loads(p.stdout); return t,data,p.stdout,j
            except Exception as e: last=str(e)
        else: last=p.stderr.decode()[:100]
        time.sleep(2*(i+1))
    return t,data,None,{"error":last}

def post(params,retries=4):
    """generic POST to the same ajaxProc endpoint with arbitrary params (mode required)."""
    args=["curl","-sS","-m","90","-X","POST",BASE,"-H","AJAX: true","-H","X-Requested-With: XMLHttpRequest","-H","Referer: https://www.water.or.kr/kor/realtime/sumun/index.do?mode=sumun&menuId=13_91_93_94"]
    for k,v in params.items(): args+=["--data-urlencode",f"{k}={v}"]
    last=None
    for i in range(retries):
        t=datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        p=subprocess.run(args,capture_output=True)
        if p.returncode==0 and p.stdout[:1]==b"{":
            try: return t,p.stdout,json.loads(p.stdout)
            except Exception as e: last=str(e)
        else: last=p.stderr.decode()[:100]
        time.sleep(2*(i+1))
    return t,None,{"error":last}
