# Repository Guidelines

> **For AI agents (Codex, Antigravity, Claude Code, etc.):** Read this file in full before taking any action.
> Full architectural context is in [`Career Brain Manifesto.md`](./Career%20Brain%20Manifesto.md).

---

## Project Overview

This repository is a local Python ETL pipeline for building the **Career Brain Database** — a structured, machine-readable knowledge base compiled from a decade of mixed-format career documents.

The output feeds:
1. A hardcoded **Custom Gem** in Google AI Studio (`gem_system_prompt.md`)
2. A local **query CLI** for real-time resume/KSC tailoring (`pipeline/query_brain.py`)

---

## Folder Structure

```
Career Brain/
├── source_docs/        Raw input files — do not edit manually
│   ├── resumes/
│   ├── cover_letters/
│   ├── ksc/
│   └── knowledge/
├── processed/          Phase 1 output: .txt extractions (auto-generated)
├── database/           Phase 2-4 output: JSON engines + Knowledge.md (auto-generated)
│   └── parsing_errors.log   ← quality gate — check after every run
├── pipeline/           ETL scripts (run in phase order)
│   ├── organise_raw_docs.py
│   ├── normalize_vault.py
│   ├── compile_brain.py
│   ├── curate_narratives.py
│   ├── inject_metrics.py
│   ├── clean_knowledge_vault.py
│   └── query_brain.py
├── tools/              Phase 5 Google Docs generation
│   ├── generate_document.py
│   ├── content_engine.py
│   ├── build_golden_master.py
│   ├── create_golden_master.py
│   ├── audit_doc_style.py
│   ├── qa_docs_check.py
│   └── validate_template_spec.py
├── templates/          Google Docs theme JSON configs
├── config/             Runtime config: ats_rules.json, doc_templates.json, user_config.json
├── context/            AI session context: repomix XMLs, prompts, handover docs
│   └── specs/          Template format specs (resume, cover letter, KSC)
├── agent_skills/       Versioned AI agent skill definitions
│   ├── _archived_v1/
│   ├── ats_template_qa_v3/
│   ├── docs_style_auditor_v3/
│   └── gold_template_builder_v3/
├── scratch/            One-off investigation scripts (not pipeline)
├── archive/            Legacy files — do not re-ingest without instruction
├── tests/
├── AGENTS.md                   This file
├── Career Brain Manifesto.md   Full system design + schema specs
├── BUILD_SPECS.md              Phase 5 Google Workspace build specs
└── gem_system_prompt.md        Google AI Studio Gem prompt
```

---

## ⚠️ Gatekeeper Protocol — MANDATORY

This pipeline operates under a **strict four-gate approval model**. Do NOT write, execute, or modify files without explicit user approval at each gate.

