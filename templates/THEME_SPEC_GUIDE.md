# Theme Spec Guide

> Source of truth for the `templates/` theme library.  
> All new themes must follow this guide. Before a Golden Master is built they must pass `tools/validate_templates_v2.py <path>` (offline); after it is built, `tools/audit_doc_style.py <DOC_ID> --theme <path>` must print `STYLE OK`.
> Stage order and the skill that owns each check: `.claude/skills/theme-gate/SKILL.md` ("Run order").

---

## Current Theme Library

Registration status and Doc IDs live in `config/doc_templates.json`, not here.

| File | Doc Type | Name | Font (body / heading) | Palette | Tier | Target Sector |
|---|---|---|---|---|---|---|
| `resume_professional_classic_v1.json` | resume | Professional Classic | Times New Roman | Deep Navy / Charcoal | 1 — ATS Standard | Finance, law, corporate, senior mgmt |
| `resume_contemporary_professional_v1.json` | resume | Contemporary Professional | Calibri | Forest Green / Sage | 1 — ATS Clean | Community services, NFP, government, healthcare |
| `resume_modern_minimalist_v1.json` | resume | Modern Minimalist | Arial | Slate Blue / Teal | 2 — ATS Modern | Tech, design, startups |
| `resume_warm_impact_v1.json` | resume | Warm Impact | Calibri | Ink Gold / Waratah Red | 2 — ATS Bold | Community services, career-transition |
| `resume_chronological_v1.json` | resume | Chronological | Times New Roman | Deep Navy / Charcoal | 1 — ATS Standard | Finance, law, corporate |
| `resume_hybrid_v1.json` | resume | Hybrid | Calibri | Forest Green / Sage | 1 — ATS Clean | Government, community services |
| `resume_graphite_ledger_v1.json` | resume | Graphite Ledger | Georgia / Arial | Graphite / Grey | 1 — ATS Clean | Finance, law, corporate, government |
| `resume_midnight_blueprint_v1.json` | resume | Midnight Blueprint | Arial | Deep Navy / Cyan | 2 — ATS Modern | Tech, engineering, specialty |
| `resume_citrus_edge_v1.json` | resume | Citrus Edge | Calibri / Arial | Charcoal / Orange | 2 — ATS Modern | Community services, social work |
| `resume_emerald_transit_v1.json` | resume | Emerald Transit | Calibri / Georgia | Emerald / Mint | 1 — ATS Clean | Health, transport, logistics |
| `resume_copper_teal_circuit_v1.json` | resume | Copper Teal Circuit | Arial | Copper / Teal | 2 — ATS Modern | Engineering, tech, architecture |
| `resume_violet_signal_v1.json` | resume | Violet Signal | Georgia / Arial | Violet / Amethyst | 1 — ATS Standard | Creative, arts, marketing |
| `resume_solar_gradient_v1.json` | resume | Solar Gradient | Georgia | Brown / Warm Cream | 1 — ATS Standard | Non-profit, education, community |
| `resume_nordic_neon_v1.json` | resume | Nordic Neon | Arial | Cyan / Teal | 2 — ATS Modern | Design, tech, startups |
| `resume_terracotta_service_v1.json` | resume | Terracotta Service | Georgia | Terracotta / Cream | 1 — ATS Standard | Community services, social work |
| `resume_rainbow_minimal_v1.json` | resume | Rainbow Minimal | Calibri / Arial | Slate / Multi-color | 2 — ATS Modern | General, entry-level, tech |
| `resume_terminal_signal_v1.json` | resume | Terminal Signal | Arial | Green / Charcoal | 2 — ATS Modern | Dev, IT, cybersecurity |
| `resume_horizon_edge_v1.json` | resume | Horizon Edge | Arial | Navy / Coral | 2 — ATS Modern | Media, communication, corporate |
| `resume_broadside_press_v1.json` | resume | Broadside Press | Georgia / Arial | Crimson / Black | 1 — ATS Standard | Editorial, publishing, policy |
| `resume_clay_canvas_v1.json` | resume | Clay Canvas | Georgia | Clay / Espresso | 1 — ATS Standard | Artisanal, design, education |
| `resume_cyan_blueprint_v1.json` | resume | Cyan Blueprint | Arial | Cyan / Charcoal | 2 — ATS Modern | Tech, engineering, corporate |
| `cover_letter_base_v1.json` | cover_letter | Cover Letter Base | Times New Roman | Deep Navy | 1 — ATS Standard | All sectors |
| `cover_letter_government_v1.json` | cover_letter | Cover Letter Government | Calibri | Forest Green | 1 — ATS Clean | Government, public service |
| `cover_letter_nfp_v1.json` | cover_letter | Cover Letter NFP | Calibri | Ink Gold / Waratah Red | 2 — ATS Bold | NFP, community services |
| `cover_letter_private_v1.json` | cover_letter | Cover Letter Private | Arial | Slate Blue / Teal | 2 — ATS Modern | Private sector, tech, design |
| `ksc_standard_v2.json` | ksc | KSC Standard v2 | Calibri | Forest Green / Sage | 1 — ATS Clean | Government, community services, NFP |

