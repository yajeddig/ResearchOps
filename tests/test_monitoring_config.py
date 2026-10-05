"""Tests for utils/monitoring_config.py (monitoring.json v2 loader/validator)."""
import json

import pytest

from utils.monitoring_config import load_topics


def _write(tmp_path, topics):
    path = tmp_path / "monitoring.json"
    path.write_text(json.dumps({"topics": topics}), encoding="utf-8")
    return path


class TestBackwardCompatibility:
    def test_v1_topic_loads_with_v2_defaults(self, tmp_path):
        path = _write(tmp_path, [{
            "id": "n2o-emissions",
            "name": "N2O Emissions",
            "keywords_academic": ["nitrous oxide wastewater treatment"],
            "keywords_news": ["nitrous oxide water treatment technology"],
            "paper_limit": 3,
        }])

        topics = load_topics(path)

        assert len(topics) == 1
        topic = topics[0]
        assert topic["status"] == "active"
        assert topic["priority"] == 3
        assert topic["projects"] == []
        assert topic["exclude_keywords"] == []
        assert topic["seed_paper_ids"] == []
        assert topic["min_year"] is None


class TestFiltering:
    def test_paused_topics_excluded_by_default(self, tmp_path):
        path = _write(tmp_path, [
            {"id": "a", "name": "A", "keywords_academic": ["x"], "status": "active"},
            {"id": "b", "name": "B", "keywords_academic": ["y"], "status": "paused"},
        ])

        topics = load_topics(path)

        assert [t["id"] for t in topics] == ["a"]

    def test_active_only_false_returns_everything(self, tmp_path):
        path = _write(tmp_path, [
            {"id": "a", "name": "A", "keywords_academic": ["x"], "status": "active"},
            {"id": "b", "name": "B", "keywords_academic": ["y"], "status": "paused"},
        ])

        topics = load_topics(path, active_only=False)

        assert {t["id"] for t in topics} == {"a", "b"}

    def test_sorted_by_priority(self, tmp_path):
        path = _write(tmp_path, [
            {"id": "low", "name": "Low", "keywords_academic": ["x"], "priority": 3},
            {"id": "high", "name": "High", "keywords_academic": ["y"], "priority": 1},
        ])

        topics = load_topics(path)

        assert [t["id"] for t in topics] == ["high", "low"]


class TestValidation:
    def test_missing_keywords_academic_raises_clear_error(self, tmp_path):
        path = _write(tmp_path, [{"id": "a", "name": "A"}])
        with pytest.raises(ValueError, match="keywords_academic"):
            load_topics(path)

    def test_duplicate_id_raises(self, tmp_path):
        path = _write(tmp_path, [
            {"id": "a", "name": "A", "keywords_academic": ["x"]},
            {"id": "a", "name": "A bis", "keywords_academic": ["y"]},
        ])
        with pytest.raises(ValueError, match="dupliqué"):
            load_topics(path)

    def test_unknown_field_raises(self, tmp_path):
        path = _write(tmp_path, [{"id": "a", "name": "A", "keywords_academic": ["x"], "typo_field": True}])
        with pytest.raises(ValueError):
            load_topics(path)

    def test_invalid_status_raises(self, tmp_path):
        path = _write(tmp_path, [{"id": "a", "name": "A", "keywords_academic": ["x"], "status": "inactive"}])
        with pytest.raises(ValueError):
            load_topics(path)

    def test_malformed_json_raises_clear_error(self, tmp_path):
        path = tmp_path / "monitoring.json"
        path.write_text("{not json", encoding="utf-8")
        with pytest.raises(ValueError, match="JSON"):
            load_topics(path)

    def test_empty_topics_list_raises(self, tmp_path):
        path = _write(tmp_path, [])
        with pytest.raises(ValueError):
            load_topics(path)
