---
name: family-coherence-auditor
description: Use when checking that a Career Brain theme family (family_id) yields a coherent resume, cover letter and KSC pack — shared identity, complete membership, and consistent registry entries in config/doc_templates.json. Run before registering a new family or when themes are added, renamed or retired.
---

# Family Coherence Auditor

## Overview

A family is the set of resume, cover letter and KSC templates a candidate sends together. This skill checks that the set exists, shares one identity, adapts it per document, and is registered correctly.

**Read-only.** Do not add or change `family_id`, theme JSON, `config/doc_templates.json`, preview gallery files or pipeline code unless the user explicitly asks for implementation. Mark proposed groupings or rationale not stated in the files as `[inferred]`.

## When to Use

- A new family or family member is proposed
- Themes or cover-letter/KSC templates are added, renamed or retired
- Before `output-quality-gate` scores Family coherence

Not for: single-theme distinctiveness (`theme-divergence-auditor`), live doc checks (`docs-style-auditor-v3`).

## Inputs

| Input | Required | Notes |
|---|---|---|
| `family_id`, theme paths, or `all` | Yes | |
| `config/doc_templates.json` | Yes | Registry; read the relevant `resume`, `cover_letter`, `ksc` keys |
| Member templates | Yes | `templates/resume_*`, `cover_letter_*`, `ksc_*` |

**Current state (verified 2026-11-06 — re-check, do not trust):** no template contains `family_id`; registry has 21 resume variants, 3 cover-letter variants (`government`, `nfp`, `private`) plus a base, and one KSC template (`ksc_standard_v2.json`) with no variants. If `family_id` is still absent, report it as the first finding and continue with `[inferred]` groupings.

## Shared ATS Constraints (non-negotiable)

Defined once in `output-quality-gate` → ATS spec checks (one column, canonical font, `-` bullets, white/near-white background, WCAG AA contrast, required blocks unchanged). A member that fails any of them fails the family.

## Family ID Rules

- Lowercase `snake_case`; semantic sector/strategy name (`state_gov_panel`), never visual (`teal_wave`)
- Exactly one `family_id` per family; identical string in resume, cover letter and KSC JSON
- Preferred filenames: `resume_<family_id>_v1.json`, `cover_letter_<family_id>_v1.json`, `ksc_<family_id>_v1.json`
- Minor visual revision → same `family_id`, bump `v<N>`; new `family_id` only when strategy, audience or layout identity changes

Renaming existing files to the preferred pattern breaks registry `theme` paths and `compile_theme.py`'s hard-coded `resume_<suffix>_v1.json` output name. Flag non-conforming names; do not recommend a rename without listing those knock-ons.

## KSC Coverage Rule

| Family sector | KSC member |
|---|---|
| Government, public service | Required |
| Community services / NFP | Required where selection criteria are common |
| Corporate, private, technical, startup, entry-level | Optional — needs an explicit written rationale if absent |

## Workflow

1. **Collect.** `rg -n '"family_id"' templates/` and read the registry. Run `.venv/bin/python tools/theme_fingerprint.py <member paths…>` for the shared-design fields.
2. **Membership.** For each `family_id`, list resume / cover letter / KSC members. If `family_id` is absent, propose candidate groupings from `target_sector`, font and palette overlap, each tagged `[inferred]` — e.g. `cover_letter_government_v1` + `resume_contemporary_professional_v1`/`resume_hybrid_v1` + `ksc_standard_v2` (all Calibri, Forest Green, government sector).
3. **Registry.** Every member must have a registry entry whose `theme` path exists; check each `template_doc_id` against the family's registry `status`. A placeholder or empty ID (`REPLACE_WITH_DOC_ID`, `""`, `null`) is **expected and not a defect** when the family is `status: draft` (record it as `pending`); it is a defect for `status: active` families, for legacy `variants` entries, and when `status` is missing (treat as `active`). Flag registry entries pointing to missing files and templates with no registry entry (orphans). Flag the same `family_id` used for two different identities.
4. **Shared identity.** Compare members on: font pairing (`base_font`, `heading_font`), palette (primary heading/accent hues), heading treatment, density (`line_rhythm`, `margin_frame`), tone, target sector, narrative emphasis. Cover letters and KSC have no section headings (fingerprint `heading_decoration: none`), so compare heading treatment via `name_header` styling and, for KSC, `criteria_responses.visualConfig.criterion_text` against the resume's section headings.
5. **Per-document adaptation.** Resume foregrounds evidence/experience; cover letter foregrounds motivation and fit (body paragraphs readable, `line_rhythm` medium/airy); KSC foregrounds criterion-by-criterion evidence (criterion headings visually distinct from response body).
6. **KSC coverage.** Apply the rule above.

## Scoring (out of 10)

| Points | Check |
|---|---|
| 2 | `family_id` present, valid format, identical in all members |
| 2 | Resume + cover letter present; KSC present or rule-compliant rationale |
| 1 | All members registered, theme paths exist, no placeholder Doc IDs on `active` (or status-less) entries; placeholders on `draft` families are not penalised |
| 1 | Same font pairing |
| 1 | Same palette hues (accent shade may vary) |
| 1 | Same heading treatment |
| 1 | Density consistent, allowing cover letter to be airier |
| 1 | Each document adapts the identity to its job (step 5) |

**Pass:** ≥ 8 and both 2-point checks full. **Fail:** ≤ 4, or `family_id` absent, or a required KSC missing with no rationale. **Revise:** otherwise.

## Output Format

```markdown
## Family Coherence — <family_id | all>

Commands run: <exact commands + exit codes>

### Coverage matrix
| family_id | Resume | Cover letter | KSC | Registry | Doc IDs |

### Shared identity
| Element | Resume | Cover letter | KSC | Consistent? |

### Missing / orphaned
- <item>

### Registry inconsistencies
- <key>: <problem>

Coherence: N/10
Verdict: PASS / REVISE / FAIL
```

## Examples

**Fail (snapshot 2026-11-06 — re-run, do not cite as current):** `all` — no `family_id` in any template (0/2). `[inferred]` government grouping (`cover_letter_government_v1`, `resume_contemporary_professional_v1`, `ksc_standard_v2`): all Calibri, Forest Green `#2F855A`, tight rhythm, standard margins — visually coherent, but the single KSC template is also shared by community-services and NFP. Verdict FAIL regardless of total: `family_id` absent.

**Revise (hypothetical):** `family_id: state_gov_panel` present in all three; shared fonts, palette and density; but the KSC registry entry has `template_doc_id: "REPLACE_WITH_DOC_ID"` in a family marked `status: active` (registry 0; the same placeholder in a `draft` family would score 1) and KSC `criterion_text` is plain body weight in body colour, so criteria blend into responses (adaptation 0) and do not echo the resume's uppercase ruled headings (heading 0). 2+2+0+1+1+0+1+0 = 7/10 → REVISE.

**Pass (hypothetical):** `family_id: nfp_frontline` in `resume_nfp_frontline_v1.json`, `cover_letter_nfp_frontline_v1.json`, `ksc_nfp_frontline_v1.json`; all registered with real Doc IDs; Calibri/Georgia pairing, ink-gold palette and uppercase `border_bottom` headings shared; cover letter airier; KSC criteria bold in heading colour. 10/10 → PASS.

## Hard Rules

- Never write `family_id` or registry entries; propose them as text.
- Inferred groupings are always tagged `[inferred]` and never scored as a PASS.
- Do not create Google Docs.
