# CLAUDE.md - Career Brain Operating Guide

## AI Agent Operating Principles (Karpathy)

> Read this before acting. Violating these is worse than doing nothing.

1. **Verify before completing.** Read the actual file. Don't infer from filenames. Don't trust your own prior outputs as ground truth.
2. **Don't hallucinate status.** If you haven't run the command or read the file, say so. Uncertainty is fine. False confidence is not.
3. **Don't overengineer.** The pipeline works. A new abstraction layer, config file, or wrapper script needs a concrete problem to justify it — not a hypothetical future need.
4. **Smallest change that fixes the problem.** One function, one file, one commit. If you're touching five files for a one-line bug, stop and ask why.
5. **The code is the truth.** Not the task log, not a prior conversation, not your memory. Read the file.
6. **Flag uncertainty explicitly.** Prefix any extrapolation with `[inferred]`. If you can't verify, say what you'd need to verify it.
---

## Commands

### Environment Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Build & Run the Pipeline
Always run from the project root. Scripts are idempotent.
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

---

## Architecture

The pipeline compiles source documents into three JSON engines under `database/`:
- `career_history_enriched.json` — Factual work history (roles, bullets, metrics)
- `ksc_curated.json` — STAR/CAR narratives (scored + quality-tiered 1–3)
- `skills_and_taxonomy.json` — Skills, Rosetta Stone translations, domain tags

Phase 5 (`tools/`) reads all three engines to generate tailored Google Docs.
See `Career Brain Manifesto.md` for full schema specs.

> ⚠️ **MANDATORY Gatekeeper Protocol:** Stop and wait for user approval before executing each pipeline phase. See `AGENTS.md` for the full gate table. Never execute all phases autonomously.

---

## Code Quality Checklists

### 1. Verification Checklist
- **`database/parsing_errors.log`** must be empty after a run.
- **`source_lineage`** field must be present on every node in every JSON database.
- **`needs_review`** checks must confirm high numeric metric coverage (>20 words bullet points require a number).

### 2. Style Guidelines
- **Python**: Follow PEP 8 guidelines. Write clean, modular docstrings and use type annotations for core pipeline models.
- **Theme JSON Specs**: Must strictly conform to `MASTER_SCHEMA_V2_3.json`. Never duplicate band strategy, top header silhouette, or divider rhythm between adjacent themes.

---

## Gotchas

- **`archive/`**: Never re-ingest files here without explicit user instruction.
- **Rosetta Stone**: The corporate → community-services translation map is a hardcoded constant in `compile_brain.py`. Edit there and re-run Phase 2 to change it.
- **`needs_review` flag**: Managed by pipeline scripts — do not manually remove. `inject_metrics.py` targets these bullets automatically.
- **SDK**: Uses `google-genai` 2.7.0 (not the legacy `google-generativeai`). Phase 5 LLM calls require `GEMINI_API_KEY` in `.env`; falls back to heuristic split if unset.
