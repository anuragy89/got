from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import BOT_INVITE_LINK, SUPPORT_GROUP, UPDATES_CHANNEL
from puzzle import THEMES, THEME_LIST


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BUTTON COLOUR HELPER  (Telegram Bot API 9.4+)
#
#  The `style` field on InlineKeyboardButton lets
#  bots colour buttons:
#    "primary"  → blue   (main action)
#    "success"  → green  (positive / proceed)
#    "danger"   → red    (destructive / warning)
#
#  python-telegram-bot 21.x doesn't expose `style`
#  as a named parameter yet, so we inject it via
#  api_kwargs — this works on every PTB version
#  and is forwards-compatible.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _cb(text: str, callback_data: str, style: str = None) -> InlineKeyboardButton:
    """Callback button with optional colour style."""
    kw = {"api_kwargs": {"style": style}} if style else {}
    return InlineKeyboardButton(text, callback_data=callback_data, **kw)


def _url(text: str, url: str, style: str = None) -> InlineKeyboardButton:
    """URL button with optional colour style."""
    kw = {"api_kwargs": {"style": style}} if style else {}
    return InlineKeyboardButton(text, url=url, **kw)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GRID DEEP-LINK BUILDER
#  Returns a t.me link that Telegram clients use
#  to scroll directly to a specific message.
#    • Public group  → t.me/<username>/<msg_id>
#    • Private/super → t.me/c/<numeric_id>/<msg_id>
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _grid_url(grid_msg_id: int, chat_username: str | None,
              chat_id_int: int | None) -> str | None:
    if not grid_msg_id:
        return None
    if chat_username:
        return f"https://t.me/{chat_username}/{grid_msg_id}"
    if chat_id_int:
        # Supergroup IDs look like -1001234567890 → strip leading -100
        raw = str(chat_id_int)
        numeric = raw[4:] if raw.startswith("-100") else raw.lstrip("-")
        return f"https://t.me/c/{numeric}/{grid_msg_id}"
    return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  KEYBOARDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def start_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [_url("➕ Add to Group", BOT_INVITE_LINK, style="success")],
        [
            _url("📢 Updates", UPDATES_CHANNEL),
            _url("🆘 Support", SUPPORT_GROUP),
        ],
        [
            _cb("❓ Help",         "cb:help"),
            _cb("🏆 Global Board", "cb:globalboard", style="primary"),
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
            _url("📢 Updates", UPDATES_CHANNEL),
        ],
        [
            _cb("💡 Hint",     "cb:hint",    style="primary"),
            _cb("🚩 End Game", "cb:endgame", style="danger"),
        ],
    ])


def word_found_kb(grid_msg_id: int,
                  chat_username: str | None = None,
                  chat_id_int:   int | None = None) -> InlineKeyboardMarkup:
    """
    FIX #2 — 'Go to Grid' is now a real URL button.
    Telegram clients open the link and scroll straight
    to the grid message — no alert pop-up, no extra tap.
    """
    link = _grid_url(grid_msg_id, chat_username, chat_id_int)
    if link:
        return InlineKeyboardMarkup([[
            _url("🔠 Go to Grid ➡️", link, style="primary"),
        ]])
    # Fallback if we can't build the URL (shouldn't normally happen)
    return InlineKeyboardMarkup([[
        _cb("🔠 Go to Grid ➡️", f"cb:gotogrid:{grid_msg_id}"),
    ]])


def next_round_kb(next_round: int, theme_key: str) -> InlineKeyboardMarkup:
    """After a round where ALL words found — includes Next Round button."""
    return InlineKeyboardMarkup([
        [
            _cb(f"▶️ Start Round {next_round}",
                f"nextround:{theme_key}:{next_round}", style="success"),
        ],
        [
            _cb("🏆 Leaderboard", "cb:leaderboard", style="primary"),
            _url("➕ Add Me",      BOT_INVITE_LINK),
        ],
        # Repeated row so tapping Leaderboard never hides the Next Round option
        [
            _cb(f"▶️ Round {next_round} again →",
                f"nextround:{theme_key}:{next_round}", style="success"),
        ],
    ])


def round_over_no_next_kb() -> InlineKeyboardMarkup:
    """After timeout — no Next Round button."""
    return InlineKeyboardMarkup([
        [
            _cb("🏆 Leaderboard", "cb:leaderboard", style="primary"),
            _url("➕ Add Me",      BOT_INVITE_LINK),
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
            _cb("🎮 New Game", "theme:random", style="success"),
            _url("➕ Add Me",   BOT_INVITE_LINK),
        ],
    ])


def leaderboard_kb(next_round: int = 0, theme_key: str = "") -> InlineKeyboardMarkup:
    """
    Group leaderboard view.
    Keeps the ▶️ Next Round button when next_round > 0 so it
    survives the user tapping Leaderboard from the round-end card.
    """
    rows = [
        [
            _cb("🌍 Global Board", "cb:globalboard", style="primary"),
            _cb("🔄 Refresh",      "cb:leaderboard"),
        ],
        [
            _cb("🎮 New Game", "theme:random", style="success"),
            _cb("❓ Help",     "cb:help"),
        ],
    ]
    if next_round > 0 and theme_key:
        rows.append([
            _cb(f"▶️ Start Round {next_round}",
                f"nextround:{theme_key}:{next_round}", style="success"),
        ])
    return InlineKeyboardMarkup(rows)


def globalboard_kb(next_round: int = 0, theme_key: str = "") -> InlineKeyboardMarkup:
    """
    FIX #1 — Global leaderboard view.
    Has its own keyboard builder so it can also carry the
    ▶️ Next Round button when the user navigates here from a
    completed-round card (instead of silently dropping it).
    """
    rows = [
        [
            _cb("🏆 Group Board", "cb:leaderboard", style="primary"),
            _cb("🔄 Refresh",     "cb:globalboard"),
        ],
        [
            _cb("🎮 New Game", "theme:random", style="success"),
            _cb("❓ Help",     "cb:help"),
        ],
    ]
    if next_round > 0 and theme_key:
        rows.append([
            _cb(f"▶️ Start Round {next_round}",
                f"nextround:{theme_key}:{next_round}", style="success"),
        ])
    return InlineKeyboardMarkup(rows)


def back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        _cb("🎮 Play Now", "theme:random", style="success"),
        _cb("« Back",      "cb:start"),
    ]])
