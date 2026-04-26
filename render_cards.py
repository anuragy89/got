import io, math
from PIL import Image, ImageDraw, ImageFont

FONT_BOLD = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
FONT_REG  = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
# Fallbacks in case Noto isn't installed
import os as _os
if not _os.path.exists(FONT_BOLD):
    FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
if not _os.path.exists(FONT_REG):
    FONT_REG  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# ── Multi-script font map ─────────────────────────────────────────
# Maps script name → (bold_path, regular_path)
_SCRIPT_FONTS = {
    "arabic":     ("/usr/share/fonts/truetype/noto/NotoNaskhArabic-Bold.ttf",
                   "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf"),
    "devanagari": ("/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf",
                   "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf"),
    "cjk":        ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                   "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
}
_font_cache: dict = {}

def _script_of(ch: str) -> str:
    """Return the Unicode script family of a single character."""
    import unicodedata
    cp = ord(ch)
    if 0x0600 <= cp <= 0x06FF or 0x0750 <= cp <= 0x077F or 0xFB50 <= cp <= 0xFDFF or 0xFE70 <= cp <= 0xFEFF:
        return "arabic"
    if 0x0900 <= cp <= 0x097F:
        return "devanagari"
    if (0x4E00 <= cp <= 0x9FFF or 0x3000 <= cp <= 0x9FFF or
            0xAC00 <= cp <= 0xD7AF or 0x3040 <= cp <= 0x309F or 0x30A0 <= cp <= 0x30FF):
        return "cjk"
    try:
        name = unicodedata.name(ch, "")
        if "ARABIC"     in name: return "arabic"
        if "DEVANAGARI" in name: return "devanagari"
        if "CJK"        in name or "HIRAGANA" in name or "KATAKANA" in name: return "cjk"
        if "HANGUL"     in name: return "cjk"
    except Exception:
        pass
    return "latin"

def _get_script_font(script: str, size: int, bold: bool = True) -> "ImageFont.FreeTypeFont":
    """Return a cached font object for the given script and size."""
    key = (script, size, bold)
    if key in _font_cache:
        return _font_cache[key]
    paths = _SCRIPT_FONTS.get(script, (FONT_BOLD, FONT_REG))
    path  = paths[0] if bold else paths[1]
    try:
        f = ImageFont.truetype(path, size)
    except Exception:
        f = ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)
    _font_cache[key] = f
    return f

def draw_text_ms(draw, text: str, x: int, y: int, base_font,
                 fill, bold: bool = True) -> int:
    """
    Draw text with automatic per-character script-aware font selection.
    Returns the total pixel width drawn.
    """
    size = base_font.size
    cx   = x
    for ch in text:
        if ch == " ":
            cx += size // 3
            continue
        script = _script_of(ch)
        f = base_font if script == "latin" else _get_script_font(script, size, bold)
        try:
            w = int(draw.textlength(ch, font=f))
            draw.text((cx, y), ch, fill=fill, font=f)
            cx += w
        except Exception:
            cx += size // 2
    return cx - x

def measure_text_ms(draw, text: str, base_font, bold: bool = True) -> int:
    """Measure total width of multi-script text."""
    size  = base_font.size
    total = 0
    for ch in text:
        if ch == " ":
            total += size // 3
            continue
        script = _script_of(ch)
        f = base_font if script == "latin" else _get_script_font(script, size, bold)
        try:
            total += int(draw.textlength(ch, font=f))
        except Exception:
            total += size // 2
    return total

def font(path, size):
    try: return ImageFont.truetype(path, size)
    except: return ImageFont.load_default()

def rr(draw, x, y, w, h, r, fill=None, outline=None, width=1):
    draw.rounded_rectangle([x,y,x+w,y+h], radius=r, fill=fill, outline=outline, width=width)

def tc(draw, text, cx, y, f, color):
    tw = draw.textlength(text, font=f)
    draw.text((cx - tw/2, y), text, fill=color, font=f)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  RANK TIERS  — light theme matching the mockup
#  Colors from the widget:
#   Bronze  bg=#FAEEDA  border=#EF9F27  title=#633806  sub=#854F0B  bar=#BA7517
#   Silver  bg=#F1EFE8  border=#B4B2A9  title=#444441  sub=#5F5E5A  bar=#888780
#   Diamond bg=#E6F1FB  border=#85B7EB  title=#0C447C  sub=#185FA5  bar=#378ADD
#   Legend  bg=#EEEDFE  border=#AFA9EC  title=#3C3489  sub=#534AB7  bar=#7F77DD
#   WordGod bg=#FAECE7  border=#F0997B  title=#712B13  sub=#993C1D  bar=#D85A30
#   Speed   bg=#E1F5EE  border=#5DCAA5  title=#085041  sub=#0F6E56  bar=#1D9E75
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def hex2rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2],16) for i in (0,2,4))

