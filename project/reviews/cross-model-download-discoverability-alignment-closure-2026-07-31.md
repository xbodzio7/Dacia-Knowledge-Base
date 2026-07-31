# Cross-Model Download Discoverability Alignment Closure

Date: 2026-07-31

## Closure decision

The discoverability inconsistency identified after v1.9.0 is closed.

The verified cross-model HTML is now surfaced consistently in downloader metadata, terminal output and the consumer guide. Exposure remains conditional on manifest membership, so older releases without this product continue to work unchanged.

## Evidence

PR #417 passed all 17 workflows, the full 1,676-test baseline, Windows, Python 3.10, 3.13 and 3.14, and the public v1.0.0 download smoke.

## Preserved boundaries

No workspace-index card, release asset, source observation, reporting scope, comparison pair, ranking, recommendation or inferred value was changed.

## Follow-up

The next package is a priority-selection review. It must choose a new bounded direction rather than reopen this completed usability boundary.
