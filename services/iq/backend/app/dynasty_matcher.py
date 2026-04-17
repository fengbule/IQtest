"""
历史朝代人物匹配算法
方案A：原型累计得分 + 风格向量 + 余弦相似度
"""

from typing import TypedDict
from math import sqrt
from .dynasty_data import (
    PROTOTYPES,
    HISTORICAL_FIGURES,
    TRAIT_DIMENSIONS,
    get_characters_for_dynasty,
    get_prototypes_for_dynasty,
)


class TraitVector(TypedDict):
    """风格维度得分"""
    leadership: float
    strategy: float
    execution: float
    idealism: float
    diplomacy: float
    risk: float
    order: float
    expression: float
    resilience: float
    control: float


class PrototypeScores(TypedDict):
    """原型得分"""
    leader: float
    strategist: float
    champion: float
    balancer: float
    stoic: float
    executor: float
    idealist: float
    diplomat: float


class MatchResult(TypedDict):
    """匹配结果"""
    character_id: str
    name: str
    dynasty: str
    title: str
    role_label: str
    summary: str
    description: str
    similarity: float
    prototype_score: float
    cosine_similarity: float
    tags: list[str]


def normalize_vector(vector: dict) -> dict:
    """
    将向量归一化（L2范数）
    
    Args:
        vector: 待归一化的向量
    
    Returns:
        归一化后的向量
    """
    # 计算L2范数
    magnitude = sqrt(sum(v ** 2 for v in vector.values()))
    if magnitude == 0:
        return {k: 0.0 for k in vector}
    
    # 归一化
    return {k: v / magnitude for k, v in vector.items()}


def cosine_similarity(vec1: dict, vec2: dict) -> float:
    """
    计算两个向量的余弦相似度
    
    Args:
        vec1: 第一个向量
        vec2: 第二个向量
    
    Returns:
        余弦相似度 (-1 到 1)
    """
    # 计算点积
    dot_product = sum(vec1.get(k, 0) * vec2.get(k, 0) for k in set(vec1) | set(vec2))
    
    # 计算模长
    mag1 = sqrt(sum(v ** 2 for v in vec1.values()))
    mag2 = sqrt(sum(v ** 2 for v in vec2.values()))
    
    if mag1 == 0 or mag2 == 0:
        return 0.0
    
    return dot_product / (mag1 * mag2)


def init_trait_vector() -> TraitVector:
    """初始化空的风格向量"""
    return {dim: 0.0 for dim in TRAIT_DIMENSIONS}


def init_prototype_scores() -> PrototypeScores:
    """初始化原型得分"""
    return {p["id"]: 0.0 for p in PROTOTYPES}


def calculate_result(
    answers: list[dict],
    dynasty_id: str,
    prototype_weight: float = 0.6,
    cosine_weight: float = 0.4,
) -> list[MatchResult]:
    """
    计算用户在指定朝代的人格匹配结果
    
    三阶段匹配算法：
    1. 题目答案累计到原型分
    2. 题目答案累计到风格维度向量
    3. 计算综合得分 = 原型权重 × 原型分 + 余弦权重 × 余弦相似度
    
    Args:
        answers: 用户答案列表，每项包含 prototype_scores 和 trait_delta
        dynasty_id: 朝代ID
        prototype_weight: 原型得分权重，默认0.6
        cosine_weight: 余弦相似度权重，默认0.4
    
    Returns:
        按综合得分降序排列的前3名匹配结果
    """
    # 初始化
    prototype_totals = init_prototype_scores()
    trait_vector = init_trait_vector()
    
    # 阶段1&2：累计原型分和风格向量
    for answer in answers:
        # 累加原型分
        prototype_scores = answer.get("prototype_scores", {})
        for proto_id, score in prototype_scores.items():
            if proto_id in prototype_totals:
                prototype_totals[proto_id] += score
        
        # 累加风格向量
        trait_delta = answer.get("trait_delta", {})
        for trait, delta in trait_delta.items():
            if trait in trait_vector:
                trait_vector[trait] += delta
    
    # 归一化原型得分（0-100）
    max_prototype_score = max(prototype_totals.values()) if max(prototype_totals.values()) > 0 else 1
    normalized_prototypes = {
        k: (v / max_prototype_score) * 100 for k, v in prototype_totals.items()
    }
    
    # 归一化风格向量
    normalized_traits = normalize_vector(trait_vector)
    
    # 获取该朝代的人物
    characters = get_characters_for_dynasty(dynasty_id)
    
    # 阶段3：计算每个人物与用户的相似度
    results = []
    user_trait_vector = {k: normalized_traits.get(k, 0) * 100 for k in TRAIT_DIMENSIONS}
    
    for character in characters:
        # 原型得分
        prototype_id = character.get("prototype_id", "")
        prototype_score = normalized_prototypes.get(prototype_id, 0)
        
        # 余弦相似度
        character_vector = character.get("vector", {})
        normalized_char_vector = normalize_vector(character_vector)
        cosine = cosine_similarity(normalized_traits, normalized_char_vector)
        cosine_100 = (cosine + 1) / 2 * 100  # 转换到0-100
        
        # 综合得分
        final_score = prototype_weight * prototype_score + cosine_weight * cosine_100
        
        results.append({
            "character_id": character["id"],
            "name": character["name"],
            "dynasty": character["dynasty"],
            "title": character.get("title", ""),
            "role_label": character.get("role_label", ""),
            "summary": character.get("summary", ""),
            "description": character.get("description", ""),
            "similarity": round(final_score, 1),
            "prototype_score": round(prototype_score, 1),
            "cosine_similarity": round(cosine_100, 1),
            "tags": character.get("tags", []),
            "similarities": character.get("similarities", []),
            "differences": character.get("differences", []),
        })
    
    # 按综合得分降序排列
    results.sort(key=lambda x: x["similarity"], reverse=True)
    
    return results[:3]


def get_dominant_prototype(prototype_scores: dict) -> tuple[str, float]:
    """
    获取得分最高的原型
    
    Args:
        prototype_scores: 原型得分字典
    
    Returns:
        (原型ID, 得分)
    """
    if not prototype_scores:
        return ("leader", 0.0)
    
    max_proto = max(prototype_scores.items(), key=lambda x: x[1])
    return (max_proto[0], max_proto[1])


def get_prototype_name(prototype_id: str) -> str:
    """获取原型的中文名称"""
    for p in PROTOTYPES:
        if p["id"] == prototype_id:
            return p["name"]
    return prototype_id


def get_prototype_description(prototype_id: str) -> str:
    """获取原型的描述"""
    for p in PROTOTYPES:
        if p["id"] == prototype_id:
            return p["description"]
    return ""


def generate_result_summary(top_matches: list[MatchResult], dynasty_name: str) -> str:
    """
    生成结果总结文本
    
    Args:
        top_matches: 前3名匹配结果
        dynasty_name: 朝代名称
    
    Returns:
        总结文本
    """
    if not top_matches:
        return f"抱歉，{dynasty_name}暂无足够数据生成结果。"
    
    main_match = top_matches[0]
    
    summary = f"在{dynasty_name}时代，你的气质最接近{main_match['name']}——{main_match['role_label']}。"
    
    if len(top_matches) > 1:
        second = top_matches[1]
        summary += f"\n\n此外，你还具有与{second['name']}相似的特质，展现出多样的性格面向。"
    
    return summary
