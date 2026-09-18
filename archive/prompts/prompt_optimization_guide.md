# Gemini AI Studio Best Practices & Prompt Optimization

Based on the `theme-extraction-spec.md` and your goals, here are the evidence-based best practices for using the Gemini model in Google AI Studio for this specific multimodal task, followed by your polished System Instructions and Prompt.

## 🌡️ Recommended Settings
- **Model:** `gemini-3.1-pro-preview`
- **Temperature: `0.3`**
  *Why?* You need a balance. A temperature of 0.0 will make it too rigid and it might struggle to creatively synthesize *new* themes from the PDFs. A temperature of 1.0 will cause it to hallucinate hex codes or lose track of the strict formatting. `0.3` provides enough creativity to synthesize the design DNA while remaining highly obedient to the ATS constraints and JSON-prep formatting.
- **Top-K / Top-P:** Leave at default.

## 📎 Files to Attach
In addition to the 10 PDF resume templates, you **MUST** attach these context files from your repo to ground the model in your domain language. Without these, it will guess what "bands", "dividers", and "accent_logic" mean.

1. `templates/MASTER_SCHEMA_V2_3.json` (Gives it the exact data structure it is preparing for)
2. `templates/theme-01-graphite-ledger.json` (Serves as a perfect example of the expected outcome)
3. `planning/theme-extraction-spec.md` (Gives it the overarching context of *why* it is doing this)

---

## 🧠 Best Practices for `gemini-3.1-pro-preview` in Google AI Studio

1. **Split System Instructions vs. Prompt:** 
   AI Studio has a dedicated "System Instructions" field. Use it for the overarching persona, hard rules (like ATS constraints), and global formatting. Keep the user prompt focused strictly on the *action* you want performed on the attached files. This prevents the model from forgetting its constraints mid-task.
2. **Chain-of-Thought via XML Tags:**
   Gemini performs significantly better on complex synthesis when forced to "think out loud" before outputting the final structure. We should mandate a `<design_critique>` XML block for its analysis phase. This prevents it from skipping straight to the final output and missing the nuances of the 2-column designs.
3. **Explicitly Address the 2-Column Bias:** 
   LLMs tend to conflate "this layout is not ATS safe" with "this design is bad." You must explicitly tell the model to decouple the **layout** (which will be discarded) from the **visual DNA** (typography, colors, rhythm, which will be kept).
4. **Align with the v2.3 Schema:**
   Since this text output will be fed into Claude to generate the v2.3 JSON schema, the prompt needs to explicitly ask for the exact fields Claude expects (e.g., `density_target`, `base_colours` as an array of 3, 6-digit uppercase hex codes).

---

## 🛠️ 1. System Instructions
*Paste this into the **System Instructions** field in Google AI Studio.*

```text
You are an elite typographer and visual designer. You are evaluating external resume template files to identify the absolute strongest design grammars and adapt them into distinct, production-ready, ATS-safe theme specifications for the "Career Brain" pipeline.

GLOBAL CONSTRAINTS & ATS SAFETY:
- Hard ATS Safety for OUTPUT: Single-column only, no tables, no floating text boxes, no headers/footers, no graphic icons/emojis.
- MULTI-COLUMN SOURCE HANDLING: DO NOT penalize or reject a source template because it uses a double-column layout or sidebars. Your job is to look past the layout to extract the underlying visual DNA (color palette, typography pairings, hierarchical sizing, divider logic) and ADAPT those aesthetics into a strict single-column layout.
- Fonts: Arial, Calibri, Georgia, or Times New Roman only (whitelisted Google Docs fonts).
- Base Size: 10.5pt.
- Line Spacing: 1.22 to 1.28.
- Color: High-contrast body text (#1F1F1F or darker). Pastels must only be used as micro-accents or background tints behind high-contrast text. 
- Hex Codes: All hex codes must be strict 6-digit uppercase (e.g., #EBF8FF). No 3-digit hex codes.
```

---

## 🚀 2. User Prompt
*Paste this into the main chat window after attaching the 10 PDFs + 3 Context Files.*

```text
I have attached 10 resume template files (PDFs) as well as the Master Schema (v2.3), an example theme (Graphite Ledger), and the Extraction Spec for context. 

Execute the following critique skill chain:

<task>
1. Analyze (Reasoning): Inspect each of the 10 uploaded PDF files. Analyze their aesthetics, color schemes, typographical hierarchies, and overall mood. Explicitly identify which elements in the source files violate ATS safety (e.g., sidebars, tables, icons) so you know what not to carry over.
2. Score (Aesthetics First): Evaluate each template strictly on aesthetic impact, typographical clarity, and distinctiveness of color palette/mood.
3. Select & Adapt: Identify the 3 absolute strongest, most visually distinct template designs from the 10 files. Discard the other 7. For the 3 chosen designs, extract their core aesthetics (color scheme, typography pairings, hierarchical sizing) and adapt them to strictly comply with our ATS constraints (forcing the aesthetics into single-column layouts).
</task>

<output_format>
First, provide your internal analysis and scoring inside `<design_critique>` XML tags.

Then, write your complete response in Markdown. Cover these sections for each of the 3 selected concepts so they can be parsed perfectly into our JSON schema in Phase 2:

### [Concept Name]
**Visual Identity:** Silhouette, density target (low/medium/high), motif name, and mood.
**Palette:** Precise 6-digit uppercase hex codes only. Explicitly assign: `base_colours` (list of 3), `complementary_accent`, `neutral_surface`, `neutral_text`, `neutral_background`, and `supporting_neutral`.
**Typography:** Exact base font family (ATS-safe only), font size, line spacing, heading weights, and heading sizes (in pt).
**Layout & Rhythm:** Margins (in inches), band strategy (height in pt, intensity, and location), and divider grammar.
**Accent Logic:** Strict rules for where color is allowed (headings, lines, micro-markers) vs. forbidden (body text).
**Anti-Generic Rules:** Guardrails to prevent the design from falling back to boring templates.
**Source Attribution:** Explicitly state which of the 10 files was selected as the foundation, and explicitly describe how you adapted its multi-column or unsafe elements into a striking single-column layout.
</output_format>
```
