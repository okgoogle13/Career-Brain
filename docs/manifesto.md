# **PROJECT MANIFESTO: THE CAREER BRAIN DATABASE**

## **Agentic ETL Pipeline, Schema Architecture, and Taxonomy Mapping Logic**

---

## **1. VISION AND CORE MISSION**

The goal of this system is to ingest, standardize, and synthesize a vast archive of unstructured historical career documents — spanning over a decade of professional experience — into a highly structured, machine-readable **Career Brain Database**.

This database is split into three modular JSON engines to optimize Retrieval-Augmented Generation (RAG). By separating **Facts** (Career History), **Narratives** (STAR Stories/Pivots), and **Translations** (Skills & Taxonomies), we prevent LLM context-bloat and prompt drift.

This engine is designed to feed a custom, hardcoded Gemini Copilot Gem in Google AI Studio, as well as serve as a local query engine within our active IDE workspace — enabling instantaneous, precise tailoring of resumes, cover letters, and Key Selection Criteria (KSC) responses via direct Google Workspace Document generation.

---

## **2. THE LOCAL WORKSPACE ARCHITECTURE**

```
Career Brain/
├── source_docs/            Raw input files — do not edit manually
│   ├── resumes/            Raw resume variations (.pdf, .docx, legacy .doc)
│   ├── cover_letters/      Raw cover letters & introductory templates
│   ├── ksc/                Raw STAR selection criteria documents
│   └── knowledge/          Reference knowledge files
├── processed/              Phase 1 Output: sanitized .txt files
├── database/               Phase 2–4 Output: final structural database
│   ├── career_history_enriched.json
│   ├── ksc_curated.json
│   ├── skills_and_taxonomy.json
│   ├── Career_Brain_Knowledge.md
│   └── parsing_errors.log
├── pipeline/               ETL scripts (run in phase order)
│   ├── organise_raw_docs.py
│   ├── normalize_vault.py
│   ├── compile_brain.py
│   ├── curate_narratives.py
│   ├── inject_metrics.py
│   ├── clean_knowledge_vault.py
│   └── query_brain.py
├── tools/                  Phase 5 Google Workspace generation
│   ├── generate_document.py
│   ├── content_engine.py
│   ├── build_golden_master.py
│   ├── create_golden_master.py
│   ├── audit_doc_style.py
│   ├── qa_docs_check.py
│   └── validate_template_spec.py
├── templates/              Google Docs theme JSON configs
├── config/                 Runtime config: ats_rules.json, doc_templates.json, user_config.json
├── context/                AI session files: repomix XMLs, prompts, handover docs
│   └── specs/              Document format specs (resume, cover letter, KSC)
├── .claude/skills/           Versioned AI agent skill definitions
├── archive/                Legacy source files — do not re-ingest without instruction
└── tests/
```

---

## **3. STATE MACHINE & GATEKEEPER PROTOCOLS**

This pipeline operates under a strict, user-controlled sequential state gate inside our IDE's Agent Planning Mode. The model must not skip gates without explicit user validation:

| Gate | Name | Action | Transition |
|---|---|---|---|
| **1** | Blueprint Validation | Assess raw files in directories, verify path layouts, propose changes | STOP — request user approval before writing any files |
| **2** | Phase 1 Normalisation | Execute `pipeline/normalize_vault.py` to batch-process all binaries to plain .txt in `processed/` | STOP — present health ledger (file list, character count, extraction status). Wait for user approval |
| **3** | Phase 2 Semantic Compilation | Execute `pipeline/compile_brain.py` using validated Pydantic model schemas to build JSON engines in `database/` | STOP — present final database audit statistics, mapping metrics, and parsing error log |
| **4** | Phase 5 Google Docs Export | Execute `tools/generate_document.py` using Google Workspace APIs to clone templates and map extracted data | STOP — present generated document IDs/links and the generation report |

---

## **4. PHASE 0: SOURCE ORGANISATION**

**Script:** `pipeline/organise_raw_docs.py`

Moves and deduplicates raw career documents from `archive/` into the correct `source_docs/` subdirectory. Applies include/exclude rules to filter personal financial documents and non-career files. Non-reversible — run only once on a fresh workspace, or after adding new source documents.

---

## **5. PHASE 1: SANITISATION & NORMALISATION (THE VACUUM)**

**Script:** `pipeline/normalize_vault.py`  
**Input:** `source_docs/`  
**Output:** `processed/`

**Objective:** Strip container file liabilities and isolate raw strings cleanly without losing logical formatting.

**Directives:**
1. Iterate through raw files in `source_docs/resumes/`, `source_docs/cover_letters/`, `source_docs/ksc/`, `source_docs/knowledge/`, and `source_docs/references/`.
2. Programmatically convert all formats (.docx, .pdf, .doc) into plain text (.txt) files mapped to `processed/`.
3. Maintain complete downstream lineaging: output text files must retain their original raw name (e.g., `2024_Resume_FlatOut.pdf` → `resumes__2024_Resume_FlatOut.txt`).
4. If a document format is corrupt or unsupported, immediately write the error trace to `database/parsing_errors.log` with the original filename.
5. DO NOT summarize, redact, correct grammar, or logically process the text in this phase. The objective is pure string dumping.

---

## **6. PHASE 2: SEMANTIC EXTRACTION & TAXONOMY COMPILATION**

**Script:** `pipeline/compile_brain.py`  
**Input:** `processed/`  
**Output:** `database/`

**Objective:** Deconstruct raw strings into three LLM-optimized JSON engines using Pydantic runtime model schemas.

### Database Modules

**PILLAR 1 — FACT MATRIX** (`database/career_history.json`)

Chronological list of roles, employers, operational dates, and individual achievement bullet arrays.

