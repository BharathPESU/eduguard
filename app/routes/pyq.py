"""
PYQ (Previous Year Questions) FastAPI router — MongoDB-first.

Flow:
  1. POST /pyq/upload  → Agent 1 extracts all questions → saved to disk + MongoDB
  2. GET  /pyq/sessions         → list from MongoDB (user's own sessions)
  3. GET  /pyq/session/{id}     → full session from MongoDB (questions + cached answers)
  4. POST /pyq/question         → single question from MongoDB + cached answer if exists
  5. POST /pyq/answer           → check MongoDB cache first; generate only if missing → store
  6. DELETE /pyq/session/{id}   → delete from MongoDB + disk
"""
import asyncio
from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form

from app.agents.pyq_extractor import extract_questions_from_file
from app.agents.pyq_session_manager import delete_session as delete_from_disk
from app.agents.pyq_answering import answer_question
from app.models.pyq_models import PYQQuestionRequest, PYQAnswerRequest
from app.auth.dependencies import get_current_user
from app.db.pyq_db import (
    ensure_indexes,
    migrate_disk_sessions,
    save_session,
    list_sessions,
    get_session_db,
    delete_session_db,
    get_cached_answer,
    save_answer,
    get_all_answers_for_session,
)

from app.limiter import limiter

router = APIRouter(prefix="/pyq", tags=["PYQ Practice"])

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


# ── Startup initialisation ────────────────────────────────
# Called from app/main.py startup event (avoids deprecated on_event)

async def pyq_startup():
    """Create indexes and sync any disk sessions that aren't in MongoDB."""
    await ensure_indexes()
    await migrate_disk_sessions()


# ── Helpers ───────────────────────────────────────────────

def _pick_question(session: dict, q_num: int) -> dict:
    """Extract one question (1-based) from a session dict."""
    questions = session.get("questions", [])
    if q_num < 1 or q_num > len(questions):
        raise IndexError(
            f"Question {q_num} is out of range "
            f"(session has {len(questions)} questions)."
        )
    return questions[q_num - 1]


