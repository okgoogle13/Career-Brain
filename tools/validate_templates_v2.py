#!/usr/bin/env python3
"""
validate_templates_v2.py — Lightweight schema conformance check for v2 templates.

Validates that JSON templates:
1. Are valid JSON
2. Contain all required top-level keys for schema v2.0
3. Have schema_version == "2.0"

Usage:
    python3 validate_templates_v2.py <template.json>
    python3 validate_templates_v2.py --all
"""

import json
import sys
from pathlib import Path

REQUIRED_KEYS = {
    "schema_version",
    "template_id",
    "tier",
    "tier_label",
    "doc_type",
    "target_sector",
    "region",
    "placeholder_schema",
    "description",
    "ats_constraints",
    "palette",
    "typography",
    "page",
    "blocks"
}

def validate_template(filepath: Path) -> list[str]:
    failures = []
    
    try:
        content = json.loads(filepath.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"]
    except Exception as e:
        return [f"File read error: {e}"]

    # 1. Check required keys
    missing = REQUIRED_KEYS - set(content.keys())
    if missing:
        failures.append(f"Missing required keys: {', '.join(sorted(missing))}")

    # 2. Check schema_version const
    version = content.get("schema_version")
    if version != "2.0":
        failures.append(f"schema_version must be '2.0', found '{version}'")

    return failures

def main() -> int:
    if "--all" in sys.argv:
        templates_dir = Path(__file__).parent.parent / "templates"
        files = []
        for prefix in ("resume_", "cover_letter_", "ksc_"):
            files.extend(templates_dir.glob(f"{prefix}*.json"))
    elif len(sys.argv) > 1:
        files = [Path(arg) for arg in sys.argv[1:]]
    else:
        print("Usage: validate_templates_v2.py <file.json> ... or --all")
        return 2

    all_passed = True
    print(f"Validating {len(files)} template(s)...")
    
    for f in sorted(files):
        failures = validate_template(f)
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
