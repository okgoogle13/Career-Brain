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


# Paragraph roles that use heading_font_family[0]; all other roles use base_font.
HEADING_ROLES = ("name", "headline", "h1", "h2")


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
            add(f"{{{{KSC_CRITERION_{c}_TEXT}}}}", "HEADING_1", bold=True, role="h2")
            add(f"{{{{KSC_{c}_CONTEXT}}}}", "NORMAL_TEXT", role="body")
            add(f"{{{{KSC_{c}_ACTION}}}}", "NORMAL_TEXT", role="body")
            add(f"{{{{KSC_{c}_RESULT}}}}", "NORMAL_TEXT", role="body")
            add(f"- {{{{KSC_{c}_SUPPORT_BULLET_1}}}}", "NORMAL_TEXT", role="bullet")
            add(f"- {{{{KSC_{c}_SUPPORT_BULLET_2}}}}", "NORMAL_TEXT", role="bullet")

    return rows


def _vc(theme: dict, block_id: str) -> dict:
    """visualConfig of a block, or {} when the block or its visualConfig is absent."""
    block = next((b for b in theme.get("blocks", []) if b["block_id"] == block_id), None)
    return (block or {}).get("visualConfig") or {}


def _below(vc: dict, default: float) -> float:
    return vc.get("margin_bottom_pt", vc.get("padding_bottom_pt", default))


def role_style(theme: dict, role: str) -> dict:
    """Resolved paragraph + text style for one paragraph role.

    Single source of the role -> style map: the builder emits it and the audit,
    verifier and fingerprint tools read it, so they cannot drift apart.
    Keys: font, weight, font_size, color, line_spacing (percent), space_above, space_below.
    """
    doc_type = theme.get("doc_type", "resume")
    typo = theme.get("typography", {})
    base_font = typo.get("base_font", "Calibri")
    heading_font = (theme.get("heading_font_family") or [base_font])[0]
    body_size = typo.get("base_size_pt", 11.0)
    body_color = theme.get("palette", {}).get("body_text", "#1A1A1A")
    body_ls = typo.get("line_spacing", 1.15)
    ev = _vc(theme, "experience_section")
    kv = _vc(theme, "criteria_responses")
    above = 0.0

    if role == "name":
        vc = _vc(theme, "name_header")
        size, color, ls, below = vc.get("font_size_pt", 24), vc.get("font_color", "#000000"), vc.get("line_spacing", body_ls), _below(vc, 2.0)
    elif role == "contact":
        vc = _vc(theme, "contact_info")
        size, color, ls, below = vc.get("font_size_pt", 11), vc.get("font_color", "#444444"), vc.get("line_spacing", body_ls), _below(vc, 2.0)
    elif role == "headline":
        vc = _vc(theme, "role_headline")
        size, color, ls, below = vc.get("font_size_pt", 12), vc.get("font_color", "#1A1A1A"), vc.get("line_spacing", body_ls), _below(vc, 8.0)
    elif role == "employer":
        size, color, ls, below = body_size, body_color, body_ls, 2.0
    elif role == "h1":
        vc = _vc(theme, "summary_section").get("heading", {})
        size, color, ls, below = vc.get("font_size_pt", 14), vc.get("font_color", "#000000"), vc.get("line_spacing", body_ls), vc.get("margin_bottom_pt", 6.0)
    elif role == "h2":
        vc = kv.get("criterion_text", {}) if doc_type == "ksc" else ev.get("role_title", {})
        size, color, ls = vc.get("font_size_pt", 12), vc.get("font_color", "#000000"), vc.get("line_spacing", body_ls)
        above, below = vc.get("margin_top_pt", 0.0), vc.get("margin_bottom_pt", 2.0)
    elif role == "role_meta":
        vc = ev.get("role_meta", {})
        size, color, ls, below = vc.get("font_size_pt", 11), vc.get("font_color", "#444444"), vc.get("line_spacing", body_ls), vc.get("margin_bottom_pt", 4.0)
    elif role == "bullet":
        vc = kv.get("bullet", {}) if doc_type == "ksc" else ev.get("bullet", {})
        size, color, ls, below = vc.get("font_size_pt", body_size), vc.get("font_color", body_color), vc.get("line_spacing", 1.2), vc.get("margin_bottom_pt", 2.0)
    elif role == "skills_body":
        vc = _vc(theme, "skills_section").get("item", {})
        size, color, ls, below = vc.get("font_size_pt", body_size), vc.get("font_color", body_color), vc.get("line_spacing", body_ls), 6.0
    else:  # body
        vc = kv.get("body", {}) if doc_type == "ksc" else {}
        size, color = vc.get("font_size_pt", body_size), vc.get("font_color", body_color)
        ls = vc.get("line_spacing", body_ls)
        below = vc.get("paragraph_spacing_after_pt", typo.get("spacing_after_pt", 6.0))

    heading = role in HEADING_ROLES
    return {
        "font": heading_font if heading else base_font,
        "weight": typo.get("section_heading_weight") if heading else None,
        "font_size": size,
        "color": color,
        "line_spacing": round(ls * 100),
        "space_above": above,
        "space_below": below,
    }


