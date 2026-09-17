"""Tests for the WF1 quality gate."""
from utils.content_guard import (
    is_junk_analysis,
    normalize_url,
    validate_note,
    validate_scraped,
)


class TestNormalizeUrl:
    def test_unwraps_linkedin_safety_redirect(self):
        wrapped = "https://www.linkedin.com/safety/go/?url=https%3A%2F%2Farxiv.org%2Fabs%2F2511.08992&trk=flagship"
        assert normalize_url(wrapped) == "https://arxiv.org/abs/2511.08992"

    def test_unwraps_google_redirect(self):
        assert normalize_url("https://www.google.com/url?q=https://example.org/a&sa=D") == "https://example.org/a"

    def test_strips_trailing_punctuation(self):
        assert normalize_url("https://example.org/paper).") == "https://example.org/paper"

    def test_plain_url_untouched(self):
        assert normalize_url("https://pubs.acs.org/doi/10.1021/x") == "https://pubs.acs.org/doi/10.1021/x"


class TestValidateScraped:
    def test_rejects_http_error(self):
        ok, reason = validate_scraped("whatever", status_code=404)
        assert not ok and reason == "http_404"

    def test_rejects_empty(self):
        assert validate_scraped("", 200)[0] is False
        assert validate_scraped(None, 200)[0] is False

    def test_rejects_404_page(self):
        text = "Title: 404 - Page Not Found\n\nURL Source: https://x\n\n" + "lorem " * 200
        ok, reason = validate_scraped(text, 200)
        assert not ok and "blocked_or_missing_page" in reason

    def test_rejects_anti_bot_interstitial(self):
        text = "Title: Making sure you're not a bot!\n\n" + "content " * 200
        assert validate_scraped(text, 200)[0] is False

    def test_rejects_short_content(self):
        ok, reason = validate_scraped("Title: Real article\n\nA few words only.", 200)
        assert not ok and reason.startswith("too_short")

    def test_accepts_real_content(self):
        text = "Title: Physics-informed neural ODE for microbial kinetics\n\n" + ("Monod kinetics and mass balance. " * 40)
        assert validate_scraped(text, 200) == (True, None)


class TestValidateNote:
    def test_rejects_empty_note(self):
        assert validate_note("   ")[0] is False
        assert validate_note("Ingest:")[0] is False

    def test_accepts_sentence(self):
        assert validate_note("Idée : tester un observateur de Luenberger sur le kLa.")[0] is True


class TestIsJunkAnalysis:
    def test_low_confidence_is_junk(self):
        junk, reason = is_junk_analysis({"title": "Some article", "confidence": 0.1}, 0.3)
        assert junk and "confidence" in reason

    def test_junk_title_is_junk(self):
        junk, reason = is_junk_analysis({"title": "LinkedIn Page Not Found Error (404)", "confidence": 0.95}, 0.3)
        assert junk and "junk title" in reason

    def test_inbox_range_is_kept(self):
        """0.3 <= confidence < 0.6 goes to _Inbox for manual triage, not rejected"""
        assert is_junk_analysis({"title": "Ambiguous but real content", "confidence": 0.45}, 0.3) == (False, None)

    def test_good_analysis_kept(self):
        assert is_junk_analysis({"title": "Hybrid modelling of a CSTR", "confidence": 0.9}, 0.3) == (False, None)
