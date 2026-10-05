"""Tests for the Claude-backed analysis in wf1_ingest.py (structured outputs, faceted taxonomy)."""
import json
import os

os.environ.setdefault("ANTHROPIC_API_KEY", "sk-test-fake")

import wf1_ingest  # noqa: E402


class _Block:
    def __init__(self, type_, **kw):
        self.type = type_
        for k, v in kw.items():
            setattr(self, k, v)


class _Usage:
    def __init__(self, input_tokens=100, output_tokens=200):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens


class FakeResponse:
    def __init__(self, content, stop_reason="end_turn", model="claude-sonnet-5-5"):
        self.content = content
        self.stop_reason = stop_reason
        self.model = model
        self.usage = _Usage()


class FakeMessages:
    def __init__(self, response=None, exc=None, capture=None):
        self._response = response
        self._exc = exc
        self._capture = capture

    def stream(self, **kwargs):
        if self._capture is not None:
            self._capture.append(kwargs)
        if self._exc:
            raise self._exc
        return _FakeStream(self._response)


class _FakeStream:
    def __init__(self, response):
        self._response = response

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def get_final_message(self):
        return self._response


class FakeBeta:
    def __init__(self, messages):
        self.messages = messages


class FakeClient:
    def __init__(self, response=None, exc=None, capture=None):
        self.beta = FakeBeta(FakeMessages(response, exc, capture))


def _json_response(**fields):
    payload = {
        "title": "Hybrid modelling of a CSTR",
        "category": "Process_Modeling",
        "confidence": 0.9,
        "content_body": "Detailed technical write-up.",
        "key_insights": ["insight 1"],
        "references": [],
        "relevance": "Useful for reactor design.",
        "tags": ["reactor-cstr", "hybrid-modeling"],
        "sectors": [],
        "new_tag_candidates": [],
        "type": "Article",
        "source_type": "Article",
        "reason": "Matches Process_Modeling.",
    }
    payload.update(fields)
    return FakeResponse([_Block("text", text=json.dumps(payload))])


class TestOutputSchema:
    def test_category_enum_excludes_inbox(self):
        schema = wf1_ingest.TAXONOMY.output_schema(wf1_ingest.CONTENT_PROPERTIES)
        assert "_Inbox" not in schema["properties"]["category"]["enum"]

    def test_every_field_required_and_closed(self):
        schema = wf1_ingest.TAXONOMY.output_schema(wf1_ingest.CONTENT_PROPERTIES)
        assert set(schema["required"]) == set(schema["properties"])
        assert schema["additionalProperties"] is False
        for field in ("title", "content_body", "category", "tags", "sectors", "new_tag_candidates"):
            assert field in schema["properties"]

    def test_tags_constrained_to_vocabulary(self):
        schema = wf1_ingest.TAXONOMY.output_schema(wf1_ingest.CONTENT_PROPERTIES)
        assert schema["properties"]["tags"]["items"]["enum"] == wf1_ingest.TAXONOMY.tags


class TestBuildAnalysisPrompt:
    def test_image_prompt_includes_ocr_instructions(self):
        prompt = wf1_ingest.build_analysis_prompt("[Image content - analyze visually]", "image")
        assert "OCR" in prompt

    def test_text_prompt_has_no_ocr_instructions(self):
        prompt = wf1_ingest.build_analysis_prompt("some article text", "web_page")
        assert "OCR" not in prompt

    def test_prompt_truncates_long_content(self):
        prompt = wf1_ingest.build_analysis_prompt("x" * 50000, "raw_note")
        assert "x" * 30000 in prompt
        assert "x" * 30001 not in prompt


class TestImageMediaType:
    def test_known_extensions(self):
        assert wf1_ingest._image_media_type("photo.jpg") == "image/jpeg"
        assert wf1_ingest._image_media_type("photo.PNG") == "image/png"
        assert wf1_ingest._image_media_type("photo.webp") == "image/webp"

    def test_unknown_extension_defaults_to_jpeg(self):
        assert wf1_ingest._image_media_type("photo.bin") == "image/jpeg"


