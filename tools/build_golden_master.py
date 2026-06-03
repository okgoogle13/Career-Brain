#!/usr/bin/env python3
"""
Build a styled Google Doc Golden Master from a theme JSON spec.

Usage:
    python3 build_golden_master.py templates/resume_contemporary_professional_v1.json

Prints the created Google Doc ID on success.
"""

import json
import sys
from pathlib import Path


def hex_to_rgb(hex_color: str) -> dict:
    h = hex_color.lstrip("#")
    return {
        "red":   int(h[0:2], 16) / 255,
        "green": int(h[2:4], 16) / 255,
        "blue":  int(h[4:6], 16) / 255,
    }


def cm_to_pt(cm: float) -> float:
    return cm * 28.3465


def cm_to_magnitude(cm: float) -> dict:
    return {"magnitude": cm_to_pt(cm), "unit": "PT"}


def pt(v: float) -> dict:
    return {"magnitude": v, "unit": "PT"}


def build_paragraphs(theme: dict) -> list[tuple[str, str, bool, bool, str | None]]:
    doc_type = theme.get("doc_type", "resume")
    rows: list[tuple[str, str, bool, bool, str]] = []

    def add(text, named_style, bold=False, italic=False, role="body"):
        rows.append((text, named_style, bold, italic, role))

    if doc_type == "resume":
        # ── header block ──────────────────────────────────────────────────────────
        add("{{CONTACT_NAME}}", "TITLE", bold=True, role="name")
        add("{{CONTACT_PHONE}}", "NORMAL_TEXT", role="contact")
        add("{{CONTACT_EMAIL}}", "NORMAL_TEXT", role="contact")
        add("{{CONTACT_LOCATION}}", "NORMAL_TEXT", role="contact")
        add("{{TARGET_ROLE}}", "NORMAL_TEXT", bold=True, role="headline")

        # ── summary ───────────────────────────────────────────────────────────────
        summary_block = next((b for b in theme.get("blocks", []) if b["block_id"] == "summary_section"), None)
        if summary_block:
            add(summary_block.get("heading", "SUMMARY"), "HEADING_1", bold=True, role="h1")
            add("{{PROFESSIONAL_SUMMARY}}", "NORMAL_TEXT", role="body")

        # ── skills ────────────────────────────────────────────────────────────────
        skills_block = next((b for b in theme.get("blocks", []) if b["block_id"] == "skills_section"), None)
        if skills_block:
            add(skills_block.get("heading", "SKILLS"), "HEADING_1", bold=True, role="h1")
            skills_tokens = ", ".join(skills_block.get("tokens", []))
            add(skills_tokens, "NORMAL_TEXT", role="skills_body")

        # ── experience ────────────────────────────────────────────────────────────
        exp_block = next((b for b in theme.get("blocks", []) if b["block_id"] == "experience_section"), None)
        if exp_block:
            add(exp_block.get("heading", "EXPERIENCE"), "HEADING_1", bold=True, role="h1")
            for role_entry in exp_block.get("roles", []):
                t = role_entry.get("tokens", {})
                add(t.get("title", ""), "HEADING_2", bold=True, role="h2")
                add(f"{t.get('org', '')}   {t.get('dates', '')}", "NORMAL_TEXT", italic=True, role="role_meta")
                for bullet in t.get("bullets", []):
                    add(f"- {bullet}", "NORMAL_TEXT", role="bullet")

        # ── education ─────────────────────────────────────────────────────────────
        edu_block = next((b for b in theme.get("blocks", []) if b["block_id"] == "education_section"), None)
        if edu_block:
            add(edu_block.get("heading", "EDUCATION"), "HEADING_1", bold=True, role="h1")
            for tok in edu_block.get("tokens", []):
                add(tok, "NORMAL_TEXT", role="body")

        # ── certifications ────────────────────────────────────────────────────────
        cert_block = next((b for b in theme.get("blocks", []) if b["block_id"] == "certifications_section"), None)
        if cert_block:
            add(cert_block.get("heading", "CERTIFICATIONS"), "HEADING_1", bold=True, role="h1")
            for tok in cert_block.get("tokens", []):
                add(tok, "NORMAL_TEXT", role="body")

    elif doc_type == "cover_letter":
        add("{{CONTACT_NAME}}", "TITLE", bold=True, role="name")
        add("{{CONTACT_PHONE}}", "NORMAL_TEXT", role="contact")
        add("{{CONTACT_EMAIL}}", "NORMAL_TEXT", role="contact")
        add("{{CONTACT_LOCATION}}", "NORMAL_TEXT", role="contact")
        
        add("{{EMPLOYER_CONTACT_NAME}}", "NORMAL_TEXT", role="employer")
        add("{{EMPLOYER_ORG}}", "NORMAL_TEXT", role="employer")
        add("{{EMPLOYER_ADDRESS}}", "NORMAL_TEXT", role="employer")
        
        add("{{CURRENT_DATE}}", "NORMAL_TEXT", role="body")
        add("{{SALUTATION}}", "NORMAL_TEXT", role="body")
        
        add("{{HOOK_PARAGRAPH}}", "NORMAL_TEXT", role="body")
        add("{{BRIDGE_PARAGRAPH}}", "NORMAL_TEXT", role="body")
        add("{{EVIDENCE_PARAGRAPH_1}}", "NORMAL_TEXT", role="body")
        add("{{EVIDENCE_PARAGRAPH_2}}", "NORMAL_TEXT", role="body")
        
        add("{{CLOSING_PARAGRAPH}}", "NORMAL_TEXT", role="body")

    elif doc_type == "ksc":
        add("{{CONTACT_NAME}}", "TITLE", bold=True, role="name")
        add("{{CONTACT_PHONE}}", "NORMAL_TEXT", role="contact")
        add("{{CONTACT_EMAIL}}", "NORMAL_TEXT", role="contact")
        add("{{CONTACT_LOCATION}}", "NORMAL_TEXT", role="contact")
        
        add("{{TARGET_ROLE}}", "NORMAL_TEXT", bold=True, role="headline")
        add("{{EMPLOYER_ORG}}", "NORMAL_TEXT", role="employer")
        
        criteria_block = next(
            (b for b in theme.get("blocks", []) if b["block_id"] == "criteria_responses"), {}
        )
        max_criteria = criteria_block.get("max_criteria", 3)
        for c in range(1, max_criteria + 1):
            add(f"{{{{KSC_CRITERION_{c}_TEXT}}}}", "HEADING_1", bold=True, role="h1")
            add(f"{{{{KSC_{c}_CONTEXT}}}}", "NORMAL_TEXT", role="body")
            add(f"{{{{KSC_{c}_ACTION}}}}", "NORMAL_TEXT", role="body")
            add(f"{{{{KSC_{c}_RESULT}}}}", "NORMAL_TEXT", role="body")
            add(f"- {{{{KSC_{c}_SUPPORT_BULLET_1}}}}", "NORMAL_TEXT", role="bullet")
            add(f"- {{{{KSC_{c}_SUPPORT_BULLET_2}}}}", "NORMAL_TEXT", role="bullet")

    return rows


