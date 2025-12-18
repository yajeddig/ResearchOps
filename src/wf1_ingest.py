import os
import json
import requests
import re
import tempfile
import mimetypes
from datetime import datetime
import google.generativeai as genai
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

genai.configure(api_key=GOOGLE_API_KEY)
generation_config = {
    "temperature": 0.3,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config
)

CATEGORIES = json.load(open("config/categories.json"))["categories"]

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
    ext = os.path.splitext(file_path)[1] # Gets .jpg, .pdf, etc.
    
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
    print(f"�� Scraping Jina: {url}")
    try:
        return requests.get(f"https://r.jina.ai/{url}", timeout=20).text
    except:
        return None

def analyze_content(content_or_path, input_type="text"):
    print(f"🧠 Gemini Analysis ({input_type})...")
    
    base_prompt = f"""
    EXPERT ANALYSIS ({input_type}).
    Extract technical value for a PhD Engineer (Process Eng / Data Science).
    
    STRICT JSON OUTPUT:
    {{
        "title": "Precise technical title",
        "category": "One from {CATEGORIES}",
        "summary": "Structured summary in 3-4 markdown bullets (Context, Innovation, Feasibility)",
        "relevance": "Why is this useful (ROI, Industrial Application)",
        "tags": ["tag1", "tag2"],
        "type": "Paper" if "{input_type}" == "document" else "Article"
    }}
    """
    
    try:
        if input_type == "image":
            # Vision Processing (JPG/PNG)
            img = Image.open(content_or_path)
            response = model.generate_content([base_prompt, img])
            
        elif input_type == "document":
            # Document Processing (PDF uploaded to Gemini)
            uploaded_file = genai.upload_file(content_or_path)
            response = model.generate_content([base_prompt, uploaded_file])
            # Gemini handles TTL
            
        else:
            # Text / Web Processing
            response = model.generate_content(f"{base_prompt}\nCONTENT:\n{content_or_path[:30000]}")
            
        return json.loads(response.text)
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return None

def main():
    print(f"🚀 Processing Issue #{ISSUE_NUMBER}: {ISSUE_TITLE}")
    
    data_payload = None
    input_type = "text"
    source_ref = ISSUE_TITLE

    # --- 1. ROUTING ---
    
    # CASE A: IMAGE (IMG_ID) - Adapted for Make.com format "IMAGE_URL: ..." or "IMG_ID: ..."
    # Note: The user mentioned IMG_ID in the prompt, but previous spec used IMAGE_URL. 
    # I will support both logic or rely on the user's prompt logic which uses IMG_ID.
    # Let's stick to the user's provided code structure which uses IMG_ID/DOC_ID logic 
    # BUT we need to be careful if Make.com sends "IMAGE_URL".
    # Let's assume the user updated Make.com to send IMG_ID based on their prompt.
    
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
        # Find URL in title or body
        text_to_search = ISSUE_TITLE + " " + ISSUE_BODY
        match = re.search(r'https?://\S+', text_to_search)
        if match:
            url = match.group(0)
            data_payload = clean_jina_content(url)
            input_type = "web_page"
            source_ref = url
        else:
             # Fallback
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
        hash_id = datetime.now().strftime('%H%M%S') # Simple hash for filename
        
        md = f"""---
title: "{analysis['title']}"
date: {datetime.now().strftime("%Y-%m-%d")}
category: {analysis['category']}
tags: {analysis['tags']}
source: "{source_ref}"
type: {analysis['type']}
hash: {hash_id}
---

### 🎯 Relevance
{analysis['relevance']}

### 📝 Summary
{analysis['summary']}
"""
        # --- 4. SAVE ---
        safe_title = re.sub(r'[^a-zA-Z0-9]', '_', analysis['title'][:30])
        filename = f"content/{analysis['category']}/{datetime.now().strftime('%Y%m%d')}_{hash_id}_{safe_title}.md"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, "w", encoding="utf-8") as f: 
            f.write(md)
        
        print(f"✅ Saved: {filename}")
        
        # Safe commit
        safe_commit(
            files=[filename],
            message=f"WF1: {analysis['type']} - {analysis['title'][:50]}"
        )

        # Update history (if URL)
        if input_type == "web_page":
            add_to_history(source_ref, hash_id)

        # Notify
        telegram_notify(
            f"✅ Processed: {analysis['title']}\nCategory: {analysis['category']}",
            "SUCCESS"
        )
        
        # Cleanup temp files
        if input_type in ["image", "document"] and isinstance(data_payload, str):
            if os.path.exists(data_payload):
                os.remove(data_payload)

if __name__ == "__main__":
    main()
