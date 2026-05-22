# Repository Guidelines

> **For AI agents (Codex, Antigravity, Claude Code, etc.):** Read this file in full before taking any action.
> Full architectural context is in [`Career Brain Manifesto.md`](./Career%20Brain%20Manifesto.md).

---

## Project Overview

This repository is a local Python ETL pipeline for building the **Career Brain Database** — a structured, machine-readable knowledge base compiled from a decade of mixed-format career documents.

The output feeds:
1. A hardcoded **Custom Gem** in Google AI Studio (`gem_system_prompt.md`)
2. A local **query CLI** for real-time resume/KSC tailoring

---

## Project Structure & Module Organization

```
Career Brain/
├── raw_docs/           # Source inputs (.docx, .doc, .pdf, .txt, .md, .csv)
│   ├── resumes/
│   ├── cover_letters/
│   ├── ksc/
│   └── knowledge/
├── normalized_vault/   # Phase 1 output: sanitized .txt files (do not edit manually)
├── output/             # Phase 2+ output: compiled JSON engines and reports
│   ├── career_history_enriched.json   # Pillar 1: Fact Matrix
│   ├── ksc_curated.json               # Pillar 2: Narrative Registry
│   ├── skills_and_taxonomy.json       # Pillar 3: Rosetta Stone / Skills Engine
│   ├── metric_injection_targets.md
│   ├── narrative_curation_report.md
│   └── parsing_errors.log             # Quality gate — check this after every run
├── AGENTS.md                          # This file
├── Career Brain Manifesto.md          # Full system design & schema specs
├── gem_system_prompt.md               # Google AI Studio Gem system prompt (standalone)
├── normalize_vault.py                 # Phase 1
├── organise_raw_docs.py               # Pre-Phase 1: file sorting/deduplication
├── compile_brain.py                   # Phase 2
├── curate_narratives.py               # Phase 3
├── inject_metrics.py                  # Phase 4
└── query_brain.py                     # Interactive CLI query engine
```

---

## ⚠️ Gatekeeper Protocol — MANDATORY

This pipeline operates under a **strict three-gate approval model**. Do NOT write, execute, or modify files without explicit user approval at each gate.

| Gate | Trigger | Action | Then… |
|---|---|---|---|
| **Gate 1 – Audit** | Before any script changes | Analyse directories, propose changes, list affected files | **STOP. Wait for approval.** |
| **Gate 2 – Phase 1** | After Gate 1 approval | Run `organise_raw_docs.py` then `normalize_vault.py` | **STOP. Present health ledger (file list, char counts, errors). Wait.** |
| **Gate 3 – Phase 2+** | After Gate 2 approval | Run `compile_brain.py`, then optionally `curate_narratives.py` + `inject_metrics.py` | **STOP. Present audit stats + parsing errors. Wait.** |

If the user says "run the pipeline", default to Gate 1 first — never execute all phases autonomously.

---

## Build, Test & Development Commands

### Environment setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Pipeline run order (sequential — do not skip steps)
```bash
python3 organise_raw_docs.py      # Pre-phase: sort/deduplicate raw_docs/
python3 normalize_vault.py        # Phase 1: extract binary → .txt
python3 compile_brain.py          # Phase 2: build 3-pillar JSON engines
python3 curate_narratives.py      # Phase 3: score + tier narratives
python3 inject_metrics.py         # Phase 4: enrich flagged bullets
python3 query_brain.py --help     # Verify CLI is intact
```

Scripts are **idempotent** — safe to re-run. Each phase reads the previous phase's output directory.

---

## Quality Gates — Check These After Every Run

1. **`output/parsing_errors.log`** — Any entry here is a failure. Investigate before proceeding.
2. **`needs_review: true` flag** — Set automatically on bullets >20 words with zero numerical metrics. These are targets for `inject_metrics.py`. Do not manually remove this flag.
3. **`source_lineage` field** — Every node in every JSON engine MUST retain its `source_lineage` (original raw filename). If a script strips this field, that is a critical bug.
4. **Summary counters** — `compile_brain.py` prints role count, bullet count, and narrative count. Compare against previous run to catch regressions.

---

## Output Schema — Quick Reference

| File | Pillar | Key fields |
|---|---|---|
| `career_history_enriched.json` | Fact Matrix | `company`, `role`, `start_date`, `achievements[]`, `action_verb`, `metric_outcome`, `domain_tags[]`, `needs_review`, `source_lineage` |
| `ksc_curated.json` | Narrative Registry | `type` (STAR/CAR/hook/pivot), `competency_tags[]`, `quality_tier`, `full_text`, `source_lineage` |
| `skills_and_taxonomy.json` | Rosetta Stone / Skills | `corporate_framing`, `community_translation`, `community_keywords[]`, `contextual_bridge` |

For full schema specs and phase extraction logic, see [`Career Brain Manifesto.md`](./Career%20Brain%20Manifesto.md) §4–6.

---

## Coding Style & Naming Conventions

- Python 3, 4-space indentation, UTF-8 source files.
- Use `Path`-based file handling (`pathlib`), structured `logging` over `print()`.
- `snake_case` for functions/variables/files; `UPPER_SNAKE_CASE` for constants.
- Scripts must be deterministic and idempotent — safe to re-run without manual cleanup.
- Type hints where useful; validate output structures with Pydantic (already a dependency).

---

## Testing Guidelines

No formal `tests/` suite yet. Use script-level validation:

- Confirm each script exits cleanly and writes expected outputs to `output/`.
- Treat `parsing_errors.log` and summary counters as the quality gate (see above).
- Minimum validation run after any change: `normalize_vault.py` → `compile_brain.py` → `query_brain.py --help`.

If adding automated tests, use `pytest` with `tests/test_<module>.py` naming.

---

## Commit Guidelines

No git history in this workspace. Use Conventional Commits:

```
feat: add cross-source metric matcher
fix: handle empty pdf pages in extractor
chore: re-run pipeline after new raw_docs added
docs: update pipeline usage in AGENTS.md
```

---

## Security & Data Handling

Inputs contain sensitive personal information (PII, lived experience disclosures, referee contacts).

- Do **not** print, log, or surface raw document content in terminal output beyond what is needed for debugging.
- Do **not** publish raw documents, full JSON engines, or complete `Career_Brain_Knowledge.md` externally.
- Prefer sharing diffs, redacted samples, and script-level changes.
- The `CLEANUP/` directory contains archived/legacy files — do not re-ingest without explicit instruction.

---

## See Also

| Document | Purpose |
|---|---|
| [`Career Brain Manifesto.md`](./Career%20Brain%20Manifesto.md) | Full system vision, phase specs, state machine, schema design, quality control guardrails |
| [`gem_system_prompt.md`](./gem_system_prompt.md) | Rosetta Stone matrix, retrieval rules, output formats — paste into Google AI Studio Gem |
| [`PIPELINE_INIT.md`](./PIPELINE_INIT.md) | Legacy agentic init prompt — superseded by this file and Manifesto; archive candidate |