class TestAnalyzeContentText:
    def test_uses_structured_output_and_returns_routed_result(self, monkeypatch):
        capture = []
        client = FakeClient(response=_json_response(), capture=capture)
        monkeypatch.setattr(wf1_ingest, "get_client", lambda: client)

        result = wf1_ingest.analyze_content("some article text", "web_page")

        assert result["title"] == "Hybrid modelling of a CSTR"
        assert result["category"] == "Process_Modeling"  # confidence 0.9 clears the threshold
        assert result["tags"] == ["reactor-cstr", "hybrid-modeling"]
        call = capture[0]
        assert call["output_config"]["format"]["type"] == "json_schema"
        assert "tool_choice" not in call  # forced tool use is a 400 on Sonnet 5.5
        assert "Controlled vocabulary" in call["system"]
        assert call["model"] == wf1_ingest.CLAUDE_MODEL
        assert call["output_config"]["effort"] == "high"
        assert isinstance(call["messages"][0]["content"], str)

    def test_off_vocabulary_and_excess_tags_dropped(self, monkeypatch):
        tags = ["not-a-real-tag", "reactor-cstr", "pinn", "control-mpc", "lca", "n2o", "transport-kla"]
        client = FakeClient(response=_json_response(tags=tags, new_tag_candidates=["pinn", "Sludge-Age ", "a", "b", "c"]))
        monkeypatch.setattr(wf1_ingest, "get_client", lambda: client)

        result = wf1_ingest.analyze_content("some article text", "web_page")

        assert result["tags"] == ["reactor-cstr", "pinn", "control-mpc", "lca", "n2o"]
        # a candidate already in the vocabulary is not a candidate; max 3
        assert result["new_tag_candidates"] == ["sludge-age", "a", "b"]

    def test_max_tokens_truncation_returns_none(self, monkeypatch):
        client = FakeClient(response=FakeResponse([_Block("text", text='{"title": "trunc')], stop_reason="max_tokens"))
        monkeypatch.setattr(wf1_ingest, "get_client", lambda: client)

        assert wf1_ingest.analyze_content("some article text", "web_page") is None

    def test_low_confidence_routes_to_inbox(self, monkeypatch):
        client = FakeClient(response=_json_response(confidence=0.1))
        monkeypatch.setattr(wf1_ingest, "get_client", lambda: client)

        result = wf1_ingest.analyze_content("some article text", "web_page")

        assert result["category"] == "_Inbox"
        assert "fallback_reason" in result
        assert result["tags"] == ["reactor-cstr", "hybrid-modeling"]  # kept, no inbox marker

    def test_refusal_returns_none(self, monkeypatch):
        client = FakeClient(response=FakeResponse([], stop_reason="refusal"))
        monkeypatch.setattr(wf1_ingest, "get_client", lambda: client)

        assert wf1_ingest.analyze_content("some article text", "web_page") is None

    def test_no_text_block_returns_none(self, monkeypatch):
        client = FakeClient(response=FakeResponse([_Block("thinking", thinking="")]))
        monkeypatch.setattr(wf1_ingest, "get_client", lambda: client)

        assert wf1_ingest.analyze_content("some article text", "web_page") is None

    def test_api_exception_returns_none(self, monkeypatch):
        client = FakeClient(exc=RuntimeError("boom"))
        monkeypatch.setattr(wf1_ingest, "get_client", lambda: client)

        assert wf1_ingest.analyze_content("some article text", "web_page") is None


class TestAnalyzeContentMultimodal:
    def test_image_sends_base64_image_block(self, monkeypatch, tmp_path):
        img = tmp_path / "capture.png"
        img.write_bytes(b"\x89PNG\r\n\x1a\nfake")
        capture = []
        client = FakeClient(response=_json_response(), capture=capture)
        monkeypatch.setattr(wf1_ingest, "get_client", lambda: client)

        result = wf1_ingest.analyze_content(str(img), "image")

        assert result is not None
        blocks = capture[0]["messages"][0]["content"]
        image_block = next(b for b in blocks if b["type"] == "image")
        assert image_block["source"]["media_type"] == "image/png"
        text_block = next(b for b in blocks if b["type"] == "text")
        assert "OCR" in text_block["text"]

    def test_pdf_document_sends_base64_document_block(self, monkeypatch, tmp_path):
        pdf = tmp_path / "paper.pdf"
        pdf.write_bytes(b"%PDF-1.4 fake")
        capture = []
        client = FakeClient(response=_json_response(), capture=capture)
        monkeypatch.setattr(wf1_ingest, "get_client", lambda: client)

        result = wf1_ingest.analyze_content(str(pdf), "document")

        assert result is not None
        blocks = capture[0]["messages"][0]["content"]
        doc_block = next(b for b in blocks if b["type"] == "document")
        assert doc_block["source"]["media_type"] == "application/pdf"

    def test_non_pdf_document_is_rejected_without_api_call(self, monkeypatch, tmp_path):
        docx = tmp_path / "report.docx"
        docx.write_bytes(b"fake docx")
        capture = []
        client = FakeClient(response=_json_response(), capture=capture)
        monkeypatch.setattr(wf1_ingest, "get_client", lambda: client)

        result = wf1_ingest.analyze_content(str(docx), "document")

        assert result is None
        assert capture == []


class TestFinish:
    def test_logs_outcome_and_commits_the_log_file(self, monkeypatch):
        logged = []
        committed = []
        monkeypatch.setattr(wf1_ingest, "set_output", lambda *a: None)
        monkeypatch.setattr(wf1_ingest, "telegram_notify", lambda *a: None)
        monkeypatch.setattr(wf1_ingest, "log_outcome", lambda status, **kw: logged.append({"status": status, **kw}))
        monkeypatch.setattr(wf1_ingest, "safe_commit", lambda files, message: committed.append((files, message)))

        wf1_ingest.finish("rejected", "Rejeté (too_short) : x", "WARNING", reason="too_short")

        assert logged == [{"status": "rejected", "reason": "too_short", "category": None, "new_tag_candidates": None}]
        assert committed == [(["data/ingest_log.jsonl"], "WF1 log: rejected")]

    def test_log_push_failure_does_not_raise(self, monkeypatch):
        monkeypatch.setattr(wf1_ingest, "set_output", lambda *a: None)
        monkeypatch.setattr(wf1_ingest, "telegram_notify", lambda *a: None)
        monkeypatch.setattr(wf1_ingest, "log_outcome", lambda *a, **kw: None)

        def push_fails(files, message):
            raise RuntimeError("Git push failed after 3 attempts")
        monkeypatch.setattr(wf1_ingest, "safe_commit", push_fails)

        wf1_ingest.finish("rejected", "Rejeté", "WARNING", reason="too_short")  # must not raise

    def test_saved_outcome_carries_category(self, monkeypatch):
        logged = []
        monkeypatch.setattr(wf1_ingest, "set_output", lambda *a: None)
        monkeypatch.setattr(wf1_ingest, "telegram_notify", lambda *a: None)
        monkeypatch.setattr(wf1_ingest, "log_outcome", lambda status, **kw: logged.append({"status": status, **kw}))
        monkeypatch.setattr(wf1_ingest, "safe_commit", lambda files, message: None)

        wf1_ingest.finish("saved", "Fiche créée", "SUCCESS", category="Process_Engineering")

        assert logged == [{"status": "saved", "reason": None, "category": "Process_Engineering", "new_tag_candidates": None}]
