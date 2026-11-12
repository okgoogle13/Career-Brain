#!/usr/bin/env python3
"""
curate_narratives.py — Career Brain Pipeline: Narrative Curation Pass
======================================================================
Scores all narratives in ksc_and_narratives.json on 5 axes:
  1. Length (word count)
  2. STAR completeness (keyword coverage)
  3. Metric presence (quantified outcomes)
  4. Near-duplicate detection (Jaccard similarity ≥85%)
  5. Voice authenticity (LLM-based, optional — requires GEMINI_API_KEY)

Adds quality_tier (1/2/3), quality_flags, quality_score, voice_score,
and vetted fields to each narrative.

Flags:
  --full-voice-score    Run LLM voice scoring on every narrative (slow/costly).
                        Default: score only narratives near the Tier 1/2 boundary
                        (quality_score 5–8) to maximise signal per API call.

Outputs:
  database/ksc_curated.json          — All narratives with quality scores
  database/ksc_curated_tier1.json    — Tier 1 only (for Gem upload — precision over volume)
  database/narrative_curation_report.md
"""

import re
import json
import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from collections import Counter
from typing import Optional

BASE    = Path(__file__).parent.parent  # project root
OUTPUT  = BASE / "database"
SOURCE  = OUTPUT / "ksc_and_narratives.json"
CURATED = OUTPUT / "ksc_curated.json"
TIER1   = OUTPUT / "ksc_curated_tier1.json"
REPORT  = OUTPUT / "narrative_curation_report.md"
CURATION_CONFIG = BASE / "config" / "narrative_curation.json"
SHARING_POLICY  = BASE / "config" / "ai_sharing_policy.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("curate_narratives")

# ─── Scoring Constants ────────────────────────────────────────────────────────

STAR_KEYWORDS = {
    "situation": ["situation", "context", "background", "when", "while working"],
    "task":      ["task", "responsible", "required", "needed to", "my role was"],
    "action":    ["action", "i ", "i've", "implemented", "developed", "led", "coordinated",
                  "facilitated", "worked", "engaged", "established", "delivered"],
    "result":    ["result", "outcome", "achieved", "led to", "resulted in", "ensured",
                  "successfully", "improved", "increased", "reduced", "enabled"],
}

METRIC_PATTERN = re.compile(
    r"(\b\d+[\d,]*\.?\d*\s*(?:%|percent|clients?|people|cases?|hours?|\$|AUD|k\b|thousand|million)|"
    r"\$[\d,]+|"
    r"\bteam\s+of\s+\d+|"
    r"\b\d+[\s-]*(?:member|person|staff)s?\b|"
    r"\b\d+[\s-]*(?:year|month|week|day)s?\b)",
    re.IGNORECASE
)

# Voice authenticity LLM scoring (BS-7.1)
# Boundary-case range: narratives with quality_score in this range get voice-scored
# in the default (non-full) mode to catch promotable Tier-2 narratives.
_VOICE_SCORE_BOUNDARY_RANGE = (5, 8)  # inclusive

_VOICE_SCORE_SYSTEM = """\
You are a voice-authenticity judge for a career-services knowledge base.
Your ONLY job is to score one narrative on five authentic voice patterns.
Return ONLY a JSON object with this exact schema (no markdown, no explanation):
{
  "score": <integer 0-5>,
  "patterns_hit": [<list of pattern IDs from below that were clearly present>],
  "reason": "<one sentence>"
}

Pattern IDs and criteria:
P1 named_service_chain
   The narrative names a specific service, team, hospital, or organisation it
   escalated/referred to AND states what happened next (not generic "appropriate
   supports").
P2 lived_experience_as_method
   Lived experience is used as a deliberate clinical/practice decision and
   leads to a service design or outcome — not merely asserted as a credential.
P3 honest_self_assessment
   The narrative admits a limitation, mistake, or area of growth AND closes
   the loop on what changed in practice afterwards.
P4 corporate_mechanics_transfer
   A named artefact, mechanism, or named stakeholder from a corporate context
   is shown to transfer concretely — not described as abstract "skills".
P5 pivot_with_thesis
   The career change is stated once with an actual position or thesis the reader
   can agree or disagree with — not a cliche or repeated in every paragraph.

Score = number of patterns clearly present (0–5).
"""

# ─── LLM helper ───────────────────────────────────────────────────────────────

