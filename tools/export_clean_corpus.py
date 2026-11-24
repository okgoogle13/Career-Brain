#!/usr/bin/env python3
"""
export_clean_corpus.py — Stage 1 Local Scrubber & Corpus Packager
=================================================================
Reads normalized text files in ``processed/`` (read-only), filters out
third-party files, referee contact sheets, and generic templates/guides,
deduplicates exact and near-identical copies, scrubs contact PII, and
writes two git-ignored staging bundles to ``scratch/clean_corpus/``:

  - ``own_ksc_and_letters.local.md``  (KSCs, cover letters, interview prep)
  - ``own_resumes.local.md``          (resumes, master resume, statement of results)
  - ``manifest.local.json``           (audit trail: kept, deduplicated, excluded, redactions)

Usage:
  .venv/bin/python tools/export_clean_corpus.py --dry-run
  .venv/bin/python tools/export_clean_corpus.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

BASE = Path(__file__).parent.parent
PROCESSED_DIR = BASE / "processed"
CURATION_CONFIG = BASE / "config" / "narrative_curation.json"
SHARING_POLICY = BASE / "config" / "ai_sharing_policy.json"
DEFAULT_OUT_DIR = BASE / "scratch" / "clean_corpus"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("export_clean_corpus")

# Filenames matching any of these substrings (case-insensitive) are always excluded:
# third-party applicants, referee contact lists (Amber), and generic templates/AI guides.
EXCLUDE_SUBSTRINGS: tuple[str, ...] = (
    "kassie",
    "references__",
    "_references_",
    "references_for_",
    "references_-_",
    "cv_template",
    "ats_stylish_accounting",
    "free_copy",
    "geminis_responses",
    "robert_walters",
    "example_master_resume",
    "euc_lft_uds",
    "final_combined_resumes",
    "emailing_resumes_combined",
)

# Content-level Red-tier gate: any file hitting 2+ clinical/pathology/gov-ID markers
# (or any explicit Medicare/TFN/pathology marker) is excluded whole-file.
RED_TIER_CONTENT_RE = re.compile(
    r"\b(?:medicare|tax\s+file\s+number|\btfn\b|pathology|specimen|creatinine|bilirubin|patient\s+id|lab\s+no)\b",
    re.IGNORECASE,
)

# Within knowledge__*, only these explicitly own-authored patterns are kept.
OWN_KNOWLEDGE_PATTERNS: tuple[str, ...] = (
    "iap_launch_interview_prep_responses",
    "master_resume_with_subtypes",
    "statement_of_results_mp",
    "nishant_dougall_",
)

# Additional PII / secret scrubbing patterns beyond config/narrative_curation.json.
EXTRA_REDACTION_PATTERNS: tuple[tuple[str, str], ...] = (
    ("email", r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    ("au_mobile", r"(?:\+?61[\s-]?|\b0)4\d{2}[\s-]?\d{3}[\s-]?\d{3}\b"),
    ("au_landline", r"(?:\+?61[\s-]?|\b0)[2378][\s-]?\d{4}[\s-]?\d{4}\b"),
    ("uk_phone", r"(?:\+?44[\s-]?|\b0)7\d{3}[\s-]?\d{6}\b"),
    ("au_street_address", r"\b\d{1,4}(?:/\d{1,4})?\s+[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?\s+(?:Street|St|Road|Rd|Avenue|Ave|Drive|Dr|Court|Ct|Parade|Pde|Crescent|Cres|Lane|Ln|Place|Pl)\b(?:,\s*[A-Za-z\s]+?\s+(?:VIC|NSW|QLD|SA|WA|TAS|NT|ACT)\s+\d{4})?"),
    ("api_key_like", r"\b(?:AIza[0-9A-Za-z_-]{20,}|sk-[0-9A-Za-z_-]{20,})\b"),
)


def _load_redaction_config() -> tuple[str, list[tuple[str, re.Pattern[str]]]]:
    placeholder = "[[REDACTED_SENSITIVE_DATA]]"
    if SHARING_POLICY.exists():
        policy = json.loads(SHARING_POLICY.read_text(encoding="utf-8"))
        placeholder = policy.get("redaction", {}).get("placeholder", placeholder)

    patterns: list[tuple[str, re.Pattern[str]]] = []
    if CURATION_CONFIG.exists():
        cfg = json.loads(CURATION_CONFIG.read_text(encoding="utf-8"))
        for idx, pat in enumerate(cfg.get("contact_patterns", []), start=1):
            patterns.append((f"config_contact_{idx}", re.compile(pat, re.IGNORECASE)))

    for label, pat in EXTRA_REDACTION_PATTERNS:
        flags = 0 if label in ("au_street_address", "api_key_like") else re.IGNORECASE
        patterns.append((label, re.compile(pat, flags)))

    return placeholder, patterns


def classify_file(filename: str) -> tuple[str, str]:
    """Return (bucket, reason) where bucket is 'ksc_letters', 'resumes', or 'exclude'."""
    low = filename.lower()

    for sub in EXCLUDE_SUBSTRINGS:
        if sub in low:
            return "exclude", f"matched_exclude:{sub}"

    if low.startswith("knowledge__"):
        if not any(pat in low for pat in OWN_KNOWLEDGE_PATTERNS):
            return "exclude", "non_own_knowledge_guide"
        if any(tok in low for tok in ("interview_prep", "cover_letter", "cover-letter")):
            return "ksc_letters", "own_knowledge_ksc_or_letter"
        return "resumes", "own_knowledge_resume_or_transcript"

    if low.startswith("ksc__"):
        return "ksc_letters", "ksc_prefix"

    if low.startswith("cover_letters__"):
        if "final_combined_resumes" in low:
            return "resumes", "misfiled_resume_in_cover_letters"
        return "ksc_letters", "cover_letters_prefix"

    if low.startswith("resumes__"):
        if "responses_to_key_selection_criteria" in low or "cover_letter" in low or "letter_1_green" in low:
            return "ksc_letters", "misfiled_ksc_or_letter_in_resumes"
        return "resumes", "resumes_prefix"

    return "exclude", "unrecognised_prefix"


def scrub_text(
    text: str,
    placeholder: str,
    patterns: list[tuple[str, re.Pattern[str]]],
) -> tuple[str, dict[str, int]]:
    counts: dict[str, int] = {}
    cleaned = text
    for label, regex in patterns:
        cleaned, hits = regex.subn(placeholder, cleaned)
        if hits:
            counts[label] = counts.get(label, 0) + hits
    return cleaned, counts


def _norm_for_hash(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _ngrams(text: str, n: int = 4) -> set[tuple[str, ...]]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    if len(words) < n:
        return {tuple(words)} if words else set()
    return set(zip(*(words[i:] for i in range(n))))


def _jaccard(a: set[tuple[str, ...]], b: set[tuple[str, ...]]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _preference_rank(filename: str, text_len: int) -> tuple[int, int, int, int]:
    """Prefer direct non-harvested, non-converted, longer originals when deduplicating."""
    low = filename.lower()
    is_harvested = 1 if "harvested_" in low else 0
    is_converted = 1 if "__converted_" in low else 0
    has_dup_suffix = 1 if re.search(r"_\d+_\.txt$", low) else 0
    return (is_harvested, is_converted, has_dup_suffix, -text_len)


def deduplicate_docs(
    docs: list[dict[str, Any]],
    near_dup_threshold: float = 0.90,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Collapse exact and near-duplicate documents while preserving lineage."""
    ordered = sorted(docs, key=lambda d: _preference_rank(d["filename"], len(d["text"])))

    kept: list[dict[str, Any]] = []
    dropped: list[dict[str, Any]] = []
    seen_hashes: dict[str, dict[str, Any]] = {}
    kept_ngrams: list[tuple[dict[str, Any], set[tuple[str, ...]]]] = []

    for doc in ordered:
        norm = _norm_for_hash(doc["text"])
        if not norm:
            dropped.append({"filename": doc["filename"], "reason": "empty_after_norm", "kept_ref": None})
            continue
        digest = hashlib.sha256(norm.encode("utf-8")).hexdigest()
        if digest in seen_hashes:
            owner = seen_hashes[digest]
            owner.setdefault("collapsed_duplicates", []).append(doc["filename"])
            dropped.append({"filename": doc["filename"], "reason": "exact_duplicate", "kept_ref": owner["filename"]})
            continue

        grams = _ngrams(doc["text"])
        matched_owner: dict[str, Any] | None = None
        matched_sim = 0.0
        for owner, owner_grams in kept_ngrams:
            sim = _jaccard(grams, owner_grams)
            if sim >= near_dup_threshold:
                matched_owner = owner
                matched_sim = sim
                break

        if matched_owner is not None:
            matched_owner.setdefault("collapsed_duplicates", []).append(doc["filename"])
            dropped.append({
                "filename": doc["filename"],
                "reason": f"near_duplicate:{matched_sim:.2f}",
                "kept_ref": matched_owner["filename"],
            })
            continue

        doc["collapsed_duplicates"] = []
        seen_hashes[digest] = doc
        kept.append(doc)
        kept_ngrams.append((doc, grams))

    kept.sort(key=lambda d: d["filename"])
    return kept, dropped


