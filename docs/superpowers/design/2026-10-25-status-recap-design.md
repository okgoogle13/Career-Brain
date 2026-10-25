---
name: Status recap
description: Script-generated task/plan recap shown by a Stop hook only when state changed, plus on-demand /status; standardises plan and task docs.
task: none
status: draft
---

# Design: Status recap

**Date:** 2026-10-25
**Status:** Draft, awaiting approval

## Intent

"Next steps" written by the model are generic. A script that reads the project's own task and plan docs gives specific, repeatable steps at no extra model turn. The recap appears only when state changed, and on demand.

## Goals / non-goals / anti-goals

- Goals: recap of active task, plan, first unchecked step, gate status, exact next command; standard plan/task doc format.
- Non-goals: model-written recap, new planning skill, per-project override layer.
- Anti-goal: a confident but stale recap. A missed checkbox update must be visible (last-edit date printed).

## Constraints

- Stdlib-only Python, run as `.venv/bin/python`. No new dependencies.
- Config over code: gate marker and file paths live in constants at the top of the script (no config file unless needed).
- CLAUDE.md approval gates apply: each build step below needs separate approval.
- Missing or ambiguous data prints as `null`/"unknown"; never inferred.

## Decisions (user)

- Recap only when state changed, plus on demand.
- Script-generated, shown via Stop hook `systemMessage` (no extra model turn).

## Design

1. **Convention.** Plans and designs carry front matter `task`, `status` (`draft|approved|in-progress|done`). Steps are checkboxes; gated steps carry `[GATE: user]`. `TASKS.md` keeps Active and Blocked only; each entry has `Plan:` and `Next:` lines. Completed entries move to `docs/tasks-archive.md`.
2. **`.claude/hooks/status.py`.** Hashes: `TASKS.md` Active section, plan/design front matter, unchecked-step counts, dirty-file count. If it differs from `.claude/.status-hash`, print at most 10 lines: active task, plan, first unchecked step, gated or not, `Next:` command, `TASKS.md` last-edit date. `--force` skips the hash check. Parse error prints a one-line warning.
3. **Stop hook** in `.claude/settings.json` runs the script and returns JSON `{"systemMessage": ...}`; prints nothing when unchanged.
4. **`/status`** command file runs the script with `--force`.
5. **`tests/test_status.py`** with fixture docs: changed, unchanged, malformed, gated.
6. **CLAUDE.md**: two lines telling Claude to update checkboxes and `Next:` as it works.

## Builder's calls (mine, not the user's)

- Hash cache at `.claude/.status-hash`, added to `.gitignore`.
- `/status` as a command file, not a skill (no listing cost).
- Multiple Active tasks: show the one with the most recently edited plan; list others as one-line titles.
- Hook failure must never block a stop: always exit 0.

## Build order (each step needs approval)

1. `status.py` + `tests/test_status.py` + fixtures.
2. Stop hook + `/status` + `.gitignore` entry.
3. `TASKS.md` migration and `docs/tasks-archive.md` (riskiest; diff reviewed first).
4. CLAUDE.md two lines.

## Open questions

- How should `Next:` handle steps needing a Gemini/Google call (CLAUDE.md approval gate)? Proposed: the gate marker is mandatory on those steps and the recap prints it.
