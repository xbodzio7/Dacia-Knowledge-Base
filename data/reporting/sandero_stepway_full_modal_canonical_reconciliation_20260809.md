# Sandero Stepway Full Modal Canonical Reconciliation

Date: 2026-08-09

## Result

- reconciled all 1708 captured rows across 15 exact configurator states;
- safely mapped 588 equipment rows as proven standard equipment;
- filled 26 previously missing scalar technical observations;
- preserved 154 safe technical literals as already-covered source evidence instead of duplicating master observations;
- preserved 441 equipment rows and 499 technical rows as unmatched/ambiguous evidence;
- materialized 588 dated standard-equipment observations and 26 dated technical observations;
- registered the full-modal snapshot and its 15 exact source-to-configuration relationships.

## Safety boundaries

The standard-equipment modal proves only `standard` status. Negative/base-state literals are not promoted to `not_available` or `optional`. Technical values are gap-fill only and do not duplicate already covered canonical slots. No inheritance is inferred between grades or powertrains. Composite/model-qualified dimensions and mixed petrol/LPG strings remain literal evidence.
