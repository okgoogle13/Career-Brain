# Claude Code Execution Prompt: Theme Synthesis

Copy and paste the following XML-structured prompt into your Claude Code terminal. This prompt is heavily optimized for Claude 3.5 Sonnet (Opus/Sonnet architecture) and strictly enforces the separation of tasks and phases.

```xml
<system_context>
You are an expert AI software engineer and design synthesist operating via the Claude Code CLI. You are executing a highly structured, multi-phase ETL and design pipeline for the "Career Brain" project.
</system_context>

<deep_plan_context>
The full context, constraints, and step-by-step execution details are located in two specific documents. 
You must read these documents completely before taking any action:
1. `planning/claude-research.md` (Contains constraints, ATS requirements, and external PDF analysis)
2. `planning/claude-plan.md` (Contains the detailed 3-Phase execution plan and success criteria)
</deep_plan_context>

<operating_rules>
1. **Strict Phase Segregation:** You MUST execute the plan in distinct, isolated phases. You are forbidden from starting Phase N+1 until Phase N is 100% complete, verified, and documented.
2. **State Management via tasks.md:** You MUST create and actively maintain a `tasks.md` file in the root directory. This file will serve as your granular state tracker and checklist.
3. **No Hallucination:** Read the actual schema and reference files. Do not infer structure from memory.
4. **Verification-First:** Do not assume a script or generation worked. Run the required checks (e.g., regex for hex codes, Python validators) before checking off a task.
</operating_rules>

<execution_pipeline>
<phase name="Phase 0: Initialization & Task Segregation">
<objective>Internalize the deep plan and initialize state tracking.</objective>
<steps>
  1. Read `planning/claude-research.md`.
  2. Read `planning/claude-plan.md`.
  3. Create `tasks.md` in the root directory. Extract the steps from `claude-plan.md` into a granular, checkable markdown checklist (`- [ ]`). Group the checklist strictly by Phase 1, Phase 2, and Phase 3.
  4. Ensure `tasks.md` includes verification sub-steps (e.g., verifying hex codes, ATS constraints).
</steps>
<gate>Do NOT proceed to Phase 1 until `tasks.md` is written and you have verified its contents.</gate>
</phase>

<phase name="Phase 1: Design Synthesis">
<objective>Generate pure text specifications without jumping ahead to JSON.</objective>
<steps>
  1. Execute the synthesis steps exactly as described in Phase 1 of `claude-plan.md`.
  2. Produce the required markdown output: `planning/phase1-design-synthesis.md`.
  3. Verify that the concepts differ from the existing 10 themes on ≥3 dimensions.
  4. Update `tasks.md` to mark all Phase 1 items as complete (`- [x]`).
</steps>
<gate>Do NOT write any JSON files during this phase. Wait until `tasks.md` is updated before moving to Phase 2.</gate>
</phase>

<phase name="Phase 2: Schema Extraction & JSON Generation">
<objective>Translate the text specifications into valid v2.3 JSON theme files.</objective>
<steps>
  1. Read the newly created `planning/phase1-design-synthesis.md`.
  2. Generate the 3 JSON files in the `templates/` directory.
  3. Validate hex codes (uppercase, 6-digit) and ATS compliance (single-column, correct fonts, etc.).
  4. Update `tasks.md` to mark Phase 2 items as complete (`- [x]`).
</steps>
<gate>Ensure the JSON files strictly adhere to `templates/MASTER_SCHEMA_V2_3.json`. Do not proceed until verified.</gate>
</phase>

<phase name="Phase 3: Validation & Testing">
<objective>Run integration tests and finalize the pipeline.</objective>
<steps>
  1. Run `python3 tools/validate_template_spec.py` on all 3 new JSON themes.
  2. Generate the `planning/QUALITY_SUMMARY.md` report as specified in the plan.
  3. Update `tasks.md` to reflect 100% project completion.
</steps>
</phase>
</execution_pipeline>

<initial_directive>
Begin immediately with Phase 0. Acknowledge these instructions, read the two planning documents, and create the `tasks.md` file. Wait for my confirmation, or proceed methodically through the pipeline while heavily logging your progress to `tasks.md`.
</initial_directive>
```
