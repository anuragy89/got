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
    rows.append([InlineKeyboardButton("🎲 Random", callback_data="theme:random")])
    return InlineKeyboardMarkup(rows)


def game_action_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🏆 Leaderboard", callback_data="cb:leaderboard"),
            InlineKeyboardButton("⏱ Time Left",    callback_data="cb:timeleft"),
        ],
    ])


def leaderboard_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🌍 Global",   callback_data="cb:globalboard"),
            InlineKeyboardButton("🔄 Refresh",  callback_data="cb:leaderboard"),
        ],
    ])


def back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("« Back", callback_data="cb:start")],
    ])
