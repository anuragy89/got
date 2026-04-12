"""
countdown_gif.py — Digital clock countdown GIF renderer
Generates an animated GIF (10 → 1) styled as a green 7-segment display
on a black background, matching the reference screenshot.
No external dependencies beyond Pillow (already in requirements.txt).
"""

import io
from PIL import Image, ImageDraw, ImageFilter

# ── 7-segment definitions ─────────────────────────────────────────
# Indices: top, top-right, bottom-right, bottom, bottom-left, top-left, middle
_SEGS = {
    '0': [1,1,1,1,1,1,0],
    '1': [0,1,1,0,0,0,0],
    '2': [1,1,0,1,1,0,1],
    '3': [1,1,1,1,0,0,1],
    '4': [0,1,1,0,0,1,1],
    '5': [1,0,1,1,0,1,1],
    '6': [1,0,1,1,1,1,1],
    '7': [1,1,1,0,0,0,0],
    '8': [1,1,1,1,1,1,1],
    '9': [1,1,1,1,0,1,1],
}

_GREEN  = (0, 255, 60)
_BRIGHT = (80, 255, 110)   # used for glow layer
_DIM    = (0, 35, 10)
_BG     = (0, 0, 0)


def _draw_segs(draw, ch: str, ox: int, oy: int,
               DW: int, DH: int, DT: int,
               on_color: tuple, off_color: tuple) -> None:
    """Draw a single 7-segment digit at (ox, oy)."""
    segs = _SEGS.get(ch, [0] * 7)
    hh   = DH // 2
    g    = 4

    def col(i):
        return on_color if segs[i] else off_color

    # top
    draw.polygon([
        (ox+g+DT, oy),       (ox+DW-g-DT, oy),
        (ox+DW-g, oy+DT),    (ox+DW-g-DT, oy+DT*2),
        (ox+g+DT, oy+DT*2),  (ox+g, oy+DT),
    ], fill=col(0))
    # top-right
    draw.polygon([
        (ox+DW-DT,   oy+g),        (ox+DW,     oy+g+DT),
        (ox+DW,      oy+hh-g),     (ox+DW-DT,  oy+hh-g-DT),
        (ox+DW-DT*2, oy+hh-g-DT), (ox+DW-DT*2,oy+g+DT),
    ], fill=col(1))
    # bottom-right
    draw.polygon([
        (ox+DW-DT,   oy+hh+g+DT), (ox+DW,     oy+hh+g),
        (ox+DW,      oy+DH-g-DT), (ox+DW-DT,  oy+DH-g),
        (ox+DW-DT*2, oy+DH-g-DT),(ox+DW-DT*2, oy+hh+g+DT),
    ], fill=col(2))
    # bottom
    draw.polygon([
        (ox+g,     oy+DH-DT),   (ox+g+DT,    oy+DH-DT*2),
        (ox+DW-g-DT,oy+DH-DT*2),(ox+DW-g,    oy+DH-DT),
        (ox+DW-g-DT,oy+DH),     (ox+g+DT,    oy+DH),
    ], fill=col(3))
    # bottom-left
    draw.polygon([
        (ox+DT,   oy+hh+g),     (ox+DT*2, oy+hh+g+DT),
        (ox+DT*2, oy+DH-g-DT),  (ox+DT,   oy+DH-g),
        (ox,      oy+DH-g-DT),  (ox,      oy+hh+g),
    ], fill=col(4))
    # top-left
    draw.polygon([
        (ox+DT,   oy+g),       (ox+DT*2, oy+g+DT),
        (ox+DT*2, oy+hh-g-DT), (ox+DT,   oy+hh-g),
        (ox,      oy+hh-g),    (ox,       oy+g+DT),
    ], fill=col(5))
    # middle
    draw.polygon([
        (ox+g,     oy+hh),     (ox+g+DT,    oy+hh-DT),
        (ox+DW-g-DT,oy+hh-DT),(ox+DW-g,    oy+hh),
        (ox+DW-g-DT,oy+hh+DT),(ox+g+DT,    oy+hh+DT),
    ], fill=col(6))


def _render_frame(number: int, scale: int = 3) -> Image.Image:
    """Render one frame: black bg, green 7-seg '0:XX' display."""
    S   = scale
    DW  = 70 * S
    DH  = 120 * S
    DT  = 9  * S
    GAP = 18 * S
    COL = 24 * S
    PAD = 30 * S

    W = DW + COL + GAP + DW + GAP + DW + PAD * 2
    H = DH + PAD * 2

    # ── Sharp layer ───────────────────────────────────────────────
    base = Image.new("RGB", (W, H), _BG)
    draw = ImageDraw.Draw(base)

    y   = PAD
    x0  = PAD                    # '0' minute digit
    cx  = x0 + DW + GAP//2 + COL//2   # colon centre
    x1  = cx - COL//2 + COL + GAP//2  # tens digit
    x2  = x1 + DW + GAP              # units digit

    tens  = str(number // 10)
    units = str(number % 10)

    _draw_segs(draw, '0',   x0, y, DW, DH, DT, _GREEN, _DIM)
    r = DT // 2 + 2
    q = DH // 4
    draw.ellipse([cx-r, y+DH//2-q-r, cx+r, y+DH//2-q+r], fill=_GREEN)
    draw.ellipse([cx-r, y+DH//2+q-r, cx+r, y+DH//2+q+r], fill=_GREEN)
    _draw_segs(draw, tens,  x1, y, DW, DH, DT, _GREEN, _DIM)
    _draw_segs(draw, units, x2, y, DW, DH, DT, _GREEN, _DIM)

    # ── Glow layer ────────────────────────────────────────────────
    glow = Image.new("RGB", (W, H), _BG)
    gd   = ImageDraw.Draw(glow)

    _draw_segs(gd, '0',   x0, y, DW, DH, DT, _BRIGHT, _BG)
    gd.ellipse([cx-r, y+DH//2-q-r, cx+r, y+DH//2-q+r], fill=_BRIGHT)
    gd.ellipse([cx-r, y+DH//2+q-r, cx+r, y+DH//2+q+r], fill=_BRIGHT)
    _draw_segs(gd, tens,  x1, y, DW, DH, DT, _BRIGHT, _BG)
    _draw_segs(gd, units, x2, y, DW, DH, DT, _BRIGHT, _BG)

    glow_blur = glow.filter(ImageFilter.GaussianBlur(radius=14))
    merged    = Image.blend(base, glow_blur, alpha=0.6)
    final     = Image.blend(merged, base, alpha=0.72)

    return final.resize((W // S, H // S), Image.LANCZOS)


def build_countdown_gif() -> bytes:
    """
    Build and return an animated GIF bytes object.
    10 frames (10 → 1), 1 second each.
    Display format: 0:10 → 0:09 → … → 0:01
    """
    frames = [_render_frame(n) for n in range(10, 0, -1)]

    buf = io.BytesIO()
    frames[0].save(
        buf,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=1000,
        loop=0,
        optimize=False,
    )
    buf.seek(0)
    return buf.read()
