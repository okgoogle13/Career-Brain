# QUALITY SUMMARY — Themes 21–25 (Phase 2 + Phase 3)

**Date:** 2026-06-03
**Scope:** 5 new v2.3 resume themes generated from the text design specs in
`claude_code_final_phases_prompt.md` (Concepts 1–5).
**Source spec:** `planning/phase1-design-synthesis.md` · **Phase-2 build notes:** `planning/phase2_tasks.md`
**Verification script (re-runnable):** `scratch/verify_themes_2125.py`

| # | File | Theme | Status |
|---|------|-------|--------|
| 21 | `templates/theme-21-terminal-signal.json` | Terminal Signal | ✅ PASS |
| 22 | `templates/theme-22-horizon-edge.json` | Horizon Edge | ✅ PASS |
| 23 | `templates/theme-23-broadside-press.json` | Broadside Press | ✅ PASS |
| 24 | `templates/theme-24-clay-canvas.json` | Clay Canvas | ✅ PASS |
| 25 | `templates/theme-25-cyan-blueprint.json` | Cyan Blueprint | ✅ PASS |

---

## 1. Executive summary

All 5 themes are **structurally schema-conformant and ATS-safe**. A complete
field-by-field diff against the literal text spec found **20 deviations**; of these:

- **4 were build errors** (heading sizes/weight silently flattened) → **corrected to spec** this phase.
- **16 are intentional** (ATS-font swaps, schema-mandated intensity caps, accessibility
  accent darkening, enum normalization, and semantically-equivalent wording) → **retained and documented below.**

No structural validation failures remain. No live Golden Master was built (gated — see §7).

---

## 2. Validation methodology (important correction)

> ⚠️ The execution prompt named `python3 tools/validate_template_spec.py <theme>.json`
> as the validate step. **That tool cannot validate theme JSON.** It is a hard-gate for
> **KSC Markdown specs** (`## META / ## STRUCTURE / {{KSC_CRITERION_N}}` tokens) and
> exits 1 on the reference `theme-01-graphite-ledger.json` itself. No `.py` in the repo
> imports `jsonschema` or references `MASTER_SCHEMA_V2_3` / any theme-JSON field — there
> is **no automated structural validator** for v2.3 themes. `tools/audit_doc_style.py`
> only audits a *live Google Doc* via `--theme`; it is not a standalone JSON check.

**Corrected verification used here** (`scratch/verify_themes_2125.py`):

1. JSON parses cleanly (all 5).
2. Key-shape parity vs `theme-01` reference — **95 keys, 0 missing, 0 extra**.
3. All hex codes **6-digit uppercase** (`^#[0-9A-F]{6}$`).
4. `base_font` ∈ ATS whitelist `{Arial, Calibri, Georgia}` **and** first in `font_family`.
5. Profile fields (`band_placement_profile`, `accent_placement_profile`,
   `divider_rhythm`, `accent_logic.contrast_intensity`) are scalars (per theme-01/02 convention, not the enum arrays in the master schema).
6. Full field-by-field diff of every `→ maps to X.Y`-annotated spec value vs the JSON.
7. Adjacency non-duplication (CLAUDE.md) + band-height sanity.

---

## 3. Structural validation — all PASS

| Theme | Keys | Parity vs theme-01 | Hex 6-digit upper | `base_font` (ATS) | Heading |
|-------|------|--------------------|-------------------|-------------------|---------|
| 21 Terminal Signal | 95 | OK | OK | Arial ✅ | 11pt / 700 |
| 22 Horizon Edge | 95 | OK | OK | Arial ✅ | 12pt / 800 |
| 23 Broadside Press | 95 | OK | OK | Georgia ✅ | 14pt / 700 |
| 24 Clay Canvas | 95 | OK | OK | Georgia ✅ | 13pt / 400 |
| 25 Cyan Blueprint | 95 | OK | OK | Arial ✅ | 11pt / 600 |

---

## 4. Corrected this phase — Bucket 3 (build errors → restored to spec)

The Phase-2 build silently flattened several distinctive heading specs to the
baseline (11pt). These had **no ATS or schema justification** and undermined the
themes' design intent. All values are fully ATS-safe and were **restored to spec**:

| Theme | Field | Was (built) | Now (spec) | Why it mattered |
|-------|-------|-------------|------------|-----------------|
| 22 Horizon Edge | `typography.section_heading_size_pt` | 11 | **12** | bold widescreen header hierarchy |
| 23 Broadside Press | `typography.section_heading_size_pt` | 11 | **14** | "massive serif header" is the core identity |
| 24 Clay Canvas | `typography.section_heading_size_pt` | 11 | **13** | airy editorial heading scale |
| 24 Clay Canvas | `typography.section_heading_weight` | 600 | **400** | soft/airy identity (semibold contradicted it) |

---

## 5. Retained intentional deviations (kept + documented)

These 16 fields differ from the literal text spec **by design**. Retained per
review decision (2026-06-03).

