from __future__ import annotations

import csv
import io
import os
from datetime import date, datetime, time
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine, get_db
from .dimension_mapping import normalize_dimension
from .migrations import apply_lightweight_migrations
from .models import AdminUser, AttemptAnswer, Question, TestAttempt, PersonalityQuestion, PersonalityAttempt, PersonalityAnswer
from .question_selector import DIMENSIONS, QUESTION_PLAN, TIME_LIMIT_SECONDS, sample_questions
from .schemas import (
    AdminLoginIn,
    AdminLoginOut,
    AttemptDetailOut,
    AttemptListOut,
    AttemptSummaryOut,
    DashboardStatsOut,
    QuestionOut,
    ResultOut,
    ScoreFactorsOut,
    StartAttemptIn,
    StartAttemptOut,
    SubmitAttemptIn,
    PersonalityQuestionOut,
    PersonalityStartOut,
    PersonalitySubmitIn,
    PersonalityResultOut,
    PersonalityAttemptListOut,
    PersonalityAttemptSummaryOut,
)
from .scoring import (
    CATEGORY_LABELS,
    DIFFICULTY_LABELS,
    ability_from_cpi,
    score_attempt,
)
from .security import create_access_token, decode_access_token, verify_password
from .seed import seed_admin, seed_questions, seed_personality_questions
from .personality_scorer import calculate_personality_scores, find_top_matches, get_dimension_interpretation, generate_summary
from .personality_data import HISTORICAL_FIGURES


VALIDITY_LABELS = {
    "high": "高可信度",
    "medium": "中可信度",
    "low": "低可信度",
}

FRONTEND_ASSET_VERSION = "20260415-4"
RECENT_ATTEMPT_LOOKBACK = 3


def resolve_frontend_dir() -> Path:
    candidates = []
    env_path = os.getenv("FRONTEND_DIR")
    if env_path:
        candidates.append(Path(env_path))
    candidates.append(Path("/app/frontend"))
    candidates.append(Path(__file__).resolve().parents[2] / "frontend")

    checked = []
    for candidate in candidates:
        resolved = candidate.resolve()
        checked.append(str(resolved))
        if resolved.exists():
            return resolved

    raise RuntimeError(
        "Frontend directory does not exist. Checked: "
        + ", ".join(checked)
        + ". Set FRONTEND_DIR or ensure the Docker image copies files into /app/frontend."
    )


FRONTEND_DIR = resolve_frontend_dir()


class FrontendStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        if response.status_code < 400:
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

app = FastAPI(title="IQ Assessment Project", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    Base.metadata.create_all(bind=engine)
    apply_lightweight_migrations(engine)
    db = SessionLocal()
    try:
        seed_admin(db)
        seed_questions(db)
        seed_personality_questions(db)
    finally:
        db.close()


@app.get("/", include_in_schema=False)
def index_redirect():
    return RedirectResponse(url="/portal.html")


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "iq-app", "time": datetime.utcnow().isoformat()}


@app.get("/api/public/info")
def public_info(db: Session = Depends(get_db)):
    return {
        "title": "在线智力检测平台",
        "time_limit_seconds": TIME_LIMIT_SECONDS,
        "question_count": len(DIMENSIONS) * sum(QUESTION_PLAN.values()),
        "question_pool_count": db.query(Question).filter(Question.is_active.is_(True)).count(),
        "asset_version": FRONTEND_ASSET_VERSION,
        "notice": "本项目展示的是基于站内题库的综合认知表现，不等同于正式标准化 IQ 测验。",
    }


def serialize_attempt_summary(attempt: TestAttempt) -> AttemptSummaryOut:
    ability = ability_from_cpi(attempt.cpi_score)
    return AttemptSummaryOut(
        attempt_id=attempt.id,
        nickname=attempt.nickname or "匿名用户",
        submitted_at=attempt.submitted_at.isoformat() if attempt.submitted_at else None,
        duration_seconds=attempt.duration_seconds,
        cpi_score=attempt.cpi_score,
        estimated_iq=attempt.estimated_iq,
        ability_level=attempt.ability_level,
        ability_label=ability["label"],
        percentile=attempt.percentile,
        validity_flag=attempt.validity_flag,
        validity_label=VALIDITY_LABELS.get(attempt.validity_flag, "低可信度"),
        iq_range=attempt.iq_range,
    )


