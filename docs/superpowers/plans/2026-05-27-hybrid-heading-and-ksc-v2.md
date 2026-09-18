# Hybrid Heading Rename + KSC v2 End-to-End Validation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** (1) Normalise all 5 hybrid resume headings to the ATS-compliant whitelist across JSON theme + Markdown spec + live Google Doc atomically, and (2) drive the unvalidated KSC anti-slop v2 toolchain end-to-end to produce a validated spec, JSON theme, Golden Master, and one live KSC generation.

**Architecture:** Two sequential workstreams. Workstream A (TASK-001) is three coordinated file edits + one manual Google Doc edit by the user. Workstream B (TASK-002) is the v2 KSC pipeline: `gold_template_builder_v3` (LLM) → Markdown spec → `validate_template_spec.py` (hard gate) → JSON theme translation → `build_golden_master.py` (Google Doc creation) → config registration → dry-run → live generation → mark design Approved.

**Tech Stack:** Python 3 (existing `tools/` scripts), Google Docs/Drive API (via existing builders), Markdown specs, JSON theme files following `templates/THEME_SPEC_GUIDE.md`.

**Spec reference:** `docs/superpowers/specs/2026-05-27-session-status-and-next-steps-design.md`

**Note on TDD:** This project has no formal test suite for templates/specs. Verification is via grep, the validator script, dry-run mode, and visual inspection of generated Google Docs. Each task includes explicit verification steps in place of pytest runs.

---

## Workstream A — TASK-001: Hybrid heading atomic rename

### Task 1: Update `templates/resume_hybrid_v1.json` (5 headings)

**Files:**
- Modify: `templates/resume_hybrid_v1.json` (lines 110, 139, 183, 314, 345)

- [ ] **Step 1: Read the file**

Run: `Read templates/resume_hybrid_v1.json`
Confirm current headings: `PROFESSIONAL SUMMARY` (block 4), `CORE SKILLS` (block 5), `WORK EXPERIENCE` (block 6), `EDUCATION` (block 7), `CERTIFICATIONS` (block 8).

- [ ] **Step 2: Apply 5 heading edits**

Use Edit tool 5 times (one per heading). Exact old_string/new_string pairs:

```
"heading": "PROFESSIONAL SUMMARY"  →  "heading": "Summary"
"heading": "CORE SKILLS"           →  "heading": "Skills"
"heading": "WORK EXPERIENCE"       →  "heading": "Experience"
"heading": "EDUCATION"             →  "heading": "Education"
"heading": "CERTIFICATIONS"        →  "heading": "Certifications"
```

Note: each `"heading":` string is unique in the file, so single Edit calls (not replace_all) will succeed.

- [ ] **Step 3: Verify all 5 headings updated**

Run: `grep -n '"heading":' templates/resume_hybrid_v1.json`
Expected output:
```
"heading": "Summary"
"heading": "Skills"
"heading": "Experience"
"heading": "Education"
"heading": "Certifications"
```

- [ ] **Step 4: Verify JSON is still valid**

Run: `python3 -c "import json; json.load(open('templates/resume_hybrid_v1.json'))" && echo "VALID"`
Expected: `VALID`

---

### Task 2: Update `context/specs/resume_hybrid_template_spec.md` (5 headings + DOC_ID + ATS_AUDIT)

**Files:**
- Modify: `context/specs/resume_hybrid_template_spec.md` (lines 5, 52, 54, 56, 69, 72, 80, 89)

- [ ] **Step 1: Replace DOC_ID in META (line 5)**

```
Old: DOC_ID: REPLACE_WITH_RESUME_HYBRID_GOLDEN_MASTER_DOC_ID
New: DOC_ID: 16FlPfFjHCYibECNtGORE-KEZtr1ogP_dRayo29L0y_I
```

This token appears twice in the file (META line 5 and REGISTRATION_FRAGMENT line 89). Use Edit with `replace_all: true`.

- [ ] **Step 2: Update STRUCTURE line 6 — SUMMARY**

```
Old: 6. [Heading 1] SUMMARY
New: 6. [Heading 1] Summary
```

- [ ] **Step 3: Update STRUCTURE line 8 — CORE COMPETENCIES**

```
Old: 8. [Heading 1] CORE COMPETENCIES
New: 8. [Heading 1] Skills
```

