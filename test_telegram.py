"""Test Telegram bot connection and message sending."""
from dotenv import load_dotenv
from src.db import get_setting
from src.telegram import send_alert

load_dotenv()


def main():
    print("=== Test Telegram ===\n")

    # 1. Check config
    bot_token = get_setting("telegram_bot_token")
    chat_id = get_setting("telegram_chat_id")

    if not bot_token:
        print("ERROR: Falta telegram_bot_token en settings.")
        return
    if not chat_id:
        print("ERROR: Falta telegram_chat_id en settings.")
        return

    print(f"Bot token: {bot_token[:10]}...{bot_token[-5:]}")
    print(f"Chat ID: {chat_id}")

    # 2. Send test message
    message = (
        "📈 *TEST* IOL Alerts\n"
        "Precio: $5,350.00 (cierre ant: $5,000.00)\n"
        "Regla: Test de conexion"
    )

    print(f"\nEnviando mensaje de prueba...", end=" ")
    ok = send_alert(message, bot_token, chat_id)

    if ok:
        print("OK")
        print("\nRevisa tu Telegram, deberia haber llegado el mensaje.")
    else:
        print("FALLO")
        print("\nVerifica que:")
        print("  1. El bot token sea correcto")
        print("  2. El chat_id sea correcto")
        print("  3. Hayas iniciado una conversacion con el bot (/start)")

    print("\n=== Test Telegram completado ===")


if __name__ == "__main__":
    main()
