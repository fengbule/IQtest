from __future__ import annotations

from sqlalchemy import inspect
from sqlalchemy.engine import Engine


REQUIRED_COLUMNS = {
    "questions": {
        "difficulty_weight": "FLOAT DEFAULT 1.2",
        "tags": "TEXT",
        "estimated_seconds": "INTEGER DEFAULT 35",
    },
    "test_attempts": {
        "answered_count": "INTEGER DEFAULT 0",
        "accuracy_score": "FLOAT DEFAULT 0",
        "difficulty_score": "FLOAT DEFAULT 0",
        "completion_score": "FLOAT DEFAULT 0",
        "response_quality_score": "FLOAT DEFAULT 0",
        "cpi_score": "INTEGER DEFAULT 40",
        "estimated_iq": "INTEGER DEFAULT 100",
        "ability_level": "VARCHAR(4) DEFAULT 'E'",
        "iq_range": "VARCHAR(32) DEFAULT '90 以下参考区间'",
        "validity_flag": "VARCHAR(16) DEFAULT 'low'",
        "validity_note": "TEXT DEFAULT ''",
        "summary": "TEXT DEFAULT ''",
        "math_score": "FLOAT DEFAULT 0",
        "logic_score": "FLOAT DEFAULT 0",
        "verbal_score": "FLOAT DEFAULT 0",
        "spatial_score": "FLOAT DEFAULT 0",
    },
    "attempt_answers": {
        "question_order": "INTEGER DEFAULT 0",
        "question_dimension": "VARCHAR(50) DEFAULT ''",
        "question_difficulty": "VARCHAR(20) DEFAULT 'medium'",
        "question_weight": "FLOAT DEFAULT 1.2",
        "estimated_seconds": "INTEGER DEFAULT 35",
        "prompt_snapshot": "TEXT DEFAULT ''",
        "correct_answer_snapshot": "VARCHAR(1) DEFAULT ''",
        "explanation_snapshot": "TEXT DEFAULT ''",
        "time_spent_seconds": "INTEGER DEFAULT 0",
    },
}


def apply_lightweight_migrations(engine: Engine) -> None:
    inspector = inspect(engine)
    with engine.begin() as connection:
        for table_name, column_map in REQUIRED_COLUMNS.items():
            if not inspector.has_table(table_name):
                continue
            existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
            for column_name, ddl in column_map.items():
                if column_name in existing_columns:
                    continue
                connection.exec_driver_sql(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {ddl}")
