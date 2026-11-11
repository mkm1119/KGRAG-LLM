#!/usr/bin/env python3
"""랩미팅 자료(docx): 검증 방법 선행연구 조사와 단계별 검증 설계(안).
서식은 11/06 자료(build_labmeeting_how_kg2.py)와 같다(labdoc_lib, 같은 템플릿).
11/06 서버 실행 결과(05_retrieval/server_runs_20261106_tasks82)에서 의도 추출 단계와 최종 결과를 대조한 숫자를 쓴다.
사용: python3 scripts/build_labmeeting_validation.py <출력 docx>
"""
import collections, glob, importlib.util, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('L', os.path.join(HERE, 'labdoc_lib.py')); L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
_li, _para = L.li, L.para
LS = ' w:line="252" w:lineRule="auto"'
L.li = lambda t, sz=19: _li(t, sz).replace('<w:spacing w:after="60"/>', '<w:spacing w:after="40"%s/>' % LS, 1)
L.para = lambda t, sz=19: _para(t, sz).replace('w:after="120"/>', 'w:after="100"%s/>' % LS, 1)
L.cell.__defaults__ = L.cell.__defaults__[:4] + (17,) + L.cell.__defaults__[5:]
L.table.__defaults__ = (True, True, 17, ())
_h1 = L.h1
L.h1 = lambda t, pagebreak=False: _h1(t, False).replace('<w:pStyle w:val="1"/>', '<w:pStyle w:val="1"/><w:spacing w:before="280" w:after="40"/>', 1)
L.label = lambda t: '<w:p><w:pPr><w:keepNext/><w:spacing w:before="140" w:after="20"/><w:rPr>%s</w:rPr></w:pPr>%s</w:p>' % (L.LANG, L.run(t, sz=22, b=True, color='1F4E79'))
for n in ('title', 'subtitle', 'dateline', 'label', 'h1', 'h2', 'para', 'li', 'spacer', 'table'):
    globals()[n] = getattr(L, n)

ROOT = os.path.join(HERE, '..'); R5 = os.path.join(ROOT, '05_retrieval')
LAB = os.path.join(ROOT, '..', 'lab_meeting')
OUT = sys.argv[1]
T = L.Template(os.path.join(LAB, '랩미팅 자료_KG구축_검색답변_최종.docx'))

# ------------------------------------------------------------------ 사실: 11/06 실행에서 의도 추출 단계와 최종 결과 대조
QS = {q['id']: q for q in json.load(open(os.path.join(R5, 'question_set_tasks82.json'), encoding='utf-8'))}
src = open(os.path.join(R5, 'tasks82_llm_review.py'), encoding='utf-8').read()
LAB_L = eval(src[src.find('L = {') + 4:src.find('\n}\n') + 2])        # 사람이 답변까지 읽고 나눈 결과(①~④)
RUN = [json.load(open(f, encoding='utf-8')) for f in sorted(glob.glob(os.path.join(R5, 'server_runs_20261106_tasks82', 'q*.json')))]
assert len(RUN) == 82
NOW = [r for r in RUN if r['expect'] == 'answer_now']
assert len(NOW) == 13
OK_FINAL = [r['id'] for r in NOW if LAB_L[r['id']][0] == 1]
OK_INTENT = [r['id'] for r in NOW if r['intent_match']]
assert len(OK_FINAL) == 8 and len(OK_INTENT) == 5
FINAL_OK_INTENT_X = sorted(set(OK_FINAL) - set(OK_INTENT))
INTENT_OK_FINAL_X = sorted(set(OK_INTENT) - set(OK_FINAL))
assert FINAL_OK_INTENT_X == ['q029', 'q038', 'q044', 'q092'] and INTENT_OK_FINAL_X == ['q028']
assert LAB_L['q039'][0] == 3 and not next(r for r in NOW if r['id'] == 'q039')['intent_match']
REFUSE = sum(1 for q in QS.values() if q['expect'] == 'refuse')
assert REFUSE == 33

B = []
add = B.append


def lis(*items):
    for t in items:
        add(li(t))