| Gate | Trigger | Action | Then… |
|---|---|---|---|
| **Gate 1 – Audit** | Before any script changes | Analyse directories, propose changes, list affected files | **STOP. Wait for approval.** |
| **Gate 2 – Phase 1** | After Gate 1 approval | Run `organise_raw_docs.py` then `normalize_vault.py` | **STOP. Present health ledger (file list, char counts, errors). Wait.** |
| **Gate 3 – Phase 2+** | After Gate 2 approval | Run `compile_brain.py`, then optionally `curate_narratives.py` + `inject_metrics.py` | **STOP. Present audit stats + parsing errors. Wait.** |
| **Gate 4 – Phase 5** | After Gate 3 approval | Run `tools/generate_document.py` to compile templates | **STOP. Present generated Google Doc links. Wait.** |

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
python3 pipeline/organise_raw_docs.py     # Phase 0: sort/deduplicate source_docs/
python3 pipeline/normalize_vault.py       # Phase 1: extract binary → .txt in processed/
python3 pipeline/compile_brain.py         # Phase 2: build 3-pillar JSON engines in database/
python3 pipeline/curate_narratives.py     # Phase 3: score + tier narratives
python3 pipeline/inject_metrics.py        # Phase 4: enrich flagged bullets
python3 tools/generate_document.py --target "Role" --template resume  # Phase 5
python3 pipeline/query_brain.py --help    # Verify CLI is intact
```

Scripts are **idempotent** — safe to re-run. Each phase reads the previous phase's output directory.

---

## Quality Gates — Check These After Every Run

1. **`database/parsing_errors.log`** — Any entry here is a failure. Investigate before proceeding.
2. **`needs_review: true` flag** — Set automatically on bullets >20 words with zero numerical metrics. Targets for `pipeline/inject_metrics.py`. Do not manually remove this flag.
3. **`source_lineage` field** — Every node in every JSON engine MUST retain its `source_lineage` (original raw filename). If a script strips this field, that is a critical bug.
4. **Summary counters** — `compile_brain.py` prints role count, bullet count, and narrative count. Compare against previous run to catch regressions.

---

## Output Schema — Quick Reference

| File | Pillar | Key fields |
|---|---|---|
| `database/career_history_enriched.json` | Fact Matrix | `company`, `role`, `start_date`, `achievements[]`, `action_verb`, `metric_outcome`, `domain_tags[]`, `needs_review`, `source_lineage` |
| `database/ksc_curated.json` | Narrative Registry | `type` (STAR/CAR/hook/pivot), `competency_tags[]`, `quality_tier`, `full_text`, `source_lineage` |
| `database/skills_and_taxonomy.json` | Rosetta Stone / Skills | `corporate_framing`, `community_translation`, `community_keywords[]`, `contextual_bridge` |

For full schema specs and phase extraction logic, see [`Career Brain Manifesto.md`](./Career%20Brain%20Manifesto.md) §4–6.

---

## Coding Style & Naming Conventions

- Python 3, 4-space indentation, UTF-8 source files.
- Use `Path`-based file handling (`pathlib`), structured `logging` over `print()`.
- `snake_case` for functions/variables/files; `UPPER_SNAKE_CASE` for constants.
- Scripts must be deterministic and idempotent — safe to re-run without manual cleanup.
- All scripts use `Path(__file__).parent.parent` as BASE to resolve to project root from `pipeline/` or `tools/` subdirectory.
- Type hints where useful; validate output structures with Pydantic (already a dependency).

---

## Testing Guidelines

No formal `tests/` suite yet. Use script-level validation:

- Confirm each script exits cleanly and writes expected outputs to `database/`.
- Treat `database/parsing_errors.log` and summary counters as the quality gate (see above).
- Minimum validation run after any change: `pipeline/normalize_vault.py` → `pipeline/compile_brain.py` → `pipeline/query_brain.py --help`.

If adding automated tests, use `pytest` with `tests/test_<module>.py` naming.

---

## Commit Guidelines

No git history in this workspace. Use Conventional Commits:

```
feat: add cross-source metric matcher
fix: handle empty pdf pages in extractor
chore: re-run pipeline after new source_docs added
docs: update pipeline usage in AGENTS.md
```

---

## Security & Data Handling

Inputs contain sensitive personal information (PII, lived experience disclosures, referee contacts).

- Do **not** print, log, or surface raw document content in terminal output beyond what is needed for debugging.
- Do **not** publish raw documents, full JSON engines, or complete `Career_Brain_Knowledge.md` externally.
- Prefer sharing diffs, redacted samples, and script-level changes.
- The `archive/` directory contains legacy files — do not re-ingest without explicit instruction.

---

## See Also

| Document | Purpose |
|---|---|
| [`Career Brain Manifesto.md`](./Career%20Brain%20Manifesto.md) | Full system vision, phase specs, state machine, schema design, quality control guardrails |
| [`gem_system_prompt.md`](./gem_system_prompt.md) | Rosetta Stone matrix, retrieval rules, output formats — paste into Google AI Studio Gem |
| [`BUILD_SPECS.md`](./BUILD_SPECS.md) | Phase 5 Google Workspace integration detailed specs |
