"""
WF1 - Omni-channel ingest.

Turns a GitHub issue (created by the Make/Telegram bridge or by hand) into a
classified Markdown knowledge card under content/<Category>/.

Pipeline:
  route input -> quality gate -> dedup -> Claude analysis -> post-LLM gate
  -> write card -> commit -> notify (Telegram + workflow outputs)
"""
import base64
import json
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path

import requests
from anthropic import Anthropic

from utils import frontmatter
from utils.content_guard import (
    extract_pdf_text,
    is_junk_analysis,
    normalize_url,
    validate_note,
    validate_scraped,
)
from utils.dedup import add_to_history, content_hash, is_duplicate
from utils.git_ops import safe_commit
from utils.ingest_log import log_outcome
from utils.logger import get_logger
from utils.notify import set_output, telegram_notify
from utils.pii_guard import detect_pii
from utils.taxonomy import Taxonomy

log = get_logger("WF1")

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ISSUE_TITLE = os.getenv("ISSUE_TITLE", "")
ISSUE_BODY = os.getenv("ISSUE_BODY", "")
ISSUE_NUMBER = os.getenv("ISSUE_NUMBER", "")

# Sonnet, not Opus: WF1 runs on every capture (potentially several a day),
# WF2/WF4 run monthly / on-demand and keep Opus for that lower volume.
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")
# Streamed, so the cap can leave room for adaptive thinking on top of a long card.
MAX_TOKENS = 64000
EFFORT = "high"  # the model's default, pinned: card quality is the point of WF1

TAXONOMY = Taxonomy()
SETTINGS = TAXONOMY.settings

CONTENT_PROPERTIES = {
    "title": {"type": "string", "description": "Precise technical title based on actual content"},
    "content_body": {
        "type": "string",
        "description": (
            "Detailed technical write-up in Markdown: full explanation of the concepts, methods and "
            "architecture; code blocks with syntax highlighting (```python, ```sql, ...); mathematical "
            "equations in LaTeX ($E=mc^2$ or $$\\int_0^1 f(x)dx$$); chemical formulas and reaction "
            "equations; ASCII or mermaid diagrams for processes/architectures; tables for structured data; "
            "step-by-step procedures where applicable. Preserve technical depth — do not over-summarize."
        ),
    },
    "key_insights": {"type": "array", "items": {"type": "string"}},
    "references": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": ["source", "cited"]},
                "citation": {"type": "string"},
            },
            "required": ["type", "citation"],
            "additionalProperties": False,
        },
    },
    "relevance": {"type": "string", "description": "Why this is useful (ROI, industrial application, learning opportunity)"},
    "type": {"type": "string", "enum": ["Article", "Screenshot"]},
    "source_type": {
        "type": "string",
        "enum": ["LinkedIn Post", "Article", "Paper", "Tutorial", "Infographic", "Chart", "Other"],
    },
    "reason": {"type": "string", "description": "One sentence justifying the category choice"},
}

_client = None


def get_client() -> Anthropic:
    """Lazy Anthropic client so the module can be imported without credentials."""
    global _client
    if _client is None:
        _client = Anthropic()
    return _client


def slugify(text: str) -> str:
    """Convert text to a filename-safe slug."""
    return re.sub(r"[^a-zA-Z0-9]", "_", text.lower())


def route_content(analysis: dict, settings: dict, categories: dict) -> dict:
    """
    Confidence fallback: below the threshold, or a category outside the
    taxonomy, the card goes to _Inbox for manual triage. Tags are kept.
    """
    threshold = settings["confidence_threshold"]
    fallback = settings["fallback_category"]
    confidence = analysis.get("confidence", 0.0)
    if confidence < threshold:
        analysis["fallback_reason"] = f"confidence {confidence:.2f} < {threshold}"
        analysis["category"] = fallback
    elif analysis.get("category") not in categories:
        analysis["fallback_reason"] = f"unknown category: {analysis.get('category')}"
        analysis["category"] = fallback
    return analysis


def get_save_path(category: str, title: str, content_hash_id: str) -> Path:
    """content/{category}/{date}_{hash}_{title}.md"""
    date_str = datetime.now().strftime("%Y%m%d")
    safe_title = slugify(title)[:50]
    filename = f"{date_str}_{content_hash_id[:8]}_{safe_title}.md"
    return Path("content") / category / filename


