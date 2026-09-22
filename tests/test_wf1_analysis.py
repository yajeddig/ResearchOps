"""Tests for the Claude-backed analysis in wf1_ingest.py (WF1 Gemini -> Claude migration)."""
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
    def __init__(self, content, stop_reason="tool_use", model="claude-sonnet-5"):
        self.content = content
        self.stop_reason = stop_reason
        self.model = model
        self.usage = _Usage()


class FakeMessages:
    def __init__(self, response=None, exc=None, capture=None):
        self._response = response
        self._exc = exc
        self._capture = capture

    def create(self, **kwargs):
        if self._capture is not None:
            self._capture.append(kwargs)
        if self._exc:
            raise self._exc
        return self._response


class FakeBeta:
    def __init__(self, messages):
        self.messages = messages


class FakeClient:
    def __init__(self, response=None, exc=None, capture=None):
        self.beta = FakeBeta(FakeMessages(response, exc, capture))


def _tool_use_response(**fields):
    payload = {
        "title": "Hybrid modelling of a CSTR",
        "category": "Process_Engineering",
        "confidence": 0.9,
        "content_body": "Detailed technical write-up.",
        "key_insights": ["insight 1"],
        "references": [],
        "relevance": "Useful for reactor design.",
        "auto_tags": ["reactor", "hybrid-model"],
        "sector_tags": [],
        "type": "Article",
        "source_type": "Article",
        "reason": "Matches Process_Engineering.",
    }
    payload.update(fields)
    return FakeResponse([_Block("tool_use", input=payload)])


class TestBuildClassifyTool:
    def test_category_enum_excludes_inbox(self):
        tool = wf1_ingest.build_classify_tool()
        assert "_Inbox" not in tool["input_schema"]["properties"]["category"]["enum"]

    def test_required_fields_present(self):
        tool = wf1_ingest.build_classify_tool()
        required = tool["input_schema"]["properties"]
        for field in ("title", "category", "confidence", "content_body", "relevance", "auto_tags", "reason"):
            assert field in required


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
    def test_forces_tool_choice_and_returns_routed_result(self, monkeypatch):
        capture = []
        client = FakeClient(response=_tool_use_response(), capture=capture)
        monkeypatch.setattr(wf1_ingest, "get_client", lambda: client)

        result = wf1_ingest.analyze_content("some article text", "web_page")

        assert result["title"] == "Hybrid modelling of a CSTR"
        assert result["category"] == "Process_Engineering"  # confidence 0.9 clears the threshold
        call = capture[0]
        assert call["tool_choice"] == {"type": "tool", "name": "classify_content"}
        assert call["model"] == wf1_ingest.CLAUDE_MODEL
        assert isinstance(call["messages"][0]["content"], str)

    def test_low_confidence_routes_to_inbox(self, monkeypatch):
        client = FakeClient(response=_tool_use_response(confidence=0.1))
        monkeypatch.setattr(wf1_ingest, "get_client", lambda: client)

        result = wf1_ingest.analyze_content("some article text", "web_page")

        assert result["category"] == "_Inbox"
        assert "fallback_reason" in result

    def test_refusal_returns_none(self, monkeypatch):
        client = FakeClient(response=FakeResponse([], stop_reason="refusal"))
        monkeypatch.setattr(wf1_ingest, "get_client", lambda: client)

        assert wf1_ingest.analyze_content("some article text", "web_page") is None

    def test_no_tool_use_block_returns_none(self, monkeypatch):
        client = FakeClient(response=FakeResponse([_Block("text", text="I'd rather not.")]))
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
        client = FakeClient(response=_tool_use_response(), capture=capture)
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
        client = FakeClient(response=_tool_use_response(), capture=capture)
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
        client = FakeClient(response=_tool_use_response(), capture=capture)
        monkeypatch.setattr(wf1_ingest, "get_client", lambda: client)

        result = wf1_ingest.analyze_content(str(docx), "document")

        assert result is None
        assert capture == []
