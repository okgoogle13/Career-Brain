# Theme Gallery Render Spec — Instructions for Claude Desktop

## Task

Produce a single HTML artifact that renders all 10 Career Brain themes side-by-side using fixed sample content. The output is a gallery for visual assessment — the user will pick which themes are distinct and strong enough to compile and register as production templates.

---

## Source files (load these into Project context)

- `templates/theme-01-graphite-ledger.json` through `templates/theme-10-rainbow-minimal.json` — the 10 v2.3 theme specs
- `context/theme_viz_sample_content.md` — fixed resume content to use in every card
- `context/theme_viz_render_spec.md` — this file

---

## What to render per card

Each card represents one theme. Render a scaled-down single-page resume using:

1. **Sample content** from `theme_viz_sample_content.md` — name, contact, target role, summary (2 sentences), skills (first 4), one role with 2 bullets, education line.
2. **Typography**: `typography.base_font`, `typography.base_size_pt`, `typography.line_spacing`
3. **Palette**: use `palette.complementary_accent` for section heading colour; `palette.neutral_text` or `body_text_color` for body; `palette.neutral_surface` or `neutral_background` for page background
4. **Section headings**: apply `section_heading_style.font_color` and `section_heading_style.accent_color`; if `"decoration"` mentions "rule", render a 1px bottom border on section headings using the accent colour
5. **Page margins**: convert `page.margins_in` to px at 96 dpi (1 in = 96 px)
6. **Name**: largest text (1.8× body size), use the copper/primary accent if available; fallback to `palette.complementary_accent`
7. **Contact line**: slightly muted — use `muted_text_color` or the second `palette.base_colours` entry

---

## Gallery layout

- 2 columns × 5 rows, each card at roughly A4 proportions (scaled to ~280px wide)
- Theme name, mood, and font as caption below each card
- Add a visual ATS-risk badge in red if `theme-02-midnight-blueprint` (dark background) — note "dark mode: ATS risk"
- Keep all 10 in the same HTML file

---

## Ranking output

After the gallery HTML, append a markdown ranking table:

| Rank | Theme | Strengths | Concerns | Keep? |
|---|---|---|---|---|
| 1 | ... | ... | ... | ✅ / ❌ |

Evaluate each on:
- **Distinctiveness** from the 6 existing registered themes (Forest Green, Navy, Slate Blue, Gold/Red, Navy/Charcoal — the registered palette set)
- **Visual appeal** — premium, clear, purposeful
- **ATS safety** — light background, no decorative elements that create structural noise
- **Career-justice fit** — does it work for community services, government, NFP contexts?

Flag `theme-02` as high ATS risk due to dark background. Flag any theme with yellow (`theme-03`) or neon (`theme-08`) as accessibility concern for low-contrast body text.

---

## Deliverable

One self-contained HTML file. Output it in a code block so it can be copied and opened directly in a browser.

Then output a short "keep set" list — the theme IDs to compile to v2.0 — formatted as:

```
KEEP SET (for Claude Code compilation):
theme-01, theme-04, theme-05, theme-06, theme-09
```

(Fill in based on your assessment — this is a placeholder.)
