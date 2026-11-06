"""질문 세트 v2 = v1(50개) + 태스크 후보 중 v1에 없던 42개 태스크의 질문 + 예전 질문 묶음(중복 제외). question_set_v2.json을 만든다.

태스크 82개가 모두 질문을 하나 이상 갖는다. expect는 v1과 같고, 옛 KG 구조를 전제한 질문은 obsolete로 둔다.
extension 코드: O1 제원, O2 홍수기 기간, O3 규정 조문, O4 수계 관계 / T1 기간 통계, T2 예년 비교, T3 여러 댐 비교,
T4 승인 대비 실측, T5 결측·이상치, T6 사상 추출, T7 문서 초안, T8 번호로 원문 조회 / P1~P4 공개자료 추가 수집
"""
import csv, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
CH, SY, HS, GD = '충주댐', '소양강댐', '횡성댐', '광동댐'
P = lambda s, e: {'start': s, 'end': e}
A1to5 = ['CQ1', 'CQ2', 'CQ3', 'CQ4', 'CQ5']

# ---- 태스크 중 v1에 없던 42개 (요청 예를 실제 댐·날짜로)
NEW = [
 ('A06', '충주댐 유역에 지금까지 비 얼마나 왔어?', 'extend', 'P1', '유역 강우 미수집(댐 지점 강우만 있음)'),
 ('A08', '충주댐 하류 목계교 수위 어때?', 'extend', 'P2', '하천 수위 미수집'),
 ('B06', '충주댐에서 방류하면 하류 여주까지 몇 시간 걸려?', 'refuse', None, '내부 자료'),
 ('B07', '충주댐 하류가 홍수 경보 단계야?', 'extend', 'P2', '경보 기준 미수집'),
 ('B08', '충주댐 수문 2m 열면 방류량이 얼마야?', 'refuse', None, '내부 자료'),
 ('B10', '소양강댐 홍수기 끝나면 언제쯤 상시만수위 돼?', 'refuse', None, '예측·모형'),
 ('C03', '충주댐 방류 승인 요청서 초안 써줘', 'refuse', None, '양식'),
 ('C05', '충주댐 방류하면 어디에 연락해야 해?', 'refuse', None, '내부 연락 체계'),
 ('D02', '횡성댐 지금 물로 며칠 공급할 수 있어?', 'refuse', None, '공급량 자료'),
 ('D04', '충주댐 하천유지용수 기준이 얼마야?', 'extend', 'P3', '기준 미수집'),
 ('D05', '광동댐 이번 달 용수 공급 계획대로 됐어?', 'refuse', None, '내부 자료'),
 ('D06', '소양강댐은 예전에 가뭄 때 저수율이 얼마까지 내려갔어?', 'extend', 'T6', '저수율 최저 사상'),
 ('E02', '충주댐 지금 발전 방류량 얼마야?', 'refuse', None, '내부 자료'),
 ('E03', '충주댐 발전기 몇 대 돌고 있어?', 'refuse', None, '내부 자료'),
 ('E05', '충주댐 총방류량 중 발전 방류가 얼마야?', 'refuse', None, '내부 자료'),
 ('E06', '충주댐 지난달 발전기 정지 이력 보여줘', 'refuse', None, '내부 자료'),
 ('E07', '충주댐 오늘 발전 운영 요약해줘', 'refuse', None, '내부 자료'),
 ('F04', '연계운영규정 이번 개정에서 바뀐 게 뭐야?', 'extend', 'P4', '개정 이력 일부만 있음(criterion_version_history)'),
 ('F06', '소양강댐 계획홍수위랑 상시만수위 알려줘', 'extend', 'O1', '제원'),
 ('F07', '방류 전에 해야 할 절차가 뭐야?', 'refuse', None, '내부 매뉴얼'),
 ('G03', '충주댐 수위계 두 개 값이 왜 달라?', 'refuse', None, '계측 태그'),
 ('G04', '충주댐 이번 달 누수량 기준 넘은 적 있어?', 'refuse', None, '안전 계측'),
 ('G06', '충주댐 수문 설비 마지막 점검이 언제야?', 'refuse', None, '점검 기록'),
 ('G07', '충주댐 어제 수문 몇 번 열었어?', 'refuse', None, '설비 기록'),
 ('G08', '수위계 고장 나면 어떻게 해?', 'refuse', None, '내부 매뉴얼'),
 ('H03', '2020년 8월 충주댐 방류 결과 보고 써줘', 'extend', 'T7', '근거는 CQ2~CQ4'),
 ('H04', '충주댐 2026년 9월 운영 실적 요약해줘', 'extend', 'T1', '기간 통계 + 문서'),
 ('H05', '충주댐 오늘 야간 근무 인수인계 요약해줘', 'extend', 'T7', '근무 기록은 없음, 수문 상태만 가능'),
 ('H06', '충주댐 지금 상황 본사 보고용으로 세 줄 요약해줘', 'extend', 'T7', '근거는 CQ1(+CQ5)'),
 ('H07', '이 메모를 운영 일지 양식으로 바꿔줘', 'refuse', None, '입력 문서·양식'),
 ('H08', '이 보고서 수치가 맞는지 확인해줘', 'refuse', None, '입력 문서'),
 ('I04', '충주댐 2020년이랑 2011년 홍수 운영 비교해줘', 'extend', 'T6', '사상 비교(근거는 CQ2~CQ4로 일부 가능)'),
 ('I06', '충주댐은 유입량 대비 승인 방류량이 보통 어느 정도였어?', 'extend', 'T4', ''),
 ('I07', '승인 3519번 원본 기록 보여줘', 'extend', 'T8', '번호로 원문 조회(시연 화면 출처 보기로는 가능)'),
 ('J03', '충주댐 이대로면 모레 수위 얼마나 돼?', 'refuse', None, '예측·모형'),
 ('J04', '충주댐 방류 1000이랑 2000일 때 비교해줘', 'refuse', None, '모형'),
 ('J05', '충주댐 지난 홍수 때 유입 예측이 얼마나 맞았어?', 'refuse', None, '예측 이력'),
 ('J06', '홍수기 전에 점검할 것 정리해줘', 'refuse', None, '내부 매뉴얼'),
 ('J07', '충주댐 올해 운영 계획 대비 실적 어때?', 'refuse', None, '계획 자료'),
 ('K02', '2020년 8월 충주댐 방류 언론 설명자료 초안 써줘', 'extend', 'T7', ''),
 ('K03', '신입한테 홍수기 운영 기본을 설명해줘', 'extend', 'O3', '규정 조문'),
 ('K05', '2020년 8월 2일 충주댐 방류량이랑 수위 정리해줘', 'answer_now', {'intent': ['CQ2'], 'dam': CH, 'period': {'at': '2020-08-02'}}, ''),
]

