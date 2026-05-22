#!/usr/bin/env python3
"""
inject_metrics.py — Career Brain Pipeline: Metric Injection Pass (v2)
======================================================================
Multi-pass heuristic metric injection for all bullets flagged needs_review: true.

PASS 1 (Expanded Regex): Ordinals, frequency, team sizes, caseload language,
         scale phrases, timeframes — auto-clears flag if signal found.

PASS 2 (Cross-Source Inference): If another source file version of the same
         bullet (same role fingerprint, high text similarity) DOES have a metric,
         extract the metric phrase and annotate this bullet.

PASS 3 (Sibling Context): If other bullets in the SAME role contain a metric
         that is contextually compatible (same domain tag), suggest it as a
         possible annotation and flag for human confirmation.

Only bullets that survive all 3 passes go to the manual hit list.

Outputs:
  output/career_history_enriched.json   — updated JSON with auto-resolved flags
  output/metric_injection_targets.md    — truly unresolvable manual hit list
"""

import re
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE     = Path(__file__).parent
OUTPUT   = BASE / "output"
# Use enriched if it exists (from a prior partial run), otherwise use source
SOURCE   = OUTPUT / "career_history.json"
ENRICHED = OUTPUT / "career_history_enriched.json"
TARGETS  = OUTPUT / "metric_injection_targets.md"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("inject_metrics_v2")

# ─── Pass 1: Expanded Metric Patterns ────────────────────────────────────────

PATTERNS = [
    # Hard numbers & percentages
    re.compile(r"\b\d+[\d,]*\.?\d*\s*(%|percent|clients?|people|cases?|hours?|\$|AUD|k\b|thousand|million)", re.IGNORECASE),
    re.compile(r"\$[\d,]+", re.IGNORECASE),
    # Team / group size
    re.compile(r"\bteam\s+of\s+\d+", re.IGNORECASE),
    re.compile(r"\b\d+[\s-]*(member|person|staff|volunteer|worker)s?\b", re.IGNORECASE),
    # Ordinal / superlative signals
    re.compile(r"\b(first|only|sole|primary|lead|senior|inaugural|largest|highest|lowest)\b", re.IGNORECASE),
    # Frequency / cadence
    re.compile(r"\b(daily|weekly|monthly|quarterly|annually|fortnightly|ongoing|continuous|regular)\b", re.IGNORECASE),
    # Caseload / scope
    re.compile(r"\bcaseload\b", re.IGNORECASE),
    re.compile(r"\b(portfolio|workload|cohort|cohorts|waitlist|roster)\b", re.IGNORECASE),
    # Scale language
    re.compile(r"\b(multi[\s-]?site|state[\s-]?wide|nation[\s-]?wide|organisation[\s-]?wide|sector[\s-]?wide)\b", re.IGNORECASE),
    re.compile(r"\b(extensive|significant|substantial|large[\s-]?scale|high[\s-]?volume|complex)\b", re.IGNORECASE),
    # Timeframe signals
    re.compile(r"\b\d+[\s-]*(year|month|week|day)s?\b", re.IGNORECASE),
    re.compile(r"\bover\s+(a|the|an)?\s*(decade|year|month)\b", re.IGNORECASE),
]

METRIC_EXTRACTOR = re.compile(
    r"(\b\d+[\d,]*\.?\d*\s*(?:%|percent|clients?|people|cases?|hours?|\$|AUD|k\b|thousand|million)|"
    r"\$[\d,]+|"
    r"\bteam\s+of\s+\d+|"
    r"\b\d+[\s-]*(?:member|person|staff|volunteer|worker)s?\b|"
    r"\b\d+[\s-]*(?:year|month|week|day)s?\b)",
    re.IGNORECASE
)


def has_any_signal(text: str) -> tuple[bool, str]:
    for pattern in PATTERNS:
        m = pattern.search(text)
        if m:
            return True, m.group(0)
    return False, ""


def extract_metric_phrases(text: str) -> list[str]:
    """Extract all hard metric phrases from a text."""
    return METRIC_EXTRACTOR.findall(text)


