---
name: ats-template-qa
description: Use when QA-checking or validating a Career Brain Google Docs template — before a live pipeline run, after editing a Golden Master, or when batch-validating all entries in doc_templates.json.
---

# ATS Template QA Skill

## Overview

This skill instructs AI agents to statically lint and quality-assure **Google Docs Golden Master templates** for the Career Brain Phase 5 pipeline.

Golden Masters are Google Docs stored in Drive. The pipeline clones them and performs batch `replaceAllText` substitutions. This skill validates that those docs are correctly structured before any live run.

The active reference files are:
- **`doc_templates.json`** — Registered template IDs to validate
- **`ats_rules.json`** — Authoritative ATS compliance rules
- **`generate_document.py`** — Defines valid `{{PLACEHOLDER}}` tokens in `PLACEHOLDER_SCHEMA_V2`

---

## Validation Protocol

When asked to validate a template, the agent MUST run all three checks below in sequence and produce a structured report.

---

### Check 1: Placeholder Hygiene

**Reference:** `PLACEHOLDER_SCHEMA_V2` in `generate_document.py`

#### v2 Schema (current — use for new templates)

**Resume:**
```
{{CONTACT_NAME}}, {{CONTACT_PHONE}}, {{CONTACT_EMAIL}}, {{CONTACT_LOCATION}}
{{PROFESSIONAL_SUMMARY}}
{{SKILL_1}} ... {{SKILL_6}}
{{ROLE_N_TITLE}}, {{ROLE_N_ORG}}, {{ROLE_N_DATES}}
{{ROLE_N_BULLET_1}} ... {{ROLE_N_BULLET_4}}
{{EDUCATION_1}}, {{EDUCATION_2}}
{{CERT_1}}, {{CERT_2}}, {{CERT_3}}
```

**Cover Letter:**
```
{{CONTACT_NAME}}, {{CONTACT_PHONE}}, {{CONTACT_EMAIL}}, {{CONTACT_LOCATION}}
{{EMPLOYER_CONTACT_NAME}}, {{EMPLOYER_ORG}}, {{EMPLOYER_ADDRESS}}
{{SALUTATION}}, {{CURRENT_DATE}}
{{HOOK_PARAGRAPH}}, {{BRIDGE_PARAGRAPH}}
{{EVIDENCE_PARAGRAPH_1}}, {{EVIDENCE_PARAGRAPH_2}}
{{CLOSING_PARAGRAPH}}
```

**KSC:**
```
{{CONTACT_NAME}}, {{TARGET_ROLE}}, {{EMPLOYER_ORG}}
{{KSC_CRITERION_N_TEXT}}
{{KSC_N_CONTEXT}}, {{KSC_N_ACTION}}, {{KSC_N_RESULT}}
{{KSC_N_SUPPORT_BULLET_1}} ... {{KSC_N_SUPPORT_BULLET_2}}
```

#### v1 Schema (legacy — backward compat only, acceptable in older templates)
```
{{TARGET_ROLE}}, {{SUMMARY}}
{{BULLET_1}} – {{BULLET_6}}               # Resume legacy
{{KSC_RESPONSE_1}} – {{KSC_RESPONSE_3}}  # Cover letter legacy
```

#### Validation Rules
- **Required tokens present** — Verify all mandatory tokens for the document type appear in the doc.
- **No unknown tokens** — Scan for any `{{...}}` pattern NOT in the schema above. Flag as **CRITICAL ERROR**.
- **No REPLACE_WITH placeholders** — Any `template_doc_id` still containing `REPLACE_WITH` in `doc_templates.json` means the Golden Master has not been registered. Flag as **UNREGISTERED — skip live run**.
- **Placement warning** — If a token is found inside a nested table cell or text box, flag as **WARNING: ATS risk**.
- **Header/footer tokens** — Tokens in headers or footers (e.g., `{{CONTACT_NAME}}`) are acceptable for contact blocks.

---

### Check 2: ATS Structural Compliance

Reference: `ats_rules.json` → `structure` block.

| Rule | Expected | Failure Severity |
|---|---|---|
| `columns_max: 1` | Single-column document only | CRITICAL |
| `allow_tables: false` | No grid tables used for alignment or layout | CRITICAL |
| `allow_text_boxes: false` | No floating text boxes, frames, or shapes | CRITICAL |
| `allow_inline_objects: false` | No images, icons, or graphic elements | CRITICAL |
| Heading styles | Use native Google Docs Heading 1/Heading 2, not bolded Normal text | WARNING |
| Bullet glyphs | Only plain `-` or `–` characters. **Forbidden:** `•`, `✔`, `★`, `❖`, `●`, `✅`, `❌` | CRITICAL |
| Background fills | Canvas must be white. No shaded sections or coloured backgrounds | CRITICAL |

---

### Check 3: Australian Terminology

Reference: `ats_rules.json` → `terminology.australian_mappings`

Scan static boilerplate text (non-placeholder sections) for forbidden US/UK terms:

| Use This | Not This |
|---|---|
| organisation / organisations | company / companies |
| sector / sectors | industry / industries |
| position description | job description |
| position advertisement | job ad |
| key selection criteria | competency questions |

Flag any mismatch as **WARNING: Terminology**.

Note: Placeholder content (`{{...}}` tokens) is handled at runtime by the pipeline's `build_placeholder_values_v2()` function, which applies Australian terminology automatically. Only audit static text.

---

### Check 4: KSC Word Limit Awareness (KSC templates only)

Reference: `ats_rules.json` → `ksc.word_limits`

Confirm the template's CAR structure (Context / Action / Result) provides adequate space for:
- Context: 40–100 words
- Action: 60–200 words
- Result: 30–100 words
- Total per criterion: 200–500 words

Flag if the template design compresses these sections in a way that would truncate content.

---

## Batch Validation Protocol

When asked to perform a full batch validation:

1. Read `doc_templates.json`.
2. Extract every `template_doc_id` value (including nested `variants`).
3. For each ID containing `REPLACE_WITH`: log as **UNREGISTERED** — skip structural checks.
4. For registered IDs: run Checks 1–3 against each Golden Master (via Docs API read or file upload).
5. Output a Markdown report grading each template:

```markdown
## Batch Validation Report — [Date]

### resume (chronological)
- Doc ID: [id]
- Status: ✅ PASS / ❌ FAIL / ⚠️ WARNINGS
- Issues: [list]

### cover_letter (government)
- Doc ID: UNREGISTERED — skip
...
```

---

## Dry-Run Validation (No Docs API Required)

To test placeholder resolution without making API calls or creating a live Google Doc:

```bash
# Resume dry-run
python3 generate_document.py --type resume --target "Test Role at Test Org" --dry-run

# Cover letter dry-run
python3 generate_document.py --type cover_letter --target "Case Manager at DHHS" --employer-type government --dry-run

# KSC dry-run
python3 generate_document.py --type ksc --target "Intake Worker at Launch Housing" --criteria criteria.txt --dry-run
```

Dry-run output will surface unresolved `{{PLACEHOLDER}}` tokens and fill-rate statistics without writing to Google Drive. Check `output/parsing_errors.log` for any failures.
