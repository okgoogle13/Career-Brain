---
name: theme-purpose-interrogator
description: Use when a Career Brain theme is proposed or under review and you need to test whether it has a real user, application context, reader focus and story — or is just a colour variation. Run before building a Golden Master or approving a new theme family.
---

# Theme Purpose Interrogator

## Overview

Forces every theme to answer *who is this for and why does it look like this*. A theme passes only if its design decisions follow from a specific purpose that no existing theme already serves.

**Read-only.** Do not modify theme JSON, `config/doc_templates.json`, preview gallery files or pipeline code unless the user explicitly asks for implementation. Mark any rationale you supply that is not stated in the theme files or by the user as `[inferred]`. Never invent intent to fill a gap — absent rationale is a finding.

## When to Use

- A new theme or family is proposed
- An existing theme has no clear reason to exist (often flagged by `theme-divergence-auditor`)
- Before `output-quality-gate` scores Purpose clarity

Not for: visual near-duplicate detection (`theme-divergence-auditor`), live doc style checks (`docs-style-auditor-v3`).

## Inputs

| Input | Required | Notes |
|---|---|---|
| Theme JSON path or proposed spec | Yes | Compiled v2.0 file. The v2.3 `templates/theme-NN-<name>.json` source is optional: read it only if it still exists in `templates/` or an archive folder; it may be archived or retired |
| Target sector, seniority, application context | No | If the user supplies them, they override metadata; quote them |

**Rationale sources, in order:** user statement → family definition if the theme belongs to a family (`family_id`, `target_sector`, `seniority`, `tone`, KSC rationale, reader focus and story as written in the family proposal or registry; quote it) → v2.3 `visual_identity`, `theme_specific_rules`, `avoid_list` when a source file exists → compiled `description`, `target_sector`, `tier_label`. A missing v2.3 source is not a finding for a hand-authored family theme; score from the sources above. Resumes without a v2.3 source (`professional_classic`, `chronological`, `hybrid`, `contemporary_professional`, `modern_minimalist`, `warm_impact`) have only `description` and `target_sector`; record "rationale absent" for questions those fields cannot answer.

## Shared ATS Constraints (non-negotiable)

Defined once in `output-quality-gate` → ATS spec checks (one column, canonical font, `-` bullets, white/near-white background, WCAG AA contrast, required blocks and placeholders unchanged). A purpose that requires breaking any of these (e.g. "creative sidebar") is rejected — redirect it to a permitted dimension.

## Workflow

1. **Extract** metadata, palette, typography, page, block order (`.venv/bin/python tools/theme_fingerprint.py <theme.json>` gives a compact summary; read the v2.3 source's `visual_identity` and `theme_specific_rules` with a bounded `rg -n` when the source exists; otherwise use the family definition).
2. **Answer the nine questions** from the sources. Quote the field that answers each; if nothing does, write "absent".

   | # | Question | A specific answer looks like |
   |---|---|---|
   | Q1 | Who is this for? | "mid-career community-services practitioners moving into team-leader roles" — not "professionals" |
   | Q2 | What application context? | "state government roles with selection criteria", "agency-recruited tech contracts" |
   | Q3 | What should a recruiter notice first? | one element: role headline, metrics in bullets, credentials |
   | Q4 | What story does it tell? | "steady, accountable progression" — must not fit every theme |
   | Q5 | What evidence is foregrounded? | named block or field |
   | Q6 | What is de-emphasised? | named block or field |
   | Q7 | Why not an existing theme? | names the nearest theme and the user/story gap |
   | Q8 | Why not just a colour variation? | quotes the `theme-divergence-auditor` result: `cosmetic_only: false` and the `structural_diffs` vs nearest. Do not re-derive it; if divergence has not run, run it first. `cosmetic_only: true` → 0 |
   | Q9 | Which design decisions express the purpose? | ≥ 2 field→purpose links, e.g. `heading_scale: strong` → "scannable for panel shortlisting" |

3. **Duplicate-purpose check.** Compare Q1/Q2/Q4 against every theme with an overlapping `target_sector` (see the library table in `templates/THEME_SPEC_GUIDE.md`). Same user + same story = duplicate, regardless of palette.
4. **Rationale quality.** Flag answers that are:
   - **Vague** — adjectives only ("modern", "clean", "impactful", "bold")
   - **Circular** — restates the design ("for people who want a terracotta look")
   - **Unsupported** — claim with no matching field (e.g. "compact for senior roles" but `line_rhythm: airy`)
5. **Write the identity statement:** `For <Q1> applying to <Q2>, <theme> foregrounds <Q5> through <Q9 decision>, so a recruiter first sees <Q3>.`

## Scoring

Each question 0–2: **0** absent/generic · **1** stated but vague or unsupported · **2** specific and backed by a field or user statement. Max 18.

**Reject** if any of:
- Q1 scores 0 (target user too broad or absent)
- Q3 scores 0 (reader focus generic)
- Q4 story could apply to any theme in the same sector
- Q9 < 2 (design does not follow from purpose)
- Duplicate-purpose check finds an existing theme with the same user and story

**Pass** if not rejected, total ≥ 14, and Q7, Q8, Q9 each score 2.
**Revise** otherwise.

## Output Format

```markdown
## Theme Purpose — <theme>

Sources read: <files + fields>
Commands run: <exact commands + exit codes>

**Identity:** <one sentence>

### Purpose scorecard
| # | Question | Answer (quoted / absent / [inferred]) | Score |
Total: N/18

### Design-to-purpose alignment
| Design decision (field = value) | Purpose it serves | Aligned? |

### Weak rationale
- Q<n>: <vague / circular / unsupported> — <why>

### Duplicate purpose
- <theme> serves <same user/story> — or "none found"

### Required revisions
- <specific change to metadata or design field>

Verdict: PASS / REVISE / REJECT
```

## Examples

**Reject — circular, duplicate:** `resume_chronological_v1`. No v2.3 source; `target_sector` overlaps `resume_professional_classic_v1` (finance, law, corporate); same font family and palette. Q4 absent, Q7 absent, Q8 absent (fingerprint distance to `professional_classic` is 1, contact separator only). → REJECT as separate theme; keep one.

**Reject — too broad (hypothetical):** "Bold, modern theme for ambitious professionals in any sector." Q1 0 ("ambitious professionals"), Q4 vague. → REJECT; if the user narrows it to "grad-entry data analysts, metrics-first", re-score.

**Revise — unsupported (hypothetical):** "Compact, information-dense layout for senior executives", but the fingerprint shows `line_rhythm: airy`, `margin_frame: wide`. Q9 = 1 (claim contradicts fields). → REVISE: tighten line spacing/margins or change the stated purpose.

**Pass (hypothetical):** "For frontline community workers applying to state government case-management roles, foregrounds practice-framework skills via a filled skills block, airy line rhythm for panel reading, sans body with tracked uppercase labels; de-emphasises education." Q7 names `contemporary_professional` as nearest and the gap as case-management panels; Q8 cites `skills_fill`, `line_rhythm: airy`. Total 16, Q7–Q9 = 2 → PASS.

## Hard Rules

- Never fabricate a target user or story; "absent" is a valid answer and costs points.
- Purpose must be expressible within the shared ATS constraints.
- Do not edit files; required revisions are text unless the user asks for implementation.
