#!/usr/bin/env python3
"""STEP 1-D term inventory (Noy Step 3): comprehensive list, NOT classified into class/relation/property.
Counts are computed from the actual regulation text and Approval 비고; definitions only where a source states one."""
import csv, glob, re, json, collections
REG=open(glob.glob('01_raw/Law/admrul_2100000282102*')[0],encoding='utf-8').read()
regtext=REG.replace('<![CDATA[','\n').replace(']]>','\n'); regtext=re.sub(r'<[^>]+>','\n',regtext); regtext=re.sub(r'\s+',' ',regtext)
ap=list(csv.DictReader(open('03_normalized/approval_records_hrfco_raw_fields.csv',encoding='utf-8-sig')))
remarks=[r['비고'] for r in ap]
def cnt_reg(t): return regtext.count(t)
def cnt_rem(t): return sum(1 for b in remarks if t in b)
# definitions verbatim (제2조) from raw
art2=re.search(r'제2조\(정의\).*?(?=\]\]>)',REG,flags=re.S).group(0); art2=re.sub(r'\s+',' ',art2)
def d2(n):
    m=re.search(r'%d\. (.*?)(?= \d\. |$)'%n,art2); return m.group(1).strip() if m else ''
DEF={ '연계운영':d2(1),'기준지점':d2(2),'홍수기':d2(3),'갈수기':d2(4),'시설관리자':d2(5),'관계기관':d2(6)}
vd={ (r['source_variable_name(verbatim)'],r['source_id']):r for r in csv.DictReader(open('02_metadata/variable_dictionary.csv',encoding='utf-8-sig'))}
def vdef(name,sid): 
    r=vd.get((name,sid)); return r['source_definition(verbatim/quoted)'] if r else ''
DEF['유입량']=vdef('유입량','S01'); DEF['자체유입량']=vdef('자체유입량','S01'); DEF['총방류량']=vdef('총방류량','S01'); DEF['저수율']=vdef('저수율','S02'); DEF['저수량']=vdef('저수량','S01'); DEF['강우량']=vdef('강우량','S01')
DEF['비고']="(data.go.kr 15085926 설명) 비고 데이터는 초기방류 사항 및 수문전폐(발전방류만 시행 등) 사항, 방류시간 변경사항, 이전 방류와 비교하여 증가 및 감소하는 방류량 등 특이사항을 기록합니다."
DEF['접수방류량']="(data.go.kr 15085926 설명) 접수 방류량(단위 : CMS)"
# term rows: (term, source_kind, location, extra literature note)
R=[]
def add(term,kind,loc,lit=''): R.append((term,kind,loc,lit))
# 1 purpose & CQ (as written in handoff / user prompt)
for t in ['댐','기상','수문','상태','운영행위','승인','운영기준','근거자료','운영자','판단','관측자료','시점','기간','방류 승인','문서','관측소','측정자료','강우','유입량','저수위','방류량','과거 운영행위','당시']:
    add(t,'purpose/CQ','연구 목적 문장, CQ1–CQ6 (handoff §1.1, §4.3)')
# 2 regulation-defined & other regulation terms
for t in ['연계운영','기준지점','홍수기','갈수기','시설관리자','관계기관']: add(t,'regulation-defined','연계운영규정 제2조 정의')
for t in ['홍수통제소장','수문조작','사전 승인','제한수위','홍수기 제한수위','최저 운영수위','저류공간','홍수주의보','경보','하천유지유량','연계운영계획','연계운영협의회','비상방류','통보','지시','수계','다목적댐','용수댐','수력발전댐','둑높임','물사용 시설','저수량','발전량','수질','모니터링','운영실적','시설','수문','방류','저수위','유입량','방류량']: add(t,'regulation','연계운영규정 조문·별표1·별표3')
# 3 approval fields and remarks vocabulary
for t in ['순차번호','관측소코드','관측소명','승인년월일시분','방류시작시간','접수방류량','접수일자','비고']: add(t,'data-field','Approval CSV 컬럼(원본)')
for t in ['감소방류','증가방류','수문전폐','초기수문방류','초기방류','탄력적','변경승인','방류기간','기간연장','정정','당초','최대방류량','발전방류','추가방류','자연월류량','여수로','발전설비','수문방류','방류승인','방류시간','취소','변경없음']: add(t,'data-value','Approval `비고` 어휘(빈도순 상위 토큰에서 선택; 의미 미부여)')
# 4 measurement / spec variables
for t in ['저수위','저수량','강우량','유입량','자체유입량','총방류량','저수율','수위','유량','시간우량','누적우량','우량관측소','수위관측소','지점코드','댐코드','댐수위','상시만수위','계획홍수위','홍수기제한수위','월류정표고','총저수용량','유효저수량','홍수조절용량','유역면적','댐형식','정상표고','사업기간','연간용수공급용량','저수면적']: add(t,'data-variable','MyWater getPeriod/getHydr/getBasic/getRain 표기, KHNP 페이지')
# 5 facility categories, basin, geography
for t in ['다목적댐','용수댐','수력발전댐','홍수조절용댐','조정지','역조정지댐','다기능보','수중보','저류지','하굿둑','한강수계','북한강','남한강','섬강','소양강','합류','상류','하류','지류','본류','하천']: add(t,'facility/basin term','별표1, K-water 시설 소개 텍스트, MyWater')
# 6 documents / actors
for t in ['훈령','별표','제·개정','시행일자','고시','하천법','댐건설ㆍ관리 및 주변지역지원 등에 관한 법률','댐관리규정','관리규정','비상대처계획']: add(t,'document term','법제처 문서 목록, 규정 조문')
for t in ['홍수통제소','한국수자원공사','한국수력원자력','기후에너지환경부','운영기관']: add(t,'actor term','규정 제2조·제6조·별표2, 승인 파일 제공기관, MyWater/KHNP 페이지')
# 7 literature terms (as appearing in the papers; page from verified reading)
LIT=[('Dam','DDKG c1 Dam (Table 1 text; p.4)'),('Parameter','DDKG c4 Parameter (p.4, p.11)'),('Location','DDKG c3 Location'),('SafetyEvaluation','DDKG c7 SafetyEvaluation'),('Sensor','OntoDSMS p.4–5 (SOSA: sensors, observations, procedures, features of interest, samples, actuators)'),('Observation','OntoDSMS p.4 (SOSA Observation)'),('Structure','OntoDSMS p.5 (class Structure)')]
for t,l in LIT: add(t,'literature term',l,'검토 참고용(우리 용어 아님)')
out=[];seen=set()
for i,(t,k,l,lit) in enumerate(R,1):
    key=(t,k)
    if key in seen: continue
    seen.add(key)
    out.append({'term_id':f'T{len(out)+1:03d}','term_verbatim':t,'source_kind':k,'source_location':l,'occurrences_in_regulation_text':cnt_reg(t) if k not in('literature term',) else '', 'approval_records_containing_in_비고':cnt_rem(t) if k in('data-value','purpose/CQ','regulation','facility/basin term','actor term','data-variable') else '','source_stated_definition(verbatim)':DEF.get(t,''),'literature_note':lit,'classification':'NOT_CLASSIFIED (Noy Step 3: 용어를 클래스/슬롯 구분 없이 수집)'})
cols=list(out[0].keys())
with open('03_normalized/step1_term_inventory.csv','w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); w.writerows(out)
print(len(out),'terms'); print(collections.Counter(o['source_kind'] for o in out))
zero=[o['term_verbatim'] for o in out if o['source_kind']=='regulation' and o['occurrences_in_regulation_text']==0]; print('regulation-kind terms with 0 hits in regulation text:',zero)
