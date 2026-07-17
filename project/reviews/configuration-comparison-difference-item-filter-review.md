# Configuration Comparison Difference Item Filter Review

Date: 2026-07-17

## Scope

This review closes the roadmap package **Configuration Comparison Difference Item Filter Review** after merge of PR #60.

Reviewed evidence:

- PR #60 metadata and complete changed-file list,
- implementation patch in `tools/configuration_comparison.py`,
- focused unit-test patches in `tests/test_configuration_comparison.py` and `tests/test_dkb_cli.py`,
- verified snapshot recorded in the PR description,
- GitHub Actions Quality run #153 for commit `74d2104083671d63acff51bee9ff31b0c67ae281`.

The review did not rerun the repository locally. Runtime conclusions below rely on the committed tests and the successful GitHub Actions run.

## Result

The package is accepted without corrective follow-up.

The implementation preserves the intended separation of concerns:

- `--pair-type` narrows the comparison report,
- `--difference-domain` narrows only the flat difference CSV,
- `--difference-item-code` narrows only the flat difference CSV,
- JSON, Markdown, report summaries and the global evidence snapshot remain unchanged by CSV-only filters.

## Verified behaviour

The merged package establishes the following current snapshot:

- 21 active configuration pairs,
- 305 default difference rows,
- 109 known item codes,
- no current item-code collisions between `prices`, `technical` and `equipment`,
- 34 `co2_emissions` difference rows in the full report,
- 2 `co2_emissions` rows for `same_version_different_transmission`,
- known items with no rows after composition produce a valid header-only CSV,
- unknown item codes are rejected before an output CSV is written,
- JSON and Markdown bytes remain unchanged when the item filter is used,
- Quality run #153 completed successfully with 410 tests and 14 quality steps.

## Implementation review

### Full-scope validation

Item-code validation is intentionally based on the full active comparison report. When `--pair-type` is present, the command builds an unfiltered validation report before validating the item code. This prevents a valid global code from being rejected merely because it is absent from the selected pair subset.

### Filter composition

The row pipeline applies filters in a safe order:

1. validate the controlled domain,
2. validate the requested item code,
3. iterate selected pairs and domains,
4. apply domain and item filters,
5. export only `different` rows backed by two recorded states.

This preserves header-only output for valid combinations with zero differences while still rejecting unsupported codes.

### Regression coverage

The focused tests cover:

- deterministic known-code discovery,
- composition with pair and domain filters,
- price-delta preservation,
- header-only output,
- unknown-code rejection,
- forwarding through the unified `dkb.py` CLI.

The successful full Quality workflow provides repository-wide regression coverage beyond the focused tests.

## Remaining limitation

The CLI now expects users to know one of 109 valid item codes, but it does not provide a deterministic way to discover them. The current absence of cross-domain collisions is documented and tested through the snapshot, but it is not yet exposed as a user-facing catalog or a dedicated invariant with domain metadata.

## Selected next package

### Configuration Comparison Difference Item Catalog

Add an optional deterministic catalog export to the existing `configuration-comparison` command.

Proposed scope:

- add `--difference-item-catalog-csv PATH`,
- generate one row per `(domain, item_code)` from the full active report,
- include `domain`, `item_code`, `item_name`, `category`, `context_count`, `comparison_count`, `equal_count`, `different_count` and `not_comparable_count`,
- keep ordering deterministic by domain and item code,
- explicitly reject cross-domain item-code collisions unless the catalog contract is changed to require domain-qualified selection,
- preserve existing JSON, Markdown and difference-CSV bytes by default,
- add focused unit and CLI-forwarding tests,
- do not change master data, evidence classifications, quality steps or workflow structure.

This is the smallest useful follow-up because it makes the existing filter discoverable and turns the current collision-free snapshot into an explicit, reviewable contract.

## Decision

The Difference Item Filter review is complete. The recommended next implementation package is **Configuration Comparison Difference Item Catalog**.
