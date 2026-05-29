import asyncio
import io
import logging
import random

from telegram import Update, InputMediaPhoto
from telegram.constants import ParseMode, ChatType
from telegram.error import TelegramError, Forbidden, BadRequest
from telegram.ext import ContextTypes

from render_cards import render_leaderboard, render_me_card
import database as db
from config import OWNER_ID, BROADCAST_DELAY, IDLE_NUDGE_AFTER
from game import (
    sessions, GameSession,
    pick_random_theme, pick_hard_theme, pick_hard_words,
    NORMAL_GRID_SIZE, NORMAL_N_WORDS_MIN, NORMAL_N_WORDS_MAX, NORMAL_DURATION,
    HARD_GRID_SIZE, HARD_N_WORDS_MIN, HARD_N_WORDS_MAX,
    HARD_POINTS_PER_WORD, HARD_FIRST_PTS,
    EASY_WORD_MAX_LEN, HARD_WORD_MIN_LEN,
    touch_activity, idle_seconds,
)
from keyboards import (
    start_kb, theme_kb, game_action_kb, hard_action_kb,
    leaderboard_kb, globalboard_kb, back_kb,
    round_over_no_next_kb, word_found_kb, me_kb,
    final_round_kb,
)
from puzzle import build_puzzle, render_image, THEMES, THEME_LIST
from strings import (
    start_private, start_group, new_group_welcome, help_text,
    game_start_caption, word_found, round_end,
    leaderboard_text, my_stats, bot_stats,
    BROADCAST_USAGE, broadcast_done,
    hint_text, no_hint_text, IDLE_NUDGES,
    ICO_FIRE, ICO_PUZZLE, ICO_TROPHY, ICO_STAR, ICO_CROWN, ICO_ROCKET,
)

log = logging.getLogger(__name__)

# ── Per-chat end-round lock ───────────────────────────────────────
_ending_round: set[int] = set()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def _is_admin(update, ctx):
    if update.effective_user.id == OWNER_ID:
        return True
    try:
        from telegram import ChatMemberAdministrator, ChatMemberOwner
        m = await ctx.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return isinstance(m, (ChatMemberAdministrator, ChatMemberOwner))
    except Exception:
        return False


async def _safe_edit_text(q, text, parse_mode=ParseMode.HTML, reply_markup=None):
    try:
        await q.edit_message_text(text, parse_mode=parse_mode, reply_markup=reply_markup)
    except BadRequest as e:
        err = str(e).lower()
        if "there is no text in the message" in err:
            try:
                await q.delete_message()
            except TelegramError:
                pass
            try:
                await q.message.chat.send_message(text, parse_mode=parse_mode,
                                                   reply_markup=reply_markup)
            except TelegramError:
                pass
        elif "message is not modified" in err:
            pass
        else:
            log.warning(f"edit_message_text failed: {e}")


def _build_hint_text(session) -> str:
    lines = []
    for w in session.words:
        if w in session.found_words:
            lines.append(f"✅ <b>{w}</b> — found!")
        else:
            lines.append(hint_text(session.get_hint(w), len(w)))
    return "\n\n".join(lines)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CORE ROUND LOGIC
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def _end_round(chat_id, session, ctx, from_timer=False):
    if chat_id in _ending_round:
        return
    _ending_round.add(chat_id)

    try:
        if not session.active:
            return
        session.active = False

        summary        = session.summary()
        missed         = [w for w in session.words if w not in session.found_words]
        round_complete = session.complete()

        for row in summary:
            await db.add_score(chat_id, row["user_id"], row["name"], row["score"],
                               row["words"], username=row.get("username"))

        text = round_end(
            summary, missed, THEMES[session.theme]["name"],
            round_num=1, max_rounds=1,
            round_complete=round_complete,
        )

        kb = final_round_kb()

        try:
            await ctx.bot.send_message(chat_id, text, parse_mode=ParseMode.HTML,
                                       reply_markup=kb)
        except TelegramError:
            pass

        touch_activity(chat_id)
        sessions.remove(chat_id)

    finally:
        _ending_round.discard(chat_id)


