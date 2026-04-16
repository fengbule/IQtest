from __future__ import annotations

import json
from sqlalchemy.orm import Session

from .models import FunQuizDefinition, FunQuizQuestion, FunQuizResult
from .fun_quiz_loader import load_all_fun_quiz_manifests


def seed_fun_quizzes(db: Session) -> None:
    manifests = load_all_fun_quiz_manifests()
    for manifest in manifests:
        _seed_single_quiz(db, manifest)
    db.commit()


def _seed_single_quiz(db: Session, manifest: dict) -> None:
    slug = manifest["slug"]
    quiz = db.query(FunQuizDefinition).filter(FunQuizDefinition.slug == slug).first()

    if quiz is None:
        quiz = FunQuizDefinition(slug=slug)
        db.add(quiz)
    else:
        db.query(FunQuizQuestion).filter(FunQuizQuestion.quiz_id == quiz.id).delete()
        db.query(FunQuizResult).filter(FunQuizResult.quiz_id == quiz.id).delete()

    quiz.title = manifest.get("title", "")
    quiz.subtitle = manifest.get("subtitle")
    quiz.description = manifest.get("description")
    quiz.cover_image = manifest.get("cover_image")
    quiz.theme_color = manifest.get("theme_color")
    quiz.estimated_minutes = manifest.get("estimated_minutes", 2)
    quiz.play_style = manifest.get("play_style", "quick")
    quiz.scoring_mode = manifest.get("scoring_mode", "archetype_sum")
    quiz.question_count = len(manifest.get("questions", []))
    quiz.result_count = len(manifest.get("results", []))
    quiz.disclaimer = manifest.get("disclaimer")
    quiz.sort_order = manifest.get("sort_order", 0)
    quiz.is_active = manifest.get("is_active", True)
    db.flush()

    for q_data in manifest.get("questions", []):
        question = FunQuizQuestion(
            quiz_id=quiz.id,
            question_key=q_data.get("id", ""),
            position=q_data.get("position", 0),
            question_text=q_data.get("text", ""),
            question_subtext=q_data.get("subtext"),
            question_type=q_data.get("type", "single_choice"),
            scene_text=q_data.get("scene_text"),
            dimension_key=q_data.get("dimension_key"),
            option_payload_json=json.dumps(q_data.get("options", []), ensure_ascii=False),
            is_active=True,
        )
        db.add(question)

    for r_data in manifest.get("results", []):
        result = FunQuizResult(
            quiz_id=quiz.id,
            result_key=r_data.get("key", ""),
            result_name=r_data.get("name", ""),
            result_subtitle=r_data.get("subtitle"),
            result_summary=r_data.get("summary", ""),
            result_long_desc=r_data.get("long_desc"),
            poster_image=r_data.get("poster_image"),
            share_title=r_data.get("share_title"),
            share_subtitle=r_data.get("share_subtitle"),
            extra_payload_json=json.dumps(r_data.get("extra", {}), ensure_ascii=False),
        )
        db.add(result)