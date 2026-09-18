 Context fully loaded. Key differences from the
  previous run detected in ats_rules.json:
  - | (pipe) is now a forbidden character —
  contact blocks must use line breaks
  - allowed_headings is now explicit: ["Skills", 
  "Certifications", "Professional Experience", 
  "Education", "Key Achievements"]
  - Both resume Doc IDs are already registered in
  doc_templates.json

  Executing Batch 1 with corrected specs.

  ---
  Batch 1 — Resume Template Specifications (v2, 
  Corrected)

  ---
  1a. Chronological Resume

  Phase 1: Target Ingestion

  - Type: resume | Variant: chronological
  - Sector: Australian community services
  (APS/VPS/NFP compatible)

  Phase 2: Placeholder Mapping

  ┌──────────┬────────────────────────────────┐
  │ Section  │             Tokens             │
  ├──────────┼────────────────────────────────┤
  │          │ {{CONTACT_NAME}},              │
  │ Contact  │ {{CONTACT_PHONE}},             │
  │ block    │ {{CONTACT_EMAIL}},             │
  │          │ {{CONTACT_LOCATION}}           │
  ├────────────────┼──────────────────────────┤
  │ Summary        │ {{PROFESSIONAL_SUMMARY}} │
  ├────────────────┼──────────────────────────┤
  │ Skills         │ {{SKILL_1}} –            │
  │                │ {{SKILL_6}}              │
  ├────────────────┼──────────────────────────┤
  │ Role 1–6       │ {{ROLE_N_TITLE}},        │
  │ header         │ {{ROLE_N_ORG}},          │
  │                │ {{ROLE_N_DATES}}         │
  ├────────────────┼──────────────────────────┤
  │ Role 1–6       │ {{ROLE_N_BULLET_1}} –    │
  │ bullets        │ {{ROLE_N_BULLET_4}}      │
  ├────────────────┼──────────────────────────┤
  │ Education      │ {{EDUCATION_1}},         │
  │                │ {{EDUCATION_2}}          │
  ├────────────────┼──────────────────────────┤
  │ Certifications │ {{CERT_1}}, {{CERT_2}},  │
  │                │ {{CERT_3}}               │
  └────────────────┴──────────────────────────┘

  Phase 3: Document Structure

  [Document settings: Calibri 11pt, 1.15 line
  spacing, 6pt after paragraph, 2cm margins]

  ━━━ CONTACT BLOCK ━━━
  [Title style — Calibri 14pt, centred]
  {{CONTACT_NAME}}

  [Normal — centred, LINE BREAKS between items, NO
   pipe characters]
  {{CONTACT_PHONE}}
  {{CONTACT_EMAIL}}
  {{CONTACT_LOCATION}}

  ━━━ PROFESSIONAL SUMMARY ━━━
  [Heading 1]
  Professional Summary

  [Normal]
  {{PROFESSIONAL_SUMMARY}}

  ━━━ SKILLS ━━━
  [Heading 1]
  Skills

  [Normal — comma-separated, single paragraph, NO
  pipe characters]
  {{SKILL_1}}, {{SKILL_2}}, {{SKILL_3}},
  {{SKILL_4}}, {{SKILL_5}}, {{SKILL_6}}

  ━━━ PROFESSIONAL EXPERIENCE ━━━
  [Heading 1]
  Professional Experience

  [Repeat × 6 roles]

  [Heading 2]
  {{ROLE_1_TITLE}}

  [Normal — italic]
  {{ROLE_1_ORG}}    {{ROLE_1_DATES}}

  [Normal — plain hyphen bullets]
  - {{ROLE_1_BULLET_1}}
  - {{ROLE_1_BULLET_2}}
  - {{ROLE_1_BULLET_3}}
  - {{ROLE_1_BULLET_4}}

  [... repeat for ROLE_2 through ROLE_6 ...]

  ━━━ EDUCATION ━━━
  [Heading 1]
  Education

  [Normal]
  {{EDUCATION_1}}
  {{EDUCATION_2}}

  ━━━ CERTIFICATIONS ━━━   ← MUST BE FINAL SECTION
  [Heading 1]
  Certifications

  [Normal]
  {{CERT_1}}
  {{CERT_2}}
  {{CERT_3}}

  Phase 4: ATS Audit

  ┌──────────────────┬───────┬────────────────┐
  │       Rule       │ Statu │      Note      │
  │                  │   s   │                │
  ├────────────────────┼───────┼──────────────┤
  │                    │       │ Single       │
  │ columns_max: 1     │ ✅    │ column, no   │
  │                    │       │ side panels  │
  ────────────────────────────────────────
  Rule: allow_text_boxes: false
  Status: ✅
  Note: No frames or shapes    
  ────────────────────────────────────────    
  Rule: allow_inline_objects: false
  Status: ✅
  Note: No images or icons     
  ────────────────────────────────────────
  Rule: Forbidden chars incl. |
  Status: ✅
  Note: Contact uses line breaks; Skills use
  commas
  ────────────────────────────────────────
  Rule: Bullet glyphs
  Status: ✅
  Note: Plain - only
  ────────────────────────────────────────
  Rule: Heading names
  Status: ✅
  Note: "Skills", "Professional Experience",
    "Education", "Certifications" — all in
    allowed_headings
  ────────────────────────────────────────
  Rule: Certifications last
  Status: ✅
  Note: Final section as required
  ────────────────────────────────────────
  Rule: Australian terminology
  Status: ✅
  Note: "organisation" in any boilerplate; no
    "company", "industry", "job description"

  PASS — no violations.

  Phase 5: Registration & Commands

  Doc ID (already registered):
  {
    "resume": {
      "variants": {
        "chronological": {
          "template_doc_id":
  "17PRt5xe5S38a5wt5H_Y6jvQ0n5dIw2opWPM61IMb3kc"
        }
      }
    } 
  }

  Dry-run:
  python3 generate_document.py --type resume
  --target "Test Role at Test Org" --dry-run

  ---
  1b. Hybrid Resume

  Phase 1: Target Ingestion

  - Type: resume | Variant: hybrid
  - Audience: Career-transition candidates
  (corporate finance → community services)
  - Strategy: Skills-forward with abbreviated
  chronological anchoring

  Phase 2: Placeholder Mapping

  ┌────────┬────────────────────────┬────────┐
  │ Sectio │         Tokens         │  Note  │
  Section: Contact block
  Tokens: {{CONTACT_NAME}}, {{CONTACT_PHONE}},
    {{CONTACT_EMAIL}}, {{CONTACT_LOCATION}}
  Note:
  ────────────────────────────────────────
  Section: Summary
  Tokens: {{PROFESSIONAL_SUMMARY}}
  Note: Rosetta Stone framed
  ────────────────────────────────────────
  Section: Key Transferable Skills
  Tokens: {{SKILL_1}} – {{SKILL_6}}
  Note: Community-translated via Rosetta Stone
  ────────────────────────────────────────
  Section: Role 1–6 header only
  Tokens: {{ROLE_N_TITLE}}, {{ROLE_N_ORG}},
    {{ROLE_N_DATES}}
  Note: No per-role bullet tokens — intentionally
    omitted
  ────────────────────────────────────────
  Section: Education
  Tokens: {{EDUCATION_1}}, {{EDUCATION_2}}
  Note:
  ────────────────────────────────────────
  Section: Certifications
  Tokens: {{CERT_1}}, {{CERT_2}}, {{CERT_3}}
  Note:

  ▎ {{ROLE_N_BULLET_N}} tokens are absent by 
  ▎ design. The pipeline skips unfound tokens — no
  ▎  error.

  Phase 3: Document Structure

  [Document settings: Calibri 11pt, 1.15 line
  spacing, 6pt after paragraph, 2cm margins]

  ━━━ CONTACT BLOCK ━━━
  [Title style — Calibri 14pt, centred]
  {{CONTACT_NAME}}

  [Normal — centred, LINE BREAKS, NO pipe
  characters]
  {{CONTACT_PHONE}}
  {{CONTACT_EMAIL}}
  {{CONTACT_LOCATION}}

  ━━━ PROFESSIONAL SUMMARY ━━━
  [Heading 1]
  Professional Summary

  [Normal — Rosetta Stone community framing: e.g.,
   "Dedicated professional with
  over 12 years across service coordination,
  complex case load management, and
  trauma-informed organisational practice..."]
  {{PROFESSIONAL_SUMMARY}}

  ━━━ KEY TRANSFERABLE SKILLS ━━━  ← ⚠️  See ATS
  Note below
  [Heading 1]
  Key Transferable Skills

  [Normal — community-translated skill labels, one
   per line with plain hyphens]
  - {{SKILL_1}}
  - {{SKILL_2}}
  - {{SKILL_3}}
  - {{SKILL_4}}
  - {{SKILL_5}}
  - {{SKILL_6}}

  [Static framing note below skills — optional
  boilerplate in Normal italic:]
  Skills translated from corporate finance
  experience using Rosetta Stone
  community-sector framing.

  ━━━ PROFESSIONAL EXPERIENCE ━━━
  [Heading 1]
  Professional Experience

  [Heading 2 — abbreviated: title/org/dates only,
  NO bullets]
  {{ROLE_1_TITLE}}
  [Normal — italic]
  {{ROLE_1_ORG}}    {{ROLE_1_DATES}}

  [... repeat for ROLE_2 through ROLE_6 —
  title/org/dates only ...]

  ━━━ EDUCATION ━━━
  [Heading 1]
  Education

  [Normal]
  {{EDUCATION_1}}
  {{EDUCATION_2}}

  ━━━ CERTIFICATIONS ━━━   ← MUST BE FINAL SECTION
  [Heading 1]
  Certifications

  [Normal]
  {{CERT_1}}
  {{CERT_2}}
  {{CERT_3}}

  Phase 4: ATS Audit

  ┌──────────────────────┬───────┬───────────┐
  │         Rule         │ Statu │   Note    │
  │                      │   s   │           │
  ├──────────────────────┼───────┼───────────┤
  │ columns_max: 1       │ ✅    │ Single    │
  │                      │       │ column    │
  ├──────────────────────┼───────┼───────────┤
  │                      │       │ Skills    │
  │ allow_tables: false  │ ✅    │ use plain │
  │                      │       │  hyphenat │
  │                      │       │ ed list   │
  ├──────────────────────┼───────┼───────────┤
  Rule: allow_inline_objects: false
  Status: ✅             
  Note: No images
  ────────────────────────────────────────
  Rule: Forbidden chars incl. |
  Status: ✅
  Note: No pipes anywhere
  ────────────────────────────────────────
  Rule: Bullet glyphs
  Status: ✅
  Note: Plain - only     
  ────────────────────────────────────────
  Rule: Heading names
  Status: ⚠️  WARNING
  Note: "Key Transferable Skills" is NOT in
    ats_rules.json allowed_headings. Closest
  match:
     "Skills". Recommendation: rename to "Skills"
    OR add "Key Transferable Skills" to
    allowed_headings before go-live.
  ────────────────────────────────────────
  Rule: Certifications last
  Status: ✅
  Note: Final section
  ────────────────────────────────────────
  Rule: Australian terminology
  Status: ✅
  Note: "organisation", "sector" — no forbidden
    terms
  ────────────────────────────────────────
  Rule: Rosetta Stone applied
  Status: ✅
  Note: {{SKILL_N}} values must use community
    translations (Service Coordination, Complex
    Case Load Management, MDT Facilitation, etc.)
  —
     verified at runtime by
    content_engine.py:select_skills()

  WARNING — 1 issue requires resolution before 
  go-live (heading name).

  Rosetta Stone framing required for {{SKILL_N}} 
  values:

  ┌───────────────┬─────┬─────────────────────┐
  │  Corporate    │     │  Community Skill    │
  │   Background   │  →  │  Label to use in   │
  │                │     │      template      │
  ├────────────────┼─────┼────────────────────┤
  │ Project        │ →   │ Service            │
  │ Management     │     │ Coordination       │
  ├────────────────┼─────┼────────────────────┤
  │ Compliance /   │ →   │ Quality Assurance  │
  │ Audit          │     │ & Governance       │
  ├────────────────┼─────┼────────────────────┤
  │ Stakeholder    │ →   │ Sector Engagement  │
  │ Management     │     │ & System Advocacy  │
  ├────────────────┼─────┼────────────────────┤
  │                │     │ MARAM Risk         │
  │ Risk Modelling │ →   │ Assessment &       │
  │                │     │ Safety Planning    │
  │                 │     │ Safety Planning   │
  ├─────────────────┼─────┼───────────────────┤
  │ Client          │     │ Complex Case Load │
  │ Portfolio       │ →   │  Management       │
  │ Management      │     │                   │
  ├─────────────────┼─────┼───────────────────┤
  │                 │     │ Program Fidelity  │
  │ Internal Audit  │ →   │ & Funding         │
  │                 │     │ Compliance        │
  ├─────────────────┼─────┼───────────────────┤
  │ Team Leadership │ →   │ MDT Facilitation  │
  ├─────────────────┼─────┼───────────────────┤
  │ CRM             │     │ Case Management   │
  │ Administration  │ →   │ Systems (CIMS,    │
  │                 │     │ Penelope)         │
  ├─────────────────┼─────┼───────────────────┤
  │ Change          │     │ Trauma-Informed   │
  │ Management      │ →   │ Organisational    │
  │                 │     │ Practice          │
  └─────────────────┴─────┴───────────────────┘

  Phase 5: Registration & Commands

  Doc ID (already registered):
  {
    "resume": {
      "variants": {
        "hybrid": {
          "template_doc_id":
  "1TqUqpa4QtZhfO1CQDkjwpK5xkoSkSHOqwoZpH5xGanA"
        }
      }
    }
  }

  Dry-run:
  python3 generate_document.py --type resume
  --target "Test Role at Test Org" --dry-run

  ---
  Batch 1 Summary

  Template: Chronological
  Doc ID: 17PRt5xe5S38a5wt5H_Y...  
  ATS Status: ✅ PASS  
  Action Required: Build doc per spec above
  ────────────────────────────────────────
  Template: Hybrid
  Doc ID: 1TqUqpa4QtZhfO1CQDkj...
  ATS Status: ⚠️  1 WARNING
  Action Required: Build doc; resolve heading name

    before go-live

  Heading name decision needed for Hybrid: Either
  rename the section to Skills (matches
  allowed_headings) or update ats_rules.json to
  add "Key Transferable Skills" to the array —
  whichever aligns with your intended branding.

  ---
  STOP — Batch 1 complete.

  Build both Golden Masters in Google Docs using
  the specs above. Both Doc IDs are already
  registered in doc_templates.json. Run the
  dry-run commands after building, then return to
  proceed with Batch 2 (cover letter templates).

  ---

  ▎ ⚠️  CRITICAL GATING PROTOCOL: OPUS REVIEW 
  ▎ REQUIRED
  ▎ Sonnet has compiled the Batch 1 candidate 
  ▎ structures. Before marking these templates as 
  ▎ final and active in your database, copy the 
  ▎ compiled template structures above and feed 
  ▎ them to Claude Opus with the following system 
  ▎ verification instruction:
  ▎
  ▎ "You are the Lead Career Copilot Quality 
  ▎ Auditor. Review the template structure 
  ▎ generated by Sonnet. Inspect the Calibri 
  ▎ typographic hierarchy, standard 
  ▎ hyphen/circular bullet structures, line-break
  ▎ contact block separation, and ensure that the
  ▎ Hybrid Resume has successfully translated
  ▎ corporate banking terms using the Rosetta
  ▎ Stone Matrix. Do not approve if any generic or
  ▎  unpolished formatting remains."

✻ Baked for 1m 52s

❯ /advisor                                        

──────────────────────────────────────────────────
  Advisor (experimental)
                    
  When Claude needs stronger judgment — a
  complex decision, an ambiguous failure, a
  problem it's circling without progress — it
  ▎ hyphen/circular bullet structures, line-break
  ▎ contact block separation, and ensure that the
  ▎ Hybrid Resume has successfully translated
  ▎ corporate banking terms using the Rosetta
  ▎ Stone Matrix. Do not approve if any generic or
  ▎  unpolished formatting remains."

✻ Baked for 1m 52s

❯ /advisor                                        
  ⎿  Advisor set to Opus 4.7

❯ "You are the Lead Career Copilot Quality        
    ▎ Auditor. Review the template structure      
    ▎ generated by Sonnet. Inspect the Calibri    
    ▎ typographic hierarchy, standard             
    ▎ hyphen/circular bullet structures,          
  line-break                                      
    ▎ contact block separation, and ensure that   
  the                                             
    ▎ Hybrid Resume has successfully translated   
    ▎ corporate banking terms using the Rosetta   
    ▎ Stone Matrix. Do not approve if any generic 
   or                                             
    ▎  unpolished formatting remains."            
                                                  
  ✻ Baked for 1m 52s                              
                                                  
  ❯ /advisor                                      
                                                  
                                                  
  ─────────────────────────────────────────────── 
  ───                                             
    Advisor (experimental)                        
                                                  
    When Claude needs stronger judgment — a       
    complex decision, an ambiguous failure, a     
    problem it's circling without progress — it   
    ▎ hyphen/circular bullet structures,          
  line-break                                      
    ▎ contact block separation, and ensure that   
  the                                             
    ▎ Hybrid Resume has successfully translated   
    ▎ corporate banking terms using the Rosetta   
    ▎ Stone Matrix. Do not approve if any generic 
   or                                             
    ▎  unpolished formatting remains      