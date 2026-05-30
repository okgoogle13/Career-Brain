# TASKS

Persistent task tracker. Update status as work progresses. Completed tasks stay in the log.

---

## Active

### TASK-004 — Database Quality Sweep & Narrative Taxonomy — ✅ COMPLETE 2026-05-30
**Status:** ✅ Complete
**Priority:** High — Garbage in, garbage out mitigation
**Progress:**
- [x] `pipeline/audit_and_repair_database.py` — built (deterministic rules + two-track Gemini LLM)
- [x] `pipeline/compile_brain.py` — Pydantic models extended with audit fields; fingerprint-aware merge logic added; `needs_review` added to `_AUDIT_FIELDS`
- [x] `tools/content_engine.py` — `_bullet_text()` updated to prefer `suggested_rewrite`; migrated to `google-genai` SDK
- [x] Dry-run executed → `database/quality_audit_report_draft.md` generated (12 stratified samples, live LLM rewrites confirmed)
- [x] `needs_review` idempotency fix — selective reset: only clears `archived_fragment` flags when bullet no longer qualifies; preserves `compile_brain.py` metric-injection flags
- [x] SDK migration — `google-generativeai` → `google-genai` 2.7.0 (code + environment); old package uninstalled
- [x] Full sweep run — `python3 pipeline/audit_and_repair_database.py --write` (2026-05-30)
  - First pass: 2,364 items processed | 1,547 fixed | 1,012 LLM rewrites | 270 lived experience flags | 254 archived fragments (Backup: `database/backups/20260530_020209/`)
  - Incremental STAR result pass (2026-05-30): Surgically updated `should_process()` to check all 2,363 items and incrementally run Gemini LLM rewrites for the 53 qualifying STAR narratives missing results.
  - Backup: `database/backups/20260530_192945/`
  - Report: `database/quality_audit_report.md`
- [x] STAR narrative gap detection — extend auditor to flag narratives missing a clear Result clause; built, verified, and executed.
- [x] `_RECRUITER_SYSTEM_PROMPT` updated — Community Services Values block + 3 gold-standard STAR few-shot examples added (2026-05-30)

**Problem Description:** A deep audit of `career_history_enriched.json` (1,017 items) and `ksc_curated.json` (1,347 items) found numerous data quality defects. Specifically, the 665 `statement` type narratives (initially flagged as "lacking outcome language") were delineated via sequential reasoning into:
1. **Valid Lived Experience (113)**: Intentional identity-grounded claims (preserve/upgrade).
2. **Mislabelled Outcome Statements (104)**: Actually contain outcome verbs, should be STAR/achievement type (reclassify).
3. **Qualification Fragments (23)**: Structural resume elements, not KSC evidence (archive).
4. **Role Descriptions (19)**: Valid context but missing results (flag for LLM review).
5. **Generic Filler (14)**: Clichés harming KSC quality (demote/archive).
6. **Unclassified (396)**: Mostly structural resume headers or bullet lists masquerading as narratives (archive).
**Resolution Plan:** `pipeline/audit_and_repair_database.py` applies deterministic fixes (markdown stripping, glyph removal, lived-experience flagging, CAR quality scoring) followed by a two-track Gemini Flash LLM pass. Use `domain_knowledge_insights.md` as reference for KSC SAO/STAR standards, inclusive language, and action verb bank.

### TASK-002 — KSC v2 end-to-end validation — ✅ COMPLETE 2026-05-30
**Status:** ✅ Complete
**Priority:** High — v2 tooling is built but never validated; existing ksc_base was built with v1
**Spec:** `docs/superpowers/specs/2026-05-27-session-status-and-next-steps-design.md` § Task 2
**Design doc:** `context/specs/2026-05-25-ksc-anti-slop-skill-v2-design.md`
**Leveraging Old Knowledge (Gemini):** Before live generation, update `_RECRUITER_SYSTEM_PROMPT` in `content_engine.py` to enforce Community Services Values. Provide the Gold Standard STAR KSC responses from `archive/Chromebook Downloads/ai_studio_code.txt` as few-shot examples so the LLM perfectly replicates the Australian sector tone and structure.