def build_result_payload(attempt: TestAttempt, answer_rows: list[AttemptAnswer]) -> ResultOut:
    derived = score_attempt(answer_rows, attempt.duration_seconds)
    ability = ability_from_cpi(attempt.cpi_score)
    return ResultOut(
        attempt_id=attempt.id,
        total_questions=attempt.total_questions,
        answered_count=attempt.answered_count,
        correct_count=attempt.correct_count,
        cpi_score=attempt.cpi_score,
        estimated_iq=attempt.estimated_iq,
        ability_level=attempt.ability_level,
        ability_label=ability["label"],
        percentile=attempt.percentile,
        iq_range=attempt.iq_range,
        validity_flag=attempt.validity_flag,
        validity_label=VALIDITY_LABELS.get(attempt.validity_flag, "低可信度"),
        validity_note=attempt.validity_note,
        summary=attempt.summary,
        interpretation=attempt.interpretation,
        duration_seconds=attempt.duration_seconds,
        disclaimer=derived["disclaimer"],
        score_factors=ScoreFactorsOut(
            accuracy_score=attempt.accuracy_score,
            difficulty_score=attempt.difficulty_score,
            completion_score=attempt.completion_score,
            response_quality_score=attempt.response_quality_score,
        ),
        dimension_breakdown=derived["dimension_breakdown"],
        answer_review=derived["answer_review"],
    )


def build_attempt_detail(attempt: TestAttempt) -> AttemptDetailOut:
    payload = build_result_payload(attempt, attempt.answers).model_dump()
    payload.update(
        {
            "nickname": attempt.nickname or "匿名用户",
            "email": attempt.email,
            "started_at": attempt.started_at.isoformat(),
            "submitted_at": attempt.submitted_at.isoformat() if attempt.submitted_at else "",
        }
    )
    return AttemptDetailOut(**payload)


def query_attempts(
    db: Session,
    keyword: str | None = None,
    level: str | None = None,
    validity: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
):
    query = db.query(TestAttempt).filter(TestAttempt.submitted_at.is_not(None))
    if keyword:
        like_value = f"%{keyword.strip()}%"
        query = query.filter(
            or_(TestAttempt.nickname.like(like_value), TestAttempt.email.like(like_value))
        )
    if level:
        query = query.filter(TestAttempt.ability_level == level.upper())
    if validity:
        query = query.filter(TestAttempt.validity_flag == validity.lower())
    if date_from:
        query = query.filter(TestAttempt.submitted_at >= datetime.combine(date_from, time.min))
    if date_to:
        query = query.filter(TestAttempt.submitted_at <= datetime.combine(date_to, time.max))
    return query


def recent_question_ids_for_attempt(payload: StartAttemptIn, request: Request, db: Session) -> set[int]:
    email = str(payload.email).strip().lower() if payload.email else None
    nickname = payload.nickname.strip() if payload.nickname else None
    client_ip = request.client.host if request.client else None

    query = db.query(TestAttempt).filter(TestAttempt.submitted_at.is_not(None))
    if email:
        query = query.filter(TestAttempt.email == email)
    elif nickname and client_ip:
        query = query.filter(TestAttempt.nickname == nickname, TestAttempt.client_ip == client_ip)
    elif nickname:
        query = query.filter(TestAttempt.nickname == nickname)
    elif client_ip:
        query = query.filter(TestAttempt.client_ip == client_ip)
    else:
        return set()

    attempts = (
        query.order_by(TestAttempt.submitted_at.desc())
        .limit(RECENT_ATTEMPT_LOOKBACK)
        .all()
    )
    return {answer.question_id for attempt in attempts for answer in attempt.answers}


