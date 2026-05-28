#!/usr/bin/env python3
"""
audit_and_repair_database.py — Career Brain Pipeline: TASK-004
================================================================
Quality audit and repair sweep for career_history_enriched.json
and ksc_curated.json.

Usage:
  python3 pipeline/audit_and_repair_database.py --dry-run
      Sample 10 stratified entries, write database/quality_audit_report_draft.md.
      STOP and review before running --write.

  python3 pipeline/audit_and_repair_database.py --write
      Backup originals → process all entries → write updated files + final report.

  python3 pipeline/audit_and_repair_database.py --write --force
      Re-sweep all items regardless of existing applied_fixes.

  python3 pipeline/audit_and_repair_database.py --write --force --min-score 3
      Re-sweep only items with car_quality_score < 3.
"""

import argparse
import json
import logging
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE     = Path(__file__).parent.parent
DB       = BASE / "database"
ENRICHED = DB / "career_history_enriched.json"
CURATED  = DB / "ksc_curated.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("audit_repair")

# ─── Patterns ─────────────────────────────────────────────────────────────────
_GLYPH_RE = re.compile(r"[•✔★❖●✅❌|]|\*\*")
_METRIC_RE = re.compile(
    r"\b(\d+[\d,]*\.?\d*\s*(%|percent|clients?|people|cases?|hours?|\$|AUD|k\b|thousand|million)"
    r"|\$[\d,]+)",
    re.IGNORECASE,
)
_RESULT_RE = re.compile(
    r"\b(result|outcome|led to|reduced|increased|improved|achieved|delivered|"
    r"saved|raised|generated|impact|benefit|success|enabled|supporting)\b",
    re.IGNORECASE,
)
_LIVED_EXP_RE = re.compile(
    r"\b(queer|neurodivergent|non.binary|person of colou?r|trans(?:gender|sexual|masc|femme|\s)|"
    r"LGBTIQA?\+?|I identify as|my lived experience|as a .{0,20} person|"
    r"as someone who|my personal|lived experience|peer worker)\b",
    re.IGNORECASE,
)
_BAD_VERB_RE = re.compile(
    r"^(Deep|Commitment|Strong|Passionate|Extensive|Dedicated|Demonstrated|"
    r"Proven|Experienced|The|A|An|This|My|Our|I\b)",
    re.IGNORECASE,
)
_SUBJECTIVE_RE = re.compile(
    r"\b(possess|strong (interpersonal|communication|organisational)|extensive experience"
    r"|I have|ability to|proven track record)\b",
    re.IGNORECASE,
)

# ════════════════════════════════════════════════════════════════════════════
# SECTION 1: DETERMINISTIC RULES
# ════════════════════════════════════════════════════════════════════════════

def strip_glyphs(text: str) -> tuple[str, list[str]]:
    cleaned = _GLYPH_RE.sub("", text)
    cleaned = re.sub(r"  +", " ", cleaned).strip()
    return cleaned, (["removed_markdown_glyphs"] if cleaned != text else [])


def flag_lived_experience(text: str) -> bool:
    return bool(_LIVED_EXP_RE.search(text))


def score_car_quality(text: str) -> int:
    """1–5: length + metric + result signal + action verb + not purely subjective."""
    score = 1
    if len(text.split()) >= 12:
        score += 1
    if _METRIC_RE.search(text):
        score += 1
    if _RESULT_RE.search(text):
        score += 1
    first_word = text.split()[0] if text.split() else ""
    if first_word and not _BAD_VERB_RE.match(first_word):
        score += 1
    return min(score, 5)


def run_deterministic(item: dict, text_field: str) -> list[str]:
    """Apply all deterministic fixes in place. Returns list of fix labels."""
    fixes: list[str] = []
    original = item.get(text_field, "")

    cleaned, glyph_fixes = strip_glyphs(original)
    if glyph_fixes:
        item[text_field] = cleaned
        fixes.extend(glyph_fixes)

    current = item.get(text_field, "")

    if flag_lived_experience(current):
        item["is_lived_experience"] = True
        fixes.append("flagged_lived_experience")

    item["car_quality_score"] = score_car_quality(current)

    if text_field == "raw_text":
        verb = item.get("action_verb", "")
        if not verb or _BAD_VERB_RE.match(verb):
            fixes.append("flagged_bad_action_verb")

    return fixes


