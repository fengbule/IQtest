from __future__ import annotations

import random
from collections import defaultdict

from .dimension_mapping import LEGACY_DIMENSIONS, normalize_dimension


DIMENSIONS = LEGACY_DIMENSIONS
STANDARD_IQ_CATEGORY_BLUEPRINT = {
    "numerical": {"matrix", "series"},
    "logical": {"logic", "pattern", "deduction"},
    "verbal": {"analogy", "classification", "memory", "verbal"},
    "spatial": {"folding", "cube", "rotation", "spatial"},
}
QUESTION_PLAN = {
    "easy": 2,
    "medium": 4,
    "hard": 2,
}
TIME_LIMIT_SECONDS = 25 * 60


def pick_questions_with_type_coverage(rows: list, count: int, avoid_question_ids: set[int]) -> list:
    by_category = defaultdict(list)
    for row in rows:
        by_category[row.category].append(row)

    for category_rows in by_category.values():
        random.shuffle(category_rows)

    categories = list(by_category.keys())
    random.shuffle(categories)

    selected = []
    used_ids = set()

    category_slots = categories[: min(count, len(categories))]
    for category in category_slots:
        preferred = [row for row in by_category[category] if row.id not in avoid_question_ids]
        fallback = [row for row in by_category[category] if row.id in avoid_question_ids]
        pick_source = preferred if preferred else fallback
        if not pick_source:
            continue
        picked = random.choice(pick_source)
        selected.append(picked)
        used_ids.add(picked.id)

    if len(selected) >= count:
        return selected[:count]

    remaining_fresh = [row for row in rows if row.id not in avoid_question_ids and row.id not in used_ids]
    random.shuffle(remaining_fresh)
    selected.extend(remaining_fresh[: count - len(selected)])
    used_ids.update(row.id for row in selected)

    if len(selected) >= count:
        return selected[:count]

    remaining_fallback = [row for row in rows if row.id in avoid_question_ids and row.id not in used_ids]
    random.shuffle(remaining_fallback)
    selected.extend(remaining_fallback[: count - len(selected)])
    return selected


def validate_selection(selected: list) -> None:
    distribution = defaultdict(int)
    category_coverage = defaultdict(set)
    for row in selected:
        distribution[(normalize_dimension(row.category), row.difficulty)] += 1
        category_coverage[normalize_dimension(row.category)].add(row.category)

    for dimension in DIMENSIONS:
        for difficulty, required in QUESTION_PLAN.items():
            actual = distribution[(dimension, difficulty)]
            if actual != required:
                raise ValueError(
                    f"Question selection distribution mismatch for {dimension}/{difficulty}: "
                    f"need {required}, got {actual}"
                )

    for dimension, required_categories in STANDARD_IQ_CATEGORY_BLUEPRINT.items():
        missing = required_categories - category_coverage[dimension]
        if missing:
            raise ValueError(
                f"Question selection lacks standard IQ categories for {dimension}: "
                f"missing {sorted(missing)}"
            )


def validate_pool_against_blueprint(question_rows: list) -> None:
    distribution = defaultdict(int)
    category_coverage = defaultdict(set)
    for row in question_rows:
        dimension = normalize_dimension(row.category)
        distribution[(dimension, row.difficulty)] += 1
        category_coverage[dimension].add(row.category)

    for dimension in DIMENSIONS:
        for difficulty, required in QUESTION_PLAN.items():
            actual = distribution[(dimension, difficulty)]
            if actual < required:
                raise ValueError(
                    f"Question pool is insufficient for {dimension}/{difficulty}: "
                    f"need {required}, got {actual}"
                )

    for dimension, required_categories in STANDARD_IQ_CATEGORY_BLUEPRINT.items():
        missing = required_categories - category_coverage[dimension]
        if missing:
            raise ValueError(
                f"Question pool lacks standard IQ categories for {dimension}: "
                f"missing {sorted(missing)}"
            )


def sample_questions(question_rows: list, avoid_question_ids: set[int] | None = None) -> list:
    validate_pool_against_blueprint(question_rows)

    bucketed = defaultdict(list)
    avoid_question_ids = set(avoid_question_ids or set())
    for row in question_rows:
        bucketed[(normalize_dimension(row.category), row.difficulty)].append(row)

    for _ in range(12):
        selected = []
        for dimension in DIMENSIONS:
            for difficulty, count in QUESTION_PLAN.items():
                pool = list(bucketed[(dimension, difficulty)])
                picked = pick_questions_with_type_coverage(pool, count, avoid_question_ids)
                if len(picked) != count:
                    raise ValueError(
                        f"Question pool is insufficient after applying coverage for {dimension}/{difficulty}: "
                        f"need {count}, got {len(picked)}"
                    )
                selected.extend(picked)

        try:
            validate_selection(selected)
            random.shuffle(selected)
            return selected
        except ValueError:
            continue

    raise ValueError("Failed to assemble a standard-IQ-compliant question set after retries")
