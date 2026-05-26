#!/usr/bin/env python3
"""
compile_brain.py — Career Brain Pipeline: Phase 2
==================================================
Reads all .txt files from processed/ and compiles them into three
LLM-optimised JSON engines using Pydantic validation:

  database/career_history.json      — Chronological roles + aggregated bullets
  database/ksc_and_narratives.json  — STAR/CAR/Pivot narratives indexed by competency
  database/skills_and_taxonomy.json — RBS-to-Community Rosetta Stone mapping

Rosetta Stone Mapping Logic is hardcoded per the Career Brain Manifesto.
"""

import re
import sys
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

# ─── Paths ────────────────────────────────────────────────────────────────────────────
BASE    = Path(__file__).parent.parent  # project root
VAULT   = BASE / "processed"
OUTPUT  = BASE / "database"
OUTPUT.mkdir(parents=True, exist_ok=True)
ERROR_LOG = OUTPUT / "parsing_errors.log"

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("compile_brain")

error_entries = []
def log_error(source: str, reason: str):
    entry = f"[{datetime.now().isoformat()}] ERROR | {source} | {reason}"
    error_entries.append(entry)
    log.warning(f"COMPILE ERROR: {source} → {reason}")


# ════════════════════════════════════════════════════════════════════════════
# SECTION 1: PYDANTIC SCHEMAS
# ════════════════════════════════════════════════════════════════════════════

class AchievementBullet(BaseModel):
    raw_text: str
    action_verb: Optional[str] = None
    task_responsibility: Optional[str] = None
    metric_outcome: Optional[str] = None
    strategy_methodology: Optional[str] = None
    domain_tags: list[str] = Field(default_factory=list)
    needs_review: bool = False          # True if >20 words but zero numeric metrics
    source_lineage: str = ""

    @field_validator("raw_text")
    @classmethod
    def must_have_content(cls, v):
        if not v or len(v.strip()) < 5:
            raise ValueError("Achievement bullet too short")
        return v.strip()


class JobRecord(BaseModel):
    fingerprint: str                    # MD5 of Company+Role+StartDate
    company: str
    role: str
    start_date: str
    end_date: str
    location: Optional[str] = None
    employment_type: Optional[str] = None
    sector: Optional[str] = None        # "corporate" | "community" | "hybrid"
    domain_archetypes: list[str] = Field(default_factory=list)
    achievements: list[AchievementBullet] = Field(default_factory=list)
    source_lineage: list[str] = Field(default_factory=list)


class CareerHistoryDB(BaseModel):
    generated_at: str
    total_roles: int = 0
    total_bullets: int = 0
    roles: list[JobRecord] = Field(default_factory=list)


class Narrative(BaseModel):
    narrative_type: str                 # "STAR" | "CAR" | "pivot" | "hook" | "statement"
    title: str
    full_text: str
    competency_tags: list[str] = Field(default_factory=list)
    organisation_context: Optional[str] = None
    word_count: int = 0
    source_lineage: str = ""

    @field_validator("full_text")
    @classmethod
    def must_have_content(cls, v):
        if not v or len(v.strip()) < 30:
            raise ValueError("Narrative text too short")
        return v.strip()


class NarrativesDB(BaseModel):
    generated_at: str
    total_narratives: int = 0
    narratives: list[Narrative] = Field(default_factory=list)


class TaxonomyTranslation(BaseModel):
    corporate_framing: str
    community_translation: str
    community_keywords: list[str]
    contextual_bridge: str
    domain_tags: list[str] = Field(default_factory=list)


class SkillEntry(BaseModel):
    skill_name: str
    skill_level: Optional[str] = None  # "advanced" | "intermediate" | "foundational"
    context: Optional[str] = None
    source_lineage: list[str] = Field(default_factory=list)


class TaxonomyDB(BaseModel):
    generated_at: str
    rosetta_stone: dict[str, TaxonomyTranslation] = Field(default_factory=dict)
    skills_inventory: list[SkillEntry] = Field(default_factory=list)
    keyword_bank: dict[str, list[str]] = Field(default_factory=dict)


# ════════════════════════════════════════════════════════════════════════════
# SECTION 2: HARDCODED ROSETTA STONE MAPPING
# ════════════════════════════════════════════════════════════════════════════

