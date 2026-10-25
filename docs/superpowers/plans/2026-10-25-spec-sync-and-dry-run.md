# Career Brain — Spec Sync, Log Baseline, Dry-Run Check

Status: spec sync committed as `97ee8bc` (2026-10-25). Remaining: tree cleanup, optional log baseline, dry-runs.

## Context

Working tree has uncommitted spec sync (`config/llm-specs/AGENT-OPS.md`, `MANIFEST.md`, canonical `b59571e` → `d4ae57d`) and one untracked file (`.claude/settings.local.json.pre-cleanup`). `database/parsing_errors.log` holds 239 historical lines. Phase 5 dry-runs have not been re-checked. A prior draft of this plan was reviewed; cut items are listed at the bottom.

## Goal

Clean working tree, optional log baseline, and dry-run generation exiting 0 for resume, cover_letter and ksc. Done when `git status --short` is empty and all three dry-runs exit 0 with no unresolved tokens in the report.

## Approval routing

- Commit, `rm`, log truncation: **user** (CLAUDE.md gates).
- Any Gemini/Google call: **user**. None are in this plan.
- Design-judgment calls (ambiguity, trade-offs): **advisor tool**.

## Steps

1. **Tree cleanup** [GATE: user approves commit + rm]. The spec sync is already done (`97ee8bc`); do not redo it.
   - `diff .claude/settings.local.json.pre-cleanup .claude/settings.local.json`. Report anything in the backup that the live file is missing.
   - `rm .claude/settings.local.json.pre-cleanup`
   - `git add docs/superpowers/plans/2026-10-25-spec-sync-and-dry-run.md && git commit -m "docs: add spec-sync and dry-run plan"` (append attribution lines per session reminder)
   - Verify: `git status --short` is empty.

2. **Log baseline** (optional) [GATE: user]
   - `cp database/parsing_errors.log database/backups/parsing_errors_archive_$(date +%Y%m%d).log`
   - `: > database/parsing_errors.log`
   - Verify: `test ! -s database/parsing_errors.log`
   - Note: baseline reset only. The invariant is proven by an approved pipeline re-run, not by truncation. The log and `database/backups/` are gitignored.

3. **Dry-runs** (local, no external calls)
   - `--dry-run` skips Google APIs only. It does **not** skip Gemini. `generate_document.py:33–40` loads `.env` into the environment, which sets `GEMINI_API_KEY` to an `op://` literal. That value is truthy, so the KSC CAR rewrite (`content_engine.py:833–836`) would call Gemini. Prefix every run with an empty `GEMINI_API_KEY=` (`setdefault` won't overwrite it, and `not api_key` then skips the call). Do **not** use `op run`.
   - `--target` is required. Use the dummy target `"Test Role at Test Org"`, never a real application.
   - `GEMINI_API_KEY= .venv/bin/python tools/generate_document.py --type resume --target "Test Role at Test Org" --dry-run`
   - `GEMINI_API_KEY= .venv/bin/python tools/generate_document.py --type cover_letter --target "Test Role at Test Org" --employer-type nfp --dry-run`
   - `GEMINI_API_KEY= .venv/bin/python tools/generate_document.py --type ksc --target "Test Role at Test Org" --criteria "1. Demonstrated experience in case management. 2. Strong written communication skills." --dry-run`
   - Each run overwrites `database/doc_generation_report.json` (`DEFAULT_REPORT`, `:70–73`). Pass `--out-report /tmp/cb_dryrun_<type>.json` on each run so the three reports don't overwrite each other and nothing extra is written to `database/`.
   - Verify: exit 0 each; open the report at `--out-report` (default `DEFAULT_REPORT`) and confirm 0 unresolved tokens. Report key names are unverified — read the report, do not assume them.

4. **BS-7.5** stays deferred in `TASKS.md` (`:28`, `:75`). Dry-run emits placeholders, so it cannot close the slop check. Do not edit `TASKS.md`.

## Verification

- `git status --short` empty after step 1.
- `.venv/bin/pytest -q tests` → 93 passed (baseline checked 2026-10-25).
- Three dry-run exit codes = 0.

## Action prompt (paste into a fresh Claude Code session in the project root)

```markdown
## Goal
Clean working tree and all three dry-run generations exit 0. Done when
`git status --short` is empty and each dry-run report shows 0 unresolved tokens.

## Input
Read `docs/superpowers/plans/2026-10-25-spec-sync-and-dry-run.md` and execute its Steps 1–4 in order.

## Skills
Invoke `andrej-karpathy-skills:karpathy-guidelines` first. Invoke `superpowers:verification-before-completion` before claiming done. No other skills.

## Rules
- Stop and ask me before: the commit, `rm`, log truncation, and any Gemini/Google call.
- For design-judgment calls, call the advisor tool. It cannot approve the gates above.
- Use `.venv/bin/python` and `.venv/bin/pytest`. Never print whole files, raw JSON engines or logs; use bounded reads.
- Do not edit `TASKS.md`, `processed/`, `database/` (other than step 2 if I approve), or add tests.
- If a command's flags differ from the plan, trust `--help` and report the difference.
- Mark unverified conclusions `[inferred]`.

## Report
Changed paths, commands actually run with exit codes, anything skipped and why.
```
