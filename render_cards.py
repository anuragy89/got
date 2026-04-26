import io, math
from PIL import Image, ImageDraw, ImageFont

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

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
    (5000, "RUBY",     "#E8003A", "#2A0010", "#FF2060", "MAX"),
    (3000, "GOLD",     "#FFD700", "#1A1400", "#FFF060", "5,000"),
    (2500, "WORD GOD", "#D85A30", "#1A0A04", "#FF8050", "3,000"),
    (1001, "LEGEND",   "#7F77DD", "#0D0A20", "#AFA9EC", "2,500"),
    (501,  "DIAMOND",  "#378ADD", "#061428", "#85B7EB", "1,001"),
    (201,  "SILVER",   "#B4B2A9", "#141412", "#D3D1C7", "501"),
    (0,    "BRONZE",   "#EF9F27", "#180E00", "#FAC775", "201"),
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
) -> bytes:
    S = 2
    W = 700
    PAD = 26

    # ── Palette ──────────────────────────────────────────────────
    pal_idx = user_id % len(USER_PALETTES)
    CARD_BG, ACCENT, NAME_C, SUB_C, STAT_BG, STAT_BD = USER_PALETTES[pal_idx]
    ACCENT_LIGHT = tuple(min(255, int(c * 1.35)) for c in ACCENT)

    # ── Tier ─────────────────────────────────────────────────────
    tier_tag, tier_hex, tier_bg_hex, tier_glow_hex, next_label = _get_me_tier(words_found)
    TIER_C   = hex2rgb(tier_hex)
    TIER_BG  = hex2rgb(tier_bg_hex)
    TIER_GLW = hex2rgb(tier_glow_hex)
    done_xp, total_xp, xp_pct = _me_xp_progress(words_found)

    # ── Fonts ─────────────────────────────────────────────────────
    f_name  = font(FONT_BOLD, 22*S)
    f_sub   = font(FONT_REG,  13*S)
    f_tier  = font(FONT_BOLD, 14*S)
    f_stat  = font(FONT_BOLD, 20*S)
    f_slbl  = font(FONT_REG,  11*S)
    f_path  = font(FONT_BOLD, 10*S)
    f_xp    = font(FONT_REG,  11*S)
    f_init  = font(FONT_BOLD, 28*S)
    f_streak= font(FONT_BOLD, 15*S)

    # ── Height calc ───────────────────────────────────────────────
    # Top section: avatar + name + rank row + xp bar = ~200px
    # Stats row: 80px
    # Tier path: 60px
    # Streak bar: 60px
    # Group section (optional): 140px
    MAIN_H = 530
    GRPX_H = 150 if show_group else 0
    H = MAIN_H + GRPX_H
    W2, H2 = W*S, H*S

    base = Image.new("RGB", (W2, H2), CARD_BG)
    draw = ImageDraw.Draw(base)

    # ── Top accent bar ────────────────────────────────────────────
    draw.rectangle([0, 0, W2, 10*S], fill=ACCENT)
    draw.rectangle([0, 8*S, W2, 10*S], fill=ACCENT_LIGHT)

    # ── Avatar circle ─────────────────────────────────────────────
    AX, AY, AR = PAD*S + 44*S, 38*S, 44*S
    # Glow ring
    for r_off in range(6, 0, -1):
        alpha = int(80 * (r_off / 6))
        glow_col = tuple(int(c * alpha / 255) + int(CARD_BG[j] * (255-alpha) / 255)
                         for j, c in enumerate(TIER_GLW))
        draw.ellipse([AX-AR-r_off*2, AY-AR-r_off*2, AX+AR+r_off*2, AY+AR+r_off*2],
                     fill=glow_col)
    # Avatar border
    draw.ellipse([AX-AR-3, AY-AR-3, AX+AR+3, AY+AR+3], fill=TIER_C)
    # Avatar fill / photo
    if avatar_bytes:
        try:
            av_img = Image.open(io.BytesIO(avatar_bytes)).convert("RGB")
            av_img = av_img.resize((AR*2, AR*2), Image.LANCZOS)
            mask   = Image.new("L", (AR*2, AR*2), 0)
            ImageDraw.Draw(mask).ellipse([0, 0, AR*2, AR*2], fill=255)
            tmp    = Image.new("RGB", (AR*2, AR*2), CARD_BG)
            tmp.paste(av_img, (0, 0), mask)
            base.paste(tmp, (AX-AR, AY-AR), mask)
        except Exception:
            avatar_bytes = None
    if not avatar_bytes:
        draw.ellipse([AX-AR, AY-AR, AX+AR, AY+AR], fill=TIER_BG)
        ini = (name[:2] if len(name) >= 2 else name).upper()
        iw  = draw.textlength(ini, font=f_init)
        draw.text((AX - iw//2, AY - 17*S), ini, fill=TIER_C, font=f_init)

    # Tier badge under avatar
    badge_txt = tier_tag
    bw = int(draw.textlength(badge_txt, font=f_tier)) + 18*S
    bx = AX - bw//2
    by = AY + AR + 6*S
    rr(draw, bx, by, bw, 20*S, 10*S, fill=TIER_BG, outline=TIER_C, width=3)
    draw.text((bx + 9*S, by + 4*S), badge_txt, fill=TIER_C, font=f_tier)

    # ── Name + sub ────────────────────────────────────────────────
    NX = AX + AR + 18*S
    NY = 42*S
    trunc_name = name[:20]
    draw.text((NX, NY), trunc_name, fill=NAME_C, font=f_name)
    sub_txt = f"@{name.lower().replace(' ','_')}  ·  WordGrid Player"
    draw.text((NX, NY + 30*S), sub_txt, fill=SUB_C, font=f_sub)

    # ── Global rank pill + streak badge ──────────────────────────
    # Rank pill
    rank_txt = f"#{global_rank}  Global"
    rw2      = int(draw.textlength(rank_txt, font=f_sub)) + 20*S
    rr(draw, NX, NY + 54*S, rw2, 22*S, 11*S, fill=STAT_BG, outline=ACCENT, width=2)
    draw.text((NX + 10*S, NY + 58*S), rank_txt, fill=ACCENT_LIGHT, font=f_sub)
    # Streak badge
    streak_txt = f"🔥 {streak_days}d streak"
    sx = NX + rw2 + 12*S
    sw = int(draw.textlength(streak_txt, font=f_sub)) + 20*S
    STREAK_BG  = (26, 14, 0)
    STREAK_BD  = (216, 90, 48)
    STREAK_TXT = (255, 160, 96)
    rr(draw, sx, NY + 54*S, sw, 22*S, 11*S, fill=STREAK_BG, outline=STREAK_BD, width=2)
    draw.text((sx + 10*S, NY + 58*S), streak_txt, fill=STREAK_TXT, font=f_sub)

    # ── XP bar ───────────────────────────────────────────────────
    XP_Y  = NY + 90*S
    XP_X  = NX
    XP_W  = W2 - NX - PAD*S
    next_tier_name = ME_TIERS[max(0, [t[0] for t in ME_TIERS].index(
        next((t[0] for t in ME_TIERS if t[0] > words_found), ME_TIERS[0][0])
    )  if words_found < ME_TIERS[0][0] else 0)][1] if words_found < ME_TIERS[0][0] else "MAX"

    # label
    if tier_tag != "RUBY":
        xp_label = f"Progress to {next_label} words"
    else:
        xp_label = "Tier: RUBY — Maximum reached!"
    draw.text((XP_X, XP_Y - 16*S), xp_label, fill=SUB_C, font=f_xp)
    xp_val_txt = f"{words_found:,} words"
    xvw = int(draw.textlength(xp_val_txt, font=f_xp))
    draw.text((W2 - PAD*S - xvw, XP_Y - 16*S), xp_val_txt, fill=ACCENT_LIGHT, font=f_xp)
    # track
    rr(draw, XP_X, XP_Y, XP_W, 10*S, 5*S, fill=STAT_BG, outline=STAT_BD, width=1)
    # fill
    fw = max(int(XP_W * xp_pct), 10*S)
    rr(draw, XP_X, XP_Y, fw, 10*S, 5*S, fill=ACCENT)
    # shine strip
    rr(draw, XP_X, XP_Y, fw, 4*S, 4*S, fill=ACCENT_LIGHT)

    # ── Divider ───────────────────────────────────────────────────
    DIV_Y = XP_Y + 26*S
    draw.line([(PAD*S, DIV_Y), (W2 - PAD*S, DIV_Y)], fill=STAT_BD, width=1)

    # ── Stat boxes ───────────────────────────────────────────────
    STAT_Y  = DIV_Y + 16*S
    stats   = [
        (f"{score:,}", "total score", "pts"),
        (f"{words_found:,}", "words found", "all time"),
        (f"{rounds_won}/{rounds_played}", "rounds", f"{int(rounds_won/max(rounds_played,1)*100)}% win"),
    ]
    SB_W = (W2 - PAD*S*2 - 16*S*2) // 3
    SB_H = 78*S
    for i, (val, lbl, sub) in enumerate(stats):
        sx2 = PAD*S + i * (SB_W + 16*S)
        rr(draw, sx2, STAT_Y, SB_W, SB_H, 10*S, fill=STAT_BG, outline=STAT_BD, width=1)
        vw = int(draw.textlength(val, font=f_stat))
        draw.text((sx2 + SB_W//2 - vw//2, STAT_Y + 10*S), val, fill=NAME_C, font=f_stat)
        lw = int(draw.textlength(lbl, font=f_slbl))
        draw.text((sx2 + SB_W//2 - lw//2, STAT_Y + 38*S), lbl, fill=SUB_C, font=f_slbl)
        sw2 = int(draw.textlength(sub, font=f_slbl))
        draw.text((sx2 + SB_W//2 - sw2//2, STAT_Y + 54*S), sub, fill=ACCENT_LIGHT, font=f_slbl)

    # ── Tier path row ─────────────────────────────────────────────
    TP_Y    = STAT_Y + SB_H + 20*S
    tiers   = list(reversed(ME_TIERS))  # Bronze first → Ruby last
    n_tiers = len(tiers)
    arrow_w = 16*S
    usable  = W2 - PAD*S*2 - arrow_w*(n_tiers-1)
    pill_w  = usable // n_tiers
    pill_h  = 28*S

    active_idx = next((i for i,(mw,*_) in enumerate(tiers) if words_found >= mw), n_tiers-1)

    for i, (min_w, tag, acc, bg_h, glow_h, _) in enumerate(tiers):
        px  = PAD*S + i*(pill_w + arrow_w)
        is_done   = (i <= active_idx)
        is_active = (i == active_idx)
        P_ACC  = hex2rgb(acc)
        P_BG   = hex2rgb(bg_h)
        P_GLOW = hex2rgb(glow_h)

        if is_active:
            # Glowing active pill — multi-ring glow
            for r_off in range(5, 0, -1):
                gc = tuple(int(P_GLOW[j]*r_off/5 + CARD_BG[j]*(1-r_off/5)) for j in range(3))
                rr(draw, px-r_off*2, TP_Y-r_off*2, pill_w+r_off*4, pill_h+r_off*4,
                   pill_h//2+r_off, fill=gc)
            rr(draw, px, TP_Y, pill_w, pill_h, pill_h//2, fill=P_BG, outline=P_ACC, width=3)
        elif is_done:
            rr(draw, px, TP_Y, pill_w, pill_h, pill_h//2, fill=P_BG, outline=P_ACC, width=2)
        else:
            dim_bg  = tuple(max(0, c - 10) for c in CARD_BG)
            dim_bdr = tuple(int(c * 0.25) for c in P_ACC)
            dim_txt_col = tuple(int(c * 0.3) for c in P_ACC)
            rr(draw, px, TP_Y, pill_w, pill_h, pill_h//2, fill=dim_bg, outline=dim_bdr, width=1)
            tw2 = int(draw.textlength(tag, font=f_path))
            draw.text((px + pill_w//2 - tw2//2, TP_Y + 9*S), tag, fill=dim_txt_col, font=f_path)
            # Draw arrow and continue
            if i < n_tiers - 1:
                ax = px + pill_w + arrow_w//2 - 4*S
                ay = TP_Y + pill_h//2
                draw.text((ax, ay - 8*S), "›", fill=dim_bdr, font=f_tier)
            continue

        tw2 = int(draw.textlength(tag, font=f_path))
        draw.text((px + pill_w//2 - tw2//2, TP_Y + 9*S), tag,
                  fill=P_GLOW if is_active else P_ACC, font=f_path)

        # Arrow between pills
        if i < n_tiers - 1:
            ax = px + pill_w + arrow_w//2 - 4*S
            ay = TP_Y + pill_h//2
            next_done = (i+1 <= active_idx)
            arr_col = hex2rgb(tiers[i+1][2]) if next_done else tuple(int(c*0.25) for c in hex2rgb(tiers[i+1][2]))
            draw.text((ax, ay - 8*S), "›", fill=arr_col, font=f_tier)

    # ── Daily streak bar ─────────────────────────────────────────
    STR_Y = TP_Y + pill_h + 18*S
    SBAR_BG  = tuple(max(0, c - 8) for c in CARD_BG)
    draw.rectangle([0, STR_Y, W2, STR_Y + 60*S], fill=SBAR_BG)
    draw.line([(0, STR_Y), (W2, STR_Y)], fill=STAT_BD, width=1)

    # Flame icon + label
    flame_txt = "🔥"
    draw.text((PAD*S, STR_Y + 14*S), flame_txt, font=f_streak)
    streakbig = f"{streak_days}-day streak!"
    draw.text((PAD*S + 30*S, STR_Y + 12*S), streakbig, fill=(255,160,80), font=f_streak)
    sub_str   = "Play at least one round daily to keep it going"
    draw.text((PAD*S + 30*S, STR_Y + 32*S), sub_str, fill=(120,70,20), font=f_xp)

    # 7-dot week row
    DAYS = ["M","T","W","T","F","S","S"]
    dot_r    = 14*S
    dot_gap  = 8*S
    total_dw = len(DAYS)*(dot_r*2) + (len(DAYS)-1)*dot_gap
    dot_x0   = W2 - PAD*S - total_dw
    dot_y    = STR_Y + 15*S
    played_days = min(streak_days, 7)
    for di, day in enumerate(DAYS):
        dx = dot_x0 + di * (dot_r*2 + dot_gap)
        dy = dot_y
        if di < played_days - 1:
            draw.ellipse([dx, dy, dx+dot_r*2, dy+dot_r*2], fill=(216,90,48))
        elif di == played_days - 1:
            # Today — brighter
            draw.ellipse([dx-2, dy-2, dx+dot_r*2+2, dy+dot_r*2+2], fill=(255,160,80))
            draw.ellipse([dx, dy, dx+dot_r*2, dy+dot_r*2], fill=(255,200,100))
        else:
            draw.ellipse([dx, dy, dx+dot_r*2, dy+dot_r*2], fill=(40,20,5), outline=(80,40,10), width=1)
        dw2 = int(draw.textlength(day, font=f_xp))
        draw.text((dx + dot_r - dw2//2, dy + 10*S), day, fill=(255,255,255) if di < played_days else (60,35,10), font=f_xp)

    # ── Group section ─────────────────────────────────────────────
    if show_group and group_name:
        GRP_Y = MAIN_H*S
        draw.line([(0, GRP_Y), (W2, GRP_Y)], fill=STAT_BD, width=2)
        draw.rectangle([0, GRP_Y, W2, H2], fill=tuple(max(0, c-6) for c in CARD_BG))

        # Header
        grp_hdr = f"📍 {group_name[:28]}"
        draw.text((PAD*S, GRP_Y + 14*S), grp_hdr, fill=NAME_C, font=f_streak)
        grp_sub = f"Your rank in this chat"
        draw.text((PAD*S, GRP_Y + 36*S), grp_sub, fill=SUB_C, font=f_xp)

        # Group rank pill
        gr_txt = f"#{group_rank} in group"
        grw    = int(draw.textlength(gr_txt, font=f_sub)) + 20*S
        rr(draw, W2 - PAD*S - grw, GRP_Y + 14*S, grw, 24*S, 12*S,
           fill=STAT_BG, outline=ACCENT, width=2)
        draw.text((W2 - PAD*S - grw + 10*S, GRP_Y + 18*S), gr_txt, fill=ACCENT_LIGHT, font=f_sub)

        # Group stat boxes (3 mini boxes)
        grp_stats = [
            (f"{group_score:,}", "group pts"),
            (f"{group_words:,}", "words here"),
            (f"{group_rounds_won}", "rounds won"),
        ]
        GSB_W = (W2 - PAD*S*2 - 12*S*2) // 3
        GSB_H = 52*S
        GST_Y = GRP_Y + 68*S
        for i, (val, lbl) in enumerate(grp_stats):
            gsx = PAD*S + i*(GSB_W + 12*S)
            rr(draw, gsx, GST_Y, GSB_W, GSB_H, 8*S, fill=STAT_BG, outline=STAT_BD, width=1)
            vw3 = int(draw.textlength(val, font=f_streak))
            draw.text((gsx + GSB_W//2 - vw3//2, GST_Y + 8*S), val, fill=NAME_C, font=f_streak)
            lw3 = int(draw.textlength(lbl, font=f_slbl))
            draw.text((gsx + GSB_W//2 - lw3//2, GST_Y + 30*S), lbl, fill=SUB_C, font=f_slbl)

    # ── Footer watermark ─────────────────────────────────────────
    FTR_Y = H2 - 22*S
    ftxt  = "WordGrid Bot  •  /me"
    fw2   = int(draw.textlength(ftxt, font=f_xp))
    draw.text((W2//2 - fw2//2, FTR_Y), ftxt, fill=STAT_BD, font=f_xp)

    out = base.resize((W, H), Image.LANCZOS)
    buf = io.BytesIO()
    out.save(buf, "PNG", optimize=True, compress_level=6)
    buf.seek(0)
    return buf.read()
