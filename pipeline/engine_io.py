"""Shared engine-file safety helpers for pipeline writers.

- append_errors: the only way scripts other than normalize_vault.py touch
  database/parsing_errors.log. Appends with a run_id header, written only when
  there are entries, so a clean run leaves the log empty.
- backup: timestamped copy of engine files to database/backups/<ts>/ before a write.
- validate_engine: re-validates an engine file against the compile_brain models
  (source_lineage must be non-empty on every node).
"""

from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent.parent
DB = BASE / "database"
ERROR_LOG = DB / "parsing_errors.log"
BACKUPS = DB / "backups"

log = logging.getLogger("engine_io")


def run_id(script: str) -> str:
    return f"{script}-{datetime.now().strftime('%Y%m%dT%H%M%S')}"


def append_errors(rid: str, entries: list[str]) -> None:
    """Append entries under a run_id header; no-op when there are none."""
    if not entries:
        return
    with ERROR_LOG.open("a", encoding="utf-8") as fh:
        fh.write(f"### run_id={rid}\n")
        fh.write("\n".join(entries) + "\n")
        fh.flush()


def backup(paths: list[Path], ts: str | None = None) -> Path:
    """Copy existing files to database/backups/<ts>/ and return that directory."""
    ts = ts or datetime.now().strftime("%Y%m%dT%H%M%S")
    dest = BACKUPS / ts
    dest.mkdir(parents=True, exist_ok=True)
    for src in paths:
        if src.exists():
            shutil.copy2(src, dest / src.name)
            log.info(f"  Backed up {src.name} → backups/{ts}/")
    return dest


def validate_engine(path: Path) -> None:
    """Validate an engine file against its compile_brain model; raises ValueError on failure."""
    import compile_brain as cb  # local import: compile_brain imports this module

    models = {
        "career_history.json": cb.CareerHistoryDB,
        "career_history_enriched.json": cb.CareerHistoryDB,
        "ksc_and_narratives.json": cb.NarrativesDB,
        "ksc_curated.json": cb.NarrativesDB,
        "ksc_curated_tier1.json": cb.NarrativesDB,
        "skills_and_taxonomy.json": cb.TaxonomyDB,
    }
    model = models[path.name]
    model.model_validate(json.loads(path.read_text(encoding="utf-8")))
