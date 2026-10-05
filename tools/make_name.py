# -*- coding: utf-8 -*-
"""重制校名图: 中文校名为主体, 英文行缩小附于其下; 去白底后平涂校徽蓝 #0066B3。
输出:
  sust_name_v2_blue.png / sust_name_v2_white.png  中文+英文(封面/致谢页用)
  sust_name_cn_white.png                          纯中文(页眉用, 高度小, 避免英文糊成线)
"""
from PIL import Image
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BLUE = (0, 102, 179)      # 校徽主体蓝
WHITE_THRESH = 250
EN_SCALE = 0.80           # 英文行缩放
GAP = 26                  # 中英文行间距
PAD = 10


def dewhite(im):
    """白底 -> alpha, 返回 (RGBA墨色图, alpha图)。"""
    src = im.convert("RGB")
    out = Image.new("RGBA", src.size, (0, 0, 0, 0))
    sp, op = src.load(), out.load()
    for y in range(src.height):
        for x in range(src.width):
            r, g, b = sp[x, y]
            m = min(r, g, b)
            a = 0 if m >= WHITE_THRESH else 255 - m
            op[x, y] = (r, g, b, a)
    return out


def ink_row(im, y0, y1):
    """取某一行区间的墨迹(alpha>0 的包围盒), 返回裁好的 RGBA。"""
    band = im.crop((0, y0, im.width, y1))
    bbox = band.getchannel("A").getbbox()
    return band.crop(bbox)


src = Image.open(os.path.join(HERE, "name.jpg"))
ink = dewhite(src)

# 按行投影自动定位中文行 / 英文行
px = ink.load()
rows = [sum(1 for x in range(0, ink.width, 2) if px[x, y][3] > 8) for y in range(ink.height)]
segs, s = [], None
for y, n in enumerate(rows):
    if n > 0 and s is None:
        s = y
    elif n == 0 and s is not None:
        if y - s > 8:
            segs.append((s, y))
        s = None
if s is not None:
    segs.append((s, ink.height))
segs.sort(key=lambda t: t[1] - t[0], reverse=True)
cn_seg, en_seg = sorted(segs[:2], key=lambda t: t[0])

cn = ink_row(ink, *cn_seg)
en = ink_row(ink, *en_seg)
en = en.resize((max(1, round(en.width * EN_SCALE)), max(1, round(en.height * EN_SCALE))),
               Image.LANCZOS)
print(f"中文行 {cn.width}x{cn.height}  英文行(缩放后) {en.width}x{en.height}")

canvas = Image.new("RGBA", (cn.width, cn.height + GAP + en.height), (0, 0, 0, 0))
canvas.paste(cn, (0, 0), cn)
canvas.paste(en, ((cn.width - en.width) // 2, cn.height + GAP), en)
canvas = canvas.crop(canvas.getchannel("A").getbbox())
canvas = Image.new("RGBA", (canvas.width + PAD * 2, canvas.height + PAD * 2), (0, 0, 0, 0)).paste(
    canvas, (PAD, PAD), canvas) or canvas

def flat(alpha_src, rgb):
    out = Image.new("RGBA", alpha_src.size, rgb + (0,))
    out.putalpha(alpha_src.getchannel("A"))
    return out


def save(im, name):
    im.save(os.path.join(HERE, name), "PNG", optimize=True)
    a = im.getchannel("A")
    tr = sum(1 for v in a.get_flattened_data() if v < 16) / (im.width * im.height)
    print(f"{name:26s} {im.width}x{im.height} 比例 {im.width/im.height:.2f}:1 透明 {tr:.1%}")


# 中文+英文(封面用)
save(flat(canvas, BLUE), "sust_name_v2_blue.png")
save(flat(canvas, (255, 255, 255)), "sust_name_v2_white.png")
# 纯中文(页眉用)
save(flat(cn, (255, 255, 255)), "sust_name_cn_white.png")
print("done")
