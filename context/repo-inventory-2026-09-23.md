# Repository Inventory (2026-09-23)

## 1. Directory map

```text
.
├── .claude/ [protected placeholder]
├── BUILD_SPECS.md
├── CLAUDE.md
├── Career Brain Manifesto.md
├── PROJECT_MAP.md
├── README.md
├── TASKS.md
├── config/
│   ├── ats_rules.json
│   ├── doc_templates.json
│   ├── llm-specs/
│   │   ├── AGENT-OPS.md
│   │   ├── MANIFEST.md
│   │   └── agent-operating-spec.md
│   ├── user_config.example.json
│   └── user_config.json
├── context/
│   ├── EXTERNAL_TEMPLATES_ANALYSIS.md
│   ├── THEME_HANDOVER_BRIEF.md
│   ├── ai_studio_system_instructions.md
│   ├── ai_studio_task_phase1.md
│   ├── build_remaining_golden_masters.md
│   ├── claude_fix_and_audit_themes.md
│   ├── claude_review_companion_ats_templates.md
│   ├── gemini_25_pro_handover.md
│   ├── recap.md
│   ├── skills template prompt
│   ├── specs/
│   ├── theme_project_description.md
│   ├── theme_viz_render_spec.md
│   └── theme_viz_sample_content.md
├── docs/
│   ├── superpowers/
│   ├── theme-preview/
│   └── voice/
├── gem_system_prompt.md
├── package.json
├── pipeline/
├── planning/
│   ├── HANDOFF_*
│   ├── ai_prompt_reference/
│   ├── cleanupcodexprompt.md
│   ├── comprehensive_cleanup_prompt.md
│   ├── deep_plan_config.json
│   ├── master_agentic_workflow_prompt.md
│   ├── phase1-design-synthesis.md
│   ├── theme-extraction-spec.md
│   └── ...
├── requirements.txt
├── scratch/
│   └── fetch_doc.py
├── slop_test_doc.md
├── templates/
│   ├── MASTER_SCHEMA_V2_3.json
│   ├── patched/
│   └── ... (JSON templates)
├── tests/
└── tools/
    ├── audit_doc_style.py
    ├── build_golden_master.py
    ├── check_voice_slop.py
    ├── compile_theme.py
    ├── content_engine.py
    ├── generate_document.py
    ├── settle_golden_masters.py
    ├── test_env.py
    ├── test_key.py
    ├── theme_preview.html
    ├── validate_template_spec.py
    ├── validate_templates_v2.py
    └── verify_golden_master.py
```

## 2. Documentation and instruction surfaces

| Path / Pattern | Type | Purpose | Lifecycle | Git Status | Disposition | Confidence |
|---|---|---|---|---|---|---|
| `CLAUDE.md` | instruction | Root AI instructions/invariants | active | modified | KEEP | high |
| `gem_system_prompt.md` | instruction | Gemini system prompt | active | tracked | KEEP | high |
| `.claude/skills/*` | instruction | Claude MCP skills | active | tracked | KEEP | high |
| `config/llm-specs/*` | specification | Legacy LLM operation specs | legacy | modified | ARCHIVE | medium |
| `planning/master_agentic_workflow_prompt.md` | instruction | Workflow prompt | reference | tracked | REVIEW | medium |
| `planning/ai_prompt_reference/*` | config | Prompt templates | reference | tracked | CONSOLIDATE | low |
| `context/specs/*` | specification | Various JSON template specs | active | tracked | REVIEW | low |

**Overlapping Roles:**
- There is significant semantic overlap between root-level `CLAUDE.md`, `.claude/skills/`, `config/llm-specs/`, and `gem_system_prompt.md`.
- `planning/ai_prompt_reference/` contains prompt configurations that might overlap with `config/llm-specs/` or `.claude/skills/`.
- `context/specs/` and `docs/superpowers/specs/` indicate a fragmented specification strategy.

## 3. Templates

