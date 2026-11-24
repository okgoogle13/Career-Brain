"""Single gate for every external LLM call (decision D-A).

policy_check(text, purpose) returns the text to send, or None when the call
must not happen. Callers store None as null and never as 0.

- purpose must be an export profile in config/ai_sharing_policy.json, and the
  target must be listed in approved_targets.
- Red-tier patterns (config/redaction_patterns.json "red_block") block the call
  unless the run sets CB_ALLOW_RED_TIER=1.
- Redaction patterns for each policy redaction.fields_to_scan entry are
  replaced with the policy placeholder before the text leaves the machine.
"""

from __future__ import annotations

import json
import logging
import os
import re
from functools import lru_cache
from pathlib import Path

BASE = Path(__file__).parent.parent
POLICY_PATH = BASE / "config" / "ai_sharing_policy.json"
PATTERNS_PATH = BASE / "config" / "redaction_patterns.json"

log = logging.getLogger("ai_policy")


@lru_cache(maxsize=1)
def _load() -> tuple[dict, dict]:
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    patterns = json.loads(PATTERNS_PATH.read_text(encoding="utf-8"))
    return policy, patterns


def policy_check(text: str, purpose: str, target: str = "gemini_api") -> str | None:
    """Return redacted text that may be sent to `target`, or None if the call is blocked."""
    policy, patterns = _load()
    if purpose not in policy["export_profiles"]:
        log.warning("Policy gate: unknown purpose %r — call blocked", purpose)
        return None
    if target not in policy["approved_targets"]:
        log.warning("Policy gate: target %r not approved — call blocked", target)
        return None
    if os.environ.get("CB_ALLOW_RED_TIER") != "1":
        for category, regexes in patterns["red_block"].items():
            if any(re.search(rx, text) for rx in regexes):
                log.warning("Policy gate: red-tier %s detected (purpose=%s) — call blocked", category, purpose)
                return None
    placeholder = policy["redaction"]["placeholder"]
    for field in policy["redaction"]["fields_to_scan"]:
        for rx in patterns["redact"].get(field, []):
            text = re.sub(rx, placeholder, text)
    return text
