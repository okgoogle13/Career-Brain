# Theme Spec Guide

> Source of truth for the `templates/` theme library.  
> All new themes must follow this guide. Before a Golden Master is built they must pass `tools/validate_templates_v2.py <path>` (offline); after it is built, `tools/audit_doc_style.py <DOC_ID> --theme <path>` must print `STYLE OK`.
> Stage order and the skill that owns each check: `.claude/skills/career_brain_skill_integration_v3/SKILL.md`.

---

## Current Theme Library

| File | Doc Type | Name | Font (body / heading) | Palette | Tier | Target Sector | Status |
|---|---|---|---|---|---|---|---|
| `resume_professional_classic_v1.json` | resume | Professional Classic | Times New Roman | Deep Navy / Charcoal | 1 — ATS Standard | Finance, law, corporate, senior mgmt | ✅ Registered |
| `resume_contemporary_professional_v1.json` | resume | Contemporary Professional | Calibri | Forest Green / Sage | 1 — ATS Clean | Community services, NFP, government, healthcare | ✅ Registered |
| `resume_modern_minimalist_v1.json` | resume | Modern Minimalist | Arial | Slate Blue / Teal | 2 — ATS Modern | Tech, design, startups | ✅ Registered |
| `resume_warm_impact_v1.json` | resume | Warm Impact | Calibri | Ink Gold / Waratah Red | 2 — ATS Bold | Community services, career-transition | ✅ Registered |
| `resume_chronological_v1.json` | resume | Chronological | Times New Roman | Deep Navy / Charcoal | 1 — ATS Standard | Finance, law, corporate | ✅ Registered |
| `resume_hybrid_v1.json` | resume | Hybrid | Calibri | Forest Green / Sage | 1 — ATS Clean | Government, community services | ✅ Registered |
| `resume_graphite_ledger_v1.json` | resume | Graphite Ledger | Georgia / Arial | Graphite / Grey | 1 — ATS Clean | Finance, law, corporate, government | ✅ Registered |
| `resume_midnight_blueprint_v1.json` | resume | Midnight Blueprint | Arial | Deep Navy / Cyan | 2 — ATS Modern | Tech, engineering, specialty | ✅ Registered |
| `resume_citrus_edge_v1.json` | resume | Citrus Edge | Calibri / Arial | Charcoal / Orange | 2 — ATS Modern | Community services, social work | ✅ Registered |
| `resume_emerald_transit_v1.json` | resume | Emerald Transit | Calibri / Georgia | Emerald / Mint | 1 — ATS Clean | Health, transport, logistics | ✅ Registered |
| `resume_copper_teal_circuit_v1.json` | resume | Copper Teal Circuit | Arial | Copper / Teal | 2 — ATS Modern | Engineering, tech, architecture | ✅ Registered |
| `resume_violet_signal_v1.json` | resume | Violet Signal | Georgia / Arial | Violet / Amethyst | 1 — ATS Standard | Creative, arts, marketing | ✅ Registered |
| `resume_solar_gradient_v1.json` | resume | Solar Gradient | Georgia | Brown / Warm Cream | 1 — ATS Standard | Non-profit, education, community | ✅ Registered |
| `resume_nordic_neon_v1.json` | resume | Nordic Neon | Arial | Cyan / Teal | 2 — ATS Modern | Design, tech, startups | ✅ Registered |
| `resume_terracotta_service_v1.json` | resume | Terracotta Service | Georgia | Terracotta / Cream | 1 — ATS Standard | Community services, social work | ✅ Registered |
| `resume_rainbow_minimal_v1.json` | resume | Rainbow Minimal | Calibri / Arial | Slate / Multi-color | 2 — ATS Modern | General, entry-level, tech | ✅ Registered |
| `resume_terminal_signal_v1.json` | resume | Terminal Signal | Arial | Green / Charcoal | 2 — ATS Modern | Dev, IT, cybersecurity | ✅ Registered |
| `resume_horizon_edge_v1.json` | resume | Horizon Edge | Arial | Navy / Coral | 2 — ATS Modern | Media, communication, corporate | ✅ Registered |
| `resume_broadside_press_v1.json` | resume | Broadside Press | Georgia / Arial | Crimson / Black | 1 — ATS Standard | Editorial, publishing, policy | ✅ Registered |
| `resume_clay_canvas_v1.json` | resume | Clay Canvas | Georgia | Clay / Espresso | 1 — ATS Standard | Artisanal, design, education | ✅ Registered |
| `resume_cyan_blueprint_v1.json` | resume | Cyan Blueprint | Arial | Cyan / Charcoal | 2 — ATS Modern | Tech, engineering, corporate | ✅ Registered |
| `cover_letter_base_v1.json` | cover_letter | Cover Letter Base | Times New Roman | Deep Navy | 1 — ATS Standard | All sectors | ✅ Registered |
| `cover_letter_government_v1.json` | cover_letter | Cover Letter Government | Calibri | Forest Green | 1 — ATS Clean | Government, public service | ✅ Registered |
| `cover_letter_nfp_v1.json` | cover_letter | Cover Letter NFP | Calibri | Ink Gold / Waratah Red | 2 — ATS Bold | NFP, community services | ✅ Registered |
| `cover_letter_private_v1.json` | cover_letter | Cover Letter Private | Arial | Slate Blue / Teal | 2 — ATS Modern | Private sector, tech, design | ✅ Registered |
| `ksc_standard_v2.json` | ksc | KSC Standard v2 | Calibri | Forest Green / Sage | 1 — ATS Clean | Government, community services, NFP | ✅ Registered |

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