def _call_gemini_voice(text: str) -> Optional[dict]:
    """Call Gemini Flash to score voice authenticity. Returns parsed JSON dict or None."""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        from google import genai  # noqa: PLC0415
        from google.genai import types  # noqa: PLC0415
    except ImportError:
        log.warning("google-genai not installed — skipping voice scoring")
        return None
    try:
        client = genai.Client(api_key=api_key)
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Score this narrative:\n\n{text[:1500]}",
            config=types.GenerateContentConfig(
                system_instruction=_VOICE_SCORE_SYSTEM,
                max_output_tokens=200,
                temperature=0.1,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
                response_mime_type="application/json",
            ),
        )
        return json.loads(resp.text.strip())
    except Exception as exc:
        log.warning("Voice LLM call failed: %s", exc)
        return None


# ─── Voice authenticity scorer ─────────────────────────────────────────────────

def score_voice_authenticity(narrative: dict) -> tuple[int, list[str], Optional[str]]:
    """
    Score a narrative on voice authenticity via Gemini LLM.
    Returns (voice_score 0-5, patterns_hit[], reason).
    Returns (0, [], None) when GEMINI_API_KEY is unset or call fails.
    """
    text = narrative.get("full_text", "")
    if not text.strip():
        return 0, [], None
    result = _call_gemini_voice(text)
    if result is None:
        return 0, [], None
    score = int(result.get("score", 0))
    patterns = result.get("patterns_hit", [])
    reason = result.get("reason", "")
    return score, patterns, reason


# ─── Jaccard Similarity ───────────────────────────────────────────────────────

def jaccard(text_a: str, text_b: str, n: int = 4) -> float:
    """N-gram Jaccard similarity between two texts."""
    def ngrams(text, n):
        words = re.findall(r"\w+", text.lower())
        return set(zip(*[words[i:] for i in range(n)])) if len(words) >= n else set(words)
    a, b = ngrams(text_a, n), ngrams(text_b, n)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

# ─── Scoring ──────────────────────────────────────────────────────────────────

