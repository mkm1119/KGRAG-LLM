#!/usr/bin/env python3
"""교수님 회의자료(docx, 5쪽 안팎): 설계한 큰 틀, 댐 운영에 적용한 KG 설계, 근거 검색과 근거 묶음, LLM 파트에서 논의할 사항.
서식은 10/09 랩미팅 자료를 따른다. 사용: NODE_PATH=... python3 scripts/build_meeting_prof.py <출력 docx>
"""
import collections, csv, importlib.util, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('L', os.path.join(HERE, 'labdoc_lib.py')); L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
for n in ('title', 'subtitle', 'dateline', 'label', 'h1', 'h2', 'para', 'li', 'lead', 'spacer', 'table', 'box', 'code', 'flow', 'image', 'caption'):
    globals()[n] = getattr(L, n)
ROOT = os.path.join(HERE, '..'); N = os.path.join(ROOT, '03_normalized'); FIG = os.path.join(ROOT, '..', 'lab_meeting', 'meeting_figs')
OUT = sys.argv[1]
T = L.Template(os.path.join(ROOT, '..', 'lab_meeting', '랩미팅 자료_KG구축_검색답변_최종.docx'))
rd = lambda p: list(csv.DictReader(open(os.path.join(N, p), encoding='utf-8-sig')))
ents, rels = rd('kgv4_entities.csv'), rd('kgv4_relations.csv')
EC, RC = collections.Counter(e['class'] for e in ents), collections.Counter(r['relation'] for r in rels)
assert (len(ents), len(rels)) == (264, 418)
SZ = collections.OrderedDict(json.load(open(os.path.join(ROOT, '04_reports', 'bundle_size_by_dam.json'), encoding='utf-8')))
S = 18
B = []; add = B.append
H = lambda t: h1(t, pagebreak=False)

add(title('댐 운영 판단 지원을 위한 KG 기반 RAG', '구축 현황과 LLM 파트 논의'))
add(subtitle('설계한 큰 틀 · 댐 운영 적용 · 근거 묶음 · LLM 파트 논의 사항'))
add(dateline('2026.10.15 자문 회의 · 국민대학교', before=200))

add(H('1. 연구 개요'))
add(para('댐 운영자는 현재의 수문·기상 상태를 보고 방류 등을 판단한다. 이때 과거의 운영행위, 그 방류를 허가한 승인, 현행 운영기준(홍수기 제한수위)이 필요한데, 이 정보는 승인 기록, 측정 시계열, 규정 문서에 나뉘어 있다. LLM 단독 답변은 근거를 확인할 수 없으므로, 흩어진 자료를 지식그래프(KG)로 연결하고, 질문에 필요한 근거를 찾아 LLM에 주어 근거 위에서 답하게 하는 구조(RAG)를 만든다.'))
add(table([['', '질문 (Competency Question)'],
           ['전체 질문', '특정 댐의 현재 수문·기상 상태와 현행 운영기준을 확인하고, 선택된 과거 사례의 상태·운영행위·승인·근거를 함께 추적하여 운영 판단을 지원할 수 있는가?'],
           ['CQ1 · CQ2', '현재 수문·기상 상태 / 과거 시점의 수문·기상 상태'],
           ['CQ3 · CQ4', '과거 운영행위 / 과거 방류 승인과 승인 내용'],
           ['CQ5 · CQ6', '현재 운영기준(홍수기 제한수위) / 위 정보의 공식 근거']], [1700, 8272], sz=S))
add(para('대상은 한강수계 4개 댐(충주·소양강·횡성·광동), 방류 승인 80건(2010~2021), K-water 시간별 수문기상 자료 50.8만 행, 연계운영규정 별표3이다.', sz=19))

add(H('2. 설계한 큰 틀'))
add(image('fig1', os.path.join(FIG, 'meeting_fig1_framework.png'), 1400, 1092, '전체 구조', width=8200))
add(caption('그림 1. 전체 구조 (a) Ontology 설계 (b) KG 구축 (c) 질문 응답'))
add(li('KG 구축의 각 단계는 근거 문헌(DDKG, OntoDSMS, Noy & McGuinness, Li)의 방법에서 원리를 가져왔고, 문헌에 없는 기준은 연구자가 정하지 않았다.', S + 2))
add(li('근거 검색은 정해진 규칙의 코드로 자동화했다. 같은 입력이면 같은 결과가 나오고, 실행된 질의를 확인할 수 있다.', S + 2))
add(li('LLM은 두 곳만 맡는다: 질문 해석(의도·댐·시점 추출)과 답변 생성. 비교·유사 판단은 코드가 아니라 LLM이 하되, 답변에서 근거와 판단을 나누어 표시한다.', S + 2))

