"""
YAML frontmatter helpers shared by WF1 (write), WF2/WF4 (read) and the site builder.
"""
import re
from pathlib import Path

import yaml

_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)


def parse(text: str) -> tuple[dict, str]:
    """Split a markdown document into (metadata, body). Tolerant of legacy files."""
    match = _FM_RE.match(text)
    if not match:
        return {}, text
    raw, body = match.group(1), text[match.end():]
    try:
        meta = yaml.safe_load(raw) or {}
        if not isinstance(meta, dict):
            meta = {}
    except yaml.YAMLError:
        meta = _legacy_parse(raw)
    return meta, body


def _legacy_parse(raw: str) -> dict:
    """Line-based fallback for hand-written frontmatter that is not valid YAML."""
    meta = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip().strip("\"'")
        if value.startswith("[") and value.endswith("]"):
            value = [v.strip().strip("\"'") for v in value[1:-1].split(",") if v.strip()]
        meta[key.strip()] = value
    return meta


def dump(meta: dict, body: str) -> str:
    """Render a document with a YAML frontmatter block."""
    header = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False, default_flow_style=None).strip()
    return f"---\n{header}\n---\n{body.lstrip()}"


def load_cards(root: str | Path = "content") -> list[dict]:
    """Load every knowledge card: {path, category, meta, body}."""
    cards = []
    for path in sorted(Path(root).glob("**/*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        meta, body = parse(text)
        cards.append({
            "path": str(path).replace("\\", "/"),
            "category": path.parent.name,
            "meta": meta,
            "body": body,
        })
    return cards
