from __future__ import annotations

from collections import Counter, defaultdict


CATEGORY_LABELS = {
    "numerical": "数理推理",
    "logical": "逻辑推理",
    "verbal": "言语理解",
    "spatial": "空间想象",
}

CATEGORY_SCORE_FIELDS = {
    "numerical": "math_score",
    "logical": "logic_score",
    "verbal": "verbal_score",
    "spatial": "spatial_score",
}

DIFFICULTY_LABELS = {
    "easy": "基础题",
    "medium": "进阶题",
    "hard": "挑战题",
}

ABILITY_META = [
    ("S", "突出水平", "突出表现区", 125),
    ("A", "优秀水平", "优秀表现区", 110),
    ("B", "良好水平", "良好表现区", 90),
    ("C", "中等水平", "中等表现区", 75),
    ("D", "发展提升", "发展提升区", 60),
    ("E", "基础观察", "基础观察区", 0),
]

DIMENSION_FEEDBACK = {
    "numerical": {
        "strength": "你在数量关系和基础计算转换上更容易把握核心结构。",
        "focus": "建议继续练习数列、比例和方程转化，让计算过程更稳定。",
    },
    "logical": {
        "strength": "你在规则识别和条件推断方面有不错的敏感度。",
        "focus": "建议多做真假推理、条件命题和排序约束题，强化严密推断。",
    },
    "verbal": {
        "strength": "你在词义辨析和信息提炼方面表现较稳。",
        "focus": "建议加强阅读概括、语义关系和语句组织训练，提升理解精度。",
    },
    "spatial": {
        "strength": "你在图形旋转、镜像和空间位置判断方面更容易建立直觉。",
        "focus": "建议继续练习折叠、旋转和多步骤图形变换，提升空间想象速度。",
    },
}


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def ability_from_cpi(cpi: int) -> dict[str, str]:
    for level, label, zone, threshold in ABILITY_META:
        if cpi >= threshold:
            return {
                "level": level,
                "label": label,
                "zone": zone,
            }
    return {
        "level": "E",
        "label": "基础观察",
        "zone": "基础观察区",
    }


def percentile_from_cpi(cpi: int) -> int:
    bands = [
        (40, 59, 10, 20),
        (60, 74, 20, 40),
        (75, 89, 40, 60),
        (90, 109, 60, 80),
        (110, 124, 80, 92),
        (125, 130, 92, 98),
    ]
    bounded = int(clamp(cpi, 40, 130))
    for start, end, low, high in bands:
        if start <= bounded <= end:
            if end == start:
                return low
            ratio = (bounded - start) / (end - start)
            return round(low + ratio * (high - low))
    return 10


def iq_range_from_cpi(cpi: int) -> str:
    if cpi >= 125:
        return "120-129"
    if cpi >= 110:
        return "110-119"
    if cpi >= 90:
        return "100-109"
    if cpi >= 75:
        return "90-99"
    return "90 以下参考区间"


def option_repeat_ratio(answer_rows: list) -> float:
    selected = [row.selected_option for row in answer_rows if row.selected_option]
    if not selected:
        return 0.0
    most_common = Counter(selected).most_common(1)[0][1]
    return most_common / len(selected)


def response_quality(answer_rows: list, duration_seconds: int, completion_score: float) -> tuple[float, dict]:
    answered_rows = [row for row in answer_rows if row.selected_option]
    answered_count = len(answered_rows)
    avg_seconds = duration_seconds / answered_count if answered_count else 0.0
    very_fast_count = 0
    for row in answered_rows:
        threshold = max(4, int(row.estimated_seconds * 0.35))
        if row.time_spent_seconds and row.time_spent_seconds < threshold:
            very_fast_count += 1
    very_fast_ratio = very_fast_count / answered_count if answered_count else 0.0
    repeat_ratio = option_repeat_ratio(answer_rows)

    score = 1.0
    if avg_seconds and avg_seconds < 4:
        score -= 0.20
    if very_fast_ratio > 0.35:
        score -= 0.15
    if completion_score < 0.85:
        score -= 0.10
    if repeat_ratio > 0.55:
        score -= 0.10
    score = clamp(score, 0.60, 1.0)

    return score, {
        "avg_seconds_per_question": round(avg_seconds, 2),
        "very_fast_ratio": round(very_fast_ratio, 4),
        "repeat_ratio": round(repeat_ratio, 4),
    }


def validity_from_scores(
    completion_score: float,
    quality_score: float,
    quality_meta: dict,
) -> dict[str, str]:
    avg_seconds = quality_meta["avg_seconds_per_question"]
    very_fast_ratio = quality_meta["very_fast_ratio"]

    if completion_score >= 0.95 and quality_score >= 0.90 and very_fast_ratio <= 0.20:
        return {
            "flag": "high",
            "label": "高可信度",
            "note": "作答完整、节奏稳定，本次结果具有较高参考价值。",
        }
    if completion_score >= 0.85 and quality_score >= 0.75 and avg_seconds >= 4:
        return {
            "flag": "medium",
            "label": "中可信度",
            "note": "本次作答整体有效，但存在少量快速作答或节奏波动，建议结合复测结果综合判断。",
        }
    return {
        "flag": "low",
        "label": "低可信度",
        "note": "本次作答存在较多快速作答或未完整完成的情况，结果更适合作为粗略参考。",
    }


