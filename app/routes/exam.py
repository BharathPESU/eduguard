from fastapi import APIRouter, HTTPException
from app.models.request_models import ExamRequest
from app.guardrails.injection import check_grade_injection
from app.llm.plagiarism_llm import detect_plagiarism
from app.llm.grader_llm import grade_answer
from app.db.mongo import log_exam_submission, log_violation

router = APIRouter(prefix="/exam", tags=["Exam Validator"])

@router.post("/validate")
async def validate_exam(request: ExamRequest):
    stages_passed = []

    # Stage 1: Injection check
    injection_result = check_grade_injection(request.student_answer)
    if not injection_result.passed:
        await log_violation({
            "student_id": request.student_id,
            "exam_id": request.exam_id,
            "type": injection_result.rule_triggered,
            "severity": injection_result.severity,
            "input": request.student_answer,
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
        student_answer=request.student_answer,
        grade_level=request.grade_level
    )
    stages_passed.append("plagiarism_detection")

    # Stage 3: Grade the answer
    try:
        grading_result = await grade_answer(
            question=request.question,
            rubric=request.rubric,
            student_answer=request.student_answer
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Grading error: {str(e)}")
    stages_passed.append("grading")

    # Save full submission
    await log_exam_submission({
        "student_id": request.student_id,
        "exam_id": request.exam_id,
        "question": request.question,
        "student_answer": request.student_answer,
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
        "student_id": request.student_id,
        "exam_id": request.exam_id,
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