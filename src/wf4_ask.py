"""
WF4 - Ask the knowledge base.

Trigger: a GitHub issue labelled `ask` (created by the Make bridge when a
Telegram message starts with "?" or by hand). The question is the issue title,
optional precisions in the body.

Two Claude calls:
  1. Selection: pick the most relevant cards from a compact index (title,
     category, tags) - cheap, low effort.
  2. Answer: read the selected cards in full and answer in French, citing [C n].

Nothing is committed; the answer lives in the issue comment and on Telegram.
"""
import json
import os
import re

from anthropic import Anthropic

from utils import frontmatter
from utils.logger import get_logger
from utils.notify import github_issue_comment, set_output, telegram_send_long

log = get_logger("WF4")

CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-5")
MAX_SELECTED = 8
MAX_CHARS_PER_CARD = 9000

ISSUE_TITLE = os.getenv("ISSUE_TITLE", "")
ISSUE_BODY = os.getenv("ISSUE_BODY", "")
ISSUE_NUMBER = os.getenv("ISSUE_NUMBER", "")


def extract_question(title: str, body: str) -> str:
    q = re.sub(r"^\s*(ask|question)\s*:\s*", "", title, flags=re.IGNORECASE).strip()
    q = q.lstrip("?").strip()
    body = (body or "").strip()
    if body and body.lower() != q.lower():
        q = f"{q}\n\nPrécisions : {body}"
    return q


def build_index(cards: list[dict]) -> str:
    lines = []
    for n, card in enumerate(cards, 1):
        meta = card["meta"]
        tags = meta.get("tags", [])
        tags = ", ".join(map(str, tags[:8])) if isinstance(tags, list) else str(tags)
        lines.append(f"[{n}] {meta.get('title', card['path'])} | {card['category']} | {meta.get('date', '')} | {tags}")
    return "\n".join(lines)


def select_cards(client: Anthropic, question: str, cards: list[dict]) -> list[dict]:
    """Ask Claude which cards to read; returns the selected card dicts."""
    prompt = f"""Voici l'index d'une base de connaissances personnelle (fiches de veille R&D, génie des procédés, data science).

QUESTION : {question}

INDEX (numéro | titre | catégorie | date | tags) :
{build_index(cards)}

Sélectionne les fiches les plus pertinentes pour répondre à la question (au plus {MAX_SELECTED}).
Réponds UNIQUEMENT avec un tableau JSON de numéros, par exemple [3, 12, 40]. Tableau vide si rien n'est pertinent."""
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=256,
        output_config={"effort": "low"},
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(b.text for b in response.content if b.type == "text")
    match = re.search(r"\[[\d,\s]*\]", text)
    if not match:
        return []
    try:
        numbers = json.loads(match.group(0))
    except json.JSONDecodeError:
        return []
    selected = []
    for n in numbers[:MAX_SELECTED]:
        if isinstance(n, int) and 1 <= n <= len(cards):
            selected.append(cards[n - 1])
    return selected


def answer(client: Anthropic, question: str, selected: list[dict]) -> str:
    """Answer from the selected cards only, with [C n] citations."""
    if not selected:
        return ("Aucune fiche de la base ne couvre cette question. "
                "Envoyez une URL, un PDF ou une capture au bot pour l'ajouter.")

    docs = []
    sources = []
    for n, card in enumerate(selected, 1):
        meta = card["meta"]
        body = card["body"][:MAX_CHARS_PER_CARD]
        docs.append(f"<card id=\"C{n}\" title=\"{meta.get('title', '')}\" path=\"{card['path']}\">\n{body}\n</card>")
        sources.append(f"[C{n}] {meta.get('title', '')} — `{card['path']}`")

    prompt = f"""Tu réponds à une question en t'appuyant EXCLUSIVEMENT sur les fiches fournies.

RÈGLES :
- Réponds en français, de façon structurée et concise (puces, tableau si utile).
- Cite chaque affirmation avec l'identifiant de la fiche : [C1], [C2]…
- Si les fiches ne répondent pas ou seulement partiellement, dis-le explicitement.
- Termine par une section "Sources" listant les fiches utilisées, une par ligne, au format fourni.

QUESTION : {question}

FICHES :
{chr(10).join(docs)}

FORMAT DES SOURCES :
{chr(10).join(sources)}
"""
    response = client.beta.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=8000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        messages=[{"role": "user", "content": prompt}],
    )
    if response.stop_reason == "refusal":
        return "La requête a été refusée par le modèle."
    log.info(f"Claude usage: in={response.usage.input_tokens} out={response.usage.output_tokens}")
    return "".join(b.text for b in response.content if b.type == "text")


def main() -> None:
    question = extract_question(ISSUE_TITLE, ISSUE_BODY)
    if not question:
        set_output("status", "rejected")
        set_output("message", "Question vide")
        return
    log.info(f"Question: {question[:120]}")

    cards = frontmatter.load_cards("content")
    log.info(f"{len(cards)} cards indexed")

    client = Anthropic()
    selected = select_cards(client, question, cards)
    log.info(f"{len(selected)} cards selected: {[c['path'] for c in selected]}")
    text = answer(client, question, selected)

    repo = os.getenv("GITHUB_REPOSITORY", "")
    issue_link = f"https://github.com/{repo}/issues/{ISSUE_NUMBER}" if repo and ISSUE_NUMBER else ""
    github_issue_comment(ISSUE_NUMBER, f"**Question :** {question}\n\n{text}")

    telegram_text = f"❓ {question.splitlines()[0][:200]}\n\n{text}"
    if len(telegram_text) > 3500:
        telegram_text = telegram_text[:3400] + f"\n\n[…] Réponse complète : {issue_link}"
    telegram_send_long(telegram_text)

    set_output("status", "answered")
    set_output("message", f"{len(selected)} fiches utilisées")


if __name__ == "__main__":
    main()
