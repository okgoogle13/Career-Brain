# Project Goal: Build the 7 Remaining Golden Masters

**Context:**
The Career Brain pipeline relies on Golden Master Google Docs to inject tailored tokens. We currently have 3 "Contemporary/Modern" resume themes fully built. We now need to build the remaining 7 variants defined in `doc_templates.json`.

**Your Task:**
You must create the 7 missing JSON theme specs, build them using our script, audit them, and update the registry.

## Step 1: Create Theme JSON Specs
Create the following 7 files in `doc_templates/`. Ensure they strictly follow `THEME_SPEC_GUIDE.md` and include the appropriate `doc_type`.

1. `cover_letter_government_v1.json`
   - `doc_type`: "cover_letter"
   - Match the typography and palette of `Contemporary Professional` (Calibri, Forest Green/Sage, safe).
2. `cover_letter_nfp_v1.json`
   - `doc_type`: "cover_letter"
   - Match the typography and palette of `Warm Impact` (Calibri, Ink Gold/Waratah Red, safe).
3. `cover_letter_private_v1.json`
   - `doc_type`: "cover_letter"
   - Match the typography and palette of `Modern Minimalist` (Arial, Slate Blue/Teal, safe).
4. `cover_letter_base_v1.json`
   - `doc_type`: "cover_letter"
   - Match the typography and palette of `Professional Classic` (Times New Roman, Deep Navy/Charcoal, safe).
5. `ksc_base_v1.json`
   - `doc_type`: "ksc"
   - Match the typography and palette of `Contemporary Professional`.
6. `resume_chronological_v1.json`
   - `doc_type`: "resume"
   - Match the typography and palette of `Professional Classic`. Use the standard 8 resume blocks.
7. `resume_hybrid_v1.json`
   - `doc_type`: "resume"
   - Match the typography and palette of `Contemporary Professional`. Use the standard 8 resume blocks.

*Note: Ensure the Cover Letter and KSC JSON files contain the correct block names as updated in `THEME_SPEC_GUIDE.md` (e.g., `employer_info`, `salutation` etc).*

## Step 2: Build the Golden Masters
For each of the 7 new JSON specs, run:
```bash
source .venv/bin/activate
python3 build_golden_master.py doc_templates/<filename>.json
```
This will print out a Google Doc ID on success.

## Step 3: Run the Auditor
For each generated Google Doc ID, verify its styling using the updated auditor:
```bash
python3 audit_doc_style.py <DOC_ID> --theme doc_templates/<filename>.json
```
If any document fails, inspect the JSON's `visualConfig` and typography settings to ensure they match the constraints.

## Step 4: Update the Registry
Finally, update `doc_templates.json`. Map each of the new Doc IDs to their respective variants:
- `cover_letter` (base)
- `cover_letter.variants.government`
- `cover_letter.variants.nfp`
- `cover_letter.variants.private`
- `ksc` (base)
- `resume.variants.chronological`
- `resume.variants.hybrid`

When you have successfully built, audited, and registered all 7 templates, summarize your changes and stop.