| Path | Type | Purpose | Lifecycle | Git Status | Disposition | Confidence |
|---|---|---|---|---|---|---|
| `templates/*.json` | template | Base/theme resume templates | active | tracked | KEEP | high |
| `templates/patched/*.json` | template | Patched theme versions | unclear | tracked | REVIEW | high |
| `templates/MASTER_SCHEMA_V2_3.json` | template | Validation schema | active | tracked | KEEP | high |
| `templates/THEME_SPEC_GUIDE.md` | documentation | Guide for templates | active | tracked | KEEP | high |

**Observation on `templates/patched/`:**
A cryptographic hash comparison (shasum) of `templates/*.json` and `templates/patched/*.json` reveals that **all files in `patched/` are currently byte-identical to their counterparts in `templates/`**. There is no observable difference. Evidence suggests `patched/` might be a backup or a staging ground for a script, but currently, it is a 1:1 duplicate.

## 4. Organisation candidates

| Candidate | Current Semantic Issues | Plausible Destinations |
|---|---|---|
| `tools/theme_preview.html` | Exists alongside python scripts in `tools/`, but is an HTML preview asset. | `docs/theme-preview/` |
| `planning/ai_prompt_reference/` | Configuration living in a planning directory. | `config/`, `.claude/` |
| `context/specs/` | Specs living in temporary context instead of docs. | `docs/specs/` |
| `planning/HANDOFF_*` | Stale historical state/sprint records cluttering active directories. | `archive/planning/` |
| `config/llm-specs/` | Ambiguous/legacy name for AI ops, potentially superseded by `.claude`. | `archive/`, `.claude/` |
| `slop_test_doc.md` | Unstructured test doc at root level. | `scratch/`, `tests/fixtures/` |

## 5. Legacy and reference signals

- **`config/llm-specs/`**: This directory is referenced in:
  - `TASKS.md`
  - `tests/test_generate_document.py`
  - `config/llm-specs/AGENT-OPS.md` (self-referential)
  - `docs/voice/voice-authenticity-profile.md`
  *Caution*: Moving or deleting `llm-specs` requires updating test fixtures and active documentation references.

- **`tools/theme_preview.html`**: No explicit text references found in root or `tools/` python scripts via grep. It appears loosely coupled, potentially standalone or referenced by uncommitted local scripts.

## 6. Risk register

- **`config/llm-specs/`**: Referenced by `test_generate_document.py`. Do not delete without refactoring the test suite.
- **`.claude/skills/`**: Active Claude Code agent tools. Modifying these without understanding the MCP manifest could break local workflows.
- **`templates/`**: Heavily relied upon by `tools/compile_theme.py` and `tools/generate_document.py`. Schema and file structures here are runtime dependencies.
- **`pipeline/*.py`**: Core data orchestration tools. Likely depend on hardcoded paths to `database/` or `processed/`. Do not move without auditing scripts.

## 7. Candidate review queue

1. **`templates/patched/`** (Low Risk, High Value): Verify if these byte-identical duplicates can be deleted.
2. **`tools/theme_preview.html`** (Low Risk, Low Value): Relocate to `docs/theme-preview/`.
3. **`planning/HANDOFF_*`** (Low Risk, High Value): Archive legacy sprint records.
4. **`config/llm-specs/` vs `.claude/skills/`** (Medium Risk, High Value): Consolidate AI instructions and update test references.
5. **`context/specs/` vs `docs/superpowers/specs/`** (Medium Risk, Medium Value): Consolidate specification documentation.
6. **`slop_test_doc.md`** (Low Risk, Low Value): Delete or move to scratch.

---

### End of Inventory

- **Scope covered**: Root files, `.claude/`, `context/`, `docs/`, `config/`, `planning/`, `templates/`, `tools/`, `scratch/`, `tests/`.
- **Scope intentionally excluded**: `.git/`, `.venv/`, `.pytest_cache/`, repomix xml artifacts.
- **Protected paths not inspected**: `source_docs/`, `processed/`, `database/`, `archive/`, `.env*`, `credentials.json`, `token.json`, and potential PII contents.
- **Known uncertainties**: The exact runtime usage of `planning/ai_prompt_reference/`, whether `templates/patched/` is generated automatically by a script or manually copied, and whether `tools/theme_preview.html` is dynamically accessed by any un-greppable tooling.
- **Suggested first verification batch for Claude Code**: Review `templates/patched/` redundancy and `planning/HANDOFF_*` archival.
