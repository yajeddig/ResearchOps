"""
Append-only WF1 outcome log (data/ingest_log.jsonl), one JSON line per issue
processed. Read by WF2 to render the monthly "pipeline health" section.

Never logs captured content, titles or any PII — status/reason codes and
category only, same discipline as the PII gate's own notifications.
"""
import json
from datetime import date, datetime
from pathlib import Path

LOG_FILE = Path("data/ingest_log.jsonl")


def log_outcome(
    status: str,
    reason: str | None = None,
    category: str | None = None,
    new_tag_candidates: list[str] | None = None,
) -> None:
    entry = {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "reason": reason,
        "category": category,
        "new_tag_candidates": new_tag_candidates,
    }
    entry = {k: v for k, v in entry.items() if v is not None}
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def load_entries(period_start: date, period_end: date) -> list[dict]:
    """Entries whose timestamp falls within [period_start, period_end], inclusive."""
    if not LOG_FILE.exists():
        return []
    entries = []
    for line in LOG_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
            ts = datetime.fromisoformat(entry["timestamp"]).date()
        except (json.JSONDecodeError, KeyError, ValueError):
            continue
        if period_start <= ts <= period_end:
            entries.append(entry)
    return entries
