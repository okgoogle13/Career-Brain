# Master Agentic Workflow: Comprehensive Multi-Agent Integration Guide & Prompting Suite

This document serves as your single consolidated master resource for **TASK-005 (Theme Standardisation)**. It defines the complete multi-agent division of labor, explicit tool configurations, advanced settings (thinking levels, effort, MCP tools), and contains copy-paste ready master prompts to execute the entire theme and document synthesis pipeline.

---

## 🏛️ Section 1: The Triad Division of Labor & Executive Placement

To achieve a production-ready, visually stunning, and ATS-safe document suite (Resumes, Cover Letters, and KSC templates matching themes 01–13) without exhausting context limits or token budget, the work is strictly segregated by agent capability:

```mermaid
graph TD
    A[Gemini 3.1 Pro/Thinking <br/>in Google AI Studio] -->|1. Multimodal Design Critique & Spec Synthesis| B(planning/phase1-design-synthesis.md)
    B -->|2. Seed benchmarks & Schema TDD| C[Claude Code CLI <br/>Sonnet 3.5 / Opus]
    C -->|3. Validated seed themes 11, 12, 13| D[Gemini via Antigravity IDE <br/>Autonomous Scale-up]
    D -->|4. Mass-generates matching CL / KSC templates| E(templates/theme-01...13 suite)
    E -->|5. Visual audit & HTML/SVG previews| F[Claude Desktop <br/>Interactive Artifacts]
```

### 1. Where to Run the Prompts & Why

*   **Gemini 3.1 Pro / Advanced (Thinking) [Google AI Studio / API]:**
    *   *Task:* Multimodal Design Critique & Concept Synthesis (Phase 1).
    *   *Why:* Ingesting 8 separate resume PDF designs demands native visual/multimodal eyes. Gemini’s **2M token context window** allows it to hold all PDFs, the entire codebase schema (`MASTER_SCHEMA_V2_3.json`), and the existing 10 themes simultaneously without context fatigue.
*   **Claude Code CLI [Local Terminal]:**
    *   *Task:* Seed TDD Theme Implementation (Phase 2).
    *   *Why:* Claude Code operates in a terminal-bound, high-speed loop. It has local tool access to immediately run tests (`validate_template_spec.py`) and correct files. Tasks requiring precise coding to a strict schema are best completed here.
*   **Gemini Agent [Antigravity IDE]:**
    *   *Task:* Autonomous Theme Scale-up & Synchronization (Phase 3).
    *   *Why:* Scaling matching Cover Letters and KSCs across all 13 themes is a high-volume, highly repetitive task. Gemini can swallow the whole workspace and automate file creation at zero cost, freeing Claude from token-heavy repetition.
*   **Claude Desktop [Web Chat]:**
    *   *Task:* Interactive Visual Audits (Phase 4).
    *   *Why:* Claude Desktop's **Artifacts rendering engine** is unmatched for visual feedback. It can render HTML/SVG previews of the entire document suite side-by-side.

---

## 🛠️ Section 2: Strategic Tool & Configuration Matrix

This matrix establishes precisely when to invoke specific tools and how to configure them for maximum quality and cost efficiency.

### 1. Claude Code CLI Advanced Settings

When invoking Claude Code, use the following configuration settings tailored to the task complexity:

| Complexity Profile | CLI Settings & Flag Allocations | Recommended Tasks | Rationale |
|---|---|---|---|
| **Medium / High** | `claude -t high` or default | Standard day-to-day coding loop, minor refactors, and simple scripts. | Minimizes execution cost while maintaining fast response times and high code quality. |
| **X-High** | `claude -t xhigh` <br/>*or* `--thinking-level=xhigh` | Tricky, mathematically intense, or highly constrained bugs (e.g., the `updateTextStyle` ordering bug in `build_golden_master.py`). | Forces Sonnet to spend substantial compute cycles reasoning on a single block of code before outputting. |
| **Ultracode / Workflows** | `claude --model opus` <br/>*or* `claude --workflow` | Large-scale structural changes, major schema upgrades, and multi-file orchestrations. | Parallelizes validations, enforces rigorous task separation, and keeps the main chat context clean. |

---

### 2. Antigravity IDE (Gemini Agent) MCP Tool Matrix

Use the following mapping to choose the correct autonomous MCP tools within the Antigravity IDE:

