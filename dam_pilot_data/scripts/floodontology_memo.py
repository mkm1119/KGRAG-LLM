#!/usr/bin/env python3
"""Li 외(2025) 홍수 온톨로지 논문의 리뷰 메모를 JSON으로 쓴다. 사용: python3 floodontology_memo.py <출력.json> [<정리.md>]
형식: {"쪽": [{"lead": "#메모 제목", "ko": "- 항목…", "anchors": ["S:원문 문장의 첫머리", ...]}]}  (build_paper_review_pdf.py memo2)"""
import json, sys

M = {}


def N(page, title, body, *anchors):
    M.setdefault(str(page), []).append({'lead': '#' + title, 'ko': body, 'anchors': ['S:' + a for a in anchors]})


N(1, '연구 목적',
  '- 홍수 위험 소통 메시지는 너무 일반적이고 실행할 안내가 없어 무시된다\n- 목적 1: 새로운 반자동 방식으로 홍수 온톨로지를 만든다\n- 목적 2: 그 온톨로지가 복잡한 자료를 명확하고 개인에 맞춘 경보로 옮기는 기반이 됨을 보인다\n- 방법: 전문가가 정의한 스키마 + LLM의 확장 + 권위 있는 출처로부터의 정제 (사람이 개입)',
  'This research aims to enhance flood risk', 'We introduce a semi-automated, human-in-the-loop')
N(1, '결과 요약 (초록)',
  '- (1) 기술 지표: 기존 재난 온톨로지보다 관계 풍부도와 표현력이 높다\n- (2) 사례 연구: 일반 경보를 대상에 맞춘 실행 가능한 메시지로 바꿀 수 있음을 보인다\n- 기여: 재현 가능하고 다른 분야에 쓸 수 있는 반자동 구축 방법론, 그리고 실제 시연',
  'Evaluation results are twofold', 'Consequently, this research delivers two key contributions')
N(1, '연구 배경',
  '- 돌발 홍수가 잦아지고 강해지며 취약 지역사회에 더 큰 영향을 준다\n- 대중 경보는 기술 용어가 많고 구체적 안내가 없다\n- 근본 원인: 홍수 정보가 기관마다 조각나 있고 용어가 맞지 않는다',
  'However, flood risk communication often fails', 'Public alerts are frequently too generic', 'This communication failure stems from')

N(2, '기존 연구의 한계 (두 가지)',
  '- 한계 1: 기존 홍수·재난 온톨로지는 전문가의 자료 통합용이라, 대중을 향한 소통에 필요한 세밀한 개념이 없다 (예: OFPO)\n- 한계 2: 구축이 느린 수작업이거나, LLM 완전 자동이라 의미 표류와 환각에 취약하다\n- 그래서 필요한 것: 사람의 전문성과 AI를 합친 반자동 파이프라인, 그리고 소통용으로 설계되고 시연된 온톨로지',
  'First, many existing models', 'Second, their construction often relies', 'Together, these findings reveal')
N(2, '연구 방법의 개요',
  '- 1부 온톨로지 구축: 전문가가 범위 정의 → LLM이 씨앗 온톨로지로 확장 → CQ로 반복 정제·검증 → FEMA·NWS 문서로 보강\n- 2부 적용 시연: NWS의 실제 돌발 홍수 경보를 온톨로지로 분해하고 고쳐 써서 전후를 비교',
  'The first phase focuses on ontology construction', 'It begins with domain experts defining', 'This ontology is then iteratively refined', 'The second phase demonstrates')
N(2, '[우리 연구와의 관계]',
  '- 온톨로지를 CQ로 정제하고 "검증"한다고 명시한 곳이다. 우리 연구의 CQ 70/30 방식의 출처\n- 구축의 출발이 전문가의 범위 정의라는 점은 우리와 같다 (우리는 연구진이 CQ 6개로 범위를 정함)')

N(3, '온톨로지와 지식그래프의 정의',
  '- 온톨로지: 분야의 형식적 어휘와 스키마 (개념과 관계의 정의)\n- 지식그래프: 그 스키마를 구체적 자료로 채운 것\n- Noy의 Ontology Development 101에서 말한 "지식 베이스"를 이 논문은 지식그래프로 해석한다',
  'An ontology specifies the formal vocabulary', 'A knowledge graph, in turn, instantiates', 'In this paper, we interpret the referenced')
