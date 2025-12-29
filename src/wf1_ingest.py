import os
import json
import requests
import re
import tempfile
from pathlib import Path
from datetime import datetime
from google import genai
from PIL import Image
from utils.dedup import is_duplicate, add_to_history
from utils.git_ops import safe_commit
from utils.notify import telegram_notify

# --- CONFIGURATION ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ISSUE_TITLE = os.getenv("ISSUE_TITLE", "")
ISSUE_BODY = os.getenv("ISSUE_BODY", "")
ISSUE_NUMBER = os.getenv("ISSUE_NUMBER", "")

client = genai.Client(api_key=GOOGLE_API_KEY)
generation_config = {
    "temperature": 0.3,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}
MODEL_NAME = "gemini-2.5-flash"

# Load categories configuration
CONFIG_PATH = Path(__file__).parent.parent / "config" / "categories.json"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CATEGORIES_CONFIG = json.load(f)

CATEGORIES = list(CATEGORIES_CONFIG["categories"].keys())
SECTOR_TAGS = CATEGORIES_CONFIG["sector_tags"]
SETTINGS = CATEGORIES_CONFIG["settings"]


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    return re.sub(r'[^a-zA-Z0-9]', '_', text.lower())


def get_categories_list() -> str:
    """Format categories with descriptions for prompt."""
    lines = []
    for name, data in CATEGORIES_CONFIG["categories"].items():
        if name != "_Inbox":  # Don't show _Inbox in prompt
            lines.append(f"- {name}: {data['description']}")
    return "\n".join(lines)


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


def get_save_path(category: str, title: str, content_hash: str) -> Path:
    """Generate save path: content/{category}/{date}_{hash}_{title}.md"""
    date_str = datetime.now().strftime("%Y%m%d")
    safe_title = slugify(title)[:50]
    filename = f"{date_str}_{content_hash[:8]}_{safe_title}.md"
    return Path("content") / category / filename


def download_telegram_file(file_id):
    """Downloads a file (Image or Doc) from Telegram"""
    print(f"📥 Downloading ID: {file_id}")

    # 1. Get Path
    url_info = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={file_id}"
    try:
        r = requests.get(url_info, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"❌ Telegram Info Error: {e}")
        return None

    file_path = r.json()['result']['file_path']
    ext = os.path.splitext(file_path)[1]

    # 2. Download Content
    url_content = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
    try:
        content_data = requests.get(url_content, timeout=30).content
    except Exception as e:
        print(f"❌ Telegram Download Error: {e}")
        return None

    # 3. Save Temp
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    tmp.write(content_data)
    tmp.close()
    return tmp.name


def clean_jina_content(url):
    """Scrape URL content via Jina Reader."""
    print(f"🌐 Scraping Jina: {url}")
    try:
        return requests.get(f"https://r.jina.ai/{url}", timeout=20).text
    except Exception:
        return None


def build_classification_prompt(content: str, input_type: str) -> str:
    """Build the classification prompt for Gemini."""
    categories_list = get_categories_list()
    sector_tags_list = ", ".join(SECTOR_TAGS)

    return f"""
Classify this content for a process engineering / industrial data science knowledge base.

INPUT TYPE: {input_type}

CATEGORIES (pick exactly one):
{categories_list}

SECTOR TAGS (pick 0-3 if applicable):
{sector_tags_list}

Respond ONLY with valid JSON:
{{
  "title": "Precise technical title",
  "category": "<category_name>",
  "confidence": <0.0-1.0>,
  "summary": "Structured summary in 3-4 markdown bullets (Context, Innovation, Feasibility)",
  "relevance": "Why is this useful (ROI, Industrial Application)",
  "auto_tags": ["<tag1>", "<tag2>"],
  "sector_tags": ["<sector1>"],
  "type": "Paper" if document else "Article",
  "reason": "<1 sentence justification for category choice>"
}}

If content doesn't fit any category well, use "_Inbox" with low confidence.

CONTENT:
{content[:30000]}
"""


def analyze_content(content_or_path, input_type="text"):
    """Analyze content using Gemini and return structured classification."""
    print(f"🧠 Gemini Analysis ({input_type})...")

    try:
        if input_type == "image":
            # Vision Processing (JPG/PNG)
            img = Image.open(content_or_path)
            prompt = build_classification_prompt("[Image content - analyze visually]", input_type)
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[prompt, img],
                config=generation_config
            )

        elif input_type == "document":
            # Document Processing (PDF uploaded to Gemini)
            uploaded_file = client.files.upload(file=content_or_path)
            prompt = build_classification_prompt("[Document content - analyze text]", input_type)
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[prompt, uploaded_file],
                config=generation_config
            )

        else:
            # Text / Web Processing
            prompt = build_classification_prompt(content_or_path, input_type)
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=generation_config
            )

        # Parse response
        result = json.loads(response.text)

        # Apply routing logic with fallback
        result = route_content(result, CATEGORIES_CONFIG)

        return result

    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return None


