# Claude Review Companion: Google Docs ATS Templates

## Purpose
This document is a review companion for Claude Code. It aligns:
1. Gemini's strategy memo: `google_docs_ats_templates_strategy.md`
2. Current implementation in this repo: Phase 5 `generate_document.py` and related artifacts

Use this as the authoritative context for a meticulous defect/risk review.

> **Status as of 2026-05-22:** Initial review completed. Patches applied. See `walkthrough.md` for full outcomes.

---

## Source Inputs for Review

### Gemini Strategy Reference
- `/Users/okgoogle13/.gemini/antigravity-ide/brain/0666d05e-cac5-45ef-b06f-a8ff6cb41b76/google_docs_ats_templates_strategy.md`

### Implemented Repo Files
- `generate_document.py`
- `tests/test_generate_document.py`
- `doc_templates.json`
- `.env.example`
- `README.md`
- `requirements.txt`
- `skills/ats_template_qa/SKILL.md` _(new — added post-review)_

---

## Current Implementation Snapshot (Phase 5)

### What Was Built
- New script `generate_document.py` as Phase 5:
  - Preflight reads/parses:
    - `output/career_history_enriched.json`
    - `output/ksc_curated.json`
    - optional `output/skills_and_taxonomy.json`
  - Resolves Google template doc ID from `doc_templates.json`
  - Builds deterministic placeholder values
  - Clones Golden Master via Drive API
  - Replaces placeholders via Docs API `batchUpdate`
  - Postflight scans resulting doc for unresolved `{{...}}` tokens
  - Writes redacted report JSON

### Supported CLI
- `python3 generate_document.py --target "Role" --template resume|cover_letter --out-report output/doc_generation_report.json`
- Supports `--template-variant`, `--config`, `--output-dir`, `--summary`, `--dry-run`

### Placeholder Contract (v1)
- Shared:
  - `{{TARGET_ROLE}}`
  - `{{SUMMARY}}`
- Resume:
  - `{{BULLET_1}}` ... `{{BULLET_6}}`
- Cover letter:
  - `{{KSC_RESPONSE_1}}` ... `{{KSC_RESPONSE_3}}`

### Fail-Fast Rules Implemented
- Required source JSON missing or invalid -> error
- Template mapping missing/invalid -> error
- Required content missing:
  - resume requires at least `{{BULLET_1}}`
  - cover letter requires at least `{{KSC_RESPONSE_1}}`
  - both require `{{TARGET_ROLE}}` and `{{SUMMARY}}` (summary can be derived)
- Unresolved placeholders after replacement are reported

### Logging/PII Posture
- Logs only counts/status/doc ID or dry-run marker
- No full bullets or narrative text emitted in terminal logs
- Report contains metadata and stats, not raw source dumps

---

## Strategy Fit Against Gemini Memo

### Chosen Strategy
- **Strategy 1: Golden Master cloning via Docs API** is implemented.

### Deferred / Not Implemented in v1
- Strategy 2: Docs Sidebar add-on
- Strategy 3: Pandoc/local DOCX bridge
- Strategy 4: Full component vault assembly logic

### Review Focus
Claude should verify that Strategy 1 implementation is production-safe and that it does not accidentally depend on assumptions from deferred strategies.

---

## ATS Compliance Review Criteria

Note: runtime code does not enforce visual ATS formatting; template discipline does.

Claude should explicitly verify and comment on:
1. Whether the system relies on Google Doc template hygiene (headings, single column, no text boxes/tables for core data, standard fonts).
2. Whether placeholder replacement can break ATS readability (e.g., unintended linebreak collapse, insertion into header/footer, token collisions).
3. Whether unresolved token detection is sufficient for ATS-safe output confidence.
4. Whether report fields are enough for auditability across many templates.

---

## Test Coverage

Tests added or confirmed after review:
1. Deterministic ordering of mapped bullets/responses ✅
2. Missing required placeholder behavior ✅
3. Unresolved token detection ✅
4. Stable `batchUpdate` request ordering ✅
5. `_extract_document_text` — verifies headers and footers are scanned ✅ _(added post-review)_
6. `clone_and_replace` — verifies `HttpError` is caught and wrapped as `DocumentGenerationError` ✅ _(added post-review)_

Still missing (lower priority):
- Variant config edge cases (e.g. `template_variant` not found)
- Placeholder collisions/duplicates in a real doc body
- Exit code semantics for operational workflows

---

## Risk Register

1. **Data quality risk** _(Open)_:
`_candidate_bullets` excludes `needs_review=true` bullets, which may reduce available content for some roles. No fallback or warning is emitted. Recommend adding a report warning when review-excluded bullets reduce the usable pool below the slot count.

2. **Summary derivation risk** _(Open)_:
Auto-summary is semantically generic. Recommend emitting a `derived_summary_used: true` flag in the run report to prompt the operator to supply `--summary` manually.

3. **Template drift risk across 10+ templates** _(Mitigated — framework in place)_:
`skills/ats_template_qa/SKILL.md` defines the linting protocol, but batch validation against real Google Doc IDs has not yet been executed. Risk remains until template IDs are configured and validated.

4. **Operational auth risk** _(Mitigated)_:
`HttpError` from Drive and Docs API calls is now caught in `clone_and_replace` and re-raised as `DocumentGenerationError` with the underlying API message. OAuth and service-account token expiry paths are unchanged.

5. **Postflight scope risk** _(Resolved)_:
`_extract_document_text` now walks `headers`, `footers`, and `footnotes` in addition to the document body. Covered by new unit test.

---

## Review Outcomes (Completed 2026-05-22)

**Ship readiness verdict:** ~~Conditionally Ready~~ → **Ready** _(after patches applied)_

Findings addressed:
1. ~~High: Postflight scanner ignores headers/footers~~ → **Fixed** (`generate_document.py:290`)
2. ~~Medium: Google API errors bubble as raw tracebacks~~ → **Fixed** (`generate_document.py:clone_and_replace`)
3. ~~Medium: No API error mock tests~~ → **Fixed** (`tests/test_generate_document.py`)
4. Low: Derived summaries are generic → **Open** (report flag recommended, not yet implemented)

For full detail, see: `walkthrough.md` in the Antigravity artifacts directory.

---

## Recommendation: Custom ATS Template Skill (for 10+ templates)

Given the target of at least 10 templates, a custom skill is recommended.

Minimum scope for that skill:
1. Define a versioned placeholder schema contract.
2. Add template lint checks (required placeholders present, no unknown placeholders).
3. Add ATS structure checklist checks (single column intent, heading usage guidance, prohibited layout patterns).
4. Add deterministic template QA report per template variant.
5. Add batch validation command for all template IDs in `doc_templates.json`.

This is the main control that will prevent template drift and inconsistent ATS outcomes at scale.

