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
FIG1A = os.path.join(REPO, 'team_brief', 'fig1a_step12.png')
FIG1B = os.path.join(REPO, 'team_brief', 'fig1b_step3.png')


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


def cell(text, w, fill=None, b=False, color=None, center=False, sz=TBL):
    lines = [l for l in str(text).split('\n')] or ['']
    ps = []
    for l in lines:
        ind = '<w:ind w:left="180" w:hanging="180"/>' if l.startswith('• ') else ''
        ps.append('<w:p><w:pPr><w:spacing w:after="20" w:line="252" w:lineRule="auto"/>%s%s</w:pPr>%s</w:p>' % (ind, '<w:jc w:val="center"/>' if center else '', run(l, sz=sz, b=b, color=color)))
    return '<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/>%s%s</w:tcPr>%s</w:tc>' % (w, '<w:shd w:val="clear" w:color="auto" w:fill="%s"/>' % fill if fill else '', MAR, ''.join(ps))


B = []
add = B.append
add(title_s('댐 운영 판단 지원 시스템', '연구 구조, 사용한 데이터, 시험 결과'))
add(sub_s('LLM 연구팀 공유용 요약 · 국민대학교 연구팀 · 2026.10.12 (10월 2일, 9일 랩미팅 종합) · 진행 중인 연구'))

# ---------------------------------------------------------------- 1
add(h1('1. 연구의 큰 틀', pagebreak=False))
add(image_w('fig0', FIG0, 1500, 1345, 'Figure 1 연구의 큰 틀', 0.85))
add(caption('그림 1. 연구의 전체 큰 틀(STEP 1~3)과 그 안에서 하이브리드 검색이 흘러가는 구조. 주황색이 LLM이 하는 일이다.'))
add(li('STEP 1 Ontology 설계: 어떤 대상(예: 댐, 방류 승인)이 있고 서로 어떤 관계(예: 승인이 운영행위를 허가한다)를 갖는지 정한 설계도이다. 답해야 할 질문을 먼저 정하고 그에 맞추어 설계하였다.'))
add(li('STEP 2 KG 구축: 실제 자료를 설계에 맞추어 지식그래프(KG)의 점(개체)과 선(관계)으로 정리한다. 예) “충주댐”이 점, “승인 1368은 충주댐에 대한 승인이다”가 선'))
add(li('KG는 모든 값을 담지 않는다. 측정값 표와 규정 원문은 별도 저장소에 두고, KG에는 찾아갈 위치(번호)만 적는다.'))
add(li('STEP 3 질문 응답: 하이브리드 검색으로 성격이 다른 세 곳(KG, 측정자료 저장소, 문서 저장소)에서 각각 맞는 방식으로 근거를 찾는다.'))
add(li('KG에서 연결을 따라가며 관련 승인·기준을 찾고, 그 결과의 번호로 측정자료 저장소의 숫자와 문서 저장소의 규정 원문을 가져온다.'))
add(li('모은 근거를 LLM에 주고 근거 안에서만 답하게 한다. LLM이 맡는 부분(질문 해석, 답변 작성)을 LLM 팀과 함께 설계하고자 한다.'))

