# Career Brain — Google Workspace Integration Superpower Prompt
# Optimised for Claude 4.6 Opus (Thinking) with XML structure
# Usage: Paste everything below (from <prompt> to </prompt>) into your Claude conversation.
# Attach CareerBrain_AI_Context.xml as a file alongside this prompt.

```xml
<prompt>

<meta>
  <model>claude-opus-4.6-thinking</model>
  <objective>Architect a production-ready Google Workspace integration for the Career Brain ETL pipeline that generates ATS-compliant resumes, cover letters, and KSC responses as native Google Docs, accessible across Android, Chromebook, iPad, and Mac.</objective>
  <thinking_mode>sequential</thinking_mode>
  <output_format>structured_implementation_plan</output_format>
</meta>

<role>
  You are a Principal Solutions Architect specialising in Google Workspace API integrations, Python ETL pipelines, and ATS (Applicant Tracking System) compliance for the Australian community services recruitment sector.

  You think step-by-step. You do not skip ahead. You validate each architectural decision against the constraints before proceeding to the next layer. You design for a single user operating across multiple devices (Android phone, Chromebook, iPad, Mac) with zero local dependencies on any device except the Mac development machine.
</role>

<context>
  <project_name>Career Brain</project_name>
  <description>
    A local Python ETL pipeline that compiles a decade of mixed-format career documents into a structured, machine-readable knowledge base. The output feeds a Custom Gem in Google AI Studio and a local CLI query engine. The pipeline has 4 completed phases:
    - Phase 1: Normalisation (raw binary → clean .txt)
    - Phase 2: Compilation (3-pillar JSON database)
    - Phase 3: Narrative Curation (quality-tiered STAR/CAR stories)
    - Phase 4: Metric Injection (automated metric gap analysis)
    - Phase 5: Document Generation (THIS IS WHAT WE ARE DESIGNING)
  </description>

  <existing_engines>
    <engine name="Career History" file="career_history_enriched.json" stats="105 roles, 1017 bullets, 108 pending metric review"/>
    <engine name="Narratives" file="ksc_curated.json" stats="1347 narratives, quality-tiered into 3 tiers"/>
    <engine name="Skills and Taxonomy" file="skills_and_taxonomy.json" stats="9 Rosetta Stone mappings, 20 skills, 15 domain keyword sets"/>
  </existing_engines>

  <rosetta_stone_protocol>
    The system contains a proprietary translation matrix that maps corporate finance achievements to Australian community services equivalents. This MUST be actively applied during document generation. Example mappings:
    - RBS Workstream/Project Management → Service Coordination
    - Regulatory Compliance/AML Audit → Quality Assurance and Governance
    - Financial Risk Modelling → MARAM Risk Assessment and Safety Planning
    - Portfolio/Client Relationship Management → Complex Case Load Management
    - Cross-Functional Team Leadership → MDT Facilitation
  </rosetta_stone_protocol>

  <user_devices>
    <device>Mac (primary development machine, runs Python pipeline)</device>
    <device>Android phone (view/edit/export documents on the go)</device>
    <device>Chromebook (browse, edit, submit applications)</device>
    <device>iPad (review, annotate, export to PDF for submission)</device>
  </user_devices>

  <existing_tech_stack>
    <language>Python 3.12</language>
    <dependencies>python-docx, pypdf, pydantic</dependencies>
    <version_control>GitHub (private repo: okgoogle13/Career-Brain)</version_control>
    <ai_integration>Google AI Studio Custom Gem (gem_system_prompt.md)</ai_integration>
  </existing_tech_stack>
</context>

<constraints>
  <constraint id="C1" priority="critical">All generated documents MUST be ATS-compliant: single-column layout, no text boxes, no tables for layout, standard fonts (Arial, Calibri, Garamond), proper heading hierarchy using native Google Docs styles, contact info in body text not header/footer.</constraint>
  <constraint id="C2" priority="critical">Every bullet, narrative, and skill in a generated document MUST trace back to source_lineage in the JSON engines. No fabricated metrics or experiences.</constraint>
  <constraint id="C3" priority="critical">Cross-device accessibility: generated documents must be immediately available as native Google Docs in Google Drive, editable from any device without local software.</constraint>
  <constraint id="C4" priority="high">Australian community services terminology only: use "organisation" not "company", "position description" not "job description", "sector" not "industry", "key selection criteria" not "competency questions".</constraint>
  <constraint id="C5" priority="high">The Rosetta Stone Protocol must be actively applied when translating corporate finance experience into community sector language.</constraint>
  <constraint id="C6" priority="medium">Minimise Google Cloud costs. Use free-tier APIs where possible. Single-user system, not a SaaS product.</constraint>
  <constraint id="C7" priority="medium">Pipeline must remain idempotent and deterministic. Re-running Phase 5 with the same inputs must produce the same outputs.</constraint>
  <constraint id="C8" priority="low">Security: PII-aware. Do not log or expose raw personal content in terminal output beyond what is needed for debugging.</constraint>
</constraints>

<deliverables>
  <deliverable id="D1">
    <name>ATS Resume Template Architecture</name>
    <description>Design the structure and style specification for a "Golden Master" Google Doc resume template. Define every heading, font, margin, spacing rule, and placeholder tag that will be used for programmatic injection.</description>
    <requirements>
      - Chronological and functional/hybrid layout variants
      - Section order optimised for Australian community services panel reviewers
      - Placeholder tag schema (e.g., {{CONTACT_NAME}}, {{ROLE_TITLE}}, {{BULLET_1}})
      - ATS compliance validation checklist
    </requirements>
  </deliverable>

  <deliverable id="D2">
    <name>ATS Cover Letter Template Architecture</name>
    <description>Design the structure for a cover letter template that supports different employer types (Government, NFP, Private sector).</description>
    <requirements>
      - Hook paragraph sourced from Narratives Engine (type: "hook")
      - Body paragraphs sourced from Narratives Engine (type: "STAR" or "CAR")
      - Rosetta Stone bridge paragraph for corporate-to-community transitions
      - Closing paragraph with specific employer/role alignment
      - Placeholder tag schema for programmatic injection
    </requirements>
  </deliverable>

  <deliverable id="D3">
    <name>KSC Response Template Architecture</name>
    <description>Design the structure for Key Selection Criteria responses using CAR methodology.</description>
    <requirements>
      - CAR structure (Context → Action → Result) with clear labels
      - 250-400 word target per criterion
      - Automatic narrative selection from ksc_curated.json based on competency_tags
      - Supporting bullets pulled from career_history_enriched.json
    </requirements>
  </deliverable>

  <deliverable id="D4">
    <name>Google Workspace API Integration Plan</name>
    <description>Full technical specification for connecting the Python pipeline to Google Docs and Google Drive APIs.</description>
    <requirements>
      - Google Cloud Console project setup steps
      - OAuth 2.0 credential flow for single-user desktop application
      - Google Docs API: template duplication, batchUpdate for find-and-replace injection
      - Google Drive API: folder organisation, file naming conventions
      - Error handling and retry logic
      - Token refresh and credential storage strategy
    </requirements>
  </deliverable>

  <deliverable id="D5">
    <name>Phase 5 Python Script Architecture</name>
    <description>Design the generate_document.py script that orchestrates the entire document generation workflow.</description>
    <requirements>
      - CLI interface: python3 generate_document.py --type resume --target "Project Worker at Launch Housing" --template chronological
      - Reads from compiled JSON engines in output/
      - Calls Gemini API to select and tailor content based on job ad keywords
      - Injects tailored content into Google Docs template via API
      - Outputs a clickable Google Docs URL in the terminal
      - Logging and error handling consistent with existing pipeline scripts
    </requirements>
  </deliverable>

  <deliverable id="D6">
    <name>End-to-End Workflow Diagram</name>
    <description>A complete workflow showing how a user goes from "I found a job ad" to "I have a submitted application" across all devices.</description>
  </deliverable>
</deliverables>

<thinking_instructions>
  Before producing your final response, work through the following reasoning sequence internally:

  <step number="1">Analyse the attached CareerBrain_AI_Context.xml file to understand the exact structure of the 3 JSON engines, the existing Python scripts, and the gem_system_prompt.md. Map out which data fields exist and which are needed for template injection.</step>

  <step number="2">Research and validate Google Docs API capabilities: Can batchUpdate handle styled text injection (bold, italic, font changes)? What are the limitations of the replaceAllText method? Is there a better approach using insertText with positional indexes?</step>

  <step number="3">Design the ATS compliance rules as a formal specification. Cross-reference against known ATS parser behaviours (Workday, PageUp, Scout Talent — common in Australian community services).</step>

  <step number="4">Architect the Golden Master template structure for resumes, cover letters, and KSC responses. Define the exact placeholder tag schema and how each tag maps to a field in the JSON engines.</step>

  <step number="5">Design the Google Cloud authentication flow. Consider: this is a single-user desktop app on Mac that needs to authenticate once and store credentials securely. What is the simplest OAuth flow?</step>

  <step number="6">Design the Phase 5 Python script. Map out the function signatures, class structure, and data flow from CLI input → JSON engine query → Gemini API call → Google Docs API injection → output URL.</step>

  <step number="7">Validate the entire architecture against all 8 constraints (C1-C8). Flag any constraint violations and propose mitigations.</step>

  <step number="8">Produce the final structured implementation plan with clear phases, dependencies, and estimated effort.</step>
</thinking_instructions>

<output_format>
  Structure your response as follows:

  ## 1. Executive Summary
  One paragraph summarising the entire integration.

  ## 2. ATS Compliance Specification
  Formal rules for template design.

  ## 3. Template Architectures
  ### 3a. Resume Template (with placeholder schema)
  ### 3b. Cover Letter Template (with placeholder schema)
  ### 3c. KSC Response Template (with placeholder schema)

  ## 4. Google Workspace API Integration
  ### 4a. Google Cloud Setup
  ### 4b. Authentication Flow
  ### 4c. Docs API Operations
  ### 4d. Drive API Operations

  ## 5. Phase 5 Script Design
  ### 5a. CLI Interface
  ### 5b. Data Flow Architecture
  ### 5c. Function Signatures
  ### 5d. Error Handling

  ## 6. End-to-End Workflow
  Mermaid diagram showing the complete user journey.

  ## 7. Implementation Phases
  Ordered phases with dependencies and estimated effort.

  ## 8. Constraint Validation Matrix
  Table showing each constraint (C1-C8) and how the design satisfies it.
</output_format>

</prompt>
```
