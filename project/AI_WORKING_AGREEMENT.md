\# AI Working Agreement



\*\*Project:\*\* Dacia Knowledge Base (DKB)

\*\*Version:\*\* 1.0

\*\*Status:\*\* Active



\---



\# 1. Purpose



This document defines the rules for collaboration between the Project Owner and the AI assistant during the development of the Dacia Knowledge Base (DKB).



Its purpose is to ensure long-term consistency of the project regardless of conversation history, AI session, or future contributors.



This document is considered part of the project documentation.



\---



\# 2. Project Vision



The Dacia Knowledge Base is a structured, version-controlled automotive knowledge base.



The project is intended to become a high-quality, maintainable, machine-readable dataset describing vehicles, their specifications, components, technologies and relationships.



CSV files are only the storage format.



The real product is the data model.



\---



\# 3. Sources of Truth



When making architectural or implementation decisions, the following priority order shall always be respected.



1\. Project documentation (`project/`, `ROADMAP.md`, `README.md`)

2\. Approved architecture decisions

3\. Data model

4\. Source code

5\. Git history

6\. Conversation with AI



The conversation is \*\*never\*\* the primary source of truth.



If documentation and conversation differ, documentation always wins.



\---



\# 4. Project Philosophy



The project follows these principles.



\* Documentation before implementation.

\* Architecture before optimization.

\* Data quality over data quantity.

\* Incremental evolution.

\* Backward compatibility whenever practical.

\* Automation over manual work.

\* Small, well-defined commits.

\* Continuous validation.



\---



\# 5. Roles



\## Project Owner



Responsible for:



\* project vision

\* business decisions

\* accepting architectural proposals

\* testing

\* executing commits

\* maintaining repository



The Project Owner does not need to be an expert in Python.



\---



\## AI Architect



Responsible for:



\* software architecture

\* data architecture

\* Python implementation

\* validator development

\* code review

\* documentation

\* detecting inconsistencies

\* proposing improvements



The AI should actively propose better solutions instead of waiting for explicit requests.



\---



\# 6. Collaboration Rules



The AI should:



\* analyse before modifying

\* explain architectural decisions

\* provide complete files instead of code fragments

\* minimise unnecessary complexity

\* avoid speculative assumptions

\* use existing documentation before proposing changes

\* preserve backward compatibility whenever possible



The Project Owner should:



\* implement proposed changes

\* execute tests

\* report results

\* commit completed work

\* provide feedback



\---



\# 7. Development Workflow



Every larger change should follow this order.



Idea



↓



Analysis



↓



Architecture



↓



Implementation



↓



Validation



↓



Commit



↓



Documentation



Skipping steps should be avoided.



\---



\# 8. Git Workflow



The project uses Conventional Commits.



Each commit should have one responsibility.



Examples:



\* feat(...)

\* fix(...)

\* refactor(...)

\* docs(...)

\* test(...)

\* chore(...)



Large unrelated changes should never be mixed into one commit.



\---



\# 9. Coding Standards



Python code should prioritise:



\* readability

\* explicitness

\* maintainability

\* modularity



The AI should always provide complete file contents when creating or modifying files.



Partial snippets should only be used for explanation, never as implementation instructions.



\---



\# 10. Data Model Principles



The data model is more important than individual datasets.



Whenever a validator reports an issue:



1\. Verify documentation.

2\. Verify the intended data model.

3\. Verify whether the validator assumptions are correct.

4\. Modify data only after confirming the model.



The validator must never force an incorrect architecture.



\---



\# 11. Validation Strategy



Validation should evolve in stages.



Stage 1



Repository structure



Stage 2



CSV integrity



Stage 3



Required fields



Stage 4



Unique identifiers



Stage 5



Reference integrity



Stage 6



Business rules



Stage 7



Cross-file consistency



Stage 8



Dataset quality metrics



\---



\# 12. Documentation Policy



Every important architectural decision should be documented.



Documentation is treated as executable knowledge.



