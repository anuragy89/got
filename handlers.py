import asyncio
import io
import logging
import random
import time

from telegram import Update, InputMediaPhoto
from telegram.constants import ParseMode, ChatType
from telegram.error import TelegramError, Forbidden, BadRequest
from telegram.ext import ContextTypes

import database as db
from config import (
    OWNER_ID, ROUND_DURATION, WORDS_PER_ROUND,
    GRID_SIZE, BROADCAST_DELAY, COOLDOWN_SECONDS,
)
from game import sessions, GameSession
from keyboards import start_kb, theme_kb, game_action_kb, leaderboard_kb, back_kb
from puzzle import build_puzzle, render_image, THEMES, THEME_LIST
from strings import (
    start_private, start_group, new_group_welcome, help_text,
    game_start_caption, word_found, round_end,
    leaderboard_text, my_stats, bot_stats,
    BROADCAST_USAGE, broadcast_done,
    ICO_FIRE, ICO_PUZZLE, ICO_TROPHY, ICO_STAR, ICO_CROWN,
)

log = logging.getLogger(__name__)


# ── Helpers ──────────────────────────────────────────────────────

async def _is_admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> bool:
    if update.effective_user.id == OWNER_ID:
        return True
    try:
        from telegram import ChatMemberAdministrator, ChatMemberOwner
        m = await ctx.bot.get_chat_member(
            update.effective_chat.id, update.effective_user.id
        )
        return isinstance(m, (ChatMemberAdministrator, ChatMemberOwner))
    except Exception:
        return False


async def _end_round(chat_id: int, session: GameSession,
                     ctx: ContextTypes.DEFAULT_TYPE):
    """Finalise a round: post summary, save scores, set cooldown."""
    session.active = False
    summary = session.summary()
    missed  = [w for w in session.words if w not in session.found_words]

    # persist scores
    for row in summary:
        await db.add_score(
            chat_id, row["user_id"], row["name"],
            row["score"], row["words"]
        )

    text = round_end(summary, missed, THEMES[session.theme]["name"])
    try:
        await ctx.bot.send_message(chat_id, text, parse_mode=ParseMode.HTML)
    except TelegramError:
        pass

    sessions.remove(chat_id)
    sessions.set_cooldown(chat_id)


async def _timer_task(chat_id: int, session: GameSession,
                      ctx: ContextTypes.DEFAULT_TYPE):
    """Background task: 15-second warning then end."""
    warn_after = ROUND_DURATION - 15
    await asyncio.sleep(warn_after)
    if not session.active:
        return
    try:
        await ctx.bot.send_message(
            chat_id,
            f"{ICO_FIRE()} <b>15 seconds left!</b> Find more words fast!",
            parse_mode=ParseMode.HTML,
        )
    except TelegramError:
        pass
    await asyncio.sleep(15)
    if session.active:
        await _end_round(chat_id, session, ctx)


async def _launch(chat_id: int, chat_title: str,
                  theme_key: str, ctx: ContextTypes.DEFAULT_TYPE):
    """Build puzzle, render image, start session."""
    t = THEMES[theme_key]

    # build puzzle in executor (CPU-bound)
    loop = asyncio.get_event_loop()
    grid, words, placed = await loop.run_in_executor(
        None, build_puzzle, theme_key, GRID_SIZE, WORDS_PER_ROUND
    )

    # render image in executor (Pillow)
    img = await loop.run_in_executor(
        None, render_image, theme_key, grid, placed, [], 1, GRID_SIZE
    )

    session = GameSession(chat_id, theme_key, grid, words, placed, 1, img)
    sessions.put(session)

    caption = game_start_caption(
        t["name"], t["emoji"], session.round_num,
        len(words), ROUND_DURATION
    )
    try:
        msg = await ctx.bot.send_photo(
            chat_id,
            photo=io.BytesIO(img),
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=game_action_kb(),
        )
        session.grid_msg_id = msg.message_id
    except TelegramError as e:
        log.error(f"send_photo failed {chat_id}: {e}")
        sessions.remove(chat_id)
        return

    task = asyncio.create_task(_timer_task(chat_id, session, ctx))
    session._task = task


# ── /start ───────────────────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    await db.upsert_user(user)

    if chat.type == ChatType.PRIVATE:
        await update.message.reply_text(
            start_private(user.first_name),
            parse_mode=ParseMode.HTML,
            reply_markup=start_kb(),
        )
    else:
        await db.upsert_group(chat)
        await update.message.reply_text(
            start_group(), parse_mode=ParseMode.HTML
        )


# ── Bot added / removed from group ───────────────────────────────

