---
name: theme-divergence-auditor
description: Use when checking whether a Career Brain theme (existing or proposed) is meaningfully different from its nearest neighbour, before adding, revising, renaming or retiring themes in templates/. Catches near-duplicates that differ only by accent colour, font name or minor spacing.
---

# Theme Divergence Auditor

## Overview

Finds each theme's nearest neighbour and scores how different the two look in the generated document. Structural evidence comes from `tools/theme_fingerprint.py` (read-only); this skill adds judgement only for dimensions the script cannot compute. ATS compliance is not re-checked here — it stays with `validate_templates_v2.py` and `docs-style-auditor-v3`.

**Read-only.** Do not modify theme JSON, `config/doc_templates.json`, preview gallery files or pipeline code unless the user explicitly asks for implementation. Mark any claim not backed by script output or a quoted JSON field as `[inferred]`.

## When to Use

- A new theme is proposed (JSON or written spec) and needs a nearest-neighbour check
- The user asks which themes are duplicates, clichéd, or safe to retire/merge
- Before `output-quality-gate` scores Distinctiveness

Not for: live Golden Master style checks (`docs-style-auditor-v3`), HTML previews (`theme-visual-preview-v3`).

## Inputs

| Input | Required | Notes |
|---|---|---|
| Theme paths or `all` | Yes | Compiled v2.0 files: `templates/resume_*`, `cover_letter_*`, `ksc_*` |
| Proposed theme spec | No | JSON or prose; if prose, score from stated values and mark them `[inferred]` until a JSON exists |

**Which file is "visible":** score from the compiled v2.0 file — that is what the Golden Master is built from. Use the v2.3 `templates/theme-*.json` source only for intent (`visual_identity`, `theme_specific_rules`, `avoid_list`). If source and compiled disagree (`source_drift` in script output), report the drift as a finding; do not pick one silently.

## Shared ATS Constraints (non-negotiable)

Defined once in `output-quality-gate` → ATS spec checks (one column, canonical font, `-` bullets, white/near-white background, WCAG AA contrast, required blocks and `{{TOKEN}}`s unchanged). A proposal that needs any of them broken to be "distinct" fails outright — variation must come from the dimensions below.

## Workflow

1. **Fingerprint.** Run:
   ```bash
   .venv/bin/python tools/theme_fingerprint.py --all --doc-type <resume|cover_letter|ksc> --nearest
   .venv/bin/python tools/theme_fingerprint.py <theme.json> <neighbour.json>
   ```
   The first gives nearest neighbours (fewest differing structural fields, same `doc_type`); the second gives full fingerprints for the pair. For a prose proposal, build the fingerprint fields by hand from the spec and mark them `[inferred]`.
2. **Baseline compliance.** Run `.venv/bin/python tools/validate_templates_v2.py <theme.json>` (offline). Do not run the live audit — `docs-style-auditor-v3` owns it. Record its latest result as `run: STYLE OK`, `run: FAIL`, `not run`, or `n/a (no Golden Master yet)`.
3. **Cosmetic-only check.** If `cosmetic_only` is `true`, or every differing field is in `cosmetic`, the pair is a near-duplicate in the built document. Verdict cannot be better than revise/merge.
   **Compiler-loss check:** `build_golden_master.py` builds from the compiled file, and `tools/compile_theme.py` does not carry v2.3 `bands`, `dividers` or `accent_logic` into it. If both themes have v2.3 sources whose `bands.strategy`, `dividers.grammar` or `visual_identity.header_silhouette` differ, verdict is **REVISE — compiled output lost v2.3 structure** (fix the compiled spec/compiler), not MERGE or RETIRE.
4. **Score the 10 dimensions** (0–3, table below) against the nearest neighbour. If there are ties for nearest, score against each and report the worst.
5. **Cliché check.** Flag: generic names (`modern`, `minimal`, `professional`, `clean`) with no structural signature; palette-named themes (`<colour> <noun>`) whose only distinct field is colour; any `avoid_list` / `forbidden_repeats` entry from the v2.3 source that the compiled file violates.
6. **Recommend** retain / revise / merge / rename / retire, with the specific field changes that would pass.

## Dimension Scoring

Scale: **0** effectively identical · **1** cosmetic difference · **2** clear visible difference · **3** fundamentally different approach.

