"""Tests for .claude/hooks/status.py (loaded by file path; not a package)."""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / ".claude" / "hooks" / "status.py"
spec = importlib.util.spec_from_file_location("status", SCRIPT)
status = importlib.util.module_from_spec(spec)
spec.loader.exec_module(status)

TASKS = """# TASKS

## Active

### TASK-001 — Alpha
**Status:** in progress
**Plan:** docs/plans/alpha.md
**Next:** `.venv/bin/pytest -q tests`

## Completed

### TASK-000 — Old
"""

PLAN = """---
task: TASK-001
status: in-progress
---
- [x] done step
- [ ] open step
- [ ] later step
"""


def make(root, tasks=TASKS, plan=PLAN):
    (root / "TASKS.md").write_text(tasks)
    if plan is not None:
        (root / "docs/plans").mkdir(parents=True, exist_ok=True)
        (root / "docs/plans/alpha.md").write_text(plan)


def test_changed_then_unchanged(tmp_path):
    make(tmp_path)
    first = status.run(tmp_path)
    assert "TASK-001" in first and "open step" in first
    assert "Next: `.venv/bin/pytest" in first or "Next: .venv/bin/pytest" in first
    assert status.run(tmp_path) is None
    assert status.run(tmp_path, force=True) == first


def test_state_change_retriggers(tmp_path):
    make(tmp_path)
    status.run(tmp_path)
    (tmp_path / "docs/plans/alpha.md").write_text(PLAN.replace("- [ ] open step", "- [x] open step"))
    again = status.run(tmp_path)
    assert again and "later step" in again


def test_dirty_count_not_in_hash(tmp_path):
    make(tmp_path)
    _, h1 = status.build(tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "x.py").write_text("1")
    _, h2 = status.build(tmp_path)
    assert h1 == h2


def test_gated(tmp_path):
    make(tmp_path, plan=PLAN.replace("open step", "call Gemini [GATE: user]"))
    out = status.run(tmp_path)
    assert "Gated: yes" in out


def test_ungated(tmp_path):
    make(tmp_path)
    assert "Gated: no" in status.run(tmp_path)


def test_missing_plan_line(tmp_path):
    make(tmp_path, tasks=TASKS.replace("**Plan:** docs/plans/alpha.md\n", ""), plan=None)
    out = status.run(tmp_path)
    assert "Plan: unknown" in out
    assert "First unchecked step: unknown" in out


def test_plan_file_not_found(tmp_path):
    make(tmp_path, plan=None)
    assert "file not found" in status.run(tmp_path)


def test_no_next_line(tmp_path):
    make(tmp_path, tasks=TASKS.replace("**Next:** `.venv/bin/pytest -q tests`\n", ""))
    assert "Next: unknown" in status.run(tmp_path)


def test_duplicate_ids_in_active_and_completed(tmp_path):
    tasks = TASKS.replace("## Completed", "### TASK-001 — Alpha again\n\n## Completed").replace(
        "### TASK-000 — Old", "### TASK-000 — Old\n### TASK-001 — Alpha done")
    make(tmp_path, tasks=tasks)
    out = status.run(tmp_path)
    assert "duplicate ID in Active" in out
    assert "also listed in Completed" in out
    assert out.count("TASK-001") == 1


def test_most_recent_plan_wins(tmp_path):
    tasks = TASKS.replace("## Completed", (
        "### TASK-002 — Beta\n**Plan:** docs/plans/beta.md\n\n## Completed"))
    make(tmp_path, tasks=tasks)
    beta = tmp_path / "docs/plans/beta.md"
    beta.write_text(PLAN.replace("TASK-001", "TASK-002"))
    os.utime(tmp_path / "docs/plans/alpha.md", (1, 1))
    out = status.run(tmp_path)
    assert out.startswith("Active task: TASK-002")
    assert "Also active: TASK-001" in out


def test_no_checkboxes_no_plans(tmp_path):
    make(tmp_path, plan=None, tasks="## Active\n\n### TASK-009 — Plain\n**Status:** x\n")
    out = status.run(tmp_path)
    assert "TASK-009" in out and "unknown" in out


def test_missing_tasks_file(tmp_path):
    assert "not found" in status.run(tmp_path)


def test_line_cap(tmp_path):
    make(tmp_path)
    assert len(status.run(tmp_path).splitlines()) <= 10


def test_cli_always_exit_0_and_json(tmp_path):
    make(tmp_path)
    r = subprocess.run([sys.executable, str(SCRIPT)], cwd=tmp_path, capture_output=True, text=True)
    assert r.returncode == 0
    assert "systemMessage" in json.loads(r.stdout)
    r2 = subprocess.run([sys.executable, str(SCRIPT)], cwd=tmp_path, capture_output=True, text=True)
    assert r2.returncode == 0 and r2.stdout == ""
    (tmp_path / "TASKS.md").unlink()
    r3 = subprocess.run([sys.executable, str(SCRIPT), "--force"], cwd=tmp_path, capture_output=True, text=True)
    assert r3.returncode == 0
