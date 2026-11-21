#!/usr/bin/env python3
"""추가 조사 후보의 서지 확인(Crossref)과 arXiv 주제 검색. 결과는 candidates_checked.json 에 쌓는다.
사용: python3 harvest.py   (원문을 읽는 것이 아니라 제목·학술지·연도·초록 유무만 확인한다)"""
import json, re, time, urllib.parse, urllib.request, xml.etree.ElementTree as ET
UA = {'User-Agent': 'literature-survey-script/1.0'}
def get(u, t=40):
    for k in range(3):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t).read()
        except Exception as e:
            err = e; time.sleep(4 * (k + 1))
    print('FAIL', u[:90], err); return None
TITLES = ['An Ontology Framework for Flooding Forecasting', 'An ontology and a reasoning approach for evacuation in flood disaster response',
 'OFPO & KGFPO: Ontology and knowledge graph for flood process observation', 'An ontological data model to support urban flood disaster response',
 'Semantic agent framework for automated flood assessment using dynamic knowledge graphs',
 'Knowledge graph and mitigation measures recommendation for safety hazards in large-scale hydropower projects',
 'An ontology for sharing and managing information in disaster response: An illustrative case study of flood evacuation',
 'Spatio-Temporal Ontology for Change Analysis of Flood Affected Areas Using Remote Sensing Images',
 'An online anomaly recognition and knowledge graph construction method for dam safety monitoring',
 'Intelligent generation method of emergency plan for hydraulic engineering based on knowledge graph',
 'Research on a knowledge graph embedding method based on improved convolutional neural networks for hydraulic engineering',
 'A Systematic Review of Ontology-Based River Streamflow and Flood Data Management Challenges',
 'ORFFM: An Ontology-Based Semantic Model of River Flow and Flood Mitigation',
 'Towards an information centric flood ontology for information management and communication',
 'Construction and application of flood disaster knowledge graph based on multi-modal data',
 'A three-stage online anomaly identification model for monitoring data in dams',
 'Cracking risk analysis of face slabs in concrete face rockfill dams during the operation period',
 'Ontology for Evacuation Center in Flood Management Domain', 'Designing a knowledge graph system for digital twin to assess urban flood risk',
 'Construction and application of knowledge graph for flood defense and rescue of water infrastructure',
 'Construction and application of a knowledge graph for flood control and emergency response plans',
 'BIM and ontology-based knowledge management identification method for dam risk analysis',
 'Dam safety evaluation based on interval-valued intuitionistic fuzzy sets and evidence theory',
 'Application of Knowledge Graph in Water Conservancy Education Resource Organization under the Background of Big Data',
 'FloodBrain: Flood disaster reporting by web-based retrieval augmented generation with an LLM',
 'REMFLOW: RAG-enhanced multi-factor rainfall flooding warning in sponge airports via large language model',
 'The Implementation of Multimodal Large Language Models for Hydrological Applications',
 'Hydrological Research Evolution: A Large Language Model-Based Analysis of 310,000 Studies',
 'Using Large Language Models for Early Flood Analysis: A Case Study', 'RAG vs fine-tuning: Pipelines, trade offs, and a case study on agriculture']
out = {'crossref': [], 'arxiv': []}
for t in TITLES:
    b = get('https://api.crossref.org/works?rows=1&select=DOI,title,container-title,issued,abstract,type,publisher&query.bibliographic=' + urllib.parse.quote(t))
    if not b: continue
    it = json.loads(b)['message']['items']
    if not it: continue
    it = it[0]; ti = (it.get('title') or [''])[0]
    n = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
    out['crossref'].append({'query': t, 'match': n(t)[:40] == n(ti.replace('&amp;', '&'))[:40], 'doi': it.get('DOI'), 'title': ti, 'venue': (it.get('container-title') or [''])[0],
                            'year': (it.get('issued', {}).get('date-parts') or [[None]])[0][0], 'publisher': it.get('publisher'), 'has_abstract': 'abstract' in it})
    time.sleep(1)
Q = {'댐·저수지 KG/온톨로지': 'all:"knowledge graph" AND (all:dam OR all:reservoir OR all:hydropower)',
     '홍수·수자원 KG/온톨로지': '(all:"knowledge graph" OR all:ontology) AND (all:flood OR all:hydrology OR abs:"water resources")',
     '수자원 LLM/RAG': '(all:"large language model" OR all:"retrieval-augmented") AND (all:hydrology OR all:flood OR all:reservoir OR abs:"water resources")',
     'CQ 기반 온톨로지': 'all:"competency questions" AND all:ontology',
     'LLM 온톨로지·KG 구축': 'abs:"knowledge graph construction" AND abs:"large language model" AND abs:ontology',
     'KG 질의응답(Text2Cypher)': '(abs:"text-to-cypher" OR abs:"text2cypher" OR abs:"knowledge graph question answering") AND abs:"large language model"'}
ns = {'a': 'http://www.w3.org/2005/Atom'}
for g, q in Q.items():
    b = get('https://export.arxiv.org/api/query?max_results=40&sortBy=relevance&search_query=' + urllib.parse.quote(q), 60)
    if not b: continue
    for e in ET.fromstring(b).findall('a:entry', ns):
        out['arxiv'].append({'group': g, 'id': e.find('a:id', ns).text.split('/abs/')[-1], 'title': re.sub(r'\s+', ' ', e.find('a:title', ns).text).strip(),
                             'year': e.find('a:published', ns).text[:4], 'abstract': re.sub(r'\s+', ' ', e.find('a:summary', ns).text).strip()})
    time.sleep(4)
json.dump(out, open('candidates_checked.json', 'w'), ensure_ascii=False, indent=1)
print('crossref', len(out['crossref']), 'matched', sum(c['match'] for c in out['crossref']))
import collections
print(collections.Counter(c['publisher'] for c in out['crossref'] if c['match']).most_common())
print('arxiv', collections.Counter(a['group'] for a in out['arxiv']))
