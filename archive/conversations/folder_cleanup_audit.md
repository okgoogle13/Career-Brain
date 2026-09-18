# Career Brain — Folder Cleanup Audit
**Goal:** Slim project folder for upload to Gemini web chat.  
**Current total size:** ~1.4 GB (includes `.git`) / ~900 MB (excluding `.git`)

---

## 🔴 Remove — Safe, Massive Wins

| Path | Size | Reason |
|---|---|---|
| `archive/` | **372 MB** | Legacy files — AGENTS.md explicitly says "do not re-ingest without instruction". Source docs are on Google Drive. |
| `.venv/` | **279 MB** | Python virtualenv — recreatable with `pip install -r requirements.txt`. Never needed in uploads. |
| `node_modules/` | **161 MB** | npm packages for `firebase` only — recreatable with `npm install`. Never needed in uploads. |
| `source_docs/` | **45 MB** | Raw binary source files (PDFs, DOCXs) — you confirmed these are on Google Drive. Already extracted to `processed/`. |
| `.git/` | **497 MB** | Git history — not useful for Gemini chat context. |

**Subtotal freed: ~1.35 GB**

---

## 🟡 Remove — Safe, Smaller Wins

| Path | Size | Reason |
|---|---|---|
| `context/CareerBrain_AI_Context.xml` | **6.9 MB** | Large repomix dump — redundant if uploading the actual project folder |
| `context/CareerBrain_Targeted_Context.xml` | **352 KB** | Another repomix dump |
| `context/CareerBrain_Themes_Handover_Context.xml` | **200 KB** | AI session handover — likely stale |
| `context/repomix_gas_context.xml` | **108 KB** | Repomix dump |
| `context/repomix_perplexity_context_slim.xml` | **93 KB** | Repomix dump |
| `CareerBrain_Database_Optimizer.xml` | **168 KB** | Root-level repomix/optimizer XML |
| `database/backups/` | unknown | Old backup copies of JSON engines — check if needed |
| `database/*.png` / `database/*.html` | ~1.5 MB | Preview screenshots and HTML files (not pipeline data) |
| `database/harvest_run.log` | **33 KB** | Old run log |
| `database/workspace_cleanup.log` | **19 KB** | Old cleanup log |
| `database/vault_cleanup.log` | **1.5 KB** | Old cleanup log |
| `database/doc_generation_report_*.json` | ~2 KB | Old test report files (4 files) |
| `processed/` | **4 MB** | Extracted `.txt` files — these are intermediate pipeline artefacts, regeneratable. Only keep if you want Gemini to read raw text. |
| `__pycache__/` (root + pipeline/ + tools/ + tests/) | ~116 KB | Python bytecode — always safe to delete |
| `package-lock.json` | **44 KB** | npm lock file — not needed if removing node_modules |
| `package.json` | small | Only has `firebase` dep — keep if you need Firebase later, delete if not |
| `scratch/` | **104 KB** | One-off investigation scripts — check individually |

---

## 🟢 Keep — Core Project Files

| Path | Size | Reason |
|---|---|---|
| `pipeline/` | 272 KB | ETL scripts — the brain of the project |
| `tools/` | 352 KB | Doc generation tools |
| `database/career_history_enriched.json` | 702 KB | Core output — Pillar 1 |
| `database/ksc_curated.json` | 2.3 MB | Core output — Pillar 2 |
| `database/skills_and_taxonomy.json` | 74 KB | Core output — Pillar 3 |
| `database/Career_Brain_Knowledge.md` | 12 KB | Human-readable knowledge summary |
| `database/quality_audit_report.md` | 64 KB | Quality gate output |
| `database/parsing_errors.log` | 65 KB | Quality gate — check after every run |
| `templates/` | 240 KB | Google Docs theme configs |
| `config/` | 16 KB | Runtime config files |
| `context/specs/` | small | Template format specs |
| `context/*.md` | ~150 KB total | AI session docs, handover briefs, task specs |
| `planning/` | 84 KB | Planning and spec docs |
| `AGENTS.md` | 12 KB | Core operating instructions |
| `Career Brain Manifesto.md` | 12 KB | System design doc |
| `gem_system_prompt.md` | 8 KB | Google AI Studio Gem prompt |
| `BUILD_SPECS.md` | 24 KB | Phase 5 specs |
| `requirements.txt` | 4 KB | Python deps |
| `ai/` | 464 KB | Flows, schemas, prompts |
| `tests/` | 124 KB | Test files |
| `.claude/` | 52 KB | Claude skills (versioned) |
| `credentials.json` / `token.json` | small | Google API auth — keep locally |

---

## 📊 Estimated Post-Cleanup Size

| Scenario | Est. Size |
|---|---|
| Remove all 🔴 items (incl. `.git`) | ~50–80 MB |
| Remove all 🔴 + 🟡 items | ~30–50 MB |
| Minimal "Gemini upload" slice (keep only/core data) | ~5–10 MB |

---

## ⚠️ Notes Before Deleting

1. **`.gitignore` update recommended** — Add `.venv/`, `node_modules/`, `__pycache__/`, `source_docs/`, `archive/` so they don't re-appear on next push.
2. **`source_docs/` caution** — Only delete locally if you're confident Google Drive backup is complete and current.
3. **`processed/` caution** — These `.txt` extractions are regeneratable from `normalize_vault.py`, but only if `source_docs/` is available. If you delete both, you'll need to re-run Phase 1 from Google Drive.
4. **`credentials.json` / `token.json`** — Do NOT include in any upload (PII + auth tokens). Add to `.gitignore` if not already there.
5. **`database/ksc_curated_tier1.json`** (759 KB, May 21) — Older copy from before enrichment — likely superseded by `ksc_curated.json` (May 30). Candidate for removal.

---

## Suggested `.gitignore` additions
```
.venv/
node_modules/
__pycache__/
*.pyc
source_docs/
archive/
*.xml
credentials.json
token.json
database/backups/
database/*.log
database/*.png
database/*.html
```