- [ ] **Step 4: Update STRUCTURE line 10 — PROFESSIONAL EXPERIENCE**

```
Old: 10. [Heading 1] PROFESSIONAL EXPERIENCE
New: 10. [Heading 1] Experience
```

- [ ] **Step 5: Update STRUCTURE line 23 — EDUCATION**

```
Old: 23. [Heading 1] EDUCATION
New: 23. [Heading 1] Education
```

- [ ] **Step 6: Update STRUCTURE line 26 — CERTIFICATIONS AND LICENSING**

```
Old: 26. [Heading 1] CERTIFICATIONS AND LICENSING
New: 26. [Heading 1] Certifications
```

- [ ] **Step 7: Fix fabricated ATS_AUDIT line 80**

```
Old: allowed_headings: PASS — Calibri only, consistent styles
New: allowed_headings: PASS — all 5 headings (Summary, Skills, Experience, Education, Certifications) in allowed_headings whitelist
```

- [ ] **Step 8: Verify all changes**

Run: `grep -nE 'DOC_ID|\[Heading 1\]|allowed_headings' context/specs/resume_hybrid_template_spec.md`

Expected output (paraphrased — exact line numbers may shift if file length changed):
- DOC_ID line shows real Doc ID
- 5 `[Heading 1]` lines show: `Summary`, `Skills`, `Experience`, `Education`, `Certifications`
- allowed_headings line shows the corrected PASS message
- REGISTRATION_FRAGMENT `template_doc_id` shows real Doc ID

Run: `grep -c REPLACE_WITH_RESUME_HYBRID_GOLDEN_MASTER_DOC_ID context/specs/resume_hybrid_template_spec.md`
Expected: `0`

---

### Task 3: Cross-artefact consistency check

- [ ] **Step 1: Confirm JSON and spec headings agree**

Run:
```bash
echo "=== JSON headings ===" && grep '"heading":' templates/resume_hybrid_v1.json
echo "=== Spec headings ===" && grep '\[Heading 1\]' context/specs/resume_hybrid_template_spec.md
```

Both must list (in order): Summary, Skills, Experience, Education, Certifications. Stop here if mismatched.

- [ ] **Step 2: Confirm allowed_headings whitelist coverage**

Run: `python3 -c "import json; rules=json.load(open('config/ats_rules.json')); print(rules.get('allowed_headings'))"`
Confirm output includes all 5 of: Summary, Skills, Experience, Education, Certifications. (Expected: `['Summary', 'Skills', 'Experience', 'Education', 'Certifications', 'Key Achievements']`)

---

### Task 4: Commit Workstream A

- [ ] **Step 1: Stage and commit**

```bash
git add templates/resume_hybrid_v1.json context/specs/resume_hybrid_template_spec.md
git commit -m "$(cat <<'EOF'
fix(resume-hybrid): normalise all 5 section headings to ATS allowed_headings whitelist

Rename SUMMARY/PROFESSIONAL SUMMARY → Summary, CORE COMPETENCIES/CORE SKILLS → Skills,
PROFESSIONAL EXPERIENCE/WORK EXPERIENCE → Experience, EDUCATION → Education,
CERTIFICATIONS AND LICENSING/CERTIFICATIONS → Certifications across JSON theme and
Markdown spec. Replace placeholder DOC_ID with real Golden Master ID. Fix fabricated
ATS_AUDIT allowed_headings line.

Live Google Doc 16FlPfFjHCYibECNtGORE-KEZtr1ogP_dRayo29L0y_I must be manually updated
to match (user action) — atomic with this commit.

Spec: docs/superpowers/specs/2026-05-27-session-status-and-next-steps-design.md § Task 1
EOF
)"
```

- [ ] **Step 2: Verify commit**

Run: `git log -1 --stat`
Expected: 2 files changed in the diff.

---

### Task 5: User manual action — Google Doc heading rename

This task is performed by the user, not the agent. The agent must STOP and present instructions, then wait.

- [ ] **Step 1: Present instructions to user**

Message to user (verbatim):