@app.post("/api/attempts/start", response_model=StartAttemptOut)
def start_attempt(payload: StartAttemptIn, request: Request, db: Session = Depends(get_db)):
    question_rows = db.query(Question).filter(Question.is_active.is_(True)).all()
    avoid_question_ids = recent_question_ids_for_attempt(payload, request, db)
    try:
        selected_questions = sample_questions(question_rows, avoid_question_ids=avoid_question_ids)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    attempt = TestAttempt(
        nickname=payload.nickname,
        email=str(payload.email) if payload.email else None,
        started_at=datetime.utcnow(),
        total_questions=len(selected_questions),
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", "")[:255],
    )
    db.add(attempt)
    db.flush()

    for display_order, question in enumerate(selected_questions, start=1):
        db.add(
            AttemptAnswer(
                attempt_id=attempt.id,
                question_id=question.id,
                question_order=display_order,
                question_dimension=normalize_dimension(question.category),
                question_difficulty=question.difficulty,
                question_weight=question.difficulty_weight,
                estimated_seconds=question.estimated_seconds,
                prompt_snapshot=question.prompt,
                correct_answer_snapshot=question.correct_option,
                explanation_snapshot=question.explanation,
            )
        )

    db.commit()
    db.refresh(attempt)

    question_payload = [
        QuestionOut(
            id=question.id,
            order_no=index,
            category=CATEGORY_LABELS.get(
                normalize_dimension(question.category),
                normalize_dimension(question.category),
            ),
            difficulty=DIFFICULTY_LABELS.get(question.difficulty, question.difficulty),
            prompt=question.prompt,
            options={
                "A": question.option_a,
                "B": question.option_b,
                "C": question.option_c,
                "D": question.option_d,
            },
        )
        for index, question in enumerate(selected_questions, start=1)
    ]
    return StartAttemptOut(
        attempt_id=attempt.id,
        started_at=attempt.started_at.isoformat(),
        time_limit_seconds=TIME_LIMIT_SECONDS,
        questions=question_payload,
        note="本次将从题库中随机抽取 32 题，并优先避开你最近测过的题目；结果会综合正确率、题目难度、完整度与作答质量生成。",
    )


@app.post("/api/attempts/{attempt_id}/submit", response_model=ResultOut)
def submit_attempt(attempt_id: int, payload: SubmitAttemptIn, db: Session = Depends(get_db)):
    attempt = db.query(TestAttempt).filter(TestAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="attempt not found")
    if attempt.submitted_at is not None:
        raise HTTPException(status_code=400, detail="attempt already submitted")

    answer_rows = list(attempt.answers)
    answer_map = {item.question_id: item for item in payload.answers}

    for row in answer_rows:
        submitted = answer_map.get(row.question_id)
        row.selected_option = submitted.selected_option if submitted else None
        row.time_spent_seconds = submitted.time_spent_seconds if submitted else 0
        row.is_correct = bool(row.selected_option) and row.selected_option == row.correct_answer_snapshot

    scoring = score_attempt(answer_rows, payload.duration_seconds)
    attempt.submitted_at = datetime.utcnow()
    attempt.duration_seconds = payload.duration_seconds
    attempt.answered_count = scoring["answered_count"]
    attempt.correct_count = scoring["correct_count"]
    attempt.accuracy_score = scoring["accuracy_score"]
    attempt.difficulty_score = scoring["difficulty_score"]
    attempt.completion_score = scoring["completion_score"]
    attempt.response_quality_score = scoring["response_quality_score"]
    attempt.cpi_score = scoring["cpi_score"]
    attempt.estimated_iq = scoring["estimated_iq"]
    attempt.percentile = scoring["percentile"]
    attempt.ability_level = scoring["ability_level"]
    attempt.iq_range = scoring["iq_range"]
    attempt.validity_flag = scoring["validity_flag"]
    attempt.validity_note = scoring["validity_note"]
    attempt.summary = scoring["summary"]
    attempt.interpretation = scoring["interpretation"]

    for field_name, value in scoring["stored_dimension_scores"].items():
        setattr(attempt, field_name, value)

    db.commit()
    db.refresh(attempt)
    return build_result_payload(attempt, answer_rows)