# ════════════════════════════════════════════════════════════════════════════
# SECTION 2: LLM REWRITE (GEMINI — two-track)
# ════════════════════════════════════════════════════════════════════════════

_SYSTEM_PROFESSIONAL = """\
<role>
You are a senior recruitment consultant with 15+ years specialising in Australian public sector,
NFP, and community services applications. You write with precision, authenticity, and a deep
understanding of merit-based selection frameworks.
</role>
<task>
Rewrite the provided achievement into a clear Context-Action-Result (CAR) structure.
Return ONLY valid JSON: {"context": "...", "action": "...", "result": "..."}.
No text, explanation, or markdown outside the JSON object.
</task>
<constraints>
GROUNDING: Use only information present in the source text and any supporting evidence provided.
HALLUCINATION GUARD: Never fabricate org names, dates, titles, team sizes, or figures.
INFERENCE MARKING: Wrap any inferred content in [[NEEDS_REVIEW: <your addition>]].
AUSTRALIAN ENGLISH: "organisation", "programme", "behaviour".
</constraints>
"""

_SYSTEM_LIVED_EXP = """\
You are a compassionate editor working with Australian community services job applications.
The following entry is a lived experience statement reflecting the candidate's personal identity.
Your task:
1. Fix formatting artifacts (remove **markdown**, stray glyphs like •, ★, |).
2. Improve professional tone while preserving the candidate's authentic voice.
3. Ensure alignment with LGBTIQA+-inclusive language guidelines.
IMPORTANT: Do NOT impose a CAR/STAR structure. Do NOT add metrics or invented details.
Do NOT alter, minimise, or qualify the lived experience.
Return ONLY the improved text as a plain string.
"""


def _call_gemini(prompt: str, system: str, max_tokens: int = 500) -> Optional[str]:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        log.debug("GEMINI_API_KEY not set — skipping LLM rewrite")
        return None
    try:
        import google.generativeai as genai  # noqa: PLC0415
    except ImportError:
        log.warning("google-generativeai not installed — skipping LLM rewrite")
        return None
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system,
        )
        resp = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=0.3,
            ),
        )
        return resp.text.strip()
    except Exception as exc:
        log.warning("Gemini call failed: %s", exc)
        return None


def _extract_grounding(history: dict, competencies: list[str], max_bullets: int = 5) -> str:
    """Pull top matching achievement bullets from career history as evidence."""
    hits: list[str] = []
    for role in history.get("roles", []):
        for ach in role.get("achievements", []):
            text = ach.get("raw_text", "")
            tags = " ".join(ach.get("domain_tags", []))
            if any(c.lower().replace("_", " ") in tags for c in competencies):
                hits.append(f"- [{role.get('company', '')}] {text}")
                if len(hits) >= max_bullets:
                    break
        if len(hits) >= max_bullets:
            break
    return "\n".join(hits)


def rewrite_with_llm(item: dict, text_field: str, history: Optional[dict]) -> bool:
    """Attempt LLM rewrite. Stores result in item['suggested_rewrite']. Returns True on success."""
    text = item.get(text_field, "")
    is_lived = item.get("is_lived_experience", False)

    if is_lived:
        result = _call_gemini(
            prompt=f"Improve this lived experience statement:\n\n{text}",
            system=_SYSTEM_LIVED_EXP,
            max_tokens=300,
        )
    else:
        competencies = item.get("competency_tags") or item.get("domain_tags") or []
        grounding = _extract_grounding(history, competencies) if history else ""
        prompt = (
            f"ACHIEVEMENT TO IMPROVE:\n{text[:1500]}\n\n"
            f"COMPETENCIES: {', '.join(competencies) or 'general'}\n\n"
            f"GROUNDING EVIDENCE:\n{grounding or '(none)'}\n\n"
            "Rewrite into a clear CAR structure. "
            'Return JSON only: {"context": "...", "action": "...", "result": "..."}. '
            "Wrap inferred content in [[NEEDS_REVIEW: ...]]."
        )
        raw = _call_gemini(prompt=prompt, system=_SYSTEM_PROFESSIONAL, max_tokens=500)
        if raw:
            try:
                raw = re.sub(r"^```[a-z]*\n?", "", raw)
                raw = re.sub(r"\n?```$", "", raw)
                parsed = json.loads(raw)
                result = " ".join(filter(None, [
                    parsed.get("context", ""),
                    parsed.get("action", ""),
                    parsed.get("result", ""),
                ])).strip()
            except Exception:
                result = raw
        else:
            result = None

    if result:
        item["suggested_rewrite"] = result
        fixes = item.get("applied_fixes", [])
        if "llm_rewrite" not in fixes:
            item["applied_fixes"] = fixes + ["llm_rewrite"]
        return True
    return False


