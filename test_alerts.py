"""Test alert evaluation against live data."""
import sys
from dotenv import load_dotenv
from src.db import get_setting, get_active_rules

load_dotenv()


def main():
    print("=== Test Evaluacion de Alertas ===\n")

    # 1. Check rules
    rules = get_active_rules()
    if not rules:
        print("No hay reglas activas. Crea una desde la web.")
        return

    print(f"Reglas activas: {len(rules)}")
    for r in rules:
        print(f"  [{r['id']}] {r['name']} | {r['type']} | {r['symbol']} "
              f"| threshold={r['threshold']} | dir={r['direction']}")

    # 2. Authenticate
    username = get_setting("iol_username")
    password = get_setting("iol_password")
    if not username or not password:
        print("\nERROR: Faltan credenciales IOL en settings.")
        return

    print(f"\nAutenticando...", end=" ")
    try:
        from src.iol_client import IOLClient
        iol = IOLClient(username, password)
        print("OK")
    except Exception as e:
        print(f"FALLO\n  {e}")
        return

    # 3. Fetch quotes
    from src.engine import deduplicate_symbols
    symbols = deduplicate_symbols(rules)
    quotes = {}

    print(f"\nObteniendo cotizaciones ({len(symbols)} simbolos)...")
    for mercado, symbol in symbols:
        try:
            quote = iol.get_quote(mercado, symbol)
            quotes[(mercado, symbol)] = quote
            precio = quote.get("ultimoPrecio", "N/A")
            cierre = quote.get("cierreAnterior", "N/A")
            print(f"  {symbol}: precio={precio}, cierre_ant={cierre}")
        except Exception as e:
            print(f"  {symbol}: ERROR - {e}")

    # 4. Evaluate rules
    from src.alerts import evaluate_rules
    triggered = evaluate_rules(rules, quotes)

    print(f"\n--- Resultado ---")
    if triggered:
        print(f"{len(triggered)} alerta(s) se dispararian:\n")
        for rule, msg in triggered:
            print(f"  Regla: {rule['name']}")
            print(f"  Mensaje:")
            for line in msg.split("\n"):
                print(f"    {line}")
            print()
    else:
        print("Ninguna alerta se dispara con los precios actuales.")

        # Show why
        print("\nDetalle:")
        for r in rules:
            key = (r["mercado"], r["symbol"])
            quote = quotes.get(key)
            if not quote:
                print(f"  {r['name']}: sin cotizacion")
                continue
            precio = quote.get("ultimoPrecio", 0)
            cierre = quote.get("cierreAnterior", 0)
            if cierre and float(cierre) > 0:
                pct = ((float(precio) - float(cierre)) / float(cierre)) * 100
                print(f"  {r['name']}: {r['symbol']} var={pct:+.2f}% "
                      f"(threshold={r['threshold']}%)")

    print("\n=== Test Alertas completado ===")


if __name__ == "__main__":
    main()
