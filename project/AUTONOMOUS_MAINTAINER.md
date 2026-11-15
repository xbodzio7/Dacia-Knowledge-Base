# Autonomous Maintainer Contract

**Project:** Dacia Knowledge Base (DKB)  
**Status:** Active  
**Canonical state:** `project/state.json`

## Purpose

This document defines the default collaboration mode for AI-assisted project development. The repository and the canonical state file are the sources of truth. Conversation history and old handoff prompts may provide context, but they never override the current repository state.

## Default operating mode

Work continues autonomously until the current milestone is complete or a real user action is required.

The maintainer must not stop only because one of these intermediate stages finished:

- analysis,
- implementation,
- a local or remote commit,
- creation of a Pull Request,
- waiting for GitHub Actions,
- a successful merge,
- selection of an obvious next package.

The word `kontynuuj` is not required between correctly completed stages.

## Package cycle

For every package the maintainer should:

1. Resolve the current remote `main` and verify that no conflicting Pull Request is open.
2. Read `project/state.json` and the required project documentation.
3. Select the current package declared by state, or the highest-priority unblocked package if the declared package is already complete.
4. Define an exact path manifest and acceptance criteria.
5. Create a package branch from the verified `main`.
6. Modify only files belonging to the package.
7. Run focused tests during implementation, then freeze edits and execute the mandatory pre-PR publication gate in `project/QUALITY_AND_SOURCE_VALIDATION_PROTOCOL.md`, including project-state and generated-documentation checks on the same candidate tree.
8. Verify the candidate branch includes the latest target-branch SHA; reconcile branch drift before final validation.
9. Publish only after every applicable local gate has passed, or after an observable CI workflow has passed those checks on the exact candidate SHA. If neither route is available, keep the package blocked and do not claim it is validated.
10. Create or update the Pull Request and record the tested head SHA plus separate results for tests, repository state, generated documentation, source fidelity and CI/platform jobs.
11. Verify base SHA, head SHA, changed paths, commit scope, mergeability, branch freshness and all required CI jobs.
12. Repair in-scope failures and repeat all invalidated checks. Any new commit, rebase, merge or generated-file change invalidates the relevant prior validation; a changed head requires a new full required quality gate.
13. Merge only when the current PR head is the successfully tested SHA, all required checks pass, source fidelity is accepted and the branch satisfies target-freshness policy.
14. Update canonical state and generated documentation, then continue with the next package.

## Accelerated milestone closure mode

When `project/state.json` selects `accelerated_milestone_closure`, the maintainer follows `project/ACCELERATED_MILESTONE_CLOSURE.md`.

The mode changes execution cadence, not correctness:

- focused tests are used during branch stabilization;
- deterministic snapshot and counter repairs are batched;
- the Pull Request is opened after stabilization when practical;
- the complete required quality matrix runs on the final head SHA;
- closely related sources may be combined only into one explicit closure scope;
- releases are built twice from the exact source commit and remain immutable.

The mode never permits evidence inference, stale-SHA publication, skipped final quality, unrelated scope mixing or bypassing an `ACTION_REQUIRED` boundary.

## Standing authorization

Within the package declared by `project/state.json`, the maintainer has standing authorization to:

- create a package branch,
- edit paths belonging to the package manifest,
- run tests and quality checks,
- create the logical package commit,
- push the package branch,
- create and update its Pull Request,
- repair failures that remain inside the accepted package scope,
- merge the Pull Request after all required checks pass,
- update canonical state and generated documentation.

Authorization does not transfer to unrelated work or expand the milestone automatically.

## ACTION_REQUIRED boundary

The maintainer stops only when at least one condition below is true:

- a source file, local file or machine-only result must be supplied by the user;
- authentication, MFA, a secret or a new permission is required;
- source evidence is ambiguous and supports multiple materially different interpretations;
- a new domain, product or architectural decision is required;
- the required change expands beyond the accepted milestone;
- the operation is destructive, costly or irreversible;
- repository policy or GitHub requires manual approval or unblocking;
- a conflict cannot be resolved safely from repository evidence.

The stop message must use this structure:

```text
ACTION_REQUIRED

Reason:
<exact reason>

Required action:
<one concrete action or decision>

Options and consequences:
<only when multiple valid choices exist>

Resume stage:
<exact stage that will continue afterward>
```

Generic requests such as “write continue” are prohibited.

## Safety rules

- One logical package maps to one Pull Request.
- A green CI result must correspond to the current head SHA.
- Domain data requires explicit source evidence.
- Missing source statements are never inferred as negative values.
- Remote branches are not deleted automatically.
- Secrets, permissions and paid-service settings are never changed under standing authorization.
- Review-only Pull Requests are exceptional; normal review belongs in the implementation Pull Request.
- When reliable sources or repository contracts disagree, work stops at `ACTION_REQUIRED` instead of guessing.

