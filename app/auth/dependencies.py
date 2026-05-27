"""
JWT authentication dependency for FastAPI.

Usage:
    from app.auth.dependencies import get_current_user, require_teacher

    @router.get("/secret")
    async def secret(user: dict = Depends(get_current_user)):
        return {"user_id": user["sub"]}

Token source: Supabase access token.
When SUPABASE_JWT_SECRET is configured, tokens are verified locally.
Otherwise, the token is verified by Supabase Auth using SUPABASE_URL and
SUPABASE_ANON_KEY. The sub claim is the Supabase user UUID — used as the
canonical student_id.
"""
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import settings

_bearer = HTTPBearer(auto_error=False)


def _decode_jwt(token: str) -> dict:
    """Decode and verify a Supabase-issued JWT."""
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


async def _get_user_from_supabase(token: str) -> dict:
    """Verify the token with Supabase Auth and normalize the user payload."""
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Server is not configured for authentication "
                "(missing SUPABASE_JWT_SECRET or SUPABASE_URL/SUPABASE_ANON_KEY)."
            ),
        )

    url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/user"
    headers = {
        "apikey": settings.SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {token}",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to verify authentication with Supabase.",
        ) from exc

    if response.status_code in {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN}:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if response.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to verify authentication with Supabase.",
        )

    user = response.json()
    user_id = user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: Supabase user id missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "sub": user_id,
        "email": user.get("email"),
        "aud": user.get("aud"),
        "role": user.get("role"),
        "app_metadata": user.get("app_metadata") or {},
        "user_metadata": user.get("user_metadata") or {},
    }


async def _decode(token: str) -> dict:
    """Verify a Supabase access token and return normalized claims."""
    if settings.SUPABASE_JWT_SECRET:
        return _decode_jwt(token)
    return await _get_user_from_supabase(token)


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
    return await _decode(creds.credentials)


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
