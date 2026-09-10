# CLAUDE.md - Career Brain Operating Guide

> **For AI agents (Codex, Antigravity, Claude Code, etc.):** Read this file in full before taking any action.
> Full architectural context is in [`Career Brain Manifesto.md`](./Career%20Brain%20Manifesto.md).

## AI Agent Operating Principles (Karpathy)

> Read this before acting. Violating these is worse than doing nothing.

1. **Verify before completing.** Read the actual file. Don't infer from filenames. Don't trust your own prior outputs as ground truth.
2. **Don't hallucinate status.** If you haven't run the command or read the file, say so. Uncertainty is fine. False confidence is not.
3. **Don't overengineer.** The pipeline works. A new abstraction layer, config file, or wrapper script needs a concrete problem to justify it — not a hypothetical future need.
4. **Smallest change that fixes the problem.** One function, one file, one commit. If you're touching five files for a one-line bug, stop and ask why.
5. **The code is the truth.** Not the task log, not a prior conversation, not your memory. Read the file.
6. **Flag uncertainty explicitly.** Prefix any extrapolation with `[inferred]`. If you can't verify, say what you'd need to verify it.

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
├── .claude/skills/       Versioned AI agent skill definitions
│   ├── _archived_v1/
│   ├── ats_template_qa_v3/
│   ├── docs_style_auditor_v3/
│   └── gold_template_builder_v3/
├── scratch/            One-off investigation scripts (not pipeline)
├── archive/            Legacy files — do not re-ingest without instruction
├── tests/
├── CLAUDE.md                   This file
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

**Gate 4 wording authority:** all generated application copy is governed by
`docs/voice/voice-authenticity-profile.md`, enforced via `config/ats_rules.json`
(`vocabulary.banned_phrases`, `review_phrases`, `overclaim_terms`,
`terminology.australian_spelling`). Review every `banned_phrase_detected`,
`review_phrase_flagged` and `overclaim_term_flagged` warning in the run report before
submitting. Only spelling is auto-corrected; phrases are never silently rewritten.

---

## Commands

### Environment Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Build & Run the Pipeline
Always run from the project root. Scripts are idempotent — safe to re-run. Each phase reads the previous phase's output directory.
```bash
python3 pipeline/organise_raw_docs.py    # Phase 0: Sort & deduplicate raw files
python3 pipeline/normalize_vault.py      # Phase 1: Extract binary formats to .txt
python3 pipeline/compile_brain.py        # Phase 2: Build 3-pillar JSON database
python3 pipeline/curate_narratives.py    # Phase 3: Score and tier STAR narratives
python3 pipeline/inject_metrics.py       # Phase 4: Auto-resolve metric flags
# Phase 5 requires .env with Google OAuth credentials (credentials.json + token.json) and optionally GEMINI_API_KEY
python3 tools/generate_document.py --target "Role Name" --template resume  # Phase 5: Generate doc
python3 pipeline/query_brain.py --help   # Verify interactive CLI
```

```bash
python3 tools/compile_theme.py <theme-XX-name.json>  # Compile v2.3 theme spec → v2.0 production template
python3 tools/build_golden_master.py <template_v1.json>  # Build/rebuild a Golden Master Google Doc
```

### Quality & Validation Tools
```bash
python3 tools/validate_template_spec.py  # Validate JSON themes against spec schema
python3 tools/qa_docs_check.py           # QA check generated docs
python3 tools/audit_doc_style.py         # Style auditing for built templates
```

### Running Tests
```bash
pytest                                   # Run all automated tests
```

No formal `tests/` suite yet beyond this. Minimum validation run after any pipeline change:
`pipeline/normalize_vault.py` → `pipeline/compile_brain.py` → `pipeline/query_brain.py --help`.
If adding automated tests, use `pytest` with `tests/test_<module>.py` naming.

---

## Architecture

The pipeline compiles source documents into three JSON engines under `database/`:
- `career_history_enriched.json` — Factual work history (roles, bullets, metrics)
- `ksc_curated.json` — STAR/CAR narratives (scored + quality-tiered 1–3)
- `skills_and_taxonomy.json` — Skills, Rosetta Stone translations, domain tags

Phase 5 (`tools/`) reads all three engines to generate tailored Google Docs.
See `Career Brain Manifesto.md` for full schema specs.

- `config/` — Runtime config: `user_config.json` (contact/education data for Phase 5), `doc_templates.json` (Golden Master Drive IDs), `ats_rules.json`

### Output Schema — Quick Reference

| File | Pillar | Key fields |
|---|---|---|
| `database/career_history_enriched.json` | Fact Matrix | `company`, `role`, `start_date`, `achievements[]`, `action_verb`, `metric_outcome`, `domain_tags[]`, `needs_review`, `source_lineage` |
| `database/ksc_curated.json` | Narrative Registry | `type` (STAR/CAR/hook/pivot), `competency_tags[]`, `quality_tier`, `full_text`, `source_lineage` |
| `database/skills_and_taxonomy.json` | Rosetta Stone / Skills | `corporate_framing`, `community_translation`, `community_keywords[]`, `contextual_bridge` |

For full schema specs and phase extraction logic, see [`Career Brain Manifesto.md`](./Career%20Brain%20Manifesto.md) §4–6.

---

## Code Quality Checklists

### 1. Verification Checklist
- **`database/parsing_errors.log`** must be empty after a run. Any entry is a failure — investigate before proceeding.
- **`source_lineage`** field must be present on every node in every JSON database. If a script strips this field, that is a critical bug.
- **`needs_review`** checks must confirm high numeric metric coverage (>20 words bullet points require a number). Set automatically; targets for `pipeline/inject_metrics.py`. Do not manually remove this flag.
- **Summary counters** — `compile_brain.py` prints role count, bullet count, and narrative count. Compare against previous run to catch regressions.

### 2. Style Guidelines
- **Python**: Follow PEP 8 guidelines. 4-space indentation, UTF-8 source files. Use `Path`-based file handling (`pathlib`), structured `logging` over `print()`. `snake_case` for functions/variables/files; `UPPER_SNAKE_CASE` for constants. Write clean, modular docstrings and use type annotations for core pipeline models. All scripts use `Path(__file__).parent.parent` as BASE to resolve to project root from `pipeline/` or `tools/` subdirectory. Validate output structures with Pydantic (already a dependency).
- **Theme JSON Specs**: Must strictly conform to `MASTER_SCHEMA_V2_3.json`. Never duplicate band strategy, top header silhouette, or divider rhythm between adjacent themes.

### 3. Commit Guidelines
Use Conventional Commits:
```
feat: add cross-source metric matcher
fix: handle empty pdf pages in extractor
chore: re-run pipeline after new source_docs added
docs: update pipeline usage in CLAUDE.md
```

---

## Gotchas

- **`archive/`**: Never re-ingest files here without explicit user instruction.
- **Rosetta Stone**: The corporate → community-services translation map is a hardcoded constant in `compile_brain.py`. Edit there and re-run Phase 2 to change it.
- **`needs_review` flag**: Managed by pipeline scripts — do not manually remove. `inject_metrics.py` targets these bullets automatically.
- **SDK**: Uses `google-genai` 2.7.0 (not the legacy `google-generativeai`). Phase 5 LLM calls require `GEMINI_API_KEY` in `.env`; falls back to heuristic split if unset.

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
