# Comprehensive Cleanup — Five Hand-offs

Five paste-ready prompts. Run them **in order, each in its own fresh session**, reviewing
between them. Do not paste more than one at a time — the gating is the point.

| # | Hand-off | Risk | Gate |
|---|---|---|---|
| 1 | Pre-flight | none (read-only) | — |
| 2 | Main cleanup | code/pipeline | 3 stop points |
| 3 | Skill audit | docs only | after Hand-off 2 |
| 4 | PII-safe file map | none (export) | after Hand-off 2 |
| 5 | Root-level file placement | doc/file moves only | after Hand-off 2 |

## Repo state a fresh session needs to know

- Git history was reset to a single `Initial commit` to purge PII backup blobs. **There is no
  `git log`/`git blame` to consult** — never treat a file's absence from history as evidence
  it is dead. Use static reachability (ripgrep over imports and call sites).
- `database/backups/` is gitignored and untracked, but **6 backup directories remain on disk
  on purpose** (script safety). They are not stray files. Never open anything under
  `database/` — it holds the lived-experience disclosures CLAUDE.md's Security section
  protects. Metadata only.
- 193 tracked files; 33 `.py` (7,453 LOC across `pipeline/` + `tools/`); `.venv/bin/python`
  exists; bootstrap is `pip install -r requirements.txt` (there is no `pyproject.toml`, so
  `uv sync` will fail here).
- `tests/` has 2 real test files, so `.venv/bin/pytest tests/` is a genuine gate — despite
  CLAUDE.md still claiming "No formal tests/ suite yet" (stale; Hand-off 3 fixes it).

---

## Hand-off 1 — Pre-flight (read-only)

```
Goal: Pin scope, catch stale skill cross-references, stress-test the plan.

Context you need: git history was reset to a single "Initial commit" to
purge PII backup blobs. There is no git log/blame to consult, and the
working tree is clean. database/backups/ is gitignored and untracked but
still on disk (intentional, script safety) — never open a file under
database/.

Step 1 — /interview-me: Which downstream phases are in scope this pass, and
how aggressive on archiving (delete-shy vs delete-eager)?

Step 2 — Stale-reference triage (~10 min, NOT the full skill audit): grep
.claude/skills/*/SKILL.md for referenced paths/scripts; confirm each exists.
Known broken: gold_template_builder_v3 mandates output matching
skills/gold_template_builder_v2/ksc_template_spec_form.md, which does not
exist. Also note pipeline/audit_and_repair_database.py exists and
peer-review depends on it, but CLAUDE.md's folder structure omits it.
Report only — fix nothing.

Step 3 — /critique-plan: Stress-test Hand-off 2 below. Specifically: does
archiving any candidate break tools/generate_document.py or
pipeline/audit_and_repair_database.py?

Do not touch: any file. All three steps are read-only.
Verify: none — output is a scope decision plus two findings lists.
```

---

## Hand-off 2 — Main cleanup (gated)

```
Goal: Gated, local-only cleanup pass over Career-Brain pipeline code,
producing a reviewed diff — stopping for approval between phases per this
repo's Gatekeeper Protocol.

Phase 1 — Orientation (no Repomix, no external transfer, no committed artifact):
  Do NOT run repomix pack_codebase unscoped. Measured: this repo is 27.8 MB
  of JSON (21.1 MB of it database/backups/), so compress=true — which only
  strips code bodies — buys nothing, floods context, and would sweep PII
  into the pack. Do NOT send any output to an external service; source_docs/,
  database/*.json and Career_Brain_Knowledge.md contain PII and CLAUDE.md's
  Security & Data Handling section forbids publishing them externally.
  Do NOT write index.md. A 193-file hand-written index is a point-in-time
  snapshot that goes stale on the next commit, and Phases 2-3 would then make
  decisions from it instead of from the code.
  Instead: read the 33 tracked .py files directly and map the import/call
  graph with ripgrep. Hold this in working context and carry it into Phases
  2-3. Report a short orientation summary only: entry points, which modules
  are reachable from tools/generate_document.py and the pipeline scripts, and
  any file with no inbound references (Phase 3 candidates).

  --- STOP. Present the orientation summary before continuing. ---

Phase 2 — Review:
  /code-review on pipeline/*.py and tools/*.py for correctness, security,
  performance. /security-review for anything touching credentials.json,
  token.json, or .env handling. Report findings; apply no fixes yet.

  --- STOP. Present findings before continuing. ---

Phase 3 — Cleanup and archiving:
  Carry in the stale-reference list from Hand-off 1 Step 2 — do not
  re-derive it, and do not rule a file dead solely because CLAUDE.md omits it.
  Move obsolete files into archive/ (existing convention — do not create
  legacy/). Do not touch anything already under archive/.
  Apply /deprecation-and-migration to decide what is safe to archive, and
  /doubt-driven-development per file before archiving (irreversible —
  adversarially confirm nothing still imports it, especially
  tools/generate_document.py and pipeline/audit_and_repair_database.py).
  Apply /simplify (not the reference-only code-simplification skill) to
  files flagged in Phase 2 — it reviews and applies, so no separate step.
  Then run the project's peer-review skill over the pipeline/*.py diff
  before commit — its documented trigger, and it hard-gates on Career Brain
  invariants.

  database/backups/ is ALREADY HANDLED — gitignored, untracked, and git
  history was reset to purge the PII blobs. Do not re-litigate it, do not
  re-add it, do not propose any further history rewrite. The 6 backup dirs
  on disk are intentional (script safety). Never open a file under
  database/ — it holds the lived-experience disclosures CLAUDE.md's
  Security section protects; metadata only.

  There is NO git history to consult (single Initial commit). Do not use
  "last modified" or absence from git log as evidence a file is dead —
  that signal does not exist here. Reachability must come from ripgrep over
  imports and call sites alone. Commit each archive move as its own commit
  so it stays individually revertible.

  Verify:
    .venv/bin/python -m py_compile <changed files>
    .venv/bin/python pipeline/query_brain.py --help
    .venv/bin/python tools/generate_document.py --help
    .venv/bin/pip install pytest && .venv/bin/python -m pytest tests/

  --- STOP. Present diff + archive list. ---

Escalation: for any Phase 3 decision still ambiguous after
doubt-driven-development, call advisor() before proceeding.

Do not touch: source_docs/, database/ contents, archive/ (existing
contents), config/*.json values.

Commit: Phase 1 produces no commit (no artifact). Phase 3 commits as:
  refactor: archive superseded pipeline scripts
```

