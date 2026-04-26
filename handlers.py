"""
handlers.py — All Telegram command, callback, message, and job handlers
for WordGrid Bot.
"""

import asyncio
import io
import logging
import random
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from telegram import Update, InputMediaPhoto
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ContextTypes

import database as db
from config import (
    OWNER_ID, COOLDOWN_SECONDS, MSG_DELETE_AFTER,
    IDLE_NUDGE_AFTER, BROADCAST_DELAY,
)
from game import (
    GameSession, SessionManager, sessions,
    get_level, MAX_ROUNDS,
    pick_random_theme, pick_next_round_theme,
    pick_hard_theme, pick_hard_words,
    HARD_N_WORDS_MIN, HARD_N_WORDS_MAX,
    touch_activity, idle_seconds,
)
from keyboards import (
    start_kb, theme_kb, game_action_kb, hard_action_kb,
    word_found_kb, next_round_kb, round_over_no_next_kb,
    final_round_kb, leaderboard_kb, globalboard_kb, back_kb,
    round_mode_kb,
)
from puzzle import THEMES, THEME_LIST, build_grid, render_image
from render_cards import render_leaderboard, render_rank_tiers
from strings import (
    start_private, start_group, new_group_welcome, help_text,
    game_start_caption, word_found, hint_text, no_hint_text,
    round_end, leaderboard_text, my_stats, bot_stats as fmt_bot_stats,
    BROADCAST_USAGE, broadcast_done, IDLE_NUDGES,
)

log = logging.getLogger(__name__)
_executor = ThreadPoolExecutor(max_workers=4)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _spaced_hint(word: str) -> str:
    """Return a hint with spaced underscores: A _ _ _ N (first + last letters shown)."""
    if len(word) <= 1:
        return word
    if len(word) == 2:
        return word[0] + " _"
    if len(word) == 3:
        return word[0] + " _ " + word[-1]
    inner = " ".join(["_"] * (len(word) - 2))
    return word[0] + " " + inner + " " + word[-1]


async def _run_in_executor(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, func, *args)


async def _safe_delete(bot, chat_id: int, msg_id: int):
    try:
        await bot.delete_message(chat_id=chat_id, message_id=msg_id)
    except Exception:
        pass


async def _schedule_cleanup(bot, chat_id: int, msg_ids: list, delay: int):
    """Delete all listed messages after `delay` seconds."""
    if not delay or not msg_ids:
        return
    await asyncio.sleep(delay)
    for mid in msg_ids:
        await _safe_delete(bot, chat_id, mid)


async def _end_round(context: ContextTypes.DEFAULT_TYPE, chat_id: int,
                     s: GameSession, reason: str = "timeout"):
    """
    Finalise a round: update DB, send summary, schedule cleanup.
    reason: "timeout" | "complete" | "endgame"
    """
    if not s.active:
        return
    s.active = False
    sessions.remove(chat_id)
    touch_activity(chat_id)

    summary = s.summary()
    missed  = [w for w in s.words if w not in s.found_words]
    theme   = THEMES[s.theme]
    round_complete = (reason == "complete")

    # Persist scores
    for row in summary:
        await db.add_score(
            chat_id, row["user_id"], row["name"],
            row["score"], row["words"],
            username=row.get("username"),
        )

    is_final   = (s.round_num >= MAX_ROUNDS) or s.is_hard
    next_round = s.round_num + 1

    if is_final:
        kb = final_round_kb()
    elif round_complete:
        kb = next_round_kb(next_round, s.theme, s.is_hard)
    else:
        kb = round_over_no_next_kb()

    text = round_end(
        summary, missed, theme["name"],
        s.round_num, MAX_ROUNDS,
        round_complete=round_complete,
    )
    msg = await context.bot.send_message(
        chat_id=chat_id, text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=kb,
    )

    # Auto-advance in auto mode when all words found and not final
    if round_complete and not is_final and s.round_mode == "auto":
        asyncio.create_task(
            _auto_next_round(context, chat_id, s, next_round)
        )

    # Schedule cleanup
    all_ids = list(s.msg_ids) + [msg.message_id]
    if MSG_DELETE_AFTER:
        asyncio.create_task(
            _schedule_cleanup(context.bot, chat_id, all_ids, MSG_DELETE_AFTER)
        )

    sessions.set_cooldown(chat_id, COOLDOWN_SECONDS)


