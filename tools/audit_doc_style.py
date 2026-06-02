#!/usr/bin/env python3
"""
audit_doc_style.py — Zero-confabulation style gate for Career Brain Google Docs templates.

Mechanically traverses the Google Docs API payload and asserts structural and typographic
rules. Never infers or estimates — only flags explicit deviations found in the API response.

Usage:
    python3 audit_doc_style.py <GOOGLE_DOC_ID> [--theme path/to/theme.json]

Exit codes:
    0 — All checks pass. Prints "STYLE OK".
    1 — One or more FAIL lines printed. Document must be fixed manually.
    2 — Authentication or fetch error.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# ── Auth ──────────────────────────────────────────────────────────────────────

SCOPES = ["https://www.googleapis.com/auth/documents"]
BASE = Path(__file__).parent.parent  # project root
TOKEN_FILE = BASE / "token.json"  # credentials stay in root
CREDENTIALS_FILE = BASE / "credentials.json"  # credentials stay in root


def _get_credentials() -> Credentials:
    creds: Credentials | None = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                print(
                    "ERROR: credentials.json not found. Run generate_document.py once "
                    "to complete OAuth setup, then retry.",
                    file=sys.stderr,
                )
                sys.exit(2)
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
    return creds


# ── Style rules (Defaults) ───────────────────────────────────────────────────

HEADING_NAMED_STYLES = {"HEADING_1", "TITLE"}
FAKE_HEADING_MAX_CHARS = 60         # all-bold NORMAL_TEXT shorter than this → flag

class ExpectedStyle:
    def __init__(self, font: str, normal_size: float, heading_size: float, line_spacing_pct: float, space_below_pt: float):
        self.font = font
        self.normal_size = normal_size
        self.heading_size = heading_size
        self.line_spacing_pct = line_spacing_pct
        self.space_below_pt = space_below_pt

# Default to Calibri if no theme is provided
DEFAULT_STYLE = ExpectedStyle("Calibri", 11.0, 14.0, 115.0, 6.0)


def load_theme_style(theme_path: str) -> ExpectedStyle:
    path = Path(theme_path)
    if not path.exists():
        print(f"ERROR: Theme file not found at {path}", file=sys.stderr)
        sys.exit(2)
    
    try:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        print(f"ERROR: Invalid JSON in {path}: {exc}", file=sys.stderr)
        sys.exit(2)
    
    ats = data.get("ats_constraints", {})
    typo = data.get("typography", {})
    
    font = ats.get("font_family", typo.get("base_font", "Calibri"))
    normal_size = typo.get("base_size_pt", 11.0)
    heading_size = typo.get("section_heading_size_pt", 14.0)
    
    # Line spacing is typically like 1.15 or 1.2
    line_spacing = typo.get("line_spacing", 1.15)
    line_spacing_pct = line_spacing * 100.0
    
    space_below = typo.get("spacing_after_pt", 6.0)
    
    return ExpectedStyle(font, float(normal_size), float(heading_size), float(line_spacing_pct), float(space_below))


# ── Helpers ───────────────────────────────────────────────────────────────────

def _snippet(text: str, max_len: int = 45) -> str:
    text = text.replace("\n", " ").strip()
    return text[:max_len] + "…" if len(text) > max_len else text


def _para_text(paragraph: dict) -> str:
    parts = []
    for el in paragraph.get("elements", []):
        if "textRun" in el:
            parts.append(el["textRun"].get("content", ""))
    return "".join(parts)


# ── Audit logic ───────────────────────────────────────────────────────────────

def _audit(doc: dict, expected: ExpectedStyle) -> list[str]:
    failures: list[str] = []
    table_count = 0
    inline_image_count = 0

    for structural_el in doc.get("body", {}).get("content", []):

        # ── Tables ──
        if "table" in structural_el:
            table_count += 1
            continue

        if "paragraph" not in structural_el:
            continue

        paragraph = structural_el["paragraph"]
        para_style = paragraph.get("paragraphStyle", {})
        named_style = para_style.get("namedStyleType", "NORMAL_TEXT")
        para_snippet = _snippet(_para_text(paragraph))

        # ── Line spacing ──
        line_spacing = para_style.get("lineSpacing")
        if line_spacing is not None:
            if abs(line_spacing - expected.line_spacing_pct) > 0.5:
                failures.append(
                    f"FAIL: Paragraph '{para_snippet}' — line spacing is "
                    f"{line_spacing}% (expected {expected.line_spacing_pct}%)"
                )

        # ── Space below ──
        space_below = para_style.get("spaceBelow", {})
        if space_below:
            magnitude = space_below.get("magnitude", 0.0)
            unit = space_below.get("unit", "PT")
            if unit == "PT" and abs(magnitude - expected.space_below_pt) > 0.5:
                failures.append(
                    f"FAIL: Paragraph '{para_snippet}' — space below is "
                    f"{magnitude}pt (expected {expected.space_below_pt}pt)"
                )

        # ── Per-run checks ──
        elements = paragraph.get("elements", [])
        all_runs_bold = True
        has_text_content = False

        for el in elements:
            # ── Inline images ──
            if "inlineObjectElement" in el:
                inline_image_count += 1
                continue

            if "textRun" not in el:
                continue

            text_run = el["textRun"]
            content = text_run.get("content", "")
            if not content.strip():
                continue

            has_text_content = True
            text_style = text_run.get("textStyle", {})
            run_snippet = _snippet(content)

            # ── Font family ──
            weighted_font = text_style.get("weightedFontFamily", {})
            font_family = weighted_font.get("fontFamily")
            if font_family is None:
                failures.append(
                    f"FAIL: Text run '{run_snippet}' — weightedFontFamily not set "
                    f"(expected '{expected.font}')"
                )
            elif font_family != expected.font:
                failures.append(
                    f"FAIL: Text run '{run_snippet}' — font is '{font_family}' "
                    f"(expected '{expected.font}')"
                )

            # ── Font size ──
            font_size_obj = text_style.get("fontSize", {})
            size_pt = font_size_obj.get("magnitude")
            if size_pt is None:
                failures.append(
                    f"FAIL: Text run '{run_snippet}' — fontSize not set "
                    f"(expected {expected.normal_size}pt)"
                )
            else:
                if named_style in HEADING_NAMED_STYLES:
                    if abs(size_pt - expected.heading_size) > 0.5:
                        failures.append(
                            f"FAIL: Text run '{run_snippet}' in {named_style} — "
                            f"font size is {size_pt}pt (expected {expected.heading_size}pt)"
                        )
                elif named_style == "NORMAL_TEXT":
                    if abs(size_pt - expected.normal_size) > 0.5:
                        failures.append(
                            f"FAIL: Text run '{run_snippet}' in NORMAL_TEXT — "
                            f"font size is {size_pt}pt (expected {expected.normal_size}pt)"
                        )

            # ── Track bold state for fake-heading detection ──
            if not text_style.get("bold", False):
                all_runs_bold = False

        # ── Fake heading detection ──
        full_text = _para_text(paragraph).strip()
        if (
            has_text_content
            and all_runs_bold
            and named_style == "NORMAL_TEXT"
            and 0 < len(full_text) < FAKE_HEADING_MAX_CHARS
        ):
            failures.append(
                f"FAIL: Paragraph '{para_snippet}' — all-bold NORMAL_TEXT resembles a "
                f"heading but must use HEADING_1 or HEADING_2 paragraph style"
            )

    # ── Layout assertions ──
    if table_count > 0:
        failures.append(
            f"FAIL: Document contains {table_count} table(s) — "
            f"tables are forbidden (ATS structural risk)"
        )
    if inline_image_count > 0:
        failures.append(
            f"FAIL: Document contains {inline_image_count} inline image(s) — "
            f"inline objects are forbidden (ATS structural risk)"
        )

    return failures


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Audit a Google Doc against ATS style rules.")
    parser.add_argument("doc_id", help="The ID of the Google Doc to audit")
    parser.add_argument("--theme", help="Path to a theme JSON file to extract style constraints", type=str)
    
    args = parser.parse_args()

    expected_style = DEFAULT_STYLE
    if args.theme:
        expected_style = load_theme_style(args.theme)

    try:
        creds = _get_credentials()
        service = build("docs", "v1", credentials=creds)
        doc = service.documents().get(documentId=args.doc_id).execute()
    except Exception as exc:
        print(f"ERROR: Could not fetch document '{args.doc_id}': {exc}", file=sys.stderr)
        sys.exit(2)

    failures = _audit(doc, expected_style)

    if failures:
        for line in failures:
            print(line)
        sys.exit(1)

    print("STYLE OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
