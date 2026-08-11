# Workflow Profiles

**Project:** Dacia Knowledge Base (DKB)  
**Status:** Active  
**Effective date:** 2026-08-11  
**Canonical state:** `project/state.json`

---

# Workflow Bootstrap Contract

**Never start project work from conversation memory alone.** A new chat, new session, application/browser switch, tool-limit change, recovery event, or handoff must not cause the AI to reconstruct the workflow from memory.

Before any project action, the AI shall perform this bootstrap:

1. Read `project/state.json` and identify the current package, next package, autonomy policy and execution policy.
2. Read `project/STATE_SUMMARY.md`, `project/WORKFLOW_PROFILES.md`, `project/AUTONOMOUS_MAINTAINER.md` and `project/SESSION_STATE.md` as required by `START_HERE.md`.
3. Verify the actual repository/remote state and the capabilities available in the current session.
4. Determine whether GitHub read/write access, local repository access, Codex/Work and other required execution capabilities are actually available.
5. Select the strongest appropriate execution profile from the table below.
6. Perform the Workflow Check before implementation.
7. Continue autonomously from the verified repository state unless an `ACTION_REQUIRED` boundary is reached.

The previous conversation is context only. It cannot select, override or reactivate a workflow profile.

## Active Workflow Profile

At session start the AI shall be able to state, internally or in the session record when useful:

- active profile;
- repository access mode;
- local repository availability;
- Codex/Work availability;
- current execution policy;
- autonomy mode;
- next package;
- applicable stop conditions.

`project/state.json` remains canonical for project state. The active profile is an execution decision derived from the current environment; it must not be treated as a permanent project-state value.

## Workflow Check

Before implementation, all of the following must be true:

- [ ] canonical `state.json` loaded;
- [ ] required startup documents loaded;
- [ ] current remote `main`/repository state verified when repository execution is available;
- [ ] current package and exact scope identified from repository state;
- [ ] actual execution capabilities identified;
- [ ] active profile selected from those capabilities;
- [ ] evidence/source boundary resolved;
- [ ] no `ACTION_REQUIRED` blocker present;
- [ ] acceptance criteria defined.

If a check fails, do not silently substitute a remembered workflow. Enter `RECOVERY` or diagnostic mode as appropriate and identify the exact blocker.

---

# Purpose

This document defines the supported execution profiles for developing and maintaining DKB when different ChatGPT plans, GitHub access modes, local repository access, or Codex availability are present.

It does not replace the canonical state, repository governance, source-assimilation rules, or maintainer contract. It defines how the same project workflow may be executed through different available environments.

The active project mode remains the value declared by `project/state.json`. This document never activates a profile by itself.

---

# Authority and precedence

The following remain authoritative in this order:

1. `project/state.json` for current project/package state and active execution policy;
2. repository documentation and approved architectural decisions;
3. `project/AUTONOMOUS_MAINTAINER.md` for autonomy and `ACTION_REQUIRED` boundaries;
4. `project/STANDARDS.md` for sprint and package rules;
5. source and data-model standards;
6. this document for selection of an available execution profile;
7. conversation history.

A profile may reduce available execution capabilities, but it must never weaken evidence requirements, quality gates, scope limits, or repository governance.

---

# Workflow v3

Workflow v3 is the project-level model in which **analysis, implementation, validation, repository state and recovery are separated from the particular tool used to execute them**.

The logical lifecycle is:

`state → manifest/scope → evidence analysis → implementation → validation → commit → PR → CI → merge → state update`

The execution environment may change during the lifecycle. A temporary lack of Codex or a local checkout does not by itself stop the project when an approved alternative path remains available.

Every implementation sprint still has one logical scope, explicit acceptance criteria, source-backed changes, validation, and a single coherent commit/PR boundary unless existing governance explicitly requires otherwise.

---

# Profiles

## GITHUB-FIRST

Use when ChatGPT has repository read/write access but local Work/Codex is unavailable or exhausted.

Flow:

`GitHub state → analysis → branch → GitHub file/tree change → commit → PR → CI → merge → state update`

Suitable for documentation, data, code and other changes that can be safely made through GitHub APIs without requiring local-only binaries or interactive tools.

The local checkout is not authoritative during this profile. After a merge, it should be synchronized by the owner when convenient.

## LOCAL/CODEX

Use when the local repository is available and Codex/Work can execute repository operations.

Flow:

`local state → analysis → branch → local change → local tests → commit/push → PR → CI → merge → state update`

This profile is preferred for tasks requiring local binaries, generated artifacts, extensive test execution, filesystem inspection, or other operations not reliably available through GitHub APIs.

## CHATGPT + CODEX

Use when ChatGPT performs architectural/source analysis and Codex performs the repository execution.

The two roles must share the same canonical repository state. Handoff text is not a replacement for re-reading `project/state.json` and the affected repository files.

## CHATGPT WITHOUT CODEX

Use when Codex is unavailable or its usage limit is exhausted.

If GitHub write access is available, select `GITHUB-FIRST`. If only read access is available, continue in diagnostic/planning mode and defer implementation until a write-capable profile is available.

## FREE

`FREE` is an execution constraint, not a separate project governance model.

Under Free, use whichever capabilities are actually available in the current session. Do not assume that switching between the desktop application and browser creates an additional usage allowance.

If GitHub write access is available, `FREE + GITHUB-FIRST` can continue implementation without Codex. If write access is unavailable, use diagnostic mode and prepare a bounded implementation package for later execution.

