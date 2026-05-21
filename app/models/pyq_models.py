from pydantic import BaseModel
from typing import Optional


class PYQUploadResponse(BaseModel):
    session_id: str
    filename: str
    subject: str
    year: str
    total_questions: int
    created_at: str


class PYQQuestionRequest(BaseModel):
    session_id: str
    question_number: int


class PYQAnswerRequest(BaseModel):
    session_id: str
    question_number: int
