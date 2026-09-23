---
name: Session status and next steps
description: Captures confirmed incomplete tasks, housekeeping fixes applied this session, and the corrected implementation design for the hybrid heading rename and KSC v2 end-to-end validation.
type: project
---

# Design: Session Status and Next Steps

**Date:** 2026-05-27
**Status:** Approved — proceeding to implementation

---

## Background

Audit of project state revealed three incomplete tasks and one immediate housekeeping issue. The housekeeping issue was resolved in-session before this doc was written.

### Housekeeping resolved this session

- **Drive folder IDs** — `config/doc_templates.json` already updated by user automation script before session.
- **Stale theme paths** — All `"theme"` fields in `config/doc_templates.json` referenced `doc_templates/` (non-existent directory). Fixed via sed to `templates/`. Verified clean.

---

## Task 1 — Hybrid resume heading rename

### Problem

All 5 section headings in the hybrid resume are non-compliant with `ats_rules.json` `allowed_headings`, and the JSON theme and Markdown spec disagree on what those headings currently are:

| Section | `templates/resume_hybrid_v1.json` | `context/specs/resume_hybrid_template_spec.md` | Compliant target |
|---|---|---|---|
| Summary | `PROFESSIONAL SUMMARY` | `SUMMARY` | `Summary` |
| Skills | `CORE SKILLS` | `CORE COMPETENCIES` | `Skills` |
| Experience | `WORK EXPERIENCE` | `PROFESSIONAL EXPERIENCE` | `Experience` |
| Education | `EDUCATION` | `EDUCATION` | `Education` |
| Certifications | `CERTIFICATIONS` | `CERTIFICATIONS AND LICENSING` | `Certifications` |

The live Google Doc (`16FlPfFjHCYibECNtGORE-KEZtr1ogP_dRayo29L0y_I`) was built from a prior v1 spec and is assumed non-compliant pending visual inspection.

The `allowed_headings` whitelist is exactly: `Summary`, `Skills`, `Experience`, `Education`, `Certifications`, `Key Achievements`. No `ats_rules.json` changes required.

### Atomicity requirement

All three artefacts must land together. If any artefact retains a stale heading, the next `build_golden_master.py` run will regenerate the Google Doc with the wrong heading, undoing the manual fix.

### Validation note

`tools/validate_template_spec.py` is **KSC-only**. Running it against the hybrid resume spec produces 29+ spurious rule2 failures because the validator's token allowlist is keyed to KSC criteria_responses tokens, not resume blocks. Resume spec validation is therefore **manual** until a resume-aware validator (or a doc_type-dispatching validator) exists. This is a known gap, not a deferred sub-task of this work.

### Changes

**File: `templates/resume_hybrid_v1.json`**
- `summary_section.heading`: `"PROFESSIONAL SUMMARY"` → `"Summary"`
- `skills_section.heading`: `"CORE SKILLS"` → `"Skills"`
- `experience_section.heading`: `"WORK EXPERIENCE"` → `"Experience"`
- `education_section.heading`: `"EDUCATION"` → `"Education"`
- `certifications_section.heading`: `"CERTIFICATIONS"` → `"Certifications"`

**File: `context/specs/resume_hybrid_template_spec.md`**
- STRUCTURE line 6: `[Heading 1] SUMMARY` → `[Heading 1] Summary`
- STRUCTURE line 8: `[Heading 1] CORE COMPETENCIES` → `[Heading 1] Skills`
- STRUCTURE line 10: `[Heading 1] PROFESSIONAL EXPERIENCE` → `[Heading 1] Experience`
- STRUCTURE line 23: `[Heading 1] EDUCATION` → `[Heading 1] Education`
- STRUCTURE line 26: `[Heading 1] CERTIFICATIONS AND LICENSING` → `[Heading 1] Certifications`
- META `DOC_ID` (line 5): `REPLACE_WITH_RESUME_HYBRID_GOLDEN_MASTER_DOC_ID` → `16FlPfFjHCYibECNtGORE-KEZtr1ogP_dRayo29L0y_I`
- ATS_AUDIT `allowed_headings` line: fabricated `PASS — Calibri only, consistent styles` → `PASS — all 5 headings (Summary, Skills, Experience, Education, Certifications) in allowed_headings whitelist`
- REGISTRATION_FRAGMENT `template_doc_id`: `REPLACE_WITH_RESUME_HYBRID_GOLDEN_MASTER_DOC_ID` → `16FlPfFjHCYibECNtGORE-KEZtr1ogP_dRayo29L0y_I`

