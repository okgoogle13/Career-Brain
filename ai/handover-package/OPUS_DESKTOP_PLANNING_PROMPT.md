# Opus Desktop Planning Prompt

Generate one valid JSON schema object for an ATS-safe resume theme system. This is not a generic style blob. It is a design-spec schema that must force specific visual decisions.

Requirements:
- Single-column ATS-safe structure.
- Google Docs-compatible.
- Common fonts only.
- No images, tables as layout, sidebars, text boxes, floating objects, or decorative graphics for essential content.
- Keep body text dark, legible, and accessible.
- Explicit support for band strategy, accent placement, divider grammar, density, and motif.
- Include explicit theme-specific fields: band strategy, band targets, accent placement, complementary accent, divider grammar, density target, motif name, signature device, visual differentiators, forbidden repeats, anti-generic rules.

Use a schema shape with top-level areas:
- schema_version
- template_id
- tier
- tier_label
- doc_type
- target_sector
- region
- placeholder_schema
- description
- visual_identity
- ats_constraints
- palette
- typography
- page
- bands
- dividers
- accent_logic
- theme_specific_rules
- section_heading_style
- body_text_color
- muted_text_color
- skills_background_tint
- avoid_list

Output valid JSON only. No markdown. No explanation.
