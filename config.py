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
#  Step 1: Set USE_PREMIUM_EMOJI=true
#  Step 2: Get IDs by sending custom emoji to
#          @getidsbot — copy custom_emoji_id
#  Step 3: Paste each ID below or in .env
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USE_PREMIUM_EMOJI = os.getenv("USE_PREMIUM_EMOJI", "false").lower() == "true"

PEMOJI_TROPHY    = os.getenv("PEMOJI_TROPHY",    "5368324170671202286")
PEMOJI_FIRE      = os.getenv("PEMOJI_FIRE",      "5368324170671202286")
PEMOJI_STAR      = os.getenv("PEMOJI_STAR",      "5368324170671202286")
PEMOJI_CROWN     = os.getenv("PEMOJI_CROWN",     "5368324170671202286")
PEMOJI_DIAMOND   = os.getenv("PEMOJI_DIAMOND",   "5368324170671202286")
PEMOJI_LIGHTNING = os.getenv("PEMOJI_LIGHTNING", "5368324170671202286")
PEMOJI_PUZZLE    = os.getenv("PEMOJI_PUZZLE",    "5368324170671202286")
PEMOJI_ROCKET    = os.getenv("PEMOJI_ROCKET",    "5368324170671202286")
PEMOJI_JOYSTICK  = os.getenv("PEMOJI_JOYSTICK",  "5368324170671202286")
PEMOJI_MEDAL     = os.getenv("PEMOJI_MEDAL",     "5368324170671202286")

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
#  PERFORMANCE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BROADCAST_DELAY = float(os.getenv("BROADCAST_DELAY", "0.05"))
