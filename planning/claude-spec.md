# Complete Specification: Theme Extraction & Synthesis

**Project:** Career Brain Theme Library Expansion  
**Objective:** Extract strongest design elements from 8 external resume template PDFs and synthesize 3 production-ready v2.3 JSON theme files  
**Date:** 2026-06-01  
**Execution Model:** Claude Opus 4.8 (both design synthesis + JSON extraction)

---

## Executive Summary

**What:** Design 3 new resume themes for Career Brain's existing 10-theme library.

**Why:** Career Brain is a career-justice tool for community-services and social-work contexts in Australia. The current 10 themes (Graphite Ledger, Midnight Blueprint, Citrus Edge, etc.) cover monochrome, technical, warm, cool, and minimal aesthetics. The new 3 themes should add **Pastel Contemporary** aesthetic—soft, approachable, contemporary—filling a gap in the existing palette.

**Constraint:** All themes must be **ATS-safe** (single-column, body-only content, no icons/images/text boxes, whitelisted fonts). Production runs on Gemini, so all outputs are model-agnostic JSON.

**Scope:** 
- **3 new themes** (not 4—user prioritizes clarity over exhaustive exploration)
- Each theme differs from existing 10 on **at least 3 dimensions** (band placement, divider grammar, header silhouette, palette mood, accent strategy)
- All themes conform to v2.3 schema (`MASTER_SCHEMA_V2_3.json`)
- All themes are validated against quality gates (hex format, ATS compliance, font whitelist, avoided patterns)

---

## Background: Career Brain Architecture

### Schema Halves

1. **Content/Structure Half (v2.0)** — 300–400-line production templates with `blocks[]`, tokens, margins, fonts
2. **Design-Token Half (v2.3)** — ~200-line themes with `visual_identity`, `bands`, `dividers`, `accent_logic`

This work focuses on **v2.3 design tokens**. JSON output is machine-readable, model-agnostic, and ready for production pipeline compilation.

### Existing 10 Themes (Non-Overlap Baseline)

| Theme | Motif | Band Strategy | Divider Grammar | Silhouette | Palette Mood | Accent |
|-------|-------|---|---|---|---|---|
| Graphite Ledger | ledger lines | header-only | solid | divider-led | monochrome | none |
| Midnight Blueprint | blueprint grid | header+metadata | solid grid | divider-led | dark navy | cyan #38BDF8 |
| Citrus Edge | highlight edge | header+edges | thin | hybrid | light warm | orange/yellow |
| Emerald Transit | transit stops | header+stops | connecting | band-led | emerald | green #10B981 |
| Copper Teal Circuit | logic patterns | mixed | dashed | hybrid | copper+teal | dashed dual |
| Violet Signal | signal lines | minimal bands | editorial mix | divider-led | violet+orange | violet |
| Solar Gradient | tonal flow | mixed | soft dashed | hybrid | warm browns | gold accents |
| Nordic Neon | micro-tension | divider-led | sharp offsets | divider-led | dark cool | cyan micro |
| Terracotta Service | gentle frame | section band | soft dotted | section-led | terracotta | terracotta chips |
| Rainbow Minimal | spectrum | metadata only | thin + micro | minimal | light | 6-color micro |

**Key Observation:** Pastels are completely absent. Band strategies cover header, metadata, section, and divider—but no theme uses a **soft pastel header band as primary accent**. This is the gap.

---

## Source Analysis: 8 External Resume Templates

### ATS-Compatible Single-Column Sources (4)

1. **Less Boring B&W**
   - Layout: Single-column
   - Strategy: Typography-first hierarchy via font weight (no color)
   - Dividers: Minimal
   - **Design lesson:** Bold sans-serif weight contrasts; clean minimal approach

2. **Purple Head**
   - Layout: Single-column
   - Strategy: Lavender header band + pill-shaped dividers
   - Colors: Lavender band, dark text, white body
   - **Design lesson:** Pastel header bands work; pill-shaped dividers provide visual rhythm