> Workstream A code changes committed. Please now open Google Doc `16FlPfFjHCYibECNtGORE-KEZtr1ogP_dRayo29L0y_I` and rename all 5 section headings:
>
> - `SUMMARY` (or `PROFESSIONAL SUMMARY`) → `Summary`
> - `CORE COMPETENCIES` (or `CORE SKILLS`) → `Skills`
> - `PROFESSIONAL EXPERIENCE` (or `WORK EXPERIENCE`) → `Experience`
> - `EDUCATION` → `Education`
> - `CERTIFICATIONS AND LICENSING` (or `CERTIFICATIONS`) → `Certifications`
>
> Each must remain styled as **Heading 1** (not bolded Normal text). Reply when done so I can proceed to Workstream B.

- [ ] **Step 2: Wait for user confirmation**

Do not proceed to Workstream B until user confirms manual edit complete.

- [ ] **Step 3: Update TASKS.md** — mark TASK-001 complete

Edit `TASKS.md`: move TASK-001 from `## Active` to `## Completed`, change all `- [ ]` to `- [x]`, append `(YYYY-MM-DD)` to title with today's date.

```bash
git add TASKS.md && git commit -m "chore(tasks): mark TASK-001 hybrid heading rename complete"
```

---

## Workstream B — TASK-002: KSC v2 end-to-end validation

**Gate:** Do not begin Workstream B until Task 5 user confirmation received.

### Task 6: Generate KSC v2 Markdown spec

**Files:**
- Create: `context/specs/ksc_standard_v2_spec.md`

**Skill to invoke:** `gold_template_builder_v3` (definition at `agent_skills/gold_template_builder_v3/SKILL.md`)

- [ ] **Step 1: Read the skill definition**

Run: `Read agent_skills/gold_template_builder_v3/SKILL.md`
Note the required output shape (`ksc_template_spec_form.md`) and the META/TOKENS_USED/STRUCTURE/ATS_AUDIT/REGISTRATION_FRAGMENT/DRY_RUN_CMD sections it must produce.

- [ ] **Step 2: Read existing v1 KSC for context (do not copy)**

Run: `Read templates/ksc_base_v1.json` to understand the current block structure (name_header, contact_info, application_meta, criteria_responses per THEME_SPEC_GUIDE.md).

- [ ] **Step 3: Read the design spec for KSC v2**

Run: `Read context/specs/2026-05-25-ksc-anti-slop-skill-v2-design.md`
This documents what v2 is supposed to produce differently from v1 (anti-slop guardrails).

- [ ] **Step 4: Produce the Markdown spec**

Write to `context/specs/ksc_standard_v2_spec.md`. The spec MUST contain these sections (per ksc_template_spec_form):
- `## META` — TEMPLATE_TYPE: ksc, VARIANT: standard, DOC_ID: REPLACE_AT_BUILD_TIME, TARGET_SECTOR
- `## TOKENS_USED` — every `{{TOKEN}}` mapped to source `generate_document.py:LINE`
- `## STRUCTURE` — numbered, `[Heading X]` style annotations
- `## ATS_AUDIT` — PASS/FAIL evidence per rule (NO fabrication — every PASS must cite the actual constraint satisfied)
- `## REGISTRATION_FRAGMENT` — JSON snippet for `config/doc_templates.json`
- `## DRY_RUN_CMD` — exact `generate_document.py` invocation

- [ ] **Step 5: Verify file exists**

Run: `wc -l context/specs/ksc_standard_v2_spec.md`
Expected: non-zero line count.

---

### Task 7: Validate the spec with `validate_template_spec.py` (HARD GATE)

- [ ] **Step 1: Run validator**

Run: `python3 tools/validate_template_spec.py context/specs/ksc_standard_v2_spec.md`

- [ ] **Step 2: Inspect output**

Expected on success: final line `SPEC OK` (exit 0).
On failure: one or more `FAIL` lines with rule numbers. Read them all.

- [ ] **Step 3: If FAIL — iterate**

For each `FAIL` line:
1. Identify the rule cited
2. Re-read the relevant section of `context/specs/ksc_standard_v2_spec.md`
3. Edit the spec to address the failure (do NOT modify the validator)
4. Re-run Step 1

Loop until validator returns `SPEC OK`. Do not proceed past this gate on a FAIL.

- [ ] **Step 4: Commit validated spec**

