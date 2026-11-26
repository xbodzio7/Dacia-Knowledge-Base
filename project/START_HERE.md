# START HERE

**Project:** Dacia Knowledge Base (DKB)

**Purpose**

This document defines the mandatory startup procedure for every AI session.

---

# Required Reading Order

Read the following documents and state resources in exactly this order:

1. `state.json`
2. `STATE_SUMMARY.md`
3. `AUTONOMOUS_MAINTAINER.md`
4. `ACCELERATED_MILESTONE_CLOSURE.md`
5. `WORKFLOW_PROFILES.md`
6. `AI_WORKING_AGREEMENT.md`
7. `AI_CONTEXT.md`
8. `SOURCE_ASSIMILATION_STANDARD.md`
9. `SOURCE_FIRST_EXTRACTION_WORKFLOW.md`
10. `QUALITY_AND_SOURCE_VALIDATION_PROTOCOL.md`
11. `DOCUMENTATION_STANDARD.md`
12. `DOCUMENT_TYPES.md`
13. `GLOSSARY.md`
14. `DECISIONS.md`
15. `SESSION_STATE.md`
16. `ROADMAP.md`
17. `REPOSITORY_GOVERNANCE.md`

`README.md` may be consulted if additional project context is required.

When narrative documents disagree about the current phase or package, the canonical `state.json` wins. Versioned source data and approved decisions remain higher-priority evidence for domain facts.

---

# Workflow Bootstrap

**Do not start project work from conversation memory alone.** A new chat, new session, application/browser switch, tool-limit change, recovery event, or handoff must not cause the AI to reconstruct the workflow from memory.

Before any project action, the AI shall also perform a **continuity freshness check**:

- treat `project/state.json` as the only current package selector;
- verify that `project/STATE_SUMMARY.md` and any session-state counters agree with `state.json`;
- run `python tools/dkb.py project-state --check` before selecting or publishing work; in GitHub Actions this also validates canonical repository/default-branch metadata against the workflow repository and Pull Request target;
- for every Pull Request, require the Quality workflow's `project_state_transition.py --self-test` and transition gate to validate package lifecycle, exact PR-bound completion evidence, completed-report promotion, next-package rationale and existence of declared source files;
- if generated state documentation is stale, repair/regenerate it before selecting or describing the next package;
- verify that every recently merged package affecting the current milestone is reflected in the canonical state and its reconciliation/manifest before requesting or repeating any user action;
- never treat a conversation handoff, remembered package number, tab list or previous assistant statement as evidence that a package is still open;
- when duplicate work is suspected, reconcile by exact configuration/source identifiers and merged commit/PR evidence before doing new extraction;
- before selecting any new source-backed next package, inspect the report registry, source registry and merged PR history for completed work on the same source/model/domain; do not rely only on the previous `next_package` pointer;
- include `next_package.selection_evidence` with registered `reviewed_report_ids`, existing `reviewed_evidence_paths`, precise `residual_scope` and `scope_resolutions` for every reviewed report sharing a model family; the transition gate rejects unexplained semantic overlap and reuse of an already registered candidate report ID;
- validate every completed current-package receipt against the report registry, exact report ID/path and completed report status on every state transition; a mismatch blocks further package selection.

If this check finds a state/documentation mismatch, enter recovery/diagnostic handling first; do not continue from the stale narrative.

### Durable Result and Recovery Checkpoint

Before continuing work, reconcile the previous session's deliverables against the repository:

- enumerate completed analyses, generated reports, extracted data, code changes, and artifacts created during the prior work period;
- verify each deliverable's exact persisted location and GitHub commit/PR status; a conversation statement or tool output is not proof of publication;
- recover valuable uncommitted/off-repository artifacts from available conversation uploads, ZIPs, Library files, or generated outputs, then compare against current `main` before adding them;
- record recovered deliverables in `reports/recovered/` with provenance, snapshot date, and scope limitations; never import report-derived values into `data/master` without a separate source-evidence workflow;
- update the canonical state and session documentation with what was recovered, published, left local, or blocked;
- do not mark a task done until its result is durably saved and its location is recorded.

When file/repository access is unavailable, explicitly mark the result `not recovered` or `action required`; do not assume it was published or lost.

Before any project action, the AI shall:

- load `project/state.json` and identify the current package, next package, autonomy policy and execution policy;
- verify the actual repository/remote state when repository execution is available;
- identify the execution capabilities actually available in the current session, including GitHub read/write access, local repository access and Codex/Work availability;
- select the strongest appropriate profile defined in `WORKFLOW_PROFILES.md`;
- complete the Workflow Check defined there;
- only then begin project work.

The previous conversation is context only. It cannot select, override or reactivate a workflow profile. If the bootstrap cannot be completed, enter `RECOVERY` or diagnostic mode and report the exact blocker.