def score_narrative(narrative: dict) -> tuple[int, list[str], int]:
    """
    Score a narrative on axes 1-3. Returns (tier, quality_flags, score).
    Tier 1 = strongest, Tier 3 = weakest.
    Voice scoring (axis 5) is applied separately in main() via score_voice_authenticity().
    """
    text       = narrative.get("full_text", "")
    word_count = len(text.split())
    flags      = []
    score      = 0  # 0–10 scale

    # ── Axis 1: Length ──────────────────────────────────────────────────────
    if word_count >= 80:
        score += 3
    elif word_count >= 40:
        score += 1
    else:
        flags.append("too_short")

    # ── Axis 2: STAR completeness ──────────────────────────────────────────
    text_lower = text.lower()
    star_hits  = 0
    for component, signals in STAR_KEYWORDS.items():
        if any(s in text_lower for s in signals):
            star_hits += 1

    if star_hits >= 3:
        score += 4
    elif star_hits == 2:
        score += 2
    elif star_hits <= 1:
        flags.append("incomplete_star")

    # ── Axis 3: Metric presence ────────────────────────────────────────────
    if METRIC_PATTERN.search(text):
        score += 3
    else:
        flags.append("no_metric")

    # ── Tier assignment ────────────────────────────────────────────────────
    if score >= 7:
        tier = 1
    elif score >= 3:
        tier = 2
    else:
        tier = 3

    return tier, flags, score


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Career Brain Narrative Curation Pass (5-axis scoring)",
    )
    parser.add_argument(
        "--full-voice-score",
        action="store_true",
        help="Run LLM voice scoring on ALL narratives (slow/costly). Default: boundary cases only.",
    )
    args = parser.parse_args()

    log.info("=" * 60)
    log.info("CAREER BRAIN — NARRATIVE CURATION PASS")
    log.info(f"Started: {datetime.now().isoformat()}")
    log.info("=" * 60)

    if not SOURCE.exists():
        log.error(f"Source not found: {SOURCE}")
        sys.exit(1)

    with open(SOURCE, encoding="utf-8") as f:
        data = json.load(f)

    narratives = data.get("narratives", [])
    log.info(f"  Processing {len(narratives)} narratives...")

    # ── Pass 0: Own-source filter, contact redaction, lived-experience flag ──
    cfg = json.loads(CURATION_CONFIG.read_text(encoding="utf-8"))
    placeholder = json.loads(SHARING_POLICY.read_text(encoding="utf-8"))["redaction"]["placeholder"]
    own_re     = re.compile("|".join(cfg["own_source_patterns"]), re.IGNORECASE)
    contact_re = re.compile("|".join(cfg["contact_patterns"]), re.IGNORECASE)
    letter_re  = re.compile("|".join(cfg["letter_markers"]), re.IGNORECASE)

    own = [n for n in narratives if own_re.search(n.get("source_lineage", ""))]
    log.info(f"  Dropped {len(narratives) - len(own)} narratives from non-own (reference/example) sources")
    narratives = own

    redacted_count = 0
    for n in narratives:
        n["full_text"], hits = contact_re.subn(placeholder, n.get("full_text", ""))
        if hits:
            redacted_count += 1
        n["is_lived_experience"] = "lived_experience" in n.get("competency_tags", [])
    log.info(f"  Redacted contact details in {redacted_count} narratives")

    # ── Pass 1: Score all narratives ─────────────────────────────────────────
    tier_counts  = Counter()
    flag_counts  = Counter()
    scored       = []

    for n in narratives:
        tier, flags, score = score_narrative(n)
        if placeholder in n.get("full_text", ""):
            flags.append("contact_redacted")
        if letter_re.search(n.get("full_text", "")):
            flags.append("full_letter")
            tier = max(tier, 2)
        if len(n.get("full_text", "").split()) > cfg["tier1_max_words"]:
            flags.append("too_long")
            tier = max(tier, 2)
        n["quality_tier"]  = tier
        n["quality_flags"] = flags
        n["quality_score"] = score
        n["vetted"]        = False
        scored.append(n)
        tier_counts[tier] += 1
        for f in flags:
            flag_counts[f] += 1

    # ── Pass 2: Near-duplicate detection (Jaccard) ────────────────────────────
    log.info("  Running near-duplicate detection...")
    dup_count  = 0
    # Only check within same narrative_type × competency_tag combos for efficiency
    buckets: dict[str, list] = {}
    for n in scored:
        key = n.get("narrative_type", "")
        buckets.setdefault(key, []).append(n)

    seen_dup_pairs = set()
    for bucket_key, bucket in buckets.items():
        for i, n_a in enumerate(bucket):
            for j, n_b in enumerate(bucket):
                if i >= j:
                    continue
                pair_key = (id(n_a), id(n_b))
                if pair_key in seen_dup_pairs:
                    continue
                seen_dup_pairs.add(pair_key)
                sim = jaccard(n_a["full_text"], n_b["full_text"])
                if sim >= 0.85:
                    # Mark the lower-scoring one as duplicate
                    loser = n_a if n_a["quality_score"] <= n_b["quality_score"] else n_b
                    if "near_duplicate" not in loser["quality_flags"]:
                        loser["quality_flags"].append("near_duplicate")
                        old_tier = loser["quality_tier"]
                        loser["quality_tier"] = max(old_tier, 2)  # bump down at least to T2
                        tier_counts[old_tier] -= 1
                        tier_counts[loser["quality_tier"]] += 1
                        dup_count += 1

    log.info(f"  Near-duplicates detected: {dup_count}")

    # ── Pass 3: Voice authenticity scoring (Axis 5, LLM, optional) ──────────────
    has_gemini = bool(os.environ.get("GEMINI_API_KEY"))
    voice_scored_count = 0
    voice_score_mode = "none"

    if has_gemini:
        lo, hi = _VOICE_SCORE_BOUNDARY_RANGE
        to_voice_score = [
            n for n in scored
            if args.full_voice_score or (lo <= n["quality_score"] <= hi)
        ]
        voice_score_mode = "full" if args.full_voice_score else f"boundary ({lo}–{hi})"
        log.info(f"  Running voice scoring on {len(to_voice_score)} narratives (mode: {voice_score_mode})...")

        for n in to_voice_score:
            v_score, v_patterns, v_reason = score_voice_authenticity(n)
            n["voice_score"] = v_score
            n["voice_patterns"] = v_patterns
            if v_reason:
                n["voice_reason"] = v_reason
            if v_reason is not None:
                voice_scored_count += 1
            # Re-tier upward if voice score is strong (≥3 patterns) and narrative
            # is on the T1/T2 boundary
            if v_score >= 3 and n["quality_tier"] == 2:
                n["quality_tier"] = 1
                n["quality_flags"].append("voice_promoted")
                tier_counts[2] -= 1
                tier_counts[1] += 1
        log.info(f"  Voice-scored: {voice_scored_count}")
    else:
        log.info("  GEMINI_API_KEY not set — voice scoring skipped (run with op run or set key)")

    # ── Summary ───────────────────────────────────────────────────────────────
    log.info(f"\n{'─'*60}")
    log.info("CURATION SUMMARY")
    log.info(f"{'─'*60}")
    for tier in [1, 2, 3]:
        log.info(f"  Tier {tier}: {tier_counts[tier]} narratives")
    log.info(f"  Near-duplicates flagged: {dup_count}")
    for flag, count in flag_counts.most_common():
        log.info(f"  Flag [{flag}]: {count}")
    log.info(f"{'─'*60}")

    # ── Write full curated JSON ───────────────────────────────────────────────
    data["narratives"] = scored
    data["curation_meta"] = {
        "run_at": datetime.now().isoformat(),
        "total": len(scored),
        "tier_1": tier_counts[1],
        "tier_2": tier_counts[2],
        "tier_3": tier_counts[3],
        "near_duplicates_flagged": dup_count,
        "voice_score_mode": voice_score_mode,
        "voice_scored_count": voice_scored_count,
    }
    with open(CURATED, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    log.info(f"\n  ✅ Saved: {CURATED.name}  ({CURATED.stat().st_size // 1024} KB)")

    # ── Write Tier 1 only JSON ────────────────────────────────────────────────
    tier1_narratives = [n for n in scored if n["quality_tier"] == 1]
    tier1_data = {
        "generated_at":     data.get("generated_at"),
        "curation_meta":    data["curation_meta"],
        "total_narratives": len(tier1_narratives),
        "narratives":       tier1_narratives,
    }
    with open(TIER1, "w", encoding="utf-8") as f:
        json.dump(tier1_data, f, indent=2, ensure_ascii=False)
    log.info(f"  ✅ Saved: {TIER1.name}  ({TIER1.stat().st_size // 1024} KB)  ← recommended for Gem")

    # ── Write Markdown Report ─────────────────────────────────────────────────
    # Competency coverage breakdown for Tier 1
    t1_competency: Counter = Counter()
    for n in tier1_narratives:
        for tag in n.get("competency_tags", []):
            t1_competency[tag] += 1

    # Narrative type breakdown
    type_counts: Counter = Counter(n.get("narrative_type") for n in scored)
    t1_type_counts: Counter = Counter(n.get("narrative_type") for n in tier1_narratives)

    lines = [
        "# Career Brain — Narrative Curation Report",
        "",
        f"Generated: {datetime.now().isoformat()}",
        "",
        "## Tier Distribution",
        "",
        "| Tier | Description | Count | % |",
        "|---|---|---|---|",
        f"| **Tier 1** | High-signal STAR/metric narratives | {tier_counts[1]} | {tier_counts[1]*100//len(scored)}% |",
        f"| **Tier 2** | Moderate — good content, missing one axis | {tier_counts[2]} | {tier_counts[2]*100//len(scored)}% |",
        f"| **Tier 3** | Low-signal — too short or header-only | {tier_counts[3]} | {tier_counts[3]*100//len(scored)}% |",
        f"| **Near-Duplicates** | Flagged within tier | {dup_count} | {dup_count*100//len(scored)}% |",
        "",
        "## Quality Flags (All Tiers)",
        "",
        "| Flag | Count |",
        "|---|---|",
        *[f"| `{flag}` | {count} |" for flag, count in flag_counts.most_common()],
        "",
        "## Narrative Type Breakdown",
        "",
        "| Type | Total | Tier 1 |",
        "|---|---|---|",
        *[f"| {t} | {type_counts[t]} | {t1_type_counts.get(t, 0)} |" for t in sorted(type_counts)],
        "",
        "## Tier 1 Competency Coverage",
        "",
        "| Competency | Tier 1 Narratives |",
        "|---|---|",
        *[f"| {comp} | {count} |" for comp, count in t1_competency.most_common()],
        "",
        "## Gem Recommendation",
        "",
        f"> [!TIP]",
        f"> **Use `ksc_curated_tier1.json`** ({TIER1.stat().st_size // 1024} KB) as your Gem knowledge file.",
        f"> It contains {tier_counts[1]} high-signal narratives vs the full 1,126 — dramatically better RAG precision.",
        "",
        "---",
        "",
        f"Files generated:",
        f"- `{CURATED.name}` — full scored dataset",
        f"- `{TIER1.name}` — Tier 1 only (recommended for Gem)",
    ]

    REPORT.write_text("\n".join(lines), encoding="utf-8")
    log.info(f"  ✅ Saved: {REPORT.name}")
    log.info("\nNarrative curation pass complete.")


if __name__ == "__main__":
    main()
