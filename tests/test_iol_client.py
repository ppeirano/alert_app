from unittest.mock import patch, MagicMock
from src.iol_client import IOLClient


@patch("src.iol_client.requests.post")
def test_authenticate(mock_post):
    """Test that authentication sends correct request."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "access_token": "test_token",
        "refresh_token": "test_refresh",
        ".expires": "2026-12-31T23:59:59",
    }
    mock_resp.raise_for_status = MagicMock()
    mock_post.return_value = mock_resp

    client = IOLClient("user@test.com", "pass123")

    assert client.access_token == "test_token"
    assert client.refresh_token == "test_refresh"
    mock_post.assert_called_once()
    call_data = mock_post.call_args[1]["data"]
    assert call_data["username"] == "user@test.com"
    assert call_data["grant_type"] == "password"


@patch("src.iol_client.requests.get")
@patch("src.iol_client.requests.post")
def test_get_quote(mock_post, mock_get):
    """Test quote fetching."""
    # Auth
    mock_auth = MagicMock()
    mock_auth.json.return_value = {
        "access_token": "tok", "refresh_token": "ref",
        ".expires": "2026-12-31T23:59:59",
    }
    mock_auth.raise_for_status = MagicMock()
    mock_post.return_value = mock_auth

    # Quote
    mock_quote = MagicMock()
    mock_quote.json.return_value = {"ultimoPrecio": 1850.0, "variacion": -2.5}
    mock_quote.raise_for_status = MagicMock()
    mock_get.return_value = mock_quote

    client = IOLClient("user", "pass")
    quote = client.get_quote("bCBA", "GGAL")

    assert quote["ultimoPrecio"] == 1850.0
    mock_get.assert_called_once()
    assert "bCBA/Titulos/GGAL/Cotizacion" in mock_get.call_args[0][0]
