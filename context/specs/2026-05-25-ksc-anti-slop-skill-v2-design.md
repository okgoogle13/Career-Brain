# Design: KSC Anti-Slop Skill v2

**Date:** 2026-05-25
**Status:** Approved — live generation validated 2026-05-30
**Scope:** KSC document type only (resume and cover_letter to follow once pattern proven)

---

## 1. Problem

The current `gold_template_builder` and `ats_template_qa` skills produce poor outputs that fall into two distinct failure modes, observed in real runs (see `recap.md` Batch 1 and the Batch 3 KSC output pasted in the brainstorming session).

**Cosmetic slop** — the agent's spec output is itself unprofessional:
- Decorative emoji headers (`📄 🔍 🧩 🧪 ⚠️`)
- ASCII box-drawing characters (`┌┐└┘├┤─│`) used as visual decoration
- Self-appended ritual footers ("CRITICAL GATING PROTOCOL: OPUS REVIEW REQUIRED") that the user never requested
- Markdown `##` used in place of explicit `[Heading 1]` annotations

**Fabrication slop** — the agent confabulates compliance:
- Invents token names (`{{KSC_CRITERION_1}}` when canonical is `{{KSC_CRITERION_1_TEXT}}`)
- Invents permissions ("standard circular bullets allowed" when `●` is explicitly in `forbidden_characters`)
- Declares "Validation Passed" without performing the listed checks
- Produces JSON registration fragments in the wrong shape (flat vs `variants`-nested)

These are different problems. Cosmetic slop is improvisation in a vacuum — fix by removing room to improvise. Fabrication slop is the model pretending to follow rules it never checked — fix by moving verifiable checks out of the LLM.

## 2. Goal

Make the KSC templating workflow robust enough that a Sonnet- or Haiku-class model produces a schema-correct, polished, ATS-compliant spec without requiring Opus to review and fix it.

Success means: an LLM-produced spec either passes a mechanical validator and is registered, or is rejected with a precise error pointing to the violated rule. No false PASS verdicts.

## 3. Non-goals

- Resume and cover_letter doc types (deferred until KSC pattern is proven).
- Strategy 3 from brainstorming (single-source-of-truth code → skill sync). Deferred to a follow-up spec.
- Anti-pattern gallery in the skill body. Deferred — small leverage, contamination risk needs careful framing.
- Replacing or modifying `generate_document.py`, `ats_rules.json`, or `doc_templates.json`. This work is additive.
- Deprecating v1 skills. v1 stays live until v2 is proven on KSC end-to-end.

## 4. Architecture

Two new artefacts, built alongside the existing v1 skills:

```
skills/
  gold_template_builder/          # v1 — unchanged, stays live
  ats_template_qa/                # v1 — unchanged, stays live
  gold_template_builder_v2/
    SKILL.md                      # KSC-only, rigid output template
    ksc_template_spec_form.md     # the fill-in form the LLM must produce
  ats_template_qa_v2/
    SKILL.md                      # KSC-only, references the linter

validate_template_spec.py         # new — hard-gate mechanical validator
```

The flow:

```
User invokes gold_template_builder_v2 for KSC
  → LLM produces a spec by filling the rigid form
  → User (or pre-commit hook) runs validate_template_spec.py against the spec
  → Validator either PASSES (spec is registerable) or FAILS (precise error)
  → On PASS: user creates Golden Master in Google Docs, registers Doc ID
  → User invokes ats_template_qa_v2 to validate the live Doc
```

The LLM proposes structure and prose. The script enforces facts.

## 5. Strategy 2 — Rigid output template (`gold_template_builder_v2`)

### 5.1 Skill body

The v2 SKILL.md replaces the prose "5-phase protocol" with a single instruction: **produce output that exactly matches `ksc_template_spec_form.md`. No additional sections. No decorative elements. No ritual footers.**

The skill body shrinks to roughly:
- One-paragraph overview (what KSC templates are, what the pipeline does).
- Pointer to `ksc_template_spec_form.md` as the required output shape.
- Pointer to `PLACEHOLDER_SCHEMA_V2` location in `generate_document.py` as the only valid source of token names.
- Pointer to `ats_rules.json` as the only valid source of forbidden glyphs and allowed headings.
- Hard rule: **"For every `{{TOKEN}}` you write in TOKENS_USED, cite the line range in `generate_document.py` where it is defined. If you cannot cite a line, the token is invalid — do not write it."**
- One-line invocation of the validator: `python3 validate_template_spec.py <spec_file>`.

