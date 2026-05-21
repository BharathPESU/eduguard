from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.tutor import router as tutor_router
from app.routes.exam import router as exam_router
from app.routes.image import router as image_router
from app.routes.documents import router as documents_router
from app.routes.auth import router as auth_router
from app.routes.pyq import router as pyq_router, pyq_startup
from app.db.mongo import get_recent_violations, get_exam_submissions


@asynccontextmanager
async def lifespan(app: FastAPI):
    await pyq_startup()   # create indexes + sync disk sessions → MongoDB
    yield

app = FastAPI(
    title="EduGuard AI",
    description="Guardrail-Enforced AI Safety Platform for Education",
    version="1.0.0",
    lifespan=lifespan,
)

import os

# Build allowed origins: always include localhost for dev,
# plus the deployed frontend URL from env (set on Cloud Run).
_frontend_url = os.getenv("FRONTEND_URL", "")
_allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
if _frontend_url and _frontend_url not in _allowed_origins:
    _allowed_origins.append(_frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_origin_regex=r"https://.*\.run\.app",   # allow ALL Cloud Run services
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tutor_router)
app.include_router(exam_router)
app.include_router(image_router)
app.include_router(documents_router)
app.include_router(auth_router)
app.include_router(pyq_router)


@app.get("/")
def root():
    return {
        "app": "EduGuard AI",
        "version": "1.0.0",
        "endpoints": [
            "/tutor/ask",
            "/exam/validate",
            "/images/concept",
            "/documents/upload",
            "/auth/signup",
            "/auth/login",
            "/auth/google",
            "/docs",
        ]
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/dashboard/violations")
async def dashboard_violations():
    return await get_recent_violations(limit=50)


@app.get("/dashboard/submissions")
async def dashboard_submissions():
    return await get_exam_submissions(limit=50)
