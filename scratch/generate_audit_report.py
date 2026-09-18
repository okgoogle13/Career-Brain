#!/usr/bin/env python3
import json
from pathlib import Path

RAW_JSON_PATH = Path("/Users/okgoogle13/Projects/Career Brain/scratch/knowledge_audit_raw.json")
REPORT_PATH = Path("/Users/okgoogle13/.gemini/antigravity-ide/brain/0666d05e-cac5-45ef-b06f-a8ff6cb41b76/knowledge_audit_results.md")
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

def analyze_file(f, all_files):
    name = f["name"]
    ext = f["ext"]
    size_kb = round(f["size"] / 1024, 2)
    snippet = f["snippet"]
    is_dup = f["is_duplicate"]
    dup_of = f["duplicate_of"]
    
    # Defaults
    purpose = "Unclassified reference"
    value = "Med"
    action = "Keep"
    
    # 1. Flag duplicates
    if is_dup:
        return {
            "name": name,
            "ext": ext,
            "size_kb": size_kb,
            "purpose": f"Identical clone of {dup_of}",
            "value": "Very Low",
            "action": "Delete",
            "reason": "Exact byte-for-byte duplicate.",
            "snippet": f"[Duplicate of {dup_of}]"
        }
        
    # Check if a rich .md version of this exact text file exists in the directory
    name_no_ext = Path(name).stem
    ext_lower = ext.lower()
    
    # Recognize categories
    lower_name = name.lower()
    
    # Actual personal resumes/cover letters
    if "nishant" in lower_name or "resume" in lower_name or "cover_letter" in lower_name:
        if "nishant_dougall" in lower_name or "nishant dougall" in lower_name:
            purpose = "Nishant's direct personal application/resume file."
            value = "Very High"
            action = "Keep (Core Pipeline Source)"
        elif "example" in lower_name:
            purpose = "Reference resume example for sector benchmarking."
            value = "Med"
            action = "Keep as reference"
        elif "final combined resumes" in lower_name or "master resume with subtypes" in lower_name:
            purpose = "Master aggregated resume file compiling multiple versions."
            value = "Very High"
            action = "Keep (Core Pipeline Source)"
            
    # Prompts and gem config
    elif "prompt" in lower_name or "customgem" in lower_name or "gemini" in lower_name or "manual" in lower_name:
        purpose = "Prompt engineering template, AI routing instructions, or Custom Gem guide."
        value = "Very High"
        action = "Keep & merge into gem_system_prompt.md"
        
    # Sector terminologies, skills, key words
    elif "keyword" in lower_name or "taxonomy" in lower_name or "glossary" in lower_name or "vocabulary" in lower_name or "verbs" in lower_name or "definitions" in lower_name or "inclusive-language" in lower_name:
        purpose = "Australian community sector-specific skills translation matrix, keyword bank, or glossary."
        value = "High"
        action = "Keep & sync with skills_and_taxonomy.json"
        
    # Criteria examples
    elif "selection criteria" in lower_name or "ksc" in lower_name or "star_method" in lower_name or "summary_examples" in lower_name or "community_services_rag" in lower_name:
        purpose = "STAR/CAR structured narrative templates and examples for Australian community sector."
        value = "Very High"
        action = "Keep & extract to ksc_curated.json"
        
    # Standard third party files (seek, articles, etc)
    elif "seek" in lower_name or "resume writers" in lower_name or "how to tailor" in lower_name or "cheat sheet" in lower_name:
        purpose = "Standard third-party career article/guide downloaded from the web."
        value = "Low"
        action = "Archive (Not specific to Nishant)"
        
    # Documents in cleanup or downloads
    elif "untitled document" in lower_name or "prd" in lower_name or "workflow_diagram" in lower_name:
        purpose = "General project planning, schema requirements, or flowcharts."
        value = "Med"
        action = "Keep for project reference"

    # Specific override rules based on contents
    if "Rosetta Stone Translation" in snippet or "Rosetta Stone Protocol" in snippet:
        purpose = "Rosetta Stone translation taxonomy mapping guides."
        value = "Very High"
        action = "Keep (Core Translation Reference)"
        
    if "LGBTIQA+" in snippet or "inclusive language" in snippet:
        purpose = "Standard guidelines on LGBTIQA+ inclusive language in Australia."
        value = "High"
        action = "Keep (Compliance/Safety Resource)"

    # Format consolidation: if this is a .txt and a matching name exists as .md or .docx, flag the .txt
    if ext_lower in [".txt", ".csv"]:
        for other in all_files:
            other_name = other["name"]
            other_ext = other["ext"].lower()
            if other_name != name and Path(other_name).stem == name_no_ext:
                if other_ext in [".md", ".docx", ".pdf"]:
                    purpose = f"Text copy of matching {other_ext} file."
                    value = "Very Low"
                    action = "Delete"
                    break
        
    return {
        "name": name,
        "ext": ext,
        "size_kb": size_kb,
        "purpose": purpose,
        "value": value,
        "action": action,
        "snippet": snippet[:180].replace('\n', ' ') + "..."
    }

