# Custom Skills Created from Sync/Verification Discussion

**Date Created:** May 28, 2026  
**Base Directory:** `/Users/okgoogle13/Projects/Career Brain/custom_skills/`  
**Status:** ✓ Ready for packaging and installation

---

## Three Skills Created

### 1. **custom-skills-sync**
**Purpose:** Sync custom Claude skills from IDE/local directories to Cowork mode  
**Location:** `custom-skills-sync/`

**What it does:**
- Discovers all skill directories recursively (finds `SKILL.md` files)
- Copies skills with integrity validation (byte-for-byte verification)
- Detects and reports encoding issues (stray backticks, control characters)
- Generates timestamped `SYNC_MANIFEST.md` with detailed status

**When to use:**
- Migrating skills from Claude Code to Cowork
- Backing up custom skills
- Syncing updated skills from IDE to Cowork
- Bulk skill deployment

**Test cases:** 3 evals covering initial sync, multi-directory consolidation, and re-sync of updated skills

---

### 2. **skills-verification-qa**
**Purpose:** Run production-grade QA on synced/updated skills  
**Location:** `skills-verification-qa/`

**What it does:**
- Binary file comparison (cmp-based exact matching)
- Encoding integrity checks (detects corrupted UTF-8, stray escapes)
- YAML frontmatter validation (`name`, `description` present)
- Markdown syntax validation
- Comparative version checking (what changed between versions)
- Generates audit-ready verification reports

**When to use:**
- After syncing skills to verify copy integrity
- Before deploying skills to catch encoding/permission issues
- Debugging a skill that's not working correctly
- Creating compliance audit trails
- Post-update validation

**Test cases:** 3 evals covering post-sync verification, encoding issue detection, and audit report generation

---

### 3. **career-brain-skill-integration**
**Purpose:** Orchestrate the Career Brain ATS/template pipeline  
**Location:** `career-brain-skill-integration/`

**What it does:**
- Coordinates Gold Template Builder → Docs Style Auditor → ATS Template QA workflow
- Knows which skill to invoke at each stage
- Understands the KSC pipeline (template design → Golden Master → ATS validation)
- Handles themed resume variants (contemporary_professional, professional_classic, modern_minimalist)
- Guides through full template creation or debugging workflow

**When to use:**
- Creating new KSC templates from scratch
- Validating template specs before Golden Master creation
- Auditing Golden Master documents for ATS compliance
- Building themed resume variants
- Debugging why a template isn't working
- Final QA before template registration

**Test cases:** 3 evals covering full pipeline creation, themed variant auditing, and diagnostic debugging

---

## How These Skills Were Designed

These skills were extracted and synthesized from our actual sync/verification workflow:

1. **custom-skills-sync** — From our experience syncing your three existing skills (ats_template_qa_v3, docs_style_auditor_v3, gold_template_builder_v3) and discovering encoding issues during the process

2. **skills-verification-qa** — From our verification process where we caught a corrupted heading (backtick) in ats_template_qa_v3 and had to fix it. Generalizes that QA workflow into a reusable skill

3. **career-brain-skill-integration** — From understanding your existing three skills and how they work together in the KSC template pipeline. Orchestrates them for future users

---

## File Structure

```
custom_skills/
├── custom-skills-sync/
│   ├── SKILL.md (primary content)
│   └── evals.json (3 test cases)
├── skills-verification-qa/
│   ├── SKILL.md (primary content)
│   └── evals.json (3 test cases)
└── career-brain-skill-integration/
    ├── SKILL.md (primary content)
    └── evals.json (3 test cases)
```

---

## Installation Instructions

### For Claude Desktop App (macOS)

Each skill is self-contained in its directory. To install:

1. **Locate your Claude skills directory:**
   ```
   ~/.claude/skills/
   ```
   Or create it if it doesn't exist:
   ```
   mkdir -p ~/.claude/skills/
   ```

2. **Copy each skill folder:**
   ```bash
   cp -r custom-skills-sync ~/.claude/skills/
   cp -r skills-verification-qa ~/.claude/skills/
   cp -r career-brain-skill-integration ~/.claude/skills/
   ```

3. **Restart Claude Desktop App** to pick up the new skills

4. **Skills will be available immediately** — reference them by name:
   - `custom-skills-sync` for syncing skills
   - `skills-verification-qa` for QA validation
   - `career-brain-skill-integration` for Career Brain workflows

### For Claude Code (via CLI)

If using Claude Code, skills can be referenced directly from their file paths or installed in your Claude Code plugins directory.

---

## Skill Triggering

### custom-skills-sync
Triggers when user mentions:
- "Sync my skills to Cowork"
- "Backup my custom skills"
- "Migrate skills from IDE"
- "Copy skills to outputs folder"
- Any request involving syncing/backing up skill directories

### skills-verification-qa
Triggers when user mentions:
- "Verify my synced skills"
- "QA check before deployment"
- "Is this file corrupted?"
- "Generate audit report"
- Any skill validation/verification request

### career-brain-skill-integration
Triggers when user mentions:
- "Create a KSC template"
- "Design a template spec"
- "Audit my Golden Master"
- "Is this template ATS-safe?"
- "Build themed resume variants"
- Template pipeline or Career Brain workflow requests

---

## Next Steps

1. **Copy skills to ~/.claude/skills/** (see installation above)
2. **Restart Claude Desktop App** to load the skills
3. **Test by referencing them:** "I have custom skills in ~/Projects/Career Brain/agent_skills - sync them using custom-skills-sync"
4. **Keep originals:** Skills in custom_skills/ folder are the canonical versions — back them up or add to version control

---

## Files Included

**Skill Definitions (SKILL.md):**
- All three skills have complete, production-ready SKILL.md files
- Each includes frontmatter (name, description), detailed instructions, examples, and usage patterns
- Descriptions are written to be "pushy" and capture all trigger phrases

**Test Cases (evals.json):**
- 3 realistic test cases per skill
- Written as actual user prompts (not abstract scenarios)
- Include expected outputs so you can validate skill performance
- Ready for evaluation/iteration workflow

---

## Version Info

- **Skills Version:** 1.0
- **Created:** May 28, 2026
- **Based on:** Real sync/verification workflow from Career Brain custom skills
- **Status:** Production-ready for installation and use

---

## Support & Maintenance

If you need to update a skill:
1. Edit the SKILL.md in the custom_skills/ folder
2. Test with the included evals.json test cases
3. Update the installed version in ~/.claude/skills/
4. Restart Claude to pick up changes

All three skills are independent but work well together as a workflow: sync → verify → integrate.
