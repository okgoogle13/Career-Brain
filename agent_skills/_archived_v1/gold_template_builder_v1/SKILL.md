---
name: gold-template-builder
description: Use when designing or specifying a new Career Brain Google Docs template (resume, cover letter, or KSC) before building the Golden Master in Google Drive.
---

# Gold Template Builder Skill

## Overview

This skill instructs AI agents to design and specify **Gold Standard Google Docs templates** for the Career Brain Phase 5 document generation pipeline.

The pipeline clones a **Golden Master Google Doc** stored in Drive, then performs batch `replaceAllText` substitutions using `{{PLACEHOLDER}}` tokens. Templates are NOT JSON layout files or Python objects — they are Google Docs with correctly placed placeholder tokens.

The active configuration files are:
- **`doc_templates.json`** — Maps template type → Google Doc IDs (Golden Masters in Drive)
- **`generate_document.py`** — Phase 5 engine; defines all valid `{{PLACEHOLDER}}` tokens in `PLACEHOLDER_SCHEMA_V2`
- **`ats_rules.json`** — Defines structural rules, vocabulary constraints, KSC word limits, and Australian terminology mappings
- **`user_config.json`** — Provides static contact info, education, certifications

---

## The 5-Step Sequential Thinking Protocol

When invoked, the agent MUST run through these phases before producing any output:

```
[Phase 1: Target Ingestion] → [Phase 2: Placeholder Mapping] → [Phase 3: Document Structure Design] → [Phase 4: ATS Audit] → [Phase 5: Specification & Test Command Output]
```

### Phase 1: Target Ingestion
- Identify the document type: `resume`, `cover_letter`, or `ksc`.
- Identify the target sector/tone (e.g., Government/APS, NFP/Community Services, Private).
- Identify any variant required (e.g., `chronological`, `hybrid` for resume; `government`, `nfp`, `private` for cover letter).

### Phase 2: Placeholder Mapping
- Select the correct `{{PLACEHOLDER}}` tokens from the **PLACEHOLDER_SCHEMA_V2** reference below.
- Map each placeholder to its intended position in the document structure.
- Flag any token NOT in the schema as invalid — do not invent new placeholders.

### Phase 3: Document Structure Design
- Describe the intended Google Docs layout as a **textual specification**: heading hierarchy, paragraph order, placeholder positions, static boilerplate text.
- Specify which Heading Styles to use (Heading 1, Heading 2, Normal) — do NOT rely on bold Normal text for section headings.
- MUST use standard headings: `Skills` (never Core Competencies) and `Certifications`. `Certifications` MUST be placed as the final section.
- MUST use line breaks instead of pipe (`|`) characters for the Contact Block.
- All layouts must be single-column. No tables for alignment. No text boxes. No inline images.
- For cover letters: specify formal salutation structure appropriate for the target sector.
- For KSC: specify CAR methodology structure (Context → Action → Result) per criterion.

### Phase 4: ATS Audit
Verify the proposed template design against `ats_rules.json` rules:

| Rule | Check |
|---|---|
| `structure.columns_max: 1` | Single-column layout only |
| `structure.allow_tables: false` | No grid tables for layout or alignment |
| `structure.allow_text_boxes: false` | No floating text boxes, frames, shapes |
| `structure.allow_inline_objects: false` | No profile photos, icons, graphic elements |
| `structure.allowed_headings` | Must use `Skills` and `Certifications`. Do NOT use `Core Competencies`. |
| `vocabulary.forbidden_characters` | Must not use: `•`, `✔`, `★`, `❖`, `●`, `✅`, `❌`, `|` (use plain `-` or `–` for bullets, line breaks for separators) |
| `terminology.australian_mappings` | Verify static boilerplate text uses AU terminology: "organisation" not "company", "position description" not "job description", "key selection criteria" not "competency questions" |
| `ksc.word_limits` | Context: 40–100 words, Action: 60–200 words, Result: 30–100 words, Total: 200–500 words |

If any rule is violated, reject the design and revise Phase 3 before proceeding.

### Phase 5: Specification & Test Command Output
- Output a clear, human-readable **template specification** the user can follow when building the Golden Master in Google Docs.
- Output the `doc_templates.json` entry fragment needed to register the new template.
- Output the dry-run test command to validate pipeline compatibility.

---

## PLACEHOLDER_SCHEMA_V2 Reference

