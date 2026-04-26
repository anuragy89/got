from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import BOT_INVITE_LINK, SUPPORT_GROUP, UPDATES_CHANNEL, USE_PREMIUM_EMOJI, \
    PEMOJI_ROCKET, PEMOJI_LIGHTNING, PEMOJI_JOYSTICK, PEMOJI_FIRE, PEMOJI_TROPHY, PEMOJI_STAR
from puzzle import THEMES, THEME_LIST


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PREMIUM EMOJI HELPER (for buttons)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _pe(eid, fallback):
    if USE_PREMIUM_EMOJI:
        return f'<tg-emoji emoji-id="{eid}">{fallback}</tg-emoji>'
    return fallback


def _BTN_AUTO():      return "🚀"
def _BTN_MANUAL():    return "🕹️"
def _BTN_NEXT():      return "⚡"
def _BTN_TROPHY():    return "🏆"
def _BTN_FIRE():      return "🔥"
def _BTN_STAR():      return "⭐"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BUTTON COLOUR HELPERS  (Telegram Bot API 9.4+)
#
#  style values rendered by Telegram clients:
#    "primary"  →  blue    (navigation / info)
#    "success"  →  green   (positive / start / add)
#    "danger"   →  red     (destructive / end)
#
#  python-telegram-bot 21.x doesn't expose `style`
#  as a named kwarg yet, but api_kwargs is fully
#  supported — the field survives to_dict() and
#  is sent verbatim to Telegram.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _cb(text: str, data: str, style: str = None) -> InlineKeyboardButton:
    """Callback button, optional colour."""
    kw = {"api_kwargs": {"style": style}} if style else {}
    return InlineKeyboardButton(text, callback_data=data, **kw)


