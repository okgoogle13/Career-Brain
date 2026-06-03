# Phase 2 Tasks — Theme Standardisation (themes 21–25)

> Translate the 5 text design specs in `planning/phase1-design-synthesis.md` into
> 5 schema-conformant theme JSON files under `templates/`.

## ⚠️ Validator correction (read first)

The execution prompt names `python3 tools/validate_template_spec.py <file>` as the
"validate" step. **That tool cannot validate theme JSON.** It is a hard-gate for
**KSC Markdown specs** (`## META / ## STRUCTURE / {{KSC_CRITERION_N}}` tokens) and
fails on the reference `theme-01-graphite-ledger.json` itself (exit 1, "Missing
required section: ## META …"). No `.py` in the repo references `MASTER_SCHEMA` or any
theme-JSON field, so there is **no automated structural validator** for these files.
`tools/audit_doc_style.py` requires a live Google Doc ID and only reads a theme via
`--theme` for style constraints — it is not a standalone JSON check.

**Corrected verification used here** (JSON parse + key-shape parity vs theme-01 +
6-digit-uppercase hex + ATS-font whitelist + scalar profile fields):

```bash
python3 - <<'PY'
import json, glob
ref = json.load(open("templates/theme-01-graphite-ledger.json"))
def keyset(d, p=""):
    ks=set()
    if isinstance(d,dict):
        for k,v in d.items(): ks.add(p+k); ks|=keyset(v,p+k+".")
    return ks
refk = keyset(ref)
for f in sorted(glob.glob("templates/theme-2[1-5]-*.json")):
    d = json.load(open(f)); dk = keyset(d)
    print(f, "missing", sorted(refk-dk) or "none", "extra", sorted(dk-refk) or "none")
PY
```

## Conventions (locked from theme-01 / theme-02, the schema 2.3 reference impls)
- Profile fields (`band_placement_profile`, `accent_placement_profile`,
  `divider_rhythm`, `accent_logic.contrast_intensity`) are **scalars**, not the
  enum arrays shown in `MASTER_SCHEMA_V2_3.json`.
- 95 keys total, exact key order from theme-01.
- `placeholder_schema` = `"PLACEHOLDERSCHEMAV2"`; `region` = `"AU"`; `tier` = 1.
- `font_family` = ATS whitelist with `base_font` first.
- `avoid_list` = theme-01's 17-item base + spec's "Avoid List Additions".
- Boilerplate (`forbidden_repeats`, `non_reuse_constraints`,
  `adjacent_theme_difference_rules`) copied verbatim across themes.

## Per-file checklist

| File | Create/transform | Verify (corrected) | Status |
|---|---|---|---|
| `templates/theme-21-terminal-signal.json` | map spec → JSON | shape/hex/font/scalar checks | ✅ pass |
| `templates/theme-22-horizon-edge.json` | map spec → JSON | shape/hex/font/scalar checks | ✅ pass |
| `templates/theme-23-broadside-press.json` | map spec → JSON | shape/hex/font/scalar checks | ✅ pass |
| `templates/theme-24-clay-canvas.json` | map spec → JSON | shape/hex/font/scalar checks | ✅ pass |
| `templates/theme-25-cyan-blueprint.json` | map spec → JSON | shape/hex/font/scalar checks | ✅ pass |

## Resolved spec↔schema reconciliations
1. **Clay Canvas `must_include`** said "Lora font" → set to **"Georgia serif body
   font"** (Lora is not on the ATS whitelist and contradicted `base_font: Georgia`).
2. **Cyan Blueprint `must_include`** said "Open Sans font" → set to **"Arial
   sans-serif font"** (same reason; `base_font: Arial`).
3. **Band heights below master's `height_rule.min_pt: 2`** — Broadside (1/2/1) and
   Clay (1/1/1) preserved as the spec's design intent. The master value is the
   baseline theme's own height, not an enforced floor; flagged, not altered.
4. **Divider rhythm** — Clay and Cyan both map to `"alternating"`; their divider
   *grammar* differs ("dashed" vs "alternating thin/medium rules"). Preserved as
   specified; noted as a soft adjacency overlap (no validator enforces it).
5. **Unspecified-but-required fields** (`band_targets`, `highlight_band_targets`,
   `accent_logic.complementary_accent_role`) derived from each theme's stated band
   placement and accent logic using master-schema-allowed values — no placeholders.
