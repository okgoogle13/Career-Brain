---
name: theme-visual-preview-v3
description: Use to generate an HTML visual preview of ATS resume templates directly in the Claude Desktop/Web UI via Artifacts. Essential for Phase 0 aesthetic review before compiling or building Golden Master documents.
---

# Theme Visual Preview v3

## Overview

A dedicated skill for rendering ATS resume theme JSONs as print-accurate HTML previews so a human can rank them on look-and-feel. Because CLI tools cannot render or evaluate visual aesthetics, this skill leverages Claude's native Artifacts capability to generate a self-contained, side-by-side gallery of A4 mockups.

## When to Use

- Before compiling a batch of `theme-*.json` specs into v2.0 templates
- When designing a new theme and wanting to preview its color palette, typography, and contrast
- When doing Phase 0 Visual QA (as part of the Career Brain pipeline)

## How It Works

When triggered, this skill fetches the necessary context files and produces a single raw HTML/CSS artifact.

1. It requires the theme JSON files (e.g., `templates/theme-01-graphite-ledger.json`).
2. It uses `context/theme_viz_sample_content.md` as the dummy content.
3. It maps JSON styling tokens to CSS according to the rules in `context/theme_viz_render_spec.md`.

## Execution Prompt (For the LLM)

When the user asks to "preview themes" or "generate visual previews", immediately execute the following instructions:

<task>
Produce one self-contained HTML artifact (raw HTML + inline CSS — no React, no Tailwind, no external fonts, no JS) rendering the requested themes as A4 pages stacked vertically, each labeled with its theme name. Use the exact content from `context/theme_viz_sample_content.md` for every page; only the visual treatment changes.
</task>

<fidelity_rules>
Map each JSON field to CSS exactly — no approximations:
- Page box: `width:210mm; min-height:297mm;` `padding` = `page.margins_in` (in inches); `background` = `palette.neutral_surface`
- Body: `font-family` = `typography.base_font` + generic fallback; `font-size` = `base_size_pt pt`; `line-height` = `line_spacing` (unitless); `color` = `body_text_color`
- Section headings: `font-size`/`font-weight`/`letter-spacing` from `section_heading_*` (pt); color/transform/decoration from `section_heading_style`
- Bands: colored block at stated `placement`, height from `bands.height_rule` (pt)
- Dividers: `border-style` matches `dividers.grammar` (solid/dotted/dashed); weight and frequency as stated
- Accent (`complementary_accent`): headings, rules, bands, micro-markers ONLY — **never body text, never background fills** (`accent_logic.forbidden_scope` is a hard constraint)
- All hex codes exactly as given; no invented fonts; single column; no images or icons
</fidelity_rules>

<caveat>
The production builder is ATS-minimal: it applies font, sizes, colors, line-spacing, and heading borders — it does NOT emit decorative bands, dashed circuit rules, or chips. Rank on palette, font pairing, heading treatment, and tone. Decorative motifs may not survive into the final Google Doc. theme-02 (dark background) is a known ATS/print risk — flag it if it merits exclusion.
</caveat>

<output>
1. Generate the HTML artifact.
2. Present a table to the user with one row per theme: 1-line aesthetic verdict | visual tweaks & improvements | distinctiveness rating.
3. Ask the user to rank the themes and note any desired tweaks.
</output>

## Workflow

1. User triggers skill: "Preview themes 01 to 03"
2. LLM reads the specified theme JSONs from `templates/`
3. LLM reads `context/theme_viz_sample_content.md`
4. LLM outputs the HTML artifact and aesthetic table
5. User provides ranking/tweaks
6. Proceed to compilation and Golden Master build (via the `career-brain-skill-integration` workflow)
