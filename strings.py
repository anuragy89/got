from config import (
    USE_PREMIUM_EMOJI,
    PEMOJI_TROPHY, PEMOJI_FIRE, PEMOJI_STAR, PEMOJI_CROWN,
    PEMOJI_DIAMOND, PEMOJI_LIGHTNING, PEMOJI_PUZZLE,
    PEMOJI_ROCKET, PEMOJI_JOYSTICK, PEMOJI_MEDAL,
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PREMIUM EMOJI HELPER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _pe(eid: str, fallback: str) -> str:
    if USE_PREMIUM_EMOJI:
        return f'<tg-emoji emoji-id="{eid}">{fallback}</tg-emoji>'
    return fallback

def ICO_TROPHY():    return _pe(PEMOJI_TROPHY,    "🏆")
def ICO_FIRE():      return _pe(PEMOJI_FIRE,      "🔥")
def ICO_STAR():      return _pe(PEMOJI_STAR,      "⭐")
def ICO_CROWN():     return _pe(PEMOJI_CROWN,     "👑")
def ICO_DIAMOND():   return _pe(PEMOJI_DIAMOND,   "💎")
def ICO_LIGHTNING(): return _pe(PEMOJI_LIGHTNING, "⚡")
def ICO_PUZZLE():    return _pe(PEMOJI_PUZZLE,     "🧩")
def ICO_ROCKET():    return _pe(PEMOJI_ROCKET,    "🚀")
def ICO_JOYSTICK():  return _pe(PEMOJI_JOYSTICK,  "🕹️")
def ICO_MEDAL():     return _pe(PEMOJI_MEDAL,     "🎖️")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  START — PRIVATE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def start_private(name: str) -> str:
    return (
        f"{ICO_ROCKET()} <b>Hey {name}, welcome to WordGrid Bot!</b>\n\n"
        f"{ICO_PUZZLE()} I'm a <b>Word Grid Puzzle Game Bot</b> made for Telegram groups.\n"
        f"I drop beautiful themed grid images — you find hidden words!\n\n"
        f"<b>┌ How to play</b>\n"
        f"<b>│</b> {ICO_JOYSTICK()} Bot drops a colourful themed grid in your group\n"
        f"<b>│</b> {ICO_LIGHTNING()} Type any word you spot to claim it\n"
        f"<b>│</b> {ICO_FIRE()} Build combos for up to <b>3×</b> bonus points\n"
        f"<b>│</b> {ICO_TROPHY()} Most words found = <b>WINNER</b>!\n"
        f"<b>└────────────────────</b>\n\n"
        f"<b>┌ Themes</b>\n"
        f"<b>│</b> 🐾 Animals  🍎 Fruits  🌊 Ocean  🚀 Space\n"
        f"<b>│</b> ⚽ Sports  🌍 Countries  🍕 Food  🎬 Bollywood\n"
        f"<b>└────────────────────</b>\n\n"
        f"{ICO_DIAMOND()} <b>Add me to your group and start playing now!</b>"
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  START — GROUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def start_group() -> str:
    return (
        f"{ICO_PUZZLE()} <b>WordGrid Bot is ready!</b>\n\n"
        f"Use /newgame to start a round.\n"
        f"Use /help to see all commands."
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ADDED TO NEW GROUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def new_group_welcome(title: str) -> str:
    return (
        f"{ICO_ROCKET()} <b>WordGrid Bot just landed in {title}!</b>\n\n"
        f"{ICO_JOYSTICK()} I bring <b>Word Grid Puzzle Games</b> to your group.\n\n"
        f"<b>┌ Quick start</b>\n"
        f"<b>│</b> /newgame — Start a round right now\n"
        f"<b>│</b> /theme — Pick a fun theme\n"
        f"<b>│</b> /leaderboard — See top players\n"
        f"<b>│</b> /help — Full command list\n"
        f"<b>└────────────────────</b>\n\n"
        f"<b>┌ How it works</b>\n"
        f"<b>│</b> {ICO_PUZZLE()} I send a beautiful themed grid image\n"
        f"<b>│</b> {ICO_LIGHTNING()} Type words you find — claim them!\n"
        f"<b>│</b> {ICO_FIRE()} Consecutive finds = combo multiplier\n"
        f"<b>│</b> {ICO_TROPHY()} Highest score wins the round\n"
        f"<b>└────────────────────</b>\n\n"
        f"{ICO_CROWN()} Ready? Type /newgame to begin!"
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  HELP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def help_text() -> str:
    return (
        f"{ICO_PUZZLE()} <b>WordGrid Bot — Commands</b>\n\n"
        f"{ICO_JOYSTICK()} <b>Game</b>\n"
        f"  /newgame — Start a round (random theme)\n"
        f"  /newgame [theme] — e.g. /newgame space\n"
        f"  /theme — Browse & pick a theme\n"
        f"  /endgame — End round early (admins)\n\n"
        f"{ICO_TROPHY()} <b>Leaderboard</b>\n"
        f"  /leaderboard — This group's top 10\n"
        f"  /globalboard — All-time global top 10\n"
        f"  /mystats — Your personal stats\n"
        f"  /resetboard — Reset group board (admins)\n\n"
        f"{ICO_FIRE()} <b>Themes</b>\n"
        f"  animals • fruits • ocean • space\n"
        f"  sports • countries • food • bollywood\n\n"
        f"{ICO_LIGHTNING()} <b>Scoring</b>\n"
        f"  Base = word_length × 10 pts\n"
        f"  First finder bonus = +25 pts\n"
        f"  Combo ×1.5 → ×2.0 → ×2.5 → ×3.0\n\n"
        f"{ICO_STAR()} <b>Combo</b>\n"
        f"  2 correct in a row → ×1.5\n"
        f"  3 in a row → ×2.0\n"
        f"  4 in a row → ×2.5\n"
        f"  5+ in a row → ×3.0"
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GAME START (caption for grid photo)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def game_start_caption(theme_name: str, theme_emoji: str,
                       round_num: int, n_words: int, duration: int) -> str:
    return (
        f"{ICO_PUZZLE()} <b>Round {round_num} — {theme_emoji} {theme_name} Theme!</b>\n\n"
        f"Find <b>{n_words} hidden words</b> in the grid!\n"
        f"Type any word you spot to claim it {ICO_FIRE()}\n\n"
        f"{ICO_LIGHTNING()} Timer: <b>{duration}s</b>  |  "
        f"{ICO_STAR()} Build combos for bonus points!"
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  WORD FOUND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def word_found(name: str, word: str, pts: int, combo: int, left: int) -> str:
    combo_txt = f"  {ICO_FIRE()} ×{combo} combo!" if combo >= 2 else ""
    return (
        f"{ICO_STAR()} <b>{name}</b> found <code>{word}</code>! "
        f"<b>+{pts} pts</b>{combo_txt}\n"
        f"<i>{left} word(s) still hidden</i>"
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ROUND END
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MEDALS = ["🥇", "🥈", "🥉"]

def round_end(summary: list, missed: list, theme_name: str) -> str:
    lines = [f"{ICO_CROWN()} <b>Round Over! — {theme_name}</b>",
             "━" * 26]
    if not summary:
        lines.append("<i>No one scored this round!</i>")
    else:
        for i, row in enumerate(summary[:5]):
            med = MEDALS[i] if i < 3 else f"  {i+1}."
            lines.append(f"{med} <b>{row['name']}</b> — {row['score']} pts  "
                         f"<i>({row['words']} words)</i>")
        lines.append("")
        lines.append(f"{ICO_TROPHY()} <b>Winner: {summary[0]['name']}</b>  🎉")

    if missed:
        lines.append("")
        lines.append(f"{ICO_PUZZLE()} <b>Missed:</b> {', '.join(missed)}")

    lines.append("")
    lines.append("Type /newgame to play again!")
    return "\n".join(lines)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  LEADERBOARD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def leaderboard_text(rows: list, title: str) -> str:
    if not rows:
        return (f"{ICO_TROPHY()} <b>{title}</b>\n\n"
                "No scores yet — play /newgame to get started!")
    lines = [f"{ICO_TROPHY()} <b>{title}</b>", "━" * 26]
    for i, row in enumerate(rows):
        med = MEDALS[i] if i < 3 else f"  {i+1}."
        wf  = row.get("words_found", 0)
        lines.append(f"{med} <b>{row['name']}</b> — {row['score']} pts "
                     f"<i>({wf} words)</i>")
    return "\n".join(lines)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MY STATS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def my_stats(first_name: str, doc: dict) -> str:
    return (
        f"{ICO_MEDAL()} <b>Stats — {first_name}</b>\n\n"
        f"{ICO_STAR()} Score:       <b>{doc.get('score',0):,}</b>\n"
        f"{ICO_PUZZLE()} Words found: <b>{doc.get('words_found',0):,}</b>\n"
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BOT STATS  (owner)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def bot_stats(users: int, groups: int) -> str:
    return (
        f"{ICO_DIAMOND()} <b>Bot Stats</b>\n\n"
        f"👥 Users:  <b>{users:,}</b>\n"
        f"💬 Groups: <b>{groups:,}</b>\n"
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BROADCAST
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BROADCAST_USAGE = (
    "📢 <b>Broadcast</b>\n\n"
    "/broadcast all &lt;msg&gt; — Users + Groups\n"
    "/broadcast users &lt;msg&gt; — Users only\n"
    "/broadcast groups &lt;msg&gt; — Groups only\n\n"
    "<i>HTML formatting supported.</i>"
)

def broadcast_done(sent: int, failed: int, total: int) -> str:
    return (
        f"📢 <b>Broadcast Complete</b>\n\n"
        f"✅ Sent:   <b>{sent}</b>\n"
        f"❌ Failed: <b>{failed}</b>\n"
        f"📊 Total:  <b>{total}</b>"
    )
