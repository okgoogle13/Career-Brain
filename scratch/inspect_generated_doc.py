#!/usr/bin/env python3
"""Quick inspection of a generated Google Doc — headings, token resolution, structure."""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "tools"))
from generate_document import build_google_services

DOC_ID = "13AumoTN_jR0jZULgCJ48lNhJ7g_pyg52r89dBaqyvh4"

def main():
    docs_service, _ = build_google_services()
    doc = docs_service.documents().get(documentId=DOC_ID).execute()
    print(f"Title: {doc.get('title')}\n")

    import re
    PLACEHOLDER_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")
    unresolved = []
    blank_headings = []
    headings = []
    paragraphs = []

    for el in doc.get("body", {}).get("content", []):
        para = el.get("paragraph")
        if not para:
            continue
        style = para.get("paragraphStyle", {}).get("namedStyleType", "NORMAL_TEXT")
        text = "".join(
            run.get("textRun", {}).get("content", "")
            for run in para.get("elements", [])
        ).strip()
        if not text:
            continue

        tokens = PLACEHOLDER_RE.findall(text)
        if tokens:
            unresolved.extend(tokens)

        if style in ("HEADING_1", "HEADING_2", "TITLE"):
            headings.append((style, text))
            if not text or text.isspace():
                blank_headings.append(style)
        else:
            paragraphs.append(text[:120])

    print("=== HEADINGS ===")
    for h, t in headings:
        print(f"  [{h}] {t}")

    print("\n=== BODY PARAGRAPHS (first 20) ===")
    for p in paragraphs[:20]:
        print(f"  {p}")

    print(f"\n=== UNRESOLVED TOKENS ({len(unresolved)}) ===")
    for t in sorted(set(unresolved)):
        print(f"  {t}")

    print(f"\nTotal unresolved: {len(unresolved)}")
    print(f"Total headings: {len(headings)}")

if __name__ == "__main__":
    main()
