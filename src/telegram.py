import requests
import logging

logger = logging.getLogger(__name__)


def send_alert(message, bot_token, chat_id):
    """Send a Telegram message. Returns True on success."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        return True
    except requests.RequestException as e:
        logger.error("Error sending Telegram message: %s", e)
        return False
