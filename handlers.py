import asyncio
import io
import logging
import random

from telegram import Update, InputMediaPhoto, InputMediaAnimation
from telegram.constants import ParseMode, ChatType
from telegram.error import TelegramError, Forbidden, BadRequest
from telegram.ext import ContextTypes

from countdown_gif import build_countdown_gif
from render_cards import render_leaderboard, render_rank_tiers, render_me_card
import database as db
from config import OWNER_ID, BROADCAST_DELAY, MSG_DELETE_AFTER, IDLE_NUDGE_AFTER
from game import (
    sessions, GameSession, get_level, MAX_ROUNDS,
    pick_random_theme, pick_next_round_theme,
    pick_hard_theme, pick_hard_words,
    HARD_GRID_SIZE, HARD_N_WORDS_MIN, HARD_N_WORDS_MAX,
    HARD_POINTS_PER_WORD, HARD_FIRST_PTS,
    touch_activity, idle_seconds,
)
from keyboards import (
    start_kb, theme_kb, game_action_kb, hard_action_kb, leaderboard_kb, globalboard_kb,
    back_kb, next_round_kb, final_round_kb, round_over_no_next_kb,
    word_found_kb, round_mode_kb, me_kb,
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

# ── Per-chat state for leaderboard next-round persistence ─────────
# Stores (next_round, theme_key) after a completed round, cleared on new game
_pending_next: dict[int, tuple] = {}

# ── Per-chat end-round lock — prevents double "round over" messages ─
# when two players find the last word at the exact same instant.
_ending_round: set[int] = set()


# ── Helpers ───────────────────────────────────────────────────────

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
                await q.message.chat.send_message(text, parse_mode=parse_mode, reply_markup=reply_markup)
            except TelegramError:
                pass
        elif "message is not modified" in err:
            pass
        else:
            log.warning(f"edit_message_text failed: {e}")


async def _delete_messages_later(bot, chat_id: int, msg_ids: list, delay: int):
    """Wait delay seconds then silently delete all listed message IDs."""
    if not msg_ids or delay <= 0:
        return
    await asyncio.sleep(delay)
    for mid in msg_ids:
        try:
            await bot.delete_message(chat_id, mid)
        except TelegramError:
            pass
        await asyncio.sleep(0.05)


def _build_hint_text(session) -> str:
    """Build the full hint message for all unfound words, filling in found ones."""
    lines = []
    for w in session.words:
        if w in session.found_words:
            lines.append(f"✅ <b>{w}</b> — found!")
        else:
            lines.append(hint_text(session.get_hint(w), len(w)))
    return "\n\n".join(lines)


# ── Core round logic ──────────────────────────────────────────────

async def _end_round(chat_id, session, ctx, from_timer=False):
    # ── Race-condition guard: only one coroutine may end this round ──
    if chat_id in _ending_round:
        return
    _ending_round.add(chat_id)

    try:
        if not session.active:
            return
        session.active = False

        summary        = session.summary()
        missed         = [w for w in session.words if w not in session.found_words]
        is_final       = session.round_num >= MAX_ROUNDS
        round_complete = session.complete()

        for row in summary:
            await db.add_score(chat_id, row["user_id"], row["name"], row["score"], row["words"])

        next_theme     = (
            pick_next_round_theme(chat_id, session.theme, THEME_LIST)
            if not is_final else session.theme
        )
        next_round_num = session.round_num + 1

        text = round_end(
            summary, missed, THEMES[session.theme]["name"],
            session.round_num, MAX_ROUNDS,
            round_complete=round_complete,
        )

        # ── Choose keyboard ──────────────────────────────────────────
        # Manual mode: show "▶️ Start Round N" button
        # Auto mode: no next-round button, auto-starts after countdown
        is_manual = getattr(session, 'round_mode', 'auto') == 'manual'
        is_hard   = getattr(session, 'is_hard', False)

        if is_final:
            kb = final_round_kb()
            _pending_next.pop(chat_id, None)
        elif round_complete and is_manual:
            kb = next_round_kb(next_round_num, next_theme, is_hard=is_hard)
            _pending_next[chat_id] = (next_round_num, next_theme, is_hard)
        else:
            kb = round_over_no_next_kb()
            if round_complete:
                _pending_next[chat_id] = (next_round_num, next_theme, is_hard)
            else:
                _pending_next.pop(chat_id, None)

        all_msg_ids = []
        if session.grid_msg_id:
            all_msg_ids.append(session.grid_msg_id)
        all_msg_ids.extend(session.msg_ids)

        try:
            await ctx.bot.send_message(chat_id, text, parse_mode=ParseMode.HTML, reply_markup=kb)
        except TelegramError:
            pass

        touch_activity(chat_id)
        sessions.remove(chat_id)

        if all_msg_ids and MSG_DELETE_AFTER > 0:
            asyncio.create_task(
                _delete_messages_later(ctx.bot, chat_id, all_msg_ids, MSG_DELETE_AFTER)
            )

        # ── Auto-start next round after 10-second countdown (auto mode only) ──
        if round_complete and not is_final and not is_manual:
            asyncio.create_task(
                _auto_next_round(chat_id, next_round_num, next_theme, ctx, is_hard=is_hard)
            )
    finally:
        _ending_round.discard(chat_id)


async def _auto_next_round(chat_id: int, next_round: int, theme_key: str, ctx,
                           is_hard: bool = False):
    """
    Send an animated digital-clock GIF countdown (10→1) as a single
    Telegram animation message, then auto-launch the next round.
    The GIF itself animates — no message editing needed.
    """
    theme_emoji = THEMES.get(theme_key, {}).get("emoji", "🎮")
    theme_name  = THEMES.get(theme_key, {}).get("name", "")

    loop = asyncio.get_event_loop()
    try:
        gif_bytes = await loop.run_in_executor(None, build_countdown_gif)
    except Exception as e:
        log.error(f"build_countdown_gif failed: {e}")
        gif_bytes = None

    countdown_msg = None
    if gif_bytes:
        try:
            countdown_msg = await ctx.bot.send_animation(
                chat_id,
                animation=io.BytesIO(gif_bytes),
                caption=f"🎮 <b>Round {next_round}</b>  ·  {theme_emoji} {theme_name}\n<i>Next round starting…</i>",
                parse_mode=ParseMode.HTML,
                width=400,
                height=160,
            )
        except TelegramError as e:
            log.warning(f"send_animation failed: {e}")
            countdown_msg = None

    # If GIF failed, fall back to a plain text countdown
    if not countdown_msg:
        try:
            countdown_msg = await ctx.bot.send_message(
                chat_id,
                f"⏱ <b>Round {next_round}</b> starts in <b>10s</b>…",
                parse_mode=ParseMode.HTML,
            )
        except TelegramError:
            pass

    # Wait for the GIF to finish playing (10 s × 1 s/frame)
    await asyncio.sleep(10)

    # Abort if a game started manually during the countdown
    if sessions.active(chat_id):
        if countdown_msg:
            try:
                await ctx.bot.delete_message(chat_id, countdown_msg.message_id)
            except TelegramError:
                pass
        return

    if countdown_msg:
        try:
            await ctx.bot.delete_message(chat_id, countdown_msg.message_id)
        except TelegramError:
            pass

    if sessions.active(chat_id) or sessions.cooldown(chat_id):
        return

    if is_hard:
        await _launch_hard(chat_id, ctx=ctx, round_mode="auto")
    else:
        await _launch(chat_id, theme_key, round_num=next_round, ctx=ctx, round_mode="auto")


async def _timer_task(chat_id, session, ctx):
    warn_after = session.duration - 15
    if warn_after > 0:
        await asyncio.sleep(warn_after)
        if not session.active:
            return
        try:
            warn_msg = await ctx.bot.send_message(
                chat_id,
                f"{ICO_FIRE()} <b>15 seconds left!</b> Find more words fast!",
                parse_mode=ParseMode.HTML,
            )
            session.msg_ids.append(warn_msg.message_id)
        except TelegramError:
            pass
        await asyncio.sleep(15)
    else:
        await asyncio.sleep(session.duration)
    if session.active:
        await _end_round(chat_id, session, ctx, from_timer=True)


async def _launch(chat_id, theme_key, round_num, ctx, round_mode: str = "auto"):
    duration, n_words, grid_size = get_level(round_num)
    t = THEMES[theme_key]

    loop = asyncio.get_event_loop()
    try:
        grid, words, placed = await loop.run_in_executor(
            None, build_puzzle, theme_key, grid_size, n_words
        )
    except Exception as e:
        log.error(f"_launch build_puzzle failed chat={chat_id} theme={theme_key}: {e}")
        try:
            await ctx.bot.send_message(
                chat_id,
                "⚠️ Couldn't generate puzzle. Please try /newgame again!",
                parse_mode=ParseMode.HTML,
            )
        except TelegramError:
            pass
        return

    try:
        img = await loop.run_in_executor(
            None, render_image, theme_key, grid, placed, [], round_num, grid_size
        )
    except Exception as e:
        log.error(f"_launch render_image failed chat={chat_id}: {e}")
        try:
            await ctx.bot.send_message(
                chat_id,
                "⚠️ Couldn't render grid image. Please try /newgame again!",
                parse_mode=ParseMode.HTML,
            )
        except TelegramError:
            pass
        return

    session = GameSession(chat_id, theme_key, grid, words, placed, round_num, img,
                          round_mode=round_mode)
    sessions.put(session)
    touch_activity(chat_id)
    _pending_next.pop(chat_id, None)

    caption = game_start_caption(t["name"], t["emoji"], round_num, len(words), duration, grid_size,
                                 words=words, found_words=[])
    try:
        msg = await ctx.bot.send_photo(
            chat_id, photo=io.BytesIO(img),
            caption=caption, parse_mode=ParseMode.HTML,
            reply_markup=game_action_kb(),
        )
        session.grid_msg_id = msg.message_id
    except TelegramError as e:
        log.error(f"send_photo failed {chat_id}: {e}")
        sessions.remove(chat_id)
        return

    session._task = asyncio.create_task(_timer_task(chat_id, session, ctx))


# ── Commands ──────────────────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    await db.upsert_user(user)
    if chat.type == ChatType.PRIVATE:
        BANNER_URL = "https://ibb.co/JjJrTmBt"
        caption    = start_private(user.first_name)
        # Send as ONE message: image + caption + buttons (clean, compact, like screenshot 2).
        # Caption is kept under 1024 chars and has no box-drawing chars inside HTML tags.
        try:
            await update.message.reply_photo(
                photo=BANNER_URL,
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=start_kb(),
            )
        except TelegramError as e:
            log.warning(f"reply_photo failed in /start: {e} — falling back to text only")
            # Fallback: text + buttons without image
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
    await update.message.reply_text(help_text(), parse_mode=ParseMode.HTML, reply_markup=back_kb())


async def cmd_theme(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"{ICO_PUZZLE()} <b>Choose a theme:</b>", parse_mode=ParseMode.HTML, reply_markup=theme_kb()
    )


async def cmd_newgame(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    if chat.type == ChatType.PRIVATE:
        await update.message.reply_text(
            f"{ICO_PUZZLE()} Add me to a group to play!", parse_mode=ParseMode.HTML, reply_markup=start_kb()
        )
        return
    await db.upsert_user(user)
    await db.upsert_group(chat)
    if sessions.active(chat.id):
        await update.message.reply_text(f"{ICO_FIRE()} A game is already running!", parse_mode=ParseMode.HTML)
        return
    args      = ctx.args or []
    arg       = args[0].lower() if args else "random"
    theme_key = arg if arg in THEMES else pick_random_theme(chat.id, THEME_LIST)
    # Store chosen theme for when mode is selected
    ctx.chat_data["pending_theme"] = theme_key
    await update.message.reply_text(
        f"{ICO_ROCKET()} <b>Choose round progression mode:</b>\n\n"
        f"🚀 <b>Automatic</b> — next round starts automatically after 10s\n"
        f"🕹️ <b>Manual</b> — you press the button to start each round",
        parse_mode=ParseMode.HTML,
        reply_markup=round_mode_kb("normal"),
    )


async def _launch_hard(chat_id: int, ctx, round_mode: str = "auto") -> None:
    """Start a single /newhard session — 11x11 grid, 10-15 words, high pts."""
    from puzzle import render_image as _render_image, _place, _empty, _fill

    theme_key = pick_hard_theme(chat_id, THEME_LIST)
    t         = THEMES[theme_key]

    # Pick non-repeating word subset (3+ letters, 10-15 words)
    hard_words = pick_hard_words(
        chat_id, theme_key, t["words"],
        HARD_N_WORDS_MIN, HARD_N_WORDS_MAX,
    )

    loop = asyncio.get_event_loop()

    def _build():
        import random as _rand
        # Try up to 5 times to place at least HARD_N_WORDS_MIN words
        best_grid, best_chosen, best_placed = None, [], []
        for attempt in range(5):
            grid   = _empty(HARD_GRID_SIZE)
            placed = []
            chosen = []
            for w in _rand.sample(hard_words, len(hard_words)):
                cells = _place(grid, w, HARD_GRID_SIZE)
                if cells:
                    chosen.append(w)
                    placed.append({"word": w, "cells": cells})
            if len(chosen) > len(best_chosen):
                best_grid, best_chosen, best_placed = grid, chosen, placed
            if len(chosen) >= HARD_N_WORDS_MIN:
                break
        if not best_chosen:
            raise ValueError("Hard puzzle: couldn't place any words")
        _fill(best_grid, HARD_GRID_SIZE)
        return best_grid, best_chosen, best_placed

    try:
        grid, words, placed = await loop.run_in_executor(None, _build)
    except ValueError as e:
        log.error(f"_launch_hard: {e}")
        try:
            await ctx.bot.send_message(
                chat_id, "Could not generate hard puzzle. Try /newhard again!",
                parse_mode=ParseMode.HTML,
            )
        except TelegramError:
            pass
        return

    img = await loop.run_in_executor(
        None, _render_image, theme_key, grid, placed, [], 1, HARD_GRID_SIZE,
    )

    session = GameSession(chat_id, theme_key, grid, words, placed,
                          round_num=1, img_bytes=img, is_hard=True, round_mode=round_mode)
    sessions.put(session)
    touch_activity(chat_id)
    _pending_next.pop(chat_id, None)

    caption = game_start_caption(
        t["name"], t["emoji"], 1, len(words), session.duration, HARD_GRID_SIZE,
        words=words, found_words=[],
    )
    caption = "🔥 <b>HARD MODE</b> — " + caption[caption.index("<b>Round"):]

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


async def cmd_newhard(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Start a Hard Mode game — /newhard"""
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
    await update.message.reply_text(
        f"{ICO_FIRE()} <b>🔥 HARD MODE — Choose round progression:</b>\n\n"
        f"🚀 <b>Automatic</b> — next hard round starts automatically after 10s\n"
        f"🕹️ <b>Manual</b> — you press the button to start each hard round",
        parse_mode=ParseMode.HTML,
        reply_markup=round_mode_kb("hard"),
    )


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
        # Try to update existing hint message
        try:
            await ctx.bot.edit_message_text(
                chat_id=chat.id, message_id=session.hint_msg_id,
                text=hint_body, parse_mode=ParseMode.HTML,
            )
            return
        except TelegramError:
            pass  # fall through to send new one

    # Send fresh hint message
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
        pts   = session.register(word, user.id, name)
        left  = len(session.words) - len(session.found_words)
        combo = session.p_combos.get(user.id, 1)
        await db.upsert_user(user)

        loop    = asyncio.get_event_loop()
        new_img = await loop.run_in_executor(
            None, render_image, session.theme, session.grid, session.placed,
            session.found_words, session.round_num, session.grid_size,
        )
        session.img_bytes = new_img

        # FIX #2 — pass chat info so word_found_kb builds a real URL button
        # that Telegram scrolls straight to the grid message.
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

        # Update grid image caption (inline hints refresh + hard mode badge)
        if session.grid_msg_id:
            try:
                t           = THEMES[session.theme]
                new_caption = game_start_caption(
                    t["name"], t["emoji"], session.round_num,
                    len(session.words), session.duration, session.grid_size,
                    words=session.words, found_words=session.found_words,
                )
                if session.is_hard:
                    new_caption = f"🔥 <b>HARD MODE</b> — {new_caption[new_caption.index('<b>Round'):]}"
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
            # _end_round has its own lock so double-triggers are safe
            await _end_round(chat.id, session, ctx)

    elif session.already_found(word):
        session.reset_combo(user.id)
        reply = await msg.reply_text(f"❌ <code>{word}</code> was already found!", parse_mode=ParseMode.HTML)
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
    chat    = update.effective_chat
    rows    = await db.global_leaderboard()
    pending = _pending_next.get(chat.id)
    if pending and len(pending) == 3:
        nr, tk, ih = pending
    elif pending:
        nr, tk = pending; ih = False
    else:
        nr, tk, ih = 0, "", False
    kb = globalboard_kb(next_round=nr, theme_key=tk, is_hard=ih)
    await update.message.reply_text(
        leaderboard_text(rows, "🌍 Global Leaderboard"),
        parse_mode=ParseMode.HTML, reply_markup=kb,
    )


async def cmd_mystats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await db.upsert_user(user)
    doc = await db.user_global_stats(user.id)
    if not doc:
        await update.message.reply_text("You haven't played yet! Join a group and type /newgame.")
        return
    await update.message.reply_text(my_stats(user.first_name, doc), parse_mode=ParseMode.HTML)


async def cmd_me(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Send a beautiful profile card image for the user."""
    user = update.effective_user
    chat = update.effective_chat
    await db.upsert_user(user)

    global_doc = await db.user_global_stats(user.id)
    if not global_doc:
        await update.message.reply_text(
            f"👤 <b>{user.first_name}</b>, you haven't played yet!\n"
            "Join a group and type /newgame to start building your profile.",
            parse_mode=ParseMode.HTML,
        )
        return

    # Global rank
    all_rows    = await db.global_leaderboard(limit=500)
    global_rank = next((i+1 for i,r in enumerate(all_rows) if r.get("user_id") == user.id), 0) or len(all_rows)+1

    words_found   = global_doc.get("words_found", 0)
    score         = global_doc.get("score", 0)
    rounds_won    = global_doc.get("rounds_won", 0)
    rounds_played = global_doc.get("rounds_played", 0)
    streak_days   = global_doc.get("streak_days", 0)

    # Group stats (only if called from a group)
    in_group     = chat.type in (ChatType.GROUP, ChatType.SUPERGROUP)
    group_score  = 0; group_rank_pos = 0; group_words = 0; group_rounds_won = 0
    if in_group:
        grp_rows   = await db.group_leaderboard(chat.id, limit=200)
        grp_me     = next((r for r in grp_rows if r.get("user_id") == user.id), None)
        group_rank_pos = next((i+1 for i,r in enumerate(grp_rows) if r.get("user_id") == user.id), 0)
        if grp_me:
            group_score = grp_me.get("score", 0)
            group_words = grp_me.get("words_found", 0)
            group_rounds_won = grp_me.get("rounds_won", 0)

    # Fetch profile photo
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
    img  = await loop.run_in_executor(None, render_me_card,
        user.first_name, user.id,
        words_found, score, global_rank,
        rounds_won, rounds_played, streak_days,
        group_score, group_rank_pos,
        chat.title if in_group else "",
        group_words, group_rounds_won,
        avatar_bytes,
        in_group,
    )

    await update.message.reply_photo(
        photo=io.BytesIO(img),
        caption=f"👤 <b>{user.first_name}'s</b> WordGrid Profile",
        parse_mode=ParseMode.HTML,
        reply_markup=me_kb(in_group=in_group),
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
    await update.message.reply_text(f"{ICO_TROPHY()} Group leaderboard reset.", parse_mode=ParseMode.HTML)


async def cmd_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    data = await db.bot_stats()
    await update.message.reply_text(bot_stats(data["users"], data["groups"]), parse_mode=ParseMode.HTML)


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
    prog  = await update.message.reply_text(f"📢 Broadcasting to <b>{total}</b> targets…", parse_mode=ParseMode.HTML)
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


# ── Idle nudge job ────────────────────────────────────────────────

async def idle_nudge_job(ctx: ContextTypes.DEFAULT_TYPE):
    """Runs on schedule. Nudges groups idle for IDLE_NUDGE_AFTER seconds."""
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


# ── Callbacks ─────────────────────────────────────────────────────

async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q    = update.callback_query
    data = q.data
    chat = update.effective_chat
    user = update.effective_user
    await q.answer()

    if data == "cb:start":
        await _safe_edit_text(q, start_private(user.first_name), reply_markup=start_kb())

    elif data.startswith("startmode:"):
        # startmode:{game_type}:{mode}  e.g. startmode:normal:auto
        parts = data.split(":")
        if len(parts) != 3:
            await q.answer("Invalid selection.", show_alert=True)
            return
        game_type  = parts[1]   # "normal" or "hard"
        round_mode = parts[2]   # "auto" or "manual"
        if chat.type == ChatType.PRIVATE:
            await q.answer("Add me to a group to play!", show_alert=True)
            return
        if sessions.active(chat.id):
            await q.answer("A game is already running!", show_alert=True)
            return
        await db.upsert_group(chat)
        mode_label = "🚀 Automatic" if round_mode == "auto" else "🕹️ Manual"
        await q.answer(f"{mode_label} mode selected!")
        try:
            await q.delete_message()
        except TelegramError:
            pass
        if game_type == "hard":
            await _launch_hard(chat.id, ctx=ctx, round_mode=round_mode)
        else:
            theme_key = ctx.chat_data.get("pending_theme") or pick_random_theme(chat.id, THEME_LIST)
            ctx.chat_data.pop("pending_theme", None)
            await _launch(chat.id, theme_key, round_num=1, ctx=ctx, round_mode=round_mode)

    elif data == "cb:help":
        await _safe_edit_text(q, help_text(), reply_markup=back_kb())

    elif data == "cb:me_group":
        # Show group-specific profile card
        user = update.effective_user
        if chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
            await q.answer("This only works in groups!", show_alert=True)
            return
        global_doc = await db.user_global_stats(user.id)
        if not global_doc:
            await q.answer("No stats yet — play first!", show_alert=True)
            return
        all_rows    = await db.global_leaderboard(limit=500)
        global_rank = next((i+1 for i,r in enumerate(all_rows) if r.get("user_id") == user.id), len(all_rows)+1)
        grp_rows    = await db.group_leaderboard(chat.id, limit=200)
        grp_me      = next((r for r in grp_rows if r.get("user_id") == user.id), {})
        group_rank_pos = next((i+1 for i,r in enumerate(grp_rows) if r.get("user_id") == user.id), 0)
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
        img  = await loop.run_in_executor(None, render_me_card,
            user.first_name, user.id,
            global_doc.get("words_found", 0), global_doc.get("score", 0), global_rank,
            global_doc.get("rounds_won", 0), global_doc.get("rounds_played", 0),
            global_doc.get("streak_days", 0),
            grp_me.get("score", 0), group_rank_pos,
            chat.title or "",
            grp_me.get("words_found", 0), grp_me.get("rounds_won", 0),
            avatar_bytes, True,
        )
        await q.answer()
        try:
            await q.delete_message()
        except TelegramError:
            pass
        await ctx.bot.send_photo(
            chat.id, photo=io.BytesIO(img),
            caption=f"👤 <b>{user.first_name}'s</b> Chat Profile — {chat.title}",
            parse_mode=ParseMode.HTML,
            reply_markup=me_kb(in_group=True),
        )

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
        kb   = globalboard_kb()
        await _safe_edit_text(
            q, leaderboard_text(rows, "🌍 Global Leaderboard"),
            reply_markup=kb,
        )

    elif data.startswith("lb:"):
        # Format: lb:{scope}:{time_filter}  e.g. lb:chat:alltime, lb:global:week
        parts = data.split(":")
        scope  = parts[1] if len(parts) > 1 else "chat"   # "chat" or "global"
        tfilter = parts[2] if len(parts) > 2 else "alltime"  # "today","week","alltime"

        if scope == "global":
            rows  = await db.global_leaderboard(limit=15)
            title = "🌍 Global Leaderboard"
            kb    = globalboard_kb(time_filter=tfilter)
        else:
            rows  = await db.group_leaderboard(chat.id, limit=15)
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
        # Legacy fallback — new Go-to-Grid buttons are URL buttons and never
        # fire a callback. This only runs for old messages sent before the fix.
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

    elif data.startswith("nextround:"):
        parts = data.split(":")
        if len(parts) < 3:
            return
        theme_key  = parts[1]
        try:
            next_round = int(parts[2])
        except ValueError:
            return
        # parts[3] optionally carries "hard" or "normal"
        is_hard_next = (len(parts) >= 4 and parts[3] == "hard")
        if chat.type == ChatType.PRIVATE:
            await q.answer("Add me to a group to play!", show_alert=True)
            return
        if sessions.active(chat.id):
            await q.answer("A game is already running!", show_alert=True)
            return
        if theme_key not in THEMES:
            theme_key = pick_random_theme(chat.id, THEME_LIST)
        await db.upsert_group(chat)
        await q.answer(f"▶️ Starting Round {next_round}!")
        try:
            await q.delete_message()
        except TelegramError:
            pass
        if is_hard_next:
            await _launch_hard(chat.id, ctx=ctx, round_mode="manual")
        else:
            await _launch(chat.id, theme_key, round_num=next_round, ctx=ctx, round_mode="manual")

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
        # Store chosen theme and ask for round progression mode
        ctx.chat_data["pending_theme"] = key
        await _safe_edit_text(
            q,
            f"🎮 <b>{THEMES[key]['emoji']} {THEMES[key]['name']}</b> selected!\n\n"
            f"🚀 <b>Automatic</b> — next round starts automatically after 10s\n"
            f"🕹️ <b>Manual</b> — you press the button to start each round",
            reply_markup=round_mode_kb("normal"),
        )


# ── Global error handler ──────────────────────────────────────────
async def error_handler(update: object, ctx: ContextTypes.DEFAULT_TYPE):
    """Catches ALL unhandled exceptions — logs them, notifies user only for real errors."""
    err = ctx.error

    # Silently ignore common non-critical Telegram API errors
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
