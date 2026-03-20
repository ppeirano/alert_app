import os
import mysql.connector
from mysql.connector import pooling

_pool = None


def get_pool():
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="iol_alerts",
            pool_size=5,
            host=os.getenv("DB_HOST", "127.0.0.1"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "iol_alerts"),
            charset="utf8mb4",
        )
    return _pool


def get_connection():
    return get_pool().get_connection()


# --- Settings ---

def get_setting(key):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT value FROM settings WHERE key_name = %s", (key,))
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def save_setting(key, value):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO settings (key_name, value) VALUES (%s, %s) "
            "ON DUPLICATE KEY UPDATE value = %s",
            (key, value, value),
        )
        conn.commit()
    finally:
        conn.close()


def get_all_settings():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT key_name, value FROM settings")
        return dict(cur.fetchall())
    finally:
        conn.close()


# --- Alert Rules ---

def get_active_rules():
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM alert_rules WHERE active = TRUE")
        return cur.fetchall()
    finally:
        conn.close()


def get_all_rules():
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM alert_rules ORDER BY created_at DESC")
        return cur.fetchall()
    finally:
        conn.close()


def get_rule(rule_id):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM alert_rules WHERE id = %s", (rule_id,))
        return cur.fetchone()
    finally:
        conn.close()


def create_rule(data):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO alert_rules "
            "(name, type, symbol, mercado, direction, threshold, "
            "underlying, option_type, strike, expiry, `condition`, cooldown_minutes) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                data["name"], data["type"], data["symbol"],
                data.get("mercado", "bCBA"), data.get("direction", "any"),
                data["threshold"], data.get("underlying"),
                data.get("option_type"), data.get("strike"),
                data.get("expiry"), data.get("condition"),
                data.get("cooldown_minutes", 60),
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def update_rule(rule_id, data):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE alert_rules SET "
            "name=%s, type=%s, symbol=%s, mercado=%s, direction=%s, "
            "threshold=%s, underlying=%s, option_type=%s, strike=%s, "
            "expiry=%s, `condition`=%s, cooldown_minutes=%s "
            "WHERE id=%s",
            (
                data["name"], data["type"], data["symbol"],
                data.get("mercado", "bCBA"), data.get("direction", "any"),
                data["threshold"], data.get("underlying"),
                data.get("option_type"), data.get("strike"),
                data.get("expiry"), data.get("condition"),
                data.get("cooldown_minutes", 60),
                rule_id,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def toggle_rule(rule_id, active):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE alert_rules SET active = %s WHERE id = %s",
            (active, rule_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_rule(rule_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM alert_rules WHERE id = %s", (rule_id,))
        conn.commit()
    finally:
        conn.close()


# --- Price History ---

def save_price(symbol, mercado, quote_data, iv=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO price_history "
            "(symbol, mercado, precio, variacion, apertura, maximo, minimo, "
            "cierre_anterior, volumen, iv) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                symbol, mercado,
                quote_data.get("ultimoPrecio"),
                quote_data.get("variacion"),
                quote_data.get("apertura"),
                quote_data.get("maximo"),
                quote_data.get("minimo"),
                quote_data.get("cierreAnterior"),
                quote_data.get("volumen"),
                iv,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def get_last_price(symbol):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM price_history WHERE symbol = %s "
            "ORDER BY timestamp DESC LIMIT 1",
            (symbol,),
        )
        return cur.fetchone()
    finally:
        conn.close()


def get_price_history(symbol, limit=100, date_from=None, date_to=None):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        query = "SELECT * FROM price_history WHERE symbol = %s"
        params = [symbol]
        if date_from:
            query += " AND timestamp >= %s"
            params.append(date_from)
        if date_to:
            query += " AND timestamp <= %s"
            params.append(date_to)
        query += " ORDER BY timestamp DESC LIMIT %s"
        params.append(limit)
        cur.execute(query, params)
        return cur.fetchall()
    finally:
        conn.close()


# --- Alert Log ---

def log_alert(rule_id, message, price):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO alert_log (rule_id, message, price_at_trigger) "
            "VALUES (%s, %s, %s)",
            (rule_id, message, price),
        )
        conn.commit()
    finally:
        conn.close()


def get_last_alert_time(rule_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT sent_at FROM alert_log WHERE rule_id = %s "
            "ORDER BY sent_at DESC LIMIT 1",
            (rule_id,),
        )
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def get_alert_log(limit=100):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT al.*, ar.name as rule_name, ar.symbol "
            "FROM alert_log al "
            "JOIN alert_rules ar ON al.rule_id = ar.id "
            "ORDER BY al.sent_at DESC LIMIT %s",
            (limit,),
        )
        return cur.fetchall()
    finally:
        conn.close()