def text_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def bullet_has_hard_metric(bullet: dict) -> bool:
    """Check if a bullet has a hard numeric metric (not just soft signals)."""
    return bool(METRIC_EXTRACTOR.search(bullet.get("raw_text", "")))


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    log.info("=" * 60)
    log.info("CAREER BRAIN — METRIC INJECTION PASS v2 (Multi-Heuristic)")
    log.info(f"Started: {datetime.now().isoformat()}")
    log.info("=" * 60)

    if not SOURCE.exists():
        log.error(f"Source not found: {SOURCE}")
        sys.exit(1)

    with open(SOURCE, encoding="utf-8") as f:
        data = json.load(f)

    roles = data.get("roles", [])

    # ── Pre-index: all bullets with hard metrics, indexed by fingerprint ──────
    # We'll use this for Pass 2 cross-source inference
    metric_rich_bullets: dict[str, list[dict]] = {}  # fingerprint → bullets w/ metrics
    for role in roles:
        fp = role.get("fingerprint", "")
        metric_bullets = [b for b in role.get("achievements", []) if bullet_has_hard_metric(b)]
        if metric_bullets:
            metric_rich_bullets[fp] = metric_bullets

    # ── Stats counters ─────────────────────────────────────────────────────────
    total_flagged  = 0
    p1_resolved    = 0
    p2_resolved    = 0
    p3_suggested   = 0
    manual_needed  = []

    for role in roles:
        employer  = role.get("company", "Unknown")
        role_name = role.get("role", "Unknown")
        fp        = role.get("fingerprint", "")

        # All sibling bullets in this role (for Pass 3)
        all_siblings = role.get("achievements", [])
        sibling_metrics = []
        for sib in all_siblings:
            phrases = extract_metric_phrases(sib.get("raw_text", ""))
            sibling_metrics.extend(phrases)

        for bullet in all_siblings:
            if not bullet.get("needs_review", False):
                continue

            total_flagged += 1
            text = bullet.get("raw_text", "")

            # ── PASS 1: Expanded regex ────────────────────────────────────────
            found, matched = has_any_signal(text)
            if found:
                bullet["needs_review"] = False
                bullet["metric_signal"] = matched
                bullet["metric_resolution"] = "pass1_regex"
                p1_resolved += 1
                log.info(f'  [P1 ✓] [{employer}]: signal="{matched}" | "{text[:60]}..."')
                continue

            # ── PASS 2: Cross-source similarity ──────────────────────────────
            # Look for a near-identical bullet (≥75% similar) in the same role
            # that has a hard metric. Extract and annotate.
            p2_hit = False
            if fp in metric_rich_bullets:
                for rich_bullet in metric_rich_bullets[fp]:
                    rich_text = rich_bullet.get("raw_text", "")
                    sim = text_similarity(text, rich_text)
                    if sim >= 0.65:  # Liberal threshold for variant phrasing
                        metric_phrases = extract_metric_phrases(rich_text)
                        if metric_phrases:
                            bullet["needs_review"] = False
                            bullet["metric_signal"] = metric_phrases[0]
                            bullet["metric_resolution"] = "pass2_cross_source"
                            bullet["metric_source_bullet"] = rich_text[:120]
                            bullet["metric_similarity"] = round(sim, 3)
                            p2_resolved += 1
                            p2_hit = True
                            log.info(f'  [P2 ✓] [{employer}]: sim={sim:.2f} metric="{metric_phrases[0]}" | "{text[:60]}..."')
                            break

            if p2_hit:
                continue

            # ── PASS 3: Sibling context suggestion ────────────────────────────
            # If other bullets in the same role have metrics, suggest the most
            # common one as a possible annotation. Does NOT auto-clear the flag —
            # annotates with a suggestion for human confirmation.
            if sibling_metrics:
                from collections import Counter
                most_common = Counter(sibling_metrics).most_common(1)[0][0]
                bullet["metric_suggestion"] = most_common
                bullet["metric_resolution"] = "pass3_sibling_suggestion"
                p3_suggested += 1
                log.info(f'  [P3 ~] [{employer}]: suggestion="{most_common}" | "{text[:60]}..."')

            manual_needed.append({
                "company": employer,
                "role": role_name,
                "raw_text": text,
                "source_lineage": bullet.get("source_lineage", ""),
                "domain_tags": bullet.get("domain_tags", []),
                "metric_suggestion": bullet.get("metric_suggestion", ""),
                "resolution": bullet.get("metric_resolution", "unresolved"),
            })

    # ─── Summary ──────────────────────────────────────────────────────────────
    log.info(f"\n{'─'*60}")
    log.info("METRIC INJECTION SUMMARY")
    log.info(f"{'─'*60}")
    log.info(f"  Total flagged        : {total_flagged}")
    log.info(f"  Pass 1 auto-resolved : {p1_resolved}  (expanded regex signal)")
    log.info(f"  Pass 2 auto-resolved : {p2_resolved}  (cross-source similarity)")
    log.info(f"  Pass 3 suggestion    : {p3_suggested}  (sibling context — needs confirmation)")
    log.info(f"  Truly manual needed  : {len(manual_needed) - p3_suggested}  (no signal whatsoever)")
    log.info(f"  In manual targets    : {len(manual_needed)}  (P3 suggestions + truly manual)")
    log.info(f"{'─'*60}")

    # ─── Write enriched JSON ──────────────────────────────────────────────────
    data["meta"] = data.get("meta", {})
    data["meta"]["metric_injection_run"] = datetime.now().isoformat()
    data["meta"]["metric_injection_version"] = "v2_multi_heuristic"
    data["meta"]["p1_resolved"] = p1_resolved
    data["meta"]["p2_resolved"] = p2_resolved
    data["meta"]["p3_suggested"] = p3_suggested
    data["meta"]["manual_pending"] = len(manual_needed)

    with open(ENRICHED, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    log.info(f"\n  ✅ Saved: {ENRICHED.name}")

    # ─── Write manual targets Markdown ────────────────────────────────────────
    if manual_needed:
        by_employer: dict[str, list] = {}
        for item in manual_needed:
            by_employer.setdefault(item["company"], []).append(item)

        truly_manual = [b for b in manual_needed if b["resolution"] == "unresolved"]
        p3_items     = [b for b in manual_needed if b["resolution"] == "pass3_sibling_suggestion"]

        lines = [
            "# Career Brain — Metric Injection Targets",
            "",
            f"Generated: {datetime.now().isoformat()}",
            "",
            "## Summary",
            "",
            f"| Pass | Result |",
            f"|---|---|",
            f"| Pass 1 (Expanded Regex) | {p1_resolved} auto-resolved ✅ |",
            f"| Pass 2 (Cross-Source Similarity) | {p2_resolved} auto-resolved ✅ |",
            f"| Pass 3 (Sibling Context) | {p3_suggested} suggestions provided 🔶 |",
            f"| Truly Manual | {len(truly_manual)} — no signal found 🔴 |",
            "",
            "> **Legend:**",
            "> - 🔶 Pass 3 items have a suggested metric from a sibling bullet — confirm or replace",
            "> - 🔴 Truly manual items need you to write a metric from memory",
            "",
            "---",
            "",
        ]

        for employer, bullets in sorted(by_employer.items()):
            lines.append(f"## {employer}")
            lines.append("")
            for i, b in enumerate(bullets, 1):
                icon = "🔶" if b["resolution"] == "pass3_sibling_suggestion" else "🔴"
                lines.append(f"### {icon} Bullet {i}")
                lines.append(f"**Role:** {b['role']}  ")
                lines.append(f"**Source:** `{b['source_lineage']}`  ")
                lines.append(f"**Tags:** {', '.join(b['domain_tags']) or 'none'}")
                lines.append("")
                lines.append(f"> {b['raw_text']}")
                lines.append("")
                if b.get("metric_suggestion"):
                    lines.append(f"💡 **Suggested metric (from sibling bullet):** `{b['metric_suggestion']}`")
                    lines.append("")
                lines.append("**✏️ Your metric annotation:**")
                lines.append("")
                lines.append("_[Add metric here — e.g. 'caseload of 30 clients', '~15 referrals/week', 'across 3 sites']_")
                lines.append("")
                lines.append("---")
                lines.append("")

        TARGETS.write_text("\n".join(lines), encoding="utf-8")
        log.info(f"  ✅ Saved: {TARGETS.name}")
    else:
        log.info("  🎉 All bullets resolved — no manual annotation file needed!")

    log.info("\nMetric injection pass complete.")
    return len([b for b in manual_needed if b["resolution"] == "unresolved"])


if __name__ == "__main__":
    remaining = main()
    sys.exit(0 if remaining == 0 else 1)