---

## Hand-off 3 — Skill audit (after Hand-off 2)

```
Goal: Grade and polish the custom skills, log remaining gaps. Run only after
Hand-off 2's diff is reviewed, so the audit grades the final state.

Step 1 — skill-creator:skill-creator: Grade ats_template_qa_v3,
docs_style_auditor_v3, gold_template_builder_v3, theme_visual_preview_v3,
career_brain_skill_integration_v3, peer-review, and all skills in custom_skills/
for clarity, usefulness, architecture alignment, triggering accuracy. Fix 
gold_template_builder_v3's reference to the nonexistent
skills/gold_template_builder_v2/ksc_template_spec_form.md, fix the stale 
reference in custom_skills/skills-verification-qa/SKILL.md, and fix the bare
validate_template_spec.py invocations (it lives in tools/). Verdict per skill.

Step 2 — claude-md-management:claude-md-improver: Polish skill docs per Step
1. Also add pipeline/audit_and_repair_database.py to CLAUDE.md's folder
structure — it exists and peer-review depends on it, but it is undocumented.

Step 3 — claude-code-setup:claude-automation-recommender: Suggest where
manual tasks can be scripted.

Step 4 — planning-and-task-breakdown: Turn Steps 1-3 plus open items from
Hand-off 2 into TASKS.md (append; never overwrite existing entries) — one
tracked task per gap.

Do not touch: pipeline/*.py, tools/*.py.
Verify: .venv/bin/pytest tests/ (2 real test files exist:
test_build_golden_master.py, test_generate_document.py), plus manual
TASKS.md diff read. Note CLAUDE.md claims "No formal tests/ suite yet" —
that line is stale; correct it in Step 2.
Commit: docs: polish skill documentation and log remaining gaps
```

---

## Hand-off 4 — PII-safe file map (after Hand-off 2)

```
Goal: Produce PROJECT_MAP.md — a file map describing what each tracked file
is FOR, with zero file contents — safe to paste to an external reviewer
(Perplexity or similar) for the objective outside assessment the original
cleanup prompt wanted but could not safely get.

Run this AFTER Hand-off 2, so the map describes the post-cleanup state
rather than one that is about to change.

Hard constraint — this file is written to leave the machine:
  - Describe purpose and relationships ONLY. No file bodies, no code
    excerpts, no JSON values, no sample data, no field values.
  - Never open anything under source_docs/, database/, or processed/.
    Describe those directories from their role in the pipeline and their
    schema names as documented in CLAUDE.md and the Manifesto — not by
    reading them.
  - No personal data of any kind: no names, employers, referees, dates of
    employment, or narrative content. If a filename itself is revealing,
    describe it generically.
  - templates/ and config/: describe what each file configures, not the
    values it contains.

Method: `git ls-files` for the inventory (193 tracked files), targeted
reads of the 33 .py files for their purpose, and ripgrep over imports for
the dependency relationships. Group by directory. For each file: one line
on what it does and what it depends on.

Then re-read the finished PROJECT_MAP.md start to finish as an adversarial
check, asking only: "if a stranger read this, what would they learn about
the person behind this repo?" The correct answer is nothing. Remove
anything that fails that test before presenting it.

PROJECT_MAP.md is a regeneratable export, NOT tracked documentation. Add it
to .gitignore under the existing "regeneratable output" rule that already
covers processed/, e.g.:
  # Generated export — regeneratable from the codebase, never committed
  PROJECT_MAP.md
Rationale: it is a point-in-time snapshot of 193 files that goes stale on
the next commit, and its entire purpose is to leave the machine — keeping
it untracked means it can never be pushed by accident. Regenerate it
whenever an outside read is needed rather than maintaining it.

Do not touch: any other file. This produces one gitignored markdown file
plus a one-line .gitignore addition.
Verify: `git ls-files | wc -l` (193, unchanged) vs. entries in
PROJECT_MAP.md; `git status --short` shows only the .gitignore change, not
PROJECT_MAP.md itself; and a manual read-through confirming no data values
or personal details appear.
Commit: chore: ignore generated PROJECT_MAP export
```

