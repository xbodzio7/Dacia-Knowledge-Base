# Spring Exact Current Semantic Migration Review

Package ID: `spring_exact_current_semantic_migration_review_001`

Status: complete

## Goal

Compare exact current Spring snapshots with the existing commercial model and separate safe in-place updates from changes that would alter item semantics or infer unavailable grade context.

## Delivered

- reviewed all 25 existing Spring commercial mappings across Essential, Expression and Extreme;
- approved one safe in-place update: Essential Lichen Khaki, optional, 2300 PLN;
- confirmed that Extreme CITY 1800 PLN and POWER 3000 PLN are already current and require no change;
- classified the Essential and Extreme Type 2 mappings as semantic migrations because current evidence says standard equipment while the repository models a commercial option;
- classified Essential Biel Alpejska as a semantic migration because it is current standard paint at zero surcharge but is modeled as an optional item with unknown price;
- retained 19 mappings without change because current Expression or complete paint-palette evidence is missing;
- identified the 1500 PLN home charging cable for Essential and Extreme as requiring a new representation rather than reuse of `charging_connector_type`;
- generated deterministic JSON and Markdown review reports.

## Master-data boundary

This package is review-only. It changes no master row, price, availability state, item, attribute, model or domain.

## Follow-up

Proceed with `spring_essential_khaki_price_apply_001` and update only the existing Essential Lichen Khaki optional mapping to 2300 PLN. All semantic and unresolved cases remain untouched.