add(H('3. 댐 운영에 적용한 KG 설계'))
add(image('fig2', os.path.join(FIG, 'meeting_fig2_kg.png'), 1400, 1064, 'KG 예시', width=7600))
add(caption('그림 2. 충주댐 예시로 본 KG 구조 (Class 6개, Relation 9개)'))
add(table([['자료', 'KG에 들어간 것', 'KG 밖 저장소'],
           ['방류 승인 기록 (80건)', 'Approval 80, Operation 68 (비고 문장에서 규칙으로 추출), 근거자료 80', '-'],
           ['수문기상 시간 자료', '댐 × 변수 상태 개체 24개(stationCode)', '측정자료 저장소: 508,246행'],
           ['연계운영규정 별표3', 'Criterion 3 (충주·소양강·횡성), 근거자료 1', '문서 저장소: 별표3 원문'],
           ['댐 기본 정보', 'Dam 4', '-']], [2400, 4572, 3000], sz=S))
add(para('KG는 개체 %d개, 관계 %d개이고, 값 자체(측정값, 규정 원문)는 넣지 않고 찾아가는 키(stationCode, sourceLocator)만 둔다. 구조 검사 5개 항목을 통과했다. 검증 중 승인에서 댐으로 가는 경로가 없어 승인 80건 중 63건만 댐에서 도달 가능한 문제를 발견하여, Approval–concernsDam–Dam 관계를 추가했다(80건 모두 도달).' % (len(ents), len(rels)), sz=19))

add(H('4. 근거 검색과 근거 묶음'))
add(flow(['① 입력 확인\n의도·댐·시점\n범위 검사', '② KG 조회\n의도별 Cypher\n질의 틀', '③ 저장소 조회\n측정값 · 원문', '④ 근거 묶음\n출처 번호 부착\n원값 그대로'], sz=S))
add(li('의도는 CQ1~CQ6이고, 질문 하나가 여러 CQ를 함께 물을 수 있다. 의도마다 Ontology의 관계 경로를 따라가는 Cypher 질의 틀이 미리 정해져 있고, LLM은 질의를 쓰지 않는다.', S + 2))
add(li('측정값은 시각으로 조회한다. 운영 시각이 정각이면 그 시각 1행, 아니면 앞뒤 정시 2행을 그대로 준다(보간·반올림 없음).', S + 2))
add(li('근거 묶음에는 계산한 값을 넣지 않는다. 차이, 유사 여부 같은 해석은 LLM의 몫이다.', S + 2))
add(para('예시 질문: “충주댐 현재 수문, 기상 데이터를 가져오고 제한수위와 비교한 후에, 이와 비슷한 수문상태일 때의 승인 및 운영 행위가 있었으면 알려줘.”   →   LLM이 넘기는 값', sz=19))
add(code('{"intent": ["CQ1", "CQ5", "CQ2", "CQ3", "CQ4", "CQ6"], "dam": "충주댐", "period": "전체"}', sz=16))
add(para('근거 묶음 (발췌, 운영행위 14개 중 일부):', sz=19))
add(code('[근거 1. 현재 상태] (CQ1)  저장된 가장 최근 시각이며 실시간이 아님\n'
         '[MEA:1003110:2026092823] 2026-09-28 23:00  수위 131.6689 EL.m, 유입량 14.402 CMS, 총방류량 0.43 CMS, 저수율 54.2 % …\n'
         '[근거 2. 운영기준] (CQ5)   [CRI:CR-02] 충주댐 홍수기 제한수위: 138.0 EL.m   [EVI:LAW:별표3] 원문 …\n'
         '[근거 3. 운영행위와 허가한 승인] (CQ3)\n'
         '[OPR:1368:1] 탄력적 방류, 시각 2012-08-24 15:00 ← 승인 [APR:1368]   [OPR:3412:1] 방류, 시각 2020-08-02 18:00 ← 승인 [APR:3412] …\n'
         '[근거 4. 운영 시각의 상태] (CQ2)\n'
         '[OPR:1368:1] 2012-08-24 15:00\n'
         '  [MEA:1003110:2012082415] 수위 134.17 EL.m, 유입량 1107.905 CMS, 총방류량 692.183 CMS, 저수율 61.7 % …\n'
         '[근거 5. 방류 승인] (CQ4)  [APR:1368] 승인일 2012-08-24: 방류시작 2012-08-24 15:00; 접수방류량 2000㎥/s; 비고: 이내 탄력적 조정 …\n'
         '[근거 6. 출처] (CQ6)  [EVI:AP:1368] 환경부 한강홍수통제소 홍수예보 댐방류승인, 위치: 순차번호 1368 ← [OPR:1368:1], [APR:1368] …\n'
         '[근거 사용 원칙] 1. 근거에 있는 내용만 사실로 쓰고 문장마다 출처 번호를 붙인다. 2. 비교·해석은 LLM의 판단임을 밝히고 어느 근거에서 나온 판단인지 적는다. 3. 근거에 없으면 “자료에 없음”이라고 답한다.', sz=14))
