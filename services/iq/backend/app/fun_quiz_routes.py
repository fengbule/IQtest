from __future__ import annotations

import json
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from .database import get_db
from .fun_quiz_engine import score_fun_quiz, resolve_result_card, build_dimension_breakdown
from .fun_quiz_loader import load_fun_quiz_manifest
from .fun_quiz_schemas import (
    FunQuizListItemOut,
    FunQuizDetailOut,
    FunQuizStartOut,
    FunQuizSubmitIn,
    FunQuizSubmitOut,
    FunQuizAttemptListOut,
    FunQuizAttemptSummaryOut,
    FunQuizOptionOut,
    FunQuizQuestionOut,
)
from .fun_quiz_helpers import get_current_admin
from .models import FunQuizDefinition, FunQuizQuestion, FunQuizResult, FunQuizAttempt, FunQuizAnswer


router = APIRouter(prefix="/api", tags=["fun-quiz"])


@router.get("/fun-quizzes", response_model=list[FunQuizListItemOut])
def list_fun_quizzes(db: Session = Depends(get_db)):
    quizzes = db.query(FunQuizDefinition).filter(
        FunQuizDefinition.is_active == True
    ).order_by(FunQuizDefinition.sort_order).all()

    return [
        FunQuizListItemOut(
            slug=q.slug,
            title=q.title,
            subtitle=q.subtitle,
            cover_image=q.cover_image,
            theme_color=q.theme_color,
            estimated_minutes=q.estimated_minutes,
            play_style=q.play_style,
            question_count=q.question_count,
        )
        for q in quizzes
    ]


@router.get("/fun-quizzes/{slug}", response_model=FunQuizDetailOut)
def get_fun_quiz(slug: str, db: Session = Depends(get_db)):
    quiz = db.query(FunQuizDefinition).filter(
        FunQuizDefinition.slug == slug,
        FunQuizDefinition.is_active == True
    ).first()

    if not quiz:
        raise HTTPException(status_code=404, detail="quiz not found")

    return FunQuizDetailOut(
        slug=quiz.slug,
        title=quiz.title,
        subtitle=quiz.subtitle,
        description=quiz.description,
        cover_image=quiz.cover_image,
        theme_color=quiz.theme_color,
        estimated_minutes=quiz.estimated_minutes,
        play_style=quiz.play_style,
        scoring_mode=quiz.scoring_mode,
        question_count=quiz.question_count,
        disclaimer=quiz.disclaimer,
    )


@router.post("/fun-quizzes/{slug}/attempts", response_model=FunQuizStartOut)
def start_fun_quiz_attempt(
    slug: str,
    request: Request,
    db: Session = Depends(get_db)
):
    quiz = db.query(FunQuizDefinition).filter(
        FunQuizDefinition.slug == slug,
        FunQuizDefinition.is_active == True
    ).first()

    if not quiz:
        raise HTTPException(status_code=404, detail="quiz not found")

    attempt = FunQuizAttempt(
        quiz_id=quiz.id,
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", "")[:255],
    )
    db.add(attempt)
    db.flush()

    questions = db.query(FunQuizQuestion).filter(
        FunQuizQuestion.quiz_id == quiz.id,
        FunQuizQuestion.is_active == True
    ).order_by(FunQuizQuestion.position).all()

    question_payload = []
    for q in questions:
        options_data = json.loads(q.option_payload_json) if q.option_payload_json else []
        question_payload.append(
            FunQuizQuestionOut(
                id=q.question_key,
                order_no=q.position,
                type=q.question_type or "single_choice",
                text=q.question_text,
                subtext=q.question_subtext,
                options=[
                    FunQuizOptionOut(value=o.get("value", ""), label=o.get("label", ""))
                    for o in options_data
                ],
            )
        )

    db.commit()

    return FunQuizStartOut(
        attempt_id=attempt.id,
        started_at=attempt.started_at.isoformat(),
        questions=question_payload,
        note="这是一个娱乐向心理测验，请按第一直觉作答。",
    )