**ATS-safe fonts (canonical list; also the `font_family` enum in `schema_v2_0.json`):** `Arial`, `Calibri`, `Helvetica`, `Verdana`, `Tahoma`, `Trebuchet MS`, `Century Gothic`, `Gill Sans`, `Lucida Sans`, `Lucida Grande`, `Garamond`, `Georgia`, `Cambria`, `Times New Roman`, `Century Schoolbook`, `New Century Schoolbook`, `Palatino`, `Book Antiqua`. `base_font`, `ats_constraints.font_family` and `heading_font_family` must all come from this list. Helvetica is not reliably available in Google Docs — use Arial as fallback.

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

It does **not** read `text_transform`, `letter_spacing_pt`, `text_align`, contact `separator`, skills `layout`/`display`, block `order` (section order is fixed), or any v2.3 `bands`, `dividers` or `accent_logic`. Values in those fields do not change the document, so they do not make a theme distinct (see `.claude/skills/theme-divergence-auditor`).

### Background fills
Permitted on `skills_section.container` only. Use a light tint from the palette (`#F0FFF4`, `#FDF5DC`, `#E6FFFA`). All other blocks take the page background.

### Font colors
- Every text colour must meet WCAG AA against its actual background (the page, or the skills fill for text inside it): 4.5:1, or 3:1 for text ≥ 18pt or ≥ 14pt bold. `.venv/bin/python tools/theme_fingerprint.py <path>` lists failures under `contrast_failures`; it must be empty.
- Headings: palette primary color (green, navy, teal), subject to the contrast rule — bright accents (`#22C55E`, `#38B2AC`, `#F472B6`) fail on white.
- Body text: `#1A1A1A` or `#2D3748` (near-black)
- Muted / meta text: `#4A5568` (7.5:1 on white). Do not use `#718096`: 4.02:1 on white, which fails AA.
- Never use pure black `#000000` (renders harsh in print) or pure white on white

---

## Naming Convention

```
<doc_type>_<name>_v<N>.json
```

Examples:
- `resume_professional_classic_v1.json`
- `cover_letter_warm_impact_v1.json`  *(future)*
- `ksc_contemporary_professional_v1.json`  *(future)*

Increment `v<N>` for breaking changes to an existing theme's layout. Create a new theme file for a new visual identity.

---

## Adding a New Theme — Checklist

```
[ ] Copy an existing theme file as your starting point
[ ] Update template_id, tier, tier_label, target_sector, description
[ ] Define palette with named hex colors
[ ] Set font_family in both ats_constraints and typography.base_font (must match)
[ ] Confirm all 8 blocks present with correct order
[ ] Confirm all ROLE_N tokens present (6 roles × 4 bullets)
[ ] Confirm bullet glyph is "-" in experience_section.visualConfig.bullet.glyph
[ ] No character from config/ats_rules.json forbidden_characters / forbidden_char_ranges appears anywhere in the file
[ ] Run: .venv/bin/python tools/validate_templates_v2.py templates/<new_file>.json  → PASS
[ ] Run: .venv/bin/python tools/theme_fingerprint.py templates/<new_file>.json  → contrast_failures empty
[ ] Run the output-quality-gate skill, Stage A → APPROVE
[ ] Build: .venv/bin/python tools/build_golden_master.py templates/<new_file>.json  (--dry-run first; live build calls Google)
[ ] Run: .venv/bin/python tools/audit_doc_style.py <DOC_ID> --theme templates/<new_file>.json  → STYLE OK
[ ] Run the output-quality-gate skill, Stage B → APPROVE
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
