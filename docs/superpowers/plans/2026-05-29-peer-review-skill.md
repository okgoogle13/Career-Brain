# Peer Review Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create `agent_skills/peer-review/SKILL.md` — a Career Brain-specific slash-command skill that guides Claude through a 4-phase staged audit of pipeline code changes, producing a terminal verdict and a saved report file.

**Architecture:** Single SKILL.md following the `agent_skills/` convention (one file per skill folder). No code, no dependencies. The skill is a structured protocol Claude reads and follows; it dispatches no subagents. Output is a terminal summary plus a file written to `database/peer_review_reports/`.

**Tech Stack:** Markdown, YAML frontmatter, Career Brain pipeline knowledge (`pipeline/compile_brain.py` Pydantic models as schema ground truth).

---

## File Map

| Action | Path | Purpose |
|--------|------|---------|
| Create | `agent_skills/peer-review/SKILL.md` | The complete skill protocol |

No other files are created or modified. The skill writes report files at runtime to `database/peer_review_reports/` (that directory is created by Claude when the skill runs, not during this implementation).

---

### Task 1: Validate conventions against existing skills

**Files:**
- Read: `agent_skills/ats_template_qa_v3/SKILL.md`
- Read: `agent_skills/docs_style_auditor_v3/SKILL.md`

- [ ] **Step 1: Read both existing skills**

```bash
cat "agent_skills/ats_template_qa_v3/SKILL.md"
cat "agent_skills/docs_style_auditor_v3/SKILL.md"
```

Note the frontmatter pattern, heading structure, use of tables vs prose, and how commands are presented. The peer-review skill must match this style.

- [ ] **Step 2: Confirm schema ground truth fields**

```bash
grep -n "source_lineage\|needs_review\|backup\|_log_pipeline_error" pipeline/compile_brain.py | head -20
grep -n "source_lineage\|needs_review\|backup\|_log_pipeline_error" pipeline/audit_and_repair_database.py | head -20
```

Confirm: `AchievementBullet` and `JobRecord` in `pipeline/compile_brain.py` are the Pydantic models. Confirm `_log_pipeline_error()` is the canonical error-logging function in `pipeline/audit_and_repair_database.py`. These names are used verbatim in the skill.

---

### Task 2: Write the skill

**Files:**
- Create: `agent_skills/peer-review/SKILL.md`

- [ ] **Step 1: Create the directory**

```bash
mkdir -p "agent_skills/peer-review"
```

- [ ] **Step 2: Write SKILL.md**

Create `agent_skills/peer-review/SKILL.md` with exactly this content:

````markdown
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
| `backup-before-write` | Every `--write` branch creates a timestamped backup file before mutating any JSON on disk |
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
\```python
<quoted block>
\```
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
````

- [ ] **Step 3: Verify frontmatter character count**

```bash
python3 -c "
import re
content = open('agent_skills/peer-review/SKILL.md').read()
fm = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
print(f'Frontmatter chars: {len(fm.group(0))} (limit: 1024)')
assert len(fm.group(0)) <= 1024, 'FAIL: frontmatter exceeds 1024 chars'
print('PASS')
"
```

Expected: `Frontmatter chars: <N> (limit: 1024)` followed by `PASS`.

- [ ] **Step 4: Verify description starts with "Use when" and contains no workflow summary**

```bash
python3 -c "
import re
content = open('agent_skills/peer-review/SKILL.md').read()
fm = re.search(r'description: (.+)', content)
desc = fm.group(1)
assert desc.startswith('Use when'), f'FAIL: description must start with Use when, got: {desc[:40]}'
forbidden = ['phase', 'triage', 'fixed lenses', 'dispatches', 'protocol', 'four-phase']
for word in forbidden:
    assert word.lower() not in desc.lower(), f'FAIL: description summarises workflow (contains: {word})'
print('PASS: description is trigger-only')
"
```

Expected: `PASS: description is trigger-only`

- [ ] **Step 5: Commit**

```bash
git add agent_skills/peer-review/SKILL.md
git commit -m "feat(skills): add peer-review skill for pipeline audit"
```

---

### Task 3: Smoke-test the skill

This is not a full RED-GREEN test per writing-skills TDD (that would require running a subagent baseline). It is a structural smoke-test to confirm the skill is self-consistent before use.

**Files:**
- Read: `agent_skills/peer-review/SKILL.md`

- [ ] **Step 1: Check all cross-references exist**

```bash
# Verify the files the skill references actually exist
ls pipeline/compile_brain.py && echo "compile_brain.py OK"
ls pipeline/audit_and_repair_database.py && echo "audit_and_repair_database.py OK"
grep -c "AchievementBullet" pipeline/compile_brain.py && echo "AchievementBullet found"
grep -c "JobRecord" pipeline/compile_brain.py && echo "JobRecord found"
grep -c "_log_pipeline_error" pipeline/audit_and_repair_database.py && echo "_log_pipeline_error found"
```

Expected: all five `OK` / `found` lines.

- [ ] **Step 2: Simulate Phase 1 with the example prompt**

Read the skill and mentally walk through Phase 1 using the canonical example prompt:

> "Perform a rigorous Data Integrity & Schema Audit on the recent modifications to pipeline/audit_and_repair_database.py and pipeline/compile_brain.py. Specifically verify that the new 'needs_review' merge logic is safe, that the 'archived_fragment' rule handles edge cases properly, and that no source_lineage fields are at risk of being stripped."

Confirm:
- Files extracted: `pipeline/audit_and_repair_database.py`, `pipeline/compile_brain.py` ✓
- Targeted concerns identified: (1) needs_review merge logic, (2) archived_fragment edge cases, (3) source_lineage stripping ✓
- Phase 1 gate not triggered (files named, concerns stated) ✓

- [ ] **Step 3: Commit smoke-test confirmation**

No code changes. If Step 1 or Step 2 revealed a problem, fix `SKILL.md`, re-verify, then:

```bash
git add agent_skills/peer-review/SKILL.md
git commit -m "fix(skills): correct peer-review skill reference after smoke-test"
```

If no issues found, no commit needed.

---

## Done Criteria

- [ ] `agent_skills/peer-review/SKILL.md` exists and passes frontmatter validation
- [ ] Description is trigger-only (no workflow summary)
- [ ] All five cross-references (two pipeline files, two Pydantic model names, one function name) exist in the codebase
- [ ] Skill is committed to git