async def _auto_next_round(context: ContextTypes.DEFAULT_TYPE, chat_id: int,
                            prev: GameSession, next_round: int):
    """Wait 10 s then start the next round automatically."""
    await asyncio.sleep(10)
    if sessions.active(chat_id):
        return   # someone started a game manually in the gap
    next_theme = pick_next_round_theme(chat_id, prev.theme, THEME_LIST)
    await _launch_round(
        context, chat_id,
        theme_key=next_theme,
        round_num=next_round,
        is_hard=prev.is_hard,
        round_mode=prev.round_mode,
    )


async def _launch_round(context: ContextTypes.DEFAULT_TYPE,
                        chat_id: int,
                        theme_key: str,
                        round_num: int,
                        is_hard: bool = False,
                        round_mode: str = "auto"):
    """Build grid, render image, send to group and set up timer."""
    theme = THEMES[theme_key]
    duration, n_words, grid_size = get_level(round_num)

    if is_hard:
        words = pick_hard_words(
            chat_id, theme_key, theme["words"],
            HARD_N_WORDS_MIN, HARD_N_WORDS_MAX,
        )
        grid_size = 11
    else:
        all_words = theme["words"]
        words = random.sample(
            [w for w in all_words if len(w) <= grid_size],
            min(n_words, len(all_words)),
        )

    # Build grid & render image in thread pool (CPU-bound)
    grid, placed = await _run_in_executor(build_grid, grid_size, words)
    img_bytes    = await _run_in_executor(
        render_image, theme_key, grid, placed, [], round_num, grid_size
    )

    s = GameSession(
        chat_id=chat_id,
        theme=theme_key,
        grid=grid,
        words=words,
        placed=placed,
        round_num=round_num,
        img_bytes=img_bytes,
        is_hard=is_hard,
        round_mode=round_mode,
    )
    sessions.put(s)
    touch_activity(chat_id)

    caption = game_start_caption(
        theme["name"], theme["emoji"],
        round_num, len(words), s.duration, grid_size,
        words=words, found_words=[],
    )
    kb = hard_action_kb() if is_hard else game_action_kb()

    photo_msg = await context.bot.send_photo(
        chat_id=chat_id,
        photo=io.BytesIO(img_bytes),
        caption=caption,
        parse_mode=ParseMode.HTML,
        reply_markup=kb,
    )
    s.grid_msg_id = photo_msg.message_id
    s.msg_ids.append(photo_msg.message_id)

    # Set timer task
    s._task = asyncio.create_task(_round_timer(context, chat_id, s))


async def _round_timer(context: ContextTypes.DEFAULT_TYPE,
                       chat_id: int, s: GameSession):
    await asyncio.sleep(s.duration)
    if s.active:
        await _end_round(context, chat_id, s, reason="timeout")


async def _is_admin(update: Update) -> bool:
    """Check if the command sender is a group admin or creator."""
    try:
        member = await update.effective_chat.get_member(update.effective_user.id)
        return member.status in ("administrator", "creator")
    except Exception:
        return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  COMMAND HANDLERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await db.upsert_user(user)

    if update.effective_chat.type == "private":
        await update.message.reply_text(
            start_private(user.first_name),
            parse_mode=ParseMode.HTML,
            reply_markup=start_kb(),
        )
    else:
        await update.message.reply_text(
            start_group(),
            parse_mode=ParseMode.HTML,
        )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        help_text(),
        parse_mode=ParseMode.HTML,
    )