async def _timer_task(chat_id, session, ctx):
    duration = session.duration

    # ── Warning 1: 100 seconds left ──────────────────────────────
    warn1_after = duration - 100
    if warn1_after > 0:
        await asyncio.sleep(warn1_after)
        if not session.active:
            return
        try:
            warn_msg = await ctx.bot.send_message(
                chat_id,
                f"⚠️ <b>100 seconds left!</b> Hurry up and find more words! {ICO_FIRE()}",
                parse_mode=ParseMode.HTML,
            )
            session.msg_ids.append(warn_msg.message_id)
        except TelegramError:
            pass
    else:
        await asyncio.sleep(max(0, warn1_after + duration))  # already past

    if not session.active:
        return

    # ── Warning 2: 15 seconds left ───────────────────────────────
    warn2_after = 85  # 100 - 15 = 85 more seconds after first warning
    await asyncio.sleep(warn2_after)
    if not session.active:
        return
    try:
        warn_msg2 = await ctx.bot.send_message(
            chat_id,
            f"🚨 <b>ONLY 15 SECONDS LEFT!</b> Last chance! {ICO_LIGHTNING()}",
            parse_mode=ParseMode.HTML,
        )
        session.msg_ids.append(warn_msg2.message_id)
    except TelegramError:
        pass

    # ── Final 15 second wait ─────────────────────────────────────
    await asyncio.sleep(15)
    if session.active:
        await _end_round(chat_id, session, ctx, from_timer=True)


async def _launch_normal(chat_id: int, theme_key: str, ctx) -> None:
    """Start a normal game — 10×10 grid, 10-15 easy words."""
    t    = THEMES[theme_key]
    size = NORMAL_GRID_SIZE

    n_words = random.randint(NORMAL_N_WORDS_MIN, NORMAL_N_WORDS_MAX)

    loop = asyncio.get_event_loop()
    try:
        grid, words, placed = await loop.run_in_executor(
            None, build_puzzle, theme_key, size, n_words, True  # easy_mode=True
        )
    except Exception as e:
        log.error(f"_launch_normal build_puzzle failed chat={chat_id}: {e}")
        try:
            await ctx.bot.send_message(
                chat_id, "⚠️ Couldn't generate puzzle. Please try /newgame again!",
                parse_mode=ParseMode.HTML,
            )
        except TelegramError:
            pass
        return

    try:
        img = await loop.run_in_executor(
            None, render_image, theme_key, grid, placed, [], 1, size
        )
    except Exception as e:
        log.error(f"_launch_normal render_image failed chat={chat_id}: {e}")
        try:
            await ctx.bot.send_message(
                chat_id, "⚠️ Couldn't render grid. Please try /newgame again!",
                parse_mode=ParseMode.HTML,
            )
        except TelegramError:
            pass
        return

    session = GameSession(chat_id, theme_key, grid, words, placed, img, is_hard=False)
    sessions.put(session)
    touch_activity(chat_id)

    caption = game_start_caption(
        t["name"], t["emoji"], "easy", len(words), NORMAL_DURATION, size,
        words=words, found_words=[],
    )
    try:
        msg = await ctx.bot.send_photo(
            chat_id, photo=io.BytesIO(img),
            caption=caption, parse_mode=ParseMode.HTML,
            reply_markup=game_action_kb(),
        )
        session.grid_msg_id = msg.message_id
    except TelegramError as e:
        log.error(f"send_photo (normal) failed {chat_id}: {e}")
        sessions.remove(chat_id)
        return

    session._task = asyncio.create_task(_timer_task(chat_id, session, ctx))


