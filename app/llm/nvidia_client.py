"""
NVIDIA NIM client — uses NVIDIA's OpenAI-compatible API endpoint.
All EduGuard LLM calls go through invoke_llm_async() to stay async-safe.
"""
import asyncio
from openai import OpenAI
from app.config import settings


def _get_client() -> OpenAI:
    """Create a fresh OpenAI-compatible client pointing at NVIDIA NIM."""
    return OpenAI(
        base_url=settings.NVIDIA_BASE_URL,
        api_key=settings.NVIDIA_API_KEY,
    )


def invoke_llm(system_prompt: str, user_message: str, model_id: str, max_tokens: int = 1024) -> str:
    """Synchronous LLM call via NVIDIA NIM — do NOT call from async context."""
    client = _get_client()
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        max_tokens=max_tokens,
        temperature=0.6,
    )
    return response.choices[0].message.content


async def invoke_llm_async(system_prompt: str, user_message: str, model_id: str, max_tokens: int = 1024) -> str:
    """Async-safe wrapper: runs sync NVIDIA NIM call in a thread pool."""
    return await asyncio.to_thread(
        invoke_llm,
        system_prompt,
        user_message,
        model_id,
        max_tokens,
    )
