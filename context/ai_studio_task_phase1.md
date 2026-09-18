# TASK INSTRUCTIONS — Phase 1 Kickoff
# This is the FIRST USER TURN in the Google AI Studio conversation.
# Paste this after uploading the two context files.
# Do NOT paste the system instructions here — those go in the System field.

I have uploaded two context files:
- `repomix_gas_context.xml` — contains the source code of the existing Python pipeline
  (content_engine.py, generate_document.py), all 5 template spec files, doc_templates.json,
  ats_rules.json, user_config.json, and gem_system_prompt.md
- `gemini_25_pro_handover.md` — the full build specification including placeholder schemas,
  content selection rules, constraint matrix, file structure, and phased build plan

Read both files in full before writing any code.

---

## WHAT WE ARE BUILDING

A Google Apps Script Web App that reads three compiled JSON knowledge engines from
Google Drive and generates ATS-compliant Google Docs (resumes, cover letters, KSC
responses) via the Google Docs batchUpdate API. The Python ETL pipeline that produced
the JSON engines is complete and is NOT being rebuilt.

## PROJECT FILE STRUCTURE

```
Code.gs              ← Entry point: doGet(), server functions
ContentEngine.gs     ← Content selection logic (port from content_engine.py)
WorkspaceApi.gs      ← Drive clone + Docs batchUpdate injection
DataLoader.gs        ← Load + cache JSON engines from Drive
Config.gs            ← All constants: file IDs, folder IDs, template IDs, limits
index.html           ← Shell layout + navigation sidebar
Dashboard.html       ← Stats widgets + quick generate form
Generate.html        ← Full form + preview panel
Browse.html          ← DB explorer
Rosetta.html         ← Translation tool
Settings.html        ← Contact info, folder IDs
app.js.html          ← Shared client-side JS
styles.css.html      ← Shared CSS with design tokens
```

## KEY CONSTANTS FOR Config.gs

Use these exact values — they are real Google Drive file IDs:

```javascript
// Google Doc Template IDs (Golden Master — READ ONLY, clone only)
const TEMPLATE_IDS = {
  resume: {
    chronological:           '1Bc8BMBgmT3YYpdjfdxSfTidUVvrpUGukRlbWIJN-Rb8',
    hybrid:                  '1Bc8BMBgmT3YYpdjfdxSfTidUVvrpUGukRlbWIJN-Rb8',
    contemporary_professional:'1eZG0SWplIowrxv13En36h_Qqew7ibIWqRhQAV6D7YKM',
    professional_classic:    '18PUuV8FHuN7upC8dl941qkOhF1cqhgfXJ2R8EFEM56E',
    modern_minimalist:       '1xpXFsl0OvmPxayiRKIaGE-3DRNkvtD16WPcp9qc324k',
  },
  cover_letter: {
    government: '18UOiEOQkK3M4vfVYwgYlf0tYGZePbvG2fxt-_19rDM4',
    nfp:        '18UOiEOQkK3M4vfVYwgYlf0tYGZePbvG2fxt-_19rDM4',
    private:    '18UOiEOQkK3M4vfVYwgYlf0tYGZePbvG2fxt-_19rDM4',
  },
  ksc: {
    standard:   '10PT1cgIPnrQd63tp0CRqCMnq0Z1QZEYkXv0BdNWzh2I',
  },
};

// Drive folder IDs
const FOLDER_IDS = {
  root:          '1U0qpznqgKRbJtCQMRA9_VXL90U9Bk5wl',
  resumes:       'REPLACE_WITH_RESUMES_FOLDER_ID',
  cover_letters: 'REPLACE_WITH_COVER_LETTERS_FOLDER_ID',
  ksc_responses: 'REPLACE_WITH_KSC_FOLDER_ID',
};

// JSON engine file IDs (replace with real Drive file IDs after uploading)
const ENGINE_FILE_IDS = {
  history:    'REPLACE_WITH_HISTORY_FILE_ID',
  narratives: 'REPLACE_WITH_NARRATIVES_FILE_ID',
  taxonomy:   'REPLACE_WITH_TAXONOMY_FILE_ID',
};

// Content selection limits
const MAX_RESUME_ROLES     = 6;
const MAX_BULLETS_PER_ROLE = 4;
const MAX_RESUME_SKILLS    = 6;
const MAX_KSC_CRITERIA     = 6;
const MAX_KSC_SUPPORT_BULLETS = 2;
const CACHE_TTL_SECONDS    = 600;

// Salutation defaults
const SALUTATION_MAP = {
  government: 'Selection Panel',
  nfp:        'Hiring Manager',
  private:    'Hiring Manager',
};

// KSC word count targets
const KSC_WORD_TARGETS = {
  context: [40, 100],
  action:  [60, 200],
  result:  [30, 100],
  total:   [200, 500],
};

// Australian terminology substitutions — applied to ALL generated text
const AU_TERMINOLOGY_MAP = {
  'company':              'organisation',
  'companies':            'organisations',
  'industry':             'sector',
  'industries':           'sectors',
  'job description':      'position description',
  'job ad':               'position advertisement',
  'competency questions': 'key selection criteria',
};
```