### 5.2 The form (`ksc_template_spec_form.md`)

The form is the discipline. The LLM produces a Markdown file matching this shape exactly:

```
# KSC Template Spec

## META
TEMPLATE_TYPE: ksc
VARIANT: <name, lowercase, hyphenated>
DOC_ID: <Google Doc ID, or REPLACE_WITH_KSC_GOLDEN_MASTER_DOC_ID>
TARGET_SECTOR: <government | nfp | private | other>

## TOKENS_USED
<one per line, format: TOKEN_NAME → generate_document.py:LINE_RANGE>
<illustrative shape only — real line numbers will come from reading generate_document.py at spec-writing time:>
CONTACT_NAME → generate_document.py:<line>
TARGET_ROLE → generate_document.py:<line>
EMPLOYER_ORG → generate_document.py:<line>
KSC_CRITERION_1_TEXT → generate_document.py:<line>
KSC_1_CONTEXT → generate_document.py:<line>
...

## STRUCTURE
<ordered list, each line format: [HeadingStyle] HeadingText → {{TOKEN}} or static text>
<example:>
1. [Title] {{CONTACT_NAME}}
2. [Normal] {{TARGET_ROLE}}
3. [Normal] {{EMPLOYER_ORG}}
4. [Heading 1] {{KSC_CRITERION_1_TEXT}}
5. [Normal] Context: {{KSC_1_CONTEXT}}
6. [Normal] Action: {{KSC_1_ACTION}}
7. [Normal] Result: {{KSC_1_RESULT}}
8. [Bullet -] {{KSC_1_SUPPORT_BULLET_1}}
9. [Bullet -] {{KSC_1_SUPPORT_BULLET_2}}
... (repeat for criteria 2-6)

## ATS_AUDIT
columns_max: <PASS|FAIL> — <evidence string, max 20 words>
forbidden_chars: <PASS|FAIL> — <list any used, or "none">
allowed_headings: <PASS|FAIL> — <list heading texts used vs ats_rules.json allowed_headings>
au_terminology: <PASS|FAIL> — <list any non-AU terms found in static text, or "none">
ksc_word_limit_fit: <PASS|FAIL> — <evidence the CAR structure accommodates 200–500 words per criterion>

## REGISTRATION_FRAGMENT
```json
{
  "ksc": {
    "variants": {
      "<variant_name>": {
        "template_doc_id": "<id>"
      }
    }
  }
}
```

## DRY_RUN_CMD
python3 generate_document.py --type ksc --target "<Test Role at Test Org>" --criteria <criteria_file> --dry-run
```

The form is rigid: no emoji headers, no markdown tables for the audit (key-value lines only), no narrative "Phase 1 → Phase 2" framing, no self-appended approval rituals. Every field is mechanically parseable.

The audit values are not free-form. They must be one of the literal strings `PASS` or `FAIL`, followed by an em-dash and short evidence. The validator will reject other shapes.

## 6. Strategy 1 — Mechanical validator (`validate_template_spec.py`)

### 6.1 Inputs

- Path to a spec file produced by the v2 skill.
- Reads `generate_document.py` to extract `PLACEHOLDER_SCHEMA_V2` token names and their source line ranges.
- Reads `ats_rules.json` for forbidden characters, allowed headings, AU mappings.
- Reads existing `doc_templates.json` to learn the canonical shape of registration fragments.

### 6.2 Checks (hard gate — any failure blocks registration)

1. **Form shape conformance.** All required sections present (`META`, `TOKENS_USED`, `STRUCTURE`, `ATS_AUDIT`, `REGISTRATION_FRAGMENT`, `DRY_RUN_CMD`). No extra top-level sections. No emoji or box-drawing characters anywhere in the spec.
2. **Token validity.** Every `{{TOKEN}}` in `STRUCTURE` and `TOKENS_USED` must appear in `PLACEHOLDER_SCHEMA_V2`. Every token in `TOKENS_USED` must have a citation matching `generate_document.py:LINE` or `generate_document.py:LINE-LINE`, and the cited line range must actually contain that token name when read from disk.
3. **No fabricated tokens.** The set of tokens in `STRUCTURE` must equal the set in `TOKENS_USED` (no token used without citation; no citation for an unused token).
4. **Forbidden glyph scan.** The spec file is grepped for every character in `ats_rules.json` `forbidden_characters`. Any hit fails the spec, with a line number.
5. **Heading whitelist.** All `[Heading 1]` and `[Heading 2]` heading texts in `STRUCTURE` must appear in `ats_rules.json` `allowed_headings`.
6. **AU terminology.** All static text in `STRUCTURE` (text not inside `{{}}`) is scanned for forbidden US/UK terms from `ats_rules.json` `terminology.australian_mappings`. Any hit fails.
7. **Audit verdict honesty.** For each `ATS_AUDIT` line that says `PASS`, the corresponding mechanical check (rules 4, 5, 6 above) must also pass. If the LLM said `PASS` but the script finds a violation, the spec fails with a "fabricated PASS" error — this is the explicit anti-fabrication check.
8. **Registration fragment shape.** The JSON block must parse, must contain `ksc.variants.<variant>.template_doc_id`, and the variant name must match the META `VARIANT` value.
9. **KSC structural completeness.** Between 1 and 6 criteria blocks present (bounded by `MAX_KSC_CRITERIA` in `generate_document.py`). Each criterion block must contain `KSC_N_CONTEXT`, `KSC_N_ACTION`, `KSC_N_RESULT`, and 0–2 `KSC_N_SUPPORT_BULLET_N` entries. Criterion numbering must be contiguous starting at 1 (no gaps).