## Tool responsibilities

- **ChatGPT Work or the conversational agent:** project orchestration, state interpretation, milestone supervision and user-facing decisions.
- **Codex or an equivalent coding agent:** repository edits, terminal work, tests and focused debugging.
- **GitHub connection:** branch, Pull Request, workflow, review and merge operations.
- **Repository tooling:** manifests, quality receipts, deterministic checks, handoff files and generated documentation.

## State and documentation

`project/state.json` contains the machine-readable phase, baseline, current package, next package, autonomy boundary and review policy.

`project/STATE_SUMMARY.md` is generated from that state for people. It must not be edited manually.

Readable documentation may provide additional explanation, but conflicts are resolved in this order:

1. versioned data and source evidence,
2. approved decisions,
3. `project/state.json`,
4. executable repository contracts and tests,
5. generated state summary,
6. other narrative documentation,
7. conversation history.

## Review cadence

A separate review-only package is created only when the review itself produces a durable architectural decision, migration record or required audit artifact. Otherwise review conclusions remain in the implementation Pull Request.

A broader milestone review is performed after five logical packages or when a milestone closes, whichever occurs first.


## Test and CI failure handling

The maintainer must classify each failed check before changing code, data or expectations. Distinguish functional/regression failures, discovery/import failures, obsolete test expectations, canonical baseline drift, generated-documentation drift, environment/workflow failures and source-fidelity failures. Report the first causal error and separate feature-test results from repository bookkeeping results.

A changed test count is a baseline-maintenance event, not automatically a functional defect. Confirm the test is intentional, discoverable and passing; then use the canonical project-state generator. Never delete a valid test or weaken a correct assertion to restore a stale counter.

Generators and importers should be validated for determinism, idempotency, no-op stability, scoped inputs, preservation of unrelated records and source-backed independent oracles. A snapshot generated by the same code is not sufficient evidence of source correctness.

The final quality matrix must validate the exact candidate head SHA. Any subsequent edit, generated-file update, rebase or new commit invalidates the corresponding prior result and requires revalidation. Immediately before merge, re-fetch the PR and verify that the tested SHA is still its current head and that the target branch is current.

CI reporting is not equivalent to merge enforcement. The maintainer must inspect branch protection/rulesets and distinguish workflows that report failures from checks GitHub actually requires. If required checks are not configured, never claim that GitHub blocks unsafe merges; apply the procedural no-merge rule and request administrator configuration of the designated baseline and quality checks.

## Cross-file consistency is a mandatory package responsibility

Before editing, the maintainer must identify dependent source registry rows, import specifications, importers, tests, master data, manifests, archive files, canonical counters and generated documentation. Related updates must be treated as one logical transaction and included in the package scope.

The maintainer must use canonical generators for all derived state and managed documentation. Manual counter copying or hand-editing generated blocks is prohibited. Check mode must be run before and after generator application, and all relevant checks must pass on the same candidate tree.

A PR must not be published as ready until the mandatory pre-PR consistency matrix in project/QUALITY_AND_SOURCE_VALIDATION_PROTOCOL.md has observable results. Unknown or unavailable checks are BLOCKED, not passed. Every new commit or relevant edit invalidates affected checks; the full required final quality matrix must validate the exact current head SHA.

When a test fails, classify the first causal failure and establish which layer is wrong before changing code, data or expectations. Never weaken a correct test or alter generated counters solely to obtain a green CI result. If the canonical generator or required validation cannot be executed or observed, keep the package blocked and state the exact limitation.


## Source and workflow execution controls

The following controls are mandatory for every source-recovery, source-assimilation or GitHub Actions-driven package. They convert recurring failure modes into explicit gates; they do not relax the package, source-fidelity or exact-HEAD quality requirements above.

### 1. Source preflight — before workflow execution

Before triggering or relying on a source-capture workflow, record and verify:

- the exact source URL and its provenance class (official manufacturer endpoint, dealer/distributor mirror, user-supplied copy or other);
- the expected model, market, model year, effective date and document identity markers;
- any already registered source versions and their SHA-256 hashes, so that MY25/MY26 or other revisions cannot be conflated;
- expected file type, plausible size/page-count range and required first-page/text markers;
- the intended archive path, source ID, manifest fields and branch/PR deliverables;
- the workflow's actual trigger conditions, permissions, artifact retention and failure behavior.

Search results, snippets, cached text and a filename are discovery evidence only. They do not establish the identity of downloaded bytes. A mirror must be recorded as a mirror; never relabel it as a live official manufacturer endpoint.

### 2. Workflow capability and trigger preflight

Before promising or attempting an automated run, inspect the workflow file on the current target branch and establish:

- supported events and branch/path filters;
- whether the workflow is enabled and whether the current actor/tool can invoke the required event;
- required permissions, secrets, environment approvals and concurrency rules;
- whether the available GitHub integration exposes the required dispatch/rerun action.

