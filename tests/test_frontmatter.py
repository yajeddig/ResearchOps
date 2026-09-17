"""Tests for YAML frontmatter helpers and content-hash deduplication."""
import tempfile
from pathlib import Path
from unittest.mock import patch

from utils import frontmatter


class TestFrontmatter:
    def test_roundtrip(self):
        meta = {"title": "A \"quoted\" title: with colon", "date": "2026-09-17", "tags": ["a:b", "c"], "confidence": 0.9}
        text = frontmatter.dump(meta, "# Body\n\ncontent")
        parsed, body = frontmatter.parse(text)
        assert parsed["title"] == meta["title"]
        assert parsed["tags"] == ["a:b", "c"]
        assert body.startswith("# Body")

    def test_parses_legacy_card(self):
        legacy = "---\ntitle: \"Legacy\"\ndate: 2025-12-29\ncategory: Data_Science\ntags: ['ds:llm', 'ds:rag']\nhash: 112211\n---\n\n## Content\n"
        meta, body = frontmatter.parse(legacy)
        assert meta["title"] == "Legacy"
        assert meta["tags"] == ["ds:llm", "ds:rag"]
        assert "## Content" in body

    def test_no_frontmatter(self):
        meta, body = frontmatter.parse("# Just markdown")
        assert meta == {} and body == "# Just markdown"

    def test_invalid_yaml_falls_back(self):
        broken = "---\ntitle: \"Unbalanced \" quotes\" here\ntags: ['x']\n---\nbody"
        meta, _ = frontmatter.parse(broken)
        assert meta["tags"] == ["x"]

    def test_load_cards(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "content" / "Data_Science"
            root.mkdir(parents=True)
            (root / "a.md").write_text(frontmatter.dump({"title": "A"}, "body"), encoding="utf-8")
            cards = frontmatter.load_cards(Path(tmp) / "content")
            assert len(cards) == 1
            assert cards[0]["category"] == "Data_Science"
            assert cards[0]["meta"]["title"] == "A"


class TestContentDedup:
    def test_content_hash_detects_same_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            history = Path(tmp) / "history.json"
            with patch("utils.dedup.HISTORY_FILE", history):
                from utils.dedup import add_to_history, is_duplicate
                assert is_duplicate(content=b"%PDF-1.4 same document") is False
                add_to_history(content=b"%PDF-1.4 same document", kind="document", file="x.md")
                assert is_duplicate(content=b"%PDF-1.4 same document") is True
                assert is_duplicate(content=b"%PDF-1.4 other document") is False

    def test_url_and_content_keys_coexist(self):
        with tempfile.TemporaryDirectory() as tmp:
            history = Path(tmp) / "history.json"
            with patch("utils.dedup.HISTORY_FILE", history):
                from utils.dedup import add_to_history, is_duplicate, load_history
                add_to_history(url="https://example.org/p", content="page text", kind="web_page")
                assert is_duplicate(url="https://example.org/p")
                assert is_duplicate(content="page text")
                assert len(load_history()) == 2
