---
name: theme-gate
description: Use as the pass/fail checkpoint for a Career Brain theme family before building its Golden Masters (Stage A) or registering them in config/doc_templates.json (Stage B). Prints PASS or the failing lines; also holds the theme and KSC run order.
---

# Theme Gate

Pass/fail only. Every line below is checked from command output or a quoted JSON field; a line without that evidence fails. Do not edit files, create Docs or call Google from this skill.

Rule sources (one copy each): S1–S6 → `templates/THEME_SPEC_GUIDE.md` "Design Standard"; brief fields, `family_id` rules, KSC coverage → `templates/THEME_BRIEF_FORM.md`; forbidden characters → `config/ats_rules.json`; fonts, columns, `allows_*` → `templates/schema_v2_0.json`.

## Stage A — before building (offline)

Run for each member (resume, cover letter, KSC) of `<family_id>`:

```bash
.venv/bin/python tools/validate_templates_v2.py <member.json>
.venv/bin/python tools/theme_fingerprint.py <member.json>
.venv/bin/python tools/theme_fingerprint.py --all --doc-type resume --nearest
```

| # | Line | Pass when |
|---|---|---|
| A1 | Schema | `validate_templates_v2.py` PASS for every member |
| A2 | Contrast | `contrast_failures` empty for every member |
| A3 | Design standard | S1, S2, S3, S4 PASS per member, evidence in the brief's `STANDARD_CHECK` |
| A4 | Distinct | the family's resume vs its nearest resume: `structural_distance ≥ 2` and `cosmetic_only: false` |
| A5 | Brief | every `THEME_BRIEF_FORM.md` field filled (or "absent" with a reason); DECISIONS has ≥ 2 emitted-field links |
| A6 | Family | identical `family_id` in all members; S6 equal across members |
| A7 | Preview | the user has ranked the family in `theme-visual-preview-v3` |
| A8 | ATS glyphs | every bullet `glyph == "-"`; no forbidden character anywhere in the file; `page.background_color` white or near-white (each channel ≥ `F0`, max − min ≤ 16) |

## Stage B — before registering

All Stage A lines, plus:

| # | Line | Pass when |
|---|---|---|
| B1 | Live style | `docs-style-auditor-v3` reports `STYLE OK` for every member's Golden Master, audited with `--theme` |
| B2 | Page fit | S5 checked on the rendered Doc |
| B3 | Registry | each member has a real Doc ID (no `REPLACE_WITH_DOC_ID`, `""` or `null`) |

The gate never runs the live audit; `docs-style-auditor-v3` owns it and asks before calling Google.

## Output

```
Theme Gate — <family_id> · Stage <A|B>
Commands: <command → exit code / key line>, one per line
PASS
```
or `FAIL` followed by one line per failing check: `<#> <member>: <evidence>`.

## Run order

Theme family (resume, cover letter, KSC):
1. Fill `templates/THEME_BRIEF_FORM.md`.
2. Write the member JSONs from the brief.
3. `theme-visual-preview-v3` → user ranks (A7).
4. `theme-gate` Stage A → PASS.
5. `tools/build_golden_master.py <member.json> --dry-run`, then the live build (Google write: approve once per batch).
6. `docs-style-auditor-v3` → `STYLE OK` per member.
7. `theme-gate` Stage B → PASS.
8. Register the Doc IDs in `config/doc_templates.json` under `<type>.variants.<family_id>`.

Code changes: `peer-review` before any `--write` run or commit touching `pipeline/` or `tools/`.

## Rules

- Start at the first step whose exit criterion is not met; re-run a step only if a member JSON changed since.
- Never report a line passed without its command output.
