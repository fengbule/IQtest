from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class QuestionOut(BaseModel):
    id: int
    order_no: int
    category: str
    difficulty: str
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
    time_spent_seconds: int = Field(default=0, ge=0, le=600)


class SubmitAttemptIn(BaseModel):
    answers: list[AnswerIn]
    duration_seconds: int = Field(ge=0, le=7200)


class DimensionBreakdownOut(BaseModel):
    key: str
    label: str
    correct: int
    total: int
    accuracy: float
    score: int
    level: str
    level_label: str
    description: str
    advice: str


class AnswerReviewOut(BaseModel):
    question_order: int
    prompt: str
    dimension: str
    difficulty: str
    selected_option: str | None
    correct_option: str
    is_correct: bool
    time_spent_seconds: int
    explanation: str | None


class ScoreFactorsOut(BaseModel):
    accuracy_score: float
    difficulty_score: float
    completion_score: float
    response_quality_score: float


class ResultOut(BaseModel):
    attempt_id: int
    total_questions: int
    answered_count: int
    correct_count: int
    cpi_score: int
    estimated_iq: int
    ability_level: str
    ability_label: str
    percentile: int
    iq_range: str
    validity_flag: str
    validity_label: str
    validity_note: str
    summary: str
    interpretation: str
    duration_seconds: int
    disclaimer: str
    score_factors: ScoreFactorsOut
    dimension_breakdown: list[DimensionBreakdownOut]
    answer_review: list[AnswerReviewOut]


class AdminLoginIn(BaseModel):
    username: str
    password: str


class AdminLoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AttemptSummaryOut(BaseModel):
    attempt_id: int
    nickname: str
    submitted_at: str | None
    duration_seconds: int
    cpi_score: int
    estimated_iq: int
    ability_level: str
    ability_label: str
    percentile: int
    validity_flag: str
    validity_label: str
    iq_range: str


class AttemptListOut(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[AttemptSummaryOut]


class DashboardStatsOut(BaseModel):
    total_attempts: int
    completed_attempts: int
    average_cpi_score: float
    average_completion_score: float
    valid_attempt_rate: float
    dimension_accuracy: dict[str, float]
    recent_results: list[AttemptSummaryOut]


class AttemptDetailOut(ResultOut):
    nickname: str
    email: str | None
    started_at: str
    submitted_at: str


# Personality Test Schemas

class PersonalityQuestionOut(BaseModel):
    id: int
    question: str
    dimension: str


class PersonalityStartOut(BaseModel):
    attempt_id: int
    started_at: str
    questions: list[PersonalityQuestionOut]
    note: str


class PersonalityAnswerIn(BaseModel):
    question_id: int
    score: int = Field(ge=1, le=5)


class PersonalitySubmitIn(BaseModel):
    answers: list[PersonalityAnswerIn]
    duration_seconds: int = Field(ge=0, le=1200)


class HistoricalFigureOut(BaseModel):
    id: int
    name: str
    dynasty: str
    title: str
    description: str
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float


class PersonalityMatchOut(BaseModel):
    figure_id: int
    name: str
    dynasty: str
    title: str
    description: str
    similarity: float


class DimensionScoreOut(BaseModel):
    dimension: str
    name: str
    score: float
    level: str
    description: str


class PersonalityResultOut(BaseModel):
    attempt_id: int
    duration_seconds: int
    submitted_at: str | None
    openness_score: float
    conscientiousness_score: float
    extraversion_score: float
    agreeableness_score: float
    neuroticism_score: float
    dimension_breakdown: list[DimensionScoreOut]
    top_match: PersonalityMatchOut
    second_match: PersonalityMatchOut
    third_match: PersonalityMatchOut
    summary: str


class PersonalityAttemptSummaryOut(BaseModel):
    attempt_id: int
    nickname: str
    submitted_at: str | None
    duration_seconds: int
    top_match_name: str
    top_match_similarity: float


class PersonalityAttemptListOut(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[PersonalityAttemptSummaryOut]
