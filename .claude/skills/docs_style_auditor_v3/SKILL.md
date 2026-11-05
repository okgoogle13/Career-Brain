---
name: docs-style-auditor-v3
description: Use when verifying or QA-checking that a live Career Brain Google Docs Golden Master (themed resume, cover letter or KSC) is structurally and typographically compliant before registration or a live pipeline run — catches font, spacing, heading style, and layout violations that LLM review cannot reliably detect.
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

**Fonts must come from the canonical ATS-safe list** (`font_family` enum in `templates/schema_v2_0.json`; see `templates/THEME_SPEC_GUIDE.md`). `audit_doc_style.py` checks the doc against the theme's font; it does not check the allowlist — run `.venv/bin/python tools/validate_templates_v2.py <theme.json>` for that.

Read the theme JSON for the authoritative font, sizes and spacing; do not rely on values copied here.

## Protocol

This skill is the single owner of the live audit: `output-quality-gate` and `gold-template-builder-v3` consume its result rather than re-running it. Both scripts call the Google Docs API — ask the user before each run.

**Step 1 — Run the audit:**

For a KSC or unthemed template:
```bash
.venv/bin/python tools/audit_doc_style.py <DOC_ID>
```

For a themed resume Golden Master (preferred — avoids false font FAILs):
```bash
.venv/bin/python tools/audit_doc_style.py <DOC_ID> --theme templates/resume_<theme_name>_v1.json
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

**Step 4 — Supplementary checks** (all Golden Masters):

```bash
.venv/bin/python tools/verify_golden_master.py <DOC_ID> --theme=templates/<theme>.json
```

This adds a heading-aware font check. Neither script detects text boxes (positioned objects) — confirm none from the doc and report `PASS` or `FAIL — <evidence>`. KSC Golden Masters: run the spec stage in `gold-template-builder-v3` first.

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