def render_bundle(title: str, docs: list[dict[str, Any]]) -> str:
    total_chars = sum(len(d["text"]) for d in docs)
    lines = [
        f"# {title}",
        "",
        f"- Documents included: {len(docs)}",
        f"- Approximate tokens (~4 chars/token): {total_chars // 4:,}",
        "- PII status: contact details and street addresses replaced with `[[REDACTED_SENSITIVE_DATA]]`",
        "- Third-party files and referee contact sheets excluded.",
        "",
        "---",
        "",
    ]
    for doc in docs:
        dups = doc.get("collapsed_duplicates") or []
        lines.append(f"=== FILE: {doc['filename']} ===")
        if dups:
            lines.append(f"<!-- collapsed_duplicates ({len(dups)}): {', '.join(dups)} -->")
        lines.append("")
        lines.append(doc["text"].strip())
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


def verify_bundle_clean(bundle_text: str, kept_filenames: list[str]) -> list[str]:
    """Post-export verification: confirm zero emails, AU mobiles, or excluded filenames."""
    issues: list[str] = []
    for fn in kept_filenames:
        low = fn.lower()
        for sub in EXCLUDE_SUBSTRINGS:
            if sub in low:
                issues.append(f"excluded_filename_leaked:{fn}")

    email_hits = re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", bundle_text)
    if email_hits:
        issues.append(f"email_leaked:{len(email_hits)}")

    mobile_hits = re.findall(r"(?:\+?61[\s-]?|\b0)4\d{2}[\s-]?\d{3}[\s-]?\d{3}\b", bundle_text)
    if mobile_hits:
        issues.append(f"au_mobile_leaked:{len(mobile_hits)}")

    red_hits = sorted(set(m.lower() for m in RED_TIER_CONTENT_RE.findall(bundle_text)))
    if red_hits:
        issues.append(f"red_tier_content_leaked:{','.join(red_hits)}")

    return issues


