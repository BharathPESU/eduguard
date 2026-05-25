from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.auth.dependencies import require_teacher
from app.config import settings
from app.limiter import limiter
from app.db.mongo import get_exam_submissions, get_recent_violations
from app.routes.auth import router as auth_router
from app.routes.documents import router as documents_router
from app.routes.exam import router as exam_router
from app.routes.image import router as image_router
from app.routes.pyq import pyq_startup
from app.routes.pyq import router as pyq_router
from app.routes.tutor import router as tutor_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await pyq_startup()   # create indexes + sync disk sessions → MongoDB
    yield


# ── App factory ────────────────────────────────────────────────────────────
_is_production = settings.APP_ENV == "production"

app = FastAPI(
    title="EduGuard AI",
    description="Guardrail-Enforced AI Safety Platform for Education",
    version="1.1.0",
    lifespan=lifespan,
    # Hide interactive docs in production — reduces attack surface
    docs_url=None if _is_production else "/docs",
    redoc_url=None if _is_production else "/redoc",
    openapi_url=None if _is_production else "/openapi.json",
)

# ── Attach rate-limiter state and handler ──────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS — explicit allowlist only, no wildcard regex ─────────────────────
_allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
if settings.FRONTEND_URL and settings.FRONTEND_URL not in _allowed_origins:
    _allowed_origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# ── Routers ────────────────────────────────────────────────────────────────
app.include_router(tutor_router)
app.include_router(exam_router)
app.include_router(image_router)
app.include_router(documents_router)
app.include_router(auth_router)
app.include_router(pyq_router)


# ── Public utility endpoints ───────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "app": "EduGuard AI",
        "version": "1.1.0",
        "endpoints": [
            "/tutor/ask",
            "/exam/validate",
            "/images/concept",
            "/documents/upload",
            "/auth/signup",
            "/auth/login",
            "/auth/google",
        ],
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


# ── Dashboard — teacher-only, authenticated ────────────────────────────────
@app.get("/dashboard/violations")
async def dashboard_violations(user: dict = Depends(require_teacher)):
    return await get_recent_violations(limit=50)


@app.get("/dashboard/submissions")
async def dashboard_submissions(user: dict = Depends(require_teacher)):
    return await get_exam_submissions(limit=50)
