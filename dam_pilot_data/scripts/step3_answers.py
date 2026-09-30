#!/usr/bin/env python3
"""Answers = claims each tied to retrieved evidence IDs; checker verifies key strings occur in cited evidence.
The answer writer is the session model, restricted to the retrieved evidence (no pretraining domain knowledge)."""
import csv, collections
N='03_normalized/'
rd=lambda f:list(csv.DictReader(open(N+f,encoding='utf-8-sig')))
ev={e['evidence_id']:e for e in rd('qa_retrieved_evidence.csv')}
ents=rd('kg_entities_pilot.csv')
RF,DI,UC,UA,UG='RETRIEVED_FACT','DERIVED_INTERPRETATION','UNCERTAIN','UNAVAILABLE','UNSUPPORTED_GENERATION'
C=[]  # (qid, claim, class, evidence ids, key strings, in_answer)
def c(q,t,k,ids,keys=(),inans=True): C.append((q,t,k,ids,keys,inans))
c('Q01','승인파일 충주(관측소코드 1003110)에는 2020년 승인 record가 4건(순차번호 3412, 3519, 3647, 3771)이다.',RF,['Q01-E01','Q01-E02','Q01-E03','Q01-E04'],['3412','3519','3647','3771'])
c('Q01','3412: 접수일자 2020-08-02, 방류시작시간 2020-08-02 18:00, 접수방류량 3000.',RF,['Q01-E01'],['2020-08-02 18:00','3000'])
c('Q01','3519: 접수일자 2020-08-06, 방류시작시간 2020-08-02 18:00, 접수방류량 7000; 비고 원문에 (당초) 3000㎥/s (변경) 7000㎥/s가 기재됨.',RF,['Q01-E02'],['2020-08-06','7000','3000㎥/s'])
c('Q01','3647: 접수일자 2020-08-12, 방류시작시간 2020-08-06 06:00, 접수방류량 7000. 3771: 접수일자 2020-09-02, 방류시작시간 2020-09-03 12:00, 접수방류량 2000.',RF,['Q01-E03','Q01-E04'],['2020-08-12','2020-08-06 06:00','2020-09-03 12:00','2000'])
c('Q01','필드 의미(접수방류량이 승인방류량인지 등)는 미확정이며 원천 명칭 그대로 보고한다.',UC,['Q01-E01'],[])
c('Q02','소양강댐 홍수기 제한수위: 연계운영규정 [별표3] 셀 원문 190.3 (EL.m). 근거 문서 = 댐과 보 등의 연계운영규정 현행(시행 2026-07-08).',RF,['Q02-E01','Q02-E02'],['190.3','EL.m','2026-07-08'])
c('Q03','순차번호 3519 비고 원문: "방류기간 (당초) 08/02 18:00 ~ 08/12 18:00 (변경) 08/02 18:00 ~ 08/16 24:00 방류량(당초) 3000㎥/s(변경) 7000㎥/s".',RF,['Q03-E01'],['방류기간 (당초) 08/02 18:00 ~ 08/12 18:00 (변경) 08/02 18:00 ~ 08/16 24:00 방류량(당초) 3000㎥/s(변경) 7000㎥/s'])
c('Q04','MyWater 충주댐(1003110) 조회 아래 나열된 관측소는 49개(우량관측소 36, 수위관측소 13; 원천 표기). 이는 조회 목록 연관이며 공간·수문학적 관계로 확인된 것은 아니다.',RF,['Q04-E01'],['49개','36','13'])
c('Q05','충주댐 2020-08 운영행위(수문조작) 기록은 본 자료에 없다(KG에 Operation 엔티티 0건). 승인 record나 측정 변화를 운영행위로 대체하지 않는다.',UA,[],[])
c('Q05','"승인이 났으므로 수문 조작이 이루어졌다"',UG,[],[],False)
c('Q06','확보한 기준값은 현행(2026-07-08 시행) [별표3] 충주댐 제한수위 138.0 EL.m뿐이다.',RF,['Q06-E01','Q06-E02'],['138.0','2026-07-08'])
c('Q06','2020-08-02 당시 적용된 제한수위는 확인할 수 없다(당시 시행 버전 미확보). 현행 값을 당시 값으로 답하지 않는다.',UA,['Q06-E02'],[])
c('N01','승인 3412는 방류시작시간 2020-08-02 18:00, 접수방류량 3000이다.',RF,['N01-E01'],['2020-08-02 18:00','3000'])
c('N01','MyWater 충주댐(1003110) 시간자료의 방류시작시간 -6h~+12h(라벨 기준) 19행에서 수위 138.29~140.58 EL.m, 유입량 1901.39~7800.85 CMS, 총방류량 697.594~719.181 CMS이다(단순 최소/최대).',DI,['N01-E22'],['138.29','140.58','697.594','719.181','7800.85'])
c('N01','예: 2020-08-02 18시 라벨 행 수위 139.55, 유입량 4945.201, 총방류량 707.145, 저수율 77.3.',RF,['N01-E09'],['139.55','4945.201','707.145','77.3'])
c('N01','승인파일 충주와 MyWater 충주댐이 동일 시설인지는 미확정(코드·이름 유사)이며 시간 라벨 규약(hour=24, 시간대)도 미확정이다. 이 연결은 KG 간선이 아니라 대응표 조회이다.',UC,['N01-E02'],['REVIEW_REQUIRED'])
c('N01','승인 때문에 유입량이 늘었다/방류가 조절되었다',UG,[],[],False)
c('N02','2020년 횡성(1006110) 승인은 5건(3475, 3648, 3732, 3742, 3767)이며 비고 원문 예: 3475 "횡성댐 방류승인 최대 300㎥/s".',RF,['N02-E01','N02-E02'],['3475','3648','3732','3742','3767','최대 300㎥/s'])
c('N02','같은 시설명의 현행 [별표3] 횡성댐 제한수위 셀 원문은 178.2 EL.m이다(현행 2026-07-08본).',RF,['N02-E07','N02-E08'],['178.2','2026-07-08'])
c('N02','승인이 어떤 운영기준을 근거로 했는지는 자료에 없다. Approval과 Criterion을 잇는 관계·근거 기재가 없고, 당시 시행 기준도 미확보이다.',UA,['N02-E07'],[])
c('N02','승인 근거는 제한수위 178.2이다',UG,[],[],False)
c('N03','시설명이 지정된 Criterion(CR-01~09)에 광동댐은 없다(0건). 시설 지정 없는 조문(CR-10~15)만 있으며, 이들이 광동댐 승인에 적용되는지는 자료에 없다.',UA,['N03-E01'],['0건'])
c('N04','승인 3412의 접수방류량은 3000이고, 같은 창(방류시작시간 -6h~+12h)의 시간자료 총방류량은 697.594~719.181 CMS이다.',RF,['N04-E01','N04-E21'],['3000','697.594','719.181'])
c('N04','두 값이 서로 다른 개념(접수방류량 vs 총방류량)이며 창이 방류시작 후 12시간뿐이므로, 승인량만큼 방류되었는지는 이 자료로 판단할 수 없다.',UC,['N04-E01','N04-E21'],[])
c('N05','현재 상황과 유사한 과거 승인 사례를 찾는 유사도 정의·검색 방법이 본 pilot에 없어 답할 수 없다.',UA,['N05-E01'],['유사도'])
rows=[]
for i,(q,t,k,ids,keys,ia) in enumerate(C,1):
    text=' '.join(ev[e]['content'] for e in ids)
    ok=all(s in text for s in keys)
    if k==UA and q=='Q05': ok=ok and sum(1 for e in ents if e['class_']=='Operation')==0
    if k==UG: ok=None
    res='EXCLUDED' if k==UG else ('PASS' if ok else 'FAIL')
    if k in (RF,DI) and not ids: res='FAIL'
    rows.append(dict(claim_id=f'C{i:02d}',question_id=q,claim=t,claim_class=k,evidence_ids=';'.join(ids),key_strings_checked=' | '.join(keys),automatic_check=res,included_in_answer='Y' if ia else 'N'))
with open(N+'qa_answer_claim_check.csv','w',encoding='utf-8-sig',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(collections.Counter((r['claim_class'],r['automatic_check']) for r in rows))