| # | Dimension | Evidence (fingerprint field) | Structural? |
|---|---|---|---|
| 1 | Layout strategy | `skills_fill`, `name_rule` (the builder emits no alignment, separator or skills layout; those sit under `not_emitted` and are never scored) | Yes |
| 2 | Information hierarchy | `heading_scale`, `name_scale` | Yes |
| 3 | Typography personality | `base_font`, `heading_font` (class and pairing only) | No |
| 4 | Palette temperature / register | `heading_color`, `accent_color`, `skills_fill_color` | No |
| 5 | Section ordering | `not_emitted.block_order` (builder hard-codes order; informational only) | Yes |
| 6 | Density and whitespace | `line_rhythm`, `margin_frame` | Yes |
| 7 | Heading treatment | `heading_decoration`, `heading_case` (literal heading text; `text_transform` and tracking are not emitted) | Yes |
| 8 | Target audience and seniority | `target_sector`, `description` | No |
| 9 | Sector communication style | `target_sector`, v2.3 `visual_identity.mood` | No |
| 10 | Tone and narrative emphasis | `role_headline` / `summary_section` prominence | No |

Anchors:
- **Structural dims (1, 2, 5, 6, 7):** 0 = all fields equal; 1 = only raw values in `cosmetic` differ (same bucket); 2 = one structural field differs; 3 = two or more structural fields differ.
- **Typography (3):** font-name swap within the same class (sans↔sans, serif↔serif) = max 1. Body serif↔sans = 2. 3 = body class change *and* a different heading/body pairing (e.g. serif body + sans headings vs single sans family). Heading case scores under dim 7 only — never count a field twice.
- **Palette (4):** hue swap at the same temperature = 1; warm↔cool↔neutral change = 2; 3 only if accent scope also changes visibly (e.g. accent moves from rules to fills). Palette never counts toward the structural rule.
- **Ordering (5):** resume, cover letter and KSC block orders are fixed by `THEME_SPEC_GUIDE.md`, so this scores 0 unless the spec is changed. Do not award points for reordering the spec forbids.
- **Metadata dims (8, 9, 10):** capped at 1 unless a visible field carries the difference (e.g. a different `role_headline` size/weight for seniority). Relabelling `target_sector` alone is worth at most 1.

## Pass Rules

PASS only if all three hold against the nearest neighbour:
1. ≥ 3 dimensions score 2 or higher
2. Total ≥ 7 (out of 30)
3. ≥ 1 of the 2+ dimensions is structural (1, 2, 5, 6 or 7)

Otherwise: **revise** (one or two field changes would pass), **merge** (cosmetic-only and same sector), **rename** (distinct but name implies something it is not), **retire** (cosmetic-only and a neighbour already serves the sector).

## Output Format

```markdown
## Theme Divergence — <scope>

Commands run: <exact commands + exit codes>
Baseline: validate_templates_v2.py <PASS/FAIL> · docs-style-auditor-v3 <status>

### Nearest neighbours
| Theme | Nearest | Structural distance | Cosmetic-only? |

### Pairwise scores — <theme> vs <neighbour>
| # | Dimension | Score | Evidence |
Total: N/30 · Dims ≥2: N · Structural ≥2: yes/no

### Weak or clichéd themes
- <theme>: <reason, citing field>

### Drift (v2.3 source vs compiled)
- <theme>: <field> source=<x> compiled=<y>

### Recommendations
- <theme>: <verdict> — <specific field change, e.g. "experience_section.visualConfig.heading: border_bottom → border_left; line_spacing 1.24 → 1.4">

Verdict: PASS / REVISE / MERGE / RENAME / RETIRE
```

## Examples

Examples marked *snapshot* reflect the repo on 2026-11-06 — re-run the commands; do not cite them as current status.

**Fail — compiler loss (snapshot):** `resume_graphite_ledger_v1` vs `resume_terracotta_service_v1` — `structural_distance: 0`. Both Georgia body, uppercase `border_bottom` headings, medium rhythm, narrow margins; compiled blocks differ only in colours, heading font (Arial vs Georgia) and tracking 1.3 vs 1.2pt (same bucket). Typography 1, palette 2 (neutral → warm), structural dims 0. Total ≈ 3, structural rule fails. Both have v2.3 sources with different band/divider intent → REVISE (compiled output lost v2.3 structure), not MERGE.

**Fail — near-duplicate (snapshot):** `resume_chronological_v1` vs `resume_hybrid_v1` — `cosmetic_only: true`, no v2.3 sources. Differ by body font (Times New Roman vs Calibri: serif↔sans, typography 2) and navy vs green (palette 1). Total 3, structural rule fails → RETIRE one or REVISE.

**Pass (hypothetical):** a proposed theme vs `resume_modern_minimalist_v1` with `heading_decoration` none + `heading_transform` none + strong `heading_scale` (hierarchy 3, heading 3), `line_rhythm` airy + `margin_frame` wide (density 3), serif body with tracked small-caps labels (typography 2). Total 11, four dims ≥2, structural → PASS.

## Hard Rules

- Never declare a theme distinct without fingerprint output or quoted JSON fields.
- Never run `audit_doc_style.py`; consume `docs-style-auditor-v3` output.
- Colour, font-name or within-bucket spacing changes never satisfy the structural rule.
- Do not edit files; recommendations are text unless the user asks for implementation.
