# Interface Source Coverage Repair

Date: 2026-08-01

Status: **complete**

## Goal

Resolve the reported comparison-interface defects and exact source-price coverage gaps without expanding the model, version, configuration or attribute domains.

## Result

- Spring has an official registered model image.
- The comparison selection panel becomes non-sticky while the comparison is open, so it no longer covers the sticky table headers.
- Parameter categories can be collapsed individually or hidden/shown globally; the state persists for the browser session.
- Sandero TCe 100 remains `direct_injection` because this is the exact source-backed value in the official Polish MY26 price list dated 2026-07-03.
- Nineteen exact Sandero and Sandero Stepway option/package price mappings were added from that source.
- The interface distinguishes an absent database record, a missing price mapping and a price not stated in the source.
- Technical and equipment comparison cells expose source and observation-date provenance.

## Non-inference boundary

No value, availability state or amount is copied between configurations. A blank source amount is never treated as zero or estimated.

## Follow-up

`registered_source_completeness_reconciliation_001` audits the remaining active comparison and optional-price gaps against registered exact sources and classifies them without adding models or domains.

## Validation

- Dedicated interface/source-coverage regression tests.
- Existing shortlist, comparison, selection and pricing contracts.
- Complete Linux, Windows and supported-Python quality matrix on the final Pull Request head.