---

## Hand-off 5 — Root-level file placement (after Hand-off 2)

```
Goal: Relocate the loose, tracked files sitting at repo root into a proper
home, producing a reviewed git mv mapping — stopping for approval before
any move, per this repo's Gatekeeper Protocol.

Context you need: this repo's pipeline/, tools/, config/, templates/,
database/, source_docs/ are load-bearing architecture, not "documents" —
scripts resolve paths via Path(__file__).parent.parent and
config/doc_templates.json. Do not propose moving anything under those
directories. This hand-off only concerns files with no defined home:
currently README.md, "Career Brain Manifesto.md",
SKILLS_CREATION_SUMMARY.md, SKILLS_SYNC_VERIFICATION.md,
SYNCED_SKILLS_MANIFEST.md, apply_theme_patches.py, theme-preview-gallery.html,
and Career_Brain___15-Theme_A4_Preview_Gallery_PREMIUM.html — plus anything
else loose at root matching the same pattern (stray top-level .md/.html/.py
with no other tracked home).

Scope — read/move only:
  repo root (top-level files only, not subdirectories), planning/, docs/,
  context/.
Do not touch: pipeline/, tools/, config/, templates/, database/,
source_docs/, archive/ (existing contents), .venv/, .git/, credentials.json,
token.json, .env*, or any *.xml file (all gitignored/regeneratable already).

Step 1 — Inventory: List the loose root-level tracked files (git ls-files
at top level). For each, decide target: docs/ (if it's reference
documentation still in use) or archive/ (existing convention — do not
create legacy/) if superseded or unused.

Step 2 — Reachability check: For apply_theme_patches.py specifically
(and any other loose .py file found), ripgrep pipeline/ and tools/ for
imports or call sites before proposing archival — same
doubt-driven-development gate Hand-off 2 Phase 3 uses. Do not archive
solely because it looks unused; confirm no inbound references first.

Step 3 — Propose mapping: Present a table of current_path → proposed
new_path → rationale. Use git mv semantics (preserves history).

  --- STOP. Present the proposed mapping. Wait for approval. ---

Step 4 — Execute (only after approval): git mv each approved file.

Verify:
  git status --short   (shows only the approved moves)
  .venv/bin/python -m pytest tests/
  .venv/bin/python tools/generate_document.py --help

Commit: chore: relocate root-level docs into docs/ and archive/
```

---

## Why this differs from the original draft

- **Repomix dropped.** `compress=true` strips function bodies from *code*, but 99% of this
  repo's weight was JSON data with no bodies to strip — so it would flood context while
  withholding the call sites Phases 2–3 depend on. 33 files / 7,453 LOC reads directly at
  full fidelity.
- **External handoff to Perplexity cut** — forbidden by CLAUDE.md's Security & Data Handling
  section. Rescheduled as Hand-off 4 in the only shape that can safely leave the machine.
  That cut is what surfaced the 21.1 MB of tracked PII backups, since resolved.
- **`index.md` dropped** — its only stated consumer was the handoff that was cut, and a
  193-file snapshot goes stale immediately while looking canonical.
- **"Continuous execution" replaced with gates**, per the Gatekeeper Protocol and the
  Karpathy principles at the top of CLAUDE.md.
- **`legacy/` → `archive/`**, the existing convention.
- **Skill names corrected.** `@code-reviewer`/`@security-auditor` → `/code-review`,
  `/security-review`. `automation recommender` → `claude-code-setup:claude-automation-recommender`.
  `claude-md-improver` → `claude-md-management:claude-md-improver`. `run-skill-generator`
  and `skills-doctor` don't exist — both point at `skill-creator:skill-creator`.
- **Skill audit moved last**, because five of the six custom skills are Google-Docs/template
  skills the cleanup never invokes. `peer-review` was pulled forward into Phase 3 instead —
  it's the one whose documented trigger is `pipeline/*.py` changes before commit.
- **Hand-off 5 replaces, not adopts, `planning/cleanupcodexprompt.md`.** That prompt targets
  the wrong path (`Career Brain` vs. the actual `Career-Brain`), traverses the whole repo
  with no exclusion list (would walk `database/`, `source_docs/`, `credentials.json`,
  `token.json`), and maps everything — including `pipeline/`, `tools/`, `config/` — onto a
  generic `docs/prompts/content/agents/` layout that conflicts with this repo's load-bearing
  ETL structure. Hand-off 5 keeps the same underlying goal (a home for loose root files) but
  scopes it to root-level files only, inherits Hand-off 4's do-not-open list, and reuses the
  existing Gatekeeper stop-gate instead of `cleanupcodexprompt.md`'s own step-6 STOP.
