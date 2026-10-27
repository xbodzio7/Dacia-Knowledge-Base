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



\# 16. Future Evolution



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