rtable = lambda rows, widths: table(rows, widths, header=True, firstcol=False)

# ================================================================== 표지
add(title('검증 방법 선행연구 조사', '그래프 기반 질의응답의 단계별 검증'))
add(subtitle('선행연구의 검증 방법과 우리 파이프라인에 적용할 검증(안)'))
add(dateline('2026.11 · 문경민'))

# ================================================================== 1
add(h1('1. 검증을 다시 보는 이유'))
lis('11/06 자료에서 82개 질문을 실제 파이프라인(의도 추출 → KG 검색 → 근거 묶음 → 답변)으로 돌리고, 사람이 답변까지 읽어 결과(①~④)와 한계(A~G)로 나눴다.',
    '이 분류는 최종 답변을 보고 한 것이다. 같은 결과를 의도 추출 단계의 정답(gold)과 대조하면 표 1과 같다.')
add(label('표 1. 지금 답해야 하는 질문 13개: 최종 결과와 의도 추출 단계 정답 일치'))
add(rtable([['구분', '질문 수', '질문'],
            ['최종 결과 ① (근거로 맞게 답함)', str(len(OK_FINAL)), ', '.join(OK_FINAL)],
            ['의도 추출 단계가 정답과 일치', str(len(OK_INTENT)), ', '.join(OK_INTENT)],
            ['최종은 ①인데 의도 추출은 정답과 다름', str(len(FINAL_OK_INTENT_X)), ', '.join(FINAL_OK_INTENT_X) + ' (CQ를 더 넣거나 빼거나, 대상 값을 추가로 냄)'],
            ['의도 추출은 정답인데 최종은 ①이 아님', str(len(INTENT_OK_FINAL_X)), 'q028 (KG의 별표3에 광동댐이 없어 "자료에 없음")'],
            ['의도 추출이 틀려 최종이 틀린 답', '1', 'q039 ("2017년 8월"을 8월 1일 하루로 읽어 "방류 기록 없음")']],
           [3600, 1100, 5272]))
lis('최종 답변만 채점하면 q029, q038, q044, q092는 맞은 것으로만 보이고, 의도 추출 단계의 차이는 드러나지 않는다.',
    'q039는 답변만 보면 그럴듯한 "기록 없음"이다. 원인이 기간 값 추출(1단계)에 있다는 것은 단계별로 봐야 알 수 있다. q028은 의도와 검색은 맞고 원인이 KG의 범위에 있다.',
    '→ 어느 단계에서 틀렸는지 알아야 고칠 곳을 정할 수 있다. 선행연구가 검증을 어떻게 했는지 조사하고, 우리 파이프라인의 단계별 검증을 설계한다.')

# ================================================================== 2
add(h1('2. 조사 방법'))
lis('출발 논문: 검증을 주제로 한 최근 논문 3편.',
    '  · GRADES (Draetta 외, 2025): 그래프 기반 질의응답의 단계별 평가 프레임워크, RAGE-KG 2025(ISWC 워크숍)',
    '  · HERMES (Nuñez 외, 2026): GraphRAG 답변이 그래프 근거를 따르는지 검증, RAGE-KG 2026(ISWC 워크숍)',
    '  · Yu 외(2024): RAG 평가 서베이(검색과 생성 구성요소별 지표·벤치마크 정리)',
    '거슬러 올라가기(backward snowballing): 출발 논문의 참고문헌 중 평가·검증을 다룬 문헌을 모으고, 그 문헌의 참고문헌으로 다시 거슬러 올라간다. 이번 자료는 1차(출발 논문의 참고문헌)까지이다.',
    '우리 분야(댐·수자원)는 따로 검색해 검증 방법을 확인했다.',
    '분류 기준: 무엇을 검증하나(파이프라인 단계) × 어떻게 검증하나(정답 비교 / 자동 지표 / LLM 판정 / 사람·전문가).')