@router.post("/fun-quizzes/{slug}/attempts/{attempt_id}/submit", response_model=FunQuizSubmitOut)
def submit_fun_quiz_attempt(
    slug: str,
    attempt_id: int,
    payload: FunQuizSubmitIn,
    db: Session = Depends(get_db)
):
    quiz = db.query(FunQuizDefinition).filter(
        FunQuizDefinition.slug == slug,
        FunQuizDefinition.is_active == True
    ).first()

    if not quiz:
        raise HTTPException(status_code=404, detail="quiz not found")

    attempt = db.query(FunQuizAttempt).filter(
        FunQuizAttempt.id == attempt_id,
        FunQuizAttempt.quiz_id == quiz.id
    ).first()

    if not attempt:
        raise HTTPException(status_code=404, detail="attempt not found")

    if attempt.submitted_at is not None:
        raise HTTPException(status_code=400, detail="attempt already submitted")

    manifest = load_fun_quiz_manifest(slug)
    if not manifest:
        raise HTTPException(status_code=500, detail="quiz manifest not found")

    if len(payload.answers) != quiz.question_count:
        raise HTTPException(status_code=400, detail="answers incomplete")

    questions = db.query(FunQuizQuestion).filter(
        FunQuizQuestion.quiz_id == quiz.id
    ).all()
    question_map = {q.question_key: q for q in questions}

    for answer in payload.answers:
        q = question_map.get(answer.question_id)
        if not q:
            continue

        options_data = json.loads(q.option_payload_json) if q.option_payload_json else []
        selected_label = ""
        score_payload = {}

        for option in options_data:
            if option.get("value") == answer.selected_value:
                selected_label = option.get("label", "")
                score_payload = option.get("scores", {})
                break

        fa = FunQuizAnswer(
            attempt_id=attempt.id,
            question_id=q.id,
            selected_value=answer.selected_value,
            selected_label=selected_label,
            score_payload_json=json.dumps(score_payload, ensure_ascii=False),
        )
        db.add(fa)

    answers_for_scoring = [
        {"question_id": a.question_id, "selected_value": a.selected_value}
        for a in payload.answers
    ]

    manifest_questions = manifest.get("questions", [])
    for mq in manifest_questions:
        for a in answers_for_scoring:
            if mq.get("id") == a["question_id"]:
                a["_manifest"] = mq
                break

    scoring_result = score_fun_quiz(manifest, answers_for_scoring)
    result_cards = resolve_result_card(manifest, scoring_result)

    dimension_breakdown = []
    if manifest.get("scoring_mode") == "scorecard":
        dimension_breakdown = build_dimension_breakdown(manifest, scoring_result.get("dimension_scores", {}))

    attempt.submitted_at = datetime.utcnow()
    attempt.duration_seconds = payload.duration_seconds
    attempt.top_result_key = (result_cards.get("primary_result") or {}).get("key")
    attempt.secondary_result_key = (result_cards.get("secondary_result") or {}).get("key")
    attempt.score_payload_json = json.dumps(scoring_result, ensure_ascii=False)

    db.commit()
    db.refresh(attempt)

    return FunQuizSubmitOut(
        attempt_id=attempt.id,
        submitted_at=attempt.submitted_at.isoformat(),
        duration_seconds=attempt.duration_seconds,
        quiz_slug=slug,
        primary_result=result_cards.get("primary_result"),
        secondary_result=result_cards.get("secondary_result"),
        dimension_breakdown=dimension_breakdown,
        score_payload=scoring_result,
        disclaimer=quiz.disclaimer or "本测验仅供娱乐，请勿当真。",
    )


@router.get("/fun-quizzes/{slug}/attempts/{attempt_id}/result", response_model=FunQuizSubmitOut)
def get_fun_quiz_attempt_result(
    slug: str,
    attempt_id: int,
    db: Session = Depends(get_db)
):
    quiz = db.query(FunQuizDefinition).filter(
        FunQuizDefinition.slug == slug,
        FunQuizDefinition.is_active == True
    ).first()

    if not quiz:
        raise HTTPException(status_code=404, detail="quiz not found")

    attempt = db.query(FunQuizAttempt).filter(
        FunQuizAttempt.id == attempt_id,
        FunQuizAttempt.quiz_id == quiz.id
    ).first()

    if not attempt:
        raise HTTPException(status_code=404, detail="attempt not found")

    if attempt.submitted_at is None:
        raise HTTPException(status_code=400, detail="attempt not submitted yet")

    manifest = load_fun_quiz_manifest(slug)
    if not manifest:
        raise HTTPException(status_code=500, detail="quiz manifest not found")

    scoring_result = {}
    if attempt.score_payload_json:
        try:
            scoring_result = json.loads(attempt.score_payload_json)
        except json.JSONDecodeError:
            scoring_result = {}

    result_cards = resolve_result_card(manifest, scoring_result)

    dimension_breakdown = []
    if manifest.get("scoring_mode") == "scorecard":
        dimension_breakdown = build_dimension_breakdown(manifest, scoring_result.get("dimension_scores", {}))

    return FunQuizSubmitOut(
        attempt_id=attempt.id,
        submitted_at=attempt.submitted_at.isoformat(),
        duration_seconds=attempt.duration_seconds or 0,
        quiz_slug=slug,
        primary_result=result_cards.get("primary_result"),
        secondary_result=result_cards.get("secondary_result"),
        dimension_breakdown=dimension_breakdown,
        score_payload=scoring_result,
        disclaimer=quiz.disclaimer or "本测验仅供娱乐，请勿当真。",
    )


@router.get("/admin/fun-quizzes/attempts", response_model=FunQuizAttemptListOut)
def list_fun_quiz_attempts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    slug: str | None = None,
    _: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    query = db.query(FunQuizAttempt).filter(FunQuizAttempt.submitted_at.isnot(None))

    if slug:
        quiz = db.query(FunQuizDefinition).filter(FunQuizDefinition.slug == slug).first()
        if quiz:
            query = query.filter(FunQuizAttempt.quiz_id == quiz.id)

    total = query.count()

    offset = (page - 1) * page_size
    attempts = query.order_by(FunQuizAttempt.submitted_at.desc()).offset(offset).limit(page_size).all()

    items = []
    for attempt in attempts:
        quiz = attempt.quiz
        primary_result_name = None
        if attempt.top_result_key:
            result = db.query(FunQuizResult).filter(
                FunQuizResult.quiz_id == quiz.id,
                FunQuizResult.result_key == attempt.top_result_key
            ).first()
            if result:
                primary_result_name = result.result_name

        items.append(FunQuizAttemptSummaryOut(
            attempt_id=attempt.id,
            quiz_slug=quiz.slug if quiz else "",
            quiz_title=quiz.title if quiz else "",
            nickname=attempt.nickname or "匿名用户",
            submitted_at=attempt.submitted_at.isoformat() if attempt.submitted_at else None,
            duration_seconds=attempt.duration_seconds,
            primary_result_key=attempt.top_result_key,
            primary_result_name=primary_result_name,
        ))

    return FunQuizAttemptListOut(
        page=page,
        page_size=page_size,
        total=total,
        items=items,
    )