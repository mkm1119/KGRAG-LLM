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
