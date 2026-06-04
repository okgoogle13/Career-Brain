# Implementation Plan - Phase 3 Theme Validation & Pipeline Integration

We will build a custom standalone validator script to ensure theme JSON specifications are structurally sound, strictly valid against `MASTER_SCHEMA_V2_3.json` rules, and visually consistent. We will then verify all 5 new themes alongside the 2 reference themes, perform a compilation sanity check, and compile a quality summary.

## User Review Required

> [!IMPORTANT]
> The custom validator will enforce the exact schema constraints from `MASTER_SCHEMA_V2_3.json` and structural patterns from `theme-01-graphite-ledger.json`. Specifically:
> - Hex colors must be uppercase 6-digit hex format (e.g., `#FFFFFF`).
> - Font families must strictly use the ATS-safe whitelist: `Arial`, `Calibri`, `Georgia`.
> - Layout fields like columns must equal 1, tables/images must be disabled.
> - Key-shape consistency (exactly matching the 95 keys in `theme-01`).
> - Profile fields (e.g. `band_placement_profile`, `accent_placement_profile`, `divider_rhythm`, `accent_logic.contrast_intensity`) will be validated as scalars (strings), which aligns with the production references rather than the schema's array definitions.

## Proposed Changes

### Build Custom Theme Validator

#### [NEW] [validate_theme_spec.py](file:///Users/okgoogle13/Projects/Career%20Brain/tools/validate_theme_spec.py)
A Python utility that:
1. Loads `templates/MASTER_SCHEMA_V2_3.json` and a target theme JSON file.
2. Checks that the target theme file contains exactly the same keys and structure as the reference `templates/theme-01-graphite-ledger.json`.
3. Validates color codes against hex regex (`^#[0-9A-F]{6}$`).
4. Enforces the ATS-safe font whitelist (`Arial`, `Calibri`, `Georgia`).
5. Checks constraints from `MASTER_SCHEMA_V2_3.json` (such as `columns: 1`, no tables/images/text boxes allowed).
6. Outputs errors/warnings clearly to stdout and exits with code 1 on failures, or code 0 on success.

### Update Planning Tasks

#### [NEW] [phase3_tasks.md](file:///Users/okgoogle13/Projects/Career%20Brain/planning/phase3_tasks.md)
Tracks progress through Phase 3: script creation, validation execution, compilation check, and summary creation. (This file will be created in the project's `planning/` workspace folder).

#### [DELETE] [phase2_tasks.md](file:///Users/okgoogle13/Projects/Career%20Brain/planning/phase2_tasks.md)
We will remove the completed Phase 2 tasks sheet to clean up the workspace context.

### Verification and Compilation Test

We will run the pipeline's compilation step using `python3 pipeline/compile_brain.py` to ensure it runs cleanly with the new themes.

#### [NEW] [QUALITY_SUMMARY.md](file:///Users/okgoogle13/Projects/Career%20Brain/planning/QUALITY_SUMMARY.md)
A summary report documenting:
1. Validator checks executed and their outcomes.
2. Parity, contrast compliance, font compliance, and metadata verification status.
3. Pipeline integration test output.

## Verification Plan

### Automated Tests
- Test execution of the new script:
  ```bash
  python3 tools/validate_theme_spec.py templates/theme-01-graphite-ledger.json
  python3 tools/validate_theme_spec.py templates/theme-02-midnight-blueprint.json
  python3 tools/validate_theme_spec.py templates/theme-21-terminal-signal.json
  python3 tools/validate_theme_spec.py templates/theme-22-horizon-edge.json
  python3 tools/validate_theme_spec.py templates/theme-23-broadside-press.json
  python3 tools/validate_theme_spec.py templates/theme-24-clay-canvas.json
  python3 tools/validate_theme_spec.py templates/theme-25-cyan-blueprint.json
  ```
- Pipeline check:
  ```bash
  python3 pipeline/compile_brain.py
  ```