async def _launch_hard(chat_id: int, ctx) -> None:
    """Start a hard game — 10×10 grid, 10-15 hard words, longer timer."""
    from puzzle import _place, _empty, _fill

    theme_key = pick_hard_theme(chat_id, THEME_LIST)
    t         = THEMES[theme_key]
    size      = HARD_GRID_SIZE

    hard_words = pick_hard_words(
        chat_id, theme_key, t["words"],
        HARD_N_WORDS_MIN, HARD_N_WORDS_MAX,
    )

    loop = asyncio.get_event_loop()

    def _build():
        import random as _rand
        best_grid, best_chosen, best_placed = None, [], []
        for _ in range(5):
            grid   = _empty(size)
            placed = []
            chosen = []
            for w in _rand.sample(hard_words, len(hard_words)):
                cells = _place(grid, w, size)
                if cells:
                    chosen.append(w)
                    placed.append({"word": w, "cells": cells})
            if len(chosen) > len(best_chosen):
                best_grid, best_chosen, best_placed = grid, chosen, placed
            if len(chosen) >= HARD_N_WORDS_MIN:
                break
        if not best_chosen:
            raise ValueError("Hard puzzle: couldn't place any words")
        _fill(best_grid, size)
        return best_grid, best_chosen, best_placed

    try:
        grid, words, placed = await loop.run_in_executor(None, _build)
    except ValueError as e:
        log.error(f"_launch_hard: {e}")
        try:
            await ctx.bot.send_message(
                chat_id, "⚠️ Could not generate hard puzzle. Try /newhard again!",
                parse_mode=ParseMode.HTML,
            )
        except TelegramError:
            pass
        return

    img = await loop.run_in_executor(
        None, render_image, theme_key, grid, placed, [], 1, size,
    )

    session = GameSession(chat_id, theme_key, grid, words, placed, img, is_hard=True)
    sessions.put(session)
    touch_activity(chat_id)

    caption = game_start_caption(
        t["name"], t["emoji"], "hard", len(words), session.duration, size,
        words=words, found_words=[],
    )
    caption = "🔥 <b>HARD MODE</b> — " + caption[caption.index("<b>"):] if "<b>" in caption else caption

    try:
        msg = await ctx.bot.send_photo(
            chat_id, photo=io.BytesIO(img),
            caption=caption, parse_mode=ParseMode.HTML,
            reply_markup=hard_action_kb(),
        )
        session.grid_msg_id = msg.message_id
    except TelegramError as e:
        log.error(f"send_photo (hard) failed {chat_id}: {e}")
        sessions.remove(chat_id)
        return

    session._task = asyncio.create_task(_timer_task(chat_id, session, ctx))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  COMMANDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    await db.upsert_user(user)
    if chat.type == ChatType.PRIVATE:
        BANNER_URL = "https://ibb.co/JjJrTmBt"
        caption    = start_private(user.first_name)
        try:
            await update.message.reply_photo(
                photo=BANNER_URL, caption=caption,
                parse_mode=ParseMode.HTML, reply_markup=start_kb(),
            )
        except TelegramError as e:
            log.warning(f"reply_photo failed in /start: {e}")
            await update.message.reply_text(
                caption, parse_mode=ParseMode.HTML, reply_markup=start_kb()
            )
    else:
        await db.upsert_group(chat)
        await update.message.reply_text(start_group(), parse_mode=ParseMode.HTML)


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
                chat.id, new_group_welcome(chat.title or "the group"),
                parse_mode=ParseMode.HTML, reply_markup=game_action_kb(),
            )
        except TelegramError as e:
            log.warning(f"Welcome failed {chat.id}: {e}")
    elif status in ("left", "kicked"):
        await db.mark_group_inactive(chat.id)


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        help_text(), parse_mode=ParseMode.HTML, reply_markup=back_kb()
    )


async def cmd_theme(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"{ICO_PUZZLE()} <b>Choose a theme:</b>",
        parse_mode=ParseMode.HTML, reply_markup=theme_kb()
    )