# ---------------------------------------------------------------- 2
add(h1('2. 댐 운영에 적용한 구성 (현재 시험 중)', pagebreak=False))
add(li('큰 틀을 댐 운영 자료에 적용한 구성이다. STEP 1·2는 구축과 검증을 마쳤고, STEP 3은 질문 10개로 시험한 단계이며 확정한 방법이 아니다.'))
add(image_w('fig1a', FIG1A, 1500, 1000, 'Figure 2 STEP 1·2', 0.95))
add(caption('그림 2. 댐 운영에 적용한 구성 (1): STEP 1 설계와 STEP 2 구축.'))
add(image_w('fig1b', FIG1B, 1500, 1015, 'Figure 3 STEP 3', 0.9))
add(caption('그림 3. 댐 운영에 적용한 구성 (2): STEP 3 질문 처리. 주황색이 LLM이 하는 일이다.'))
add(li('STEP 1 Ontology 설계: 운영자에게 필요한 질문 7개(전체 질문 1개, 세부 질문 6개)를 먼저 설정하였다.'))
add(li('세부 질문 6개: 현재 상태, 과거 상태, 과거 운영행위(실제 수행된 방류 같은 조작), 과거 방류 승인, 현재 운영기준, 공식 근거'))
add(li('위 질문에 답하기 위해 개체 6종류(댐, 수문기상 상태, 방류 승인, 운영행위, 운영기준, 근거자료)와 관계 9종류를 설계하였다.'))
add(li('STEP 2 사전 구축: 세 자료(방류 승인 기록, 수문기상 시간 자료, 규정 별표3)를 미리 정한 규칙으로 자동 정리하여 세 저장소에 나누어 담는다.'))
add(li('KG에는 개체·관계·근거의 위치를 담고, 측정값 전체는 측정자료 저장소에, 규정 원문은 문서 저장소에 둔다.'))
add(li('STEP 3 질문 처리: ① LLM이 질문을 “질문 유형”과 “댐·기간” 값으로 변환한다. 예) 유형은 비슷한 과거 사례, 댐은 소양강댐'))
add(li('②~⑤ 정해진 규칙이 값을 확인하고, KG와 저장소에서 근거를 조회하고, 제한수위와의 차이·승인량 대비 방류량 비율·비슷한 과거 사례를 계산한다.'))
add(li('⑥ 결과를 번호 붙인 “근거 모음”으로 LLM에 주면, LLM이 출처 번호를 붙여 답한다.'))
add(li('질문 유형: 세부 질문 6개에 수치 비교용 “비슷한 과거 사례”를 더해 설계하였고, 시험 중 “현재 상태와 제한수위 비교”, “기간 내 종합”, “범위 밖”을 추가하여 임시로 10개를 두었다. 이 분류 체계 자체가 검토 대상이다.'))
add(li('조회와 계산은 LLM이 아닌 규칙이 하도록 하였다. 값이 정확하고 확인 가능해야 하기 때문이며, 시험에서 LLM이 직접 계산한 값이 틀린 경우가 있었다.'))
add(li('사용 모델: Qwen3-8B(80억 매개변수 모델)를 AWQ 방식으로 압축하여 vLLM 서버에서 실행하였다.'))

# ---------------------------------------------------------------- 3
add(h1('3. 사용한 데이터', pagebreak=False))
add(table([
    ['자료', '출처', '내용과 예', 'KG에서의 쓰임'],
    ['방류 승인 기록', '한강홍수통제소(공공데이터포털)',
     '• 충주·소양강·횡성·광동 4개 댐의 방류 승인 80건 (2010-09 ~ 2021-07)\n• 표 파일, 한 행이 승인 한 건이며 비고란에 “이내 탄력적 조정” 같은 짧은 문장이 있음\n• 예) 충주댐 승인 1368번, 2012-08-24 승인', '승인, 운영행위'],
    ['수문기상 시간 자료', 'K-water MyWater',
     '• 4개 댐의 시간별 측정값 약 50.8만 줄 (2010-08 ~ 2026-09)\n• 변수: 수위, 저수량, 강우량, 유입량, 총방류량, 저수율\n• 예) 소양강댐 2017-08-25 15:00, 수위 192.53 EL.m(해발 높이 m), 유입량 1027.58 CMS(초당 ㎥), 총방류량 523.33 CMS', '측정자료 저장소 (KG에는 찾아갈 번호만)'],
    ['홍수기 제한수위', '연계운영규정 별표3(법제처)',
     '• 홍수기에 넘기지 않도록 정한 수위\n• 충주 138.0, 소양강 190.3, 횡성 178.2 EL.m (광동댐은 없음)\n• 선 문자로 그린 표가 들어 있는 법령 텍스트', '운영기준, 문서 저장소(원문 10조각)'],
], [1.4, 1.7, 5.0, 1.9]))
add(li('자료를 Ontology의 개체 6종류와 관계 9종류에 맞추어 구조화하였다. 승인 한 건은 “승인 → 허가한 운영행위 → 댐”, “댐 → 수위 상태 → 측정자료 저장소”, “댐 ← 제한수위 ← 별표3”으로 이어진다(4.1의 그림 4).'))
add(li('실제 운영 기록은 공개되어 있지 않아, 운영행위는 승인 비고와 측정된 방류량 변화에서 규칙으로 구성하였다. 규칙(분류, 시각)은 연구자가 정한 임시 기준이다.'))

