import io, math
from PIL import Image, ImageDraw, ImageFont

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def font(path, size):
    try: return ImageFont.truetype(path, size)
    except: return ImageFont.load_default()

def draw_activity_chart(draw, x, y, w, h, data, color):
    max_val = max(data) or 1
    days = ["S", "M", "T", "W", "T", "F", "S"]
    bar_w = (w / 7) - 4
    for i, val in enumerate(data):
        bar_h = (val / max_val) * (h - 15)
        bx = x + i * (bar_w + 4)
        by = y + (h - bar_h) - 12
        draw.rectangle([bx, by, bx + bar_w, y + h - 12], fill=color)
        f_s = font(FONT_REG, 18)
        draw.text((bx + 2, y + h - 10), days[i], fill=(120, 115, 145), font=f_s)

def render_leaderboard(rows, title, activity_data=[0]*7):
    S=2; W, ROW_H, HDR_H = 700, 64, 110
    H = HDR_H + ROW_H*len(rows) + 45
    W2, H2 = W*S, H*S
    base = Image.new("RGB", (W2, H2), (250, 249, 247))
    draw = ImageDraw.Draw(base)
    
    # Header
    draw.rectangle([0, 0, W2, HDR_H*S], fill=(255, 255, 255))
    draw.text((30*S, 25*S), title.upper(), fill=(22, 18, 50), font=font(FONT_BOLD, 26*S))
    
    # Activity Chart in Header
    draw_activity_chart(draw, W2 - 180*S, 20*S, 150*S, 60*S, activity_data, (56, 189, 248))

    # Rows
    for i, row in enumerate(rows):
        y0 = (HDR_H*S) + i*(ROW_H*S)
        draw.rectangle([0, y0, W2, y0+(ROW_H*S)], fill=(255,255,255) if i%2==0 else (246,245,250))
        draw.text((80*S, y0+20*S), row.get("name", "User")[:15], fill=(22,18,50), font=font(FONT_BOLD, 15*S))
        pts_txt = f"{row.get('score', 0):,} pts"
        draw.text((W2-150*S, y0+20*S), pts_txt, fill=(22,18,50), font=font(FONT_BOLD, 15*S))

    buf = io.BytesIO()
    base.resize((W, H), Image.LANCZOS).save(buf, "PNG")
    buf.seek(0)
    return buf.read()