def main():
    print(f"🚀 Processing Issue #{ISSUE_NUMBER}: {ISSUE_TITLE}")

    data_payload = None
    input_type = "text"
    source_ref = ISSUE_TITLE

    # --- 1. ROUTING ---

    # CASE A: IMAGE (IMG_ID)
    if "IMG_ID:" in ISSUE_BODY:
        file_id = ISSUE_BODY.split("IMG_ID:")[1].split()[0].strip()
        local_path = download_telegram_file(file_id)
        if local_path:
            data_payload = local_path
            input_type = "image"
            source_ref = "Telegram Image"

    # CASE B: DOCUMENT (DOC_ID)
    elif "DOC_ID:" in ISSUE_BODY:
        file_id = ISSUE_BODY.split("DOC_ID:")[1].split()[0].strip()
        local_path = download_telegram_file(file_id)
        if local_path:
            data_payload = local_path
            input_type = "document"
            source_ref = "Telegram Document"

    # CASE C: WEB URL
    elif "http" in ISSUE_TITLE or "http" in ISSUE_BODY:
        text_to_search = ISSUE_TITLE + " " + ISSUE_BODY
        match = re.search(r'https?://\S+', text_to_search)
        if match:
            url = match.group(0)
            data_payload = clean_jina_content(url)
            input_type = "web_page"
            source_ref = url
        else:
            data_payload = f"{ISSUE_TITLE}\n{ISSUE_BODY}"
            input_type = "raw_note"

    # CASE D: TEXT NOTE
    else:
        data_payload = f"{ISSUE_TITLE}\n{ISSUE_BODY}"
        input_type = "raw_note"

    if not data_payload:
        print("❌ Empty or invalid input")
        return

    # Deduplication (only for URLs)
    if input_type == "web_page" and is_duplicate(source_ref):
        print(f"⚠️ Duplicate detected: {source_ref}")
        telegram_notify(f"Duplicate skipped: {ISSUE_TITLE}", "WARNING")
        return

    # --- 2. ANALYSIS ---
    analysis = analyze_content(data_payload, input_type)

    if analysis:
        # --- 3. MARKDOWN GENERATION ---
        hash_id = datetime.now().strftime('%H%M%S')

        # Build tags list
        all_tags = analysis.get('auto_tags', []) + analysis.get('sector_tags', [])

        # Check if routed to inbox
        fallback_note = ""
        if analysis['category'] == "_Inbox":
            fallback_reason = analysis.get('fallback_reason', 'manual triage needed')
            fallback_note = f"\n> ⚠️ **Inbox Note**: {fallback_reason}\n"

        md = f"""---
title: "{analysis['title']}"
date: {datetime.now().strftime("%Y-%m-%d")}
category: {analysis['category']}
confidence: {analysis.get('confidence', 0.0):.2f}
tags: {all_tags}
source: "{source_ref}"
type: {analysis.get('type', 'Article')}
hash: {hash_id}
---
{fallback_note}
### 🎯 Relevance
{analysis.get('relevance', 'N/A')}

### 📝 Summary
{analysis.get('summary', 'N/A')}

### 🏷️ Classification Reason
{analysis.get('reason', 'N/A')}
"""
        # --- 4. SAVE ---
        filepath = get_save_path(analysis['category'], analysis['title'], hash_id)
        os.makedirs(filepath.parent, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md)

        print(f"✅ Saved: {filepath}")

        # Log confidence and category
        confidence = analysis.get('confidence', 0.0)
        print(f"📊 Category: {analysis['category']} (confidence: {confidence:.2f})")

        # Safe commit
        safe_commit(
            files=[str(filepath)],
            message=f"WF1: {analysis.get('type', 'Article')} - {analysis['title'][:50]}"
        )

        # Update history (if URL)
        if input_type == "web_page":
            add_to_history(source_ref, hash_id)

        # Notify
        inbox_note = " [→ _Inbox]" if analysis['category'] == "_Inbox" else ""
        telegram_notify(
            f"✅ Processed: {analysis['title']}\nCategory: {analysis['category']}{inbox_note}\nConfidence: {confidence:.0%}",
            "SUCCESS" if analysis['category'] != "_Inbox" else "WARNING"
        )

        # Cleanup temp files
        if input_type in ["image", "document"] and isinstance(data_payload, str):
            if os.path.exists(data_payload):
                os.remove(data_payload)


if __name__ == "__main__":
    main()
