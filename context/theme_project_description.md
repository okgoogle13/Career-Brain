# Claude Desktop Project — Career Brain Theme Gallery

## Project purpose

You are helping assess 10 candidate resume themes for the Career Brain pipeline. Career Brain generates tailored Google Docs resumes, cover letters, and KSC responses for community-services and social-work job seekers in Australia.

The existing production library has 6 registered templates. The task is to evaluate 10 new conceptual themes and decide which are visually distinct, strong, and safe to compile into production templates.

---

## Files in this Project

| File | Purpose |
|---|---|
| `theme-01-graphite-ledger.json` … `theme-10-rainbow-minimal.json` | v2.3 conceptual theme specs — palette, typography, section heading style, visual identity |
| `context/theme_viz_render_spec.md` | Full instructions for the render task |
| `context/theme_viz_sample_content.md` | Fixed AU resume content to use in all 10 mockups |

---

## Your task

1. Read `theme_viz_render_spec.md` for detailed instructions.
2. Render all 10 themes as a single HTML gallery using the fixed sample content.
3. Produce a ranked assessment table and a "keep set" — the theme IDs to compile.

---

## Constraints

- **ATS safety is critical.** Dark backgrounds (theme-02), strong neon accents (theme-08), and low-contrast colour combinations are disqualifying or high-risk flags.
- **Distinctiveness matters.** The existing 6 templates use: Forest Green + Calibri, Deep Navy + Times New Roman, Slate Blue/Teal + Arial, Gold/Red + Calibri. A new theme that looks like one of these is low-value.
- **Career-justice fit.** Themes should work for community services, government, NFP, and healthcare sectors — not just corporate or tech aesthetics.
- **Do not invent content.** Use `theme_viz_sample_content.md` verbatim for every card.

---

## Output format

1. One self-contained HTML file with all 10 cards in a 2×5 grid.
2. A ranked markdown table with your assessment.
3. A "KEEP SET" line at the end, e.g.:

```
KEEP SET (for Claude Code compilation):
theme-01, theme-04, theme-05, theme-06, theme-09
```

Copy this keep set back to Claude Code to trigger Phase 1 compilation.
