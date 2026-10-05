"""
P2 - Propose Semantic Scholar seed_paper_ids from existing fiches.

For every card with a DOI or arXiv reference in its source or body, resolves
the Semantic Scholar paperId and suggests which monitoring.json topic it
best matches (keyword overlap with the topic's keywords_academic — no LLM
call, this is meant to be free and instant). Dry-run only: prints a table,
never writes to monitoring.json — add the paperId you want to
seed_paper_ids yourself.

Usage:
    python scripts/seed_from_fiches.py
"""
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import requests

from utils import frontmatter  # noqa: E402
from utils.monitoring_config import load_topics  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
S2_PAPER_API = "https://api.semanticscholar.org/graph/v1/paper"

_DOI_RE = re.compile(r"\b10\.\d{4,9}/[^\s\)\]\}\"'<>]+")
_ARXIV_RE = re.compile(r"arxiv\.org/abs/(\d{4}\.\d{4,5})|arxiv:(\d{4}\.\d{4,5})", re.IGNORECASE)
_WORD_RE = re.compile(r"[a-zA-Zàâäéèêëïîôöùûüç]{4,}")


_DOI_VERSION_RE = re.compile(r"(?<=\d)(/v\d+|v\d+)$")


def find_identifiers(text: str) -> list[tuple[str, str]]:
    """Returns [(kind, id), ...] — kind is 'DOI' or 'arXiv'."""
    # Preprint DOIs (bioRxiv, chemRxiv) carry a version suffix S2 doesn't index.
    found = [("DOI", _DOI_VERSION_RE.sub("", m.group(0).rstrip(".,;)}"))) for m in _DOI_RE.finditer(text)]
    for m in _ARXIV_RE.finditer(text):
        found.append(("arXiv", m.group(1) or m.group(2)))
    return found


def resolve_paper_id(kind: str, identifier: str) -> dict | None:
    delay = 2.0
    for attempt in range(3):
        try:
            r = requests.get(f"{S2_PAPER_API}/{kind}:{identifier}", params={"fields": "paperId,title"}, timeout=15)
        except requests.RequestException:
            return None
        if r.status_code == 429 and attempt < 2:
            time.sleep(delay)
            delay *= 2
            continue
        return r.json() if r.status_code == 200 else None
    return None


def suggest_topic(card_text: str, topics: list[dict]) -> str:
    """Topic whose keywords_academic share the most tokens with the card — no match if there's no overlap at all."""
    card_tokens = set(_WORD_RE.findall(card_text.lower()))
    best_id, best_score = "(aucun sujet proche)", 0
    for topic in topics:
        topic_tokens = {tok for kw in topic["keywords_academic"] for tok in _WORD_RE.findall(kw.lower())}
        score = len(card_tokens & topic_tokens)
        if score > best_score:
            best_id, best_score = topic["id"], score
    return best_id


def main() -> None:
    topics = load_topics(ROOT / "config" / "monitoring.json")
    rows = []
    for card in frontmatter.load_cards("content"):
        text = f"{card['meta'].get('source', '')}\n{card['body']}"
        identifiers = find_identifiers(text)
        if not identifiers:
            continue
        kind, identifier = identifiers[0]  # one seed candidate per card is enough
        resolved = resolve_paper_id(kind, identifier)
        time.sleep(1.1)  # unauthenticated S2 rate limit
        if not resolved or not resolved.get("paperId"):
            rows.append((card["path"], kind, identifier, "(résolution échouée)", "-"))
            continue
        tags = " ".join(map(str, card["meta"].get("tags", []) or []))
        topic_id = suggest_topic(f"{card['meta'].get('title', '')} {tags}", topics)
        rows.append((card["path"], kind, identifier, resolved["paperId"], topic_id))

    if not rows:
        print("Aucune fiche avec DOI ou arXiv trouvée.")
        return

    print(f"{'fichier':<70}  {'type':<6}  {'identifiant':<20}  {'paperId':<42}  sujet proposé")
    for path, kind, identifier, paper_id, topic_id in rows:
        print(f"{path:<70}  {kind:<6}  {identifier:<20}  {paper_id:<42}  {topic_id}")
    print(
        f"\n{len(rows)} candidat(s). Rien n'est écrit : ajoute le(s) paperId retenu(s) "
        "à la main dans seed_paper_ids du sujet choisi, config/monitoring.json."
    )


if __name__ == "__main__":
    main()
