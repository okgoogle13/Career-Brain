# Custom Claude Skills — Synced to Cowork

**Sync Date:** May 28, 2026  
**Source:** `/Users/okgoogle13/Projects/Career Brain/agent_skills/`  
**Status:** ✓ All skills backed up and ready to use

---

## Skills Synced (3 total)

### 1. **ATS Template QA v2** (`ats_template_qa_v3`)
**Purpose:** QA-check KSC template specs and live Golden Master Google Docs before registration or pipeline run.

**Two-stage process:**
- **Stage 1:** Mechanical validation via `validate_template_spec.py`
- **Stage 2:** Docs-API checks (heading styles, fonts, spacing, structural rules)

**Trigger phrase:** Use when verifying template compliance, checking for ATS violations, or validating spec files.

**Key checks:**
- Token validity, forbidden glyphs, heading whitelist
- AU terminology compliance
- Font/size/spacing against theme specs
- Native heading styles (no bolded text posing as headers)
- No tables, images, or text boxes

---

### 2. **Docs Style Auditor** (`docs_style_auditor_v3`)
**Purpose:** Mechanical audit of Google Docs Golden Master templates for style & structure compliance before pipeline runs.

**Zero-inference approach:** Only flags explicit deviations in the document's API response.

**Trigger phrase:** Use when auditing Golden Master templates, checking formatting before registration, or debugging template output issues.

**Theme-aware:** Validates against the correct font/size/spacing based on theme JSON if provided.

**Key enforcements:**
- Font family (Calibri by default, or theme-specific)
- Font sizes for body, headings, titles
- Line spacing & paragraph spacing
- Structural rules (no tables, images, or heading violations)
- AU terminology

---

### 3. **Gold Template Builder v2** (`gold_template_builder_v3`)
**Purpose:** Design and specify new KSC templates for the Career Brain pipeline.

**Output:** A machine-parseable Markdown spec that passes `validate_template_spec.py` before Golden Master registration.

**Trigger phrase:** Use when designing new KSC templates, specifying Golden Master structure, or creating template specs.

**Token system:** Uses canonical `{{PLACEHOLDER}}` tokens defined in `generate_document.py`:
- `{{CONTACT_NAME}}`, `{{TARGET_ROLE}}`, `{{EMPLOYER_ORG}}`
- `{{KSC_CRITERION_c_TEXT}}`, `{{KSC_c_CONTEXT}}`, `{{KSC_c_ACTION}}`, `{{KSC_c_RESULT}}`
- Support bullets for each criterion

**ATS compliance checks:**
- Single column layout only
- Word limits: Context 40–100w, Action 60–200w, Result 30–100w, Total 200–500w per criterion
- Forbidden characters: `•  ✔  ★  ❖  ●  ✅  ❌  |`
- AU terminology enforcement

---

## How to Use in Cowork

These skills are now available in your Cowork session. Reference them by name when you need to:
- Design or validate KSC templates
- Audit Golden Master Google Docs before registration
- Check ATS compliance and formatting

Each skill has detailed internal guidance on exactly what to check and how to report results.

---

## File Locations

**Backup copy in outputs:**  
`/Users/okgoogle13/Projects/Career Brain/synced_skills/`

**Original source:**  
`/Users/okgoogle13/Projects/Career Brain/agent_skills/`

---

## Next Steps

1. **Reference the skills** in your Cowork workflow by their trigger names
2. **Use them together:** Builder → Auditor → QA validator workflow
3. **Keep this manifest** as a quick reference for skill descriptions and purposes

All three skills are production-ready and integrate with your Career Brain KSC pipeline.
