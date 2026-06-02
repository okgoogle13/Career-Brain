# Deep-Plan Interview Transcript

**Date:** 2026-06-01  
**Topic:** Theme Extraction & Synthesis — Execution Strategy

---

## Interview Findings

**Q1: Concept Direction**  
**User Selection:** The Pastel Contemporary  
**Rationale:** Soft header bands with lavender/lilac accent strategy; positioned as approachable and contemporary for career-justice and social-work contexts.

**Q2: Phase 1 Output Scope**  
**User Selection:** Clarity (3 very distinct themes, not 4)  
**Rationale:** Simpler to execute, easier QA and validation. Focus on strongest concepts rather than exhaustive exploration.

**Q3: Phase 1 Execution Model**  
**User Selection:** Use Claude Opus instead of Gemini for both phases  
**Rationale:** Prefer single-model pipeline (Claude Opus 4.8 for design synthesis + JSON extraction) over two-model (Gemini + Opus).

---

## Synthesis Constraints (Confirmed)

**Primary Direction:**
- Accent strategy: **Pastel** (lavender, lilac, soft accents)
- Band approach: **Header-band centric** (soft colored header bands + section rules)
- Aesthetic: **Approachable, contemporary** (not technical, not corporate-heavy)
- Target count: **3 cohesive, visually distinct themes** (not 4)

**Must Differ From Existing 10 Themes On:**
- Band placement profile (no existing theme uses soft pastel header band strategy)
- Divider grammar (must differ from existing solid/grid/dashed/dotted patterns)
- Header silhouette (must differ from existing 10 header styles)
- Palette mood (pastels are underexplored in existing 10)
- Accent placement (pastel micro vs. bold accent strategies)

**ATS Constraints (Non-Negotiable):**
- Single-column always
- Arial, Calibri, or Georgia font
- 10.5pt base, 1.22–1.28 line spacing
- A4 portrait, 0.6–0.7" margins
- No icons, images, text boxes, tables, headers/footers
- Dark body text, high contrast
- Plain text in reading order

---

## Phase 1 (Claude Opus): Design Synthesis Output Format

Each of the 3 themes will be described in text (NOT JSON) with:

1. **Visual Identity**
   - Theme name (human-readable)
   - Mood (3–4 adjectives)
   - Motif name (visual hallmark)
   - Density target (low/medium/high)
   - Silhouette (layout description)
   - Personality axis
   - Header silhouette (specific to pastel contemporary direction)
   - Section emphasis pattern (divider-led, band-led, accent-led)
   - Contrast intensity

2. **Palette (Exact Hex Codes)**
   - Base text colors
   - Pastel accent color (lavender/lilac/soft)
   - Complementary neutral accents
   - Neutral surfaces (#FFFFFF)
   - Background tints

3. **Typography**
   - ATS-safe font family (Arial, Calibri, or Georgia)
   - Heading weight and sizing
   - Body text spacing
   - Line height specifics

4. **Layout & Rhythm**
   - Margin estimations
   - Band strategy (placement, height, intensity)
   - Divider grammar (rule style, frequency, weight)
   - Section spacing and grouping

5. **Accent Logic**
   - Where pastel color is allowed (labels, dividers, band backgrounds)
   - Where pastel is forbidden (body text, large blocks)
   - Micro-accent balance rules

6. **Anti-Generic Rules**
   - Design guardrails specific to this theme
   - Must-include visual elements
   - Avoid-list items (must not appear in this design)

7. **Source Attribution**
   - Which of the 8 PDFs inspired which elements
   - Specific design patterns extracted (divider style, header band height, accent placement)

---

## Phase 2 (Claude Opus): JSON Schema Extraction

Each text spec will be translated into valid v2.3 JSON conforming to:
- `templates/MASTER_SCHEMA_V2_3.json` structure
- File naming: `templates/theme-11-*.json`, `theme-12-*.json`, `theme-13-*.json`
- Schema version: "2.3"
- Tier: 1 (ATS Standard)
- Region: "AU"

Validation gates:
- All hex codes are 6-digit uppercase (#ABC123 not #abc123 or #ABC)
- Fonts are in whitelist (Arial, Calibri, Georgia)
- Band strategy is unique vs. existing 10
- Divider grammar is unique vs. existing 10
- Header silhouette is unique vs. existing 10
- No forbidden glyphs or avoided patterns
- No two new themes share the same band+divider combination

---

## Execution Model (Revised from Spec)

**Original Spec:** Gemini 3.1 Pro → Text specs → Claude Opus → JSON

**Revised Model (Per User):** Claude Opus 4.8 → Design synthesis (text specs) + JSON extraction (both phases in Opus)

**Rationale:** Single-model pipeline reduces coordination overhead; Opus 4.8 is capable of both multimodal PDF analysis (given context) and strict JSON schema extraction.

---

## Next Steps

1. **Write Initial Spec** (synthesis of spec + research + interview)
2. **Generate Implementation Plan** (TDD-oriented, section-based execution)
3. **External Opus Review** (plan validation + feedback integration)
4. **Apply TDD Approach** (test stubs for each section)
5. **Create Section Index** (section boundaries for parallel execution)
6. **Execute Sections** (section-writer subagents for text specs + JSON)
7. **Final Verification & Output** (QA, artifact consolidation)
