import unittest

from generate_document import (
    DocumentGenerationError,
    build_placeholder_values,
    find_unresolved_placeholders,
    make_replace_requests,
    _extract_document_text,
    clone_and_replace,
)
from unittest.mock import MagicMock


class PlaceholderMappingTests(unittest.TestCase):
    def test_resume_placeholders_use_deterministic_bullet_order(self):
        history = {
            "roles": [
                {
                    "achievements": [
                        {"raw_text": "Second bullet", "needs_review": False},
                        {"raw_text": "Needs metric", "needs_review": True},
                    ]
                },
                {
                    "achievements": [
                        {"raw_text": "First bullet", "needs_review": False},
                    ]
                },
            ]
        }
        narratives = {"narratives": []}

        values, stats = build_placeholder_values(
            template="resume",
            target_role="Peer Worker",
            history=history,
            narratives=narratives,
        )

        self.assertEqual(values["{{TARGET_ROLE}}"], "Peer Worker")
        self.assertIn("Peer Worker", values["{{SUMMARY}}"])
        self.assertEqual(values["{{BULLET_1}}"], "Second bullet")
        self.assertEqual(values["{{BULLET_2}}"], "First bullet")
        self.assertEqual(values["{{BULLET_3}}"], "")
        self.assertEqual(stats["filled"], 4)
        self.assertEqual(stats["blank"], 4)

    def test_required_resume_summary_missing_raises_deterministic_error(self):
        history = {"roles": [{"achievements": [{"raw_text": "Implemented intake improvements"}]}]}
        narratives = {"narratives": []}

        with self.assertRaisesRegex(DocumentGenerationError, "SUMMARY"):
            build_placeholder_values(
                template="resume",
                target_role="Intake Worker",
                history=history,
                narratives=narratives,
                require_summary=True,
            )

    def test_resume_requires_at_least_one_usable_bullet(self):
        history = {"roles": [{"achievements": [{"raw_text": "Needs metric", "needs_review": True}]}]}
        narratives = {"narratives": []}

        with self.assertRaisesRegex(DocumentGenerationError, "BULLET_1"):
            build_placeholder_values(
                template="resume",
                target_role="Intake Worker",
                history=history,
                narratives=narratives,
            )

    def test_cover_letter_uses_tiered_narratives_in_order(self):
        history = {"roles": []}
        narratives = {
            "narratives": [
                {
                    "full_text": "Tier 2 response",
                    "quality_tier": 2,
                    "word_count": 50,
                },
                {
                    "full_text": "Tier 1 response",
                    "quality_tier": 1,
                    "word_count": 20,
                },
            ]
        }

        values, stats = build_placeholder_values(
            template="cover_letter",
            target_role="Case Manager",
            history=history,
            narratives=narratives,
            summary="Short tailored summary",
        )

        self.assertEqual(values["{{KSC_RESPONSE_1}}"], "Tier 1 response")
        self.assertEqual(values["{{KSC_RESPONSE_2}}"], "Tier 2 response")
        self.assertEqual(values["{{KSC_RESPONSE_3}}"], "")
        self.assertEqual(stats["filled"], 4)

    def test_cover_letter_requires_at_least_one_response(self):
        history = {"roles": []}
        narratives = {"narratives": [{"full_text": ""}]}

        with self.assertRaisesRegex(DocumentGenerationError, "KSC_RESPONSE_1"):
            build_placeholder_values(
                template="cover_letter",
                target_role="Case Manager",
                history=history,
                narratives=narratives,
                summary="Short tailored summary",
            )

    def test_unresolved_placeholders_are_detected_from_document_text(self):
        text = "Filled {{TARGET_ROLE}} but left {{UNKNOWN_TOKEN}} and {{BULLET_9}}."

        unresolved = find_unresolved_placeholders(text)

        self.assertEqual(unresolved, ["{{BULLET_9}}", "{{TARGET_ROLE}}", "{{UNKNOWN_TOKEN}}"])

    def test_replace_requests_are_sorted_for_stable_batch_updates(self):
        values = {
            "{{BULLET_2}}": "Second",
            "{{TARGET_ROLE}}": "Role",
            "{{BULLET_1}}": "First",
        }

        requests = make_replace_requests(values)

        placeholders = [
            request["replaceAllText"]["containsText"]["text"]
            for request in requests
        ]
        self.assertEqual(placeholders, ["{{BULLET_1}}", "{{BULLET_2}}", "{{TARGET_ROLE}}"])



    def test_extract_document_text_includes_headers_and_footers(self):
        document = {
            "body": {
                "content": [{"textRun": {"content": "Body text. "}}]
            },
            "headers": {
                "h1": {"content": [{"textRun": {"content": "Header {{TARGET_ROLE}}. "}}]}
            },
            "footers": {
                "f1": {"content": [{"textRun": {"content": "Footer {{SUMMARY}}."}}]}
            }
        }
        text = _extract_document_text(document)
        self.assertIn("Body text.", text)
        self.assertIn("Header {{TARGET_ROLE}}.", text)
        self.assertIn("Footer {{SUMMARY}}.", text)
        unresolved = find_unresolved_placeholders(text)
        self.assertEqual(sorted(unresolved), ["{{SUMMARY}}", "{{TARGET_ROLE}}"])


class CloneAndReplaceTests(unittest.TestCase):
    def test_clone_and_replace_bubbles_http_error(self):
        drive_service = MagicMock()
        docs_service = MagicMock()
        
        # We need to simulate HttpError. We'll create a dummy class with the same name.
        class HttpError(Exception):
            pass
            
        # Make the drive service raise our mock HttpError
        drive_service.files().copy().execute.side_effect = HttpError("Mock HTTP Error")
        
        # We also need to patch type(exc).__name__ since our mock class is called HttpError
        # or we just rely on the name matching.
        
        with self.assertRaises(DocumentGenerationError):
            clone_and_replace(
                docs_service=docs_service,
                drive_service=drive_service,
                template_doc_id="123",
                values={"{{TARGET_ROLE}}": "Role"},
                target_role="Role",
                template="resume",
            )

if __name__ == "__main__":
    unittest.main()
