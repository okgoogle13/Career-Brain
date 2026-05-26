# **PROJECT MANIFESTO: THE CAREER BRAIN DATABASE**

## **Agentic ETL Pipeline, Schema Architecture, and Taxonomy Mapping Logic**

## **1\. VISION AND CORE MISSION**

The goal of this system is to ingest, standardize, and synthesize a vast archive of unstructured historical career documents—spanning over a decade of professional experience—into a highly structured, machine-readable **Career Brain Database**.  
This database is split into three modular JSON engines to optimize Retrieval-Augmented Generation (RAG). By separating **Facts** (Career History), **Narratives** (STAR Stories/Pivots), and **Translations** (Skills & Taxonomies), we prevent LLM context-bloat and prompt drift.  
This engine is designed to feed a custom, hardcoded Gemini Copilot Gem in Google AI Studio, as well as serve as a local query engine within our active IDE workspace, enabling instantaneous, precise tailoring of resumes, cover letters, and Key Selection Criteria (KSC) responses via direct Google Workspace Document generation.

## **2\. THE LOCAL WORKSPACE ARCHITECTURE**

├── PROJECT\_MANIFESTO.md     \# This system directive file  
├── requirements.txt         \# Global Python environment dependencies  
├── normalize\_vault.py       \# Phase 1: Pure-text extraction script  
├── compile\_brain.py         \# Phase 2: Semantic extraction & Pydantic mapping  
├── raw\_docs/                \# User source directories  
│   ├── resumes/             \# Raw resume variations (.pdf, .docx, legacy .doc)  
│   ├── cover\_letters/       \# Raw cover letters & introductory templates  
│   └── ksc/                 \# Raw STAR selection criteria documents  
├── normalized\_vault/        \# Phase 1 Output: Sanitized .txt files  
└── output/                  \# Phase 2 Output: Final structural database  
    ├── career\_history.json  
    ├── ksc\_and\_narratives.json  
    ├── skills\_and\_taxonomy.json  
    ├── doc\_generation\_report.json
    └── parsing\_errors.log
├── doc\_templates.json        \# Phase 5: Template config for Google Docs
├── generate\_document.py      \# Phase 5: Google Workspace generator

## **3\. STATE MACHINE & GATEKEEPER PROTOCOLS**

This pipeline operates under a strict, user-controlled sequential state gate inside our IDE's Agent Planning Mode. The model must not skip gates without explicit user validation:  
\<gatekeeper\_machine\>  
    \<gate id="1" name="Blueprint Validation"\>  
        \<action\>Assess raw files in directories, verify path layouts, design Python helper libraries (python-docx, PyPDF2), and generate environment scripts.\</action\>  
        \<transition\>STOP and request user approval in chat before modifying or writing code files.\</transition\>  
    \</gate\>  
    \<gate id="2" name="Phase 1 Normalization"\>  
        \<action\>Execute normalize\_vault.py to batch process all binaries to plain .txt in normalized\_vault/.\</action\>  
        \<transition\>STOP and present a health ledger (file list, character count, extraction status). Wait for user approval before moving to semantic analysis.\</transition\>  
    \</gate\>  
    \<gate id="3" name="Phase 2 Semantic Compilation"\>  
        \<action\>Execute compile\_brain.py using validated Pydantic model schemas to build output JSON engines.\</action\>  
        \<transition\>STOP and present final database audit statistics, mapping metrics, and the parsing error logs.\</transition\>  
    \</gate\>  
    \<gate id="4" name="Phase 5 Google Docs Export"\>  
        \<action\>Execute generate\_document.py using Google Workspace APIs to clone templates and map extracted data.\</action\>  
        \<transition\>STOP and present the generated document IDs/links and the generation report.\</transition\>  
    \</gate\>  
\</gatekeeper\_machine\>

## **4\. PHASE 1: SANITIZATION & NORMALIZATION (THE VACUUM)**

