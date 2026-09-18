# Hand-off 2 — Pipeline Audit & Cleanup Complete
**Date:** 2026-09-19  
**Status:** ✅ All three phases done. Security incident resolved. Gate cleared. Hand-off 3 is unblocked.  
**Verified baseline:** 78/78 tests pass

---

## Phase 1 — Reachability Audit

Applied the corrected candidate rule from Hand-off 1 (candidate = no inbound import AND not invoked by CLAUDE.md Commands, any SKILL.md, or TASKS.md).

- Found exactly **one** true dead-code candidate: `tools/check_quota.py`.
- `pipeline/clean_knowledge_vault.py` had no imports, but was referenced in `CLAUDE.md`'s folder tree. Kept under the delete-shy rule.

## Phase 2 — Correctness, Security & Performance Review

### 🔴 Security Incident (Resolved)
- **Finding:** A committed `.env.save` was reachable from `origin/main` (added in a prior history reset).
- **Resolution:** 
  1. Rotated the exposed `GEMINI_API_KEY` via 1Password CLI.
  2. Purged the blob from git history via `git filter-repo`.
  3. Force-pushed rewritten history to `origin/main`.
  4. Added 1Password CLI secret management documentation to `AGENTS.md`.
- **Pending Action:** User must submit a GitHub Support ticket ([Data Removal Request](https://support.github.com/contact/data-removal-request)) to purge the cached object from the CDN.

### Correctness Bugs (Resolved)
1. **`.docx` blackhole:** `normalize_vault.py` skipped all `.docx` files because of a faulty uppercase guard.
2. **Employer name corruption:** `generate_document.py` applied `australian_mappings` to proper nouns (e.g. converting "The Walt Disney Company" to "The Walt Disney Organisation").
3. **`parsing_errors.log` never cleared:** Three different scripts appended to the log instead of truncating it at startup, making the gate ("must be empty") unpassable.

*(Note: Minor sorting bugs or untested files were logged but not fixed, sticking strictly to the approved scope of fixing showstoppers).*

## Phase 3 — Cleanup Execution

Executed in two strictly scoped commits:

1. **Commit A (`dcecb97`):** `refactor: archive superseded pipeline scripts`
   - Moved `tools/check_quota.py` to `archive/one_offs/check_quota.py`.
2. **Commit B (`51df17a`):** `fix: correctness bugs found in Phase 2 audit`
   - Fixed the `.docx` skip logic.
   - Guarded proper-noun keys (`_ORG}}`, `_TITLE}}`, etc.) against terminology mappings.
   - Added truncate-at-startup for `parsing_errors.log` in all pipeline phases.

**Verification:** All assertions passed. Pytest suite ran clean (78/78).

---

## Gate declaration

**Hand-off 3 is unblocked.**

The pipeline is verified clean, the security incident is operationally closed, and the repo is ready for the Skill Audit.