```
                    Is the task investigatory or active execution?
                                  │
                 ┌────────────────┴────────────────┐
                 ▼                                 ▼
           Investigatory                        Execution
                 │                                 │
         ┌───────┴───────┐                 ┌───────┴───────┐
         ▼               ▼                 ▼               ▼
   [deep-research] [sequential-thinking]  [deep-plan]  [deep-implement]
   Wide folder      Deep logic / step     TDD prep &   Strict checklist
   analysis &       by step evaluation    schema-first execution matching
   mapping          avoiding shortcuts    architecture  tasks.md
```

*   **`deep-plan`:** Invoke when making major architectural changes (e.g., restructuring the relationship between Cover Letters and Resume themes). It prepares a strict implementation plan, analyzes risks, and creates TDD test stubs.
*   **`deep-implement`:** Invoke when executing the step-by-step list in `tasks.md`. It tracks state, keeps code updates minimal, and runs continuous verification.
*   **`deep-project` / `deep-research`:** Invoke for initial directory-wide audits, mapping requirements across directories, or researching cross-source references (e.g., comparing old `archive/` formats to new schema layouts).
*   **`sequential thinking mcp` (Sequential Thinking):** Always use first for complex, logically constrained problems. It prevents the agent from rushing to a shallow solution by forcing it to write out its cognitive steps (conjectures, constraints, and revisions) in a separate thought stream.
*   **`superpowers`:** Use for direct workspace optimization and terminal-driven automation steps.

---

## 📋 Section 3: Current Status & Gap Resolution Roadmap

> **Last updated: 2026-06-06**

### TASK-005 — Theme Standardisation ✅ COMPLETE

All 15 Golden Masters built, style-audited (15/15 STYLE OK), premium fonts baked in, and registered in `config/doc_templates.json`. The three gaps listed in the original version of this document are closed:
- `planning/phase1-design-synthesis.md` — exists
- Themes 21–25 (the actual final set) — built and registered
- `updateTextStyle` ordering bug — fixed (commit `30d00de`) and verified live

---

### TASK-006 — Cover Letter & KSC Template Suite (ACTIVE)

#### Confirmed State (verified 2026-06-06)

| Check | Status |
|---|---|
| `user_config.json` populated (BS-1.1) | ✅ Done — name, email, education present |
| Drive folder IDs in `doc_templates.json` (BS-1.7) | ✅ Done — all 4 folders configured |
| Cover Letter Golden Masters in `doc_templates.json` | ✅ Done — base + government + nfp + private IDs present |
| KSC Golden Master ID in `doc_templates.json` | ✅ Done — `ksc_standard_v2.json` ID registered |
| `--dry-run` passes for all 3 doc types | ✅ Done — resume 54 filled, CL 16 filled, KSC 5 filled |

> **Note:** `validate_template_spec.py` reports failures on CL and KSC templates for chars like `●`, `✅`, `❌`, `|` — these are false positives from the validator scanning the `forbidden_glyphs` *definition field itself*, not document content. Same false positives appear on all resume templates. Not a blocker.

#### Remaining Gate Items

```
[BS-1.4] Build Golden Master: Cover Letter (Government)
         Template: templates/cover_letter_government_v1.json
         Requires: Gate 4 approval → build_golden_master.py
                    │
                    ▼
[BS-1.5] Build Golden Master: Cover Letter (NFP)
         Template: templates/cover_letter_nfp_v1.json
         Requires: Gate 4 approval → build_golden_master.py
                    │
                    ▼
[BS-1.6] Verify KSC Golden Master still valid after font changes
         Template: templates/ksc_standard_v2.json
         Action: run audit_doc_style.py on the registered KSC doc ID
                    │
                    ▼
[BS-2.1] ATS QA audit on all active Golden Masters (0 failures required)
         Action: run tools/qa_docs_check.py (or ATS QA skill) on each live doc
                    │
                    ▼
[BS-2.2] Lock template versions in doc_templates.json
```

#### Gate 4 Command Reference

```bash
# Build Cover Letter Golden Master (requires Google OAuth active)
python3 tools/build_golden_master.py templates/cover_letter_government_v1.json

# Audit the resulting doc
python3 tools/audit_doc_style.py --doc-id <returned_doc_id>

# Verify KSC Golden Master
python3 tools/audit_doc_style.py --doc-id 1vtekKqdoK_MoavvlxD5qBg4KNkTJInnOJ2ZAALcxBes
```

