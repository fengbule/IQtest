"""
性格测试计分和历史人物匹配逻辑
基于Big Five人格模型
"""

from typing import TypedDict
from math import sqrt
from .personality_data import PERSONALITY_DIMENSIONS, HISTORICAL_FIGURES


class PersonalityScores(TypedDict):
    """性格维度得分"""
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float


class MatchResult(TypedDict):
    """匹配结果"""
    figure_id: int
    name: str
    similarity: float  # 0-100


def calculate_personality_scores(answers: dict[int, int]) -> PersonalityScores:
    """
    根据答题情况计算五大人格维度得分
    
    Args:
        answers: {question_id: score}，score为1-5
    
    Returns:
        PersonalityScores字典，包含5个维度的0-100分数
    """
    from .personality_data import PERSONALITY_QUESTIONS
    
    # 初始化维度计数和得分
    dimension_scores = {
        "openness": {"sum": 0, "count": 0},
        "conscientiousness": {"sum": 0, "count": 0},
        "extraversion": {"sum": 0, "count": 0},
        "agreeableness": {"sum": 0, "count": 0},
        "neuroticism": {"sum": 0, "count": 0},
    }
    
    # 处理每个答案
    question_dict = {q["id"]: q for q in PERSONALITY_QUESTIONS}
    
    for question_id, answer_score in answers.items():
        if question_id not in question_dict:
            continue
        
        question = question_dict[question_id]
        dimension = question["dimension"]
        
        # 反向题需要反转分数
        if question["is_reverse"]:
            score = 6 - answer_score  # 1->5, 2->4, 3->3, 4->2, 5->1
        else:
            score = answer_score
        
        dimension_scores[dimension]["sum"] += score
        dimension_scores[dimension]["count"] += 1
    
    # 计算每个维度的平均分并转换为0-100分
    result = {}
    for dimension, data in dimension_scores.items():
        if data["count"] > 0:
            # 平均分是1-5，转换为0-100
            avg_score = data["sum"] / data["count"]
            normalized_score = ((avg_score - 1) / 4) * 100
            result[dimension] = round(normalized_score, 2)
        else:
            result[dimension] = 0.0
    
    return result


def calculate_similarity(user_scores: PersonalityScores, figure: dict) -> float:
    """
    计算用户与历史人物的相似度（欧氏距离的倒数）
    
    Args:
        user_scores: 用户的五大人格维度得分
        figure: 历史人物数据
    
    Returns:
        相似度百分比 (0-100)
    """
    dimensions = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]
    
    # 计算欧氏距离
    sum_of_squares = 0
    for dim in dimensions:
        user_score = user_scores[dim]
        figure_score = figure[dim]
        sum_of_squares += (user_score - figure_score) ** 2
    
    euclidean_distance = sqrt(sum_of_squares)
    
    # 将距离转换为相似度百分比
    # 最大距离是 sqrt(100^2 * 5) ≈ 223.6
    max_distance = sqrt(5 * (100 ** 2))
    similarity = 100 * (1 - euclidean_distance / max_distance)
    
    return round(max(0, similarity), 2)


def find_top_matches(user_scores: PersonalityScores, limit: int = 3) -> list[MatchResult]:
    """
    找到与用户最匹配的历史人物
    
    Args:
        user_scores: 用户的五大人格维度得分
        limit: 返回的匹配数量
    
    Returns:
        按相似度排序的匹配结果列表
    """
    matches = []
    
    for figure in HISTORICAL_FIGURES:
        similarity = calculate_similarity(user_scores, figure)
        matches.append({
            "figure_id": figure["id"],
            "name": figure["name"],
            "similarity": similarity,
        })
    
    # 按相似度排序
    matches.sort(key=lambda x: x["similarity"], reverse=True)
    
    return matches[:limit]


def get_dimension_interpretation(dimension: str, score: float) -> dict:
    """
    获取维度得分的解释
    
    Args:
        dimension: 维度名称
        score: 得分 (0-100)
    
    Returns:
        包含维度解释的字典
    """
    dim_info = PERSONALITY_DIMENSIONS.get(dimension, {})
    
    if score >= 75:
        level = "高"
        description = dim_info.get("high", "")
    elif score >= 50:
        level = "中等"
        description = f"既有{dim_info.get('high', '')}的特点，也有一些{dim_info.get('low', '')}的倾向"
    else:
        level = "低"
        description = dim_info.get("low", "")
    
    return {
        "dimension": dimension,
        "name": dim_info.get("name", dimension),
        "score": score,
        "level": level,
        "description": description,
    }


def generate_summary(user_scores: PersonalityScores, top_matches: list[MatchResult]) -> str:
    """
    生成性格测试的总体总结
    
    Args:
        user_scores: 用户的五大人格维度得分
        top_matches: 前3个匹配的历史人物
    
    Returns:
        总结文本
    """
    # 找出最强和最弱的维度
    sorted_dims = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)
    strongest_dim = sorted_dims[0]
    weakest_dim = sorted_dims[-1]
    
    strongest_name = PERSONALITY_DIMENSIONS[strongest_dim[0]]["name"]
    weakest_name = PERSONALITY_DIMENSIONS[weakest_dim[0]]["name"]
    
    top_match = top_matches[0] if top_matches else None
    
    summary = f"你在{strongest_name}维度得分最高({strongest_dim[1]:.0f}分)，"
    summary += f"在{weakest_name}维度相对较低({weakest_dim[1]:.0f}分)。"
    
    if top_match:
        summary += f"\n与历史人物{top_match['name']}的性格相似度最高，达到{top_match['similarity']:.1f}%。"
    
    return summary
