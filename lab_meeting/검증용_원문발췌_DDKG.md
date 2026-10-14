# 검증용 원문 발췌: DDKG (Huang et al., 2026)

자료에 넣는 글이 아니라, 정리한 내용이 사실인지 확인하기 위한 발췌이다.
- 문헌: Huang, J. et al. (2026). Advanced Engineering Informatics, 76, 104987. (파일: `46_DDKG.pdf`)
- 아래 영문은 PDF에서 추출한 원문이며, 번역은 이 발췌용으로 옮긴 것이다.

## 1. 전체 구조 (3장 Methodology 첫 문단)

> “Fig. 1 illustrates the overall construction framework of the DDKG, which comprises three main components: DDO construction, knowledge extraction, and knowledge fusion.”

번역: 그림 1은 DDKG의 전체 구축 틀을 보여 주며, 세 구성 요소인 DDO(댐 결함 도메인 온톨로지) 구축, 지식 추출, 지식 융합으로 이루어진다.

## 2. 3.1절 DDO 구축: 7단계

> “In this study, a seven-step methodology is adopted to construct the DDO. The process comprises the following steps: (1) defining the dam hazard domain ontology and related tasks; (2) considering the reuse of existing ontology models related to dam hazards; (3) enumerating relevant terminology; (4) defining ontology classes and hierarchical structures; (5) defining class attributes and relationships; (6) specifying constraints; and (7) creating instances.”

번역: 본 연구는 DDO를 구축하기 위해 7단계 방법론을 쓴다. ① 도메인과 과제 정의, ② 기존 온톨로지 재사용 검토, ③ 관련 용어 나열, ④ Class와 계층 정의, ⑤ 속성과 관계 정의, ⑥ 제약 조건 지정, ⑦ 인스턴스 생성.

(이 7단계는 Noy & McGuinness(2001)의 Ontology Development 101 단계와 같은 순서이다. 본 발췌에서는 DDKG가 이를 쓴다는 점만 확인한다.)

> “DDO = ⟨C, P, H⟩ (1) where C = {c_i | i ∈ N*} is the set of top-level classes; … P = {p_ij | i, j ∈ N*, i ≠ j} is the set of object properties, where p_ij represents a directed relationship c_i → c_j; H = {S_i | c_i ∈ C*} is the set of all subclasses under each top-level class …”

번역: DDO는 Class 집합 C, 객체 속성(관계) 집합 P(방향이 있는 c_i → c_j), 하위 Class 집합 H의 세 요소로 나타낸다 (식 1).

## 3. 3.2.1절 지식 출처와 전처리

> “The China Reservoir Operation and Management Platform stores a large volume of fundamental engineering data in the form of structured tables, which largely satisfy the data requirements of top-level classes c1–c4 in the DDO. In contrast, the data corresponding to top-level classes c5–c7 are derived from unstructured text. These texts are highly heterogenous in formats, including PDF, DOC, and PNG files, and the original documents often contain redundant or irrelevant information. Prior to knowledge extraction, the texts are preprocessed to eliminate noise and normalize the data.”

번역: 중국 저수지 운영관리 플랫폼은 구조화된 표 형태의 기본 공학 자료를 대량 보유하며, 이는 DDO의 상위 Class c1~c4가 요구하는 자료를 대체로 충족한다. 반면 c5~c7에 해당하는 자료는 비정형 텍스트에서 얻는다. 이 텍스트는 PDF, DOC, PNG 등 형식이 매우 다양하고 불필요한 내용이 많으므로, 지식 추출 전에 잡음을 제거하고 데이터를 정규화한다.

> “For a given unstructured text D, its format is first converted into a structured markdown representation D_md. State-of-the-art optical character recognition models are then applied to perform layout parsing and format conversion. Next, regular expressions are used to delimit the boundaries of text blocks D_md,i that contain relevant knowledge entities and remove redundant content. Finally, the extracted text blocks are integrated into a single corpus, denoted as T: T = {D_md,1, D_md,2, ⋯, D_md,n} (2)”

