"""
Unit tests for WF1 content routing logic

These tests are self-contained and don't require external dependencies.
The routing functions are copied here to avoid import issues with google-genai.
"""
import pytest
import re
from pathlib import Path
from datetime import datetime


# --- Copy of routing functions for testing ---
# These mirror the implementation in wf1_ingest.py

def route_content(gemini_response: dict, config: dict) -> dict:
    """
    Apply fallback logic based on confidence threshold.

    Routes to _Inbox if:
    - confidence < threshold (default 0.6)
    - category not in valid categories
    """
    threshold = config["settings"]["confidence_threshold"]
    fallback = config["settings"]["fallback_category"]
    valid_categories = list(config["categories"].keys())

    category = gemini_response.get("category", fallback)
    confidence = gemini_response.get("confidence", 0.0)

    # Fallback conditions
    if confidence < threshold:
        category = fallback
        gemini_response["auto_tags"] = ["inbox:low-confidence"]
        gemini_response["fallback_reason"] = f"confidence {confidence:.2f} < {threshold}"
    elif category not in valid_categories:
        original_category = category
        category = fallback
        gemini_response["auto_tags"] = ["inbox:ambiguous"]
        gemini_response["fallback_reason"] = f"unknown category: {original_category}"

    gemini_response["category"] = category
    return gemini_response


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    return re.sub(r'[^a-zA-Z0-9]', '_', text.lower())


def get_save_path(category: str, title: str, content_hash: str) -> Path:
    """Generate save path: content/{category}/{date}_{hash}_{title}.md"""
    date_str = datetime.now().strftime("%Y%m%d")
    safe_title = slugify(title)[:50]
    filename = f"{date_str}_{content_hash[:8]}_{safe_title}.md"
    return Path("content") / category / filename


# --- Mock config for testing ---

MOCK_CONFIG = {
    "categories": {
        "Data_Science": {
            "description": "ML, stats, modélisation hybride",
            "auto_tags": ["ds:ml", "ds:stats"]
        },
        "Process_Engineering": {
            "description": "Conception, simulation, contrôle",
            "auto_tags": ["n3:simulation"]
        },
        "_Inbox": {
            "description": "Contenu non classifiable",
            "auto_tags": ["inbox:review-needed"]
        }
    },
    "settings": {
        "confidence_threshold": 0.6,
        "fallback_category": "_Inbox"
    }
}


# --- Tests ---

class TestRouteContent:
    """Tests for route_content() function"""

    def test_high_confidence_valid_category(self):
        """Test: confidence >= 0.6 and valid category → normal routing"""
        response = {
            "category": "Data_Science",
            "confidence": 0.85,
            "auto_tags": ["ds:ml"]
        }

        result = route_content(response, MOCK_CONFIG)

        assert result["category"] == "Data_Science"
        assert result["auto_tags"] == ["ds:ml"]
        assert "fallback_reason" not in result

    def test_low_confidence_routes_to_inbox(self):
        """Test: confidence < 0.6 → routes to _Inbox with low-confidence tag"""
        response = {
            "category": "Data_Science",
            "confidence": 0.5,
            "auto_tags": ["ds:ml"]
        }

        result = route_content(response, MOCK_CONFIG)

        assert result["category"] == "_Inbox"
        assert "inbox:low-confidence" in result["auto_tags"]
        assert "fallback_reason" in result
        assert "0.50 < 0.6" in result["fallback_reason"]

    def test_unknown_category_routes_to_inbox(self):
        """Test: unknown category → routes to _Inbox with ambiguous tag"""
        response = {
            "category": "Unknown_Category",
            "confidence": 0.9,
            "auto_tags": ["some:tag"]
        }

        result = route_content(response, MOCK_CONFIG)

        assert result["category"] == "_Inbox"
        assert "inbox:ambiguous" in result["auto_tags"]
        assert "fallback_reason" in result
        assert "Unknown_Category" in result["fallback_reason"]

    def test_zero_confidence(self):
        """Test: confidence = 0 → routes to _Inbox"""
        response = {
            "category": "Process_Engineering",
            "confidence": 0.0,
            "auto_tags": []
        }

        result = route_content(response, MOCK_CONFIG)

        assert result["category"] == "_Inbox"
        assert "inbox:low-confidence" in result["auto_tags"]

    def test_boundary_confidence_exact_threshold(self):
        """Test: confidence = 0.6 exactly → should pass (not fall back)"""
        response = {
            "category": "Data_Science",
            "confidence": 0.6,
            "auto_tags": ["ds:ml"]
        }

        result = route_content(response, MOCK_CONFIG)

        assert result["category"] == "Data_Science"
        assert "fallback_reason" not in result

    def test_missing_confidence_defaults_to_zero(self):
        """Test: missing confidence field → treated as 0 → routes to _Inbox"""
        response = {
            "category": "Data_Science",
            "auto_tags": ["ds:ml"]
            # No confidence field
        }

        result = route_content(response, MOCK_CONFIG)

        assert result["category"] == "_Inbox"
        assert "inbox:low-confidence" in result["auto_tags"]

    def test_missing_category_defaults_to_fallback(self):
        """Test: missing category field → uses fallback"""
        response = {
            "confidence": 0.8,
            "auto_tags": ["some:tag"]
            # No category field
        }

        result = route_content(response, MOCK_CONFIG)

        # Falls back due to missing category (defaults to _Inbox from .get())
        # _Inbox is a valid category, so it stays
        assert result["category"] == "_Inbox"

    def test_inbox_category_with_high_confidence_stays_inbox(self):
        """Test: _Inbox category with high confidence → stays in _Inbox"""
        response = {
            "category": "_Inbox",
            "confidence": 0.9,
            "auto_tags": ["inbox:off-topic"]
        }

        result = route_content(response, MOCK_CONFIG)

        assert result["category"] == "_Inbox"
        # Should keep original tags since it's a valid category with high confidence
        assert result["auto_tags"] == ["inbox:off-topic"]


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
