# Data Products v1.12.1 Registered Push Bridge

Date: 2026-08-03

## Purpose

Install a one-time publisher in the already registered Versioned Data Product Release workflow.

The publisher runs only on the merge push whose commit message contains `release: publish Data Products v1.12.1 via registered push bridge`. It builds the exact merge SHA twice, verifies byte identity and the complete offline workspace, publishes immutable assets, verifies public downloads, records the receipt, restores the canonical manual release contract and removes all temporary publication files.

No source data or report semantics change.
