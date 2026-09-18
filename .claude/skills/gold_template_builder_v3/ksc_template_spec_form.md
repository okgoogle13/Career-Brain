# KSC Template Spec

## META
TEMPLATE_TYPE: ksc
VARIANT: <name, lowercase-hyphenated, or "standard">
DOC_ID: <Google Doc ID, or REPLACE_WITH_KSC_GOLDEN_MASTER_DOC_ID>
TARGET_SECTOR: <government / nfp / private / other>

## TOKENS_USED
<One entry per line. Format: TOKEN_NAME → generate_document.py:LINE>
<Read PLACEHOLDER_SCHEMA_V2["ksc"] in generate_document.py to find exact line numbers before writing this section. Do not guess or copy from this form.>
<Every token written here MUST appear in STRUCTURE. Every token in STRUCTURE MUST be cited here.>
CONTACT_NAME → generate_document.py:<line>
TARGET_ROLE → generate_document.py:<line>
EMPLOYER_ORG → generate_document.py:<line>
KSC_CRITERION_1_TEXT → generate_document.py:<line>
KSC_1_CONTEXT → generate_document.py:<line>
KSC_1_ACTION → generate_document.py:<line>
KSC_1_RESULT → generate_document.py:<line>
KSC_1_SUPPORT_BULLET_1 → generate_document.py:<line>
KSC_1_SUPPORT_BULLET_2 → generate_document.py:<line>
<Repeat for each criterion N you include. MAX 6 criteria. Numbering must start at 1 and be contiguous.>

## STRUCTURE
<Ordered list. Each line: N. [Style] content>
<Styles: [Title], [Normal], [Normal italic], [Heading 1], [Heading 2], [Bullet -]>
<Heading text that is a placeholder (e.g. {{KSC_CRITERION_1_TEXT}}) is exempt from the allowed_headings whitelist.>
<Static heading text (non-placeholder) MUST appear in ats_rules.json allowed_headings.>
1. [Title] {{CONTACT_NAME}}
2. [Normal] {{TARGET_ROLE}}
3. [Normal italic] {{EMPLOYER_ORG}}
4. [Heading 1] {{KSC_CRITERION_1_TEXT}}
5. [Normal] Context: {{KSC_1_CONTEXT}}
6. [Normal] Action: {{KSC_1_ACTION}}
7. [Normal] Result: {{KSC_1_RESULT}}
8. [Bullet -] {{KSC_1_SUPPORT_BULLET_1}}
9. [Bullet -] {{KSC_1_SUPPORT_BULLET_2}}
<Repeat blocks 4–9 for each additional criterion, incrementing N. Do not skip numbers.>

## ATS_AUDIT
<Fill each line. PASS or FAIL, followed by em-dash and brief evidence. No decoration.>
columns_max: PASS — single column, no tables, no text boxes
forbidden_chars: PASS — none
allowed_headings: PASS — criterion headings are placeholders (exempt); no static headings used
au_terminology: PASS — none
ksc_word_limit_fit: PASS — CAR structure provides context 40–100w, action 60–200w, result 30–100w per criterion

## REGISTRATION_FRAGMENT
```json
{
  "ksc": {
    "template_doc_id": "REPLACE_WITH_KSC_GOLDEN_MASTER_DOC_ID"
  }
}
```

## DRY_RUN_CMD
python3 generate_document.py --type ksc --target "<Test Role at Test Org>" --criteria <criteria_file.txt> --dry-run