# ---------------------------------------------------------------- 4
add(h1('4. 시험 결과 (예비)', pagebreak=False))
add(h2('4.1 지식그래프 구축'))
add(table([
    ['결과', '의미와 예'],
    ['개체 273개\n관계 457개',
     '• 개체는 KG의 점, 관계는 점 사이의 선이다.\n• 개체 예: 충주댐(댐 4개 중 하나), 승인 1368(승인 80건 중 하나), 탄력적 방류(운영행위 68개 중 하나)\n• 관계 예: “승인 1368 → 허가 → 탄력적 방류”, “승인 1368 → 대상 댐 → 충주댐”\n• 개체 내역: 댐 4, 수문기상 상태 24(댐 4개 × 변수 6개, 예: 충주댐_수위), 승인 80, 운영행위 68, 운영기준 3(광동댐 제외), 근거자료 94\n• 관계 중 202개는 각 개체가 어떤 근거자료에서 왔는지를 가리킴'],
    ['외부 저장소',
     '• 측정자료 저장소: 시간별 측정값 508,246줄 (한 줄은 댐 하나의 한 시각 값, 예: 소양강댐 2017-08-25 15:00의 수위·유입량·방류량)\n• 문서 저장소: 별표3 원문 10조각 (현행 1개, 과거 개정판 9개)\n• KG에는 값 대신 찾아갈 번호(측정소 번호, 조각 번호)만 있음'],
    ['구조 검증',
     '• KG가 설계대로 만들어졌는지 5가지를 검사하였고, 어긋난 곳은 모두 0건이었다.\n• 검사 예: 모든 관계의 양쪽 끝 개체가 실제로 존재하는가, 승인마다 승인일이 있는가\n• 그 밖의 예: 날짜가 “2012-08-24” 형식인가, 모든 승인·운영행위가 근거자료에 이어지는가, 승인에서 댐으로 바로 가는 길과 운영행위를 거쳐 가는 길이 같은 댐을 가리키는가\n• 세부 질문 6개 각각에 대해 KG에서 답을 찾아갈 경로가 있는지 확인하였고, 과거 운영행위를 묻는 질문 하나만 “부분 가능”이었다.\n• 운영행위가 실제 기록이 아니라 승인에서 구성한 것이어서 실제 수행 여부는 확인할 수 없기 때문이다.'],
    ['점검 중 발견·수정',
     '• 이전 승인을 변경하는 성격의 승인 6건(예: 승인 1369)은 연결된 운영행위가 없었다.\n• “댐 → 운영행위 → 승인” 순서로 찾으면 80건 중 74건만 찾을 수 있었다.\n• 승인과 댐을 바로 잇는 관계(승인 → 대상 댐)를 추가하여 80건 모두 찾을 수 있게 하였다. (관계 종류 8개 → 9개)'],
], [1.9, 8.1]))
if USE_FIG2:
    add(image_w('fig2', FIG2, 1500, 1515, 'Figure 4 KG 예시', 0.78))
    add(caption('그림 4. 충주댐 승인 1368번 한 건의 KG 일부(회색 화살표는 근거자료를 가리키는 관계, 초록 파선은 KG 밖 저장소를 찾아가는 번호).'))
