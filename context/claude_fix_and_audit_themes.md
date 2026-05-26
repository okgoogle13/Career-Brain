# Career Brain — Theme Fix, Audit & Warm Impact Registration
> Target model: Claude Code (Plan Mode)
> Extended thinking: ON
> Execution mode: Sequential — no parallel subagents. API calls are quota-sensitive.
> AGENTS.md gate: This task touches `doc_templates/` JSON specs and `doc_templates.json` only.
> No pipeline scripts (`normalize_vault.py`, `compile_brain.py`, etc.) are touched.

---

## 0. Read These Before Planning

You MUST read the following files in full before creating your plan:

1. `AGENTS.md` — gatekeeper protocol and coding conventions
2. `skills/docs_style_auditor/SKILL.md` — the mechanical style audit protocol you will follow
3. `skills/ats_template_qa_v2/SKILL.md` — the two-stage QA protocol you will follow
4. `doc_templates/THEME_SPEC_GUIDE.md` — source of truth for block schemas and visual rules
5. `doc_templates.json` — current registry (9 themes, all unique Doc IDs)
6. `build_golden_master.py` — read-only reference; you will NOT modify it except for Bug Fix A and Bug Fix B below

Do NOT begin planning until you have read all six.

---

## 1. Background

An Antigravity audit session identified the following gaps in the 9-theme Career Brain template library. Your job is to fix them, then run the custom skills to verify every template is compliant before declaring done.

---

## 2. Fixes Required

Work through these in order. **Do not skip to verification until all fixes are applied.**

---

### Fix 1 — KSC builder: criterion heading colour not applied  
**File:** `build_golden_master.py`  
**Severity:** 🔴 High — criterion headings in the KSC Golden Master render in default black, not Forest Green.

**Root cause:** In `build_paragraphs()`, KSC criteria headings are emitted with `role="h2"`. In `build_requests()`, the `h2` role reads colour from `exp_block["visualConfig"]["role_title"]["font_color"]` (the *experience_section*) — but for a KSC doc, `exp_block` is `None` (no experience section exists), so the fallback default `#000000` is used.

**Fix:** In `build_requests()`, add a branch: when `doc_type == "ksc"` and `role == "h2"`, read `font_color` from the `criteria_responses` block's `visualConfig.criterion_text.font_color` instead of `ev["role_title"]`.

Pseudocode:
```python
elif role == "h2":
    if doc_type == "ksc":
        ksc_block = get_block("criteria_responses")
        ksc_cv = ksc_block["visualConfig"]["criterion_text"] if ksc_block else {}
        font_size = ksc_cv.get("font_size_pt", 12)
        color = ksc_cv.get("font_color", "#000000")
        space_below = ksc_cv.get("margin_top_pt", 14)
    else:
        rt = ev.get("role_title", {})
        font_size = rt.get("font_size_pt", 12)
        color = rt.get("font_color", "#000000")
        space_below = rt.get("margin_top_pt", 8.0)
    line_spacing = 115
```

---

### Fix 2 — KSC builder: max_criteria hardcoded at 3  
**File:** `build_golden_master.py`  
**Severity:** 🔴 High — AU public service KSCs run 4–6 criteria; `range(1, 4)` always caps at 3.

**Fix:** In `build_paragraphs()`, replace:
```python
for c in range(1, 4):
```
with:
```python
criteria_block = next(
    (b for b in theme.get("blocks", []) if b["block_id"] == "criteria_responses"), {}
)
max_criteria = criteria_block.get("max_criteria", 3)
for c in range(1, max_criteria + 1):
```

---

### Fix 3 — Remove unimplemented `accent_bar` field from warm_impact spec  
**File:** `doc_templates/resume_warm_impact_v1.json`  
**Severity:** 🟡 Medium — `build_golden_master.py` has no code path for `accent_bar`. The field is silently ignored at build time, creating a gap between spec and output.

**Fix:** Remove the `accent_bar` sub-object from `summary_section.visualConfig.body`. Keep all other fields in that block unchanged. After removal the `body` key should read:
```json
"body": {
  "font_size_pt": 11.5,
  "font_color": "#1A1A1A",
  "line_spacing": 1.3
}
```

---

### Fix 4 — Differentiate `chronological` from `professional_classic` visually  
**File:** `doc_templates/resume_chronological_v1.json`  
**Severity:** 🟡 Medium — these two themes share identical font, palette, and rule style. A selector cannot distinguish them.

**Fix:** In `resume_chronological_v1.json`, change section heading colours from Deep Navy `#1A365D` to Charcoal `#2D3748` in every heading `visualConfig` block (`summary_section`, `skills_section`, `experience_section`, `education_section`, `certifications_section`). Keep the `name_header` colour as `#1A365D` (Navy name, Charcoal section headings = clear visual hierarchy different from `professional_classic`). Also change `name_header.border_bottom.color` to `#2D3748` to match the new heading theme.

**Do not change** the palette keys — only the `font_color` values inside `visualConfig` blocks.

---

