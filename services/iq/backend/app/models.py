from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class AdminUser(Base):
    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_no: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    difficulty_weight: Mapped[float] = mapped_column(Float, default=1.2)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    option_a: Mapped[str] = mapped_column(Text, nullable=False)
    option_b: Mapped[str] = mapped_column(Text, nullable=False)
    option_c: Mapped[str] = mapped_column(Text, nullable=False)
    option_d: Mapped[str] = mapped_column(Text, nullable=False)
    correct_option: Mapped[str] = mapped_column(String(1), nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_seconds: Mapped[int] = mapped_column(Integer, default=35)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class TestAttempt(Base):
    __tablename__ = "test_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nickname: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    total_questions: Mapped[int] = mapped_column(Integer, default=0)
    answered_count: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    accuracy_score: Mapped[float] = mapped_column(Float, default=0.0)
    difficulty_score: Mapped[float] = mapped_column(Float, default=0.0)
    completion_score: Mapped[float] = mapped_column(Float, default=0.0)
    response_quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    cpi_score: Mapped[int] = mapped_column(Integer, default=40)
    estimated_iq: Mapped[int] = mapped_column(Integer, default=100)
    percentile: Mapped[int] = mapped_column(Integer, default=10)
    ability_level: Mapped[str] = mapped_column(String(4), default="E")
    iq_range: Mapped[str] = mapped_column(String(32), default="90 以下参考区间")
    validity_flag: Mapped[str] = mapped_column(String(16), default="low")
    validity_note: Mapped[str] = mapped_column(Text, default="")
    summary: Mapped[str] = mapped_column(Text, default="")
    interpretation: Mapped[str] = mapped_column(Text, default="")
    math_score: Mapped[float] = mapped_column(Float, default=0.0)
    logic_score: Mapped[float] = mapped_column(Float, default=0.0)
    verbal_score: Mapped[float] = mapped_column(Float, default=0.0)
    spatial_score: Mapped[float] = mapped_column(Float, default=0.0)
    client_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)

    answers: Mapped[list["AttemptAnswer"]] = relationship(
        "AttemptAnswer",
        back_populates="attempt",
        cascade="all, delete-orphan",
        order_by="AttemptAnswer.question_order",
    )


class AttemptAnswer(Base):
    __tablename__ = "attempt_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("test_attempts.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    question_order: Mapped[int] = mapped_column(Integer, default=0)
    question_dimension: Mapped[str] = mapped_column(String(50), default="")
    question_difficulty: Mapped[str] = mapped_column(String(20), default="medium")
    question_weight: Mapped[float] = mapped_column(Float, default=1.2)
    estimated_seconds: Mapped[int] = mapped_column(Integer, default=35)
    prompt_snapshot: Mapped[str] = mapped_column(Text, default="")
    selected_option: Mapped[str | None] = mapped_column(String(1), nullable=True)
    correct_answer_snapshot: Mapped[str] = mapped_column(String(1), default="")
    explanation_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)
    time_spent_seconds: Mapped[int] = mapped_column(Integer, default=0)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)

    attempt: Mapped[TestAttempt] = relationship("TestAttempt", back_populates="answers")


class PersonalityQuestion(Base):
    __tablename__ = "personality_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    dimension: Mapped[str] = mapped_column(String(50), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    is_reverse: Mapped[bool] = mapped_column(Boolean, default=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)


class PersonalityAttempt(Base):
    __tablename__ = "personality_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nickname: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    
    # 五大人格维度得分（0-100）
    openness_score: Mapped[float] = mapped_column(Float, default=0.0)
    conscientiousness_score: Mapped[float] = mapped_column(Float, default=0.0)
    extraversion_score: Mapped[float] = mapped_column(Float, default=0.0)
    agreeableness_score: Mapped[float] = mapped_column(Float, default=0.0)
    neuroticism_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    # 匹配的历史人物
    top_match_id: Mapped[int] = mapped_column(Integer, nullable=True)
    top_match_similarity: Mapped[float] = mapped_column(Float, default=0.0)
    second_match_id: Mapped[int] = mapped_column(Integer, nullable=True)
    second_match_similarity: Mapped[float] = mapped_column(Float, default=0.0)
    third_match_id: Mapped[int] = mapped_column(Integer, nullable=True)
    third_match_similarity: Mapped[float] = mapped_column(Float, default=0.0)
    
    summary: Mapped[str] = mapped_column(Text, default="")
    client_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)

    answers: Mapped[list["PersonalityAnswer"]] = relationship(
        "PersonalityAnswer",
        back_populates="attempt",
        cascade="all, delete-orphan",
    )


