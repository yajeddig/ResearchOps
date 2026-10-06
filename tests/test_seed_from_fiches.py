"""Tests for scripts/seed_from_fiches.py (P2: seed proposal, dry-run only)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import seed_from_fiches  # noqa: E402

TOPICS = [
    {"id": "n2o-emissions", "keywords_academic": ["nitrous oxide wastewater treatment"]},
    {"id": "hybrid-sciml-bioprocess", "keywords_academic": ["hybrid modeling bioprocess machine learning"]},
]


class TestFindIdentifiers:
    def test_finds_doi(self):
        text = "Source: https://doi.org/10.1016/j.watres.2024.121000 great paper"
        assert ("DOI", "10.1016/j.watres.2024.121000") in seed_from_fiches.find_identifiers(text)

    def test_finds_arxiv_url(self):
        text = "See https://arxiv.org/abs/2511.08992 for details"
        assert ("arXiv", "2511.08992") in seed_from_fiches.find_identifiers(text)

    def test_finds_arxiv_bare_id(self):
        text = "Reference: arXiv:2401.12345"
        assert ("arXiv", "2401.12345") in seed_from_fiches.find_identifiers(text)

    def test_no_identifier_returns_empty(self):
        assert seed_from_fiches.find_identifiers("Just a regular article with no DOI.") == []

    def test_trailing_punctuation_stripped_from_doi(self):
        text = "(see https://doi.org/10.1016/j.watres.2024.121000)."
        kinds = seed_from_fiches.find_identifiers(text)
        assert ("DOI", "10.1016/j.watres.2024.121000") in kinds

    def test_preprint_version_suffix_stripped(self):
        ids = seed_from_fiches.find_identifiers("doi 10.1101/2025.07.08.663743v1 and 10.26434/chemrxiv.10001495/v1")
        assert ("DOI", "10.1101/2025.07.08.663743") in ids
        assert ("DOI", "10.26434/chemrxiv.10001495") in ids

    def test_bibtex_brace_stripped_from_doi(self):
        text = "doi = {10.21105/joss.08158}"
        assert ("DOI", "10.21105/joss.08158") in seed_from_fiches.find_identifiers(text)


class TestSuggestTopic:
    def test_matches_best_overlapping_topic(self):
        text = "Hybrid modeling of bioprocess systems using machine learning"
        assert seed_from_fiches.suggest_topic(text, TOPICS) == "hybrid-sciml-bioprocess"

    def test_no_overlap_returns_placeholder(self):
        text = "Completely unrelated subject about something else entirely"
        assert seed_from_fiches.suggest_topic(text, TOPICS) == "(aucun sujet proche)"


class TestResolvePaperId:
    def test_returns_none_on_non_200(self, monkeypatch):
        class FakeResponse:
            status_code = 404
        monkeypatch.setattr(seed_from_fiches.requests, "get", lambda *a, **kw: FakeResponse())
        assert seed_from_fiches.resolve_paper_id("DOI", "10.1/x") is None

    def test_returns_json_on_200(self, monkeypatch):
        class FakeResponse:
            status_code = 200
            def json(self):
                return {"paperId": "abc123", "title": "Some Paper"}
        monkeypatch.setattr(seed_from_fiches.requests, "get", lambda *a, **kw: FakeResponse())
        assert seed_from_fiches.resolve_paper_id("DOI", "10.1/x") == {"paperId": "abc123", "title": "Some Paper"}

    def test_retries_on_rate_limit(self, monkeypatch):
        class R:
            def __init__(self, code):
                self.status_code = code
            def json(self):
                return {"paperId": "abc123"}
        responses = iter([R(429), R(200)])
        monkeypatch.setattr(seed_from_fiches.requests, "get", lambda *a, **kw: next(responses))
        monkeypatch.setattr(seed_from_fiches.time, "sleep", lambda s: None)
        assert seed_from_fiches.resolve_paper_id("arXiv", "2310.10688") == {"paperId": "abc123"}

    def test_returns_none_on_network_error(self, monkeypatch):
        def boom(*a, **kw):
            raise seed_from_fiches.requests.RequestException("down")
        monkeypatch.setattr(seed_from_fiches.requests, "get", boom)
        assert seed_from_fiches.resolve_paper_id("DOI", "10.1/x") is None