# ================================================================== 3
add(h1('3. 조사 결과'))
add(h2('3.1 댐·수자원 분야 연구의 검증'))
add(label('표 2. 댐·수자원 분야 KG·LLM 연구가 한 검증'))
add(rtable([['연구', '만든 것', '검증 방법', '단계별 검증'],
            ['저수지 조도 규칙 KG (2023, 중국)', '조도 규칙 KG와 추론 경로', '삼협댐에 적용해 그래프를 보임', '없음'],
            ['Baudrit 외 (2022)', '댐 시스템 그래프 지식 모델', '개념 증명(proof of concept)', '확인 못 함'],
            ['Zhou 외 (2023), OntoDSMS', '댐 안전 모니터링 온톨로지', '관계형 DB와 검색 시간 비교, 사례 질의', '없음'],
            ['Huang 외 (2026), DDKG', 'LLM으로 댐 결함 KG 구축', '개체 인식 지표(모두 90% 이상), 전문가 검증 모듈', '추출 단계만'],
            ['HydroLLM-Benchmark (2025)', '수문학 LLM 벤치마크', '문항 정답률, 서술형은 코사인 유사도', '없음(LLM 단독)'],
            ['WaterGPT (EvalWater)', '수자원 도메인 LLM', '약 1만 문항 정답률', '없음(LLM 단독)'],
            ['Hosseini 외 (수자원 LLM 비교)', '범용 LLM 3종 비교', '리뷰 논문의 답을 기준으로 관련성·정확성 등 평가', '없음(LLM 단독)'],
            ['수리 KG 제약 RAG (중국)', 'KG 제약을 더한 벡터 검색 RAG', '전문 질의응답 정확도 91.5%', '없음(최종 정답률)']],
           [2700, 2500, 3272, 1500]))
lis('조사한 범위에서 댐·수자원 연구의 검증은 사례 적용, 추출 단계 지표, 최종 정답률이었다. 질의응답 파이프라인을 단계별로 검증하거나, 범위 밖 질문의 거절을 검증한 연구는 찾지 못했다.')

add(h2('3.2 그래프 RAG·RAG 평가 연구: 단계별로 정리'))
add(label('표 3. 단계별로 검증할 것과 선행연구의 방법'))
add(rtable([['단계', '검증할 것', '방법', '문헌'],
            ['질문 이해 (정보 추출)', '질문에서 뽑은 엔티티·유형이 맞는지', '전문가가 만든 정답과 비교해 정밀도·재현율·F1', 'GRADES'],
            ['검색 (엔티티 연결·조회)', '가져온 엔티티·근거가 질문에 맞는지', '전문가가 상위 10개의 관련성 판단 → 평균 정밀도', 'GRADES'],
            ['', '', '맥락 관련성을 LLM이 판정', 'RAGAS, ARES'],
            ['', '', '검색 지표(정밀도, 재현율, 순위 지표) 정리', 'Yu 외(2024)'],
            ['답변의 근거 충실성', '답의 내용이 가져온 근거에 있는지', '답을 원자 주장으로 쪼개 근거 트리플과 하나씩 대조', 'HERMES'],
            ['', '', 'LLM이 주장별로 근거에서 확인되는지 판정', 'RAGAS'],
            ['', '', '작은 LM 판정기 + 소량의 사람 주석으로 보정', 'ARES'],
            ['답변 문장의 오류', '틀린 내용, 확인 불가, 오해 소지', '오류 분류표로 수작업 분류', 'Kasner·Dušek(2024), GRADES'],
            ['거절', '근거에 답이 없을 때 거절하는지', '답이 없는 문서만 줬을 때의 거절률', 'RGB (Chen 외, 2024)'],
            ['사람·전문가', '질문 세트의 타당성, 출력의 쓸모', '전문가가 질문을 검토하고 출력의 적합성 판단', 'GRADES'],
            ['', '', '크라우드소싱 판정', 'Gienapp 외(2025)'],
            ['', 'KG 자체의 정확성', 'LLM 판정과 사람 확인을 결합한 KG 검증', 'Tsaneva 외(2025)'],
            ['온톨로지', 'CQ를 다 답하는지, 구조 품질', 'CQ 충족 여부, 평가 분류(정답 비교·코퍼스·과업·기준)', 'FOCA, Raad·Cruz(2015), McDaniel·Storey(2019)']],
           [1900, 2300, 3672, 2100]))
