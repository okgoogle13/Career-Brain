#!/usr/bin/env python3
"""
create_golden_master.py

Automates the creation of Golden Master Google Docs by parsing a template spec
(e.g., ksc_template_spec.md), creating a Google Doc via the Docs API, applying
the requested formatting (from the STRUCTURE section), and updating doc_templates.json.

Usage:
  python3 create_golden_master.py ksc_template_spec.md
"""

import argparse
import json
import logging
import re
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger("create_golden_master")

BASE = Path(__file__).parent.parent  # project root
DOC_TEMPLATES_JSON = BASE / "config" / "doc_templates.json"


def parse_spec(spec_path: Path):
    if not spec_path.exists():
        raise FileNotFoundError(f"Spec file not found: {spec_path}")

    text = spec_path.read_text(encoding="utf-8")
    meta = {}
    structure_lines = []

    # Parse META
    meta_match = re.search(r"## META\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if meta_match:
        for line in meta_match.group(1).strip().split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                meta[key.strip()] = val.strip()

    # Parse STRUCTURE
    struct_match = re.search(r"## STRUCTURE\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if struct_match:
        for line in struct_match.group(1).strip().split("\n"):
            line = line.strip()
            # Match formats like: "1. [Title] {{CONTACT_NAME}}" or "3. [Normal italic] {{EMPLOYER_ORG}}"
            m = re.match(r"^\d+\.\s*\[(.*?)\]\s*(.*)$", line)
            if m:
                style_raw = m.group(1)
                content = m.group(2)
                
                style = "NORMAL_TEXT"
                italic = False
                is_bullet = False
                is_numbered = False
                is_centered = False

                if "Title" in style_raw:
                    style = "TITLE"
                elif "Heading 1" in style_raw:
                    style = "HEADING_1"
                elif "Heading 2" in style_raw:
                    style = "HEADING_2"
                elif "Bullet" in style_raw:
                    is_bullet = True
                
                if "italic" in style_raw.lower():
                    italic = True
                if "center" in style_raw.lower():
                    is_centered = True
                if "numbered" in style_raw.lower():
                    is_numbered = True

                structure_lines.append({
                    "style": style,
                    "italic": italic,
                    "is_bullet": is_bullet,
                    "is_numbered": is_numbered,
                    "is_centered": is_centered,
                    "text": content
                })

    return meta, structure_lines


def generate_golden_master(spec_path: Path):
    log.info(f"Parsing spec: {spec_path}")
    meta, structure = parse_spec(spec_path)
    
    template_type = meta.get("TEMPLATE_TYPE", "unknown")
    variant = meta.get("VARIANT", "standard")
    doc_title = f"Golden Master - {template_type.upper()} - {variant.title()}"

    log.info("Authenticating with Google API...")
    from generate_document import build_google_services
    docs_service, drive_service = build_google_services()

    log.info(f"Creating Google Doc: '{doc_title}'")
    doc = docs_service.documents().create(body={"title": doc_title}).execute()
    doc_id = doc.get("documentId")
    log.info(f"Doc created. ID: {doc_id}")
    doc_link = f"https://docs.google.com/document/d/{doc_id}/edit"

    # We build the text content by joining all blocks with newlines.
    # Docs API inserts text backwards to keep indices stable, but we can just insert a single
    # block of text at index 1 and then apply paragraph styles.
    
    full_text = "\n".join(item["text"] for item in structure) + "\n"

    requests = []

    # 0. Set Margins (2 cm = 56.69 points)
    requests.append({
        "updateDocumentStyle": {
            "documentStyle": {
                "marginTop": {"magnitude": 56.69, "unit": "PT"},
                "marginBottom": {"magnitude": 56.69, "unit": "PT"},
                "marginLeft": {"magnitude": 56.69, "unit": "PT"},
                "marginRight": {"magnitude": 56.69, "unit": "PT"}
            },
            "fields": "marginTop,marginBottom,marginLeft,marginRight"
        }
    })

    # 1. Insert all text at index 1
    requests.append({
        "insertText": {
            "location": {"index": 1},
            "text": full_text
        }
    })

    # 2. Update default font to Calibri
    requests.append({
        "updateTextStyle": {
            "range": {
                "startIndex": 1,
                "endIndex": 1 + len(full_text)
            },
            "textStyle": {
                "weightedFontFamily": {
                    "fontFamily": "Calibri"
                },
                "fontSize": {
                    "magnitude": 11,
                    "unit": "PT"
                }
            },
            "fields": "weightedFontFamily,fontSize"
        }
    })

    # 3. Apply styles block by block
    current_index = 1
    for item in structure:
        text_len = len(item["text"]) + 1 # +1 for the newline
        end_index = current_index + text_len

        # Paragraph style
        para_style = {
            "lineSpacing": 115.0,
            "spaceBelow": {
                "magnitude": 6.0,
                "unit": "PT"
            }
        }
        fields = ["lineSpacing", "spaceBelow"]
        if item["style"] != "NORMAL_TEXT":
            para_style["namedStyleType"] = item["style"]
            fields.append("namedStyleType")
        if item["is_centered"]:
            para_style["alignment"] = "CENTER"
            fields.append("alignment")
        
        requests.append({
            "updateParagraphStyle": {
                "range": {
                    "startIndex": current_index,
                    "endIndex": end_index
                },
                "paragraphStyle": para_style,
                "fields": ",".join(fields)
            }
        })

        # Bold and resize headings/title specifically
        if item["style"] in ("TITLE", "HEADING_1", "HEADING_2"):
            requests.append({
                "updateTextStyle": {
                    "range": {
                        "startIndex": current_index,
                        "endIndex": end_index - 1
                    },
                    "textStyle": {
                        "fontSize": {
                            "magnitude": 14,
                            "unit": "PT"
                        },
                        "bold": True
                    },
                    "fields": "fontSize,bold"
                }
            })
        
        # Italic
        if item["italic"]:
            requests.append({
                "updateTextStyle": {
                    "range": {
                        "startIndex": current_index,
                        "endIndex": end_index - 1 # don't italicize newline
                    },
                    "textStyle": {
                        "italic": True
                    },
                    "fields": "italic"
                }
            })

        # Bullet
        if item["is_bullet"]:
            requests.append({
                "createParagraphBullets": {
                    "range": {
                        "startIndex": current_index,
                        "endIndex": end_index
                    },
                    "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"
                }
            })

        # Numbered List
        if item["is_numbered"]:
            requests.append({
                "createParagraphBullets": {
                    "range": {
                        "startIndex": current_index,
                        "endIndex": end_index
                    },
                    "bulletPreset": "NUMBERED_DECIMAL_ALPHA_ROMAN"
                }
            })

        current_index = end_index

    log.info("Executing batchUpdate for text insertion and styling...")
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": requests}
    ).execute()

    log.info(f"Golden Master created successfully: {doc_link}")

    # Register in doc_templates.json
    if DOC_TEMPLATES_JSON.exists():
        log.info(f"Updating {DOC_TEMPLATES_JSON.name}...")
        templates = json.loads(DOC_TEMPLATES_JSON.read_text(encoding="utf-8"))
        
        # Determine the key path. For KSC, it's typically templates["ksc"]["template_doc_id"]
        # or templates["ksc"]["variants"]["variant_name"]["template_doc_id"] if using variants.
        # Based on current `doc_templates.json` and ksc_template_spec.md, it's just "ksc".
        
        if template_type not in templates:
            templates[template_type] = {}
            
        if isinstance(templates[template_type], dict):
            # If variants are used
            if "variants" in templates[template_type] and variant in templates[template_type]["variants"]:
                if isinstance(templates[template_type]["variants"][variant], dict):
                    templates[template_type]["variants"][variant]["template_doc_id"] = doc_id
                else:
                    templates[template_type]["variants"][variant] = doc_id
            else:
                templates[template_type]["template_doc_id"] = doc_id
        elif isinstance(templates[template_type], str):
             templates[template_type] = doc_id

        DOC_TEMPLATES_JSON.write_text(json.dumps(templates, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        log.info(f"Registered Doc ID {doc_id} for '{template_type}'.")
    else:
        log.warning(f"{DOC_TEMPLATES_JSON.name} not found. Skipped registration.")

    print(f"\nSUCCESS! Golden Master '{doc_title}' generated.")
    print(f"Link: {doc_link}")
    print(f"Registered in doc_templates.json: {doc_id}")

def main():
    parser = argparse.ArgumentParser(description="Create Golden Master Google Doc from spec.")
    parser.add_argument("spec_file", type=Path, help="Path to the template spec markdown file")
    args = parser.parse_args()

    try:
        generate_golden_master(args.spec_file)
    except Exception as e:
        log.error(f"Failed to create Golden Master: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
