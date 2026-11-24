#!/usr/bin/env python3
"""최종보고서 조립: project_khnp/final_report/sections/*.json 의 소절을 템플릿에 넣어 hwpx로 만든다.
- 소절 파일은 [종류, 내용] 항목의 배열이다(작성 지침: sections/_작성지침.md).
- ⟦문헌:id⟧ 는 처음 나온 순서대로 [n]으로 바꾸고 참고문헌 목록을 만든다(서지는 references/case_survey/bib.json).
- ⟦표:라벨⟧, ⟦그림:라벨⟧ 은 장 번호를 붙여 '표 1.3', '그림 1.2'로 바꾼다.
- 목차, 표 목차, 그림 목차는 본문의 제목에서 다시 만든다(쪽 번호는 한글의 차례 만들기로 넣는다).
- 소절 파일 이름(1_1_1 등)은 과업 항목 번호이며, 보고서에서는 서론이 1장이므로 2.1.1이 된다.
- 논문 그림은 자동으로 넣을 수 없으므로 그림 자리(FIGPLACE)는 자리표시 문단과 그림 제목으로 넣는다.
사용: python3 dam_pilot_data/scripts/build_final_report.py [출력.hwpx]
"""
import glob, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from final_report_lib import *          # noqa
ROOT = os.path.join(HERE, '..', '..')
SEC = os.path.join(ROOT, 'project_khnp', 'final_report', 'sections')
BIB = json.load(open(os.path.join(ROOT, 'references', 'case_survey', 'bib.json'), encoding='utf-8'))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'project_khnp', 'final_report', '최종보고서_초안.hwpx')

# 절 제목(템플릿의 제목) -> 그 절에 들어갈 소절 파일(순서대로)
PLAN = {
    '1.1 과업의 배경 및 목적': ['0_1'],
    '1.2 과업 범위': ['0_2'],
    '1.3 추진 경위': ['0_3'],
    '2.1 수자원 분야 사례 조사': ['1_1_1', '1_1_2', '1_1_3', '1_1_4', '1_1_5'],
    '2.2 국내 운영 여건 조사': ['1_2'],
    '2.3 적용 기술요소 및 모델 제안': ['1_3'],
    '3.1 수집 경로 조사': ['2_1'],
    '3.2 온톨로지·메타데이터 설계방안 조사': ['2_2'],
    '3.3 RAG-LLM 통합 파이프라인(안) 제시': ['2_3'],
}
MAKE = {'H3': H3, 'H4': H4, 'H5': H5, 'BODY': BODY, 'SQ': SQ, 'CI': CI, 'DS': DS, 'NOTE': NOTE}
FORM = {'H3': form_h3, 'H4': form_h4, 'H5': form_h5}        # 발주처 양식의 제목 번호로 바꾼다

refs, labels, missing_bib = [], {}, set()
counters = {}


def chapter_of(heading):
    return heading.split('.')[0]


def cite(m):
    key = m.group(1).strip()
    if key not in BIB:
        missing_bib.add(key)
        return '[?]'
    if key not in refs:
        refs.append(key)
    return '[%d]' % (refs.index(key) + 1)


def first_pass(items, ch):
    """표·그림 번호를 나온 순서대로 매긴다."""
    for kind, v in items:
        if kind in ('TABLE', 'FIGPLACE'):
            typ = '표' if kind == 'TABLE' else '그림'
            counters[(ch, typ)] = counters.get((ch, typ), 0) + 1
            labels[(typ, v['label'])] = '%s %s.%d' % (typ, ch, counters[(ch, typ)])


def resolve(t):
    t = re.sub(r'⟦문헌:([^⟧]+)⟧', cite, t)
    t = re.sub(r'⟦(표|그림):([^⟧]+)⟧', lambda m: labels.get((m.group(1), m.group(2).strip()), '%s ?(%s)' % (m.group(1), m.group(2))), t)
    t = form_refs(re.sub(r'\s+\[', ' [', t))
    # '표 2.3과 같다'처럼 번호의 끝 숫자에 맞는 조사를 쓴다(0·1·3·6·7·8은 받침이 있다)
    return re.sub(r'((?:표|그림) \d+\.\d*(\d))(?:와|과)(?= 같| ((?:표|그림)) )', lambda m: m.group(1) + ('과' if m.group(2) in '013678' else '와'), t)


def render(items):
    out = []
    for kind, v in items:
        if kind == 'TABLE':
            rows = [[resolve(str(c)) for c in r] for r in v['rows']]
            out += table('%s %s' % (labels[('표', v['label'])], v['caption']), rows, v['widths'], v.get('align'), v.get('unit'), resolve(v['note']) if v.get('note') else None)
        elif kind == 'FIGPLACE':
            out += [BODY('[그림 자리] %s' % resolve(v.get('source', ''))), FCAP('%s %s' % (labels[('그림', v['label'])], v['caption'])), BLANK()]
        else:
            out.append(MAKE[kind](resolve(FORM[kind](v)) if kind in FORM else resolve(v)))
    return out


doc = Report()
loaded, stats = {}, []
for heading, files in PLAN.items():
    items = []
    for f in files:
        p = os.path.join(SEC, f + '.json')
        if os.path.exists(p):
            part = json.load(open(p, encoding='utf-8'))
            items += part
            stats.append((f, sum(len(v) for k, v in part if isinstance(v, str)), sum(1 for k, v in part if k == 'TABLE'), sum(1 for k, v in part if k == 'FIGPLACE')))
    loaded[heading] = items
for heading, items in loaded.items():
    first_pass(items, chapter_of(heading))
for heading, items in loaded.items():
    if items:
        doc.fill(form_h2(heading), render(items))
doc.references([BIB[k] for k in refs] or ['(작성 중)'])
toc_n = doc.rebuild_toc()
doc.save(OUT)
unres = [l for l in re.findall(r'(?:표|그림) \?\([^)]*\)', ''.join(doc.ps))]
print('저장', OUT)
print('  목차 %d줄, 표 목차 %d건, 그림 목차 %d건' % toc_n)
for s in stats:
    print('  %-8s 본문 %6d자  표 %2d  그림 자리 %2d' % s)
print('  참고문헌 %d건, 서지 없는 인용 %s, 풀리지 않은 표·그림 참조 %s' % (len(refs), sorted(missing_bib), unres))