N(3, '기존 홍수 온톨로지의 흐름',
  '- 초기: 의미적 상호운용성 (POLARISCO)\n- 최근: 재난 관리 전 주기로 확장, 관측·의사결정 작업 흐름까지 모델링 (OFPO)\n- 공통 한계: 여전히 수작업 설계. AI는 인스턴스 채우기(개체명 인식)에만 쓰이고 온톨로지 설계에는 쓰이지 않았다',
  'Nevertheless, as shown in Table 1', 'Where AI is applied', 'In the critical domain of flooding')

N(5, '형식성과 실용성의 균형',
  '- 표 1의 온톨로지 대부분은 OWL로 구현되어 형식성 점수가 가장 높다(5/5)\n- 그러나 형식성이 높다고 실제 성능이 더 좋은 것은 아니다. 표현력과 적용성 사이의 균형이 필요하다',
  'However, Greater formal rigor')
N(5, '소통에서 온톨로지의 역할',
  '- 기관마다 같은 현상을 다른 이름으로 부른다 (돌발 홍수, 강우성 사건, 지표수 침수)\n- 온톨로지는 정보를 모으고 맥락을 주고 공통 개념을 형식화해 조각남을 해결한다\n- 가장 가까운 선행 연구(Sermet·Demir)는 수작업으로 설계되었고 LLM을 쓰지 않았다',
  'Agencies may label the same phenomenon', 'Ontologies address fragmentation by', 'Their ontology, however, is manually engineered')

N(6, 'LLM을 쓴 온톨로지 구축 연구',
  '- LLM은 대량의 비정형 자료를 빠르게 처리해 온톨로지 공학의 반복 작업을 맡을 수 있다\n- 그러나 대부분의 연구가 여전히 전문가의 입력이나 검증을 필요로 한다 (OntoGenix, Kommineni 외)\n- 환각의 위험 때문에 사람의 감독이 계속 중요하다',
  'In recent years, large language models have begun', 'However, the risk of')
N(6, '사람과 AI의 분업',
  '- AI: 대규모 정보 처리\n- 사람 전문가: 범위 정의, 모호함 해결, 품질 보장',
  'Collectively, these studies suggest')

N(9, '기존 연구의 남은 문제',
  '- LLM은 상위 온톨로지(BFO)에서 벗어나 고립된 "온톨로지 사일로"를 만든다\n- 이 분야는 임시방편의 과업 설계, 일관되지 않은 평가, 낮은 재현성의 문제가 있다\n- 그래서 이 연구는 개념·관계 추출, 구축, 평가까지 사람과 AI가 함께 하는 방식을 택한다',
  'Benson et al. report that large language', 'To address this gap, our methodology adopts')
N(9, '방법론의 기본 생각',
  '- 사람의 전문성이 분야의 개념적 경계를 정한다\n- LLM이 그 경계 안에서 자료를 써서 여러 번 정제한다\n- LLM의 모든 중간 결과에 사람의 검증을 넣어 환각을 막는다',
  'The proposed ontology-engineering strategy follows', 'Nevertheless, human intervention for verification')
N(9, '그림 1: 전체 작업 흐름',
  '- 1단계 전문가의 초기 온톨로지 → 2단계 CQ로 LLM 확장 → 3단계 권위 있는 문서로 스키마 보강 → 4단계 뉴스 기사로 인스턴스 채우기 → (5단계 사례 연구)\n- 본문은 "네 개의 주요 단계"라 하지만 3.5절에 5단계가 있다')

N(10, '1단계: 전문가의 초기 온톨로지',
  '- 사업 요구사항 검토와 이해관계자 면담으로 시작\n- 최상위 클래스 여섯 개: 홍수의 유형, 홍수 단계, 영향, 사회경제적 취약 요인, 환경 맥락, 지역사회 회복력 대책\n- LLM으로 클래스마다 레이블과 설명을 생성 (설명은 뒤에서 임베딩 비교에 쓰임)\n- 이 단계의 결과는 클래스 계층뿐이고 속성은 아직 없다',
  'At the end of Stage 1, the ontology primarily consisted', 'LLMs were then utilized to generate')
