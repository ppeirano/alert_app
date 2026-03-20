"""Test IOL API connection and quote fetching."""
import sys
from dotenv import load_dotenv
from src.db import get_setting

load_dotenv()


def main():
    symbol = sys.argv[1] if len(sys.argv) > 1 else "GGAL"
    mercado = sys.argv[2] if len(sys.argv) > 2 else "bCBA"

    print(f"=== Test API IOL ===\n")

    # 1. Credentials check
    username = get_setting("iol_username")
    password = get_setting("iol_password")
    if not username or not password:
        print("ERROR: Faltan credenciales IOL en settings.")
        print("Configuralas desde la web en Config.")
        return

    print(f"Usuario: {username}")

    # 2. Authentication
    print("\nAutenticando...", end=" ")
    try:
        from src.iol_client import IOLClient
        iol = IOLClient(username, password)
        print("OK")
        print(f"Token expira: {iol.token_expiry}")
    except Exception as e:
        print(f"FALLO\n  {e}")
        return

    # 3. Get quote
    print(f"\nObteniendo cotizacion {mercado}:{symbol}...", end=" ")
    try:
        quote = iol.get_quote(mercado, symbol)
        print("OK\n")
    except Exception as e:
        print(f"FALLO\n  {e}")
        return

    # 4. Show quote data
    fields = [
        ("Ultimo Precio", "ultimoPrecio"),
        ("Variacion %", "variacion"),
        ("Apertura", "apertura"),
        ("Maximo", "maximo"),
        ("Minimo", "minimo"),
        ("Cierre Anterior", "cierreAnterior"),
        ("Volumen", "volumen"),
    ]
    for label, key in fields:
        val = quote.get(key, "N/A")
        print(f"  {label:20s}: {val}")

    # 5. Puntas (bid/ask)
    puntas = quote.get("puntas")
    if puntas:
        print(f"\n  Puntas:")
        for p in puntas[:3]:
            print(f"    Compra: {p.get('precioCompra', 'N/A')}  |  Venta: {p.get('precioVenta', 'N/A')}")

    print("\n=== Test API completado ===")


if __name__ == "__main__":
    main()
