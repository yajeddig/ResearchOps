import json
import hashlib
from pathlib import Path
from datetime import datetime

HISTORY_FILE = Path("data/history.json")

def load_history():
    if not HISTORY_FILE.exists():
        return {}
    return json.loads(HISTORY_FILE.read_text())

def save_history(data):
    HISTORY_FILE.parent.mkdir(exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(data, indent=2))

def compute_hash(url):
    return hashlib.md5(url.encode()).hexdigest()[:8]

def is_duplicate(url):
    history = load_history()
    url_hash = compute_hash(url)
    return url_hash in history

def add_to_history(url, hash_id):
    history = load_history()
    url_hash = compute_hash(url)
    history[url_hash] = {
        "url": url,
        "hash": hash_id,
        "added": datetime.now().isoformat()
    }
    save_history(history)
