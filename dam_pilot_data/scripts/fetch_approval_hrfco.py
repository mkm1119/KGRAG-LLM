#!/usr/bin/env python3
"""Approval gap-filling: official 한강홍수통제소 '댐방류승인' file data on data.go.kr (dataset 15085926, CSV, no login).
1) page download function -> fileDownload.do?atchFileId=FILE_000000002577079&fileDetailSn=1&insertDataPrcus=N  (used)
2/3) HRFCO web table (https://www.hrfco.go.kr/sumun/dam/damFct.do) AJAX/CSV endpoint: NOT inspectable (host unreachable: 503 DNS resolution failed / TLS reset)
4) HTML table parsing: not applicable (page unreachable)
Raw file is saved unmodified; retry on failure."""
import subprocess, time, hashlib, os, csv, datetime
URL="https://www.data.go.kr/cmm/cmm/fileDownload.do?atchFileId=FILE_000000002577079&fileDetailSn=1&insertDataPrcus=N"
OUT="01_raw/FloodControl/환경부_한강홍수통제소_홍수예보_댐방류승인_20220727.csv"
def fetch():
    for i in range(5):
        t=datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        p=subprocess.run(["curl","-sS","-L","-m","90","-o",OUT+".tmp",URL])
        if p.returncode==0 and os.path.getsize(OUT+".tmp")>1000: os.replace(OUT+".tmp",OUT); return t
        time.sleep(3*(i+1))
    raise SystemExit("download failed")
if __name__=="__main__": print(fetch(), hashlib.sha256(open(OUT,"rb").read()).hexdigest())
