"""
WF1 - Omni-channel ingest.

Turns a GitHub issue (created by the Make/Telegram bridge or by hand) into a
classified Markdown knowledge card under content/<Category>/.

Pipeline:
  route input -> quality gate -> dedup -> Gemini analysis -> post-LLM gate
  -> write card -> commit -> notify (Telegram + workflow outputs)
"""
import json
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path

import requests

from utils import frontmatter
from utils.content_guard import (
    is_junk_analysis,
    normalize_url,
    validate_note,
    validate_scraped,
)
from utils.dedup import add_to_history, content_hash, is_duplicate
from utils.git_ops import safe_commit
from utils.logger import get_logger
from utils.notify import set_output, telegram_notify

log = get_logger("WF1")

# --- CONFIGURATION ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ISSUE_TITLE = os.getenv("ISSUE_TITLE", "")
ISSUE_BODY = os.getenv("ISSUE_BODY", "")
ISSUE_NUMBER = os.getenv("ISSUE_NUMBER", "")

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GENERATION_CONFIG = {
    "temperature": 0.3,
    "max_output_tokens": 16384,
    "response_mime_type": "application/json",
}

CONFIG_PATH = Path(__file__).parent.parent / "config" / "categories.json"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CATEGORIES_CONFIG = json.load(f)

CATEGORIES = list(CATEGORIES_CONFIG["categories"].keys())
SECTOR_TAGS = CATEGORIES_CONFIG["sector_tags"]
SETTINGS = CATEGORIES_CONFIG["settings"]

_client = None


def get_client():
    """Lazy Gemini client so the module can be imported without credentials."""
    global _client
    if _client is None:
        from google import genai
        _client = genai.Client(api_key=GOOGLE_API_KEY)
    return _client


def slugify(text: str) -> str:
    """Convert text to a filename-safe slug."""
    return re.sub(r"[^a-zA-Z0-9]", "_", text.lower())


def get_categories_list() -> str:
    """Format categories with descriptions for the prompt (without _Inbox)."""
    return "\n".join(
        f"- {name}: {data['description']}"
        for name, data in CATEGORIES_CONFIG["categories"].items()
        if name != "_Inbox"
    )


def route_content(gemini_response: dict, config: dict) -> dict:
    """
    Apply the confidence fallback:
    - confidence < threshold  -> _Inbox (manual triage)
    - unknown category        -> _Inbox
    """
    threshold = config["settings"]["confidence_threshold"]
    fallback = config["settings"]["fallback_category"]
    valid_categories = list(config["categories"].keys())

    category = gemini_response.get("category", fallback)
    confidence = gemini_response.get("confidence", 0.0)

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


def build_classification_prompt(content: str, input_type: str) -> str:
    """Build the classification prompt for Gemini."""
    categories_list = get_categories_list()
    sector_tags_list = ", ".join(SECTOR_TAGS)

    extraction_instructions = ""
    if input_type == "image":
        extraction_instructions = """
IMPORTANT - IMAGE CONTENT EXTRACTION:
1. First, extract ALL visible text from the image (OCR): headlines, body text,
   numbers, author names, sources, dates, quotes.
2. Preserve the original language of the text.
3. Base your summary on the ACTUAL extracted content, not on a description of the image.
4. If the image contains no readable technical content, set confidence to 0.1 and
   title to "Unreadable image".
"""

    return f"""
Analyze and classify this content for a process engineering / industrial data science knowledge base.

INPUT TYPE: {input_type}
{extraction_instructions}

CATEGORIES (pick exactly one):
{categories_list}

SECTOR TAGS (pick 0-3 if applicable):
{sector_tags_list}

Respond ONLY with valid JSON:
{{
  "title": "Precise technical title based on actual content",
  "category": "<category_name>",
  "confidence": <0.0-1.0>,

  "content_body": "DETAILED transcription of the content. Include:
    - Full explanation of concepts, methods, architecture
    - Code blocks with syntax highlighting (```python, ```sql, etc.)
    - Mathematical equations in LaTeX format ($E=mc^2$ or $$\\int_0^1 f(x)dx$$)
    - Chemical formulas (H₂SO₄) and reaction equations
    - ASCII diagrams or mermaid diagrams for processes/architectures
    - Tables for structured data
    - Step-by-step procedures if applicable
    Preserve technical depth. Do NOT over-summarize.",

  "key_insights": ["insight1", "insight2", "insight3"],

  "references": [
    {{"type": "source", "citation": "Author, Title, Year, URL"}},
    {{"type": "cited", "citation": "Referenced work mentioned in content"}}
  ],

  "equations": ["LaTeX equation if applicable"],
  "code_snippets": [{{"language": "python", "code": "...", "description": "..."}}],

  "relevance": "Why is this useful (ROI, Industrial Application, Learning opportunity)",
  "auto_tags": ["<tag1>", "<tag2>", "<tag3>"],
  "sector_tags": ["<sector1>"],
  "type": "Screenshot" if image else "Article",
  "source_type": "<LinkedIn Post | Article | Paper | Tutorial | Infographic | Chart | Other>",
  "reason": "<1 sentence justification for category choice>"
}}

If the content is an error page, a login wall, a bot check or otherwise carries no
technical content, respond with confidence 0.1 and an explicit title such as
"Blocked page: <reason>". Do not invent content.

If content doesn't fit any category well, use "_Inbox" with low confidence.

CONTENT:
{content[:30000]}
"""


