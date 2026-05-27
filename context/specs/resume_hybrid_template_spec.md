# Resume Template Spec

## META
TEMPLATE_TYPE: resume
VARIANT: hybrid
DOC_ID: 16FlPfFjHCYibECNtGORE-KEZtr1ogP_dRayo29L0y_I
TARGET_SECTOR: non_profit

## TOKENS_USED
CONTACT_NAME → generate_document.py:447
CONTACT_PHONE → generate_document.py:448
CONTACT_EMAIL → generate_document.py:449
CONTACT_LOCATION → generate_document.py:450
TARGET_ROLE → generate_document.py:458
PROFESSIONAL_SUMMARY → generate_document.py:526
SKILL_1 → generate_document.py:532
SKILL_2 → generate_document.py:532
SKILL_3 → generate_document.py:532
SKILL_4 → generate_document.py:532
SKILL_5 → generate_document.py:532
SKILL_6 → generate_document.py:532
ROLE_1_TITLE → generate_document.py:536
ROLE_1_ORG → generate_document.py:537
ROLE_1_DATES → generate_document.py:538
ROLE_2_TITLE → generate_document.py:536
ROLE_2_ORG → generate_document.py:537
ROLE_2_DATES → generate_document.py:538
ROLE_3_TITLE → generate_document.py:536
ROLE_3_ORG → generate_document.py:537
ROLE_3_DATES → generate_document.py:538
ROLE_4_TITLE → generate_document.py:536
ROLE_4_ORG → generate_document.py:537
ROLE_4_DATES → generate_document.py:538
ROLE_5_TITLE → generate_document.py:536
ROLE_5_ORG → generate_document.py:537
ROLE_5_DATES → generate_document.py:538
ROLE_6_TITLE → generate_document.py:536
ROLE_6_ORG → generate_document.py:537
ROLE_6_DATES → generate_document.py:538
EDUCATION_1 → generate_document.py:558
EDUCATION_2 → generate_document.py:558
CERT_1 → generate_document.py:562
CERT_2 → generate_document.py:562
CERT_3 → generate_document.py:562

## STRUCTURE
1. [Title Center] {{CONTACT_NAME}}
2. [Normal Center] {{CONTACT_PHONE}}
3. [Normal Center] {{CONTACT_EMAIL}}
4. [Normal Center] {{CONTACT_LOCATION}}
5. [Normal Center italic] {{TARGET_ROLE}}
6. [Heading 1] Summary
7. [Normal] {{PROFESSIONAL_SUMMARY}}
8. [Heading 1] Skills
9. [Normal] {{SKILL_1}} - {{SKILL_2}} - {{SKILL_3}} - {{SKILL_4}} - {{SKILL_5}} - {{SKILL_6}}
10. [Heading 1] Experience
11. [Heading 2] {{ROLE_1_TITLE}}
12. [Normal italic] {{ROLE_1_ORG}} — {{ROLE_1_DATES}}
13. [Heading 2] {{ROLE_2_TITLE}}
14. [Normal italic] {{ROLE_2_ORG}} — {{ROLE_2_DATES}}
15. [Heading 2] {{ROLE_3_TITLE}}
16. [Normal italic] {{ROLE_3_ORG}} — {{ROLE_3_DATES}}
17. [Heading 2] {{ROLE_4_TITLE}}
18. [Normal italic] {{ROLE_4_ORG}} — {{ROLE_4_DATES}}
19. [Heading 2] {{ROLE_5_TITLE}}
20. [Normal italic] {{ROLE_5_ORG}} — {{ROLE_5_DATES}}
21. [Heading 2] {{ROLE_6_TITLE}}
22. [Normal italic] {{ROLE_6_ORG}} — {{ROLE_6_DATES}}
23. [Heading 1] Education
24. [Normal] {{EDUCATION_1}}
25. [Normal] {{EDUCATION_2}}
26. [Heading 1] Certifications
27. [Normal] {{CERT_1}}
28. [Normal] {{CERT_2}}
29. [Normal] {{CERT_3}}

## ATS_AUDIT
columns_max: PASS — single column, no tables, no text boxes
forbidden_chars: PASS — none
allowed_headings: PASS — all 5 headings (Summary, Skills, Experience, Education, Certifications) in allowed_headings whitelist
au_terminology: PASS — none

## REGISTRATION_FRAGMENT
```json
{
  "resume": {
    "variants": {
      "hybrid": {
        "template_doc_id": "16FlPfFjHCYibECNtGORE-KEZtr1ogP_dRayo29L0y_I"
      }
    }
  }
}
```

## DRY_RUN_CMD
python3 generate_document.py --type resume --variant hybrid --target "Test Role at Test Org" --dry-run
