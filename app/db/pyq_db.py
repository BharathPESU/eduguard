"""
MongoDB operations for PYQ Practice.

Collections:
  pyq_sessions — one doc per uploaded paper; stores session metadata + all questions
  pyq_answers  — one doc per (session_id, question_number); the answer cache

Key behaviour:
  - Sessions are upserted on upload (disk JSON + MongoDB, both written).
  - Questions are read FROM MongoDB (disk is only an emergency backup).
  - Answers are written on first AI generation; subsequent requests return
    the cached doc immediately — zero tokens consumed.
"""
from datetime import datetime, UTC
from pathlib import Path
import json

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

_client = AsyncIOMotorClient(settings.MONGO_URI)
_db = _client[settings.DB_NAME]

pyq_sessions_col = _db["pyq_sessions"]
pyq_answers_col  = _db["pyq_answers"]


# ── Startup ───────────────────────────────────────────────

async def ensure_indexes():
    """Create necessary indexes. Safe to call multiple times."""
    await pyq_sessions_col.create_index("session_id", unique=True)
    await pyq_answers_col.create_index(
        [("session_id", 1), ("question_number", 1)], unique=True
    )


async def migrate_disk_sessions():
    """
    On startup, scan the disk sessions folder and upsert any sessions that
    are not yet in MongoDB. Handles cases where the server was restarted
    after a disk-only upload.
    """
    sessions_dir = Path(settings.PYQ_SESSIONS_DIR)
    if not sessions_dir.exists():
        return
    for f in sessions_dir.glob("*.json"):
        try:
            with open(f) as fp:
                session = json.load(fp)
            await pyq_sessions_col.update_one(
                {"session_id": session["session_id"]},
                {"$setOnInsert": {**session, "saved_at": datetime.now(UTC)}},
                upsert=True,
            )
        except Exception:
            pass   # silently skip malformed files


# ── Session operations ────────────────────────────────────

async def save_session(session: dict) -> None:
    """Upsert a full session document (questions included) into MongoDB."""
    doc = {**session, "saved_at": datetime.now(UTC)}
    await pyq_sessions_col.update_one(
        {"session_id": session["session_id"]},
        {"$set": doc},
        upsert=True,
    )


async def list_sessions(limit: int = 100) -> list:
    """Return session summaries sorted newest-first (no questions array)."""
    cursor = pyq_sessions_col.find(
        {},
        {
            "_id": 0, "session_id": 1, "filename": 1,
            "subject": 1, "year": 1, "total_questions": 1,
            "created_at": 1, "saved_at": 1,
        },
    ).sort("saved_at", -1).limit(limit)
    return [doc async for doc in cursor]


async def get_session_db(session_id: str) -> dict | None:
    """Return full session doc (with questions list) or None."""
    return await pyq_sessions_col.find_one({"session_id": session_id}, {"_id": 0})


async def delete_session_db(session_id: str) -> bool:
    """Delete session + all its cached answers. Returns True if found."""
    res = await pyq_sessions_col.delete_one({"session_id": session_id})
    await pyq_answers_col.delete_many({"session_id": session_id})
    return res.deleted_count > 0


# ── Answer cache operations ───────────────────────────────

async def get_cached_answer(session_id: str, question_number: int) -> dict | None:
    """Return full cached answer doc or None if not generated yet."""
    return await pyq_answers_col.find_one(
        {"session_id": session_id, "question_number": question_number},
        {"_id": 0},
    )


async def save_answer(
    session_id: str,
    question_number: int,
    question_text: str,
    answer_text: str,
    model_used: str,
    subject: str,
    marks,
    year: str,
) -> None:
    """Upsert an answer into pyq_answers (idempotent)."""
    doc = {
        "session_id": session_id,
        "question_number": question_number,
        "question_text": question_text,
        "answer": answer_text,
        "model_used": model_used,
        "subject": subject,
        "marks": marks,
        "year": year,
        "generated_at": datetime.now(UTC),
    }
    await pyq_answers_col.update_one(
        {"session_id": session_id, "question_number": question_number},
        {"$set": doc},
        upsert=True,
    )


async def get_all_answers_for_session(session_id: str) -> dict:
    """Return {question_number (int): answer_text} for a full session."""
    cursor = pyq_answers_col.find(
        {"session_id": session_id},
        {"_id": 0, "question_number": 1, "answer": 1, "model_used": 1, "generated_at": 1},
    )
    return {
        doc["question_number"]: {
            "answer": doc["answer"],
            "model_used": doc.get("model_used", ""),
            "from_cache": True,
        }
        async for doc in cursor
    }