For remote-only regeneration of canonical counters and managed documentation, follow `project/BASELINE_REPAIR_WORKFLOW.md`. The `Baseline Repair` workflow must be dispatched from the trusted `main` branch, never from the PR branch, and only after its definition has landed on `main`. Supply only the PR number: the read-only generation job discovers and verifies the exact branch/head/base from GitHub, while a separate write-back job re-verifies them and applies only the six allowlisted generated files. PR code must never run with write credentials. After write-back, inspect the PR diff and require all six normal CI checks on the new exact head SHA.

## Automated repository governance

Read project/REPOSITORY_GOVERNANCE.md before changing CI, branch protection, merge settings or package lifecycle rules. Quality and Repository Baselines use only ordinary pull_request events with read-only permissions and credentials persistence disabled; they must never execute PR code through pull_request_target or workflow_run. A separate main-only governance audit reads trusted workflow files and repository metadata without checking out or executing PR code. Package-closeout receipts are checked by the local canonical transition validator. The owner-confirmed branch-protection screenshot remains authoritative for settings the standard Actions token cannot read. Baseline write-back remains a separate workflow_dispatch operation from main.

## Recorded GitHub `main` branch-protection baseline

The Project Owner confirmed on 2026-11-20 that the `main` branch protection rule requires all six status checks:

1. `Package workflow / Windows`
2. `Repository state / project-state --check`
3. `Generated documentation / documentation-baseline --check`
4. `Python 3.10`
5. `Python 3.13`
6. `Python 3.14`

The setting **Require branches to be up to date before merging** is disabled. This is the owner-confirmed protection setting from the 2026-11-26 screenshot. The required Quality workflow independently rejects a PR branch that is behind the current target branch, so exact branch freshness remains a CI requirement even though GitHub branch protection does not require it. This is a durable, owner-confirmed repository fact. Do not ask the Project Owner to reconfirm it in future sessions merely because the current GitHub connector cannot inspect the setting (including a 403 response). Verify the six checks and branch freshness on each exact PR head as usual. Reconfirm with the Project Owner only if concrete evidence indicates that the protection rule has changed; otherwise, any available API re-check should be silent.

---

# Mandatory Rules

Before implementation the AI shall:

- read the canonical state and required documents;
- analyse the current repository and remote `main`;
- identify the current package declared by state;
- verify that no architectural or evidence blocker exists;
- define an exact package scope and acceptance criteria.

Implementation shall not begin before the required analysis has been completed.

The AI shall read and follow `QUALITY_AND_SOURCE_VALIDATION_PROTOCOL.md` in every new chat/session and at every continuation after a handoff. This includes the mandatory cross-file change transaction, dependency-impact inventory, canonical-generator-only baseline updates, pre-PR consistency matrix, scope-safe tests for shared sources, failure classification and exact-HEAD revalidation. For model, version, configuration or source-registry changes, also apply sections 24.3–24.6: portfolio-wide tests must derive live inventory from canonical registries, historical tests must use immutable package fixtures, dependent reports must be reviewed by declared input scope, and package/release lifecycle tests must use isolated temporary repositories with no real remote push. Tests must distinguish source identity from package ownership and must never use broad filename-prefix selection or whole-source absence/count assertions where later packages may legitimately extend the same source. Every such extension must be validated alongside the earlier source-family regression tests. These controls apply automatically even when the user only says `kontynuuj`; they must not depend on conversation memory or a repeated user instruction. This is a mandatory startup rule, not an optional checklist and not dependent on the user repeating it. It governs the full package lifecycle, test design, CI failure diagnosis, independent source-fidelity review and PR/merge gates. If this file cannot be read, do not begin implementation; enter recovery/diagnostic mode and report the blocker.

When reviewing or repairing tests of reports, findings, notes or generated documentation, follow section 24.2 of the quality protocol: assert stable semantic contracts and required behavior rather than incidental editorial wording. Exact text matching is reserved for text that is itself a declared interface or contract. A wording-only correction must preserve positive and negative checks for the underlying invariant.

Before using a PDF, brochure, price list, saved configuration, instruction or equivalent documentary source, the AI shall resolve its coverage state under `SOURCE_ASSIMILATION_STANDARD.md` and follow `SOURCE_FIRST_EXTRACTION_WORKFLOW.md`. A registered source, normalized slice or earlier bounded migration must not be presented as a complete document analysis unless every page, table, footnote, symbol and relevant rendered visual has been reviewed and classified.

For vehicle data-completion work, the documentary source must be assimilated and compared with master data before the interactive configurator is used for gap filling. The configurator is not the default first extraction source.

After implementation begins, work continues autonomously through tests, Pull Request, CI repair and merge until the package or milestone is complete. A generic `continue` or `kontynuuj` command is not required between correctly completed stages.

The AI stops only at a boundary defined in `AUTONOMOUS_MAINTAINER.md` and must then use the `ACTION_REQUIRED` format.

---

## User-supplied source persistence (mandatory)

Before asking the Project Owner to upload or resend any source file, search in this order:

