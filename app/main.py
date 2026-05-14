from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.tutor import router as tutor_router
from app.routes.exam import router as exam_router

app = FastAPI(
    title="EduGuard AI",
    description="Guardrail-Enforced AI Safety Platform for Education",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tutor_router)
app.include_router(exam_router)

@app.get("/")
def root():
    return {
        "app": "EduGuard AI",
        "version": "1.0.0",
        "endpoints": ["/tutor/ask", "/exam/validate", "/docs"]
    }

@app.get("/health")
def health():
    return {"status": "healthy"}