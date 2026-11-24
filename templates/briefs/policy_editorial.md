# Theme Brief — policy_editorial

<!-- Form: templates/THEME_BRIEF_FORM.md. Purpose answers are a draft for review at stop S2; [ASSUMPTION] marks audience framing not yet confirmed by the user. -->

## META
FAMILY_ID: policy_editorial
STATUS: draft
MEMBERS: resume=templates/resume_policy_editorial_v1.json | cover_letter=templates/cover_letter_policy_editorial_v1.json | ksc=templates/ksc_policy_editorial_v1.json (Required (government and policy roles use criteria))

## PURPOSE
AUDIENCE (Q1): Policy, research and advocacy applicants with dense evidence [ASSUMPTION: confirm at S2]
CONTEXT (Q2): Policy and research roles in government and advocacy bodies
READER_FIRST (Q3): The dominant ruled name and strong uppercase headings
STORY (Q4): Evidence-dense, editorial authority
FOREGROUND (Q5): experience_section bullets at tight rhythm and narrow margins
DEEMPHASISE (Q6): role_headline
NEAREST (Q7): resume_corporate_classic_v1 (distance 3) - flat headings, medium rhythm, standard margins

## DECISIONS
page.margin_*_cm = 1.6 with line_spacing = 1.15 -> narrow, tight frame holds more evidence per page
experience_section.visualConfig.heading.border_bottom = #8B0000 -> dark red rules are the single accent role
heading_font_family = Arial over Georgia body -> serif + sans editorial pairing

## SHARED_IDENTITY
base_font: Georgia
heading_font: Arial
heading_colour: #000000
name_header: 26.0pt / bold / #000000 / rule #8B0000
margins_cm: 1.6, 1.6, 1.6, 1.6

## PER_DOCUMENT
resume: line_spacing 1.15; skills fill True; headings upper border_bottom
cover_letter: line_spacing 1.25 (line_rhythm one bucket airier or equal); name block identical to resume
ksc: criterion_text Arial / bold / #000000 / 14.5pt (= resume section heading); body line_spacing 1.25

## STANDARD_CHECK
S1: PASS - name_scale dominant, heading_scale strong; role_title bold 11.5pt; meta #4A5568
S2: PASS - body 11pt, bullets/meta 10.5pt; families ['Arial', 'Georgia'] (serif + sans)
S3: PASS - accent #8B0000 in one role (rules); body #1A1A1A; meta #4A5568; contrast_failures []
S4: PASS - line_spacing 1.15; spacing_after_pt 6; margins 1.6 cm, left = right; one heading style for every section
S5: PENDING - rendered check
S6: PASS - base_font, heading font, heading colour, name_header and margins identical in all three members (fingerprint + JSON compare)
