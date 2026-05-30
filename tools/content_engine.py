#!/usr/bin/env python3
"""
Content selection engine for Career Brain Phase 5.

Provides intelligent content selection from the 3-pillar JSON engines
(Career History, Narratives, Skills & Taxonomy) based on job ad keywords,
domain relevance, quality tiers, and the Rosetta Stone translation protocol.

This module is used by generate_document.py to build placeholder values
for Google Docs template injection.
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

log = logging.getLogger("content_engine")


# ──────────────────────────────────────────────────────────────────────
# Enums & Config
# ──────────────────────────────────────────────────────────────────────

class DocumentType(str, Enum):
    RESUME = "resume"
    COVER_LETTER = "cover_letter"
    KSC = "ksc"


class EmployerType(str, Enum):
    GOVERNMENT = "government"
    NFP = "nfp"
    PRIVATE = "private"


@dataclass
class GenerationConfig:
    """All parameters for a single document generation run."""
    doc_type: DocumentType
    target_role: str
    variant: str | None = None
    employer_type: EmployerType = EmployerType.NFP
    job_ad_text: str | None = None
    criteria_text: list[str] | None = None
    dry_run: bool = False
    summary_override: str | None = None
    rosetta: bool = True



# ──────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────

MAX_RESUME_ROLES = 6
MAX_BULLETS_PER_ROLE = 4
MAX_RESUME_SKILLS = 6
MAX_COVER_LETTER_EVIDENCE = 2
MAX_KSC_CRITERIA = 6
MAX_KSC_SUPPORT_BULLETS = 2

# Word count targets for KSC CAR sections
KSC_WORD_TARGETS = {
    "context": (40, 100),
    "action": (60, 200),
    "result": (30, 100),
    "total": (200, 500),
}

# Load centralized ATS rules if available
ATS_RULES_PATH = Path(__file__).parent.parent / "config" / "ats_rules.json"
if ATS_RULES_PATH.exists():
    try:
        with ATS_RULES_PATH.open(encoding="utf-8") as fh:
            _ats_data = json.load(fh)
            _limits = _ats_data.get("ksc", {}).get("word_limits", {})
            for _key, _val in _limits.items():
                if isinstance(_val, list) and len(_val) == 2:
                    KSC_WORD_TARGETS[_key] = (_val[0], _val[1])
    except Exception as _exc:
        log.warning("Failed to load KSC word limits from %s: %s", ATS_RULES_PATH, _exc)


# Salutation defaults by employer type
SALUTATION_MAP = {
    EmployerType.GOVERNMENT: "Selection Panel",
    EmployerType.NFP: "Hiring Manager",
    EmployerType.PRIVATE: "Hiring Manager",
}


# ──────────────────────────────────────────────────────────────────────
# User Config
# ──────────────────────────────────────────────────────────────────────

def load_user_config(path: Path) -> dict[str, Any]:
    """Load static user configuration (contact info, education, certs)."""
    if not path.exists():
        log.warning("User config not found at %s — using empty defaults", path)
        return {}
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


# ──────────────────────────────────────────────────────────────────────
# Keyword Extraction
# ──────────────────────────────────────────────────────────────────────

def extract_job_ad_keywords(
    job_ad_text: str,
    keyword_bank: dict[str, list[str]],
) -> dict[str, float]:
    """Match job ad text against keyword_bank domains.

    Returns a dict of ``{domain_tag: relevance_score}`` where the score
    is the proportion of domain keywords found in the job ad text.
    """
    if not job_ad_text or not keyword_bank:
        return {}

    ad_lower = job_ad_text.lower()
    scores: dict[str, float] = {}

    for domain, keywords in keyword_bank.items():
        if not keywords:
            continue
        hits = sum(1 for kw in keywords if kw.lower() in ad_lower)
        if hits > 0:
            scores[domain] = hits / len(keywords)

    return dict(sorted(scores.items(), key=lambda item: -item[1]))


# ──────────────────────────────────────────────────────────────────────
# Role Selection
# ──────────────────────────────────────────────────────────────────────

def _parse_date_rank(date_str: str | None) -> int:
    """Convert a date string into a numeric rank for sorting.

    More recent dates get higher values.  "Present" or "Current" are
    treated as the most recent possible date.  Returns 0 for unparseable
    dates.
    """
    if not date_str or not isinstance(date_str, str):
        return 0
    # "Present" / "Current" / "Ongoing" → always most recent
    if date_str.strip().lower() in ("present", "current", "ongoing"):
        return 9999 * 12
    # Try common patterns: "2024", "Jan 2024", "2024-01", "01/2024"
    match = re.search(r"(\d{4})", date_str)
    if match:
        year = int(match.group(1))
        # Bonus for month ordering within a year
        month_match = re.search(
            r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)", date_str, re.I
        )
        month_bonus = 0
        if month_match:
            months = [
                "jan", "feb", "mar", "apr", "may", "jun",
                "jul", "aug", "sep", "oct", "nov", "dec",
            ]
            month_bonus = months.index(month_match.group(1).lower()[:3])
        return year * 12 + month_bonus
    return 0


def _role_domain_score(
    role: dict[str, Any],
    keyword_scores: dict[str, float],
) -> float:
    """Score a role's relevance based on its domain archetypes and
    achievement domain tags against keyword scores."""
    score = 0.0
    # Score from role-level domain archetypes
    for archetype in role.get("domain_archetypes", []):
        if isinstance(archetype, str):
            score += keyword_scores.get(archetype, 0.0)

    # Score from achievement-level domain tags
    for achievement in role.get("achievements", []):
        for tag in achievement.get("domain_tags", []):
            if isinstance(tag, str):
                score += keyword_scores.get(tag, 0.0) * 0.1
    return score


def select_roles(
    history: dict[str, Any],
    target_role: str,
    keyword_scores: dict[str, float],
    max_roles: int = MAX_RESUME_ROLES,
) -> list[dict[str, Any]]:
    """Select and rank roles by recency and domain relevance.

    Returns up to ``max_roles`` roles sorted by a composite score of
    recency (60% weight) and domain relevance (40% weight).
    """
    roles = history.get("roles", [])
    if not roles:
        return []

    # Find the maximum date rank for normalisation
    date_ranks = [_parse_date_rank(r.get("end_date") or r.get("start_date")) for r in roles]
    max_date = max(date_ranks) if date_ranks else 1
    if max_date == 0:
        max_date = 1

    # Pre-compute domain scores across ALL roles for proper normalisation
    domain_scores = [_role_domain_score(r, keyword_scores) for r in roles]
    max_domain_all = max(max(domain_scores), 1.0) if domain_scores else 1.0

    scored: list[tuple[float, int, dict[str, Any]]] = []
    for idx, role in enumerate(roles):
        recency = _parse_date_rank(role.get("end_date") or role.get("start_date")) / max_date
        domain_normalised = domain_scores[idx] / max_domain_all
        composite = (recency * 0.6) + (domain_normalised * 0.4)
        scored.append((composite, idx, role))

    scored.sort(key=lambda item: (-item[0], item[1]))
    return [item[2] for item in scored[:max_roles]]


# ──────────────────────────────────────────────────────────────────────
# Bullet Selection
# ──────────────────────────────────────────────────────────────────────

def _clean_text(value: Any) -> str:
    """Collapse whitespace in a string value."""
    if not isinstance(value, str):
        return ""
    return " ".join(value.split())


def _bullet_text(achievement: dict[str, Any]) -> str:
    """Extract the display text from an achievement node, preferring audit-improved text."""
    return _clean_text(
        achievement.get("suggested_rewrite")
        or achievement.get("raw_text")
        or achievement.get("text")
        or achievement.get("achievement")
    )


def _has_metric(text: str) -> bool:
    """Return True if text contains a numeric metric."""
    return bool(re.search(r"\d+[%$]|\$\d|(?:\d+\s*(?:client|team|staff|hour|day|week|month|year|site|case))", text, re.I))


def select_bullets(
    role: dict[str, Any],
    keyword_scores: dict[str, float],
    max_bullets: int = MAX_BULLETS_PER_ROLE,
) -> list[str]:
    """Select and rank bullets within a role.

    Prioritises bullets with metrics, then by domain tag relevance.
    Excludes ``needs_review=True`` bullets.
    """
    candidates: list[tuple[float, int, str]] = []

    for idx, achievement in enumerate(role.get("achievements", [])):
        if achievement.get("needs_review"):
            continue
        text = _bullet_text(achievement)
        if not text:
            continue

        # Score: metric presence (bonus 1.0) + domain relevance
        score = 1.0 if _has_metric(text) else 0.0
        for tag in achievement.get("domain_tags", []):
            if isinstance(tag, str):
                score += keyword_scores.get(tag, 0.0) * 0.5
        candidates.append((score, idx, text))

    candidates.sort(key=lambda item: (-item[0], item[1]))
    return [item[2] for item in candidates[:max_bullets]]


def select_all_bullets(
    history: dict[str, Any],
    keyword_scores: dict[str, float],
    max_total: int = 6,
) -> list[str]:
    """Select the best bullets across all roles, flattened.

    Used by the v1-compatible resume placeholder builder.
    """
    all_bullets: list[tuple[float, int, int, str]] = []
    for role_idx, role in enumerate(history.get("roles", [])):
        for ach_idx, achievement in enumerate(role.get("achievements", [])):
            if achievement.get("needs_review"):
                continue
            text = _bullet_text(achievement)
            if not text:
                continue
            score = 1.0 if _has_metric(text) else 0.0
            for tag in achievement.get("domain_tags", []):
                if isinstance(tag, str):
                    score += keyword_scores.get(tag, 0.0) * 0.5
            all_bullets.append((score, role_idx, ach_idx, text))

    all_bullets.sort(key=lambda item: (-item[0], item[1], item[2]))
    return [item[3] for item in all_bullets[:max_total]]


# ──────────────────────────────────────────────────────────────────────
# Narrative Selection
# ──────────────────────────────────────────────────────────────────────

def select_narratives(
    narratives: list[dict[str, Any]],
    competency_targets: list[str] | None = None,
    narrative_types: list[str] | None = None,
    max_count: int = 3,
    max_word_count: int | None = None,
    exclude_cover_letters: bool = False,
) -> list[dict[str, Any]]:
    """Select narratives by competency match and quality tier.

    Priority order:
    1. quality_tier ascending (tier 1 first)
    2. competency_tags match count (more matches = better)
    3. quality_score descending
    """
    if not narratives:
        return []

    targets_lower = [t.lower() for t in (competency_targets or [])]
    type_filter = [t.lower() for t in (narrative_types or [])]

    scored: list[tuple[int, int, int, int, dict[str, Any]]] = []

    for idx, narrative in enumerate(narratives):
        text = _clean_text(narrative.get("full_text"))
        if not text:
            continue

        # Filter by narrative type if specified
        n_type = (narrative.get("narrative_type") or "").lower()
        if type_filter and n_type not in type_filter:
            continue

        # Filter by maximum word count if specified
        if max_word_count is not None:
            wc = narrative.get("word_count") or len(text.split())
            if wc > max_word_count:
                continue

        # Filter out cover-letter-style documents when exclude_cover_letters=True
        if exclude_cover_letters and _looks_like_cover_letter(text):
            continue

        tier = narrative.get("quality_tier", 99)
        try:
            tier_val = int(tier)
        except (TypeError, ValueError):
            tier_val = 99

        quality_score = narrative.get("quality_score", 0)
        try:
            q_score = int(quality_score or 0)
        except (TypeError, ValueError):
            q_score = 0

        # Competency match count
        comp_tags = [
            t.lower() for t in narrative.get("competency_tags", [])
            if isinstance(t, str)
        ]
        match_count = sum(1 for t in targets_lower if t in comp_tags)

        scored.append((tier_val, -match_count, -q_score, idx, narrative))

    scored.sort()
    return [item[4] for item in scored[:max_count]]


# ──────────────────────────────────────────────────────────────────────
# Rosetta Stone Translation
# ──────────────────────────────────────────────────────────────────────

def apply_rosetta_stone(
    text: str,
    rosetta_stone: dict[str, dict[str, Any]],
    target_domain: str | None = None,
) -> str:
    """Apply Rosetta Stone translations to reframe corporate language.

    Scans the text for corporate framing keywords and appends
    community-sector equivalents in parentheses where the community
    terminology is not already present.  Preserves the original text
    structure — only adds context, never removes content.

    Example:
        Input:  "Led cross-departmental compliance workstreams"
        Output: "Led cross-departmental compliance workstreams
                 (Complex Case Coordination, MDT Collaboration)"
    """
    if not text or not rosetta_stone:
        return text

    applied_bridges: list[str] = []

    for _key, mapping in rosetta_stone.items():
        corporate = mapping.get("corporate_framing", "")
        community = mapping.get("community_translation", "")
        community_kws = mapping.get("community_keywords", [])

        if not corporate or not community:
            continue

        # Check if corporate framing keywords appear in the text
        corporate_terms = [
            term.strip().lower()
            for term in re.split(r"[,/]", corporate)
            if len(term.strip()) > 3
        ]

        text_lower = text.lower()
        match_found = any(term in text_lower for term in corporate_terms[:5])

        if match_found:
            # Check if community keywords are already present
            has_community = any(
                kw.lower() in text_lower for kw in community_kws[:3]
            )
            if not has_community and community_kws:
                bridge_kws = ", ".join(community_kws[:3])
                applied_bridges.append(bridge_kws)
                log.debug(
                    "Rosetta Stone applied: %s → %s (%s)",
                    corporate[:40], community, bridge_kws,
                )

    if applied_bridges:
        # Append all bridge keywords as a parenthetical to the text
        all_kws = ", ".join(applied_bridges)
        # Strip trailing period to append cleanly, then re-add
        stripped = text.rstrip(". ")
        text = f"{stripped} ({all_kws})."

    return text


def generate_bridge_paragraph(
    rosetta_stone: dict[str, dict[str, Any]],
    keyword_scores: dict[str, float],
) -> str:
    """Generate a Rosetta Stone bridge paragraph for cover letters.

    Selects the most relevant corporate-to-community translation based
    on the job ad keyword scores and constructs a bridging paragraph.
    """
    if not rosetta_stone:
        return ""

    # Find the best matching Rosetta Stone entry based on keyword overlap
    best_key: str | None = None
    best_score = -1.0

    for key, mapping in rosetta_stone.items():
        community_kws = mapping.get("community_keywords", [])
        score = 0.0
        for kw in community_kws:
            kw_lower = kw.lower()
            for domain, domain_score in keyword_scores.items():
                if kw_lower in domain.lower() or domain.lower() in kw_lower:
                    score += domain_score
        if score > best_score:
            best_score = score
            best_key = key

    if not best_key or best_key not in rosetta_stone:
        # Fall back to the first entry
        best_key = next(iter(rosetta_stone))

    mapping = rosetta_stone[best_key]
    corporate = mapping.get("corporate_framing", "")
    community = mapping.get("community_translation", "")
    bridge = mapping.get("contextual_bridge", "")
    community_kws = mapping.get("community_keywords", [])

    if bridge:
        return bridge

    # Construct a bridge paragraph from the mapping
    kw_phrase = ", ".join(community_kws[:3]) if community_kws else community
    paragraph = (
        f"My experience in {corporate.rstrip('.')} "
        f"translates directly into {community.lower()} capabilities. "
        f"I bring demonstrated competency in {kw_phrase}, "
        f"applying a structured, evidence-based approach developed through "
        f"years of cross-functional delivery in complex organisational environments."
    )
    return paragraph


# ──────────────────────────────────────────────────────────────────────
# Skill Selection
# ──────────────────────────────────────────────────────────────────────

def select_skills(
    taxonomy: dict[str, Any],
    keyword_scores: dict[str, float],
    max_skills: int = MAX_RESUME_SKILLS,
) -> list[str]:
    """Select and format skills for the resume skills section.

    Draws from the skills_inventory and Rosetta Stone community keywords.
    Prioritises skills that match job ad domain keywords.
    """
    skills_inventory = taxonomy.get("skills_inventory", [])
    rosetta_stone = taxonomy.get("rosetta_stone", {})
    keyword_bank = taxonomy.get("keyword_bank", {})

    # Collect candidate skill phrases
    candidates: list[tuple[float, str]] = []

    # From skills inventory
    for skill in skills_inventory:
        name = skill.get("skill_name", "")
        if not name:
            continue
        # Score by keyword overlap
        score = 0.0
        name_lower = name.lower()
        for domain, domain_score in keyword_scores.items():
            domain_kws = keyword_bank.get(domain, [])
            if any(kw.lower() in name_lower or name_lower in kw.lower() for kw in domain_kws):
                score += domain_score
        candidates.append((score, name))

    # From Rosetta Stone community keywords
    for _key, mapping in rosetta_stone.items():
        for kw in mapping.get("community_keywords", []):
            if not kw:
                continue
            score = 0.0
            kw_lower = kw.lower()
            for domain, domain_score in keyword_scores.items():
                if kw_lower in domain or domain in kw_lower:
                    score += domain_score * 1.5  # Boost community keywords
            candidates.append((score, kw))

    # Deduplicate by lowercase normalisation
    seen: set[str] = set()
    unique: list[tuple[float, str]] = []
    for score, name in candidates:
        key = name.lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append((score, name))

    unique.sort(key=lambda item: -item[0])
    return [item[1] for item in unique[:max_skills]]


# ──────────────────────────────────────────────────────────────────────
# Summary Generation
# ──────────────────────────────────────────────────────────────────────

def generate_professional_summary(
    config: GenerationConfig,
    selected_roles: list[dict[str, Any]],
    keyword_scores: dict[str, float],
    rosetta_stone: dict[str, dict[str, Any]],
) -> str:
    """Generate a 3–4 sentence professional summary.

    Deterministic fallback (no Gemini API). Composes a summary from
    domain tags, role history, and Rosetta Stone translations.
    """
    if config.summary_override is not None:
        cleaned = _clean_text(config.summary_override)
        if not cleaned:
            log.warning("Empty --summary override provided. Falling back to generated summary.")
        else:
            return cleaned

    # Collect top domain tags across selected roles
    tags: dict[str, int] = {}
    for role in selected_roles:
        for achievement in role.get("achievements", []):
            for tag in achievement.get("domain_tags", []):
                if isinstance(tag, str) and tag:
                    tags[tag] = tags.get(tag, 0) + 1

    top_tags = [
        tag.replace("_", " ").title()
        for tag, _ in sorted(tags.items(), key=lambda item: (-item[1], item[0]))[:3]
    ]

    # Get years of experience from role dates
    years = set()
    for role in selected_roles:
        start = role.get("start_date", "")
        end = role.get("end_date", "")
        for d in (start, end):
            match = re.search(r"(\d{4})", str(d))
            if match:
                years.add(int(match.group(1)))

    experience_span = ""
    if years:
        span = max(years) - min(years)
        if span > 0:
            experience_span = f"with over {span} years of experience "

    # Get the most relevant Rosetta Stone community translation
    community_capability = ""
    if rosetta_stone:
        best_score = -1.0
        best_translation = ""
        for _key, mapping in rosetta_stone.items():
            comm_kws = mapping.get("community_keywords", [])
            score = sum(
                keyword_scores.get(tag, 0.0)
                for kw in comm_kws
                for tag in keyword_scores
                if kw.lower() in tag or tag in kw.lower()
            )
            if score > best_score:
                best_score = score
                best_translation = mapping.get("community_translation", "")
        if best_translation:
            community_capability = f", with particular strength in {best_translation.lower()}"

    # Compose summary
    domain_phrase = ", ".join(top_tags) if top_tags else "community services"
    target = _clean_text(config.target_role)

    summary = (
        f"Dedicated professional {experience_span}"
        f"across {domain_phrase.lower()}{community_capability}. "
        f"Seeking to contribute to {target} with a track record of "
        f"delivering person-centred outcomes in complex service environments. "
        f"Brings a unique combination of corporate governance rigour and "
        f"frontline community sector practice."
    )
    return summary


# ──────────────────────────────────────────────────────────────────────
# CAR Recruiter Rewrite
# ──────────────────────────────────────────────────────────────────────

_RECRUITER_SYSTEM_PROMPT = """\
<role>
You are a senior recruitment consultant with 15+ years specialising in Australian public \
sector, NFP, and community services applications. You write with precision, authenticity, \
and a deep understanding of merit-based selection frameworks.
</role>

