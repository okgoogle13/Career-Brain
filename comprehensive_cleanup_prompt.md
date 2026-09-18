/goal Execute a comprehensive, multi-phase project cleanup and meticulous file analysis using the structured approach below. You (Sonnet) will act as the primary orchestrator. You must relentlessly execute these phases, aggressively leveraging specialized subagents, MCP tools, and custom skills. 

### Phase 1: Codebase Packing & Indexing (via Repomix)
Your first objective is to generate a comprehensive codebase index (`index.md`) that can be handed off to an external, blind agent (like Perplexity) for objective assessment.
1. **Run Repomix:** Use the `call_mcp_tool` to invoke `pack_codebase` (or `pack_remote_repository` if targeting a remote repo) from the `repomix` MCP server. 
   - **Crucial parameters:** Set `style` to `"xml"` so the output is structured with clear `<file>` tags for parsing. Set `compress` to `true` to use Tree-sitter to extract essential code signatures and structures while stripping verbose implementation details.
2. **Analyze the XML Dump:** Review the generated XML output, analyzing the file tree structure, imports, exports, code signatures, and comments within each `<file>` block.
3. **Generate `index.md`:** Create an exhaustive `index.md` file at the root. List **every single file** present in the repository. Group the files logically (e.g., by directory or module). For each file, write a concise description of its purpose, its dependencies, and how it fits into the broader architecture based on the XML context.

### Phase 2: Meticulous Analysis & Code Review
1. Delegate to the `@code-reviewer` and `@security-auditor` subagents to perform a rigorous, multi-axis review (correctness, readability, architecture, security, performance) on all core logic and execution scripts identified in the index.
2. Apply the `code-review-and-quality` and `doubt-driven-development` skills to stress-test high-stakes configurations, looking for edge cases, missing assertions, and logic contradictions.
3. Evaluate the general effectiveness of the code: Does it efficiently achieve its intended purpose as documented in Phase 1?

### Phase 3: Cleanup, Deprecation, & Archiving
1. Identify legacy files, dead code, unreferenced dependencies, and outdated architectural patterns.
2. Apply the `deprecation-and-migration` skill to safely sunset old code. Move any unused, obsolete, or superseded files into a designated `legacy/` archive folder rather than permanently deleting them.
3. Apply the `code-simplification` skill to refactor and remove accumulated complexity in the remaining active files, ensuring existing behavior remains intact.

### Phase 4: Custom Skills, Themes, & Gap Analysis
1. Conduct a dedicated review of the custom skills and themes I have created. Evaluate their clarity, usefulness, and alignment with the project's current architecture.
2. Apply your `claude-md-improver` skill to refine, polish, and standardize the documentation of these skills. 
3. Apply your `automation recommender` skill to suggest areas where manual tasks can be scripted or automated.
4. Audit the final state of the repository against our project goals. Update `tasks.md` by logging any remaining gaps, architectural issues, or bugs that need to be addressed in future sessions.

### Execution Rules & Escalation Protocol
- **Continuous Execution:** Do not stop until all four phases are complete and the entire directory has been packed, indexed, cleaned, and documented.
- **Opus Escalation:** At critical decision points—such as before making major, irreversible architectural changes, archiving highly integrated components, or resolving complex logic contradictions—pause and use the `/advisor` command to escalate the specific dilemma to Opus for a secondary review. Wait for Opus's verdict before proceeding.
- **Documentation Standards:** Ensure all markdown outputs (`index.md`, `tasks.md`, skill documentation) are highly polished and provide sufficient context for blind external agents to understand the system.
