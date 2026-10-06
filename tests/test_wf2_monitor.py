"""Tests for wf2_monitor.py (P2: Recommendations API, filters, health section)."""
import os

os.environ.setdefault("ANTHROPIC_API_KEY", "sk-test-fake")

import wf2_monitor  # noqa: E402


def _raw_paper(**kw):
    paper = {
        "paperId": "p1",
        "title": "Hybrid modelling of a CSTR",
        "authors": [{"name": "A. Researcher"}],
        "year": 2026,
        "publicationDate": "2026-01-15",
        "url": "https://example.org/paper",
        "abstract": "A study on reactor modelling.",
        "citationCount": 5,
        "venue": "Journal of Process Engineering",
    }
    paper.update(kw)
    return paper


class TestNormalizePaper:
    def test_builds_doi_link_when_no_url(self):
        raw = _raw_paper(url=None, externalIds={"DOI": "10.1234/x"})
        paper = wf2_monitor._normalize_paper(raw, "my-topic")
        assert paper["link"] == "https://doi.org/10.1234/x"
        assert paper["topic"] == "my-topic"

    def test_returns_none_without_paper_id(self):
        raw = _raw_paper(paperId=None)
        assert wf2_monitor._normalize_paper(raw, "my-topic") is None

    def test_returns_none_without_any_link(self):
        raw = _raw_paper(url=None, externalIds={})
        assert wf2_monitor._normalize_paper(raw, "my-topic") is None


class TestPassesFilters:
    def test_rejects_below_min_year(self):
        paper = wf2_monitor._normalize_paper(_raw_paper(year=2020), "t")
        assert wf2_monitor._passes_filters(paper, {"min_year": 2023}) is False

    def test_accepts_at_min_year(self):
        paper = wf2_monitor._normalize_paper(_raw_paper(year=2023), "t")
        assert wf2_monitor._passes_filters(paper, {"min_year": 2023}) is True

    def test_rejects_excluded_keyword_in_title(self):
        paper = wf2_monitor._normalize_paper(_raw_paper(title="Medical imaging with deep learning"), "t")
        assert wf2_monitor._passes_filters(paper, {"exclude_keywords": ["medical imaging"]}) is False

    def test_accepts_when_no_filters_set(self):
        paper = wf2_monitor._normalize_paper(_raw_paper(), "t")
        assert wf2_monitor._passes_filters(paper, {}) is True


class TestSearchSemanticScholar:
    def test_uses_recommendations_when_seeded(self, monkeypatch):
        monkeypatch.setattr(wf2_monitor, "get_recommendations", lambda topic: [wf2_monitor._normalize_paper(_raw_paper(), "t")])
        monkeypatch.setattr(wf2_monitor, "search_by_keywords", lambda *a: (_ for _ in ()).throw(AssertionError("should not be called")))

        papers = wf2_monitor.search_semantic_scholar(
            {"name": "t", "seed_paper_ids": ["seed1"], "paper_limit": 3}, None, None, {}
        )
        assert len(papers) == 1

    def test_falls_back_to_keywords_when_no_seeds(self, monkeypatch):
        monkeypatch.setattr(wf2_monitor, "search_by_keywords", lambda *a: [wf2_monitor._normalize_paper(_raw_paper(), "t")])
        monkeypatch.setattr(wf2_monitor, "get_recommendations", lambda topic: (_ for _ in ()).throw(AssertionError("should not be called")))

        papers = wf2_monitor.search_semantic_scholar(
            {"name": "t", "seed_paper_ids": [], "paper_limit": 3}, None, None, {}
        )
        assert len(papers) == 1

    def test_excludes_already_seen_papers(self, monkeypatch):
        monkeypatch.setattr(wf2_monitor, "search_by_keywords", lambda *a: [wf2_monitor._normalize_paper(_raw_paper(), "t")])

        papers = wf2_monitor.search_semantic_scholar(
            {"name": "t", "seed_paper_ids": [], "paper_limit": 3}, None, None, {"p1": "2026-01-01"}
        )
        assert papers == []

    def test_respects_paper_limit(self, monkeypatch):
        many = [wf2_monitor._normalize_paper(_raw_paper(paperId=f"p{i}", citationCount=i), "t") for i in range(5)]
        monkeypatch.setattr(wf2_monitor, "search_by_keywords", lambda *a: many)

        papers = wf2_monitor.search_semantic_scholar({"name": "t", "seed_paper_ids": [], "paper_limit": 2}, None, None, {})
        assert len(papers) == 2

    def test_search_failure_returns_empty_list(self, monkeypatch):
        def boom(*a):
            raise RuntimeError("network down")
        monkeypatch.setattr(wf2_monitor, "search_by_keywords", boom)

        papers = wf2_monitor.search_semantic_scholar({"name": "t", "seed_paper_ids": [], "paper_limit": 3}, None, None, {})
        assert papers == []


class TestRenderHealthSection:
    def test_counts_statuses_and_reasons(self):
        entries = [
            {"status": "saved", "category": "Process_Engineering"},
            {"status": "saved", "category": "_Inbox"},
            {"status": "rejected", "reason": "too_short"},
            {"status": "rejected_pii", "reason": "nir"},
            {"status": "duplicate"},
        ]
        section = wf2_monitor.render_health_section(entries, {"Process_Engineering": [1]}, [])

        assert "Ingestions traitées** : 5" in section
        assert "too_short (1)" in section
        assert "nir (1)" in section
        assert "50%" in section  # 1/2 saved went to _Inbox

    def test_empty_period_has_no_crash(self):
        section = wf2_monitor.render_health_section([], {}, [])
        assert "n/a" in section

    def test_papers_per_topic_counted(self):
        papers = [{"topic": "n2o-emissions"}, {"topic": "n2o-emissions"}, {"topic": "process-digital-twin"}]
        section = wf2_monitor.render_health_section([], {}, papers)
        assert "n2o-emissions (2)" in section
        assert "process-digital-twin (1)" in section


class TestHealthTagCandidates:
    def test_tag_candidates_aggregated(self):
        entries = [
            {"status": "saved", "category": "Hybrid_SciML", "new_tag_candidates": ["latent-sde", "koopman"]},
            {"status": "saved", "category": "Hybrid_SciML", "new_tag_candidates": ["latent-sde"]},
            {"status": "rejected", "reason": "too_short"},
        ]
        section = wf2_monitor.render_health_section(entries, {}, [])
        assert "latent-sde (2)" in section
        assert "koopman (1)" in section

    def test_no_candidates_line_when_none(self):
        section = wf2_monitor.render_health_section([{"status": "saved", "category": "Hybrid_SciML"}], {}, [])
        assert "Tags candidats" not in section
