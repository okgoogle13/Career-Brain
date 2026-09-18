# Cover Letter Template Spec

## META
TEMPLATE_TYPE: cover_letter
VARIANT: nfp
DOC_ID: REPLACE_WITH_COVER_LETTER_GOLDEN_MASTER_DOC_ID
TARGET_SECTOR: non_profit

## TOKENS_USED
CONTACT_NAME → generate_document.py:105
CONTACT_PHONE → generate_document.py:105
CONTACT_EMAIL → generate_document.py:105
CONTACT_LOCATION → generate_document.py:105
EMPLOYER_CONTACT_NAME → generate_document.py:107
EMPLOYER_ORG → generate_document.py:107
EMPLOYER_ADDRESS → generate_document.py:107
SALUTATION → generate_document.py:108
CURRENT_DATE → generate_document.py:108
HOOK_PARAGRAPH → generate_document.py:110
BRIDGE_PARAGRAPH → generate_document.py:111
EVIDENCE_PARAGRAPH_1 → generate_document.py:112
EVIDENCE_PARAGRAPH_2 → generate_document.py:112
CLOSING_PARAGRAPH → generate_document.py:113
TARGET_ROLE → generate_document.py:115

## STRUCTURE
1. [Title Center] {{CONTACT_NAME}}
2. [Normal Center] {{CONTACT_PHONE}}
3. [Normal Center] {{CONTACT_EMAIL}}
4. [Normal Center] {{CONTACT_LOCATION}}
5. [Normal Center italic] {{TARGET_ROLE}} at {{EMPLOYER_ORG}}
6. [Normal] {{CURRENT_DATE}}
7. [Normal] {{EMPLOYER_CONTACT_NAME}}
8. [Normal] {{EMPLOYER_ORG}}
9. [Normal] {{EMPLOYER_ADDRESS}}
10. [Normal] {{SALUTATION}}
11. [Normal] {{HOOK_PARAGRAPH}}
12. [Normal] {{BRIDGE_PARAGRAPH}}
13. [Normal] {{EVIDENCE_PARAGRAPH_1}}
14. [Normal] {{EVIDENCE_PARAGRAPH_2}}
15. [Normal] {{CLOSING_PARAGRAPH}}
16. [Normal] Sincerely,
17. [Normal] {{CONTACT_NAME}}

## ATS_AUDIT
columns_max: PASS — single column, no tables, no text boxes
forbidden_chars: PASS — none
allowed_headings: PASS — Calibri only, consistent styles
au_terminology: PASS — none

## REGISTRATION_FRAGMENT
```json
{
  "cover_letter": {
    "variants": {
      "nfp": {
        "template_doc_id": "REPLACE_WITH_COVER_LETTER_GOLDEN_MASTER_DOC_ID"
      }
    }
  }
}
```

## DRY_RUN_CMD
python3 generate_document.py --type cover_letter --employer-type nfp --target "Test Role at Test Org" --dry-run
