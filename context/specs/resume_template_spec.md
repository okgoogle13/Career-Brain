# Resume Template Spec

## META
TEMPLATE_TYPE: resume
VARIANT: chronological
DOC_ID: REPLACE_WITH_RESUME_GOLDEN_MASTER_DOC_ID
TARGET_SECTOR: non_profit

## TOKENS_USED
CONTACT_NAME → generate_document.py:80
CONTACT_PHONE → generate_document.py:80
CONTACT_EMAIL → generate_document.py:80
CONTACT_LOCATION → generate_document.py:80
TARGET_ROLE → generate_document.py:100
EMPLOYER_ORG → generate_document.py:107
PROFESSIONAL_SUMMARY → generate_document.py:82
SKILL_1 → generate_document.py:84
SKILL_2 → generate_document.py:84
SKILL_3 → generate_document.py:84
SKILL_4 → generate_document.py:84
SKILL_5 → generate_document.py:84
SKILL_6 → generate_document.py:84
ROLE_1_TITLE → generate_document.py:90
ROLE_1_ORG → generate_document.py:91
ROLE_1_DATES → generate_document.py:92
ROLE_1_BULLET_1 → generate_document.py:93
ROLE_1_BULLET_2 → generate_document.py:93
ROLE_1_BULLET_3 → generate_document.py:93
ROLE_1_BULLET_4 → generate_document.py:93
ROLE_2_TITLE → generate_document.py:90
ROLE_2_ORG → generate_document.py:91
ROLE_2_DATES → generate_document.py:92
ROLE_2_BULLET_1 → generate_document.py:93
ROLE_2_BULLET_2 → generate_document.py:93
ROLE_2_BULLET_3 → generate_document.py:93
ROLE_2_BULLET_4 → generate_document.py:93
ROLE_3_TITLE → generate_document.py:90
ROLE_3_ORG → generate_document.py:91
ROLE_3_DATES → generate_document.py:92
ROLE_3_BULLET_1 → generate_document.py:93
ROLE_3_BULLET_2 → generate_document.py:93
ROLE_3_BULLET_3 → generate_document.py:93
ROLE_3_BULLET_4 → generate_document.py:93
ROLE_4_TITLE → generate_document.py:90
ROLE_4_ORG → generate_document.py:91
ROLE_4_DATES → generate_document.py:92
ROLE_4_BULLET_1 → generate_document.py:93
ROLE_4_BULLET_2 → generate_document.py:93
ROLE_4_BULLET_3 → generate_document.py:93
ROLE_4_BULLET_4 → generate_document.py:93
ROLE_5_TITLE → generate_document.py:90
ROLE_5_ORG → generate_document.py:91
ROLE_5_DATES → generate_document.py:92
ROLE_5_BULLET_1 → generate_document.py:93
ROLE_5_BULLET_2 → generate_document.py:93
ROLE_5_BULLET_3 → generate_document.py:93
ROLE_5_BULLET_4 → generate_document.py:93
ROLE_6_TITLE → generate_document.py:90
ROLE_6_ORG → generate_document.py:91
ROLE_6_DATES → generate_document.py:92
ROLE_6_BULLET_1 → generate_document.py:93
ROLE_6_BULLET_2 → generate_document.py:93
ROLE_6_BULLET_3 → generate_document.py:93
ROLE_6_BULLET_4 → generate_document.py:93
EDUCATION_1 → generate_document.py:97
EDUCATION_2 → generate_document.py:97
CERT_1 → generate_document.py:98
CERT_2 → generate_document.py:98
CERT_3 → generate_document.py:98

