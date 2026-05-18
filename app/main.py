from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.tutor import router as tutor_router
from app.routes.exam import router as exam_router
from app.routes.image import router as image_router
from app.db.mongo import get_recent_violations, get_exam_submissions

app = FastAPI(
    title="EduGuard AI",
    description="Guardrail-Enforced AI Safety Platform for Education",
    version="1.0.0"
)

# Allow requests from React dev server (5173) and any local origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tutor_router)
app.include_router(exam_router)
app.include_router(image_router)


@app.get("/")
def root():
    return {
        "app": "EduGuard AI",
        "version": "1.0.0",
        "endpoints": ["/tutor/ask", "/exam/validate", "/images/concept", "/docs"]
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
