# Hand-off 1 — Pre-flight Complete
**Date:** 2026-09-19  
**Status:** ✅ All three steps done. Gate cleared. Hand-off 2 is unblocked.  
**Session model:** Claude Sonnet 4.6 (Thinking)  
**Verified baseline:** 78/78 tests pass · 12.26 s

---

## Step 1 — /interview-me: Scope decision

> *"Step 1 confirmed (Hand-off 2 only · delete-shy). No advisor() call — the hand-off explicitly rules it out."*

| Dimension | Decision |
|---|---|
| Phases in scope this pass | Hand-off 2 only |
| Archiving aggression | **delete-shy** |
| `advisor()` | Not called — Hand-off 1 rules it out |

---

## Step 2 — Stale-reference triage

Scanned all 11 SKILL.md files under `.claude/skills/` plus the 3 under `custom_skills/`. **Report only — nothing changed.**

### A. The two "known broken" items in the hand-off are themselves stale

| Claim in Hand-off 1 prompt | Verified reality |
|---|---|
| `gold_template_builder_v3` mandates output matching `skills/gold_template_builder_v2/ksc_template_spec_form.md`, which does not exist | **Already fixed.** `SKILL.md:16` references `ksc_template_spec_form.md` bare (same-directory relative) — and that file **exists** (2,551 bytes, May 26). No `gold_template_builder_v2` path appears anywhere. Hand-off 3 Step 1's fix instruction is also stale. |
| `pipeline/audit_and_repair_database.py` exists, peer-review depends on it, CLAUDE.md omits it | **Confirmed.** Script exists; `peer-review/SKILL.md` names it; `CLAUDE.md:52-60` folder tree omits it. |

### B. Genuinely broken references found

| # | File | Reference | Problem |
|---|---|---|---|
| 1 | `docs_style_auditor_v3/SKILL.md:51,56` | `python3 audit_doc_style.py` | Bare name; script is at `tools/audit_doc_style.py`. Copy-paste fails from repo root. |
| 2 | `docs_style_auditor_v3/SKILL.md:56` | `--theme doc_templates/resume_<theme>_v1.json` | `doc_templates/` does not exist. Theme JSONs live in `templates/`; `doc_templates.json` is a config file in `config/`. Two distinct errors on one line. |
| 3 | `career_brain_skill_integration_v3/SKILL.md:69,122,156` | bare `validate_template_spec.py` | Lives at `tools/`. |
| 4 | `career-brain-skill-integration/SKILL.md:38,103,131,252` | bare `validate_template_spec.py` | Same ×4, plus the `custom_skills/` duplicate. |
| 5 | `ats_template_qa_v3/SKILL.md:3,12` / `gold_template_builder_v3:3,10` | bare `validate_template_spec.py` | Inconsistent within the same file — correct at line 19/58 (`tools/validate_template_spec.py`), wrong in prose. |
| 6 | `custom_skills/` (6 tracked files) | duplicate source of truth | diff confirms all three SKILL.md and all three evals.json are byte-identical to their `.claude/skills/` counterparts. Two canonical directories, no marker for which wins. |

### C. Checked and clean — do not "fix" these

- `theme_visual_preview_v3` — all three refs verified present: `context/theme_viz_render_spec.md`, `context/theme_viz_sample_content.md`, `templates/theme-01-graphite-ledger.json`.
- `peer-review` — `pipeline/compile_brain.py`, `pipeline/audit_and_repair_database.py` both present.
- `skills-verification-qa`'s `SKILL_VERIFICATION_REPORT*.md` / `SYNC_MANIFEST.md`, and `custom-skills-sync`'s `helper.py` / `reference-file.md`: generated outputs and illustrative tree diagrams, not input paths. Not stale.
- `ksc_template_spec.md` / `template_spec.md` in the integration skills are named pipeline outputs, not files expected on disk.
- `_archived_v1/` skills reference only existing config JSONs — and are archived regardless.

### D. Repo-state corrections the hand-off doc gets wrong

| Doc claim | Verified reality |
|---|---|
| "214 tracked files" (Hand-off 4 verify gate) | **212** (`git ls-files | wc -l`) |
| Hand-off 5: `git rm --cached prompt-skills-library` and `git rm --cached .env.save` | Neither is tracked. Both exist on disk, untracked. Both commands will **fail**. |
| Hand-off 5: change `.gitignore` `^\.env$` → `.env*` | **Already done** — `.gitignore:33` is `.env*`. |
| Hand-off 2 verify: `.venv/bin/pip install pytest && ...` | `.venv/bin/pytest` already exists. Unnecessary write inside a phase whose contract is "present the diff". |
| "27.8 MB of JSON" | `database/` is 26 MB. Immaterial but the number was presented as measured. |

---

## Step 3 — /critique-plan: Hand-off 2

### Verdict

> **Proceed with changes** — the plan's gates and do-not-touch list are sound, but Phase 1's stated candidate rule ("any file with no inbound references") is **wrong for this repo** and would sweep 20 of 33 live `.py` files into the Phase 3 candidate set.

### Core finding: content_engine.py is the single load-bearing import

*Does archiving any candidate break `tools/generate_document.py` or `pipeline/audit_and_repair_database.py`?*

**Exactly one file: `tools/content_engine.py`.** It is the sole shared dependency of both:

```
tools/content_engine.py
  ├── tools/generate_document.py:42        from content_engine import (...)
  │     ├── tools/build_golden_master.py:387   (lazy)
  │     │     └── tools/audit_doc_style.py:135 (lazy)
  │     └── tests/test_generate_document.py:4,14
  └── pipeline/audit_and_repair_database.py:45  from tools.content_engine import _looks_like_cover_letter
```

Every other `.py` in the repo is an import leaf. The literal answer is "no named candidate breaks them" — but only because Hand-off 2 derives its candidates in Phase 1, and that derivation is the defect.

### All critique findings

| # | Finding | Class | Action |
|---|---|---|---|
| 1 | Phase 1's candidate rule flags 20/33 live `.py` files as dead (CLI entry-points have zero inbound imports by design) | **Valid + Actionable** | Replace with: *candidate = no inbound import AND not invoked by CLAUDE.md Commands, any SKILL.md, or TASKS.md*. Add `rg` over `*.md` to the reachability step. |
| 2 | `scratch/` is neither in scope nor protected | **Valid + Actionable** | Add `scratch/` to Phase 3's do-not-touch. Under delete-shy it is out of scope by definition. |
| 3 | `py_compile` cannot catch the one failure mode that matters (archiving `content_engine.py` passes syntax checks on all remaining files) | **Valid + Actionable** | Add import smoke-test to Verify (see corrected Verify block below). |
| 4 | `pip install pytest` is an unsanctioned write, and unnecessary (`.venv/bin/pytest` exists) | **Valid + Actionable** | Drop it; Verify becomes `.venv/bin/pytest tests/`. |
| 5 | Carrying "the stale-reference list from Hand-off 1 Step 2" pulls skill-doc fixes into a `refactor:` commit | **Valid + Actionable** | Use the list only as **negative evidence** (a file referenced by a SKILL.md is not dead). Fix no `.md` in Hand-off 2. |
| 6 | `apply_theme_patches.py` claimed by both Hand-off 2 Phase 1 rule and Hand-off 5 Step 2 | **Valid Trade-off** | Assign to Hand-off 5. Root-level file; TASKS.md:34 records it as producer of `templates/patched/`. |
| 7 | `/simplify` on `content_engine.py` risks both consumers; `audit_and_repair_database.py` has no test coverage | **Valid Trade-off** | If Phase 2 flags `content_engine.py`, do it last and under the peer-review gate. |
| 8 | Three `scratch/` scripts hardcode `/Users/okgoogle13/Projects/Career Brain/` (old dir name, space) — already broken | **Noise** | None this pass — `scratch/` out of scope. Log to TASKS.md. |
| 9 | "27.8 MB / 214 files" slightly off (26 MB / 212) | **Noise** | Hand-off 4's verify gate asserts 214 and will fail — flag there. |

### Open question for user

> **Is `scratch/` intended to survive this cleanup?**  
> If yes → finding #2 stands; leave it alone.  
> If no → that's a deliberate decision (≈15 files), not a reachability result, and contradicts delete-shy. Requires separate approval.

---

## Verified baselines (machine-confirmed 2026-09-19T02:19 AEST)

| Check | Command | Result |
|---|---|---|
| `ksc_template_spec_form` cited in SKILL.md | `grep -rn "ksc_template_spec_form" .claude/skills/gold_template_builder_v3/SKILL.md` | ✅ Line 16 |
| `ksc_template_spec_form.md` on disk | `ls .claude/skills/gold_template_builder_v3/ksc_template_spec_form.md` | ✅ 2,551 bytes |
| Entry-point set | `grep -nE 'python3? (pipeline\|tools)/' CLAUDE.md` | ✅ Lines 110–129 (Phases 0–5 + 5 tool scripts) |
| `content_engine` import map | `grep -rn "content_engine" --include='*.py' pipeline tools tests` | ✅ 4 consumers identified |
| Pytest gate | `.venv/bin/pytest tests/ -q` | ✅ **78/78 passed in 12.26 s** |

---

## Corrected Hand-off 2 Phase 3 Verify block

> Replace the Verify block in `comprehensive_cleanup_prompt.md` Hand-off 2 with:

```bash
# Syntax check (catches parse errors)
.venv/bin/python -m py_compile <changed files>

# Import smoke-test (catches the one real failure mode — bare import in generate_document.py)
PYTHONPATH=tools .venv/bin/python -c "import content_engine, generate_document"
.venv/bin/python pipeline/audit_and_repair_database.py --help

# Entry-point CLI check
.venv/bin/python pipeline/query_brain.py --help
.venv/bin/python tools/generate_document.py --help

# Full test gate (78 pass = baseline from Hand-off 1)
.venv/bin/pytest tests/ -q
```

---

## Gate declaration

**Hand-off 2 is unblocked.**

The critique findings above are **amendments to apply mentally when running Hand-off 2** — not blockers. The two mandatory ones:

1. **Finding #1:** Fix the candidate rule. Reachability = import graph + SKILL.md + CLAUDE.md + TASKS.md references. CLI entry-points are not dead because they have no inbound Python imports.
2. **Finding #5:** Use the stale-ref list as negative evidence only. Fix no `.md` files in Hand-off 2.

Paste Hand-off 2 into a **fresh session** — Opus 5 · ultrathink · plan mode for Phase 1, normal ask-each-edit for Phases 2–3.
