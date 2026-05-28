#!/usr/bin/env python3
"""
Rename 5 section headings in the hybrid resume Golden Master Google Doc.
Uses replaceAllText to be safe — only touches exact heading strings.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "tools"))

from generate_document import build_google_services

DOC_ID = "16FlPfFjHCYibECNtGORE-KEZtr1ogP_dRayo29L0y_I"

# Each tuple: (current text, replacement text)
# Ordered most-specific first to avoid partial-match collisions
RENAMES = [
    ("PROFESSIONAL SUMMARY", "Summary"),
    ("SUMMARY", "Summary"),
    ("CORE COMPETENCIES", "Skills"),
    ("CORE SKILLS", "Skills"),
    ("PROFESSIONAL EXPERIENCE", "Experience"),
    ("WORK EXPERIENCE", "Experience"),
    ("EDUCATION", "Education"),
    ("CERTIFICATIONS AND LICENSING", "Certifications"),
    ("CERTIFICATIONS", "Certifications"),
]

def build_replace_requests(renames):
    requests = []
    for old, new in renames:
        if old == new:
            continue
        requests.append({
            "replaceAllText": {
                "containsText": {"text": old, "matchCase": True},
                "replaceText": new,
            }
        })
    return requests

def main():
    print("Authenticating...")
    docs_service, _ = build_google_services()

    # Fetch doc to verify it exists and show current headings
    doc = docs_service.documents().get(documentId=DOC_ID).execute()
    print(f"Opened: {doc.get('title', '(untitled)')}")

    # Show existing heading paragraphs for confirmation
    headings_found = []
    for el in doc.get("body", {}).get("content", []):
        para = el.get("paragraph", {})
        style = para.get("paragraphStyle", {}).get("namedStyleType", "")
        if style in ("HEADING_1", "HEADING_2", "TITLE"):
            text = "".join(
                run.get("textRun", {}).get("content", "")
                for run in para.get("elements", [])
            ).strip()
            if text:
                headings_found.append((style, text))

    print("\nCurrent headings in document:")
    for style, text in headings_found:
        print(f"  [{style}] {text}")

    requests = build_replace_requests(RENAMES)
    if not requests:
        print("\nNothing to replace.")
        return

    print(f"\nApplying {len(requests)} replacement(s)...")
    response = docs_service.documents().batchUpdate(
        documentId=DOC_ID,
        body={"requests": requests},
    ).execute()

    # Report replacement counts
    for i, reply in enumerate(response.get("replies", [])):
        result = reply.get("replaceAllText", {})
        count = result.get("occurrencesChanged", 0)
        old = RENAMES[i][0]
        new = RENAMES[i][1]
        if count:
            print(f"  ✓ '{old}' → '{new}' ({count} occurrence{'s' if count != 1 else ''})")
        else:
            print(f"  — '{old}' not found (skipped)")

    print("\nDone. Verify heading styles remain as Heading 1 in Google Docs.")

if __name__ == "__main__":
    main()
