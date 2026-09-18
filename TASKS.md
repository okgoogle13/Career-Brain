# TASKS

Persistent task tracker. Update status as work progresses. Completed tasks stay in the log.

---

## Active

### TASK-008 — Skill audit follow-ups (Hand-off 3, 2026-09-19)
**Status:** 🔵 Planned
**Priority:** Low
**Branch:** `main`
**Context:** `.claude/skills/` is the canonical skill source; `custom_skills/` (byte-identical duplicate) was removed and the superseded `career-brain-skill-integration` moved to `_archived_v1/career-brain-skill-integration_v2/`. Remaining gaps, one per line:
- [x] BS-8.1 — `tools/validate_template_spec.py:32,143` cite stale `generate_document.py:118-133`; the KSC block is now lines 127–144. Update comment/message (tools/ was off-limits in Hand-off 3).
- [ ] BS-8.2 — `gold_template_builder_v3/ksc_template_spec_form.md` `DRY_RUN_CMD` uses bare `generate_document.py`; change to `tools/generate_document.py` after confirming the validator doesn't match on it.
- [ ] BS-8.3 — `ats_template_qa_v3` Stage 2 hard-codes per-theme typography; replace with "read expected values from the theme JSON" to stop drift, and point Stage 2 at `tools/verify_golden_master.py` / `tools/audit_doc_style.py`.
- [ ] BS-8.4 — `peer-review` triggers only on `pipeline/`; extend "When to Use" to `tools/*.py` changes (e.g. `generate_document.py`, `audit_doc_style.py`).
- [ ] BS-8.5 — No `evals.json` for the v3 skills or `peer-review`; add 2–3 trigger/no-trigger prompts each (only the sync/verification skills have evals).
- [ ] BS-8.6 — `custom-skills-sync` (170 lines) and `skills-verification-qa` (242 lines) are Cowork-migration utilities with long example output; trim, or archive if Cowork sync is no longer used.
- [ ] BS-8.7 — `career_brain_skill_integration_v3` hard-codes "15+ themes" and theme families; derive from `templates/` instead.

---

### TASK-007 — Voice Authenticity Profile Gap Remediation
**Status:** 🔵 Planned
**Priority:** Medium
**Branch:** `main`

#### Stage 1 — Narrative Voice Evaluation (Addresses Gap 3)
- [ ] BS-7.1 — Enhance `pipeline/curate_narratives.py` to replace length/regex-based `quality_tier` with an LLM-based voice authenticity score using `voice-authenticity-profile.md` criteria.
- [ ] BS-7.2 — Re-run curation pipeline to re-tier all 1,346 narratives with the new voice-aware criteria (Gate 3 change).

#### Stage 2 — Proper Noun Preservation (Addresses Gap 5)
- [ ] BS-7.3 — Add an `exceptions` list to `terminology.australian_spelling` in `config/ats_rules.json` (e.g., "World Health Organization").
- [ ] BS-7.4 — Update substitution logic in `tools/generate_document.py` to bypass terms in the exceptions list, preserving proper noun casing and spelling.

#### Stage 3 — Semantic Slop Detection (Addresses Gap 6)
- [ ] BS-7.5 — Develop a post-generation semantic review tool or LLM judge to detect paraphrased slop that bypasses fixed-string checks.

---

### TASK-006 — Premium Font Upgrade & Cover Letter / KSC Template Suite
**Status:** 🔵 In Progress
**Priority:** High
**Branch:** `main`

