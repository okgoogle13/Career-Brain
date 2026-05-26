#!/usr/bin/env python3
"""
organise_raw_docs.py — Career Brain Pipeline Pre-step
Moves source files from archive/ into source_docs/
with include/exclude rules applied. Non-reversible — ensure backup exists.
"""

import os
import shutil
import re
from pathlib import Path

BASE = Path(__file__).parent.parent  # project root
CLEANUP = BASE / "archive"
RAW = BASE / "source_docs"

# Files to skip regardless of location
SKIP_PATTERNS = [
    r"^~\$",                        # Word temp lockfiles
    r"\(Converted - \d{4}-\d{2}-\d{2}",  # Google Docs auto-converted duplicates
    r"\(\d+\)\.(docx|doc|pdf)$",   # Numbered re-download duplicates (handled by hash later)
    r"\.DS_Store$",
    r"\.zip$",
    r"\.xlsx$",
    r"\.csv$",
    r"\.png$",
    r"\.jpg$",
    r"\.jpeg$",
    r"\.mp4$",
    r"\.psl$",
    r"\.textClipping$",
    r"\.html$",
    r"\.json$",
    r"\.dotx$",
    r"\.dotm$",
]

# Extra skip patterns for Chromebook Downloads (personal files)
CHROMEBOOK_SKIP_PATTERNS = SKIP_PATTERNS + [
    # Financial / personal
    r"American Express",
    r"OVO Energy",
    r"Invoice",
    r"INVOICE",
    r"Receipt",
    r"SaleReceipt",
    r"Portfolio",
    r"Payment History",
    r"activity.*\.pdf",
    r"Compassionate_release",
    r"Partner-Statutory",
    r"Statutory-declaration",
    r"Supporting-statement",
    r"Application-form-Fee-waiver",
    r"TLS_Dividend",
    r"Gmail -",
    r"My Billing",
    r"Contract BMW",
    r"c59631e6",
    r"postbox_analysis",
    r"nishant-d-and-lucy",
    # Code / project files
    r"Index\.tsx",
    r"code\.(css|py|sh|txt)",
    r"populate_profile\.py",
    r"create-re\.psl",
    r"careercopilot-ses",
    r"client_secret",
    r"material-theme",
    r"pdf_themes",
    r"marketplace\.html",
    r"mood-colorizer\.html",
    r"radon_report",
    r"WhatsApp Chat",
    r"3-Week Melbourne",
    r"Travel planner",
    r"PXL_\d+",
    r"ChatGPT Image",
    r"kr-hero",
    r"kr-solidarity",
    r"New-Design-Reference",
    r"generated-image",
    r"ai_chatbot_workflow",
    r"fefc392e",
    r"6a056fb0",
    r"productionresults",
    r"m8q813wo",
    r"mawoi04o",
    r"Screenshot",
    r"2025-0[6789]-07\.pdf",  # monthly statements
    r"2025-1[012]-07\.pdf",
    r"8674085122164083",
    r"588F539E",
    r"INVOICE_MM",
    r"Salesinvoice",
    r"logs_\d+\.zip",
    r"exported-assets",
    r"e2e-test-results",
    r"drive-download",
    r"🚀 WhatsApp Hub",
]

# Chromebook Downloads files to explicitly INCLUDE (career-relevant)
CHROMEBOOK_INCLUDE = [
    "final combined resumes.md",
    "Master Resume with subtypes.md",
    "Nishant_Dougall_Master_Resume.pdf",
    "Gold Standard Knowledge Artifact.md",
    "Gold Standard Knowledge Artifact.pdf",
    "community_services_rag.md",
    "community_services_rag_CAR_responses_examples.md",
    "star_method_examples.md",
    "summary_examples.md",
    "australian_sector_glossary.md",
    "skill_taxonomy_community_services.md",
    "IAP Launch Interview Prep Responses.txt",
    "Nishant_Dougall_Cover_Letter_Harm_Reduction_ Peer_Worker_HRvic.pdf",
    "Nishant_Dougall_Cover_Letter_Project_Worker_Harm_Reduction_Victoria.pdf",
    "Nishant_Dougall_Cover_Letter_TGD_Peer Navigator.pdf",
    "Nishant_Dougall_Master_Resume.pdf",
    "Nishant_Dougall_Resume_Project_Worker_Harm_Reduction_Victoria.pdf",
    "Nishant_Dougall_Resume_TGD_Peer_Navigator.pdf",
    "Nishant_Dougall_References_Project_Worker_Harm_Reduction_Victoria.pdf",
    "Nishant Dougall - Harm Reduction Peer Worker Resume-cover-letter.pdf",
    "WORKFLOW_DIAGRAM.md",
    "ai_resume_agent_manual.md",
    "audit_report.md",
    "can you compile all of this information about comm.md",
    "Untitled document.md",
    "gemini_job_prompts.md",
    "cyberpop_context.md",
    "community_services_keywords.csv",  # keep for knowledge
    "australian_sector_glossary.docx",
    "Definitions.docx",
    "LGBTIQA-inclusive-language-guide.docx",
    "Solution Design Resume Agent Requirements.md",
    "Prompt & Context Engineering for Resume Agents_ Be.md",
    "Can you help me draft the following knowledge docu.md",
]

