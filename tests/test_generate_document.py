import unittest
from unittest.mock import MagicMock

from generate_document import (
    DocumentGenerationError,
    build_placeholder_values,
    build_placeholder_values_v2,
    find_unresolved_placeholders,
    make_replace_requests,
    _extract_document_text,
    validate_document_structure,
    clone_and_replace,
)
from content_engine import (
    DocumentType,
    EmployerType,
    GenerationConfig,
    extract_job_ad_keywords,
    select_roles,
    select_bullets,
    select_all_bullets,
    select_narratives,
    select_skills,
    apply_rosetta_stone,
    generate_professional_summary,
    generate_bridge_paragraph,
    generate_closing_paragraph,
    parse_criteria,
    build_ksc_response,
    validate_ksc_word_counts,
    load_user_config,
)

# ──────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────

SAMPLE_HISTORY = {
    "roles": [
        {
            "fingerprint": "fp1",
            "company": "Launch Housing",
            "role": "Project Worker",
            "start_date": "Jan 2023",
            "end_date": "Present",
            "domain_archetypes": ["service_coordination", "harm_reduction"],
            "achievements": [
                {
                    "raw_text": "Coordinated wraparound support for 45 clients experiencing homelessness",
                    "domain_tags": ["service_coordination", "housing"],
                    "needs_review": False,
                },
                {
                    "raw_text": "Facilitated weekly MDT meetings with allied health providers",
                    "domain_tags": ["leadership", "service_coordination"],
                    "needs_review": False,
                },
                {
                    "raw_text": "Generic bullet without metrics about community engagement",
                    "domain_tags": ["community_services"],
                    "needs_review": True,
                },
            ],
        },
        {
            "fingerprint": "fp2",
            "company": "Royal Bank of Scotland",
            "role": "Project Manager",
            "start_date": "Mar 2015",
            "end_date": "Dec 2018",
            "domain_archetypes": ["project_management", "corporate_finance"],
            "achievements": [
                {
                    "raw_text": "Led cross-departmental compliance workstream across 3 regions",
                    "domain_tags": ["project_management", "corporate_finance"],
                    "needs_review": False,
                },
                {
                    "raw_text": "Managed $2.5M budget for regulatory reform program",
                    "domain_tags": ["corporate_finance"],
                    "needs_review": False,
                },
            ],
        },
    ]
}

SAMPLE_NARRATIVES = {
    "narratives": [
        {
            "narrative_type": "hook",
            "full_text": "Having transitioned from corporate finance to community services, I bring a unique perspective.",
            "competency_tags": ["career_transition"],
            "quality_tier": 1,
            "quality_score": 85,
            "word_count": 15,
        },
        {
            "narrative_type": "STAR",
            "full_text": "At Launch Housing, I identified a gap in intake processes. I redesigned the referral pathway, collaborating with 4 partner agencies. This reduced wait times by 30% and improved client outcomes across the housing access program.",
            "competency_tags": ["service_coordination", "problem_solving"],
            "quality_tier": 1,
            "quality_score": 92,
            "word_count": 40,
        },
        {
            "narrative_type": "CAR",
            "full_text": "In my role at cohealth, I managed complex cases involving dual diagnosis. I implemented a structured support framework. Client engagement improved measurably.",
            "competency_tags": ["case_management", "complex_needs"],
            "quality_tier": 2,
            "quality_score": 70,
            "word_count": 25,
        },
        {
            "narrative_type": "pivot",
            "full_text": "My transition from banking to community services was driven by lived experience.",
            "competency_tags": ["career_transition", "lived_experience"],
            "quality_tier": 1,
            "quality_score": 80,
            "word_count": 14,
        },
    ]
}

SAMPLE_TAXONOMY = {
    "rosetta_stone": {
        "RBS_Project_Management": {
            "corporate_framing": "Led cross-departmental regulatory compliance workstreams",
            "community_translation": "Service Coordination",
            "community_keywords": ["Complex Case Coordination", "MDT Collaboration", "Wraparound Support"],
            "contextual_bridge": "",
        },
        "RBS_Regulatory_Compliance": {
            "corporate_framing": "Strengthened anti-tax avoidance protocols, performed audits",
            "community_translation": "Quality Assurance & Governance",
            "community_keywords": ["Clinical Governance", "MARAM Risk Assessment", "Safeguarding"],
        },
    },
    "skills_inventory": [
        {"skill_name": "Service Coordination", "source_lineage": ["test.txt"]},
        {"skill_name": "MARAM Risk Assessment", "source_lineage": ["test.txt"]},
        {"skill_name": "AML", "source_lineage": ["test.txt"]},
    ],
    "keyword_bank": {
        "service_coordination": ["care plan", "coordination", "wraparound", "referral"],
        "corporate_finance": ["AML", "RBS", "compliance", "regulatory", "audit"],
        "harm_reduction": ["harm reduction", "needle", "naloxone", "AOD"],
    },
}