async def cmd_newgame(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    if chat.type == ChatType.PRIVATE:
        await update.message.reply_text(
            f"{ICO_PUZZLE()} Add me to a group to play!",
            parse_mode=ParseMode.HTML, reply_markup=start_kb()
        )
        return
    await db.upsert_user(user)
    await db.upsert_group(chat)
    if sessions.active(chat.id):
        await update.message.reply_text(
            f"{ICO_FIRE()} A game is already running!", parse_mode=ParseMode.HTML
        )
        return

    args      = ctx.args or []
    arg       = args[0].lower() if args else "random"
    theme_key = arg if arg in THEMES else pick_random_theme(chat.id, THEME_LIST)
    await _launch_normal(chat.id, theme_key, ctx)


async def cmd_newhard(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    if chat.type == ChatType.PRIVATE:
        await update.message.reply_text(
            f"{ICO_PUZZLE()} Add me to a group to play Hard Mode!",
            parse_mode=ParseMode.HTML, reply_markup=start_kb(),
        )
        return
    await db.upsert_user(user)
    await db.upsert_group(chat)
    if sessions.active(chat.id):
        await update.message.reply_text(
            f"{ICO_FIRE()} A game is already running!", parse_mode=ParseMode.HTML
        )
        return
    await _launch_hard(chat.id, ctx)


async def cmd_hint(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == ChatType.PRIVATE:
        await update.message.reply_text("Hints only work during a group game!")
        return
    session = sessions.get(chat.id)
    if not session or not session.active:
        await update.message.reply_text("No active game to hint!")
        return
    unfound = [w for w in session.words if w not in session.found_words]
    if not unfound:
        await update.message.reply_text(no_hint_text(), parse_mode=ParseMode.HTML)
        return

    hint_body = _build_hint_text(session)

    if session.hint_msg_id:
        try:
            await ctx.bot.edit_message_text(
                chat_id=chat.id, message_id=session.hint_msg_id,
                text=hint_body, parse_mode=ParseMode.HTML,
            )
            return
        except TelegramError:
            pass

    hint_msg = await update.message.reply_text(hint_body, parse_mode=ParseMode.HTML)
    session.hint_msg_id = hint_msg.message_id
    session.msg_ids.append(hint_msg.message_id)


async def on_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
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
        name  = user.first_name or user.username or "Player"
        pts   = session.register(word, user.id, name, username=getattr(user, "username", None))
        left  = len(session.words) - len(session.found_words)
        combo = session.p_combos.get(user.id, 1)
        await db.upsert_user(user)

        loop    = asyncio.get_event_loop()
        new_img = await loop.run_in_executor(
            None, render_image, session.theme, session.grid, session.placed,
            session.found_words, session.round_num, session.grid_size,
        )
        session.img_bytes = new_img

        kb = word_found_kb(
            session.grid_msg_id,
            chat_username=getattr(chat, "username", None),
            chat_id_int=chat.id,
        ) if session.grid_msg_id else None

        reply = await msg.reply_text(
            word_found(name, word, pts, combo, left),
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
        )
        session.msg_ids.append(reply.message_id)

        # Update grid image + caption
        if session.grid_msg_id:
            try:
                t           = THEMES[session.theme]
                new_caption = game_start_caption(
                    t["name"], t["emoji"], "hard" if session.is_hard else "easy",
                    len(session.words), session.duration, session.grid_size,
                    words=session.words, found_words=session.found_words,
                )
                if session.is_hard:
                    new_caption = f"🔥 <b>HARD MODE</b> — {new_caption[new_caption.index('<b>'):]}" if "<b>" in new_caption else new_caption
                await ctx.bot.edit_message_media(
                    chat_id=chat.id, message_id=session.grid_msg_id,
                    media=InputMediaPhoto(
                        media=io.BytesIO(new_img),
                        caption=new_caption,
                        parse_mode=ParseMode.HTML,
                    ),
                )
            except (TelegramError, BadRequest):
                pass

        if session.complete():
            if session._task:
                session._task.cancel()
            await _end_round(chat.id, session, ctx)

    elif session.already_found(word):
        session.reset_combo(user.id)
        reply = await msg.reply_text(
            f"❌ <code>{word}</code> was already found!", parse_mode=ParseMode.HTML
        )
        session.msg_ids.append(reply.message_id)


async def cmd_leaderboard(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == ChatType.PRIVATE:
        rows  = await db.global_leaderboard(limit=15)
        title = "🌍 Global Leaderboard"
        kb    = globalboard_kb()
    else:
        rows  = await db.group_leaderboard(chat.id, limit=15)
        title = f"🏆 {chat.title or 'Group Leaderboard'}"
        kb    = leaderboard_kb()
    await update.message.reply_text(
        leaderboard_text(rows, title), parse_mode=ParseMode.HTML, reply_markup=kb
    )


async def cmd_globalboard(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    rows = await db.global_leaderboard()
    kb   = globalboard_kb()
    await update.message.reply_text(
        leaderboard_text(rows, "🌍 Global Leaderboard"),
        parse_mode=ParseMode.HTML, reply_markup=kb,
    )


async def cmd_mystats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await db.upsert_user(user)
    doc = await db.user_global_stats(user.id)
    if not doc:
        await update.message.reply_text(
            "You haven't played yet! Join a group and type /newgame."
        )
        return
    await update.message.reply_text(my_stats(user.first_name, doc), parse_mode=ParseMode.HTML)


async def cmd_me(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await db.upsert_user(user)
    global_doc = await db.user_global_stats(user.id)
    if not global_doc:
        await update.message.reply_text(
            f"👤 <b>{user.first_name}</b>, you haven't played yet!\n"
            "Join a group and type /newgame to start building your profile.",
            parse_mode=ParseMode.HTML,
        )
        return

    all_rows    = await db.global_leaderboard(limit=500)
    global_rank = next(
        (i+1 for i, r in enumerate(all_rows) if r.get("user_id") == user.id), 0
    ) or len(all_rows) + 1

    words_found   = global_doc.get("words_found", 0)
    score         = global_doc.get("score", 0)
    rounds_won    = global_doc.get("rounds_won", 0)
    rounds_played = global_doc.get("rounds_played", 0)
    streak_days   = global_doc.get("streak_days", 0)

    avatar_bytes = None
    try:
        photos = await ctx.bot.get_user_profile_photos(user.id, limit=1)
        if photos.photos:
            file = await ctx.bot.get_file(photos.photos[0][-1].file_id)
            buf  = io.BytesIO()
            await file.download_to_memory(buf)
            avatar_bytes = buf.getvalue()
    except Exception:
        pass

    loop = asyncio.get_event_loop()
    img  = await loop.run_in_executor(
        None, render_me_card,
        user.first_name, user.id,
        words_found, score, global_rank,
        rounds_won, rounds_played, streak_days,
        0, 0, "", 0, 0,
        avatar_bytes,
        False, -1,
    )

    await update.message.reply_photo(
        photo=io.BytesIO(img),
        caption=f"👤 <b>{user.first_name}'s</b> WordGrid Card",
        parse_mode=ParseMode.HTML,
        reply_markup=me_kb(),
    )


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


async def cmd_resetboard(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await _is_admin(update, ctx):
        await update.message.reply_text("❌ Admins only.")
        return
    await db.reset_group_board(update.effective_chat.id)
    await update.message.reply_text(
        f"{ICO_TROPHY()} Group leaderboard reset.", parse_mode=ParseMode.HTML
    )


async def cmd_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    data = await db.bot_stats()
    await update.message.reply_text(
        bot_stats(data["users"], data["groups"]), parse_mode=ParseMode.HTML
    )


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
    ids = []
    if target in ("all", "users"):
        ids += await db.all_user_ids()
    if target in ("all", "groups"):
        ids += await db.all_group_ids()
    ids   = list(set(ids))
    total = len(ids)
    prog  = await update.message.reply_text(
        f"📢 Broadcasting to <b>{total}</b> targets…", parse_mode=ParseMode.HTML
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
    await prog.edit_text(broadcast_done(sent, failed, total), parse_mode=ParseMode.HTML)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  IDLE NUDGE JOB
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def idle_nudge_job(ctx: ContextTypes.DEFAULT_TYPE):
    group_ids = await db.all_group_ids()
    for chat_id in group_ids:
        if sessions.active(chat_id):
            continue
        if idle_seconds(chat_id) < IDLE_NUDGE_AFTER:
            continue
        try:
            await ctx.bot.send_message(
                chat_id, random.choice(IDLE_NUDGES), parse_mode=ParseMode.HTML,
            )
            touch_activity(chat_id)
        except Forbidden:
            await db.mark_group_inactive(chat_id)
        except TelegramError:
            pass
        await asyncio.sleep(0.05)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CALLBACKS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q    = update.callback_query
    data = q.data
    chat = update.effective_chat
    user = update.effective_user
    await q.answer()

    if data == "cb:start":
        await _safe_edit_text(q, start_private(user.first_name), reply_markup=start_kb())

    elif data == "cb:help":
        await _safe_edit_text(q, help_text(), reply_markup=back_kb())

    elif data == "cb:leaderboard":
        if chat.type == ChatType.PRIVATE:
            rows  = await db.global_leaderboard(limit=15)
            title = "🌍 Global Leaderboard"
            kb    = globalboard_kb()
        else:
            rows  = await db.group_leaderboard(chat.id, limit=15)
            title = f"🏆 {chat.title or 'Group Leaderboard'}"
            kb    = leaderboard_kb()
        await _safe_edit_text(q, leaderboard_text(rows, title), reply_markup=kb)

    elif data == "cb:globalboard":
        rows = await db.global_leaderboard(limit=15)
        await _safe_edit_text(
            q, leaderboard_text(rows, "🌍 Global Leaderboard"),
            reply_markup=globalboard_kb(),
        )

    elif data.startswith("lb:"):
        parts   = data.split(":")
        scope   = parts[1] if len(parts) > 1 else "chat"
        tfilter = parts[2] if len(parts) > 2 else "alltime"
        if scope == "global":
            rows  = await db.global_leaderboard(limit=15, time_filter=tfilter)
            title = "🌍 Global Leaderboard"
            kb    = globalboard_kb(time_filter=tfilter)
        else:
            rows  = await db.group_leaderboard(chat.id, limit=15, time_filter=tfilter)
            title = f"🏆 {chat.title or 'Group'} Leaderboard"
            kb    = leaderboard_kb(time_filter=tfilter)
        await _safe_edit_text(q, leaderboard_text(rows, title), reply_markup=kb)

    elif data == "cb:timeleft":
        session = sessions.get(chat.id)
        if session and session.active:
            await q.answer(f"⏱ {session.time_left()} seconds remaining!", show_alert=True)
        else:
            await q.answer("No active game.", show_alert=True)

    elif data == "cb:hint":
        session = sessions.get(chat.id)
        if not session or not session.active:
            await q.answer("No active game!", show_alert=True)
            return
        unfound = [w for w in session.words if w not in session.found_words]
        if not unfound:
            await q.answer("All words found already!", show_alert=True)
            return
        hint_body = _build_hint_text(session)
        if session.hint_msg_id:
            try:
                await ctx.bot.edit_message_text(
                    chat_id=chat.id, message_id=session.hint_msg_id,
                    text=hint_body, parse_mode=ParseMode.HTML,
                )
                return
            except TelegramError:
                pass
        try:
            hint_msg = await ctx.bot.send_message(chat.id, hint_body, parse_mode=ParseMode.HTML)
            session.hint_msg_id = hint_msg.message_id
            session.msg_ids.append(hint_msg.message_id)
        except TelegramError:
            pass

    elif data.startswith("cb:gotogrid:"):
        try:
            grid_msg_id = int(data.split(":")[2])
            chat_obj    = await ctx.bot.get_chat(chat.id)
            username    = getattr(chat_obj, "username", None)
            if username:
                link = f"https://t.me/{username}/{grid_msg_id}"
            else:
                raw     = str(chat.id)
                numeric = raw[4:] if raw.startswith("-100") else raw.lstrip("-")
                link    = f"https://t.me/c/{numeric}/{grid_msg_id}"
            await q.answer(f"Tap to jump → {link}", show_alert=True)
        except Exception:
            await q.answer("Scroll up to find the grid!", show_alert=True)

    elif data == "cb:endgame":
        if user.id != OWNER_ID:
            try:
                from telegram import ChatMemberAdministrator, ChatMemberOwner
                m = await ctx.bot.get_chat_member(chat.id, user.id)
                if not isinstance(m, (ChatMemberAdministrator, ChatMemberOwner)):
                    await q.answer("Admins only!", show_alert=True)
                    return
            except Exception:
                await q.answer("Admins only!", show_alert=True)
                return
        session = sessions.get(chat.id)
        if not session or not session.active:
            await q.answer("No active game.", show_alert=True)
            return
        if session._task:
            session._task.cancel()
        await _end_round(chat.id, session, ctx)

    elif data.startswith("theme:"):
        key = data.split(":")[1]
        if key == "random":
            key = pick_random_theme(chat.id, THEME_LIST)
        if chat.type == ChatType.PRIVATE:
            await q.answer("Add me to a group to play!", show_alert=True)
            return
        if sessions.active(chat.id):
            await q.answer("A game is running! Finish it first.", show_alert=True)
            return
        await db.upsert_group(chat)
        await q.answer(f"🎮 Starting {THEMES[key]['name']}!")
        try:
            await q.delete_message()
        except TelegramError:
            pass
        await _launch_normal(chat.id, key, ctx)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GLOBAL ERROR HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def error_handler(update: object, ctx: ContextTypes.DEFAULT_TYPE):
    err = ctx.error
    if isinstance(err, (Forbidden, BadRequest)):
        log.warning(f"Ignored TelegramError: {err}")
        return
    if isinstance(err, TelegramError):
        log.warning(f"TelegramError (non-critical): {err}")
        return
    log.error("Unhandled exception:", exc_info=err)
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ Something went wrong. Please try again in a moment."
            )
        except TelegramError:
            pass
