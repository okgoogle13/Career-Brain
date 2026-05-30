# Career Brain

A local Python ETL pipeline that turns a decade of mixed-format career documents into a structured, machine-readable database — then uses that database to generate tailored resumes, cover letters, and KSC responses via Google Docs.

---

## How it works

```
source_docs/  →  pipeline/  →  processed/  →  database/  →  Google Docs
(raw files)     (ETL scripts)  (plain text)  (JSON engines)  (via tools/)
```

**5 phases, gate-controlled — never skip steps, never run autonomously:**

| Phase | Script | What it does |
|---|---|---|
| 0 — Sort | `pipeline/organise_raw_docs.py` | Moves files from `archive/` into `source_docs/` |
| 1 — Extract | `pipeline/normalize_vault.py` | Converts .docx/.pdf/.doc → plain .txt in `processed/` |
| 2 — Compile | `pipeline/compile_brain.py` | Builds 3 JSON engines in `database/` |
| 3 — Curate | `pipeline/curate_narratives.py` | Scores and tiers STAR narratives |
| 4 — Enrich | `pipeline/inject_metrics.py` | Auto-resolves metric gaps |
| 5 — Generate | `tools/generate_document.py` | Clones Google Doc templates and fills them |

---

## Folder structure

```
Career Brain/
├── source_docs/        Your original career documents (inputs — do not edit manually)
│   ├── resumes/
│   ├── cover_letters/
│   ├── ksc/
│   └── knowledge/
│
├── processed/          Phase 1 output: plain .txt extractions (auto-generated)
│
├── database/           Phase 2-4 output: the compiled Career Brain (auto-generated)
│   ├── career_history_enriched.json
│   ├── ksc_curated.json
│   ├── skills_and_taxonomy.json
│   ├── Career_Brain_Knowledge.md
│   └── parsing_errors.log        ← check this after every run
│
├── pipeline/           ETL scripts — run in order
│   ├── organise_raw_docs.py
│   ├── normalize_vault.py
│   ├── compile_brain.py
│   ├── curate_narratives.py
│   ├── inject_metrics.py
│   ├── clean_knowledge_vault.py
│   └── query_brain.py            ← interactive CLI
│
├── tools/              Phase 5: Google Docs generation scripts
│   ├── generate_document.py
│   ├── content_engine.py
│   ├── build_golden_master.py
│   ├── create_golden_master.py
│   ├── audit_doc_style.py
│   ├── qa_docs_check.py
│   └── validate_template_spec.py
│
├── templates/          Google Docs theme configs (JSON + THEME_SPEC_GUIDE.md)
├── config/             Runtime config: ats_rules.json, doc_templates.json, user_config.json
├── context/            AI session files: repomix XMLs, prompts, handover docs
│   └── specs/          Document format specs (resume, cover letter, KSC)
├── .claude/skills/       AI agent skill definitions (versioned)
│   ├── _archived_v1/
│   ├── ats_template_qa_v3/
│   ├── docs_style_auditor_v3/
│   └── gold_template_builder_v3/
├── scratch/            One-off investigation scripts (not part of pipeline)
├── archive/            Legacy source files — do not re-ingest without explicit instruction
├── tests/
│
├── AGENTS.md                    Agent operating instructions (read before acting)
├── Career Brain Manifesto.md    Full system design and schema specs
├── BUILD_SPECS.md               Phase 5 Google Workspace build specs
├── gem_system_prompt.md         Paste into Google AI Studio Custom Gem
└── requirements.txt
```

---

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the pipeline

Scripts are idempotent — safe to re-run. Always run from the project root or from within the `pipeline/` or `tools/` directory.

```bash
python3 pipeline/organise_raw_docs.py    # Phase 0: sort and deduplicate source docs
python3 pipeline/normalize_vault.py      # Phase 1: extract binary files to plain text
python3 pipeline/compile_brain.py        # Phase 2: build 3-pillar JSON database
python3 pipeline/curate_narratives.py    # Phase 3: score and tier narratives
python3 pipeline/inject_metrics.py       # Phase 4: auto-resolve metric flags
python3 tools/generate_document.py --target "Role Name" --template resume  # Phase 5
python3 pipeline/query_brain.py --help   # verify CLI is intact
```

## Quality checks — run after every phase

1. **`database/parsing_errors.log`** — any entry = failure. Investigate before continuing.
2. **`needs_review: true`** flags — set on bullets >20 words with no numeric metrics. Target for `inject_metrics.py`.
3. **`source_lineage` field** — must be present on every node in every JSON engine. If missing, that is a critical bug.
4. **Summary counters** — `compile_brain.py` prints role/bullet/narrative counts. Compare against previous run to catch regressions.

---

## Security

Source documents contain PII and sensitive personal information. Do not print or log raw document content beyond debugging needs. Do not publish JSON engines, `Career_Brain_Knowledge.md`, or raw source docs externally. See `AGENTS.md` for the full security and gatekeeper protocol.
