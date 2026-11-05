#!/usr/bin/env python3
"""Heading-aware font check in tools/verify_golden_master.py (no Google calls).

Simulates the runs Google Docs returns for a built Golden Master: an override
equal to the doc default font (Arial) is normalized away to no fontFamily.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import build_golden_master as bgm  # noqa: E402
from verify_golden_master import check_fonts_by_role  # noqa: E402

DEFAULT = "Arial"


def load(name):
    return json.loads((ROOT / "templates" / name).read_text(encoding="utf-8"))


def simulate_doc(theme, override=None):
    """Build Doc-shaped paragraphs as Docs would store them after a correct build."""
    base = theme["typography"]["base_font"]
    heading = (theme.get("heading_font_family") or [base])[0]
    paragraphs = []
    for i, row in enumerate(bgm.build_paragraphs(theme)):
        font = heading if row[4] in bgm.HEADING_ROLES else base
        if override and i in override:
            font = override[i]
        style = {} if font == DEFAULT else {"weightedFontFamily": {"fontFamily": font}}
        style["foregroundColor"] = {"color": {}}
        paragraphs.append([(row[0] + "\n", style)])
    return paragraphs


def run(theme, paragraphs):
    base = theme["typography"]["base_font"]
    heading = (theme.get("heading_font_family") or [base])[0]
    return check_fonts_by_role(paragraphs, bgm.build_paragraphs(theme), DEFAULT, base, heading, bgm.HEADING_ROLES)


def test_georgia_body_arial_headings_passes():
    theme = load("resume_graphite_ledger_v1.json")
    ok, checked, problems = run(theme, simulate_doc(theme))
    assert ok, problems
    assert checked == len(bgm.build_paragraphs(theme))


def test_heading_runs_without_override_are_the_heading_roles():
    theme = load("resume_graphite_ledger_v1.json")
    paragraphs = simulate_doc(theme)
    bare = [p for p in paragraphs if "weightedFontFamily" not in p[0][1]]
    heading_rows = [r for r in bgm.build_paragraphs(theme) if r[4] in bgm.HEADING_ROLES]
    assert len(bare) == len(heading_rows) == 13


def test_body_run_in_wrong_font_fails():
    theme = load("resume_graphite_ledger_v1.json")
    rows = bgm.build_paragraphs(theme)
    body_idx = next(i for i, r in enumerate(rows) if r[4] not in bgm.HEADING_ROLES)
    ok, _, problems = run(theme, simulate_doc(theme, {body_idx: DEFAULT}))
    assert not ok and "expected=Georgia" in problems[0]


def test_heading_run_in_body_font_fails():
    theme = load("resume_graphite_ledger_v1.json")
    rows = bgm.build_paragraphs(theme)
    head_idx = next(i for i, r in enumerate(rows) if r[4] == "h1")
    ok, _, problems = run(theme, simulate_doc(theme, {head_idx: "Georgia"}))
    assert not ok and "expected=Arial" in problems[0]


def test_unmatched_paragraph_fails():
    theme = load("resume_graphite_ledger_v1.json")
    paragraphs = simulate_doc(theme) + [[("Unexpected text\n", {})]]
    ok, _, problems = run(theme, paragraphs)
    assert not ok and problems[0].startswith("unmatched paragraph")


def test_calibri_ksc_all_runs_need_override():
    theme = load("ksc_standard_v2.json")
    ok, _, problems = run(theme, simulate_doc(theme))
    assert ok, problems
    rows = bgm.build_paragraphs(theme)
    ok, _, _ = run(theme, simulate_doc(theme, {0: DEFAULT}))
    assert not ok


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