<task>
Rewrite the provided candidate narrative into a structured \
Context-Action-Result (CAR) response for a Key Selection Criteria (KSC) application. \
The output must be grounded exclusively in the supplied source material. \
You will produce a single JSON object and nothing else.
</task>

<community_services_values>
The Community Services sector in Australia is guided by these core values. \
Your rewrites must authentically reflect them — not as generic filler, but as \
demonstrated behaviours woven into the CAR narrative:

- PERSON-CENTRED: The client's dignity, voice, and self-determination are paramount. \
  Use language that centres the person, not the service system.
- TRAUMA-INFORMED: Acknowledge that clients carry complex histories. \
  Actions should reflect safety, trust, choice, collaboration, and empowerment.
- STRENGTHS-BASED: Frame challenges as opportunities to build capacity. \
  Highlight client resilience and the candidate's role in amplifying it.
- SOCIAL JUSTICE: Recognise structural disadvantage. Actions that address \
  systemic barriers (access, equity, inclusion) are valued over transactional service delivery.
- COLLABORATIVE: Emphasise partnerships — with clients, families, carers, \
  multidisciplinary teams, and community organisations.
- ACCOUNTABILITY: Evidence-based practice, clear documentation, \
  and outcome measurement matter in this sector.
</community_services_values>

<output_schema>
Return ONLY valid JSON with exactly these three keys:
{
  "context": "<40-100 words. The organisational setting, role mandate, and challenge or \
problem being addressed. Third-person framing of the situation.>",
  "action":  "<80-200 words. What the candidate personally did — concrete steps, methods, \
tools, and competencies deployed. First person, active voice, strong action verbs. \
Never begin with 'I am' or 'I have'.>",
  "result":  "<40-120 words. Measurable or observable outcomes. Quantify with real figures \
where the source provides them. Name stakeholder impact where relevant.>"
}
No text, explanation, or markdown outside the JSON object.
</output_schema>

