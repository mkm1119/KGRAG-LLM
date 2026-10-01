#!/usr/bin/env python3
"""Parse [별표3] 댐의 홍수기 제한수위 from each historical version XML (raw preserved; no inference)."""
import re,glob,csv,json,os
R='01_raw/Law_history/'
hist={r[0]:r for r in json.load(open('scripts/gap_inputs/hist.json'))}
out=[];summ=[]
def clean(x): return re.sub(r'\s+','',x)
for f in sorted(glob.glob(R+'admrul_*.xml'),key=lambda f:re.search(r'시행(\d+)',f).group(1)):
    seq=re.search(r'admrul_(\d+)_',f).group(1); h=hist[seq]
    s=open(f,encoding='utf-8').read()
    for m in re.finditer(r'<별표단위[^>]*>(.*?)</별표단위>',s,flags=re.S):
        b=m.group(1)
        t=re.search(r'<별표제목><!\[CDATA\[(.*?)\]\]>',b)
        if not t or '홍수기 제한수위' not in t.group(1): continue
        body=re.sub(r'<!\[CDATA\[|\]\]>','',re.search(r'<별표내용>(.*?)</별표내용>',b,flags=re.S).group(1))
        note=re.search(r'주\)(.*)',body,flags=re.S); note=re.sub(r'\s+',' ',note.group(1)).strip() if note else ''
        basin=typ=''; n=0
        for line in body.split('\n'):
            if not line.startswith('│'): continue
            cells=[c.strip() for c in line.strip().strip('│').split('│')]
            if len(cells)<5 or cells[0]=='구 분' or cells[0].startswith('(') : continue
            if cells[0]: basin=(basin+cells[0]) if False else cells[0]
            # basin names span two rows ("한 강"/"수 계"): handled by combining below
            if cells[1]: typ=cells[1]
            name=cells[2]
            if not name or name=='-' : continue
            out.append(dict(document_title='댐과 보 등의 연계운영규정',version_date=h[2],promulgation_no=h[3],revision_type=h[5],effective_from=h[4],basin_cell_raw=cells[0],facility_type_cell_raw=cells[1] or typ+' (carried from previous row; blank cell in source)',facility=name,facility_normalized=clean(name),criterion_type='홍수기 제한수위 / 시설별 최저 운영수위 ([별표3] 제6조)',flood_limit_raw=cells[3],min_operating_raw=cells[4],unit='EL.m',source_footnote_text=note,source_url=f'http://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID={seq}&type=XML',source_locator='[별표 3] 댐의 홍수기 제한수위(제6조)',raw_file=f,admrul_seq=seq)); n+=1
        summ.append((h[4],n))
print(summ)
json.dump(out,open('scripts/gap_inputs/crit_rows.json','w'),ensure_ascii=False)
