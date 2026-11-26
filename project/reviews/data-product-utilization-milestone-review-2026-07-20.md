# Data Product Utilization Milestone Review

## Scope

This milestone review evaluates the complete consumer path delivered without expanding source data:

1. deterministic configuration products,
2. immutable versioned release assets,
3. verified public release download and safe extraction,
4. one deterministic offline workspace index.

The review does not change `data-products-v1.0.0`, add sources, reinterpret comparison values or select a new publication channel.

## Delivered consumer path

The repository now supports a complete explicit flow:

```text
public GitHub Release version
  -> tag and asset identity verification
  -> streamed download of the three canonical assets
  -> manifest and SHA-256 verification
  -> safe extraction of verified members
  -> deterministic local index.html
  -> shortlist, workbook, scope reports, release notes and provenance
```

The public `v1.0.0` release remains immutable. A consumer names the exact semantic version, receives a workspace only after the tag commit, asset inventory, checksums and archive members pass, and can then enter the result through one self-contained page.

## Milestone assessment

### Usability

The consumer no longer needs to clone the repository, understand the archive layout or preserve terminal output to find the principal products. The root index links the shortlist, workbook, comparison manifest, release notes, every comparison scope and the original provenance assets.

### Integrity at creation time

The downloader is fail-closed and transactional. It rejects mutable version aliases, release identity mismatches, unexpected assets, corrupt files, unsafe archive members and malformed comparison manifests. The workspace is published by an atomic directory rename only after the derived index is complete.

### Portability

The product path is offline after download. The index contains no JavaScript or external runtime resources and is byte-identical between Linux and Windows for the same verified release.

### Data boundaries

No product ranks configurations, recommends a vehicle, fills absent observations or compares configurations across independent reporting scopes. The milestone uses only the existing source-backed portfolio.

## Remaining consumer risks

The initial downloader proves integrity only while creating a workspace. Afterward, a workspace may be copied, synchronized, archived, edited or partially deleted. There is currently no single command that can later prove that:

- the three original assets still match their checksums,
- every extracted release member still matches the immutable manifest,
- no unexpected file has appeared inside `contents/`,
- the root `index.html` still equals the deterministic rendering of the verified manifests,
- every local index link still resolves inside the workspace,
- release identity and scope/configuration counts remain mutually consistent.

This is now the highest-value gap because the delivery and navigation layers are complete; repeated integrity verification is the missing lifecycle operation.

## Options considered

### Republish `v1.0.0` with the index inside the archive

Reject. The release is immutable, and the index is deliberately a consumer-side derived file that can be generated from already verified manifests. Republishing would break the version contract without improving post-copy integrity.

### Add a mutable `latest` download alias

Reject. It weakens reproducibility and makes later verification ambiguous. Explicit semantic versions remain required.

### Automatically launch the browser after download

Defer. Browser launching is a platform side effect, is unsuitable for CI and remote shells, and does not address integrity after the workspace is moved.

### Add an offline workspace verification CLI

Select. It reuses the existing release verifier and deterministic index renderer, introduces no network or source-data dependency, and gives both people and automation a stable way to validate a workspace throughout its lifetime.

## Decision

Select **Local Data Product Workspace Verification CLI** as the next package.

The command will accept an existing workspace directory and perform a read-only, fully offline verification.

## Planned contract

The command will:

- require an explicit workspace directory,
- verify the three canonical files under `assets/` with the existing release verifier,
- require the workspace release version, tag and commit to remain internally consistent,
- hash every expected file under `contents/` against the external release manifest,
- reject missing, duplicate, unsafe or unexpected content members,
- reconstruct the expected `index.html` bytes from verified manifests and compare them with the stored page,
- parse the stored index and require every local link to resolve to a file inside the workspace,
- reject external runtime dependencies while allowing only the canonical displayed GitHub Release link,
- print a concise human summary and optionally emit deterministic JSON for automation,
- never repair, rewrite, download or delete workspace files.

## Validation plan

Tests should cover a valid synthetic workspace, missing or changed assets, changed extracted members, unexpected content files, unsafe manifest paths, an edited or missing index, broken and escaping links, release identity mismatches, deterministic JSON output and proof that verification is read-only.

A read-only Linux/Windows live workflow should first create a fresh workspace from public `v1.0.0`, verify it with the new command, then corrupt one copied member and prove that the command fails without modifying either workspace.

## Milestone outcome

The public release, verified download and offline navigation path are complete and independently validated. The next package extends that path from one-time safe creation to repeatable lifecycle integrity without expanding the source-data portfolio or changing release bytes.
