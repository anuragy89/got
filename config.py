import os
from dotenv import load_dotenv

load_dotenv()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BOT CREDENTIALS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BOT_TOKEN    = os.getenv("BOT_TOKEN", "")
BOT_USERNAME = os.getenv("BOT_USERNAME", "WordGridBot")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  OWNER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MONGODB
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME   = os.getenv("DB_NAME", "wordgrid_bot")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  LINKS  (edit these)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
UPDATES_CHANNEL = os.getenv("UPDATES_CHANNEL", "https://t.me/YourChannel")
SUPPORT_GROUP   = os.getenv("SUPPORT_GROUP",   "https://t.me/YourSupport")
BOT_INVITE_LINK = os.getenv(
    "BOT_INVITE_LINK",
    f"https://t.me/{os.getenv('BOT_USERNAME','WordGridBot')}?startgroup=true"
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PREMIUM EMOJI IDs
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USE_PREMIUM_EMOJI = os.getenv("USE_PREMIUM_EMOJI", "false").lower() == "true"

PEMOJI_TROPHY    = os.getenv("PEMOJI_TROPHY",    "5188344996356448758")
PEMOJI_FIRE      = os.getenv("PEMOJI_FIRE",      "5424972470023104089")
PEMOJI_STAR      = os.getenv("PEMOJI_STAR",      "5411411879585129198")
PEMOJI_CROWN     = os.getenv("PEMOJI_CROWN",     "5418167785832328381")
PEMOJI_DIAMOND   = os.getenv("PEMOJI_DIAMOND",   "5465283645788937267")
PEMOJI_LIGHTNING = os.getenv("PEMOJI_LIGHTNING", "6316383393185533398")
PEMOJI_PUZZLE    = os.getenv("PEMOJI_PUZZLE",    "5429368540849260641")
PEMOJI_ROCKET    = os.getenv("PEMOJI_ROCKET",    "5188481279963715781")
PEMOJI_JOYSTICK  = os.getenv("PEMOJI_JOYSTICK",  "5361741454685256344")
PEMOJI_MEDAL     = os.getenv("PEMOJI_MEDAL",     "5440539497383087970")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GAME SETTINGS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ROUND_DURATION   = int(os.getenv("ROUND_DURATION",   "90"))
GRID_SIZE        = int(os.getenv("GRID_SIZE",        "10"))
WORDS_PER_ROUND  = int(os.getenv("WORDS_PER_ROUND",  "8"))
COOLDOWN_SECONDS = int(os.getenv("COOLDOWN_SECONDS", "30"))

POINTS_PER_LETTER  = int(os.getenv("POINTS_PER_LETTER",  "10"))
FIRST_FINDER_BONUS = int(os.getenv("FIRST_FINDER_BONUS", "25"))
COMBO_MULTIPLIERS  = {1: 1.0, 2: 1.5, 3: 2.0, 4: 2.5, 5: 3.0}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MESSAGE CLEANUP
#  Seconds after round ends before all in-round
#  messages (grid image, word finds, hints,
#  warnings) are auto-deleted.
#  Default: 300 (5 minutes). Set 0 to disable.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MSG_DELETE_AFTER = int(os.getenv("MSG_DELETE_AFTER", "300"))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  IDLE NUDGE SETTINGS
#  IDLE_NUDGE_AFTER — seconds of no game before
#                     bot sends an engaging msg.
#                     Default: 10800 (3 hours)
#  IDLE_NUDGE_CHECK — how often (seconds) bot
#                     checks for idle groups.
#                     Default: 1800 (30 min)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IDLE_NUDGE_AFTER = int(os.getenv("IDLE_NUDGE_AFTER", "10800"))
IDLE_NUDGE_CHECK = int(os.getenv("IDLE_NUDGE_CHECK", "1800"))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PERFORMANCE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BROADCAST_DELAY = float(os.getenv("BROADCAST_DELAY", "0.05"))
