import random
import io
from PIL import Image, ImageDraw, ImageFont
from config import GRID_SIZE, WORDS_PER_ROUND

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  THEMES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THEMES = {
    "animals": {
        "name": "Animals", "emoji": "🐾",
        "words": ["LION","TIGER","ELEPHANT","MONKEY","ZEBRA","GIRAFFE","PANDA",
                  "WOLF","EAGLE","SNAKE","BEAR","FOX","DEER","PARROT","CHEETAH",
                  "JAGUAR","HIPPO","RHINO","LEMUR","KOALA","BISON","LYNX"],
        "bg":          (10, 28, 48),
        "header_bg":   (6,  18, 34),
        "cell_bg":     (14, 42, 72),
        "cell_border": (28, 72, 110),
        "accent":      (56, 189, 248),
        "letter":      (220, 242, 255),
        "sub":         (120, 200, 240),
    },
    "fruits": {
        "name": "Fruits", "emoji": "🍎",
        "words": ["MANGO","APPLE","GRAPE","BANANA","ORANGE","PAPAYA","GUAVA",
                  "LEMON","PEACH","PLUM","CHERRY","MELON","LITCHI","KIWI",
                  "BERRY","PEAR","APRICOT","FIG","DATES","COCONUT","JACKFRUIT"],
        "bg":          (28, 10, 0),
        "header_bg":   (48, 18, 0),
        "cell_bg":     (44, 18, 2),
        "cell_border": (96, 48, 4),
        "accent":      (251, 146, 60),
        "letter":      (255, 220, 175),
        "sub":         (240, 170, 100),
    },
    "ocean": {
        "name": "Ocean", "emoji": "🌊",
        "words": ["SHARK","WHALE","DOLPHIN","OCTOPUS","CORAL","TURTLE","SQUID",
                  "CRAB","SALMON","LOBSTER","SEAHORSE","NARWHAL","CLAM",
                  "URCHIN","BARRACUDA","PUFFERFISH","MANATEE","SEAL","WALRUS","JELLYFISH"],
        "bg":          (0, 20, 45),
        "header_bg":   (0, 30, 60),
        "cell_bg":     (0, 28, 58),
        "cell_border": (0, 78, 130),
        "accent":      (34, 211, 238),
        "letter":      (200, 248, 255),
        "sub":         (100, 225, 245),
    },
    "space": {
        "name": "Space", "emoji": "🚀",
        "words": ["SATURN","JUPITER","MARS","VENUS","URANUS","METEOR","COMET",
                  "GALAXY","NEBULA","ASTEROID","ECLIPSE","COSMOS","ORBIT",
                  "PULSAR","QUASAR","NEUTRON","SUPERNOVA","HUBBLE","VOYAGER","PLUTO"],
        "bg":          (6, 2, 20),
        "header_bg":   (12, 4, 38),
        "cell_bg":     (14, 4, 44),
        "cell_border": (48, 18, 130),
        "accent":      (167, 139, 250),
        "letter":      (235, 228, 255),
        "sub":         (190, 170, 255),
    },
    "sports": {
        "name": "Sports", "emoji": "⚽",
        "words": ["CRICKET","TENNIS","HOCKEY","BOXING","RUGBY","POLO","CHESS",
                  "GOLF","KABADDI","ARCHERY","SWIMMING","CYCLING","ROWING",
                  "WRESTLING","JUDO","BADMINTON","VOLLEYBALL","BASKETBALL","MARATHON","FENCING"],
        "bg":          (2, 22, 4),
        "header_bg":   (4, 34, 6),
        "cell_bg":     (4, 30, 6),
        "cell_border": (8, 88, 12),
        "accent":      (74, 222, 128),
        "letter":      (215, 252, 225),
        "sub":         (130, 235, 165),
    },
    "countries": {
        "name": "Countries", "emoji": "🌍",
        "words": ["INDIA","JAPAN","BRAZIL","FRANCE","CHINA","EGYPT","SPAIN",
                  "KENYA","ITALY","PERU","NEPAL","GHANA","CANADA","RUSSIA",
                  "TURKEY","MEXICO","SWEDEN","NORWAY","FINLAND","DENMARK","NIGERIA"],
        "bg":          (28, 2, 38),
        "header_bg":   (48, 4, 58),
        "cell_bg":     (34, 4, 50),
        "cell_border": (84, 10, 130),
        "accent":      (232, 121, 249),
        "letter":      (250, 228, 255),
        "sub":         (235, 165, 252),
    },
    "food": {
        "name": "Food", "emoji": "🍕",
        "words": ["PIZZA","BURGER","NOODLES","SALAD","TACO","SUSHI","CURRY",
                  "BIRYANI","PASTA","SANDWICH","WAFFLE","PANCAKE","DUMPLING",
                  "RAMEN","KEBAB","BURRITO","GYOZA","FALAFEL","LASAGNA","SHAWARMA"],
        "bg":          (28, 6, 16),
        "header_bg":   (50, 10, 24),
        "cell_bg":     (36, 8, 18),
        "cell_border": (110, 24, 56),
        "accent":      (251, 113, 133),
        "letter":      (255, 228, 232),
        "sub":         (252, 160, 175),
    },
    "bollywood": {
        "name": "Bollywood", "emoji": "🎬",
        "words": ["SHOLAY","DILWALE","LAGAAN","DEVDAS","MUGHAL","BAJIRAO",
                  "DANGAL","BRAHMASTRA","PATHAAN","SINGHAM","DHOOM","KRRISH",
                  "DHAMAAL","GOLMAAL","BAAZIGAR","DEEWAR","AGNEEPATH","TAARE","ZINDAGI","GANGS"],
        "bg":          (28, 18, 0),
        "header_bg":   (52, 28, 0),
        "cell_bg":     (34, 22, 0),
        "cell_border": (110, 70, 4),
        "accent":      (251, 191, 36),
        "letter":      (255, 244, 200),
        "sub":         (252, 215, 100),
    },
}

