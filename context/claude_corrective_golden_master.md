# CORRECTIVE PROMPT — Career Brain Styling & Golden Master Build
> Target model: Claude Opus 4.5 / 4 (extended thinking enabled)
> Mode: Sequential execution — do NOT use parallel subagents to avoid I/O race conditions on log files.
> Priority: **OVERRIDE any audit tasks queued**. This supersedes the previous pipeline audit.

---

## Context Reset

You were about to audit the Career Brain pipeline. **Pause that audit completely.**

The situation has changed. An Antigravity session has already:
1. Migrated the 5 Chromebook themes from `CLEANUP/Chromebook Downloads/pdf_themes_json.json`
2. Created 3 ATS-safe theme JSON specs in `doc_templates/`:
   - `resume_contemporary_professional_v1.json` — Calibri / Forest Green (`#2F855A`)
   - `resume_professional_classic_v1.json` — Times New Roman / Deep Navy (`#1A365D`)
   - `resume_modern_minimalist_v1.json` — Arial / Teal (`#38B2AC`)
3. Created `doc_templates/THEME_SPEC_GUIDE.md` — the single source of truth for the theme library
4. Registered placeholder Doc IDs in `doc_templates.json` for all three variants

**The Doc IDs already in `doc_templates.json` appear real (not REPLACE_WITH stubs) — verify them. If they exist but fail the style audit, discard them and generate new ones.**

---

## Your Mission

**Read the plan at:**
`/Users/okgoogle13/.claude/plans/glimmering-wiggling-avalanche.md`

That plan is the spec for what to build, but **apply the following overrides**:
1. **The script exists:** `build_golden_master.py` already exists in the project root. Review it rather than rewriting it from scratch.
2. **No Font Failures:** Step 2 of the plan expects Themes 2 & 3 to fail the font audit. **Ignore this.** The `audit_doc_style.py` script is now theme-aware. All themes MUST return `STYLE OK`.

Do not improvise on styling. The theme JSON files and the plan table are the source of truth.

---

## Skills Status (READ BEFORE ACTING)

All skills are **active and updated**:

- `gold_template_builder_v2` — KSC-only, out of scope for resume themes. Do not use for this task.
- `ats_template_qa_v2` — **Updated to be theme-aware.** Use this for QA.
- `docs_style_auditor` — **Updated to be theme-aware.** Pass `--theme doc_templates/resume_<name>_v1.json` when auditing a themed Golden Master. 

---

## Execution Protocol (Thinking Mode)

Use your extended thinking to:

1. **Read first, act second** — review the existing `build_golden_master.py` to ensure it aligns with the plan's index tracking and Google Services auth approach.
   
2. **Execute Sequentially**:
   - For each theme (one at a time): build → audit (`--theme`) → dry-run → register Doc ID.
   - Do NOT run in parallel to prevent locking `output/parsing_errors.log`.

3. **Verify before replacing** — run `audit_doc_style.py` against the existing IDs in `doc_templates.json` first. If they pass, registration is already done.

4. **Produce the handover report** from the plan's template (one block per theme).

---

## Quality Gate (Non-Negotiable)

Do NOT declare done until:
- [ ] All 3 Doc IDs in `doc_templates.json` are real and pass the style audit.
- [ ] `output/parsing_errors.log` is empty after all three dry-runs.
- [ ] Each dry-run shows `blank: 0` for core tokens.
- [ ] Handover report produced with Doc ID, audit result, dry-run fill rate, open issues.

---

## What NOT to Do

- Do not run `normalize_vault.py`, `compile_brain.py`, or any Phase 1–4 pipeline scripts.
- Do not audit `output/parsing_errors.log` for existing errors (that's the old audit task).
- Do not modify `generate_document.py` or any existing pipeline scripts.
- Do not invent new placeholder tokens not already in `PLACEHOLDER_SCHEMA_V2`.

---

## Deliverables

1. Ensure `build_golden_master.py` is fully functional.
2. Three Golden Master Google Docs (one per theme) with real Doc IDs.
3. Updated `doc_templates.json` with all three variants registered.
4. Handover report (formatted exactly per the plan's template).