add(h2('4.2 질문에서 답변까지: Qwen3-8B 시험'))
add(li('질문 10개를 한 번씩 실행하였다. 아래는 현재 상태와 제한수위 확인, 비슷한 과거 사례의 승인·운영행위 조회, 승인량 대비 방류량 비교를 모두 포함하는 질문 하나의 전 과정이다. 오른쪽 열은 값의 의미이다.'))
t4 = TR('m04')
assert '67.4%' in t4['bundle'] and '0.223' in t4['bundle'] and '1011.2' in t4['bundle']
add(table([
    ['단계', '실제 내용', '값의 의미'],
    ['질문', QD['m04']['question'], '현재 상태, 제한수위, 비슷한 과거 사례, 승인량 대비 방류량을 한 번에 묻는 질문'],
    ['① LLM 질문 해석', t4['intent_raw'], '• 질문 유형은 비슷한 과거 사례(SIMILAR), 댐은 소양강댐\n• 보여 줄 사례 수(k)는 1: 질문에 없었는데 LLM이 채움'],
    ['② 현재 상태', '2026-09-28 23:00, 수위 185.2644 EL.m', '저장된 자료 중 가장 최근 시각(실시간 아님)을 “현재”로 사용'],
    ['② 제한수위 비교', '제한수위 190.3 EL.m, 차이 -5.04 m', '현재 수위가 제한수위보다 5.04 m 낮음 (185.2644 − 190.3)'],
    ['③ 비슷한 과거 사례 선택', '2017-08-25 15:00, 거리 0.223', '• 수위와 유입량이 현재와 얼마나 비슷한지 잰 값 (0이면 완전히 같고 클수록 다름)\n• 후보 4개 중 현재와 가장 가까운 시점'],
    ['④ 그 사례의 승인·운영행위', '운영행위 탄력적 방류(OPR:2754:2), 승인 APR:2754, 승인 방류량 1500 ㎥/s', '그 시각의 방류 운영행위와 이를 허가한 승인'],
    ['⑤ 승인량 대비 방류량', '사례 전후 시간 중 최대 총방류량 1011.2 CMS는 승인량의 67.4%', '승인된 방류량의 약 3분의 2를 실제로 방류 (1011.2 ÷ 1500)'],
    ['⑥ LLM 답변', t4['answer'].replace('**', ''), '결과를 “근거 모음”으로 받아 출처 번호([CRI:CR-01] 등)를 붙여 작성'],
], [1.7, 4.5, 3.8]))
add(li('답변의 수치와 출처 번호는 근거 모음과 일치하였다.'))
add(li('사례를 1개만 보여 준 것은 LLM이 사례 수를 1로 채웠기 때문이다.'))
add(li('답변의 “+7.27 m”(사례 수위 192.53 − 현재 수위 185.2644)는 근거 모음에 없어 LLM이 직접 계산한 값이다. 계산은 맞았으나 원래 규칙이 해야 하는 일이다.'))
add(li('10개 질문 전체의 결과는 아래 표와 같다.'))
add(li('질문 유형 분류: ① 단계에서 LLM이 고른 유형이 기대한 유형과 같은지 여부이다. 판정: 사람이 답변을 근거 모음과 대조하여 읽고 정한 것이다.'))
add(li('CURRENT: 현재 상태와 제한수위 비교, INTEGRATED: 기간 내 운영·승인·상태·근거 종합, SIMILAR: 비슷한 과거 사례'))
add(table([
    ['질문(요약)', '질문 유형 분류', '판정', '무엇이 맞고 틀렸나(예)'],
    ['소양강·충주·광동 현재 수위와 제한수위 비교(3개)', 'CURRENT, 3개 모두 기대와 같음', '맞음', '• 예) 소양강댐 현재 수위 185.2644 EL.m, 제한수위 190.3 EL.m가 근거 모음과 일치\n• 광동댐은 제한수위가 없어 “자료에 없음”이라고 정확히 답함'],
    ['횡성 2020-08 운영·승인·수위·근거 정리', 'INTEGRATED', '대체로 맞음', '• 수치는 일치\n• 운영행위 시각은 연구자가 정한 임시 기준인데 “승인된 시각”처럼 표현함'],
    ['충주 방류 전 승인과 공식 근거', 'INTEGRATED', '오류', '• 방류의 근거(승인 기록)와 제한수위의 근거(별표3)를 서로 바꾸어 연결함'],
    ['소양강, 광동 비슷한 과거 사례(2개)', 'SIMILAR', '대체로 맞음', '• 수치는 일치\n• 질문에 없는 사례 수를 LLM이 정함, 수위 차를 직접 계산함, 수위를 소수 15자리까지 출력함'],
    ['충주 비슷한 사례의 승인·방류·수위 비교', 'SIMILAR', '오류', '• 사례의 값이 아니라 현재 값을 사례 값처럼 씀\n• 증가율을 잘못 계산함'],
    ['충주 승인량과 실측 방류량의 차이', 'INTEGRATED', '오류', '• 비율(예: 67.4%)을 “차이”라고 서술함\n• 방류 시점보다 나중에 승인된 상한값을 비교에 사용함'],
    ['소양강·충주 중 제한수위에 더 가까운 댐', 'CURRENT (기대: 범위 밖)', '실패', '• 두 댐 비교는 지원하지 않는 질문임\n• LLM이 “dam” 항목을 두 번 쓴 형식으로 출력하여 프로그램이 마지막 값만 읽고 한 댐 질문으로 처리함'],
], [3.0, 1.9, 1.0, 4.1]))
add(h2('4.3 확인된 것과 한계'))
add(li('확인된 것: 질문 해석 → KG·저장소 조회 → 출처 번호가 붙은 답변까지 전 과정이 동작하였다.'))
add(li('확인된 것: 질문 유형 분류는 10개 중 9개가 기대와 같았다(어긋난 1개는 위 표의 마지막 질문). 단순한 질문은 정확히 답하였다.'))
add(li('문제의 원인(규칙 쪽): 방류 후에 승인된 상한값을 비교에 쓴 것, 근거 모음에 계산값이 없던 것 등은 수정하였으나 재시험은 하지 않았다.'))
add(li('문제의 원인(LLM 쪽): 질문에 없는 값(사례 수)을 임의로 채움, 같은 항목을 두 번 쓰는 출력 형식 오류, 비슷한 개념의 혼동(비율과 차이, 승인 근거와 제한수위 근거)'))
add(li('한계: 질문 10개, 작은 모델, 1회 실행이다.'))
add(li('한계: 같은 LLM에 표 데이터를 그대로 주는 방식(비교 기준)과의 비교가 없어, 우리 구성이 더 낫다고 말할 수 없다.'))
add(li('한계: 운영행위는 실제 기록이 아니라 승인에서 구성한 추정이다.'))

