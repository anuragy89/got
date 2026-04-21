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


sample=[
    {"name":"Shayyy",      "score":8610,  "words_found":1722},
    {"name":"Ria Rathore", "score":4355,  "words_found":871},
    {"name":"Depreciated", "score":4230,  "words_found":846},
    {"name":"Reiko",       "score":3750,  "words_found":750},
    {"name":"Cornetto",    "score":3045,  "words_found":609},
    {"name":"ANURAG",      "score":2335,  "words_found":467},
    {"name":"VORTEX",      "score":2205,  "words_found":441},
    {"name":"Rudra",       "score":1380,  "words_found":276},
    {"name":"Advik",       "score":900,   "words_found":180},
    {"name":"Reiko2",      "score":575,   "words_found":115},
]

with open("/home/claude/lb_light.png","wb") as f: f.write(render_leaderboard(sample,"Global Leaderboard"))
with open("/home/claude/tiers_light.png","wb") as f: f.write(render_rank_tiers())
print("done")
