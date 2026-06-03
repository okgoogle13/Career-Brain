# Theme Finalization — Handover Brief

**Goal:** finalize the 10 conceptual themes (`templates/theme-01…theme-10.json`, schema **v2.3**)
into shippable production themes (schema **v2.0**), starting with the audit's nominated winner,
**Copper Teal Circuit (`theme-05`)**.

## Bigger picture — this is one slice of a schema-standardisation project

The overarching goal (see `context/theme_project_description.md`) is **one canonical, validatable
JSON schema + a critique rubric** for the whole template library. The library has **two existing
halves**, and the canonical schema is their **union**:

1. **Content/structure half** — the older 300–400-line **v2.0 production templates** (`resume_*`,
   `cover_letter_*`, `ksc_*`): concrete `blocks[]`, tokens, cm margins, single-string font (the
   *what* the pipeline consumes).
2. **Design-token half** — the newer ~200-line **v2.3 themes** + `MASTER_SCHEMA_V2_3.json`:
   `visual_identity`, `bands`, `dividers`, `accent_logic` (the *how-it-looks*).

`MASTER_SCHEMA_V2_3.json` is a **filled-in theme instance, not a validatable schema** (resume-only,
no `blocks[]`, inch margins + `font_family` array) — use it as the **design-token + rubric seed**,
not the canonical schema. **Hard constraint:** Claude is design-time only; production runs on
**Google Gemini**, so all outputs must be model-agnostic. Theme finalization below is the
visual/non-overlap slice of that larger effort.

**Two tools, each doing what it does best:**

| Track | Tool | Job |
|---|---|---|
| 1 — Visualize | **Claude Desktop** | Render all 10 as comparable mockups so a human can rank them |
| 2 — Compile/build | **Claude Code (IDE)** | Compile chosen theme v2.3 → v2.0, build the Golden Master, audit, register |

Shared context for both tracks: **`context/CareerBrain_Themes_Handover_Context.xml`** (bundles the
10 theme JSONs, `THEME_SPEC_GUIDE.md`, `MASTER_SCHEMA_V2_3.json`, `audit_doc_style.py`,
`config/doc_templates.json`, the v2.0 reference templates, and the audit report). No new repomix
packs.

---

## Track 1 — Visualize (Claude Desktop)

**Inputs to give Desktop:**
- `context/CareerBrain_Themes_Handover_Context.xml`
- `context/theme_viz_render_spec.md` — render instructions
- `context/theme_viz_sample_content.md` — the fixed sample resume

**Desktop produces:** 10 single-A4-page HTML mockups (ideally one side-by-side gallery), same
sample content, each honoring its theme's palette / typography / heading style / dividers / bands.

**Desktop returns:** a ranked shortlist + per-theme palette/typography tweak notes. Likely exclude
`theme-02 midnight-blueprint` (dark-mode = ATS/print risk).

**Fidelity caveat:** mockups approximate palette + type + heading/divider treatment. The production
builder is ATS-minimal (font, sizes, colors, line spacing, heading top/left accent borders, skills
tint) — it does **not** emit dashed "circuit" rules, decorative bands, or chips. Rank on palette,
font pairing, heading style, and tone; fine decorative motifs may not survive into production.

---

## Track 2 — Compile / build / register (Claude Code)

**Intent:** make **every aesthetically strong, visually distinct** theme available as a production
option — not a single winner. Track 1 (Desktop preview) decides which qualify.

