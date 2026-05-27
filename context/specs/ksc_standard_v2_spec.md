# KSC Template Spec

## META
TEMPLATE_TYPE: ksc
VARIANT: standard
DOC_ID: REPLACE_WITH_KSC_GOLDEN_MASTER_DOC_ID
TARGET_SECTOR: government, community_services, non_profit

## TOKENS_USED
CONTACT_NAME → generate_document.py:120
CONTACT_PHONE → generate_document.py:120
CONTACT_EMAIL → generate_document.py:120
CONTACT_LOCATION → generate_document.py:120
TARGET_ROLE → generate_document.py:121
EMPLOYER_ORG → generate_document.py:121
KSC_CRITERION_1_TEXT → generate_document.py:127
KSC_1_CONTEXT → generate_document.py:128
KSC_1_ACTION → generate_document.py:129
KSC_1_RESULT → generate_document.py:130
KSC_1_SUPPORT_BULLET_1 → generate_document.py:131
KSC_1_SUPPORT_BULLET_2 → generate_document.py:131
KSC_CRITERION_2_TEXT → generate_document.py:127
KSC_2_CONTEXT → generate_document.py:128
KSC_2_ACTION → generate_document.py:129
KSC_2_RESULT → generate_document.py:130
KSC_2_SUPPORT_BULLET_1 → generate_document.py:131
KSC_2_SUPPORT_BULLET_2 → generate_document.py:131
KSC_CRITERION_3_TEXT → generate_document.py:127
KSC_3_CONTEXT → generate_document.py:128
KSC_3_ACTION → generate_document.py:129
KSC_3_RESULT → generate_document.py:130
KSC_3_SUPPORT_BULLET_1 → generate_document.py:131
KSC_3_SUPPORT_BULLET_2 → generate_document.py:131
KSC_CRITERION_4_TEXT → generate_document.py:127
KSC_4_CONTEXT → generate_document.py:128
KSC_4_ACTION → generate_document.py:129
KSC_4_RESULT → generate_document.py:130
KSC_4_SUPPORT_BULLET_1 → generate_document.py:131
KSC_4_SUPPORT_BULLET_2 → generate_document.py:131
KSC_CRITERION_5_TEXT → generate_document.py:127
KSC_5_CONTEXT → generate_document.py:128
KSC_5_ACTION → generate_document.py:129
KSC_5_RESULT → generate_document.py:130
KSC_5_SUPPORT_BULLET_1 → generate_document.py:131
KSC_5_SUPPORT_BULLET_2 → generate_document.py:131
KSC_CRITERION_6_TEXT → generate_document.py:127
KSC_6_CONTEXT → generate_document.py:128
KSC_6_ACTION → generate_document.py:129
KSC_6_RESULT → generate_document.py:130
KSC_6_SUPPORT_BULLET_1 → generate_document.py:131
KSC_6_SUPPORT_BULLET_2 → generate_document.py:131

## STRUCTURE
1. [Title] {{CONTACT_NAME}}
2. [Normal] {{CONTACT_PHONE}}    {{CONTACT_EMAIL}}    {{CONTACT_LOCATION}}
3. [Normal] {{TARGET_ROLE}}
4. [Normal italic] {{EMPLOYER_ORG}}
5. [Heading 1] {{KSC_CRITERION_1_TEXT}}
6. [Normal] Context: {{KSC_1_CONTEXT}}
7. [Normal] Action: {{KSC_1_ACTION}}
8. [Normal] Result: {{KSC_1_RESULT}}
9. [Bullet -] {{KSC_1_SUPPORT_BULLET_1}}
10. [Bullet -] {{KSC_1_SUPPORT_BULLET_2}}
11. [Heading 1] {{KSC_CRITERION_2_TEXT}}
12. [Normal] Context: {{KSC_2_CONTEXT}}
13. [Normal] Action: {{KSC_2_ACTION}}
14. [Normal] Result: {{KSC_2_RESULT}}
15. [Bullet -] {{KSC_2_SUPPORT_BULLET_1}}
16. [Bullet -] {{KSC_2_SUPPORT_BULLET_2}}
17. [Heading 1] {{KSC_CRITERION_3_TEXT}}
18. [Normal] Context: {{KSC_3_CONTEXT}}
19. [Normal] Action: {{KSC_3_ACTION}}
20. [Normal] Result: {{KSC_3_RESULT}}
21. [Bullet -] {{KSC_3_SUPPORT_BULLET_1}}
22. [Bullet -] {{KSC_3_SUPPORT_BULLET_2}}
23. [Heading 1] {{KSC_CRITERION_4_TEXT}}
24. [Normal] Context: {{KSC_4_CONTEXT}}
25. [Normal] Action: {{KSC_4_ACTION}}
26. [Normal] Result: {{KSC_4_RESULT}}
27. [Bullet -] {{KSC_4_SUPPORT_BULLET_1}}
28. [Bullet -] {{KSC_4_SUPPORT_BULLET_2}}
29. [Heading 1] {{KSC_CRITERION_5_TEXT}}
30. [Normal] Context: {{KSC_5_CONTEXT}}
31. [Normal] Action: {{KSC_5_ACTION}}
32. [Normal] Result: {{KSC_5_RESULT}}
33. [Bullet -] {{KSC_5_SUPPORT_BULLET_1}}
34. [Bullet -] {{KSC_5_SUPPORT_BULLET_2}}
35. [Heading 1] {{KSC_CRITERION_6_TEXT}}
36. [Normal] Context: {{KSC_6_CONTEXT}}
37. [Normal] Action: {{KSC_6_ACTION}}
38. [Normal] Result: {{KSC_6_RESULT}}
39. [Bullet -] {{KSC_6_SUPPORT_BULLET_1}}
40. [Bullet -] {{KSC_6_SUPPORT_BULLET_2}}

## ATS_AUDIT
columns_max: PASS — single column, no tables, no text boxes
forbidden_chars: PASS — static labels (Context:, Action:, Result:) use plain ASCII; bullets use hyphen only; no forbidden glyphs in any static text
allowed_headings: PASS — all 6 criterion headings are placeholder tokens (KSC_CRITERION_c_TEXT, exempt from whitelist); no static Heading 1 text present
au_terminology: PASS — no static AU-specific terminology violations in the structure
ksc_word_limit_fit: PASS — CAR structure maps to context 40-100w, action 60-200w, result 30-100w, total 200-500w per criterion

## REGISTRATION_FRAGMENT
```json
{
  "ksc": {
    "template_doc_id": "REPLACE_WITH_KSC_GOLDEN_MASTER_DOC_ID"
  }
}
```

## DRY_RUN_CMD
python3 tools/generate_document.py --type ksc --target "Test Role at Test Org" --criteria context/specs/ksc_standard_v2_spec.md --dry-run