---

## ✍️ Section 4: The Polished Master Prompts Suite

Below are the optimized, highly structured master prompts for each stage of the project.

---

### Prompt A: Multimodal Design Critique & Concept Synthesis
*   **Execute In:** Gemini 3.1 Pro / Advanced (Thinking) in **Google AI Studio** or API.
*   **Inputs:** Upload the 8 template PDFs + paste this prompt.

```xml
<design_critique_prompt>
<system_context>
You are an elite typographer and visual designer. You are evaluating 8 external resume template PDFs to extract their design grammar and synthesize them into 3 distinct, production-ready ATS-safe "Pastel Contemporary" theme specifications for the "Career Brain" pipeline.
</system_context>

<constraints>
- Hard ATS Safety: Single-column only, no tables, no floating text boxes, no headers/footers, no graphic icons/emojis.
- Fonts: Arial, Calibri, or Georgia only (whitelisted Google Docs fonts).
- Base Size: 10.5pt.
- Line Spacing: 1.22 to 1.28.
- Color: High-contrast body text (#1F1F1F or darker). Pastels must only be used as micro-accents or background tints behind high-contrast text.
</constraints>

<critique_skill_chain>
1. **Analyze (Reasoning):** Inspect each of the 8 uploaded PDFs. Critique their layout grids, spacing, typographical hierarchies, and identify which elements violate ATS safety.
2. **Score:** Evaluate each template on clarity, distinctiveness, accessibility, and ATS-compatibility.
3. **Synthesize:** Extract the strongest features and combine them into 3 cohesive, visually distinct "Pastel Contemporary" concepts. They must differ from existing themes 01-10 on at least 3 dimensions (band placement, divider grammar, header silhouette, palette mood, or accent logic).
</critique_skill_chain>

<output_format>
Write your complete response to a markdown file format. You must cover these sections for each of the 3 synthesized concepts:
- **Concept Name & Visual Identity:** Silhouette, density target, motif name, and mood.
- **Palette:** Precise 6-digit uppercase hex codes only (e.g., #EBF8FF, #2B6CB0). No shorthand. Explicitly assign: base_colours, complementary_accent, neutral_surface, neutral_text, neutral_background, and supporting_neutral.
- **Typography:** Exact base font family, font size, line spacing, heading weights, and heading sizes.
- **Layout & Rhythm:** Margins (in inches), band strategy (height in pt, intensity, and location), and divider grammar (solid, dashed, editorial-mix, etc.).
- **Accent Logic:** Strict rules for where color is allowed vs. forbidden.
- **Anti-Generic Rules:** Guardrails to prevent the design from falling back to boring templates.
- **Source Attribution:** List which of the 8 PDFs contributed which elements to this concept.
</output_format>

<directive>
Execute the critique skill chain in full. Write the resulting 3 design specifications into a single, cohesive, production-ready markdown file.
</directive>
</design_critique_prompt>
```

---

### Prompt B: Claude Code CLI Seed TDD Implementation
*   **Execute In:** Local Terminal using **Claude Code**.
*   **CLI Invocation Syntax:**  
    `claude --model sonnet --thinking-level xhigh`
*   **Inputs:** Paste this prompt once the session starts.

```xml
<claude_code_tdd_prompt>
<system_context>
You are an expert software engineer running inside the Claude Code CLI with advanced thinking enabled (--thinking-level=xhigh). You are executing Phase 2 of the Career Brain Theme Standardisation plan.
</system_context>

<objective>
Translate the newly synthesized text specifications in `planning/phase1-design-synthesis.md` into 3 production-ready, schema-validated JSON files inside `templates/`.
</objective>

<execution_instructions>
1. Read `planning/phase1-design-synthesis.md`.
2. Read the master schema at `templates/MASTER_SCHEMA_V2_3.json`.
3. Read an existing theme (e.g., `templates/theme-01-graphite-ledger.json`) to understand correct formatting and key layout.
4. Write the 3 JSON files:
   - `templates/theme-11-gentle-authority.json`
   - `templates/theme-12-contemporary-lilac.json`
   - `templates/theme-13-warm-minimal.json`
5. Run the schema validator:
   `python3 tools/validate_template_spec.py templates/theme-11-gentle-authority.json`
   `python3 tools/validate_template_spec.py templates/theme-12-contemporary-lilac.json`
   `python3 tools/validate_template_spec.py templates/theme-13-warm-minimal.json`
6. Correct all hex codes to be 6-digit uppercase. Ensure 100% compliance with ATS rules (single-column, correct font whitelist).
7. Create a `tasks.md` file in the root directory to track your checklist and log all verification outcomes.
</execution_instructions>

<verification_criteria>
- No parsing errors from `validate_template_spec.py`.
- No two themes share the same band_placement + divider_rhythm.
- All hex codes are uppercase and fully expanded (e.g., #4A5568).
</verification_criteria>
</claude_code_tdd_prompt>
```

