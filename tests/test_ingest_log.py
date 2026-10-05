"""Tests for utils/ingest_log.py (WF1 outcome log read by WF2's health section)."""
from datetime import date

from utils import ingest_log


def test_log_outcome_appends_a_json_line(tmp_path, monkeypatch):
    path = tmp_path / "ingest_log.jsonl"
    monkeypatch.setattr(ingest_log, "LOG_FILE", path)

    ingest_log.log_outcome("rejected", reason="too_short")
    ingest_log.log_outcome("saved", category="Process_Engineering")

    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2


def test_log_outcome_omits_none_fields(tmp_path, monkeypatch):
    path = tmp_path / "ingest_log.jsonl"
    monkeypatch.setattr(ingest_log, "LOG_FILE", path)

    ingest_log.log_outcome("saved", category="Process_Engineering")

    assert "reason" not in path.read_text(encoding="utf-8")


def test_load_entries_filters_by_period(tmp_path, monkeypatch):
    path = tmp_path / "ingest_log.jsonl"
    path.write_text(
        '{"timestamp": "2026-08-31T23:00:00", "status": "saved"}\n'
        '{"timestamp": "2026-09-15T10:00:00", "status": "rejected", "reason": "too_short"}\n'
        '{"timestamp": "2026-10-01T00:00:00", "status": "saved"}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(ingest_log, "LOG_FILE", path)

    entries = ingest_log.load_entries(date(2026, 9, 1), date(2026, 9, 30))

    assert len(entries) == 1
    assert entries[0]["status"] == "rejected"


def test_load_entries_skips_malformed_lines(tmp_path, monkeypatch):
    path = tmp_path / "ingest_log.jsonl"
    path.write_text('not json\n{"timestamp": "2026-09-15T10:00:00", "status": "saved"}\n\n', encoding="utf-8")
    monkeypatch.setattr(ingest_log, "LOG_FILE", path)

    entries = ingest_log.load_entries(date(2026, 9, 1), date(2026, 9, 30))

    assert len(entries) == 1


def test_load_entries_missing_file_returns_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(ingest_log, "LOG_FILE", tmp_path / "nope.jsonl")
    assert ingest_log.load_entries(date(2026, 9, 1), date(2026, 9, 30)) == []


def test_log_outcome_records_tag_candidates(tmp_path, monkeypatch):
    path = tmp_path / "ingest_log.jsonl"
    monkeypatch.setattr(ingest_log, "LOG_FILE", path)

    ingest_log.log_outcome("saved", category="Hybrid_SciML", new_tag_candidates=["latent-sde"])

    assert '"new_tag_candidates": ["latent-sde"]' in path.read_text(encoding="utf-8")
