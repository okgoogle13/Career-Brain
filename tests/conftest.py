import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def _no_real_answer_bank(monkeypatch):
    """Keep the local, personal answer bank out of every test run."""
    import generate_document

    monkeypatch.setattr(generate_document, "ANSWER_BANK_PATH", ROOT / "tests" / "_no_answer_bank.json")