```bash
git add context/specs/ksc_standard_v2_spec.md
git commit -m "feat(ksc): add validated v2 standard spec (passes validate_template_spec.py)"
```

---

### Task 8: Translate validated spec → JSON theme

**Files:**
- Create: `templates/ksc_standard_v2.json`
- Reference: `templates/THEME_SPEC_GUIDE.md`, `templates/ksc_base_v1.json` (structural reference only)

- [ ] **Step 1: Read THEME_SPEC_GUIDE.md**

Run: `Read templates/THEME_SPEC_GUIDE.md`
Confirm the block schema (block_id, type, order, tokens, content, visualConfig) and the KSC-specific block list (`name_header`, `contact_info`, `application_meta`, `criteria_responses`).

- [ ] **Step 2: Read v1 theme as structural reference**

Run: `Read templates/ksc_base_v1.json`
Use as a starting structural template — do NOT copy content verbatim. v2 may differ in tokens, palette, typography per the validated spec.

- [ ] **Step 3: Write `templates/ksc_standard_v2.json`**

Required top-level fields (per THEME_SPEC_GUIDE.md):
- `schema_version`: `"2.0"`
- `template_id`: `"ksc_standard_v2"`
- `doc_type`: `"ksc"`
- `placeholder_schema`: `"PLACEHOLDER_SCHEMA_V2"`
- `ats_constraints`, `palette`, `typography`, `page`, `blocks`

Each block in `blocks[]` must mirror the STRUCTURE order from the validated Markdown spec. Tokens in JSON must match exactly the TOKENS_USED list in the spec.

- [ ] **Step 4: Verify JSON is valid**

Run: `python3 -c "import json; json.load(open('templates/ksc_standard_v2.json'))" && echo "VALID"`
Expected: `VALID`

- [ ] **Step 5: Verify token parity between spec and JSON**

Run:
```bash
echo "=== Spec tokens ===" && grep -oE '\{\{[A-Z_0-9]+\}\}' context/specs/ksc_standard_v2_spec.md | sort -u
echo "=== JSON tokens ===" && grep -oE '\{\{[A-Z_0-9]+\}\}' templates/ksc_standard_v2.json | sort -u
```
Both lists must be identical. If divergent, reconcile (spec is source of truth — fix the JSON).

---

### Task 9: Build the Golden Master Google Doc

- [ ] **Step 1: Run the builder**

Run: `python3 tools/build_golden_master.py templates/ksc_standard_v2.json`

- [ ] **Step 2: Capture Doc ID from output**

The script prints the Doc ID on success. Record it (call it `<KSC_V2_DOC_ID>` for the rest of the plan).

- [ ] **Step 3: Verify Doc accessible**

Open `https://docs.google.com/document/d/<KSC_V2_DOC_ID>/edit` in browser (or report URL to user for verification). Confirm the document exists and contains the unfilled `{{TOKEN}}` placeholders from the spec.

- [ ] **Step 4: Stop if build_golden_master.py failed**

If the script errors (Google Drive auth, API quota, JSON parse, etc.), do NOT proceed. Surface the error to the user and resolve before continuing.

---

### Task 10: Register the new Doc ID in `config/doc_templates.json`

**Files:**
- Modify: `config/doc_templates.json` (lines 26-29 — the `ksc` block)

**Decision:** Replace `ksc.template_doc_id` and `ksc.theme` in-place (no variants block). Rationale: v1 ksc_base was never validated and is being superseded — there is no v1 to retain. `generate_document.py:216` resolves via `template_doc_id` fallback when no variants block exists, so this is the simplest valid registration.

- [ ] **Step 1: Edit the file**

```
Old:
  "ksc": {
    "template_doc_id": "1mZ8OSphGNvot6Y3NSp3Ix0UdZdSP3MP1zf4LY8o9bVM",
    "theme": "templates/ksc_base_v1.json"
  },

New:
  "ksc": {
    "template_doc_id": "<KSC_V2_DOC_ID>",
    "theme": "templates/ksc_standard_v2.json"
  },
```

Substitute `<KSC_V2_DOC_ID>` with the actual ID captured in Task 9 Step 2.

- [ ] **Step 2: Verify JSON valid**

Run: `python3 -c "import json; json.load(open('config/doc_templates.json'))" && echo "VALID"`
Expected: `VALID`

