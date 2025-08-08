import os
import tempfile
from unittest.mock import patch

import pytest

from source.token_manager import TokenManager


def test_load_token():
    env_content = (
        "CLIENT_ID=123\n"
        "CLIENT_SECRET=secret\n"
        "ACCESS_TOKEN=access123\n"
        "REFRESH_TOKEN=refresh123\n"
        "EXPIRES_AT=9999999999\n"
    )

    with tempfile.NamedTemporaryFile("w+", delete=False) as tmp_env:
        tmp_env.write(env_content)
        tmp_env.flush()
        path = tmp_env.name

    tm = TokenManager(env_file=path)
    tokens = tm.tokens

    assert tokens["CLIENT_ID"] == 123
    assert tokens["CLIENT_SECRET"] == "secret"
    assert tokens["ACCESS_TOKEN"] == "access123"
    assert tokens["REFRESH_TOKEN"] == "refresh123"
    assert tokens["EXPIRES_AT"] == 9999999999

    os.remove(path)

def test_is_expired_true():
    pass