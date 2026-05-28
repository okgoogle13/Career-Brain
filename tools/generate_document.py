#!/usr/bin/env python3
"""
Phase 5 document generator for Career Brain (v2).

Clones a Golden Master Google Doc, selects and injects tailored content
from the Career Brain JSON engines, validates ATS compliance, and writes
a redacted run report.

Supports three document types:
  - resume: ATS-compliant resume with role/bullet selection
  - cover_letter: Structured cover letter with Rosetta Stone bridge
  - ksc: Key Selection Criteria responses using CAR methodology

Usage:
  python3 generate_document.py --type resume --target "Project Worker at Launch Housing"
  python3 generate_document.py --type cover_letter --target "Case Manager at cohealth" --employer-type nfp
  python3 generate_document.py --type ksc --target "Intake Worker" --criteria criteria.txt
  python3 generate_document.py --type resume --target "Project Worker" --dry-run
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Load .env from project root so ANTHROPIC_API_KEY is available without manual export
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    for _line in _env_path.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

from content_engine import (
    DocumentType,
    EmployerType,
    GenerationConfig,
    apply_rosetta_stone,
    build_ksc_response,
    extract_job_ad_keywords,
    generate_bridge_paragraph,
    generate_closing_paragraph,
    generate_professional_summary,
    load_user_config,
    parse_criteria,
    select_all_bullets,
    select_bullets,
    select_narratives,
    select_roles,
    select_skills,
    validate_ksc_word_counts,
    MAX_RESUME_ROLES,
    MAX_BULLETS_PER_ROLE,
    MAX_RESUME_SKILLS,
    MAX_COVER_LETTER_EVIDENCE,
    MAX_KSC_CRITERIA,
    MAX_KSC_SUPPORT_BULLETS,
    SALUTATION_MAP,
)

BASE = Path(__file__).parent.parent  # project root
OUTPUT = BASE / "database"
DEFAULT_CONFIG = BASE / "config" / "doc_templates.json"
DEFAULT_USER_CONFIG = BASE / "config" / "user_config.json"
DEFAULT_REPORT = OUTPUT / "doc_generation_report.json"

HISTORY_FILE = "career_history_enriched.json"
NARRATIVES_FILE = "ksc_curated.json"
TAXONOMY_FILE = "skills_and_taxonomy.json"

DOC_LINK_TEMPLATE = "https://docs.google.com/document/d/{doc_id}/edit"
PLACEHOLDER_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")

# ──────────────────────────────────────────────────────────────────────
# v2 Placeholder Schemas
# ──────────────────────────────────────────────────────────────────────

PLACEHOLDER_SCHEMA_V2: dict[str, tuple[str, ...]] = {
    "resume": (
        # Contact (static)
        "{{CONTACT_NAME}}", "{{CONTACT_PHONE}}", "{{CONTACT_EMAIL}}", "{{CONTACT_LOCATION}}",
        # Summary
        "{{PROFESSIONAL_SUMMARY}}",
        # Skills
        *(f"{{{{SKILL_{i}}}}}" for i in range(1, MAX_RESUME_SKILLS + 1)),
        # Roles (up to 6 roles × 4 bullets + title/org/dates each)
        *(
            tag
            for r in range(1, MAX_RESUME_ROLES + 1)
            for tag in (
                f"{{{{ROLE_{r}_TITLE}}}}",
                f"{{{{ROLE_{r}_ORG}}}}",
                f"{{{{ROLE_{r}_DATES}}}}",
                *(f"{{{{ROLE_{r}_BULLET_{b}}}}}" for b in range(1, MAX_BULLETS_PER_ROLE + 1)),
            )
        ),
        # Education & Certs
        "{{EDUCATION_1}}", "{{EDUCATION_2}}",
        "{{CERT_1}}", "{{CERT_2}}", "{{CERT_3}}",
        # Legacy compatibility
        "{{TARGET_ROLE}}", "{{SUMMARY}}",
        *(f"{{{{BULLET_{i}}}}}" for i in range(1, 7)),
    ),
    "cover_letter": (
        # Contact (static)
        "{{CONTACT_NAME}}", "{{CONTACT_PHONE}}", "{{CONTACT_EMAIL}}", "{{CONTACT_LOCATION}}",
        # Employer
        "{{EMPLOYER_CONTACT_NAME}}", "{{EMPLOYER_ORG}}", "{{EMPLOYER_ADDRESS}}",
        "{{SALUTATION}}", "{{CURRENT_DATE}}",
        # Content paragraphs
        "{{HOOK_PARAGRAPH}}",
        "{{BRIDGE_PARAGRAPH}}",
        "{{EVIDENCE_PARAGRAPH_1}}", "{{EVIDENCE_PARAGRAPH_2}}",
        "{{CLOSING_PARAGRAPH}}",
        # Legacy compatibility
        "{{TARGET_ROLE}}", "{{SUMMARY}}",
        *(f"{{{{KSC_RESPONSE_{i}}}}}" for i in range(1, 4)),
    ),
    "ksc": (
        # Contact
        "{{CONTACT_NAME}}", "{{CONTACT_PHONE}}", "{{CONTACT_EMAIL}}", "{{CONTACT_LOCATION}}",
        "{{TARGET_ROLE}}", "{{EMPLOYER_ORG}}",
        # Criteria (up to 6)
        *(
            tag
            for c in range(1, MAX_KSC_CRITERIA + 1)
            for tag in (
                f"{{{{KSC_CRITERION_{c}_TEXT}}}}",
                f"{{{{KSC_{c}_CONTEXT}}}}",
                f"{{{{KSC_{c}_ACTION}}}}",
                f"{{{{KSC_{c}_RESULT}}}}",
                *(f"{{{{KSC_{c}_SUPPORT_BULLET_{b}}}}}" for b in range(1, MAX_KSC_SUPPORT_BULLETS + 1)),
            )
        ),
    ),
}

# ──────────────────────────────────────────────────────────────────────
# v1 backward compatibility — keep the old schema for tests
# ──────────────────────────────────────────────────────────────────────

RESUME_BULLET_COUNT = 6
COVER_LETTER_RESPONSE_COUNT = 3

PLACEHOLDER_SCHEMA = {
    "resume": (
        "{{TARGET_ROLE}}",
        "{{SUMMARY}}",
        *(f"{{{{BULLET_{i}}}}}" for i in range(1, RESUME_BULLET_COUNT + 1)),
    ),
    "cover_letter": (
        "{{TARGET_ROLE}}",
        "{{SUMMARY}}",
        *(f"{{{{KSC_RESPONSE_{i}}}}}" for i in range(1, COVER_LETTER_RESPONSE_COUNT + 1)),
    ),
}

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("generate_document")


class DocumentGenerationError(RuntimeError):
    """Raised when Phase 5 cannot safely generate a document."""


# ──────────────────────────────────────────────────────────────────────
# JSON Loading
# ──────────────────────────────────────────────────────────────────────

def load_json(path: Path, *, required: bool = True) -> dict[str, Any]:
    if not path.exists():
        if required:
            raise DocumentGenerationError(f"Required JSON file missing: {path}")
        return {}
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        raise DocumentGenerationError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise DocumentGenerationError(f"Expected object at top level of {path}")
    return data


def load_source_data(output_dir: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    history = load_json(output_dir / HISTORY_FILE)
    narratives = load_json(output_dir / NARRATIVES_FILE)
    taxonomy = load_json(output_dir / TAXONOMY_FILE, required=False)
    return history, narratives, taxonomy


def load_template_config(path: Path) -> dict[str, Any]:
    config = load_json(path)
    if not config:
        raise DocumentGenerationError(f"Template config is empty: {path}")
    return config


def load_ats_rules() -> dict[str, Any]:
    path = BASE / "config" / "ats_rules.json"
    try:
        return load_json(path, required=False)
    except Exception as exc:
        log.warning(f"Failed to load ats_rules.json: {exc}")
        return {}



# ──────────────────────────────────────────────────────────────────────
# Template Resolution
# ──────────────────────────────────────────────────────────────────────

def resolve_template_doc_id(
    config: dict[str, Any],
    template: str,
    template_variant: str | None = None,
    *,
    allow_placeholder: bool = False,
) -> str:
    entry = config.get(template)
    if entry is None:
        raise DocumentGenerationError(f"No template config found for '{template}'")

    if isinstance(entry, str):
        doc_id = entry
    elif isinstance(entry, dict):
        if template_variant:
            variants = entry.get("variants", {})
            variant = variants.get(template_variant)
            if isinstance(variant, str):
                doc_id = variant
            elif isinstance(variant, dict):
                doc_id = variant.get("template_doc_id", "")
            else:
                raise DocumentGenerationError(
                    f"No variant '{template_variant}' found for '{template}'"
                )
        else:
            doc_id = entry.get("template_doc_id", "")
    else:
        raise DocumentGenerationError(f"Invalid template config for '{template}'")

    if not doc_id or ("REPLACE_WITH" in doc_id and not allow_placeholder):
        raise DocumentGenerationError(
            f"Google Doc ID is not configured for '{template}'"
        )
    return doc_id


# ──────────────────────────────────────────────────────────────────────
# Text Helpers
# ──────────────────────────────────────────────────────────────────────

def _clean_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    text = " ".join(value.split())
    # Strip leading bullet characters
    text = re.sub(r"^[•\-\*▪◦‣➤►→]\s*", "", text)
    # Strip first-person pronouns and common weak openers
    text = re.sub(r"^(I\s+)?(am\s+|have\s+|will\s+)?(completed|working|conducted|conduct|delivered|managed)\s+", lambda m: m.group(3).capitalize() + " ", text, flags=re.IGNORECASE)
    text = re.sub(r"^I\s+([a-z])", lambda m: m.group(1).upper(), text, flags=re.IGNORECASE)
    return text.strip()


def _format_date_range(start: str | None, end: str | None) -> str:
    """Format start/end dates into a display range (MMM YYYY)."""
    def parse_date(d: str | None) -> str:
        if not d: return "Unknown"
        d = d.strip()
        if not d or d.lower() in ("unknown", "present", "current", "ongoing"):
            return "Present" if d.lower() in ("present", "current", "ongoing") else "Unknown"
        # Match Month Year
        m = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s-]*(\d{4})', d, re.IGNORECASE)
        if m:
            return f"{m.group(1).capitalize()} {m.group(2)}"
        # Match MM/YYYY
        m2 = re.search(r'(\d{1,2})[/\-](\d{4})', d)
        if m2:
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            try:
                month_idx = int(m2.group(1)) - 1
                if 0 <= month_idx < 12:
                    return f"{months[month_idx]} {m2.group(2)}"
            except ValueError:
                pass
        return d # Fallback
        
    s = parse_date(start)
    e = parse_date(end)
    return f"{s} – {e}"


# ──────────────────────────────────────────────────────────────────────
# v1 Compatibility Functions (kept for existing tests)
# ──────────────────────────────────────────────────────────────────────

def _candidate_bullets(history: dict[str, Any]) -> list[str]:
    bullets: list[str] = []
    for role in history.get("roles", []):
        for achievement in role.get("achievements", []):
            if achievement.get("needs_review"):
                continue
            text = _clean_text(
                achievement.get("raw_text")
                or achievement.get("text")
                or achievement.get("achievement")
            )
            if text:
                bullets.append(text)
    return bullets


def _candidate_narratives(narratives: dict[str, Any]) -> list[str]:
    indexed = []
    for index, narrative in enumerate(narratives.get("narratives", [])):
        text = _clean_text(narrative.get("full_text"))
        if not text:
            continue
        tier = narrative.get("quality_tier", 99)
        try:
            tier_value = int(tier)
        except (TypeError, ValueError):
            tier_value = 99
        quality_score = narrative.get("quality_score", 0)
        word_count = narrative.get("word_count", 0)
        indexed.append((tier_value, -int(quality_score or 0), -int(word_count or 0), index, text))
    indexed.sort()
    return [item[-1] for item in indexed]


def _derive_summary(
    target_role: str,
    history: dict[str, Any],
    narratives: dict[str, Any],
    taxonomy: dict[str, Any] | None = None,
) -> str:
    tags: dict[str, int] = {}
    for role in history.get("roles", []):
        for achievement in role.get("achievements", []):
            for tag in achievement.get("domain_tags", []):
                if isinstance(tag, str) and tag:
                    tags[tag] = tags.get(tag, 0) + 1

    top_tags = [tag.replace("_", " ") for tag, _ in sorted(tags.items(), key=lambda item: (-item[1], item[0]))[:3]]
    if top_tags:
        return f"Targeting {target_role} roles with evidence across {', '.join(top_tags)}."

    if _candidate_bullets(history):
        return f"Targeting {target_role} roles with selected achievements from the Career Brain evidence base."

    if narratives.get("narratives"):
        return f"Targeting {target_role} roles with curated career evidence and selection criteria examples."

    if taxonomy and taxonomy:
        return f"Targeting {target_role} roles with a structured skills taxonomy and career evidence base."

    return ""


def _count_stats(values: dict[str, str]) -> dict[str, int]:
    filled = sum(1 for value in values.values() if value)
    blank = sum(1 for value in values.values() if not value)
    return {
        "total": len(values),
        "filled": filled,
        "blank": blank,
    }


def build_placeholder_values(
    *,
    template: str,
    target_role: str,
    history: dict[str, Any],
    narratives: dict[str, Any],
    taxonomy: dict[str, Any] | None = None,
    summary: str | None = None,
    require_summary: bool = False,
) -> tuple[dict[str, str], dict[str, int]]:
    """v1 placeholder builder — kept for backward compatibility and existing tests."""
    if template not in PLACEHOLDER_SCHEMA:
        raise DocumentGenerationError(f"Unsupported template: {template}")
    if require_summary and not _clean_text(summary):
        raise DocumentGenerationError("Required placeholder data missing: {{SUMMARY}}")

    values = {placeholder: "" for placeholder in PLACEHOLDER_SCHEMA[template]}
    values["{{TARGET_ROLE}}"] = _clean_text(target_role)
    values["{{SUMMARY}}"] = _clean_text(summary) or _derive_summary(
        target_role=values["{{TARGET_ROLE}}"],
        history=history,
        narratives=narratives,
        taxonomy=taxonomy,
    )

    if template == "resume":
        for index, bullet in enumerate(_candidate_bullets(history)[:RESUME_BULLET_COUNT], start=1):
            values[f"{{{{BULLET_{index}}}}}"] = bullet
    elif template == "cover_letter":
        for index, response in enumerate(_candidate_narratives(narratives)[:COVER_LETTER_RESPONSE_COUNT], start=1):
            values[f"{{{{KSC_RESPONSE_{index}}}}}"] = response

    missing_required = [
        placeholder
        for placeholder in ("{{TARGET_ROLE}}", "{{SUMMARY}}")
        if not values.get(placeholder)
    ]
    if template == "resume" and not values.get("{{BULLET_1}}"):
        missing_required.append("{{BULLET_1}}")
    if template == "cover_letter" and not values.get("{{KSC_RESPONSE_1}}"):
        missing_required.append("{{KSC_RESPONSE_1}}")
    if missing_required:
        missing = ", ".join(sorted(set(missing_required)))
        raise DocumentGenerationError(f"Required placeholder data missing: {missing}")

    return values, _count_stats(values)


# ──────────────────────────────────────────────────────────────────────
# v2 Placeholder Builder
# ──────────────────────────────────────────────────────────────────────

def build_placeholder_values_v2(
    *,
    config: GenerationConfig,
    history: dict[str, Any],
    narratives: dict[str, Any],
    taxonomy: dict[str, Any],
    user_config: dict[str, Any],
) -> tuple[dict[str, str], dict[str, int], list[str]]:
    """Build all placeholder values for the given document type.

    Returns ``(values, stats, warnings)``.
    """
    doc_type = config.doc_type.value
    if doc_type not in PLACEHOLDER_SCHEMA_V2:
        raise DocumentGenerationError(f"Unsupported document type: {doc_type}")

    values = {ph: "" for ph in PLACEHOLDER_SCHEMA_V2[doc_type]}
    warnings: list[str] = []

    # ── Static contact info ──
    contact = user_config.get("contact", {})
    values["{{CONTACT_NAME}}"] = _clean_text(contact.get("name", ""))
    values["{{CONTACT_PHONE}}"] = _clean_text(contact.get("phone", ""))
    values["{{CONTACT_EMAIL}}"] = _clean_text(contact.get("email", ""))
    values["{{CONTACT_LOCATION}}"] = _clean_text(contact.get("location", ""))

    if not values.get("{{CONTACT_NAME}}"):
        warnings.append("contact_name_missing")

    # ── Target role ──
    target = _clean_text(config.target_role)
    if "{{TARGET_ROLE}}" in values:
        values["{{TARGET_ROLE}}"] = target

    # ── Extract keyword scores from job ad ──
    keyword_bank = taxonomy.get("keyword_bank", {})
    keyword_scores = extract_job_ad_keywords(
        config.job_ad_text or "", keyword_bank,
    )

    rosetta_stone = taxonomy.get("rosetta_stone", {})

    # ── Type-specific content ──
    if doc_type == "resume":
        _build_resume_values(
            values, warnings, config, history, narratives, taxonomy,
            keyword_scores, rosetta_stone, user_config,
        )
    elif doc_type == "cover_letter":
        _build_cover_letter_values(
            values, warnings, config, history, narratives, taxonomy,
            keyword_scores, rosetta_stone,
        )
    elif doc_type == "ksc":
        _build_ksc_values(
            values, warnings, config, history, narratives,
            keyword_scores, rosetta_stone,
        )

    # ── Post-processing: Australian Terminology (BS-6.1) ──
    ats_rules = load_ats_rules()
    au_mappings = ats_rules.get("terminology", {}).get("australian_mappings", {})
    if au_mappings:
        for ph, text in values.items():
            if not text:
                continue
            # Perform whole-word, case-insensitive substitution
            for eng_term, au_term in au_mappings.items():
                def preserve_case_replace(match):
                    original = match.group(0)
                    if original.isupper():
                        return au_term.upper()
                    if original[0].isupper():
                        return au_term[0].upper() + au_term[1:]
                    return au_term
                pattern = re.compile(r'\b' + re.escape(eng_term) + r'\b', re.IGNORECASE)
                text = pattern.sub(preserve_case_replace, text)
            values[ph] = text

    return values, _count_stats(values), warnings



def _build_resume_values(
    values: dict[str, str],
    warnings: list[str],
    config: GenerationConfig,
    history: dict[str, Any],
    narratives: dict[str, Any],
    taxonomy: dict[str, Any],
    keyword_scores: dict[str, float],
    rosetta_stone: dict[str, dict[str, Any]],
    user_config: dict[str, Any],
) -> None:
    """Populate resume placeholder values."""
    # Professional summary
    selected_roles = select_roles(history, config.target_role, keyword_scores)
    summary = generate_professional_summary(
        config, selected_roles, keyword_scores, rosetta_stone,
    )
    values["{{PROFESSIONAL_SUMMARY}}"] = summary
    values["{{SUMMARY}}"] = summary  # Legacy compat

    # Skills
    skills = select_skills(taxonomy, keyword_scores)
    for idx, skill in enumerate(skills[:MAX_RESUME_SKILLS], start=1):
        values[f"{{{{SKILL_{idx}}}}}"] = skill

    # Roles and bullets
    for role_idx, role in enumerate(selected_roles[:MAX_RESUME_ROLES], start=1):
        values[f"{{{{ROLE_{role_idx}_TITLE}}}}"] = _clean_text(role.get("role", ""))
        values[f"{{{{ROLE_{role_idx}_ORG}}}}"] = _clean_text(role.get("company", ""))
        values[f"{{{{ROLE_{role_idx}_DATES}}}}"] = _format_date_range(
            role.get("start_date"), role.get("end_date"),
        )
        bullets = select_bullets(role, keyword_scores)
        for b_idx, bullet in enumerate(bullets[:MAX_BULLETS_PER_ROLE], start=1):
            if config.rosetta:
                bullet = apply_rosetta_stone(bullet, rosetta_stone)
            values[f"{{{{ROLE_{role_idx}_BULLET_{b_idx}}}}}"] = _clean_text(bullet)

    # Legacy flat bullets (hardcoded 6 to decouple from v1 constants)
    flat_bullets = select_all_bullets(history, keyword_scores, max_total=6)
    for idx, bullet in enumerate(flat_bullets, start=1):
        if config.rosetta:
            bullet = apply_rosetta_stone(bullet, rosetta_stone)
        values[f"{{{{BULLET_{idx}}}}}"] = _clean_text(bullet)


    # Education & Certs
    education = user_config.get("education", [])
    for idx, edu in enumerate(education[:2], start=1):
        values[f"{{{{EDUCATION_{idx}}}}}"] = _clean_text(edu)

    certs = user_config.get("certifications", [])
    for idx, cert in enumerate(certs[:3], start=1):
        values[f"{{{{CERT_{idx}}}}}"] = _clean_text(cert)

    if not selected_roles:
        warnings.append("no_roles_selected")
    if not flat_bullets:
        warnings.append("no_bullets_available")


def _build_cover_letter_values(
    values: dict[str, str],
    warnings: list[str],
    config: GenerationConfig,
    history: dict[str, Any],
    narratives: dict[str, Any],
    taxonomy: dict[str, Any],
    keyword_scores: dict[str, float],
    rosetta_stone: dict[str, dict[str, Any]],
) -> None:
    """Populate cover letter placeholder values."""
    all_narratives = narratives.get("narratives", [])

    # Employer info
    target = _clean_text(config.target_role)
    # Try to extract org name from "Role at Org" pattern
    org_name = ""
    if " at " in target:
        org_name = target.split(" at ", 1)[1].strip()
    values["{{EMPLOYER_ORG}}"] = org_name
    values["{{EMPLOYER_CONTACT_NAME}}"] = ""
    values["{{EMPLOYER_ADDRESS}}"] = ""
    values["{{SALUTATION}}"] = SALUTATION_MAP.get(
        config.employer_type, "Hiring Manager"
    )
    values["{{CURRENT_DATE}}"] = datetime.now(timezone.utc).strftime("%-d %B %Y")
    values["{{TARGET_ROLE}}"] = target

    # Hook paragraph (from narratives type "hook")
    hooks = select_narratives(
        all_narratives, narrative_types=["hook"], max_count=1,
    )
    if hooks:
        values["{{HOOK_PARAGRAPH}}"] = _clean_text(hooks[0].get("full_text", ""))
    else:
        # Fallback: use a high-tier pivot narrative
        pivots = select_narratives(
            all_narratives, narrative_types=["pivot", "hook"], max_count=1,
        )
        if pivots:
            values["{{HOOK_PARAGRAPH}}"] = _clean_text(pivots[0].get("full_text", ""))
            warnings.append("no_hook_narrative_used_pivot_fallback")
        else:
            warnings.append("no_hook_or_pivot_narrative_available")

    # Bridge paragraph (Rosetta Stone)
    bridge = generate_bridge_paragraph(rosetta_stone, keyword_scores)
    values["{{BRIDGE_PARAGRAPH}}"] = bridge

    # Evidence paragraphs (STAR/CAR narratives)
    evidence = select_narratives(
        all_narratives,
        narrative_types=["STAR", "CAR"],
        max_count=MAX_COVER_LETTER_EVIDENCE,
    )
    for idx, narrative in enumerate(evidence, start=1):
        values[f"{{{{EVIDENCE_PARAGRAPH_{idx}}}}}"] = _clean_text(
            narrative.get("full_text", ""),
        )

    # Closing paragraph
    closing = generate_closing_paragraph(config, keyword_scores)
    values["{{CLOSING_PARAGRAPH}}"] = closing

    # Legacy summary
    values["{{SUMMARY}}"] = values.get("{{HOOK_PARAGRAPH}}", "")

    # Legacy KSC_RESPONSE placeholders
    tiered = _candidate_narratives(narratives)
    for idx, response in enumerate(tiered[:COVER_LETTER_RESPONSE_COUNT], start=1):
        values[f"{{{{KSC_RESPONSE_{idx}}}}}"] = response

    if not values.get("{{HOOK_PARAGRAPH}}"):
        warnings.append("hook_paragraph_empty")


def _build_ksc_values(
    values: dict[str, str],
    warnings: list[str],
    config: GenerationConfig,
    history: dict[str, Any],
    narratives: dict[str, Any],
    keyword_scores: dict[str, float],
    rosetta_stone: dict[str, dict[str, Any]],
) -> None:
    """Populate KSC placeholder values."""
    target = _clean_text(config.target_role)
    values["{{TARGET_ROLE}}"] = target

    # Extract org name
    org_name = ""
    if " at " in target:
        org_name = target.split(" at ", 1)[1].strip()
    values["{{EMPLOYER_ORG}}"] = org_name

    # Parse criteria
    criteria_list = []
    if config.criteria_text:
        criteria_list = parse_criteria("\n".join(config.criteria_text))

    if not criteria_list:
        warnings.append("no_criteria_provided_or_parsed")
        return

    all_narratives = narratives.get("narratives", [])

    for c_idx, criterion in enumerate(criteria_list[:MAX_KSC_CRITERIA], start=1):
        values[f"{{{{KSC_CRITERION_{c_idx}_TEXT}}}}"] = criterion.get("criterion_text", "")

        # Build CAR response
        response = build_ksc_response(
            criterion, all_narratives, history, rosetta_stone,
        )

        values[f"{{{{KSC_{c_idx}_CONTEXT}}}}"] = response.get("context", "")
        values[f"{{{{KSC_{c_idx}_ACTION}}}}"] = response.get("action", "")
        values[f"{{{{KSC_{c_idx}_RESULT}}}}"] = response.get("result", "")

        for b_idx in range(1, MAX_KSC_SUPPORT_BULLETS + 1):
            bullet = response.get(f"support_bullet_{b_idx}", "")
            values[f"{{{{KSC_{c_idx}_SUPPORT_BULLET_{b_idx}}}}}"] = bullet

        # Validate word counts
        wc_warnings = validate_ksc_word_counts(response)
        for w in wc_warnings:
            warnings.append(f"criterion_{c_idx}_{w}")


# ──────────────────────────────────────────────────────────────────────
# Google Docs API Operations
# ──────────────────────────────────────────────────────────────────────

def make_replace_requests(values: dict[str, str]) -> list[dict[str, Any]]:
    requests = []
    for placeholder, replacement in sorted(values.items()):
        requests.append(
            {
                "replaceAllText": {
                    "containsText": {
                        "text": placeholder,
                        "matchCase": True,
                    },
                    "replaceText": replacement,
                }
            }
        )
    return requests


def find_unresolved_placeholders(text: str) -> list[str]:
    return sorted(set(PLACEHOLDER_RE.findall(text or "")))


def _extract_document_text(document: dict[str, Any]) -> str:
    parts: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            text_run = node.get("textRun")
            if isinstance(text_run, dict):
                content = text_run.get("content")
                if isinstance(content, str):
                    parts.append(content)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(document.get("body", {}).get("content", []))
    for header in document.get("headers", {}).values():
        walk(header.get("content", []))
    for footer in document.get("footers", {}).values():
        walk(footer.get("content", []))
    for footnote in document.get("footnotes", {}).values():
        walk(footnote.get("content", []))

    return "".join(parts)


def validate_document_structure(document: dict[str, Any]) -> list[str]:
    """Check word counts, section presence, and ATS compliance post-generation."""
    warnings: list[str] = []
    text = _extract_document_text(document)
    total_words = len(text.split())

    if total_words < 100:
        warnings.append("document_too_short")
    if total_words > 3000:
        warnings.append("document_too_long")

    # Check for ATS-breaking patterns based on centralized rules
    ats_rules = load_ats_rules()
    struct_rules = ats_rules.get("structure", {})
    allow_inline = struct_rules.get("allow_inline_objects", False)

    if not allow_inline and document.get("inlineObjects"):
        warnings.append("inline_objects_detected_ats_risk")

    # Check for forbidden characters in generated text
    vocab_rules = ats_rules.get("vocabulary", {})
    forbidden_chars = vocab_rules.get("forbidden_characters", [])
    for char in forbidden_chars:
        if char in text:
            warnings.append(f"forbidden_character_detected_ats_risk: '{char}'")

    return warnings



def build_google_services() -> tuple[Any, Any]:
    try:
        from google.oauth2 import service_account
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise DocumentGenerationError(
            "Google API dependencies are missing. Run: "
            "pip install google-api-python-client google-auth-oauthlib google-auth-httplib2"
        ) from exc

    scopes = [
        "https://www.googleapis.com/auth/documents",
        "https://www.googleapis.com/auth/drive",
    ]
    service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if service_account_path:
        credentials = service_account.Credentials.from_service_account_file(
            service_account_path,
            scopes=scopes,
        )
    else:
        client_secrets_path = Path(os.getenv("GOOGLE_OAUTH_CLIENT_SECRETS", "credentials.json"))
        token_path = Path(os.getenv("GOOGLE_OAUTH_TOKEN", "token.json"))
        credentials = None
        if token_path.exists():
            credentials = Credentials.from_authorized_user_file(str(token_path), scopes)
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        if not credentials or not credentials.valid:
            if not client_secrets_path.exists():
                raise DocumentGenerationError(
                    "OAuth client secrets not found. Set GOOGLE_OAUTH_CLIENT_SECRETS "
                    "or GOOGLE_APPLICATION_CREDENTIALS."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets_path), scopes)
            credentials = flow.run_local_server(port=0)
            token_path.write_text(credentials.to_json(), encoding="utf-8")

    docs_service = build("docs", "v1", credentials=credentials)
    drive_service = build("drive", "v3", credentials=credentials)
    return docs_service, drive_service


def resolve_target_folder(
    drive_service: Any,
    doc_type: str,
    folder_config: dict[str, str],
) -> str | None:
    """Resolve the target Drive folder ID for the given document type."""
    folder_map = {
        "resume": "resumes",
        "cover_letter": "cover_letters",
        "ksc": "ksc_responses",
    }
    folder_key = folder_map.get(doc_type, "")
    folder_id = folder_config.get(folder_key, "")

    if folder_id and "REPLACE_WITH" not in folder_id:
        return folder_id
    return None


def clone_and_replace(
    *,
    docs_service: Any,
    drive_service: Any,
    template_doc_id: str,
    values: dict[str, str],
    target_role: str,
    template: str,
    target_folder_id: str | None = None,
) -> tuple[str, str, list[str]]:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    copy_body: dict[str, Any] = {
        "name": f"Career Brain {template} - {target_role} - {timestamp}",
    }

    try:
        copied = (
            drive_service.files()
            .copy(
                fileId=template_doc_id,
                body=copy_body,
                fields="id, webViewLink",
            )
            .execute()
        )
        doc_id = copied["id"]
        
        if target_folder_id:
            file_info = drive_service.files().get(fileId=doc_id, fields="parents").execute()
            previous_parents = ",".join(file_info.get("parents", []))
            if target_folder_id not in file_info.get("parents", []):
                drive_service.files().update(
                    fileId=doc_id,
                    addParents=target_folder_id,
                    removeParents=previous_parents,
                ).execute()

        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": make_replace_requests(values)},
        ).execute()

        document = docs_service.documents().get(documentId=doc_id).execute()
    except Exception as exc:
        if type(exc).__name__ == "HttpError":
            raise DocumentGenerationError(f"Google API Error: {exc}") from exc
        raise

    unresolved = find_unresolved_placeholders(_extract_document_text(document))
    doc_link = copied.get("webViewLink") or DOC_LINK_TEMPLATE.format(doc_id=doc_id)
    return doc_id, doc_link, unresolved


# ──────────────────────────────────────────────────────────────────────
# Reporting
# ──────────────────────────────────────────────────────────────────────

def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(
    *,
    template: str,
    template_variant: str | None,
    template_doc_id: str,
    generated_doc_id: str | None,
    generated_doc_link: str | None,
    placeholder_stats: dict[str, int],
    unresolved_tokens: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    return {
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "template": template,
        "template_variant": template_variant,
        "template_doc_id": template_doc_id,
        "generated_doc_id": generated_doc_id,
        "generated_doc_link": generated_doc_link,
        "placeholder_stats": placeholder_stats,
        "unresolved_tokens": unresolved_tokens,
        "warnings": warnings,
    }


# ──────────────────────────────────────────────────────────────────────
# CLI Argument Parsing
# ──────────────────────────────────────────────────────────────────────

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Career Brain Phase 5 — Generate ATS-compliant Google Docs "
        "from the Career Brain knowledge base.",
    )

    # v2 arguments
    parser.add_argument(
        "--type",
        dest="doc_type",
        choices=["resume", "cover_letter", "ksc"],
        default=None,
        help="Document type to generate.",
    )
    parser.add_argument(
        "--target", required=True,
        help='Target role (e.g., "Project Worker at Launch Housing").',
    )
    parser.add_argument(
        "--variant", default=None,
        help="Template variant (e.g., chronological, hybrid, government).",
    )
    parser.add_argument(
        "--job-ad", type=Path, default=None,
        help="Path to job ad text file for keyword extraction.",
    )
    parser.add_argument(
        "--employer-type",
        choices=["government", "nfp", "private"],
        default="nfp",
        help="Employer type for cover letter tone.",
    )
    parser.add_argument(
        "--criteria", default=None,
        help="KSC criteria text: path to a file OR inline text string (required for --type ksc).",
    )
    parser.add_argument(
        "--user-config", type=Path, default=DEFAULT_USER_CONFIG,
        help="Path to user config JSON (contact info, education, certs).",
    )

    # v1 backward-compat argument
    parser.add_argument(
        "--template",
        choices=["resume", "cover_letter"],
        default=None,
        help="(v1 compat) Logical template type. Use --type instead.",
    )
    parser.add_argument(
        "--template-variant", default=None,
        help="(v1 compat) Template variant. Use --variant instead.",
    )
    parser.add_argument(
        "--config", type=Path, default=DEFAULT_CONFIG,
        help="Path to doc template config JSON.",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=OUTPUT,
        help="Directory containing Career Brain JSON outputs.",
    )
    parser.add_argument(
        "--out-report", type=Path, default=DEFAULT_REPORT,
        help="Path for redacted document generation report.",
    )
    parser.add_argument(
        "--summary", default=None,
        help="Optional summary override.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Build placeholder values and report without calling Google APIs.",
    )
    parser.add_argument(
        "--rosetta", action="store_true", default=True,
        help="Apply Rosetta Stone community translation to corporate-dense resume bullets.",
    )
    parser.add_argument(
        "--no-rosetta", action="store_false", dest="rosetta",
        help="Disable Rosetta Stone community translation for resume bullets.",
    )


    args = parser.parse_args(argv)

    # Resolve doc_type from v1 --template if --type not given
    if args.doc_type is None:
        if args.template:
            args.doc_type = args.template
        else:
            parser.error("--type is required (or use legacy --template)")

    # Resolve variant from v1 --template-variant if --variant not given
    if args.variant is None and args.template_variant:
        args.variant = args.template_variant

    return args


# ──────────────────────────────────────────────────────────────────────
# Main Entrypoint
# ──────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    assert set(EmployerType) == set(SALUTATION_MAP.keys()), "EmployerType choices must match SALUTATION_MAP"
    args = parse_args(argv)
    all_warnings: list[str] = []

    try:
        # Load source data
        history, narratives, taxonomy = load_source_data(args.output_dir)
        config_data = load_template_config(args.config)

        # Resolve template doc ID
        template_key = args.doc_type
        template_doc_id = resolve_template_doc_id(
            config_data,
            template_key,
            args.variant,
            allow_placeholder=args.dry_run,
        )

        # Load job ad text if provided
        job_ad_text = None
        if args.job_ad and args.job_ad.exists():
            job_ad_text = args.job_ad.read_text(encoding="utf-8")

        # Load criteria text if provided (file path or inline string — BS-4.2)
        criteria_text = None
        if args.criteria:
            criteria_path = Path(args.criteria)
            if criteria_path.exists():
                criteria_text = criteria_path.read_text(encoding="utf-8").split("\n")
            else:
                # Treat as inline text — use splitlines so parse_criteria
                # can correctly split numbered/bulleted inline strings
                criteria_text = args.criteria.splitlines() or [args.criteria]

        # Build generation config
        gen_config = GenerationConfig(
            doc_type=DocumentType(args.doc_type),
            target_role=args.target,
            variant=args.variant,
            employer_type=EmployerType(args.employer_type),
            job_ad_text=job_ad_text,
            criteria_text=criteria_text,
            dry_run=args.dry_run,
            summary_override=args.summary,
            rosetta=args.rosetta,
        )


        # Load user config
        user_config = load_user_config(args.user_config)

        # Build placeholder values using v2 engine
        values, placeholder_stats, content_warnings = build_placeholder_values_v2(
            config=gen_config,
            history=history,
            narratives=narratives,
            taxonomy=taxonomy,
            user_config=user_config,
        )
        all_warnings.extend(content_warnings)

        if args.doc_type == "resume" and ("no_roles_selected" in all_warnings or "no_bullets_available" in all_warnings):
            raise DocumentGenerationError("No usable roles or bullets found for this target role.")

        # Execute or dry-run
        generated_doc_id = None
        generated_doc_link = None
        unresolved_tokens: list[str] = []

        if args.dry_run:
            all_warnings.append("dry_run_no_google_document_created")
            log.info("DRY RUN — placeholder values built, no Google API calls made.")
        else:
            docs_service, drive_service = build_google_services()

            # Resolve target folder
            folder_config = config_data.get("drive_folders", {})
            target_folder_id = resolve_target_folder(
                drive_service, args.doc_type, folder_config,
            )

            generated_doc_id, generated_doc_link, unresolved_tokens = clone_and_replace(
                docs_service=docs_service,
                drive_service=drive_service,
                template_doc_id=template_doc_id,
                values=values,
                target_role=args.target,
                template=args.doc_type,
                target_folder_id=target_folder_id,
            )
            if unresolved_tokens:
                all_warnings.append("unresolved_placeholders_after_replacement")

        # Write report
        report = build_report(
            template=args.doc_type,
            template_variant=args.variant,
            template_doc_id=template_doc_id,
            generated_doc_id=generated_doc_id,
            generated_doc_link=generated_doc_link,
            placeholder_stats=placeholder_stats,
            unresolved_tokens=unresolved_tokens,
            warnings=all_warnings,
        )
        write_report(args.out_report, report)

        # Summary log
        log.info(
            "Document generation complete: type=%s filled=%s blank=%s warnings=%s unresolved=%s doc_id=%s",
            args.doc_type,
            placeholder_stats["filled"],
            placeholder_stats["blank"],
            len(all_warnings),
            len(unresolved_tokens),
            generated_doc_id or "dry-run",
        )
        if generated_doc_link:
            log.info("Generated document link: %s", generated_doc_link)

        return 1 if all_warnings else 0

    except DocumentGenerationError as exc:
        log.error(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
