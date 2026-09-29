#!/usr/bin/env python3
"""Unified Dam catalog, Criterion list, Document list, Variable dictionary, time conventions.
All texts quoted verbatim from raw; blanks = not provided by source. No inference."""
import csv, glob, re, os, json, hashlib
ADM=glob.glob("01_raw/Law/admrul_2100000282102*")[0]
ADM_URL="http://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000282102&type=XML"
x=open(ADM,encoding="utf-8").read()
arts={int(re.match(r"제(\d+)조",a).group(1)):re.sub(r"\s+"," ",a).strip() for a in re.findall(r"<조문내용><!\[CDATA\[(제\d+조\(.*?)\]\]>",x,flags=re.S)}
def W(path,hdr,rows,enc="utf-8-sig"):
    with open(path,"w",newline="",encoding=enc) as f: w=csv.writer(f); w.writerow(hdr); w.writerows(rows)
# ---------- Criterion list
a3=open("03_normalized/law_admrul_annex_000300_text.txt",encoding="utf-8").read()
han=[]
for line in re.findall(r"│[^│]*│[^│]*│([^│]+)│([^│]+)│([^│]+)│",a3):
    pass
def row(nm):
    m=re.search(r"│\s*"+r"\s*".join(list(nm))+r"\s*│\s*([\d\.]+)\s*(\d?)\s*│\s*([\d\.\-]+)",a3); return m
crit=[]; n=0
HAN=[("소양강댐","다목적댐"),("충주댐","다목적댐"),("횡성댐","다목적댐"),("화천댐","수력발전댐"),("춘천댐","수력발전댐"),("의암댐","수력발전댐"),("청평댐","수력발전댐"),("괴산댐","수력발전댐"),("팔당댐","수력발전댐")]
for nm,_ in HAN:
    core=nm.replace("댐","")
    m=re.search(r"│\s*"+r"\s*".join(list(core))+r"\s*댐\s*│\s*([^│]+?)\s*│\s*([^│]+?)\s*│",a3)
    if not m: print("MISSING",nm); continue
    n+=1
    cell=m.group(1).strip()
    crit.append([f"CR-{n:02d}","홍수기 제한수위 / 시설별 최저 운영수위","[별표3] 댐의 홍수기 제한수위(제6조): "+nm,f"홍수기 제한수위 셀 원문='{cell}'; 시설별 최저 운영수위 셀 원문='{m.group(2).strip()}'","EL.m",nm,"댐과 보 등의 연계운영규정 [별표3] (기후에너지환경부 훈령 제42호, 시행 2026-07-08)",ADM_URL,ADM,"셀 값 뒤 숫자+')'는 각주 표시로 보임(별표 원문 주: 1) 표시의 댐은 홍수기 제한수위가 별도로 설정되어 있지 않아 상시만수위를 대신 표기)" if ")" in cell else ""])
for art,typ,note in [(2,"정의(홍수기 기간·연계운영·기준지점)",""),(6,"홍수기 운영: 제한수위 준수, 수문조작 시 홍수통제소장 사전 승인, 저류공간 활용 지시","Approval 개념의 규범적 근거 조문(실제 승인 record 아님)"),(7,"갈수기 운영",""),(11,"연계운영 모니터링 및 조치",""),(13,"운영실적 평가 항목(월별 저수위·유입량·방류량 등)",""),(14,"비상방류(통보·요청·지시)","Operation 개념의 규범적 근거 조문(실제 운영 record 아님)")]:
    n+=1
    crit.append([f"CR-{n:02d}",typ,f"제{art}조",arts[art],"","(연계운영 대상시설 전반; 별표1 참조)","댐과 보 등의 연계운영규정 제%d조"%art,ADM_URL,ADM,note])
