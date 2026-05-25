"""
JWT authentication dependency for FastAPI.

Usage:
    from app.auth.dependencies import get_current_user, require_teacher

    @router.get("/secret")
    async def secret(user: dict = Depends(get_current_user)):
        return {"user_id": user["sub"]}

Token source: Supabase JWT (HS256, signed with SUPABASE_JWT_SECRET).
The sub claim is the Supabase user UUID — used as the canonical student_id.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import settings

_bearer = HTTPBearer(auto_error=False)


def _decode(token: str) -> dict:
    """Decode and verify a Supabase-issued JWT."""
    if not settings.SUPABASE_JWT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server is not configured for authentication (missing SUPABASE_JWT_SECRET).",
        )
    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False},   # Supabase doesn't set audience by default
        )
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


async def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict:
    """
    Dependency — validates the Bearer JWT and returns the decoded claims.
    Raises HTTP 401 if no token or invalid token.
    """
    if creds is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Provide a Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _decode(creds.credentials)


async def require_teacher(user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency — requires a valid JWT AND the user's role to be 'teacher'.
    Supabase stores custom claims under app_metadata.role or user_metadata.role.
    """
    role = (
        (user.get("app_metadata") or {}).get("role")
        or (user.get("user_metadata") or {}).get("role")
        or user.get("role")
    )
    if role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Teacher role required.",
        )
    return user
