---
name: gold-template-builder-v2
description: Use when designing or specifying a new KSC template for the Career Brain pipeline. Produces a machine-parseable spec that validate_template_spec.py can hard-gate before registration.
---

# Gold Template Builder v2 (KSC)

## What this skill does

Produces a **KSC template spec** — a structured Markdown file that describes a Golden Master Google Doc's layout, placeholder tokens, and ATS compliance. The spec must pass `validate_template_spec.py` before the Golden Master is registered in `doc_templates.json`.

The pipeline clones the Golden Master Google Doc, performs batch `replaceAllText` substitutions using `{{PLACEHOLDER}}` tokens, and outputs the final KSC document. This skill specifies the structure of that doc.

## Output rule

Produce output that **exactly matches** `skills/gold_template_builder_v2/ksc_template_spec_form.md`. No additional sections. No decorative elements. No emoji. No box-drawing characters. No ritual footers. No preamble. No phase headers.

The spec file is the deliverable. Nothing else.

## Token rule

**Every `{{TOKEN}}` you write must be cited in TOKENS_USED with its source line in `generate_document.py`.**

KSC tokens are defined at `generate_document.py:118–133`. Read those lines before writing the spec. The canonical token list is:

```
{{CONTACT_NAME}}  {{TARGET_ROLE}}  {{EMPLOYER_ORG}}

Per criterion c (1 to 6):
  {{KSC_CRITERION_c_TEXT}}
  {{KSC_c_CONTEXT}}
  {{KSC_c_ACTION}}
  {{KSC_c_RESULT}}
  {{KSC_c_SUPPORT_BULLET_1}}
  {{KSC_c_SUPPORT_BULLET_2}}
```

If a token name is not in this list, it does not exist in the pipeline. Do not write it.

## ATS rules (source of truth: `ats_rules.json`)

- **Forbidden characters** (never use in spec or document): `•  ✔  ★  ❖  ●  ✅  ❌  |`
- **Bullet style**: plain hyphen `-` only. Never `•` or any Unicode bullet.
- **Allowed static headings**: `Summary`, `Skills`, `Experience`, `Education`, `Certifications`, `Key Achievements`. Criterion headings filled by `{{KSC_CRITERION_N_TEXT}}` are placeholder headings — exempt.
- **AU terminology**: use `organisation` not `company`, `sector` not `industry`, `position description` not `job description`, `key selection criteria` not `competency questions`.
- **Layout**: single column only. No tables. No text boxes. No inline images.
- **KSC word limits**: Context 40–100w, Action 60–200w, Result 30–100w, Total 200–500w per criterion.

## ATS_AUDIT fill rule

For each audit key, write `PASS` or `FAIL` only if you have checked it against the spec you are writing. Do not write `PASS` for a check you did not perform. The validator will independently re-run every mechanical check and flag any fabricated PASS.

## Validation

After writing the spec, run:

```bash
python3 validate_template_spec.py <spec_file.md>
```

If it returns `FAIL`, fix the named issue and re-run. Do not declare done until it returns `SPEC OK`.

## Registration fragment shape

Match the existing shape in `doc_templates.json`. The current KSC entry is flat:

```json
{
  "ksc": {
    "template_doc_id": "REPLACE_WITH_KSC_GOLDEN_MASTER_DOC_ID"
  }
}
```

Replace `REPLACE_WITH_KSC_GOLDEN_MASTER_DOC_ID` with the actual Google Doc ID after building the Golden Master.

## Out of scope

This skill does not cover resume or cover_letter templates (handled by v1 until v2 is extended). It does not produce JSON layout schemas, Python models, or `.docx` files.
