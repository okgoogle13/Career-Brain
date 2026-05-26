# Google AI Studio — Session Configuration Cheat Sheet
# Career Brain Google Apps Script Build

---

## MODEL

**Gemini 2.5 Pro** (`gemini-2.5-pro-preview`)

**Why not Flash?**
Flash is faster and cheaper but weaker at multi-file code generation requiring
deep cross-file consistency (e.g., function signatures used across Code.gs,
ContentEngine.gs, and WorkspaceApi.gs must align perfectly). Pro is worth it here.

**Why not Opus/Claude in AI Studio?**
This is a Google Workspace build — Gemini 2.5 Pro has native, trained knowledge
of Google Apps Script APIs, HTML Service quirks, CacheService limits, and
google.script.run serialisation constraints. Claude requires more explicit prompting
for GAS-specific behaviour.

---

## MODEL SETTINGS

| Setting | Value | Reason |
|---|---|---|
| **Temperature** | `0.3` | Low — we want deterministic, consistent code. Higher temp = hallucinated APIs. |
| **Thinking** | `Enabled` (budget: Auto or High) | Required for multi-file dependency tracking and accurate algorithm porting |
| **Output token limit** | `65,536` (max) | Each .gs file can be 400–800 lines. Do not cap this. |
| **Top-P** | Leave default | Temperature 0.3 dominates; Top-P adjustment unnecessary |
| **Top-K** | Leave default | Same reason |
| **Safety settings** | All default | No sensitive content in this build |

---

## HOW TO SET UP THE SESSION

### Step 1 — Create a new prompt in AI Studio
Go to: https://aistudio.google.com → **Create prompt** → **Chat prompt**
(not "Structured prompt" — we need conversation turns)

### Step 2 — Select model
Top-left dropdown → **Gemini 2.5 Pro**
Enable **Thinking** if toggle is present.

### Step 3 — Set Temperature to 0.3
Right panel → Advanced settings → Temperature slider → drag to 0.3

### Step 4 — Set max output tokens to max
Right panel → Output length → set to 65536

### Step 5 — Paste System Instructions
Right panel → **System instructions** field (or "Add system instructions" link)
Paste the full contents of: `prompts/ai_studio_system_instructions.md`
Do NOT include the filename header line — paste from "You are a senior..." onwards.

### Step 6 — Upload context files
In the conversation area, use the **+** / attachment button to upload:
1. `prompts/repomix_gas_context.xml` (110 KB — targeted code context)
2. `prompts/gemini_25_pro_handover.md` (full build spec)

### Step 7 — Paste Phase 1 task prompt
Paste the full contents of `prompts/ai_studio_task_phase1.md` as your first message.

---

## SESSION MANAGEMENT TIPS

**Save the session** before each phase transition — AI Studio lets you name and
save prompts. Name it "Career Brain GAS — Phase N complete" after each phase passes
its success criterion.

**Don't regenerate mid-session** — if a response is partially wrong, reply with
a correction rather than clicking Regenerate. Regenerating loses the accumulated
context of what was already built.

**Phase transition prompts** — once Phase 1 passes its success criterion, use:
> "Phase 1 confirmed. Proceed to Phase 2: ContentEngine.gs.
>  Read content_engine.py from the repomix context and port each function to
>  JavaScript in the same order. Start with extractJobAdKeywords()."

**If context window fills up** — you'll see quality drop (hallucinated field names,
truncated files). At that point: start a new session, re-attach both context files,
paste the system instructions again, then summarise what was built:
> "Phases 1 and 2 are complete. Config.gs, DataLoader.gs, Code.gs, ContentEngine.gs
>  are done and working. Begin Phase 3: WorkspaceApi.gs."

---

## PHASE TRANSITION PROMPTS (copy-paste ready)

### After Phase 1 passes:
```
Phase 1 confirmed — scaffold loads and stats display correctly.

Proceed to Phase 2: ContentEngine.gs.

Port all content selection functions from content_engine.py in the repomix context.
Implement them as a single ContentEngine.gs file with a namespace object.
Start with: extractJobAdKeywords(), then selectRoles(), selectBullets(), selectNarratives(),
selectSkills(), generateProfessionalSummary(), applyRosettaStone(),
generateBridgeParagraph(), parseCriteria(), buildKscResponse().

Finish with buildPlaceholders(params, engines) — the orchestration function that
calls all of the above and returns the complete {placeholder: value} map.
Include the AU_TERMINOLOGY_MAP substitution pass as the final step.

Output the complete file. Do not truncate.
```

### After Phase 2 passes:
```
Phase 2 confirmed — ContentEngine.buildPlaceholders() returns correct map.

Proceed to Phase 3: WorkspaceApi.gs.

Build: cloneTemplate(docType, variant, targetRole, date),
injectValues(docId, placeholderMap), postFlightScan(docId),
moveToFolder(fileId, folderType), and the orchestration function
cloneAndInject(params, placeholderMap) that calls them in sequence.

Note: Docs.Documents.batchUpdate() requires the Advanced Google Services
"Google Docs API" to be enabled in the Apps Script project.
Flag this requirement in your response before writing the code.
```

### After Phase 3 passes:
```
Phase 3 confirmed — generateDoc() produces a real Google Doc with 0 unresolved tokens.

Proceed to Phase 4: Generate.html and updates to app.js.html.

Build the full generation form with preview panel, swap controls for bullets/narratives,
loading spinner, and success/error states. The preview panel calls previewContent()
(no API call, no doc cloning) and displays the assembled placeholder map in a
structured, readable layout before the user commits to creating the doc.
```

### After Phase 4 passes:
```
Phase 4 confirmed — full journey works end to end in under 60 seconds.

Proceed to Phase 5: Dashboard.html full build + Browse.html + Rosetta.html.
```

### After Phase 5 passes:
```
Phase 5 confirmed.

Proceed to Phase 6: Settings.html, first-run wizard, ATS template validator,
and responsive CSS polish for mobile (≤640px).
```

---

## FILE LOCATIONS (all in the Career Brain project)

| File | Path |
|---|---|
| System Instructions | `prompts/ai_studio_system_instructions.md` |
| Phase 1 Task Prompt | `prompts/ai_studio_task_phase1.md` |
| Phase 2–6 Prompts | This file (see section above) |
| Repomix Context | `prompts/repomix_gas_context.xml` |
| Full Build Spec | `prompts/gemini_25_pro_handover.md` |
| Master Spec Sheet | (in Antigravity artifact — career_brain_rebuild_spec.md) |
