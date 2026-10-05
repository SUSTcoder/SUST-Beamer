# -*- coding: utf-8 -*-
"""用 Windows 艺术字体渲染校训水印图（透明底, 深色）。
输出: sust_motto_navy.png(华文行楷, 主推) + 两个备选。
"""
from PIL import Image, ImageDraw, ImageFont
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WIN = r"C:\Windows\Fonts"
NAVY = (0, 58, 102, 255)
LINES = ["致远至恒", "务学悟真"]
OUT_W = 1200          # 输出宽度(与吉大原图一致)
SIZE = 205            # 字号
TRACKING = 16         # 字间距(书法体略放松更像题词)
LINE_GAP = 78         # 行间距
STROKE = 3            # 描边加粗, 保证 0.28 水印下笔画不断


def render(font_file, size, tracking, line_gap, stroke):
    font = ImageFont.truetype(os.path.join(WIN, font_file), size)
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    widths = [probe.textbbox((0, 0), s, font=font)[2] -
              probe.textbbox((0, 0), s, font=font)[0] for s in LINES]
    line_w = [w + tracking * (len(s) - 1) for w, s in zip(widths, LINES)]
    ascent = probe.textbbox((0, 0), "致", font=font)[1]
    line_h = size + line_gap

    W = max(line_w) + stroke * 4 + 8
    H = line_h * len(LINES) + stroke * 4 + 8
    img = Image.new("RGBA", (int(W), int(H)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    y0 = stroke * 2 - ascent
    for i, s in enumerate(LINES):
        x = (W - line_w[i]) / 2
        for ch in s:
            d.text((x + stroke * 2, y0 + i * line_h), ch, font=font, fill=NAVY,
                   stroke_width=stroke, stroke_fill=NAVY)
            x += probe.textbbox((0, 0), ch, font=font)[2] - \
                 probe.textbbox((0, 0), ch, font=font)[0] + tracking
    img = img.crop(img.getchannel("A").getbbox())
    img = img.resize((OUT_W, max(1, round(OUT_W * img.height / img.width))),
                     Image.LANCZOS)
    return img


def save(im, name):
    im.save(os.path.join(HERE, name), "PNG", optimize=True)
    print(f"{name:34s} {im.width}x{im.height}")


save(render("STXINGKA.TTF", SIZE, TRACKING, LINE_GAP, STROKE),
     "sust_motto_navy.png")
save(render("FZSTK.TTF", SIZE + 6, TRACKING + 2, LINE_GAP, 2),
     "sust_motto_navy_备选-方正舒体.png")
save(render("STXINWEI.TTF", SIZE - 4, TRACKING, LINE_GAP + 10, 2),
     "sust_motto_navy_备选-华文新魏.png")
save(render("STLITI.TTF", SIZE - 6, TRACKING + 6, LINE_GAP + 14, 2),
     "sust_motto_navy_备选-华文隶书.png")
print("done")
