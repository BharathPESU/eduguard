from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from datetime import datetime

client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.DB_NAME]

tutor_logs = db["tutor_logs"]
exam_logs = db["exam_logs"]
violations = db["violations"]

async def log_tutor_interaction(data: dict):
    data["timestamp"] = datetime.utcnow()
    await tutor_logs.insert_one(data)

async def log_exam_submission(data: dict):
    data["timestamp"] = datetime.utcnow()
    await exam_logs.insert_one(data)

async def log_violation(data: dict):
    data["timestamp"] = datetime.utcnow()
    await violations.insert_one(data)

async def get_recent_violations(limit: int = 50):
    cursor = violations.find().sort("timestamp", -1).limit(limit)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results

async def get_exam_submissions(limit: int = 50):
    cursor = exam_logs.find().sort("timestamp", -1).limit(limit)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results