# Configuration Shortlist Task-First Explorer UI

Date: 2026-08-08  
Package: `configuration_shortlist_task_first_explorer_ui_001`

## Goal

Change the interactive Dacia shortlist from a filter-first entry experience into a task-first explorer without replacing the proven shortlist, comparison or data-product architecture.

## Result

A new primary entry surface is injected above the metrics and detailed filters. It offers four direct tasks:

- **Skonfiguruj samochód** — opens the existing eight-step configurator path;
- **Porównaj wersje** — moves directly to the existing multi-configuration selection/comparison area;
- **Przeglądaj modele** — moves directly to the model picker;
- **Sprawdź źródła** — opens the exact configurator-observation evidence controls where available.

The existing eight steps remain unchanged: Model, Wersja, Silnik i skrzynia, Kolor, Koła, Tapicerka, Pakiety i opcje, Podsumowanie. Existing comparison, session selection, export and offline behavior remain in place.

## Evidence presentation

The new entry surface states the evidence boundary before the user enters detailed controls:

- **Wybór** — a complete selectable list confirmed by evidence;
- **Obserwacja** — the saved state of one exact configuration;
- **Poziom wersji** — evidence that is not automatically promoted to an engine/transmission-specific catalogue;
- **Brak źródła** — no synthetic selector is created.

This is especially relevant to the preceding Sandero/Sandero Stepway data package: all 15 current exact configuration identities and catalogue prices are verified, but only 2 exact Design surfaces have complete reproducible choices and 13 remain source-blocked.

## Files

- `tools/reporting/configuration_shortlist_equipment_groups.js`
- `tools/reporting/configuration_shortlist_equipment_groups.css`
- `data/reporting/configuration_shortlist_task_first_explorer_ui_20260808.json`
- `project/packages/configuration-shortlist-task-first-explorer-ui-001-20260808.md`
- `project/state.json`
- `project/STATE_SUMMARY.md`

## Boundaries

- no `data/master` mutation;
- no source-data mutation;
- no new compatibility inference;
- no ranking or recommendation layer;
- no selected observation promoted to a complete catalogue;
- no grade-level evidence promoted to exact powertrain/transmission choices;
- no cross-grade, cross-powertrain or cross-transmission projection;
- no change to immutable Data Products v1.19.1.

## Release boundary

This package changes `main` after the already-published immutable v1.19.1 release. It does not publish a new public release. Any later immutable release containing this interface requires a fresh explicit publication authorization.
