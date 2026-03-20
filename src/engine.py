import logging
import time
from datetime import datetime, date

import schedule
from dotenv import load_dotenv

from src.db import (
    get_active_rules, get_setting, save_price, log_alert,
)
from src.iol_client import IOLClient
from src.alerts import evaluate_rules
from src.telegram import send_alert
from src.iv import calc_iv

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def is_market_hours():
    """Check if current time is within configured market hours (Mon-Fri)."""
    now = datetime.now()
    if now.weekday() >= 5:  # Saturday=5, Sunday=6
        return False

    market_open = get_setting("market_open") or "11:00"
    market_close = get_setting("market_close") or "17:00"

    open_h, open_m = map(int, market_open.split(":"))
    close_h, close_m = map(int, market_close.split(":"))

    current = now.hour * 60 + now.minute
    return (open_h * 60 + open_m) <= current < (close_h * 60 + close_m)


def deduplicate_symbols(rules):
    """Extract unique (mercado, symbol) pairs from rules."""
    symbols = set()
    for r in rules:
        symbols.add((r["mercado"], r["symbol"]))
        # For IV rules, also need the underlying
        if r["type"] == "iv_threshold" and r.get("underlying"):
            symbols.add((r["mercado"], r["underlying"]))
    return symbols


def compute_iv_for_rule(rule, quotes):
    """Compute implied volatility for an IV threshold rule."""
    key = (rule["mercado"], rule["symbol"])
    option_quote = quotes.get(key)
    if not option_quote or not option_quote.get("ultimoPrecio"):
        return None

    underlying_key = (rule["mercado"], rule["underlying"])
    underlying_quote = quotes.get(underlying_key)
    if not underlying_quote or not underlying_quote.get("ultimoPrecio"):
        return None

    option_price = float(option_quote["ultimoPrecio"])
    spot = float(underlying_quote["ultimoPrecio"])
    strike = float(rule["strike"])
    expiry = rule["expiry"]

    if isinstance(expiry, str):
        expiry = date.fromisoformat(expiry)
    days_to_expiry = (expiry - date.today()).days
    if days_to_expiry <= 0:
        return None

    T = days_to_expiry / 365.0
    r = float(get_setting("risk_free_rate") or "0.40")
    option_type = rule.get("option_type", "call")

    return calc_iv(option_price, spot, strike, T, r, option_type)


def check_alerts():
    """Main alert checking cycle."""
    if not is_market_hours():
        return

    logger.info("Running alert check...")

    username = get_setting("iol_username")
    password = get_setting("iol_password")
    bot_token = get_setting("telegram_bot_token")
    chat_id = get_setting("telegram_chat_id")

    if not all([username, password, bot_token, chat_id]):
        logger.warning("Missing credentials in settings. Skipping check.")
        return

    try:
        iol = IOLClient(username, password)
    except Exception as e:
        logger.error("IOL authentication failed: %s", e)
        return

    rules = get_active_rules()
    if not rules:
        logger.info("No active rules. Skipping.")
        return

    symbols = deduplicate_symbols(rules)

    # Fetch all quotes
    quotes = {}
    for mercado, symbol in symbols:
        try:
            quote = iol.get_quote(mercado, symbol)
            quotes[(mercado, symbol)] = quote
        except Exception as e:
            logger.error("Failed to fetch quote for %s:%s: %s", mercado, symbol, e)

    # Compute IVs for IV rules
    ivs = {}
    for rule in rules:
        if rule["type"] == "iv_threshold":
            iv = compute_iv_for_rule(rule, quotes)
            if iv is not None:
                ivs[rule["symbol"]] = iv

    # Evaluate rules
    triggered = evaluate_rules(rules, quotes, ivs)

    # Send alerts and log
    for rule, message in triggered:
        key = (rule["mercado"], rule["symbol"])
        quote = quotes.get(key, {})
        price = quote.get("ultimoPrecio")

        if send_alert(message, bot_token, chat_id):
            log_alert(rule["id"], message, price)
            logger.info("Alert sent: %s", rule["name"])
        else:
            logger.error("Failed to send alert: %s", rule["name"])

    # Save price history for all fetched quotes
    for (mercado, symbol), quote in quotes.items():
        iv = ivs.get(symbol)
        save_price(symbol, mercado, quote, iv)

    logger.info("Check complete. %d alerts triggered.", len(triggered))


def main():
    logger.info("IOL Alert Engine started.")
    interval = int(get_setting("poll_interval_minutes") or "2")
    schedule.every(interval).minutes.do(check_alerts)

    # Run once immediately
    check_alerts()

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