### Fix 5 — Add `border_bottom` to `cover_letter_government` name block  
**File:** `doc_templates/cover_letter_government_v1.json`  
**Severity:** 🟢 Low — structural inconsistency vs the Forest Green resume family.

**Fix:** Add to `name_header.visualConfig`:
```json
"border_bottom": {
  "color": "#2F855A",
  "width_pt": 0.5,
  "style": "solid"
}
```

---

### Fix 6 — Change `cover_letter_private` name colour to Teal  
**File:** `doc_templates/cover_letter_private_v1.json`  
**Severity:** 🟢 Low — name is Slate `#4A5568` but the paired `modern_minimalist` resume uses Teal `#38B2AC` for its role headline. The cover letter should echo the same palette energy.

**Fix:** In `name_header.visualConfig`, change `font_color` from `#4A5568` to `#38B2AC`.

---

### Fix 7 — Update stale `THEME_SPEC_GUIDE.md` content  
**File:** `doc_templates/THEME_SPEC_GUIDE.md`  
**Severity:** 🟢 Low — two stale sections mislead future theme authors.

**Fix A:** Replace lines 213–220 (the section "Relationship to `audit_doc_style.py`") with:

```markdown
## Relationship to `audit_doc_style.py`

`audit_doc_style.py` supports `--theme <path>` and loads font family, font sizes, line spacing,
and colour expectations directly from the theme JSON. Pass `--theme` for every themed Golden
Master audit. Unthemed/KSC templates are audited without the flag (Calibri defaults apply).

See `skills/docs_style_auditor/SKILL.md` for the full protocol.
```

**Fix B:** Update the "Current Theme Library" table in Section 1 to include all 9 registered themes (add `chronological`, `hybrid`, `contemporary_professional` as three existing rows; add the four cover letter entries; add the KSC entry; add `warm_impact` with status "orphan — build pending").

---

### Fix 8 — Build and register the `warm_impact` Golden Master  
**Files:** `doc_templates.json`, Google Docs API  
**Severity:** 🟡 Medium — `resume_warm_impact_v1.json` is a complete spec but has no Golden Master Doc and is not in the registry.

**Fix — after Fix 3 is applied:**
1. Validate the spec: `python3 validate_template_spec.py doc_templates/resume_warm_impact_v1.json`
2. Build the Golden Master: `python3 build_golden_master.py doc_templates/resume_warm_impact_v1.json`
3. Capture the printed Doc ID.
4. Register in `doc_templates.json` under `resume.variants` as:
   ```json
   "warm_impact": {
     "template_doc_id": "<captured_id>",
     "theme": "doc_templates/resume_warm_impact_v1.json"
   }
   ```

---

## 3. Verification — Run Skills Before Declaring Done

After all 8 fixes are applied, execute the following verification protocol. **Do not mark any item complete until the script exits 0 or you have documented why a non-zero result is a known false-positive.**

---

### Stage 1 — Spec validation (ats_template_qa_v2 skill, Stage 1)

For every file you modified or created, run:
```bash
python3 validate_template_spec.py doc_templates/<file>.json
```

Files to validate:
- `resume_warm_impact_v1.json` (modified + new build)
- `resume_chronological_v1.json` (modified)
- `cover_letter_government_v1.json` (modified)
- `cover_letter_private_v1.json` (modified)

**Required result:** `SPEC OK` for each. If any FAIL lines appear, fix them before proceeding. Relay output verbatim.

---

### Stage 2 — Style audit of affected Golden Masters (docs_style_auditor skill)

Run the mechanical style audit for every Golden Master whose theme spec you modified:

```bash
# Cover letter — government (Calibri theme)
python3 audit_doc_style.py <government_cl_doc_id> --theme doc_templates/cover_letter_government_v1.json

# Cover letter — private (Arial theme)
python3 audit_doc_style.py <private_cl_doc_id> --theme doc_templates/cover_letter_private_v1.json

# Resume — chronological (Times New Roman theme)
python3 audit_doc_style.py <chronological_doc_id> --theme doc_templates/resume_chronological_v1.json

# Resume — warm_impact (Calibri theme — new build)
python3 audit_doc_style.py <warm_impact_doc_id> --theme doc_templates/resume_warm_impact_v1.json

# KSC base — re-audit after builder fix
python3 audit_doc_style.py <ksc_doc_id> --theme doc_templates/ksc_base_v1.json
```

Doc IDs are in `doc_templates.json`. Warm impact ID is captured at Fix 8 Step 2.

**Required result:** `STYLE OK` for each OR documented known false-positives (per-role spacing variance — see AGENTS.md known caveats). Any `FAIL:` line that is NOT the known spacing false-positive must be investigated and resolved.

**Per the docs_style_auditor skill HARD RULES:**
- Never declare PASS without running the script.
- Relay FAIL output verbatim.
- Do not attempt automated fixes to Google Docs.

---

### Stage 3 — Dry-run token render check

```bash
python3 generate_document.py --dry-run --template cover_letter government
python3 generate_document.py --dry-run --template cover_letter private
python3 generate_document.py --dry-run --template resume chronological
python3 generate_document.py --dry-run --template resume warm_impact
python3 generate_document.py --dry-run --template ksc
```

