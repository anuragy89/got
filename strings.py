from config import (
    USE_PREMIUM_EMOJI,
    PEMOJI_TROPHY, PEMOJI_FIRE, PEMOJI_STAR, PEMOJI_CROWN,
    PEMOJI_DIAMOND, PEMOJI_LIGHTNING, PEMOJI_PUZZLE,
    PEMOJI_ROCKET, PEMOJI_JOYSTICK, PEMOJI_MEDAL,
)

def _pe(eid, fallback):
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
        f"<b>│20 Themes</b>\n"
       
        f"{ICO_DIAMOND()} <b>Add me to your group and start playing now!</b>"
    )

def start_group() -> str:
    return (
        f"{ICO_PUZZLE()} <b>WordGrid Bot is ready!</b>\n\n"
        f"Use /newgame to start a round.\n"
        f"Use /help to see all commands."
    )

def new_group_welcome(title: str) -> str:
    return (
        f"{ICO_ROCKET()} <b>WordGrid Bot just landed in {title}!</b>\n\n"
        f"{ICO_JOYSTICK()} I bring <b>Word Grid Puzzle Games</b> to your group.\n\n"
        f"<b>┌ Quick start</b>\n"
        f"<b>│</b> /newgame — Start round 1\n"
        f"<b>│</b> /hint — Get a letter hint during a game\n"
        f"<b>│</b> /theme — Pick a fun theme\n"
        f"<b>│</b> /leaderboard — See top players\n"
        f"<b>│</b> /help — Full command list\n"
        f"<b>└────────────────────</b>\n\n"
        f"<b>┌ 12 Progressive Rounds</b>\n"
        f"<b>│</b> R1: 30s · 3 words · 4×4 grid\n"
        f"<b>│</b> R6: 3m · 8 words · 8×8 grid\n"
        f"<b>│</b> R12: 6m · 14 words · 11×11 grid\n"
        f"<b>└────────────────────</b>\n\n"
        f"{ICO_CROWN()} Ready? Type /newgame to begin!"
    )

def help_text() -> str:
    return (
        f"{ICO_PUZZLE()} <b>WordGrid Bot — Commands</b>\n\n"
        f"{ICO_JOYSTICK()} <b>Game</b>\n"
        f"  /newgame — Start round 1 (random theme)\n"
        f"  /newgame [theme] — e.g. /newgame space\n"
        f"  /theme — Browse & pick a theme\n"
        f"  /hint — Reveal hints for all hidden words\n"
        f"  /endgame — End round early (admins)\n\n"
        f"{ICO_TROPHY()} <b>Leaderboard</b>\n"
        f"  /leaderboard — This group's top 10\n"
        f"  /globalboard — All-time global top 10\n"
        f"  /mystats — Your personal stats\n"
        f"  /resetboard — Reset group board (admins)\n\n"
        f"{ICO_FIRE()} <b>20 Themes</b>\n"
        f"  animals • fruits • ocean • space • sports\n"
        f"  countries • food • bollywood • science • technology\n"
        f"  mythology • music • geography • movies • history\n"
        f"  cricket • nature • vehicles • bodyparts • games\n\n"
        f"{ICO_LIGHTNING()} <b>12 Progressive Rounds</b>\n"
        f"  R1: 30s · 3 words · 4×4  →  R6: 3m · 8 words · 8×8\n"
        f"  R12: 6m · 14 words · 11×11\n\n"
        f"{ICO_STAR()} <b>Combo</b>\n"
        f"  2 in a row → ×1.5  |  3 → ×2.0\n"
        f"  4 → ×2.5  |  5+ → ×3.0"
    )

def game_start_caption(theme_name, theme_emoji, round_num, n_words, duration, grid_size,
                       words=None, found_words=None) -> str:
    """
    Caption shown under the grid image.
    When words/found_words are provided, inline hints replace the old
    'Find X hidden words' line — each unfound word shows first+last letter,
    each found word shows a ✅ tick.
    """
    header = (
        f"{ICO_PUZZLE()} <b>Round {round_num} — {theme_emoji} {theme_name}!</b>\n"
        f"{ICO_LIGHTNING()} Timer: <b>{duration}s</b>  |  "
        f"{ICO_STAR()} Build combos for bonus points!\n\n"
    )

    if words:
        found_set = set(found_words or [])
        hint_lines = []
        for w in words:
            if w in found_set:
                hint_lines.append(f"✅ <b>{w}</b>")
            else:
                if len(w) <= 2:
                    masked = w[0] + " _" * (len(w) - 1)
                else:
                    masked = w[0] + " _ " * (len(w) - 2) + w[-1]
                hint_lines.append(f"💡 <code>{masked}</code>  <i>({len(w)} letters)</i>")
        return header + "\n".join(hint_lines)

    # Fallback when words not yet available (shouldn't normally happen)
    return (
        header +
        f"Find <b>{n_words} hidden words</b> in the <b>{grid_size}×{grid_size}</b> grid!"
    )

def word_found(name, word, pts, combo, left) -> str:
    combo_txt = f"  {ICO_FIRE()} ×{combo} combo!" if combo >= 2 else ""
    return (
        f"{ICO_STAR()} <b>{name}</b> found <code>{word}</code>! "
        f"<b>+{pts} pts</b>{combo_txt}\n"
        f"<i>{left} word(s) still hidden</i>"
    )

def hint_text(hint: str, length: int) -> str:
    return (
        f"💡 <b>Hint!</b>  ({length} letters)\n"
        f"<code>{hint}</code>"
    )