async def on_my_chat_member(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    result = update.my_chat_member
    if not result:
        return
    status = result.new_chat_member.status
    chat   = update.effective_chat

    if status in ("member", "administrator"):
        await db.upsert_group(chat)
        try:
            await ctx.bot.send_message(
                chat.id,
                new_group_welcome(chat.title or "the group"),
                parse_mode=ParseMode.HTML,
                reply_markup=game_action_kb(),
            )
        except TelegramError as e:
            log.warning(f"Welcome failed {chat.id}: {e}")

    elif status in ("left", "kicked"):
        await db.mark_group_inactive(chat.id)


# ── /help ────────────────────────────────────────────────────────

async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        help_text(), parse_mode=ParseMode.HTML, reply_markup=back_kb()
    )


# ── /theme ───────────────────────────────────────────────────────

async def cmd_theme(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"{ICO_PUZZLE()} <b>Choose a theme:</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=theme_kb(),
    )


# ── /newgame ─────────────────────────────────────────────────────

async def cmd_newgame(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == ChatType.PRIVATE:
        await update.message.reply_text(
            f"{ICO_PUZZLE()} Add me to a group to play! "
            "Word Grid games run in group chats.",
            parse_mode=ParseMode.HTML,
            reply_markup=start_kb(),
        )
        return

    await db.upsert_user(user)
    await db.upsert_group(chat)

    if sessions.active(chat.id):
        await update.message.reply_text(
            f"{ICO_FIRE()} A game is already running! Finish it first.",
            parse_mode=ParseMode.HTML,
        )
        return

    if sessions.cooldown(chat.id):
        left = sessions.cooldown_left(chat.id)
        await update.message.reply_text(
            f"⏳ Cooldown — next game in <b>{left}s</b>.",
            parse_mode=ParseMode.HTML,
        )
        return

    args = ctx.args or []
    arg  = args[0].lower() if args else "random"
    theme_key = arg if arg in THEMES else random.choice(THEME_LIST)

    await _launch(chat.id, chat.title or "", theme_key, ctx)


# ── Message handler — word guesses ───────────────────────────────

async def on_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg  = update.message
    if not msg or not msg.text:
        return
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == ChatType.PRIVATE:
        return

    session = sessions.get(chat.id)
    if not session or not session.active:
        return

    word = msg.text.strip().upper()
    if len(word) < 3 or not word.isalpha():
        return

    if session.valid_guess(word):
        name = user.first_name or user.username or "Player"
        pts  = session.register(word, user.id, name)
        left = len(session.words) - len(session.found_words)
        combo = session.p_combos.get(user.id, 1)

        await db.upsert_user(user)

        # Re-render grid with found highlights
        loop = asyncio.get_event_loop()
        new_img = await loop.run_in_executor(
            None, render_image,
            session.theme, session.grid, session.placed,
            session.found_words, session.round_num, GRID_SIZE
        )
        session.img_bytes = new_img

        # Reply
        await msg.reply_text(
            word_found(name, word, pts, combo, left),
            parse_mode=ParseMode.HTML,
        )

        # Edit grid photo in-place
        if session.grid_msg_id:
            try:
                t = THEMES[session.theme]
                new_caption = game_start_caption(
                    t["name"], t["emoji"],
                    session.round_num, len(session.words), ROUND_DURATION
                )
                await ctx.bot.edit_message_media(
                    chat_id=chat.id,
                    message_id=session.grid_msg_id,
                    media=InputMediaPhoto(
                        media=io.BytesIO(new_img),
                        caption=new_caption,
                        parse_mode=ParseMode.HTML,
                    ),
                )
            except (TelegramError, BadRequest):
                pass  # non-critical

        if session.complete():
            if session._task:
                session._task.cancel()
            await _end_round(chat.id, session, ctx)

    elif session.already_found(word):
        session.reset_combo(user.id)
        await msg.reply_text(
            f"❌ <code>{word}</code> was already found!",
            parse_mode=ParseMode.HTML,
        )


# ── /leaderboard ─────────────────────────────────────────────────

async def cmd_leaderboard(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == ChatType.PRIVATE:
        rows  = await db.global_leaderboard()
        title = "🌍 Global Leaderboard"
    else:
        rows  = await db.group_leaderboard(chat.id)
        title = f"🏆 {chat.title}"
    await update.message.reply_text(
        leaderboard_text(rows, title),
        parse_mode=ParseMode.HTML,
        reply_markup=leaderboard_kb(),
    )


# ── /globalboard ─────────────────────────────────────────────────

async def cmd_globalboard(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    rows = await db.global_leaderboard()
    await update.message.reply_text(
        leaderboard_text(rows, "🌍 Global Leaderboard"),
        parse_mode=ParseMode.HTML,
        reply_markup=leaderboard_kb(),
    )


# ── /mystats ─────────────────────────────────────────────────────

async def cmd_mystats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await db.upsert_user(user)
    doc = await db.user_global_stats(user.id)
    if not doc:
        await update.message.reply_text(
            "You haven't played yet! Join a group and type /newgame."
        )
        return
    await update.message.reply_text(
        my_stats(user.first_name, doc), parse_mode=ParseMode.HTML
    )


# ── /endgame ─────────────────────────────────────────────────────

async def cmd_endgame(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await _is_admin(update, ctx):
        await update.message.reply_text("❌ Admins only.")
        return
    chat    = update.effective_chat
    session = sessions.get(chat.id)
    if not session or not session.active:
        await update.message.reply_text("No active game.")
        return
    if session._task:
        session._task.cancel()
    await _end_round(chat.id, session, ctx)


# ── /resetboard ──────────────────────────────────────────────────

async def cmd_resetboard(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await _is_admin(update, ctx):
        await update.message.reply_text("❌ Admins only.")
        return
    await db.reset_group_board(update.effective_chat.id)
    await update.message.reply_text(
        f"{ICO_TROPHY()} Group leaderboard reset.",
        parse_mode=ParseMode.HTML,
    )


# ── /stats (owner) ───────────────────────────────────────────────

async def cmd_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    data = await db.bot_stats()
    await update.message.reply_text(
        bot_stats(data["users"], data["groups"]),
        parse_mode=ParseMode.HTML,
    )


# ── /broadcast (owner) ───────────────────────────────────────────

async def cmd_broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    args = ctx.args or []
    if not args or args[0] not in ("all", "users", "groups"):
        await update.message.reply_text(BROADCAST_USAGE, parse_mode=ParseMode.HTML)
        return

    target = args[0]
    text   = " ".join(args[1:]).strip()
    if not text:
        await update.message.reply_text("❌ Message is empty.")
        return

    ids: list = []
    if target in ("all", "users"):
        ids += await db.all_user_ids()
    if target in ("all", "groups"):
        ids += await db.all_group_ids()
    ids   = list(set(ids))
    total = len(ids)

    prog = await update.message.reply_text(
        f"📢 Broadcasting to <b>{total}</b> targets…",
        parse_mode=ParseMode.HTML,
    )

    sent = failed = 0
    for cid in ids:
        try:
            await ctx.bot.send_message(cid, text, parse_mode=ParseMode.HTML)
            sent += 1
        except Forbidden:
            await db.mark_blocked(cid, True)
            failed += 1
        except TelegramError:
            failed += 1
        await asyncio.sleep(BROADCAST_DELAY)

    await prog.edit_text(
        broadcast_done(sent, failed, total), parse_mode=ParseMode.HTML
    )


# ── Callback queries ─────────────────────────────────────────────

async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q    = update.callback_query
    data = q.data
    chat = update.effective_chat
    user = update.effective_user

    await q.answer()

    if data == "cb:start":
        await q.edit_message_text(
            start_private(user.first_name),
            parse_mode=ParseMode.HTML,
            reply_markup=start_kb(),
        )

    elif data == "cb:help":
        await q.edit_message_text(
            help_text(), parse_mode=ParseMode.HTML, reply_markup=back_kb()
        )

    elif data == "cb:leaderboard":
        if chat.type == ChatType.PRIVATE:
            rows  = await db.global_leaderboard()
            title = "🌍 Global Leaderboard"
        else:
            rows  = await db.group_leaderboard(chat.id)
            title = f"🏆 {chat.title}"
        await q.edit_message_text(
            leaderboard_text(rows, title),
            parse_mode=ParseMode.HTML,
            reply_markup=leaderboard_kb(),
        )

    elif data == "cb:globalboard":
        rows = await db.global_leaderboard()
        await q.edit_message_text(
            leaderboard_text(rows, "🌍 Global Leaderboard"),
            parse_mode=ParseMode.HTML,
            reply_markup=leaderboard_kb(),
        )

    elif data == "cb:timeleft":
        session = sessions.get(chat.id)
        if session and session.active:
            left = session.time_left()
            await q.answer(f"⏱ {left} seconds remaining!", show_alert=True)
        else:
            await q.answer("No active game.", show_alert=True)

    elif data.startswith("theme:"):
        key = data.split(":")[1]
        if key == "random":
            key = random.choice(THEME_LIST)

        if chat.type == ChatType.PRIVATE:
            await q.answer("Add me to a group to play!", show_alert=True)
            return

        if sessions.active(chat.id):
            await q.answer("A game is running! Finish it first.", show_alert=True)
            return
        if sessions.cooldown(chat.id):
            left = sessions.cooldown_left(chat.id)
            await q.answer(f"Cooldown — {left}s left.", show_alert=True)
            return

        await db.upsert_group(chat)
        await q.answer(f"Starting {THEMES[key]['emoji']} {THEMES[key]['name']}!")
        try:
            await q.delete_message()
        except TelegramError:
            pass
        await _launch(chat.id, chat.title or "", key, ctx)