def download_telegram_file(file_id: str) -> str | None:
    """Download a Telegram file (image or document) to a temp path."""
    log.info(f"Downloading Telegram file {file_id[:12]}…")
    try:
        r = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile", params={"file_id": file_id}, timeout=10)
        r.raise_for_status()
        file_path = r.json()["result"]["file_path"]
        content = requests.get(f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}", timeout=60)
        content.raise_for_status()
    except Exception as exc:
        log.error(f"Telegram download error: {exc}")
        return None
    ext = os.path.splitext(file_path)[1]
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    tmp.write(content.content)
    tmp.close()
    return tmp.name


def scrape_url(url: str) -> tuple[str | None, int | None]:
    """Fetch readable page text through Jina Reader. Returns (text, status_code)."""
    log.info(f"Scraping {url}")
    try:
        r = requests.get(f"https://r.jina.ai/{url}", timeout=30, headers={"Accept": "text/plain"})
        return r.text, r.status_code
    except Exception as exc:
        log.warning(f"Scrape failed: {exc}")
        return None, None


def build_analysis_prompt(content: str, input_type: str) -> str:
    """Per-capture instructions; the taxonomy itself lives in the system prompt."""
    extraction_instructions = ""
    if input_type == "image":
        extraction_instructions = """
IMPORTANT - IMAGE CONTENT EXTRACTION:
1. First, extract ALL visible text from the image (OCR): headlines, body text,
   numbers, author names, sources, dates, quotes.
2. Preserve the original language of the text.
3. Base your analysis on the ACTUAL extracted content, not on a description of the image.
4. If the image contains no readable technical content, set confidence to 0.1 and
   title to "Unreadable image".
"""

    return f"""
Analyze and classify this content, then write a detailed knowledge card from it.

INPUT TYPE: {input_type}
{extraction_instructions}
If the content is an error page, a login wall, a bot check or otherwise carries no
technical content, set confidence to 0.1 and an explicit title such as
"Blocked page: <reason>". Do not invent content.

If content doesn't fit any category well, still pick your best category — low
confidence routes it to _Inbox automatically, you don't need to do that yourself.

CONTENT:
{content[:30000]}
"""


