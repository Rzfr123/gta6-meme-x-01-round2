#!/usr/bin/env python3
"""Render the gta6-meme-x-01 round-2 meme: CLEAN single-gag WASTED.

Round 1's judge critique was clutter: stacked text blocks and the
"SINCE 2002" line muddying the joke. Round 2 keeps the WASTED gag and
the satire (13 years / 2 delays / 99% loading) but as ONE line, not a
stack. Exactly three text elements in the whole picture:

  - "WASTED": huge grey death-screen lettering across the open sky.
  - One satire line: "13 YEARS. 2 DELAYS. STILL 99%."
  - One punchline line in the bottom bar, next to the REAL make.fun
    ghost: "MY AI AGENT ALREADY WON REAL MONEY ON make.fun".

Plus two graphics, no text: a pink loading bar HUD stuck at 99% (the
99% is already in the satire line, so the bar carries no label) and
five gold wanted stars top-right (GTA HUD detail).

Fresh original illustration: a Hawaiian-shirt gamer slumped asleep in
a deck chair on a neon Vice City beach, cobwebbed, clutching his
controller, dusty console and empty cans beside him — he waited so
long the wait itself got him. All text is drawn with PIL (DejaVu Sans
Bold); no text comes from the generated art. No copyrighted GTA art,
no lifted screenshot, no trademark logo image.
"""
import hashlib
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

W = 1024
BASE = ASSETS / "media-generation-gta6-round2-clean-base-0-5bc67525-aade-429c-98bc-29d62f414d44.png"
GHOST = ASSETS / "mark-1024.png"

# Bottom punchline bar geometry. The gamer's chair runs down the right
# side, so the punchline text stays in the column right of the ghost,
# clear of the chair legs.
BAR_Y0 = 908
BAR_Y1 = 1024


def fit_font(text, max_w, start, min_size=20):
    """Largest bold font size at which `text` fits max_w."""
    size = start
    while size > min_size:
        f = ImageFont.truetype(BOLD, size)
        if f.getlength(text) <= max_w:
            return f
        size -= 2
    return ImageFont.truetype(BOLD, min_size)


def draw_outlined(draw, xy, text, font, fill="white", stroke="black",
                  stroke_w=None):
    sw = stroke_w if stroke_w is not None else max(2, font.size // 12)
    draw.text(xy, text, font=font, fill=fill, stroke_width=sw,
              stroke_fill=stroke)


def draw_centered(draw, text, font, cx, y, **kw):
    draw_outlined(draw, (cx - font.getlength(text) / 2, y), text, font, **kw)


def draw_spaced(draw, text, font, cx, y, tracking, fill, stroke, stroke_w):
    """Draw `text` centred with extra letter spacing (death-screen feel)."""
    widths = [font.getlength(ch) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill, stroke_width=stroke_w,
                  stroke_fill=stroke)
        x += w + tracking


def draw_star(draw, cx, cy, r, fill, stroke="black", stroke_w=3):
    """Five-pointed wanted star centred at (cx, cy)."""
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=fill, outline=stroke, width=stroke_w)


def main():
    base = Image.open(BASE).convert("RGB").resize((W, W), Image.LANCZOS)
    ghost = Image.open(GHOST).convert("RGBA")
    canvas = base.copy()
    draw = ImageDraw.Draw(canvas, "RGBA")

    # ---- Wanted stars: 5 stars, top-right (GTA HUD) ----
    star_r, gap, top = 26, 62, 52
    x = W - 24 - star_r
    for _ in range(5):
        draw_star(draw, x, top, star_r, fill="#FFD23F")
        x -= gap

    # ---- WASTED: huge grey death-screen lettering over the open sky ----
    f_wasted = fit_font("WASTED", W - 60, 200)
    tracking = 18
    while (sum(f_wasted.getlength(c) for c in "WASTED")
           + tracking * 5 > W - 40 and f_wasted.size > 60):
        f_wasted = ImageFont.truetype(BOLD, f_wasted.size - 4)
    wasted_y = 110
    draw_spaced(draw, "WASTED", f_wasted, W // 2, wasted_y, tracking,
                fill="#D8D8D8", stroke="black", stroke_w=7)
    wasted_bottom = wasted_y + f_wasted.size + 14

    # ---- The ONE satire line: wait + delays + loading, in a single line.
    satire = "13 YEARS. 2 DELAYS. STILL 99%."
    f_sat = fit_font(satire, W - 80, 48)
    sat_y = wasted_bottom + 8
    draw_centered(draw, satire, f_sat, W // 2, sat_y,
                  fill="white", stroke="black")
    sat_bottom = sat_y + f_sat.size

    # ---- Loading bar HUD: stuck at 99% — the download that never ends.
    # No label on the bar: the 99% is already in the satire line above.
    # Skyline top in the bar zone is y 420 (measured), so the bar must
    # end above it.
    bar_w, bar_h = 560, 30
    bar_x0 = (W - bar_w) // 2
    bar_y0 = sat_bottom + 16
    bar_y1 = bar_y0 + bar_h
    assert bar_y1 < 420, bar_y1  # must stay above the skyline
    draw.rectangle([bar_x0 - 3, bar_y0 - 3, bar_x0 + bar_w + 3,
                    bar_y1 + 3], fill="black")
    draw.rectangle([bar_x0, bar_y0, bar_x0 + bar_w, bar_y1],
                   fill="#1A1A22")
    fill_w = int(bar_w * 0.99)
    draw.rectangle([bar_x0, bar_y0, bar_x0 + fill_w, bar_y1],
                   fill="#FF2E88")
    draw.rectangle([bar_x0 + fill_w, bar_y0, bar_x0 + bar_w, bar_y1],
                   fill="#3A3A44")

    # ---- Bottom punchline bar: ghost + ONE line, right of the ghost ----
    draw.rectangle([0, BAR_Y0, W, BAR_Y1], fill=(0, 0, 0, 178))
    ghost_size = 104
    g = ghost.resize((ghost_size, ghost_size), Image.LANCZOS)
    gy = BAR_Y0 + (BAR_Y1 - BAR_Y0 - ghost_size) // 2
    canvas.paste(g, (14, gy), g)
    draw = ImageDraw.Draw(canvas, "RGBA")
    punch = "MY AI AGENT ALREADY WON REAL MONEY ON make.fun"
    f_bot = fit_font(punch, W - 130 - 20, 34)
    y = BAR_Y0 + (BAR_Y1 - BAR_Y0 - f_bot.size) // 2
    draw_centered(draw, punch, f_bot, 130 + (W - 130) // 2, y,
                  fill="white", stroke="black")

    out = HERE / "meme.png"
    canvas.save(out, "PNG")
    print("wrote", out, canvas.size)
    print("sha256", hashlib.sha256(out.read_bytes()).hexdigest())
    print("wasted font", f_wasted.size, "satire", f_sat.size,
          "punch", f_bot.size, "bar_y0", bar_y0, "bar_y1", bar_y1)

    # ---- Output validation: the render must not silently drift ----
    # Re-read what was actually written and check the deliverable, plus
    # confirm the ghost asset loaded at the size the layout assumes.
    saved = Image.open(out)
    assert saved.size == (W, W), saved.size
    assert out.stat().st_size <= 1024 * 1024, out.stat().st_size
    assert ghost.size == (1024, 1024), ghost.size
    print("validated", out, saved.size, out.stat().st_size, "bytes",
          "ghost", ghost.size)


if __name__ == "__main__":
    main()
