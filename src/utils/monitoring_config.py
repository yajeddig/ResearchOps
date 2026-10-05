"""
Validated loader for config/monitoring.json (WF2 academic watch topics).

Schema v2, backward compatible with v1: a v1 topic (id, name,
keywords_academic, keywords_news, paper_limit) loads as-is, with the new
fields (status, priority, projects, exclude_keywords, seed_paper_ids,
negative_paper_ids, min_year) defaulted.
"""
import json
from pathlib import Path

import jsonschema

TOPIC_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string", "minLength": 1},
        "name": {"type": "string", "minLength": 1},
        "status": {"type": "string", "enum": ["active", "paused"]},
        "priority": {"type": "integer", "minimum": 1},
        "projects": {"type": "array", "items": {"type": "string"}},
        "keywords_academic": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "keywords_news": {"type": "array", "items": {"type": "string"}},
        "exclude_keywords": {"type": "array", "items": {"type": "string"}},
        "seed_paper_ids": {"type": "array", "items": {"type": "string"}},
        "negative_paper_ids": {"type": "array", "items": {"type": "string"}},
        "min_year": {"type": ["integer", "null"]},
        "paper_limit": {"type": "integer", "minimum": 1},
    },
    "required": ["id", "name", "keywords_academic"],
    "additionalProperties": False,
}

SCHEMA = {
    "type": "object",
    "properties": {"topics": {"type": "array", "items": TOPIC_SCHEMA, "minItems": 1}},
    "required": ["topics"],
    "additionalProperties": False,
}

DEFAULTS = {
    "status": "active",
    "priority": 3,
    "projects": [],
    "keywords_news": [],
    "exclude_keywords": [],
    "seed_paper_ids": [],
    "negative_paper_ids": [],
    "min_year": None,
    "paper_limit": 3,
}


def load_topics(path: str | Path = "config/monitoring.json", active_only: bool = True) -> list[dict]:
    """
    Load, validate and default-fill monitoring.json's topics.
    Raises ValueError with a precise, human-readable message on a malformed
    config rather than letting a KeyError/jsonschema traceback surface.
    """
    path = Path(path)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path} illisible ou n'est pas du JSON valide : {exc}") from exc

    try:
        jsonschema.validate(raw, SCHEMA)
    except jsonschema.ValidationError as exc:
        location = "/".join(str(p) for p in exc.path) or "racine"
        raise ValueError(f"{path} invalide à '{location}' : {exc.message}") from exc

    topics = []
    seen_ids: set[str] = set()
    for topic in raw["topics"]:
        if topic["id"] in seen_ids:
            raise ValueError(f"{path} invalide : id de sujet dupliqué '{topic['id']}'")
        seen_ids.add(topic["id"])
        topics.append({**DEFAULTS, **topic})

    if active_only:
        topics = [t for t in topics if t["status"] == "active"]
    return sorted(topics, key=lambda t: t["priority"])
