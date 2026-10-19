# -*- coding: utf-8 -*-
"""Generate the README before/after comparison image.

Renders two side-by-side "documents" illustrating the problem word-master
solves:

  left  — AI output with drifting formatting (hand-typed numbers, random
          font sizes, misplaced captions, inconsistent table styles)
  right — the same content after the template contract + builder + gate

The image is illustrative (not a screenshot of real output) and is meant to
make the core claim legible at a glance.

Usage:
  python scripts/make_compare_image.py [--out docs/assets/before-after.png]
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]

W, H = 1600, 940
MARGIN = 40
GAP = 24
PANEL_W = (W - MARGIN * 2 - GAP) // 2
PANEL_H = H - MARGIN * 2 - 64

BG = (247, 247, 245)
PANEL_BG = (255, 255, 255)
INK = (32, 32, 32)
MUTED = (128, 128, 128)
RED = (200, 60, 50)
GREEN = (32, 130, 90)
LINE = (226, 226, 222)
TAG_BG = (238, 238, 234)


def font(name, size):
    for p in (f"C:/Windows/Fonts/{name}", f"/usr/share/fonts/truetype/{name}"):
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


F = {
    "title": font("msyhbd.ttc", 26),
    "h1": font("simhei.ttf", 22),
    "h2": font("simhei.ttf", 18),
    "body": font("simsun.ttc", 15),
    "small": font("msyh.ttc", 13),
    "tag": font("msyhbd.ttc", 14),
    "mono": font("consola.ttf", 13),
}


def draw_panel(img, x, y, w, h, header, header_color):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=PANEL_BG, outline=LINE)
    d.rounded_rectangle([x, y, x + w, y + 44], radius=10, fill=header_color)
    d.rectangle([x, y + 30, x + w, y + 44], fill=header_color)
    d.text((x + 18, y + 12), header, font=F["tag"], fill=(255, 255, 255))
    return d


def draw_page(d, ox, oy, page_w, drift):
    """Draw a faux A4 page. drift=True renders the 'bad' variant."""
    pad = 26
    x0, y0 = ox + pad, oy + pad
    inner_w = page_w - pad * 2

    if drift:
        # title: random size, off-center, wrong font
        d.text((x0 + 30, y0), "河道水环境综合治理工程", font=F["title"], fill=RED)
        d.text((x0 + 30, y0 + 34), "可行性研究", font=F["small"], fill=MUTED)

        # hand-typed heading numbers, inconsistent sizes
        d.text((x0 + 30, y0 + 70), "1. 概述", font=F["h1"], fill=INK)
        d.text((x0 + 30, y0 + 106), "1.1 编制依据", font=F["body"], fill=INK)
        d.text((x0 + 44, y0 + 130), "（1）沿线污水管道运行年限较长", font=F["small"], fill=INK)
        d.text((x0 + 44, y0 + 150), "1) 管道上岸段结构性缺陷比例较高", font=F["body"], fill=INK)

        # figure ABOVE caption but caption above figure (wrong order)
        d.text((x0 + 30, y0 + 182), "图 1.1-1 某河道工程地理位置图", font=F["body"], fill=RED)
        d.rectangle([x0 + 30, y0 + 204, x0 + inner_w - 10, y0 + 300], fill=(238, 240, 242), outline=(200, 205, 210))
        d.text((x0 + 120, y0 + 244), "[ 图片 ]", font=F["small"], fill=MUTED)

        # table with random styling
        d.text((x0 + 30, y0 + 318), "主要建设项目一览表", font=F["body"], fill=RED)
        ty = y0 + 340
        for r in range(4):
            fill = (250, 250, 250) if r % 2 else (240, 244, 250)
            d.rectangle([x0 + 30, ty + r * 26, x0 + inner_w - 10, ty + (r + 1) * 26], fill=fill, outline=(180, 180, 180))
        d.text((x0 + 36, ty + 6), "序号", font=F["small"], fill=INK)
        d.text((x0 + 106, ty + 6), "项目内容", font=F["small"], fill=INK)

        # hand-typed cross reference pointing nowhere
        d.text((x0 + 30, y0 + 458), "详见 表 3-2（实际编号为 表1.1-1）", font=F["small"], fill=RED)

        d.text((x0 + 30, y0 + 492), "字体：宋体 / 微软雅黑 / Arial 混用", font=F["mono"], fill=RED)
        d.text((x0 + 30, y0 + 512), "字号：16 / 15 / 14 / 12 / 10.5 pt 混用", font=F["mono"], fill=RED)
    else:
        # title: contract style — centered, fixed size
        title = "河道水环境综合治理工程可行性研究"
        tw = d.textlength(title, font=F["title"])
        d.text((x0 + (inner_w - tw) / 2, y0), title, font=F["title"], fill=INK)

        d.text((x0 + 30, y0 + 54), "1  概述", font=F["h1"], fill=INK)
        d.text((x0 + 30, y0 + 90), "1.1  编制依据", font=F["h2"], fill=INK)
        d.text((x0 + 30, y0 + 122), "（1）沿线污水管道运行年限较长，存在破损渗漏；", font=F["body"], fill=INK)
        d.text((x0 + 30, y0 + 146), "1)  管道上岸段结构性缺陷比例较高；", font=F["body"], fill=INK)

        # figure then caption (correct order)
        d.rectangle([x0 + 30, y0 + 176, x0 + inner_w - 10, y0 + 272], fill=(238, 240, 242), outline=(200, 205, 210))
        d.text((x0 + 120, y0 + 216), "[ 嵌入型图片 ]", font=F["small"], fill=MUTED)
        cap = "图1.1-1  某河道工程地理位置图"
        cw = d.textlength(cap, font=F["body"])
        d.text((x0 + (inner_w - cw) / 2, y0 + 280), cap, font=F["body"], fill=INK)

        # table: caption above, contract style
        cap2 = "表1.1-1  主要建设项目一览表"
        cw2 = d.textlength(cap2, font=F["body"])
        d.text((x0 + (inner_w - cw2) / 2, y0 + 312), cap2, font=F["body"], fill=INK)
        ty = y0 + 336
        for r in range(4):
            d.rectangle([x0 + 30, ty + r * 26, x0 + inner_w - 10, ty + (r + 1) * 26],
                        fill=(255, 255, 255), outline=(90, 90, 90))
        d.line([x0 + 30, ty + 26, x0 + inner_w - 10, ty + 26], fill=(60, 60, 60), width=2)
        d.text((x0 + 36, ty + 6), "序号", font=F["small"], fill=INK)
        d.text((x0 + 106, ty + 6), "项目内容", font=F["small"], fill=INK)

        d.text((x0 + 30, y0 + 456), "详见 表1.1-1（REF 域，F9 自动更新）", font=F["small"], fill=INK)

        d.text((x0 + 30, y0 + 492), "字体：宋体 + Times New Roman（契约锁定）", font=F["mono"], fill=GREEN)
        d.text((x0 + 30, y0 + 512), "字号：全部来自样式表，run 级零直接格式", font=F["mono"], fill=GREEN)


def draw_checklist(d, ox, oy, panel_w, items, color):
    y = oy
    for text in items:
        d.text((ox, y), "✗" if color == RED else "✓", font=F["body"], fill=color)
        d.text((ox + 20, y), text, font=F["small"], fill=INK)
        y += 22


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "docs" / "assets" / "before-after.png"))
    args = ap.parse_args()

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    d.text((MARGIN, 18), "word-master · 同一份内容，两种产出", font=F["title"], fill=INK)
    d.text((MARGIN + 560, 28), "内容与样式分离：AI 只写语义，格式由模板契约决定", font=F["small"], fill=MUTED)

    x_left = MARGIN
    x_right = MARGIN + PANEL_W + GAP
    y = 64

    d_left = draw_panel(img, x_left, y, PANEL_W, PANEL_H, "✗  通用 AI 直出：每次格式都不一样", RED)
    d_right = draw_panel(img, x_right, y, PANEL_W, PANEL_H, "✓  word-master：契约锁定 + 门禁把关", GREEN)

    draw_page(d_left, x_left, y + 52, PANEL_W, drift=True)
    draw_page(d_right, x_right, y + 52, PANEL_W, drift=False)

    # footers
    fy = y + PANEL_H - 150
    d_left.line([x_left + 20, fy, x_left + PANEL_W - 20, fy], fill=LINE)
    d_left.text((x_left + 20, fy + 10), "交付前必须人工逐项核对", font=F["tag"], fill=RED)
    draw_checklist(d_left, x_left + 24, fy + 34, PANEL_W,
                   ["标题编号手打，插入章节后全部错位",
                    "图名在图上方 / 表题在图下方，方向随机",
                    "字体字号混用，评审退回重排",
                    "交叉引用是死文本，改一处要全文搜"], RED)

    d_right.line([x_right + 20, fy, x_right + PANEL_W - 20, fy], fill=LINE)
    d_right.text((x_right + 20, fy + 10), "门禁 fail-closed：blocking 清零才交付", font=F["tag"], fill=GREEN)
    draw_checklist(d_right, x_right + 24, fy + 34, PANEL_W,
                   ["编号全部来自自动编号域，插入章节自动重排",
                    "图名在下、表题在上，模板固定",
                    "字体只许宋体/黑体 + Times New Roman",
                    "交叉引用是 REF 域，Ctrl+A → F9 全量刷新"], GREEN)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)
    print(f"written: {out}  ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
