from datetime import datetime
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine, get_db
from .models import AdminUser, AttemptAnswer, Question, TestAttempt
from .schemas import (
    AdminLoginIn,
    AdminLoginOut,
    DashboardStatsOut,
    QuestionOut,
    ResultOut,
    StartAttemptIn,
    StartAttemptOut,
    SubmitAttemptIn,
)
from .scoring import CATEGORY_LABELS, score_attempt
from .security import create_access_token, decode_access_token, verify_password
from .seed import seed_admin, seed_questions

app = FastAPI(title="IQ Assessment Project", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_admin(db)
        seed_questions(db)
    finally:
        db.close()


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "iq-app", "time": datetime.utcnow().isoformat()}


@app.get("/api/public/info")
def public_info():
    return {
        "title": "智商检测与认知推理项目",
        "time_limit_seconds": 20 * 60,
        "question_count": 20,
        "notice": "这是娱乐性在线认知测评，不等同于临床或教育标准化 IQ 诊断。",
    }


@app.post("/api/attempts/start", response_model=StartAttemptOut)
def start_attempt(payload: StartAttemptIn, request: Request, db: Session = Depends(get_db)):
    questions = (
        db.query(Question)
        .filter(Question.is_active.is_(True))
        .order_by(Question.order_no.asc())
        .all()
    )
    attempt = TestAttempt(
        nickname=payload.nickname,
        email=str(payload.email) if payload.email else None,
        started_at=datetime.utcnow(),
        total_questions=len(questions),
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", "")[:255],
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    question_payload = [
        QuestionOut(
            id=q.id,
            order_no=q.order_no,
            category=CATEGORY_LABELS.get(q.category, q.category),
            difficulty=q.difficulty,
            prompt=q.prompt,
            options={"A": q.option_a, "B": q.option_b, "C": q.option_c, "D": q.option_d},
        )
        for q in questions
    ]
    return StartAttemptOut(
        attempt_id=attempt.id,
        started_at=attempt.started_at.isoformat(),
        time_limit_seconds=20 * 60,
        questions=question_payload,
        note="题目提交后将生成内部标准化得分、分维度表现与答题复盘。",
    )


@app.post("/api/attempts/{attempt_id}/submit", response_model=ResultOut)
def submit_attempt(attempt_id: int, payload: SubmitAttemptIn, db: Session = Depends(get_db)):
    attempt = db.query(TestAttempt).filter(TestAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="attempt not found")
    if attempt.submitted_at is not None:
        raise HTTPException(status_code=400, detail="attempt already submitted")

    questions = db.query(Question).filter(Question.is_active.is_(True)).order_by(Question.order_no.asc()).all()
    submitted_answers = {item.question_id: item.selected_option for item in payload.answers}
    scoring = score_attempt(questions, submitted_answers, payload.duration_seconds)

    attempt.submitted_at = datetime.utcnow()
    attempt.duration_seconds = payload.duration_seconds
    attempt.correct_count = scoring["correct_count"]
    attempt.raw_score = scoring["raw_score"]
    attempt.normalized_score = scoring["normalized_score"]
    attempt.estimated_iq = scoring["estimated_iq"]
    attempt.percentile = scoring["percentile"]
    attempt.interpretation = scoring["interpretation"]

    for q in questions:
        selected = submitted_answers.get(q.id)
        db.add(
            AttemptAnswer(
                attempt_id=attempt.id,
                question_id=q.id,
                selected_option=selected,
                is_correct=(selected == q.correct_option),
            )
        )

    db.commit()

    return ResultOut(
        attempt_id=attempt.id,
        total_questions=scoring["total_questions"],
        correct_count=scoring["correct_count"],
        raw_score=scoring["raw_score"],
        normalized_score=scoring["normalized_score"],
        estimated_iq=scoring["estimated_iq"],
        percentile=scoring["percentile"],
        interpretation=scoring["interpretation"],
        duration_seconds=payload.duration_seconds,
        disclaimer="本结果仅基于站内题库与内部换算模型，不能替代正式心理测验、教育测量或医疗判断。",
        category_breakdown=scoring["category_breakdown"],
        answer_review=scoring["review"],
    )


@app.get("/api/attempts/{attempt_id}/result", response_model=ResultOut)
def get_result(attempt_id: int, db: Session = Depends(get_db)):
    attempt = db.query(TestAttempt).filter(TestAttempt.id == attempt_id).first()
    if not attempt or attempt.submitted_at is None:
        raise HTTPException(status_code=404, detail="result not found")

    questions = db.query(Question).filter(Question.is_active.is_(True)).order_by(Question.order_no.asc()).all()
    submitted_answers = {
        row.question_id: row.selected_option
        for row in db.query(AttemptAnswer).filter(AttemptAnswer.attempt_id == attempt.id).all()
    }
    scoring = score_attempt(questions, submitted_answers, attempt.duration_seconds)

    return ResultOut(
        attempt_id=attempt.id,
        total_questions=scoring["total_questions"],
        correct_count=scoring["correct_count"],
        raw_score=scoring["raw_score"],
        normalized_score=scoring["normalized_score"],
        estimated_iq=attempt.estimated_iq,
        percentile=attempt.percentile,
        interpretation=attempt.interpretation,
        duration_seconds=attempt.duration_seconds,
        disclaimer="本结果仅基于站内题库与内部换算模型，不能替代正式心理测验、教育测量或医疗判断。",
        category_breakdown=scoring["category_breakdown"],
        answer_review=scoring["review"],
    )


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
    completed = [x for x in attempts if x.submitted_at is not None]
    total_attempts = len(attempts)
    completed_attempts = len(completed)
    avg_iq = round(sum(x.estimated_iq for x in completed) / completed_attempts, 2) if completed_attempts else 0.0
    avg_duration = round(sum(x.duration_seconds for x in completed) / completed_attempts, 2) if completed_attempts else 0.0
    avg_accuracy = round(sum(x.raw_score for x in completed) / completed_attempts, 2) if completed_attempts else 0.0

    question_map = {q.id: q for q in db.query(Question).all()}
    category_rollup: dict[str, list[int]] = {}
    rows = db.query(AttemptAnswer).all()
    for row in rows:
        question = question_map.get(row.question_id)
        if not question:
            continue
        key = CATEGORY_LABELS.get(question.category, question.category)
        category_rollup.setdefault(key, [0, 0])
        category_rollup[key][0] += int(row.is_correct)
        category_rollup[key][1] += 1

    category_accuracy = {
        key: round((value[0] / value[1]) * 100, 2) if value[1] else 0.0
        for key, value in category_rollup.items()
    }

    recent_results = [
        {
            "attempt_id": x.id,
            "nickname": x.nickname or "匿名用户",
            "estimated_iq": x.estimated_iq,
            "percentile": x.percentile,
            "duration_seconds": x.duration_seconds,
            "submitted_at": x.submitted_at.isoformat() if x.submitted_at else None,
        }
        for x in sorted(completed, key=lambda item: item.submitted_at or datetime.min, reverse=True)[:20]
    ]

    return DashboardStatsOut(
        total_attempts=total_attempts,
        completed_attempts=completed_attempts,
        average_estimated_iq=avg_iq,
        average_duration_seconds=avg_duration,
        average_accuracy=avg_accuracy,
        category_accuracy=category_accuracy,
        recent_results=recent_results,
    )