\<phase\_1\_normalization\_specs\>  
    \<objective\>Strip container file liabilities and isolate raw strings cleanly without losing logical formatting.\</objective\>  
    \<directives\>  
        1\. Iterate through raw files in raw\_docs/resumes/, raw\_docs/cover\_letters/, and raw\_docs/ksc/.  
        2\. Programmatically convert all formats (.docx, .pdf, and legacy .doc) into plain text (.txt) files mapped to normalized\_vault/.  
        3\. Maintain complete downstream lineaging: output text files must retain their original raw name (e.g., "2024\_Resume\_FlatOut.pdf" \-\> "2024\_Resume\_FlatOut.txt").  
        4\. Integrate robust local text stream converters. If a document format is corrupt or unsupported, immediately write the error trace to output/parsing\_errors.log with the original filename.  
        5\. DO NOT summarize, redact, correct grammar, or logically process the text in this phase. The objective is pure string dumping.  
    \</directives\>  
\</phase\_1\_normalization\_specs\>

## **5\. PHASE 2: SEMANTIC EXTRACTION & TAXONOMY COMPILATION**

\<phase\_2\_extraction\_specs\>  
    \<objective\>Deconstruct raw strings in normalized\_vault/ into three LLM-optimized JSON engines utilizing Pydantic runtime model schemas.\</objective\>

    \<database\_modules\>  
        \<\!-- PILLAR 1: FACT MATRIX \--\>  
        \<module id="career\_history" file="career\_history.json"\>  
            \<structure\>Chronological list of roles, employers, operational dates, and individual achievement bullet arrays.\</structure\>  
            \<rule\_variation\_preservation\>  
                If matching job fingerprints (unique MD5 hash of Company \+ Role \+ StartDate) are identified across multiple historical files:  
                \- DO NOT choose a single "master" resume to override the others.  
                \- AGGREGATE all semantically distinct bullet descriptions into the achievements array of that superjob node.  
                \- Eliminate pure duplicate text strings, but preserve every nuanced variation in phrasing (e.g., NAB described as technical vs. NAB described as stakeholder engagement).  
            \</rule\_variation\_preservation\>  
            \<bullet\_structure\_format\>  
                Deconstruct each bullet into fields: Action Verb, Task/Responsibility, Metric/Outcome (if present), Strategy/Methodology (e.g., MARAM, Oracle BPM), and Source Lineage (the originating filename).  
            \</bullet\_structure\_format\>  
            \<domain\_tagging\>  
                Tag every achievement bullet point dynamically with category lists: \["project\_management", "corporate\_finance"\] vs \["service\_coordination", "quality\_assurance", "harm\_reduction"\]. This allows the Custom Gem to filter and pull exact perspectives on demand.  
            \</domain\_tagging\>  
        \</module\>

        \<\!-- PILLAR 2: NARRATIVE REGISTRY \--\>  
        \<module id="ksc\_and\_narratives" file="ksc\_and\_narratives.json"\>  
            \<structure\>High-impact STAR/CAR behavioral stories, cover letter introductory "hooks," and deep lived-experience "pivot narratives."\</structure\>  
            \<rules\>  
                \- Extract long-form paragraphs where the candidate navigates the transition from Corporate Finance to Community Services.  
                \- Index and categorize narratives by core competency benchmarks: \["conflict\_resolution", "complex\_advocacy", "cultural\_humility", "risk\_de-escalation"\].  
                \- Ensure the original formatting of successful, vetted submissions is strictly preserved.  
            \</rules\>  
        \</module\>

        \<\!-- PILLAR 3: SKILLS & TAXONOMY ENGINE (THE ROSETTA STONE) \--\>  
        \<module id="skills\_and\_taxonomy" file="skills\_and\_taxonomy.json"\>  
            \<structure\>An active translation key mapping corporate project/finance achievements to Community Service standards.\</structure\>  
            \<mapping\_logic\>  
                This module acts as the semantic engine, telling the AI how to translate Royal Bank of Scotland (RBS) portfolio governance into social sector assets. Incorporate these three specific translation mappings:  
                  
                1\. Project Management / Workstream Leadership  ➔  SERVICE COORDINATION  
                   \- Corporate Framing: Led cross-departmental regulatory compliance workstreams and managed deliverables.  
                   \- Community Sector Framing: Coordinates complex wraparound services, case-management pathways, and multi-agency collaborations (allied health, housing, and justice systems).  
                     
                2\. Regulatory Compliance / Anti-Tax Avoidance & Audit  ➔  QUALITY ASSURANCE & GOVERNANCE  
                   \- Corporate Framing: Strengthened anti-tax avoidance protocols, performed audits, and mitigated risk of financial crime.  
                   \- Community Sector Framing: Executes clinical governance, statutory compliance audit processes, program quality assurance, and MARAM Risk Assessment/Safeguarding frameworks.  
                     
                3\. High-Net-Worth Portfolio & Stakeholder Management  ➔  SECTOR ENGAGEMENT & SYSTEM ADVOCACY  
                   \- Corporate Framing: Managed relationships and negotiated agreements with high-profile global stakeholders and client groups.  
                   \- Community Sector Framing: High-level systems navigation and strategic client advocacy within complex government, medical, and administrative bureaucracies.  
            \</mapping\_logic\>  
        \</module\>  
    \</database\_modules\>  
