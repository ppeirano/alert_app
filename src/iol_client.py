import requests
from datetime import datetime, timedelta


class IOLClient:
    TOKEN_URL = "https://api.invertironline.com/token"
    BASE_URL = "https://api.invertironline.com"

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
        self.authenticate()

    def authenticate(self):
        resp = requests.post(
            self.TOKEN_URL,
            data={
                "username": self.username,
                "password": self.password,
                "grant_type": "password",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        self._store_token(data)

    def _store_token(self, data):
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        expires_str = data.get(".expires", "")
        if expires_str:
            try:
                self.token_expiry = datetime.fromisoformat(expires_str)
            except ValueError:
                self.token_expiry = datetime.utcnow() + timedelta(minutes=14)
        else:
            self.token_expiry = datetime.utcnow() + timedelta(minutes=14)

    def _refresh(self):
        resp = requests.post(
            self.TOKEN_URL,
            data={
                "refresh_token": self.refresh_token,
                "grant_type": "refresh_token",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=15,
        )
        resp.raise_for_status()
        self._store_token(resp.json())

    def _ensure_token(self):
        if self.token_expiry and datetime.utcnow() >= self.token_expiry - timedelta(seconds=60):
            self._refresh()

    def _get(self, path):
        self._ensure_token()
        resp = requests.get(
            f"{self.BASE_URL}{path}",
            headers={"Authorization": f"Bearer {self.access_token}"},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def get_quote(self, mercado, simbolo):
        """Get current quote for a symbol.

        Returns dict with keys: ultimoPrecio, variacion, apertura, maximo,
        minimo, cierreAnterior, volumen, puntas, etc.
        """
        return self._get(f"/api/v2/{mercado}/Titulos/{simbolo}/Cotizacion")

    def get_quote_detail(self, mercado, simbolo):
        """Get detailed quote for a symbol."""
        return self._get(f"/api/v2/{mercado}/Titulos/{simbolo}/CotizacionDetalle")

    def get_options(self, mercado, simbolo):
        """Get options chain for an underlying symbol.

        Returns list of option dicts.
        """
        return self._get(f"/api/v2/{mercado}/Titulos/{simbolo}/Opciones")

    def get_title(self, mercado, simbolo):
        """Get security details."""
        return self._get(f"/api/v2/{mercado}/Titulos/{simbolo}")
