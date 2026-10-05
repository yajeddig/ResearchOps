"""
Semantic Scholar paper dedup for WF2 — data/monitor_seen.json, keyed by S2
paperId rather than a URL hash: paperId is stable across query phrasing,
recommendation vs. search, and DOI/arXiv resolution, so it survives being
found again through a different path next month.
"""
import json
from datetime import date
from pathlib import Path

SEEN_FILE = Path("data/monitor_seen.json")


def load_seen() -> dict:
    if not SEEN_FILE.exists():
        return {}
    try:
        return json.loads(SEEN_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_seen(seen: dict) -> None:
    SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    SEEN_FILE.write_text(json.dumps(seen, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def mark_seen(seen: dict, paper_id: str, report_date: date | None = None) -> None:
    """Record paper_id as seen, keeping the earliest date if already present."""
    if paper_id not in seen:
        seen[paper_id] = (report_date or date.today()).isoformat()
