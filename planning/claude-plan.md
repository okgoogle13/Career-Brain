# Implementation Plan: Theme Extraction & Synthesis

**Date:** 2026-06-01  
**Objective:** Design 3 new v2.3 JSON theme files (Pastel Contemporary aesthetic)  
**Scope:** Design synthesis (Opus) + Schema extraction (Opus) + Validation  
**Execution Model:** Section-based, TDD-oriented, parallel-ready

---

## Phase 1: Design Synthesis (Opus Analysis + Spec Generation)

### Goal
Generate 3 coherent, visually distinct Pastel Contemporary design specifications in **text format** (NOT JSON yet). Each spec covers visual identity, palette (exact hex), typography, layout/rhythm, accent logic, anti-generic rules, and source attribution.

### Input Dependencies
- Existing 10 themes (from `templates/theme-01-*.json`)
- 8 external PDFs (Purple Head, Lilac, Modern Black Green, Less Boring B&W, etc.)
- v2.3 schema reference (from `MASTER_SCHEMA_V2_3.json`)
- Quality gates (ATS constraints, differentiation rules)

### Execution Steps

#### Step 1A: Analyze Existing 10 Themes (Read Template Library)
- Read `templates/MASTER_SCHEMA_V2_3.json` (full schema)
- Read all 10 theme files (`theme-01-*.json` through `theme-10-*.json`)
- Extract for each theme:
  - Band placement profile (header-only, metadata, section-led, divider-led, hybrid, minimal)
  - Divider grammar (solid, grid, thin, dashed, dotted, signal-mix, sharp+offset, editorial)
  - Header silhouette (specific top-of-page layout)
  - Palette mood (monochrome, dark navy, warm, cool, terracotta, spectrum, etc.)
  - Accent strategy (none, bold color, micro-accents, micro-spectrum)
- **Deliverable:** Table of 10 themes with their differentiation profiles
- **Verification:** Confirm no two existing themes share same band+divider+palette+accent combination

#### Step 1B: Analyze 8 External PDFs (Multimodal Context)
- For each PDF (Purple Head, Lilac, Modern Black Green, Less Boring B&W, Black & Red, etc.):
  - Extract layout structure (single-column vs. multi-column)
  - Identify color palette (hex codes where possible)
  - Note typography patterns (font families, weights, sizes)
  - Describe divider/rule approaches
  - Identify band strategies (header bands, section bands, metadata strips)
  - Note visual motifs (what makes this design memorable?)
  - Assess ATS compatibility
- **Deliverable:** 8-template design summary (layout, colors, typography, motifs, ATS rating)
- **Verification:** Confirm understanding of which templates are ATS-compatible (4) vs. multi-column (4)

#### Step 1C: Synthesize 3 Pastel Contemporary Concepts
- **Constraint:** Do NOT create 1:1 extractions. Synthesize composite concepts.
- **Strategy:**
  - Take strongest elements from ATS-compatible sources (Purple Head, Modern Black Green, Less Boring B&W, Black & Red)
  - Adapt pastel aesthetics from multi-column sources (Lilac, Monochrome) to single-column
  - Ensure each concept differs from existing 10 on ≥3 dimensions (band, divider, header, palette, accent)
  - Ensure no two new concepts share same band+divider combination

- **Concept 1: The Gentle Authority** (based on plan spec)
  - Motif: Soft lavender header bands
  - Band strategy: Prominent header band + subtle section dividers
  - Divider grammar: Thin solid rules with lavender micro-tints
  - Palette: Soft lavender, warm beige, dark text
  - Source: Purple Head (header concept) + Lilac (pastel palette) + Less Boring B&W (minimal dividers)

- **Concept 2: The Contemporary Lilac** (based on plan spec)
  - Motif: Lilac accent bands with airy whitespace
  - Band strategy: Soft lilac section bands + metadata strip with lilac tint
  - Divider grammar: Dashed thin rules with lilac undertones (editorial style)
  - Palette: Lilac, light greys, dark slate
  - Source: Lilac template (aesthetic) + Violet Signal (editorial divider) + Purple Head (band placement)

- **Concept 3: The Warm Minimal** (based on plan spec)
  - Motif: Minimal bands with warm pastel micros
  - Band strategy: Metadata strip only (subtle) + thin section rules with warm micro-tints
  - Divider grammar: Simple thin solid + warm accent undertones (blush/warm taupe)
  - Palette: Warm beige, blush, light grey, dark text
  - Source: Rainbow Minimal (metadata strip) + Less Boring B&W (minimal) + Modern Black Green (micro-accent adapted)