async def cmd_theme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎨 <b>Choose a theme for your next game:</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=theme_kb(),
    )


async def cmd_newgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if update.effective_chat.type == "private":
        await update.message.reply_text(
            "➕ Add me to a group to play! Use the button below.",
            reply_markup=start_kb(),
        )
        return

    if sessions.active(chat_id):
        await update.message.reply_text("⚠️ A game is already running! Use /endgame to stop it.")
        return

    if sessions.cooldown(chat_id):
        left = sessions.cooldown_left(chat_id)
        await update.message.reply_text(f"⏳ Please wait {left}s before starting a new game.")
        return

    # Optional theme argument
    args = context.args
    if args:
        theme_key = args[0].lower()
        if theme_key not in THEMES:
            await update.message.reply_text(
                f"❓ Unknown theme <code>{theme_key}</code>. Use /theme to see all themes.",
                parse_mode=ParseMode.HTML,
            )
            return
    else:
        theme_key = None  # will ask for mode, then pick

    # Ask for round mode
    msg = await update.message.reply_text(
        "🚀 <b>Choose round progression mode:</b>\n\n"
        "• <b>Automatic</b> — next round starts automatically when all words found\n"
        "• <b>Manual</b> — you decide when to start each round",
        parse_mode=ParseMode.HTML,
        reply_markup=round_mode_kb("normal"),
    )
    # Store theme choice in bot_data temporarily
    context.bot_data[f"pending_theme:{chat_id}"] = theme_key


async def cmd_newhard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if update.effective_chat.type == "private":
        await update.message.reply_text("➕ Add me to a group to play!")
        return

    if sessions.active(chat_id):
        await update.message.reply_text("⚠️ A game is already running! Use /endgame to stop it.")
        return

    if sessions.cooldown(chat_id):
        left = sessions.cooldown_left(chat_id)
        await update.message.reply_text(f"⏳ Please wait {left}s before starting a new game.")
        return

    msg = await update.message.reply_text(
        "🔥 <b>HARD MODE — Choose round progression:</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=round_mode_kb("hard"),
    )