<constraints>
GROUNDING: Use only information explicitly present in the source narrative and supporting \
career evidence provided. Do not invent, bridge, or extrapolate.

HALLUCINATION GUARD: Never fabricate organisation names, dates, job titles, team sizes, \
dollar values, or percentages not stated in the source material.

INFERENCE MARKING: Any word, phrase, or sentence you add that is not directly evidenced \
in the source MUST be wrapped in [[NEEDS_REVIEW: <your addition>]]. This includes \
connective tissue, implied scope, and estimated metrics.

AUSTRALIAN ENGLISH: Use Australian spelling and terminology throughout \
(e.g. "organisation" not "organization", "programme" not "program", \
"behaviour" not "behavior").

QUALITY BAR: A strong CAR response reads as a confident first-person account. \
Avoid passive voice, hedging language, and generic filler phrases \
("demonstrated ability to", "strong communication skills", "team player").
</constraints>

<few_shot_examples>
Study these gold-standard examples carefully. Match their tone, specificity, \
sector language, and structural balance exactly.

EXAMPLE 1 — KSC: Experience in providing direct support to vulnerable individuals
{
  "context": "Working in a homelessness outreach service, I was assigned a client who had \
been rough sleeping for over two years and had a deep distrust of support services due to \
past negative experiences. Rebuilding that trust was the prerequisite for any practical \
intervention.",
  "action": "I employed a trauma-informed approach, meeting the client on their terms in \
familiar public spaces rather than an office. Using active listening, I consistently \
followed through on small promises — bringing a coffee, a warm blanket — to demonstrate \
reliability over three weeks. I mapped local services and, with the client's gradual \
consent, facilitated a warm handover to a community mental health practitioner, ensuring \
continuity of care rather than a cold referral.",
  "result": "This patient, client-centred approach successfully broke the cycle of \
disengagement. The client entered supportive accommodation and began actively \
participating in their mental health recovery plan — an outcome that had not been \
achievable through previous service contacts."
}

