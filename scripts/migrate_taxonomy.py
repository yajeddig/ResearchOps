"""
P3 - Re-classify every existing card into the faceted taxonomy.

Dry-run (default): one Claude call per card, on the card's existing title,
tags and body (no re-scraping), appended to data/taxonomy_migration.csv as
it goes. Re-running skips cards already in the CSV, so an interrupted or
rate-limited run resumes where it stopped. No card is touched.

--apply: replays the CSV with no LLM call, so what gets applied is exactly
what was reviewed (and hand-corrected in the CSV, if needed): git mv into
the new category folder, rewrite the frontmatter (category, confidence,
tags, sectors, projects, legacy_category), body untouched.

Low-confidence rows are flagged, not sent to _Inbox: _Inbox is excluded
from the public site, and these cards were already accepted once. Change
new_category to _Inbox in the CSV for the ones you want triaged.

Usage:
    python scripts/migrate_taxonomy.py [--limit N]
    python scripts/migrate_taxonomy.py --apply
"""
import argparse
import csv
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import frontmatter  # noqa: E402
from utils.taxonomy import INBOX, Taxonomy  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "taxonomy_migration.csv"
FIELDS = ["path", "old_category", "new_category", "confidence", "low_confidence",
          "tags", "sectors", "projects", "new_tag_candidates"]
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")
MAX_BODY_CHARS = 30000  # same cap as WF1's capture prompt


def _join(items) -> str:
    return ";".join(items)


def _split(value: str) -> list[str]:
    return [item.strip() for item in (value or "").split(";") if item.strip()]


# ---------------------------------------------------------------- classify
def build_prompt(card: dict) -> str:
    meta = card["meta"]
    old_tags = meta.get("tags", [])
    old_tags = ", ".join(map(str, old_tags)) if isinstance(old_tags, list) else str(old_tags)
    return (
        "Classify this existing knowledge card into the taxonomy. Facets only — the card's text stays as is.\n\n"
        f"TITLE: {meta.get('title', '')}\n"
        f"FREE-TEXT TAGS FROM THE OLD TAXONOMY (hints, not vocabulary): {old_tags}\n\n"
        f"CARD BODY:\n{card['body'][:MAX_BODY_CHARS]}"
    )


def classify_card(client, taxonomy: Taxonomy, card: dict) -> dict | None:
    """One structured-output call; None (logged) when the answer is unusable."""
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=4000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        # Identical across every card: cached after the first call.
        system=[{"type": "text", "text": taxonomy.system_prompt(), "cache_control": {"type": "ephemeral"}}],
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": taxonomy.output_schema()}},
        messages=[{"role": "user", "content": build_prompt(card)}],
    )
    if response.stop_reason in ("refusal", "max_tokens"):
        print(f"  ! {card['path']}: stop_reason={response.stop_reason}", file=sys.stderr)
        return None
    text = next((b.text for b in response.content if b.type == "text"), None)
    if text is None:
        print(f"  ! {card['path']}: no text block", file=sys.stderr)
        return None
    return taxonomy.validate_facets(json.loads(text))


def to_row(card: dict, facets: dict, taxonomy: Taxonomy) -> dict:
    threshold = taxonomy.settings["confidence_threshold"]
    return {
        "path": card["path"],
        "old_category": card["category"],
        "new_category": facets["category"],
        "confidence": f"{facets['confidence']:.2f}",
        "low_confidence": "yes" if facets["confidence"] < threshold else "",
        "tags": _join(facets["tags"]),
        "sectors": _join(facets["sectors"]),
        "projects": _join(facets.get("projects", [])),
        "new_tag_candidates": _join(facets["new_tag_candidates"]),
    }


