import os
import tempfile
from unittest.mock import patch, MagicMock, mock_open

import pytest

from source.token_manager import TokenManager
from source.token_manager import TOKEN_URL


@pytest.fixture
def mock_tokens():
    m_tokens = {
        "CLIENT_ID": 123,
        "CLIENT_SECRET": "secret123",
        "ACCESS_TOKEN": "old_token123",
        "REFRESH_TOKEN": "old_refresh123",
        "EXPIRES_AT": 1000
    }
    return m_tokens

@pytest.fixture
def mock_new_data():
    new_data = {
        "access_token": "new_token",
        "refresh_token": "new_refresh",
        "expires_at": 2000
    }
    return new_data

def test_load_tokens(monkeypatch, mock_tokens):
    monkeypatch.setattr("os.getenv", lambda key: mock_tokens[key])
    tm = TokenManager(env_file="dummy.env")
    assert tm.tokens['CLIENT_ID'] == 123
    assert tm.tokens['CLIENT_SECRET'] == 'secret123'

def test_is_expired(mock_tokens):
    tm = TokenManager.__new__(TokenManager)
    tm.tokens = mock_tokens

    with patch("time.time", return_value=tm.tokens["EXPIRES_AT"] + 5):
        assert tm.is_expired() is True
    with patch("time.time", return_value=tm.tokens["EXPIRES_AT"] - 5):
        assert tm.is_expired() is False
    with patch("time.time", return_value=tm.tokens["EXPIRES_AT"]):
        assert tm.is_expired() is False

def test_refresh_access_token_pass(mock_tokens, mock_new_data):
    tm = TokenManager.__new__(TokenManager)
    tm.tokens = mock_tokens

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_new_data

    with patch("requests.post", return_value=mock_response) as mock_post, \
        patch.object(tm, "_save_tokens") as mock_save_tokens, \
        patch.object(tm, "_load_tokens") as mock_load_tokens:

        tm.refresh_access_token()
        mock_post.assert_called_once_with(TOKEN_URL, data={
            "client_id": mock_tokens["CLIENT_ID"],
            "client_secret": mock_tokens["CLIENT_SECRET"],
            "refresh_token": mock_tokens["REFRESH_TOKEN"],
            "grant_type": "refresh_token"
        })
        mock_save_tokens.assert_called_once()
        mock_load_tokens.assert_called_once()

def test_refresh_access_token_fail(mock_tokens):
    tm = TokenManager.__new__(TokenManager)
    tm.tokens = mock_tokens

    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"

    with patch("requests.post", return_value=mock_response):
        with pytest.raises(Exception, match="Unable to refresh access token."):
            tm.refresh_access_token()

def test_get_access_token_not_expired(mock_tokens):
    tm = TokenManager.__new__(TokenManager)
    tm.tokens = mock_tokens

    with patch.object(tm, "is_expired", return_value=False) as mock_is_expired, \
         patch.object(tm, "refresh_access_token") as mock_refresh_access_token:

        token = tm.get_access_token()
        assert token == mock_tokens["ACCESS_TOKEN"]
        mock_is_expired.assert_called_once()
        mock_refresh_access_token.assert_not_called()

def test_get_access_token__expired(mock_tokens):
    tm = TokenManager.__new__(TokenManager)
    tm.tokens = mock_tokens

    with patch.object(tm, "is_expired", return_value=True) as mock_is_expired, \
         patch.object(tm, "refresh_access_token") as mock_refresh_access_token:

        token = tm.get_access_token()
        assert token == mock_tokens["ACCESS_TOKEN"]
        mock_is_expired.assert_called_once()
        mock_refresh_access_token.assert_called_once()