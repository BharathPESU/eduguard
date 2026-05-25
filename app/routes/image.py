"""
Image generation route — uses NVIDIA qwen/qwen-image via the OpenAI-compatible
images endpoint at https://integrate.api.nvidia.com/v1.

Pipeline:
  1. LLM (TUTOR_MODEL_ID) distils the question + tutor answer into a focused
     educational visual prompt  (≤ 100 words, no text in image).
  2. NVIDIA qwen/qwen-image generates the image and returns b64_json.
  3. We return a data URI so the browser can display it without a second fetch.
"""
import base64
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from app.auth.dependencies import get_current_user
from app.limiter import limiter

from app.config import settings
from app.llm.nvidia_client import invoke_llm_async

router = APIRouter(prefix="/images", tags=["images"])

# ──────────────────────────────────────────────────────────
# Request / helpers
# ──────────────────────────────────────────────────────────

class ConceptImageRequest(BaseModel):
    question: str = Field(..., min_length=3)
    subject: str = "General"
    grade_level: str = "10"
    tutor_response: Optional[str] = None   # AI answer to summarise (optional)


_PROMPT_SYSTEM = (
    "You are a visual-prompt engineer for educational AI. "
    "Given a student's question and an optional tutor explanation, "
    "write ONE concise image-generation prompt (max 80 words) that will "
    "produce a clear, accurate, labelled educational diagram or illustration. "
    "Rules: NO text in the image, photorealistic or clean line-art style, "
    "grade-appropriate, single-concept focus. Output ONLY the prompt, nothing else."
)


async def _build_visual_prompt(question: str, subject: str, grade: str,
                                tutor_response: Optional[str]) -> str:
    """Ask the LLM to summarise into a crisp visual prompt."""
    context = f"Subject: {subject}\nGrade: {grade}\nStudent question: {question}"
    if tutor_response:
        # Keep it concise — first 600 chars is plenty for context
        context += f"\nTutor explanation (excerpt): {tutor_response[:600]}"
    try:
        prompt = await invoke_llm_async(
            system_prompt=_PROMPT_SYSTEM,
            user_message=context,
            model_id=settings.TUTOR_MODEL_ID,
            max_tokens=150,
        )
        return prompt.strip()
    except Exception:
        # Fallback: build a prompt manually
        return (
            f"Educational diagram for Grade {grade} {subject}: {question}. "
            "Clean, labeled illustration, no decorative text."
        )


def _b64_to_data_uri(b64: str, mime: str = "image/png") -> str:
    """Wrap a raw base64 string in a data URI."""
    # NVIDIA sometimes wraps it with a data URI prefix already
    if b64.startswith("data:"):
        return b64
    return f"data:{mime};base64,{b64}"


# ──────────────────────────────────────────────────────────
# Route
# ──────────────────────────────────────────────────────────

@router.post("/concept")
@limiter.limit("5/minute")
async def generate_concept_image(
    request: Request,
    body: ConceptImageRequest,
    user: dict = Depends(get_current_user),
):
    if not settings.NVIDIA_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="NVIDIA_API_KEY is not configured on the server.",
        )

    # Step 1 — distil question + tutor answer into a visual prompt
    visual_prompt = await _build_visual_prompt(
        question=body.question,
        subject=body.subject,
        grade=body.grade_level,
        tutor_response=body.tutor_response,
    )

    # Step 2 — call NVIDIA qwen/qwen-image (OpenAI images endpoint)
    payload = {
        "model": settings.IMAGE_MODEL_ID,
        "prompt": visual_prompt,
        "n": 1,
        "response_format": "b64_json",
    }

    try:
        async with httpx.AsyncClient(timeout=180) as http:
            resp = await http.post(
                f"{settings.NVIDIA_BASE_URL}/images/generations",
                headers={
                    "Authorization": f"Bearer {settings.NVIDIA_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text[:600] if exc.response is not None else str(exc)
        raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"NVIDIA image request failed: {exc}") from exc

    data = resp.json()

    # Step 3 — extract image(s) from the OpenAI-compatible response
    image_items = data.get("data", [])
    if not image_items:
        raise HTTPException(
            status_code=502,
            detail="NVIDIA response did not include image data.",
        )

    images = []
    for item in image_items:
        b64 = item.get("b64_json") or item.get("url")
        if b64:
            images.append(_b64_to_data_uri(b64))

    if not images:
        raise HTTPException(
            status_code=502,
            detail="Could not extract images from NVIDIA response.",
        )

    return {
        "status": "success",
        "prompt": visual_prompt,
        "images": images,
    }
