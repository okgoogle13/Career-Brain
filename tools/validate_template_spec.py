#!/usr/bin/env python3
"""
validate_template_spec.py — Hard-gate validator for KSC template specs.

Usage:
    python3 validate_template_spec.py <spec_file.md>

Exit 0: spec passes all checks — safe to register in doc_templates.json.
Exit 1: one or more failures — each printed as:
        FAIL rule<N> <file>:<line>: <description>
Exit 2: usage error or missing input file.
"""

import json
import re
import sys
from pathlib import Path

# ── paths ─────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent.parent  # project root
ATS_RULES_PATH = SCRIPT_DIR / "config" / "ats_rules.json"
GENERATE_DOC_PATH = SCRIPT_DIR / "tools" / "generate_document.py"

REQUIRED_SECTIONS = ["META", "TOKENS_USED", "STRUCTURE", "ATS_AUDIT",
                     "REGISTRATION_FRAGMENT", "DRY_RUN_CMD"]

PLACEHOLDER_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
CITATION_RE = re.compile(r"generate_document\.py:(\d+)(?:-(\d+))?$")
BOX_DRAWING_RE = re.compile(r"[┌┐└┘├┤┬┴┼─│╔╗╚╝╠╣╦╩╬═║]")
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF☀-➿✂-➰]")

# KSC token set — mirrors PLACEHOLDER_SCHEMA_V2["ksc"] in generate_document.py:118-133
# Constants sourced from content_engine.py:65-66
_MAX_CRITERIA = 6
_MAX_BULLETS = 2
KSC_V2_TOKENS: frozenset[str] = frozenset({
    "CONTACT_NAME", "CONTACT_PHONE", "CONTACT_EMAIL", "CONTACT_LOCATION",
    "TARGET_ROLE", "EMPLOYER_ORG",
    *(f"KSC_CRITERION_{c}_TEXT" for c in range(1, _MAX_CRITERIA + 1)),
    *(f"KSC_{c}_CONTEXT" for c in range(1, _MAX_CRITERIA + 1)),
    *(f"KSC_{c}_ACTION" for c in range(1, _MAX_CRITERIA + 1)),
    *(f"KSC_{c}_RESULT" for c in range(1, _MAX_CRITERIA + 1)),
    *(
        f"KSC_{c}_SUPPORT_BULLET_{b}"
        for c in range(1, _MAX_CRITERIA + 1)
        for b in range(1, _MAX_BULLETS + 1)
    ),
})

Failure = tuple[str, str, int]  # (rule_id, description, line_number)


# ── section parser ────────────────────────────────────────────────────────

def parse_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current: str | None = None
    lines: list[str] = []
    for raw in text.splitlines():
        m = re.match(r"^##\s+(\w+)\s*$", raw)
        if m:
            if current is not None:
                sections[current] = "\n".join(lines).strip()
            current = m.group(1)
            lines = []
        elif current is not None:
            lines.append(raw)
    if current is not None:
        sections[current] = "\n".join(lines).strip()
    return sections


