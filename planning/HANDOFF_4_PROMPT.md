Goal: Produce PROJECT_MAP.md — a purpose-only map of this repo's tracked files,
containing zero file contents and zero personal data — safe to paste to an
external reviewer (Perplexity or similar). Then add it to .gitignore.

Run with: NEW session · Opus 5 · think hard · normal mode (ask-each-edit).
  Not plan mode, not auto-accept. The file is written to leave the machine, so
  every line should pass under your eye before it exists.
advisor(): NO. Do not call it in this session. advisor() forwards the whole
  transcript, and using an outside reviewer to judge what is safe to send
  outside is circular. Do the adversarial re-read yourself (Step 5).

State (from the previous session — verify, don't trust):
  - Hand-offs 1, 2, 3 and 5 are complete and committed. This is the last one.
  - Expected: 210 tracked files, 28 .py, PROJECT_MAP.md does not exist yet.
  - Pre-existing uncommitted changes NOT yours: planning/comprehensive_cleanup_prompt.md
    (modified) and planning/HANDOFF_4_PROMPT.md (untracked). Never stage them.
  - package.json at root was deliberately left there. Describe it; don't move it.

Step 0 — Baseline. Run and record YOUR numbers; use them, not the ones above:
    git ls-files | wc -l
    git ls-files '*.py' | wc -l
    git status --short
    ls PROJECT_MAP.md            (expect: not found)
    grep -n PROJECT_MAP .gitignore   (expect: nothing)
  If PROJECT_MAP.md already exists, read it and say so before overwriting.

Hard constraints — this file leaves the machine:
  1. Purpose and relationships only. No file bodies, code excerpts, JSON
     values, sample data, field values, or quoted text from any document.
  2. Never open anything under source_docs/, database/, processed/, or
     database/backups/. Do not `cat`, `head`, `rg` inside, or list filenames
     from them. Describe them from CLAUDE.md and the Manifesto (role and
     schema field NAMES only). Report file COUNTS per subdirectory, never names.
  3. Do not open docs/voice/*, config/user_config.json, or anything else that
     is personal by nature. Describe by role from CLAUDE.md ("voice/style
     rules governing generated copy", "user contact/education config").
  4. Filenames that reveal a person, employer, role, or lived experience are
     described generically ("a resume source file"). Tracked filenames outside
     the three data directories are fine to list.
  5. No absolute paths (they contain a local username), no git author or
     email, no commit hashes, no API-key or secret item names, no 1Password
     item names, no Google Doc / Drive IDs. Mention that secrets are injected
     at runtime; nothing more.
  6. Describe domain vocabulary generically. Say "a domain-translation map",
     not the specific sector it translates into.

Step 1 — Inventory. List everything EXCEPT the three data directories:
    git ls-files | grep -Ev '^(source_docs|database|processed)/'
  For source_docs/, database/, processed/: counts per top-level subdirectory
  only, via `git ls-files <dir> | wc -l` (or `cut -d/ -f1-2 | sort | uniq -c`,
  which prints paths — pipe through `awk '{print $1}'` or count in code
  so filenames never enter the transcript). If a command would print a
  filename from those directories, don't run it.

Step 2 — Purpose per file. For the .py files, read only the module docstring
  and the imports/argparse header (`sed -n '1,40p'`), enough to state purpose.
  For dependency edges use: rg -n '^(from|import) ' pipeline tools tests.
  For config/ and templates/: what each file CONFIGURES, not its values —
  read the CLAUDE.md description, don't open the JSON. For .md docs: one line
  from their title/first heading only.

Step 3 — Write PROJECT_MAP.md at repo root, in this shape (short, scannable):
    # Project map (purpose-only export)
    One paragraph: what the repo is, generic — a local ETL pipeline that
    compiles source documents into structured JSON knowledge bases and
    generates templated documents from them.
    ## Pipeline flow        (5-8 lines: phase → script → reads → writes)
    ## Directory guide      (one table: dir | role | file count)
    ## Files by directory   (per file: one line — purpose; depends on: X)
    ## Data directories     (role + schema field names + counts; no names)
    ## Known issues        (see Step 4)
  Target under ~250 lines. Group by directory. Every tracked file outside the
  data directories gets exactly one line, so the entry count is checkable.

Step 4 — Include a "Known issues" section only from facts you verified this
  session (e.g. a script with no callers, a stale doc, a config with no
  reader). Mark anything not verified as [inferred]. Keep it to items an
  outside reviewer could act on. Do not pad.

Step 5 — Adversarial PII re-read (local, no advisor). Read the finished file
  start to finish asking only: "if a stranger read this, what would they learn
  about the person behind this repo?" The right answer is nothing. Then run:
    rg -n -i '/Users/|@|jonas|dougall|okgoogle|gmail|op://|token|credential|\bDOC_ID\b|[0-9a-zA-Z_-]{30,}' PROJECT_MAP.md
  Review each hit; remove or genericise. Finally list the removals you made.

  --- STOP. Present the file (or its full text) and the removal list.
      Wait for approval before touching .gitignore. ---

Step 6 — After approval only: add to .gitignore, under the existing
  regeneratable-output rule that covers processed/:
    # Generated export — regeneratable from the codebase, never committed
    PROJECT_MAP.md
  Edit .gitignore only. Touch no other file.

Verify:
  git ls-files | wc -l                 (equals your Step 0 count — proves the
                                        map did not become tracked)
  git check-ignore -v PROJECT_MAP.md   (points at your new .gitignore line)
  git status --short                   (.gitignore modified; the two
                                        pre-existing planning/ entries; NOT
                                        PROJECT_MAP.md)
  rows in "Files by directory" == (Step 0 count − files in the three data
                                   directories)

Commit (stage only .gitignore; do not use `git add -A`):
  git add .gitignore
  git commit -m "chore: ignore generated PROJECT_MAP export"
End the commit message with the attribution line from the session reminder.

Finish: write planning/HANDOFF_4_COMPLETE_2026-09-19.md (5-10 lines: what was
produced, the Step 5 removals, verify results, anything not verified) — match
HANDOFF_3_COMPLETE_2026-09-19.md's format. Do not commit it unless asked.
Then end with a "Next steps" section of runnable commands.
