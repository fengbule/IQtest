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
    completion_rate = round((answered_count / total) * 100, 2) if total else 0.0

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

    if percentile >= 98:
        crowd_desc = "已经明显高于大多数参与者"
    elif percentile >= 84:
        crowd_desc = "高于多数参与者"
    elif percentile >= 50:
        crowd_desc = "处于常见区间或略高于常见区间"
    elif percentile >= 16:
        crowd_desc = "略低于常见区间"
    else:
        crowd_desc = "目前明显低于本测验内部常见区间"

    if estimated_iq >= 125:
        level_label = "优势表现区"
        level_desc = "从这次作答看，你在题目理解、规律发现和信息处理上都表现得比较稳定，整体属于非常突出的水平。"
    elif estimated_iq >= 110:
        level_label = "良好表现区"
        level_desc = "从这次作答看，你的整体推理能力高于本测验内部平均水平，面对常规推理题时通常会更容易找到规律。"
    elif estimated_iq >= 90:
        level_label = "常模区间"
        level_desc = "从这次作答看，你的表现处于常见区间，说明基础理解和推理能力是比较稳定的。"
    elif estimated_iq >= 75:
        level_label = "基础发展区"
        level_desc = "从这次作答看，你当前在一些题型上还没有完全适应，尤其在规律提取和细节辨别上还有提升空间。"
    else:
        level_label = "起步提升区"
        level_desc = "这次结果更像一次摸底，不建议把它直接理解为最终能力结论，尤其当作答不完整或答题过快时，结果会偏低。"

    if answered_count < max(8, total // 2):
        reliability_note = (
            "【结果有效性提醒】你本次作答完成度偏低，未完成的题目较多，因此当前“参考 IQ”只能当作非常粗略的临时参考，"
            "不能代表你的真实稳定水平。更建议完整作答后再看结果。"
        )
    elif duration_seconds < 180:
        reliability_note = (
            "【结果有效性提醒】你的提交速度非常快，说明这次结果可能更接近“快速尝试”而不是认真完成后的稳定表现，"
            "建议重新完整作答一次，再看最终参考值。"
        )
    else:
        reliability_note = (
            "【结果有效性提醒】本次结果可作为一次相对有效的站内参考，但它仍然不是正式心理测验结果，"
            "更适合用来观察你的大致表现区间和强弱项。"
        )

    interpretation = (
        f"一、你现在大概处于什么水平？\n"
        f"本次结果显示：你当前大致处于“{level_label}”。参考 IQ 为 {estimated_iq}，参考百分位约为 P{percentile}，这意味着在本测验的内部换算里，你的表现 {crowd_desc}。\n\n"
        f"二、这组数字应该怎么理解？\n"
        f"- 参考 IQ：{estimated_iq}，这是基于本站题库和内部换算模型得到的粗略值，不等于正式智商测验结论。\n"
        f"- 百分位：P{percentile}，表示如果把大家放在一起比较，你本次成绩大约处在什么位置。\n"
        f"- 作答情况：本次共答对 {correct_count}/{total} 题，实际作答 {answered_count}/{total} 题，完成度约 {completion_rate}%。\n\n"
        f"三、结合这次作答，应该怎么理解你的表现？\n"
        f"{level_desc}\n\n"
        f"四、你的强项和短板分别是什么？\n"
        f"- 相对优势：{strongest_name}\n"
        f"- 优先提升：{weakest_name}\n"
        f"如果想让结果更好看、也更接近真实水平，最直接的方法就是先把弱项维度的错题做复盘，再做同类型训练。\n\n"
        f"五、这次结果靠不靠谱？\n"
        f"{reliability_note}"
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