W("03_normalized/criterion_list.csv",["criterion_id(연구용 임시ID)","criterion_type","locator_in_document","verbatim_text_or_value","unit","applies_to_facility_per_source","defined_in_document","source_url","raw_file","note"],crit)
# ---------- Document list
docs=[]
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()
def add(did,title,org,kind,url,path,note=""):
    docs.append([did,title,org,kind,url,path,os.path.getsize(path) if os.path.exists(path) else "",sha(path) if os.path.exists(path) else "",note])
i=0
for p in sorted(glob.glob("01_raw/Regulations/*")):
    i+=1; add(f"DOC-{i:02d}",os.path.basename(p),"기후에너지환경부(법제처 게재)","원본 첨부파일(PDF/HWPX)","https://www.law.go.kr/LSW/flDownload.do (flSeq는 admrul XML 첨부파일링크 참조)",p,"댐과 보 등의 연계운영규정 훈령 제42호 시행 2026-07-08 첨부")
for p in sorted(glob.glob("01_raw/Law/*.xml")):
    b=os.path.basename(p)
    if b.startswith("search_"): continue
    i+=1
    kind="행정규칙 XML" if b.startswith("admrul") else "법령 XML"
    add(f"DOC-{i:02d}",re.sub(r"^(law|admrul)_\d+_","",b)[:-4],"법제처 국가법령정보 공동활용(DRF)",kind,"http://www.law.go.kr/DRF/lawService.do (OC=test)",p,"한강권역 하천유역수자원관리계획 고시는 2.7KB 고시문만 수집(계획 본문/첨부 미수집)" if "한강권역" in b else "")
for p in sorted(glob.glob("01_raw/KWater/pages/*"))+sorted(glob.glob("01_raw/KHNP/pages/*"))+sorted(glob.glob("01_raw/KMA/pages/*"))+sorted(glob.glob("01_raw/DataGoKr/catalog_pages/*")):
    i+=1; add(f"DOC-{i:02d}",os.path.basename(p),"K-water/KHNP/기상청/공공데이터포털","웹페이지 스냅샷(HTML, 2026-09-29 UTC)","(파일명·source_catalog 참조)",p,"")
W("03_normalized/document_list.csv",["document_id(연구용 임시ID)","title_or_filename","organization","type","source_url","raw_file","bytes","sha256","note"],docs)
# ---------- Dam catalog unified
kw=list(csv.DictReader(open("03_normalized/dam_catalog_kwater_basic.csv",encoding="utf-8-sig")))
rows=[]
BYEOL={"소양강댐","충주댐","횡성댐","광동댐","강천보","여주보","이포보","평화의댐","군남댐","한탄강댐"}
for r in kw:
    nm=r["dam_name_source"]
    inb=("별표1 한강수계 목록에 있음" if nm in BYEOL else ("별표1: '충주댐(조정지댐포함)'로 기재 — 충주조정지와의 동일시설 여부 REVIEW_REQUIRED" if nm=="충주조정지" else "별표1 한강수계 목록에 없음"))
    rows.append([r["dam_id_source"],nm,"K-water (MyWater/K-water 페이지 게재; 한강유역본부 12개 시설 목록 중 해당)","한국수자원공사","MyWater ID(DAM_CD)",r.get("river_label_source",""),inb,"","", "MyWater getBasic 원본: dam_basic_raw_all_damGb.csv / 필드: dam_catalog_kwater_basic.csv"])
for nm in ["화천","춘천","의암","청평","팔당","괴산","도암"]:
    rows.append(["",nm+"댐","KHNP 수력 실시간정보 페이지에 발전소명으로 게재","한국수력원자력","(공식 ID 미확보)","","별표1 한강수계 수력발전댐 목록에 있음","","","현재/전일 수문값만 스냅샷(01_raw/KHNP/pages/khnp_realtime_water.html); 과거 시계열·제원 미확보"])
