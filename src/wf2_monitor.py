"""
WF2 - Monthly strategic monitor.

Inputs
  A. Internal: knowledge cards captured last month (content/**).
  B. External: papers from Semantic Scholar for the active topics in
     config/monitoring.json (free API, optional key) — keyword search, or
     the Recommendations API for a topic with seed_paper_ids. Google
     Scholar via SerpAPI and Perplexity news were removed: paid, low
     recall, uncitable.

Output
  reports/<year>/<generation-month>_Monitor.md, French, every claim cited as
  [I<n>] (internal) or [P<n>] (paper), with a bibliography built from the same
  numbering so the model cannot cite something that was not provided. A
  "Santé du pipeline" section is appended after Claude's narrative, computed
  in Python from data/ingest_log.jsonl so its numbers can't be hallucinated.
"""
import json
import os
import time
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

import requests
from anthropic import Anthropic

from utils import frontmatter
from utils.ingest_log import load_entries
from utils.logger import get_logger
from utils.monitor_seen import load_seen, mark_seen, save_seen
from utils.monitoring_config import load_topics
from utils.notify import telegram_notify

log = get_logger("WF2")

CONFIG_PATH = Path(__file__).parent.parent / "config"
categories_config = json.load(open(CONFIG_PATH / "categories.json", encoding="utf-8"))

CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-5")
S2_SEARCH_API = "https://api.semanticscholar.org/graph/v1/paper/search"
S2_RECOMMEND_API = "https://api.semanticscholar.org/recommendations/v1/papers"
S2_FIELDS = "title,authors,year,publicationDate,url,abstract,citationCount,externalIds,venue"

MONTHS_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
             "août", "septembre", "octobre", "novembre", "décembre"]


def previous_month(today: date | None = None) -> tuple[date, date]:
    """(first_day, last_day) of the month before `today`."""
    today = today or date.today()
    last_day_prev = today.replace(day=1) - timedelta(days=1)
    first_day_prev = last_day_prev.replace(day=1)
    return first_day_prev, last_day_prev


def month_label_fr(d: date) -> str:
    return f"{MONTHS_FR[d.month - 1]} {d.year}"


# ---------------------------------------------------------------- Section A
def get_monthly_internal_content(period_start: date, period_end: date) -> dict[str, list[dict]]:
    """Cards whose frontmatter date (fallback: filename prefix) falls in the period."""
    by_category: dict[str, list[dict]] = {}
    for card in frontmatter.load_cards("content"):
        card_date = _card_date(card)
        if not card_date or not (period_start <= card_date <= period_end):
            continue
        meta = card["meta"]
        by_category.setdefault(card["category"], []).append({
            "filename": Path(card["path"]).name,
            "path": card["path"],
            "title": str(meta.get("title", Path(card["path"]).name)),
            "source": str(meta.get("source", "Unknown")),
            "tags": meta.get("tags", []) if isinstance(meta.get("tags"), list) else [],
            "content": card["body"],
        })
    return by_category


def _card_date(card: dict) -> date | None:
    value = card["meta"].get("date")
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            pass
    name = Path(card["path"]).name
    try:
        return datetime.strptime(name[:8], "%Y%m%d").date()
    except ValueError:
        return None


# ---------------------------------------------------------------- Section B
def _s2_headers() -> dict:
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    return {"x-api-key": api_key} if api_key else {}


def _request_with_backoff(method: str, url: str, **kwargs) -> requests.Response | None:
    """A couple of retries on 429, matching S2's ~1 req/s unauthenticated limit."""
    delay = 2.0
    for attempt in range(3):
        try:
            r = requests.request(method, url, timeout=30, **kwargs)
        except requests.RequestException as exc:
            log.warning(f"Semantic Scholar request failed: {exc}")
            return None
        if r.status_code == 429 and attempt < 2:
            log.warning(f"Semantic Scholar rate limit hit, waiting {delay:.0f}s")
            time.sleep(delay)
            delay *= 2
            continue
        return r
    return None