ROSETTA_STONE = {
    # ── Original 3 mappings (Manifesto-specified) ────────────────────────────
    "RBS_Project_Management": TaxonomyTranslation(
        corporate_framing="Led cross-departmental regulatory compliance workstreams and managed deliverables across global teams at Royal Bank of Scotland.",
        community_translation="Service Coordination",
        community_keywords=["Complex Case Coordination", "MDT Collaboration", "Systems Navigation",
                            "Wraparound Support", "Care Pathway Management", "Multi-Agency Collaboration"],
        contextual_bridge="Applies rigorous project management methodologies — stakeholder mapping, milestone tracking, and deliverable accountability — to coordinate comprehensive wraparound support for clients navigating complex social systems.",
        domain_tags=["project_management", "service_coordination", "community_services"],
    ),
    "RBS_Regulatory_Compliance": TaxonomyTranslation(
        corporate_framing="Strengthened anti-tax avoidance protocols, performed financial audits, and mitigated risk of financial crime within RBS portfolio governance.",
        community_translation="Quality Assurance & Governance",
        community_keywords=["Clinical Governance", "CQI", "MARAM Risk Assessment", "Safeguarding",
                            "Statutory Compliance", "Program Quality Assurance", "Funding Compliance"],
        contextual_bridge="Leverages financial auditing and regulatory compliance background to ensure programs strictly adhere to funding guidelines, safeguarding frameworks, and clinical governance requirements including MARAM and CQI processes.",
        domain_tags=["quality_assurance", "governance", "risk_management", "compliance"],
    ),
    "RBS_Stakeholder_Management": TaxonomyTranslation(
        corporate_framing="Managed high-net-worth client portfolios and negotiated agreements with high-profile global stakeholders across RBS international divisions.",
        community_translation="Sector Engagement & System Advocacy",
        community_keywords=["Systems Navigation", "Strategic Client Advocacy", "Government Liaison",
                            "Medical System Navigation", "Administrative Advocacy", "Sector Partnerships"],
        contextual_bridge="Translates high-stakes stakeholder management and negotiation skills into high-level systems navigation and strategic client advocacy within complex government, medical, and administrative bureaucracies on behalf of vulnerable clients.",
        domain_tags=["stakeholder_management", "advocacy", "sector_engagement", "systems_navigation"],
    ),

    # ── Sprint 2 Expansion: 6 new mappings ──────────────────────────────────
    "RBS_Financial_Risk_Modelling": TaxonomyTranslation(
        corporate_framing="Performed financial risk modelling, stress-testing, and scenario analysis to assess portfolio exposure and mitigate regulatory risk at RBS and NAB.",
        community_translation="MARAM Risk Assessment & Safety Planning",
        community_keywords=["MARAM Risk Assessment", "Safety Planning", "Risk Stratification",
                            "Lethality Assessment", "Contextual Risk Analysis", "Protective Factors",
                            "Multi-Risk Identification"],
        contextual_bridge="Applies structured financial risk methodology — scenario modelling, exposure assessment, and weighted factor analysis — to MARAM risk assessment and family violence safety planning, bringing analytical rigour to lethality and contextual risk identification.",
        domain_tags=["quality_assurance", "risk_management", "community_services", "mental_health"],
    ),
    "RBS_Portfolio_Client_Management": TaxonomyTranslation(
        corporate_framing="Managed a portfolio of high-net-worth and corporate clients, maintaining ongoing service relationships, conducting needs assessments, and delivering tailored financial solutions.",
        community_translation="Complex Case Load Management",
        community_keywords=["Complex Caseload", "Needs Assessment", "Client-Centred Practice",
                            "Ongoing Case Management", "Care Planning", "Client Relationship Management",
                            "Support Coordination"],
        contextual_bridge="Transfers direct client portfolio management — structured intake, ongoing needs assessment, and relationship stewardship across a large client base — to complex case load management in community services, maintaining accountability for client outcomes across a high-volume caseload.",
        domain_tags=["service_coordination", "community_services", "project_management"],
    ),
    "RBS_Audit_Internal_Controls": TaxonomyTranslation(
        corporate_framing="Designed and executed internal audit processes, assessed control frameworks, and ensured organisational compliance with financial regulatory standards.",
        community_translation="Program Fidelity & Funding Compliance",
        community_keywords=["Program Fidelity", "Funding Compliance", "Grant Acquittal",
                            "Output Reporting", "KPI Monitoring", "Program Evaluation",
                            "DHHS Compliance", "DSS Reporting"],
        contextual_bridge="Applies internal audit discipline — framework assessment, evidence-based compliance verification, and reporting accountability — to ensure community programs meet government funding requirements, DHHS/DSS output targets, and grant acquittal obligations.",
        domain_tags=["quality_assurance", "governance", "compliance", "community_services"],
    ),
    "RBS_CrossFunctional_Leadership": TaxonomyTranslation(
        corporate_framing="Led cross-functional teams across multiple business units and geographies, facilitating alignment between technical, compliance, and commercial workstreams.",
        community_translation="Multi-Disciplinary Team (MDT) Facilitation",
        community_keywords=["MDT Facilitation", "Multi-Agency Collaboration", "Interagency Coordination",
                            "Integrated Care", "Team Around the Client", "Wraparound Facilitation",
                            "Allied Health Coordination"],
        contextual_bridge="Translates cross-functional team leadership — navigating competing priorities, facilitating alignment, and driving shared outcomes across diverse disciplines — to MDT facilitation in community services, convening allied health, legal, housing, and social work professionals around complex client needs.",
        domain_tags=["project_management", "service_coordination", "community_services", "leadership"],
    ),
    "RBS_CRM_Systems": TaxonomyTranslation(
        corporate_framing="Implemented and administered Salesforce CRM and Oracle BPM workflow systems to manage client pipelines, automate compliance reporting, and track portfolio performance.",
        community_translation="Case Management Systems (CIMS, Penelope, Salesforce NFP)",
        community_keywords=["Case Management System", "CIMS", "Penelope", "Salesforce NFP",
                            "Client Database Management", "Data Entry Compliance", "Outcome Recording",
                            "Digital Case Notes"],
        contextual_bridge="Applies enterprise CRM and BPM systems experience to case management platform administration in the community sector — ensuring accurate client record-keeping, compliant outcome data entry, and effective use of CIMS, Penelope, or Salesforce NFP as operational case management tools.",
        domain_tags=["project_management", "quality_assurance", "community_services"],
    ),
    "RBS_Change_Management": TaxonomyTranslation(
        corporate_framing="Led organisational change management programs at RBS post-GFC restructure, embedding new compliance frameworks and cultural transformation across affected teams.",
        community_translation="Trauma-Informed Organisational Practice",
        community_keywords=["Trauma-Informed Practice", "Organisational Change", "Cultural Safety",
                            "Staff Wellbeing", "Reflective Practice", "Vicarious Trauma",
                            "Psychological Safety", "Secondary Trauma"],
        contextual_bridge="Translates change management leadership — communicating uncertainty, building psychological safety, embedding new practice frameworks, and sustaining team cohesion through disruption — to trauma-informed organisational practice, supporting team resilience, reflective supervision, and cultural safety in high-stress community service environments.",
        domain_tags=["leadership", "community_services", "mental_health", "cultural_safety"],
    ),
}