N(10, '2단계: CQ 생성과 70/30 분할',
  '- 씨앗 온톨로지를 맥락으로 주고 GPT-4o로 CQ를 생성\n- 사람이 검토하여 품질이 높은 40개만 남김\n- 70%는 온톨로지 확장에, 30%는 최종 온톨로지 평가에만 쓰도록 분리\n- 원문에 "51개의 그룹으로 나눴다"고 되어 있으나 뜻이 불분명하다. 뒤의 평가에서 시험용은 12개(40의 30%)다',
  'Using the seed ontology as the foundational context', 'Following this automated generation', 'To facilitate subsequent')
N(10, '[우리 연구와의 관계]',
  '- 우리 계획의 70/30 분할이 이 문단에서 왔다\n- 차이 1: 이 논문의 CQ는 LLM이 만들고 연구진이 고른 것이다. 실무자가 만들거나 검토한 것이 아니다\n- 차이 2: 어떤 기준으로 40개를 골랐는지, 70과 30을 어떻게 나눴는지(무작위인지)는 적혀 있지 않다')
N(10, '2단계: CQ에서 개체 추출과 중복 제거',
  '- 70%의 CQ에서 GPT-4o(온도 0.1)로 클래스와 관계를 추출\n- 검증 1: 임베딩(text-embedding-3-large)으로 기존 개체 설명과의 코사인 유사도를 계산해 0.7 넘는 후보를 제거\n- 0.7은 실험으로 정한 값',
  'The 70% group of CQs was used', 'First, an automated filtering process')

N(11, '2단계: 사람 검토와 계층 배치',
  '- 검증 2: 남은 후보를 사람이 검토해 개념의 세밀함을 조정 (침수 경보 시스템 → 경보 시스템으로 통합)\n- LLM이 새 클래스의 계층상 위치와 관계를 제안하고, 사람 전문가가 논리적 일관성과 정의역·치역을 최종 검토\n- 결과: 1단계의 분류 체계가 관계로 이어진 T-Box가 됨',
  'Second, the remaining candidates underwent', 'Once the set of new entities was validated', 'These structural suggestions underwent')
N(11, '3단계: 권위 있는 문서로 스키마 보강',
  '- 자료 두 범주: 연방 권고 문서(FEMA, 국토안보부), 웹에서 모은 뉴스 기사\n- PDF를 마크다운으로 바꾼 뒤, LLM이 분야 지식이 있는 문장을 찾아 최상위 클래스에서 하위 클래스로 내려가며 분류\n- 뉴스 기사의 지식은 인스턴스로, 연방 문서의 지식은 개념과 인스턴스로 나눔\n- 개념 통합 4단계: 임베딩으로 중복 제거 → LLM이 클래스 배정 → 온톨로지에 삽입 → 사람 전문가 검토·승인',
  'The first category included federal', 'The second category comprised', 'The conceptual knowledge was integrated')
N(11, '거부된 후보의 비율',
  '- 이 단계에서 개체 후보의 약 8%, 관계 후보의 약 10%가 거부됨\n- 거부 사유 세 범주: 환각, 모호함, 의미 표류 (표 3)',
  'This hybrid process proved to be highly selective')

N(12, '표 3: 거부된 후보의 예',
  '- 환각/논리 오류: 나이 → 성별 → 인종을 상하위로 이은 계층, 해안 홍수의 하위 클래스로 통계 지표(1% 홍수위)를 둔 것\n- 모호함: 거의 같은 이름의 Community가 온톨로지의 두 곳에 생김\n- 의미 표류: 너무 넓은 "지리", 너무 특수한 "코나 폭풍"\n- LLM이 틀리는 방식을 구체적으로 보여 준다. 우리가 온톨로지를 확장할 때 사람이 확인할 항목의 참고가 된다')
N(12, '4단계: 인스턴스 채우기 (KG)',
  '- 이 논문의 초점은 스키마 구축이고, KG는 실용성을 보이기 위한 표본이다\n- 뉴스 기사에서 LLM이 개체를 뽑아 온톨로지의 하위 클래스로 점점 깊이 분류',
  'Although the primary focus of this paper is the construction')

N(13, '4단계: 관계 추론과 적재',
  '- 분류된 개체를 LLM 필터로 다시 정제\n- 다른 LLM이 온톨로지가 허용한 관계 안에서 개체 사이의 관계를 추론\n- 두 클래스 사이에 관계가 정의되어 있다고 그 클래스의 모든 개체 사이에 관계가 성립하는 것은 아니다. 맥락상의 증거가 충분할 때만 관계를 만든다\n- Neo4j에 적재',
  'Subsequently, another LLM agent', 'Thus, the existence of a valid ontological relationship', 'A relationship is created in the knowledge graph')
