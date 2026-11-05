#!/usr/bin/env python3
"""
theme_fingerprint.py — Read-only structural fingerprint of compiled theme templates.

Extracts the visible-in-document features of compiled v2.0 templates
(resume_*, cover_letter_*, ksc_*), splits them into structural and cosmetic
features, and finds each theme's nearest neighbour (same doc_type) by
structural distance. Numeric values are bucketed using thresholds in
config/theme_fingerprint.json; a change inside one bucket is cosmetic.

Only properties that tools/build_golden_master.py actually emits are scored as
"structural". Properties the builder never reads (text_transform, letter
spacing, alignment, contact separator, skills layout/item display, block
order) are listed under "not_emitted": reported for information, never counted
in structural distance. Heading case comes from each block's literal heading
text, which the builder does emit.

Writes nothing. Prints JSON to stdout.

Usage:
    .venv/bin/python tools/theme_fingerprint.py --all
    .venv/bin/python tools/theme_fingerprint.py templates/resume_hybrid_v1.json templates/resume_chronological_v1.json
    .venv/bin/python tools/theme_fingerprint.py --all --doc-type resume --nearest

Exit codes: 0 ok, 2 usage/input error.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = ROOT / "templates"
CONFIG = json.loads((ROOT / "config" / "theme_fingerprint.json").read_text(encoding="utf-8"))


def _bucket(value: float | None, edges: list[float], labels: list[str]) -> str | None:
    if value is None:
        return None
    for edge, label in zip(edges, labels):
        if value < edge:
            return label
    return labels[-1]


def _first_heading(blocks: list[dict]) -> dict:
    for block in blocks:
        heading = block.get("visualConfig", {}).get("heading")
        if heading:
            return heading
    return {}


def _source_for(path: Path) -> Path | None:
    # resume_graphite_ledger_v1.json -> theme-NN-graphite-ledger.json
    stem = path.stem.removeprefix("resume_").rsplit("_v", 1)[0].replace("_", "-")
    matches = sorted(TEMPLATES_DIR.glob(f"theme-*-{stem}.json"))
    return matches[0] if matches else None


def _luminance(hex_color: str) -> float:
    channels = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def _text_styles(node: object, path: str = "") -> list[tuple[str, dict]]:
    """Every dict carrying a 6-digit font_color, with its path."""
    found = []
    if isinstance(node, dict):
        color = node.get("font_color")
        if isinstance(color, str) and len(color) == 7:
            found.append((path, node))
        for key, value in node.items():
            found.extend(_text_styles(value, f"{path}.{key}"))
    elif isinstance(node, list):
        for item in node:
            label = item.get("block_id", "") if isinstance(item, dict) else ""
            found.extend(_text_styles(item, f"{path}[{label}]"))
    return found


def contrast_failures(blocks: list[dict], background: str, base_size: float | None) -> list[dict]:
    """Text styles below WCAG AA (3:1 large text, else 4.5:1) against the page background,
    or the block's container fill when it has one."""
    failures = []
    for block in blocks:
        fill = block.get("visualConfig", {}).get("container", {}).get("background_color")
        failures.extend(_block_failures(block, fill or background, base_size))
    return failures


def _block_failures(block: dict, background: str, base_size: float | None) -> list[dict]:
    bg = _luminance(background)
    failures = []
    for path, style in _text_styles(block, f"[{block.get('block_id', '')}]"):
        fg = _luminance(style["font_color"])
        ratio = round((max(fg, bg) + 0.05) / (min(fg, bg) + 0.05), 2)
        size = style.get("font_size_pt") or base_size or 0
        large = size >= 18 or (size >= 14 and style.get("font_weight") == "bold")
        required = 3.0 if large else 4.5
        if ratio < required:
            failures.append({"path": path, "color": style["font_color"], "background": background,
                             "size_pt": size, "ratio": ratio, "required": required})
    return failures


def _heading_case(blocks: list[dict]) -> str | None:
    """Case of the literal section-heading text (the builder emits it verbatim)."""
    texts = [b["heading"] for b in blocks if isinstance(b.get("heading"), str)]
    letters = [t for t in texts if any(c.isalpha() for c in t)]
    if not letters:
        return None
    if all(t == t.upper() for t in letters):
        return "upper"
    if all(t == t.title() for t in letters):
        return "title"
    return "mixed"


