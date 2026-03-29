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

import database as db
from config import BOT_TOKEN
from handlers import (
    cmd_start, cmd_help, cmd_theme, cmd_newgame,
    cmd_leaderboard, cmd_globalboard, cmd_mystats,
    cmd_endgame, cmd_resetboard,
    cmd_broadcast, cmd_stats,
    on_message, on_callback, on_my_chat_member,
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
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)        # handle multiple groups in parallel
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .pool_timeout(30)
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
    app.add_handler(CommandHandler("endgame",     cmd_endgame))
    app.add_handler(CommandHandler("skip",        cmd_endgame))
    app.add_handler(CommandHandler("resetboard",  cmd_resetboard))
    app.add_handler(CommandHandler("broadcast",   cmd_broadcast))
    app.add_handler(CommandHandler("stats",       cmd_stats))

    # ── Inline buttons ──
    app.add_handler(CallbackQueryHandler(on_callback))

    # ── Bot added/removed from group ──
    app.add_handler(
        ChatMemberHandler(on_my_chat_member,
                          ChatMemberHandler.MY_CHAT_MEMBER)
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
        poll_interval=0,          # fastest possible polling
        timeout=20,
    )


if __name__ == "__main__":
    main()
