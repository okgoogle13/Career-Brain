#!/usr/bin/env python3
"""
Batch 4 Docs-API QA check for Career Brain Golden Master templates.

Checks the following for each unique Google Doc ID:
- Font: Calibri 11pt body; Calibri 14pt for Title style
- Line spacing: 1.15
- Paragraph spacing: 6pt after paragraph
- Margins: 2cm all sides
- Heading styles: Native Heading 1/Heading 2 -- NOT bolded Normal text
- Inline objects: None
- Text boxes: None (positioned objects)
- Background: White canvas; no shaded sections
"""

from __future__ import annotations
import json
import os
import sys
from pathlib import Path
from typing import Any

BASE = Path(__file__).parent.parent  # project root

DOCS_TO_CHECK = {
    "ksc_standard": "10PT1cgIPnrQd63tp0CRqCMnq0Z1QZEYkXv0BdNWzh2I",
    "resume_chronological_and_hybrid": "1Bc8BMBgmT3YYpdjfdxSfTidUVvrpUGukRlbWIJN-Rb8",
    "cover_letter_government_nfp_private": "18UOiEOQkK3M4vfVYwgYlf0tYGZePbvG2fxt-_19rDM4",
}

# Expected values
EXPECTED_BODY_FONT = "Calibri"
EXPECTED_BODY_SIZE_PT = 11.0
EXPECTED_TITLE_FONT = "Calibri"
EXPECTED_TITLE_SIZE_PT = 14.0
EXPECTED_LINE_SPACING = 1.15  # as a ratio (115 in API units)
EXPECTED_SPACE_BELOW_PT = 6.0
EXPECTED_MARGIN_CM = 2.0
EXPECTED_MARGIN_PT = EXPECTED_MARGIN_CM * 28.3465  # 56.693pt
MARGIN_TOLERANCE_PT = 2.0  # allow ±2pt


def build_docs_service():
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    scopes = [
        "https://www.googleapis.com/auth/documents",
        "https://www.googleapis.com/auth/drive",
    ]
    token_path = Path(os.getenv("GOOGLE_OAUTH_TOKEN", str(BASE / "token.json")))
    client_secrets_path = Path(os.getenv("GOOGLE_OAUTH_CLIENT_SECRETS", str(BASE / "credentials.json")))

    credentials = None
    if token_path.exists():
        credentials = Credentials.from_authorized_user_file(str(token_path), scopes)
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        token_path.write_text(credentials.to_json(), encoding="utf-8")
    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets_path), scopes)
        credentials = flow.run_local_server(port=0)
        token_path.write_text(credentials.to_json(), encoding="utf-8")

    return build("docs", "v1", credentials=credentials)


def pts_from_magnitude(mag: dict | None) -> float | None:
    if not mag:
        return None
    unit = mag.get("unit", "PT")
    val = mag.get("magnitude", 0.0)
    if unit == "PT":
        return float(val)
    if unit == "INCH":
        return float(val) * 72.0
    if unit == "CM":
        return float(val) * 28.3465
    if unit == "MM":
        return float(val) * 2.83465
    return float(val)


def check_margin(label: str, mag: dict | None) -> tuple[str, str]:
    val = pts_from_magnitude(mag)
    if val is None:
        return label, f"FAIL — margin not set (None)"
    diff = abs(val - EXPECTED_MARGIN_PT)
    val_cm = val / 28.3465
    if diff <= MARGIN_TOLERANCE_PT:
        return label, f"PASS ({val_cm:.2f} cm / {val:.1f}pt)"
    return label, f"FAIL — {val_cm:.2f} cm ({val:.1f}pt), expected ~{EXPECTED_MARGIN_CM} cm ({EXPECTED_MARGIN_PT:.1f}pt)"


