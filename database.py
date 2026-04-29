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
    await db.users.create_index("user_id", unique=True)
    await db.groups.create_index("chat_id", unique=True)
    await db.global_lb.create_index("user_id", unique=True)
    await db.scores.create_index([("timestamp", 1)]) # For Today/Week
    await db.scores.create_index([("chat_id", 1), ("timestamp", 1)])

async def upsert_user(user):
    await db.users.update_one(
        {"user_id": user.id},
        {"$set": {"username": user.username, "first_name": user.first_name},
         "$setOnInsert": {"user_id": user.id, "joined": datetime.now(timezone.utc), "blocked": False}},
        upsert=True
    )

async def upsert_group(chat):
    await db.groups.update_one(
        {"chat_id": chat.id},
        {"$set": {"title": chat.title, "username": getattr(chat, "username", None), "active": True},
         "$setOnInsert": {"chat_id": chat.id, "joined": datetime.now(timezone.utc), "activity": [0]*7}},
        upsert=True
    )

async def add_score(chat_id: int, user_id: int, name: str, pts: int, words: int, username: str = None):
    now = datetime.now(timezone.utc)
    # Sunday=0, Monday=1... Saturday=6
    weekday = (now.weekday() + 1) % 7 

    # 1. Individual score record (for Today/Week filtering)
    await db.scores.insert_one({
        "chat_id": chat_id, "user_id": user_id, "name": name,
        "pts": pts, "words": words, "timestamp": now
    })

    # 2. Update Group Activity & Total (For Group vs Group Virality)
    await db.groups.update_one(
        {"chat_id": chat_id},
        {"$inc": {f"activity.{weekday}": pts, "total_score": pts}}
    )

    # 3. Update Global All-Time & Activity
    await db.global_lb.update_one(
        {"user_id": user_id},
        {"$inc": {"score": pts, "words_found": words, f"activity.{weekday}": pts},
         "$set": {"name": name, "username": username}},
        upsert=True
    )

async def get_leaderboard(chat_id=None, time_filter="alltime", limit=10):
    if time_filter == "alltime":
        coll = db.leaderboard if chat_id else db.global_lb
        query = {"chat_id": chat_id} if chat_id else {}
        cur = coll.find(query).sort("score", -1).limit(limit)
        return [d async for d in cur]
    
    # Filter for Today or Week
    now = datetime.now(timezone.utc)
    if time_filter == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    else: # week
        start_date = now - timedelta(days=7)

    match = {"timestamp": {"$gte": start_date}}
    if chat_id: match["chat_id"] = chat_id

    pipeline = [
        {"$match": match},
        {"$group": {"_id": "$user_id", "name": {"$first": "$name"}, "score": {"$sum": "$pts"}, "words_found": {"$sum": "$words"}}},
        {"$sort": {"score": -1}}, {"$limit": limit}
    ]
    cur = db.scores.aggregate(pipeline)
    return [d async for d in cur]

async def get_top_groups(limit=10):
    cur = db.groups.find({"active": True}).sort("total_score", -1).limit(limit)
    return [d async for d in cur]

async def get_activity(chat_id=None):
    coll = db.groups if chat_id else db.global_lb # Using global stats as fallback
    doc = await coll.find_one({"chat_id": chat_id} if chat_id else {})
    return doc.get("activity", [0]*7) if doc else [0]*7

async def all_group_ids():
    cur = db.groups.find({"active": True}, {"chat_id": 1})
    return [d["chat_id"] async for d in cur]

async def bot_stats():
    return {"users": await db.users.count_documents({}), "groups": await db.groups.count_documents({"active": True})}
