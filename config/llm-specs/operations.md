# operations.md

Budgets, rollout order, verification and maintenance. **This file never gets pasted anywhere** — it's the operating manual, not the payload.

Payload lives in `agent-operating-spec.md` (CORE, +DEPTH, +CODE) and `comms/voice-profile.md` (+COMMS). See `deploy-map.md` for placement and `RITUAL.md` for update procedures.

---

## Voice delivery policy

- `+COMMS` is not repository-synced.
- Deploy it only through approved private prompt surfaces listed in `deploy-map.md`.
- A model call without `+COMMS` must not draft as the user.

Embedding an alternate copy creates drift, and reading a machine-local path does not scale across surfaces or machines. Therefore, apps must hand drafting to a session already carrying `+COMMS`.

---

## Character budget

**Design constraint: CORE stays under 1,500 characters**, so it deploys to the tightest field anywhere without an edit. This is checked by `ops/check.sh`.

Stacked-block compositions matter:
- CORE + COMMS
- CORE + DEPTH + CODE

If CORE exceeds the smallest supported field, cut a central rule; do not create a per-surface abbreviated rewrite.

---

## Fallback

The archived `+COMMS` fallback is an exceptional contingency used only if a field rejects the canonical block; see the specific archive file or deployment map.

---

## Rollout

1. Update canonical source and run checks.
2. Deploy to the smallest relevant pilot surface.
3. Run applicable verification tests with real tasks.
4. Fix failures in canonical source, then re-paste.
5. Expand only after the pilot holds.

Live rollout state belongs in `TASKS.md` or a future deployment-status record, not this file.

---

## Verification

| Test | Pass looks like | Targets |
|---|---|---|
| Weak premise | Pushback before the answer | CORE |
| Researched question | Surface-native citations that support claims | CORE |
| Missing decision context | Up to three material questions, otherwise stated assumptions and useful pass | CORE |
| Heavy topic | Named plainly, then options | CORE |
| Non-trivial plan | Implementation-ready, no invented side projects | +DEPTH |
| Inside decline | Decision first, optional one reason after | +COMMS |
| Outside decline | Decision first, no reason | +COMMS |
| Family boundary | Boundary once plus concrete alternative | +COMMS |
| Formal delay | Outcome, constraint, ask; no apology opener or emoji | +COMMS |
| Claude Comms Project | Scenario-appropriate roster patterns, labelled code blocks, no commentary | +COMMS + roster |
| Generic chat draft | Three genuinely different labelled angles, no commentary | +COMMS |
| Small code edit | Whole updated file, verification path, untested items | +CODE |
| Code tool asked for Slack message | Must not apply +COMMS | Separation |

Failing test → fix the block in this repo, then re-paste. Never patch a deployed copy.

---

## Send-capable workflows

Approval gates, recipient validation, queue behavior, and irreversible-action stop conditions belong to the private Comms Hub operator specification. This repository defines drafting configuration, not message dispatch.

---

## Maintenance

Changes flow one direction: out of these files. **Never edit a deployed copy** — a copy you edited in place is a fork you'll forget about.

| Change to | Re-paste to | Expected frequency |
|---|---|---|
| CORE | Every surface in `deploy-map.md` | Twice a year |
| +DEPTH | Every surface in `deploy-map.md` carrying +DEPTH | Rarely |
| +CODE | Every coding surface in `deploy-map.md` | Rarely |
| +COMMS | Every surface in `deploy-map.md` carrying +COMMS | When a tier rule proves wrong |

**Quarterly drift check:** run every test in the table above against every deployed surface. Log which failed. If the same clause fails on two surfaces, revise the canonical clause, not the platform configuration.
