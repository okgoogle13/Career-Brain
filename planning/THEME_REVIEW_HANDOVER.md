# Theme Visual-Review Handover → Claude Desktop (Opus 4.8)

**Date:** 2026-06-04 · **From:** Claude Code (Antigravity IDE) · **To:** Claude Desktop visual QA
**Purpose:** Render themes **01–10 and 21–25** as print-accurate HTML previews so a human can rank them and note tweaks. CLI tools can't do visual aesthetic review — this is the Track-1 "Visualize" step.

---

## ✅ Pre-flight: pipeline bugs fixed — 2026-06-04 (do NOT re-investigate)

A multi-angle code review of the builder tools surfaced 3 bugs. All three were fixed and verified by Claude Code before this handover was opened. **Claude Desktop has no action here — these are recorded for context only.**

| # | File | Bug | Fix applied |
|---|---|---|---|
| 1 | `tools/build_golden_master.py` L344 | Flag typo (e.g. `--dry-rn`) silently stripped as a positional, triggering a **live** Google Docs build | `KNOWN_FLAGS` whitelist added; unrecognised flags → `exit 1` immediately |
| 2 | `tools/generate_document.py` L795 | `TransportError` (network down during token refresh) was not caught → raw traceback | `except (RefreshError, TransportError)` now catches both |
| 3 | `tools/generate_document.py` L838 | `run_local_server()` called unconditionally → hangs forever in CI/SSH | `sys.stdin.isatty()` guard raises a clear `DocumentGenerationError` before attempting browser auth |

Verified: 3/3 existing tests pass; `--dry-rn` → exit 1; `--dry-run` → exit 0 with payload; `TransportError` + `isatty` confirmed in source.

---

## 0. Read this first — what "verified" means here (don't cross-wire the three)

| Sense | Applies to | Status |
|---|---|---|
| **(a) Structurally + spec-validated** | themes **01–10 & 21–25** (v2.3 JSON) | ✅ done — see `planning/QUALITY_SUMMARY.md`. **NOT visually reviewed, NOT compiled to v2.0, no Golden Master built.** |
| **(b) Builder styling-bake fix** | `build_golden_master.py` run-level styling | ✅ empirically verified live on **v2.0 production templates** (Arial + Calibri). Unrelated to the look of these themes. |
| **(c) Buildability** | v2.3 themes (01–10, 21–25) | ⚠️ **cannot be built directly** — they have no `blocks[]`. They are design-token specs; they must be compiled v2.3→v2.0 *after* you pick winners. |

**This handover is about sense (a):** previewing the 15 design specs so you can choose a keep-set. The visual review does **not** require building anything.

---

## 1. Ready for visual review — themes 01–10 and 21–25

All fifteen passed Phase-3 validation (95-key parity, ATS-whitelist fonts, 6-digit hex, adjacency rules). Full record: `planning/QUALITY_SUMMARY.md`.

| File | Theme | Font | Accent | Heading | Identity |
|---|---|---|---|---|---|
| `templates/theme-01-graphite-ledger.json` | Graphite Ledger | Georgia | `#6B7280` | 11pt/700 | ledger-like horizontal rules, monochrome palette, header bar plus minimal metadata strip |
| `templates/theme-02-midnight-blueprint.json` | Midnight Blueprint | Arial | `#38BDF8` | 11pt/700 | light text on deep midnight background, technical grid-like divider rhythm, blueprint palette with electric accent |
| `templates/theme-03-citrus-edge.json` | Citrus Edge | Calibri | `#FACC15` | 11pt/700 | citrus orange/yellow accents, edge-based bands rather than full-width blocks, light, open spacing |
| `templates/theme-04-emerald-transit.json` | Emerald Transit | Calibri | `#22C55E` | 11pt/700 | emerald transit bands, stop-based section feel, connecting rules instead of full grids |
| `templates/theme-05-copper-teal-circuit.json` | Copper Teal Circuit | Arial | `#2D8A8A` | 11pt/700 | dual-tone copper and teal logic, dashed rules with label breaks, mixed header and section accent behaviour |
| `templates/theme-06-violet-signal.json` | Violet Signal | Georgia | `#F97316` | 11pt/700 | violet signal lines, editorial divider rhythm, minimal bands with strong rule character |
| `templates/theme-07-solar-gradient.json` | Solar Gradient | Georgia | `#C9825C` | 11pt/700 | layered warm bands, soft dashed divider texture, open airy spacing |
| `templates/theme-08-nordic-neon.json` | Nordic Neon | Arial | `#7BE0FF` | 11pt/700 | electric cyan neon micro accents, tight divider-led rhythm with offsets, minimal header treatment |
| `templates/theme-09-terracotta-service.json` | Terracotta Service | Georgia | `#D4865A` | 11pt/700 | earthy terracotta bands and labels, soft dotted dividers instead of solid rules, section-led hierarchy with chip emphasis |
| `templates/theme-10-rainbow-minimal.json` | Rainbow Minimal | Calibri | `#F472B6` | 11pt/700 | multi-hue spectrum used only in micro elements, very clean neutral canvas, minimal dividers and bands compared to other themes |
| `templates/theme-21-terminal-signal.json` | Terminal Signal | Arial | `#008800` | 11pt/700 | command-line aesthetic, neon vs charcoal contrast, strict rigid left-edge anchoring |
| `templates/theme-22-horizon-edge.json` | Horizon Edge | Arial | `#FF5722` | 12pt/800 | cinematic/widescreen feel, vibrant sunset palette against midnight blue, stepped header alignment |
| `templates/theme-23-broadside-press.json` | Broadside Press | Georgia | `#8B0000` | 14pt/700 | editorial/newspaper broadsheet aesthetic, ultra-high contrast serif, deep crimson editor's-ink accents |
| `templates/theme-24-clay-canvas.json` | Clay Canvas | Georgia | `#D84315` | 13pt/400 | earthy/tactile palette, absence of solid black lines, airy lowercase styling |
| `templates/theme-25-cyan-blueprint.json` | Cyan Blueprint | Arial | `#0088A0` | 11pt/600 | architectural blueprint aesthetic, stark cyan against slate grey, highly measured and organized grid spacing |

