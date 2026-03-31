from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import BOT_INVITE_LINK, SUPPORT_GROUP, UPDATES_CHANNEL
from puzzle import THEMES, THEME_LIST


def start_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add to Group", url=BOT_INVITE_LINK),
        ],
        [
            InlineKeyboardButton("📢 Updates",  url=UPDATES_CHANNEL),
            InlineKeyboardButton("🆘 Support",  url=SUPPORT_GROUP),
        ],
        [
            InlineKeyboardButton("❓ Help",          callback_data="cb:help"),
            InlineKeyboardButton("🏆 Global Board",  callback_data="cb:globalboard"),
        ],
    ])


def theme_kb() -> InlineKeyboardMarkup:
    rows, row = [], []
    for key in THEME_LIST:
        t = THEMES[key]
        row.append(InlineKeyboardButton(
            f"{t['emoji']} {t['name']}", callback_data=f"theme:{key}"
        ))
        if len(row) == 2:
            rows.append(row); row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("🎲 Random Theme", callback_data="theme:random")])
    return InlineKeyboardMarkup(rows)


def game_action_kb() -> InlineKeyboardMarkup:
    """Buttons shown under the grid image during an active round."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add Me",    url=BOT_INVITE_LINK),
            InlineKeyboardButton("📢 Updates",   url=UPDATES_CHANNEL),
        ],
        [
            InlineKeyboardButton("💡 Hint",      callback_data="cb:hint"),
            InlineKeyboardButton("🚩 End Game",   callback_data="cb:endgame"),
        ],
    ])


def next_round_kb(next_round: int, theme_key: str) -> InlineKeyboardMarkup:
    """Shown after a round where ALL words were found — Next Round button included."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"▶️ Start Round {next_round}",
                callback_data=f"nextround:{theme_key}:{next_round}"
            ),
        ],
        [
            InlineKeyboardButton("🏆 Leaderboard", callback_data="cb:leaderboard"),
            InlineKeyboardButton("➕ Add Me",       url=BOT_INVITE_LINK),
        ],
    ])


def round_over_no_next_kb() -> InlineKeyboardMarkup:
    """Shown after a round ended by timeout — no Next Round button."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🏆 Leaderboard", callback_data="cb:leaderboard"),
            InlineKeyboardButton("➕ Add Me",       url=BOT_INVITE_LINK),
        ],
    ])


def final_round_kb() -> InlineKeyboardMarkup:
    """Shown after round 12 — full game complete."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🏆 Leaderboard",  callback_data="cb:leaderboard"),
            InlineKeyboardButton("🌍 Global Board",  callback_data="cb:globalboard"),
        ],
        [
            InlineKeyboardButton("🎮 New Game", callback_data="theme:random"),
            InlineKeyboardButton("➕ Add Me",   url=BOT_INVITE_LINK),
        ],
    ])


def leaderboard_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🌍 Global Board", callback_data="cb:globalboard"),
            InlineKeyboardButton("🔄 Refresh",       callback_data="cb:leaderboard"),
        ],
        [
            InlineKeyboardButton("🎮 New Game",  callback_data="theme:random"),
            InlineKeyboardButton("❓ Help",      callback_data="cb:help"),
        ],
    ])


def back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎮 Play Now",  callback_data="theme:random"),
            InlineKeyboardButton("« Back",       callback_data="cb:start"),
        ],
    ])
