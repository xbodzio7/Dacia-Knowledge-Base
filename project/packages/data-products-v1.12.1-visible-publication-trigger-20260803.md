# Data Products v1.12.1 Visible Publication Trigger

Date: 2026-08-03

## Purpose

Run the repaired bounded Data Products v1.12.1 publisher through a single same-repository `pull_request` workflow whose status and logs are directly observable.

## Exact source

The activation contract is pinned to `1c87eed4410303b842ccb8ea1205d1790fc30d9a`, the merge commit of the publication test-contract repair.

## Safety

The workflow uses the same repository-wide publication concurrency group, refuses an existing tag or release, builds independently twice, requires byte identity, verifies the direct model-family workspace entry point and card, verifies public downloads, records the receipt and removes temporary publication automation. This activation pull request is not intended to merge.