Steps:
- [x] 0. Pre-work: Updated `_RECRUITER_SYSTEM_PROMPT` in `tools/content_engine.py` — added `<community_services_values>` block + 3 gold-standard STAR few-shot examples (2026-05-30)
- [x] 1. `context/specs/ksc_standard_v2_spec.md` already existed from prior session
- [x] 2. `python3 tools/validate_template_spec.py` → `SPEC OK` (2026-05-30); fixed DOC_ID placeholder
- [x] 3. `templates/ksc_standard_v2.json` already existed from prior session
- [x] 4. Golden master Doc ID `1vtekKqdoK_MoavvlxD5qBg4KNkTJInnOJ2ZAALcxBes` already in `config/doc_templates.json`
- [x] 5. `config/doc_templates.json` already registered under `ksc.template_doc_id`
- [x] 6. Dry-run: 6/6 LLM CAR rewrites successful, 30/42 filled, 0 unresolved (2026-05-30)
  - Fixed Gemini 2.5-flash JSON truncation bug: `thinkingBudget=0` + `responseMimeType="application/json"` + `max_output_tokens=2048`
- [x] 7. Live KSC generation — Doc `1yXUubTrE9U0mQceDBkrz0oSeTcSO9Fnjk9qBI4AZoZ4` created; 6/6 LLM calls succeeded (2026-05-30)
- [x] 8. `context/specs/2026-05-25-ksc-anti-slop-skill-v2-design.md` status → Approved (2026-05-30)

**Gate:** Do not proceed past Step 2 until validator returns exit 0.

**Blocked at Step 7 → Unblocked 2026-05-28:** TASK-003 resolved. CAR content is now clean. Step 8 requires one clean live generation with `GEMINI_API_KEY` set to confirm LLM rewrite output before marking design Approved.

**To complete Step 8:** Set `GEMINI_API_KEY`, run live generation, inspect that context/action/result fields contain coherent CAR paragraphs (not raw bullets), then mark `context/specs/2026-05-25-ksc-anti-slop-skill-v2-design.md` status Approved.

---

## Completed

### TASK-003 — Debug build_ksc_response() narrative pool contamination — 2026-05-28
**Root cause found:** `ksc_curated.json` type values are `STAR`/`pivot`/`statement`/`hook`, not `CAR`/`achievement`/`evidence`. The type filter was rejecting all records and falling through to unfiltered results (cover letters).
**Fix (commit `3b40878`):**
- `_looks_like_cover_letter()` + `_COVER_LETTER_RE`: content-based guard strips 8 mis-tagged cover letter STAR records; 393 clean resume-content STAR records remain.
- `_rewrite_car_with_llm()`: Gemini Flash call rewrites selected narrative into proper CAR sections. Any inferred content wrapped in `[[NEEDS_REVIEW: ...]]`. Falls back to heuristic split if `GEMINI_API_KEY` unset.
- `_extract_grounding_evidence()`: grounds LLM on matching career history achievements to prevent hallucination.

---

### TASK-001 — Fix hybrid resume headings (atomically) — 2026-05-27
- [x] `templates/resume_hybrid_v1.json` — all 5 headings renamed (Summary, Skills, Experience, Education, Certifications)
- [x] `context/specs/resume_hybrid_template_spec.md` — all 5 STRUCTURE headings updated, DOC_ID populated, ATS_AUDIT fixed
- [x] Manual: Google Doc `16FlPfFjHCYibECNtGORE-KEZtr1ogP_dRayo29L0y_I` headings renamed by user
- Commit: `3dc1719`

---

### TASK-000 — Housekeeping (2026-05-27)
- [x] Drive folder IDs set in `config/doc_templates.json` (user automation script)
- [x] Stale `doc_templates/` theme paths corrected to `templates/` across all 10 entries in `config/doc_templates.json`