**Excluded (not migrated):**
- `theme3` (Bold Executive) — two-column layout, ATS-unsafe
- `theme5` (Vibrant Creative) — two-column layout, ATS-unsafe
- `ksc_base_v1.json` — Archived (Use `ksc_standard_v2.json`)

These exist in `archive/` (local archive, not in repo) as design references. They may be built as human-submission-only variants in future if a `--no-ats` flag is added to `tools/generate_document.py`.

---

## Required JSON Schema (schema_version 2.0)

Every theme file must contain these top-level keys in this order:

```json
{
  "schema_version": "2.0",
  "template_id": "<doc_type>_<name>_v<N>",
  "tier": 1,
  "tier_label": "<human label>",
  "doc_type": "resume",
  "target_sector": ["<sector>"],
  "region": "AU",
  "placeholder_schema": "PLACEHOLDER_SCHEMA_V2",
  "description": "<one sentence: visual identity, palette, font, ATS status>",

  "ats_constraints": { ... },
  "palette": { ... },
  "typography": { ... },
  "page": { ... },
  "blocks": [ ... ]
}
```

### `ats_constraints` (required)

```json
{
  "columns": 1,
  "allows_tables": false,
  "allows_images": false,
  "allows_text_boxes": false,
  "allows_headers_footers": false,
  "font_family": "<ATS-safe font>",
  "content_layer": "body_only",
  "forbidden_glyphs": ["•", "✔", "★", "❖", "●", "✅", "❌", "|"]
}
```

Source for `forbidden_glyphs`: `config/ats_rules.json` `vocabulary.forbidden_characters` (plus `forbidden_char_ranges`). Do not copy the list from this example. Existing themes predate `!` being added to that file and omit it.

**ATS-safe fonts:** the canonical list is the `font_family` enum in `templates/schema_v2_0.json`. `base_font`, `ats_constraints.font_family` and `heading_font_family` must all come from it. Helvetica is not reliably available in Google Docs — use Arial as fallback.

### `palette` (required)

Named hex colors. Use descriptive keys (`forest_green`, `teal_accent`) not role keys (`primary`, `secondary`). All colors must be full 6-digit hex (`#2F855A` not `#2f855a`).

### `typography` (required)

```json
{
  "base_font": "<must match ats_constraints.font_family>",
  "base_size_pt": 11,
  "line_spacing": 1.15,
  "spacing_after_pt": 6,
  "section_heading_tracking_pt": 0,
  "section_heading_size_pt": 13
}
```

### `page` (required)

Margins in cm. Background must be white or near-white for ATS safety: every RGB channel ≥ `F0` hex and the highest minus lowest channel ≤ 16. `#FFFFFF`, `#FAFAFA` and `#FAF8F5` pass; `#EEEEEE` and `#FFF5E0` fail. The builder only emits a page background when it is not `#FFFFFF`.

```json
{
  "margin_top_cm": 1.9,
  "margin_bottom_cm": 1.9,
  "margin_left_cm": 1.9,
  "margin_right_cm": 1.9,
  "background_color": "#FFFFFF"
}
```

### `blocks[]` (required)

Ordered list of content blocks. The required blocks depend on the `doc_type`:

**For `resume` themes (8 blocks required in order):**

| Order | block_id | type |
|---|---|---|
| 1 | `name_header` | `name_block` |
| 2 | `contact_info` | `contact_block` |
| 3 | `role_headline` | `headline_block` |
| 4 | `summary_section` | `summary_block` |
| 5 | `skills_section` | `skills_block` |
| 6 | `experience_section` | `experience_block` |
| 7 | `education_section` | `education_block` |
| 8 | `certifications_section` | `certifications_block` |