# Read raw
with open(RAW_JSON_PATH, "r", encoding="utf-8") as f_in:
    f_all = json.load(f_in)

analyzed = []
for f in f_all:
    analyzed.append(analyze_file(f, f_all))

# Sort: duplicates/Very Low at the bottom, Very High at the top
value_order = {"Very High": 0, "High": 1, "Med": 2, "Low": 3, "Very Low": 4}
analyzed.sort(key=lambda x: (value_order.get(x["value"], 5), x["name"]))

# Write report
markdown = []
markdown.append("# **Career Brain Knowledge Vault Audit Report**")
markdown.append("\nThis report reviews all **69 files** in `/raw_docs/knowledge/` to identify high-value sources, redundant text dumps, and third-party generic documents. It groups files by value, maps their purpose, and recommends cleanup actions.")

# Count stats
stats = {"Very High": 0, "High": 0, "Med": 0, "Low": 0, "Very Low": 0}
for item in analyzed:
    stats[item["value"]] = stats.get(item["value"], 0) + 1

markdown.append(f"\n## **Audit Summary**\n")
markdown.append(f"| Value Rating | Count | Purpose | Recommended Action |")
markdown.append(f"| --- | --- | --- | --- |")
markdown.append(f"| 🟢 **Very High** | {stats['Very High']} | Gold source resumes, STAR narratives, Custom Gem specs. | Keep & compile in primary JSON engines. |")
markdown.append(f"| 🔵 **High** | {stats['High']} | Sector taxonomies, keywords, action verbs, inclusive language. | Keep & sync with skills taxonomy. |")
markdown.append(f"| 🟡 **Med** | {stats['Med']} | Project schema configs, planning briefs, reference mappings. | Keep for workspace reference. |")
markdown.append(f"| 🟠 **Low** | {stats['Low']} | Generic third-party web guides (e.g. SEEK articles). | Move to `CLEANUP/archive/` (Not personal). |")
markdown.append(f"| 🔴 **Very Low** | {stats['Very Low']} | Identical byte clones, plain text copies of active markdown. | Delete safely to reclaim space and avoid duplicate indexing. |")

markdown.append("\n## **File Registry and Analysis**\n")
markdown.append("| File Name | Size (KB) | Value | Purpose | Action | Summary / Snippet |")
markdown.append("| --- | --- | --- | --- | --- | --- |")

for item in analyzed:
    # Escape pipe char in snippet to avoid breaking table formatting
    clean_snippet = item["snippet"].replace("|", "\\|")
    markdown.append(f"| `{item['name']}` | {item['size_kb']} KB | **{item['value']}** | {item['purpose']} | `{item['action']}` | *{clean_snippet}* |")

# Suggested Automated Conversion Workflow section
markdown.append("\n## **Proposed Automated Conversion & Cleanup Workflow**")
markdown.append("\nTo automate the decluttering of `/raw_docs/knowledge` and enforce a single source of truth, we can run a custom Python maintenance script to execute the following pipeline:")
markdown.append("\n```mermaid\ngraph TD\n    A[Scan raw_docs/knowledge] --> B{Duplicate Check?}\n    B -->|Byte Identical / Hash Match| C[Delete Safely]\n    B -->|Format Redundancy e.g. .txt of .md| D[Retain .md / Delete .txt]\n    B -->|Unique File| E{Value Check?}\n    E -->|Very High / High / Med| F[Sync with normalized_vault/ & JSON engines]\n    E -->|Low / Generic Web Guides| G[Archive to CLEANUP/archive/]\n```")

markdown.append("\n### **Implementation Plan: `clean_knowledge_vault.py`**")
markdown.append("We can write and execute a self-healing maintenance script `clean_knowledge_vault.py` in the project root to:")
markdown.append("1. **Byte-Level Deduplication:** Match MD5 hashes of all 69 files and instantly purge duplicate clones.")
markdown.append("2. **Format Consolidation:** Where `.md` and `.txt`/`.txt.md` variants exist, keep the rich `.md` formatting and delete the redundant flat text files.")
markdown.append("3. **Third-Party Archival:** Move the 7 generic internet articles (SEEK guides, generic resume-writing guides) from `/raw_docs/knowledge` to `/CLEANUP/archive/` so they don't pollute the custom pipeline's extraction context.")
markdown.append("4. **Lineage Preservation:** Log all actions in `output/vault_cleanup.log` so the record of original file structures remains intact.")

with open(REPORT_PATH, "w", encoding="utf-8") as f_out:
    f_out.write("\n".join(markdown))

print(f"Report generated successfully: {REPORT_PATH}")
