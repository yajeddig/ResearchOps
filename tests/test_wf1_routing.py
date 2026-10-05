"""
Unit tests for WF1 routing, slug and save-path logic.

route_content is tested against the real module. slugify/get_save_path are
still local copies (legacy of the Gemini era, when importing wf1_ingest
pulled google-genai); they mirror wf1_ingest's implementation.
"""
import os
import re
from datetime import datetime
from pathlib import Path

os.environ.setdefault("ANTHROPIC_API_KEY", "sk-test-fake")

from wf1_ingest import route_content  # noqa: E402


# --- Copy of routing functions for testing ---
# These mirror the implementation in wf1_ingest.py

def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    return re.sub(r'[^a-zA-Z0-9]', '_', text.lower())


def get_save_path(category: str, title: str, content_hash: str) -> Path:
    """Generate save path: content/{category}/{date}_{hash}_{title}.md"""
    date_str = datetime.now().strftime("%Y%m%d")
    safe_title = slugify(title)[:50]
    filename = f"{date_str}_{content_hash[:8]}_{safe_title}.md"
    return Path("content") / category / filename


# --- Tests ---

SETTINGS = {"confidence_threshold": 0.6, "fallback_category": "_Inbox"}
CATEGORIES = {"Hybrid_SciML": "UDE, PINN", "Process_Modeling": "Mechanistic models"}


class TestRouteContent:
    """Against the real wf1_ingest.route_content (not a copy)."""

    def test_high_confidence_valid_category(self):
        result = route_content({"category": "Hybrid_SciML", "confidence": 0.85, "tags": ["pinn"]}, SETTINGS, CATEGORIES)
        assert result["category"] == "Hybrid_SciML"
        assert "fallback_reason" not in result

    def test_low_confidence_routes_to_inbox_and_keeps_tags(self):
        result = route_content({"category": "Hybrid_SciML", "confidence": 0.5, "tags": ["pinn"]}, SETTINGS, CATEGORIES)
        assert result["category"] == "_Inbox"
        assert result["tags"] == ["pinn"]
        assert "0.50 < 0.6" in result["fallback_reason"]

    def test_unknown_category_routes_to_inbox(self):
        result = route_content({"category": "Data_Science", "confidence": 0.9}, SETTINGS, CATEGORIES)
        assert result["category"] == "_Inbox"
        assert "Data_Science" in result["fallback_reason"]

    def test_boundary_confidence_exact_threshold_passes(self):
        result = route_content({"category": "Process_Modeling", "confidence": 0.6}, SETTINGS, CATEGORIES)
        assert result["category"] == "Process_Modeling"

    def test_missing_confidence_defaults_to_zero(self):
        result = route_content({"category": "Process_Modeling"}, SETTINGS, CATEGORIES)
        assert result["category"] == "_Inbox"


class TestSlugify:
    """Tests for slugify() function"""

    def test_basic_slugify(self):
        """Test basic text slugification"""
        assert slugify("Hello World") == "hello_world"
        assert slugify("Test-123") == "test_123"

    def test_special_characters(self):
        """Test slugify handles special characters"""
        assert slugify("ML/AI: Future?") == "ml_ai__future_"
        assert slugify("100% Efficiency") == "100__efficiency"

    def test_unicode_characters(self):
        """Test slugify handles unicode"""
        # Unicode chars become underscores
        result = slugify("Émissions N₂O")
        assert "_" in result
        assert result.islower() or "_" in result


class TestGetSavePath:
    """Tests for get_save_path() function"""

    def test_save_path_format(self):
        """Test save path generation"""
        path = get_save_path("Data_Science", "ML for Process Control", "abc123def")

        assert path.parent.name == "Data_Science"
        assert path.parent.parent.name == "content"
        assert path.suffix == ".md"
        assert "abc123de" in path.name  # First 8 chars of hash

    def test_save_path_truncates_long_titles(self):
        """Test that long titles are truncated"""
        long_title = "This is a very long title that should be truncated to 50 characters maximum for the filename"
        path = get_save_path("_Inbox", long_title, "xyz789abc")

        # Filename format: {date}_{hash}_{title}.md
        filename = path.name
        # Remove .md extension
        name_without_ext = filename[:-3]
        # Split: date_hash_title
        parts = name_without_ext.split("_", 2)

        if len(parts) >= 3:
            title_part = parts[2]
            assert len(title_part) <= 50

    def test_save_path_inbox_category(self):
        """Test save path for _Inbox category"""
        path = get_save_path("_Inbox", "Ambiguous Content", "hash123")

        assert path.parent.name == "_Inbox"
        assert "content/_Inbox" in str(path)
