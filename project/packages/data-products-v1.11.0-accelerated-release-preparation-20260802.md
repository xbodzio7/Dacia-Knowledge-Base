# Data Products v1.11.0 Accelerated Release Preparation

Date: 2026-08-02

Package ID: `data_products_v1_11_0_accelerated_release_preparation_001`

Status: **complete**

## Purpose

Prepare one immutable minor release from the repository state reached after the fully closed Spring legacy-PDF assimilation milestone.

The public `data-products-v1.10.0` remains immutable.

## Source-backed delta

The release adds the 36 observations approved and materialized by the Spring non-conflicting technical review and migration packages for the three existing passenger configurations:

- permanent-magnet synchronous motor type;
- LFP traction-battery chemistry;
- electric steering;
- nine common body dimensions.

The release preserves the exact Spring brochure source, observation date, configuration identity and passenger-vehicle scope.

## Preserved boundaries

The release does not import, replace or generalize:

- the 204 kg battery mass or 354 V stated only for MY2025 dealer stock;
- the unqualified 24.3 kWh battery capacity;
- charging times without complete SOC, power and option context;
- range or maximum-speed values already represented by later sources;
- wheel-qualified ground clearance;
- Cargo, accessory or interior-storage facts into passenger configurations;
- one charging-cable source state over another.

No cross-scope pair, ranking, recommendation or inferred value is introduced.

## Publication architecture

Preparation installs a temporary publisher on `main`, but does not create a tag or release. A separate publication Pull Request adds one trigger receipt. Because the publisher already exists on the default branch before that merge, the publication workflow can:

1. check out the exact publication merge SHA;
2. prove that tag and release `data-products-v1.11.0` are absent;
3. run focused release contracts and canonical state verification;
4. build the assets twice and compare them byte for byte;
5. verify the release assets and extracted offline workspace;
6. publish the immutable archive, manifest and checksums against the exact SHA;
7. download and compare the public assets;
8. record the publication and remove the temporary publisher, recorder and trigger.

## Target

- version: `1.11.0`;
- tag: `data-products-v1.11.0`;
- archive: `dacia-knowledge-base-data-products-v1.11.0.zip`;
- public assets: archive, manifest and `SHA256SUMS`.

## Acceptance criteria

- release notes describe the bounded Spring delta and every preserved deferral;
- persistent release-contract tests pass;
- the final preparation Pull Request head passes the complete Quality matrix;
- publication runs only after a separate trigger Pull Request is merged;
- publication uses the exact merge SHA and proves double-build byte identity;
- the extracted offline workspace passes verification;
- public assets are byte-identical to the verified local build;
- the publication receipt advances canonical state without reopening the closed source milestone.

## Next package

`data_products_v1_11_0_publication_001` will add the publication trigger on a separate branch and publish only after its final head passes complete Quality.
