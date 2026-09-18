---
name: ats-template-qa-v3
description: Use to QA-check a KSC template spec or a live Golden Master Google Doc (including themed resume variants) before registration or a live pipeline run. Runs validate_template_spec.py then checks the Docs-API-only items the script cannot see.
---

# ATS Template QA v3 (KSC)

## Overview

Two-stage QA process:

1. **Mechanical validation** — run `validate_template_spec.py` against the spec file. The script checks token validity, forbidden glyphs, heading whitelist, AU terminology, audit honesty, registration shape, and KSC structural completeness. It either passes or prints specific FAIL lines. Trust its output.

2. **Docs-API check** — verify the items that only exist in the live Google Doc and cannot be checked from the spec file alone.

## Stage 1 — Run the validator

```bash
python3 validate_template_spec.py <spec_file.md>
```

Report the exact output verbatim. Do not interpret or paraphrase it. If exit code is 1, list each FAIL line to the user and stop — do not proceed to Stage 2 until the spec is fixed and the validator returns `SPEC OK`.

## Stage 2 — Docs-API checks (after Golden Master is built)

These checks require reading the actual Google Doc. Run them only after the user has built the Golden Master and registered its Doc ID.

**Theme-aware:** For themed resume Golden Masters, check font/size/spacing against the theme spec, not Calibri defaults. Structural rules (no tables, no images, native headings) apply to ALL templates.

### Structural checks (all templates)

| Check | Expected |
|---|---|
| Heading styles | Native HEADING_1 or HEADING_2 — NOT bolded Normal text |
| Inline objects | None (no images, no icons) |
| Text boxes | None |
| Tables | None |

### Typography checks — use theme spec if available

| Check | KSC / unthemed | contemporary_professional | professional_classic | modern_minimalist |
|---|---|---|---|---|
| Font | Calibri | Calibri | Times New Roman | Arial |
| Body size | 11pt | 10.5pt | 11pt | 10.5pt |
| H1 size | 14pt | 13pt | 14pt | 13pt |
| Title size | 14pt | 17pt | 16pt | 18pt |
| Line spacing | 1.15 | 1.2 | 1.15 | 1.2 |
| Space after para | 6pt | per theme JSON | per theme JSON | per theme JSON |
| Margins | 2cm | 1.9cm | 1.9cm | 2.3cm |

Report each check as `PASS` or `FAIL — <evidence>`. Do not claim PASS without reading the doc.

## What you must never do

- Declare the template QA-passed before Stage 1 returns `SPEC OK`.
- Invent a PASS verdict for any Stage 2 check without reading the live doc.
- Add decorative formatting, emoji, or summaries to your report — raw check results only.
