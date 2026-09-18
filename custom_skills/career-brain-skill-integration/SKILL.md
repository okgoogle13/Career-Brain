---
name: career-brain-skill-integration
description: Manage and orchestrate the Career Brain ATS/template workflow skills (ats-template-qa, docs-style-auditor, gold-template-builder). Use this when designing KSC templates, auditing Golden Master documents, validating template specs, or running the full template pipeline. Handles skill coordination, workflow sequencing, and integration with the Career Brain document generation system.
---

# Career Brain Skill Integration

## Overview

Orchestration skill for the Career Brain ATS-compliant resume/KSC template pipeline. Coordinates three specialized skills in a cohesive workflow:

1. **Gold Template Builder v2** — Design new KSC templates and template specs
2. **Docs Style Auditor** — Validate Golden Master formatting before registration
3. **ATS Template QA v2** — Comprehensive QA of specs and live documents

This skill knows when to invoke each one, in what order, and how to interpret their results.

## When to Use

- **Full pipeline run:** You're creating a new KSC template from scratch
- **Spec validation:** You've written a template spec and want to validate it before Golden Master creation
- **Golden Master QA:** You've built a Golden Master doc and need it audited before registration
- **Debugging templates:** A template isn't working — need to trace through the pipeline to find the issue
- **ATS compliance check:** Need to confirm a template is ATS-safe before a live pipeline run
- **Template variant creation:** Building themed resume variants (contemporary_professional, professional_classic, modern_minimalist)

## The Career Brain Pipeline

### Stage 1: Template Design (Gold Template Builder)

You design the structure of a KSC template:

```
Input: Description of template layout and structure
↓
Output: ksc_template_spec.md (machine-parseable spec)
↓
Validated by: validate_template_spec.py (must return SPEC OK)
```

**Tokens Used:**
```
{{CONTACT_NAME}}, {{TARGET_ROLE}}, {{EMPLOYER_ORG}}
{{KSC_CRITERION_c_TEXT}}, {{KSC_c_CONTEXT}}, {{KSC_c_ACTION}}, {{KSC_c_RESULT}}
{{KSC_c_SUPPORT_BULLET_1}}, {{KSC_c_SUPPORT_BULLET_2}}
```

**ATS Rules:**
- Single column layout only
- Forbidden: `•  ✔  ★  ❖  ●  ✅  ❌  |`
- Bullet style: plain hyphen `-` only
- AU terminology: `organisation`, `sector`, `position description`, `key selection criteria`
- Word limits: Context 40–100w, Action 60–200w, Result 30–100w, Total 200–500w per criterion

### Stage 2: Golden Master Creation

You create a Google Doc based on your spec (using template spec as a template).

```
Input: ksc_template_spec.md
↓
Create: Golden Master Google Doc in Google Docs
- Fill in static text, headings, structure
- Leave {{PLACEHOLDERS}} for pipeline substitution
↓
Document the: Google Doc ID
```

### Stage 3: Document Styling (Docs Style Auditor)

Before registering, validate the Golden Master's formatting:

```
Input: Google Doc ID (for live doc audit) + optional theme JSON
↓
Checks:
- Heading styles (native HEADING_1/HEADING_2, not bolded NORMAL_TEXT)
- Font family (Calibri by default; theme-specific overrides)
- Font sizes (body 11pt, H1 14pt, title 14pt — adjusted per theme)
- Line spacing (1.15 default; per-theme variants)
- No tables, images, text boxes
- Margins (2cm default)
↓
Output: STYLE OK or list of FAIL items
```

**Themed Resume Variants:**

| Theme | Font | Body | H1 | Title | Line spacing |
|---|---|---|---|---|---|
| contemporary_professional | Calibri | 10.5pt | 13pt | 17pt | 1.2 |
| professional_classic | Times New Roman | 11pt | 14pt | 16pt | 1.15 |
| modern_minimalist | Arial | 10.5pt | 13pt | 18pt | 1.2 |

### Stage 4: QA Validation (ATS Template QA)

Final comprehensive QA before live registration:

```
Input: spec file OR registered Golden Master Doc ID
↓
Two-stage process:
1. Mechanical validation (validate_template_spec.py)
   - Token validity
   - Forbidden glyphs
   - Heading whitelist
   - AU terminology
   - Registration shape
   - KSC structural completeness
   
2. Docs-API checks (after Golden Master built)
   - Heading styles
   - Inline objects (none permitted)
   - Text boxes (none permitted)
   - Tables (none permitted)
   - Typography per theme spec
↓
Output: SPEC OK + STYLE PASS or detailed failure list
```

## Workflow Patterns

### Pattern A: New Template Creation (Full Pipeline)

```
1. Run Gold Template Builder
   Ask: "What should the template structure be?"
   Output: ksc_template_spec.md
   ↓
2. Validate spec with ATS Template QA
   Stage 1: Run validate_template_spec.py
   If FAIL: return failures to user, repeat until SPEC OK
   ↓
3. Create Golden Master in Google Docs
   Ask user: "Create a Google Doc using this spec. Leave {{PLACEHOLDERS}} unchanged."
   ↓
4. Audit Golden Master with Docs Style Auditor
   Input: Doc ID + theme JSON (if themed)
   Output: STYLE OK or FAIL list
   ↓
5. Final QA with ATS Template QA
   Stage 2: Run Docs-API checks
   Output: Template ready for registration OR issues to fix
```

