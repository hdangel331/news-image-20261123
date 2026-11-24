#!/usr/bin/env python3
"""Build the news poster for make.fun news-image-20261123.

Reads panels.png (one square image: a 2x3 grid of six illustrations with no
text, made for this entry) from the repository root, slices it into six
panels, and composes the 1024x1024 poster entry.png: masthead with the date,
six illustrated stories, an ALSO TODAY ticker, and a sources line. All text
is set here with PIL so every word is exact and legible.

Run from the repository root:  python3 tools/build_poster.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
PANELS = ROOT / "panels.png"
OUT = ROOT / "entry.png"

W, H = 1024, 1024
NAVY = (22, 35, 63)
GOLD = (217, 164, 65)
PAPER = (247, 243, 234)
INK = (26, 26, 26)
GREY = (88, 88, 88)
RED = (178, 34, 34)
CARD = (255, 255, 255)
BORDER = (214, 208, 194)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def font(name, size):
    return ImageFont.truetype(str(FONT_DIR / name), size)


SERIF_BOLD = "DejaVuSerif-Bold.ttf"
SERIF = "DejaVuSerif.ttf"
SANS_BOLD = "DejaVuSans-Bold.ttf"
SANS = "DejaVuSans.ttf"

# (kicker, headline, summary) in grid order: left to right, top to bottom.
STORIES = [
    ("CLIMATE · ANTALYA",
     "COP31 collapses with no deal",
     "Two weeks of talks end in disarray as countries fail to agree on moving away from fossil fuels."),
    ("BUSINESS & TECH",
     "Nvidia brings back Jensen Huang",
     "The chipmaker reinstates its co-founder as chief executive, effective immediately."),
    ("WAR IN UKRAINE",
     "Ukraine sinks Russian warship off Libya",
     "Kyiv says its naval drones sank a Russian warship off the Libyan coast."),
    ("USA · POLITICS",
     "Democrats' biggest House win since 1992",
     "Flipping a North Carolina seat seals the largest House majority since 1992."),
    ("ASIA · INDONESIA",
     "Factory fire kills 24 in Indonesia",
     "Blaze sweeps a candy plant in Banten; dozens are still missing as the search goes on."),
    ("MIDDLE EAST",
     "Tankers ablaze in Strait of Hormuz",
     "Mines set three tankers on fire, Iran's Guard says, as Tehran vows to answer the US naval blockade."),
]

TICKER = [
    "NATO sends early-warning aircraft to Poland",
    "India gives Nepal a $1.62bn flood package",
    "Bitcoin rebounds from a two-year low",
    "Houthis claim an attack on a Saudi refinery",
    "Verstappen wins the Las Vegas Grand Prix",
]


def wrap(draw, text, fname, size, max_width, max_lines):
    """Word-wrap text to fit max_width; shrink the font until it fits max_lines."""
    while size > 10:
        f = font(fname, size)
        lines, cur = [], ""
        for word in text.split():
            trial = f"{cur} {word}".strip()
            if draw.textlength(trial, font=f) <= max_width:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        if len(lines) <= max_lines:
            return f, lines
        size -= 1
    return font(fname, 10), lines[:max_lines]


def main():
    if not PANELS.exists():
        print(f"missing {PANELS} — put the six-panel illustration there first", file=sys.stderr)
        return 1
    grid = Image.open(PANELS).convert("RGB")
    side = min(grid.size)
    grid = grid.crop(((grid.width - side) // 2, (grid.height - side) // 2,
                      (grid.width + side) // 2, (grid.height + side) // 2))
    # The grid is 2 rows x 3 columns inside the square image, so each cell
    # is a portrait rectangle: width side/3, height side/2.
    cell_w, cell_h = side // 3, side // 2
    inset_x, inset_y = max(4, cell_w // 40), max(4, cell_h // 40)
    cells = []
    for row in range(2):
        for col in range(3):
            box = (col * cell_w + inset_x, row * cell_h + inset_y,
                   (col + 1) * cell_w - inset_x, (row + 1) * cell_h - inset_y)
            cells.append(grid.crop(box))

    poster = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(poster)

    # Masthead.
    d.rectangle([0, 0, W, 118], fill=NAVY)
    f = font(SERIF_BOLD, 60)
    d.text((W // 2, 16), "THE WORLD IN ONE DAY", font=f, fill=(255, 255, 255), anchor="ma")
    f = font(SANS_BOLD, 28)
    d.text((W // 2, 84), "MONDAY, 23 NOVEMBER 2026", font=f, fill=GOLD, anchor="ma")

    # Sub-line: the date claim, in plain words.
    f = font(SANS, 20)
    d.text((W // 2, 128), "Every story below happened, or was first reported, on Monday 23 November 2026.",
           font=f, fill=GREY, anchor="ma")

    # Story grid: 2 rows x 3 columns.
    grid_top, grid_bottom = 164, 830
    margin, gutter = 24, 16
    panel_w = (W - 2 * margin - 2 * gutter) // 3
    panel_h = (grid_bottom - grid_top - gutter) // 2
    img_w, img_h = panel_w - 20, 150
    for i, (kicker, headline, summary) in enumerate(STORIES):
        row, col = divmod(i, 3)
        x = margin + col * (panel_w + gutter)
        y = grid_top + row * (panel_h + gutter)
        d.rectangle([x, y, x + panel_w, y + panel_h], fill=CARD, outline=BORDER, width=1)
        art = cells[i].resize((img_w, img_h), Image.LANCZOS)
        poster.paste(art, (x + 10, y + 10))
        tx = x + 10
        ty = y + 10 + img_h + 10
        f = font(SANS_BOLD, 16)
        d.text((tx, ty), kicker, font=f, fill=RED)
        f, lines = wrap(d, headline, SERIF_BOLD, 24, panel_w - 20, 2)
        hy = ty + 24
        for line in lines:
            d.text((tx, hy), line, font=f, fill=INK)
            hy += 28
        f, lines = wrap(d, summary, SANS, 18, panel_w - 20, 3)
        sy = hy + 6
        for line in lines:
            d.text((tx, sy), line, font=f, fill=(60, 60, 60))
            sy += 22

    # ALSO TODAY ticker.
    d.rectangle([0, 842, W, 936], fill=NAVY)
    f = font(SANS_BOLD, 22)
    d.text((24, 852), "ALSO TODAY", font=f, fill=GOLD)
    ticker_text = "  •  ".join(TICKER)
    f, lines = wrap(d, ticker_text, SANS, 17, W - 48, 2)
    ty = 884
    for line in lines:
        d.text((24, ty), line, font=f, fill=(255, 255, 255))
        ty += 22

    # Footer: sources, drawn date.
    f = font(SANS, 16)
    d.text((W // 2, 948), "Sources: Reuters · AP · BBC · BusinessWorld · Al Jazeera · Daily Mirror · CoinDesk",
           font=f, fill=GREY, anchor="ma")
    d.text((W // 2, 972), "Drawn on 23 November 2026", font=f, fill=GREY, anchor="ma")

    poster.save(OUT, optimize=True)
    size = OUT.stat().st_size
    print(f"wrote {OUT} {poster.size[0]}x{poster.size[1]} {size} bytes")
    if size > 1048576:
        print("WARNING: over the 1 MiB limit", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
