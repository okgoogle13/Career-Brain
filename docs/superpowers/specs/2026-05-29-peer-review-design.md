# Peer Review Skill — Design Spec
_Date: 2026-05-29_

## Summary

A Career Brain-specific `/peer-review` skill that audits recent agent modifications to pipeline scripts before any `--write` run. Claude follows a 4-phase staged protocol: triage → fixed invariant lenses (hard gates) → targeted deep-dive → verdict + report.

---

## Identity

| Field | Value |
|-------|-------|
| **Skill name** | `peer-review` |
| **Location** | `agent_skills/peer-review/SKILL.md` |
| **Invocation** | `claude /peer-review "<audit prompt>"` |
| **Output** | Terminal summary + saved report file |
| **Reviewer** | Claude follows the skill (no subagent dispatch) |

---

## Trigger Conditions

Invoke `/peer-review` when:
- An agent (or human) has modified a pipeline file
- Before running `--write` on audit_and_repair_database.py or compile_brain.py
- Before committing changes that touch JSON mutation, merge logic, or schema fields
- When a specific concern exists about field preservation, edge cases, or logic safety

---

## Phase Design

### Phase 1 — Triage
1. Extract named file paths from the audit prompt
2. Run `git diff HEAD -- <files>` to surface all staged and unstaged changes since the last commit (not `HEAD~1`, which would miss uncommitted work)
3. Parse the audit prompt into a numbered list of targeted concerns
4. **Gate:** If no files are named and no specific concerns are stated, stop and ask for a more specific audit prompt before continuing

### Phase 2 — Fixed Lenses (Hard Gates)

Run all four lenses. Each returns **PASS** / **WARN** / **FAIL**.

**Rule:** Any single FAIL → overall verdict is immediately **BLOCK**. Skip Phase 3. Go directly to Phase 4 (report).

| Lens | Check |
|------|-------|
| `source_lineage` | No code path strips, overwrites, or defaults `source_lineage` to `""` during merge or update operations |
| `backup-before-write` | Every `--write` branch creates a timestamped backup file before mutating any JSON |
| `schema-compliance` | All dict/object shapes passed to Pydantic constructors match current model fields (ground truth: `AchievementBullet`, `JobRecord`, and sibling models in `pipeline/compile_brain.py`); no unexpected keys silently dropped |
| `error-logging` | Exceptions and parse failures surface via `_log_pipeline_error()` to `parsing_errors.log`; no bare `except: pass`, no `except` block that logs only to stdout without calling `_log_pipeline_error()` |

### Phase 3 — Targeted Deep-dive

Work through each concern extracted in Phase 1. For each concern:
- Quote the relevant code block
- State the specific risk
- Verdict: **SAFE** / **WARN** / **FAIL**
- One-line rationale

Skip if Phase 2 produced a FAIL (already BLOCK).

### Phase 4 — Verdict & Report

**Overall verdict logic:**
- Any Phase 2 or Phase 3 FAIL → **BLOCK**
- Any WARN, no FAILs → **SAFE WITH WARNINGS**
- All PASS/SAFE → **SAFE**

**Terminal output:** Verdict banner + severity-grouped findings (FAIL → WARN → PASS)

**Saved report:** `database/peer_review_reports/YYYY-MM-DD-<slug>.md` where slug = first 3 words of the audit prompt, lowercased and hyphenated (e.g. `data-integrity-schema`). Create `database/peer_review_reports/` if it does not exist.

Report structure:
```
# Peer Review Report
_Date | Files reviewed | Audit prompt_

## Verdict: [SAFE | SAFE WITH WARNINGS | BLOCK]

## Phase 2 — Fixed Lenses
[table: lens | result | notes]

## Phase 3 — Targeted Findings
[per-concern blocks]

## Recommended Actions
[numbered list, only if WARN or BLOCK]
```

---

## Scope Constraints

- This skill does **not** modify any files other than writing the report
- It does **not** run the pipeline scripts
- It does **not** approve or reject a `--write` run automatically — that remains the user's decision
- The `agent_skills/` directory convention: single `SKILL.md` file per skill folder

---

## Out of Scope

- Reviewing non-pipeline files (Google Doc templates, config files) — use `docs_style_auditor_v3` or `ats_template_qa_v3` for those
- Automated fix suggestions — findings are informational, not prescriptive patches