---

## PHASE 1 — BUILD NOW

Build the following four files in this order. Output each file as a complete,
untruncated code block before moving to the next.

### File 1: Config.gs
All constants above. Add a `getConfig()` function that returns the full config
as a plain object (for passing to client-side if needed).

### File 2: DataLoader.gs
```
function loadEngines():
  - Check CacheService.getUserCache() for key 'cb_engines'
  - If cache hit: return JSON.parse(cached)
  - Else: read each file via DriveApp.getFileById(id).getBlob().getDataAsString()
  - Parse JSON, bundle as { history, narratives, taxonomy }
  - Store in cache with CACHE_TTL_SECONDS TTL
  - Return engines object

function getStats(engines):
  - roles: engines.history.roles.length
  - totalBullets: sum of achievements.length across all roles
  - needsReview: count of achievements where needs_review === true
  - narrativesByTier: {1: count, 2: count, 3: count} from engines.narratives.narratives
  - rosettaMappings: Object.keys(engines.taxonomy.rosetta_stone).length
  - skills: engines.taxonomy.skills_inventory.length
  - Return plain object with all above fields
```

### File 3: Code.gs
```
function doGet(e):
  - Return HtmlService.createTemplateFromFile('index').evaluate()
    with title 'Career Brain' and XFrameOptionsMode ALLOWALL

function getStatsForDashboard():
  - const engines = loadEngines()
  - return getStats(engines)
  [this is the server function the dashboard calls via google.script.run]

function include(filename):
  - Helper to include CSS/JS partials: HtmlService.createHtmlOutputFromFile(filename).getContent()
```

### File 4: index.html
- Dark-themed shell layout with left navigation sidebar
- Nav links: Dashboard, Generate, Browse, Rosetta, Settings
- Page content area (right side, takes remaining width)
- Include styles.css.html and app.js.html via the include() helper
- On load: use google.script.run.getStatsForDashboard() to populate Dashboard tab
- Navigation switches visible panel without reloading the page (single-page pattern)

### File 5: styles.css.html
Implement the full CSS design system using these tokens:
```css
--color-primary: hsl(220, 70%, 50%);
--color-accent: hsl(160, 60%, 45%);
--color-warning: hsl(35, 90%, 55%);
--color-danger: hsl(0, 70%, 55%);
--color-surface: hsl(220, 15%, 12%);
--color-surface-elevated: hsl(220, 15%, 18%);
--color-surface-card: hsl(220, 15%, 22%);
--color-text: hsl(220, 15%, 92%);
--color-text-muted: hsl(220, 10%, 60%);
--color-border: hsl(220, 15%, 28%);
--font-body: 'Inter', sans-serif;
--font-mono: 'JetBrains Mono', monospace;
--radius: 8px;
--shadow: 0 4px 24px rgba(0,0,0,0.3);
```
Include: layout grid, sidebar nav styles, card component, stat widgets, button variants
(primary/secondary/danger), form elements, loading spinner, responsive breakpoints
(mobile ≤640px collapses sidebar to bottom nav).

### File 6: Dashboard.html
- Stat cards grid: Roles, Bullets, Needs Review, Narratives (T1/T2/T3), Rosetta Mappings, Skills
- Needs Review card shows count with amber colour and "Review queue →" link
- Loading skeleton shown while google.script.run.getStatsForDashboard() is in flight
- Quick Generate shortcut: minimal inline form (doc type + target role + generate button)
  that navigates to the Generate tab with those fields pre-populated

---

## SUCCESS CRITERION FOR PHASE 1

After deploying as a Web App (Extensions → Apps Script → Deploy → New Deployment →
Web App, Execute as: Me, Access: Only myself), the URL must load and the Dashboard
must display accurate statistics matching:

```
105 roles | 1,017 bullets | 108 needs review
Narratives: T1: [n] T2: [n] T3: [n] (total 1,347)
Rosetta mappings: 9 | Skills: 20
```

State these numbers in your response once you have read the context files and
confirm they match what you see in the JSON engine schema before writing any code.

Begin with File 1: Config.gs.