\</phase\_2\_extraction\_specs\>

## **6\. PHASE 5: GOOGLE DOCS TEMPLATE GENERATION (THE EXPORT)**

\<phase\_5\_export\_specs\>  
    \<objective\>Inject structured JSON output into polished, standardized Google Docs formats using the Google Workspace APIs.\</objective\>  
    \<directives\>  
        1\. Read config from `doc_templates.json` to identify Golden Master Google Doc IDs for each template type (resume, cover\_letter, etc.).
        2\. Clone the Golden Master document and perform batch text replacements using fixed placeholders (e.g., `{{TARGET_ROLE}}`, `{{BULLET_1}}`).
        3\. Output a `doc_generation_report.json` tracking filled placeholders, unresolved tokens, and generated Google Doc links.
        4\. Do not permanently store PII or OAuth tokens in the repository.
    \</directives\>  
\</phase\_5\_export\_specs\>

## **7\. PIPELINE QUALITY CONTROL GUARDRAILS**

To guarantee high fidelity and programmatic stability, the Phase 2 compilation engine must validate output data against the following rules:

1. **Strict Type Validation:** All generated JSON structures must be validated at runtime via Pydantic model definitions. Any invalid objects must raise a logging action to parsing\_errors.log and be bypassed rather than crashing the pipeline.  
2. **The Metric Audit Loop:** For every bullet point compiled inside career\_history.json, calculate the string length. If an achievement bullet has a length exceeding 20 words but contains *zero* numerical metrics (no %, $, client counts, hours, or caseload scale), programmatically set:  
   needs\_review: true  
   This flags weak points for immediate, targeted metric injection during future iterations.  
3. **Data Lineage Integrity:** Every single narrative, skill, and history node in the final database must preserve its source. A field named source\_lineage must record the exact raw filename (e.g., 2024\_Resume\_Flat\_Out\_v2.txt) to maintain total transparency.

## **8\. MAINTENANCE AND ITERATION PROTOCOL**

Whenever a new role, community-service certificate, or successful job application artifact is developed:

1. Drop the raw file into the appropriate directory under /raw\_docs/.  
2. Run Phase 1 to generate a matching standardized text file in normalized\_vault/.  
3. Run Phase 2 to parse, merge, preserve variations, and compile the update directly into the 3-pillar files.  
4. The Custom AI Gem's memory layer is instantly kept pristine, synchronized, and optimized for infinite future tailoring.