def _image_media_type(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    return {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
            ".gif": "image/gif", ".webp": "image/webp"}.get(ext, "image/jpeg")


def analyze_content(content_or_path, input_type: str = "text") -> dict | None:
    """Analyze content with Claude and return the structured classification."""
    log.info(f"Claude analysis ({input_type}, {CLAUDE_MODEL})")
    client = get_client()
    try:
        if input_type == "image":
            data = base64.standard_b64encode(Path(content_or_path).read_bytes()).decode()
            prompt = build_analysis_prompt("[Image content - analyze visually]", input_type)
            content_blocks = [
                {"type": "image", "source": {"type": "base64", "media_type": _image_media_type(content_or_path), "data": data}},
                {"type": "text", "text": prompt},
            ]
        elif input_type == "document":
            if not str(content_or_path).lower().endswith(".pdf"):
                log.error(f"Unsupported document type for Claude analysis: {content_or_path}")
                return None
            data = base64.standard_b64encode(Path(content_or_path).read_bytes()).decode()
            prompt = build_analysis_prompt("[PDF document - analyze content]", input_type)
            content_blocks = [
                {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": data}},
                {"type": "text", "text": prompt},
            ]
        else:
            content_blocks = build_analysis_prompt(content_or_path, input_type)

        with client.beta.messages.stream(
            model=CLAUDE_MODEL,
            max_tokens=MAX_TOKENS,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            system=TAXONOMY.system_prompt(),
            output_config={
                "effort": EFFORT,
                "format": {"type": "json_schema", "schema": TAXONOMY.output_schema(CONTENT_PROPERTIES)},
            },
            messages=[{"role": "user", "content": content_blocks}],
        ) as stream:
            response = stream.get_final_message()
        if response.stop_reason == "refusal":
            log.warning(f"Claude refused the request: {getattr(response, 'stop_details', None)}")
            return None
        if response.stop_reason == "max_tokens":
            log.error(f"Claude output truncated at max_tokens={MAX_TOKENS}")
            return None
        text = next((b.text for b in response.content if b.type == "text"), None)
        if text is None:
            log.error("Claude response carried no text block")
            return None
        log.info(f"Claude usage: in={response.usage.input_tokens} out={response.usage.output_tokens} model={response.model}")
        result = TAXONOMY.validate_facets(json.loads(text))
        return route_content(result, SETTINGS, TAXONOMY.categories)
    except Exception as exc:
        log.exception(f"Claude error: {exc}")
        return None


def build_card(analysis: dict, source_ref: str, hash_id: str) -> str:
    """Render the Markdown knowledge card (YAML frontmatter + sections)."""
    meta = {
        "title": str(analysis["title"]),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "category": analysis["category"],
        "confidence": round(float(analysis.get("confidence", 0.0) or 0.0), 2),
        "tags": list(analysis.get("tags", [])),
        "sectors": list(analysis.get("sectors", [])),
        "source": source_ref,
        "type": analysis.get("type", "Article"),
        "source_type": analysis.get("source_type", "Unknown"),
        "hash": hash_id,
    }
    if analysis.get("projects"):
        meta["projects"] = list(analysis["projects"])

    fallback_note = ""
    if analysis["category"] == "_Inbox":
        fallback_note = f"\n> ⚠️ **Inbox Note**: {analysis.get('fallback_reason', 'manual triage needed')}\n"

    insights = "\n".join(f"- {i}" for i in analysis.get("key_insights", []))
    references = "\n".join(
        f"- {r.get('citation', '')} " + ("*(source)*" if r.get("type") == "source" else "*(cited)*")
        for r in analysis.get("references", [])
        if isinstance(r, dict)
    )

    body = f"""{fallback_note}
## 🎯 Relevance
{analysis.get('relevance', 'N/A')}

## 📖 Content
{analysis.get('content_body', 'N/A')}

## 💡 Key Insights
{insights}

## 📚 References
{references}

## 🏷️ Classification
{analysis.get('reason', 'N/A')}
"""
    return frontmatter.dump(meta, body)


def finish(
    status: str,
    message: str,
    level: str = "INFO",
    reason: str | None = None,
    category: str | None = None,
    new_tag_candidates: list[str] | None = None,
) -> None:
    """Single exit point: workflow outputs + Telegram + ingest log (committed on every outcome)."""
    set_output("status", status)
    set_output("message", message)
    telegram_notify(message, level)
    try:
        log_outcome(status, reason=reason, category=category, new_tag_candidates=new_tag_candidates)
        safe_commit(files=["data/ingest_log.jsonl"], message=f"WF1 log: {status}")
    except Exception as exc:  # telemetry must never fail the ingestion itself
        log.warning(f"Ingest log not recorded: {exc}")
    log.info(f"[{status}] {message}")


def resolve_input() -> tuple[object, str, str, bytes | None]:
    """
    Route the issue to an input type.
    Returns (payload, input_type, source_ref, raw_bytes_for_hash).
    """
    # Make historically put the file id in the title for photos and only in a
    # bold "File ID" line for documents: look in both title and body.
    issue_text = f"{ISSUE_TITLE}\n{ISSUE_BODY}"

    if "IMG_ID:" in issue_text:
        file_id = issue_text.split("IMG_ID:")[1].split()[0].strip()
        local_path = download_telegram_file(file_id)
        if not local_path:
            return None, "image", "Telegram Image", None
        return local_path, "image", "Telegram Image", Path(local_path).read_bytes()

    if "DOC_ID:" in issue_text or "**File ID** :" in issue_text:
        marker = "DOC_ID:" if "DOC_ID:" in issue_text else "**File ID** :"
        file_id = issue_text.split(marker)[1].split()[0].strip().strip("`")
        local_path = download_telegram_file(file_id)
        if not local_path:
            return None, "document", "Telegram Document", None
        raw = Path(local_path).read_bytes()
        ext = os.path.splitext(local_path)[1].lower()
        if ext in [".md", ".txt", ".csv", ".json"]:
            return raw.decode("utf-8", errors="ignore"), "text", f"Telegram Document ({ext})", raw
        return local_path, "document", "Telegram Document", raw

    text_to_search = f"{ISSUE_TITLE} {ISSUE_BODY}"
    match = re.search(r"https?://\S+", text_to_search)
    if match:
        url = normalize_url(match.group(0))
        return url, "web_page", url, None

    note = f"{ISSUE_TITLE}\n{ISSUE_BODY}".strip()
    return note, "raw_note", ISSUE_TITLE, note.encode("utf-8")


def main() -> None:
    log.info(f"Processing issue #{ISSUE_NUMBER}: {ISSUE_TITLE}")

    payload, input_type, source_ref, raw = resolve_input()
    if payload is None:
        finish("rejected", f"Rejeté : fichier Telegram introuvable ({ISSUE_TITLE})", "WARNING", reason="telegram_file_not_found")
        return

    # --- QUALITY GATE + DEDUP (before any LLM spend) ---
    if input_type == "web_page":
        url = payload
        if is_duplicate(url=url):
            finish("duplicate", f"Doublon ignoré : {url}", "WARNING", reason="duplicate_url")
            return
        text, status = scrape_url(url)
        ok, reason = validate_scraped(text, status)
        if not ok:
            finish("rejected", f"Rejeté ({reason}) : {url}", "WARNING", reason=reason)
            return
        payload, raw = text, text.encode("utf-8")
    elif input_type in ("raw_note", "text"):
        ok, reason = validate_note(payload)
        if not ok:
            finish("rejected", f"Rejeté ({reason}) : note vide", "WARNING", reason=reason)
            return
    elif input_type == "document" and isinstance(payload, str) and payload.lower().endswith(".pdf"):
        pdf_text = extract_pdf_text(payload)
        if pdf_text is not None:
            ok, reason = validate_scraped(pdf_text)
            if not ok:
                finish("rejected", f"Rejeté ({reason}) : document PDF", "WARNING", reason=reason)
                return
            pii_reasons = detect_pii(pdf_text)
            if pii_reasons:
                finish("rejected_pii", "Contenu rejeté : données personnelles détectées.", "WARNING", reason=",".join(pii_reasons))
                return
        # else: scanned/unreadable PDF, no extractable text — fall through to
        # Claude and rely on the post-LLM PII/quality gate below.

    if input_type in ("web_page", "raw_note", "text"):
        pii_reasons = detect_pii(payload)
        if pii_reasons:
            finish("rejected_pii", "Contenu rejeté : données personnelles détectées.", "WARNING", reason=",".join(pii_reasons))
            return

    if raw is not None and is_duplicate(content=raw):
        finish("duplicate", f"Doublon ignoré (contenu déjà ingéré) : {ISSUE_TITLE[:80]}", "WARNING", reason="duplicate_content")
        return

    hash_id = content_hash(raw) if raw is not None else datetime.now().strftime("%H%M%S")

    # --- ANALYSIS ---
    analysis = analyze_content(payload, input_type)
    if not analysis:
        finish("failed", f"Échec de l'analyse : {ISSUE_TITLE[:80]}", "ERROR", reason="analysis_failed")
        return

    # PII on the LLM output itself: catches what OCR/transcription surfaced
    # from an image or a scanned PDF that slipped past the pre-LLM gates.
    analysis_text = " ".join([
        str(analysis.get("title", "")),
        str(analysis.get("content_body", "")),
        " ".join(str(i) for i in analysis.get("key_insights", []) or []),
    ])
    pii_reasons = detect_pii(analysis_text)
    if pii_reasons:
        finish("rejected_pii", "Contenu rejeté après analyse : données personnelles détectées.", "WARNING", reason=",".join(pii_reasons))
        return

    junk, reason = is_junk_analysis(analysis, SETTINGS.get("reject_threshold", 0.3))
    if junk:
        finish("rejected", f"Rejeté après analyse ({reason}) : {analysis.get('title', ISSUE_TITLE)[:80]}", "WARNING", reason=reason)
        return

    # --- WRITE + COMMIT ---
    filepath = get_save_path(analysis["category"], analysis["title"], hash_id)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(build_card(analysis, source_ref, hash_id), encoding="utf-8")
    log.info(f"Saved {filepath}")

    add_to_history(
        url=source_ref if input_type == "web_page" else None,
        content=raw,
        file=str(filepath),
        kind=input_type,
    )

    safe_commit(
        files=[str(filepath), "data/history.json"],
        message=f"WF1: {analysis.get('type', 'Article')} - {analysis['title'][:50]}",
    )

    confidence = float(analysis.get("confidence", 0.0) or 0.0)
    inbox_note = " [→ _Inbox]" if analysis["category"] == "_Inbox" else ""
    finish(
        "saved",
        f"Fiche créée : {analysis['title']}\nCatégorie : {analysis['category']}{inbox_note}\nConfiance : {confidence:.0%}\nFichier : {filepath}",
        "SUCCESS" if analysis["category"] != "_Inbox" else "WARNING",
        category=analysis["category"],
        new_tag_candidates=analysis.get("new_tag_candidates") or None,
    )

    if input_type in ["image", "document"] and isinstance(payload, str) and os.path.exists(payload):
        os.remove(payload)


if __name__ == "__main__":
    main()
