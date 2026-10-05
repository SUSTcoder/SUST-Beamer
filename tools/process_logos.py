# -*- coding: utf-8 -*-
"""把苏州科技大学参考图加工成 beamer 模板所需的 5 张透明底素材。
输入:  苏州科技大学-logo-1024px.png / name.jpg
输出:  sust_logo_blue.png / sust_logo_white.png / sust_name_blue.png / sust_name_white.png / sust_motto_navy.png
"""
from PIL import Image, ImageDraw, ImageFont
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PAD = 12          # 裁边后保留的透明边距(像素)
WHITE_THRESH = 250  # 低于此 min(RGB) 视为内容, 高于此视为白底

def crop_content(im, pad=PAD):
    """按 alpha 裁剪到内容包围盒, 四周留 pad 像素透明边。"""
    bbox = im.getchannel("A").getbbox()
    if bbox:
        l, t, r, b = bbox
        l = max(0, l - pad); t = max(0, t - pad)
        r = min(im.width, r + pad); b = min(im.height, b + pad)
        im = im.crop((l, t, r, b))
    return im

def pad_square(im):
    """补成正方形画布, 内容居中。"""
    side = max(im.size)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(im, ((side - im.width) // 2, (side - im.height) // 2), im)
    return canvas

def to_white(im):
    """保留 alpha, 颜色全部置白 -> 深色背景用白版。"""
    out = im.copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            px[x, y] = (255, 255, 255, a)
    return out

def save(im, name):
    path = os.path.join(HERE, name)
    im.save(path, "PNG", optimize=True)
    # 统计供验证
    a = im.getchannel("A")
    trans = sum(1 for v in a.getdata() if v < 16) / (im.width * im.height)
    print(f"{name:24s} {im.width}x{im.height}  透明像素 {trans:.1%}")

# ---------- 1+2. 校徽: 蓝版 / 白版 ----------
logo = Image.open(os.path.join(HERE, "苏州科技大学-logo-1024px.png")).convert("RGBA")
logo_c = crop_content(logo)
save(pad_square(logo_c), "sust_logo_blue.png")
save(pad_square(to_white(logo_c)), "sust_logo_white.png")

# ---------- 3+4. 校名: JPG 去白底 -> 蓝版 / 白版 ----------
src = Image.open(os.path.join(HERE, "name.jpg")).convert("RGB")
ink = Image.new("RGBA", src.size, (0, 0, 0, 0))
sp, ip = src.load(), ink.load()
for y in range(src.height):
    for x in range(src.width):
        r, g, b = sp[x, y]
        m = min(r, g, b)
        if m >= WHITE_THRESH:
            ip[x, y] = (0, 0, 0, 0)           # 白底 -> 全透明
        else:
            a = 255 - m                        # 离白越远越不透明
            # 反预乘: 恢复被白色冲淡的真实墨色, 让半透明边缘不发灰
            rr = max(0, min(255, 255 - (255 - r) * 255 // a))
            gg = max(0, min(255, 255 - (255 - g) * 255 // a))
            bb = max(0, min(255, 255 - (255 - b) * 255 // a))
            ip[x, y] = (rr, gg, bb, a)
name_c = crop_content(ink)
save(name_c, "sust_name_blue.png")
save(to_white(name_c), "sust_name_white.png")

# ---------- 5. 校训水印(占位): 致远至恒 务学悟真 ----------
W, H = 1200, 789
NAVY = (0, 58, 102, 255)   # 苏科大蓝加深, 水印用
motto = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(motto)
font = ImageFont.truetype(os.path.join(HERE, "..", "fonts", "SimKai.TTF"), 175)
lines = ["致远至恒", "务学悟真"]
lh = 262
y0 = (H - lh * len(lines)) // 2
for i, line in enumerate(lines):
    bb = d.textbbox((0, 0), line, font=font)
    w = bb[2] - bb[0]
    d.text(((W - w) // 2 - bb[0], y0 + i * lh - bb[1]), line, font=font, fill=NAVY)
save(motto, "sust_motto_navy.png")
print("done")
