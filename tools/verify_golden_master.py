#!/usr/bin/env python3
"""Live verification of a built Golden Master Google Doc.

Confirms the 2026-06-02 "fix text style sequence" actually persists run-level
styling in the live Docs environment: re-fetches the Doc and checks that
non-blank text runs carry non-empty `textStyle` — NOT the vacuous `STYLE OK`
that audit_doc_style.py reports. Also exports a PDF for visual review.

Font-aware: Google Docs stores only *deltas* from the inherited named style, so
a run whose font equals the doc default (Arial) legitimately has NO
weightedFontFamily override. Pass --base-font so the verdict only requires
weightedFontFamily when the theme font differs from the doc default.

Heading-aware mode (--theme=path): rebuilds the paragraph list with
build_golden_master.build_paragraphs(), labels each Doc paragraph as heading or
body, and checks each run's font against heading_font_family[0] or base_font.
A run with no override passes only when the expected font equals the doc default.

Usage:
    python3 tools/verify_golden_master.py <DOC_ID> [pdf_out] [--base-font=Calibri]
    python3 tools/verify_golden_master.py <DOC_ID> [pdf_out] --theme=templates/<name>.json
"""
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))


def check_fonts_by_role(paragraphs, rows, default_font, base_font, heading_font, heading_roles):
    """Check run fonts against the font each paragraph's role expects.

    paragraphs: list of lists of (content, textStyle) runs, one list per Doc paragraph.
    rows: build_paragraphs() output; row[0] is the text, row[4] the role.
    Returns (ok, checked_runs, problems).
    """
    role_by_text = {}
    for row in rows:
        role_by_text.setdefault(row[0].strip(), row[4])
    problems, checked = [], 0
    for runs in paragraphs:
        text = "".join(c for c, _ in runs).strip()
        if not text:
            continue
        role = role_by_text.get(text)
        if role is None:
            problems.append(f"unmatched paragraph {text[:40]!r}")
            continue
        expected = heading_font if role in heading_roles else base_font
        for content, ts in runs:
            if not content.strip():
                continue
            checked += 1
            actual = ts.get("weightedFontFamily", {}).get("fontFamily")
            if actual is None and expected == default_font:
                continue  # Docs normalizes an override equal to the default away
            if actual != expected:
                problems.append(f"{role} {content.strip()[:30]!r}: font={actual} expected={expected}")
    return not problems, checked, problems


def main():
    positional = [a for a in sys.argv[1:] if not a.startswith("--")]
    base_font = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--base-font=")), None)
    theme_path = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--theme=")), None)
    theme = None
    if theme_path:
        theme = json.loads(Path(theme_path).read_text(encoding="utf-8"))
        theme_base = theme["typography"]["base_font"]
        if base_font and base_font != theme_base:
            print(f"--base-font={base_font} conflicts with theme base_font {theme_base}", file=sys.stderr)
            sys.exit(2)
        base_font = theme_base
    if not positional or not positional[0].strip():
        print("usage: verify_golden_master.py <DOC_ID> [pdf_out] [--base-font=NAME]", file=sys.stderr)
        sys.exit(2)
    doc_id = positional[0].strip()
    pdf_out = Path(positional[1]) if len(positional) > 1 else ROOT / "scratch" / "golden_master_verification.pdf"

    from generate_document import build_google_services
    from googleapiclient.http import MediaIoBaseDownload

    docs_service, drive_service = build_google_services()
    doc = docs_service.documents().get(documentId=doc_id).execute()

    default_font = None
    for s in doc.get("namedStyles", {}).get("styles", []):
        if s.get("namedStyleType") == "NORMAL_TEXT":
            default_font = s.get("textStyle", {}).get("weightedFontFamily", {}).get("fontFamily")

    runs, paragraphs = [], []
    for el in doc.get("body", {}).get("content", []):
        para = el.get("paragraph")
        if not para:
            continue
        para_runs = []
        for pe in para.get("elements", []):
            tr = pe.get("textRun")
            if tr is None:
                continue
            para_runs.append((tr.get("content", ""), tr.get("textStyle", {})))
        runs.extend(para_runs)
        paragraphs.append(para_runs)

    nonblank = [(c, ts) for c, ts in runs if c.strip()]
    with_font = [ts for c, ts in nonblank if ts.get("weightedFontFamily", {}).get("fontFamily")]
    with_size = [ts for c, ts in nonblank if ts.get("fontSize")]
    with_color = [ts for c, ts in nonblank if ts.get("foregroundColor")]
    empty = [(c, ts) for c, ts in nonblank if not ts]

    print(f"Doc: https://docs.google.com/document/d/{doc_id}/edit")
    print(f"doc default font (NORMAL_TEXT): {default_font} | theme base_font: {base_font or '(not given)'}")
    print(f"runs total={len(runs)} | non-blank={len(nonblank)}")
    print(f"  with weightedFontFamily: {len(with_font)}/{len(nonblank)}")
    print(f"  with fontSize:           {len(with_size)}/{len(nonblank)}")
    print(f"  with foregroundColor:    {len(with_color)}/{len(nonblank)}")
    print(f"  EMPTY textStyle:         {len(empty)}/{len(nonblank)}")

    print("\nsamples (first 6 non-blank runs):")
    for c, ts in nonblank[:6]:
        fam = ts.get("weightedFontFamily", {}).get("fontFamily")
        sz = ts.get("fontSize", {}).get("magnitude")
        rgb = ts.get("foregroundColor", {}).get("color", {}).get("rgbColor", {})
        print(f"  {c.strip()[:34]!r:38} font={fam} size={sz} bold={ts.get('bold')} color={rgb}")

    pdf_out.parent.mkdir(parents=True, exist_ok=True)
    request = drive_service.files().export_media(fileId=doc_id, mimeType="application/pdf")
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    pdf_out.write_bytes(buf.getvalue())
    print(f"\nPDF exported: {pdf_out}  ({buf.getbuffer().nbytes} bytes)")

    # Verdict. Original bug = textStyle:{} on every run; color always differs from
    # default black so it must persist on all runs. weightedFontFamily is only an
    # *expected* override when the theme font differs from the doc default.
    font_expected = bool(base_font) and base_font != default_font
    if theme is not None:
        import build_golden_master as bgm
        heading_font = (theme.get("heading_font_family") or [base_font])[0]
        font_ok, checked, problems = check_fonts_by_role(
            paragraphs, bgm.build_paragraphs(theme), default_font, base_font, heading_font, bgm.HEADING_ROLES)
        font_note = (f"BY ROLE (body {base_font}, headings {heading_font}, default {default_font}) -> "
                     f"{checked - len(problems)}/{checked} runs ok")
        for prob in problems[:10]:
            print(f"  font problem: {prob}")
    elif font_expected:
        font_ok = len(with_font) == len(nonblank)
        font_note = f"REQUIRED ({base_font} != default {default_font}) -> {len(with_font)}/{len(nonblank)}"
    else:
        font_ok = True
        font_note = (f"N/A (base_font {base_font} == doc default -> override normalized away)"
                     if base_font else "N/A (no --base-font given)")

    no_empty = len(nonblank) > 0 and not empty
    color_ok = len(with_color) == len(nonblank)
    ok = no_empty and color_ok and font_ok
    print(f"\n  no-empty-textStyle: {no_empty} | color-on-all: {color_ok} | font: {font_note}")
    print(f"VERDICT: {'PASS — run-level textStyle persisted (fix confirmed live)' if ok else 'FAIL'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
