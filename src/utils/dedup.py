"""
Deduplication based on data/history.json.

Two kinds of keys coexist in the history file:
- URL keys: md5(url)[:8]  (legacy format, kept for backward compatibility with
  the ~90 entries already recorded).
- Content keys: sha256(bytes)[:12], used for every capture (text, image, PDF)
  so that the same document sent twice is detected even without a URL.
"""
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

HISTORY_FILE = Path("data/history.json")


def load_history() -> dict:
    if not HISTORY_FILE.exists():
        return {}
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_history(data: dict) -> None:
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def compute_hash(url: str) -> str:
    """Legacy URL key (md5, 8 hex chars). Kept stable so old entries still match."""
    return hashlib.md5(url.encode("utf-8")).hexdigest()[:8]


def content_hash(data: Union[str, bytes]) -> str:
    """Content key (sha256, 12 hex chars) over the raw captured bytes."""
    if isinstance(data, str):
        data = data.encode("utf-8", errors="ignore")
    return hashlib.sha256(data).hexdigest()[:12]


def is_duplicate(url: Optional[str] = None, content: Optional[Union[str, bytes]] = None) -> bool:
    """True if the URL or the content was already ingested."""
    history = load_history()
    if url and compute_hash(url) in history:
        return True
    if content is not None and content_hash(content) in history:
        return True
    return False


def add_to_history(
    url: Optional[str] = None,
    content: Optional[Union[str, bytes]] = None,
    file: Optional[str] = None,
    kind: str = "capture",
) -> None:
    """Record a capture under its URL key and/or its content key."""
    history = load_history()
    now = datetime.now().isoformat()
    if url:
        history[compute_hash(url)] = {"url": url, "type": kind, "file": file, "added": now}
    if content is not None:
        history[content_hash(content)] = {"content": True, "url": url, "type": kind, "file": file, "added": now}
    save_history(history)
