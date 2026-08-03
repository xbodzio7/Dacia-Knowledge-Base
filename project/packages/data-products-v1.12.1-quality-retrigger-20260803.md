# Data Products v1.12.1 Quality Retrigger

Date: 2026-08-03

## Purpose

Trigger a fresh `Quality` run after the one-time `workflow_run` publication bridge is already registered on `main`.

The successful `Quality` head SHA of this merge is the exact source and target for the immutable `data-products-v1.12.1` release.

This retrigger changes no source data, report semantics, comparison scope, ranking, recommendation or inferred value.
