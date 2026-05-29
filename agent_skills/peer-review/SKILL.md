---
name: peer-review
description: Use when verifying recent agent modifications to Career Brain pipeline scripts before a --write run or commit. Invoke when changes touch JSON mutation, merge logic, schema fields, or audit/repair rules in pipeline/.
---

# Career Brain — Peer Review

## Overview

Four-phase staged audit for pipeline code changes. Phases 1–2 are always mandatory. Phase 2 hard-gates on Career Brain's critical invariants — a single FAIL there short-circuits to BLOCK without entering Phase 3.

## When to Use

- Before running `--write` on `audit_and_repair_database.py` or `compile_brain.py`
- Before committing changes that touch JSON mutation, merge logic, or schema fields
- When a specific concern exists about field preservation, edge cases, or logic safety

## When NOT to Use

- Reviewing Google Doc templates or KSC spec files → use `ats_template_qa_v3` or `docs_style_auditor_v3`
- General code review with no pipeline concern → use standard code review

---

## Phase 1 — Triage

1. Extract all file paths named in the audit prompt
2. Run `git diff HEAD -- <files>` to surface all staged and unstaged changes since the last commit
3. Parse the audit prompt into a numbered list of targeted concerns
4. **Gate:** If no files are named and no specific concerns are stated, stop and ask for a more specific audit prompt before continuing

---

## Phase 2 — Fixed Lenses (Hard Gates)

Run all four lenses. Each returns **PASS** / **WARN** / **FAIL**.

> **Rule:** Any single FAIL → verdict is immediately **BLOCK**. Skip Phase 3. Go directly to Phase 4.

| Lens | What to verify |
|------|----------------|
| `source_lineage` | No code path strips, overwrites, or defaults `source_lineage` to `""` during merge or update. Ground truth: `AchievementBullet.source_lineage` (str) and `JobRecord.source_lineage` (list[str]) in `pipeline/compile_brain.py` |
| `backup-before-write` | Every `--write` branch calls `_backup()` before mutating any JSON on disk |
| `schema-compliance` | All dict/object shapes passed to Pydantic constructors match current model fields in `pipeline/compile_brain.py` (`AchievementBullet`, `JobRecord`, and sibling models); no unexpected keys silently dropped |
| `error-logging` | Exceptions and parse failures call `_log_pipeline_error()` → `database/parsing_errors.log`; no bare `except: pass`; no `except` block that logs only to stdout without calling `_log_pipeline_error()` |

---

## Phase 3 — Targeted Deep-dive

_(Skip entirely if Phase 2 produced any FAIL.)_

Work through each concern extracted in Phase 1. For each concern:

1. Quote the relevant code block verbatim
2. State the specific risk
3. Verdict: **SAFE** / **WARN** / **FAIL**
4. One-line rationale

---

## Phase 4 — Verdict & Report

### Verdict logic

| Condition | Verdict |
|-----------|---------|
| Any FAIL in Phase 2 or Phase 3 | **BLOCK** |
| Any WARN, no FAILs | **SAFE WITH WARNINGS** |
| All PASS / SAFE | **SAFE** |

### Terminal output

Print the verdict banner first, then severity-grouped findings in order: FAIL → WARN → PASS/SAFE.

### Save the report

1. Create `database/peer_review_reports/` if it does not exist
2. Derive a slug: take the first 3 words of the audit prompt, lowercase, hyphenate (e.g. `data-integrity-schema`)
3. Save to `database/peer_review_reports/YYYY-MM-DD-<slug>.md`

Use this report template:

```markdown
# Peer Review Report
_Date: YYYY-MM-DD | Files: <list> | Prompt: "<audit prompt>"_

## Verdict: [SAFE | SAFE WITH WARNINGS | BLOCK]

## Phase 2 — Fixed Lenses
| Lens | Result | Notes |
|------|--------|-------|
| source_lineage | | |
| backup-before-write | | |
| schema-compliance | | |
| error-logging | | |

## Phase 3 — Targeted Findings
### Concern 1: <name>
**Code:**
```python
<quoted block>
```
**Risk:** ...
**Verdict:** SAFE / WARN / FAIL — _rationale_

## Recommended Actions
_(Only include this section if verdict is WARN or BLOCK)_
1. ...
```

---

## Scope

- Does **not** modify any pipeline files
- Does **not** run the pipeline scripts
- Verdict is advisory — the user decides whether to proceed with `--write`
