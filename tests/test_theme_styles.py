"""B2: builder honours theme spacing per role; verifier compares size/spacing/margins/RGB (offline)."""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import build_golden_master as bgm  # noqa: E402
from verify_golden_master import TOLERANCES_PATH, check_styles_by_role  # noqa: E402

TOL = json.loads(TOLERANCES_PATH.read_text(encoding="utf-8"))


def load(name):
    return json.loads((ROOT / "templates" / name).read_text(encoding="utf-8"))


def para_requests(theme):
    paras = bgm.build_paragraphs(theme)
    reqs = bgm.build_requests(theme, paras, doc_id="TEST")
    by_range = [r["updateParagraphStyle"] for r in reqs if "updateParagraphStyle" in r]
    return list(zip(paras, by_range))


def test_line_spacing_follows_theme_not_hardcoded_115():
    theme = load("resume_contemporary_professional_v1.json")
    theme["typography"]["line_spacing"] = 1.3
    for row, req in para_requests(theme):
        if row[4] in ("name", "headline", "h1", "role_meta", "skills_body", "body"):
            assert req["paragraphStyle"]["lineSpacing"] == 130, (row[4], req["paragraphStyle"]["lineSpacing"])


def test_role_title_margin_top_is_space_above_not_below():
    theme = load("resume_contemporary_professional_v1.json")
    rt = next(b for b in theme["blocks"] if b["block_id"] == "experience_section")["visualConfig"]["role_title"]
    h2 = next(req for row, req in para_requests(theme) if row[4] == "h2")["paragraphStyle"]
    assert h2["spaceAbove"]["magnitude"] == rt["margin_top_pt"]
    assert h2["spaceBelow"]["magnitude"] != rt["margin_top_pt"]


def test_missing_visual_config_does_not_raise():
    theme = load("resume_contemporary_professional_v1.json")
    for block in theme["blocks"]:
        block.pop("visualConfig", None)
    assert para_requests(theme)


def test_ksc_bullets_use_criteria_bullet_config():
    theme = load("ksc_standard_v2.json")
    kb = next(b for b in theme["blocks"] if b["block_id"] == "criteria_responses")["visualConfig"]["bullet"]
    assert bgm.role_style(theme, "bullet")["line_spacing"] == round(kb["line_spacing"] * 100)


def simulate_doc(theme):
    """Doc JSON as Google returns it after a correct build."""
    page = theme["page"]
    doc = {"documentStyle": {
        f"margin{s.capitalize()}": {"magnitude": bgm.cm_to_pt(page[f"margin_{s}_cm"]), "unit": "PT"}
        for s in ("top", "bottom", "left", "right")
    }, "body": {"content": []}}
    for text, _ns, _b, _i, role in bgm.build_paragraphs(theme):
        st = bgm.role_style(theme, role)
        doc["body"]["content"].append({"paragraph": {
            "paragraphStyle": {"lineSpacing": st["line_spacing"],
                               "spaceAbove": {"magnitude": st["space_above"]},
                               "spaceBelow": {"magnitude": st["space_below"]}},
            "elements": [{"textRun": {"content": text + "\n", "textStyle": {
                "fontSize": {"magnitude": st["font_size"]},
                "foregroundColor": {"color": {"rgbColor": bgm.hex_to_rgb(st["color"])}},
            }}}],
        }})
    return doc


def test_verifier_passes_a_correct_build():
    theme = load("resume_contemporary_professional_v1.json")
    ok, problems = check_styles_by_role(simulate_doc(theme), theme, TOL)
    assert ok, problems


def test_verifier_catches_size_spacing_margin_and_colour_drift():
    theme = load("resume_contemporary_professional_v1.json")
    doc = simulate_doc(theme)
    bad = copy.deepcopy(doc)
    bad["documentStyle"]["marginLeft"]["magnitude"] += 5
    first = bad["body"]["content"][0]["paragraph"]
    first["paragraphStyle"]["lineSpacing"] = 200
    run = first["elements"][0]["textRun"]["textStyle"]
    run["fontSize"]["magnitude"] += 3
    run["foregroundColor"]["color"]["rgbColor"] = {"red": 1.0, "green": 0.0, "blue": 0.0}
    ok, problems = check_styles_by_role(bad, theme, TOL)
    text = " | ".join(problems)
    assert not ok
    for needle in ("margin left", "lineSpacing", "fontSize", "colour"):
        assert needle in text, needle