> Two accents (21 `#008800`, 25 `#0088A0`) were darkened from the literal spec (`#00FF00`, `#00E5FF`) for contrast — see QUALITY_SUMMARY §5c. If a vivid look reads better on screen, note it as a tweak.

---

## 2. Recommended Artifact settings — **raw HTML + CSS, not React/Tailwind**

**Use a single self-contained HTML artifact.** Rationale:

- The v2.3 schema is **print-precise**: `base_size_pt` (e.g. 10.5pt), `line_spacing` as a **unitless** multiplier (1.22), `section_heading_tracking_pt` (letter-spacing in **pt**), margins in **inches**, exact 6-digit hex. CSS expresses all of these natively (`font-size:10.5pt`, `line-height:1.22`, `letter-spacing:2pt`, `padding:0.65in`, `#008800`).
- **Tailwind** can't hit those values without arbitrary-value escapes (`text-[10.5pt] leading-[1.22] tracking-[2pt]`) — verbose, error-prone, and it hides the 1:1 JSON→CSS contract. **React** adds component scaffolding with zero benefit for a static one-page preview.
- HTML models an A4 page exactly: a page box at `width:210mm; min-height:297mm`, `padding` = the theme's inch margins, `background` = `neutral_surface`. Easy to eyeball side-by-side and to "Print → Save as PDF" if desired.

**Field → CSS contract** (give this to Desktop so the render is faithful, not impressionistic):

| JSON field | CSS |
|---|---|
| `typography.base_font` | `font-family` (+ ATS fallback, e.g. `Arial, sans-serif` / `Georgia, serif`) |
| `typography.base_size_pt` | body `font-size: Npt` |
| `typography.line_spacing` | `line-height: N` (unitless) |
| `typography.section_heading_size_pt` / `_weight` / `_tracking_pt` | section `h` `font-size:Npt` / `font-weight` / `letter-spacing:Npt` |
| `typography.spacing_after_pt` | paragraph/heading `margin-bottom: Npt` |
| `page.margins_in` | page-box `padding: top right bottom left` (in `in`) |
| `palette.neutral_surface` | page-box `background` |
| `palette.neutral_text` / `body_text_color` | body `color` |
| `palette.base_colours[]` | text hierarchy (primary/secondary/muted) |
| `complementary_accent` / `section_heading_style.accent_color` | accent: heading color, rules, bands |
| `section_heading_style.text_transform` / `decoration` | heading `text-transform`, underline/border treatment |
| `bands.*` (`strategy`, `placement`, `height_rule.*pt`, `intensity`) | top/section band: a colored block of `height:Npt` at the stated placement |
| `dividers.grammar` / `weight` / `frequency` | `hr` `border-style` (solid/dotted/dashed), `border-width`, how often |
| `accent_logic.forbidden_scope` | **hard "do-not": never apply accent to body text or background fills** |
| `ats_constraints` | single column, **no images/icons**, all text selectable |

---

## 3. Copy-paste prompt for Claude Desktop (Opus 4.8)

> Attach to the Desktop chat/project first: all 15 JSON theme files (`templates/theme-01..10-*.json` and `templates/theme-21..25-*.json`), plus `context/theme_viz_sample_content.md` (fixed sample resume) and `context/theme_viz_render_spec.md`. Then paste everything between the lines.

---
You are a senior typographic designer. I have attached **15 ATS resume theme specs** (v2.3 JSON format, themes 01–10 and 21–25), a visual render specification (theme_viz_render_spec.md), and a fixed sample resume (theme_viz_sample_content.md).

