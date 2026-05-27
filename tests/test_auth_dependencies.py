import asyncio

import httpx
import pytest
from fastapi import HTTPException

from app.auth import dependencies
from app.config import settings


class FakeAsyncClient:
    def __init__(self, response):
        self.response = response
        self.request_headers = None
        self.request_url = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url, headers):
        self.request_url = url
        self.request_headers = headers
        return self.response


def test_decode_uses_supabase_auth_api_when_jwt_secret_is_missing(monkeypatch):
    monkeypatch.setattr(settings, "SUPABASE_JWT_SECRET", "")
    monkeypatch.setattr(settings, "SUPABASE_URL", "https://example.supabase.co/")
    monkeypatch.setattr(settings, "SUPABASE_ANON_KEY", "anon-key")

    response = httpx.Response(
        200,
        json={
            "id": "user-123",
            "email": "student@example.com",
            "role": "authenticated",
            "app_metadata": {"role": "student"},
            "user_metadata": {"name": "Student"},
        },
    )
    fake_client = FakeAsyncClient(response)
    monkeypatch.setattr(dependencies.httpx, "AsyncClient", lambda timeout: fake_client)

    user = asyncio.run(dependencies._decode("access-token"))

    assert user["sub"] == "user-123"
    assert user["email"] == "student@example.com"
    assert user["app_metadata"] == {"role": "student"}
    assert fake_client.request_url == "https://example.supabase.co/auth/v1/user"
    assert fake_client.request_headers == {
        "apikey": "anon-key",
        "Authorization": "Bearer access-token",
    }


def test_decode_rejects_invalid_supabase_token(monkeypatch):
    monkeypatch.setattr(settings, "SUPABASE_JWT_SECRET", "")
    monkeypatch.setattr(settings, "SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setattr(settings, "SUPABASE_ANON_KEY", "anon-key")

    fake_client = FakeAsyncClient(httpx.Response(401, json={"message": "bad token"}))
    monkeypatch.setattr(dependencies.httpx, "AsyncClient", lambda timeout: fake_client)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(dependencies._decode("bad-token"))

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid or expired token."