EXAMPLE 2 — KSC: Ability to use lived experience of recovery
{
  "context": "A new client in our AOD recovery programme was expressing significant \
hopelessness, stating they did not believe long-term recovery was possible. The clinical \
team identified an opportunity for peer-led engagement to complement the therapeutic model.",
  "action": "Using intentional self-disclosure, I briefly shared that I had faced similar \
feelings early in my own journey, then immediately refocused the conversation on the \
client — applying motivational interviewing techniques to explore their values and what \
a life in recovery could mean for them. I shared practical, non-clinical strategies for \
managing early cravings, drawn from personal experience, without oversharing or \
making the session about myself.",
  "result": "The client reported a significant shift in perspective, describing the \
conversation as a turning point. They remained engaged in the programme and later \
volunteered as a peer mentor for newer members — demonstrating the multiplier effect \
of peer-led support."
}

EXAMPLE 3 — KSC: Demonstrated organisational skills
{
  "context": "Our annual community wellness event — serving over 300 residents — was at \
risk after a key service provider withdrew with 48 hours' notice. The Programme \
Coordinator needed immediate support to manage replacement sourcing, stakeholder \
communications, and materials updates simultaneously.",
  "action": "I created a shared tracking spreadsheet to manage potential replacement \
providers, their contact details, and communication status in real time. I drafted a \
clear, concise stakeholder update template so communications could go out the moment \
a replacement was confirmed. While the Coordinator handled provider negotiations by phone, \
I updated the event run sheet and promotional materials in parallel, eliminating \
sequential bottlenecks.",
  "result": "A replacement provider was secured within 24 hours. All stakeholder \
communications were distributed with a full day to spare. The event proceeded without \
disruption to the 300+ attendees, and the Coordinator noted the parallel-workstream \
approach as a model for future contingency planning."
}
</few_shot_examples>
"""


def _extract_grounding_evidence(
    history: dict[str, Any],
    competencies: list[str],
    max_bullets: int = 8,
) -> str:
    """Pull the top matching achievement bullets from career history as grounding evidence."""
    candidates: list[tuple[int, int, str]] = []
    for role_idx, role in enumerate(history.get("roles", [])):
        company = role.get("company", "")
        role_title = role.get("role", "")
        for ach_idx, ach in enumerate(role.get("achievements", [])):
            text = _clean_text(ach.get("raw_text", ""))
            if not text:
                continue
            tags = [t.lower().replace("_", " ") for t in ach.get("domain_tags", []) if isinstance(t, str)]
            match_count = sum(1 for c in competencies if c in " ".join(tags))
            if match_count > 0:
                prefix = f"[{company} / {role_title}] " if (company and company != "Unknown") else ""
                candidates.append((match_count, role_idx * 1000 + ach_idx, f"{prefix}{text}"))
    candidates.sort(key=lambda x: (-x[0], x[1]))
    bullets = [c[2] for c in candidates[:max_bullets]]
    return "\n".join(f"- {b}" for b in bullets)


def _rewrite_car_with_llm(
    full_text: str,
    criterion_text: str,
    competencies: list[str],
    history: dict[str, Any],
) -> dict[str, str] | None:
    """Call the Gemini API to rewrite narrative into structured CAR sections.

    Returns {"context": ..., "action": ..., "result": ...} or None on failure.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        log.debug("GEMINI_API_KEY not set — skipping LLM CAR rewrite")
        return None

    try:
        from google import genai  # noqa: PLC0415
        from google.genai import types  # noqa: PLC0415
    except ImportError:
        log.warning("google-genai package not installed — skipping LLM CAR rewrite")
        return None

    grounding = _extract_grounding_evidence(history, competencies)

    user_content = (
        f"SELECTION CRITERION:\n{criterion_text}\n\n"
        f"COMPETENCIES TO ADDRESS: {', '.join(competencies) or 'general'}\n\n"
        f"SOURCE NARRATIVE (raw career material):\n{full_text[:2000]}\n\n"
        f"SUPPORTING CAREER EVIDENCE (verified achievements from career history):\n"
        f"{grounding or '(none matched)'}\n\n"
        "Rewrite the source narrative into CAR sections addressing the criterion. "
        "Return JSON only: {{\"context\": \"...\", \"action\": \"...\", \"result\": \"...\"}}."
    )

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_content,
            config=types.GenerateContentConfig(
                system_instruction=_RECRUITER_SYSTEM_PROMPT,
                max_output_tokens=2048,
                temperature=0.3,
                responseMimeType="application/json",
                thinkingConfig=types.ThinkingConfig(thinkingBudget=0),
            ),
        )
        raw = response.text.strip()
        parsed = json.loads(raw)
        result = {
            "context": str(parsed.get("context", "")),
            "action": str(parsed.get("action", "")),
            "result": str(parsed.get("result", "")),
        }
        if not any(result.values()):
            return None
        return result
    except Exception as exc:  # noqa: BLE001
        log.warning("LLM CAR rewrite failed: %s", exc)
        return None


