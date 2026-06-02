# TASKS

Persistent task tracker. Update status as work progresses. Completed tasks stay in the log.

---

## Active

### TASK-005 — Theme Standardisation & Golden Master Build — 🔄 IN PROGRESS
**Status:** 🔄 In progress — PR `claude/refine-local-plan-kr29k` partially merged context
**Priority:** High
**Branch:** `claude/refine-local-plan-kr29k`
**Handover doc:** `context/THEME_HANDOVER_BRIEF.md`

**Two tracks:**

**Track A — Builder fix (needs Google credentials / local session)**
- [ ] Investigate `updateTextStyle` not-persisting bug: symptom is `textStyle: {}` on all runs after build; hypothesis is `updateParagraphStyle(namedStyleType)` in same batchUpdate resets run-level overrides
- [ ] Minimal repro: 2-para test doc, re-fetch, confirm runs empty
- [ ] Fix: reverse order — emit `updateParagraphStyle` first, then `updateTextStyle` per paragraph in `build_golden_master.py`
- [ ] Verify fix against orphan doc `1vWpzuBOyyKrLWkHWT0bUHH5EQPMBtAKKFAeyGcPNZPc`
- [ ] Re-audit: `python3 tools/audit_doc_style.py <DOC_ID> --theme templates/resume_copper_teal_circuit_v1.json`
- **Gate:** Do NOT register new themes or build Golden Masters until this is verified ✋

**Track B — Schema / compile (no credentials needed) — partially complete**
- [x] `build_golden_master.py`: `int()` → `round()` fix on 4 line_spacing call sites (commit `9d56066`)
- [x] `audit_doc_style.py`: vacuous-pass fix — now flags absent `weightedFontFamily`/`fontSize` on runs (commit `9d56066`)
- [x] `templates/resume_copper_teal_circuit_v1.json`: theme-05 compiled v2.3 → v2.0; copper/teal/Arial; 8 blocks; validates against `schema_v2_0` (commit `9d56066`)
- [x] `templates/schema_v2_0.json`: JSON Schema draft-07; 13/13 v2.0 templates pass; 10/10 v2.3 conceptual themes correctly fail (commit `9d56066`)
- [x] Context files for Phase-0 Desktop gallery: `context/theme_viz_render_spec.md`, `context/theme_viz_sample_content.md`, `context/theme_project_description.md` (commit `9d56066`)
- [ ] **Phase 0** — Run Desktop gallery render (this session / Claude.ai Desktop): produce HTML mockups for all 10 v2.3 themes using `theme_viz_render_spec.md` + `theme_viz_sample_content.md`; return ranked keep set
- [ ] **Phase 1** — Compile kept themes (01–04, 06–10) to v2.0 using `resume_copper_teal_circuit_v1.json` as reference skeleton; validate each against `schema_v2_0.json`; gated on Track A builder fix
- [ ] Register compiled themes in `config/doc_templates.json`; build + audit Golden Masters; gated on Track A builder fix

**Schema / ontology work (this session — Claude Desktop chat, no credentials):**
- [ ] Design unified canonical JSON schema (v2.3 → single format) — merge legacy 300–400 line templates with newer ~200 line v2.3 themes
- [ ] Produce critique rubric (Markdown) for evaluating theme differentiation, ATS safety, accessibility, and Career Brain sector alignment
- [ ] Normalise all 10 v2.3 themes against unified schema; surface incompatible fields under `legacy_fields` rather than silently dropping

**Phase 0 note — switching from Claude Code Desktop to standard Claude Desktop chat:**
Phase 0 (gallery render) is designed to run in **Claude.ai Desktop / Web chat** (this interface), not Claude Code. The 10 v2.3 theme JSONs and render spec are loaded as Project files. Produce the HTML gallery artifact here, rank themes, return the keep set to Claude Code for Phase 1 compilation.

---

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

### TASK-002 — KSC v2 end-to-end validation — ✅ COMPLETE 2026-05-30
**Status:** ✅ Complete
**Priority:** High — v2 tooling is built but never validated; existing ksc_base was built with v1
**Spec:** `docs/superpowers/specs/2026-05-27-session-status-and-next-steps-design.md` § Task 2
**Design doc:** `context/specs/2026-05-25-ksc-anti-slop-skill-v2-design.md`

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
