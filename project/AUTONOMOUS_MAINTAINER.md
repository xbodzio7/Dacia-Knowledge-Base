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
7. Run focused tests and the complete quality gate appropriate to the scope.
8. Publish the package through the repository workflow and structured handoff where local Git execution is available.
9. Create or update the Pull Request.
10. Verify base SHA, head SHA, changed paths, commit scope, mergeability and all CI jobs.
11. Repair in-scope failures and repeat validation without asking for a generic continuation command.
12. Merge only a current, green and mergeable Pull Request.
13. Update canonical state and generated documentation.
14. Continue with the next package.

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