- **Variation preservation rule:** If matching job fingerprints (unique MD5 hash of Company + Role + StartDate) are identified across multiple historical files, DO NOT choose a single master resume. AGGREGATE all semantically distinct bullet descriptions into the achievements array. Eliminate pure duplicate text strings, but preserve every nuanced variation in phrasing.
- **Bullet structure:** Deconstruct each bullet into fields: Action Verb, Task/Responsibility, Metric/Outcome (if present), Strategy/Methodology (e.g., MARAM, Oracle BPM), and Source Lineage.
- **Domain tagging:** Tag every achievement bullet dynamically with domain categories: `["project_management", "corporate_finance"]` vs `["service_coordination", "quality_assurance", "harm_reduction"]`.

**PILLAR 2 — NARRATIVE REGISTRY** (`database/ksc_and_narratives.json`)

High-impact STAR/CAR behavioral stories, cover letter introductory "hooks," and deep lived-experience "pivot narratives."

- Extract long-form paragraphs where the candidate navigates the transition from Corporate Finance to Community Services.
- Index and categorize narratives by core competency benchmarks: `["conflict_resolution", "complex_advocacy", "cultural_humility", "risk_de-escalation"]`.

**PILLAR 3 — SKILLS & TAXONOMY ENGINE / THE ROSETTA STONE** (`database/skills_and_taxonomy.json`)

An active translation key mapping corporate project/finance achievements to Community Service standards.

Core translation mappings (hardcoded):
1. **Project Management / Workstream Leadership → SERVICE COORDINATION**
2. **Regulatory Compliance / Anti-Tax Avoidance & Audit → QUALITY ASSURANCE & GOVERNANCE**
3. **High-Net-Worth Portfolio & Stakeholder Management → SECTOR ENGAGEMENT & SYSTEM ADVOCACY**

See `pipeline/compile_brain.py` (ROSETTA_STONE constant) for the full 9-mapping implementation.

---

## **7. PHASE 3: NARRATIVE CURATION**

**Script:** `pipeline/curate_narratives.py`  
**Input:** `database/ksc_and_narratives.json`  
**Output:** `database/ksc_curated.json`, `database/ksc_curated_tier1.json`, `database/narrative_curation_report.md`

Scores all narratives on 4 axes: length (word count), STAR completeness (keyword coverage), metric presence, and near-duplicate detection (Jaccard similarity ≥85%). Assigns quality_tier (1/2/3) to each narrative. Tier 1 is recommended for Gem upload — precision over volume.

---

## **8. PHASE 4: METRIC INJECTION**

**Script:** `pipeline/inject_metrics.py`  
**Input:** `database/career_history.json`  
**Output:** `database/career_history_enriched.json`, `database/metric_injection_targets.md`

Multi-pass heuristic metric injection for all bullets flagged `needs_review: true`:
- **Pass 1 (Expanded Regex):** Ordinals, frequency, team sizes, caseload language, scale phrases, timeframes — auto-clears flag if signal found.
- **Pass 2 (Cross-Source Inference):** Near-identical bullet in same role with a metric — extract and annotate.
- **Pass 3 (Sibling Context):** Suggests a metric from a sibling bullet for human confirmation.

Only bullets that survive all 3 passes go to the manual hit list in `database/metric_injection_targets.md`.

---

## **9. PHASE 5: GOOGLE DOCS TEMPLATE GENERATION (THE EXPORT)**

**Scripts:** `tools/generate_document.py`, `tools/content_engine.py`  
**Config:** `config/doc_templates.json`, `config/user_config.json`  
**Templates:** `templates/*.json`

**Objective:** Inject structured JSON output into polished, standardized Google Docs formats using the Google Workspace APIs.

**Directives:**
1. Read config from `config/doc_templates.json` to identify Golden Master Google Doc IDs for each template type (resume, cover_letter, ksc).
2. Clone the Golden Master document and perform batch text replacements using fixed placeholders (e.g., `{{TARGET_ROLE}}`, `{{BULLET_1}}`).
3. Output a `database/doc_generation_report.json` tracking filled placeholders, unresolved tokens, and generated Google Doc links.
4. Do not permanently store PII or OAuth tokens in the repository.

See `archive/planning/BUILD_SPECS_2026-05-27.md` for the full Phase 5 milestone breakdown and definition of done.

---

## **10. PIPELINE QUALITY CONTROL GUARDRAILS**

1. **Strict Type Validation:** All generated JSON structures must be validated at runtime via Pydantic model definitions. Any invalid objects must raise a logging action to `database/parsing_errors.log` and be bypassed rather than crashing the pipeline.

2. **The Metric Audit Loop:** For every bullet point compiled inside `career_history.json`, calculate the string length. If an achievement bullet exceeds 20 words but contains zero numerical metrics (no %, $, client counts, hours, or caseload scale), programmatically set `needs_review: true`. This flags weak points for metric injection in Phase 4.

3. **Data Lineage Integrity:** Every single narrative, skill, and history node in the final database must preserve its source. A field named `source_lineage` must record the exact raw filename to maintain total transparency. If a script strips this field, that is a critical bug.

---

## **11. MAINTENANCE AND ITERATION PROTOCOL**

Whenever a new role, certificate, or successful job application artifact is developed:

1. Drop the raw file into the appropriate directory under `source_docs/`.
2. Run Phase 1 (`pipeline/normalize_vault.py`) to generate a matching standardized text file in `processed/`.
3. Run Phase 2 (`pipeline/compile_brain.py`) to parse, merge, preserve variations, and compile the update directly into the 3-pillar files in `database/`.
4. Optionally run Phases 3–4 to re-score narratives and resolve any new metric gaps.
5. The Custom AI Gem's memory layer is instantly kept pristine, synchronized, and optimized for future tailoring.