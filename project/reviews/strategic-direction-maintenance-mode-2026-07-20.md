# Strategic Direction Decision — Maintenance Mode

## Scope

This review resolves the `ACTION_REQUIRED` boundary recorded by the completed `Data Product Utilization` phase.

It selects the next project direction without changing source data, public release assets, product semantics, reporting scopes or the existing consumer-tool architecture.

## Decision context

The completed utilization milestone already provides:

- deterministic shortlist, selection, comparison and workbook products,
- immutable semantic-versioned GitHub Release distribution,
- verified explicit-version download,
- deterministic offline workspace navigation,
- offline read-only lifecycle verification,
- validated Polish-language consumer documentation.

The completion review identified three possible directions:

1. standalone consumer-tool distribution,
2. source-backed data expansion,
3. maintenance mode.

## Selected direction

The project enters **Maintenance Mode**.

This is the only direction that continues useful repository work without making an unapproved architecture decision or expanding the accepted source-data milestone.

Maintenance Mode preserves the current stable product and release contracts while allowing bounded operational work.

## Maintenance contract

In-scope work includes:

- bug fixes within existing data and product semantics,
- security and dependency maintenance,
- GitHub Actions and CI reliability work,
- documentation corrections,
- repository hygiene,
- compatibility repairs for supported Python and Windows validation,
- publication of a new immutable data-product release only after source-backed repository content intentionally changes.

Out-of-scope work remains:

- a new standalone packaging or installation architecture,
- new platform, signing, update-channel or support commitments,
- new models, configurations, options, packages or technical evidence without a separate source-scope decision,
- mutable release aliases,
- changes to the immutable `data-products-v1.0.0` assets,
- ranking, recommendation or inferred-value semantics.

## Deferred strategic options

### Standalone consumer-tool distribution

This direction remains available for a later explicit architecture decision. It requires choices covering distribution format, supported platforms, signing, installation, updates, compatibility and security support.

### Source-backed data expansion

This direction remains available for a later explicit source milestone. It requires named source priorities, evidence boundaries and an accepted coverage denominator.

Neither deferred option is rejected permanently. Both require a new maintainer decision before implementation begins.

## Initial maintenance package

The first planned package is `Repository Hygiene and CI Baseline`.

Its goal is to establish a clean operational baseline by:

- resolving clearly superseded draft work,
- inventorying active workflows and maintenance surfaces,
- documenting the supported validation baseline,
- identifying only evidence-backed reliability, security or compatibility repairs,
- leaving source data and product behavior unchanged.

One immediate hygiene finding is draft Pull Request #105, `Selected Jogger Technical Specification Import`. Its selected 312-observation denominator was delivered by merged Pull Request #106, `Jogger MY26 Technical Specification Import`, and subsequent project baselines already include that work. The old draft can therefore be closed as superseded without deleting its remote branch automatically.

## State transition

- previous phase: `Data Product Utilization`
- previous package: `Data Product Utilization Completion Review`
- selected phase: `Maintenance Mode`
- current package: `Strategic Direction Decision`
- next package: `Repository Hygiene and CI Baseline`
- verified baseline: unchanged at 667 tests
- reference delivery: unchanged at `Data Product Consumer Guide` Pull Request #167

## Validation boundary

This decision package changes only durable project governance and generated state documentation.

It does not:

- modify source CSV or JSON data,
- modify release assets,
- modify Python product code,
- change dependencies,
- change workflows,
- create a new release or tag.