# ──────────────────────────────────────────────────────────────────────
# Cover Letter Detection Guard
# ──────────────────────────────────────────────────────────────────────

# Patterns that indicate a narrative is actually a cover letter or address block,
# not a genuine STAR/CAR achievement narrative. Used to filter ksc_curated.json
# entries that were mis-tagged as STAR during ETL.
_COVER_LETTER_RE = re.compile(
    r"(dear\s|to\s+whom\s+it\s+may\s|attn:|i\s+am\s+writing\s+to"
    r"|sincerely,|kind\s+regards,|yours\s+faithfully"
    r"|\d+/\d+\s+[a-z]+\s+street|\d+\s+[a-z]+\s+street\s+[a-z]+\s+vic)",
    re.IGNORECASE,
)


def _looks_like_cover_letter(text: str) -> bool:
    """Return True if the text appears to be a cover letter or address block."""
    return bool(_COVER_LETTER_RE.search(text[:500]))


# ──────────────────────────────────────────────────────────────────────
# KSC Engine
# ──────────────────────────────────────────────────────────────────────

def parse_criteria(criteria_text: str) -> list[dict[str, Any]]:
    """Parse selection criteria from position description text.

    Supports numbered lists, lettered lists, and bullet-point lists.
    Returns ``[{criterion_text, extracted_competencies}]``.
    """
    if not criteria_text:
        return []

    # Split on common criterion patterns
    # e.g., "1.", "1)", "a.", "a)", "•", "-", or blank-line-separated paragraphs
    lines = criteria_text.strip().split("\n")
    criteria: list[dict[str, Any]] = []
    current: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current:
                criteria.append(_build_criterion(" ".join(current)))
                current = []
            continue

        # Check for new criterion marker
        is_new = bool(re.match(
            r"^(?:\d+[.)]\s|[a-z][.)]\s|[•\-\*]\s|(?:criterion|criteria)\s*\d*\s*[:\-])",
            stripped, re.I,
        ))

        if is_new and current:
            criteria.append(_build_criterion(" ".join(current)))
            current = []

        # Strip the marker
        cleaned = re.sub(
            r"^(?:\d+[.)]\s*|[a-z][.)]\s*|[•\-\*]\s*|(?:criterion|criteria)\s*\d*\s*[:\-]\s*)",
            "", stripped, flags=re.I,
        )
        if cleaned:
            current.append(cleaned)

    if current:
        criteria.append(_build_criterion(" ".join(current)))

    return criteria[:MAX_KSC_CRITERIA]