# ════════════════════════════════════════════════════════════════════════════
# SECTION 3: STRATIFIED SAMPLING
# ════════════════════════════════════════════════════════════════════════════

def _categorise(item: dict, text_field: str) -> Optional[str]:
    text = item.get(text_field, "")
    verb = item.get("action_verb", "")
    if _GLYPH_RE.search(text):
        return "formatting_artifact"
    if flag_lived_experience(text):
        return "lived_experience"
    if text_field == "raw_text" and (not verb or _BAD_VERB_RE.match(verb)):
        return "bad_action_verb"
    if _SUBJECTIVE_RE.search(text) and not _METRIC_RE.search(text):
        return "subjective_claim"
    if len(text.split()) > 15 and not _METRIC_RE.search(text) and not _RESULT_RE.search(text):
        return "incomplete_car"
    return None


def sample_stratified(
    enriched: dict,
    curated: dict,
    n_per_category: int = 2,
) -> list[dict]:
    """Return up to 10 stratified sample items, 2 per problem category."""
    CATEGORIES = ["formatting_artifact", "lived_experience", "bad_action_verb",
                  "subjective_claim", "incomplete_car"]
    buckets: dict[str, list[dict]] = {c: [] for c in CATEGORIES}

    for role in enriched.get("roles", []):
        for bullet in role.get("achievements", []):
            cat = _categorise(bullet, "raw_text")
            if cat and len(buckets[cat]) < n_per_category:
                sample = dict(bullet)
                sample["_category"] = cat
                sample["_source"] = "achievement"
                sample["_original_text"] = bullet.get("raw_text", "")
                buckets[cat].append(sample)
        if all(len(v) >= n_per_category for v in buckets.values()):
            break

    for narrative in curated.get("narratives", []):
        for cat_name in CATEGORIES:
            if len(buckets[cat_name]) >= n_per_category:
                continue
            cat = _categorise(narrative, "full_text")
            if cat == cat_name:
                sample = dict(narrative)
                sample["_category"] = cat
                sample["_source"] = "narrative"
                sample["_original_text"] = narrative.get("full_text", "")
                buckets[cat_name].append(sample)
                break

    result: list[dict] = []
    for cat in CATEGORIES:
        result.extend(buckets[cat])
    return result


# ════════════════════════════════════════════════════════════════════════════
# SECTION 4: PROCESS SINGLE ITEM
# ════════════════════════════════════════════════════════════════════════════

def should_process(item: dict, force: bool, min_score: int) -> bool:
    if force:
        return item.get("car_quality_score", 0) < min_score if min_score < 5 else True
    return not bool(item.get("applied_fixes"))


def process_item(
    item: dict,
    text_field: str,
    history: Optional[dict],
    force: bool,
    min_score: int,
) -> list[str]:
    """Apply deterministic rules + LLM rewrite. Returns list of new fixes applied."""
    if not should_process(item, force, min_score):
        return []

    det_fixes = run_deterministic(item, text_field)

    existing_fixes = item.get("applied_fixes", [])
    all_fixes = list(set(existing_fixes + det_fixes))
    item["applied_fixes"] = all_fixes

    needs_llm = (
        item.get("car_quality_score", 0) <= 2
        or "removed_markdown_glyphs" in det_fixes
        or "flagged_bad_action_verb" in det_fixes
    )
    if needs_llm:
        rewrite_with_llm(item, text_field, history)

    return det_fixes + (["llm_rewrite"] if "llm_rewrite" in item.get("applied_fixes", []) and "llm_rewrite" not in existing_fixes else [])


