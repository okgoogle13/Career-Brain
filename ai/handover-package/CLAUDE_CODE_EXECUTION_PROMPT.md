# Claude Code Execution Prompt

Generate JSON theme objects one at a time using the master schema.

Rules:
- Output valid JSON only.
- Each theme must conform to the master schema.
- Each theme must be visually distinct.
- No two adjacent themes may share the same band strategy.
- No two adjacent themes may share the same divider grammar.
- No tonal-only palettes.
- No safe generic fallbacks.
- No repeated top-of-page structure.
- Each theme must have a named motif.
- Each theme must have a complementary accent.
- Each theme must have a clear density target.
- Each theme must specify exact band placement and accent placement.
- Each theme must specify what to avoid.

Batches:
- Batch 1: Graphite Ledger, Midnight Blueprint, Citrus Edge, Emerald Transit.
- Batch 2: Copper Teal Circuit, Violet Signal, Solar Gradient.
- Batch 3: Nordic Neon, Terracotta Service, Rainbow Minimal.

Final output rules:
- Never output prose when JSON is requested.
- Never mix themes into a single combined object.
- Prefer stronger contrast over safe sameness.
- Prefer explicit anti-generic rules over vague style language.
