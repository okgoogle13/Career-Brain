# Theme Brief — state_gov_panel

<!-- Form: templates/THEME_BRIEF_FORM.md. Purpose answers are a draft for review at stop S2; [ASSUMPTION] marks audience framing not yet confirmed by the user. -->

## META
FAMILY_ID: state_gov_panel
STATUS: draft
MEMBERS: resume=templates/resume_state_gov_panel_v1.json | cover_letter=templates/cover_letter_state_gov_panel_v1.json | ksc=templates/ksc_state_gov_panel_v1.json (Required (government sector))

## PURPOSE
AUDIENCE (Q1): Applicants to AU state government and statutory roles assessed by a selection panel [ASSUMPTION: confirm at S2]
CONTEXT (Q2): State and local government roles with key selection criteria and a scored panel shortlist
READER_FIRST (Q3): The filled Key Skills block, which carries the criteria keywords
STORY (Q4): Accountable, criteria-matched service delivery a panel can tick off line by line
FOREGROUND (Q5): skills_section (filled container) and experience_section bullets
DEEMPHASISE (Q6): role_headline (body-weight sized, no rule)
NEAREST (Q7): resume_policy_editorial_v1 / resume_corporate_classic_v1 (distance 4) - neither targets panel shortlisting with a skills fill at tight rhythm and standard margins

## DECISIONS
skills_section.visualConfig.container.background_color = #F0FFF4 -> keywords grouped where a panel scans first
typography.line_spacing = 1.15 -> tight rhythm fits six roles on two pages for long-tenure applicants
experience_section.visualConfig.heading.border_bottom = #22543D -> ruled uppercase sections mirror selection-report structure

## SHARED_IDENTITY
base_font: Calibri
heading_font: Calibri
heading_colour: #22543D
name_header: 20.0pt / bold / #22543D
margins_cm: 2.0, 2.0, 2.0, 2.0

## PER_DOCUMENT
resume: line_spacing 1.15; skills fill True; headings upper border_bottom
cover_letter: line_spacing 1.25 (line_rhythm one bucket airier or equal); name block identical to resume
ksc: criterion_text Calibri / bold / #22543D / 13.0pt (= resume section heading); body line_spacing 1.25

## STANDARD_CHECK
S1: PASS - name_scale prominent, heading_scale moderate; role_title bold 11.5pt; meta #4A5568
S2: PASS - body 11pt, bullets/meta 10.5pt; families ['Calibri']
S3: PASS - accent #F0FFF4 in one role (skills fill); body #1A1A1A; meta #4A5568; contrast_failures []
S4: PASS - line_spacing 1.15; spacing_after_pt 6; margins 2.0 cm, left = right; one heading style for every section
S5: PENDING - rendered check
S6: PASS - base_font, heading font, heading colour, name_header and margins identical in all three members (fingerprint + JSON compare)
