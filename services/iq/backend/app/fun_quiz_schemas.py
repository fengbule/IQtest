from __future__ import annotations

from pydantic import BaseModel, Field


class FunQuizListItemOut(BaseModel):
    slug: str
    title: str
    subtitle: str | None = None
    cover_image: str | None = None
    theme_color: str | None = None
    estimated_minutes: int
    play_style: str
    question_count: int


class FunQuizDetailOut(BaseModel):
    slug: str
    title: str
    subtitle: str | None = None
    description: str | None = None
    cover_image: str | None = None
    theme_color: str | None = None
    estimated_minutes: int
    play_style: str
    scoring_mode: str
    question_count: int
    disclaimer: str | None = None


class FunQuizOptionOut(BaseModel):
    value: str
    label: str


class FunQuizQuestionOut(BaseModel):
    id: str
    order_no: int
    type: str
    text: str
    subtext: str | None = None
    options: list[FunQuizOptionOut]


class FunQuizStartOut(BaseModel):
    attempt_id: int
    started_at: str
    questions: list[FunQuizQuestionOut]
    note: str


class FunQuizAnswerIn(BaseModel):
    question_id: str
    selected_value: str


class FunQuizSubmitIn(BaseModel):
    duration_seconds: int
    answers: list[FunQuizAnswerIn]


class FunQuizResultCardOut(BaseModel):
    key: str
    name: str
    subtitle: str | None = None
    summary: str
    long_desc: str | None = None
    poster_image: str | None = None
    share_title: str | None = None
    share_subtitle: str | None = None
    extra: dict | None = None


class FunQuizDimensionOut(BaseModel):
    key: str
    name: str
    score: float


class FunQuizSubmitOut(BaseModel):
    attempt_id: int
    submitted_at: str
    duration_seconds: int
    quiz_slug: str
    primary_result: FunQuizResultCardOut
    secondary_result: FunQuizResultCardOut | None = None
    dimension_breakdown: list[FunQuizDimensionOut] = []
    score_payload: dict = {}
    disclaimer: str


class FunQuizAttemptSummaryOut(BaseModel):
    attempt_id: int
    quiz_slug: str
    quiz_title: str
    nickname: str
    submitted_at: str | None = None
    duration_seconds: int
    primary_result_key: str | None = None
    primary_result_name: str | None = None


class FunQuizAttemptListOut(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[FunQuizAttemptSummaryOut]