def run_export(
    processed_dir: Path = PROCESSED_DIR,
    out_dir: Path = DEFAULT_OUT_DIR,
    *,
    near_dup_threshold: float = 0.80,
    dry_run: bool = False,
) -> dict[str, Any]:
    if not processed_dir.exists():
        raise FileNotFoundError(f"Processed directory not found: {processed_dir}")

    placeholder, patterns = _load_redaction_config()
    buckets: dict[str, list[dict[str, Any]]] = {"ksc_letters": [], "resumes": []}
    excluded: list[dict[str, str]] = []
    total_redactions: dict[str, int] = {}

    for path in sorted(processed_dir.iterdir()):
        if not path.is_file() or path.name.startswith("."):
            continue
        bucket, reason = classify_file(path.name)
        if bucket == "exclude":
            excluded.append({"filename": path.name, "reason": reason})
            continue

        raw_text = path.read_text(encoding="utf-8", errors="replace")
        red_hits = sorted(set(m.lower() for m in RED_TIER_CONTENT_RE.findall(raw_text)))
        if red_hits:
            excluded.append({"filename": path.name, "reason": f"red_tier_content:{','.join(red_hits)}"})
            continue
        cleaned, red_counts = scrub_text(raw_text, placeholder, patterns)
        for k, v in red_counts.items():
            total_redactions[k] = total_redactions.get(k, 0) + v

        buckets[bucket].append({
            "filename": path.name,
            "route_reason": reason,
            "text": cleaned,
            "redactions": red_counts,
        })

    summary: dict[str, Any] = {
        "processed_total": sum(len(v) for v in buckets.values()) + len(excluded),
        "excluded_count": len(excluded),
        "total_redactions": total_redactions,
        "bundles": {},
        "excluded_files": excluded,
    }

    bundle_specs = (
        ("ksc_letters", "own_ksc_and_letters.local.md", "Career Brain — Scrubbed Own KSC, Cover Letters & Interview Prep"),
        ("resumes", "own_resumes.local.md", "Career Brain — Scrubbed Own Resumes & Academic Record"),
    )

    if not dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    for key, out_name, title in bundle_specs:
        raw_docs = buckets[key]
        kept, deduped = deduplicate_docs(raw_docs, near_dup_threshold=near_dup_threshold)
        rendered = render_bundle(title, kept)
        verify_issues = verify_bundle_clean(rendered, [d["filename"] for d in kept])
        est_tokens = len(rendered) // 4

        summary["bundles"][key] = {
            "output_file": str(out_dir / out_name),
            "raw_matched": len(raw_docs),
            "kept_unique": len(kept),
            "deduplicated": len(deduped),
            "bytes": len(rendered.encode("utf-8")),
            "est_tokens": est_tokens,
            "verify_issues": verify_issues,
            "kept_files": [
                {
                    "filename": d["filename"],
                    "chars": len(d["text"]),
                    "collapsed_duplicates": d["collapsed_duplicates"],
                }
                for d in kept
            ],
            "deduped_files": deduped,
        }

        if not dry_run:
            (out_dir / out_name).write_text(rendered, encoding="utf-8")

    if not dry_run:
        (out_dir / "manifest.local.json").write_text(
            json.dumps(summary, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    return summary


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scrub and package own-authored processed/ files into clean staging bundles."
    )
    parser.add_argument("--dry-run", action="store_true", help="Report counts and verification without writing files.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR, help="Destination directory (git-ignored).")
    parser.add_argument("--near-dup", type=float, default=0.80, help="4-gram Jaccard threshold for near-dup collapse.")
    args = parser.parse_args()

    summary = run_export(out_dir=args.out_dir, near_dup_threshold=args.near_dup, dry_run=args.dry_run)

    log.info("Processed scanned : %d files", summary["processed_total"])
    log.info("Excluded          : %d files", summary["excluded_count"])
    log.info("Redactions        : %s", summary["total_redactions"])
    exit_code = 0
    for key, info in summary["bundles"].items():
        log.info(
            "Bundle %-11s: raw=%d -> kept=%d (deduped=%d) | %d KB | ~%s tokens | issues=%s",
            key,
            info["raw_matched"],
            info["kept_unique"],
            info["deduplicated"],
            info["bytes"] // 1024,
            f"{info['est_tokens']:,}",
            info["verify_issues"] or "NONE",
        )
        if info["verify_issues"]:
            exit_code = 2
    if args.dry_run:
        log.info("Dry-run only — no files written.")
    else:
        log.info("Wrote clean staging bundles and manifest to %s", args.out_dir)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
