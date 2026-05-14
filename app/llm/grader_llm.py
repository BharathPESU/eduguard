import json
from app.llm.bedrock_client import invoke_llm_async
from app.config import settings

GRADER_SYSTEM_PROMPT = """You are a strict but fair exam grader.

Rules:
1. Grade ONLY based on the rubric and question provided.
2. Be objective. Do not be lenient or harsh without reason.
3. Return ONLY valid JSON. No preamble, no explanation outside the JSON.
4. If the answer is empty or nonsensical, score it 0.

Return this exact JSON structure:
{
  "score": <integer 0-100>,
  "grade": "<A/B/C/D/F>",
  "concept_scores": {"<concept_name>": <score>},
  "correct_parts": ["<what was correct>"],
  "incorrect_parts": ["<what was wrong or missing>"],
  "feedback": "<2-3 sentence specific feedback>",
  "improvement_suggestion": "<one actionable suggestion>"
}"""

async def grade_answer(question: str, rubric: str, student_answer: str) -> dict:
    user_message = f"""
Question: {question}
Grading Rubric: {rubric}
Student Answer: {student_answer}

Grade this answer strictly according to the rubric.
"""
    raw = await invoke_llm_async(
        system_prompt=GRADER_SYSTEM_PROMPT,
        user_message=user_message,
        model_id=settings.GRADER_MODEL_ID
    )
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        return json.loads(raw[start:end])