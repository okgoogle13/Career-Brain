#!/usr/bin/env python3
"""
Automate compilation of v2.3 conceptual themes into v2.0 production templates.
Maps visual identity, palettes, typography, and page margins to blocks and visualConfig.
"""
import json
import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
SCHEMA_PATH = TEMPLATES_DIR / "schema_v2_0.json"

def get_theme_suffix(filename: str) -> str:
    # e.g. theme-01-graphite-ledger.json -> graphite_ledger
    # e.g. theme-21-terminal-signal.json -> terminal_signal
    name = Path(filename).stem
    # Remove prefix "theme-XX-"
    parts = name.split("-", 2)
    if len(parts) >= 3:
        return parts[2].replace("-", "_")
    return name.replace("-", "_")

def compile_one(theme_path: Path) -> dict:
    theme = json.loads(theme_path.read_text(encoding="utf-8"))
    suffix = get_theme_suffix(theme_path.name)
    
    # 1. Palette mapping
    base_colours = theme["palette"]["base_colours"]
    primary_color = base_colours[1] if len(base_colours) > 1 else base_colours[0]
    
    palette = {
        "primary_color": primary_color,
        "body_text": theme["body_text_color"],
        "muted_text": theme["muted_text_color"],
        "accent_color": theme["palette"]["complementary_accent"],
        "skills_tint": theme["skills_background_tint"],
        "surface_color": theme["palette"]["neutral_surface"],
        "white": "#FFFFFF"
    }

    # 2. Typography mapping
    typo = theme["typography"]
    base_font = typo["base_font"]
    base_size_pt = typo["base_size_pt"]
    
    # Normalise line spacing to standard range (round to 2 decimals)
    line_spacing = round(typo["line_spacing"], 2)
    
    typography = {
        "base_font": base_font,
        "base_size_pt": base_size_pt,
        "line_spacing": line_spacing,
        "spacing_after_pt": typo["spacing_after_pt"],
        "section_heading_tracking_pt": typo.get("section_heading_tracking_pt", 0.0),
        "section_heading_size_pt": typo.get("section_heading_size_pt", 11.0)
    }
    
    # Add optional heading weight to typography if specified
    if "section_heading_weight" in typo:
        typography["section_heading_weight"] = typo["section_heading_weight"]

    # 3. Page margins conversion (inches to cm)
    margins_in = theme["page"]["margins_in"]
    page = {
        "margin_top_cm": round(margins_in["top"] * 2.54, 2),
        "margin_bottom_cm": round(margins_in["bottom"] * 2.54, 2),
        "margin_left_cm": round(margins_in["left"] * 2.54, 2),
        "margin_right_cm": round(margins_in["right"] * 2.54, 2),
        "background_color": theme["palette"]["neutral_surface"]
    }

    # 4. Heading decorations (border_left vs border_bottom)
    heading_style = theme["section_heading_style"]
    decoration_desc = heading_style.get("decoration", "").lower()
    
    use_left_border = "border_left" in decoration_desc or "border-left" in decoration_desc or "citrus edge" in decoration_desc or "emerald transit" in decoration_desc
    
    heading_border = {}
    if use_left_border:
        heading_border = {
            "border_left": {
                "color": heading_style["accent_color"],
                "width_pt": 2,
                "style": "solid"
            },
            "padding_left_pt": 8
        }
    else:
        # Default to bottom border
        heading_border = {
            "border_bottom": {
                "color": heading_style["accent_color"],
                "width_pt": 1.0,
                "style": "solid"
            }
        }

    # Font weight mapping
    font_weight = "bold" if typo.get("section_heading_weight", 700) >= 600 else "normal"

    # Name alignment and size overrides based on concept spec
    name_align = "left"
    name_size = 20
    if suffix == "clay_canvas":
        name_align = "right"
        name_size = 22
    elif suffix == "broadside_press":
        name_size = 30

    h_transform = heading_style.get("text_transform", "uppercase")
    
    # Setup H1 visual config template
    h1_visual_config = {
        "font_size_pt": typo.get("section_heading_size_pt", 11.0),
        "font_weight": font_weight,
        "font_color": heading_style["font_color"],
        "text_transform": h_transform,
        "letter_spacing_pt": typo.get("section_heading_tracking_pt", 0.0),
        **heading_border,
        "margin_bottom_pt": typo["spacing_after_pt"]
    }

    # Construct the blocks list
    blocks = [
        {
            "block_id": "name_header",
            "type": "name_block",
            "order": 1,
            "tokens": ["{{CONTACT_NAME}}"],
            "content": "{{CONTACT_NAME}}",
            "visualConfig": {
                "font_size_pt": name_size,
                "font_weight": "bold",
                "font_color": primary_color,
                "text_align": name_align,
                "padding_top_pt": 0,
                "padding_bottom_pt": 2,
                "letter_spacing": "normal",
                "margin_bottom_pt": 6
            }
        },
        {
            "block_id": "contact_info",
            "type": "contact_block",
            "order": 2,
            "tokens": ["{{CONTACT_PHONE}}", "{{CONTACT_EMAIL}}", "{{CONTACT_LOCATION}}"],
            "content": "{{CONTACT_PHONE}}    {{CONTACT_EMAIL}}    {{CONTACT_LOCATION}}",
            "visualConfig": {
                "font_size_pt": 9,
                "font_color": theme["muted_text_color"],
                "text_align": name_align,
                "padding_top_pt": 3,
                "padding_bottom_pt": 14,
                "line_spacing": line_spacing,
                "margin_bottom_pt": 6,
                "separator": "inline_spaced"
            }
        },
        {
            "block_id": "role_headline",
            "type": "headline_block",
            "order": 3,
            "tokens": ["{{TARGET_ROLE}}"],
            "content": "{{TARGET_ROLE}}",
            "visualConfig": {
                "font_size_pt": typo.get("section_heading_size_pt", 11.0),
                "font_weight": "bold",
                "font_color": theme["palette"]["complementary_accent"],
                "text_align": name_align,
                "padding_top_pt": 0,
                "padding_bottom_pt": 16,
                "margin_bottom_pt": 6
            }
        },
        {
            "block_id": "summary_section",
            "type": "summary_block",
            "order": 4,
            "heading": "SUMMARY",
            "tokens": ["{{PROFESSIONAL_SUMMARY}}"],
            "content": "{{PROFESSIONAL_SUMMARY}}",
            "visualConfig": {
                "heading": h1_visual_config,
                "body": {
                    "font_size_pt": base_size_pt,
                    "font_color": theme["body_text_color"],
                    "line_spacing": line_spacing
                }
            }
        },
        {
            "block_id": "skills_section",
            "type": "skills_block",
            "order": 5,
            "heading": "SKILLS",
            "tokens": ["{{SKILL_1}}", "{{SKILL_2}}", "{{SKILL_3}}", "{{SKILL_4}}", "{{SKILL_5}}", "{{SKILL_6}}"],
            "layout": "grouped_inline",
            "visualConfig": {
                "heading": h1_visual_config,
                "container": {
                    "background_color": theme["skills_background_tint"],
                    "padding_top_pt": 6,
                    "padding_bottom_pt": 6,
                    "padding_left_pt": 10,
                    "padding_right_pt": 10
                },
                "item": {
                    "font_size_pt": base_size_pt,
                    "font_color": theme["body_text_color"],
                    "separator": "comma",
                    "display": "inline"
                }
            }
        },
        {
            "block_id": "experience_section",
            "type": "experience_block",
            "order": 6,
            "heading": "EXPERIENCE",
            "max_roles": 6,
            "max_bullets_per_role": 4,
            "roles": [
                {
                    "role_index": r,
                    "tokens": {
                        "title": f"{{{{ROLE_{r}_TITLE}}}}",
                        "org": f"{{{{ROLE_{r}_ORG}}}}",
                        "dates": f"{{{{ROLE_{r}_DATES}}}}",
                        "bullets": [f"{{{{ROLE_{r}_BULLET_{b}}}}}" for b in range(1, 5)]
                    }
                } for r in range(1, 7)
            ],
            "visualConfig": {
                "heading": h1_visual_config,
                "role_title": {
                    "font_size_pt": base_size_pt,
                    "font_weight": "bold",
                    "font_color": theme["body_text_color"],
                    "margin_top_pt": 6
                },
                "role_meta": {
                    "font_size_pt": 9,
                    "font_style": "normal",
                    "font_color": theme["muted_text_color"],
                    "margin_bottom_pt": 6,
                    "format": "{{ROLE_N_ORG}}   {{ROLE_N_DATES}}"
                },
                "bullet": {
                    "font_size_pt": base_size_pt,
                    "font_color": theme["body_text_color"],
                    "glyph": "-",
                    "indent_pt": 14,
                    "line_spacing": line_spacing,
                    "margin_bottom_pt": 6
                }
            }
        },
        {
            "block_id": "education_section",
            "type": "education_block",
            "order": 7,
            "heading": "EDUCATION",
            "tokens": ["{{EDUCATION_1}}", "{{EDUCATION_2}}"],
            "visualConfig": {
                "heading": h1_visual_config,
                "item": {
                    "font_size_pt": base_size_pt,
                    "font_color": theme["body_text_color"],
                    "line_spacing": line_spacing,
                    "separator": "line_break"
                }
            }
        },
        {
            "block_id": "certifications_section",
            "type": "certifications_block",
            "order": 8,
            "heading": "CERTIFICATIONS",
            "tokens": ["{{CERT_1}}", "{{CERT_2}}", "{{CERT_3}}"],
            "visualConfig": {
                "heading": h1_visual_config,
                "item": {
                    "font_size_pt": base_size_pt,
                    "font_color": theme["body_text_color"],
                    "line_spacing": line_spacing,
                    "separator": "line_break"
                }
            }
        }
    ]

    # Combine into schema v2.0 shape
    template = {
        "schema_version": "2.0",
        "template_id": f"resume_{suffix}_v1",
        "tier": 2,
        "tier_label": "ATS Modern",
        "doc_type": "resume",
        "target_sector": theme.get("target_sector") or ["community_services", "social_work", "government"],
        "region": "AU",
        "placeholder_schema": "PLACEHOLDER_SCHEMA_V2",
        "description": f"Production template compiled from theme {theme_path.stem}. {theme.get('description', '')}",
        "ats_constraints": {
            "columns": 1,
            "allows_tables": False,
            "allows_images": False,
            "allows_text_boxes": False,
            "allows_headers_footers": False,
            "font_family": base_font,
            "content_layer": "body_only",
            "forbidden_glyphs": ["•", "✔", "★", "❖", "●", "✅", "❌", "|"]
        },
        "palette": palette,
        "typography": typography,
        "page": page,
        "blocks": blocks
    }
    
    return template

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 compile_theme.py <theme_file.json> [<theme_file2.json> ...]")
        sys.exit(1)
        
    for arg in sys.argv[1:]:
        p = Path(arg)
        if not p.exists():
            print(f"Error: {p} not found")
            continue
            
        print(f"Compiling {p.name} ...")
        try:
            template = compile_one(p)
            out_name = f"resume_{get_theme_suffix(p.name)}_v1.json"
            out_path = TEMPLATES_DIR / out_name
            out_path.write_text(json.dumps(template, indent=2), encoding="utf-8")
            print(f"  Saved to {out_path}")
        except Exception as e:
            print(f"  Failed to compile {p.name}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
