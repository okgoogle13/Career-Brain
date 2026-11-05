---
name: output-quality-gate
description: Use as the final approval checkpoint for a Career Brain theme or theme family before building a Golden Master or registering it — combines theme-divergence-auditor, theme-purpose-interrogator, family-coherence-auditor and ATS validation into one scorecard and an approve / revise / reject verdict.
---

# Output Quality Gate

## Overview

One verdict from four inputs. The gate does not re-derive what the other skills produce; it consumes their outputs (or runs them), adds the design-quality dimensions they don't cover, and applies fixed approval rules.

**Read-only.** Do not modify theme JSON, `config/doc_templates.json`, preview gallery files or pipeline code, and do not create Google Docs, unless the user explicitly asks for implementation. Mark any score not backed by command output, a sub-skill result or a quoted JSON field as `[inferred]`. Never report a validation as passed unless the command was run in this session and its output checked.

## When to Use

- "Is this theme/family ready?" — before a Golden Master build (Stage A) or registry entry (Stage B)
- After revisions requested by an earlier gate run

Not for: a single sub-check — use the specific skill.

## Inputs

| Input | Required | Notes |
|---|---|---|
| Theme path(s) or `family_id` | Yes | |
| Sub-skill outputs | No | If missing or stale (theme JSON changed since), run the skill |
| `docs-style-auditor-v3` result | Stage B only | `STYLE OK` from the live Golden Master, audited with `--theme` |

## Two Stages

| Stage | Question | ATS evidence required |
|---|---|---|
| **A — Build** | Is this spec good enough to build a Golden Master from? | Offline only: `validate_templates_v2.py` PASS + spec checks below |
| **B — Register** | Is the built Golden Master ready for `doc_templates.json`? | Stage A evidence **plus** `docs-style-auditor-v3` → `STYLE OK` |

The gate never runs the live audit itself — `docs-style-auditor-v3` owns it. If no result exists at Stage B, run that skill (it asks before calling the Google Docs API) or use output the user pastes. A proposal has no Doc, so the live audit is "n/a" at Stage A — never "passed".

## Workflow

1. **Run or consume, in order:**
   ```bash
   .venv/bin/python tools/validate_templates_v2.py <theme.json>
   .venv/bin/python tools/theme_fingerprint.py --all --doc-type <type> --nearest
   .venv/bin/python tools/theme_fingerprint.py <theme.json>
   ```
   Then apply `theme-divergence-auditor`, `theme-purpose-interrogator`, `family-coherence-auditor` (in that order). Stage B: consume the `docs-style-auditor-v3` result.
2. **ATS spec checks** — the single list of shared ATS constraints; the other theme skills point here. One column, every `allows_*` false and font in the canonical enum are schema constants, so a `validate_templates_v2.py` PASS covers them. Check the rest from the theme JSON / fingerprint: every bullet `glyph == "-"`; no character from `config/ats_rules.json` `forbidden_characters` / `forbidden_char_ranges` anywhere; `page.background_color` white or near-white (every RGB channel ≥ `F0` hex and max − min channel ≤ 16 — e.g. `#FFFFFF`, `#FAFAFA`, `#FAF8F5` pass; `#EEEEEE` and `#FFF5E0` fail; contrast is still judged by `contrast_failures` against the actual background); `contrast_failures` empty; required blocks and `{{TOKEN}}`s present per `THEME_SPEC_GUIDE.md`.
3. **Score** the 10 dimensions below.
4. **Classify issues** as blocking (high severity) or non-blocking.
5. **List required changes** as exact JSON paths / registry keys and target values.
6. **Verdict.**

## Scorecard (each 0–10)