# ---- 예전 질문 묶음 (원래 위치, 태스크, 질문, 기대, gold/확장, 비고). v1·위와 겹치는 것은 뺐다
OLD = [
 ('old_v3/q01', 'A01', '소양강댐 지금 수위랑 방류량이 어때?', 'answer_now', {'intent': ['CQ1'], 'dam': SY, 'period': '전체'}, ''),
 ('old_v3/q02', 'A01', '충주 댐 현재 저수율 알려줘', 'answer_now', {'intent': ['CQ1'], 'dam': CH, 'period': '전체'}, '띄어쓰기'),
 ('old_v3/q04', 'A02', '횡성댐에서 2020년 8월 4일 오후 3시 전후로 수위가 어땠는지 보고 싶어', 'answer_now', {'intent': ['CQ2'], 'dam': HS, 'period': {'at': '2020-08-04'}}, '시각 지정'),
 ('old_v3/q05', 'I01', '2020년 8월에 충주댐에서 어떤 방류 조작이 있었어?', 'answer_now', {'intent': ['CQ3'], 'dam': CH, 'period': P('2020-08-01', '2020-08-31')}, ''),
 ('old_v3/q06', 'I01', '광동댐은 2019년 9월에 어떤 식으로 방류를 운영했나요?', 'answer_now', {'intent': ['CQ3'], 'dam': GD, 'period': P('2019-09-01', '2019-09-30')}, ''),
 ('old_v3/q07', 'C01', '2020년 8월 광동댐 방류 승인 내역 알려줘', 'answer_now', {'intent': ['CQ4'], 'dam': GD, 'period': P('2020-08-01', '2020-08-31')}, ''),
 ('old_v3/q09', 'F01', '횡성댐 홍수기 제한수위는?', 'answer_now', {'intent': ['CQ5'], 'dam': HS, 'period': '전체'}, ''),
 ('old_v3/q10', 'F01', '광동댐은 지켜야 하는 제한수위가 얼마야?', 'answer_now', {'intent': ['CQ5'], 'dam': GD, 'period': '전체'}, '별표3에 없음(O1 보완)'),
 ('old_v3/q11', 'F02', '승인 3412번은 무슨 자료에 근거한 거야?', 'answer_now', {'intent': ['CQ6'], 'target': {'type': 'approval', 'id': '3412'}}, '번호 지정'),
 ('old_v3/q12', 'F02', '충주댐 수위 데이터 출처가 뭐야?', 'answer_now', {'intent': ['CQ1', 'CQ6'], 'dam': CH, 'period': '전체'}, ''),
 ('old_v3/q13', 'B04', '2017년 8월 24일부터 31일까지 소양강댐 운영 상황을 승인, 당시 상태, 기준까지 알려줘', 'answer_now', {'intent': ['CQ2', 'CQ3', 'CQ4', 'CQ5'], 'dam': SY, 'period': P('2017-08-24', '2017-08-31')}, ''),
 ('old_v3/q14', 'B04', '지금 소양강댐 상황이랑 비슷했던 과거에는 어떻게 했어?', 'answer_now', {'intent': A1to5, 'dam': SY, 'period': '전체'}, ''),
 ('old_v3/q15', 'B04', '광동댐 지금 상태랑 비슷한 과거 사례 두 개만 보여줘', 'answer_now', {'intent': A1to5, 'dam': GD, 'period': '전체'}, '개수 지정'),
 ('old_v3/q18', 'C01', '소양강댐 방류 승인 내역 알려줘', 'answer_now', {'intent': ['CQ4'], 'dam': SY, 'period': '전체'}, '기간 없음'),
 ('old_v3/q19', 'J02', '내일 충주댐 날씨 어때?', 'refuse', None, '예보 미수집'),
 ('old_v3/m01', 'B01', '지금 소양강댐 수위가 제한수위보다 얼마나 낮아? 현재 상태를 기준이랑 같이 알려줘', 'answer_now', {'intent': ['CQ1', 'CQ5'], 'dam': SY, 'period': '전체'}, ''),
 ('old_v3/m03', 'B04', '지금 충주댐 상황이랑 비슷했던 과거 사례를 찾아서, 그때 어떤 승인이 있었고 어떤 방류를 했는지, 제한수위에 비해 수위는 어땠는지 비교해줘', 'answer_now', {'intent': A1to5, 'dam': CH, 'period': '전체'}, ''),
 ('old_v3/m04', 'C02', '소양강댐 지금 상태를 제한수위와 비교하고, 비슷했던 과거 사례에서 승인된 방류량 대비 실제 방류량이 어땠는지 알려줘', 'extend', 'T4', ''),
 ('old_v3/m05', 'C02', '2020년 8월 2일부터 10일 사이 충주댐에서 승인된 방류량과 실제 측정된 방류량이 얼마나 차이 났는지, 그때 수위가 제한수위를 넘었는지 알려줘', 'extend', 'T4', ''),
 ('old_v3/m06', 'H02', '횡성댐 2020년 8월 방류 운영을 승인 내용과 당시 수위, 제한수위, 근거까지 한 번에 정리해줘', 'answer_now', {'intent': ['CQ2', 'CQ3', 'CQ4', 'CQ5', 'CQ6'], 'dam': HS, 'period': P('2020-08-01', '2020-08-31')}, ''),
 ('old_v3/m07', 'B04', '광동댐 현재 상태와 비슷한 과거 사례에서의 승인과 방류 내용을 알려줘. 제한수위는 얼마나 되는지도', 'answer_now', {'intent': A1to5, 'dam': GD, 'period': '전체'}, ''),
 ('old_v3/m08', 'B01', '광동댐 현재 수위가 제한수위에 비해 어때?', 'answer_now', {'intent': ['CQ1', 'CQ5'], 'dam': GD, 'period': '전체'}, '기준 없음(O1 보완)'),
 ('old_v3/m09', 'F02', '충주댐이 2020년 8월에 방류하기 전에 어떤 승인을 받았고 그 방류의 공식 근거는 뭐야?', 'answer_now', {'intent': ['CQ3', 'CQ4', 'CQ6'], 'dam': CH, 'period': P('2020-08-01', '2020-08-31')}, ''),
 ('old_v3/m10', 'A07', '소양강댐이랑 충주댐 중 지금 어느 쪽이 제한수위에 더 가까워?', 'extend', 'T3', ''),
 ('qa_pilot/Q01', 'C01', '충주(승인파일 관측소코드 1003110)의 2020년 방류 승인 record는 몇 건이며 각각 접수일자·방류시작시간·접수방류량은?', 'answer_now', {'intent': ['CQ4'], 'dam': CH, 'period': P('2020-01-01', '2020-12-31')}, '접수일자는 KG에 없음(10/30 검토할 점 1)'),
 ('qa_pilot/Q02', 'F02', '소양강댐의 홍수기 제한수위 기준값과 그 값이 실린 문서는?', 'answer_now', {'intent': ['CQ5', 'CQ6'], 'dam': SY, 'period': '전체'}, '서버 실행 q2와 같은 뜻'),
 ('qa_pilot/Q03', 'I07', '승인 순차번호 3519의 비고 원문은?', 'extend', 'T8', ''),
 ('qa_pilot/Q04', '-', 'MyWater 충주댐(1003110)에 조회 목록으로 연결된 관측소는 몇 개이며 유형별로는?', 'obsolete', None, '옛 KG(관측소 Class) 기준'),
 ('qa_pilot/Q06', 'B02', '2020-08-02 충주댐 승인 당시 적용되던 홍수기 제한수위는?', 'answer_now', {'intent': ['CQ5'], 'dam': CH, 'period': {'at': '2020-08-02'}}, '기준의 시점 버전은 KG에 없음(현재 규정 값만)'),
 ('qa_pilot/N01', 'I02', '충주댐에서 2020년 8월 초 방류 승인이 났을 때 그 무렵 저수위·유입량·방류량은 어땠나?', 'answer_now', {'intent': ['CQ2', 'CQ3', 'CQ4'], 'dam': CH, 'period': P('2020-08-01', '2020-08-10')}, '"8월 초" 해석'),
 ('qa_pilot/N02', 'F05', '횡성댐의 2020년 방류 승인은 어떤 운영기준을 근거로 한 것인가?', 'answer_now', {'intent': ['CQ4', 'CQ5'], 'dam': HS, 'period': P('2020-01-01', '2020-12-31')}, '승인-기준 관계는 KG에 없음. 단정하지 않아야 함'),
 ('qa_pilot/N03', 'F01', '광동댐 방류 승인 시 참고할 운영기준(시설별 값)이 있나?', 'answer_now', {'intent': ['CQ5'], 'dam': GD, 'period': '전체'}, '없음(O1 보완)'),
 ('qa_pilot/N04', 'C02', '충주댐 2020-08-02 승인의 접수방류량(3000)만큼 실제로 방류가 이루어졌나?', 'extend', 'T4', ''),
 ('server/q1', 'B04', '충주댐 현재 수문, 기상 데이터를 가져오고 제한수위와 비교한 후에, 이와 비슷한 수문상태일 때의 승인 및 운영 행위가 있었으면 알려줘.', 'answer_now', {'intent': A1to5, 'dam': CH, 'period': '전체'}, '10/16 서버 실행 q1'),
 ('server/q3', 'I02', '2020년 8월 충주댐 방류 승인과 운영행위, 그때의 수문 상태를 알려줘.', 'answer_now', {'intent': ['CQ2', 'CQ3', 'CQ4'], 'dam': CH, 'period': P('2020-08-01', '2020-08-31')}, '10/16 서버 실행 q3'),
]