lis('평가 지표 자체의 한계도 보고되었다: 자동 지표는 사람 판단과 상관이 낮고(Novikova 외, 2017), LLM 판정은 사람의 관련성 판정을 대체하지 못한다(Clarke·Dietz, 2024).',
    'GRADES는 LLM의 한계를 보완하려는 파이프라인을 LLM으로만 평가하면 자기강화 고리에 빠질 위험이 있다고 보고, 중간 단계 평가와 최종 출력의 사람 평가를 함께 둘 것을 제안했다.',
    'RAG 평가를 실험 설계부터 정리한 방법론도 있다(Simon 외, 2024).')

add(h2('3.3 조사에서 확인한 것'))
lis('최근 연구는 최종 출력만이 아니라 파이프라인 구성요소별로 평가한다(GRADES, ARES, Yu 외).',
    '자동 지표나 LLM 판정만으로 평가하지 않고 사람·전문가 평가를 함께 둔다(GRADES, ARES, Gienapp 외).',
    '거절은 RGB에서 별도의 능력(negative rejection)으로 측정한다. 그래프 기반 질의응답에서 범위 밖 질문의 거절을 평가한 연구는 이번 조사에서 찾지 못했다.')

# ================================================================== 4
add(h1('4. 우리 파이프라인의 단계별 검증(안)'))
add(label('표 4. 단계별 검증할 것, 기준, 참고한 방법, 지금 있는 것'))
add(rtable([['단계', '검증할 것', '기준·지표', '참고', '지금 있는 것'],
            ['⓪ 온톨로지·KG', 'CQ마다 답을 돌려주는지, KG 값이 원자료와 같은지', 'CQ 충족 여부, 표본 대조 일치율', 'FOCA, Tsaneva 외', 'CQ 5개, Entity 264·Relation 418'],
            ['① 의도 추출', '의도·댐·기간·대상이 정답과 같은지', '항목별 일치율, 오류 유형(한계 A·B)', 'GRADES', 'intent_match (지금 답할 13개 중 5개 일치)'],
            ['② KG 검색', '필요한 행과 근거를 다 가져왔는지', '정답 의도로 실행한 결과와 비교한 재현율·정밀도', 'GRADES, Yu 외', '정답 의도 실행(gold 모드)'],
            ['③ 근거 묶음', '모델 한도 안인지, 답에 필요한 근거가 들어갔는지', '글자 수, 필요한 근거 포함률(한계 C)', 'RAGAS', '근거 묶음 글자 수 기록'],
            ['④ 답변', '근거에 있는 내용만 말하는지, 다른 값으로 대신하지 않는지, 출처 표기', '주장 단위 대조, 오류 분류(한계 D·E·G)', 'HERMES, RAGAS, Kasner·Dušek', '결과 ①~④ 수작업 분류'],
            ['⑤ 거절', '범위 밖·자료 없는 질문을 거절하는지, 거절 이유가 맞는지', '거절해야 할 %d개 질문의 거절률, 이유 일치(한계 F)' % REFUSE, 'RGB', '기대 동작(거절) 표시된 질문 세트'],
            ['⑥ 실무자', '질문 세트가 실제 업무에 맞는지, 답이 쓸모 있는지', '실무자 검토 의견', 'GRADES', '82개 태스크 실무자 검토 요청 예정']],
           [1500, 2600, 2400, 1572, 1900]))
lis('①~③은 정답을 정해 두면 자동으로 계산할 수 있다. ④~⑥은 사람 판정이 필요하며, LLM 판정을 쓰더라도 일부를 사람이 확인해 보정한다(ARES의 방식).',
    '①·②의 정답은 지금 답할 13개 질문에 이미 있다(question_set_tasks82.json의 gold). 확장해야 할 36개는 확장 후 정답을 만든다.')