---

### Prompt C: Gemini Autonomous Theme Scale-up & Synchronization
*   **Execute In:** Gemini Agent via the **Antigravity IDE** planning mode.
*   **Inputs:** Paste this prompt into the Antigravity session.

```xml
<antigravity_scaleup_prompt>
<system_context>
You are the Gemini Agent operating autonomously inside the Antigravity IDE workspace. You are executing Phase 3 of the Theme Standardisation plan using your deep codebase search and batch-generation capabilities.
</system_context>

<objective>
Using the 3 new validated JSON seed themes (11, 12, 13) as a design benchmark, scale the theme architecture so that every Resume theme has a perfectly matching Cover Letter and KSC template inside the `templates/` directory.
</objective>

<actions>
1. Read the new theme JSON files (`templates/theme-11-*.json`, `theme-12-*.json`, `theme-13-*.json`).
2. Read the base templates: `templates/cover_letter_base_v1.json` and `templates/ksc_base_v1.json`.
3. For every theme from 01 through 13:
   - Generate a matching Cover Letter template (e.g., `templates/cover_letter_theme_01_graphite_ledger.json`).
   - Generate a matching KSC template (e.g., `templates/ksc_theme_01_graphite_ledger.json`).
   - Deep-copy the exact color palette, primary/secondary accents, fonts, margins, line spacing, and divider/border logic from the resume theme into the respective Cover Letter and KSC files.
4. Verify that all 39 templates (13 Resumes + 13 Cover Letters + 13 KSCs) are perfectly aligned, fully populated, and syntactically correct.
5. Generate a comprehensive validation report at `planning/QUALITY_SUMMARY.md` tracking the complete suite.
</actions>

<karpathy_rules>
- Smallest change that solves the problem.
- Maintain complete source lineage.
- Zero placeholder strings.
</karpathy_rules>
</antigravity_scaleup_prompt>
```

---

### Prompt D: Claude Desktop Visual Preview Rendering
*   **Execute In:** **Claude Desktop** (Web Chat).
*   **Inputs:** Attach the v2.3 theme JSONs + paste this prompt.

```xml
<claude_desktop_preview_prompt>
<system_context>
You are an expert frontend engineer and UI/UX designer. You are evaluating the complete Career Brain document theme suite (Resumes, Cover Letters, and KSCs).
</system_context>

<objective>
Render a side-by-side, high-fidelity visual gallery of the document suite for the user's final aesthetic review and sign-off.
</objective>

<action>
1. Parse the attached JSON theme files.
2. Render an interactive, beautifully structured HTML/CSS preview dashboard as a Claude Artifact.
3. The dashboard must show:
   - A side-by-side comparison of a Resume, Cover Letter, and KSC response.
   - Live color palette chips showing exact contrast ratios.
   - Interactive toggles to switch between Theme 11 (Gentle Authority), Theme 12 (Contemporary Lilac), and Theme 13 (Warm Minimal).
4. Use standard, high-quality Tailwind CSS or modern vanilla CSS to make the layouts look exactly like printed A4 documents.
</action>

<output_instructions>
Create a single, self-contained HTML/CSS file containing the dashboard and render it directly inside an interactive Claude Artifact.
</output_instructions>
</claude_desktop_preview_prompt>
```

---

## 🚀 Section 5: TASK-006 Stage 2 — Cover Letter & KSC Build Prompts

These prompts are the active execution suite for the remaining open items. Section 4 prompts are now historical (TASK-005 reference only).

