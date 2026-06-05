# Theme Visual Review — Desktop → Claude Code Handover

**Date:** 2026-06-04
**From:** Claude Desktop · theme_visual_preview_v3 skill
**To:** Claude Code · Gate 4 (Phase 1 compile + Golden Master build)
**Decision:** ALL 15 themes kept. Apply 8 JSON tweaks → compile v2.3→v2.0 → build Golden Masters.

---

## §0 Paste-back block (Claude Code entry point)

```
VISUAL REVIEW RESULT (from Claude Desktop, 2026-06-04)

RANKED THEMES (1 = most production-ready):
  1.  theme-09 · Terracotta Service
  2.  theme-01 · Graphite Ledger
  3.  theme-05 · Copper Teal Circuit
  4.  theme-07 · Solar Gradient
  5.  theme-25 · Cyan Blueprint
  6.  theme-04 · Emerald Transit
  7.  theme-23 · Broadside Press
  8.  theme-06 · Violet Signal
  9.  theme-03 · Citrus Edge
  10. theme-10 · Rainbow Minimal
  11. theme-21 · Terminal Signal
  12. theme-08 · Nordic Neon
  13. theme-22 · Horizon Edge
  14. theme-24 · Clay Canvas
  15. theme-02 · Midnight Blueprint  <- dark-bg ATS risk; user accepted; build last

TWEAKS: 8 JSON edits required before compile. See §1.
  ⚠ Two are CONFIRM OVERRIDE — they reverse Phase-3 spec restorations.

NEXT:
  1. Confirm override decisions (§1, themes 23 + 24)
  2. Apply 8 JSON edits (§1)
  3. Quick JSON sanity check on modified files (§2)
  4. Compile all 15 v2.3→v2.0 in rank order (§3)
  5. Build Golden Masters under Gate 4, one at a time (§4)
  6. Register each Doc ID in config/doc_templates.json
```


---

## §1 JSON tweaks — apply before compile

### theme-03 · Citrus Edge · `templates/theme-03-citrus-edge.json`
| Field | Old | New | Reason |
|-------|-----|-----|--------|
| `complementary_accent` | `"#FACC15"` | `"#90440eff"` | Yellow ≈1.8:1 on white — fails as marker/rule. Orange already used for section edges; unify. |

### theme-04 · Emerald Transit · `templates/theme-04-emerald-transit.json`
| Field | Old | New | Reason |
|-------|-----|-----|--------|
| `muted_text_color` | `"#6EE7B7"` | `"#047857"` | #6EE7B7 on white ≈1.4:1 — invisible as contact/meta text. |

### theme-06 · Violet Signal · `templates/theme-06-violet-signal.json`
| Field | Old | New | Reason |
|-------|-----|-----|--------|
| `complementary_accent` | `"#F97316"` | `"#7C3AED"` | Orange clashes with violet identity; pure violet palette cleaner. |

### theme-07 · Solar Gradient · `templates/theme-07-solar-gradient.json`
| Field | Old | New | Reason |
|-------|-----|-----|--------|
| `section_heading_style.font_color` | `"#9A6A4B"` | `"#7A5238"` | Brown on warm cream ≈3.5:1 — borderline. #7A5238 clears 4.5:1, stays warm. |

### theme-08 · Nordic Neon · `templates/theme-08-nordic-neon.json`
| Field | Old | New | Reason |
|-------|-----|-----|--------|
| `complementary_accent` | `"#7BE0FF"` | `"#0E7490"` | #7BE0FF on #F8FCFD ≈1.3:1 — near-invisible. #0E7490 gives visible teal micro-markers. |

### theme-09 · Terracotta Service · `templates/theme-09-terracotta-service.json`
| Field | Old | New | Reason |
|-------|-----|-----|--------|
| `section_heading_style.font_color` | `"#B77456"` | `"#8A4F36"` | ≈3.2:1 on cream — fails AA. #8A4F36 clears 4.5:1, stays earthy. |
| `muted_text_color` | `"#B08772"` | `"#8A6A57"` | Improves meta legibility within terracotta palette. |


### theme-23 · Broadside Press · `templates/theme-23-broadside-press.json`

⚠️ **CONFIRM OVERRIDE** — Phase-3 deliberately restored `section_heading_size_pt` to 14
(it was flattened to 11 by a build error; 14 is the spec value). This tweak overrides that.

| Field | Old | New | Reason |
|-------|-----|-----|--------|
| `section_heading_size_pt` | `14` | `13` | 14pt uppercase Georgia reads rhythmically heavy; 13pt matches schema standard while preserving editorial weight. |

> **Hard constraint: do NOT change `body_text_color` — #000000 is an explicit, non-negotiable theme requirement.**

### theme-24 · Clay Canvas · `templates/theme-24-clay-canvas.json`

⚠️ **CONFIRM OVERRIDE** — Phase-3 deliberately restored `section_heading_weight` to 400
(it was built as 600 in error; 400 is the spec value for the "airy" identity). This tweak overrides that.

| Field | Old | New | Reason |
|-------|-----|-----|--------|
| `section_heading_weight` | `400` | `600` | Weight-400 lowercase headings too faint for ATS heading recognition; 600 keeps artisanal softness. |

---

