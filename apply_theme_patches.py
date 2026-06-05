#!/usr/bin/env python3
"""
Career Brain — Theme Premium Patch Script
==========================================
Run from the project root (where theme-*.json files live).
Writes patched files to ./patched/ (does NOT overwrite originals).
Review diff, then copy to templates/ when satisfied.

Usage:
    python3 apply_theme_patches.py
    python3 apply_theme_patches.py --inplace   # overwrite originals

WCAG AA verification is built in: any text-on-surface pair that
fails 4.5:1 after patching will print a warning before writing.
"""

import json, copy, math, sys, os, pathlib

# ── WCAG helper ──────────────────────────────────────────────────────────────
def _lin(c): c /= 255; return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
def luminance(h):
    h = h.lstrip('#'); r,g,b = (int(h[i:i+2],16) for i in (0,2,4))
    return 0.2126*_lin(r) + 0.7152*_lin(g) + 0.0722*_lin(b)
def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la,lb), min(la,lb)
    return round((hi + 0.05) / (lo + 0.05), 2)

# ── Patch definitions ─────────────────────────────────────────────────────────
# Each entry is (filename, patches_dict, heading_font_family, text_pairs_to_check)
# patches_dict keys are dot-paths into the JSON; special keys:
#   "heading_font_family"  -> injected as new top-level field
#   "legacy_fields.<key>"  -> written under legacy_fields block
# text_pairs_to_check: list of (fg_field_dotpath, bg_hex) for WCAG post-check