def check_named_styles(named_styles_list: list) -> list[tuple[str, str]]:
    results = []
    style_map: dict[str, dict] = {}
    for ns in named_styles_list:
        style_map[ns.get("namedStyleType", "")] = ns

    # Body font / size
    normal = style_map.get("NORMAL_TEXT", {})
    normal_props = normal.get("textStyle", {})
    body_font = normal_props.get("weightedFontFamily", {}).get("fontFamily", "")
    body_size_mag = normal_props.get("fontSize", {})
    body_size = pts_from_magnitude(body_size_mag)
    if body_font == EXPECTED_BODY_FONT and body_size is not None and abs(body_size - EXPECTED_BODY_SIZE_PT) < 0.5:
        results.append(("Body font (NORMAL_TEXT)", f"PASS ({body_font} {body_size:.1f}pt)"))
    else:
        results.append(("Body font (NORMAL_TEXT)", f"FAIL — font='{body_font}' size={body_size}pt (expected {EXPECTED_BODY_FONT} {EXPECTED_BODY_SIZE_PT}pt)"))

    # Line spacing on NORMAL_TEXT paragraph style
    normal_para = normal.get("paragraphStyle", {})
    line_spacing_raw = normal_para.get("lineSpacing")  # API reports as percentage value (e.g. 115 = 1.15)
    if line_spacing_raw is not None:
        line_spacing = float(line_spacing_raw) / 100.0
        if abs(line_spacing - EXPECTED_LINE_SPACING) < 0.01:
            results.append(("Line spacing (NORMAL_TEXT)", f"PASS ({line_spacing:.2f})"))
        else:
            results.append(("Line spacing (NORMAL_TEXT)", f"FAIL — {line_spacing:.2f} (expected {EXPECTED_LINE_SPACING})"))
    else:
        results.append(("Line spacing (NORMAL_TEXT)", "FAIL — lineSpacing not set on NORMAL_TEXT named style"))

    # Paragraph spacing after (spaceBelow) on NORMAL_TEXT
    space_below_mag = normal_para.get("spaceBelow")
    space_below = pts_from_magnitude(space_below_mag)
    if space_below is not None and abs(space_below - EXPECTED_SPACE_BELOW_PT) < 0.5:
        results.append(("Paragraph spacing after (NORMAL_TEXT)", f"PASS ({space_below:.1f}pt)"))
    else:
        results.append(("Paragraph spacing after (NORMAL_TEXT)", f"FAIL — {space_below}pt (expected {EXPECTED_SPACE_BELOW_PT}pt)"))

    # Title style
    title = style_map.get("TITLE", {})
    title_props = title.get("textStyle", {})
    title_font = title_props.get("weightedFontFamily", {}).get("fontFamily", "")
    title_size_mag = title_props.get("fontSize", {})
    title_size = pts_from_magnitude(title_size_mag)
    if title_font == EXPECTED_TITLE_FONT and title_size is not None and abs(title_size - EXPECTED_TITLE_SIZE_PT) < 0.5:
        results.append(("Title font/size", f"PASS ({title_font} {title_size:.1f}pt)"))
    else:
        results.append(("Title font/size", f"FAIL — font='{title_font}' size={title_size}pt (expected {EXPECTED_TITLE_FONT} {EXPECTED_TITLE_SIZE_PT}pt)"))

    # HEADING_1 style type check
    h1 = style_map.get("HEADING_1", {})
    h1_para = h1.get("paragraphStyle", {})
    h1_text = h1.get("textStyle", {})
    # Heading should not have bold=True in the named style as bolded normal text
    h1_named_style_type = "HEADING_1" if "HEADING_1" in style_map else None
    if h1_named_style_type:
        results.append(("Heading 1 style registered", "PASS — HEADING_1 named style exists"))
    else:
        results.append(("Heading 1 style registered", "FAIL — HEADING_1 not found in namedStyles"))

    h2 = style_map.get("HEADING_2", {})
    if "HEADING_2" in style_map:
        results.append(("Heading 2 style registered", "PASS — HEADING_2 named style exists"))
    else:
        results.append(("Heading 2 style registered", "FAIL — HEADING_2 not found in namedStyles"))

    return results


def check_body_for_heading_abuse(body_content: list) -> list[tuple[str, str]]:
    """Check paragraphs styled as NORMAL_TEXT with manual bold to fake headings."""
    abused_headings = []
    for element in body_content:
        para = element.get("paragraph")
        if not para:
            continue
        para_style = para.get("paragraphStyle", {})
        named_style = para_style.get("namedStyleType", "")
        if named_style not in ("NORMAL_TEXT", ""):
            continue  # real heading style — fine
        # Check if all text runs in this paragraph are bold
        elements = para.get("elements", [])
        if not elements:
            continue
        all_bold = True
        has_text = False
        for el in elements:
            tr = el.get("textRun", {})
            content = tr.get("content", "")
            if content.strip():
                has_text = True
                ts = tr.get("textStyle", {})
                if not ts.get("bold", False):
                    all_bold = False
                    break
        if has_text and all_bold:
            # Check text length — short all-bold lines are suspicious heading fakes
            text = "".join(
                el.get("textRun", {}).get("content", "") for el in elements
            ).strip()
            if text and len(text) < 60:
                abused_headings.append(text[:50])

    if abused_headings:
        return [("Heading style abuse (bolded NORMAL_TEXT)", f"FAIL — {len(abused_headings)} bolded NORMAL_TEXT paragraphs that may be faked headings: {abused_headings[:5]}")]
    return [("Heading style abuse (bolded NORMAL_TEXT)", "PASS — no suspicious bolded NORMAL_TEXT acting as headings")]