THEME_LIST = list(THEMES.keys())

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GRID BUILDER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DIRS = [(0,1),(1,0),(0,-1),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]


def _empty(size: int) -> list:
    return [[""] * size for _ in range(size)]


def _place(grid: list, word: str, size: int):
    for _ in range(200):
        dr, dc = random.choice(DIRS)
        r, c   = random.randint(0, size-1), random.randint(0, size-1)
        er      = r + dr * (len(word)-1)
        ec      = c + dc * (len(word)-1)
        if not (0 <= er < size and 0 <= ec < size):
            continue
        cells, ok = [], True
        for i in range(len(word)):
            nr, nc = r+dr*i, c+dc*i
            if grid[nr][nc] not in ("", word[i]):
                ok = False; break
            cells.append((nr, nc))
        if ok:
            for (nr, nc), ch in zip(cells, word):
                grid[nr][nc] = ch
            return cells
    return None


def _fill(grid: list, size: int):
    alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for r in range(size):
        for c in range(size):
            if not grid[r][c]:
                grid[r][c] = random.choice(alpha)


def build_puzzle(theme_key: str, size: int = GRID_SIZE,
                 n_words: int = WORDS_PER_ROUND) -> tuple:
    """Returns (grid, words_list, placed_list)."""
    pool   = random.sample(THEMES[theme_key]["words"],
                           min(len(THEMES[theme_key]["words"]), n_words + 5))
    grid   = _empty(size)
    words, placed = [], []
    for w in pool:
        if len(words) >= n_words:
            break
        cells = _place(grid, w, size)
        if cells:
            words.append(w)
            placed.append({"word": w, "cells": cells})
    _fill(grid, size)
    return grid, words, placed


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  IMAGE RENDERER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CELL     = 44
PAD      = 16
HDR_H    = 80
CORNER   = 7

# Highlight colours for found words (RGBA)
HI_FILLS = [
    (56,189,248,100),(251,191,36,100),(167,139,250,100),(52,211,153,100),
    (248,113,113,100),(251,146,60,100),(196,181,253,100),(110,231,183,100),
]
HI_STROKES = [
    (56,189,248),(251,191,36),(167,139,250),(52,211,153),
    (248,113,113),(251,146,60),(196,181,253),(110,231,183),
]


