#!/usr/bin/env python3
"""fetch_law(): law.go.kr DRF (OC=test sample id, unauthenticated) - raw XML of selected statutes/admin rules."""
import subprocess, re, time, glob, os, csv, datetime, hashlib
WANT={ 'law':['하천법','하천법 시행령','댐건설ㆍ관리 및 주변지역지원 등에 관한 법률','댐건설ㆍ관리 및 주변지역지원 등에 관한 법률 시행령','저수지ㆍ댐의 안전관리 및 재해예방에 관한 법률'],
       'admrul':['홍수조절지 및 저류지 관리규정','한강권역 하천유역수자원관리계획 고시','지구단위 홍수방어기준','댐시설 최소유지관리기준','수문(水文)조사 업무규정','수문(水文)자료의 공인 및 저장 배포 활용 기준']}
def get(url,params,retries=5):
    for i in range(retries):
        a=["curl","-sS","-m","60","-G",url]
        for k,v in params.items(): a+=["--data-urlencode",f"{k}={v}"]
        p=subprocess.run(a,capture_output=True)
        if p.returncode==0 and p.stdout: return p.stdout
        time.sleep(2*(i+1))
    return None
rows=[]
for t,names in WANT.items():
    for n in names:
        s=get("http://www.law.go.kr/DRF/lawSearch.do",{"OC":"test","target":t,"type":"XML","query":n,"display":"100"})
        if not s: print("search fail",n); continue
        x=s.decode()
        blocks=re.findall(r'<(?:law|admrul) id="\d+">.*?</(?:law|admrul)>',x,flags=re.S)
        for b in blocks:
            nm=re.search(r'<(?:법령명한글|행정규칙명)><!\[CDATA\[(.*?)\]\]>',b).group(1)
            if nm!=n: continue
            if t=='law': sid=re.search(r'<법령일련번호>(\d+)',b).group(1); eff=re.search(r'<시행일자>(\d+)',b).group(1); params={"OC":"test","target":"law","MST":sid,"type":"XML"}
            else: sid=re.search(r'<행정규칙일련번호>(\d+)',b).group(1); eff=re.search(r'<시행일자>(\d+)',b).group(1); params={"OC":"test","target":"admrul","ID":sid,"type":"XML"}
            raw=get("http://www.law.go.kr/DRF/lawService.do",params)
            if not raw or len(raw)<500: print("body fail",n); continue
            fn=f"01_raw/Law/{t}_{sid}_{re.sub(r'[^0-9A-Za-z가-힣]','',n)}_시행{eff}.xml"
            open(fn,"wb").write(raw)
            rows.append([datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),"법제처","국가법령정보 공동활용 DRF",t,n,sid,eff,"http://www.law.go.kr/DRF/lawService.do?"+"&".join(f"{k}={v}" for k,v in params.items()),fn,len(raw),hashlib.sha256(raw).hexdigest()])
            print("OK",fn,len(raw)); break
new=not os.path.exists("02_metadata/law_fetch_manifest.csv")
w=csv.writer(open("02_metadata/law_fetch_manifest.csv","a",newline="",encoding="utf-8"))
if new: w.writerow(["retrieval_time_utc","source_organization","source_system","target","title","serial_no","effective_date","API_endpoint_with_params(OC=test)","file_name","bytes","sha256"])
w.writerows(rows)
