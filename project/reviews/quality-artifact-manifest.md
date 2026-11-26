# Quality Artifact Manifest

## Portfolio review

Quality run #177 published the standard `dacia-knowledge-base-build` bundle with 22 payload files:

- the verified SQLite database,
- the quality log and structured summary,
- documentation baseline outputs,
- configuration completeness outputs,
- source coverage outputs,
- gap triage, source review, evidence and resolution outputs,
- configuration comparison outputs,
- the comparison item catalog,
- the validation report.

The bundle was complete, but it did not contain a machine-readable inventory. A consumer had to know the expected files in advance and could not validate individual file integrity after download.

## Candidate ranking

1. **Quality Artifact Manifest** — cross-cutting automation value, no report-semantic or archive-layout change.
2. Archive path normalization — useful, but potentially breaking for existing consumers.
3. Spreadsheet export — valuable for manual analysis, but adds a format and dependency surface.
4. Additional comparison filter — valuable reporting work, but does not solve bundle verification.

The manifest was selected because it improves every existing reporting output while preserving the current artifact contract.

## Implementation

`tools/quality_artifact_manifest.py` generates deterministic JSON from an explicit list of artifact files.

The manifest contains:

- schema version,
- logical artifact name,
- hash algorithm,
- payload file count,
- total payload size,
- one sorted entry per file with its name, media type, byte size and SHA-256.

It intentionally omits a generation timestamp so identical payloads produce identical manifests. The manifest does not include its own hash.

The tool rejects:

- missing input files,
- duplicate basenames,
- an output file included as an input,
- malformed or non-deterministically ordered manifests,
- missing, unexpected or duplicated files during verification,
- size or SHA-256 mismatches.

## Workflow integration

The Python 3.13 Quality job generates the manifest after all reports and the item catalog have succeeded:

```bash
python tools/quality_artifact_manifest.py \
  --output "${RUNNER_TEMP}/artifact-manifest.json" \
  --file ...
```

The resulting `artifact-manifest.json` is uploaded in the existing `dacia-knowledge-base-build` artifact. The existing artifact name, archive layout, retention period and failure behavior remain unchanged.

## Verified delivery candidate

Quality run #179 completed successfully on Python 3.10, Python 3.13 and Windows. GitHub Actions published `dacia-knowledge-base-build` with digest:

```text
sha256:d43fc02b38f81ac27fc7ca638a8df78086639ccfe2eca514fc53d92e4fef3a53
```

Inspection of the downloaded ZIP confirmed:

- 23 files in the archive: 22 payloads plus `artifact-manifest.json`,
- exactly one manifest,
- `file_count` equal to 22,
- `total_size_bytes` equal to 3,157,598,
- sorted entries from `configuration-comparison-differences.csv` through `validation_report.md`,
- successful verification of every declared size and SHA-256.

## Consumer verification

After extracting the artifact:

```bash
python tools/quality_artifact_manifest.py \
  --verify extracted/artifact-manifest.json \
  --root extracted
```

A successful verification proves that all 22 declared payload files are present and byte-identical to the files hashed by the Quality workflow.

## Regression contract

`tests/quality_artifact_manifest_contract.py` covers:

- deterministic sorted generation,
- successful verification across nested extracted paths,
- content tampering detection,
- duplicate basename rejection,
- missing and unexpected file rejection,
- generation and verification CLI paths.

The contract is run explicitly on Python 3.10 and Windows without changing the established 410-test documentation baseline.

## Next package

The next reporting package is **Configuration Comparison Difference Context Filter**. The catalog now exposes exact contexts and the artifact bundle can be integrity-checked, so the next user-facing improvement is to allow an exact context to constrain the flat difference CSV while preserving all default outputs.

## Scope boundary

This package does not change:

- master data,
- report semantics or row ordering,
- existing report formats,
- artifact names, paths or retention,
- the local `quality` stage list,
- evidence classifications.
