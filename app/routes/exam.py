from fastapi import APIRouter, Depends, HTTPException, Request
from app.models.request_models import ExamRequest
from app.guardrails.injection import check_grade_injection
from app.llm.plagiarism_llm import detect_plagiarism
from app.llm.grader_llm import grade_answer
from app.db.mongo import log_exam_submission, log_violation
from app.auth.dependencies import get_current_user
from app.limiter import limiter

router = APIRouter(prefix="/exam", tags=["Exam Validator"])


def _assert_owns(user: dict, student_id: str) -> None:
    if user.get("sub", "") != student_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied. student_id must match your account.",
        )


@router.post("/validate")
@limiter.limit("20/minute")
async def validate_exam(
    request: Request,
    body: ExamRequest,
    user: dict = Depends(get_current_user),
):
    # IDOR fix — only the owning student can submit under their ID
    _assert_owns(user, body.student_id)

    stages_passed = []

    # Stage 1: Injection check
    injection_result = check_grade_injection(body.student_answer)
    if not injection_result.passed:
        await log_violation({
            "student_id": body.student_id,
            "exam_id": body.exam_id,
            "type": injection_result.rule_triggered,
            "severity": injection_result.severity,
            "input": body.student_answer,
            "endpoint": "/exam/validate"
        })
        return {
            "status": "blocked",
            "stage": "injection_check",
            "reason": injection_result.rule_triggered,
            "message": injection_result.message,
            "security": {"injection_attempt": True},
            "grading": None
        }
    stages_passed.append("injection_check")

    # Stage 2: Plagiarism detection
    plagiarism_result = await detect_plagiarism(
        student_answer=body.student_answer,
        grade_level=body.grade_level
    )
    stages_passed.append("plagiarism_detection")

    # Stage 3: Grade the answer
    try:
        grading_result = await grade_answer(
            question=body.question,
            rubric=body.rubric,
            student_answer=body.student_answer
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Grading error: {str(e)}")
    stages_passed.append("grading")

    # Save full submission
    await log_exam_submission({
        "student_id": body.student_id,
        "exam_id": body.exam_id,
        "question": body.question,
        "student_answer": body.student_answer,
        "security": {
            "injection_attempt": False,
            "plagiarism_suspected": plagiarism_result.get("plagiarism_suspected"),
            "ai_generated_probability": plagiarism_result.get("ai_generated_probability"),
            "plagiarism_confidence": plagiarism_result.get("confidence"),
            "signals": plagiarism_result.get("signals", [])
        },
        "grading": grading_result,
        "stages_passed": stages_passed
    })

    return {
        "status": "success",
        "student_id": body.student_id,
        "exam_id": body.exam_id,
        "stages_passed": stages_passed,
        "security": {
            "injection_attempt": False,
            "plagiarism_suspected": plagiarism_result.get("plagiarism_suspected"),
            "ai_generated_probability": plagiarism_result.get("ai_generated_probability"),
            "plagiarism_confidence": plagiarism_result.get("confidence"),
            "signals": plagiarism_result.get("signals", [])
        },
        "grading": grading_result
    }