def build_requests(theme: dict, paragraphs: list, doc_id: str) -> list[dict]:
    """Build all batchUpdate requests for styling after content is inserted."""
    page = theme.get("page", {
        "margin_top_cm": 2.0, "margin_bottom_cm": 2.0,
        "margin_left_cm": 2.0, "margin_right_cm": 2.0,
        "background_color": "#FFFFFF"
    })
    ev = _vc(theme, "experience_section")
    sv = _vc(theme, "skills_section")
    nv = _vc(theme, "name_header")
    h1_vc = _vc(theme, "summary_section").get("heading", {})
    bullet_vc = _vc(theme, "criteria_responses").get("bullet", {}) if theme.get("doc_type") == "ksc" else ev.get("bullet", {})

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

        st = role_style(theme, role)

        # Paragraph style request
        para_style = {
            "namedStyleType": named_style,
            "lineSpacing": st["line_spacing"],
            "spaceBelow": pt(st["space_below"]),
            "spaceAbove": pt(st["space_above"]),
        }

        if role == "bullet":
            para_style["indentStart"] = pt(bullet_vc.get("indent_pt", 14))
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
                    "fontSize": pt(st["font_size"]),
                    "foregroundColor": {"color": {"rgbColor": hex_to_rgb(st["color"])}},
                    "weightedFontFamily": {
                        "fontFamily": st["font"],
                        **({"weight": st["weight"]} if st["weight"] else {}),
                    },
                },
                "fields": "bold,italic,fontSize,foregroundColor,weightedFontFamily",
            }
        })

    return requests


def main():
    positional = []
    dry_run = False
    update_doc_id = None
    
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--dry-run":
            dry_run = True
        elif arg == "--update":
            if i + 1 < len(args):
                update_doc_id = args[i+1]
                i += 1
            else:
                print("Error: --update requires a doc_id", file=sys.stderr)
                sys.exit(1)
        elif arg.startswith("-"):
            print(f"Error: unrecognised flag: {arg}", file=sys.stderr)
            print("Usage: python3 build_golden_master.py <theme_json_path> [--dry-run] [--update <doc_id>]", file=sys.stderr)
            sys.exit(1)
        else:
            positional.append(arg)
        i += 1

    if len(positional) != 1:
        print("Usage: python3 build_golden_master.py <theme_json_path> [--dry-run] [--update <doc_id>]", file=sys.stderr)
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

    if update_doc_id:
        doc_id = update_doc_id
        print(f"Updating Google Doc ID: {doc_id} ...", file=sys.stderr)
        doc = docs_service.documents().get(documentId=doc_id).execute()
        content = doc.get("body", {}).get("content", [])
        if content:
            end_index = content[-1].get("endIndex", 2)
            if end_index > 2:
                print("  Clearing existing content ...", file=sys.stderr)
                docs_service.documents().batchUpdate(
                    documentId=doc_id,
                    body={"requests": [{"deleteContentRange": {"range": {"startIndex": 1, "endIndex": end_index - 1}}}]},
                ).execute()
    else:
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