def _normalize_paper(raw: dict, topic_name: str) -> dict | None:
    pid = raw.get("paperId")
    link = raw.get("url") or (
        f"https://doi.org/{raw['externalIds']['DOI']}" if raw.get("externalIds", {}).get("DOI") else ""
    )
    if not pid or not link:
        return None
    return {
        "paperId": pid,
        "title": raw.get("title", ""),
        "authors": ", ".join(a.get("name", "") for a in (raw.get("authors") or [])[:4]),
        "year": raw.get("year"),
        "date": raw.get("publicationDate") or "",
        "venue": raw.get("venue") or "",
        "link": link,
        "abstract": (raw.get("abstract") or "")[:1200],
        "citations": raw.get("citationCount", 0) or 0,
        "topic": topic_name,
    }


def _passes_filters(paper: dict, topic: dict) -> bool:
    if topic.get("min_year") and (paper["year"] or 0) < topic["min_year"]:
        return False
    haystack = f"{paper['title']} {paper['abstract']}".lower()
    return not any(excluded.lower() in haystack for excluded in topic.get("exclude_keywords", []))


def search_by_keywords(topic: dict, period_start: date, period_end: date) -> list[dict]:
    """Papers matching the topic's keywords, published in the period."""
    seen_ids: set[str] = set()
    papers: list[dict] = []
    for query in topic.get("keywords_academic", []):
        params = {
            "query": query,
            "publicationDateOrYear": f"{period_start.isoformat()}:{period_end.isoformat()}",
            "fields": S2_FIELDS,
            "limit": 10,
        }
        r = _request_with_backoff("GET", S2_SEARCH_API, params=params, headers=_s2_headers())
        data = (r.json().get("data") or []) if r is not None and r.status_code == 200 else []
        for raw in data:
            paper = _normalize_paper(raw, topic["name"])
            if not paper or paper["paperId"] in seen_ids:
                continue
            seen_ids.add(paper["paperId"])
            papers.append(paper)
        time.sleep(1.1)  # unauthenticated S2 allows ~1 request/second
    return papers


def get_recommendations(topic: dict) -> list[dict]:
    """
    Papers similar to the topic's seed_paper_ids (no period filter: the
    Recommendations API returns the most similar papers overall, not "new
    this month" — monitor_seen.json is what keeps it from repeating).
    """
    body = {"positivePaperIds": topic["seed_paper_ids"], "negativePaperIds": topic.get("negative_paper_ids", [])}
    r = _request_with_backoff(
        "POST", S2_RECOMMEND_API, params={"fields": S2_FIELDS, "limit": 20}, headers=_s2_headers(), json=body,
    )
    data = (r.json().get("recommendedPapers") or []) if r is not None and r.status_code == 200 else []
    seen_ids: set[str] = set()
    papers: list[dict] = []
    for raw in data:
        paper = _normalize_paper(raw, topic["name"])
        if not paper or paper["paperId"] in seen_ids:
            continue
        seen_ids.add(paper["paperId"])
        papers.append(paper)
    return papers


def search_semantic_scholar(topic: dict, period_start: date, period_end: date, seen: dict) -> list[dict]:
    """New papers for a topic: Recommendations API if seeded, else keyword search."""
    try:
        papers = get_recommendations(topic) if topic.get("seed_paper_ids") else search_by_keywords(topic, period_start, period_end)
    except Exception as exc:
        log.warning(f"Semantic Scholar failed for topic '{topic['name']}': {exc}")
        return []

    papers = [p for p in papers if _passes_filters(p, topic) and p["paperId"] not in seen]
    papers.sort(key=lambda p: (p["citations"], p["date"]), reverse=True)
    return papers[: topic.get("paper_limit", 3)]


