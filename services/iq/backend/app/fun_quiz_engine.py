from __future__ import annotations

import json
from typing import Any


def score_fun_quiz(
    manifest: dict[str, Any],
    answers: list[dict[str, str]]
) -> dict[str, Any]:
    scoring_mode = manifest.get("scoring_mode", "archetype_sum")

    if scoring_mode == "archetype_sum":
        return _score_archetype_sum(manifest, answers)
    elif scoring_mode == "scorecard":
        return _score_dimension_profile(manifest, answers)
    else:
        return _score_archetype_sum(manifest, answers)


def _score_archetype_sum(
    manifest: dict[str, Any],
    answers: list[dict[str, str]]
) -> dict[str, Any]:
    score_map: dict[str, float] = {}
    answer_map = {a["question_id"]: a["selected_value"] for a in answers}

    for question in manifest.get("questions", []):
        selected_value = answer_map.get(question.get("id", ""))
        if not selected_value:
            continue

        for option in question.get("options", []):
            if option.get("value") == selected_value:
                scores = option.get("scores", {})
                for key, value in scores.items():
                    if key != "total":
                        score_map[key] = score_map.get(key, 0) + value
                break

    sorted_items = sorted(score_map.items(), key=lambda x: x[1], reverse=True)
    primary_key = sorted_items[0][0] if sorted_items else None
    secondary_key = sorted_items[1][0] if len(sorted_items) > 1 else None

    return {
        "primary_key": primary_key,
        "secondary_key": secondary_key,
        "score_map": score_map,
        "dimension_scores": score_map,
        "total_score": sum(score_map.values()) if score_map else 0,
    }


def _score_dimension_profile(
    manifest: dict[str, Any],
    answers: list[dict[str, str]]
) -> dict[str, Any]:
    dimension_scores: dict[str, float] = {}
    total_score = 0
    answer_map = {a["question_id"]: a["selected_value"] for a in answers}

    for question in manifest.get("questions", []):
        selected_value = answer_map.get(question.get("id", ""))
        if not selected_value:
            continue

        for option in question.get("options", []):
            if option.get("value") == selected_value:
                scores = option.get("scores", {})
                for key, value in scores.items():
                    if key == "total":
                        total_score += value
                    else:
                        dimension_scores[key] = dimension_scores.get(key, 0) + value
                break

    return {
        "primary_key": None,
        "secondary_key": None,
        "score_map": dimension_scores,
        "dimension_scores": dimension_scores,
        "total_score": total_score,
    }


def resolve_result_card(
    manifest: dict[str, Any],
    scoring_result: dict[str, Any]
) -> dict[str, Any]:
    primary_result = None
    secondary_result = None
    scoring_mode = manifest.get("scoring_mode", "archetype_sum")

    for result in manifest.get("results", []):
        result_key = result.get("key", "")
        rule = result.get("rule", {})

        if scoring_mode == "scorecard":
            if rule.get("type") == "score_range":
                min_total = rule.get("min_total", 0)
                max_total = rule.get("max_total", 9999)
                if min_total <= scoring_result.get("total_score", 0) <= max_total:
                    if primary_result is None:
                        primary_result = _build_result_card(result)
                    elif secondary_result is None:
                        secondary_result = _build_result_card(result)
        else:
            if result_key == scoring_result.get("primary_key"):
                primary_result = _build_result_card(result)
            elif result_key == scoring_result.get("secondary_key"):
                secondary_result = _build_result_card(result)

    if primary_result is None and scoring_mode == "archetype_sum":
        top_key = scoring_result.get("primary_key")
        for result in manifest.get("results", []):
            if result.get("key") == top_key:
                primary_result = _build_result_card(result)
                break

    return {
        "primary_result": primary_result,
        "secondary_result": secondary_result,
    }


def _build_result_card(result: dict[str, Any]) -> dict[str, Any]:
    extra = result.get("extra", {})
    if isinstance(extra, str):
        try:
            extra = json.loads(extra)
        except (json.JSONDecodeError, TypeError):
            extra = {}

    return {
        "key": result.get("key", ""),
        "name": result.get("name", ""),
        "subtitle": result.get("subtitle"),
        "summary": result.get("summary", ""),
        "long_desc": result.get("long_desc"),
        "poster_image": result.get("poster_image"),
        "share_title": result.get("share_title"),
        "share_subtitle": result.get("share_subtitle"),
        "extra": extra if isinstance(extra, dict) else {},
    }


def build_dimension_breakdown(
    manifest: dict[str, Any],
    dimension_scores: dict[str, float]
) -> list[dict[str, Any]]:
    dimensions = manifest.get("dimensions", [])
    if not dimensions:
        return []

    breakdown = []
    for dim in dimensions:
        key = dim.get("key", "")
        breakdown.append({
            "key": key,
            "name": dim.get("name", key),
            "score": dimension_scores.get(key, 0),
        })

    return breakdown