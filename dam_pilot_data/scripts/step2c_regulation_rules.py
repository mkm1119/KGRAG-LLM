#!/usr/bin/env python3
"""STEP 2C-4: 수집한 법령·규정에서 방류·승인 관련 조문을 원문 그대로 추출하고, 규칙 속성을 붙여 표로 만든다. stdlib만 사용.

- verbatim(원문)은 법제처 XML에서 그대로 가져온다(개정 표시와 중복 항번호만 정리).
- subject / condition / requirement / rule_type 등 구조화 칸은 Claude가 조문을 읽고 적은 주석이며, 사람 검토가 필요하다.
출력: 03_normalized/regulation_rules_v1.csv
"""
import csv, glob, os, re
import xml.etree.ElementTree as ET

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
N = os.path.join(ROOT, '03_normalized')
L = os.path.join(ROOT, '01_raw/Law')


def clean(t):
    t = re.sub(r'<개정[^>]*>|<신설[^>]*>|<전문개정[^>]*>|\[[^\]]*이동[^\]]*\]', '', t)
    t = re.sub(r'([①-⑳])\s*\1', r'\1', t)
    t = re.sub(r'\b(\d+)\.\s*\1\.\s', r'\1. ', t)
    return re.sub(r'\s+', ' ', t).strip()


def load_law(path):
    r = ET.parse(path).getroot()
    arts = {}
    if r.tag == 'AdmRulService':
        for el in r.findall('조문내용'):
            t = (el.text or '').strip()
            m = re.match(r'제(\d+)조(?:의(\d+))?\(', t)
            if m:
                arts[('제%s조' % m.group(1)) + (('의' + m.group(2)) if m.group(2) else '')] = clean(t)
    else:
        for u in r.iter('조문단위'):
            if (u.findtext('조문여부') or '') != '조문':
                continue
            no, sub = u.findtext('조문번호') or '', u.findtext('조문가지번호') or ''
            t = clean(''.join(u.itertext()))
            i = t.find('제%s조' % no)
            arts[('제%s조' % no) + (('의' + sub) if sub else '')] = t[i:] if i >= 0 else t
    return arts


def pick(files, pat):
    return [f for f in files if re.search(pat, os.path.basename(f))][0]


files = glob.glob(os.path.join(L, '*.xml'))
DOCS = {
    '하천법': load_law(pick(files, r'law_\d+_하천법_시행')),
    '하천법 시행령': load_law(pick(files, r'law_\d+_하천법시행령')),
    '댐건설관리법': load_law(pick(files, r'law_\d+_댐건설관리및주변지역지원등에관한법률_시행')),
    '연계운영규정': load_law(pick(files, r'admrul_.*연계운영규정')),
}
CIRC = '①②③④⑤⑥⑦⑧⑨⑩'


def clause(doc, art, mark=None):
    t = DOCS[doc][art]
    if not mark:
        return t
    i = t.find(mark)
    if i < 0:
        return ''
    j = len(t)
    nxt = CIRC.find(mark) + 1
    if nxt < len(CIRC) and CIRC[nxt] in t[i + 1:]:
        j = t.find(CIRC[nxt], i + 1)
    return t[i:j].strip()


def item(doc, art, num):
    t = DOCS[doc][art]
    m = re.search(r'%d\.\s.*?(?=\s%d\.\s|$)' % (num, num + 1), t)
    return m.group(0).strip() if m else ''


