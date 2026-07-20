# Local Data Product Workspace Verification CLI

## Status

Implementation package for the `Data Product Utilization` phase.

## Goal

Verify an existing local data-product workspace fully offline and read-only after it has been copied, synchronized, archived or otherwise moved beyond the original download operation.

## Command

```bash
python tools/dkb.py data-product-workspace-verify \
  --workspace-directory ../dkb-data-products-v1.0.0
```

For automation:

```bash
python tools/dkb.py data-product-workspace-verify \
  --workspace-directory ../dkb-data-products-v1.0.0 \
  --json
```

## Verification contract

The command:

- requires exactly `assets/`, `contents/` and `index.html` at the workspace root,
- reuses the canonical release verifier for the three original assets, manifest, `SHA256SUMS`, ZIP inventory and deterministic ZIP metadata,
- requires every extracted content file to match the manifest path, size and SHA-256,
- rejects missing, additional, unsafe, unsupported or symbolic-link content entries,
- reconstructs the expected deterministic `index.html` from the verified manifests and compares its exact UTF-8 bytes,
- validates every local index link and rejects query strings, fragments, escaping paths or missing targets,
- rejects runtime `src` and form `action` URLs,
- allows exactly the canonical displayed GitHub Release link,
- returns a deterministic report without generation time, hostname or absolute workspace path.

## Read-only boundary

Verification never downloads, repairs, rewrites, deletes or normalizes workspace files. Any failure returns a non-zero exit status and leaves the workspace unchanged.

## Output

The human summary reports release version, tag, commit, snapshot date, asset and extracted-file counts, configuration and scope counts, local index-link count and the index SHA-256.

The optional JSON report uses schema version 1 and stable key order for the same verified workspace.

## Validation

Ten explicit synthetic checks cover a valid workspace, deterministic reporting, read-only behavior, changed assets, changed extracted members, missing or unexpected content, edited index bytes, unexpected root entries, unsafe links, runtime resources, CLI output and unified-command forwarding.

The existing Linux/Windows `Verified Data Product Release Download` workflow also:

1. creates a fresh workspace from public immutable `v1.0.0`,
2. verifies it fully offline with the new command,
3. copies and corrupts one extracted member,
4. proves that verification fails,
5. proves that the verifier does not further modify the corrupted copy,
6. retains byte-identical workspace-index validation across both systems.

## Non-goals

- repairing damaged workspaces,
- refreshing or replacing release assets,
- contacting GitHub or any other network service,
- adding mutable version aliases,
- changing the immutable public release,
- expanding or reinterpreting source data.
