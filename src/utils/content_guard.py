"""
Quality gate for WF1.

21% of the cards produced before this module were 404 pages, anti-bot
interstitials, empty inputs or test messages that the LLM dutifully turned
into "intelligence cards". Everything here runs BEFORE the LLM call (cheap)
or right after it (to catch what slipped through).
"""
import re
from urllib.parse import parse_qs, unquote, urlparse

MIN_SCRAPED_CHARS = 500      # below this, a web page is considered empty/blocked
MIN_NOTE_CHARS = 20          # below this, a raw text note is noise
HEAD_WINDOW = 1500           # junk markers are looked for in the first N chars

# Lower-cased substrings/regexes found in blocked or missing pages
JUNK_MARKERS = [
    r"\b404\b",
    r"page not found",
    r"page introuvable",
    r"just a moment",
    r"making sure you.re not a bot",
    r"verify(ing)? (that )?you are (a )?human",
    r"security verification",
    r"checking your browser",
    r"enable javascript and cookies",
    r"please enable cookies",
    r"access denied",
    r"attention required",
    r"\bcaptcha\b",
    r"unusual traffic",
    r"ddos",
    r"sign in to linkedin",
    r"join linkedin",
    r"this content isn.t available",
    r"connection reset",
]

# Titles the LLM produces when it had nothing to analyse
JUNK_TITLE_MARKERS = [
    r"not found", r"\b404\b", r"unavailable", r"inaccessible", r"security verification",
    r"unanalyzed", r"empty content", r"placeholder", r"test message", r"error",
    r"not a bot", r"content unavailable",
]

_REDIRECT_WRAPPERS = {
    # host suffix -> query parameter holding the real URL
    "linkedin.com": "url",
    "l.facebook.com": "u",
    "lm.facebook.com": "u",
    "google.com": "q",
    "t.umblr.com": "z",
}


def normalize_url(url: str) -> str:
    """
    Unwrap redirect wrappers (LinkedIn safety links, Facebook l.php, Google
    redirects) and strip trailing punctuation copied from chat messages.
    """
    url = url.strip().rstrip(").,;>\"'")
    try:
        parsed = urlparse(url)
    except ValueError:
        return url
    host = parsed.netloc.lower()
    for suffix, param in _REDIRECT_WRAPPERS.items():
        if host == suffix or host.endswith("." + suffix):
            target = parse_qs(parsed.query).get(param)
            if target and target[0].startswith("http"):
                return normalize_url(unquote(target[0]))
    return url


def validate_scraped(text: str | None, status_code: int | None = None) -> tuple[bool, str | None]:
    """
    Decide whether scraped page content is worth sending to the LLM.
    Returns (ok, reason). `reason` is a short machine-friendly code.
    """
    if status_code is not None and status_code >= 400:
        return False, f"http_{status_code}"
    if not text or not text.strip():
        return False, "empty"
    stripped = text.strip()
    head = stripped[:HEAD_WINDOW].lower()
    for pattern in JUNK_MARKERS:
        if re.search(pattern, head):
            return False, f"blocked_or_missing_page ({pattern})"
    if len(stripped) < MIN_SCRAPED_CHARS:
        return False, f"too_short ({len(stripped)} chars)"
    return True, None


def validate_note(text: str | None) -> tuple[bool, str | None]:
    """A raw text note must carry at least a sentence."""
    if not text or len(text.strip()) < MIN_NOTE_CHARS:
        return False, "empty_note"
    return True, None


def extract_pdf_text(path: str) -> str | None:
    """
    Extract text from a PDF for pre-LLM gating. Returns None on a scanned
    (text-less) or unreadable PDF, or if pypdf itself can't be loaded, so the
    caller falls back to sending it to the LLM directly and gates on the
    post-LLM analysis instead.
    """
    try:
        from pypdf import PdfReader
        from pypdf.errors import PdfReadError
    except Exception:
        return None
    try:
        reader = PdfReader(path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except (PdfReadError, OSError):
        return None
    return text if text.strip() else None


def is_junk_analysis(analysis: dict, reject_threshold: float) -> tuple[bool, str | None]:
    """
    Post-LLM gate: very low confidence, or a title that describes a failure
    rather than content, means the model had nothing real to work with.
    """
    confidence = float(analysis.get("confidence", 0.0) or 0.0)
    title = str(analysis.get("title", "")).lower()
    if confidence <= reject_threshold:
        return True, f"confidence {confidence:.2f} <= {reject_threshold}"
    for pattern in JUNK_TITLE_MARKERS:
        if re.search(pattern, title):
            return True, f"junk title ({pattern})"
    return False, None
