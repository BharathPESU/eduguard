"""
Agent 2 — PYQ Session Manager
Manages session state on disk: listing, retrieving, navigating questions,
and deleting sessions. No AI calls — pure file I/O.
"""
import json
from pathlib import Path
from app.config import settings


def get_all_sessions() -> list:
    """Return summary info for all sessions, sorted newest-first."""
    sessions_dir = Path(settings.PYQ_SESSIONS_DIR)
    if not sessions_dir.exists():
        return []
    sessions = []
    for f in sorted(sessions_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
        with open(f) as file:
            data = json.load(file)
            sessions.append({
                "session_id": data["session_id"],
                "filename": data["filename"],
                "subject": data["subject"],
                "year": data["year"],
                "total_questions": data["total_questions"],
                "created_at": data["created_at"],
            })
    return sessions


def get_session(session_id: str) -> dict:
    """Load and return the full session (including all questions)."""
    session_file = Path(settings.PYQ_SESSIONS_DIR) / f"{session_id}.json"
    if not session_file.exists():
        raise FileNotFoundError(f"Session {session_id} not found")
    with open(session_file) as f:
        return json.load(f)


def get_question(session_id: str, question_number: int) -> dict:
    """
    Return a single question from a session by 1-based question_number.
    Raises IndexError if out of range, FileNotFoundError if session missing.
    """
    session = get_session(session_id)
    questions = session["questions"]
    if question_number < 1 or question_number > len(questions):
        raise IndexError(
            f"Question {question_number} out of range. "
            f"Session has {len(questions)} questions."
        )
    question = questions[question_number - 1]
    return {
        "session_id": session_id,
        "subject": session["subject"],
        "year": session["year"],
        "current_question_number": question_number,
        "total_questions": session["total_questions"],
        "is_last": question_number == session["total_questions"],
        "question": question,
    }


def delete_session(session_id: str) -> bool:
    """Delete a session JSON file. Returns True if deleted, False if not found."""
    session_file = Path(settings.PYQ_SESSIONS_DIR) / f"{session_id}.json"
    if session_file.exists():
        session_file.unlink()
        return True
    return False
