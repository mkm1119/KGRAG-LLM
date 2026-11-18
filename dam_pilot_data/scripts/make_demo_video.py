# 시연 영상 후처리(1차: 화면 안내 + 첫 질문). 사용: python3 make.py <원본.mp4> <작업 폴더> <출력.mp4>
import sys, os, subprocess, math
from PIL import Image, ImageDraw, ImageFont
SRC, W, OUT = sys.argv[1:4]
FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
F = lambda s: ImageFont.truetype(FONT, s)
TOP, CH, CW, STRIP = 86, 946, 1920, 134          # 브라우저 탭·주소창 86px를 잘라내고 아래 134px에 자막
NAVY, RED = (0, 59, 113), (226, 43, 43)
def run(*a): subprocess.run(['ffmpeg', '-v', 'error', '-y', *a], check=True)
def grab(t, name):
    p = os.path.join(W, name); run('-ss', str(t), '-i', SRC, '-frames:v', '1', p)
    return Image.open(p).convert('RGB').crop((0, TOP, CW, TOP + CH))
def strip(img, cap, tag=None):                    # 1920x1080 화면 = 내용 + 자막 띠
    fr = Image.new('RGB', (CW, 1080), NAVY); fr.paste(img, (0, 0)); d = ImageDraw.Draw(fr)
    f = F(40); w = d.textlength(cap, font=f); d.text(((CW - w) / 2 + (60 if tag else 0), CH + 40), cap, font=f, fill='white')
    if tag: d.text((40, CH + 48), tag, font=F(28), fill=(157, 190, 221))
    return fr
def box(d, b, label=None, side='right'):          # 빨간 네모 + 이름표와 화살표
    x1, y1, x2, y2 = b
    for k in range(5): d.rounded_rectangle((x1 - k, y1 - k, x2 + k, y2 + k), radius=10, outline=RED)
    if not label: return
    f = F(34); tw = d.textlength(label, font=f); cy = (y1 + y2) / 2
    if side == 'right': lx = x2 + 110; ax1, ax2 = lx - 6, x2 + 12
    else: lx = x1 - 110 - tw - 36; ax1, ax2 = lx + tw + 42, x1 - 12
    d.rounded_rectangle((lx, cy - 32, lx + tw + 36, cy + 32), radius=12, fill=RED); d.text((lx + 18, cy - 22), label, font=f, fill='white')
    d.line((ax1, cy, ax2, cy), fill=RED, width=7); s = 1 if ax2 > ax1 else -1
    d.polygon([(ax2, cy), (ax2 - 22 * s, cy - 14), (ax2 - 22 * s, cy + 14)], fill=RED)
def zoom(img, x0, y0, w):
    h = round(w * CH / CW); return img.crop((x0, y0, x0 + w, y0 + h)).resize((CW, CH), Image.LANCZOS), CW / w
def zb(b, x0, y0, s): return tuple(round(v) for v in ((b[0] - x0) * s, (b[1] - y0) * s, (b[2] - x0) * s, (b[3] - y0) * s))
segs = []
def still(fr, sec, name):
    p = os.path.join(W, name + '.png'); fr.save(p); o = os.path.join(W, name + '.mp4')
    run('-loop', '1', '-t', str(sec), '-i', p, '-r', '30', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'veryfast', o); segs.append(o)
def clip(t1, t2, cap, name, speed=1, tag=None):
    ov = Image.new('RGBA', (CW, 1080), (0, 0, 0, 0)); st = strip(Image.new('RGB', (CW, CH)), cap, tag).crop((0, CH, CW, 1080)); ov.paste(st, (0, CH)); p = os.path.join(W, name + '_ov.png'); ov.save(p)
    o = os.path.join(W, name + '.mp4')
    run('-ss', str(t1), '-to', str(t2), '-i', SRC, '-i', p, '-filter_complex', f'[0:v]crop={CW}:{CH}:0:{TOP},setpts=PTS/{speed},pad={CW}:1080:0:0[v];[v][1:v]overlay=0:0,fps=30[o]', '-map', '[o]', '-an', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'veryfast', o); segs.append(o)

