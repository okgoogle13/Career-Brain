import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
doc_templates = json.loads((BASE / "config" / "doc_templates.json").read_text())
venv_python = str(BASE / ".venv" / "bin" / "python")

items = []
def traverse(node):
    if "template_doc_id" in node and "theme" in node:
        items.append((node["template_doc_id"], node["theme"]))
    if "variants" in node:
        for k, v in node["variants"].items():
            traverse(v)

traverse(doc_templates.get("resume", {}))

# resume_warm_impact_v1.json failed, let's start from it
start = False
failed = False
for doc_id, theme in items:
    if "resume_warm_impact_v1.json" in theme:
        start = True
    if not start:
        continue

    print(f"\n--- Rebuilding {theme} ({doc_id}) ---")
    res = subprocess.run([venv_python, str(BASE / "tools" / "build_golden_master.py"), theme, "--update", doc_id], cwd=str(BASE))
    if res.returncode != 0:
        failed = True
        print(f"FAILED to rebuild {theme}")
        continue
    
    print(f"--- Auditing {theme} ({doc_id}) ---")
    res = subprocess.run([venv_python, str(BASE / "tools" / "audit_doc_style.py"), doc_id, "--theme", theme], cwd=str(BASE))
    if res.returncode != 0:
        failed = True
        print(f"FAILED audit for {theme}")

if failed:
    sys.exit(1)
