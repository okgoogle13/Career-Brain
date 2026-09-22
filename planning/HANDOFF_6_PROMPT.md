# HANDOFF 6 — TASK-006 Stage 2 Close-Out (Execution Brief)

**Prepared:** 2026-09-22 · **For:** an execution agent with no prior context
**Repo:** `/Users/okgoogle13/Projects/Career-Brain`
**Python:** always `.venv/bin/python`. Never bare `python3`, never system Python.

> Read `CLAUDE.md` and `TASKS.md` before starting.
> All diagnostics in the Findings section below were run offline on 2026-09-22.
> **No live Google API call has been made.** Phase 0 is therefore blocking.

---

## 1. Your objective

Three Golden Masters fail their gates and block BS-2.1 (ATS QA audit):

| Build Spec | Template | Current Doc ID | Failure |
|---|---|---|---|
| BS-1.4 | `templates/cover_letter_government_v1.json` | `1ZZI4zb2aB6SPnFWzfrsQvto86eOk7BG9Mx_kjVNRObI` | `audit_doc_style.py` FAIL |
| BS-1.5 | `templates/cover_letter_nfp_v1.json` | `1a-JfEX2p5AZFFK6rZSj9qiLU23i5u4a_NG1WudQ9D54` | `audit_doc_style.py` FAIL |
| BS-1.6 | `templates/ksc_standard_v2.json` | `1pGTQ65rrsYpqi1TC7zI-DjO5v9LVurO6JZOLJONW_C4` | `verify_golden_master.py` (color-on-all: False) **+** `audit_doc_style.py` FAIL |

Get all three to `STYLE OK`, re-register them, then reassess BS-2.1.

## 2. Rules of engagement

- **`[GATE 4]`** marks any command that creates or mutates a live Google Doc. **Stop and wait for
  explicit user approval before each one.** Do not batch gates.
- Always `--dry-run` before a live build. It is offline and free.
- Do not edit `TASKS.md` until Phase 4 passes. The diff is in the Appendix.
- Do not run `validate_template_spec.py` expecting it to help — see F7.

---

## 3. Findings — read before touching anything

### F1 — Editing template JSON cannot fix the style audit ⚠️ REFUTES THE ORIGINAL BRIEF

`audit_doc_style.py:135` imports `build_paragraphs` from `build_golden_master.py`. The two
style-resolution blocks — `build_golden_master.py:203-261` and `audit_doc_style.py:212-270` — are
identical branch-for-branch: same `get_block` lookups, same fallback dicts, same font routing, same
`heading_font` fallback.

**The audit compares a live Doc against what the current builder would produce from the same
template.** A template edit moves both sides of the comparison equally and cannot change the verdict.

`TASKS.md:59` records the prescription *"Fix templates and rebuild"*. **That prescription is wrong.**
Only two things can produce a FAIL:

- **(a)** the live Doc was built by a different builder/template revision than what is on disk, or
- **(b)** Google Docs normalised away a style delta the auditor still demands.

Fixes live in `build_golden_master.py`, or in rebuilding. Not in `templates/`.

### F2 — The `heading_font_family` hypothesis is false

`heading_font_family` is absent from all three failing templates **and** from
`resume_chronological_v1.json`, which passes. It exists on only a subset of resume themes. Builder
and auditor both fall back to `typography.base_font` identically (`build_golden_master.py:138`,
`audit_doc_style.py:173`). Not the cause. Do not pursue it.

### F3 — KSC: confirmed builder bug, `h1`/`h2` role mismatch

`build_paragraphs:124` tags KSC criterion headings `role="h1"`. But the KSC-specific style values —
`criteria_responses.visualConfig.criterion_text` (12pt, `#2F855A` green, `border_bottom`) — are only
reachable from the `h2` branch (`build_golden_master.py:229`, `audit_doc_style.py:238`). The local
`ksc_cv` is computed at line 168 and never read.

`ksc_standard_v2.json` has **no `summary_section` block**, so `h1_vc` falls back to the hardcoded
`{"font_size_pt": 14, "font_color": "#000000"}`. Criterion headings therefore render black 14pt
instead of green 12pt. `criterion_text` visualConfig is dead config.

KSC-only: cover letters emit no `h1` paragraphs at all. **This is verified from source and safe to
fix regardless of what Phase 0 returns.**

### F4 — Every rebuild produces a NEW Doc ID