3. **Modern Black Green**
   - Layout: Single-column
   - Strategy: Neon green micro-accents on dark background; high contrast
   - Colors: Black text, neon green badges
   - **Design lesson:** High-energy modern aesthetic via strategic accent placement

4. **Black & Red**
   - Layout: Single-column
   - Strategy: Black text + strategic red accent (minimally used)
   - Dividers: Thin black rules + red elements
   - **Design lesson:** Red as micro-accent works if usage is disciplined

### Multi-Column Concepts (Adapt, Don't Copy)

5. **Monochrome** → Charcoal + grey palette (adapt sidebar to single-column band)
6. **Lilac** → Pastel sidebar concept (adapt to header band)
7. **B&W 2-Col Bold** → Black sidebar contrast (adapt to accent treatment)
8. **Monochrome Adobe** → Minimal grey approach

---

## Design Direction: Pastel Contemporary

**Concept:** Soft, approachable, contemporary aesthetic using pastel accents (lavender, lilac, soft tints) in header bands and section rules. Personality bridges professional (career-focused) and humane (community-services context).

### The 3 New Themes (Specifications)

#### **Theme 11: The Gentle Authority**

- **Motif:** Soft pastel header bands with warm neutral frame
- **Band Strategy:** Prominent soft lavender header band (height ~18–20pt) + subtle section divider bands
- **Divider Grammar:** Thin solid rules with lavender micro-tints
- **Palette:** Soft lavender (#D8BFD8 or #E6D5E6), warm beige neutrals (#F5F5F0), dark text (#2D2D2D)
- **Accent Logic:** Lavender reserved for header band and section label backgrounds; never overlaid on body text
- **Personality:** Professional yet warm; authoritative but approachable
- **Differentiation vs. Existing 10:** Pastel header band is unique (no existing theme uses soft pastel as primary band color); warm neutral palette is distinct from navy, green, orange, and cool tones
- **Source Attribution:** Purple Head (header band concept) + Lilac (pastel palette) + Less Boring B&W (minimal divider approach)

#### **Theme 12: The Contemporary Lilac**

- **Motif:** Lilac accent bands with airy whitespace and light framing
- **Band Strategy:** Soft lilac section bands (height ~12–14pt) + metadata strip with lilac tint
- **Divider Grammar:** Dashed thin rules with lilac undertones (editorial style)
- **Palette:** Lilac (#DCC9E8 or #E8D5E8), light greys (#F8F8F8), dark slate (#3A3A3A)
- **Accent Logic:** Lilac used on section label backgrounds and dashed rules; body text remains dark
- **Personality:** Contemporary, airy, accessible; feels modern and humane
- **Differentiation vs. Existing 10:** Dashed + lilac combination is unique (Copper Teal uses dashed but not with pastel; Violet uses editorial mix but not lilac); silhouette is hybrid (mixed section + divider emphasis)
- **Source Attribution:** Lilac template (entire aesthetic) + Violet Signal (editorial divider concept) + Purple Head (band placement)

#### **Theme 13: The Warm Minimal**

- **Motif:** Minimal bands with warm pastel micros and clean spacing
- **Band Strategy:** Metadata strip only (very subtle, warm beige background) + thin section rules with warm accent micro-tints
- **Divider Grammar:** Simple thin solid rules + warm accent undertones (blush pink or warm taupe micro-elements)
- **Palette:** Warm beige (#F5E6D3), blush (#F5D5D0), light grey (#F9F9F9), dark text (#2F2F2F)
- **Accent Logic:** Warm pastels appear only in dividers and metadata strip; never on large sections
- **Personality:** Clean, minimal, warm; feels inviting without being cluttered
- **Differentiation vs. Existing 10:** Minimal band strategy with warm micro-accents is unique (Rainbow Minimal uses spectrum but not warm; Graphite Ledger is minimal but monochrome); no existing theme combines minimal band strategy with warm pastel micros
- **Source Attribution:** Rainbow Minimal (metadata-strip concept) + Less Boring B&W (minimal aesthetic) + Modern Black Green (micro-accent idea adapted to warm tones)

---

## Quality Gates & Validation Criteria

### Schema Compliance
- ✓ All themes conform to v2.3 structure (visual_identity, ats_constraints, palette, typography, page, bands, dividers, accent_logic, etc.)
- ✓ File naming: `theme-11-*.json`, `theme-12-*.json`, `theme-13-*.json`
- ✓ schema_version: "2.3", tier: 1, region: "AU"

### ATS Safety (Non-Negotiable)
- ✓ Single-column layout always
- ✓ Fonts: Arial, Calibri, or Georgia only
- ✓ Base size: 10.5pt
- ✓ Line spacing: 1.22–1.28
- ✓ Margins: A4 portrait, 0.65–0.7" all sides
- ✓ No icons, images, text boxes, tables, headers/footers
- ✓ Body text dark (#2D2D2D or darker) for high contrast
- ✓ All essential content in plain text, reading order

### Differentiation vs. Existing 10
- ✓ Theme 11 differs on: band strategy (pastel header vs. existing), palette mood (warm pastel unique), accent placement (header-band-first)
- ✓ Theme 12 differs on: divider grammar (dashed lilac unique), palette mood (lilac + light unique), section emphasis (hybrid distinct)
- ✓ Theme 13 differs on: band strategy (minimal + warm micro unique), palette mood (warm pastels unique), silhouette (minimal + warm accent distinct)
- ✓ No two new themes share same band+divider combination

### Hex Code Format
- ✓ All colors are 6-digit uppercase (#D8BFD8, not #d8bfd8 or #DBD)

### Anti-Generic Rules
- ✓ No two themes are "mild recolors" of each other
- ✓ Each theme has explicit visual motif (not generic)
- ✓ Pastel accents are structured differently across 3 themes (header-band, section-band, micro-accents)

---

## Execution Plan (20 Steps → TDD Implementation)

See `claude-plan.md` for detailed step-by-step execution strategy.

**Summary:**
1. **Phase 1: Design Synthesis** (Claude Opus)
   - Analyze the 8 PDFs and existing 10 themes
   - Synthesize 3 coherent, distinct Pastel Contemporary specs
   - Output text descriptions covering visual_identity, palette, typography, layout, accent_logic, anti-generic rules

2. **Phase 2: JSON Extraction & Validation** (Claude Opus)
   - Translate each text spec to strict v2.3 JSON
   - Validate hex codes, ATS compliance, differentiation
   - Write `theme-11-*.json`, `theme-12-*.json`, `theme-13-*.json`
   - Run `validate_template_spec.py` to confirm schema validity

3. **Quality Assurance**
   - Cross-check band strategies, divider grammars, header silhouettes vs. existing 10
   - Verify no two new themes share band+divider combination
   - Confirm all hex codes are uppercase 6-digit
   - Test rendering in Career Brain pipeline (compile_brain.py + generate_document.py)

---

## Success Criteria

✅ **3 production-ready v2.3 JSON theme files** in `templates/`  
✅ **All themes ATS-safe** (single-column, whitelisted fonts, no forbidden elements)  
✅ **All themes differ from existing 10** on at least 3 dimensions  
✅ **Pastel Contemporary aesthetic** is cohesive and visually distinct across 3 themes  
✅ **All files pass schema validation** (hex format, structure, constraints)  
✅ **Themes integrate with Career Brain pipeline** (no parsing errors, metadata complete)  
✅ **No hallucinated tokens or forbidden glyphs** in any JSON

---

## References

- **Project Spec:** `/Users/okgoogle13/Projects/Career Brain/planning/theme-extraction-spec.md`
- **Research:** `/Users/okgoogle13/Projects/Career Brain/planning/claude-research.md`
- **Interview:** `/Users/okgoogle13/Projects/Career Brain/planning/claude-interview.md`
- **Existing Schemas:** `templates/MASTER_SCHEMA_V2_3.json`, `templates/theme-01-*.json` (examples)
- **Validation Tool:** `tools/validate_template_spec.py`
- **Career Brain Guide:** `CLAUDE.md`
