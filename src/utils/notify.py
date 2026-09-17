"""
Outbound notifications: Telegram, GitHub issue comments, GitHub Actions outputs.
"""
import os

import requests

from utils.logger import get_logger

log = get_logger("NOTIFY")

TELEGRAM_MAX_CHARS = 4000  # hard API limit is 4096


def telegram_notify(message: str, level: str = "INFO") -> None:
    """Send a short status message to the configured Telegram chat."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        log.info(f"Telegram not configured. Message: {message}")
        return

    icon = {"SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "🚨"}.get(level, "ℹ️")
    text = f"{icon} *ResearchOps*\n\n{message}"
    _telegram_send(token, chat_id, text, parse_mode="Markdown")


def telegram_send_long(message: str) -> None:
    """Send a long plain-text message, split into API-sized chunks."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        log.info(f"Telegram not configured. Message: {message[:200]}")
        return
    for i in range(0, len(message), TELEGRAM_MAX_CHARS):
        _telegram_send(token, chat_id, message[i:i + TELEGRAM_MAX_CHARS], parse_mode=None)


def _telegram_send(token: str, chat_id: str, text: str, parse_mode: str | None) -> None:
    payload = {"chat_id": chat_id, "text": text, "disable_web_page_preview": True}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    try:
        r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json=payload, timeout=10)
        if parse_mode and r.status_code == 400:
            # Telegram answers 400 on Markdown parse errors, common with generated text: retry as plain text
            payload.pop("parse_mode", None)
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json=payload, timeout=10)
    except Exception as exc:  # network errors must never fail a workflow
        log.warning(f"Failed to send Telegram message: {exc}")


def github_issue_comment(issue_number: str | int, body: str) -> bool:
    """Post a comment on an issue using the Actions token (GITHUB_TOKEN)."""
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    if not token or not repo or not issue_number:
        log.info("GitHub comment skipped (no token/repo/issue)")
        return False
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    try:
        r = requests.post(url, headers=headers, json={"body": body}, timeout=15)
        return r.status_code == 201
    except Exception as exc:
        log.warning(f"Failed to comment on issue #{issue_number}: {exc}")
        return False


def set_output(name: str, value: str) -> None:
    """Expose a single-line value to later workflow steps via $GITHUB_OUTPUT."""
    value = str(value).replace("\n", " ").strip()
    path = os.getenv("GITHUB_OUTPUT")
    if not path:
        log.debug(f"output {name}={value}")
        return
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{name}={value}\n")