def _build_criterion(text: str) -> dict[str, Any]:
    """Build a criterion dict with extracted competency keywords."""
    competency_keywords = [
        "communication", "teamwork", "leadership", "problem solving",
        "conflict resolution", "cultural safety", "risk assessment",
        "case management", "stakeholder engagement", "advocacy",
        "trauma informed", "harm reduction", "governance",
        "quality assurance", "compliance", "coordination",
        "facilitation", "collaboration", "complex needs",
        "person centred", "recovery oriented", "inclusive practice",
        "safety planning", "community development", "intake",
        "assessment", "service delivery", "program management",
    ]

    text_lower = text.lower()
    extracted = [kw for kw in competency_keywords if kw in text_lower]

    return {
        "criterion_text": _clean_text(text),
        "extracted_competencies": extracted,
    }


def build_ksc_response(
    criterion: dict[str, Any],
    narratives: list[dict[str, Any]],
    history: dict[str, Any],
    rosetta_stone: dict[str, dict[str, Any]],
) -> dict[str, str]:
    """Build a CAR response for a single criterion.

    Returns ``{context, action, result, support_bullet_1, support_bullet_2}``.
    """
    competencies = criterion.get("extracted_competencies", [])

    # KSC narrative guard: exclude cover letters and address blocks mis-tagged
    # as STAR in ksc_curated.json during ETL. Uses content-based detection.

    # Select the best narrative for this criterion
    matched = select_narratives(
        narratives=narratives,
        competency_targets=competencies,
        narrative_types=["STAR", "CAR"],
        max_count=1,
        exclude_cover_letters=True,
    )

    if not matched:
        matched = select_narratives(
            narratives=narratives,
            competency_targets=competencies,
            narrative_types=["STAR", "CAR", "achievement", "evidence"],
            max_count=1,
            exclude_cover_letters=True,
        )

    response = {"context": "", "action": "", "result": ""}

    if matched:
        narrative = matched[0]
        full_text = _clean_text(narrative.get("full_text", ""))
        criterion_text = criterion.get("criterion_text", "")

        # Attempt LLM-driven recruiter rewrite first; fall back to heuristic split
        llm_car = _rewrite_car_with_llm(full_text, criterion_text, competencies, history)
        if llm_car:
            response.update(llm_car)
        else:
            # Heuristic fallback: split on sentence boundaries into rough CAR thirds
            sentences = re.split(r"(?<=[.!?])\s+", full_text)
            total = len(sentences)
            if total >= 3:
                ctx_end = max(1, total // 4)
                act_end = max(ctx_end + 1, total * 3 // 4)
                response["context"] = " ".join(sentences[:ctx_end])
                response["action"] = " ".join(sentences[ctx_end:act_end])
                response["result"] = " ".join(sentences[act_end:])
            elif total == 2:
                response["context"] = sentences[0]
                response["action"] = sentences[1]
                response["result"] = "[[NEEDS_REVIEW: result section could not be extracted from available narrative]]"
            elif total == 1:
                response["context"] = sentences[0]
                response["action"] = "[[NEEDS_REVIEW: action section could not be extracted from available narrative]]"
                response["result"] = "[[NEEDS_REVIEW: result section could not be extracted from available narrative]]"

    # Select supporting bullets from career history
    support_bullets = _select_support_bullets(
        history, competencies, max_bullets=MAX_KSC_SUPPORT_BULLETS,
    )
    for idx, bullet in enumerate(support_bullets, start=1):
        response[f"support_bullet_{idx}"] = bullet

    return response


def _select_support_bullets(
    history: dict[str, Any],
    competencies: list[str],
    max_bullets: int = 2,
) -> list[str]:
    """Select supporting bullets from career history that match
    the criterion's competencies."""
    candidates: list[tuple[int, int, str]] = []

    for role_idx, role in enumerate(history.get("roles", [])):
        for ach_idx, achievement in enumerate(role.get("achievements", [])):
            if achievement.get("needs_review"):
                continue
            text = _bullet_text(achievement)
            if not text:
                continue

            tags = [
                t.lower().replace("_", " ")
                for t in achievement.get("domain_tags", [])
                if isinstance(t, str)
            ]
            match_count = sum(1 for c in competencies if c in " ".join(tags))

            if match_count > 0:
                candidates.append((match_count, role_idx * 100 + ach_idx, text))

    candidates.sort(key=lambda item: (-item[0], item[1]))
    return [item[2] for item in candidates[:max_bullets]]


# ──────────────────────────────────────────────────────────────────────
# KSC Word Count Validation
# ──────────────────────────────────────────────────────────────────────

def validate_ksc_word_counts(
    response: dict[str, str],
) -> list[str]:
    """Validate word counts for each CAR section.

    Returns a list of warning strings for out-of-range sections.
    """
    warnings: list[str] = []

    for section in ("context", "action", "result"):
        text = response.get(section, "")
        word_count = len(text.split()) if text else 0
        min_words, max_words = KSC_WORD_TARGETS.get(section, (0, 9999))

        if word_count < min_words:
            warnings.append(
                f"ksc_{section}_too_short: {word_count} words (min {min_words})"
            )
        elif word_count > max_words:
            warnings.append(
                f"ksc_{section}_too_long: {word_count} words (max {max_words})"
            )

    # Total word count
    total = sum(
        len(response.get(s, "").split())
        for s in ("context", "action", "result")
    )
    min_total, max_total = KSC_WORD_TARGETS["total"]
    if total < min_total:
        warnings.append(f"ksc_total_too_short: {total} words (min {min_total})")
    elif total > max_total:
        warnings.append(f"ksc_total_too_long: {total} words (max {max_total})")

    return warnings


# ──────────────────────────────────────────────────────────────────────
# Cover Letter Closing
# ──────────────────────────────────────────────────────────────────────

def generate_closing_paragraph(
    config: GenerationConfig,
    keyword_scores: dict[str, float],
) -> str:
    """Generate an employer-specific closing paragraph.

    Deterministic fallback (no Gemini API).
    """
    target = _clean_text(config.target_role)
    top_domains = list(keyword_scores.keys())[:2]
    domain_phrase = " and ".join(
        d.replace("_", " ") for d in top_domains
    ) if top_domains else "community services"

    if config.employer_type == EmployerType.GOVERNMENT:
        return (
            f"I am confident that my experience across {domain_phrase} "
            f"equips me to deliver high-quality outcomes in this {target} role. "
            f"I welcome the opportunity to discuss how my background aligns "
            f"with the requirements of this position and the priorities of your "
            f"organisation. I am available for interview at your convenience."
        )
    elif config.employer_type == EmployerType.NFP:
        return (
            f"I would welcome the opportunity to bring my skills in "
            f"{domain_phrase} to your team. I am deeply aligned with the "
            f"mission and values of your organisation, and I believe my "
            f"combination of corporate rigour and frontline community practice "
            f"would make a meaningful contribution to the {target} role."
        )
    else:
        return (
            f"I am excited by the opportunity to contribute to this {target} role, "
            f"bringing expertise in {domain_phrase} and a proven track record "
            f"of delivering results in complex stakeholder environments. "
            f"I would appreciate the chance to discuss my candidacy further."
        )