---

### Prompt E: Build Cover Letter Golden Masters (BS-1.4, BS-1.5)
*   **Execute In:** Local Terminal using **Claude Code CLI** (requires active Google OAuth).
*   **Gate:** Requires explicit user approval before running `build_golden_master.py` (AGENTS.md Gate 4).

```xml
<cover_letter_golden_master_prompt>
<system_context>
You are Claude Code CLI executing TASK-006 Stage 2, BS-1.4 and BS-1.5.
Project root: /Users/okgoogle13/Projects/Career Brain
</system_context>

<objective>
Build two Cover Letter Golden Master Google Docs and register their doc IDs.
</objective>

<execution_instructions>
1. Confirm user approval before each build (Gate 4 per AGENTS.md).
2. Build Government variant:
   python3 tools/build_golden_master.py templates/cover_letter_government_v1.json
   - Note the returned doc_id.
3. Run audit:
   python3 tools/audit_doc_style.py --doc-id <returned_doc_id>
   - Must return STYLE OK.
4. Register the doc_id in config/doc_templates.json under:
   cover_letter.variants.government.template_doc_id
5. Build NFP variant:
   python3 tools/build_golden_master.py templates/cover_letter_nfp_v1.json
   - Note the returned doc_id.
6. Run audit:
   python3 tools/audit_doc_style.py --doc-id <returned_doc_id>
   - Must return STYLE OK.
7. Register the doc_id in config/doc_templates.json under:
   cover_letter.variants.nfp.template_doc_id
</execution_instructions>

<verification_criteria>
- Both audit_doc_style.py runs return STYLE OK.
- Both doc IDs written to config/doc_templates.json.
- Dry-run still exits 0 after the config update.
</verification_criteria>
</cover_letter_golden_master_prompt>
```

---

### Prompt F: Verify KSC Golden Master (BS-1.6)
*   **Execute In:** Local Terminal using **Claude Code CLI**.

```xml
<ksc_verification_prompt>
<system_context>
You are Claude Code CLI executing TASK-006 Stage 2, BS-1.6.
The KSC Golden Master doc ID is: 1vtekKqdoK_MoavvlxD5qBg4KNkTJInnOJ2ZAALcxBes
</system_context>

<objective>
Confirm the KSC Golden Master is still valid after the premium font changes applied in Stage 1.
</objective>

<execution_instructions>
1. Run:
   python3 tools/audit_doc_style.py --doc-id 1vtekKqdoK_MoavvlxD5qBg4KNkTJInnOJ2ZAALcxBes
2. If STYLE OK → BS-1.6 is done. Log result in TASKS.md.
3. If any FAIL → report the specific failures before taking any action.
   Do NOT attempt automatic fixes without user review.
</execution_instructions>

<verification_criteria>
- audit_doc_style.py returns STYLE OK for the KSC doc.
</verification_criteria>
</ksc_verification_prompt>
```

---

### Prompt G: ATS QA & Version Lock (BS-2.1, BS-2.2)
*   **Execute In:** Local Terminal or Claude Code CLI after BS-1.4 through BS-1.6 are complete.

```xml
<ats_qa_lock_prompt>
<system_context>
You are Claude Code CLI executing TASK-006 Stage 2, BS-2.1 and BS-2.2.
All Golden Master doc IDs are in config/doc_templates.json.
</system_context>

<objective>
Run ATS QA audit on all active Golden Masters and lock template versions.
</objective>

<execution_instructions>
1. For each template variant in config/doc_templates.json that has a non-empty
   template_doc_id, run:
   python3 tools/audit_doc_style.py --doc-id <template_doc_id>
   Log each result.
2. If any doc returns failures other than the known false-positive forbidden_glyphs
   issue (chars inside the forbidden_glyphs definition field), stop and report.
3. When all active docs return STYLE OK:
   - Add a "template_version_locked" timestamp field to each variant entry in
     config/doc_templates.json using today's ISO date.
   - Update TASKS.md: mark BS-2.1 and BS-2.2 complete.
</execution_instructions>

<verification_criteria>
- Zero unexpected ATS failures across all registered Golden Masters.
- config/doc_templates.json has version lock timestamps.
- All Stage 2 tasks in TASKS.md are ticked.
</verification_criteria>
</ats_qa_lock_prompt>
```
