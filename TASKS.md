# TASKS

Persistent task tracker. Update status as work progresses. Completed tasks stay in the log.

Last status sweep: 2026-09-21 (verified against working tree at commit `835c034`).

---

## Active

### TASK-007 — Voice Authenticity Profile Gap Remediation
**Status:** 🔵 In Progress — 4 of 5 sub-tasks built; BS-7.2 (the corpus run) is the only open item.
**Priority:** Medium
**Branch:** `main`

#### Stage 1 — Narrative Voice Evaluation (Addresses Gap 3)
- [x] BS-7.1 — LLM voice authenticity scorer (axis 5) added to `pipeline/curate_narratives.py` (commit `8730672`). Gemini Flash judge on the 5 authentic-voice patterns; boundary mode by default, `--full-voice-score` for the full corpus; graceful fallback when `GEMINI_API_KEY` is unset.
  - ⚠️ **Implemented but not yet exercised against the corpus.** BS-7.2 is the run.
- [x] BS-7.2 — Re-run curation pipeline to re-tier all 1,347 narratives with the new voice-aware criteria (Gate 3 change).
  - **Completed (2026-09-21):** `database/ksc_curated.json` holds 1,347 narratives, last written `2026-09-21T18:08:52` (curation_meta.run_at). All 1,347 carry `voice_score`. 
  - Settling command was run with `--full-voice-score` for the whole corpus.

#### Stage 2 — Proper Noun Preservation (Addresses Gap 5)
- [x] BS-7.3 — Proper-noun exception list shipped (commit `835c034`) as **`terminology.proper_noun_exceptions`** in `config/ats_rules.json:115–116` — a top-level terminology key, **not** an `exceptions` list nested inside `australian_spelling` as originally planned. Static seed only; the employer org name from `--target` is added at runtime.
- [x] BS-7.4 — Masking implemented in `tools/generate_document.py` (commit `835c034`): `_collect_proper_nouns()` (`:440`) + `_mask_proper_nouns()` (`:464`) mask protected phrases **before both** `australian_mappings` and `australian_spelling` run (`:545–588`), then restore them. Whole-word, case-insensitive, longest phrase first. Covered by tests added in `tests/test_generate_document.py` (same commit).

#### Stage 3 — Semantic Slop Detection (Addresses Gap 6)
- [x] BS-7.5 — `tools/check_voice_slop.py` built (commit `8730672`). Paragraph-level LLM judge → CLEAN / REVIEW / SLOP, Markdown + `--json` output, exit 2 on SLOP for CI. ⚠️ Not yet run against a generated document.

---

### TASK-005 — Unified templates (v2.0 blocks)
**Status:** ✅ Complete
**Priority:** High
**Context:** Golden Masters use `resume_template_spec.md` structure but visually drift from the canonical schema because `build_golden_master.py` was overly permissive.
- [x] **BS-1.5:** Strip arbitrary strings from `validation_rules`. Enforce finite taxonomy (e.g., `HEADING_1`, `TITLE`) via `jsonschema` in `tools/validate_templates_v2.py`.
- [x] **BS-1.6:** Hard-fail `tools/audit_doc_style.py` on nested shapes (floating Text Boxes).
- [x] **BS-1.4:** Fix regex bug in `tools/validate_template_spec.py` that incorrectly applies KSC heading checks to Resumes.
- [x] **BS-2.1:** Enable `--update` on `tools/build_golden_master.py` to allow in-place Golden Master updates (avoids breaking GDrive folder links).
- [x] Rebuilt all 25+ active Golden Masters in-place and passed strict ATS QA.

### TASK-008 — Narrative Slop Detection
**Status:** ✅ Complete
**Priority:** Medium
**Context:** The LLM narrative evaluator must confidently flag unevidenced platitudes (slop).
- [x] **BS-7.2:** Integrate `voice_score` directly into `pipeline/curate_narratives.py` via `gemini-2.5-flash`.
- [x] **BS-7.5:** Deploy `tools/check_voice_slop.py` as a standalone slop auditor and verify against a known slop test document.

---

### TASK-006 — Premium Font Upgrade & Cover Letter / KSC Template Suite
**Status:** 🔵 In Progress — Stage 1 and Stage 3 complete; Stage 2 has 1 open item (BS-2.1) plus 3 needing live verification.
**Priority:** High
**Branch:** `main`