1. current conversation attachments and previously uploaded conversation files;
2. the user's persistent Library, including prior uploads and alternate filenames;
3. Project files/knowledge when the source belongs to this project;
4. the repository across the default branch, relevant branches, commits and pull requests;
5. the exact official source URL already recorded in the source register, if applicable.

Do not ask for a file again until these locations have been checked. Verify the actual bytes, size and SHA-256 where possible, and compare with repository copies before creating another copy.

Every user-supplied documentary source intended for DKB must be made durable: retain the original in the persistent Library if no identical copy exists; archive the original binary in the canonical repository source location when permitted; register source identity, provenance, canonical path, byte length and verified SHA-256; and explicitly record any blocked persistence step. Never claim a file was archived or retained unless its exact destination is verified.

The repository is the canonical project archive; the Library is a persistent secondary retrieval location. Reuse identical files and record their existing locations instead of creating duplicates. Compare bytes (SHA-256 and size), not filenames alone.

If a source cannot be found or read, report exactly which locations were checked and the remaining blocker. Request a new upload only as the final recovery action, not because session context or an earlier attachment reference was not carried forward.

# Git Bash Safety

When Git Bash is used for repository operations, follow `project/GIT_BASH_SAFE_OPERATIONS.md` before switching branches, synchronizing, stashing, committing or pushing. Its safeguards supplement the quality protocol and do not authorize destructive recovery commands.

# Repository First

The repository is the primary source of truth.

Conversation history and old handoff prompts must never replace repository analysis or canonical state validation.

Run this check at session start whenever repository execution is available:

```bash
python tools/dkb.py project-state --check
```

Run the fast data-integrity preflight before committing or publishing a package, and after any data CSV/JSON edit:

```bash
python tools/dkb.py package-preflight
```

The preflight is also mandatory in the Quality GitHub Actions workflow. It does not replace the full repository validator or the complete quality/source-fidelity gates.

For a package whose canonical `kind` is `residual_review`, prepare the exact review input with:

```bash
python tools/residual_review_bundle.py --output-directory ../residual-review-bundle
```

The command resolves the package from `project/state.json`, verifies the canonical prioritization block and source receipt, checks the archived PDF SHA-256, and produces the candidate block, page text, and authoritative page PNG. When local binary-file access is unavailable, run the `Residual Review Bundle` GitHub Actions workflow and use its artifact instead of requesting a repository ZIP.

The package ID, exact manifest paths and source boundary are read from `project/state.json`; they must not be copied from a handoff prompt.

---

# Expected Output

For each completed milestone report:

- merged Pull Requests;
- exact merge commits;
- quality results;
- baseline changes;
- current and next package;
- unresolved risks or `ACTION_REQUIRED` items.

When working directly inside the repository, do not reproduce complete files in chat unless needed for a decision or recovery.

---

# End of document


## Analytical report freshness (mandatory)

Before relying on a report under `data/reporting/` or `project/packages/`, check its provenance and freshness under `project/REPORT_FRESHNESS_STANDARD.md`. A report without exact input identities is historical/legacy, not proof of current state. Recheck old findings against current master data and source evidence; never ask the Project Owner to repeat an upload or action based only on an old report. When source/master data changes, identify dependent reports and refresh or explicitly retain them as historical. The automated freshness gate is part of the required Quality workflow; run it locally before publication as described below.


The report freshness contract is now enforced by the required Quality workflow. Maintain `data/reporting/report_registry.json` whenever adding or materially refreshing an analytical report; run `python tools/dkb.py report-freshness` before proposing the package. Only explicitly registered historical reports may use the legacy exception, and they must never be described as current. Run this check locally after the final report JSON, Markdown, registry and finding edits, and before committing/pushing; CI is the independent final gate, not the first place to discover report-contract defects.

## Remote-main and post-merge continuity (mandatory)

For every continuation, the remote GitHub default branch and its exact commit SHA are authoritative. Local files and generated counters are not canonical until the local HEAD is verified against that remote revision.

Before work:
- verify the current remote main SHA and read project/state.json from that revision;
- inspect recent merges and open PRs before selecting or repeating a package;
- if local execution is used, verify branch, HEAD, upstream and working-tree status first;
- never treat output from local project-state --apply as a GitHub update: it only changes the local working tree;
- distinguish automatic CI triggered by PR/push from manual workflow dispatch supported by the current tool connection.

After every merge:
- verify the PR's merged status, exact head SHA, merge commit and changed paths;
- verify the merge commit is present on remote main;
- reconcile current_package and next_package in canonical project/state.json;
- regenerate STATE_SUMMARY.md only with python tools/dkb.py project-state --apply;
- run project-state --check and documentation-baseline --check on the same candidate tree;
- submit and validate the state/documentation reconciliation through a PR;
- reread remote state before choosing the next package.

Never hand-edit generated summaries or copy counters from stale local output. If the canonical generator cannot be executed or validated, record the exact blocker and do not claim state synchronization or silently select work from the stale queue.

