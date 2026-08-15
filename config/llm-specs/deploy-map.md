# deploy-map.md

Per-surface block and field mapping. `operations.md` owns budgets, verification, rollout, and maintenance.

---

## Where each block goes

| Surface | Required behavior |
|---|---|
| Claude profile | CORE in profile instructions |
| ChatGPT custom instructions | CORE |
| Gemini Saved info | CORE |
| Perplexity profile | CORE |
| Claude Custom Style | None; never create one, because a persistent style can bleed into coding contexts |
| Claude Comms Project | `+COMMS` plus roster rules; `+COMMS` above roster rules in Project Instructions |
| Claude Comms Project Knowledge | `comms-examples.local.md` and `claude-project.md`; reference/wiring material only, never Instructions |
| Claude Code global | CORE + `+DEPTH` + `+CODE` in `~/.claude/CLAUDE.md` |
| Claude Code per repo | No canonical blocks; repo-specific commands/conventions only |
| Cowork development folder | CORE + `+DEPTH` + `+CODE` in connected-folder `CLAUDE.md`; do not rely on account-profile inheritance |
| Claude API / Agent SDK | CORE plus optional additions; `+DEPTH` for planning, `+CODE` for technical agents, `+COMMS` only for approved private drafting sessions |
| ChatGPT Comms Project | `+COMMS` only; portable tiers apply, but no person-specific roster/scenario rules |
| Gemini comms context | `+COMMS` only in a Gem or drafting-conversation head; portable tiers apply, but no person-specific roster/scenario rules |
| Claude Desktop `my-voice-comms` skill | `+COMMS`, no roster; local `SKILL.md`, hand-pasted, never symlinked |
| Gemini CLI | CORE + `+DEPTH` + `+CODE` in `GEMINI.md` |
| Codex / Antigravity | CORE + `+DEPTH` + `+CODE` in `AGENTS.md` or equivalent |
| Generic API | CORE plus optional additions in system prompt |

**ChatGPT's two-box layout**
CORE can be pasted whole or split at its existing "About me" / "How to respond" boundary. Do not add `+DEPTH` unless explicitly deciding ChatGPT needs it.

---

## If it's behaving wrong

- Weak pushback, one oversized recommendation, or poor assumptions -> CORE.
- Fragmented plans, repeated questions, or invented side projects -> `+DEPTH`.
- Verbose/incomplete code or unrelated refactors -> `+CODE`.
- Assistant-like, too-long, or trade-off-heavy drafts -> `+COMMS`.
- Comms voice in coding -> remove `+COMMS` from that surface.
- Unsupported researched claims or citation formatting that conflicts with the platform -> CORE plus that platform's citation convention.