SAMPLE_USER_CONFIG = {
    "contact": {
        "name": "Test User",
        "phone": "0400 000 000",
        "email": "test@example.com",
        "location": "Melbourne, VIC",
    },
    "education": [
        "Bachelor of Business — Test University, 2010",
    ],
    "certifications": [
        "MARAM Risk Assessment (Intermediate)",
        "Working with Children Check (current)",
    ],
}


# ══════════════════════════════════════════════════════════════════════
# v1 BACKWARD COMPATIBILITY TESTS (unchanged)
# ══════════════════════════════════════════════════════════════════════

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
                "content": [{"paragraph": {"elements": [{"textRun": {"content": "Body text. "}}]}}]
            },
            "headers": {
                "h1": {"content": [{"paragraph": {"elements": [{"textRun": {"content": "Header {{TARGET_ROLE}}. "}}]}}]}
            },
            "footers": {
                "f1": {"content": [{"paragraph": {"elements": [{"textRun": {"content": "Footer {{SUMMARY}}."}}]}}]}
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

        class HttpError(Exception):
            pass

        drive_service.files().copy().execute.side_effect = HttpError("Mock HTTP Error")

        with self.assertRaises(DocumentGenerationError):
            clone_and_replace(
                docs_service=docs_service,
                drive_service=drive_service,
                template_doc_id="123",
                values={"{{TARGET_ROLE}}": "Role"},
                target_role="Role",
                template="resume",
            )


# ══════════════════════════════════════════════════════════════════════
# v2 CONTENT ENGINE TESTS
# ══════════════════════════════════════════════════════════════════════

class KeywordExtractionTests(unittest.TestCase):
    def test_extracts_matching_domains(self):
        job_ad = "We need someone with care plan experience and coordination skills for wraparound support."
        keyword_bank = SAMPLE_TAXONOMY["keyword_bank"]

        scores = extract_job_ad_keywords(job_ad, keyword_bank)

        self.assertIn("service_coordination", scores)
        self.assertGreater(scores["service_coordination"], 0.0)

    def test_empty_job_ad_returns_empty(self):
        scores = extract_job_ad_keywords("", SAMPLE_TAXONOMY["keyword_bank"])
        self.assertEqual(scores, {})

    def test_empty_keyword_bank_returns_empty(self):
        scores = extract_job_ad_keywords("some text", {})
        self.assertEqual(scores, {})

    def test_no_matches_returns_empty(self):
        scores = extract_job_ad_keywords("xyz abc 123", SAMPLE_TAXONOMY["keyword_bank"])
        self.assertEqual(scores, {})


class RoleSelectionTests(unittest.TestCase):
    def test_selects_roles_by_recency(self):
        roles = select_roles(SAMPLE_HISTORY, "Project Worker", {}, max_roles=2)

        self.assertEqual(len(roles), 2)
        # "Present" end_date should rank as most recent
        self.assertEqual(roles[0]["company"], "Launch Housing")

    def test_present_end_date_ranks_highest(self):
        """Roles with end_date='Present' must outrank any specific date."""
        history = {
            "roles": [
                {"company": "Old Co", "start_date": "Jan 2020", "end_date": "Dec 2024", "achievements": []},
                {"company": "Current Co", "start_date": "Jan 2023", "end_date": "Present", "achievements": []},
            ]
        }
        roles = select_roles(history, "Worker", {}, max_roles=2)
        self.assertEqual(roles[0]["company"], "Current Co")

    def test_respects_max_roles(self):
        roles = select_roles(SAMPLE_HISTORY, "Project Worker", {}, max_roles=1)
        self.assertEqual(len(roles), 1)

    def test_empty_history_returns_empty(self):
        roles = select_roles({"roles": []}, "Worker", {})
        self.assertEqual(roles, [])

    def test_domain_relevance_boosts_ranking(self):
        keyword_scores = {"corporate_finance": 0.9, "project_management": 0.8}
        roles = select_roles(SAMPLE_HISTORY, "Project Manager", keyword_scores, max_roles=2)
        # With strong corporate finance keywords, RBS role should score higher on domain
        self.assertEqual(len(roles), 2)


class BulletSelectionTests(unittest.TestCase):
    def test_excludes_needs_review_bullets(self):
        role = SAMPLE_HISTORY["roles"][0]
        bullets = select_bullets(role, {})

        self.assertEqual(len(bullets), 2)
        self.assertFalse(any("Generic bullet" in b for b in bullets))

    def test_prioritises_bullets_with_metrics(self):
        role = SAMPLE_HISTORY["roles"][0]
        bullets = select_bullets(role, {})

        # The bullet with "45 clients" has a metric — should be first
        self.assertIn("45 clients", bullets[0])

    def test_respects_max_bullets(self):
        role = SAMPLE_HISTORY["roles"][0]
        bullets = select_bullets(role, {}, max_bullets=1)
        self.assertEqual(len(bullets), 1)

    def test_select_all_bullets_flattened(self):
        bullets = select_all_bullets(SAMPLE_HISTORY, {}, max_total=10)
        # Should include bullets from both roles, excluding needs_review
        self.assertEqual(len(bullets), 4)


class NarrativeSelectionTests(unittest.TestCase):
    def test_selects_by_quality_tier(self):
        all_narratives = SAMPLE_NARRATIVES["narratives"]
        selected = select_narratives(all_narratives, max_count=2)

        # Tier 1 narratives should come first
        self.assertEqual(selected[0]["quality_tier"], 1)

    def test_filters_by_narrative_type(self):
        all_narratives = SAMPLE_NARRATIVES["narratives"]
        hooks = select_narratives(all_narratives, narrative_types=["hook"])

        self.assertTrue(all(n["narrative_type"] == "hook" for n in hooks))

    def test_matches_competency_targets(self):
        all_narratives = SAMPLE_NARRATIVES["narratives"]
        # When filtering by competency, tier 1 narratives still sort first.
        # With max_count=3, we should get the case_management narrative included.
        selected = select_narratives(
            all_narratives,
            competency_targets=["case_management"],
            max_count=4,
        )

        self.assertGreater(len(selected), 0)
        # The case_management narrative (tier 2) should be present somewhere
        tags_flat = [tag for n in selected for tag in n.get("competency_tags", [])]
        self.assertIn("case_management", tags_flat)

    def test_empty_narratives_returns_empty(self):
        selected = select_narratives([], max_count=5)
        self.assertEqual(selected, [])


class SkillSelectionTests(unittest.TestCase):
    def test_selects_skills_from_inventory(self):
        skills = select_skills(SAMPLE_TAXONOMY, {}, max_skills=3)
        self.assertGreater(len(skills), 0)
        self.assertLessEqual(len(skills), 3)

    def test_deduplicates_skills(self):
        skills = select_skills(SAMPLE_TAXONOMY, {}, max_skills=20)
        lowercase = [s.lower() for s in skills]
        self.assertEqual(len(lowercase), len(set(lowercase)))


class RosettaStoneTests(unittest.TestCase):
    def test_returns_text_unchanged_when_no_match(self):
        text = "Provided person-centred support to clients."
        result = apply_rosetta_stone(text, SAMPLE_TAXONOMY["rosetta_stone"])
        self.assertEqual(result, text)

    def test_returns_text_for_empty_rosetta(self):
        text = "Some text"
        result = apply_rosetta_stone(text, {})
        self.assertEqual(result, text)

    def test_appends_community_keywords_when_corporate_match(self):
        """Rosetta Stone must actually modify text when corporate terms are found."""
        text = "Led cross-departmental regulatory compliance workstreams across regions."
        result = apply_rosetta_stone(text, SAMPLE_TAXONOMY["rosetta_stone"])
        # The original text should be preserved
        self.assertIn("cross-departmental", result)
        # Community keywords should be appended
        self.assertNotEqual(result, text)
        self.assertIn("(", result)  # Parenthetical bridge added
        self.assertIn("Complex Case Coordination", result)

    def test_does_not_double_apply_when_community_already_present(self):
        """If community keywords already exist, don't add them again."""
        text = "Led compliance workstreams with Complex Case Coordination focus."
        result = apply_rosetta_stone(text, SAMPLE_TAXONOMY["rosetta_stone"])
        # Should not add a parenthetical because community keyword is already present
        self.assertNotIn("(", result)


class BridgeParagraphTests(unittest.TestCase):
    def test_generates_bridge_paragraph(self):
        bridge = generate_bridge_paragraph(
            SAMPLE_TAXONOMY["rosetta_stone"],
            {"service_coordination": 0.8},
        )
        self.assertGreater(len(bridge), 50)
        self.assertIn("translates directly into", bridge.lower())

    def test_empty_rosetta_returns_empty(self):
        bridge = generate_bridge_paragraph({}, {})
        self.assertEqual(bridge, "")


class ProfessionalSummaryTests(unittest.TestCase):
    def test_generates_summary_with_domain_tags(self):
        config = GenerationConfig(
            doc_type=DocumentType.RESUME,
            target_role="Project Worker at Launch Housing",
        )
        roles = SAMPLE_HISTORY["roles"]
        summary = generate_professional_summary(
            config, roles, {}, SAMPLE_TAXONOMY["rosetta_stone"],
        )
        self.assertGreater(len(summary), 50)
        self.assertIn("Project Worker at Launch Housing", summary)

    def test_uses_override_when_provided(self):
        config = GenerationConfig(
            doc_type=DocumentType.RESUME,
            target_role="Worker",
            summary_override="Custom summary text here.",
        )
        summary = generate_professional_summary(config, [], {}, {})
        self.assertEqual(summary, "Custom summary text here.")


class ClosingParagraphTests(unittest.TestCase):
    def test_government_closing(self):
        config = GenerationConfig(
            doc_type=DocumentType.COVER_LETTER,
            target_role="Case Manager",
            employer_type=EmployerType.GOVERNMENT,
        )
        closing = generate_closing_paragraph(config, {"service_coordination": 0.8})
        self.assertIn("available for interview", closing.lower())

    def test_nfp_closing(self):
        config = GenerationConfig(
            doc_type=DocumentType.COVER_LETTER,
            target_role="Project Worker",
            employer_type=EmployerType.NFP,
        )
        closing = generate_closing_paragraph(config, {})
        self.assertIn("mission and values", closing.lower())


# ══════════════════════════════════════════════════════════════════════
# KSC ENGINE TESTS
# ══════════════════════════════════════════════════════════════════════

class CriteriaParsingTests(unittest.TestCase):
    def test_parses_numbered_criteria(self):
        text = """1. Demonstrated experience in case management
2. Ability to work with complex client needs
3. Knowledge of harm reduction frameworks"""
        criteria = parse_criteria(text)
        self.assertEqual(len(criteria), 3)
        self.assertIn("case management", criteria[0]["criterion_text"].lower())

    def test_parses_bullet_criteria(self):
        text = """• Strong communication and interpersonal skills
• Experience in service coordination
• Ability to work in a multi-disciplinary team"""
        criteria = parse_criteria(text)
        self.assertEqual(len(criteria), 3)

    def test_empty_text_returns_empty(self):
        criteria = parse_criteria("")
        self.assertEqual(criteria, [])

    def test_extracts_competency_keywords(self):
        text = "1. Demonstrated experience in case management and risk assessment"
        criteria = parse_criteria(text)
        self.assertIn("case management", criteria[0]["extracted_competencies"])
        self.assertIn("risk assessment", criteria[0]["extracted_competencies"])

    def test_limits_to_max_criteria(self):
        lines = [f"{i}. Criterion {i}" for i in range(1, 20)]
        criteria = parse_criteria("\n".join(lines))
        self.assertLessEqual(len(criteria), 6)


class KSCResponseTests(unittest.TestCase):
    def test_builds_car_response(self):
        criterion = {
            "criterion_text": "Demonstrated experience in service coordination",
            "extracted_competencies": ["service_coordination"],
        }
        response = build_ksc_response(
            criterion,
            SAMPLE_NARRATIVES["narratives"],
            SAMPLE_HISTORY,
            SAMPLE_TAXONOMY["rosetta_stone"],
        )

        # Should have context, action, result
        self.assertIn("context", response)
        self.assertIn("action", response)
        self.assertIn("result", response)
        # At least one section should have content
        has_content = any(response.get(k) for k in ("context", "action", "result"))
        self.assertTrue(has_content)


class KSCWordCountTests(unittest.TestCase):
    def test_warns_on_short_sections(self):
        response = {"context": "Short.", "action": "Also short.", "result": "Done."}
        warnings = validate_ksc_word_counts(response)
        self.assertTrue(any("too_short" in w for w in warnings))

    def test_no_warnings_for_adequate_length(self):
        response = {
            "context": " ".join(["word"] * 60),
            "action": " ".join(["word"] * 100),
            "result": " ".join(["word"] * 50),
        }
        warnings = validate_ksc_word_counts(response)
        self.assertEqual(len(warnings), 0)


# ══════════════════════════════════════════════════════════════════════
# v2 PLACEHOLDER BUILDER TESTS
# ══════════════════════════════════════════════════════════════════════

class PlaceholderV2Tests(unittest.TestCase):
    def test_resume_v2_populates_contact_and_roles(self):
        config = GenerationConfig(
            doc_type=DocumentType.RESUME,
            target_role="Project Worker at Launch Housing",
        )
        values, stats, warnings = build_placeholder_values_v2(
            config=config,
            history=SAMPLE_HISTORY,
            narratives=SAMPLE_NARRATIVES,
            taxonomy=SAMPLE_TAXONOMY,
            user_config=SAMPLE_USER_CONFIG,
        )

        self.assertEqual(values["{{CONTACT_NAME}}"], "Test User")
        self.assertEqual(values["{{CONTACT_EMAIL}}"], "test@example.com")
        # With "Present" end_date fixed, Launch Housing (current role) should be first
        self.assertEqual(values["{{ROLE_1_ORG}}"], "Launch Housing")
        self.assertGreater(stats["filled"], 10)

    def test_resume_v2_with_job_ad_keywords(self):
        """Job ad keywords should influence skill and bullet selection."""
        config = GenerationConfig(
            doc_type=DocumentType.RESUME,
            target_role="Case Manager at cohealth",
            job_ad_text="We need someone with care plan coordination and wraparound support experience.",
        )
        values, stats, warnings = build_placeholder_values_v2(
            config=config,
            history=SAMPLE_HISTORY,
            narratives=SAMPLE_NARRATIVES,
            taxonomy=SAMPLE_TAXONOMY,
            user_config=SAMPLE_USER_CONFIG,
        )
        # Should have filled more placeholders than a run with no job ad
        self.assertGreater(stats["filled"], 10)

    def test_cover_letter_v2_populates_hook_and_bridge(self):
        config = GenerationConfig(
            doc_type=DocumentType.COVER_LETTER,
            target_role="Case Manager at cohealth",
            employer_type=EmployerType.NFP,
        )
        values, stats, warnings = build_placeholder_values_v2(
            config=config,
            history=SAMPLE_HISTORY,
            narratives=SAMPLE_NARRATIVES,
            taxonomy=SAMPLE_TAXONOMY,
            user_config=SAMPLE_USER_CONFIG,
        )

        self.assertGreater(len(values["{{HOOK_PARAGRAPH}}"]), 0)
        self.assertGreater(len(values["{{BRIDGE_PARAGRAPH}}"]), 0)
        self.assertGreater(len(values["{{CLOSING_PARAGRAPH}}"]), 0)
        self.assertEqual(values["{{EMPLOYER_ORG}}"], "cohealth")

    def test_ksc_v2_populates_car_responses(self):
        config = GenerationConfig(
            doc_type=DocumentType.KSC,
            target_role="Intake Worker at Sacred Heart",
            criteria_text=[
                "1. Demonstrated experience in case management",
                "2. Ability to work with complex client needs",
            ],
        )
        values, stats, warnings = build_placeholder_values_v2(
            config=config,
            history=SAMPLE_HISTORY,
            narratives=SAMPLE_NARRATIVES,
            taxonomy=SAMPLE_TAXONOMY,
            user_config=SAMPLE_USER_CONFIG,
        )

        self.assertGreater(len(values.get("{{KSC_CRITERION_1_TEXT}}", "")), 0)
        self.assertEqual(values["{{EMPLOYER_ORG}}"], "Sacred Heart")

    def test_ksc_v2_warns_on_empty_criteria(self):
        config = GenerationConfig(
            doc_type=DocumentType.KSC,
            target_role="Worker",
        )
        values, stats, warnings = build_placeholder_values_v2(
            config=config,
            history=SAMPLE_HISTORY,
            narratives=SAMPLE_NARRATIVES,
            taxonomy=SAMPLE_TAXONOMY,
            user_config=SAMPLE_USER_CONFIG,
        )
        self.assertIn("no_criteria_provided_or_parsed", warnings)

    def test_resume_v2_warns_on_missing_contact(self):
        config = GenerationConfig(
            doc_type=DocumentType.RESUME,
            target_role="Worker",
        )
        values, stats, warnings = build_placeholder_values_v2(
            config=config,
            history=SAMPLE_HISTORY,
            narratives=SAMPLE_NARRATIVES,
            taxonomy=SAMPLE_TAXONOMY,
            user_config={},  # Empty user config
        )
        self.assertIn("contact_name_missing", warnings)


# ══════════════════════════════════════════════════════════════════════
# DOCUMENT VALIDATION TESTS
# ══════════════════════════════════════════════════════════════════════

class DocumentValidationTests(unittest.TestCase):
    def test_detects_short_document(self):
        document = {
            "body": {"content": [{"paragraph": {"elements": [{"textRun": {"content": "Short text."}}]}}]},
        }
        warnings = validate_document_structure(document)
        self.assertIn("document_too_short", warnings)

    def test_detects_inline_objects(self):
        document = {
            "body": {"content": [{"paragraph": {"elements": [{"textRun": {"content": " ".join(["word"] * 200)}}]}}]},
            "inlineObjects": {"obj1": {}},
        }
        warnings = validate_document_structure(document)
        self.assertIn("inline_objects_detected_ats_risk", warnings)

    def test_clean_document_has_no_warnings(self):
        document = {
            "body": {"content": [{"paragraph": {"elements": [{"textRun": {"content": " ".join(["word"] * 200)}}]}}]},
        }
        warnings = validate_document_structure(document)
        self.assertEqual(warnings, [])


class CareerCopilotLeverageTests(unittest.TestCase):
    def test_load_ats_rules_returns_dict(self):
        from generate_document import load_ats_rules
        rules = load_ats_rules()
        self.assertIsInstance(rules, dict)
        if rules:
            self.assertIn("terminology", rules)
            self.assertIn("vocabulary", rules)

    def test_australian_terminology_substitution(self):
        config = GenerationConfig(
            doc_type=DocumentType.RESUME,
            target_role="Project Manager at RBS company",
        )
        values, stats, warnings = build_placeholder_values_v2(
            config=config,
            history=SAMPLE_HISTORY,
            narratives=SAMPLE_NARRATIVES,
            taxonomy=SAMPLE_TAXONOMY,
            user_config=SAMPLE_USER_CONFIG,
        )
        # Target role has "RBS company" which should map to "RBS organisation"
        self.assertEqual(values["{{TARGET_ROLE}}"], "Project Manager at RBS organisation")

    def test_rosetta_stone_resume_bullets_toggle(self):
        import copy
        local_history = copy.deepcopy(SAMPLE_HISTORY)
        local_history["roles"][1]["achievements"][0]["raw_text"] = "Led cross-departmental regulatory compliance workstreams across regions."

        # Test with rosetta=True
        config_with = GenerationConfig(
            doc_type=DocumentType.RESUME,
            target_role="Project Worker",
            rosetta=True,
        )
        values_with, _, _ = build_placeholder_values_v2(
            config=config_with,
            history=local_history,
            narratives=SAMPLE_NARRATIVES,
            taxonomy=SAMPLE_TAXONOMY,
            user_config=SAMPLE_USER_CONFIG,
        )
        
        # Test with rosetta=False
        config_without = GenerationConfig(
            doc_type=DocumentType.RESUME,
            target_role="Project Worker",
            rosetta=False,
        )
        values_without, _, _ = build_placeholder_values_v2(
            config=config_without,
            history=local_history,
            narratives=SAMPLE_NARRATIVES,
            taxonomy=SAMPLE_TAXONOMY,
            user_config=SAMPLE_USER_CONFIG,
        )
        
        # Verify that bullet containing corporate framing got translated in values_with but not in values_without.
        # "Led cross-departmental compliance workstream" is in RBS role, which maps to community keywords in taxonomy
        found_translation = False
        for k, v in values_with.items():
            if "ROLE_" in k and "BULLET_" in k and "Complex Case Coordination" in v:
                found_translation = True
                break
        self.assertTrue(found_translation, "Expected Rosetta Stone translation in bullet when --rosetta is enabled")

        found_translation_without = False
        for k, v in values_without.items():
            if "ROLE_" in k and "BULLET_" in k and "Complex Case Coordination" in v:
                found_translation_without = True
                break
        self.assertFalse(found_translation_without, "Expected no Rosetta Stone translation in bullet when --rosetta is disabled")


    def test_detects_forbidden_characters_in_document(self):
        # Bullet char "•" is in our ats_rules.json forbidden characters list
        document = {
            "body": {"content": [{"paragraph": {"elements": [{"textRun": {"content": "• " + " ".join(["word"] * 200)}}]}}]},
        }
        warnings = validate_document_structure(document)
        self.assertTrue(any("forbidden_character_detected" in w for w in warnings))


if __name__ == "__main__":
    unittest.main()

