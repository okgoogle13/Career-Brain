import json
import glob
import os

theme_files = sorted(glob.glob("templates/theme-*.json"))

print("| File | Theme | Font | Accent | Heading | Identity |")
print("|---|---|---|---|---|---|")

for path in theme_files:
    filename = os.path.basename(path)
    with open(path, 'r') as f:
        data = json.load(f)
    
    theme_name = data.get("visual_identity", {}).get("theme_name", "")
    base_font = data.get("typography", {}).get("base_font", "")
    accent = data.get("palette", {}).get("complementary_accent", "")
    h_size = data.get("typography", {}).get("section_heading_size_pt", "")
    h_weight = data.get("typography", {}).get("section_heading_weight", "")
    
    # Generate identity string
    diffs = data.get("theme_specific_rules", {}).get("visual_differentiators", [])
    identity = ", ".join(diffs) if diffs else data.get("description", "")
    
    # Format line
    print(f"| `templates/{filename}` | {theme_name} | {base_font} | `{accent}` | {h_size}pt/{h_weight} | {identity} |")
