# Bigster Tribrid 150 4x4 — engine power gap closure

**Date:** 2026-11-05  
**Source:** registered Polish Bigster MY26 price list effective 2026-10-01, page 6, section SILNIKI.

## Imported observations

Added three source-linked `engine_power` observations, each **103 kW**, for the Expression, Extreme and Journey Tribrid 150 4x4 automatic configurations. The source states `103 (140)` at `5 000` rpm. The maximum hybrid-system power row is kept separate: `103 (140) + 10 (13)`; it is not normalized as engine power and no arithmetic total is inferred.

## Evidence and boundaries

- Source PDF page: 6.
- Engine maximum power: 103 kW (140 KM).
- Engine speed at maximum power: 5,000 rpm.
- Configurations: Expression, Extreme and Journey, all Tribrid 150 4x4 automatic.
- Observation date: 2026-10-01, matching the registered source edition.
- No existing observations were overwritten.
- The user additionally supplied the official price list effective 2026-11-02. Its page 6 repeats the same engine-power value and retains the separate hybrid-system-power row. Its technical-data footnote still says data status 2026-10-01; it therefore confirms, rather than supersedes, this technical observation. The uploaded binary has SHA-256 `592f28852118b57fe6bdef75864ea479d9e01bb9af9a166108014eff4ae85b5b` and size 1,995,398 bytes. It is not yet archived in the repository, so it is not registered as a repository source in this package.

## Verification

The declarative import spec is covered by the shared import-spec contract and a focused test that checks all three configurations, source page text, registered source hash, and exact master-row materialization.
