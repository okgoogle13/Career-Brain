#!/usr/bin/env python3
"""
Automates building and registering Golden Masters for all 14 compiled resume templates.
Uses build_golden_master.py to build Google Docs, audits them with audit_doc_style.py,
and updates config/doc_templates.json with the generated Doc IDs.
"""
import json
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
CONFIG_PATH = BASE_DIR / "config" / "doc_templates.json"
TEMPLATES_DIR = BASE_DIR / "templates"

# The 15 templates to process (key: template suffix, value: template JSON filename)
TEMPLATES = {
    "graphite_ledger": "resume_graphite_ledger_v1.json",
    "citrus_edge": "resume_citrus_edge_v1.json",
    "emerald_transit": "resume_emerald_transit_v1.json",
    "copper_teal_circuit": "resume_copper_teal_circuit_v1.json",
    "violet_signal": "resume_violet_signal_v1.json",
    "solar_gradient": "resume_solar_gradient_v1.json",
    "nordic_neon": "resume_nordic_neon_v1.json",
    "terracotta_service": "resume_terracotta_service_v1.json",
    "rainbow_minimal": "resume_rainbow_minimal_v1.json",
    "terminal_signal": "resume_terminal_signal_v1.json",
    "horizon_edge": "resume_horizon_edge_v1.json",
    "broadside_press": "resume_broadside_press_v1.json",
    "clay_canvas": "resume_clay_canvas_v1.json",
    "cyan_blueprint": "resume_cyan_blueprint_v1.json",
    "midnight_blueprint": "resume_midnight_blueprint_v1.json"
}

# Pre-built IDs to reuse and avoid rebuilding
PREBUILT_IDS = {
    "copper_teal_circuit": "124DpzQrY6p56vYrHwKEong10VYRei6wU8dFQFdGBkGQ",
    "nordic_neon": "1ZsDf4N-Og68K6UMRS09jUXYLCc6ulqceYqGQOtQ9vfA",
    "terminal_signal": "1MeDZdqXi36_vXQmdCU8XdbPy2VC2rknXEQQJby28SM8",
    "horizon_edge": "1A_tGkoYv5KYt5BdabbRmGtfk708LNlC9ROUitGKn9kQ",
    "broadside_press": "19y2G0iG2ZAMj9sP1N4d0LxgICGcoivLi6Ta7Un3_Bbw",
    "clay_canvas": "1oIxr8PmxTzQc_mk_GFAAUxUtSrOvuNWFwjd6HQkVU6M",
    "cyan_blueprint": "1-nqOlBU6aG48_wVK5lwthGkJY5h3UtEfa8Uv_FpCuas",
    "midnight_blueprint": "1cD-OSbY0-DSw0Dbav96DflrGCxnae9_vgyJp1JPSuhc"
}

def run_command(args: list[str]) -> str:
    res = subprocess.run(args, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(args)}\nStdout: {res.stdout}\nStderr: {res.stderr}")
    return res.stdout.strip()

def main():
    print("Loading templates config ...")
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    
    variants = config.setdefault("resume", {}).setdefault("variants", {})
    
    results = {}
    
    for key, filename in TEMPLATES.items():
        template_path = TEMPLATES_DIR / filename
        if not template_path.exists():
            print(f"Skipping {key} — {filename} not found.")
            continue
            
        print(f"\nProcessing {key} ...")
        
        # 1. Build or reuse
        if key in PREBUILT_IDS:
            doc_id = PREBUILT_IDS[key]
            print(f"  Reusing built Doc ID: {doc_id}")
        else:
            print("  Building Golden Master Google Doc ...")
            try:
                doc_id = run_command(["python3", "tools/build_golden_master.py", str(template_path)])
                # Extract clean doc_id (last line)
                doc_id = doc_id.splitlines()[-1].strip()
                print(f"  Generated Doc ID: {doc_id}")
            except Exception as e:
                print(f"  ERROR building {key}: {e}")
                continue
                
        # 2. Audit style
        print("  Auditing style ...")
        try:
            audit_res = run_command(["python3", "tools/audit_doc_style.py", doc_id, "--theme", str(template_path)])
            print(f"  Audit result: {audit_res}")
        except Exception as e:
            print(f"  ERROR auditing {key}: {e}")
            continue
            
        # 3. Save to registration dict
        variants[key] = {
            "template_doc_id": doc_id,
            "theme": f"templates/{filename}"
        }
        results[key] = doc_id

    # Write updated config
    CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")
    print("\nUpdated config/doc_templates.json successfully!")
    
    print("\nRegistration Summary:")
    print("--------------------")
    for key, doc_id in results.items():
        print(f"{key}: {doc_id}")

if __name__ == "__main__":
    main()