def build_requests(theme: dict, paragraphs: list, doc_id: str) -> list[dict]:
    """Build all batchUpdate requests for styling after content is inserted."""
    doc_type = theme.get("doc_type", "resume")
    font = theme["typography"]["base_font"]
    page = theme.get("page", {
        "margin_top_cm": 2.0, "margin_bottom_cm": 2.0, 
        "margin_left_cm": 2.0, "margin_right_cm": 2.0, 
        "background_color": "#FFFFFF"
    })

    def get_block(block_id):
        return next((b for b in theme.get("blocks", []) if b["block_id"] == block_id), None)

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
    typo = theme.get("typography", {})
    body_size = typo.get("base_size_pt", 11.0)
    body_color = theme.get("palette", {}).get("body_text", "#1A1A1A")

    requests = []

    # ── 1. Document style (margins + page background) ─────────────────────────
    doc_style = {
        "marginTop":    cm_to_magnitude(page["margin_top_cm"]),
        "marginBottom": cm_to_magnitude(page["margin_bottom_cm"]),
        "marginLeft":   cm_to_magnitude(page["margin_left_cm"]),
        "marginRight":  cm_to_magnitude(page["margin_right_cm"]),
    }
    if page.get("background_color") and page["background_color"] != "#FFFFFF":
        doc_style["background"] = {"color": {"color": {"rgbColor": hex_to_rgb(page["background_color"])}}}

    requests.append({
        "updateDocumentStyle": {
            "documentStyle": doc_style,
            "fields": "marginTop,marginBottom,marginLeft,marginRight" + (
                ",background" if "background" in doc_style else ""
            ),
        }
    })

    # ── 2. Per-paragraph styling ───────────────────────────────────────────────
    index = 1
    for i, (text, named_style, bold, italic, role) in enumerate(paragraphs):
        start = index
        end = index + len(text)
        index = end + 1

        if role == "name":
            font_size = nv.get("font_size_pt", 24)
            color = nv.get("font_color", "#000000")
            line_spacing = 115
            space_below = nv.get("margin_bottom_pt", 2.0)
        elif role == "contact":
            font_size = cv.get("font_size_pt", 11)
            color = cv.get("font_color", "#444444")
            line_spacing = round(cv.get("line_spacing", 1.15) * 100)
            space_below = cv.get("margin_bottom_pt", 2.0)
        elif role == "headline":
            font_size = hv.get("font_size_pt", 12)
            color = hv.get("font_color", "#1A1A1A")
            line_spacing = 115
            space_below = hv.get("margin_bottom_pt", 8.0)
        elif role == "employer":
            font_size = body_size
            color = body_color
            line_spacing = round(typo.get("line_spacing", 1.15) * 100)
            space_below = 2.0
        elif role == "h1":
            font_size = h1_vc.get("font_size_pt", 14)
            color = h1_vc.get("font_color", "#000000")
            line_spacing = 115
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
            line_spacing = 115
        elif role == "role_meta":
            rm = ev.get("role_meta", {})
            font_size = rm.get("font_size_pt", 11)
            color = rm.get("font_color", "#444444")
            line_spacing = 115
            space_below = rm.get("margin_bottom_pt", 4.0)
        elif role == "bullet":
            b_vc = ev.get("bullet", {})
            font_size = b_vc.get("font_size_pt", body_size)
            color = b_vc.get("font_color", body_color)
            line_spacing = round(b_vc.get("line_spacing", 1.2) * 100)
            space_below = b_vc.get("margin_bottom_pt", 2.0)
        elif role == "skills_body":
            item = sv.get("item", {})
            font_size = item.get("font_size_pt", body_size)
            color = item.get("font_color", body_color)
            line_spacing = 115
            space_below = 6.0
        else:  # body
            font_size = body_size
            color = body_color
            line_spacing = round(typo.get("line_spacing", 1.15) * 100)
            space_below = typo.get("spacing_after_pt", 6.0)

        # Paragraph style request
        para_style = {
            "namedStyleType": named_style,
            "lineSpacing": line_spacing,
            "spaceBelow": pt(space_below),
            "spaceAbove": pt(0),
        }

        if role == "bullet":
            para_style["indentStart"] = pt(ev.get("bullet", {}).get("indent_pt", 14))
            para_style["indentFirstLine"] = pt(0)

        para_fields = "namedStyleType,lineSpacing,spaceBelow,spaceAbove"

        if role == "skills_body" and sv.get("container", {}).get("background_color"):
            bg_hex = sv["container"]["background_color"]
            if bg_hex and bg_hex != "#FFFFFF":
                para_style["shading"] = {"backgroundColor": {"color": {"rgbColor": hex_to_rgb(bg_hex)}}}
                para_fields += ",shading"

        if role == "bullet":
            para_fields += ",indentStart,indentFirstLine"

        if role == "h1":
            border_bottom = h1_vc.get("border_bottom")
            border_left = h1_vc.get("border_left")
            if border_bottom:
                width_pt = border_bottom.get("width_pt", 1.0)
                para_style["borderBottom"] = {
                    "color": {"color": {"rgbColor": hex_to_rgb(border_bottom["color"])}},
                    "width": pt(width_pt),
                    "padding": pt(1),
                    "dashStyle": "SOLID",
                }
                para_fields += ",borderBottom"
            elif border_left:
                width_pt = border_left.get("width_pt", 2)
                para_style["borderLeft"] = {
                    "color": {"color": {"rgbColor": hex_to_rgb(border_left["color"])}},
                    "width": pt(width_pt),
                    "padding": pt(8),
                    "dashStyle": "SOLID",
                }
                para_style["indentStart"] = pt(8)
                para_fields += ",borderLeft,indentStart"

        if role == "name" and nv.get("border_bottom"):
            para_style["borderBottom"] = {
                "color": {"color": {"rgbColor": hex_to_rgb(nv["border_bottom"]["color"])}},
                "width": pt(nv["border_bottom"].get("width_pt", 0.5)),
                "padding": pt(1),
                "dashStyle": "SOLID",
            }
            para_fields += ",borderBottom"

        requests.append({
            "updateParagraphStyle": {
                "range": {"startIndex": start, "endIndex": end},
                "paragraphStyle": para_style,
                "fields": para_fields,
            }
        })

        # Text style request (Must come AFTER paragraph style to avoid being overwritten)
        requests.append({
            "updateTextStyle": {
                "range": {"startIndex": start, "endIndex": end},
                "textStyle": {
                    "bold": bold,
                    "italic": italic,
                    "fontSize": pt(font_size),
                    "foregroundColor": {"color": {"rgbColor": hex_to_rgb(color)}},
                    "weightedFontFamily": {"fontFamily": font},
                },
                "fields": "bold,italic,fontSize,foregroundColor,weightedFontFamily",
            }
        })

    return requests


