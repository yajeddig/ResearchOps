"""Tests for utils/taxonomy.py (P3 faceted taxonomy)."""
import json

import pytest

from utils.taxonomy import INBOX, MAX_TAG_CANDIDATES, MAX_TAGS, Taxonomy


@pytest.fixture
def config_dir(tmp_path):
    (tmp_path / "categories.json").write_text(json.dumps({
        "categories": {
            "Process_Modeling": {"description": "Mechanistic models"},
            "Hybrid_SciML": {"description": "UDE, PINN"},
            INBOX: {"description": "triage"},
        },
        "sector_tags": ["sector:wwtp", "sector:biogas"],
        "settings": {"confidence_threshold": 0.6, "reject_threshold": 0.3, "fallback_category": INBOX},
    }))
    (tmp_path / "tags.json").write_text(json.dumps({"tags": ["pinn", "ude", "n2o", "lca", "asm", "adm", "kla"]}))
    return tmp_path


class TestRealConfig:
    def test_six_categories_plus_inbox(self):
        taxonomy = Taxonomy()
        assert set(taxonomy.categories) == {
            "Process_Modeling", "Hybrid_SciML", "ML_Industrial_Data",
            "Data_Systems_ITOT", "Digital_Twin_Ops", "Business_Market",
        }

    def test_required_tags_present(self):
        tags = Taxonomy().tags
        for tag in ("n2o", "carbon", "lca", "energy-efficiency"):
            assert tag in tags

    def test_vocabulary_has_no_duplicates_or_status_markers(self):
        tags = Taxonomy().tags
        assert len(tags) == len(set(tags))
        assert not any(t.startswith("inbox:") or ":" in t for t in tags)


class TestSchema:
    def test_projects_facet_absent_without_local_file(self, config_dir):
        schema = Taxonomy(config_dir).output_schema()
        assert "projects" not in schema["properties"]

    def test_projects_facet_enabled_by_local_file(self, config_dir):
        (config_dir / "projects.local.json").write_text(json.dumps({"projects": [{"id": "projet-a", "description": "x"}]}))
        taxonomy = Taxonomy(config_dir)
        schema = taxonomy.output_schema()
        assert schema["properties"]["projects"]["items"]["enum"] == ["projet-a"]
        assert "projet-a" in taxonomy.system_prompt()

    def test_extra_properties_merged_and_all_required(self, config_dir):
        schema = Taxonomy(config_dir).output_schema({"title": {"type": "string"}})
        assert "title" in schema["properties"]
        assert set(schema["required"]) == set(schema["properties"])

    def test_no_constraints_structured_outputs_rejects(self, config_dir):
        """minItems/maxItems/minimum/maximum aren't supported by structured outputs."""
        dumped = json.dumps(Taxonomy(config_dir).output_schema())
        for keyword in ("minItems", "maxItems", '"minimum"', '"maximum"'):
            assert keyword not in dumped

    def test_system_prompt_lists_vocabulary(self, config_dir):
        prompt = Taxonomy(config_dir).system_prompt()
        assert "Controlled vocabulary: pinn, ude" in prompt
        assert INBOX not in prompt


class TestValidateFacets:
    def test_clamps_confidence(self, config_dir):
        taxonomy = Taxonomy(config_dir)
        assert taxonomy.validate_facets({"confidence": 1.7})["confidence"] == 1.0
        assert taxonomy.validate_facets({"confidence": -2})["confidence"] == 0.0
        assert taxonomy.validate_facets({"confidence": "oops"})["confidence"] == 0.0

    def test_tags_filtered_deduped_capped(self, config_dir):
        result = Taxonomy(config_dir).validate_facets(
            {"tags": ["pinn", "pinn", "nope", "ude", "n2o", "lca", "asm", "adm"]}
        )
        assert result["tags"] == ["pinn", "ude", "n2o", "lca", "asm"]
        assert len(result["tags"]) == MAX_TAGS

    def test_candidates_normalized_and_capped(self, config_dir):
        result = Taxonomy(config_dir).validate_facets(
            {"new_tag_candidates": [" Sludge-Age ", "pinn", "", "a", "b", "c"]}
        )
        assert result["new_tag_candidates"] == ["sludge-age", "a", "b"]
        assert len(result["new_tag_candidates"]) == MAX_TAG_CANDIDATES

    def test_unknown_sectors_and_projects_dropped(self, config_dir):
        result = Taxonomy(config_dir).validate_facets({"sectors": ["sector:wwtp", "sector:mars"], "projects": ["ghost"]})
        assert result["sectors"] == ["sector:wwtp"]
        assert result["projects"] == []
