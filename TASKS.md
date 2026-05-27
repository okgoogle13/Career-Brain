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
