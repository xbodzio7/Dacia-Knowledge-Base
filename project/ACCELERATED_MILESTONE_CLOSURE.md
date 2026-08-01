# Accelerated Milestone Closure Mode

**Project:** Dacia Knowledge Base (DKB)  
**Status:** Active  
**Effective date:** 2026-08-01

## Purpose

This mode shortens the path from an already bounded backlog to a verified milestone or release without weakening evidence rules, final validation, or repository traceability.

It is used when the remaining work is known, logically related and small enough that repeated full-matrix runs and repeated Pull Request setup would add more overhead than safety.

## Activation

The mode is active when `project/state.json` contains:

```json
"execution_policy": {
  "mode": "accelerated_milestone_closure"
}
```

The canonical state may activate or deactivate the mode. Conversation history alone never activates it.

## Operating rules

1. Resolve the exact current package and remaining bounded backlog from repository state and generated analysis.
2. Combine multiple source reviews only when they form one logical closure package and preserve exact source, configuration, date, fuel, transmission and model-year boundaries.
3. Stabilize the branch before opening the Pull Request whenever repository tooling permits safe branch-only work.
4. During implementation run focused tests for the changed paths and contracts.
5. Batch mechanical repairs such as generated snapshots, counters and deterministic manifests before the final quality run.
6. Run the complete required quality matrix once against the final Pull Request head SHA.
7. Merge only when the current head is green, mergeable and review-clean.
8. For a release, build twice from the exact release source commit, prove byte identity, verify the offline workspace and publish immutable assets.
9. Record the publication result and restore the next bounded package in canonical state.
10. Do not create temporary automation whose implementation and maintenance cost exceeds the remaining backlog.

## Non-negotiable boundaries

Acceleration never permits:

- skipping the final complete quality gate;
- publishing from an unverified or stale SHA;
- combining unrelated domains into one Pull Request;
- inferring missing source facts;
- transferring values between configurations, fuels, transmissions, grades, model years or sources;
- replacing missing evidence with `not_available`, zero or a guessed value;
- rewriting an existing public release;
- bypassing an `ACTION_REQUIRED` boundary.

## Pull Request rule

One logical package still maps to one Pull Request.

A closure package may contain several closely related sources or the release preparation and publication automation when they serve one explicit milestone and share one acceptance contract. Unrelated work remains separate.

## Validation cadence

During development:

- run focused unit and contract tests;
- regenerate only affected deterministic outputs;
- avoid repeated full-matrix runs after each mechanical correction.

At the final head:

- run all required Linux, Windows and supported-Python checks;
- run the complete repository quality gate;
- verify canonical project state;
- verify release assets when a release is in scope.

## Release cadence

An accelerated release may use one Pull Request plus a post-merge publication workflow when all of the following are true:

- the workflow targets the exact merge SHA;
- assets are built twice and compared byte for byte;
- the tag and release are absent before publication;
- public assets are verified after upload;
- the workflow records the publication and removes itself;
- a later commit cannot silently change the already published assets.

## End of document