### Resume (`--type resume`)
```
{{CONTACT_NAME}}         # User's full name
{{CONTACT_PHONE}}        # Phone number
{{CONTACT_EMAIL}}        # Email address
{{CONTACT_LOCATION}}     # Suburb, State
{{PROFESSIONAL_SUMMARY}} # AI-generated summary paragraph
{{SKILL_1}} – {{SKILL_6}} # Core skills (MAX_RESUME_SKILLS = 6)
{{ROLE_1_TITLE}}         # Job title
{{ROLE_1_ORG}}           # Organisation name
{{ROLE_1_DATES}}         # "Start Date – End Date" range
{{ROLE_1_BULLET_1}} – {{ROLE_1_BULLET_4}} # Achievement bullets per role (MAX_BULLETS_PER_ROLE = 4)
# Repeat ROLE_2_, ROLE_3_, ... up to ROLE_6 (MAX_RESUME_ROLES = 6)
{{EDUCATION_1}}, {{EDUCATION_2}}
{{CERT_1}}, {{CERT_2}}, {{CERT_3}}
# Legacy v1 tokens (backward compat only — do not use for new templates):
{{TARGET_ROLE}}, {{SUMMARY}}, {{BULLET_1}}–{{BULLET_6}}
```

### Cover Letter (`--type cover_letter`)
```
{{CONTACT_NAME}}, {{CONTACT_PHONE}}, {{CONTACT_EMAIL}}, {{CONTACT_LOCATION}}
{{EMPLOYER_CONTACT_NAME}}   # Hiring manager name (may be blank)
{{EMPLOYER_ORG}}            # Extracted from target "Role at Org"
{{EMPLOYER_ADDRESS}}        # Organisation address (may be blank)
{{SALUTATION}}              # Auto-mapped from --employer-type flag
{{CURRENT_DATE}}            # Auto-generated
{{HOOK_PARAGRAPH}}          # From "hook" or "pivot" narrative type
{{BRIDGE_PARAGRAPH}}        # Rosetta Stone translation paragraph
{{EVIDENCE_PARAGRAPH_1}}, {{EVIDENCE_PARAGRAPH_2}}  # STAR/CAR narratives
{{CLOSING_PARAGRAPH}}       # Auto-generated closing
# Legacy v1 tokens (backward compat only):
{{TARGET_ROLE}}, {{SUMMARY}}, {{KSC_RESPONSE_1}}–{{KSC_RESPONSE_3}}
```

### KSC (`--type ksc`)
```
{{CONTACT_NAME}}, {{TARGET_ROLE}}, {{EMPLOYER_ORG}}
# Per criterion (up to 6, MAX_KSC_CRITERIA = 6):
{{KSC_CRITERION_1_TEXT}}        # The criterion statement itself
{{KSC_1_CONTEXT}}               # CAR: Context block
{{KSC_1_ACTION}}                # CAR: Action block
{{KSC_1_RESULT}}                # CAR: Result block
{{KSC_1_SUPPORT_BULLET_1}} – {{KSC_1_SUPPORT_BULLET_2}}  # Evidence bullets (MAX_KSC_SUPPORT_BULLETS = 2)
# Repeat for KSC_2_, KSC_3_, ... up to KSC_6
```

---

## `doc_templates.json` Registration

When specifying a new template, output the registration fragment. Example for a new government cover letter variant:

```json
{
  "cover_letter": {
    "variants": {
      "government": {
        "template_doc_id": "REPLACE_WITH_GOV_COVER_LETTER_DOC_ID"
      }
    }
  }
}
```

The user must replace `REPLACE_WITH_*` with the actual Google Doc ID after creating the Golden Master in Google Drive.

---

## Verification Commands

After the user creates the Golden Master Google Doc and registers its ID in `doc_templates.json`:

```bash
# Dry-run validation (no API calls, validates token resolution only)
python3 generate_document.py --type resume --target "Test Role at Test Org" --dry-run

# Cover letter dry-run with employer type
python3 generate_document.py --type cover_letter --target "Case Manager at DHHS" --employer-type government --dry-run

# KSC dry-run with criteria file
python3 generate_document.py --type ksc --target "Intake Worker at Launch Housing" --criteria criteria.txt --dry-run

# Full live run (requires valid Google Doc ID and OAuth credentials)
python3 generate_document.py --type resume --target "Project Worker at Launch Housing"
```

---

## Out of Scope

This skill does NOT produce:
- JSON layout block schemas (no `kind`/`source` structure)
- Python `ThemeTokens` models
- React components or CSS variables
- `python-docx` `.docx` files
- Claude Code `/skill-creator` commands

All document output goes through `generate_document.py` → Google Docs API.
