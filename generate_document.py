#!/usr/bin/env python3
"""
Phase 5 document generator for Career Brain.

Clones a Golden Master Google Doc, replaces fixed placeholders from existing
Career Brain JSON outputs, then writes a redacted run report.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE = Path(__file__).parent
OUTPUT = BASE / "output"
DEFAULT_CONFIG = BASE / "doc_templates.json"
DEFAULT_REPORT = OUTPUT / "doc_generation_report.json"

HISTORY_FILE = "career_history_enriched.json"
NARRATIVES_FILE = "ksc_curated.json"
TAXONOMY_FILE = "skills_and_taxonomy.json"

DOC_LINK_TEMPLATE = "https://docs.google.com/document/d/{doc_id}/edit"
PLACEHOLDER_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")

RESUME_BULLET_COUNT = 6
COVER_LETTER_RESPONSE_COUNT = 3

PLACEHOLDER_SCHEMA = {
    "resume": (
        "{{TARGET_ROLE}}",
        "{{SUMMARY}}",
        *(f"{{{{BULLET_{i}}}}}" for i in range(1, RESUME_BULLET_COUNT + 1)),
    ),
    "cover_letter": (
        "{{TARGET_ROLE}}",
        "{{SUMMARY}}",
        *(f"{{{{KSC_RESPONSE_{i}}}}}" for i in range(1, COVER_LETTER_RESPONSE_COUNT + 1)),
    ),
}

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("generate_document")


class DocumentGenerationError(RuntimeError):
    """Raised when Phase 5 cannot safely generate a document."""


def load_json(path: Path, *, required: bool = True) -> dict[str, Any]:
    if not path.exists():
        if required:
            raise DocumentGenerationError(f"Required JSON file missing: {path}")
        return {}
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        raise DocumentGenerationError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise DocumentGenerationError(f"Expected object at top level of {path}")
    return data


def load_source_data(output_dir: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    history = load_json(output_dir / HISTORY_FILE)
    narratives = load_json(output_dir / NARRATIVES_FILE)
    taxonomy = load_json(output_dir / TAXONOMY_FILE, required=False)
    return history, narratives, taxonomy


def load_template_config(path: Path) -> dict[str, Any]:
    config = load_json(path)
    if not config:
        raise DocumentGenerationError(f"Template config is empty: {path}")
    return config


def resolve_template_doc_id(
    config: dict[str, Any],
    template: str,
    template_variant: str | None = None,
    *,
    allow_placeholder: bool = False,
) -> str:
    entry = config.get(template)
    if entry is None:
        raise DocumentGenerationError(f"No template config found for '{template}'")

    if isinstance(entry, str):
        doc_id = entry
    elif isinstance(entry, dict):
        if template_variant:
            variants = entry.get("variants", {})
            variant = variants.get(template_variant)
            if isinstance(variant, str):
                doc_id = variant
            elif isinstance(variant, dict):
                doc_id = variant.get("template_doc_id", "")
            else:
                raise DocumentGenerationError(
                    f"No variant '{template_variant}' found for '{template}'"
                )
        else:
            doc_id = entry.get("template_doc_id", "")
    else:
        raise DocumentGenerationError(f"Invalid template config for '{template}'")

    if not doc_id or ("REPLACE_WITH" in doc_id and not allow_placeholder):
        raise DocumentGenerationError(
            f"Google Doc ID is not configured for '{template}'"
        )
    return doc_id


def _clean_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.split())


def _candidate_bullets(history: dict[str, Any]) -> list[str]:
    bullets: list[str] = []
    for role in history.get("roles", []):
        for achievement in role.get("achievements", []):
            if achievement.get("needs_review"):
                continue
            text = _clean_text(
                achievement.get("raw_text")
                or achievement.get("text")
                or achievement.get("achievement")
            )
            if text:
                bullets.append(text)
    return bullets


def _candidate_narratives(narratives: dict[str, Any]) -> list[str]:
    indexed = []
    for index, narrative in enumerate(narratives.get("narratives", [])):
        text = _clean_text(narrative.get("full_text"))
        if not text:
            continue
        tier = narrative.get("quality_tier", 99)
        try:
            tier_value = int(tier)
        except (TypeError, ValueError):
            tier_value = 99
        quality_score = narrative.get("quality_score", 0)
        word_count = narrative.get("word_count", 0)
        indexed.append((tier_value, -int(quality_score or 0), -int(word_count or 0), index, text))
    indexed.sort()
    return [item[-1] for item in indexed]


def _derive_summary(
    target_role: str,
    history: dict[str, Any],
    narratives: dict[str, Any],
    taxonomy: dict[str, Any] | None = None,
) -> str:
    tags: dict[str, int] = {}
    for role in history.get("roles", []):
        for achievement in role.get("achievements", []):
            for tag in achievement.get("domain_tags", []):
                if isinstance(tag, str) and tag:
                    tags[tag] = tags.get(tag, 0) + 1

    top_tags = [tag.replace("_", " ") for tag, _ in sorted(tags.items(), key=lambda item: (-item[1], item[0]))[:3]]
    if top_tags:
        return f"Targeting {target_role} roles with evidence across {', '.join(top_tags)}."

    if _candidate_bullets(history):
        return f"Targeting {target_role} roles with selected achievements from the Career Brain evidence base."

    if narratives.get("narratives"):
        return f"Targeting {target_role} roles with curated career evidence and selection criteria examples."

    if taxonomy and taxonomy:
        return f"Targeting {target_role} roles with a structured skills taxonomy and career evidence base."

    return ""


def _count_stats(values: dict[str, str]) -> dict[str, int]:
    filled = sum(1 for value in values.values() if value)
    blank = sum(1 for value in values.values() if not value)
    return {
        "total": len(values),
        "filled": filled,
        "blank": blank,
    }


def build_placeholder_values(
    *,
    template: str,
    target_role: str,
    history: dict[str, Any],
    narratives: dict[str, Any],
    taxonomy: dict[str, Any] | None = None,
    summary: str | None = None,
    require_summary: bool = False,
) -> tuple[dict[str, str], dict[str, int]]:
    if template not in PLACEHOLDER_SCHEMA:
        raise DocumentGenerationError(f"Unsupported template: {template}")
    if require_summary and not _clean_text(summary):
        raise DocumentGenerationError("Required placeholder data missing: {{SUMMARY}}")

    values = {placeholder: "" for placeholder in PLACEHOLDER_SCHEMA[template]}
    values["{{TARGET_ROLE}}"] = _clean_text(target_role)
    values["{{SUMMARY}}"] = _clean_text(summary) or _derive_summary(
        target_role=values["{{TARGET_ROLE}}"],
        history=history,
        narratives=narratives,
        taxonomy=taxonomy,
    )

    if template == "resume":
        for index, bullet in enumerate(_candidate_bullets(history)[:RESUME_BULLET_COUNT], start=1):
            values[f"{{{{BULLET_{index}}}}}"] = bullet
    elif template == "cover_letter":
        for index, response in enumerate(_candidate_narratives(narratives)[:COVER_LETTER_RESPONSE_COUNT], start=1):
            values[f"{{{{KSC_RESPONSE_{index}}}}}"] = response

    missing_required = [
        placeholder
        for placeholder in ("{{TARGET_ROLE}}", "{{SUMMARY}}")
        if not values.get(placeholder)
    ]
    if template == "resume" and not values.get("{{BULLET_1}}"):
        missing_required.append("{{BULLET_1}}")
    if template == "cover_letter" and not values.get("{{KSC_RESPONSE_1}}"):
        missing_required.append("{{KSC_RESPONSE_1}}")
    if missing_required:
        missing = ", ".join(sorted(set(missing_required)))
        raise DocumentGenerationError(f"Required placeholder data missing: {missing}")

    return values, _count_stats(values)


def make_replace_requests(values: dict[str, str]) -> list[dict[str, Any]]:
    requests = []
    for placeholder, replacement in sorted(values.items()):
        requests.append(
            {
                "replaceAllText": {
                    "containsText": {
                        "text": placeholder,
                        "matchCase": True,
                    },
                    "replaceText": replacement,
                }
            }
        )
    return requests


def find_unresolved_placeholders(text: str) -> list[str]:
    return sorted(set(PLACEHOLDER_RE.findall(text or "")))


def _extract_document_text(document: dict[str, Any]) -> str:
    parts: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            text_run = node.get("textRun")
            if isinstance(text_run, dict):
                content = text_run.get("content")
                if isinstance(content, str):
                    parts.append(content)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(document.get("body", {}).get("content", []))
    for header in document.get("headers", {}).values():
        walk(header.get("content", []))
    for footer in document.get("footers", {}).values():
        walk(footer.get("content", []))
    for footnote in document.get("footnotes", {}).values():
        walk(footnote.get("content", []))
        
    return "".join(parts)


def build_google_services() -> tuple[Any, Any]:
    try:
        from google.oauth2 import service_account
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise DocumentGenerationError(
            "Google API dependencies are missing. Run: "
            "pip install google-api-python-client google-auth-oauthlib google-auth-httplib2"
        ) from exc

    scopes = [
        "https://www.googleapis.com/auth/documents",
        "https://www.googleapis.com/auth/drive",
    ]
    service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if service_account_path:
        credentials = service_account.Credentials.from_service_account_file(
            service_account_path,
            scopes=scopes,
        )
    else:
        client_secrets_path = Path(os.getenv("GOOGLE_OAUTH_CLIENT_SECRETS", "credentials.json"))
        token_path = Path(os.getenv("GOOGLE_OAUTH_TOKEN", "token.json"))
        credentials = None
        if token_path.exists():
            credentials = Credentials.from_authorized_user_file(str(token_path), scopes)
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        if not credentials or not credentials.valid:
            if not client_secrets_path.exists():
                raise DocumentGenerationError(
                    "OAuth client secrets not found. Set GOOGLE_OAUTH_CLIENT_SECRETS "
                    "or GOOGLE_APPLICATION_CREDENTIALS."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets_path), scopes)
            credentials = flow.run_local_server(port=0)
            token_path.write_text(credentials.to_json(), encoding="utf-8")

    docs_service = build("docs", "v1", credentials=credentials)
    drive_service = build("drive", "v3", credentials=credentials)
    return docs_service, drive_service


def clone_and_replace(
    *,
    docs_service: Any,
    drive_service: Any,
    template_doc_id: str,
    values: dict[str, str],
    target_role: str,
    template: str,
) -> tuple[str, str, list[str]]:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    try:
        copied = (
            drive_service.files()
            .copy(
                fileId=template_doc_id,
                body={"name": f"Career Brain {template} - {target_role} - {timestamp}"},
                fields="id, webViewLink",
            )
            .execute()
        )
        doc_id = copied["id"]

        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": make_replace_requests(values)},
        ).execute()

        document = docs_service.documents().get(documentId=doc_id).execute()
    except Exception as exc:
        if type(exc).__name__ == "HttpError":
            raise DocumentGenerationError(f"Google API Error: {exc}") from exc
        raise

    unresolved = find_unresolved_placeholders(_extract_document_text(document))
    doc_link = copied.get("webViewLink") or DOC_LINK_TEMPLATE.format(doc_id=doc_id)
    return doc_id, doc_link, unresolved


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(
    *,
    template: str,
    template_variant: str | None,
    template_doc_id: str,
    generated_doc_id: str | None,
    generated_doc_link: str | None,
    placeholder_stats: dict[str, int],
    unresolved_tokens: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    return {
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "template": template,
        "template_variant": template_variant,
        "template_doc_id": template_doc_id,
        "generated_doc_id": generated_doc_id,
        "generated_doc_link": generated_doc_link,
        "placeholder_stats": placeholder_stats,
        "unresolved_tokens": unresolved_tokens,
        "warnings": warnings,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clone a Google Docs Golden Master and fill Career Brain placeholders."
    )
    parser.add_argument("--target", required=True, help="Target role title for {{TARGET_ROLE}}.")
    parser.add_argument(
        "--template",
        required=True,
        choices=sorted(PLACEHOLDER_SCHEMA),
        help="Logical template type from doc_templates.json.",
    )
    parser.add_argument(
        "--template-variant",
        default=None,
        help="Optional variant key under the selected template config.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to doc template config JSON.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT,
        help="Directory containing Career Brain JSON outputs.",
    )
    parser.add_argument(
        "--out-report",
        type=Path,
        default=DEFAULT_REPORT,
        help="Path for redacted document generation report.",
    )
    parser.add_argument(
        "--summary",
        default=None,
        help="Optional summary override for {{SUMMARY}}.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build placeholder values and report without calling Google APIs.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    warnings: list[str] = []

    try:
        history, narratives, taxonomy = load_source_data(args.output_dir)
        config = load_template_config(args.config)
        template_doc_id = resolve_template_doc_id(
            config,
            args.template,
            args.template_variant,
            allow_placeholder=args.dry_run,
        )
        values, placeholder_stats = build_placeholder_values(
            template=args.template,
            target_role=args.target,
            history=history,
            narratives=narratives,
            taxonomy=taxonomy,
            summary=args.summary,
        )

        generated_doc_id = None
        generated_doc_link = None
        unresolved_tokens: list[str] = []

        if args.dry_run:
            warnings.append("dry_run_no_google_document_created")
        else:
            docs_service, drive_service = build_google_services()
            generated_doc_id, generated_doc_link, unresolved_tokens = clone_and_replace(
                docs_service=docs_service,
                drive_service=drive_service,
                template_doc_id=template_doc_id,
                values=values,
                target_role=args.target,
                template=args.template,
            )
            if unresolved_tokens:
                warnings.append("unresolved_placeholders_after_replacement")

        report = build_report(
            template=args.template,
            template_variant=args.template_variant,
            template_doc_id=template_doc_id,
            generated_doc_id=generated_doc_id,
            generated_doc_link=generated_doc_link,
            placeholder_stats=placeholder_stats,
            unresolved_tokens=unresolved_tokens,
            warnings=warnings,
        )
        write_report(args.out_report, report)

        log.info(
            "Document generation complete: template=%s filled=%s blank=%s unresolved=%s doc_id=%s",
            args.template,
            placeholder_stats["filled"],
            placeholder_stats["blank"],
            len(unresolved_tokens),
            generated_doc_id or "dry-run",
        )
        if generated_doc_link:
            log.info("Generated document link: %s", generated_doc_link)
        return 1 if unresolved_tokens else 0
    except DocumentGenerationError as exc:
        log.error(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
