#!/usr/bin/env python3
import os
import re
import hashlib
import json
from pathlib import Path

# Try imports for different file types
try:
    from docx import Document
except ImportError:
    Document = None

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

KNOWLEDGE_DIR = Path("/Users/okgoogle13/Projects/Career Brain/raw_docs/knowledge")
SCRATCH_DIR = Path("/Users/okgoogle13/Projects/Career Brain/scratch")
SCRATCH_DIR.mkdir(parents=True, exist_ok=True)

def get_hash(path: Path) -> str:
    h = hashlib.md5()
    h.update(path.read_bytes())
    return h.hexdigest()

def extract_snippet(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in [".txt", ".md", ".csv"]:
        try:
            content = path.read_text(encoding="utf-8").strip()
            return content[:1500]
        except Exception:
            try:
                content = path.read_text(encoding="latin-1").strip()
                return content[:1500]
            except Exception as e:
                return f"[Error reading text: {e}]"
    elif ext == ".docx":
        if Document is None:
            return "[docx library missing]"
        try:
            doc = Document(str(path))
            text = "\n".join([p.text for p in doc.paragraphs[:10]])
            return text[:1500]
        except Exception as e:
            return f"[Error reading docx: {e}]"
    elif ext == ".pdf":
        if PdfReader is None:
            return "[pdf library missing]"
        try:
            reader = PdfReader(str(path))
            if not reader.pages:
                return "[Empty PDF]"
            first_page_text = reader.pages[0].extract_text() or ""
            return first_page_text[:1500]
        except Exception as e:
            return f"[Error reading pdf: {e}]"
    else:
        return f"[Unsupported extension: {ext}]"

def main():
    files_info = []
    seen_hashes = {}
    
    for f in sorted(KNOWLEDGE_DIR.iterdir()):
        if f.name.startswith("."):
            continue
        if not f.is_file():
            continue
            
        fhash = get_hash(f)
        size = f.stat().st_size
        snippet = extract_snippet(f)
        
        # Check duplicate
        is_duplicate = False
        duplicate_of = None
        if fhash in seen_hashes:
            is_duplicate = True
            duplicate_of = seen_hashes[fhash]
        else:
            seen_hashes[fhash] = f.name
            
        files_info.append({
            "name": f.name,
            "ext": f.suffix.lower(),
            "size": size,
            "hash": fhash,
            "is_duplicate": is_duplicate,
            "duplicate_of": duplicate_of,
            "snippet": snippet
        })
        
    out_path = SCRATCH_DIR / "knowledge_audit_raw.json"
    out_path.write_text(json.dumps(files_info, indent=2), encoding="utf-8")
    print(f"Audited {len(files_info)} files. Raw data saved to {out_path}")

if __name__ == "__main__":
    main()