class PersonalityAnswer(Base):
    __tablename__ = "personality_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("personality_attempts.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("personality_questions.id"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5

    attempt: Mapped[PersonalityAttempt] = relationship("PersonalityAttempt", back_populates="answers")


class DynastyAttempt(Base):
    __tablename__ = "dynasty_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    dynasty_id: Mapped[str] = mapped_column(String(50), nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    
    # Top 3 匹配结果
    top_match_id: Mapped[str] = mapped_column(String(50), nullable=True)
    top_match_similarity: Mapped[float] = mapped_column(Float, default=0.0)
    second_match_id: Mapped[str] = mapped_column(String(50), nullable=True)
    second_match_similarity: Mapped[float] = mapped_column(Float, default=0.0)
    third_match_id: Mapped[str] = mapped_column(String(50), nullable=True)
    third_match_similarity: Mapped[float] = mapped_column(Float, default=0.0)
    
    # 原型匹配结果
    dominant_prototype_id: Mapped[str] = mapped_column(String(50), nullable=True)
    dominant_prototype_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    summary: Mapped[str] = mapped_column(Text, default="")
    client_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)

    answers: Mapped[list["DynastyAnswer"]] = relationship(
        "DynastyAnswer",
        back_populates="attempt",
        cascade="all, delete-orphan",
    )


class DynastyAnswer(Base):
    __tablename__ = "dynasty_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("dynasty_attempts.id"), nullable=False)
    question_id: Mapped[str] = mapped_column(String(20), nullable=False)  # e.g., "tk_q01"
    selected_option_id: Mapped[str] = mapped_column(String(1), nullable=False)  # "A", "B", "C", "D"

    attempt: Mapped[DynastyAttempt] = relationship("DynastyAttempt", back_populates="answers")


class FunQuizDefinition(Base):
    __tablename__ = "fun_quiz_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    subtitle: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_image: Mapped[str | None] = mapped_column(String(255), nullable=True)
    theme_color: Mapped[str | None] = mapped_column(String(32), nullable=True)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=2)
    play_style: Mapped[str] = mapped_column(String(32), default="quick")
    scoring_mode: Mapped[str] = mapped_column(String(32), default="archetype_sum")
    question_count: Mapped[int] = mapped_column(Integer, default=0)
    result_count: Mapped[int] = mapped_column(Integer, default=0)
    disclaimer: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    questions: Mapped[list["FunQuizQuestion"]] = relationship(
        "FunQuizQuestion",
        back_populates="quiz",
        cascade="all, delete-orphan",
    )
    results: Mapped[list["FunQuizResult"]] = relationship(
        "FunQuizResult",
        back_populates="quiz",
        cascade="all, delete-orphan",
    )
    attempts: Mapped[list["FunQuizAttempt"]] = relationship(
        "FunQuizAttempt",
        back_populates="quiz",
    )


class FunQuizQuestion(Base):
    __tablename__ = "fun_quiz_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("fun_quiz_definitions.id"), nullable=False)
    question_key: Mapped[str] = mapped_column(String(50), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_subtext: Mapped[str | None] = mapped_column(String(255), nullable=True)
    question_type: Mapped[str] = mapped_column(String(32), default="single_choice")
    scene_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dimension_key: Mapped[str | None] = mapped_column(String(50), nullable=True)
    option_payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    quiz: Mapped[FunQuizDefinition] = relationship("FunQuizDefinition", back_populates="questions")
    answers: Mapped[list["FunQuizAnswer"]] = relationship(
        "FunQuizAnswer",
        back_populates="question",
        cascade="all, delete-orphan",
    )


class FunQuizResult(Base):
    __tablename__ = "fun_quiz_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("fun_quiz_definitions.id"), nullable=False)
    result_key: Mapped[str] = mapped_column(String(50), nullable=False)
    result_name: Mapped[str] = mapped_column(String(100), nullable=False)
    result_subtitle: Mapped[str | None] = mapped_column(String(255), nullable=True)
    result_summary: Mapped[str] = mapped_column(Text, default="")
    result_long_desc: Mapped[str | None] = mapped_column(Text, nullable=True)
    poster_image: Mapped[str | None] = mapped_column(String(255), nullable=True)
    share_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    share_subtitle: Mapped[str | None] = mapped_column(String(255), nullable=True)
    extra_payload_json: Mapped[str] = mapped_column(Text, default="{}")

    quiz: Mapped[FunQuizDefinition] = relationship("FunQuizDefinition", back_populates="results")


class FunQuizAttempt(Base):
    __tablename__ = "fun_quiz_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("fun_quiz_definitions.id"), nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    top_result_key: Mapped[str | None] = mapped_column(String(50), nullable=True)
    secondary_result_key: Mapped[str | None] = mapped_column(String(50), nullable=True)
    score_payload_json: Mapped[str] = mapped_column(Text, default="{}")
    client_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)

    quiz: Mapped[FunQuizDefinition] = relationship("FunQuizDefinition", back_populates="attempts")
    answers: Mapped[list["FunQuizAnswer"]] = relationship(
        "FunQuizAnswer",
        back_populates="attempt",
        cascade="all, delete-orphan",
    )


class FunQuizAnswer(Base):
    __tablename__ = "fun_quiz_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("fun_quiz_attempts.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("fun_quiz_questions.id"), nullable=False)
    selected_value: Mapped[str] = mapped_column(String(10), nullable=False)
    selected_label: Mapped[str] = mapped_column(String(255), nullable=False)
    score_payload_json: Mapped[str] = mapped_column(Text, default="{}")

    attempt: Mapped[FunQuizAttempt] = relationship("FunQuizAttempt", back_populates="answers")
    question: Mapped[FunQuizQuestion] = relationship("FunQuizQuestion", back_populates="answers")
