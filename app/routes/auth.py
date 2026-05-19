import asyncio
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr, Field
from supabase import create_client

from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
oauth_code_verifiers: dict[str, str] = {}


class AuthCredentials(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


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
async def signup(credentials: AuthCredentials):
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
async def login(credentials: AuthCredentials):
    supabase = _get_supabase()
    response = await _run_supabase(
        lambda: supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password,
        })
    )
    return _auth_response_payload(response, "success")


@router.get("/google")
async def google_login():
    supabase = _get_supabase()
    state = uuid4().hex
    response = await _run_supabase(
        lambda: supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": f"{settings.BACKEND_URL}/auth/callback",
                "query_params": {"state": state},
            },
        })
    )
    storage_key = getattr(supabase.auth, "_storage_key", "supabase.auth.token")
    code_verifier = supabase.auth._storage.get_item(f"{storage_key}-code-verifier")
    if code_verifier:
        oauth_code_verifiers[state] = code_verifier

    return RedirectResponse(url=response.url, status_code=302)


@router.get("/callback")
async def auth_callback(code: str = Query(...), state: str | None = None):
    supabase = _get_supabase()
    code_verifier = oauth_code_verifiers.pop(state, None) if state else None
    if not code_verifier:
        raise HTTPException(status_code=400, detail="OAuth state expired. Start Google login again.")

    response = await _run_supabase(
        lambda: supabase.auth.exchange_code_for_session({
            "auth_code": code,
            "code_verifier": code_verifier,
        })
    )
    payload = _auth_response_payload(response, "success")
    session = payload.get("session") or {}
    if not session.get("access_token"):
        raise HTTPException(status_code=400, detail="Supabase did not return a session.")

    redirect_url = (
        f"{settings.FRONTEND_URL}/auth/callback"
        f"?access_token={session['access_token']}"
        f"&refresh_token={session.get('refresh_token') or ''}"
        f"&email={(payload.get('user') or {}).get('email') or ''}"
    )
    return RedirectResponse(url=redirect_url, status_code=302)
