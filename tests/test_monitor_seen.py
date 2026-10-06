"""Tests for utils/monitor_seen.py (WF2 paper-level dedup, keyed by S2 paperId)."""
from datetime import date

from utils import monitor_seen


def test_load_seen_missing_file_returns_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(monitor_seen, "SEEN_FILE", tmp_path / "nope.json")
    assert monitor_seen.load_seen() == {}


def test_mark_seen_then_save_then_reload(tmp_path, monkeypatch):
    path = tmp_path / "monitor_seen.json"
    monkeypatch.setattr(monitor_seen, "SEEN_FILE", path)

    seen = {}
    monitor_seen.mark_seen(seen, "paper123", date(2026, 9, 1))
    monitor_seen.save_seen(seen)

    reloaded = monitor_seen.load_seen()
    assert reloaded == {"paper123": "2026-09-01"}


def test_mark_seen_keeps_earliest_date(tmp_path, monkeypatch):
    seen = {"paper123": "2026-01-01"}
    monitor_seen.mark_seen(seen, "paper123", date(2026, 9, 1))
    assert seen["paper123"] == "2026-01-01"


def test_load_seen_tolerates_corrupt_file(tmp_path, monkeypatch):
    path = tmp_path / "monitor_seen.json"
    path.write_text("not json", encoding="utf-8")
    monkeypatch.setattr(monitor_seen, "SEEN_FILE", path)
    assert monitor_seen.load_seen() == {}