def fingerprint(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    typo = data.get("typography", {})
    page = data.get("page", {})
    blocks = sorted(data.get("blocks", []), key=lambda b: b.get("order", 0))
    by_id = {b.get("block_id"): b.get("visualConfig", {}) for b in blocks}
    heading = _first_heading(blocks)
    name = by_id.get("name_header", {})
    contact = by_id.get("contact_info", {})
    skills_block = next((b for b in blocks if b.get("block_id") == "skills_section"), {})
    skills = skills_block.get("visualConfig", {})

    base = typo.get("base_size_pt")
    head_size = typo.get("section_heading_size_pt") or heading.get("font_size_pt")
    name_size = name.get("font_size_pt")
    margins = [page.get(f"margin_{s}_cm") for s in ("top", "bottom", "left", "right")]
    margins = [m for m in margins if m is not None]
    margin_mean = round(sum(margins) / len(margins), 2) if margins else None
    tracking = heading.get("letter_spacing_pt", typo.get("section_heading_tracking_pt"))

    decoration = "none"
    if "border_bottom" in heading and "border_left" in heading:
        decoration = "both"  # forbidden by THEME_SPEC_GUIDE
    elif "border_bottom" in heading:
        decoration = "border_bottom"
    elif "border_left" in heading:
        decoration = "border_left"

    structural = {
        "heading_decoration": decoration,
        "heading_case": _heading_case(blocks),
        "name_rule": bool(name.get("border_bottom")),
        "heading_scale": _bucket(head_size / base if head_size and base else None,
                                 CONFIG["heading_scale_buckets"], ["flat", "moderate", "strong"]),
        "name_scale": _bucket(name_size / base if name_size and base else None,
                              CONFIG["name_scale_buckets"], ["modest", "prominent", "dominant"]),
        "skills_fill": bool(skills.get("container", {}).get("background_color")) if skills else None,
        "line_rhythm": _bucket(typo.get("line_spacing"), CONFIG["line_spacing_buckets"],
                               ["tight", "medium", "airy"]),
        "margin_frame": _bucket(margin_mean, CONFIG["margin_mean_cm_buckets"],
                                ["narrow", "standard", "wide"]),
    }
    # Never read by build_golden_master.py: informational only, not scored.
    not_emitted = {
        "block_order": [b.get("block_id") for b in blocks],
        "heading_transform": heading.get("text_transform"),
        "heading_tracking": None if tracking is None else
            ("tracked" if tracking >= CONFIG["heading_tracking_min_pt"] else "flat"),
        "name_align": name.get("text_align"),
        "contact_separator": contact.get("separator"),
        "skills_layout": skills_block.get("layout"),
        "skills_item_display": skills.get("item", {}).get("display"),
    }
    cosmetic = {
        "base_font": typo.get("base_font"),
        "heading_font": data.get("heading_font_family"),
        "heading_color": heading.get("font_color"),
        "accent_color": (heading.get("border_bottom") or heading.get("border_left") or {}).get("color"),
        "skills_fill_color": skills.get("container", {}).get("background_color"),
        "base_size_pt": base,
        "line_spacing": typo.get("line_spacing"),
        "section_heading_size_pt": head_size,
        "name_size_pt": name_size,
        "margin_mean_cm": margin_mean,
        "background_color": page.get("background_color"),
    }

    result = {
        "file": str(path.relative_to(ROOT)) if path.is_absolute() else str(path),
        "template_id": data.get("template_id"),
        "doc_type": data.get("doc_type"),
        "target_sector": data.get("target_sector"),
        "structural": structural,
        "not_emitted": not_emitted,
        "cosmetic": cosmetic,
        "contrast_failures": contrast_failures(blocks, page.get("background_color", "#FFFFFF"), base),
        "source": None,
        "visual_identity": None,
        "source_drift": [],
    }

    source = _source_for(path) if data.get("doc_type") == "resume" else None
    if source:
        src = json.loads(source.read_text(encoding="utf-8"))
        result["source"] = str(source.relative_to(ROOT))
        result["visual_identity"] = src.get("visual_identity")
        src_typo = src.get("typography", {})
        for key in ("base_font", "base_size_pt", "line_spacing", "section_heading_size_pt"):
            if key in src_typo and src_typo[key] != typo.get(key):
                result["source_drift"].append(
                    {"field": f"typography.{key}", "source": src_typo[key], "compiled": typo.get(key)}
                )
    return result


def nearest(prints: list[dict]) -> list[dict]:
    out = []
    for a in prints:
        rows = []
        for b in prints:
            if b is a or b["doc_type"] != a["doc_type"]:
                continue
            s_diff = [k for k in a["structural"] if a["structural"][k] != b["structural"][k]]
            c_diff = [k for k in a["cosmetic"] if a["cosmetic"][k] != b["cosmetic"][k]]
            rows.append({"neighbour": b["template_id"], "structural_distance": len(s_diff),
                         "structural_diffs": s_diff, "cosmetic_diffs": c_diff})
        if not rows:
            out.append({"template_id": a["template_id"], "nearest": []})
            continue
        best = min(r["structural_distance"] for r in rows)
        ties = [r for r in rows if r["structural_distance"] == best]
        out.append({
            "template_id": a["template_id"],
            "nearest": ties,
            "cosmetic_only": best == 0,
        })
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="*", help="Compiled template JSON paths")
    parser.add_argument("--all", action="store_true", help="All compiled resume_/cover_letter_/ksc_ templates")
    parser.add_argument("--doc-type", choices=["resume", "cover_letter", "ksc"], help="Filter by doc_type")
    parser.add_argument("--nearest", action="store_true", help="Print nearest-neighbour report instead of fingerprints")
    args = parser.parse_args()

    if args.all:
        paths = sorted(p for prefix in ("resume_", "cover_letter_", "ksc_")
                       for p in TEMPLATES_DIR.glob(f"{prefix}*.json"))
    else:
        paths = [Path(p).resolve() for p in args.paths]
    if not paths:
        parser.print_usage(sys.stderr)
        return 2
    missing = [p for p in paths if not p.exists()]
    if missing:
        print(f"Not found: {', '.join(map(str, missing))}", file=sys.stderr)
        return 2

    prints = [fingerprint(p) for p in paths]
    if args.doc_type:
        prints = [p for p in prints if p["doc_type"] == args.doc_type]
    print(json.dumps(nearest(prints) if args.nearest else prints, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
