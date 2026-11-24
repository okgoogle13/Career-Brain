"""Unit tests for tools/export_clean_corpus.py (Stage 1 scrubber & packager)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import export_clean_corpus as ecc  # noqa: E402


def test_classify_excludes_third_party_referees_templates_and_megafiles():
    assert ecc.classify_file("cover_letters__Kassies_Cover_Letter_NPU.txt")[0] == "exclude"
    assert ecc.classify_file("references__Nishant_Dougall_References_2025.txt")[0] == "exclude"
    assert ecc.classify_file("resumes__Nishant_Dougall_References_Launch.txt")[0] == "exclude"
    assert ecc.classify_file("resumes__CV_Template_20140621.txt")[0] == "exclude"
    assert ecc.classify_file("resumes__harvested_EUC_LFT_UDS_16.9.25.txt")[0] == "exclude"
    assert ecc.classify_file("cover_letters__final_combined_resumes.txt")[0] == "exclude"
    assert ecc.classify_file("knowledge__10_selection_criteria_examples.txt")[0] == "exclude"


def test_classify_routes_own_docs_to_correct_bundles():
    assert ecc.classify_file("ksc__20240526_Flat_Out_KSC.txt")[0] == "ksc_letters"
    assert ecc.classify_file("cover_letters__20250120_CSW_Cohealth_Cover_Letter.txt")[0] == "ksc_letters"
    assert ecc.classify_file("resumes__20240626_PLC_Home_Care_Support_Worker_Role_-_Responses_to_Key_Selection_Criteria.txt")[0] == "ksc_letters"
    assert ecc.classify_file("resumes__Nishant_Dougall_Letter_1_GREEN.txt")[0] == "ksc_letters"
    assert ecc.classify_file("knowledge__IAP_Launch_Interview_Prep_Responses.txt")[0] == "ksc_letters"
    assert ecc.classify_file("resumes__20250121_CSW_Cohealth.txt")[0] == "resumes"
    assert ecc.classify_file("knowledge__Master_Resume_with_subtypes.txt")[0] == "resumes"


def test_run_export_scrubs_pii_drops_red_tier_and_deduplicates(tmp_path: Path):
    proc = tmp_path / "processed"
    out = tmp_path / "out"
    proc.mkdir()

    ksc_text = (
        "Contact: user@example.com | 0412 345 678 | 12 Example Street, Melbourne VIC 3000.\n"
        "Conducted over 400 intake interviews at Diamond Valley Community Support."
    )
    (proc / "ksc__20240526_Flat_Out_KSC.txt").write_text(ksc_text, encoding="utf-8")
    (proc / "ksc__harvested_Key_Selection_Criteria_Responses__20240526_Flat_Out_KSC.docx__Converted.txt").write_text(
        ksc_text + " ", encoding="utf-8"
    )
    (proc / "cover_letters__Kassies_Cover_Letter.txt").write_text("Third party letter.", encoding="utf-8")
    (proc / "resumes__hidden_lab_report.txt").write_text(
        "Pathology Specimen Creatinine Medicare 1234 56789 1", encoding="utf-8"
    )
    (proc / "resumes__20250121_CSW_Cohealth.txt").write_text(
        "Community Support Worker at DVCS. Email: user@example.com", encoding="utf-8"
    )

    summary = ecc.run_export(processed_dir=proc, out_dir=out, dry_run=False)

    assert summary["excluded_count"] == 2
    assert summary["bundles"]["ksc_letters"]["kept_unique"] == 1
    assert summary["bundles"]["ksc_letters"]["deduplicated"] == 1
    assert summary["bundles"]["ksc_letters"]["verify_issues"] == []
    assert summary["bundles"]["ksc_letters"]["kept_files"][0]["filename"] == "ksc__20240526_Flat_Out_KSC.txt"

    assert summary["bundles"]["resumes"]["kept_unique"] == 1
    assert summary["bundles"]["resumes"]["verify_issues"] == []

    bundle_text = (out / "own_ksc_and_letters.local.md").read_text(encoding="utf-8")
    assert "user@example.com" not in bundle_text
    assert "0412 345 678" not in bundle_text
    assert "12 Example Street" not in bundle_text
    assert "[[REDACTED_SENSITIVE_DATA]]" in bundle_text
    assert "Diamond Valley Community Support" in bundle_text