> ⚠️ **BLOCKER (verified 2026-05-31):** `build_golden_master.py` applies paragraph styling but its
> **run-level text styling does not persist** — built golden masters carry no theme font/size/color/
> bold/heading-borders, only Google's default named styles. All 6 existing registered masters are in
> this same state, and `generate_document.py` only copies + token-replaces (no styling step). **Net:
> every registered theme currently renders identically** — so registering themes is pointless until
> the styling-bake bug is fixed. Track 1 previewing is **unaffected** (Desktop renders from JSON
> tokens, not from the builder). Evidence: identical named-style defs + empty run `textStyle: {}` on
> both `theme-05` and `modern_minimalist`. Root cause not yet diagnosed.
>
> **UPDATE 2026-06-03 — diagnosed & fixed (pending live re-verify):** old code emitted
> `updateTextStyle` *before* `updateParagraphStyle(namedStyleType)`; applying the named style
> re-asserted its text formatting over the runs and wiped the overrides → `textStyle: {}`. Reordered
> so the text-style request is emitted *after* the paragraph-style request, in commit `30d00de`
> (2026-06-02), `build_golden_master.py:316-337`. **This blocker was logged 2026-05-31, before that
> fix.** Live re-verification (built doc → non-empty run `textStyle` + PDF visual proof) is being run
> this session; the success criterion is non-empty run `textStyle`, NOT a vacuous `STYLE OK`.
>
> **CONFIRMED 2026-06-03 — BLOCKER LIFTED.** Built two Golden Masters and re-fetched: **0/53
> runs with empty `textStyle`** (bug gone), `foregroundColor` 53/53. Font path proven by control
> build — Calibri `weightedFontFamily` 53/53 vs Arial 0/53. Note `weightedFontFamily`/`fontSize`
> normalize to *absent* when a run's value equals the doc default (Arial/11pt) — expected, not a
> regression. Registration of compiled themes is unblocked (still per Phase-5 Gate 4).

**Prerequisite before any registration:** fix the run-styling persistence in `build_golden_master.py`
(diagnose first — paragraph styles land at the same ranges where run styles don't), then re-verify
on a built master (run `textStyle` populated + PDF visual proof; needs a Drive export OAuth scope).

Reference block skeleton: `templates/resume_modern_minimalist_v1.json` (closest v2.0 aesthetic).

**Per kept theme (`theme-05-copper-teal-circuit` already compiled + proven as the first):**

1. **Compile v2.3 → v2.0.** New `templates/resume_copper_teal_circuit_v1.json`:
   - Copy the 8-block skeleton + 6 roles × 4 bullets from the reference.
   - `font_family` = first array element (`Arial`) in both `ats_constraints.font_family` and
     `typography.base_font`.
   - palette → named keys, full 6-digit hex: copper `#9A5A3A`, teal `#2D8A8A`, surface `#FAF8F5`,
     body `#1D1C1A`, muted `#7D6A5A`, skills tint `#E8D4C6`.
   - margins inches → cm (`0.65in ≈ 1.65cm`, `0.7in ≈ 1.78cm`).
   - headings: copper/teal accent via **one** of `border_bottom` *or* `border_left` (not both).
   - bullet glyph `-`; no `forbidden_glyphs`; set `target_sector`, `tier`, `tier_label`, `description`.
2. **Build Golden Master:** `python3 tools/build_golden_master.py templates/resume_copper_teal_circuit_v1.json`
   → prints the Doc ID. Requires Google OAuth (`credentials.json` + `token.json` in repo root; a
   stale token triggers an interactive browser refresh).
3. **Audit the built Doc** (⚠️ this script audits a *live Doc*, not the JSON — the JSON path is only
   the `--theme` comparison source):
   `python3 tools/audit_doc_style.py <DOC_ID> --theme templates/resume_copper_teal_circuit_v1.json`
   → must print `STYLE OK` / exit 0. **`STYLE OK` is necessary but NOT sufficient:** the auditor only
   flags styles that are *present*, so an unstyled doc (empty run styles) passes vacuously. It cannot
   confirm the theme actually rendered — use the PDF visual check for that.
4. **Register:** add the Doc ID under `resume.variants.copper_teal_circuit` in
   `config/doc_templates.json` with its `theme` path.
5. **Update** the library table in `templates/THEME_SPEC_GUIDE.md` and the status in `TASKS.md`.

**Gatekeeper (`AGENTS.md`):** building the Golden Master is the Phase-5 gate — present the Doc link
and wait for approval before building further themes.

---

## Handoff loop

`Code → (XML + render spec + sample content) → Desktop → (ranked shortlist) → Code (compile/build/register)`