def _url(text: str, link: str, style: str = None) -> InlineKeyboardButton:
    """URL button, optional colour."""
    kw = {"api_kwargs": {"style": style}} if style else {}
    return InlineKeyboardButton(text, url=link, **kw)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GRID DEEP-LINK BUILDER  (FIX #2)
#
#  Builds the t.me URL that scrolls Telegram
#  straight to the grid message in the group.
#    Public group  → t.me/<username>/<msg_id>
#    Private/super → t.me/c/<numeric_id>/<msg_id>
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _grid_url(grid_msg_id: int,
              chat_username: "str | None",
              chat_id_int:   "int | None") -> "str | None":
    if not grid_msg_id:
        return None
    if chat_username:
        return f"https://t.me/{chat_username}/{grid_msg_id}"
    if chat_id_int:
        raw     = str(chat_id_int)
        numeric = raw[4:] if raw.startswith("-100") else raw.lstrip("-")
        return f"https://t.me/c/{numeric}/{grid_msg_id}"
    return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  KEYBOARDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def round_mode_kb(game_type: str = "normal") -> InlineKeyboardMarkup:
    """
    Ask user to pick Automatic or Manual round progression.
    game_type: "normal" or "hard"
    """
    prefix = f"startmode:{game_type}"
    return InlineKeyboardMarkup([
        [
            _cb(f"{_BTN_AUTO()} Automatic", f"{prefix}:auto",   style="success"),
            _cb(f"{_BTN_MANUAL()} Manual",  f"{prefix}:manual", style="primary"),
        ],
    ])


def start_kb() -> InlineKeyboardMarkup:
    """Buttons shown under the /start message in private chat."""
    return InlineKeyboardMarkup([
        [_url("➕ Add to Group", BOT_INVITE_LINK, style="success")],
        [
            _url("📢 Updates", UPDATES_CHANNEL),
            _url("🆘 Support", SUPPORT_GROUP),
        ],
        [
            _cb("❓ Help",         "cb:help"),
            _cb("🏆 Global Board", "cb:globalboard"),
        ],
    ])


def theme_kb() -> InlineKeyboardMarkup:
    rows, row = [], []
    for key in THEME_LIST:
        t = THEMES[key]
        row.append(_cb(f"{t['emoji']} {t['name']}", f"theme:{key}"))
        if len(row) == 2:
            rows.append(row); row = []
    if row:
        rows.append(row)
    rows.append([_cb("🎲 Random Theme", "theme:random", style="success")])
    return InlineKeyboardMarkup(rows)


def game_action_kb() -> InlineKeyboardMarkup:
    """Buttons under the grid image during an active round."""
    return InlineKeyboardMarkup([
        [
            _url("➕ Add Me",  BOT_INVITE_LINK, style="success"),
            _url("📢 Updates", UPDATES_CHANNEL, style="primary"),
        ],
        [
            _url("🎮 Play Games", SUPPORT_GROUP, style="primary"),
            _cb("🚩 End Game",   "cb:endgame",  style="danger"),
        ],
    ])


def hard_action_kb() -> InlineKeyboardMarkup:
    """Buttons under the grid image during a HARD MODE round."""
    return InlineKeyboardMarkup([
        [
            _url("➕ Add Me",    BOT_INVITE_LINK, style="success"),
            _url("📢 Updates",   UPDATES_CHANNEL, style="primary"),
        ],
        [
            _url("🎮 Play Games", SUPPORT_GROUP,  style="primary"),
            _cb("🚩 End Game",   "cb:endgame",    style="danger"),
        ],
    ])


def word_found_kb(grid_msg_id: int,
                  chat_username: "str | None" = None,
                  chat_id_int:   "int | None" = None) -> InlineKeyboardMarkup:
    """
    FIX #2 — 'Go to Grid' is a real URL button.
    Telegram clients follow the link and scroll directly to the grid message.
    Falls back to callback if the URL can't be built.
    """
    link = _grid_url(grid_msg_id, chat_username, chat_id_int)
    if link:
        return InlineKeyboardMarkup([[
            _url("🔠 Go to Grid ➡️", link, style="success"),
        ]])
    return InlineKeyboardMarkup([[
        _cb("🔠 Go to Grid ➡️", f"cb:gotogrid:{grid_msg_id}", style="success"),
    ]])


def next_round_kb(next_round: int, theme_key: str, is_hard: bool = False) -> InlineKeyboardMarkup:
    """After a round where ALL words found — manual mode: includes Next Round button."""
    mode = "hard" if is_hard else "normal"
    return InlineKeyboardMarkup([
        [
            _cb(f"{_BTN_NEXT()} Start Round {next_round}",
                f"nextround:{theme_key}:{next_round}:{mode}", style="danger"),
        ],
        [
            _cb(f"{_BTN_TROPHY()} Leaderboard", "cb:leaderboard", style="primary"),
            _url("➕ Add Me",      BOT_INVITE_LINK,  style="success"),
        ],
    ])


def round_over_no_next_kb() -> InlineKeyboardMarkup:
    """After timeout — no Next Round button."""
    return InlineKeyboardMarkup([
        [
            _cb("🏆 Leaderboard", "cb:leaderboard", style="primary"),
            _url("➕ Add Me",      BOT_INVITE_LINK,  style="success"),
        ],
    ])


def final_round_kb() -> InlineKeyboardMarkup:
    """After round 12 — full game complete."""
    return InlineKeyboardMarkup([
        [
            _cb("🏆 Leaderboard",  "cb:leaderboard",  style="primary"),
            _cb("🌍 Global Board", "cb:globalboard",  style="primary"),
        ],
        [
            _cb("🎮 New Game", "theme:random",   style="success"),
            _url("➕ Add Me",   BOT_INVITE_LINK, style="success"),
        ],
    ])


def leaderboard_kb(next_round: int = 0, theme_key: str = "", is_hard: bool = False,
                   time_filter: str = "alltime") -> InlineKeyboardMarkup:
    """
    Group leaderboard keyboard.
    Row 1: [Current Chat ✅]  [🌍 Global]
    Row 2: [Today]  [Week]  [All Time ✅]   (active tab gets ✅)
    Row 3: [🎮 Play New Game]  (green)
    """
    today_lbl   = "📅 Today ✅"   if time_filter == "today"   else "📅 Today"
    week_lbl    = "📆 Week ✅"    if time_filter == "week"    else "📆 Week"
    alltime_lbl = "🏆 All Time ✅" if time_filter == "alltime" else "🏆 All Time"

    rows = [
        [
            _cb("📍 Current Chat ✅", "lb:chat:alltime"),
            _cb("🌍 Global",          "lb:global:alltime"),
        ],
        [
            _cb(today_lbl,   f"lb:chat:{time_filter if time_filter=='today' else 'today'}"),
            _cb(week_lbl,    f"lb:chat:{time_filter if time_filter=='week' else 'week'}"),
            _cb(alltime_lbl, "lb:chat:alltime"),
        ],
        [
            _cb("🎮 Play New Game", "theme:random", style="success"),
        ],
    ]
    return InlineKeyboardMarkup(rows)


def globalboard_kb(next_round: int = 0, theme_key: str = "", is_hard: bool = False,
                   time_filter: str = "alltime") -> InlineKeyboardMarkup:
    """
    Global leaderboard keyboard.
    Row 1: [Current Chat]  [🌍 Global ✅]
    Row 2: [Today]  [Week]  [All Time ✅]
    Row 3: [🎮 Play New Game]  (green)
    """
    today_lbl   = "📅 Today ✅"   if time_filter == "today"   else "📅 Today"
    week_lbl    = "📆 Week ✅"    if time_filter == "week"    else "📆 Week"
    alltime_lbl = "🏆 All Time ✅" if time_filter == "alltime" else "🏆 All Time"

    rows = [
        [
            _cb("📍 Current Chat",  "lb:chat:alltime"),
            _cb("🌍 Global ✅",     "lb:global:alltime"),
        ],
        [
            _cb(today_lbl,   f"lb:global:{time_filter if time_filter=='today' else 'today'}"),
            _cb(week_lbl,    f"lb:global:{time_filter if time_filter=='week' else 'week'}"),
            _cb(alltime_lbl, "lb:global:alltime"),
        ],
        [
            _cb("🎮 Play New Game", "theme:random", style="success"),
        ],
    ]
    return InlineKeyboardMarkup(rows)


def back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        _cb("🎮 Play Now", "theme:random", style="success"),
        _cb("« Back",      "cb:start"),                                  # neutral
    ]])
