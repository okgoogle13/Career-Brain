# Theme Brief — modern_private

<!-- Form: templates/THEME_BRIEF_FORM.md. Purpose answers are a draft for review at stop S2; [ASSUMPTION] marks audience framing not yet confirmed by the user. -->

## META
FAMILY_ID: modern_private
STATUS: draft
MEMBERS: resume=templates/resume_modern_private_v1.json | cover_letter=templates/cover_letter_modern_private_v1.json | ksc=templates/ksc_modern_private_v1.json (Optional - included for private roles that ask for criteria responses)

## PURPOSE
AUDIENCE (Q1): Private-sector, technology and startup applicants [ASSUMPTION: confirm at S2]
CONTEXT (Q2): Recruiter-screened private roles where fast scanning beats long narrative
READER_FIRST (Q3): Strong title-case section headings with a teal left bar
STORY (Q4): Direct, outcome-first progression
FOREGROUND (Q5): experience_section headings and bullets
DEEMPHASISE (Q6): skills_section (no fill)
NEAREST (Q7): resume_community_practice_v1 (distance 3) - serif, bottom-ruled, airy

## DECISIONS
experience_section.visualConfig.heading.border_left = #38B2AC -> left bar is the only accent and marks scan points
typography.section_heading_size_pt = 14.5 -> strong heading scale for quick section finding
page.margin_*_cm = 2.4 -> wide margins, open page

## SHARED_IDENTITY
base_font: Arial
heading_font: Arial
heading_colour: #234E52
name_header: 20.0pt / bold / #234E52
margins_cm: 2.4, 2.4, 2.4, 2.4

## PER_DOCUMENT
resume: line_spacing 1.25; skills fill False; headings title border_left
cover_letter: line_spacing 1.35 (line_rhythm one bucket airier or equal); name block identical to resume
ksc: criterion_text Arial / bold / #234E52 / 14.5pt (= resume section heading); body line_spacing 1.25

## STANDARD_CHECK
S1: PASS - name_scale prominent, heading_scale strong; role_title bold 11.5pt; meta #4A5568
S2: PASS - body 11pt, bullets/meta 10.5pt; families ['Arial']
S3: PASS - accent #38B2AC in one role (rules); body #1A1A1A; meta #4A5568; contrast_failures []
S4: PASS - line_spacing 1.25; spacing_after_pt 6; margins 2.4 cm, left = right; one heading style for every section
S5: PENDING - rendered check
S6: PASS - base_font, heading font, heading colour, name_header and margins identical in all three members (fingerprint + JSON compare)