PATCHES = {

"theme-01-graphite-ledger.json": {
    "fields": {
        "ats_constraints.font_family":              ["Source Serif 4", "Georgia"],
        "typography.base_font":                     "Source Serif 4",
        "typography.line_spacing":                  1.30,
        "typography.spacing_after_pt":              7,
        "palette.base_colours":                     ["#14181F", "#3D434F", "#C2C7CF"],
        "complementary_accent":                     "#33485E",
        "palette.neutral_text":                     "#14181F",
        "muted_text_color":                         "#5A6270",
        "body_text_color":                          "#14181F",
        "section_heading_style.font_color":         "#14181F",
        "section_heading_style.accent_color":       "#33485E",
        "skills_background_tint":                   "#E0E4EA",
    },
    "heading_font_family": ["Archivo", "Arial"],
    "wcag_checks": [("#14181F","#FFFFFF"),("#5A6270","#FFFFFF"),("#33485E","#FFFFFF")],
},

"theme-02-midnight-blueprint.json": {
    "fields": {
        "ats_constraints.font_family":              ["IBM Plex Sans", "Arial"],
        "typography.base_font":                     "IBM Plex Sans",
        "typography.line_spacing":                  1.20,
        "typography.spacing_after_pt":              4,
        "palette.base_colours":                     ["#0B1B2B", "#2E5A8C", "#16324A"],
        "complementary_accent":                     "#5CC8FF",
        "palette.neutral_surface":                  "#0B1B2B",
        "palette.neutral_background":               "#0B1B2B",
        "palette.neutral_text":                     "#E8EEF4",
        "palette.supporting_neutral":               "#16324A",
        "body_text_color":                          "#E8EEF4",
        "muted_text_color":                         "#9FB2C4",
        "section_heading_style.font_color":         "#E8EEF4",
        "section_heading_style.accent_color":       "#5CC8FF",
        "skills_background_tint":                   "#16324A",
    },
    "heading_font_family": ["IBM Plex Mono", "Consolas"],
    # dark surface: check light-on-dark
    "wcag_checks": [("#E8EEF4","#0B1B2B"),("#9FB2C4","#0B1B2B"),("#5CC8FF","#0B1B2B")],
    "notes": [
        "ADVISORY: dark neutral_surface is an ATS/print risk (see render spec).",
        "Consider a light 'Daylight Blueprint' sibling for submission copies.",
    ],
},

"theme-03-citrus-edge.json": {
    "fields": {
        "ats_constraints.font_family":              ["Public Sans", "Arial"],
        "typography.base_font":                     "Public Sans",
        "typography.line_spacing":                  1.32,
        "typography.spacing_after_pt":              7,
        "palette.base_colours":                     ["#1A1D24", "#5A6270", "#E2571E"],
        "complementary_accent":                     "#F4B41A",   # band/marker only — NOT heading text
        "palette.neutral_text":                     "#1A1D24",
        "body_text_color":                          "#1A1D24",
        "muted_text_color":                         "#5A6270",
        "section_heading_style.font_color":         "#1A1D24",
        "section_heading_style.accent_color":       "#B5481F",  # burnt-orange heads
        "skills_background_tint":                   "#FBEAD2",
    },
    "heading_font_family": ["Space Grotesk", "Arial"],
    "wcag_checks": [("#1A1D24","#FFFFFF"),("#B5481F","#FFFFFF"),("#5A6270","#FFFFFF")],
    "notes": [
        "complementary_accent #F4B41A is band/marker only (1.53:1 — fails as text). "
        "Never apply to heading or body text.",
    ],
},

"theme-04-emerald-transit.json": {
    "fields": {
        "ats_constraints.font_family":              ["Public Sans", "Arial"],
        "typography.base_font":                     "Public Sans",
        "typography.line_spacing":                  1.30,
        "typography.spacing_after_pt":              6,
        "palette.base_colours":                     ["#0B3D2E", "#1A7A52", "#BFE3CF"],
        "complementary_accent":                     "#1A7A52",
        "palette.neutral_text":                     "#0B3D2E",
        "body_text_color":                          "#0B3D2E",
        "muted_text_color":                         "#2F6F57",  # KEY FIX — was #6EE7B7 (1.52:1 FAIL)
        "section_heading_style.font_color":         "#0B3D2E",
        "section_heading_style.accent_color":       "#1A7A52",
        "skills_background_tint":                   "#E7F4EC",
    },
    "heading_font_family": ["Fraunces", "Georgia"],
    "wcag_checks": [("#0B3D2E","#FFFFFF"),("#1A7A52","#FFFFFF"),("#2F6F57","#FFFFFF")],
},

"theme-05-copper-teal-circuit.json": {
    "fields": {
        "ats_constraints.font_family":              ["IBM Plex Sans", "Arial"],
        "typography.base_font":                     "IBM Plex Sans",
        "typography.line_spacing":                  1.28,
        "typography.spacing_after_pt":              6,
        "palette.base_colours":                     ["#1D1C1A", "#A85A34", "#6B5A4A"],
        "complementary_accent":                     "#1F7A7A",
        "palette.neutral_text":                     "#1D1C1A",
        "body_text_color":                          "#1D1C1A",
        "muted_text_color":                         "#6B5A4A",
        "section_heading_style.font_color":         "#8A4A2C",  # copper heads
        "section_heading_style.accent_color":       "#1F7A7A",
        "skills_background_tint":                   "#E8D4C6",
    },
    "heading_font_family": ["Space Grotesk", "Arial"],
    "wcag_checks": [("#1D1C1A","#FAF8F5"),("#8A4A2C","#FAF8F5"),("#1F7A7A","#FAF8F5"),("#6B5A4A","#FAF8F5")],
},

"theme-06-violet-signal.json": {
    "fields": {
        "ats_constraints.font_family":              ["Newsreader", "Georgia"],
        "typography.base_font":                     "Newsreader",
        "typography.line_spacing":                  1.32,
        "typography.spacing_after_pt":              7,
        "palette.base_colours":                     ["#15131A", "#3D1A78", "#6A2CC9"],
        "complementary_accent":                     "#C2410C",
        "palette.neutral_text":                     "#15131A",
        "body_text_color":                          "#15131A",
        "muted_text_color":                         "#5A5560",
        "section_heading_style.font_color":         "#3D1A78",
        "section_heading_style.accent_color":       "#6A2CC9",
        "skills_background_tint":                   "#EFE6FF",
    },
    "heading_font_family": ["Space Grotesk", "Arial"],
    "wcag_checks": [("#15131A","#FFFFFF"),("#3D1A78","#FFFFFF"),("#6A2CC9","#FFFFFF"),("#5A5560","#FFFFFF")],
},

"theme-07-solar-gradient.json": {
    "fields": {
        "ats_constraints.font_family":              ["Spectral", "Georgia"],
        "typography.base_font":                     "Spectral",
        "typography.line_spacing":                  1.34,
        "typography.spacing_after_pt":              8,
        "palette.base_colours":                     ["#34261E", "#8A5638", "#E7C7A6"],
        "complementary_accent":                     "#B5532A",
        "palette.neutral_surface":                  "#FFF8F2",
        "palette.neutral_background":               "#FFF8F2",
        "palette.neutral_text":                     "#34261E",
        "body_text_color":                          "#34261E",
        "muted_text_color":                         "#6E4A33",  # KEY FIX — was #9A6A4B (4.43:1)
        "section_heading_style.font_color":         "#7A4A30",  # KEY FIX — was #9A6A4B
        "section_heading_style.accent_color":       "#B5532A",
        "skills_background_tint":                   "#F4E5D6",
    },
    "heading_font_family": ["Fraunces", "Georgia"],
    "wcag_checks": [("#34261E","#FFF8F2"),("#7A4A30","#FFF8F2"),("#6E4A33","#FFF8F2"),("#B5532A","#FFF8F2")],
    "notes": [
        "palette is still warm-tonal; optional cross-hue micro-accent "
        "(e.g. dusk-teal #1F6A6A) on metadata-only fully satisfies avoid_list 'tonal-only'.",
    ],
},

"theme-08-nordic-neon.json": {
    "fields": {
        "ats_constraints.font_family":              ["Inter", "Arial"],
        "typography.base_font":                     "Inter",
        "typography.line_spacing":                  1.20,
        "typography.spacing_after_pt":              4,
        "palette.base_colours":                     ["#0F1A2A", "#4E5A6E", "#CDE9F2"],
        "complementary_accent":                     "#5BD4F5",   # band/micro only — NOT text
        "palette.neutral_surface":                  "#F7FBFC",
        "palette.neutral_background":               "#F7FBFC",
        "palette.neutral_text":                     "#0F1A2A",
        "body_text_color":                          "#0F1A2A",
        "muted_text_color":                         "#4E5A6E",
        "section_heading_style.font_color":         "#155E78",   # KEY FIX — was #4F89B9 (3.62:1)
        "section_heading_style.accent_color":       "#0E6E8C",   # KEY FIX — was #7BE0FF (1.46:1 FAIL)
        "skills_background_tint":                   "#E3F4F8",
    },
    "heading_font_family": ["Space Grotesk", "Arial"],
    "wcag_checks": [("#0F1A2A","#F7FBFC"),("#155E78","#F7FBFC"),("#0E6E8C","#F7FBFC"),("#4E5A6E","#F7FBFC")],
    "notes": [
        "complementary_accent #5BD4F5 is band/micro decorative only (fails as text). "
        "accent_color #0E6E8C carries all text-level neon identity.",
    ],
},

"theme-09-terracotta-service.json": {
    "fields": {
        "ats_constraints.font_family":              ["Source Serif 4", "Georgia"],
        "typography.base_font":                     "Source Serif 4",
        "typography.line_spacing":                  1.32,
        "typography.spacing_after_pt":              7,
        "palette.base_colours":                     ["#3A2A22", "#9A5638", "#E8CBB3"],
        "complementary_accent":                     "#B5532A",
        "palette.neutral_surface":                  "#FCF7F2",
        "palette.neutral_background":               "#FCF7F2",
        "palette.neutral_text":                     "#3A2A22",
        "body_text_color":                          "#3A2A22",
        "muted_text_color":                         "#6E5346",   # KEY FIX — was #B08772 (3.08:1 FAIL)
        "section_heading_style.font_color":         "#8A4A2E",   # KEY FIX — was #B77456 (3.58:1)
        "section_heading_style.accent_color":       "#B5532A",
        "skills_background_tint":                   "#F3E6DB",
        "visual_identity.contrast_intensity":       "medium",    # was "low" — mission theme must not be least accessible
    },
    "heading_font_family": ["Fraunces", "Georgia"],
    "wcag_checks": [("#3A2A22","#FCF7F2"),("#8A4A2E","#FCF7F2"),("#6E5346","#FCF7F2"),("#B5532A","#FCF7F2")],
},

"theme-10-rainbow-minimal.json": {
    "fields": {
        "ats_constraints.font_family":              ["Work Sans", "Arial"],
        "typography.base_font":                     "Work Sans",
        "typography.line_spacing":                  1.30,
        "typography.spacing_after_pt":              6,
        "palette.base_colours":                     ["#15181E", "#565E6B", "#D4D7DD"],
        "complementary_accent":                     "#C2185B",
        "palette.neutral_text":                     "#15181E",
        "body_text_color":                          "#15181E",
        "muted_text_color":                         "#565E6B",
        "section_heading_style.font_color":         "#15181E",
        "section_heading_style.accent_color":       "#C2185B",
        "skills_background_tint":                   "#F5F5F6",
        # Optional — uncomment to enable spectrum concept
        # "accent_rotation": ["#C2185B","#0E7490","#1A7A52","#B5481F","#6A2CC9"],
    },
    "heading_font_family": ["Outfit", "Arial"],
    "wcag_checks": [("#15181E","#FFFFFF"),("#C2185B","#FFFFFF"),("#565E6B","#FFFFFF")],
    "notes": [
        "accent_rotation is commented out. Uncomment to activate the 'controlled spectrum' "
        "concept (curated 5-hue rotation on section micro-markers only; all ≥ 4.5:1).",
    ],
},

"theme-21-terminal-signal.json": {
    "fields": {
        "ats_constraints.font_family":              ["IBM Plex Sans", "Arial"],
        "typography.base_font":                     "IBM Plex Sans",
        "typography.line_spacing":                  1.20,
        "typography.spacing_after_pt":              4,
        "palette.base_colours":                     ["#0A0A0A", "#3A3A3A", "#6A6A6A"],
        "complementary_accent":                     "#00B341",   # band/underscore glow only
        "palette.neutral_text":                     "#0A0A0A",
        "body_text_color":                          "#0A0A0A",
        "muted_text_color":                         "#4A4A4A",
        "section_heading_style.font_color":         "#0A0A0A",
        "section_heading_style.accent_color":       "#0A6E2E",   # text-safe terminal green
        "skills_background_tint":                   "#EAEAEA",
    },
    "heading_font_family": ["JetBrains Mono", "Consolas"],
    "wcag_checks": [("#0A0A0A","#FFFFFF"),("#0A6E2E","#FFFFFF"),("#4A4A4A","#FFFFFF")],
    "notes": [
        "complementary_accent #00B341 is decorative rule/underscore ONLY (2.79:1). "
        "section_heading_style.accent_color #0A6E2E carries text-level terminal-green identity.",
    ],
},

"theme-22-horizon-edge.json": {
    "fields": {
        "ats_constraints.font_family":              ["Libre Franklin", "Arial"],
        "typography.base_font":                     "Libre Franklin",
        "typography.line_spacing":                  1.30,
        "typography.spacing_after_pt":              6,
        "palette.base_colours":                     ["#0A1A2F", "#1E3E62", "#476685"],
        "complementary_accent":                     "#FF5A3C",   # band/thick-frame only
        "palette.neutral_text":                     "#0A1A2F",
        "body_text_color":                          "#0A1A2F",
        "muted_text_color":                         "#3E5570",
        "section_heading_style.font_color":         "#0A1A2F",
        "section_heading_style.accent_color":       "#C4441E",   # KEY FIX — was #FF5722 (3.16:1)
        "skills_background_tint":                   "#E0E8F0",
    },
    "heading_font_family": ["Archivo", "Arial"],
    "wcag_checks": [("#0A1A2F","#FFFFFF"),("#C4441E","#FFFFFF"),("#3E5570","#FFFFFF")],
    "notes": [
        "complementary_accent #FF5A3C is thick-frame/band decoration only. "
        "section_heading_style.accent_color #C4441E carries the cinematic coral on text.",
    ],
},

"theme-23-broadside-press.json": {
    "fields": {
        "ats_constraints.font_family":              ["Source Serif 4", "Georgia"],
        "typography.base_font":                     "Source Serif 4",
        "typography.line_spacing":                  1.30,
        "typography.spacing_after_pt":              6,
        "palette.base_colours":                     ["#0B0B0B", "#2A2A2A", "#5A5A5A"],
        "complementary_accent":                     "#A01818",
        "palette.neutral_text":                     "#0B0B0B",
        "palette.neutral_background":               "#FFFFFF",
        "body_text_color":                          "#0B0B0B",   # FIX pure #000000 (spec forbids)
        "muted_text_color":                         "#3A3A3A",
        "section_heading_style.font_color":         "#0B0B0B",
        "section_heading_style.accent_color":       "#A01818",
        "skills_background_tint":                   "#F5F5F5",
    },
    "heading_font_family": ["Archivo Black", "Arial"],
    "wcag_checks": [("#0B0B0B","#FFFFFF"),("#A01818","#FFFFFF"),("#3A3A3A","#FFFFFF")],
},

"theme-24-clay-canvas.json": {
    "fields": {
        "ats_constraints.font_family":              ["Lora", "Georgia"],
        "typography.base_font":                     "Lora",
        "typography.section_heading_weight":        650,         # KEY FIX — was 400 (inverted hierarchy)
        "typography.line_spacing":                  1.34,
        "typography.spacing_after_pt":              9,
        "palette.base_colours":                     ["#2E1F18", "#6A4A3A", "#9A7A6A"],
        "complementary_accent":                     "#B24A2B",
        "palette.neutral_surface":                  "#FFFFFF",
        "palette.neutral_background":               "#FBF8F4",
        "palette.neutral_text":                     "#2E1F18",
        "body_text_color":                          "#2E1F18",
        "muted_text_color":                         "#6E5346",
        "section_heading_style.font_color":         "#2E1F18",
        "section_heading_style.accent_color":       "#B24A2B",
        "skills_background_tint":                   "#EFE6DD",
    },
    "heading_font_family": ["Fraunces", "Georgia"],
    "wcag_checks": [("#2E1F18","#FBF8F4"),("#B24A2B","#FFFFFF"),("#6E5346","#FBF8F4")],
    "notes": [
        "section_heading_weight raised 400 → 650 to restore hierarchy. "
        "text_transform 'lowercase' is kept — Fraunces at 650 is visually distinct from body.",
    ],
},

"theme-25-cyan-blueprint.json": {
    "fields": {
        "ats_constraints.font_family":              ["IBM Plex Sans", "Arial"],
        "typography.base_font":                     "IBM Plex Sans",
        "typography.line_spacing":                  1.22,
        "typography.spacing_after_pt":              5,
        "palette.base_colours":                     ["#16212B", "#34495E", "#5D6D7E"],
        "complementary_accent":                     "#0A7387",   # KEY FIX — was #0088A0 (4.18:1)
        "palette.neutral_text":                     "#16212B",
        "palette.neutral_background":               "#F4F6F7",
        "body_text_color":                          "#16212B",
        "muted_text_color":                         "#4E5E6E",
        "section_heading_style.font_color":         "#16212B",
        "section_heading_style.accent_color":       "#0A7387",
        "skills_background_tint":                   "#E4EBEF",
    },
    "heading_font_family": ["IBM Plex Mono", "Consolas"],
    "wcag_checks": [("#16212B","#FFFFFF"),("#0A7387","#FFFFFF"),("#4E5E6E","#FFFFFF")],
},

}  # end PATCHES