add(para('묶음의 길이는 댐마다 다르다 (전체 질문 기준, 별표3 원문 포함): %s.' % ', '.join('%s 약 %s자(운영행위 %d개, 승인 %d건)' % (k, format(round(v['chars'], -2), ','), v['ops'], v['apps']) for k, v in SZ.items()), sz=19))
add(para('답변 형식 (예시, 형식 설명용이며 모델 평가 결과가 아님)', sz=19))
add(code('[근거] 현재 수위 131.6689 EL.m [MEA:1003110:2026092823], 제한수위 138.0 EL.m [CRI:CR-02]. 2020-09-03 12:00 방류 [OPR:3771:1], 당시 수위 129.69 EL.m, 유입량 1472.336 CMS [MEA:1003110:2020090312] …\n'
         '[판단 (LLM)] 현재 수위는 제한수위보다 6.3311 m 낮다. (근거: [MEA:1003110:2026092823], [CRI:CR-02])\n'
         '수위만 보면 2020-09-03 12:00 사례가 가장 가깝지만 당시 유입량·총방류량이 현재보다 훨씬 커서 비슷한 상태로 보기 어렵다. (근거: [MEA:1003110:2020090312], [MEA:1003110:2026092823])', sz=14))

add(H('5. LLM 파트에서 논의하고 싶은 사항'))
add(para('구조와 근거 검색은 구현했고, LLM이 맡는 두 곳(질문 해석, 답변 생성)의 설계가 남아 있다. 새 구조에서의 실제 모델 실행은 서버 환경 문제로 아직 하지 못했고(이전 구조에서는 Qwen3-8B로 실행해 본 경험이 있음), 아래는 실행 전 설계 단계의 질문이다.', sz=19))
add(table([['주제', '현재 구상', '논의하고 싶은 점'],
           ['1. 질문 해석\n(의도 추출)', '프롬프트로 CQ1~CQ6 중 해당하는 것을 모두 고르고 댐·시점을 JSON으로 출력. 목록 밖 값은 코드가 정규화하거나 거부 (Zhang의 세 가지 통제 중 코드 쪽)', '• 프롬프트·few-shot으로 충분한지, 미세조정이 필요한지\n• 여러 의도가 섞인 질문의 오분류에 어떻게 대응할지(재질문, 보수적으로 전체 조회)'],
           ['2. 근거 묶음의 형식과 길이', '태그와 출처 번호가 붙은 텍스트. 댐에 따라 약 %s~%s자' % (format(round(min(v['chars'] for v in SZ.values()), -2), ','), format(round(max(v['chars'] for v in SZ.values()), -2), ',')), '• 텍스트, 표, JSON 중 어떤 형식이 8B급 모델에 유리한지\n• 길어질 때 전체를 주는 것과 선별·요약의 득실, 근거 순서의 영향'],
           ['3. 근거와 판단의 분리', '근거 사용 원칙 세 문장과 [근거]/[판단] 두 부분의 답변 형식을 프롬프트로 지시', '• 프롬프트만으로 지켜지는지, 구조화 출력(JSON 스키마) 같은 강제 방법이 필요한지\n• 출처 번호가 묶음에 실제로 있는지, 인용한 값이 원값과 같은지를 후처리로 자동 검사할지'],
           ['4. 비교·계산의 신뢰성', '차이, 유사 여부는 LLM이 근거의 원값을 보고 직접 판단. 연구자 지정 기준(거리 계산 등)은 두지 않음', '• 산술 오류와 “비슷하다” 판단을 어떻게 검증할지\n• 계산만 도구 호출(function calling)에 맡기는 방안이 “연구자 판단 배제” 원칙과 양립하는지'],
           ['5. 모델', '로컬에서 Qwen3-8B (vLLM). 한 모델이 질문 해석과 답변 생성을 프롬프트만 바꿔 담당', '• 8B로 충분한지, 32B급과 비교할 가치가 있는지\n• 질문 해석과 답변 생성을 다른 모델로 나눌 필요가 있는지'],
           ['6. 평가', '정답이 하나로 정해지지 않는 질문(“비슷한 상태”)이 있어 정확도만으로 평가하기 어려움. 후보: 출처 번호 정확도, 값 일치율, 근거 없는 주장 비율, 비교 기준선(KG 없는 RAG, 근거 없는 LLM)', '• 지표 구성과 비교 기준선의 적절성\n• 정답이 없는 판단을 평가하는 방법(전문가 평가 등)과 실제 운영기록 확보 방안']], [1700, 3772, 4500], sz=17))
add(box('우선 정하고 싶은 것 (제안)', '위 6개 중 LLM 파트의 평가 설계(지표와 비교 기준선)를 먼저 정하고 싶습니다. 구조는 이미 구현되어 있으므로 평가 설계가 정해지면 바로 실행할 수 있습니다.', w1=2400, sz=19))

T.save(OUT, ''.join(B), L.IMGS)
print('저장', OUT)
