# Career Brain

Local Python ETL pipeline for building the Career Brain Database from career documents.

## Phase 5: Google Docs Template Generation

`generate_document.py` clones a Golden Master Google Doc and replaces a fixed placeholder schema from existing `output/` JSON files.

```bash
python3 generate_document.py --target "Peer Worker" --template resume --out-report output/doc_generation_report.json
python3 generate_document.py --target "Peer Worker" --template cover_letter --out-report output/doc_generation_report.json
```

Use `--dry-run` to validate local JSON parsing and placeholder mapping without calling Google APIs.

```bash
python3 generate_document.py --target "Peer Worker" --template resume --dry-run
```

### Template Config

Set the Golden Master document IDs in `doc_templates.json`.

```json
{
  "resume": {
    "template_doc_id": "GOOGLE_DOC_ID"
  },
  "cover_letter": {
    "template_doc_id": "GOOGLE_DOC_ID"
  }
}
```

Supported placeholders:

```text
{{TARGET_ROLE}}
{{SUMMARY}}
{{BULLET_1}} ... {{BULLET_6}}
{{KSC_RESPONSE_1}} ... {{KSC_RESPONSE_3}}
```

Resume templates should use the bullet placeholders. Cover letter templates should use the KSC response placeholders.

### Google Auth

Install dependencies with:

```bash
pip install -r requirements.txt
```

OAuth desktop app flow:

```bash
export GOOGLE_OAUTH_CLIENT_SECRETS=credentials.json
export GOOGLE_OAUTH_TOKEN=token.json
python3 generate_document.py --target "Peer Worker" --template resume
```

Service account flow:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=service-account.json
python3 generate_document.py --target "Peer Worker" --template resume
```

For service accounts, share each Golden Master Google Doc with the service account email.

### Output Report

The script writes `output/doc_generation_report.json` with the run timestamp, selected template, generated document ID/link, placeholder fill counts, unresolved tokens, and warnings. It does not log full resume bullets, narratives, or source document content.
