"""
Agent 3 — PYQ Answering
Generates a detailed, markdown-formatted exam answer using NVIDIA NIM
(the same provider used by the rest of EduGuard AI).
"""
from typing import Optional
from app.llm.nvidia_client import invoke_llm_async
from app.config import settings


ANSWER_SYSTEM_PROMPT = """You are an expert academic tutor answering exam questions for students.

Your answer must:
1. Start with a one-line direct answer (the core answer in **bold**).
2. Provide a detailed explanation with correct technical terminology.
3. Include a step-by-step breakdown if it is a numerical or derivation problem.
4. Include a real-world example or analogy if it aids understanding.
5. List **Key Points to Remember** at the end as bullet points.
6. Keep the tone educational, clear, and exam-focused.
7. If the question has multiple parts (a, b, c), answer each part separately.

Format your response in clean markdown."""


async def answer_question(
    question_text: str,
    subject: str = "General",
    marks: Optional[int] = None,
    year: str = "Unknown",
) -> dict:
    """
    Async — generate a comprehensive exam-ready answer.
    Returns a dict with answer text and metadata.
    """
    marks_context = f"This question carries {marks} marks. " if marks else ""
    year_context = f"This is from a {year} exam paper. "

    user_prompt = f"""Subject: {subject}
{year_context}{marks_context}

Question:
{question_text}

Provide a complete, exam-ready answer."""

    answer_text = await invoke_llm_async(
        system_prompt=ANSWER_SYSTEM_PROMPT,
        user_message=user_prompt,
        model_id=settings.TUTOR_MODEL_ID,
        max_tokens=2048,
    )

    return {
        "question": question_text,
        "subject": subject,
        "marks": marks,
        "answer": answer_text,
        "model_used": settings.TUTOR_MODEL_ID,
    }