# ════════════════════════════════════════════════════════════════════════════
# SECTION 3: KEYWORD TAXONOMIES & PATTERN LIBRARIES
# ════════════════════════════════════════════════════════════════════════════

# Domain tagging keywords — used to auto-tag bullets
DOMAIN_KEYWORDS = {
    "project_management":    ["project", "workstream", "milestone", "deliverable", "scope", "stakeholder", "budget", "timeline", "coordination", "managed", "led"],
    "corporate_finance":     ["RBS", "banking", "audit", "compliance", "regulatory", "financial", "revenue", "portfolio", "anti-tax", "AML", "risk"],
    "service_coordination":  ["case", "coordination", "wraparound", "referral", "MDT", "multi-agency", "allied health", "pathway", "support plan", "care plan", "integrated care"],
    "quality_assurance":     ["governance", "CQI", "MARAM", "safeguarding", "compliance", "audit", "quality", "framework", "clinical", "fidelity", "acquittal", "KPI", "DHHS", "DSS"],
    "harm_reduction":        ["harm reduction", "AOD", "drugs", "alcohol", "peer", "lived experience", "LGBTIQ", "PWUD", "naloxone"],
    "housing":               ["housing", "homelessness", "tenancy", "shelter", "IAP", "rough sleeping", "Launch Housing"],
    "community_services":    ["community", "social work", "welfare", "support worker", "client", "FDV", "DV", "crisis", "advocacy"],
    "mental_health":         ["mental health", "wellbeing", "headspace", "counselling", "trauma", "PTSD", "therapeutic", "AOD", "vicarious trauma", "secondary trauma"],
    "peer_work":             ["peer", "lived experience", "peer worker", "peer support", "neuroqueer", "trans", "queer"],
    "cultural_safety":       ["cultural", "LGBTIQ", "Aboriginal", "First Nations", "inclusive", "diversity", "CALD", "ATSI", "TGD", "cultural safety", "psychological safety"],
    "advocacy":              ["advocate", "advocacy", "rights", "system", "navigate", "empower", "justice"],
    # Sprint 2 additions
    "risk_assessment":       ["risk", "MARAM", "safety plan", "lethality", "protective", "risk stratif", "risk model", "scenario", "stress test"],
    "case_management":       ["caseload", "case management", "CIMS", "Penelope", "Salesforce", "case notes", "client database", "intake", "needs assessment"],
    "leadership":            ["led", "lead", "manage", "mentor", "supervis", "team", "MDT facilit", "cross-functional", "chair"],
    "change_management":     ["change", "restructure", "transformation", "embed", "reform", "implement", "transition", "new framework"],
}

