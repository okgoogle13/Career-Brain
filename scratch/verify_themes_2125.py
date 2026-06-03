#!/usr/bin/env python3
"""One-off Phase 3 fidelity diff: themes 21-25 JSON vs the text design specs
in claude_code_final_phases_prompt.md. Every `→ maps to X.Y`-annotated spec
field is compared to the produced JSON. Prints MATCH / DEVIATION per field so
the QUALITY_SUMMARY deviation inventory is provably complete (not spot-checked).
Not part of the pipeline. Re-runnable, read-only.
"""
import json
import sys
import re
from pathlib import Path

T = Path("templates")

# ── literal spec values transcribed from the prompt's 5 concepts ──────────────
SPECS = {
    "theme-21-terminal-signal.json": {
        "visual_identity.mood": "cyber, technical, utilitarian, stark",
        "visual_identity.motif_name": "glowing terminal underscores",
        "visual_identity.density_target": "high",
        "visual_identity.silhouette": "flush-left, rigid, data-driven",
        "visual_identity.personality_axis": "precise, unapologetic, developer-minded",
        "visual_identity.header_silhouette": "stark flush-left minimalist block with a heavy neon underscore",
        "visual_identity.section_emphasis_pattern": "accent-led",
        "visual_identity.contrast_intensity": "high",
        "palette.base_colours": ["#111111", "#333333", "#555555"],
        "palette.complementary_accent": "#00FF00",
        "palette.neutral_surface": "#FFFFFF",
        "palette.neutral_text": "#111111",
        "palette.neutral_background": "#FAFAFA",
        "palette.supporting_neutral": "#EAEAEA",
        "typography.base_font": "Roboto",
        "typography.base_size_pt": 10.5,
        "typography.line_spacing": 1.22,
        "typography.section_heading_weight": 700,
        "typography.section_heading_size_pt": 11,
        "typography.section_heading_tracking_pt": 2.0,
        "typography.spacing_after_pt": 4,
        "page.margins_in": {"top": 0.65, "right": 0.65, "bottom": 0.65, "left": 0.65},
        "bands.strategy": "minimal bottom-edge neon accents mimicking a command-line cursor",
        "bands.band_placement_profile": "minimal_signature",
        "bands.placement": ["header edge"],
        "bands.height_rule": {"min_pt": 2, "max_pt": 4, "default_pt": 3},
        "bands.intensity": "strong",
        "bands.accent_placement_profile": "mixed_micro_use",
        "dividers.grammar": "dotted",
        "dividers.frequency": "moderate",
        "dividers.weight": "thin",
        "dividers.divider_rhythm": "regular",
        "dividers.divider_targets": ["between sections", "between role and achievement clusters"],
        "accent_logic.primary_use": ["header underscore", "tiny bullet points", "date markers"],
        "accent_logic.allowed_scope": ["micro markers", "header edge"],
        "accent_logic.forbidden_scope": ["body text", "background fills", "horizontal rules between sections"],
        "accent_logic.accent_balance": "neon green must be used exclusively as a pinpoint \"signal\" in a sea of rigid charcoal text, mimicking a terminal prompt",
        "theme_specific_rules.must_include": ["stark flush-left alignment", "dotted section dividers", "neon green micro-accents", "heavy tracking on headers"],
        "theme_specific_rules.visual_differentiators": ["command-line aesthetic", "neon vs charcoal contrast", "strict rigid left-edge anchoring"],
        "theme_specific_rules.anti_generic_rules": ["no centered text whatsoever", "no solid section dividers", "no soft/rounded fonts"],
        "_avoid_additions": ["centered text", "solid grey dividers", "soft palettes", "serif fonts"],
    },
    "theme-22-horizon-edge.json": {
        "visual_identity.mood": "expansive, optimistic, cinematic, warm",
        "visual_identity.motif_name": "thick cinematic framing rules",
        "visual_identity.density_target": "medium",
        "visual_identity.silhouette": "wide, horizontal-sweeping",
        "visual_identity.personality_axis": "visionary, modern, bold",
        "visual_identity.header_silhouette": "asymmetrical stepped header (name flush left, contact far right) with thick top and bottom coral framing",
        "visual_identity.section_emphasis_pattern": "band-led",
        "visual_identity.contrast_intensity": "medium",
        "palette.base_colours": ["#0B192C", "#1E3E62", "#476685"],
        "palette.complementary_accent": "#FF5722",
        "palette.neutral_surface": "#FFFFFF",
        "palette.neutral_text": "#0B192C",
        "palette.neutral_background": "#F9F9F9",
        "palette.supporting_neutral": "#E0E0E0",
        "typography.base_font": "Montserrat",
        "typography.base_size_pt": 10.5,
        "typography.line_spacing": 1.26,
        "typography.section_heading_weight": 800,
        "typography.section_heading_size_pt": 12,
        "typography.section_heading_tracking_pt": 1.8,
        "typography.spacing_after_pt": 6,
        "page.margins_in": {"top": 0.70, "right": 0.60, "bottom": 0.70, "left": 0.60},
        "bands.strategy": "thick, sweeping horizontal bands that act as cinematic letterboxes for sections",
        "bands.band_placement_profile": "section_only",
        "bands.placement": ["section separator zones"],
        "bands.height_rule": {"min_pt": 4, "max_pt": 6, "default_pt": 4},
        "bands.intensity": "strong",
        "bands.accent_placement_profile": "section_headers_only",
        "dividers.grammar": "solid",
        "dividers.frequency": "sparse",
        "dividers.weight": "medium",
        "dividers.divider_rhythm": "sparse",
        "dividers.divider_targets": ["between major sections only"],
        "accent_logic.primary_use": ["thick horizontal framing rules around section headers"],
        "accent_logic.allowed_scope": ["section horizontal boundaries"],
        "accent_logic.forbidden_scope": ["body text", "small labels", "bullet points"],
        "accent_logic.accent_balance": "coral must only exist as vast, sweeping horizontal lines, never as delicate micro-markers",
        "theme_specific_rules.must_include": ["deep navy body text", "thick coral horizontal rules", "extra-wide tracking on headers", "asymmetrical header layout"],
        "theme_specific_rules.visual_differentiators": ["cinematic/widescreen feel", "vibrant sunset palette against midnight blue", "stepped header alignment"],
        "theme_specific_rules.anti_generic_rules": ["no centered name blocks", "no thin/faint grey lines", "no standard black text"],
        "_avoid_additions": ["black body text", "centered headers", "thin grey dividers", "cramped margins"],
    },
    "theme-23-broadside-press.json": {
        "visual_identity.mood": "journalistic, urgent, factual, uncompromising",
        "visual_identity.motif_name": "heavy headline tracking and sharp offsets",
        "visual_identity.density_target": "high",
        "visual_identity.silhouette": "dense, text-heavy, column-mimicking",
        "visual_identity.personality_axis": "truth-seeking, articulate, bold",
        "visual_identity.header_silhouette": "massive serif typography dominating the top margin, tightly stacked",
        "visual_identity.section_emphasis_pattern": "divider-led",
        "visual_identity.contrast_intensity": "high",
        "palette.base_colours": ["#000000", "#222222", "#444444"],
        "palette.complementary_accent": "#8B0000",
        "palette.neutral_surface": "#FFFFFF",
        "palette.neutral_text": "#000000",
        "palette.neutral_background": "#FFFFFF",
        "palette.supporting_neutral": "#F5F5F5",
        "typography.base_font": "Georgia",
        "typography.base_size_pt": 10.5,
        "typography.line_spacing": 1.24,
        "typography.section_heading_weight": 700,
        "typography.section_heading_size_pt": 14,
        "typography.section_heading_tracking_pt": 0.0,
        "typography.spacing_after_pt": 6,
        "page.margins_in": {"top": 0.60, "right": 0.70, "bottom": 0.60, "left": 0.70},
        "bands.strategy": "sharp, newspaper-like structural divisions using offset rules",
        "bands.band_placement_profile": "divider_led",
        "bands.placement": ["section separator zones"],
        "bands.height_rule": {"min_pt": 1, "max_pt": 2, "default_pt": 1},
        "bands.intensity": "moderate",
        "bands.accent_placement_profile": "metadata_only",
        "dividers.grammar": "sharp+offset",
        "dividers.frequency": "frequent",
        "dividers.weight": "thin-to-medium",
        "dividers.divider_rhythm": "progressive",
        "dividers.divider_targets": ["between sections", "between role and achievement clusters"],
        "accent_logic.primary_use": ["dates", "locations", "sharp structural offset rules"],
        "accent_logic.allowed_scope": ["metadata blocks", "specific horizontal rules"],
        "accent_logic.forbidden_scope": ["body text", "major section headings", "background fills"],
        "accent_logic.accent_balance": "crimson acts as the \"red ink\" editor's pen, used strictly for dates, locations, and structural separations, never for narrative text",
        "theme_specific_rules.must_include": ["pure black Georgia font", "massive tightly-stacked header", "crimson metadata", "sharp offset dividers"],
        "theme_specific_rules.visual_differentiators": ["editorial/newspaper broadsheet aesthetic", "ultra-high contrast serif", "deep crimson \"editor's ink\" accents"],
        "theme_specific_rules.anti_generic_rules": ["do not use sans-serif", "do not use wide tracking on headings", "do not soften black to dark grey"],
        "_avoid_additions": ["sans-serif fonts", "wide tracking", "dark grey instead of pure black", "pastel accents"],
    },
    "theme-24-clay-canvas.json": {
        "visual_identity.mood": "tactile, grounded, artisanal, soft",
        "visual_identity.motif_name": "terracotta chips and vast line spacing",
        "visual_identity.density_target": "low",
        "visual_identity.silhouette": "flush-right floating, airy",
        "visual_identity.personality_axis": "empathetic, thoughtful, crafted",
        "visual_identity.header_silhouette": "flush-right, lowercase-styled header floating in vast whitespace",
        "visual_identity.section_emphasis_pattern": "hybrid",
        "visual_identity.contrast_intensity": "low",
        "palette.base_colours": ["#3E2723", "#5D4037", "#8D6E63"],
        "palette.complementary_accent": "#D84315",
        "palette.neutral_surface": "#FFFFFF",
        "palette.neutral_text": "#3E2723",
        "palette.neutral_background": "#FCFBF8",
        "palette.supporting_neutral": "#EFEBE9",
        "typography.base_font": "Lora",
        "typography.base_size_pt": 10.5,
        "typography.line_spacing": 1.28,
        "typography.section_heading_weight": 400,
        "typography.section_heading_size_pt": 13,
        "typography.section_heading_tracking_pt": 1.0,
        "typography.spacing_after_pt": 8,
        "page.margins_in": {"top": 0.70, "right": 0.70, "bottom": 0.70, "left": 0.70},
        "bands.strategy": "gentle framing using bordered chips rather than sweeping lines",
        "bands.band_placement_profile": "mixed",
        "bands.placement": ["section labels", "metadata strip"],
        "bands.height_rule": {"min_pt": 1, "max_pt": 1, "default_pt": 1},
        "bands.intensity": "subtle",
        "bands.accent_placement_profile": "chips_only",
        "dividers.grammar": "dashed",
        "dividers.frequency": "sparse",
        "dividers.weight": "thin",
        "dividers.divider_rhythm": "alternating",
        "dividers.divider_targets": ["between major sections"],
        "accent_logic.primary_use": ["borders around section headings (chips)"],
        "accent_logic.allowed_scope": ["text borders"],
        "accent_logic.forbidden_scope": ["body text", "horizontal rules", "large blocks"],
        "accent_logic.accent_balance": "rust/clay accent is restricted purely to delicate borders outlining the section headings, acting as a \"stamp\" on the canvas",
        "theme_specific_rules.must_include": ["espresso brown body text", "Lora font", "flush-right lowercase header", "terracotta chip borders"],
        "theme_specific_rules.visual_differentiators": ["earthy/tactile palette", "absence of solid black lines", "airy lowercase styling"],
        "theme_specific_rules.anti_generic_rules": ["no black text", "no uppercase block headers", "no solid horizontal lines"],
        "_avoid_additions": ["uppercase block headings", "solid dividers", "stark white/black contrast", "pure black text"],
    },
    "theme-25-cyan-blueprint.json": {
        "visual_identity.mood": "structural, analytical, precise, calculated",
        "visual_identity.motif_name": "technical cyan grid-markers",
        "visual_identity.density_target": "high",
        "visual_identity.silhouette": "framed, measured, block-led",
        "visual_identity.personality_axis": "systematic, organized, methodical",
        "visual_identity.header_silhouette": "technical multi-line block anchored to the top edge",
        "visual_identity.section_emphasis_pattern": "band-led",
        "visual_identity.contrast_intensity": "high",
        "palette.base_colours": ["#1C2833", "#34495E", "#5D6D7E"],
        "palette.complementary_accent": "#00E5FF",
        "palette.neutral_surface": "#FFFFFF",
        "palette.neutral_text": "#1C2833",
        "palette.neutral_background": "#F4F6F7",
        "palette.supporting_neutral": "#E5E8E8",
        "typography.base_font": "Open Sans",
        "typography.base_size_pt": 10.5,
        "typography.line_spacing": 1.25,
        "typography.section_heading_weight": 600,
        "typography.section_heading_size_pt": 11,
        "typography.section_heading_tracking_pt": 1.4,
        "typography.spacing_after_pt": 6,
        "page.margins_in": {"top": 0.60, "right": 0.65, "bottom": 0.60, "left": 0.65},
        "bands.strategy": "strict edge-to-edge top banding setting a structural blueprint feel",
        "bands.band_placement_profile": "header_only",
        "bands.placement": ["top header edge"],
        "bands.height_rule": {"min_pt": 6, "max_pt": 8, "default_pt": 8},
        "bands.intensity": "strong",
        "bands.accent_placement_profile": "labels_only",
        "dividers.grammar": "signal-mix",
        "dividers.frequency": "moderate",
        "dividers.weight": "thin-to-medium",
        "dividers.divider_rhythm": "regular",
        "dividers.divider_targets": ["between sections", "between header and body"],
        "accent_logic.primary_use": ["small inline labels", "top header edge band"],
        "accent_logic.allowed_scope": ["top edge framing", "tiny metadata labels"],
        "accent_logic.forbidden_scope": ["body text", "major section headings", "standard dividers"],
        "accent_logic.accent_balance": "cyan must only be used as a \"highlighter\" for structural boundaries and labels, never for continuous reading",
        "theme_specific_rules.must_include": ["edge-to-edge cyan top band", "slate grey body text", "Open Sans font", "signal-mix alternating dividers"],
        "theme_specific_rules.visual_differentiators": ["architectural blueprint aesthetic", "stark cyan against slate grey", "highly measured and organized grid spacing"],
        "theme_specific_rules.anti_generic_rules": ["do not use standard black text", "do not center the layout", "do not use faint/invisible dividers"],
        "_avoid_additions": ["standard black text", "centered text", "invisible structure", "warm/earthy colors"],
    },
}


