---
name: career-brain-skill-integration
description: Use when you need to know which Career Brain template or theme skill to run next, or the order for a full theme or KSC template run. Routes to the right skill; does not perform any check itself.
---

# Career Brain Skill Integration

Router only. Each skill owns its own checks; this file holds the order and each stage's exit criterion. Do not restate rules here.

**Rule sources (one copy each):** forbidden glyphs, headings, terminology, KSC word limits → `config/ats_rules.json`; fonts, columns, `allows_*` → `templates/schema_v2_0.json`; required blocks, heading treatment → `templates/THEME_SPEC_GUIDE.md`; theme ATS spec checks (incl. near-white background, contrast) → `output-quality-gate` step 2.

## Theme chain (resume, cover letter)

| # | Stage | Skill or command | Exit criterion |
|---|---|---|---|
| 1 | Look-and-feel ranking | `theme-visual-preview-v3` | User ranks themes |
| 2 | Near-duplicate check | `theme-divergence-auditor` | PASS |
| 3 | Purpose | `theme-purpose-interrogator` (Q7/Q8 use stage 2's result) | PASS |
| 4 | Family | `family-coherence-auditor` | PASS |
| 5 | Build approval | `output-quality-gate` Stage A | APPROVE (Stage A) |
| 6 | Compile, then build Golden Master | `tools/compile_theme.py`, `tools/build_golden_master.py` | Doc ID |
| 7 | Live audit | `docs-style-auditor-v3` | `STYLE OK` |
| 8 | Register approval | `output-quality-gate` Stage B (consumes stage 7) | APPROVE (Stage B) |
| 9 | Register | entry in `config/doc_templates.json` | Real `template_doc_id` |

## KSC chain

| # | Stage | Skill or command | Exit criterion |
|---|---|---|---|
| 1 | Spec | `gold-template-builder-v3` | `SPEC OK` |
| 2 | Golden Master | User builds it in Google Docs | Doc ID |
| 3 | Live audit | `docs-style-auditor-v3` (via `gold-template-builder-v3` QA Stage 2) | `STYLE OK` |
| 4 | Register | `ksc` entry in `config/doc_templates.json` | Real `template_doc_id` |

When the KSC belongs to a theme family, also run `family-coherence-auditor`.

## Code changes

`peer-review` before any `--write` run or commit touching `pipeline/` or `tools/`. Not part of either chain.

## Rules

- Start at the first stage whose exit criterion is not met. Re-run a passed stage only if the theme JSON or spec changed since.
- Theme stage 6, theme stage 7, KSC stage 3 and every registry edit call Google or change shared config: get the user's approval for each.
- Never report a stage passed without its command or skill output.
