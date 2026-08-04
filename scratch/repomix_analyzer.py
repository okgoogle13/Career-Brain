import os
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from pathlib import Path

# Base workspace directory
WORKSPACE_DIR = Path("/Users/okgoogle13/Projects/Career Brain")

# Target XML output path
OUTPUT_PATH = WORKSPACE_DIR / "repomix-vram-summary.xml"

# Allowed extensions and their mapped languages
CODE_EXTENSIONS = {
    ".py": "Python",
    ".ts": "TypeScript",
    ".tsx": "TypeScript React",
    ".js": "JavaScript",
    ".jsx": "JavaScript React",
    ".java": "Java",
    ".cs": "C#",
    ".go": "Go",
    ".rs": "Rust",
    ".cpp": "C++",
    ".c": "C",
    ".h": "C/C++ Header",
    ".rb": "Ruby",
    ".php": "PHP",
    ".swift": "Swift",
    ".kt": "Kotlin"
}

CONFIG_EXTENSIONS = {
    ".sh": "Shell",
    ".ps1": "PowerShell",
    ".yml": "YAML",
    ".yaml": "YAML",
    ".json": "JSON"
}

# Exclude directories
EXCLUDE_DIRS = {
    "data", "tests/fixtures", "docs", "saved_pages", "planning", "research", "prompts",
    "node_modules", "vendor", ".venv", "dist", "build"
}

# Directories that contain bulk data, NOT config
BULK_DATA_DIRS = {
    "database", "database/backups"
}

def should_exclude_path(path: Path) -> bool:
    # Check hidden folders/files (names starting with .)
    for part in path.parts:
        if part.startswith(".") and part not in (".", ".."):
            return True
            
    # Check specific excluded folders relative to workspace
    rel_path_str = str(path.relative_to(WORKSPACE_DIR)).replace("\\", "/")
    
    # Check if any parent dir or the directory itself is in EXCLUDE_DIRS
    parts = rel_path_str.split("/")
    for i in range(len(parts)):
        parent_part = "/".join(parts[:i+1])
        if parent_part in EXCLUDE_DIRS:
            return True
            
    # Also exclude bulk data directories
    for bulk_dir in BULK_DATA_DIRS:
        if rel_path_str.startswith(bulk_dir + "/") or rel_path_str == bulk_dir:
            return True
            
    # Exclude specific files like credentials.json and token.json (contain secrets, not general configs)
    if path.name in ("credentials.json", "token.json"):
        return True
        
    return False

def get_file_language(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in CODE_EXTENSIONS:
        return CODE_EXTENSIONS[ext]
    if ext in CONFIG_EXTENSIONS:
        return CONFIG_EXTENSIONS[ext]
    return ""

def main():
    included_files = []
    total_chars = 0
    
    # Recursively traverse directory
    for root, dirs, files in os.walk(WORKSPACE_DIR):
        # Exclude hidden directories from traversal in place
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        
        for file in files:
            file_path = Path(root) / file
            
            # Skip hidden files
            if file.startswith("."):
                continue
                
            # Skip if file should be excluded
            if should_exclude_path(file_path):
                continue
                
            # Get extension and language
            lang = get_file_language(file_path)
            if not lang:
                continue
                
            # Read character count
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                char_count = len(content)
            except Exception as e:
                print(f"Skipping {file_path} due to read error: {e}")
                continue
                
            rel_path = file_path.relative_to(WORKSPACE_DIR)
            included_files.append({
                "path": str(rel_path).replace("\\", "/"),
                "language": lang,
                "chars": char_count
            })
            total_chars += char_count

    # Sort files by path for consistency
    included_files.sort(key=lambda x: x["path"])

    # Build XML
    project_el = ET.Element("project")
    files_el = ET.SubElement(project_el, "files")
    
    for f in included_files:
        ET.SubElement(files_el, "file", {
            "path": f["path"],
            "language": f["language"],
            "chars": str(f["chars"])
        })
        
    summary_el = ET.SubElement(project_el, "summary")
    total_files_el = ET.SubElement(summary_el, "total_files")
    total_files_el.text = str(len(included_files))
    total_chars_el = ET.SubElement(summary_el, "total_chars")
    total_chars_el.text = str(total_chars)

    # Convert to string and pretty-print using minidom
    xml_str = ET.tostring(project_el, encoding="utf-8")
    parsed_xml = minidom.parseString(xml_str)
    
    # We want exactly the formatting shown in the prompt
    lines = []
    lines.append('<project>')
    lines.append('  <files>')
    for f in included_files:
        lines.append(f'    <file path="{f["path"]}" language="{f["language"]}" chars="{f["chars"]}" />')
    lines.append('  </files>')
    lines.append('  <summary>')
    lines.append(f'    <total_files>{len(included_files)}</total_files>')
    lines.append(f'    <total_chars>{total_chars}</total_chars>')
    lines.append('  </summary>')
    lines.append('</project>')
    
    output_content = "\n".join(lines) + "\n"
    
    OUTPUT_PATH.write_text(output_content, encoding="utf-8")
    print(f"Generated {OUTPUT_PATH}")
    print(f"Total files: {len(included_files)}")
    print(f"Total characters: {total_chars}")

if __name__ == "__main__":
    main()
