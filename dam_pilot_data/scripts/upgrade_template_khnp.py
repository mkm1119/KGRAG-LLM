#!/usr/bin/env python3
"""최종보고서 템플릿에 발주처 보고서 양식을 반영한다(한 번만 실행).
발주처 양식(hwp)에서 읽은 값: 글꼴 한양신명조, 본문 12pt, 큰 제목 15pt 굵게, 줄간격 160%,
용지 여백(왼쪽 15, 오른쪽 12, 위 15, 아래 15, 머리말 30, 꼬리말 0, 제본 8mm), 목차·표 목차·그림 목차, 1장 서론, 결론, 참고문헌, 부록.
바꾸는 것: 글꼴과 크기, 줄간격, 문단 보호(문단이 쪽 사이에서 나뉘지 않음), 용지 여백, 장 번호(서론이 1장), 결론 장, 표 목차·그림 목차 자리.
사용: python3 dam_pilot_data/scripts/upgrade_template_khnp.py
"""
import os, re, shutil, sys, zipfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from final_report_lib import TEMPLATE, _top_paragraphs, text_of, H1, H2, BLANK, TOC1, TOC2, _p

src = TEMPLATE.replace('.hwpx', '_v1.hwpx')
if not os.path.exists(src):
    shutil.copy(TEMPLATE, src)                       # 이전 템플릿을 남겨 둔다
z = zipfile.ZipFile(src)
head = z.read('Contents/header.xml').decode('utf8')
sec = z.read('Contents/section0.xml').decode('utf8')

# ---------------------------------------------------------------- header.xml: 글꼴, 크기, 줄간격, 문단 보호
head = head.replace('한양중고딕', '한양신명조')
SIZE = {22: 1500, 17: 1300, 23: 1200, 24: 1200, 25: 1200, 26: 1200, 28: 1000}          # 글자 모양 번호 -> 크기(1/100 pt)
for cid, h in SIZE.items():
    head, n = re.subn(r'(<hh:charPr id="%d" height=")\d+(")' % cid, r'\g<1>%d\2' % h, head)
    assert n == 1, cid


def para(pid, fn):
    global head
    m = re.search(r'<hh:paraPr id="%d".*?</hh:paraPr>' % pid, head, re.S)
    head = head[:m.start()] + fn(m.group(0)) + head[m.end():]


for pid in range(33, 39):                            # 제목과 본문의 줄간격을 160%로
    para(pid, lambda b: re.sub(r'(<hh:lineSpacing type="PERCENT" value=")\d+', r'\g<1>160', b))
for pid in (38, 39, 40, 41, 47, 48):                 # 본문, □, ◦, -, 주·자료, 참고문헌: 문단 보호
    para(pid, lambda b: b.replace('keepLines="0"', 'keepLines="1"'))

# ---------------------------------------------------------------- section0.xml: 용지 여백
sec, n = re.subn(r'<hp:margin header="\d+" footer="\d+" gutter="\d+" left="\d+" right="\d+" top="\d+" bottom="\d+"/>',
                 '<hp:margin header="8504" footer="0" gutter="2268" left="4252" right="3402" top="4252" bottom="4252"/>', sec)
assert n == 1

# 장 번호: 서론이 1장이 되므로 과업 항목의 장을 하나씩 뒤로 민다
OLD = ['1. 국내외 기술 트렌드 조사', '1.1 수자원 분야 사례 조사', '1.2 국내 운영 여건 조사', '1.3 적용 기술요소 및 모델 제안',
       '2. LLM 활용 데이터 파이프라인 조사', '2.1 수집 경로 조사', '2.2 온톨로지·메타데이터 설계방안 조사', '2.3 RAG-LLM 통합 파이프라인(안) 제시',
       '3. sLLM 후보군 평가 방향', '3.1 후보 모델 조사', '3.2 모델 구조 및 특성 검토', '3.3 후보군 적용방안 제시',
       '4. 도메인 특화 성능 향상 전략', '4.1 RAG 기반 적용방안 조사', '4.2 경량 미세조정 방식 검토', '4.3 성능 향상 전략 제시',
       '5. 연구개발 추진 방향 및 로드맵(안)']
for t in reversed(OLD):
    new = str(int(t[0]) + 1) + t[1:]
    sec = sec.replace('<hp:t>%s</hp:t>' % t, '<hp:t>%s</hp:t>' % new)
