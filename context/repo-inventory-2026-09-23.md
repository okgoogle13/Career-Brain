# Repository Inventory (2026-09-23)

## 1. Root Directory Tree
*Excluding `.git`, `.venv`, `source_docs/`, `processed/`, `database/`, `archive/`, caches, binaries, and secret files.*

```text
.
├── BUILD_SPECS.md
├── CLAUDE.md
├── Career Brain Manifesto.md
├── PROJECT_MAP.md
├── README.md
├── TASKS.md
├── careerbrain-repomix-vram-summary.xml
├── config/
│   ├── ats_rules.json
│   ├── doc_templates.json
│   ├── llm-specs/
│   └── user_config.example.json
├── context/
│   ├── EXTERNAL_TEMPLATES_ANALYSIS.md
│   ├── THEME_HANDOVER_BRIEF.md
│   ├── ai_studio_system_instructions.md
│   ├── recap.md
│   ├── specs/
│   └── ... (XML and MD context files)
├── docs/
│   ├── superpowers/
│   ├── theme-preview/
│   └── voice/
├── gem_system_prompt.md
├── package.json
├── pipeline/
│   ├── audit_and_repair_database.py
│   ├── clean_knowledge_vault.py
│   ├── compile_brain.py
│   ├── curate_narratives.py
│   ├── inject_metrics.py
│   ├── normalize_vault.py
│   ├── organise_raw_docs.py
│   └── query_brain.py
├── planning/
│   ├── HANDOFF_*_COMPLETE_*.md
│   ├── ai_prompt_reference/
│   └── ... (planning prompts and configs)
├── repomix-output-lite.xml
├── repomix-output.xml
├── requirements.txt
├── scratch/
│   └── fetch_doc.py
├── slop_test_doc.md
├── templates/
│   ├── MASTER_SCHEMA_V2_3.json
│   ├── patched/
│   └── ... (JSON templates)
├── tests/
│   ├── test_build_golden_master.py
│   └── test_generate_document.py
└── tools/
    ├── audit_doc_style.py
    ├── build_golden_master.py
    ├── check_voice_slop.py
    ├── compile_theme.py
    ├── content_engine.py
    ├── generate_document.py
    ├── settle_golden_masters.py
    ├── validate_template_spec.py
    └── ...
```
*(Filtered to show structure; full file details below)*

## 2. File details

| Path | Purpose | Git State | Size | Status |
|---|---|---|---|---|
| `./pipeline/*.py` | Core data processing pipeline scripts | Tracked (`curate_narratives.py` modified) | 5KB - 45KB | Active |
| `./tools/*.py` | Helper scripts for generation and validation | Tracked / Untracked (`test_env.py`, `test_key.py`, `settle_golden_masters.py`) | 1KB - 54KB | Active / Some unclear |
| `./config/` | Configuration files and LLM specifications | Tracked (Some modified) | < 10KB | Active |
| `./templates/` | JSON structures for resumes and cover letters | Tracked (Some modified) | 4KB - 10KB | Active |
| `./templates/patched/` | Duplicate JSON templates | Tracked | ~6KB | Unclear / Legacy |
| `./context/` | Background context for LLMs (MD, XML) | Tracked | 2KB - 403KB | Active / Legacy |
| `./planning/` | Sprint planning, handoff records, prompts | Tracked (`HANDOFF_6_PROMPT.md` untracked) | 1KB - 26KB | Legacy / Active |
| `./docs/` | Rendered previews and voice exemplars | Tracked | 9KB - 71KB | Active |
| `./repomix-output*.xml` | Consolidated repo context | Tracked | 1.6MB - 19.9MB | Generated |
| `./slop_test_doc.md` | Test document | Untracked | < 1KB | Unclear |
| `./scratch/` | Scratchpad / ad-hoc scripts | Tracked | < 1KB | Unclear |
| Root `.md` files | Core documentation and manifests | Tracked (Some modified) | 4KB - 26KB | Active |

## 3. Git Summary

- **Branch:** `main` (ahead of `origin/main` by 5 commits)
- **State:** Dirty
- **Modified files:**
  - `CLAUDE.md`, `TASKS.md`, `config/doc_templates.json`, `config/llm-specs/AGENT-OPS.md`, `config/llm-specs/MANIFEST.md`, `context/specs/resume_template_spec.md`, `pipeline/curate_narratives.py`, `requirements.txt`, `scratch/golden_master_verification.pdf`, `templates/ksc_standard_v2.json`, `templates/schema_v2_0.json`, `tools/audit_doc_style.py`, `tools/build_golden_master.py`, `tools/check_voice_slop.py`, `tools/validate_template_spec.py`, `tools/validate_templates_v2.py`
- **Untracked files:**
  - `planning/HANDOFF_6_PROMPT.md`, `slop_test_doc.md`, `tools/settle_golden_masters.py`, `tools/test_env.py`, `tools/test_key.py`

**Latest 10 commits:**
```text
55ff093 (HEAD -> main) docs: condense root CLAUDE.md to core invariants
0f01de3 Fix: address audit feedback and unapproved changes
fcfc475 docs: update 1Password secret name references
d50617e chore: update TASKS.md with network verification failures for BS-1.x and BS-2.1
c0da79f chore: execute claude agent plan for TASK-005-B and BS-7.2
ef65d3d (origin/main, origin/HEAD) chore: update llm specs manifest and add document fetcher scratch script
78b4b0d sync: update config/llm-specs/ from +JOB sync
8c4e7ee docs: resync +JOB spec, close voice-profile Known gaps 5-6
9e182a8 docs: inherit +JOB block in voice-authenticity-profile
835c034 fix: mask proper nouns before AU terminology substitution (BS-7.3/7.4)
```

## 4. Candidates for Cleanup (Flagged for Review)

- **Duplicates:**
  - `./templates/patched/*` mirrors files in `./templates/`
- **Stale-references:**
  - `planning/HANDOFF_*_COMPLETE_*.md` (Historical handoff files, possibly legacy)
- **Oversized-docs:**
  - `repomix-output.xml` (19.9MB)
  - `repomix-output-lite.xml` (1.6MB)
  - `context/CareerBrain_Themes_Handover_Context.xml` (403KB)
- **Unclear-purpose candidates:**
  - `slop_test_doc.md`
  - `tools/test_env.py`
  - `tools/test_key.py`
  - `scratch/fetch_doc.py`

## 5. Protected-path List

- `source_docs/`
- `processed/`
- `database/`
- `archive/`
- `.env*`
- `credentials.json`
- `token.json`
- Any files likely containing PII.

## 6. Audit Metadata

**Exact commands run:**
1. `git status`
2. `git log -n 10 --oneline`
3. `tree -L 3 -I '.git|.venv|source_docs|processed|database|archive|__pycache__|*.pyc|.DS_Store'`
4. `find . -maxdepth 3 -type f -not -path '*/\.git/*' -not -path '*/\.venv/*' -not -path './source_docs/*' -not -path './processed/*' -not -path './database/*' -not -path './archive/*' -not -path '*/__pycache__/*' -not -name '*.pyc' -not -name '.DS_Store' -exec stat -f "%N %z" {} +`

**Paths not inspected:**
- `.git/`
- `.venv/`
- `source_docs/`
- `processed/`
- `database/`
- `archive/`
- Any depths beyond 3 levels.
- File contents were not read.

Inventory complete — ready for Claude cleanup planning.
