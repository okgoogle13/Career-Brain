# Career Brain
ETL: docs → JSON + Docs. Verify against repo, not memory.
- Approval: no write/exec/commit/push without approval; phases 0-1/2-4/5 need separate sign-off, audit first.
- PII: never expose source_docs/; do not hand-edit. Secrets via 1Password `op run`, never raw values.
- Outputs: processed/, database/ don't hand-edit; archive/ never re-ingested unprompted.
- Invariants: source_lineage required; needs_review pipeline-managed; parsing_errors.log empty post-run.
- Details: Career Brain Manifesto.md; code in pipeline/, tools/, config/.
