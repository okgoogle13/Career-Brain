---
name: career-brain-skill-integration
description: Manage and orchestrate the Career Brain ATS/template workflow skills (peer-review, ats-template-qa-v3, docs-style-auditor-v3, gold-template-builder-v3). Use this when designing templates, auditing Golden Master documents, validating template specs, or running the full template pipeline. Handles skill coordination, workflow sequencing, and integration with the Career Brain document generation system.
---

# Career Brain Skill Integration

## Overview

Orchestration skill for the Career Brain ATS-compliant template pipeline. Coordinates five specialized skills in a cohesive workflow:

1. **Peer Review** — Staged audit for pipeline code changes before commit/write
2. **Theme Visual Preview v3** — Generate HTML previews of themes via Claude Artifacts
3. **Gold Template Builder v3** — Design new template specs (KSC, resumes, cover letters)
4. **Docs Style Auditor v3** — Validate Golden Master formatting before registration
5. **ATS Template QA v3** — Comprehensive QA of specs and live documents

This skill knows when to invoke each one, in what order, and how to interpret their results.

## When to Use

- **Code modification:** You are editing a Python script in `pipeline/` or `tools/` and need to verify it with `peer-review` before committing
- **Full pipeline run:** You're creating a new template from scratch
- **Spec validation:** You've written a template spec and want to validate it before Golden Master creation
- **Golden Master QA:** You've built a Golden Master doc and need it audited before registration
- **Debugging templates:** A template isn't working — need to trace through the pipeline to find the issue
- **ATS compliance check:** Need to confirm a template is ATS-safe before a live pipeline run
- **Theme integration:** Building and verifying any of the 15+ themed resume variants

## The Career Brain Pipeline

### Stage 0: Code Verification (Peer Review)

Before modifying any pipeline script, ensure changes are safe:

```
Input: Proposed script changes
↓
Run: peer-review skill
↓
Check: Invariants (source_lineage preserved, no bare exceptions, backup-before-write)
↓
Output: SAFE or BLOCK
```

### Stage 1: Visual Aesthetic Review (Theme Visual Preview v3)

Before committing to a template or Golden Master, visualize the JSON theme:

```
Input: theme JSON file(s) + sample content
↓
Run: theme-visual-preview-v3
↓
Output: HTML Artifact gallery rendering the designs
↓
Action: User ranks and selects themes to compile
```

### Stage 2: Template Design (Gold Template Builder v3)

You design the structure of a template:

```
Input: Description of template layout and structure
↓
Output: template_spec.md (machine-parseable spec)
↓
Validated by: validate_template_spec.py (must return SPEC OK)
```

**Tokens Used:**
```
{{CONTACT_NAME}}, {{TARGET_ROLE}}, {{EMPLOYER_ORG}}
Plus specific tokens based on document type (KSC, Resume, Cover Letter).
Read generate_document.py token constants for the definitive list.
```

**ATS Rules:**
- Single column layout only
- Forbidden: `•  ✔  ★  ❖  ●  ✅  ❌  |`
- Bullet style: plain hyphen `-` only
- AU terminology: `organisation`, `sector`, `position description`, `key selection criteria`

### Stage 2: Golden Master Creation

You create a Google Doc based on your spec (using template spec as a template) or via the JSON builder.

```
Input: template_spec.md OR theme JSON
↓
Create: Golden Master Google Doc in Google Docs
- Fill in static text, headings, structure
- Leave {{PLACEHOLDERS}} for pipeline substitution
↓
Document the: Google Doc ID
```

### Stage 3: Document Styling (Docs Style Auditor v3)

Before registering, validate the Golden Master's formatting:

```
Input: Google Doc ID (for live doc audit) + optional theme JSON
↓
Checks:
- Heading styles (native HEADING_1/HEADING_2, not bolded NORMAL_TEXT)
- Font family/sizes/spacing (checked against theme spec or Calibri defaults)
- No tables, images, text boxes
↓
Output: STYLE OK or list of FAIL items
```

### Stage 4: QA Validation (ATS Template QA v3)

Final comprehensive QA before live registration:

```
Input: spec file OR registered Golden Master Doc ID
↓
Two-stage process:
1. Mechanical validation (validate_template_spec.py)
   - Token validity, forbidden glyphs, AU terminology
2. Docs-API checks (after Golden Master built)
   - Structural and typographic verification via docs-style-auditor-v3
↓
Output: SPEC OK + STYLE PASS or detailed failure list
```

## Themed Variants (15+ Available)

The pipeline currently supports 15+ rich JSON theme definitions, split into conceptual families:
- `theme-01` to `theme-10`: Core design templates (Graphite, Citrus, Neon, etc.)
- `theme-21` to `theme-25`: Phase 3 advanced templates (Terminal, Broadside, etc.)
- Legacy/Standard variants: `contemporary_professional`, `professional_classic`, `modern_minimalist`, `chronological`, `hybrid`, `warm_impact`, `copper_teal_circuit`.

When running `docs-style-auditor-v3` against a themed document, ALWAYS pass the `--theme path/to/theme.json` flag so the auditor validates against the correct specific font/spacing values defined in the theme's `visualConfig`, rather than rejecting them for not being Calibri.

## Trigger Guidance

Use this skill when the user mentions:
- "Create a new template"
- "Design a template spec"
- "Audit my Golden Master"
- "Check if this template is ATS-safe"
- "I built a Golden Master doc, now what?"
- "This template isn't working, debug it"
- "Build themed resume variants"
- "Validate a template before registration"
- "Review my pipeline code changes"

## Success Criteria

### Template Design (Gold Template Builder v3)
✓ Spec file produced  
✓ validate_template_spec.py returns `SPEC OK`  

### Document Formatting (Docs Style Auditor v3)
✓ Heading styles: Native HEADING_1/HEADING_2  
✓ Typography matches spec or theme JSON exactly  
✓ No tables, images, or text boxes  
✓ Script returns `STYLE OK`

### QA Validation (ATS Template QA v3)
✓ Spec passes mechanical validation  
✓ All Docs-API checks pass  
✓ Template is production-ready for registration