### Pattern B: Audit Existing Template

```
1. User provides: Google Doc ID of Golden Master
   ↓
2. Run Docs Style Auditor
   Check: Font, spacing, headings, structure
   ↓
3. If any issues, report them + fixes
   ↓
4. User makes fixes in Google Docs
   ↓
5. Re-run auditor to confirm STYLE OK
```

### Pattern C: Debug a Failing Template

```
1. User reports: "This template isn't producing the right output"
   ↓
2. Verify spec with ATS Template QA (Stage 1)
   Check: Is the spec structurally sound?
   ↓
3. Audit Golden Master with Docs Style Auditor
   Check: Is the document formatted correctly?
   ↓
4. Compare: Identify which stage is failing
   - Spec problem? Fix template spec, re-validate
   - Document problem? Fix Golden Master formatting, re-audit
   - Pipeline integration problem? Verify token substitution
```

## Integration with Registration

After QA passes, template is registered in `doc_templates.json`:

```json
{
  "ksc": {
    "template_doc_id": "1a2b3c4d5e6f7g8h9i0j"
  },
  "resume_contemporary_professional": {
    "template_doc_id": "2b3c4d5e6f7g8h9i0j1k"
  }
}
```

The pipeline then:
1. Clones the Golden Master doc
2. Substitutes all `{{PLACEHOLDERS}}` with user data
3. Exports the populated document

## Key Concepts

### KSC (Key Selection Criteria)

Australian job application format that structures qualifications around specific criteria. Each criterion has:
- **Context:** 40–100 words setting the scene
- **Action:** 60–200 words describing what you did
- **Result:** 30–100 words showing the outcome/impact
- **Support bullets:** 2 bullets providing evidence

### ATS Compliance

Resume/document passes Applicant Tracking System parsing:
- Single column (no multi-column layouts)
- No tables, images, or decorative elements
- Native heading styles (parsed correctly)
- AU-appropriate terminology
- No forbidden glyphs that break scanners

### Themed Variants

A template can have multiple visual themes (fonts, sizing, spacing) while keeping the same structure. Each theme has a JSON file defining `visualConfig`:

```json
{
  "name": "contemporary_professional",
  "visualConfig": {
    "fontFamily": "Calibri",
    "bodySize": "10.5pt",
    "headingSize": "13pt",
    "titleSize": "17pt",
    "lineHeight": 1.2
  }
}
```

## Trigger Guidance

Use this skill when the user mentions:
- "Create a new KSC template"
- "Design a template spec"
- "Audit my Golden Master"
- "Check if this template is ATS-safe"
- "I built a Golden Master doc, now what?"
- "This template isn't working, debug it"
- "Build themed resume variants"
- "Validate a template before registration"

Even if they don't explicitly ask for "template pipeline" or "Career Brain workflow," if they're talking about templates, specs, Golden Masters, or ATS compliance in the context of resume/KSC documents, this skill applies.

## Success Criteria

### Template Design (Gold Template Builder)
✓ Spec file produced  
✓ validate_template_spec.py returns `SPEC OK`  
✓ All tokens documented and valid

### Document Formatting (Docs Style Auditor)
✓ Heading styles: Native HEADING_1/HEADING_2  
✓ Font & sizing: Match spec or theme JSON  
✓ Line spacing & margins: Per spec  
✓ No tables, images, or text boxes  
✓ Script returns `STYLE OK`

### QA Validation (ATS Template QA)
✓ Stage 1: Spec passes mechanical validation  
✓ Stage 2: All Docs-API checks pass  
✓ Both stages complete without FAIL items  
✓ Template is production-ready for registration

---

## Example: Full Template Creation

**User:** "I want to create a new KSC template for a creative industry position. It should have a Portfolio section in addition to the standard criteria."

**This skill will:**

1. Invoke Gold Template Builder
   - Design spec with custom "Portfolio" section
   - Define placeholder tokens for portfolio items
   - Ensure AU terminology and word limits

2. Ask user to create Golden Master
   - Provide the spec as a template
   - Show example placeholders

3. Invoke Docs Style Auditor
   - Check formatting of the Golden Master doc
   - Verify fonts, spacing, heading styles

4. Invoke ATS Template QA (Stage 2)
   - Run final Docs-API checks
   - Confirm no forbidden glyphs or layout violations

5. Generate registration fragment
   - Provide JSON for `doc_templates.json`
   - Confirm template is ready for pipeline

---

## Next Steps After Skill Coordination

1. **Spec written:** Copy to version control / Career Brain repo
2. **Golden Master created:** Document the Google Doc ID
3. **Audited & QA'd:** Add to `doc_templates.json`
4. **Registered:** Template ready for live pipeline runs
5. **Variant creation:** Repeat steps 2–4 for each themed variant

For multi-variant templates (e.g., contemporary_professional + professional_classic + modern_minimalist), run the full pipeline once per variant, using the theme JSON in the Docs Style Auditor step.
