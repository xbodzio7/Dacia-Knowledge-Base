# Post-Cross-Model Priority Selection Review

Date: 2026-07-26

## Selection

The selected next package is `Data Products v1.8.0 Release Preparation`.

Public `data-products-v1.7.0` is immutable and contains eighty-three archive members. The repository now has a fully closed and verified eighty-five-member candidate containing two additional consumer products:

- `cross-model/cross-model-comparison-view.json`;
- `cross-model/cross-model-comparison-view.html`.

Publishing the completed work has the highest immediate consumer value, requires no new architecture or evidence decision and reuses the entire deterministic release lifecycle.

## Selection policy

Candidates were scored from one to five using:

- consumer value — 30%;
- evidence readiness — 25%;
- existing tooling reuse — 20%;
- low implementation risk — 15%;
- dependency clearance — 10%.

A candidate may be selected only when it does not require ambiguous source interpretation, an unavailable exact configuration relationship or a new architecture decision.

## Ranked candidates

1. `Data Products v1.8.0 Release Preparation` — 100, selected.
2. `Cross-Model Navigation Usability Review` — 84, follow-up after publication.
3. `PDF Candidate Extraction Automation Review` — 67, strategic later.
4. `Exact Configuration Expansion Review` — 57, blocked by evidence.
5. `Spring Source Foundation Review` — 46, blocked by missing exact current sources and an approved scope.

## Release rationale

A minor version is appropriate because the release gains both a new machine-readable product and a new user-facing navigation surface. The underlying configuration data and comparison semantics remain unchanged:

- 72 active configurations;
- 19 independent scopes;
- 114 within-scope pairs;
- 1695 recorded differences;
- no cross-scope pairs;
- no ranking, recommendation or inferred value.

## v1.8.0 preparation contract

The preparation package must:

- target version `1.8.0` and tag `data-products-v1.8.0`;
- build exactly eighty-five archive members from a green source commit;
- include the two `cross-model` products;
- verify deterministic generation;
- verify the cross-model JSON and static HTML inside the offline workspace;
- prepare exact preflight evidence for a later immutable tag-to-commit publication;
- retain the established three-asset release set.

It must not import new data, expand the cross-model UI, generate rankings or recommendations, infer missing facts or create pairs between reporting scopes.

## Deferred candidates

A richer cross-model interface may follow only after the completed foundation is publicly delivered. PDF automation remains valuable but is an internal productivity investment. Exact configuration expansion and Spring work remain blocked until exact sources and relationships are available.

## Next package

`Data Products v1.8.0 Release Preparation` — freeze release identity and notes, build and verify the deterministic eighty-five-member candidate, validate the offline cross-model products and prepare exact preflight evidence without publishing yet.