#### Stage 1 — Premium Font Upgrade to Golden Masters (Gate 4 — needs approval)
- [x] **`build_golden_master.py` patched** (2026-06-06): `heading_font_family` + `section_heading_weight` support added; heading roles (name, headline, h1, h2) now use their own typeface and optional weight, separate from the body font.
- [x] **`apply_theme_patches.py`** run: 15/15 v2.3 spec files patched with WCAG-corrected palettes + Google Fonts design identities. Output: `templates/patched/`.
- [x] **15 v2.0 compiled templates updated**: `heading_font_family` injected + `typography.base_font` upgraded to premium Google Font per theme; theme-24 gets `section_heading_weight=650`. Dry-run 15/15 pass (53 paragraphs, 107 style requests, 0 errors).
- [x] **HTML preview gallery**: `Career_Brain___15-Theme_A4_Preview_Gallery_PREMIUM.html` — full A4 gallery with Google Fonts and `--headingfont` CSS variable per theme. Committed 2026-06-06.
- [x] **Rebuild Golden Masters** (Gate 4 — user approval required): Built, style-audited (15/15 STYLE OK), and registered all 15 visual themes with premium fonts baked in. Doc IDs updated in `config/doc_templates.json`.

#### Stage 2 — Cover Letter & KSC Template Suite (Milestones 1–2)
**Context:** `archive/planning/claude-plan.md` + `planning/master_agentic_workflow_prompt.md` planned cover letter / KSC scale-up matching the resume themes.
- [x] BS-1.1 — Populate `config/user_config.json` with real contact, education, certification data (verified 2026-06-06: name/email/education present; dry-run exits 0).
- [x] BS-1.2 & BS-1.3 — Create Golden Master: Resume Chronological & Hybrid (Completed under Stage 1).
- [ ] BS-1.4 — Build Golden Master: Cover Letter (Government) from `templates/cover_letter_government_v1.json`. (Salutation: "Selection Panel"; formal tone).
- [ ] BS-1.5 — Build Golden Master: Cover Letter (NFP) from `templates/cover_letter_nfp_v1.json`. (Salutation: "Hiring Manager"; warm NFP tone).
- [ ] BS-1.6 — Verify KSC Golden Master (`ksc_standard_v2.json`) still valid after font changes. Ensure Context/Action/Result/Support format is strictly maintained.
- [x] BS-1.7 — Confirm Drive subfolder IDs configured in `config/doc_templates.json` (verified 2026-06-06: all 4 folder IDs + CL/KSC doc IDs present).
- [ ] BS-2.1 — ATS QA audit on all active Golden Masters (0 failures required). Audit: all placeholders present, no unknown placeholders, no inline objects, no layout tables, no text boxes, contact in body, header/fonts adhere to standards.
- [ ] BS-2.2 — Lock template versions by setting `"template_revision"` inside `doc_templates.json`.

#### Stage 3 — Report & Constraint Enhancements (Milestones 3–6, deferred)
- [ ] BS-3.1 — Add `derived_summary_used` (boolean) to `doc_generation_report.json` based on fallback usage.
- [ ] BS-3.2 — Add `needs_review_exclusions_count` (int) to report to flag skipped `needs_review=True` achievements.
- [ ] BS-3.3 — Surface KSC word count warnings in report JSON (`ksc_word_count_warnings` list).
- [ ] BS-3.4 — Define Exit Code Semantics: `0` (success), `1` (DocumentGenerationError), `2` (Prerequisite config failure).
- [ ] BS-3.5 — Add `source_files_used` (list of unique source line filenames) to report.
- [ ] BS-4.1 — `--job-ad` file flag for content tailoring. Resolve local text files or raw strings to `extract_job_ad_keywords()`.
- [ ] BS-4.2 — Verify `--criteria` file flag supports file paths (not just inline text) for KSC parsing.
- [ ] BS-5.1 — Batch template validator (`--validate-templates`). Asserts placeholders, ATS hygiene, and revision parity across all configured template IDs.
- [ ] BS-6.1 — Australian terminology post-processing (`AU_TERMINOLOGY_MAP`). Replace US/corporate terms ("industry", "company") globally prior to text injection.
- [ ] BS-6.2 — Rosetta Stone on resume bullets. Append parenthetical community sector translations to corporate keywords if `--rosetta` is enabled.
- [ ] BS-6.3 — Integration tests: all 3 document types (dry-run). Asserts exit 0, zero unresolved tokens, and report JSON schema compliance.

