from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import settings

router = APIRouter(prefix="/images", tags=["images"])


class ConceptImageRequest(BaseModel):
    question: str = Field(..., min_length=3)
    subject: str = "General"
    grade_level: str = "10"


def _extract_image_urls(payload: dict[str, Any]) -> list[str]:
    data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    if not isinstance(data, dict):
        return []

    for key in ("image_urls", "urls"):
        urls = data.get(key)
        if isinstance(urls, list):
            return [url for url in urls if isinstance(url, str)]

    images = data.get("images")
    if isinstance(images, list):
        urls = []
        for image in images:
            if isinstance(image, str):
                urls.append(image)
            elif isinstance(image, dict) and isinstance(image.get("url"), str):
                urls.append(image["url"])
        return urls

    return []


@router.post("/concept")
async def generate_concept_image(request: ConceptImageRequest):
    if not settings.MINIMAX_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="MINIMAX_API_KEY is not configured on the server.",
        )

    prompt = (
        f"Create a clear educational visual for a Grade {request.grade_level} "
        f"{request.subject} concept. The student asked: {request.question}. "
        "Make it accurate, beginner-friendly, photorealistic or clean diagram style, "
        "with no distracting text, labels only when useful for understanding."
    )

    payload = {
        "model": settings.MINIMAX_IMAGE_MODEL,
        "prompt": prompt,
        "aspect_ratio": "16:9",
        "response_format": "url",
        "n": 1,
        "prompt_optimizer": True,
    }

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                "https://api.minimax.io/v1/image_generation",
                headers={
                    "Authorization": f"Bearer {settings.MINIMAX_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text[:500] if exc.response is not None else str(exc)
        raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"MiniMax request failed: {exc}") from exc

    data = response.json()
    base_resp = data.get("base_resp")
    if isinstance(base_resp, dict) and base_resp.get("status_code") not in (None, 0):
        status_msg = base_resp.get("status_msg") or "MiniMax image generation failed."
        status_code = 402 if "balance" in status_msg.lower() else 502
        raise HTTPException(status_code=status_code, detail=status_msg)

    image_urls = _extract_image_urls(data)
    if not image_urls:
        raise HTTPException(
            status_code=502,
            detail="MiniMax response did not include image URLs.",
        )

    return {
        "status": "success",
        "prompt": prompt,
        "images": image_urls,
    }