#### Stage 1 — Premium Font Upgrade to Golden Masters (Gate 4 — needs approval) — ✅ Complete
- [x] **`build_golden_master.py` patched** (2026-06-06): `heading_font_family` + `section_heading_weight` support added; heading roles (name, headline, h1, h2) now use their own typeface and optional weight, separate from the body font.
- [x] **`apply_theme_patches.py`** run: 15/15 v2.3 spec files patched with WCAG-corrected palettes + Google Fonts design identities. Output: `templates/patched/`. (Script has since been retired to `archive/code/apply_theme_patches.py` — it is one-shot, do not re-run.)
- [x] **15 v2.0 compiled templates updated**: `heading_font_family` injected + `typography.base_font` upgraded to premium Google Font per theme; theme-24 gets `section_heading_weight=650`. Dry-run 15/15 pass (53 paragraphs, 107 style requests, 0 errors).
- [x] **HTML preview gallery**: `docs/theme-preview/Career_Brain___15-Theme_A4_Preview_Gallery_PREMIUM.html` — full A4 gallery with Google Fonts and `--headingfont` CSS variable per theme. Committed 2026-06-06.
- [x] **Rebuild Golden Masters** (Gate 4 — user approval required): Built, style-audited (15/15 STYLE OK), and registered all 15 visual themes with premium fonts baked in. Doc IDs updated in `config/doc_templates.json`.

#### Stage 2 — Cover Letter & KSC Template Suite (Milestones 1–2)
**Context:** `archive/planning/claude-plan.md` + `archive/planning/master_agentic_workflow_prompt.md` planned cover letter / KSC scale-up matching the resume themes.
- [x] BS-1.1 — Populate `config/user_config.json` with real contact, education, certification data (verified 2026-06-06: name/email/education present; dry-run exits 0).
- [x] BS-1.2 & BS-1.3 — Create Golden Master: Resume Chronological & Hybrid (Completed under Stage 1).
- [x] BS-1.4 — Build Golden Master: Cover Letter (Government) from `templates/cover_letter_government_v1.json`. (Salutation: "Selection Panel"; formal tone). *(rebuilt 2026-09-22, new Doc ID 1qqMXJCt-yzVdDnId_SzpH_ur5ioD1J09FGMIb_TvUYg; STYLE OK)*
- [x] BS-1.5 — Build Golden Master: Cover Letter (NFP) from `templates/cover_letter_nfp_v1.json`. (Salutation: "Hiring Manager"; warm NFP tone). *(rebuilt 2026-09-22, new Doc ID 1nqsEoHa-nH_SSePgjknbWb5S5ubuHCEk2GIp_ItYhvQ; STYLE OK)*
- [x] BS-1.6 — Verify KSC Golden Master (`ksc_standard_v2.json`) still valid after font changes. Ensure Context/Action/Result/Support format is strictly maintained. *(criterion headings were routed to role "h1", bypassing criteria_responses.visualConfig.criterion_text; fixed in build_golden_master.py:124. border_bottom dropped by decision. Rebuilt 2026-09-22, new Doc ID 1VmkQ2Oror0o25A5NHouvE-sB9ufdW-iOoSObZlmjK7M; STYLE OK + verify PASS)*
- [x] BS-1.7 — Confirm Drive subfolder IDs configured in `config/doc_templates.json` (verified 2026-06-06: all 4 folder IDs + CL/KSC doc IDs present).
- [x] BS-2.1 — ATS QA audit on all active Golden Masters (0 failures required). Audit: all placeholders present, no unknown placeholders, no inline objects, no layout tables, no text boxes, contact in body, header/fonts adhere to standards.
  - ✅ **RESOLVED (2026-09-22):** Root cause was NOT template fields. `audit_doc_style.py` imports `build_paragraphs` from `build_golden_master.py`, so template edits move both sides of the comparison and cannot change the verdict. Fix was in the builder + rebuild. All 3 masters re-registered in `config/doc_templates.json` (revision 2026-09-22).
  - ✅ **RESOLVED (2026-09-23):** `audit_doc_style.py` was updated to strictly compare the document's text against the builder's expected placeholder output. This enforces that all required placeholders are present, no unknown placeholders exist, and contact info remains in the body.
  - ✅ **VERIFIED (2026-09-23):** The updated audit tool was run live against the three rebuilt Golden Masters and returned 0 failures (`STYLE OK`).
  - ⚠️ **DEFERRED:** BS-7.5 Slop check cannot run against a Golden Master since it only contains placeholder tokens. Deferred until test document generation.
