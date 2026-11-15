# Duster MY26 2026-11-02 Hybrid 155 Voltage Evidence Consistency Correction

## Result

**Documentation correction only.** The Duster MY26 2026-11-02 reconciliation Markdown report is aligned with the visually verified official PDF and the already-correct JSON report. No master data, source registry records, or voltage observations are changed.

## Exact source identity

- Source code: `src_pl_duster_price_my26_20261102`
- Official source: https://cdn.group.renault.com/dac/pl/pdf/cenniki/duster-price.pdf.asset.pdf/f07ca0a87f.pdf
- Archived file: `PDF/Cenniki/DACIA DUSTER cennik MY26 20261102.pdf`
- SHA-256: `dd6c65d048d7531251967ba39bb8ab6767256882325254e9b3eaafac11d89118`
- Page count: 10

## Correct voltage evidence

For all three Duster Hybrid 155 configurations:

- Printed page 6 technical table: **230 V**.
- Printed page 2 narrative: **260 V** (1.4 kWh traction battery statement).
- Previous 2026-09-01 printed page-6 technical table: **230 V**.

The earlier 280 V statement was a text-extraction error. The source hash is already registered and verified. The 260 V narrative and 230 V technical-table value are separate source contexts; neither should be substituted for the other.

## Changes

- Corrected `data/reporting/duster_price_list_20261102_commercial_reconciliation.md`:
  - corrected document page count to 10;
  - corrected Hybrid 155 page-6 voltage to 230 V;
  - retained page-2 narrative 260 V as distinct evidence;
  - removed the false claim that three 280 V observations were pending;
  - corrected printed-page inventory: page 9 dimensions; page 10 legal/commercial terms;
  - corrected deferred items and the closing evidence boundary.
- Updated `project/SESSION_STATE.md` to record the corrected evidence and remove stale Jogger next-package wording.
- Left `data/reporting/duster_price_list_20261102_commercial_reconciliation.json`, `data/master/`, and the source registry unchanged.

## Explicit non-actions

- No 280 V observation was created.
- No existing 230 V master observation was modified or overwritten.
- No 260 V configuration-level observation was inferred from narrative text.
- No price, equipment, package, or availability data was imported.
- No brochure or configurator source was used.

## Validation

Final validation is performed by the PR's six mandatory exact-head checks: Python 3.10, Python 3.13, Python 3.14, Package workflow / Windows, Generated documentation / documentation-baseline --check, and Repository state / project-state --check.


## Merge and closure

- Pull Request: [#830](https://github.com/xbodzio7/Dacia-Knowledge-Base/pull/830)
- Exact reviewed PR head: `fa5f25e766fda5e6a211bb35a1b6a99d428d36a4`
- Required exact-head checks: all six passed.
- Merge commit: `0ad4a78c9d051116f20d288ef6cffaccb5e7f2ac`
- Verified merged state: `merged=true`; current `main` points to the merge commit.
- Canonical project state and generated state summary are handed off to the next Spring MY26 cennik package.