# ---- 1. 화면 안내 (왼쪽 칸)
a, b = grab(3, 'k03.png'), grab(12, 'k12.png')
fr = a.copy(); box(ImageDraw.Draw(fr), (6, 8, 330, 940), '답변 범위 안내', 'right'); still(strip(fr, '화면 왼쪽: 답변할 수 있는 범위와 사용한 자료를 안내', '화면 안내'), 4, 'i1')
z, s = zoom(a, 0, 10, 873); fr = z.copy(); box(ImageDraw.Draw(fr), zb((14, 142, 306, 438), 0, 10, s), '답변 범위'); still(strip(fr, '답변 범위: 수문 상태, 방류 승인, 운영행위, 운영기준, 근거', '화면 안내'), 5, 'i2')
z, s = zoom(a, 0, 425, 873); fr = z.copy(); box(ImageDraw.Draw(fr), zb((14, 450, 306, 712), 0, 425, s), '댐별 자료'); still(strip(fr, '댐별 자료: K-water 댐 4개의 측정값, 승인, 운영행위, 제한수위', '화면 안내'), 5, 'i3')
z, s = zoom(b, 0, 516, 873); fr = z.copy(); box(ImageDraw.Draw(fr), zb((14, 620, 324, 750), 0, 516, s), '범위 밖'); still(strip(fr, '범위 밖: 다른 댐, 예측값, 방류 사유 등의 질문에는 답하지 않음', '화면 안내'), 5, 'i4')
fr = z.copy(); box(ImageDraw.Draw(fr), zb((14, 762, 324, 930), 0, 516, s), '알아 두실 점'); still(strip(fr, '"현재"는 저장된 마지막 시각(2026-09-28 23:00)의 값', '화면 안내'), 5, 'i5')
# ---- 2. 첫 질문
clip(14.0, 21.0, '질문 1  현재 수문·기상 상태 (CQ1)', 'q1a', 1, '시연')
clip(21.0, 54.5, '답변 생성 중 (8배속)', 'q1b', 8, '시연')
c = grab(57.5, 'k57.png'); X0, Y0 = 350, 85; z, s = zoom(c, X0, Y0, 1325)
def q(bx, label, cap, name, sec=5, side='right'):
    fr = z.copy(); box(ImageDraw.Draw(fr), zb(bx, X0, Y0, s), label, side); still(strip(fr, cap, '답변 보기'), sec, name)
q((368, 97, 838, 135), '진행 단계', '질문 해석 → KG·저장소 검색 → 근거 정리 → 답변 작성 순서로 진행', 'q1c1')
q((368, 137, 1246, 222), None, '질문을 CQ1(현재 수문 상태)·충주댐으로 분류하고, KG 경로를 따라 근거를 조회', 'q1c2')
q((362, 224, 860, 460), '근거', '근거: KG와 저장소에서 찾은 값. 값마다 출처 번호가 붙음', 'q1c3')
q((362, 462, 1262, 678), None, '판단: 근거를 정리한 문장. 자료에 없는 내용은 "자료에 없음"으로 표시', 'q1c4')
q((664, 256, 838, 286), '출처 번호', '출처 번호를 누르면 원본 값을 확인할 수 있음', 'q1c5', 4)
clip(57.8, 60.0, '출처 번호를 누름', 'q1d', 1, '시연')
c = grab(61, 'k61.png'); z, s = zoom(c, 640, 0, 1280); fr = z.copy(); box(ImageDraw.Draw(fr), zb((1372, 4, 1908, 340), 640, 0, s), '원본 값', 'left')
still(strip(fr, '측정 저장소의 원본 행: 관측소 코드 1003110, 2026-09-28 23:00', '원본 확인'), 6, 'q1e')
clip(61.5, 64.5, '원본 창을 닫고 다음 질문으로', 'q1f', 1, '시연')
lst = os.path.join(W, 'list.txt'); open(lst, 'w').write(''.join("file '%s'\n" % os.path.abspath(x) for x in segs))
run('-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', OUT); print('ok', len(segs))