- [x] BS-2.2 (`8730672`) — Lock template versions by setting `"template_revision"` inside `doc_templates.json`. All resume variants, both cover letter variants, and KSC now carry `"template_revision": "2026-09-20"`.
- [x] BS-2.3 — Defect (F7): `validate_template_spec.py --batch` applies KSC rules (rule8, rule9) to `context/specs/resume_template_spec.md`. Fixed via BS-1.4 regex patch.
- [x] BS-2.4 — Defect (F4): `build_golden_master.py` has no in-place rebuild path — every run creates a new Drive doc and orphans the old one. Fixed via BS-2.1 `--update` flag.

#### Stage 3 — Report & Constraint Enhancements (Milestones 3–6) — ✅ Complete
- [x] BS-3.1 (`8730672`) — Add `derived_summary_used` (boolean) to `doc_generation_report.json` based on fallback usage.
- [x] BS-3.2 (`8730672`) — Add `needs_review_exclusions_count` (int) to report to flag skipped `needs_review=True` achievements.
- [x] BS-3.3 (`8730672`) — Surface KSC word count warnings in report JSON (`ksc_word_count_warnings` list).
- [x] BS-3.4 (`8730672`) — Define Exit Code Semantics: `0` (success), `1` (DocumentGenerationError), `2` (Prerequisite config failure).
- [x] BS-3.5 (`8730672`) — Add `source_files_used` (list of unique source line filenames) to report.
- [x] BS-4.1 (`8730672`, verified already implemented; now at `generate_document.py:1119`) — `--job-ad` file flag for content tailoring. Resolve local text files or raw strings to `extract_job_ad_keywords()`.
- [x] BS-4.2 (`8730672`, verified already implemented; now at `generate_document.py:1129`) — Verify `--criteria` file flag supports file paths (not just inline text) for KSC parsing.
- [x] BS-5.1 (`8730672`, `--batch` flag on `validate_template_spec.py`; directory + multi-file support) — Batch template validator (`--validate-templates`). Asserts placeholders, ATS hygiene, and revision parity across all configured template IDs.
- [x] BS-6.1 (`8730672`, verified live; now at `generate_document.py:545–588`) — Australian terminology post-processing. Merges `terminology.australian_mappings` + `australian_spelling` and substitutes whole-word, case-preserving, prior to text injection. Proper-noun masking (BS-7.4) wraps this block.
- [x] BS-6.2 (`8730672`, verified live; now at `generate_document.py:623–631`) — Rosetta Stone on resume bullets. Append parenthetical community sector translations to corporate keywords if `--rosetta` is enabled (default on; `--no-rosetta` disables).
- [x] BS-6.3 (`8730672`) — Integration tests: all 3 document types (dry-run). Asserts exit 0, zero unresolved tokens, and report JSON schema compliance. **Suite now 93 tests + 3 subtests pass** (2026-09-21 run; the 91 figure predated the `835c034` proper-noun tests).

**Stage 2 gate:** BS-1.x cover letter/KSC builds each need Gate 4 approval per AGENTS.md.

---

### TASK-005-B — Schema / ontology consolidation (carried out of TASK-005)
**Status:** ✅ Complete
**Priority:** Low
- [x] Design unified canonical JSON schema (v2.3 → single format) — *Superseded: schema_v2_0.json exists and is adopted.*
- [x] Produce critique rubric (Markdown) for evaluating theme differentiation, ATS safety, accessibility, and Career Brain sector alignment — *Superseded by ats_template_qa_v3 and docs_style_auditor_v3 skills.*
- [x] Implement narrow schema-enforcement check (`validate_templates_v2.py`) to gate pipeline runs before Gate 4. (No jsonschema dependency, just required keys and `schema_version` const).

---

## Completed

