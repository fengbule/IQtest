"""
历史朝代人物匹配 - 朝代配置数据
方案A：朝代 → 原型 → 人物 三层结构
"""

from typing import TypedDict
from .dynasty_data import (
    DYNASTIES,
    PROTOTYPES,
    HISTORICAL_FIGURES,
    DYNASTY_QUESTIONS,
    TRAIT_DIMENSIONS,
    get_dynasty_config,
    get_prototypes_for_dynasty,
    get_characters_for_dynasty,
    get_questions_for_dynasty,
)

__all__ = [
    "DYNASTIES",
    "PROTOTYPES", 
    "HISTORICAL_FIGURES",
    "DYNASTY_QUESTIONS",
    "TRAIT_DIMENSIONS",
    "get_dynasty_config",
    "get_prototypes_for_dynasty",
    "get_characters_for_dynasty",
    "get_questions_for_dynasty",
]