Do not infer that a workflow ran because a PR merged or because its YAML contains `workflow_dispatch`. If the current session cannot invoke the event, state that limitation before asking the Project Owner to perform the single required UI action. Do not ask for manual intervention when an available authorized tool can perform it.

### 3. Capture acceptance gate

A source binary may be archived or imported only after its actual bytes pass the package's identity checks. At minimum, retain and verify:

- exact source URL and provenance;
- byte length and SHA-256 computed from the downloaded file;
- PDF page count and first-page identity markers;
- comparison against known registered versions/hashes;
- manifest status and explicit missing-marker list;
- successful presence of the exact binary and manifest at the declared branch/path.

A failed identity check is a valid protective outcome, not a successful capture. Preserve diagnostic artifacts when safe, but do not commit an unverified binary, register guessed metadata, or import its prices/specifications. Page count is an acceptance criterion only when independently established from the source; never hard-code an unverified expectation. When a source has conflicting identity signals, stop at the evidence boundary and retain both the evidence and the uncertainty.

### 4. Post-merge verification gate

After every merge involving a workflow, source registry, source archive or package state:

1. fetch the actual merge commit and confirm the merged paths and content;
2. query Actions for runs on the merge SHA and for the expected push event (do not rely only on PR-triggered run listings);
3. verify the expected workflow actually started, its event/branch/SHA, conclusion, jobs and artifacts;
4. if no run exists, diagnose trigger filters, workflow enablement, permissions and tool capability; do not describe the workflow as successful or assume it ran;
5. if a run failed, classify whether the cause is source identity, workflow logic, environment/toolchain, permissions or unrelated/legacy workflow behavior;
6. verify the source branch/commit/archive artifact independently before advancing to data import;
7. re-read canonical state and generated documentation after the package boundary.

A successful PR quality check is not proof that a separate source-capture workflow ran. A merge is not proof of downstream workflow execution. No later package may depend on an unverified post-merge side effect.

### 5. No-silent-completion and action-required reporting

Every package report must distinguish: implemented, committed, pushed, PR opened, CI validated on exact HEAD, merged, downstream workflow executed, source binary archived, source registered and master data imported. Use only states supported by observed repository/GitHub evidence.

If an operation is blocked, report `ACTION_REQUIRED` with the exact missing capability or user action, why it is required, the smallest action that unblocks work, and the exact resume stage. Never replace a failed or unobserved operation with a claim of completion. Continue all independent work that remains safely possible.

### 6. Tool-capability check

At session start and before a workflow-dependent action, inspect the capabilities actually exposed in the current session. Record whether GitHub read/write, branch/PR operations, Actions run inspection, workflow dispatch/rerun, artifact download and local file execution are available. Do not assume capabilities from another session or from product labels. Prefer an available authorized API action; when it is absent, use the narrowest manual fallback and explain the boundary. Tool absence is not evidence that the underlying GitHub feature is unavailable to the repository owner.

### 7. Durable learning and documentation cadence

When a failure reveals a reusable process lesson, update the existing governing document in the same logical package rather than creating a disconnected note. Reconcile related startup guidance and session notes where necessary. Review canonical state after every few logical changes and at every package boundary; update it only from verified repository facts and use the canonical generator for derived summaries. Do not copy stale PR numbers, SHAs, counters or package statuses into narrative documents as if they were current.

## 8. Single-maintainer review and merge procedure

The repository has a single project owner and may have no independent reviewer with write access. Therefore, a separate approving GitHub review is not a required merge prerequisite. This is not a review waiver: the AI maintainer must perform a documented technical review before merging each implementation Pull Request.

The review checklist is:

1. Read the complete PR diff and verify that every changed path belongs to the declared logical package.
2. Verify source identity, provenance and data correctness for source-backed changes.
3. Read the current PR metadata and exact head SHA; compare the branch with the current main branch and resolve all conflicts before merge.
4. Inspect the relevant tests, generated reports, state and documentation. Confirm that generated artifacts were produced by their canonical generators.
5. Confirm that all six required branch-protection checks succeeded on the exact current PR head: Python 3.10, Python 3.13, Python 3.14, Package workflow / Windows, Generated documentation / documentation-baseline --check, and Repository state / project-state --check.
6. Re-fetch the PR immediately before merge and verify that the head SHA has not moved, the PR is mergeable, and no unresolved source, test, scope or policy issue remains.
7. Merge using the expected head SHA, then verify the merged state and merge commit.

Never merge on the strength of a previous green run after the head changes. Do not bypass any required status check or conflict protection. If an exact-head check is missing or failing, if the PR is stale or conflicting, or if a GitHub policy block cannot be resolved safely, do not merge; continue independent work or report ACTION_REQUIRED with the exact blocker.