# ---------------------------------------------------------------- Context
def build_structured_context(internal_by_category: dict, papers: list[dict], period: date) -> tuple[str, dict]:
    """
    Numbered context. Returns (context, references) where references maps
    'I1'/'P1' ids to their source description, used to build the bibliography.
    """
    refs: dict[str, str] = {}
    context = f"# Données pour le rapport mensuel — {month_label_fr(period)}\n\n"

    context += "## SECTION A : BASE DE CONNAISSANCES INTERNE (mes captures)\n\n"
    if not internal_by_category:
        context += "*Aucune capture ce mois-ci.*\n\n"
    i = 0
    for category, docs in internal_by_category.items():
        cat_desc = categories_config["categories"].get(category, {}).get("description", "")
        context += f"### Catégorie : {category}\n*{cat_desc}*\n\n"
        for doc in docs:
            i += 1
            ref = f"I{i}"
            refs[ref] = f"{doc['title']} — `{doc['path']}`"
            preview = doc["content"][:3000] + ("…" if len(doc["content"]) > 3000 else "")
            context += (
                f"**[{ref}] {doc['title']}**\n"
                f"- Source : {doc['source']}\n"
                f"- Fichier : `{doc['filename']}`\n"
                f"- Tags : {', '.join(map(str, doc['tags']))}\n\n{preview}\n\n---\n\n"
            )

    context += "## SECTION B : PUBLICATIONS ACADÉMIQUES (Semantic Scholar)\n\n"
    if not papers:
        context += "*Aucune nouvelle publication trouvée ce mois-ci.*\n\n"
    for n, p in enumerate(papers, 1):
        ref = f"P{n}"
        refs[ref] = f"{p['authors']}, « {p['title']} », {p['venue'] or 'n/a'}, {p['year']}, {p['link']}"
        context += (
            f"**[{ref}] {p['title']}**\n"
            f"- Auteurs : {p['authors']}\n- Date : {p['date']} — Citations : {p['citations']}\n"
            f"- Sujet : {p['topic']}\n- URL : {p['link']}\n- Résumé : {p['abstract']}\n\n"
        )
    return context, refs


def build_prompt(context: str, refs: dict, period: date, total_docs: int) -> str:
    bibliography = "\n".join(f"[{k}] {v}" for k, v in refs.items()) or "(aucune référence)"
    return f"""Tu es un ingénieur R&D senior rédigeant un rapport de veille mensuel de qualité scientifique.

RÈGLES STRICTES :
1. CITATIONS OBLIGATOIRES : chaque affirmation cite sa source avec [I1], [P2], etc.
2. UNIQUEMENT les références listées dans la BIBLIOGRAPHIE ci-dessous. N'en invente aucune.
3. NE PAS INVENTER : si une information manque, dis-le. Pas d'hallucination.
4. LANGUE : français.
5. FORMAT : respecte exactement la structure ci-dessous. Recopie la bibliographie telle quelle à la fin.

LÉGENDE : [I n] = document interne (mes captures) ; [P n] = publication académique.

BIBLIOGRAPHIE (à recopier en fin de rapport, sans modification) :
{bibliography}

---

# 🔬 Rapport de Veille Mensuel — {month_label_fr(period)}

**Période couverte :** {month_label_fr(period)}
**Documents internes analysés :** {total_docs}
**Publications externes :** {sum(1 for k in refs if k.startswith('P'))}
**Date de génération :** {date.today().isoformat()}

---

## 📋 Synthèse Exécutive
3 à 5 points clés du mois, chacun cité.

## 🧠 Base de Connaissances Interne
Pour chaque thématique identifiée dans mes captures :
### [Thématique]
**Connaissances mobilisables :** points cités [I n]
**Outils & ressources identifiés :** [I n]
**Applications potentielles :** comment utiliser ces connaissances
(Si aucune capture : une ligne le disant, sans recommandation générique.)

## 🌍 Veille Externe — Frontière Académique
Pour chaque publication : **Titre** — Auteurs (Année) ; contribution clé (1-2 phrases) ; pertinence pour mes travaux ; [P n].

## 🔗 Analyse Croisée
Connexions entre captures internes et publications ; lacunes de ma veille ; confirmations ou contradictions.

## 💡 Recommandations Actionnables
| Priorité | Action | Justification | Refs |
|---|---|---|---|

## 📚 Bibliographie
(recopier la bibliographie fournie)

---

DONNÉES À ANALYSER :

{context}
"""


def synthesize_report(prompt: str) -> str:
    """Generate the report with Claude (adaptive thinking, refusal fallback enabled)."""
    client = Anthropic()
    response = client.beta.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=16000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        messages=[{"role": "user", "content": prompt}],
    )
    if response.stop_reason == "refusal":
        raise RuntimeError(f"Claude refused the request: {getattr(response, 'stop_details', None)}")
    text = "".join(block.text for block in response.content if block.type == "text")
    log.info(f"Claude usage: in={response.usage.input_tokens} out={response.usage.output_tokens} model={response.model}")
    return text


