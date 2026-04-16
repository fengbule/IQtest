from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MANIFESTS_DIR = Path(__file__).parent / "fun_quiz_data" / "manifests"


def load_all_fun_quiz_manifests() -> list[dict[str, Any]]:
    if not MANIFESTS_DIR.exists():
        return []
    manifests = []
    for json_file in sorted(MANIFESTS_DIR.glob("*.json")):
        with open(json_file, encoding="utf-8") as f:
            manifests.append(json.load(f))
    return manifests


def load_fun_quiz_manifest(slug: str) -> dict[str, Any] | None:
    manifest_path = MANIFESTS_DIR / f"{slug}.json"
    if not manifest_path.exists():
        return None
    with open(manifest_path, encoding="utf-8") as f:
        return json.load(f)


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors = []
    required_fields = ["slug", "title", "questions", "results"]
    for field in required_fields:
        if field not in manifest:
            errors.append(f"Missing required field: {field}")
    if "questions" in manifest:
        for i, q in enumerate(manifest["questions"]):
            if "id" not in q:
                errors.append(f"Question {i} missing 'id' field")
            if "options" not in q:
                errors.append(f"Question {i} missing 'options' field")
            elif not isinstance(q["options"], list):
                errors.append(f"Question {i} 'options' must be a list")
            elif len(q["options"]) == 0:
                errors.append(f"Question {i} 'options' cannot be empty")
    if "results" in manifest:
        for i, r in enumerate(manifest["results"]):
            if "key" not in r:
                errors.append(f"Result {i} missing 'key' field")
            if "name" not in r:
                errors.append(f"Result {i} missing 'name' field")
    return errors