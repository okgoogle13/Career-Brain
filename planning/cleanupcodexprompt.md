<agent_task>
  <identity>
    You are a refactor/knowledge-management agent running via Codex CLI
    (Gemini 5.4 mini) inside Google Antigravity.
    Project root:
      /Users/okgoogle13/Projects/Career Brain
  </identity>

  <goal>
    Analyse this project and generate a concrete, machine-usable refactor plan:
    - Classify important docs (planning, templates, schemas, resumes, KSC,
      cover letters, knowledge artifacts, configs).
    - Propose a clean folder structure.
    - Output a migration mapping (current_path → new_path) WITHOUT changing
      any files.
  </goal>

  <scope>
    - Work ONLY under:
        /Users/okgoogle13/Projects/Career Brain
    - Read and classify files.
    - DO NOT move, rename, edit, or delete any files.
    - Prefer fast, deterministic scans (no network calls).
  </scope>

  <target_structure>
    Use this as a baseline, adjust only if clearly needed:

    /Users/okgoogle13/Projects/Career Brain
      /docs/
        /planning/      # strategies, roadmaps, design docs
        /policies/      # rules, AGENTS-style docs
        /knowledge/     # knowledge artifacts, research, rubrics
      /prompts/
        /templates/     # reusable prompts
        /schemas/       # JSON/YAML schemas
        /workflows/     # multi-step prompt flows
      /content/
        /resumes/
        /cover_letters/
        /ksc_responses/
        /applications/
      /agents/
        /configs/
        /playbooks/
      /archive/
        /legacy/
        /scratch/

    Maintain a shallow hierarchy; group by doc TYPE and FUNCTION, not by tool.
  </target_structure>

  <required_outputs>
    1) Inventory file:
       - Path: logs/refactor_inventory.json
       - JSON array; each item:
         {
           "current_path": "relative/from/project/root",
           "filename": "name.ext",
           "ext": ".md" | ".txt" | ".pdf" | ".json" | ...,
           "doc_type": "planning|template|schema|resume|ksc|cover_letter|knowledge_artifact|config|scratch|unknown",
           "source_tool": "claude|gemini|perplexity|antigravity|unknown",
           "notes": "optional short classifier rationale"
         }

    2) Structural issues summary:
       - Path: logs/refactor_issues.md
       - Short Markdown report:
         - key problems (scattered planning docs, mixed directories, etc.)
         - counts per doc_type
         - any notable duplicates or obvious redundancies

    3) Migration / refactor plan:
       - Path: logs/refactor_plan.json
       - JSON array; each item:
         {
           "current_path": "relative/from/project/root",
           "proposed_new_path": "relative/new/path",
           "doc_type": "…",
           "retention_action": "KEEP|ARCHIVE|MERGE|RENAME",
           "comment": "short rationale"
         }

    4) Human-readable summary:
       - Path: logs/refactor_plan_summary.md
       - Short Markdown:
         - final proposed folder tree
         - counts by doc_type and target folder
         - any files marked ARCHIVE or MERGE
  </required_outputs>

  <classification_rules>
    - Infer doc_type from:
      - filename (contains: "resume", "cv", "cover", "ksc", "schema",
        "template", "plan", "strategy", "roadmap", "policy", "note", "scratch")
      - parent directory name
      - first heading or first 1–2 lines (where cheap to read)
    - Suggested mapping:
      - "resume", "cv"                   → doc_type = "resume"
      - "cover"                          → "cover_letter"
      - "ksc", "key selection"           → "ksc"
      - "template", "prompt", "macro"    → "template"
      - "schema", ".schema", json/yaml   → "schema"
      - "plan", "strategy", "roadmap"    → "planning"
      - "policy", "rules", "guidelines"  → "policy" (map to planning/policies)
      - "notes", "knowledge", "playbook" → "knowledge_artifact"
      - "config", "agent", "settings"    → "config"
      - obviously rough / scratch files  → "scratch"
    - source_tool:
      - match hints like "claude", "gemini", "perplexity", "antigravity"
        in names or paths; else "unknown".
  </classification_rules>

  <steps>
    STEP 1 — Inventory
      - Recursively traverse from project root.
      - For each file:
        - Determine relative path.
        - Classify ext and doc_type (using rules above).
        - Optionally peek at first lines/headings where cheap.
      - Write logs/refactor_inventory.json.

    STEP 2 — Issue detection
      - Using the inventory:
        - Count how many files per doc_type and per top-level directory.
        - Detect:
          - doc_types spread across many unrelated dirs (e.g. resumes in 4 dirs)
          - mixed dirs containing multiple doc_types
        - Write concise issues to logs/refactor_issues.md.

    STEP 3 — Proposed folder structure
      - Start from <target_structure>.
      - Add ONLY necessary subfolders (e.g. /content/portfolios) based on
        actual doc_types found.
      - Represent final structure textually in logs/refactor_plan_summary.md.

    STEP 4 — Migration mapping
      - For each inventory entry:
        - Decide proposed_new_path under target structure:
          e.g.:
            doc_type = resume          → /content/resumes/<filename>
            doc_type = ksc            → /content/ksc_responses/<filename>
            doc_type = cover_letter   → /content/cover_letters/<filename>
            doc_type = planning       → /docs/planning/<filename>
            doc_type = template       → /prompts/templates/<filename>
            doc_type = schema         → /prompts/schemas/<filename>
            doc_type = knowledge_artifact → /docs/knowledge/<filename>
            doc_type = config         → /agents/configs/<filename>
            doc_type = scratch        → /archive/scratch/<filename>
        - Set retention_action:
          - KEEP   (keep as-is, but move into new structure)
          - ARCHIVE (move under /archive/…)
          - MERGE  (if clearly a variant/duplicate; note in comment)
          - RENAME (only if obvious conflict or unclear name; specify)
      - Write full mapping to logs/refactor_plan.json.

    STEP 5 — Summary
      - Summarise:
        - final proposed folder tree
        - number of files per doc_type → per target folder
        - any files flagged ARCHIVE or MERGE (with brief reasons)
      - Append this to logs/refactor_plan_summary.md.

    STEP 6 — STOP
      - DO NOT apply changes.
      - Print a final message:
        "Refactor plan ready. Review logs/refactor_plan.json and
         logs/refactor_plan_summary.md before executing any moves."
  </steps>

  <constraints>
    - STRICTLY READ-ONLY: do not modify/move/rename/delete files or directories.
    - Use relative paths in all JSON and Markdown outputs.
    - Do not assume anything about external tools; rely only on filenames,
      paths, and cheap content inspection.
    - Keep outputs compact and deterministic so they can be used by another
      Codex/Antigravity agent as an execution plan.
  </constraints>
</agent_task>