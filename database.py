from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
from config import MONGO_URI, DB_NAME
import logging

log = logging.getLogger(__name__)

_client: AsyncIOMotorClient = None
db = None


async def connect():
    global _client, db
    _client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=8000)
    db = _client[DB_NAME]
    await _indexes()
    log.info("✅ MongoDB connected")


async def disconnect():
    if _client:
        _client.close()


async def _indexes():
    await db.users.create_index("user_id",  unique=True)
    await db.groups.create_index("chat_id", unique=True)
    await db.leaderboard.create_index(
        [("chat_id", 1), ("score", -1)]
    )
    await db.global_lb.create_index("user_id", unique=True)
    await db.global_lb.create_index([("score", -1)])
    # score_events: one doc per word-found event, used for today/week filtering
    await db.score_events.create_index([("chat_id", 1), ("ts", -1)])
    await db.score_events.create_index([("ts", -1)])


# ── Users ────────────────────────────────────────────────────────

async def upsert_user(user):
    await db.users.update_one(
        {"user_id": user.id},
        {
            "$set": {
                "username":   user.username,
                "first_name": user.first_name,
            },
            "$setOnInsert": {
                "user_id": user.id,
                "joined":  datetime.now(timezone.utc),
                "blocked": False,
            },
        },
        upsert=True,
    )


async def mark_blocked(uid: int, blocked: bool):
    await db.users.update_one(
        {"user_id": uid}, {"$set": {"blocked": blocked}}
    )


async def all_user_ids() -> list:
    cur = db.users.find({"blocked": {"$ne": True}}, {"user_id": 1})
    return [d["user_id"] async for d in cur]


async def count_users() -> int:
    return await db.users.count_documents({})


# ── Groups ───────────────────────────────────────────────────────

async def upsert_group(chat):
    await db.groups.update_one(
        {"chat_id": chat.id},
        {
            "$set": {
                "title":    chat.title,
                "username": getattr(chat, "username", None),
                "active":   True,
            },
            "$setOnInsert": {
                "chat_id": chat.id,
                "joined":  datetime.now(timezone.utc),
            },
        },
        upsert=True,
    )


async def mark_group_inactive(chat_id: int):
    await db.groups.update_one(
        {"chat_id": chat_id}, {"$set": {"active": False}}
    )


async def all_group_ids() -> list:
    cur = db.groups.find({"active": True}, {"chat_id": 1})
    return [d["chat_id"] async for d in cur]


async def count_groups() -> int:
    return await db.groups.count_documents({"active": True})


# ── Time-filter helper ───────────────────────────────────────────

def _time_match(time_filter: str) -> dict:
    """Return a MongoDB match fragment for today/week/alltime."""
    now = datetime.now(timezone.utc)
    if time_filter == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return {"ts": {"$gte": start}}
    if time_filter == "week":
        # Monday 00:00 UTC of the current ISO week
        start = (now - timedelta(days=now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        return {"ts": {"$gte": start}}
    return {}   # alltime — no filter


# ── Leaderboard ──────────────────────────────────────────────────

async def add_score(chat_id: int, user_id: int, name: str, pts: int, words: int = 1,
                    username: str = None):
    # Group board (cumulative all-time)
    await db.leaderboard.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {
            "$inc": {"score": pts, "words_found": words},
            "$set": {"name": name},
            "$setOnInsert": {"chat_id": chat_id, "user_id": user_id},
        },
        upsert=True,
    )
    # Global board — store username for clickable leaderboard mentions
    global_set = {"name": name}
    if username:
        global_set["username"] = username
    await db.global_lb.update_one(
        {"user_id": user_id},
        {
            "$inc": {"score": pts, "words_found": words},
            "$set": global_set,
            "$setOnInsert": {"user_id": user_id},
        },
        upsert=True,
    )
    # score_events — timestamped record for today/week filtering
    event: dict = {
        "chat_id":  chat_id,
        "user_id":  user_id,
        "name":     name,
        "pts":      pts,
        "words":    words,
        "ts":       datetime.now(timezone.utc),
    }
    if username:
        event["username"] = username
    await db.score_events.insert_one(event)


async def group_leaderboard(chat_id: int, limit: int = 10,
                            time_filter: str = "alltime") -> list:
    if time_filter == "alltime":
        cur = db.leaderboard.find({"chat_id": chat_id}).sort("score", -1).limit(limit)
        return [d async for d in cur]

    match_q = {"chat_id": chat_id, **_time_match(time_filter)}
    pipeline = [
        {"$match": match_q},
        {"$group": {
            "_id":         "$user_id",
            "name":        {"$last": "$name"},
            "score":       {"$sum": "$pts"},
            "words_found": {"$sum": "$words"},
        }},
        {"$sort": {"score": -1}},
        {"$limit": limit},
    ]
    rows = []
    async for d in db.score_events.aggregate(pipeline):
        rows.append({
            "user_id":     d["_id"],
            "name":        d["name"],
            "score":       d["score"],
            "words_found": d["words_found"],
        })
    return rows


async def global_leaderboard(limit: int = 10,
                              time_filter: str = "alltime") -> list:
    if time_filter == "alltime":
        cur = db.global_lb.find().sort("score", -1).limit(limit)
        return [d async for d in cur]

    pipeline = [
        {"$match": _time_match(time_filter)},
        {"$group": {
            "_id":         "$user_id",
            "name":        {"$last": "$name"},
            "username":    {"$last": "$username"},
            "score":       {"$sum": "$pts"},
            "words_found": {"$sum": "$words"},
        }},
        {"$sort": {"score": -1}},
        {"$limit": limit},
    ]
    rows = []
    async for d in db.score_events.aggregate(pipeline):
        rows.append({
            "user_id":     d["_id"],
            "name":        d["name"],
            "username":    d.get("username"),
            "score":       d["score"],
            "words_found": d["words_found"],
        })
    return rows


async def user_global_stats(user_id: int) -> dict:
    return await db.global_lb.find_one({"user_id": user_id}) or {}


async def reset_group_board(chat_id: int):
    await db.leaderboard.delete_many({"chat_id": chat_id})


# ── Bot stats ────────────────────────────────────────────────────

async def bot_stats() -> dict:
    return {
        "users":  await count_users(),
        "groups": await count_groups(),
    }
