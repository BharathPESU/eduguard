import os
import asyncio
from any_llm import completion

def invoke_llm(system_prompt: str, user_message: str, model_id: str, max_tokens: int = 1024) -> str:
    """Synchronous LLM call — do NOT call from async context, use invoke_llm_async instead."""
    # Ensure boto3 picks up credentials from env (loaded from .env by config.py at startup)
    client_args = {
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "region_name": os.getenv("AWS_REGION"),
    }
    response = completion(
        model=model_id,
        provider="bedrock",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        max_tokens=max_tokens,
        client_args=client_args,
    )
    return response.choices[0].message.content

async def invoke_llm_async(system_prompt: str, user_message: str, model_id: str, max_tokens: int = 1024) -> str:
    """Async-safe wrapper: runs the sync LLM call in a thread pool to avoid blocking the event loop."""
    return await asyncio.to_thread(
        invoke_llm,
        system_prompt,
        user_message,
        model_id,
        max_tokens
    )