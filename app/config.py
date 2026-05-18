from dotenv import load_dotenv
import os

load_dotenv()

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

    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME: str = os.getenv("DB_NAME", "eduguard")

    MINIMAX_API_KEY: str = os.getenv("MINIMAX_API_KEY", "")
    MINIMAX_IMAGE_MODEL: str = os.getenv("MINIMAX_IMAGE_MODEL", "image-01")

settings = Settings()
