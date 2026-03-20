import logging
from datetime import datetime, timedelta
from src.db import get_last_price, get_last_alert_time

logger = logging.getLogger(__name__)


def evaluate_rules(rules, quotes, ivs=None):
    """Evaluate all alert rules against current data.

    Args:
        rules: list of rule dicts from DB
        quotes: dict mapping (mercado, symbol) -> quote data
        ivs: dict mapping symbol -> current IV (for iv_threshold rules)

    Returns:
        list of (rule, message) tuples for triggered alerts
    """
    ivs = ivs or {}
    triggered = []

    for rule in rules:
        if not _cooldown_ok(rule):
            continue

        key = (rule["mercado"], rule["symbol"])
        quote = quotes.get(key)
        if not quote:
            continue

        current_price = quote.get("ultimoPrecio")
        if current_price is None:
            continue

        prev = get_last_price(rule["symbol"])
        msg = None

        if rule["type"] == "price_pct_change":
            msg = _check_pct_change(rule, current_price, prev)
        elif rule["type"] == "price_abs_change":
            msg = _check_abs_change(rule, current_price, prev)
        elif rule["type"] == "iv_threshold":
            current_iv = ivs.get(rule["symbol"])
            prev_iv = prev.get("iv") if prev else None
            msg = _check_iv_cross(rule, current_iv, prev_iv)

        if msg:
            triggered.append((rule, msg))

    return triggered


def _cooldown_ok(rule):
    """Check if enough time has passed since last alert for this rule."""
    last_alert = get_last_alert_time(rule["id"])
    if last_alert is None:
        return True
    cooldown = timedelta(minutes=rule.get("cooldown_minutes", 60))
    return datetime.now() - last_alert >= cooldown


def _check_pct_change(rule, current_price, prev):
    """Check percentage change alert."""
    if prev is None or prev.get("precio") is None:
        return None

    prev_price = float(prev["precio"])
    if prev_price == 0:
        return None

    pct = ((current_price - prev_price) / prev_price) * 100
    threshold = float(rule["threshold"])
    direction = rule.get("direction", "any")

    fired = False
    if direction == "down" and pct <= -threshold:
        fired = True
    elif direction == "up" and pct >= threshold:
        fired = True
    elif direction == "any" and abs(pct) >= threshold:
        fired = True

    if fired:
        arrow = "📉" if pct < 0 else "📈"
        return (
            f"{arrow} *{rule['symbol']}* {pct:+.2f}%\n"
            f"Precio: ${current_price:,.2f} (anterior: ${prev_price:,.2f})\n"
            f"Regla: {rule['name']}"
        )
    return None


def _check_abs_change(rule, current_price, prev):
    """Check absolute change alert."""
    if prev is None or prev.get("precio") is None:
        return None

    prev_price = float(prev["precio"])
    diff = current_price - prev_price
    threshold = float(rule["threshold"])
    direction = rule.get("direction", "any")

    fired = False
    if direction == "down" and diff <= -threshold:
        fired = True
    elif direction == "up" and diff >= threshold:
        fired = True
    elif direction == "any" and abs(diff) >= threshold:
        fired = True

    if fired:
        arrow = "📉" if diff < 0 else "📈"
        return (
            f"{arrow} *{rule['symbol']}* {diff:+,.2f}\n"
            f"Precio: ${current_price:,.2f} (anterior: ${prev_price:,.2f})\n"
            f"Regla: {rule['name']}"
        )
    return None


def _check_iv_cross(rule, current_iv, prev_iv):
    """Check implied volatility threshold crossing."""
    if current_iv is None:
        return None

    threshold = float(rule["threshold"])
    condition = rule.get("condition", "above")

    # First run: no previous IV, just record without alerting
    if prev_iv is None:
        return None

    prev_iv = float(prev_iv)
    crossed_above = prev_iv < threshold <= current_iv
    crossed_below = prev_iv > threshold >= current_iv

    if condition == "above" and crossed_above:
        direction = "SUBE"
    elif condition == "below" and crossed_below:
        direction = "BAJA"
    elif condition == "either" and (crossed_above or crossed_below):
        direction = "SUBE" if crossed_above else "BAJA"
    else:
        return None

    return (
        f"⚡ IV *{rule['symbol']}* {direction} umbral {threshold:.0%}\n"
        f"IV: {prev_iv:.2%} → {current_iv:.2%}\n"
        f"Regla: {rule['name']}"
    )
