# Career Brain — Theme Standardisation Handover Brief

**Date:** 2026-05-31  
**Branch:** `claude/refine-local-plan-kr29k`

---

## Two tracks

```
Track A — Builder fix (local session, needs Google credentials)
  └─ Investigate updateTextStyle not-persisting bug
  └─ Minimal repro: 2-para test doc, re-fetch, confirm run textStyle empty
  └─ Fix: reverse request order per paragraph (updateParagraphStyle first, then updateTextStyle)
  └─ Verify against orphan doc 1vWpzuBOyyKrLWkHWT0bUHH5EQPMBtAKKFAeyGcPNZPc
  └─ Gate: do NOT register new themes until this is verified

Track B — Schema / compile (Claude Code, no credentials needed)
  └─ DONE: int()→round() fix in build_golden_master.py (3 call sites)
  └─ DONE: audit_doc_style.py vacuous-pass fix (now requires explicit font + size on runs)
  └─ DONE: theme-05 compiled → templates/resume_copper_teal_circuit_v1.json
  └─ DONE: templates/schema_v2_0.json — validates all 13 v2.0 templates; all 10 v2.3 themes fail
  └─ DONE: context files for Phase 0 Desktop preview
```

---

## Status table

| Item | Status | Notes |
|---|---|---|
| `build_golden_master.py` int→round fix | ✅ Done | Lines 209, 219, 247, 258 |
| `audit_doc_style.py` vacuous-pass fix | ✅ Done | Now flags absent font/size on runs |
| `templates/resume_copper_teal_circuit_v1.json` | ✅ Done | theme-05 compiled to v2.0; 8 blocks; copper/teal palette |
| `templates/schema_v2_0.json` | ✅ Done | Draft-07 JSON Schema; 13/13 v2.0 pass; 10/10 v2.3 fail |
| `context/theme_viz_render_spec.md` | ✅ Done | Desktop render instructions |
| `context/theme_viz_sample_content.md` | ✅ Done | Fixed AU sample resume for all mockups |
| `context/theme_project_description.md` | ✅ Done | Desktop Project custom instructions |
| `updateTextStyle` not-persisting bug | ⚠️ Needs local session | Hypothesis: updateParagraphStyle(namedStyleType) resets run styles applied earlier in same batchUpdate |
| Register theme-05 in doc_templates.json | ⏳ Blocked | Gated on builder fix |
| Compile remaining themes (01–04, 06–10) | ⏳ Blocked | Gated on Phase 0 "keep" set from Desktop |
| Build Golden Masters for new themes | ⏳ Blocked | Gated on builder fix |

---

## Phase 0 → Phase 1 handoff protocol

1. Open a Claude Desktop Project with these files loaded:
   - `templates/theme-01-*.json` … `templates/theme-10-*.json`
   - `context/theme_viz_render_spec.md`
   - `context/theme_viz_sample_content.md`
   - `context/theme_project_description.md`

2. Run the render task (instructions in `theme_viz_render_spec.md`). Get the gallery HTML and "keep set".

3. Return to Claude Code with the keep set. Compile each kept theme to v2.0 using:
   - Reference: `templates/resume_copper_teal_circuit_v1.json` (theme-05 as working example)
   - Mapping rules: inches → cm margins (`× 2.54`), palette tokens → block visualConfig colors
   - Validate each against `templates/schema_v2_0.json` before proceeding
   - Gate: builder fix must be verified before building any Golden Master

---

## updateTextStyle bug — investigation approach (for local session)

**Symptom:** After `build_golden_master.py` runs, fetching the doc back shows `textStyle: {}` on every run — font, size, color not set. All 6 registered masters are in this state; they all render identically (Google default font/size).

**Leading hypothesis:** In the batchUpdate, `updateTextStyle` is emitted first, then `updateParagraphStyle` with `namedStyleType`. Google Docs API may reset run-level overrides when a named style is assigned to the paragraph. Fix: swap the order per paragraph — emit `updateParagraphStyle` first, then `updateTextStyle`.

**Test procedure:**
```python
# 1. Build a 2-paragraph test doc with just two updateTextStyle calls (no updateParagraphStyle)
# 2. Re-fetch the doc; check textStyle on runs
# 3. If runs are populated: add updateParagraphStyle before/after; re-test
# 4. Fix build_golden_master.py: emit paragraphStyle, then textStyle
# 5. Rebuild orphan doc 1vWpzuBOyyKrLWkHWT0bUHH5EQPMBtAKKFAeyGcPNZPc
# 6. Re-audit: python3 tools/audit_doc_style.py <DOC_ID> --theme templates/resume_copper_teal_circuit_v1.json
```

---

## File inventory

```
templates/
  schema_v2_0.json                      ← NEW: validates v2.0 templates
  resume_copper_teal_circuit_v1.json    ← NEW: theme-05 compiled to v2.0
  theme-01-graphite-ledger.json         ← v2.3 conceptual (not yet compiled)
  ...
  theme-10-rainbow-minimal.json         ← v2.3 conceptual (not yet compiled)
  resume_contemporary_professional_v1.json  ← reference skeleton for compilation

tools/
  build_golden_master.py                ← PATCHED: round() not int()
  audit_doc_style.py                    ← PATCHED: explicit font/size absence check

context/
  THEME_HANDOVER_BRIEF.md               ← this file
  theme_viz_render_spec.md              ← Desktop render instructions
  theme_viz_sample_content.md           ← Fixed sample content
  theme_project_description.md          ← Desktop Project custom instructions
```
