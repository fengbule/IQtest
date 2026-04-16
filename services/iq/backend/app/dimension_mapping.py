from __future__ import annotations

LEGACY_DIMENSIONS = ["numerical", "logical", "verbal", "spatial"]

CATEGORY_TO_DIMENSION = {
    # Legacy categories
    "numerical": "numerical",
    "logical": "logical",
    "verbal": "verbal",
    "spatial": "spatial",
    # Current question bank categories
    "matrix": "numerical",
    "series": "numerical",
    "logic": "logical",
    "pattern": "logical",
    "deduction": "logical",
    "analogy": "verbal",
    "classification": "verbal",
    "memory": "verbal",
    "folding": "spatial",
    "cube": "spatial",
    "rotation": "spatial",
}


def normalize_dimension(category: str) -> str:
    return CATEGORY_TO_DIMENSION.get(category, category)
