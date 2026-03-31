"""
WordGrid Bot — Main entry point (polling mode)
Optimised for Heroku Standard-2X with 10 k+ groups.
"""

import asyncio
import logging
import sys

from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    ChatMemberHandler,
    CommandHandler,
    MessageHandler,
    filters,
)
from telegram.request import HTTPXRequest

import database as db
from config import BOT_TOKEN, IDLE_NUDGE_CHECK
from handlers import (
    cmd_hint,
    cmd_start, cmd_help, cmd_theme, cmd_newgame,
    cmd_leaderboard, cmd_globalboard, cmd_mystats,
    cmd_endgame, cmd_resetboard,
    cmd_broadcast, cmd_stats,
    on_message, on_callback, on_my_chat_member,
    idle_nudge_job,
)

# ── Logging ───────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
log = logging.getLogger("wordgrid")


def build_app() -> Application:
    updater_request = HTTPXRequest(
        connection_pool_size=8,
        read_timeout=35,
        write_timeout=30,
        connect_timeout=30,
        pool_timeout=30,
    )
    bot_request = HTTPXRequest(
        connection_pool_size=16,
        read_timeout=30,
        write_timeout=30,
        connect_timeout=30,
        pool_timeout=30,
    )

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .request(bot_request)
        .get_updates_request(updater_request)
        .concurrent_updates(True)
        .build()
    )

    # ── Commands ──
    app.add_handler(CommandHandler("start",       cmd_start))
    app.add_handler(CommandHandler("help",        cmd_help))
    app.add_handler(CommandHandler("theme",       cmd_theme))
    app.add_handler(CommandHandler("newgame",     cmd_newgame))
    app.add_handler(CommandHandler("leaderboard", cmd_leaderboard))
    app.add_handler(CommandHandler("globalboard", cmd_globalboard))
    app.add_handler(CommandHandler("mystats",     cmd_mystats))
    app.add_handler(CommandHandler("hint",        cmd_hint))
    app.add_handler(CommandHandler("endgame",     cmd_endgame))
    app.add_handler(CommandHandler("skip",        cmd_endgame))
    app.add_handler(CommandHandler("resetboard",  cmd_resetboard))
    app.add_handler(CommandHandler("broadcast",   cmd_broadcast))
    app.add_handler(CommandHandler("stats",       cmd_stats))

    # ── Inline buttons ──
    app.add_handler(CallbackQueryHandler(on_callback))

    # ── Bot added/removed from group ──
    app.add_handler(
        ChatMemberHandler(on_my_chat_member, ChatMemberHandler.MY_CHAT_MEMBER)
    )

    # ── Word guesses in groups ──
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS,
            on_message,
        )
    )

    return app


async def post_init(app: Application):
    await db.connect()
    me = await app.bot.get_me()
    log.info(f"✅ Bot started as @{me.username}")

    # Schedule idle nudge job — checks every IDLE_NUDGE_CHECK seconds
    if app.job_queue is not None:
        app.job_queue.run_repeating(
            idle_nudge_job,
            interval=IDLE_NUDGE_CHECK,
            first=IDLE_NUDGE_CHECK,
            name="idle_nudge",
        )
        log.info(f"⏰ Idle nudge job scheduled every {IDLE_NUDGE_CHECK}s")
    else:
        log.warning("JobQueue not available — idle nudge disabled. Install: pip install 'python-telegram-bot[job-queue]'")


async def post_shutdown(app: Application):
    await db.disconnect()
    log.info("Bot shut down.")


def main():
    if not BOT_TOKEN:
        log.critical("BOT_TOKEN is missing — set it in .env or Heroku config vars!")
        sys.exit(1)

    app = build_app()
    app.post_init     = post_init
    app.post_shutdown = post_shutdown

    log.info("Starting polling…")
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES,
        poll_interval=0,
        timeout=30,
    )


if __name__ == "__main__":
    main()
