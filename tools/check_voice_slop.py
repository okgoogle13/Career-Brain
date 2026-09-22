#!/usr/bin/env python3
"""
check_voice_slop.py — Post-generation voice authenticity audit tool (BS-7.5)
=============================================================================
Reads a text file or stdin containing generated job application content
(resume, cover letter, or KSC) and runs it through a Gemini LLM judge
to detect paraphrased slop that bypasses fixed-string checks.

Unlike the banned_phrases / review_phrases checks in scan_voice_phrases()
(which match fixed strings), this tool detects *semantic* anti-patterns:
  - Abstract virtue paragraphs ("I am passionate about helping people")
  - Unfalsifiable claims (no evidence, no number, no named service)
  - Apology openers ("While my background may seem unrelated…")
  - Template voice (generic sentences any applicant could write)

Requires GEMINI_API_KEY (via op run or env).

Usage:
  op run --env-file=".env" -- .venv/bin/python tools/check_voice_slop.py <text_file>
  echo "Cover letter text..." | op run --env-file=".env" -- .venv/bin/python tools/check_voice_slop.py -
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent  # project root

# Load .env from project root
_env_path = BASE / ".env"
if _env_path.exists():
    for _line in _env_path.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("check_voice_slop")

# ─── Prompt ───────────────────────────────────────────────────────────────────

_SLOP_JUDGE_SYSTEM = """\
You are a ruthless editor for job applications in the Australian community
services sector. You detect paraphrased "slop" — generic, unfalsifiable, or
template-sounding text that any applicant could have written.

You will receive a block of application text (resume summary, cover letter
paragraph, or KSC response). Analyse it paragraph by paragraph.

Return ONLY a JSON object with this exact schema (no markdown):
{
  "overall_verdict": "CLEAN" | "REVIEW" | "SLOP",
  "slop_ratio": <float 0.0-1.0, fraction of paragraphs with issues>,
  "paragraphs": [
    {
      "text_snippet": "<first 80 chars of paragraph>",
      "verdict": "CLEAN" | "REVIEW" | "SLOP",
      "pattern": null | "abstract_virtue" | "unfalsifiable_claim" | "apology_opener" | "template_voice",
      "note": "<one sentence — what is wrong, or null>"
    }
  ],
  "top_issues": ["<issue 1>", "<issue 2>"]
}

Anti-patterns to detect:
- abstract_virtue: Asserts a quality ("I am passionate about", "I deeply care")
  without any named action, named service, or observable evidence.
- unfalsifiable_claim: A claim no one could check ("I consistently deliver
  outcomes", "strong communication skills"). No number, no named service,
  no specific example.
- apology_opener: Opens with a concession ("While my background may seem
  unrelated", "Although I do not have direct experience").
- template_voice: So generic it could appear in any application for any role
  ("I am excited to apply for this opportunity", "I would bring my skills
  to your team").

CLEAN = specific, evidenced, named — or a factual sentence (dates, titles, etc.)
REVIEW = borderline — possibly legitimate, worth a human read
SLOP = clearly generic, unfalsifiable, or template

Be strict. A sentence about "400 client interviews at Diamond Valley Community
Support" is CLEAN. "I have extensive experience working with diverse clients"
is SLOP.
"""


def _call_gemini_judge(text: str) -> dict | None:
    """Run the slop judge LLM. Returns parsed JSON or None."""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        log.error("GEMINI_API_KEY not set. Run with: op run --env-file='.env' -- ...")
        return None
    
    try:
        from google import genai  # noqa: PLC0415
        from google.genai import types  # noqa: PLC0415
    except ImportError:
        log.error("google-genai not installed. Run: pip install google-genai")
        return None
    try:
        client = genai.Client(api_key=api_key)
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Analyse this application text:\n\n{text[:4000]}",
            config=types.GenerateContentConfig(
                system_instruction=_SLOP_JUDGE_SYSTEM,
                max_output_tokens=1500,
                temperature=0.1,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
                response_mime_type="application/json",
            ),
        )
        return json.loads(resp.text.strip())
    except Exception as exc:
        log.error("Gemini call failed: %s", exc)
        return None


def _format_report(result: dict, source_label: str) -> str:
    """Format the LLM result as a readable Markdown report."""
    verdict = result.get("overall_verdict", "UNKNOWN")
    slop_ratio = result.get("slop_ratio", 0.0)
    paragraphs = result.get("paragraphs", [])
    top_issues = result.get("top_issues", [])

    verdict_icon = {"CLEAN": "✅", "REVIEW": "⚠️", "SLOP": "🚨"}.get(verdict, "❓")

    lines = [
        f"# Voice Slop Audit — {source_label}",
        "",
        f"**Overall verdict:** {verdict_icon} {verdict}  ",
        f"**Slop ratio:** {slop_ratio:.0%} of paragraphs flagged",
        "",
    ]

    if top_issues:
        lines += ["## Top Issues", ""]
        for issue in top_issues:
            lines.append(f"- {issue}")
        lines.append("")

    if paragraphs:
        slop_paras = [p for p in paragraphs if p.get("verdict") != "CLEAN"]
        if slop_paras:
            lines += ["## Flagged Paragraphs", ""]
            for p in slop_paras:
                icon = {"REVIEW": "⚠️", "SLOP": "🚨"}.get(p.get("verdict", ""), "❓")
                pattern = p.get("pattern") or ""
                note = p.get("note") or ""
                snippet = p.get("text_snippet", "")
                lines += [
                    f"### {icon} {p.get('verdict', '')} — `{pattern}`",
                    f"> …{snippet}…",
                    f"",
                    f"{note}",
                    "",
                ]

    if verdict == "CLEAN":
        lines += ["No slop detected. All paragraphs are specific and evidenced."]

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Semantic voice slop detection for Career Brain generated documents.",
    )
    parser.add_argument(
        "source",
        help="Path to text file to audit, or '-' to read from stdin.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON instead of a Markdown report.",
    )
    args = parser.parse_args()

    if args.source == "-":
        text = sys.stdin.read()
        label = "stdin"
    else:
        path = Path(args.source)
        if not path.exists():
            log.error("File not found: %s", path)
            sys.exit(1)
        text = path.read_text(encoding="utf-8")
        label = path.name

    if not text.strip():
        log.error("Input is empty.")
        sys.exit(1)

    log.info("Auditing %d chars from '%s'…", len(text), label)
    result = _call_gemini_judge(text)

    if result is None:
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(_format_report(result, label))

    # Exit with non-zero if any SLOP detected, for CI use
    if result.get("overall_verdict") == "SLOP":
        sys.exit(2)


if __name__ == "__main__":
    main()
