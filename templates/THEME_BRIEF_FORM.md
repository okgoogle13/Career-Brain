# Theme Brief

<!-- One brief per family, written before any theme JSON. Fill every field; write "absent" rather than
inventing a rationale. Field rules: templates/THEME_SPEC_GUIDE.md "Design Standard" (S1-S6) and
"Naming Convention". Q-numbers map to theme-purpose-interrogator; Q8 (colour variation) comes from
theme-divergence-auditor and is not filled here. DECISIONS may cite emitted fields only. -->

## META
FAMILY_ID: <snake_case sector or strategy name>
STATUS: <draft | active>
MEMBERS: resume=<templates/resume_<family_id>_v1.json> | cover_letter=<templates/cover_letter_<family_id>_v1.json> | ksc=<templates/ksc_<family_id>_v1.json, or none - <rationale per KSC coverage rule>>

## PURPOSE
AUDIENCE (Q1): <specific user, e.g. mid-career community-services practitioners moving into team-leader roles>
CONTEXT (Q2): <application context, e.g. state government roles with selection criteria>
READER_FIRST (Q3): <one element a recruiter should notice first>
STORY (Q4): <one sentence that would not fit another theme in the same sector>
FOREGROUND (Q5): <block or field>
DEEMPHASISE (Q6): <block or field>
NEAREST (Q7): <nearest existing theme> - <the user or story gap it leaves>

## DECISIONS
<!-- Q9: at least two. Format: json.path = value -> purpose it serves -->
<json.path> = <value> -> <purpose>
<json.path> = <value> -> <purpose>

## SHARED_IDENTITY
base_font: <font>
heading_font: <font, or same>
heading_colour: <#RRGGBB>
name_header: <size pt / weight / #RRGGBB>
margins_cm: <top, bottom, left, right>

## PER_DOCUMENT
resume: <how it foregrounds evidence>
cover_letter: <line_spacing and name block>
ksc: <criterion_text font, weight, colour>

## STANDARD_CHECK
<!-- PASS or FAIL, then evidence quoted from theme_fingerprint.py output or the JSON. -->
S1: <PASS | FAIL> - <evidence>
S2: <PASS | FAIL> - <evidence>
S3: <PASS | FAIL> - <evidence>
S4: <PASS | FAIL> - <evidence>
S5: PENDING - rendered check
S6: <PASS | FAIL> - <evidence>
