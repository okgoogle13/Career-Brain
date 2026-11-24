# Handover — Career-Brain Pipeline Unblock & Canonical Bank Build

**Date:** 2026-11-24  
**Strategy:** Approved **Option 5 (Phased Hybrid)** — clean `processed/` once into canonical local JSON banks (`answer_bank.local.json`, `career_history_enriched.json`), freeze Phases 0–3 as historical archive, keep Phase 5 local Google Docs generation clean, and optionally layer GCP GenAI App Builder credits for retrieval/grounding.

---

## 1. Key Findings (Verified)

- **Why `docs/voice/answer_bank.local.json` only has 17 stories (`S1`–`S17`):** It was hand-imported on `2026-11-12` from a Claude Duet proposal (not pipeline-generated). All 17 are `status: "confirmed"`, 12 carry open verification `flags`, 14 have `disclosure_tier: null`, and competencies have gaps (`0` `leadership`, `1` `conflict_resolution`, `1` `data_systems`, `2` `risk_de_escalation`, `2` `mdt_facilitation`).
- **Pipeline breakage audit on `database/ksc_curated.json` (`563` own-source records, all `vetted: false`):**
  - Of **73** Tier-1 (`27`) + Tier-2 (`46`) non-duplicate `STAR` records: **47 (64%)** are mis-tagged resume bullet blocks, **7 (10%)** are cover letters, **4 (5%)** are short framing snippets, and only **15 (21%)** are actual KSC narratives (6 overlap `S1`–`S17`, 4 are multi-criterion bundled chunks, ~5 are net-new leads — all flagged `no_metric`).
  - `config/narrative_curation.json` was simultaneously dropping 7 real own-authored `ksc__*` files + 16 dated resumes (because of `ksc__` prefixes) while letting third-party files (`Kassies_*`) slip through.
- **Red-tier safety catch in `processed/`:** A pathology lab report (`..._EUC_LFT_UDS_16.9.25.txt`, containing Medicare/DOB/lab markers) had landed under `processed/resumes__*`. It is now hard-blocked by both filename and content-level Red-tier gates in `tools/export_clean_corpus.py`.

---

## 2. What Was Completed

### Stage 1 — Local Scrubber & Corpus Packager (**Committed: `2ebbc64`**)
- Added `tools/export_clean_corpus.py` and `tests/test_export_clean_corpus.py`.
- Scanned `337` files in `processed/` → excluded `105` (non-own knowledge guides, `Kassies_*`, referee contact sheets, templates, pathology report, `final_combined_resumes` megafiles), redacted `452` contact/address hits, and generated git-ignored staging outputs in `scratch/clean_corpus/`:
  - `scratch/clean_corpus/own_ksc_and_letters.local.md` — **60** unique docs (`45` deduped), **293 KB**, **~74.2k tokens**, `verify_issues: []`
  - `scratch/clean_corpus/own_resumes.local.md` — **70** unique docs (`57` deduped), **615 KB**, **~108.4k tokens**, `verify_issues: []`
  - `scratch/clean_corpus/manifest.local.json` — full audit trail

### Stage 2 — Extraction Prompt Pack (**Ready for User Run**)
- Created `scratch/clean_corpus/stage2_extraction_prompts.md` (git-ignored) with copy-paste prompts and exact JSON schemas for:
  - **Pass A:** Expand `docs/voice/answer_bank.local.json` (`S18+`, `status: "needs_confirmation"`) targeting competency gaps + resolving open flags on `S1`–`S17`.
  - **Pass B:** Consolidate the `63` overlapping role entries in `database/career_history_enriched.json` against `config/career_roles.json`.

### Stage 3 — Targeted Phase 5 Fixes (**Implemented & Tested, Uncommitted**)
- `tools/content_engine.py` & `tools/generate_document.py`: Added `max_ksc_criteria` to `GenerationConfig` and `--max-ksc-criteria` CLI flag (default `6` for existing 6-slot templates; prevents silent truncation on 7–8+ criterion PDs).
- `tools/generate_document.py`: Added optional `pd_text` argument to `scan_voice_phrases()` (wired in `_build_ksc_values()`), exempting `review_phrases` mirrored verbatim from the PD/criterion while keeping `banned_phrases` and `overclaim_terms` strictly enforced.
- `tests/test_generate_document.py`: Added tests for both behaviors.

### Verification
- `.venv/bin/pytest tests/ -q` → **153 passed, 6 subtests passed** (1.63s)
- `.venv/bin/python tools/export_clean_corpus.py --dry-run` → `issues=NONE`

---

## 3. Current Git Status (`main`)

- **Committed (not pushed):** `2ebbc64` (`feat: add Stage 1 clean corpus scrubber and exporter`) — `tools/export_clean_corpus.py`, `tests/test_export_clean_corpus.py`.
- **Uncommitted Stage 3 changes:** `tools/content_engine.py`, `tools/generate_document.py`, `tests/test_generate_document.py`.
- **Pre-existing dirty files (do not blindly include in commits):** `README.md`, `TASKS.md`, `config/gemini_skill_system_prompt.md`, `database/`.
- **Git-ignored local staging outputs:** `scratch/clean_corpus/*` (verified ignored via `git check-ignore`).

---

## 4. Aligned Constraints & Available Credits

- **Static historical corpus:** Clean/extract `processed/` once; future roles/stories go directly into canonical JSON banks.
- **Day-to-day workflow:** Both interactive drafting (Claude Duet / Google AI Studio) and local `tools/generate_document.py` Google Docs export.
- **GCP Credit:** **\$1,401.15** *"Trial credit for GenAI App Builder"* (100% remaining, valid until **9 June 2027**) — strictly for Vertex AI Agent Builder / Agent Search / Discovery Engine (`RankService.rank()`, `check_grounding()`, search), **not** unrestricted Gemini LLM spend.

---

## 5. Next Steps

1. **Optional Stage 3 commit:** If requested, commit `tools/content_engine.py`, `tools/generate_document.py`, and `tests/test_generate_document.py` as a focused Conventional Commit (keep pre-existing dirty files separate; do not push without explicit approval).
2. **Stage 2 ingestion & human sign-off:** Once the user runs Pass A / Pass B from `scratch/clean_corpus/stage2_extraction_prompts.md` in Google AI Studio (Gemini 2.5 Pro, 1M context) or Claude Duet:
   - Validate returned JSON against `config/ats_rules.json` (Australian English, banned/review/overclaim checks) and `config/career_roles.json` (canonical dates/titles).
   - Keep new stories at `status: "needs_confirmation"` until the user confirms facts, dates, metrics, and `disclosure_tier` (1–4), plus resolves the 12 open flags on `S1`–`S17`.
   - Merge confirmed entries into `docs/voice/answer_bank.local.json` (and canonical roles if Pass B is run).
3. **Stage 4 (Optional, after Stage 2):** Wire stateless Discovery Engine `RankService.rank()` (cross-encoder + global bipartite KSC matching) and `check_grounding()` (hallucination / cross-role chimera detector) per `brainstormusingcredits.md` Proposals 1–2.

---

## 6. Guardrails for Incoming Agent

- Follow `CLAUDE.md` approval gates: never `git push`, run live Gemini/Google API calls, or touch `source_docs/`/`archive/` without explicit approval.
- Never print raw narrative text, PII, or full JSON engines in output; report counts, diffs, and redacted summaries only.
- `docs/voice/*.local.*` and `scratch/` must stay git-ignored.
