import zipfile
import xml.etree.ElementTree as ET
import os

docx_path = "/Users/okgoogle13/Projects/Career Brain/source_docs/knowledge/ATS Resume Formatting Checklist.docx"

if not os.path.exists(docx_path):
    print(f"File not found: {docx_path}")
    exit(1)

try:
    with zipfile.ZipFile(docx_path) as z:
        xml_content = z.read("word/document.xml")
        root = ET.fromstring(xml_content)
        
        # Word XML namespaces
        namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        
        paragraphs = []
        for paragraph in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
            texts = [node.text for node in paragraph.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if node.text]
            if texts:
                paragraphs.append("".join(texts))
        
        print("\n".join(paragraphs))
except Exception as e:
    print(f"Error reading docx: {e}")