# Competency tags for narratives
COMPETENCY_KEYWORDS = {
    "conflict_resolution":   ["conflict", "mediation", "de-escalat", "tension", "dispute", "resolution"],
    "complex_advocacy":      ["advocate", "advocacy", "complex", "system", "bureaucrac", "navigate"],
    "cultural_humility":     ["cultural", "humble", "diversity", "inclusive", "LGBTIQ", "Aboriginal", "TGD", "queer", "cultural safety"],
    "risk_de_escalation":    ["risk", "de-escalat", "crisis", "safety", "danger", "MARAM", "safeguard", "lethality", "safety plan"],
    "stakeholder_engagement":["stakeholder", "partner", "collaborat", "relationship", "network", "interagency", "liaison"],
    "service_coordination":  ["coordinat", "case", "wraparound", "referral", "pathway", "MDT", "integrated", "multi-agency"],
    "career_transition":     ["transition", "career change", "pivot", "community", "banking", "corporate", "sector"],
    "lived_experience":      ["lived experience", "peer", "personal", "recovery", "journey"],
    "leadership":            ["led", "lead", "manage", "mentor", "supervis", "team", "facilitat", "chair"],
    "project_management":    ["project", "deliverable", "workstream", "milestone", "managed"],
    # Sprint 2 additions
    "trauma_informed_practice": ["trauma", "trauma-informed", "vicarious", "secondary trauma", "psychological safety", "reflective", "resilience"],
    "program_compliance":    ["funding", "acquittal", "KPI", "output", "DHHS", "DSS", "fidelity", "reporting", "grant"],
    "mdt_facilitation":      ["MDT", "multi-disciplinary", "multi-agency", "interagency", "team around", "allied health", "wraparound team"],
    "data_systems":          ["CIMS", "Penelope", "Salesforce", "Oracle", "CRM", "case management system", "database", "digital"],
}

# STAR/CAR indicator phrases
STAR_INDICATORS   = ["situation", "task", "action", "result", "context", "challenge", "response", "outcome", "S:", "T:", "A:", "R:", "C:", "STAR", "CAR"]
PIVOT_INDICATORS  = ["transition", "career change", "from banking", "from finance", "community services", "sector change", "pivot"]
HOOK_INDICATORS   = ["I am a", "I bring", "With over", "As a", "Having worked", "My background", "Drawing on"]

# Metrics pattern — numbers, percentages, dollar amounts, client counts
METRIC_PATTERN = re.compile(r"\b(\d+[\d,]*\.?\d*\s*(%|percent|clients?|people|cases?|hours?|\$|AUD|k\b|thousand|million)|\$[\d,]+)", re.IGNORECASE)

# Known employers — for job fingerprinting
KNOWN_EMPLOYERS = {
    "Royal Bank of Scotland": ["RBS", "royal bank of scotland"],
    "NAB": ["nab", "national australia bank"],
    "Launch Housing": ["launch housing", "launch housing iap", "iap"],
    "Flat Out": ["flat out", "flat-out", "fdv justice"],
    "Thorne Harbour Health": ["thorne harbour", "THH", "PLC"],
    "Headspace": ["headspace", "work & study", "work and study"],
    "Uniting": ["uniting", "united csw"],
    "Harm Reduction Victoria": ["harm reduction victoria", "HRVic", "hrv", "fuse"],
    "PRONTO": ["pronto"],
    "ASRC": ["asrc", "asylum seeker"],
    "Orygen": ["orygen", "tgd peer nav"],
    "Good Shepherd": ["good shepherd"],
    "CoHealth": ["cohealth"],
    "PLC": ["plc home care"],
}