**Task:** produce **one self-contained HTML artifact** (raw HTML + CSS, **no React, no Tailwind, no external fonts/CDNs/JS**) that renders **all 15 themes** as **A4 pages**, one per theme, stacked vertically, each labeled with its theme name. Use the **same** sample-resume content in every page so they're directly comparable.

**Fidelity rules — map each JSON field exactly, do not approximate:**
- Page box: `width:210mm; min-height:297mm; box-sizing:border-box;` `padding` = `page.margins_in` (in inches); `background` = `palette.neutral_surface`.
- Body: `font-family` = `typography.base_font` (+ generic fallback); `font-size` = `base_size_pt` in `pt`; `line-height` = `line_spacing` (unitless); `color` = `body_text_color`.
- Section headings: `font-size`/`font-weight`/`letter-spacing` from `section_heading_*` (pt where stated); color/transform/decoration from `section_heading_style`.
- Accent (`complementary_accent`): use **only** for headings, thin rules, bands, and metadata markers. **Never** put the accent on body text or as a background behind body text** (`accent_logic.forbidden_scope`).
- Bands (`bands`): render as colored blocks of the stated `height_rule` pt at the stated `placement` (e.g. top edge / section separators).
- Dividers (`dividers`): match `grammar` (solid/dotted/dashed/offset), `weight` (thin/medium), and `frequency`.
- Honor each theme's `theme_specific_rules.must_include` and `anti_generic_rules`; respect single-column, no-image ATS constraints.
- All hex codes exactly as given (6-digit). Don't invent fonts outside the spec.

**After the artifact**, output a short table: for each theme — a 1-line aesthetic verdict, a **keep / cut** recommendation, and any concrete tweak (e.g. "accent too low-contrast → try #X", "heading 14pt feels heavy → 13pt"). Rank the keepers best-to-worst.

**Caveat to weigh:** the production builder is ATS-minimal (font, sizes, colors, line-spacing, heading border, skills tint) — decorative bands/dotted "circuit" rules/chips may **not** survive into the final Google Doc. Rank primarily on palette, font pairing, heading treatment, and overall tone.
---

---

## 4. Frictionless loop — IDE ⇄ Desktop ⇄ CLI (Phase 5)

```
┌─ Antigravity IDE (Claude Code) ──────────────────────────────────────────┐
│ • Owns the pipeline + source of truth: templates/theme-*.json,           │
│   planning/QUALITY_SUMMARY.md                                            │
│ • Phase 2/3: generate + validate theme JSON  ✅ (21–25 done)             │
│ • Produces THIS handover                                                 │
└───────────────┬───────────────────────────────────────────────────────┘
                │  attach all 15 JSON specs + sample content + render spec;
                │  paste the §3 prompt
                ▼
┌─ Claude Desktop (Opus 4.8) ──────────────────────────────────────────────┐
│ • Renders the HTML gallery artifact (visual, can't be done in CLI)       │
│ • You eyeball side-by-side, rank, note palette/type tweaks               │
│ • Decides the KEEP-SET                                                    │
└───────────────┬───────────────────────────────────────────────────────┘
                │  paste the decision back into the CLI (template below)
                ▼
┌─ Antigravity IDE (Claude Code) — Phase 5 ────────────────────────────────┐
│ 1. apply tweaks to the v2.3 JSON → re-run Phase-3 validation             │
│ 2. compile each KEEP theme v2.3 → v2.0 (skeleton:                        │
│    resume_copper_teal_circuit_v1.json)                                   │
│ 3. build Golden Master  ✅ styling-bake now verified                     │
│    (each build = AGENTS.md Phase-5 Gate 4 → present Doc link, wait)      │
│ 4. verify run textStyle (scratch/verify_golden_master.py --base-font=…)  │
│ 5. register Doc ID in config/doc_templates.json                          │
└──────────────────────────────────────────────────────────────────────────┘
```

**Bring the decision back to the CLI** by pasting something like:

```
VISUAL REVIEW RESULT (from Claude Desktop, 2026-06-0X)
KEEP (ranked): theme-23, theme-21, theme-25
CUT: theme-22 (coral bands too heavy for ATS), theme-24 (contrast too low)
TWEAKS:
  - theme-21: restore vivid accent #00FF00? (decide vs contrast)
  - theme-25: heading 11pt → 12pt
NEXT: compile keepers v2.3→v2.0 and build Golden Masters
```

I'll then apply tweaks, re-validate, compile, and build under Gate 4.

---

## 5. Attachments & caveats

- **Attach to Desktop:** all 15 JSON theme files (`templates/theme-01..10-*.json` and `templates/theme-21..25-*.json`), `context/theme_viz_sample_content.md`, `context/theme_viz_render_spec.md` (optionally `templates/MASTER_SCHEMA_V2_3.json` for field semantics).
- **Fidelity caveat:** the HTML preview can be richer than the eventual ATS-minimal production doc; rank on palette / type / heading / tone, not on fine decorative motifs.
- **Do not** treat the preview as proof a Golden Master will look identical — production is sense (c)→(b), compiled + built later.