# ---------------------------------------------------------------- Health
def render_health_section(entries: list[dict], internal_by_category: dict, papers: list[dict]) -> str:
    """
    Pipeline health for the period, computed in Python from
    data/ingest_log.jsonl — never asked of the model, so these numbers
    can't drift from what actually happened.
    """
    by_status = Counter(e["status"] for e in entries)
    reject_reasons = Counter(e.get("reason", "unknown") for e in entries if e["status"] in ("rejected", "rejected_pii", "failed"))
    saved = [e for e in entries if e["status"] == "saved"]
    inbox_count = sum(1 for e in saved if e.get("category") == "_Inbox")
    by_category = Counter(category for category, docs in internal_by_category.items() for _ in docs)
    by_topic = Counter(p["topic"] for p in papers)

    lines = ["## 🩺 Santé du pipeline", ""]
    lines.append(
        f"- **Ingestions traitées** : {len(entries)} "
        f"(saved : {by_status.get('saved', 0)}, rejected : {by_status.get('rejected', 0)}, "
        f"rejected_pii : {by_status.get('rejected_pii', 0)}, duplicate : {by_status.get('duplicate', 0)}, "
        f"failed : {by_status.get('failed', 0)})"
    )
    if reject_reasons:
        lines.append("- **Rejets par raison** : " + ", ".join(f"{r} ({n})" for r, n in reject_reasons.most_common()))
    if saved:
        lines.append(f"- **Taux de passage en _Inbox** : {inbox_count / len(saved) * 100:.0f}% ({inbox_count}/{len(saved)})")
    else:
        lines.append("- **Taux de passage en _Inbox** : n/a (aucune fiche sauvegardée)")
    if by_category:
        lines.append("- **Répartition par catégorie** : " + ", ".join(f"{c} ({n})" for c, n in by_category.most_common()))
    if by_topic:
        lines.append("- **Papiers par sujet de veille** : " + ", ".join(f"{t} ({n})" for t, n in by_topic.most_common()))
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- Main
def main() -> None:
    period_start, period_end = previous_month()
    log.info(f"Generating report for {month_label_fr(period_start)}")

    try:
        topics = load_topics(CONFIG_PATH / "monitoring.json")
    except ValueError as exc:
        log.error(str(exc))
        telegram_notify(f"Veille {month_label_fr(period_start)} : config/monitoring.json invalide — {exc}", "ERROR")
        raise

    internal_by_category = get_monthly_internal_content(period_start, period_end)
    total_docs = sum(len(v) for v in internal_by_category.values())
    log.info(f"{total_docs} internal documents in {len(internal_by_category)} categories")

    seen = load_seen()
    papers: list[dict] = []
    for topic in topics:
        found = search_semantic_scholar(topic, period_start, period_end, seen)
        log.info(f"Topic '{topic['name']}': {len(found)} new papers")
        papers.extend(found)

    if total_docs == 0 and not papers:
        log.warning("Nothing to report this month; skipping generation")
        telegram_notify(f"Veille {month_label_fr(period_start)} : aucune capture ni publication, rapport non généré.", "WARNING")
        return

    context, refs = build_structured_context(internal_by_category, papers, period_start)
    report = synthesize_report(build_prompt(context, refs, period_start, total_docs))

    entries = load_entries(period_start, period_end)
    report += "\n---\n\n" + render_health_section(entries, internal_by_category, papers)

    gen_month = date.today().strftime("%Y-%m")
    output_path = Path("reports") / str(date.today().year) / f"{gen_month}_Monitor.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")

    # Only papers actually reported are marked as seen (burning every search
    # hit regardless of whether it made the cut would starve future months).
    for p in papers:
        mark_seen(seen, p["paperId"], date.today())
    save_seen(seen)

    from utils.git_ops import safe_commit
    safe_commit(files=[str(output_path), "data/monitor_seen.json"], message=f"WF2: Monthly monitor {gen_month}")

    repo = os.getenv("GITHUB_REPOSITORY", "")
    link = f"https://github.com/{repo}/blob/main/{output_path}" if repo else str(output_path)
    telegram_notify(
        f"Rapport de veille {month_label_fr(period_start)} généré\n{total_docs} captures, {len(papers)} publications\n{link}",
        "SUCCESS",
    )
    log.info(f"Report saved: {output_path}")


if __name__ == "__main__":
    main()