# ════════════════════════════════════════════════════════════════════════════
# SECTION 4: HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════

def fingerprint(company: str, role: str, start: str) -> str:
    key = f"{company.lower().strip()}|{role.lower().strip()}|{start.strip()}"
    return hashlib.md5(key.encode()).hexdigest()[:12]


def tag_domains(text: str) -> list[str]:
    text_lower = text.lower()
    tags = []
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(kw.lower() in text_lower for kw in keywords):
            tags.append(domain)
    return sorted(set(tags))


def tag_competencies(text: str) -> list[str]:
    text_lower = text.lower()
    tags = []
    for comp, keywords in COMPETENCY_KEYWORDS.items():
        if any(kw.lower() in text_lower for kw in keywords):
            tags.append(comp)
    return sorted(set(tags))


def has_metrics(text: str) -> bool:
    return bool(METRIC_PATTERN.search(text))


def needs_review_check(text: str) -> bool:
    words = text.split()
    return len(words) > 20 and not has_metrics(text)


def extract_action_verb(text: str) -> Optional[str]:
    """Extract the first word if it looks like a resume action verb."""
    words = text.strip().split()
    if words and words[0][0].isupper() and len(words[0]) > 2:
        return words[0]
    return None


def detect_employer(text: str) -> Optional[str]:
    text_lower = text.lower()
    for employer, aliases in KNOWN_EMPLOYERS.items():
        if any(alias.lower() in text_lower for alias in aliases):
            return employer
    return None


def detect_narrative_type(text: str) -> str:
    text_lower = text.lower()
    if any(ind.lower() in text_lower for ind in PIVOT_INDICATORS):
        return "pivot"
    if any(ind.lower() in text_lower for ind in HOOK_INDICATORS[:3]):
        return "hook"
    if any(ind.lower() in text_lower for ind in STAR_INDICATORS[:8]):
        return "STAR"
    return "statement"


def detect_sector(text: str) -> str:
    text_lower = text.lower()
    community_signals = sum(1 for kw in ["community", "social", "peer", "client", "support worker", "housing", "harm reduction", "crisis"] if kw in text_lower)
    corporate_signals = sum(1 for kw in ["rbs", "banking", "audit", "financial", "revenue", "portfolio", "nab"] if kw in text_lower)
    if community_signals > corporate_signals:
        return "community"
    elif corporate_signals > community_signals:
        return "corporate"
    return "hybrid"


def read_vault_file(path: Path) -> tuple[str, str, str]:
    """Returns (category, source_filename, body_text)."""
    raw = path.read_text(encoding="utf-8", errors="replace")
    lines = raw.splitlines()

    # Parse header
    source = path.name
    category = path.stem.split("__")[0] if "__" in path.stem else "unknown"

    for line in lines[:5]:
        if line.startswith("=== SOURCE:"):
            source = line.replace("=== SOURCE:", "").replace("===", "").strip()
        if line.startswith("=== CATEGORY:"):
            category = line.replace("=== CATEGORY:", "").replace("===", "").strip()

    # Strip header (4 lines + blank)
    sep_idx = next((i for i, l in enumerate(lines) if l.startswith("=" * 10)), 3)
    body = "\n".join(lines[sep_idx + 2:]).strip()

    return category, source, body


def extract_bullet_blocks(text: str) -> list[str]:
    """
    Extract bullet point lines from resume-style text.
    Handles •, -, *, ▪, numbers, and em-dash prefixed lines.
    """
    bullets = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Match bullet prefixes
        if re.match(r"^[•\-\*▪◦‣➤►→]\s+.{10,}", line):
            bullets.append(re.sub(r"^[•\-\*▪◦‣➤►→]\s+", "", line).strip())
        elif re.match(r"^\d+\.\s+.{10,}", line):
            bullets.append(re.sub(r"^\d+\.\s+", "", line).strip())
        # Capture un-prefixed lines that look like achievements (start with capital verb)
        elif re.match(r"^[A-Z][a-z]+ed|^[A-Z][a-z]+ed|^Managed|^Led|^Developed|^Delivered|^Coordinated|^Supported|^Facilitated|^Implemented|^Established|^Built|^Created|^Designed|^Conducted|^Provided|^Maintained", line):
            if len(line.split()) >= 5:
                bullets.append(line.strip())
    return bullets


