from fastapi import APIRouter, HTTPException
from app.models.request_models import TutorRequest
from app.guardrails.jailbreak import check_jailbreak, check_integrity
from app.guardrails.content import check_content_safety
from app.llm.tutor_llm import get_tutor_response
from app.db.mongo import log_tutor_interaction, log_violation
from datetime import datetime

router = APIRouter(prefix="/tutor", tags=["Safe Tutor"])

@router.post("/ask")
async def ask_tutor(request: TutorRequest):
    stages_passed = []

    # Stage 1: Jailbreak check
    jailbreak_result = check_jailbreak(request.question)
    if not jailbreak_result.passed:
        await log_violation({
            "student_id": request.student_id,
            "type": jailbreak_result.rule_triggered,
            "severity": jailbreak_result.severity,
            "input": request.question,
            "endpoint": "/tutor/ask"
        })
        return {
            "status": "blocked",
            "stage": "jailbreak_check",
            "reason": jailbreak_result.rule_triggered,
            "message": jailbreak_result.message,
            "response": None
        }
    stages_passed.append("jailbreak_check")

    # Stage 2: Academic integrity check
    integrity_result = check_integrity(request.question)
    if not integrity_result.passed:
        await log_violation({
            "student_id": request.student_id,
            "type": integrity_result.rule_triggered,
            "severity": integrity_result.severity,
            "input": request.question,
            "endpoint": "/tutor/ask"
        })
        return {
            "status": "blocked",
            "stage": "integrity_check",
            "reason": integrity_result.rule_triggered,
            "message": integrity_result.message,
            "response": None
        }
    stages_passed.append("integrity_check")

    # Stage 3: Content safety check
    content_result = check_content_safety(request.question)
    if not content_result.passed:
        await log_violation({
            "student_id": request.student_id,
            "type": content_result.rule_triggered,
            "severity": content_result.severity,
            "input": request.question,
            "endpoint": "/tutor/ask"
        })
        return {
            "status": "blocked",
            "stage": "content_safety",
            "reason": content_result.rule_triggered,
            "message": content_result.message,
            "response": None
        }
    stages_passed.append("content_safety")

    # All stages passed — invoke LLM
    try:
        tutor_response = await get_tutor_response(
            question=request.question,
            subject=request.subject,
            grade=request.grade_level
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

    await log_tutor_interaction({
        "student_id": request.student_id,
        "question": request.question,
        "subject": request.subject,
        "grade_level": request.grade_level,
        "stages_passed": stages_passed,
        "response_length": len(tutor_response)
    })

    return {
        "status": "success",
        "stages_passed": stages_passed,
        "response": tutor_response
    }