TIERS = [
    {"tag":"BRONZE","sub":"Wordsmith","range":"0 – 200 words",
     "bg":"#FAEEDA","border":"#EF9F27","title":"#633806","sub_c":"#854F0B","bar":"#BA7517","bar_w":0.15},
    {"tag":"SILVER","sub":"Solver","range":"201 – 500 words",
     "bg":"#F1EFE8","border":"#B4B2A9","title":"#444441","sub_c":"#5F5E5A","bar":"#888780","bar_w":0.35},
    {"tag":"DIAMOND","sub":"Hunter","range":"501 – 1,000 words",
     "bg":"#E6F1FB","border":"#85B7EB","title":"#0C447C","sub_c":"#185FA5","bar":"#378ADD","bar_w":0.58},
    {"tag":"LEGEND","sub":"","range":"1,001 – 2,500 words",
     "bg":"#EEEDFE","border":"#AFA9EC","title":"#3C3489","sub_c":"#534AB7","bar":"#7F77DD","bar_w":0.78},
    {"tag":"WORD GOD","sub":"","range":"2,500+ words",
     "bg":"#FAECE7","border":"#F0997B","title":"#712B13","sub_c":"#993C1D","bar":"#D85A30","bar_w":1.0},
    {"tag":"SPEED DEMON","sub":"","range":"Fastest finder in round",
     "bg":"#E1F5EE","border":"#5DCAA5","title":"#085041","sub_c":"#0F6E56","bar":"#1D9E75","bar_w":0.65},
]

