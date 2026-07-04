\# Dacia Knowledge Base (DKB) Roadmap



\*\*Project:\*\* Dacia Knowledge Base (DKB)



\*\*Current Version:\*\* v2.1



\*\*Status:\*\* Active Development



\---



\# Vision



The Dacia Knowledge Base aims to become a comprehensive, structured and validated automotive knowledge model for Dacia vehicles.



The project focuses on:



\* data quality

\* maintainability

\* consistency

\* extensibility

\* automation

\* future API and database integration



The repository is treated as the single source of truth for the DKB data model.



\---



\# Project Phases



\## Phase 1 — Foundation ✅ Completed



\### Data Model



\* Complete attribute catalogue

\* Stable attribute identifiers

\* Standardized naming

\* CSV integrity validation



\### Reference Dictionaries



\* domains.csv

\* units.csv

\* value\_types.csv

\* validation\_rules.csv



\### Project Governance



\* Workflow v2

\* Coding standards

\* Architecture decisions

\* Session management

\* Data quality checklist



\---



\## Phase 2 — Tooling 🚧 Current Phase



Objective:



Build tools that automatically validate, document and transform the DKB data model.



Planned deliverables:



\### Validator



\* CSV validation

\* Duplicate detection

\* Reference dictionary validation

\* Data quality checks



\### Documentation Generator



Generate documentation directly from CSV files.



\### JSON Export



Generate machine-readable JSON representations.



\### SQLite Export



Generate a relational database for querying and analysis.



\---



\## Phase 3 — Automation



Planned work:



\* Automated validation pipeline

\* Release generation

\* Documentation publishing

\* CI integration

\* Automated quality reports



\---



\## Phase 4 — Integration



Long-term objectives:



\* REST API

\* GraphQL API

\* SQL database

\* Search engine

\* External integrations



\---



\# Current Priorities



1\. Validator framework

2\. Documentation generator

3\. SQLite exporter

4\. JSON exporter



\---



\# Technical Debt



Current known items:



\* Review ontology consistency

\* Review enum candidates

\* Review duplicated semantic concepts

\* Expand validation rules

\* Improve documentation automation



\---



\# Design Principles



The project follows these principles:



\* Single Source of Truth

\* Incremental Evolution

\* Backward Compatibility

\* Data First

\* Validation Before Expansion

\* Documentation Driven Development



\---



\# Success Criteria



The project is considered mature when:



\* all data is automatically validated

\* documentation is generated automatically

\* no manual consistency checks are required

\* data can be exported to multiple formats

\* external applications can consume the model through stable interfaces



\---



\# Current Milestone



\*\*DKB v2.1 — Managed Data Model\*\*



Status: Completed



Next milestone:



\*\*DKB v2.2 — Tooling \& Automation\*\*



