# Safe Git Bash Operations

This procedure is mandatory whenever a maintainer uses Git Bash to synchronize, switch branches, regenerate repository state, commit or push DKB changes.

Its purpose is to prevent accidental work on `main`, overwriting local edits, confusing repeated terminal input, and publishing a partially validated tree.

## Non-negotiable safety rules

- Never use `git reset --hard`, `git clean -fd`, force-push, or discard local changes as a routine recovery step.
- Never switch branches or pull over a dirty working tree without first identifying and safely preserving the changes.
- Never run package edits or commits on `main`. Use the package branch named by the current task/PR.
- Never use `git add .` or `git add -A` for routine package commits. Stage only reviewed, in-scope paths.
- Never restore a stash blindly. Inspect it first and apply it only to the branch and files for which it was created.
- Never manually edit generated state or generated documentation. Use the canonical generator.
- Execute one command at a time. Wait for the shell prompt to return and inspect the result before entering the next command.
- If a command fails, stop. Do not paste or repeat the remaining sequence until the failure is understood.

## A. Preflight before any branch or synchronization operation

Run these commands separately:

```bash
git status --short
git branch --show-current
git remote -v
git log -1 --oneline
```

Interpretation:

1. Confirm the repository path and expected remote.
2. Confirm the current branch is the intended package branch. If it is `main`, do not edit or commit package work there.
3. If `git status --short` prints any paths, the working tree is not clean. Inspect and classify every path before proceeding.
4. If the branch, remote or repository identity is unexpected, stop and resolve that discrepancy first.

Do not treat an empty `git status --short` output as an error: it means there are no reported working-tree changes.

## B. Preserve local changes before switching branches

First inspect the exact changes:

```bash
git status --short
git diff -- project/STATE_SUMMARY.md project/state.json
git diff --stat
```

If the changes are generated state files produced by `python tools/dkb.py project-state --apply`, do not discard them. They may be the intended repair for the current package branch.

If a branch switch is necessary and the changes must remain local temporarily, stash only the identified paths. Example:

```bash
git stash push -m "describe-purpose-and-date" -- project/STATE_SUMMARY.md project/state.json
git stash list -n 3
git status --short
```

Confirm that the stash was created and the working tree is clean before switching. A stash is a local safety copy, not a commit or remote backup.

If the changes are not limited to the named paths, do not copy this example unchanged. Identify every changed path and decide whether it belongs to the current package, should be committed, or must be preserved separately.

Do not run `git stash pop` automatically. After switching branches, inspect the target branch and the stash contents first:

```bash
git stash show --stat stash@{0}
git stash show -p stash@{0}
```

Apply a stash only when its contents are appropriate for the current branch. Prefer `git stash apply` over `pop` so the safety copy remains until the result is verified. Drop a stash only after confirming that its changes are safely committed or otherwise preserved.

## C. Switch and synchronize the intended branch

Use the exact branch name from the current task or Pull Request. Execute each command separately:

```bash
git fetch origin
git checkout <exact-branch-name>
git branch --show-current
git pull --ff-only origin <exact-branch-name>
git status --short
```

Replace `<exact-branch-name>` with the real branch name; do not type the angle brackets.

Stop if:

- checkout reports that local changes would be overwritten;
- pull reports that local changes would be overwritten;
- the current branch is not the intended branch;
- fast-forward-only pull cannot proceed;
- the working tree contains unexplained changes.

Do not solve these conditions with reset, force-pull, or deletion. Return to section B and preserve/understand the changes.

## D. Regenerate canonical state and validate

On the intended package branch, run the canonical generator only when the package requires state synchronization:

```bash
python tools/dkb.py project-state --apply
```

Read its complete output. Then run each check separately:

```bash
python tools/dkb.py project-state --check
python tools/dkb.py documentation-baseline --check
```

Both checks must pass on the same candidate tree. If either fails, stop and report the complete output. Do not manually edit `project/state.json` or `project/STATE_SUMMARY.md` to imitate generator output.

## E. Review and commit only intended files

Before staging:

```bash
git status --short
git diff --check
git diff --stat
git diff
```

Review the complete diff. Confirm the current branch again:

```bash
git branch --show-current
```

Stage only the intended paths, for example:

```bash
git add project/STATE_SUMMARY.md
git status --short
git diff --cached --check
git diff --cached --stat
git diff --cached
```

Add `project/state.json` only if it is an intended, generator-produced change for this package. Do not stage unrelated local files.

Commit only after the staged diff has been reviewed and all required checks pass:

```bash
git commit -m "chore(state): regenerate project state summary"
git status --short
git log -1 --oneline
```

If the commit fails, stop and inspect the message. Do not repeatedly paste the same command.

## F. Push and verify

Push only the intended package branch:

```bash
git push origin <exact-branch-name>
```

Then verify:

```bash
git status --short
git log -1 --oneline
git rev-parse HEAD
```

The working tree should be clean. Record the exact resulting commit SHA and verify that the Pull Request head points to that SHA before treating CI as relevant.

Any new commit, generated-file update, rebase or other candidate-tree change invalidates the previous final validation. Re-run the affected checks and require the complete CI matrix on the new exact HEAD SHA.

## G. Terminal input discipline

- Paste only the command currently requested, not the shell prompt (`$`) or explanatory text.
- Wait until Git Bash displays a new prompt before pasting the next command.
- If a response contains multiple commands, run them one at a time unless the instruction explicitly says the block is a single safe script.
- Repeated command text in terminal output is not proof that each command ran. Use the final prompt, branch name, status and command output to establish what actually happened.
- If output is truncated, duplicated, or ambiguous, run only read-only diagnostics (`git status --short`, `git branch --show-current`, `git log -1 --oneline`) and report them before continuing.

## Recovery report

When stopping on an error, provide:

1. the exact command that was run;
2. the complete error output;
3. `git status --short`;
4. `git branch --show-current`;
5. whether a stash was created and its label, if applicable.

Do not attempt destructive cleanup while waiting for diagnosis.

## Relationship to other controls

This guide supplements, and does not replace:

- `project/QUALITY_AND_SOURCE_VALIDATION_PROTOCOL.md` — source fidelity, tests, canonical generators and exact-SHA quality gates;
- `project/AUTONOMOUS_MAINTAINER.md` — package scope, autonomy and stop conditions;
- `project/START_HERE.md` — mandatory session bootstrap.

If instructions conflict, canonical repository policy and the quality protocol take precedence. Unknown checks are BLOCKED, not PASS.