# ── Dot-path setter ───────────────────────────────────────────────────────────
def set_path(d, path, value):
    keys = path.split(".")
    for k in keys[:-1]:
        d = d.setdefault(k, {})
    d[keys[-1]] = value


# ── Apply + write ─────────────────────────────────────────────────────────────
def _lin(c): c /= 255; return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
def luminance(h):
    h = h.lstrip('#'); r,g,b = (int(h[i:i+2],16) for i in (0,2,4))
    return 0.2126*_lin(r) + 0.7152*_lin(g) + 0.0722*_lin(b)
def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    return round((max(la,lb) + 0.05) / (min(la,lb) + 0.05), 2)

INPLACE = "--inplace" in sys.argv
base = pathlib.Path(__file__).parent / "templates"
out_dir = base if INPLACE else base / "patched"
out_dir.mkdir(exist_ok=True)

ok = fail = 0
for fname, spec in PATCHES.items():
    src = base / fname
    if not src.exists():
        print(f"  SKIP {fname} (not found)")
        continue

    data = json.loads(src.read_text())
    original = copy.deepcopy(data)

    # Preserve old values under legacy_fields.pre_premium_patch
    legacy = {}
    for dotpath, new_val in spec["fields"].items():
        keys = dotpath.split(".")
        cur = data
        try:
            for k in keys: cur = cur[k]
            legacy[dotpath] = cur
        except (KeyError, TypeError):
            pass
    data.setdefault("legacy_fields", {})["pre_premium_patch"] = legacy

    # Apply field patches
    for dotpath, new_val in spec["fields"].items():
        set_path(data, dotpath, new_val)

    # Inject heading_font_family (new field, after ats_constraints)
    if "heading_font_family" in spec:
        data["heading_font_family"] = spec["heading_font_family"]

    # WCAG post-check
    warnings = []
    for fg, bg in spec.get("wcag_checks", []):
        r = contrast(fg, bg)
        if r < 4.5:
            warnings.append(f"    ⚠  WCAG FAIL after patch: {fg} on {bg} = {r}:1")

    # Write
    dest = out_dir / fname
    dest.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    status = "✓" if not warnings else "⚠"
    print(f"  {status}  {fname} → {'(in-place)' if INPLACE else str(dest.relative_to(base))}")
    for w in warnings:
        print(w); fail += 1
    for note in spec.get("notes", []):
        print(f"    ℹ  {note}")
    if not warnings:
        ok += 1

print(f"\n  Patched {ok+fail} files. Contrast warnings: {fail}.")
if not INPLACE:
    print(f"  Review diff in ./patched/ then copy to your templates dir.")
    print(f"  Re-run with --inplace to overwrite originals.")
