"""
WF2 - Monthly strategic monitor.

Inputs
  A. Internal: knowledge cards captured last month (content/**).
  B. External: new papers from Semantic Scholar for the topics in
     config/monitoring.json (free API, optional key). Google Scholar via SerpAPI
     and Perplexity news were removed: paid, low recall, uncitable.

Output
  reports/<year>/<generation-month>_Monitor.md, French, every claim cited as
  [I<n>] (internal) or [P<n>] (paper), with a bibliography built from the same
  numbering so the model cannot cite something that was not provided.
"""
import calendar
import json
import os
import time
from datetime import date, datetime, timedelta
from pathlib import Path

import requests
from anthropic import Anthropic

from utils import frontmatter
from utils.dedup import compute_hash, load_history, save_history
from utils.logger import get_logger
from utils.notify import telegram_notify

log = get_logger("WF2")

CONFIG_PATH = Path(__file__).parent.parent / "config"
monitoring_config = json.load(open(CONFIG_PATH / "monitoring.json", encoding="utf-8"))
categories_config = json.load(open(CONFIG_PATH / "categories.json", encoding="utf-8"))

CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-5")
S2_API = "https://api.semanticscholar.org/graph/v1/paper/search"
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
def search_semantic_scholar(topic: dict, period_start: date, period_end: date, history: dict) -> list[dict]:
    """New papers for a topic, published in the period, not seen before."""
    headers = {}
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key

    seen_ids: set[str] = set()
    papers: list[dict] = []
    for query in topic.get("keywords_academic", []):
        params = {
            "query": query,
            "publicationDateOrYear": f"{period_start.isoformat()}:{period_end.isoformat()}",
            "fields": S2_FIELDS,
            "limit": 10,
        }
        try:
            r = requests.get(S2_API, params=params, headers=headers, timeout=30)
            if r.status_code == 429:
                log.warning("Semantic Scholar rate limit hit, waiting 5s")
                time.sleep(5)
                r = requests.get(S2_API, params=params, headers=headers, timeout=30)
            r.raise_for_status()
            data = r.json().get("data", []) or []
        except Exception as exc:
            log.warning(f"Semantic Scholar failed for '{query}': {exc}")
            data = []
        for p in data:
            pid = p.get("paperId")
            link = p.get("url") or (f"https://doi.org/{p['externalIds']['DOI']}" if p.get("externalIds", {}).get("DOI") else "")
            if not pid or pid in seen_ids or not link:
                continue
            seen_ids.add(pid)
            if compute_hash(link) in history:
                continue
            papers.append({
                "title": p.get("title", ""),
                "authors": ", ".join(a.get("name", "") for a in (p.get("authors") or [])[:4]),
                "year": p.get("year"),
                "date": p.get("publicationDate") or "",
                "venue": p.get("venue") or "",
                "link": link,
                "abstract": (p.get("abstract") or "")[:1200],
                "citations": p.get("citationCount", 0) or 0,
            })
        time.sleep(1.1)  # unauthenticated S2 allows ~1 request/second

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


# ---------------------------------------------------------------- Main
def main() -> None:
    period_start, period_end = previous_month()
    log.info(f"Generating report for {month_label_fr(period_start)}")

    internal_by_category = get_monthly_internal_content(period_start, period_end)
    total_docs = sum(len(v) for v in internal_by_category.values())
    log.info(f"{total_docs} internal documents in {len(internal_by_category)} categories")

    history = load_history()
    papers: list[dict] = []
    for topic in monitoring_config["topics"]:
        found = search_semantic_scholar(topic, period_start, period_end, history)
        for p in found:
            p["topic"] = topic["name"]
        log.info(f"Topic '{topic['name']}': {len(found)} new papers")
        papers.extend(found)

    if total_docs == 0 and not papers:
        log.warning("Nothing to report this month; skipping generation")
        telegram_notify(f"Veille {month_label_fr(period_start)} : aucune capture ni publication, rapport non généré.", "WARNING")
        return

    context, refs = build_structured_context(internal_by_category, papers, period_start)
    report = synthesize_report(build_prompt(context, refs, period_start, total_docs))

    gen_month = date.today().strftime("%Y-%m")
    output_path = Path("reports") / str(date.today().year) / f"{gen_month}_Monitor.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")

    # Only papers actually reported are marked as seen (previous code burned
    # every search hit, reported or not).
    now = datetime.now().isoformat()
    for p in papers:
        history[compute_hash(p["link"])] = {"url": p["link"], "type": "paper", "added": now}
    save_history(history)

    from utils.git_ops import safe_commit
    safe_commit(files=[str(output_path), "data/history.json"], message=f"WF2: Monthly monitor {gen_month}")

    repo = os.getenv("GITHUB_REPOSITORY", "")
    link = f"https://github.com/{repo}/blob/main/{output_path}" if repo else str(output_path)
    telegram_notify(
        f"Rapport de veille {month_label_fr(period_start)} généré\n{total_docs} captures, {len(papers)} publications\n{link}",
        "SUCCESS",
    )
    log.info(f"Report saved: {output_path}")


if __name__ == "__main__":
    main()