### 5a. ATS font swaps — Bucket 1 (already noted in phase2_tasks.md) + Bucket 2 (newly documented)

The ATS whitelist is `{Arial, Calibri, Georgia}`. The spec requested four fonts
that are **not** on it; all were mapped to the nearest whitelist family. ATS safety
is the entire purpose of these templates, so restoring the literal fonts is **not** desirable.

| Theme | Field | Spec | JSON | Note |
|-------|-------|------|------|------|
| 21 Terminal Signal | `base_font` | Roboto | **Arial** | sans → Arial (newly documented) |
| 22 Horizon Edge | `base_font` | Montserrat | **Arial** | sans → Arial (newly documented) |
| 24 Clay Canvas | `base_font` | Lora | **Georgia** | serif → Georgia (phase2_tasks #1) |
| 24 Clay Canvas | `must_include[1]` | "Lora font" | "Georgia serif body font" | string follows the font swap |
| 25 Cyan Blueprint | `base_font` | Open Sans | **Arial** | sans → Arial (phase2_tasks #2) |
| 25 Cyan Blueprint | `must_include[2]` | "Open Sans font" | "Arial sans-serif font" | string follows the font swap |

### 5b. Schema-mandated band-intensity cap — Bucket 2

`MASTER_SCHEMA_V2_3.json` constrains `bands.intensity` to **"subtle to moderate only."**
The spec requested `strong` for three themes; each was clamped to the schema ceiling.

| Theme | Field | Spec | JSON |
|-------|-------|------|------|
| 21 Terminal Signal | `bands.intensity` | strong | **moderate** |
| 22 Horizon Edge | `bands.intensity` | strong | **moderate** |
| 25 Cyan Blueprint | `bands.intensity` | strong | **moderate** |

### 5c. Accent darkening for contrast — Bucket 2 ⭐ (explicit deviation from text spec)

The spec's vivid accents fail WCAG contrast on a white surface and print poorly.
Both were darkened to preserve the hue while staying legible. Accents are used only
on micro-markers / band edges, never on body text. **This is a deliberate departure
from the literal hex in the design spec, retained for accessibility/legibility.**

| Theme | Field | Spec hex | JSON hex | Effect |
|-------|-------|----------|----------|--------|
| 21 Terminal Signal | `palette.complementary_accent` | `#00FF00` (neon green) | **`#008800`** | darker green; readable on white |
| 25 Cyan Blueprint | `palette.complementary_accent` | `#00E5FF` (electric cyan) | **`#0088A0`** | darker teal-cyan; readable on white |

### 5d. Enum normalization + equivalent wording — Bucket 2/4

| Theme | Field | Spec | JSON | Kind |
|-------|-------|------|------|------|
| 21 Terminal Signal | `dividers.divider_rhythm` | "regular" | "moderate" | "regular" is not in the master enum `{sparse,moderate,frequent,alternating,progressive}` |
| 22 Horizon Edge | `accent_logic.primary_use[0]` | "…section headers" | "…section headings" | wording only |
| 23 Broadside Press | `dividers.grammar` | "sharp+offset" | "sharp solid rules with offset breaks between sections" | token expanded to prose |
| 23 Broadside Press | `visual_differentiators[2]` | `deep crimson "editor's ink" accents` | `deep crimson editor's-ink accents` | quote/hyphen style only |
| 25 Cyan Blueprint | `dividers.grammar` | "signal-mix" | "alternating thin and medium rules suggesting a technical signal grid" | token expanded to prose |

---

## 6. Advisories (no action taken — flagged)

- **Divider-rhythm adjacency (soft rule).** `theme-24` and `theme-25` both use
  `divider_rhythm: "alternating"`. CLAUDE.md says adjacent themes must not share
  divider rhythm. **Left as-is per review decision** — both values come from the
  spec and the divider *grammar* differs (dashed vs signal-mix), providing visual
  differentiation. No automated check enforces this; noted as an accepted soft-rule exception.
- **Band heights below baseline.** `theme-23` (1/2/1 pt) and `theme-24` (1/1/1 pt)
  sit below the master schema's `height_rule` baseline of `min_pt: 2`. Preserved as
  the spec's design intent (newspaper offset rules / delicate chip borders). The
  master value is the neutral baseline theme's own height, not an enforced floor.
  ⚠️ At 1pt, verify the band actually renders in the live Google Doc build (§7).

---

## 7. Outstanding / not done

- **No theme registered** in `config/doc_templates.json` and **no Golden Master built.**
  Per `TASKS.md` TASK-005, registration + live build are **gated on the Track A
  `build_golden_master.py` `updateTextStyle` fix** and require Google credentials.
- **No live ATS/style audit** (`tools/audit_doc_style.py`) — requires a live Doc ID.
- 1pt band rendering (themes 23/24) is unverified in a live document (see §6).

## 8. Reproduce

```bash
python3 scratch/verify_themes_2125.py      # full structural + spec-fidelity diff
# Expected: TOTAL DEVIATION FIELDS ACROSS ALL 5 THEMES: 16 (all intentional, §5)
```