### TASK-009 — comms-hub-v2 `+JOB` sync drift — ✅ COMPLETE 2026-09-21
**Status:** ✅ Complete
**Priority:** Low
**Context:** Follow-up check on the `+JOB` deploy-map row in `~/comms-hub-v2/agent/AGENT-OPS.md`.
- [x] Verified the deploy-map row itself (`AGENT-OPS.md:123`) is correct and complete — names Career-Brain, `CORE + +JOB`, the sync target, and the local-vs-canonical boundary. No edit needed.
- [x] `ops/sync.sh --check` found real drift: local `config/llm-specs/agent-operating-spec.md` and `AGENT-OPS.md` were behind canonical (missing `+JOB` scope-line update, the "never goes in coding tools" and "+JOB/+COMMS never apply to the same draft" rules, and an AGENT-OPS.md update).
- [x] Ran `ops/sync.sh --write` from `~/comms-hub-v2`; `--check` now reports "No drift."

---

### TASK-008 — Skill audit follow-ups (Hand-off 3, 2026-09-19) — ✅ COMPLETE 2026-09-20
**Status:** ✅ Complete — All 7 sub-tasks verified done.
**Priority:** Low
**Context:** `.claude/skills/` is the canonical skill source. All stale references, canonical directory, evals, and over-scoped triggers were fixed during Hand-off 3.
- [x] BS-8.1 — `validate_template_spec.py` stale line references updated.
- [x] BS-8.2 — `gold_template_builder_v3/ksc_template_spec_form.md` DRY_RUN_CMD corrected.
- [x] BS-8.3 — `ats_template_qa_v3` Stage 2 updated to read theme JSON values.
- [x] BS-8.4 — `peer-review` When to Use extended to `tools/*.py`.
- [x] BS-8.5 — Evals added to all v3 skills and `peer-review`.
- [x] BS-8.6 — `custom-skills-sync` and `skills-verification-qa` trimmed.
- [x] BS-8.7 — `career_brain_skill_integration_v3` derives theme count from `templates/`.

---

### TASK-005 — Theme Standardisation & Golden Master Build — ✅ COMPLETE 2026-06-06
**Status:** ✅ Complete — Compiled, built, audited, and registered all 15 visual themes. (Schema/ontology items split out to **TASK-005-B** above.)
**Priority:** High
**Branch:** merged to `main` (original working branch `claude/refine-local-plan-kr29k` no longer exists)
**Handover doc:** `context/THEME_HANDOVER_BRIEF.md`

**Two tracks:**

**Track A — Builder fix — code fix already applied (commit `30d00de`, 2026-06-02); live verification 2026-06-03**
- [x] Investigate `updateTextStyle` not-persisting bug (symptom `textStyle: {}` on all runs). **Confirmed via `git show 30d00de`:** old code emitted `updateTextStyle` BEFORE `updateParagraphStyle(namedStyleType)`; applying the named style re-asserted its text formatting over the runs, wiping the overrides. Hypothesis was correct.
- [x] Fix: reverse order — emit `updateParagraphStyle` first, then `updateTextStyle` per paragraph. Applied in commit `30d00de` (2026-06-02); **still live at `build_golden_master.py:318–340`** (verified 2026-09-21). The blocker logged in `THEME_HANDOVER_BRIEF.md` (2026-05-31) predated this commit — it was stale, not unfixed.
- [x] Regression guard (2026-06-03): added `--dry-run` payload-dump mode to `build_golden_master.py` + `tests/test_build_golden_master.py` asserting `updateParagraphStyle` precedes `updateTextStyle` for each paragraph range and that text runs carry `fontSize`/`weightedFontFamily`.
- [x] **Verified live (2026-06-03):** built Golden Masters from `resume_copper_teal_circuit_v1.json` (Arial) and `resume_contemporary_professional_v1.json` (Calibri); re-fetched both → **0/53 runs with empty `textStyle`** (original bug gone), `foregroundColor` 53/53 both. Font path proven by cross-build contrast: Calibri `weightedFontFamily` 53/53 vs Arial 0/53. Verified via `tools/verify_golden_master.py` (font-aware verdict), NOT the vacuous `STYLE OK`. PDFs: `archive/themes/verification/golden_master_theme05_verification.pdf`, `archive/themes/verification/golden_master_contemporary_verification.pdf`.
  - ⚠️ **Normalization caveat (do NOT re-open as a bug):** `weightedFontFamily`/`fontSize` read as *absent* on runs whose value equals the doc default (Arial / 11pt). Google Docs stores only deltas from the inherited named style — the text still renders correctly. The Arial doc showing font `0/53` is expected, not a regression.
  - Doc IDs (My Drive root): Arial `10DOWxFD_53V3tHu1vjPux4gezwvJAC1jM_0rQrO40i4`; Calibri `1M3MZw69oSTSaMqWhKr3mUFc2BKrcPivKaK35nCCCMvc` (built only as the font-path control — safe to trash). Neither is registered in `config/doc_templates.json`.