N(13, '[우리 연구와의 관계]',
  '- 온톨로지를 기준으로 LLM이 비정형 자료에서 개체와 관계를 뽑아 넣는 방식이다. 우리가 확장 후에 택하려는 온톨로지 기반 방식과 같다\n- 다만 이 논문은 이렇게 만든 KG를 검증하지 않았다. 뽑은 개체와 관계가 맞는지에 대한 평가가 없다')

N(14, '5단계: 사례 연구',
  '- 실제 NWS 돌발 홍수 경보(테네시주 두 카운티)를 기준 메시지로 삼음\n- 기준 메시지의 문제 넷: 지리적 구체성 부족, 모호한 영향 평가, 일반적인 행동 촉구, 취약 계층 미고려\n- 온톨로지의 개체와 트리플로 네 문제를 각각 해결\n- 완전 자동 시스템이 아니라 개념 증명이다',
  'We selected an authentic Flash Flood Warning', 'First, it suffers from a lack of geographic specificity', 'This process is not a fully')

N(16, '방법론의 일반화',
  '- 네 단계 작업 흐름은 수문학에 특화된 것이 아니어서 다른 재난(산불, 지진, 보건)에도 쓸 수 있다고 주장\n- 다른 분야에 쓰려면 단계마다 입력(권위 있는 출처, 핵심 개념)을 바꾼다\n- 실제로 다른 분야에 적용해 보인 것은 아니다',
  'Applying this methodology to a different disaster requires')
N(16, '평가의 구성',
  '- 평가 1: OntoQA 지표로 스키마의 구조 품질 (RR, IR)\n- 평가 2: 남겨 둔 30%의 CQ로 개념 범위 점검\n- 평가 2의 논리: 온톨로지가 이 질문들의 개념을 표현할 수 있으면, 자료를 채웠을 때 질의 응답을 지원할 수 있다',
  'First, we assessed the schema', 'Second, to examine the comprehensiveness', 'This evaluation involved applying the remaining 30%', 'If the ontology could successfully')
N(16, '구조 지표의 정의',
  '- RR(관계 풍부도) = 객체 속성 수 / (객체 속성 수 + 하위 클래스 관계 수)\n- IR(상속 풍부도) = 하위 클래스 관계 수 / 클래스 수\n- 원문은 "세 가지 지표"라 하지만 든 것은 RR과 IR 둘이다 (셋째는 공리 수로 보인다)',
  'RR measures the', 'Inheritance Richness (IR) evaluates')

N(17, '구조 평가 결과 (표 4)',
  '- RR = 0.58로 FDSO(0.16), DMDO(0.01), OntoCity(0.18)보다 높다\n- 공리 3754개, 클래스 350개, 객체 속성 473개\n- IR = 1로 계층이 비교적 평평하다고 해석\n- 표 4의 IR 값은 정의와 맞지 않는 곳이 있다. 정의대로 계산하면 FDSO는 607/403 = 1.5, DMDO는 1001/366 = 2.7인데 표에는 둘 다 1이다. 또 IR = 1인 자기 온톨로지를 IR = 0.81인 OntoCity보다 평평하다고 해석한다',
  'Utilizing LLMs for ontology construction', 'However, despite having a substantial class count')
N(17, '개념 범위 평가의 방법',
  '- 묻는 것: CQ에 있는 개념이 온톨로지의 개념으로 포괄되는가\n- 낱말이 정확히 같은지만 보면 뜻이 비슷하고 철자가 다른 개념을 놓친다\n- 그래서 임베딩(text-embedding-3-large)의 코사인 유사도로 비교\n- 평가는 온톨로지를 만들 때 쓰지 않은 CQ 시험 집합으로 한다',
  'Concept coverage is a descriptive measure', 'However, this approach would', 'The evaluation is conducted on a CQ test set')
N(17, '[우리 연구와의 관계]',
  '- 이 평가는 CQ에 "답이 나오는지"를 보는 것이 아니다. CQ의 개념이 온톨로지에 "있는지"를 본다\n- 지난주 자료에서 정한 우리 방식(30%의 CQ마다 필요한 개념을 적고 온톨로지에 있는지 확인)과 같은 종류의 검증이다\n- 차이: 이 논문은 개념 추출을 LLM이, 대조를 임베딩 유사도가 한다. 우리는 CQ가 적어 사람이 직접 대조할 수 있다')