W("03_normalized/dam_catalog.csv",["dam_id_source","dam_name_source","operator_evidence","organization","id_system","river_label_in_source(하천 그룹 표기; 검증된 수계 아님)","별표1_한강수계_목록_여부","latitude","longitude","note"],rows)
# ---------- Variable dictionary
DP15="https://www.data.go.kr/data/15099110/openapi.do"; DP49="https://www.data.go.kr/data/15099049/openapi.do"; MW="https://www.water.or.kr/kor/realtime/sumun/index.do?mode=sumun&menuId=13_91_93_94"; MWP="https://www.water.or.kr/kor/realtime/sumun/index.do?mode=period&menuId=13_91_93_95"
V=[]
def v(sid,sysn,name,field,unit,res,defn,defurl,oc,qn,cand="",st="REVIEW_REQUIRED"): V.append([sid,sysn,name,field,unit,res,defn,defurl,oc,qn,cand,"NOT_ASSESSED",st])
v("S01","MyWater getPeriod","저수위","selector DATA1 (COLn in periodList)","EL.m","10분/30분/시간/일","(MyWater 페이지에 별도 정의문 없음) data.go.kr 15099110: '댐수위[EL.m] : 저수지 수위를 의미'",DP15,"UNSPECIFIED (페이지가 관측/계산 여부를 명시하지 않음)","10분 자료는 파랑 등에 의한 순간 수위변동으로 실제와 상이 가능(페이지 고지)","water level")
v("S01","MyWater getPeriod","저수량","selector DATA2","MCM","동일","data.go.kr 15099110: '저수량[㎥/sec] : 수위를 이용해 계산된 값' (단위 표기가 카탈로그 내 '백만㎥'과 '㎥/sec'로 불일치)",DP15,"CALCULATED (수위로부터 계산, 카탈로그 서술)","카탈로그 내 단위 표기 불일치","storage")
v("S01","MyWater getPeriod","강우량","selector DATA3","mm","동일","data.go.kr: '일정한 기간 동안 내린 비의 양으로, 넓은 의미로 눈, 싸락눈, 우박, 이슬 및 서리의 양도 포함'",DP15,"UNSPECIFIED (댐 지점 관측인지 유역평균인지 미명시)","","rainfall")
v("S01","MyWater getPeriod","유입량","selector DATA4","CMS","동일","MyWater: '댐유역 및 댐의 외부에서 유입되는 유입량의 합(수위변화에 따른 저수량 차이로 계산)' / data.go.kr: '단위 시간당 댐 수위 변화에 따른 저수량의 차이와 단위 시간의 평균방류량을 이용하여 계산'",MW,"CALCULATED","두 K-water 서술의 문구가 다름. 충주조정지에서 유입량과 자체유입량이 다른 값을 보임(관찰만; 원인 해석 안 함)","inflow-related")
v("S01","MyWater getPeriod","자체유입량","selector DATA5","CMS","동일","MyWater: '외부유입량이 없는 댐유역에서만 유출되는 유량'",MW,"UNSPECIFIED","'유입량'과 다른 변수. 병합 금지","inflow-related (별개 변수)")
v("S01","MyWater getPeriod","총방류량","selector DATA6","CMS","동일","MyWater: '저수지에서 공급되는 유량의 합(저수지 상류측 취수량 및 하류측 방류량)' / data.go.kr 15099110: '방류량 : 저수지 등 수체로부터 외부로 유출되는 양'",MW,"UNSPECIFIED","두 서술의 취수량 포함 여부 표현이 다름. 발전방류/수문방류 구분 항목 미수집","discharge-related")
v("S02","MyWater getHydr","수위","DATA1","EL.m","10분/시간/일","(period의 '저수위'와 동일 항목으로 사이트가 표기하는지 문서 미확인)",MW,"UNSPECIFIED","period(2자리)와 hydr(3~4자리)는 값이 표시 정밀도 내(최대차 0.005)에서 일치","water level")
v("S02","MyWater getHydr","저수량","DATA2","MCM","동일","(위와 동일)",MW,"CALCULATED","","storage")
v("S02","MyWater getHydr","강우량","DATA3","mm","동일","(위와 동일)",MW,"UNSPECIFIED","","rainfall")
v("S02","MyWater getHydr","유입량","DATA4","CMS","동일","MyWater 페이지 정의문 (위와 동일)",MW,"CALCULATED","","inflow-related")
v("S02","MyWater getHydr","(사이트 미표시)","DATA5","","동일","사이트 JS가 표시하지 않음; 의미 미확정",MW,"UNKNOWN","period의 자체유입량 selector(DATA5)와 같은 의미인지 미검증","", "UNRESOLVED")
v("S02","MyWater getHydr","총방류량","DATA6","CMS","동일","MyWater 정의문 (위와 동일)",MW,"UNSPECIFIED","","discharge-related")
v("S02","MyWater getHydr","저수율","DATA7","%","동일","MyWater: '유효저수율(이수목적 활용): 유효저수용량(상시만수위~저수위)에 대한 현재 수위 유효저수량의 비율' / data.go.kr: '계획홍수위 기준(용수댐: 상시만수위 기준) 저수용량(총저수용량)에 대한 현재 저수량의 비율'",DP15,"CALCULATED","같은 K-water의 두 문서가 서로 다른 정의를 서술. 수치 검증: 한강 K-water 댐 다수에서 저수율≈저수량/총저수용량(중앙 절대차 0.003%p, 충주조정지 제외: 중앙차 43%p, 광동댐 최대 3.6%p) — 정의 확정 아님","storage rate")
v("S04","MyWater getRain (A)","지점명 / 시간우량 / 누적우량","DATA1 / DATA2 / DATA3, OBS_CD","- / mm / mm","요청 창 끝 시점 1건","사이트 표 머리글(시간우량(mm), 누적우량(mm)); 일자 조회 시 '일간우량'",MW,"UNSPECIFIED","응답이 기간 시계열이 아니라 요청 종료일(24시) 시점 1건(관찰). 누적 기준 시점 미확인","rainfall (station)")
v("S04","MyWater getRain (C)","지점명 / 수위 / 유량","DATA1 / DATA2 / DATA3, OBS_CD","- / m / CMS","요청 창 끝 시점 1건","사이트 표 머리글(수위(m), 유량(CMS))",MW,"UNSPECIFIED","수위 단위가 댐수위(EL.m)와 다름(m). 유량이 관측인지 수위-유량 곡선 환산인지 미명시","water level / discharge (station)")
v("S03","MyWater getBasic","제원 DATA1-18","DATA1..DATA18","dam_catalog_kwater_basic.csv 머리글 참조","스냅샷","사이트 표 머리글 (높이 m, 길이 m, 정상표고 EL.m, 체적 천m3, 유역면적 km2, 연간용수공급용량 MCM, 저수면적 km2, 계획홍수위/상시만수위/홍수기제한수위/월류정표고/저수위 EL.m, 총저수용량/유효저수량/홍수조절용량 MCM, 사업기간, 댐형식)",MW,"STATIC","보(weir) 레이아웃은 필드 매핑이 다름(원본 보존만)")
v("S06","KHNP 수력 실시간정보","댐수위","(HTML 표 행)","EL.m","실시간/전일","(정의문 없음)","https://www.khnp.co.kr/main/realTimeMgr.do?key=205&category=water","UNSPECIFIED","페이지 고지: 보정을 거친 최종자료와 다를 수 있음(잠정)","water level")
v("S06","KHNP 수력 실시간정보","유입량","(HTML 표 행)","㎥/s","실시간/전일","(정의문 없음)","https://www.khnp.co.kr/main/realTimeMgr.do?key=205&category=water","UNSPECIFIED","K-water 유입량과 동일 정의인지 미확인","inflow-related")
v("S06","KHNP 수력 실시간정보","방류량","(HTML 표 행)","㎥/s","실시간/전일","(정의문 없음)","https://www.khnp.co.kr/main/realTimeMgr.do?key=205&category=water","UNSPECIFIED","K-water '총방류량'과 동일시 금지","discharge-related")
v("S06","KHNP 수력 실시간정보","강우량","(HTML 표 행)","mm","실시간/전일","(정의문 없음)","https://www.khnp.co.kr/main/realTimeMgr.do?key=205&category=water","UNSPECIFIED","","rainfall")
v("S07","연계운영규정 별표3","홍수기 제한수위 / 시설별 최저 운영수위","(별표 표)","EL.m","기준값(규범)","규정 별표3 (제6조 관련)",ADM_URL,"NORMATIVE (측정값 아님)","각주: 상시만수위 대체 표기, 시범운영 기간 적용 수위 등","")
v("S07","연계운영규정 제2조","홍수기","(조문)","기간","-","'홍수기란 홍수 피해가 발생할 가능성이 있는 6월 21일부터 9월 20일까지의 기간'",ADM_URL,"NORMATIVE","※ 본 수집의 10분 자료 구간은 6/21~9/30(상위 구간)으로 요청함","")
v("S08","data.go.kr K-water 15099110 (미수집)","obsrdt/lowlevel/rf/inflowqy/totdcwtrqy/rsvwtqy/rsvwtrt","응답 element","일시/EL.m/㎜/㎥/sec/㎥/sec/백만㎥/%","10분/시간/일","카탈로그 응답 항목표",DP15,"(미수집; 키 필요)","MyWater와 field 이름이 다름 → 이후 교차검증 시 매핑은 REVIEW_REQUIRED","", "NOT_COLLECTED")
W("02_metadata/variable_dictionary.csv",["source_id","source_system","source_variable_name(verbatim)","raw_field_name","unit_per_source","temporal_resolution","source_definition(verbatim/quoted)","definition_source_url","observed_or_calculated","quality_note","candidate_normalized_concept(제안만, 확정 아님)","mapping_confidence","status"],V)
# ---------- time conventions
T=[["MyWater getPeriod","D1","'YYYY-MM-DD' (예 2025-07-10)","일 단위; 집계 규칙 미명시","최신→과거 순서로 반환"],
["MyWater getPeriod","H1","'YYYY-MM-DD HH' — HH가 01..24 (예 '2020-12-31 24' 관찰)","시간 단위; 24시 표기가 존재(해당 시각의 구간 종료 기준인지 미명시)","창 시작일 00시에 해당하는 행이 전일 '24'로 표기됨 → 시각 규약 REVIEW_REQUIRED"],
["MyWater getPeriod","M1","'yy-MM-dd HH:mm' (예 '21-08-02 23:50')","10분 간격","동상"],
["MyWater getHydr","D","'YYYYMMDD'","일","period와 표기만 다름"],
["MyWater getHydr","H","'YYYYMMDDHH' (예 2025063024)","시간(01..24)","hour=24 존재"],
["MyWater getRain","H(param rainJobGb)","'YYYYMMDD24' (요청 종료일 + '24')","요청 창 끝 1건","시계열 아님"],
["전체","-","시간대(timezone)","페이지에 명시 없음(미확인)","KST 여부를 자료에서 확정하지 못함 → REVIEW_REQUIRED"],
["전체","-","결측 표기","응답 JSON에서 해당 COLn 키가 사라짐(null/'' 미관찰). 정규화 테이블 key_present_in_raw=N","한강 K-water 시설 시간자료: 1행(시각)만 결측 키 확인(quality_absent_keys.csv)"],
["MyWater","-","실시간/잠정/최종 여부","MyWater 페이지: 분·시간 자료는 실시간자료(홍수시 활용), 일자료는 용수관리 활용","품질보정(최종) 여부는 미명시"],
["연계운영규정 제2조","-","홍수기 정의 6/21~9/20","규범 정의","10분 요청 구간은 6/21~9/30"]]
W("02_metadata/time_conventions.csv",["source","resolution","timestamp_format_observed","interval/aggregation","note"],T)
print(len(crit),len(docs),len(rows),len(V))