def no_hint_text() -> str:
    return "💡 No unfound words left to hint!"

MEDALS = ["🥇", "🥈", "🥉"]

def round_end(summary, missed, theme_name, round_num, max_rounds, round_complete=False) -> str:
    is_final = (round_num >= max_rounds)
    header = f"{ICO_CROWN()} <b>{'🏁 FINAL ' if is_final else ''}Round {round_num} Over! — {theme_name}</b>"
    lines = [header, "━" * 26]
    if not summary:
        lines.append("<i>No one scored this round!</i>")
    else:
        for i, row in enumerate(summary[:5]):
            med = MEDALS[i] if i < 3 else f"  {i+1}."
            lines.append(f"{med} <b>{row['name']}</b> — {row['score']} pts  <i>({row['words']} words)</i>")
        lines.append("")
        lines.append(f"{ICO_TROPHY()} <b>Round winner: {summary[0]['name']}</b>  🎉")
    if missed:
        lines.append("")
        lines.append(f"{ICO_PUZZLE()} <b>Missed:</b> {', '.join(missed)}")
    lines.append("")
    if is_final:
        lines.append("🏁 <b>All 12 rounds complete! Great game!</b>")
        lines.append("Type /newgame to start fresh.")
    elif round_complete:
        lines.append(f"{ICO_ROCKET()} <b>Round {round_num + 1} is next!</b> Press the button below.")
    else:
        lines.append(f"⏰ <b>Time's up!</b> Not all words were found.")
        lines.append(f"Type /newgame to start a new game!")
    return "\n".join(lines)

def leaderboard_text(rows, title) -> str:
    if not rows:
        return f"{ICO_TROPHY()} <b>{title}</b>\n\nNo scores yet — play /newgame to get started!"
    lines = [f"{ICO_TROPHY()} <b>{title}</b>", "━" * 26]
    for i, row in enumerate(rows):
        med = MEDALS[i] if i < 3 else f"  {i+1}."
        wf  = row.get("words_found", 0)
        lines.append(f"{med} <b>{row['name']}</b> — {row['score']} pts <i>({wf} words)</i>")
    return "\n".join(lines)

def my_stats(first_name, doc) -> str:
    return (
        f"{ICO_MEDAL()} <b>Stats — {first_name}</b>\n\n"
        f"{ICO_STAR()} Score:       <b>{doc.get('score',0):,}</b>\n"
        f"{ICO_PUZZLE()} Words found: <b>{doc.get('words_found',0):,}</b>\n"
    )

def bot_stats(users, groups) -> str:
    return (
        f"{ICO_DIAMOND()} <b>Bot Stats</b>\n\n"
        f"👥 Users:  <b>{users:,}</b>\n"
        f"💬 Groups: <b>{groups:,}</b>\n"
    )

BROADCAST_USAGE = (
    "📢 <b>Broadcast</b>\n\n"
    "/broadcast all &lt;msg&gt; — Users + Groups\n"
    "/broadcast users &lt;msg&gt; — Users only\n"
    "/broadcast groups &lt;msg&gt; — Groups only\n\n"
    "<i>HTML formatting supported.</i>"
)

def broadcast_done(sent, failed, total) -> str:
    return (
        f"📢 <b>Broadcast Complete</b>\n\n"
        f"✅ Sent:   <b>{sent}</b>\n"
        f"❌ Failed: <b>{failed}</b>\n"
        f"📊 Total:  <b>{total}</b>"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  IDLE NUDGE MESSAGES
#  Sent to groups that haven't played in a while
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IDLE_NUDGES = [
    (
        f"{ICO_JOYSTICK()} <b>Getting bored in here?</b> 😴\n"
        f"Wake everyone up — type /newgame and drop a word grid! 🎮"
    ),
    (
        f"{ICO_FIRE()} <b>The grid is waiting...</b> 🧩\n"
        f"Find hidden words, beat your friends, climb the board! /newgame"
    ),
    (
        f"{ICO_ROCKET()} <b>Psst! Still alive in here?</b> 👀\n"
        f"Let's play Word Grid — type /newgame to fire one up! 🚀"
    ),
    (
        f"{ICO_LIGHTNING()} <b>No game? No fun!</b> ⚡\n"
        f"Challenge the whole group right now — /newgame to drop a fresh grid!"
    ),
    (
        f"{ICO_CROWN()} <b>Who's the word champion here?</b> 🏆\n"
        f"Only one way to find out... /newgame and let's settle it! 👑"
    ),
    (
        f"{ICO_STAR()} <b>Break's over!</b> ⭐\n"
        f"Time for a quick word hunt — /newgame and let's go! 🔥"
    ),
    (
        f"{ICO_PUZZLE()} <b>Hidden words are waiting to be found!</b> 🧩\n"
        f"Can your group find them all? /newgame to find out!"
    ),
    (
        f"{ICO_DIAMOND()} <b>This group has gone quiet...</b> 💎\n"
        f"Stir things up with a word game! /newgame 🎯"
    ),
    (
        f"{ICO_MEDAL()} <b>Your leaderboard rank is slipping!</b> 🎖️\n"
        f"Don't let others overtake you — jump back in with /newgame!"
    ),
    (
        f"{ICO_FIRE()} <b>This group needs some heat!</b> 🔥\n"
        f"Start a word grid, get everyone competing — /newgame now!"
    ),
]
