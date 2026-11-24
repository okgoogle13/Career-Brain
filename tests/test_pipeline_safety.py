"""Stage A1 safety tests: error log, dry-run isolation, policy gate, null on failure."""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
ENGINE_FIXTURES = Path(__file__).parent / "fixtures" / "engines"

import ai_policy  # noqa: E402
import engine_io  # noqa: E402


class ErrorLogTests(unittest.TestCase):
    def test_append_writes_header_and_entries_and_keeps_prior_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "parsing_errors.log"
            log_path.write_text("earlier\n", encoding="utf-8")
            with patch.object(engine_io, "ERROR_LOG", log_path):
                engine_io.append_errors("run-1", ["e1", "e2"])
            self.assertEqual(log_path.read_text(encoding="utf-8"), "earlier\n### run_id=run-1\ne1\ne2\n")

    def test_no_entries_leaves_log_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "parsing_errors.log"
            log_path.write_text("", encoding="utf-8")
            with patch.object(engine_io, "ERROR_LOG", log_path):
                engine_io.append_errors("run-1", [])
            self.assertEqual(log_path.read_text(encoding="utf-8"), "")


class EngineValidationTests(unittest.TestCase):
    @staticmethod
    def _history(bullet_lineage):
        return {"generated_at": "x", "roles": [{
            "fingerprint": "f", "company": "C", "role": "R", "start_date": "2020", "end_date": "2021",
            "achievements": [{"raw_text": "Did a meaningful thing at work", "source_lineage": bullet_lineage}],
            "source_lineage": ["a.txt"],
        }]}

    def _validate(self, data):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "career_history.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            engine_io.validate_engine(path)

    def test_valid_lineage_passes(self):
        self._validate(self._history("a.txt"))

    def test_empty_source_lineage_fails_validation(self):
        with self.assertRaisesRegex(ValueError, "source_lineage"):
            self._validate(self._history(""))


class PolicyGateTests(unittest.TestCase):
    def test_red_tier_text_is_blocked(self):
        with patch.dict(os.environ, {"CB_ALLOW_RED_TIER": ""}):
            self.assertIsNone(ai_policy.policy_check("my TFN: 123 456 789", "ksc_tailoring"))
            self.assertIsNone(ai_policy.policy_check("key AIza" + "A" * 35, "ksc_tailoring"))

    def test_red_tier_allowed_only_with_explicit_flag(self):
        with patch.dict(os.environ, {"CB_ALLOW_RED_TIER": "1"}):
            out = ai_policy.policy_check("my TFN: 123 456 789", "ksc_tailoring")
        self.assertIsNotNone(out)
        self.assertNotIn("123 456 789", out)

    def test_contact_details_are_redacted_and_narrative_kept(self):
        text = "Call 0412 345 678 or jo@example.com. I supported peers with lived experience of mental illness."
        out = ai_policy.policy_check(text, "ksc_tailoring")
        self.assertNotIn("0412 345 678", out)
        self.assertNotIn("jo@example.com", out)
        self.assertIn("lived experience of mental illness", out)

    def test_unknown_purpose_is_blocked(self):
        self.assertIsNone(ai_policy.policy_check("plain text", "not_a_profile"))


class NoExternalCallTests(unittest.TestCase):
    def test_ksc_dry_run_never_calls_llm_and_reports_llm_used_false(self):
        from generate_document import main

        with tempfile.TemporaryDirectory() as tmp, \
                patch.dict(os.environ, {"GEMINI_API_KEY": "fake-key"}), \
                patch("content_engine._rewrite_car_with_llm", side_effect=AssertionError("LLM called")), \
                patch("generate_document.build_google_services", side_effect=AssertionError("Google called")):
            report_path = Path(tmp) / "report.json"
            code = main([
                "--type", "ksc", "--target", "Test Role at Test Org", "--dry-run",
                "--output-dir", str(ENGINE_FIXTURES),
                "--user-config", str(ENGINE_FIXTURES / "user_config.fixture.json"),
                "--out-report", str(report_path),
                "--criteria", "1. Demonstrated experience in case management.",
            ])
            report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(code, 0)
        self.assertFalse(report["llm_used"])

    def test_blocked_policy_means_no_client_is_built(self):
        import content_engine

        with patch.dict(os.environ, {"GEMINI_API_KEY": "fake-key"}), \
                patch("content_engine.policy_check", return_value=None), \
                patch("google.genai.Client", side_effect=AssertionError("client built")):
            out = content_engine._rewrite_car_with_llm("text", "criterion", [], {"roles": []})
        self.assertIsNone(out)


class NullOnFailureTests(unittest.TestCase):
    def test_failed_voice_call_scores_null_not_zero(self):
        import curate_narratives

        with patch.object(curate_narratives, "_call_gemini_voice", return_value=None):
            score, patterns, reason = curate_narratives.score_voice_authenticity({"full_text": "Some narrative."})
        self.assertIsNone(score)
        self.assertEqual(patterns, [])
        self.assertIsNone(reason)

    def test_voice_score_is_clamped(self):
        import curate_narratives

        with patch.object(curate_narratives, "_call_gemini_voice", return_value={"score": 9}):
            score, _, _ = curate_narratives.score_voice_authenticity({"full_text": "Some narrative."})
        self.assertEqual(score, 5)


if __name__ == "__main__":
    unittest.main()
