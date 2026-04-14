from __future__ import annotations

import random
from collections import defaultdict


DIMENSIONS = ["numerical", "logical", "verbal", "spatial"]
QUESTION_PLAN = {
    "easy": 2,
    "medium": 4,
    "hard": 2,
}
TIME_LIMIT_SECONDS = 25 * 60


def sample_questions(question_rows: list) -> list:
    bucketed = defaultdict(list)
    for row in question_rows:
        bucketed[(row.category, row.difficulty)].append(row)

    selected = []
    for dimension in DIMENSIONS:
        for difficulty, count in QUESTION_PLAN.items():
            pool = list(bucketed[(dimension, difficulty)])
            if len(pool) < count:
                raise ValueError(
                    f"Question pool is insufficient for {dimension}/{difficulty}: "
                    f"need {count}, got {len(pool)}"
                )
            selected.extend(random.sample(pool, count))

    random.shuffle(selected)
    return selected