# ════════════════════════════════════════════════════════════════════════════
# SECTION 5: REPORT
# ════════════════════════════════════════════════════════════════════════════

def render_report(
    processed_items: list[dict],
    stats: dict,
    is_dry_run: bool,
) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    mode = f"DRY-RUN SAMPLE ({len(processed_items)} entries)" if is_dry_run else f"FULL SWEEP"
    lines = [
        "# Career Brain — Quality Audit Report",
        f"_Generated: {ts} | Mode: {mode}_",
        "",
        "## Summary",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total processed | {stats.get('total', 0)} |",
        f"| Items with fixes | {stats.get('fixed', 0)} |",
        f"| Lived experience flagged | {stats.get('lived_experience', 0)} |",
        f"| LLM rewrites generated | {stats.get('llm_rewrites', 0)} |",
        "",
        "## Fix Type Counts",
    ]
    for fix_type, count in sorted(stats.get("fix_counts", {}).items(), key=lambda x: -x[1]):
        lines.append(f"- `{fix_type}`: {count}")

    lines += ["", "---", "", "## Before / After", ""]

    for item in processed_items:
        tf = "full_text" if item.get("_source") == "narrative" else "raw_text"
        original = item.get("_original_text", item.get(tf, ""))
        current = item.get(tf, "")
        fixes = item.get("applied_fixes", [])
        lines += [
            f"### [{item.get('_category', 'entry')}] {item.get('_source', '')}",
            f"**Original:** {original[:300]}",
            "",
            f"**After deterministic fixes:** {current[:300]}",
            "",
        ]
        if item.get("suggested_rewrite"):
            lines += [f"**LLM suggested rewrite:** {item['suggested_rewrite'][:400]}", ""]
        lines += [
            f"**Fixes applied:** `{'`, `'.join(fixes) if fixes else 'none'}`",
            f"**CAR score:** {item.get('car_quality_score', 0)}/5 | "
            f"**Lived experience:** {item.get('is_lived_experience', False)}",
            "",
        ]

    if is_dry_run:
        lines += [
            "---",
            "",
            "> **Next step:** Review this report, then run "
            "`python3 pipeline/audit_and_repair_database.py --write` to apply to the full database.",
        ]
    return "\n".join(lines)


# ════════════════════════════════════════════════════════════════════════════
# SECTION 6: MAIN
# ════════════════════════════════════════════════════════════════════════════

def _backup(ts: str) -> None:
    backup_dir = DB / "backups" / ts
    backup_dir.mkdir(parents=True, exist_ok=True)
    for src in [ENRICHED, CURATED]:
        if src.exists():
            shutil.copy2(src, backup_dir / src.name)
            log.info(f"  Backed up {src.name} → backups/{ts}/")