**Stage 1 gate:** User approves Golden Master rebuild → execute sequentially per AGENTS.md Gate 4.
**Stage 2 gate:** BS-1.x cover letter/KSC builds each need Gate 4 approval per AGENTS.md.

---

### TASK-005 — Theme Standardisation & Golden Master Build — ✅ COMPLETE 2026-06-04
**Status:** ✅ Complete — Compiled, built, audited, and registered all 15 visual themes.
**Priority:** High
**Branch:** `claude/refine-local-plan-kr29k`
**Handover doc:** `context/THEME_HANDOVER_BRIEF.md`

**Two tracks:**

**Track A — Builder fix — code fix already applied (commit `30d00de`, 2026-06-02); live verification this session (2026-06-03)**
- [x] Investigate `updateTextStyle` not-persisting bug (symptom `textStyle: {}` on all runs). **Confirmed via `git show 30d00de`:** old code emitted `updateTextStyle` BEFORE `updateParagraphStyle(namedStyleType)`; applying the named style re-asserted its text formatting over the runs, wiping the overrides. Hypothesis was correct.
- [x] Fix: reverse order — emit `updateParagraphStyle` first, then `updateTextStyle` per paragraph. **Already applied in commit `30d00de` (2026-06-02)** ("fix text style sequence"), `build_golden_master.py:316-337`. The blocker logged below in `THEME_HANDOVER_BRIEF.md` (2026-05-31) predated this commit — it was stale, not unfixed.
- [x] Regression guard (2026-06-03): added `--dry-run` payload-dump mode to `build_golden_master.py` + `tests/test_build_golden_master.py` asserting `updateParagraphStyle` precedes `updateTextStyle` for each paragraph range and that text runs carry `fontSize`/`weightedFontFamily`.
- [x] **Verified live (2026-06-03):** built Golden Masters from `resume_copper_teal_circuit_v1.json` (Arial) and `resume_contemporary_professional_v1.json` (Calibri); re-fetched both → **0/53 runs with empty `textStyle`** (original bug gone), `foregroundColor` 53/53 both. Font path proven by cross-build contrast: Calibri `weightedFontFamily` 53/53 vs Arial 0/53. Verified via `tools/verify_golden_master.py` (font-aware verdict), NOT the vacuous `STYLE OK`. PDFs: `archive/verification/golden_master_*_verification.pdf`.
  - ⚠️ **Normalization caveat (do NOT re-open as a bug):** `weightedFontFamily`/`fontSize` read as *absent* on runs whose value equals the doc default (Arial / 11pt). Google Docs stores only deltas from the inherited named style — the text still renders correctly. The Arial doc showing font `0/53` is expected, not a regression.
  - Doc IDs (My Drive root): Arial `10DOWxFD_53V3tHu1vjPux4gezwvJAC1jM_0rQrO40i4`; Calibri `1M3MZw69oSTSaMqWhKr3mUFc2BKrcPivKaK35nCCCMvc` (built only as the font-path control — safe to trash).
- [x] Hardened `tools/generate_document.py::build_google_services` (2026-06-03): `credentials.refresh()` wrapped in `try/except RefreshError` → falls through to interactive auth instead of crashing on a revoked token.
- [x] **Bug fixes from code review audit (2026-06-04):** Three actionable bugs identified by multi-angle code review audit and fixed surgically:
  - [x] `build_golden_master.py` L344 — **Silent flag swallowing** (most urgent): single-dash filter stripped `--dry-rn` typo as a positional, triggering a live Google Docs build. Fixed: added `KNOWN_FLAGS = {"--dry-run"}`; any unrecognised dash-prefixed arg now exits 1 with `Error: unrecognised flag(s): ...` before touching any API.
  - [x] `generate_document.py` L795 — **`TransportError` not caught**: only `RefreshError` was caught; network error during token refresh crashed with a raw `google.auth` traceback. Fixed: `except (RefreshError, TransportError)` catches both; error message now includes the exception class name.
  - [x] `generate_document.py` L838 — **Headless blocking**: `flow.run_local_server(port=0)` was called unconditionally after a failed token refresh, hanging forever in CI/SSH. Fixed: `sys.stdin.isatty()` guard raises `DocumentGenerationError` with a clear message before attempting browser auth in non-interactive environments.
  - All 3 fixes verified: existing 3-test suite 3/3 pass; `--dry-rn` → exit 1; `--dry-run` still works; `TransportError` + `isatty` confirmed in source.
