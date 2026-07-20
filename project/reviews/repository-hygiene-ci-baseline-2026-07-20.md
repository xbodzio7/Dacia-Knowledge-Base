# Repository Hygiene and CI Baseline

## Scope

This maintenance review establishes the first operational baseline after entry into `Maintenance Mode`.

It covers:

- open Pull Request and issue hygiene,
- the current Pull Request workflow surface,
- evidence from the completed strategic-direction change,
- selection of one bounded CI reliability package.

It does not change source data, product code, workflow behavior, public release assets or product semantics.

## Repository hygiene

At the start of the review, draft Pull Request #105, `Selected Jogger Technical Specification Import`, remained open even though its selected 312-observation denominator had already been delivered by merged Pull Request #106, `Jogger MY26 Technical Specification Import`.

Pull Request #105 was closed as superseded with an explanatory comment. Its remote branch was retained because the repository policy does not delete remote branches automatically.

After that cleanup and the merge of Pull Request #169, the repository has:

- zero open Pull Requests,
- zero open issues,
- no unresolved review thread or CI repair package identified from the active backlog.

## CI inventory

The strategic-direction Pull Request #169 changed only:

- `project/state.json`,
- `project/STATE_SUMMARY.md`,
- one document under `project/reviews/`.

That three-file governance-only change triggered 15 workflows:

1. `Quality`,
2. `Configuration Selection Export`,
3. `Versioned Data Product Release`,
4. `Verified Data Product Release Download`,
5. `Configuration Comparison Workbook`,
6. `Configuration Comparison Bundle`,
7. `Configuration Shortlist`,
8. `Configuration Shortlist HTML`,
9. `Configuration Comparison HTML`,
10. `Sandero Eco-G 120 Manual Reporting`,
11. `Sandero Stepway Eco-G 120 Automatic Reporting`,
12. `Jogger Eco-G 120 Manual Reporting`,
13. `Jogger Eco-G 120 Automatic Reporting`,
14. `Jogger TCe 110 Manual Reporting`,
15. `Jogger Hybrid 155 Automatic Reporting`.

All 15 completed successfully. `Quality` run #922 passed on Python 3.10, Python 3.13 and the Windows package-state job. The product, release, download, workbook, shortlist, selection, comparison and reporting workflows also passed.

## Trigger audit

### Quality

`.github/workflows/quality.yml` intentionally has an unrestricted `pull_request` trigger.

This is appropriate for maintenance mode because it contains the canonical project-state check and remains the repository-wide safety gate.

### Specialized workflows

Fourteen specialized workflows also ran for the governance-only change.

The trigger review found:

- thirteen specialized workflows use an unrestricted `pull_request` trigger,
- `Verified Data Product Release Download` uses a path allowlist that includes broad `project/**`,
- none of the specialized workflows distinguishes governance-only state and review documents from code, data, tests or workflow changes.

The result is correct but unnecessarily expensive validation for changes that cannot affect generated products or reporting behavior.

## Selected maintenance package

The next package is `Governance-Only CI Scope Reduction`.

It will preserve `Quality` on every Pull Request and add one shared exclusion contract to the fourteen specialized workflows.

A specialized workflow may be skipped only when every changed file is contained in this governance-only set:

- `project/state.json`,
- `project/STATE_SUMMARY.md`,
- `project/reviews/**`.

Any Pull Request that also changes code, data, tests, documentation outside this set or a workflow file must continue to run the affected specialized workflows.

## Implementation contract

The package must:

1. leave `.github/workflows/quality.yml` unrestricted,
2. add equivalent `pull_request.paths-ignore` entries to all fourteen specialized workflows,
3. preserve every existing `workflow_dispatch` trigger,
4. preserve all jobs, permissions, matrices, artifact generation and commands,
5. preserve release-publication safety boundaries,
6. avoid source-data, Python-code and product-semantic changes,
7. verify that every edited workflow remains valid YAML,
8. run the complete current workflow set because the implementation Pull Request changes the workflow files themselves,
9. perform a later governance-only verification change to confirm that only `Quality` is selected.

## Boundary

This package is a CI scope correction, not a reduction of product validation.

It does not:

- disable `Quality`,
- skip checks for code, data, test or workflow changes,
- change branch protection,
- change supported Python or Windows coverage,
- alter release assets or immutable release identity,
- introduce dependencies,
- start a feature or source-expansion milestone.

## State transition

- phase: `Maintenance Mode`
- completed package: `Repository Hygiene and CI Baseline`
- selected next package: `Governance-Only CI Scope Reduction`
- verified baseline: unchanged at 667 tests
- reference delivery: unchanged at `Data Product Consumer Guide` Pull Request #167