def read_rows(csv_path: Path) -> list[dict]:
    if not csv_path.exists():
        return []
    with open(csv_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def dry_run(client, taxonomy: Taxonomy, root: Path, csv_path: Path, limit: int | None) -> list[dict]:
    done = {row["path"] for row in read_rows(csv_path)}
    cards = [c for c in frontmatter.load_cards(root / "content")]
    for card in cards:
        card["path"] = str(Path(card["path"]).relative_to(root)).replace("\\", "/")
    todo = [c for c in cards if c["path"] not in done]
    if limit is not None:
        todo = todo[:limit]
    print(f"{len(cards)} cartes, {len(done)} déjà classées, {len(todo)} à classer ({MODEL})")

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    new_file = not csv_path.exists()
    failed = 0
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        for n, card in enumerate(todo, 1):
            try:
                facets = classify_card(client, taxonomy, card)
            except Exception as exc:  # one bad card must not lose the rest of the run
                print(f"  ! {card['path']}: {exc}", file=sys.stderr)
                facets = None
            if facets is None:
                failed += 1
                continue
            writer.writerow(to_row(card, facets, taxonomy))
            f.flush()
            print(f"  [{n}/{len(todo)}] {card['category']} -> {facets['category']}  {card['path']}")
    if failed:
        print(f"{failed} carte(s) en échec : relancer le script les reprend.")
    return read_rows(csv_path)


def summarize(rows: list[dict]) -> str:
    moves = Counter((r["old_category"], r["new_category"]) for r in rows)
    by_new = Counter(r["new_category"] for r in rows)
    candidates = Counter(c for r in rows for c in _split(r["new_tag_candidates"]))
    low = sum(1 for r in rows if r["low_confidence"])
    lines = [f"## Migration taxonomie — {len(rows)} cartes", "", "| Nouvelle catégorie | Cartes |", "|---|---|"]
    lines += [f"| {cat} | {n} |" for cat, n in by_new.most_common()]
    lines += ["", "| Ancienne → nouvelle | Cartes |", "|---|---|"]
    lines += [f"| {old} → {new} | {n} |" for (old, new), n in moves.most_common()]
    lines += ["", f"Confiance basse (< seuil, à vérifier) : {low}"]
    if candidates:
        lines.append("Tags candidats : " + ", ".join(f"{c} ({n})" for c, n in candidates.most_common(15)))
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- apply
def validate_row(row: dict, taxonomy: Taxonomy, root: Path) -> str | None:
    """Error message for a row that can't be applied as written, else None."""
    src = root / row["path"]
    if not src.exists():
        return f"{row['path']}: fichier introuvable"
    new_category = row["new_category"].strip()
    if new_category not in taxonomy.categories and new_category != INBOX:
        return f"{row['path']}: catégorie inconnue '{new_category}'"
    unknown = [t for t in _split(row["tags"]) if t not in taxonomy.tags]
    if unknown:
        return f"{row['path']}: tags hors vocabulaire {unknown}"
    unknown = [s for s in _split(row["sectors"]) if s not in taxonomy.sectors]
    if unknown:
        return f"{row['path']}: secteurs inconnus {unknown}"
    dest = root / "content" / new_category / src.name
    if dest != src and dest.exists():
        return f"{row['path']}: {dest.relative_to(root)} existe déjà"
    try:
        float(row["confidence"] or 0.0)
    except ValueError:
        return f"{row['path']}: confiance invalide '{row['confidence']}'"
    return None


def apply_row(row: dict, root: Path) -> Path:
    """Move and rewrite one card from an already-validated CSV row."""
    src = root / row["path"]
    new_category = row["new_category"].strip()
    meta, body = frontmatter.parse(src.read_text(encoding="utf-8"))
    meta.setdefault("legacy_category", row["old_category"])
    meta["category"] = new_category
    meta["confidence"] = float(row["confidence"] or 0.0)
    meta["tags"] = _split(row["tags"])
    meta["sectors"] = _split(row["sectors"])
    projects = _split(row["projects"])
    if projects:
        meta["projects"] = projects
    else:
        meta.pop("projects", None)

    dest = root / "content" / new_category / src.name
    if dest != src:
        dest.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "mv", str(src), str(dest)], cwd=root, check=True, capture_output=True)
    dest.write_text(frontmatter.dump(meta, body), encoding="utf-8")
    subprocess.run(["git", "add", str(dest)], cwd=root, check=True, capture_output=True)
    return dest


def apply(taxonomy: Taxonomy, root: Path, csv_path: Path) -> tuple[int, list[str]]:
    """All-or-nothing: every row is validated before a single file is touched."""
    rows = read_rows(csv_path)
    if not rows:
        raise SystemExit(f"{csv_path} absent ou vide : lancer le dry-run d'abord.")
    errors = [err for row in rows if (err := validate_row(row, taxonomy, root))]
    if errors:
        return 0, errors
    for row in rows:
        apply_row(row, root)
    for folder in (root / "content").iterdir():
        if folder.is_dir() and not any(folder.iterdir()):
            folder.rmdir()
    return len(rows), []


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true", help="Apply the reviewed CSV (no LLM call).")
    parser.add_argument("--limit", type=int, default=None, help="Classify at most N cards (dry-run).")
    args = parser.parse_args()
    taxonomy = Taxonomy()

    if args.apply:
        applied, errors = apply(taxonomy, ROOT, CSV_PATH)
        if errors:
            print(f"Rien n'a été appliqué : {len(errors)} ligne(s) invalide(s) dans le CSV.")
            for err in errors:
                print(f"  ! {err}")
            sys.exit(1)
        print(f"{applied} carte(s) migrée(s). Vérifier `git status`, puis committer.")
        return

    from anthropic import Anthropic
    rows = dry_run(Anthropic(), taxonomy, ROOT, CSV_PATH, args.limit)
    summary = summarize(rows)
    print("\n" + summary)
    print(f"Revue : {CSV_PATH.relative_to(ROOT)} — rien n'a été modifié dans content/.")
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(summary)


if __name__ == "__main__":
    main()
