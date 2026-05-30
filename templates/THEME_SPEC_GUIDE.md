# Theme Spec Guide

> Source of truth for the `templates/` theme library.  
> All new themes must follow this guide and be validated by `tools/audit_doc_style.py --theme <path>` before a Golden Master is built.

---

## Current Theme Library

| File | Doc Type | Name | Font | Palette | Tier | Target Sector | Status |
|---|---|---|---|---|---|---|---|
| `resume_professional_classic_v1.json` | resume | Professional Classic | Times New Roman | Deep Navy / Charcoal | 1 — ATS Standard | Finance, law, corporate, senior mgmt | ✅ Registered |
| `resume_contemporary_professional_v1.json` | resume | Contemporary Professional | Calibri | Forest Green / Sage | 1 — ATS Clean | Community services, NFP, government, healthcare | ✅ Registered |
| `resume_modern_minimalist_v1.json` | resume | Modern Minimalist | Arial | Slate Blue / Teal | 2 — ATS Modern | Tech, design, startups | ✅ Registered |
| `resume_warm_impact_v1.json` | resume | Warm Impact | Calibri | Ink Gold / Waratah Red | 2 — ATS Bold | Community services, career-transition | ✅ Registered |
| `resume_chronological_v1.json` | resume | Chronological | Times New Roman | Deep Navy / Charcoal | 1 — ATS Standard | Finance, law, corporate | ✅ Registered |
| `resume_hybrid_v1.json` | resume | Hybrid | Calibri | Forest Green / Sage | 1 — ATS Clean | Government, community services | ✅ Registered |
| `cover_letter_base_v1.json` | cover_letter | Cover Letter Base | Times New Roman | Deep Navy | 1 — ATS Standard | All sectors | ✅ Registered |
| `cover_letter_government_v1.json` | cover_letter | Cover Letter Government | Calibri | Forest Green | 1 — ATS Clean | Government, public service | ✅ Registered |
| `cover_letter_nfp_v1.json` | cover_letter | Cover Letter NFP | Calibri | Ink Gold / Waratah Red | 2 — ATS Bold | NFP, community services | ✅ Registered |
| `cover_letter_private_v1.json` | cover_letter | Cover Letter Private | Arial | Slate Blue / Teal | 2 — ATS Modern | Private sector, tech, design | ✅ Registered |
| `ksc_base_v1.json` | ksc | KSC Base | Calibri | Forest Green | 1 — ATS Clean | AU public service | ✅ Registered |

**Excluded (not migrated):**
- `theme3` (Bold Executive) — two-column layout, ATS-unsafe
- `theme5` (Vibrant Creative) — two-column layout, ATS-unsafe

These exist in `archive/` as design references. They may be built as human-submission-only variants in future if a `--no-ats` flag is added to `tools/generate_document.py`.

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

**ATS-safe fonts (Google Docs available):** `Calibri`, `Arial`, `Times New Roman`, `Helvetica` (use Arial as fallback — Helvetica is not reliably available in Google Docs).

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

Margins in cm. Background must be `#FFFFFF` or `#FAFAFA` for ATS safety.

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

Do not combine both on the same heading.

### Background fills
Permitted on `skills_section.container` only. Use a light tint from the palette (`#F0FFF4`, `#FDF5DC`, `#E6FFFA`). All other blocks must use `#FFFFFF` or `#FAFAFA`.

### Font colors
- Headings: palette primary color (green, navy, teal)
- Body text: `#1A1A1A` or `#2D3748` (near-black)
- Muted / meta text: `#718096` or `#4A5568`
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
[ ] No forbidden_glyphs appear anywhere in the file
[ ] Run: python3 tools/audit_doc_style.py --theme templates/<new_file>.json
[ ] Build the Golden Master Google Doc using the visualConfig as the build spec
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

See `.claude/skills/docs_style_auditor_v3/SKILL.md` for the full protocol.
