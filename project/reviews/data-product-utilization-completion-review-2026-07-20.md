# Data Product Utilization Completion Review

## Scope

This review determines whether the current `Data Product Utilization` phase has another clearly justified autonomous package that can use the existing source-backed portfolio without introducing a new architecture or expanding source data.

The review covers the complete consumer path delivered through the current milestone. It does not change public release bytes, source data, reporting scopes or product semantics.

## Delivered system

### User-facing data products

The repository now provides:

- a deterministic configuration shortlist CLI,
- a self-contained interactive shortlist HTML,
- persistent browser selection with deterministic JSON and TXT export,
- scope-safe comparison JSON, Markdown, CSV and HTML,
- a transactional comparison bundle with SHA-256 manifest,
- a deterministic six-sheet XLSX workbook,
- source and provenance surfaces that preserve dates, evidence and independent reporting scopes.

### Immutable distribution

The existing products can be published as one deterministic, versioned GitHub Release with:

- an immutable semantic version and tag,
- one canonical ZIP,
- an external release manifest,
- `SHA256SUMS`,
- an exact repository commit,
- reproducible release inventory and checksums.

The public reference release is `data-products-v1.0.0`.

### Verified consumption

A consumer can request one explicit release version and receive a workspace only after:

- GitHub Release and tag identity verification,
- exact three-asset inventory verification,
- size and checksum verification,
- deterministic ZIP and member verification,
- safe extraction without `extractall`,
- manifest-to-tag commit equality,
- transactional publication of the complete workspace.

### Offline navigation

Every verified workspace contains one deterministic root `index.html` that:

- works without JavaScript, a web server or external runtime resources,
- links the shortlist, workbook, bundle manifest, release notes and every comparison scope,
- links the original provenance assets,
- preserves release identity and scope boundaries,
- is byte-identical on Linux and Windows for the same release.

### Lifecycle integrity

An existing workspace can be verified later, fully offline and read-only. The verifier checks:

- all three original assets,
- the complete extracted member inventory,
- file sizes and SHA-256 values,
- exact deterministic index bytes,
- every local index link,
- the absence of external runtime dependencies,
- release, configuration and scope identity consistency.

It rejects damage without repairing or further modifying the workspace.

### Consumer documentation

One validated Polish-language guide now covers:

- immutable release download,
- offline navigation,
- shortlist selection,
- existing workbook and scope reports,
- custom comparison-bundle generation,
- provenance and independent checksums,
- recovery after detected corruption,
- later lifecycle verification,
- semantic boundaries around missing data, scopes, inference, rankings and recommendations.

Every documented unified-CLI command and product path is checked in CI together with the public reference release.

## Completion assessment

The phase goal was to turn the existing source-backed data into usable, reproducible and verifiable products without expanding the source portfolio.

That goal is complete:

1. products can be generated deterministically,
2. products can be distributed immutably,
3. products can be downloaded by explicit version,
4. products can be navigated offline,
5. users can create their own scope-safe comparison bundles,
6. workspaces can be re-verified throughout their lifetime,
7. the complete workflow is documented and validated on Linux and Windows.

No material consumer lifecycle step remains missing inside the current repository-owned, checkout-based architecture.

## Remaining opportunities assessed

### Standalone consumer-tool distribution

A user currently needs a repository checkout and Python to run the downloader and verifier. Packaging these tools for users without the repository could improve adoption.

This is not a small continuation of the current phase. It requires new architecture decisions, including:

- distribution format: Python package, zipapp, standalone executable or container,
- supported operating systems and architectures,
- dependency and runtime policy,
- signing, provenance and checksum policy for the tool itself,
- installation and update channel,
- release cadence and compatibility guarantees,
- support and security-maintenance expectations.

This option crosses the repository stop condition `new_domain_or_architecture_decision`.

### Source-backed data expansion

The project could return to adding models, configurations, options, packages or technical observations.

This requires a new source priority and evidence plan. It changes the milestone from product utilization to source acquisition and data coverage, and crosses the stop condition `scope_expansion_beyond_current_milestone`.

### Additional convenience features

Previously assessed convenience ideas do not justify another package:

- a mutable `latest` alias weakens reproducibility,
- republishing immutable `v1.0.0` would violate the release contract,
- automatic browser launching adds platform side effects without improving data integrity,
- platform-specific shortcuts or symlinks reduce portability,
- duplicating the local index inside a future archive does not improve the existing reference release,
- more wrapper commands would duplicate the validated consumer guide and unified CLI.

### Maintenance mode

The project can remain operational without starting another feature package. Maintenance mode would include:

- in-scope bug fixes,
- dependency and GitHub Actions maintenance,
- CI reliability and security fixes,
- documentation corrections,
- intentional creation of a new immutable data-product release when source-backed repository content changes.

This is a valid steady state, not a new utilization product.

## Decision

The `Data Product Utilization` phase is complete.

There is no further autonomous package that is both clearly justified and inside the current architecture and source-data boundaries.

Starting another milestone now requires a strategic choice by the maintainer.

## ACTION_REQUIRED boundary

### Reason

The remaining meaningful directions require either a new distribution architecture or an explicit expansion of source-data scope. The repository autonomy policy requires maintainer input for both boundaries.

### Required action

Choose one strategic direction before another implementation package begins.

### Options and consequences

#### Option 1 — Standalone Consumer Tool Distribution

Package the downloader, workspace verifier and selected consumer commands for users without a repository checkout.

Consequences:

- improves accessibility for non-developer consumers,
- creates a new release and support surface,
- requires format, platform, signing, update and compatibility decisions,
- does not expand source data.

#### Option 2 — Source-Backed Data Expansion

Start a new data milestone focused on explicitly selected models, configurations or missing evidence.

Consequences:

- increases knowledge-base coverage,
- requires named source priorities and evidence boundaries,
- resumes import, validation and reporting work,
- expands beyond the completed utilization milestone.

#### Option 3 — Maintenance Mode

Do not begin a new feature milestone.

Consequences:

- preserves the current stable products and public release workflow,
- limits work to bugs, security, dependencies, CI and documentation,
- avoids new architecture and source commitments,
- feature development resumes only after a later explicit decision.

### Resume stage

After the maintainer selects an option, update `project/state.json` with the new phase and first planned package, then create the corresponding package branch from current `main`.
