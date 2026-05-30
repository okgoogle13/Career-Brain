from pathlib import Path
import json, zipfile

base = Path(__file__).parent
zip_path = base / 'careerbrain-handover-package.zip'
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for p in base.iterdir():
        if p.name == zip_path.name:
            continue
        if p.is_file():
            zf.write(p, arcname=p.name)
print(zip_path)
