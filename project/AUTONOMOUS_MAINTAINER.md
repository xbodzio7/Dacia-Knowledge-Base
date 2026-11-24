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

## Git Bash operational safety

Whenever local Git Bash is used, the maintainer must follow
`project/GIT_BASH_SAFE_OPERATIONS.md`. This includes preflight checks for
repository identity, branch and working-tree state; preserving rather than
discarding local changes; stopping on failed checkout/pull operations;
one-command-at-a-time execution; canonical state regeneration; explicit diff
review and path-scoped staging; and exact-branch push verification. Destructive
reset/clean operations and blind stash restoration are prohibited as routine
recovery. If the local state is ambiguous, stop and request read-only
diagnostics before proceeding.


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



## 9. Fail-closed package consistency gate

Before a Pull Request may be considered ready for merge, the maintainer must verify that the required `Repository state / project-state --check` job completed all three checks on the same candidate commit:

1. `package-preflight` for repository CSV/JSON and source-capture manifest integrity;
2. `project-state --check` for canonical counters, state references and generated state summary;
3. `documentation-baseline --check` for managed documentation blocks.

The CI job is read-only and blocks on the first failure. Do not repair its output manually in GitHub or claim that the umbrella job proves an individual layer unless its log shows that layer passed. Repair through canonical tooling, inspect all generated changes, and rerun the complete gate after the final edit.

These checks complement, and do not replace, the Python/Windows quality matrix, importer-specific tests, independent source-fidelity review, complete diff review and exact-head merge procedure. The six required status-check names remain unchanged.

## 10. Remote repository continuity and post-merge closure (mandatory)

The remote GitHub default branch is the authority for project state. A local checkout is only a candidate workspace until its branch and exact HEAD SHA are verified against remote main.

At the start of every continuation:
- fetch the current remote default-branch SHA and inspect canonical project/state.json from that revision;
- inspect open/recent PRs and recent merges that may have changed the active package, source inventory, tests or generated documentation;
- record the remote SHA used for decisions; do not promote a local project-state --apply result to canonical status;
- if local tools are used, prove local HEAD, upstream and clean/dirty status before running generators; label results with that exact tree SHA;
- distinguish GitHub Actions automatic PR/push checks from manual workflow dispatch. Missing dispatch capability in the current connector is not a CI outage when normal PR workflows trigger and report checks.

After every merged package, perform a mandatory post-merge closure:
1. Verify PR merged status, final tested head SHA, merge commit SHA and changed paths.
2. Verify the merge commit is present on remote default branch.
3. Update canonical project/state.json so the completed package and next package accurately reflect the merged repository. Use the canonical state workflow; do not rely on the PR description or chat memory as the only queue update.
4. Run project-state --apply only on the verified current candidate tree, then inspect its complete diff and rerun project-state --check plus documentation-baseline --check.
5. Never hand-edit STATE_SUMMARY.md, copy counters from an old local run, or claim generator completion when the generator was not run.
6. Include the state and generated-documentation reconciliation in a reviewed PR. Confirm that its checks ran on the exact final head before merge.
7. Re-read remote state after that merge before selecting the next package.

If the state transaction cannot be completed because execution/generator access is unavailable, explicitly mark the state repair as blocked, preserve the exact remote SHA and pending package transition, and do not silently continue from an obsolete package queue.

A package may be reported as complete only when its result is durably merged and the post-merge state transaction is either verified complete or explicitly recorded as a separate blocking follow-up. A green PR alone does not update canonical project state.




## 10. Branch protection and merge-block diagnosis (mandatory)

Branch protection is a safety boundary, not an obstacle to work around. Never disable the protection of `main`, bypass required checks, force-push, or push directly to the protected branch to make a Pull Request mergeable.

Before any merge attempt, record the exact current target-branch SHA, PR base SHA, PR head SHA, mergeability/conflict state, and the six required check results on that exact head. Re-fetch these values immediately before merging. A check result from another SHA is not evidence for the current candidate.

