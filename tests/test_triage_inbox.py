"""Tests for scripts/triage_inbox.py (P1: _Inbox cleanup, no LLM call)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from utils import frontmatter  # noqa: E402
import triage_inbox  # noqa: E402

VALID_CATEGORIES = {"Data_Science", "Process_Engineering"}


def make_card(tmp_path, name, meta, body):
    inbox = tmp_path / "content" / "_Inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    path = inbox / name
    path.write_text(frontmatter.dump(meta, body), encoding="utf-8")
    return path


class TestClassifyCard:
    def test_low_confidence_is_delete(self):
        meta = {"title": "Some article", "confidence": 0.10}
        verdict, reason, category = triage_inbox.classify_card(meta, "body text " * 50, VALID_CATEGORIES, 0.3)
        assert verdict == "delete"
        assert "confidence" in reason

    def test_junk_title_is_delete(self):
        meta = {"title": "404 - Page Not Found", "confidence": 0.9}
        verdict, reason, category = triage_inbox.classify_card(meta, "content " * 200, VALID_CATEGORIES, 0.3)
        assert verdict == "delete"
        assert "junk title" in reason

    def test_pii_is_delete_even_at_high_confidence(self):
        meta = {"title": "Fiche RH", "confidence": 0.95}
        body = "Bulletin de paie, NIR 185127510823481, IBAN FR7630006000011234567890189."
        verdict, reason, category = triage_inbox.classify_card(meta, body, VALID_CATEGORIES, 0.3)
        assert verdict == "delete"
        assert reason.startswith("pii:")
        assert "185127510823481" not in reason

    def test_blocked_page_markers_in_body_is_delete(self):
        meta = {"title": "Some page", "confidence": 0.9}
        body = "Access Denied\n\nYou don't have permission to access this resource. " + ("content " * 100)
        verdict, reason, category = triage_inbox.classify_card(meta, body, VALID_CATEGORIES, 0.3)
        assert verdict == "delete"

    def test_reclassify_when_unknown_category_now_valid(self):
        meta = {"title": "Hybrid modelling of a CSTR", "confidence": 0.9}
        body = (
            "> ⚠️ **Inbox Note**: unknown category: Process_Engineering\n\n"
            + ("Real technical content about reactor modelling. " * 40)
        )
        verdict, reason, category = triage_inbox.classify_card(meta, body, VALID_CATEGORIES, 0.3)
        assert verdict == "reclassify"
        assert category == "Process_Engineering"

    def test_unknown_category_not_in_current_taxonomy_is_kept(self):
        meta = {"title": "Hybrid modelling of a CSTR", "confidence": 0.9}
        body = (
            "> ⚠️ **Inbox Note**: unknown category: Some_Retired_Category\n\n"
            + ("Real technical content about reactor modelling. " * 40)
        )
        verdict, reason, category = triage_inbox.classify_card(meta, body, VALID_CATEGORIES, 0.3)
        assert verdict == "keep"

    def test_good_content_with_no_signal_is_kept(self):
        meta = {"title": "Ambiguous but real content", "confidence": 0.45}
        body = "Real technical discussion about process control. " * 40
        verdict, reason, category = triage_inbox.classify_card(meta, body, VALID_CATEGORIES, 0.3)
        assert verdict == "keep"


class TestApply:
    def test_apply_delete_removes_file(self, tmp_path):
        path = make_card(tmp_path, "junk.md", {"title": "404", "confidence": 0.1}, "x")
        triage_inbox.apply_delete(path)
        assert not path.exists()

    def test_apply_reclassify_moves_file_and_rewrites_frontmatter(self, tmp_path):
        meta = {"title": "Real content", "confidence": 0.9, "category": "_Inbox", "tags": ["inbox:ambiguous", "n3:simulation"]}
        body = "> ⚠️ **Inbox Note**: unknown category: Process_Engineering\n\nSome real content."
        path = make_card(tmp_path, "card.md", meta, body)

        dest = triage_inbox.apply_reclassify(path, meta, body, "Process_Engineering", content_root=tmp_path / "content")

        assert not path.exists()
        assert dest.exists()
        assert dest.parent.name == "Process_Engineering"
        new_meta, new_body = frontmatter.parse(dest.read_text(encoding="utf-8"))
        assert new_meta["category"] == "Process_Engineering"
        assert "inbox:ambiguous" not in new_meta["tags"]
        assert "n3:simulation" in new_meta["tags"]
        assert "Inbox Note" not in new_body


class TestMainIntegration:
    def _setup_repo(self, tmp_path, monkeypatch):
        (tmp_path / "config").mkdir()
        config = {
            "categories": {"Process_Engineering": {}, "_Inbox": {}},
            "settings": {"reject_threshold": 0.3, "confidence_threshold": 0.6, "fallback_category": "_Inbox"},
        }
        (tmp_path / "config" / "categories.json").write_text(json.dumps(config), encoding="utf-8")
        monkeypatch.setattr(triage_inbox, "ROOT", tmp_path)
        monkeypatch.setattr(triage_inbox, "INBOX", tmp_path / "content" / "_Inbox")
        monkeypatch.setattr(triage_inbox, "CONFIG_PATH", tmp_path / "config" / "categories.json")

    def test_dry_run_does_not_touch_files(self, tmp_path, monkeypatch, capsys):
        self._setup_repo(tmp_path, monkeypatch)
        path = make_card(tmp_path, "junk.md", {"title": "404", "confidence": 0.1}, "x")

        monkeypatch.setattr(sys, "argv", ["triage_inbox.py"])
        triage_inbox.main()

        assert path.exists()
        out = capsys.readouterr().out
        assert "dry-run" in out
        assert "1 delete" in out

    def test_apply_deletes_junk(self, tmp_path, monkeypatch, capsys):
        self._setup_repo(tmp_path, monkeypatch)
        path = make_card(tmp_path, "junk.md", {"title": "404", "confidence": 0.1}, "x")

        monkeypatch.setattr(sys, "argv", ["triage_inbox.py", "--apply"])
        triage_inbox.main()

        assert not path.exists()

    def test_apply_reclassifies_into_real_content_tree(self, tmp_path, monkeypatch, capsys):
        self._setup_repo(tmp_path, monkeypatch)
        meta = {"title": "Real content", "confidence": 0.9}
        body = "> ⚠️ **Inbox Note**: unknown category: Process_Engineering\n\n" + ("Real content. " * 40)
        path = make_card(tmp_path, "card.md", meta, body)

        monkeypatch.setattr(sys, "argv", ["triage_inbox.py", "--apply"])
        triage_inbox.main()

        assert not path.exists()
        moved = tmp_path / "content" / "Process_Engineering" / "card.md"
        assert moved.exists()
