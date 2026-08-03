# Data Products v1.12.1 PR-Target Publication Bridge

Date: 2026-08-03

## Purpose

Install one bounded `pull_request_target` publisher for Data Products v1.12.1 after connector-created merge commits failed to emit a usable push workflow run.

The publisher is restricted to a same-repository activation branch named `agent/data-products-v1-12-1-pr-target-trigger-003`. It checks out the exact base SHA from `main`, performs the existing double-build and public-download publication contract, records the receipt, restores the canonical release workflow, and then removes its own temporary workflow.

This package changes no source data, generated report semantics, release version, or publication acceptance criteria. It only replaces the non-firing push activation mechanism with a bounded base-trusted event.
