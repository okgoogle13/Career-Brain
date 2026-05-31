# Career Brain — Quality Audit Report
_Generated: 2026-05-30 19:27 | Mode: DRY-RUN SAMPLE (12 entries)_

## Summary
| Metric | Value |
|--------|-------|
| Total processed | 12 |
| Items with fixes | 8 |
| Lived experience flagged | 2 |
| LLM rewrites generated | 6 |

## Fix Type Counts
- `llm_rewrite`: 6
- `flagged_bad_action_verb`: 4
- `flagged_lived_experience`: 2
- `archived_fragment`: 2
- `missing_result`: 2
- `removed_markdown_glyphs`: 1

---

## Before / After

### [lived_experience] achievement
**Original:** Experienced Peer Worker specializing in community services with a strong background in project management and

**After deterministic fixes:** Experienced Peer Worker specializing in community services with a strong background in project management and

**LLM suggested rewrite:** Experienced Peer Worker specializing in community services with a strong background in

**Fixes applied:** `flagged_lived_experience`, `llm_rewrite`, `flagged_bad_action_verb`
**CAR score:** 2/5 | **Lived experience:** True

### [lived_experience] achievement
**Original:** Deep understanding of community needs and lived experience: I have a unique perspective on the challenges

**After deterministic fixes:** Deep understanding of community needs and lived experience: I have a unique perspective on the challenges

**LLM suggested rewrite:** My lived experience provides a deep understanding of community needs and

**Fixes applied:** `flagged_lived_experience`, `llm_rewrite`, `flagged_bad_action_verb`
**CAR score:** 2/5 | **Lived experience:** True

### [bad_action_verb] achievement
**Original:** Proven record of successful case management and strong people skills: In my previous role at Diamond Valley

**After deterministic fixes:** Proven record of successful case management and strong people skills: In my previous role at Diamond Valley

**LLM suggested rewrite:** {
  "context": "In my previous role at [[NEEDS

**Fixes applied:** `llm_rewrite`, `flagged_bad_action_verb`
**CAR score:** 2/5 | **Lived experience:** False

### [bad_action_verb] achievement
**Original:** Commitment to strengths-based practice and client-centred care: my approach to support is grounded in cultural

**After deterministic fixes:** Commitment to strengths-based practice and client-centred care: my approach to support is grounded in cultural

**LLM suggested rewrite:** {
  "context": "[[NEEDS_REVIEW: In a community

**Fixes applied:** `llm_rewrite`, `flagged_bad_action_verb`
**CAR score:** 2/5 | **Lived experience:** False

### [subjective_claim] achievement
**Original:** Used strong organisational skills to maintain accurate records, schedule follow-ups for clients, promote

**After deterministic fixes:** Used strong organisational skills to maintain accurate records, schedule follow-ups for clients, promote

**Fixes applied:** `none`
**CAR score:** 3/5 | **Lived experience:** False

### [subjective_claim] achievement
**Original:** Developed strong interpersonal skills and a deep understanding of community development principles.

**After deterministic fixes:** Developed strong interpersonal skills and a deep understanding of community development principles.

**Fixes applied:** `none`
**CAR score:** 3/5 | **Lived experience:** False

### [incomplete_car] achievement
**Original:** Significant professional and organizational skills: My 9+ years in banking and finance have developed a diverse

**After deterministic fixes:** Significant professional and organizational skills: My 9+ years in banking and finance have developed a diverse

**Fixes applied:** `none`
**CAR score:** 3/5 | **Lived experience:** False

### [incomplete_car] achievement
**Original:** Completed internship on the diversity and inclusion team responsible for culturally responsive practice across the headspace network of approx 150 sites nationally

**After deterministic fixes:** Completed internship on the diversity and inclusion team responsible for culturally responsive practice across the headspace network of approx 150 sites nationally

**Fixes applied:** `none`
**CAR score:** 3/5 | **Lived experience:** False

### [archived_fragment] achievement
**Original:** Led International Students Project, applying community development principles to

**After deterministic fixes:** Led International Students Project, applying community development principles to

**Fixes applied:** `archived_fragment`
**CAR score:** 2/5 | **Lived experience:** False

### [archived_fragment] achievement
**Original:** Employed de-escalation techniques to ensure client well-being and safety.

**After deterministic fixes:** Employed de-escalation techniques to ensure client well-being and safety.

**Fixes applied:** `archived_fragment`
**CAR score:** 2/5 | **Lived experience:** False

### [missing_result] narrative
**Original:** * Collaborated with 20 international students to conduct focus groups and gather qualitative data on client needs.
 * Coded participant responses and conducted a thematic analysis, contributing to a 50-page research findings report to inform culturally sensitive program design.

**After deterministic fixes:** * Collaborated with 20 international students to conduct focus groups and gather qualitative data on client needs.
 * Coded participant responses and conducted a thematic analysis, contributing to a 50-page research findings report to inform culturally sensitive program design.

**LLM suggested rewrite:** * Collaborated with 20 international students to conduct focus groups and gather qualitative data on client needs.
 * Coded participant responses and conducted a thematic analysis, contributing to a 50-page research findings report to inform culturally sensitive program design. [[NEEDS_REVIEW: The comprehensive findings from this report were subsequently adopted by the organisation, directly informing the development of new, culturally sensitive support programmes that better met the identified needs of international students.]]

**Fixes applied:** `missing_result`, `llm_rewrite`, `removed_markdown_glyphs`
**CAR score:** 3/5 | **Lived experience:** False

### [missing_result] narrative
**Original:** ### Instructions for Completion
Fill in each section with your specific experiences, using concrete details and quantifiable outcomes wherever possible. Organize examples by competency areas to enable easy reference during application development.

**After deterministic fixes:** ### Instructions for Completion
Fill in each section with your specific experiences, using concrete details and quantifiable outcomes wherever possible. Organize examples by competency areas to enable easy reference during application development.

**LLM suggested rewrite:** ### Instructions for Completion
Fill in each section with your specific experiences, using concrete details and quantifiable outcomes wherever possible. Organize examples by competency areas to enable easy reference during application development. [[NEEDS_REVIEW: This structured approach ensures that all key selection criteria are addressed comprehensively, significantly enhancing the

**Fixes applied:** `llm_rewrite`, `missing_result`
**CAR score:** 3/5 | **Lived experience:** False

---

> **Next step:** Review this report, then run `python3 pipeline/audit_and_repair_database.py --write` to apply to the full database.