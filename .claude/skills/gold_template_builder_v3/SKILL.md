---
name: gold-template-builder-v3
description: Use when designing, specifying or QA-checking a Career Brain KSC template — writes a machine-parseable spec that validate_template_spec.py hard-gates, then QA-checks the spec and the built KSC Golden Master before registration or a live pipeline run. KSC only — not for building or checking resume or cover-letter Golden Masters.
---

# Gold Template Builder v3 (KSC)

## What this skill does

Produces a **KSC template spec** — a structured Markdown file that describes a Golden Master Google Doc's layout, placeholder tokens, and ATS compliance. The spec must pass `validate_template_spec.py` before the Golden Master is registered in `doc_templates.json`.

The pipeline clones the Golden Master Google Doc, performs batch `replaceAllText` substitutions using `{{PLACEHOLDER}}` tokens, and outputs the final KSC document. This skill specifies the structure of that doc.

## Output rule

Produce output that **exactly matches** `.claude/skills/gold_template_builder_v3/ksc_template_spec_form.md` (sibling of this file). No additional sections. No decorative elements. No emoji. No box-drawing characters. No ritual footers. No preamble. No phase headers.

The spec file is the deliverable. Nothing else.

## Token rule

**Every `{{TOKEN}}` you write must be cited in TOKENS_USED with its source line in `generate_document.py`.**

KSC tokens are defined in `PLACEHOLDER_SCHEMA_V2["ksc"]` in `tools/generate_document.py` (the `"ksc": (` block; find it with `rg -n '"ksc": \(' tools/generate_document.py`). Read that block for exact line numbers before writing the spec. The canonical token list is:

```
{{CONTACT_NAME}}  {{CONTACT_PHONE}}  {{CONTACT_EMAIL}}  {{CONTACT_LOCATION}}
{{TARGET_ROLE}}  {{EMPLOYER_ORG}}

Per criterion c (1 to 6):
  {{KSC_CRITERION_c_TEXT}}
  {{KSC_c_CONTEXT}}
  {{KSC_c_ACTION}}
  {{KSC_c_RESULT}}
  {{KSC_c_SUPPORT_BULLET_1}}
  {{KSC_c_SUPPORT_BULLET_2}}
```

If a token name is not in this list, it does not exist in the pipeline. Do not write it.

## ATS rules (read, don't copy)

Before writing, read these keys from `config/ats_rules.json` with `rg -n`: `forbidden_characters`, `forbidden_char_ranges`, `allowed_headings`, `terminology`, `ksc.word_limits`. They are the only source — do not rely on remembered lists. Criterion headings filled by `{{KSC_CRITERION_N_TEXT}}` are placeholder headings, exempt from `allowed_headings`.

Not in that file: bullets are plain hyphen `-` only; layout is single column with no tables, text boxes or inline images.

## ATS_AUDIT fill rule

For each audit key, write `PASS` or `FAIL` only if you have checked it against the spec you are writing. Do not write `PASS` for a check you did not perform. The validator will independently re-run every mechanical check and flag any fabricated PASS.

## Validation

After writing the spec, run:

```bash
.venv/bin/python tools/validate_template_spec.py <spec_file.md>
```

If it returns `FAIL`, fix the named issue and re-run. Do not declare done until it returns `SPEC OK`.

## QA (existing spec or built Golden Master)

Use this section alone when asked to QA a KSC spec or KSC Golden Master you did not just write.

**Stage 1 — Spec.** Run the validator above against the spec. It checks token validity, forbidden glyphs, heading whitelist, AU terminology, audit honesty, registration shape and KSC structural completeness. Report its output verbatim. On exit 1, list each `FAIL` line and stop — no Stage 2 until it returns `SPEC OK`.

**Stage 2 — Live Golden Master** (only after the user has built it and has its Doc ID): run `docs-style-auditor-v3` on the Doc ID. It owns the live audit, the supplementary checks and the Google Docs API approval. Relay its result; never PASS without its output. Raw check results only — no decorative formatting or summaries.

Never declare a KSC template QA-passed before Stage 1 returns `SPEC OK`.

## Registration fragment shape

Match the existing shape in `config/doc_templates.json`. The KSC entry has a doc ID plus a `theme` path (the spec form's fragment shows only `template_doc_id`, which is what the validator checks):

```json
{
  "ksc": {
    "template_doc_id": "REPLACE_WITH_KSC_GOLDEN_MASTER_DOC_ID",
    "theme": "templates/ksc_standard_v2.json"
  }
}
```

Replace `REPLACE_WITH_KSC_GOLDEN_MASTER_DOC_ID` with the actual Google Doc ID after building the Golden Master.

## Out of scope

This skill covers KSC templates only. Resume and cover_letter Golden Masters are built from theme JSON via `tools/build_golden_master.py`, not from a spec; QA them with `docs-style-auditor-v3`. It does not produce JSON layout schemas, Python models, or `.docx` files.
