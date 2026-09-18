# Address Copilot PR Review Gaps

This plan addresses the gaps identified in Copilot's PR review for the `claude/themes-21-25-phase3` branch. We will execute the "quick wins" immediately and defer the larger refactors to the project planning document.

## User Review Required

Please review the proposed changes and confirm if the approach to fixing the `verify_themes_2125.py` script and the adjacent-theme rule makes sense. Once approved, I will implement the quick wins and update the planning docs.

## Proposed Changes

### Verification Script (Quick Win)

We need to make the script actually perform the checks that the documentation claims it does, and fail the CI if unexpected deviations are found.

#### [MODIFY] [verify_themes_2125.py](file:///Users/okgoogle13/Projects/Career Brain/scratch/verify_themes_2125.py)
- **Add Structural Checks:** I will add logic to load `theme-01-graphite-ledger.json` and recursively compare its keys against themes 21-25 to ensure exact key parity.
- **Add Hex & Font Checks:** I will add regex validation for 6-digit uppercase hex codes (`^#[0-9A-F]{6}$`) and verify that `base_font` is strictly one of `Arial`, `Calibri`, or `Georgia`.
- **Fail on Deviation:** I will modify the script to `sys.exit(1)` if `total_dev != 16` (the known allowlisted deviations) or if any of the new structural checks fail. 

### Theme Rule Conflict (Quick Win)

Themes 24 and 25 currently both use `alternating` for `divider_rhythm`, violating the `CLAUDE.md` rule against adjacent theme duplication.

#### [MODIFY] [theme-25-cyan-blueprint.json](file:///Users/okgoogle13/Projects/Career Brain/templates/theme-25-cyan-blueprint.json)
- Change `dividers.divider_rhythm` from `"alternating"` to `"regular"` to resolve the conflict while keeping the structural blueprint aesthetic intact.

### Planning Docs (Deferred Tasks)

The low-priority polish items (redundancy in the script and wording normalization) are better executed as a separate chore later. 

#### [MODIFY] [claude-plan.md](file:///Users/okgoogle13/Projects/Career Brain/planning/claude-plan.md)
- Add a new "Tech Debt / Refactoring" section.
- Add Task: Refactor `verify_themes_2125.py` to load the spec map from a structured JSON/YAML fixture instead of hardcoding it.
- Add Task: Standardize terminology across themes (e.g., "section headers" vs "section headings").

## Verification Plan

### Automated Tests
- Run `python3 scratch/verify_themes_2125.py`. It should print out the structural check successes and exit `0` (since we expect exactly 16 deviations).
- Intentionally break a hex code or key to verify it exits `1`.
