# Handover Package Manifest

This folder is the final handover bundle for the ATS resume theme system update.

## Included
- Master schema JSON.
- Theme JSON files for batches 1, 2, and 3.
- Planning prompts for Opus Desktop.
- Execution prompts for Claude Code in IDE.
- Handover prompt markdown.
- Supporting scripts used to draft the batch outputs.

## Source references
- Canonical batch reference: `Objective_-Conduct-comprehensive-research-on-Appli.md`.
- Batch-1 reference: `proceed-with-batch-1.md`.

## Package intent
- Keep the schema version aligned across all dependent theme files.
- Preserve ATS-safe constraints and single-column layout rules.
- Enforce explicit theme differentiation through silhouette, band strategy, divider grammar, accent placement, and density target.

## Output rules
- JSON files remain valid and standalone.
- Prompts are separated by stage: planning, execution, and handover.
- Scripts are included only if they were used to produce the final bundle.

## Recommended zip name
`careerbrain-handover-package.zip`