| Dimension | Source | Rule |
|---|---|---|
| Distinctiveness | divergence total `T` (/30) | `min(10, T)` if divergence PASS, else `min(5, T)` |
| Purpose clarity | purpose total `P` (/18) minus Q8 | `round((P − Q8) / 1.6)`; REJECT verdict caps at 4. Q8 (colour variation) is the divergence result, already scored under Distinctiveness |
| Visual hierarchy | `heading_scale`, `name_scale`, role-title vs body sizes | 10 = three clearly distinct levels (name > section > role > body); −3 per collapsed level |
| Typography quality | fonts, sizes, tracking | 10 = body 10–12pt, heading/body pairing intentional, ≤ 2 families; −2 per issue |
| Palette quality | colours, accent scope | 10 = one accent role, temperature fits purpose; −3 per issue. Contrast is scored under ATS safety only |
| Family coherence | family score `F` (/10) | `F`; for a single theme with no family yet, score 0 and state why |
| Scanning rhythm | `line_rhythm`, `margin_frame`, `spacing_after_pt`, role spacing | 10 = consistent vertical rhythm, role blocks separable at a glance; −2 per inconsistency |
| ATS safety | step 2 + audit | 10 only if every step-2 check passes **and** (Stage A) `validate_templates_v2.py` PASS or (Stage B) also `STYLE OK`; otherwise 0–9 by count of failures |
| Implementation readiness | schema, registry, drift | 10 = schema PASS, no v2.3→compiled `source_drift`, registry entry real (Stage B); −2 per gap |
| Professional credibility | purpose + sector norms | 10 = a recruiter in the stated sector would read it as standard-plus; −3 for novelty that reads as gimmick (e.g. high-chroma role headline) |

**Overall** = mean of the 10, one decimal.

## Severity

**High (blocking):** any ATS check failure; Stage B without `STYLE OK`; divergence not PASS (incl. cosmetic-only nearest neighbour); purpose REJECT; `family_id` missing or inconsistent across members; required KSC missing without rationale; placeholder Doc ID at Stage B; `source_drift` that crosses a fingerprint bucket.

**Non-blocking:** purpose REVISE items, single-point scoring deductions, naming that doesn't follow `<doc_type>_<family_id>_v<N>`, drift within one bucket.

## Approval Rules

APPROVE only if **all**:
- ATS safety = 10
- Distinctiveness ≥ 8 (so divergence total ≥ 8 — passing divergence at 7 is necessary, not sufficient)
- Overall ≥ 8.0
- No unresolved high-severity issue
- Nearest-neighbour three-dimension rule met
- Family coverage complete, or absence explicitly justified per the KSC coverage rule

REJECT if purpose is REJECT, or the theme is cosmetic-only against its nearest neighbour with no viable revision. Otherwise REVISE.

## Output Format

```markdown
## Quality Gate — <theme | family> · Stage <A|B>

Commands run: <exact command → exit code / key line>
Sub-skills: divergence <verdict, T/30> · purpose <verdict, P/18> · family <verdict, F/10>

| Dimension | Score | Evidence |
|---|---|---|
| … | | |
Overall: N.N/10

### Blocking issues
1. <issue> — <evidence>

### Non-blocking improvements
- <issue>

### Required JSON / registry changes
- `<file>`: `<json.path>` <current> → <target>

Verdict: APPROVE (Stage A|B) / REVISE / REJECT
```

## Examples

*Snapshot examples reflect the repo on 2026-11-06 — re-run the commands; do not cite them as current status.*

**Revise — blocked (snapshot):** `resume_emerald_transit_v1` — fingerprint `cosmetic_only: true` against 10 other themes (distinctiveness ≤ 5); `contrast_failures` include `#22C55E` at 2.28:1 (ATS safety < 10); no `family_id`. Its v2.3 source carries band/divider intent the compiled file lost, so there is a structure to revise toward → REVISE, not REJECT.

**Revise (hypothetical):** a proposed family scores distinctiveness 9, purpose 8, family 8, ATS 10 at Stage A, overall 8.3, but the KSC member is missing for a government family with no rationale → one blocking issue → REVISE.

**Approve Stage A (hypothetical):** divergence PASS with T = 10, purpose PASS 16/18, family 10/10, all ATS spec checks pass and `validate_templates_v2.py` PASS, overall 8.6, no blocking issues → APPROVE (Stage A). Stage B still requires the live `STYLE OK`.

## Hard Rules

- Never APPROVE on inferred ATS evidence.
- Never run `audit_doc_style.py` directly; Stage B evidence comes from `docs-style-auditor-v3`.
- Score each defect in one dimension only; blocking status is separate from the score.
- Report commands exactly as run, with results.
- Do not edit files or create Docs; required changes are text unless the user asks for implementation.
