# Theme Brief — corporate_classic

<!-- Form: templates/THEME_BRIEF_FORM.md. Purpose answers are a draft for review at stop S2; [ASSUMPTION] marks audience framing not yet confirmed by the user. -->

## META
FAMILY_ID: corporate_classic
STATUS: draft
MEMBERS: resume=templates/resume_corporate_classic_v1.json | cover_letter=templates/cover_letter_corporate_classic_v1.json | ksc=templates/ksc_corporate_classic_v1.json (Optional - included for corporate roles that still ask for selection criteria)

## PURPOSE
AUDIENCE (Q1): Applicants to finance, law and corporate roles screened by recruiters [ASSUMPTION: confirm at S2]
CONTEXT (Q2): Agency- or HR-screened corporate roles with conventional resume expectations
READER_FIRST (Q3): The dominant ruled name block
STORY (Q4): Steady, conventional professional standing
FOREGROUND (Q5): name_header (26pt with rule) and experience_section
DEEMPHASISE (Q6): section headings (body size; differ by weight, case, colour and rule)
NEAREST (Q7): resume_policy_editorial_v1 (distance 3) - same rules but strong headings, tight rhythm, narrow margins

## DECISIONS
name_header.visualConfig.font_size_pt = 26 with border_bottom -> name dominates, letterhead convention
typography.section_heading_size_pt = 11.5 -> flat heading scale keeps the page conservative
skills_section.visualConfig.container.background_color = #EDF2F7 -> one quiet accent role

## SHARED_IDENTITY
base_font: Times New Roman
heading_font: Times New Roman
heading_colour: #1A365D
name_header: 26.0pt / bold / #1A365D / rule #1A365D
margins_cm: 2.0, 2.0, 2.0, 2.0

## PER_DOCUMENT
resume: line_spacing 1.25; skills fill True; headings upper border_bottom
cover_letter: line_spacing 1.35 (line_rhythm one bucket airier or equal); name block identical to resume
ksc: criterion_text Times New Roman / bold / #1A365D / 11.5pt (= resume section heading); body line_spacing 1.25

## STANDARD_CHECK
S1: PASS - name_scale dominant, heading_scale flat (flat: differs from body by bold, uppercase, colour #1A365D and rule); role_title bold 11.5pt; meta #4A5568
S2: PASS - body 11pt, bullets/meta 10.5pt; families ['Times New Roman']
S3: PASS - accent #EDF2F7 in one role (skills fill); body #1A1A1A; meta #4A5568; contrast_failures []
S4: PASS - line_spacing 1.25; spacing_after_pt 6; margins 2.0 cm, left = right; one heading style for every section
S5: PENDING - rendered check
S6: PASS - base_font, heading font, heading colour, name_header and margins identical in all three members (fingerprint + JSON compare)
