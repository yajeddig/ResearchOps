"""
P1 - Triage content/_Inbox/ without calling an LLM.

_Inbox held 23 cards on 2026-09-21, almost all 404/captcha/test-message
artifacts predating the P0 quality gate. This classifies each card
deterministically (no LLM call, no API cost) and prints a review table.
Dry-run by default; --apply acts on it.

Usage:
    python scripts/triage_inbox.py            # print the table only
    python scripts/triage_inbox.py --apply     # delete/reclassify for real
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import frontmatter  # noqa: E402
from utils.content_guard import is_junk_analysis, validate_scraped  # noqa: E402
from utils.pii_guard import detect_pii  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
INBOX = ROOT / "content" / "_Inbox"
CONFIG_PATH = ROOT / "config" / "categories.json"

_INBOX_NOTE_RE = re.compile(r"⚠️ \*\*Inbox Note\*\*:\s*(.+)")
_UNKNOWN_CATEGORY_RE = re.compile(r"unknown category:\s*(\S+)")


def classify_card(meta: dict, body: str, valid_categories: set[str], reject_threshold: float) -> tuple[str, str, str | None]:
    """
    Decide what to do with one _Inbox card without an LLM call.
    Returns (verdict, reason, proposed_category); verdict is one of
    "delete" / "reclassify" / "keep".
    """
    pii_reasons = detect_pii(f"{meta.get('title', '')}\n{body}")
    if pii_reasons:
        return "delete", f"pii:{','.join(pii_reasons)}", None

    junk, junk_reason = is_junk_analysis(meta, reject_threshold)
    if junk:
        return "delete", junk_reason, None

    scraped_ok, scraped_reason = validate_scraped(body)
    if not scraped_ok:
        return "delete", scraped_reason, None

    note_match = _INBOX_NOTE_RE.search(body)
    if note_match:
        cat_match = _UNKNOWN_CATEGORY_RE.search(note_match.group(1))
        if cat_match and cat_match.group(1) in valid_categories:
            candidate = cat_match.group(1)
            return "reclassify", f"unknown_category_now_valid:{candidate}", candidate

    return "keep", "no_clear_signal - needs a human look", None


def apply_delete(path: Path) -> None:
    path.unlink()


def apply_reclassify(path: Path, meta: dict, body: str, new_category: str, content_root: Path) -> Path:
    """Move the card to its new category dir, drop the inbox tag/note, return the new path."""
    meta = dict(meta)
    meta["category"] = new_category
    tags = meta.get("tags", [])
    if isinstance(tags, list):
        meta["tags"] = [t for t in tags if not str(t).startswith("inbox:")]
    body = _INBOX_NOTE_RE.sub("", body, count=1).lstrip("\n")

    dest_dir = content_root / new_category
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / path.name
    dest.write_text(frontmatter.dump(meta, body), encoding="utf-8")
    path.unlink()
    return dest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Act on the verdicts instead of just printing them.")
    args = parser.parse_args()

    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    valid_categories = set(config["categories"].keys()) - {"_Inbox"}
    reject_threshold = config["settings"]["reject_threshold"]

    rows = []
    for path in sorted(INBOX.glob("*.md")):
        meta, body = frontmatter.parse(path.read_text(encoding="utf-8"))
        verdict, reason, proposed_category = classify_card(meta, body, valid_categories, reject_threshold)
        rows.append((path, verdict, reason, proposed_category))

    name_w = max((len(p.name) for p, *_ in rows), default=6)
    print(f"{'fichier':<{name_w}}  {'verdict':<11}  {'catégorie proposée':<20}  raison")
    for path, verdict, reason, proposed_category in rows:
        print(f"{path.name:<{name_w}}  {verdict:<11}  {(proposed_category or ''):<20}  {reason}")

    counts = {"delete": 0, "reclassify": 0, "keep": 0}
    for _, verdict, _, _ in rows:
        counts[verdict] += 1
    print(f"\n{counts['delete']} delete, {counts['reclassify']} reclassify, {counts['keep']} keep "
          f"(sur {len(rows)} fiches)" + ("" if args.apply else " — dry-run, relancer avec --apply pour agir"))

    if not args.apply:
        return

    for path, verdict, reason, proposed_category in rows:
        if verdict == "delete":
            apply_delete(path)
        elif verdict == "reclassify":
            meta, body = frontmatter.parse(path.read_text(encoding="utf-8"))
            dest = apply_reclassify(path, meta, body, proposed_category, content_root=INBOX.parent)
            print(f"→ {path.name} déplacé vers {dest.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