def main():
    # positional theme path + optional --dry-run flag
    positional = [a for a in sys.argv[1:] if not a.startswith("-")]
    dry_run = "--dry-run" in sys.argv[1:]
    if len(positional) != 1:
        print("Usage: python3 build_golden_master.py <theme_json_path> [--dry-run]", file=sys.stderr)
        sys.exit(1)

    theme_path = Path(positional[0])
    if not theme_path.exists():
        print(f"Error: {theme_path} not found", file=sys.stderr)
        sys.exit(1)

    theme = json.loads(theme_path.read_text(encoding="utf-8"))
    template_name = theme.get("template_id", theme_path.stem)

    paragraphs = build_paragraphs(theme)
    full_text = "\n".join(text for text, *_ in paragraphs)
    insert_request = {"insertText": {"location": {"index": 1}, "text": full_text + "\n"}}

    if dry_run:
        # Offline payload dump — no Google API calls, no quota. Lets us validate
        # request ordering (paragraph style before text style) and payload shapes
        # before spending a live build. doc_id is unused by build_requests().
        style_requests = build_requests(theme, paragraphs, doc_id="DRY_RUN")
        print(json.dumps({
            "template_id": template_name,
            "doc_type": theme.get("doc_type", "resume"),
            "paragraph_count": len(paragraphs),
            "insert_request": insert_request,
            "style_requests": style_requests,
        }, indent=2))
        return

    from generate_document import build_google_services
    docs_service, drive_service = build_google_services()

    print(f"Creating Google Doc: {template_name} ...", file=sys.stderr)
    file_meta = drive_service.files().create(
        body={
            "name": f"[GOLDEN MASTER] {template_name}",
            "mimeType": "application/vnd.google-apps.document",
        },
        fields="id",
    ).execute()
    doc_id = file_meta["id"]
    print(f"  Created doc ID: {doc_id}", file=sys.stderr)

    print("  Inserting content ...", file=sys.stderr)
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": [insert_request]},
    ).execute()

    print("  Applying styles ...", file=sys.stderr)
    style_requests = build_requests(theme, paragraphs, doc_id)

    for chunk_start in range(0, len(style_requests), 499):
        chunk = style_requests[chunk_start: chunk_start + 499]
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": chunk},
        ).execute()

    print(f"\n{doc_id}")


if __name__ == "__main__":
    main()