# ---------------------------------------------------------------- 5
add(h1('5. 우리 구성에 대한 의견 요청', pagebreak=False))
add(table([
    ['주제', '지금 해 본 것과 묻고 싶은 것'],
    ['질문 해석', '• LLM 하나가 질문 유형 10개 중 하나를 정해진 형식(JSON)으로 출력해 보았다.\n• 한 질문에 여러 유형이 섞일 때의 분류 체계\n• 규칙이나 학습한 분류기와의 병행\n• 출력 형식을 강제하는 방법'],
    ['답변 검증', '• “근거 안에서만 답하라” 등의 규칙을 프롬프트에 넣었으나 개념 혼동이 남았다.\n• 답변의 숫자와 출처 번호를 근거 모음과 자동으로 대조하는 방법\n• 계산을 LLM에 어디까지 맡길지'],
    ['검색 설계', '• 질문 유형별로 정해 둔 조회문으로 KG를 조회하고, 문서는 조각 번호로 찾아 보았다.\n• LLM이 조회문(Cypher)을 직접 쓰게 할지\n• 문서가 늘면 의미 유사도로 찾는 벡터 검색을 언제 더할지\n• 수치로 된 상태에서 비슷한 과거 사례를 찾는 방법'],
    ['평가', '• 지금은 사람이 읽고 판정하였다.\n• 같은 LLM에 표 데이터를 그대로 주는 비교 기준\n• 정답 질문 세트\n• 평가 지표(예: 답변 수치가 근거 모음과 일치하는 비율, 출처 번호를 제대로 단 비율)'],
    ['모델·서버', '• Qwen3-8B-AWQ를 여러 사람이 함께 쓰는 GPU(남은 메모리 약 11.7GB)에서 실행하였고, 질문 하나에 9~97초 걸렸다.\n• 더 큰 32B 모델은 메모리 부족으로 실패하였다.\n• 적합한 모델 크기와 응답 시간을 줄이는 방법'],
    ['데이터 확장', '• 현재는 저장해 둔 자료의 가장 최근 시각을 “현재”로 사용한다.\n• 실시간 자료 연결\n• 실제 운영 기록 확보\n• 댐과 문서를 늘릴 때 생길 병목'],
], [1.4, 8.6]))
add(li('시험 질문 전문, 프롬프트 전문, 구축 단계별 상세(근거 문헌 포함)는 요청 시 별도로 제공한다.'))

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
