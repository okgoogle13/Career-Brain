---
name: custom-skills-sync
description: Sync custom Claude skills from your IDE or local directory to Cowork mode. Use this whenever you have custom skills in your codebase that you want to make available in Cowork — whether you're migrating from Claude Code, backing up your skills, or onboarding new ones. Handles directory discovery, file integrity checks, and version tracking automatically.
---

# Custom Skills Sync Manager

## Overview

This skill automates the workflow for discovering, validating, and syncing your custom Claude skills from any local directory to Cowork mode. It's designed to handle bulk migrations from Claude Code / IDE environments and keep your skills in sync across systems.

## When to Use

- **Initial migration:** You have custom skills scattered across your IDE and want them all in Cowork
- **Backup & restore:** Creating a backup copy of your skills before updating your IDE setup
- **Onboarding:** You've written new skills and want to make them available in your Cowork session
- **Version tracking:** You want to maintain a verified copy of each skill iteration

## Key Features

- **Automatic discovery:** Finds all skill directories (those containing `SKILL.md` files)
- **Recursive scanning:** Handles nested skill directories and bulk skill collections
- **File integrity:** Uses checksums to verify copied files match originals exactly
- **Encoding detection:** Identifies and reports character encoding issues during copy
- **Metadata preservation:** Maintains file permissions, modification dates, and YAML frontmatter
- **Verification report:** Generates a detailed manifest of what was synced and any issues found

## How It Works

### Step 1: Locate Your Skills

Provide the root directory where your skills are stored:

```bash
# Example paths that work:
/Users/yourname/Projects/MyWork/agent_skills/
/Users/yourname/Claude Code/skills/
~/.claude/skills/
/path/to/any/directory/containing/skill-folders/
```

The skill scans recursively for any subdirectory containing a `SKILL.md` file.

### Step 2: Copy to Cowork

For each skill found:

```
source/
├── skill-1/
│   ├── SKILL.md
│   ├── reference-file.md
│   └── scripts/
│       └── helper.py
└── skill-2/
    └── SKILL.md
```

Skills are copied to:
```
outputs/synced_skills/
├── skill-1/
├── skill-2/
└── SYNC_MANIFEST.md
```

### Step 3: Verify Integrity

Each file is validated:

| Check | What it verifies |
|---|---|
| **File presence** | All source files are present in the synced copy |
| **Byte-for-byte match** | Content checksums match (using `cmp` binary comparison) |
| **Encoding integrity** | Detects corrupted characters (e.g., backticks, escape sequences) |
| **Directory structure** | Nested files and subdirectories are preserved |

If any file differs, a detailed report shows file sizes and the exact differences.

### Step 4: Generate Manifest

A `SYNC_MANIFEST.md` is created listing:
- Skills synced (count, names)
- Any issues found and how they were fixed
- Verification status for each skill
- Links to original sources and synced copies
- Next steps for using the skills

## Example Output

```markdown
# Custom Claude Skills — Synced to Cowork

**Sync Date:** May 28, 2026  
**Source:** `/Users/okgoogle13/Projects/Career Brain/agent_skills/`  
**Status:** ✓ All skills backed up and verified

## Skills Synced (3 total)

### 1. ats-template-qa-v2
Status: ✓ VERIFIED & CORRECTED
Issue found: Encoding corruption on line 7 (backtick) — FIXED

### 2. docs-style-auditor  
Status: ✓ IDENTICAL — NO ISSUES FOUND

### 3. gold-template-builder-v2
Status: ✓ IDENTICAL — ALL FILES VERIFIED
```

## What Gets Copied

Everything in each skill directory is synced:

- `SKILL.md` (required) — the skill definition
- `scripts/` (if present) — Python, bash, or other executable code
- `references/` (if present) — documentation files
- `assets/` (if present) — templates, icons, fonts
- Any other files in the skill folder (configurations, data, etc.)

## Usage Pattern

When asked to sync skills:

1. **Ask for the source directory:** "Where are your custom skills stored?"
2. **Scan recursively:** Find all skill directories automatically
3. **Copy with verification:** Copy each skill and check integrity
4. **Generate manifest:** Create a verification report
5. **Report status:** Show user what was synced and any corrections made

## Error Handling

| Issue | Resolution |
|---|---|
| **Encoding corruption** (stray backticks, escape sequences) | Automatically detect and fix common encoding issues; report in manifest |
| **File size mismatch** | Report byte counts for both source and synced; show first few lines of diff |
| **Missing files** | List files present in source but absent in copy; don't declare sync complete |
| **Permission issues** | Report if synced copy is read-only; suggest copying to writable location |

## Best Practices

- **Verify before using:** Always review the `SYNC_MANIFEST.md` to understand what changed
- **Keep originals:** The source directory remains unchanged — synced copies are working copies
- **Update both:** If you edit a synced skill, update the original too so the next sync is clean
- **Test after sync:** If a skill has test cases, run them on the synced version to confirm integrity
- **Archive versions:** The manifest is timestamped — keep old manifests to track skill evolution

## Command Reference

```bash
# Typical sync workflow (as performed by this skill):
find /source/directory -name SKILL.md | while read skill; do
  skill_dir=$(dirname "$skill")
  cp -r "$skill_dir" /output/location/
done

# Verify files match
cmp -s source_file synced_file && echo "✓ Match" || echo "✗ Mismatch"

# Generate manifest with status
```

---

**Next Steps After Syncing:**

1. Review the generated `SYNC_MANIFEST.md` for any issues noted
2. If issues were auto-corrected, the manifest explains what changed and why
3. Copy the synced skills folder to your Cowork skills directory if you want them loaded automatically
4. Test one skill to confirm it works correctly in your Cowork session
