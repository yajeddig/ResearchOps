"""
Faceted taxonomy (P3): one category + sectors + controlled tags + optional
projects, all closed enums built from config files, shared by WF1 (capture)
and scripts/migrate_taxonomy.py (re-classification of existing cards).

Structured outputs can't express array-length or numeric bounds, so those
(1-5 tags, <= 3 tag candidates, confidence in [0, 1]) are enforced by
validate_facets() after the response, not by the schema.
"""
import json
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"
INBOX = "_Inbox"
MAX_TAGS = 5
MAX_TAG_CANDIDATES = 3


def load_categories(config_dir: Path = CONFIG_DIR) -> dict:
    return json.loads((config_dir / "categories.json").read_text(encoding="utf-8"))


def load_tags(config_dir: Path = CONFIG_DIR) -> list[str]:
    return json.loads((config_dir / "tags.json").read_text(encoding="utf-8"))["tags"]


def load_projects(config_dir: Path = CONFIG_DIR) -> list[dict]:
    """Project list from the git-ignored projects.local.json; [] (facet disabled) when absent."""
    path = config_dir / "projects.local.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8")).get("projects", [])


class Taxonomy:
    def __init__(self, config_dir: Path = CONFIG_DIR):
        config = load_categories(config_dir)
        self.categories: dict[str, str] = {
            name: data["description"] for name, data in config["categories"].items() if name != INBOX
        }
        self.sectors: list[str] = config["sector_tags"]
        self.settings: dict = config["settings"]
        self.tags: list[str] = load_tags(config_dir)
        self.projects: list[dict] = load_projects(config_dir)

    def facet_properties(self) -> dict:
        props = {
            "category": {"type": "string", "enum": list(self.categories)},
            "confidence": {"type": "number", "description": "0 to 1"},
            "sectors": {"type": "array", "items": {"type": "string", "enum": self.sectors}},
            "tags": {"type": "array", "items": {"type": "string", "enum": self.tags},
                     "description": f"1 to {MAX_TAGS} tags from the controlled vocabulary"},
            "new_tag_candidates": {"type": "array", "items": {"type": "string"},
                                   "description": f"0 to {MAX_TAG_CANDIDATES} short kebab-case tags missing from the vocabulary"},
        }
        if self.projects:
            props["projects"] = {"type": "array", "items": {"type": "string", "enum": [p["id"] for p in self.projects]}}
        return props

    def output_schema(self, extra_properties: dict | None = None) -> dict:
        """JSON schema for output_config.format: facets (+ extra fields), every field required."""
        props = {**(extra_properties or {}), **self.facet_properties()}
        return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}

    def system_prompt(self) -> str:
        """Stable taxonomy description — the cacheable prefix of every classification call."""
        lines = [
            "You classify content for a process engineering / industrial data science knowledge base.",
            "",
            "CATEGORY (exactly one — the main subject of the content):",
            *[f"- {name}: {desc}" for name, desc in self.categories.items()],
            "",
            f"TAGS: 1 to {MAX_TAGS} tags, only from the controlled vocabulary in the schema enum. "
            "Pick the most specific tags that describe methods, equipment or topics actually covered.",
            "Controlled vocabulary: " + ", ".join(self.tags),
            f"NEW_TAG_CANDIDATES: if an important concept has no matching tag, propose up to {MAX_TAG_CANDIDATES} "
            "short kebab-case candidates; otherwise an empty list.",
            "SECTORS: 0 or more industrial sectors from the enum, only if the content is explicitly about them.",
        ]
        if self.projects:
            lines += ["", "PROJECTS (0 or more, only if the content is clearly relevant to the project):",
                      *[f"- {p['id']}: {p.get('description', '')}" for p in self.projects]]
        lines += ["", "CONFIDENCE: how sure you are of the category, from 0 to 1."]
        return "\n".join(lines)

    def validate_facets(self, result: dict) -> dict:
        """Enforce the bounds the schema can't, and drop anything off-vocabulary (e.g. after a fallback model)."""
        result = dict(result)
        try:
            confidence = float(result.get("confidence", 0.0) or 0.0)
        except (TypeError, ValueError):
            confidence = 0.0
        result["confidence"] = min(max(confidence, 0.0), 1.0)
        result["tags"] = _dedupe([t for t in result.get("tags", []) if t in self.tags])[:MAX_TAGS]
        result["sectors"] = _dedupe([s for s in result.get("sectors", []) if s in self.sectors])
        project_ids = {p["id"] for p in self.projects}
        result["projects"] = _dedupe([p for p in result.get("projects", []) if p in project_ids])
        candidates = [str(c).strip().lower() for c in result.get("new_tag_candidates", []) if str(c).strip()]
        result["new_tag_candidates"] = _dedupe([c for c in candidates if c not in self.tags])[:MAX_TAG_CANDIDATES]
        return result


def _dedupe(items: list) -> list:
    return list(dict.fromkeys(items))
