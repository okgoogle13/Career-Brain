#!/usr/bin/env python3
"""
clean_knowledge_vault.py — Career Brain Pipeline Maintenance
============================================================
Safely deduplicates, consolidates formats, and archives generic 
third-party articles from raw_docs/knowledge/ to enforce a 
single source of truth for the ETL extraction pipeline.

Run this script to clean and optimize your knowledge directory.
"""

import os
import shutil
import hashlib
import logging
import sys
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent
KNOWLEDGE_DIR = BASE / "raw_docs" / "knowledge"
ARCHIVE_DIR = BASE / "CLEANUP" / "archive_third_party"
OUTPUT_DIR = BASE / "output"
CLEANUP_LOG = OUTPUT_DIR / "vault_cleanup.log"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger("clean_knowledge_vault")

# Generic third-party web files to move to archive
THIRD_PARTY_PATTERNS = [
    r"seek",
    r"resume writers",
    r"how to tailor",
    r"cheat sheet",
    r"examples of ksc responses long",
    r"resume example",
]

def get_hash(path: Path) -> str:
    h = hashlib.md5()
    h.update(path.read_bytes())
    return h.hexdigest()

def is_third_party(filename: str) -> bool:
    lower_name = filename.lower()
    return any(p in lower_name for p in THIRD_PARTY_PATTERNS)

def main():
    log.info("="*60)
    log.info("CAREER BRAIN — KNOWLEDGE VAULT CLEANUP WORKFLOW")
    log.info(f"Started: {datetime.now().isoformat()}")
    log.info("="*60)

    if not KNOWLEDGE_DIR.exists():
        log.error(f"Knowledge directory does not exist: {KNOWLEDGE_DIR}")
        sys.exit(1)

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    seen_hashes = {}
    actions_taken = []
    
    # 1. First Pass: Compute Hashes and Detect Exact Byte-Level Duplicates
    all_files = sorted(KNOWLEDGE_DIR.iterdir())
    files_to_process = [f for f in all_files if f.is_file() and not f.name.startswith(".")]

    log.info(f"Auditing {len(files_to_process)} files for byte-level duplicates...")
    for f in list(files_to_process):
        fhash = get_hash(f)
        if fhash in seen_hashes:
            original = seen_hashes[fhash]
            log.info(f"  [DUP] Purging byte duplicate: {f.name} (Clone of {original})")
            f.unlink()
            actions_taken.append(f"DELETE_DUPLICATE | {f.name} | Byte-level clone of {original}")
            files_to_process.remove(f)
        else:
            seen_hashes[fhash] = f.name

    # 2. Second Pass: Format Consolidation (Remove flat .txt copy if .md version exists)
    log.info("\nConsolidating format redundancies (e.g. keeping .md over .txt)...")
    for f in list(files_to_process):
        stem = f.stem
        ext = f.suffix.lower()
        
        # If this is a txt file, check if there is an md, docx, or pdf version of the exact same document
        if ext in [".txt", ".csv"]:
            redundant = False
            rich_match = None
            
            for other in files_to_process:
                if other != f and other.stem == stem and other.suffix.lower() in [".md", ".docx", ".pdf"]:
                    redundant = True
                    rich_match = other.name
                    break
            
            # Special check for dual-extension cases like file.md.txt
            if not redundant and stem.endswith(".md"):
                md_stem = stem[:-3]
                for other in files_to_process:
                    if other != f and (other.stem == md_stem or other.name == stem):
                        redundant = True
                        rich_match = other.name
                        break
            
            if redundant:
                log.info(f"  [FORMAT] Purging flat text: {f.name} (Rich source is {rich_match})")
                f.unlink()
                actions_taken.append(f"DELETE_FORMAT_REDUNDANT | {f.name} | Superceded by rich file {rich_match}")
                files_to_process.remove(f)

    # 3. Third Pass: Move generic third-party files to cleanup/archive_third_party
    log.info("\nArchiving generic third-party web reference guides...")
    for f in list(files_to_process):
        if is_third_party(f.name):
            dest = ARCHIVE_DIR / f.name
            log.info(f"  [ARCHIVE] Moving: {f.name} → CLEANUP/archive_third_party/")
            shutil.move(str(f), str(dest))
            actions_taken.append(f"ARCHIVE_THIRD_PARTY | {f.name} | Moved to {ARCHIVE_DIR.name}/")
            files_to_process.remove(f)

    # Write log
    cleanup_log_content = [
        f"=== CAREER BRAIN VAULT CLEANUP LOG ===",
        f"Executed: {datetime.now().isoformat()}",
        f"Actions Taken: {len(actions_taken)}",
        "========================================",
        ""
    ] + actions_taken
    
    CLEANUP_LOG.write_text("\n".join(cleanup_log_content) + "\n", encoding="utf-8")
    
    log.info("\n" + "="*60)
    log.info("CLEANUP WORKFLOW SUMMARY")
    log.info("="*60)
    log.info(f"  Safe Deletions (Duplicates/Redundant): {sum(1 for a in actions_taken if 'DELETE' in a)}")
    log.info(f"  Archived Web Reference Files        : {sum(1 for a in actions_taken if 'ARCHIVE' in a)}")
    log.info(f"  Remaining Clean Pipeline Sources     : {len(files_to_process)}")
    log.info(f"  Action Log Saved To                  : {CLEANUP_LOG}")
    log.info("="*60)

if __name__ == "__main__":
    main()