def should_skip(filename, extra_patterns=None):
    patterns = extra_patterns or SKIP_PATTERNS
    for p in patterns:
        if re.search(p, filename):
            return True
    return False

def move_file(src: Path, dst_dir: Path, log: list):
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / src.name
    if dst.exists():
        log.append(f"  SKIP (exists, already moved): {src.name}")
        return
    shutil.move(str(src), str(dst))
    log.append(f"  MOVED: {src.name}")

def main():
    log = []
    counts = {}

    # --- RESUMES ---
    log.append("\n=== source_docs/resumes/ ===")
    src_dir = CLEANUP / "Old resumes "
    dst_dir = RAW / "resumes"
    n = 0
    for f in sorted(src_dir.iterdir()):
        if f.is_file() and not should_skip(f.name):
            move_file(f, dst_dir, log)
            n += 1
    counts["resumes"] = n

    # --- COVER LETTERS ---
    log.append("\n=== source_docs/cover_letters/ ===")
    src_dir = CLEANUP / "Old cover letters"
    dst_dir = RAW / "cover_letters"
    n = 0
    for f in sorted(src_dir.iterdir()):
        if f.is_file() and not should_skip(f.name):
            move_file(f, dst_dir, log)
            n += 1
    counts["cover_letters"] = n

    # --- KSC ---
    log.append("\n=== source_docs/ksc/ ===")
    src_dir = CLEANUP / "Key Selection Criteria Responses"
    dst_dir = RAW / "ksc"
    n = 0
    for f in sorted(src_dir.iterdir()):
        if f.is_file() and not should_skip(f.name):
            move_file(f, dst_dir, log)
            n += 1
    counts["ksc"] = n

    # --- REFERENCES ---
    log.append("\n=== source_docs/references/ ===")
    src_dir = CLEANUP / "References"
    dst_dir = RAW / "references"
    n = 0
    for f in sorted(src_dir.iterdir()):
        if f.is_file() and not should_skip(f.name):
            move_file(f, dst_dir, log)
            n += 1
    counts["references"] = n

    # --- KNOWLEDGE: AI Knowledge Files ---
    log.append("\n=== source_docs/knowledge/ [from AI Knowledge Files] ===")
    src_dir = CLEANUP / "AI Knowledge Files"
    dst_dir = RAW / "knowledge"
    n = 0
    for f in sorted(src_dir.iterdir()):
        if f.is_file() and not should_skip(f.name):
            move_file(f, dst_dir, log)
            n += 1
    counts["knowledge_ai"] = n

    # --- KNOWLEDGE: CUSTOM GEM REFERENCE STUFF ---
    log.append("\n=== source_docs/knowledge/ [from CUSTOM GEM REFERENCE STUFF] ===")
    src_dir = CLEANUP / "CUSTOM GEM REFERENCE STUFF"
    dst_dir = RAW / "knowledge"
    n = 0
    for f in sorted(src_dir.iterdir()):
        if f.is_file() and not should_skip(f.name):
            move_file(f, dst_dir, log)
            n += 1
    counts["knowledge_custom"] = n

    # --- KNOWLEDGE: Selected Chromebook Downloads ---
    log.append("\n=== source_docs/knowledge/ [from Chromebook Downloads — selected only] ===")
    src_dir = CLEANUP / "Chromebook Downloads"
    dst_dir = RAW / "knowledge"
    n = 0
    for fname in CHROMEBOOK_INCLUDE:
        f = src_dir / fname
        if f.exists() and f.is_file():
            move_file(f, dst_dir, log)
            n += 1
        else:
            log.append(f"  MISSING (skipped): {fname}")
    counts["knowledge_chromebook"] = n

    # Print summary
    print("\n" + "="*60)
    print("ORGANISE RAW DOCS — COMPLETE")
    print("="*60)
    print(f"  resumes/        : {counts['resumes']} files")
    print(f"  cover_letters/  : {counts['cover_letters']} files")
    print(f"  ksc/            : {counts['ksc']} files")
    print(f"  references/     : {counts['references']} files")
    print(f"  knowledge/      : {counts['knowledge_ai'] + counts['knowledge_custom'] + counts['knowledge_chromebook']} files")
    print(f"  TOTAL           : {sum(counts.values())} files")
    print("="*60)
    print("\n".join(log))

if __name__ == "__main__":
    main()