def extract_paragraphs(text: str, min_words: int = 30) -> list[str]:
    """Extract substantial paragraphs for narrative extraction."""
    paragraphs = re.split(r"\n{2,}", text)
    return [p.strip() for p in paragraphs if len(p.split()) >= min_words]


def extract_role_blocks(text: str) -> list[dict]:
    """
    Heuristically identify job blocks in a resume.
    Looks for date patterns near company/title lines.
    Returns list of dicts with company, role, dates, body.
    """
    blocks = []

    # Date patterns: "2020 – 2022", "Jan 2019 – Present", "2018 to 2020", "2019-2022"
    DATE_PATTERN = re.compile(
        r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\.?\s*\d{4})\s*[-–—to]+\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\.?\s*\d{4}|Present|Current|Ongoing)",
        re.IGNORECASE
    )

    lines = text.splitlines()
    current_block = None
    current_body = []

    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if not line_stripped:
            if current_block and current_body:
                current_body.append("")
            continue

        date_match = DATE_PATTERN.search(line_stripped)
        if date_match:
            # Save previous block
            if current_block:
                current_block["body"] = "\n".join(current_body).strip()
                blocks.append(current_block)

            # Try to get company/role from surrounding lines
            context_lines = lines[max(0, i-3):i+2]
            context_text = " | ".join(l.strip() for l in context_lines if l.strip())

            employer = detect_employer(context_text)
            role_guess = "Unknown"
            
            clean_context = [l.strip() for l in context_lines if l.strip() and not DATE_PATTERN.search(l)]
            if not employer and clean_context:
                employer = clean_context[-1]
            if clean_context:
                role_guess = clean_context[0] if len(clean_context) > 1 else "Unknown"

            current_block = {
                "company": employer or "Unknown",
                "role": role_guess,
                "start_date": date_match.group(1).strip(),
                "end_date": date_match.group(2).strip(),
                "raw_header": line_stripped,
            }
            current_body = []
        elif current_block is not None:
            current_body.append(line_stripped)

    # Flush last block
    if current_block:
        current_block["body"] = "\n".join(current_body).strip()
        blocks.append(current_block)

    return blocks


# ════════════════════════════════════════════════════════════════════════════
# SECTION 5: PILLAR COMPILERS
# ════════════════════════════════════════════════════════════════════════════

def compile_career_history(vault_files: list[Path]) -> CareerHistoryDB:
    """
    PILLAR 1: Aggregate all resume files into a deduplicated career history.
    Aggregates bullets across identical job fingerprints; preserves phrasing variations.
    """
    log.info("\n── PILLAR 1: Career History ──")
    db = CareerHistoryDB(generated_at=datetime.now().isoformat())

    # job_map: fingerprint → JobRecord
    job_map: dict[str, JobRecord] = {}
    # seen_bullets: fingerprint → set of normalized bullet texts (for exact-dup check)
    seen_bullets: dict[str, set] = {}

    resume_files = [f for f in vault_files if f.stem.startswith("resumes__") or f.stem.startswith("cover_letters__resumes")]

    for vf in sorted(vault_files):
        cat, source, body = read_vault_file(vf)
        if cat not in ("resumes", "references"):
            continue

        log.info(f"  Processing: {source}")
        try:
            role_blocks = extract_role_blocks(body)
            if not role_blocks:
                # Treat entire file as one block
                role_blocks = [{"company": detect_employer(body) or "Unknown",
                                "role": "Unknown", "start_date": "Unknown",
                                "end_date": "Unknown", "body": body, "raw_header": source}]

            for block in role_blocks:
                company  = block["company"]
                role     = block.get("role", "Unknown")
                start    = block.get("start_date", "Unknown")
                end      = block.get("end_date", "Unknown")
                fp       = fingerprint(company, role, start)

                if fp not in job_map:
                    job_map[fp] = JobRecord(
                        fingerprint=fp,
                        company=company,
                        role=role,
                        start_date=start,
                        end_date=end,
                        sector=detect_sector(block.get("body", "")),
                        source_lineage=[source],
                    )
                    seen_bullets[fp] = set()
                else:
                    if source not in job_map[fp].source_lineage:
                        job_map[fp].source_lineage.append(source)

                bullets = extract_bullet_blocks(block.get("body", ""))
                for raw in bullets:
                    # Filter out bullets that are just hyphens, empty, or too short after cleaning
                    cleaned = re.sub(r"^[•\-\*▪◦‣➤►→\s]+", "", raw).strip()
                    if len(cleaned) < 10:
                        continue
                    # Exact duplicate check (normalised)
                    norm = re.sub(r"\s+", " ", raw.lower().strip())
                    if norm in seen_bullets[fp]:
                        continue
                    seen_bullets[fp].add(norm)

                    try:
                        bullet = AchievementBullet(
                            raw_text=raw,
                            action_verb=extract_action_verb(raw),
                            domain_tags=tag_domains(raw),
                            needs_review=needs_review_check(raw),
                            source_lineage=source,
                        )
                        job_map[fp].achievements.append(bullet)
                    except Exception as e:
                        log_error(source, f"Bullet validation: {e}")

        except Exception as e:
            log_error(source, f"Career history block: {e}")

    db.roles = sorted(job_map.values(), key=lambda r: r.start_date, reverse=True)
    db.total_roles = len(db.roles)
    db.total_bullets = sum(len(r.achievements) for r in db.roles)
    log.info(f"  → {db.total_roles} roles, {db.total_bullets} aggregated bullets")
    return db


