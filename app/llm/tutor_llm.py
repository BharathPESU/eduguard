from app.llm.nvidia_client import invoke_llm_async
from app.config import settings

TUTOR_SYSTEM_PROMPT = """You are a Socratic AI tutor for school and college students.

Your strict rules:
1. NEVER give direct answers to homework, exam, or assignment questions.
2. Always respond with guiding questions, hints, or partial explanations.
3. Break down complex topics into 2-3 simple steps.
4. Use real-world analogies and examples.
5. Keep language appropriate for the student's grade level.
6. End every response with an encouraging question that pushes the student to think further.
7. If a student seems frustrated, acknowledge it and offer a simpler hint.

You are NOT a cheating tool. You are a thinking partner."""

async def get_tutor_response(question: str, subject: str = "General", grade: str = "10") -> str:
    user_message = f"""
Subject: {subject}
Grade Level: {grade}
Student Question: {question}

Remember: Guide, don't give the answer.
"""
    return await invoke_llm_async(
        system_prompt=TUTOR_SYSTEM_PROMPT,
        user_message=user_message,
        model_id=settings.TUTOR_MODEL_ID
    )