### 6.3 Output

On PASS: prints `SPEC OK: <path>` and exits 0.

On FAIL: prints each violation as a single line: `FAIL <rule_number> <spec_file>:<line>: <description>`. Exits 1. Multiple failures all reported in one pass (not first-fail).

### 6.4 Hard gate enforcement

Three enforcement points:
- The v2 SKILL.md instructs the LLM to run the validator and re-iterate on failure before declaring done.
- A pre-commit hook (added to `.pre-commit-config.yaml` or as a standalone git hook) runs the validator on any spec file in `docs/superpowers/specs/ksc/` and blocks the commit on failure.
- The user is instructed not to register a Doc ID in `doc_templates.json` until the validator returns 0 for the corresponding spec.

## 7. QA v2 wrapper (`ats_template_qa_v2`)

The v2 QA skill becomes a thin wrapper: when asked to validate a KSC template, it invokes `validate_template_spec.py` for the spec, and additionally walks the live Google Doc via the Docs API (the parts the script cannot see — heading styles applied, actual font, actual margins). The semantic Google-Docs-API checks stay with the LLM because they need interpretation. The mechanical checks do not.

The v2 QA SKILL.md is short: one paragraph of purpose, the validator command, and a short checklist of the Docs-API-only checks (font is Calibri 11pt; heading styles are native, not bolded Normal; no inline images; no text boxes).

## 8. Migration & rollout

1. Build `validate_template_spec.py`, `gold_template_builder_v2/`, `ats_template_qa_v2/` alongside v1.
2. Produce a KSC spec for one variant using v2. Run validator. Iterate until PASS.
3. Build the Golden Master Doc in Google Drive. Register Doc ID.
4. Run `generate_document.py --type ksc ... --dry-run`. Verify token resolution.
5. Run one end-to-end live KSC generation. Inspect output for polish.
6. If clean: extend the same pattern to resume and cover_letter as a follow-up spec. Deprecate v1 only once all three doc types are on v2.
7. If unclean: diagnose where the mechanical pipeline failed to catch the issue, add the check, re-test. Do not extend to other doc types until the KSC loop is clean.

## 9. Risks

- **Form rigidity may push fabrication elsewhere.** The LLM might fill the citation field with plausible-looking but wrong line numbers. Mitigated by check 2 (validator reads the cited line range and confirms the token name is actually there).
- **Validator becomes the new source of drift.** If `generate_document.py` changes its schema location, the validator's extraction logic breaks silently. Mitigated by adding a smoke test that runs the validator against a known-good spec on every CI run.
- **User friction from the hard gate.** Iterating to a clean spec may take 2–3 LLM revisions. Acceptable trade-off given the alternative is silent slop entering the live pipeline.
- **No peer review on this spec.** Codex peer-review profile is uninitialised, so the strategy was validated by a single reviewer pass rather than blind debate. A second independent review before implementation would strengthen confidence in the rule list (section 6.2 in particular).

## 10. Success criteria

- A KSC spec produced by Sonnet (not Opus) passes `validate_template_spec.py` on first or second attempt.
- The resulting Google Doc generates a clean KSC document via `generate_document.py` with no `parsing_errors.log` entries.
- The Batch 3 anti-pattern (wrong token names, fabricated PASS, decorative emoji, ritual footer) cannot recur — each is blocked by a specific named check in section 6.2.

## 11. Open questions

None — user has answered scope (KSC only), enforcement (hard gate), and rollout (alongside v1).