Interpret GitHub's evidence precisely:

- A workflow run and a commit check run are related but not interchangeable with the required status context GitHub enforces.
- For each required check, verify exact context/name, conclusion, head SHA, check suite and source GitHub App where exposed.
- Inspect both Checks API data and classic commit status data when diagnosing a required-check rejection. An empty classic status list does not prove that GitHub Actions check runs are absent; conversely, successful check runs do not prove that branch protection recognizes the required context.
- Read the actual branch-protection/ruleset configuration when permissions allow. If the API returns 403 or omits the configuration, record it as inaccessible; do not claim that the rule has been independently verified through the API. Owner-provided screenshots are evidence of the displayed settings at the time supplied.
- Preserve the exact GitHub merge error and HTTP status. Do not infer the cause from a single correlated fact (for example, a branch being one commit behind).

When GitHub rejects a merge despite apparently successful checks:

1. Stop repeated merge attempts against the same unchanged head.
2. Capture the exact PR head SHA, target SHA, all required check contexts and conclusions, check-suite/app identity, classic status contexts, branch freshness and full rejection message.
3. Classify the blocker as stale branch, missing/failed required check, context/app mismatch, merge conflict, policy/permission restriction, or unresolved/unknown. Multiple causes may coexist.
4. Do not change branch protection merely to test a hypothesis. First establish the causal mechanism from GitHub evidence or an owner-confirmed controlled change.
5. If the cause is stale branch, update the PR branch using the repository's supported non-destructive method, then rerun the full required quality matrix on the resulting exact head.
6. If the cause is a required-context or GitHub App mismatch, request the minimum administrator investigation/correction. Preserve all six required checks and their quality meaning; do not weaken the rule by removing checks or switching to unverified contexts.
7. If the cause cannot be established, leave the PR unmerged and report the precise unknown plus the smallest action needed.

A passing CI workflow is necessary but not sufficient for merge. The final merge gate still requires technical review, exact-head success for all six required checks, target freshness as configured, no conflicts, and a successful merge response. Never retry merge after any head or target change without repeating the relevant checks.

### Temporary protection changes

Any proposed temporary change to branch protection requires a demonstrated root cause, explicit Project Owner approval, a written scope, a rollback condition and a verification plan. Prefer the narrowest reversible adjustment. Never recommend disabling all protection as a routine workaround. If a setting is changed, record the before/after state and restore the original protection immediately after the bounded operation; verify restoration. No standing authorization permits changing repository security settings.


## Trusted baseline-repair write-back

The canonical Baseline Repair workflow is started from `main` with the target PR number, exact branch name and exact 40-character head SHA. It also captures and rechecks the exact `main` base SHA, refusing to write back if the PR or `main` advances during generation. It uses two isolated jobs:

1. The generation job checks the PR identity and immutable head, checks out that SHA without write credentials, runs both canonical generators, validates their outputs and uploads only the six-file allowlist.
2. The write-back job runs only after generation succeeds. It re-verifies that the same same-repository PR is still open against `main` and still points to the exact original head. It downloads the artifact, rejects symbolic links and any missing, extra or unexpected file, and stages only `CHANGELOG.md`, `README.md`, `project/ROADMAP.md`, `project/SESSION_STATE.md`, `project/state.json` and `project/STATE_SUMMARY.md`.

Only the write-back job receives `contents: write` and `actions: write`. It does not execute scripts or build steps from the PR branch. The repair is committed and pushed as a normal fast-forward update; force-push is prohibited. A branch race or changed PR identity fails closed. After verifying the new PR head, the workflow explicitly dispatches `quality.yml` and `repository-baselines.yml` on that branch because pushes made with the workflow's `GITHUB_TOKEN` do not automatically start the normal push/pull-request workflows.

The Project Owner no longer needs to download, extract or upload the repair ZIP. The required six CI checks must still pass on the new exact head before the PR can be merged.