`build_golden_master.py:391` calls `drive_service.files().create()`. There is **no in-place update
path**. Rebuilding orphans the old Doc in Drive and invalidates the IDs in
`config/doc_templates.json`, whose own `_note` says `template_revision` must be bumped on any
rebuild. Phase 3 exists for this. Skipping it leaves document generation pointed at the old broken
masters.

### F5 — Expected paragraph counts (from `--dry-run`, verified offline)

| Template | Expected non-empty paragraphs |
|---|---|
| `ksc_standard_v2.json` | **42** (`max_criteria: 6` × 6 paragraphs + 6 header) |
| `cover_letter_government_v1.json` | **14** |
| `cover_letter_nfp_v1.json` | **14** |

`audit_doc_style.py:193` checks this count *first*. A mismatch misaligns the `zip` at line 200 and
cascades bogus FAILs across every following paragraph. This is the single discriminating diagnostic.

### F6 — Open question: `color-on-all: False`

Unresolved, and **do not assume it shares a cause with the style FAILs** — `audit_doc_style.py`
never inspects `foregroundColor`. Two candidates:

1. Google dropped the colour override entirely (plausible where the builder writes `#000000` onto a
   HEADING_1 whose inherited colour is already black — see F3).
2. Non-blank runs exist outside the builder's styled ranges (Doc edited, or built by an older
   builder).

Note: proto3 omits zero values, so a *persisted* black override returns
`foregroundColor: {color: {rgbColor: {}}}` — still truthy, so `verify_golden_master.py:78` would
pass. Only a total drop (1) or stray runs (2) explain the observed `False`.

### F7 — Distractor, do not fix here

