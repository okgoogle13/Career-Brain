# Theme Extraction & Synthesis — Deep-Plan Spec

> **Objective:** Extract the strongest design elements from 8 external resume template PDFs and
> synthesize them into 3–4 distinct, production-ready Career Brain theme JSON files (v2.3 schema),
> using a two-phase model pipeline with design-critique skill chain.

---

## Background & Project Context

Career Brain is a career-justice tool for community-services and social-work contexts in Australia.
The `templates/` library contains two schema halves:

1. **Content/structure half (v2.0)** — 300–400-line production templates with `blocks[]`, tokens,
   cm margins, single-string fonts. These are what the pipeline consumes.
2. **Design-token half (v2.3)** — ~200-line themes (`theme-01…10`) with `visual_identity`, `bands`,
   `dividers`, `accent_logic`. These describe *how it looks*.

The canonical schema must eventually merge both halves. This spec covers **extracting new v2.3
design-token themes** from external inspiration PDFs, which will later be compiled to v2.0 for
production.

### Hard Constraints

- **ATS-safety is non-negotiable.** All outputs must be single-column, body-only content layer,
  ATS-safe fonts, no icons/images/text-boxes/headers-footers.
- **Model-agnostic outputs.** Claude is design-time only. Production runs on Google Gemini.
  All artifacts must be plain, portable JSON/markdown.
- **Google Docs compatible.** ATS-safe fonts available in Google Docs: `Arial`, `Calibri`,
  `Georgia`, `Times New Roman`.

---

## Source Material — 8 External Resume Template PDFs

Located in Google Drive at:
`~/Library/CloudStorage/GoogleDrive-nishantdougall@gmail.com/My Drive/Career stuff/Resume templates/`

| # | Filename | Shorthand |
|---|----------|-----------|
| 1 | `resume template less boring black and white.pdf` | Less Boring B&W |
| 2 | `resume template monochrome.pdf` | Monochrome |
| 3 | `resume template monochrome adobe express.pdf` | Monochrome Adobe |
| 4 | `resume template purple head.pdf` | Purple Head |
| 5 | `Resume template lilac.pdf` | Lilac |
| 6 | `Resume template modern black green.pdf` | Modern Black Green |
| 7 | `resume template black and white 2 column bold.pdf` | B&W 2-Col Bold |
| 8 | `Resume template black and red.pdf` | Black & Red |

---

## Two-Phase Pipeline

### Phase 1 — Gemini 3.1 Pro: Design Critique & Synthesis

**Model:** Gemini 3.1 Pro (via Google AI Studio or API)
**Input:** All 8 PDFs uploaded as multimodal context
**Task:** Run a design-critique skill chain:

#### Step 1: Critique & Analyze (internal reasoning)
- Analyze the layout, grid, spacing, and header silhouettes of all 8 PDFs.
- Critique their ATS-safety (flag two-column layouts, floating text boxes, icons).
- Identify the most striking color palettes, typography pairings, horizontal divider logic,
  and accent treatments.
- Score each template's strengths on: clarity, distinctiveness, accessibility, ATS-safety,
  and alignment with Career Brain's career-justice aims.

#### Step 2: Synthesize & Differentiate
- Amalgamate the strongest elements across the library into **3–4 cohesive, distinct composite
  design concepts**. Do NOT create a 1:1 per-file extraction.
- Each concept must be visually distinct from the others AND from the existing 10 themes
  in `templates/theme-01…10.json`.
- Example concept archetypes (adapt based on what the PDFs actually contain):
  1. *The Executive Minimalist* — Monochrome, ledger lines, serif headers
  2. *The Bold Contemporary* — Strong top header bands, green/teal accents, sans-serif
  3. *The Subtle Modern* — Lilac/Purple subtle accents, border-left emphasis, high whitespace
  4. *The High-Impact Hybrid* — Red/Black palette, high contrast, divider-heavy

#### Step 3: Output Format (text specifications, NOT JSON yet)
For each of the 3–4 synthesized concepts, output a detailed design specification covering:
- **Visual Identity:** Mood, motif, silhouette, and personality
- **Palette (Exact Hex Codes):** Base text colors, primary accents, background tints, neutral surfaces
- **Typography:** ATS-safe font families, heading weights, and spacing
- **Layout & Rhythm:** Margin estimations, band strategies, divider grammar
- **Accent Logic:** Where color is allowed (headings, lines) vs forbidden (body text)
- **Anti-Generic Rules:** Design guardrails to keep the theme premium and distinct
- **Source Attribution:** Which PDFs contributed which elements to this concept

