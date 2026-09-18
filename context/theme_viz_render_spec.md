# Theme Visualization Render Spec — for Claude Desktop

> **Purpose:** render all 10 conceptual themes (`templates/theme-01…theme-10.json`, schema v2.3)
> as comparable single-page resume mockups so a human can rank them on look-and-feel.
> Use this spec **together with** the other files in this Project: `theme_viz_sample_content.md`
> (the fixed sample resume), the 10 theme specs `theme-01-*.json` … `theme-10-*.json`, and
> `THEME_SPEC_GUIDE.md`.

## What to produce

Produce **one self-contained HTML artifact** containing **all 10 themes** as a responsive
side-by-side gallery of single-A4-page mockups, so they can be compared and ranked directly. It
renders live inline — iterate on it with follow-up prompts (e.g. "tighten theme-07 headings",
"warm up theme-09's palette") and it re-renders in place. Use the **same sample content for every
theme** — the only thing that changes between mockups is the visual treatment. This is what makes
them rankable.

## Hard rules (every mockup)

- **A4 portrait, single column.** White (`#FFFFFF`) or `#FAFAFA` page background only.
- **No multi-column, no tables, no text boxes, no images, no icons.** These themes are ATS-safe by
  definition — do not add layout chrome that the production pipeline can't emit.
- **Bullet glyph is `-` only.** Never `•`, `●`, `◆`, `✔`, `★`, or any `forbidden_glyphs` entry.
- Body text near-black (`body_text_color` / palette body), never pure `#000000`.

## Map each theme's v2.3 tokens to the mockup

Read these keys from the theme JSON and honor them:

| Token | Apply to |
|---|---|
| `typography.base_font` / `ats_constraints.font_family[0]` | Whole document font (use the **first** font in the array) |
| `typography.base_size_pt`, `line_spacing`, `spacing_after_pt` | Body text size / leading / paragraph spacing |
| `typography.section_heading_size_pt`, `section_heading_weight`, `section_heading_tracking_pt` | Section headings |
| `palette` (`base_colours`, `complementary_accent`, `neutral_surface`, `neutral_text`, `supporting_neutral`) | Heading color, accent rules/markers, page surface, body text |
| `section_heading_style` (`font_color`, `text_transform`, `decoration`, `accent_color`) | How section headings look (e.g. UPPERCASE + accent rule) |
| `dividers` (`grammar`, `frequency`, `weight`, `divider_rhythm`) | Rules between header/sections/roles — interpret the prose (e.g. "dashed rules", "progressive rhythm") visually |
| `bands` (`placement`, `intensity`, `height_rule`) | Thin accent bands at header edge / metadata strip / section accents |
| `accent_logic` (`primary_use`, `allowed_scope`) | Where the accent color is allowed — headings, labels, thin rules, chip borders, micro markers **only** |
| `skills_background_tint` | Light fill behind the Skills block only |
| `page.margins_in` | Page margins (these are in **inches** in v2.3) |

The `dividers`/`bands`/`accent_logic` values are intentionally **prose, not pixel specs** — that
is why a human is rendering them. Interpret each theme's described motif faithfully and distinctly
(e.g. Copper Teal Circuit = dual-tone copper structure + teal micro-accents + dashed section rules;
Midnight Blueprint = light text on dark surface; Graphite Ledger = thin solid ledger lines).

## Layout skeleton (same 8 blocks, in this order — matches production v2.0)

1. Name (large, theme heading color)
2. Contact line (phone · email · location, muted)
3. Target-role headline (accent color)
4. **SUMMARY** heading + paragraph
5. **SKILLS** heading + inline comma-separated list (with `skills_background_tint`)
6. **EXPERIENCE** heading + 3 roles, each: bold title, muted `org   dates`, `-` bullets
7. **EDUCATION** heading + entries
8. **CERTIFICATIONS** heading + entries

Use the **same 8-block skeleton** so a chosen mockup transfers cleanly to the production v2.0
template that Claude Code compiles.

## Fidelity caveat (state this to the user)

These mockups approximate **palette + typography + heading/divider treatment**. The production
builder (`build_golden_master.py`) is deliberately ATS-minimal: it applies font, sizes, colors,
line spacing, heading top/left accent borders, and the skills tint — but it does **not** emit
dashed "circuit" rules, decorative bands, or chips. So the real Google Doc Golden Master will be a
cleaner, flatter version of these mockups. Rank on **palette, font pairing, heading style, and
overall tone** — those survive into production; fine decorative motifs may not.

## Output back to Claude Code

A short ranked list, e.g.:

```
1. theme-05 copper-teal-circuit — ship first
2. theme-08 nordic-neon — strong, slate alternative
3. theme-01 graphite-ledger — conservative pick
... (+ any palette/typography tweak notes per theme)
exclude: theme-02 midnight-blueprint (dark-mode ATS/print risk)
```

Claude Code then compiles the winners v2.3 → v2.0, builds the Golden Master, audits, and registers.
