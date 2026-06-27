"""
Agent 1 — PYQ Extractor
Receives an uploaded file (PDF or image), extracts all questions, and saves
them as a JSON session file.

Uses NVIDIA NIM vision model (llama-3.2-90b-vision-instruct) via the
OpenAI-compatible API — the same provider used by the rest of EduGuard.

PDF pages are converted to base64-encoded PNG images and sent one-by-one
to the vision model (NIM does not support multi-image in a single message),
then results are merged into a single question list.
"""
import base64
import json
import uuid
from datetime import datetime
from pathlib import Path

import fitz  # pymupdf
from openai import OpenAI

from app.config import settings
from app.utils.logger import logger


# ──────────────────────────────────────────────────────────
# NVIDIA NIM client (vision-capable)
# ──────────────────────────────────────────────────────────

def _get_vision_client() -> OpenAI:
    return OpenAI(
        base_url=settings.NVIDIA_BASE_URL,
        api_key=settings.NVIDIA_API_KEY,
    )


# ──────────────────────────────────────────────────────────
# Prompts
# ──────────────────────────────────────────────────────────

_EXTRACT_SYSTEM = (
    "You are an expert at extracting exam questions from scanned question papers. "
    "Return ONLY a valid JSON array with no preamble, no explanation, and no markdown fences."
)

_EXTRACT_USER_TMPL = """
Analyze this exam paper page image and extract ALL questions visible.

Rules:
1. Extract every question exactly as written — do not paraphrase or shorten.
2. Include sub-questions (a, b, c) as part of the parent question text.
3. Include marks if shown e.g. "[5 marks]". Set "marks" to null if not shown.
4. Ignore instructions, headers, roll number fields, and time limits.
5. Continue numbering from {start_num} (there may be prior pages already extracted).

Return ONLY a valid JSON array. No preamble, no explanation, no markdown backticks.
[
  {{
    "question_number": {start_num},
    "question_text": "full question text here",
    "marks": 5,
    "subject_hint": "topic this question is about"
  }}
]

If no questions are found on this page (e.g. it is a cover page), return an empty array: []
"""

_EXTRACT_USER_TMPL_TEXT = """
Extract ALL exam questions from this question paper text.

Rules:
1. Extract every question exactly as written — do not paraphrase or shorten.
2. Include sub-questions (a, b, c) as part of the parent question text.
3. Include marks if shown e.g. "[5 marks]". Set "marks" to null if not shown.
4. Ignore instructions, headers, roll number fields, and time limits.
5. Number questions sequentially starting from 1.

Question paper text:
{text}

Return ONLY a valid JSON array. No preamble, no explanation, no markdown backticks.
[
  {{
    "question_number": 1,
    "question_text": "full question text here",
    "marks": 5,
    "subject_hint": "topic"
  }}
]
"""


# ──────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────

def _pdf_to_b64_images(pdf_bytes: bytes) -> list[str]:
    """Convert every PDF page to a base64-encoded PNG string."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    b64_images = []
    for page in doc:
        pix = page.get_pixmap(dpi=150)          # 150 DPI — good balance of quality/size
        img_bytes = pix.tobytes("png")
        b64_images.append(base64.b64encode(img_bytes).decode("utf-8"))
    return b64_images


def _pdf_to_text(pdf_bytes: bytes) -> str:
    """Extract embedded text from a PDF (fallback when images fail)."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return "\n\n".join(page.get_text() for page in doc).strip()


def _parse_json_response(raw: str) -> list:
    """Strip markdown fences and parse JSON array from model output."""
    raw = raw.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    # Find the array boundaries robustly
    start = raw.find("[")
    end = raw.rfind("]")
    if start == -1 or end == -1:
        return []
    return json.loads(raw[start : end + 1])


def _extract_from_image_b64(client: OpenAI, b64: str, start_num: int, mime: str = "image/png") -> list:
    """Send one image to the vision model and return extracted questions."""
    prompt = _EXTRACT_USER_TMPL.format(start_num=start_num)
    resp = client.chat.completions.create(
        model=settings.VISION_MODEL_ID,
        messages=[
            {"role": "system", "content": _EXTRACT_SYSTEM},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                    {"type": "text", "text": prompt},
                ],
            },
        ],
        max_tokens=2048,
        temperature=0.1,
    )
    raw = resp.choices[0].message.content or ""
    return _parse_json_response(raw)


def _extract_from_text(client: OpenAI, text: str) -> list:
    """Extract questions from plain text using the text LLM."""
    from app.llm.nvidia_client import invoke_llm   # sync call fine here (we're not in async)
    prompt = _EXTRACT_USER_TMPL_TEXT.format(text=text[:8000])
    raw = invoke_llm(
        system_prompt=_EXTRACT_SYSTEM,
        user_message=prompt,
        model_id=settings.TUTOR_MODEL_ID,
        max_tokens=3000,
    )
    return _parse_json_response(raw)


# ──────────────────────────────────────────────────────────
# Public entry point
# ──────────────────────────────────────────────────────────

def extract_questions_from_file(
    file_bytes: bytes,
    filename: str,
    subject: str = "Unknown",
    year: str = "Unknown",
) -> dict:
    """
    Extract all questions from a PDF or image file.

    Strategy:
      - PDF: convert every page to a PNG image → send each to vision model.
        If images are too large / vision call fails for a page, fall back to
        embedded text extraction for that page.
      - Image (PNG/JPG): send directly to vision model.

    All extracted questions are merged, renumbered, and saved as a session JSON.
    """
    client = _get_vision_client()
    questions: list = []
    lower = filename.lower()

    if lower.endswith(".pdf"):
        # Try vision-based extraction page by page
        try:
            b64_pages = _pdf_to_b64_images(file_bytes)
            for b64 in b64_pages:
                start_num = len(questions) + 1
                try:
                    page_qs = _extract_from_image_b64(client, b64, start_num)
                    questions.extend(page_qs)
                except Exception as e:
                    logger.exception("Vision extraction failed for page")

            # If vision yielded nothing, fall back to text extraction
            if not questions:
                text = _pdf_to_text(file_bytes)
                if text.strip():
                    questions = _extract_from_text(client, text)
        except Exception as e:
            logger.exception("PDF image conversion or vision extraction failed, falling back to text")
            # PDF image conversion failed — extract as text
            text = _pdf_to_text(file_bytes)
            if text.strip():
                questions = _extract_from_text(client, text)

    elif lower.endswith(".jpg") or lower.endswith(".jpeg"):
        b64 = base64.b64encode(file_bytes).decode("utf-8")
        questions = _extract_from_image_b64(client, b64, 1, mime="image/jpeg")
    else:
        # PNG or other image
        b64 = base64.b64encode(file_bytes).decode("utf-8")
        questions = _extract_from_image_b64(client, b64, 1, mime="image/png")

    # Re-number questions sequentially (model may restart numbering per page)
    for idx, q in enumerate(questions, start=1):
        q["question_number"] = idx

    # Build and persist the session
    session_id = str(uuid.uuid4())[:8].upper()
    session = {
        "session_id": session_id,
        "filename": filename,
        "subject": subject,
        "year": year,
        "total_questions": len(questions),
        "created_at": datetime.utcnow().isoformat(),
        "questions": questions,
    }

    sessions_dir = Path(settings.PYQ_SESSIONS_DIR)
    sessions_dir.mkdir(parents=True, exist_ok=True)
    session_file = sessions_dir / f"{session_id}.json"
    with open(session_file, "w") as f:
        json.dump(session, f, indent=2)

    return session
