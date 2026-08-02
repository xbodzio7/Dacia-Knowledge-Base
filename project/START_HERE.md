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
5. `AI_WORKING_AGREEMENT.md`
6. `AI_CONTEXT.md`
7. `SOURCE_ASSIMILATION_STANDARD.md`
8. `DOCUMENTATION_STANDARD.md`
9. `DOCUMENT_TYPES.md`
10. `GLOSSARY.md`
11. `DECISIONS.md`
12. `SESSION_STATE.md`
13. `ROADMAP.md`

`README.md` may be consulted if additional project context is required.

When narrative documents disagree about the current phase or package, the canonical `state.json` wins. Versioned source data and approved decisions remain higher-priority evidence for domain facts.

---

# Mandatory Rules

Before implementation the AI shall:

- read the canonical state and required documents;
- analyse the current repository and remote `main`;
- identify the current package declared by state;
- verify that no architectural or evidence blocker exists;
- define an exact package scope and acceptance criteria.

Implementation shall not begin before the required analysis has been completed.

Before using a PDF, brochure, price list, saved configuration, instruction or equivalent documentary source, the AI shall resolve its coverage state under `SOURCE_ASSIMILATION_STANDARD.md`. A registered source, normalized slice or earlier bounded migration must not be presented as a complete document analysis unless every page, table, footnote, symbol and relevant rendered visual has been reviewed and classified.

After implementation begins, work continues autonomously through tests, Pull Request, CI repair and merge until the package or milestone is complete. A generic `continue` or `kontynuuj` command is not required between correctly completed stages.

The AI stops only at a boundary defined in `AUTONOMOUS_MAINTAINER.md` and must then use the `ACTION_REQUIRED` format.

---

# Repository First

The repository is the primary source of truth.

Conversation history and old handoff prompts must never replace repository analysis or canonical state validation.

Run this check at session start whenever repository execution is available:

```bash
python tools/dkb.py project-state --check
```

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