def _load_json(path: Path) -> dict:
    if not path.exists():
        log.error(f"Required file not found: {path}")
        sys.exit(1)
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="Sample 10 entries and write draft report only")
    parser.add_argument("--write", action="store_true", help="Full sweep — backup + process + write updated files")
    parser.add_argument("--force", action="store_true", help="Bypass idempotency guard (re-process already-fixed items)")
    parser.add_argument("--min-score", type=int, default=5, metavar="N",
                        help="With --force: only re-sweep items with car_quality_score < N (default: 5 = all)")
    args = parser.parse_args()

    if not args.dry_run and not args.write:
        parser.error("Specify --dry-run or --write")
    if args.dry_run and args.write:
        parser.error("--dry-run and --write are mutually exclusive")

    log.info("=" * 60)
    log.info("CAREER BRAIN — TASK-004: QUALITY AUDIT & REPAIR")
    log.info(f"Mode: {'DRY-RUN' if args.dry_run else 'WRITE'}"
             + (" (FORCE)" if args.force else ""))
    log.info(f"Started: {datetime.now().isoformat()}")
    log.info("=" * 60)

    enriched = _load_json(ENRICHED)
    curated = _load_json(CURATED)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    if args.dry_run:
        samples = sample_stratified(enriched, curated)
        log.info(f"Sampled {len(samples)} stratified entries across 5 problem categories")

        stats: dict = {"total": len(samples), "fixed": 0, "lived_experience": 0,
                       "llm_rewrites": 0, "fix_counts": {}}

        for item in samples:
            tf = "full_text" if item.get("_source") == "narrative" else "raw_text"
            fixes = process_item(item, tf, enriched, force=True, min_score=5)
            if fixes:
                stats["fixed"] += 1
            if item.get("is_lived_experience"):
                stats["lived_experience"] += 1
            if "llm_rewrite" in item.get("applied_fixes", []):
                stats["llm_rewrites"] += 1
            for f in item.get("applied_fixes", []):
                stats["fix_counts"][f] = stats["fix_counts"].get(f, 0) + 1

        report = render_report(samples, stats, is_dry_run=True)
        out_path = DB / "quality_audit_report_draft.md"
        out_path.write_text(report, encoding="utf-8")
        log.info(f"\nDraft report written to: {out_path}")
        log.info("REVIEW the report, then run --write to apply to the full database.")

    else:  # --write
        _backup(ts)

        stats = {"total": 0, "fixed": 0, "lived_experience": 0,
                 "llm_rewrites": 0, "fix_counts": {}}
        all_processed: list[dict] = []

        # Process career history
        for role in enriched.get("roles", []):
            for bullet in role.get("achievements", []):
                stats["total"] += 1
                bullet["_original_text"] = bullet.get("raw_text", "")
                bullet["_source"] = "achievement"
                fixes = process_item(bullet, "raw_text", enriched, args.force, args.min_score)
                if fixes:
                    stats["fixed"] += 1
                if bullet.get("is_lived_experience"):
                    stats["lived_experience"] += 1
                if "llm_rewrite" in bullet.get("applied_fixes", []):
                    stats["llm_rewrites"] += 1
                for f in bullet.get("applied_fixes", []):
                    stats["fix_counts"][f] = stats["fix_counts"].get(f, 0) + 1
                if fixes:
                    all_processed.append(dict(bullet))

        # Process narratives
        for narrative in curated.get("narratives", []):
            stats["total"] += 1
            narrative["_original_text"] = narrative.get("full_text", "")
            narrative["_source"] = "narrative"
            fixes = process_item(narrative, "full_text", enriched, args.force, args.min_score)
            if fixes:
                stats["fixed"] += 1
            if narrative.get("is_lived_experience"):
                stats["lived_experience"] += 1
            if "llm_rewrite" in narrative.get("applied_fixes", []):
                stats["llm_rewrites"] += 1
            for f in narrative.get("applied_fixes", []):
                stats["fix_counts"][f] = stats["fix_counts"].get(f, 0) + 1
            if fixes:
                all_processed.append(dict(narrative))

        # Strip internal keys before writing
        for item in enriched.get("roles", []):
            for b in item.get("achievements", []):
                b.pop("_original_text", None)
                b.pop("_source", None)
        for n in curated.get("narratives", []):
            n.pop("_original_text", None)
            n.pop("_source", None)

        ENRICHED.write_text(json.dumps(enriched, indent=2, ensure_ascii=False), encoding="utf-8")
        CURATED.write_text(json.dumps(curated, indent=2, ensure_ascii=False), encoding="utf-8")
        log.info(f"Updated: {ENRICHED.name}")
        log.info(f"Updated: {CURATED.name}")

        report = render_report(all_processed, stats, is_dry_run=False)
        out_path = DB / "quality_audit_report.md"
        out_path.write_text(report, encoding="utf-8")
        log.info(f"Report written to: {out_path}")

        log.info("\n" + "=" * 60)
        log.info("AUDIT COMPLETE")
        log.info(f"  Total items processed : {stats['total']}")
        log.info(f"  Items fixed           : {stats['fixed']}")
        log.info(f"  Lived experience flags: {stats['lived_experience']}")
        log.info(f"  LLM rewrites          : {stats['llm_rewrites']}")
        log.info("=" * 60)


if __name__ == "__main__":
    main()
