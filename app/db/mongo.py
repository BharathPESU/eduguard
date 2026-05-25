from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from datetime import datetime
from bson import ObjectId

client = AsyncIOMotorClient(
    settings.MONGO_URI,
    serverSelectionTimeoutMS=5000,
)
db = client[settings.DB_NAME]

tutor_logs = db["tutor_logs"]
exam_logs = db["exam_logs"]
violations = db["violations"]
documents = db["documents"]

async def log_tutor_interaction(data: dict):
    data["timestamp"] = datetime.utcnow()
    await tutor_logs.insert_one(data)

async def log_exam_submission(data: dict):
    data["timestamp"] = datetime.utcnow()
    await exam_logs.insert_one(data)

async def log_violation(data: dict):
    data["timestamp"] = datetime.utcnow()
    await violations.insert_one(data)

async def save_document_metadata(data: dict):
    data["uploaded_at"] = datetime.utcnow()
    result = await documents.insert_one(data)
    data["_id"] = str(result.inserted_id)
    return data

async def get_student_documents(student_id: str, limit: int = 50):
    cursor = documents.find({"student_id": student_id}).sort("uploaded_at", -1).limit(limit)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results

async def get_document_by_id(document_id: str):
    if not ObjectId.is_valid(document_id):
        return None

    doc = await documents.find_one({"_id": ObjectId(document_id)})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

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