def _rr(draw, x, y, w, h, r, fill=None, outline=None, width=1):
    draw.rounded_rectangle([x, y, x+w, y+h], radius=r,
                            fill=fill, outline=outline, width=width)


def _font(path: str, size: int):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def render_image(theme_key: str, grid: list, placed: list,
                 found_words: list, round_num: int,
                 size: int = GRID_SIZE) -> bytes:
    t = THEMES[theme_key]
    W = size * CELL + PAD * 2
    H = size * CELL + PAD * 2 + HDR_H

    base  = Image.new("RGB", (W, H), t["bg"])
    draw  = ImageDraw.Draw(base)

    # ── subtle dot-grid background ──
    dot_col = tuple(min(v+14, 255) for v in t["bg"])
    for x in range(0, W, 22):
        for y in range(0, H, 22):
            draw.ellipse([x-1, y-1, x+1, y+1], fill=dot_col)

    # ── header ──
    draw.rectangle([0, 0, W, HDR_H], fill=t["header_bg"])
    draw.rectangle([0, HDR_H-2, W, HDR_H], fill=t["accent"])  # accent line

    # fonts
    f_title  = _font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  21)
    f_sub    = _font("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",       12)
    f_letter = _font("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 17)
    f_tag    = _font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",   9)

    title = f"{t['name'].upper()}  WORD  GRID"
    tw    = draw.textlength(title, font=f_title)
    draw.text(((W-tw)/2, 12), title, fill=t["accent"], font=f_title)

    found_count = len(found_words)
    sub = (f"Find all hidden words!  •  {len(placed)} words  •  "
           f"Round {round_num}  •  Found: {found_count}/{len(placed)}")
    sw  = draw.textlength(sub, font=f_sub)
    draw.text(((W-sw)/2, 42), sub, fill=t["sub"], font=f_sub)

    # corner dots
    for cx, cy in [(PAD-5, HDR_H+PAD-5), (W-PAD+5, HDR_H+PAD-5),
                   (PAD-5, H-PAD+5),      (W-PAD+5, H-PAD+5)]:
        draw.ellipse([cx-4, cy-4, cx+4, cy+4], fill=t["accent"])

    # ── found-cell map ──
    found_map: dict = {}
    for fi, fw in enumerate(found_words):
        pw = next((p for p in placed if p["word"] == fw), None)
        if pw:
            for cell in pw["cells"]:
                found_map[cell] = fi

    # ── overlay for highlights ──
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov      = ImageDraw.Draw(overlay)

    # ── cells ──
    for r in range(size):
        for c in range(size):
            x = PAD + c * CELL
            y = HDR_H + PAD + r * CELL
            letter = grid[r][c]

            _rr(draw, x+1, y+1, CELL-2, CELL-2, CORNER,
                fill=t["cell_bg"], outline=t["cell_border"], width=1)

            if (r, c) in found_map:
                fi  = found_map[(r, c)]
                fc  = HI_FILLS[fi % len(HI_FILLS)]
                sc  = HI_STROKES[fi % len(HI_STROKES)]
                _rr(ov, x+1, y+1, CELL-2, CELL-2, CORNER,
                    fill=fc, outline=sc, width=2)

            lw = draw.textlength(letter, font=f_letter)
            draw.text((x+(CELL-lw)/2, y+(CELL-17)/2),
                      letter, fill=t["letter"], font=f_letter)

    # ── merge ──
    merged = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")

    # ── tiny word tag on first cell of each found word ──
    d2 = ImageDraw.Draw(merged)
    for fi, fw in enumerate(found_words):
        pw = next((p for p in placed if p["word"] == fw), None)
        if pw and pw["cells"]:
            r0, c0 = pw["cells"][0]
            x = PAD + c0*CELL + 3
            y = HDR_H + PAD + r0*CELL + 3
            sc = HI_STROKES[fi % len(HI_STROKES)]
            d2.text((x, y), fw[:4], fill=sc, font=f_tag)

    buf = io.BytesIO()
    merged.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return buf.read()