def build_dimension_breakdown(answer_rows: list) -> list[dict]:
    grouped: dict[str, list] = defaultdict(list)
    for row in answer_rows:
        grouped[row.question_dimension].append(row)

    breakdown = []
    for key, label in CATEGORY_LABELS.items():
        rows = grouped.get(key, [])
        total = len(rows)
        correct = sum(1 for row in rows if row.is_correct)
        weight_total = sum(row.question_weight for row in rows)
        weight_correct = sum(row.question_weight for row in rows if row.is_correct)
        accuracy = round((correct / total) * 100, 2) if total else 0.0
        score_ratio = (weight_correct / weight_total) if weight_total else 0.0
        dimension_cpi = round(40 + score_ratio * 90) if total else 40
        ability = ability_from_cpi(dimension_cpi)
        feedback = DIMENSION_FEEDBACK[key]
        description = feedback["strength"] if accuracy >= 62 else feedback["focus"]
        advice = feedback["focus"] if accuracy >= 62 else "建议优先复盘该维度错题，再做同类型训练来提升稳定性。"
        breakdown.append(
            {
                "key": key,
                "label": label,
                "correct": correct,
                "total": total,
                "accuracy": accuracy,
                "score": dimension_cpi,
                "level": ability["level"],
                "level_label": ability["label"],
                "description": description,
                "advice": advice,
            }
        )
    return breakdown


def build_answer_review(answer_rows: list) -> list[dict]:
    review = []
    for row in answer_rows:
        review.append(
            {
                "question_order": row.question_order,
                "prompt": row.prompt_snapshot,
                "dimension": CATEGORY_LABELS.get(row.question_dimension, row.question_dimension),
                "difficulty": DIFFICULTY_LABELS.get(row.question_difficulty, row.question_difficulty),
                "selected_option": row.selected_option,
                "correct_option": row.correct_answer_snapshot,
                "is_correct": row.is_correct,
                "time_spent_seconds": row.time_spent_seconds,
                "explanation": row.explanation_snapshot,
            }
        )
    return review


def build_interpretation(
    ability: dict[str, str],
    percentile: int,
    strongest: dict,
    weakest: dict,
    validity: dict[str, str],
) -> tuple[str, str]:
    summary = (
        f"你的综合认知表现处于“{ability['label']}”，当前结果大致超过站内 {percentile}% 的有效作答用户。"
    )
    interpretation = (
        f"总体结论：本次综合认知表现落在“{ability['zone']}”。\n"
        f"优势维度：{strongest['label']}更稳，说明你在这一类题型上的规则识别与判断更顺畅。\n"
        f"优先提升：{weakest['label']}相对偏弱，建议优先复盘该维度错题，再做针对性练习。\n"
        f"可信度提示：{validity['note']}"
    )
    return summary, interpretation


def score_attempt(answer_rows: list, duration_seconds: int) -> dict:
    total_questions = len(answer_rows)
    answered_rows = [row for row in answer_rows if row.selected_option]
    correct_rows = [row for row in answered_rows if row.is_correct]

    answered_count = len(answered_rows)
    correct_count = len(correct_rows)
    accuracy_score = (correct_count / answered_count) if answered_count else 0.0
    total_weight = sum(row.question_weight for row in answer_rows)
    earned_weight = sum(row.question_weight for row in correct_rows)
    difficulty_score = (earned_weight / total_weight) if total_weight else 0.0
    completion_score = (answered_count / total_questions) if total_questions else 0.0
    response_quality_score, quality_meta = response_quality(answer_rows, duration_seconds, completion_score)

    final_score_ratio = (
        0.45 * accuracy_score
        + 0.30 * difficulty_score
        + 0.10 * completion_score
        + 0.15 * response_quality_score
    )
    cpi_score = round(40 + final_score_ratio * 90)
    cpi_score = int(clamp(cpi_score, 40, 130))
    percentile = percentile_from_cpi(cpi_score)
    ability = ability_from_cpi(cpi_score)
    iq_range = iq_range_from_cpi(cpi_score)
    validity = validity_from_scores(completion_score, response_quality_score, quality_meta)

    dimension_breakdown = build_dimension_breakdown(answer_rows)
    strongest = max(dimension_breakdown, key=lambda item: (item["score"], item["accuracy"]))
    weakest = min(dimension_breakdown, key=lambda item: (item["score"], item["accuracy"]))
    summary, interpretation = build_interpretation(ability, percentile, strongest, weakest, validity)

    stored_dimension_scores = {
        CATEGORY_SCORE_FIELDS[item["key"]]: item["score"] for item in dimension_breakdown
    }

    return {
        "total_questions": total_questions,
        "answered_count": answered_count,
        "correct_count": correct_count,
        "accuracy_score": round(accuracy_score, 4),
        "difficulty_score": round(difficulty_score, 4),
        "completion_score": round(completion_score, 4),
        "response_quality_score": round(response_quality_score, 4),
        "cpi_score": cpi_score,
        "percentile": percentile,
        "ability_level": ability["level"],
        "ability_label": ability["label"],
        "ability_zone": ability["zone"],
        "iq_range": iq_range,
        "validity_flag": validity["flag"],
        "validity_label": validity["label"],
        "validity_note": validity["note"],
        "summary": summary,
        "interpretation": interpretation,
        "dimension_breakdown": dimension_breakdown,
        "answer_review": build_answer_review(answer_rows),
        "quality_meta": quality_meta,
        "stored_dimension_scores": stored_dimension_scores,
        "disclaimer": (
            "本结果基于本站题库、评分规则与作答行为生成，仅供认知表现体验与项目展示参考，"
            "不等同于正式标准化 IQ 测验、心理诊断或教育评估。"
        ),
    }