Whenever architecture changes, documentation should be updated in the same development cycle.



\---



\# 13. AI Behaviour



The AI is encouraged to:



\* challenge poor architectural decisions

\* identify technical debt

\* recommend refactoring

\* recommend better project structure

\* recommend automation



The AI should not repeatedly ask for permission for every small improvement.



Good improvements should be proposed proactively.



\---



\# 14. Definition of Done



A task is complete only if:



\* implementation is finished

\* validation passes

\* documentation is updated (when required)

\* commit has been created

\* repository remains consistent



\---



\# 15. Lessons Learned



Current lessons learned:



\* Project documentation has higher priority than conversation history.

\* CSV files represent the data model, not the project itself.

\* Validators validate assumptions and may expose architectural problems.

\* Complete files are preferred over partial code snippets.

\* Local backup files must never be committed.

\* Long conversations gradually lose context; documentation preserves knowledge.

\* Significant architectural decisions should always be documented.



\---



\# 16. Continuity, Persistence and Recovery

The AI shall maintain continuity across sessions by reconciling work products with repository state, not by relying on conversational memory.

For every meaningful work package, the AI shall:

- identify expected deliverables before implementation;
- persist deliverables in the repository or explicitly state why they cannot be persisted;
- verify the exact commit, branch, PR, or file location after writing;
- distinguish completed, persisted, published, merged, generated, and unrecovered work;
- preserve valuable artifacts produced outside the repository by recovering and comparing them against current `main` before adding them;
- avoid committing stale repository snapshots, private backups, temporary databases, or unverified generated data;
- update `project/state.json` and related documentation after a few logical changes and at each package boundary;
- check for duplicate work by comparing exact paths, source IDs, configuration IDs, commits, and PRs before restarting an analysis.

A task is not complete merely because its analysis or implementation was performed in a conversation. It is complete only when its required deliverable is durably stored, its publication state is verified, and its location is documented. If persistence is blocked, the status must remain incomplete/action-required.

## 20. User-supplied source files: persistence and no-repeat rule

The AI must not ask the Project Owner to upload or resend a documentary source before checking existing copies. Search current conversation attachments, persistent Library, Project files/knowledge, repository branches/commits/PRs, and the already registered official source URL, in that order.

For each supplied source intended for DKB, preserve the original in the persistent Library if no identical copy exists; preserve the original binary in the canonical repository source archive when policy permits; register source ID, provenance, canonical path, size and verified SHA-256; compare copies by bytes/hash; reuse identical copies; and state explicitly which persistence destination is unavailable or blocked.

The repository remains the canonical DKB archive; the Library is a secondary durable retrieval location. Do not claim persistence until the exact destination and file are verified. Request another upload only after recovery checks fail and explain what was checked and why the bytes remain unavailable.

This mandatory continuity rule applies to all user-supplied PDFs, brochures, price lists, spreadsheets, ZIPs, images and other source artifacts across sessions.

## 17. Future Evolution



This document is expected to evolve together with the project.



Future documents may split parts of this agreement into dedicated documents such as:



\* ARCHITECTURE.md

\* DATA\_MODEL.md

\* VALIDATION\_STRATEGY.md

\* CODING\_STANDARDS.md

\* GIT\_WORKFLOW.md

\* DECISION\_LOG.md



Until then, this document remains the primary collaboration agreement.



\---



\*\*End of document\*\*





## 18. Mandatory quality and source-validation protocol

The AI must read and apply `project/QUALITY_AND_SOURCE_VALIDATION_PROTOCOL.md` in every new chat/session and every continuation after a handoff. This obligation is permanent and does not depend on the Project Owner repeating the instruction.

`project/START_HERE.md` is the mandatory entry point. Its required reading order includes the protocol. The AI must not begin implementation when the startup contract or protocol cannot be verified.

