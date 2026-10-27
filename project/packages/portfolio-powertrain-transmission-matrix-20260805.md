# Portfolio Powertrain and Transmission Matrix

## Package

- Package ID: `portfolio_powertrain_transmission_matrix_001`
- Kind: `deterministic_portfolio_reporting`
- Date: 2026-08-05
- Status: complete

## Purpose

Provide deterministic JSON, CSV and standalone HTML views that group every active configuration by the exact `powertrain_label` and `transmission_type` already recorded in canonical master data.

## Output contract

The product reports:

- exact powertrain label;
- exact transmission type;
- configuration, model and version counts;
- sorted model, version and configuration codes;
- detailed configuration membership in JSON;
- a flat deterministic CSV view;
- a standalone Polish-language HTML table.

## Boundaries

- no normalized or newly invented powertrain identifier;
- no parsing of power, fuel, drive layout or gear count from labels;
- no ranking or recommendation;
- no inferred missing values;
- no mutation of master data;
- each active configuration appears exactly once.

## Verification

The package tests exact coverage, unique group identity, stable ordering, no-inference flags and deterministic JSON/CSV/HTML rendering. Full repository CI and canonical `project-state --check` are required before merge.
