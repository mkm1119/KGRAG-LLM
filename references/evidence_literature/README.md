# references/evidence_literature/ — 근거 문헌 원본 PDF

사용자가 공유한 원본 PDF를 **수정 없이** 보관한다. 연구 문서(`01_AI_RESEARCH_HANDOFF.md` §17)의 인용과의 대응은 아래와 같다.

| 파일 | handoff §17 대응 문헌 | 식별 근거 |
|---|---|---|
| `Noy.pdf` | Noy & McGuinness, *Ontology Development 101: A Guide to Creating Your First Ontology* (handoff §17: 2001) | **내용 확인됨(2026-09-30)**: 1쪽 제목·저자(Natalya F. Noy, Deborah L. McGuinness, Stanford University), 25쪽. PDF에 발행 연도·보고서 번호 표시 없음(연도는 handoff 표기) |
| `36_FloodOntology.pdf` | Li et al. (2025), *A Semi-Automated Framework for Flood Ontology Construction with an Application in Risk Communication*, Water 17, 2801 | 파일명. PDF 메타데이터에 제목 없음(약 31쪽) — **내용 미확인** |
| `46_DDKG.pdf` | Huang et al. (2026), *Dam defects ontology and knowledge graph construction from multi-source hazard data using large language models* | PDF 메타데이터 제목 일치 (약 16쪽) |
| `47_OntoDSMS.pdf` | Zhou et al. (2023), *BIM and ontology-based knowledge management for dam safety monitoring* | PDF 메타데이터 제목 일치 (약 12쪽) |
| `39_GraphAide.pdf` | Purohit et al. (2024), *GraphAide: Advanced Graph-Assisted Query and Reasoning System* | PDF 메타데이터 제목 일치 (약 9쪽) |

- 무결성: `SHA256SUMS.txt`
- 이 폴더에 넣었다는 사실은 원문 대조를 수행했다는 뜻이 아니다. **대조 상태:** `Noy.pdf` — STEP 1-A Step 1 절(p.4–6)을 대조 완료(`dam_pilot_data/04_reports/M_STEP1A_DOMAIN_SCOPE.md` §9); 그 외 4편 — 미대조. 대조 시 절·쪽을 확인한 뒤 `STEP1_DECISION_LOG.md`를 갱신한다.
- 텍스트 확인에는 `dam_pilot_data/scripts/pdf_text_extract.py`(표준 라이브러리 전용, 단순 인코딩 PDF만 지원)를 썼다. `Noy.pdf`에는 동작했고 `36_FloodOntology.pdf`는 읽지 못했다.
- 출판사 PDF의 저작권·재배포 조건은 저장소 공개 범위에 따라 확인이 필요하다.

## validation/ — 검증 방법 문헌 (2026-11-11 추가)

공개 원문(arXiv, CEUR-WS, Semantic Web Journal 원고, SciTePress)을 받은 그대로 보관한다. 해석: `lab_meeting/paper_review/검증부분_해석2_온톨로지_KG.md`

| 파일 | 문헌 |
|---|---|
| RaadCruz2015_OntologyEvaluationSurvey.pdf | Raad & Cruz (2015), A Survey on Ontology Evaluation Methods, KEOD |
| Lippolis2025_LLM_OntologyEvaluation.pdf | Lippolis et al. (2025), Large Language Models Assisting Ontology Evaluation, arXiv:2507.14552 |
| Bandeira2016_FOCA.pdf | Bandeira et al. (2016), FOCA: A Methodology for Ontology Evaluation, arXiv:1612.03353 |
| Zaveri2016_LinkedDataQuality.pdf | Zaveri et al. (2016), Quality Assessment for Linked Data: A Survey, Semantic Web 7(1) (게재 전 원고) |
| Paulheim2017_KGRefinement.pdf | Paulheim (2017), Knowledge Graph Refinement: A Survey of Approaches and Evaluation Methods, Semantic Web 8(3) (게재 전 원고) |
| Gao2019_KGAccuracyEvaluation.pdf | Gao et al. (2019), Efficient Knowledge Graph Accuracy Evaluation, PVLDB 12(11), arXiv:1907.09657 |
| Draetta2025_GRADES.pdf | Draetta et al. (2025), Beyond the Metrics (GRADES), RAGE-KG 2025, CEUR-WS Vol-4079 |
| Nunez2026_HERMES.pdf | Nuñez et al. (2026), HERMES, RAGE-KG 2026, CEUR-WS Vol-4312 |
| KeetKhan2024_TypesOfCQs.pdf | Keet & Khan (2024), Discerning and Characterising Types of Competency Questions for Ontologies, arXiv:2412.13688 |
| Alharbi2023_RetrofittingCQs.pdf | Alharbi et al. (2024), An Experiment in Retrofitting Competency Questions for Existing Ontologies, ACM SAC 2024, arXiv:2311.05662 |
| Alharbi2025_CQElicitationComparison.pdf | Alharbi et al. (2025), A Comparative Study of Competency Question Elicitation Methods from Ontology Requirements, arXiv:2507.02989 |
| WatkissLeek2026_IDEA2.pdf | Watkiss-Leek et al. (2026), IDEA2: Expert-in-the-loop competency question elicitation, arXiv:2604.01344 |
| AbuSalih2021_DomainSpecificKGSurvey.pdf | Abu-Salih (2021), Domain-specific Knowledge Graphs: A survey, J. Network and Computer Applications 185, arXiv:2011.00235 (3.5절 KG 평가, 8쪽) |
| Wilson2023_OntologyQualityModel.pdf | Wilson et al. (2023), A Conceptual Model for Ontology Quality Assessment: A Systematic Review, Semantic Web 14(6), 1051–1097 (SWJ 원고 swj3003) |
| LiGarijo2025_LLM4OE_SLR.pdf | Li, Garijo & Poveda-Villalón (2026), Large Language Models for Ontology Engineering: A Systematic Literature Review, Semantic Web, doi:10.1177/22104968261465514 (SWJ 원고 swj3864) |
| KeetLawrynowicz2016_TDD.pdf | Keet & Ławrynowicz (2016), Test-Driven Development of Ontologies, ESWC 2016 (확장판 arXiv:1512.06211) |
| BezerraFreitas2017_CQUnitTesting.pdf | Bezerra & Freitas (2017), Verifying Description Logic Ontologies based on Competency Questions and Unit Testing, ONTOBRAS 2017, CEUR-WS Vol-1908, 159–164 |