def analyze_content(content_or_path, input_type: str = "text") -> dict | None:
    """Analyze content with Gemini and return the structured classification."""
    log.info(f"Gemini analysis ({input_type}, {MODEL_NAME})")
    client = get_client()
    try:
        if input_type == "image":
            from PIL import Image
            img = Image.open(content_or_path)
            prompt = build_classification_prompt("[Image content - analyze visually]", input_type)
            response = client.models.generate_content(model=MODEL_NAME, contents=[prompt, img], config=GENERATION_CONFIG)
        elif input_type == "document":
            uploaded_file = client.files.upload(file=content_or_path)
            prompt = build_classification_prompt("[Document content - analyze text]", input_type)
            response = client.models.generate_content(model=MODEL_NAME, contents=[prompt, uploaded_file], config=GENERATION_CONFIG)
        else:
            prompt = build_classification_prompt(content_or_path, input_type)
            response = client.models.generate_content(model=MODEL_NAME, contents=prompt, config=GENERATION_CONFIG)

        result = json.loads(response.text)
        return route_content(result, CATEGORIES_CONFIG)
    except Exception as exc:
        log.exception(f"Gemini error: {exc}")
        return None


def build_card(analysis: dict, source_ref: str, hash_id: str) -> str:
    """Render the Markdown knowledge card (YAML frontmatter + sections)."""
    all_tags = list(analysis.get("auto_tags", [])) + list(analysis.get("sector_tags", []))
    meta = {
        "title": str(analysis["title"]),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "category": analysis["category"],
        "confidence": round(float(analysis.get("confidence", 0.0) or 0.0), 2),
        "tags": all_tags,
        "source": source_ref,
        "type": analysis.get("type", "Article"),
        "source_type": analysis.get("source_type", "Unknown"),
        "hash": hash_id,
    }

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


def finish(status: str, message: str, level: str = "INFO") -> None:
    """Single exit point: workflow outputs + Telegram."""
    set_output("status", status)
    set_output("message", message)
    telegram_notify(message, level)
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
        finish("rejected", f"Rejeté : fichier Telegram introuvable ({ISSUE_TITLE})", "WARNING")
        return

    # --- QUALITY GATE + DEDUP (before any LLM spend) ---
    if input_type == "web_page":
        url = payload
        if is_duplicate(url=url):
            finish("duplicate", f"Doublon ignoré : {url}", "WARNING")
            return
        text, status = scrape_url(url)
        ok, reason = validate_scraped(text, status)
        if not ok:
            finish("rejected", f"Rejeté ({reason}) : {url}", "WARNING")
            return
        payload, raw = text, text.encode("utf-8")
    elif input_type == "raw_note":
        ok, reason = validate_note(payload)
        if not ok:
            finish("rejected", f"Rejeté ({reason}) : note vide", "WARNING")
            return

    if raw is not None and is_duplicate(content=raw):
        finish("duplicate", f"Doublon ignoré (contenu déjà ingéré) : {ISSUE_TITLE[:80]}", "WARNING")
        return

    hash_id = content_hash(raw) if raw is not None else datetime.now().strftime("%H%M%S")

    # --- ANALYSIS ---
    analysis = analyze_content(payload, input_type)
    if not analysis:
        finish("failed", f"Échec de l'analyse Gemini : {ISSUE_TITLE[:80]}", "ERROR")
        return

    junk, reason = is_junk_analysis(analysis, SETTINGS.get("reject_threshold", 0.3))
    if junk:
        finish("rejected", f"Rejeté après analyse ({reason}) : {analysis.get('title', ISSUE_TITLE)[:80]}", "WARNING")
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
    )

    if input_type in ["image", "document"] and isinstance(payload, str) and os.path.exists(payload):
        os.remove(payload)


if __name__ == "__main__":
    main()