@app.get("/api/attempts/{attempt_id}/result", response_model=ResultOut)
def get_result(attempt_id: int, db: Session = Depends(get_db)):
    attempt = db.query(TestAttempt).filter(TestAttempt.id == attempt_id).first()
    if not attempt or attempt.submitted_at is None:
        raise HTTPException(status_code=404, detail="result not found")
    return build_result_payload(attempt, list(attempt.answers))


@app.post("/api/admin/login", response_model=AdminLoginOut)
def admin_login(payload: AdminLoginIn, db: Session = Depends(get_db)):
    admin = db.query(AdminUser).filter(AdminUser.username == payload.username).first()
    if not admin or not verify_password(payload.password, admin.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
    token = create_access_token(subject=admin.username)
    return AdminLoginOut(access_token=token)


def get_current_admin(authorization: Annotated[str | None, Header()] = None):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    token = authorization.split(" ", 1)[1]
    subject = decode_access_token(token)
    if not subject:
        raise HTTPException(status_code=401, detail="invalid token")
    return subject


@app.get("/api/admin/dashboard", response_model=DashboardStatsOut)
def admin_dashboard(_: str = Depends(get_current_admin), db: Session = Depends(get_db)):
    attempts = db.query(TestAttempt).all()
    completed = [item for item in attempts if item.submitted_at is not None]
    completed_count = len(completed)

    average_cpi_score = round(
        sum(item.cpi_score for item in completed) / completed_count, 2
    ) if completed_count else 0.0
    average_completion_score = round(
        (sum(item.completion_score for item in completed) / completed_count) * 100, 2
    ) if completed_count else 0.0
    valid_attempt_rate = round(
        (sum(1 for item in completed if item.validity_flag != "low") / completed_count) * 100,
        2,
    ) if completed_count else 0.0

    dimension_rollup = {label: [0, 0] for label in CATEGORY_LABELS.values()}
    for attempt in completed:
        for row in attempt.answers:
            dimension = normalize_dimension(row.question_dimension)
            label = CATEGORY_LABELS.get(dimension, dimension)
            dimension_rollup.setdefault(label, [0, 0])
            dimension_rollup[label][0] += int(row.is_correct)
            dimension_rollup[label][1] += 1

    dimension_accuracy = {
        label: round((correct / total) * 100, 2) if total else 0.0
        for label, (correct, total) in dimension_rollup.items()
    }

    recent_results = [
        serialize_attempt_summary(item)
        for item in sorted(completed, key=lambda row: row.submitted_at or datetime.min, reverse=True)[:20]
    ]

    return DashboardStatsOut(
        total_attempts=len(attempts),
        completed_attempts=completed_count,
        average_cpi_score=average_cpi_score,
        average_completion_score=average_completion_score,
        valid_attempt_rate=valid_attempt_rate,
        dimension_accuracy=dimension_accuracy,
        recent_results=recent_results,
    )


@app.get("/api/admin/attempts", response_model=AttemptListOut)
def list_attempts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str | None = None,
    level: str | None = None,
    validity: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    _: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    query = query_attempts(
        db,
        keyword=keyword,
        level=level,
        validity=validity,
        date_from=date_from,
        date_to=date_to,
    )
    total = query.count()
    rows = (
        query.order_by(TestAttempt.submitted_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return AttemptListOut(
        page=page,
        page_size=page_size,
        total=total,
        items=[serialize_attempt_summary(row) for row in rows],
    )


@app.get("/api/admin/attempts/export.csv")
def export_attempts(
    keyword: str | None = None,
    level: str | None = None,
    validity: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    _: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    rows = (
        query_attempts(
            db,
            keyword=keyword,
            level=level,
            validity=validity,
            date_from=date_from,
            date_to=date_to,
        )
        .order_by(TestAttempt.submitted_at.desc())
        .all()
    )

    buffer = io.StringIO()
    buffer.write("\ufeff")
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "attempt_id",
            "user_name",
            "submitted_at",
            "total_seconds",
            "answered_count",
            "correct_count",
            "cpi",
            "estimated_iq",
            "level",
            "percentile",
            "iq_range",
            "math_score",
            "logic_score",
            "verbal_score",
            "spatial_score",
            "validity_flag",
        ]
    )
    for row in rows:
        writer.writerow(
            [
                row.id,
                row.nickname or "匿名用户",
                row.submitted_at.isoformat() if row.submitted_at else "",
                row.duration_seconds,
                row.answered_count,
                row.correct_count,
                row.cpi_score,
                row.estimated_iq,
                row.ability_level,
                row.percentile,
                row.iq_range,
                row.math_score,
                row.logic_score,
                row.verbal_score,
                row.spatial_score,
                row.validity_flag,
            ]
        )

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=iq-attempts.csv"},
    )


@app.get("/api/admin/attempts/{attempt_id}", response_model=AttemptDetailOut)
def attempt_detail(attempt_id: int, _: str = Depends(get_current_admin), db: Session = Depends(get_db)):
    attempt = db.query(TestAttempt).filter(TestAttempt.id == attempt_id).first()
    if not attempt or attempt.submitted_at is None:
        raise HTTPException(status_code=404, detail="attempt not found")
    return build_attempt_detail(attempt)


# ===== Personality Test API Routes =====

@app.post("/api/personality/attempts", response_model=PersonalityStartOut)
def start_personality_attempt(payload: StartAttemptIn, request: Request, db: Session = Depends(get_db)):
    """Start a new personality test"""
    # Create new attempt
    attempt = PersonalityAttempt(
        nickname=payload.nickname,
        email=payload.email,
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(attempt)
    db.flush()
    
    # Get all personality questions
    questions = db.query(PersonalityQuestion).order_by(PersonalityQuestion.position).all()
    
    question_payload = [
        PersonalityQuestionOut(
            id=q.id,
            question=q.question,
            dimension=q.dimension,
        )
        for q in questions
    ]
    
    db.commit()
    
    return PersonalityStartOut(
        attempt_id=attempt.id,
        started_at=attempt.started_at.isoformat(),
        questions=question_payload,
        note="请根据自己的实际情况回答以下问题，没有完全正确或完全错误的答案。此测评基于Big Five人格模型，会展示你与8位历史人物的相似度。",
    )


@app.post("/api/personality/attempts/{attempt_id}/submit", response_model=PersonalityResultOut)
def submit_personality_attempt(
    attempt_id: int,
    payload: PersonalitySubmitIn,
    db: Session = Depends(get_db)
):
    """Submit personality test and get results"""
    attempt = db.query(PersonalityAttempt).filter(PersonalityAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="attempt not found")
    if attempt.submitted_at is not None:
        raise HTTPException(status_code=400, detail="attempt already submitted")
    
    # Save answers
    answers_dict = {}
    for answer in payload.answers:
        pa = PersonalityAnswer(
            attempt_id=attempt.id,
            question_id=answer.question_id,
            score=answer.score,
        )
        db.add(pa)
        answers_dict[answer.question_id] = answer.score
    
    # Calculate scores
    scores = calculate_personality_scores(answers_dict)
    
    # Find top matches
    top_matches = find_top_matches(scores, limit=3)
    
    # Update attempt with results
    attempt.submitted_at = datetime.utcnow()
    attempt.duration_seconds = payload.duration_seconds
    attempt.openness_score = scores["openness"]
    attempt.conscientiousness_score = scores["conscientiousness"]
    attempt.extraversion_score = scores["extraversion"]
    attempt.agreeableness_score = scores["agreeableness"]
    attempt.neuroticism_score = scores["neuroticism"]
    
    if top_matches:
        attempt.top_match_id = top_matches[0]["figure_id"]
        attempt.top_match_similarity = top_matches[0]["similarity"]
    if len(top_matches) > 1:
        attempt.second_match_id = top_matches[1]["figure_id"]
        attempt.second_match_similarity = top_matches[1]["similarity"]
    if len(top_matches) > 2:
        attempt.third_match_id = top_matches[2]["figure_id"]
        attempt.third_match_similarity = top_matches[2]["similarity"]
    
    attempt.summary = generate_summary(scores, top_matches)
    
    db.commit()
    
    # Build response
    dimensions = []
    for dim_key in ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]:
        dim_interp = get_dimension_interpretation(dim_key, scores[dim_key])
        from .schemas import DimensionScoreOut
        dimensions.append(DimensionScoreOut(**dim_interp))
    
    def get_figure(figure_id):
        for fig in HISTORICAL_FIGURES:
            if fig["id"] == figure_id:
                return fig
        return None
    
    # Build match figures
    match_figures = []
    for i, match in enumerate(top_matches):
        fig = get_figure(match["figure_id"])
        if fig:
            from .schemas import PersonalityMatchOut
            match_figures.append(PersonalityMatchOut(
                figure_id=fig["id"],
                name=fig["name"],
                dynasty=fig["dynasty"],
                title=fig["title"],
                description=fig["description"],
                similarity=match["similarity"],
            ))
    
    # Ensure we have at least 3 matches
    while len(match_figures) < 3:
        match_figures.append(match_figures[-1] if match_figures else None)
    
    return PersonalityResultOut(
        attempt_id=attempt.id,
        duration_seconds=attempt.duration_seconds,
        submitted_at=attempt.submitted_at.isoformat() if attempt.submitted_at else None,
        openness_score=scores["openness"],
        conscientiousness_score=scores["conscientiousness"],
        extraversion_score=scores["extraversion"],
        agreeableness_score=scores["agreeableness"],
        neuroticism_score=scores["neuroticism"],
        dimension_breakdown=dimensions,
        top_match=match_figures[0],
        second_match=match_figures[1],
        third_match=match_figures[2],
        summary=attempt.summary,
    )


@app.get("/api/personality/attempts", response_model=PersonalityAttemptListOut)
def list_personality_attempts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List all personality test attempts (admin only)"""
    query = db.query(PersonalityAttempt).filter(PersonalityAttempt.submitted_at.isnot(None))
    total = query.count()
    
    offset = (page - 1) * page_size
    attempts = query.order_by(PersonalityAttempt.submitted_at.desc()).offset(offset).limit(page_size).all()
    
    items = []
    for attempt in attempts:
        top_figure = None
        if attempt.top_match_id:
            for fig in HISTORICAL_FIGURES:
                if fig["id"] == attempt.top_match_id:
                    top_figure = fig["name"]
                    break
        
        items.append(PersonalityAttemptSummaryOut(
            attempt_id=attempt.id,
            nickname=attempt.nickname or "匿名用户",
            submitted_at=attempt.submitted_at.isoformat() if attempt.submitted_at else None,
            duration_seconds=attempt.duration_seconds,
            top_match_name=top_figure or "未知",
            top_match_similarity=attempt.top_match_similarity,
        ))
    
    return PersonalityAttemptListOut(
        page=page,
        page_size=page_size,
        total=total,
        items=items,
    )


# Mount frontend files (must be after all API routes)
@app.get("/personality", include_in_schema=False)
def personality_page():
    return FileResponse(Path(FRONTEND_DIR) / "personality.html", media_type="text/html")

@app.get("/personality/", include_in_schema=False)
def personality_page_slash():
    return FileResponse(Path(FRONTEND_DIR) / "personality.html", media_type="text/html")


@app.get("/sbti", include_in_schema=False)
def sbti_page():
    return FileResponse(Path(FRONTEND_DIR) / "sbti.html", media_type="text/html")


@app.get("/sbti/", include_in_schema=False)
def sbti_page_slash():
    return FileResponse(Path(FRONTEND_DIR) / "sbti.html", media_type="text/html")

app.mount("/iq", FrontendStaticFiles(directory=str(FRONTEND_DIR), html=True), name="iq-frontend")
app.mount("", FrontendStaticFiles(directory=str(FRONTEND_DIR), html=True), name="root-frontend")