def check_inline_objects(doc: dict) -> tuple[str, str]:
    inline = doc.get("inlineObjects", {})
    if inline:
        return ("Inline objects", f"FAIL — {len(inline)} inline object(s) found (IDs: {list(inline.keys())[:3]})")
    return ("Inline objects", "PASS — none")


def check_text_boxes(doc: dict) -> tuple[str, str]:
    positioned = doc.get("positionedObjects", {})
    if positioned:
        return ("Text boxes / positioned objects", f"FAIL — {len(positioned)} positioned object(s) found")
    return ("Text boxes / positioned objects", "PASS — none")


def check_background(doc: dict) -> tuple[str, str]:
    doc_style = doc.get("documentStyle", {})
    bg = doc_style.get("background", {})
    color = bg.get("color", {})
    rgb = color.get("rgbColor", {})
    r = rgb.get("red", 1.0)
    g = rgb.get("green", 1.0)
    b = rgb.get("blue", 1.0)
    # White is 1.0, 1.0, 1.0 or absent (defaults to white)
    if abs(r - 1.0) < 0.01 and abs(g - 1.0) < 0.01 and abs(b - 1.0) < 0.01:
        return ("Background color", "PASS — white canvas")
    return ("Background color", f"FAIL — background RGB ({r:.2f}, {g:.2f}, {b:.2f})")


def check_shaded_sections(body_content: list) -> tuple[str, str]:
    """Check paragraph background shading."""
    shaded = []
    for element in body_content:
        para = element.get("paragraph")
        if not para:
            continue
        para_style = para.get("paragraphStyle", {})
        shading = para_style.get("shading", {})
        bg_color = shading.get("backgroundColor", {})
        color = bg_color.get("color", {})
        rgb = color.get("rgbColor", {})
        if rgb:
            r = rgb.get("red", 1.0)
            g = rgb.get("green", 1.0)
            b = rgb.get("blue", 1.0)
            if not (abs(r - 1.0) < 0.01 and abs(g - 1.0) < 0.01 and abs(b - 1.0) < 0.01):
                text_preview = "".join(
                    el.get("textRun", {}).get("content", "") for el in para.get("elements", [])
                ).strip()[:40]
                shaded.append(text_preview)
    if shaded:
        return ("Shaded sections", f"FAIL — {len(shaded)} paragraph(s) with non-white background: {shaded[:3]}")
    return ("Shaded sections", "PASS — no shaded paragraphs")


def check_document(docs_service, label: str, doc_id: str) -> None:
    print(f"\n{'='*70}")
    print(f"TEMPLATE: {label}")
    print(f"Doc ID:   {doc_id}")
    print(f"{'='*70}")

    try:
        doc = docs_service.documents().get(documentId=doc_id).execute()
    except Exception as exc:
        print(f"FAIL — Could not fetch document: {exc}")
        return

    doc_style = doc.get("documentStyle", {})
    body_content = doc.get("body", {}).get("content", [])
    named_styles = doc.get("namedStyles", {}).get("styles", [])

    # Margins
    for margin_label, key in [
        ("Margin top", "marginTop"),
        ("Margin bottom", "marginBottom"),
        ("Margin left", "marginLeft"),
        ("Margin right", "marginRight"),
    ]:
        lbl, result = check_margin(margin_label, doc_style.get(key))
        print(f"  {lbl}: {result}")

    # Named styles (font, line spacing, para spacing, title, heading registration)
    for lbl, result in check_named_styles(named_styles):
        print(f"  {lbl}: {result}")

    # Heading style abuse check
    for lbl, result in check_body_for_heading_abuse(body_content):
        print(f"  {lbl}: {result}")

    # Inline objects
    lbl, result = check_inline_objects(doc)
    print(f"  {lbl}: {result}")

    # Text boxes / positioned objects
    lbl, result = check_text_boxes(doc)
    print(f"  {lbl}: {result}")

    # Background
    lbl, result = check_background(doc)
    print(f"  {lbl}: {result}")

    # Shaded sections
    lbl, result = check_shaded_sections(body_content)
    print(f"  {lbl}: {result}")


def main():
    print("Building Google Docs service...")
    try:
        docs_service = build_docs_service()
    except Exception as exc:
        print(f"ERROR: Could not build Docs service: {exc}", file=sys.stderr)
        sys.exit(1)

    for label, doc_id in DOCS_TO_CHECK.items():
        check_document(docs_service, label, doc_id)

    print(f"\n{'='*70}")
    print("Docs-API QA check complete.")


if __name__ == "__main__":
    main()
