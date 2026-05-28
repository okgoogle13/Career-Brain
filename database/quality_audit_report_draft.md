# Career Brain — Quality Audit Report
_Generated: 2026-05-29 05:32 | Mode: DRY-RUN SAMPLE (10 entries)_

## Summary
| Metric | Value |
|--------|-------|
| Total processed | 10 |
| Items with fixes | 6 |
| Lived experience flagged | 3 |
| LLM rewrites generated | 0 |

## Fix Type Counts
- `flagged_bad_action_verb`: 6
- `flagged_lived_experience`: 3
- `removed_markdown_glyphs`: 2

---

## Before / After

### [formatting_artifact] achievement
**Original:** I offer a deep understanding of the community's needs.** As a queer, neurodivergent, non-binary person of colour, I have lived experience navigating the healthcare system and accessing support services, and I understand the challenges faced by marginalized communities.

**After deterministic fixes:** I offer a deep understanding of the community's needs. As a queer, neurodivergent, non-binary person of colour, I have lived experience navigating the healthcare system and accessing support services, and I understand the challenges faced by marginalized communities.

**Fixes applied:** `flagged_bad_action_verb`, `flagged_lived_experience`, `removed_markdown_glyphs`
**CAR score:** 2/5 | **Lived experience:** True

### [formatting_artifact] achievement
**Original:** **I possess strong interpersonal skills and experience in providing sensitive support.** In my previous role at Diamond Valley Community Support, I conducted over 400 client interviews, demonstrating my ability to build rapport, actively listen, and create a safe space for individuals from diverse b

**After deterministic fixes:** I possess strong interpersonal skills and experience in providing sensitive support. In my previous role at Diamond Valley Community Support, I conducted over 400 client interviews, demonstrating my ability to build rapport, actively listen, and create a safe space for individuals from diverse backg

**Fixes applied:** `flagged_bad_action_verb`, `removed_markdown_glyphs`
**CAR score:** 3/5 | **Lived experience:** False

### [lived_experience] achievement
**Original:** Experienced Peer Worker specializing in community services with a strong background in project management and

**After deterministic fixes:** Experienced Peer Worker specializing in community services with a strong background in project management and

**Fixes applied:** `flagged_lived_experience`, `flagged_bad_action_verb`
**CAR score:** 2/5 | **Lived experience:** True

### [lived_experience] achievement
**Original:** Deep understanding of community needs and lived experience: I have a unique perspective on the challenges

**After deterministic fixes:** Deep understanding of community needs and lived experience: I have a unique perspective on the challenges

**Fixes applied:** `flagged_lived_experience`, `flagged_bad_action_verb`
**CAR score:** 2/5 | **Lived experience:** True

### [bad_action_verb] achievement
**Original:** Proven record of successful case management and strong people skills: In my previous role at Diamond Valley

**After deterministic fixes:** Proven record of successful case management and strong people skills: In my previous role at Diamond Valley

**Fixes applied:** `flagged_bad_action_verb`
**CAR score:** 2/5 | **Lived experience:** False

### [bad_action_verb] achievement
**Original:** Commitment to strengths-based practice and client-centred care: my approach to support is grounded in cultural

**After deterministic fixes:** Commitment to strengths-based practice and client-centred care: my approach to support is grounded in cultural

**Fixes applied:** `flagged_bad_action_verb`
**CAR score:** 2/5 | **Lived experience:** False

### [subjective_claim] achievement
**Original:** Used strong organisational skills to maintain accurate records, schedule follow-ups for clients, promote

**After deterministic fixes:** Used strong organisational skills to maintain accurate records, schedule follow-ups for clients, promote

**Fixes applied:** `none`
**CAR score:** 3/5 | **Lived experience:** False

### [subjective_claim] achievement
**Original:** Professional Skills: Strong organisational and

**After deterministic fixes:** Professional Skills: Strong organisational and

**Fixes applied:** `none`
**CAR score:** 2/5 | **Lived experience:** False

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

---

> **Next step:** Review this report, then run `python3 pipeline/audit_and_repair_database.py --write` to apply to the full database.