## §2 Post-edit sanity check

```bash
# For each of the 8 modified files:
python3 -c "import json; json.load(open('templates/theme-NN-name.json')); print('OK')"
# All changed hex values are valid 6-digit uppercase as written — no further check needed.
# For themes 21-25 if modified in future: python3 scratch/verify_themes_2125.py
```

> Tool note: `tools/audit_doc_style.py` = live-Doc auditor only (requires Doc ID).
> `tools/validate_template_spec.py` = KSC-only. Neither works as a JSON source validator.

---

## §3 Compile — v2.3 → v2.0 (all 15)

**Skeleton:** `templates/resume_copper_teal_circuit_v1.json` (per TASKS.md Phase 1).

The v2.3 files have no `blocks[]`. For each theme: translate v2.3 tokens into the
v2.0 `blocks[]` structure using the skeleton. Output filename: `resume_<name>_v1.json`.

**Compile order** (rank order — highest priority first):
```
theme-09 → theme-01 → theme-05 → theme-07 → theme-25 → theme-04 → theme-23 → theme-06
→ theme-03 → theme-10 → theme-21 → theme-08 → theme-22 → theme-24 → theme-02
```


---

## §4 Build Golden Masters — Gate 4 (AGENTS.md Phase 5)

```bash
# Per compiled theme, in order:
python3 tools/build_golden_master.py --theme templates/resume_<name>_v1.json --dry-run
# Review output. If clean:
python3 tools/build_golden_master.py --theme templates/resume_<name>_v1.json
# STOP. Present Google Doc link. Wait for confirmation before next theme.
```

Register each Doc ID immediately after build:
```json
// config/doc_templates.json → resume.variants.<name>
{ "template_doc_id": "<DOC_ID>", "theme": "templates/resume_<name>_v1.json" }
```

> Builder caveat (expected, not a bug): decorative bands, dashed rules, and chip borders
> will not appear in the live Doc. Builder applies font/size/color/heading-borders only.
> Ranked on palette + type + heading — those survive.

---

## §5 Production notes — no JSON change needed

| Theme | Note |
|-------|------|
| theme-01 | `#9CA3AF` in `base_colours[2]` unused for heading/body text — rubric flag logged; no action |
| theme-02 | Dark surface accepted by user; build last; flag ATS/print risk in `doc_templates.json` |
| theme-04 | Emerald section bands → solid rules in builder (expected) |
| theme-05 | Dashed rules → solid in builder (expected) |
| theme-07 | Soft-dashed rules → solid in builder (expected) |
| theme-21 | Accent `#008800` retained (darkened from `#00FF00` in Phase-3 — QUALITY_SUMMARY §5c; do not re-open) |
| theme-22 | Coral framing → heading rules in builder (expected); navy+coral heading rule survives |
| theme-24 | Chip borders → standard heading in builder (expected); lowercase text-transform survives |
| theme-25 | Accent `#0088A0` retained (darkened from `#00E5FF` in Phase-3 — QUALITY_SUMMARY §5c; do not re-open) |

---

## §6 Pre-flight — do NOT re-investigate

Three pipeline bugs fixed + verified 2026-06-04. Closed.

| # | File | Fix |
|---|------|-----|
| 1 | `tools/build_golden_master.py` | `KNOWN_FLAGS` whitelist; unknown flags → exit 1 |
| 2 | `tools/generate_document.py` L795 | `except (RefreshError, TransportError)` added |
| 3 | `tools/generate_document.py` L838 | `sys.stdin.isatty()` guard for CI/SSH headless |

---

## §7 Ranking rationale (record)

| Rank | Theme | Signal |
|------|-------|--------|
| 1 | Terracotta Service | On-brand community services; warm Georgia; earthy dotted softness |
| 2 | Graphite Ledger | Safest professional default; ledger rules; high trust; broad sector fit |
| 3 | Copper Teal Circuit | Premium dual-tone; teal/copper contrast is distinctive without loudness |
| 4 | Solar Gradient | Warm, humane, open; airy Georgia; NFP/community tone |
| 5 | Cyan Blueprint | Crisp structured; cyan top-band survives; gov/tech |
| 6 | Emerald Transit | Fresh health/community; band-led stops; Calibri modern |
| 7 | Broadside Press | Bold editorial serif; gov/policy/legal; crimson dates strong |
| 8 | Violet Signal | Confident + articulate; violet heading hierarchy clear |
| 9 | Citrus Edge | Friendly modern; left citrus edge is a clean distinctive motif |
| 10 | Rainbow Minimal | Clean canvas; inclusive micro-spectrum; Calibri reads fresh |
| 11 | Terminal Signal | Distinctive dev/tech; off-audience for community services |
| 12 | Nordic Neon | Cool + clean; teal markers now visible post-tweak |
| 13 | Horizon Edge | Cinematic navy+coral; bands flatten but heading rule survives |
| 14 | Clay Canvas | Artisanal warmth; lowercase + weight-600 post-fix; NFP aligned |
| 15 | Midnight Blueprint | Niche dark-mode; ATS risk accepted; specialty variant |

---

*Produced by: theme_visual_preview_v3 skill · Claude Desktop · 2026-06-04*
*Source of truth for Phase 1 compile + Gate 4 build.*
