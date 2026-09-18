#!/usr/bin/env python3
"""
purge_and_archive_vault.py — Career Brain Workspace Cleanup & Purge Script
========================================================================
Reads consolidated_vault_audit_raw.json, unlinks all "Very Low" value items 
(byte duplicates and temp files), and archives "Low" value files 
(PII documents, non-career files, generic web guides) to enforce cleanliness.
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

# Paths
BASE = Path("/Users/okgoogle13/Projects/Career Brain")
AUDIT_JSON_PATH = BASE / "scratch" / "consolidated_vault_audit_raw.json"
ARCHIVE_PII_DIR = BASE / "CLEANUP" / "archive_personal_pii"
ARCHIVE_GUIDES_DIR = BASE / "CLEANUP" / "archive_third_party"
CLEANUP_LOG = BASE / "output" / "workspace_cleanup.log"

def main():
    print("=" * 60)
    print("CAREER BRAIN - WORKSPACE CLEANUP & DEDUPLICATION WORKFLOW")
    print("=" * 60)
    
    if not AUDIT_JSON_PATH.exists():
        print(f"Error: Audit database JSON not found at {AUDIT_JSON_PATH}.")
        print("Please run scratch/consolidated_vault_audit.py first.")
        return

    # Load registry
    registry = json.loads(AUDIT_JSON_PATH.read_text(encoding="utf-8"))
    
    # Target directories
    ARCHIVE_PII_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_GUIDES_DIR.mkdir(parents=True, exist_ok=True)
    
    stats = {
        "deleted_duplicates": 0,
        "deleted_temps": 0,
        "archived_pii": 0,
        "archived_guides": 0,
        "errors": 0,
        "skipped": 0
    }
    
    log_entries = []
    
    # Process
    for item in registry:
        name = item["name"]
        folder_slug = item["folder"]
        value = item["value"]
        purpose = item["purpose"]
        action = item["action"]
        
        original_path = BASE / folder_slug / name
        if not original_path.exists():
            # Try absolute path
            original_path = Path(folder_slug) / name
            if not original_path.exists():
                # Already deleted or moved
                stats["skipped"] += 1
                continue
                
        # 1. Process "Very Low" - Safe Deletions
        if value == "Very Low":
            # Avoid deleting active source files by accident (failsafe check)
            if folder_slug.startswith("raw_docs"):
                print(f"Failsafe: Skipping deletion of raw_docs file: {name}")
                stats["skipped"] += 1
                continue
                
            try:
                print(f"Deleting duplicate/temp: {folder_slug}/{name}")
                original_path.unlink()
                
                if "temporary" in purpose.lower() or name.startswith("~$"):
                    stats["deleted_temps"] += 1
                    log_entries.append(f"DELETE_TEMP | {folder_slug}/{name} | Word temp file")
                else:
                    stats["deleted_duplicates"] += 1
                    log_entries.append(f"DELETE_DUP | {folder_slug}/{name} | Identical byte duplicate")
            except Exception as e:
                print(f"  [ERROR] Failed to delete {name}: {e}")
                stats["errors"] += 1
                log_entries.append(f"ERROR_DELETE | {folder_slug}/{name} | {e}")
                
        # 2. Process "Low" - Safe Archival
        elif value == "Low":
            # Failsafe check
            if folder_slug.startswith("raw_docs"):
                print(f"Failsafe: Skipping archival of active raw_docs file: {name}")
                stats["skipped"] += 1
                continue
                
            try:
                # Direct personal administrative files go to secure PII archive
                if "personal non-career" in purpose.lower() or "medicare" in purpose.lower() or "ovo energy" in name.lower() or "billing" in name.lower() or "american express" in name.lower():
                    dest_path = ARCHIVE_PII_DIR / name
                    print(f"Archiving PII: {folder_slug}/{name} → CLEANUP/archive_personal_pii/")
                    shutil.move(str(original_path), str(dest_path))
                    stats["archived_pii"] += 1
                    log_entries.append(f"ARCHIVE_PII | {folder_slug}/{name} → archive_personal_pii/")
                # Standard third party web guides go to deep third party advice
                else:
                    dest_path = ARCHIVE_GUIDES_DIR / name
                    print(f"Archiving Guide: {folder_slug}/{name} → CLEANUP/archive_third_party/")
                    shutil.move(str(original_path), str(dest_path))
                    stats["archived_guides"] += 1
                    log_entries.append(f"ARCHIVE_GUIDE | {folder_slug}/{name} → archive_third_party/")
            except Exception as e:
                print(f"  [ERROR] Failed to move {name}: {e}")
                stats["errors"] += 1
                log_entries.append(f"ERROR_MOVE | {folder_slug}/{name} | {e}")
                
    # Write summary log
    summary = [
        "=== CAREER BRAIN WORKSPACE CLEANUP RUN LOG ===",
        f"Timestamp: {datetime.now().isoformat()}",
        f"Actions Taken:",
        f"  Deleted Duplicates        : {stats['deleted_duplicates']}",
        f"  Deleted Temp Files        : {stats['deleted_temps']}",
        f"  Archived Personal PII     : {stats['archived_pii']}",
        f"  Archived Generic Guides   : {stats['archived_guides']}",
        f"Errors Encountered          : {stats['errors']}",
        f"Skipped Files               : {stats['skipped']}",
        "==============================================",
        ""
    ] + log_entries
    
    CLEANUP_LOG.parent.mkdir(parents=True, exist_ok=True)
    CLEANUP_LOG.write_text("\n".join(summary) + "\n", encoding="utf-8")
    
    print("\n" + "=" * 60)
    print("WORKSPACE CLEANUP COMPLETE")
    print("=" * 60)
    print(f"  ✓ Exact Byte Clones Deleted    : {stats['deleted_duplicates']}")
    print(f"  ✓ Word Temp Files Deleted      : {stats['deleted_temps']}")
    print(f"  ✓ Secure PII Files Archived    : {stats['archived_pii']}")
    print(f"  ✓ Third-Party Guides Archived  : {stats['archived_guides']}")
    print(f"  ✗ Errors Encountered          : {stats['errors']}")
    print(f"  - Skipped (Active or Deleted)  : {stats['skipped']}")
    print(f"Detailed cleanup log saved to   : {CLEANUP_LOG}")
    print("=" * 60)

if __name__ == "__main__":
    main()