**Manual user action (Google Doc `16FlPfFjHCYibECNtGORE-KEZtr1ogP_dRayo29L0y_I`)**
- Rename all 5 section headings per the table above
- Confirm each is styled as Heading 1 (not bolded Normal text)

---

## Task 2 — KSC v2 end-to-end validation

### Problem

The anti-slop v2 tooling is fully built but has never been exercised end-to-end:
- `validate_template_spec.py` exists but no spec has ever been run through it
- `agent_skills/gold_template_builder_v3/SKILL.md` exists but no spec has been produced with it
- The existing `ksc_base` Golden Master was built with v1 skills before the validator existed
- The design spec (`context/specs/2026-05-25-ksc-anti-slop-skill-v2-design.md`) is still marked "Draft — awaiting user review"

### Architecture note

`build_golden_master.py` requires a **JSON theme file** as input — it does not accept Markdown spec files. The v2 flow produces a Markdown spec first (for validation), which must then be translated to a JSON theme file before the Golden Master can be built.

### Corrected flow

```
gold_template_builder_v3 (LLM)
  → context/specs/ksc_standard_v2_spec.md   (Markdown spec)
  → python3 tools/validate_template_spec.py  (hard gate — iterate on FAILs)
  → templates/ksc_standard_v2.json           (JSON theme translation)
  → python3 tools/build_golden_master.py     (builds Google Doc, prints Doc ID)
  → config/doc_templates.json                (register new Doc ID)
  → generate_document.py --dry-run           (verify token resolution)
  → one live KSC generation                  (inspect output)
  → mark design spec as Approved
```

### Path table

| Artefact | Path |
|---|---|
| Validated Markdown spec | `context/specs/ksc_standard_v2_spec.md` |
| Translated JSON theme | `templates/ksc_standard_v2.json` |
| Theme spec guide | `templates/THEME_SPEC_GUIDE.md` |
| Validator | `tools/validate_template_spec.py` |
| Golden Master builder | `tools/build_golden_master.py` |
| Config to update | `config/doc_templates.json` |

### KSC JSON block structure (from THEME_SPEC_GUIDE.md)

Blocks expected: `name_header`, `contact_info`, `application_meta`, `criteria_responses`.

### Steps

1. Invoke `gold_template_builder_v3` to produce `context/specs/ksc_standard_v2_spec.md`
2. Run `python3 tools/validate_template_spec.py context/specs/ksc_standard_v2_spec.md` — iterate on any FAILs until exit 0
3. Translate the validated spec into `templates/ksc_standard_v2.json` following `templates/THEME_SPEC_GUIDE.md`
4. Run `python3 tools/build_golden_master.py templates/ksc_standard_v2.json` — capture printed Doc ID
5. Update `config/doc_templates.json` with the new Doc ID under `ksc.variants.standard` (or replace `ksc.template_doc_id` if treating as the new base)
6. Run `python3 tools/generate_document.py --type ksc --target "Test Role at Test Org" --criteria <criteria_file> --dry-run`
7. Run one live KSC generation — inspect output for token resolution and formatting
8. If clean: update `context/specs/2026-05-25-ksc-anti-slop-skill-v2-design.md` status from "Draft" to "Approved"

### Gate rule

Do not proceed past Step 2 until the validator returns `SPEC OK`. Do not proceed past Step 4 until the JSON theme is confirmed against `THEME_SPEC_GUIDE.md`.

---

## Non-goals (this session)

- Extending v2 pattern to resume and cover_letter doc types (deferred until KSC loop is clean)
- Deprecating v1 skills
- Changes to `generate_document.py`, `ats_rules.json`, or `THEME_SPEC_GUIDE.md`