def parse_meta(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            result[key.strip()] = val.strip()
    return result


def extract_tokens_from_section(text: str) -> set[str]:
    return set(PLACEHOLDER_RE.findall(text))


def extract_citations(tokens_used: str) -> dict[str, str]:
    citations: dict[str, str] = {}
    for line in tokens_used.splitlines():
        line = line.strip()
        if not line or line.startswith("<"):
            continue
        m = re.match(r"([A-Z0-9_]+)\s*→\s*(.+)$", line)
        if m:
            citations[m.group(1)] = m.group(2).strip()
    return citations


def extract_json_block(text: str) -> str | None:
    m = re.search(r"```json\s*\n(.+?)```", text, re.DOTALL)
    return m.group(1).strip() if m else None


def parse_ats_audit(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        m = re.match(r"([a-z_]+):\s*(PASS|FAIL)\s*[—\-]", line.strip())
        if m:
            result[m.group(1)] = m.group(2)
    return result


# ── rule checks ───────────────────────────────────────────────────────────

def r1_form_shape(spec_text: str, sections: dict) -> list[Failure]:
    """All required sections present; no box-drawing or emoji anywhere."""
    failures: list[Failure] = []
    for req in REQUIRED_SECTIONS:
        if req not in sections:
            failures.append(("rule1", f"Missing required section: ## {req}", 0))
    for i, line in enumerate(spec_text.splitlines(), 1):
        if BOX_DRAWING_RE.search(line):
            failures.append(("rule1", "Box-drawing character in spec", i))
            break
        if EMOJI_RE.search(line):
            failures.append(("rule1", "Emoji character in spec", i))
            break
    return failures


def r2_token_validity(sections: dict) -> list[Failure]:
    """Every TOKENS_USED citation names a real KSC v2 token, with valid citation format."""
    if "TOKENS_USED" not in sections:
        return []
    failures: list[Failure] = []
    citations = extract_citations(sections["TOKENS_USED"])
    try:
        gen_line_count = len(GENERATE_DOC_PATH.read_text().splitlines())
    except OSError:
        gen_line_count = None

    for token, citation in citations.items():
        if token not in KSC_V2_TOKENS:
            failures.append(("rule2", f"Unknown token {{{{{token}}}}} — not in KSC PLACEHOLDER_SCHEMA_V2 (generate_document.py:118-133)", 0))
            continue
        cm = CITATION_RE.search(citation)
        if not cm:
            failures.append(("rule2", f"{{{{{token}}}}}: citation '{citation}' must match 'generate_document.py:LINE' or 'generate_document.py:LINE-LINE'", 0))
        elif gen_line_count is not None:
            line_no = int(cm.group(1))
            if line_no > gen_line_count:
                failures.append(("rule2", f"{{{{{token}}}}}: cited line {line_no} exceeds generate_document.py length ({gen_line_count} lines)", 0))
    return failures


def r3_no_fabricated_tokens(sections: dict) -> list[Failure]:
    """Token sets in STRUCTURE and TOKENS_USED must match exactly."""
    if "TOKENS_USED" not in sections or "STRUCTURE" not in sections:
        return []
    cited = set(extract_citations(sections["TOKENS_USED"]).keys())
    used = extract_tokens_from_section(sections["STRUCTURE"])
    failures: list[Failure] = []
    for t in used - cited:
        failures.append(("rule3", f"{{{{{t}}}}} used in STRUCTURE but not cited in TOKENS_USED", 0))
    for t in cited - used:
        failures.append(("rule3", f"{{{{{t}}}}} cited in TOKENS_USED but absent from STRUCTURE", 0))
    return failures


def r4_forbidden_glyphs(spec_text: str, ats_rules: dict) -> list[Failure]:
    """No characters from ats_rules.json vocabulary.forbidden_characters appear in spec."""
    forbidden = ats_rules.get("vocabulary", {}).get("forbidden_characters", [])
    failures: list[Failure] = []
    for i, line in enumerate(spec_text.splitlines(), 1):
        for ch in forbidden:
            if ch in line:
                failures.append(("rule4", f"Forbidden character '{ch}' (ats_rules.json forbidden_characters)", i))
    return failures


def r5_heading_whitelist(sections: dict, ats_rules: dict) -> list[Failure]:
    """Static [Heading N] text must be in ats_rules.json allowed_headings; placeholder headings are exempt."""
    if "STRUCTURE" not in sections:
        return []
    allowed = set(ats_rules.get("structure", {}).get("allowed_headings", []))
    failures: list[Failure] = []
    for i, line in enumerate(sections["STRUCTURE"].splitlines(), 1):
        m = re.match(r"\d+\.\s+\[Heading [12]\]\s+(.+)$", line)
        if not m:
            continue
        heading_text = m.group(1).strip()
        if PLACEHOLDER_RE.fullmatch(heading_text):
            continue  # criterion-text placeholder — exempt
        if heading_text not in allowed:
            failures.append(("rule5", f"Static heading '{heading_text}' not in ats_rules.json allowed_headings {sorted(allowed)}", i))
    return failures


def r6_au_terminology(sections: dict, ats_rules: dict) -> list[Failure]:
    """No US/UK terminology in static text of STRUCTURE."""
    if "STRUCTURE" not in sections:
        return []
    mappings: dict[str, str] = ats_rules.get("terminology", {}).get("australian_mappings", {})
    failures: list[Failure] = []
    for i, line in enumerate(sections["STRUCTURE"].splitlines(), 1):
        static = PLACEHOLDER_RE.sub("", line).lower()
        for forbidden_term, au_term in mappings.items():
            if forbidden_term in static:
                failures.append(("rule6", f"Non-AU term '{forbidden_term}' in static text — use '{au_term}'", i))
    return failures


def r7_audit_honesty(sections: dict, f4: list[Failure], f5: list[Failure], f6: list[Failure]) -> list[Failure]:
    """ATS_AUDIT PASS verdicts must align with independent mechanical checks."""
    if "ATS_AUDIT" not in sections:
        return [("rule7", "ATS_AUDIT section missing — cannot verify honesty", 0)]
    audit = parse_ats_audit(sections["ATS_AUDIT"])
    failures: list[Failure] = []
    required_keys = ("columns_max", "forbidden_chars", "allowed_headings", "au_terminology", "ksc_word_limit_fit")
    for key in required_keys:
        if key not in audit:
            failures.append(("rule7", f"ATS_AUDIT missing required key '{key}'", 0))
    if audit.get("forbidden_chars") == "PASS" and f4:
        failures.append(("rule7", "ATS_AUDIT claims forbidden_chars: PASS but rule4 found forbidden characters", 0))
    if audit.get("allowed_headings") == "PASS" and f5:
        failures.append(("rule7", "ATS_AUDIT claims allowed_headings: PASS but rule5 found heading violations", 0))
    if audit.get("au_terminology") == "PASS" and f6:
        failures.append(("rule7", "ATS_AUDIT claims au_terminology: PASS but rule6 found non-AU terms", 0))
    return failures


def r8_registration_shape(sections: dict, meta: dict) -> list[Failure]:
    """REGISTRATION_FRAGMENT must be valid JSON with correct ksc shape; variant must match META."""
    if "REGISTRATION_FRAGMENT" not in sections:
        return []
    json_block = extract_json_block(sections["REGISTRATION_FRAGMENT"])
    if not json_block:
        return [("rule8", "REGISTRATION_FRAGMENT has no ```json code block", 0)]
    try:
        data = json.loads(json_block)
    except json.JSONDecodeError as e:
        return [("rule8", f"REGISTRATION_FRAGMENT JSON parse error: {e}", 0)]
    failures: list[Failure] = []
    if "ksc" not in data:
        failures.append(("rule8", "Registration fragment missing top-level 'ksc' key", 0))
        return failures
    ksc = data["ksc"]
    if "template_doc_id" in ksc:
        pass  # flat shape — valid
    elif "variants" in ksc:
        variant_name = meta.get("VARIANT", "").strip().strip("<>")
        if variant_name and variant_name not in ksc["variants"]:
            failures.append(("rule8", f"META VARIANT '{variant_name}' not found in registration fragment variants {list(ksc['variants'].keys())}", 0))
    else:
        failures.append(("rule8", "Registration fragment 'ksc' key has neither 'template_doc_id' nor 'variants'", 0))
    return failures


def r9_ksc_structure(sections: dict) -> list[Failure]:
    """Between 1–6 criterion blocks; contiguous from 1; each has CONTEXT/ACTION/RESULT."""
    if "STRUCTURE" not in sections:
        return []
    structure = sections["STRUCTURE"]
    all_tokens = extract_tokens_from_section(structure)
    criteria_found: set[int] = set()
    for token in all_tokens:
        m = re.match(r"KSC_CRITERION_(\d+)_TEXT", token)
        if m:
            criteria_found.add(int(m.group(1)))
    failures: list[Failure] = []
    if not criteria_found:
        failures.append(("rule9", "No KSC_CRITERION_N_TEXT tokens found in STRUCTURE — at least 1 criterion required", 0))
        return failures
    if max(criteria_found) > _MAX_CRITERIA:
        failures.append(("rule9", f"Criterion numbers exceed MAX_KSC_CRITERIA ({_MAX_CRITERIA}): found {sorted(criteria_found)}", 0))
    expected = set(range(1, max(criteria_found) + 1))
    if criteria_found != expected:
        failures.append(("rule9", f"Criterion numbering not contiguous from 1: found {sorted(criteria_found)}, expected {sorted(expected)}", 0))
    for c in sorted(criteria_found):
        for part in ("CONTEXT", "ACTION", "RESULT"):
            token = f"KSC_{c}_{part}"
            if token not in all_tokens:
                failures.append(("rule9", f"Criterion {c} missing token {{{{{token}}}}}", 0))
    return failures


# ── main ─────────────────────────────────────────────────────────────────

def validate(spec_path: Path) -> list[Failure]:
    ats_rules = json.loads(ATS_RULES_PATH.read_text(encoding="utf-8"))
    spec_text = spec_path.read_text(encoding="utf-8")
    sections = parse_sections(spec_text)
    meta = parse_meta(sections.get("META", ""))

    f4 = r4_forbidden_glyphs(spec_text, ats_rules)
    f5 = r5_heading_whitelist(sections, ats_rules)
    f6 = r6_au_terminology(sections, ats_rules)

    return (
        r1_form_shape(spec_text, sections)
        + r2_token_validity(sections)
        + r3_no_fabricated_tokens(sections)
        + f4 + f5 + f6
        + r7_audit_honesty(sections, f4, f5, f6)
        + r8_registration_shape(sections, meta)
        + r9_ksc_structure(sections)
    )


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <spec_file.md>", file=sys.stderr)
        return 2
    spec_path = Path(sys.argv[1])
    if not spec_path.exists():
        print(f"ERROR: not found: {spec_path}", file=sys.stderr)
        return 2
    failures = validate(spec_path)
    if not failures:
        print(f"SPEC OK: {spec_path}")
        return 0
    for rule_id, desc, line_no in failures:
        loc = f"{spec_path}:{line_no}" if line_no else str(spec_path)
        print(f"FAIL {rule_id} {loc}: {desc}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
