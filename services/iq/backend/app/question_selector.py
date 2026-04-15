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


def sample_questions(question_rows: list, avoid_question_ids: set[int] | None = None) -> list:
    bucketed = defaultdict(list)
    avoid_question_ids = set(avoid_question_ids or set())
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
            fresh_pool = [row for row in pool if row.id not in avoid_question_ids]
            if len(fresh_pool) >= count:
                selected.extend(random.sample(fresh_pool, count))
                continue

            fallback_pool = [row for row in pool if row.id in avoid_question_ids]
            selected.extend(fresh_pool)
            selected.extend(random.sample(fallback_pool, count - len(fresh_pool)))

    random.shuffle(selected)
    return selected