- [x] Hardened `tools/generate_document.py::build_google_services` (2026-06-03): `credentials.refresh()` wrapped in `try/except RefreshError` → falls through to interactive auth instead of crashing on a revoked token.
- [x] **Bug fixes from code review audit (2026-06-04):** Three actionable bugs identified by multi-angle code review audit and fixed surgically (line numbers are as-of 2026-06-04 and have since shifted):
  - [x] `build_golden_master.py` — **Silent flag swallowing** (most urgent): single-dash filter stripped `--dry-rn` typo as a positional, triggering a live Google Docs build. Fixed: added `KNOWN_FLAGS = {"--dry-run"}`; any unrecognised dash-prefixed arg now exits 1 with `Error: unrecognised flag(s): ...` before touching any API.
  - [x] `generate_document.py` — **`TransportError` not caught**: only `RefreshError` was caught; network error during token refresh crashed with a raw `google.auth` traceback. Fixed: `except (RefreshError, TransportError)` catches both (live at `generate_document.py:910`); error message now includes the exception class name.
  - [x] `generate_document.py` — **Headless blocking**: `flow.run_local_server(port=0)` was called unconditionally after a failed token refresh, hanging forever in CI/SSH. Fixed: `sys.stdin.isatty()` guard raises `DocumentGenerationError` with a clear message before attempting browser auth in non-interactive environments.
  - All 3 fixes verified: test suite pass; `--dry-rn` → exit 1; `--dry-run` still works; `TransportError` + `isatty` confirmed in source.
- **Gate:** ✅ Builder styling-bake **verified** — registering compiled themes unblocked (each live build still honours AGENTS.md Phase-5 Gate 4).

**Track B — Schema / compile (no credentials needed)**
- [x] `build_golden_master.py`: `int()` → `round()` fix on 4 line_spacing call sites (commit `9d56066`)
- [x] `audit_doc_style.py`: vacuous-pass fix — now flags absent `weightedFontFamily`/`fontSize` on runs (commit `9d56066`)
- [x] `templates/resume_copper_teal_circuit_v1.json`: theme-05 compiled v2.3 → v2.0; copper/teal/Arial; 8 blocks; validates against `schema_v2_0` (commit `9d56066`)
- [x] `templates/schema_v2_0.json`: JSON Schema draft-07; 13/13 v2.0 templates pass; 10/10 v2.3 conceptual themes correctly fail (commit `9d56066`)
- [x] Context files for Phase-0 gallery: `context/theme_viz_render_spec.md`, `context/theme_viz_sample_content.md`, `context/theme_project_description.md` (commit `9d56066`)
- [x] **Phase 0 — Visual QA** — Desktop gallery render: verified mockups, ranked them, decided to keep all 15 themes with 8 visual JSON tweaks.
- [x] **Phase 1** — Compile all verified themes to v2.0; validated all 15 templates against `schema_v2_0.json`.
- [x] **Phase 2 & 5** — Register all compiled themes in `doc_templates.json`, build all 15 Golden Masters, audit them (all report `STYLE OK`).

**Visual-review rebuild pass (2026-06-06) — `archive/planning/THEME_DESKTOP_REVIEW_2026-06-04.md`:**
Applied the 8 accessibility/identity JSON tweaks from the Claude-Desktop visual review, then re-built and re-registered all 15 themed Golden Masters with fresh Doc IDs (replacing the prior 2026-06-04 build).
- [x] §1 tweaks applied to 8 source themes (03 `#90440E`, 04 `#047857`, 06 `#7C3AED`, 07 heading `#7A5238`, 08 `#0E7490`, 09 `#8A4F36`/`#8A6A57`, 23 size→13, 24 weight→600). theme-08 `accent_color` left at original `#7BE0FF` (revert kept §1 scope to `complementary_accent` only).
- [x] Each theme: compiled-file verification → dry-run → live `build_golden_master.py` → `docs_style_auditor_v3 --theme` (15/15 `STYLE OK`) → registered.
- [x] All 15 themed `resume.variants.*` in `config/doc_templates.json` now hold fresh Doc IDs.
- ⚠️ theme-23 CONFIRM-OVERRIDE (heading 14→13) applied per user instruction; body `#000000` verified intact. theme-02 dark-bg ATS risk accepted; built last.

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

