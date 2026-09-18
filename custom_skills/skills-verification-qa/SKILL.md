---
name: skills-verification-qa
description: Run comprehensive QA checks on synced or updated skills to ensure they match originals, have no encoding issues, and are ready for production. Use this after syncing skills, before deploying them, or anytime you want to verify that a skill's implementation is correct. Detects corruption, compares versions, and generates detailed audit reports.
---

# Skills Verification & QA

## Overview

Production-grade verification skill for validating synced or updated custom Claude skills. Runs binary file comparisons, encoding checks, structural validation, and generates audit-ready reports.

This skill is designed to catch issues that could cause silent failures — corrupted headings, missing files, encoding problems, permission issues — before they reach production.

## When to Use

- **After syncing skills:** Verify that all files copied correctly and match originals
- **Before deploying:** QA check before adding skills to your Cowork session
- **When debugging:** A skill isn't working — run verification to find what's different
- **Post-update:** You edited a skill — confirm the edits are correct and nothing got corrupted
- **Compliance:** Generate audit trails showing skills are validated and match source

## Verification Checks

### File-Level Checks

| Check | What it validates | Failure condition |
|---|---|---|
| **Presence** | All source files exist in the verification copy | Files missing from target |
| **Binary match** | Files are byte-for-byte identical | File size or content differs |
| **Encoding integrity** | No stray escape sequences, corrupted UTF-8, or control characters | Non-printing chars found |
| **Permissions** | Files are readable (u+r at minimum) | Read permission denied |

### Skill-Level Checks

| Check | What it validates |
|---|---|
| **SKILL.md exists** | Every skill has a valid SKILL.md file |
| **YAML frontmatter** | Frontmatter parses correctly (`name`, `description` present) |
| **Markdown syntax** | No unclosed code blocks, broken links, or malformed tables |
| **Required fields** | `name` and `description` are non-empty strings |
| **Directory structure** | Optional directories (`scripts/`, `references/`, `assets/`) follow naming convention if present |

### Comparative Checks (when comparing two versions)

| Check | Purpose |
|---|---|
| **Version change** | Detect what changed between original and updated version |
| **Content drift** | Identify if a skill was accidentally modified |
| **Metadata changes** | Track updates to name, description, or frontmatter |

## Report Format

Generated as `SKILL_VERIFICATION_REPORT.md`:

```markdown
# Skills Verification Report

**Date:** 2026-05-28  
**Verification Type:** Post-sync integrity check  
**Status:** ✓ PASS (3/3 skills verified)

## Summary

All 3 skills verified successfully. No issues found.

## Detailed Results

### ats-template-qa-v3 ✓ PASS

**Files checked:** 1
- ✓ SKILL.md (2632 bytes) — MATCH

**Frontmatter:** ✓ Valid
- name: ats-template-qa-v2
- description: [present]

**Encoding:** ✓ Clean
**Permissions:** ✓ Readable

**Status:** Production-ready

### docs-style-auditor-v3 ✓ PASS

**Files checked:** 1
- ✓ SKILL.md (4351 bytes) — MATCH

**Frontmatter:** ✓ Valid
**Encoding:** ✓ Clean
**Permissions:** ✓ Readable

**Status:** Production-ready

---

## Fail Examples

If issues are found:

```markdown
### gold-template-builder-v3 ✗ FAIL

**Files checked:** 2
- ✓ SKILL.md (3458 bytes) — MATCH
- ✗ ksc_template_spec_form.md — NOT FOUND

**Encoding issues detected:**
- Line 15: Stray backtick (` before heading)
- Line 42: Non-ASCII quote mark (should be ")

**Recommendations:**
1. Copy the missing file: ksc_template_spec_form.md
2. Fix line 15: Remove backtick before "# Gold Template..."
3. Fix line 42: Replace curly quote with straight quote
4. Re-run verification after fixes
```
```

## Output Levels

### Summary (default)

Shows pass/fail for each skill and critical issues only:

```
✓ ats-template-qa-v3 — PASS
✓ docs-style-auditor-v3 — PASS
✗ gold-template-builder-v3 — FAIL (missing ksc_template_spec_form.md)
```

### Detailed

Full file-by-file breakdown, encoding analysis, and recommendations.

### Audit

Includes checksums, timestamps, file sizes, and metadata suitable for compliance/archival.

## Usage Workflow

### Scenario 1: Post-Sync Verification

```
1. Run sync (custom-skills-sync)
2. Run this verification
3. If any issues found → auto-fix common ones (encoding) OR ask user to fix
4. Re-run verification to confirm
5. Proceed to deployment
```

### Scenario 2: Debugging a Broken Skill

```
1. User reports: "This skill isn't triggering"
2. Run verification on both source and deployed version
3. Compare the two versions
4. Identify the difference (e.g., corrupted frontmatter, missing file)
5. Show user the exact issue and how to fix it
```

### Scenario 3: Quality Gate Before Deployment

```
Before adding a skill to production Cowork session:
1. Run verification with --strict flag
2. All checks must pass with no warnings
3. Generate audit report
4. Sign off on deployment
```

## Interpretation Guide

### ✓ PASS — Production-Ready

- All files present and match originals
- No encoding issues or structural problems
- Frontmatter is valid and complete
- Ready to use immediately

### ⚠ PASS WITH WARNINGS

- All files match but minor issues noted (e.g., very long lines, deprecated patterns)
- Skill will work but minor cleanup recommended
- Can proceed but consider addressing warnings in next iteration

### ✗ FAIL — Do Not Deploy

- File corruption detected (size or content mismatch)
- Missing required files
- Encoding issues that would cause parsing failures
- Invalid frontmatter
- **Action required:** Fix issues before deployment

## Common Issues & Fixes

| Issue | Cause | Fix |
|---|---|---|
| Stray backtick in heading | Copy/paste encoding issue | Remove backtick; re-verify |
| File size mismatch | Incomplete copy or partial write | Re-copy and verify |
| Missing .md file | Nested file not copied | Use `-r` flag for recursive copy |
| Non-UTF8 characters | Source uses different encoding | Convert to UTF-8; re-copy |
| Permission denied on read | File is read-only | `chmod u+r` and verify again |

## Advanced: Comparative Verification

Compare a synced skill against a previous version:

```
Verification: gold-template-builder-v3
Source: ~/Projects/Career Brain/.claude/skills/gold-template-builder-v3
Previous: ~/outputs/synced_skills/gold-template-builder-v3 (from last sync)

Changes detected:
- SKILL.md: +5 lines, -2 lines (content updated)
- ksc_template_spec_form.md: NO CHANGE

Status: ✓ Changes are intentional updates, not corruption
```

## Report Archival

Save verification reports alongside skills for audit trail:

```
synced_skills/
├── ats-template-qa-v3/
├── docs-style-auditor-v3/
├── gold-template-builder-v3/
├── SYNC_MANIFEST.md (from sync)
├── SKILL_VERIFICATION_REPORT_2026-05-28.md ← this report
└── SKILL_VERIFICATION_REPORT_2026-05-27.md ← previous
```

Timestamped reports create a complete history of skill integrity checks.

---

**Next Steps:**

1. Run verification immediately after syncing
2. Address any FAIL items before using skills
3. Archive the verification report for your records
4. For PASS results, proceed to skill testing/deployment