- [ ] **Step 3: Commit**

```bash
git add templates/ksc_standard_v2.json config/doc_templates.json
git commit -m "feat(ksc): register validated v2 Golden Master and JSON theme"
```

---

### Task 11: Dry-run verification

- [ ] **Step 1: Prepare a test criteria file**

Run: `ls source_docs/ksc/` to find an existing criteria file. If none suitable exists, ask user for a sample criteria text file path. Call this `<CRITERIA_FILE>`.

- [ ] **Step 2: Run dry-run**

Run:
```bash
python3 tools/generate_document.py --type ksc --target "Test Role at Test Org" --criteria <CRITERIA_FILE> --dry-run
```

- [ ] **Step 3: Inspect output**

Expected: the dry-run prints the resolved token map (every `{{TOKEN}}` from the spec mapped to a value drawn from `database/ksc_curated.json` / pipeline output). No exceptions. No `KeyError` on tokens.

- [ ] **Step 4: Stop if any token unresolved**

If the dry-run shows unresolved tokens or missing builder logic, the JSON theme may be referencing tokens the `_build_ksc_values` function in `tools/generate_document.py` does not produce. Surface the gap to the user — do NOT silently extend `generate_document.py` (out of scope per design spec).

---

### Task 12: Live KSC generation

- [ ] **Step 1: Run live generation**

Run:
```bash
python3 tools/generate_document.py --type ksc --target "Test Role at Test Org" --criteria <CRITERIA_FILE>
```

- [ ] **Step 2: Capture generated Doc URL**

The script prints the URL of the new Google Doc on success.

- [ ] **Step 3: Inspect generated Doc**

Open the URL. Verify:
1. All `{{TOKEN}}` placeholders are resolved (no literal `{{...}}` remaining)
2. Formatting matches the spec STRUCTURE (correct heading levels, no forbidden glyphs from `ats_rules.json`)
3. No empty sections from unbound tokens

- [ ] **Step 4: Present URL to user**

Message: "Live KSC generation produced `<URL>` — please inspect and confirm before I mark the v2 design as Approved."

- [ ] **Step 5: Wait for user approval**

Do not proceed to Task 13 until user confirms output is acceptable.

---

### Task 13: Mark design spec as Approved

**Files:**
- Modify: `context/specs/2026-05-25-ksc-anti-slop-skill-v2-design.md` (status line near top)

- [ ] **Step 1: Read current status line**

Run: `grep -n "Status:" context/specs/2026-05-25-ksc-anti-slop-skill-v2-design.md | head -3`
Identify the line containing `Draft — awaiting user review` or similar.

- [ ] **Step 2: Update status**

```
Old: Status: Draft — awaiting user review
New: Status: Approved — validated end-to-end 2026-05-27
```

(Substitute today's date if different.)

- [ ] **Step 3: Update TASKS.md**

Mark TASK-002 complete: move from `## Active` to `## Completed`, change checkboxes to `[x]`, append today's date to title.

- [ ] **Step 4: Commit**

```bash
git add context/specs/2026-05-25-ksc-anti-slop-skill-v2-design.md TASKS.md
git commit -m "$(cat <<'EOF'
chore: mark KSC v2 design Approved after end-to-end validation

Validated flow: gold_template_builder_v3 → ksc_standard_v2_spec.md → validate_template_spec.py
(SPEC OK) → ksc_standard_v2.json → build_golden_master.py → config registration → dry-run
→ live generation → user-approved output.

Closes TASK-002.
EOF
)"
```

---

## Final state

After both workstreams complete:
- `templates/resume_hybrid_v1.json`, `context/specs/resume_hybrid_template_spec.md`, and live Doc `16FlPfFjHCYibECNtGORE-...` all use the 5 compliant heading names
- `context/specs/ksc_standard_v2_spec.md` exists and passes `validate_template_spec.py`
- `templates/ksc_standard_v2.json` exists and is the registered theme for the `ksc` doc type
- A new validated KSC Golden Master Google Doc replaces the v1 doc in `config/doc_templates.json`
- One live KSC generation has been produced and user-approved
- `context/specs/2026-05-25-ksc-anti-slop-skill-v2-design.md` is marked Approved
- `TASKS.md` shows TASK-001 and TASK-002 in the Completed section
