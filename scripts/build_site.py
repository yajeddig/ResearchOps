"""
Assemble site_src/ for MkDocs from content/ (cards), reports/ and research/.

- Copies the markdown as-is (frontmatter is consumed by Material's tags plugin).
- Generates index.md (counts, latest cards) and tags.md ([TAGS] marker).
- Repairs frontmatter that is not valid YAML so `mkdocs build --strict` passes.
"""
import shutil
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from utils import frontmatter  # noqa: E402

SRC_DIRS = {"content": "Fiches", "reports": "Rapports mensuels", "research": "Recherches"}
OUT = ROOT / "site_src"


def copy_markdown(src: Path, dst: Path) -> list[dict]:
    cards = []
    for path in sorted(src.glob("**/*.md")):
        rel = path.relative_to(src)
        if "_Inbox" in rel.parts:
            # Unclassified / low-confidence triage content: never publish to the public site.
            continue
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        text = path.read_text(encoding="utf-8")
        meta, body = frontmatter.parse(text)
        if meta:
            meta = _clean_meta(meta)
            text = frontmatter.dump(meta, body)
        target.write_text(text, encoding="utf-8")
        cards.append({"path": f"{src.name}/{rel.as_posix()}", "meta": meta, "category": path.parent.name})
    return cards


def _clean_meta(meta: dict) -> dict:
    """Material expects `tags` to be a list of strings and `title` to be a string."""
    tags = meta.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.strip("[]").split(",") if t.strip()]
    meta["tags"] = [str(t) for t in tags if str(t).strip()]
    if "title" in meta:
        meta["title"] = str(meta["title"])
    return meta


def write_category_indexes(cards: list[dict]) -> None:
    """One landing page per category so /content/<Category>/ resolves."""
    by_category: dict[str, list[dict]] = {}
    for c in cards:
        by_category.setdefault(c["category"], []).append(c)
    for cat, items in by_category.items():
        lines = [f"# {cat}", "", f"{len(items)} fiches", ""]
        for c in sorted(items, key=lambda c: str(c["meta"].get("date", "")), reverse=True):
            name = Path(c["path"]).name
            lines.append(f"- {c['meta'].get('date', '')} — [{c['meta'].get('title', name)}]({name})")
        (OUT / "content" / cat / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_index(cards: list[dict], reports: list[dict]) -> None:
    by_category = Counter(c["category"] for c in cards)
    latest = sorted(cards, key=lambda c: str(c["meta"].get("date", "")), reverse=True)[:20]

    lines = [
        "# ResearchOps — Knowledge Base",
        "",
        f"**{len(cards)} fiches** dans {len(by_category)} catégories · **{len(reports)} rapports mensuels**",
        "",
        "Utilisez la recherche (touche `/`) ou la page [Tags](tags.md).",
        "",
        "## Catégories",
        "",
        "| Catégorie | Fiches |",
        "|---|---|",
    ]
    for cat, n in by_category.most_common():
        lines.append(f"| [{cat}](content/{cat}/) | {n} |")
    lines += ["", "## Dernières fiches", ""]
    for c in latest:
        title = c["meta"].get("title", c["path"])
        lines.append(f"- {c['meta'].get('date', '')} — [{title}]({c['path']}) · *{c['category']}*")
    lines += ["", "## Rapports mensuels", ""]
    for r in sorted(reports, key=lambda r: r["path"], reverse=True):
        lines.append(f"- [{Path(r['path']).stem}]({r['path']})")
    (OUT / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT / "tags.md").write_text("# Tags\n\n[TAGS]\n", encoding="utf-8")


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    (OUT / "javascripts").mkdir()
    (OUT / "javascripts" / "mathjax.js").write_text(
        "window.MathJax = {tex: {inlineMath: [['$', '$'], ['\\\\(', '\\\\)']], displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]},"
        "options: {ignoreHtmlClass: '.*|', processHtmlClass: 'arithmatex'}};\n",
        encoding="utf-8",
    )

    cards = copy_markdown(ROOT / "content", OUT / "content") if (ROOT / "content").exists() else []
    reports = copy_markdown(ROOT / "reports", OUT / "reports") if (ROOT / "reports").exists() else []
    if (ROOT / "research").exists():
        copy_markdown(ROOT / "research", OUT / "research")
    write_category_indexes(cards)
    write_index(cards, reports)
    print(f"site_src assembled: {len(cards)} cards, {len(reports)} reports")


if __name__ == "__main__":
    main()