---

### Phase 2 — Claude Opus 4.8: Strict JSON Schema Extraction

**Model:** Claude Opus 4.8 (via Claude Desktop)
**Input:** Phase 1 text output from Gemini + existing theme references
**Task:** Translate each text-based design specification into valid, strictly formatted JSON
blocks conforming to Career Brain Theme Specification v2.3.

#### Existing Schema Reference

The output JSON must match the structure used by `templates/theme-01-graphite-ledger.json` and
`templates/MASTER_SCHEMA_V2_3.json`. Key sections:

```json
{
  "schema_version": "2.3",
  "template_id": "theme_<snake_case_short_name>",
  "tier": 1,
  "tier_label": "ATS Standard",
  "doc_type": "resume",
  "target_sector": [],
  "region": "AU",
  "placeholder_schema": "PLACEHOLDERSCHEMAV2",
  "description": "<one sentence>",
  "visual_identity": {
    "theme_name": "<Human Readable>",
    "mood": "<adjectives>",
    "motif_name": "<visual hallmark>",
    "density_target": "<low|medium|high>",
    "silhouette": "<layout description>",
    "personality_axis": "<adjectives>",
    "header_silhouette": "<header block style>",
    "section_emphasis_pattern": "<divider-led|block-led|accent-led>",
    "contrast_intensity": "<low|medium|high>"
  },
  "ats_constraints": { "columns": 1, "allows_tables": false, "..." : "..." },
  "palette": {
    "base_colours": ["#HEX1", "#HEX2", "#HEX3"],
    "complementary_accent": "#HEX",
    "neutral_surface": "#FFFFFF",
    "neutral_text": "#HEX",
    "neutral_background": "#FFFFFF",
    "supporting_neutral": "#HEX"
  },
  "typography": { "base_font": "<font>", "base_size_pt": 10.5, "..." : "..." },
  "page": { "margins_in": { "top": 0.65, "..." : "..." }, "..." : "..." },
  "bands": { "strategy": "<>", "placement": [], "..." : "..." },
  "dividers": { "grammar": "<>", "frequency": "<>", "..." : "..." },
  "accent_logic": { "primary_use": [], "..." : "..." },
  "theme_specific_rules": { "must_include": [], "..." : "..." },
  "section_heading_style": { "font_color": "#HEX", "..." : "..." },
  "body_text_color": "#HEX",
  "muted_text_color": "#HEX",
  "skills_background_tint": "#HEX",
  "avoid_list": []
}
```

#### Differentiation Constraint

Each new theme must differ from ALL existing themes in `templates/` on at least 3 of:
- Band placement profile
- Divider rhythm / grammar
- Accent placement profile
- Header silhouette
- Section emphasis pattern
- Palette mood (monochrome vs warm vs cool vs high-contrast)

---

## Output Artifacts

| Phase | Produces | Location |
|-------|----------|----------|
| Phase 1 (Gemini) | 3–4 text design specifications with critique notes | `planning/phase1-design-synthesis.md` |
| Phase 2 (Claude Opus) | 3–4 validated v2.3 JSON theme files | `templates/theme-11-*.json`, `theme-12-*.json`, etc. |

---

## Quality Gates

1. **No two new themes share the same band_placement_profile + divider_rhythm combination.**
2. **All hex codes are 6-digit, uppercase (#2F855A not #2f855a or #2F8).**
3. **Font families are ATS-safe and Google Docs compatible.**
4. **No `avoid_list` items appear in the theme's own design tokens.**
5. **Each theme's `visual_differentiators` are genuinely visible at a glance** — not just
   palette swaps.

---

## Existing Theme Library (for non-overlap verification)

| Theme | Motif | Palette Mood |
|-------|-------|-------------|
| theme-01 Graphite Ledger | horizontal ledger lines | monochrome greys |
| theme-02 Midnight Blueprint | dark header bar | dark navy |
| theme-03 Citrus Edge | citrus accent lines | warm yellow-orange |
| theme-04 Emerald Transit | transit-inspired bands | green |
| theme-05 Copper Teal Circuit | circuit patterns | copper + teal |
| theme-06 Violet Signal | signal-inspired | violet |
| theme-07 Solar Gradient | gradient header | warm solar |
| theme-08 Nordic Neon | neon accent | cool blue-neon |
| theme-09 Terracotta Service | service-inspired | terracotta |
| theme-10 Rainbow Minimal | subtle rainbow | multicolor minimal |
