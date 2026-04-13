from collections import defaultdict
from math import erf, sqrt


CATEGORY_LABELS = {
    "numerical": "数理推理",
    "logical": "逻辑推理",
    "verbal": "言语理解",
    "spatial": "空间想象",
}


def normal_cdf(z: float) -> float:
    return 0.5 * (1 + erf(z / sqrt(2)))



def score_attempt(question_rows, submitted_answers: dict[int, str | None], duration_seconds: int):
    total = len(question_rows)
    correct_count = 0
    answered_count = 0
    difficulty_sum = sum(q.difficulty for q in question_rows)
    earned_weight = 0
    review = []
    category_totals = defaultdict(lambda: {"total": 0, "correct": 0})

    for q in question_rows:
        selected = submitted_answers.get(q.id)
        if selected is not None:
            answered_count += 1
        is_correct = selected == q.correct_option
        if is_correct:
            correct_count += 1
            earned_weight += q.difficulty
        category_totals[q.category]["total"] += 1
        category_totals[q.category]["correct"] += int(is_correct)
        review.append(
            {
                "question_id": q.id,
                "selected_option": selected,
                "correct_option": q.correct_option,
                "is_correct": is_correct,
                "explanation": q.explanation,
            }
        )

    raw_score = round((correct_count / total) * 100, 2) if total else 0.0
    weighted_accuracy = (earned_weight / difficulty_sum) if difficulty_sum else 0.0

    expected_duration = 20 * 60
    time_factor = max(0.90, min(1.05, expected_duration / max(duration_seconds, 300)))
    normalized_score = round(min(100.0, raw_score * 0.85 + weighted_accuracy * 100 * 0.15) * time_factor, 2)

    z = ((normalized_score / 100.0) - 0.55) / 0.18
    z = max(-2.33, min(2.33, z))
    estimated_iq = round(100 + 15 * z)
    percentile = round(normal_cdf(z) * 100)

    category_breakdown = {}
    for key, payload in category_totals.items():
        total_num = payload["total"]
        correct_num = payload["correct"]
        category_breakdown[CATEGORY_LABELS.get(key, key)] = {
            "correct": correct_num,
            "total": total_num,
            "accuracy": round((correct_num / total_num) * 100, 2) if total_num else 0.0,
        }

    sorted_categories = sorted(
        category_breakdown.items(),
        key=lambda item: (item[1]["accuracy"], item[1]["correct"]),
        reverse=True,
    )
    strongest_name = sorted_categories[0][0] if sorted_categories else "暂无"
    weakest_name = sorted_categories[-1][0] if sorted_categories else "暂无"

    if estimated_iq >= 125:
        level_label = "优势表现区"
        level_desc = "整体表现非常突出，理解、推理和作答稳定性都比较强。"
    elif estimated_iq >= 110:
        level_label = "良好表现区"
        level_desc = "整体表现高于本测验内部平均水平，已经具备较好的综合推理能力。"
    elif estimated_iq >= 90:
        level_label = "常模区间"
        level_desc = "整体表现处于本测验内部常见区间，基础能力较稳定。"
    elif estimated_iq >= 75:
        level_label = "基础发展区"
        level_desc = "当前表现略低于本测验内部平均区间，但通过针对性练习仍有明显提升空间。"
    else:
        level_label = "起步提升区"
        level_desc = "当前结果说明你在本次测验中还没有发挥出来，更建议把它看成一次摸底而不是最终结论。"

    interpretation = (
        f"当前所处水平：{level_label}。\n"
        f"综合说明：本次共答对 {correct_count}/{total} 题，作答 {answered_count}/{total} 题，参考百分位约为 P{percentile}。{level_desc}\n"
        f"优势维度：{strongest_name}。\n"
        f"优先提升：{weakest_name}。建议先从错题复盘、同类型题目重复训练开始。"
    )

    return {
        "total_questions": total,
        "correct_count": correct_count,
        "raw_score": raw_score,
        "normalized_score": normalized_score,
        "estimated_iq": estimated_iq,
        "percentile": percentile,
        "interpretation": interpretation,
        "category_breakdown": category_breakdown,
        "review": review,
    }
