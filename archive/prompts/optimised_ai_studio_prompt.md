# Optimised Google AI Studio Prompt — Career Brain Theme Extraction

> **Model target:** Gemini 3.1 Pro (Google AI Studio)
> **Usage:** Copy the **System Instructions** block into the AI Studio system prompt field. Copy the **Task Instructions** block into the chat input, then attach the Context files in the specified order.

---

## ✅ Gemini 3.1 Pro Optimisations Applied

| Optimisation | What changed | Why |
|---|---|---|
| **Prompt as Protocol** | Restructured prompt into Role, Constraints, Context, and Task blocks. | Gemini 3.1 Pro excels with structured, deterministic specifications over conversational prose. |
| **Positive Framing** | Changed negative rules ("Do not use multi-column") to positive mandates ("Use single-column layouts exclusively"). | Negations force the model to process the prohibited concept first; positive framing improves compliance. |
| **Context First** | Moved the existing theme library and schema grounding to the beginning of the prompt. | With large context windows, placing data/context first and specific instructions at the end ensures maximum task focus. |
| **Testable Constraints** | Condensed the System Instructions into highly testable, enforceable bullet points. | Reduces "prompt drift" and prevents the model from ignoring overly verbose "constitutions." |
| **Built-in Self-Correction** | Added a strict verification step at the end of the generation. | Leverages Gemini 3.1 Pro's agentic execution loop capabilities to self-correct hex codes and ATS rules before final output. |

---

## System Instructions

```
You are an elite typographer, visual designer, and ATS-optimization expert.
You produce TEXT DESIGN SPECIFICATIONS that map directly to the Career Brain Theme Schema v2.3.

CONSTRAINTS (Enforce strictly):
1. Layout: Use single-column layouts exclusively.
2. Fonts: Use only Arial, Calibri, Georgia, or Times New Roman.
3. Typography: Set base text size to exactly 10.5pt and line spacing between 1.22 and 1.28.
4. Contrast: Use high contrast colors for body text (#1F1F1F or darker).
5. Accents: Apply accent colors only to headings, thin rules, micro-markers, chip borders, and metadata labels. Keep body text backgrounds transparent/white.
6. Hex Codes: Output all hex codes in strict 6-digit uppercase format (e.g., #EBF8FF).
7. Dimensions: Set margins to 0.60–0.70 inches on all sides on A4 portrait paper.

DIFFERENTIATION PROTOCOL:
Any new theme you propose MUST differ from ALL existing themes on at least 3 of these 6 dimensions:
1. Band placement profile (header_only | section_only | mixed | divider_led | minimal_signature)
2. Divider grammar/rhythm (solid | grid | dashed | dotted | signal-mix | sharp+offset | editorial-mix)
3. Header silhouette (the specific top-of-page visual structure)
4. Palette mood (monochrome | dark | warm | cool | earthy | pastel | high-contrast | spectrum)
5. Accent placement profile (metadata_only | labels_only | chips_only | section_headers_only | mixed_micro_use)
6. Section emphasis pattern (divider-led | band-led | accent-led | hybrid)
```

---

## Task Instructions

```
CONTEXT:
I have attached the Master Schema (v2.3 JSON), an example theme file (Graphite Ledger JSON) for structural reference, and a batch of 8 resume template PDFs.

Existing Theme Library Matrix:
| # | Theme | Motif | Band Profile | Divider Grammar | Palette Mood | Accent |
|---|-------|-------|---|---|---|---|
| 01 | Graphite Ledger | horizontal ledger lines | header_led | solid horizontal rules | monochrome grey | metadata_only |
| 02 | Midnight Blueprint | blueprint grid | header+metadata | precise solid grid | dark navy | electric cyan |
| 03 | Citrus Edge | citrus highlight edge | header+section edges | thin solid | warm accents | mixed |
| 04 | Emerald Transit | transit line stops | header+section stops | thin connecting | emerald green | section band |
| 05 | Copper Teal Circuit | dual-tone logic | mixed header+section | dashed + label breaks | copper+teal | dashed chips |
| 06 | Violet Signal | signal lines | minimal+metadata | editorial thin/heavy mix | violet+orange | signal micro |
| 07 | Solar Gradient | tonal flow | mixed header+section | soft dashed layered | warm browns+gold | warm golden |
| 08 | Nordic Neon | micro-accent tension | divider_led+metadata | sharp solid+micro-offset | dark cool | cyan micro |
| 09 | Terracotta Service | gentle framing | section header band | soft dotted | earthy terracotta | terracotta chips |
| 10 | Rainbow Minimal | controlled spectrum | metadata strip only | simple thin | light+spectrum micro | 6-colour micro |


TASK:
1. Analyze the 8 attached PDFs to extract their underlying visual DNA (color palette, typography pairings, hierarchical sizing, divider logic).
2. For source templates using double-column or sidebars, extract the visual aesthetics and adapt them into strict single-column ATS-safe layouts.
3. Score each template based on Clarity, Distinctiveness, Accessibility, Adaptability, and Career-Justice Alignment, and select the 3 strongest-scoring templates.
4. Output design specifications for the 3 selected concepts using the exact Markdown format provided below.

OUTPUT FORMAT:
Generate the response strictly using the following Markdown structure for each concept. The field names mapped in brackets (e.g. `→ maps to X.Y`) must be mechanically reproducible.

### [Concept N]: [Concept Name]

#### Visual Identity
- **Theme Name:** [Human-readable name, 2-3 words]
- **Mood:** [3-4 adjectives] → maps to `visual_identity.mood`
- **Motif Name:** [Visual hallmark] → maps to `visual_identity.motif_name`
- **Density Target:** [low | medium | high] → maps to `visual_identity.density_target`
- **Silhouette:** [Layout description] → maps to `visual_identity.silhouette`
- **Personality Axis:** [2-3 adjectives] → maps to `visual_identity.personality_axis`
- **Header Silhouette:** [Structure description] → maps to `visual_identity.header_silhouette`
- **Section Emphasis Pattern:** [divider-led | band-led | accent-led | hybrid] → maps to `visual_identity.section_emphasis_pattern`
- **Contrast Intensity:** [low | medium | high] → maps to `visual_identity.contrast_intensity`

#### Palette
(Enforce `^#[A-F0-9]{6}$` regex)
- **base_colours**:
  1. `#______` — [role]
  2. `#______` — [role]
  3. `#______` — [role]