**`experience_block` must define exactly 6 roles** with tokens `{{ROLE_N_TITLE}}`, `{{ROLE_N_ORG}}`, `{{ROLE_N_DATES}}`, and 4 bullets each — matching `PLACEHOLDER_SCHEMA_V2` in `generate_document.py`.

**For `cover_letter` themes (required blocks):**
- `name_header`
- `contact_info`
- `employer_info`
- `salutation`
- `body_paragraphs`
- `closing`

**For `ksc` themes (required blocks):**
- `name_header`
- `contact_info`
- `application_meta`
- `criteria_responses`

Resume and cover-letter structure is defined by the theme JSON `blocks[]`; `build_golden_master.py` builds from it. Only KSC has a Markdown spec (`context/specs/ksc_standard_v2_spec.md`, via `gold-template-builder-v3`).

---

## `visualConfig` Rules

### Bullet glyph
**Always `-`**. Unicode bullets (`•`, `●`, `◆`) are in `forbidden_glyphs` and will fail `audit_doc_style.py`.

### Section heading decoration
Two permitted styles:
1. `border_bottom` — horizontal rule below the heading (Classic, Contemporary)
2. `border_left` — vertical accent bar left of heading text (Modern Minimalist)

Do not combine both on the same heading. Both are emitted as solid lines only; KSC criterion headings take no border.

### What the builder emits

`tools/build_golden_master.py` builds the Golden Master from the compiled JSON and reads only: fonts, sizes, weights and colours; line spacing and space below; margins; page background; solid heading bottom rule or left bar; the name rule; skills-block shading; and the literal `heading` text of each block (so heading case comes from that text, e.g. `SUMMARY` vs `Summary`).

It does **not** read `text_transform`, `letter_spacing_pt`, `text_align`, contact `separator`, skills `layout`/`display`, block `order` (section order is fixed), or any v2.3 `bands`, `dividers` or `accent_logic`. Values in those fields do not change the document, so they do not make a theme distinct (theme-gate line A4).

### Background fills
Permitted on `skills_section.container` only. Use a light tint from the palette (`#F0FFF4`, `#FDF5DC`, `#E6FFFA`). All other blocks take the page background.

### Font colors
- Every text colour must meet WCAG AA against its actual background (the page, or the skills fill for text inside it): 4.5:1, or 3:1 for text ≥ 18pt or ≥ 14pt bold. `.venv/bin/python tools/theme_fingerprint.py <path>` lists failures under `contrast_failures`; it must be empty.
- Headings: palette primary color (green, navy, teal), subject to the contrast rule — bright accents (`#22C55E`, `#38B2AC`, `#F472B6`) fail on white.
- Body text: `#1A1A1A` or `#2D3748` (near-black)
- Muted / meta text: `#4A5568` (7.5:1 on white). Do not use `#718096`: 4.02:1 on white, which fails AA.
- Never use pure black `#000000` (renders harsh in print) or pure white on white

---

## Design Standard

Every theme and family must meet S1–S6. Rules use only fields the builder emits (see "What the builder emits"); anything else does not reach the document and cannot satisfy a rule. Buckets come from `config/theme_fingerprint.json`; read values with `.venv/bin/python tools/theme_fingerprint.py <path>`. Record the result in the family's `THEME_BRIEF_FORM.md` `STANDARD_CHECK`.

**S1 Hierarchy** — four readable levels: name > section heading > role title > body.
- `name_scale` is `prominent` or `dominant`.
- `heading_scale` is `moderate` or `strong`. If `flat`, the heading must differ from body on at least two of: weight, case, colour, rule.
- Role title is bold or larger than body; org and dates use the muted colour.

**S2 Typography** — body 10.5–12pt; at most two families. A second family must be a different class (serif + sans); two sans or two serif families is a FAIL.

**S3 Colour** — the accent has one role (headings, or rules, or skills fill) and never colours body text. Body `#1A1A1A` or `#2D3748`; meta `#4A5568`; contrast per "Font colors".

**S4 Rhythm** — `line_spacing` 1.15–1.35; `spacing_after_pt` 4–8; margins 1.5–2.5 cm with left = right. One value per role: all section headings share size and spacing; all bullets share spacing.

