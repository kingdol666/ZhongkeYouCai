#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目图标生成器 — 生成 icon.png + icon.ico
"""

import os
from PIL import Image, ImageDraw

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIZE = 256


def draw_icon(size: int) -> Image.Image:
    """绘制一个热力图风格的图标"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    margin = max(1, size * 0.06)
    r = max(1, int(size * 0.2))

    # 深色圆角方形背景
    d.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=r, fill="#1e293b")

    # 热力图渐变网格 (5x5)
    inner = max(2, size * 0.16)
    cols, rows = 5, 5
    cw = (size - 2 * inner) / cols
    ch = (size - 2 * inner) / rows
    heat_colors = [
        (0, 59, 130, 255),     # 蓝
        (0, 180, 216, 255),    # 青
        (0, 200, 120, 255),    # 绿
        (255, 210, 50, 255),   # 黄
        (240, 80, 60, 255),    # 红
    ]

    for row in range(rows):
        for col in range(cols):
            t = row / max(rows - 1, 1)
            idx_f = t * (len(heat_colors) - 1)
            lo = int(idx_f)
            hi = min(lo + 1, len(heat_colors) - 1)
            frac = idx_f - lo
            color = tuple(
                int(heat_colors[lo][i] + (heat_colors[hi][i] - heat_colors[lo][i]) * frac)
                for i in range(4))

            x0 = inner + col * cw
            y0 = inner + row * ch
            gap = max(0.8, size * 0.01)
            rr = max(1, int(size * 0.04))
            d.rounded_rectangle(
                [x0 + gap, y0 + gap, x0 + cw - gap, y0 + ch - gap],
                radius=rr, fill=color)

    # 白色十字准线
    cx = size / 2
    cy = size / 2
    cr = size * 0.13
    lw = max(2, int(size * 0.03))
    d.line([cx - cr, cy, cx + cr, cy], fill="#ffffff", width=lw)
    d.line([cx, cy - cr, cx, cy + cr], fill="#ffffff", width=lw)

    # 琥珀色中心点
    dr = max(2, size * 0.04)
    d.ellipse([cx - dr, cy - dr, cx + dr, cy + dr], fill="#f59e0b")

    return img


def main():
    icon = draw_icon(SIZE)

    png_path = os.path.join(PROJECT_ROOT, "icon.png")
    ico_path = os.path.join(PROJECT_ROOT, "icon.ico")

    icon.save(png_path, format="PNG")
    icon.save(ico_path, format="ICO")

    print(f"Generated:")
    print(f"  {png_path}  ({icon.size[0]}x{icon.size[1]} PNG)")
    print(f"  {ico_path}  ({icon.size[0]}x{icon.size[1]} ICO)")


if __name__ == "__main__":
    main()
