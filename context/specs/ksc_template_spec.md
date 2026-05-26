# KSC Template Spec

## META
TEMPLATE_TYPE: ksc
VARIANT: standard
DOC_ID: REPLACE_WITH_KSC_GOLDEN_MASTER_DOC_ID
TARGET_SECTOR: government

## TOKENS_USED
CONTACT_NAME → generate_document.py:120
CONTACT_PHONE → generate_document.py:120
CONTACT_EMAIL → generate_document.py:120
CONTACT_LOCATION → generate_document.py:120
TARGET_ROLE → generate_document.py:120
EMPLOYER_ORG → generate_document.py:120
KSC_CRITERION_1_TEXT → generate_document.py:126
KSC_1_CONTEXT → generate_document.py:127
KSC_1_ACTION → generate_document.py:128
KSC_1_RESULT → generate_document.py:129
KSC_1_SUPPORT_BULLET_1 → generate_document.py:130
KSC_1_SUPPORT_BULLET_2 → generate_document.py:130
KSC_CRITERION_2_TEXT → generate_document.py:126
KSC_2_CONTEXT → generate_document.py:127
KSC_2_ACTION → generate_document.py:128
KSC_2_RESULT → generate_document.py:129
KSC_2_SUPPORT_BULLET_1 → generate_document.py:130
KSC_2_SUPPORT_BULLET_2 → generate_document.py:130
KSC_CRITERION_3_TEXT → generate_document.py:126
KSC_3_CONTEXT → generate_document.py:127
KSC_3_ACTION → generate_document.py:128
KSC_3_RESULT → generate_document.py:129
KSC_3_SUPPORT_BULLET_1 → generate_document.py:130
KSC_3_SUPPORT_BULLET_2 → generate_document.py:130
KSC_CRITERION_4_TEXT → generate_document.py:126
KSC_4_CONTEXT → generate_document.py:127
KSC_4_ACTION → generate_document.py:128
KSC_4_RESULT → generate_document.py:129
KSC_4_SUPPORT_BULLET_1 → generate_document.py:130
KSC_4_SUPPORT_BULLET_2 → generate_document.py:130
KSC_CRITERION_5_TEXT → generate_document.py:126
KSC_5_CONTEXT → generate_document.py:127
KSC_5_ACTION → generate_document.py:128
KSC_5_RESULT → generate_document.py:129
KSC_5_SUPPORT_BULLET_1 → generate_document.py:130
KSC_5_SUPPORT_BULLET_2 → generate_document.py:130
KSC_CRITERION_6_TEXT → generate_document.py:126
KSC_6_CONTEXT → generate_document.py:127
KSC_6_ACTION → generate_document.py:128
KSC_6_RESULT → generate_document.py:129
KSC_6_SUPPORT_BULLET_1 → generate_document.py:130
KSC_6_SUPPORT_BULLET_2 → generate_document.py:130

## STRUCTURE
1. [Title Center] {{CONTACT_NAME}}
2. [Normal Center] {{CONTACT_PHONE}}
3. [Normal Center] {{CONTACT_EMAIL}}
4. [Normal Center] {{CONTACT_LOCATION}}
5. [Normal Center italic] {{TARGET_ROLE}} at {{EMPLOYER_ORG}}
6. [Heading 1 Numbered] {{KSC_CRITERION_1_TEXT}}
7. [Normal] Context: {{KSC_1_CONTEXT}}
8. [Normal] Action: {{KSC_1_ACTION}}
9. [Normal] Result: {{KSC_1_RESULT}}
10. [Bullet -] {{KSC_1_SUPPORT_BULLET_1}}
11. [Bullet -] {{KSC_1_SUPPORT_BULLET_2}}
12. [Heading 1 Numbered] {{KSC_CRITERION_2_TEXT}}
13. [Normal] Context: {{KSC_2_CONTEXT}}
14. [Normal] Action: {{KSC_2_ACTION}}
15. [Normal] Result: {{KSC_2_RESULT}}
16. [Bullet -] {{KSC_2_SUPPORT_BULLET_1}}
17. [Bullet -] {{KSC_2_SUPPORT_BULLET_2}}
18. [Heading 1 Numbered] {{KSC_CRITERION_3_TEXT}}
19. [Normal] Context: {{KSC_3_CONTEXT}}
20. [Normal] Action: {{KSC_3_ACTION}}
21. [Normal] Result: {{KSC_3_RESULT}}
22. [Bullet -] {{KSC_3_SUPPORT_BULLET_1}}
23. [Bullet -] {{KSC_3_SUPPORT_BULLET_2}}
24. [Heading 1 Numbered] {{KSC_CRITERION_4_TEXT}}
25. [Normal] Context: {{KSC_4_CONTEXT}}
26. [Normal] Action: {{KSC_4_ACTION}}
27. [Normal] Result: {{KSC_4_RESULT}}
28. [Bullet -] {{KSC_4_SUPPORT_BULLET_1}}
29. [Bullet -] {{KSC_4_SUPPORT_BULLET_2}}
30. [Heading 1 Numbered] {{KSC_CRITERION_5_TEXT}}
31. [Normal] Context: {{KSC_5_CONTEXT}}
32. [Normal] Action: {{KSC_5_ACTION}}
33. [Normal] Result: {{KSC_5_RESULT}}
34. [Bullet -] {{KSC_5_SUPPORT_BULLET_1}}
35. [Bullet -] {{KSC_5_SUPPORT_BULLET_2}}
36. [Heading 1 Numbered] {{KSC_CRITERION_6_TEXT}}
37. [Normal] Context: {{KSC_6_CONTEXT}}
38. [Normal] Action: {{KSC_6_ACTION}}
39. [Normal] Result: {{KSC_6_RESULT}}
40. [Bullet -] {{KSC_6_SUPPORT_BULLET_1}}
41. [Bullet -] {{KSC_6_SUPPORT_BULLET_2}}

## ATS_AUDIT
columns_max: PASS — single column, no tables, no text boxes
forbidden_chars: PASS — none
allowed_headings: PASS — criterion headings are placeholders (exempt); no static headings used
au_terminology: PASS — none
ksc_word_limit_fit: PASS — CAR structure provides context 40-100w, action 60-200w, result 30-100w per criterion

## REGISTRATION_FRAGMENT
```json
{
  "ksc": {
    "template_doc_id": "REPLACE_WITH_KSC_GOLDEN_MASTER_DOC_ID"
  }
}
```

## DRY_RUN_CMD
python3 generate_document.py --type ksc --target "Test Role at Test Org" --criteria criteria.txt --dry-run