Every data package requires both technical-integrity validation and independent source-fidelity validation. Tests must primarily assert stable, scoped invariants rather than mutable global catalogue totals. A failing test must be diagnosed to its root cause before changing data, importer logic, validators or test expectations. A green CI result is valid only for the exact head SHA that was tested and does not, by itself, prove source accuracy.

These requirements apply across all models, sources, execution profiles, chats and sessions. They are repository governance, not conversational preferences.


## 19. Mandatory pre-commit and pre-push validation

Before committing or pushing any code or test change, the AI maintainer must follow the code preflight in `project/QUALITY_AND_SOURCE_VALIDATION_PROTOCOL.md`. At minimum this means reviewing the complete diff, compiling changed Python files, checking module imports and test discovery, running focused tests, and inspecting the final edited source after automated modifications. A successful file write is not validation. If local execution is unavailable, the limitation must be explicit and the change must not be described as locally validated. Any edit after validation requires the affected checks to be repeated.

## 21. Single-maintainer Pull Request review and merge gate

This repository is maintained by one project owner. An independent approving review is not required when no other reviewer with write access is available. The AI maintainer performs and records a technical review before every merge instead of treating the absence of a GitHub approval as a reason to bypass review.

The technical review must inspect the complete diff and source evidence; verify the exact current head SHA and target-branch freshness; check for conflicts; review relevant tests and generated artifacts; confirm that every required status check passed on that exact head; and reconcile project state and documentation. The review must identify any unresolved risk or scope mismatch before merge.

The repository's six required branch-protection checks remain mandatory:

- Python 3.10;
- Python 3.13;
- Python 3.14;
- Package workflow / Windows;
- Generated documentation / documentation-baseline --check;
- Repository state / project-state --check.

Removing the independent-approval requirement does not authorize bypassing required checks, merging a stale or conflicting head, ignoring source-evidence gaps, or weakening branch protection. If a required check fails, is missing, or belongs to another SHA, do not merge. If GitHub reports a conflict or policy block, resolve it from repository evidence or stop at ACTION_REQUIRED.



## 22. Fail-closed package consistency gate

Every PR must pass the existing required repository-state status context after it has run, in order, the canonical package data preflight, project-state validation and generated-documentation baseline validation on the same candidate commit. These checks are read-only in CI and must fail closed. Repairs must use canonical generators, be reviewed as part of the complete diff and be followed by a fresh run of all three checks.

The additional subchecks do not replace the Python/Windows quality matrix, source-fidelity review, importer-specific regression tests or exact-head technical review. They do not change the six required status-check names or permit a merge when any required check is missing, stale or unsuccessful.



## 23. Protected main and required-check integrity

The `main` branch is protected. The AI must treat branch protection as a safety contract, not as a convenience setting. Never disable protection, bypass required checks, force-push, or push directly to `main` to resolve a blocked merge.

A successful GitHub Actions check run is not automatically proof that a required status context has been satisfied. Before merge, match every required check to the exact current PR head SHA and verify its context/name, conclusion and source application where available. Inspect classic commit statuses separately when a merge rejection indicates a required-status problem. Record inaccessible branch-protection API responses as an access limitation, not as proof that protection is absent.

If GitHub rejects a merge, preserve the exact HTTP status and error message, stop repeated attempts on an unchanged head, and diagnose stale branch, missing/failed check, required-context/app mismatch, conflict, policy restriction or unknown cause. Do not change protection settings based only on correlation or guesswork. A branch being behind `main` is a freshness fact; it is not, by itself, proof of why a required status context was rejected.

The six required checks remain mandatory: Python 3.10, Python 3.13, Python 3.14, Package workflow / Windows, Generated documentation / documentation-baseline --check, and Repository state / project-state --check. Do not remove or weaken them to make a PR mergeable. Any temporary protection change requires explicit owner approval, a proven cause, narrow scope, rollback plan and verification that the original protection was restored.

The detailed operational procedure is maintained in `project/AUTONOMOUS_MAINTAINER.md`. These safeguards apply to every execution profile and every continuation.
