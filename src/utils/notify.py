import os
import requests

def telegram_notify(message, level="INFO"):
    """
    Sends notification to Telegram
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print(f"[Notify] Telegram not configured. Message: {message}")
        return

    icon = "ℹ️"
    if level == "SUCCESS": icon = "✅"
    elif level == "WARNING": icon = "⚠️"
    elif level == "ERROR": icon = "🚨"
    
    text = f"{icon} **ResearchOps**\n\n{message}"
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[Notify] Failed to send Telegram message: {e}")