## STRUCTURE
1. [Title Center] {{CONTACT_NAME}}
2. [Normal Center] {{CONTACT_PHONE}}
3. [Normal Center] {{CONTACT_EMAIL}}
4. [Normal Center] {{CONTACT_LOCATION}}
5. [Normal Center italic] {{TARGET_ROLE}} at {{EMPLOYER_ORG}}
6. [Heading 1] SUMMARY
7. [Normal] {{PROFESSIONAL_SUMMARY}}
8. [Heading 1] SKILLS
9. [Normal] {{SKILL_1}} - {{SKILL_2}} - {{SKILL_3}} - {{SKILL_4}} - {{SKILL_5}} - {{SKILL_6}}
10. [Heading 1] PROFESSIONAL EXPERIENCE
11. [Heading 2] {{ROLE_1_TITLE}}
12. [Normal italic] {{ROLE_1_ORG}} — {{ROLE_1_DATES}}
13. [Bullet -] {{ROLE_1_BULLET_1}}
14. [Bullet -] {{ROLE_1_BULLET_2}}
15. [Bullet -] {{ROLE_1_BULLET_3}}
16. [Bullet -] {{ROLE_1_BULLET_4}}
17. [Heading 2] {{ROLE_2_TITLE}}
18. [Normal italic] {{ROLE_2_ORG}} — {{ROLE_2_DATES}}
19. [Bullet -] {{ROLE_2_BULLET_1}}
20. [Bullet -] {{ROLE_2_BULLET_2}}
21. [Bullet -] {{ROLE_2_BULLET_3}}
22. [Bullet -] {{ROLE_2_BULLET_4}}
23. [Heading 2] {{ROLE_3_TITLE}}
24. [Normal italic] {{ROLE_3_ORG}} — {{ROLE_3_DATES}}
25. [Bullet -] {{ROLE_3_BULLET_1}}
26. [Bullet -] {{ROLE_3_BULLET_2}}
27. [Bullet -] {{ROLE_3_BULLET_3}}
28. [Bullet -] {{ROLE_3_BULLET_4}}
29. [Heading 2] {{ROLE_4_TITLE}}
30. [Normal italic] {{ROLE_4_ORG}} — {{ROLE_4_DATES}}
31. [Bullet -] {{ROLE_4_BULLET_1}}
32. [Bullet -] {{ROLE_4_BULLET_2}}
33. [Bullet -] {{ROLE_4_BULLET_3}}
34. [Bullet -] {{ROLE_4_BULLET_4}}
35. [Heading 2] {{ROLE_5_TITLE}}
36. [Normal italic] {{ROLE_5_ORG}} — {{ROLE_5_DATES}}
37. [Bullet -] {{ROLE_5_BULLET_1}}
38. [Bullet -] {{ROLE_5_BULLET_2}}
39. [Bullet -] {{ROLE_5_BULLET_3}}
40. [Bullet -] {{ROLE_5_BULLET_4}}
41. [Heading 2] {{ROLE_6_TITLE}}
42. [Normal italic] {{ROLE_6_ORG}} — {{ROLE_6_DATES}}
43. [Bullet -] {{ROLE_6_BULLET_1}}
44. [Bullet -] {{ROLE_6_BULLET_2}}
45. [Bullet -] {{ROLE_6_BULLET_3}}
46. [Bullet -] {{ROLE_6_BULLET_4}}
47. [Heading 1] EDUCATION
48. [Normal] {{EDUCATION_1}}
49. [Normal] {{EDUCATION_2}}
50. [Heading 1] CERTIFICATIONS AND LICENSING
51. [Normal] {{CERT_1}}
52. [Normal] {{CERT_2}}
53. [Normal] {{CERT_3}}

## ATS_AUDIT
columns_max: PASS — single column, no tables, no text boxes
forbidden_chars: PASS — none
allowed_headings: PASS — Calibri only, consistent styles
au_terminology: PASS — none

## REGISTRATION_FRAGMENT
```json
{
  "resume": {
    "variants": {
      "chronological": {
        "template_doc_id": "REPLACE_WITH_RESUME_GOLDEN_MASTER_DOC_ID"
      }
    }
  }
}
```

## DRY_RUN_CMD
python3 generate_document.py --type resume --variant chronological --target "Test Role at Test Org" --dry-run
