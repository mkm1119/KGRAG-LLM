#!/usr/bin/env python3
"""LLM 연구팀 공유용 요약(5쪽 이내) 생성. build_team_brief.py의 서식 부품과 사실 확인을 그대로 쓰고 본문만 새로 쓴다. stdlib만 사용.
사용: python3 scripts/build_team_overview.py <출력 docx 경로> [--no-fig2]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, 'build_team_brief.py'), encoding='utf-8').read().split('# =================================================================== 표지')[0]
USE_FIG2 = '--no-fig2' not in sys.argv
sys.argv = [a for a in sys.argv if not a.startswith('--')]
exec(compile(_src, 'build_team_brief_head', 'exec'))


FIG0 = os.path.join(REPO, 'team_brief', 'fig0_framework.png')


def image_w(key, path, px_w, px_h, name, scale):
    rid = 'rIdImg%d' % (len(IMGS) + 1)
    IMGS[key] = (rid, path)
    cx = int(9972 * 635 * scale)
    cy = int(cx * px_h / px_w)
    n = len(IMGS)
    return ('<w:p><w:pPr><w:keepNext/><w:spacing w:before="40" w:after="20"/><w:jc w:val="center"/></w:pPr><w:r><w:drawing>'
            '<wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="%d" cy="%d"/><wp:docPr id="%d" name="%s" descr="%s"/>'
            '<wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/></wp:cNvGraphicFramePr>'
            '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="%d" name="%s"/><pic:cNvPicPr/></pic:nvPicPr>'
            '<pic:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
            '</a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>') % (cx, cy, n, name, esc(name), n, name, rid, cx, cy)


def title_s(t1, t2):
    return ('<w:p><w:pPr><w:spacing w:before="0" w:after="60"/><w:jc w:val="center"/><w:rPr>%s</w:rPr></w:pPr><w:r><w:rPr><w:b/><w:color w:val="1F4E79"/><w:sz w:val="36"/>%s</w:rPr>'
            '<w:t xml:space="preserve">%s</w:t><w:br/><w:t xml:space="preserve">%s</w:t></w:r></w:p>' % (LANG, LANG, esc(t1), esc(t2)))


def sub_s(t):
    return '<w:p><w:pPr><w:spacing w:after="80"/><w:jc w:val="center"/><w:rPr>%s</w:rPr></w:pPr>%s</w:p>' % (LANG, run(t, sz=19, color='505050'))


B = []
add = B.append
add(title_s('댐 운영 판단 지원 시스템', '연구 구조, 사용한 데이터, 시험 결과'))
add(sub_s('LLM 연구팀 공유용 요약 · 국민대학교 연구팀 · 2026.10.12 (10월 2일, 9일 랩미팅 종합) · 진행 중인 연구'))

# ---------------------------------------------------------------- 1
add(h1('1. 연구 목적', pagebreak=False))
add(para('댐 운영자가 “지금 소양강댐 상태와 비슷했던 과거 사례에서 어떤 방류 승인과 운영이 있었고, 그 근거는 무엇인가”처럼 물으면, 승인 기록·관측 자료·규정 원문에서 찾은 근거를 번호와 함께 답하는 시스템입니다. 방류를 결정하는 것이 아니라 운영자의 판단을 근거와 함께 돕는 것이 목적입니다. 필요한 정보가 서로 다른 형태(표 파일 두 종류, 법령 텍스트)로 흩어져 있고, 운영 판단에는 근거 없는 답변이 위험하므로, 자료를 먼저 구조화해 저장하고 LLM에는 그 안에서 찾은 근거만 주어 답하게 합니다.'))

# ---------------------------------------------------------------- 2
add(h1('2. 연구의 큰 틀', pagebreak=False))
add(image_w('fig0', FIG0, 1500, 720, 'Figure 0 연구의 큰 틀', 0.95))
add(caption('그림 1. 연구의 큰 틀(3단계)과 질문 응답 흐름. 주황색이 LLM이 하는 일이다.'))
add(li('STEP 1 Ontology 설계: 어떤 종류의 대상(댐, 승인, 운영행위 등)이 있고 어떤 관계로 연결되는지를 먼저 정의합니다. 단순히 표를 그래프로 옮기는 것이 아니라, 서로 다른 출처의 정보를 의미로 연결해 근거까지 따라가기 위한 설계입니다.'))
add(li('STEP 2 KG 구축: 실제 자료를 설계에 맞추어 지식그래프(KG)의 개체·관계·값으로 구성합니다. KG는 모든 자료를 담는 데이터베이스가 아니라, 의미 관계와 근거의 위치를 담아 문서·측정자료를 찾아가게 하는 중심 구조입니다.'))
add(li('STEP 3 질문 응답: 질문을 해석해 필요한 정보를 정하고, KG·문서·측정자료에서 근거를 찾아 모은 뒤, LLM이 근거 안에서만 답변을 설명합니다. 이 단계(질문 해석, 답변 작성)가 LLM 팀과 함께 설계할 부분입니다.'))

# ---------------------------------------------------------------- 2b
add(h1('3. 댐 운영에 적용한 구성 (현재 시험 중)', pagebreak=False))
add(para('큰 틀을 댐 운영 자료에 적용해 만들어 본 구성입니다. A(STEP 1~2)는 구축과 검증을 마쳤고, B(STEP 3)는 질문 10개로 시험한 단계이며 확정한 방법이 아닙니다.'))
add(image_w('fig1', FIG1, 1500, 1130, 'Figure 1 댐 운영 적용 구성', 1.0))
add(caption('그림 2. 큰 틀을 댐 운영에 적용한 구성. A는 자료를 구조화해 저장하는 사전 구축, B는 질문마다 수행하는 처리. 주황색이 LLM이 하는 일이다.'))
add(li('A. 사전 구축: 세 가지 자료를 규칙(코드)으로 구조화해 세 저장소에 나눕니다. KG에는 댐·승인·운영행위·운영기준·근거자료와 그 사이의 관계, 근거의 위치를 담고, 큰 값은 넣지 않고 찾아갈 키만 둡니다. 측정값 전체는 측정자료 저장소에, 규정 원문은 문서 저장소에 둡니다.'))
add(li('B. 질문 처리: ① LLM이 질문을 의도(질문 유형)와 값(댐, 기간)의 JSON으로 바꾸면, ②~⑤ 코드가 값을 검증하고 KG와 저장소에서 근거를 조회하고 차이·비율·유사 사례를 계산합니다. ⑥ 모아 둔 결과를 “근거 묶음”으로 LLM에 주면, LLM이 근거 번호를 붙여 답합니다.'))
add(li('의도는 처음 설계한 CQ1~CQ6(현재·과거 상태, 운영행위, 승인, 운영기준, 근거)과 수치 비교용 SIMILAR에, 구현 중 CURRENT·INTEGRATED·범위 밖을 더해 임시로 10개를 두었고, 이 체계 자체가 검토 대상입니다.'))
add(li('LLM을 두 곳에만 쓴 이유: 조회와 계산은 정확하고 확인 가능해야 한다고 보았기 때문입니다. 시험에서 LLM이 직접 계산한 값이 틀린 경우가 있었습니다. 모델은 Qwen3-8B-AWQ(vLLM)입니다.'))

# ---------------------------------------------------------------- 3
add(h1('4. 사용한 데이터', pagebreak=False))
add(table([
    ['자료', '출처', '규모와 형태', 'KG에서의 쓰임'],
    ['방류 승인 기록', '한강홍수통제소(공공데이터포털)', '충주·소양강·횡성·광동 4개 댐 80건(2010-09 ~ 2021-07). 표 파일, 한 행이 승인 한 건이고 비고란에 “이내 탄력적 조정” 같은 짧은 문장', '승인, 운영행위'],
    ['수문기상 시간 자료', 'K-water MyWater', '4개 댐 × 6개 변수(수위, 저수량, 강우량, 유입량, 총방류량, 저수율), 시간별 약 50.8만 행(2010-08 ~ 2026-09)', '측정자료 저장소 (KG에는 키만)'],
    ['홍수기 제한수위', '연계운영규정 별표3(법제처)', '충주 138.0, 소양강 190.3, 횡성 178.2 EL.m(광동댐은 없음). 선 문자로 그린 표가 들어 있는 법령 텍스트', '운영기준, 문서 저장소(원문 10조각)'],
], [1.5, 2, 4.8, 2]))
add(para('이 자료를 미리 설계한 구조에 맞추어 개체 6종류(댐, 수문기상 상태, 승인, 운영행위, 운영기준, 근거자료)와 관계 9종류로 구조화했습니다. 예를 들어 승인 한 건은 “승인 → 허가한 운영행위 → 댐”, “댐 → 수위 상태 → 측정값 저장소”, “댐 ← 제한수위 ← 별표3”으로 이어집니다(5.1의 그림 3). 단, 실제 운영기록은 공개되어 있지 않아 운영행위는 승인 비고와 측정 방류량 변화에서 규칙으로 구성한 것이며, 규칙(분류, 시각)은 연구자가 정한 임시 기준입니다.'))

# ---------------------------------------------------------------- 4
add(h1('5. 시험 결과 (예비)', pagebreak=False))
add(h2('5.1 지식그래프 구축'))
add(table([
    ['결과', '의미'],
    ['개체 273개, 관계 457개', '댐 4, 상태 24(댐 4 × 변수 6), 승인 80, 운영행위 68(승인 80건에서 구성), 운영기준 3(광동댐 제외), 근거자료 94. 관계는 근거 연결 202, 승인→운영행위 80, 승인→댐 80 등이다.'],
    ['외부 저장소', '측정값 508,246행, 규정 원문 10조각. KG에는 이를 찾아갈 키(측정소 코드, 조각 번호)만 있다.'],
    ['구조 검증', '관계 양 끝, 필수 속성, 값 형식, 근거 연결, 경로 일치 5개 검사 모두 위반 0건. 질문 유형(CQ)별 점검에서 실제 수행 확인이 필요한 CQ3(과거 운영행위)만 부분 가능, 나머지는 가능했다.'],
    ['점검 중 발견·수정', '운영행위가 연결되지 않은 승인 6건은 댐에서 찾아갈 경로가 없었다(도달 74/80건). 승인과 댐을 직접 잇는 관계를 추가해 80건 모두 도달하게 했다(관계 8개 → 9개).'],
], [2, 8]))
if USE_FIG2:
    add(image_w('fig2', FIG2, 1500, 950, 'Figure 2 KG 예시', 0.78))
    add(caption('그림 3. 충주댐 승인 1368번 한 건의 KG 일부(회색은 근거자료로 향하는 supportedBy, 파선은 KG 밖 저장소를 찾아가는 키).'))
add(h2('5.2 질문에서 답변까지: Qwen3-8B 시험'))
add(para('질문 10개를 한 번씩 실행했습니다. 아래는 현재 상태와 제한수위 확인, 비슷한 과거 사례의 승인·운영행위·근거 조회, 승인량 대비 방류량 비교를 모두 포함하는 질문의 전 과정입니다.'))
t4 = TR('m04')
assert '67.4%' in t4['bundle'] and '0.223' in t4['bundle']
add(table([
    ['질문', QD['m04']['question']],
    ['① LLM 출력', t4['intent_raw'] + '  (사례 수 k는 질문에 없었는데 LLM이 채움)'],
    ['②~⑤ 코드', '검증 통과 → 제한수위 190.3 EL.m(KG), 현재 상태 2026-09-28 23:00의 수위 185.2644 EL.m(측정자료, 저장된 가장 최근 값) → 현재 수위는 제한수위 대비 -5.04 m. 비슷한 과거 사례를 수위·유입량의 유클리드 거리로 골라 2017-08-25 15:00(거리 0.223), 그 사례의 운영행위·승인·측정값 조회, 최대 총방류량 1011.2 CMS는 승인량 1500㎥/s의 67.4%.'],
    ['⑥ LLM 답변', t4['answer'].replace('**', '')],
], [1.3, 8.7]))
add(para('답변의 수치와 근거 번호는 근거 묶음과 일치했고, 수위 차 “+7.27 m”는 묶음에 계산값이 없어 LLM이 직접 계산한 값입니다(정확). 사례를 1개만 제시한 것은 LLM이 사례 수를 1로 채웠기 때문입니다. 10개 질문의 결과는 다음과 같습니다(CURRENT는 현재 상태와 제한수위 비교, INTEGRATED는 기간 내 운영·승인·상태·근거 종합, SIMILAR는 비슷한 과거 사례).'))
add(table([
    ['질문(요약)', '의도 분류', '판정', '관찰'],
    ['소양강·충주·광동 현재 수위와 제한수위 비교(3개)', '3개 모두 CURRENT', '맞음', '수치와 근거 일치. 광동댐은 기준이 없어 “자료에 없음”이라고 정확히 답함'],
    ['횡성 2020-08 운영·승인·수위·근거 정리', 'INTEGRATED', '대체로 맞음', '수치 일치. 방류 시작 시각을 “승인된”이라고 표현'],
    ['충주 방류 전 승인과 공식 근거', 'INTEGRATED', '오류', '방류의 근거(승인 기록)와 제한수위의 근거(별표3)를 혼동'],
    ['소양강, 광동 비슷한 과거 사례(2개)', 'SIMILAR', '대체로 맞음', '수치 일치. 사례 수를 임의로 지정, 수위 차 직접 계산, 소수 15자리 출력'],
    ['충주 비슷한 사례의 승인·방류·수위 비교', 'SIMILAR', '오류', '현재 값을 사례 값처럼 씀, 증가율 계산 오류'],
    ['충주 승인량과 실측 방류량의 차이', 'INTEGRATED', '오류', '비율을 “차이”로 서술, 늦게 승인된 상한을 비교에 씀'],
    ['소양강·충주 중 제한수위에 더 가까운 댐', 'CURRENT (기대: 범위 밖)', '실패', '같은 키를 두 번 쓴 JSON을 파서가 마지막 값만 읽어 한 댐으로 처리'],
], [3.4, 1.9, 1.1, 3.6]))
add(h2('5.3 확인된 것과 한계'))
add(li('확인된 것: 질문 해석 → KG·저장소 조회 → 근거 번호가 붙은 답변까지 구조가 끝까지 동작합니다. 의도 분류는 10개 중 9개가 기대와 같았고, 단순한 질문은 정확히 답했습니다.'))
add(li('문제의 원인: 오류의 상당수는 근거 묶음의 구성이나 계산 부족(코드)에서 나와 수정했습니다(재시험 전). LLM 쪽 문제는 선택 값을 임의로 채우는 것, 같은 키를 두 번 쓰는 JSON, 개념 혼동(비율과 차이, 근거의 구분)입니다.'))
add(li('한계: 질문 10개, 소형 모델, 1회 실행이며, 같은 LLM에 표 데이터를 그대로 주는 방식과의 비교는 아직 없습니다. 운영행위는 승인에서 구성한 추정입니다.'))

# ---------------------------------------------------------------- 5
add(h1('6. 우리 구성에 대한 의견 요청', pagebreak=False))
add(table([
    ['주제', '지금 해 본 것과 묻고 싶은 것'],
    ['질문 해석', 'LLM 하나가 의도 10개 중 하나를 JSON으로 출력해 보았습니다. 한 질문에 여러 유형이 섞일 때의 의도 체계, 규칙·학습 모델과의 병행, JSON 형식 제약 방법.'],
    ['답변 검증', '근거 안에서만 답하도록 프롬프트 규칙을 줬지만 개념 혼동이 남았습니다. 숫자·근거 번호를 근거 묶음과 자동 대조하는 방법, 계산을 LLM에 어디까지 허용할지.'],
    ['검색 설계', '의도별로 정해 둔 질의 틀로 조회하고 문서는 조각 번호로 찾아 보았습니다. text-to-Cypher 도입 여부, 문서가 늘 때 벡터 검색 병행 시점, 수치 상태의 유사 사례 검색 방법.'],
    ['평가', '지금은 사람이 읽고 판정했습니다. 같은 LLM에 표 데이터를 직접 주는 기준선과 정답 세트, 지표(근거 일치율, 인용률 등) 설계.'],
    ['모델·서버', 'Qwen3-8B-AWQ를 공유 GPU(여유 약 11.7GB)에서 사용, 질문당 9~97초. 32B는 메모리 부족으로 실패했습니다. 적합한 모델 크기와 처리 시간 단축 방법.'],
    ['데이터 확장', '현재는 저장해 둔 자료의 가장 최근 시각을 “현재”로 씁니다. 실시간 조회, 실제 운영기록 확보, 댐과 문서 확대 시 병목.'],
], [1.4, 8.6]))
add(para('시험 질문 전문, 프롬프트 전문, 구축 단계별 상세(근거 문헌 포함)는 요청하시면 별도로 드리겠습니다.'))

doc = ROOT_OPEN + ''.join(B) + SECT + '</w:body></w:document>'
import xml.dom.minidom
xml.dom.minidom.parseString(doc.encode('utf8'))
rels = tz.read('word/_rels/document.xml.rels').decode('utf8')
ct = tz.read('[Content_Types].xml').decode('utf8')
footer = tz.read('word/footer1.xml').decode('utf8').replace('랩미팅 연구 진행사항 · Ontology–KG–Hybrid Retrieval–LLM', '댐 운영 판단 지원 시스템 · LLM 연구팀 공유용 요약')
assert '공유용 요약' in footer
for key, (rid, path) in IMGS.items():
    rels = rels.replace('</Relationships>', '<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/%s.png"/></Relationships>' % (rid, key))
if 'Extension="png"' not in ct:
    ct = ct.replace('<Default Extension="xml"', '<Default Extension="png" ContentType="image/png"/><Default Extension="xml"')
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as zo:
    for item in tz.infolist():
        data = tz.read(item.filename)
        if item.filename == 'word/document.xml':
            data = doc.encode('utf8')
        elif item.filename == 'word/_rels/document.xml.rels':
            data = rels.encode('utf8')
        elif item.filename == '[Content_Types].xml':
            data = ct.encode('utf8')
        elif item.filename == 'word/footer1.xml':
            data = footer.encode('utf8')
        zo.writestr(item, data)
    for key, (rid, path) in IMGS.items():
        zo.write(path, 'word/media/%s.png' % key)
print('저장', OUT, '| 요소', len(B), '| 그림', len(IMGS))