# ================================================================== 5
add(h1('5. 다음 할 일'))
lis('조사 계속: 출발 논문 참고문헌의 참고문헌(2차)과, 출발 논문을 인용한 최근 논문(앞으로 따라가기)으로 단계별 20편 이상을 모아 비교표를 만든다.',
    '단계별 정답 정리: 82개 질문의 의도 정답과 검색 정답(가져와야 할 행·근거)을 정리한다.',
    '단계별 지표 계산: 11/06 실행 결과에 ①~③ 지표를 계산해 한계 A~G가 어느 단계에서 생기는지 숫자로 확인한다.')

# ================================================================== 참고문헌
add(h1('부록. 참고문헌'))
lis('Chen, J., Lin, H., Han, X., & Sun, L. (2024). Benchmarking large language models in retrieval-augmented generation. AAAI 2024, 38, 17754–17762.',
    'Clarke, C. L., & Dietz, L. (2024). LLM-based relevance assessment still can\'t replace human relevance assessment. arXiv:2412.17156.',
    'Draetta, L., Stranisci, M. A., Corallo, F., Balestrucci, P. F., Oliverio, M., Damiano, R., & Mazzei, A. (2025). Beyond the Metrics: an Investigation into the Reliability of Evaluation Metrics for Domain Specific Graph-based Question Answering. RAGE-KG 2025, CEUR-WS Vol-4079.',
    'Es, S., James, J., Espinosa Anke, L., & Schockaert, S. (2024). RAGAs: Automated evaluation of retrieval augmented generation. EACL 2024 (System Demonstrations).',
    'Gienapp, L., Hagen, T., Fröbe, M., Hagen, M., Stein, B., Potthast, M., & Scells, H. (2025). The viability of crowdsourcing for RAG evaluation. arXiv:2504.15689.',
    'Huang, J., Hou, W., Zhang, S., Du, Z., & Yin, J. (2026). Dam defects ontology and knowledge graph construction from multi-source hazard data using large language models. Advanced Engineering Informatics, 76, 104987.',
    'Kasner, Z., & Dušek, O. (2024). Beyond traditional benchmarks: Analyzing behaviors of open LLMs on data-to-text generation. ACL 2024.',
    'McDaniel, M., & Storey, V. C. (2019). Evaluating domain ontologies: Clarification, classification, and challenges. ACM Computing Surveys, 52(4), 70.',
    'Novikova, J., Dušek, O., Cercas Curry, A., & Rieser, V. (2017). Why we need new evaluation metrics for NLG. EMNLP 2017.',
    'Nuñez, G., Zárate, M., & Fillottrani, P. R. (2026). HERMES: Grounding Fidelity Evaluation in GraphRAG-Based Marine Knowledge Graphs Across LLM Configurations. RAGE-KG 2026, CEUR-WS Vol-4312.',
    'Raad, J., & Cruz, C. (2015). A survey on ontology evaluation methods. KEOD 2015.',
    'Saad-Falcon, J., Khattab, O., Potts, C., & Zaharia, M. (2024). ARES: An automated evaluation framework for retrieval-augmented generation systems. NAACL 2024.',
    'Simon, S., Mailach, A., Dorn, J., & Siegmund, N. (2024). A methodology for evaluating RAG systems: A case study on configuration dependency validation. arXiv:2410.08801.',
    'Tsaneva, S., Dessì, D., Osborne, F., & Sabou, M. (2025). Knowledge graph validation by integrating LLMs and human-in-the-loop. Information Processing & Management, 62, 104145.',
    'Yu, H., Gan, A., Zhang, K., Tong, S., Liu, Q., & Liu, Z. (2024). Evaluation of retrieval-augmented generation: A survey. CCF Conference on Big Data, 102–120.',
    'Zhou, Y., Bao, T., Shu, X., Li, Y., & Li, Y. (2023). BIM and ontology-based knowledge management for dam safety monitoring. Automation in Construction, 145, 104649.',
    '그 밖에 표 2의 수자원 분야 연구(저수지 조도 규칙 KG, Baudrit 외 2022, HydroLLM-Benchmark, WaterGPT, Hosseini 외, 수리 KG 제약 RAG)와 FOCA(Bandeira 외)는 서지 정보를 원문으로 확인한 뒤 채운다.')

T.save(OUT, ''.join(B), L.IMGS, page_numbers=True)
print('saved', OUT)