def render_rank_tiers() -> bytes:
    S=2
    W,H = 700,560
    W2,H2 = W*S, H*S

    PAGE_BG = (250,249,247)   # very light warm white
    HDR_BG  = (255,255,255)
    HDR_TXT = (30,25,60)
    SUB_TXT = (120,115,145)
    SEP     = (220,218,228)

    base = Image.new("RGB",(W2,H2), PAGE_BG)
    draw = ImageDraw.Draw(base)

    f_hdr   = font(FONT_BOLD, 28*S)
    f_sub   = font(FONT_REG,  13*S)
    f_tag   = font(FONT_BOLD, 17*S)
    f_name  = font(FONT_BOLD, 13*S)
    f_range = font(FONT_REG,  12*S)
    f_pct   = font(FONT_BOLD, 10*S)

    # header area
    HDR = 80*S
    draw.rectangle([0,0,W2,HDR], fill=HDR_BG)
    draw.line([(0,HDR),(W2,HDR)], fill=SEP, width=2)
    tc(draw,"RANK  TIERS",W2//2, 14*S, f_hdr, HDR_TXT)
    tc(draw,"Earned by total words found  •  WordGrid Bot",W2//2, 50*S, f_sub, SUB_TXT)

    PAD=18*S; COLS=2; ROWS=math.ceil(len(TIERS)/COLS)
    TW=(W2-PAD*3)//COLS
    TH=(H2-HDR-PAD*(ROWS+1))//ROWS
    R=12*S

    for idx,t in enumerate(TIERS):
        col=idx%COLS; row=idx//COLS
        x=PAD+col*(TW+PAD)
        y=HDR+PAD+row*(TH+PAD)

        bg  = hex2rgb(t["bg"])
        bdr = hex2rgb(t["border"])
        ttl = hex2rgb(t["title"])
        sc  = hex2rgb(t["sub_c"])
        bar = hex2rgb(t["bar"])

        # card
        rr(draw,x,y,TW,TH,R, fill=bg, outline=bdr, width=3)

        # left accent strip
        rr(draw,x,y,7*S,TH,R, fill=bdr)

        TX=x+20*S; TY=y+16*S

        # tag + subtitle on same line
        draw.text((TX,TY), t["tag"], fill=ttl, font=f_tag)
        if t["sub"]:
            tag_w = draw.textlength(t["tag"], font=f_tag)
            draw.text((TX+tag_w+6*S, TY+4*S), t["sub"], fill=sc, font=f_name)

        # range
        draw.text((TX, TY+34*S), t["range"], fill=sc, font=f_range)

        # progress bar
        BX=TX; BY=y+TH-22*S; BW=TW-50*S; BH=7*S; BR=4*S
        # bar bg (dimmed version of border color)
        bar_bg = tuple(int(bdr[j]*0.25 + bg[j]*0.75) for j in range(3))
        rr(draw,BX,BY,BW,BH,BR, fill=bar_bg)
        fw=max(int(BW*t["bar_w"]),BR*2)
        rr(draw,BX,BY,fw,BH,BR, fill=bar)
        pct_str=f"{int(t['bar_w']*100)}%"
        draw.text((BX+BW+6*S,BY-1*S), pct_str, fill=sc, font=f_pct)

    out = base.resize((W,H),Image.LANCZOS)
    buf = io.BytesIO()
    out.save(buf,"PNG",optimize=True,compress_level=6)
    buf.seek(0)
    return buf.read()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  LEADERBOARD  — light theme matching the mockup
#  Header:  white bg, dark title
#  Rows:    alternating white / light-gray
#  Avatar:  initials circle colored by tier
#  Badges:  pill with tier color bg + text
#  Bar:     tier color fill on gray track
#  Ranks:   gold/silver/bronze boxes for top 3
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TIER_LOOKUP = [
    (2500,"WORD GOD",  "#712B13","#FAECE7","#F0997B"),
    (1001,"LEGEND",    "#3C3489","#EEEDFE","#AFA9EC"),
    (501, "DIAMOND",   "#0C447C","#E6F1FB","#85B7EB"),
    (201, "SILVER",    "#444441","#F1EFE8","#B4B2A9"),
    (0,   "BRONZE",    "#633806","#FAEEDA","#EF9F27"),
]

def get_tier(words):
    for thr,name,txt,bg,bdr in TIER_LOOKUP:
        if words>=thr:
            return name, hex2rgb(txt), hex2rgb(bg), hex2rgb(bdr)
    return "BRONZE",hex2rgb("#633806"),hex2rgb("#FAEEDA"),hex2rgb("#EF9F27")

def render_leaderboard(rows:list, title:str="Global Leaderboard") -> bytes:
    S=2; W=700; ROW_H=64; HDR_H=90; FTR_H=40
    H = HDR_H + ROW_H*len(rows) + FTR_H + 6
    W2,H2=W*S,H*S; RH2=ROW_H*S; HDR2=HDR_H*S

    PAGE_BG  = (250,249,247)
    HDR_BG   = (255,255,255)
    ROW_A    = (255,255,255)
    ROW_B    = (246,245,250)
    SEP      = (228,225,235)
    HDR_TXT  = (22,18,50)
    SUB_TXT  = (120,115,145)
    DIM_TXT  = (160,155,180)
    NAME_COL = (22,18,50)
    FTR_BG   = (242,240,248)
    TRACK    = (220,218,228)

    GOLD_BG=(254,243,199); GOLD_BD=(202,138,4);   GOLD_TX=(120,80,0)
    SILV_BG=(241,245,249); SILV_BD=(148,163,184);  SILV_TX=(71,85,105)
    BRNZ_BG=(254,237,213); BRNZ_BD=(180,110,20);   BRNZ_TX=(120,70,10)
    RANK3=[(GOLD_BG,GOLD_BD,GOLD_TX,"#1"),(SILV_BG,SILV_BD,SILV_TX,"#2"),(BRNZ_BG,BRNZ_BD,BRNZ_TX,"#3")]

    base=Image.new("RGB",(W2,H2),PAGE_BG)
    draw=ImageDraw.Draw(base)

    f_hdr  = font(FONT_BOLD,26*S)
    f_sub  = font(FONT_REG, 13*S)
    f_rank = font(FONT_BOLD,15*S)
    f_name = font(FONT_BOLD,15*S)
    f_pts  = font(FONT_BOLD,14*S)
    f_wrd  = font(FONT_REG, 11*S)
    f_bdg  = font(FONT_BOLD,10*S)
    f_init = font(FONT_BOLD,14*S)

    # header
    draw.rectangle([0,0,W2,HDR2], fill=HDR_BG)
    draw.line([(0,HDR2),(W2,HDR2)], fill=SEP, width=2)
    tc(draw, title.upper(), W2//2, 14*S, f_hdr, HDR_TXT)
    tc(draw, f"Top {len(rows)} players  •  all time", W2//2, 48*S, f_sub, SUB_TXT)

    PAD=20*S
    max_sc=max(r.get("score",1) for r in rows) or 1

    for i,row in enumerate(rows):
        y0=HDR2+i*RH2
        draw.rectangle([0,y0,W2,y0+RH2], fill=ROW_A if i%2==0 else ROW_B)
        draw.line([(0,y0+RH2-1),(W2,y0+RH2-1)], fill=SEP, width=1)

        name  = row.get("name","?")[:18]
        score = row.get("score",0)
        words = row.get("words_found",0)
        tier_name, tier_txt, tier_bg, tier_bdr = get_tier(words)
        cy = y0 + RH2//2

        # rank badge
        if i<3:
            rb,rd,rt,rl = RANK3[i]
            rr(draw,PAD,cy-13*S,30*S,26*S,6*S, fill=rb, outline=rd, width=2)
            rw=draw.textlength(rl,font=f_rank)
            draw.text((PAD+15*S-rw/2,cy-11*S), rl, fill=rt, font=f_rank)
        else:
            rk=str(i+1)
            rw=draw.textlength(rk,font=f_rank)
            draw.text((PAD+15*S-rw/2,cy-11*S), rk, fill=DIM_TXT, font=f_rank)

        # avatar circle
        AX=PAD+48*S; AR=19*S
        draw.ellipse([AX-AR,cy-AR,AX+AR,cy+AR], fill=tier_bg, outline=tier_bdr, width=2)
        ini=name[0].upper()
        iw=draw.textlength(ini,font=f_init)
        draw.text((AX-iw/2,cy-11*S), ini, fill=tier_txt, font=f_init)

        # name
        NX=PAD+76*S
        draw.text((NX,cy-19*S), name, fill=NAME_COL, font=f_name)

        # tier badge pill
        bw=draw.textlength(tier_name,font=f_bdg)+10*S
        BY=cy+4*S; BH=15*S
        rr(draw,NX,BY,bw,BH,7*S, fill=tier_bg, outline=tier_bdr, width=1)
        draw.text((NX+5*S,BY+3*S), tier_name, fill=tier_txt, font=f_bdg)

        # score bar
        BAR_X=W2-215*S; BAR_Y=cy-5*S; BAR_W=108*S; BAR_H=6*S
        rr(draw,BAR_X,BAR_Y,BAR_W,BAR_H,3*S, fill=TRACK)
        fw=max(int(BAR_W*(score/max_sc)),4)
        if i<3:
            bc=(hex2rgb("#CA8A04"),hex2rgb("#94A3B8"),hex2rgb("#B46E14"))[i]
        else:
            bc=tier_bdr
        rr(draw,BAR_X,BAR_Y,fw,BAR_H,3*S, fill=bc)

        # pts + words
        pts_str=f"{score:,} pts"
        pw=draw.textlength(pts_str,font=f_pts)
        draw.text((W2-PAD-pw,cy-19*S), pts_str, fill=NAME_COL, font=f_pts)
        wrd_str=f"{words:,} words"
        ww=draw.textlength(wrd_str,font=f_wrd)
        draw.text((W2-PAD-ww,cy+8*S), wrd_str, fill=SUB_TXT, font=f_wrd)

    # footer
    FY=HDR2+len(rows)*RH2
    draw.rectangle([0,FY,W2,H2], fill=FTR_BG)
    draw.line([(0,FY),(W2,FY)], fill=SEP, width=1)
    tc(draw,"WordGrid Bot  •  /globalboard  •  /leaderboard",W2//2,FY+13*S,f_sub,DIM_TXT)

    out=base.resize((W,H),Image.LANCZOS)
    buf=io.BytesIO()
    out.save(buf,"PNG",optimize=True,compress_level=6)
    buf.seek(0)
    return buf.read()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /me PROFILE CARD
#  7 tiers: Bronze → Silver → Diamond → Legend
#           → Word God → Gold → Ruby
#  Per-user accent colour chosen from USER_PALETTES
#  based on user_id so it's always the same for
#  the same user but different across players.
#  Accepts optional avatar_bytes (JPEG/PNG) for
#  the profile photo circle.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Full 7-tier table used both for tier detection and the path row
ME_TIERS = [
    # (min_words, tag, accent_hex, bg_hex, glow_hex, next_threshold_label)
    # Order: highest first (for detection logic), display reverses this to Bronze→…→Word God
    (2500, "WORD GOD", "#D85A30", "#1A0A04", "#FF8050", "MAX"),
    (1001, "LEGEND",   "#7F77DD", "#0D0A20", "#AFA9EC", "2,500"),
    (501,  "DIAMOND",  "#378ADD", "#061428", "#85B7EB", "1,001"),
    (201,  "RUBY",     "#E8003A", "#2A0010", "#FF2060", "501"),
    (101,  "GOLD",     "#FFD700", "#1A1400", "#FFF060", "201"),
    (50,   "SILVER",   "#B4B2A9", "#141412", "#D3D1C7", "101"),
    (0,    "BRONZE",   "#EF9F27", "#180E00", "#FAC775", "50"),
]

# 12 per-user colour palettes — picked by user_id % 12
# Each: (card_bg, top_bar, name_col, sub_col, stat_bg, stat_border)
USER_PALETTES = [
    # 0  Deep blue
    ((8,18,40),   (55,138,221), (208,234,255), (80,130,185), (13,30,60),  (30,74,130)),
    # 1  Forest teal
    ((6,22,18),   (29,158,117), (180,255,225), (60,160,120), (10,36,28),  (20,100,70)),
    # 2  Royal purple
    ((16,10,34),  (127,119,221),(210,200,255), (100,90,190), (24,16,50),  (80,70,180)),
    # 3  Deep coral
    ((28,8,4),    (216,90,48),  (255,210,190), (180,90,60),  (40,14,8),   (150,60,30)),
    # 4  Crimson
    ((24,4,10),   (180,20,60),  (255,190,210), (200,80,110), (36,8,16),   (150,30,60)),
    # 5  Amber gold
    ((24,16,0),   (186,117,23), (255,235,160), (190,140,60), (36,24,4),   (140,90,20)),
    # 6  Arctic cyan
    ((4,20,28),   (29,158,200), (180,240,255), (60,160,200), (8,32,44),   (20,110,160)),
    # 7  Neon green
    ((6,20,6),    (80,180,60),  (190,255,180), (80,180,80),  (10,30,10),  (50,140,50)),
    # 8  Slate indigo
    ((10,10,24),  (100,90,200), (200,200,255), (100,100,200),(16,16,36),  (70,70,160)),
    # 9  Magenta pink
    ((24,4,20),   (200,60,180), (255,190,250), (200,80,180), (36,8,30),   (160,40,140)),
    # 10 Warm sunset
    ((24,10,0),   (220,100,30), (255,220,180), (200,120,60), (36,16,4),   (170,80,20)),
    # 11 Ice silver
    ((14,18,24),  (148,163,184),(220,230,245), (120,140,165),(22,28,38),  (100,120,150)),
]

def _get_me_tier(words_found: int):
    for min_w, tag, acc, bg, glow, nxt in ME_TIERS:
        if words_found >= min_w:
            return tag, acc, bg, glow, nxt
    return ME_TIERS[-1][1], ME_TIERS[-1][2], ME_TIERS[-1][3], ME_TIERS[-1][4], ME_TIERS[-1][5]

def _me_xp_progress(words_found: int):
    """Return (current_in_tier, tier_total, pct 0.0-1.0) for XP bar."""
    thresholds = [t[0] for t in ME_TIERS]  # [5000,3000,2500,1001,501,201,0]
    for i, (min_w, *_) in enumerate(ME_TIERS):
        if words_found >= min_w:
            if i == 0:   # MAX tier
                return words_found, words_found, 1.0
            prev = ME_TIERS[i-1][0]  # next tier threshold
            span = prev - min_w
            done = words_found - min_w
            return done, span, min(done / span, 1.0) if span else 1.0
    return 0, ME_TIERS[-1][0], 0.0

def render_me_card(
    name: str,
    user_id: int,
    words_found: int,
    score: int,
    global_rank: int,
    rounds_won: int,
    rounds_played: int,
    streak_days: int,
    group_score: int       = 0,
    group_rank: int        = 0,
    group_name: str        = "",
    group_words: int       = 0,
    group_rounds_won: int  = 0,
    avatar_bytes: bytes    = None,
    show_group: bool       = False,
    palette_idx: int       = -1,
) -> bytes:
    """
    Renders a profile card exactly matching the reference design:
    - Dark navy background (#0D1B2A)
    - Blue top border accent
    - Large avatar circle (left), name + username + rank/streak pills (right)
    - Thin divider line
    - Progress label + XP bar + word count
    - 3 stat boxes
    - Tier path pills
    - Streak bar at bottom with day dots
    Fixed single colour scheme — no random palette.
    """
    # ── Fixed colour scheme matching reference screenshot ─────────
    # Dark navy background, blue accent (matches the reference exactly)
    S       = 2
    W       = 700
    PAD     = 28

    CARD_BG      = (13, 27, 42)       # #0D1B2A  dark navy
    ACCENT       = (55, 138, 221)     # #378ADD  blue
    ACCENT_LIGHT = (130, 190, 255)    # lighter blue for shine/text
    NAME_C       = (240, 248, 255)    # near-white for name
    SUB_C        = (148, 175, 206)    # muted blue-grey for sub text
    STAT_BG      = (19, 38, 60)       # slightly lighter than card bg
    STAT_BD      = (35, 65, 105)      # border for stat boxes
    DIVIDER      = (30, 55, 90)       # thin divider lines

    # ── Tier detection ────────────────────────────────────────────
    tier_tag, tier_hex, tier_bg_hex, tier_glow_hex, next_label = _get_me_tier(words_found)
    TIER_C   = hex2rgb(tier_hex)
    TIER_BG  = hex2rgb(tier_bg_hex)
    TIER_GLW = hex2rgb(tier_glow_hex)
    done_xp, total_xp, xp_pct = _me_xp_progress(words_found)

    # ── Canvas size ───────────────────────────────────────────────
    # Matches reference proportions: wide card, sections stacked cleanly
    CARD_W  = W
    # Section heights (logical px before ×S):
    #   Top bar       : 5
    #   Header area   : 195  (avatar + name + rank/streak + xp bar)
    #   Divider       : 1
    #   Stats         : 115
    #   Tier path     : 70
    #   Streak bar    : 80
    #   Footer        : 24
    CARD_H  = 5 + 195 + 2 + 115 + 70 + 80 + 24
    W2, H2  = CARD_W * S, CARD_H * S

    base = Image.new("RGB", (W2, H2), CARD_BG)
    draw = ImageDraw.Draw(base)

    # ── Fonts — bigger sizes matching reference ───────────────────
    f_name   = font(FONT_BOLD, 26*S)   # large name
    f_sub    = font(FONT_REG,  13*S)   # @username, sub labels
    f_tier   = font(FONT_BOLD, 11*S)   # tier badge text
    f_stat_v = font(FONT_BOLD, 22*S)   # stat value (78,468)
    f_stat_l = font(FONT_REG,  12*S)   # stat label (total score)
    f_stat_s = font(FONT_BOLD, 11*S)   # stat sub (pts / all time)
    f_path   = font(FONT_BOLD, 10*S)   # tier path pill text
    f_xp     = font(FONT_REG,  12*S)   # xp bar labels
    f_init   = font(FONT_BOLD, 30*S)   # initials in avatar
    f_streak = font(FONT_BOLD, 14*S)   # streak bold text
    f_streak_s = font(FONT_REG, 11*S)  # streak sub text
    f_arrow  = font(FONT_BOLD, 13*S)   # › arrows between tier pills

    # ── Top accent bar (5px blue line) ────────────────────────────
    draw.rectangle([0, 0, W2, 5*S], fill=ACCENT)

    # ──────────────────────────────────────────────────────────────
    #  HEADER SECTION  (y: 5 → 200)
    # ──────────────────────────────────────────────────────────────
    HDR_TOP = 5   # px from top (after accent bar)

    # Avatar: centred at x=85, y=HDR_TOP+95 (in logical px)
    AX = 85 * S
    AY = (HDR_TOP + 95) * S
    AR = 52 * S   # radius — bigger circle like reference

    # Glow ring around avatar (tier colour)
    for r_off in range(8, 0, -1):
        t   = r_off / 8
        gc  = tuple(int(TIER_GLW[j] * t * 0.5 + CARD_BG[j] * (1 - t * 0.5))
                    for j in range(3))
        draw.ellipse([AX-AR-r_off*3, AY-AR-r_off*3,
                      AX+AR+r_off*3, AY+AR+r_off*3], fill=gc)

    # Avatar border ring (tier colour, 3px)
    draw.ellipse([AX-AR-3*S//2, AY-AR-3*S//2,
                  AX+AR+3*S//2, AY+AR+3*S//2], fill=TIER_C)

    # Avatar fill / profile photo
    if avatar_bytes:
        try:
            av_img = Image.open(io.BytesIO(avatar_bytes)).convert("RGB")
            # Resize to fill the full circle diameter
            diam = AR * 2
            av_img = av_img.resize((diam, diam), Image.LANCZOS)
            mask   = Image.new("L", (diam, diam), 0)
            ImageDraw.Draw(mask).ellipse([0, 0, diam, diam], fill=255)
            tmp    = Image.new("RGB", (diam, diam), CARD_BG)
            tmp.paste(av_img, (0, 0), mask)
            base.paste(tmp, (AX - AR, AY - AR), mask)
        except Exception:
            avatar_bytes = None   # fall through to initials

    if not avatar_bytes:
        draw.ellipse([AX-AR, AY-AR, AX+AR, AY+AR], fill=TIER_BG)
        ini = (name[:2] if len(name) >= 2 else name[0:1]).upper()
        iw  = measure_text_ms(draw, ini, f_init, bold=True)
        draw_text_ms(draw, ini, AX - iw // 2, AY - 18*S, f_init, fill=TIER_C, bold=True)

    # Tier badge pill — centred under avatar
    bdg_txt = tier_tag
    bdg_w   = int(draw.textlength(bdg_txt, font=f_tier)) + 16*S
    bdg_h   = 18*S
    bdg_x   = AX - bdg_w // 2
    bdg_y   = AY + AR + 6*S
    rr(draw, bdg_x, bdg_y, bdg_w, bdg_h, bdg_h // 2,
       fill=TIER_BG, outline=TIER_C, width=2*S//2)
    tw_ = int(draw.textlength(bdg_txt, font=f_tier))
    draw.text((bdg_x + (bdg_w - tw_) // 2, bdg_y + 4*S),
              bdg_txt, fill=TIER_C, font=f_tier)

    # Name text — to the right of avatar
    NX = (85 + 52 + 22) * S   # avatar centre + radius + gap
    NY = (HDR_TOP + 22) * S

    trunc_name = name[:22]
    draw_text_ms(draw, trunc_name, NX, NY, f_name, fill=NAME_C, bold=True)

    # @username · WordGrid Player
    sub_line = f"@{name.lower().replace(' ','_')}  ·  WordGrid Player"
    draw_text_ms(draw, sub_line, NX, NY + 32*S, f_sub, fill=SUB_C, bold=False)

    # Global rank pill  ──  filled dark, blue border
    PILL_Y = NY + 58*S
    PILL_H = 26*S

    rank_txt = f"#{global_rank}  Global rank"
    rk_w     = int(draw.textlength(rank_txt, font=f_sub)) + 24*S
    rr(draw, NX, PILL_Y, rk_w, PILL_H, PILL_H // 2,
       fill=STAT_BG, outline=ACCENT, width=max(1, S//1))
    draw.text((NX + 12*S, PILL_Y + 6*S), rank_txt, fill=ACCENT_LIGHT, font=f_sub)

    # Streak pill  ──  dark bg, orange/red border + small orange dot
    STK_BG  = (22, 11, 2)
    STK_BD  = (210, 80, 40)
    STK_TXT = (255, 150, 80)
    stk_txt  = f"{streak_days}  day streak"
    stk_x    = NX + rk_w + 14*S
    dot_sz   = 8*S   # small circle diameter
    stk_w    = dot_sz + 6*S + int(draw.textlength(stk_txt, font=f_sub)) + 24*S
    rr(draw, stk_x, PILL_Y, stk_w, PILL_H, PILL_H // 2,
       fill=STK_BG, outline=STK_BD, width=max(1, S//1))
    # Small orange dot (flame indicator)
    dot_cx = stk_x + 12*S
    dot_cy_center = PILL_Y + PILL_H // 2
    draw.ellipse([dot_cx, dot_cy_center - dot_sz//2,
                  dot_cx + dot_sz, dot_cy_center + dot_sz//2], fill=(255, 120, 40))
    draw.text((dot_cx + dot_sz + 6*S, PILL_Y + 6*S), stk_txt, fill=STK_TXT, font=f_sub)

    # XP progress bar  ──  spans full width from NX to right edge
    XP_TOP = PILL_Y + PILL_H + 16*S
    XP_X   = NX
    XP_W   = W2 - NX - PAD*S
    XP_H   = 9*S

    # label left
    if tier_tag != "RUBY":
        xp_lbl = f"Progress to {next_label}"
    else:
        xp_lbl = "Maximum tier reached!"
    draw.text((XP_X, XP_TOP - 16*S), xp_lbl, fill=SUB_C, font=f_xp)
    # label right — words count
    xp_rval = f"{words_found:,} / {next_label} words" if tier_tag != "RUBY" else f"{words_found:,} words"
    xrvw = int(draw.textlength(xp_rval, font=f_xp))
    draw.text((W2 - PAD*S - xrvw, XP_TOP - 16*S), xp_rval, fill=ACCENT_LIGHT, font=f_xp)
    # track
    rr(draw, XP_X, XP_TOP, XP_W, XP_H, XP_H // 2, fill=STAT_BD)
    # fill
    fill_w = max(int(XP_W * xp_pct), XP_H)
    rr(draw, XP_X, XP_TOP, fill_w, XP_H, XP_H // 2, fill=ACCENT)
    # shine
    rr(draw, XP_X, XP_TOP, fill_w, XP_H // 2, XP_H // 2, fill=ACCENT_LIGHT)

    # Thin divider below header
    DIV_Y = (HDR_TOP + 195) * S
    draw.line([(0, DIV_Y), (W2, DIV_Y)], fill=DIVIDER, width=S)

    # ──────────────────────────────────────────────────────────────
    #  STAT BOXES  (y: 200 → 315)
    # ──────────────────────────────────────────────────────────────
    STAT_TOP = DIV_Y + 14*S
    win_pct  = int(rounds_won / max(rounds_played, 1) * 100)
    stats    = [
        (f"{score:,}",             "Total score",  "pts"),
        (f"{words_found:,}",       "Words found",  "all time"),
        (f"{rounds_won}/{rounds_played}", "Rounds won", f"{win_pct}% win rate"),
    ]
    GAP_S  = 14*S
    SB_W   = (W2 - PAD*S*2 - GAP_S*2) // 3
    SB_H   = 100*S

    for i, (val, lbl, sub) in enumerate(stats):
        bx = PAD*S + i * (SB_W + GAP_S)
        rr(draw, bx, STAT_TOP, SB_W, SB_H, 10*S, fill=STAT_BG, outline=STAT_BD, width=S)
        # value (big)
        vw = int(draw.textlength(val, font=f_stat_v))
        draw.text((bx + (SB_W - vw) // 2, STAT_TOP + 14*S), val, fill=NAME_C, font=f_stat_v)
        # label
        lw = int(draw.textlength(lbl, font=f_stat_l))
        draw.text((bx + (SB_W - lw) // 2, STAT_TOP + 46*S), lbl, fill=SUB_C, font=f_stat_l)
        # sub
        sw = int(draw.textlength(sub, font=f_stat_s))
        draw.text((bx + (SB_W - sw) // 2, STAT_TOP + 65*S), sub, fill=ACCENT_LIGHT, font=f_stat_s)

    # ──────────────────────────────────────────────────────────────
    #  TIER PATH  (y: 315 → 385)
    # ──────────────────────────────────────────────────────────────
    TP_TOP  = STAT_TOP + SB_H + 20*S
    tiers   = list(reversed(ME_TIERS))   # Bronze first → Ruby last
    n_t     = len(tiers)
    ARR_W   = 14*S
    usable  = W2 - PAD*S*2 - ARR_W*(n_t - 1)
    pill_w  = usable // n_t
    pill_h  = 28*S

    # "Tier path" label
    draw.text((PAD*S, TP_TOP - 18*S), "Tier path", fill=SUB_C, font=f_stat_l)

    # Find which pill is active: highest tier the user has reached
    # tiers list is Bronze→Ruby (left to right), so active = rightmost qualifying
    active_idx = 0
    for i, (min_w, *_) in enumerate(tiers):
        if words_found >= min_w:
            active_idx = i   # keep updating — last match = highest tier reached

    for i, (min_w, tag, acc, bg_h, glow_h, _) in enumerate(tiers):
        px      = PAD*S + i * (pill_w + ARR_W)
        P_ACC   = hex2rgb(acc)
        P_BG    = hex2rgb(bg_h)
        P_GLOW  = hex2rgb(glow_h)
        is_active = (i == active_idx)
        is_done   = (i <= active_idx)

        if is_active:
            # Glowing highlighted pill
            for r_off in range(5, 0, -1):
                gc = tuple(int(P_GLOW[j] * r_off/5 + CARD_BG[j] * (1 - r_off/5))
                           for j in range(3))
                rr(draw, px - r_off*2, TP_TOP - r_off*2,
                   pill_w + r_off*4, pill_h + r_off*4,
                   pill_h // 2 + r_off, fill=gc)
            rr(draw, px, TP_TOP, pill_w, pill_h, pill_h // 2,
               fill=P_BG, outline=P_ACC, width=3)
            tw2 = int(draw.textlength(tag, font=f_path))
            draw.text((px + (pill_w - tw2) // 2, TP_TOP + 9*S),
                      tag, fill=P_GLOW, font=f_path)
        elif is_done:
            rr(draw, px, TP_TOP, pill_w, pill_h, pill_h // 2,
               fill=P_BG, outline=P_ACC, width=2)
            tw2 = int(draw.textlength(tag, font=f_path))
            draw.text((px + (pill_w - tw2) // 2, TP_TOP + 9*S),
                      tag, fill=P_ACC, font=f_path)
        else:
            dim_bg  = tuple(max(0, c - 8) for c in CARD_BG)
            dim_bdr = tuple(int(c * 0.35) for c in P_ACC)
            dim_txt = tuple(int(c * 0.55) for c in P_ACC)   # brighter — more readable
            rr(draw, px, TP_TOP, pill_w, pill_h, pill_h // 2,
               fill=dim_bg, outline=dim_bdr, width=1)
            tw2 = int(draw.textlength(tag, font=f_path))
            draw.text((px + (pill_w - tw2) // 2, TP_TOP + 9*S),
                      tag, fill=dim_txt, font=f_path)

        # Arrow › between pills
        if i < n_t - 1:
            ax   = px + pill_w + ARR_W // 2 - 5*S
            ay   = TP_TOP + pill_h // 2 - 8*S
            next_done = (i + 1 <= active_idx)
            if next_done:
                arr_c = hex2rgb(tiers[i+1][2])
            else:
                arr_c = tuple(int(c * 0.22) for c in hex2rgb(tiers[i+1][2]))
            draw.text((ax, ay), "›", fill=arr_c, font=f_arrow)

    # ──────────────────────────────────────────────────────────────
    #  STREAK BAR  (y: 385 → 465)
    # ──────────────────────────────────────────────────────────────
    STR_TOP = TP_TOP + pill_h + 18*S
    SBAR_BG = tuple(max(0, c - 6) for c in CARD_BG)
    draw.rectangle([0, STR_TOP, W2, STR_TOP + 72*S], fill=SBAR_BG)
    draw.line([(0, STR_TOP), (W2, STR_TOP)], fill=DIVIDER, width=S)

    # Flame icon drawn as simple orange circle + text "🔥" fallback with text label
    flame_x = PAD*S
    flame_y = STR_TOP + 12*S
    # Draw a small orange flame circle as visual indicator
    fc = 16*S
    draw.ellipse([flame_x, flame_y + 2*S, flame_x + fc, flame_y + fc + 2*S], fill=(216, 90, 48))
    draw.ellipse([flame_x + 3*S, flame_y + 4*S, flame_x + fc - 3*S, flame_y + fc - 2*S], fill=(255, 160, 80))
    big_str = f"{streak_days}-day streak — keep it going!"
    draw.text((flame_x + fc + 8*S, flame_y + 2*S), big_str,
              fill=(255, 160, 80), font=f_streak)
    sub_str = "Play at least one round today to extend it"
    draw.text((flame_x + fc + 8*S, flame_y + 22*S), sub_str,
              fill=(140, 80, 30), font=f_streak_s)

    # 7 day-dot circles (right side)
    DAYS      = ["M", "T", "W", "T", "F", "S", "S"]
    dot_r     = 16*S
    dot_gap   = 6*S
    total_dw  = len(DAYS) * dot_r*2 + (len(DAYS) - 1) * dot_gap
    dot_x0    = W2 - PAD*S - total_dw
    dot_cy    = STR_TOP + 36*S     # centre y of dots
    played    = min(streak_days, 7)

    for di, day in enumerate(DAYS):
        dx = dot_x0 + di * (dot_r*2 + dot_gap)
        dy = dot_cy - dot_r
        if di < played - 1:
            fill_c = (216, 90, 48)    # played days — orange
        elif di == played - 1:
            # Today — brightest
            draw.ellipse([dx - 2, dy - 2, dx + dot_r*2 + 2, dy + dot_r*2 + 2],
                         fill=(255, 160, 80))
            fill_c = (255, 200, 100)
        else:
            fill_c = (50, 28, 8)      # future — dark but not invisible
        draw.ellipse([dx, dy, dx + dot_r*2, dy + dot_r*2], fill=fill_c)
        dw2 = int(draw.textlength(day, font=f_streak_s))
        # Always white text — visible on both orange and dark circles
        draw.text((dx + dot_r - dw2 // 2, dot_cy - 7*S), day,
                  fill=(255, 255, 255), font=f_streak_s)

    # ──────────────────────────────────────────────────────────────
    #  FOOTER watermark
    # ──────────────────────────────────────────────────────────────
    FTR_Y = H2 - 20*S
    ftxt  = "WordGrid Bot  •  /me"
    fw    = int(draw.textlength(ftxt, font=f_streak_s))
    draw.text((W2 // 2 - fw // 2, FTR_Y), ftxt, fill=DIVIDER, font=f_streak_s)

    # ── Final output ─────────────────────────────────────────────
    out = base.resize((CARD_W, CARD_H), Image.LANCZOS)
    buf = io.BytesIO()
    out.save(buf, "PNG", optimize=True, compress_level=6)
    buf.seek(0)
    return buf.read()
