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


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  START — PRIVATE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def start_private(name: str) -> str:
    return (
        f"👋 <b>Hey {name}! Welcome to WordGrid Bot!</b>\n\n"

        f"{ICO_PUZZLE()} <b>What is this?</b>\n"
        f"A <b>Word Grid Puzzle Game</b> for Telegram groups!\n"
        f"A themed grid drops — players race to find hidden words.\n\n"

        f"{ICO_JOYSTICK()} <b>How to play</b>\n"
        f"› Bot sends a colourful grid in your group\n"
        f"› Type any hidden word to claim it\n"
        f"› Chain words for up to {ICO_FIRE()} <b>3× combo bonus!</b>\n"
        f"› Most points at the end = {ICO_CROWN()} <b>WINNER</b>\n\n"

        f"{ICO_STAR()} <b>20 Themes</b> — Animals, Space, Bollywood,\n"
        f"Cricket, Food, Ocean, Science & more!\n\n"

        f"{ICO_DIAMOND()} <b>Add me to your group and let's play!</b>"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  START — GROUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def start_group() -> str:
    return (
        f"{ICO_PUZZLE()} <b>WordGrid Bot is ready!</b>\n\n"
        f"› /newgame — Start a new round\n"
        f"› /help — See all commands\n\n"
        f"{ICO_FIRE()} <i>Type /newgame to drop the first grid!</i>"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  NEW GROUP WELCOME
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def new_group_welcome(title: str) -> str:
    return (
        f"{ICO_ROCKET()} <b>WordGrid Bot just landed in {title}!</b>\n\n"

        f"{ICO_JOYSTICK()} I bring <b>Word Grid Puzzle Games</b> to your group.\n\n"

        f"<b>--- Quick Start ---</b>\n"
        f"› /newgame — Start round 1\n"
        f"› /newhard — Start a hard round\n"
        f"› /hint — Get a letter hint mid-game\n"
        f"› /theme — Pick a fun theme\n"
        f"› /leaderboard — See top players\n"
        f"› /help — Full command list\n\n"

        f"<b>--- 12 Progressive Rounds ---</b>\n"
        f"› R1: 2m · 4 words · 5×5 grid\n"
        f"› R6: 3.5m · 8 words · 8×8 grid\n"
        f"› R12: 7.5m · 14 words · 11×11 grid\n\n"

        f"{ICO_CROWN()} <b>Ready? Type /newgame to begin!</b>"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  HELP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def help_text() -> str:
    return (
        f"{ICO_PUZZLE()} <b>WordGrid Bot — Commands</b>\n\n"

        f"{ICO_JOYSTICK()} <b>Game</b>\n"
        f"› /newgame — Start round 1 (random theme)\n"
        f"› /newhard — Start a hard round\n"
        f"› /newgame [theme] — e.g. /newgame space\n"
        f"› /theme — Browse & pick a theme\n"
        f"› /hint — Reveal hints for unfound words\n"
        f"› /endgame — End round early (admins)\n\n"

        f"{ICO_TROPHY()} <b>Leaderboard</b>\n"
        f"› /leaderboard — This group's top 10\n"
        f"› /globalboard — All-time global top 10\n"
        f"› /mystats — Your personal stats\n"
        f"› /me — Your profile card\n"
        f"› /resetboard — Reset group board (admins)\n\n"

        f"{ICO_FIRE()} <b>20 Themes</b>\n"
        f"  animals • fruits • ocean • space • sports\n"
        f"  countries • food • bollywood • science • tech\n"
        f"  mythology • music • geography • movies • history\n"
        f"  cricket • nature • vehicles • bodyparts • games\n\n"

        f"{ICO_LIGHTNING()} <b>12 Progressive Rounds</b>\n"
        f"  R1: 2m · 4 words · 5×5  →  R12: 7.5m · 14 words · 11×11\n\n"

        f"{ICO_STAR()} <b>Combo Multipliers</b>\n"
        f"  2 in a row → ×1.5  |  3 → ×2.0\n"
        f"  4 → ×2.5  |  5+ → ×3.0"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GRID CAPTION (shown under the grid image)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def game_start_caption(theme_name, theme_emoji, round_num, n_words, duration, grid_size,
                       words=None, found_words=None) -> str:
    header = (
        f"{ICO_PUZZLE()} <b>Round {round_num} — {theme_emoji} {theme_name}!</b>\n"
        f"{ICO_LIGHTNING()} Timer: <b>{duration}s</b>  |  "
        f"{ICO_STAR()} Combos give bonus points!\n\n"
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
                elif len(w) == 3:
                    masked = w[0] + " _ " + w[-1]
                else:
                    masked = w[0] + " _" * (len(w) - 2) + " " + w[-1]
                hint_lines.append(f"💡 <code>{masked}</code>  <i>({len(w)} letters)</i>")
        return header + "\n".join(hint_lines)

    return (
        header +
        f"Find <b>{n_words} hidden words</b> in the <b>{grid_size}×{grid_size}</b> grid!"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  WORD FOUND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def word_found(name, word, pts, combo, left) -> str:
    combo_txt = f"  {ICO_FIRE()} <b>×{combo} combo!</b>" if combo >= 2 else ""
    return (
        f"{ICO_STAR()} <b>{name}</b> found <code>{word}</code>!"
        f"  <b>+{pts} pts</b>{combo_txt}\n"
        f"<i>{left} word(s) still hidden</i>"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  HINT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def hint_text(hint: str, length: int) -> str:
    return (
        f"💡 <b>Hint!</b>  ({length} letters)\n"
        f"<code>{hint}</code>"
    )

def no_hint_text() -> str:
    return f"💡 <i>No unfound words left to hint!</i>"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ROUND END
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MEDALS = ["🥇", "🥈", "🥉"]

def round_end(summary, missed, theme_name, round_num, max_rounds, round_complete=False) -> str:
    is_final = (round_num >= max_rounds)

    # ── QUOTE 1: Header
    if is_final:
        q1 = f'<blockquote>🎉 {ICO_CROWN()} <b>Game Over!</b> {ICO_TROPHY()} 🎉</blockquote>'
    else:
        q1 = f'<blockquote>🎉 {ICO_FIRE()} <b>Game Over!</b> {ICO_FIRE()} 🎉</blockquote>'

    # ── QUOTE 2: Round Summary + scores + missed
    summary_lines = ["<b>--- Round Summary ---</b>", ""]
    if not summary:
        summary_lines.append("<i>No one scored this round!</i>")
    else:
        for i, row in enumerate(summary[:5]):
            med     = MEDALS[i] if i < 3 else f"  {i+1}."
            uid     = row.get("user_id")
            name    = row.get("name", "Player")
            mention = f'<a href="tg://user?id={uid}">{name}</a>' if uid else f"<b>{name}</b>"
            summary_lines.append(
                f"{med} {mention}: <b>{row['score']} points</b>  <i>({row['words']} words)</i>"
            )
    if missed:
        summary_lines.append("")
        summary_lines.append(
            f"{ICO_PUZZLE()} <b>Missed:</b> {', '.join(missed)}"
        )
    q2 = "<blockquote>" + "\n".join(summary_lines) + "</blockquote>"

    # ── QUOTE 3: Footer
    if is_final:
        footer_lines = [
            f"🏁 {ICO_STAR()} <b>All {max_rounds} rounds complete! Great game!</b>",
            f"{ICO_ROCKET()} Thanks for playing — start fresh with /newhard or /newgame.",
        ]
    elif round_complete:
        footer_lines = [
            f"{ICO_LIGHTNING()} <b>All words found!</b> Round {round_num + 1} starts automatically in 10s\u2026",
            f"{ICO_ROCKET()} Thanks for playing — start another game by /newhard or /newgame.",
        ]
    else:
        footer_lines = [
            f"\u23f0 <b>Time's up!</b> Not all words were found.",
            f"{ICO_ROCKET()} Thanks for playing — start another game by /newhard or /newgame.",
        ]
    q3 = "<blockquote>" + "\n".join(footer_lines) + "</blockquote>"

    return q1 + "\n" + q2 + "\n" + q3


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  LEADERBOARD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def leaderboard_text(rows, title) -> str:
    if not rows:
        return (
            f"{ICO_TROPHY()} <b>{title}</b>\n\n"
            f"<i>No scores yet — play /newgame to get started!</i>"
        )
    lines = [
        f"{ICO_TROPHY()} <b>{title}</b>",
        "",
        "<b>--- Top Players ---</b>",
        "",
    ]
    for i, row in enumerate(rows):
        med     = MEDALS[i] if i < 3 else f"  {i+1}."
        wf      = row.get("words_found", 0)
        uid     = row.get("user_id")
        name    = row.get("name", "Player")
        mention = f'<a href="tg://user?id={uid}">{name}</a>' if uid else f"<b>{name}</b>"
        lines.append(f"{med} {mention}: <b>{row['score']} pts</b>  <i>({wf} words)</i>")
    return "\n".join(lines)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MY STATS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def my_stats(first_name, doc) -> str:
    return (
        f"{ICO_MEDAL()} <b>Stats — {first_name}</b>\n\n"
        f"<b>--- Your Numbers ---</b>\n\n"
        f"{ICO_STAR()} Score:        <b>{doc.get('score', 0):,}</b>\n"
        f"{ICO_PUZZLE()} Words found:  <b>{doc.get('words_found', 0):,}</b>\n"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BOT STATS (owner only)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def bot_stats(users, groups) -> str:
    return (
        f"{ICO_DIAMOND()} <b>Bot Stats</b>\n\n"
        f"<b>--- Overview ---</b>\n\n"
        f"👥 Users:   <b>{users:,}</b>\n"
        f"💬 Groups:  <b>{groups:,}</b>\n"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BROADCAST (owner only)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BROADCAST_USAGE = (
    "📢 <b>Broadcast</b>\n\n"
    "› /broadcast all &lt;msg&gt; — Users + Groups\n"
    "› /broadcast users &lt;msg&gt; — Users only\n"
    "› /broadcast groups &lt;msg&gt; — Groups only\n\n"
    "<i>HTML formatting supported.</i>"
)

def broadcast_done(sent, failed, total) -> str:
    return (
        f"📢 <b>Broadcast Complete</b>\n\n"
        f"<b>--- Result ---</b>\n\n"
        f"✅ Sent:    <b>{sent}</b>\n"
        f"❌ Failed:  <b>{failed}</b>\n"
        f"📊 Total:   <b>{total}</b>"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  IDLE NUDGE MESSAGES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IDLE_NUDGES = [
    (
        f"{ICO_JOYSTICK()} <b>Getting bored in here?</b> 😴\n"
        f"Wake everyone up — /newgame and drop a word grid! 🎮"
    ),
    (
        f"{ICO_FIRE()} <b>The grid is waiting...</b> 🧩\n"
        f"Find hidden words, beat your friends, climb the board! /newgame"
    ),
    (
        f"{ICO_ROCKET()} <b>Psst! Still alive in here?</b> 👀\n"
        f"Fire up a Word Grid — /newgame and let's go! 🚀"
    ),
    (
        f"{ICO_LIGHTNING()} <b>No game? No fun!</b> ⚡\n"
        f"Challenge the whole group right now — /newgame!"
    ),
    (
        f"{ICO_CROWN()} <b>Who's the word champion here?</b> 🏆\n"
        f"Only one way to find out — /newgame and settle it! 👑"
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