for a, b in (('(1~2번)', '(2~3장)'), ('1번과 2번을', '2장과 3장을'), ('(3~4번)', '(4~5장)'), ('3번과 4번을', '4장과 5장을'),
             ('18pt 굵게', '15pt 굵게'), ('11.5pt 굵게', '12pt 굵게'), ('11pt 굵게', '12pt 굵게'), ('<hp:t>11pt</hp:t>', '<hp:t>12pt</hp:t>'),
             ('<hp:t>9pt</hp:t>', '<hp:t>10pt</hp:t>'), ('줄간격 180%, 첫 줄 들여쓰기', '줄간격 160%, 첫 줄 들여쓰기'),
             ('글꼴은 모두 한양중고딕입니다.', '글꼴은 모두 한양신명조입니다(발주처 보고서 양식).'),
             ('용지 여백은 월간 진도보고서와 같습니다.', '용지 여백과 본문 크기(12pt), 줄간격(160%)은 발주처 보고서 양식과 같습니다. 문단은 쪽 사이에서 나뉘지 않도록 문단 보호를 적용하였습니다.')):
    assert a in sec, a
    sec = sec.replace(a, b)

sp = _top_paragraphs(sec)
pre, post = sec[:sp[0][0]], sec[sp[-1][1]:]
ps = [sec[a:b] for a, b in sp]
is_h1 = lambda p: 'styleIDRef="34"' in p[:200]
toc = [i for i, p in enumerate(ps) if text_of(p).startswith('목    차')][0]
body = [i for i, p in enumerate(ps) if i > toc and is_h1(p) and text_of(p).startswith('2. 국내외')][0]
# 쪽 번호를 1부터 새로 매기는 조판 부호를 2장 제목에서 떼어 서론 제목으로 옮긴다
CTRL = '<hp:ctrl><hp:pageNum pos="BOTTOM_CENTER" formatType="DIGIT" sideChar="-"/></hp:ctrl><hp:ctrl><hp:newNum num="1" numType="PAGE"/></hp:ctrl>'
assert CTRL in ps[body]
ps[body] = ps[body].replace(CTRL, '')
intro_h1 = H1('1. 서론').replace('<hp:t>', CTRL + '<hp:t>', 1)
intro = [intro_h1]
for t in ('1.1 과업의 배경 및 목적', '1.2 과업 범위', '1.3 추진 경위'):
    intro += [H2(t), BLANK(), BLANK()]
ref = [i for i, p in enumerate(ps) if i > body and is_h1(p) and text_of(p).startswith('참고문헌')][0]
concl = [H1('7. 결론'), BLANK()]
# 목차: 조립할 때 본문의 제목과 표·그림 제목으로 다시 만든다. 템플릿에는 자리만 둔다.
toc_entries = [TOC1('1. 서론'), TOC2('1.1 과업의 배경 및 목적'), TOC2('1.2 과업 범위'), TOC2('1.3 추진 경위')]
for t in OLD:
    new = str(int(t[0]) + 1) + t[1:]
    toc_entries.append(TOC1(new) if new[1:3] == '. ' else TOC2(new))
toc_entries += [TOC1('7. 결론'), TOC1('참고문헌'), TOC1('부록'),
                _p('표 목 차', 33, 34, 22, 1), TOC2('표 1.1 ○○○○○'), _p('그림 목차', 33, 34, 22, 1), TOC2('그림 1.1 ○○○○○')]
ps = ps[:toc + 1] + toc_entries + intro + ps[body:ref] + concl + ps[ref:]
strip = lambda p: p if ('<hp:tbl' in p or '<hp:pic' in p) else re.sub(r'<hp:linesegarray>.*?</hp:linesegarray>', '', p, flags=re.S)
out_sec = pre + ''.join(strip(p) for p in ps) + post

with zipfile.ZipFile(TEMPLATE, 'w') as zo:
    zo.writestr(zipfile.ZipInfo('mimetype'), z.read('mimetype'), compress_type=zipfile.ZIP_STORED)
    for it in z.infolist():
        if it.filename == 'mimetype':
            continue
        data = {'Contents/header.xml': head.encode('utf8'), 'Contents/section0.xml': out_sec.encode('utf8')}.get(it.filename, z.read(it.filename))
        zo.writestr(it.filename, data, compress_type=zipfile.ZIP_DEFLATED)
print('템플릿 갱신:', TEMPLATE)
