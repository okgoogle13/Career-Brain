# Theme Brief — community_practice

<!-- Form: templates/THEME_BRIEF_FORM.md. Purpose answers are a draft for review at stop S2; [ASSUMPTION] marks audience framing not yet confirmed by the user. -->

## META
FAMILY_ID: community_practice
STATUS: draft
MEMBERS: resume=templates/resume_community_practice_v1.json | cover_letter=templates/cover_letter_community_practice_v1.json | ksc=templates/ksc_community_practice_v1.json (Required where selection criteria are common (NFP))

## PURPOSE
AUDIENCE (Q1): Frontline and senior practitioners in community services, NFP and health [ASSUMPTION: confirm at S2]
CONTEXT (Q2): Community-sector roles where long practice narratives and values fit are read in full
READER_FIRST (Q3): The professional summary, set in airy Georgia
STORY (Q4): Relational, values-led practice told in readable paragraphs
FOREGROUND (Q5): summary_section and role bullets at airy rhythm
DEEMPHASISE (Q6): skills_section (no fill)
NEAREST (Q7): resume_modern_private_v1 (distance 3) - sans, strong left-bar headings for private sector; no serif reading rhythm

## DECISIONS
typography.line_spacing = 1.35 -> airy rhythm for narrative-heavy reading
page.margin_*_cm = 2.4 -> wide margins reduce line length for serif body text
blocks[].heading = title case -> warmer register than uppercase

## SHARED_IDENTITY
base_font: Georgia
heading_font: Arial
heading_colour: #7B341E
name_header: 20.0pt / bold / #7B341E
margins_cm: 2.4, 2.4, 2.4, 2.4

## PER_DOCUMENT
resume: line_spacing 1.35; skills fill False; headings title border_bottom
cover_letter: line_spacing 1.35 (line_rhythm one bucket airier or equal); name block identical to resume
ksc: criterion_text Arial / bold / #7B341E / 13.0pt (= resume section heading); body line_spacing 1.35

## STANDARD_CHECK
S1: PASS - name_scale prominent, heading_scale moderate; role_title bold 11.5pt; meta #4A5568
S2: PASS - body 11pt, bullets/meta 10.5pt; families ['Arial', 'Georgia'] (serif + sans)
S3: PASS - accent #D4865A in one role (rules); body #1A1A1A; meta #4A5568; contrast_failures []
S4: PASS - line_spacing 1.35; spacing_after_pt 6; margins 2.4 cm, left = right; one heading style for every section
S5: PENDING - rendered check
S6: PASS - base_font, heading font, heading colour, name_header and margins identical in all three members (fingerprint + JSON compare)
