# Career Brain — Template Schema & Critique (Design-Time)

> Canonical Project description / custom instructions. Mirrors the Claude Desktop Project context so
> the repo and the design workspace stay in sync.

**What this is:** Career Brain is a career-justice tool for community-services and social-work
contexts in Australia. This is the **design-time workspace** for standardising its resume /
cover-letter / KSC and theme templates.

**Goal:** Produce (a) **one canonical, validatable JSON schema** that unifies a mixed library into a
single format, and (b) a **critique rubric** for evaluating any template on: clarity, non-overlap
(themes must be visually/structurally distinct), accessibility, ATS-safety, and alignment with
Career Brain's career-justice aims.

## The library has two existing halves — the canonical schema is their union

1. **Content/structure half** — the older 300–400-line **v2.0 production templates** (`resume_*`,
   `cover_letter_*`, `ksc_*`). These hold the concrete `blocks[]`, tokens (`{{ROLE_N_…}}`, etc.),
   cm margins, and single-string fonts the production pipeline actually consumes. This is the *what*.
2. **Design-token half** — the newer ~200-line **v2.3 themes** (`theme-01…10`) plus
   `MASTER_SCHEMA_V2_3.json`. These hold `visual_identity`, `bands`, `dividers`, `accent_logic` —
   the *how-it-looks*.

## Status of `MASTER_SCHEMA_V2_3.json` (important)

Despite its name it is a **filled-in theme instance, not a validatable schema** (no
`$schema`/`properties`/`required`), it is **resume-only**, has **no `blocks[]`**, and uses inch
margins + a `font_family` array (production-incompatible). Treat it as: (a) the **seed for the
design-token vocabulary**, and (b) a **rubric goldmine** — lift `theme_specific_rules`,
`anti_generic_rules`, `forbidden_repeats`, `adjacent_theme_difference_rules`, and `avoid_list` as
the non-overlap/clarity/accessibility criteria. Do **not** treat it as the canonical schema.

## The canonical schema must

- Merge both halves.
- Cover all three `doc_type`s (resume, cover_letter, ksc).
- Normalise to one convention set (cm margins, single-string font).
- Express the design tokens **and** the `blocks`/token contract.
- Be an **actual validatable schema** so faster models can validate normalised output in Phase 2.

## Hard constraint — model-agnostic outputs

Claude is **design-time only**. Production runs on **Google Gemini**, not Anthropic APIs. Every
artifact (schema, rubric, normalised themes, critique objects) must be plain, portable JSON/markdown
reusable as Gemini system/context — no Anthropic-specific SDKs, tools, or assumptions.

## Phased plan (multi-session)

1. **Schema + rubric design** (Opus 4.8) — synthesise the canonical schema from both halves; draft
   the rubric seeded from `MASTER_SCHEMA_V2_3`'s rule blocks; validate against a few representative
   old + new templates.
2. **Bulk normalisation + critique** (faster models) — convert the full library to the canonical
   schema; emit one critique object per template against the rubric.
3. **Final audit** (Opus 4.8) — refine the ontology, resolve overlaps, tidy repo structure.

## Working principles

Smallest change that works; verify against the actual files, don't infer; surface tradeoffs and
ambiguity explicitly; keep outputs human-readable and reusable. ATS-safety and accessibility are
non-negotiable evaluation axes.