번역: 비정형 텍스트 D는 먼저 구조화된 마크다운 D_md로 변환하고, OCR 모델로 레이아웃 분석과 형식 변환을 한다. 이어서 정규식으로 관련 지식 개체가 있는 텍스트 블록 D_md,i의 경계를 찾고 불필요한 내용을 제거한다. 마지막으로 블록들을 하나의 말뭉치 T로 합친다 (식 2).

## 4. 3.2.2절 규칙 기반 추출

> “Each evaluation is classified into Grade A, B, or C, corresponding to no defect, minor defect, and serious defect, respectively. Because these results are generally described in highly standardized forms, they can be directly extracted using regular expressions. For example, from the expression ‘the flood-control safety rating is Grade C’, the flood-control safety evaluation result can be accurately extracted as ‘C’, without the need for deep learning-based recognition.”

번역: 각 평가는 A, B, C 등급(결함 없음, 경미, 심각)으로 분류된다. 이 결과는 대체로 매우 정형화된 형태로 서술되므로 정규식으로 바로 추출할 수 있다. 예를 들어 “홍수 조절 안전성 평가 등급은 C등급이다”에서 평가 결과 “C”를 딥러닝 없이 정확하게 뽑을 수 있다.

## 5. 3.2.3절 LLM 기반 추출 (DDKG 방법. 우리는 쓰지 않음)

> “T → P1 → H = {h1, h2, …, hm} → P2 → E = {e1, e2, …, en} (3)” — 프롬프트 P1로 결함 관련 서술 조각을 찾고, 프롬프트 P2로 복합 서술을 단위로 쪼갠다.

> 분류기 OHCF의 4단계: (a) LoRA로 LLM 미세조정(식 4~6), (b) 온도를 바꿔 n번 추론한 뒤 가장 많이 나온 라벨을 선택하는 투표(식 7~9), (c) 온톨로지 제약 일관성 검사, (d) 전문가 검토와 온톨로지 확장.

> “A constraint-conflict set A, defined as a sparse subset of the cartesian product, is introduced to record clearly incompatible c5 and c6 label pairs … A ⊆ S_f × S_c (10) … V(L*_i) = False if (s*_f, s*_c) ∈ A; True if (s*_f, s*_c) ∉ A (11)”

번역: 서로 맞지 않는 c5·c6 라벨 쌍을 기록한 충돌 집합 A(곱집합의 부분집합)를 두고, 분류 결과가 A에 속하면 False, 아니면 True를 내는 일관성 검사 함수 V를 정의한다 (식 10~11).

> “Samples marked as ‘False’ are automatically aggregated by the system and submitted to an expert review queue … If the expert confirms that the concept is new, a corresponding node is added to the DDO …”

번역: False로 표시된 샘플은 전문가 검토 대기열에 모이고, 전문가가 새 개념으로 확인하면 DDO에 노드를 추가한다. 이렇게 온톨로지가 갱신·확장된다.

## 6. 3.3절 KG 저장

> “The knowledge extracted in Section 3.2 is integrated into JSON format. Based on the semantic and hierarchical relationships within the DDO, a Python script was developed to parse JSON key-value pairs and generate corresponding Cypher statements. This process facilitates the batch creation of DDKG nodes and the construction of inter-entity relationships, completing the injection of dam hazard knowledge into the Neo4j database.”

번역: 3.2절에서 추출한 지식을 JSON으로 통합하고, DDO의 의미·계층 관계에 따라 파이썬 스크립트가 JSON의 키·값을 읽어 Cypher 명령문을 만들어 Neo4j에 노드와 관계를 한꺼번에 적재한다.

## 7. 4.3.2절 Cypher 검색 예

> “(:Dam)-[:exhibitsHazards]->(:HazardForm) … (:HazardForm {node_name:'Structure'})-[:hasSubclass*0..]->(:HazardForm)”

번역: Dam에서 exhibitsHazards 관계로 결함 형태(HazardForm)를 따라가고, 하위 계층(hasSubclass)은 0단계 이상 따라가는 Cypher 질의로 조건을 건 검색을 보여 준다.
