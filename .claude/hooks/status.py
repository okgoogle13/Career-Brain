#!/usr/bin/env python3
"""Status recap: reads TASKS.md and plan docs, prints a short recap only when
state changed (or with --force). Output is Stop-hook JSON. Always exits 0.

Design: docs/superpowers/design/2026-10-25-status-recap-design.md
"""
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# --- Config (constants, no config file) ---
TASKS_FILE = "TASKS.md"
HASH_FILE = ".claude/.status-hash"
GATE_MARKER = "[GATE: user]"
MAX_LINES = 10

TASK_RE = re.compile(r"^###\s+(TASK-\d+)\b\s*[—–-]*\s*(.*)$")
FIELD_RE = r"^\s*(?:[-*]\s*)?\**{name}:?\**:?\**\s*(.+?)\s*$"
STEP_RE = re.compile(r"^\s*[-*]\s+\[( |x|X)\]\s+(.*)$")


def _field(block, name):
    m = re.search(FIELD_RE.format(name=name), block, re.M)
    return m.group(1).strip("` ") if m else None


def _section(text, heading):
    """Text of '## heading' up to the next '## ' heading ('' if absent)."""
    m = re.search(r"^##\s+%s\b.*$" % re.escape(heading), text, re.M)
    if not m:
        return ""
    rest = text[m.end():]
    n = re.search(r"^##\s+", rest, re.M)
    return rest[: n.start()] if n else rest


def _tasks(section):
    """Split a section into [{'id','title','block'}] in file order."""
    out, cur = [], None
    for line in section.splitlines():
        m = TASK_RE.match(line)
        if m:
            cur = {"id": m.group(1), "title": m.group(2).strip(), "lines": []}
            out.append(cur)
        elif cur is not None:
            cur["lines"].append(line)
    for t in out:
        t["block"] = "\n".join(t.pop("lines"))
    return out


def _front_matter(text):
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    fm = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip()
    return fm


def _plan_info(root, rel):
    """Return dict for a plan path, or None if missing/unreadable."""
    if not rel:
        return None
    p = root / rel
    if not p.is_file():
        return None
    text = p.read_text(encoding="utf-8")
    steps = [STEP_RE.match(line) for line in text.splitlines()]
    steps = [(m.group(1) != " ", m.group(2)) for m in steps if m]
    unchecked = [s for done, s in steps if not done]
    return {
        "path": rel,
        "mtime": p.stat().st_mtime,
        "front": _front_matter(text),
        "unchecked": unchecked,
    }


def _dirty_count(root):
    try:
        r = subprocess.run(
            ["git", "status", "--porcelain"], cwd=root,
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode != 0:
            return None
        return len([x for x in r.stdout.splitlines() if x.strip()])
    except Exception:
        return None


def build(root):
    """Return (recap_text, hash_digest). Dirty count is shown, not hashed."""
    root = Path(root)
    tasks_path = root / TASKS_FILE
    if not tasks_path.is_file():
        return "Status: TASKS.md not found.", "missing"
    text = tasks_path.read_text(encoding="utf-8")
    active = _tasks(_section(text, "Active"))
    completed_ids = {t["id"] for t in _tasks(_section(text, "Completed"))}

    seen, dupes = set(), set()
    for t in active:
        if t["id"] in seen:
            dupes.add(t["id"])
        seen.add(t["id"])
    # First occurrence wins; later duplicates are dropped from the list.
    uniq, ids = [], set()
    for t in active:
        if t["id"] not in ids:
            ids.add(t["id"])
            uniq.append(t)
    for t in uniq:
        t["plan"] = _plan_info(root, _field(t["block"], "Plan"))
        t["plan_ref"] = _field(t["block"], "Plan")
        t["next"] = _field(t["block"], "Next")

    # Focus: most recently edited plan; else first Active entry.
    with_plan = [t for t in uniq if t["plan"]]
    focus = max(with_plan, key=lambda t: t["plan"]["mtime"]) if with_plan else (uniq[0] if uniq else None)

    # Hash inputs: Active section, plan front matter, unchecked counts. No dirty count.
    h = hashlib.sha256()
    h.update(_section(text, "Active").encode())
    for t in uniq:
        if t["plan"]:
            h.update(json.dumps(
                [t["plan"]["path"], t["plan"]["front"], len(t["plan"]["unchecked"])],
                sort_keys=True).encode())

    lines = []
    if focus is None:
        lines.append("Active task: none")
    else:
        flags = []
        if focus["id"] in dupes:
            flags.append("duplicate ID in Active")
        if focus["id"] in completed_ids:
            flags.append("also listed in Completed")
        flag = f" [{'; '.join(flags)}]" if flags else ""
        lines.append(f"Active task: {focus['id']} {focus['title']}".rstrip() + flag)
        plan = focus["plan"]
        if plan:
            lines.append(f"Plan: {plan['path']} (status: {plan['front'].get('status', 'unknown')})")
            if plan["unchecked"]:
                step = plan["unchecked"][0]
                gated = GATE_MARKER in step
                lines.append(f"First unchecked step: {step}")
                lines.append(f"Gated: {'yes (' + GATE_MARKER + ')' if gated else 'no'}")
            else:
                lines.append("First unchecked step: none")
                lines.append("Gated: unknown")
        else:
            ref = focus["plan_ref"]
            lines.append("Plan: " + (f"{ref} (file not found)" if ref else "unknown"))
            lines.append("First unchecked step: unknown")
            lines.append("Gated: unknown")
        lines.append(f"Next: {focus['next'] or 'unknown'}")
        others = [t for t in uniq if t is not focus]
        if others:
            lines.append("Also active: " + "; ".join(f"{t['id']} {t['title']}".strip() for t in others))
    mtime = datetime.fromtimestamp(tasks_path.stat().st_mtime).strftime("%Y-%m-%d")
    dirty = _dirty_count(root)
    lines.append(f"TASKS.md last edited: {mtime} | changed files: {dirty if dirty is not None else 'unknown'}")
    return "\n".join(lines[:MAX_LINES]), h.hexdigest()


def run(root, force=False):
    """Return recap text to show, or None if unchanged. Updates the hash file."""
    root = Path(root)
    try:
        recap, digest = build(root)
    except Exception as e:  # parse error: one-line warning
        return f"Status: could not parse tasks/plans ({type(e).__name__}).\n"[:-1]
    hash_path = root / HASH_FILE
    old = hash_path.read_text().strip() if hash_path.is_file() else None
    if not force and old == digest:
        return None
    try:
        hash_path.parent.mkdir(parents=True, exist_ok=True)
        hash_path.write_text(digest)
    except OSError:
        pass
    return recap


def main(argv):
    try:
        msg = run(Path.cwd(), force="--force" in argv)
        if msg:
            print(json.dumps({"systemMessage": msg}))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
