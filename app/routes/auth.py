import asyncio
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr, Field
from supabase import create_client

from app.config import settings
from app.limiter import limiter

router = APIRouter(prefix="/auth", tags=["auth"])


class AuthCredentials(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)


def _get_supabase():
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        raise HTTPException(
            status_code=500,
            detail="SUPABASE_URL and SUPABASE_ANON_KEY must be configured.",
        )
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


def _user_payload(user):
    if not user:
        return None
    return {
        "id": getattr(user, "id", None),
        "email": getattr(user, "email", None),
        "created_at": getattr(user, "created_at", None),
    }


def _session_payload(session):
    if not session:
        return None
    return {
        "access_token": getattr(session, "access_token", None),
        "refresh_token": getattr(session, "refresh_token", None),
        "token_type": getattr(session, "token_type", "bearer"),
        "expires_in": getattr(session, "expires_in", None),
        "expires_at": getattr(session, "expires_at", None),
    }


def _auth_response_payload(response, status: str):
    session = _session_payload(getattr(response, "session", None))
    return {
        "status": status,
        "user": _user_payload(getattr(response, "user", None)),
        "session": session,
        "access_token": session["access_token"] if session else None,
    }


async def _run_supabase(callable_):
    try:
        return await asyncio.to_thread(callable_)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/signup")
@limiter.limit("10/minute")
async def signup(request: Request, credentials: AuthCredentials):
    supabase = _get_supabase()
    response = await _run_supabase(
        lambda: supabase.auth.sign_up({
            "email": credentials.email,
            "password": credentials.password,
            "options": {
                "email_redirect_to": f"{settings.FRONTEND_URL}/login",
            },
        })
    )
    payload = _auth_response_payload(response, "confirmation_sent")
    payload["message"] = "Check your email to confirm your account."
    return payload


@router.post("/login")
@limiter.limit("10/minute")
async def login(request: Request, credentials: AuthCredentials):
    supabase = _get_supabase()
    response = await _run_supabase(
        lambda: supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password,
        })
    )
    return _auth_response_payload(response, "success")


@router.post("/refresh")
@limiter.limit("20/minute")
async def refresh_session(request: Request, payload: RefreshRequest):
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        raise HTTPException(
            status_code=500,
            detail="SUPABASE_URL and SUPABASE_ANON_KEY must be configured.",
        )

    url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/token?grant_type=refresh_token"
    headers = {
        "apikey": settings.SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_ANON_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                url,
                headers=headers,
                json={"refresh_token": payload.refresh_token},
            )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=503,
            detail="Unable to refresh Supabase session.",
        ) from exc

    if response.status_code in {400, 401, 403}:
        raise HTTPException(
            status_code=401,
            detail="Session expired. Please log in again.",
        )
    if response.status_code >= 400:
        raise HTTPException(
            status_code=503,
            detail="Unable to refresh Supabase session.",
        )

    data = response.json()
    session = {
        "access_token": data.get("access_token"),
        "refresh_token": data.get("refresh_token") or payload.refresh_token,
        "token_type": data.get("token_type", "bearer"),
        "expires_in": data.get("expires_in"),
        "expires_at": data.get("expires_at"),
    }
    return {
        "status": "success",
        "user": data.get("user"),
        "session": session,
        "access_token": session["access_token"],
    }


@router.get("/google")
async def google_login():
    if not settings.SUPABASE_URL:
        raise HTTPException(status_code=500, detail="SUPABASE_URL must be configured.")

    query = urlencode({
        "provider": "google",
        "redirect_to": f"{settings.FRONTEND_URL}/auth/callback",
    })
    auth_url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/authorize?{query}"
    return RedirectResponse(url=auth_url, status_code=302)
