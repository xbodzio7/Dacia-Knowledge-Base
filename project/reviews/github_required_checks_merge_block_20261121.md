# GitHub required-check merge rejection — incident record

**Date:** 2026-11-21  
**Repository:** `xbodzio7/Dacia-Knowledge-Base`  
**Affected operation:** Attempted squash merge of PR #865 and PR #866  
**Status:** Diagnosed partially; root cause not yet established

## Observed facts

- The Project Owner supplied a screenshot of the `main` branch protection settings.
- The screenshot showed **Require a pull request before merging** enabled.
- **Require status checks to pass before merging** was enabled, with exactly six required checks, each selected under **GitHub Actions**:
  - `Python 3.14`
  - `Repository state / project-state --check`
  - `Python 3.10`
  - `Python 3.13`
  - `Package workflow / Windows`
  - `Generated documentation / documentation-baseline --check`
- **Require branches to be up to date before merging** was enabled.
- **Do not allow bypassing the above settings** was enabled.
- The screenshot showed that required approvals, Code Owner review and conversation resolution were not enabled.
- For PR #866 head `9021ab137c0c45782091a7a93cc0a7a0831abced`, the six named GitHub Actions check runs were observed as successful.
- The classic commit status endpoint returned an empty status list (`total: 0`) for that SHA.
- The merge endpoint rejected the attempt with HTTP 405 and message: `6 of 6 required status checks are expected.`
- The GitHub connector could not read the branch-protection endpoint (HTTP 403).
- At the time of inspection, `main` was `a10f02c6ab461182e4c2fa46ef51032efa0421c2`; PR #866's comparison reported it one commit behind `main`.

## What is and is not established

The evidence establishes that visible successful Actions check runs were not sufficient for GitHub to accept the merge. It does **not** establish why GitHub did not recognize the six required status checks. The empty classic status list and the branch-freshness difference are relevant diagnostic observations, not a proven causal explanation.

The Project Owner was advised not to disable all protection. No branch-protection setting was changed by the maintainer.

## Required follow-up

1. Preserve all six required checks and the protected-branch policy.
2. Re-fetch the exact PR head and current `main` SHA before further merge attempts.
3. Compare required context names, exact-head check runs, check-suite/source-App identity and classic status contexts.
4. If the cause is branch freshness, update the PR branch non-destructively and rerun the full required quality matrix on the new head.
5. If GitHub still rejects a fresh exact-head candidate, request administrator-level inspection of the required context/App binding and correct only the proven mismatch.
6. Do not repeat a deterministic merge attempt on an unchanged head or disable protection as a diagnostic experiment.

## Documentation

The permanent safeguards are recorded in:

- `project/AUTONOMOUS_MAINTAINER.md`
- `project/AI_WORKING_AGREEMENT.md`
- `project/WORKFLOW_PROFILES.md`
- `project/DECISIONS.md` (D-033)

This report records the incident evidence; it does not replace the operational rules in those documents.