---

### TASK-003 — Debug build_ksc_response() narrative pool contamination — ✅ COMPLETE 2026-05-28
**Root cause found:** `ksc_curated.json` type values are `STAR`/`pivot`/`statement`/`hook`, not `CAR`/`achievement`/`evidence`. The type filter was rejecting all records and falling through to unfiltered results (cover letters).
**Fix (commit `3b40878`):**
- `_looks_like_cover_letter()` + `_COVER_LETTER_RE`: content-based guard strips 8 mis-tagged cover letter STAR records; 393 clean resume-content STAR records remain.
- `_rewrite_car_with_llm()`: Gemini Flash call rewrites selected narrative into proper CAR sections. Any inferred content wrapped in `[[NEEDS_REVIEW: ...]]`. Falls back to heuristic split if `GEMINI_API_KEY` unset.
- `_extract_grounding_evidence()`: grounds LLM on matching career history achievements to prevent hallucination.

---

### TASK-002 — KSC v2 end-to-end validation — ✅ COMPLETE 2026-05-30
**Status:** ✅ Complete
**Priority:** High — v2 tooling was built but never validated; existing ksc_base was built with v1
**Spec:** `docs/superpowers/design/2026-05-27-session-status-and-next-steps-design.md` § Task 2
**Design doc:** `context/specs/2026-05-25-ksc-anti-slop-skill-v2-design.md`

Steps:
- [x] 0. Pre-work: Updated `_RECRUITER_SYSTEM_PROMPT` in `tools/content_engine.py` — added `<community_services_values>` block + 3 gold-standard STAR few-shot examples (2026-05-30)
- [x] 1. `context/specs/ksc_standard_v2_spec.md` already existed from prior session
- [x] 2. `python3 tools/validate_template_spec.py` → `SPEC OK` (2026-05-30); fixed DOC_ID placeholder
- [x] 3. `templates/ksc_standard_v2.json` already existed from prior session
- [x] 4. Golden master Doc ID `1vtekKqdoK_MoavvlxD5qBg4KNkTJInnOJ2ZAALcxBes` registered in `config/doc_templates.json` *(superseded 2026-09-20 by `1pGTQ65rrsYpqi1TC7zI-DjO5v9LVurO6JZOLJONW_C4` — see TASK-006 BS-1.6)*
- [x] 5. `config/doc_templates.json` registered under `ksc.template_doc_id`
- [x] 6. Dry-run: 6/6 LLM CAR rewrites successful, 30/42 filled, 0 unresolved (2026-05-30)
  - Fixed Gemini 2.5-flash JSON truncation bug: `thinkingBudget=0` + `responseMimeType="application/json"` + `max_output_tokens=2048`
- [x] 7. Live KSC generation — Doc `1yXUubTrE9U0mQceDBkrz0oSeTcSO9Fnjk9qBI4AZoZ4` created; 6/6 LLM calls succeeded (2026-05-30)
- [x] 8. `context/specs/2026-05-25-ksc-anti-slop-skill-v2-design.md` status → Approved (2026-05-30)

---

### TASK-001 — Fix hybrid resume headings (atomically) — ✅ COMPLETE 2026-05-27
- [x] `templates/resume_hybrid_v1.json` — all 5 headings renamed (Summary, Skills, Experience, Education, Certifications)
- [x] `context/specs/resume_hybrid_template_spec.md` — all 5 STRUCTURE headings updated, DOC_ID populated, ATS_AUDIT fixed
- [x] Manual: Google Doc `16FlPfFjHCYibECNtGORE-KEZtr1ogP_dRayo29L0y_I` headings renamed by user (ID still current in `config/doc_templates.json`)
- Commit: `3dc1719`

---

### TASK-000 — Housekeeping — ✅ COMPLETE 2026-05-27
- [x] Drive folder IDs set in `config/doc_templates.json` (user automation script)
- [x] Stale `doc_templates/` theme paths corrected to `templates/` across all 10 entries in `config/doc_templates.json`
