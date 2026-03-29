# 🧩 WordGrid Bot

A viral Telegram **Word Grid Puzzle Game Bot** — themed grid images, live leaderboards, combo scoring, built for 10,000+ groups.

---

## Features

- 🎨 **8 visual themes** — Animals, Fruits, Ocean, Space, Sports, Countries, Food, Bollywood
- 🖼️ **Canvas-rendered grid images** — beautiful coloured PNG sent to each group
- ⚡ **Combo multiplier system** — consecutive finds = 1.5× → 2× → 2.5× → 3×
- 🏆 **Per-group + global leaderboard** stored in MongoDB
- 📢 **Owner broadcast** — send HTML messages to all users/groups
- 💎 **Premium emoji support** — configurable IDs in `.env`
- 🚀 **Heroku Standard-2X ready** — async, concurrent updates, executor for CPU tasks

---

## Deploy to Heroku

## 🚀 Quick Deploy to Heroku

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/anuragy89/got)

**Manual steps:**

### 1. Clone & push
```bash
git clone https://github.com/yourname/wordgrid-bot
cd wordgrid-bot
heroku create your-app-name
git push heroku main
```

### 2. Set config vars
```bash
heroku config:set BOT_TOKEN=your_token
heroku config:set BOT_USERNAME=YourBotUsername
heroku config:set OWNER_ID=123456789
heroku config:set MONGO_URI="mongodb+srv://..."
```

### 3. Scale worker dyno
```bash
heroku ps:scale worker=1:standard-2x
```

### 4. View logs
```bash
heroku logs --tail
```

---

## Local development

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your values
python bot.py
```

---

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message with buttons |
| `/newgame` | Start a round (random theme) |
| `/newgame [theme]` | Start with specific theme |
| `/theme` | Browse themes with inline buttons |
| `/leaderboard` | Group top 10 |
| `/globalboard` | All-time global top 10 |
| `/mystats` | Your personal stats |
| `/endgame` | End round early (admins) |
| `/resetboard` | Reset group leaderboard (admins) |
| `/broadcast all <msg>` | Broadcast to everyone (owner) |
| `/broadcast users <msg>` | Users only (owner) |
| `/broadcast groups <msg>` | Groups only (owner) |
| `/stats` | Bot stats — users & groups (owner) |

---

## Premium Emoji Setup

1. Set `USE_PREMIUM_EMOJI=true` in `.env` / Heroku config
2. Send a custom emoji in Telegram
3. Forward it to [@getidsbot](https://t.me/getidsbot)
4. Copy the `custom_emoji_id` value
5. Paste it into the matching `PEMOJI_*` variable

---

## Scoring

- Base = `word_length × POINTS_PER_LETTER` (default 10)
- First word of round = +25 bonus
- Combo multipliers:
  - 2 correct in a row → ×1.5
  - 3 → ×2.0 | 4 → ×2.5 | 5+ → ×3.0
  - Wrong guess resets combo

---

## Architecture

```
bot.py          Main entry — registers handlers, polling
config.py       All settings via env vars
database.py     Async MongoDB via Motor
puzzle.py       Grid generation + Pillow image renderer
game.py         In-memory session manager per group
handlers.py     All Telegram command/callback handlers
strings.py      All message templates + premium emoji helpers
keyboards.py    All InlineKeyboardMarkup builders
```
