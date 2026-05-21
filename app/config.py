from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    # NVIDIA NIM (active provider on feature/nvidia-nim-provider branch)
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_BASE_URL: str = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")

    # AWS Bedrock (active on main branch)
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = os.getenv("AWS_REGION", "ap-south-1")

    # Shared model IDs (value differs per branch via .env)
    TUTOR_MODEL_ID: str = os.getenv("TUTOR_MODEL_ID")
    GRADER_MODEL_ID: str = os.getenv("GRADER_MODEL_ID")
    PLAGIARISM_MODEL_ID: str = os.getenv("PLAGIARISM_MODEL_ID")
    IMAGE_MODEL_ID: str = os.getenv("IMAGE_MODEL_ID", "qwen/qwen-image")
    VISION_MODEL_ID: str = os.getenv("VISION_MODEL_ID", "meta/llama-3.2-90b-vision-instruct")

    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME: str = os.getenv("DB_NAME", "eduguard")

    MINIMAX_API_KEY: str = os.getenv("MINIMAX_API_KEY", "")
    MINIMAX_IMAGE_MODEL: str = os.getenv("MINIMAX_IMAGE_MODEL", "image-01")

    DOCUMENT_STORAGE_DIR: str = os.getenv("DOCUMENT_STORAGE_DIR", "storage/documents")
    MAX_DOCUMENT_SIZE_MB: int = int(os.getenv("MAX_DOCUMENT_SIZE_MB", "25"))

    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

    # Vertex AI / Google Cloud (PYQ feature)
    GOOGLE_APPLICATION_CREDENTIALS_JSON: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON", "")
    VERTEX_AI_PROJECT: str = os.getenv("VERTEX_AI_PROJECT", "")
    VERTEX_AI_LOCATION: str = os.getenv("VERTEX_AI_LOCATION", "us-central1")
    VERTEX_AI_MODEL: str = os.getenv("VERTEX_AI_MODEL", "gemini-1.5-flash-001")
    PYQ_SESSIONS_DIR: str = os.getenv("PYQ_SESSIONS_DIR", "data/pyq_sessions")

settings = Settings()
