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
4. `AI_WORKING_AGREEMENT.md`
5. `AI_CONTEXT.md`
6. `DOCUMENTATION_STANDARD.md`
7. `DOCUMENT_TYPES.md`
8. `GLOSSARY.md`
9. `DECISIONS.md`
10. `SESSION_STATE.md`
11. `ROADMAP.md`

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
