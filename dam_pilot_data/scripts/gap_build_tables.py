#!/usr/bin/env python3
"""Build the data-gap supplement tables. Only facts with a stated source are filled; blanks stay blank."""
import csv,re,json,hashlib,os,collections
def wr(path,cols,rows):
    with open(path,'w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
        for r in rows: w.writerow({c:r.get(c,'') for c in cols})
    print(path,len(rows))
DG='https://www.data.go.kr/data/15085926/fileData.do'
DESC='한강홍수통제소에서 한국수자원공사와 한국수력원자력의 방류승인 요청을 받아 승인 진행을 완료한 댐 방류 승인 내역 데이터입니다. 순차번호, 댐 관측소 코드, 댐 관측소 명, 승인일자, 방류 시작시간(년월일시분), 접수 방류량(단위 : CMS), 접수일자, 비고 데이터를 제공합니다. 비고 데이터는 초기방류 사항 및 수문전폐(발전방류만 시행 등) 사항, 방류시간 변경사항, 이전 방류와 비교하여 증가 및 감소하는 방류량 등 특이사항을 기록합니다. 댐방류 승인 데이터는 2010년 7월 이후 승인된 데이터를 제공합니다.'
LOC='01_raw/FloodControl/pages/datagokr_15085926_fileData.html (상세 및 제공정보 > 설명); datagokr_15085926_fileData.json(description)'
ORG='기후에너지환경부 한강홍수통제소 (공공데이터포털 게재)'
TITLE='기후에너지환경부 한강홍수통제소_홍수예보_댐방류승인_20220726'
# ---------------- approval_field_dictionary
af=[
('순차번호','(정의문 없음; 목록 항목명 "순차번호"로만 기재)',"설명 문장에 '순차번호' 항목이 제공 항목으로 나열됨(정의 서술 없음). 파일 관찰: 1~3929 연속, 결번·중복 없음(STEP 0)",'PARTIAL','명칭 이상의 정의 없음. record 일련 번호로 읽히나 공식 정의 문장은 없음'),
('관측소코드',"'댐 관측소 코드'","설명 문장: '순차번호, 댐 관측소 코드, 댐 관측소 명, 승인일자, ...' 중 '댐 관측소 코드'",'PARTIAL','코드 체계(발급기관·체계명)가 명시되지 않음. K-water DAM_CD와 동일 체계라는 서술 없음(facility_identity_evidence.csv)'),
('관측소명',"'댐 관측소 명'","설명 문장: '댐 관측소 명'",'PARTIAL','시설(댐/보) 명칭인지 관측소 명칭인지 구분 서술 없음. K-water 시설과 달리 "댐" 접미 유무가 시설마다 다름(관찰)'),
('승인년월일시분',"'승인일자'(설명 문장); 컬럼 머리글은 '승인년월일시분'","설명 문장: '승인일자'. 파일 값은 10자(YYYY-MM-DD)이며 시각 성분 없음(3929건 전부, 관찰)",'PARTIAL','공식 설명은 날짜(승인일자)이고 머리글만 시분을 암시 → 값은 날짜로만 취급. 시각 정보는 제공되지 않음'),
('방류시작시간',"'방류 시작시간(년월일시분)'","설명 문장: '방류 시작시간(년월일시분)'. 파일 값 형식 YYYY-MM-DD HH:MM, HH 00~23(24 없음), 3929건 전부(관찰)",'VERIFIED','시간대(timezone)·계획/실제 구분은 정의되지 않음. 이 필드가 승인된 "시작 시각"인지 실제 시작인지 설명 문장은 구분하지 않음(승인 내역 데이터라는 서술만 있음)'),
('접수방류량',"'접수 방류량(단위 : CMS)'","설명 문장: '접수 방류량(단위 : CMS)'; 같은 문장은 이 데이터가 '방류승인 요청을 받아 승인 진행을 완료한 댐 방류 승인 내역'이라고 서술",'PARTIAL','단위 CMS는 공식 확인. 그러나 "접수 방류량"이 승인된 방류량(approved)인지 요청(requested)량인지는 문장에 없음 → approvedReleaseAmount로 매핑 불가(미확정). 실제 방류량(측정값)과도 동일시 금지'),
('접수일자',"(정의문 없음; '접수일자'로만 나열)","설명 문장: '접수일자'(정의 없음). 관찰: 승인일자와 값이 다른 record 62건(STEP 0)",'UNRESOLVED','무엇을 접수한 날인지(요청 접수/승인 접수) 공식 설명 없음'),
('비고',"'비고 데이터는 초기방류 사항 및 수문전폐(발전방류만 시행 등) 사항, 방류시간 변경사항, 이전 방류와 비교하여 증가 및 감소하는 방류량 등 특이사항을 기록합니다.'","설명 문장 인용(좌). 3,764건에 내용 존재(공란은 결측으로 유지)",'VERIFIED','기재 내용의 범주는 공식 설명됨(자유 텍스트 특이사항). 비고 문구를 실제 실행 사실로 해석하는 것은 공식 설명에 없음 → Operation 근거로 사용 금지 유지'),
('(데이터셋 수준) 범위/기관',"한강홍수통제소가 한국수자원공사·한국수력원자력의 방류승인 요청을 받아 승인을 완료한 내역; 2010년 7월 이후 승인분","설명 문장 인용 + 페이지 '제공기관 기후에너지환경부 한강홍수통제소', '이용허락범위 제한 없음', '업데이트 주기 수시 (1회성 데이터)', 수정일 2025-12-22",'VERIFIED','승인 기록은 "승인 완료" 건만 포함(미승인·반려 건 없음을 의미하는지는 명시되지 않음)'),
]
rows=[dict(source_field=a,official_definition=b,source_organization=ORG,source_title=TITLE,source_url=DG,source_locator=LOC,evidence_quote_or_summary=c,interpretation_status=d,note=n) for a,b,c,d,n in af]
wr('02_metadata/approval_field_dictionary.csv',['source_field','official_definition','source_organization','source_title','source_url','source_locator','evidence_quote_or_summary','interpretation_status','note'],rows)
# ---------------- time_conventions_verified
KW='K-water MyWater'; 
tc=[
(KW+' getHydr(H)','SDATE','2021013023 (YYYYMMDDHH)','(공식 정의문 없음 — 사이트 페이지/기술문서에 시각 의미 서술 없음)','미명시','미확정(구간 시작/종료 표기 불명)','관찰(원자료): 하루 24행 HH=01..24, HH=00 행은 전체 23,067일 중 1건(여주보 1007602, 2021010200)뿐. 창 시작일은 23행인 사례 11건','https://www.water.or.kr/kor/realtime/sumun/index.do?mode=sumun&menuId=13_91_93_94','03_normalized/kwater_mywater_hydr_H_wide.csv.gz (SDATE_raw)','PARTIAL (형식·분포 VERIFIED_BY_RAW; 의미 UNRESOLVED)'),
(KW+' getPeriod(H1)','SDATE','2021-01-30 23 (YYYY-MM-DD HH)','(공식 정의문 없음)','미명시','미확정','관찰: HH=01..24 + 00(소수); 창 시작 00시 해당 행은 전일 24로 표기','https://www.water.or.kr/kor/realtime/sumun/index.do?mode=period&menuId=13_91_93_95','03_normalized/kwater_mywater_period_hourly_long.csv.gz','PARTIAL'),
(KW+' getRainTrend(H)','SDATE','2020080201..2020080324','(공식 정의문 없음)','미명시','미확정','관찰(검증 호출 2건, 충주댐 소속 관측소 1001420(A)·1002655(C), 2020-08-02~03): 48행, HH=01..24, 00 없음','https://www.water.or.kr/kor/realtime/sumun/index.do?mode=sumun&menuId=13_91_93_94','01_raw/KWater/lookup_probe/*.json','PARTIAL'),
(KW+' getRain(H)','SDATE','2021013024 (요청 종료일+24)','(공식 정의문 없음)','미명시','요청 창 끝 시점 1건(시계열 아님; 관찰)','관찰: 요청 종료일 + "24"','https://www.water.or.kr/kor/realtime/sumun/index.do?mode=sumun&menuId=13_91_93_94','03_normalized/kwater_mywater_rain_level_window_snapshot_long.csv.gz','PARTIAL'),
(KW+' getHydr(D)/getPeriod(D1)','SDATE','20211231 / 2021-12-31','(공식 정의문 없음; 사이트: 일자료는 용수관리 활용)','미명시','일 단위; 집계(평균/합/말일값) 규칙 미명시','—','https://www.water.or.kr/kor/realtime/sumun/index.do?mode=period&menuId=13_91_93_95','03_normalized/kwater_mywater_hydr_D_wide.csv.gz','UNRESOLVED (집계 의미)'),
(KW+' 한강현황 페이지(한강수계 운영현황)','기준일시','2026-10-01 23:00','페이지 열 머리글 "기준일시"','KST로 추정 가능(공식 서술 아님): 재수집 수신 2026-10-01T14:03:26Z(=KST 23:03:26) vs 페이지 기준일시 23:00 (이전 수집 2026-09-29: 수신 UTC 11:59 vs 기준일시 20:50)','현재 시점 스냅샷(10분 갱신으로 보임; 근거: 기준일시 22:50/23:00 혼재)','관찰 근거: 수신시각과 기준일시의 UTC+9 정합','https://www.water.or.kr/kor/flood/floodstatus/index.do?mode=list&types=1&menuId=16_166_271_272','01_raw/KWater/pages/mywater_floodstatus_hangang_2026-10-01.html (재수집); 01_raw/KWater/pages/mywater_flood_operation_status_2026-09-29.html (기존; 원 요청 URL 미기록)','PARTIAL (정합 관찰만; 공식 timezone 서술 없음)'),
('K-water data.go.kr 수문 운영 정보(15099110)','obsrdt / obsrdtmnt','시간별 샘플 "10-01 01시", 10분 샘플 "10-01 00시 10분"','공식 기술문서 v1.5.1: 항목 "일시"(obsrdt) 설명만 있음','미명시','미확정. 단 공식 기술문서 샘플은 stdt=eddt=2018-10-01 요청에서 시간 자료가 "01시"부터, 10분 자료가 "00시 10분"부터 시작(00시 00분/00시 행 없음) — 구간 종료 기준 라벨링과 일관되나 정의문은 아님','연도 없는 문자열(MM-DD HH시)','https://www.data.go.kr/data/15099110/openapi.do ; 참고문서 기술문서_한국수자원공사_수문 운영 정보_v1.5.1.docx','01_raw/DataGoKr/tech_docs/15099110_기술문서_수문_운영_정보_v1.5.1.docx (요청 예시/응답 샘플)','PARTIAL (공식 샘플 패턴만; 명시 정의 없음)'),
('K-water data.go.kr 수문 운영 정보(15099110)','저수율/저수량 등','—','공식 설명: 저수량[백만㎥/sec 표기] vs "[㎥/sec]" — 단위 표기 불일치(카탈로그 내)','—','—','단위 표기 자체의 오류 가능성은 해석하지 않음','https://www.data.go.kr/data/15099110/openapi.do','01_raw/DataGoKr/catalog_pages/15099110.html','UNRESOLVED'),
('HRFCO 방류승인 CSV','승인년월일시분','2020-08-02','데이터셋 설명 "승인일자"','미명시','날짜만(시각 없음; 3929건 전부 10자)','머리글(년월일시분)과 값(날짜) 불일치','https://www.data.go.kr/data/15085926/fileData.do','01_raw/FloodControl/pages/datagokr_15085926_fileData.html','PARTIAL (날짜로만 VERIFIED; 시각 없음)'),
('HRFCO 방류승인 CSV','방류시작시간','2020-08-02 18:00','데이터셋 설명 "방류 시작시간(년월일시분)"','미명시','분 단위 시점; HH 00~23; 24시 표기 없음(관찰). 비고에 "08/16 24:00" 같은 24:00 표기가 2건 존재(자유 텍스트)','시각의 계획/실제 구분 정의 없음. 승인일보다 앞선 방류시작 날짜 76건(보정 안 함)','https://www.data.go.kr/data/15085926/fileData.do','01_raw/FloodControl/환경부_한강홍수통제소_홍수예보_댐방류승인_20220727.csv','PARTIAL (형식 VERIFIED; timezone/의미 UNRESOLVED)'),
('HRFCO 방류승인 CSV','접수일자','2020-08-06','(정의 없음)','미명시','날짜만','승인일자와 다른 record 62건','https://www.data.go.kr/data/15085926/fileData.do','01_raw/FloodControl/pages/datagokr_15085926_fileData.html','UNRESOLVED'),
('KHNP 수력 실시간정보 페이지','측정시간','2026-09-29 20:44:50','페이지 열 "측정시간"','KST로 추정 가능(공식 서술 아님): 파일 수신 UTC 11:46:35 = KST 20:46:35, 측정시간 20:44:50','현재 스냅샷(실시간/전일 선택)','자료는 "보정을 거친 최종자료와 다를 수 있음"(페이지 고지 원문)','https://www.khnp.co.kr/main/realTimeMgr.do?key=205&category=water','01_raw/KHNP/pages/khnp_realtime_water.html','PARTIAL'),
('법제처 행정규칙 XML','발령일자/시행일자','20240229 / 20240229','DRF 응답 항목 <발령일자>,<시행일자>(YYYYMMDD)','날짜만(시각 없음)','시행일자부터 효력(해당 버전의 시행일과 다음 연혁 시행일 사이 구간으로 읽는 것은 본 작업의 파생; 법적 효력 종료일 별도 확인 안 함)','—','http://www.law.go.kr/DRF/lawSearch.do?target=admrul','01_raw/Law_history/search_admrul_연계운영규정_history_nw2.xml','VERIFIED (항목 형식); 효력 종료는 UNRESOLVED'),
('연계운영규정 제2조','홍수기','6월 21일~9월 20일','조문: "홍수기란 홍수 피해가 발생할 가능성이 있는 6월 21일부터 9월 20일까지의 기간"(현행본)','—','날짜 구간(시각 없음)','과거 버전에서 같은 정의였는지는 버전별 조문 대조 필요(미수행)','http://www.law.go.kr/DRF/lawService.do?target=admrul&ID=2100000282102','01_raw/Law/admrul_2100000282102_*.xml','VERIFIED (현행본만)'),
]
rows=[dict(source_system=a,source_field=b,example_raw_value=c,official_definition=d,timezone=e,interval_semantics=f,special_case=g,source_url=h,source_locator=i,verification_status=j) for a,b,c,d,e,f,g,h,i,j in tc]
wr('02_metadata/time_conventions_verified.csv',['source_system','source_field','example_raw_value','official_definition','timezone','interval_semantics','special_case','source_url','source_locator','verification_status'],rows)

# ================= facility_identity_evidence =================
kw=json.load(open('scripts/gap_inputs/kw_official_codes.json'))
cw=list(csv.DictReader(open('03_normalized/approval_facility_code_crosswalk.csv',encoding='utf-8-sig')))
mw={x['dam_id_source']:x['dam_name_source'] for x in csv.DictReader(open('03_normalized/dam_catalog.csv',encoding='utf-8-sig')) if x['dam_id_source']}
HR='HRFCO 방류승인 CSV(data.go.kr 15085926)'; MW='K-water MyWater DAM_CD'; KO='K-water 공식 댐코드 목록(data.go.kr 15140222 설명)'
APF='03_normalized/approval_facility_code_crosswalk.csv'
fi=[]
def add(**k): fi.append(k)
norm=lambda n:re.sub(r'(댐|보)$','',n)
for x in cw:
    code,name=x['approval_file_관측소코드'],x['approval_file_관측소명']
    if code in mw:
        ev=f'{APF} (approval code={code}); 03_normalized/dam_catalog.csv (MyWater DAM_CD={code})'
        if code in kw: ev+=f'; 01_raw/DataGoKr/catalog_pages/15140222.html "참고사항(댐코드_DAMCD)" {code} {kw[code]}'
        add(source_system_a=HR,source_code_a=code,source_name_a=name,source_system_b=MW,source_code_b=code,source_name_b=mw[code],evidence_source=ev,evidence_locator='코드 동일; 명칭 동일(접미 "댐" 제외 비교)' if norm(name)==norm(mw[code]) else '코드 동일; 명칭 상이',candidate_status='POSSIBLE_SAME',match_basis='same code + equal name (modulo 댐 suffix) in two official listings',note='두 공식 목록이 같은 코드 체계를 공유한다는 명시적 서술 또는 공식 대응표는 확보하지 못함 → VERIFIED_SAME 불가(공식 crosswalk 필요, HRFCO 댐 관측소 코드표/WAMIS 접근 불가)')
    elif x['MyWater_code_with_similar_name']:
        c2=x['MyWater_code_with_similar_name']
        add(source_system_a=HR,source_code_a=code,source_name_a=name,source_system_b=MW,source_code_b=c2,source_name_b=mw.get(c2,''),evidence_source=f'{APF}; 03_normalized/dam_catalog.csv',evidence_locator='명칭 동일(접미 "보")·코드 상이',candidate_status='UNRESOLVED',match_basis='equal name, DIFFERENT code',note='코드가 서로 다른 공식 목록이 같은 물리 시설을 가리키는지 근거 없음(체계 차이일 가능성/별개 시설일 가능성 모두 열려 있음)')
    else:
        add(source_system_a=HR,source_code_a=code,source_name_a=name,source_system_b='(K-water MyWater: 대응 코드 없음)',evidence_source=APF,evidence_locator='relation_status=no MyWater counterpart collected',candidate_status='UNRESOLVED',match_basis='no counterpart in collected K-water list',note='한국수력원자력 운영 시설로 추정(승인 요청 기관은 K-water·KHNP 두 곳이라는 데이터셋 설명만 있음; 시설별 운영기관 명시 없음)')
# KHNP API plant codes (data.go.kr 15157779)
khnp={'3110':'화천','3120':'춘천','3140':'의암','3150':'청평','3160':'팔당','3170':'괴산'}
ap_by_name={norm(x['approval_file_관측소명']):x for x in cw}
for kc,kn in khnp.items():
    x=ap_by_name.get(kn)
    if x: add(source_system_a=HR,source_code_a=x['approval_file_관측소코드'],source_name_a=x['approval_file_관측소명'],source_system_b='KHNP 수력발전소 수문자료 OpenAPI(data.go.kr 15157779) genName',source_code_b=kc,source_name_b=kn+'수력발전소',evidence_source='01_raw/DataGoKr/catalog_pages/15157779.html (○ genName 코드표)',evidence_locator='코드 체계 상이; 명칭만 일치',candidate_status='POSSIBLE_SAME',match_basis='equal facility name only',note='KHNP API 대상은 "수력발전소"(plant)이고 승인 파일 대상은 "댐" — 엔티티 유형(plant vs dam)이 같은지 근거 없음')
# regulation names <-> approval / MyWater
reg3=[r for r in csv.DictReader(open('03_normalized/criterion_version_history.csv',encoding='utf-8-sig')) if r['effective_from(시행일자)']=='20260708' and r['facility(raw, spaces kept)']]
regname={re.sub(r'\s+','',r['facility(raw, spaces kept)']):r for r in reg3}
for x in cw:
    n=x['approval_file_관측소명']; rn=n if n.endswith('댐') else n+'댐'
    if rn in regname:
        add(source_system_a=HR,source_code_a=x['approval_file_관측소코드'],source_name_a=n,source_system_b='연계운영규정 [별표3] (시행 2026-07-08)',source_code_b='(코드 없음)',source_name_b=regname[rn]['facility(raw, spaces kept)'],evidence_source='03_normalized/criterion_version_history.csv; '+regname[rn]['raw_file'],evidence_locator='[별표3] 댐 명 열',candidate_status='POSSIBLE_SAME',match_basis='equal name (modulo 댐 suffix); regulation has no facility code',note='규정 시설 목록은 코드 없이 명칭만 사용 — Criterion–Dam 연결은 명칭 일치에 의존(공식 코드 대응 없음)')
for code,nm in mw.items():
    rn=nm if nm.endswith('댐') else nm
    if rn in regname:
        add(source_system_a=MW,source_code_a=code,source_name_a=nm,source_system_b='연계운영규정 [별표3] (시행 2026-07-08)',source_code_b='(코드 없음)',source_name_b=regname[rn]['facility(raw, spaces kept)'],evidence_source='03_normalized/dam_catalog.csv; '+regname[rn]['raw_file'],evidence_locator='[별표3] 댐 명 열',candidate_status='POSSIBLE_SAME',match_basis='equal name; regulation has no facility code',note='')
add(source_system_a=HR,source_code_a='1003611',source_name_a='충주조정지',source_system_b='연계운영규정 [별표1] (시행 2026-07-08)',source_code_b='(코드 없음)',source_name_b='충주댐(조정지댐포함)',evidence_source='01_raw/Law_history/admrul_2100000282102_댐과보등의연계운영규정_시행20260708.xml [별표1]',evidence_locator='[별표1] 한강수계 다목적댐 및 용수댐 열',candidate_status='CONFLICT',match_basis='entity granularity differs',note='규정은 조정지댐을 충주댐에 포함해 한 항목으로 서술하나, 승인 파일·K-water는 별도 코드(1003611)를 가진 별도 시설로 기재 — 시설 단위(granularity) 불일치')
add(source_system_a=HR,source_code_a='1001210',source_name_a='광동',source_system_b='연계운영규정 [별표3]',source_code_b='(코드 없음)',source_name_b='(별표3에 광동댐 없음; [별표1]에는 광동댐 있음, 2018-06-29판 이후)',evidence_source='03_normalized/criterion_version_history.csv (모든 버전 별표3에 광동댐 행 없음); 01_raw/Law_history/*20180629.xml [별표1]',evidence_locator='[별표1] vs [별표3]',candidate_status='UNRESOLVED',match_basis='absent in 별표3',note='광동댐 승인 36건에 대응할 규정 제한수위 값이 없음(Criterion appliesToDam 후보 없음)')
wr('03_normalized/facility_identity_evidence.csv',['source_system_a','source_code_a','source_name_a','source_system_b','source_code_b','source_name_b','evidence_source','evidence_locator','candidate_status','match_basis','note'],fi)
print(collections.Counter(r['candidate_status'] for r in fi))

# ================= measurement_lookup_key_evidence =================
ds=list(csv.DictReader(open('03_normalized/measurement_dataset_list.csv',encoding='utf-8-sig')))
hyd={}
for d in ds:
    if d['group_or_kind'] in('hydr-H','hydr-D'): hyd.setdefault(d['facility'].split(' ')[0],set()).add(d['group_or_kind'])
st=list(csv.DictReader(open('03_normalized/observation_station_list.csv',encoding='utf-8-sig')))
stc=collections.Counter((x['associated_DAM_CD_in_query'],x['station_type_per_source_page'][:2]) for x in st)
HY='MyWater ajaxProc getHydr (damCd=DAM_CD, param1=H|D)'
vars_=[('저수위(수위)','DATA1','EL.m'),('저수량','DATA2','MCM'),('강우량(댐 단위 항목)','DATA3','mm'),('유입량','DATA4','CMS'),('총방류량','DATA6','CMS'),('저수율','DATA7','%')]
lk=[]
U='https://www.water.or.kr/kor/realtime/sumun/index.do?mode=sumun&menuId=13_91_93_94'
for code,nm in mw.items():
    has=sorted(hyd.get(code,[]))
    for v,sel,u in vars_:
        lk.append(dict(dam_name=nm,variable_type=v,source_system=HY,lookup_key_type='DAM_CODE',lookup_key=code,source_field=f'{sel} (응답 DATAn) ; SDATE=시각 라벨; 요청 파라미터 damCd, param1(해상도), startDate, endDate',source_url=U,evidence=f'원자료 응답에 DAM_CD={code} 행으로 반환(03_normalized/kwater_mywater_hydr_*_wide.csv.gz); 수집된 dataset: {",".join(has) if has else "없음"}; 변수 정의는 variable_dictionary.csv에서 REVIEW_REQUIRED',verification_status='VERIFIED_BY_RAW_RESPONSE' if has else 'NOT_COLLECTED'))
    for kind,vn,desc in (('우량','강우량(관측소 단위: 시간우량/누적우량)','A'),('수위','수위·유량(관측소 단위)','C')):
        n=stc.get((code,'우량' if desc=='A' else '수위'),0)
        if n:
            lk.append(dict(dam_name=nm,variable_type=vn,source_system=f'MyWater ajaxProc getRain / getRainTrend (param1={desc})',lookup_key_type='STATION_CODE',lookup_key=f'damCd={code} + obsCd(OBS_CD) ; 관측소 {n}개(03_normalized/observation_station_list.csv)',source_field='OBS_CD ; 시계열 조회는 getRainTrend(damCd, obsCd, param1, rainJobGb, rainStartDate, rainEndDate)',source_url=U,evidence=('getRainTrend 검증 호출(충주댐 소속 관측소 2개, 2020-08-02~03, 각 48행 반환): 01_raw/KWater/lookup_probe/ ; ' if code=='1003110' else '이 댐은 getRainTrend를 호출하지 않음(사이트 JS의 파라미터 정의만 확인: mywater_sumun_page_2026-09-29.html) ; ')+'관측소는 조회 파라미터 damCd 아래에 나열(각 OBS_CD는 정확히 1개 damCd 아래에만 등장, 94/94) — 공간·수문학적 관계로 확정 아님',verification_status='VERIFIED_BY_RAW_RESPONSE (probe)' if code=='1003110' else 'KEY_PATTERN_FROM_SITE_JS (not probed)'))
# data.go.kr K-water API
for v,fld,u in [('저수위(댐수위)','lowlevel','EL.m'),('강우량','rf','mm'),('유입량','inflowqy','㎥/sec'),('총방류량','totdcwtrqy','㎥/sec'),('저수량','rsvwtqy','백만㎥'),('저수율','rsvwtrt','%')]:
    lk.append(dict(dam_name='(K-water 서비스 대상 61개소 전반; 한강 K-water 시설 포함 여부는 댐코드 목록으로 확인)',variable_type=v,source_system='K-water 수문 운영 정보 OpenAPI (data.go.kr 15099110; B500001/dam/sluicePresentCondition/hourlist·mntlist·delist)',lookup_key_type='DAM_CODE',lookup_key='damcode (7자리; 서비스 요청 변수, 필수) + stdt/eddt',source_field=fld,source_url='https://www.data.go.kr/data/15099110/openapi.do',evidence='공식 기술문서 v1.5.1(01_raw/DataGoKr/tech_docs/15099110_*.docx) 요청변수 표: damcode "수문제원현황 서비스의 댐코드조회 기능 참조"; 응답 항목 '+fld+' ; 인증키 필요로 실제 응답은 미수집',verification_status='OFFICIAL_DOC_ONLY (no key; not called)'))
# KHNP
for v,fld in [('강우량','qart'),('방류량','qdag'),('저수위','ulwl'),('사용수량','quew'),('유하량','qyhr')]:
    lk.append(dict(dam_name='화천·춘천·의암·청평·팔당·괴산 등 KHNP 수력발전소(API 대상 9개 발전소)',variable_type=v,source_system='KHNP 수력 발전소 수문자료 현황 OpenAPI (data.go.kr 15157779)',lookup_key_type='FACILITY_CODE',lookup_key='genName(발전소 구분 코드: 3110 화천, 3120 춘천, 3140 의암, 3150 청평, 3160 팔당, 3170 괴산 …) 또는 ippt(발전소 코드) + dgenymd(측정일)',source_field=fld,source_url='https://www.data.go.kr/data/15157779/openapi.do',evidence='01_raw/DataGoKr/catalog_pages/15157779.html 설명(요청/응답 항목표). 유입량 항목은 목록에 없음(qyhr 유하량의 의미는 정의 없음). 인증키 필요로 미호출',verification_status='OFFICIAL_DOC_ONLY (no key; not called)'))
lk.append(dict(dam_name='KHNP 수력 댐(화천·춘천·의암·청평·팔당·괴산·도암 등)',variable_type='댐수위·유입량·방류량·강우량',source_system='KHNP 수력 실시간정보 웹페이지(수문자료 실시간/전일)',lookup_key_type='FACILITY_CODE' if False else 'UNKNOWN',lookup_key='(HTML 표 열 = 시설명; 코드 없음)',source_field='(표 행/열)',source_url='https://www.khnp.co.kr/main/realTimeMgr.do?key=205&category=water',evidence='01_raw/KHNP/pages/khnp_realtime_water.html — 시설명으로만 식별, 이력 조회 기능 확인 안 됨. 페이지 고지: 보정 최종자료와 다를 수 있음',verification_status='SNAPSHOT_ONLY'))
lk.append(dict(dam_name='승인 파일 시설 16개(HRFCO 관측소코드 체계)',variable_type='댐수위·유입량·방류량 등(HRFCO 표준수문DB 댐자료)',source_system='HRFCO 표준수문DB (data.go.kr 3040409; hrfco.go.kr / api.hrfco.go.kr) / WAMIS',lookup_key_type='UNKNOWN',lookup_key='(확인 못 함)',source_field='(확인 못 함)',source_url='https://www.data.go.kr/data/3040409/openapi.do',evidence='카탈로그에는 "댐자료: 댐 관측소 제원 및 실시간 댐 자료"만 서술. hrfco.go.kr·api.hrfco.go.kr·wamis.go.kr 접속 실패(02_metadata/gap_fetch_log.csv)로 요청 변수/조회 키 명세 미확인. 승인 파일의 관측소코드가 이 API의 조회 키인지 확인 불가',verification_status='NOT_FOUND (source not accessible)'))
wr('03_normalized/measurement_lookup_key_evidence.csv',['dam_name','variable_type','source_system','lookup_key_type','lookup_key','source_field','source_url','evidence','verification_status'],lk)
print(collections.Counter((r['lookup_key_type'],r['verification_status'][:22]) for r in lk))

# ================= operation_source_search_log =================
os_=[
('OP-01','공공데이터포털(data.go.kr) 검색','검색어: 댐 방류 / 수문 조작 / 방류 통보 / 댐 운영 실적 / 수문 운영 / 방류 실적 / 수문 개폐 정보 / 충주댐 / 소양강댐 / 횡성댐 / 댐 수문 / 방류량 수문개폐 / 한강홍수통제소 댐 / 한국수력원자력 댐 방류 / 수문방류 / 댐 운영일지 / 홍수조절 실적 (총 18회)','https://www.data.go.kr/tcs/dss/selectDataSetList.do?keyword=…','OK(검색 결과 HTML 저장)','한강수계 K-water/KHNP 댐의 "실제 수문조작·방류 수행 기록"으로 판단되는 파일/API는 확인되지 않음. 관련 후보 7건은 아래 OP-02~OP-08','SEARCH_DONE','검색 결과 제목만으로 판단(검색 단서). 개별 후보는 카탈로그 원문 페이지를 읽어 판정','01_raw/DataGoKr/search/*.html'),
('OP-02','K-water','한국수자원공사_수문 방류정보 조회 서비스 (data.go.kr 15140222)','https://www.data.go.kr/data/15140222/openapi.do','카탈로그 페이지 확인; OpenAPI는 인증키·심의승인 필요(미호출)','제공항목: 방류시작 시간(STARTDATE)·방류종료 시간(ENDDATE)·메시지 생성/업데이트 시간·영향범위, 15분 주기, 댐코드 목록에 충주 1003110·소양강 1012110·횡성 1006110·광동 1001210 등 포함. 설명: "댐 수문방류정보 및 영향지역 데이터 제공 서비스(내비게이션 표출 등 재난예방)"','CANDIDATE_OPERATION_LIKE (방류 통보 메시지)','통보/예고 메시지인지 실제 수행 기록인지 공식 설명에 구분이 없음. 과거 이력 제공 여부 미기재(실시간 서비스로 서술). 키 필요','01_raw/DataGoKr/catalog_pages/15140222.html'),
('OP-03','K-water','한국수자원공사_섬진강댐 수문 개폐 정보 (data.go.kr 15117149; CSV 17,778행)','https://www.data.go.kr/data/15117149/fileData.do','다운로드 성공(미가공 저장)','설명: "수문의 개폐 상태, 개폐 시각 등의 세부 정보". 컬럼: 시간, 수문1~수문15 (숫자). 기간 2021-06-24 01:00 ~ 2023-07-05 00:00(원자료 관찰)','CANDIDATE_OPERATION_LIKE (수문 단위 개폐 값) — 한강수계 밖','섬진강댐은 본 연구 pilot 범위(한강수계)가 아님. 수문값의 단위·의미(개도율/높이 등)가 컬럼 정의서 외에는 확인 안 됨. Operation 구조(수문 단위 값)를 보여주는 참고 사례로만 보존','01_raw/DataGoKr/operation_candidates/15117149_섬진강댐_수문개폐정보.csv; 01_raw/DataGoKr/catalog_pages/15117149.html'),
('OP-04','K-water','한국수자원공사_수어댐_주암댐_방류량_수문개폐정보 샘플데이터 (15139712; XLSX 1,474행)','https://www.data.go.kr/data/15139712/fileData.do','카탈로그 확인; 파일 링크가 페이지에 노출되지 않아 미다운로드','설명: 방류 시각, 방류량, 수문 개방 여부·높이·폭','CANDIDATE_OPERATION_LIKE — 한강수계 밖, 샘플','범위 밖(섬진강수계 수어·주암); 샘플 데이터','01_raw/DataGoKr/catalog_pages/15139712.html'),
('OP-05','K-water','한국수자원공사_다목적댐 발전량 및 수문운영 데이터 (15150943; 2024-01-01~12-31 시간별, 충주·소양강 포함 9개 다목적댐)','https://www.data.go.kr/data/15150943/fileData.do','카탈로그 확인; 파일 링크 미노출로 미다운로드','제공 항목: 발전기별 발전량, 저수위, 방수로수위, 저수량, 저수율, 유입량, 자체/외부 유입량, 공용량, 총방류량','MEASUREMENT_NOT_OPERATION (수문 상태가 아닌 수문(水文) 관측·계산 변수)','기간이 2024년 단일 연도라 승인 기록(2010-2021)과 겹치지 않음. 방류 "행위"가 아니라 방류량 측정값','01_raw/DataGoKr/catalog_pages/15150943.html'),
('OP-06','K-water','한국수자원공사_수문 운영 정보 OpenAPI (15099110) 및 다목적댐/용수댐 운영 정보(15099049/15099047)','https://www.data.go.kr/data/15099110/openapi.do','카탈로그·기술문서 확인; 인증키 필요(미호출)','항목: 댐수위·강우량·유입량·총방류량·저수량·저수율 (10분/시간/일). 이름의 "수문"은 水文(hydrology)이며 수문 개폐가 아님(제공항목 목록으로 확인)','MEASUREMENT_NOT_OPERATION','MyWater에서 이미 수집한 항목과 동일 계열','01_raw/DataGoKr/catalog_pages/15099110.html; 01_raw/DataGoKr/tech_docs/'),
('OP-07','한국수력원자력','한국수력원자력(주)_수력 발전소 수문자료 현황 (15157779)','https://www.data.go.kr/data/15157779/openapi.do','카탈로그 확인; 인증키 필요(미호출)','항목: 측정일, 강우량, 방류량, 사용수량, 일일발전량, 유하량, 저수위 등 (발전소 코드/명)','MEASUREMENT_NOT_OPERATION','방류량은 측정/집계 값이며 수문조작 기록 아님(항목 목록 기준). 일 단위로 보이나 주기 명시 없음(미확인)','01_raw/DataGoKr/catalog_pages/15157779.html'),
('OP-08','K-water MyWater','한강현황 운영현황 표의 "방류상태" 열 (현재 스냅샷)','https://www.water.or.kr/kor/flood/floodstatus/index.do?mode=list&types=1&menuId=16_166_271_272','OK (2026-09-29 및 2026-10-01 두 번 저장)','한강수계 15개 시설 모두 방류상태 "-"(두 스냅샷), 의미·값 도메인 설명 없음. 이력 조회 기능 확인 안 됨','CANDIDATE_OPERATION_LIKE (현재 상태 열; 내용 없음)','값이 비어 있어 내용 확인 불가; 방류상태 정의 없음; 과거 기록 없음','01_raw/KWater/pages/mywater_floodstatus_hangang_2026-10-01.html; mywater_flood_operation_status_2026-09-29.html'),
('OP-09','K-water MyWater','수문현황 getHydr/getPeriod의 총방류량(DATA6) 시계열 (수집 완료)','https://www.water.or.kr/kor/realtime/sumun/index.do?mode=sumun&menuId=13_91_93_94','OK','방류량 측정(또는 계산)값의 시계열. 사이트 정의: "저수지에서 공급되는 유량의 합"','MEASUREMENT_NOT_OPERATION','방류 시작·종료·수문 조작 주체가 없는 결과 변수. 총방류량 변화를 Operation으로 환원하지 않음(지침)','03_normalized/kwater_mywater_hydr_*_wide.csv.gz'),
('OP-10','한강홍수통제소 / WAMIS / 환경부 / K-water 구 OpenAPI','hrfco.go.kr, api.hrfco.go.kr, wamis.go.kr, me.go.kr, opendata.kwater.or.kr','각 도메인 루트','FAIL (연결 실패/프록시 차단; 2026-09-29 및 2026-10-01 재시도 모두)','내용 확인 불가','NOT_ACCESSIBLE','"자료 없음"이 아니라 "접근 못 함". 이 환경에서 확인 불가한 출처이므로 사람이 접근 가능한 환경에서 방류 통보·운영일지 공개 여부 확인 필요','02_metadata/gap_fetch_log.csv; 04_reports/access_probe*.tsv'),
('OP-11','법제처 행정규칙','연계운영규정 제6조②(수문조작 시 홍수통제소장 사전 승인), 제14조①(방류량 조정 후 지체없이 통보), 제13조(운영실적 평가: 월별 저수위·유입량·방류량·발전량)','http://www.law.go.kr/DRF/lawService.do?target=admrul&ID=2100000134749&type=XML (2018-06-29판) 외','OK','규정은 수문조작·방류량 조정·통보라는 행위와 사전 승인·사후 통보 절차의 존재를 서술. 그 행위의 기록물 형식·공개 여부는 규정에 없음','DEFINITION_ONLY','행위의 개념 근거이며 인스턴스 자료가 아님','01_raw/Law_history/admrul_2100000134749_*.xml'),
]
wr('03_normalized/operation_source_search_log.csv',['search_id','official_source','query_or_dataset','url','access_result','finding','classification','limitation_or_failure_reason','raw_file'],[dict(zip(['search_id','official_source','query_or_dataset','url','access_result','finding','classification','limitation_or_failure_reason','raw_file'],r)) for r in os_])

# ================= data_gap_inventory =================
inv=[
('G01','Operation (실제 수행된 운영행위 instance)','Approval과 구별되는 실제 방류 수행·수문 개폐·실제 시작시각·실제 방류량 기록(한강수계 충주/소양강/횡성/광동 등)','(없음)','STEP 0/1: Operation instance 미확보(S1A-09)','한강수계 공개 자료에서 실제 운영행위 기록을 확인하지 못함','1','K-water 수문 방류정보 API(15140222, 키), HRFCO 방류통보/운영 공개자료(접속 불가), 댐 운영기관 요청','DATA_REQUIRED','03_normalized/operation_source_search_log.csv'),
('G02','Operation.operationType / operationTime 정의','수문조작·방류·방류량 조정의 구분과 시각 의미','01_raw/Law_history/*20180629.xml','규정 제6조②·제14조①이 행위·절차를 서술','행위 유형 목록/시각 정의는 규정에 없음. 공식 데이터 정의서 없음','2','연계운영규정, 댐 관리규정(미확보), K-water/HRFCO 업무 문서','DEFINITION_REQUIRED','operation_source_search_log OP-11'),
('G03','Approval --authorizes--> Operation 연결','승인과 실제 운영행위를 잇는 식별자 또는 설명','(없음)','승인 파일에 운영행위 id/참조 없음','연결 근거 자료 없음. 승인 기록을 운영행위로 대체 금지','1','Operation 자료 확보 시 동시 조사','NOT_FOUND',''),
('G04','Approval 필드: 순차번호','필드 정의','02_metadata/approval_field_dictionary.csv','공식 설명 문장에 항목 나열만 있음','명칭 이상의 정의 없음','3','data.go.kr 15085926','PARTIALLY_AVAILABLE','approval_field_dictionary.csv'),
('G05','Approval 필드: 관측소코드/관측소명','코드 체계·대상(댐/관측소) 정의','approval_field_dictionary.csv; facility_identity_evidence.csv','"댐 관측소 코드/명"이라는 표현만 있음','발급기관·코드체계 명세 없음','1','HRFCO 댐 관측소 코드표(WAMIS/hrfco; 접속 불가)','OFFICIAL_CROSSWALK_REQUIRED','approval_field_dictionary.csv'),
('G06','Approval 필드: 승인년월일시분','필드 정의, 시각 성분','approval_field_dictionary.csv','공식 설명은 "승인일자"; 값은 날짜만','머리글과 설명·값 불일치(시각 없음)','2','data.go.kr 15085926','PARTIALLY_AVAILABLE','approval_field_dictionary.csv'),
('G07','Approval 필드: 방류시작시간','필드 정의, 계획/실제, timezone','approval_field_dictionary.csv; time_conventions_verified.csv','공식 "방류 시작시간(년월일시분)"','승인된 시작 시각인지 실제 시작인지·시간대 미명시','2','data.go.kr 15085926','PARTIALLY_AVAILABLE','approval_field_dictionary.csv'),
('G08','Approval 필드: 접수방류량','"접수 방류량"의 의미(요청량/승인량)','approval_field_dictionary.csv','공식 "접수 방류량(단위 : CMS)"','승인량과의 동일성 서술 없음 — approvedReleaseAmount 매핑 불가','1','HRFCO 업무 설명/데이터 정의서(미확보)','DEFINITION_REQUIRED','approval_field_dictionary.csv'),
('G09','Approval 필드: 접수일자','필드 정의','approval_field_dictionary.csv','정의 없음','무엇의 접수일인지 불명','2','HRFCO','DEFINITION_REQUIRED','approval_field_dictionary.csv'),
('G10','Approval 필드: 비고','내용 범주','approval_field_dictionary.csv','공식 설명으로 범주 확인(초기방류·수문전폐·방류시간 변경·증감 등)','자유 텍스트; 정형 분리 불가','3','data.go.kr 15085926','ALREADY_AVAILABLE','approval_field_dictionary.csv'),
('G11','Approval.approvalContent ← 어떤 source field들','한 Approval 속성이 여러 원천 필드와 대응(접수방류량·방류시작시간·비고 등)','(없음)','온톨로지 속성 approvalContent의 구성 규칙이 문서화되지 않음','한 속성 ↔ 다수 필드: 매핑 규칙 결정 필요(온톨로지 수정은 하지 않음)','2','(사람 결정)','DEFINITION_REQUIRED','HUMAN_REVIEW_QUEUE H-04'),
('G12','Criterion 버전 이력 (2012-01-01 이후)','연계운영규정 연혁 9개판, 별표3 값','03_normalized/criterion_version_history.csv; 01_raw/Law_history/','법제처 DRF 연혁(nw=2)에서 9개판 확보; 별표3은 XML 6판 + HWP 첨부 3판에서 추출','2013-01-01·2013-04-17·2016-04-29판은 HWP 첨부 텍스트에서 복원(행 정렬은 이름·값 그룹 순서로 재구성). 효력 종료일은 법적 폐지일이 아니라 다음 판 시행일','1','국가법령정보센터','PARTIALLY_AVAILABLE','criterion_version_history.csv'),
('G13','Criterion — 2012-01-01 이전 승인(1,146건: 2010-07-16~2011-12-31)에 해당하는 규정','승인 시점에 시행되던 운영기준','(없음)','연계운영규정 시리즈의 최초 시행일은 2012-01-01(발령 2011-10-31)','그 이전 기간의 홍수기 제한수위 근거(다른 규정/댐 관리규정)는 이번 조사에서 확인 못 함','2','국가법령정보센터(구 규정·댐 관리규정), K-water 댐 관리규정','DATA_REQUIRED','criterion_version_history.csv'),
('G14','Criterion — 규정 외 시설별 기준(댐 관리규정 등)','광동댐 등 별표3에 없는 시설의 기준','(없음)','광동댐은 별표3에 모든 버전에서 행 없음','별표3 외 기준 출처 미확인','3','K-water 댐 관리규정/운영규칙','NOT_FOUND','criterion_version_history.csv'),
('G15','Criterion --appliesToDam--> Dam 근거','규정 시설명 ↔ Dam instance 대응','facility_identity_evidence.csv','규정은 코드 없이 시설명만 사용; 충주댐(조정지댐포함) 단위 불일치','명칭 일치만 가능; 코드 대응 없음','1','공식 시설 코드표','OFFICIAL_CROSSWALK_REQUIRED','facility_identity_evidence.csv'),
('G16','Dam identity: K-water ↔ 승인파일(7개 동일코드 시설)','공식 crosswalk 또는 명시적 근거','facility_identity_evidence.csv; 15140222 코드 목록','같은 코드·같은 명칭(접미 제외)이나 명시적 대응 서술은 없음','VERIFIED_SAME 불가','1','HRFCO 댐 관측소 코드표 / WAMIS / 환경부','OFFICIAL_CROSSWALK_REQUIRED','facility_identity_evidence.csv'),
('G17','Dam identity: 보 3곳(코드 상이)','강천·여주·이포 코드 대응','facility_identity_evidence.csv','승인 파일 1007801-3 vs MyWater 1007601-3','같은 시설인지 근거 없음','2','공식 코드표','OFFICIAL_CROSSWALK_REQUIRED','facility_identity_evidence.csv'),
('G18','Dam identity: KHNP 시설(승인 파일 6개 ↔ KHNP API/페이지)','코드 대응, 댐 vs 발전소 단위','facility_identity_evidence.csv','KHNP API 발전소 코드(3110 등)와 승인 파일 코드(1010310 등) 체계 상이','명칭 일치뿐; plant/dam 단위 불명','2','KHNP/HRFCO 공식 목록','OFFICIAL_CROSSWALK_REQUIRED','facility_identity_evidence.csv'),
('G19','Dam.damName / damType 출처','시설 명칭 표기·유형','03_normalized/dam_catalog*.csv','K-water getBasic에 시설 유형 표기(다목적/용수 등); KHNP·보 유형은 별표1 열 기준','출처별 표기가 다르고 유형 체계 정의 없음','3','K-water getBasic, 규정 별표1','PARTIALLY_AVAILABLE','dam_catalog_kwater_basic.csv'),
('G20','시간 규약 (MyWater)','hour=24, 구간 시작/종료, timezone','time_conventions_verified.csv','분포는 원자료로 확인(01..24; 00은 1건). 공식 기술문서 샘플은 구간 종료 라벨과 일관되나 정의문 아님','공식 정의문 없음','1','K-water 기술문서(15099110) 상세 문의, 사이트 안내','PARTIALLY_AVAILABLE','time_conventions_verified.csv'),
('G21','시간 규약 (승인 파일)','방류시작시간 timezone, 승인일 vs 접수일','time_conventions_verified.csv','형식은 확인(YYYY-MM-DD HH:MM, HH 00~23)','timezone·의미 미정','2','HRFCO','DEFINITION_REQUIRED','time_conventions_verified.csv'),
('G22','HydrometeorologicalState 조회키: 강우량','어떤 stationCode로 조회되는가','measurement_lookup_key_evidence.csv','관측소 단위: (damCd, OBS_CD) 조합; getRainTrend 검증 호출 충주 2개 관측소; 댐 단위 강우량 DATA3는 DAM_CD','댐 단위 강우량 항목이 지점 관측인지 유역평균인지 미명시; 다른 댐의 getRainTrend는 미호출','1','K-water MyWater','PARTIALLY_AVAILABLE','measurement_lookup_key_evidence.csv'),
('G23','조회키: 수위','station vs dam','measurement_lookup_key_evidence.csv','댐 저수위: DAM_CD; 하천 수위·유량 관측소(C): (damCd, OBS_CD)','HRFCO 수위관측소 코드와의 관계 미확인','1','K-water / HRFCO','PARTIALLY_AVAILABLE','measurement_lookup_key_evidence.csv'),
('G24','조회키: 유입량·방류량','stationCode 기반인지 dam code 기반인지','measurement_lookup_key_evidence.csv','MyWater: DAM_CD 기반(관측소 단위 유입·방류 없음)','stationCode가 아니라 DAM_CODE — 온톨로지의 stationCode 속성으로 표현 불가한 변수가 있음(후보로만 기록)','1','K-water','ALREADY_AVAILABLE','measurement_lookup_key_evidence.csv'),
('G25','조회키: HRFCO/WAMIS','승인 파일 관측소코드의 조회 API 키','measurement_lookup_key_evidence.csv','(없음)','접속 불가 및 명세 미확보','1','HRFCO 표준수문DB 명세','NOT_FOUND','measurement_lookup_key_evidence.csv'),
('G26','Station–Dam 연결 의미','관측소가 댐 소속인지 단순 조회 목록인지','observation_station_list.csv','94개 관측소 각각 정확히 하나의 damCd 조회 아래에만 나열','공간·수문학적 관계 근거 없음','2','K-water 관측망 설명','DEFINITION_REQUIRED','measurement_lookup_key_evidence.csv'),
('G27','승인 시점 주변 측정자료 (2010~2018 승인)','과거 승인에 대응하는 시간별 자료','03_normalized/linkage_pilot_*.csv (2019-08~2020-09 24건만)','MyWater 서비스 보유기간 2006-01~(공식 설명, 지점별 상이; data.go.kr 15099110)','2019년 이전 승인에 대한 측정 창은 수집하지 않음(수집 가능성은 미확인)','3','MyWater getHydr/getPeriod','DATA_REQUIRED','')
,('G28','EvidenceSource (sourceTitle/Type/Locator)','근거 출처 메타데이터','document_list.csv; kg_provenance_pilot.csv; 02_metadata/gap_fetch_log.csv','문서 45건 메타데이터와 행 단위 위치(row_number_in_file) 확보','승인 record의 sourceLocator 형식 확정은 사람 결정','3','-','PARTIALLY_AVAILABLE','')
]
cols=['gap_id','target_concept','required_information','existing_file','existing_evidence','current_problem','collection_priority','candidate_official_source','status','new_evidence_file']
wr('03_normalized/data_gap_inventory.csv',cols,[dict(zip(cols,r)) for r in inv])
print(collections.Counter(r[8] for r in inv))
