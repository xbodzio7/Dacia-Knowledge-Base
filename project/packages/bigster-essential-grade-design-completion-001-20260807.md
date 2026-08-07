# Bigster Essential Grade Design Completion 001

Date: 2026-08-07  
Baseline main: `10b05d9b7b550681359700ecd0506b243f89a195`

## Purpose

Promote one independently complete current grade-level Design panel into the configurator UI readiness layer without converting exact-configuration prices into grade-wide prices.

## Current official grade page

The Bigster Essential page exposes a complete visible Design panel:

### Colours

- Biel Alpejska;
- Szary Schiste;
- Czarna Perła.

### Wheels

- `aluminiowe obręcze kół 17" 215 TERGAN`.

### Upholstery

- `tapicerka materiałowa essential`.

The same grade page lists both `mild hybrid-G 140` and `mild hybrid 140`, each with a six-speed manual transmission.

## Price boundary

The grade page does not expose individual prices for the Design choices. The current exact default configurator separately proves, for `bigster_essential_mildhybridg140_4x2_manual` only:

- Biel Alpejska — 0 PLN;
- Szary Schiste — +3000 PLN;
- Czarna Perła — +3000 PLN;
- 17" TERGAN — 0 PLN;
- Essential upholstery — 0 PLN.

Those prices are not projected to `mild hybrid 140`.

## UI impact

Bigster Essential can now expose the complete current grade-level colour/wheel/upholstery list before engine selection. Exact prices are overlaid only when the exact LPG configuration is selected and its independent exact source applies.

Complete visible grade-design coverage rises from 2 to 3 of 21 current grade surfaces:

- Sandero Journey;
- Bigster Expression;
- Bigster Essential.

## Repository impact

- reporting/integration only;
- no master-data mutation;
- no schema change;
- no inferred compatibility outside the grade page;
- no price projection between powertrains.

## Files

- `data/reporting/bigster_essential_grade_design_completion_20260807.json`
- `project/packages/bigster-essential-grade-design-completion-001-20260807.md`
- `project/state.json`
- `project/STATE_SUMMARY.md`
