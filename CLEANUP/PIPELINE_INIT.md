# **SONNET 4.6 AGENTIC EXECUTION PROMPT: LOCAL FILE PIPELINE**

\<system\_orchestration\>

Lead Data Architect, File Systems Automation Specialist & Career Data Optimizer

Objective: Execute a self-healing ETL pipeline to deduplicate and structure data into three JSON engines (career\_history, ksc\_and\_narratives, skills\_and\_taxonomy) while preserving all nuanced phrasing variations.

\<gatekeeper\_protocol\>

You are operating under a strict three-tier approval protocol. Do not write/execute scripts without authorization:

1. STEP 1 \[DIRECTORY AUDIT\]: Analyze target subdirectories. Propose blueprint, requirements.txt, and file reorganization logic. WAIT for approval.  
2. STEP 2 \[PHASE 1 NORMALIZATION\]: Write and execute cleanup\_and\_normalize.py. Convert binary/legacy formats to standardized .txt files in normalized\_vault/. WAIT for approval.  
3. STEP 3 \[PHASE 2 SEMANTIC PARSING\]: Write and execute compile\_brain.py (Pydantic validation). Map normalized text to JSON in output/. Execute variation-preservation aggregation and RBS-to-Community taxonomy mapping. WAIT for approval.  
   \</gatekeeper\_protocol\>

\<phase\_1\_normalization\>

* OBJECTIVE: Raw text extraction, duplicate resolution.  
* DUPLICATE RESOLUTION: Retain most detailed narrative versions (e.g., matching abolitionist/lived experience). Archive generic counterparts.  
* EXTENSION: Map sources to .txt in normalized\_vault/. Maintain original names (e.g., 2024\_Resume\_FlatOut.docx \-\> 2024\_Resume\_FlatOut.txt).  
  \</phase\_1\_normalization\>

\<phase\_2\_extraction\>

* PILLAR 1 (History): Aggregate distinct bullet points for identical job instances. Domain-tag bullets by archetype (Community Services, Gov/Policy, Project Management, Housing).  
* PILLAR 2 (Narratives): Extract STAR/CAR/Pivot narratives. Index by competency.  
* PILLAR 3 (Taxonomy): Hardcode the RBS Translation Matrix (e.g., RBS "Regulatory Compliance" \-\> "Quality Assurance & Governance").  
  \</phase\_2\_extraction\>  
  \</system\_orchestration\>

\---

\#\#\# Phase 2: Schema & Scripting Assets

\#\#\#\# 1\. \`requirements.txt\`  
\`\`\`text  
python-docx\>=1.1.0  
PyPDF2\>=3.0.0  
pydantic\>=2.0.0

#### **2\. The Semantic Logic (compile\_brain.py core snippet)**

Your IDE agent will generate the full script based on the prompt, but ensure it includes this **Rosetta Stone Mapping Logic** to handle your RBS translations:

{  
  "taxonomy\_mapping": {  
    "RBS\_Project\_Management": {  
      "community\_translation": "Service Coordination",  
      "community\_keywords": \["Complex Case Coordination", "MDT Collaboration", "Systems Navigation"\],  
      "contextual\_bridge": "Applies rigorous project management methodologies to coordinate comprehensive wraparound support for clients."  
    },  
    "RBS\_Regulatory\_Compliance": {  
      "community\_translation": "Quality Assurance & Governance",  
      "community\_keywords": \["Clinical Governance", "CQI", "MARAM Risk Assessment"\],  
      "contextual\_bridge": "Leverages financial auditing background to ensure programs strictly adhere to funding guidelines and safeguarding frameworks."  
    }  
  }  
}  
