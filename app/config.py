from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")

    TUTOR_MODEL_ID: str = os.getenv("TUTOR_MODEL_ID")
    GRADER_MODEL_ID: str = os.getenv("GRADER_MODEL_ID")
    PLAGIARISM_MODEL_ID: str = os.getenv("PLAGIARISM_MODEL_ID")

    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME: str = os.getenv("DB_NAME", "eduguard")

settings = Settings()