async def _load_session(session_id: str) -> dict:
    """Load session from MongoDB. Raises 404 HTTPException if not found."""
    session = await get_session_db(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return session


# ── Endpoints ─────────────────────────────────────────────

@router.post("/upload")
@limiter.limit("5/minute")
async def upload_question_paper(
    request: Request,
    file: UploadFile = File(...),
    subject: str = Form(default="Unknown"),
    year: str = Form(default="Unknown"),
    user: dict = Depends(get_current_user),
):
    """
    Upload a PDF or image question paper.
    Agent 1 extracts all questions and stores them in MongoDB immediately.
    """
    ext = "." + file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Use PDF, PNG, or JPG.",
        )

    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File too large. Maximum 20 MB.")

    try:
        # CPU-heavy extraction runs in thread pool (also writes disk JSON backup)
        session = await asyncio.to_thread(
            extract_questions_from_file,
            file_bytes,
            file.filename,
            subject,
            year,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

    # Always save to MongoDB — store owner for access control
    session["owner_id"] = user.get("sub", "")
    await save_session(session)

    return {
        "status": "success",
        "message": f"Extracted {session['total_questions']} questions and stored in database.",
        "session": {
            "session_id": session["session_id"],
            "filename": session["filename"],
            "subject": session["subject"],
            "year": session["year"],
            "total_questions": session["total_questions"],
            "created_at": session["created_at"],
        },
    }


@router.get("/sessions")
async def list_sessions_route(user: dict = Depends(get_current_user)):
    """List sessions owned by the authenticated user."""
    sessions = await list_sessions(owner_id=user.get("sub", ""))
    return {"sessions": sessions, "total": len(sessions)}


@router.get("/session/{session_id}")
async def get_session_detail(
    session_id: str,
    user: dict = Depends(get_current_user),
):
    """
    Return full session (all questions) + map of all already-generated answers.
    Frontend uses cached_answers to pre-populate answers without extra calls.
    """
    session = await _load_session(session_id)
    # IDOR fix — only the session owner can read it
    if session.get("owner_id") and session["owner_id"] != user.get("sub", ""):
        raise HTTPException(status_code=403, detail="Access denied.")
    cached = await get_all_answers_for_session(session_id)
    return {
        "session_id": session["session_id"],
        "filename": session["filename"],
        "subject": session["subject"],
        "year": session["year"],
        "total_questions": session["total_questions"],
        "created_at": session["created_at"],
        "questions": session.get("questions", []),
        "cached_answers": cached,   # {question_number: {answer, model_used, from_cache}}
    }


@router.post("/question")
async def get_question(
    req: PYQQuestionRequest,
    user: dict = Depends(get_current_user),
):
    """
    Fetch a single question from MongoDB by 1-based question_number.
    Also returns the cached answer if one exists, so the frontend can
    show the answer immediately without an extra /answer call.
    """
    session = await _load_session(req.session_id)

    try:
        q_data = _pick_question(session, req.question_number)
    except IndexError as e:
        raise HTTPException(status_code=400, detail=str(e))

    total = session["total_questions"]
    cached = await get_cached_answer(req.session_id, req.question_number)

    return {
        "session_id": req.session_id,
        "subject": session["subject"],
        "year": session["year"],
        "current_question_number": req.question_number,
        "total_questions": total,
        "is_last": req.question_number == total,
        "question": q_data,
        "cached_answer": {
            "answer": cached["answer"],
            "model_used": cached.get("model_used", ""),
            "from_cache": True,
        } if cached else None,
    }


@router.post("/answer")
@limiter.limit("20/minute")
async def get_answer(
    request: Request,
    req: PYQAnswerRequest,
    user: dict = Depends(get_current_user),
):
    """
    Answer a specific question.

    Cache-first logic:
      1. Check MongoDB for existing answer → return immediately if found.
      2. If not cached → call AI, store result in MongoDB, then return.

    The AI is NEVER called twice for the same (session_id, question_number).
    """
    session = await _load_session(req.session_id)

    try:
        q_data = _pick_question(session, req.question_number)
    except IndexError as e:
        raise HTTPException(status_code=400, detail=str(e))

    total = session["total_questions"]

    # ── 1. Cache hit ──────────────────────────────────────
    cached = await get_cached_answer(req.session_id, req.question_number)
    if cached:
        return {
            "status": "success",
            "from_cache": True,
            "current_question_number": req.question_number,
            "total_questions": total,
            "is_last": req.question_number == total,
            "question": q_data["question_text"],
            "subject": session["subject"],
            "marks": q_data.get("marks"),
            "answer": cached["answer"],
            "model_used": cached.get("model_used", ""),
        }

    # ── 2. Cache miss → generate ──────────────────────────
    result = await answer_question(
        question_text=q_data["question_text"],
        subject=session["subject"],
        marks=q_data.get("marks"),
        year=session["year"],
    )

    # Store in MongoDB so subsequent requests are instant
    await save_answer(
        session_id=req.session_id,
        question_number=req.question_number,
        question_text=q_data["question_text"],
        answer_text=result["answer"],
        model_used=result["model_used"],
        subject=session["subject"],
        marks=q_data.get("marks"),
        year=session["year"],
    )

    return {
        "status": "success",
        "from_cache": False,
        "current_question_number": req.question_number,
        "total_questions": total,
        "is_last": req.question_number == total,
        "question": q_data["question_text"],
        "subject": session["subject"],
        "marks": q_data.get("marks"),
        **result,
    }


@router.delete("/session/{session_id}")
async def delete_session_route(
    session_id: str,
    user: dict = Depends(get_current_user),
):
    """Delete a session and all its cached answers from MongoDB and disk."""
    session = await get_session_db(session_id)
    if session and session.get("owner_id") and session["owner_id"] != user.get("sub", ""):
        raise HTTPException(status_code=403, detail="Access denied.")
    db_ok   = await delete_session_db(session_id)
    disk_ok = delete_from_disk(session_id)
    if db_ok or disk_ok:
        return {"status": "success", "message": f"Session '{session_id}' deleted."}
    raise HTTPException(status_code=404, detail="Session not found.")
