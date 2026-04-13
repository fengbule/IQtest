from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class QuestionOut(BaseModel):
    id: int
    order_no: int
    category: str
    difficulty: int
    prompt: str
    options: dict[str, str]


class StartAttemptIn(BaseModel):
    nickname: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = None


class StartAttemptOut(BaseModel):
    attempt_id: int
    started_at: str
    time_limit_seconds: int
    questions: list[QuestionOut]
    note: str


class AnswerIn(BaseModel):
    question_id: int
    selected_option: Literal["A", "B", "C", "D"] | None = None


class SubmitAttemptIn(BaseModel):
    answers: list[AnswerIn]
    duration_seconds: int = Field(ge=0, le=7200)


class AnswerReviewOut(BaseModel):
    question_id: int
    selected_option: str | None
    correct_option: str
    is_correct: bool
    explanation: str | None


class ResultOut(BaseModel):
    attempt_id: int
    total_questions: int
    correct_count: int
    raw_score: float
    normalized_score: float
    estimated_iq: int
    percentile: int
    interpretation: str
    duration_seconds: int
    disclaimer: str
    category_breakdown: dict[str, dict[str, float]]
    answer_review: list[AnswerReviewOut]


class AdminLoginIn(BaseModel):
    username: str
    password: str


class AdminLoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class DashboardStatsOut(BaseModel):
    total_attempts: int
    completed_attempts: int
    average_estimated_iq: float
    average_duration_seconds: float
    average_accuracy: float
    category_accuracy: dict[str, float]
    recent_results: list[dict]
