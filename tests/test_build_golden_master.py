#!/usr/bin/env python3
"""Regression guard for the Golden Master styling sequence.

Locks the fix from commit 30d00de ("fix text style sequence"): within the
batchUpdate request list, each paragraph's `updateParagraphStyle` MUST precede
its `updateTextStyle` for the same range — otherwise applying `namedStyleType`
re-asserts the named style's text formatting over the runs and wipes the
overrides (the `textStyle: {}` bug).

Runs two ways:
    pytest tests/test_build_golden_master.py        # if pytest is installed
    python3 tests/test_build_golden_master.py        # standalone, stdlib only
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import build_golden_master as bgm  # noqa: E402

# A real v2.0 production template that exercises the full resume path (8 blocks).
TEMPLATE = ROOT / "templates" / "resume_copper_teal_circuit_v1.json"


def _build_requests():
    theme = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    paragraphs = bgm.build_paragraphs(theme)
    assert paragraphs, "build_paragraphs produced no paragraphs"
    return bgm.build_requests(theme, paragraphs, doc_id="TEST"), paragraphs


def test_paragraph_style_precedes_text_style_per_range():
    """For every range, updateParagraphStyle is emitted before updateTextStyle."""
    requests, _ = _build_requests()
    first_para = {}
    first_text = {}
    for i, req in enumerate(requests):
        if "updateParagraphStyle" in req:
            r = req["updateParagraphStyle"]["range"]
            first_para.setdefault((r["startIndex"], r["endIndex"]), i)
        elif "updateTextStyle" in req:
            r = req["updateTextStyle"]["range"]
            first_text.setdefault((r["startIndex"], r["endIndex"]), i)

    assert first_text, "no updateTextStyle requests were generated"
    for rng, text_i in first_text.items():
        assert rng in first_para, f"text style range {rng} has no matching paragraph style"
        assert first_para[rng] < text_i, (
            f"REGRESSION: updateParagraphStyle for {rng} must precede its updateTextStyle "
            f"(para at {first_para[rng]}, text at {text_i})"
        )


def test_text_runs_carry_font_size_and_family():
    """Every text run sets the fields that were empty in the bug (fontSize, weightedFontFamily)."""
    requests, _ = _build_requests()
    text_reqs = [r["updateTextStyle"] for r in requests if "updateTextStyle" in r]
    assert text_reqs, "no updateTextStyle requests were generated"
    for ts_req in text_reqs:
        ts = ts_req["textStyle"]
        assert ts.get("fontSize", {}).get("magnitude", 0) > 0, "fontSize magnitude must be > 0"
        assert ts.get("weightedFontFamily", {}).get("fontFamily"), "weightedFontFamily.fontFamily must be set"
        fields = ts_req["fields"]
        assert "fontSize" in fields and "weightedFontFamily" in fields, (
            f"fields must declare fontSize + weightedFontFamily, got: {fields}"
        )


def test_dry_run_invariant_holds_for_all_v2_templates():
    """The ordering invariant must hold for every v2.0 production template, not just one."""
    checked = 0
    for tpl in sorted((ROOT / "templates").glob("*_v1.json")):
        theme = json.loads(tpl.read_text(encoding="utf-8"))
        if "blocks" not in theme:  # v2.0 production templates only
            continue
        paragraphs = bgm.build_paragraphs(theme)
        requests = bgm.build_requests(theme, paragraphs, doc_id="TEST")
        first_para, first_text = {}, {}
        for i, req in enumerate(requests):
            if "updateParagraphStyle" in req:
                r = req["updateParagraphStyle"]["range"]
                first_para.setdefault((r["startIndex"], r["endIndex"]), i)
            elif "updateTextStyle" in req:
                r = req["updateTextStyle"]["range"]
                first_text.setdefault((r["startIndex"], r["endIndex"]), i)
        for rng, text_i in first_text.items():
            assert rng in first_para and first_para[rng] < text_i, (
                f"{tpl.name}: paragraph style must precede text style for {rng}"
            )
        checked += 1
    assert checked > 0, "no v2.0 production templates (with blocks[]) were found to check"


if __name__ == "__main__":
    tests = [
        test_paragraph_style_precedes_text_style_per_range,
        test_text_runs_carry_font_size_and_family,
        test_dry_run_invariant_holds_for_all_v2_templates,
    ]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {t.__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