- **complementary_accent:** `#______` — [role]
- **neutral_surface:** `#______`
- **neutral_text:** `#______`
- **neutral_background:** `#______`
- **supporting_neutral:** `#______`

#### Typography
- **Base Font Family:** [Arial | Calibri | Georgia | Times New Roman] → maps to `typography.base_font`
- **Base Size:** 10.5pt → maps to `typography.base_size_pt`
- **Line Spacing:** [Exact value 1.22-1.28] → maps to `typography.line_spacing`
- **Section Heading Weight:** [Numeric] → maps to `typography.section_heading_weight`
- **Section Heading Size:** [pt value] → maps to `typography.section_heading_size_pt`
- **Section Heading Tracking:** [pt value] → maps to `typography.section_heading_tracking_pt`
- **Spacing After:** [pt value] → maps to `typography.spacing_after_pt`

#### Layout & Rhythm
- **Margins (inches):** top: ___ | right: ___ | bottom: ___ | left: ___ 
- **Band Strategy:** [description] → maps to `bands.strategy`
- **Band Placement Profile:** [header_only | section_only | mixed | divider_led | minimal_signature] → maps to `bands.band_placement_profile`
- **Band Placement Targets:** [list] → maps to `bands.placement`
- **Band Height:** min ___pt / max ___pt / default ___pt → maps to `bands.height_rule`
- **Band Intensity:** [subtle | moderate | strong] → maps to `bands.intensity`
- **Accent Placement Profile:** [metadata_only | labels_only | chips_only | section_headers_only | mixed_micro_use] → maps to `bands.accent_placement_profile`
- **Divider Grammar:** [description] → maps to `dividers.grammar`
- **Divider Frequency:** [sparse | moderate | frequent] → maps to `dividers.frequency`
- **Divider Weight:** [thin | thin-to-medium | medium] → maps to `dividers.weight`
- **Divider Rhythm:** [sparse | moderate | frequent | alternating | progressive] → maps to `dividers.divider_rhythm`
- **Divider Targets:** [list] → maps to `dividers.divider_targets`

#### Accent Logic
- **Primary Use:** [list] → maps to `accent_logic.primary_use`
- **Allowed Scope:** [list] → maps to `accent_logic.allowed_scope`
- **Forbidden Scope:** [list] → maps to `accent_logic.forbidden_scope`
- **Balance Rule:** [constraint] → maps to `accent_logic.accent_balance`

#### Anti-Generic Rules
- **Must Include:** [3-5 visual elements] → maps to `theme_specific_rules.must_include`
- **Visual Differentiators:** [3-5 elements] → maps to `theme_specific_rules.visual_differentiators`
- **Anti-Generic Rules:** [3-5 guardrails] → maps to `theme_specific_rules.anti_generic_rules`
- **Avoid List Additions:** [theme-specific items] → maps to `avoid_list`

#### Source Attribution
- **Primary Foundation:** [PDF filename] — extracted elements
- **Secondary Influences:** [PDF filename(s)] — borrowed elements
- **Adaptation Notes:** Describe single-column adaptation from ATS-unsafe sources.

---

### Verification Table
Provide a matrix verifying that each of the 3 new concepts differs from the existing 10 themes on at least 3 dimensions.

### Quality Checklist
- [ ] 3 concepts produced
- [ ] All hex codes are exactly 6-digit uppercase (#XXXXXX)
- [ ] All fonts are strictly from the ATS-safe whitelist
- [ ] All layouts are exclusively single-column
- [ ] Each concept differs from the existing 10 on ≥3 dimensions
```

---

## Attachments Checklist

When you paste the Task Instructions into AI Studio, attach these files in this exact order:

| # | File | Purpose |
|---|---|---|
| 1 | `templates/MASTER_SCHEMA_V2_3.json` | Establishes the structural frame |
| 2 | `templates/theme-01-graphite-ledger.json` | Shows expected output structure |
| 3-10 | All 8 resume template PDFs | Source material for visual DNA extraction |

> [!TIP]
> Order matters for Gemini 3.1 Pro. Attaching the schema first ensures the model builds its internal representation around the constraints before parsing the PDFs.