The Free profile does not permit relaxing evidence rules, inventing missing data, bypassing validation, or merging changes that have not passed the applicable quality gates.

## PLUS

`PLUS` is likewise an execution constraint rather than a different quality standard.

Use `PLUS + GITHUB-FIRST` when GitHub write access is available and Codex is unavailable/exhausted; use `PLUS + LOCAL/CODEX` when local execution is available and appropriate.

A higher plan does not override repository governance or source-evidence requirements.

## RECOVERY

Use when the normal execution path is interrupted, the local checkout is unavailable, a tool limit is reached, or session context has become unreliable.

Recovery order:

1. read `project/state.json`;
2. read `project/STATE_SUMMARY.md` and `project/SESSION_STATE.md` as applicable;
3. verify remote `main`, current branch/PR state and CI dynamically;
4. identify the current package and exact manifest/scope from repository state;
5. use the residual-review bundle or GitHub Actions artifact when local binary access is unavailable;
6. select the strongest currently available profile;
7. resume only from a verified repository state.

Recovery must not create a competing source of truth or infer missing work from conversation memory.

---

# Profile selection

Select the strongest available profile that is appropriate for the task:

| Situation | Preferred profile |
|---|---|
| Local repository + Codex/Work available | `LOCAL/CODEX` |
| GitHub write access, Codex unavailable/exhausted | `GITHUB-FIRST` |
| ChatGPT with Codex but no useful local access | `CHATGPT + CODEX` or `GITHUB-FIRST` as appropriate |
| Free plan with GitHub write access | `FREE + GITHUB-FIRST` |
| Plus plan with GitHub write access | `PLUS + GITHUB-FIRST` |
| Read-only access only | Diagnostic/planning mode |
| Broken or uncertain state | `RECOVERY` |

The profile is selected from actual available capabilities, not from assumptions about a plan or application surface.

---

# Capability-aware task selection

The canonical `next_package` is the first package to evaluate, not an unconditional command to stop or an assumption that the current environment can execute it.

After selecting the active profile, the AI shall evaluate whether the current `next_package` is executable with the actual capabilities and evidence available in the session.

If the `next_package` is **not executable because of an environment or tool limitation**, the AI shall, before declaring `ACTION_REQUIRED`:

1. preserve the canonical package and its status in `project/state.json`;
2. record the exact capability/evidence blocker in `SESSION` when useful;
3. inspect the repository-defined package/manifest/backlog sequence for the next safe, in-scope package that is executable under the active profile;
4. select that package for the current session if doing so does not require a new architectural decision, source assumption, scope expansion, or user choice;
5. continue autonomously with that executable package;
6. return to the blocked canonical package when the required capability becomes available.

A package blocked only by the current environment is **not completed, cancelled, rejected, or advanced**. Skipping it for execution is a session-level scheduling decision and does not modify canonical state.

`ACTION_REQUIRED` is therefore reached only when:

- the blocked package is the only safe executable work remaining; or
- continuing with another package would require a decision, scope change, unsupported assumption, missing evidence, or other autonomy boundary defined elsewhere in the project contracts.

The AI must not skip a blocked package merely because it is inconvenient, and it must not reorder packages in a way that violates dependencies or canonical prioritization.

This rule does not permit importing data without required evidence, bypassing validation, changing `state.json` to hide a blocker, or treating a planned package as completed merely because another package was executed.

---

# Checkpoints

Before implementation:

- canonical state verified;
- current remote `main` verified;
- package and scope identified from repository state;
- evidence/source boundary resolved;
- no `ACTION_REQUIRED` blocker present;
- acceptance criteria defined.

Before PR:

- only in-scope files changed;
- focused validation completed;
- generated/documentation state updated where required;
- commit has one logical responsibility.

Before merge:

- PR is the intended package;
- required CI/quality checks are green;
- no unresolved review or evidence blocker exists;
- project state can be advanced consistently.

---

# VERIFIED / SESSION reporting protocol

`VERIFIED` contains repository/source facts that were actually checked. It must not contain guesses or conclusions presented as facts.

`SESSION` contains interpretation, decision, recommendation, current working hypothesis, blockers and the next bounded action. It is not a competing canonical state.

When a statement cannot be verified from the repository or authoritative source, keep it in `SESSION` and label the uncertainty.

---

# ACTION_REQUIRED

When an autonomy boundary from `AUTONOMOUS_MAINTAINER.md` is reached, stop at that boundary and report:

- **reason**;
- **required_action**;
- **options_and_consequences**;
- **resume_stage**.

A tool limit alone is not an `ACTION_REQUIRED` decision if an approved alternative profile can perform the same in-scope work safely.

---

# FREE diagnostic mode

When no write-capable execution path is available, work may continue without repository mutation:

`state → evidence → diagnosis → proposed exact changes → acceptance criteria → handoff`

This is a diagnostic workflow, not an implementation sprint. It must not be reported as completed implementation and must not advance canonical state.

---

# Relationship to existing contracts

This document supplements, and does not replace:

- `project/START_HERE.md` — mandatory startup and reading order;
- `project/state.json` — canonical current state and active execution policy;
- `project/AUTONOMOUS_MAINTAINER.md` — autonomy and stop conditions;
- `project/ACCELERATED_MILESTONE_CLOSURE.md` — accelerated milestone rules;
- `project/AI_WORKING_AGREEMENT.md` — collaboration principles;
- `project/STANDARDS.md` — sprint and implementation standards;
- `project/DOCUMENT_TYPES.md` — documentation responsibilities.

---

# End of document