N(17, 'CQ에서 개념 추출',
  '- LLM이 CQ마다 핵심 개념을 3~7개 추출 (프롬프트는 그림 6)\n- 질문에 직접 적히지 않은 상위 개념도 가끔 추출됨 (예: "홍수 관리"). 이롭지만 관련 없는 개념이 나올 위험도 있다',
  'The first step involves extracting concepts', 'Interestingly, we found that the model occasionally')

N(18, '추출한 개념의 사람 검증',
  '- 평가자 3명이 CQ 12개에서 추출된 개념 56개를 "좋음/나쁨"으로 평가하고 빠진 개념을 제안\n- 평가자는 이 온톨로지 구축에 참여한 사람들이다. 독립된 평가자가 아니다',
  'To ensure the LLM concept extraction achieved good coverage', 'The quiz presented each evaluator')

N(19, '사람 검증의 결과',
  '- 3명 중 2명 이상이 승인한 개념만 남김 (다수결)\n- 승인율 93.5%, 평균 품질 평점 4.5/5\n- 개념 56개 → 66개 (2개 제거, 12개 추가)',
  'The results were processed using a majority voting system', 'This validation process demonstrated', 'The human validation resulted in a refined concept set')
N(19, '유형 1 비교: CQ 개념 대 온톨로지 레이블',
  '- CQ 개념과 온톨로지 레이블을 각각 임베딩해 코사인 유사도를 잼\n- 알맞은 임계값을 알 수 없어 여러 임계값에서 결과를 비교\n- 예: "communities", "Community", "community"가 같은 개념인데 유사도가 다르게 나온다. 같은 개념이 온톨로지의 깊이 1과 2에 중복되어 있음도 드러난다',
  'We then measure the distance between each CQ', 'Because we are uncertain about the optimal', 'While we intuitively recognize', 'This example also highlights the need')

N(20, '유형 2 비교: CQ 개념 대 온톨로지 설명',
  '- 한 낱말만 임베딩하면 맥락이 사라진다 (동형이의어 "bank"의 예)\n- 그래서 온톨로지 레이블의 설명을 임베딩해 CQ 개념과 비교',
  'A significant issue with embedding single-word concepts', 'To combat this, we embed the ontology label')

N(21, '유형 3, 4 비교',
  '- 유형 3: CQ 개념 대 "레이블: 설명"\n- 유형 4: CQ 질문 전체 대 "레이블: 설명" (개념 추출 단계를 건너뜀)\n- 그림 13, 14의 제목은 본문·표 6의 정의와 맞지 않는다',
  'We also embed the ontology label along with its description', 'In Figure 14, we embed the question')

N(23, '표 6: 임계값별 범위',
  '- 시험 질문 12개, 개념 66개\n- 임계값 0.3: 네 유형 모두 100%\n- 임계값 0.5: 유형 1 92.4%, 유형 2 62.1%, 유형 3 59.1%, 유형 4 100% (평균 78.4%)\n- 임계값 0.6: 75.8%, 36.4%, 31.8%, 25.0%\n- 임계값 0.7: 유형 1 45.5%, 나머지는 한 자릿수 이하\n- 임계값을 어디에 두느냐에 따라 결과가 100%에서 0%까지 달라진다',
  'At the lowest cutoff', 'The most significant divergence occurs', 'However, raising the threshold incrementally')
N(23, '분석: 임계값의 선택',
  '- 실용적인 꺾이는 점은 대략 0.5~0.6이라고 봄\n- 높은 임계값에서의 거짓 음성 일부는 온톨로지의 구조 문제(중복 클래스, 빠진 용어)를 가리킨다',
  'Taken together, these trends underscore', 'Some of the false negatives')

N(24, '개념 범위 평가의 한계 (저자 스스로 밝힘)',
  '- 개념 범위는 온톨로지의 정확성이나 후속 과업에서의 유용성을 완벽히 반영하지 않는다\n- "올바른 임계값"이 모호하다\n- 모든 낱말이 실린 사전과 비교하면 범위 100%가 나오지만 사전은 쓸모가 없다. 개념이 있는 것과 개념 사이의 추론이 맞는 것은 다르다\n- 그래도 필요한 개념을 모델링했는지를 아는 데는 의미가 있다',
  'The concept coverage evaluation is not a perfect reflection', 'We could achieve 100% concept coverage', 'It is still important to know')
