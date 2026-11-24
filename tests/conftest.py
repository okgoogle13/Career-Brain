import os
import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "pipeline"))

# Blank (not delete) secrets before any tool module is imported: the .env
# loaders use setdefault, so an empty value blocks repopulation from .env.
for _key in (
    "GEMINI_API_KEY",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "GOOGLE_OAUTH_CLIENT_SECRETS",
    "GOOGLE_OAUTH_TOKEN",
):
    os.environ[_key] = ""

import pytest  # noqa: E402


def _blocked(*_args, **_kwargs):
    raise RuntimeError("Network access is blocked during tests")


@pytest.fixture(autouse=True, scope="session")
def _no_network():
    """Fail any test that tries to open a network connection."""
    original_connect = socket.socket.connect
    original_create = socket.create_connection
    socket.socket.connect = _blocked
    socket.create_connection = _blocked
    yield
    socket.socket.connect = original_connect
    socket.create_connection = original_create


@pytest.fixture(autouse=True)
def _no_real_answer_bank(monkeypatch):
    """Keep the local, personal answer bank out of every test run."""
    import generate_document

    monkeypatch.setattr(generate_document, "ANSWER_BANK_PATH", ROOT / "tests" / "_no_answer_bank.json")
