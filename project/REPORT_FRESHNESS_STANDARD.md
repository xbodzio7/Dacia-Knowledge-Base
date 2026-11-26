# Report Provenance and Freshness Standard

**Status:** Active  
**Applies to:** Machine-readable and human-readable analytical reports under `data/reporting/` and package reports under `project/packages/`.

## 1. Purpose

A report is a dated analytical result, not a live view of repository data. A report must never be presented as current merely because its file remains in the default branch.

## 2. Required provenance for new or materially refreshed reports

The machine-readable report must include a top-level `report_metadata` object with:

- `schema_version`: integer, initially `1`;
- `report_id`: stable, unique identifier;
- `generated_at`: ISO-8601 timestamp with timezone;
- `reviewed_on`: source/evidence review date when distinct from generation date;
- `repository`: exact repository full name;
- `base_commit_sha`: exact commit SHA whose repository tree was analysed;
- `input_files`: non-empty array of repository-relative paths, each with its Git blob SHA and SHA-256 of the file bytes;
- `scope`: concise statement of included and excluded evidence;
- `status`: one of `current`, `historical`, `needs_review`, or `blocked`.

The Markdown companion must display the report ID, generation/review date, analysed commit SHA, status and scope. These fields must agree with the JSON report.

Do not fabricate a timestamp, commit, hash or file identity. If exact input hashes or the analysed commit cannot be established, use `blocked` and explain the missing evidence.

## 3. Freshness rules

A report is current only when all of the following are true:

1. its declared repository matches the current repository;
2. its input paths exist;
3. every recorded Git blob SHA and content SHA-256 still matches the current input;
4. its declared scope remains valid;
5. its unresolved findings have been rechecked against current canonical data and source evidence;
6. the Markdown companion agrees with the machine-readable report.

A changed input makes the report `needs_review`; it does not automatically make every conclusion false. Preserve the original input fingerprints and analysed commit while the report is awaiting review. The validator must accept changed input hashes only when `report_metadata.status` is explicitly `needs_review`; all other statuses fail closed. Re-evaluate the report before it can return to `current`.

A report whose inputs remain unchanged may still require review when source identity, interpretation, scope or a referenced decision changes. Input hashes are necessary but not sufficient evidence of freshness.

## 4. Finding lifecycle

Every actionable finding must have a stable `finding_id` and one of these states:

- `open`: currently reproduced and supported;
- `resolved`: closure is supported by exact current evidence;
- `not_reproducible`: the former finding could not be reproduced; retain the explanation and evidence;
- `out_of_scope`: deliberately excluded under an explicit scope rule;
- `needs_review`: evidence is incomplete or changed.

A finding must record its evidence references and last verification date. A prior `open` finding must never be copied into a new report without rechecking it. A prior `resolved` finding must not be reopened without new contradictory evidence.

## 5. Historical preservation

Do not overwrite historical reports to make them appear current. Preserve the original review date and result. A refreshed analysis receives a new report identity or a clearly versioned successor, with a supersedes relationship where applicable.

The Markdown companion is a rendered explanation, not an independent source of truth. Machine-readable JSON is canonical for structured findings; source files and master data remain canonical for domain facts.

## 6. Change workflow

When source/master data or a referenced decision changes:

1. identify dependent reports and package summaries;
2. compare their recorded input identities with the candidate tree;
3. mark affected reports `needs_review`;
4. re-evaluate every open and previously unresolved finding;
5. regenerate Markdown from the reviewed structured result where a canonical generator exists;
6. verify JSON/Markdown parity and the final exact commit;
7. record the refreshed report and its provenance in the package closure.

Never silently update only the prose while leaving stale JSON, or vice versa.

## 7. Rollout and compatibility

This contract applies immediately to new and materially refreshed reports. Existing reports without `report_metadata` are historical/legacy and must not be retroactively labelled current. They are migrated only when naturally revisited or when selected as a current deliverable.

The automated validator introduced by the follow-up implementation must fail closed for newly registered reports, while allowing explicitly classified legacy reports to remain readable. It must not require every historical report in the repository to be rewritten in one migration.

## 8. Related controls

This standard supplements, and does not replace:

- `package-preflight` structural validation;
- `project-state --check` and generated state checks;
- `documentation-baseline --check`;
- exact-head CI, technical review and source-fidelity review;
- source archive manifest integrity checks.



## 9. Automated enforcement

The canonical registry is `data/reporting/report_registry.json`. Every new or materially refreshed analytical report covered by this standard must be registered with its JSON and Markdown companion paths. New entries are strict by default: missing metadata, missing inputs, unsafe paths, malformed hashes, changed inputs on reports not marked `needs_review`, invalid finding states or JSON/Markdown drift fail `python tools/dkb.py report-freshness`. A report marked `needs_review` may retain its original stale input fingerprints; do not rewrite those hashes or the analysed commit until the report has actually been re-evaluated. The only compatibility exception is an explicit `legacy: true` entry; a legacy report cannot claim `current` status. Legacy classification is temporary and must be removed when the report is substantively refreshed. The validator checks both Git blob SHA-1 and content SHA-256 for each declared input.
