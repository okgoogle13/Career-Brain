---
name: docs-style-auditor-v3
description: Use when verifying that a Career Brain Google Docs Golden Master template is structurally and typographically compliant before a live pipeline run — catches font, spacing, heading style, and layout violations that LLM review cannot reliably detect.
---

# Docs Style Auditor v3

## Overview

Runs a mechanical Python audit against the live Google Docs API payload. Zero inference — only explicit deviations in the document's API response are flagged. Replaces LLM-based style review, which is prone to fabricated PASS results.

**Theme-aware:** When auditing a themed resume Golden Master, always pass the theme JSON so the auditor checks against the correct font, sizes, and spacing — not Calibri defaults.

## When to Use

- Before registering a new Golden Master Doc ID in `doc_templates.json`
- After editing a Golden Master in Google Docs (any formatting change)
- When a dry-run shows unexpected output and the template is suspected

## Rules Enforced

### Default (KSC / unthemed templates)

| Rule | Expected value |
|---|---|
| Font family | Calibri (all text runs) |
| Font size — NORMAL_TEXT | 11pt |
| Font size — HEADING_1 / TITLE | 14pt |
| Line spacing | 115% (1.15) |
| Space below paragraph | 6pt |
| Heading style | Native HEADING_1 or HEADING_2 — NOT bolded NORMAL_TEXT |
| Tables | 0 |
| Inline images / objects | 0 |

### Theme-specific overrides (resume variants)

When a theme JSON is provided, the font family, font sizes, line spacing, and color checks are driven by the theme's `ats_constraints.font_family` and `typography` block — not the Calibri defaults above. The structural rules (no tables, no images, native heading styles) apply to **all** themes regardless.

**Fonts must come from the canonical ATS-safe list** (the `font_family` enum in `templates/schema_v2_0.json`; listed in `templates/THEME_SPEC_GUIDE.md`): Arial, Calibri, Helvetica, Verdana, Tahoma, Trebuchet MS, Century Gothic, Gill Sans, Lucida Sans, Lucida Grande, Garamond, Georgia, Cambria, Times New Roman, Century Schoolbook, New Century Schoolbook, Palatino, Book Antiqua. `base_font`, `ats_constraints.font_family` and `heading_font_family` are all constrained to it. `audit_doc_style.py` checks the doc against the theme's font; it does not check the allowlist — run `python3 tools/validate_templates_v2.py <theme.json>` for that.

Example expected values (read the theme JSON for the authoritative numbers):

| Theme | Font | Normal size | Line spacing |
|---|---|---|---|
| `contemporary_professional` | Calibri | 10.5pt | 1.2 |
| `professional_classic` | Times New Roman | 11pt | 1.15 |
| `modern_minimalist` | Arial | 10.5pt | 1.2 |
| `graphite_ledger`, `broadside_press`, `violet_signal` | body Georgia, headings Arial | per theme | per theme |
| `citrus_edge`, `rainbow_minimal` | body Calibri, headings Arial | per theme | per theme |
| `emerald_transit` | body Calibri, headings Georgia | per theme | per theme |

## Protocol

**Step 1 — Run the audit:**

For a KSC or unthemed template:
```bash
python3 tools/audit_doc_style.py <DOC_ID>
```

For a themed resume Golden Master (preferred — avoids false font FAILs):
```bash
python3 tools/audit_doc_style.py <DOC_ID> --theme templates/resume_<theme_name>_v1.json
```

The `--theme` flag (supported by `tools/audit_doc_style.py`) tells the auditor to read expected font, sizes, and spacing from the theme JSON instead of Calibri hardcoded defaults.

**Step 2 — Interpret output:**

If the script prints `STYLE OK` and exits 0 → document is fully compliant. Proceed with registration or pipeline run.

If the script prints any `FAIL:` lines → relay the exact failure messages to the user verbatim. Do NOT attempt to fix the document via the API.

**Step 3 — On failure:**

Instruct the user:
> "Fix the following issues in your Google Doc directly in the browser, then re-run the audit:
> [paste FAIL lines here]"

Do not proceed with the pipeline run until the audit exits 0.

## Hard Rules

- **Never declare PASS without running the script.** LLM review of raw API JSON is not a substitute.
- **Never attempt automated fixes.** The Golden Master is source-of-truth — only the user edits it.
- **Relay FAIL output verbatim.** Do not paraphrase or omit failure lines.
- **Never fail a themed template for using the wrong font** unless the font doesn't match its own theme spec. A Times New Roman or Georgia doc is not broken — it's intentional. A theme whose own fonts fall outside the canonical list is a template defect: fix the theme JSON, not the doc.

## Common Issues

| FAIL message pattern | Fix in Google Docs |
|---|---|
| `font is 'Arial'` (unthemed) | Select text → Format → Font → change to Calibri |
| `font is 'Arial'` (modern_minimalist theme) | Expected — not a failure for this theme |
| `all-bold NORMAL_TEXT resembles a heading` | Select paragraph → Apply Heading 1 or Heading 2 style |
| `line spacing is 100%` | Select all → Format → Line & paragraph spacing → set per theme |
| `space below is 0pt` | Select all → Format → Line & paragraph spacing → Add spacing after |
| `contains N table(s)` | Delete table, replace with plain-text paragraph |
| `contains N inline image(s)` | Delete image(s) — no images permitted |
