# AGENT-OPS.md

Merged from `operations.md` (budgets, rollout order, verification, maintenance) and
`deploy-map.md` (per-surface block/field mapping) on 2026-08-16. Content below is
unchanged from the two source files, concatenated under their original headings.

---

# operations.md

Budgets, rollout order, verification and maintenance. **This file never gets pasted anywhere** — it's the operating manual, not the payload.

Payload lives in `agent-operating-spec.md` (CORE, +DEPTH, +CODE) and `comms/voice-profile.md` (+COMMS). See `deploy-map.md` section below for placement and `RITUAL.md` for update procedures.

---

## Voice delivery policy

- `+COMMS` is not repository-synced.
- Deploy it only through approved private prompt surfaces listed in the placement table below.
- A model call without `+COMMS` must not draft as the user — hand drafting to a session that already carries it rather than embedding a copy.

---

## Character budget

**Design constraint: CORE stays under 1,500 characters**, so it deploys to the tightest field anywhere without an edit. This is checked by `ops/check.sh`.

Stacked-block compositions matter:
- CORE + COMMS
- CORE + DEPTH + CODE

If CORE exceeds the smallest supported field, cut a central rule; do not create a per-surface abbreviated rewrite.

---

## No fallback

Fail closed: no shortened `+COMMS` variant exists, so a field that rejects the canonical block
gets no `+COMMS` at all rather than a stale or approximate one.

---

## Rollout

Deploy to the smallest relevant surface, verify with the tests below, then expand. Live rollout
state belongs in `TASKS.md`, not this file.

---

## Verification

| Test | Pass looks like | Targets |
|---|---|---|
| Weak premise | Pushback before the answer | CORE |
| Researched question | Surface-native citations that support claims | CORE |
| Missing decision context | Up to three material questions, otherwise stated assumptions and useful pass | CORE |
| Heavy topic | Named plainly, then options | CORE |
| Non-trivial plan | Implementation-ready, no invented side projects | +DEPTH |
| Close friends decline | Decision first, optional one reason after | +COMMS |
| Acquaintances decline | Decision first, no reason | +COMMS |
| Family boundary | Boundary once plus concrete alternative | +COMMS |
| Formal delay | Outcome, constraint, ask; no apology opener or emoji | +COMMS |
| Claude Comms Project | Scenario-appropriate roster patterns, labelled code blocks, no commentary | +COMMS + roster |
| Contested content | Stance variants only; no apology for the disputed matter; no apology opener borrowed from another scenario; no added softening warmth; nothing conceded by omission (silence on the disputed claim doesn't read as agreement); no concession variant unless the input establishes my own responsibility | +COMMS + roster |
| Own-responsibility repair | Ordinary repair survives: apology, one unglamorous reason, concrete next step, routed scenario governs; the contested block does not fire | +COMMS + roster |
| Comms Project inherits CORE | Weak premise inside the Project draws pushback before the answer, with no CORE in the Instructions paste | CORE by inheritance |
| Generic chat draft | Three genuinely different labelled angles, no commentary | +COMMS |
| Small code edit | Whole updated file, verification path, untested items | +CODE |
| Code tool asked for Slack message | Must not apply +COMMS | Separation |

Failing test → fix the block in this repo, then re-paste. Never patch a deployed copy.

---

## Send-capable workflows

Approval gates, recipient validation, queue behavior, and irreversible-action stop conditions belong to the private Comms Hub operator specification. This repository defines drafting configuration, not message dispatch.

---

## Maintenance

| Change to | Re-paste to | Expected frequency |
|---|---|---|
| CORE | Every surface in the placement table below | Twice a year |
| +DEPTH | Every surface carrying +DEPTH in the placement table below | Rarely |
| +CODE | Every coding surface in the placement table below | Rarely |
| +COMMS | Every surface carrying +COMMS in the placement table below | When a category rule proves wrong |

**Quarterly drift check:** run every test in the table above against every deployed surface. Log which failed. If the same clause fails on two surfaces, revise the canonical clause, not the platform configuration.

---

# deploy-map.md

Per-surface block and field mapping. The sections above own budgets, verification, rollout, and maintenance.

---

## Where each block goes

| Surface | Required behavior |
|---|---|
| Claude profile | CORE in profile instructions |
| ChatGPT custom instructions | CORE |
| Gemini Saved info | CORE |
| Perplexity profile | CORE |
| Claude Custom Style | None; never create one, because a persistent style can bleed into coding contexts |
| Claude Comms Project | `+COMMS` plus roster rules, built by `ops/build-project-instructions.sh`; `+COMMS` above roster rules in Project Instructions. CORE is inherited from the Claude profile, never pasted here |
| Claude Comms Project Knowledge | `comms-examples.local.md` and `claude-project.md`; reference/wiring material only, never Instructions |
| Claude Code global | CORE + `+DEPTH` + `+CODE` in `~/.claude/CLAUDE.md` |
| Claude Code per repo | No canonical blocks; repo-specific commands/conventions only |
| Cowork development folder | CORE + `+DEPTH` + `+CODE` in connected-folder `CLAUDE.md`; do not rely on account-profile inheritance |
| Claude API / Agent SDK | CORE plus optional additions; `+DEPTH` for planning, `+CODE` for technical agents, `+COMMS` only for approved private drafting sessions |
| ChatGPT Comms Project | `+COMMS` only; CORE inherited from ChatGPT custom instructions, never pasted here; portable categories apply, but no person-specific roster/scenario rules |
| Gemini comms context | `+COMMS` only in a Gem or drafting-conversation head; CORE inherited from Gemini Saved info, never pasted here; portable categories apply, but no person-specific roster/scenario rules |
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