- **Gate:** ✅ Builder styling-bake **verified** — registering compiled themes is unblocked (each live build still honours AGENTS.md Phase-5 Gate 4).

**Track B — Schema / compile (no credentials needed) — partially complete**
- [x] `build_golden_master.py`: `int()` → `round()` fix on 4 line_spacing call sites (commit `9d56066`)
- [x] `audit_doc_style.py`: vacuous-pass fix — now flags absent `weightedFontFamily`/`fontSize` on runs (commit `9d56066`)
- [x] `templates/resume_copper_teal_circuit_v1.json`: theme-05 compiled v2.3 → v2.0; copper/teal/Arial; 8 blocks; validates against `schema_v2_0` (commit `9d56066`)
- [x] `templates/schema_v2_0.json`: JSON Schema draft-07; 13/13 v2.0 templates pass; 10/10 v2.3 conceptual themes correctly fail (commit `9d56066`)
- [x] Context files for Phase-0 Desktop gallery: `context/theme_viz_render_spec.md`, `context/theme_viz_sample_content.md`, `context/theme_project_description.md` (commit `9d56066`)
- [x] **Phase 0 — Visual QA** — Run Desktop gallery render: verified mockups, ranked them, and decided to keep all 15 themes with 8 visual JSON tweaks.
- [x] **Phase 1** — Compile all verified themes to v2.0; validated all 15 templates successfully against `schema_v2_0.json`.
- [x] **Phase 2 & 5** — Register all compiled themes in `doc_templates.json`, build all 15 Golden Masters, and audit them successfully (all report `STYLE OK`).

**Visual-review rebuild pass (2026-06-06) — `planning/THEME_DESKTOP_REVIEW_2026-06-04.md`:**
Applied the 8 accessibility/identity JSON tweaks from the Claude-Desktop visual review, then re-built and re-registered all 15 themed Golden Masters with fresh Doc IDs (replacing the prior 2026-06-04 build).
- [x] §1 tweaks applied to 8 source themes (03 `#90440E`, 04 `#047857`, 06 `#7C3AED`, 07 heading `#7A5238`, 08 `#0E7490`, 09 `#8A4F36`/`#8A6A57`, 23 size→13, 24 weight→600). theme-08 `accent_color` left at original `#7BE0FF` (revert kept §1 scope to `complementary_accent` only).
- [x] Each theme: compiled-file verification → dry-run → live `build_golden_master.py` → `docs_style_auditor_v3 --theme` (15/15 `STYLE OK`) → registered.
- [x] All 15 themed `resume.variants.*` in `config/doc_templates.json` now hold fresh Doc IDs.
- ⚠️ theme-23 CONFIRM-OVERRIDE (heading 14→13) applied per user instruction; body `#000000` verified intact. theme-02 dark-bg ATS risk accepted; built last.


**Schema / ontology work (this session — Claude Desktop chat, no credentials):**
- [ ] Design unified canonical JSON schema (v2.3 → single format) — merge legacy 300–400 line templates with newer ~200 line v2.3 themes
- [ ] Produce critique rubric (Markdown) for evaluating theme differentiation, ATS safety, accessibility, and Career Brain sector alignment
- [ ] Normalise all 15 v2.3 themes against unified schema; surface incompatible fields under `legacy_fields` rather than silently dropping

**Phase 0 note — switching from Claude Code Desktop to standard Claude Desktop chat:**
Phase 0 (gallery render) is designed to run in **Claude.ai Desktop / Web chat** (this interface), not Claude Code. The 15 v2.3 theme JSONs and render spec are loaded as Project files. Produce the HTML gallery artifact here, rank themes, return the keep set to Claude Code for Phase 1 compilation.

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