# (rule_id, 문서, 조문, 항표시, 규칙유형, 주체, 조건, 요구·권한, 적용대상, 쓰임)
R = [
    ('R01', '하천법', '제41조', '①', '승인 요건', '댐 등의 설치자 또는 관리자', '홍수에 대비하여 댐의 저수를 방류하려는 때', '기후에너지환경부장관의 승인을 얻어야 함', '댐', 'Approval의 법적 근거'),
    ('R02', '하천법 시행령', '제48조', None, '승인 사항', '댐 등의 설치자 또는 관리자', '댐의 저수를 방류하려는 때', '방류량, 방류 시작 시각, 방류기간에 대해 승인을 받아야 함', '댐', '승인 CSV의 방류량·방류시작시간·방류기간과 대응'),
    ('R03', '하천법', '제41조', '②', '지시·명령', '하천관리청', '홍수 재해의 방지 또는 경감을 위해 긴급한 조치가 필요한 때', '댐 등의 설치자 또는 관리자에게 필요한 조치를 명할 수 있음', '댐', '방류 이유(긴급 조치 명령)'),
    ('R04', '하천법', '제41조', '③', '통지', '기후에너지환경부장관 또는 하천관리청', '제2항의 조치명령을 한 때', '내용을 중앙재난안전대책본부장에게 통지', '댐', '통지 의무'),
    ('R05', '하천법', '제39조', '③', '기록 의무', '댐 등의 설치자 또는 관리자', '상시', '댐 등의 관리 및 수문에 관한 기록을 작성·비치하고 하천관리청 요구 시 제출', '댐', '실제 운영 기록의 존재 근거'),
    ('R06', '댐건설관리법', '제7조', '①', '규정 제정', '댐관리청', '상시', '댐관리규정을 정해야 함', '댐', '댐별 관리규정의 존재 근거'),
    ('R07', '댐건설관리법', '제7조', '②', '규정 승인', '댐수탁관리자', '관리 위탁을 받은 경우', '댐관리규정을 작성하여 댐관리청의 승인을 받아야 함', '댐', '댐별 관리규정의 존재 근거'),
    ('R08', '연계운영규정', '제2조', '3호', '기간 정의', '-', '-', '홍수기: 6월 21일부터 9월 20일까지', '시설', '운영 시점이 홍수기인지 판정'),
    ('R09', '연계운영규정', '제4조', None, '규정 간 관계', '-', '-', '개별 시설의 관리규정에서 정한 사항 이외에는 이 규정을 따름', '시설', '댐별 관리규정 우선'),
    ('R10', '연계운영규정', '제6조', '②', '기준 준수·승인 요건', '시설관리자', '홍수기', '홍수기 제한수위를 준수해야 하고, 홍수조절을 위한 수문조작이 필요하면 홍수통제소장의 사전 승인을 받아야 함', '시설', 'Criterion(제한수위)과 Approval의 연결 근거'),
    ('R11', '연계운영규정', '제6조', '③', '지시', '홍수통제소장', '홍수주의보·경보 발령이 필요하거나 홍수 피해 우려가 있다고 판단할 때', '시설별 최저 운영수위까지의 저류공간을 홍수조절에 이용하는 등 필요한 조치를 지시할 수 있음', '시설', '방류 이유(홍수 대비 지시)'),
    ('R12', '연계운영규정', '제7조', '②', '지시', '홍수통제소장', '갈수상황 발생 우려', '시설물관리자에게 필요한 조치를 지시할 수 있음', '시설', '방류 이유(갈수 대응)'),
    ('R13', '연계운영규정', '제8조', None, '저수량 활용', '홍수통제소장', '하천 수질 개선(깨끗한 물 확보)', '저수량을 활용할 수 있고, 시설관리자 및 관계기관과 협의해야 함', '시설', '방류 이유(수질 개선)'),
    ('R14', '연계운영규정', '제11조', '②', '모니터링·조치', '홍수통제소장', '제6조~제8조 사항', '상시 모니터링하고 필요 시 협의하여 방류 등의 조치를 취할 수 있음', '시설', '방류 이유, 승인 주체'),
    ('R15', '연계운영규정', '제13조', '①', '실적 평가·보고', '홍수통제소장, 시설관리자', '연 1회', '댐·보 시설관리자는 월별 저수위, 유입량, 방류량, 발전량 등 운영실적을 평가 대상으로 함', '시설', '운영실적 자료 항목'),
    ('R16', '연계운영규정', '제14조', '①', '비상방류·통보', '시설관리자', '예상치 못한 기상변화, 하천의 유량 및 수질변화, 안전관리 등과 관련한 긴급한 사유', '방류량을 조정하고 그 결과를 관할 홍수통제소장에게 지체없이 통보', '시설', '방류 이유(비상), 사후 통보'),
    ('R17', '연계운영규정', '제14조', '②', '요청', '관계기관', '긴급한 사유 발생', '관할 홍수통제소장에게 비상방류를 요청할 수 있음', '시설', '방류 이유(요청)'),
    ('R18', '연계운영규정', '제14조', '③', '지시', '관할 홍수통제소장', '비상방류 요청을 받고 물수급 상황을 고려해 필요한 경우', '시설관리자에게 비상방류를 지시할 수 있고, 시설관리자는 시설사용에 지장이 없는 한 따라야 함', '시설', '방류 이유(지시)'),
]


def main():
    rows = []
    for rid, doc, art, mk, rtype, subj, cond, req, tgt, use in R:
        if mk and mk[0] in CIRC:
            v = clause(doc, art, mk)
        elif mk and mk.endswith('호'):
            v = item(doc, art, int(mk[:-1]))
        else:
            v = clause(doc, art)
        rows.append({'rule_id': rid, 'source_doc': doc, 'article': art + (mk or ''), 'verbatim': v, 'rule_type': rtype, 'subject': subj,
                     'condition': cond, 'requirement_or_power': req, 'applies_to': tgt, 'use_in_kg': use, 'verbatim_found': 'Y' if v else 'N',
                     'annotation_by': 'Claude(검토 필요)'})
    with open(os.path.join(N, 'regulation_rules_v1.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    for r in rows:
        print(r['rule_id'], r['source_doc'], r['article'], '| 원문찾음', r['verbatim_found'], '|', r['verbatim'][:90])


if __name__ == '__main__':
    main()
