from pydantic import BaseModel, Field
from typing import Optional

class TutorRequest(BaseModel):
    student_id: str = Field(..., example="STU_001")
    question: str = Field(..., min_length=5, max_length=2000)
    subject: Optional[str] = Field(default="General", example="Physics")
    grade_level: Optional[str] = Field(default="10", example="10")

class ExamRequest(BaseModel):
    student_id: str = Field(..., example="STU_001")
    exam_id: str = Field(..., example="EXAM_PHY_001")
    question: str = Field(..., min_length=5, max_length=2000)
    rubric: str = Field(..., min_length=10, max_length=2000)
    student_answer: str = Field(..., min_length=1, max_length=5000)
    grade_level: Optional[str] = Field(default="10", example="10")