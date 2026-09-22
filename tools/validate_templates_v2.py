#!/usr/bin/env python3
"""
validate_templates_v2.py — Schema conformance check for v2 templates.

Validates that JSON templates:
1. Are valid JSON
2. Conform to the JSON Schema in templates/schema_v2_0.json

Usage:
    python3 validate_templates_v2.py <template.json>
    python3 validate_templates_v2.py --all
"""

import json
import sys
from pathlib import Path
import jsonschema

SCHEMA_PATH = Path(__file__).parent.parent / "templates" / "schema_v2_0.json"

def validate_template(filepath: Path, schema: dict) -> list[str]:
    failures = []
    try:
        content = json.loads(filepath.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"]
    except Exception as e:
        return [f"File read error: {e}"]

    try:
        jsonschema.validate(instance=content, schema=schema)
    except jsonschema.exceptions.ValidationError as e:
        path = ".".join([str(p) for p in e.path]) if e.path else "root"
        failures.append(f"Schema violation at {path}: {e.message}")
    except jsonschema.exceptions.SchemaError as e:
        failures.append(f"Invalid schema: {e.message}")

    return failures

def main() -> int:
    if "--all" in sys.argv:
        templates_dir = SCHEMA_PATH.parent
        files = []
        for prefix in ("resume_", "cover_letter_", "ksc_"):
            files.extend(templates_dir.glob(f"{prefix}*.json"))
    elif len(sys.argv) > 1:
        files = [Path(arg) for arg in sys.argv[1:]]
    else:
        print("Usage: validate_templates_v2.py <file.json> ... or --all")
        return 2

    if not SCHEMA_PATH.exists():
        print(f"Error: Schema not found at {SCHEMA_PATH}")
        return 2

    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error loading schema: {e}")
        return 2

    all_passed = True
    print(f"Validating {len(files)} template(s)...")
    
    for f in sorted(files):
        failures = validate_template(f, schema)
        if failures:
            all_passed = False
            print(f"❌ FAIL: {f.name}")
            for failure in failures:
                print(f"   - {failure}")
        else:
            print(f"✅ PASS: {f.name}")

    if all_passed:
        print("All templates passed schema v2.0 validation.")
        return 0
    else:
        print("Validation failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