def compile_narratives(vault_files: list[Path]) -> NarrativesDB:
    """
    PILLAR 2: Extract STAR/CAR/Pivot narratives from KSC and cover letter files.
    Indexes by competency tag.
    """
    log.info("\n── PILLAR 2: KSC & Narratives ──")
    db = NarrativesDB(generated_at=datetime.now().isoformat())
    seen_texts: set = set()

    TARGET_CATS = ("ksc", "cover_letters", "knowledge")

    for vf in sorted(vault_files):
        cat, source, body = read_vault_file(vf)
        if cat not in TARGET_CATS:
            continue

        log.info(f"  Processing: {source}")
        try:
            paragraphs = extract_paragraphs(body, min_words=25)

            for para in paragraphs:
                norm = re.sub(r"\s+", " ", para.lower().strip())
                if norm in seen_texts:
                    continue

                # Minimum quality filter
                if len(para.split()) < 25:
                    continue
                # Skip headers and metadata lines
                if para.startswith("===") or para.startswith("---"):
                    continue

                seen_texts.add(norm)

                ntype = detect_narrative_type(para)
                competencies = tag_competencies(para)
                employer_ctx = detect_employer(para)

                try:
                    narrative = Narrative(
                        narrative_type=ntype,
                        title=f"{ntype.upper()} — {source[:40]}",
                        full_text=para,
                        competency_tags=competencies,
                        organisation_context=employer_ctx,
                        word_count=len(para.split()),
                        source_lineage=source,
                    )
                    db.narratives.append(narrative)
                except Exception as e:
                    log_error(source, f"Narrative validation: {e}")

        except Exception as e:
            log_error(source, f"Narrative extraction: {e}")

    db.total_narratives = len(db.narratives)
    log.info(f"  → {db.total_narratives} narratives extracted")
    return db


def compile_taxonomy(vault_files: list[Path]) -> TaxonomyDB:
    """
    PILLAR 3: Skills & Taxonomy Engine.
    Hardcodes the Rosetta Stone mapping and builds a skills inventory + keyword bank.
    """
    log.info("\n── PILLAR 3: Skills & Taxonomy ──")
    db = TaxonomyDB(
        generated_at=datetime.now().isoformat(),
        rosetta_stone={k: v for k, v in ROSETTA_STONE.items()},
    )

    # Build keyword bank from knowledge files
    keyword_bank: dict[str, set] = {domain: set() for domain in DOMAIN_KEYWORDS}

    skill_map: dict[str, SkillEntry] = {}
    SKILL_PATTERNS = re.compile(
        r"\b(MARAM|CQI|NDIS|FDV|AOD|MDT|AML|STAR|CAR|Oracle BPM|Salesforce|"
        r"case management|harm reduction|motivational interview|trauma.informed|"
        r"cultural humility|clinical governance|risk assessment|peer support|"
        r"project management|stakeholder management|regulatory compliance|"
        r"financial audit|anti.tax avoidance|portfolio management)\b",
        re.IGNORECASE
    )

    for vf in sorted(vault_files):
        cat, source, body = read_vault_file(vf)

        # Extract explicit skills
        skills_found = SKILL_PATTERNS.findall(body)
        for skill in skills_found:
            skill_norm = skill.strip().lower()
            if skill_norm not in skill_map:
                skill_map[skill_norm] = SkillEntry(
                    skill_name=skill.strip(),
                    source_lineage=[source],
                )
            elif source not in skill_map[skill_norm].source_lineage:
                skill_map[skill_norm].source_lineage.append(source)

        # Contribute to keyword bank
        body_lower = body.lower()
        for domain, kws in DOMAIN_KEYWORDS.items():
            for kw in kws:
                if kw.lower() in body_lower:
                    keyword_bank[domain].add(kw)

    db.skills_inventory = sorted(skill_map.values(), key=lambda s: s.skill_name)
    db.keyword_bank = {k: sorted(v) for k, v in keyword_bank.items() if v}

    log.info(f"  → {len(db.skills_inventory)} skills extracted")
    log.info(f"  → {len(db.keyword_bank)} domain keyword sets")
    log.info(f"  → {len(db.rosetta_stone)} Rosetta Stone translations hardcoded")
    return db