v1 = json.load(open(os.path.join(HERE, 'question_set_v1.json'), encoding='utf-8'))
tasks = {t['번호']: t for t in csv.DictReader(open(os.path.join(HERE, '..', '..', 'lab_meeting', 'task_candidates', '태스크후보_v1.csv'), encoding='utf-8-sig'))}
out = []
for q in v1:
    out.append(dict(q, source='v1'))
for t, q, e, g, note in NEW:
    out.append({'task': t, 'question': q, 'expect': e, 'gold': g if isinstance(g, dict) else None, 'extension': g if isinstance(g, str) else None, 'note': note, 'source': 'task'})
for src, t, q, e, g, note in OLD:
    out.append({'task': t, 'question': q, 'expect': e, 'gold': g if isinstance(g, dict) else None, 'extension': g if isinstance(g, str) else None, 'note': note, 'source': src})
for n, q in enumerate(out, 1):
    q['id'] = 'q%03d' % n
    q['task_name'] = tasks[q['task']]['태스크'] if q['task'] in tasks else ''
assert len({q['question'] for q in out}) == len(out), '중복 질문'
missing = sorted(set(tasks) - {q['task'] for q in out})
assert not missing, missing
json.dump(out, open(os.path.join(HERE, 'question_set_v2.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
from collections import Counter
print(len(out), dict(Counter(q['expect'] for q in out)), dict(Counter(q['source'].split('/')[0] for q in out)))
print(dict(sorted(Counter(q['extension'] for q in out if q['extension']).items())))
