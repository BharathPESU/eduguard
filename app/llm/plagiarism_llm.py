import json
from app.llm.bedrock_client import invoke_llm_async
from app.config import settings

PLAGIARISM_SYSTEM_PROMPT = """You are an academic integrity analyzer.
Analyze the student answer for plagiarism and AI-generation signals.

Return ONLY valid JSON:
{
  "plagiarism_suspected": <true/false>,
  "ai_generated_probability": <integer 0-100>,
  "confidence": <integer 0-100>,
  "signals": ["<detected signal 1>", "<detected signal 2>"]
}"""

async def detect_plagiarism(student_answer: str, grade_level: str = "10") -> dict:
    user_message = f"""
Grade Level: {grade_level}
Student Answer: {student_answer}

Analyze this for plagiarism and AI-generation signals.
"""
    raw = await invoke_llm_async(
        system_prompt=PLAGIARISM_SYSTEM_PROMPT,
        user_message=user_message,
        model_id=settings.PLAGIARISM_MODEL_ID
    )
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        return json.loads(raw[start:end])