**S5 Page fit** (rendered, not offline) — with the stress content in `context/theme_viz_sample_content.md`: resume ≤ 2 A4 pages, cover letter 1 page, no section or criterion heading alone at a page foot, no bullet ending in a one-word line.

**S6 Family** — members share `base_font`, heading font, heading colour hue, `name_header` styling and margins (±0.3 cm). The cover letter may sit one `line_rhythm` bucket airier. KSC `criteria_responses.visualConfig.criterion_text` reuses the resume section heading's font, weight and colour.

**Banned (each is a FAIL):**
- Section heading indistinguishable from body (fails S1)
- Same-class font pair (fails S2)
- Accent on body text, or in more than one role (fails S3)
- Identity that relies only on non-emitted fields (`bands`, `dividers`, `accent_logic`, `text_transform`, `letter_spacing_pt`)
- Generic name (`modern`, `minimal`, `clean`, `professional`) with no structural signature

---

## Naming Convention

```
<doc_type>_<family_id>_v<N>.json
```

`family_id` is lowercase `snake_case` and names the sector or strategy (`state_gov_panel`), never the look (`teal_wave`). Example family: `resume_state_gov_panel_v1.json`, `cover_letter_state_gov_panel_v1.json`, `ksc_state_gov_panel_v1.json`.

Existing files keep their current names: renaming breaks registry `theme` paths and `compile_theme.py`'s `resume_<suffix>_v1.json` output name.

Increment `v<N>` for a visual revision within the same identity. Create a new `family_id` only when strategy, audience or layout identity changes.

---

## Adding a New Theme — Checklist

```
[ ] Fill templates/THEME_BRIEF_FORM.md for the family (purpose, decisions, shared identity)
[ ] Start the theme JSON from the brief's SHARED_IDENTITY and DECISIONS
[ ] Update template_id, tier, tier_label, target_sector, description
[ ] Define palette with named hex colors
[ ] Set font_family in both ats_constraints and typography.base_font (must match)
[ ] Confirm all 8 blocks present with correct order
[ ] Confirm all ROLE_N tokens present (6 roles × 4 bullets)
[ ] Confirm bullet glyph is "-" in experience_section.visualConfig.bullet.glyph
[ ] No character from config/ats_rules.json forbidden_characters / forbidden_char_ranges appears anywhere in the file
[ ] Check against Design Standard S1–S4 and S6; record results in the brief's STANDARD_CHECK
[ ] Run: .venv/bin/python tools/validate_templates_v2.py templates/<new_file>.json  → PASS
[ ] Run: .venv/bin/python tools/theme_fingerprint.py templates/<new_file>.json  → contrast_failures empty
[ ] Run the theme-gate skill, Stage A → PASS
[ ] Build: .venv/bin/python tools/build_golden_master.py templates/<new_file>.json  (--dry-run first; live build calls Google)
[ ] Run: .venv/bin/python tools/audit_doc_style.py <DOC_ID> --theme templates/<new_file>.json  → STYLE OK
[ ] Run the theme-gate skill, Stage B → PASS
[ ] Register Doc ID in config/doc_templates.json under resume.variants.<name>
```

---

## Relationship to `doc_templates.json`

Theme JSON files in `templates/` are **design specifications only**. They do not contain Google Doc IDs. The registry lives in `config/doc_templates.json`:

```json
{
  "resume": {
    "variants": {
      "chronological": {
        "template_doc_id": "...",
        "theme": "templates/resume_professional_classic_v1.json"
      },
      "warm_impact": {
        "template_doc_id": "REPLACE_WITH_DOC_ID",
        "theme": "templates/resume_warm_impact_v1.json"
      }
    }
  }
}
```

The `theme` field is currently informational — `generate_document.py` does not yet load it at runtime. This is tracked as Priority 6 in `deprecated_artifact_recovery.md`.

---

## Relationship to `audit_doc_style.py`

`tools/audit_doc_style.py` supports `--theme <path>` and loads font family, font sizes, line spacing,
and colour expectations directly from the theme JSON. Pass `--theme` for every themed Golden
Master audit. Unthemed/KSC templates are audited without the flag (Calibri defaults apply).
It checks that the doc matches its theme; it does not check the font allowlist, contrast or
background — those are offline checks (`validate_templates_v2.py`, `theme_fingerprint.py`).

See `.claude/skills/docs_style_auditor_v3/SKILL.md` for the full protocol.
