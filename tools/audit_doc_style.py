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

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]
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

def _audit(doc: dict, expected: ExpectedStyle, theme_data: dict | None = None) -> list[str]:
    failures: list[str] = []
    table_count = 0
    inline_image_count = 0

    # If it is a v2.0 template (has blocks), run role-aware paragraph audit
    if theme_data and "blocks" in theme_data:
        try:
            import sys
            # Add BASE to path to import build_golden_master
            sys.path.insert(0, str(BASE))
            from build_golden_master import build_paragraphs
        except ImportError as exc:
            failures.append(f"FAIL: Could not import build_paragraphs for verification: {exc}")
            return failures

        expected_paras = build_paragraphs(theme_data)
        doc_type = theme_data.get("doc_type", "resume")
        
        # Helper to get block config
        def get_block(block_id):
            return next((b for b in theme_data.get("blocks", []) if b["block_id"] == block_id), None)

        exp_block = get_block("experience_section")
        ev = exp_block["visualConfig"] if exp_block else {"role_title": {}, "role_meta": {}, "bullet": {}}

        skills_block = get_block("skills_section")
        sv = skills_block["visualConfig"] if skills_block else {"item": {}}

        name_block = get_block("name_header")
        nv = name_block["visualConfig"] if name_block else {"font_size_pt": 24, "font_color": "#000000"}

        summary_block = get_block("summary_section")
        h1_vc = summary_block["visualConfig"]["heading"] if summary_block and "visualConfig" in summary_block else {"font_size_pt": 14, "font_color": "#000000"}

        contact_block = get_block("contact_info")
        cv = contact_block["visualConfig"] if contact_block else {"font_size_pt": 11, "font_color": "#444444"}

        headline_block = get_block("role_headline")
        hv = headline_block["visualConfig"] if headline_block else {"font_size_pt": 12, "font_color": "#1A1A1A"}

        criteria_block = get_block("criteria_responses")
        ksc_cv = criteria_block["visualConfig"]["criterion_text"] if criteria_block else {}

        # Default body settings from typography
        typo = theme_data.get("typography", {})
        body_size = typo.get("base_size_pt", 11.0)
        body_color = theme_data.get("palette", {}).get("body_text", "#1A1A1A")
        font = typo.get("base_font", "Calibri")
        heading_font = (theme_data.get("heading_font_family") or [font])[0]

        # 1. Collect all non-empty paragraphs from document
        doc_paras = []
        for structural_el in doc.get("body", {}).get("content", []):
            if "table" in structural_el:
                table_count += 1
            if "paragraph" in structural_el:
                paragraph = structural_el["paragraph"]
                full_text = _para_text(paragraph)
                
                # Check for inline images
                for el in paragraph.get("elements", []):
                    if "inlineObjectElement" in el:
                        inline_image_count += 1
                        
                if full_text.strip():  # ignore blank lines
                    doc_paras.append(paragraph)

        # 2. Check counts
        if len(doc_paras) != len(expected_paras):
            failures.append(
                f"FAIL: Paragraph count mismatch. Google Doc has {len(doc_paras)} "
                f"non-empty paragraphs, expected {len(expected_paras)}"
            )

        # 3. Step-by-step styles comparison
        for idx, (doc_para, (exp_text, exp_named_style, exp_bold, exp_italic, role)) in enumerate(zip(doc_paras, expected_paras)):
            para_style = doc_para.get("paragraphStyle", {})
            named_style = para_style.get("namedStyleType", "NORMAL_TEXT")
            para_snippet = _snippet(_para_text(doc_para))

            if named_style != exp_named_style:
                failures.append(
                    f"FAIL: Paragraph '{para_snippet}' (role '{role}') — named style is "
                    f"'{named_style}' (expected '{exp_named_style}')"
                )

            # Map the expected block configs
            if role == "name":
                font_size = nv.get("font_size_pt", 24)
                color = nv.get("font_color", "#000000")
                line_spacing_pct = 115.0
                space_below = nv.get("margin_bottom_pt", 2.0)
            elif role == "contact":
                font_size = cv.get("font_size_pt", 11)
                color = cv.get("font_color", "#444444")
                line_spacing_pct = cv.get("line_spacing", 1.15) * 100.0
                space_below = cv.get("margin_bottom_pt", 2.0)
            elif role == "headline":
                font_size = hv.get("font_size_pt", 12)
                color = hv.get("font_color", "#1A1A1A")
                line_spacing_pct = 115.0
                space_below = hv.get("margin_bottom_pt", 8.0)
            elif role == "employer":
                font_size = body_size
                color = body_color
                line_spacing_pct = typo.get("line_spacing", 1.15) * 100.0
                space_below = 2.0
            elif role == "h1":
                font_size = h1_vc.get("font_size_pt", 14)
                color = h1_vc.get("font_color", "#000000")
                line_spacing_pct = 115.0
                space_below = h1_vc.get("margin_bottom_pt", 6.0)
            elif role == "h2":
                if doc_type == "ksc":
                    font_size = ksc_cv.get("font_size_pt", 12)
                    color = ksc_cv.get("font_color", "#000000")
                    space_below = ksc_cv.get("margin_bottom_pt", 8.0)
                else:
                    rt = ev.get("role_title", {})
                    font_size = rt.get("font_size_pt", 12)
                    color = rt.get("font_color", "#000000")
                    space_below = rt.get("margin_top_pt", 8.0)
                line_spacing_pct = 115.0
            elif role == "role_meta":
                rm = ev.get("role_meta", {})
                font_size = rm.get("font_size_pt", 11)
                color = rm.get("font_color", "#444444")
                line_spacing_pct = 115.0
                space_below = rm.get("margin_bottom_pt", 4.0)
            elif role == "bullet":
                b_vc = ev.get("bullet", {})
                font_size = b_vc.get("font_size_pt", body_size)
                color = b_vc.get("font_color", body_color)
                line_spacing_pct = b_vc.get("line_spacing", 1.2) * 100.0
                space_below = b_vc.get("margin_bottom_pt", 2.0)
            elif role == "skills_body":
                item = sv.get("item", {})
                font_size = item.get("font_size_pt", body_size)
                color = item.get("font_color", body_color)
                line_spacing_pct = 115.0
                space_below = 6.0
            else:  # body
                font_size = body_size
                color = body_color
                line_spacing_pct = typo.get("line_spacing", 1.15) * 100.0
                space_below = typo.get("spacing_after_pt", 6.0)

            # Line spacing check
            ls = para_style.get("lineSpacing")
            if ls is not None:
                if abs(ls - line_spacing_pct) > 0.5:
                    failures.append(
                        f"FAIL: Paragraph '{para_snippet}' (role '{role}') — line spacing is "
                        f"{ls}% (expected {line_spacing_pct}%)"
                    )

            # Space below check
            sb = para_style.get("spaceBelow", {})
            if sb:
                mag = sb.get("magnitude", 0.0)
                unit = sb.get("unit", "PT")
                if unit == "PT" and abs(mag - space_below) > 0.5:
                    failures.append(
                        f"FAIL: Paragraph '{para_snippet}' (role '{role}') — space below is "
                        f"{mag}pt (expected {space_below}pt)"
                    )

            # Text runs style check
            for el in doc_para.get("elements", []):
                if "textRun" not in el:
                    continue
                text_run = el["textRun"]
                content = text_run.get("content", "")
                if not content.strip():
                    continue
                run_snippet = _snippet(content)
                text_style = text_run.get("textStyle", {})

                # Check bold / italic
                bold = text_style.get("bold", False)
                italic = text_style.get("italic", False)
                if bold != exp_bold:
                    failures.append(
                        f"FAIL: Text run '{run_snippet}' (role '{role}') — bold is "
                        f"{bold} (expected {exp_bold})"
                    )
                if italic != exp_italic:
                    failures.append(
                        f"FAIL: Text run '{run_snippet}' (role '{role}') — italic is "
                        f"{italic} (expected {exp_italic})"
                    )

                # Check font family (accept absent if default Arial)
                expected_font = heading_font if role in ("name", "headline", "h1", "h2") else font
                weighted_font = text_style.get("weightedFontFamily", {})
                font_family = weighted_font.get("fontFamily")
                if font_family is None:
                    if expected_font != "Arial":
                        failures.append(
                            f"FAIL: Text run '{run_snippet}' (role '{role}') — weightedFontFamily not set "
                            f"(expected '{expected_font}')"
                        )
                elif font_family != expected_font:
                    failures.append(
                        f"FAIL: Text run '{run_snippet}' (role '{role}') — font is '{font_family}' "
                        f"(expected '{expected_font}')"
                    )

                # Check font size (accept absent if default 11.0pt)
                font_size_obj = text_style.get("fontSize", {})
                size_pt = font_size_obj.get("magnitude")
                if size_pt is None:
                    if not (abs(font_size - 11.0) < 0.1):
                        failures.append(
                            f"FAIL: Text run '{run_snippet}' (role '{role}') — fontSize not set "
                            f"(expected {font_size}pt)"
                        )
                elif abs(size_pt - font_size) > 0.5:
                    failures.append(
                        f"FAIL: Text run '{run_snippet}' (role '{role}') — font size is "
                        f"{size_pt}pt (expected {font_size}pt)"
                    )

    else:
        # Fallback to default style audit for legacy files
        for structural_el in doc.get("body", {}).get("content", []):
            if "table" in structural_el:
                table_count += 1
                continue

            if "paragraph" not in structural_el:
                continue

            paragraph = structural_el["paragraph"]
            para_style = paragraph.get("paragraphStyle", {})
            named_style = para_style.get("namedStyleType", "NORMAL_TEXT")
            para_snippet = _snippet(_para_text(paragraph))

            line_spacing = para_style.get("lineSpacing")
            if line_spacing is not None:
                if abs(line_spacing - expected.line_spacing_pct) > 0.5:
                    failures.append(
                        f"FAIL: Paragraph '{para_snippet}' — line spacing is "
                        f"{line_spacing}% (expected {expected.line_spacing_pct}%)"
                    )

            space_below = para_style.get("spaceBelow", {})
            if space_below:
                magnitude = space_below.get("magnitude", 0.0)
                unit = space_below.get("unit", "PT")
                if unit == "PT" and abs(magnitude - expected.space_below_pt) > 0.5:
                    failures.append(
                        f"FAIL: Paragraph '{para_snippet}' — space below is "
                        f"{magnitude}pt (expected {expected.space_below_pt}pt)"
                    )

            elements = paragraph.get("elements", [])
            all_runs_bold = True
            has_text_content = False

            for el in elements:
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

                weighted_font = text_style.get("weightedFontFamily", {})
                font_family = weighted_font.get("fontFamily")
                if font_family is None:
                    if expected.font != "Arial":
                        failures.append(
                            f"FAIL: Text run '{run_snippet}' — weightedFontFamily not set "
                            f"(expected '{expected.font}')"
                        )
                elif font_family != expected.font:
                    failures.append(
                        f"FAIL: Text run '{run_snippet}' — font is '{font_family}' "
                        f"(expected '{expected.font}')"
                    )

                font_size_obj = text_style.get("fontSize", {})
                size_pt = font_size_obj.get("magnitude")
                if size_pt is None:
                    if not (expected.font == "Arial" and abs(expected.normal_size - 11.0) < 0.1):
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

                if not text_style.get("bold", False):
                    all_runs_bold = False

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
    theme_data = None
    if args.theme:
        expected_style = load_theme_style(args.theme)
        theme_path = Path(args.theme)
        if theme_path.exists():
            try:
                theme_data = json.loads(theme_path.read_text(encoding="utf-8"))
            except Exception:
                pass

    try:
        creds = _get_credentials()
        service = build("docs", "v1", credentials=creds)
        doc = service.documents().get(documentId=args.doc_id).execute()
    except Exception as exc:
        print(f"ERROR: Could not fetch document '{args.doc_id}': {exc}", file=sys.stderr)
        sys.exit(2)

    failures = _audit(doc, expected_style, theme_data)

    if failures:
        for line in failures:
            print(line)
        sys.exit(1)

    print("STYLE OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