# ════════════════════════════════════════════════════════════════════════════
# SECTION 6: MAIN
# ════════════════════════════════════════════════════════════════════════════

def main():
    log.info("=" * 60)
    log.info("CAREER BRAIN — PHASE 2: SEMANTIC COMPILATION")
    log.info(f"Started: {datetime.now().isoformat()}")
    log.info("=" * 60)

    vault_files = sorted(VAULT.glob("*.txt"))
    if not vault_files:
        log.error("Vault is empty! Run normalize_vault.py first.")
        sys.exit(1)
    log.info(f"Vault: {len(vault_files)} files to process")

    # ── PILLAR 1 ────────────────────────────────────────────────────────────
    career_db = compile_career_history(vault_files)
    career_path = OUTPUT / "career_history.json"
    career_path.write_text(
        json.dumps(career_db.model_dump(), indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    log.info(f"  Saved: {career_path}")

    # ── PILLAR 2 ────────────────────────────────────────────────────────────
    narratives_db = compile_narratives(vault_files)
    narratives_path = OUTPUT / "ksc_and_narratives.json"
    narratives_path.write_text(
        json.dumps(narratives_db.model_dump(), indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    log.info(f"  Saved: {narratives_path}")

    # ── PILLAR 3 ────────────────────────────────────────────────────────────
    taxonomy_db = compile_taxonomy(vault_files)
    taxonomy_path = OUTPUT / "skills_and_taxonomy.json"
    taxonomy_path.write_text(
        json.dumps(taxonomy_db.model_dump(), indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    log.info(f"  Saved: {taxonomy_path}")

    # ── WRITE ERROR LOG ─────────────────────────────────────────────────────
    if error_entries:
        existing = ERROR_LOG.read_text(encoding="utf-8") if ERROR_LOG.exists() else ""
        ERROR_LOG.write_text(existing + "\n".join(error_entries) + "\n", encoding="utf-8")

    # ── FINAL AUDIT REPORT ──────────────────────────────────────────────────
    needs_review_count = sum(
        1 for r in career_db.roles
        for b in r.achievements
        if b.needs_review
    )

    log.info("\n" + "=" * 60)
    log.info("PHASE 2 FINAL AUDIT")
    log.info("=" * 60)
    log.info(f"  PILLAR 1 — career_history.json")
    log.info(f"    Roles compiled           : {career_db.total_roles}")
    log.info(f"    Achievement bullets      : {career_db.total_bullets}")
    log.info(f"    Flagged needs_review     : {needs_review_count}  ← metric injection needed")
    log.info(f"  PILLAR 2 — ksc_and_narratives.json")
    log.info(f"    Narratives extracted     : {narratives_db.total_narratives}")
    competency_coverage = {}
    for n in narratives_db.narratives:
        for tag in n.competency_tags:
            competency_coverage[tag] = competency_coverage.get(tag, 0) + 1
    for comp, count in sorted(competency_coverage.items(), key=lambda x: -x[1])[:8]:
        log.info(f"      {comp:<30} {count:>4} narratives")
    log.info(f"  PILLAR 3 — skills_and_taxonomy.json")
    log.info(f"    Skills extracted         : {len(taxonomy_db.skills_inventory)}")
    log.info(f"    Rosetta Stone mappings   : {len(taxonomy_db.rosetta_stone)}")
    log.info(f"    Domain keyword sets      : {len(taxonomy_db.keyword_bank)}")
    log.info(f"  COMPILE ERRORS             : {len(error_entries)}")
    log.info("=" * 60)
    log.info("\nPhase 2 complete. Career Brain database is live.")

    return len(error_entries) == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