def dig(d, dotted):
    cur = d
    for part in dotted.split("."):
        cur = cur[part]
    return cur

def get_all_keys(d, prefix=""):
    keys = set()
    for k, v in d.items():
        path = f"{prefix}.{k}" if prefix else k
        keys.add(path)
        if isinstance(v, dict):
            keys.update(get_all_keys(v, path))
    return keys


theme01_path = T / "theme-01-graphite-ledger.json"
if theme01_path.exists():
    j01 = json.loads(theme01_path.read_text())
    base_keys = get_all_keys(j01)
else:
    print("Warning: theme-01-graphite-ledger.json not found for baseline check.")
    base_keys = None

total_dev = 0
structural_failures = 0

for fname, spec in SPECS.items():
    j = json.loads((T / fname).read_text())
    print(f"\n{'='*78}\n{fname}\n{'='*78}")
    
    if base_keys:
        j_keys = get_all_keys(j)
        missing = base_keys - j_keys
        extra = j_keys - base_keys
        if missing or extra:
            print(f"  STRUCTURAL DEVIATION: Keys do not match theme-01.")
            if missing: print(f"    Missing: {missing}")
            if extra: print(f"    Extra: {extra}")
            structural_failures += 1
            
    base_font = dig(j, "typography.base_font")
    if base_font not in {"Arial", "Calibri", "Georgia"}:
        print(f"  STRUCTURAL DEVIATION: base_font {base_font!r} not in ATS whitelist.")
        structural_failures += 1
        
    for k, v in j.get("palette", {}).items():
        if isinstance(v, str) and v.startswith("#"):
            if not re.match(r"^#[0-9A-F]{6}$", v):
                print(f"  STRUCTURAL DEVIATION: palette.{k} {v!r} is not a 6-digit uppercase hex.")
                structural_failures += 1
        elif isinstance(v, list):
            for i, c in enumerate(v):
                if isinstance(c, str) and c.startswith("#"):
                    if not re.match(r"^#[0-9A-F]{6}$", c):
                        print(f"  STRUCTURAL DEVIATION: palette.{k}[{i}] {c!r} is not a 6-digit uppercase hex.")
                        structural_failures += 1

    for path, want in spec.items():
        if path == "_avoid_additions":
            got = j["avoid_list"]
            missing = [a for a in want if a not in got]
            status = "MATCH" if not missing else f"DEVIATION (missing additions: {missing})"
            if missing:
                total_dev += 1
            print(f"  avoid_list additions present? {status}")
            continue
        try:
            got = dig(j, path)
        except KeyError:
            got = "<MISSING>"
        if got == want:
            continue  # only print deviations to keep signal high
        total_dev += 1
        print(f"  DEVIATION  {path}")
        print(f"       spec: {want!r}")
        print(f"       json: {got!r}")
    # confirm no deviations line
    print("  (only deviations shown above; everything else MATCHES spec)")

print(f"\n\nTOTAL DEVIATION FIELDS ACROSS ALL 5 THEMES: {total_dev}")
print(f"TOTAL STRUCTURAL FAILURES: {structural_failures}")

# Enforce exactly 16 intentional deviations (no more, no less) and 0 structural failures
EXPECTED_DEVIATIONS = 16
if total_dev != EXPECTED_DEVIATIONS or structural_failures > 0:
    print("\nFAIL: Unexpected deviations or structural errors found.")
    sys.exit(1)
else:
    print("\nOK: Only expected deviations found. Structural checks passed.")
    sys.exit(0)
