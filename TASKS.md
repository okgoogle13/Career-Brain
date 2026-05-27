# TASKS

Persistent task tracker. Update status as work progresses. Completed tasks stay in the log.

---

## Active

### TASK-002 — KSC v2 end-to-end validation
**Status:** Ready to execute
**Priority:** High — v2 tooling is built but never validated; existing ksc_base was built with v1
**Spec:** `docs/superpowers/specs/2026-05-27-session-status-and-next-steps-design.md` § Task 2
**Design doc:** `context/specs/2026-05-25-ksc-anti-slop-skill-v2-design.md`

Steps:
- [ ] 1. Invoke `gold_template_builder_v3` → produce `context/specs/ksc_standard_v2_spec.md`
- [ ] 2. Run `python3 tools/validate_template_spec.py context/specs/ksc_standard_v2_spec.md` — iterate until `SPEC OK`
- [ ] 3. Translate validated spec → `templates/ksc_standard_v2.json` (follow `templates/THEME_SPEC_GUIDE.md`)
- [ ] 4. Run `python3 tools/build_golden_master.py templates/ksc_standard_v2.json` — capture Doc ID
- [ ] 5. Update `config/doc_templates.json` with new Doc ID under `ksc.variants.standard`
- [ ] 6. Run dry-run: `python3 tools/generate_document.py --type ksc --target "Test Role at Test Org" --criteria <file> --dry-run`
- [ ] 7. Run one live KSC generation — inspect output
- [ ] 8. Mark `context/specs/2026-05-25-ksc-anti-slop-skill-v2-design.md` status as Approved

**Gate:** Do not proceed past Step 2 until validator returns exit 0.

**Blocked at Step 7:** Live generation confirmed HEADING_1 structure is correct (Issue 1 resolved). Body content (result, support_bullets) is still being populated with cover letter boilerplate and raw contact text. Root cause is in `build_ksc_response()` — see TASK-003. Step 8 is blocked until TASK-003 resolves.

---

### TASK-003 — Debug build_ksc_response() narrative pool contamination
**Status:** Ready to investigate
**Priority:** High — blocks TASK-002 Step 8 and all live KSC generation quality
**Raised:** 2026-05-27

**Symptom:** `result` and `support_bullet` fields in generated KSC documents contain cover letter boilerplate ("I would love to discuss..."), Bank Australia cover letter fragments, and raw contact text instead of CAR narrative content.

**Suspected root cause:** `build_ksc_response()` in `tools/content_engine.py` calls `select_narratives()` with `narrative_types=["STAR", "CAR", "achievement", "evidence"]` (primary) and falls back to `["STAR", "CAR", "achievement", "evidence"]` with broadened competency matching. Neither call restricts the narrative source file — the full `narratives` list passed in appears to include cover letter hooks and contact text, not just KSC-curated narratives.

**Hypothesis to verify:**
- What file does `generate_document.py` load `narratives` from? Is it `ksc_curated.json` or a shared `narratives.json` that contains all narrative types including hooks and cover letter paragraphs?
- Does `select_narratives()` correctly filter on `narrative_type` field when `narrative_types` is specified, or is the `narrative_type` field absent/misnamed in the source data?
- Is the `_build_ksc_values()` call passing the correct narratives dict?

**Investigation steps:**
- [ ] 1. Find which file `generate_document.py` loads as `narratives` for doc_type=ksc (grep `load_json`, `NARRATIVES_FILE`, `narratives_path`)
- [ ] 2. Inspect that file — check `narrative_type` field values present across records
- [ ] 3. Trace `select_narratives()` with the actual narrative pool — confirm whether type filtering is working
- [ ] 4. Fix: ensure `build_ksc_response()` only draws from narratives with `narrative_type` in `["STAR", "CAR", "achievement", "evidence"]`, or load from the correct source file if narratives are segregated by file
- [ ] 5. Re-run live KSC generation — confirm result and support_bullet fields contain clean CAR content
- [ ] 6. On clean output: close TASK-003, unblock TASK-002 Step 8

---

## Completed

### TASK-001 — Fix hybrid resume headings (atomically) — 2026-05-27
- [x] `templates/resume_hybrid_v1.json` — all 5 headings renamed (Summary, Skills, Experience, Education, Certifications)
- [x] `context/specs/resume_hybrid_template_spec.md` — all 5 STRUCTURE headings updated, DOC_ID populated, ATS_AUDIT fixed
- [x] Manual: Google Doc `16FlPfFjHCYibECNtGORE-KEZtr1ogP_dRayo29L0y_I` headings renamed by user
- Commit: `3dc1719`

---

### TASK-000 — Housekeeping (2026-05-27)
- [x] Drive folder IDs set in `config/doc_templates.json` (user automation script)
- [x] Stale `doc_templates/` theme paths corrected to `templates/` across all 10 entries in `config/doc_templates.json`
