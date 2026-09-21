import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from generate_document import build_google_services

doc_id = sys.argv[1]
docs_service, _ = build_google_services()
doc = docs_service.documents().get(documentId=doc_id).execute()

for el in doc.get("body", {}).get("content", []):
    para = el.get("paragraph")
    if not para:
        continue
    for pe in para.get("elements", []):
        tr = pe.get("textRun")
        if tr is None:
            continue
        sys.stdout.write(tr.get("content", ""))