async def cmd_hint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /hint — reveal first+last letter hints for all unfound words.
    Format: A _ _ _ N  (spaced underscores)
    """
    chat_id = update.effective_chat.id
    s = sessions.get(chat_id)

    if not s or not s.active:
        await update.message.reply_text("💡 No active game. Start one with /newgame!")
        return

    unfound = [w for w in s.words if w not in s.found_words]
    if not unfound:
        msg = await update.message.reply_text(no_hint_text(), parse_mode=ParseMode.HTML)
        s.msg_ids.append(msg.message_id)
        return

    lines = []
    for w in unfound:
        hint = _spaced_hint(w)
        lines.append(f"💡 <code>{hint}</code>  <i>({len(w)} letters)</i>")

    text = "💡 <b>Hints for remaining words:</b>\n\n" + "\n".join(lines)

    # Delete previous hint message to keep chat clean
    if s.hint_msg_id:
        await _safe_delete(context.bot, chat_id, s.hint_msg_id)

    msg = await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    s.hint_msg_id = msg.message_id
    s.msg_ids.append(msg.message_id)


async def cmd_endgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not await _is_admin(update) and update.effective_user.id != OWNER_ID:
        await update.message.reply_text("🚫 Only admins can end the game.")
        return

    s = sessions.get(chat_id)
    if not s or not s.active:
        await update.message.reply_text("No active game to end.")
        return

    await _end_round(context, chat_id, s, reason="endgame")


async def cmd_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    rows = await db.group_leaderboard(chat_id)

    if rows:
        img_bytes = await _run_in_executor(
            render_leaderboard, rows, f"{update.effective_chat.title} Leaderboard"
        )
        await update.message.reply_photo(
            photo=io.BytesIO(img_bytes),
            caption=leaderboard_text(rows, f"{update.effective_chat.title} — Top Players"),
            parse_mode=ParseMode.HTML,
            reply_markup=leaderboard_kb(),
        )
    else:
        await update.message.reply_text(
            leaderboard_text([], "Leaderboard"),
            parse_mode=ParseMode.HTML,
            reply_markup=leaderboard_kb(),
        )


async def cmd_globalboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = await db.global_leaderboard()

    if rows:
        img_bytes = await _run_in_executor(
            render_leaderboard, rows, "Global Leaderboard"
        )
        await update.message.reply_photo(
            photo=io.BytesIO(img_bytes),
            caption=leaderboard_text(rows, "🌍 Global Top Players"),
            parse_mode=ParseMode.HTML,
            reply_markup=globalboard_kb(),
        )
    else:
        await update.message.reply_text(
            leaderboard_text([], "Global Leaderboard"),
            parse_mode=ParseMode.HTML,
            reply_markup=globalboard_kb(),
        )


async def cmd_mystats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    doc  = await db.user_global_stats(user.id)
    await update.message.reply_text(
        my_stats(user.first_name, doc),
        parse_mode=ParseMode.HTML,
    )


async def cmd_resetboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _is_admin(update) and update.effective_user.id != OWNER_ID:
        await update.message.reply_text("🚫 Only admins can reset the leaderboard.")
        return

    await db.reset_group_board(update.effective_chat.id)
    await update.message.reply_text("✅ Group leaderboard has been reset.")


async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    args = context.args
    if not args or args[0] not in ("all", "users", "groups"):
        await update.message.reply_text(BROADCAST_USAGE, parse_mode=ParseMode.HTML)
        return

    target  = args[0]
    message = " ".join(args[1:]).strip()
    if not message:
        await update.message.reply_text(BROADCAST_USAGE, parse_mode=ParseMode.HTML)
        return

    ids: list = []
    if target in ("all", "users"):
        ids += await db.all_user_ids()
    if target in ("all", "groups"):
        ids += await db.all_group_ids()

    sent = failed = 0
    for cid in ids:
        try:
            await context.bot.send_message(cid, message, parse_mode=ParseMode.HTML)
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(BROADCAST_DELAY)

    await update.message.reply_text(
        broadcast_done(sent, failed, len(ids)),
        parse_mode=ParseMode.HTML,
    )


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    stats = await db.bot_stats()
    await update.message.reply_text(
        fmt_bot_stats(stats["users"], stats["groups"]),
        parse_mode=ParseMode.HTML,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MESSAGE HANDLER  (word guesses)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    s = sessions.get(chat_id)
    if not s or not s.active:
        return

    text = update.message.text.strip().upper()
    user = update.effective_user

    if not text.isalpha():
        return

    if s.already_found(text):
        return  # silently ignore already found words

    if not s.valid_guess(text):
        # Wrong guess — reset combo
        s.reset_combo(user.id)
        return

    # Correct guess!
    pts   = s.register(text, user.id, user.first_name, user.username)
    combo = s.p_combos[user.id]
    left  = len(s.words) - len(s.found_words)

    chat  = update.effective_chat
    msg = await update.message.reply_text(
        word_found(user.first_name, text, pts, combo, left),
        parse_mode=ParseMode.HTML,
        reply_markup=word_found_kb(
            s.grid_msg_id,
            chat_username=getattr(chat, "username", None),
            chat_id_int=chat.id,
        ),
    )
    s.msg_ids.append(msg.message_id)
    s.msg_ids.append(update.message.message_id)

    # Update grid image to show found word highlighted
    try:
        new_img = await _run_in_executor(
            render_image,
            s.theme, s.grid, s.placed, s.found_words,
            s.round_num, s.grid_size,
        )
        new_caption = game_start_caption(
            THEMES[s.theme]["name"], THEMES[s.theme]["emoji"],
            s.round_num, len(s.words), s.duration, s.grid_size,
            words=s.words, found_words=s.found_words,
        )
        kb = hard_action_kb() if s.is_hard else game_action_kb()
        await context.bot.edit_message_media(
            chat_id=chat_id,
            message_id=s.grid_msg_id,
            media=InputMediaPhoto(
                media=io.BytesIO(new_img),
                caption=new_caption,
                parse_mode=ParseMode.HTML,
            ),
            reply_markup=kb,
        )
    except Exception as e:
        log.debug(f"Grid update skipped: {e}")

    if s.complete():
        if s._task:
            s._task.cancel()
        await _end_round(context, chat_id, s, reason="complete")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CALLBACK QUERY HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q    = update.callback_query
    data = q.data
    uid  = q.from_user.id
    chat = q.message.chat

    await q.answer()

    # ── start / help / globalboard shortcuts ──
    if data == "cb:start":
        await q.message.edit_text(
            start_private(q.from_user.first_name),
            parse_mode=ParseMode.HTML,
            reply_markup=start_kb(),
        )
        return

    if data == "cb:help":
        await q.message.reply_text(help_text(), parse_mode=ParseMode.HTML)
        return

    if data == "cb:globalboard":
        rows = await db.global_leaderboard()
        if rows:
            img_bytes = await _run_in_executor(render_leaderboard, rows, "Global Leaderboard")
            await q.message.reply_photo(
                photo=io.BytesIO(img_bytes),
                caption=leaderboard_text(rows, "🌍 Global Top Players"),
                parse_mode=ParseMode.HTML,
                reply_markup=globalboard_kb(),
            )
        else:
            await q.message.reply_text(
                leaderboard_text([], "Global Leaderboard"),
                parse_mode=ParseMode.HTML,
                reply_markup=globalboard_kb(),
            )
        return

    if data == "cb:leaderboard":
        chat_id = chat.id
        rows = await db.group_leaderboard(chat_id)
        if rows:
            img_bytes = await _run_in_executor(
                render_leaderboard, rows, f"{chat.title} Leaderboard"
            )
            await q.message.reply_photo(
                photo=io.BytesIO(img_bytes),
                caption=leaderboard_text(rows, f"{chat.title} — Top Players"),
                parse_mode=ParseMode.HTML,
                reply_markup=leaderboard_kb(),
            )
        else:
            await q.message.reply_text(
                leaderboard_text([], "Leaderboard"),
                parse_mode=ParseMode.HTML,
                reply_markup=leaderboard_kb(),
            )
        return

    if data == "cb:endgame":
        chat_id = chat.id
        try:
            member = await chat.get_member(uid)
            is_admin = member.status in ("administrator", "creator")
        except Exception:
            is_admin = False

        if not is_admin and uid != OWNER_ID:
            await q.answer("🚫 Only admins can end the game.", show_alert=True)
            return

        s = sessions.get(chat_id)
        if not s or not s.active:
            await q.answer("No active game.", show_alert=True)
            return

        await _end_round(context, chat_id, s, reason="endgame")
        return

    # ── Round mode selection (startmode:normal:auto / startmode:hard:manual …) ──
    if data.startswith("startmode:"):
        _, game_type, mode = data.split(":")
        chat_id  = chat.id
        is_hard  = (game_type == "hard")

        if sessions.active(chat_id):
            await q.answer("A game is already running!", show_alert=True)
            return

        pending_key = f"pending_theme:{chat_id}"
        theme_key   = context.bot_data.pop(pending_key, None)

        if is_hard:
            theme_key = pick_hard_theme(chat_id, THEME_LIST)
        elif not theme_key:
            theme_key = pick_random_theme(chat_id, THEME_LIST)

        await q.message.delete()
        await _launch_round(
            context, chat_id,
            theme_key=theme_key,
            round_num=1,
            is_hard=is_hard,
            round_mode=mode,
        )
        return

    # ── Theme picker ──
    if data.startswith("theme:"):
        key     = data.split(":", 1)[1]
        chat_id = chat.id

        if sessions.active(chat_id):
            await q.answer("A game is already running!", show_alert=True)
            return

        if key == "random":
            key = pick_random_theme(chat_id, THEME_LIST)

        if key not in THEMES:
            await q.answer("Unknown theme.", show_alert=True)
            return

        # Store theme, ask for round mode
        context.bot_data[f"pending_theme:{chat_id}"] = key
        await q.message.edit_text(
            f"✅ Theme: <b>{THEMES[key]['emoji']} {THEMES[key]['name']}</b>\n\n"
            "Choose round progression mode:",
            parse_mode=ParseMode.HTML,
            reply_markup=round_mode_kb("normal"),
        )
        return

    # ── Next round button (manual mode) ──
    if data.startswith("nextround:"):
        parts       = data.split(":")          # nextround:theme:round:mode
        theme_key   = parts[1]
        next_round  = int(parts[2])
        mode        = parts[3] if len(parts) > 3 else "auto"
        chat_id     = chat.id
        is_hard     = (mode == "hard")

        if sessions.active(chat_id):
            await q.answer("A game is already running!", show_alert=True)
            return

        await q.message.delete()
        await _launch_round(
            context, chat_id,
            theme_key=theme_key,
            round_num=next_round,
            is_hard=is_hard,
            round_mode=mode,
        )
        return

    # ── Leaderboard tabs (lb:chat:today / lb:global:alltime …) ──
    if data.startswith("lb:"):
        _, scope, time_filter = data.split(":")
        chat_id = chat.id

        if scope == "global":
            rows = await db.global_leaderboard()
            title = "🌍 Global Top Players"
            kb    = globalboard_kb(time_filter=time_filter)
        else:
            rows  = await db.group_leaderboard(chat_id)
            title = f"{chat.title} — Top Players"
            kb    = leaderboard_kb(time_filter=time_filter)

        if rows:
            img_bytes = await _run_in_executor(render_leaderboard, rows, title)
            try:
                await q.message.delete()
            except Exception:
                pass
            await q.message.reply_photo(
                photo=io.BytesIO(img_bytes),
                caption=leaderboard_text(rows, title),
                parse_mode=ParseMode.HTML,
                reply_markup=kb,
            )
        else:
            await q.message.edit_text(
                leaderboard_text([], title),
                parse_mode=ParseMode.HTML,
                reply_markup=kb,
            )
        return

    # ── Go-to-grid fallback callback ──
    if data.startswith("cb:gotogrid:"):
        await q.answer("Scroll up to find the grid! 🔠", show_alert=True)
        return


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CHAT MEMBER HANDLER  (bot added / removed)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def on_my_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.my_chat_member
    chat   = result.chat
    new    = result.new_chat_member

    if new.status in ("member", "administrator"):
        # Bot was added to a group
        await db.upsert_group(chat)
        try:
            await context.bot.send_message(
                chat_id=chat.id,
                text=new_group_welcome(chat.title),
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            pass
    elif new.status in ("left", "kicked"):
        await db.mark_group_inactive(chat.id)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  IDLE NUDGE JOB
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def idle_nudge_job(context: ContextTypes.DEFAULT_TYPE):
    """Periodic job: nudge groups that haven't played in a while."""
    group_ids = await db.all_group_ids()
    for chat_id in group_ids:
        if sessions.active(chat_id):
            continue
        if idle_seconds(chat_id) < IDLE_NUDGE_AFTER:
            continue
        # Mark as nudged so we don't spam
        touch_activity(chat_id)
        nudge = random.choice(IDLE_NUDGES)
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=nudge,
                parse_mode=ParseMode.HTML,
            )
        except Exception as e:
            log.debug(f"Nudge failed for {chat_id}: {e}")
        await asyncio.sleep(0.1)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ERROR HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    log.error("Exception while handling update:", exc_info=context.error)
