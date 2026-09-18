# Claude Code Execution Prompt: Phase 2 & 3 (JSON Generation & Validation)

> **Usage:** Copy everything inside the code block below (both the XML instructions and the 5 theme concepts) and paste it directly into your Claude Code terminal.

```xml
<system_context>
You are an expert AI software engineer operating via the Claude Code CLI. Phase 1 (Design Synthesis) has been completed externally via Google AI Studio. Your task is to execute Phase 2 (Schema Extraction & JSON Generation) and Phase 3 (Validation & Integration) for the Career Brain pipeline.
</system_context>

<operating_rules>
1. **Strict Mapping:** You must translate the provided text specifications directly into valid v2.3 JSON theme files adhering strictly to `templates/MASTER_SCHEMA_V2_3.json`.
2. **No Hallucination:** Map the fields exactly as annotated in the text specs (`→ maps to X.Y`). Do not invent new fields.
3. **Hex Code Enforcement:** Ensure all hex codes are strictly 6-digit uppercase (e.g., #FFFFFF).
4. **Verification-First:** After writing the JSON files, you MUST run the Python validation script on them before declaring the task complete.
</operating_rules>

<execution_pipeline>
<phase name="Phase 2: Schema Extraction & JSON Generation">
<objective>Translate the provided text specifications into valid v2.3 JSON theme files.</objective>
<steps>
  1. Read the 5 theme concepts provided at the bottom of this prompt.
  2. Ask the user which 3 concepts they would like to proceed with (or if they want to generate all 5). Wait for their selection.
  3. Generate the corresponding JSON files in the `templates/` directory (e.g., `theme-11-terminal-signal.json`).
  4. Ensure the JSON structure exactly mirrors `templates/theme-01-graphite-ledger.json` and perfectly maps to `templates/MASTER_SCHEMA_V2_3.json`.
</steps>
</phase>

<phase name="Phase 3: Validation & Testing">
<objective>Run integration tests to guarantee ATS safety and schema compliance.</objective>
<steps>
  1. Run `python3 tools/validate_template_spec.py templates/<new_theme_file>.json` for each newly created theme.
  2. If any validation fails, read the error output, fix the JSON file, and re-run the validator until all themes PASS.
  3. Generate the `planning/QUALITY_SUMMARY.md` report documenting the new themes and their validation status.
</steps>
</phase>
</execution_pipeline>

<initial_directive>
Acknowledge these instructions, read the concepts provided below, and ask me which themes you should convert into JSON.
</initial_directive>

---

### [Concept 1]: Terminal Signal
**Visual Identity**
Theme Name: Terminal Signal
Mood: cyber, technical, utilitarian, stark → maps to visual_identity.mood
Motif Name: glowing terminal underscores → maps to visual_identity.motif_name
Density Target: high → maps to visual_identity.density_target
Silhouette: flush-left, rigid, data-driven → maps to visual_identity.silhouette
Personality Axis: precise, unapologetic, developer-minded → maps to visual_identity.personality_axis
Header Silhouette: stark flush-left minimalist block with a heavy neon underscore → maps to visual_identity.header_silhouette
Section Emphasis Pattern: accent-led → maps to visual_identity.section_emphasis_pattern
Contrast Intensity: high → maps to visual_identity.contrast_intensity

**Palette**
base_colours:
#111111 — [primary text and dark structural rules]
#333333 — [secondary text]
#555555 — [muted text]
complementary_accent: #00FF00 — [neon green for terminal underscores and micro-markers]
neutral_surface: #FFFFFF
neutral_text: #111111
neutral_background: #FAFAFA
supporting_neutral: #EAEAEA

**Typography**
Base Font Family: Roboto → maps to typography.base_font
Base Size: 10.5pt → maps to typography.base_size_pt
Line Spacing: 1.22 → maps to typography.line_spacing
Section Heading Weight: 700 → maps to typography.section_heading_weight
Section Heading Size: 11pt → maps to typography.section_heading_size_pt
Section Heading Tracking: 2.0pt → maps to typography.section_heading_tracking_pt
Spacing After: 4pt → maps to typography.spacing_after_pt

**Layout & Rhythm**
Margins (inches): top: 0.65 | right: 0.65 | bottom: 0.65 | left: 0.65
Band Strategy: minimal bottom-edge neon accents mimicking a command-line cursor → maps to bands.strategy
Band Placement Profile: minimal_signature → maps to bands.band_placement_profile
Band Placement Targets: [header edge] → maps to bands.placement
Band Height: min 2pt / max 4pt / default 3pt → maps to bands.height_rule
Band Intensity: strong → maps to bands.intensity
Accent Placement Profile: mixed_micro_use → maps to bands.accent_placement_profile
Divider Grammar: dotted → maps to dividers.grammar
Divider Frequency: moderate → maps to dividers.frequency
Divider Weight: thin → maps to dividers.weight
Divider Rhythm: regular → maps to dividers.divider_rhythm
Divider Targets: [between sections, between role and achievement clusters] → maps to dividers.divider_targets

**Accent Logic**
Primary Use: [header underscore, tiny bullet points, date markers] → maps to accent_logic.primary_use
Allowed Scope: [micro markers, header edge] → maps to accent_logic.allowed_scope
Forbidden Scope: [body text, background fills, horizontal rules between sections] → maps to accent_logic.forbidden_scope
Balance Rule: neon green must be used exclusively as a pinpoint "signal" in a sea of rigid charcoal text, mimicking a terminal prompt → maps to accent_logic.accent_balance

**Anti-Generic Rules**
Must Include: [stark flush-left alignment, dotted section dividers, neon green micro-accents, heavy tracking on headers] → maps to theme_specific_rules.must_include
Visual Differentiators: [command-line aesthetic, neon vs charcoal contrast, strict rigid left-edge anchoring] → maps to theme_specific_rules.visual_differentiators
Anti-Generic Rules: [no centered text whatsoever, no solid section dividers, no soft/rounded fonts] → maps to theme_specific_rules.anti_generic_rules
Avoid List Additions: [centered text, solid grey dividers, soft palettes, serif fonts] → maps to avoid_list

***

### [Concept 2]: Horizon Edge
**Visual Identity**
Theme Name: Horizon Edge
Mood: expansive, optimistic, cinematic, warm → maps to visual_identity.mood
Motif Name: thick cinematic framing rules → maps to visual_identity.motif_name
Density Target: medium → maps to visual_identity.density_target
Silhouette: wide, horizontal-sweeping → maps to visual_identity.silhouette
Personality Axis: visionary, modern, bold → maps to visual_identity.personality_axis
Header Silhouette: asymmetrical stepped header (name flush left, contact far right) with thick top and bottom coral framing → maps to visual_identity.header_silhouette
Section Emphasis Pattern: band-led → maps to visual_identity.section_emphasis_pattern
Contrast Intensity: medium → maps to visual_identity.contrast_intensity

**Palette**
base_colours:
#0B192C — [primary text, deep midnight navy]
#1E3E62 — [secondary text]
#476685 — [muted text]
complementary_accent: #FF5722 — [vibrant coral for thick section framing rules]
neutral_surface: #FFFFFF
neutral_text: #0B192C
neutral_background: #F9F9F9
supporting_neutral: #E0E0E0

**Typography**
Base Font Family: Montserrat → maps to typography.base_font
Base Size: 10.5pt → maps to typography.base_size_pt
Line Spacing: 1.26 → maps to typography.line_spacing
Section Heading Weight: 800 → maps to typography.section_heading_weight
Section Heading Size: 12pt → maps to typography.section_heading_size_pt
Section Heading Tracking: 1.8pt → maps to typography.section_heading_tracking_pt
Spacing After: 6pt → maps to typography.spacing_after_pt

**Layout & Rhythm**
Margins (inches): top: 0.70 | right: 0.60 | bottom: 0.70 | left: 0.60
Band Strategy: thick, sweeping horizontal bands that act as cinematic letterboxes for sections → maps to bands.strategy
Band Placement Profile: section_only → maps to bands.band_placement_profile
Band Placement Targets: [section separator zones] → maps to bands.placement
Band Height: min 4pt / max 6pt / default 4pt → maps to bands.height_rule
Band Intensity: strong → maps to bands.intensity
Accent Placement Profile: section_headers_only → maps to bands.accent_placement_profile
Divider Grammar: solid → maps to dividers.grammar
Divider Frequency: sparse → maps to dividers.frequency
Divider Weight: medium → maps to dividers.weight
Divider Rhythm: sparse → maps to dividers.divider_rhythm
Divider Targets: [between major sections only] → maps to dividers.divider_targets

**Accent Logic**
Primary Use: [thick horizontal framing rules around section headers] → maps to accent_logic.primary_use
Allowed Scope: [section horizontal boundaries] → maps to accent_logic.allowed_scope
Forbidden Scope: [body text, small labels, bullet points] → maps to accent_logic.forbidden_scope
Balance Rule: coral must only exist as vast, sweeping horizontal lines, never as delicate micro-markers → maps to accent_logic.accent_balance

**Anti-Generic Rules**
Must Include: [deep navy body text, thick coral horizontal rules, extra-wide tracking on headers, asymmetrical header layout] → maps to theme_specific_rules.must_include
Visual Differentiators: [cinematic/widescreen feel, vibrant sunset palette against midnight blue, stepped header alignment] → maps to theme_specific_rules.visual_differentiators
Anti-Generic Rules: [no centered name blocks, no thin/faint grey lines, no standard black text] → maps to theme_specific_rules.anti_generic_rules
Avoid List Additions: [black body text, centered headers, thin grey dividers, cramped margins] → maps to avoid_list

***

### [Concept 3]: Broadside Press
**Visual Identity**
Theme Name: Broadside Press
Mood: journalistic, urgent, factual, uncompromising → maps to visual_identity.mood
Motif Name: heavy headline tracking and sharp offsets → maps to visual_identity.motif_name
Density Target: high → maps to visual_identity.density_target
Silhouette: dense, text-heavy, column-mimicking → maps to visual_identity.silhouette
Personality Axis: truth-seeking, articulate, bold → maps to visual_identity.personality_axis
Header Silhouette: massive serif typography dominating the top margin, tightly stacked → maps to visual_identity.header_silhouette
Section Emphasis Pattern: divider-led → maps to visual_identity.section_emphasis_pattern
Contrast Intensity: high → maps to visual_identity.contrast_intensity

**Palette**
base_colours:
#000000 — [primary text, true black]
#222222 — [secondary text]
#444444 — [muted text]
complementary_accent: #8B0000 — [deep crimson for metadata and sharp offset rules]
neutral_surface: #FFFFFF
neutral_text: #000000
neutral_background: #FFFFFF
supporting_neutral: #F5F5F5

**Typography**
Base Font Family: Georgia → maps to typography.base_font
Base Size: 10.5pt → maps to typography.base_size_pt
Line Spacing: 1.24 → maps to typography.line_spacing
Section Heading Weight: 700 → maps to typography.section_heading_weight
Section Heading Size: 14pt → maps to typography.section_heading_size_pt
Section Heading Tracking: 0.0pt → maps to typography.section_heading_tracking_pt
Spacing After: 6pt → maps to typography.spacing_after_pt

**Layout & Rhythm**
Margins (inches): top: 0.60 | right: 0.70 | bottom: 0.60 | left: 0.70
Band Strategy: sharp, newspaper-like structural divisions using offset rules → maps to bands.strategy
Band Placement Profile: divider_led → maps to bands.band_placement_profile
Band Placement Targets: [section separator zones] → maps to bands.placement
Band Height: min 1pt / max 2pt / default 1pt → maps to bands.height_rule
Band Intensity: moderate → maps to bands.intensity
Accent Placement Profile: metadata_only → maps to bands.accent_placement_profile
Divider Grammar: sharp+offset → maps to dividers.grammar
Divider Frequency: frequent → maps to dividers.frequency
Divider Weight: thin-to-medium → maps to dividers.weight
Divider Rhythm: progressive → maps to dividers.divider_rhythm
Divider Targets: [between sections, between role and achievement clusters] → maps to dividers.divider_targets

**Accent Logic**
Primary Use: [dates, locations, sharp structural offset rules] → maps to accent_logic.primary_use
Allowed Scope: [metadata blocks, specific horizontal rules] → maps to accent_logic.allowed_scope
Forbidden Scope: [body text, major section headings, background fills] → maps to accent_logic.forbidden_scope
Balance Rule: crimson acts as the "red ink" editor's pen, used strictly for dates, locations, and structural separations, never for narrative text → maps to accent_logic.accent_balance

**Anti-Generic Rules**
Must Include: [pure black Georgia font, massive tightly-stacked header, crimson metadata, sharp offset dividers] → maps to theme_specific_rules.must_include
Visual Differentiators: [editorial/newspaper broadsheet aesthetic, ultra-high contrast serif, deep crimson "editor's ink" accents] → maps to theme_specific_rules.visual_differentiators
Anti-Generic Rules: [do not use sans-serif, do not use wide tracking on headings, do not soften black to dark grey] → maps to theme_specific_rules.anti_generic_rules
Avoid List Additions: [sans-serif fonts, wide tracking, dark grey instead of pure black, pastel accents] → maps to avoid_list

***

### [Concept 4]: Clay Canvas
**Visual Identity**
Theme Name: Clay Canvas
Mood: tactile, grounded, artisanal, soft → maps to visual_identity.mood
Motif Name: terracotta chips and vast line spacing → maps to visual_identity.motif_name
Density Target: low → maps to visual_identity.density_target
Silhouette: flush-right floating, airy → maps to visual_identity.silhouette
Personality Axis: empathetic, thoughtful, crafted → maps to visual_identity.personality_axis
Header Silhouette: flush-right, lowercase-styled header floating in vast whitespace → maps to visual_identity.header_silhouette
Section Emphasis Pattern: hybrid → maps to visual_identity.section_emphasis_pattern
Contrast Intensity: low → maps to visual_identity.contrast_intensity

**Palette**
base_colours:
#3E2723 — [primary text, dark espresso brown]
#5D4037 — [secondary text]
#8D6E63 — [muted text]
complementary_accent: #D84315 — [rust/clay for chip borders]
neutral_surface: #FFFFFF
neutral_text: #3E2723
neutral_background: #FCFBF8
supporting_neutral: #EFEBE9

**Typography**
Base Font Family: Lora → maps to typography.base_font
Base Size: 10.5pt → maps to typography.base_size_pt
Line Spacing: 1.28 → maps to typography.line_spacing
Section Heading Weight: 400 → maps to typography.section_heading_weight
Section Heading Size: 13pt → maps to typography.section_heading_size_pt
Section Heading Tracking: 1.0pt → maps to typography.section_heading_tracking_pt
Spacing After: 8pt → maps to typography.spacing_after_pt

**Layout & Rhythm**
Margins (inches): top: 0.70 | right: 0.70 | bottom: 0.70 | left: 0.70
Band Strategy: gentle framing using bordered chips rather than sweeping lines → maps to bands.strategy
Band Placement Profile: mixed → maps to bands.band_placement_profile
Band Placement Targets: [section labels, metadata strip] → maps to bands.placement
Band Height: min 1pt / max 1pt / default 1pt → maps to bands.height_rule
Band Intensity: subtle → maps to bands.intensity
Accent Placement Profile: chips_only → maps to bands.accent_placement_profile
Divider Grammar: dashed → maps to dividers.grammar
Divider Frequency: sparse → maps to dividers.frequency
Divider Weight: thin → maps to dividers.weight
Divider Rhythm: alternating → maps to dividers.divider_rhythm
Divider Targets: [between major sections] → maps to dividers.divider_targets

**Accent Logic**
Primary Use: [borders around section headings (chips)] → maps to accent_logic.primary_use
Allowed Scope: [text borders] → maps to accent_logic.allowed_scope
Forbidden Scope: [body text, horizontal rules, large blocks] → maps to accent_logic.forbidden_scope
Balance Rule: rust/clay accent is restricted purely to delicate borders outlining the section headings, acting as a "stamp" on the canvas → maps to accent_logic.accent_balance

**Anti-Generic Rules**
Must Include: [espresso brown body text, Lora font, flush-right lowercase header, terracotta chip borders] → maps to theme_specific_rules.must_include
Visual Differentiators: [earthy/tactile palette, absence of solid black lines, airy lowercase styling] → maps to theme_specific_rules.visual_differentiators
Anti-Generic Rules: [no black text, no uppercase block headers, no solid horizontal lines] → maps to theme_specific_rules.anti_generic_rules
Avoid List Additions: [uppercase block headings, solid dividers, stark white/black contrast, pure black text] → maps to avoid_list

***

### [Concept 5]: Cyan Blueprint
**Visual Identity**
Theme Name: Cyan Blueprint
Mood: structural, analytical, precise, calculated → maps to visual_identity.mood
Motif Name: technical cyan grid-markers → maps to visual_identity.motif_name
Density Target: high → maps to visual_identity.density_target
Silhouette: framed, measured, block-led → maps to visual_identity.silhouette
Personality Axis: systematic, organized, methodical → maps to visual_identity.personality_axis
Header Silhouette: technical multi-line block anchored to the top edge → maps to visual_identity.header_silhouette
Section Emphasis Pattern: band-led → maps to visual_identity.section_emphasis_pattern
Contrast Intensity: high → maps to visual_identity.contrast_intensity

**Palette**
base_colours:
#1C2833 — [primary text, deep slate]
#34495E — [secondary text]
#5D6D7E — [muted text]
complementary_accent: #00E5FF — [electric cyan for labels and signal markers]
neutral_surface: #FFFFFF
neutral_text: #1C2833
neutral_background: #F4F6F7
supporting_neutral: #E5E8E8

**Typography**
Base Font Family: Open Sans → maps to typography.base_font
Base Size: 10.5pt → maps to typography.base_size_pt
Line Spacing: 1.25 → maps to typography.line_spacing
Section Heading Weight: 600 → maps to typography.section_heading_weight
Section Heading Size: 11pt → maps to typography.section_heading_size_pt
Section Heading Tracking: 1.4pt → maps to typography.section_heading_tracking_pt
Spacing After: 6pt → maps to typography.spacing_after_pt

**Layout & Rhythm**
Margins (inches): top: 0.60 | right: 0.65 | bottom: 0.60 | left: 0.65
Band Strategy: strict edge-to-edge top banding setting a structural blueprint feel → maps to bands.strategy
Band Placement Profile: header_only → maps to bands.band_placement_profile
Band Placement Targets: [top header edge] → maps to bands.placement
Band Height: min 6pt / max 8pt / default 8pt → maps to bands.height_rule
Band Intensity: strong → maps to bands.intensity
Accent Placement Profile: labels_only → maps to bands.accent_placement_profile
Divider Grammar: signal-mix → maps to dividers.grammar
Divider Frequency: moderate → maps to dividers.frequency
Divider Weight: thin-to-medium → maps to dividers.weight
Divider Rhythm: alternating → maps to dividers.divider_rhythm
Divider Targets: [between sections, between header and body] → maps to dividers.divider_targets

**Accent Logic**
Primary Use: [small inline labels, top header edge band] → maps to accent_logic.primary_use
Allowed Scope: [top edge framing, tiny metadata labels] → maps to accent_logic.allowed_scope
Forbidden Scope: [body text, major section headings, standard dividers] → maps to accent_logic.forbidden_scope
Balance Rule: cyan must only be used as a "highlighter" for structural boundaries and labels, never for continuous reading → maps to accent_logic.accent_balance

**Anti-Generic Rules**
Must Include: [edge-to-edge cyan top band, slate grey body text, Open Sans font, signal-mix alternating dividers] → maps to theme_specific_rules.must_include
Visual Differentiators: [architectural blueprint aesthetic, stark cyan against slate grey, highly measured and organized grid spacing] → maps to theme_specific_rules.visual_differentiators
Anti-Generic Rules: [do not use standard black text, do not center the layout, do not use faint/invisible dividers] → maps to theme_specific_rules.anti_generic_rules
Avoid List Additions: [standard black text, centered text, invisible structure, warm/earthy colors] → maps to avoid_list
```
