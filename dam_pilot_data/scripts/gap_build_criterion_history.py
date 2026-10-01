#!/usr/bin/env python3
import re,json,csv,glob,sys
sys.path.insert(0,'scripts')
rows=json.load(open('scripts/gap_inputs/crit_rows.json'))
hist={r[4]:r for r in json.load(open('scripts/gap_inputs/hist.json'))}
versions=sorted(hist)   # effective dates
def eff_to(v):
    i=versions.index(v); return versions[i+1] if i+1<len(versions) else ''
def parse_val(raw):
    m=re.match(r'^\s*(\d+\.\d)(\d\))?\s*$',raw)
    return (m.group(1),m.group(2) or '') if m else ('','')
def row_out(r,status,extra=''):
    v,fn=parse_val(r['flood_limit_raw'])
    return {'document_title':r['document_title'],'version_date(발령일자)':r['version_date'],'promulgation_no':r['promulgation_no'],'revision_type':r['revision_type'],
     'effective_from(시행일자)':r['effective_from'],'effective_to(next version 시행일자; not a legal 폐지일)':eff_to(r['effective_from']),
     'facility(raw, spaces kept)':r['facility'],'facility_type_raw':r['facility_type_cell_raw'],'criterion_type':r['criterion_type'],
     'criterion_value_raw(flood_limit)':r['flood_limit_raw'],'criterion_value_derived(footnote marker split; derived)':v,'footnote_marker_in_raw':fn,
     'min_operating_level_raw':r['min_operating_raw'],'unit':'EL.m','source_footnote_text':r['source_footnote_text'],
     'source_url':r['source_url'],'source_locator':r['source_locator'],'raw_file':r['raw_file'],'verification_status':status,'note':extra}
out=[]
for r in rows: out.append(row_out(r,'EXTRACTED_FROM_OFFICIAL_XML_TABLE'))
# HWP-attachment versions
from hwp_text_extract import hwp_text
att={'20130101':'01_raw/Law_history/attachments/별표3_flSeq12672224_시행20130101.bin','20130417':'01_raw/Law_history/attachments/별표3_flSeq13938987_시행20130417.bin','20160429':'01_raw/Law_history/attachments/별표3_flSeq24502710_시행20160429.bin'}
def clean(x): return re.sub(r'\s+','',x)
for v,f in att.items():
    t=hwp_text(f); toks=[x.strip() for x in t.split('\n') if x.strip()]
    toks=[x for x in toks if not x.startswith('捤') and x not in('氠瑢',) ]
    # strip header
    i=toks.index('(EL.m)'); i=toks.index('(EL.m)',i+1); toks=toks[i+1:]
    note_i=next((k for k,x in enumerate(toks) if x.startswith('주)')),len(toks)); note=' '.join(toks[note_i:]); toks=toks[:note_i]
    isname=lambda x:clean(x).endswith('댐') and clean(x) not in('다목적댐','수력발전댐')
    isnum=lambda x:re.match(r'^\d+\.\d(\d\))?$',x) or x=='-'
    k=0; grp=[]
    while k<len(toks):
        if isname(toks[k]):
            names=[]
            while k<len(toks) and isname(toks[k]): names.append(toks[k]); k+=1
            vals=toks[k:k+len(names)]; k+=len(names); mins=toks[k:k+len(names)]; k+=len(names)
            assert all(isnum(x) for x in vals+mins),(v,names,vals,mins)
            for n,a,b in zip(names,vals,mins):
                r=dict(document_title='댐과 보 등의 연계운영규정',version_date=hist[v][2],promulgation_no=hist[v][3],revision_type=hist[v][5],effective_from=v,facility=n,facility_type_cell_raw='(HWP 첨부 텍스트 추출: 행 정렬은 이름·값·최저수위 그룹 순서로 복원; 열 구조 직접 확인 불가)',criterion_type='홍수기 제한수위 / 시설별 최저 운영수위 ([별표3] 제6조)',flood_limit_raw=a,min_operating_raw=b,source_footnote_text=note,source_url=f'https://www.law.go.kr/LSW/flDownload.do?flSeq='+re.search(r'flSeq(\d+)',f).group(1),source_locator='[별표 3] 댐의 홍수기 제한수위(제6조) (HWP 첨부)',raw_file=f)
                out.append(row_out(r,'EXTRACTED_FROM_OFFICIAL_HWP_ATTACHMENT','name/value alignment reconstructed from extracted text order; verify against original HWP if used in analysis'))
        else: k+=1
# article-level version index (no facility) : document versions
for v in versions:
    h=hist[v]
    out.append({'document_title':'댐과 보 등의 연계운영규정','version_date(발령일자)':h[2],'promulgation_no':h[3],'revision_type':h[5],'effective_from(시행일자)':v,'effective_to(next version 시행일자; not a legal 폐지일)':eff_to(v),'facility(raw, spaces kept)':'','facility_type_raw':'','criterion_type':'(document version index)','criterion_value_raw(flood_limit)':'','criterion_value_derived(footnote marker split; derived)':'','footnote_marker_in_raw':'','min_operating_level_raw':'','unit':'','source_footnote_text':'','source_url':f'http://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID={h[0]}&type=XML','source_locator':'행정규칙기본정보','raw_file':glob.glob(f'01_raw/Law_history/admrul_{h[0]}_*.xml')[0],'verification_status':'OFFICIAL_VERSION_LIST','note':'effective_to = next listed version effective date (list from DRF nw=2); legal 폐지/효력 종료일은 별도 확인 안 함'})
cols=list(out[0].keys())
with open('03_normalized/criterion_version_history.csv','w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); w.writerows(out)
import collections
print(collections.Counter((r['effective_from(시행일자)'],r['verification_status']) for r in out))
# value comparison across versions for 한강 facilities
tab=collections.defaultdict(dict)
for r in out:
    if r['facility(raw, spaces kept)']: tab[clean(r['facility(raw, spaces kept)'])][r['effective_from(시행일자)']]=r['criterion_value_raw(flood_limit)']+'/'+r['min_operating_level_raw']
for fac in ['소양강댐','충주댐','횡성댐','화천댐','춘천댐','의암댐','청평댐','괴산댐','팔당댐','광동댐']:
    print(fac,tab.get(fac))