- **Deliverable:** 3 concept sketches (name, motif, band strategy, divider grammar, palette, personality, source attribution)
- **Verification:** Confirm each concept differs from existing 10 on ≥3 dimensions

#### Step 1D: Generate Detailed Text Specifications (Per Concept)

For **each of the 3 concepts**, write a comprehensive text specification covering:

**Section A: Visual Identity**
- Theme name (human-readable)
- Mood (3–4 adjectives)
- Motif name (visual hallmark)
- Density target (low/medium/high)
- Silhouette (layout description)
- Personality axis (adjectives)
- Header silhouette (specific to this theme)
- Section emphasis pattern (divider-led, band-led, accent-led, hybrid)
- Contrast intensity (low/medium/high)

**Section B: Palette (Exact Hex Codes)**
- Base text colors (#XXXXXX format, uppercase)
- Primary pastel accent (#XXXXXX)
- Complementary neutrals (#XXXXXX)
- Neutral surface (#FFFFFF standard, or variant)
- Neutral text (#XXXXXX, dark)
- Neutral background (#FFFFFF standard, or variant)
- Supporting neutral (#XXXXXX)
- Hex code validation: all 6-digit, uppercase, no #ABC format

**Section C: Typography**
- Base font family (Arial, Calibri, or Georgia)
- Base font size (10.5pt mandatory)
- Line spacing (1.22–1.28, with specific value)
- Heading font weight (bold, semi-bold, etc.)
- Heading size (pt)
- Letter spacing / tracking (optional, if needed)

**Section D: Layout & Rhythm**
- Margin estimations (top, right, bottom, left in inches)
- Band strategy (placement, height in pt, intensity)
- Divider grammar (rule style, frequency, weight, spacing)
- Section spacing rules (before/after, line height)
- Page flow description (top-to-bottom, reading order)

**Section E: Accent Logic**
- Primary use of pastel color (label backgrounds, dividers, band fills, metadata tints)
- Forbidden uses (body text, large blocks, over-text layers)
- Balance rules (how much pastel is "enough" vs. "too much")
- Contrast requirements (pastel band vs. dark text on white)

**Section F: Anti-Generic Rules**
- Must-include visual elements (specific to this theme)
- Forbidden repeats (rules not to repeat from other themes)
- Visual differentiators (what makes this theme instantly recognizable)
- Design guardrails (constraints to avoid generic fallback)

**Section G: Source Attribution**
- List the 8 PDFs and which elements each contributed
- Example: "Purple Head inspired the lavender header band height (18–20pt) and white body background"
- Example: "Less Boring B&W inspired the minimal divider approach; only thin single rules used"

- **Deliverable:** 3 detailed text specifications (one per theme concept)
- **Verification:** Confirm all hex codes are 6-digit uppercase; all measurements are in proper units (pt for font, in for margins, etc.)

### Phase 1 Output
**File:** `planning/phase1-design-synthesis.md`  
**Contains:** 3 complete text design specifications (sections A–G for each concept)  
**No JSON yet.** Pure text descriptions ready for JSON extraction.

---

## Phase 2: Schema Extraction & JSON Generation

### Goal
Translate each text specification into a valid v2.3 JSON theme file. Each file is production-ready and conforms to `MASTER_SCHEMA_V2_3.json`.

### Input Dependencies
- 3 text specifications from Phase 1
- `templates/MASTER_SCHEMA_V2_3.json` (schema reference)
- Existing 10 theme JSON files (for validation of non-overlap)

### Execution Steps

#### Step 2A: Create JSON Template Structure (Per Theme)

For each of the 3 themes, create a JSON file with this structure (reference existing `theme-01-graphite-ledger.json`):

```json
{
  "schema_version": "2.3",
  "template_id": "theme_<snake_case_name>",
  "tier": 1,
  "tier_label": "ATS Standard",
  "doc_type": "resume",
  "target_sector": [],
  "region": "AU",
  "placeholder_schema": "PLACEHOLDERSCHEMAV2",
  "description": "<one sentence describing the theme>",
  "visual_identity": {
    "theme_name": "<from text spec section A>",
    "mood": "<from text spec section A>",
    "motif_name": "<from text spec section A>",
    "density_target": "<low|medium|high from section A>",
    "silhouette": "<layout description from section A>",
    "personality_axis": "<from section A>",
    "header_silhouette": "<from section A>",
    "section_emphasis_pattern": "<divider-led|band-led|accent-led|hybrid from section A>",
    "contrast_intensity": "<low|medium|high from section A>"
  },
  "ats_constraints": {
    "columns": 1,
    "allows_tables": false,
    "allows_images": false,
    "allows_text_boxes": false,
    "allows_headers_footers": false,
    "font_family": ["Arial", "Calibri", "Georgia"],
    "content_layer": "all essential content must remain plain text in normal reading order and selectable",
    "forbidden_glyphs": ["icons", "emoji", "ornamental bullets", "nonstandard ligatures", "special symbols used as decoration", "layout-only unicode art"]
  },
  "palette": {
    "base_colours": ["<from section B>", "<from section B>", "<from section B>"],
    "complementary_accent": "<from section B>",
    "neutral_surface": "#FFFFFF",
    "neutral_text": "<from section B>",
    "neutral_background": "#FFFFFF",
    "supporting_neutral": "<from section B>"
  },
  "typography": {
    "base_font": "<from section C: Arial, Calibri, or Georgia>",
    "base_size_pt": 10.5,
    "line_height_multiplier": <from section C: 1.22-1.28>,
    "heading_weight": "<from section C>",
    "heading_size_pt": <from section C>,
    "letter_spacing": "<optional from section C>"
  },
  "page": {
    "size": "A4",
    "orientation": "portrait",
    "margins_in": {
      "top": <from section D>,
      "right": <from section D>,
      "bottom": <from section D>,
      "left": <from section D>
    }
  },
  "bands": {
    "strategy": "<from section D>",
    "placement": [
      {"location": "<header|section|metadata>", "height_pt": <from section D>, "intensity": "<soft|medium|strong>"}
    ],
    "background_tint": "<from section D>"
  },
  "dividers": {
    "grammar": "<from section D: solid|grid|dashed|dotted|editorial-mix|sharp+offset>",
    "frequency": "<from section D: sparse|regular|dense>",
    "weight_pt": <from section D>,
    "targets": ["<section labels|metadata|divider elements>""],
    "rhythm": "<from section D>"
  },
  "accent_logic": {
    "primary_use": ["<from section E>"],
    "secondary_use": ["<from section E>"],
    "forbidden_scope": ["<from section E>"],
    "balance_rule": "<from section E>"
  },
  "theme_specific_rules": {
    "must_include": ["<from section F>"],
    "forbidden_repeats": ["<from section F>"],
    "visual_differentiators": ["<from section F>"],
    "anti_generic_rules": ["<from section F>"]
  },
  "section_heading_style": {
    "font_color": "<from section B>",
    "background_tint": "<optional from section B>",
    "font_weight": "<from section C>"
  },
  "body_text_color": "<from section B>",
  "muted_text_color": "<from section B>",
  "skills_background_tint": "<optional from section B>",
  "avoid_list": [
    "tonal-only palette dependency",
    "same top-of-page structure as other themes",
    "same divider grammar as adjacent theme",
    "generic safe fallback",
    "over-softened hierarchy",
    "repeated band placement from existing 10 themes",
    "<additional theme-specific items from section F>"
  ]
}
```

- **Deliverable:** 3 JSON file stubs (structure complete, values extracted from Phase 1)
- **Verification:** Confirm all required keys are present; no typos in key names

#### Step 2B: Validate Hex Codes

For each theme's JSON:
- Confirm all color hex codes are 6-digit uppercase (#XXXXXX format)
- No shorthand (#ABC), no lowercase (#xxxxxx), no alpha channel (#XXXXXXXX)
- Example corrections:
  - #D8BFD8 ✓ (correct)
  - #d8bfd8 ✗ (lowercase → convert to uppercase #D8BFD8)
  - #DBD ✗ (shorthand → expand to 6-digit)

- **Deliverable:** 3 validated JSON files with correct hex formatting
- **Verification:** Run shell command to check all colors in each file: `grep -E '"#[A-F0-9]{6}"' theme-*.json`

#### Step 2C: Validate ATS Compliance

For each theme's JSON:
- ✓ Columns = 1 (no multi-column)
- ✓ allows_tables = false
- ✓ allows_images = false
- ✓ allows_text_boxes = false
- ✓ allows_headers_footers = false
- ✓ font_family includes only Arial, Calibri, Georgia
- ✓ base_size_pt = 10.5
- ✓ line_height_multiplier is 1.22–1.28
- ✓ margins are 0.6–0.7" (all sides)
- ✓ forbidden_glyphs list is complete and accurate

- **Deliverable:** 3 ATS-compliant JSON files (verified)
- **Verification:** Spot-check against `MASTER_SCHEMA_V2_3.json` constraints

#### Step 2D: Validate Differentiation vs. Existing 10 Themes

For each new theme (11, 12, 13):
- Extract band strategy, divider grammar, header silhouette, palette mood, accent approach
- Compare to all 10 existing themes
- Confirm differences on **at least 3 dimensions**

Example:
- **Theme 11 (Gentle Authority):**
  - Band strategy: header-only with soft lavender (unique—no existing theme uses pastel header band)
  - Divider grammar: thin solid rules with pastel tints (unique—no existing theme combines this)
  - Palette mood: warm pastel (unique—existing 10 avoid pastels)
  - **Result:** Differs on 3+ dimensions ✓

- **Theme 12 (Contemporary Lilac):**
  - Band strategy: soft lilac section bands + metadata strip (hybrid approach, unique combination)
  - Divider grammar: dashed lilac rules (unique—Copper Teal uses dashed but with metallic accents, not lilac)
  - Palette mood: lilac + light + airy (unique—no existing theme uses lilac as primary)
  - **Result:** Differs on 3+ dimensions ✓

- **Theme 13 (Warm Minimal):**
  - Band strategy: metadata-only (like Rainbow Minimal) BUT with warm pastel micro-tints (unique)
  - Divider grammar: thin + warm blush/taupe undertones (unique—Rainbow Minimal uses thin but with cool spectrum)
  - Palette mood: warm pastels (unique—existing 10 don't use warm pastels)
  - **Result:** Differs on 3+ dimensions ✓

- **Also verify:** No two new themes share the same band+divider combination
  - Theme 11: header-band + thin-solid-lavender
  - Theme 12: section-band + dashed-lilac
  - Theme 13: metadata-only + thin-blush
  - **Result:** All unique ✓

- **Deliverable:** Differentiation verification report (table showing each new theme vs. all 10 existing)
- **Verification:** Confirm no overlaps; ensure each new theme is visually distinct

#### Step 2E: Validate No Forbidden Glyphs or Avoided Patterns

For each theme's JSON:
- Confirm avoid_list does NOT contain any items that appear in the theme's actual values
  - Example: If avoid_list includes "tonal-only palette dependency", confirm the theme uses multiple distinct hues, not tones
- Confirm forbidden_glyphs are not referenced anywhere in visual identity or design rules
- Confirm theme_specific_rules align with actual design (no contradictions)

- **Deliverable:** 3 validated JSON files (no forbidden patterns)
- **Verification:** Manual spot-check of avoid_list vs. actual design elements

#### Step 2F: Write to Filesystem

Create 3 JSON theme files in `templates/` directory:
- `templates/theme-11-gentle-authority.json`
- `templates/theme-12-contemporary-lilac.json`
- `templates/theme-13-warm-minimal.json`

Confirm files are readable and properly formatted (valid JSON syntax).

- **Deliverable:** 3 JSON files in templates/ directory
- **Verification:** `cd templates && ls -la theme-{11,12,13}-*.json`

### Phase 2 Output
**Files:** 
- `templates/theme-11-gentle-authority.json`
- `templates/theme-12-contemporary-lilac.json`
- `templates/theme-13-warm-minimal.json`

**Status:** Production-ready v2.3 JSON theme files, validated against schema, ATS constraints, differentiation, and quality gates.

---

## Phase 3: Final Validation & Integration Testing

### Goal
Ensure all 3 new themes integrate with Career Brain's pipeline without errors.

### Steps

#### Step 3A: Schema Validation (validate_template_spec.py)

Run the existing validator on each new theme JSON:
```bash
python3 tools/validate_template_spec.py templates/theme-11-gentle-authority.json
python3 tools/validate_template_spec.py templates/theme-12-contemporary-lilac.json
python3 tools/validate_template_spec.py templates/theme-13-warm-minimal.json
```

Validate against rules:
- Rule 1: Form shape (required sections, no forbidden chars)
- Rule 2: Token validity (if any references)
- Rule 3: No fabricated tokens
- Rule 4: Forbidden glyphs check
- Rule 5: Heading whitelist
- Rule 6: AU terminology
- Rule 7: Audit honesty
- Rule 8: Registration shape (if applicable)
- Rule 9: KSC structure (if applicable)

Expected result: **PASS** (no errors, all rules satisfied)

- **Deliverable:** 3 validator outputs (PASS status)
- **Verification:** Confirm no FAIL messages

#### Step 3B: Integration Test (Pipeline Simulation)

Optionally run Career Brain pipeline to confirm new themes don't break compilation:
```bash
python3 pipeline/compile_brain.py  # Phase 2
python3 tools/generate_document.py --target "Sample Role" --template resume  # Phase 5 (uses theme selection)
```

Confirm:
- No parsing errors related to new themes
- New themes appear in theme selection UI
- Sample document generates without errors using new themes

- **Deliverable:** Integration test results (no errors)
- **Verification:** Spot-check generated document for correct theme application

#### Step 3C: Quality Summary Report

Create a summary report documenting:
- 3 new themes created (names, motifs, key differentiators)
- All themes ATS-safe and v2.3 compliant
- All themes differ from existing 10 on ≥3 dimensions
- Validation results (schema, ATS, differentiation, no forbidden patterns)
- Pipeline integration status

- **Deliverable:** `planning/QUALITY_SUMMARY.md`
- **Verification:** All items checked and documented

### Phase 3 Output
**Files:**
- Validation reports (3 validator outputs)
- Integration test results
- Quality summary report

**Status:** All 3 new themes validated, tested, and ready for production.

---

## Success Criteria (Verification Checklist)

- [ ] Phase 1 complete: `planning/phase1-design-synthesis.md` contains 3 detailed text specifications
- [ ] Phase 2 complete: 3 JSON files in `templates/theme-{11,12,13}-*.json` with valid structure
- [ ] All hex codes: 6-digit uppercase (#XXXXXX format)
- [ ] All themes: ATS-safe (single-column, whitelisted fonts, no forbidden elements)
- [ ] All themes: Differ from existing 10 on ≥3 dimensions
- [ ] All themes: No two share same band+divider combination
- [ ] All themes: No forbidden glyphs or avoided patterns in avoid_list
- [ ] Schema validation: All 3 themes pass validate_template_spec.py
- [ ] Pipeline integration: New themes don't break compile_brain.py or generate_document.py
- [ ] Quality report: Complete and accurate

---

## Risk Mitigation

**Risk:** Pastel colors may not differentiate enough from existing 10 themes  
**Mitigation:** Pastel Contemporary is completely absent from existing 10; emphasis on band placement + divider grammar as primary differentiators (not palette alone)

**Risk:** Soft pastel may reduce readability or contrast  
**Mitigation:** Validated ATS constraints require dark body text (#2D2D2D or darker) and high contrast on all pastel bands

**Risk:** Hex codes may be inconsistent or non-compliant  
**Mitigation:** Validate all colors are 6-digit uppercase before writing to JSON; spot-check with regex

**Risk:** New themes may accidentally repeat existing band+divider combinations  
**Mitigation:** Explicit differentiation check vs. all 10 existing themes; table-based verification

**Risk:** JSON structure may have typos or missing required keys  
**Mitigation:** Use template structure from existing `theme-01-*.json` as reference; validate against MASTER_SCHEMA_V2_3.json before finalizing

---

## Timeline & Dependencies

- **Phase 1 (Design Synthesis):** Depends on input (spec, research, interview)
- **Phase 2 (JSON Extraction):** Depends on Phase 1 completion
- **Phase 3 (Validation & Integration):** Depends on Phase 2 completion
- **Total scope:** ~30–40 steps across 3 phases; section-based execution enables parallelization within phases

---

## Next Steps (After Plan Approval)

1. **External LLM Review** — Plan is reviewed by Opus subagent for feasibility, clarity, completeness
2. **Integrate Feedback** — Any suggestions are incorporated into this plan
3. **User Review** — Final review and approval before execution
4. **Apply TDD Approach** — Test stubs created for each section
5. **Section Splitting** — Plan divided into sections for parallel execution
6. **Execute Sections** — Section-writer subagents execute each phase in parallel
7. **Final Verification** — All artifacts validated; output summary generated