N(24, '[우리 연구와의 관계]',
  '- 30% CQ 검증으로 말할 수 있는 것은 "필요한 개념이 온톨로지에 있다"까지다. "답이 맞다"는 KG 검증에서 따로 본다\n- 평가에서 빠진 개념과 중복 클래스가 드러나고, 이것이 다음 확장의 입력이 된다. 우리 계획의 "없는 개념은 다음 확장에서 다룬다"와 같다',
  'This evaluation also reveals areas for improvement', 'The more questions we ask')
N(24, '논의: 구조의 해석',
  '- RR이 높은 것은 소통용이라는 설계 목적 때문이라고 해석 (범주를 가로지르는 관계가 필요)\n- IR이 낮은 것(평평한 계층)은 한계로 인정',
  'This outcome reflects', 'Nonetheless, we acknowledge this as a')

N(25, '방법론의 효과에 대한 주장',
  '- 사람이 개입하는 네 단계 방법이 LLM의 환각, 의미 표류, 온톨로지 사일로를 줄이도록 설계되었다\n- 근거로 든 것은 표 3의 거부 사례다. 사람이 걸러 낸 뒤에 남은 오류가 얼마인지는 재지 않았다',
  'Our four-stage, human-in-the-loop methodology', 'Our hybrid verification protocol')
N(25, '한계 (저자가 밝힘)',
  '- 평가가 구조적(OntoQA)이고 정성적(사례 연구)이다. 과업 수준의 정량 평가가 없다\n- 온톨로지의 계층이 얕다\n- 실제 운영 환경에서 시험하지 않았다',
  'The evaluation presented is primarily structural', 'Second, as noted, the ontology', 'Finally, the framework has not yet been field-tested')
N(25, '결론',
  '- 사람이 개입하는 반자동 방법으로 소통용의 의미가 풍부한 온톨로지를 만들 수 있음을 보였다\n- 재현 가능한 작업 흐름과 실용적 지식 틀을 제공한다',
  'This research demonstrates that a semi-automated')
N(25, '[종합: 우리 연구에 가져올 것과 주의할 것]',
  '- 가져올 것 1: CQ를 확장용 70%와 평가용 30%로 나누고, 평가용은 구축에 쓰지 않는다\n- 가져올 것 2: 평가는 "CQ의 개념이 온톨로지에 있는가"로 한다. 빠진 개념은 다음 확장의 입력으로 쓴다\n- 가져올 것 3: LLM이 제안한 클래스와 관계는 사람이 계층 위치와 정의역·치역을 확인한다 (표 3의 오류 유형)\n- 주의 1: 이 논문의 CQ는 LLM이 만들고 연구진이 골랐다. 실무자 검토가 없다. 우리가 실무자 설문을 넣는 것은 이 논문에 없는 보완이다\n- 주의 2: 임베딩 유사도와 임계값에 따라 범위가 100%에서 0%까지 달라진다. 우리는 CQ가 적으므로 사람이 직접 대조한다\n- 주의 3: 평가자가 구축에 참여한 사람들이다\n- 주의 4: KG는 표본으로만 만들었고 검증하지 않았다. KG 검증의 근거로는 쓸 수 없다')

json.dump(M, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
if len(sys.argv) > 2:
    o = ['# FloodOntology 논문 리뷰 메모', '',
         'Li, S., Erickson, C., Zajac, M., Guo, X., Duan, Q., & Gong, J. (2025). A semi-automated framework for flood ontology construction with an application in risk communication. Water, 17, 2801.', '',
         '- 메모 제목과 같은 색 형광펜으로 원문 문장을 표시함(FloodOntology_메모작성본.pdf)',
         '- 제목이 [대괄호]인 메모는 원문 내용이 아니라 우리 연구에 대어 본 것임', '', '---', '']
    for p in sorted(M, key=int):
        o += ['## %s쪽' % p, '']
        for e in M[p]:
            o += ['### ' + e['lead'][1:], '', e['ko'], '']
    open(sys.argv[2], 'w', encoding='utf-8').write('\n'.join(o))
print('pages', len(M), 'memos', sum(len(v) for v in M.values()))