`validate_template_spec.py --batch` validates **markdown specs in `context/specs/`**, not the JSON
templates, and currently checks `resume_template_spec.md` against KSC rules (rule8: *"missing
top-level 'ksc' key"*; rule9: *"No KSC_CRITERION_N_TEXT tokens"*). Pre-existing and unrelated to
TASK-006. Log it; do not fix it in this task.

---

## Phase 0 — Capture live data (BLOCKING, must be user-run)

This cannot run from an agent sandbox: the OAuth refresh writes `token.json` at the repo root,
outside the write allowlist. Confirmed failure: `Operation not permitted: .../token.json`.

**Ask the user to run these three in the Claude Code prompt using the `!` prefix**, so the output
lands in the conversation:

```
! cd ~/Projects/Career-Brain && .venv/bin/python tools/audit_doc_style.py 1ZZI4zb2aB6SPnFWzfrsQvto86eOk7BG9Mx_kjVNRObI --theme templates/cover_letter_government_v1.json 2>&1 | head -40
```
```
! cd ~/Projects/Career-Brain && .venv/bin/python tools/audit_doc_style.py 1a-JfEX2p5AZFFK6rZSj9qiLU23i5u4a_NG1WudQ9D54 --theme templates/cover_letter_nfp_v1.json 2>&1 | head -40
```
```
! cd ~/Projects/Career-Brain && .venv/bin/python tools/audit_doc_style.py 1pGTQ65rrsYpqi1TC7zI-DjO5v9LVurO6JZOLJONW_C4 --theme templates/ksc_standard_v2.json 2>&1 | head -40
```

These are read-only Docs `.get()` calls — safe, no gate required.

**Read the first FAIL line of each output and branch:**

| First FAIL line | Meaning | Branch |
|---|---|---|
| `Paragraph count mismatch … expected 42 / 14 / 14` | Doc predates the current builder/template (F1a) | **Branch A** — rebuild is the entire fix; skip Phase 1.2 |
| Anything else (font, size, spacing, named style) | Genuine builder↔Docs divergence (F1b) | **Branch B** — fix the named divergence in Phase 1.2 first |

**Do not proceed past Phase 0 without this output.** Phase 1.2's scope is unknown until you have it.

---

## Phase 1 — Code fix in `build_golden_master.py`

### 1.1 KSC criterion heading routing (F3) — required in both branches

**Decided by the user on 2026-09-22: take the one-line fix and drop the criterion bottom rule.**

Edit `tools/build_golden_master.py:124`, inside the `doc_type == "ksc"` branch:

```python
# before
add(f"{{{{KSC_CRITERION_{c}_TEXT}}}}", "HEADING_1", bold=True, role="h1")
# after
add(f"{{{{KSC_CRITERION_{c}_TEXT}}}}", "HEADING_1", bold=True, role="h2")
```

One edit only. Because `audit_doc_style.py` imports `build_paragraphs`, the auditor picks the change
up automatically and the two files stay consistent.

**Known, accepted trade-off:** the `h2` branch has no `border_bottom` handling (only `h1` does, at
`build_golden_master.py:286-307`), so `criterion_text.border_bottom` (`#C6F6D5`, 1.0pt) will not
render. This is intended.

Because of that, also make the template honest — delete the now-unreachable key:

`templates/ksc_standard_v2.json` → `criteria_responses.visualConfig.criterion_text.border_bottom`

This is documentation accuracy, not a fix; per F1 it has no effect on the audit. It is the **only**
sanctioned edit under `templates/` in this task.

> **Rejected alternative, recorded so it is not re-litigated:** extending the `h1` branch with a
> `doc_type == "ksc"` check would preserve the border, but requires byte-identical edits in *both*
> `build_golden_master.py:223-227` and `audit_doc_style.py:232-236`. If the border is ever demanded
> back, that is the route — not a template edit.

**Verify (offline, no API):**

```bash
cd ~/Projects/Career-Brain && .venv/bin/python tools/build_golden_master.py templates/ksc_standard_v2.json --dry-run | python3 -c "
import json,sys
d=json.load(sys.stdin)
print('paragraph_count:', d['paragraph_count'])
for r in d['style_requests']:
    ts=r.get('updateTextStyle')
    if ts and abs(ts['textStyle']['fontSize']['magnitude']-12.0)<0.01:
        print('12pt run colour:', ts['textStyle']['foregroundColor']); break
"
```

Expected: `paragraph_count: 42`, and an `rgbColor` matching `#2F855A`
(≈ `{'red': 0.1843…, 'green': 0.5216…, 'blue': 0.3765…}`).

### 1.2 Branch B only — fix whatever Phase 0 named

Apply the minimal change in `build_golden_master.py` that makes the builder emit what the Doc needs.
If the divergence is in the auditor's *expectation* rather than the builder's output, mirror the
change at the matching line in `audit_doc_style.py` and leave a comment naming the paired line, so
the next reader knows the two must move together.

**Do not edit `templates/` to chase the audit.** Per F1 that cannot change the verdict; per F2 the
suspected missing field is not missing.

---

## Phase 2 — Rebuild the three masters `[GATE 4]`

Dry-run each first and confirm `paragraph_count` is **14 / 14 / 42**. Then, **one gate at a time,
waiting for user approval before each**:

```
[GATE 4] cd ~/Projects/Career-Brain && .venv/bin/python tools/build_golden_master.py templates/cover_letter_government_v1.json
[GATE 4] cd ~/Projects/Career-Brain && .venv/bin/python tools/build_golden_master.py templates/cover_letter_nfp_v1.json
[GATE 4] cd ~/Projects/Career-Brain && .venv/bin/python tools/build_golden_master.py templates/ksc_standard_v2.json
```

Each prints a **new Doc ID** as the last line of stdout. Record all three verbatim — Phase 3 needs
them and they cannot be recovered from the tool.

---

## Phase 3 — Re-register the new Doc IDs (mandatory, F4)

Edit `config/doc_templates.json`:

| JSON path | New value |
|---|---|
| `cover_letter.variants.government.template_doc_id` | new gov CL ID |
| `cover_letter.variants.nfp.template_doc_id` | new NFP CL ID |
| `ksc.template_doc_id` | new KSC ID |
| `…template_revision` (those three entries) | `2026-09-22` |
| `_version` | `2026-09-22` |

**Verify:**

```bash
cd ~/Projects/Career-Brain && python3 -c "
import json
d=json.load(open('config/doc_templates.json'))
v=d['cover_letter']['variants']
for k,e in [('gov',v['government']),('nfp',v['nfp']),('ksc',d['ksc'])]:
    print(k, e['template_doc_id'], e['template_revision'])
"
```

Expected: three new IDs, all revisions `2026-09-22`.

The three superseded Docs are now orphaned in Drive. **Leave them** — flag them to the user for
manual cleanup rather than deleting programmatically.

---

## Phase 4 — Verification

Run against the **new** IDs from Phase 2.

```bash
cd ~/Projects/Career-Brain
.venv/bin/python tools/audit_doc_style.py <NEW_GOV_ID> --theme templates/cover_letter_government_v1.json
.venv/bin/python tools/audit_doc_style.py <NEW_NFP_ID> --theme templates/cover_letter_nfp_v1.json
.venv/bin/python tools/audit_doc_style.py <NEW_KSC_ID> --theme templates/ksc_standard_v2.json
```

Expected each: `STYLE OK`, exit 0.

```bash
.venv/bin/python tools/verify_golden_master.py <NEW_KSC_ID> --base-font=Calibri
```

Expected: `no-empty-textStyle: True | color-on-all: True`, `VERDICT: PASS`, exit 0.

**If `color-on-all` is still False** (F6), the cause is mechanism 2 — runs outside the styled ranges.
Compare `runs total` against `non-blank` in the output and against the expected 42; the gap names the
offending paragraphs. This is a *separate* defect from the style audit. Do not block Phase 5 on it
without re-reading F6, and do not silently mark BS-1.6 complete while it fails.

---

## Phase 5 — BS-2.1 ATS QA gate

**Scope warning — three × `STYLE OK` is NOT BS-2.1.** `TASKS.md:58` additionally requires: all
placeholders present, no unknown placeholders, no inline objects, no layout tables, no text boxes,
contact in body.

`audit_doc_style.py` covers only **inline objects** (line 459) and **tables** (line 454).
Placeholder presence, unknown-placeholder detection, text boxes and contact-in-body are **not
checked by any tool reviewed during planning**. Before closing BS-2.1, either locate the tool that
covers those four, or state plainly in `TASKS.md` that they are unverified. Do not tick BS-2.1 on the
strength of the style audit alone.

**BS-7.5 slop check** cannot run against a Golden Master. The masters contain only `{{PLACEHOLDER}}`
tokens, so `check_voice_slop.py` would score nothing. It needs a document produced through
`generate_document.py` with real narrative content — a further `[GATE 4]`. Either generate one test
document or defer BS-7.5 and say which.

---

## Appendix — Proposed `TASKS.md` diff

Apply **only** after Phase 4 passes. Not to be applied inline during execution.

```diff
-- [ ] BS-1.4 — Build Golden Master: Cover Letter (Government) ...
+- [x] BS-1.4 — Build Golden Master: Cover Letter (Government) ... *(rebuilt 2026-09-22, new Doc ID <NEW_GOV_ID>; STYLE OK)*

-- [ ] BS-1.5 — Build Golden Master: Cover Letter (NFP) ...
+- [x] BS-1.5 — Build Golden Master: Cover Letter (NFP) ... *(rebuilt 2026-09-22, new Doc ID <NEW_NFP_ID>; STYLE OK)*

-- [ ] BS-1.6 — Verify KSC Golden Master ...
+- [x] BS-1.6 — Verify KSC Golden Master ... *(criterion headings were routed to role "h1", bypassing criteria_responses.visualConfig.criterion_text; fixed in build_golden_master.py:124. border_bottom dropped by decision. Rebuilt 2026-09-22, new Doc ID <NEW_KSC_ID>; STYLE OK + verify PASS)*

-  - ❌ **FAILED (2026-09-22):** `audit_doc_style.py` was run live and failed on all 3 active Golden Masters (BS-1.4, 1.5, 1.6). Fix templates and rebuild.
+  - ✅ **RESOLVED (2026-09-22):** Root cause was NOT template fields. `audit_doc_style.py` imports `build_paragraphs` from `build_golden_master.py`, so template edits move both sides of the comparison and cannot change the verdict. Fix was in the builder + rebuild. All 3 masters re-registered in `config/doc_templates.json` (revision 2026-09-22).
```

New defects to log separately:

```
- [ ] `validate_template_spec.py --batch` applies KSC rules (rule8, rule9) to
      `context/specs/resume_template_spec.md`. Pre-existing; unrelated to TASK-006. (F7)
- [ ] `build_golden_master.py` has no in-place rebuild path — every run creates a new Drive
      doc and orphans the old one. Consider an `--update <doc_id>` flag. (F4)
```

---

## Known limitations of this brief

- **Phase 0 is blocking and was not run.** If the CL audits fail on something other than paragraph
  count, Phase 1.2 is unspecified work of unknown size.
- **F6 is unresolved.** The `color-on-all: False` mechanism is a hypothesis, not a finding.
- **F3 is verified from source** and is the one fix that does not depend on live data.
- **Assumed:** OAuth credentials at `credentials.json` / `token.json` are valid, and the user can
  complete a browser consent flow if the refresh fails.
