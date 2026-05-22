---
name: ats-template-qa
description: Evaluates Google Docs ATS templates for placeholder hygiene and structural compliance.
---

# ATS Template QA Skill

## Overview
This skill provides instructions for AI agents to statically lint and QA Google Docs "Golden Master" templates intended for Applicant Tracking Systems (ATS) and the Career Brain pipeline.

## Placeholder Schema Contract (v1)

### Shared
- `{{TARGET_ROLE}}`
- `{{SUMMARY}}`

### Resume Templates
- `{{BULLET_1}}` through `{{BULLET_6}}`

### Cover Letter Templates
- `{{KSC_RESPONSE_1}}` through `{{KSC_RESPONSE_3}}`

## Validation Protocol

When asked to validate ATS templates, the agent MUST execute the following checks:

### 1. Placeholder Validation
- **Required Tokens:** Verify all required placeholders for the template type are present.
- **Unknown Tokens:** Scan for any `{{...}}` tokens that do NOT match the schema contract above and flag them as critical errors.
- **Placement:** Warn if placeholders are inside complex nested tables. Placeholders in Headers/Footers are acceptable.

### 2. ATS Structure Compliance
- **Layout:** Enforce single-column intent. Multi-column tables are highly risky for ATS parsing.
- **Containers:** Reject the use of text boxes or shapes for core contact or experience data.
- **Semantics:** Encourage the use of native Google Docs Heading styles (Heading 1, Heading 2) rather than just bolding Normal text.

### 3. Batch Verification
If the user requests a full batch validation:
1. Read `doc_templates.json`.
2. Extract every `template_doc_id` (including nested variants).
3. Using the Docs API (via a script or direct interaction), extract the text and structure of each Golden Master.
4. Output a comprehensive, deterministic Markdown report grading each template on the criteria above.
