# CLAUDE.md — Career Brain (AGENTS.md is a symlink)

## Role and operating rules

- Career Brain is a local Python ETL pipeline that transforms sensitive career documents into JSON knowledge engines and tailored Google Docs.
- Work from an explicit task, target path, diff, failing command, or named invariant.
- Verify against repository files and command output; never infer status from filenames, prior chat, or memory.
- Make the smallest change that solves the verified problem. Do not add abstractions, config, wrappers, dependencies, or broad refactors without a concrete need and approval.
- Mark unverified conclusions as `[inferred]`.

## Approval gates

- Do not write, execute, modify, generate, commit, push, deploy, or call external services without explicit approval for the relevant step.
- Approval of a written plan covers, within that plan's scope: local edits, tests, `--dry-run` runs, one focused commit per stage, and `git rm` of files the plan names.
- Before script changes outside an approved plan: audit affected paths and proposed changes, then stop for approval.
- Pipeline stages require separate approval until pipeline Stage A1 (timestamped backups, `--dry-run` defaults, append-only error log) is committed and verified; after that, an approved plan may run local stages end-to-end:
  1. Phase 0–1: `organise_raw_docs.py`, `normalize_vault.py`
  2. Phase 2–4: `compile_brain.py`, `curate_narratives.py`, `inject_metrics.py`
  3. Phase 5: `tools/generate_document.py`
- Hard gates (approval every time, once per batch, plan approval never covers them): writes to `source_docs/` or `archive/`; live Gemini calls or Google Docs/Drive writes; tier changes in `config/ai_sharing_policy.json`; OAuth scopes or credentials; `git push`.
- “Run the pipeline” without an approved plan means audit first, never all phases autonomously.
- Before generating or submitting application copy, review every banned-phrase, review-phrase, and overclaim warning; only spelling may be auto-corrected.

## Context and output

- Use the smallest sufficient context: named files, bounded ranges, `git diff`, or narrow `rg -n`.
- Do not perform broad discovery, recursively ingest source documents, or print whole files, large unchanged excerpts, raw logs, raw JSON engines, or `Career_Brain_Knowledge.md`.
- Prefer diffs, redacted samples, structural summaries, and script-level findings.
- Report: findings, changed paths, commands actually run, results, and blockers—no unsupported claims.

## Data and secrets

- `source_docs/` contains sensitive personal information; never edit raw inputs manually or expose their content beyond what is necessary for approved debugging.
- `processed/` and `database/` are generated outputs; do not edit them manually unless explicitly instructed.
- `archive/` is legacy material; never re-ingest it without explicit instruction.
- Never publish raw source documents, complete database engines, or full knowledge exports.
- Approved AI targets (Gemini, Claude, OpenAI) operate under `config/ai_sharing_policy.json` (low-friction risk-tiered: user career material, application drafts, contact details, and professional lived-experience narratives are Green share-by-default without repeated gates; Amber task-scoped; Red strictly excluded); the canonical Career Brain database remains strictly local.
- Secrets are managed with 1Password CLI (`op`). Never write raw secret values to `.env`, logs, source, commits, or output.
- Use `op run --env-file=".env" -- <command>` when approved runtime secrets are needed; `.env` must contain only `op://` references.

## Architecture and invariants

- Pipeline code: `pipeline/`; Phase 5 document tooling: `tools/`; runtime configuration: `config/`; Google Docs themes: `templates/`; agent skills: `.claude/skills/`.
- Full architecture, schemas, and phase design: `docs/manifesto.md`.
- Three generated engines: `database/career_history_enriched.json`, `database/ksc_curated.json`, `database/skills_and_taxonomy.json`.
- `source_lineage` is mandatory on every database node.
- `needs_review` is pipeline-managed; never remove it manually.
- `database/parsing_errors.log` must be empty after an approved pipeline run.
- The corporate-to-community translation map is defined in `pipeline/compile_brain.py`.

## Validation

- After an approved pipeline-code change, run only the relevant checks; minimum pipeline validation is:
  ```bash
  .venv/bin/python pipeline/normalize_vault.py
  .venv/bin/python pipeline/compile_brain.py
  .venv/bin/python pipeline/query_brain.py --help
  ```
- `.venv/bin/pytest tests/` — covers `tools/generate_document.py`, `tools/build_golden_master.py` and `tools/verify_golden_master.py` only; no pipeline/ tests exist.
- For theme work, use the relevant validation or audit tool in `tools/`.
- Never claim validation passed unless the command was run successfully and relevant output was checked.

## Change hygiene

- Python: PEP 8, 4 spaces, `pathlib`, structured `logging`, type annotations for core models, and repository-root resolution via `Path(__file__).parent.parent`. Use `google-genai` (not legacy SDK).
- Theme sources (`theme-*.json`) conform to `MASTER_SCHEMA_V2_3.json`; compiled templates validate against `schema_v2_0.json`.
- If authorized to commit, use focused Conventional Commits: `feat:`, `fix:`, `chore:`, or `docs:`.