**Required result for each:** `blank: 0` in the placeholder fill-rate report. Zero `fake_placeholder` warnings. If `warm_impact` is a new variant, confirm the route resolves correctly.

---

### Stage 4 — Registry integrity check

Confirm `doc_templates.json` state after all changes:
- All 10 variants (9 original + warm_impact) have a `template_doc_id` that is NOT a `REPLACE_WITH_*` placeholder.
- All 10 have a `theme` pointer to a file that exists on disk.
- No two variants share the same `template_doc_id`.

Run:
```bash
python3 -c "
import json, pathlib
d = json.loads(pathlib.Path('doc_templates.json').read_text())

def walk(node, path=''):
    if isinstance(node, dict):
        if 'template_doc_id' in node:
            tid = node['template_doc_id']
            theme = node.get('theme', 'MISSING')
            flag = '⚠️ PLACEHOLDER' if 'REPLACE_WITH' in tid else '✅'
            print(f'{flag} {path}: {tid} | theme={theme}')
        for k, v in node.items():
            walk(v, path + '.' + k if path else k)

walk(d)
"
```

All lines must show `✅`. Any `⚠️ PLACEHOLDER` is a failure.

---

## 4. Completion Criteria — Do Not Declare Done Until All Are Met

- [ ] `build_golden_master.py` KSC criterion colour bug fixed and verified
- [ ] `build_golden_master.py` max_criteria bug fixed and verified  
- [ ] `resume_warm_impact_v1.json` `accent_bar` removed
- [ ] `resume_chronological_v1.json` section heading colours changed to Charcoal
- [ ] `cover_letter_government_v1.json` name border_bottom added
- [ ] `cover_letter_private_v1.json` name colour changed to Teal
- [ ] `THEME_SPEC_GUIDE.md` stale audit section replaced
- [ ] `THEME_SPEC_GUIDE.md` theme library table updated to all 9/10 entries
- [ ] `resume_warm_impact_v1.json` validated by `validate_template_spec.py` (SPEC OK)
- [ ] `resume_warm_impact_v1.json` Golden Master built and Doc ID captured
- [ ] `doc_templates.json` `warm_impact` variant registered
- [ ] Stage 2 style audit passed for all 5 affected Golden Masters
- [ ] Stage 3 dry-run shows `blank: 0` for all 5 affected templates
- [ ] Stage 4 registry check shows `✅` for all variants (no REPLACE_WITH stubs)

**Only when every checkbox above is confirmed may you write the handover summary.**

---

## 5. Handover Summary Format

When complete, produce a summary in this exact format:

```
## Career Brain Theme Fix Handover

### Fixes Applied
| Fix | File | Status |
|---|---|---|
| KSC criterion colour | build_golden_master.py | ✅ Applied |
| KSC max_criteria cap | build_golden_master.py | ✅ Applied |
| warm_impact accent_bar removed | resume_warm_impact_v1.json | ✅ Applied |
| chronological heading colour | resume_chronological_v1.json | ✅ Applied |
| government CL name border | cover_letter_government_v1.json | ✅ Applied |
| private CL name teal | cover_letter_private_v1.json | ✅ Applied |
| THEME_SPEC_GUIDE stale note | THEME_SPEC_GUIDE.md | ✅ Applied |
| THEME_SPEC_GUIDE table | THEME_SPEC_GUIDE.md | ✅ Applied |
| warm_impact Golden Master | doc_templates.json | ✅ Registered |

### warm_impact Golden Master
Doc ID: <id>
Audit result: STYLE OK / FAIL lines (verbatim)
Dry-run blank count: 0

### Stage Audit Results
| Template | Spec OK? | Style OK? | Dry-run blank? |
|---|---|---|---|
| cover_letter_government | ✅ | ✅ | ✅ |
| cover_letter_private | ✅ | ✅ | ✅ |
| resume_chronological | ✅ | ✅ | ✅ |
| resume_warm_impact | ✅ | ✅ | ✅ |
| ksc_base | N/A | ✅ | ✅ |

### Known Caveats (not defects)
- Spacing false-positives in audit: ~70 FAILs per doc on per-role spacing (known auditor limitation — not ATS defects)
- KSC max_criteria: spec now reads from theme JSON; existing Golden Master capped at 3. Rebuild KSC Golden Master to pick up Fix 2 (separate manual step — quota-sensitive).

### Registry State
All 10 variants registered. No REPLACE_WITH stubs remain.
```

---

## 6. What NOT To Do

- Do not run `normalize_vault.py`, `compile_brain.py`, `curate_narratives.py`, `inject_metrics.py`.
- Do not modify `generate_document.py`, `audit_doc_style.py`, or `validate_template_spec.py`.
- Do not invent new placeholder tokens outside `PLACEHOLDER_SCHEMA_V2`.
- Do not declare STYLE OK without running `audit_doc_style.py` and reading its output.
- Do not declare SPEC OK without running `validate_template_spec.py` and reading its output.
- Do not declare the task complete before all 14 completion criteria are checked.
