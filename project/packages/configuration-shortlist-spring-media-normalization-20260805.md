# Configuration Shortlist Spring Media Normalization

## Package

- Package ID: `configuration_shortlist_spring_media_normalization_001`
- Kind: `user_interface_repair`
- Date: 2026-08-05
- Status: complete

## Purpose

Normalize Spring with the same official Dacia Polska car-picker media path used by the shared model catalogue, while preserving deterministic offline rendering and leaving every other model image unchanged.

## Official source

- Page: `https://www.dacia.pl/hybrydy-i-elektryczne/spring-miejski.html`
- Image mechanism: `d_brandSite_carPicker_1.png`
- Captured on: `2026-08-05`
- Cached content: `assets/model-media/spring-cc7712919408010a.png`
- SHA-256: `cc7712919408010ac2cfcb5a33a358def1affef5e7e3b9476b059be9f7cfb2b7`

The packshot is the current transparent/neutral official Spring image exposed by the Dacia Polska model page. It replaces the separate parking-scene image previously sourced from `3dv2.renault.com`.

## Changes

- added `spring` to `project/sources/dacia-pl-model-media-20260724.json`;
- added the verified PNG to the deterministic local model-media cache;
- preserved per-model capture dates so the older unchanged model entries retain their original catalogue date;
- removed `project/sources/dacia-pl-spring-model-media-20260801.json`;
- removed `_apply_supplemental_model_media(...)` and its Spring-only source contract;
- removed Spring-only `object-fit: cover`, scale, position and frame sizing;
- removed the JavaScript class assignment used only by that special crop;
- retained the forced dark theme, card layout, equipment groups, search, comparison and offline operation.

## Boundaries

- no image URL or cached bytes changed for Sandero, Sandero Stepway, Jogger, Duster or Bigster;
- no master data, configuration identity, price, equipment or technical observation changed;
- no inference was introduced;
- immutable v1.16.0 release assets remain unchanged.

## Verification

Focused regression coverage verifies:

- the shared source contains the official Spring car-picker URL;
- the supplemental source and override code are absent;
- the cached PNG exists and matches the pinned SHA-256;
- the Spring-only crop class is absent from CSS, JavaScript and rendered release HTML;
- all external shortlist URLs remain official Dacia Polska URLs;
- the model-media cache verifies offline.

## Next package

`configuration_shortlist_configurator_observation_filters_001`
